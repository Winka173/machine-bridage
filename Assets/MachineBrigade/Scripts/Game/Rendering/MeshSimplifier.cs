using System;
using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Error-bounded quadric edge-collapse simplifier (Garland and Heckbert 1997, with the vertex
    /// kinds and pass structure of meshoptimizer's simplifier) for the vehicles' far detail level.
    /// It works on welded positions: every triangle carries a group (its surface), and the lines
    /// between groups and the open edges of the mesh only slide along themselves, so colours stay
    /// where they were and outlines keep their shape. Collapses are half-edge (a vertex moves onto
    /// a neighbour), so every vertex left is an input vertex and nothing is placed off the surface.
    /// </summary>
    public static class MeshSimplifier
    {
        private enum Kind : byte
        {
            /// <summary>Inside a surface: may move onto any neighbour.</summary>
            Manifold,

            /// <summary>On an open edge: moves only along it.</summary>
            Border,

            /// <summary>On the line between two groups: moves only along it.</summary>
            Seam,

            /// <summary>Corners, junctions and non-manifold vertices stay where they are.</summary>
            Locked,
        }

        /// <summary>Weight of the planes that hold open edges and group lines in place, against the faces' own.</summary>
        private const double BorderWeight = 10.0;

        private const double SeamWeight = 2.0;

        /// <summary>Set to a builder to have each pass described (tests).</summary>
        internal static System.Text.StringBuilder Trace;
        private const int MaxPasses = 64;

        private struct Quadric
        {
            public double A2, B2, C2, AB, AC, BC, AD, BD, CD, D2, W;

            public void Add(double a, double b, double c, double d, double w)
            {
                A2 += a * a * w;
                B2 += b * b * w;
                C2 += c * c * w;
                AB += a * b * w;
                AC += a * c * w;
                BC += b * c * w;
                AD += a * d * w;
                BD += b * d * w;
                CD += c * d * w;
                D2 += d * d * w;
                W += w;
            }

            public void Add(in Quadric q)
            {
                A2 += q.A2;
                B2 += q.B2;
                C2 += q.C2;
                AB += q.AB;
                AC += q.AC;
                BC += q.BC;
                AD += q.AD;
                BD += q.BD;
                CD += q.CD;
                D2 += q.D2;
                W += q.W;
            }

            /// <summary>Mean squared distance of a point from the planes gathered here.</summary>
            public double Error(double x, double y, double z)
            {
                if (W <= 0.0) return 0.0;
                var r = A2 * x * x + B2 * y * y + C2 * z * z + 2.0 * (AB * x * y + AC * x * z + BC * y * z) +
                        2.0 * (AD * x + BD * y + CD * z) + D2;
                return Math.Abs(r) / W;
            }
        }

        /// <summary>
        /// Simplifies an indexed triangle mesh. <paramref name="maxError"/> is how far (in the
        /// positions' units) the surface may move; <paramref name="minComponent"/> drops whole
        /// connected pieces smaller than that across (bolts and rivets nobody can see). Returns the
        /// triangles kept, as indices into <paramref name="positions"/>, and their groups.
        /// </summary>
        public static (int[] triangles, int[] groups) Simplify(IReadOnlyList<Vector3> positions, int[] triangles, int[] groups,
            float maxError, float minComponent = 0f)
        {
            if (triangles.Length % 3 != 0) throw new ArgumentException("Triangles must come in threes.", nameof(triangles));
            if (groups.Length != triangles.Length / 3) throw new ArgumentException("One group per triangle.", nameof(groups));
            var n = positions.Count;
            var idx = (int[])triangles.Clone();
            var grp = (int[])groups.Clone();
            var count = idx.Length / 3;
            if (count == 0 || n == 0) return (idx, grp);

            // Positions in doubles, relative to the mesh's lowest corner.
            var lo = positions[0];
            var hi = positions[0];
            for (var i = 1; i < n; i++)
            {
                lo = Vector3.Min(lo, positions[i]);
                hi = Vector3.Max(hi, positions[i]);
            }
            var x = new double[n];
            var y = new double[n];
            var z = new double[n];
            for (var i = 0; i < n; i++)
            {
                x[i] = positions[i].x - lo.x;
                y[i] = positions[i].y - lo.y;
                z[i] = positions[i].z - lo.z;
            }

            if (minComponent > 0f) count = DropSmallPieces(x, y, z, idx, grp, count, minComponent);
            count = RemoveDegenerate(idx, grp, count);

            var quadrics = new Quadric[n];
            var edges = new EdgeMap(count * 2);
            var adjacency = new Adjacency(n);
            adjacency.Build(idx, count);
            edges.Build(idx, grp, adjacency, n);
            for (var t = 0; t < count; t++)
            {
                int a = idx[3 * t], b = idx[3 * t + 1], c = idx[3 * t + 2];
                if (!Normal(x, y, z, a, b, c, out var nx, out var ny, out var nz, out var length)) continue;
                var d = -(nx * x[a] + ny * y[a] + nz * z[a]);
                var area = length * 0.5;
                quadrics[a].Add(nx, ny, nz, d, area);
                quadrics[b].Add(nx, ny, nz, d, area);
                quadrics[c].Add(nx, ny, nz, d, area);
                for (var k = 0; k < 3; k++)
                {
                    var p = idx[3 * t + k];
                    var q = idx[3 * t + (k + 1) % 3];
                    var e = edges.Find(p, q);
                    if (e < 0) continue;
                    var border = edges.Count[e] == 1;
                    if (!border && !edges.Seam[e]) continue;
                    AddEdgePlane(quadrics, x, y, z, p, q, nx, ny, nz, border ? BorderWeight : SeamWeight);
                }
            }

            var limit = (double)maxError * maxError;
            var kinds = new Kind[n];
            var locked = new bool[n];
            var remap = new int[n];
            var ring = new List<int>();
            var from = new int[count * 3];
            var to = new int[count * 3];
            var costs = new double[count * 3];
            var order = new int[count * 3];
            for (var pass = 0; pass < MaxPasses && count > 0; pass++)
            {
                if (pass > 0)
                {
                    adjacency.Build(idx, count);
                    edges.Build(idx, grp, adjacency, n);
                }
                Classify(edges, kinds, n);

                var candidates = 0;
                for (var e = 0; e < edges.Used; e++)
                {
                    int a = edges.A[e], b = edges.B[e];
                    var ab = CanCollapse(kinds[a], edges, e);
                    var ba = CanCollapse(kinds[b], edges, e);
                    if (!ab && !ba) continue;
                    var cab = ab ? quadrics[a].Error(x[b], y[b], z[b]) : double.MaxValue;
                    var cba = ba ? quadrics[b].Error(x[a], y[a], z[a]) : double.MaxValue;
                    var cost = Math.Min(cab, cba);
                    if (cost > limit) continue;
                    from[candidates] = cab <= cba ? a : b;
                    to[candidates] = cab <= cba ? b : a;
                    costs[candidates] = cost;
                    order[candidates] = candidates;
                    candidates++;
                }
                if (candidates == 0) break;
                Array.Sort(costs, order, 0, candidates);

                Array.Clear(locked, 0, n);
                for (var v = 0; v < n; v++) remap[v] = v;
                var collapsed = 0;
                int byLock = 0, byLink = 0, byFlip = 0;
                for (var i = 0; i < candidates; i++)
                {
                    var c = order[i];
                    int u = from[c], v = to[c];
                    // Each vertex moves or is moved onto once a pass; corners already moved are
                    // followed through the remap, so the flip test sees the mesh as it is now.
                    if (locked[u] || locked[v]) { byLock++; continue; }
                    if (!LinkHolds(idx, adjacency, remap, u, v, ring)) { byLink++; continue; }
                    if (Flips(x, y, z, idx, adjacency, remap, u, v)) { byFlip++; continue; }
                    remap[u] = v;
                    quadrics[v].Add(quadrics[u]);
                    locked[u] = locked[v] = true;
                    collapsed++;
                }
                for (var i = 0; i < count * 3; i++) idx[i] = remap[idx[i]];
                count = RemoveDegenerate(idx, grp, count);
                if (Trace != null)
                {
                    var hist = new int[4];
                    foreach (var k in kinds) hist[(int)k]++;
                    Trace.AppendLine($"pass {pass}: candidates={candidates} collapsed={collapsed} lock={byLock} link={byLink} flip={byFlip} tris={count} kinds={string.Join(",", hist)}");
                }
                if (collapsed == 0) break;
            }

            var outIdx = new int[count * 3];
            var outGrp = new int[count];
            Array.Copy(idx, outIdx, count * 3);
            Array.Copy(grp, outGrp, count);
            return (outIdx, outGrp);
        }

        private static bool CanCollapse(Kind kind, EdgeMap edges, int e) => kind switch
        {
            Kind.Manifold => true,
            Kind.Border => edges.Count[e] == 1,
            Kind.Seam => edges.Count[e] == 2 && edges.Seam[e],
            _ => false,
        };

        private static void Classify(EdgeMap edges, Kind[] kinds, int n)
        {
            var border = new byte[n];
            var seam = new byte[n];
            var complex = new bool[n];
            for (var e = 0; e < edges.Used; e++)
            {
                int a = edges.A[e], b = edges.B[e];
                if (edges.Count[e] > 2)
                {
                    complex[a] = complex[b] = true;
                    continue;
                }
                if (edges.Count[e] == 1)
                {
                    border[a] = (byte)Math.Min(255, border[a] + 1);
                    border[b] = (byte)Math.Min(255, border[b] + 1);
                }
                else if (edges.Seam[e])
                {
                    seam[a] = (byte)Math.Min(255, seam[a] + 1);
                    seam[b] = (byte)Math.Min(255, seam[b] + 1);
                }
            }
            for (var v = 0; v < n; v++)
                kinds[v] = complex[v] || (border[v] > 0 && seam[v] > 0) ? Kind.Locked
                    : border[v] == 2 ? Kind.Border
                    : border[v] > 0 ? Kind.Locked
                    : seam[v] == 2 ? Kind.Seam
                    : seam[v] > 0 ? Kind.Locked
                    : Kind.Manifold;
        }

        /// <summary>
        /// The link condition: u and v may share no neighbour but the far corners of the
        /// triangles on their edge, or the collapse would pinch the surface into an edge that
        /// three triangles share (which then locks everything round it).
        /// </summary>
        private static bool LinkHolds(int[] idx, Adjacency adjacency, int[] remap, int u, int v, List<int> ring)
        {
            ring.Clear();
            var opposite0 = -1;
            var opposite1 = -1;
            for (var k = adjacency.Start[u]; k < adjacency.Start[u + 1]; k++)
            {
                var t = adjacency.Triangles[k];
                int a = remap[idx[3 * t]], b = remap[idx[3 * t + 1]], c = remap[idx[3 * t + 2]];
                if (a == b || b == c || a == c) continue;
                var onEdge = a == v || b == v || c == v;
                foreach (var w in new[] { a, b, c })
                {
                    if (w == u || w == v) continue;
                    if (onEdge)
                    {
                        if (opposite0 < 0) opposite0 = w;
                        else if (w != opposite0) opposite1 = w;
                    }
                    else if (!ring.Contains(w)) ring.Add(w);
                }
            }
            for (var k = adjacency.Start[v]; k < adjacency.Start[v + 1]; k++)
            {
                var t = adjacency.Triangles[k];
                int a = remap[idx[3 * t]], b = remap[idx[3 * t + 1]], c = remap[idx[3 * t + 2]];
                if (a == b || b == c || a == c) continue;
                foreach (var w in new[] { a, b, c })
                    if (w != u && w != v && w != opposite0 && w != opposite1 && ring.Contains(w)) return false;
            }
            return true;
        }

        /// <summary>Whether moving u onto v turns any triangle round u over (or folds it flat).</summary>
        private static bool Flips(double[] x, double[] y, double[] z, int[] idx, Adjacency adjacency, int[] remap, int u, int v)
        {
            for (var k = adjacency.Start[u]; k < adjacency.Start[u + 1]; k++)
            {
                var t = adjacency.Triangles[k];
                int a = remap[idx[3 * t]], b = remap[idx[3 * t + 1]], c = remap[idx[3 * t + 2]];
                if (a == v || b == v || c == v || a == b || b == c || a == c) continue;
                if (!Normal(x, y, z, a, b, c, out var ox, out var oy, out var oz, out _)) continue;
                if (a == u) a = v;
                else if (b == u) b = v;
                else c = v;
                if (!Normal(x, y, z, a, b, c, out var nx, out var ny, out var nz, out _)) return true;
                if (ox * nx + oy * ny + oz * nz < 0.2) return true;
            }
            return false;
        }

        private static bool Normal(double[] x, double[] y, double[] z, int a, int b, int c,
            out double nx, out double ny, out double nz, out double length)
        {
            double ux = x[b] - x[a], uy = y[b] - y[a], uz = z[b] - z[a];
            double vx = x[c] - x[a], vy = y[c] - y[a], vz = z[c] - z[a];
            nx = uy * vz - uz * vy;
            ny = uz * vx - ux * vz;
            nz = ux * vy - uy * vx;
            length = Math.Sqrt(nx * nx + ny * ny + nz * nz);
            if (length < 1e-14)
            {
                nx = ny = nz = 0.0;
                return false;
            }
            nx /= length;
            ny /= length;
            nz /= length;
            return true;
        }

        /// <summary>A plane through the edge p-q standing up from its face, so the edge resists moving sideways.</summary>
        private static void AddEdgePlane(Quadric[] quadrics, double[] x, double[] y, double[] z, int p, int q,
            double nx, double ny, double nz, double weight)
        {
            double ex = x[q] - x[p], ey = y[q] - y[p], ez = z[q] - z[p];
            var length2 = ex * ex + ey * ey + ez * ez;
            if (length2 < 1e-20) return;
            double px = ey * nz - ez * ny, py = ez * nx - ex * nz, pz = ex * ny - ey * nx;
            var l = Math.Sqrt(px * px + py * py + pz * pz);
            if (l < 1e-14) return;
            px /= l;
            py /= l;
            pz /= l;
            var d = -(px * x[p] + py * y[p] + pz * z[p]);
            quadrics[p].Add(px, py, pz, d, length2 * weight);
            quadrics[q].Add(px, py, pz, d, length2 * weight);
        }

        private static int RemoveDegenerate(int[] idx, int[] grp, int count)
        {
            var kept = 0;
            for (var t = 0; t < count; t++)
            {
                int a = idx[3 * t], b = idx[3 * t + 1], c = idx[3 * t + 2];
                if (a == b || b == c || a == c) continue;
                idx[3 * kept] = a;
                idx[3 * kept + 1] = b;
                idx[3 * kept + 2] = c;
                grp[kept] = grp[t];
                kept++;
            }
            return kept;
        }

        /// <summary>Removes connected pieces whose bounding box is smaller than <paramref name="size"/> across.</summary>
        private static int DropSmallPieces(double[] x, double[] y, double[] z, int[] idx, int[] grp, int count, float size)
        {
            var n = x.Length;
            var parent = new int[n];
            for (var i = 0; i < n; i++) parent[i] = i;
            int Root(int i)
            {
                while (parent[i] != i)
                {
                    parent[i] = parent[parent[i]];
                    i = parent[i];
                }
                return i;
            }
            for (var t = 0; t < count; t++)
            {
                var a = Root(idx[3 * t]);
                var b = Root(idx[3 * t + 1]);
                var c = Root(idx[3 * t + 2]);
                parent[b] = a;
                parent[Root(c)] = a;
            }
            var lo = new Dictionary<int, (double x0, double y0, double z0, double x1, double y1, double z1)>();
            for (var t = 0; t < count; t++)
                for (var k = 0; k < 3; k++)
                {
                    var v = idx[3 * t + k];
                    var r = Root(v);
                    if (!lo.TryGetValue(r, out var box)) box = (x[v], y[v], z[v], x[v], y[v], z[v]);
                    lo[r] = (Math.Min(box.x0, x[v]), Math.Min(box.y0, y[v]), Math.Min(box.z0, z[v]),
                        Math.Max(box.x1, x[v]), Math.Max(box.y1, y[v]), Math.Max(box.z1, z[v]));
                }
            var limit = (double)size * size;
            var kept = 0;
            for (var t = 0; t < count; t++)
            {
                var box = lo[Root(idx[3 * t])];
                double dx = box.x1 - box.x0, dy = box.y1 - box.y0, dz = box.z1 - box.z0;
                if (dx * dx + dy * dy + dz * dz < limit) continue;
                idx[3 * kept] = idx[3 * t];
                idx[3 * kept + 1] = idx[3 * t + 1];
                idx[3 * kept + 2] = idx[3 * t + 2];
                grp[kept] = grp[t];
                kept++;
            }
            return kept;
        }

        /// <summary>
        /// Undirected edges of the current triangles, found through the vertices' triangle lists
        /// (no hashing): how many triangles share each, and whether they differ in group. The
        /// edges of vertex a to higher-numbered vertices are Start[a] to Start[a + 1].
        /// </summary>
        private sealed class EdgeMap
        {
            public int[] A, B, Count, Group;
            public bool[] Seam;
            public int[] Start = Array.Empty<int>();
            public int Used;

            public EdgeMap(int capacity)
            {
                A = new int[capacity];
                B = new int[capacity];
                Count = new int[capacity];
                Group = new int[capacity];
                Seam = new bool[capacity];
            }

            public int Find(int p, int q)
            {
                int a = Math.Min(p, q), b = Math.Max(p, q);
                for (var e = Start[a]; e < Start[a + 1]; e++)
                    if (B[e] == b) return e;
                return -1;
            }

            public void Build(int[] idx, int[] grp, Adjacency adjacency, int n)
            {
                if (Start.Length != n + 1) Start = new int[n + 1];
                Used = 0;
                for (var a = 0; a < n; a++)
                {
                    Start[a] = Used;
                    for (var k = adjacency.Start[a]; k < adjacency.Start[a + 1]; k++)
                    {
                        var t = adjacency.Triangles[k];
                        for (var j = 0; j < 3; j++)
                        {
                            var b = idx[3 * t + j];
                            if (b <= a) continue;
                            var e = Start[a];
                            while (e < Used && B[e] != b) e++;
                            if (e < Used)
                            {
                                Count[e]++;
                                if (Group[e] != grp[t]) Seam[e] = true;
                                continue;
                            }
                            if (Used == A.Length) Grow();
                            A[Used] = a;
                            B[Used] = b;
                            Count[Used] = 1;
                            Group[Used] = grp[t];
                            Seam[Used] = false;
                            Used++;
                        }
                    }
                }
                Start[n] = Used;
            }

            private void Grow()
            {
                var size = A.Length * 2 + 16;
                Array.Resize(ref A, size);
                Array.Resize(ref B, size);
                Array.Resize(ref Count, size);
                Array.Resize(ref Group, size);
                Array.Resize(ref Seam, size);
            }
        }

        /// <summary>The triangles round each vertex, packed (Start[v] to Start[v + 1] in Triangles).</summary>
        private sealed class Adjacency
        {
            public readonly int[] Start;
            public int[] Triangles = Array.Empty<int>();

            public Adjacency(int vertices) => Start = new int[vertices + 1];

            public void Build(int[] idx, int count)
            {
                Array.Clear(Start, 0, Start.Length);
                for (var i = 0; i < count * 3; i++) Start[idx[i] + 1]++;
                for (var v = 1; v < Start.Length; v++) Start[v] += Start[v - 1];
                if (Triangles.Length < count * 3) Triangles = new int[count * 3];
                var fill = new int[Start.Length];
                Array.Copy(Start, fill, Start.Length);
                for (var t = 0; t < count; t++)
                    for (var k = 0; k < 3; k++)
                        Triangles[fill[idx[3 * t + k]]++] = t;
            }
        }
    }
}
