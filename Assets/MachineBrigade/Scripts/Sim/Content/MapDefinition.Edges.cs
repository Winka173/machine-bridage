#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Prompt 33 L2: what lies beyond a stretch of the map's edge.</summary>
    public enum EdgeType
    {
        Land,
        Sea,
        River,
        Cliff,
        Urban,
    }

    /// <summary>Prompt 33 L2: an optional flavour of an edge stretch (Ironport's sea is a harbour).</summary>
    public enum EdgeModifier
    {
        None,
        Harbor,
        Industrial,
        Urban,
    }

    /// <summary>One stretch of a side of the map's rectangle with one edge type ("from"/"to" along x on N and S, along z on E and W).</summary>
    public sealed class EdgeSegmentDef
    {
        public EdgeSegmentDef(string side, float from, float to, EdgeType type, EdgeModifier modifier, string? shore)
        {
            Side = side;
            From = from;
            To = to;
            Type = type;
            Modifier = modifier;
            Shore = shore;
        }

        public string Side { get; }
        public float From { get; }
        public float To { get; }
        public EdgeType Type { get; }
        public EdgeModifier Modifier { get; }

        /// <summary>On a SEA stretch, how the coast meets the land: BEACH, CLIFF or QUAY (null elsewhere).</summary>
        public string? Shore { get; }
    }

    /// <summary>Where two edge types meet: the prebuilt corner piece the view puts there (never random ground).</summary>
    public sealed class EdgeCornerDef
    {
        public EdgeCornerDef(Vector2 position, EdgeType a, EdgeType b, string piece, bool outer)
        {
            Position = position;
            A = a;
            B = b;
            Piece = piece;
            Outer = outer;
        }

        public Vector2 Position { get; }
        public EdgeType A { get; }
        public EdgeType B { get; }
        public string Piece { get; }

        /// <summary>One of the rectangle's four corners (else a change of type along a side).</summary>
        public bool Outer { get; }
    }

    /// <summary>A line that meets the edge and runs on out (road, rail, river, coast, seaLane, air): the view draws it on.</summary>
    public sealed class EdgeLinkDef
    {
        public EdgeLinkDef(string kind, Vector2 position, Vector2 outward, float width)
        {
            Kind = kind;
            Position = position;
            Outward = outward;
            Width = width;
        }

        public string Kind { get; }
        public Vector2 Position { get; }
        public Vector2 Outward { get; }
        public float Width { get; }
    }

    /// <summary>Prompt 33 L2: the map's edges (map data "edges", Tools/maps/edges.py), empty on a map without them.</summary>
    public sealed class MapEdgesDef
    {
        public static readonly MapEdgesDef None = new(0f, 0f, Array.Empty<EdgeSegmentDef>(), Array.Empty<EdgeCornerDef>(), Array.Empty<EdgeLinkDef>());

        public MapEdgesDef(float band, float outer, IReadOnlyList<EdgeSegmentDef> segments, IReadOnlyList<EdgeCornerDef> corners, IReadOnlyList<EdgeLinkDef> links)
        {
            Band = band;
            Outer = outer;
            Segments = segments;
            Corners = corners;
            Links = links;
        }

        /// <summary>The edge band's width (metres, view only).</summary>
        public float Band { get; }

        /// <summary>How far the lines run on beyond the rectangle (metres, view only).</summary>
        public float Outer { get; }

        public IReadOnlyList<EdgeSegmentDef> Segments { get; }
        public IReadOnlyList<EdgeCornerDef> Corners { get; }
        public IReadOnlyList<EdgeLinkDef> Links { get; }

        /// <summary>The stretch of <paramref name="side"/> at <paramref name="along"/>, or null.</summary>
        public EdgeSegmentDef? At(string side, float along)
        {
            foreach (var s in Segments)
                if (s.Side == side && along >= s.From - 1e-3f && along <= s.To + 1e-3f) return s;
            return null;
        }

        /// <summary>Whether any stretch of the edge is sea.</summary>
        public bool HasSea
        {
            get
            {
                foreach (var s in Segments)
                    if (s.Type == EdgeType.Sea) return true;
                return false;
            }
        }

        internal static MapEdgesDef Parse(JsonObject root)
        {
            if (!root.Has("edges")) return None;
            var e = root.Object("edges");
            var segments = new List<EdgeSegmentDef>();
            foreach (var s in e.Array("segments"))
                segments.Add(new EdgeSegmentDef(s.String("side"), s.Float("from"), s.Float("to"), TypeOf(s.String("type")),
                    ModifierOf(s.OptionalString("modifier")), s.OptionalString("shore")));
            var corners = new List<EdgeCornerDef>();
            if (e.Has("corners"))
                foreach (var c in e.Array("corners"))
                {
                    var between = c.Raw.TryGetValue("between", out var b) && b is List<object?> pair && pair.Count == 2 ? pair : null;
                    corners.Add(new EdgeCornerDef(new Vector2(c.Float("x"), c.Float("z")), TypeOf(between?[0] as string), TypeOf(between?[1] as string),
                        c.String("piece"), c.Bool("outer", false)));
                }
            var links = new List<EdgeLinkDef>();
            if (e.Has("links"))
                foreach (var l in e.Array("links"))
                    links.Add(new EdgeLinkDef(l.String("kind"), new Vector2(l.Float("x"), l.Float("z")), new Vector2(l.Float("dirX", 0f), l.Float("dirZ", 0f)),
                        l.Float("width", 0f)));
            return new MapEdgesDef(e.Float("band", 16f), e.Float("outer", EntryGate.OuterLength), segments, corners, links);
        }

        private static EdgeType TypeOf(string? type) => type switch
        {
            "SEA" => EdgeType.Sea,
            "RIVER" => EdgeType.River,
            "CLIFF" => EdgeType.Cliff,
            "URBAN" => EdgeType.Urban,
            _ => EdgeType.Land,
        };

        private static EdgeModifier ModifierOf(string? modifier) => modifier switch
        {
            "HARBOR" => EdgeModifier.Harbor,
            "INDUSTRIAL" => EdgeModifier.Industrial,
            "URBAN" => EdgeModifier.Urban,
            _ => EdgeModifier.None,
        };
    }

    public sealed partial class MapDefinition
    {
        /// <summary>Prompt 33 L2: the edge types, corner pieces and the lines that run on out (view and validators only).</summary>
        public MapEdgesDef Edges { get; internal set; } = MapEdgesDef.None;

        /// <summary>Prompt 33 L2: the entry gates of the ingress contract (Tools/maps/edges.py); empty on a map without them.</summary>
        public IReadOnlyList<EntryGate> EntryGates { get; internal set; } = Array.Empty<EntryGate>();
    }
}
