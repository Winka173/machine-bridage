#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>A weapon's tuning. Loaded from the balance catalog; immutable during a match.</summary>
    public sealed partial class WeaponDef
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
        public bool Indirect => MinRange > 0f || Lofted || Projectile is ProjectileKind.Bomb or ProjectileKind.Drone;

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
        /// Prompt 13 C: an aircraft's stores (bombs, missiles, rockets): rounds carried when fully
        /// loaded (0: not stores). A salvo fires what is left of it; the rounds come back one at a time
        /// over the field (<see cref="Abilities.SupplySystem"/>). A carrier's own "loads" may say otherwise
        /// (<see cref="VehicleDef.LoadOf"/>). Guns never run out.
        /// </summary>
        public int Load { get; internal set; }

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

        /// <summary>
        /// Sustained fire (test feedback 11C): a magazine of this many rounds, fired one at a time
        /// <see cref="Cooldown"/> apart at whatever the mount is laid on (it tracks its target, unlike a
        /// salvo, and stops when the target stops bearing), then <see cref="ClipReload"/> seconds to change
        /// magazines. A pause of that long tops a part-used magazine up. 0: no magazine (a single shot,
        /// a salvo, or a machine gun's runs of fire). Only for single-round weapons (burst 1).
        /// </summary>
        public int Clip { get; internal set; }

        /// <summary>Seconds to change an empty magazine (see <see cref="Clip"/>).</summary>
        public float ClipReload { get; internal set; }

        /// <summary>
        /// How heavy one round looks and sounds (its tracer, muzzle flash and report): its damage,
        /// unless the data gives "roundWeight" (a gun made to fire faster with lighter rounds still
        /// looks and sounds like its calibre).
        /// </summary>
        public float RoundWeight
        {
            get => _roundWeight > 0f ? _roundWeight : Damage;
            internal set => _roundWeight = value;
        }

        private float _roundWeight;

        /// <summary>Rounds one trigger pull or one magazine fires off: the magazine, else the salvo.</summary>
        // Prompt 34 L4: a simultaneous gun's volley is every barrel.
        public int RoundsPerCycle => Clip > 0 ? Clip : Burst * RoundsPerPull;

        /// <summary>Seconds from one magazine's or salvo's first round to the next one's first round.</summary>
        public float CycleSeconds => Clip > 0 ? (Clip - 1) * Cooldown + ClipReload : Cooldown + (Burst - 1) * BurstInterval;

        /// <summary>Damage a second over a whole cycle (reload included), before damage tables and bonuses.</summary>
        public float SustainedDps => Damage * RoundsPerCycle / MathF.Max(0.05f, CycleSeconds);

        /// <summary>Gap between rounds a view draws inside one step: a fast salvo's interval, a magazine's cadence; 0 for neither.</summary>
        public float RoundGap => Burst > 1 ? BurstInterval : Clip > 0 ? Cooldown : 0f;

        public float BurstInterval { get; }

        /// <summary>Layers this weapon can engage: ground vehicles, aircraft or both.</summary>
        public TargetLayers Targets { get; }

        public bool CanTarget(bool flying) => !InterceptOnly && (Targets & (flying ? TargetLayers.Air : TargetLayers.Ground)) != 0;

        /// <summary>
        /// Play-test 6 (DECISIONS 21F): a point-defence gun (the C-RAM's) that fires only at incoming rounds (its
        /// <see cref="ApsDef"/> bursts): it never takes a vehicle or an aircraft as a target.
        /// </summary>
        public bool InterceptOnly { get; internal set; }

        /// <summary>A railgun slug: it goes through everything on its line and hurts all of it.</summary>
        public bool Pierce { get; internal set; }

        /// <summary>A laser: drawn as a beam from the muzzle to the target (it hits at once).</summary>
        public bool Beam { get; internal set; }

        /// <summary>A blow, not a round (the bulldozer's blade): no muzzle flash and no tracer, the hit lands at once.</summary>
        public bool Melee { get; internal set; }

        /// <summary>Seconds a charged weapon (a railgun) powers up, target in sight, before each shot; 0 for none.</summary>
        public float Charge { get; internal set; }

        /// <summary>
        /// Prompt 13 (the owner's slower SAMs): the share of flare decoys a guided missile's seeker sees
        /// through, 0 to 1 (0: an old infrared seeker, pulled off by flares about one time in three;
        /// a radar-guided SAM sees through most of them).
        /// </summary>
        public float FlareResist { get; internal set; }

        // Prompt 29 S05 (C13): capability flags. canHitGround / canHitAir are the targets; the others are computed from the
        // round (DamageSystem.TryIntercept / GunTakes, flares on guided missiles) and these optional data overrides only say
        // "never" or "always" where the round rules would say otherwise (balance.json "interceptable", "flareEligible",
        // "apsEligible", "ciwsEligible"). Null: the round decides.
        public bool CanHitGround => CanTarget(false);
        public bool CanHitAir => CanTarget(true);
        public bool? Interceptable { get; internal set; }
        public bool? FlareEligible { get; internal set; }
        public bool? ApsEligible { get; internal set; }
        public bool? CiwsEligible { get; internal set; }

        /// <summary>
        /// Prompt 13 B: the weapon family its round belongs to (mg, autocannon, tank_gun, howitzer, mortar,
        /// rocket, atgm, aa_missile, bomb, cruise, ballistic, drone, flame, laser, railgun, grenade, melee),
        /// or null. Within a family damage per round rises with <see cref="Size"/>.
        /// </summary>
        public string? Family { get; internal set; }

        /// <summary>The round's size in its family: the calibre in mm, or a missile's, bomb's or drone's kg.</summary>
        public float Size { get; internal set; }

        /// <summary>The real weapon it is (M256 120 mm, 9M133 Kornet), for the detail screen; null when none.</summary>
        public string? RealName { get; internal set; }

        /// <summary>
        /// Prompt 25 A3: the weapon family it belongs to (data "weaponFamily": every weapon that is the same real weapon
        /// takes the family's speed, blast radius, round model and round weight), or null.
        /// </summary>
        public string? WeaponFamily { get; internal set; }

        /// <summary>
        /// Prompt 15 B.1: how deep its rounds pierce, 0 (a 7.62 mm machine gun) to 4 (120 mm darts, heavy
        /// anti-tank missiles, railguns). Data "pen"; without it, by family and size
        /// (<see cref="Armour.DefaultPenetration(WeaponDef)"/>). Shaped charges pierce by their warhead, not their size.
        /// </summary>
        public int Penetration
        {
            get => _penetration >= 0 ? _penetration : Armour.DefaultPenetration(this);
            internal set => _penetration = Math.Clamp(value, 0, ArmourLevels.Max);
        }

        private int _penetration = -1;

        /// <summary>Prompt 15 B.3: a top-attack weapon (a top-attack missile, a diving drone, bomblets): it strikes the roof.</summary>
        public bool TopAttack { get; internal set; }

        /// <summary>
        /// Prompt 16: laid and fired by the boss system (a ship's main battery, its cruise missiles): the combat
        /// system never picks a target for it, and its mount keeps the heading it was given (data "laid").
        /// </summary>
        public bool Laid { get; internal set; }

        /// <summary>
        /// Prompt 15 C.3: high explosive with the thermobaric tag (the TOS, thermobaric rockets): more against
        /// structures and dug-in targets, its blast falls off less, and cages do not stop it.
        /// </summary>
        public bool Thermobaric { get; internal set; }

        /// <summary>Prompt 15 D.3: the shape of its round, for the icon. Data "form"; without it, by family (<see cref="Armour.DefaultForm"/>).</summary>
        public WeaponForm Form
        {
            get => _form ?? Armour.DefaultForm(this);
            internal set => _form = value;
        }

        private WeaponForm? _form;

        /// <summary>
        /// Play-test 8 A (DECISIONS 22Q): a bomb steered onto its target (data "guided": the SDB, the JDAM; or the GuidedBomb
        /// form): it glides down onto the target. Every other bomb falls where its drop point and its fall put it.
        /// </summary>
        public bool GuidedBomb => Projectile == ProjectileKind.Bomb && (Steered || _form == WeaponForm.GuidedBomb);

        /// <summary>Data "guided" (see <see cref="GuidedBomb"/>).</summary>
        internal bool Steered { get; set; }

        /// <summary>Its rounds burst over an area (a splash radius).</summary>
        public bool Splashes => SplashRadius > 0f || Cluster != null;

        /// <summary>
        /// Made to kill armour: a kinetic dart or slug, a shaped charge or a beam that pierces level 3 or more
        /// (what the roles, the commander and the base cover count as anti-tank).
        /// </summary>
        public bool AntiArmour => Penetration >= 3 && DamageType is DamageType.Kinetic or DamageType.ShapedCharge or DamageType.Energy;

        /// <summary>
        /// A round that strikes sparks off armour when it lands (a tank gun's round, an armour-piercing cannon
        /// burst, a railgun slug, a shaped charge): the view draws its impact so. Data "piercing" (the rounds
        /// that were "armour-piercing" before prompt 15); the view only, never the damage.
        /// </summary>
        public bool PiercingLook { get; internal set; }

        /// <summary>Extra damage against some targets (see <see cref="DamageBonus"/>).</summary>
        public IReadOnlyList<DamageBonus> Bonuses { get; internal set; } = System.Array.Empty<DamageBonus>();

        /// <summary>The model its rounds fly as (a missile, rocket, bomb, shell or drone), or null for the default of its kind.</summary>
        public string? ProjectileModel { get; internal set; }

        /// <summary>How big that model is drawn (one shell model for 105, 155 and 203 mm).</summary>
        public float ProjectileScale { get; internal set; } = 1f;

        /// <summary>
        /// Prompt 25 B3 (DECISIONS 25B): how long the round is drawn, in metres (the balance sheet's "Kích thước đạn": 0.8
        /// x real from the ground, 0.5 x real from an aircraft, 0.8 m at least), 0 for none ("roundLength"). The view fits
        /// whichever model flies it to that length (its own, a stand-in, its kind's default), before its legibility boost;
        /// <see cref="ProjectileScale"/> stays the one that gives it on the model the game ships.
        /// </summary>
        public float RoundLength { get; internal set; }
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
                Load = Load,
                ImpactScale = ImpactScale,
                InterceptOnly = InterceptOnly,
                Cluster = cluster,
                Pierce = Pierce,
                Beam = Beam,
                Melee = Melee,
                // Everything else the equipment does not change travels with the copy (the charge,
                // the bonuses and the round's model were once lost on a tuned weapon).
                Charge = Charge,
                FlareResist = FlareResist,
                Interceptable = Interceptable, FlareEligible = FlareEligible, ApsEligible = ApsEligible, CiwsEligible = CiwsEligible,
                _penetration = _penetration,
                TopAttack = TopAttack,
                Thermobaric = Thermobaric,
                _form = _form,
                PiercingLook = PiercingLook,
                Family = Family,
                Size = Size,
                CaliberMm = CaliberMm, WarheadKg = WarheadKg, PowerKw = PowerKw, EnergyMj = EnergyMj,
                RealName = RealName,
                WeaponFamily = WeaponFamily,
                // Prompt 34 L1: the family, variant and tier travel with the copy.
                WeaponFamilyId = WeaponFamilyId, WeaponVariantId = WeaponVariantId, Tier = Tier,
                Barrels = Barrels, Simultaneous = Simultaneous,
                Bonuses = Bonuses,
                ProjectileModel = ProjectileModel,
                ProjectileScale = ProjectileScale,
                RoundLength = RoundLength,
                Clip = Clip,
                ClipReload = ClipReload,
                _roundWeight = _roundWeight,
                // Prompt 17 C.
                Ramp = Ramp,
                SwarmReach = SwarmReach,
                // Prompt 26 B.3: a boss weapon's two-layer blast.
                SplashEdge = SplashEdge, EdgeShare = EdgeShare,
                // Prompt 19: the tier it reaches goes with it.
                Ceiling = Ceiling,
                // Prompt 17 D.
                HeRound = HeRound,
                // Tower branches: the air-burst round.
                AirRound = AirRound,
                // Play-test 8 A: a steered bomb stays steered.
                Steered = Steered,
                // Prompt 25 F2 batch A: the new weapons' mechanisms.
                GroundRange = GroundRange, MinReach = MinReach, GroundMinReach = GroundMinReach, GroupPriority = GroupPriority, BigGame = BigGame, JamProof = JamProof,
                OneAtATime = OneAtATime, Lofted = Lofted, Mrsi = Mrsi, Glides = Glides, Prey = Prey,
                // Play-test 13 (lane C): the flight profile.
                FlightData = FlightData,
                // The bomb-run fix: the stick travels with the copy.
                Stick = Stick,
                // Prompt 25 G: the gun's second rounds (the rounds are not tuned: the gun's reach and cadence govern).
                Rounds = Rounds,
                RoundOf = RoundOf,
                RoundKind = RoundKind,
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

        /// <summary>
        /// Prompt 15 B.3: the bomblets' penetration (dual-purpose bomblets carry a small shaped charge); they come
        /// down on the roof. Data "pen" in "cluster".
        /// </summary>
        public int Penetration { get; internal set; } = DefaultPenetration;

        public const int DefaultPenetration = 2;
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

        /// <summary>Prompt 26 B.3: the outer radius of a two-layer blast (<see cref="Radius"/> is its core); 0: one layer.</summary>
        public float Edge { get; set; }

        /// <summary>Prompt 26 B.3: the share of the damage the edge layer takes.</summary>
        public float EdgeShare { get; set; } = 0.4f;

        /// <summary>Prompt 26 B.3: a boss's blast: the core at <paramref name="radius"/>, full damage, and an edge twice as wide (at most 20 m) at 40 %.</summary>
        public static ExplosionDef TwoLayer(float damage, float radius, ExplosionTier tier) =>
            new(damage, radius, 0f, tier) { Edge = MathF.Min(WeaponDef.MaxEdge, radius * 2f) is var edge && edge > radius ? edge : 0f };
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

        /// <summary>Prompt 26 B.5: its weapons fire this many times as fast from then on (phase 3: 1.25), multiplied in.</summary>
        public float FireRate { get; set; } = 1f;

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
            Armor = flying ? ArmorClass.Air : armor;
            Armour = ArmourLevels.OfClass(Armor);
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
        /// A vehicle card a deck can hold (false: only an item's or a mission's vehicle, such as the Gunship
        /// item's AC-130, prompt 13 E.3): never bought, never listed as a card.
        /// </summary>
        public bool Card { get; internal set; } = true;

        /// <summary>Prompt 13 C: stores this aircraft carries of a weapon when fully loaded, over the weapon's own (weapon id: rounds).</summary>
        public IReadOnlyDictionary<string, int> Loads { get; internal set; } = new Dictionary<string, int>();

        /// <summary>
        /// Rounds of <paramref name="weapon"/> this vehicle carries when fully loaded (0: not stores). Only
        /// aircraft carry stores (bosses excepted: a boss fight is its own); ground launchers keep their
        /// magazines and reloads in place.
        /// </summary>
        public int LoadOf(WeaponDef weapon)
        {
            if (!Flying || Boss) return 0;
            return Loads.TryGetValue(weapon.Id, out var n) ? n : weapon.Load;
        }

        /// <summary>
        /// Prompt 13 I.2: the card's measured combat value per CP against the roster's middle (1), from the
        /// combat-value measurement (data "value"): what the commander weighs a card's price by.
        /// </summary>
        public float CombatValue { get; internal set; } = 1f;

        /// <summary>
        /// Seconds from empty to fully loaded at the holding pattern's full rate (prompt 13 C.2; data
        /// "rearmTime"): helicopters and drones about 8.5, fighters 11, attack jets 14, bombers 21.
        /// </summary>
        public float RearmTime { get; internal set; }

        /// <summary>
        /// Circles its target instead of making strafing runs: a gunship's left-hand pylon turn,
        /// which keeps its side-firing guns on the target for as long as it likes.
        /// </summary>
        public bool Orbit { get; internal set; }

        /// <summary>
        /// The pylon turn's radius in metres (data "orbitRadius"); 0: from its main gun's reach. A tight turn keeps a
        /// gunship over what it shoots at, where the battle camera sees it (test feedback 19P).
        /// </summary>
        public float OrbitRadius { get; internal set; }

        /// <summary>Seen only close up (at <see cref="StealthSight"/> of a spotter's sight) unless it has just fired.</summary>
        public bool Stealth { get; internal set; }

        /// <summary>Share of a spotter's sight at which a stealthy aircraft shows.</summary>
        public static float StealthSight => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.VehicleDef.StealthSight;

        /// <summary>
        /// Prompt 25 A1 (the scout jeep): a scout that hides when it stands. Once it has stood still a second, and until
        /// it fires, a spotter sees it only at 1 - this share of its sight (data "stillCamo", 0 to 0.9).
        /// </summary>
        public float StillCamouflage { get; internal set; }

        /// <summary>A fighter on combat air patrol: goes after enemy aircraft well beyond its own post.</summary>
        public bool Interceptor { get; internal set; }

        /// <summary>Can stop in the air to shoot (a Harrier or F-35B): a few seconds at a time, then it must fly on.</summary>
        public bool Vtol { get; internal set; }

        /// <summary>
        /// Seconds an aeroplane holds its guns on the target once it is in reach (test feedback 2,
        /// DECISIONS 12F): a VTOL jet hovers, any other slows to a crawl with its nose on the target,
        /// then it breaks away, comes round and holds again. 0: plain strafing passes (bombers).
        /// </summary>
        public float AttackHold { get; internal set; }

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

        /// <summary>
        /// Prompt 25 B1 (DECISIONS 25B): the drawn model's length, width and height in metres (its whole box, gun
        /// included: the balance sheet's "Kích thước model"), 0 when the data gives none ("modelSize"). The view fits the
        /// model's length to it, so an old model and one rebuilt at another size are drawn alike; <see cref="Scale"/>
        /// stays the one that matches the model the game ships (the importer keeps them in step).
        /// </summary>
        public float ModelLength { get; internal set; }

        /// <summary>The drawn model's width in metres (see <see cref="ModelLength"/>).</summary>
        public float ModelWidth { get; internal set; }

        /// <summary>The drawn model's height in metres (see <see cref="ModelLength"/>).</summary>
        public float ModelHeight { get; internal set; }

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

        /// <summary>Re-arms friendly vehicles around it (the ammunition carrier; engineers before prompt 13).</summary>
        public AuraDef? RearmAura { get; internal set; }

        /// <summary>A forward rearm point for helicopters (the ammunition carrier): their stores come back twice as fast beside it.</summary>
        public AuraDef? AirRearm { get; internal set; }

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

        /// <summary>
        /// The broad class (Air, Structure, or on the ground Heavy from front armour 3, else Light): what roles,
        /// the commander and the cards read. Damage reads <see cref="Armour"/> and <see cref="Kind"/>.
        /// </summary>
        public ArmorClass Armor { get; private set; }

        /// <summary>Prompt 15 A: its armour level on each face (0-4).</summary>
        public ArmourLevels Armour { get; private set; }

        /// <summary>What the damage-type table reads it as: in the air, a structure (towers, buildings: high explosive's extra), else the ground.</summary>
        public TargetKind Kind => Flying ? TargetKind.Air : Armor == ArmorClass.Structure ? TargetKind.Structure : TargetKind.Ground;

        /// <summary>Sets its armour levels (the catalog, from the data) and with them its broad class; a structure stays one.</summary>
        internal void SetArmour(ArmourLevels levels, bool structure)
        {
            Armour = levels;
            Armor = Flying ? ArmorClass.Air : structure ? ArmorClass.Structure : levels.GroundClass;
        }

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
            Armour = armor == ArmorClass.Structure ? ArmourLevels.Uniform(1) : ArmourLevels.OfClass(armor);
            MaxHp = Guard.Positive(maxHp, id, "hp");
            Width = Guard.Positive(width, id, nameof(width));
            Depth = Guard.Positive(depth, id, nameof(depth));
            BlocksMovement = blocksMovement;
            Explosion = explosion;
        }

        public string Id { get; }
        public ArmorClass Armor { get; }

        /// <summary>
        /// Prompt 15 A.3: its armour level (the same all round): a house, a wall or sandbags 1 by default, a
        /// wreck by its class; data "armour" (a concrete base wall 3, a fortress gate or HQ 4).
        /// </summary>
        public ArmourLevels Armour { get; internal set; }

        /// <summary>What the damage-type table reads it as: a building is a structure, a wreck the ground.</summary>
        public TargetKind Kind => Armor == ArmorClass.Structure ? TargetKind.Structure : TargetKind.Ground;

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
