#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>
    /// The Sandbox's own battlefields (prompt 21 B.1): a flat test range with nothing on it, 300 m across, the two
    /// sides' rallies 160 m apart on the diagonal. The view draws a metre grid over it (every 10 m, heavier every
    /// 50 m) to read ranges and distances off. Play-test 8 A (DECISIONS 22Q): the same range with a sea along its east
    /// side (<see cref="Coast"/>), where ships and the naval bosses can be put on the water.
    /// </summary>
    public static class SandboxMaps
    {
        public const string FlatId = "sandbox_flat";

        /// <summary>Play-test 8 A: the flat test range with a sea along its east side.</summary>
        public const string CoastId = "sandbox_coast";

        /// <summary>The test range's size, metres.</summary>
        public const float FlatSize = 300f;

        /// <summary>The grid's fine and heavy steps, metres.</summary>
        public const float GridStep = 10f, GridMajor = 50f;

        /// <summary>The coastal range's waterline (x, metres from the middle) and the water tiles' size (river water's).</summary>
        public const float Shore = 90f, WaterTile = 4f;

        /// <summary>The coastal range's sea lanes, metres out from the middle (x): near, mid and far (a big ship's lane).</summary>
        public static readonly float[] LaneX = { 106f, 120f, 134f };

        /// <summary>One of the Sandbox's own test ranges (flat, or flat with the sea): the grid, towers anywhere.</summary>
        public static bool IsFlat(string? id) => id == FlatId || id == CoastId;

        /// <summary>The test range of this id (the coastal one, else the plain flat one).</summary>
        public static MapDefinition For(string? id) => id == CoastId ? Coast() : Flat();

        public static MapDefinition Flat()
        {
            var teams = new[] { new TeamStart(0, new Vector2(-56f, -56f)), new TeamStart(1, new Vector2(56f, 56f)) };
            return new MapDefinition(FlatId, FlatSize, teams, Array.Empty<PropPlacement>(), Array.Empty<UnitPlacement>(), theme: "temperate");
        }

        /// <summary>
        /// Play-test 8 A: the flat test range with the sea east of <see cref="Shore"/> (60 m of water, drawn and blocking
        /// ground vehicles like any map's), a straight coast running north to south, three sea lanes (the far one takes the
        /// Leviathan's 86 m hull), two beaches for landing craft, three piers to shoot at ships from, and the fleet's
        /// aircraft coming in over the water.
        /// </summary>
        public static MapDefinition Coast()
        {
            var teams = new[] { new TeamStart(0, new Vector2(-56f, -56f)), new TeamStart(1, new Vector2(56f, 56f)) };
            var water = new List<PropPlacement>();
            var half = FlatSize * 0.5f;
            for (var x = Shore + WaterTile * 0.5f; x < half; x += WaterTile)
                for (var z = -half + WaterTile * 0.5f; z < half; z += WaterTile)
                    water.Add(new PropPlacement("river_water", new Vector2(x, z), 0));
            var lanes = new List<SeaLaneDef>
            {
                new() { Id = "near", W = LaneX[0], Patrol = 110f, End = 146f },
                new() { Id = "mid", W = LaneX[1], Patrol = 104f, End = 146f },
                new() { Id = "far", W = LaneX[2], Patrol = 96f, End = 146f },
            };
            var landings = new List<SeaLandingDef>
            {
                new() { At = new Vector2(Shore + 1f, -40f), Inland = new Vector2(Shore - 20f, -40f) },
                new() { At = new Vector2(Shore + 1f, 40f), Inland = new Vector2(Shore - 20f, 40f) },
            };
            var piers = new[] { new Vector2(Shore - 4f, -60f), new Vector2(Shore - 4f, 0f), new Vector2(Shore - 4f, 60f) };
            // The coast runs north (+u); the sea is out to the east (+w = +x).
            var sea = SeaDef.Straight(new Vector2(0f, 1f), Shore, -half, half, lanes, landings, piers, new Vector2(half - 6f, 0f));
            return new MapDefinition(CoastId, FlatSize, teams, water, Array.Empty<UnitPlacement>(), theme: "temperate") { Sea = sea };
        }
    }
}
