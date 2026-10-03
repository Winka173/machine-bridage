using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using AudioCode = MachineBrigade.Game.Audio;
using FxCode = MachineBrigade.Game.Effects;
using RenderCode = MachineBrigade.Game.Rendering;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Balance pack (lane B, §3): game.json "balancePack": the values the export's NEED_CODE_CHECK cells need, read from
    /// the game's own code (SimTunables, BalancePackFacts and the game's classes), one key per sheet. Each section is
    /// built on its own: one that throws writes {"error": ...} and the rest still export. Nothing here changes the game.
    /// </summary>
    public partial class ExportGameDoc
    {
        private static Dictionary<string, object> BalancePack(Catalog catalog)
        {
            var pack = new Dictionary<string, object>();
            void Section(string key, Func<object> build)
            {
                try
                {
                    pack[key] = build();
                }
                catch (Exception e)
                {
                    pack[key] = new Dictionary<string, object> { ["error"] = e.GetType().Name + ": " + e.Message };
                }
            }
            Section("tunables", () => SimTunables.Snapshot().Select(t => (object)new Dictionary<string, object>
            {
                ["key"] = t.key, ["unit"] = t.unit, ["value"] = t.value,
            }).ToList());
            Section("interception", () => PackInterception(catalog));
            Section("roundGroups", () => PackRoundGroups(catalog));
            Section("secondRounds", () => PackSecondRounds(catalog));
            Section("flaresPerRelease", () => PackFlares(catalog));
            Section("weaponFlight", () => PackFlight(catalog));
            Section("vehicles", () => PackVehicles(catalog));
            Section("openingSquads", () => PackOpening(catalog));
            Section("aircraftShotBand", () => NotApplicable(
                "no target band of shots to kill aircraft in the code or the data (the owner's D8 band is in Docs/balance only)"));
            Section("boss", () => PackBoss(catalog));
            Section("towers", () => PackTowers(catalog));
            Section("economy", () => PackEconomy(catalog));
            Section("dialogue", () => PackDialogue(catalog));
            Section("missions", PackMissions);
            Section("matchEnd", PackMatchEnd);
            Section("cutscene", PackCutscene);
            Section("audio", PackAudio);
            Section("wrecks", () => PackWrecks(catalog));
            Section("models", () => NotApplicable(
                "LOD0 is the shipped GLB (Tools/assets/glb_analyze.py counts it); LOD1 is built at load by ModelLibrary.Lod " +
                "(error 0.5 px), which needs the runtime model import: not available in the EditMode export"));
            Section("previews", () => catalog.Vehicles.Values.OrderBy(v => v.Id).Select(v => (object)new Dictionary<string, object>
            {
                ["id"] = v.Id, ["setting"] = RenderCode.PreviewSettings.Of(v).ToString(),
            }).ToList());
            Section("defaultSettings", PackSettings);
            return pack;
        }

        private static Dictionary<string, object> NotApplicable(string reason) => new()
        {
            ["status"] = "KHONG_AP_DUNG", ["reason"] = reason,
        };

        /// <summary>Khac_che chan_*: each protection system against each round kind (yes / no / some of them, the shell share).</summary>
        private static object PackInterception(Catalog catalog)
        {
            var byKind = BalancePackFacts.RoundKinds.ToDictionary(k => k, k => catalog.Weapons.Values.Where(w => BalancePackFacts.RoundKind(w) == k).ToList());
            var carriers = new List<object>();
            foreach (var v in catalog.Vehicles.Values.Where(v => v.Aps != null).OrderBy(v => v.Id))
            {
                var blocks = new Dictionary<string, object>();
                var shares = new Dictionary<string, object>();
                foreach (var kind in BalancePackFacts.RoundKinds)
                {
                    var list = byKind[kind];
                    var taken = 0;
                    var share = 1f;
                    foreach (var w in list)
                        if (BalancePackFacts.MayIntercept(v, w, out var s))
                        {
                            taken++;
                            share = Math.Min(share, s);
                        }
                    blocks[kind] = list.Count == 0 ? "khong_co_dan" : taken == 0 ? "khong" : taken == list.Count ? "co" : "mot_phan:" + taken + "/" + list.Count;
                    shares[kind] = taken > 0 ? share : 0f;
                }
                var a = v.Aps!;
                carriers.Add(new Dictionary<string, object>
                {
                    ["id"] = v.Id, ["mode"] = v.InterceptionMode.ToString(), ["static"] = v.Static, ["boss"] = v.Boss,
                    ["radius"] = a.Radius, ["charges"] = a.Charges, ["recharge"] = a.Recharge, ["burst"] = a.Burst, ["heavy"] = a.Heavy,
                    ["rockets"] = a.Rockets, ["shells"] = a.Shells, ["direct"] = a.Direct, ["laser"] = a.Laser,
                    ["blocks"] = blocks, ["shellShare"] = shares,
                });
            }
            return new Dictionary<string, object>
            {
                ["kinds"] = BalancePackFacts.RoundKinds.Cast<object>().ToList(),
                ["note"] = "static rules of DamageSystem.TryIntercept / GunTakes (reach, interceptors left, smoke and rolls left out)",
                ["carriers"] = carriers,
            };
        }

        /// <summary>Hanh_vi_dan_nhom: per round kind, how its rounds aim, warn and fly, and what flares and APS do to them.</summary>
        private static object PackRoundGroups(Catalog catalog)
        {
            var rules = catalog.Munitions;
            var rows = new List<object>();
            foreach (var kind in BalancePackFacts.RoundKinds.Append("other"))
            {
                var list = catalog.Weapons.Values.Where(w => BalancePackFacts.RoundKind(w) == kind).ToList();
                if (list.Count == 0) continue;
                float Share(Func<WeaponDef, bool> f) => list.Count(f) / (float)list.Count;
                rows.Add(new Dictionary<string, object>
                {
                    ["kind"] = kind, ["weapons"] = list.Count,
                    ["homing"] = Share(w => MachineBrigade.Sim.Combat.CombatSystem.Homes(w)),
                    ["flareTakes"] = Share(w => MachineBrigade.Sim.Combat.CombatSystem.FlareTakes(w, rules)),
                    ["apsEligible"] = Share(w => w.ApsEligible != false), ["ciwsEligible"] = Share(w => w.CiwsEligible != false),
                    ["interceptable"] = Share(w => w.Interceptable != false), ["warns"] = Share(w => catalog.Warnings.Warns(w)),
                    ["maxFlightSeconds"] = list.Max(w => BalancePackFacts.FlightSeconds(catalog, w, w.Range)),
                    ["splashing"] = Share(w => w.Splashes),
                });
            }
            return new Dictionary<string, object>
            {
                ["rules"] = new Dictionary<string, object>
                {
                    ["leadCapSeconds"] = rules.LeadCap, ["proximityFuzeM"] = rules.ProximityFuze, ["missReachScale"] = rules.ReachScale,
                    ["flareDecoyChance"] = rules.FlareDecoyChance,
                    ["onMiss"] = "a round past its range x reachScale self-destructs (Divert.Reach); a sight-guided missile whose shooter dies or loses sight (smoke, a wall) is lost (Divert.Sight)",
                    ["aim"] = "homing: guided, guided rocket, guided bomb, guided shell; else led (lead capped at leadCapSeconds)",
                },
                ["groups"] = rows,
            };
        }

        /// <summary>Dan_thay_the: when a gun switches round (the round's use), how long the switch takes and how long a want must hold.</summary>
        private static object PackSecondRounds(Catalog catalog)
        {
            var rows = new List<object>();
            foreach (var w in catalog.Weapons.Values.OrderBy(w => w.Id))
                foreach (var r in w.Rounds)
                    rows.Add(new Dictionary<string, object>
                    {
                        ["weapon"] = w.Id, ["round"] = r.Round.Id, ["use"] = r.Use.ToString(), ["eliteOnly"] = r.EliteOnly,
                        ["switchSeconds"] = w.SwitchSeconds(r),
                    });
            return new Dictionary<string, object>
            {
                ["minSwitchSeconds"] = WeaponDef.MinSwitchSeconds, ["roundHoldSeconds"] = WeaponDef.RoundHoldSeconds,
                ["rule"] = "the gun loads the round whose use fits the target (air, ground, armour, light, structure, cluster); a wanted change must hold roundHoldSeconds; the switch takes switchSeconds",
                ["rounds"] = rows,
            };
        }

        /// <summary>Phao_sang so_qua_moi_lan: flares one release puts out (the view's rule by size), with the charges and recharge.</summary>
        private static object PackFlares(Catalog catalog)
        {
            var rules = catalog.Munitions;
            var rows = new List<object>();
            foreach (var v in catalog.Vehicles.Values.OrderBy(v => v.Id))
            {
                var (kind, charges, recharge) = BalancePackFacts.SelfDefence(v);
                if (kind != "flare") continue;
                var size = v.Class == UnitClass.Helicopter ? "helicopter" : v.Radius >= 4f || v.Boss ? "large" : "fighter";
                var count = size == "helicopter" ? rules.FlaresHelicopter : size == "large" ? rules.FlaresLarge : rules.FlaresFighter;
                rows.Add(new Dictionary<string, object>
                {
                    ["id"] = v.Id, ["size"] = size, ["flaresMin"] = count.min, ["flaresMax"] = count.max, ["charges"] = charges,
                    ["rechargeSeconds"] = recharge,
                });
            }
            return rows;
        }

        /// <summary>Vu_khi.thoi_gian_bay_toi_tam_s_game: each weapon's flight at its full range, as the combat system launches it.</summary>
        private static object PackFlight(Catalog catalog) => catalog.Weapons.Values.OrderBy(w => w.Id).Select(w => (object)new Dictionary<string, object>
        {
            ["id"] = w.Id, ["range"] = w.Range, ["speed"] = w.ProjectileSpeed, ["warnSeconds"] = w.WarnSeconds, ["warns"] = catalog.Warnings.Warns(w),
            ["flightAtRangeSeconds"] = BalancePackFacts.FlightSeconds(catalog, w, w.Range),
        }).ToList();

        /// <summary>Xe and Xe_suy_ra: price group, factor, power bonus, drop time by group, in-battle health, self-defence and its recharge.</summary>
        private static object PackVehicles(Catalog catalog)
        {
            var rows = new List<object>();
            foreach (var v in catalog.Vehicles.Values.Where(v => !v.Boss && !v.Static).OrderBy(v => v.Id))
            {
                var splash = BalancePackFacts.IsSplashUnit(v);
                var (kind, charges, recharge) = BalancePackFacts.SelfDefence(v);
                rows.Add(new Dictionary<string, object>
                {
                    ["id"] = v.Id, ["baseCp"] = v.BaseCp, ["priceGroup"] = BalancePackFacts.PriceGroup(v.BaseCp),
                    ["priceFactor"] = BalancePackFacts.PriceFactor(v.BaseCp), ["splashUnit"] = splash,
                    ["powerBonus"] = BalancePackFacts.PowerBonus(v.BaseCp, splash), ["outgoingDamageMult"] = v.OutgoingDamageMult,
                    ["dropByGroupSeconds"] = BalancePackFacts.DropTimeByGroup(v.BaseCp), ["dropDelay"] = v.DropDelay,
                    ["hpInBattle"] = v.MaxHp, ["selfDefence"] = kind, ["selfDefenceCharges"] = charges, ["selfDefenceRechargeSeconds"] = recharge,
                    ["interceptionMode"] = v.Aps != null ? v.InterceptionMode.ToString() : "", ["apsCapability"] = v.ApsCapability.ToString(),
                    ["turnSeconds180"] = v.TurnRate > 0f ? MathF.PI / v.TurnRate : 0f,
                    ["turretSeconds180"] = v.TurretTurnRate > 0f ? MathF.PI / v.TurretTurnRate : 0f,
                    ["unlock"] = v.Elite ? new Dictionary<string, object>() : Unlock(catalog, v),
                });
            }
            return new Dictionary<string, object>
            {
                ["splashRule"] = "splash unit = main weapon fires indirectly (minimum range, lofted, bomb, drone) or glides",
                ["vehicles"] = rows,
            };
        }

        private static readonly (GameModeKind kind, string map)[] OpeningMaps =
        {
            (GameModeKind.Conquest, "ashfield"), (GameModeKind.Deathmatch, "greenvale"), (GameModeKind.KingOfTheHill, "dunebreak"),
            (GameModeKind.Assault, "redrock"), (GameModeKind.Siege, "ashfield"), (GameModeKind.Defend, "greenvale"),
            (GameModeKind.Endless, "ironport"), (GameModeKind.Survival, "frostpeak"), (GameModeKind.BossRush, "ashfield"),
            (GameModeKind.Showdown, "ashfield"),
        };

        /// <summary>
        /// Doi_mo_man_suy_ra.phan_tram_cp_khoi_dau: each mode's player opening squad as the game drops it (a fresh battle, seed
        /// 1, the starter deck): its cards, their baseCP and the share of the starting CP they took (at most openingSquads.share).
        /// </summary>
        private static object PackOpening(Catalog catalog)
        {
            var rows = new List<object>();
            var (mode, deck, supports, difficulty) = (MatchSettings.Mode, MatchSettings.DeckVehicles.ToList(), MatchSettings.DeckSupports.ToList(), MatchSettings.Difficulty);
            try
            {
                foreach (var (kind, map) in OpeningMaps)
                {
                    if (!catalog.Opening.AppliesTo(kind.ToString())) continue;
                    MatchSettings.Mode = kind;
                    MatchSettings.Difficulty = MachineBrigade.Sim.AI.AiDifficulty.Normal;
                    MatchSettings.DeckVehicles.Clear();
                    MatchSettings.DeckVehicles.AddRange(Progression.StarterVehicles);
                    BossRushSession.Pending = null;
                    var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(ModeSession.MapFile(kind, map)), seed: 1);
                    ModeSession.Create(kind, false, world, 1);
                    if (!world.TryGetEconomy(0, out var economy)) continue;
                    var squad = world.VehicleList.Where(x => x.IsAlive && x.Team == 0 && !x.Ally && !x.Def.Static && x.Def.BaseCp > 0)
                        .Select(x => x.Def).OrderBy(d => d.Id).ToList();
                    var spent = squad.Sum(d => d.BaseCp);
                    var start = economy.Cp + spent;
                    rows.Add(new Dictionary<string, object>
                    {
                        ["mode"] = kind.ToString(), ["startCp"] = start, ["squad"] = squad.Select(d => (object)d.Id).ToList(), ["squadCp"] = spent,
                        ["share"] = start > 0f ? spent / start : 0f, ["maxShare"] = catalog.Opening.Share,
                    });
                }
            }
            finally
            {
                MatchSettings.Mode = mode;
                MatchSettings.Difficulty = difficulty;
                MatchSettings.DeckVehicles.Clear();
                MatchSettings.DeckVehicles.AddRange(deck);
                MatchSettings.DeckSupports.Clear();
                MatchSettings.DeckSupports.AddRange(supports);
            }
            return rows;
        }

        /// <summary>03 boss: the time-to-kill targets, the hunt's draw rules and each boss's air defence.</summary>
        private static object PackBoss(Catalog catalog)
        {
            return new Dictionary<string, object>
            {
                ["timeToKillSeconds"] = new Dictionary<string, object>
                {
                    ["weeklyMini"] = SimTunables.Bosses.BossRushRules.MiniSeconds, ["weeklyMain"] = SimTunables.Bosses.BossRushRules.MainSeconds,
                    ["fullMini"] = SimTunables.Bosses.BossRushRules.FullMiniSeconds, ["fullMain"] = SimTunables.Bosses.BossRushRules.FullMainSeconds,
                    ["hpShare"] = SimTunables.Bosses.BossRushRules.HpShare,
                },
                ["compensation"] = NotApplicable("Boss_dps.cach_bu is a design call (DECISIONS: left to the owner); no rule in the code or the data"),
                ["hunt"] = new Dictionary<string, object>
                {
                    ["weeklyMains"] = BossHunt.WeeklyMains, ["weeklyMinis"] = BossHunt.WeeklyMinis, ["airDefenceMains"] = BossHunt.AirDefenceMains,
                    ["airDefenceMinis"] = BossHunt.AirDefenceMinis, ["fullFrom"] = BossHunt.FullFrom, ["fullTo"] = BossHunt.FullTo,
                    ["weeklyStep"] = BossHunt.WeeklyStep, ["weeklyMinutes"] = BossHunts.WeeklyMinutes,
                    ["bosses"] = BossHunts.Story.Select(b => (object)new Dictionary<string, object>
                    {
                        ["id"] = b.Id, ["main"] = b.Main, ["chapter"] = b.Chapter, ["airDefence"] = b.AirDefence,
                    }).ToList(),
                },
            };
        }

        /// <summary>Thap: the balance multiplier, the card a branch folds into, the unlock route and the self-defence recharge.</summary>
        private static object PackTowers(Catalog catalog) => catalog.Vehicles.Values.Where(v => v.Static && !v.Boss).OrderBy(v => v.Id).Select(v =>
        {
            var (kind, charges, recharge) = BalancePackFacts.SelfDefence(v);
            return (object)new Dictionary<string, object>
            {
                ["id"] = v.Id, ["card"] = v.CardId, ["outgoingDamageMult"] = v.OutgoingDamageMult,
                ["balanceCut"] = v.OutgoingDamageMult < 1f ? "giam_dps_giu_mau" : "",
                ["unlockRoute"] = Progression.Route(v.Id).ToString(), ["selfDefence"] = kind, ["selfDefenceCharges"] = charges,
                ["selfDefenceRechargeSeconds"] = recharge, ["turretSeconds180"] = v.TurretTurnRate > 0f ? MathF.PI / v.TurretTurnRate : 0f,
            };
        }).ToList();

        private static readonly string[] EconomyModes =
            { "Conquest", "Deathmatch", "KingOfTheHill", "Assault", "Siege", "Defend", "Endless", "Survival", "BossRush", "Campaign", "Showdown" };

        /// <summary>05 Kinh_te: the supply formula's numbers by mode, the upkeep curve, the catch-up, the refunds; Vo_han's reward growth.</summary>
        private static object PackEconomy(Catalog catalog)
        {
            var modes = EconomyModes.Select(m =>
            {
                var (data, cap, supply) = BalancePackFacts.SupplyLine(catalog, m);
                return (object)new Dictionary<string, object> { ["mode"] = m, ["armyCapData"] = data, ["armyCap"] = cap, ["supply"] = supply };
            }).ToList();
            var upkeep = new[] { 1f, 1.25f, 1.5f, 2f, 2.5f, 3f }.Select(x => (object)new Dictionary<string, object>
            {
                ["armyOverSupply"] = x, ["incomeKept"] = BalancePackFacts.Upkeep((int)MathF.Round(100f * x), 100),
            }).ToList();
            var catchUp = new[] { 1f, 0.75f, 0.6f, 0.5f, 0.4f, 0.3f, 0.2f, 0.1f }.Select(x => (object)new Dictionary<string, object>
            {
                ["ownOverRival"] = x, ["incomeBoost"] = BalancePackFacts.CatchUp((int)MathF.Round(100f * x), 100),
            }).ToList();
            return new Dictionary<string, object>
            {
                ["formula"] = "armyCap = round((economy.armyCap[mode] x supplyPriceScale + bonus) x economy.supply x commander); supply = floor(armyCap x supplyPerArmyCap); " +
                              "income kept = max(upkeepFloor, 1 - upkeepSlope x (army - supply) / supply) above the supply",
                ["supplyScale"] = catalog.SupplyScale, ["supplyPriceScale"] = SimTunables.Modes.EconomyRules.SupplyPriceScale,
                ["supplyPerArmyCap"] = SimTunables.Modes.EconomyRules.SupplyPerArmyCap, ["upkeepSlope"] = SimTunables.Modes.EconomyRules.UpkeepSlope,
                ["upkeepFloor"] = SimTunables.Modes.EconomyRules.UpkeepFloor, ["modes"] = modes, ["upkeepCurve"] = upkeep, ["catchUpCurve"] = catchUp,
                ["killShare"] = BalancePackFacts.KillShare(), ["killRefundCap"] = SimTunables.Modes.EconomySystem.KillRefundCap,
                ["lossRefundCap"] = SimTunables.Modes.EconomySystem.LossRefundCap,
                ["endless"] = new Dictionary<string, object>
                {
                    ["enemyPerWave"] = EndlessRules.EnemyPerWave, ["enemyPerBoss"] = EndlessRules.EnemyPerBoss, ["playerPerWave"] = EndlessRules.PlayerPerWave,
                    ["playerMax"] = EndlessRules.PlayerMax, ["coinDecay"] = EndlessRules.CoinDecay, ["waveCoins"] = EndlessRules.WaveCoins,
                    ["bossCoins"] = EndlessRules.BossCoins, ["dailyCap"] = EndlessRules.DailyCap,
                    ["coinsByStep"] = Enumerable.Range(0, 10).Select(k => (object)EndlessRules.Coins(k)).ToList(),
                    ["enemyScaleByStep"] = Enumerable.Range(0, 10).Select(k => (object)EndlessRules.EnemyScale(k)).ToList(),
                },
            };
        }

        /// <summary>07 Thoai / Nhan_vat / Trigger_thoai: portraits, the triggers' counts and gaps, the most lines a line wraps to.</summary>
        private static object PackDialogue(Catalog catalog)
        {
            var script = ScriptText.Script;
            var speakers = script.Speakers.Keys.OrderBy(k => k, StringComparer.Ordinal).Select(id => (object)new Dictionary<string, object>
            {
                ["id"] = id, ["portrait"] = Portraits.Find(id) != null,
            }).ToList();
            var characters = new[] { "khai", "mai", "dieuhau", "linh", "hung", "varga", "orlov", "kessler", "sen", "quaden", "aurel" }
                .Select(id => (object)new Dictionary<string, object> { ["id"] = id, ["portrait"] = Portraits.Find(id) != null }).ToList();
            var triggers = script.All.GroupBy(l => l.TriggerKey).OrderBy(g => g.Key, StringComparer.Ordinal).Select(g => (object)new Dictionary<string, object>
            {
                ["trigger"] = g.Key, ["lines"] = g.Count(), ["onceLines"] = g.Count(l => l.Once), ["repeatLines"] = g.Count(l => !l.Once),
            }).ToList();
            var genericGap = typeof(RadioDirector).GetField("GenericGap", BindingFlags.NonPublic | BindingFlags.Static)?.GetValue(null);
            return new Dictionary<string, object>
            {
                ["speakers"] = speakers, ["characters"] = characters, ["triggers"] = triggers,
                ["countRule"] = "a line marked once plays once a battle; the rest repeat after the gaps",
                ["gapsSeconds"] = new Dictionary<string, object>
                {
                    ["dialogue"] = DialogueDirector.Gap, ["boss"] = DialogueDirector.BossGap, ["radioGeneric"] = genericGap is double d ? d : 0.0,
                    ["reactiveRadio"] = ReactiveRadio.Gap,
                },
                ["maxVisibleLines"] = PackDialogueLines(script),
            };
        }

        /// <summary>
        /// Thoai.so_dong_hien_thi_toi_da: the most lines one dialogue line wraps to in the narrowest strip (the HUD's 1280 x 720
        /// reference at the largest UI size, the strip beside the open selection panel, large text, a portrait), measured with
        /// the UI font's own glyph advances (Barlow Regular through UnityEngine.Font: UI Toolkit's text engine needs a live
        /// panel, so this is the font metrics' word wrap, not the engine's).
        /// </summary>
        private static object PackDialogueLines(StoryScript script)
        {
            const float fontSize = 29f;           // Tokens.uss: --fc-fs-dialogue in .fc-text-large
            const float portrait = 52f + 8f;      // Screens.uss: the large-text portrait and its margin (--fc-space-2)
            const float padding = 2f * 12f;       // Screens.uss: the strip's side padding (--fc-space-3)
            var logicalWidth = 1280f / 1.1f;      // BattleHud: ScaleWithScreenSize 1280 x 720 (4:3 and 16:9 keep 1280 wide), UI size x1.1
            var raisedStrip = logicalWidth - 12f - 720f; // Screens.uss .fc-dialogue--raised: left 12 px, right 720 px
            var normalStrip = logicalWidth * 0.5f;       // .fc-dialogue: left 25 %, right 25 %
            var font = Resources.Load<Font>("Fonts/Barlow-Regular");
            var method = "UnityEngine.Font glyph advances";
            float Advance(char c)
            {
                if (font != null && font.GetCharacterInfo(c, out var info, (int)fontSize)) return info.advance;
                method = "estimate: 0.5 em a glyph (font metrics unavailable)";
                return fontSize * 0.5f;
            }
            int Lines(string text, float width)
            {
                if (font != null) font.RequestCharactersInTexture(text, (int)fontSize);
                var lines = 1;
                var x = 0f;
                var space = Advance(' ');
                foreach (var word in text.Split(' '))
                {
                    var w = word.Sum(Advance);
                    if (x > 0f && x + space + w > width)
                    {
                        lines++;
                        x = 0f;
                    }
                    x += (x > 0f ? space : 0f) + w;
                    while (x > width)
                    {
                        lines++;
                        x -= width;
                    }
                }
                return lines;
            }
            var result = new Dictionary<string, object>();
            foreach (var (label, strip) in new[] { ("raised", raisedStrip), ("normal", normalStrip) })
            {
                var width = strip - padding - portrait;
                var maxVi = 0;
                var maxEn = 0;
                var overTwo = 0;
                var worst = "";
                foreach (var line in script.All)
                {
                    var name = Strings.Has("char." + line.Speaker + ".name") ? Strings.Get("char." + line.Speaker + ".name") + ": " : "";
                    var vi = Lines(name + line.Vi, width);
                    var en = Lines(name + line.En, width);
                    if (vi > 2 || en > 2) overTwo++;
                    if (vi > maxVi)
                    {
                        maxVi = vi;
                        worst = line.Key;
                    }
                    maxEn = Math.Max(maxEn, en);
                }
                result[label] = new Dictionary<string, object>
                {
                    ["textWidthPx"] = width, ["maxLinesVi"] = maxVi, ["maxLinesEn"] = maxEn, ["linesOverTwo"] = overTwo, ["worstKey"] = worst,
                };
            }
            result["fontSizePx"] = fontSize;
            result["method"] = method;
            return result;
        }

        /// <summary>07 Nhiem_vu.trang_thai_kich_ban and Bo_bai_game: each mission's script lines and deck rules.</summary>
        private static object PackMissions()
        {
            var script = ScriptText.Script;
            return Campaign.All.Select(m =>
            {
                var lines = script.For(m.Id).Count;
                return (object)new Dictionary<string, object>
                {
                    ["id"] = m.Id, ["scriptLines"] = lines, ["scriptStatus"] = lines > 0 ? "co_kich_ban" : "chua_co_kich_ban",
                    ["mainSpeaker"] = script.MainSpeaker(m.Id) ?? "", ["fixedDeck"] = MissionDecks.IsFixed(m),
                    ["deckGoal"] = "KHONG_AP_DUNG: no kept-goal field in the code (MissionDecks has the fixed deck, the air minimum and the loans)",
                };
            }).ToList();
        }

        /// <summary>07 Ket_tran: the match end's presentation by kind.</summary>
        private static object PackMatchEnd() => new Dictionary<string, object>
        {
            ["skipAfterSeconds"] = MatchEnd.SkipAfter,
            ["kinds"] = Enum.GetValues(typeof(EndKind)).Cast<EndKind>().Select(k => (object)new Dictionary<string, object>
            {
                ["kind"] = k.ToString(), ["seconds"] = MatchEnd.DurationFor(k), ["slowMotion"] = k != EndKind.Loss && k != EndKind.Replay,
            }).ToList(),
        };

        /// <summary>07 Cutscene_khoanh_khac: the battle's cinematic moments (on by default) and their timing.</summary>
        private static object PackCutscene() => new Dictionary<string, object>
        {
            ["cinematicMoments"] = MatchSettings.CinematicMoments, ["momentMaxSeconds"] = DialogueDirector.MomentMax,
            ["easeInSeconds"] = DialogueDirector.MomentEaseIn, ["easeOutSeconds"] = DialogueDirector.MomentEaseOut,
            ["momentScale"] = DialogueDirector.MomentScale,
        };

        /// <summary>09 Am_thanh_mixer / Am_thanh_thu_vien: the mix groups and default volumes, the sound banks on disk.</summary>
        private static object PackAudio()
        {
            var root = Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Audio");
            var banks = Directory.Exists(root)
                ? Directory.GetDirectories(root).Select(d => (object)new Dictionary<string, object>
                {
                    ["bank"] = Path.GetFileName(d),
                    ["files"] = Directory.GetFiles(d).Count(f => !f.EndsWith(".meta", StringComparison.Ordinal)),
                }).OrderBy(x => (string)((Dictionary<string, object>)x)["bank"], StringComparer.Ordinal).ToList()
                : new List<object>();
            return new Dictionary<string, object>
            {
                ["groups"] = Enum.GetNames(typeof(AudioCode.AudioGroup)).Cast<object>().ToList(),
                ["volumes"] = new Dictionary<string, object>
                {
                    ["master"] = MatchSettings.Volume, ["music"] = MatchSettings.MusicVolume, ["effects"] = MatchSettings.EffectsVolume,
                    ["dialogue"] = MatchSettings.DialogueVolume,
                },
                ["library"] = banks,
            };
        }

        /// <summary>09 Xac_vo: how long wrecks stay, by graphics tier, and how many stay whole.</summary>
        private static object PackWrecks(Catalog catalog)
        {
            var tank = catalog.Vehicles["main_battle_tank"];
            var boss = catalog.Vehicles.Values.Where(v => v.Boss).OrderBy(v => v.Id).First();
            return new[] { GraphicsQuality.Low, GraphicsQuality.Medium, GraphicsQuality.High }.Select(t => (object)new Dictionary<string, object>
            {
                ["tier"] = t.ToString(), ["fullCap"] = FxCode.WreckClasses.FullCap(t),
                ["lifeMinSeconds"] = FxCode.WreckClasses.Life(tank, 0f, t), ["lifeMaxSeconds"] = FxCode.WreckClasses.Life(tank, 1f, t),
                ["bossLifeSeconds"] = FxCode.WreckClasses.Life(boss, 0.5f, t),
            }).ToList();
        }

        /// <summary>11 Cai_dat_mac_dinh: the settings as the game starts them (MatchSettings' initial values; the export loads no save).</summary>
        private static object PackSettings() => new Dictionary<string, object>
        {
            ["volume"] = MatchSettings.Volume, ["musicVolume"] = MatchSettings.MusicVolume, ["effectsVolume"] = MatchSettings.EffectsVolume,
            ["dialogueVolume"] = MatchSettings.DialogueVolume, ["graphics"] = MatchSettings.Graphics.ToString(), ["screenShake"] = MatchSettings.ScreenShake,
            ["haptics"] = MatchSettings.Haptics, ["colorBlind"] = MatchSettings.ColorBlind, ["cinematicMoments"] = MatchSettings.CinematicMoments,
            ["dialogue"] = MatchSettings.Dialogue.ToString(), ["cameraSpeed"] = MatchSettings.CameraSpeed, ["batterySaver"] = MatchSettings.BatterySaver,
            ["brightness"] = MatchSettings.Brightness, ["uiSize"] = MatchSettings.UiSize, ["textSize"] = MatchSettings.TextSize.ToString(),
            ["showFps"] = MatchSettings.ShowFps, ["aiHints"] = MatchSettings.AiHints, ["language"] = MatchSettings.Language.ToString(),
            ["autoDeploy"] = MatchSettings.AutoDeploy, ["autoStrike"] = MatchSettings.AutoStrike, ["compactHud"] = MatchSettings.CompactHud,
            ["showCombatNumbers"] = MatchSettings.ShowCombatNumbers,
        };
    }
}
