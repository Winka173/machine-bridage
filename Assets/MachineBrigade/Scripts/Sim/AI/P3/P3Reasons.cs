#nullable enable
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P3 (Part O): the reason codes of the coordination lane, written to the DecisionLog as plain lines (like
    /// P2Reasons / CombatReasons; the DecisionLog class is unchanged). Namespaces: OBJECTIVE_*, ROUTE_*, ARTILLERY_*, TARGET_*,
    /// SUPPORT_*, FORMATION_*, SQUAD_*.
    /// </summary>
    public static class P3Reasons
    {
        // Attack packages, staging, scouting, frontage (131, 134-137, 126).
        public const string PackageCreated = "OBJECTIVE_PACKAGE_CREATED";
        public const string PackageAborted = "OBJECTIVE_PACKAGE_ABORTED";
        public const string SyncStage = "OBJECTIVE_SYNC_STAGE";
        public const string SyncGo = "OBJECTIVE_SYNC_GO";
        public const string FixHold = "OBJECTIVE_FIX_ENVELOPE";
        public const string FlankAssigned = "OBJECTIVE_FIX_AND_FLANK";
        public const string ScoutBeforeCommit = "OBJECTIVE_SCOUT_BEFORE_COMMIT";
        public const string ScoutTimeout = "OBJECTIVE_SCOUT_TIMEOUT_COMMIT";
        public const string FrontageSecondRoute = "ROUTE_FRONTAGE_SECOND_ROUTE";
        public const string FrontageStagger = "ROUTE_FRONTAGE_STAGGER_WAVE";

        // Reserve, economy of force, sunk cost, deadlines, depth, counterattack (170-172, 207, 210-212, P2 22).
        public const string ReserveRelease = "OBJECTIVE_RESERVE_RELEASE";
        public const string ReserveKeptWon = "OBJECTIVE_RESERVE_KEPT_FIGHT_WON";
        public const string EconomyOfForce = "OBJECTIVE_ECONOMY_OF_FORCE";
        public const string SunkCostReset = "OBJECTIVE_SUNK_COST_RESET";
        public const string DeadlineSkip = "OBJECTIVE_DEADLINE_SKIP";
        public const string DeadlineFast = "OBJECTIVE_DEADLINE_FAST_UNIT";
        public const string DepthNextLine = "OBJECTIVE_DEPTH_NEXT_LINE";
        public const string DepthRestored = "OBJECTIVE_DEPTH_FORWARD_LINE";
        public const string CounterattackWindow = "OBJECTIVE_COUNTERATTACK_WINDOW";
        public const string TwoObjectiveSplit = "SQUAD_SPLIT_TWO_OBJECTIVES";

        // Routes and memory (127-130).
        public const string RouteDiversity = "ROUTE_DIVERSITY";
        public const string RouteKillZone = "ROUTE_RECENT_LOSSES";
        public const string RouteFailed = "ROUTE_FAILED_REMEMBERED";

        // Artillery (143-145, 213).
        public const string CounterBatteryMission = "ARTILLERY_COUNTERBATTERY_MISSION";
        public const string CounterBatteryStrike = "ARTILLERY_COUNTERBATTERY_AREA_FIRE";
        public const string Scoot = "ARTILLERY_SCOOT";
        public const string CounterBatteryScoot = "ARTILLERY_COUNTERBATTERY_SCOOT";
        public const string FinishMission = "ARTILLERY_FINISH_MISSION";
        public const string StaleTarget = "ARTILLERY_STALE_TARGET_DROPPED";

        // Targeting (139, 146-150, 199-201, 205).
        public const string PursuitAbort = "TARGET_PURSUIT_ABORT_LEASH";
        public const string PursuitIrrelevant = "TARGET_PURSUIT_ABORT_NOT_MISSION";
        public const string Intercept = "TARGET_INTERCEPT_PREDICT";
        public const string Cutoff = "TARGET_CUTOFF_CHOKE";
        public const string FocusFire = "TARGET_FOCUS_FIRE";
        public const string SpreadFire = "TARGET_SPREAD_FIRE";
        public const string Handoff = "TARGET_HANDOFF_SUITABILITY";
        public const string AmbushRange = "TARGET_AMBUSH_OPEN_RANGE";
        public const string AmbushHighValue = "TARGET_AMBUSH_OPEN_HIGH_VALUE";
        public const string AmbushDetected = "TARGET_AMBUSH_DETECTED";
        public const string AmbushSync = "TARGET_AMBUSH_SYNC_VOLLEY";

        // Support (140-142, 169).
        public const string RepairReserved = "SUPPORT_REPAIR_RESERVED";
        public const string SmokeDeconflicted = "SUPPORT_SMOKE_DECONFLICTED";
        public const string SmokePlanned = "SUPPORT_SMOKE_PLANNED";
        public const string CoverageAssigned = "SUPPORT_AA_COVERAGE_ASSIGNED";

        // Formations (213).
        public const string DisperseHold = "FORMATION_DISPERSE_HOLD";

        internal static void Unit(SimWorld world, Vehicle v, DecisionKind kind, string code, string detail = "") =>
            world.AiLog.Add(new DecisionEntry(world.Time, v.Team, AiLayer.Unit, (int)v.Id.Value, kind, detail.Length > 0 ? code + " " + detail : code));

        internal static void Squad(SimWorld world, int team, int squad, DecisionKind kind, string code, string detail = "") =>
            world.AiLog.Add(new DecisionEntry(world.Time, team, AiLayer.Squad, squad, kind, detail.Length > 0 ? code + " " + detail : code));

        internal static void Commander(SimWorld world, int team, DecisionKind kind, string code, string detail = "") =>
            world.AiLog.Add(new DecisionEntry(world.Time, team, AiLayer.Commander, 0, kind, detail.Length > 0 ? code + " " + detail : code));
    }
}
