#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>
    /// The Sandbox's own battlefield (prompt 21 B.1): a flat test range with nothing on it, 300 m across, the two
    /// sides' rallies 160 m apart on the diagonal. The view draws a metre grid over it (every 10 m, heavier every
    /// 50 m) to read ranges and distances off.
    /// </summary>
    public static class SandboxMaps
    {
        public const string FlatId = "sandbox_flat";

        /// <summary>The test range's size, metres.</summary>
        public const float FlatSize = 300f;

        /// <summary>The grid's fine and heavy steps, metres.</summary>
        public const float GridStep = 10f, GridMajor = 50f;

        public static bool IsFlat(string? id) => id == FlatId;

        public static MapDefinition Flat()
        {
            var teams = new[] { new TeamStart(0, new Vector2(-56f, -56f)), new TeamStart(1, new Vector2(56f, 56f)) };
            return new MapDefinition(FlatId, FlatSize, teams, Array.Empty<PropPlacement>(), Array.Empty<UnitPlacement>(), theme: "temperate");
        }
    }
}
