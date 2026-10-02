using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Views;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 33 L6: the biome dressing is decoration only. Eight biomes, each with every zone's set; every model is a
    /// `dress_*` GLB that exists and is never a gameplay prop (so nothing in the layer can block a route or a sight
    /// line, and the map audit's gameplay layer stays the map files' props); densities fall off from the edge band
    /// outwards; the data never reaches the simulation (the Sim assembly does not reference the view's).
    /// </summary>
    public class MapDressingTests
    {
        private const string ModelsFolder = "Assets/MachineBrigade/Resources/Models";

        private static readonly string[] Biomes = { "temperate", "desert", "snow", "harbor", "jungle", "volcanic", "urban", "coast" };

        [Test]
        public void EveryBiomeHasEveryZone()
        {
            MapDressing.Reset();
            var problems = new List<string>();
            foreach (var id in Biomes)
            {
                var b = MapDressing.Biome(id);
                if (b == null)
                {
                    problems.Add($"{id}: missing");
                    continue;
                }
                if (b.playSet == null || b.playSet.Length == 0) problems.Add($"{id}: no play set");
                if (b.bandSet == null || b.bandSet.Length == 0) problems.Add($"{id}: no band set");
                if (b.ringSet == null || b.ringSet.Length == 0) problems.Add($"{id}: no ring set");
                if (b.farSet == null || b.farSet.Length == 0) problems.Add($"{id}: no far set");
                if (!(b.band >= b.ring && b.ring > 0f && b.play > 0f && b.play < b.ring))
                    problems.Add($"{id}: densities play {b.play} band {b.band} ring {b.ring} should fall off: band >= ring > play > 0");
                if (b.edgeBand < 12f || b.edgeBand > 20f) problems.Add($"{id}: edge band {b.edgeBand}");
            }
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void EveryDressingModelIsADecorationGlb()
        {
            MapDressing.Reset();
            var gameplay = new HashSet<string>(GameContent.LoadCatalog().Props.Keys);
            var problems = new List<string>();
            foreach (var b in MapDressing.Data.biomes)
            {
                var all = new[] { b.playSet, b.bandSet, b.ringSet, b.farSet, b.seaSet, b.horizonSet }
                    .Where(s => s != null).SelectMany(s => s).ToList();
                if (!string.IsNullOrEmpty(b.farTree)) all.Add(b.farTree);
                foreach (var id in all.Distinct())
                {
                    if (!id.StartsWith("dress_")) problems.Add($"{b.id}: {id} is not a dress_* decoration model");
                    if (gameplay.Contains(id)) problems.Add($"{b.id}: {id} is a gameplay prop");
                    if (!File.Exists(Path.Combine(ModelsFolder, id + ".glb"))) problems.Add($"{b.id}: {id}.glb missing");
                }
            }
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void EveryMapIsDressedAsAKnownBiome()
        {
            MapDressing.Reset();
            var problems = new List<string>();
            foreach (var m in MapDressing.Data.maps)
            {
                if (MapDressing.Biome(m.biome) == null) problems.Add($"{m.id}: biome {m.biome}");
                if (m.density < 0.3f || m.density > 2f) problems.Add($"{m.id}: density {m.density}");
                if (m.hills < 0 || m.berms < 0 || m.ditches < 0 || m.dryBeds < 0) problems.Add($"{m.id}: negative relief count");
                if (!string.IsNullOrEmpty(m.farTree) && m.farTree != "none" && !File.Exists(Path.Combine(ModelsFolder, m.farTree + ".glb")))
                    problems.Add($"{m.id}: far tree {m.farTree}.glb missing");
            }
            Assert.GreaterOrEqual(MapDressing.Data.maps.Length, 25);
            Assert.IsEmpty(problems, string.Join("\n", problems));
            // The coasts and ports named by the prompt are dressed as such.
            Assert.AreEqual("harbor", MapDressing.ForMap("ironport_conquest").biome);
            Assert.AreEqual("coast", MapDressing.ForMap("lighthousebay_long").biome);
            Assert.AreEqual("coast", MapDressing.ForMap("coralisles_siege").biome);
        }

        [Test]
        public void DressingNeverReachesTheSimulation()
        {
            var sim = typeof(MachineBrigade.Sim.SimWorld).Assembly;
            var game = typeof(MapDressing).Assembly;
            Assert.IsFalse(sim.GetReferencedAssemblies().Any(a => a.Name == game.GetName().Name),
                "the simulation must not see the view's dressing");
        }
    }
}
