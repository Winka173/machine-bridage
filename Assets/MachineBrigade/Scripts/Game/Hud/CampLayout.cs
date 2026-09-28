using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Where the base screen draws a camp: the map from above, turned so the camp's front (the
    /// HQ's heading, towards the enemy) points up, scaled to fit the panel. Hardpoint frames are
    /// drawn at a size for their class (bigger than the hardpoint itself, so a finger can hit
    /// them); where two would overlap they are pushed apart just enough, so the diagram keeps the
    /// camp's shape without frames on top of each other.
    /// </summary>
    internal static class CampLayout
    {
        /// <summary>The fitted camp: metres to panel pixels, and each frame's centre.</summary>
        public readonly struct Fit
        {
            public Fit(float scale, Vector2 origin, float heading, Vector2 hq, Vector2[] centres)
            {
                Scale = scale;
                Origin = origin;
                Heading = heading;
                Hq = hq;
                Centres = centres;
            }

            /// <summary>Panel pixels per metre.</summary>
            public float Scale { get; }

            /// <summary>Where the HQ's map position lands in the panel (before frames were pushed apart).</summary>
            public Vector2 Origin { get; }

            public float Heading { get; }
            public Vector2 Hq { get; }

            /// <summary>Each frame's centre in the panel, in the order given.</summary>
            public Vector2[] Centres { get; }

            /// <summary>A map position (x, z) in the panel.</summary>
            public Vector2 ToPanel(Vector2 world)
            {
                var local = Local(world - Hq, Heading);
                return Origin + new Vector2(local.x, -local.y) * Scale;
            }

            /// <summary>A map direction (radians, 0 = +z) as a panel direction (y down).</summary>
            public Vector2 PanelDirection(float heading)
            {
                var d = Local(new Vector2(Mathf.Sin(heading), Mathf.Cos(heading)), Heading);
                return new Vector2(d.x, -d.y);
            }
        }

        /// <summary>A map offset in the camp's own frame: x to the right of its front, y towards the front.</summary>
        public static Vector2 Local(Vector2 offset, float heading)
        {
            var forward = new Vector2(Mathf.Sin(heading), Mathf.Cos(heading));
            var right = new Vector2(forward.y, -forward.x);
            return new Vector2(Vector2.Dot(offset, right), Vector2.Dot(offset, forward));
        }

        public static Vector2 ToUnity(System.Numerics.Vector2 v) => new(v.X, v.Y);

        /// <summary>
        /// Lays frames out in a panel: <paramref name="world"/> are their map positions (the HQ's
        /// among them), <paramref name="sizes"/> their frame sizes in pixels. The camp is centred
        /// and scaled to fit with <paramref name="pad"/> round it; then overlapping frames (closer
        /// than <paramref name="gap"/>) are pushed apart along the shorter way out, and kept inside.
        /// </summary>
        public static Fit Arrange(Vector2 hq, float heading, IReadOnlyList<Vector2> world, IReadOnlyList<float> sizes, Vector2 panel,
            float gap = 6f, float pad = 10f, float maxScale = 9f)
        {
            var n = world.Count;
            var local = new Vector2[n];
            Vector2 min = new(float.MaxValue, float.MaxValue), max = new(float.MinValue, float.MinValue);
            var largest = 0f;
            for (var i = 0; i < n; i++)
            {
                local[i] = Local(world[i] - hq, heading);
                min = Vector2.Min(min, local[i]);
                max = Vector2.Max(max, local[i]);
                largest = Mathf.Max(largest, sizes[i]);
            }
            if (n == 0) min = max = Vector2.zero;
            var span = max - min;
            var usable = panel - Vector2.one * (2f * pad + largest);
            var scale = Mathf.Min(maxScale, Mathf.Max(0.1f, usable.x) / Mathf.Max(1f, span.x), Mathf.Max(0.1f, usable.y) / Mathf.Max(1f, span.y));
            var middle = (min + max) * 0.5f;
            var origin = panel * 0.5f - new Vector2(middle.x, -middle.y) * scale;
            var centres = new Vector2[n];
            for (var i = 0; i < n; i++) centres[i] = origin + new Vector2(local[i].x, -local[i].y) * scale;

            for (var pass = 0; pass < 300; pass++)
            {
                var moved = false;
                for (var i = 0; i < n; i++)
                    for (var j = i + 1; j < n; j++)
                    {
                        var need = (sizes[i] + sizes[j]) * 0.5f + gap;
                        var d = centres[j] - centres[i];
                        var ox = need - Mathf.Abs(d.x);
                        var oy = need - Mathf.Abs(d.y);
                        if (ox <= 0.01f || oy <= 0.01f) continue;
                        moved = true;
                        if (ox < oy)
                        {
                            var s = d.x > 0f || (d.x == 0f && i < j) ? 1f : -1f;
                            centres[i].x -= s * ox * 0.5f;
                            centres[j].x += s * ox * 0.5f;
                        }
                        else
                        {
                            var s = d.y > 0f || (d.y == 0f && i < j) ? 1f : -1f;
                            centres[i].y -= s * oy * 0.5f;
                            centres[j].y += s * oy * 0.5f;
                        }
                    }
                for (var i = 0; i < n; i++)
                {
                    var half = sizes[i] * 0.5f + pad * 0.5f;
                    centres[i] = new Vector2(Mathf.Clamp(centres[i].x, half, Mathf.Max(half, panel.x - half)),
                        Mathf.Clamp(centres[i].y, half, Mathf.Max(half, panel.y - half)));
                }
                if (!moved) break;
            }
            // Where pushing got stuck against the edges, the smallest frame in the way moves to the
            // nearest free spot (a spiral of candidates round it).
            for (var round = 0; round < n; round++)
            {
                var worst = -1;
                for (var i = 0; i < n; i++)
                    if (Clashes(centres, sizes, panel, i, centres[i], FixGap, pad) && (worst < 0 || sizes[i] < sizes[worst])) worst = i;
                if (worst < 0) break;
                if (!NearestFree(centres, sizes, panel, worst, pad, out var spot)) break;
                centres[worst] = spot;
            }
            return new Fit(scale, origin, heading, hq, centres);
        }

        /// <summary>The space kept between frames by the final fix-up (less than the relaxation's gap).</summary>
        private const float FixGap = 2f;

        private static bool Clashes(Vector2[] centres, IReadOnlyList<float> sizes, Vector2 panel, int i, Vector2 at, float gap, float pad)
        {
            var half = sizes[i] * 0.5f;
            var edge = pad * 0.5f - 0.01f;
            if (at.x - half < edge || at.y - half < edge || at.x + half > panel.x - edge || at.y + half > panel.y - edge) return true;
            for (var j = 0; j < centres.Length; j++)
            {
                if (j == i) continue;
                var need = (sizes[i] + sizes[j]) * 0.5f + gap - 0.01f;
                if (Mathf.Abs(centres[j].x - at.x) < need && Mathf.Abs(centres[j].y - at.y) < need) return true;
            }
            return false;
        }

        private static bool NearestFree(Vector2[] centres, IReadOnlyList<float> sizes, Vector2 panel, int i, float pad, out Vector2 spot)
        {
            const float step = 4f;
            var from = centres[i];
            var rings = Mathf.CeilToInt(Mathf.Max(panel.x, panel.y) / step);
            for (var r = 1; r <= rings; r++)
            {
                var found = false;
                var best = Vector2.zero;
                var bestD = float.MaxValue;
                for (var k = -r; k <= r; k++)
                    foreach (var offset in new[] { new Vector2(k, -r), new Vector2(k, r), new Vector2(-r, k), new Vector2(r, k) })
                    {
                        var at = from + offset * step;
                        if (Clashes(centres, sizes, panel, i, at, FixGap, pad)) continue;
                        var d = (at - from).sqrMagnitude;
                        if (d >= bestD) continue;
                        bestD = d;
                        best = at;
                        found = true;
                    }
                if (!found) continue;
                spot = best;
                return true;
            }
            spot = from;
            return false;
        }

        /// <summary>Whether any two frames overlap (tests; closer than <paramref name="gap"/> counts).</summary>
        public static bool Overlaps(IReadOnlyList<Vector2> centres, IReadOnlyList<float> sizes, float gap = 0f)
        {
            for (var i = 0; i < centres.Count; i++)
                for (var j = i + 1; j < centres.Count; j++)
                {
                    var need = (sizes[i] + sizes[j]) * 0.5f + gap;
                    var d = centres[j] - centres[i];
                    if (Mathf.Abs(d.x) < need - 0.5f && Mathf.Abs(d.y) < need - 0.5f) return true;
                }
            return false;
        }

    }
}
