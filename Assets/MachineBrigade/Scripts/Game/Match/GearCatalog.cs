using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>Which branches of the army a piece or trait is meant for (crates favour the player's deck).</summary>
    [Flags]
    public enum BranchMask
    {
        None = 0,
        Armor = 1 << GearBranch.Armor,
        Light = 1 << GearBranch.Light,
        Artillery = 1 << GearBranch.Artillery,
        Air = 1 << GearBranch.Air,
        All = Armor | Light | Artillery | Air,
    }

    /// <summary>
    /// A base type: what a piece is (a long barrel, a slat cage), its picture, and its implicit
    /// line (one, or two for a merged type), which grows with level like the main stat. Trade-offs
    /// drop at Rare and up only; their drawback grows with the piece's level and rarity as its gain
    /// does. Which branches it fits is worked out from what its lines need (<see cref="VehicleFit"/>).
    /// </summary>
    public sealed class BaseTypeDef
    {
        public BaseTypeDef(string id, GearSlot slot, BranchMask branches, StatId implicitStat, float[] top)
        {
            Id = id;
            Slot = slot;
            _hint = branches;
            Implicit = implicitStat;
            Top = top;
        }

        /// <summary>A vehicle base type (its branches come from what its lines need).</summary>
        public BaseTypeDef(string id, GearSlot slot, StatId implicitStat, float[] top) : this(id, slot, BranchMask.None, implicitStat, top) { }

        private readonly BranchMask _hint;
        private BranchMask? _fit;

        /// <summary>Its id: the save's key, the strings' key and the picture's name (Resources/UI/Gear/&lt;id&gt;.png).</summary>
        public string Id { get; }

        public GearSlot Slot { get; }

        /// <summary>The branches it works for (from its lines' needs and the roster; tower base types: none).</summary>
        public BranchMask Branches => Gear.IsTower(Slot) ? _hint : _fit ??= VehicleFit.BranchesFor(VehicleFit.Need(this));

        /// <summary>The implicit line's stat (<see cref="StatId.Count"/>: none).</summary>
        public StatId Implicit { get; }

        /// <summary>The implicit line at each rarity's top level, Common to Legendary.</summary>
        public float[] Top { get; }

        /// <summary>A second implicit line (a merged type: the drivetrain's turret traverse, the signal relay's vision), or none.</summary>
        public StatId Implicit2 { get; set; } = StatId.Count;

        public float[] Top2 { get; set; }

        /// <summary>The implicit line does not grow with level (a smoke radius, a share of a magazine).</summary>
        public bool Flat { get; set; }

        /// <summary>A trade-off's drawback and its value by rarity at the top level (negative); it grows with level as the gain does.</summary>
        public StatId Penalty { get; set; } = StatId.Count;

        public float[] PenaltyTop { get; set; }

        /// <summary>Lowest rarity it drops at (trade-offs: Rare).</summary>
        public int MinRarity { get; set; }

        /// <summary>A plating base type of the Armor slot: its main stat is less damage taken instead of health.</summary>
        public bool Plating { get; set; }

        /// <summary>Main stat multiplier (Monolith Plate: 1.8).</summary>
        public float MainScale { get; set; } = 1f;

        /// <summary>Rolls no sub-stats (Monolith Plate).</summary>
        public bool NoSubs { get; set; }

        /// <summary>A hidden extra from a rarity up (none since the Mine Rollers became the Underbelly Armour).</summary>
        public TraitId Extra { get; set; }

        public int ExtraFrom { get; set; } = 99;

        /// <summary>
        /// The stat its main line raises when it is not its slot's (<see cref="StatId.Count"/>: the
        /// slot's own). Tower base types use it: an ammunition hoist raises rate of fire, traverse
        /// motors the turret's turn rate.
        /// </summary>
        public StatId Main { get; set; } = StatId.Count;

        public bool TradeOff => Penalty != StatId.Count;
    }

    /// <summary>A unique trait: the slot whose pool it is in, what a vehicle needs for it to work (so the branches it suits), and its numbers at Epic and Legendary.</summary>
    public sealed class TraitDef
    {
        public TraitDef(TraitId id, GearSlot slot, BranchMask branches, float[] epic, float[] legendary)
        {
            Id = id;
            Slot = slot;
            _hint = branches;
            Epic = epic;
            Legendary = legendary;
        }

        /// <summary>A vehicle trait: works for every branch where a vehicle has what <paramref name="need"/> asks.</summary>
        public TraitDef(TraitId id, GearSlot slot, VehicleNeed need, float[] epic, float[] legendary) : this(id, slot, BranchMask.None, epic, legendary) =>
            Needs = need;

        private readonly BranchMask _hint;
        private BranchMask? _fit;

        public TraitId Id { get; }
        public GearSlot Slot { get; }

        /// <summary>The branches it works for (vehicle traits: from its need; tower traits: none).</summary>
        public BranchMask Branches => Gear.IsTower(Slot) ? _hint : _fit ??= VehicleFit.BranchesFor(Needs);

        public float[] Epic { get; }
        public float[] Legendary { get; }
        public string Key => GearKeys.Trait(Id);

        /// <summary>What a vehicle must have for it to do anything (vehicle pools; see <see cref="VehicleFit"/>).</summary>
        public VehicleNeed Needs { get; set; }

        /// <summary>What a tower must have for it to do anything (tower pools only; see <see cref="TowerFit"/>).</summary>
        public TowerNeed Need { get; set; }

        public GearTrait At(Rarity rarity)
        {
            var v = rarity >= Rarity.Legendary ? Legendary : Epic;
            return new GearTrait(Id, v.Length > 0 ? v[0] : 0f, v.Length > 1 ? v[1] : 0f, v.Length > 2 ? v[2] : 0f);
        }
    }

    /// <summary>A special module: its numbers at Epic and Legendary (power, power 2) and what a vehicle needs for it (so the branches it suits).</summary>
    public sealed class ModuleDef
    {
        public ModuleDef(SpecialModule module, VehicleNeed need, float epic, float legendary, float epic2 = 0f, float legendary2 = 0f)
        {
            Module = module;
            Needs = need;
            Epic = epic;
            Legendary = legendary;
            Epic2 = epic2;
            Legendary2 = legendary2;
        }

        private BranchMask? _fit;

        public SpecialModule Module { get; }
        public VehicleNeed Needs { get; }
        public BranchMask Branches => _fit ??= VehicleFit.BranchesFor(Needs);
        public float Epic { get; }
        public float Legendary { get; }
        public float Epic2 { get; }
        public float Legendary2 { get; }
        public string Key => GearKeys.Module(Module);

        /// <summary>Its effect is sized to the vehicle's price (CP / 7, between 0.4 and 1.3; prompt 8 I.5).</summary>
        public bool Scaled => Module is SpecialModule.DroneEscort or SpecialModule.UplinkBarrage or SpecialModule.MineDispenser or SpecialModule.EmpPayload;
    }

    /// <summary>A sub-stat of the pool: values at the top level for Uncommon to Legendary, the slots it rolls on, and its loadout cap.</summary>
    public sealed class SubDef
    {
        public SubDef(StatId stat, float[] values, GearSlot[] slots, float weight = 1f)
        {
            Stat = stat;
            Values = values;
            Slots = slots;
            Weight = weight;
        }

        public StatId Stat { get; }
        public float[] Values { get; }
        public GearSlot[] Slots { get; }
        public float Weight { get; }

        public bool RollsOn(GearSlot slot) => Array.IndexOf(Slots, slot) >= 0;
    }

    /// <summary>A set brand: its two-piece bonus (a stat line, or a behaviour) and its four-piece behaviour.</summary>
    public sealed class BrandDef
    {
        public BrandDef(int index, string id, StatId stat, float value, GearTrait fourPiece)
        {
            Index = index;
            Id = id;
            Stat = stat;
            Value = value;
            FourPiece = fourPiece;
        }

        /// <summary>1 to 13 (0 on a piece: no brand).</summary>
        public int Index { get; }

        public string Id { get; }

        /// <summary>The two-piece stat line (<see cref="StatId.Count"/>: the two-piece bonus is a behaviour, <see cref="TwoPiece"/>).</summary>
        public StatId Stat { get; }

        public float Value { get; }

        /// <summary>A two-piece behaviour instead of a stat line (Wolfpack Tactics' pack bonus).</summary>
        public GearTrait TwoPiece { get; set; }

        public GearTrait FourPiece { get; }

        /// <summary>A brand of tower equipment (Bulwark Engineering): its pieces count across the whole base.</summary>
        public bool TowerOnly { get; set; }

        private BranchMask? _fit;

        /// <summary>The branches either of its bonuses works for.</summary>
        public BranchMask Branches => TowerOnly ? BranchMask.None : _fit ??= VehicleFit.BranchesFor(VehicleFit.Need(this, false)) | VehicleFit.BranchesFor(VehicleFit.Need(this, true));
    }

    /// <summary>
    /// The equipment catalogue (Docs research: base types after Path of Exile and Borderlands,
    /// sub-stats after The Division 2, unique traits after Archero, Warframe and Clash of Clans,
    /// brands after The Division 2's gear sets): 38 stat base types, 14 special modules, 45
    /// traits and 13 brands (one of them for towers). Numbers are at the top level; level 1 has 40 %
    /// of a main stat or implicit line.
    /// </summary>
    public static partial class GearCatalog
    {
        private static float[] V(params float[] v) => v;

        private const VehicleNeed Any = VehicleNeed.None, Armed = VehicleNeed.Armed, Ground = VehicleNeed.Ground, Flying = VehicleNeed.Flying;

        public static readonly BaseTypeDef[] Bases =
        {
            // Weapon: main stat +damage.
            new("long_barrel", GearSlot.Weapon, StatId.Range, V(0.02f, 0.03f, 0.04f, 0.06f, 0.08f)),
            // Prompt 15 C.9: a level of penetration at the top (part levels below it), not a share against heavy vehicles.
            new("tungsten_penetrator", GearSlot.Weapon, StatId.Penetration, V(0.4f, 0.55f, 0.7f, 0.85f, 1f)),
            new("he_frag_filler", GearSlot.Weapon, StatId.Splash, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("proximity_fuze", GearSlot.Weapon, StatId.DamageVsAir, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("bunker_buster", GearSlot.Weapon, StatId.DamageVsStructure, V(0.06f, 0.09f, 0.13f, 0.18f, 0.24f)),
            new("heavy_barrel", GearSlot.Weapon, StatId.Range, V(0f, 0f, 0.08f, 0.1f, 0.12f))
                { Penalty = StatId.Speed, PenaltyTop = V(0f, 0f, -0.05f, -0.06f, -0.07f), MinRarity = 2 },
            // Prompt 8: rounds for flank shots, and airburst rounds against drones and what flies at it
            // (the Hyper-Velocity Charge's place: its extra shell speed was hard to feel).
            new("flanking_rounds", GearSlot.Weapon, StatId.DamageFlank, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("airburst_rounds", GearSlot.Weapon, StatId.DamageVsDrone, V(0.08f, 0.12f, 0.18f, 0.24f, 0.3f)),

            // Loader: main stat +fire rate.
            new("carousel_autoloader", GearSlot.Loader, StatId.MagazineReload, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("extended_ammo_rack", GearSlot.Loader, StatId.Magazine, V(0.1f, 0.15f, 0.2f, 0.25f, 0.3f)),
            new("belt_feed", GearSlot.Loader, StatId.SecondaryFireRate, V(0.08f, 0.12f, 0.16f, 0.2f, 0.25f)),
            new("salvo_rack", GearSlot.Loader, StatId.SalvoInterval, V(0.1f, 0.15f, 0.2f, 0.25f, 0.3f)),
            new("hair_trigger", GearSlot.Loader, StatId.FireRate, V(0f, 0f, 0.1f, 0.12f, 0.15f))
                { Penalty = StatId.Spread, PenaltyTop = V(0f, 0f, -0.1f, -0.12f, -0.14f), MinRarity = 2 },
            // Prompt 8: an empty launcher gets part of its magazine back at once, once a life.
            new("spare_magazine", GearSlot.Loader, StatId.SpareMagazine, V(0.4f, 0.55f, 0.7f, 0.85f, 1f)) { Flat = true },

            // Armour: main stat +health.
            new("composite_addon", GearSlot.Armor, StatId.ResistShapedCharge, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f)),
            new("spall_liner", GearSlot.Armor, StatId.ResistHighExplosive, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f)),
            // Prompt 15 C.9: a level of side and rear armour at the top.
            new("applique_steel", GearSlot.Armor, StatId.ArmourSide, V(0.4f, 0.55f, 0.7f, 0.85f, 1f)),
            new("fire_retardant_hull", GearSlot.Armor, StatId.ResistFire, V(0.08f, 0.12f, 0.16f, 0.2f, 0.25f)),
            // Prompt 15 C.9: an aircraft's armoured cockpit tub: a level of armour all round at the top.
            new("armoured_tub", GearSlot.Armor, StatId.ArmourAll, V(0.4f, 0.55f, 0.7f, 0.85f, 1f)),
            new("monolith_plate", GearSlot.Armor, StatId.Count, V(0f, 0f, 0f, 0f, 0f))
                { Penalty = StatId.Speed, PenaltyTop = V(0f, 0f, -0.04f, -0.05f, -0.06f), MinRarity = 2, MainScale = 1.8f, NoSubs = true },
            // Prompt 8: enemy missiles must come closer to lock on.
            new("radar_absorbent_coating", GearSlot.Armor, StatId.LockRange, V(0.06f, 0.09f, 0.13f, 0.16f, 0.2f)),

            // Armour, plating base types: main stat less damage taken.
            new("frontal_wedge", GearSlot.Armor, StatId.ResistFrontal, V(0.05f, 0.08f, 0.11f, 0.15f, 0.18f)) { Plating = true },
            new("slat_cage", GearSlot.Armor, StatId.ResistRocket, V(0.06f, 0.09f, 0.13f, 0.17f, 0.22f)) { Plating = true },
            new("overhead_screen", GearSlot.Armor, StatId.ResistIndirect, V(0.06f, 0.09f, 0.13f, 0.17f, 0.22f)) { Plating = true },
            // The Mine Rollers renamed (prompt 8 I.8): blasts and mines, so it works in every battle.
            new("underbelly_armor", GearSlot.Armor, StatId.ResistBlast, V(0.05f, 0.08f, 0.11f, 0.15f, 0.18f)) { Plating = true },

            // Engine: main stat +speed.
            // The Turbocharger and the Turret Drive merged (prompt 8 I.8): hull and turret turn faster.
            new("drivetrain", GearSlot.Engine, StatId.TurnRate, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f))
                { Implicit2 = StatId.TurretRate, Top2 = V(0.08f, 0.12f, 0.16f, 0.2f, 0.25f) },
            new("transit_gearbox", GearSlot.Engine, StatId.TransitSpeed, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("overtuned_engine", GearSlot.Engine, StatId.Speed, V(0f, 0f, 0.1f, 0.12f, 0.15f))
                { Penalty = StatId.Health, PenaltyTop = V(0f, 0f, -0.04f, -0.05f, -0.06f), MinRarity = 2 },
            // Prompt 8: faster in reverse, and it backs off nose-on from enemies that close in.
            new("reverse_gearbox", GearSlot.Engine, StatId.ReverseSpeed, V(0.15f, 0.2f, 0.28f, 0.34f, 0.4f)),

            // Repair: main stat regeneration out of combat.
            new("toolbox", GearSlot.Repair, StatId.RegenDelay, V(1f, 1.5f, 2f, 2.5f, 3f)),
            new("crew_drills", GearSlot.Repair, StatId.Cooldowns, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f)),
            new("fire_extinguisher", GearSlot.Repair, StatId.StatusDuration, V(0.1f, 0.18f, 0.26f, 0.34f, 0.42f)),

            // Optics: main stat +vision.
            new("laser_rangefinder", GearSlot.Optics, StatId.SpreadLong, V(0.08f, 0.12f, 0.16f, 0.2f, 0.25f)),
            new("gun_stabiliser", GearSlot.Optics, StatId.SpreadMoving, V(0.1f, 0.15f, 0.2f, 0.25f, 0.3f)),
            new("commanders_periscope", GearSlot.Optics, StatId.StillVision, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("camouflage_net", GearSlot.Optics, StatId.Camouflage, V(0.05f, 0.08f, 0.11f, 0.15f, 0.18f)),
            // Prompt 8 I.8: the capture rate stays, and a little more sight for the modes with no points.
            new("signal_relay", GearSlot.Optics, StatId.CaptureRate, V(0.1f, 0.15f, 0.2f, 0.25f, 0.3f))
                { Implicit2 = StatId.Vision, Top2 = V(0.03f, 0.04f, 0.06f, 0.08f, 0.1f) },
            // Prompt 8: a smoke screen when an anti-tank missile locks on (every 20 s); the radius.
            new("laser_warning", GearSlot.Optics, StatId.LaserWarning, V(6f, 6.5f, 7f, 7.5f, 8f)) { Flat = true },
        };

        /// <summary>
        /// Special modules, Epic / Legendary, and what a vehicle needs for each. The fixed-effect ones
        /// (drone escort, uplink barrage, mine dispenser, EMP payload) are sized to the vehicle's price.
        /// </summary>
        public static readonly ModuleDef[] Modules =
        {
            // Prompt 15 C.9: reactive armour cuts shaped charges hard and nothing else (it was 12-18 % of everything).
            new(SpecialModule.ReactiveArmor, Ground, 0.4f, 0.55f),
            new(SpecialModule.AutoRepair, Any, 0.012f, 0.018f),
            new(SpecialModule.VeteranCrew, Armed, 0.08f, 0.12f),
            new(SpecialModule.SmokeDischarger, Ground, 8f, 10f, 0f, 1f),
            // Prompt 29 L5: Trophy only for a vehicle with an APS mount (ApsCapability not None), the heat decoys only for
            // flares as charges (FlareCharges above 0); see VehicleFit.Hardware.
            new(SpecialModule.TrophyAps, Ground | VehicleNeed.ApsMount, 1f, 2f, 25f, 20f),
            new(SpecialModule.FlareDispenser, Flying | VehicleNeed.Flares, 3f, 4f, 25f, 18f),
            new(SpecialModule.DroneEscort, Any, 1f, 2f, 25f, 20f),
            new(SpecialModule.EmpPayload, Any, 2f, 3f, 10f, 14f),
            new(SpecialModule.MineDispenser, Ground, 2f, 3f, 20f, 15f),
            new(SpecialModule.WarProfiteer, Armed, 0.5f, 0.8f),
            new(SpecialModule.RallyHorn, Any, 0.06f, 0.1f, 12f, 15f),
            new(SpecialModule.AegisDome, Any, 2f, 3f),
            new(SpecialModule.DecoyLauncher, Ground, 4f, 6f, 35f, 25f),
            new(SpecialModule.UplinkBarrage, VehicleNeed.HitsGround, 3f, 5f, 45f, 35f),
        };

        public static readonly TraitDef[] Traits =
        {
            // Weapon
            new(TraitId.TwinFeed, GearSlot.Weapon, Armed, V(0.15f, 0.15f), V(0.2f, 0.2f)),
            new(TraitId.IncendiaryRounds, GearSlot.Weapon, Armed, V(0.18f), V(0.25f)),
            new(TraitId.RicochetShells, GearSlot.Weapon, VehicleNeed.HitsGround, V(0.35f, 8f), V(0.5f, 10f)),
            new(TraitId.ClusterWarhead, GearSlot.Weapon, VehicleNeed.Lobs, V(5f), V(8f)),
            new(TraitId.ShredderRounds, GearSlot.Weapon, Armed, V(0.03f), V(0.04f)),
            new(TraitId.OpeningSalvo, GearSlot.Weapon, Armed, V(0.35f), V(0.5f)),
            new(TraitId.MomentumGun, GearSlot.Weapon, Armed, V(0.05f), V(0.07f)),
            new(TraitId.Executioner, GearSlot.Weapon, Armed, V(0.4f), V(0.6f)),
            new(TraitId.TandemWarhead, GearSlot.Weapon, VehicleNeed.RocketLike, V(0.1f), V(0.15f)),
            new(TraitId.SuppressionRounds, GearSlot.Weapon, Armed, V(0.15f), V(0.25f)),
            new(TraitId.SuppressiveFire, GearSlot.Weapon, Armed, V(0.1f), V(0.15f)),
            // Loader
            new(TraitId.HullDownCrew, GearSlot.Loader, Armed | Ground, V(0.1f), V(0.15f)),
            new(TraitId.KillReload, GearSlot.Loader, Armed, V(0.25f), V(0.4f)),
            new(TraitId.RapidResponse, GearSlot.Loader, Armed, V(1.4f, 18f), V(1.6f, 14f)),
            new(TraitId.OverpressureChamber, GearSlot.Loader, Armed, V(5f), V(4f)),
            new(TraitId.HotSwap, GearSlot.Loader, VehicleNeed.Magazine, V(0.25f), V(0.4f)),
            new(TraitId.SkywardPintle, GearSlot.Loader, VehicleNeed.SecondaryGun | Ground, V(0.6f), V(0.8f)),
            new(TraitId.Vengeance, GearSlot.Loader, Armed, V(0.15f, 15f, 5f), V(0.2f, 15f, 5f)),
            // Armour and plating
            new(TraitId.AegisBarrier, GearSlot.Armor, Any, V(0.1f, 20f), V(0.15f, 16f)),
            new(TraitId.Unbreakable, GearSlot.Armor, Any, V(1.5f), V(2.5f)),
            new(TraitId.GuardianLink, GearSlot.Armor, VehicleNeed.Heavy | Ground, V(0.15f), V(0.25f)),
            new(TraitId.DarkCrown, GearSlot.Armor, Any, V(0.03f, 0.02f), V(0.04f, 0.03f)),
            new(TraitId.AdaptivePlating, GearSlot.Armor, Any, V(0.05f), V(0.06f)),
            new(TraitId.ReactiveBlocks, GearSlot.Armor, Ground, V(3f, 20f), V(4f, 15f)),
            new(TraitId.AblativeLayer, GearSlot.Armor, Any, V(0.2f), V(0.3f)),
            new(TraitId.AngledGlacis, GearSlot.Armor, Ground, V(6f), V(5f)),
            new(TraitId.SiegeAnchor, GearSlot.Armor, Ground, V(0.15f, 0.08f), V(0.2f, 0.12f)),
            // Engine
            new(TraitId.NitroDash, GearSlot.Engine, Any, V(1.6f, 25f), V(1.8f, 18f)),
            new(TraitId.ShootAndScoot, GearSlot.Engine, Armed | Ground, V(0.4f, 0.15f), V(0.6f, 0.25f)),
            new(TraitId.RapidDeployment, GearSlot.Engine, Any, V(10f), V(15f)),
            new(TraitId.VolatileFuelTanks, GearSlot.Engine, Any, V(0.3f, 8f), V(0.45f, 10f)),
            new(TraitId.AfterburnerReserve, GearSlot.Engine, Flying, V(0.5f), V(0.7f)),
            new(TraitId.Rearguard, GearSlot.Engine, Any, V(0.15f), V(0.2f)),
            // Repair
            new(TraitId.FieldMechanics, GearSlot.Repair, Any, V(0.006f, 12f), V(0.01f, 15f)),
            new(TraitId.EmergencyRepairKit, GearSlot.Repair, Any, V(0.2f), V(0.3f)),
            new(TraitId.CombatWelder, GearSlot.Repair, Any, V(0.4f), V(0.6f)),
            new(TraitId.SalvageTeam, GearSlot.Repair, Armed, V(0.08f), V(0.12f)),
            new(TraitId.AmmoCarrier, GearSlot.Repair, Any, V(0.3f, 12f), V(0.5f, 16f)),
            new(TraitId.DamageControl, GearSlot.Repair, Any, V(15f), V(10f)),
            // Optics
            new(TraitId.ThermalImager, GearSlot.Optics, Any, V(0.6f), V(1f)),
            new(TraitId.LaserDesignator, GearSlot.Optics, VehicleNeed.HitsGround, V(0.08f, 4f), V(0.12f, 6f)),
            new(TraitId.GhillieMode, GearSlot.Optics, Armed | Ground, V(0.25f, 4f), V(0.4f, 3f)),
            new(TraitId.CounterBatteryRadar, GearSlot.Optics, Any, V(0.15f, 80f, 5f), V(0.25f, 100f, 8f)),
            new(TraitId.EwJammer, GearSlot.Optics, Any, V(2f, 15f, 12f), V(3f, 12f, 16f)),
            // Widened (prompt 8 I.1): every gun whose rounds fly unguided leads a moving target, not the artillery alone.
            new(TraitId.FireControlComputer, GearSlot.Optics, VehicleNeed.Unguided, V(0.5f), V(0.75f)),
        };

        public static readonly SubDef[] Subs =
        {
            new(StatId.DamageVsLight, V(0.03f, 0.04f, 0.05f, 0.06f), new[] { GearSlot.Weapon, GearSlot.Loader, GearSlot.Optics }),
            new(StatId.DamageVsHeavy, V(0.03f, 0.04f, 0.05f, 0.06f), new[] { GearSlot.Weapon, GearSlot.Loader, GearSlot.Optics }),
            new(StatId.DamageVsAir, V(0.04f, 0.05f, 0.06f, 0.08f), new[] { GearSlot.Weapon, GearSlot.Loader, GearSlot.Optics }),
            new(StatId.DamageVsStructure, V(0.04f, 0.06f, 0.08f, 0.1f), new[] { GearSlot.Weapon, GearSlot.Loader }),
            new(StatId.FireRate, V(0.015f, 0.02f, 0.03f, 0.04f), new[] { GearSlot.Weapon }),
            new(StatId.Damage, V(0.015f, 0.02f, 0.03f, 0.04f), new[] { GearSlot.Loader, GearSlot.Optics }),
            new(StatId.Range, V(0.02f, 0.025f, 0.03f, 0.04f), new[] { GearSlot.Weapon, GearSlot.Optics }),
            new(StatId.Vision, V(0.03f, 0.04f, 0.05f, 0.06f), new[] { GearSlot.Optics, GearSlot.Engine }),
            new(StatId.Spread, V(0.04f, 0.06f, 0.08f, 0.1f), new[] { GearSlot.Weapon, GearSlot.Optics }),
            new(StatId.ProjectileSpeed, V(0.04f, 0.06f, 0.08f, 0.1f), new[] { GearSlot.Weapon, GearSlot.Loader }),
            new(StatId.Magazine, V(0.05f, 0.08f, 0.1f, 0.12f), new[] { GearSlot.Loader }),
            new(StatId.MagazineReload, V(0.04f, 0.06f, 0.08f, 0.1f), new[] { GearSlot.Loader, GearSlot.Repair }),
            new(StatId.Health, V(0.02f, 0.03f, 0.04f, 0.05f), new[] { GearSlot.Armor, GearSlot.Repair, GearSlot.Engine }),
            new(StatId.ResistKinetic, V(0.03f, 0.04f, 0.06f, 0.08f), new[] { GearSlot.Armor }, 0.2f),
            new(StatId.ResistShapedCharge, V(0.03f, 0.04f, 0.06f, 0.08f), new[] { GearSlot.Armor }, 0.2f),
            new(StatId.ResistHighExplosive, V(0.03f, 0.04f, 0.06f, 0.08f), new[] { GearSlot.Armor }, 0.2f),
            new(StatId.ResistFire, V(0.03f, 0.04f, 0.06f, 0.08f), new[] { GearSlot.Armor }, 0.2f),
            new(StatId.ResistFragmentation, V(0.03f, 0.04f, 0.06f, 0.08f), new[] { GearSlot.Armor }, 0.2f),
            new(StatId.Speed, V(0.015f, 0.02f, 0.03f, 0.04f), new[] { GearSlot.Engine, GearSlot.Armor }),
            new(StatId.TurretRate, V(0.05f, 0.08f, 0.1f, 0.12f), new[] { GearSlot.Engine, GearSlot.Optics }),
            new(StatId.CaptureRate, V(0.05f, 0.08f, 0.1f, 0.12f), new[] { GearSlot.Engine, GearSlot.Optics }),
            new(StatId.Cooldowns, V(0.03f, 0.05f, 0.07f, 0.09f), new[] { GearSlot.Repair, GearSlot.Optics }),
            new(StatId.Regen, V(0.001f, 0.0015f, 0.002f, 0.0025f), new[] { GearSlot.Repair, GearSlot.Armor }),
        };

        /// <summary>The brand index of Bulwark Engineering (tower pieces only).</summary>
        public const int BulwarkBrand = 13;

        public static readonly BrandDef[] Brands =
        {
            new(1, "ironclad", StatId.Health, 0.06f, new GearTrait(TraitId.SetBulwark, 0.15f)),
            new(2, "kestrel", StatId.Speed, 0.05f, new GearTrait(TraitId.SetHitAndRun, 0.2f, 0.5f)),
            new(3, "vulcan", StatId.BurnDamage, 0.25f, new GearTrait(TraitId.SetFirestorm, 0.1f, 6f)),
            new(4, "longbow", StatId.Range, 0.05f, new GearTrait(TraitId.SetDeepStrike, 0.15f)),
            new(5, "aegis", StatId.DamageTaken, 0.05f, new GearTrait(TraitId.SetSharedShield, 0.12f, 25f, 12f)),
            new(6, "stormfront", StatId.ResistFragmentation, 0.1f, new GearTrait(TraitId.SetStrafingRun, 4f, 30f)),
            new(7, "hivemind", StatId.SummonPower, 0.15f, new GearTrait(TraitId.SetSwarm, 10f)),
            new(8, "quartermaster", StatId.RepairReceived, 0.1f, new GearTrait(TraitId.SetSalvageRights, 0.2f, 0.1f)),
            new(9, "spectre", StatId.Vision, 0.08f, new GearTrait(TraitId.SetGhostNet, 0.15f)),
            new(10, "hammerfall", StatId.DamageVsStructure, 0.08f, new GearTrait(TraitId.SetHeavyRound, 5f, 1f)),
            // Prompt 8.
            new(11, "phoenix", StatId.RepairReceived, 0.1f, new GearTrait(TraitId.SetPhoenix, 0.1f, 8f)),
            new(12, "wolfpack", StatId.Count, 0f, new GearTrait(TraitId.SetPackFocus, 0.15f))
                { TwoPiece = new GearTrait(TraitId.SetPackHunt, 0.04f, 15f, 3f) },
            new(BulwarkBrand, "bulwark", StatId.Health, 0.1f, new GearTrait(TraitId.SetBulwarkPost, 20f)) { TowerOnly = true },
        };

        /// <summary>The brands a vehicle piece may roll (the first ones, before the tower brand).</summary>
        public static int VehicleBrandCount => BulwarkBrand - 1;

        /// <summary>What a whole loadout may add to each stat, by <see cref="StatId"/>: no loadout turns a vehicle into another.</summary>
        public static readonly float[] StatCap = BuildCaps();

        private static float[] BuildCaps()
        {
            var caps = new float[(int)StatId.Count];
            void Set(StatId id, float cap) => caps[(int)id] = cap;
            Set(StatId.Damage, 0.25f);
            Set(StatId.FireRate, 0.15f);
            Set(StatId.Health, 0.25f);
            Set(StatId.Speed, 0.15f);
            Set(StatId.Regen, 0.02f);
            Set(StatId.DamageTaken, 0.2f);
            Set(StatId.DamageVsLight, 0.25f);
            Set(StatId.DamageVsHeavy, 0.25f);
            Set(StatId.DamageVsAir, 0.25f);
            Set(StatId.DamageVsStructure, 0.3f);
            Set(StatId.Range, 0.12f);
            Set(StatId.Vision, 0.25f);
            Set(StatId.Spread, 0.3f);
            Set(StatId.ProjectileSpeed, 0.3f);
            Set(StatId.Magazine, 0.4f);
            Set(StatId.MagazineReload, 0.3f);
            for (var r = StatId.ResistKinetic; r <= StatId.ResistFragmentation; r++) Set(r, 0.3f);
            // Prompt 15 C.9: energy's resistance; penetration and armour in levels (a whole level at most).
            Set(StatId.ResistEnergy, 0.3f);
            Set(StatId.Penetration, 1f);
            Set(StatId.ArmourSide, 1f);
            Set(StatId.ArmourAll, 1f);
            Set(StatId.TurnRate, 0.3f);
            Set(StatId.TurretRate, 0.3f);
            Set(StatId.CaptureRate, 0.5f);
            Set(StatId.Cooldowns, 0.25f);
            Set(StatId.Splash, 0.3f);
            Set(StatId.SecondaryFireRate, 0.3f);
            Set(StatId.SalvoInterval, 0.35f);
            Set(StatId.ResistRocket, 0.3f);
            Set(StatId.ResistIndirect, 0.3f);
            Set(StatId.ResistMine, 0.6f);
            Set(StatId.ResistFrontal, 0.25f);
            Set(StatId.TransitSpeed, 0.25f);
            Set(StatId.StillVision, 0.25f);
            Set(StatId.Camouflage, 0.25f);
            Set(StatId.RegenDelay, 3f);
            Set(StatId.StatusDuration, 0.5f);
            Set(StatId.SpreadLong, 0.3f);
            Set(StatId.SpreadMoving, 0.35f);
            Set(StatId.BurnDamage, 0.25f);
            Set(StatId.SummonPower, 0.15f);
            Set(StatId.RepairReceived, 0.1f);
            Set(StatId.DamageFlank, 0.25f);
            Set(StatId.DamageVsDrone, 0.3f);
            Set(StatId.SpareMagazine, 1f);
            Set(StatId.LockRange, 0.25f);
            Set(StatId.LaserWarning, 8f);
            Set(StatId.ReverseSpeed, 0.5f);
            Set(StatId.ResistBlast, 0.3f);
            return caps;
        }

        private static readonly Dictionary<string, BaseTypeDef> BaseById = new();
        private static readonly Dictionary<TraitId, TraitDef> TraitById = new();
        private static readonly Dictionary<SpecialModule, ModuleDef> ModuleById = new();

        static GearCatalog()
        {
            foreach (var b in Bases) BaseById[b.Id] = b;
            foreach (var b in TowerBases) BaseById[b.Id] = b;
            foreach (var t in Traits) TraitById[t.Id] = t;
            // The tower-only lines (a vehicle trait in a tower pool keeps its vehicle entry here).
            foreach (var t in TowerTraits) TraitById.TryAdd(t.Id, t);
            foreach (var m in Modules) ModuleById[m.Module] = m;
        }

        public static BaseTypeDef Base(string id) => !string.IsNullOrEmpty(id) && BaseById.TryGetValue(id, out var b) ? b : null;

        public static TraitDef Trait(TraitId id) => TraitById.TryGetValue(id, out var t) ? t : null;

        public static TraitDef Trait(string key) => Trait(GearKeys.ParseTrait(key));

        public static ModuleDef Module(SpecialModule module) => ModuleById.TryGetValue(module, out var m) ? m : null;

        public static BrandDef Brand(int index) => index >= 1 && index <= Brands.Length ? Brands[index - 1] : null;

        public static SubDef Sub(StatId stat)
        {
            foreach (var s in Subs)
                if (s.Stat == stat) return s;
            return null;
        }

        public static IEnumerable<BaseTypeDef> BasesFor(GearSlot slot)
        {
            foreach (var b in Bases)
                if (b.Slot == slot) yield return b;
        }

        public static IEnumerable<TraitDef> TraitsFor(GearSlot slot)
        {
            foreach (var t in Traits)
                if (t.Slot == slot) yield return t;
        }

        public static BranchMask MaskOf(GearBranch branch) => (BranchMask)(1 << (int)branch);

        /// <summary>
        /// Base types retired or merged (prompt 8 I.8) and what an old piece of each becomes: the same
        /// slot, rarity and level, the replacement's lines.
        /// </summary>
        public static readonly IReadOnlyDictionary<string, string> Replaced = new Dictionary<string, string>
        {
            ["hypervelocity_charge"] = "airburst_rounds",
            ["turbocharger"] = "drivetrain",
            ["turret_drive"] = "drivetrain",
            ["mine_rollers"] = "underbelly_armor",
        };
    }
}
