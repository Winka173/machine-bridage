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

        /// <summary>
        /// Seconds to reload a whole magazine in place once it is empty (the crew restocking the
        /// launcher or the rack), standing still; 0 derives it from the magazine (see
        /// <see cref="Combat.CombatSystem.ReloadSeconds"/>).
        /// </summary>
        public float Reload { get; internal set; }

        /// <summary>
        /// Seconds to reload the whole magazine in place: <see cref="Reload"/>, else two fifths of
        /// the time it takes to fire it off, between 10 and 28 s.
        /// </summary>
        public float MagazineReload => Reload > 0f ? Reload : Math.Clamp(Ammo * Cooldown * 0.4f, 10f, 28f);

        /// <summary>How big the impact is drawn against its tier's size (a fortress gun's shell lands bigger than a tank's).</summary>
        public float ImpactScale { get; internal set; } = 1f;

        /// <summary>Cluster munition: bomblets scattered where the round lands (null: an ordinary round).</summary>
        public ClusterDef? Cluster { get; internal set; }

        /// <summary>Shots per trigger pull (rocket salvo, machine-gun burst); the cooldown starts after the last.</summary>
        public int Burst { get; }

        public float BurstInterval { get; }

        /// <summary>Layers this weapon can engage: ground vehicles, aircraft or both.</summary>
        public TargetLayers Targets { get; }

        public bool CanTarget(bool flying) => (Targets & (flying ? TargetLayers.Air : TargetLayers.Ground)) != 0;

        /// <summary>A railgun slug: it goes through everything on its line and hurts all of it.</summary>
        public bool Pierce { get; internal set; }

        /// <summary>A laser: drawn as a beam from the muzzle to the target (it hits at once).</summary>
        public bool Beam { get; internal set; }

        /// <summary>A blow, not a round (the bulldozer's blade): no muzzle flash and no tracer, the hit lands at once.</summary>
        public bool Melee { get; internal set; }

        /// <summary>Seconds a charged weapon (a railgun) powers up, target in sight, before each shot; 0 for none.</summary>
        public float Charge { get; internal set; }

        /// <summary>Extra damage against some targets (see <see cref="DamageBonus"/>).</summary>
        public IReadOnlyList<DamageBonus> Bonuses { get; internal set; } = System.Array.Empty<DamageBonus>();

        /// <summary>The model its rounds fly as (a missile, rocket, bomb, shell or drone), or null for the default of its kind.</summary>
        public string? ProjectileModel { get; internal set; }

        /// <summary>How big that model is drawn (one shell model for 105, 155 and 203 mm).</summary>
        public float ProjectileScale { get; internal set; } = 1f;
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

        /// <summary>
        /// A copy of this weapon for one vehicle's equipment (a longer barrel, a bigger magazine):
        /// the shared definition is never changed. Same id, so it looks and sounds the same.
        /// </summary>
        internal WeaponDef Tuned(float range, float cooldown, float projectileSpeed, float splashRadius, float spread, float burstInterval,
            TargetLayers targets, int ammo, float reload, ClusterDef? cluster, float damage = -1f, int burst = -1, ProjectileKind? projectile = null)
        {
            var copy = new WeaponDef(Id, DamageType, damage >= 0f ? damage : Damage, MathF.Max(0.01f, cooldown), MathF.Max(range, MinRange + 0.5f), MinRange,
                MathF.Max(0.1f, projectileSpeed), MathF.Max(0f, splashRadius), MathF.Max(0f, spread), ImpactTier, projectile ?? Projectile,
                burst >= 1 ? burst : Burst, MathF.Max(0f, burstInterval), targets)
            {
                Ammo = ammo,
                Reload = reload,
                ImpactScale = ImpactScale,
                Cluster = cluster,
                Pierce = Pierce,
                Beam = Beam,
                Melee = Melee,
            };
            return copy;
        }
    }

    /// <summary>A delayed high-explosive blast (vehicle cook-off, fuel barrel). Hurts every side.</summary>
    /// <summary>
    /// Cluster munition: where the round lands it scatters <see cref="Count"/> bomblets over
    /// <see cref="Radius"/> metres, each going off a moment later as its own small blast.
    /// </summary>
    public sealed class ClusterDef
    {
        public ClusterDef(int count, float radius, ExplosionDef bomblet)
        {
            Count = count >= 1 ? count : throw new ArgumentException("cluster: count must be at least 1.");
            Radius = Guard.Positive(radius, "cluster", nameof(radius));
            Bomblet = bomblet ?? throw new ArgumentNullException(nameof(bomblet));
        }

        public int Count { get; }
        public float Radius { get; }
        public ExplosionDef Bomblet { get; }
    }

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

        /// <summary>This mount's own round model, over the weapon's (one missile type, two carriers' variants).</summary>
        public string? ProjectileModel { get; internal set; }

        /// <summary>
        /// A firing arc of its own (radians, clockwise from the nose; data "arc": [centre, half] in
        /// degrees): it aims like a broadside gun, only within <see cref="ArcHalf"/> of <see cref="ArcCentre"/>
        /// (the Bastion's corner turrets, each covering its own quarter). 0: no arc of its own.
        /// </summary>
        public float ArcCentre { get; internal set; }

        public float ArcHalf { get; internal set; }
    }

    /// <summary>
    /// One mark on a multi-phase boss's health bar: when its health reaches <see cref="At"/> the
    /// boss transforms for <see cref="Transform"/> seconds (untouchable), then fights on with the
    /// phase's changes.
    /// </summary>
    public sealed class BossPhaseDef
    {
        /// <summary>The share of full health the phase begins at (0-1).</summary>
        public float At { get; set; }

        public float Transform { get; set; } = 3f;

        /// <summary>Health given back when the transformation ends (a share of full health).</summary>
        public float Heal { get; set; }

        /// <summary>Its damage, speed and damage taken from then on (multiplied in).</summary>
        public float Damage { get; set; } = 1f;

        public float Speed { get; set; } = 1f;

        public float Armor { get; set; } = 1f;

        /// <summary>Skills it uses at once when the phase begins (summons, a shield, a barrage...).</summary>
        public IReadOnlyList<SkillDef> Skills { get; set; } = Array.Empty<SkillDef>();

        /// <summary>A new model for the boss from this phase (its new form), or null.</summary>
        public string? Model { get; set; }

        /// <summary>Its general's radio line when the phase begins (a text key), or null.</summary>
        public string? Radio { get; set; }
    }

    public sealed partial class VehicleDef
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

        /// <summary>
        /// Circles its target instead of making strafing runs: a gunship's left-hand pylon turn,
        /// which keeps its side-firing guns on the target for as long as it likes.
        /// </summary>
        public bool Orbit { get; internal set; }

        /// <summary>Seen only close up (at <see cref="StealthSight"/> of a spotter's sight) unless it has just fired.</summary>
        public bool Stealth { get; internal set; }

        /// <summary>Share of a spotter's sight at which a stealthy aircraft shows.</summary>
        public const float StealthSight = 0.4f;

        /// <summary>A fighter on combat air patrol: goes after enemy aircraft well beyond its own post.</summary>
        public bool Interceptor { get; internal set; }

        /// <summary>Can stop in the air to shoot (a Harrier or F-35B): a few seconds at a time, then it must fly on.</summary>
        public bool Vtol { get; internal set; }

        /// <summary>
        /// A suicide vehicle (car bomb): "firing" its main weapon at a target in reach blows it up,
        /// a blast of the weapon's damage and splash that spares its own side.
        /// </summary>
        public bool Kamikaze { get; internal set; }

        /// <summary>Share of a kamikaze drone's damage that gets through (a turtle tank's shed stops most).</summary>
        public float DroneArmor { get; internal set; } = 1f;

        /// <summary>A mine roller: mines it sets off go off harmlessly in front of it.</summary>
        public bool MineProof { get; internal set; }

        /// <summary>Repairs friendly fixed defences (towers, turrets, bunkers) around it, slowly (sappers).</summary>
        public AuraDef? FortifyAura { get; internal set; }

        /// <summary>Points the main weapon another way than its default (a gunship's guns out of the left side).</summary>
        internal void AimMain(MountAim aim)
        {
            var mounts = (List<WeaponMount>)Mounts;
            mounts[0] = new WeaponMount(mounts[0].Weapon, mounts[0].Slot, aim);
        }

        /// <summary>Hull length along the heading, for collisions (the gun barrel is not counted).</summary>
        public float Length { get; internal set; }

        /// <summary>Hull width across the heading, for collisions.</summary>
        public float Width { get; internal set; }

        /// <summary>Collision capsule: half the length of its spine (0 for a round footprint).</summary>
        /// <summary>
        /// Size of the model relative to how it was built: aircraft are drawn closer to their
        /// real size next to tanks and houses, ground vehicles a little smaller. Length and width
        /// (the hull) include it; the radius, which decides how easily it is hit, does not.
        /// </summary>
        public float Scale { get; set; } = 1f;

        public float HullHalf => MathF.Max(0f, (Length - Width) * 0.5f);

        /// <summary>Collision capsule radius (a little inside the hull, so parked vehicles can touch).</summary>
        public float HullRadius => Width * 0.46f;

        /// <summary>Radius of a circle around the whole capsule.</summary>
        public float HullBound => HullHalf + HullRadius;

        /// <summary>Skills the vehicle uses on its own (elite units, boss phases).</summary>
        public IReadOnlyList<SkillDef> Skills { get; internal set; } = Array.Empty<SkillDef>();

        /// <summary>A boss's health phases, highest mark first (empty: one bar).</summary>
        public IReadOnlyList<BossPhaseDef> Phases { get; internal set; } = Array.Empty<BossPhaseDef>();

        /// <summary>The enemy general behind a boss (its radio lines and portrait), or null.</summary>
        public string? General { get; internal set; }

        /// <summary>Repairs friendly vehicles around it (engineers).</summary>
        public AuraDef? RepairAura { get; internal set; }

        /// <summary>Re-arms friendly vehicles around it (engineers).</summary>
        public AuraDef? RearmAura { get; internal set; }

        /// <summary>Radius in which enemy guided weapons and fire support are scrambled (0: no jammer).</summary>
        public float Jammer { get; internal set; }

        /// <summary>Lays mines as it goes (mine layers).</summary>
        public MineLayerDef? Mines { get; internal set; }

        /// <summary>Its place in a base loadout (towers, utility modules, the HQ); null for everything else.</summary>
        public FortDef? Fort { get; internal set; }

        /// <summary>Active protection: shoots down incoming missiles and rockets (see <see cref="ApsDef"/>).</summary>
        public ApsDef? Aps { get; internal set; }

        /// <summary>A command vehicle's fire-rate aura for friendly vehicles round it (null: none).</summary>
        public CommandAuraDef? CommandAura { get; internal set; }

        /// <summary>After standing still this many seconds it is a forward drop zone for its side (0: never).</summary>
        public float ForwardDrop { get; internal set; }

        /// <summary>How many of it a side may have in the field at once, deliveries included (0: no limit).</summary>
        public int MaxPerSide { get; internal set; }

        /// <summary>Counter-battery radar carried (null: none).</summary>
        public CounterBatteryDef? CounterBattery { get; internal set; }

        /// <summary>A helicopter that fights from the edge of its missiles' reach and keeps out of short-range anti-air.</summary>
        public bool Standoff { get; internal set; }

        /// <summary>An obstacle (dragon's teeth): it blocks the way and fights nothing; engineers breach it three times as fast.</summary>
        public bool Obstacle { get; internal set; }

        /// <summary>Never a target (a fixed minefield: its mines are what matter).</summary>
        public bool Untargetable { get; internal set; }

        /// <summary>A fixed structure vehicles drive through (a minefield, wire, a helipad): it blocks no route.</summary>
        public bool Passable { get; internal set; }

        /// <summary>Sees stealth and hidden units within its guns' reach (the guard tower).</summary>
        public bool RevealStealth { get; internal set; }

        /// <summary>Friendly towers within Radius reach Rate further (the guard tower; the best aura counts).</summary>
        public AuraDef? TowerRangeAura { get; internal set; }

        /// <summary>Enemy ground vehicles within Radius move Rate slower (wire).</summary>
        public AuraDef? SlowAura { get; internal set; }

        /// <summary>A tower that hides until an enemy comes close (the gun pit).</summary>
        public HiddenDef? Hidden { get; internal set; }

        /// <summary>A base's utility module.</summary>
        public UtilityDef? Utility { get; internal set; }

        /// <summary>A drone (light towers' anti-air guns hit it harder).</summary>
        public bool Drone { get; internal set; }

        /// <summary>No weapon that does damage (an obstacle, a minefield, a jammer, a utility module): it never fires.</summary>
        public bool Passive
        {
            get
            {
                foreach (var m in Mounts)
                    if (m.Weapon.Damage > 0f) return false;
                return true;
            }
        }

        /// <summary>The longest reach of its damaging weapons (0 for none).</summary>
        public float GunReach
        {
            get
            {
                var reach = 0f;
                foreach (var m in Mounts)
                    if (m.Weapon.Damage > 0f) reach = MathF.Max(reach, m.Weapon.Range);
                return reach;
            }
        }

        /// <summary>What the vehicle is for (counters, AI roles, card info).</summary>
        public UnitClass Class { get; internal set; }

        /// <summary>What this unit really beats when its class's line would mislead (an attack jet hunts the ground, a fighter aircraft); null: its class's.</summary>
        public IReadOnlyList<UnitClass>? StrongVs { get; internal set; }

        /// <summary>A veteran enemy variant: bigger, tougher, with skills; shown with an elite badge.</summary>
        public bool Elite { get; internal set; }

        /// <summary>For an elite: the vehicle it is a refurbished version of.</summary>
        public string? EliteOf { get; internal set; }

        /// <summary>For a tower's rank-7 branch: the tower it is a branch of (its card, rank and equipment are that tower's).</summary>
        public string? BranchOf { get; internal set; }

        /// <summary>The card this def counts as: the tower a branch belongs to, else itself.</summary>
        public string CardId => BranchOf ?? Id;

        /// <summary>What it counts against the army cap and pays out as a kill (an elite counts as its base unit).</summary>
        public int ArmyCost { get; internal set; }

        /// <summary>
        /// Rough fighting value at full health, in CP: what the unit costs, or for units that are
        /// never bought (defences, mission units) an estimate from their toughness. Bosses count
        /// as nothing here, because the army fights them whatever the odds.
        /// </summary>
        public float Power => Boss ? 0f : Elite ? MaxHp / 150f : CpCost > 0 ? CpCost : Fort is { } fort ? FortPower(fort) : Static ? MaxHp / 250f : MaxHp / 150f;

        /// <summary>
        /// A base structure's worth in CP for the AI's odds: an HQ 14, a large tower 11, a medium one
        /// 7, a light one 4; a module or anything with no gun 1 (its health alone once counted it as
        /// a whole army: an HQ was worth 90).
        /// </summary>
        private float FortPower(FortDef fort)
        {
            if (fort.Kind == FortKind.Hq) return 14f;
            if (fort.Kind == FortKind.Utility || Passive) return 1f;
            return fort.Size switch { SlotSize.Large => 11f, SlotSize.Medium => 7f, _ => 4f };
        }

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

        /// <summary>Size of the model relative to how it was built; the footprint already includes it.</summary>
        public float Scale { get; set; } = 1f;

        /// <summary>
        /// Stands tall enough to stop a direct-fire round (buildings, rock, fortress walls). Low
        /// cover and open structures (sandbags, tank traps, barriers, a water tower on legs) do not.
        /// </summary>
        public bool BlocksFire { get; }

        /// <summary>A hull knocks it down by driving into it (trees, bushes, hedges, fences).</summary>
        public bool Crushable { get; set; }

        /// <summary>
        /// Seconds a destroyed one takes to come down (a fortress wall toppling into rubble): its
        /// ground opens only then, so nothing drives through the falling wall. 0: at once.
        /// </summary>
        public float Collapse { get; set; }

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
