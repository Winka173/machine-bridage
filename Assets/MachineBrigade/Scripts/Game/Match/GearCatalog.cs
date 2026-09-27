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
    /// line, which grows with level like the main stat. Trade-offs drop at Rare and up only and
    /// carry a fixed drawback.
    /// </summary>
    public sealed class BaseTypeDef
    {
        public BaseTypeDef(string id, GearSlot slot, BranchMask branches, StatId implicitStat, float[] top)
        {
            Id = id;
            Slot = slot;
            Branches = branches;
            Implicit = implicitStat;
            Top = top;
        }

        /// <summary>Its id: the save's key, the strings' key and the picture's name (Resources/UI/Gear/&lt;id&gt;.png).</summary>
        public string Id { get; }

        public GearSlot Slot { get; }
        public BranchMask Branches { get; }

        /// <summary>The implicit line's stat (<see cref="StatId.Count"/>: none).</summary>
        public StatId Implicit { get; }

        /// <summary>The implicit line at each rarity's top level, Common to Legendary.</summary>
        public float[] Top { get; }

        /// <summary>A trade-off's drawback and its value by rarity (negative), fixed at every level.</summary>
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

        /// <summary>A hidden extra from a rarity up (Mine Rollers sweep a mine every 30 s from Epic).</summary>
        public TraitId Extra { get; set; }

        public int ExtraFrom { get; set; } = 99;

        public bool TradeOff => Penalty != StatId.Count;
    }

    /// <summary>A unique trait: the slot whose pool it is in, the branches it suits, and its numbers at Epic and Legendary.</summary>
    public sealed class TraitDef
    {
        public TraitDef(TraitId id, GearSlot slot, BranchMask branches, float[] epic, float[] legendary)
        {
            Id = id;
            Slot = slot;
            Branches = branches;
            Epic = epic;
            Legendary = legendary;
        }

        public TraitId Id { get; }
        public GearSlot Slot { get; }
        public BranchMask Branches { get; }
        public float[] Epic { get; }
        public float[] Legendary { get; }
        public string Key => GearKeys.Trait(Id);

        public GearTrait At(Rarity rarity)
        {
            var v = rarity >= Rarity.Legendary ? Legendary : Epic;
            return new GearTrait(Id, v.Length > 0 ? v[0] : 0f, v.Length > 1 ? v[1] : 0f, v.Length > 2 ? v[2] : 0f);
        }
    }

    /// <summary>A special module: its numbers at Epic and Legendary (power, power 2) and the branches it suits.</summary>
    public sealed class ModuleDef
    {
        public ModuleDef(SpecialModule module, BranchMask branches, float epic, float legendary, float epic2 = 0f, float legendary2 = 0f)
        {
            Module = module;
            Branches = branches;
            Epic = epic;
            Legendary = legendary;
            Epic2 = epic2;
            Legendary2 = legendary2;
        }

        public SpecialModule Module { get; }
        public BranchMask Branches { get; }
        public float Epic { get; }
        public float Legendary { get; }
        public float Epic2 { get; }
        public float Legendary2 { get; }
        public string Key => GearKeys.Module(Module);
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

    /// <summary>A set brand: its two-piece stat bonus and four-piece behaviour.</summary>
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

        /// <summary>1 to 10 (0 on a piece: no brand).</summary>
        public int Index { get; }

        public string Id { get; }
        public StatId Stat { get; }
        public float Value { get; }
        public GearTrait FourPiece { get; }
    }

    /// <summary>
    /// The equipment catalogue (Docs research: base types after Path of Exile and Borderlands,
    /// sub-stats after The Division 2, unique traits after Archero, Warframe and Clash of Clans,
    /// brands after The Division 2's gear sets): 34 stat base types, 14 special modules, 42
    /// traits and 10 brands. Numbers are at the top level; level 1 has 40 % of a main stat or
    /// implicit line.
    /// </summary>
    public static class GearCatalog
    {
        private const BranchMask Arm = BranchMask.Armor, Lgt = BranchMask.Light, Art = BranchMask.Artillery, Air = BranchMask.Air, All = BranchMask.All;
        private static readonly float[] None5 = { 0f, 0f, 0f, 0f, 0f };

        private static float[] V(params float[] v) => v;

        public static readonly BaseTypeDef[] Bases =
        {
            // Weapon: main stat +damage.
            new("long_barrel", GearSlot.Weapon, Arm | Lgt | Art, StatId.Range, V(0.02f, 0.03f, 0.04f, 0.06f, 0.08f)),
            new("tungsten_penetrator", GearSlot.Weapon, Arm | Lgt | Air, StatId.DamageVsHeavy, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f)),
            new("he_frag_filler", GearSlot.Weapon, Art | Lgt | Air, StatId.Splash, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("proximity_fuze", GearSlot.Weapon, Lgt | Arm | Air, StatId.DamageVsAir, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("bunker_buster", GearSlot.Weapon, Art | Arm | Air, StatId.DamageVsStructure, V(0.06f, 0.09f, 0.13f, 0.18f, 0.24f)),
            new("hypervelocity_charge", GearSlot.Weapon, Arm | Lgt, StatId.ProjectileSpeed, V(0.08f, 0.12f, 0.16f, 0.2f, 0.25f)),
            new("heavy_barrel", GearSlot.Weapon, Arm | Art, StatId.Range, V(0f, 0f, 0.08f, 0.1f, 0.12f))
                { Penalty = StatId.Speed, PenaltyTop = V(0f, 0f, -0.1f, -0.08f, -0.06f), MinRarity = 2 },

            // Loader: main stat +fire rate.
            new("carousel_autoloader", GearSlot.Loader, Arm | Art | Air, StatId.MagazineReload, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("extended_ammo_rack", GearSlot.Loader, Art | Air | Lgt, StatId.Magazine, V(0.1f, 0.15f, 0.2f, 0.25f, 0.3f)),
            new("belt_feed", GearSlot.Loader, Arm | Lgt | Air, StatId.SecondaryFireRate, V(0.08f, 0.12f, 0.16f, 0.2f, 0.25f)),
            new("salvo_rack", GearSlot.Loader, Art | Air, StatId.SalvoInterval, V(0.1f, 0.15f, 0.2f, 0.25f, 0.3f)),
            new("hair_trigger", GearSlot.Loader, Arm | Lgt | Air, StatId.FireRate, V(0f, 0f, 0.1f, 0.12f, 0.15f))
                { Penalty = StatId.Spread, PenaltyTop = V(0f, 0f, -0.15f, -0.12f, -0.1f), MinRarity = 2 },

            // Armour: main stat +health.
            new("composite_addon", GearSlot.Armor, Arm | Lgt, StatId.ResistArmorPiercing, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f)),
            new("spall_liner", GearSlot.Armor, Arm | Lgt | Art, StatId.ResistHighExplosive, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f)),
            new("applique_steel", GearSlot.Armor, Lgt | Art, StatId.ResistKinetic, V(0.05f, 0.08f, 0.11f, 0.15f, 0.18f)),
            new("fire_retardant_hull", GearSlot.Armor, Arm | Lgt | Art, StatId.ResistFire, V(0.08f, 0.12f, 0.16f, 0.2f, 0.25f)),
            new("armoured_tub", GearSlot.Armor, Air, StatId.ResistFlak, V(0.06f, 0.09f, 0.13f, 0.17f, 0.22f)),
            new("monolith_plate", GearSlot.Armor, Arm, StatId.Count, None5)
                { Penalty = StatId.Speed, PenaltyTop = V(0f, 0f, -0.06f, -0.06f, -0.06f), MinRarity = 2, MainScale = 1.8f, NoSubs = true },

            // Armour, plating base types: main stat less damage taken.
            new("frontal_wedge", GearSlot.Armor, Arm, StatId.ResistFrontal, V(0.05f, 0.08f, 0.11f, 0.15f, 0.18f)) { Plating = true },
            new("slat_cage", GearSlot.Armor, Arm | Lgt | Art, StatId.ResistRocket, V(0.06f, 0.09f, 0.13f, 0.17f, 0.22f)) { Plating = true },
            new("overhead_screen", GearSlot.Armor, Arm | Lgt | Art, StatId.ResistIndirect, V(0.06f, 0.09f, 0.13f, 0.17f, 0.22f)) { Plating = true },
            new("mine_rollers", GearSlot.Armor, Arm | Lgt, StatId.ResistMine, V(0.15f, 0.25f, 0.35f, 0.45f, 0.6f))
                { Plating = true, Extra = TraitId.MineSweep, ExtraFrom = 3 },

            // Engine: main stat +speed.
            new("turbocharger", GearSlot.Engine, All, StatId.TurnRate, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("turret_drive", GearSlot.Engine, Arm | Lgt, StatId.TurretRate, V(0.08f, 0.12f, 0.16f, 0.2f, 0.25f)),
            new("transit_gearbox", GearSlot.Engine, All, StatId.TransitSpeed, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("overtuned_engine", GearSlot.Engine, Lgt | Air, StatId.Speed, V(0f, 0f, 0.1f, 0.12f, 0.15f))
                { Penalty = StatId.Health, PenaltyTop = V(0f, 0f, -0.08f, -0.06f, -0.05f), MinRarity = 2 },

            // Repair: main stat regeneration out of combat.
            new("toolbox", GearSlot.Repair, All, StatId.RegenDelay, V(1f, 1.5f, 2f, 2.5f, 3f)),
            new("crew_drills", GearSlot.Repair, All, StatId.Cooldowns, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f)),
            new("fire_extinguisher", GearSlot.Repair, Arm | Lgt | Art, StatId.StatusDuration, V(0.1f, 0.18f, 0.26f, 0.34f, 0.42f)),

            // Optics: main stat +vision.
            new("laser_rangefinder", GearSlot.Optics, Arm | Lgt | Art, StatId.SpreadLong, V(0.08f, 0.12f, 0.16f, 0.2f, 0.25f)),
            new("gun_stabiliser", GearSlot.Optics, Arm | Lgt, StatId.SpreadMoving, V(0.1f, 0.15f, 0.2f, 0.25f, 0.3f)),
            new("commanders_periscope", GearSlot.Optics, All, StatId.StillVision, V(0.05f, 0.08f, 0.12f, 0.16f, 0.2f)),
            new("camouflage_net", GearSlot.Optics, Arm | Lgt | Art, StatId.Camouflage, V(0.05f, 0.08f, 0.11f, 0.15f, 0.18f)),
            new("signal_relay", GearSlot.Optics, Lgt | Arm, StatId.CaptureRate, V(0.1f, 0.15f, 0.2f, 0.25f, 0.3f)),
        };

        /// <summary>
        /// Special modules, Epic / Legendary. Numbers are the research's, and Legendary traits
        /// stay near +12 % strength in their niche (docs 2.3).
        /// </summary>
        public static readonly ModuleDef[] Modules =
        {
            new(SpecialModule.ReactiveArmor, All, 0.12f, 0.18f),
            new(SpecialModule.AutoRepair, All, 0.012f, 0.018f),
            new(SpecialModule.VeteranCrew, All, 0.08f, 0.12f),
            new(SpecialModule.SmokeDischarger, Arm | Lgt | Art, 8f, 10f, 0f, 1f),
            new(SpecialModule.TrophyAps, Arm | Lgt, 1f, 2f, 25f, 20f),
            new(SpecialModule.FlareDispenser, Air, 3f, 4f, 25f, 18f),
            new(SpecialModule.DroneEscort, Arm | Lgt | Art, 1f, 2f, 25f, 20f),
            new(SpecialModule.EmpPayload, Lgt | Air, 2f, 3f, 10f, 14f),
            new(SpecialModule.MineDispenser, Lgt, 2f, 3f, 20f, 15f),
            new(SpecialModule.WarProfiteer, All, 0.5f, 0.8f),
            new(SpecialModule.RallyHorn, Arm | Lgt, 0.06f, 0.1f, 12f, 15f),
            new(SpecialModule.AegisDome, Arm | Lgt, 2f, 3f),
            new(SpecialModule.DecoyLauncher, Arm | Lgt | Art, 4f, 6f, 35f, 25f),
            new(SpecialModule.UplinkBarrage, Arm | Lgt, 3f, 5f, 45f, 35f),
        };

        public static readonly TraitDef[] Traits =
        {
            // Weapon
            new(TraitId.TwinFeed, GearSlot.Weapon, All, V(0.08f), V(0.12f)),
            new(TraitId.IncendiaryRounds, GearSlot.Weapon, Arm | Lgt | Air, V(0.1f), V(0.14f)),
            new(TraitId.RicochetShells, GearSlot.Weapon, Arm | Lgt, V(0.35f, 8f), V(0.5f, 10f)),
            new(TraitId.ClusterWarhead, GearSlot.Weapon, Art | Air, V(4f), V(6f)),
            new(TraitId.ShredderRounds, GearSlot.Weapon, Arm | Lgt | Air, V(0.03f), V(0.04f)),
            new(TraitId.OpeningSalvo, GearSlot.Weapon, Arm | Lgt | Art, V(0.5f), V(0.8f)),
            new(TraitId.MomentumGun, GearSlot.Weapon, Arm | Lgt | Air, V(0.03f), V(0.04f)),
            new(TraitId.Executioner, GearSlot.Weapon, All, V(0.4f), V(0.6f)),
            new(TraitId.TandemWarhead, GearSlot.Weapon, Lgt | Arm | Air, V(0.1f), V(0.15f)),
            new(TraitId.SuppressionRounds, GearSlot.Weapon, Lgt | Arm | Air, V(0.15f), V(0.25f)),
            // Loader
            new(TraitId.HullDownCrew, GearSlot.Loader, Arm | Lgt | Art, V(0.1f), V(0.15f)),
            new(TraitId.KillReload, GearSlot.Loader, Arm | Lgt | Air, V(0.25f), V(0.4f)),
            new(TraitId.RapidResponse, GearSlot.Loader, All, V(1.4f, 18f), V(1.6f, 14f)),
            new(TraitId.OverpressureChamber, GearSlot.Loader, Arm | Art | Lgt, V(5f), V(4f)),
            new(TraitId.HotSwap, GearSlot.Loader, Art | Lgt, V(0.25f), V(0.4f)),
            new(TraitId.SkywardPintle, GearSlot.Loader, Arm | Lgt | Art, V(0.6f), V(0.8f)),
            // Armour and plating
            new(TraitId.AegisBarrier, GearSlot.Armor, Arm | Lgt | Air, V(0.1f, 20f), V(0.15f, 16f)),
            new(TraitId.Unbreakable, GearSlot.Armor, Arm | Lgt, V(1.5f), V(2.5f)),
            new(TraitId.GuardianLink, GearSlot.Armor, Arm, V(0.15f), V(0.25f)),
            new(TraitId.DarkCrown, GearSlot.Armor, Arm | Lgt, V(0.03f, 0.02f), V(0.04f, 0.03f)),
            new(TraitId.AdaptivePlating, GearSlot.Armor, All, V(0.05f), V(0.06f)),
            new(TraitId.ReactiveBlocks, GearSlot.Armor, Arm | Lgt, V(3f, 20f), V(4f, 15f)),
            new(TraitId.AblativeLayer, GearSlot.Armor, All, V(0.2f), V(0.3f)),
            new(TraitId.AngledGlacis, GearSlot.Armor, Arm, V(6f), V(5f)),
            new(TraitId.SiegeAnchor, GearSlot.Armor, Arm | Art, V(0.15f, 0.08f), V(0.2f, 0.12f)),
            // Engine
            new(TraitId.NitroDash, GearSlot.Engine, Arm | Lgt, V(1.6f, 25f), V(1.8f, 18f)),
            new(TraitId.ShootAndScoot, GearSlot.Engine, Arm | Lgt | Art, V(0.4f, 0.15f), V(0.6f, 0.25f)),
            new(TraitId.RapidDeployment, GearSlot.Engine, All, V(10f), V(15f)),
            new(TraitId.VolatileFuelTanks, GearSlot.Engine, Lgt | Arm, V(0.3f, 8f), V(0.45f, 10f)),
            new(TraitId.AfterburnerReserve, GearSlot.Engine, Air, V(0.5f), V(0.7f)),
            // Repair
            new(TraitId.FieldMechanics, GearSlot.Repair, Lgt | Arm, V(0.006f, 12f), V(0.01f, 15f)),
            new(TraitId.EmergencyRepairKit, GearSlot.Repair, All, V(0.2f), V(0.3f)),
            new(TraitId.CombatWelder, GearSlot.Repair, Arm, V(0.4f), V(0.6f)),
            new(TraitId.SalvageTeam, GearSlot.Repair, Arm | Lgt | Air, V(0.08f), V(0.12f)),
            new(TraitId.AmmoCarrier, GearSlot.Repair, Lgt, V(0.3f, 12f), V(0.5f, 16f)),
            new(TraitId.DamageControl, GearSlot.Repair, All, V(15f), V(10f)),
            // Optics
            new(TraitId.ThermalImager, GearSlot.Optics, Arm | Lgt | Air, V(0.6f), V(1f)),
            new(TraitId.LaserDesignator, GearSlot.Optics, Lgt | Air | Arm, V(0.08f, 4f), V(0.12f, 6f)),
            new(TraitId.GhillieMode, GearSlot.Optics, Lgt | Arm | Art, V(0.25f, 4f), V(0.4f, 3f)),
            new(TraitId.CounterBatteryRadar, GearSlot.Optics, Art | Lgt, V(0.15f, 80f, 5f), V(0.25f, 100f, 8f)),
            new(TraitId.EwJammer, GearSlot.Optics, Lgt | Air, V(2f, 15f, 12f), V(3f, 12f, 16f)),
            new(TraitId.FireControlComputer, GearSlot.Optics, Art, V(0.5f), V(0.75f)),
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
            new(StatId.ResistArmorPiercing, V(0.03f, 0.04f, 0.06f, 0.08f), new[] { GearSlot.Armor }, 0.2f),
            new(StatId.ResistHighExplosive, V(0.03f, 0.04f, 0.06f, 0.08f), new[] { GearSlot.Armor }, 0.2f),
            new(StatId.ResistFire, V(0.03f, 0.04f, 0.06f, 0.08f), new[] { GearSlot.Armor }, 0.2f),
            new(StatId.ResistFlak, V(0.03f, 0.04f, 0.06f, 0.08f), new[] { GearSlot.Armor }, 0.2f),
            new(StatId.Speed, V(0.015f, 0.02f, 0.03f, 0.04f), new[] { GearSlot.Engine, GearSlot.Armor }),
            new(StatId.TurretRate, V(0.05f, 0.08f, 0.1f, 0.12f), new[] { GearSlot.Engine, GearSlot.Optics }),
            new(StatId.CaptureRate, V(0.05f, 0.08f, 0.1f, 0.12f), new[] { GearSlot.Engine, GearSlot.Optics }),
            new(StatId.Cooldowns, V(0.03f, 0.05f, 0.07f, 0.09f), new[] { GearSlot.Repair, GearSlot.Optics }),
            new(StatId.Regen, V(0.001f, 0.0015f, 0.002f, 0.0025f), new[] { GearSlot.Repair, GearSlot.Armor }),
        };

        public static readonly BrandDef[] Brands =
        {
            new(1, "ironclad", StatId.Health, 0.06f, new GearTrait(TraitId.SetBulwark, 0.15f)),
            new(2, "kestrel", StatId.Speed, 0.05f, new GearTrait(TraitId.SetHitAndRun, 0.2f, 0.5f)),
            new(3, "vulcan", StatId.BurnDamage, 0.25f, new GearTrait(TraitId.SetFirestorm, 0.1f, 6f)),
            new(4, "longbow", StatId.Range, 0.05f, new GearTrait(TraitId.SetDeepStrike, 0.15f)),
            new(5, "aegis", StatId.DamageTaken, 0.05f, new GearTrait(TraitId.SetSharedShield, 0.12f, 25f, 12f)),
            new(6, "stormfront", StatId.ResistFlak, 0.1f, new GearTrait(TraitId.SetStrafingRun, 4f, 30f)),
            new(7, "hivemind", StatId.SummonPower, 0.15f, new GearTrait(TraitId.SetSwarm, 10f)),
            new(8, "quartermaster", StatId.RepairReceived, 0.1f, new GearTrait(TraitId.SetSalvageRights, 0.2f, 0.1f)),
            new(9, "spectre", StatId.Vision, 0.08f, new GearTrait(TraitId.SetGhostNet, 0.15f)),
            new(10, "hammerfall", StatId.DamageVsStructure, 0.08f, new GearTrait(TraitId.SetHeavyRound, 5f, 1f)),
        };

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
            for (var r = StatId.ResistKinetic; r <= StatId.ResistFlak; r++) Set(r, 0.3f);
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
            return caps;
        }

        private static readonly Dictionary<string, BaseTypeDef> BaseById = new();
        private static readonly Dictionary<TraitId, TraitDef> TraitById = new();
        private static readonly Dictionary<SpecialModule, ModuleDef> ModuleById = new();

        static GearCatalog()
        {
            foreach (var b in Bases) BaseById[b.Id] = b;
            foreach (var t in Traits) TraitById[t.Id] = t;
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
    }
}
