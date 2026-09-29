using System.Linq;
using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The story campaign (prompt 4): its shape, every mission playing to an end with the player's
    /// commander AI in charge and the cards and base a player really has by then, the operations
    /// within their time windows, the dialogue in the localisation, and old saves moving across.
    /// A mission whose battlefield is not in this build (the maps branch) is skipped with a note.
    /// </summary>
    public class CampaignTests
    {
        private List<string> _vehicles, _supports;
        private string _mission;
        private bool _unlockAll;

        private static IEnumerable<string> Missions()
        {
            foreach (var m in Campaign.All) yield return m.Id;
        }

        [SetUp]
        public void SetUp()
        {
            _vehicles = new List<string>(MatchSettings.DeckVehicles);
            _supports = new List<string>(MatchSettings.DeckSupports);
            _mission = MatchSettings.Mission;
            _unlockAll = Progression.TestUnlockAll;
        }

        [TearDown]
        public void TearDown()
        {
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(_vehicles);
            MatchSettings.DeckSupports.Clear();
            MatchSettings.DeckSupports.AddRange(_supports);
            MatchSettings.Mission = _mission;
            Progression.TestUnlockAll = _unlockAll;
            PlayerProfile.Load();
        }

        /// <summary>The main missions a player must have won to reach this one (a side mission: those up to the one it follows).</summary>
        private static List<MissionDef> Before(MissionDef mission)
        {
            var cut = mission.Side && mission.After != null ? Campaign.IndexOf(mission.After) + 1 : Campaign.IndexOf(mission.Id);
            var list = new List<MissionDef>();
            for (var i = 0; i < cut; i++)
                if (!Campaign.All[i].Side) list.Add(Campaign.All[i]);
            return list;
        }

        /// <summary>Every card a player has at a mission: the starter cards and what the main missions before it unlocked.</summary>
        internal static List<string> Owned(MissionDef mission)
        {
            var owned = new List<string>(Progression.StarterVehicles.Concat(Progression.StarterSupports).Concat(Progression.StarterTowers));
            foreach (var m in Before(mission))
                foreach (var id in m.Unlocks)
                    if (!owned.Contains(id)) owned.Add(id);
            return owned;
        }

        /// <summary>Starter cards plus the unlocks of every earlier mission: six strongest vehicles, two best supports.</summary>
        internal static (List<string> vehicles, List<string> supports) RealisticDeck(string missionId)
        {
            var catalog = GameContent.LoadCatalog();
            var mission = Campaign.Get(missionId);
            var all = Owned(mission);
            var owned = all.Where(id => catalog.Vehicles.TryGetValue(id, out var v) && !v.Static).ToList();
            var supports = all.Where(id => catalog.TryGetSupport(id, out _)).ToList();
            // A deck a player would build: the dearest aircraft (one at most: air slots are scarce),
            // an anti-air card, an artillery card (the answer to a dug-in enemy), then the dearest
            // ground vehicles. Ties keep the order the cards were won in.
            var byCost = owned.Select((id, i) => (id, i)).OrderByDescending(c => catalog.Vehicle(c.id).CpCost).ThenBy(c => c.i)
                .Select(c => c.id).ToList();
            var deck = new List<string>();
            void Take(System.Func<VehicleDef, bool> fits)
            {
                var id = byCost.Find(v => !deck.Contains(v) && fits(catalog.Vehicle(v)));
                if (id != null && deck.Count < 6) deck.Add(id);
            }
            Take(d => d.Flying);
            // Anti-air that also fights on the ground first (a long-range SAM is for an air-heavy enemy).
            Take(d => d.Class == UnitClass.AntiAir && d.Mounts.Any(m => m.Weapon.CanTarget(false)));
            if (!deck.Any(v => catalog.Vehicle(v).Class == UnitClass.AntiAir)) Take(d => d.Class == UnitClass.AntiAir);
            // Against an enemy in the air, a second one.
            if (FliesBoss(mission, catalog) || mission.Goal == MissionGoal.ShootDown) Take(d => !d.Flying && d.Weapon.CanTarget(true));
            Take(d => d.Class == UnitClass.Artillery || d.Weapon.MinRange > 0f);
            foreach (var id in byCost)
                if (deck.Count < 6 && !deck.Contains(id) && !catalog.Vehicle(id).Flying) deck.Add(id);
            supports.Sort((a, b) => catalog.Supports[b].CpCost.CompareTo(catalog.Supports[a].CpCost));
            return (deck, supports.GetRange(0, System.Math.Min(2, supports.Count)));
        }

        private static bool FliesBoss(MissionDef mission, Catalog catalog)
        {
            bool Flies(ScriptedUnitDef b) => b != null && catalog.Vehicles.TryGetValue(b.Resolve(catalog).def, out var d) && d.Flying;
            return Flies(mission.Boss) || mission.Stages.Any(s => Flies(s.Mission.Boss));
        }

        /// <summary>
        /// The base a player has at a mission: the HQ level the campaign has opened by then, each slot
        /// the best tower of its size they own, the modules they own.
        /// </summary>
        internal static BaseLoadout RealisticBase(MissionDef mission, Catalog catalog)
        {
            var owned = Owned(mission);
            var level = Campaign.HqLevelAt(mission);
            var loadout = new BaseLoadout { HqLevel = level };
            string[] large = { "artillery_emplacement", "missile_battery", "heavy_turret", "drone_hangar" };
            string[] medium = { "gun_turret", "rocket_turret", "atgm_tower", "c_ram" };
            string[] small = { "guard_tower", "aa_turret", "mg_bunker", "ew_tower", "dragons_teeth", "minefield" };
            void Fill(List<string> into, string[] order, SlotSize size)
            {
                var have = order.Where(owned.Contains).ToList();
                for (var i = 0; i < catalog.Base.Slots(level, size) && have.Count > 0; i++) into.Add(have[i % have.Count]);
            }
            Fill(loadout.Large, large, SlotSize.Large);
            Fill(loadout.Medium, medium, SlotSize.Medium);
            Fill(loadout.Small, small, SlotSize.Small);
            foreach (var id in new[] { "repair_bay", "ammo_depot", "radar_station", "logistics_station", "airfield" })
                if (owned.Contains(id) && loadout.Utilities.Count < catalog.Base.UtilitySlots(level)) loadout.Utilities.Add(id);
            return loadout;
        }

        /// <summary>A player's profile at a mission: the main missions before it won, the cards and base they give, nothing unlocked for testing.</summary>
        internal static void PlayerAt(MissionDef mission, Catalog catalog)
        {
            PlayerProfile.ResetForTests();
            // Off first: while every card counts as open, Unlock keeps nothing.
            Progression.TestUnlockAll = false;
            foreach (var m in Before(mission)) PlayerProfile.RecordMission(m.Id, 2);
            foreach (var id in Owned(mission)) PlayerProfile.Unlock(id);
            PlayerProfile.BaseLoadout = RealisticBase(mission, catalog);
            var (vehicles, supports) = RealisticDeck(mission.Id);
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(vehicles);
            MatchSettings.DeckSupports.Clear();
            MatchSettings.DeckSupports.AddRange(supports);
            MatchSettings.Mission = mission.Id;
            MatchSettings.MissionTier = 0;
        }

        private static void SkipWithoutMap(MissionDef def)
        {
            if (!Campaign.MapExists(def))
                Assert.Ignore($"{def.Id}: battlefield {def.Map}_{def.Variant} is not in this build (feature/new-maps); run it after the maps are merged");
        }

        /// <summary>One battle with the auto commanders: won, minutes, the session, the world, the peak army.</summary>
        private static (bool won, float minutes, MissionSession session, SimWorld world, int peak) Play(MissionDef def, int seed, float capMinutes)
        {
            var catalog = GameContent.LoadCatalog();
            PlayerAt(def, catalog);
            var world = new SimWorld(catalog, Campaign.LoadMap(def), seed: seed);
            var session = (MissionSession)ModeSession.Create(GameModeKind.Campaign, false, world, seed);
            var t = 0f;
            var peak = 0;
            for (; t < capMinutes * 60f && session.Mode.Result == null; t += 0.05f)
            {
                session.Mode.Tick(world, 0.05f);
                session.TickAi(world, 0.05f);
                world.Step(0.05f);
                world.ClearEvents();
                if (world.TryGetEconomy(0, out var economy) && economy.VehicleCount > peak) peak = economy.VehicleCount;
            }
            return (session.Mode.Result?.WinningTeam == 0, t / 60f, session, world, peak);
        }

        private static float Cap(MissionDef def) => def.Operation ? 34f : def.TimeLimit > 0f ? def.TimeLimit / 60f + 1f : 22f;

        // ------------------------------------------------------------------ shape

        [Test]
        public void TwelveChaptersOfTenMainAndTwoSideMissions()
        {
            // Prompt 20: 144 and chapter 4's epilogue boss, Leviathan (prompt 16).
            Assert.AreEqual(145, Campaign.All.Count);
            Assert.AreEqual(12, Campaign.ChapterCount);
            var catalog = GameContent.LoadCatalog();
            for (var c = 1; c <= 12; c++)
            {
                var main = Campaign.MissionsOf(c, side: false).Where(m => !m.Epilogue).ToList();
                Assert.AreEqual(10, main.Count, $"chapter {c}");
                Assert.AreEqual(2, Campaign.MissionsOf(c, side: true).Count, $"chapter {c} side missions");
                Assert.IsTrue(main[4].Goal is MissionGoal.Boss or MissionGoal.Intercept, $"chapter {c}: the fifth is a boss");
                Assert.IsTrue(main[9].Operation && main[9].Stages.Count >= 4, $"chapter {c}: the tenth is its operation");
                Assert.IsTrue(main[9].Stages.Any(s => s.Choices.Count == 2), $"chapter {c}: its operation has a choice of two");
                Assert.AreEqual(main[9], Campaign.OperationOf(c));
                var cards = main.SelectMany(m => m.Unlocks).Count(id => !id.Contains('.') && !(catalog.Vehicles.TryGetValue(id, out var v) && v.Fort is { Kind: FortKind.Utility }));
                Assert.That(cards, Is.InRange(4, 7), $"chapter {c} unlocks {cards} cards");
            }
            Assert.AreEqual("3-5", Campaign.Label(Campaign.Get("c3m05")));
            Assert.AreEqual("3-S1", Campaign.Label(Campaign.Get("c3s1")));
            CollectionAssert.AreEqual(new[] { 1, 2, 3, 4, 5 }, Campaign.All.Where(m => m.HqLevel > 0).Select(m => m.HqLevel).ToArray(), "an HQ level in chapters 1, 3, 6, 9, 11");
            CollectionAssert.AreEqual(new[] { 1, 3, 6, 9, 11 }, Campaign.All.Where(m => m.HqLevel > 0).Select(m => m.Chapter).ToArray());
        }

        [Test]
        public void EveryMissionReferencesRealContent()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var m in Campaign.All)
            {
                if (Campaign.MapExists(m)) Assert.DoesNotThrow(() => Campaign.LoadMap(m), m.Id);
                foreach (var def in new[] { m }.Concat(m.Stages.Select(s => s.Mission)))
                {
                    if (def.Boss != null)
                    {
                        var (boss, _) = def.Boss.Resolve(catalog);
                        Assert.IsTrue(catalog.Vehicles.TryGetValue(boss, out var b) && b.Boss, $"{m.Id}: {boss} is a boss");
                    }
                    foreach (var id in def.EnemyDeck) Assert.IsTrue(catalog.Vehicles.ContainsKey(id), $"{m.Id}: enemy card {id}");
                    foreach (var h in def.Hunt) Assert.IsTrue(catalog.Vehicles.ContainsKey(h.Def), $"{m.Id}: hunted {h.Def}");
                    if (def.Waves != null)
                        foreach (var id in def.Waves.Roster) Assert.IsTrue(catalog.Vehicles.ContainsKey(id), $"{m.Id}: wave {id}");
                    foreach (var u in def.Units) Assert.IsTrue(catalog.Vehicles.ContainsKey(u.DefId), $"{m.Id}: unit {u.DefId}");
                    if (def.Convoy != null) Assert.IsTrue(catalog.Vehicles.ContainsKey(def.Convoy.Def), $"{m.Id}: convoy {def.Convoy.Def}");
                }
                foreach (var s in m.Stages)
                    foreach (var e in s.Events)
                    {
                        foreach (var id in e.Units) Assert.IsTrue(catalog.Vehicles.ContainsKey(id), $"{m.Id}/{s.Id}: {id}");
                        if (e.Support != null) Assert.IsTrue(catalog.TryGetSupport(e.Support, out _), $"{m.Id}/{s.Id}: {e.Support}");
                    }
                foreach (var id in m.Unlocks) Assert.IsTrue(catalog.Vehicles.ContainsKey(id) || catalog.TryGetSupport(id, out _), $"{m.Id}: unlock {id}");
                if (m.General != null) Assert.IsNotNull(Campaign.General(m.General), $"{m.Id}: general {m.General}");
                if (m.Side) Assert.IsTrue(m.After != null && !Campaign.Get(m.After).Side && (m.RarePrints > 0 || m.TowerGear != null), $"{m.Id}");
            }
            foreach (var g in Campaign.Generals)
                foreach (var id in g.Deck) Assert.IsTrue(catalog.Vehicles.ContainsKey(id), $"general {g.Id}: {id}");
        }

        /// <summary>
        /// No mission needs a card the player cannot have yet: nothing is unlocked twice, and an enemy
        /// in the air (a flying boss, a shoot-down mission) comes only once the deck has two cards
        /// that shoot at aircraft from the ground.
        /// </summary>
        [Test]
        public void NoMissionNeedsALockedCard()
        {
            var catalog = GameContent.LoadCatalog();
            var seen = new HashSet<string>(Progression.StarterVehicles.Concat(Progression.StarterSupports).Concat(Progression.StarterTowers));
            foreach (var m in Campaign.All)
            {
                foreach (var id in m.Unlocks) Assert.IsTrue(seen.Add(id), $"{m.Id}: {id} was already the player's");
                if (!FliesBoss(m, catalog) && m.Goal != MissionGoal.ShootDown) continue;
                var (deck, _) = RealisticDeck(m.Id);
                var antiAir = deck.Count(id => !catalog.Vehicle(id).Flying && catalog.Vehicle(id).Weapon.CanTarget(true));
                Assert.GreaterOrEqual(antiAir, 2, $"{m.Id}: an enemy in the air, and the deck has {antiAir} anti-air cards ({string.Join(", ", deck)})");
            }
            foreach (var m in Campaign.All.Where(m => m.PlayerBase != BaseRole.None))
                Assert.GreaterOrEqual(Campaign.IndexOf(m.Id), Campaign.IndexOf(Campaign.HqLevelMission(1).Id), $"{m.Id}: a base before the first HQ");
        }

        /// <summary>Two missions on one battlefield differ in at least two of: direction, base, weather, play area, goal.</summary>
        [Test]
        public void EveryReturnToAMapChangesItsSetUp()
        {
            var all = Campaign.All;
            for (var i = 0; i < all.Count; i++)
                for (var j = i + 1; j < all.Count; j++)
                {
                    var a = all[i];
                    var b = all[j];
                    if (a.Map != b.Map) continue;
                    var differs = 0;
                    if (a.Reversed != b.Reversed) differs++;
                    if (a.Variant != b.Variant || a.PlayerBase != b.PlayerBase || a.EnemyBase != b.EnemyBase) differs++;
                    if (a.Weather != b.Weather) differs++;
                    if (a.PlayArea.HasValue != b.PlayArea.HasValue) differs++;
                    if (a.Goal != b.Goal) differs++;
                    Assert.GreaterOrEqual(differs, 2, $"{a.Id} and {b.Id} on {a.Map}");
                }
        }

        [Test]
        public void EveryTextAndRadioLineIsLocalised()
        {
            var missing = new List<string>();
            void Need(string key)
            {
                if (key != null && !Strings.Has(key)) missing.Add(key);
            }
            foreach (var m in Campaign.All)
            {
                Need("mission." + m.Id + ".name");
                Need("mission." + m.Id + ".brief");
                Need("mission." + m.Id + ".fragment");
                Need("mission." + m.Id + ".fragment.title");
                Need("char." + m.Speaker + ".name");
                foreach (var r in m.Radio) Need(r.Key);
                foreach (var t in m.Tips) Need(t.key);
                if (m.Boss?.Name != null) Need("boss." + m.Boss.Name);
                foreach (var s in m.Stages)
                {
                    Need("stage." + m.Id + "." + s.Id);
                    foreach (var e in s.Events) Need(e.Key);
                    foreach (var c in s.Choices)
                    {
                        Need("choice." + m.Id + "." + c.Key);
                        Need("choice." + m.Id + "." + c.Key + ".info");
                    }
                    if (s.Mission.Boss?.Name != null) Need("boss." + s.Mission.Boss.Name);
                }
            }
            for (var c = 1; c <= Campaign.ChapterCount; c++)
            {
                Need($"chapter.{c}.title");
                Need($"chapter.{c}.summary");
                Need($"timeline.{c}");
            }
            foreach (var g in Campaign.Generals)
            {
                Need($"char.{g.Id}.name");
                Need($"char.{g.Id}.bio");
                Need($"radio.{g.Id}.defeat");
            }
            foreach (var speaker in CampaignText.Speakers) Need($"char.{speaker}.name");
            Need("radio.betrayal");
            Need("radio.bossFled");
            Assert.IsEmpty(missing, string.Join(", ", missing.Distinct()));
            foreach (var (key, (en, vi)) in CampaignText.Table)
            {
                Assert.IsFalse(string.IsNullOrWhiteSpace(en) || string.IsNullOrWhiteSpace(vi), key);
                Assert.IsFalse(en.Contains("...") || vi.Contains("..."), $"{key}: no '...'");
            }
        }

        [Test]
        public void EveryPortraitExists()
        {
            foreach (var id in CampaignText.Speakers)
                Assert.IsNotNull(Resources.Load<Texture2D>("UI/Portraits/" + id), $"portrait {id}");
        }

        // ------------------------------------------------------------------ the old campaign

        [Test]
        public void OldProgressMovesToTheStoryCampaign()
        {
            // A save from the 23-mission campaign: the boot camp and missions 1 to 12 won, 9 at Heroic, cards won.
            var ids = new List<string>();
            var stars = new List<int>();
            var tiers = new List<int>();
            for (var i = 0; i <= 12; i++)
            {
                ids.Add($"m{i:00}");
                stars.Add(i % 3 + 1);
                tiers.Add(i == 9 ? 1 : 0);
            }
            var json = JsonUtility.ToJson(new OldSave { missionIds = ids, missionStars = stars, missionTiers = tiers, unlocked = new List<string> { "mlrs", "gunship_heli", "cruise_missile" }, coins = 777 });
            try
            {
                PlayerProfile.LoadForTests(json);
                Progression.TestUnlockAll = false;
                foreach (var m in Campaign.All.Where(m => m.Legacy != null && ids.Contains(m.Legacy)))
                {
                    var i = ids.IndexOf(m.Legacy);
                    Assert.AreEqual(stars[i], PlayerProfile.Stars(m.Id), $"{m.Legacy} -> {m.Id}: stars");
                    Assert.AreEqual(tiers[i], PlayerProfile.MissionTier(m.Id), $"{m.Legacy} -> {m.Id}: tier");
                    Assert.IsTrue(Campaign.IsOpen(Campaign.IndexOf(m.Id)), $"{m.Id} stays open");
                    Assert.AreEqual(0, PlayerProfile.Stars(m.Legacy), "the old id is gone");
                }
                Assert.AreEqual(stars[3], PlayerProfile.Stars("c3m05"), "m03 (Iron Bird) became chapter 3's boss");
                Assert.IsTrue(PlayerProfile.IsUnlocked("gunship_heli") && PlayerProfile.IsUnlocked("cruise_missile"), "cards won stay won");
                Assert.AreEqual(777, PlayerProfile.Coins);
                Assert.AreEqual(Campaign.Get("m09"), Campaign.Get("c3m10"), "an old id still finds its mission");
                Assert.GreaterOrEqual(Campaign.HqLevelCap, 2, "the HQ level of the Iron Bird mission it won");
                // Saved and read back: nothing moves twice.
                PlayerProfile.LoadForTests(PlayerProfile.JsonForTests());
                Assert.AreEqual(stars[3], PlayerProfile.Stars("c3m05"));
            }
            finally
            {
                PlayerProfile.Load();
            }
        }

        [System.Serializable]
        private sealed class OldSave
        {
            public int version = 1;
            public int coins;
            public List<string> unlocked = new();
            public List<string> missionIds = new();
            public List<int> missionStars = new();
            public List<int> missionTiers = new();
        }

        [Test]
        public void MissionsOpenInChapterOrderAndSideMissionsAfterTheirMission()
        {
            try
            {
                PlayerProfile.ResetForTests();
                Assert.IsTrue(Campaign.IsOpen(0));
                var second = Campaign.All[1];
                Assert.AreEqual(!Campaign.MapExists(Campaign.All[0]), Campaign.IsOpen(1), "the second waits for the first (unless its battlefield is missing from this build)");
                var side = Campaign.Get("c1s1");
                Assert.IsFalse(Campaign.IsOpen(Campaign.IndexOf(side.Id)));
                foreach (var m in Campaign.All)
                {
                    if (m.Id == side.After) break;
                    PlayerProfile.RecordMission(m.Id, 1);
                }
                PlayerProfile.RecordMission(side.After, 1);
                Assert.IsTrue(Campaign.IsOpen(Campaign.IndexOf(side.Id)), "a side mission opens with the mission it follows");
                Assert.IsFalse(Campaign.All[Campaign.NextAfter(side.Id)].Side, "next after a side mission is a main one");
                Assert.IsFalse(Campaign.ChapterDone(1));
                foreach (var m in Campaign.MissionsOf(1, side: false)) PlayerProfile.RecordMission(m.Id, 1);
                Assert.IsTrue(Campaign.ChapterDone(1) && Campaign.ChapterOpen(2), "chapter 2 opens once chapter 1's operation is won");
                Progression.TestUnlockAll = false;
                Assert.AreEqual(1, Campaign.HqLevelCap);
                Assert.AreEqual(0, Campaign.OperationsTierOpen, "the Operations mode's first tier");
                Assert.IsNotNull(second);
            }
            finally
            {
                PlayerProfile.Load();
            }
        }

        [Test]
        public void TheRewardPaysBlueprintsTheHqLevelAndASideMissionsTowerPiece()
        {
            try
            {
                PlayerProfile.ResetForTests();
                MatchSettings.DeckVehicles.Clear();
                MatchSettings.DeckVehicles.AddRange(new[] { "light_tank", "ifv" });
                MatchSettings.DeckSupports.Clear();
                MatchSettings.DeckSupports.Add("artillery_barrage");
                var outpost = Campaign.HqLevelMission(1);
                var reward = Rewards.Mission(outpost, true, 60f, 0);
                Assert.Greater(reward.Prints, 0);
                Assert.AreEqual(1, reward.HqLevel);
                Assert.AreEqual(outpost.Id, reward.Fragment);
                reward.Claim();
                Assert.AreEqual(reward.Prints, reward.PrintsPaid.Sum(p => p.count), "every blueprint went to a card of the main deck");
                Assert.IsTrue(reward.PrintsPaid.All(p => PlayerProfile.MainDeck().Contains(p.card)));
                var side = Campaign.All.First(m => m.Side && m.TowerGear != null);
                var gear = PlayerProfile.GearOwned.Count;
                var loot = Rewards.Mission(side, true, 60f, 0);
                loot.Claim();
                Assert.AreEqual(gear + 1, PlayerProfile.GearOwned.Count, "the tower piece");
                Assert.IsTrue(Gear.IsTower(loot.GearPaid.Slot));
                var replay = Rewards.Mission(side, true, 60f, 0);
                Assert.IsNull(replay.TowerGear, "only the first win pays it");
            }
            finally
            {
                PlayerProfile.Load();
            }
        }

        // ------------------------------------------------------------------ playing them

        [Timeout(900000)]
        [TestCaseSource(nameof(Missions))]
        public void MissionPlaysToAnEnd(string id)
        {
            var def = Campaign.Get(id);
            SkipWithoutMap(def);
            var (won, minutes, session, world, _) = Play(def, 5, Cap(def));
            var mission = session.Mission;
            Debug.Log($"Mission {id} ({def.Goal}): {(won ? "WON" : session.Mode.Result == null ? "UNFINISHED" : "LOST")} " +
                      $"after {minutes:0.0} min, progress {mission.Progress(world):P0}, losses {mission.Losses}, kills {mission.Kills}" +
                      (def.Stages.Count > 0 ? $", stages {string.Join(">", session.Operation.Path.Select(i => def.Stages[i].Id))}" : ""));
            Assert.IsNotNull(session.Mode.Result, "a mission always ends (win, clock or defeat)");
        }

        /// <summary>
        /// Balance check, run by hand (it takes a while): each mission over five seeds with the cards
        /// and base a player really has, logging wins, time, progress and the peak army size; an
        /// operation must end within its window (15-25 minutes, the last one 15-30). Runs only with
        /// the environment variable MB_BALANCE=1 (and -testFilter WinRateOverFiveSeeds); MB_SEEDS
        /// sets how many seeds. Results go to the log ("SEEDS ...") for the report.
        /// </summary>
        [Category("Balance")]
        [Timeout(3600000)]
        [TestCaseSource(nameof(Missions))]
        public void WinRateOverFiveSeeds(string id)
        {
            if (System.Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance check: set MB_BALANCE=1 to run it");
            var def = Campaign.Get(id);
            SkipWithoutMap(def);
            var seeds = int.TryParse(System.Environment.GetEnvironmentVariable("MB_SEEDS"), out var n) ? n : 5;
            var wins = 0;
            var text = "";
            var durations = new List<float>();
            for (var seed = 1; seed <= seeds; seed++)
            {
                var (won, minutes, session, world, peak) = Play(def, seed, Cap(def));
                if (won) wins++;
                durations.Add(minutes);
                var mission = session.Mission;
                text += $" s{seed}:{(won ? "W" : "L")}{minutes:0.0}m/{mission.Progress(world):P0}/peak {peak}";
                if (def.Stages.Count > 0) text += "/" + string.Join(">", session.Operation.Path.Select(i => def.Stages[i].Id));
                foreach (var v in world.VehicleList)
                    if (!won && v.IsAlive && v.Marked) text += $" [{v.Def.Id} at {v.Position.X:0},{v.Position.Y:0} hp {v.Hp / v.MaxHp:P0}]";
                if (!won && world.TryGetVehicle(mission.Boss, out var boss) && boss.IsAlive)
                    text += $" [boss hp {boss.Hp / boss.MaxHp:P0} at {boss.Position.X:0},{boss.Position.Y:0}]";
            }
            Debug.Log($"SEEDS {id}: {wins}/{seeds} mean {durations.Average():0.0}m{text}");
            Assert.AreEqual(seeds, wins, $"{id}: won {wins} of {seeds}");
            if (!def.Operation) return;
            var last = Campaign.OperationOf(Campaign.ChapterCount) == def;
            foreach (var d in durations) Assert.That(d, Is.InRange(15f, last ? 30f : 25f), $"{id}: an operation of {d:0.0} minutes");
        }

        /// <summary>
        /// A checkpoint of a real operation: the battle replayed from its seed (the commanders and the
        /// player's pick at the branching point, as MatchRunner replays it) lands on the same state.
        /// </summary>
        [Timeout(900000)]
        [Test]
        public void ReplayingARealOperationLandsOnItsCheckpoint()
        {
            var def = Campaign.All.First(m => m.Operation && Campaign.MapExists(m));
            var catalog = GameContent.LoadCatalog();
            (SimWorld, MissionSession) Start()
            {
                PlayerAt(def, catalog);
                var w = new SimWorld(catalog, Campaign.LoadMap(def), seed: 7);
                return (w, (MissionSession)ModeSession.Create(GameModeKind.Campaign, false, w, 7));
            }
            var chosen = def.Stages.First(s => s.Choices.Count > 1).Choices[1].Key;
            // The player picks the second branch as soon as the choice comes up.
            void Feed(SimWorld w, MissionSession s)
            {
                if (s.Operation.PendingChoice != null) s.Choose(w, chosen);
            }
            void Step(SimWorld w, MissionSession s)
            {
                Feed(w, s);
                s.Mode.Tick(w, 0.05f);
                s.TickAi(w, 0.05f);
                w.Step(0.05f);
                w.ClearEvents();
            }
            var (world, session) = Start();
            for (var t = 0f; t < 30 * 60 && session.Operation.Checkpoints.Count < 2 && session.Mode.Result == null; t += 0.05f) Step(world, session);
            Assert.GreaterOrEqual(session.Operation.Checkpoints.Count, 2, "two stages done, a branch chosen");
            var checkpoint = session.Operation.Checkpoints[1];
            var (again, replay) = Start();
            while (again.Tick < checkpoint.Tick) Step(again, replay);
            // The checkpoint was taken after that step's input (here the pick), so the replay feeds it too, as MatchRunner's does.
            Feed(again, replay);
            Assert.AreEqual(checkpoint.Hash, again.StateHash(), "the same battle, step for step");
            CollectionAssert.AreEqual(session.Operation.Path.Take(2).ToArray(), replay.Operation.Path.Take(2).ToArray(), "and the same branch");
        }
    }
}
