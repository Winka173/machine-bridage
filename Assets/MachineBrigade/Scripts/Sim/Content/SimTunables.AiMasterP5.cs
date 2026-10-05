// AI MASTER lane P5 (monitoring / optimisation): the new values live in Resources/Data/tunables.json under "ai" -> health /
// ammo / towers / budget; these defaults equal the file's. Spec values where the master spec gives a number (Part K 10-20 s,
// section 98 cells 8-12 m, Part P cadences), the lane's choices elsewhere (DECISIONS "AI MASTER P5 (lane A)").
#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    public static partial class SimTunables
    {
        public static partial class Ai
        {
            /// <summary>Part K: the AI Health Monitor above the unit watchdogs (detects, re-evaluates, logs; never cheats).</summary>
            public static partial class Health
            {
                /// <summary>ai.health.enabled (flag): Part K: the health monitor runs (false: counters only, no recovery).</summary>
                public static bool Enabled = true;
                /// <summary>ai.health.periodS (s): Part K / P: the monitor looks once a second (staggered half a second after the commanders).</summary>
                public static float PeriodS = 1.0f;
                /// <summary>ai.health.squadNoDamageS (s): K1: a squad in contact that has not fired for this long is stalled (spec 10-20 s).</summary>
                public static float SquadNoDamageS = 15.0f;
                /// <summary>ai.health.contactMargin (m): K1: an enemy within the squad's reach plus this is contact (the no-damage clock runs).</summary>
                public static float ContactMargin = 15.0f;
                /// <summary>ai.health.stallS (s): K stalledObjectiveAssignments: a squad with an objective that has not come closer for this long.</summary>
                public static float StallS = 20.0f;
                /// <summary>ai.health.progressM (m): K: metres closer to the objective that count as progress.</summary>
                public static float ProgressM = 5.0f;
                /// <summary>ai.health.arriveRadius (m): K: within this of its objective a squad is there (no stall).</summary>
                public static float ArriveRadius = 15.0f;
                /// <summary>ai.health.recoveryCooldownS (s): K1: one recovery per squad this often (no command spam, spec 185).</summary>
                public static float RecoveryCooldownS = 20.0f;
                /// <summary>ai.health.idleTripShare (share): K1 too many idle armed units: this share of armed AI units idle without a reason trips the audit.</summary>
                public static float IdleTripShare = 0.1f;
                /// <summary>ai.health.blockedTripShare (share): K1 high blocked-unit ratio: this share of moving AI ground units at jam stage 3+ trips the escalation.</summary>
                public static float BlockedTripShare = 0.25f;
                /// <summary>ai.health.blockedMinUnits (count): K1: at least this many blocked units before the ratio counts.</summary>
                public static int BlockedMinUnits = 4;
                /// <summary>ai.health.churnCommitScale (x): K1 excessive churn: a churning squad's commitment times this.</summary>
                public static float ChurnCommitScale = 1.5f;
                /// <summary>ai.health.churnDampS (s): K1: how long the longer commitment lasts.</summary>
                public static float ChurnDampS = 30.0f;
                /// <summary>ai.health.strictAssertions (flag): K1 naval reverse: throw instead of logging (debug / tests only).</summary>
                public static bool StrictAssertions = false;
            }

            /// <summary>Part L: ammo / reload-aware tactics (magazines that reload in place; clips that reload on the move).</summary>
            public static partial class Ammo
            {
                /// <summary>ai.ammo.enabled (flag): Part L: reload-aware squad moves, target keeping and artillery scoots (AI sides).</summary>
                public static bool Enabled = true;
                /// <summary>ai.ammo.nearEmptyShare (share): L: a magazine under this share is near empty (no exposed charge).</summary>
                public static float NearEmptyShare = 0.25f;
                /// <summary>ai.ammo.meaningfulReloadS (s): L: a reload at least this long is meaningful (shorter ones are ignored).</summary>
                public static float MeaningfulReloadS = 2.0f;
                /// <summary>ai.ammo.emergencyUrgency (share): L: objective urgency (P2) at or above this lets a near-empty unit charge anyway.</summary>
                public static float EmergencyUrgency = 0.75f;
                /// <summary>ai.ammo.repositionMinReloadS (s): L: a clip reload with this much left is a window for a short reposition.</summary>
                public static float RepositionMinReloadS = 3.0f;
                /// <summary>ai.ammo.scootMinReloadS (s): L: artillery scoots during a reload with this much left (when the reload runs on the move).</summary>
                public static float ScootMinReloadS = 4.0f;
                /// <summary>ai.ammo.keepTargetWhileReloading (flag): L: a reloading mount keeps its valid target (no re-scoring churn).</summary>
                public static bool KeepTargetWhileReloading = true;
            }

            /// <summary>Part N: tower coordination on top of the tower modes (AI sides).</summary>
            public static partial class Towers
            {
                /// <summary>ai.towers.enabled (flag): Part N: the tower factors (protected zone, AT, anti-artillery, critical override, cross-tower overkill).</summary>
                public static bool Enabled = true;
                /// <summary>ai.towers.protectRadius (m): N: an aircraft within this of the HQ or of a friendly structure it attacks threatens the protected zone.</summary>
                public static float ProtectRadius = 45.0f;
                /// <summary>ai.towers.airThreatWorth (x): N: SAM / AA tower factor on an aircraft threatening the protected zone.</summary>
                public static float AirThreatWorth = 1.6f;
                /// <summary>ai.towers.heavyWorth (x): N: AT tower factor on heavy armour.</summary>
                public static float HeavyWorth = 1.3f;
                /// <summary>ai.towers.artilleryWorth (x): N: artillery-capable tower / drone hangar factor on enemy artillery and support.</summary>
                public static float ArtilleryWorth = 1.4f;
                /// <summary>ai.towers.criticalRadius (m): N: an enemy within this of the HQ or shooting at it is a critical objective threat.</summary>
                public static float CriticalRadius = 20.0f;
                /// <summary>ai.towers.criticalWorth (x): N: factor that lets a critical objective threat override the tower mode (above the 3x of AirFirst / ArtilleryFirst).</summary>
                public static float CriticalWorth = 4.0f;
                /// <summary>ai.towers.overkillShare (x): N: other towers' shots already on a target at this times its health: overkill.</summary>
                public static float OverkillShare = 1.15f;
                /// <summary>ai.towers.overkillFloor (x): N: factor on an overkilled target for a tower not yet on it.</summary>
                public static float OverkillFloor = 0.35f;
            }

            /// <summary>Part P / section 98: update budget (staggered ticks, spatial cells, timing counters).</summary>
            public static partial class Budget
            {
                /// <summary>ai.budget.squadBuckets (count): P: squads think in this many staggered buckets (4 Hz layer tick: each squad at 2 Hz; dodges every tick).</summary>
                public static int SquadBuckets = 2;
                /// <summary>ai.budget.spatialCell (m): 98: the AI spatial index cell (8-12 m).</summary>
                public static float SpatialCell = 10.0f;
                /// <summary>ai.budget.perfCounters (flag): P: per-system timing counters on from the start (the 48v48 harness turns them on itself).</summary>
                public static bool PerfCounters = false;
            }
        }

        private static readonly Entry[] AiMasterP5 =
        {
            new Entry("ai.health.enabled", "flag", () => Ai.Health.Enabled ? 1 : 0, v => Ai.Health.Enabled = v >= 0.5, flag: true),
            new Entry("ai.health.periodS", "s", () => Ai.Health.PeriodS, v => Ai.Health.PeriodS = (float)v),
            new Entry("ai.health.squadNoDamageS", "s", () => Ai.Health.SquadNoDamageS, v => Ai.Health.SquadNoDamageS = (float)v),
            new Entry("ai.health.contactMargin", "m", () => Ai.Health.ContactMargin, v => Ai.Health.ContactMargin = (float)v),
            new Entry("ai.health.stallS", "s", () => Ai.Health.StallS, v => Ai.Health.StallS = (float)v),
            new Entry("ai.health.progressM", "m", () => Ai.Health.ProgressM, v => Ai.Health.ProgressM = (float)v),
            new Entry("ai.health.arriveRadius", "m", () => Ai.Health.ArriveRadius, v => Ai.Health.ArriveRadius = (float)v),
            new Entry("ai.health.recoveryCooldownS", "s", () => Ai.Health.RecoveryCooldownS, v => Ai.Health.RecoveryCooldownS = (float)v),
            new Entry("ai.health.idleTripShare", "share", () => Ai.Health.IdleTripShare, v => Ai.Health.IdleTripShare = (float)v),
            new Entry("ai.health.blockedTripShare", "share", () => Ai.Health.BlockedTripShare, v => Ai.Health.BlockedTripShare = (float)v),
            new Entry("ai.health.blockedMinUnits", "count", () => Ai.Health.BlockedMinUnits, v => Ai.Health.BlockedMinUnits = (int)Math.Round(v)),
            new Entry("ai.health.churnCommitScale", "x", () => Ai.Health.ChurnCommitScale, v => Ai.Health.ChurnCommitScale = (float)v),
            new Entry("ai.health.churnDampS", "s", () => Ai.Health.ChurnDampS, v => Ai.Health.ChurnDampS = (float)v),
            new Entry("ai.health.strictAssertions", "flag", () => Ai.Health.StrictAssertions ? 1 : 0, v => Ai.Health.StrictAssertions = v >= 0.5, flag: true),
            new Entry("ai.ammo.enabled", "flag", () => Ai.Ammo.Enabled ? 1 : 0, v => Ai.Ammo.Enabled = v >= 0.5, flag: true),
            new Entry("ai.ammo.nearEmptyShare", "share", () => Ai.Ammo.NearEmptyShare, v => Ai.Ammo.NearEmptyShare = (float)v),
            new Entry("ai.ammo.meaningfulReloadS", "s", () => Ai.Ammo.MeaningfulReloadS, v => Ai.Ammo.MeaningfulReloadS = (float)v),
            new Entry("ai.ammo.emergencyUrgency", "share", () => Ai.Ammo.EmergencyUrgency, v => Ai.Ammo.EmergencyUrgency = (float)v),
            new Entry("ai.ammo.repositionMinReloadS", "s", () => Ai.Ammo.RepositionMinReloadS, v => Ai.Ammo.RepositionMinReloadS = (float)v),
            new Entry("ai.ammo.scootMinReloadS", "s", () => Ai.Ammo.ScootMinReloadS, v => Ai.Ammo.ScootMinReloadS = (float)v),
            new Entry("ai.ammo.keepTargetWhileReloading", "flag", () => Ai.Ammo.KeepTargetWhileReloading ? 1 : 0, v => Ai.Ammo.KeepTargetWhileReloading = v >= 0.5, flag: true),
            new Entry("ai.towers.enabled", "flag", () => Ai.Towers.Enabled ? 1 : 0, v => Ai.Towers.Enabled = v >= 0.5, flag: true),
            new Entry("ai.towers.protectRadius", "m", () => Ai.Towers.ProtectRadius, v => Ai.Towers.ProtectRadius = (float)v),
            new Entry("ai.towers.airThreatWorth", "x", () => Ai.Towers.AirThreatWorth, v => Ai.Towers.AirThreatWorth = (float)v),
            new Entry("ai.towers.heavyWorth", "x", () => Ai.Towers.HeavyWorth, v => Ai.Towers.HeavyWorth = (float)v),
            new Entry("ai.towers.artilleryWorth", "x", () => Ai.Towers.ArtilleryWorth, v => Ai.Towers.ArtilleryWorth = (float)v),
            new Entry("ai.towers.criticalRadius", "m", () => Ai.Towers.CriticalRadius, v => Ai.Towers.CriticalRadius = (float)v),
            new Entry("ai.towers.criticalWorth", "x", () => Ai.Towers.CriticalWorth, v => Ai.Towers.CriticalWorth = (float)v),
            new Entry("ai.towers.overkillShare", "x", () => Ai.Towers.OverkillShare, v => Ai.Towers.OverkillShare = (float)v),
            new Entry("ai.towers.overkillFloor", "x", () => Ai.Towers.OverkillFloor, v => Ai.Towers.OverkillFloor = (float)v),
            new Entry("ai.budget.squadBuckets", "count", () => Ai.Budget.SquadBuckets, v => Ai.Budget.SquadBuckets = (int)Math.Round(v)),
            new Entry("ai.budget.spatialCell", "m", () => Ai.Budget.SpatialCell, v => Ai.Budget.SpatialCell = (float)v),
            new Entry("ai.budget.perfCounters", "flag", () => Ai.Budget.PerfCounters ? 1 : 0, v => Ai.Budget.PerfCounters = v >= 0.5, flag: true),
        };
    }
}
