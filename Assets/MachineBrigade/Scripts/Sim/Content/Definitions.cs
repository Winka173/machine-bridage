#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>A weapon's tuning. Loaded from the balance catalog; immutable during a match.</summary>
    public sealed class WeaponDef
    {
        public WeaponDef(string id, DamageType damageType, float damage, float cooldown, float range,
            float minRange, float projectileSpeed, float splashRadius, float spread, ExplosionTier impactTier,
            ProjectileKind projectile = ProjectileKind.Shell, int burst = 1, float burstInterval = 0.1f,
            TargetLayers targets = TargetLayers.Ground)
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
            Projectile = projectile;
            Burst = burst >= 1 ? burst : throw new ArgumentException($"Weapon '{id}': burst must be at least 1.");
            BurstInterval = Guard.NonNegative(burstInterval, id, nameof(burstInterval));
            Targets = targets != TargetLayers.None ? targets : throw new ArgumentException($"Weapon '{id}': targets must not be empty.");
        }

        public string Id { get; }
        public DamageType DamageType { get; }

        /// <summary>What the weapon fires. Missiles home in on their target; the rest land on the aim point.</summary>
        public ProjectileKind Projectile { get; }

        public bool Guided => Projectile is ProjectileKind.Missile or ProjectileKind.Drone;

        /// <summary>
        /// Fires over cover: artillery, mortars and rocket artillery (anything with a minimum
        /// range) lob their rounds, bombs fall and drones fly. Everything else needs a clear line.
        /// </summary>
        public bool Indirect => MinRange > 0f || Projectile is ProjectileKind.Bomb or ProjectileKind.Drone;

        /// <summary>
        /// Shots (trigger pulls) carried, or 0 for unlimited. Long-range weapons run dry so they
        /// cannot be spammed; the vehicle then fights with its other mounts until it re-arms.
        /// </summary>
        public int Ammo { get; internal set; }

        /// <summary>Shots per trigger pull (rocket salvo, machine-gun burst); the cooldown starts after the last.</summary>
        public int Burst { get; }

        public float BurstInterval { get; }

        /// <summary>Layers this weapon can engage: ground vehicles, aircraft or both.</summary>
        public TargetLayers Targets { get; }

        public bool CanTarget(bool flying) => (Targets & (flying ? TargetLayers.Air : TargetLayers.Ground)) != 0;
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

    /// <summary>One weapon on a vehicle and how it is pointed. The first mount is the main weapon.</summary>
    public sealed class WeaponMount
    {
        public WeaponMount(WeaponDef weapon, string slot, MountAim aim)
        {
            Weapon = weapon ?? throw new ArgumentNullException(nameof(weapon));
            Slot = string.IsNullOrWhiteSpace(slot) ? "main" : slot;
            Aim = aim;
        }

        public WeaponDef Weapon { get; }

        /// <summary>Model muzzle name suffix (main, coax, mg, missile, rocket, gun).</summary>
        public string Slot { get; }

        public MountAim Aim { get; }
    }

    public sealed class VehicleDef
    {
        public VehicleDef(string id, ArmorClass armor, float maxHp, float speed, float turnRateDegrees,
            float turretTurnRateDegrees, float radius, int cpCost, float visionRange, bool firesWhileMoving,
            WeaponDef weapon, ExplosionDef? deathExplosion, IReadOnlyList<WeaponMount>? secondary = null,
            bool flying = false, float altitude = 0f, float captureRate = 1f, string mainSlot = "main", bool fixedWing = false,
            bool isStatic = false)
        {
            Id = Guard.Id(id);
            Armor = armor;
            MaxHp = Guard.Positive(maxHp, id, "hp");
            Static = isStatic && !flying;
            Speed = Static ? 0f : Guard.Positive(speed, id, nameof(speed));
            TurnRate = SimMath.DegToRad(Guard.Positive(turnRateDegrees, id, "turnRate"));
            TurretTurnRate = SimMath.DegToRad(Guard.Positive(turretTurnRateDegrees, id, "turretTurnRate"));
            Radius = Guard.Positive(radius, id, nameof(radius));
            CpCost = cpCost >= 0 ? cpCost : throw new ArgumentException($"Vehicle '{id}': cp must not be negative.");
            VisionRange = Guard.Positive(visionRange, id, "vision");
            FiresWhileMoving = firesWhileMoving;
            Weapon = weapon ?? throw new ArgumentNullException(nameof(weapon));
            DeathExplosion = deathExplosion;
            var mounts = new List<WeaponMount> { new WeaponMount(weapon, mainSlot, flying ? MountAim.Hull : MountAim.Turret) };
            if (secondary != null) mounts.AddRange(secondary);
            Mounts = mounts;
            Flying = flying;
            Altitude = flying ? Guard.Positive(altitude, id, nameof(altitude)) : 0f;
            CaptureRate = Guard.NonNegative(captureRate, id, nameof(captureRate));
            FixedWing = flying && fixedWing;
            Model = Id;
            ArmyCost = CpCost;
            Width = flying ? radius * 2f : radius * 1.6f;
            Length = flying ? radius * 2f : radius * 2.7f;
        }

        /// <summary>A fixed defence (gun turret, bunker, tower): it never moves, is never pushed and is never bought.</summary>
        public bool Static { get; }

        /// <summary>Hull length along the heading, for collisions (the gun barrel is not counted).</summary>
        public float Length { get; internal set; }

        /// <summary>Hull width across the heading, for collisions.</summary>
        public float Width { get; internal set; }

        /// <summary>Collision capsule: half the length of its spine (0 for a round footprint).</summary>
        public float HullHalf => MathF.Max(0f, (Length - Width) * 0.5f);

        /// <summary>Collision capsule radius (a little inside the hull, so parked vehicles can touch).</summary>
        public float HullRadius => Width * 0.46f;

        /// <summary>Radius of a circle around the whole capsule.</summary>
        public float HullBound => HullHalf + HullRadius;

        /// <summary>Skills the vehicle uses on its own (elite units, boss phases).</summary>
        public IReadOnlyList<SkillDef> Skills { get; internal set; } = Array.Empty<SkillDef>();

        /// <summary>Repairs friendly vehicles around it (engineers).</summary>
        public AuraDef? RepairAura { get; internal set; }

        /// <summary>Re-arms friendly vehicles around it (engineers).</summary>
        public AuraDef? RearmAura { get; internal set; }

        /// <summary>Radius in which enemy guided weapons and fire support are scrambled (0: no jammer).</summary>
        public float Jammer { get; internal set; }

        /// <summary>Lays mines as it goes (mine layers).</summary>
        public MineLayerDef? Mines { get; internal set; }

        /// <summary>What the vehicle is for (counters, AI roles, card info).</summary>
        public UnitClass Class { get; internal set; }

        /// <summary>A veteran enemy variant: bigger, tougher, with skills; shown with an elite badge.</summary>
        public bool Elite { get; internal set; }

        /// <summary>For an elite: the vehicle it is a refurbished version of.</summary>
        public string? EliteOf { get; internal set; }

        /// <summary>What it counts against the army cap and pays out as a kill (an elite counts as its base unit).</summary>
        public int ArmyCost { get; internal set; }

        /// <summary>
        /// Rough fighting value at full health, in CP: what the unit costs, or for units that are
        /// never bought (defences, mission units) an estimate from their toughness. Bosses count
        /// as nothing here, because the army fights them whatever the odds.
        /// </summary>
        public float Power => Boss ? 0f : Elite ? MaxHp / 150f : CpCost > 0 ? CpCost : Static ? MaxHp / 250f : MaxHp / 150f;

        /// <summary>Model to draw (defaults to the id; a convoy truck borrows the civilian truck).</summary>
        public string Model { get; internal set; }

        /// <summary>A campaign boss: counted on its own, shown with a health bar across the top.</summary>
        public bool Boss { get; internal set; }

        /// <summary>
        /// Aeroplanes (jets, drones) cannot hover: they fly on at speed, circle their post, and
        /// attack in strafing runs, pulling through and coming round again.
        /// </summary>
        public bool FixedWing { get; }

        /// <summary>Every weapon, main first.</summary>
        public IReadOnlyList<WeaponMount> Mounts { get; }

        /// <summary>Aircraft ignore terrain, buildings and wrecks, and only anti-air weapons reach them.</summary>
        public bool Flying { get; }

        /// <summary>Flight height in metres (presentation and line of sight).</summary>
        public float Altitude { get; }

        /// <summary>Capture speed multiplier on objectives (scouts and APCs are faster; aircraft cannot capture).</summary>
        public float CaptureRate { get; }

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
            ExplosionDef? explosion, bool? blocksFire = null)
        {
            BlocksFire = blocksFire ?? blocksMovement;
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

        /// <summary>
        /// Stands tall enough to stop a direct-fire round (buildings, rock, fortress walls). Low
        /// cover and open structures (sandbags, tank traps, barriers, a water tower on legs) do not.
        /// </summary>
        public bool BlocksFire { get; }

        /// <summary>Terrain (rock, earth) that no weapon can realistically destroy; never an attack target.</summary>
        public bool Indestructible => MaxHp >= 100000f;

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
