using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.Rendering;
using Random = System.Random;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 33 L2, the view side: the outer ring follows each stretch's edgeType from the map's "edges" data
    /// (Tools/maps/edges.py; DECISIONS "Prompt 33 L2 view / L7").
    /// <list type="bullet">
    /// <item>SEA: water from the edge to the horizon (a sea mesh in 2 m cells over the decorated square, 20 m cells out
    /// to three times its size), whitecaps, far ship silhouettes and hazy islands, buoys on the sea lanes' way out; no
    /// land, house, wood, field or hill there (every scatter asks <see cref="InSea"/>). The coast leaves the map at
    /// each SEA junction and runs out with a gentle wobble past the corner piece; at a rectangle corner with one SEA side
    /// the sea takes the corner and the coast runs on along that side's line. The shore matches the land: surf lines on a
    /// BEACH, sea stacks and scree on a CLIFF shore, quay walls, cranes and containers on a QUAY.</item>
    /// <item>RIVER: each RIVER stretch's river runs on out as a channel (its width, meandering past the corner pieces),
    /// the hills open round it. CLIFF: the ground beyond rises as a faceted rock wall (8-13 m) with scree. URBAN: the
    /// theme's city (its skyline) and, on a map without one, the urban set. The modifiers (HARBOR, INDUSTRIAL, URBAN)
    /// add their ring set.</item>
    /// <item>The prebuilt corner pieces where two types meet and at the rectangle's corners (mirrored when the data's
    /// order is the other way round), never random ground; the scatter and the relief keep off them.</item>
    /// <item>Continuity: roads run on out as painted strips with a cut through the hills, rails as track to their tunnel
    /// portals (the track is laid along the whole RailSpline, the play stretch too), rivers and the coast as above, the
    /// sea lanes as buoy lines. The air corridors have nothing to draw.</item>
    /// </list>
    /// Decoration only: instanced matrices and a few collider-free GameObjects (the mirrored corner pieces); nothing here
    /// reaches the simulation, its routes or its vision. A map without edges data keeps the theme's old picture.
    /// </summary>
    public sealed partial class Surroundings
    {
        private MapEdgesDef _edges;
        private DressingEdges _edgeDress;

        private bool HasEdges => _edges != null && _edges.Segments.Count > 0;

        /// <summary>The coast and the rivers run straight this far past the edge (the corner pieces' length), then wobble.</summary>
        private const float CoastStraight = 36f;

        private const float SeaCell = 4f;

        private readonly struct EdgeRiver
        {
            public EdgeRiver(Vector2 at, Vector2 dir, float half, float phase)
            {
                At = at;
                Dir = dir;
                Half = half;
                Phase = phase;
            }

            public Vector2 At { get; }
            public Vector2 Dir { get; }
            public float Half { get; }
            public float Phase { get; }
        }

        /// <summary>A line that runs on out of the map (a road, a rail): a segment and its half width.</summary>
        private readonly struct EdgeLine
        {
            public EdgeLine(Vector2 a, Vector2 b, float half, bool rail)
            {
                A = a;
                B = b;
                Half = half;
                Rail = rail;
            }

            public Vector2 A { get; }
            public Vector2 B { get; }
            public float Half { get; }
            public bool Rail { get; }
        }

        private readonly List<EdgeRiver> _edgeRivers = new();
        private readonly List<EdgeLine> _edgeLines = new();

        /// <summary>The corner pieces' ground (centre, radius): no scatter, no relief or range there.</summary>
        private readonly List<(Vector2 centre, float radius)> _cornerZones = new();

        /// <summary>Distance to the sea (metres, in <see cref="SeaCell"/> cells over the decorated square); null without sea.</summary>
        private float[] _seaField;
        private int _seaCells;

        // ------------------------------------------------------------------------------------------ set-up

        /// <summary>Reads the edges data before anything is scattered (the relief, the range and the scatter all ask it).</summary>
        private void PrepareEdges(SimWorld world)
        {
            _edges = world.Map.Edges;
            _edgeDress = MapDressing.Data.edges;
            if (!HasEdges) return;
            var reach = Extent * 3f;
            foreach (var link in _edges.Links)
            {
                var at = new Vector2(link.Position.X, link.Position.Y);
                var dir = new Vector2(link.Outward.X, link.Outward.Y);
                if (dir.sqrMagnitude < 1e-4f) continue;
                dir.Normalize();
                if (link.Kind == "river")
                    _edgeRivers.Add(new EdgeRiver(at, dir, Mathf.Max(4f, link.Width * 0.5f), (at.x * 0.37f + at.y * 0.21f) % 6.28f));
                else if (link.Kind == "road")
                    _edgeLines.Add(new EdgeLine(at - dir * 2f, at + dir * reach, Mathf.Clamp(link.Width * 0.5f, 1.5f, 12f), false));
            }
            foreach (var rail in world.Map.Rails)
                for (var i = 0; i + 1 < rail.Points.Count; i++)
                    _edgeLines.Add(new EdgeLine(new Vector2(rail.Points[i].X, rail.Points[i].Y),
                        new Vector2(rail.Points[i + 1].X, rail.Points[i + 1].Y), 2.4f, true));
            foreach (var corner in _edges.Corners)
            {
                var piece = _edgeDress?.Corner(corner.Piece);
                if (piece == null) continue;
                if (!CornerFrame(corner, piece, out _, out var ez, out var ex)) continue;
                var at = new Vector2(corner.Position.X, corner.Position.Y);
                var centre = corner.Outer ? at + (ex + ez) * piece.radius * 0.4f : at + ez * piece.radius * 0.5f;
                _cornerZones.Add((centre, piece.radius));
            }
            if (_edges.HasSea) BuildSeaField();
        }

        // ------------------------------------------------------------------------------------------ edge types

        /// <summary>The stretch beyond one side of the rectangle at a point outside it (E/W or N/S), and its along value.</summary>
        private EdgeSegmentDef SideSegment(Vector2 p, bool eastWest, float wobble, out float along)
        {
            string side;
            float lo, hi;
            if (eastWest)
            {
                side = p.x > _centre.x ? "E" : "W";
                along = p.y;
                lo = _centre.y - _halfZ;
                hi = _centre.y + _halfZ;
            }
            else
            {
                side = p.y > _centre.y ? "N" : "S";
                along = p.x;
                lo = _centre.x - _halfX;
                hi = _centre.x + _halfX;
            }
            along = Mathf.Clamp(along + wobble, lo, hi);
            return _edges.At(side, along);
        }

        /// <summary>The coast's lateral wobble at a distance out (0 within <see cref="CoastStraight"/>, so the corner pieces fit).</summary>
        private float CoastWobble(float beyond, bool eastWest, bool high) =>
            (Mathf.PerlinNoise(beyond * 0.03f + (eastWest ? 11.3f : 3.7f), high ? 5.1f : 1.9f) - 0.5f) * 34f
            * Edge(CoastStraight, CoastStraight + 45f, beyond);

        /// <summary>
        /// Whether a point outside the rectangle is on the sea beyond a SEA stretch (the map's own water inside is the
        /// map's). A point beyond a corner is sea when either side's stretch there is.
        /// </summary>
        private bool EdgeSeaAt(Vector2 p)
        {
            if (!HasEdges || !_edges.HasSea) return false;
            var dx = Mathf.Abs(p.x - _centre.x) - _halfX;
            var dz = Mathf.Abs(p.y - _centre.y) - _halfZ;
            if (dx > 0f && SideSegment(p, true, CoastWobble(dx, true, p.x > _centre.x), out _)?.Type == EdgeType.Sea) return true;
            if (dz > 0f && SideSegment(p, false, CoastWobble(dz, false, p.y > _centre.y), out _)?.Type == EdgeType.Sea) return true;
            return false;
        }

        /// <summary>Distance-to-sea field (chamfer, 4 m cells) over the decorated square, for margins and the shore paint.</summary>
        private void BuildSeaField()
        {
            _seaCells = Mathf.CeilToInt(Extent * 2f / SeaCell);
            var n = _seaCells;
            _seaField = new float[n * n];
            var queue = new Queue<int>();
            for (var z = 0; z < n; z++)
            for (var x = 0; x < n; x++)
            {
                var i = z * n + x;
                if (EdgeSeaAt(SeaCellCentre(x, z)))
                {
                    _seaField[i] = 0f;
                    queue.Enqueue(i);
                }
                else
                {
                    _seaField[i] = float.MaxValue;
                }
            }
            // Two-pass chamfer distance (4 m straight, 5.66 m diagonal).
            const float straight = SeaCell, diagonal = SeaCell * 1.41421f;
            for (var z = 0; z < n; z++)
            for (var x = 0; x < n; x++)
            {
                var i = z * n + x;
                var d = _seaField[i];
                if (x > 0) d = Mathf.Min(d, _seaField[i - 1] + straight);
                if (z > 0) d = Mathf.Min(d, _seaField[i - n] + straight);
                if (x > 0 && z > 0) d = Mathf.Min(d, _seaField[i - n - 1] + diagonal);
                if (x + 1 < n && z > 0) d = Mathf.Min(d, _seaField[i - n + 1] + diagonal);
                _seaField[i] = d;
            }
            for (var z = n - 1; z >= 0; z--)
            for (var x = n - 1; x >= 0; x--)
            {
                var i = z * n + x;
                var d = _seaField[i];
                if (x + 1 < n) d = Mathf.Min(d, _seaField[i + 1] + straight);
                if (z + 1 < n) d = Mathf.Min(d, _seaField[i + n] + straight);
                if (x + 1 < n && z + 1 < n) d = Mathf.Min(d, _seaField[i + n + 1] + diagonal);
                if (x > 0 && z + 1 < n) d = Mathf.Min(d, _seaField[i + n - 1] + diagonal);
                _seaField[i] = d;
            }
            SeaArea = queue.Count * SeaCell * SeaCell;
        }

        /// <summary>Square metres of sea in the decorated square (for the whitecaps' count).</summary>
        private float SeaArea { get; set; }

        private Vector2 SeaCellCentre(int x, int z) =>
            new(_centre.x - Extent + (x + 0.5f) * SeaCell, _centre.y - Extent + (z + 0.5f) * SeaCell);

        /// <summary>Metres to the edge sea (0 on it; 999 without any); outside the field it only says on or off.</summary>
        private float SeaDistance(Vector2 p)
        {
            if (_seaField == null) return 999f;
            var x = Mathf.FloorToInt((p.x - _centre.x + Extent) / SeaCell);
            var z = Mathf.FloorToInt((p.y - _centre.y + Extent) / SeaCell);
            if (x < 0 || z < 0 || x >= _seaCells || z >= _seaCells) return EdgeSeaAt(p) ? 0f : 999f;
            if (EdgeSeaAt(p)) return 0f;
            return Mathf.Max(0.5f, _seaField[z * _seaCells + x] - SeaCell * 0.5f);
        }

        /// <summary>Edge sea within <paramref name="margin"/> m (the scatter's question).</summary>
        private bool EdgeSea(Vector2 p, float margin) => EdgeSeaAt(p) || (margin > 0f && SeaDistance(p) < margin);

        /// <summary>Metres from the nearest river running out of the map (negative in it; 999 without one).</summary>
        private float EdgeRiverDistance(Vector2 p)
        {
            var best = 999f;
            foreach (var r in _edgeRivers)
            {
                var d = p - r.At;
                var t = Vector2.Dot(d, r.Dir);
                if (t < -1f) continue;
                var across = r.Dir.x * d.y - r.Dir.y * d.x;
                best = Mathf.Min(best, Mathf.Abs(across - Meander(r, t)) - r.Half);
            }
            return best;
        }

        private static float Meander(EdgeRiver r, float t) =>
            Mathf.Sin(t * 0.022f + r.Phase) * Mathf.Min(14f, r.Half * 0.6f) * Edge(CoastStraight, CoastStraight + 40f, t);

        /// <summary>Metres off the nearest road or rail running on out (beyond its half width), and whether it is a rail.</summary>
        private float EdgeLineDistance(Vector2 p, out bool rail)
        {
            var best = 999f;
            rail = false;
            foreach (var line in _edgeLines)
            {
                var d = SegmentDistance(p, line.A, line.B) - line.Half;
                if (d >= best) continue;
                best = d;
                rail = line.Rail;
            }
            return best;
        }

        /// <summary>
        /// On (or within <paramref name="margin"/> of) a feature of the edge the scatter keeps off: a river or road or rail
        /// running out, a corner piece.
        /// </summary>
        private bool OnEdgeFeature(Vector2 p, float margin)
        {
            if (!HasEdges) return false;
            if (_edgeRivers.Count > 0 && EdgeRiverDistance(p) < margin) return true;
            if (_edgeLines.Count > 0 && Beyond(p) > -3f && EdgeLineDistance(p, out _) < margin + 0.5f) return true;
            foreach (var (centre, radius) in _cornerZones)
                if ((p - centre).sqrMagnitude < (radius + margin) * (radius + margin)) return true;
            return false;
        }

        /// <summary>The hills open round the edge's water and lines (a factor on the range's height).</summary>
        private float EdgeValley(Vector2 p)
        {
            var valley = 1f;
            if (_seaField != null) valley *= Mathf.SmoothStep(0f, 1f, SeaDistance(p) / 30f);
            if (_edgeRivers.Count > 0) valley *= Mathf.SmoothStep(0f, 1f, (EdgeRiverDistance(p) - 3f) / 26f);
            if (_edgeLines.Count > 0) valley *= Mathf.SmoothStep(0f, 1f, (EdgeLineDistance(p, out _) - 2f) / 18f);
            return valley;
        }

        /// <summary>The relief and the range flatten under the corner pieces.</summary>
        private float CornerDamp(Vector2 p)
        {
            var damp = 1f;
            foreach (var (centre, radius) in _cornerZones)
                damp = Mathf.Min(damp, Edge(radius * 0.9f, radius + 14f, Vector2.Distance(p, centre)));
            return damp;
        }

        /// <summary>A CLIFF stretch's rock wall beyond the edge (rising from 2 m out to 8-13 m by 11 m), faded at its ends.</summary>
        private float CliffHeight(Vector2 p)
        {
            if (!HasEdges) return 0f;
            var dx = Mathf.Abs(p.x - _centre.x) - _halfX;
            var dz = Mathf.Abs(p.y - _centre.y) - _halfZ;
            if (dx <= 1f && dz <= 1f) return 0f;
            var best = 0f;
            var peaks = Mathf.Clamp(_theme.Peaks, 0.8f, 1.5f);
            for (var k = 0; k < 2; k++)
            {
                var eastWest = k == 0;
                var beyond = eastWest ? dx : dz;
                if (beyond <= 1f) continue;
                var seg = SideSegment(p, eastWest, 0f, out var along);
                if (seg == null || seg.Type != EdgeType.Cliff) continue;
                var raw = eastWest ? p.y : p.x;
                var inside = Mathf.Min(raw - seg.From, seg.To - raw);
                var lateral = Edge(-2f, 14f, inside);
                if (lateral <= 0f) continue;
                var n = Mathf.PerlinNoise(along * 0.07f + 2.1f, beyond * 0.09f + 7.7f);
                var h = (8f + 5f * n) * peaks * Edge(2f, 11f, beyond) * lateral;
                best = Mathf.Max(best, h);
            }
            return best > 0f && InSea(p, 2f) ? 0f : best;
        }

        // ------------------------------------------------------------------------------------------ water meshes

        /// <summary>The edge sea (near and far) and the rivers running out, on the theme's water material.</summary>
        private void BuildEdgeWater(MaterialLibrary materials, SimWorld world)
        {
            if (!HasEdges) return;
            if (_edges.HasSea)
            {
                // Cells that fit the decorated square exactly, so the near and far sheets meet at its edge without a gap.
                var near = Extent * 2f / Mathf.Ceil(Extent);
                var far = Extent * 2f / Mathf.Max(1f, Mathf.Round(Extent * 2f / 20f));
                // Play-test 13: shallow and foaming at the coast, deep offshore (Surroundings.Water).
                var sea = EdgeWater(materials, world);
                Place("Edge Sea", Own(SeaMesh(Extent, near, 0f)), sea);
                Place("Far Sea", Own(SeaMesh(Extent * 3f, far, Extent)), sea);
            }
            foreach (var r in _edgeRivers)
                Place("Edge River", Own(RiverMesh(r)), CalmWater(materials));
        }

        /// <summary>
        /// The sea over a square of half-size <paramref name="half"/> in cells of <paramref name="cell"/>, leaving out the inner
        /// square <paramref name="hole"/>. Play-test 14 session 5 ("chỉ bị khai rìa của biển và mặt đất": along a slanting coast the
        /// water stopped in steps, the ground showing in wedges between them under the slanting foam line): the cells wholly at
        /// sea are runs of quads as before; a cell the coast crosses is cut along it (marching squares: each crossing found on
        /// the cell's sides by halving), so the water reaches the shoreline everywhere, as the shore texture's foam does.
        /// </summary>
        private Mesh SeaMesh(float half, float cell, float hole)
        {
            var vertices = new List<Vector3>();
            var uvs = new List<UnityEngine.Vector2>();
            var triangles = new List<int>();
            var n = Mathf.RoundToInt(half * 2f / cell);
            var x0 = _centre.x - half;
            var z0 = _centre.y - half;
            // Sea or not at every cell corner, once.
            var corner = new bool[(n + 1) * (n + 1)];
            for (var z = 0; z <= n; z++)
            for (var x = 0; x <= n; x++)
                corner[z * (n + 1) + x] = SeaMeshAt(new Vector2(x0 + x * cell, z0 + z * cell), cell);
            var polygon = new List<Vector2>(6);
            for (var z = 0; z < n; z++)
            {
                var za = z0 + z * cell;
                var start = -1;
                for (var x = 0; x <= n; x++)
                {
                    var full = false;
                    var any = false;
                    if (x < n)
                    {
                        var c = new Vector2(x0 + (x + 0.5f) * cell, za + cell * 0.5f);
                        var inHole = hole > 0f && Mathf.Abs(c.x - _centre.x) < hole && Mathf.Abs(c.y - _centre.y) < hole;
                        if (!inHole)
                        {
                            bool a = corner[z * (n + 1) + x], b = corner[(z + 1) * (n + 1) + x];
                            bool d = corner[(z + 1) * (n + 1) + x + 1], e = corner[z * (n + 1) + x + 1];
                            full = a && b && d && e;
                            any = a || b || d || e;
                        }
                    }
                    // Whole sea cells: one quad per run of a row.
                    if (full && start < 0) start = x;
                    if (!full && start >= 0)
                    {
                        SeaQuad(vertices, uvs, triangles, x0 + start * cell, x0 + x * cell, za, za + cell);
                        start = -1;
                    }
                    if (full || !any) continue;
                    // A coast cell: its corners in winding order (+z, then +x: clockwise from above, facing up), the sea ones
                    // kept and a point on the coast added on each side the coast crosses.
                    polygon.Clear();
                    for (var k = 0; k < 4; k++)
                    {
                        var (px, pz) = Corner(k);
                        var (qx, qz) = Corner((k + 1) & 3);
                        var p = new Vector2(x0 + (x + px) * cell, za + pz * cell);
                        var q = new Vector2(x0 + (x + qx) * cell, za + qz * cell);
                        var pSea = corner[(z + pz) * (n + 1) + x + px];
                        var qSea = corner[(z + qz) * (n + 1) + x + qx];
                        if (pSea) polygon.Add(p);
                        if (pSea != qSea) polygon.Add(CoastCrossing(pSea ? p : q, pSea ? q : p, cell));
                    }
                    if (polygon.Count < 3) continue;
                    var first = vertices.Count;
                    foreach (var v in polygon)
                    {
                        vertices.Add(new Vector3(v.x, -0.02f, v.y));
                        uvs.Add(new UnityEngine.Vector2(v.x * 0.02f, v.y * 0.02f));
                    }
                    for (var k = 1; k + 1 < polygon.Count; k++)
                    {
                        triangles.Add(first);
                        triangles.Add(first + k);
                        triangles.Add(first + k + 1);
                    }
                }
            }
            return WaterMesh("Edge Sea", vertices, uvs, triangles);
        }

        /// <summary>A cell's corner <paramref name="k"/> (0..3) as (x, z) steps, in winding order: (0,0), (0,1), (1,1), (1,0).</summary>
        private static (int x, int z) Corner(int k) => k switch
        {
            0 => (0, 0),
            1 => (0, 1),
            2 => (1, 1),
            _ => (1, 0),
        };

        /// <summary>One flat quad of sea from (xa, za) to (xb, zb), clockwise from above (faces up).</summary>
        private static void SeaQuad(List<Vector3> vertices, List<UnityEngine.Vector2> uvs, List<int> triangles, float xa, float xb, float za, float zb)
        {
            var i = vertices.Count;
            vertices.Add(new Vector3(xa, -0.02f, za));
            vertices.Add(new Vector3(xa, -0.02f, zb));
            vertices.Add(new Vector3(xb, -0.02f, zb));
            vertices.Add(new Vector3(xb, -0.02f, za));
            uvs.Add(new UnityEngine.Vector2(xa * 0.02f, za * 0.02f));
            uvs.Add(new UnityEngine.Vector2(xa * 0.02f, zb * 0.02f));
            uvs.Add(new UnityEngine.Vector2(xb * 0.02f, zb * 0.02f));
            uvs.Add(new UnityEngine.Vector2(xb * 0.02f, za * 0.02f));
            triangles.Add(i); triangles.Add(i + 1); triangles.Add(i + 2);
            triangles.Add(i); triangles.Add(i + 2); triangles.Add(i + 3);
        }

        /// <summary>
        /// Where the coast crosses a cell side, from its sea end <paramref name="sea"/> to its land end <paramref name="land"/>:
        /// halved until the step is under 5 cm (so the near and the far sheet, and two cells, meet on the same point).
        /// </summary>
        private Vector2 CoastCrossing(Vector2 sea, Vector2 land, float reach)
        {
            var steps = Mathf.Clamp(Mathf.CeilToInt(Mathf.Log(Mathf.Max(1f, (land - sea).magnitude / 0.05f), 2f)), 1, 12);
            for (var i = 0; i < steps; i++)
            {
                var mid = (sea + land) * 0.5f;
                if (SeaMeshAt(mid, reach)) sea = mid;
                else land = mid;
            }
            return (sea + land) * 0.5f;
        }

        /// <summary>
        /// Whether the sea sheet covers a point: the edge sea; inside the map's rectangle (its own water and ground there), the
        /// corners up to <paramref name="reach"/> in from its edge count as the sea just outside them, so a coast cell on the
        /// edge is not cut along a slant that would open a seam at the map's edge.
        /// </summary>
        private bool SeaMeshAt(Vector2 p, float reach)
        {
            if (EdgeSeaAt(p)) return true;
            var dx = Mathf.Abs(p.x - _centre.x) - _halfX;
            var dz = Mathf.Abs(p.y - _centre.y) - _halfZ;
            if (dx > 0f || dz > 0f || reach <= 0f) return false;
            if (dx < -reach && dz < -reach) return false;
            var q = p;
            if (dx >= dz) q.x = _centre.x + Mathf.Sign(p.x - _centre.x) * (_halfX + 0.05f);
            else q.y = _centre.y + Mathf.Sign(p.y - _centre.y) * (_halfZ + 0.05f);
            return EdgeSeaAt(q);
        }

        /// <summary>A river's channel from the edge out to the horizon (4 m steps, meandering past the corner pieces).</summary>
        private Mesh RiverMesh(EdgeRiver r)
        {
            var vertices = new List<Vector3>();
            var uvs = new List<UnityEngine.Vector2>();
            var triangles = new List<int>();
            var side = new Vector2(-r.Dir.y, r.Dir.x);
            var end = Extent * 1.6f;
            for (var t = -1f; t <= end; t += 4f)
            {
                var mid = r.At + r.Dir * t + side * Meander(r, t);
                var a = mid - side * (r.Half + 0.6f);
                var b = mid + side * (r.Half + 0.6f);
                vertices.Add(new Vector3(a.x, -0.015f, a.y));
                vertices.Add(new Vector3(b.x, -0.015f, b.y));
                uvs.Add(new UnityEngine.Vector2(0f, t * 0.02f));
                uvs.Add(new UnityEngine.Vector2(1f, t * 0.02f));
                if (vertices.Count < 4) continue;
                var i = vertices.Count - 4;
                // "side" is the way turned a quarter anticlockwise, so this winding is clockwise seen from above (faces up).
                triangles.Add(i); triangles.Add(i + 1); triangles.Add(i + 2);
                triangles.Add(i + 1); triangles.Add(i + 3); triangles.Add(i + 2);
            }
            return WaterMesh("Edge River", vertices, uvs, triangles);
        }

        private static Mesh WaterMesh(string name, List<Vector3> vertices, List<UnityEngine.Vector2> uvs, List<int> triangles)
        {
            var mesh = new Mesh { name = name, indexFormat = vertices.Count > 65000 ? IndexFormat.UInt32 : IndexFormat.UInt16 };
            mesh.SetVertices(vertices);
            mesh.SetUVs(0, uvs);
            var normals = new Vector3[vertices.Count];
            var colors = new Color[vertices.Count];
            for (var i = 0; i < normals.Length; i++)
            {
                normals[i] = Vector3.up;
                colors[i] = Color.white;
            }
            mesh.SetNormals(normals);
            mesh.SetColors(colors);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        // ------------------------------------------------------------------------------------------ paint

        /// <summary>The outer ground's paint for the edge: sand along the sea and the rivers, the roads and the rails' ballast running out.</summary>
        private Color PaintEdges(Vector2 p, Color colour, TerrainTheme palette)
        {
            if (!HasEdges || Beyond(p) < 0f) return colour;
            var water = Mathf.Min(SeaDistance(p), _edgeRivers.Count > 0 ? EdgeRiverDistance(p) : 999f);
            if (water < 7f)
            {
                var sand = palette.Sand;
                sand.a = 1f;
                colour = Color.Lerp(colour, sand, Mathf.Clamp01(1f - (water - 2f) / 5f));
            }
            if (_edgeLines.Count > 0)
            {
                var d = EdgeLineDistance(p, out var rail);
                if (d < 1f)
                {
                    var surface = rail ? palette.Stone * 0.75f : palette.Road;
                    surface.a = 1f;
                    colour = Color.Lerp(colour, surface, Mathf.Clamp01(1f - d));
                }
            }
            return colour;
        }

        // ------------------------------------------------------------------------------------------ pieces and dressing

        /// <summary>
        /// The frame a corner piece stands in: its local +Z (<paramref name="ez"/>) and +X (<paramref name="ex"/>) on the ground
        /// (see mb_p33_edges.py). A junction's +Z points out of the map and its -X side has the piece's first type; an outer
        /// piece's +Z strip has its first type.
        /// </summary>
        private bool CornerFrame(EdgeCornerDef corner, DressingCorner piece, out Vector2 at, out Vector2 ez, out Vector2 ex)
        {
            at = new Vector2(corner.Position.X, corner.Position.Y);
            var first = TypeOf(piece.first);
            var east = Mathf.Abs(at.x - (_centre.x + _halfX)) < 0.6f;
            var west = Mathf.Abs(at.x - (_centre.x - _halfX)) < 0.6f;
            var north = Mathf.Abs(at.y - (_centre.y + _halfZ)) < 0.6f;
            var south = Mathf.Abs(at.y - (_centre.y - _halfZ)) < 0.6f;
            if (corner.Outer)
            {
                var nNorthSouth = new Vector2(0f, north ? 1f : -1f);
                var nEastWest = new Vector2(east ? 1f : -1f, 0f);
                // "between" is (the N/S side's type, the E/W side's type).
                var nsFirst = corner.A == first || corner.B != first;
                ez = nsFirst ? nNorthSouth : nEastWest;
                ex = nsFirst ? nEastWest : nNorthSouth;
                return (north || south) && (east || west);
            }
            Vector2 outward, along;
            if (east || west)
            {
                outward = new Vector2(east ? 1f : -1f, 0f);
                along = Vector2.up;
            }
            else if (north || south)
            {
                outward = new Vector2(0f, north ? 1f : -1f);
                along = Vector2.right;
            }
            else
            {
                ez = ex = Vector2.zero;
                return false;
            }
            ez = outward;
            // "between" is (the lower stretch's type, the higher one's): the first type goes on the piece's -X side.
            ex = corner.A == first ? along : -along;
            return true;
        }

        private static EdgeType TypeOf(string type) => type switch
        {
            "SEA" => EdgeType.Sea,
            "RIVER" => EdgeType.River,
            "CLIFF" => EdgeType.Cliff,
            "URBAN" => EdgeType.Urban,
            _ => EdgeType.Land,
        };

        /// <summary>Unity yaw (degrees) turning local +Z onto <paramref name="dir"/> (x, z on the ground).</summary>
        private static float YawOf(Vector2 dir) => Mathf.Atan2(dir.x, dir.y) * Mathf.Rad2Deg;

        /// <summary>Everything the edge types stand round the map (after the biome dressing).</summary>
        private void DressEdges(ModelLibrary models, SimWorld world, List<Rect> fields)
        {
            LayRails(models, world);
            if (!HasEdges || _edgeDress == null) return;
            var rng = new Random(_seed + 303);
            PlaceCorners(models);
            DressSeaEdges(models, rng);
            DressEdgeSets(models, rng, fields);
        }

        /// <summary>The corner pieces, as plain GameObjects (no collider) so a mirrored one draws the right way out.</summary>
        private void PlaceCorners(ModelLibrary models)
        {
            foreach (var corner in _edges.Corners)
            {
                var piece = _edgeDress.Corner(corner.Piece);
                if (piece == null || string.IsNullOrEmpty(piece.model) || !models.Has(piece.model)) continue;
                if (!CornerFrame(corner, piece, out var at, out var ez, out var ex)) continue;
                var yaw = YawOf(ez);
                var r = yaw * Mathf.Deg2Rad;
                var localX = new Vector2(Mathf.Cos(r), -Mathf.Sin(r));
                var mirror = Vector2.Dot(localX, ex) < 0f;
                var instance = models.Spawn(piece.model, -1, _root.transform, castShadows: true);
                var t = instance.Root.transform;
                t.position = new Vector3(at.x, 0f, at.y);
                t.rotation = Quaternion.Euler(0f, yaw, 0f);
                t.localScale = new Vector3(mirror ? -1f : 1f, 1f, 1f);
                CornersPlaced++;
            }
        }

        /// <summary>Corner pieces stood (for the scenery log).</summary>
        public int CornersPlaced { get; private set; }

        /// <summary>One coast line beyond the map: where it starts, its way out, the sea's side of it and the shore kind.</summary>
        private readonly struct CoastLine
        {
            public CoastLine(Vector2 start, Vector2 outward, Vector2 seaward, string shore, bool wobbly, bool eastWest, bool high)
            {
                Start = start;
                Outward = outward;
                Seaward = seaward;
                Shore = shore;
                Wobbly = wobbly;
                EastWest = eastWest;
                High = high;
            }

            public Vector2 Start { get; }
            public Vector2 Outward { get; }
            public Vector2 Seaward { get; }
            public string Shore { get; }
            public bool Wobbly { get; }
            public bool EastWest { get; }
            public bool High { get; }
        }

        private List<CoastLine> CoastLines()
        {
            var lines = new List<CoastLine>();
            foreach (var corner in _edges.Corners)
            {
                if (corner.A != EdgeType.Sea && corner.B != EdgeType.Sea) continue;
                if (corner.A == EdgeType.Sea && corner.B == EdgeType.Sea) continue;
                var at = new Vector2(corner.Position.X, corner.Position.Y);
                var east = Mathf.Abs(at.x - (_centre.x + _halfX)) < 0.6f;
                var west = Mathf.Abs(at.x - (_centre.x - _halfX)) < 0.6f;
                var north = Mathf.Abs(at.y - (_centre.y + _halfZ)) < 0.6f;
                var south = Mathf.Abs(at.y - (_centre.y - _halfZ)) < 0.6f;
                if (corner.Outer)
                {
                    // The sea takes the corner: the coast runs on along the SEA side's own line.
                    var nsSea = corner.A == EdgeType.Sea;
                    var seaward = nsSea ? new Vector2(0f, north ? 1f : -1f) : new Vector2(east ? 1f : -1f, 0f);
                    var outward = nsSea ? new Vector2(east ? 1f : -1f, 0f) : new Vector2(0f, north ? 1f : -1f);
                    var seg = nsSea ? _edges.At(north ? "N" : "S", at.x) : _edges.At(east ? "E" : "W", at.y);
                    lines.Add(new CoastLine(at, outward, seaward, seg?.Shore ?? "BEACH", false, false, false));
                }
                else
                {
                    var eastWest = east || west;
                    var outward = eastWest ? new Vector2(east ? 1f : -1f, 0f) : new Vector2(0f, north ? 1f : -1f);
                    var along = eastWest ? Vector2.up : Vector2.right;
                    var seaHigh = corner.B == EdgeType.Sea;
                    var side = eastWest ? (east ? "E" : "W") : (north ? "N" : "S");
                    var u = eastWest ? at.y : at.x;
                    var seg = _edges.At(side, u + (seaHigh ? 1f : -1f));
                    lines.Add(new CoastLine(at, outward, seaHigh ? along : -along, seg?.Shore ?? "BEACH", true, eastWest,
                        eastWest ? east : north));
                }
            }
            return lines;
        }

        /// <summary>A point of a coast line <paramref name="t"/> metres out (on the wobbling boundary EdgeSeaAt draws).</summary>
        private Vector2 CoastPoint(CoastLine line, float t)
        {
            var p = line.Start + line.Outward * t;
            if (!line.Wobbly) return p;
            // EdgeSeaAt shifts "along" by the wobble before it looks the stretch up, so the boundary sits that much the other way.
            var w = CoastWobble(t, line.EastWest, line.High);
            var alongDir = line.EastWest ? Vector2.up : Vector2.right;
            return p - alongDir * w;
        }

        /// <summary>The sea side: whitecaps, the shores along the coast lines, far ships, hazy islands and the lanes' buoys.</summary>
        private void DressSeaEdges(ModelLibrary models, Random rng)
        {
            var sea = _edgeDress.sea;
            if (sea == null || !_edges.HasSea) return;
            var waves = Usable(models, sea.waves);
            var density = DressDensity;
            var reach = Extent * 1.15f;
            var target = Mathf.Min(700, Mathf.RoundToInt(sea.waveDensity * density * SeaArea / Hectare));
            for (int i = 0, tries = 0; i < target && tries < target * 8 + 50 && waves.Count > 0; tries++)
            {
                var p = _centre + new Vector2((float)(rng.NextDouble() * 2 - 1) * reach, (float)(rng.NextDouble() * 2 - 1) * reach);
                if (Beyond(p) < 6f || !EdgeSeaAt(p) || SeaDistanceFromLand(p) < 4f) continue;
                Add(models, waves[rng.Next(waves.Count)], p, (float)rng.NextDouble() * 360f, 0.8f + (float)rng.NextDouble() * 0.7f,
                    0f, shadowless: true);
                i++;
                DressingPlaced++;
            }

            var outer = _zones.EdgeBand + Mathf.Max(_zones.RingX, _zones.RingZ);
            foreach (var line in CoastLines())
            {
                var shore = line.Shore ?? "BEACH";
                var tangent = line.Outward;
                for (var t = CoastStraight - 4f; t < outer + 70f; t += shore == "QUAY" ? 12f : shore == "CLIFF" ? 20f : 11f)
                {
                    var p = CoastPoint(line, t);
                    var next = CoastPoint(line, t + 4f);
                    tangent = (next - p).sqrMagnitude > 1e-4f ? (next - p).normalized : tangent;
                    var seaward = Vector2.Dot(line.Seaward, new Vector2(-tangent.y, tangent.x)) >= 0f
                        ? new Vector2(-tangent.y, tangent.x) : new Vector2(tangent.y, -tangent.x);
                    switch (shore)
                    {
                        case "QUAY":
                            AddIf(models, sea.quay, p, YawOf(seaward), 1f, 0f, false);
                            if (((int)(t / 12f)) % 4 == 1) AddIf(models, sea.crane, p - seaward * 8f, YawOf(seaward), 1f, 0f, true);
                            if (((int)(t / 12f)) % 3 == 0)
                                AddIf(models, sea.containers, p - seaward * (16f + (float)rng.NextDouble() * 12f),
                                    YawOf(tangent) + 90f, 1f, 0f, true);
                            break;
                        case "CLIFF":
                            AddIf(models, sea.stack, p + seaward * (5f + (float)rng.NextDouble() * 5f), (float)rng.NextDouble() * 360f,
                                0.8f + (float)rng.NextDouble() * 0.6f, -0.2f, true);
                            break;
                        default:
                            AddIf(models, sea.surf, p + seaward * 2f, YawOf(tangent), 1f, 0f, true);
                            break;
                    }
                }
            }

            // Far ships and hazy islands on the horizon off each SEA side, along its longest SEA stretch.
            var ships = Usable(models, sea.ships);
            var islands = Usable(models, sea.islands);
            foreach (var side in new[] { "N", "E", "S", "W" })
            {
                EdgeSegmentDef longest = null;
                foreach (var s in _edges.Segments)
                    if (s.Side == side && s.Type == EdgeType.Sea && (longest == null || s.To - s.From > longest.To - longest.From)) longest = s;
                if (longest == null) continue;
                var eastWest = side is "E" or "W";
                var normal = side switch { "N" => Vector2.up, "S" => Vector2.down, "E" => Vector2.right, _ => Vector2.left };
                var alongDir = eastWest ? Vector2.up : Vector2.right;
                Vector2 SidePoint(float u) => eastWest
                    ? new Vector2(side == "E" ? _centre.x + _halfX : _centre.x - _halfX, u)
                    : new Vector2(u, side == "N" ? _centre.y + _halfZ : _centre.y - _halfZ);
                for (var i = 0; i < sea.shipsPerSide && ships.Count > 0; i++)
                {
                    var u = Mathf.Lerp(longest.From, longest.To, (i + 0.3f + 0.4f * (float)rng.NextDouble()) / sea.shipsPerSide);
                    var p = SidePoint(u) + normal * (outer + 40f + (float)rng.NextDouble() * 130f);
                    if (!EdgeSeaAt(p)) continue;
                    var yaw = YawOf(alongDir) + (rng.Next(2) == 0 ? 0f : 180f) + ((float)rng.NextDouble() - 0.5f) * 30f;
                    Add(models, ships[rng.Next(ships.Count)], p, yaw, 0.9f + (float)rng.NextDouble() * 0.3f, -1.2f, shadowless: true);
                    DressingPlaced++;
                }
                for (var i = 0; i < sea.islandsPerSide && islands.Count > 0; i++)
                {
                    var u = Mathf.Lerp(longest.From - 120f, longest.To + 120f, (i + (float)rng.NextDouble()) / sea.islandsPerSide);
                    var p = SidePoint(u) + normal * (outer + 170f + (float)rng.NextDouble() * 260f);
                    if (!EdgeSeaAt(p)) continue;
                    Add(models, islands[rng.Next(islands.Count)], p, YawOf(alongDir) + ((float)rng.NextDouble() - 0.5f) * 40f,
                        0.8f + (float)rng.NextDouble() * 0.8f, -0.8f, shadowless: true);
                    DressingPlaced++;
                }
            }

            // The sea lanes run on out of the map: a line of buoys along each (L4's routes beyond the play area).
            if (!string.IsNullOrEmpty(sea.laneBuoy) && sea.laneStep > 1f)
                foreach (var link in _edges.Links)
                {
                    if (link.Kind != "seaLane") continue;
                    var at = new Vector2(link.Position.X, link.Position.Y);
                    var dir = new Vector2(link.Outward.X, link.Outward.Y).normalized;
                    var across = new Vector2(-dir.y, dir.x);
                    var k = 0;
                    for (var t = 15f; t < outer + 80f; t += sea.laneStep, k++)
                    {
                        var p = at + dir * t + across * (k % 2 == 0 ? 9f : -9f);
                        if (EdgeSeaAt(p)) AddIf(models, sea.laneBuoy, p, (float)rng.NextDouble() * 360f, 1f, -0.15f, true);
                    }
                }
        }

        /// <summary>The biome's buoys (its sea set) on the edge sea in the band and the ring.</summary>
        private void DressEdgeBuoys(ModelLibrary models, Random rng, List<string> buoys)
        {
            if (buoys.Count == 0 || SeaArea <= 0f) return;
            var outer = _zones.EdgeBand + Mathf.Max(_zones.RingX, _zones.RingZ);
            var count = Mathf.Clamp(Mathf.RoundToInt(0.6f * DressDensity * SeaArea / Hectare), 2, 16);
            for (int i = 0, tries = 0; i < count && tries < count * 20; tries++)
            {
                var p = DressPoint(rng, outer);
                if (Beyond(p) < 8f || !EdgeSeaAt(p) || SeaDistanceFromLand(p) < 6f) continue;
                Add(models, buoys[rng.Next(buoys.Count)], p, (float)rng.NextDouble() * 360f, 0.9f + (float)rng.NextDouble() * 0.3f,
                    -0.15f, shadowless: true);
                DressingPlaced++;
                i++;
            }
        }

        /// <summary>Metres from a sea point to the nearest land of the field (999 off the field): keeps whitecaps off the beach.</summary>
        private float SeaDistanceFromLand(Vector2 p)
        {
            for (var r = 2f; r <= 6f; r += 2f)
                if (!EdgeSeaAt(p + new Vector2(r, 0f)) || !EdgeSeaAt(p - new Vector2(r, 0f)) || !EdgeSeaAt(p + new Vector2(0f, r)) ||
                    !EdgeSeaAt(p - new Vector2(0f, r)))
                    return r;
            return 999f;
        }

        private void AddIf(ModelLibrary models, string model, Vector2 p, float yaw, float scale, float height, bool shadowless)
        {
            if (string.IsNullOrEmpty(model)) return;
            if (!_hasModel.TryGetValue(model, out var has)) _hasModel[model] = has = models.Has(model);
            if (!has) return;
            Add(models, model, p, yaw, scale, height, shadowless);
            DressingPlaced++;
        }

        /// <summary>The edge types' and modifiers' ring sets (INDUSTRIAL, HARBOR, URBAN, CLIFF) beyond each stretch.</summary>
        private void DressEdgeSets(ModelLibrary models, Random rng, List<Rect> fields)
        {
            var band = _zones.EdgeBand;
            foreach (var seg in _edges.Segments)
            {
                if (seg.Type == EdgeType.Sea) continue;
                var key = seg.Modifier switch
                {
                    EdgeModifier.Industrial => "INDUSTRIAL",
                    EdgeModifier.Harbor => "HARBOR",
                    EdgeModifier.Urban => _theme.Skyline == null ? "URBAN" : null,
                    _ => null,
                };
                if (seg.Type == EdgeType.Cliff) key = "CLIFF";
                else if (seg.Type == EdgeType.Urban && key == null && _theme.Skyline == null) key = "URBAN";
                var set = _edgeDress.Set(key);
                if (set == null || set.ring <= 0f) continue;
                var list = Usable(models, set.set);
                if (list.Count == 0) continue;
                var eastWest = seg.Side is "E" or "W";
                var ring = eastWest ? _zones.RingX : _zones.RingZ;
                var normal = seg.Side switch { "N" => Vector2.up, "S" => Vector2.down, "E" => Vector2.right, _ => Vector2.left };
                var target = Mathf.RoundToInt(set.ring * DressDensity * (seg.To - seg.From) * ring / Hectare);
                var cliff = key == "CLIFF";
                for (int i = 0, tries = 0; i < target && tries < target * 10 + 20; tries++)
                {
                    var u = Mathf.Lerp(seg.From, seg.To, (float)rng.NextDouble());
                    var o = cliff ? 2f + (float)rng.NextDouble() * 14f : band * 0.6f + (float)rng.NextDouble() * (ring + band * 0.4f);
                    var edgePoint = eastWest
                        ? new Vector2(seg.Side == "E" ? _centre.x + _halfX : _centre.x - _halfX, u)
                        : new Vector2(u, seg.Side == "N" ? _centre.y + _halfZ : _centre.y - _halfZ);
                    var p = edgePoint + normal * o;
                    if (InSea(p, 3f) || NearRiver(p, 3f) || InField(p, fields)) continue;
                    if (!cliff && InCity(p)) continue;
                    var height = Height(p);
                    if (!cliff && height > TreeLine) continue;
                    var yaw = cliff ? (float)rng.NextDouble() * 360f : YawOf(-normal) + rng.Next(4) * 90f + ((float)rng.NextDouble() - 0.5f) * 10f;
                    Add(models, list[rng.Next(list.Count)], p, yaw, 0.85f + (float)rng.NextDouble() * 0.35f, height - 0.1f,
                        shadowless: o > band);
                    DressingPlaced++;
                    i++;
                }
            }
        }

        /// <summary>
        /// The railway along every RailSpline (L5): track sections laid end to end over its whole length (the play stretch
        /// too: nothing else draws it), and a tunnel portal at each end beyond the map.
        /// </summary>
        private void LayRails(ModelLibrary models, SimWorld world)
        {
            var rail = _edgeDress?.rail;
            if (rail == null || world.Map.Rails.Count == 0) return;
            var step = rail.step > 1f ? rail.step : 6f;
            foreach (var line in world.Map.Rails)
            {
                for (var s = step * 0.5f; s < line.Length; s += step)
                {
                    var at = line.At(s);
                    var t = line.Tangent(s);
                    AddIf(models, rail.track, new Vector2(at.X, at.Y), YawOf(new Vector2(t.X, t.Y)), 1f, 0f, true);
                }
                var start = line.At(0f);
                var startDir = line.Tangent(0f);
                if (Beyond(new Vector2(start.X, start.Y)) > 4f)
                    AddIf(models, rail.portal, new Vector2(start.X, start.Y), YawOf(new Vector2(-startDir.X, -startDir.Y)), 1f, 0f, false);
                var end = line.At(line.Length);
                var endDir = line.Tangent(line.Length);
                if (Beyond(new Vector2(end.X, end.Y)) > 4f)
                    AddIf(models, rail.portal, new Vector2(end.X, end.Y), YawOf(new Vector2(endDir.X, endDir.Y)), 1f, 0f, false);
            }
        }
    }
}
