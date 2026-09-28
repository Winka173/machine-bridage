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

    /// <summary>
    /// A fixed spot in a camp (or at an outpost) that can take one tower or module: placed by the
    /// map builder so that no tower in it blocks a road, a gate or a narrow pass.
    /// </summary>
    public readonly struct HardpointDef
    {
        public HardpointDef(Vector2 position, HardpointKind kind, float size, float facing)
        {
            Position = position;
            Kind = kind;
            Size = size;
            Facing = facing;
        }

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
        public BaseSiteDef(int team, Vector2 hq, float heading, IReadOnlyList<HardpointDef> slots)
        {
            Team = team;
            Hq = hq;
            Heading = heading;
            Slots = slots;
        }

        public int Team { get; }
        public Vector2 Hq { get; }

        /// <summary>Which way the HQ faces (radians).</summary>
        public float Heading { get; }

        public IReadOnlyList<HardpointDef> Slots { get; }

        internal static HardpointDef ParseSlot(JsonObject s) =>
            new(new Vector2(s.Float("x"), s.Float("z")),
                s.Has("kind") && s.String("kind").Equals("utility", StringComparison.OrdinalIgnoreCase) ? HardpointKind.Utility : HardpointKind.Tower,
                s.Float("size", 8f), Core.SimMath.DegToRad(s.Float("facing", 0f)));

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
