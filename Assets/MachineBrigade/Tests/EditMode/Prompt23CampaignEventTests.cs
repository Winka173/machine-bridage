using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 23 E, the bare minimum: the campaign keeps the build's rules (A.2's counts, E.1's signature events, E.2's general
    /// on the field in every chapter, E.3's no two missions in a row with one set of events); the Hollow Dam's ceasefire clock;
    /// an interception's intel file going into the dossier; and one seed of three missions (chapter 2's first, the ceasefire's, and
    /// chapter 12's operation up to its Total Offensive) starting, their events firing and nothing throwing.
    /// </summary>
    public class Prompt23CampaignEventTests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private List<string> _vehicles, _supports;
        private string _mission;
        private bool _unlockAll;

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

        // ================================================================== the build's rules

        /// <summary>E.1's signature events by chapter (Tools/campaign/events.py SIGNATURES).</summary>
        private static readonly Dictionary<int, string[]> Signatures = new()
        {
            [1] = new[] { "landing_assault", "accord_landing" },
            [2] = new[] { "oil_convoy", "thorne_support" },
            [3] = new[] { "orlov_barrage", "snowstorm" },
            [4] = new[] { "landing_assault", "rail_reinforcements", "ferries" },
            [5] = new[] { "drone_swarm", "ew_blackout" },
            [6] = new[] { "enemy_all_directions", "ceasefire", "brandt_line" },
            [7] = new[] { "turned_columns", "militia" },
            [8] = new[] { "tartarus", "miners_held" },
            [9] = new[] { "landing_assault", "sea_fog" },
            [10] = new[] { "air_raids", "hawk_strike", "nightfall" },
            [11] = new[] { "drop_pods", "test_rod" },
            [12] = new[] { "enemy_all_directions", "total_offensive" },
            [14] = new[] { "hunters" },
            [15] = new[] { "harpy_hunt", "nightfall" },
        };

        /// <summary>Every event a mission names: its own and every stage's.</summary>
        private static IEnumerable<MissionEventDef> All(MissionDef m) => m.Events.Concat(m.Stages.SelectMany(s => s.Mission.Events));

        /// <summary>The events one play meets: its own, its stages' but for the one of the two it chooses between it does not play.</summary>
        private static int Played(MissionDef m)
        {
            var alternatives = new HashSet<string>(m.Stages.SelectMany(s => s.Choices).Select(c => c.Next));
            var n = m.Events.Count + m.Stages.Where(s => !alternatives.Contains(s.Id)).Sum(s => s.Mission.Events.Count);
            return n + m.Stages.Where(s => alternatives.Contains(s.Id)).Select(s => s.Mission.Events.Count).DefaultIfEmpty(0).Max();
        }

        private static string Set(MissionDef m) => string.Join(",", All(m).Select(e => e.Id).OrderBy(id => id, StringComparer.Ordinal));

        [Test]
        public void TheCampaignKeepsTheCountsTheSignaturesTheGeneralsAndNoRepeats()
        {
            var missions = Campaign.Everything;
            var chapters = Campaign.Chapters.ToDictionary(c => c.Number);
            var bad = new List<string>();
            foreach (var m in missions)
            {
                // A.2: a mission 2-4, a big operation 5-8, an interlude's mission 2-3 (a side mission is a mission).
                var (lo, hi) = m.Operation ? (5, 8) : chapters[m.Chapter].IsInterlude ? (2, 3) : (2, 4);
                var n = Played(m);
                if (n < lo || n > hi) bad.Add($"{m.Id}: {n} events (want {lo}-{hi})");
            }
            foreach (var (chapter, ids) in Signatures)
            {
                var named = new HashSet<string>(missions.Where(m => m.Chapter == chapter).SelectMany(All).Select(e => e.Id));
                foreach (var id in ids)
                    if (!named.Contains(id)) bad.Add($"chapter {chapter}: no {id}");
            }
            // E.2: the general on the field in a mission every play meets (not only in one option of a story choice).
            foreach (var c in chapters.Values.Where(c => c.General != null))
                if (!missions.Any(m => m.Chapter == c.Number && m.Branch == null && All(m).Any(e => e.Kind == MissionEventKind.GeneralField)))
                    bad.Add($"chapter {c.Number}: no general on the field");
            // E.3: the order of play (a side mission after the one it follows).
            var main = missions.Where(m => !m.Side).ToList();
            var pairs = main.Zip(main.Skip(1), (a, b) => (a, b)).ToList();
            pairs.AddRange(missions.Where(m => m.Side && m.After != null).Select(m => (missions.First(x => x.Id == m.After), m)));
            foreach (var (a, b) in pairs)
                if (Set(a) == Set(b)) bad.Add($"{a.Id} and {b.Id}: one set of events ({Set(a)})");
            // Every kind is played somewhere in the campaign.
            var kinds = new HashSet<MissionEventKind>(missions.SelectMany(All).Select(e => e.Kind));
            foreach (MissionEventKind k in Enum.GetValues(typeof(MissionEventKind)))
                if (!kinds.Contains(k)) bad.Add($"no mission plays a {k}");
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        // ================================================================== the ceasefire

        private static SimWorld Field(int seed = 1) => new(Catalog, new MapDefinition("field", 300f,
            new[] { new TeamStart(0, new Vector2(-108.75f, -108.75f)), new TeamStart(1, new Vector2(108.75f, 108.75f)) },
            new List<PropPlacement>(), new List<UnitPlacement>()), seed);

        private static MissionDef Mission(string events, string refs, string extra = "") =>
            MissionDef.ListFromJson("{\"eventLibrary\": {\"events\": [" + events + "]}, \"missions\": [{\"id\": \"p23e\", \"map\": \"field\", " +
                                    "\"goal\": \"Survive\", \"surviveSeconds\": 5000, \"enemyAi\": \"none\"" + extra + ", \"missionEvents\": [" + refs + "]}]}")[0];

        private static (SimWorld world, MissionMode mode) Start(MissionDef def)
        {
            var world = Field();
            var mode = new MissionMode(def, new SideSetup(), new SideSetup()) { EventLevel = EventLevel.Normal };
            mode.Setup(world);
            // The player's army never falls (the mission would end).
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-100f, -100f), 0f).Invulnerable = true;
            return (world, mode);
        }

        private static void Run(SimWorld world, MissionMode mode, float seconds, Action each = null)
        {
            for (var t = 0f; t < seconds; t += Dt)
            {
                each?.Invoke();
                mode.Tick(world, Dt);
                world.Step(Dt);
                world.ClearEvents();
            }
        }

        private const string Ceasefire = "{\"id\": \"cf\", \"kind\": \"Ceasefire\", \"trigger\": {\"at\": 1}, \"params\": {\"seconds\": 20, \"size\": 3, \"enemyCp\": 20}, " +
                                         "\"reward\": {\"coins\": 150}}";

        [Test]
        public void TheCeasefireCostsWhoeverFiresFirstTheirReward()
        {
            // Kept: no weapon of ours picks the sworn column on its own, even beside it; at the end both sides are paid and the
            // column is the enemy's to fight with again.
            var (world, mode) = Start(Mission(Ceasefire, "\"cf\"", ", \"general\": \"varga\""));
            Run(world, mode, 2f);
            var s = mode.Events.States[0];
            Assert.AreEqual(EventPhase.Running, s.Phase);
            var column = world.Vehicles.Where(v => v.IsAlive && v.Team == 1 && v.Truce).ToList();
            Assert.AreEqual(3, column.Count, "the sworn column");
            Assert.IsTrue(column.All(v => v.HoldFire && v.Scripted));
            var watcher = world.SpawnVehicle("main_battle_tank", 0, column[0].Position + new Vector2(0f, -22f), 0f);
            watcher.Invulnerable = true;
            Run(world, mode, 6f);
            Assert.IsTrue(column.All(v => v.Hp >= v.MaxHp), "nothing of ours fires on it unordered");
            Assert.AreEqual(EventPhase.Running, s.Phase);
            world.TryGetEconomy(1, out var foe);
            foe.Cp = 0f;
            Run(world, mode, 14f);
            Assert.IsTrue(mode.Events.Log.Any(l => l.moment == "end"), "kept to the end");
            Assert.AreEqual(EventPhase.Done, s.Phase);
            Assert.IsTrue(mode.Events.Earned.Any(e => e.kind == "coins" && e.amount == 150), "our reward");
            Assert.GreaterOrEqual(foe.Cp, 20f, "theirs");
            Assert.IsTrue(column.Where(v => v.IsAlive).All(v => !v.Truce && !v.HoldFire && !v.Scripted), "the column is let go");

            // We fire first (an ordered attack still can): ours is lost, theirs is paid now.
            (world, mode) = Start(Mission(Ceasefire, "\"cf\"", ", \"general\": \"varga\""));
            Run(world, mode, 2f);
            column = world.Vehicles.Where(v => v.IsAlive && v.Team == 1 && v.Truce).ToList();
            var gunner = world.SpawnVehicle("main_battle_tank", 0, column[0].Position + new Vector2(0f, -22f), 0f);
            gunner.Invulnerable = true;
            world.TryGetEconomy(1, out foe);
            foe.Cp = 0f;
            Run(world, mode, 0.5f);
            world.SubmitPlayer(new Command(CommandType.Attack, 0, new[] { gunner.Id }, column[0].Position, column[0].Id, manual: true));
            Run(world, mode, 6f);
            s = mode.Events.States[0];
            Assert.IsTrue(mode.Events.Log.Any(l => l.moment == "broken"), "we broke it");
            Assert.AreEqual(EventPhase.Failed, s.Phase);
            Assert.IsFalse(mode.Events.Earned.Any(e => e.kind == "coins"), "our reward is lost");
            Assert.GreaterOrEqual(foe.Cp, 20f, "theirs is paid");

            // They fire first ("breakAt"): theirs is lost, ours is paid now.
            (world, mode) = Start(Mission(Ceasefire, "{\"id\": \"cf\", \"params\": {\"breakAt\": 4}}", ", \"general\": \"varga\""));
            world.TryGetEconomy(1, out foe);
            Run(world, mode, 2f);
            foe.Cp = 0f;
            Run(world, mode, 4f);
            s = mode.Events.States[0];
            Assert.IsTrue(mode.Events.Log.Any(l => l.moment == "betrayed"), "they broke it");
            Assert.AreEqual(EventPhase.Done, s.Phase);
            Assert.IsTrue(mode.Events.Earned.Any(e => e.kind == "coins" && e.amount == 150), "our reward");
            Assert.Less(foe.Cp, 20f, "theirs is lost");
        }

        // ================================================================== the intel files

        [Test]
        public void AnInterceptedConvoysIntelFileGoesIntoTheDossier()
        {
            var (world, mode) = Start(Mission("{\"id\": \"i\", \"kind\": \"SideObjective\", \"trigger\": {\"at\": 1}, " +
                                              "\"params\": {\"type\": \"intercept\", \"count\": 2, \"seconds\": 60}, \"reward\": {\"coins\": 150}}",
                "{\"id\": \"i\", \"reward\": {\"intel\": \"c4.balance\"}}"));
            Run(world, mode, 2f);
            foreach (var t in world.Vehicles.Where(v => v.Team == 1 && v.Def.Id == MissionEventSystem.Truck).ToList()) t.Hp = 0f;
            Run(world, mode, 1f);
            Assert.IsTrue(mode.Events.Earned.Any(e => e.kind == "intel" && e.id == "c4.balance"), "the file comes with the trucks");
            Assert.IsTrue(mode.Events.Earned.Any(e => e.kind == "coins" && e.amount == 150), "with the library's coins");

            // The battle's reward carries it (won or lost: the files were taken either way) and the claim pays it into the dossier.
            PlayerProfile.ResetForTests();
            var file = Narrative.Intel.Single(f => f.Id == "c4.balance");
            Assert.IsFalse(Narrative.Found(file));
            var reward = new MatchReward { MissionId = "c4m12" };
            foreach (var (kind, _, id) in mode.Events.Earned)
                if (kind == "intel") reward.Intel.Add(id);
            Assert.AreEqual(new[] { "c4.balance" }, Narrative.FoundBy(reward, false).Select(f => f.Id).ToArray(), "shown on the result card");
            reward.Claim();
            Assert.IsTrue(PlayerProfile.IntelRecovered("c4.balance"));
            Assert.IsTrue(Narrative.Found(file), "in the dossier's Intel files");
            Assert.IsEmpty(Narrative.FoundBy(reward, false), "once");
        }

        // ================================================================== one seed of three missions

        private static (SimWorld world, MissionSession session) Begin(string id)
        {
            var def = Campaign.Everything.Single(m => m.Id == id);
            CampaignTests.PlayerAt(def, Catalog);
            var world = new SimWorld(Catalog, Campaign.LoadMap(def), seed: 1);
            var session = (MissionSession)ModeSession.Create(GameModeKind.Campaign, false, world, 1);
            return (world, session);
        }

        /// <summary>The vehicles that came onto the player's side (by def), over the battle so far.</summary>
        private static readonly HashSet<string> Arrived = new();

        private static void Play(SimWorld world, MissionSession session, float seconds)
        {
            for (var t = 0f; t < seconds && session.Mode.Result == null; t += Dt)
            {
                session.Mode.Tick(world, Dt);
                session.TickAi(world, Dt);
                world.Step(Dt);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.VehicleSpawned && e.Team == 0 && e.DefId != null) Arrived.Add(e.DefId);
                world.ClearEvents();
            }
        }

        private static bool Happened(SimWorld world, string instance, params string[] moments) =>
            world.MissionEvents.Any(e => e.Log.Any(l => l.instance == instance && moments.Contains(l.moment)));

        [Test, Timeout(900000)]
        public void ThreeMissionsStartAndTheirEventsFire()
        {
            // Early: chapter 2's first battle, five minutes held at Dunebreak: the oil convoy, Varga's wave, the sandstorm.
            var (world, session) = Begin("c2m01");
            Play(world, session, 215f);
            Assert.IsNull(session.Mode.Result, $"c2m01 is under way at {world.Time:0} s");
            Assert.IsTrue(Happened(world, "oil_convoy", "start"), "c2m01: the oil convoy");
            Assert.IsTrue(Happened(world, "enemy_wave", "start"), "c2m01: Varga's wave");
            Assert.IsTrue(Happened(world, "sandstorm", "start"), "c2m01: the sandstorm");

            // Mid-campaign: the Hollow Dam's ceasefire, called with the mission's opening lines and over by noon.
            (world, session) = Begin("c6m14");
            Play(world, session, 165f);
            Assert.IsTrue(Happened(world, "ceasefire", "start"), "c6m14: the ceasefire");
            if (world.Time > 160.0) Assert.IsTrue(Happened(world, "ceasefire", "end", "broken", "betrayed"), "c6m14: over by noon");

            // Chapter 12's operation: its own and its first stage's events, then its Varga stage's Total Offensive against the
            // enemy's reinforcements from every side (the one allied wave as strong as the enemy's).
            Arrived.Clear();
            (world, session) = Begin("c12m10");
            Play(world, session, 190f);
            Assert.IsNull(session.Mode.Result, "c12m10 is under way");
            var op = session.Operation;
            var def = Campaign.Everything.Single(m => m.Id == "c12m10");
            // The first stage's (at 90 s) while the brigade is still at it (the auto commander may take the point sooner).
            if (op.Path.Count == 1) Assert.IsTrue(Happened(world, "nadia_intel", "start", "skipped"), "c12m10: the first stage's event");
            Assert.IsTrue(Happened(world, "ew_blackout", "start"), "c12m10: the operation's own");
            // On to the Varga stage when the battle has not reached it yet (the auto commanders are often there by now).
            var command = def.Stages.ToList().FindIndex(s => s.Id == "command");
            if (!op.Path.Contains(command)) Assert.IsTrue(op.ChangePlan(world, new MissionEventDef { Stage = "command" }), "on to the Varga stage");
            Play(world, session, 60f);
            var stage = world.MissionEvents.First(e => e.States.Any(s => s.Def.Id == "total_offensive"));
            UnityEngine.Debug.Log($"PROMPT23E SMOKE c12m10 at {world.Time:0} s: " + string.Join(" > ", op.Path.Select(i => def.Stages[i].Id)));
            var offensive = stage.States.Single(s => s.Def.Id == "total_offensive");
            var wave = stage.States.Single(s => s.Def.Id == "enemy_all_directions");
            Assert.AreEqual(1, offensive.Fired, "the Total Offensive came");
            Assert.AreEqual(1, wave.Fired, "and the enemy from every side");
            Assert.IsTrue(Arrived.Contains("mara_behemoth"), "Mara's Behemoth among them");
            Assert.GreaterOrEqual(offensive.Strength, 0.6f * wave.Strength, $"as strong as the enemy's ({offensive.Strength:0} against {wave.Strength:0})");
        }
    }
}
