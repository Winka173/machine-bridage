#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>What comes in at an entry gate (prompt 33 L2): a road's, an open edge's, a rail's, the sea's.</summary>
    public enum EntryGateKind
    {
        Road,
        Edge,
        Rail,
        Sea,
        Air,
    }

    /// <summary>
    /// Prompt 33 L2, the deterministic ingress contract: a place a scripted reinforcement comes into the play area. The real
    /// entity is created at <see cref="Position"/> (its gameplayEntryPosition, open ground joined to the battlefield) on its
    /// entry tick and only exists from then on (targets, collisions, AI, damage, the unit cap, the ground grid). Before it,
    /// the view may draw a stand-in without any logic on <see cref="Path"/> (<see cref="VisualIngressLength"/> metres from
    /// the outer band to the gate), placed by the entry tick it is told: the picture never moves the tick. Map data
    /// "entryGates" (Tools/maps/edges.py); a spawn point with no gate of the data near it gets one made where it stands
    /// (<see cref="Implicit"/>), so every scripted reinforcement has one. Ships and trains keep their own routes (L4, L5).
    /// </summary>
    public sealed class EntryGate
    {
        /// <summary>How far beyond the map's rectangle an implicit gate's approach starts (the widest view's half width + 15 %).</summary>
        public static float OuterLength => global::MachineBrigade.Sim.Content.SimTunables.Maps.EntryGate.OuterLength;

        public EntryGate(string id, EntryGateKind kind, Vector2 position, Vector2 inward, float visualIngressLength, IReadOnlyList<Vector2> path,
            string side = "", bool isImplicit = false)
        {
            Id = id;
            Kind = kind;
            Position = position;
            Inward = inward.LengthSquared() > 1e-6f ? Vector2.Normalize(inward) : Vector2.UnitY;
            VisualIngressLength = MathF.Max(0f, visualIngressLength);
            Path = path;
            Side = side;
            Implicit = isImplicit;
        }

        public string Id { get; }
        public EntryGateKind Kind { get; }

        /// <summary>gameplayEntryPosition: where the real entity is created.</summary>
        public Vector2 Position { get; }

        /// <summary>The way in (a unit vector).</summary>
        public Vector2 Inward { get; }

        /// <summary>The view's approach in metres (the stand-in's road beyond the play area).</summary>
        public float VisualIngressLength { get; }

        /// <summary>The approach from out in the outer band to the gate (its last point is <see cref="Position"/>).</summary>
        public IReadOnlyList<Vector2> Path { get; }

        /// <summary>The side of the map's rectangle it comes in by ("N", "E", "S", "W"; empty for a beach landing).</summary>
        public string Side { get; }

        /// <summary>Made at a spawn point the data has no gate near (its approach runs straight back out over the nearest edge).</summary>
        public bool Implicit { get; }

        /// <summary>A gate made where a spawn point stands: its approach runs back out along -inward past the map's rectangle.</summary>
        public static EntryGate At(MapDefinition map, string id, EntryGateKind kind, Vector2 at, Vector2 inward)
        {
            inward = inward.LengthSquared() > 1e-6f ? Vector2.Normalize(inward) : Vector2.UnitY;
            var back = -inward;
            var tx = MathF.Abs(back.X) > 1e-4f ? ((back.X > 0 ? map.Max.X : map.Min.X) - at.X) / back.X : float.MaxValue;
            var ty = MathF.Abs(back.Y) > 1e-4f ? ((back.Y > 0 ? map.Max.Y : map.Min.Y) - at.Y) / back.Y : float.MaxValue;
            var toEdge = MathF.Max(0f, MathF.Min(tx, ty));
            var edge = at + back * toEdge;
            var path = new[] { edge + back * OuterLength, edge, at };
            return new EntryGate(id, kind, at, inward, toEdge + OuterLength, path, "", true);
        }

        /// <summary>Map data "entryGates": [{"id", "kind", "side", "x", "z", "inX", "inZ", "visualIngressLength", "path": [x, z, ...]}].</summary>
        internal static IReadOnlyList<EntryGate> ParseAll(JsonObject root)
        {
            if (!root.Has("entryGates")) return Array.Empty<EntryGate>();
            var list = new List<EntryGate>();
            foreach (var g in root.Array("entryGates"))
            {
                var at = new Vector2(g.Float("x"), g.Float("z"));
                var path = new List<Vector2>();
                if (g.Has("path"))
                {
                    var flat = g.FloatArray("path");
                    if (flat.Count % 2 != 0) throw new FormatException($"{g.Path}.path: needs x, z pairs.");
                    for (var i = 0; i < flat.Count; i += 2) path.Add(new Vector2(flat[i], flat[i + 1]));
                }
                if (path.Count == 0 || Vector2.DistanceSquared(path[path.Count - 1], at) > 0.01f) path.Add(at);
                list.Add(new EntryGate(g.String("id"), KindOf(g.OptionalString("kind")), at, new Vector2(g.Float("inX", 0f), g.Float("inZ", 1f)),
                    g.Float("visualIngressLength", OuterLength), path, g.OptionalString("side") ?? ""));
            }
            return list;
        }

        private static EntryGateKind KindOf(string? kind) => kind switch
        {
            "road" => EntryGateKind.Road,
            "rail" => EntryGateKind.Rail,
            "sea" => EntryGateKind.Sea,
            "air" => EntryGateKind.Air,
            _ => EntryGateKind.Edge,
        };

        /// <summary>
        /// The map's gate nearest <paramref name="at"/> within <paramref name="reach"/> that takes what comes in at a spawn
        /// point of <paramref name="kind"/> (an edge point: a road's or an edge's; a rail head: a rail's, else a road's or an
        /// edge's; the water: the sea's), or null. Ties go to the earlier gate in the data (deterministic).
        /// </summary>
        public static EntryGate? Nearest(IReadOnlyList<EntryGate> gates, Vector2 at, float reach, SpawnKind kind)
        {
            EntryGate? best = null;
            var bestD = reach * reach;
            for (var pass = 0; pass < 2 && best == null; pass++)
                foreach (var g in gates)
                {
                    if (!Takes(g.Kind, kind, pass)) continue;
                    var d = Vector2.DistanceSquared(g.Position, at);
                    if (d < bestD)
                    {
                        bestD = d;
                        best = g;
                    }
                }
            return best;
        }

        private static bool Takes(EntryGateKind gate, SpawnKind kind, int pass) => kind switch
        {
            SpawnKind.Rail => pass == 0 ? gate == EntryGateKind.Rail : (gate is EntryGateKind.Road or EntryGateKind.Edge),
            SpawnKind.Sea => pass == 0 && gate == EntryGateKind.Sea,
            _ => pass == 0 && (gate is EntryGateKind.Road or EntryGateKind.Edge),
        };
    }
}
