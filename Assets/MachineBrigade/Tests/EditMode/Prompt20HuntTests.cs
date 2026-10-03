using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 20, pass 3 (DECISIONS 19N), the cheap checks of part P: the week's Boss Hunt drawn by the week, the full
    /// hunt in story order, chapters switched off left out, checkpoints and their resume, the combat supports, every
    /// boss's rank and general, no old names, and the six missions moved onto the two new battlefields.
    /// </summary>
    public class Prompt20HuntTests
    {
        private const float Step = 0.05f;

        [TearDown]
        public void Restore()
        {
            Campaign.Release = null;
            Progression.TestUnlockAll = true;
            PlayerProfile.Load();
        }

        // ------------------------------------------------------------------ N.1: the week's hunt

        [Test]
        public void TheWeeksHuntIsDrawnByTheWeek()
        {
            // The draw alone, on a made-up story: 3 mains, 7 minis, three minis before the first main and two before each of the others (prompt 26 E.2: mains at 4, 7 and 10).
            var story = new List<HuntBoss>();
            for (var c = 1; c <= 12; c++)
            {
                story.Add(new HuntBoss($"mini{c}a", false, c));
                story.Add(new HuntBoss($"mini{c}b", false, c));
                story.Add(new HuntBoss($"main{c}", true, c));
            }
            var runs = new HashSet<string>();
            for (var week = 202601; week <= 202608; week++)
            {
                var run = BossHunt.Weekly(week, story);
                CollectionAssert.AreEqual(run, BossHunt.Weekly(week, story), "the same week draws the same run");
                Assert.AreEqual(10, run.Count);
                CollectionAssert.AllItemsAreUnique(run);
                var mains = Enumerable.Range(0, run.Count).Where(i => run[i].StartsWith("main")).ToList();
                CollectionAssert.AreEqual(new[] { 3, 6, 9 }, mains, "minis lead to each main boss: " + string.Join(",", run));
                // Each group's minis and the mains keep story order.
                var order = run.Select(id => story.FindIndex(b => b.Id == id)).ToList();
                Assert.That(mains.Select(i => order[i]), Is.Ordered);
                runs.Add(string.Join(",", run));
            }
            Assert.Greater(runs.Count, 4, "the run changes from week to week");
            Assert.AreEqual(1f, BossHunt.Multiplier(0, 1, false));
            Assert.That(Enumerable.Range(0, 10).Select(i => BossHunt.Multiplier(i, 10, false)), Is.Ordered, "stronger down the run");
            Assert.AreEqual(1.54f, BossHunt.Multiplier(9, 10, false), 1e-4f, "prompt 26 E.2: 1 + 0.06 (i - 1), x1.0 to x1.54");
            Assert.AreEqual(0.8f, BossHunt.Multiplier(0, 33, true), 1e-4f, "prompt 26 E.3: the full hunt, x0.8 to x1.3");
            Assert.AreEqual(1.3f, BossHunt.Multiplier(32, 33, true), 1e-4f);

            // This build's: from the chapter slots, every boss a boss of its rank; play-test 6 (DECISIONS 21G): the trains may
            // come (on their line's battlefield), and every week brings bosses that answer aircraft.
            var catalog = GameContent.LoadCatalog();
            for (var week = 202640; week <= 202652; week++)
            {
                var real = BossHunts.Weekly(week);
                Assert.AreEqual(10, real.Count);
                Assert.AreEqual(3, BossHunts.MainsIn(real));
                foreach (var id in real)
                {
                    Assert.IsTrue(catalog.Vehicles[id].Boss, id);
                    if (BossHunts.OnRails(catalog.Vehicles[id])) Assert.IsNotNull(catalog.Vehicles[id].Arena, id + " has a battlefield with its line");
                }
                var air = real.Where(id => BossHunts.AirDefence(catalog.Vehicles[id])).ToList();
                Assert.GreaterOrEqual(air.Count(id => catalog.Vehicles[id].Rank == BossRank.Main), BossHunt.AirDefenceMains, week + ": " + string.Join(",", real));
                Assert.GreaterOrEqual(air.Count(id => catalog.Vehicles[id].Rank == BossRank.Mini), BossHunt.AirDefenceMinis, week + ": " + string.Join(",", real));
            }
        }

        // ------------------------------------------------------------------ N.2: the full hunt; C: chapters switched off

        [Test]
        public void TheFullHuntIsEveryBossInStoryOrder()
        {
            var story = BossHunts.Story;
            var full = BossHunts.Full;
            CollectionAssert.AreEqual(story.Select(b => b.Id), full);
            // Prompt 22: in the order of play (an interlude, numbered 13-15, comes after the chapter before it).
            var order = Campaign.Chapters.Select(c => c.Number).ToList();
            Assert.That(story.Select(b => order.IndexOf(b.Chapter)), Is.Ordered);
            // Every chapter slot with a def, the trains and the railway gun too (DECISIONS 21G).
            var catalog = GameContent.LoadCatalog();
            var slots = Campaign.Chapters.SelectMany(c => c.Minis.Append(c.Main)).Where(id => id != null && catalog.Vehicles.ContainsKey(id)).Distinct().ToList();
            // Prompt 22 E: the new mini bosses no chapter lists yet come in at their interludes.
            slots.AddRange(BossHunts.Unslotted.Select(u => u.id).Where(id => !slots.Contains(id)));
            CollectionAssert.AreEquivalent(slots, full, "every chapter slot once, the trains and the railway gun too (DECISIONS 21G)");
            // Play-test 14: eleven chapter mains (Moloch holds chapters 6 and 8), Monster in chapter 11's mini slot, Kraken and Hyperion.
            Assert.AreEqual(14, story.Count(b => b.Main), "the main bosses of the hunts");
            // It opens once the last chapter on is done.
            PlayerProfile.ResetForTests();
            Progression.TestUnlockAll = false;
            Assert.IsFalse(BossHunts.FullOpen);
            PlayerProfile.RecordMission(Campaign.OperationOf(Campaign.LastChapter).Id, 1);
            Assert.IsTrue(BossHunts.FullOpen);
        }

        [TestCase(2)]
        [TestCase(3)]
        public void ChaptersSwitchedOffAreLeftOut(int lastAct)
        {
            var every = BossHunts.Full.Count;
            Campaign.Release = CampaignRelease.UpTo(lastAct);
            // Prompt 22: by act (an interlude goes with the act before it).
            Assert.IsTrue(BossHunts.Story.All(b => Campaign.Chapter(b.Chapter).Act <= lastAct));
            var onlyOff = Campaign.Chapters.Where(c => c.Act > lastAct).SelectMany(c => c.Minis.Append(c.Main))
                .Except(Campaign.Chapters.Where(c => c.Act <= lastAct).SelectMany(c => c.Minis.Append(c.Main))).ToList();
            foreach (var week in new[] { 202640, 202641, 202642 })
                foreach (var id in BossHunts.Weekly(week))
                {
                    CollectionAssert.DoesNotContain(onlyOff, id, $"week {week}");
                    Assert.IsTrue(Campaign.BossEnabled(id), id);
                }
            Assert.Less(BossHunts.Full.Count, every, "shorter with acts off");
            Campaign.Release = CampaignRelease.UpTo(4);
            Assert.AreEqual(every, BossHunts.Full.Count, "and longer again when they come back");
        }

        // ------------------------------------------------------------------ N.1: checkpoints, rests, supports

        [Test]
        public void ACheckpointAfterEachMainBossTakesTheRunUpAgain()
        {
            var catalog = GameContent.LoadCatalog();
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_sandbox"), 3);
            var rules = new BossRushRules
            {
                Bosses = new[] { "bastion_mk0", "fortress_bastion", "behemoth_inferno" }, HomeMap = "ashfield",
                Checkpoints = HuntCheckpoints.MainBosses, Supports = true, Seed = 7, Ramp = true, RestRepair = 0.3f, Breather = 3f,
            };
            var hunt = new BossRushMode(rules);
            hunt.Setup(world);
            Kill(hunt, world);
            Assert.IsNull(hunt.Offer, "no support after a mini boss");
            Assert.GreaterOrEqual(hunt.RestLeft(world), 0f, "the rest");
            Run(hunt, world, () => hunt.Boss.IsValid, 6f);
            Assert.AreEqual(0, hunt.CheckpointsTaken, "no checkpoint after a mini boss");
            // A hurt vehicle is partly repaired when the main boss falls.
            var tank = world.VehicleList.First(v => v.IsAlive && v.Team == BossRushMode.PlayerTeam && !v.Def.Static);
            tank.Hp = tank.MaxHp * 0.2f;
            Kill(hunt, world);
            Assert.AreEqual(0.5f, tank.Hp / tank.MaxHp, 0.02f, "30 % back in the rest");
            Assert.AreEqual(3, hunt.Offer?.Count, "three supports after a main boss");
            var picked = hunt.Offer[1];
            Assert.IsTrue(hunt.Choose(world, picked));
            Assert.IsNull(hunt.Offer);
            Run(hunt, world, () => hunt.Boss.IsValid, 6f);
            Assert.AreEqual(1, hunt.CheckpointsTaken, "a checkpoint as the rest after the main boss ends");
            var checkpoint = hunt.Checkpoint;
            Assert.IsTrue(checkpoint.Checkpoint);
            Assert.AreEqual(2, checkpoint.Defeated);
            Assert.AreEqual("ashfield", checkpoint.Map);
            CollectionAssert.AreEqual(new[] { picked }, checkpoint.Supports);
            Assert.Greater(checkpoint.Army.Count, 0);

            // Saved and taken up again (a later sitting): the same bosses down, the support held, the clock on.
            PlayerProfile.ResetForTests();
            PlayerProfile.SaveHuntCheckpoint(BossHunts.FullKey, 0, rules.Bosses, checkpoint);
            var saved = PlayerProfile.HuntCheckpoint(BossHunts.FullKey, 5, rules.Bosses);
            Assert.IsNotNull(saved, "the full hunt's checkpoint lasts past the week");
            Assert.IsNull(PlayerProfile.HuntCheckpoint(BossHunts.FullKey, 5, new[] { "behemoth" }), "not for another run");
            PlayerProfile.SaveHuntCheckpoint(BossHunts.WeeklyKey, 202640, rules.Bosses, checkpoint);
            Assert.IsNull(PlayerProfile.HuntCheckpoint(BossHunts.WeeklyKey, 202641, rules.Bosses), "the week's ends with the week");
            var again = new SimWorld(catalog, GameContent.LoadMap(saved.Map + "_sandbox"), 3);
            var resumed = new BossRushMode(new BossRushRules
            {
                Bosses = rules.Bosses, HomeMap = "ashfield", Checkpoints = rules.Checkpoints, Supports = true, Seed = 7, Breather = 3f, Resume = saved,
            });
            resumed.Setup(again);
            Assert.AreEqual(2, resumed.Defeated);
            CollectionAssert.AreEqual(new[] { picked }, resumed.Held);
            Assert.AreEqual(checkpoint.TimeUsed, resumed.TimeUsed, 1e-6);
            Run(resumed, again, () => resumed.Boss.IsValid, 10f);
            Assert.AreEqual("behemoth_inferno", again.TryGetVehicle(resumed.Boss, out var third) ? third.Def.Id : null, "the run goes on from its checkpoint");
        }

        [Test]
        public void TwelveSupportsOfferedFairlyAndKeptForTheRun()
        {
            Assert.AreEqual(12, HuntSupports.All.Count);
            CollectionAssert.AllItemsAreUnique(HuntSupports.All.Select(s => s.Id));
            foreach (var s in HuntSupports.All)
            {
                Assert.IsTrue(Strings.Has("hunt.support." + s.Id), s.Id);
                Assert.IsTrue(Strings.Has("hunt.support." + s.Id + ".info"), s.Id);
            }
            // Three different, none held, the same for the same run and boss; over many runs each is offered, none always.
            var seen = new Dictionary<string, int>();
            for (var seed = 0; seed < 40; seed++)
                for (var boss = 0; boss < 3; boss++)
                {
                    var held = new[] { "hull", "rapid" };
                    var offer = HuntSupports.Offer(seed, boss, held);
                    CollectionAssert.AreEqual(offer, HuntSupports.Offer(seed, boss, held));
                    Assert.AreEqual(3, offer.Distinct().Count());
                    CollectionAssert.IsEmpty(offer.Intersect(held));
                    foreach (var id in HuntSupports.Offer(seed, boss, Array.Empty<string>())) seen[id] = seen.TryGetValue(id, out var n) ? n + 1 : 1;
                }
            Assert.AreEqual(12, seen.Count, "every support is offered");
            Assert.Less(seen.Values.Max(), 120, "none is always offered");

            // What they do.
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_sandbox"), 5);
            var hunt = new BossRushMode(new BossRushRules { Bosses = new[] { "behemoth" }, Supports = true, RestRepair = 0.3f });
            hunt.Setup(world);
            world.TryGetEconomy(BossRushMode.PlayerTeam, out var economy);
            var tank = world.VehicleList.First(v => v.IsAlive && v.Team == BossRushMode.PlayerTeam && !v.Def.Static);
            tank.Hp = tank.MaxHp * 0.5f;
            var cap = economy.ArmyCap;
            foreach (var id in new[] { "hull", "rapid", "supply", "workshop" })
            {
                hunt.DebugOffer(new[] { id, "gunnery", "engines" });
                Assert.IsTrue(hunt.Choose(world, id));
                hunt.Tick(world, Step);
                world.Step(Step);
            }
            Assert.AreEqual(1.15f, tank.MaxHp / tank.Def.MaxHp / tank.BoostHp, 0.01f, "hull: +15 % health");
            Assert.AreEqual(0.5f, tank.Hp / tank.MaxHp, 0.01f, "its share of health kept");
            Assert.AreEqual(0.75f, economy.StrikeScale, 1e-4f, "rapid: cooldowns -25 %");
            Assert.AreEqual(cap + 6, economy.ArmyCap, "supply: +6");
            Assert.AreEqual(0.6f, hunt.RestRepairShare, 1e-4f, "workshop: rests repair twice as much");
            Assert.IsFalse(hunt.Choose(world, "loaders"), "only what is offered");
        }

        // ------------------------------------------------------------------ P: ranks, generals, names

        /// <summary>Prompt 20 K: each boss's general.</summary>
        private static readonly Dictionary<string, string> Generals = new()
        {
            ["fortress_bastion"] = "brandt", ["bastion_mk0"] = "brandt",
            ["behemoth"] = "varga", ["moloch"] = "varga", ["behemoth_inferno"] = "varga", ["behemoth_mk2"] = "varga",
            ["mobile_fortress"] = "orlov", ["fenrir"] = "orlov",
            ["leviathan"] = "kessler", ["behemoth_tempest"] = "kessler", ["armored_train"] = "kessler", ["scylla"] = "kessler", ["landing_hovercraft"] = "kessler",
            ["drone_mothership"] = "sen", ["locust"] = "sen",
            ["nuke_train"] = "hung", ["ixion"] = "hung", ["earth_borer"] = "hung", ["typhon"] = "hung",
            ["command_airship"] = "quaden", ["mega_gunship"] = "quaden", ["argus"] = "quaden",
            ["silver_bug"] = "aurel", ["daedalus"] = "aurel", ["icarus_mk0"] = "aurel",
            // Prompt 22 E.
            ["behemoth_mk0"] = "varga",
            // Prompt 25 F2 batch D.
            ["kraken"] = "kessler", ["monster"] = "orlov", ["hyperion"] = "aurel", ["nyx"] = "kessler", ["hydra"] = "hung",
        };

        [Test]
        public void EveryBossHasItsRankAndGeneral()
        {
            var catalog = GameContent.LoadCatalog();
            var mains = Campaign.Chapters.Select(c => c.Main).Where(id => id != null).ToList();
            Assert.AreEqual(11, mains.Distinct().Count(), "eleven main bosses (an interlude has none; Moloch holds chapters 6 and 8)");
            // Play-test 14 deleted ten bosses (their slots went to Matriarch, Behemoth Mk.II, Tartarus, Charybdis, Harpy, Roc, Monster).
            Assert.AreEqual(16, Campaign.Chapters.SelectMany(c => c.Minis).Distinct().Count(), "sixteen mini bosses in the slots");
            foreach (var c in Campaign.Chapters)
                foreach (var id in c.Minis.Append(c.Main).Where(id => id != null))
                {
                    Assert.IsTrue(catalog.Vehicles.TryGetValue(id, out var def) && def.Boss, $"chapter {c.Number}: {id} is a boss");
                    // Play-test 14: Monster (a main boss) holds a mini slot of chapter 11 in Gungnir's place (balance pack rule D: a main
                    // boss in a mini slot stays a main boss).
                    var rank = id == "monster" || id == c.Main ? BossRank.Main : BossRank.Mini;
                    Assert.AreEqual(rank, def.Rank, id);
                    Assert.AreEqual(Generals[id], def.General, id + "'s general");
                    Assert.IsTrue(Strings.Has($"char.{def.General}.name") && Strings.Has($"char.{def.General}.role"), def.General);
                    // O.2: its bar reads "Proper name · subtitle".
                    StringAssert.Contains(" · ", Strings.Card(id), id + "'s bar");
                    if (def.VariantOf != null) Assert.IsTrue(catalog.Vehicles[def.VariantOf].Rank == BossRank.Main, id + " is a variant of a main boss");
                }
            // The bosses outside the chapter slots keep the table's general too.
            foreach (var (id, general) in Generals) Assert.AreEqual(general, catalog.Vehicles[id].General, id);
            // Operations' extra boss is a mini boss of the operation's own chapter or boss.
            foreach (var op in Operations.Big)
            {
                var extra = MissionSession.ExtraBossFor(op, catalog);
                Assert.IsNotNull(extra, op.Id);
                Assert.AreEqual(BossRank.Mini, catalog.Vehicles[extra].Rank, $"{op.Id}: {extra}");
            }
        }

        private static readonly string[] OldNames =
        {
            "Silver Bug", "Bọ Bạc", "Iron Bird", "Chim sắt", "Chim Sắt", "Ice Fortress", "Pháo đài băng", "Pháo Đài Băng",
            "Hive Carrier", "Hive Mothership", "Tàu mẹ Tổ Ong", "Tàu Mẹ Tổ Ong", "Tổ Ong", "Doomsday Train", "Tận Thế",
            "Iron Train", "Đoàn tàu thép", "Đoàn Tàu Thép", "Rail Supergun", "Supreme Commander", "Tổng Tư Lệnh",
            "Earth Worm", "Sâu Đất", "Frost Monster", "Quái Vật Băng", "Frozen Behemoth", "Landing Hovercraft",
            "Command Airship", "Khinh Hạm", "Black Crow", "Hùng", "Quạ Đen", "Boss Rush", "Roc, Roc",
        };

        /// <summary>Prompt 22 A: no exception any more ("Quạ Đen" is gone; Wolff is Raven on every side).</summary>
        private static bool Allowed(string key, string name) => false;

        [Test]
        public void NoTextUsesAnOldName()
        {
            var bad = new List<string>();
            foreach (var (key, (en, vi)) in Strings.Texts.Concat(GuideText.Table).Concat(CampaignText.Table).Concat(UnitText.Table)
                         .Concat(BigAttackText.Table).Concat(OrbitalText.Table).Concat(BossText.Table))
                foreach (var name in OldNames)
                    if ((en.Contains(name) || vi.Contains(name)) && !Allowed(key, name))
                        bad.Add($"{key}: {name}");
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(40)));
        }

        // ------------------------------------------------------------------ pass 2's leftover: the two new battlefields

        [Test]
        public void SixMissionsFightOnTheNewBattlefields()
        {
            foreach (var (id, map) in new[] { ("c8m02", "openpit"), ("c8m07", "openpit"), ("c8m10", "openpit"), ("c11m04", "orbitalgate"), ("c11m07", "orbitalgate"), ("c11m10", "orbitalgate") })
            {
                var m = Campaign.Get(id);
                Assert.AreEqual(map, m.Map, id);
                var file = GameContent.LoadMap(map + "_" + m.Variant);
                // Every Destroy goal's targets stand on the new map, within its area.
                foreach (var goal in m.Stages.Select(s => s.Mission).Prepend(m).Where(g => g.Targets.Count > 0))
                    Assert.Greater(file.Props.Count(p => goal.Targets.Contains(p.DefId) &&
                        (goal.TargetNear is not { } near || Vector2.Distance(p.Position, near) <= goal.TargetRadius)), 0, $"{id}: {string.Join(",", goal.Targets)}");
            }
            // Play-test 14: Moloch waits at the head of the haul road (Kronos, whose road it was, was deleted); Tartarus tunnels up
            // in the same fight when Moloch is down to 60 %.
            var last = Campaign.Get("c8m10").Stages.Select(s => s.Mission).First(s => s.Boss?.Def == "moloch");
            var route = GameContent.LoadMap("openpit_conquest").Route("haul");
            Assert.Less(Vector2.Distance(last.Boss.Position, route[0]), 1f, "Moloch starts at the head of the haul road");
            Assert.IsTrue(last.Events.Any(e => e.Kind == MissionEventKind.MiniBoss && e.Trigger.BossHealth is > 0f), "Tartarus comes up mid-fight");
        }

        // ------------------------------------------------------------------ helpers

        private static void Run(BossRushMode mode, SimWorld world, Func<bool> until, float seconds)
        {
            for (var t = 0f; t < seconds && !until(); t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
            }
        }

        // ------------------------------------------------------------------ Prompt 26 E (written, not run)

        [Test]
        public void SupportsAreCappedAtFortyPercentThenOnlyPlayChangingOnesComeUp()
        {
            Assert.AreEqual(0.40f, HuntSupports.Cap);
            var held = new List<string> { "hull", "gunnery", "loaders" };
            Assert.AreEqual(0.37f, HuntSupports.Strength(held), 1e-4f);
            for (var boss = 0; boss < 20; boss++)
                foreach (var id in HuntSupports.Offer(7, boss, held))
                    Assert.That(HuntSupports.Get(id).PlayChanging || 0.37f + HuntSupports.Get(id).Strength <= 0.40f + 1e-4f, id);
            held.AddRange(new[] { "logistics", "regen", "supply" });
            foreach (var id in HuntSupports.Offer(7, 3, held)) Assert.IsTrue(HuntSupports.Get(id).PlayChanging, id);
        }

        [Test]
        public void AGearedDeckHasAHigherPAndABossesHealthFollowsIt()
        {
            var catalog = GameContent.LoadCatalog();
            var def = catalog.Vehicles.Values.First(v => !v.Boss && !v.Static && v.CpCost > 0 && v.Weapon != null);
            var bare = HuntPower.Estimate(new[] { (def, VehicleBoost.None) });
            var geared = HuntPower.Estimate(new[] { (def, new VehicleBoost(1.2f, 1.2f, 1.1f, 1f, 1f, 0f, SpecialModule.None, 0f)) });
            Assert.Greater(geared, bare);
            Assert.GreaterOrEqual(HuntPower.Estimate(new (VehicleDef, VehicleBoost)[0]), HuntPower.Floor);

            // Boss health = P x t x 0.6 x m: the first boss of a run with P 400 comes in with 400 x its seconds x 0.6.
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_sandbox"), 3);
            var mode = new BossRushMode(new BossRushRules { Bosses = new[] { "behemoth_inferno" }, HomeMap = "ashfield", Power = 400f, Ramp = true, MainSeconds = 150f, MiniSeconds = 60f });
            mode.Setup(world);
            Run(mode, world, () => mode.Boss.IsValid, 30f);
            Assert.IsTrue(world.TryGetVehicle(mode.Boss, out var boss));
            var seconds = boss.Def.Rank == BossRank.Main ? 150f : 60f;
            Assert.AreEqual(400f * seconds * 0.6f, boss.MaxHp, 1f);
        }

        /// <summary>Waits for the next boss and brings it down.</summary>
        private static void Kill(BossRushMode mode, SimWorld world)
        {
            Run(mode, world, () => mode.Boss.IsValid, 30f);
            Assert.IsTrue(world.TryGetVehicle(mode.Boss, out var boss), "a boss came");
            boss.Hp = 0f;
            var before = mode.Defeated;
            Run(mode, world, () => mode.Defeated > before, 2f);
            Assert.AreEqual(before + 1, mode.Defeated);
        }
    }
}
