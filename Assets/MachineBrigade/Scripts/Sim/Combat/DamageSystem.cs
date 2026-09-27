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
    /// The only place hit points change. Resolves impacts, splash and delayed explosions,
    /// and announces each destruction exactly once, which is what makes chain reactions
    /// terminate: an entity can only start one explosion.
    /// </summary>
    internal sealed class DamageSystem
    {
        /// <summary>Damage at the edge of a blast, relative to the centre.</summary>
        private const float EdgeFalloff = 0.25f;

        private readonly SimWorld _world;
        private readonly List<PendingExplosion> _pending = new();

        public DamageSystem(SimWorld world) => _world = world;

        public int PendingCount => _pending.Count;

        public void ResolveImpact(Projectile p)
        {
            var weapon = p.Weapon;
            var hit = EntityId.None;
            var at = p.AimPoint;
            if (_world.TryGetTarget(p.Target, out var target) && target.IsAlive)
            {
                // Guided missiles follow their target (unless flares decoy them or a jammer scrambles
                // them); everything else lands where it was aimed.
                var decoyed = weapon.Guided && (target is Vehicle { FlaresUp: true } || p.Jammed);
                if (weapon.Guided && !decoyed) at = target.Position;
                if (decoyed) at = target.Position + p.Miss;
                if (!decoyed && Vector2.Distance(target.Position, at) <= target.Radius + 0.5f)
                {
                    // Blame first, so a killing blow is credited to this shooter.
                    if (target is Vehicle victim) Blame(victim, p.Owner, p.OwnerTeam);
                    Apply(target, weapon.Damage, weapon.DamageType);
                    hit = target.Id;
                }
            }

            if (weapon.SplashRadius > 0f)
                Splash(at, weapon.SplashRadius, weapon.Damage, weapon.DamageType, p.OwnerTeam, hit, p.Owner, p.TargetFlying);

            _world.Emit(SimEvent.Impact(weapon, at, hit, p.OwnerTeam, p.TargetFlying));
        }

        /// <summary>
        /// Area damage with linear falloff. Weapon splash spares the shooter's team; blasts
        /// from <see cref="Teams.Environment"/> (cook-offs, fuel) hurt everyone.
        /// </summary>
        public void Splash(Vector2 at, float radius, float damage, DamageType type, int sourceTeam, EntityId exclude,
            EntityId attacker = default, bool airborne = false)
        {
            foreach (var v in _world.VehicleList)
            {
                // A blast on the ground cannot reach aircraft, and an airburst does not reach the ground.
                if (!v.IsAlive || v.Id == exclude || v.Flying != airborne) continue;
                if (sourceTeam != Teams.Environment && v.Team == sourceTeam) continue;
                if (Reaches(v, at, radius)) Blame(v, attacker, sourceTeam);
                ApplyFalloff(v, at, radius, damage, type);
            }
            if (airborne) return;
            foreach (var prop in _world.PropList)
            {
                if (!prop.IsAlive || prop.Id == exclude) continue;
                ApplyFalloff(prop, at, radius, damage, type);
            }
        }

        /// <summary>
        /// Remembers who hit a vehicle: the shooter lets idle vehicles turn on their attacker, the
        /// team decides who is paid for the kill. Blasts from the environment credit nobody.
        /// </summary>
        private void Blame(Vehicle victim, EntityId attacker, int team)
        {
            victim.LastAttackerTeam = team >= 0 ? team : -1;
            victim.LastHitTime = _world.Time;
            if (attacker.IsValid) victim.LastAttacker = attacker;
        }

        public void Apply(IDamageable target, float amount, DamageType type)
        {
            if (!target.IsAlive || !(amount > 0f)) return;
            var damage = amount * _world.Catalog.Damage.Multiplier(type, target.Armor);
            if (!(damage > 0f)) return;

            switch (target)
            {
                case Vehicle vehicle:
                    if (vehicle.ShieldUp) damage *= 1f - vehicle.ShieldAmount;
                    vehicle.Hp = MathF.Max(0f, vehicle.Hp - damage);
                    _world.Emit(SimEvent.Damage(vehicle, damage));
                    if (!vehicle.IsAlive) OnVehicleDestroyed(vehicle);
                    break;
                case Prop prop:
                    prop.Hp = MathF.Max(0f, prop.Hp - damage);
                    _world.Emit(SimEvent.Damage(prop, damage));
                    if (!prop.IsAlive) OnPropDestroyed(prop);
                    break;
            }
        }

        /// <summary>Detonates every explosion that has come due; new ones may be queued as a result.</summary>
        public void Step()
        {
            var i = 0;
            while (i < _pending.Count)
            {
                var pending = _pending[i];
                if (pending.Due > _world.Time)
                {
                    i++;
                    continue;
                }
                _pending.RemoveAt(i);
                _world.Emit(SimEvent.Exploded(pending.Position, pending.Explosion, pending.Source));
                Splash(pending.Position, pending.Explosion.Radius, pending.Explosion.Damage, DamageType.HighExplosive,
                    Teams.Environment, EntityId.None);
            }
        }

        private static bool Reaches(IDamageable target, Vector2 at, float radius) =>
            Vector2.Distance(target.Position, at) - target.Radius <= radius;

        private void ApplyFalloff(IDamageable target, Vector2 at, float radius, float damage, DamageType type)
        {
            var edgeDistance = MathF.Max(0f, Vector2.Distance(target.Position, at) - target.Radius);
            if (edgeDistance > radius) return;
            var scale = 1f - (1f - EdgeFalloff) * SimMath.Clamp01(edgeDistance / radius);
            Apply(target, damage * scale, type);
        }

        private void OnVehicleDestroyed(Vehicle vehicle)
        {
            vehicle.ClearPath();
            vehicle.Speed = 0f;
            _world.Emit(SimEvent.VehicleLost(vehicle));
            _world.Economy.OnVehicleDestroyed(vehicle);
            if (vehicle.Def.DeathExplosion != null) Schedule(vehicle.Position, vehicle.Def.DeathExplosion, vehicle.Id);
        }

        private void OnPropDestroyed(Prop prop)
        {
            if (prop.Def.BlocksMovement)
                _world.Grid.RemoveBlocker(prop.Position, prop.Width, prop.Depth, SimWorld.ObstacleClearance);
            _world.Emit(SimEvent.PropLost(prop));
            if (prop.Def.Explosion != null) Schedule(prop.Position, prop.Def.Explosion, prop.Id);
        }

        private void Schedule(Vector2 position, ExplosionDef explosion, EntityId source) =>
            _pending.Add(new PendingExplosion(_world.Time + explosion.Delay, position, explosion, source));

        private readonly struct PendingExplosion
        {
            public PendingExplosion(double due, Vector2 position, ExplosionDef explosion, EntityId source)
            {
                Due = due;
                Position = position;
                Explosion = explosion;
                Source = source;
            }

            public double Due { get; }
            public Vector2 Position { get; }
            public ExplosionDef Explosion { get; }
            public EntityId Source { get; }
        }
    }
}
