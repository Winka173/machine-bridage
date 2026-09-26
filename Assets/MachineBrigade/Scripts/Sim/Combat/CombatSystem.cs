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

        public void Step(float dt)
        {
            _focus.Clear();
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Target.IsValid) _focus.Add((v.Team, v.Target));

            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                var mounts = v.Def.Mounts;
                // Cooldowns run regardless of movement or retargeting, so micro cannot create free shots.
                for (var i = 0; i < mounts.Count; i++) v.Weapons[i].Cooldown = MathF.Max(0f, v.Weapons[i].Cooldown - dt);

                var target = SelectTarget(v);
                v.Target = target?.Id ?? EntityId.None;
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
                    return _world.TryGetTarget(v.Order.Target, out var ordered) && ordered.IsAlive ? ordered : null;

                case OrderKind.AttackMove:
                    if (_world.TryGetVehicle(v.Engaged, out var engaged) && IsValidAutoTarget(v, engaged, weapon)) return engaged;
                    return BestInRange(v, weapon, EntityId.None);

                case OrderKind.Idle:
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
            if (mount.Aim != MountAim.Free) return primary != null && InReach(v, primary, weapon) ? primary : null;
            if (_world.TryGetVehicle(v.Weapons[index].Target, out var current) && IsValidAutoTarget(v, current, weapon))
                return current;
            var best = BestInRange(v, weapon, primary?.Id ?? EntityId.None);
            if (best != null) return best;
            // An ordered attack on a building or barrel: the roof gun joins in.
            return primary != null && primary is not Vehicle && InReach(v, primary, weapon) ? primary : null;
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
                if (other.Hp <= weapon.Damage * effect) score *= 1.5f;
                if (_focus.Contains((v.Team, other.Id)) || other.Id == favoured) score *= 1.3f;
                score /= 1f + 0.5f * Vector2.Distance(v.Position, other.Position) / MathF.Max(1f, weapon.Range);
                if (score <= bestScore) continue;
                best = other;
                bestScore = score;
            }
            return best;
        }

        private static bool IsValidAutoTarget(Vehicle v, Vehicle target, WeaponDef weapon) =>
            target.IsAlive && target.Team != v.Team && target.IsVisibleTo(v.Team) && InReach(v, target, weapon);

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
                // A salvo keeps going at its last aim point even if the target dies or the turret turns.
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

            if (target == null || !CanFire(v, index, target)) return;
            Launch(v, index, target.Position, target.Id, IsFlying(target));
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
                state.Cooldown = weapon.Cooldown;
            }
        }

        private static bool CanFire(Vehicle v, int index, IDamageable target)
        {
            var mount = v.Def.Mounts[index];
            if (v.Weapons[index].Cooldown > 0f) return false;
            // Artillery and rocket launchers must stop to fire their main weapon; their machine guns need not.
            if (index == 0 && !v.Def.FiresWhileMoving && v.IsMoving) return false;
            if (!InReach(v, target, mount.Weapon)) return false;
            var desired = SimMath.HeadingOf(target.Position - v.Position);
            var tolerance = mount.Aim switch
            {
                MountAim.Turret => TurretTolerance,
                MountAim.Free => FreeTolerance,
                _ => HullTolerance,
            };
            return MathF.Abs(SimMath.WrapAngle(desired - v.MountHeading(index))) <= tolerance;
        }

        private void Launch(Vehicle shooter, int index, Vector2 aimAt, EntityId target, bool targetFlying)
        {
            var weapon = shooter.Def.Mounts[index].Weapon;
            var distance = Vector2.Distance(shooter.Position, aimAt);
            var spread = weapon.Guided ? 0f : weapon.Spread * Math.Clamp(distance / weapon.Range, 0.25f, 1f);
            var aim = aimAt + RandomInCircle(spread);
            var origin = shooter.Position + SimMath.Forward(shooter.MountHeading(index)) * shooter.Radius;
            var travel = Vector2.Distance(origin, aim) / weapon.ProjectileSpeed;

            _projectiles.Add(new Projectile(shooter.Id, shooter.Team, weapon, aim, target, travel, targetFlying));
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
