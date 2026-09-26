#nullable enable
using System;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>A weapon's tuning. Loaded from the balance catalog; immutable during a match.</summary>
    public sealed class WeaponDef
    {
        public WeaponDef(string id, DamageType damageType, float damage, float cooldown, float range,
            float minRange, float projectileSpeed, float splashRadius, float spread, ExplosionTier impactTier)
        {
            Id = Guard.Id(id);
            DamageType = damageType;
            Damage = Guard.NonNegative(damage, id, nameof(damage));
            Cooldown = Guard.Positive(cooldown, id, nameof(cooldown));
            Range = Guard.Positive(range, id, nameof(range));
            MinRange = Guard.NonNegative(minRange, id, nameof(minRange));
            if (MinRange >= Range) throw new ArgumentException($"Weapon '{id}': minRange must be below range.");
            ProjectileSpeed = Guard.Positive(projectileSpeed, id, nameof(projectileSpeed));
            SplashRadius = Guard.NonNegative(splashRadius, id, nameof(splashRadius));
            Spread = Guard.NonNegative(spread, id, nameof(spread));
            ImpactTier = impactTier;
        }

        public string Id { get; }
        public DamageType DamageType { get; }
        public float Damage { get; }

        /// <summary>Seconds between shots. Keeps counting down while moving or retargeting.</summary>
        public float Cooldown { get; }

        public float Range { get; }
        public float MinRange { get; }

        /// <summary>Metres per second; a shot lands after distance / speed.</summary>
        public float ProjectileSpeed { get; }

        public float SplashRadius { get; }

        /// <summary>Radius of random aim error at maximum range, in metres.</summary>
        public float Spread { get; }

        public ExplosionTier ImpactTier { get; }
    }

    /// <summary>A delayed high-explosive blast (vehicle cook-off, fuel barrel). Hurts every side.</summary>
    public sealed class ExplosionDef
    {
        public ExplosionDef(float damage, float radius, float delay, ExplosionTier tier)
        {
            Damage = Guard.NonNegative(damage, "explosion", nameof(damage));
            Radius = Guard.Positive(radius, "explosion", nameof(radius));
            Delay = Guard.NonNegative(delay, "explosion", nameof(delay));
            Tier = tier;
        }

        public float Damage { get; }
        public float Radius { get; }
        public float Delay { get; }
        public ExplosionTier Tier { get; }
    }

    public sealed class VehicleDef
    {
        public VehicleDef(string id, ArmorClass armor, float maxHp, float speed, float turnRateDegrees,
            float turretTurnRateDegrees, float radius, int cpCost, float visionRange, bool firesWhileMoving,
            WeaponDef weapon, ExplosionDef? deathExplosion)
        {
            Id = Guard.Id(id);
            Armor = armor;
            MaxHp = Guard.Positive(maxHp, id, "hp");
            Speed = Guard.Positive(speed, id, nameof(speed));
            TurnRate = SimMath.DegToRad(Guard.Positive(turnRateDegrees, id, "turnRate"));
            TurretTurnRate = SimMath.DegToRad(Guard.Positive(turretTurnRateDegrees, id, "turretTurnRate"));
            Radius = Guard.Positive(radius, id, nameof(radius));
            CpCost = cpCost >= 0 ? cpCost : throw new ArgumentException($"Vehicle '{id}': cp must not be negative.");
            VisionRange = Guard.Positive(visionRange, id, "vision");
            FiresWhileMoving = firesWhileMoving;
            Weapon = weapon ?? throw new ArgumentNullException(nameof(weapon));
            DeathExplosion = deathExplosion;
        }

        public string Id { get; }
        public ArmorClass Armor { get; }
        public float MaxHp { get; }
        public float Speed { get; }

        /// <summary>Hull turn rate in radians per second.</summary>
        public float TurnRate { get; }

        /// <summary>Turret turn rate in radians per second.</summary>
        public float TurretTurnRate { get; }

        public float Radius { get; }
        public int CpCost { get; }
        public float VisionRange { get; }

        /// <summary>Turreted vehicles fire on the move; artillery must stop first.</summary>
        public bool FiresWhileMoving { get; }

        public WeaponDef Weapon { get; }
        public ExplosionDef? DeathExplosion { get; }
    }

    public sealed class PropDef
    {
        public PropDef(string id, ArmorClass armor, float maxHp, float width, float depth, bool blocksMovement,
            ExplosionDef? explosion)
        {
            Id = Guard.Id(id);
            Armor = armor;
            MaxHp = Guard.Positive(maxHp, id, "hp");
            Width = Guard.Positive(width, id, nameof(width));
            Depth = Guard.Positive(depth, id, nameof(depth));
            BlocksMovement = blocksMovement;
            Explosion = explosion;
        }

        public string Id { get; }
        public ArmorClass Armor { get; }
        public float MaxHp { get; }

        /// <summary>Footprint along X before rotation, in metres.</summary>
        public float Width { get; }

        /// <summary>Footprint along Y (engine Z) before rotation, in metres.</summary>
        public float Depth { get; }

        public bool BlocksMovement { get; }

        /// <summary>Set for explosive props (barrels, fuel tanks) that detonate when destroyed.</summary>
        public ExplosionDef? Explosion { get; }
    }

    internal static class Guard
    {
        public static string Id(string id) =>
            string.IsNullOrWhiteSpace(id) ? throw new ArgumentException("Definition id must not be empty.") : id;

        public static float Positive(float value, string owner, string field) =>
            float.IsFinite(value) && value > 0f ? value : throw new ArgumentException($"'{owner}': {field} must be positive (got {value}).");

        public static float NonNegative(float value, string owner, string field) =>
            float.IsFinite(value) && value >= 0f ? value : throw new ArgumentException($"'{owner}': {field} must not be negative (got {value}).");
    }
}
