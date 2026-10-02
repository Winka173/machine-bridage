#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    public sealed partial class VehicleDef
    {
        /// <summary>
        /// Prompt 32 L1 (DECISIONS "Prompt 32 L0/L1/L2"): a tower card's two rank-7 branches as the data declares them
        /// ("branches", in A/B order); empty for a branch row, a card with <see cref="NoBranch"/> or a def without the field.
        /// </summary>
        public IReadOnlyList<string> DeclaredBranches { get; internal set; } = Array.Empty<string>();

        /// <summary>Prompt 32 L1: a tower card with no rank-7 branch ("noBranch": true).</summary>
        public bool NoBranch { get; internal set; }

        /// <summary>
        /// Prompt 32 L1: what a branch (or a card without branches) does, as a tag ("towerRole"): no two cards share one, and the
        /// two branches of a card never do (the branch rule: they differ in what they do, not only in numbers). Null: none.
        /// </summary>
        public string? Role { get; internal set; }

        /// <summary>
        /// Prompt 32 L2: the CP the balance gives flying this tower back in ("rebuildCp", baseRebuildCP; 0: its size's).
        /// What a side pays is the runtime price (a commander's cut, rounded half up once at the end).
        /// </summary>
        public int BaseRebuildCp { get; internal set; }
    }

    public sealed partial class Catalog
    {
        private static void ParseRoster(JsonObject v, VehicleDef def)
        {
            // A branch row inherits its card's line: its card's branch list and flag are not its own.
            var branch = v.Has("branchOf");
            if (!branch && v.Has("branches")) def.DeclaredBranches = v.StringArray("branches");
            def.NoBranch = !branch && v.Bool("noBranch", false);
            def.Role = v.Has("towerRole") ? v.String("towerRole") : null;
            def.BaseRebuildCp = Math.Max(0, v.Int("rebuildCp", 0));
        }
    }
}
