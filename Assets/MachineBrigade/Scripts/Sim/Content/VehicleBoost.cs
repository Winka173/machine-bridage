#nullable enable
using System;
using System.Collections.Generic;
using System.Text;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// What a side's upgrades (card ranks and equipment) do to one of its vehicles: multipliers on
    /// its health, damage, rate of fire and speed and on the damage it takes, self-repair as a
    /// share of health a second out of combat, a special module, the equipment's other stat lines
    /// (<see cref="Stats"/>, indexed by <see cref="StatId"/>) and its unique traits. Applied when
    /// the vehicle enters the battle; the defaults change nothing.
    /// </summary>
    public readonly struct VehicleBoost
    {
        public VehicleBoost(float hp, float damage, float fireRate, float speed, float damageTaken, float regen, SpecialModule special, float specialPower,
            float[]? stats = null, GearTrait[]? traits = null, float specialPower2 = 0f)
        {
            Hp = hp;
            Damage = damage;
            FireRate = fireRate;
            Speed = speed;
            DamageTaken = damageTaken;
            Regen = regen;
            Special = special;
            SpecialPower = specialPower;
            SpecialPower2 = specialPower2;
            Stats = stats;
            Traits = traits;
        }

        public float Hp { get; }
        public float Damage { get; }
        public float FireRate { get; }
        public float Speed { get; }
        public float DamageTaken { get; }
        public float Regen { get; }
        public SpecialModule Special { get; }

        /// <summary>The module's strength (a damage cut, a repair rate, a bonus, a smoke radius, charges).</summary>
        public float SpecialPower { get; }

        /// <summary>The module's second number where it has one (a cooldown, a radius).</summary>
        public float SpecialPower2 { get; }

        /// <summary>
        /// The other stat lines of the loadout, already capped (null: none). The first six
        /// (<see cref="StatId.Damage"/> to <see cref="StatId.DamageTaken"/>) are folded into the
        /// multipliers above by whoever builds the boost; the simulation reads the rest.
        /// </summary>
        public float[]? Stats { get; }

        /// <summary>Unique traits (Epic and Legendary equipment) and set behaviours (null: none).</summary>
        public GearTrait[]? Traits { get; }

        public float Stat(StatId id) => Stats != null && (int)id < Stats.Length ? Stats[(int)id] : 0f;

        public static VehicleBoost None => new(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f);
    }

    /// <summary>
    /// Every stat line equipment can carry. Values are fractions (0.08 = 8 %) except
    /// <see cref="RegenDelay"/> (seconds). Reductions (spread, reload, resistances) are positive
    /// when they help; a trade-off's drawback arrives as a negative value.
    /// </summary>
    public enum StatId
    {
        // Folded into VehicleBoost's multipliers by the builder.
        Damage,
        FireRate,
        Health,
        Speed,
        Regen,
        DamageTaken,

        /// <summary>More damage against light ground vehicles (gear balance 04/10: chassis armour class 0-2, not the face struck).</summary>
        DamageVsLight,
        /// <summary>More damage against heavy ground vehicles (gear balance 04/10: chassis armour class 3-5, whichever face is struck).</summary>
        DamageVsHeavy,
        DamageVsAir,
        DamageVsStructure,
        Range,
        Vision,
        Spread,
        ProjectileSpeed,
        Magazine,
        MagazineReload,

        // One per DamageType, in its order (ResistKinetic + (int)type) for the first five; energy's is
        // appended (Stats.Resist). Prompt 15: 17 was armour-piercing (now shaped charges), 20 flak (now fragmentation).
        ResistKinetic,
        ResistShapedCharge,
        ResistHighExplosive,
        ResistFire,
        ResistFragmentation,

        TurnRate,
        TurretRate,
        CaptureRate,
        Cooldowns,
        Splash,
        SecondaryFireRate,
        SalvoInterval,
        /// <summary>Prompt 15 C.9: a cage (slat armour): less from shaped charges on rockets, missiles and drones (thermobaric blasts go through).</summary>
        ResistRocket,
        ResistIndirect,
        ResistMine,
        ResistFrontal,
        TransitSpeed,
        StillVision,
        Camouflage,
        RegenDelay,
        StatusDuration,
        SpreadLong,
        SpreadMoving,
        BurnDamage,
        SummonPower,
        RepairReceived,

        // Prompt 8 (appended: saves keep stat ids as numbers).
        /// <summary>More damage on a hit from the side or rear (Flanking Rounds).</summary>
        DamageFlank,
        /// <summary>More damage to drones, and a share of the rockets, missiles and drones aimed at it shot down (Airburst Rounds).</summary>
        DamageVsDrone,
        /// <summary>Share of an empty magazine that comes back at once, once a life (Spare Magazine).</summary>
        SpareMagazine,
        /// <summary>Enemy missiles must be this share closer to lock on (Radar-Absorbent Coating).</summary>
        LockRange,
        /// <summary>Smoke radius thrown when an anti-tank missile locks on, every 20 s (Laser Warning).</summary>
        LaserWarning,
        /// <summary>Faster in reverse, and backs off from enemies that close in, nose on (Reverse Gearbox).</summary>
        ReverseSpeed,
        /// <summary>Less damage from blasts and mines, not direct hits (Underbelly Armour).</summary>
        ResistBlast,

        // Prompt 15 C.9 (appended: saves keep stat ids as numbers).
        /// <summary>Less energy damage (lasers, beams).</summary>
        ResistEnergy,
        /// <summary>Part levels of penetration on its rounds (a whole level at the top: Tungsten Penetrator).</summary>
        Penetration,
        /// <summary>Part levels of armour on its sides and rear (Appliqué Steel).</summary>
        ArmourSide,
        /// <summary>Part levels of armour all round (the Armoured Tub, an aircraft's cockpit tub).</summary>
        ArmourAll,
        Count,
    }

    public static class Stats
    {
        /// <summary>The resistance stat line of a damage type.</summary>
        public static StatId Resist(DamageType type) => type == DamageType.Energy ? StatId.ResistEnergy : StatId.ResistKinetic + (int)type;

        /// <summary>Stat lines counted in armour or penetration levels, not per cent (the view prints "+0.4 levels").</summary>
        public static bool InLevels(StatId id) => id is StatId.Penetration or StatId.ArmourSide or StatId.ArmourAll;
    }

    /// <summary>A unique trait (or a set's four-piece behaviour) with its numbers (see the catalogue in Game/Match/GearCatalog.cs).</summary>
    public enum TraitId
    {
        None,

        // Weapon
        TwinFeed,
        IncendiaryRounds,
        RicochetShells,
        ClusterWarhead,
        ShredderRounds,
        OpeningSalvo,
        MomentumGun,
        Executioner,
        TandemWarhead,
        SuppressionRounds,

        // Loader
        HullDownCrew,
        KillReload,
        RapidResponse,
        OverpressureChamber,
        HotSwap,
        SkywardPintle,

        // Armour and plating
        AegisBarrier,
        Unbreakable,
        GuardianLink,
        DarkCrown,
        AdaptivePlating,
        ReactiveBlocks,
        AblativeLayer,
        AngledGlacis,
        SiegeAnchor,

        // Engine
        NitroDash,
        ShootAndScoot,
        RapidDeployment,
        VolatileFuelTanks,
        AfterburnerReserve,

        // Repair
        FieldMechanics,
        EmergencyRepairKit,
        CombatWelder,
        SalvageTeam,
        AmmoCarrier,
        DamageControl,

        // Optics
        ThermalImager,
        LaserDesignator,
        GhillieMode,
        CounterBatteryRadar,
        EwJammer,
        FireControlComputer,

        // Base-type extras (Mine Rollers at Epic and up)
        MineSweep,

        // Set four-piece behaviours
        SetBulwark,
        SetHitAndRun,
        SetFirestorm,
        SetDeepStrike,
        SetSharedShield,
        SetStrafingRun,
        SetSwarm,
        SetSalvageRights,
        SetGhostNet,
        SetHeavyRound,

        // Tower equipment's own lines (the Weapon, Structure and Systems slots of a tower type)
        TowerFireLink,
        TowerCounterBattery,
        TowerModular,
        TowerSmokeLaunchers,
        TowerBackupGenerator,

        // Prompt 8: new unique lines, the new brands' behaviours.
        Vengeance,
        SuppressiveFire,
        Rearguard,
        SetPackHunt,
        SetPackFocus,
        SetPhoenix,
        SetBulwarkPost,
        Count,
    }

    /// <summary>One trait on a vehicle: its id and up to three numbers (its Epic or Legendary values).</summary>
    public readonly struct GearTrait
    {
        public GearTrait(TraitId id, float a, float b = 0f, float c = 0f)
        {
            Id = id;
            A = a;
            B = b;
            C = c;
        }

        public TraitId Id { get; }
        public float A { get; }
        public float B { get; }
        public float C { get; }
    }

    /// <summary>The special module of an equipment loadout (its seventh slot).</summary>
    public enum SpecialModule
    {
        None,

        /// <summary>Explosive reactive armour: takes less damage.</summary>
        ReactiveArmor,

        /// <summary>Repairs itself a little every second once it has not been hit for a few seconds.</summary>
        AutoRepair,

        /// <summary>A veteran crew: hits harder and fires faster.</summary>
        VeteranCrew,

        /// <summary>Throws a smoke screen round itself the first time it drops below half health (again below a quarter at Legendary).</summary>
        SmokeDischarger,

        /// <summary>An active protection system: shoots down incoming missiles, drones and rockets (power: charges, power 2: recharge).</summary>
        TrophyAps,

        /// <summary>Aircraft: flares when a missile is launched at it (power: seconds, power 2: cooldown).</summary>
        FlareDispenser,

        /// <summary>Launches kamikaze drones at the nearest enemy (power: drones, power 2: interval).</summary>
        DroneEscort,

        /// <summary>On death, stuns enemy ground vehicles round it (power: seconds, power 2: radius).</summary>
        EmpPayload,

        /// <summary>Drops mines behind it while moving (power: mines alive, power 2: interval).</summary>
        MineDispenser,

        /// <summary>Its kills refund more CP (power: the extra share).</summary>
        WarProfiteer,

        /// <summary>Allies round it deal more damage (power: bonus, power 2: radius).</summary>
        RallyHorn,

        /// <summary>Once per life, when allies round it are under fire, all of them become invulnerable (power: seconds).</summary>
        AegisDome,

        /// <summary>Drops a decoy that draws missiles and shells aimed at it (power: seconds, power 2: cooldown).</summary>
        DecoyLauncher,

        /// <summary>Calls light mortar rounds onto its target (power: rounds, power 2: interval).</summary>
        UplinkBarrage,
    }

    /// <summary>
    /// The snake_case keys of traits and modules ("twin_feed", "trophy_aps"): what the game's save,
    /// strings and pictures use, and what a <see cref="Events.SimEventKind.TraitProc"/> event carries.
    /// </summary>
    public static class GearKeys
    {
        private static readonly string[] TraitKeys = Build(typeof(TraitId), (int)TraitId.Count);
        private static readonly string[] ModuleKeys = Build(typeof(SpecialModule), Enum.GetValues(typeof(SpecialModule)).Length);
        private static readonly Dictionary<string, TraitId> TraitByKey = new();
        private static readonly Dictionary<string, SpecialModule> ModuleByKey = new();

        static GearKeys()
        {
            for (var i = 1; i < TraitKeys.Length; i++) TraitByKey[TraitKeys[i]] = (TraitId)i;
            for (var i = 1; i < ModuleKeys.Length; i++) ModuleByKey[ModuleKeys[i]] = (SpecialModule)i;
        }

        public static string Trait(TraitId id) => (int)id >= 0 && (int)id < TraitKeys.Length ? TraitKeys[(int)id] : "";

        public static string Module(SpecialModule module) => (int)module >= 0 && (int)module < ModuleKeys.Length ? ModuleKeys[(int)module] : "";

        public static TraitId ParseTrait(string? key) => key != null && TraitByKey.TryGetValue(key, out var id) ? id : TraitId.None;

        public static SpecialModule ParseModule(string? key) => key != null && ModuleByKey.TryGetValue(key, out var m) ? m : SpecialModule.None;

        /// <summary>"TwinFeed" to "twin_feed".</summary>
        public static string Snake(string pascal)
        {
            var sb = new StringBuilder(pascal.Length + 4);
            for (var i = 0; i < pascal.Length; i++)
            {
                var c = pascal[i];
                if (char.IsUpper(c))
                {
                    if (i > 0) sb.Append('_');
                    sb.Append(char.ToLowerInvariant(c));
                }
                else sb.Append(c);
            }
            return sb.ToString();
        }

        private static string[] Build(Type type, int count)
        {
            var keys = new string[count];
            for (var i = 0; i < count; i++) keys[i] = i == 0 ? "" : Snake(Enum.GetName(type, i) ?? "");
            return keys;
        }
    }
}
