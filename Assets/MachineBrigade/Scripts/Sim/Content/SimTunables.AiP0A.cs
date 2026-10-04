#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// AI MASTER P0-A (lane A, DECISIONS "AI MASTER P0-A"): the targeting and combat-watchdog values of the master spec
    /// (Docs/ai/spec_master, sections 42-47, 88-89, 107 "targeting", Part B B2/B3, Part C, Part H). Own file so the other
    /// P0 lanes (procurement, boss/naval) add theirs without touching these lines. Same rules as every entry: the default
    /// is the spec's value, tunables.json sets it at catalog load, values never change during a battle.
    /// </summary>
    public static partial class SimTunables
    {
        public static partial class Ai
        {
            /// <summary>Spec 42-47, 88-89, 107 "targeting", Part B B2/B3, Part H.</summary>
            public static class Targeting
            {
                /// <summary>ai.targeting.targetStickSeconds (s): the current target's bonus lasts this long after it is acquired (spec 45, 107).</summary>
                public static float TargetStickSeconds = 1.5f;

                /// <summary>ai.targeting.targetStickBonus (share): the current target's score bonus inside the stick window (+15 %, spec 45, 107).</summary>
                public static float TargetStickBonus = 0.15f;

                /// <summary>ai.targeting.overkillShare (x): damage already in flight above this times the target's health makes it overkill (spec 44, 107).</summary>
                public static float OverkillShare = 1.15f;

                /// <summary>ai.targeting.overkillFloor (x): an overkill target keeps this share of its score, so it is taken only when nothing else is (spec 44: "chọn target khác nếu có").</summary>
                public static float OverkillFloor = 0.001f;

                /// <summary>ai.targeting.overkillDangerWorth (CP): a target worth this much (or a boss) is "extremely dangerous" and exempt from overkill control (spec 44).</summary>
                public static float OverkillDangerWorth = 20f;

                /// <summary>ai.targeting.aimTimeConstant (s): AimPenalty = exp(-AimSeconds / this) (spec 89).</summary>
                public static float AimTimeConstant = 4f;

                /// <summary>ai.targeting.maxAimSeconds (s): a target the weapon cannot bear on within this many seconds scores 0 (spec 88).</summary>
                public static float MaxAimSeconds = 10f;

                /// <summary>ai.targeting.threatToSelfWeight (share): spec 46's ThreatToSelf weight (the scale ThreatToObjective is measured against).</summary>
                public static float ThreatToSelfWeight = 0.20f;

                /// <summary>ai.targeting.threatToObjectiveWeight (share): spec 46's ThreatToObjective weight (Part H, mode-aware).</summary>
                public static float ThreatToObjectiveWeight = 0.22f;

                /// <summary>ai.targeting.breachStructureBonus (x): a breacher's bonus on a structure blocking its mission corridor (Part B B2).</summary>
                public static float BreachStructureBonus = 25f;

                /// <summary>ai.targeting.breacherDistraction (x): a breacher's factor on a non-structure that is not an immediate survival threat (Part B B2).</summary>
                public static float BreacherDistraction = 0.5f;

                /// <summary>ai.targeting.siegeTowerBonus (x): a siege platform's factor on an armed defensive structure (Part B B3 ranks 1-2).</summary>
                public static float SiegeTowerBonus = 2f;

                /// <summary>ai.targeting.siegeEngagedTowerBonus (x): on top, a tower that is shooting at the siege platform's side (B3 rank 1).</summary>
                public static float SiegeEngagedTowerBonus = 1.5f;

                /// <summary>ai.targeting.siegeStructureBonus (x): a siege platform's factor on an unarmed structure (B3 ranks 4-5).</summary>
                public static float SiegeStructureBonus = 1.3f;

                /// <summary>ai.targeting.siegeLightPenalty (x): a siege platform's factor on a light target while a valuable structure is in reach (B3 rank 7).</summary>
                public static float SiegeLightPenalty = 0.2f;

                /// <summary>ai.targeting.breachCorridorWidth (m): a structure this close to a breacher's line to its goal blocks its mission corridor (B2).</summary>
                public static float BreachCorridorWidth = 12f;

                /// <summary>ai.targeting.defendBreachReach (m): Defend: an enemy breacher this close to one of our wall lines threatens the gate/wall (Part H).</summary>
                public static float DefendBreachReach = 30f;
            }

            /// <summary>Part C: the combat activity watchdog and the no-idle-armed-unit invariant.</summary>
            public static class CombatWatchdog
            {
                /// <summary>ai.combatWatchdog.evaluateEveryTicks (count): each armed unit is looked at every this many steps (5 at 20 Hz: 4 a second, the tactical rate of spec 3.2).</summary>
                public static int EvaluateEveryTicks = 5;

                /// <summary>ai.combatWatchdog.anomalyGraceSeconds (s): no shot this long beyond the expected aim time with target, solution and a ready weapon is COMBAT_ANOMALY (Part C1: 1.5-2.5 s).</summary>
                public static float AnomalyGraceSeconds = 2f;

                /// <summary>ai.combatWatchdog.idleReasonSeconds (s): an armed unit idle this long must carry a reason code (Part C2).</summary>
                public static float IdleReasonSeconds = 3f;

                /// <summary>ai.combatWatchdog.firedRecentlySeconds (s): a unit that fired within this counts as firing, not idle.</summary>
                public static float FiredRecentlySeconds = 2.5f;

                /// <summary>ai.combatWatchdog.suppressSeconds (s): a target the second recovery gives up is left alone this long (C1 step 6: switch target).</summary>
                public static float SuppressSeconds = 3f;

                /// <summary>ai.combatWatchdog.sidestepMetres (m): the local firing-position correction an AI unit makes (C1 step 5).</summary>
                public static float SidestepMetres = 6f;

                /// <summary>ai.combatWatchdog.explainSeconds (s): an explicit reason an AI layer gives (a hold, a formation wait) lasts this long unless renewed.</summary>
                public static float ExplainSeconds = 2f;
            }
        }

        private static readonly Entry[] AiP0AEntries =
        {
            new Entry("ai.targeting.targetStickSeconds", "s", () => Ai.Targeting.TargetStickSeconds, v => Ai.Targeting.TargetStickSeconds = (float)v),
            new Entry("ai.targeting.targetStickBonus", "share", () => Ai.Targeting.TargetStickBonus, v => Ai.Targeting.TargetStickBonus = (float)v),
            new Entry("ai.targeting.overkillShare", "x", () => Ai.Targeting.OverkillShare, v => Ai.Targeting.OverkillShare = (float)v),
            new Entry("ai.targeting.overkillFloor", "x", () => Ai.Targeting.OverkillFloor, v => Ai.Targeting.OverkillFloor = (float)v),
            new Entry("ai.targeting.overkillDangerWorth", "CP", () => Ai.Targeting.OverkillDangerWorth, v => Ai.Targeting.OverkillDangerWorth = (float)v),
            new Entry("ai.targeting.aimTimeConstant", "s", () => Ai.Targeting.AimTimeConstant, v => Ai.Targeting.AimTimeConstant = (float)v),
            new Entry("ai.targeting.maxAimSeconds", "s", () => Ai.Targeting.MaxAimSeconds, v => Ai.Targeting.MaxAimSeconds = (float)v),
            new Entry("ai.targeting.threatToSelfWeight", "share", () => Ai.Targeting.ThreatToSelfWeight, v => Ai.Targeting.ThreatToSelfWeight = (float)v),
            new Entry("ai.targeting.threatToObjectiveWeight", "share", () => Ai.Targeting.ThreatToObjectiveWeight, v => Ai.Targeting.ThreatToObjectiveWeight = (float)v),
            new Entry("ai.targeting.breachStructureBonus", "x", () => Ai.Targeting.BreachStructureBonus, v => Ai.Targeting.BreachStructureBonus = (float)v),
            new Entry("ai.targeting.breacherDistraction", "x", () => Ai.Targeting.BreacherDistraction, v => Ai.Targeting.BreacherDistraction = (float)v),
            new Entry("ai.targeting.siegeTowerBonus", "x", () => Ai.Targeting.SiegeTowerBonus, v => Ai.Targeting.SiegeTowerBonus = (float)v),
            new Entry("ai.targeting.siegeEngagedTowerBonus", "x", () => Ai.Targeting.SiegeEngagedTowerBonus, v => Ai.Targeting.SiegeEngagedTowerBonus = (float)v),
            new Entry("ai.targeting.siegeStructureBonus", "x", () => Ai.Targeting.SiegeStructureBonus, v => Ai.Targeting.SiegeStructureBonus = (float)v),
            new Entry("ai.targeting.siegeLightPenalty", "x", () => Ai.Targeting.SiegeLightPenalty, v => Ai.Targeting.SiegeLightPenalty = (float)v),
            new Entry("ai.targeting.breachCorridorWidth", "m", () => Ai.Targeting.BreachCorridorWidth, v => Ai.Targeting.BreachCorridorWidth = (float)v),
            new Entry("ai.targeting.defendBreachReach", "m", () => Ai.Targeting.DefendBreachReach, v => Ai.Targeting.DefendBreachReach = (float)v),
            new Entry("ai.combatWatchdog.evaluateEveryTicks", "count", () => Ai.CombatWatchdog.EvaluateEveryTicks, v => Ai.CombatWatchdog.EvaluateEveryTicks = Math.Max(1, (int)Math.Round(v))),
            new Entry("ai.combatWatchdog.anomalyGraceSeconds", "s", () => Ai.CombatWatchdog.AnomalyGraceSeconds, v => Ai.CombatWatchdog.AnomalyGraceSeconds = (float)v),
            new Entry("ai.combatWatchdog.idleReasonSeconds", "s", () => Ai.CombatWatchdog.IdleReasonSeconds, v => Ai.CombatWatchdog.IdleReasonSeconds = (float)v),
            new Entry("ai.combatWatchdog.firedRecentlySeconds", "s", () => Ai.CombatWatchdog.FiredRecentlySeconds, v => Ai.CombatWatchdog.FiredRecentlySeconds = (float)v),
            new Entry("ai.combatWatchdog.suppressSeconds", "s", () => Ai.CombatWatchdog.SuppressSeconds, v => Ai.CombatWatchdog.SuppressSeconds = (float)v),
            new Entry("ai.combatWatchdog.sidestepMetres", "m", () => Ai.CombatWatchdog.SidestepMetres, v => Ai.CombatWatchdog.SidestepMetres = (float)v),
            new Entry("ai.combatWatchdog.explainSeconds", "s", () => Ai.CombatWatchdog.ExplainSeconds, v => Ai.CombatWatchdog.ExplainSeconds = (float)v),
        };
    }
}
