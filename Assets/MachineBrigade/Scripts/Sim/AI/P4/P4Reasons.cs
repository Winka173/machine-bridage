#nullable enable
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P4 (Part O): the reason codes of the advanced planning lane, written to the DecisionLog as plain lines (like
    /// P3Reasons). Namespaces: OBJECTIVE_*, ROUTE_*, AIR_*, BOSS_*, ARTILLERY_*, PURCHASE_*, SQUAD_*, TARGET_*.
    /// </summary>
    public static class P4Reasons
    {
        // Forecast and plans (152-155, 158, 182-184).
        public const string PlanChosen = "OBJECTIVE_PLAN_CHOSEN";
        public const string PlanKept = "OBJECTIVE_PLAN_KEPT_COMMITMENT";
        public const string PlanHold = "OBJECTIVE_PLAN_FORECAST_HOLD";
        public const string PlanRepeatPenalty = "OBJECTIVE_PLAN_REPEAT_PENALTY";
        public const string PlanFailed = "OBJECTIVE_PLAN_FAILED_REMEMBERED";
        public const string PlanSucceeded = "OBJECTIVE_PLAN_SUCCEEDED";
        public const string Replan = "OBJECTIVE_PLAN_INTERRUPT_REPLAN";
        public const string AbortPrefix = "OBJECTIVE_PACKAGE_ABORT_";
        public const string AbortMainLost = "OBJECTIVE_PACKAGE_ABORT_MAIN_LOST";
        public const string AbortFlankBlocked = "OBJECTIVE_PACKAGE_ABORT_FLANK_BLOCKED";
        public const string AbortSupportFailed = "OBJECTIVE_PACKAGE_ABORT_SUPPORT_FAILED";
        public const string DepRoute = "OBJECTIVE_PACKAGE_ABORT_ROUTE_INVALIDATED";
        public const string DepObjective = "OBJECTIVE_PACKAGE_ABORT_OBJECTIVE_CHANGED";
        public const string DepEnemyRise = "OBJECTIVE_PACKAGE_ABORT_ENEMY_ESTIMATE_ROSE";
        public const string DepCluster = "OBJECTIVE_PACKAGE_ABORT_TARGET_CLUSTER_MOVED";
        public const string DepSupport = "OBJECTIVE_PACKAGE_ABORT_SUPPORT_LOST";
        public const string ReserveForecast = "OBJECTIVE_RESERVE_FORECAST_COLLAPSE";
        public const string SupportForecast = "SUPPORT_FORECAST_BARRAGE";

        // Opportunity windows, probe, feint (132-133, 156).
        public const string Opportunity = "OBJECTIVE_OPPORTUNITY_WINDOW";
        public const string ProbeSent = "OBJECTIVE_PROBE_SENT";
        public const string ProbeExploit = "OBJECTIVE_PROBE_EXPLOIT_WINDOW";
        public const string ProbeThreat = "OBJECTIVE_PROBE_THREAT_FOUND";
        public const string ProbeBlocked = "ROUTE_PROBE_LANE_BLOCKED";
        public const string ProbeInconclusive = "OBJECTIVE_PROBE_INCONCLUSIVE";
        public const string FeintSent = "OBJECTIVE_FEINT_SENT";
        public const string FeintSuccess = "OBJECTIVE_FEINT_REDEPLOY_SEEN";
        public const string FeintEnded = "OBJECTIVE_FEINT_ENDED_NO_REDEPLOY";
        public const string FeintRejected = "OBJECTIVE_FEINT_NO_TACTICAL_UTILITY";

        // Same-match adaptation (157, Part M).
        public const string AdaptBait = "TARGET_ADAPT_BAIT_LEASH";
        public const string AdaptRecon = "OBJECTIVE_ADAPT_MORE_RECON";
        public const string AdaptCounterBattery = "ARTILLERY_ADAPT_CAMPING_COUNTERBATTERY";
        public const string AdaptUtilization = "PURCHASE_ADAPT_LOW_UTILIZATION";
        public const string AdaptAir = "PURCHASE_ADAPT_AIR_HEAVY";
        public const string AdaptTowers = "PURCHASE_ADAPT_TOWER_PATTERN";

        // Procurement (P0-B open items).
        public const string BuyEnough = "PURCHASE_HOLD_FORCE_ENOUGH";
        public const string BuyBossPhase = "PURCHASE_RESERVE_BOSS_PHASE";

        // Air (174-178).
        public const string SeadHold = "AIR_SEAD_HOLD_INGRESS";
        public const string SeadGo = "AIR_SEAD_WINDOW_STRIKE";
        public const string SeadReroute = "AIR_SEAD_FAILED_REROUTE";
        public const string SeadDelay = "AIR_SEAD_FAILED_DELAY";
        public const string RiskRoute = "AIR_RISK_ROUTE";
        public const string Egress = "AIR_EGRESS_LOW_RISK";
        public const string CapReturn = "AIR_CAP_RETURN_ZONE";
        public const string CapPatrol = "AIR_CAP_PATROL";
        public const string Handoff = "AIR_TARGET_HANDOFF";
        public const string AirIntercept = "AIR_INTERCEPT_PREDICT";
        public const string BomberWait = "AIR_BOMBER_WAIT";
        public const string BomberGo = "AIR_BOMBER_GO";
        public const string BomberRetarget = "AIR_BOMBER_RETARGET";

        // Bosses (179-181, 204, 214).
        public const string Weakpoint = "BOSS_WEAKPOINT_UTILITY";
        public const string EscapeSector = "BOSS_TELEGRAPH_ESCAPE_SECTOR";
        public const string PatternLearnt = "BOSS_PATTERN_LEARNT";
        public const string PressureDefer = "BOSS_PRESSURE_BUDGET_DEFER";

        // Artillery ownership (P3 leftover a).
        public const string GunOwned = "ARTILLERY_ORDER_OWNER";

        // Cues (215).
        public const string Cue = "SQUAD_CUE";

        internal static void Unit(SimWorld world, Vehicle v, DecisionKind kind, string code, string detail = "") =>
            world.AiLog.Add(new DecisionEntry(world.Time, v.Team, AiLayer.Unit, (int)v.Id.Value, kind, detail.Length > 0 ? code + " " + detail : code));

        internal static void Squad(SimWorld world, int team, int squad, DecisionKind kind, string code, string detail = "") =>
            world.AiLog.Add(new DecisionEntry(world.Time, team, AiLayer.Squad, squad, kind, detail.Length > 0 ? code + " " + detail : code));

        internal static void Commander(SimWorld world, int team, DecisionKind kind, string code, string detail = "") =>
            world.AiLog.Add(new DecisionEntry(world.Time, team, AiLayer.Commander, 0, kind, detail.Length > 0 ? code + " " + detail : code));
    }
}
