#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Target selection, turret aiming, firing and projectile flight. Explicit orders decide
    /// what may be targeted; automatic targeting only fills in where orders allow it.
    /// </summary>
    internal sealed class CombatSystem
    {
        private static readonly float AimTolerance = SimMath.DegToRad(4f);

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
                // Cooldowns run regardless of movement or retargeting, so micro cannot create free shots.
                v.Cooldown = MathF.Max(0f, v.Cooldown - dt);

                var target = SelectTarget(v);
                v.Target = target?.Id ?? EntityId.None;
                var desired = target != null ? SimMath.HeadingOf(target.Position - v.Position) : v.Heading;
                v.TurretHeading = SimMath.RotateTowards(v.TurretHeading, desired, v.Def.TurretTurnRate * dt);

                if (target != null && CanFire(v, target, desired)) Fire(v, target);
            }
            UpdateProjectiles(dt);
        }

        private IDamageable? SelectTarget(Vehicle v)
        {
            switch (v.Order.Kind)
            {
                case OrderKind.Attack:
                    return _world.TryGetTarget(v.Order.Target, out var ordered) && ordered.IsAlive ? ordered : null;

                case OrderKind.AttackMove:
                    if (_world.TryGetVehicle(v.Engaged, out var engaged) && IsValidAutoTarget(v, engaged)) return engaged;
                    return BestInRange(v);

                case OrderKind.Idle:
                    if (_world.TryGetVehicle(v.Target, out var current) && IsValidAutoTarget(v, current)) return current;
                    return BestInRange(v);

                case OrderKind.Move:
                case OrderKind.Retreat:
                    // Targets of opportunity only: firing never changes the route (V2 R04).
                    return v.Def.FiresWhileMoving ? BestInRange(v) : null;

                default:
                    return null;
            }
        }

        /// <summary>
        /// The most valuable enemy in range: one this weapon hurts most, one that is badly damaged
        /// or can be finished with this shot, and one teammates are already firing on. Distance
        /// only tips the balance between otherwise equal targets.
        /// </summary>
        private Vehicle? BestInRange(Vehicle v)
        {
            var weapon = v.Def.Weapon;
            Vehicle? best = null;
            var bestScore = 0f;
            foreach (var other in _world.VehicleList)
            {
                if (!IsValidAutoTarget(v, other)) continue;
                var effect = _world.Catalog.Damage.Multiplier(weapon.DamageType, other.Armor);
                var score = (0.4f + effect) * (1.6f - other.Hp / other.MaxHp);
                if (other.Hp <= weapon.Damage * effect) score *= 1.5f;
                if (_focus.Contains((v.Team, other.Id))) score *= 1.3f;
                score /= 1f + 0.5f * Vector2.Distance(v.Position, other.Position) / MathF.Max(1f, weapon.Range);
                if (score <= bestScore) continue;
                best = other;
                bestScore = score;
            }
            return best;
        }

        private static bool IsValidAutoTarget(Vehicle v, Vehicle target)
        {
            if (!target.IsAlive || target.Team == v.Team || !target.IsVisibleTo(v.Team)) return false;
            var distance = Vector2.Distance(v.Position, target.Position);
            return distance >= v.Def.Weapon.MinRange && distance - target.Radius <= v.Def.Weapon.Range;
        }

        private static bool CanFire(Vehicle v, IDamageable target, float desiredTurret)
        {
            if (v.Cooldown > 0f) return false;
            if (!v.Def.FiresWhileMoving && v.IsMoving) return false;
            var weapon = v.Def.Weapon;
            var distance = Vector2.Distance(v.Position, target.Position);
            if (distance < weapon.MinRange || distance - target.Radius > weapon.Range) return false;
            return MathF.Abs(SimMath.WrapAngle(desiredTurret - v.TurretHeading)) <= AimTolerance;
        }

        private void Fire(Vehicle shooter, IDamageable target)
        {
            var weapon = shooter.Def.Weapon;
            var distance = Vector2.Distance(shooter.Position, target.Position);
            var spread = weapon.Spread * Math.Clamp(distance / weapon.Range, 0.25f, 1f);
            var aim = target.Position + RandomInCircle(spread);
            var origin = shooter.Position + SimMath.Forward(shooter.TurretHeading) * shooter.Radius;
            var travel = Vector2.Distance(origin, aim) / weapon.ProjectileSpeed;

            _projectiles.Add(new Projectile(shooter.Id, shooter.Team, weapon, aim, target.Id, travel));
            _world.Emit(SimEvent.Fired(shooter, origin, aim, travel));
            shooter.Cooldown = weapon.Cooldown;
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
