#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
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
    internal sealed class CombatSystem
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

        public void Step(float dt)
        {
            _missileTargets.Clear();
            foreach (var p in _projectiles)
                if (p.Weapon.Guided && p.Target.IsValid) _missileTargets.Add(p.Target);
            _focus.Clear();
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Target.IsValid) _focus.Add((v.Team, v.Target));

            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                var mounts = v.Def.Mounts;
                // Cooldowns run regardless of movement or retargeting, so micro cannot create free shots.
                for (var i = 0; i < mounts.Count; i++) v.Weapons[i].Cooldown = MathF.Max(0f, v.Weapons[i].Cooldown - dt * v.FireFactor);
                // Knocked out by an EMP: the crew can do nothing until it wears off.
                if (v.Stunned)
                {
                    v.Target = EntityId.None;
                    continue;
                }

                var target = SelectTarget(v);
                v.Target = target?.Id ?? EntityId.None;
                v.AimDistance = target != null ? Vector2.Distance(v.Position, target.Position) : 0f;
                v.AimHeight = target is Vehicle aimed && aimed.Flying ? aimed.Def.Altitude : 0f;
                if (mounts[0].Aim == MountAim.Turret)
                {
                    var desired = target != null ? SimMath.HeadingOf(target.Position - v.Position) : v.Heading;
                    v.TurretHeading = SimMath.RotateTowards(v.TurretHeading, desired, v.Def.TurretTurnRate * dt);
                }
                else
                {
                    v.TurretHeading = v.Heading;
                }
                Operate(v, 0, target, dt);

                for (var i = 1; i < mounts.Count; i++)
                {
                    var secondary = SelectSecondaryTarget(v, i, target);
                    var state = v.Weapons[i];
                    state.Target = secondary?.Id ?? EntityId.None;
                    if (mounts[i].Aim == MountAim.Free)
                    {
                        var aim = secondary != null ? SimMath.HeadingOf(secondary.Position - v.Position) : v.TurretHeading;
                        state.Heading = SimMath.RotateTowards(state.Heading, aim, FreeMountTurnRate * dt);
                    }
                    Operate(v, i, secondary, dt);
                }
            }
            UpdateProjectiles(dt);
        }

        private IDamageable? SelectTarget(Vehicle v)
        {
            var weapon = v.Def.Weapon;
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
                    if (_world.TryGetVehicle(v.Target, out var current) && IsValidAutoTarget(v, current, weapon)) return current;
                    return BestInRange(v, weapon, EntityId.None);

                case OrderKind.Move:
                case OrderKind.Retreat:
                    // Targets of opportunity only: firing never changes the route (V2 R04).
                    return v.Def.FiresWhileMoving ? BestInRange(v, weapon, EntityId.None) : null;

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
            var weapon = mount.Weapon;
            if (mount.Aim != MountAim.Free) return primary != null && InReach(v, primary, weapon) && HasLineOfFire(v, primary, weapon) ? primary : null;
            if (_world.TryGetVehicle(v.Weapons[index].Target, out var current) && IsValidAutoTarget(v, current, weapon))
                return current;
            var best = BestInRange(v, weapon, primary?.Id ?? EntityId.None);
            if (best != null) return best;
            // An ordered attack on a building or barrel: the roof gun joins in.
            return primary != null && primary is not Vehicle && InReach(v, primary, weapon) && HasLineOfFire(v, primary, weapon) ? primary : null;
        }

        /// <summary>
        /// The most valuable enemy in range: one this weapon hurts most, one that is badly damaged
        /// or can be finished with this shot, and one teammates (or this vehicle's main gun) are
        /// already firing on. Distance only tips the balance between otherwise equal targets.
        /// </summary>
        private Vehicle? BestInRange(Vehicle v, WeaponDef weapon, EntityId favoured)
        {
            Vehicle? best = null;
            var bestScore = 0f;
            foreach (var other in _world.VehicleList)
            {
                if (!IsValidAutoTarget(v, other, weapon)) continue;
                var effect = _world.Catalog.Damage.Multiplier(weapon.DamageType, other.Armor);
                if (effect <= 0f) continue;
                var score = (0.4f + effect) * (1.6f - other.Hp / other.MaxHp);
                // Guns and cannons turn on aircraft only when nothing on the ground is in reach;
                // anti-aircraft weapons go for aircraft first.
                if (other.Flying != IsAntiAir(weapon)) score *= 0.02f;
                if (other.Hp <= weapon.Damage * effect) score *= 1.5f;
                if (_focus.Contains((v.Team, other.Id)) || other.Id == favoured) score *= 1.3f;
                // Worth more the more it costs (a titan before a jeep); one aiming at us first;
                // an unarmed truck last.
                score *= MathF.Sqrt(Math.Clamp(Worth(other), 2f, 25f) / 10f);
                if (other.Target == v.Id) score *= 1.2f;
                if (other.Def.Weapon.Damage <= 0f) score *= 0.3f;
                // Slow, heavy weapons do not waste a shot on a target already as good as dead
                // from the rounds on their way to it (overkill).
                if (weapon.Cooldown >= 2f && _incoming.TryGetValue(other.Id, out var incoming) && incoming >= other.Hp * 1.1f) score *= 0.05f;
                score /= 1f + 0.5f * Vector2.Distance(v.Position, other.Position) / MathF.Max(1f, weapon.Range);
                if (score <= bestScore) continue;
                best = other;
                bestScore = score;
            }
            return best;
        }

        /// <summary>What a target is worth: its CP, or for units never bought (bosses, defences) a guess from their health.</summary>
        private static float Worth(Vehicle v) => v.Def.CpCost > 0 ? v.Def.CpCost : v.Def.Boss ? 25f : v.MaxHp / 250f;

        /// <summary>Damage on its way to each target (rounds in flight), for overkill checks.</summary>
        private readonly Dictionary<EntityId, float> _incoming = new();

        /// <summary>A weapon made for aircraft: flak, or one that can only hit what flies.</summary>
        internal static bool IsAntiAir(WeaponDef weapon) => weapon.DamageType == DamageType.Flak || weapon.Targets == TargetLayers.Air;

        /// <summary>An aeroplane's guns stay on the target of its strafing run while it is in reach.</summary>
        private bool RunTargetInReach(Vehicle v, WeaponDef weapon, out Vehicle target)
        {
            target = null!;
            return v.Def.FixedWing && _world.TryGetVehicle(v.RunTarget, out target) && IsValidAutoTarget(v, target, weapon);
        }

        private bool IsValidAutoTarget(Vehicle v, Vehicle target, WeaponDef weapon) =>
            target.IsAlive && !target.Invulnerable && target.Team != v.Team && target.IsVisibleTo(v.Team) && InReach(v, target, weapon) &&
            HasLineOfFire(v, target, weapon);

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

        private static bool InReach(Vehicle v, IDamageable target, WeaponDef weapon)
        {
            if (!weapon.CanTarget(IsFlying(target))) return false;
            var distance = Vector2.Distance(v.Position, target.Position);
            return distance >= weapon.MinRange && distance - target.Radius <= weapon.Range;
        }

        private static bool IsFlying(IDamageable target) => target is Vehicle vehicle && vehicle.Flying;

        /// <summary>Fires the mount when it can, and keeps an ongoing salvo going.</summary>
        private void Operate(Vehicle v, int index, IDamageable? target, float dt)
        {
            var state = v.Weapons[index];
            var weapon = v.Def.Mounts[index].Weapon;
            if (state.BurstLeft > 0)
            {
                // A salvo keeps going at the point first aimed at even if the target dies or the turret turns.
                state.BurstTimer -= dt;
                while (state.BurstLeft > 0 && state.BurstTimer <= 0f)
                {
                    var alive = _world.TryGetTarget(state.BurstTarget, out var t) && t.IsAlive;
                    Launch(v, index, alive ? t.Position : state.BurstAim, state.BurstTarget, state.BurstFlying);
                    state.BurstLeft--;
                    state.BurstTimer += weapon.BurstInterval;
                }
                if (state.BurstLeft == 0) state.Cooldown = weapon.Cooldown;
                return;
            }

            if (target == null || !CanFire(v, index, target) || !InRhythm(v, index)) return;
            // Limited ammunition: one round per trigger pull (a whole salvo counts as one).
            if (state.Ammo == 0) return;
            if (state.Ammo > 0) state.Ammo--;
            var scale = IsMachineGun(weapon) ? RunDamage : 1f;
            Launch(v, index, target.Position, target.Id, IsFlying(target), scale);
            if (!IsMachineGun(weapon)) v.HeavyShotAt = _world.Time;
            if (IsMachineGun(weapon))
            {
                // A run of fire, then a pause while the gunner re-lays (its damage rides on the rounds).
                state.Cooldown = weapon.Cooldown * Jitter();
                if (--state.RunLeft <= 0) state.Cooldown = RestSeconds * (0.7f + 0.6f * (float)_world.Random.NextDouble());
                return;
            }
            if (weapon.Burst > 1)
            {
                state.BurstLeft = weapon.Burst - 1;
                state.BurstTimer = weapon.BurstInterval;
                state.BurstTarget = target.Id;
                state.BurstAim = target.Position;
                state.BurstFlying = IsFlying(target);
            }
            else
            {
                state.Cooldown = weapon.Cooldown * Jitter();
            }
        }

        /// <summary>A machine gun: bullets fired faster than three a second, one at a time.</summary>
        private static bool IsMachineGun(WeaponDef weapon) =>
            weapon.Projectile == ProjectileKind.Bullet && weapon.Cooldown < 0.35f && weapon.Burst <= 1;

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

        /// <summary>
        /// The weapons of one vehicle take turns. A machine gun opens up after a random delay,
        /// fires runs of 6 to 10 rounds and pauses; it holds off for a moment round each main-gun,
        /// missile or rocket shot. Two heavy weapons never fire in the same instant: a helicopter
        /// looses its missile, then its rockets, then rakes with its gun.
        /// </summary>
        private bool InRhythm(Vehicle v, int index)
        {
            var weapon = v.Def.Mounts[index].Weapon;
            var sinceHeavy = _world.Time - v.HeavyShotAt;
            var state = v.Weapons[index];
            if (IsMachineGun(weapon))
            {
                if (!state.Started)
                {
                    state.Started = true;
                    state.Cooldown = 0.2f + 0.8f * (float)_world.Random.NextDouble();
                    return false;
                }
                if (sinceHeavy < 0.35) return false;
                // The main gun is about to fire: let it.
                if (index > 0 && !IsMachineGun(v.Def.Weapon) && v.Target.IsValid && v.Weapons[0].Cooldown is > 0f and < 0.25f) return false;
                if (state.RunLeft <= 0) state.RunLeft = _world.Random.Next(RunShortest, RunLongest + 1);
                return true;
            }
            return sinceHeavy >= 0.3;
        }

        private bool CanFire(Vehicle v, int index, IDamageable target)
        {
            var mount = v.Def.Mounts[index];
            if (v.Weapons[index].Cooldown > 0f) return false;
            // Artillery and rocket launchers must stop to fire their main weapon; their machine guns need not.
            if (index == 0 && !v.Def.FiresWhileMoving && v.IsMoving) return false;
            if (!InReach(v, target, mount.Weapon) || !HasLineOfFire(v, target, mount.Weapon)) return false;
            var desired = SimMath.HeadingOf(target.Position - v.Position);
            var tolerance = mount.Aim switch
            {
                MountAim.Turret => TurretTolerance,
                MountAim.Free => FreeTolerance,
                _ => HullTolerance,
            };
            return MathF.Abs(SimMath.WrapAngle(desired - v.MountHeading(index))) <= tolerance;
        }

        private void Launch(Vehicle shooter, int index, Vector2 aimAt, EntityId target, bool targetFlying, float damageScale = 1f)
        {
            var weapon = shooter.Def.Mounts[index].Weapon;
            var distance = Vector2.Distance(shooter.Position, aimAt);
            // Rounds scatter more the farther they fly: tight up close, and at the edge of range
            // wide enough that a long shot can miss outright.
            var reach = Math.Clamp(distance / weapon.Range, 0f, 1.2f);
            var spread = weapon.Guided ? 0f : weapon.Spread * (0.35f + 1.25f * MathF.Pow(reach, 1.4f));
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

            var projectile = new Projectile(shooter.Id, shooter.Team, weapon, aim, target, travel, targetFlying) { DamageScale = damageScale, Origin = origin };
            if (target.IsValid && _world.TryGetVehicle(target, out var aimedAt))
            {
                projectile.Incoming = weapon.Damage * damageScale * _world.Catalog.Damage.Multiplier(weapon.DamageType, aimedAt.Armor);
                _incoming[target] = (_incoming.TryGetValue(target, out var already) ? already : 0f) + projectile.Incoming;
            }
            // Guided rounds are reliable up close; at the edge of their range one in ten loses lock.
            if (weapon.Guided && _world.Random.NextDouble() < 0.02 + 0.08 * reach * reach) projectile.Failed = true;
            if (weapon.Guided && (_world.Abilities.Jammed(shooter.Position, shooter.Team) || _world.Abilities.Jammed(aimAt, shooter.Team)))
                projectile.Jammed = true;
            if (weapon.Guided)
            {
                var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                projectile.Miss = new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (5f + (float)_world.Random.NextDouble() * 6f);
            }
            _projectiles.Add(projectile);
            _world.Emit(SimEvent.Fired(shooter, index, origin, aim, travel, target));
        }

        private void UpdateProjectiles(float dt)
        {
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
