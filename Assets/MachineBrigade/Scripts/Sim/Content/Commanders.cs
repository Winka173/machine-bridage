#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 22 F.2 and F.3: the fourteen commanders of the player's side and the eight enemy generals' passives,
    /// as the spec lists them. The numbers are the starting point the balance sweep tunes (DECISIONS 22F). The old
    /// doctrines' edges live here since DECISIONS 23D: Crown has the armoured one, Hawk the air one, Longshot the
    /// artillery one, Rush the blitz one and Ledger the logistics one, merged where the commander had the same bonus.
    /// </summary>
    public static class Commanders
    {
        /// <summary>The commander a new or old save starts with, and the one a locked choice falls back to.</summary>
        public const string Default = "kade";

        private static CommanderLine L(StatId stat, float value, CommanderReach reach) => new(stat, value, reach);

        private static CommanderPrice P(PriceReach reach, float scale) => new(reach, scale);

        private static CommanderDef Combat(string id, string portrait, string unlock, DeckStyle style, params CommanderLine[] lines) =>
            new() { Id = id, Family = CommanderFamily.Combat, Portrait = portrait, Unlock = unlock, Style = style, Lines = lines };

        private static CommanderDef Econ(string id, string unlock, DeckStyle style, params CommanderLine[] lines) =>
            new() { Id = id, Family = CommanderFamily.Economy, Portrait = id, Unlock = unlock, Style = style, Lines = lines };

        private static CommanderDef Gen(string general, params CommanderLine[] lines) =>
            new() { Id = "gen." + general, Family = CommanderFamily.General, Portrait = general, Unlock = "", General = general, Lines = lines };

        /// <summary>The player's commanders, in the picker's order (combat, then economy).</summary>
        public static readonly IReadOnlyList<CommanderDef> All = new[]
        {
            // ------------------------------------------------------------ combat
            Combat("kade", "khai", "c1", DeckStyle.Balanced,
                L(StatId.Damage, 0.05f, CommanderReach.Army), L(StatId.Health, 0.05f, CommanderReach.Army)),
            new CommanderDef
            {
                Id = "lind", Family = CommanderFamily.Combat, Portrait = "mai", Unlock = "c2", Style = DeckStyle.Sustain, Repair = 1.25f,
                Prices = new[] { P(PriceReach.Engineers, 0.8f) },
                Lines = new[] { L(StatId.Damage, -0.10f, CommanderReach.Aircraft) },
            },
            new CommanderDef
            {
                // DECISIONS 23D: the air doctrine's +20 % aircraft health and 15 % faster fire support (neither overlapped).
                Id = "reyes", Family = CommanderFamily.Combat, Portrait = "dieuhau", Unlock = "c3", Style = DeckStyle.Air, AirRearm = 1.15f, AirCap = 1,
                StrikeCooldown = 0.85f,
                Lines = new[]
                {
                    L(StatId.Damage, 0.10f, CommanderReach.Aircraft), L(StatId.Health, 0.20f, CommanderReach.Aircraft),
                    L(StatId.MagazineReload, 0.15f, CommanderReach.Aircraft),
                    L(StatId.Health, -0.10f, CommanderReach.Towers),
                },
            },
            new CommanderDef
            {
                Id = "kerr", Family = CommanderFamily.Combat, Portrait = "linh", Unlock = "c4", Style = DeckStyle.Recon, StealthSight = 1.25f, ExposedTaken = 1.05f,
                Lines = new[] { L(StatId.Vision, 0.15f, CommanderReach.Army), L(StatId.Health, -0.05f, CommanderReach.Heavy) },
            },
            new CommanderDef
            {
                Id = "venn", Family = CommanderFamily.Combat, Portrait = "sen", Unlock = "c5+", Style = DeckStyle.Drones, JamResist = 0.3f,
                Lines = new[]
                {
                    L(StatId.Health, 0.15f, CommanderReach.DroneUnits), L(StatId.Damage, 0.10f, CommanderReach.Drones),
                    // The escort drones of the equipment (Hivemind, the drone escort module) hit harder the same way.
                    L(StatId.SummonPower, 0.10f, CommanderReach.Army),
                    L(StatId.Damage, -0.05f, CommanderReach.Tanks),
                },
            },
            new CommanderDef
            {
                // DECISIONS 23D: the blitz doctrine's +15 % speed merged with Rush's +10 % into one +15 %; its +15 % health on
                // scouts and light vehicles added (the whole army's -5 % still comes off after it).
                Id = "mendez", Family = CommanderFamily.Combat, Portrait = "mendez", Unlock = "i2", Style = DeckStyle.Blitz, Delivery = 0.75f,
                Lines = new[]
                {
                    L(StatId.Speed, 0.15f, CommanderReach.Vehicles), L(StatId.Health, 0.15f, CommanderReach.Light),
                    L(StatId.Health, -0.05f, CommanderReach.Army),
                },
            },
            new CommanderDef
            {
                Id = "brandt", Family = CommanderFamily.Combat, Portrait = "brandt", Unlock = "c6", Style = DeckStyle.Fortress,
                Prices = new[] { P(PriceReach.AirdropTowers, 0.8f) },
                Lines = new[]
                {
                    L(StatId.Health, 0.15f, CommanderReach.Towers), L(StatId.Damage, 0.10f, CommanderReach.Towers),
                    L(StatId.Speed, -0.05f, CommanderReach.Vehicles),
                },
            },
            // DECISIONS 23D: the artillery doctrine's +25 % artillery health and 25 % faster fire support (neither overlapped).
            Combat("dahl", "dahl", "c7", DeckStyle.Artillery,
                L(StatId.Damage, 0.15f, CommanderReach.Artillery), L(StatId.Range, 0.10f, CommanderReach.Artillery),
                L(StatId.Health, 0.25f, CommanderReach.Artillery),
                L(StatId.Damage, -0.10f, CommanderReach.DirectFire)).With(d => d.StrikeCooldown = 0.75f),

            // ------------------------------------------------------------ economy
            new CommanderDef
            {
                // DECISIONS 23D: the logistics doctrine. Its +20 % on the base rate and Ledger's +10 % on all income are one
                // bonus: +15 % on all income; its +4 army cap (a tenth of the usual 40) as supply +10 %.
                Id = "brenn", Family = CommanderFamily.Economy, Portrait = "brenn", Unlock = "i1", Style = DeckStyle.LongGame, Income = 1.15f,
                Supply = 1.10f,
                Lines = new[] { L(StatId.Damage, -0.05f, CommanderReach.Army) },
            },
            new CommanderDef
            {
                // The spec's +25 % on what a point pays was worth 2 % of the income in Conquest (DECISIONS 22F): +75 %.
                Id = "adler", Family = CommanderFamily.Economy, Portrait = "adler", Unlock = "c4", Style = DeckStyle.Points, PointIncome = 1.75f, NoPointsIncome = 0.95f,
                Lines = new[] { L(StatId.CaptureRate, 0.30f, CommanderReach.Vehicles) },
            },
            new CommanderDef
            {
                Id = "varro", Family = CommanderFamily.Economy, Portrait = "varro", Unlock = "c8", Style = DeckStyle.Swarm, Supply = 1.15f,
                Prices = new[] { P(PriceReach.Cheap, 0.85f) },
                // The spec's -10 % lost every Swarm battle of the first sweep (DECISIONS 22F).
                Lines = new[] { L(StatId.Health, -0.05f, CommanderReach.Army) },
            },
            new CommanderDef
            {
                // DECISIONS 23D: the armoured doctrine (tanks and heavies +20 % health) and Crown's +15 % health on dear
                // vehicles are one bonus: +20 % on both (a dear tank no longer gets the two stacked).
                Id = "reyn", Family = CommanderFamily.Economy, Portrait = "reyn", Unlock = "i3", Style = DeckStyle.Heavy,
                Prices = new[] { P(PriceReach.Vehicles, 1.10f) },
                Lines = new[] { L(StatId.Health, 0.20f, CommanderReach.ArmourOrDear), L(StatId.Damage, 0.15f, CommanderReach.Dear) },
            },
            Econ("quist", "c8", DeckStyle.Attrition).With(d =>
            {
                d.KillRefund = 0.35f;
                d.LossRefund = false;
            }),
            Econ("okoye", "c10", DeckStyle.Hoard).With(d =>
            {
                d.BankBonus = 15f;
                d.RichIncome = 1.10f;
                d.RichAt = 20f;
                d.EarlyIncome = 0.90f;
                d.EarlySeconds = 90f;
            }),
        };

        /// <summary>The enemy generals' passives (F.3), by the campaign's general id.</summary>
        public static readonly IReadOnlyList<CommanderDef> Generals = new[]
        {
            Gen("brandt", L(StatId.Health, 0.15f, CommanderReach.Towers), L(StatId.Speed, -0.05f, CommanderReach.Vehicles)),
            Gen("varga", L(StatId.Health, 0.10f, CommanderReach.Armour), L(StatId.Damage, -0.10f, CommanderReach.Aircraft)),
            Gen("orlov", L(StatId.Range, 0.15f, CommanderReach.Artillery), L(StatId.Spread, 0.20f, CommanderReach.Artillery),
                L(StatId.Health, -0.05f, CommanderReach.Light)),
            Gen("kessler", L(StatId.Health, 0.10f, CommanderReach.Ships), L(StatId.Health, -0.05f, CommanderReach.Towers))
                .With(d => d.Prices = new[] { P(PriceReach.Vehicles, 0.9f) }),
            Gen("sen", L(StatId.Health, 0.15f, CommanderReach.DroneUnits), L(StatId.Damage, -0.05f, CommanderReach.Tanks)),
            Gen("quaden", L(StatId.Damage, 0.10f, CommanderReach.Aircraft), L(StatId.Damage, -0.05f, CommanderReach.Ground)).With(d => d.AirCap = 1),
            Gen("hung", L(StatId.Damage, 0.05f, CommanderReach.Army)).With(d => d.LowHpDamage = 1.10f),
            Gen("aurel", L(StatId.Damage, 0.15f, CommanderReach.Energy), L(StatId.Health, 0.10f, CommanderReach.Shielded),
                L(StatId.Health, -0.05f, CommanderReach.Light)),
        };

        private static CommanderDef With(this CommanderDef d, Action<CommanderDef> set)
        {
            set(d);
            return d;
        }

        /// <summary>A commander or general by id ("kade", "gen.varga"); null for none or an unknown id.</summary>
        public static CommanderDef? Get(string? id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            foreach (var c in All)
                if (c.Id == id) return c;
            foreach (var g in Generals)
                if (g.Id == id) return g;
            return null;
        }

        /// <summary>The passive of the campaign general a mission is tied to (null: an untied mission has none).</summary>
        public static CommanderDef? General(string? generalId)
        {
            if (string.IsNullOrEmpty(generalId)) return null;
            foreach (var g in Generals)
                if (g.General == generalId) return g;
            return null;
        }
    }

    /// <summary>How a commander's lines reach units, go through the stat caps, change prices and steer the AI.</summary>
    public static class CommanderRules
    {
        public const int CheapAt = 5;
        public const int DearAt = 9;

        /// <summary>
        /// The loadout caps a commander's unit lines count towards (the Game's GearCatalog.StatCap for these stats; a
        /// test keeps the two the same). The Game hands the world the full tables (SimWorld.SetStatCaps).
        /// </summary>
        public static readonly float[] DefaultCaps = BuildCaps();

        private static float[] BuildCaps()
        {
            var caps = new float[(int)StatId.Count];
            caps[(int)StatId.Damage] = 0.25f;
            caps[(int)StatId.FireRate] = 0.15f;
            caps[(int)StatId.Health] = 0.25f;
            caps[(int)StatId.Speed] = 0.15f;
            caps[(int)StatId.Range] = 0.12f;
            caps[(int)StatId.Vision] = 0.25f;
            caps[(int)StatId.Spread] = 0.3f;
            caps[(int)StatId.MagazineReload] = 0.3f;
            caps[(int)StatId.CaptureRate] = 0.5f;
            caps[(int)StatId.SummonPower] = 0.15f;
            return caps;
        }

        /// <summary>A unit a commander works on: anything its side fields but a boss and the fixed structures that are not towers (an HQ, a wall).</summary>
        public static bool Fields(VehicleDef def) => !def.Boss && (!def.Static || def.Fort is { Kind: FortKind.Tower });

        public static bool Reaches(CommanderReach reach, VehicleDef def)
        {
            if (!Fields(def)) return false;
            var vehicle = !def.Static;
            return reach switch
            {
                CommanderReach.Army => true,
                CommanderReach.Vehicles => vehicle,
                CommanderReach.Ground => vehicle && !def.Flying,
                CommanderReach.Aircraft => vehicle && def.Flying && !def.Drone,
                CommanderReach.Drones => vehicle && (def.Drone || def.Weapon.Projectile == ProjectileKind.Drone),
                CommanderReach.DroneUnits => vehicle && def.Drone,
                CommanderReach.Tanks => vehicle && def.Class == UnitClass.Tank,
                CommanderReach.Armour => vehicle && def.Class is UnitClass.Tank or UnitClass.Heavy,
                CommanderReach.Heavy => vehicle && def.Class == UnitClass.Heavy,
                CommanderReach.Light => vehicle && def.Class is UnitClass.Light or UnitClass.Scout,
                CommanderReach.Artillery => vehicle && !def.Flying && def.Branch == ArmyBranch.Artillery,
                CommanderReach.DirectFire => vehicle && !def.Flying && def.Branch != ArmyBranch.Artillery && !def.Weapon.Indirect,
                CommanderReach.Towers => def.Static,
                CommanderReach.Ships => vehicle && def.Naval != null,
                CommanderReach.Cheap => vehicle && def.CpCost > 0 && def.CpCost <= CheapAt,
                CommanderReach.Dear => vehicle && def.CpCost >= DearAt,
                CommanderReach.ArmourOrDear => vehicle && (def.Class is UnitClass.Tank or UnitClass.Heavy || def.CpCost >= DearAt),
                CommanderReach.Energy => def.Weapon.DamageType == DamageType.Energy,
                CommanderReach.Shielded => def.Dome != null || def.Wards != null || HasShieldSkill(def),
                _ => false,
            };
        }

        private static bool HasShieldSkill(VehicleDef def)
        {
            foreach (var s in def.Skills)
                if (s.Kind == SkillKind.Shield) return true;
            return false;
        }

        /// <summary>
        /// A unit's equipment boost with the commander's lines on top (<paramref name="gear"/> unchanged when none
        /// reaches it). A strength counts towards the loadout's cap like a piece of equipment: gear and commander
        /// together never pass it, but a commander alone always gives its listed value (a line above the cap, Winter's
        /// +15 % range against the 12 % cap, is its own cap). A weakness comes off after the cap, like a trade-off's
        /// drawback. The first four stats are folded into the boost's multipliers.
        /// </summary>
        public static VehicleBoost Merge(VehicleBoost gear, CommanderDef? commander, VehicleDef def, float[]? caps)
        {
            if (commander == null || commander.Lines.Count == 0 || !Fields(def)) return gear;
            caps ??= DefaultCaps;
            float[]? stats = null;
            foreach (var line in commander.Lines)
            {
                if (!Reaches(line.Reach, def)) continue;
                stats ??= gear.Stats != null ? (float[])gear.Stats.Clone() : new float[(int)StatId.Count];
                var i = (int)line.Stat;
                if (i >= stats.Length) continue;
                var had = stats[i];
                stats[i] = line.Value > 0f ? MathF.Max(had, MathF.Min(had + line.Value, MathF.Max(i < caps.Length ? caps[i] : 0f, line.Value))) : had + line.Value;
            }
            if (stats == null) return gear;
            float Fold(StatId id, float multiplier) => multiplier * (1f + stats[(int)id]) / MathF.Max(0.05f, 1f + gear.Stat(id));
            return new VehicleBoost(Fold(StatId.Health, gear.Hp), Fold(StatId.Damage, gear.Damage), Fold(StatId.FireRate, gear.FireRate), Fold(StatId.Speed, gear.Speed),
                gear.DamageTaken, gear.Regen, gear.Special, gear.SpecialPower, stats, gear.Traits, gear.SpecialPower2);
        }

        public static bool Reaches(PriceReach reach, VehicleDef def) => reach switch
        {
            PriceReach.Vehicles => !def.Static,
            PriceReach.Cheap => !def.Static && def.CpCost > 0 && def.CpCost <= CheapAt,
            PriceReach.Engineers => def.RepairAura != null,
            _ => false,
        };

        /// <summary>What a vehicle card costs under the commander, as a share of its price (1: unchanged).</summary>
        public static float PriceScale(CommanderDef? c, VehicleDef def)
        {
            if (c == null) return 1f;
            var scale = 1f;
            foreach (var p in c.Prices)
                if (Reaches(p.Reach, def)) scale *= p.Scale;
            return scale;
        }

        /// <summary>What a support card costs under the commander, as a share of its price.</summary>
        public static float PriceScale(CommanderDef? c, SupportDef s)
        {
            if (c == null) return 1f;
            var scale = 1f;
            foreach (var p in c.Prices)
                if (p.Reach == PriceReach.AirdropTowers && s.Kind == SupportKind.Tower) scale *= p.Scale;
            return scale;
        }

        /// <summary>
        /// How well a card suits the commander, for the AI's buying (F.5): its stat lines on the card weighted by how
        /// much each stat decides a fight, a cheaper price, and the side-wide numbers that work through the card. About
        /// 0.1 for a card a commander clearly favours, below 0 for one it weakens.
        /// </summary>
        public static float Fit(CommanderDef? c, VehicleDef def)
        {
            if (c == null || !Fields(def)) return 0f;
            var fit = 0f;
            foreach (var l in c.Lines)
            {
                if (!Reaches(l.Reach, def)) continue;
                fit += l.Value * l.Stat switch
                {
                    StatId.Damage or StatId.Health => 1f,
                    StatId.Range => 0.8f,
                    StatId.Speed => 0.6f,
                    StatId.MagazineReload or StatId.Spread => 0.4f,
                    StatId.Vision => 0.3f,
                    StatId.CaptureRate => def.CaptureRate > 0f ? 0.3f : 0f,
                    _ => 0f,
                };
            }
            fit += (1f - PriceScale(c, def)) * 1.5f;
            var air = def.Flying && !def.Drone && !def.Static;
            if (air && (c.AirCap > 0 || c.AirRearm > 1f)) fit += 0.05f;
            if (def.RepairAura != null && c.Repair > 1f) fit += 0.1f;
            if (c.JamResist > 0f && Reaches(CommanderReach.Drones, def)) fit += 0.05f;
            if (c.StealthSight > 1f && def.Class == UnitClass.Scout) fit += 0.05f;
            if (c.BankBonus > 0f && def.CpCost >= DearAt) fit += 0.05f;
            return fit;
        }

        /// <summary>How well a support suits the commander (the AI's fire support, F.5): its kind against the commander's arm.</summary>
        public static float SupportFit(CommanderDef? c, SupportDef s)
        {
            if (c == null) return 0f;
            var fit = (1f - PriceScale(c, s)) * 1.5f;
            foreach (var l in c.Lines)
            {
                if (l.Value <= 0f || l.Stat != StatId.Damage) continue;
                if (l.Reach == CommanderReach.Aircraft && s.Kind is SupportKind.Airstrike) fit += l.Value;
                if (l.Reach == CommanderReach.Artillery && s.Kind is SupportKind.Barrage) fit += l.Value;
                if (l.Reach == CommanderReach.Towers && s.Kind is SupportKind.Tower) fit += l.Value;
            }
            return fit;
        }
    }
}
