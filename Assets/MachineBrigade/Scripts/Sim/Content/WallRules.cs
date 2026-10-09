#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Prompt 32 L3: what a wall line of a base is built of (chosen in the loadout, line by line).</summary>
    public enum WallType
    {
        /// <summary>No wall: the quickest way in and out.</summary>
        None,

        /// <summary>Hesco gabions: durability 1.0, the wide gate (the line's own way in barely longer).</summary>
        Hesco,

        /// <summary>Concrete T-walls: durability 1.6, a narrower gate (the T-wall's extra segment closes half of it).</summary>
        TWall,

        /// <summary>A gun wall: durability 1.2, a small tower on it, which takes one of the base's own small slots.</summary>
        GunWall,
    }

    /// <summary>One wall type's numbers (balance.json "base.walls.types").</summary>
    public sealed class WallTypeDef
    {
        public WallType Type { get; internal set; }

        /// <summary>The segment's def (a static obstacle with "wall": true).</summary>
        public string Def { get; internal set; } = "";

        /// <summary>Relative durability (HESCO 1.0): the defs' health is the segment health times this (checked by the tests).</summary>
        public float Durability { get; internal set; } = 1f;

        /// <summary>Whether the line's extra segment (half its gate) is built: the T-wall's narrower gate.</summary>
        public bool Extra { get; internal set; }

        /// <summary>Whether a small tower of the base stands on the segment next to the gate (the gun wall).</summary>
        public bool Gun { get; internal set; }
    }

    /// <summary>
    /// Prompt 32 L3 (DECISIONS "Prompt 32 L3 / L7 / L9"): the base walls ("base.walls"). A base map has up to two wall lines
    /// per camp (ring 1 the outer line, ring 2 the inner one; a siege fortress three, Defend's fall-back lines), each of 3 to
    /// 5 logic segments (map data "walls", Tools/maps/p32_walls.py). A segment is a static obstacle entity on a prebuilt
    /// NavGrid site of two states, INTACT (its ground closed) and RUBBLE (open, 20 % slower to cross); it switches only when
    /// the segment is destroyed, at the next tick. No wall logic runs every tick. No currency of its own.
    /// </summary>
    public sealed class WallRules
    {
        private readonly Dictionary<WallType, WallTypeDef> _types = new();

        /// <summary>A HESCO segment's health (durability 1); the defs carry their type's share of it.</summary>
        public float SegmentHp { get; internal set; } = 2400f;

        /// <summary>The share of speed rubble takes off ground vehicles crossing it (0.2: 20 % slower).</summary>
        public float RubbleSlow { get; internal set; } = 0.2f;

        /// <summary>Lines a camp may have, and a fortress (Defend's three fall-back lines).</summary>
        public int CampLines { get; internal set; } = 2;

        public int FortressLines { get; internal set; } = 3;

        /// <summary>The player's lines when the save names none (the data's default for every line).</summary>
        public WallType Default { get; internal set; } = WallType.Hesco;

        /// <summary>The enemy's wall type by its general's base style (brandt, kessler T-wall; varga gun wall), else "default".</summary>
        private readonly Dictionary<string, WallType> _ai = new(StringComparer.OrdinalIgnoreCase)
        {
            ["brandt"] = WallType.TWall, ["kessler"] = WallType.TWall, ["varga"] = WallType.GunWall, ["default"] = WallType.Hesco,
        };

        public WallRules()
        {
            Add(WallType.Hesco, "wall_hesco", 1f, false, false);
            Add(WallType.TWall, "wall_t", 1.6f, true, false);
            Add(WallType.GunWall, "wall_gun", 1.2f, false, true);
        }

        private void Add(WallType type, string def, float durability, bool extra, bool gun) =>
            _types[type] = new WallTypeDef { Type = type, Def = def, Durability = durability, Extra = extra, Gun = gun };

        /// <summary>A type's numbers (null for <see cref="WallType.None"/>).</summary>
        public WallTypeDef? Of(WallType type) => type != WallType.None && _types.TryGetValue(type, out var t) ? t : null;

        public IEnumerable<WallTypeDef> Types => _types.Values;

        /// <summary>The enemy's type for every line: its general's style's, else the default's.</summary>
        public WallType ForAi(string? style) =>
            style != null && _ai.TryGetValue(style, out var t) ? t : _ai.TryGetValue("default", out var d) ? d : WallType.Hesco;

        /// <summary>The data key of a type ("none", "hesco", "t_wall", "gun_wall").</summary>
        public static string Key(WallType type) => type switch
        {
            WallType.Hesco => "hesco",
            WallType.TWall => "t_wall",
            WallType.GunWall => "gun_wall",
            _ => "none",
        };

        public static bool TryParse(string? key, out WallType type)
        {
            switch ((key ?? "").Trim().ToLowerInvariant())
            {
                case "none": type = WallType.None; return true;
                case "hesco": type = WallType.Hesco; return true;
                case "t_wall": case "twall": type = WallType.TWall; return true;
                case "gun_wall": case "gunwall": type = WallType.GunWall; return true;
                default: type = WallType.None; return false;
            }
        }

        /// <summary>The next type on the Base screen: NONE, HESCO, T-wall, gun wall, round again.</summary>
        public static WallType Next(WallType type) => type switch
        {
            WallType.None => WallType.Hesco,
            WallType.Hesco => WallType.TWall,
            WallType.TWall => WallType.GunWall,
            _ => WallType.None,
        };

        internal static WallRules Parse(JsonObject w)
        {
            var rules = new WallRules
            {
                SegmentHp = Math.Max(1f, w.Float("segmentHp", 2400f)),
                RubbleSlow = Math.Clamp(w.Float("rubbleSlow", 0.2f), 0f, 0.9f),
                CampLines = Math.Clamp(w.Int("campLines", 2), 0, 3),
                FortressLines = Math.Clamp(w.Int("fortressLines", 3), 0, 3),
            };
            if (w.Has("default") && TryParse(w.String("default"), out var def)) rules.Default = def;
            if (w.Has("types"))
            {
                var types = w.Object("types");
                foreach (var key in types.Keys)
                {
                    if (!TryParse(key, out var type) || type == WallType.None) throw new FormatException($"{types.Path}: unknown wall type '{key}'.");
                    var t = types.Object(key);
                    rules.Add(type, t.String("def"), Math.Max(0f, t.Float("durability", 1f)), t.Bool("extra", false), t.Bool("gun", false));
                }
            }
            if (w.Has("ai"))
            {
                var ai = w.Object("ai");
                foreach (var key in ai.Keys)
                    if (TryParse(ai.String(key), out var type)) rules._ai[key] = type;
            }
            return rules;
        }
    }

    /// <summary>One logic segment of a wall line: an axis-aligned block (as NavGrid closes it) facing out of the base.</summary>
    public readonly struct WallSegmentDef
    {
        public WallSegmentDef(Vector2 center, float width, float depth, float facing, bool extra, bool gun)
        {
            Center = center;
            Width = width;
            Depth = depth;
            Facing = facing;
            Extra = extra;
            Gun = gun;
        }

        public Vector2 Center { get; }

        /// <summary>Metres along x and along z (one of them the segment's 12 m, the other its 2 m).</summary>
        public float Width { get; }

        public float Depth { get; }

        /// <summary>Radians: the way out of the base (the segment's front).</summary>
        public float Facing { get; }

        /// <summary>The T-wall's extra segment: half of the gate, built only for a T-wall line.</summary>
        public bool Extra { get; }

        /// <summary>The segment next to the gate: a gun wall's small tower stands on it.</summary>
        public bool Gun { get; }

        /// <summary>The segment's long side (metres).</summary>
        public float Length => MathF.Max(Width, Depth);

        /// <summary>A point this far in front of (positive) or behind (negative) the segment's face.</summary>
        public Vector2 Out(float metres) => Center + Core.SimMath.Forward(Facing) * (MathF.Min(Width, Depth) * global::MachineBrigade.Sim.Content.SimTunables.Bases.WallSegmentDef.OutMinScale + metres);
    }

    /// <summary>A wall line of a camp or a fortress (map data "walls"): its ring, its gate and its segments.</summary>
    public sealed class WallLineDef
    {
        public WallLineDef(string owner, int ring, float radius, Vector2 gate, float gateWidth, IReadOnlyList<WallSegmentDef> segments)
        {
            Owner = owner;
            Ring = ring;
            Radius = radius;
            Gate = gate;
            GateWidth = gateWidth;
            Segments = segments;
        }

        /// <summary>"camp0", "camp1" (a side's camp) or "fortress" (a siege fortress, Defend's lines).</summary>
        public string Owner { get; }

        /// <summary>1 the outer line, 2 the next, 3 a fortress's keep line; the loadout's line index is ring - 1.</summary>
        public int Ring { get; }

        /// <summary>The line's distance from its HQ (Chebyshev, metres): inside it is the base behind the line.</summary>
        public float Radius { get; }

        public Vector2 Gate { get; }
        public float GateWidth { get; }
        public IReadOnlyList<WallSegmentDef> Segments { get; }

        /// <summary>The camp's side, or -1 for a fortress line.</summary>
        public int CampTeam => Owner.StartsWith("camp", StringComparison.Ordinal) && int.TryParse(Owner.Substring(4), out var t) ? t : -1;

        /// <summary>The same line for the other side's camp (a reversed battlefield).</summary>
        internal WallLineDef Swapped() =>
            CampTeam is 0 or 1 ? new WallLineDef("camp" + (1 - CampTeam), Ring, Radius, Gate, GateWidth, Segments) : this;

        internal static List<WallLineDef> ParseAll(JsonObject root)
        {
            var list = new List<WallLineDef>();
            if (!root.Has("walls")) return list;
            foreach (var l in root.Array("walls"))
            {
                var segments = new List<WallSegmentDef>();
                foreach (var s in l.Array("segments"))
                    segments.Add(new WallSegmentDef(new Vector2(s.Float("x"), s.Float("z")), s.Float("w"), s.Float("d"),
                        Core.SimMath.DegToRad(s.Float("facing", 0f)), s.Bool("extra", false), s.Bool("gun", false)));
                var gate = l.Object("gate");
                list.Add(new WallLineDef(l.String("owner"), l.Int("ring", 1), l.Float("radius", 0f), new Vector2(gate.Float("x"), gate.Float("z")),
                    gate.Float("w", 24f), segments));
            }
            return list;
        }
    }

    public sealed partial class VehicleDef
    {
        /// <summary>Prompt 32 L3: a wall segment ("wall": true): an obstacle the wall breakers hit 1.5 times as hard.</summary>
        public bool Wall { get; internal set; }

        /// <summary>Prompt 32 L3: one of the wall breakers ("base.walls.breakers", an elite of one too).</summary>
        public bool WallBreaker { get; internal set; }

        /// <summary>What it does to walls ("base.walls.breakerMultiplier" for a wall breaker, 1 for any other).</summary>
        public float WallBreakerScale { get; internal set; } = 1f;
    }

    public sealed partial class Catalog
    {
        private static void ParseWall(JsonObject v, VehicleDef def) => def.Wall = v.Bool("wall", false);

        /// <summary>Marks the wall breakers (their elites too) once the base rules are read.</summary>
        private void FinishWalls()
        {
            var breakers = new HashSet<string>(Base.WallBreakers, StringComparer.Ordinal);
            foreach (var def in _vehicles.Values)
                def.WallBreaker = breakers.Contains(def.Id) || (def.EliteOf != null && breakers.Contains(def.EliteOf)) ||
                                  (def.BranchOf != null && breakers.Contains(def.BranchOf));
            foreach (var def in _vehicles.Values) def.WallBreakerScale = def.WallBreaker ? Base.WallBreakerMultiplier : 1f;
        }
    }
}
