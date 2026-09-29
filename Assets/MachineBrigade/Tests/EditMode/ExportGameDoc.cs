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
using MachineBrigade.Sim.Modes;

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
                    ["vehicles"] = catalog.Vehicles.Values.Where(v => !v.Static && !v.Boss && !v.Elite && v.Card).OrderBy(v => v.CpCost).ThenBy(v => v.Id).Select(v => Vehicle(catalog, v)).ToList(),
                    // Vehicles that are no card (the Gunship item's AC-130): with the items, not the deck.
                    ["itemVehicles"] = catalog.Vehicles.Values.Where(v => !v.Static && !v.Boss && !v.Elite && !v.Card).OrderBy(v => v.Id).Select(v => Vehicle(catalog, v)).ToList(),
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
                    ["chapters"] = Campaign.Chapters.Select(c => (object)new Dictionary<string, object>
                    {
                        ["number"] = c.Number, ["act"] = c.Act, ["title"] = Text("chapter." + c.Number + ".title"), ["summary"] = Text("chapter." + c.Number + ".summary"),
                        ["maps"] = c.Maps.Select(id => Strings.Get("map." + id)).ToList(), ["general"] = c.General ?? "",
                        ["missions"] = Campaign.All.Count(m => m.Chapter == c.Number),
                    }).ToList(),
                    ["characters"] = new[] { "khai", "mai", "dieuhau", "linh", "hung", "varga", "orlov", "kessler", "sen", "quaden", "aurel" }
                        .Select(id => (object)new Dictionary<string, object>
                        {
                            ["id"] = id, ["name"] = Text("char." + id + ".name"), ["role"] = Text("char." + id + ".role"), ["bio"] = Text("char." + id + ".bio"),
                        }).ToList(),
                    ["timeline"] = Enumerable.Range(0, 20).Select(i => Text("timeline." + i)).Where(s => s.Length > 0).Cast<object>().ToList(),
                    ["generals"] = Campaign.Generals.Select(g => (object)new Dictionary<string, object>
                    {
                        ["id"] = g.Id, ["name"] = Text("char." + g.Id + ".name"), ["style"] = g.Style, ["stance"] = g.Stance,
                        ["deck"] = g.Deck.Select(Strings.Card).ToList(), ["supports"] = g.Supports.Select(Strings.Support).ToList(),
                        ["elitesPrefer"] = catalog.Generals.TryGetValue(g.Id, out var rules) ? rules.ElitePrefer.ToList() : new List<string>(),
                    }).ToList(),
                    ["base"] = BaseData(catalog),
                    ["operations"] = OperationsData(),
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
                // Prompt 13 A.1: over a whole load (salvos, magazines and their change, a launcher's reload).
                var raw = MachineBrigade.Sim.Combat.FirePower.Sustained(w, v);
                weapons.Add(new Dictionary<string, object>
                {
                    ["id"] = w.Id, ["name"] = UnitLines.WeaponName(w), ["slot"] = m.Slot, ["type"] = w.DamageType.ToString(), ["damage"] = w.Damage, ["burst"] = w.Burst,
                    ["cooldown"] = w.Cooldown, ["range"] = w.Range, ["minRange"] = w.MinRange, ["splash"] = w.SplashRadius,
                    ["targets"] = w.Targets.ToString(), ["dps"] = raw, ["projectile"] = w.Projectile.ToString(),
                    ["clip"] = w.Clip, ["clipReload"] = w.ClipReload, ["speed"] = w.ProjectileSpeed,
                    ["bonuses"] = w.Bonuses.Select(b => (object)new Dictionary<string, object>
                    {
                        ["mult"] = b.Mult, ["class"] = b.Class?.ToString() ?? "", ["armor"] = b.Armor?.ToString() ?? "", ["still"] = b.StillFor, ["flank"] = b.Flank,
                    }).ToList(),
                });
                foreach (ArmorClass a in Enum.GetValues(typeof(ArmorClass)))
                {
                    var air = a == ArmorClass.Air;
                    if (!w.CanTarget(air)) continue;
                    // A bonus on an armour class alone counts in (a bunker-buster on structures); ones that
                    // depend on the target's class, standing still or a flank are listed with the weapon.
                    var bonus = 1f;
                    foreach (var b in w.Bonuses)
                        if (b.Armor == a && b.Class == null && b.StillFor <= 0f && !b.Flank) bonus *= b.Mult;
                    dps[a.ToString()] += raw * catalog.Damage.Multiplier(w, a) * bonus;
                }
            }
            return new Dictionary<string, object>
            {
                ["id"] = v.Id, ["name"] = Strings.Card(v.Id), ["short"] = Strings.Short(v.Id), ["note"] = Text("note." + v.Id), ["guide"] = Text("guide." + v.Id),
                ["rounds"] = v.Mounts.Select(m => m.ProjectileModel ?? m.Weapon.ProjectileModel ?? "").ToList(),
                ["class"] = v.Class.ToString(), ["armor"] = v.Armor.ToString(), ["hp"] = v.MaxHp, ["speed"] = v.Speed, ["cost"] = v.CpCost,
                ["vision"] = v.VisionRange, ["flying"] = v.Flying, ["model"] = v.Model, ["weapons"] = weapons, ["dpsVs"] = dps,
                ["skills"] = v.Skills.Select(s => s.Id).ToList(), ["death"] = v.DeathExplosion?.Damage ?? 0f,
                // Prompt 13 G: the generated lines, as the detail screen shows them.
                ["behavior"] = UnitLines.Behaviour(catalog, v), ["ammo"] = UnitLines.Ammo(catalog, v),
                ["phases"] = v.Phases.Select(p => (object)p.At).ToList(), ["general"] = v.General ?? "",
                ["parts"] = v.Parts.Select(p => (object)new Dictionary<string, object>
                {
                    ["id"] = p.Id, ["kind"] = p.Kind, ["name"] = Text("part." + p.Kind), ["hp"] = p.Hp, ["breakDamage"] = p.BreakDamage,
                    ["effects"] = MenuScreen.PartEffects(v, p), ["radio"] = p.Radio != null,
                }).ToList(),
                ["partLock"] = v.PartLock != null ? Text("part." + v.PartLock.Kind) + " ×" + v.PartLock.Count : "",
                ["partPatch"] = v.Skills.Any(k => k.Kind == SkillKind.Patch), ["partTip"] = Text("guide.parts.tip." + v.Id),
                ["size"] = v.Fort?.Size.ToString() ?? "", ["bossFile"] = Text("bossfile." + v.Id),
            };
        }

        private static object Support(SupportDef s) => new Dictionary<string, object>
        {
            ["id"] = s.Id, ["name"] = Strings.Support(s.Id), ["info"] = Text("support." + s.Id + ".info"), ["kind"] = s.Kind.ToString(), ["guide"] = Text("guide." + s.Id),
            ["cost"] = s.CpCost, ["cooldown"] = s.Cooldown, ["damage"] = s.Damage, ["radius"] = s.Radius, ["count"] = s.Count,
            ["duration"] = s.Duration, ["type"] = s.DamageType.ToString(),
        };

        private static object Gear()
        {
            var bases = GearCatalog.Bases.Select(b => (object)new Dictionary<string, object>
            {
                ["id"] = b.Id, ["name"] = Text("gear.base." + b.Id), ["slot"] = b.Slot.ToString(), ["implicit"] = b.Implicit.ToString(),
                ["implicitName"] = b.Implicit == StatId.Count ? GearText.BaseNote(b) : GearText.Line(b.Implicit, b.Top[b.Top.Length - 1]), ["top"] = b.Top,
                ["lines"] = b.Implicit == StatId.Count ? new List<string>() : b.Top.Select(v => GearText.Line(b.Implicit, v)).ToList(),
                ["penaltyLine"] = b.TradeOff && b.PenaltyTop != null ? GearText.Line(b.Penalty, b.PenaltyTop[b.PenaltyTop.Length - 1], true) : "",
                ["tradeOff"] = b.TradeOff, ["penalty"] = b.TradeOff ? b.Penalty.ToString() : "", ["minRarity"] = b.MinRarity,
            }).ToList();
            var traits = GearCatalog.Traits.Select(t => (object)new Dictionary<string, object>
            {
                ["id"] = t.Id.ToString(), ["key"] = t.Key, ["name"] = Text("trait." + t.Key), ["effect"] = GearText.TraitEffect(t.At(Rarity.Legendary)),
                ["effectEpic"] = GearText.TraitEffect(t.At(Rarity.Epic)), ["effectLegendary"] = GearText.TraitEffect(t.At(Rarity.Legendary)),
                ["slot"] = t.Slot.ToString(), ["epic"] = t.Epic, ["legendary"] = t.Legendary,
            }).ToList();
            var modules = GearCatalog.Modules.Select(m => (object)new Dictionary<string, object>
            {
                ["id"] = m.Module.ToString(), ["key"] = m.Key, ["name"] = Text("special." + m.Key),
                ["effect"] = GearText.ModuleEffect(m.Module, Rarity.Legendary),
                ["effectEpic"] = GearText.ModuleEffect(m.Module, Rarity.Epic), ["effectLegendary"] = GearText.ModuleEffect(m.Module, Rarity.Legendary),
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
            ["rankCut"] = Enumerable.Range(1, CardRanks.Max).Select(CardRanks.CutBasisPoints).ToList(),
            ["callCost"] = new[] { 4, 6, 8, 10, 12, 14, 16, 20, 22 }.Select(c => (object)new Dictionary<string, object>
            {
                ["cost"] = c, ["rank7"] = CardRanks.CallCost(c, 7), ["rank9"] = CardRanks.CallCost(c, 9),
            }).ToList(),
            ["bossKinds"] = MachineBrigade.Sim.Modes.BossRushRules.Kinds.Select(k => (object)k.ToList()).ToList(),
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
            ["mapName"] = Strings.Get("map." + m.Map), ["variant"] = m.Variant,
            ["goal"] = m.Goal.ToString(), ["goalName"] = Text("goal." + m.Goal.ToString().ToLowerInvariant()), ["weather"] = m.Weather,
            ["difficulty"] = m.Difficulty, ["coins"] = m.RewardCoins, ["xp"] = m.RewardXp, ["unlocks"] = m.Unlocks.Select(Strings.Card).ToList(),
            ["timeLimit"] = m.TimeLimit, ["boss"] = m.Boss != null ? Strings.Card(m.Boss.Def) : "",
            ["chapter"] = m.Chapter, ["side"] = m.Side, ["general"] = m.General ?? "", ["operation"] = m.Operation, ["replay"] = m.Replay,
            ["hqLevel"] = m.HqLevel, ["legacy"] = m.Legacy ?? "",
            ["stages"] = m.Stages.Select(s => (object)new Dictionary<string, object>
            {
                ["id"] = s.Id, ["goal"] = s.Mission.Goal.ToString(), ["goalName"] = Text("goal." + s.Mission.Goal.ToString().ToLowerInvariant()),
                ["title"] = Text("stage." + m.Id + "." + s.Id), ["cp"] = s.Cp, ["choices"] = s.Choices.Select(c => Text("choice." + m.Id + "." + c.Key)).ToList(),
                ["events"] = s.Events.Select(e => e.Kind.ToString()).Distinct().ToList(),
            }).ToList(),
            ["ally"] = m.Ally != null,
        };

        private static object BaseData(Catalog catalog)
        {
            var rules = catalog.Base;
            var levels = Enumerable.Range(1, 5).Select(l => (object)new Dictionary<string, object>
            {
                ["level"] = l, ["small"] = rules.Slots(l, SlotSize.Small), ["medium"] = rules.Slots(l, SlotSize.Medium),
                ["large"] = rules.Slots(l, SlotSize.Large), ["utility"] = rules.UtilitySlots(l),
            }).ToList();
            var towers = TowerCards.All(catalog).Select(id =>
            {
                var def = catalog.Vehicles[id];
                return (object)new Dictionary<string, object>
                {
                    ["id"] = id, ["name"] = Strings.Card(id), ["size"] = def.Fort?.Size.ToString() ?? "", ["hp"] = def.MaxHp,
                    ["rebuildCp"] = rules.RebuildCost(def), ["rebuildSeconds"] = rules.RebuildCooldown(def), ["guide"] = Text("guide." + id),
                    ["branches"] = TowerCards.Branches(catalog, id).Select(b => (object)new Dictionary<string, object>
                    {
                        ["id"] = b, ["name"] = Text("branch." + b), ["info"] = Text("branch." + b + ".info"),
                    }).ToList(),
                };
            }).ToList();
            var modules = catalog.Vehicles.Values.Where(v => v.Fort is { Kind: FortKind.Utility }).OrderBy(v => v.Id).Select(v => (object)new Dictionary<string, object>
            {
                ["id"] = v.Id, ["name"] = Strings.Card(v.Id), ["guide"] = Text("guide." + v.Id),
            }).ToList();
            return new Dictionary<string, object> { ["levels"] = levels, ["towers"] = towers, ["modules"] = modules };
        }

        private static object OperationsData()
        {
            var data = Operations.Data;
            return new Dictionary<string, object>
            {
                ["tiers"] = data.Tiers.Select((t, i) => (object)new Dictionary<string, object>
                {
                    ["id"] = t.Id, ["name"] = Text("tier." + i), ["enemy"] = t.Enemy, ["playerIncome"] = t.PlayerIncome, ["supports"] = t.Supports, ["score"] = t.Score,
                }).ToList(),
                ["scoring"] = new Dictionary<string, object>
                {
                    ["win"] = data.Scoring.Win, ["time"] = data.Scoring.Time, ["par"] = data.Scoring.Par, ["losses"] = data.Scoring.Losses,
                    ["lossesAtZero"] = data.Scoring.LossesAtZero, ["hq"] = data.Scoring.Hq,
                },
                ["weekly"] = new Dictionary<string, object> { ["fortress"] = data.WeeklyFortressReward, ["operation"] = data.WeeklyOperationReward },
                ["mutators"] = data.Mutators.Select(m => (object)new Dictionary<string, object>
                {
                    ["id"] = m.Id, ["name"] = Text("mutator." + m.Id), ["info"] = Text("mutator." + m.Id + ".info"), ["score"] = m.Score,
                }).ToList(),
                ["replayable"] = Operations.Replayable.Select(m => Text("mission." + m.Id + ".name")).Cast<object>().ToList(),
                ["rotation"] = data.Rotation(Math.Max(1, Operations.Big.Count)).Select(e => (object)new Dictionary<string, object>
                {
                    ["operation"] = Operations.Big.Count > 0 ? Text("mission." + Operations.Big[e.operation].Id + ".name") : "",
                    ["a"] = Text("mutator." + e.a.Id), ["b"] = Text("mutator." + e.b.Id),
                }).ToList(),
            };
        }

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
