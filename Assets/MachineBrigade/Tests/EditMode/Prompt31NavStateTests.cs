using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Navigation;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 31 L3 (DECISIONS "Prompt 31 L3"): the prebuilt NavGrid states. Every state of every campaign site keeps the
    /// battlefield joined; a state that would cut the anchors apart or seal ground off is refused at load and never comes in; a
    /// switch comes in on the tick it was asked for and puts nobody on closed ground; a battle and its replay (the same seed,
    /// the same commands) switch on the same step and end in the same fingerprint; a snapshot restores the states. Written for
    /// the lead to run (the owner's rule: agents write tests, they do not run them).
    /// </summary>
    public class Prompt31NavStateTests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SimWorld Field(int seed = 1) => new(Catalog, new MapDefinition("field", 300f,
            new[] { new TeamStart(0, new Vector2(-108.75f, -108.75f)), new TeamStart(1, new Vector2(108.75f, 108.75f)) },
            new List<PropPlacement>(), new List<UnitPlacement>()), seed);

        private static NavSiteDef Site(string id, params NavBlock[] closed) =>
            new(id, new[] { new NavStateDef("open"), new NavStateDef("shut", closed) }, "open");

        // ================================================================== the campaign's sites

        [Test]
        public void EveryStateOfEveryCampaignSiteKeepsTheBattlefieldJoined()
        {
            var bad = new List<string>();
            var checkedSites = 0;
            foreach (var m in Campaign.Everything.Where(m => m.NavSites.Count > 0))
            {
                if (!Campaign.MapExists(m))
                {
                    bad.Add($"{m.Id}: no map file for its nav sites");
                    continue;
                }
                var world = new SimWorld(Catalog, Campaign.LoadMap(m), 1);
                world.BuildNavSites(m.NavSites, m.TargetNear is { } near ? new[] { near } : null);
                bad.AddRange(world.NavSiteProblems.Select(p => $"{m.Id}: {p}"));
                var anchors = world.Map.Teams.Select(t => t.Rally).Concat(world.Map.Points.Select(p => p.Position)).ToList();
                foreach (var site in world.NavStates.Sites)
                {
                    checkedSites++;
                    foreach (var state in site.Def.States)
                    {
                        // Each state brought in for real (at its tick), the anchors joined over the ground it leaves.
                        Assert.IsTrue(world.NavStates.Schedule(site.Id, state.Name, world.Tick + 1, world.Tick), $"{m.Id} {site.Id} {state.Name}");
                        world.Step(Dt);
                        Assert.AreEqual(state.Name, site.ActiveName);
                        var home = Region(world.Grid, anchors[0]);
                        foreach (var a in anchors)
                            if (Region(world.Grid, a) != home) bad.Add($"{m.Id}: {site.Id} {state.Name} cuts ({a.X:0}, {a.Y:0}) off");
                    }
                }
            }
            Assert.Greater(checkedSites, 0, "the campaign builds prebuilt states (i1m01's gate, c11m10's landing sites)");
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        private static int Region(NavGrid grid, Vector2 p) =>
            grid.RegionOf(p) is var r && r > 0 ? r : grid.TryNearestWalkable(p, 5, out var open) ? grid.RegionOf(open) : 0;

        // ================================================================== the load-time check

        [Test]
        public void AStateThatCutsTheMapInTwoOrSealsAPocketIsRefused()
        {
            var world = Field();
            // A wall across the whole map: the rallies are cut apart.
            var wall = Site("wall", new NavBlock(new Vector2(0f, 0f), 300f, 4f));
            // A ring round a yard: the yard's ground would be sealed off.
            var ring = new NavSiteDef("ring", new[]
            {
                new NavStateDef("open"),
                new NavStateDef("shut", new[]
                {
                    new NavBlock(new Vector2(50f, 70f), 40f, 2f), new NavBlock(new Vector2(50f, 30f), 40f, 2f),
                    new NavBlock(new Vector2(30f, 50f), 2f, 40f), new NavBlock(new Vector2(70f, 50f), 2f, 40f),
                }),
            });
            var gate = Site("gate", new NavBlock(new Vector2(-40f, 0f), 10f, 2f));
            world.BuildNavSites(new[] { wall, ring, gate });
            Assert.AreEqual(2, world.NavSiteProblems.Count, string.Join("\n", world.NavSiteProblems));
            Assert.IsFalse(world.NavStates.CanSwitch("wall", "shut"));
            Assert.IsFalse(world.NavStates.CanSwitch("ring", "shut"));
            Assert.IsTrue(world.NavStates.CanSwitch("gate", "shut"), "a gate with a way round is fine");
            Assert.IsFalse(world.NavStates.Schedule("wall", "shut", 5, world.Tick), "a refused state never comes in");
            Assert.IsNotNull(world.NavStates.Sites[0].Refusal(1));
            // The check left the ground as it was (the initial states only).
            Assert.IsTrue(world.Grid.IsWalkable(new Vector2(0f, 0f)));
            Assert.IsTrue(world.Grid.IsWalkable(new Vector2(50f, 70f)));
        }

        [Test]
        public void SitesAreBuiltAtLoadOnly()
        {
            var world = Field();
            world.Step(Dt);
            Assert.IsTrue(world.NavStates.Locked);
            Assert.Throws<System.InvalidOperationException>(() => world.NavStates.Define(Site("late", new NavBlock(Vector2.Zero, 4f, 4f))));
        }

        // ================================================================== the switch

        [Test]
        public void ASwitchComesInOnItsTickAndPutsNobodyOnClosedGround()
        {
            var world = Field();
            world.BuildNavSites(new[] { Site("block", new NavBlock(new Vector2(0f, 0f), 20f, 20f)) });
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var at = world.Tick + 6;
            Assert.IsTrue(world.NavStates.Schedule("block", "shut", at, world.Tick));
            while (world.Tick < at - 1)
            {
                world.Step(Dt);
                Assert.IsTrue(world.Grid.IsWalkable(new Vector2(0f, 0f)), "not before its tick");
            }
            world.Step(Dt);
            Assert.AreEqual(at, world.NavStates.Sites[0].SwitchedAt);
            Assert.IsFalse(world.Grid.IsWalkable(new Vector2(0f, 0f)), "closed on its tick");
            Assert.IsTrue(world.Grid.IsWalkable(tank.Position), "the tank was put off the closed ground");
            Assert.AreEqual(world.Grid.MainRegion, world.Grid.RegionOf(tank.Position), "on the open battlefield");
            Assert.AreEqual(1, world.NavStates.Displaced);
            // Back open: the ground is as it was.
            Assert.IsTrue(world.NavStates.Schedule("block", "open", world.Tick + 1, world.Tick));
            world.Step(Dt);
            Assert.IsTrue(world.Grid.IsWalkable(new Vector2(0f, 0f)));
        }

        [Test]
        public void ASnapshotRestoresTheStates()
        {
            var world = Field();
            world.BuildNavSites(new[] { Site("gate", new NavBlock(new Vector2(-40f, 0f), 10f, 2f)) });
            world.NavStates.Schedule("gate", "shut", world.Tick + 1, world.Tick);
            world.Step(Dt);
            var snapshot = world.NavStates.Snapshot();
            var loaded = Field();
            loaded.BuildNavSites(new[] { Site("gate", new NavBlock(new Vector2(-40f, 0f), 10f, 2f)) });
            loaded.NavStates.Restore(snapshot);
            Assert.AreEqual("shut", loaded.NavStates.ActiveOf("gate"));
            Assert.AreEqual(world.Grid.IsWalkable(new Vector2(-40f, 0f)), loaded.Grid.IsWalkable(new Vector2(-40f, 0f)));
        }

        // ================================================================== the events and the replay

        private const string Gate = "{\"id\": \"gate_shuts\", \"kind\": \"GroundChange\", \"trigger\": {\"at\": 2}, \"lead\": 10, " +
                                    "\"params\": {\"navSite\": \"gate\", \"navState\": \"shut\"}}";

        private static MissionDef Mission(string events, string refs, string extra = "") =>
            MissionDef.ListFromJson("{\"eventLibrary\": {\"events\": [" + events + "]}, \"missions\": [{\"id\": \"p31l3\", \"map\": \"field\", " +
                                    "\"goal\": \"Survive\", \"surviveSeconds\": 5000, \"enemyAi\": \"none\", \"navStates\": [{\"id\": \"gate\", " +
                                    "\"initial\": \"open\", \"states\": [{\"name\": \"open\"}, {\"name\": \"shut\", \"blocks\": [{\"x\": -40, \"z\": 0, " +
                                    "\"w\": 10, \"d\": 2}]}]}]" + extra + ", \"missionEvents\": [" + refs + "]}]}")[0];

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

        [Test]
        public void TheGateShutsAfterItsWarningWithItsPlaceOnTheMinimap()
        {
            var (world, mode) = Start(Mission(Gate, "\"gate_shuts\""));
            Run(world, mode, 3f);
            var s = mode.Events.States[0];
            Assert.AreEqual(EventPhase.Warned, s.Phase);
            var lead = s.StartAt - s.WarnedAt;
            Assert.GreaterOrEqual(lead, 8.0 - 1e-6);
            Assert.LessOrEqual(lead, 12.0 + 1e-6);
            Assert.AreEqual(1, s.Marks.Count, "the gate on the minimap");
            Assert.AreEqual("open", world.NavStates.ActiveOf("gate"));
            Run(world, mode, 11f);
            Assert.AreEqual("shut", world.NavStates.ActiveOf("gate"));
            Assert.IsFalse(world.Grid.IsWalkable(new Vector2(-40f, 0f)));
        }

        [Test]
        public void AReplayMeetsTheSameStatesOnTheSameStep()
        {
            var def = Mission(Gate, "\"gate_shuts\"");
            var (a, modeA) = Start(def, 7);
            var (b, modeB) = Start(def, 7);
            var first = Run(a, modeA, 20f);
            var second = Run(b, modeB, 20f);
            CollectionAssert.AreEqual(first, second, "the same fingerprint at every mark");
            Assert.AreEqual(a.NavStates.Sites[0].SwitchedAt, b.NavStates.Sites[0].SwitchedAt);
            Assert.Greater(a.NavStates.Sites[0].SwitchedAt, 0);
            Assert.AreEqual(a.StateHash(), b.StateHash());
        }

        [Test]
        public void TheSandstormRollsOverOneHalf()
        {
            const string storm = "{\"id\": \"st\", \"kind\": \"SandstormTurn\", \"trigger\": {\"at\": 1}, \"lead\": 8, " +
                                 "\"params\": {\"half\": \"east\", \"sight\": 0.6, \"clear\": 1.2, \"seconds\": 20, \"hold\": 30}}";
            var (world, mode) = Start(Mission(storm, "\"st\""));
            Run(world, mode, 2f);
            Assert.AreEqual(EventPhase.Warned, mode.Events.States[0].Phase);
            Assert.AreEqual(3, mode.Events.States[0].Marks.Count);
            Run(world, mode, 30f);
            Assert.IsTrue(world.StormActive);
            Assert.AreEqual(0.6f, world.StormSight(new Vector2(80f, 0f)), 0.01f, "the storm's half");
            Assert.AreEqual(1.2f, world.StormSight(new Vector2(-80f, 0f)), 0.01f, "the half that clears");
            Run(world, mode, 60f);
            Assert.IsFalse(world.StormActive, "it passes after its hold");
            Assert.AreEqual(EventPhase.Done, mode.Events.States[0].Phase);
        }

        [Test]
        public void TheBlackoutShutsTheGridTowersOfBothSides()
        {
            const string power = "{\"id\": \"bo\", \"kind\": \"CityBlackout\", \"trigger\": {\"at\": 1}, \"lead\": 10, \"params\": {\"seconds\": 20, \"outage\": 40}}";
            var (world, mode) = Start(Mission(power, "\"bo\""));
            var ours = world.SpawnVehicle("radar_station", 0, new Vector2(-60f, -60f), 0f);
            var theirs = world.SpawnVehicle("radar_station", 1, new Vector2(60f, 60f), 0f);
            var gun = world.SpawnVehicle("gun_turret", 1, new Vector2(60f, 40f), 0f);
            Run(world, mode, 2f);
            Assert.AreEqual(2, mode.Events.States[0].Marks.Count, "both radars on the minimap");
            Run(world, mode, 12f);
            Assert.IsTrue(ours.Stunned && theirs.Stunned, "both sides' grid towers are off");
            Assert.IsFalse(gun.Stunned, "a gun turret is not on the grid");
            Run(world, mode, 25f);
            Assert.Less(world.WeatherSight, 0.9f, "the street lights are out");
        }

        [Test]
        public void ThePodsStandOnTheirSitesAndOpenThemWhenTheyFall()
        {
            const string pods = "{\"id\": \"op\", \"kind\": \"OrbitalPods\", \"trigger\": {\"at\": 1}, \"lead\": 10, " +
                                "\"params\": {\"sites\": [\"pad\"], \"towers\": [\"gun_turret\"], \"fall\": 4}}";
            const string pad = ", \"navStates\": [{\"id\": \"pad\", \"initial\": \"clear\", \"states\": [{\"name\": \"clear\"}, {\"name\": \"landed\", " +
                               "\"blocks\": [{\"x\": 40, \"z\": 40, \"w\": 4, \"d\": 4}]}]}]";
            var def = MissionDef.ListFromJson("{\"eventLibrary\": {\"events\": [" + pods + "]}, \"missions\": [{\"id\": \"p31pods\", \"map\": \"field\", " +
                                              "\"goal\": \"Survive\", \"surviveSeconds\": 5000, \"enemyAi\": \"none\"" + pad +
                                              ", \"missionEvents\": [\"op\"]}]}")[0];
            var (world, mode) = Start(def);
            Run(world, mode, 18f);
            Assert.AreEqual("landed", world.NavStates.ActiveOf("pad"));
            var tower = world.Vehicles.FirstOrDefault(v => v.IsAlive && v.Team == 1 && v.Def.Id == "gun_turret");
            Assert.IsNotNull(tower, "the pod stood up as a tower");
            Assert.IsFalse(world.Grid.IsWalkable(new Vector2(40f, 40f)));
            tower.Hp = 0f;
            Run(world, mode, 2f);
            Assert.AreEqual("clear", world.NavStates.ActiveOf("pad"), "its ground opens when it falls");
            Assert.IsTrue(world.Grid.IsWalkable(new Vector2(40f, 40f)));
        }
    }
}
