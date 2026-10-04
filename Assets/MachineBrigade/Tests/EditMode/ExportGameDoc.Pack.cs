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
            Section("strikes", () => PackStrikes(catalog));
            Section("defenceWaves", () => PackDefenceWaves(catalog));
            Section("drones", () => PackDrones(catalog));
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
            (Dictionary<string, object> blocks, Dictionary<string, object> shares) Blocks(VehicleDef carrier, ApsDef system)
            {
                var blocked = new Dictionary<string, object>();
                var shellShares = new Dictionary<string, object>();
                foreach (var kind in BalancePackFacts.RoundKinds)
                {
                    var list = byKind[kind];
                    var taken = 0;
                    var share = 1f;
                    foreach (var w in list)
                        if (BalancePackFacts.MayIntercept(carrier, system, w, out var s))
                        {
                            taken++;
                            share = Math.Min(share, s);
                        }
                    blocked[kind] = list.Count == 0 ? "khong_co_dan" : taken == 0 ? "khong" : taken == list.Count ? "co" : "mot_phan:" + taken + "/" + list.Count;
                    shellShares[kind] = taken > 0 ? share : 0f;
                }
                return (blocked, shellShares);
            }
            var carriers = new List<object>();
            foreach (var v in catalog.Vehicles.Values.Where(v => v.Aps != null).OrderBy(v => v.Id))
            {
                var a = v.Aps!;
                var (blocks, shares) = Blocks(v, a);
                carriers.Add(new Dictionary<string, object>
                {
                    ["id"] = v.Id, ["mode"] = v.InterceptionMode.ToString(), ["static"] = v.Static, ["boss"] = v.Boss,
                    ["radius"] = a.Radius, ["charges"] = a.Charges, ["recharge"] = a.Recharge, ["burst"] = a.Burst, ["heavy"] = a.Heavy,
                    ["rockets"] = a.Rockets, ["shells"] = a.Shells, ["direct"] = a.Direct, ["laser"] = a.Laser,
                    ["blocks"] = blocks, ["shellShare"] = shares,
                });
            }
            // The Trophy module (GearSystem.TrophyAps): the APS a RETROFIT_ELIGIBLE vehicle has only with it, and a BUILT_IN
            // one's improved APS. Only flares and APS are a vehicle's self-defence: this is APS, fitted as an upgrade.
            var upgrades = new List<object>();
            foreach (var v in catalog.Vehicles.Values.Where(v => v.ApsCapability != ApsCapability.None).OrderBy(v => v.Id))
            {
                if (MachineBrigade.Sim.Abilities.GearSystem.TrophyAps(v) is not { } trophy) continue;
                var (blocks, shares) = Blocks(v, trophy);
                upgrades.Add(new Dictionary<string, object>
                {
                    ["id"] = v.Id, ["module"] = "trophy_aps", ["capability"] = v.ApsCapability.ToString(), ["baseHasAps"] = v.Aps != null,
                    ["radius"] = trophy.Radius, ["charges"] = trophy.Charges, ["recharge"] = trophy.Recharge,
                    ["blocks"] = blocks, ["shellShare"] = shares,
                });
            }
            return new Dictionary<string, object>
            {
                ["kinds"] = BalancePackFacts.RoundKinds.Cast<object>().ToList(),
                ["note"] = "static rules of DamageSystem.TryIntercept / GunTakes (reach, interceptors left, smoke and rolls left out)",
                ["carriers"] = carriers,
                ["upgrades"] = upgrades,
            };
        }

        /// <summary>Hanh_vi_dan_nhom: per round kind, how its rounds aim, warn and fly, and what flares and APS do to them.</summary>
        private static object PackRoundGroups(Catalog catalog)
        {
            var rules = catalog.Munitions;
            Dictionary<string, object> Group(string key, string name, List<WeaponDef> members)
            {
                float Share(Func<WeaponDef, bool> f) => members.Count(f) / (float)members.Count;
                return new Dictionary<string, object>
                {
                    [key] = name, ["weapons"] = members.Count,
                    ["homing"] = Share(w => MachineBrigade.Sim.Combat.CombatSystem.Homes(w)),
                    ["flareTakes"] = Share(w => MachineBrigade.Sim.Combat.CombatSystem.FlareTakes(w, rules)),
                    ["apsEligible"] = Share(w => w.ApsEligible != false), ["ciwsEligible"] = Share(w => w.CiwsEligible != false),
                    ["interceptable"] = Share(w => w.Interceptable != false), ["warns"] = Share(w => catalog.Warnings.Warns(w)),
                    ["maxFlightSeconds"] = members.Max(w => BalancePackFacts.FlightSeconds(catalog, w, w.Range)),
                    ["splashing"] = Share(w => w.Splashes), ["jamTakes"] = Share(BalancePackFacts.JamTakes),
                };
            }
            var rows = new List<object>();
            foreach (var kind in BalancePackFacts.RoundKinds.Append("other"))
            {
                var list = catalog.Weapons.Values.Where(w => BalancePackFacts.RoundKind(w) == kind).ToList();
                if (list.Count == 0) continue;
                rows.Add(Group("kind", kind, list));
            }
            // Hanh_vi_dan_nhom's own rows: one per projectile kind (the sheet's grouping), so each row carries its own numbers.
            var byProjectile = new List<object>();
            foreach (var projectile in Enum.GetValues(typeof(ProjectileKind)).Cast<ProjectileKind>())
            {
                var list = catalog.Weapons.Values.Where(w => w.Projectile == projectile).ToList();
                if (list.Count == 0) continue;
                byProjectile.Add(Group("projectile", projectile.ToString(), list));
            }
            return new Dictionary<string, object>
            {
                ["rules"] = new Dictionary<string, object>
                {
                    ["leadCapSeconds"] = rules.LeadCap, ["proximityFuzeM"] = rules.ProximityFuze, ["missReachScale"] = rules.ReachScale,
                    ["flareDecoyChance"] = rules.FlareDecoyChance,
                    ["jamMissMinM"] = SimTunables.Weapons.JamRules.GuidedMissMin, ["jamMissSpreadM"] = SimTunables.Weapons.JamRules.GuidedMissSpread,
                    ["jamStrikeScatter"] = SimTunables.Weapons.JamRules.StrikeScatter, ["jamSwarmChance"] = SimTunables.Weapons.JamRules.SwarmJamChance,
                    ["jam"] = "a guided round (missile, drone) fired from or at a point inside an enemy jammer's radius lands jamMissMinM + up to " +
                              "jamMissSpreadM m off (jamProof weapons and a commander's drone perk excepted); fire support called into the bubble " +
                              "lands jamStrikeScatter times as wide; a boss's swarm drone over it loses its target at jamSwarmChance",
                    ["onMiss"] = "a round past its range x reachScale self-destructs (Divert.Reach); a sight-guided missile whose shooter dies or loses sight (smoke, a wall) is lost (Divert.Sight)",
                    ["aim"] = "homing: guided, guided rocket, guided bomb, guided shell; else led (lead capped at leadCapSeconds)",
                },
                ["groups"] = rows,
                ["projectileGroups"] = byProjectile,
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
                if (kind != "flare")
                {
                    // A flare tower's illumination flare (FieldWorksSystem.Flares): one flare a release, every Flares.Every s, at night.
                    if (v.Flares is { } lit)
                        rows.Add(new Dictionary<string, object>
                        {
                            ["id"] = v.Id, ["size"] = "illumination", ["flaresMin"] = 1, ["flaresMax"] = 1, ["charges"] = 0,
                            ["rechargeSeconds"] = lit.Every, ["litRadius"] = lit.Radius, ["litSeconds"] = lit.Seconds, ["range"] = lit.Range,
                        });
                    continue;
                }
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
                    ["weekRule"] = "week = ISO year x 100 + ISO week (WeeklyFortress.Week, UTC); run = BossHunts.Weekly(week), the same on every device",
                    ["weeksYear"] = HuntYear,
                    ["weeks"] = Enumerable.Range(1, ISOWeek.GetWeeksInYear(HuntYear)).Select(k => (object)new Dictionary<string, object>
                    {
                        ["week"] = HuntYear * 100 + k, ["run"] = BossHunts.Weekly(HuntYear * 100 + k).Cast<object>().ToList(),
                    }).ToList(),
                    ["bosses"] = BossHunts.Story.Select(b => (object)new Dictionary<string, object>
                    {
                        ["id"] = b.Id, ["main"] = b.Main, ["chapter"] = b.Chapter, ["airDefence"] = b.AirDefence,
                    }).ToList(),
                },
            };
        }

        /// <summary>The ISO year whose weeks the export lists for the Boss Hunt's weekly run (fixed, so the pack does not change by date).</summary>
        private const int HuntYear = 2026;

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
            // Each line's most lines (Vietnamese or English, either strip): Thoai.so_dong_hien_thi_toi_da per row.
            var perLine = new SortedDictionary<string, object>(StringComparer.Ordinal);
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
                    var most = Math.Max(vi, en);
                    if (!perLine.TryGetValue(line.Key, out var before) || (before is int was && was < most)) perLine[line.Key] = most;
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
            result["perLine"] = perLine;
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

        /// <summary>
        /// 01 Bom_vu_khi / Bom_don_vi / Bom_canh_bao: each support's damage type, blast edge and rim share and the height the
        /// view drops its bombs from; each big attack's strikes (core, edge layer, its share, falloff); each bomb carrier's
        /// rearm (a boss carries no load, so it never goes back to rearm).
        /// </summary>
        private static object PackStrikes(Catalog catalog)
        {
            // Splash 04/10: a one-radius blast has no core; its rim share is the splash row's last band before the edge (step 7, 0.25).
            var rim = catalog.Damage.SplashStep(7);
            var supports = catalog.Supports.Values.OrderBy(s => s.Id, StringComparer.Ordinal).Select(s => (object)new Dictionary<string, object>
            {
                ["id"] = s.Id, ["kind"] = s.Kind.ToString(), ["type"] = s.DamageType.ToString(), ["thermobaric"] = s.Thermobaric,
                ["blastRadius"] = s.BlastRadius, ["edgeRadius"] = 0f, ["rimShare"] = s.Thermobaric ? (1f + rim) * 0.5f : rim,
                ["releaseAltitude"] = FxCode.StrikeEffects.ReleaseAltitude(s),
            }).ToList();
            var big = catalog.BigAttacks.Values.OrderBy(b => b.Id, StringComparer.Ordinal).Select(b => (object)new Dictionary<string, object>
            {
                ["id"] = b.Id,
                ["strikes"] = b.Strikes.Select(st => (object)new Dictionary<string, object>
                {
                    ["shape"] = st.Shape.ToString(), ["type"] = st.Type.ToString(), ["radius"] = st.Radius, ["edgeRadius"] = st.EdgeRadius,
                    ["edgeShare"] = st.EdgeShare, ["falloff"] = st.Falloff,
                }).ToList(),
            }).ToList();
            var carriers = new List<object>();
            foreach (var v in catalog.Vehicles.Values.OrderBy(v => v.Id, StringComparer.Ordinal))
            {
                var bombs = v.Mounts.Select(m => m.Weapon).Where(w => w.Projectile == ProjectileKind.Bomb).Distinct().ToList();
                if (bombs.Count == 0) continue;
                carriers.Add(new Dictionary<string, object>
                {
                    ["id"] = v.Id, ["boss"] = v.Boss, ["flying"] = v.Flying, ["rearmSeconds"] = v.RearmTime,
                    ["loaded"] = bombs.Any(w => v.LoadOf(w) > 0), ["bombs"] = bombs.Select(w => (object)w.Id).ToList(),
                });
            }
            return new Dictionary<string, object>
            {
                ["supportRule"] = "a support strike's blast (StrikeSystem.Land, the cluster bomblets) calls DamageSystem.Splash with no edge layer: full " +
                                  "damage at the centre falling to rimShare at the blast radius (edgeRadius 0)",
                ["bigRule"] = "a big attack's blast has the core (radius, full damage) and the edge layer (edgeRadius, edgeShare of it); with no edge it falls to falloff at the rim",
                ["altitudeRule"] = "releaseAltitude is the view's (StrikeEffects): the simulation lands the bombs on its own schedule; 0: no aircraft drops them",
                ["supports"] = supports, ["bigAttacks"] = big, ["carriers"] = carriers,
            };
        }

        /// <summary>
        /// 01 Drone (play-test 13): every drone the game flies. A drone round (an FPV, Lancet or Shahed a vehicle sends): its
        /// speed, warhead, blast core and edge, flight to full range, the model it is drawn with and how much bigger than that
        /// model (WeaponEffects: RoundScale or projectileScale, x SizeOf, x QuadScale for the quadcopter) and its blast drawn
        /// (BlastSizes.Drone). A drone aircraft: speed, height, health and weapons.
        /// </summary>
        private static object PackDrones(Catalog catalog)
        {
            var rounds = new List<object>();
            foreach (var w in catalog.Weapons.Values.Where(w => w.Projectile == ProjectileKind.Drone).OrderBy(w => w.Id, StringComparer.Ordinal))
            {
                var model = w.ProjectileModel ?? "fpv_drone";
                var quad = model == "fpv_drone";
                rounds.Add(new Dictionary<string, object>
                {
                    ["id"] = w.Id, ["speed"] = w.ProjectileSpeed, ["damage"] = w.Damage, ["warheadKg"] = w.WarheadKg, ["splash"] = w.SplashRadius,
                    ["edge"] = w.SplashEdge, ["range"] = w.Range, ["flightAtRangeSeconds"] = BalancePackFacts.FlightSeconds(catalog, w, w.Range),
                    ["model"] = model, ["roundLength"] = w.RoundLength, ["projectileScale"] = w.ProjectileScale,
                    ["drawnScale"] = FxCode.WeaponEffects.SizeOf(w, ProjectileKind.Drone, model, false) * (quad ? FxCode.WeaponEffects.QuadScale : 1f),
                    ["blastDrawScale"] = FxCode.BlastSizes.Drone(w),
                });
            }
            var craft = catalog.Vehicles.Values.Where(v => v.Drone).OrderBy(v => v.Id, StringComparer.Ordinal).Select(v => (object)new Dictionary<string, object>
            {
                ["id"] = v.Id, ["speed"] = v.Speed, ["altitude"] = v.Altitude, ["hp"] = v.MaxHp,
                ["weapons"] = v.Mounts.Select(m => (object)m.Weapon.Id).Distinct().ToList(),
            }).ToList();
            return new Dictionary<string, object>
            {
                ["rule"] = "drawn length = (roundLength if set, else the model's length x projectileScale) x drawnScale",
                ["rounds"] = rounds, ["craft"] = craft,
            };
        }

        /// <summary>
        /// 04 Dot_phong_thu: each HQ level's reference base (BaseStrength.ReferencePower / ReferenceScore), the waves' size
        /// factor it gives (BaseStrength.WaveScale; the attacker's income x its square root) and Defend's wave curve by
        /// difficulty (SiegeMode.WaveSize with the session's numbers, tunables modes.defendWaves), outside a campaign mission.
        /// </summary>
        private static object PackDefenceWaves(Catalog catalog)
        {
            var difficulties = new[] { MachineBrigade.Sim.AI.AiDifficulty.Easy, MachineBrigade.Sim.AI.AiDifficulty.Normal, MachineBrigade.Sim.AI.AiDifficulty.Hard };
            var waveCount = EndlessRules.DefendFiniteWaves;
            var levels = new List<object>();
            for (var level = 1; level <= catalog.Base.MaxLevel; level++)
            {
                var score = BaseStrength.ReferenceScore(catalog, level);
                var scale = BaseStrength.WaveScale(score);
                var curves = new Dictionary<string, object>();
                foreach (var difficulty in difficulties)
                {
                    var start = SiegeMode.DefendWaveStart(false, difficulty);
                    var growth = SiegeMode.DefendWaveGrowth(false, difficulty);
                    curves[difficulty.ToString()] = Enumerable.Range(1, waveCount).Select(wave => (object)SiegeMode.WaveSize(start, growth,
                        SiegeMode.DefendWaveCompound(false), SiegeMode.DefendWaveMax, scale, wave)).ToList();
                }
                levels.Add(new Dictionary<string, object>
                {
                    ["level"] = level, ["referencePower"] = BaseStrength.ReferencePower(catalog, level), ["referenceScore"] = score,
                    ["waveScale"] = scale, ["incomeScale"] = MathF.Sqrt(scale), ["waves"] = curves,
                });
            }
            return new Dictionary<string, object>
            {
                ["rule"] = "wave n = min(waveMax, round((start + growth x (n - 1)) x waveScale)); waveScale = clamp((referenceScore / 100) ^ " +
                           "exponent, min, max) x the campaign progress factor (1 here); Hard covers Very Hard",
                ["waveCount"] = waveCount, ["levels"] = levels,
            };
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
