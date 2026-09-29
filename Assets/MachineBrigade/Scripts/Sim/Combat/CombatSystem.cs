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
                    v.Weapons[i].Cooldown = MathF.Max(v.Arms[i].Clip > 0 ? -dt : 0f, v.Weapons[i].Cooldown - dt * v.FireFactor);
                ReloadMagazines(v, dt);
                // Knocked out by an EMP: the crew can do nothing until it wears off. An obstacle, a
                // minefield or a module has nothing to fire; a gun pit down in its hole waits.
                // Prompt 17 C: a bunker vehicle digging in or packing up does not fire either.
                // Prompt 19: a tiered boss in orbit holds its fire (its big attack is the boss system's).
                if (v.Stunned || v.Lowered || v.HoldFire || v.Def.Passive || v.Burrowed || v.DeployBusy || v.Tier == AltitudeTier.Orbit)
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
                    if (ordered is Vehicle { Invulnerable: true }) return BestInRange(v, weapon, EntityId.None);
                    return ordered is Vehicle hidden && !hidden.IsVisibleTo(v.Team) ? null : ordered;

                case OrderKind.AttackMove:
                    if (RunTargetInReach(v, weapon, out var run)) return run;
                    if (_world.TryGetVehicle(v.Engaged, out var engaged) && IsValidAutoTarget(v, engaged, weapon)) return engaged;
                    return BestInRange(v, weapon, EntityId.None);

                case OrderKind.Idle:
                    if (RunTargetInReach(v, weapon, out var runIdle)) return runIdle;
                    // A counter-battery gun leaves what it was shelling for the enemy gun that just fired (DECISIONS 19T).
                    if (CounterBatteryTarget(v, weapon) is { } gun) return gun;
                    if (_world.TryGetVehicle(v.Target, out var current) && IsValidAutoTarget(v, current, weapon)) return current;
                    return BestInRange(v, weapon, EntityId.None);

                case OrderKind.Move:
                case OrderKind.Retreat:
                    // Targets of opportunity only: firing never changes the route (V2 R04).
                    return v.Def.FiresWhileMoving || tankGun != null ? BestInRange(v, weapon, EntityId.None) : null;

                default:
                    return null;
            }
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
            if (_world.TryGetVehicle(v.Weapons[index].Target, out var current) && IsValidAutoTarget(v, current, weapon) &&
                (!side || InArc(v, index, current.Position)))
                return current;
            // A side gun takes the main weapon's target when it bears, else the best one on its side.
            if (side && primary is Vehicle p && IsValidAutoTarget(v, p, weapon) && InArc(v, index, p.Position)) return p;
            var best = BestInRange(v, weapon, primary?.Id ?? EntityId.None, side ? index : -1);
            if (best != null) return best;
            // An ordered attack on a building or barrel: the roof gun joins in.
            return primary != null && primary is not Vehicle && InReach(v, primary, weapon) && HasLineOfFire(v, primary, weapon) ? primary : null;
        }

        /// <summary>
        /// The most valuable enemy in range: one this weapon hurts most, one that is badly damaged
        /// or can be finished with this shot, and one teammates (or this vehicle's main gun) are
        /// already firing on. Distance only tips the balance between otherwise equal targets.
        /// </summary>
        private Vehicle? BestInRange(Vehicle v, WeaponDef weapon, EntityId favoured, int arcMount = -1)
        {
            Vehicle? best = null;
            var bestScore = 0f;
            foreach (var other in _world.VehicleList)
            {
                if (!IsValidAutoTarget(v, other, weapon)) continue;
                if (arcMount >= 0 && !InArc(v, arcMount, other.Position)) continue;
                var effect = _world.Damage.Estimate(weapon, v, other);
                if (effect <= 0f) continue;
                var score = (0.4f + effect) * (1.6f - other.Hp / other.MaxHp);
                // Guns and cannons turn on aircraft only when nothing on the ground is in reach;
                // anti-aircraft weapons go for aircraft first.
                // Prompt 19: a target on altitude tiers is fair game for any weapon that reaches its tier.
                if (other.Flying != IsAntiAir(weapon) && other.Tier == AltitudeTier.None) score *= 0.02f;
                if (other.Hp <= weapon.Damage * effect) score *= 1.5f;
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
                // Slow, heavy weapons do not waste a shot on a target already as good as dead
                // from the rounds on their way to it (overkill).
                if (weapon.Cooldown >= 2f && _incoming.TryGetValue(other.Id, out var incoming) && incoming >= other.Hp * 1.1f) score *= 0.05f;
                // A stick of bombs (prompt 13 D.2): the group or the structure, not the lone light car beside it.
                if (weapon.Projectile == ProjectileKind.Bomb && weapon.Burst > 1) score *= BombWorth(v.Team, other, weapon);
                // Prompt 17 C: shield domes (the generator first), enemy CP relays, a stealth fighter's air-defence hunt.
                score *= NewContentWorth(v, other, weapon);
                score /= 1f + 0.5f * Vector2.Distance(v.Position, other.Position) / MathF.Max(1f, weapon.Range);
                if (score <= bestScore) continue;
                best = other;
                bestScore = score;
            }
            return best;
        }

        /// <summary>
        /// An aircraft for a turret machine gun (a tank's coaxial gun) while the main gun has
        /// nothing: the first turret mount that is a machine gun (firing in runs or from a magazine,
        /// test feedback 2) able to hit aircraft picks the best one in its reach.
        /// </summary>
        private Vehicle? CoaxAirTarget(Vehicle v)
        {
            if (v.Flying || v.Def.Mounts[0].Aim != MountAim.Turret || v.Def.Weapon.CanTarget(true)) return null;
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
            target.IsAlive && !target.Invulnerable && !target.Def.Untargetable && target.Team != v.Team && target.IsVisibleTo(v.Team) &&
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
            if (target is Vehicle { Tier: not AltitudeTier.None } tiered ? !TierRules.Reaches(weapon, v.Def, tiered.Tier, true) : !weapon.CanTarget(IsFlying(target)))
                return false;
            var distance = Vector2.Distance(v.Position, target.Position);
            var reach = weapon.Range * _world.Gear.Reach(v, target, weapon);
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
                        Launch(v, index, alive ? t.Position : state.BurstAim, state.BurstTarget, state.BurstFlying, state.BurstScale, false, alive ? t : null);
                    }
                    state.BurstLeft--;
                    state.BurstTimer += weapon.Burst > 1 ? weapon.BurstInterval : TwinGap;
                }
                if (state.BurstLeft == 0) state.Cooldown = weapon.Cooldown;
                return;
            }

            // A charged weapon powering up: it fires when the charge is full, whatever it aims at
            // by then (the charge is the target's warning); lost targets let it wait at full charge.
            if (state.ChargeLeft > 0f)
            {
                state.ChargeLeft -= dt;
                if (state.ChargeLeft > 0f) return;
                state.ChargeLeft = 0f;
                if (target == null || !InReach(v, target, weapon)) return;
            }
            // Limited ammunition: one round per trigger pull (a whole salvo counts as one). An empty
            // launcher never takes its turn from the machine gun.
            else if (target == null || state.Ammo == 0 || !CanFire(v, index, target) || !InRhythm(v, index)) return;
            else if (weapon.Charge > 0f)
            {
                state.ChargeLeft = weapon.Charge;
                _world.Emit(SimEvent.Charging(v, index, weapon.Charge, target.Position));
                return;
            }
            // An aircraft's stores (prompt 13 C): the salvo is what is left of them (a Grad-like ripple of
            // rockets from a half-empty pod fires half a ripple); a launcher's magazine counts trigger pulls.
            var salvo = weapon.Burst;
            if (state.Load > 0)
            {
                salvo = Math.Min(weapon.Burst, Math.Max(0, state.Ammo));
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
            Launch(v, index, target.Position, target.Id, IsFlying(target), scale * perRound, true, target);
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
        /// A gun in the fire rhythm: a machine gun, or a gun firing from a magazine. Guns take turns
        /// with each other and give way to heavy weapons (main guns, missiles, rockets).
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

        /// <summary>Quiet after a heavy round (a salvo's last) before a machine gun opens up again.</summary>
        private const float GunAfterHeavy = 0.45f;

        /// <summary>A machine gun stops this long before a heavy weapon with a target is due.</summary>
        private const float GunBeforeHeavy = 0.3f;

        /// <summary>A heavy weapon waits this long after another heavy weapon's last round, and after a machine-gun round.</summary>
        private const float HeavyAfterHeavy = 0.4f;
        private const float HeavyAfterGun = 0.25f;

        /// <summary>Another machine gun that fired this recently is in the middle of its run.</summary>
        private const float GunHandover = 0.4f;

        /// <summary>
        /// The weapons of one vehicle take clear turns, never firing together: a machine gun opens
        /// up after a random delay, fires runs of 6 to 10 rounds and pauses; it stays quiet round
        /// every main-gun, missile or rocket shot (and a whole salvo), and two machine guns take
        /// turns too (the coaxial gun, then the roof gun). A heavy weapon with its target lined
        /// up has the right of way: the machine gun breaks off its run. A helicopter looses its
        /// missile, then its rockets, then rakes with its gun. Bosses, with guns all over them,
        /// only keep their mounts out of the same instant. Test feedback 2: machine guns and AA
        /// guns fire from magazines now (a 2.5-4 s stream, then the change), taking the same turns.
        /// </summary>
        private bool InRhythm(Vehicle v, int index)
        {
            var weapon = v.Arms[index];
            var now = _world.Time;
            var state = v.Weapons[index];
            var gun = IsGun(weapon);
            if (gun && !state.Started)
            {
                state.Started = true;
                state.Cooldown = 0.2f + 0.8f * (float)_world.Random.NextDouble();
                return false;
            }
            if (v.Def.Boss) return BossTurn(v, index, now);
            // Test feedback 19P: a gunship's broadside guns each have their own crew, and the 105, the 40 and the
            // 25 mm fire together as a real AC-130's do, none waiting on another's salvo or magazine.
            if (v.Def.Orbit && IsSide(v.Def.Mounts[index])) return true;
            // Play-test 5 (DECISIONS 20W): a short-range air defence's missiles fire on their own beside its gun's
            // five-second streams (as a Tunguska's or a Pantsir's do), not only in the second the magazine changes;
            // so do a fighter's on an enemy jet's tail beside its cannon.
            if (AirMissileBesideFlak(v, index)) return !SalvoUnderWay(v, index);
            if (SalvoUnderWay(v, index) || StreamUnderWay(v, index)) return false;
            // A leading magazine gun in the middle of its magazine keeps going (test feedback 11C: an
            // armoured car's or an IFV's cannon fires on for seconds); the others wait for its magazine change.
            if (Leads(v, index) && Streaming(v, index)) return true;
            if (gun)
            {
                if (now - v.HeavyRoundAt < GunAfterHeavy) return false;
                if (now - v.HeavyWaitingAt < 0.15) return false;
                var leads = Leads(v, index);
                // The main gun's stream ready to open up but held off by a secondary gun's magazine:
                // that gun breaks off for it, as a machine gun does for a heavy weapon (test feedback 2).
                if (!leads && now - v.LeadWaitingAt < 0.15) return false;
                // A machine gun or a secondary magazine gun also makes way for the main gun's stream about
                // to open up (test feedback 2: the coaxial gun, now on a magazine, for the autocannon's).
                if (HeavyDue(v, index, !leads)) return false;
                // Before a leading magazine gun opens up, a heavy weapon lined up goes first (an IFV's
                // or a BMPT's missile, then its cannon).
                if (leads && HeavyReady(v, index)) return false;
                if (v.GunMount != index && now - v.GunRoundAt < GunHandover)
                {
                    if (leads) v.LeadWaitingAt = now;
                    return false;
                }
                // Secondary magazine guns take turns magazine by magazine: the one quiet the longest opens
                // up first (test feedback 2: a tank's coaxial gun would otherwise take every gap from its roof gun).
                if (!leads && weapon.Clip > 0 && !Streaming(v, index) && QuieterGunReady(v, index)) return false;
                if (IsMachineGun(weapon) && state.RunLeft <= 0) state.RunLeft = _world.Random.Next(RunShortest, RunLongest + 1);
                return true;
            }
            if (v.HeavyMount != index && now - v.HeavyRoundAt < HeavyAfterHeavy) return false;
            if (now - v.GunRoundAt < HeavyAfterGun)
            {
                // Ready and lined up: the machine gun ends its run for it.
                v.HeavyWaitingAt = now;
                return false;
            }
            return true;
        }

        /// <summary>
        /// A boss's mounts take turns one step at a time: never two mounts in the same instant (the
        /// rounds of one step are one mount's, a stream's two or a salvo's). A mount held off by
        /// another's round has the next step, the one waiting longest first (test feedback 2: a gun
        /// streaming every step would otherwise starve the mounts after it, so the mega gunship's,
        /// the hovercraft's and the bosses' flak and cannons could not stream).
        /// </summary>
        private static bool BossTurn(Vehicle v, int index, double now)
        {
            var state = v.Weapons[index];
            if (now - v.AnyRoundAt < 0.01)
            {
                if (v.AnyMount == index) return true;
                Hold(state, now);
                return false;
            }
            var since = Held(state, now) ? state.WaitingSince : now;
            for (var i = 0; i < v.Weapons.Length; i++)
            {
                var other = v.Weapons[i];
                if (i == index || !Held(other, now) || other.WaitingSince >= since) continue;
                Hold(state, now);
                return false;
            }
            state.HeldAt = double.NegativeInfinity;
            return true;
        }

        /// <summary>Held off this step or the one before (a mount no longer ready stops waiting).</summary>
        private static bool Held(WeaponState state, double now) => now - state.HeldAt < 0.08;

        private static void Hold(WeaponState state, double now)
        {
            if (!Held(state, now)) state.WaitingSince = now;
            state.HeldAt = now;
        }

        /// <summary>
        /// A magazine gun that has the right of way once it has opened up: a ground vehicle's or a
        /// helicopter's main weapon (an armoured car's or an IFV's cannon). An aeroplane's cannon and
        /// secondary magazine guns (a gunship's side guns) take turns like a machine gun: an
        /// aeroplane's pass is short, and its rockets and bombs must still get their turn in it.
        /// </summary>
        /// <summary>
        /// An anti-aircraft missile on a vehicle whose leading gun is an anti-aircraft magazine gun (a SHORAD's), or on a
        /// jet streaming its cannon on an enemy jet's tail: it fires beside the stream.
        /// </summary>
        private static bool AirMissileBesideFlak(Vehicle v, int index) =>
            v.Arms[index].Projectile == ProjectileKind.Missile && v.Arms[index].Targets == TargetLayers.Air &&
            (v.Def.FixedWing ? v.OnTail : index > 0 && Leads(v, 0) && IsAntiAir(v.Arms[0]));

        private static bool Leads(Vehicle v, int index) => v.Def.FixedWing
            // Play-test 5 (DECISIONS 20W): a jet on an enemy jet's tail streams its cannon on; the missiles fit round it.
            ? v.OnTail && index == Movement.MovementSystem.TailGun(v, flying: true)
            : index == 0 && v.Arms[index].Clip > 0;

        /// <summary>A heavy weapon (not a gun) could fire now or is about to: loaded, its target alive and lined up.</summary>
        private bool HeavyReady(Vehicle v, int except)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
            {
                if (i == except || IsGun(v.Arms[i]) || !v.MountWorks(i)) continue;
                var state = v.Weapons[i];
                if (state.Ammo == 0 || state.Cooldown > GunBeforeHeavy || v.Arms[i].Damage <= 0f) continue;
                // A mount that has no target yet would take the main weapon's (it chooses after the main gun, this step).
                var id = i == 0 || !state.Target.IsValid ? v.Target : state.Target;
                if (!id.IsValid || !_world.TryGetTarget(id, out var t) || !t.IsAlive) continue;
                if (state.Cooldown > 0f ? state.Target.IsValid || i == 0 : CanFire(v, i, t)) return true;
            }
            return false;
        }

        /// <summary>
        /// Another secondary magazine gun of the vehicle, at least as strong, could open up now and has
        /// been quiet longer than mount <paramref name="index"/> (test feedback 2: a tank's coaxial and
        /// roof guns share the gaps between main-gun rounds; the headquarters' two flak guns take turns
        /// and its small coaxial gun only fills in, as before).
        /// </summary>
        private bool QuieterGunReady(Vehicle v, int index)
        {
            var mine = v.Weapons[index].LastRoundAt;
            var strength = v.Arms[index].SustainedDps;
            for (var i = 0; i < v.Weapons.Length; i++)
            {
                if (i == index || v.Arms[i].Clip <= 0 || Leads(v, i) || !v.MountWorks(i) || v.Arms[i].SustainedDps < strength) continue;
                var other = v.Weapons[i];
                if (other.LastRoundAt >= mine || other.Ammo == 0 || other.Cooldown > 0f) continue;
                var id = i == 0 ? v.Target : other.Target;
                if (id.IsValid && _world.TryGetTarget(id, out var t) && t.IsAlive && CanFire(v, i, t)) return true;
            }
            return false;
        }

        /// <summary>Mount <paramref name="index"/> is a magazine gun firing: rounds left and its last round a cadence ago.</summary>
        private bool Streaming(Vehicle v, int index)
        {
            var state = v.Weapons[index];
            var weapon = v.Arms[index];
            return state.ClipLeft > 0 && _world.Time - state.LastRoundAt <= weapon.Cooldown * 1.1f + 0.06f;
        }

        /// <summary>Another mount is a leading magazine gun in the middle of its magazine.</summary>
        private bool StreamUnderWay(Vehicle v, int index)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
                if (i != index && Leads(v, i) && Streaming(v, i)) return true;
            return false;
        }

        /// <summary>Another mount of the vehicle is in the middle of a salvo.</summary>
        private static bool SalvoUnderWay(Vehicle v, int index)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
                if (i != index && v.Weapons[i].BurstLeft > 0) return true;
            return false;
        }

        /// <summary>
        /// A heavy weapon with a target is about to fire: its reload is nearly done. With
        /// <paramref name="streams"/>, the leading magazine gun (the main gun's stream) firing or about to
        /// counts too; other magazine guns take turns by the handover instead (test feedback 2: two
        /// secondary streams waiting on each other's change would break each other up).
        /// </summary>
        private static bool HeavyDue(Vehicle v, int except, bool streams)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
            {
                var state = v.Weapons[i];
                if (i == except || IsMachineGun(v.Arms[i]) || (v.Arms[i].Clip > 0 && !(streams && Leads(v, i))) || state.Ammo == 0) continue;
                var aimed = i == 0 ? v.Target.IsValid : state.Target.IsValid;
                if (aimed && state.Cooldown is > 0f and <= GunBeforeHeavy) return true;
            }
            return false;
        }

        private bool CanFire(Vehicle v, int index, IDamageable target)
        {
            var mount = v.Def.Mounts[index];
            if (v.Weapons[index].Cooldown > 0f) return false;
            // Prompt 13 D.2: no bombs where friends are too close to where they would fall.
            if (v.Arms[index].Projectile == ProjectileKind.Bomb && OwnNear(v.Team, target.Position, v.Arms[index].SplashRadius + 3f)) return false;
            // Artillery and rocket launchers must stop to fire their main weapon; their machine guns need not.
            if (index == 0 && !v.Def.FiresWhileMoving && v.IsMoving) return false;
            if (!InReach(v, target, v.Arms[index]) || !HasLineOfFire(v, target, v.Arms[index])) return false;
            var desired = SimMath.HeadingOf(target.Position - v.Position);
            if (IsSide(mount) && !InArc(v, index, target.Position)) return false;
            var tolerance = mount.Aim switch
            {
                MountAim.Turret => TurretTolerance,
                MountAim.Free or MountAim.Left or MountAim.Right => FreeTolerance,
                _ => HullTolerance,
            };
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
            // Prompt 17 D.6: a dual-purpose gun loads its high explosive for a structure or light armour.
            var weapon = RoundFor(shooter.Arms[index], target, aimTarget);
            shooter.LastFiredAt = _world.Time;
            shooter.AnyRoundAt = _world.Time;
            shooter.AnyMount = index;
            if (IsGun(weapon))
            {
                shooter.GunRoundAt = _world.Time;
                shooter.GunMount = index;
            }
            else
            {
                shooter.HeavyRoundAt = _world.Time;
                shooter.HeavyMount = index;
            }
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
            var part = aimTarget is Vehicle { HasParts: true } boss && target == boss.Id ? _world.Bosses.ChoosePart(shooter, boss, weapon) : -1;
            if (part >= 0 && aimTarget is Vehicle partOf) aimAt = partOf.PartPosition(part);
            var distance = Vector2.Distance(shooter.Position, aimAt);
            // Rounds scatter more the farther they fly: tight up close, and at the edge of range
            // wide enough that a long shot can miss outright.
            var reach = Math.Clamp(distance / weapon.Range, 0f, 1.2f);
            var spread = weapon.Guided ? 0f : weapon.Spread * (0.35f + 1.25f * MathF.Pow(reach, 1.4f));
            // A boss's broken fire-control radar: its guns scatter wider.
            if (index < shooter.MountSpread.Length) spread *= shooter.MountSpread[index];
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
            if (weapon.Projectile == ProjectileKind.Bomb && shooter.Flying)
                travel = MathF.Max(0.8f, Vector2.Distance(origin, aim) / MathF.Max(8f, shooter.Speed));

            damageScale *= shooter.DamageBoost * shooter.CommandDamage * shooter.Def.DamageScale;
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
            if (weapon.Guided && (_world.Abilities.Jammed(shooter.Position, shooter.Team) || _world.Abilities.Jammed(aimAt, shooter.Team)))
                projectile.Jammed = true;
            if (weapon.Guided)
            {
                var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                projectile.Miss = new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (5f + (float)_world.Random.NextDouble() * 6f);
            }
            _projectiles.Add(projectile);
            var wide = projectile.Jammed || projectile.Failed ? projectile.Miss : default;
            _world.Emit(SimEvent.Fired(shooter, index, origin, aim, travel, target, wide, projectile.Jammed));
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
