using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Writes the game's own numbers (vehicles and their weapons with damage per second against each
    /// armour, fire support, towers, bosses, equipment, rank and crate economy, modes, campaign) to
    /// one JSON file for the design document (Tools/docs/build_doc.py). Runs only with the
    /// environment variable MB_EXPORT set to the output path.
    /// </summary>
    public class ExportGameDoc
    {
        [Test, Category("Export")]
        public void ExportTheGameForTheDesignDocument()
        {
            var path = Environment.GetEnvironmentVariable("MB_EXPORT");
            if (string.IsNullOrEmpty(path)) Assert.Ignore("design document export: set MB_EXPORT to the output path");
            var wasVietnamese = Strings.Vietnamese;
            Strings.Vietnamese = Environment.GetEnvironmentVariable("MB_EXPORT_LANG") != "en";
            try
            {
                var catalog = GameContent.LoadCatalog();
                var doc = new Dictionary<string, object>
                {
                    ["language"] = Strings.Vietnamese ? "vi" : "en",
                    ["damageTable"] = DamageTable(catalog),
                    ["vehicles"] = catalog.Vehicles.Values.Where(v => !v.Static && !v.Boss && !v.Elite).OrderBy(v => v.CpCost).ThenBy(v => v.Id).Select(v => Vehicle(catalog, v)).ToList(),
                    ["elites"] = catalog.Vehicles.Values.Where(v => v.Elite).OrderBy(v => v.Id).Select(v => Vehicle(catalog, v)).ToList(),
                    ["bosses"] = catalog.Vehicles.Values.Where(v => v.Boss).OrderBy(v => v.MaxHp).Select(v => Vehicle(catalog, v)).ToList(),
                    ["towers"] = catalog.Vehicles.Values.Where(v => v.Static).OrderBy(v => v.Id).Select(v => Vehicle(catalog, v)).ToList(),
                    ["supports"] = catalog.Supports.Values.OrderBy(s => s.CpCost).Select(Support).ToList(),
                    ["gear"] = Gear(),
                    ["economy"] = Economy(),
                    ["modes"] = Modes(),
                    ["campaign"] = Campaign.All.Select(Mission).ToList(),
                    ["maps"] = MatchSettings.AllMaps.Select(m => (object)new Dictionary<string, object>
                    {
                        ["id"] = m.Id, ["name"] = Strings.Get("map." + m.Id), ["sub"] = Text("map." + m.Id + ".sub"), ["theme"] = m.Theme,
                    }).ToList(),
                };
                File.WriteAllText(path, Json(doc), new UTF8Encoding(false));
            }
            finally
            {
                Strings.Vietnamese = wasVietnamese;
            }
        }

        private static string Text(string key) => Strings.Has(key) ? Strings.Get(key) : "";

        private static object DamageTable(Catalog catalog)
        {
            var table = new Dictionary<string, object>();
            foreach (DamageType d in Enum.GetValues(typeof(DamageType)))
            {
                var row = new Dictionary<string, object>();
                foreach (ArmorClass a in Enum.GetValues(typeof(ArmorClass))) row[a.ToString()] = catalog.Damage.Multiplier(d, a);
                table[d.ToString()] = row;
            }
            return table;
        }

        private static object Vehicle(Catalog catalog, VehicleDef v)
        {
            var weapons = new List<object>();
            var dps = new Dictionary<string, float>();
            foreach (ArmorClass a in Enum.GetValues(typeof(ArmorClass))) dps[a.ToString()] = 0f;
            foreach (var m in v.Mounts)
            {
                var w = m.Weapon;
                if (w.Damage <= 0f) continue;
                var raw = UnitStats.Dps(w);
                weapons.Add(new Dictionary<string, object>
                {
                    ["id"] = w.Id, ["slot"] = m.Slot, ["type"] = w.DamageType.ToString(), ["damage"] = w.Damage, ["burst"] = w.Burst,
                    ["cooldown"] = w.Cooldown, ["range"] = w.Range, ["minRange"] = w.MinRange, ["splash"] = w.SplashRadius,
                    ["targets"] = w.Targets.ToString(), ["dps"] = raw, ["projectile"] = w.Projectile.ToString(),
                });
                foreach (ArmorClass a in Enum.GetValues(typeof(ArmorClass)))
                {
                    var air = a == ArmorClass.Air;
                    if (!w.CanTarget(air)) continue;
                    dps[a.ToString()] += raw * catalog.Damage.Multiplier(w.DamageType, a);
                }
            }
            return new Dictionary<string, object>
            {
                ["id"] = v.Id, ["name"] = Strings.Card(v.Id), ["short"] = Strings.Short(v.Id), ["note"] = Text("note." + v.Id),
                ["class"] = v.Class.ToString(), ["armor"] = v.Armor.ToString(), ["hp"] = v.MaxHp, ["speed"] = v.Speed, ["cost"] = v.CpCost,
                ["vision"] = v.VisionRange, ["flying"] = v.Flying, ["model"] = v.Model, ["weapons"] = weapons, ["dpsVs"] = dps,
                ["skills"] = v.Skills.Select(s => s.Id).ToList(), ["death"] = v.DeathExplosion?.Damage ?? 0f,
            };
        }

        private static object Support(SupportDef s) => new Dictionary<string, object>
        {
            ["id"] = s.Id, ["name"] = Strings.Support(s.Id), ["info"] = Text("support." + s.Id + ".info"), ["kind"] = s.Kind.ToString(),
            ["cost"] = s.CpCost, ["cooldown"] = s.Cooldown, ["damage"] = s.Damage, ["radius"] = s.Radius, ["count"] = s.Count,
            ["duration"] = s.Duration, ["type"] = s.DamageType.ToString(),
        };

        private static object Gear()
        {
            var bases = GearCatalog.Bases.Select(b => (object)new Dictionary<string, object>
            {
                ["id"] = b.Id, ["name"] = Text("gear.base." + b.Id), ["slot"] = b.Slot.ToString(), ["implicit"] = b.Implicit.ToString(),
                ["implicitName"] = Text("stat.line." + b.Implicit.ToString().ToLowerInvariant()), ["top"] = b.Top,
                ["tradeOff"] = b.TradeOff, ["penalty"] = b.TradeOff ? b.Penalty.ToString() : "", ["minRarity"] = b.MinRarity,
            }).ToList();
            var traits = GearCatalog.Traits.Select(t => (object)new Dictionary<string, object>
            {
                ["id"] = t.Id.ToString(), ["key"] = t.Key, ["name"] = Text("trait." + t.Key), ["effect"] = Text("trait." + t.Key + ".info"),
                ["slot"] = t.Slot.ToString(), ["epic"] = t.Epic, ["legendary"] = t.Legendary,
            }).ToList();
            var modules = GearCatalog.Modules.Select(m => (object)new Dictionary<string, object>
            {
                ["id"] = m.Module.ToString(), ["key"] = m.Key, ["name"] = Text("special." + m.Key), ["effect"] = Text("special." + m.Key + ".info"),
                ["epic"] = m.Epic, ["legendary"] = m.Legendary,
            }).ToList();
            var brands = new List<object>();
            for (var i = 1; i <= GearCatalog.Brands.Length; i++)
            {
                var b = GearCatalog.Brand(i);
                brands.Add(new Dictionary<string, object> { ["index"] = i, ["name"] = GearText.BrandName(b), ["bonuses"] = GearText.BrandBonuses(b) });
            }
            return new Dictionary<string, object>
            {
                ["rarities"] = new[] { "Common", "Uncommon", "Rare", "Epic", "Legendary" }, ["levelCap"] = Game.Match.Gear.LevelCap,
                ["caps"] = Game.Match.Gear.Cap, ["bases"] = bases, ["traits"] = traits, ["modules"] = modules, ["brands"] = brands,
            };
        }

        private static object Economy() => new Dictionary<string, object>
        {
            ["rankCoins"] = Enumerable.Range(1, CardRanks.Max - 1).Select(CardRanks.CoinsToNext).ToList(),
            ["rankPrints"] = Enumerable.Range(1, CardRanks.Max - 1).Select(CardRanks.BlueprintsToNext).ToList(),
            ["rankBonus"] = Enumerable.Range(1, CardRanks.Max).Select(CardRanks.Bonus).ToList(),
            ["crateCoinPrice"] = Crates.CoinPrice, ["crateRolls"] = Crates.Rolls, ["crateOdds"] = Crates.Odds,
            ["crateCoinsLow"] = Crates.CoinsLow, ["crateCoinsHigh"] = Crates.CoinsHigh,
            ["coinPacks"] = CoinStore.Packs.Select(p => (object)new Dictionary<string, object> { ["id"] = p.id, ["coins"] = p.coins, ["price"] = p.price }).ToList(),
        };

        private static object Modes()
        {
            var list = new List<object>();
            foreach (GameModeKind kind in Enum.GetValues(typeof(GameModeKind)))
            {
                var key = kind switch
                {
                    GameModeKind.KingOfTheHill => "mode.hill", GameModeKind.BossRush => "mode.bossrush", _ => "mode." + kind.ToString().ToLowerInvariant(),
                };
                list.Add(new Dictionary<string, object>
                {
                    ["id"] = kind.ToString(), ["name"] = Text(key), ["sub"] = Text(key + "Sub"), ["toast"] = Text(key + ".toast"),
                });
            }
            return list;
        }

        private static object Mission(MissionDef m) => new Dictionary<string, object>
        {
            ["id"] = m.Id, ["name"] = Text("mission." + m.Id + ".name"), ["brief"] = Text("mission." + m.Id + ".brief"), ["map"] = m.Map,
            ["goal"] = m.Goal.ToString(), ["goalName"] = Text("goal." + m.Goal.ToString().ToLowerInvariant()), ["weather"] = m.Weather,
            ["difficulty"] = m.Difficulty, ["coins"] = m.RewardCoins, ["xp"] = m.RewardXp, ["unlocks"] = m.Unlocks.Select(Strings.Card).ToList(),
            ["timeLimit"] = m.TimeLimit, ["boss"] = m.Boss != null ? Strings.Card(m.Boss.Def) : "",
        };

        // A small JSON writer (dictionaries, lists, arrays, strings, numbers, booleans).
        private static string Json(object value)
        {
            var sb = new StringBuilder();
            Write(sb, value, 0);
            return sb.ToString();
        }

        private static void Write(StringBuilder sb, object value, int depth)
        {
            switch (value)
            {
                case null:
                    sb.Append("null");
                    break;
                case string s:
                    sb.Append('"');
                    foreach (var c in s)
                        sb.Append(c switch { '"' => "\\\"", '\\' => "\\\\", '\n' => "\\n", '\r' => "", '\t' => "\\t", _ => c.ToString() });
                    sb.Append('"');
                    break;
                case bool b:
                    sb.Append(b ? "true" : "false");
                    break;
                case float f:
                    sb.Append(float.IsFinite(f) ? Math.Round(f, 4).ToString(CultureInfo.InvariantCulture) : "0");
                    break;
                case double d:
                    sb.Append(double.IsFinite(d) ? Math.Round(d, 4).ToString(CultureInfo.InvariantCulture) : "0");
                    break;
                case int i:
                    sb.Append(i.ToString(CultureInfo.InvariantCulture));
                    break;
                case IDictionary dict:
                    sb.Append('{');
                    var first = true;
                    foreach (DictionaryEntry e in dict)
                    {
                        if (!first) sb.Append(',');
                        first = false;
                        sb.Append('\n').Append(' ', depth * 2 + 2);
                        Write(sb, e.Key.ToString(), depth + 1);
                        sb.Append(": ");
                        Write(sb, e.Value, depth + 1);
                    }
                    sb.Append('\n').Append(' ', depth * 2).Append('}');
                    break;
                case IEnumerable list:
                    sb.Append('[');
                    var firstItem = true;
                    foreach (var item in list)
                    {
                        if (!firstItem) sb.Append(", ");
                        firstItem = false;
                        Write(sb, item, depth + 1);
                    }
                    sb.Append(']');
                    break;
                default:
                    Write(sb, value.ToString(), depth);
                    break;
            }
        }
    }
}
