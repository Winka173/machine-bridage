#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    /// <summary>What a hardpoint takes: a tower (fortification points) or a utility module.</summary>
    public enum HardpointKind
    {
        Tower,
        Utility,
    }

    /// <summary>A hardpoint's size class: small takes light towers, medium light or medium, large any.</summary>
    public enum SlotSize
    {
        Small,
        Medium,
        Large,
    }

    /// <summary>
    /// A fixed spot in a camp (or at an outpost) that can take one tower or module: placed by the
    /// map builder so that no tower in it blocks a road, a gate or a narrow pass.
    /// </summary>
    public readonly struct HardpointDef
    {
        public HardpointDef(Vector2 position, HardpointKind kind, float size, float facing, SlotSize sizeClass = SlotSize.Large, string? place = null)
        {
            Position = position;
            Kind = kind;
            Size = size;
            Facing = facing;
            Class = sizeClass;
            Place = place;
        }

        /// <summary>
        /// Where it stands in a layered base (prompt 17 B.5, map data "place"): "outer_gate", "outer_wall", "yard",
        /// "inner_wall", "hq_side" or "forward" (the forward works' strongpoints); null on a camp, whose places the
        /// game works out from its geometry.
        /// </summary>
        public string? Place { get; }

        /// <summary>A forward works' strongpoint of a layered base: filled from the loadout over again, not counted by the HQ level.</summary>
        public bool Forward => Place == ForwardPlace;

        public const string ForwardPlace = "forward";

        /// <summary>Its size class (what towers it takes).</summary>
        public SlotSize Class { get; }

        /// <summary>Metres across each size class keeps clear of lanes (what a structure in it may cover).</summary>
        public static float Across(SlotSize size) => size switch { SlotSize.Small => 5f, SlotSize.Medium => 6.5f, _ => 9f };

        /// <summary>The class of an old slot given in metres across.</summary>
        public static SlotSize ClassOf(float metres) => metres <= 5.5f ? SlotSize.Small : metres <= 7.5f ? SlotSize.Medium : SlotSize.Large;

        public Vector2 Position { get; }
        public HardpointKind Kind { get; }

        /// <summary>The largest footprint (metres across) a structure in it may have.</summary>
        public float Size { get; }

        /// <summary>Which way a tower in it faces (radians): towards the enemy.</summary>
        public float Facing { get; }
    }

    /// <summary>
    /// A side's camp in the map data: where its headquarters stands (the drop zone is round it) and
    /// its hardpoints, front ones first (the loadout's first towers go there).
    /// </summary>
    public sealed class BaseSiteDef
    {
        public BaseSiteDef(int team, Vector2 hq, float heading, IReadOnlyList<HardpointDef> slots, bool layered = false)
        {
            Team = team;
            Hq = hq;
            Heading = heading;
            Slots = slots;
            Layered = layered;
        }

        /// <summary>A long battlefield's layered base (prompt 17 B): its HQ levels open the long table's slots (balance.json base.longLevels).</summary>
        public bool Layered { get; }

        public int Team { get; }
        public Vector2 Hq { get; }

        /// <summary>Which way the HQ faces (radians).</summary>
        public float Heading { get; }

        public IReadOnlyList<HardpointDef> Slots { get; }

        /// <summary>A slot: its size a class ("small", "medium", "large") or, in older data, metres across.</summary>
        internal static HardpointDef ParseSlot(JsonObject s)
        {
            var kind = s.Has("kind") && s.String("kind").Equals("utility", StringComparison.OrdinalIgnoreCase) ? HardpointKind.Utility : HardpointKind.Tower;
            SlotSize size;
            if (!s.Has("size")) size = SlotSize.Large;
            else if (s.IsString("size")) size = Enum.TryParse<SlotSize>(s.String("size"), true, out var c) ? c : throw new FormatException($"{s.Path}.size: small, medium or large");
            else size = HardpointDef.ClassOf(s.Float("size"));
            return new HardpointDef(new Vector2(s.Float("x"), s.Float("z")), kind, HardpointDef.Across(size), Core.SimMath.DegToRad(s.Float("facing", 0f)), size,
                s.Has("place") ? s.String("place") : null);
        }

        internal static BaseSiteDef Parse(JsonObject b)
        {
            var hq = b.Object("hq");
            var slots = new List<HardpointDef>();
            if (b.Has("slots"))
                foreach (var s in b.Array("slots"))
                    slots.Add(ParseSlot(s));
            return new BaseSiteDef(b.Int("team", 0), new Vector2(hq.Float("x"), hq.Float("z")), Core.SimMath.DegToRad(hq.Float("heading", 0f)), slots);
        }
    }
}
