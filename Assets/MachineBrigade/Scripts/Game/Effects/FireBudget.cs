using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// How many fire-and-smoke points a boss may carry at once (prompt 9 C.7): 8 (5 on the Low
    /// setting). Over the cap, the two nearest points are merged into one, again and again: the merged
    /// fire sits at their size-weighted middle, as big as the two together (the square root of the sum of
    /// their squares), on the bigger one's anchor. Pure, so the cap is tested without a scene.
    /// </summary>
    internal static class FireBudget
    {
        public const int Cap = 8;
        public const int LowCap = 5;

        public struct Point
        {
            public Vector3 At;
            public float Size;

            /// <summary>Which transform it rides on (an index into the caller's list).</summary>
            public int Anchor;

            public Point(Vector3 at, float size, int anchor)
            {
                At = at;
                Size = size;
                Anchor = anchor;
            }
        }

        /// <summary>Merges the nearest points until at most <paramref name="cap"/> remain (a new list; the input is left as it is).</summary>
        public static List<Point> Merge(IReadOnlyList<Point> points, int cap)
        {
            var list = new List<Point>(points);
            cap = Mathf.Max(1, cap);
            while (list.Count > cap)
            {
                var a = 0;
                var b = 1;
                var best = float.MaxValue;
                for (var i = 0; i < list.Count; i++)
                for (var j = i + 1; j < list.Count; j++)
                {
                    var d = (list[i].At - list[j].At).sqrMagnitude;
                    if (d >= best) continue;
                    best = d;
                    a = i;
                    b = j;
                }
                var p = list[a];
                var q = list[b];
                var weight = p.Size + q.Size;
                var merged = new Point(
                    weight > 0f ? (p.At * p.Size + q.At * q.Size) / weight : (p.At + q.At) * 0.5f,
                    Mathf.Sqrt(p.Size * p.Size + q.Size * q.Size),
                    p.Size >= q.Size ? p.Anchor : q.Anchor);
                list[a] = merged;
                list.RemoveAt(b);
            }
            return list;
        }
    }
}
