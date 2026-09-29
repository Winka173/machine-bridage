using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;
using NVector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The Base screen's map pictures (prompt 14 B.1-B.2): each map's player camp (team 0 of its
    /// Conquest variant) rendered from straight above out of the real scene (ground, roads,
    /// props, scenery, the HQ), turned so the camp's front (the HQ's heading, towards the enemy)
    /// points up, into Resources/UI/Bases/&lt;map&gt;.png, with &lt;map&gt;.json beside it: the frame
    /// (the world point at the picture's centre, the world direction that is up, metres across and
    /// down), the camp's edge, the drop zone and the enemy approach arrows (where the lane map's
    /// main routes cross into the camp). Made by MachineBrigade.Editor.BaseMapShots; the JSON keeps
    /// the SHA-1 of the map file it was made from, so BaseMapArtTests fail while a picture is stale.
    /// </summary>
    public static class BaseMapArt
    {
        public const string Folder = "UI/Bases/";

        /// <summary>Picture size in pixels: 16:10, wider than tall like the Base screen's middle.</summary>
        public const int Width = 1024;

        public const int Height = 640;

        /// <summary>Metres of ground kept round the camp (beyond the outermost slot's centre, the HQ and the drop zone).</summary>
        public const float Margin = 18f;

        /// <summary>More in front of the camp, where the enemy comes from: room for the arrows' shafts.</summary>
        public const float FrontMargin = 30f;

        /// <summary>The camp's edge: the convex hull of the HQ, the drop zone and every slot, pushed out this far (metres).</summary>
        public const float EdgePad = 6f;

        /// <summary>Deliveries land within about this far of the drop zone (EconomySystem fans them out 2-8 m).</summary>
        public const float DropRadius = 8f;

        /// <summary>A world point or direction on the ground: x east, z north (the sim's Vector2 X and Y).</summary>
        [Serializable]
        public struct XZ
        {
            public float x;
            public float z;

            public XZ(NVector2 v)
            {
                x = Round(v.X);
                z = Round(v.Y);
            }

            public NVector2 V => new(x, z);

            private static float Round(float v) => Mathf.Round(v * 1000f) / 1000f;
        }

        /// <summary>One way into the camp: the arrow's head on the camp's edge and its inward direction (world).</summary>
        [Serializable]
        public sealed class Arrow
        {
            public XZ at;
            public XZ dir;

            /// <summary>How many of the lane map's main routes use this way in (the busiest cell).</summary>
            public int routes;
        }

        /// <summary>The JSON beside each picture.</summary>
        [Serializable]
        public sealed class Data
        {
            public int version;
            public string map;

            /// <summary>The map file it was made from (under Resources) and its SHA-1 (line endings ignored).</summary>
            public string source;

            public string sha1;
            public int width;
            public int height;

            /// <summary>The world point at the picture's centre.</summary>
            public XZ centre;

            /// <summary>The world direction that is up in the picture (unit; the camp's front).</summary>
            public XZ up;

            public float metresWide;
            public float metresHigh;
            public XZ hq;

            /// <summary>The HQ's heading in degrees (0 = north, +z; 90 = east).</summary>
            public float heading;

            public XZ dropZone;
            public float dropRadius;

            /// <summary>The camp's edge, a convex polygon anticlockwise seen from above (world).</summary>
            public List<XZ> outline = new();

            /// <summary>"route" (LaneFlags.Route) or "road" (roads, where no route crosses the edge).</summary>
            public string arrowsFrom;

            public List<Arrow> arrows = new();

            /// <summary>
            /// Mean brightness (luma 0..1) of the picture inside the camp's edge: a snow camp is
            /// far brighter than a volcanic one, so a scrim under the slots can be set to match.
            /// </summary>
            public float brightness;

            public string camera;
        }

        private static readonly Dictionary<string, BaseMapPicture> Loaded = new();

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics() => Loaded.Clear();

        /// <summary>Forgets what was loaded (after the render tool rewrote the pictures).</summary>
        public static void Reload() => ResetStatics();

        /// <summary>The camp picture of a map (its id without the variant, e.g. "ashfield"); null when it has none.</summary>
        public static BaseMapPicture For(string mapId)
        {
            if (string.IsNullOrEmpty(mapId)) return null;
            if (Loaded.TryGetValue(mapId, out var cached) && cached != null && cached.Texture != null) return cached;
            var text = Resources.Load<TextAsset>(Folder + mapId);
            var texture = Resources.Load<Texture2D>(Folder + mapId);
            BaseMapPicture picture = null;
            if (text != null && texture != null)
            {
                var data = JsonUtility.FromJson<Data>(text.text);
                if (data != null && data.metresWide > 0f && data.metresHigh > 0f) picture = new BaseMapPicture(mapId, texture, data);
            }
            Loaded[mapId] = picture;
            return picture;
        }

        /// <summary>The picture's frame: centre, up and extent in metres.</summary>
        public readonly struct Frame
        {
            public Frame(NVector2 centre, NVector2 up, float metresWide, float metresHigh)
            {
                Centre = centre;
                Up = up;
                MetresWide = metresWide;
                MetresHigh = metresHigh;
            }

            public NVector2 Centre { get; }
            public NVector2 Up { get; }
            public float MetresWide { get; }
            public float MetresHigh { get; }
        }

        /// <summary>The camp's front (the HQ's heading) as a unit world direction.</summary>
        public static NVector2 Front(float heading) => new(MathF.Sin(heading), MathF.Cos(heading));

        /// <summary>The direction to the right of <paramref name="up"/> seen from above.</summary>
        public static NVector2 RightOf(NVector2 up) => new(up.Y, -up.X);

        /// <summary>
        /// Frames a camp: front up, the HQ (its footprint), the drop zone and every slot with
        /// <see cref="Margin"/> round them (<see cref="FrontMargin"/> in front), widened or
        /// heightened about their middle to the picture's 16:10.
        /// </summary>
        public static Frame FrameFor(BaseSiteDef site, NVector2 dropZone)
        {
            var up = Front(site.Heading);
            var right = RightOf(up);
            float minX = float.MaxValue, maxX = float.MinValue, minY = float.MaxValue, maxY = float.MinValue;
            void Add(NVector2 p, float half)
            {
                var d = p - site.Hq;
                var x = NVector2.Dot(d, right);
                var y = NVector2.Dot(d, up);
                minX = Mathf.Min(minX, x - half);
                maxX = Mathf.Max(maxX, x + half);
                minY = Mathf.Min(minY, y - half);
                maxY = Mathf.Max(maxY, y + half);
            }
            // The HQ is 14 m across; slots count from their centres (the margin is beyond them).
            Add(site.Hq, 7f);
            Add(dropZone, DropRadius);
            foreach (var slot in site.Slots) Add(slot.Position, 0f);
            minX -= Margin;
            maxX += Margin;
            minY -= Margin;
            maxY += FrontMargin;
            var aspect = (float)Width / Height;
            var wide = Mathf.Max(maxX - minX, (maxY - minY) * aspect);
            var high = wide / aspect;
            var middle = site.Hq + right * ((minX + maxX) * 0.5f) + up * ((minY + maxY) * 0.5f);
            return new Frame(middle, up, wide, high);
        }

        /// <summary>
        /// The camp's edge: the convex hull of the HQ, the drop zone and every slot, each side
        /// pushed <see cref="EdgePad"/> out (corners mitred), anticlockwise seen from above.
        /// </summary>
        public static List<NVector2> Outline(BaseSiteDef site, NVector2 dropZone)
        {
            var points = new List<NVector2> { site.Hq, dropZone };
            foreach (var slot in site.Slots) points.Add(slot.Position);
            var hull = Hull(points);
            var n = hull.Count;
            var outline = new List<NVector2>(n);
            if (n < 3) return hull;
            for (var i = 0; i < n; i++)
            {
                var before = Normal(hull[(i - 1 + n) % n], hull[i]);
                var after = Normal(hull[i], hull[(i + 1) % n]);
                outline.Add(hull[i] + (before + after) * (EdgePad / (1f + NVector2.Dot(before, after))));
            }
            return outline;
        }

        /// <summary>
        /// Signed distance from a convex anticlockwise polygon's edge (negative inside): the
        /// furthest any side's line is behind the point, so outside a corner it runs square.
        /// </summary>
        public static float EdgeDistance(IReadOnlyList<NVector2> outline, NVector2 p)
        {
            var d = float.MinValue;
            for (var i = 0; i < outline.Count; i++)
            {
                var a = outline[i];
                var b = outline[(i + 1) % outline.Count];
                d = Mathf.Max(d, NVector2.Dot(p - a, Normal(a, b)));
            }
            return d;
        }

        /// <summary>The outward normal of an anticlockwise polygon's side a-b.</summary>
        private static NVector2 Normal(NVector2 a, NVector2 b)
        {
            var e = b - a;
            var length = e.Length();
            return length > 1e-5f ? new NVector2(e.Y, -e.X) / length : NVector2.Zero;
        }

        /// <summary>Andrew's monotone chain: the convex hull, anticlockwise, no repeated points.</summary>
        private static List<NVector2> Hull(List<NVector2> points)
        {
            var sorted = new List<NVector2>(points);
            sorted.Sort((a, b) => a.X != b.X ? a.X.CompareTo(b.X) : a.Y.CompareTo(b.Y));
            var hull = new List<NVector2>();
            static float Cross(NVector2 o, NVector2 a, NVector2 b) => (a.X - o.X) * (b.Y - o.Y) - (a.Y - o.Y) * (b.X - o.X);
            for (var pass = 0; pass < 2; pass++)
            {
                var start = hull.Count;
                for (var k = 0; k < sorted.Count; k++)
                {
                    var p = pass == 0 ? sorted[k] : sorted[sorted.Count - 1 - k];
                    while (hull.Count >= start + 2 && Cross(hull[hull.Count - 2], hull[hull.Count - 1], p) <= 0f) hull.RemoveAt(hull.Count - 1);
                    hull.Add(p);
                }
                hull.RemoveAt(hull.Count - 1);
            }
            return hull;
        }
    }

    /// <summary>
    /// A loaded camp picture and its frame. Picture coordinates run 0..1 across (left to right)
    /// and 0..1 down (top to bottom), the camp's front up. Directions are unit vectors as seen on
    /// the picture (x right, y down): the pixels are square, so they are the same in pixels and on
    /// screen; to step along one in 0..1 coordinates, divide x by <see cref="Width"/> and y by
    /// <see cref="Height"/> after scaling it to pixels.
    /// </summary>
    public sealed class BaseMapPicture
    {
        private readonly List<(Vector2 at, Vector2 dir)> _arrows = new();
        private readonly List<int> _arrowRoutes = new();
        private readonly List<Vector2> _outline = new();

        internal BaseMapPicture(string mapId, Texture2D texture, BaseMapArt.Data data)
        {
            MapId = mapId;
            Texture = texture;
            Data = data;
            Centre = data.centre.V;
            Up = NVector2.Normalize(data.up.V);
            Right = BaseMapArt.RightOf(Up);
            foreach (var arrow in data.arrows)
            {
                _arrows.Add((ToPicture(arrow.at.V), ToPictureDirection(arrow.dir.V)));
                _arrowRoutes.Add(arrow.routes);
            }
            foreach (var p in data.outline) _outline.Add(ToPicture(p.V));
        }

        public string MapId { get; }
        public Texture2D Texture { get; }

        /// <summary>Everything the JSON holds (world units).</summary>
        public BaseMapArt.Data Data { get; }

        public int Width => Data.width;
        public int Height => Data.height;

        /// <summary>Width over height (1.6).</summary>
        public float Aspect => (float)Data.width / Data.height;

        public float MetresPerWidth => Data.metresWide;
        public float MetresPerHeight => Data.metresHigh;

        /// <summary>The world point at the picture's centre.</summary>
        public NVector2 Centre { get; }

        /// <summary>The world direction that is up in the picture (the camp's front).</summary>
        public NVector2 Up { get; }

        /// <summary>The world direction that is right in the picture.</summary>
        public NVector2 Right { get; }

        /// <summary>A map position (x, z) in the picture: 0..1 across and down, front up.</summary>
        public Vector2 ToPicture(NVector2 world)
        {
            var d = world - Centre;
            return new Vector2(0.5f + NVector2.Dot(d, Right) / MetresPerWidth, 0.5f - NVector2.Dot(d, Up) / MetresPerHeight);
        }

        /// <summary>A picture point (0..1 across and down) on the map.</summary>
        public NVector2 ToWorld(Vector2 picture) =>
            Centre + Right * ((picture.x - 0.5f) * MetresPerWidth) + Up * ((0.5f - picture.y) * MetresPerHeight);

        /// <summary>A world direction as a unit direction on the picture (x right, y down).</summary>
        public Vector2 ToPictureDirection(NVector2 world) => new Vector2(NVector2.Dot(world, Right), -NVector2.Dot(world, Up)).normalized;

        /// <summary>A map heading (radians, 0 = +z, as slot facings and the HQ's) as a direction on the picture.</summary>
        public Vector2 PictureDirection(float heading) => ToPictureDirection(BaseMapArt.Front(heading));

        /// <summary>Metres as a share of the picture's width.</summary>
        public float WidthShare(float metres) => metres / MetresPerWidth;

        /// <summary>Where the HQ stands in the picture.</summary>
        public Vector2 Hq => ToPicture(Data.hq.V);

        /// <summary>The drop zone's centre in the picture; deliveries land within <see cref="DropRadius"/> of it.</summary>
        public Vector2 DropZone => ToPicture(Data.dropZone.V);

        /// <summary>The drop zone's radius as a share of the picture's width.</summary>
        public float DropRadius => WidthShare(Data.dropRadius);

        /// <summary>Mean brightness (luma 0..1) of the picture inside the camp's edge.</summary>
        public float Brightness => Data.brightness;

        /// <summary>The camp's edge in the picture (a convex polygon).</summary>
        public IReadOnlyList<Vector2> Outline => _outline;

        /// <summary>
        /// The enemy's ways in: each arrow's head on the camp's edge (0..1 across and down) and
        /// its inward direction on the picture (a unit vector, y down). Draw the shaft behind the
        /// head, outside the camp. One per way in, typically 1-3.
        /// </summary>
        public IReadOnlyList<(Vector2 at, Vector2 dir)> Arrows => _arrows;

        /// <summary>How many main routes use each way in (same order as <see cref="Arrows"/>): a busier one can be drawn bolder.</summary>
        public IReadOnlyList<int> ArrowRoutes => _arrowRoutes;
    }
}
