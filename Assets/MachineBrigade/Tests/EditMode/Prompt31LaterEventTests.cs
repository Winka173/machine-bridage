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
    /// Prompt 31 L5 (DECISIONS "Prompt 31 L5"): the LATER events of the sheet "Biến cố". Each switches prebuilt ground at a tick
    /// boundary after its 8-12 s warning with its places on the minimap, leaves a way round (every campaign site's states are
    /// checked by Prompt31NavStateTests), and meets the same states on the same step in a replay. Written for the lead to run
    /// (the owner's rule: agents write tests, they do not run them).
    /// </summary>
    public class Prompt31LaterEventTests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SimWorld Field(int seed = 1) => new(Catalog, new MapDefinition("field", 300f,
            new[] { new TeamStart(0, new Vector2(-108.75f, -108.75f)), new TeamStart(1, new Vector2(108.75f, 108.75f)) },
            new List<PropPlacement>(), new List<UnitPlacement>()), seed);

        /// <summary>A mission of one survive goal on the open field with the given library rows, nav sites and references.</summary>
        private static MissionDef Mission(string events, string sites, string refs) =>
            MissionDef.ListFromJson("{\"eventLibrary\": {\"events\": [" + events + "]}, \"missions\": [{\"id\": \"p31l5\", \"map\": \"field\", " +
                                    "\"goal\": \"Survive\", \"surviveSeconds\": 5000, \"enemyAi\": \"none\", \"navStates\": [" + sites + "], " +
                                    "\"missionEvents\": [" + refs + "]}]}")[0];

        private static (SimWorld world, MissionMode mode) Start(MissionDef def, int seed = 1)
        {
            var world = Field(seed);
            var mode = new MissionMode(def, new SideSetup(), new SideSetup()) { EventLevel = EventLevel.Normal };
            mode.Setup(world);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-100f, -100f), 0f).Invulnerable = true;
            return (world, mode);
        }

        private static List<ulong> Run(SimWorld world, MissionMode mode, float seconds)
        {
            var hashes = new List<ulong>();
            for (var t = 0f; t < seconds; t += Dt)
            {
                mode.Tick(world, Dt);
                world.Step(Dt);
                world.ClearEvents();
                if (world.Tick % 20 == 0) hashes.Add(world.StateHash());
            }
            return hashes;
        }

        private static EventState State(MissionMode mode, string id) => mode.Events.States.First(s => s.Def.Instance == id);

        // ================================================================== the words

        [Test]
        public void EveryLaterEventHasItsWordsInBothLanguages()
        {
            // Every ("text", state) a campaign event brings in (Tools/campaign/ground_events.py, prompt 31 L5).
            var variants = new[] { "tide.high", "tide.low", "bridge.down" };
            var keys = new List<string>();
            foreach (var v in variants)
                keys.AddRange(new[] { $"event.groundChange.{v}.warn", $"event.groundChange.{v}.start", $"radio.linh.ev.groundChange.{v}.warn" });
            var missing = keys.Where(k => !Strings.Has(k)).ToList();
            Assert.IsEmpty(missing, string.Join("\n", missing));
        }

        // ================================================================== the campaign's later events

        /// <summary>(mission, library event, nav site it switches): the missions of the sheet that play a later event (stage events aside).</summary>
        private static readonly (string mission, string evt, string site)[] Placed =
        {
            ("c1m01", "tide_turn", "shoal"),
            ("i2m03", "bridge_collapse", "east_bridge"),
        };

        [Test]
        public void TheLaterEventsArePlayedWhereTheSheetPutsThem()
        {
            var bad = new List<string>();
            foreach (var (id, evt, site) in Placed)
            {
                var m = Campaign.Everything.FirstOrDefault(x => x.Id == id);
                if (m == null)
                {
                    bad.Add($"{id}: no such mission");
                    continue;
                }
                if (!m.Events.Any(e => e.Id == evt)) bad.Add($"{id}: does not play {evt}");
                if (!m.NavSites.Any(s => s.Id == site)) bad.Add($"{id}: does not build the site {site}");
            }
            var i2m03 = Campaign.Everything.First(x => x.Id == "i2m03");
            Assert.LessOrEqual(i2m03.Events.Count, 3, "an interlude plays three events at most");
            Assert.IsTrue(i2m03.Events.Any(e => e.Id == "hunters"), "chapter 14's signature stays");
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        // ================================================================== Triều lên/xuống (the tide)

        private const string Shoal = "{\"id\": \"shoal\", \"initial\": \"low\", \"states\": [{\"name\": \"low\"}, {\"name\": \"high\", " +
                                     "\"blocks\": [{\"x\": 40, \"z\": -120, \"w\": 40, \"d\": 8}]}]}";

        private const string Tide = "{\"id\": \"tide\", \"kind\": \"GroundChange\", \"trigger\": {\"at\": 1, \"every\": 30}, \"lead\": 10, " +
                                    "\"params\": {\"navSite\": \"shoal\", \"cycle\": true, \"text\": \"tide\"}}";

        [Test]
        public void TheTideFloodsTheShoalAndDriesItAgain()
        {
            var (world, mode) = Start(Mission(Tide, Shoal, "\"tide\""));
            Run(world, mode, 2f);
            var s = State(mode, "tide");
            Assert.AreEqual(EventPhase.Warned, s.Phase);
            Assert.GreaterOrEqual(s.StartAt - s.WarnedAt, 8.0 - 1e-6);
            Assert.LessOrEqual(s.StartAt - s.WarnedAt, 12.0 + 1e-6);
            Assert.AreEqual(1, s.Marks.Count, "the shoal on the minimap");
            Assert.AreEqual(MissionEventSystem.NoticeKey(s.Def, "warn", "tide.high"), "event.groundChange.tide.high.warn");
            Run(world, mode, 11f);
            Assert.AreEqual("high", world.NavStates.ActiveOf("shoal"), "high water");
            Assert.IsFalse(world.Grid.IsWalkable(new Vector2(40f, -120f)));
            // 30 s after it came in, the tide turns again (warned first, 10 s): the shoal dries.
            Run(world, mode, 40f);
            Assert.AreEqual("low", world.NavStates.ActiveOf("shoal"), "low water");
            Assert.IsTrue(world.Grid.IsWalkable(new Vector2(40f, -120f)));
            Run(world, mode, 40f);
            Assert.AreEqual("high", world.NavStates.ActiveOf("shoal"), "and in again");
        }

        [Test]
        public void ATideReplayMeetsTheSameStatesOnTheSameStep()
        {
            var def = Mission(Tide, Shoal, "\"tide\"");
            var (a, modeA) = Start(def, 5);
            var (b, modeB) = Start(def, 5);
            CollectionAssert.AreEqual(Run(a, modeA, 80f), Run(b, modeB, 80f));
            Assert.AreEqual(a.NavStates.Sites[0].SwitchedAt, b.NavStates.Sites[0].SwitchedAt);
            Assert.AreEqual(a.NavStates.Switches, b.NavStates.Switches);
            Assert.GreaterOrEqual(a.NavStates.Switches, 2);
        }
    }
}
