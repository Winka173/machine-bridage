using System;
using System.Collections.Generic;
using System.Diagnostics;
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
    /// Prompt 17 A-B: the long battlefields (300 x 480 m) and their layered bases. A sample of maps (the owner's
    /// token rule; every map is checked by Tools/maps/check_access.py when longmap.py writes it).
    /// </summary>
    public class LongMapTests
    {
        private static readonly string[] Sample = { "ashfield", "swamp", "metrocity" };

        /// <summary>
        /// Both sides reach each other and every stage's objective with every gate shut and every hardpoint holding
        /// the biggest tower, and a route across the long battlefield keeps to the path budget (logged for DECISIONS).
        /// </summary>
        [Test]
        public void LongMapsConnectBothSidesAndRoutesStayInBudget()
        {
            var catalog = GameContent.LoadCatalog();
            var biggest = MapConnectivityTests.Biggest(catalog);
            var lines = new List<string>();
            foreach (var id in Sample)
            {
                var map = GameContent.LoadMap(id + "_long");
                Assert.IsTrue(map.IsLong, $"{id}: long");
                Assert.AreEqual(300f, map.Width, 0.01f);
                Assert.That(map.Length, Is.InRange(450f, 500f));
                var world = new SimWorld(catalog, map, 1);
                var mode = new SiegeMode(new SiegeRules { FortressLoadout = biggest, AttackerBase = biggest, Manning = 1f, Arrivals = false });
                mode.Setup(world);
                Assert.IsTrue(map.Fortress is { Layered: true }, $"{id}: a layered base");
                Assert.AreEqual(1, mode.Stage, $"{id}: the forward works' relays first");
                Assert.IsTrue(world.TryGetRally(0, out var attacker));
                Assert.IsTrue(world.TryGetRally(1, out var defender));
                var finder = new PathFinder(world.Grid);
                var path = new List<Vector2>();
                var goals = new List<(string what, Vector2 at)> { ("the defenders' drop zone", defender), ("the HQ", map.Fortress!.Hq) };
                foreach (var p in world.Props)
                    if (p.IsAlive && p.Def.Id is "radar_station_prop" or "shield_generator") goals.Add((p.Def.Id, p.Position));
                foreach (var (what, at) in goals)
                {
                    Assert.IsTrue(finder.TryFindPath(attacker, at, path), $"{id}: a route from the attack to {what}");
                    Assert.Less(Vector2.Distance(path[path.Count - 1], at), 22f, $"{id}: the route reaches {what}");
                }
                // The other side: from the keep out to the attack's camp.
                Assert.IsTrue(finder.TryFindPath(defender, attacker, path), $"{id}: a route from the keep to the attack");
                Assert.Less(Vector2.Distance(path[path.Count - 1], attacker), 22f, $"{id}: the defenders reach the attack's camp");
                // Timed on a second pass (the first warms the code up): the longest routes, end to end.
                var watch = Stopwatch.StartNew();
                var searches = 0;
                for (var pass = 0; pass < 2; pass++)
                    foreach (var (_, at) in goals)
                    {
                        finder.TryFindPath(attacker, at, path);
                        finder.TryFindPath(at, attacker, path);
                        searches += 2;
                    }
                watch.Stop();
                var ms = watch.Elapsed.TotalMilliseconds / searches;
                var cells = world.Grid.Width * world.Grid.Height;
                // NavGrid, CoverGrid, the path finder's four arrays, the lane map's and the unit cost field's bytes a cell.
                var bytes = world.Grid.MemoryBytes + world.Cover.MemoryBytes + cells * (16L + 8L + 3L);
                lines.Add($"{id}_long: {world.Grid.Width} x {world.Grid.Height} cells, {bytes / 1024} KB, {ms:F2} ms a route ({searches})");
                // Budget: 8 MB of navigation memory; 25 ms a route end to end on the desktop (a hard ceiling: the
                // measured figure goes into DECISIONS 16A against the square maps').
                Assert.Less(bytes, 8L << 20, $"{id}: navigation memory");
                Assert.Less(ms, 25.0, $"{id}: time a route");
            }
            UnityEngine.Debug.Log("[LongMapTests] " + string.Join("; ", lines));
        }

        /// <summary>B.4: a layered base opens the long table's slots at each HQ level; a camp keeps the old table.</summary>
        [Test]
        public void LayeredBaseSlotsFollowTheLongTable()
        {
            var catalog = GameContent.LoadCatalog();
            var rules = catalog.Base;
            var table = new[] { (4, 1, 0, 1), (5, 2, 1, 1), (6, 3, 1, 2), (7, 4, 2, 3), (8, 5, 3, 4) };
            var map = GameContent.LoadMap("ashfield_long");
            var fortress = map.Fortress!;
            for (var level = 1; level <= 5; level++)
            {
                var (s, m, l, u) = table[level - 1];
                Assert.AreEqual((s, m, l, u), (rules.Slots(level, SlotSize.Small, true), rules.Slots(level, SlotSize.Medium, true),
                    rules.Slots(level, SlotSize.Large, true), rules.UtilitySlots(level, true)), $"long table at level {level}");
                var loadout = MapConnectivityTests.Biggest(catalog);
                loadout.HqLevel = level;
                var world = new SimWorld(catalog, map, 1);
                var b = world.Bases.EstablishFortress(0, loadout, BaseRole.Defend, fortress.Hq, fortress.Slots);
                int Count(Func<HardpointState, bool> which) => b.Slots.Count(x => !x.Def.Forward && which(x));
                Assert.AreEqual(s, Count(x => x.Def.Kind == HardpointKind.Tower && x.Def.Class == SlotSize.Small), $"small at {level}");
                Assert.AreEqual(m, Count(x => x.Def.Kind == HardpointKind.Tower && x.Def.Class == SlotSize.Medium), $"medium at {level}");
                Assert.AreEqual(l, Count(x => x.Def.Kind == HardpointKind.Tower && x.Def.Class == SlotSize.Large), $"large at {level}");
                Assert.AreEqual(Math.Min(u, loadout.Utilities.Count), Count(x => x.Def.Kind == HardpointKind.Utility && x.Tower != null), $"utility at {level}");
                Assert.AreEqual(rules.ForwardSlots(SlotSize.Small) + rules.ForwardSlots(SlotSize.Medium), b.Slots.Count(x => x.Def.Forward), "forward works");
            }
            // The 300 m camps keep their table.
            Assert.AreEqual((6, 3, 2, 3), (rules.Slots(5, SlotSize.Small), rules.Slots(5, SlotSize.Medium), rules.Slots(5, SlotSize.Large), rules.UtilitySlots(5)));
            // B.6: the strength counts the long base's extra slots and forward works.
            var full = MapConnectivityTests.Biggest(catalog);
            var layered = full.Clone();
            layered.Layered = true;
            Assert.Greater(BaseStrength.Score(catalog, layered), BaseStrength.Score(catalog, full) * 1.2f, "a layered base is stronger");
        }

        /// <summary>B.5: one plan fits the camps and the layered bases; each ignores the other's own places.</summary>
        [Test]
        public void OnePlanFitsCampsAndLayeredBases()
        {
            var camp = BaseSites.CampOf("ashfield");
            var layered = BaseSites.LongOf("ashfield");
            Assert.IsNotNull(camp);
            Assert.IsNotNull(layered);
            Assert.IsTrue(layered.Layered);
            var keys = SlotPlaces.Keys(layered);
            Assert.IsTrue(keys.Any(k => k.Place == SlotPlace.OuterGate) && keys.Any(k => k.Place == SlotPlace.OuterWall) &&
                          keys.Any(k => k.Place == SlotPlace.Yard) && keys.Any(k => k.Place == SlotPlace.InnerWall), "the new labels");
            var plan = new BasePlan();
            var towers = camp.Slots.Select(s => s.Kind == HardpointKind.Utility ? "repair_bay" : s.Class == SlotSize.Small ? "guard_tower"
                : s.Class == SlotSize.Medium ? "gun_turret" : "missile_battery").ToArray();
            plan.FromCamp(camp, towers);
            var before = plan.Assign(camp, out _);
            // Not laid out for the long battlefields yet: the layered base borrows the camp's towers by place.
            var onLong = plan.Resolve("ashfield_long", layered, 5);
            Assert.IsTrue(onLong.Layered);
            Assert.GreaterOrEqual(onLong.Small.Count(x => x.Length > 0), 6, "the small slots take the camp's small towers");
            Assert.GreaterOrEqual(onLong.Large.Count(x => x.Length > 0), 2, "the large slots take the camp's large towers");
            // An edit on the long base makes its places its own, and leaves every camp as it was.
            var gate = Array.FindIndex(keys, k => k.Place == SlotPlace.OuterGate && k.Size == SlotSize.Small);
            plan.Set("ashfield_long", layered, gate, "aa_turret");
            Assert.IsTrue(plan.HasLong);
            Assert.AreEqual("aa_turret", plan.Assign(layered, out _)[gate]);
            CollectionAssert.AreEqual(before, plan.Assign(camp, out _), "the camp ignores the long places");
            // Auto-arrange on a camp keeps the long places.
            plan.FromCamp(camp, towers);
            Assert.AreEqual("aa_turret", plan.Assign(layered, out _)[gate]);
        }
    }
}
