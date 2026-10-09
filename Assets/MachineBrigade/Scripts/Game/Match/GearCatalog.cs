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

        /// <summary>Main stat multiplier (Monolith Plate 12/7, so 24 % health at Legendary; Hair Trigger 0.25 and Overtuned Engine 0.5, whose implicit is their slot's own main stat).</summary>
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

        /// <summary>
        /// Play-test 14 lane I (owner, 04/10: the player's smoke gear "bỏ luôn hoặc ẩn đi, tương lai có thể mang lại"): kept
        /// in the catalogue with its numbers, strings and Sim code, but never offered, rolled, worn or fired; an old save's
        /// piece is re-rolled on load (<see cref="Gear.Unhide"/>). Clear the flag to bring the line back.
        /// </summary>
        public bool Hidden { get; set; }
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

        /// <summary>
        /// Play-test 14 lane I (owner, 04/10: the player's smoke gear "bỏ luôn hoặc ẩn đi, tương lai có thể mang lại"): kept
        /// in the catalogue with its numbers, strings and Sim code, but never offered, rolled, worn or fired; an old save's
        /// piece is re-rolled on load (<see cref="Gear.Unhide"/>). Clear the flag to bring the line back.
        /// </summary>
        public bool Hidden { get; set; }

        public GearTrait At(Rarity rarity)
        {
            var v = rarity >= Rarity.Legendary ? Legendary : Epic;
            return new GearTrait(Id, v.Length > 0 ? v[0] : 0f, v.Length > 1 ? v[1] : 0f, v.Length > global::MachineBrigade.Sim.Content.SimTunables.Vehicles.TraitDef.AtLengthMin ? v[2] : 0f);
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

        /// <summary>
        /// Play-test 14 lane I (owner, 04/10: the player's smoke gear "bỏ luôn hoặc ẩn đi, tương lai có thể mang lại"): kept
        /// in the catalogue with its numbers, strings and Sim code, but never offered, rolled, worn or fired; an old save's
        /// piece is re-rolled on load (<see cref="Gear.Unhide"/>). Clear the flag to bring the line back.
        /// </summary>
        public bool Hidden { get; set; }
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
    /// brands after The Division 2's gear sets): 40 stat base types, 14 special modules, 45
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
            new("long_barrel", GearSlot.Weapon, StatId.Range, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LongBarrelTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LongBarrelTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LongBarrelTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LongBarrelTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LongBarrelTop5)),
            // Prompt 15 C.9: a level of penetration at the top (part levels below it), not a share against heavy vehicles.
            new("tungsten_penetrator", GearSlot.Weapon, StatId.Penetration, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TungstenPenetratorTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TungstenPenetratorTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TungstenPenetratorTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TungstenPenetratorTop4, 1f)),
            new("he_frag_filler", GearSlot.Weapon, StatId.Splash, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeFragFillerTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeFragFillerTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeFragFillerTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeFragFillerTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeFragFillerTop5)),
            new("proximity_fuze", GearSlot.Weapon, StatId.DamageVsAir, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ProximityFuzeTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ProximityFuzeTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ProximityFuzeTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ProximityFuzeTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ProximityFuzeTop5)),
            new("bunker_buster", GearSlot.Weapon, StatId.DamageVsStructure, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BunkerBusterTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BunkerBusterTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BunkerBusterTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BunkerBusterTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BunkerBusterTop5)),
            // Gear balance 04/10: Range 0.08/0.10/0.12 -> 0.07/0.09/0.10, Speed drawback -0.05/-0.06/-0.07 -> -0.03/-0.04/-0.05
            // (long_barrel = clean range, heavy_barrel = more range for some mobility).
            new("heavy_barrel", GearSlot.Weapon, StatId.Range, V(0f, 0f, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeavyBarrelTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeavyBarrelTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeavyBarrelTop5))
                { Penalty = StatId.Speed, PenaltyTop = V(0f, 0f, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeavyBarrelPenaltyTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeavyBarrelPenaltyTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeavyBarrelPenaltyTop5), MinRarity = global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HeavyBarrelMinRarity },
            // Prompt 8: rounds for flank shots, and airburst rounds against drones and what flies at it
            // (the Hyper-Velocity Charge's place: its extra shell speed was hard to feel).
            new("flanking_rounds", GearSlot.Weapon, StatId.DamageFlank, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FlankingRoundsTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FlankingRoundsTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FlankingRoundsTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FlankingRoundsTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FlankingRoundsTop5)),
            new("airburst_rounds", GearSlot.Weapon, StatId.DamageVsDrone, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AirburstRoundsTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AirburstRoundsTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AirburstRoundsTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AirburstRoundsTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AirburstRoundsTop5)),

            // Loader: main stat +fire rate.
            new("carousel_autoloader", GearSlot.Loader, StatId.MagazineReload, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CarouselAutoloaderTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CarouselAutoloaderTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CarouselAutoloaderTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CarouselAutoloaderTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CarouselAutoloaderTop5)),
            new("extended_ammo_rack", GearSlot.Loader, StatId.Magazine, V(0.1f, 0.15f, 0.2f, 0.25f, 0.3f)),
            new("belt_feed", GearSlot.Loader, StatId.SecondaryFireRate, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BeltFeedTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BeltFeedTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BeltFeedTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BeltFeedTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BeltFeedTop5)),
            new("salvo_rack", GearSlot.Loader, StatId.SalvoInterval, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SalvoRackTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SalvoRackTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SalvoRackTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SalvoRackTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SalvoRackTop5)),
            // Gear balance 04/10: FireRate 0.10/0.12/0.15 -> 0.08/0.10/0.12, Spread drawback -0.10/-0.12/-0.14 -> -0.08/-0.10/-0.12.
            // Gear targets 04/10 (owner): effective fire rate (the Loader's own main stat x MainScale + the implicit, top level)
            // Rare / Epic / Legendary 8 / 10 / 11 %: main 0.08 / 0.11 / 0.14 x 0.25 + implicit 0.06 / 0.0725 / 0.075 (was 0.16 / 0.21 / 0.26).
            new("hair_trigger", GearSlot.Loader, StatId.FireRate, V(0f, 0f, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HairTriggerTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HairTriggerTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HairTriggerTop5))
                { Penalty = StatId.Spread, PenaltyTop = V(0f, 0f, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HairTriggerPenaltyTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HairTriggerPenaltyTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HairTriggerPenaltyTop5), MinRarity = global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HairTriggerMinRarity, MainScale = global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HairTriggerMainScale },
            // Prompt 8: an empty launcher gets part of its magazine back at once, once a life.
            new("spare_magazine", GearSlot.Loader, StatId.SpareMagazine, V(0.4f, 0.55f, 0.7f, 0.85f, 1f)) { Flat = true },

            // Armour: main stat +health.
            new("composite_addon", GearSlot.Armor, StatId.ResistShapedCharge, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CompositeAddonTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CompositeAddonTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CompositeAddonTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CompositeAddonTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CompositeAddonTop5)),
            new("spall_liner", GearSlot.Armor, StatId.ResistHighExplosive, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpallLinerTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpallLinerTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpallLinerTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpallLinerTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpallLinerTop5)),
            // Prompt 15 C.9: a level of side and rear armour at the top.
            new("applique_steel", GearSlot.Armor, StatId.ArmourSide, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AppliqueSteelTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AppliqueSteelTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AppliqueSteelTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AppliqueSteelTop4, 1f)),
            new("fire_retardant_hull", GearSlot.Armor, StatId.ResistFire, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireRetardantHullTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireRetardantHullTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireRetardantHullTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireRetardantHullTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireRetardantHullTop5)),
            // Prompt 15 C.9: an aircraft's armoured cockpit tub: armour all round. Gear balance 04/10: 0.40-1.00 -> 0.25-0.65
            // (all faces, so lighter than the Applique Steel's side and rear level).
            new("armoured_tub", GearSlot.Armor, StatId.ArmourAll, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ArmouredTubTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ArmouredTubTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ArmouredTubTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ArmouredTubTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ArmouredTubTop5)),
            // Gear targets 04/10 (owner): Legendary health 24 % (was 0.14 x 1.8 = 25.2 %, over the 25 % cap): MainScale 1.8 -> 12/7.
            new("monolith_plate", GearSlot.Armor, StatId.Count, V(0f, 0f, 0f, 0f, 0f))
                { Penalty = StatId.Speed, PenaltyTop = V(0f, 0f, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MonolithPlatePenaltyTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MonolithPlatePenaltyTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MonolithPlatePenaltyTop5), MinRarity = global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MonolithPlateMinRarity, MainScale = global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MonolithPlateMainScale, NoSubs = true },
            // Gear balance 04/10 (new): a light counter to energy weapons, a resistance liner like the Spall Liner (main stat
            // health, not plating). It only cuts energy damage after the energy has gone past any shield, as before.
            new("energy_dissipation_liner", GearSlot.Armor, StatId.ResistEnergy, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.EnergyDissipationLinerTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.EnergyDissipationLinerTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.EnergyDissipationLinerTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.EnergyDissipationLinerTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.EnergyDissipationLinerTop5)),
            // Prompt 8: enemy missiles must come closer to lock on.
            new("radar_absorbent_coating", GearSlot.Armor, StatId.LockRange, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RadarAbsorbentCoatingTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RadarAbsorbentCoatingTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RadarAbsorbentCoatingTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RadarAbsorbentCoatingTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RadarAbsorbentCoatingTop5)),

            // Armour, plating base types: main stat less damage taken.
            new("frontal_wedge", GearSlot.Armor, StatId.ResistFrontal, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FrontalWedgeTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FrontalWedgeTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FrontalWedgeTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FrontalWedgeTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FrontalWedgeTop5)) { Plating = true },
            new("slat_cage", GearSlot.Armor, StatId.ResistRocket, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SlatCageTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SlatCageTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SlatCageTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SlatCageTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SlatCageTop5)) { Plating = true },
            new("overhead_screen", GearSlot.Armor, StatId.ResistIndirect, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OverheadScreenTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OverheadScreenTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OverheadScreenTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OverheadScreenTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OverheadScreenTop5)) { Plating = true },
            // The Mine Rollers renamed (prompt 8 I.8): blasts and mines, so it works in every battle.
            new("underbelly_armor", GearSlot.Armor, StatId.ResistBlast, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.UnderbellyArmorTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.UnderbellyArmorTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.UnderbellyArmorTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.UnderbellyArmorTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.UnderbellyArmorTop5)) { Plating = true },

            // Engine: main stat +speed.
            // The Turbocharger and the Turret Drive merged (prompt 8 I.8): hull and turret turn faster.
            new("drivetrain", GearSlot.Engine, StatId.TurnRate, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DrivetrainTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DrivetrainTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DrivetrainTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DrivetrainTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DrivetrainTop5))
                { Implicit2 = StatId.TurretRate, Top2 = V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DrivetrainTop2N1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DrivetrainTop2N2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DrivetrainTop2N3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DrivetrainTop2N4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DrivetrainTop2N5) },
            new("transit_gearbox", GearSlot.Engine, StatId.TransitSpeed, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TransitGearboxTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TransitGearboxTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TransitGearboxTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TransitGearboxTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TransitGearboxTop5)),
            // Gear balance 04/10: Speed 0.10/0.12/0.15 -> 0.08/0.10/0.12, Health drawback -0.04/-0.05/-0.06 -> -0.03/-0.04/-0.05.
            // Gear targets 04/10 (owner): effective speed (the Engine's own main stat x MainScale + the implicit, top level)
            // Rare / Epic / Legendary 8 / 10 / 12 %: main 0.05 / 0.065 / 0.08 x 0.5 + implicit 0.055 / 0.0675 / 0.08 (was 0.13 / 0.165 / 0.20).
            new("overtuned_engine", GearSlot.Engine, StatId.Speed, V(0f, 0f, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OvertunedEngineTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OvertunedEngineTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OvertunedEngineTop5))
                { Penalty = StatId.Health, PenaltyTop = V(0f, 0f, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OvertunedEnginePenaltyTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OvertunedEnginePenaltyTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OvertunedEnginePenaltyTop5), MinRarity = global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OvertunedEngineMinRarity, MainScale = global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.OvertunedEngineMainScale },
            // Prompt 8: faster in reverse, and it backs off nose-on from enemies that close in.
            new("reverse_gearbox", GearSlot.Engine, StatId.ReverseSpeed, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReverseGearboxTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReverseGearboxTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReverseGearboxTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReverseGearboxTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReverseGearboxTop5)),

            // Repair: main stat regeneration out of combat.
            new("toolbox", GearSlot.Repair, StatId.RegenDelay, V(1f, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ToolboxTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ToolboxTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ToolboxTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ToolboxTop5)),
            new("crew_drills", GearSlot.Repair, StatId.Cooldowns, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CrewDrillsTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CrewDrillsTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CrewDrillsTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CrewDrillsTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CrewDrillsTop5)),
            new("fire_extinguisher", GearSlot.Repair, StatId.StatusDuration, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireExtinguisherTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireExtinguisherTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireExtinguisherTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireExtinguisherTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireExtinguisherTop5)),
            // Gear balance 04/10 (new): more from support and repairers instead of self-repair (RepairReceived cap stays 0.10).
            new("field_service_interface", GearSlot.Repair, StatId.RepairReceived, V(0.02f, 0.03f, 0.04f, 0.06f, 0.08f)),

            // Optics: main stat +vision.
            new("laser_rangefinder", GearSlot.Optics, StatId.SpreadLong, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LaserRangefinderTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LaserRangefinderTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LaserRangefinderTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LaserRangefinderTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LaserRangefinderTop5)),
            new("gun_stabiliser", GearSlot.Optics, StatId.SpreadMoving, V(0.1f, 0.15f, 0.2f, 0.25f, 0.3f)),
            new("commanders_periscope", GearSlot.Optics, StatId.StillVision, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CommandersPeriscopeTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CommandersPeriscopeTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CommandersPeriscopeTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CommandersPeriscopeTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CommandersPeriscopeTop5)),
            new("camouflage_net", GearSlot.Optics, StatId.Camouflage, V(0.05f, 0.08f, 0.11f, 0.15f, 0.18f)),
            // Prompt 8 I.8: the capture rate stays, and a little more sight for the modes with no points.
            new("signal_relay", GearSlot.Optics, StatId.CaptureRate, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SignalRelayTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SignalRelayTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SignalRelayTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SignalRelayTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SignalRelayTop5))
                { Implicit2 = StatId.Vision, Top2 = V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SignalRelayTop2N1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SignalRelayTop2N2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SignalRelayTop2N3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SignalRelayTop2N4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SignalRelayTop2N5) },
            // Prompt 8: a smoke screen when an anti-tank missile locks on (every 20 s); the radius.
            // Play-test 14 lane I: hidden (the player's smoke gear waits; see BaseTypeDef.Hidden).
            new("laser_warning", GearSlot.Optics, StatId.LaserWarning, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LaserWarningTop1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LaserWarningTop2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LaserWarningTop3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LaserWarningTop4, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LaserWarningTop5)) { Flat = true, Hidden = true },
        };

        /// <summary>
        /// Special modules, Epic / Legendary, and what a vehicle needs for each. The fixed-effect ones
        /// (drone escort, uplink barrage, mine dispenser, EMP payload) are sized to the vehicle's price.
        /// </summary>
        public static readonly ModuleDef[] Modules =
        {
            // Prompt 15 C.9: reactive armour cuts shaped charges hard and nothing else (it was 12-18 % of everything).
            new(SpecialModule.ReactiveArmor, Ground, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReactiveArmorEpic, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReactiveArmorLegendary),
            new(SpecialModule.AutoRepair, Any, 0.012f, 0.018f),
            new(SpecialModule.VeteranCrew, Armed, 0.08f, 0.12f),
            // Play-test 14 lane I: hidden (the player's smoke gear waits; see ModuleDef.Hidden).
            new(SpecialModule.SmokeDischarger, Ground, 8f, 10f, 0f, 1f) { Hidden = true },
            // Prompt 29 L5: Trophy only for a vehicle with an APS mount (ApsCapability not None), the heat decoys only for
            // flares as charges (FlareCharges above 0); see VehicleFit.Hardware.
            new(SpecialModule.TrophyAps, Ground | VehicleNeed.ApsMount, 1f, 2f, 25f, 20f),
            new(SpecialModule.FlareDispenser, Flying | VehicleNeed.Flares, 3f, 4f, 25f, 18f),
            new(SpecialModule.DroneEscort, Any, 1f, 2f, 25f, 20f),
            new(SpecialModule.EmpPayload, Any, 2f, 3f, 10f, 14f),
            new(SpecialModule.MineDispenser, Ground, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MineDispenserEpic, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MineDispenserLegendary, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MineDispenserEpic2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MineDispenserLegendary2),
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
            new(TraitId.KillReload, GearSlot.Loader, Armed, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.KillReloadEpic1), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.KillReloadLegendary1)),
            new(TraitId.RapidResponse, GearSlot.Loader, Armed, V(1.4f, 18f), V(1.6f, 14f)),
            new(TraitId.OverpressureChamber, GearSlot.Loader, Armed, V(5f), V(4f)),
            new(TraitId.HotSwap, GearSlot.Loader, VehicleNeed.Magazine, V(0.25f), V(0.4f)),
            new(TraitId.SkywardPintle, GearSlot.Loader, VehicleNeed.SecondaryGun | Ground, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SkywardPintleEpic1), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SkywardPintleLegendary1)),
            new(TraitId.Vengeance, GearSlot.Loader, Armed, V(0.15f, 15f, 5f), V(0.2f, 15f, 5f)),
            // Armour and plating
            new(TraitId.AegisBarrier, GearSlot.Armor, Any, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AegisBarrierEpic1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AegisBarrierEpic2), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AegisBarrierLegendary1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AegisBarrierLegendary2)),
            new(TraitId.Unbreakable, GearSlot.Armor, Any, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.UnbreakableEpic1), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.UnbreakableLegendary1)),
            new(TraitId.GuardianLink, GearSlot.Armor, VehicleNeed.Heavy | Ground, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.GuardianLinkEpic1), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.GuardianLinkLegendary1)),
            new(TraitId.DarkCrown, GearSlot.Armor, Any, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DarkCrownEpic1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DarkCrownEpic2), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DarkCrownLegendary1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DarkCrownLegendary2)),
            new(TraitId.AdaptivePlating, GearSlot.Armor, Any, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AdaptivePlatingEpic1), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AdaptivePlatingLegendary1)),
            new(TraitId.ReactiveBlocks, GearSlot.Armor, Ground, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReactiveBlocksEpic1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReactiveBlocksEpic2), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReactiveBlocksLegendary1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ReactiveBlocksLegendary2)),
            new(TraitId.AblativeLayer, GearSlot.Armor, Any, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AblativeLayerEpic1), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AblativeLayerLegendary1)),
            new(TraitId.AngledGlacis, GearSlot.Armor, Ground, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AngledGlacisEpic1), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AngledGlacisLegendary1)),
            new(TraitId.SiegeAnchor, GearSlot.Armor, Ground, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SiegeAnchorEpic1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SiegeAnchorEpic2), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SiegeAnchorLegendary1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SiegeAnchorLegendary2)),
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
            new(TraitId.DamageControl, GearSlot.Repair, Any, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageControlEpic1), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageControlLegendary1)),
            // Optics
            new(TraitId.ThermalImager, GearSlot.Optics, Any, V(0.6f), V(1f)),
            new(TraitId.LaserDesignator, GearSlot.Optics, VehicleNeed.HitsGround, V(0.08f, 4f), V(0.12f, 6f)),
            new(TraitId.GhillieMode, GearSlot.Optics, Armed | Ground, V(0.25f, 4f), V(0.4f, 3f)),
            new(TraitId.CounterBatteryRadar, GearSlot.Optics, Any, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CounterBatteryRadarEpic1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CounterBatteryRadarEpic2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CounterBatteryRadarEpic3), V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CounterBatteryRadarLegendary1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CounterBatteryRadarLegendary2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CounterBatteryRadarLegendary3)),
            new(TraitId.EwJammer, GearSlot.Optics, Any, V(2f, 15f, 12f), V(3f, 12f, 16f)),
            // Widened (prompt 8 I.1): every gun whose rounds fly unguided leads a moving target, not the artillery alone.
            new(TraitId.FireControlComputer, GearSlot.Optics, VehicleNeed.Unguided, V(0.5f), V(0.75f)),
        };

        public static readonly SubDef[] Subs =
        {
            new(StatId.DamageVsLight, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsLightValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsLightValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsLightValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsLightValues4), new[] { GearSlot.Weapon, GearSlot.Loader, GearSlot.Optics }),
            new(StatId.DamageVsHeavy, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsHeavyValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsHeavyValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsHeavyValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsHeavyValues4), new[] { GearSlot.Weapon, GearSlot.Loader, GearSlot.Optics }),
            new(StatId.DamageVsAir, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsAirValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsAirValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsAirValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsAirValues4), new[] { GearSlot.Weapon, GearSlot.Loader, GearSlot.Optics }),
            new(StatId.DamageVsStructure, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsStructureValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsStructureValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsStructureValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageVsStructureValues4), new[] { GearSlot.Weapon, GearSlot.Loader }),
            new(StatId.FireRate, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireRateValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireRateValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireRateValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.FireRateValues4), new[] { GearSlot.Weapon }),
            new(StatId.Damage, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.DamageValues4), new[] { GearSlot.Loader, GearSlot.Optics }),
            new(StatId.Range, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RangeValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RangeValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RangeValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RangeValues4), new[] { GearSlot.Weapon, GearSlot.Optics }),
            new(StatId.Vision, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.VisionValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.VisionValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.VisionValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.VisionValues4), new[] { GearSlot.Optics, GearSlot.Engine }),
            new(StatId.Spread, V(0.04f, 0.06f, 0.08f, 0.1f), new[] { GearSlot.Weapon, GearSlot.Optics }),
            new(StatId.ProjectileSpeed, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ProjectileSpeedValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ProjectileSpeedValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ProjectileSpeedValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ProjectileSpeedValues4), new[] { GearSlot.Weapon, GearSlot.Loader }),
            new(StatId.Magazine, V(0.05f, 0.08f, 0.1f, 0.12f), new[] { GearSlot.Loader }),
            new(StatId.MagazineReload, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MagazineReloadValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MagazineReloadValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MagazineReloadValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.MagazineReloadValues4), new[] { GearSlot.Loader, GearSlot.Repair }),
            new(StatId.Health, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HealthValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HealthValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HealthValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HealthValues4), new[] { GearSlot.Armor, GearSlot.Repair, GearSlot.Engine }),
            new(StatId.ResistKinetic, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistKineticValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistKineticValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistKineticValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistKineticValues4), new[] { GearSlot.Armor }, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistKineticWeight),
            new(StatId.ResistShapedCharge, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistShapedChargeValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistShapedChargeValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistShapedChargeValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistShapedChargeValues4), new[] { GearSlot.Armor }, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistShapedChargeWeight),
            new(StatId.ResistHighExplosive, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistHighExplosiveValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistHighExplosiveValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistHighExplosiveValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistHighExplosiveValues4), new[] { GearSlot.Armor }, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistHighExplosiveWeight),
            new(StatId.ResistFire, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistFireValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistFireValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistFireValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistFireValues4), new[] { GearSlot.Armor }, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistFireWeight),
            new(StatId.ResistFragmentation, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistFragmentationValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistFragmentationValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistFragmentationValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistFragmentationValues4), new[] { GearSlot.Armor }, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.ResistFragmentationWeight),
            new(StatId.Speed, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpeedValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpeedValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpeedValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpeedValues4), new[] { GearSlot.Engine, GearSlot.Armor }),
            new(StatId.TurretRate, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TurretRateValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TurretRateValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TurretRateValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.TurretRateValues4), new[] { GearSlot.Engine, GearSlot.Optics }),
            new(StatId.CaptureRate, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CaptureRateValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CaptureRateValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CaptureRateValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CaptureRateValues4), new[] { GearSlot.Engine, GearSlot.Optics }),
            new(StatId.Cooldowns, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CooldownsValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CooldownsValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CooldownsValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.CooldownsValues4), new[] { GearSlot.Repair, GearSlot.Optics }),
            new(StatId.Regen, V(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RegenValues1, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RegenValues2, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RegenValues3, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.RegenValues4), new[] { GearSlot.Repair, GearSlot.Armor }),
        };

        /// <summary>The brand index of Bulwark Engineering (tower pieces only).</summary>
        public const int BulwarkBrand = 13;

        /// <summary>Gear balance 04/10: two-piece lines vulcan 0.25 -> 0.15, hivemind 0.15 -> 0.10, quartermaster and phoenix 0.10 -> 0.06 (four-piece behaviours unchanged).</summary>
        public static readonly BrandDef[] Brands =
        {
            new(1, "ironclad", StatId.Health, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.IroncladValue, new GearTrait(TraitId.SetBulwark, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.IroncladFourPieceSetBulwark)),
            new(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.KestrelIndex, "kestrel", StatId.Speed, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.KestrelValue, new GearTrait(TraitId.SetHitAndRun, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.KestrelFourPieceASetHitAndRun, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.KestrelFourPieceBSetHitAndRun)),
            new(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.VulcanIndex, "vulcan", StatId.BurnDamage, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.VulcanValue, new GearTrait(TraitId.SetFirestorm, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.VulcanFourPieceASetFirestorm, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.VulcanFourPieceBSetFirestorm)),
            new(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LongbowIndex, "longbow", StatId.Range, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LongbowValue, new GearTrait(TraitId.SetDeepStrike, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.LongbowFourPieceSetDeepStrike)),
            new(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AegisIndex, "aegis", StatId.DamageTaken, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AegisValue, new GearTrait(TraitId.SetSharedShield, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AegisFourPieceASetSharedShield, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AegisFourPieceBSetSharedShield, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.AegisFourPieceCSetSharedShield)),
            new(6, "stormfront", StatId.ResistFragmentation, 0.1f, new GearTrait(TraitId.SetStrafingRun, 4f, 30f)),
            new(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HivemindIndex, "hivemind", StatId.SummonPower, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HivemindValue, new GearTrait(TraitId.SetSwarm, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HivemindFourPieceSetSwarm)),
            new(8, "quartermaster", StatId.RepairReceived, 0.06f, new GearTrait(TraitId.SetSalvageRights, 0.2f, 0.1f)),
            new(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpectreIndex, "spectre", StatId.Vision, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpectreValue, new GearTrait(TraitId.SetGhostNet, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.SpectreFourPieceSetGhostNet)),
            new(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HammerfallIndex, "hammerfall", StatId.DamageVsStructure, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HammerfallValue, new GearTrait(TraitId.SetHeavyRound, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.HammerfallFourPieceASetHeavyRound, 1f)),
            // Prompt 8.
            new(11, "phoenix", StatId.RepairReceived, 0.06f, new GearTrait(TraitId.SetPhoenix, 0.1f, 8f)),
            new(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.WolfpackIndex, "wolfpack", StatId.Count, 0f, new GearTrait(TraitId.SetPackFocus, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.WolfpackFourPieceSetPackFocus))
                { TwoPiece = new GearTrait(TraitId.SetPackHunt, 0.04f, 15f, 3f) },
            new(BulwarkBrand, "bulwark", StatId.Health, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BulwarkValue, new GearTrait(TraitId.SetBulwarkPost, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BulwarkFourPieceSetBulwarkPost)) { TowerOnly = true },
        };

        /// <summary>The brands a vehicle piece may roll (the first ones, before the tower brand).</summary>
        public static int VehicleBrandCount => BulwarkBrand - 1;

        /// <summary>What a whole loadout may add to each stat, by <see cref="StatId"/>: no loadout turns a vehicle into another.</summary>
        public static readonly float[] StatCap = BuildCaps();

        private static float[] BuildCaps()
        {
            var caps = new float[(int)StatId.Count];
            void Set(StatId id, float cap) => caps[(int)id] = cap;
            Set(StatId.Damage, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.FireRate, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap2);
            Set(StatId.Health, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.Speed, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap2);
            Set(StatId.Regen, 0.02f);
            Set(StatId.DamageTaken, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap4);
            Set(StatId.DamageVsLight, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.DamageVsHeavy, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.DamageVsAir, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.DamageVsStructure, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap5);
            Set(StatId.Range, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap6);
            Set(StatId.Vision, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.Spread, 0.3f);
            Set(StatId.ProjectileSpeed, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap5);
            Set(StatId.Magazine, 0.4f);
            Set(StatId.MagazineReload, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap5);
            for (var r = StatId.ResistKinetic; r <= StatId.ResistFragmentation; r++) Set(r, 0.3f);
            // Prompt 15 C.9: energy's resistance; penetration and armour in levels (a whole level at most).
            Set(StatId.ResistEnergy, 0.3f);
            Set(StatId.Penetration, 1f);
            Set(StatId.ArmourSide, 1f);
            Set(StatId.ArmourAll, 1f);
            Set(StatId.TurnRate, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap5);
            Set(StatId.TurretRate, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap5);
            Set(StatId.CaptureRate, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap8);
            Set(StatId.Cooldowns, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.Splash, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap5);
            Set(StatId.SecondaryFireRate, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap5);
            Set(StatId.SalvoInterval, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap9);
            Set(StatId.ResistRocket, 0.3f);
            Set(StatId.ResistIndirect, 0.3f);
            Set(StatId.ResistMine, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap10);
            Set(StatId.ResistFrontal, 0.25f);
            Set(StatId.TransitSpeed, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.StillVision, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.Camouflage, 0.25f);
            Set(StatId.RegenDelay, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap11);
            Set(StatId.StatusDuration, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap8);
            Set(StatId.SpreadLong, 0.3f);
            Set(StatId.SpreadMoving, 0.35f);
            Set(StatId.BurnDamage, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.SummonPower, 0.15f);
            Set(StatId.RepairReceived, 0.1f);
            Set(StatId.DamageFlank, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.DamageVsDrone, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap5);
            Set(StatId.SpareMagazine, 1f);
            Set(StatId.LockRange, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap);
            Set(StatId.LaserWarning, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap13);
            Set(StatId.ReverseSpeed, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap8);
            Set(StatId.ResistBlast, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.GearCatalog.BuildCapsCap5);
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

        /// <summary>The base types a piece of this slot may be given (hidden ones left out).</summary>
        public static IEnumerable<BaseTypeDef> BasesFor(GearSlot slot)
        {
            foreach (var b in Bases)
                if (b.Slot == slot && !b.Hidden) yield return b;
        }

        /// <summary>The traits a piece of this slot may roll (hidden ones left out).</summary>
        public static IEnumerable<TraitDef> TraitsFor(GearSlot slot)
        {
            foreach (var t in Traits)
                if (t.Slot == slot && !t.Hidden) yield return t;
        }

        /// <summary>The special modules a piece may be given (hidden ones left out; <see cref="Modules"/> keeps them all).</summary>
        public static IEnumerable<ModuleDef> ShownModules
        {
            get
            {
                foreach (var m in Modules)
                    if (!m.Hidden) yield return m;
            }
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
