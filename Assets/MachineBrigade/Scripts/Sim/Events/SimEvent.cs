#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Events
{
    public enum SimEventKind
    {
        VehicleSpawned,
        VehicleDestroyed,
        PropDestroyed,
        WeaponFired,
        ProjectileImpact,
        Explosion,
        Damaged,
    }

    /// <summary>
    /// Something the presentation should show. Events describe what already happened in the
    /// simulation; effects and sounds consume them and never feed damage back.
    /// </summary>
    public readonly struct SimEvent
    {
        private SimEvent(SimEventKind kind, EntityId entity, Vector2 position, Vector2 target, float value,
            ExplosionTier tier, string? defId, int team)
        {
            Kind = kind;
            Entity = entity;
            Position = position;
            Target = target;
            Value = value;
            Tier = tier;
            DefId = defId;
            Team = team;
        }

        public SimEventKind Kind { get; }

        /// <summary>The vehicle or prop concerned (the shooter for WeaponFired, the source for Explosion).</summary>
        public EntityId Entity { get; }

        public Vector2 Position { get; }

        /// <summary>Aim point for WeaponFired.</summary>
        public Vector2 Target { get; }

        /// <summary>Travel time (WeaponFired), radius (impacts, explosions) or damage dealt (Damaged).</summary>
        public float Value { get; }

        public ExplosionTier Tier { get; }

        /// <summary>Vehicle, prop or weapon definition id, for choosing visuals.</summary>
        public string? DefId { get; }

        public int Team { get; }

        internal static SimEvent Spawned(Vehicle v) =>
            new(SimEventKind.VehicleSpawned, v.Id, v.Position, default, 0f, default, v.Def.Id, v.Team);

        internal static SimEvent Fired(Vehicle shooter, Vector2 origin, Vector2 aim, float travelTime) =>
            new(SimEventKind.WeaponFired, shooter.Id, origin, aim, travelTime, shooter.Def.Weapon.ImpactTier,
                shooter.Def.Weapon.Id, shooter.Team);

        internal static SimEvent Impact(WeaponDef weapon, Vector2 at, EntityId hit, int team) =>
            new(SimEventKind.ProjectileImpact, hit, at, default, weapon.SplashRadius, weapon.ImpactTier, weapon.Id, team);

        internal static SimEvent Exploded(Vector2 at, ExplosionDef explosion, EntityId source) =>
            new(SimEventKind.Explosion, source, at, default, explosion.Radius, explosion.Tier, null, Teams.Environment);

        internal static SimEvent Damage(IDamageable target, float amount) =>
            new(SimEventKind.Damaged, target.Id, target.Position, default, amount, default, null, target.Team);

        internal static SimEvent VehicleLost(Vehicle v) =>
            new(SimEventKind.VehicleDestroyed, v.Id, v.Position, default, 0f, ExplosionTier.Medium, v.Def.Id, v.Team);

        internal static SimEvent PropLost(Prop p) =>
            new(SimEventKind.PropDestroyed, p.Id, p.Position, default, p.Radius, ExplosionTier.Medium, p.Def.Id, Teams.Neutral);
    }
}
