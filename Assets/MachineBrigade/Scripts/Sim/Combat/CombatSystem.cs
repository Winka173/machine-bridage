#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Abilities;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Target selection, aiming, firing and projectile flight for every weapon mount. Explicit
    /// orders decide what the main weapon may target; automatic targeting only fills in where
    /// orders allow it. Secondary weapons (coaxial and roof guns, missile pods) choose their own
    /// targets, favouring the main weapon's.
    /// </summary>
    internal sealed partial class CombatSystem
    {
        private static readonly float TurretTolerance = SimMath.DegToRad(4f);
        private static readonly float FreeTolerance = SimMath.DegToRad(6f);
        private static readonly float HullTolerance = SimMath.DegToRad(12f);
        private static readonly float FreeMountTurnRate = SimMath.DegToRad(300f);

        private readonly SimWorld _world;
        private readonly List<Projectile> _projectiles = new();

        /// <summary>(team, target) pairs someone was already shooting last step, for focus fire.</summary>
        private readonly HashSet<(int team, EntityId target)> _focus = new();

        public CombatSystem(SimWorld world) => _world = world;

        /// <summary>Vehicles a guided missile or drone is flying at this step.</summary>
        private readonly HashSet<EntityId> _missileTargets = new();

        public bool MissileIncoming(EntityId vehicle) => _missileTargets.Contains(vehicle);

        /// <summary>Ground vehicles a guided missile (not a drone) is flying at this step: an anti-tank missile's lock (Laser Warning's cue).</summary>
        private readonly HashSet<EntityId> _atgmTargets = new();

        public bool AtgmIncoming(EntityId vehicle) => _atgmTargets.Contains(vehicle);

        /// <summary>Some round is on its way to this vehicle (a Decoy Launcher's cue).</summary>
        public bool RoundIncoming(EntityId vehicle) => _incoming.ContainsKey(vehicle);

        /// <summary>A round launched by equipment rather than a mount (a ricochet, a drone): it flies and lands like any other.</summary>
        public void AddProjectile(Projectile p) => _projectiles.Add(p);

        /// <summary>Rounds in flight (tests: what a shot carries, such as its damage scale).</summary>
        internal IReadOnlyList<Projectile> InFlight => _projectiles;

        public void Step(float dt)
        {
            _missileTargets.Clear();
            _atgmTargets.Clear();
            foreach (var p in _projectiles)
            {
                if (!p.Weapon.Guided || !p.Target.IsValid) continue;
                _missileTargets.Add(p.Target);
                if (p.Weapon.Projectile == ProjectileKind.Missile && !p.TargetFlying) _atgmTargets.Add(p.Target);
            }
            _focus.Clear();
            CountWingmen();
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Target.IsValid) _focus.Add((v.Team, v.Target));

            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                var mounts = v.Def.Mounts;
                // Cooldowns run regardless of movement or retargeting, so micro cannot create free shots.
                // A magazine's cadence may be finer than the step: its cooldown keeps up to one step of
                // credit, so a 20-round-a-second gun fires two rounds in some steps (see Stream).
                for (var i = 0; i < mounts.Count; i++)
                    v.Weapons[i].Cooldown = MathF.Max(v.Arms[i].Clip > 0 ? -dt : 0f, v.Weapons[i].Cooldown - dt * v.FireFactor * v.Weapons[i].RateScale);
                ReloadMagazines(v, dt);
                // Knocked out by an EMP: the crew can do nothing until it wears off. An obstacle, a
                // minefield or a module has nothing to fire; a gun pit down in its hole waits.
                // Prompt 17 C: a bunker vehicle digging in or packing up does not fire either.
                // Prompt 19: a tiered boss in orbit holds its fire (its big attack is the boss system's).
                if (v.Stunned || v.Lowered || v.HoldFire || v.AiHoldFire || v.Def.Passive || v.Burrowed || v.DeployBusy || v.Tier == AltitudeTier.Orbit)
                {
                    v.Target = EntityId.None;
                    continue;
                }

                // Play-test 5 (DECISIONS 20W): a siege tank on its tracks picks targets for its tank-mode gun.
                var target = v.Def.Deploy is { Siege: true } siege && v.Deploy != DeployState.Deployed && siege.TankMount < mounts.Count
                    ? SelectTarget(v, v.Arms[siege.TankMount])
                    : SelectTarget(v);
                v.Target = target?.Id ?? EntityId.None;
                // Nothing on the ground for the main gun: the coaxial machine gun takes on an
                // aircraft in reach and the turret swings after it.
                var air = target == null ? CoaxAirTarget(v) : null;
                v.CoaxAir = air?.Id ?? EntityId.None;
                var laid = target ?? air;
                v.AimDistance = laid != null ? Vector2.Distance(v.Position, laid.Position) : 0f;
                v.AimHeight = laid is Vehicle aimed && aimed.Flying ? aimed.Height : 0f;
                // A supergun's barrel stays laid where its last shell went (its shots are the boss system's).
                if (mounts[0].Aim == MountAim.Turret && !v.Def.LaysOwnTurret)
                {
                    var desired = laid != null ? SimMath.HeadingOf(laid.Position - v.Position) : v.Heading;
                    v.TurretHeading = SimMath.RotateTowards(v.TurretHeading, desired, v.Def.TurretTurnRate * v.TurretFactor * dt);
                    KeepToArc(v);
                }
                else
                {
                    v.TurretHeading = v.Heading;
                    if (IsSide(mounts[0])) AimSide(v, 0, target, dt);
                }
                if (v.MountWorks(0) && !v.Arms[0].Laid) Operate(v, 0, target, dt);

                for (var i = 1; i < mounts.Count; i++)
                {
                    // A boss's mount on a broken part fires no more; a mount the boss system lays (a ship's
                    // main turret, prompt 16: "laid") keeps the heading it was given.
                    if (v.Arms[i].Laid) continue;
                    if (!v.MountWorks(i))
                    {
                        v.Weapons[i].Target = EntityId.None;
                        continue;
                    }
                    var secondary = SelectSecondaryTarget(v, i, target);
                    var state = v.Weapons[i];
                    state.Target = secondary?.Id ?? EntityId.None;
                    if (mounts[i].Aim == MountAim.Free)
                    {
                        var aim = secondary != null ? SimMath.HeadingOf(secondary.Position - v.Position) : v.TurretHeading;
                        state.Heading = SimMath.RotateTowards(state.Heading, aim, FreeMountTurnRate * dt);
                    }
                    else if (IsSide(mounts[i]))
                    {
                        AimSide(v, i, secondary, dt);
                    }
                    Operate(v, i, secondary, dt);
                }
            }
            // Prompt 25 F2 batch A: the microwave's pulses and the interceptor drones' hunt.
            StepDroneKillers();
            UpdateProjectiles(dt);
        }

        /// <summary>Below this speed a vehicle counts as standing still, and its crew can reload.</summary>
        internal const float ReloadStillSpeed = 0.4f;

        /// <summary>
        /// Seconds to reload a whole magazine in place: the weapon's own figure, else two fifths of
        /// the time it takes to fire it off, between 10 and 28 s (a Grad about 17 s, a howitzer 28 s).
        /// </summary>
        public static float ReloadSeconds(WeaponDef weapon) => weapon.MagazineReload;

        /// <summary>
        /// An empty magazine is reloaded in place, like the salvo reloads of Art of War 3 and
        /// Warpath: the crew restocks while the vehicle stands still (moving pauses it), then the
        /// whole magazine is back at once. Home and a supply vehicle make it faster (see
        /// <see cref="Abilities.AbilitySystem"/>); part-empty magazines are topped up there too.
        /// </summary>
        private void ReloadMagazines(Vehicle v, float dt)
        {
            var mounts = v.Def.Mounts;
            for (var i = 0; i < mounts.Count; i++)
            {
                var state = v.Weapons[i];
                var weapon = v.Arms[i];
                if (weapon.Ammo <= 0 || state.Ammo != 0)
                {
                    state.ReloadLeft = 0f;
                    continue;
                }
                if (state.ReloadLeft <= 0f) state.ReloadLeft = ReloadSeconds(weapon);
                // Hot Swap and an ammunition carrier nearby: faster, and on the move too.
                var rate = _world.Gear.ReloadRate(v, out var onTheMove) * v.RankFire;
                if (!v.StillForReload && !onTheMove) continue;
                state.ReloadLeft -= dt * rate;
                if (state.ReloadLeft > 0f) continue;
                state.ReloadLeft = 0f;
                state.Ammo = weapon.Ammo;
            }
        }

        /// <param name="tankGun">Play-test 5: a siege tank on its tracks lays its turret for its tank-mode gun instead.</param>
        private IDamageable? SelectTarget(Vehicle v, WeaponDef? tankGun = null)
        {
            var weapon = tankGun ?? v.Weapon;
            switch (v.Order.Kind)
            {
                case OrderKind.Attack:
                    // Shooting at an ordered target needs sight of it (smoke and fog stop assigned shelling).
                    if (!_world.TryGetTarget(v.Order.Target, out var ordered) || !ordered.IsAlive) return null;
                    // Shielded for now (a boss behind its glyph): shoot at something else meanwhile.
                    if (ordered is Vehicle { Invulnerable: true }) return Retarget(v, weapon, Held(v, ordered.Id), EntityId.None, ref v.RetargetAt);
                    if (ordered is Vehicle hidden && !hidden.IsVisibleTo(v.Team)) return null;
                    // Play-test 8 A: an order from the commander AI (never the player's) gives way while something the
                    // weapon is far better at is in reach: an anti-air gun sent at a tank turns on the helicopter overhead.
                    return !v.ManualOrder && BetterThanOrder(v, weapon, ordered) is { } better ? better : ordered;

                case OrderKind.AttackMove:
                    if (RunTargetInReach(v, weapon, out var run)) return run;
                    // The enemy it broke off its route for is held, and favoured, but weighed against the rest in reach.
                    var held = Held(v, EntityId.None);
                    if ((held == null || !IsValidAutoTarget(v, held, weapon)) && _world.TryGetVehicle(v.Engaged, out var engaged)) held = engaged;
                    return Retarget(v, weapon, held, v.Engaged, ref v.RetargetAt);

                case OrderKind.Idle:
                    if (RunTargetInReach(v, weapon, out var runIdle)) return runIdle;
                    // A counter-battery gun leaves what it was shelling for the enemy gun that just fired (DECISIONS 19T).
                    if (CounterBatteryTarget(v, weapon) is { } gun) return gun;
                    return Retarget(v, weapon, Held(v, EntityId.None), EntityId.None, ref v.RetargetAt);

                case OrderKind.Move:
                case OrderKind.Retreat:
                    // Targets of opportunity only: firing never changes the route (V2 R04).
                    return v.Def.FiresWhileMoving || tankGun != null ? Retarget(v, weapon, Held(v, EntityId.None), EntityId.None, ref v.RetargetAt) : null;

                default:
                    return null;
            }
        }

        /// <summary>
        /// Play-test 8 A (DECISIONS 22Q): seconds between a weapon's looks round for a better target than the one it is on
        /// (not only when that one dies or leaves its reach), and how much better another must score to take over, so a
        /// unit never flickers between two targets of about the same worth.
        /// </summary>
        internal const float RetargetSeconds = 0.5f;

        internal const float SwitchMargin = 1.3f;

        /// <summary>Play-test 8 A: an order from the commander AI gives way only to a target this many times better for the weapon.</summary>
        internal const float OrderMargin = 5f;

        /// <summary>Play-test 8 A: a target that can shoot back at this vehicle counts this much more than one that cannot.</summary>
        internal const float ThreatWeight = 1.15f;

        /// <summary>The vehicle the main weapon was on last step (other than <paramref name="not"/>), or null.</summary>
        private Vehicle? Held(Vehicle v, EntityId not) =>
            v.Target != not && _world.TryGetVehicle(v.Target, out var held) ? held : null;

        /// <summary>
        /// Play-test 8 A: the target a weapon is best at. The one it holds stays while it is valid, and every
        /// <see cref="RetargetSeconds"/> it is weighed against the best in reach, which takes over only when it scores
        /// <see cref="SwitchMargin"/> times as much. With nothing held (or the held one lost) the best in reach at once.
        /// Deterministic: it reads the sim's clock and state only.
        /// </summary>
        private Vehicle? Retarget(Vehicle v, WeaponDef weapon, Vehicle? held, EntityId favoured, ref double nextAt, int arcMount = -1)
        {
            var holds = held != null && IsValidAutoTarget(v, held, weapon) && (arcMount < 0 || InArc(v, arcMount, held.Position));
            var now = _world.Time;
            if (holds && now < nextAt) return held;
            nextAt = now + RetargetSeconds;
            var best = BestInRange(v, weapon, favoured, arcMount, out var bestScore);
            if (!holds) return best;
            if (best == null || best == held) return held;
            return bestScore > SwitchMargin * Score(v, weapon, held!, favoured) ? best : held;
        }

        /// <summary>
        /// Play-test 8 A: what the commander AI's order should give way to: a target in reach that the weapon scores
        /// <see cref="OrderMargin"/> times as high as the ordered one, looked for every <see cref="RetargetSeconds"/> and held
        /// until the next look. An ordered structure or a target out of reach gives way only to an aircraft, and only for an
        /// anti-air weapon (the gun keeps shelling its building otherwise).
        /// </summary>
        private Vehicle? BetterThanOrder(Vehicle v, WeaponDef weapon, IDamageable ordered)
        {
            var now = _world.Time;
            if (now < v.RetargetAt)
                return Held(v, ordered.Id) is { } kept && IsValidAutoTarget(v, kept, weapon) ? kept : null;
            v.RetargetAt = now + RetargetSeconds;
            var best = BestInRange(v, weapon, ordered.Id, -1, out var bestScore);
            if (best == null || best.Id == ordered.Id) return null;
            float orderScore;
            if (ordered is Vehicle target && IsValidAutoTarget(v, target, weapon)) orderScore = Score(v, weapon, target, ordered.Id);
            else if (IsAntiAir(weapon) && best.Flying && !IsFlying(ordered)) orderScore = 0f;
            else return null;
            return bestScore > OrderMargin * orderScore ? best : null;
        }

        /// <summary>
        /// Coaxial and hull-fixed weapons can only hit what the vehicle is already pointed at;
        /// free mounts keep their target, else pick the best one in reach, favouring the main
        /// weapon's target.
        /// </summary>
        private IDamageable? SelectSecondaryTarget(Vehicle v, int index, IDamageable? primary)
        {
            var mount = v.Def.Mounts[index];
            var weapon = v.Arms[index];
            var side = IsSide(mount);
            if (mount.Aim == MountAim.Turret && primary == null && v.CoaxAir.IsValid && _world.TryGetVehicle(v.CoaxAir, out var chased) &&
                IsValidAutoTarget(v, chased, weapon))
                return chased;
            if (mount.Aim != MountAim.Free && !side) return primary != null && InReach(v, primary, weapon) && HasLineOfFire(v, primary, weapon) ? primary : null;
            var state = v.Weapons[index];
            var held = _world.TryGetVehicle(state.Target, out var current) ? current : null;
            // A side gun with nothing on its side takes the main weapon's target when it bears.
            if (side && (held == null || !IsValidAutoTarget(v, held, weapon) || !InArc(v, index, held.Position)) &&
                primary is Vehicle p && IsValidAutoTarget(v, p, weapon) && InArc(v, index, p.Position))
                held = p;
            // Play-test 8 A: a free mount keeps its target but weighs it every half second against the best in its reach
            // (a roof SAM on a tank turns on the helicopter that comes in), favouring the main weapon's.
            var best = Retarget(v, weapon, held, primary?.Id ?? EntityId.None, ref state.RetargetAt, side ? index : -1);
            if (best != null) return best;
            // An ordered attack on a building or barrel: the roof gun joins in.
            return primary != null && primary is not Vehicle && InReach(v, primary, weapon) && HasLineOfFire(v, primary, weapon) ? primary : null;
        }

        /// <summary>
        /// The most valuable enemy in range: one this weapon hurts most, one that is badly damaged
        /// or can be finished with this shot, and one teammates (or this vehicle's main gun) are
        /// already firing on. Distance only tips the balance between otherwise equal targets.
        /// </summary>
        private Vehicle? BestInRange(Vehicle v, WeaponDef weapon, EntityId favoured, int arcMount = -1) => BestInRange(v, weapon, favoured, arcMount, out _);

        private Vehicle? BestInRange(Vehicle v, WeaponDef weapon, EntityId favoured, int arcMount, out float bestScore)
        {
            Vehicle? best = null;
            bestScore = 0f;
            foreach (var other in _world.VehicleList)
            {
                if (!IsValidAutoTarget(v, other, weapon)) continue;
                if (arcMount >= 0 && !InArc(v, arcMount, other.Position)) continue;
                var score = Score(v, weapon, other, favoured);
                if (score <= bestScore) continue;
                best = other;
                bestScore = score;
            }
            return best;
        }

        /// <summary>
        /// What a valid target is worth to this weapon (0: it does nothing to it): how hard the weapon hits it (its damage
        /// type against the target's armour and the weapon's penetration against the face it would strike, and play-test 8 A:
        /// the weapon's own bonuses on it), how nearly finished it is, whether the weapon is made for its layer, whether
        /// teammates are on it, what it costs, and the threat it is (aiming at this vehicle, able to shoot back, armed).
        /// </summary>
        private float Score(Vehicle v, WeaponDef weapon, Vehicle other, EntityId favoured)
        {
            // Prompt 25 G: a gun with a second round is weighed with the round it would load for this target; whether it
            // is made for aircraft stays the gun's (an autocannon with an air-burst round still takes the ground first).
            var round = weapon.HasRounds ? RoundAgainst(v, weapon, other) : weapon;
            var effect = _world.Damage.Estimate(round, v, other);
            if (effect <= 0f) return 0f;
            effect *= DamageSystem.BonusFor(round, v, other, _world.Time);
            var score = (0.4f + effect) * (1.6f - other.Hp / other.MaxHp);
            // Guns and cannons turn on aircraft only when nothing on the ground is in reach;
            // anti-aircraft weapons go for aircraft first.
            // Prompt 19: a target on altitude tiers is fair game for any weapon that reaches its tier.
            if (other.Flying != IsAntiAir(weapon) && other.Tier == AltitudeTier.None) score *= 0.02f;
            if (other.Hp <= round.Damage * effect) score *= 1.5f;
            // An obstacle only when there is nothing else (the commander orders a breach itself).
            if (other.Def.Obstacle) score *= 0.05f;
            if (_focus.Contains((v.Team, other.Id)) || other.Id == favoured) score *= 1.3f;
            // The player has ordered the side at one of this boss's parts (prompt 9): units in reach turn on it.
            if (other.HasParts && _world.Bosses.IsFocused(v.Team, other.Id)) score *= 4f;
            // Ironclad's Bulwark: a dug-in tank draws the fire of enemies round it.
            if (other.Gear != null && _world.Gear.Taunts(other, v)) score *= 1.4f;
            // Worth more the more it costs (a titan before a jeep); one aiming at us first;
            // an unarmed truck last.
            score *= MathF.Sqrt(Math.Clamp(Worth(other), 2f, 25f) / 10f);
            if (other.Target == v.Id) score *= 1.2f;
            if (other.Def.Weapon.Damage <= 0f) score *= 0.3f;
            // Play-test 8 A: one that can hit this vehicle back before one that cannot.
            else if (other.Def.Weapon.CanTarget(v.Flying)) score *= ThreatWeight;
            // Slow, heavy weapons do not waste a shot on a target already as good as dead
            // from the rounds on their way to it (overkill).
            if (weapon.Cooldown >= 2f && _incoming.TryGetValue(other.Id, out var incoming) && incoming >= other.Hp * 1.1f) score *= 0.05f;
            // A stick of bombs (prompt 13 D.2): the group or the structure, not the lone light car beside it.
            if (weapon.Projectile == ProjectileKind.Bomb && weapon.Burst > 1) score *= BombWorth(v.Team, other, weapon);
            // Prompt 17 C: shield domes (the generator first), enemy CP relays, a stealth fighter's air-defence hunt.
            score *= NewContentWorth(v, other, weapon);
            // Prompt 25 F2 batch A: groups and big aircraft, prey, a towed gun's arc, decoys, linked towers.
            score *= P25Worth(v, other, weapon);
            // Prompt 26 B.9: a boss's area weapons look for the crowd, its guns for the dearest vehicle.
            score *= P26Worth(v, other, weapon);
            // Prompt 28: the squad's focus and tactic, a tower's mode, a boss's behaviour type, friends in the line of fire.
            score *= P28Worth(v, other, weapon);
            score /= 1f + 0.5f * Vector2.Distance(v.Position, other.Position) / MathF.Max(1f, weapon.Range);
            return score;
        }

        /// <summary>
        /// An aircraft for a turret machine gun (a tank's coaxial gun) while the main gun has
        /// nothing: the first turret mount that is a machine gun (firing in runs or from a magazine,
        /// test feedback 2) able to hit aircraft picks the best one in its reach.
        /// </summary>
        private Vehicle? CoaxAirTarget(Vehicle v)
        {
            if (v.Flying || v.Def.Mounts[0].Aim != MountAim.Turret || v.Def.Weapon.CanEngage(true, v.Def)) return null;
            var mounts = v.Def.Mounts;
            for (var i = 1; i < mounts.Count; i++)
            {
                var weapon = v.Arms[i];
                if (mounts[i].Aim != MountAim.Turret || !IsGun(weapon) || !weapon.CanTarget(true)) continue;
                if (_world.TryGetVehicle(v.CoaxAir, out var current) && current.Flying && IsValidAutoTarget(v, current, weapon)) return current;
                var best = BestInRange(v, weapon, EntityId.None);
                return best != null && best.Flying ? best : null;
            }
            return null;
        }

        /// <summary>
        /// Prompt 13 D.2: what a stick of bombs on this target is worth against a plain target: the enemies
        /// its blasts would reach (by their worth), a structure half as much again, a lone light vehicle a
        /// quarter, and a third for ground the side bombed in the last 10 s (a pause between runs on one place).
        /// </summary>
        internal float BombWorth(int team, Vehicle target, WeaponDef bombs)
        {
            if (target.Flying) return 1f;
            var reach = bombs.SplashRadius + 4f;
            var worth = 0f;
            var others = 0;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == team || e.Team < 0 || e.Flying || e.Def.Untargetable) continue;
                if (Vector2.DistanceSquared(e.Position, target.Position) > reach * reach) continue;
                worth += Math.Clamp(Worth(e), 1f, 25f);
                if (e != target) others++;
            }
            var factor = worth / Math.Clamp(Worth(target), 1f, 25f);
            if (target.Def.Static) factor *= 1.5f;
            else if (others == 0 && target.Armor == ArmorClass.Light && Worth(target) < 7f) factor *= 0.25f;
            if (RecentlyBombed(team, target.Position)) factor *= 0.33f;
            return factor;
        }

        /// <summary>Where each side's sticks of bombs fell, and when (a pause between runs on one place).</summary>
        private readonly List<(int team, Vector2 at, double when)> _bombed = new();

        private const float BombedRadius = 16f;
        private const double BombedSeconds = 10.0;

        internal bool RecentlyBombed(int team, Vector2 at)
        {
            var now = _world.Time;
            for (var i = _bombed.Count - 1; i >= 0; i--)
            {
                var (t, p, when) = _bombed[i];
                if (now - when > BombedSeconds)
                {
                    _bombed.RemoveAt(i);
                    continue;
                }
                if (t == team && Vector2.DistanceSquared(p, at) < BombedRadius * BombedRadius) return true;
            }
            return false;
        }

        /// <summary>A friendly ground vehicle within <paramref name="reach"/> of a point.</summary>
        private bool OwnNear(int team, Vector2 at, float reach)
        {
            foreach (var o in _world.VehicleList)
                if (o.IsAlive && o.Team == team && !o.Flying && !o.Def.Static && Vector2.DistanceSquared(o.Position, at) < (reach + o.Radius) * (reach + o.Radius)) return true;
            return false;
        }

        /// <summary>What a target is worth: its CP, or for units never bought (bosses, defences) a guess from their health.</summary>
        internal static float Worth(Vehicle v) => v.Def.CpCost > 0 ? v.Def.CpCost : v.Def.Boss ? 25f : v.MaxHp / 250f;

        /// <summary>Damage on its way to each target (rounds in flight), for overkill checks.</summary>
        private readonly Dictionary<EntityId, float> _incoming = new();

        /// <summary>A weapon made for aircraft: flak, or one that can only hit what flies.</summary>
        internal static bool IsAntiAir(WeaponDef weapon) => weapon.DamageType == DamageType.Fragmentation || weapon.Targets == TargetLayers.Air;

        /// <summary>An aeroplane's guns stay on the target of its strafing run while it is in reach.</summary>
        private bool RunTargetInReach(Vehicle v, WeaponDef weapon, out Vehicle target)
        {
            target = null!;
            return v.Def.FixedWing && _world.TryGetVehicle(v.RunTarget, out target) && IsValidAutoTarget(v, target, weapon);
        }

        private bool IsValidAutoTarget(Vehicle v, Vehicle target, WeaponDef weapon) =>
            target.IsAlive && !target.Invulnerable && !target.Def.Untargetable && !target.Truce && target.Team != v.Team && !_world.Ceasefire(v.Team, target.Team) && target.IsVisibleTo(v.Team) &&
            // Prompt 16: a coastal battery's guns fire on ships only.
            (!v.Def.NavalOnly || target.Def.Naval != null) && InReach(v, target, weapon) && HasLineOfFire(v, target, weapon);

        /// <summary>
        /// Direct fire needs a clear line: buildings, rock and fortress walls stop it. Aircraft
        /// fire over everything and are shot at over everything; artillery, mortars, rocket
        /// artillery, bombs and drones lob or fly over cover.
        /// </summary>
        public bool HasLineOfFire(Vehicle v, IDamageable target, WeaponDef weapon)
        {
            if (v.Flying || IsFlying(target) || weapon.Indirect) return true;
            return !_world.Cover.TryFirstHit(v.Position, target.Position, v.Radius * 0.6f, target is Vehicle ? target.Radius * 0.5f : 0f,
                target as Prop, out _);
        }

        private bool InReach(Vehicle v, IDamageable target, WeaponDef weapon)
        {
            // Prompt 19 B: a target on altitude tiers is reached by the weapons for its tier (a railgun at low, only
            // long-range SAMs and fighters at high, nothing in orbit); everything else by the ordinary air/ground rule.
            // Prompt 25 G: a gun reaches whatever one of its rounds can hit (an autocannon's air-burst round, aircraft).
            if (target is Vehicle { Tier: not AltitudeTier.None } tiered ? !TierRules.Reaches(weapon, v.Def, tiered.Tier, true) : !weapon.CanEngage(IsFlying(target), v.Def))
                return false;
            var distance = Vector2.Distance(v.Position, target.Position);
            var reach = weapon.Range * _world.Gear.Reach(v, target, weapon);
            // Prompt 25 F2 batch A: a heavy flak gun lowered at the ground reaches less far; a long-range missile has a minimum reach.
            if (weapon.GroundRange > 0f && !IsFlying(target)) reach *= weapon.GroundRange / weapon.Range;
            if (weapon.MinReach > 0f && distance - target.Radius < weapon.MinReach) return false;
            // Play-test 8 A: a free-falling bomb reaches as far ahead as the middle of its stick falls.
            if (FreeFall(v, weapon)) reach = MathF.Max(reach, BombReach(v, weapon));
            // Radar-absorbent coating: a missile must come closer to lock on.
            if (weapon.Projectile == ProjectileKind.Missile && target is Vehicle { Gear: { } coated }) reach *= 1f - Math.Clamp(coated.Stat(StatId.LockRange), 0f, 0.5f);
            return distance >= weapon.MinRange && distance - target.Radius <= reach;
        }

        private static bool IsFlying(IDamageable target) => target is Vehicle vehicle && vehicle.Flying;

        /// <summary>Fires the mount when it can, and keeps an ongoing salvo going.</summary>
        private void Operate(Vehicle v, int index, IDamageable? target, float dt)
        {
            var state = v.Weapons[index];
            var weapon = v.Arms[index];
            if (state.BurstLeft > 0)
            {
                // A salvo keeps going at the point first aimed at even if the target dies or the turret turns.
                state.BurstTimer -= dt;
                while (state.BurstLeft > 0 && state.BurstTimer <= 0f)
                {
                    // Prompt 17 C: each drone of a swarm picks its own target round the salvo's aim.
                    if (weapon.SwarmReach > 0f && !state.BurstFlying && SwarmTarget(v, weapon, state.BurstAim) is { } next)
                        Launch(v, index, next.Position, next.Id, false, state.BurstScale, false, next);
                    else
                    {
                        var alive = _world.TryGetTarget(state.BurstTarget, out var t) && t.IsAlive;
                        // Prompt 34 L4: each volley of a simultaneous gun is every barrel at once.
                        for (var b = Loaded(v, index).RoundsPerPull; b > 0; b--)
                            Launch(v, index, alive ? t.Position : state.BurstAim, state.BurstTarget, state.BurstFlying, state.BurstScale, false, alive ? t : null);
                    }
                    state.BurstLeft--;
                    state.BurstTimer += weapon.Burst > 1 ? weapon.BurstInterval : TwinGap;
                }
                if (state.BurstLeft == 0) state.Cooldown = weapon.Cooldown;
                return;
            }

            // Prompt 25 G: a gun changing rounds fires nothing until the new round is in.
            if (!KeepRound(v, index, target)) return;
            // A charged weapon powering up: it fires when the charge is full, whatever it aims at
            // by then (the charge is the target's warning); lost targets let it wait at full charge.
            if (state.ChargeLeft > 0f)
            {
                state.ChargeLeft -= dt;
                if (state.ChargeLeft > 0f) return;
                state.ChargeLeft = 0f;
                if (target == null || !InReach(v, target, weapon)) return;
            }
            // Limited ammunition: one round per trigger pull (a whole salvo counts as one).
            else if (target == null || state.Ammo == 0 || !CanFire(v, index, target) || !InRhythm(v, index)) return;
            else if (weapon.Charge > 0f)
            {
                state.ChargeLeft = weapon.Charge;
                _world.Emit(SimEvent.Charging(v, index, weapon.Charge, target.Position));
                return;
            }
            // An aircraft's stores (prompt 13 C): the salvo is what is left of them (a Grad-like ripple of
            // rockets from a half-empty pod fires half a ripple); a launcher's magazine counts trigger pulls.
            // Prompt 25 G: the round in the gun sets the salvo (a guided shell goes one at a time).
            var salvo = Loaded(v, index).Burst;
            if (state.Load > 0)
            {
                salvo = Math.Min(salvo, Math.Max(0, state.Ammo));
                state.Ammo -= salvo;
            }
            else if (state.Ammo > 0) state.Ammo--;
            if (weapon.Projectile == ProjectileKind.Bomb && salvo > 1) _bombed.Add((v.Team, target.Position, _world.Time));
            // Shoot-and-scoot (the SP gun): rounds fired from this spot.
            if (index == 0 && v.Def.Scoot != null) v.ScootShots++;
            if (weapon.Clip > 0)
            {
                Stream(v, index, target);
                return;
            }
            var machineGun = IsMachineGun(weapon);
            var scale = machineGun ? RunDamage : 1f;
            // Equipment on the main weapon: extra rounds per pull (Twin Feed, Strafing Run).
            var extra = 0;
            var perRound = 1f;
            if (index == 0 && v.Gear != null)
            {
                if (machineGun) scale *= _world.Gear.MachineGunRound(v);
                else extra = _world.Gear.ExtraRounds(v, weapon, out perRound);
            }
            // Play-test 6 (DECISIONS 21F): a swarm's drones go one at a time now; each still picks its own target round the aim.
            if (weapon.SwarmReach > 0f && weapon.Burst <= 1 && !IsFlying(target) && SwarmTarget(v, weapon, target.Position, state) is { } own)
            {
                state.SwarmBefore = state.SwarmLast;
                state.SwarmLast = own.Id;
                Launch(v, index, own.Position, own.Id, false, scale * perRound, true, own);
            }
            else
            {
                Launch(v, index, target.Position, target.Id, IsFlying(target), scale * perRound, true, target);
                // Prompt 34 L4: a simultaneous gun's other barrels fire in the same tick (one volley, one trigger pull).
                for (var b = Loaded(v, index).RoundsPerPull - 1; b > 0; b--)
                    Launch(v, index, target.Position, target.Id, IsFlying(target), scale * perRound, false, target);
            }
            if (machineGun)
            {
                // A run of fire, then a pause while the gunner re-lays (its damage rides on the rounds).
                state.Cooldown = weapon.Cooldown * Jitter();
                if (--state.RunLeft <= 0) state.Cooldown = RestSeconds * (0.7f + 0.6f * (float)_world.Random.NextDouble());
                return;
            }
            if (salvo > 1 || extra > 0)
            {
                state.BurstLeft = salvo - 1 + extra;
                state.BurstTimer = weapon.Burst > 1 ? weapon.BurstInterval : TwinGap;
                state.BurstTarget = target.Id;
                state.BurstAim = target.Position;
                state.BurstFlying = IsFlying(target);
                state.BurstScale = perRound;
            }
            else
            {
                state.Cooldown = weapon.Cooldown * Jitter();
            }
        }

        /// <summary>Seconds between a single-shot gun's round and the second one Twin Feed adds.</summary>
        private const float TwinGap = 0.15f;

        /// <summary>
        /// Sustained fire from a magazine (test feedback 11C): the rounds due this step, one
        /// cadence apart, at the target the mount is laid on; then, when the magazine is empty,
        /// the pause to change it. A lull as long as that pause tops a part-used magazine up.
        /// Machine-gun equipment applies (Strafing Run's doubled rounds, Twin Feed's harder ones);
        /// the data's damage is each round's own (no run factor).
        /// </summary>
        private void Stream(Vehicle v, int index, IDamageable target)
        {
            var state = v.Weapons[index];
            var weapon = v.Arms[index];
            var now = _world.Time;
            // Picking up again after a pause: no credit from the idle time.
            if (now - state.LastRoundAt > weapon.Cooldown + 0.06) state.Cooldown = MathF.Max(0f, state.Cooldown);
            if (state.ClipLeft <= 0 || now - state.LastRoundAt >= MathF.Max(0.5f, weapon.ClipReload)) state.ClipLeft = weapon.Clip;
            var flying = IsFlying(target);
            // At most three rounds a step (60 a second): the cadence, not the frame, sets the rate.
            for (var k = 0; k < 3 && state.Cooldown <= 0f && state.ClipLeft > 0; k++)
            {
                var scale = index == 0 && v.Gear != null ? _world.Gear.MachineGunRound(v) : 1f;
                Launch(v, index, target.Position, target.Id, flying, scale, true, target);
                state.ClipLeft--;
                state.Cooldown += weapon.Cooldown * Jitter();
            }
            state.LastRoundAt = now;
            // An empty magazine: the pause to change it (a little different every time).
            if (state.ClipLeft <= 0) state.Cooldown = MathF.Max(state.Cooldown, weapon.ClipReload * (0.9f + 0.2f * (float)_world.Random.NextDouble()));
        }

        /// <summary>A machine gun: bullets fired faster than three a second, one at a time, in runs (not from a magazine).</summary>
        private static bool IsMachineGun(WeaponDef weapon) =>
            weapon.Clip <= 0 && weapon.Projectile == ProjectileKind.Bullet && weapon.Cooldown < 0.35f && weapon.Burst <= 1;

        /// <summary>
        /// A gun in the fire rhythm: a machine gun, or a gun firing from a magazine (it opens up after a short random
        /// delay the first time; play-test 7: it no longer waits for the vehicle's other weapons).
        /// </summary>
        private static bool IsGun(WeaponDef weapon) => weapon.Clip > 0 || IsMachineGun(weapon);

        /// <summary>Rounds per run of machine-gun fire, and the pause after it.</summary>
        private const int RunShortest = 6, RunLongest = 10;
        private const float RestSeconds = 1.0f;

        /// <summary>
        /// Machine-gun rounds carry the damage of the pauses between runs, so a gun firing in
        /// bursts hurts as much per minute as one that never let go: (run + pause) / run for an
        /// average run of 8 rounds at a typical 0.18 s and a 1 s pause.
        /// </summary>
        private const float RunDamage = 1.7f;

        /// <summary>No two shots are exactly as far apart: up to 10 % either way, so identical vehicles fall out of step.</summary>
        private float Jitter() => 0.9f + 0.2f * (float)_world.Random.NextDouble();

        /// <summary>Twin barrels (two mounts of one weapon) open fire at least this many seconds apart, never in lockstep.</summary>
        internal const float TwinOffset = 0.1f;

        /// <summary>
        /// Play-test 7 (DECISIONS 22P): every mount fires on its own timing, as a real crew's guns do. The main gun, the
        /// coaxial and roof machine guns, the missiles and the rockets of one vehicle, tower or boss no longer wait for
        /// each other's rounds, salvos, magazines or streams (11B-12D's turns, 20W's and 21F's exceptions and the bosses'
        /// one-mount-a-step rule are gone). What is left: a gun opens up after a short random delay the first time (so
        /// identical vehicles fall out of step), a machine gun fires runs of 6 to 10 rounds and pauses, and twin barrels
        /// (two mounts of the same weapon) never open fire in the same instant: the second waits <see cref="TwinOffset"/>
        /// after the first; once firing, each keeps its own cadence (each round's 10 % jitter keeps them apart).
        /// </summary>
        private bool InRhythm(Vehicle v, int index)
        {
            var weapon = v.Arms[index];
            var now = _world.Time;
            var state = v.Weapons[index];
            if (IsGun(weapon) && !state.Started)
            {
                state.Started = true;
                state.Cooldown = 0.2f + 0.8f * (float)_world.Random.NextDouble();
                return false;
            }
            // Opening fire (not the next round of a stream or a run already under way).
            if (now - state.FiredAt > weapon.Cooldown * 1.1f + 0.06f)
            {
                if (TwinJustOpened(v, index, now)) return false;
                state.OpenedAt = now;
            }
            if (IsMachineGun(weapon) && state.RunLeft <= 0) state.RunLeft = _world.Random.Next(RunShortest, RunLongest + 1);
            return true;
        }

        /// <summary>Another mount of the same weapon (a twin barrel) opened fire less than <see cref="TwinOffset"/> ago.</summary>
        private static bool TwinJustOpened(Vehicle v, int index, double now)
        {
            var id = v.Arms[index].Id;
            for (var i = 0; i < v.Weapons.Length; i++)
                if (i != index && v.Arms[i].Id == id && now - v.Weapons[i].OpenedAt < TwinOffset) return true;
            return false;
        }

        private bool CanFire(Vehicle v, int index, IDamageable target)
        {
            var mount = v.Def.Mounts[index];
            if (v.Weapons[index].Cooldown > 0f) return false;
            // Prompt 25 G: the round in the gun must be one for this target's layer (it changes after its 2 s).
            if (!LoadedReaches(v, index, target)) return false;
            // Prompt 13 D.2: no bombs where friends are too close to where they would fall.
            // Play-test 8 A: a free-falling stick is judged where it will come down, not at the target.
            var freeFall = FreeFall(v, v.Arms[index]);
            if (v.Arms[index].Projectile == ProjectileKind.Bomb &&
                (freeFall ? StickNearOwn(v, index) : OwnNear(v.Team, target.Position, v.Arms[index].SplashRadius + 3f))) return false;
            // Artillery and rocket launchers must stop to fire their main weapon; their machine guns need not.
            if (index == 0 && !v.Def.FiresWhileMoving && v.IsMoving) return false;
            if (!InReach(v, target, v.Arms[index]) || !HasLineOfFire(v, target, v.Arms[index])) return false;
            // Prompt 25 F2 batch A: one fibre-optic drone in the air at a time.
            if (v.Arms[index].OneAtATime && InFlightFrom(v, index)) return false;
            var desired = SimMath.HeadingOf(target.Position - v.Position);
            if (IsSide(mount) && !InArc(v, index, target.Position)) return false;
            if (freeFall) return StickStraddles(v, index, target);
            var tolerance = mount.Aim switch
            {
                MountAim.Turret => TurretTolerance,
                MountAim.Free or MountAim.Left or MountAim.Right => FreeTolerance,
                _ => HullTolerance,
            };
            // Play-test 6 (DECISIONS 21F): an aircraft's drone bay lets its drones go whichever way it faces (they fly to their
            // own targets), so the mothership releases them one after another all through its pass, not only nose-on.
            if (v.Flying && v.Arms[index].Projectile == ProjectileKind.Drone) return true;
            return MathF.Abs(SimMath.WrapAngle(desired - v.MountHeading(index))) <= tolerance;
        }

        /// <summary>A broadside gun (out of the left or right side), or a mount with a firing arc of its own (prompt 9: the Bastion's corner turrets).</summary>
        private static bool IsSide(WeaponMount mount) => mount.Aim is MountAim.Left or MountAim.Right || mount.ArcHalf > 0f;

        /// <summary>How far either way of square to its side a broadside gun can aim.</summary>
        private const float SideArc = MathF.PI / 3f;

        /// <summary>The heading square out of a side mount's side of the hull (or the middle of its own arc).</summary>
        private static float SideCentre(Vehicle v, int index)
        {
            var mount = v.Def.Mounts[index];
            if (mount.ArcHalf > 0f) return v.Heading + mount.ArcCentre;
            return v.Heading + (mount.Aim == MountAim.Left ? -MathF.PI * 0.5f : MathF.PI * 0.5f);
        }

        private static float ArcOf(Vehicle v, int index) => v.Def.Mounts[index].ArcHalf > 0f ? v.Def.Mounts[index].ArcHalf : SideArc;

        private static bool InArc(Vehicle v, int index, Vector2 at) =>
            MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(at - v.Position) - SideCentre(v, index))) <= ArcOf(v, index);

        /// <summary>A broadside gun follows its target within its arc; with none it rests square to its side.</summary>
        private static void AimSide(Vehicle v, int index, IDamageable? target, float dt)
        {
            var centre = SideCentre(v, index);
            var aim = centre;
            if (target != null)
            {
                var off = SimMath.WrapAngle(SimMath.HeadingOf(target.Position - v.Position) - centre);
                aim = centre + Math.Clamp(off, -ArcOf(v, index), ArcOf(v, index));
            }
            var state = v.Weapons[index];
            state.Heading = SimMath.RotateTowards(state.Heading, aim, FreeMountTurnRate * dt);
        }

        private void Launch(Vehicle shooter, int index, Vector2 aimAt, EntityId target, bool targetFlying, float damageScale = 1f, bool pull = true,
            IDamageable? aimTarget = null)
        {
            // Prompt 17 D.6, prompt 25 G: the round in the gun (its own, or the second round it loaded for this target).
            var weapon = Loaded(shooter, index);
            shooter.LastFiredAt = _world.Time;
            shooter.Weapons[index].FiredAt = _world.Time;
            if (index == 0 && shooter.Def.Kamikaze)
            {
                _world.Damage.Detonate(shooter, weapon);
                return;
            }
            // Equipment: a fire-control computer leads a moving target; traits on the shot itself.
            var mods = ShotMods.Plain;
            if (shooter.Gear != null)
            {
                if (aimTarget != null) aimAt = _world.Gear.Lead(shooter, index, aimTarget, aimAt, weapon);
                mods = _world.Gear.Shot(shooter, index, target, aimAt, weapon, pull);
                damageScale *= mods.Scale * _world.Gear.PintleScale(shooter, index, targetFlying);
            }
            // Fix prompt L4 rule D: unguided rockets, shells, mortars and bombs aim where a moving ground target will be
            // after their flight (in place of the fire-control computer's lead, which only the main gun had).
            if (aimTarget is Vehicle mover && !targetFlying && Leads(weapon, FreeFall(shooter, weapon)))
                aimAt = LeadPoint(shooter, mover, weapon, _world.Catalog.Munitions.LeadCap);
            if (pull) _world.Gear.Fired(shooter, weapon);
            // Prompt 17 C: a wingman may pull an anti-air missile onto itself; the laser's damage ramps up on one target.
            var pulled = WingmanPull(shooter, weapon, target, targetFlying);
            if (pulled != target && _world.TryGetVehicle(pulled, out var wingman))
            {
                target = pulled;
                aimAt = wingman.Position;
                aimTarget = wingman;
            }
            if (weapon.Ramp != null) damageScale *= RampScale(shooter, index, target);
            // A boss with parts: the round goes at one of them (or at the body).
            // Play-test 8 A: a free-falling bomb lands where its drop point and its fall put it (the aircraft's speed carries
            // it on ahead as it drops), not on the target: a stick's bombs come down one after another along the track.
            var freeFall = FreeFall(shooter, weapon);
            if (freeFall) aimAt = BombImpact(shooter);
            var part = !freeFall && aimTarget is Vehicle { HasParts: true } boss && target == boss.Id ? _world.Bosses.ChoosePart(shooter, boss, weapon) : -1;
            if (part >= 0 && aimTarget is Vehicle partOf) aimAt = partOf.PartPosition(part);
            var distance = Vector2.Distance(shooter.Position, aimAt);
            // Rounds scatter more the farther they fly: tight up close, and at the edge of range
            // wide enough that a long shot can miss outright.
            // The gun's reach (a second round's is its gun's; equipment may lengthen the gun's own).
            var reach = Math.Clamp(distance / shooter.Arms[index].Range, 0f, 1.2f);
            var spread = weapon.Guided || weapon.GuidedRocket ? 0f : freeFall ? weapon.Spread * FreeFallScatter : weapon.Spread * (0.35f + 1.25f * MathF.Pow(reach, 1.4f));
            // A boss's broken fire-control radar: its guns scatter wider.
            if (index < shooter.MountSpread.Length) spread *= shooter.MountSpread[index];
            // Prompt 28 I.8: hit and run pays for firing while backing off.
            if (shooter.AiKiting && shooter.IsMoving) spread *= 1.3f;
            // An escort spotter's mark (prompt 16 F): the boss's guns fall tighter on the marked target.
            if (shooter.Def.Boss && spread > 0f && aimTarget is Vehicle spotted && Marked(spotted, shooter.Team)) spread *= _world.Catalog.EscortRules.SpotSpread;
            if (!weapon.Guided && spread > 0f && (shooter.Gear != null || aimTarget is Vehicle { Gear: not null }))
                spread *= _world.Gear.SpreadFactor(shooter, index, aimTarget, reach);
            // Artillery brackets its target (Wargame and real gunnery): the first round lands wide,
            // each correction brings the fall of shot in, down to 0.4 of the spread.
            if (weapon.MinRange > 0f && weapon.Projectile is ProjectileKind.Shell or ProjectileKind.Rocket)
            {
                var state = shooter.Weapons[index];
                if (target.IsValid && state.BracketTarget == target) state.BracketShots++;
                else
                {
                    state.BracketTarget = target;
                    state.BracketShots = 0;
                }
                spread *= MathF.Max(0.4f, 1.6f * MathF.Pow(0.7f, state.BracketShots));
                // A target its side has marked (a designator's laser, a radar's fix, a UAV over it): the
                // SP gun's rounds fall almost on the mark (prompt 8 A.2).
                if (index == 0 && shooter.Def.MarkedSpread < 1f && aimTarget is Vehicle marked && Marked(marked, shooter.Team)) spread *= shooter.Def.MarkedSpread;
                // Prompt 20 I.7: an Argus directing its side's fire (its radar standing).
                spread *= _world.Bosses.SpotAuraFor(shooter.Team);
            }
            // Prompt 25 F2 batch A: dazzled by an enemy searchlight in the dark; bombs over an enemy barrage balloon.
            if (!weapon.Guided && spread > 0f) spread *= _world.Works.SpreadFactor(shooter, weapon, aimAt);
            var aim = aimAt + RandomInCircle(spread);
            var origin = shooter.Position + SimMath.Forward(shooter.MountHeading(index)) * shooter.Radius;
            // A direct-fire round that meets a wall on its way (the spread took it wide, or the
            // target slipped behind a building mid-salvo) bursts on the wall and damages it.
            if (!shooter.Flying && !targetFlying && !weapon.Indirect)
            {
                _world.TryGetTarget(target, out var aimed);
                if (_world.Cover.TryFirstHit(origin, aim, 0.2f, 0f, aimed as Prop, out var wall))
                {
                    aim = wall;
                    target = _world.CoverAt(wall)?.Id ?? EntityId.None;
                }
            }
            var travel = Vector2.Distance(origin, aim) / weapon.ProjectileSpeed;
            // A bomb keeps the aircraft's forward speed as it falls, so it lands under the aircraft
            // as it passes over, not ahead of it.
            if (freeFall) travel = BombFall(shooter);
            else if (weapon.Projectile == ProjectileKind.Bomb && shooter.Flying)
                travel = MathF.Max(0.8f, Vector2.Distance(origin, aim) / MathF.Max(8f, shooter.Speed));
            // Prompt 25 F2 batch A: a glide bomb flies at its own speed; a simultaneous-impact salvo lands together.
            if (weapon.Glides) travel = Vector2.Distance(origin, aim) / weapon.ProjectileSpeed;
            travel = MrsiTravel(shooter, index, pull, travel);
            // Prompt 34 L3: a boss's T4+ round (203 mm and up, the Smerch, the 400 kg bombs) lands no sooner than its escape warning,
            // so the warning ring on its fall point shows that long. A guided round chases its target and has no fixed fall point.
            // Fix prompt L5: every shooter's warned round, not only a boss's (the view rings the enemy's; both sides alike here).
            if (weapon.WarnSeconds > travel && _world.Catalog.Warnings.Warns(weapon)) travel = weapon.WarnSeconds;

            damageScale *= shooter.DamageBoost * shooter.CommandDamage * shooter.Def.DamageScale;
            // Prompt 32 L4: a mount's own scale (a Fortress HQ's gun by HQ level).
            if (index >= 0 && index < shooter.Weapons.Length) damageScale *= shooter.Weapons[index].DamageScale;
            // Prompt 25 F2 batch A: a tower linked by a fire-control centre.
            damageScale *= shooter.LinkDamage;
            // Prompt 25 C1: a boss's own weapon damage (the sheet's target damage a second against armour 3), on the ground only:
            // its anti-air keeps its numbers.
            if (!targetFlying) damageScale *= shooter.Def.WeaponDamage;
            // Prompt 29 S03: the vehicle's own damage on every weapon (never the weapon's data, R8).
            damageScale *= shooter.Def.OutgoingDamageMult;
            // A gun pit's first shot on rising (the Ambush branch).
            if (index == 0 && shooter.AmbushReady && shooter.Def.Hidden is { } pit)
            {
                damageScale *= pit.FirstShot;
                shooter.AmbushReady = false;
            }
            var projectile = new Projectile(shooter.Id, shooter.Team, weapon, aim, target, travel, targetFlying)
            {
                DamageScale = damageScale, Origin = origin, Shooter = shooter, Main = index == 0, Tandem = mods.Tandem, ExtraSplash = mods.ExtraSplash,
                NoCluster = mods.NoCluster, Part = part, LaunchedAt = _world.Time,
            };
            if (target.IsValid && _world.TryGetVehicle(target, out var aimedAt))
            {
                projectile.Incoming = weapon.Damage * damageScale * _world.Damage.Estimate(weapon, shooter, aimedAt);
                _incoming[target] = (_incoming.TryGetValue(target, out var already) ? already : 0f) + projectile.Incoming;
            }
            // Guided rounds are reliable up close; at the edge of their range one in ten loses lock.
            var fail = index < shooter.MountFail.Length ? shooter.MountFail[index] : 0f;
            if (weapon.Guided && _world.Random.NextDouble() < 0.02 + 0.08 * reach * reach + fail) projectile.Failed = true;
            // Prompt 22 F: Dr. Venn's drones shrug off part of the jamming.
            if (weapon.Guided && (_world.Abilities.Jammed(shooter.Position, shooter.Team) || _world.Abilities.Jammed(aimAt, shooter.Team)) && !_world.ShrugsJam(shooter, weapon) && !weapon.JamProof)
                projectile.Jammed = true;
            if (weapon.Guided)
            {
                var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                projectile.Miss = new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (5f + (float)_world.Random.NextDouble() * 6f);
            }
            _projectiles.Add(projectile);
            var wide = projectile.Jammed || projectile.Failed ? projectile.Miss : default;
            _world.Emit(SimEvent.Fired(shooter, index, origin, aim, travel, target, wide, projectile.Jammed, weapon));
        }

        /// <summary>
        /// A target <paramref name="team"/> has marked: a laser designator's mark, a counter-battery
        /// radar's reveal, or a UAV scan over it.
        /// </summary>
        internal bool Marked(Vehicle target, int team)
        {
            var now = _world.Time;
            ref var mark = ref target.Statuses[(int)StatusKind.Mark];
            if (mark.Until > now && mark.Team == team) return true;
            ref var reveal = ref target.Statuses[(int)StatusKind.Reveal];
            if (reveal.Until > now && team is >= 0 and < 31 && (reveal.Stacks & (1 << team)) != 0) return true;
            return team is >= 0 and < 31 && (_world.Strikes.ScanMask(target.Position, target.Team) & (1 << team)) != 0;
        }

        private void UpdateProjectiles(float dt)
        {
            EngageIncoming(dt);
            // Fix prompt L4: flares, lost sight and reach take guided rounds off their targets in flight.
            GuideRounds();
            for (var i = _projectiles.Count - 1; i >= 0; i--)
            {
                var p = _projectiles[i];
                p.TimeLeft -= dt;
                if (p.TimeLeft > 0f) continue;
                _projectiles[i] = _projectiles[_projectiles.Count - 1];
                _projectiles.RemoveAt(_projectiles.Count - 1);
                if (p.Incoming > 0f && _incoming.TryGetValue(p.Target, out var due))
                {
                    if (due - p.Incoming > 0.01f) _incoming[p.Target] = due - p.Incoming;
                    else _incoming.Remove(p.Target);
                }
                _world.Damage.ResolveImpact(p);
            }
        }

        private Vector2 RandomInCircle(float radius)
        {
            if (radius <= 0f) return Vector2.Zero;
            var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
            var r = radius * MathF.Sqrt((float)_world.Random.NextDouble());
            return new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * r;
        }
    }
}
