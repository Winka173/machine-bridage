// AI MASTER lane P2 (role / mode intelligence, squads): the new values live in Resources/Data/tunables.json under "ai" ->
// "roleDoctrine" / "modeDoctrine" / "fireSupport" / "position" / "firingLane" / "componentState" / "formation" / "squads";
// these defaults equal the file's. Spec values where the master spec gives a number (sections 20-25, 74, 86, 162, Part I1),
// the lane's choices elsewhere (DECISIONS "AI MASTER P2 (lane C)").
#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    public static partial class SimTunables
    {
        public static partial class Ai
        {
            public static partial class RoleDoctrine
            {
                /// <summary>ai.roleDoctrine.rankTop (x): a role's first target priority (Part B ladders).</summary>
                public static float RankTop = 1.6f;
                /// <summary>ai.roleDoctrine.rankStep (x): each lower rung of the ladder.</summary>
                public static float RankStep = 0.85f;
                /// <summary>ai.roleDoctrine.lastResort (x): "only when no better target" (light for a TD, isolated light for artillery).</summary>
                public static float LastResort = 0.35f;
                /// <summary>ai.roleDoctrine.heavySalvoMinWorth (CP): B8's minimum target value for a heavy salvo weapon.</summary>
                public static float HeavySalvoMinWorth = 4f;
                /// <summary>ai.roleDoctrine.navalSalvoMinAlpha (HP): a ship's main weapon this big a trigger pull is a "big salvo" (naval FINAL 09/10).</summary>
                public static float NavalSalvoMinAlpha = 600f;
                /// <summary>ai.roleDoctrine.navalSalvoMinWorth (CP): a big naval salvo's light / drone target below this is a last resort (naval FINAL 09/10).</summary>
                public static float NavalSalvoMinWorth = 8f;
                /// <summary>ai.roleDoctrine.clusterRadius (m): enemies this close to a target make it a cluster (B8, B11).</summary>
                public static float ClusterRadius = 8f;
            }

            public static partial class ModeDoctrine
            {
                /// <summary>ai.modeDoctrine.mortarBand / artilleryBand / mlrsBand / longBand (share of reach): Part I1's anchor distances.</summary>
                public static float[] MortarBand = { 0.55f, 0.75f };
                public static float[] ArtilleryBand = { 0.65f, 0.85f };
                public static float[] MlrsBand = { 0.75f, 0.90f };
                public static float[] LongBand = { 0.85f, 0.95f };
                /// <summary>ai.modeDoctrine.mortarMaxRange (m): a gun reaching this far or less is a mortar.</summary>
                public static float MortarMaxRange = 60f;
                /// <summary>ai.modeDoctrine.longRangeMin (m): a launcher reaching this far is very-long-range (ballistic).</summary>
                public static float LongRangeMin = 140f;
                /// <summary>ai.modeDoctrine.reserveShare (share): the reserve the commander keeps where the mode allows (spec 24: 15-25 %).</summary>
                public static float[] ReserveShare = { 0.15f, 0.25f };
                /// <summary>ai.modeDoctrine.finalReserveShare (share): Showdown's final / sudden-death reserve (I12 "reduce reserve").</summary>
                public static float FinalReserveShare = 0.05f;
                /// <summary>ai.modeDoctrine.reserveCommitSeconds (s): a committed reserve keeps its new task this long.</summary>
                public static float ReserveCommitSeconds = 20f;
                /// <summary>ai.modeDoctrine.defendLeash (m): how far a no-chase doctrine lets squads leave their anchor.</summary>
                public static float DefendLeash = 35f;
                /// <summary>ai.modeDoctrine.rotateSeconds (s): Endless / Survival pockets rotate after this (I6, I16).</summary>
                public static float RotateSeconds = 60f;
                /// <summary>ai.modeDoctrine.pockets (count): prepared firing pockets in Survival / Endless (I6: 2-3).</summary>
                public static int Pockets = 3;
                /// <summary>ai.modeDoctrine.urgencyFloor (x): spec 70's lerp(1, 0.75, urgency) floor of the attack threshold.</summary>
                public static float UrgencyFloor = 0.75f;
                /// <summary>ai.modeDoctrine.urgencyEndSeconds (s): the last seconds of a timed match raise the urgency.</summary>
                public static float UrgencyEndSeconds = 120f;
                /// <summary>ai.modeDoctrine.missionTargetWeight (x): I23 Destroy: the mission structure for siege / strike / bomber roles.</summary>
                public static float MissionTargetWeight = 2.5f;
                /// <summary>ai.modeDoctrine.offMissionGround (x): I13 / I22: a ground enemy that does not threaten the AA / objective.</summary>
                public static float OffMissionGround = 0.5f;
                /// <summary>ai.modeDoctrine.quietStrikeWorth (CP): I21 recon quiet: heavy strikes only on targets worth this much.</summary>
                public static float QuietStrikeWorth = 12f;
            }

            public static partial class FireSupport
            {
                /// <summary>
                /// ai.fireSupport.weights (x): Part J AnchorScore: objective, approach, front, AA, escape, counter-battery safety
                /// (plus terms), threat, congestion, min-range violation, traffic / spawn blocking (minus terms).
                /// </summary>
                public static float[] Weights = { 1.0f, 0.8f, 0.8f, 0.4f, 0.5f, 0.8f, 1.0f, 0.4f, 2.0f, 1.0f };
                /// <summary>ai.fireSupport.minHoldSeconds (s): an anchor holds at least this long unless an emergency trigger fires.</summary>
                public static float MinHoldSeconds = 8f;
                /// <summary>ai.fireSupport.utilizationSeconds (s): a group that has not fired this long with contact repositions.</summary>
                public static float UtilizationSeconds = 20f;
                /// <summary>ai.fireSupport.bandSlack (share): the band may stretch this much before "range band lost".</summary>
                public static float BandSlack = 0.08f;
                /// <summary>ai.fireSupport.slotSpacing (m): the pieces of one anchor stand this far apart (splash).</summary>
                public static float SlotSpacing = 10f;
                /// <summary>ai.fireSupport.lateralStep (m) and lateralSamples (count each side): the anchor candidates across the axis.</summary>
                public static float LateralStep = 12f;
                public static int LateralSamples = 2;
                /// <summary>ai.fireSupport.hqSeparation (m): I2 MLRS keeps off the HQ / tower cluster.</summary>
                public static float HqSeparation = 15f;
                /// <summary>ai.fireSupport.predictSeconds (s): boss / convoy / quarry look-ahead (I4, I7, I9).</summary>
                public static float PredictSeconds = 6f;
                /// <summary>ai.fireSupport.interceptConfidence (share): I20 artillery uses a predicted route only with this intel confidence.</summary>
                public static float InterceptConfidence = 0.5f;
            }

            public static partial class Position
            {
                /// <summary>
                /// ai.position.weights (x): Part D1 PositionScore: weapon uptime, cover, hull-down, observation, escape route,
                /// friendly support (plus), enemy threat, splash density, congestion, friendly-lane blocking, counter-battery (minus).
                /// </summary>
                public static float[] Weights = { 1.0f, 0.6f, 1.2f, 0.4f, 0.3f, 0.3f, 0.8f, 0.6f, 0.4f, 0.8f, 0.6f };
                /// <summary>ai.position.searchRadius (m): how far from its slot a unit looks for a better firing position.</summary>
                public static float SearchRadius = 8f;
                /// <summary>ai.position.hullDownMin / hullDownMax (m), hullDownConeDeg (deg): low cover in front of the hull.</summary>
                public static float HullDownMin = 1.5f;
                public static float HullDownMax = 7f;
                public static float HullDownConeDeg = 35f;
                /// <summary>ai.position.reserveSeconds (s) and reserveRadius (m): D5 cover reservation.</summary>
                public static float ReserveSeconds = 10f;
                public static float ReserveRadius = 4f;
            }

            public static partial class FiringLane
            {
                /// <summary>ai.firingLane.waitSeconds (s): E2 step 1, a blocker driving through is waited for this long.</summary>
                public static float WaitSeconds = 1f;
                /// <summary>ai.firingLane.sidestepMetres (m): E2 step 2.</summary>
                public static float SidestepMetres = 4f;
                /// <summary>ai.firingLane.slotShiftMetres (m): E2 step 3, the equivalent slot on the same ring round the target.</summary>
                public static float SlotShiftMetres = 9f;
                /// <summary>ai.firingLane.cooldownSeconds (s): a unit moves on to the next E2 step at most this often.</summary>
                public static float CooldownSeconds = 4f;
                /// <summary>ai.firingLane.blockerNudgeMetres (m): E2 step 5, the idle blocker steps aside this far.</summary>
                public static float BlockerNudgeMetres = 3f;
            }

            public static partial class ComponentState
            {
                /// <summary>ai.componentState.engineCrippledShare (share): speed left under this is a crippled engine (F2).</summary>
                public static float EngineCrippledShare = 0.6f;
                /// <summary>ai.componentState.flankPenalty (points): F2, a squad with a crippled member scores a flank lower.</summary>
                public static float FlankPenalty = 15f;
                /// <summary>ai.componentState.holdBonus (points): F2, most of the squad crippled: hold / support score higher.</summary>
                public static float HoldBonus = 8f;
            }

            public static partial class Formation
            {
                /// <summary>ai.formation.commitSeconds (s): Part G minimum commitment of a formation (emergencies override).</summary>
                public static float CommitSeconds = 3f;
                /// <summary>ai.formation.chokeLookahead (m): a choke this far ahead on the squad's way switches it to Travel (86).</summary>
                public static float ChokeLookahead = 40f;
                /// <summary>ai.formation.chokeShare (share): spec 22: required width over this share of the choke splits packets.</summary>
                public static float ChokeShare = 0.75f;
                /// <summary>ai.formation.packetDelay (s): spec 22: packets go 2-4 s apart.</summary>
                public static float PacketDelay = 3f;
                /// <summary>ai.formation.splashPacket (count): spec 162: under splash threat a packet has at most this many.</summary>
                public static int SplashPacket = 3;
                /// <summary>ai.formation.morphSeconds (s): spec 159: a new formation is reached through a halfway slot first.</summary>
                public static float MorphSeconds = 1.5f;
                /// <summary>ai.formation.directAtMaxSpread (m): spec 162: against direct anti-tank fire only, no wider spread than this.</summary>
                public static float DirectAtMaxSpread = 8f;
                /// <summary>ai.formation.rearRow (m): Hold / Spread: the rear row (artillery, SAM, EW, repair) stands this far back.</summary>
                public static float RearRow = 10f;
            }

            public static partial class Squads
            {
                /// <summary>ai.squads.desiredMin / desiredMax (count): spec 20's desired squad size (5-7).</summary>
                public static int DesiredMin = 5;
                public static int DesiredMax = 7;
                /// <summary>ai.squads.mergeShare (share) and mergeDistance (m): spec 21 (strength under 45 % of desired, closer than 35 m).</summary>
                public static float MergeShare = 0.45f;
                public static float MergeDistance = 35f;
                /// <summary>ai.squads.receiveRadius (m): spec 23: a reinforcement joins inside 12-20 m (this value).</summary>
                public static float ReceiveRadius = 16f;
                /// <summary>ai.squads.rendezvousBack (m): the rendezvous lies this far behind the squad's line.</summary>
                public static float RendezvousBack = 15f;
                /// <summary>ai.squads.reinforceReach (m): a new vehicle reinforces a squad of its kind this far away (else forms a squad).</summary>
                public static float ReinforceReach = 150f;
                /// <summary>ai.squads.pendingTimeout (s): a reinforcement not received by then joins where it is.</summary>
                public static float PendingTimeout = 45f;
                /// <summary>ai.squads.cohesionWeights (share): spec 25: member distance, role coverage, route progress.</summary>
                public static float[] CohesionWeights = { 0.45f, 0.30f, 0.25f };
                /// <summary>ai.squads.cohesionRegroup (share) and cohesionSeconds (s): spec 25: regroup under 0.55 for more than 2 s.</summary>
                public static float CohesionRegroup = 0.55f;
                public static float CohesionSeconds = 2f;
                /// <summary>ai.squads.cohesionRecover (share): a regrouping squad goes on once its cohesion is back over this.</summary>
                public static float CohesionRecover = 0.7f;
                /// <summary>ai.squads.supportReach (m): a rear-role member within this of a front member counts as covered.</summary>
                public static float SupportReach = 25f;
                /// <summary>ai.squads.joinPredictSeconds (s): spec 74: futureSquadPos = pos + velocity x clamp(travelTime, 0, 6).</summary>
                public static float JoinPredictSeconds = 6f;
                /// <summary>ai.squads.reassignmentCost (points): spec 72 / 73: what changing a squad's task costs.</summary>
                public static float ReassignmentCost = 10f;
            }
        }

        private static readonly Entry[] AiMasterP2 =
        {
            new Entry("ai.roleDoctrine.rankTop", "x", () => Ai.RoleDoctrine.RankTop, v => Ai.RoleDoctrine.RankTop = (float)v),
            new Entry("ai.roleDoctrine.rankStep", "x", () => Ai.RoleDoctrine.RankStep, v => Ai.RoleDoctrine.RankStep = (float)v),
            new Entry("ai.roleDoctrine.lastResort", "x", () => Ai.RoleDoctrine.LastResort, v => Ai.RoleDoctrine.LastResort = (float)v),
            new Entry("ai.roleDoctrine.heavySalvoMinWorth", "CP", () => Ai.RoleDoctrine.HeavySalvoMinWorth, v => Ai.RoleDoctrine.HeavySalvoMinWorth = (float)v),
            new Entry("ai.roleDoctrine.navalSalvoMinAlpha", "HP", () => Ai.RoleDoctrine.NavalSalvoMinAlpha, v => Ai.RoleDoctrine.NavalSalvoMinAlpha = (float)v),
            new Entry("ai.roleDoctrine.navalSalvoMinWorth", "CP", () => Ai.RoleDoctrine.NavalSalvoMinWorth, v => Ai.RoleDoctrine.NavalSalvoMinWorth = (float)v),
            new Entry("ai.roleDoctrine.clusterRadius", "m", () => Ai.RoleDoctrine.ClusterRadius, v => Ai.RoleDoctrine.ClusterRadius = (float)v),
            Entry.FloatArray("ai.modeDoctrine.mortarBand", "share", () => Ai.ModeDoctrine.MortarBand, v => Ai.ModeDoctrine.MortarBand = v),
            Entry.FloatArray("ai.modeDoctrine.artilleryBand", "share", () => Ai.ModeDoctrine.ArtilleryBand, v => Ai.ModeDoctrine.ArtilleryBand = v),
            Entry.FloatArray("ai.modeDoctrine.mlrsBand", "share", () => Ai.ModeDoctrine.MlrsBand, v => Ai.ModeDoctrine.MlrsBand = v),
            Entry.FloatArray("ai.modeDoctrine.longBand", "share", () => Ai.ModeDoctrine.LongBand, v => Ai.ModeDoctrine.LongBand = v),
            new Entry("ai.modeDoctrine.mortarMaxRange", "m", () => Ai.ModeDoctrine.MortarMaxRange, v => Ai.ModeDoctrine.MortarMaxRange = (float)v),
            new Entry("ai.modeDoctrine.longRangeMin", "m", () => Ai.ModeDoctrine.LongRangeMin, v => Ai.ModeDoctrine.LongRangeMin = (float)v),
            Entry.FloatArray("ai.modeDoctrine.reserveShare", "share", () => Ai.ModeDoctrine.ReserveShare, v => Ai.ModeDoctrine.ReserveShare = v),
            new Entry("ai.modeDoctrine.finalReserveShare", "share", () => Ai.ModeDoctrine.FinalReserveShare, v => Ai.ModeDoctrine.FinalReserveShare = (float)v),
            new Entry("ai.modeDoctrine.reserveCommitSeconds", "s", () => Ai.ModeDoctrine.ReserveCommitSeconds, v => Ai.ModeDoctrine.ReserveCommitSeconds = (float)v),
            new Entry("ai.modeDoctrine.defendLeash", "m", () => Ai.ModeDoctrine.DefendLeash, v => Ai.ModeDoctrine.DefendLeash = (float)v),
            new Entry("ai.modeDoctrine.rotateSeconds", "s", () => Ai.ModeDoctrine.RotateSeconds, v => Ai.ModeDoctrine.RotateSeconds = (float)v),
            new Entry("ai.modeDoctrine.pockets", "count", () => Ai.ModeDoctrine.Pockets, v => Ai.ModeDoctrine.Pockets = (int)Math.Round(v)),
            new Entry("ai.modeDoctrine.urgencyFloor", "x", () => Ai.ModeDoctrine.UrgencyFloor, v => Ai.ModeDoctrine.UrgencyFloor = (float)v),
            new Entry("ai.modeDoctrine.urgencyEndSeconds", "s", () => Ai.ModeDoctrine.UrgencyEndSeconds, v => Ai.ModeDoctrine.UrgencyEndSeconds = (float)v),
            new Entry("ai.modeDoctrine.missionTargetWeight", "x", () => Ai.ModeDoctrine.MissionTargetWeight, v => Ai.ModeDoctrine.MissionTargetWeight = (float)v),
            new Entry("ai.modeDoctrine.offMissionGround", "x", () => Ai.ModeDoctrine.OffMissionGround, v => Ai.ModeDoctrine.OffMissionGround = (float)v),
            new Entry("ai.modeDoctrine.quietStrikeWorth", "CP", () => Ai.ModeDoctrine.QuietStrikeWorth, v => Ai.ModeDoctrine.QuietStrikeWorth = (float)v),
            Entry.FloatArray("ai.fireSupport.weights", "x", () => Ai.FireSupport.Weights, v => Ai.FireSupport.Weights = v),
            new Entry("ai.fireSupport.minHoldSeconds", "s", () => Ai.FireSupport.MinHoldSeconds, v => Ai.FireSupport.MinHoldSeconds = (float)v),
            new Entry("ai.fireSupport.utilizationSeconds", "s", () => Ai.FireSupport.UtilizationSeconds, v => Ai.FireSupport.UtilizationSeconds = (float)v),
            new Entry("ai.fireSupport.bandSlack", "share", () => Ai.FireSupport.BandSlack, v => Ai.FireSupport.BandSlack = (float)v),
            new Entry("ai.fireSupport.slotSpacing", "m", () => Ai.FireSupport.SlotSpacing, v => Ai.FireSupport.SlotSpacing = (float)v),
            new Entry("ai.fireSupport.lateralStep", "m", () => Ai.FireSupport.LateralStep, v => Ai.FireSupport.LateralStep = (float)v),
            new Entry("ai.fireSupport.lateralSamples", "count", () => Ai.FireSupport.LateralSamples, v => Ai.FireSupport.LateralSamples = (int)Math.Round(v)),
            new Entry("ai.fireSupport.hqSeparation", "m", () => Ai.FireSupport.HqSeparation, v => Ai.FireSupport.HqSeparation = (float)v),
            new Entry("ai.fireSupport.predictSeconds", "s", () => Ai.FireSupport.PredictSeconds, v => Ai.FireSupport.PredictSeconds = (float)v),
            new Entry("ai.fireSupport.interceptConfidence", "share", () => Ai.FireSupport.InterceptConfidence, v => Ai.FireSupport.InterceptConfidence = (float)v),
            Entry.FloatArray("ai.position.weights", "x", () => Ai.Position.Weights, v => Ai.Position.Weights = v),
            new Entry("ai.position.searchRadius", "m", () => Ai.Position.SearchRadius, v => Ai.Position.SearchRadius = (float)v),
            new Entry("ai.position.hullDownMin", "m", () => Ai.Position.HullDownMin, v => Ai.Position.HullDownMin = (float)v),
            new Entry("ai.position.hullDownMax", "m", () => Ai.Position.HullDownMax, v => Ai.Position.HullDownMax = (float)v),
            new Entry("ai.position.hullDownConeDeg", "deg", () => Ai.Position.HullDownConeDeg, v => Ai.Position.HullDownConeDeg = (float)v),
            new Entry("ai.position.reserveSeconds", "s", () => Ai.Position.ReserveSeconds, v => Ai.Position.ReserveSeconds = (float)v),
            new Entry("ai.position.reserveRadius", "m", () => Ai.Position.ReserveRadius, v => Ai.Position.ReserveRadius = (float)v),
            new Entry("ai.firingLane.waitSeconds", "s", () => Ai.FiringLane.WaitSeconds, v => Ai.FiringLane.WaitSeconds = (float)v),
            new Entry("ai.firingLane.sidestepMetres", "m", () => Ai.FiringLane.SidestepMetres, v => Ai.FiringLane.SidestepMetres = (float)v),
            new Entry("ai.firingLane.slotShiftMetres", "m", () => Ai.FiringLane.SlotShiftMetres, v => Ai.FiringLane.SlotShiftMetres = (float)v),
            new Entry("ai.firingLane.cooldownSeconds", "s", () => Ai.FiringLane.CooldownSeconds, v => Ai.FiringLane.CooldownSeconds = (float)v),
            new Entry("ai.firingLane.blockerNudgeMetres", "m", () => Ai.FiringLane.BlockerNudgeMetres, v => Ai.FiringLane.BlockerNudgeMetres = (float)v),
            new Entry("ai.componentState.engineCrippledShare", "share", () => Ai.ComponentState.EngineCrippledShare, v => Ai.ComponentState.EngineCrippledShare = (float)v),
            new Entry("ai.componentState.flankPenalty", "points", () => Ai.ComponentState.FlankPenalty, v => Ai.ComponentState.FlankPenalty = (float)v),
            new Entry("ai.componentState.holdBonus", "points", () => Ai.ComponentState.HoldBonus, v => Ai.ComponentState.HoldBonus = (float)v),
            new Entry("ai.formation.commitSeconds", "s", () => Ai.Formation.CommitSeconds, v => Ai.Formation.CommitSeconds = (float)v),
            new Entry("ai.formation.chokeLookahead", "m", () => Ai.Formation.ChokeLookahead, v => Ai.Formation.ChokeLookahead = (float)v),
            new Entry("ai.formation.chokeShare", "share", () => Ai.Formation.ChokeShare, v => Ai.Formation.ChokeShare = (float)v),
            new Entry("ai.formation.packetDelay", "s", () => Ai.Formation.PacketDelay, v => Ai.Formation.PacketDelay = (float)v),
            new Entry("ai.formation.splashPacket", "count", () => Ai.Formation.SplashPacket, v => Ai.Formation.SplashPacket = (int)Math.Round(v)),
            new Entry("ai.formation.morphSeconds", "s", () => Ai.Formation.MorphSeconds, v => Ai.Formation.MorphSeconds = (float)v),
            new Entry("ai.formation.directAtMaxSpread", "m", () => Ai.Formation.DirectAtMaxSpread, v => Ai.Formation.DirectAtMaxSpread = (float)v),
            new Entry("ai.formation.rearRow", "m", () => Ai.Formation.RearRow, v => Ai.Formation.RearRow = (float)v),
            new Entry("ai.squads.desiredMin", "count", () => Ai.Squads.DesiredMin, v => Ai.Squads.DesiredMin = (int)Math.Round(v)),
            new Entry("ai.squads.desiredMax", "count", () => Ai.Squads.DesiredMax, v => Ai.Squads.DesiredMax = (int)Math.Round(v)),
            new Entry("ai.squads.mergeShare", "share", () => Ai.Squads.MergeShare, v => Ai.Squads.MergeShare = (float)v),
            new Entry("ai.squads.mergeDistance", "m", () => Ai.Squads.MergeDistance, v => Ai.Squads.MergeDistance = (float)v),
            new Entry("ai.squads.receiveRadius", "m", () => Ai.Squads.ReceiveRadius, v => Ai.Squads.ReceiveRadius = (float)v),
            new Entry("ai.squads.rendezvousBack", "m", () => Ai.Squads.RendezvousBack, v => Ai.Squads.RendezvousBack = (float)v),
            new Entry("ai.squads.reinforceReach", "m", () => Ai.Squads.ReinforceReach, v => Ai.Squads.ReinforceReach = (float)v),
            new Entry("ai.squads.pendingTimeout", "s", () => Ai.Squads.PendingTimeout, v => Ai.Squads.PendingTimeout = (float)v),
            Entry.FloatArray("ai.squads.cohesionWeights", "share", () => Ai.Squads.CohesionWeights, v => Ai.Squads.CohesionWeights = v),
            new Entry("ai.squads.cohesionRegroup", "share", () => Ai.Squads.CohesionRegroup, v => Ai.Squads.CohesionRegroup = (float)v),
            new Entry("ai.squads.cohesionSeconds", "s", () => Ai.Squads.CohesionSeconds, v => Ai.Squads.CohesionSeconds = (float)v),
            new Entry("ai.squads.cohesionRecover", "share", () => Ai.Squads.CohesionRecover, v => Ai.Squads.CohesionRecover = (float)v),
            new Entry("ai.squads.supportReach", "m", () => Ai.Squads.SupportReach, v => Ai.Squads.SupportReach = (float)v),
            new Entry("ai.squads.joinPredictSeconds", "s", () => Ai.Squads.JoinPredictSeconds, v => Ai.Squads.JoinPredictSeconds = (float)v),
            new Entry("ai.squads.reassignmentCost", "points", () => Ai.Squads.ReassignmentCost, v => Ai.Squads.ReassignmentCost = (float)v),
        };
    }
}
