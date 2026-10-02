#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>What a node of the sea route graph is: a point on a lane, a holding node (a passing bay), or a lane's exit beyond the map.</summary>
    public enum SeaNodeKind
    {
        Track,
        Holding,
        Exit,
    }

    /// <summary>A node of the sea route graph (world position; its place in the coast's frame once bound to the sea).</summary>
    public sealed class SeaNode
    {
        internal SeaNode(int index, string id, Vector2 position, SeaNodeKind kind, string? lane)
        {
            Index = index;
            Id = id;
            Position = position;
            Kind = kind;
            Lane = lane;
        }

        public int Index { get; }
        public string Id { get; }
        public Vector2 Position { get; }
        public SeaNodeKind Kind { get; }

        /// <summary>The sea lane it lies on (a holding node: the lane it serves).</summary>
        public string? Lane { get; }

        /// <summary>(u along the coast, w out to sea), set by <see cref="SeaRouteGraph.Bind"/>.</summary>
        public Vector2 Frame { get; internal set; }
    }

    /// <summary>What a segment joins: two nodes of one lane, a lane node and its holding node, or two lanes at the same place.</summary>
    public enum SeaSegmentKind
    {
        Track,
        Bay,
        Cross,
    }

    /// <summary>A segment of the sea route graph: two nodes, two-way unless <see cref="OneWay"/> (then only from A to B).</summary>
    public sealed class SeaSegment
    {
        internal SeaSegment(int index, int a, int b, SeaSegmentKind kind, bool oneWay, string? lane, float length)
        {
            Index = index;
            A = a;
            B = b;
            Kind = kind;
            OneWay = oneWay;
            Lane = lane;
            Length = length;
        }

        public int Index { get; }
        public int A { get; }
        public int B { get; }
        public SeaSegmentKind Kind { get; }
        public bool OneWay { get; }
        public string? Lane { get; }
        public float Length { get; }
    }

    /// <summary>
    /// Prompt 33 L4 (DECISIONS "Prompt 33 L4"): the big ships' routes at sea. Boss ships, escorts and transports never use the
    /// ground grid: they sail the sea lanes, and this graph is those lanes cut into segments (a track node every
    /// <see cref="NodeStep"/> m along each lane, an exit node <see cref="ExitReach"/> m beyond each end, outside the play
    /// area), with holding nodes (passing bays) on a holding line inshore of the nearest lane and one out beyond the farthest,
    /// and cross links between neighbouring lanes. Map data "seaRoutes" (written by Tools/maps/transit.py with the same rule
    /// as <see cref="FromSea"/>); a sea without it (the Sandbox's coastal range) gets the graph built from its lanes. The
    /// naval system's traffic rules (reservations, priority, holding) run on it; small boats keep to the lanes as before.
    /// </summary>
    public sealed class SeaRouteGraph
    {
        public const float NodeStep = 40f;
        public const float ExitReach = 40f;
        public const float HoldShore = 16f;
        public const float HoldSea = 18f;
        public const float HoldMargin = 12f;
        public const float HoldWater = 8f;
        public const float DefaultCorridor = 20f;

        /// <summary>Every lane node has a passing bay within this far along the coast (two-way lanes).</summary>
        public const float BayReach = 60f;

        private readonly List<SeaNode> _nodes = new();
        private readonly List<SeaSegment> _segments = new();
        private readonly Dictionary<string, int> _byId = new();

        public IReadOnlyList<SeaNode> Nodes => _nodes;
        public IReadOnlyList<SeaSegment> Segments => _segments;

        /// <summary>How far off a lane's line a big ship may stand and still be on the routes (its escort slots, its holding).</summary>
        public float Corridor { get; private set; } = DefaultCorridor;

        public bool TryGet(string id, out SeaNode node)
        {
            if (_byId.TryGetValue(id, out var i))
            {
                node = _nodes[i];
                return true;
            }
            node = null!;
            return false;
        }

        private int AddNode(string id, Vector2 at, SeaNodeKind kind, string? lane)
        {
            if (_byId.ContainsKey(id)) throw new FormatException($"seaRoutes: node {id} twice.");
            var node = new SeaNode(_nodes.Count, id, at, kind, lane);
            _byId[id] = node.Index;
            _nodes.Add(node);
            return node.Index;
        }

        private void AddSegment(int a, int b, bool oneWay)
        {
            var na = _nodes[a];
            var nb = _nodes[b];
            var kind = na.Kind == SeaNodeKind.Holding || nb.Kind == SeaNodeKind.Holding ? SeaSegmentKind.Bay
                : na.Lane != null && na.Lane == nb.Lane ? SeaSegmentKind.Track : SeaSegmentKind.Cross;
            var lane = kind == SeaSegmentKind.Track ? na.Lane : null;
            _segments.Add(new SeaSegment(_segments.Count, a, b, kind, oneWay, lane, Vector2.Distance(na.Position, nb.Position)));
        }

        /// <summary>Map data "seaRoutes": {"corridor", "nodes": [{"id", "x", "z", "kind", "lane"}], "segments": [{"a", "b", "oneWay"}]}.</summary>
        internal static SeaRouteGraph Parse(JsonObject o)
        {
            var g = new SeaRouteGraph { Corridor = o.Float("corridor", DefaultCorridor) };
            foreach (var n in o.Array("nodes"))
            {
                var kind = n.Has("kind") ? n.String("kind") switch
                {
                    "holding" => SeaNodeKind.Holding,
                    "exit" => SeaNodeKind.Exit,
                    "track" => SeaNodeKind.Track,
                    var other => throw new FormatException($"{n.Path}.kind: track, holding or exit, not {other}"),
                } : SeaNodeKind.Track;
                g.AddNode(n.String("id"), new Vector2(n.Float("x"), n.Float("z")), kind, n.OptionalString("lane"));
            }
            foreach (var s in o.Array("segments"))
            {
                var a = s.String("a");
                var b = s.String("b");
                if (!g._byId.TryGetValue(a, out var ia) || !g._byId.TryGetValue(b, out var ib))
                    throw new FormatException($"{s.Path}: segment {a}-{b} names a missing node.");
                g.AddSegment(ia, ib, s.Bool("oneWay", false));
            }
            return g;
        }

        /// <summary>The graph built from a sea's lanes (the rule Tools/maps/transit.py writes into the map files).</summary>
        public static SeaRouteGraph FromSea(SeaDef sea, float halfSize)
        {
            var g = new SeaRouteGraph();
            var tracks = new List<List<int>>();
            var frames = new Dictionary<int, Vector2>();
            int Node(string id, float u, float w, SeaNodeKind kind, string lane)
            {
                var i = g.AddNode(id, sea.At(u, w), kind, lane);
                frames[i] = new Vector2(u, w);
                return i;
            }
            bool Inside(float u, float w, float margin)
            {
                var p = sea.At(u, w);
                return MathF.Abs(p.X) <= halfSize - margin && MathF.Abs(p.Y) <= halfSize - margin;
            }
            foreach (var lane in sea.Lanes)
            {
                var us = new List<float> { -(lane.End + ExitReach) };
                var k0 = (int)MathF.Ceiling(-lane.End / NodeStep);
                var k1 = (int)MathF.Floor(lane.End / NodeStep);
                for (var k = k0; k <= k1; k++) us.Add(k * NodeStep);
                us.Add(lane.End + ExitReach);
                var ids = new List<int>();
                for (var i = 0; i < us.Count; i++)
                    ids.Add(Node($"{lane.Id}_{i}", us[i], lane.W, i == 0 || i == us.Count - 1 ? SeaNodeKind.Exit : SeaNodeKind.Track, lane.Id));
                for (var i = 0; i + 1 < ids.Count; i++) g.AddSegment(ids[i], ids[i + 1], false);
                tracks.Add(ids);
            }
            if (sea.Lanes.Count == 0) return g;
            for (var l = 0; l + 1 < tracks.Count; l++)
                for (var i = 1; i + 1 < tracks[l].Count; i++)
                    for (var j = 1; j + 1 < tracks[l + 1].Count; j++)
                        if (MathF.Abs(frames[tracks[l][i]].X - frames[tracks[l + 1][j]].X) < 0.01f) g.AddSegment(tracks[l][i], tracks[l + 1][j], false);
            var lines = new[] { (sea.Lanes[0].W - HoldShore, 0, "shore"), (sea.Lanes[sea.Lanes.Count - 1].W + HoldSea, tracks.Count - 1, "sea") };
            foreach (var (w, l, side) in lines)
            {
                var track = tracks[l];
                for (var i = 1; i + 1 < track.Count; i++)
                {
                    var u = frames[track[i]].X;
                    if (!Inside(u, w, HoldMargin) || !sea.IsSea(sea.At(u, w), HoldWater)) continue;
                    var h = Node($"hold_{side}_{g._nodes[track[i]].Id}", u, w, SeaNodeKind.Holding, sea.Lanes[l].Id);
                    g.AddSegment(track[i], h, false);
                }
            }
            return g;
        }

        /// <summary>Puts every node in the coast's frame (u, w).</summary>
        internal void Bind(SeaDef sea)
        {
            foreach (var n in _nodes) n.Frame = sea.Frame(n.Position);
        }

        /// <summary>The lane segment nearest a point (-1: none), its parameter along it (0 at A) and the distance to it.</summary>
        public int NearestTrack(Vector2 p, out float t, out float distance)
        {
            var best = -1;
            t = 0f;
            distance = float.MaxValue;
            foreach (var s in _segments)
            {
                if (s.Kind != SeaSegmentKind.Track) continue;
                var a = _nodes[s.A].Position;
                var ab = _nodes[s.B].Position - a;
                var len2 = ab.LengthSquared();
                var k = len2 > 1e-6f ? Math.Clamp(Vector2.Dot(p - a, ab) / len2, 0f, 1f) : 0f;
                var d = Vector2.Distance(p, a + ab * k);
                if (d >= distance - 1e-4f) continue;
                distance = d;
                best = s.Index;
                t = k;
            }
            return best;
        }

        /// <summary>The next lane segment from <paramref name="segment"/> going towards +u (<paramref name="dir"/> 1) or -u (-1); -1 at the lane's end.</summary>
        public int NextAlong(int segment, int dir)
        {
            if (segment < 0 || segment >= _segments.Count) return -1;
            var s = _segments[segment];
            var ua = _nodes[s.A].Frame.X;
            var ub = _nodes[s.B].Frame.X;
            var end = (ub - ua) * dir >= 0f ? s.B : s.A;
            foreach (var o in _segments)
            {
                if (o.Index == segment || o.Kind != SeaSegmentKind.Track || o.Lane != s.Lane) continue;
                if (o.A != end && o.B != end) continue;
                var far = o.A == end ? o.B : o.A;
                if ((_nodes[far].Frame.X - _nodes[end].Frame.X) * dir > 0f) return o.Index;
            }
            return -1;
        }

        /// <summary>Whether travel along a segment towards +u (or -u) is allowed (a one-way segment only from A to B).</summary>
        public bool Allows(int segment, int dir)
        {
            if (segment < 0 || segment >= _segments.Count) return true;
            var s = _segments[segment];
            return !s.OneWay || (_nodes[s.B].Frame.X - _nodes[s.A].Frame.X) * dir >= 0f;
        }

        /// <summary>Whether a point is on the routes: within <see cref="Corridor"/> of a lane segment or a holding node.</summary>
        public bool InCorridor(Vector2 p)
        {
            NearestTrack(p, out _, out var d);
            if (d <= Corridor) return true;
            foreach (var n in _nodes)
                if (n.Kind == SeaNodeKind.Holding && Vector2.Distance(n.Position, p) <= Corridor) return true;
            return false;
        }

        /// <summary>
        /// The graph's checks (the tests and Tools/maps/transit.py): nodes inside the map on the water, exits beyond the edge,
        /// every lane joined end to end, a passing bay within <see cref="BayReach"/> m along the coast of every node of a
        /// two-way lane, every holding node joined to a lane.
        /// </summary>
        public IReadOnlyList<string> Validate(SeaDef sea, float halfSize)
        {
            var problems = new List<string>();
            Bind(sea);
            foreach (var n in _nodes)
            {
                var onMap = MathF.Abs(n.Position.X) <= halfSize && MathF.Abs(n.Position.Y) <= halfSize;
                if (n.Kind == SeaNodeKind.Exit)
                {
                    if (onMap) problems.Add($"exit {n.Id} is inside the map");
                    continue;
                }
                if (onMap && !sea.IsSea(n.Position, 4f)) problems.Add($"node {n.Id} is not on the water");
            }
            var lanes = new HashSet<string>();
            foreach (var n in _nodes)
                if (n.Lane != null && n.Kind != SeaNodeKind.Holding) lanes.Add(n.Lane);
            foreach (var lane in lanes)
            {
                // Joined end to end: from its lowest-u node, NextAlong reaches every node of the lane.
                var count = 0;
                var oneWay = false;
                foreach (var s in _segments)
                    if (s.Kind == SeaSegmentKind.Track && s.Lane == lane)
                    {
                        count++;
                        oneWay |= s.OneWay;
                    }
                var first = -1;
                var lowest = float.MaxValue;
                foreach (var s in _segments)
                {
                    if (s.Kind != SeaSegmentKind.Track || s.Lane != lane) continue;
                    var u = MathF.Min(_nodes[s.A].Frame.X, _nodes[s.B].Frame.X);
                    if (u < lowest)
                    {
                        lowest = u;
                        first = s.Index;
                    }
                }
                var walked = 0;
                for (var s = first; s >= 0 && walked <= count; s = NextAlong(s, 1)) walked++;
                if (walked != count) problems.Add($"lane {lane}: {walked} of its {count} segments joined end to end");
                if (oneWay) continue;
                foreach (var n in _nodes)
                {
                    if (n.Lane != lane || n.Kind != SeaNodeKind.Track) continue;
                    var bay = false;
                    foreach (var h in _nodes)
                        if (h.Kind == SeaNodeKind.Holding && MathF.Abs(h.Frame.X - n.Frame.X) <= BayReach) bay = true;
                    if (!bay) problems.Add($"lane node {n.Id}: no passing bay within {BayReach:0} m");
                }
            }
            foreach (var h in _nodes)
            {
                if (h.Kind != SeaNodeKind.Holding) continue;
                var joined = false;
                foreach (var s in _segments)
                    if (s.Kind == SeaSegmentKind.Bay && (s.A == h.Index || s.B == h.Index)) joined = true;
                if (!joined) problems.Add($"holding node {h.Id} is joined to no lane");
                if (MathF.Abs(h.Position.X) > halfSize - 2f || MathF.Abs(h.Position.Y) > halfSize - 2f) problems.Add($"holding node {h.Id} is off the map");
            }
            return problems;
        }
    }
}
