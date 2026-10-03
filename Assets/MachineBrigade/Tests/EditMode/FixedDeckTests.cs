using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Sandbox;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 31 L1/L2 (DECISIONS "Prompt 31 L0/L1/L2"): the decks the game hands out (campaign.json "fixedDeck", written by
    /// Tools/campaign/fixed_decks.py from the sheet "Màn bộ bài game"). Every fixed deck is eight buyable vehicle cards and two
    /// support cards of the roster; its locked cards are loaned (at most two; c1m01 four); the objectives are the ones before
    /// prompt 31; the deck replaces the player's in the battle. Data tests and one short Sim test; written under the owner's
    /// rule of 30/09 (no test runs until the test phase): not run yet.
    /// </summary>
    public class FixedDeckTests
    {
        private const float Step = 0.05f;

        /// <summary>The 13 MAKE FIRST missions of prompt 31 L2.</summary>
        private static readonly string[] MakeFirst =
            { "c1m01", "c2m04", "c2s2", "c3m06", "c4m05", "c4m06", "c5m07", "c7m11", "c8m11", "c9m08", "i3m02", "i3m03", "c11m13" };

        /// <summary>The objectives before prompt 31 (campaign.json at ca1488f4; Tools/campaign/p31_objectives_baseline.json).</summary>
        private static readonly Dictionary<string, (MissionGoal goal, string points, string targets, int kills, float time, string boss, string hunt)> Before = new()
        {
            ["c1m01"] = (MissionGoal.Capture, "east,town", "", -1, 0f, null, ""),
            ["c2m04"] = (MissionGoal.Destroy, "", "pipeline", -1, 900f, null, ""),
            ["c2s2"] = (MissionGoal.ShootDown, "", "", 10, 1100f, null, ""),
            ["c3m06"] = (MissionGoal.Hunt, "", "", -1, 1100f, null, "mlrs,artillery,mlrs"),
            ["c4m05"] = (MissionGoal.Intercept, "", "", -1, 1200f, "armored_train", ""),
            ["c4m06"] = (MissionGoal.Boss, "", "", -1, 1500f, "scylla", ""),
            ["c5m07"] = (MissionGoal.ShootDown, "", "", 14, 1200f, null, ""),
            ["c7m11"] = (MissionGoal.ShootDown, "", "", 14, 1200f, null, ""),
            ["c8m11"] = (MissionGoal.Capture, "west,town,east", "", -1, 1000f, null, ""),
            ["c9m08"] = (MissionGoal.Boss, "", "", -1, 1500f, "scylla", ""),
            ["i3m02"] = (MissionGoal.Boss, "", "", -1, 1260f, "mega_gunship", ""),
            ["i3m03"] = (MissionGoal.Relieve, "", "", -1, 1000f, null, "main_battle_tank,tank_destroyer,light_tank,mortar_carrier,ifv,main_battle_tank"),
            ["c11m13"] = (MissionGoal.Recon, "west,town,east", "", -1, 600f, null, ""),
        };

        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static IEnumerable<MissionDef> Fixed => Campaign.Everything.Where(m => m.FixedDeck != null);

        private static MissionDef Mission(string id) => Campaign.Everything.First(m => m.Id == id);

        [Test]
        public void EveryMakeFirstMissionHasItsDeck()
        {
            foreach (var id in MakeFirst)
            {
                var deck = Mission(id).FixedDeck;
                Assert.IsNotNull(deck, $"{id}: a fixed deck");
                Assert.AreEqual("MAKE_FIRST", deck.Status, id);
            }
        }

        [Test]
        public void EveryFixedDeckIsEightVehiclesAndTwoSupportsOfTheRoster()
        {
            foreach (var m in Fixed)
            {
                var deck = m.FixedDeck;
                Assert.AreEqual(FixedDeckDef.VehicleSlots, deck.Vehicles.Count, $"{m.Id}: vehicle cards");
                Assert.AreEqual(FixedDeckDef.VehicleSlots, deck.Vehicles.Distinct().Count(), $"{m.Id}: no vehicle card twice");
                Assert.AreEqual(FixedDeckDef.SupportSlots, deck.Supports.Count, $"{m.Id}: support cards");
                Assert.AreEqual(FixedDeckDef.SupportSlots, deck.Supports.Distinct().Count(), $"{m.Id}: no support card twice");
                foreach (var id in deck.Vehicles)
                {
                    Assert.IsTrue(Catalog.Vehicles.TryGetValue(id, out var def), $"{m.Id}: {id} in the roster");
                    Assert.IsTrue(def.Card && !def.Boss && !def.StoryOnly && !def.Static, $"{m.Id}: {id} is a buyable vehicle card");
                    Assert.That(MatchSettings.AllVehicles, Has.Member(id), $"{m.Id}: {id} is a deck card");
                }
                foreach (var id in deck.Supports)
                {
                    Assert.IsTrue(Catalog.TryGetSupport(id, out _), $"{m.Id}: support {id} in the roster");
                    Assert.That(MatchSettings.AllSupports, Has.Member(id), $"{m.Id}: {id} is a support card");
                }
                // Placed allies take no card slot (pass 4 places the first).
                foreach (var ally in deck.PlacedAllies)
                    Assert.IsTrue(Catalog.Vehicles.ContainsKey(ally.Def) || (ally.Fallback != null && Catalog.Vehicles.ContainsKey(ally.Fallback)), $"{m.Id}: ally {ally.Def}");
            }
        }

        /// <summary>
        /// The campaign rule "no mission asks for a card not unlocked" and its one exception: a card not owned by the mission
        /// (starters and the earlier missions' rewards; the mission's own reward is not owned in it) is loaned, a loaned card is
        /// one not owned, and at most two are loaned (c1m01, the first battle: four, DECISIONS).
        /// </summary>
        [Test]
        public void OnlyLockedCardsAreLoanedAndAtMostTwo()
        {
            var owned = new HashSet<string>(MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports).Where(Progression.IsStarter));
            foreach (var m in Campaign.Everything)
            {
                if (m.FixedDeck is { } deck)
                {
                    foreach (var id in deck.Vehicles.Concat(deck.Supports))
                        Assert.IsTrue(owned.Contains(id) || deck.IsLoaned(id), $"{m.Id}: {id} is neither unlocked by then nor loaned");
                    foreach (var id in deck.Loaned)
                    {
                        Assert.IsFalse(owned.Contains(id), $"{m.Id}: {id} is unlocked by then, not loaned");
                        Assert.IsTrue(deck.Vehicles.Contains(id) || deck.Supports.Contains(id), $"{m.Id}: loaned {id} is in the deck");
                    }
                    var most = m.Id == "c1m01" ? 4 : FixedDeckDef.MaxLoaned;
                    Assert.LessOrEqual(deck.Loaned.Count, most, $"{m.Id}: loaned cards");
                }
                foreach (var id in m.Unlocks) owned.Add(id);
            }
        }

        [Test]
        public void TheObjectivesAreTheOnesBeforePrompt31()
        {
            foreach (var (id, was) in Before.Select(kv => (kv.Key, kv.Value)))
            {
                var m = Mission(id);
                Assert.AreEqual(was.goal, m.Goal, $"{id}: goal");
                Assert.AreEqual(was.points, string.Join(",", m.Points), $"{id}: points");
                Assert.AreEqual(was.targets, string.Join(",", m.Targets), $"{id}: targets");
                if (was.kills >= 0) Assert.AreEqual(was.kills, m.KillsNeeded, $"{id}: kills needed");
                Assert.AreEqual(was.time, m.TimeLimit, 0.01f, $"{id}: time limit");
                Assert.AreEqual(was.boss, m.Boss?.Def, $"{id}: boss");
                Assert.AreEqual(was.hunt, string.Join(",", m.Hunt.Select(h => h.Def)), $"{id}: hunted");
            }
        }

        [Test]
        public void EverySpecialRuleHasItsWordsInBothLanguages()
        {
            var was = Strings.Vietnamese;
            try
            {
                foreach (var m in Fixed)
                    foreach (var rule in m.FixedDeck.SpecialRules)
                    {
                        var key = "fixeddeck.rule." + rule;
                        Assert.IsTrue(Strings.Has(key), $"{m.Id}: {key}");
                        foreach (var vietnamese in new[] { false, true })
                        {
                            Strings.Vietnamese = vietnamese;
                            Assert.AreNotEqual(key, Strings.Get(key), $"{m.Id}: {key} ({(vietnamese ? "vi" : "en")})");
                        }
                    }
                Strings.Vietnamese = true;
                Assert.AreEqual("Mượn trong nhiệm vụ này", Strings.Get("fixeddeck.loaned"));
                Strings.Vietnamese = false;
                Assert.AreEqual("Loaned for this mission", Strings.Get("fixeddeck.loaned"));
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        /// <summary>The fixed deck replaces the player's deck: its cards, its supports, its rank (i3m03 one above the curve).</summary>
        [Test]
        public void TheFixedDeckReplacesThePlayersDeck()
        {
            var mine = new List<string> { "scout_jeep", "armored_car" };
            var supports = new List<string> { "artillery_barrage" };
            foreach (var m in Fixed)
            {
                Assert.AreEqual(m.FixedDeck.Vehicles.ToList(), MissionDecks.Vehicles(Catalog, m, mine), $"{m.Id}: the battle's vehicle cards");
                Assert.AreEqual(m.FixedDeck.Supports.ToList(), MissionDecks.Supports(m, supports), $"{m.Id}: the battle's support cards");
                Assert.AreEqual(m.FixedDeck.Vehicles.ToList(), MissionDecks.Deck(m, mine).ToList(), $"{m.Id}: the deck the enemy keeps pace with");
                var curve = UnityEngine.Mathf.FloorToInt(Campaign.ExpectedRank(m));
                Assert.AreEqual(UnityEngine.Mathf.Clamp(curve + m.FixedDeck.RankBonus, 1, CardRanks.Max), MissionDecks.FixedRank(m), $"{m.Id}: rank");
                Assert.AreEqual(MissionDecks.FixedRank(m), MissionDecks.Rank(m, m.FixedDeck.Vehicles[0]), $"{m.Id}: every card at the deck's rank");
            }
            Assert.AreEqual(1, Mission("i3m03").FixedDeck.RankBonus, "Crown's elite armour: one rank above");
            // A mission without one keeps the player's deck.
            var plain = Campaign.Everything.First(m => m.FixedDeck == null && m.PlayerDeck == null);
            Assert.AreEqual(mine, MissionDecks.Vehicles(Catalog, plain, mine));
            Assert.AreEqual(supports, MissionDecks.Supports(plain, supports));
        }

        /// <summary>The special rules ride on the mission type's AI profile as flags (no AI of their own).</summary>
        [Test]
        public void TheSpecialRulesRideOnTheMissionTypesProfile()
        {
            var m = Mission("c4m05");
            var world = new SimWorld(Catalog, SandboxMaps.Flat(), 1) { MissionGoal = m.Goal.ToString() };
            var plain = world.AiProfile;
            world.AddProfileFlags(m.FixedDeck.AiFlags);
            var withRules = world.AiProfile;
            Assert.AreEqual(plain.Id, withRules.Id, "the mission type's profile");
            Assert.IsTrue(withRules.HasFlag("rule:trainPrep"));
            Assert.IsFalse(plain.HasFlag("rule:trainPrep"));
        }

        /// <summary>c4m05: the route boss stands for the deck's preparation time, then sets off.</summary>
        [Test]
        public void TheRouteBossWaitsForThePreparationTime()
        {
            var world = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            foreach (var v in world.VehicleList) v.Hp = 0f;
            world.Step(Step);
            world.ClearEvents();
            var def = new MissionDef
            {
                Id = "prep", Goal = MissionGoal.Intercept, Reinforcements = 0, EnemyAi = "none",
                Boss = new ScriptedUnitDef { Def = "main_battle_tank", Position = new Vector2(0f, 0f), Route = new[] { new Vector2(40f, 0f) } },
                FixedDeck = new FixedDeckDef { PrepSeconds = 10f },
            };
            var mode = new MissionMode(def, new SideSetup { StartCp = 5f, Income = 0f }, null);
            mode.Setup(world);
            var boss = world.VehicleList.First(v => v.Team == 1 && v.Def.Id == "main_battle_tank" && v.IsAlive);
            var start = boss.Position;
            for (var t = 0f; t < 6f; t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.Less(Vector2.Distance(start, boss.Position), 1f, "it stands while the trap is laid");
            for (var t = 0f; t < 14f; t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.Greater(Vector2.Distance(start, boss.Position), 3f, "then it sets off along its route");
        }
    }
}
