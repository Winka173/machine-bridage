// AI MASTER lane P0-D + P1 (movement / traffic): the new values live in Resources/Data/tunables.json under
// "ai" -> "navigation" / "traffic"; these defaults equal the file's.
#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    public static partial class SimTunables
    {
        public static partial class Ai
        {
            /// <summary>Spec 37-38, 102, 107: the staged jam detector, ORCA-lite steering and the relocation fail-safe.</summary>
            public static partial class Navigation
            {
                /// <summary>ai.navigation.jamStages (flag): the staged jam detector runs (0: the old stuck ladder alone).</summary>
                public static bool JamStages = true;
                /// <summary>ai.navigation.jamSoftS / jamReplanS / jamYieldS / jamCorridorS / jamEmergencyS (s): low-progress time of each stage.</summary>
                public static float JamSoftS = 1.5f;
                public static float JamReplanS = 3f;
                public static float JamYieldS = 5f;
                public static float JamCorridorS = 8f;
                public static float JamEmergencyS = 12f;
                /// <summary>ai.navigation.jamLowSpeedShare (share): slower than this share of its desired speed is low progress.</summary>
                public static float JamLowSpeedShare = 0.25f;
                /// <summary>ai.navigation.jamProgressPerSecond (m/s): route progress below this is low progress.</summary>
                public static float JamProgressPerSecond = 0.25f;
                /// <summary>ai.navigation.jamDecay (x): low-progress time drains this much faster than it builds while it moves again.</summary>
                public static float JamDecay = 2f;
                /// <summary>ai.navigation.jamEvalTicks (steps): the jam detector looks every this many steps (5 = 4 Hz, the tactical tick).</summary>
                public static int JamEvalTicks = 5;
                /// <summary>ai.navigation.localReplanMin / localReplanMax (m): stage 2's local waypoint off the line.</summary>
                public static float LocalReplanMin = 3f;
                public static float LocalReplanMax = 6f;
                /// <summary>ai.navigation.corridorAltMax (x): stage 4 takes a way round only shorter than this times the current one.</summary>
                public static float CorridorAltMax = 1.5f;
                /// <summary>ai.navigation.congestionCost (cost) / congestionRadius (m) / congestionSeconds (s): stage 4's congestion stamp.</summary>
                public static int CongestionCost = 60;
                public static float CongestionRadius = 6f;
                public static float CongestionSeconds = 12f;
                /// <summary>ai.navigation.emergencyReverseM (m): stage 5's short reverse (only a vehicle that may reverse).</summary>
                public static float EmergencyReverseM = 3f;
                /// <summary>ai.navigation.giveUpAfterEmergencyS (s): the route is given up this long into stage 5 (its commander sends it again).</summary>
                public static float GiveUpAfterEmergencyS = 3f;
                /// <summary>ai.navigation.failSafeS (s): no headway this long before the safety net (ghost, then SEVERE_UNSTUCK relocation).</summary>
                public static float FailSafeS = 14f;
                /// <summary>ai.navigation.anomalyAccelS (s): a move order must get the hull going within this (spec 185).</summary>
                public static float AnomalyAccelS = 0.5f;
                /// <summary>ai.navigation.orcaLite (flag), avoidanceHorizonGroundS (s), orcaNeighbours (count): spec 34-35.</summary>
                public static bool OrcaLite = true;
                public static float AvoidanceHorizonGroundS = 1.5f;
                public static float AvoidanceHorizonNavalS = 8f;
                public static int OrcaNeighbours = 10;
                /// <summary>ai.navigation.orcaHighShare / orcaLowShare (share): the avoidance the higher / lower right of way takes.</summary>
                public static float OrcaHighShare = 0.15f;
                public static float OrcaLowShare = 0.85f;
                /// <summary>ai.navigation.passingRelease (x): a pair's passing side is kept until they are this many avoidance radii apart.</summary>
                public static float PassingRelease = 2f;
                /// <summary>ai.navigation.separationPad (m), separationSplash (x), separationColumn (x): spec 87.</summary>
                public static float SeparationPad = 0.5f;
                public static float SeparationSplash = 1.5f;
                public static float SeparationColumn = 0.85f;
                /// <summary>ai.navigation.splashThreat (m): an enemy blast this wide counts as a splash threat for the spacing.</summary>
                public static float SplashThreat = 3f;
                /// <summary>ai.navigation.wreckSettleS (s): a fresh wreck is dear, then a wall (spec 39).</summary>
                public static float WreckSettleS = 1.5f;
                /// <summary>ai.navigation.wreckLookAhead (m): routes this far ahead through a new wreck are planned again at once.</summary>
                public static float WreckLookAhead = 40f;
            }

            /// <summary>Spec 28-33, 40-41, 84-86, 185-190: the TrafficCoordinator, shared squad corridors, passages, spawn exits.</summary>
            public static partial class Traffic
            {
                /// <summary>ai.traffic.enabled (flag): squads use shared corridors and passage reservations.</summary>
                public static bool Enabled = true;
                /// <summary>ai.traffic.priorityHoldS (s): a right of way is held at least this long (spec 32).</summary>
                public static float PriorityHoldS = 2f;
                /// <summary>ai.traffic.reservationSeconds (s): a passage reservation lasts this long unless renewed.</summary>
                public static float ReservationSeconds = 6f;
                /// <summary>ai.traffic.alternateSeconds (s): one way holds a passage at most this long while the other way waits.</summary>
                public static float AlternateSeconds = 8f;
                /// <summary>ai.traffic.preemptMargin (points): a right of way this much higher takes a passage held the other way.</summary>
                public static int PreemptMargin = 20;
                /// <summary>ai.traffic.chokeBatchGapS (s): packets through a choke go this far apart (spec 86, 2-4 s).</summary>
                public static float ChokeBatchGapS = 2.5f;
                /// <summary>ai.traffic.queueSpacing (m) / queueStart (m): queue positions Q1, Q2... before a passage (spec 85).</summary>
                public static float QueueSpacing = 8f;
                public static float QueueStart = 8f;
                /// <summary>ai.traffic.approachM (m): a squad reserves a passage on its corridor this far ahead.</summary>
                public static float ApproachM = 60f;
                /// <summary>ai.traffic.predictWindowS (s) / overload (x): spec 188, arrivals within the window over throughput.</summary>
                public static float PredictWindowS = 5f;
                public static float Overload = 1f;
                /// <summary>ai.traffic.corridorMinMembers (count) / corridorMinDistance (m) / corridorRefreshS (s) / corridorNodes (cells): spec 28-29.</summary>
                public static int CorridorMinMembers = 3;
                public static float CorridorMinDistance = 30f;
                public static float CorridorRefreshS = 8f;
                public static int CorridorNodes = 6000;
                /// <summary>ai.traffic.spawnExitRadius / spawnClearRadius / spawnRallyRadius (m), spawnBlockedS / spawnPriorityS (s): spec 40.</summary>
                public static float SpawnExitRadius = 10f;
                public static float SpawnClearRadius = 16f;
                public static float SpawnRallyRadius = 24f;
                public static float SpawnBlockedS = 2f;
                public static float SpawnPriorityS = 3f;
                /// <summary>ai.traffic.bossCorridorCost (cost) / reservedSpotCost (cost): spec 84's dear cells for routes round them.</summary>
                public static int BossCorridorCost = 200;
                public static int ReservedSpotCost = 120;
                /// <summary>ai.traffic.parkingLeaveM (m) / parkingSplashSpacing (x): spec 41's artillery parking lease.</summary>
                public static float ParkingLeaveM = 5f;
                public static float ParkingSplashSpacing = 1.5f;
                /// <summary>ai.traffic.deadlockTicks (steps): the wait-for graph is checked this often (20 = 1 Hz).</summary>
                public static int DeadlockTicks = 20;
            }
        }

        private static readonly Entry[] AiMasterP1 =
        {
            new Entry("ai.navigation.jamStages", "flag", () => Ai.Navigation.JamStages ? 1 : 0, v => Ai.Navigation.JamStages = v >= 0.5, flag: true),
            new Entry("ai.navigation.jamSoftS", "s", () => Ai.Navigation.JamSoftS, v => Ai.Navigation.JamSoftS = (float)v),
            new Entry("ai.navigation.jamReplanS", "s", () => Ai.Navigation.JamReplanS, v => Ai.Navigation.JamReplanS = (float)v),
            new Entry("ai.navigation.jamYieldS", "s", () => Ai.Navigation.JamYieldS, v => Ai.Navigation.JamYieldS = (float)v),
            new Entry("ai.navigation.jamCorridorS", "s", () => Ai.Navigation.JamCorridorS, v => Ai.Navigation.JamCorridorS = (float)v),
            new Entry("ai.navigation.jamEmergencyS", "s", () => Ai.Navigation.JamEmergencyS, v => Ai.Navigation.JamEmergencyS = (float)v),
            new Entry("ai.navigation.jamLowSpeedShare", "share", () => Ai.Navigation.JamLowSpeedShare, v => Ai.Navigation.JamLowSpeedShare = (float)v),
            new Entry("ai.navigation.jamProgressPerSecond", "m/s", () => Ai.Navigation.JamProgressPerSecond, v => Ai.Navigation.JamProgressPerSecond = (float)v),
            new Entry("ai.navigation.jamDecay", "x", () => Ai.Navigation.JamDecay, v => Ai.Navigation.JamDecay = (float)v),
            new Entry("ai.navigation.jamEvalTicks", "steps", () => Ai.Navigation.JamEvalTicks, v => Ai.Navigation.JamEvalTicks = Math.Max(1, (int)Math.Round(v))),
            new Entry("ai.navigation.localReplanMin", "m", () => Ai.Navigation.LocalReplanMin, v => Ai.Navigation.LocalReplanMin = (float)v),
            new Entry("ai.navigation.localReplanMax", "m", () => Ai.Navigation.LocalReplanMax, v => Ai.Navigation.LocalReplanMax = (float)v),
            new Entry("ai.navigation.corridorAltMax", "x", () => Ai.Navigation.CorridorAltMax, v => Ai.Navigation.CorridorAltMax = (float)v),
            new Entry("ai.navigation.congestionCost", "cost", () => Ai.Navigation.CongestionCost, v => Ai.Navigation.CongestionCost = (int)Math.Round(v)),
            new Entry("ai.navigation.congestionRadius", "m", () => Ai.Navigation.CongestionRadius, v => Ai.Navigation.CongestionRadius = (float)v),
            new Entry("ai.navigation.congestionSeconds", "s", () => Ai.Navigation.CongestionSeconds, v => Ai.Navigation.CongestionSeconds = (float)v),
            new Entry("ai.navigation.emergencyReverseM", "m", () => Ai.Navigation.EmergencyReverseM, v => Ai.Navigation.EmergencyReverseM = (float)v),
            new Entry("ai.navigation.giveUpAfterEmergencyS", "s", () => Ai.Navigation.GiveUpAfterEmergencyS, v => Ai.Navigation.GiveUpAfterEmergencyS = (float)v),
            new Entry("ai.navigation.failSafeS", "s", () => Ai.Navigation.FailSafeS, v => Ai.Navigation.FailSafeS = (float)v),
            new Entry("ai.navigation.anomalyAccelS", "s", () => Ai.Navigation.AnomalyAccelS, v => Ai.Navigation.AnomalyAccelS = (float)v),
            new Entry("ai.navigation.orcaLite", "flag", () => Ai.Navigation.OrcaLite ? 1 : 0, v => Ai.Navigation.OrcaLite = v >= 0.5, flag: true),
            new Entry("ai.navigation.avoidanceHorizonGroundS", "s", () => Ai.Navigation.AvoidanceHorizonGroundS, v => Ai.Navigation.AvoidanceHorizonGroundS = (float)v),
            new Entry("ai.navigation.avoidanceHorizonNavalS", "s", () => Ai.Navigation.AvoidanceHorizonNavalS, v => Ai.Navigation.AvoidanceHorizonNavalS = (float)v),
            new Entry("ai.navigation.orcaNeighbours", "count", () => Ai.Navigation.OrcaNeighbours, v => Ai.Navigation.OrcaNeighbours = Math.Max(1, (int)Math.Round(v))),
            new Entry("ai.navigation.orcaHighShare", "share", () => Ai.Navigation.OrcaHighShare, v => Ai.Navigation.OrcaHighShare = (float)v),
            new Entry("ai.navigation.orcaLowShare", "share", () => Ai.Navigation.OrcaLowShare, v => Ai.Navigation.OrcaLowShare = (float)v),
            new Entry("ai.navigation.passingRelease", "x", () => Ai.Navigation.PassingRelease, v => Ai.Navigation.PassingRelease = (float)v),
            new Entry("ai.navigation.separationPad", "m", () => Ai.Navigation.SeparationPad, v => Ai.Navigation.SeparationPad = (float)v),
            new Entry("ai.navigation.separationSplash", "x", () => Ai.Navigation.SeparationSplash, v => Ai.Navigation.SeparationSplash = (float)v),
            new Entry("ai.navigation.separationColumn", "x", () => Ai.Navigation.SeparationColumn, v => Ai.Navigation.SeparationColumn = (float)v),
            new Entry("ai.navigation.splashThreat", "m", () => Ai.Navigation.SplashThreat, v => Ai.Navigation.SplashThreat = (float)v),
            new Entry("ai.navigation.wreckSettleS", "s", () => Ai.Navigation.WreckSettleS, v => Ai.Navigation.WreckSettleS = (float)v),
            new Entry("ai.navigation.wreckLookAhead", "m", () => Ai.Navigation.WreckLookAhead, v => Ai.Navigation.WreckLookAhead = (float)v),
            new Entry("ai.traffic.enabled", "flag", () => Ai.Traffic.Enabled ? 1 : 0, v => Ai.Traffic.Enabled = v >= 0.5, flag: true),
            new Entry("ai.traffic.priorityHoldS", "s", () => Ai.Traffic.PriorityHoldS, v => Ai.Traffic.PriorityHoldS = (float)v),
            new Entry("ai.traffic.reservationSeconds", "s", () => Ai.Traffic.ReservationSeconds, v => Ai.Traffic.ReservationSeconds = (float)v),
            new Entry("ai.traffic.alternateSeconds", "s", () => Ai.Traffic.AlternateSeconds, v => Ai.Traffic.AlternateSeconds = (float)v),
            new Entry("ai.traffic.preemptMargin", "points", () => Ai.Traffic.PreemptMargin, v => Ai.Traffic.PreemptMargin = (int)Math.Round(v)),
            new Entry("ai.traffic.chokeBatchGapS", "s", () => Ai.Traffic.ChokeBatchGapS, v => Ai.Traffic.ChokeBatchGapS = (float)v),
            new Entry("ai.traffic.queueSpacing", "m", () => Ai.Traffic.QueueSpacing, v => Ai.Traffic.QueueSpacing = (float)v),
            new Entry("ai.traffic.queueStart", "m", () => Ai.Traffic.QueueStart, v => Ai.Traffic.QueueStart = (float)v),
            new Entry("ai.traffic.approachM", "m", () => Ai.Traffic.ApproachM, v => Ai.Traffic.ApproachM = (float)v),
            new Entry("ai.traffic.predictWindowS", "s", () => Ai.Traffic.PredictWindowS, v => Ai.Traffic.PredictWindowS = (float)v),
            new Entry("ai.traffic.overload", "x", () => Ai.Traffic.Overload, v => Ai.Traffic.Overload = (float)v),
            new Entry("ai.traffic.corridorMinMembers", "count", () => Ai.Traffic.CorridorMinMembers, v => Ai.Traffic.CorridorMinMembers = (int)Math.Round(v)),
            new Entry("ai.traffic.corridorMinDistance", "m", () => Ai.Traffic.CorridorMinDistance, v => Ai.Traffic.CorridorMinDistance = (float)v),
            new Entry("ai.traffic.corridorRefreshS", "s", () => Ai.Traffic.CorridorRefreshS, v => Ai.Traffic.CorridorRefreshS = (float)v),
            new Entry("ai.traffic.corridorNodes", "cells", () => Ai.Traffic.CorridorNodes, v => Ai.Traffic.CorridorNodes = (int)Math.Round(v)),
            new Entry("ai.traffic.spawnExitRadius", "m", () => Ai.Traffic.SpawnExitRadius, v => Ai.Traffic.SpawnExitRadius = (float)v),
            new Entry("ai.traffic.spawnClearRadius", "m", () => Ai.Traffic.SpawnClearRadius, v => Ai.Traffic.SpawnClearRadius = (float)v),
            new Entry("ai.traffic.spawnRallyRadius", "m", () => Ai.Traffic.SpawnRallyRadius, v => Ai.Traffic.SpawnRallyRadius = (float)v),
            new Entry("ai.traffic.spawnBlockedS", "s", () => Ai.Traffic.SpawnBlockedS, v => Ai.Traffic.SpawnBlockedS = (float)v),
            new Entry("ai.traffic.spawnPriorityS", "s", () => Ai.Traffic.SpawnPriorityS, v => Ai.Traffic.SpawnPriorityS = (float)v),
            new Entry("ai.traffic.bossCorridorCost", "cost", () => Ai.Traffic.BossCorridorCost, v => Ai.Traffic.BossCorridorCost = (int)Math.Round(v)),
            new Entry("ai.traffic.reservedSpotCost", "cost", () => Ai.Traffic.ReservedSpotCost, v => Ai.Traffic.ReservedSpotCost = (int)Math.Round(v)),
            new Entry("ai.traffic.parkingLeaveM", "m", () => Ai.Traffic.ParkingLeaveM, v => Ai.Traffic.ParkingLeaveM = (float)v),
            new Entry("ai.traffic.parkingSplashSpacing", "x", () => Ai.Traffic.ParkingSplashSpacing, v => Ai.Traffic.ParkingSplashSpacing = (float)v),
            new Entry("ai.traffic.deadlockTicks", "steps", () => Ai.Traffic.DeadlockTicks, v => Ai.Traffic.DeadlockTicks = Math.Max(1, (int)Math.Round(v))),
        };
    }
}
