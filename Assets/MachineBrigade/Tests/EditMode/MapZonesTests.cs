using System.Collections.Generic;
using System.IO;
using NUnit.Framework;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Views;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 33 L1: the four zones. The outer ring covers the widest camera frame (furthest zoom, fixed tilt, every
    /// supported screen, the map's yaw) + 15 % on every side, so the camera never sees the end of the world; the data
    /// file's camera block and ring numbers agree with the code; every map family has its zones.
    /// </summary>
    public class MapZonesTests
    {
        private const string MapsFolder = "Assets/MachineBrigade/Resources/Data/maps";

        [Test]
        public void ReachFollowsTheFrameOnTheGround()
        {
            // Looking west (a long map): the screen's width runs along z, its height (stretched by the tilt) along x.
            var r = CameraFrame.Reach(-90f, 52f, 50f, 20f / 9f);
            Assert.AreEqual(50f / Mathf.Sin(52f * Mathf.Deg2Rad), r.x, 0.05f);
            Assert.AreEqual(50f * 20f / 9f, r.y, 0.05f);
            // Diagonal (a square map): both axes see (width + height) / sqrt 2.
            var d = CameraFrame.Reach(-45f, 52f, 42f, 20f / 9f);
            Assert.AreEqual(d.x, d.y, 0.01f);
            Assert.AreEqual((42f * 20f / 9f + 42f / Mathf.Sin(52f * Mathf.Deg2Rad)) * 0.70711f, d.x, 0.05f);
            // A turning camera would need the half-diagonal both ways.
            var turning = CameraFrame.Reach(-45f, 52f, 42f, 20f / 9f, rotates: true);
            Assert.Greater(turning.x, d.x * 0.99f);
        }

        [Test]
        public void RingCoversEveryScreenAtTheFurthestZoomWithPad()
        {
            foreach (var longMap in new[] { false, true })
            {
                var ring = CameraFrame.RingWidth(longMap);
                foreach (var aspect in CameraFrame.Aspects)
                {
                    var reach = CameraFrame.Reach(CameraFrame.Yaw(longMap), RtsCamera.TiltDegrees, CameraFrame.MaxZoom(longMap), aspect);
                    Assert.GreaterOrEqual(ring.x, reach.x * (1f + CameraFrame.Pad) - 0.01f, $"long {longMap} aspect {aspect}: x sides");
                    Assert.GreaterOrEqual(ring.y, reach.y * (1f + CameraFrame.Pad) - 0.01f, $"long {longMap} aspect {aspect}: z ends");
                }
            }
            Assert.AreEqual(new Vector2(120f, 120f), CameraFrame.RingWidth(false), "square maps (DECISIONS Prompt 33 L1)");
            Assert.AreEqual(new Vector2(73f, 128f), CameraFrame.RingWidth(true), "long maps (DECISIONS Prompt 33 L1)");
        }

        [Test]
        public void ZonesRunPlayEdgeRingHorizon()
        {
            var zones = new MapZones(Vector2.zero, 150f, 150f, 16f, 120f, 120f);
            Assert.AreEqual(MapZone.Play, zones.ZoneOf(new Vector2(0f, 0f)));
            Assert.AreEqual(MapZone.Play, zones.ZoneOf(new Vector2(150f, -150f)));
            Assert.AreEqual(MapZone.Edge, zones.ZoneOf(new Vector2(160f, 0f)));
            Assert.AreEqual(MapZone.Ring, zones.ZoneOf(new Vector2(170f, 0f)));
            Assert.AreEqual(MapZone.Ring, zones.ZoneOf(new Vector2(-280f, 280f)));
            Assert.AreEqual(MapZone.Horizon, zones.ZoneOf(new Vector2(300f, 0f)));
            Assert.AreEqual(286f, zones.OuterX, 0.001f);
            Assert.Greater(zones.HlodStart, zones.EdgeBand);
            Assert.Less(zones.HlodStart, zones.EdgeBand + zones.RingX);
            Assert.AreEqual(300f * 300f, zones.AreaWithin(0f), 0.1f);
            Assert.AreEqual(572f * 572f, zones.AreaWithin(999f), 0.1f);
        }

        [Test]
        public void DataCameraBlockMatchesTheCode()
        {
            MapDressing.Reset();
            var data = MapDressing.Data;
            Assert.IsNotNull(data.camera, "map_dressing.json has its camera block (Tools/maps/map_dressing.py)");
            var c = data.camera;
            Assert.AreEqual(RtsCamera.TiltDegrees, c.tiltDegrees, 1e-4f);
            Assert.AreEqual(RtsCamera.PlayerMaxZoom, c.maxZoomSquare, 1e-4f);
            Assert.AreEqual(CameraFrame.MaxZoom(true), c.maxZoomLong, 1e-4f);
            Assert.AreEqual(RtsCamera.SquareYaw, c.yawSquare, 1e-4f);
            Assert.AreEqual(RtsCamera.LongYaw, c.yawLong, 1e-4f);
            Assert.AreEqual(RtsCamera.Rotates, c.rotates);
            Assert.AreEqual(CameraFrame.Pad, c.pad, 1e-4f);
            Assert.AreEqual(CameraFrame.Aspects.Length, c.aspects.Length);
            for (var i = 0; i < c.aspects.Length; i++) Assert.AreEqual(CameraFrame.Aspects[i], c.aspects[i], 1e-3f);
            Assert.AreEqual(CameraFrame.RingWidth(false).x, c.ringSquare, 1e-3f);
            Assert.AreEqual(CameraFrame.RingWidth(true).x, c.ringLongSide, 1e-3f);
            Assert.AreEqual(CameraFrame.RingWidth(true).y, c.ringLongEnd, 1e-3f);
        }

        [Test]
        public void EveryMapFamilyHasZonesAndASeed()
        {
            MapDressing.Reset();
            var problems = new List<string>();
            var seeds = new Dictionary<int, string>();
            foreach (var path in Directory.GetFiles(MapsFolder, "*.json"))
            {
                var id = Path.GetFileNameWithoutExtension(path);
                var entry = MapDressing.ForMap(id);
                if (entry == null)
                {
                    problems.Add($"{id}: no map_dressing.json entry");
                    continue;
                }
                var band = MapDressing.EdgeBand(entry, MapDressing.BiomeFor(entry, null));
                if (band < 12f || band > 20f) problems.Add($"{id}: edge band {band}");
                if (entry.seed != MapDressing.StableSeed(entry.id)) problems.Add($"{id}: seed {entry.seed} is not the stable seed");
                if (MapDressing.Seed(id) != entry.seed) problems.Add($"{id}: Seed() does not read the entry");
                if (seeds.TryGetValue(entry.seed, out var other) && other != entry.id) problems.Add($"{id}: seed shared with {other}");
                seeds[entry.seed] = entry.id;
            }
            Assert.IsEmpty(problems, string.Join("\n", problems));
            Assert.AreEqual("veyra_old_quarter", MapDressing.Family("veyra_old_quarter_long"));
            Assert.AreEqual("greenvale", MapDressing.Family("greenvale_conquest"));
        }

        [Test]
        public void StableSeedIsFnv1a()
        {
            // The same numbers as Tools/maps/map_dressing.py's stable_seed.
            Assert.AreEqual(unchecked((int)(2166136261u & 0x7FFFFFFFu)), MapDressing.StableSeed(string.Empty));
            Assert.AreEqual(MapDressing.StableSeed("greenvale"), MapDressing.StableSeed("greenvale"));
            Assert.AreNotEqual(MapDressing.StableSeed("greenvale"), MapDressing.StableSeed("ashfield"));
        }
    }
}
