using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Navigation;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 33 L2 (DECISIONS "Prompt 33 L2 / L3"): the edge types and the ingress contract. Every side of every map file is
    /// covered by edge stretches without a gap; the maps with sea declare it (Ironport's as a harbour); every entry gate of
    /// the data stands on open ground joined to the battlefield, its approach running from beyond the rectangle to it; every
    /// spawn point has a gate and an edge point near a data gate stands on it; the same map gives the same points twice.
    /// Written for the lead to run (the owner's rule: agents write tests, they do not run them).
    /// </summary>
    public class Prompt33EdgeTests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static readonly string[] Battlefields =
        {
            "ashfield", "borderbridge", "capital", "coralisles", "dunebreak", "emberridge", "foundry", "frostpeak", "greenvale", "hydrodam",
            "ironport", "junglepass", "landingbeach", "launchsite", "lighthousebay", "metrocity", "openpit", "orbitalgate", "redrock", "rustyard",
            "saltflat", "skyhold", "swamp", "veyra_old_quarter", "whiteout",
        };

        private static readonly string[] Variants = { "_conquest", "_sandbox", "_siege", "_long" };

        private static IEnumerable<string> Files()
        {
            foreach (var b in Battlefields)
                foreach (var v in Variants)
                    if (UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/maps/" + b + v) != null)
                        yield return b + v;
        }

        [Test]
        public void EverySideIsCoveredByEdgeStretches()
        {
            var problems = new List<string>();
            foreach (var id in Files())
            {
                var map = GameContent.LoadMap(id);
                if (map.Edges.Segments.Count == 0)
                {
                    problems.Add(id + ": no edges");
                    continue;
                }
                foreach (var side in new[] { "N", "E", "S", "W" })
                {
                    var along = side is "N" or "S" ? (map.Min.X, map.Max.X) : (map.Min.Y, map.Max.Y);
                    var run = map.Edges.Segments.Where(s => s.Side == side).OrderBy(s => s.From).ToList();
                    if (run.Count == 0 || System.Math.Abs(run[0].From - along.Item1) > 0.05f || System.Math.Abs(run[run.Count - 1].To - along.Item2) > 0.05f)
                        problems.Add(id + ": side " + side + " not covered end to end");
                    for (var i = 1; i < run.Count; i++)
                        if (System.Math.Abs(run[i].From - run[i - 1].To) > 0.05f) problems.Add(id + ": side " + side + " has a gap at " + run[i - 1].To);
                }
                foreach (var c in map.Edges.Corners)
                    Assert.IsFalse(string.IsNullOrEmpty(c.Piece), id + ": a corner without its piece");
            }
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void TheMapsWithSeaDeclareIt()
        {
            foreach (var b in new[] { "landingbeach", "lighthousebay", "coralisles", "ironport", "rustyard" })
                foreach (var v in new[] { "_conquest", "_sandbox", "_siege" })
                    Assert.IsTrue(GameContent.LoadMap(b + v).Edges.HasSea, b + v + " declares its sea");
            var ironport = GameContent.LoadMap("ironport_conquest");
            var north = ironport.Edges.At("N", 0f);
            Assert.IsNotNull(north, "Ironport's north side has a stretch");
            Assert.AreEqual(EdgeType.Sea, north.Type, "Ironport's quay faces the sea");
            Assert.AreEqual(EdgeModifier.Harbor, north.Modifier, "Ironport's sea is a harbour");
            foreach (var b in new[] { "ashfield", "greenvale", "skyhold" })
                Assert.IsFalse(GameContent.LoadMap(b + "_conquest").Edges.HasSea, b + " has no sea");
        }

        [Test]
        public void EveryDataGateStandsOnTheBattlefieldWithItsApproachOutside()
        {
            var problems = new List<string>();
            foreach (var b in Battlefields)
            {
                var map = GameContent.LoadMap(b + "_conquest");
                Assert.IsNotEmpty(map.EntryGates, b + " has entry gates");
                var world = new SimWorld(Catalog, map, 1);
                var main = world.Grid.MainRegion;
                foreach (var g in map.EntryGates)
                {
                    if (!world.Grid.IsWalkable(g.Position) || world.Grid.RegionOf(g.Position) != main) problems.Add(b + ": gate " + g.Id + " is not on the battlefield's ground");
                    if (g.Path.Count < 2 || Vector2.Distance(g.Path[g.Path.Count - 1], g.Position) > 0.1f) problems.Add(b + ": gate " + g.Id + "'s approach does not end at it");
                    else if (map.Contains(g.Path[0]) && g.Kind != EntryGateKind.Sea) problems.Add(b + ": gate " + g.Id + "'s approach starts inside the map");
                    if (g.VisualIngressLength < EntryGate.OuterLength - 0.1f) problems.Add(b + ": gate " + g.Id + "'s approach is too short");
                }
            }
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void EverySpawnPointHasAGateAndEdgePointsStandOnTheData()
        {
            foreach (var b in new[] { "ashfield", "ironport", "landingbeach", "metrocity", "swamp" })
            {
                var map = GameContent.LoadMap(b + "_conquest");
                var world = new SimWorld(Catalog, map, 1);
                var points = SpawnPoints.Build(world);
                Assert.IsNotEmpty(points.All, b + " has spawn points");
                foreach (var p in points.All)
                {
                    Assert.IsNotNull(p.Gate, b + ": " + p.Id + " has an entry gate");
                    if (p.Kind != SpawnKind.Edge || p.Gate.Implicit) continue;
                    Assert.Less(Vector2.Distance(p.Position, p.Gate.Position), 0.01f, b + ": " + p.Id + " stands on its gate");
                    Assert.AreEqual(p.Gate.Inward.X, p.Inward.X, 1e-4f, b + ": " + p.Id + " comes in the gate's way");
                }
                Assert.IsTrue(points.All.Any(p => p.Kind == SpawnKind.Edge && !p.Gate.Implicit), b + ": an edge point stands on a data gate");
            }
        }

        [Test]
        public void TheSameMapGivesTheSameGatesTwice()
        {
            string Sig()
            {
                var world = new SimWorld(Catalog, GameContent.LoadMap("borderbridge_conquest"), 3);
                return string.Join("|", SpawnPoints.Build(world).All.Select(p => p.Id + ":" + p.Gate.Id + ":" + p.Position.X.ToString("F3") + "," + p.Position.Y.ToString("F3")));
            }
            Assert.AreEqual(Sig(), Sig(), "the gates are deterministic");
        }

        [Test]
        public void AnImplicitGateRunsBackOutOverTheNearestEdge()
        {
            var map = GameContent.LoadMap("ashfield_conquest");
            var g = EntryGate.At(map, "t", EntryGateKind.Edge, new Vector2(140f, 0f), new Vector2(-1f, 0f));
            Assert.AreEqual(3, g.Path.Count, "out there, the edge, the gate");
            Assert.AreEqual(map.Max.X + EntryGate.OuterLength, g.Path[0].X, 0.01f, "the approach starts beyond the east edge");
            Assert.AreEqual(map.Max.X, g.Path[1].X, 0.01f, "it crosses the edge");
            Assert.AreEqual(map.Max.X - 140f + EntryGate.OuterLength, g.VisualIngressLength, 0.01f, "its length is the way to the gate");
            Assert.IsTrue(g.Implicit);
        }
    }
}
