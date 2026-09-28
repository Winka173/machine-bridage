using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Editor;
using MachineBrigade.Game.Hud;
using NVector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 14 B.1-B.2: every map with a player camp has its Base screen picture (1024 x 640) and
    /// JSON in Resources/UI/Bases; the JSON was made from the map file as it is now (its SHA-1),
    /// with the current framing, so a map edit never ships with an old picture; and every arrow
    /// sits on the camp's edge pointing into the camp. When this fails, render again with
    /// graphics: -executeMethod MachineBrigade.Editor.BaseMapShots.RenderAll.
    /// </summary>
    public class BaseMapArtTests
    {
        [Test]
        public void EveryCampHasAFreshPicture()
        {
            var camps = BaseMapShots.Camps();
            Assert.GreaterOrEqual(camps.Count, 20, "every battlefield has a camp");
            var problems = new List<string>();
            foreach (var (id, map) in camps)
            {
                var data = BaseMapShots.ReadData(id);
                if (data == null || !File.Exists(BaseMapShots.PicturePath(id)))
                {
                    problems.Add($"{id}: no picture or JSON");
                    continue;
                }
                if (data.version != BaseMapShots.Version) problems.Add($"{id}: made by version {data.version}, the tool is at {BaseMapShots.Version}");
                if (data.sha1 != BaseMapShots.Hash(id)) problems.Add($"{id}: {id}_conquest.json changed since its picture was made");
                var (w, h) = PngSize(BaseMapShots.PicturePath(id));
                if (w != BaseMapArt.Width || h != BaseMapArt.Height || data.width != w || data.height != h)
                    problems.Add($"{id}: picture {w} x {h}, JSON {data.width} x {data.height}, should be {BaseMapArt.Width} x {BaseMapArt.Height}");
                var frame = BaseMapArt.FrameFor(map.BaseOf(0), BaseMapShots.DropZone(map));
                if (NVector2.Distance(frame.Centre, data.centre.V) > 0.05f || NVector2.Distance(frame.Up, data.up.V) > 0.01f ||
                    System.Math.Abs(frame.MetresWide - data.metresWide) > 0.05f)
                    problems.Add($"{id}: framed differently from the current framing");
            }
            Assert.IsEmpty(problems, "Make the base map pictures again (BaseMapShots.RenderAll, with graphics):\n" + string.Join("\n", problems));
        }

        [Test]
        public void EveryArrowPointsIntoTheCamp()
        {
            var problems = new List<string>();
            foreach (var (id, _) in BaseMapShots.Camps())
            {
                var data = BaseMapShots.ReadData(id);
                if (data == null) continue;
                var outline = data.outline.Select(p => p.V).ToList();
                if (data.arrows.Count is < 1 or > 4) problems.Add($"{id}: {data.arrows.Count} arrows");
                if (outline.Count < 3 || BaseMapArt.EdgeDistance(outline, data.hq.V) > -BaseMapArt.EdgePad + 0.01f)
                    problems.Add($"{id}: the camp's edge does not hold the HQ");
                foreach (var arrow in data.arrows)
                {
                    var at = arrow.at.V;
                    var dir = arrow.dir.V;
                    var edge = BaseMapArt.EdgeDistance(outline, at);
                    if (System.Math.Abs(dir.Length() - 1f) > 0.01f) problems.Add($"{id}: an arrow's direction is not a unit vector");
                    if (System.Math.Abs(edge) > 1f) problems.Add($"{id}: an arrow {edge:F1} m off the camp's edge");
                    if (BaseMapArt.EdgeDistance(outline, at + dir * 6f) > edge - 2.5f) problems.Add($"{id}: an arrow at ({at.X:F0}, {at.Y:F0}) does not point in");
                    // Room for the shaft behind the head, inside the picture.
                    var tail = at - dir * 10f;
                    var right = BaseMapArt.RightOf(data.up.V);
                    var u = 0.5f + NVector2.Dot(tail - data.centre.V, right) / data.metresWide;
                    var v = 0.5f - NVector2.Dot(tail - data.centre.V, data.up.V) / data.metresHigh;
                    if (u < 0f || u > 1f || v < 0f || v > 1f) problems.Add($"{id}: an arrow's shaft leaves the picture");
                }
            }
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void TheLoaderPutsTheCampFrontUp()
        {
            BaseMapArt.Reload();
            var picture = BaseMapArt.For("ashfield");
            Assert.IsNotNull(picture);
            Assert.IsNotNull(picture.Texture);
            Assert.AreEqual(1.6f, picture.Aspect, 1e-4f);
            var hq = picture.Hq;
            Assert.That(hq.x, Is.InRange(0f, 1f));
            Assert.That(hq.y, Is.InRange(0f, 1f));
            // Towards the enemy (the HQ's heading) is up the picture; the HQ's right is right.
            var heading = picture.Data.heading * UnityEngine.Mathf.Deg2Rad;
            var ahead = picture.ToPicture(picture.Data.hq.V + BaseMapArt.Front(heading) * 20f);
            Assert.Less(ahead.y, hq.y - 0.05f);
            Assert.AreEqual(hq.x, ahead.x, 1e-3f);
            Assert.AreEqual(0f, picture.PictureDirection(heading).x, 1e-3f);
            Assert.AreEqual(-1f, picture.PictureDirection(heading).y, 1e-3f);
            // Round trip.
            var world = new NVector2(-100f, -90f);
            Assert.Less(NVector2.Distance(world, picture.ToWorld(picture.ToPicture(world))), 1e-3f);
            Assert.Greater(picture.Arrows.Count, 0);
            Assert.AreEqual(picture.Arrows.Count, picture.ArrowRoutes.Count);
            foreach (var (at, dir) in picture.Arrows)
            {
                Assert.That(at.x, Is.InRange(0f, 1f));
                Assert.That(at.y, Is.InRange(0f, 1f));
                Assert.AreEqual(1f, dir.magnitude, 1e-3f);
            }
            Assert.IsNull(BaseMapArt.For("no_such_map"));
        }

        /// <summary>A PNG's size from its header (IHDR), without decoding it.</summary>
        private static (int width, int height) PngSize(string path)
        {
            using var file = File.OpenRead(path);
            var header = new byte[24];
            if (file.Read(header, 0, 24) < 24) return (0, 0);
            int Read(int at) => (header[at] << 24) | (header[at + 1] << 16) | (header[at + 2] << 8) | header[at + 3];
            return (Read(16), Read(20));
        }
    }
}
