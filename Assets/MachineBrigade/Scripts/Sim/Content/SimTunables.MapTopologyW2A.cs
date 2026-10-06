// Map / visual / audio master spec, lane W2-A (objective approaches, choke re-measure, AI hooks): the values live in
// Resources/Data/tunables.json under "maps" -> "topology"; these defaults equal the file's. Audit references and AI switches
// only: nothing here is a combat value. The three AI hooks are off (flags false, weight 0) until the owner's playtest.
#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    public static partial class SimTunables
    {
        public static partial class Maps
        {
            public static partial class Topology
            {
                /// <summary>maps.topology.approachAlternatives (count): alternative routes searched into each objective after the cheapest (spec H).</summary>
                public static int ApproachAlternatives = 2;
                /// <summary>maps.topology.approachDistinctShare (share): a route sharing more than this of its cells with a found one is not a new approach.</summary>
                public static float ApproachDistinctShare = 0.5f;
                /// <summary>maps.topology.approachExposurePenalty (m): extra cost of an open cell (no cover within 2 m) for the safest route.</summary>
                public static float ApproachExposurePenalty = 3f;
                /// <summary>maps.topology.approachFlankOffset (share of the map's short side): how far off the primary a flank route runs.</summary>
                public static float ApproachFlankOffset = 0.2f;
                /// <summary>maps.topology.approachFlankBearing (degrees): how far a flank route's arrival bearing turns from the primary's.</summary>
                public static float ApproachFlankBearing = 45f;
                /// <summary>
                /// maps.topology.remeasureStaleChokes (flag): while the AI MASTER topology waits for its rebuild after a wall fell, a
                /// topology choke the rubble opened (its narrowest width now well over the choke's) is dropped at once instead of one
                /// topology rebuild late. Off: W1-A as before.
                /// </summary>
                public static bool RemeasureStaleChokes = true;
                /// <summary>maps.topology.aiBreachPriority (flag): breachers rank wall segments by the breach metadata (spec O). Off: as before.</summary>
                public static bool AiBreachPriority;
                /// <summary>maps.topology.breachObjectiveBonus (m): a segment whose fall opens (or shortens by a quarter) the way to a target ranks this much nearer.</summary>
                public static float BreachObjectiveBonus = 20f;
                /// <summary>maps.topology.breachSavingWeight (x): metres of ranking per metre of path the breach saves (capped at 80 m saved).</summary>
                public static float BreachSavingWeight = 0.25f;
                /// <summary>maps.topology.breachTowerPenalty (m): ranking distance added per defending tower that covers the segment.</summary>
                public static float BreachTowerPenalty = 3f;
                /// <summary>maps.topology.aiStagingCandidate (flag): attack packages also weigh the topology's staging area for their objective (spec I / H). Off: as before.</summary>
                public static bool AiStagingCandidate;
                /// <summary>maps.topology.aiConcealmentWeight (score): fire-support anchors add this times the terrain's concealment (spec P). 0: as before.</summary>
                public static float AiConcealmentWeight;
                /// <summary>maps.topology.telemetryApproaches (flag): the map telemetry also counts approach-route usage (builds the approaches in battle). Off by default.</summary>
                public static bool TelemetryApproaches;
            }
        }

        private static readonly Entry[] MapTopologyW2A =
        {
            new Entry("maps.topology.approachAlternatives", "count", () => Maps.Topology.ApproachAlternatives, v => Maps.Topology.ApproachAlternatives = (int)Math.Round(v)),
            new Entry("maps.topology.approachDistinctShare", "share", () => Maps.Topology.ApproachDistinctShare, v => Maps.Topology.ApproachDistinctShare = (float)v),
            new Entry("maps.topology.approachExposurePenalty", "m", () => Maps.Topology.ApproachExposurePenalty, v => Maps.Topology.ApproachExposurePenalty = (float)v),
            new Entry("maps.topology.approachFlankOffset", "share", () => Maps.Topology.ApproachFlankOffset, v => Maps.Topology.ApproachFlankOffset = (float)v),
            new Entry("maps.topology.approachFlankBearing", "deg", () => Maps.Topology.ApproachFlankBearing, v => Maps.Topology.ApproachFlankBearing = (float)v),
            new Entry("maps.topology.remeasureStaleChokes", "flag", () => Maps.Topology.RemeasureStaleChokes ? 1 : 0, v => Maps.Topology.RemeasureStaleChokes = v >= 0.5, flag: true),
            new Entry("maps.topology.aiBreachPriority", "flag", () => Maps.Topology.AiBreachPriority ? 1 : 0, v => Maps.Topology.AiBreachPriority = v >= 0.5, flag: true),
            new Entry("maps.topology.breachObjectiveBonus", "m", () => Maps.Topology.BreachObjectiveBonus, v => Maps.Topology.BreachObjectiveBonus = (float)v),
            new Entry("maps.topology.breachSavingWeight", "x", () => Maps.Topology.BreachSavingWeight, v => Maps.Topology.BreachSavingWeight = (float)v),
            new Entry("maps.topology.breachTowerPenalty", "m", () => Maps.Topology.BreachTowerPenalty, v => Maps.Topology.BreachTowerPenalty = (float)v),
            new Entry("maps.topology.aiStagingCandidate", "flag", () => Maps.Topology.AiStagingCandidate ? 1 : 0, v => Maps.Topology.AiStagingCandidate = v >= 0.5, flag: true),
            new Entry("maps.topology.aiConcealmentWeight", "score", () => Maps.Topology.AiConcealmentWeight, v => Maps.Topology.AiConcealmentWeight = (float)v),
            new Entry("maps.topology.telemetryApproaches", "flag", () => Maps.Topology.TelemetryApproaches ? 1 : 0, v => Maps.Topology.TelemetryApproaches = v >= 0.5, flag: true),
        };
    }
}
