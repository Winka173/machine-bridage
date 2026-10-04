// AI MASTER lane P0-B (topology, feasibility, procurement): the new values live in Resources/Data/tunables.json under
// "ai" -> "topology" / "feasibility" / "procurement"; these defaults equal the file's.
#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    public static partial class SimTunables
    {
        public static partial class Ai
        {
            public static partial class Topology
            {
                /// <summary>ai.topology.rebuildSeconds (s): the least battle time between rebuilds after the ground changed.</summary>
                public static float RebuildSeconds = 5f;
                /// <summary>ai.topology.chokeWidth (m): open ground this narrow between closed ground is a choke.</summary>
                public static float ChokeWidth = 8f;
                /// <summary>ai.topology.nearestRings (count): cells searched round a point for open ground of a domain.</summary>
                public static int NearestRings = 8;
            }

            public static partial class Feasibility
            {
                /// <summary>ai.feasibility.travelDetour (x): grid steps to metres driven (corners, traffic).</summary>
                public static float TravelDetour = 1.25f;
                /// <summary>ai.feasibility.laneSamples (count): points along a ship's lane its coverage is judged at.</summary>
                public static int LaneSamples = 9;
            }

            public static partial class Procurement
            {
                /// <summary>ai.procurement.blendWeight (points): the master score's weight on top of the legacy buying score.</summary>
                public static float BlendWeight = 3f;
                /// <summary>ai.procurement.weights (x): role deficit, counter need, objective fit, map influence, timing, survivability, synergy, cost, tactic (section 12).</summary>
                public static float[] Weights = { 0.22f, 0.18f, 0.15f, 0.12f, 0.10f, 0.08f, 0.06f, 0.05f, 0.04f };
                /// <summary>ai.procurement.intelEma (share): the observed composition's smoothing (section 15).</summary>
                public static float IntelEma = 0.20f;
                /// <summary>ai.procurement.mismatchConfirmSeconds (s): a counter need must hold this long (section 15).</summary>
                public static float MismatchConfirmSeconds = 4f;
                /// <summary>ai.procurement.mismatchShare (share): the smoothed enemy share of a threat that makes a counter need.</summary>
                public static float MismatchShare = 0.2f;
                /// <summary>ai.procurement.mismatchConfidence (share): the least intel confidence for a counter need.</summary>
                public static float MismatchConfidence = 0.5f;
                /// <summary>ai.procurement.confidenceCp (CP): enemy value seen for full intel confidence.</summary>
                public static float ConfidenceCp = 24f;
                /// <summary>ai.procurement.minPlanCards (count) and maxPlanCards (count): a purchase plan's size (section 16).</summary>
                public static int MinPlanCards = 3;
                public static int MaxPlanCards = 5;
                /// <summary>ai.procurement.planExpireSeconds (s): an unfinished plan is dropped after this.</summary>
                public static float PlanExpireSeconds = 30f;
                /// <summary>ai.procurement.reserveHorizonSeconds (s): income ahead a counter card may be saved for (section 18).</summary>
                public static float ReserveHorizonSeconds = 8f;
                /// <summary>ai.procurement.reserveMaxSeconds (s): the longest a reserve holds.</summary>
                public static float ReserveMaxSeconds = 12f;
                /// <summary>ai.procurement.feedbackCombatSeconds (s), feedbackUtilization (share), feedbackMinModifier (x): section 196.</summary>
                public static float FeedbackCombatSeconds = 20f;
                public static float FeedbackUtilization = 0.15f;
                public static float FeedbackMinModifier = 0.55f;
                /// <summary>ai.procurement.feedbackPoints (points): what the full feedback cut takes off the legacy score.</summary>
                public static float FeedbackPoints = 4f;
                /// <summary>ai.procurement.timingRefSeconds (s): time to value that scores 0 (section 208).</summary>
                public static float TimingRefSeconds = 90f;
                /// <summary>ai.procurement.lateGameSeconds (s): from here fast useful units weigh more.</summary>
                public static float LateGameSeconds = 480f;
                /// <summary>ai.procurement.longTravelSeconds (s) and longTravelMax (share): the long-travel penalty.</summary>
                public static float LongTravelSeconds = 45f;
                public static float LongTravelMax = 0.15f;
                /// <summary>ai.procurement.congestionMax (share): the congestion penalty at its worst (section 17).</summary>
                public static float CongestionMax = 0.2f;
                /// <summary>ai.procurement.redundancyPerCopy (share): each copy already fielded.</summary>
                public static float RedundancyPerCopy = 0.04f;
                /// <summary>ai.procurement.saturation (x): a role this far over its share is saturated (section 197).</summary>
                public static float Saturation = 1.3f;
                /// <summary>ai.procurement.capabilitySeconds (s): how long a lost unit's roles stay short (section 209).</summary>
                public static float CapabilitySeconds = 30f;
                /// <summary>ai.procurement.floors (share): soft floors recon, anti-air, anti-tank (section 198).</summary>
                public static float[] Floors = { 0.05f, 0.08f, 0.10f };
            }
        }

        private static readonly Entry[] AiMasterP0B =
        {
            new Entry("ai.topology.rebuildSeconds", "s", () => Ai.Topology.RebuildSeconds, v => Ai.Topology.RebuildSeconds = (float)v),
            new Entry("ai.topology.chokeWidth", "m", () => Ai.Topology.ChokeWidth, v => Ai.Topology.ChokeWidth = (float)v),
            new Entry("ai.topology.nearestRings", "count", () => Ai.Topology.NearestRings, v => Ai.Topology.NearestRings = (int)Math.Round(v)),
            new Entry("ai.feasibility.travelDetour", "x", () => Ai.Feasibility.TravelDetour, v => Ai.Feasibility.TravelDetour = (float)v),
            new Entry("ai.feasibility.laneSamples", "count", () => Ai.Feasibility.LaneSamples, v => Ai.Feasibility.LaneSamples = (int)Math.Round(v)),
            new Entry("ai.procurement.blendWeight", "points", () => Ai.Procurement.BlendWeight, v => Ai.Procurement.BlendWeight = (float)v),
            Entry.FloatArray("ai.procurement.weights", "x", () => Ai.Procurement.Weights, v => Ai.Procurement.Weights = v),
            new Entry("ai.procurement.intelEma", "share", () => Ai.Procurement.IntelEma, v => Ai.Procurement.IntelEma = (float)v),
            new Entry("ai.procurement.mismatchConfirmSeconds", "s", () => Ai.Procurement.MismatchConfirmSeconds, v => Ai.Procurement.MismatchConfirmSeconds = (float)v),
            new Entry("ai.procurement.mismatchShare", "share", () => Ai.Procurement.MismatchShare, v => Ai.Procurement.MismatchShare = (float)v),
            new Entry("ai.procurement.mismatchConfidence", "share", () => Ai.Procurement.MismatchConfidence, v => Ai.Procurement.MismatchConfidence = (float)v),
            new Entry("ai.procurement.confidenceCp", "CP", () => Ai.Procurement.ConfidenceCp, v => Ai.Procurement.ConfidenceCp = (float)v),
            new Entry("ai.procurement.minPlanCards", "count", () => Ai.Procurement.MinPlanCards, v => Ai.Procurement.MinPlanCards = (int)Math.Round(v)),
            new Entry("ai.procurement.maxPlanCards", "count", () => Ai.Procurement.MaxPlanCards, v => Ai.Procurement.MaxPlanCards = (int)Math.Round(v)),
            new Entry("ai.procurement.planExpireSeconds", "s", () => Ai.Procurement.PlanExpireSeconds, v => Ai.Procurement.PlanExpireSeconds = (float)v),
            new Entry("ai.procurement.reserveHorizonSeconds", "s", () => Ai.Procurement.ReserveHorizonSeconds, v => Ai.Procurement.ReserveHorizonSeconds = (float)v),
            new Entry("ai.procurement.reserveMaxSeconds", "s", () => Ai.Procurement.ReserveMaxSeconds, v => Ai.Procurement.ReserveMaxSeconds = (float)v),
            new Entry("ai.procurement.feedbackCombatSeconds", "s", () => Ai.Procurement.FeedbackCombatSeconds, v => Ai.Procurement.FeedbackCombatSeconds = (float)v),
            new Entry("ai.procurement.feedbackUtilization", "share", () => Ai.Procurement.FeedbackUtilization, v => Ai.Procurement.FeedbackUtilization = (float)v),
            new Entry("ai.procurement.feedbackMinModifier", "x", () => Ai.Procurement.FeedbackMinModifier, v => Ai.Procurement.FeedbackMinModifier = (float)v),
            new Entry("ai.procurement.feedbackPoints", "points", () => Ai.Procurement.FeedbackPoints, v => Ai.Procurement.FeedbackPoints = (float)v),
            new Entry("ai.procurement.timingRefSeconds", "s", () => Ai.Procurement.TimingRefSeconds, v => Ai.Procurement.TimingRefSeconds = (float)v),
            new Entry("ai.procurement.lateGameSeconds", "s", () => Ai.Procurement.LateGameSeconds, v => Ai.Procurement.LateGameSeconds = (float)v),
            new Entry("ai.procurement.longTravelSeconds", "s", () => Ai.Procurement.LongTravelSeconds, v => Ai.Procurement.LongTravelSeconds = (float)v),
            new Entry("ai.procurement.longTravelMax", "share", () => Ai.Procurement.LongTravelMax, v => Ai.Procurement.LongTravelMax = (float)v),
            new Entry("ai.procurement.congestionMax", "share", () => Ai.Procurement.CongestionMax, v => Ai.Procurement.CongestionMax = (float)v),
            new Entry("ai.procurement.redundancyPerCopy", "share", () => Ai.Procurement.RedundancyPerCopy, v => Ai.Procurement.RedundancyPerCopy = (float)v),
            new Entry("ai.procurement.saturation", "x", () => Ai.Procurement.Saturation, v => Ai.Procurement.Saturation = (float)v),
            new Entry("ai.procurement.capabilitySeconds", "s", () => Ai.Procurement.CapabilitySeconds, v => Ai.Procurement.CapabilitySeconds = (float)v),
            Entry.FloatArray("ai.procurement.floors", "share", () => Ai.Procurement.Floors, v => Ai.Procurement.Floors = v),
        };
    }
}
