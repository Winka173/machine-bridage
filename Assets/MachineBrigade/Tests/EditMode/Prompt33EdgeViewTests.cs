using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 33 L2 view / L3 view (DECISIONS "Prompt 33 L2 view / L7"): every corner piece a map's edges data names has
    /// its prebuilt model in map_dressing.json (a dress_* GLB that exists and is no gameplay prop), the sea's and the edge
    /// types' dressing are decoration models, and every landmark model the maps name and no prop of theirs is gets a spot
    /// on that very map file, off the sea. Written, not run (the lead runs the suite).
    /// </summary>
    public class Prompt33EdgeViewTests
    {
        private const string ModelsFolder = "Assets/MachineBrigade/Resources/Models";

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

        private static bool Glb(string id) => File.Exists(Path.Combine(ModelsFolder, id + ".glb"));

        [Test]
        public void EveryCornerPieceHasItsModel()
        {
            MapDressing.Reset();
            var edges = MapDressing.Data.edges;
            Assert.IsNotNull(edges, "map_dressing.json has no edges block");
            var problems = new List<string>();
            foreach (var id in Files())
                foreach (var corner in GameContent.LoadMap(id).Edges.Corners)
                {
                    var piece = edges.Corner(corner.Piece);
                    if (piece == null) problems.Add($"{id}: no model for corner piece {corner.Piece}");
                    else if (!Glb(piece.model)) problems.Add($"{id}: {piece.model}.glb missing");
                }
            Assert.IsEmpty(problems.Distinct().ToList(), string.Join("\n", problems.Distinct()));
        }

        [Test]
        public void EdgeDressingIsDecorationOnly()
        {
            MapDressing.Reset();
            var edges = MapDressing.Data.edges;
            Assert.IsNotNull(edges);
            var gameplay = new HashSet<string>(GameContent.LoadCatalog().Props.Keys);
            var all = new List<string>();
            all.AddRange(edges.corners.Select(c => c.model));
            all.AddRange(edges.sea.waves);
            all.AddRange(edges.sea.ships);
            all.AddRange(edges.sea.islands);
            all.AddRange(new[] { edges.sea.surf, edges.sea.stack, edges.sea.quay, edges.sea.crane, edges.sea.containers, edges.sea.laneBuoy });
            foreach (var set in edges.sets) all.AddRange(set.set);
            all.Add(edges.rail.track);
            all.Add(edges.rail.portal);
            var problems = new List<string>();
            foreach (var id in all.Distinct())
            {
                if (!id.StartsWith("dress_")) problems.Add($"{id} is not a dress_* decoration model");
                if (gameplay.Contains(id)) problems.Add($"{id} is a gameplay prop");
                if (!Glb(id)) problems.Add($"{id}.glb missing");
            }
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void EveryLandmarkModelHasASpot()
        {
            MapDressing.Reset();
            var problems = new List<string>();
            foreach (var id in Files())
            {
                var spots = MapDressing.LandmarksFor(id);
                foreach (var landmark in GameContent.LoadMap(id).Landmarks)
                {
                    if (string.IsNullOrEmpty(landmark.Model)) continue;
                    var spot = spots.FirstOrDefault(s => s.id == landmark.Id);
                    if (spot == null) problems.Add($"{id}: {landmark.Id} ({landmark.Model}) has no spot");
                    else if (!Glb(spot.model)) problems.Add($"{id}: {spot.model}.glb missing");
                }
            }
            Assert.IsEmpty(problems, string.Join("\n", problems));
            Assert.IsTrue(MapDressing.LandmarksFor("ironport_conquest").Any(s => s.id == "ironport.outer_lighthouse"),
                "Ironport's lighthouse out at sea (c4m12.05)");
            Assert.IsFalse(MapDressing.LandmarksFor("ironport_long").Any(s => s.id == "ironport.outer_lighthouse"),
                "the long file's north side is no sea");
        }

        [Test]
        public void SeaMapsDeclareTheirSea()
        {
            foreach (var b in new[] { "landingbeach", "lighthousebay", "coralisles", "ironport", "rustyard" })
            {
                var edges = GameContent.LoadMap(b + "_conquest").Edges;
                Assert.IsTrue(edges.HasSea, b + " declares its sea");
                Assert.IsTrue(edges.Segments.Where(s => s.Type == EdgeType.Sea).All(s => !string.IsNullOrEmpty(s.Shore)),
                    b + ": every SEA stretch says its shore (BEACH / CLIFF / QUAY), which picks the view's coast dressing");
            }
        }
    }
}
