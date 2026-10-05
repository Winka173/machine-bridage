#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.AI
{
    /// <summary>One registered reason code (Part O): the code, its namespace, the lane that writes it, an alias (an older line verb or score-factor key that means the same), and what it says.</summary>
    public readonly struct ReasonCode
    {
        public ReasonCode(string code, string ns, string lane, string meaning, string alias = "")
        {
            Code = code;
            Namespace = ns;
            Lane = lane;
            Meaning = meaning;
            Alias = alias;
        }

        public string Code { get; }
        public string Namespace { get; }
        public string Lane { get; }
        public string Meaning { get; }
        public string Alias { get; }

        public override string ToString() => Code;
    }

    /// <summary>
    /// AI MASTER P5 (Part O): the one registry of every reason code the AI lanes write to the <see cref="DecisionLog"/> (the
    /// per-lane constant classes CombatReasons, P2Reasons, P3Reasons, P4Reasons and P5Reasons stay the writers' names; this table
    /// is what the tests check them against and what the export pack lists, Tools/export/domains/_p5_ai.py). A line's code is
    /// its first word; the purchase lines keep section 94's verbs (BUY / REJECT / PLAN / RESERVE, registered as aliases) and
    /// prompt 28 J.4's plain lines (objective, tactic, action switches) carry no code. Writing a code never feeds back.
    /// </summary>
    public static class ReasonCodes
    {
        /// <summary>Part O's minimum namespaces.</summary>
        public static readonly string[] Namespaces =
        {
            "PURCHASE", "TARGET", "POSITION", "ROUTE", "TRAFFIC", "JAM", "COMBAT_IDLE", "FORMATION", "MODE", "BOSS", "NAVAL", "SUPPORT",
            "AIR", "ARTILLERY", "OBJECTIVE", "WATCHDOG",
        };

        /// <summary>Namespaces the lanes added beyond Part O's minimum (squad lifecycle, component-state roles, combat activity).</summary>
        public static readonly string[] ExtraNamespaces = { "SQUAD", "ROLE", "COMBAT" };

        /// <summary>Part O's example codes (every one is registered and written by some lane).</summary>
        public static readonly string[] SpecExamples =
        {
            "PURCHASE_NO_MAP_INFLUENCE", "PURCHASE_ROLE_SATURATED", "TARGET_NO_FIRING_SOLUTION", "TARGET_WRONG_WEAPON_DOMAIN",
            "POSITION_FRIENDLY_BLOCK", "JAM_CHOKE_QUEUE", "COMBAT_IDLE_STALE_AIM", "MODE_DEFEND_NO_CHASE", "BOSS_HULL_ROUTE_OWNS_HEADING",
            "NAVAL_REVERSE_FORBIDDEN", "ARTILLERY_COUNTERBATTERY_SCOOT", "WATCHDOG_SQUAD_ZERO_UTILIZATION",
        };

        public static readonly ReasonCode[] All =
        {
            // ---------------------------------------------------------------- PURCHASE (P0-B, P4)
            new ReasonCode("PURCHASE_BUY", "PURCHASE", "P0B", "a card bought: score, plan, top plus / minus factors, runner-up (section 94)", "BUY"),
            new ReasonCode("PURCHASE_REJECT", "PURCHASE", "P0B", "a card rejected before scoring, with its PURCHASE_* reason (section 94)", "REJECT"),
            new ReasonCode("PURCHASE_PLAN", "PURCHASE", "P0B", "a purchase plan made or cancelled (section 16)", "PLAN"),
            new ReasonCode("PURCHASE_RESERVE", "PURCHASE", "P0B", "CP held back for a counter card (section 17)", "RESERVE"),
            new ReasonCode("PURCHASE_NO_MAP_INFLUENCE", "PURCHASE", "P0B", "the card cannot reach or shoot any objective or enemy on this map"),
            new ReasonCode("PURCHASE_DEPLOYMENT_UNREACHABLE", "PURCHASE", "P0B", "no deployment point from which the card reaches the fight"),
            new ReasonCode("PURCHASE_ROLE_SATURATED", "PURCHASE", "P0B", "the card's role is above its share (BUY factor)", "role-saturated"),
            new ReasonCode("PURCHASE_ADAPT_LOW_UTILIZATION", "PURCHASE", "P4", "a class that cannot hit what is in reach buys less (same match)"),
            new ReasonCode("PURCHASE_ADAPT_AIR_HEAVY", "PURCHASE", "P4", "the enemy fields many aircraft: more anti-air"),
            new ReasonCode("PURCHASE_ADAPT_TOWER_PATTERN", "PURCHASE", "P4", "the enemy relies on towers: more siege / breach"),
            new ReasonCode("PURCHASE_HOLD_FORCE_ENOUGH", "PURCHASE", "P4", "the forecast says the force is enough: CP held"),
            new ReasonCode("PURCHASE_RESERVE_BOSS_PHASE", "PURCHASE", "P4", "CP held for a seen boss near its phase change"),

            // ---------------------------------------------------------------- TARGET (P0-A, P2, P3, P4)
            new ReasonCode("TARGET_OK", "TARGET", "P0A", "the candidate passes the hard feasibility filter"),
            new ReasonCode("TARGET_INVALID", "TARGET", "P0A", "dead, untargetable, truce or ceasefire"),
            new ReasonCode("TARGET_WRONG_WEAPON_DOMAIN", "TARGET", "P0A", "the weapon cannot hit that layer / domain"),
            new ReasonCode("TARGET_NOT_VISIBLE", "TARGET", "P0A", "not seen by the side (fog)"),
            new ReasonCode("TARGET_OUT_OF_REACH", "TARGET", "P0A", "beyond the weapon's reach"),
            new ReasonCode("TARGET_MIN_RANGE", "TARGET", "P0A", "inside the weapon's minimum range"),
            new ReasonCode("TARGET_NO_FIRING_SOLUTION", "TARGET", "P0A", "no line of fire"),
            new ReasonCode("TARGET_OUTSIDE_ARC", "TARGET", "P0A", "outside every mount's arc and the hull cannot turn"),
            new ReasonCode("TARGET_AIM_TOO_LONG", "TARGET", "P0A", "the aim would take longer than the cut"),
            new ReasonCode("TARGET_UNREACHABLE", "TARGET", "P0A", "no reachable firing position"),
            new ReasonCode("TARGET_UNREACHABLE_DROPPED", "TARGET", "P0A", "an unreachable target dropped (no chase)"),
            new ReasonCode("TARGET_OVERKILL_SPREAD", "TARGET", "P0A", "enough damage already on it: another target"),
            new ReasonCode("TARGET_BREACH_HELD", "TARGET", "P0A", "a breacher keeps its wall against a non-threat"),
            new ReasonCode("TARGET_BREACH_FIRST", "TARGET", "P0A", "the wall in front of the target first"),
            new ReasonCode("TARGET_SWITCH_FRIENDLY_BLOCK", "TARGET", "P2", "a friend blocks the shot: another target"),
            new ReasonCode("TARGET_PURSUIT_ABORT_LEASH", "TARGET", "P3", "the pursuit passed its leash"),
            new ReasonCode("TARGET_PURSUIT_ABORT_NOT_MISSION", "TARGET", "P3", "the fleeing target is not worth the mission"),
            new ReasonCode("TARGET_INTERCEPT_PREDICT", "TARGET", "P3", "intercept at the predicted point"),
            new ReasonCode("TARGET_CUTOFF_CHOKE", "TARGET", "P3", "cut off at the choke instead of chasing"),
            new ReasonCode("TARGET_FOCUS_FIRE", "TARGET", "P3", "squad focus fire (threat, near kill, boss, high value)"),
            new ReasonCode("TARGET_SPREAD_FIRE", "TARGET", "P3", "fire spread over targets"),
            new ReasonCode("TARGET_HANDOFF_SUITABILITY", "TARGET", "P3", "the target handed to the better-suited shooter"),
            new ReasonCode("TARGET_AMBUSH_OPEN_RANGE", "TARGET", "P3", "ambush opens: the enemy at the kill range"),
            new ReasonCode("TARGET_AMBUSH_OPEN_HIGH_VALUE", "TARGET", "P3", "ambush opens on a high-value target"),
            new ReasonCode("TARGET_AMBUSH_DETECTED", "TARGET", "P3", "ambush opens: spotted"),
            new ReasonCode("TARGET_AMBUSH_SYNC_VOLLEY", "TARGET", "P3", "ambush opens in one volley"),
            new ReasonCode("TARGET_ADAPT_BAIT_LEASH", "TARGET", "P4", "a baited lane: shorter pursuit leash"),
            new ReasonCode("TARGET_KEEP_WHILE_RELOADING", "TARGET", "P5", "a reloading mount keeps its valid target (Part L; counted, not logged per shot)"),

            // ---------------------------------------------------------------- POSITION (P0-A, P2, P5)
            new ReasonCode("POSITION_TRANSIT_FALLBACK", "POSITION", "P0A", "a firing spot on a route (map data to fix)"),
            new ReasonCode("POSITION_HULL_DOWN", "POSITION", "P2", "hull-down position chosen"),
            new ReasonCode("POSITION_COVER_RESERVED", "POSITION", "P2", "cover spot reserved"),
            new ReasonCode("POSITION_FRIENDLY_BLOCK", "POSITION", "P2", "a friend blocks the firing lane"),
            new ReasonCode("POSITION_FRIENDLY_BLOCK_WAIT", "POSITION", "P2", "blocked lane: wait a moment"),
            new ReasonCode("POSITION_FRIENDLY_BLOCK_SIDESTEP", "POSITION", "P2", "blocked lane: side-step"),
            new ReasonCode("POSITION_FRIENDLY_BLOCK_ALT_SLOT", "POSITION", "P2", "blocked lane: another slot"),
            new ReasonCode("POSITION_FRIENDLY_BLOCKER_YIELD", "POSITION", "P2", "the blocker steps aside"),
            new ReasonCode("POSITION_RELOAD_HOLD", "POSITION", "P5", "a reloading (near-empty) unit holds instead of an exposed advance (Part L)"),
            new ReasonCode("POSITION_RELOAD_RESUME", "POSITION", "P5", "reloaded (or an emergency): the held unit rejoins the squad's move"),

            // ---------------------------------------------------------------- ROUTE (P1, P3, P4)
            new ReasonCode("ROUTE_ALT_CONGESTION", "ROUTE", "P1", "predicted congestion: a way round"),
            new ReasonCode("ROUTE_WRECK_REPLAN", "ROUTE", "P1", "a wreck on the path: replanned"),
            new ReasonCode("ROUTE_FRONTAGE_SECOND_ROUTE", "ROUTE", "P3", "frontage overflow: a second route"),
            new ReasonCode("ROUTE_FRONTAGE_STAGGER_WAVE", "ROUTE", "P3", "frontage overflow: a later wave"),
            new ReasonCode("ROUTE_DIVERSITY", "ROUTE", "P3", "route diversity: a different lane"),
            new ReasonCode("ROUTE_RECENT_LOSSES", "ROUTE", "P3", "recent deaths on the route: avoided"),
            new ReasonCode("ROUTE_FAILED_REMEMBERED", "ROUTE", "P3", "a failed route remembered"),
            new ReasonCode("ROUTE_PROBE_LANE_BLOCKED", "ROUTE", "P4", "the probe found the lane blocked"),

            // ---------------------------------------------------------------- TRAFFIC (P1)
            new ReasonCode("TRAFFIC_GRANT", "TRAFFIC", "P1", "passage granted"),
            new ReasonCode("TRAFFIC_PREEMPT", "TRAFFIC", "P1", "passage taken by a higher priority"),
            new ReasonCode("TRAFFIC_QUEUE_TIMEOUT", "TRAFFIC", "P1", "queue waited too long"),
            new ReasonCode("TRAFFIC_SPAWN_EXIT_CLEAR", "TRAFFIC", "P1", "a fresh unit cleared the spawn exit"),
            new ReasonCode("TRAFFIC_DEADLOCK_CYCLE", "TRAFFIC", "P1", "wait-for cycle broken"),

            // ---------------------------------------------------------------- JAM (P1)
            new ReasonCode("JAM_NONE", "JAM", "P1", "no jam"),
            new ReasonCode("JAM_SOFT", "JAM", "P1", "stage 1 soft jam"),
            new ReasonCode("JAM_SOFT_SIDESTEP", "JAM", "P1", "stage 1: deterministic side-step"),
            new ReasonCode("JAM_LOCAL_REPLAN", "JAM", "P1", "stage 2 local replan"),
            new ReasonCode("JAM_YIELD", "JAM", "P1", "stage 3 yield by priority"),
            new ReasonCode("JAM_YIELD_NO_FRIEND", "JAM", "P1", "stage 3: no friend to yield to"),
            new ReasonCode("JAM_YIELD_GATHERING", "JAM", "P1", "stage 3: the squad is gathering"),
            new ReasonCode("JAM_YIELD_BOSSES", "JAM", "P1", "stage 3: a boss never yields"),
            new ReasonCode("JAM_CORRIDOR_REPLAN", "JAM", "P1", "stage 4 corridor replan"),
            new ReasonCode("JAM_CORRIDOR_ALTERNATIVE", "JAM", "P1", "stage 4: an alternative corridor"),
            new ReasonCode("JAM_CORRIDOR_NO_ALTERNATIVE", "JAM", "P1", "stage 4: no alternative corridor"),
            new ReasonCode("JAM_EMERGENCY", "JAM", "P1", "stage 5 emergency unjam"),
            new ReasonCode("JAM_EMERGENCY_REVERSE", "JAM", "P1", "stage 5: reverse out"),
            new ReasonCode("JAM_EMERGENCY_ALTERNATE", "JAM", "P1", "stage 5: alternate goal"),
            new ReasonCode("JAM_EMERGENCY_REPLAN", "JAM", "P1", "stage 5: full replan"),
            new ReasonCode("JAM_CHOKE_QUEUE", "JAM", "P1", "waiting in a choke queue"),
            new ReasonCode("JAM_FAILSAFE_GHOST", "JAM", "P1", "fail-safe: collision ghosting"),
            new ReasonCode("SEVERE_UNSTUCK", "JAM", "P1", "fail-safe relocation (place / hop); counted, target <= 1 per 10 unit-minutes"),

            // ---------------------------------------------------------------- COMBAT_IDLE / COMBAT (P0-A)
            new ReasonCode("COMBAT_ACTIVE", "COMBAT", "P0A", "not idle"),
            new ReasonCode("COMBAT_FIRING", "COMBAT", "P0A", "firing"),
            new ReasonCode("COMBAT_MOVING", "COMBAT", "P0A", "moving"),
            new ReasonCode("COMBAT_IDLE_RELOADING", "COMBAT_IDLE", "P0A", "reloading"),
            new ReasonCode("COMBAT_IDLE_WAITING_RESUPPLY", "COMBAT_IDLE", "P0A", "out of ammunition, waiting for resupply"),
            new ReasonCode("COMBAT_IDLE_DISABLED", "COMBAT_IDLE", "P0A", "stunned / disabled"),
            new ReasonCode("COMBAT_IDLE_DISABLED_MAIN_WEAPON", "COMBAT_IDLE", "P0A", "main weapon broken"),
            new ReasonCode("COMBAT_IDLE_DEPLOYING", "COMBAT_IDLE", "P0A", "deploying / packing up"),
            new ReasonCode("COMBAT_IDLE_HOLD_FIRE_ORDER", "COMBAT_IDLE", "P0A", "hold-fire order"),
            new ReasonCode("COMBAT_IDLE_HOLD_FIRE_AMBUSH", "COMBAT_IDLE", "P0A", "ambush discipline"),
            new ReasonCode("COMBAT_IDLE_OBJECTIVE_HOLD", "COMBAT_IDLE", "P0A", "holding an objective"),
            new ReasonCode("COMBAT_IDLE_WAITING_FORMATION", "COMBAT_IDLE", "P0A", "waiting for the formation"),
            new ReasonCode("COMBAT_IDLE_WAITING_FIRE_MISSION", "COMBAT_IDLE", "P0A", "waiting for a fire mission"),
            new ReasonCode("COMBAT_IDLE_GUARD_POST", "COMBAT_IDLE", "P0A", "guard post"),
            new ReasonCode("COMBAT_IDLE_SPOTTING", "COMBAT_IDLE", "P0A", "a recon / support role watching"),
            new ReasonCode("COMBAT_IDLE_NO_VALID_WEAPON_TARGET", "COMBAT_IDLE", "P0A", "nothing its weapons can hit"),
            new ReasonCode("COMBAT_IDLE_NO_REACHABLE_TARGET", "COMBAT_IDLE", "P0A", "nothing reachable"),
            new ReasonCode("COMBAT_IDLE_WAITING_MIN_RANGE", "COMBAT_IDLE", "P0A", "target inside the minimum range"),
            new ReasonCode("COMBAT_IDLE_BLOCKED_BY_FRIEND", "COMBAT_IDLE", "P0A", "a friend in the line of fire"),
            new ReasonCode("COMBAT_IDLE_BLOCKED_BY_LOS", "COMBAT_IDLE", "P0A", "no line of sight"),
            new ReasonCode("COMBAT_IDLE_BLOCKED_BY_ARC", "COMBAT_IDLE", "P0A", "outside the mount's arc"),
            new ReasonCode("COMBAT_IDLE_AIMING", "COMBAT_IDLE", "P0A", "aiming"),
            new ReasonCode("COMBAT_IDLE_BOSS_CONTROLLED", "COMBAT_IDLE", "P0A", "a boss's laid mount"),
            new ReasonCode("COMBAT_IDLE_STALE_AIM", "COMBAT_IDLE", "P0A", "target and ready weapon but no shot (anomaly, recovered)"),
            new ReasonCode("COMBAT_IDLE_UNEXPLAINED", "COMBAT_IDLE", "P0A", "no reason found: the bug Part C2 forbids (recovered)"),

            // ---------------------------------------------------------------- FORMATION (P2, P3)
            new ReasonCode("FORMATION_CHOKE_TRAVEL", "FORMATION", "P2", "choke ahead: travel column"),
            new ReasonCode("FORMATION_SPLASH_SPREAD", "FORMATION", "P2", "splash threat: spread"),
            new ReasonCode("FORMATION_STATIC_HOLD", "FORMATION", "P2", "static defence: hold"),
            new ReasonCode("FORMATION_FLANK_OPEN", "FORMATION", "P2", "flank: open order"),
            new ReasonCode("FORMATION_LOW_COHESION_REGROUP", "FORMATION", "P2", "low cohesion: regroup"),
            new ReasonCode("FORMATION_STATE", "FORMATION", "P2", "formation state change"),
            new ReasonCode("FORMATION_CHOKE_PACKETS", "FORMATION", "P2", "through the choke in packets"),
            new ReasonCode("FORMATION_DISPERSE_HOLD", "FORMATION", "P3", "dispersed hold against artillery"),

            // ---------------------------------------------------------------- MODE (P2)
            new ReasonCode("MODE_DOCTRINE", "MODE", "P2", "the mode doctrine resolved"),
            new ReasonCode("MODE_DOCTRINE_FALLBACK", "MODE", "P2", "unknown mode: BalancedObjectiveDoctrine"),
            new ReasonCode("MODE_PHASE_REBUILD", "MODE", "P2", "a phase change rebuilt anchors and priorities"),
            new ReasonCode("MODE_DEFEND_NO_CHASE", "MODE", "P2", "defend doctrine: no chase"),
            new ReasonCode("MODE_LEASH", "MODE", "P2", "the mode's pursuit leash"),
            new ReasonCode("MODE_RESERVE_HOLD", "MODE", "P2", "reserve held back"),
            new ReasonCode("MODE_RESERVE_COMMIT", "MODE", "P2", "reserve committed"),
            new ReasonCode("MODE_RECON_QUIET", "MODE", "P2", "recon stays quiet"),

            // ---------------------------------------------------------------- BOSS (P0-C, P2, P4)
            new ReasonCode("BOSS_HULL_ROUTE_OWNS_HEADING", "BOSS", "P0C", "the route / lane owns the hull heading (no target steers it)"),
            new ReasonCode("BOSS_HULL_PHASE", "BOSS", "P0C", "a new phase's route goal owns the hull"),
            new ReasonCode("BOSS_HULL_ESCAPE", "BOSS", "P0C", "the scripted escape run owns the hull"),
            new ReasonCode("BOSS_HULL_WEAPON_ALIGNMENT", "BOSS", "P0C", "a hull-fixed weapon's alignment request granted"),
            new ReasonCode("BOSS_HULL_ARMOUR_FACING", "BOSS", "P0C", "standing, the front turned to the heaviest fire (granted)"),
            new ReasonCode("BOSS_HULL_COLLISION", "BOSS", "P0C", "turning away from a predicted collision or a wreck"),
            new ReasonCode("BOSS_HULL_HOLD", "BOSS", "P0C", "holding / stopped"),
            new ReasonCode("BOSS_PHASE_ROUTE", "BOSS", "P0C", "a phase began: new route goal, 3 s mission lock"),
            new ReasonCode("BOSS_BROADSIDE_RECOMPUTE", "BOSS", "P2", "a broken part took mounts away: broadside recomputed"),
            new ReasonCode("BOSS_WEAKPOINT_UTILITY", "BOSS", "P4", "aim at the weakpoint by utility"),
            new ReasonCode("BOSS_TELEGRAPH_ESCAPE_SECTOR", "BOSS", "P4", "escape sectors under a telegraphed attack"),
            new ReasonCode("BOSS_PATTERN_LEARNT", "BOSS", "P4", "a follow-up pattern learnt this match"),
            new ReasonCode("BOSS_PRESSURE_BUDGET_DEFER", "BOSS", "P4", "a big attack waits for the pressure budget"),
            new ReasonCode("BOSS_ESCORT_SPAWN_REJECT", "BOSS", "P5", "an escort / factory spawn refused (no map influence there)"),

            // ---------------------------------------------------------------- NAVAL (P0-C, P5)
            new ReasonCode("NAVAL_BROADSIDE_OFFSET", "NAVAL", "P0C", "the broadside controller's offset holds the hull"),
            new ReasonCode("NAVAL_CPA_AVOID", "NAVAL", "P0C", "closest-approach avoidance turned the hull"),
            new ReasonCode("NAVAL_TURNABOUT_NO_REVERSE", "NAVAL", "P0C", "coming about forward for a goal behind (never reverse)"),
            new ReasonCode("NAVAL_REVERSE_FORBIDDEN", "NAVAL", "P5", "a boss ship's speed would have gone below 0 or a reverse was asked: refused, counted, logged as an error"),

            // ---------------------------------------------------------------- SUPPORT (P2, P3, P4)
            new ReasonCode("SUPPORT_AA_COVERAGE_HANDOFF", "SUPPORT", "P2", "radar lost: AA coverage handed off"),
            new ReasonCode("SUPPORT_AA_COVERAGE_ASSIGNED", "SUPPORT", "P3", "AA assigned to cover an asset"),
            new ReasonCode("SUPPORT_REPAIR_RESERVED", "SUPPORT", "P3", "a repair slot reserved"),
            new ReasonCode("SUPPORT_SMOKE_DECONFLICTED", "SUPPORT", "P3", "smoke kept off a friendly firing lane"),
            new ReasonCode("SUPPORT_SMOKE_PLANNED", "SUPPORT", "P3", "smoke planned"),
            new ReasonCode("SUPPORT_FORECAST_BARRAGE", "SUPPORT", "P4", "a barrage the forecast asks for"),

            // ---------------------------------------------------------------- AIR (P4)
            new ReasonCode("AIR_SEAD_HOLD_INGRESS", "AIR", "P4", "strikers hold at the ingress point for SEAD"),
            new ReasonCode("AIR_SEAD_WINDOW_STRIKE", "AIR", "P4", "SEAD window open: strike"),
            new ReasonCode("AIR_SEAD_FAILED_REROUTE", "AIR", "P4", "SEAD failed: reroute"),
            new ReasonCode("AIR_SEAD_FAILED_DELAY", "AIR", "P4", "SEAD failed: delay"),
            new ReasonCode("AIR_RISK_ROUTE", "AIR", "P4", "risk-aware air route"),
            new ReasonCode("AIR_EGRESS_LOW_RISK", "AIR", "P4", "low-risk egress"),
            new ReasonCode("AIR_CAP_RETURN_ZONE", "AIR", "P4", "CAP fighter returns to its zone"),
            new ReasonCode("AIR_CAP_PATROL", "AIR", "P4", "CAP patrol"),
            new ReasonCode("AIR_TARGET_HANDOFF", "AIR", "P4", "air target handed off"),
            new ReasonCode("AIR_INTERCEPT_PREDICT", "AIR", "P4", "air intercept at the predicted point"),
            new ReasonCode("AIR_BOMBER_WAIT", "AIR", "P4", "bomber loiters for a worthwhile target"),
            new ReasonCode("AIR_BOMBER_GO", "AIR", "P4", "bomber run"),
            new ReasonCode("AIR_BOMBER_RETARGET", "AIR", "P4", "bomber retargets"),

            // ---------------------------------------------------------------- ARTILLERY (P2, P3, P4, P5)
            new ReasonCode("ARTILLERY_ANCHOR_SET", "ARTILLERY", "P2", "fire-support anchor set"),
            new ReasonCode("ARTILLERY_ANCHOR_KEPT", "ARTILLERY", "P2", "fire-support anchor kept"),
            new ReasonCode("ARTILLERY_COUNTERBATTERY_SCOOT", "ARTILLERY", "P2", "counter-battery threat: shoot and scoot"),
            new ReasonCode("ARTILLERY_COUNTERBATTERY_MISSION", "ARTILLERY", "P3", "counter-battery fire mission"),
            new ReasonCode("ARTILLERY_COUNTERBATTERY_AREA_FIRE", "ARTILLERY", "P3", "counter-battery area fire"),
            new ReasonCode("ARTILLERY_SCOOT", "ARTILLERY", "P3", "scoot after the salvo count"),
            new ReasonCode("ARTILLERY_FINISH_MISSION", "ARTILLERY", "P3", "finish a near-dead target"),
            new ReasonCode("ARTILLERY_STALE_TARGET_DROPPED", "ARTILLERY", "P3", "stale remembered target dropped"),
            new ReasonCode("ARTILLERY_ORDER_OWNER", "ARTILLERY", "P4", "one owner orders a gun at a time"),
            new ReasonCode("ARTILLERY_ADAPT_CAMPING_COUNTERBATTERY", "ARTILLERY", "P4", "the enemy camps with artillery: more counter-battery"),
            new ReasonCode("ARTILLERY_SCOOT_DURING_RELOAD", "ARTILLERY", "P5", "scoot inside a reload window that runs on the move (Part L)"),

            // ---------------------------------------------------------------- OBJECTIVE (P3, P4)
            new ReasonCode("OBJECTIVE_PACKAGE_CREATED", "OBJECTIVE", "P3", "attack package created"),
            new ReasonCode("OBJECTIVE_PACKAGE_ABORTED", "OBJECTIVE", "P3", "attack package aborted"),
            new ReasonCode("OBJECTIVE_SYNC_STAGE", "OBJECTIVE", "P3", "synchronised attack: staging"),
            new ReasonCode("OBJECTIVE_SYNC_GO", "OBJECTIVE", "P3", "synchronised attack: go"),
            new ReasonCode("OBJECTIVE_FIX_ENVELOPE", "OBJECTIVE", "P3", "fixing force holds the envelope"),
            new ReasonCode("OBJECTIVE_FIX_AND_FLANK", "OBJECTIVE", "P3", "fix and flank assigned"),
            new ReasonCode("OBJECTIVE_SCOUT_BEFORE_COMMIT", "OBJECTIVE", "P3", "scout before commit"),
            new ReasonCode("OBJECTIVE_SCOUT_TIMEOUT_COMMIT", "OBJECTIVE", "P3", "scout timed out: commit"),
            new ReasonCode("OBJECTIVE_RESERVE_RELEASE", "OBJECTIVE", "P3", "reserve released"),
            new ReasonCode("OBJECTIVE_RESERVE_KEPT_FIGHT_WON", "OBJECTIVE", "P3", "reserve kept: the fight is won"),
            new ReasonCode("OBJECTIVE_ECONOMY_OF_FORCE", "OBJECTIVE", "P3", "economy of force"),
            new ReasonCode("OBJECTIVE_SUNK_COST_RESET", "OBJECTIVE", "P3", "sunk-cost reset"),
            new ReasonCode("OBJECTIVE_DEADLINE_SKIP", "OBJECTIVE", "P3", "deadline: objective skipped"),
            new ReasonCode("OBJECTIVE_DEADLINE_FAST_UNIT", "OBJECTIVE", "P3", "deadline: a fast unit sent"),
            new ReasonCode("OBJECTIVE_DEPTH_NEXT_LINE", "OBJECTIVE", "P3", "defence in depth: next line"),
            new ReasonCode("OBJECTIVE_DEPTH_FORWARD_LINE", "OBJECTIVE", "P3", "defence in depth: forward line restored"),
            new ReasonCode("OBJECTIVE_COUNTERATTACK_WINDOW", "OBJECTIVE", "P3", "counterattack window"),
            new ReasonCode("OBJECTIVE_PLAN_CHOSEN", "OBJECTIVE", "P4", "shallow plan chosen"),
            new ReasonCode("OBJECTIVE_PLAN_KEPT_COMMITMENT", "OBJECTIVE", "P4", "plan kept (commitment window)"),
            new ReasonCode("OBJECTIVE_PLAN_FORECAST_HOLD", "OBJECTIVE", "P4", "forecast says hold"),
            new ReasonCode("OBJECTIVE_PLAN_REPEAT_PENALTY", "OBJECTIVE", "P4", "anti-repetition penalty"),
            new ReasonCode("OBJECTIVE_PLAN_FAILED_REMEMBERED", "OBJECTIVE", "P4", "failed plan remembered"),
            new ReasonCode("OBJECTIVE_PLAN_SUCCEEDED", "OBJECTIVE", "P4", "plan succeeded"),
            new ReasonCode("OBJECTIVE_PLAN_INTERRUPT_REPLAN", "OBJECTIVE", "P4", "tactical interrupt: replan"),
            new ReasonCode("OBJECTIVE_PACKAGE_ABORT_MAIN_LOST", "OBJECTIVE", "P4", "abort: main force lost"),
            new ReasonCode("OBJECTIVE_PACKAGE_ABORT_FLANK_BLOCKED", "OBJECTIVE", "P4", "abort: flank blocked"),
            new ReasonCode("OBJECTIVE_PACKAGE_ABORT_SUPPORT_FAILED", "OBJECTIVE", "P4", "abort: support failed"),
            new ReasonCode("OBJECTIVE_PACKAGE_ABORT_ROUTE_INVALIDATED", "OBJECTIVE", "P4", "abort: route invalidated"),
            new ReasonCode("OBJECTIVE_PACKAGE_ABORT_OBJECTIVE_CHANGED", "OBJECTIVE", "P4", "abort: objective changed"),
            new ReasonCode("OBJECTIVE_PACKAGE_ABORT_ENEMY_ESTIMATE_ROSE", "OBJECTIVE", "P4", "abort: enemy estimate rose"),
            new ReasonCode("OBJECTIVE_PACKAGE_ABORT_TARGET_CLUSTER_MOVED", "OBJECTIVE", "P4", "abort: target cluster moved"),
            new ReasonCode("OBJECTIVE_PACKAGE_ABORT_SUPPORT_LOST", "OBJECTIVE", "P4", "abort: support lost"),
            new ReasonCode("OBJECTIVE_RESERVE_FORECAST_COLLAPSE", "OBJECTIVE", "P4", "forecast collapse: reserve committed"),
            new ReasonCode("OBJECTIVE_OPPORTUNITY_WINDOW", "OBJECTIVE", "P4", "opportunity window"),
            new ReasonCode("OBJECTIVE_PROBE_SENT", "OBJECTIVE", "P4", "probe sent"),
            new ReasonCode("OBJECTIVE_PROBE_EXPLOIT_WINDOW", "OBJECTIVE", "P4", "probe found a weak lane: exploit"),
            new ReasonCode("OBJECTIVE_PROBE_THREAT_FOUND", "OBJECTIVE", "P4", "probe found a threat"),
            new ReasonCode("OBJECTIVE_PROBE_INCONCLUSIVE", "OBJECTIVE", "P4", "probe inconclusive"),
            new ReasonCode("OBJECTIVE_FEINT_SENT", "OBJECTIVE", "P4", "feint sent"),
            new ReasonCode("OBJECTIVE_FEINT_REDEPLOY_SEEN", "OBJECTIVE", "P4", "feint worked: a redeploy seen"),
            new ReasonCode("OBJECTIVE_FEINT_ENDED_NO_REDEPLOY", "OBJECTIVE", "P4", "feint ended without a redeploy"),
            new ReasonCode("OBJECTIVE_FEINT_NO_TACTICAL_UTILITY", "OBJECTIVE", "P4", "feint rejected: no utility"),
            new ReasonCode("OBJECTIVE_ADAPT_MORE_RECON", "OBJECTIVE", "P4", "adaptation: more recon"),

            // ---------------------------------------------------------------- WATCHDOG (P0-A, P5)
            new ReasonCode("WATCHDOG_COMBAT_ANOMALY", "WATCHDOG", "P0A", "a unit's combat anomaly (stale aim) recovered"),
            new ReasonCode("WATCHDOG_RECOVERY_ESCALATED", "WATCHDOG", "P0A", "a unit's recovery escalated"),
            new ReasonCode("WATCHDOG_IDLE_UNEXPLAINED", "WATCHDOG", "P0A", "an armed unit idle without a reason (recovered)"),
            new ReasonCode("WATCHDOG_SQUAD_ZERO_UTILIZATION", "WATCHDOG", "P5", "a squad in contact did no damage for 10-20 s: anchor, route and mission re-evaluated"),
            new ReasonCode("WATCHDOG_SQUAD_STALLED_OBJECTIVE", "WATCHDOG", "P5", "a squad's objective assignment made no progress: route and mission re-evaluated"),
            new ReasonCode("WATCHDOG_IDLE_AUDIT", "WATCHDOG", "P5", "too many armed units idle without a reason: target / firing-solution audit forced"),
            new ReasonCode("WATCHDOG_IDLE_TOP_REASONS", "WATCHDOG", "P5", "the top idle reasons of a side at the audit"),
            new ReasonCode("WATCHDOG_TRAFFIC_ESCALATION", "WATCHDOG", "P5", "high blocked-unit ratio: blocked squads re-routed"),
            new ReasonCode("WATCHDOG_CHURN_DAMPED", "WATCHDOG", "P5", "a churning squad's commitment lengthened for a while"),
            new ReasonCode("WATCHDOG_LOW_UTILIZATION_CLASSES", "WATCHDOG", "P5", "unit classes below the utilization threshold (the purchase modifier acts)"),

            // ---------------------------------------------------------------- SQUAD / ROLE (P2, P3, P4)
            new ReasonCode("SQUAD_LIFECYCLE", "SQUAD", "P2", "squad lifecycle stage"),
            new ReasonCode("SQUAD_MERGE", "SQUAD", "P2", "squads merged"),
            new ReasonCode("SQUAD_SPLIT", "SQUAD", "P2", "squad split"),
            new ReasonCode("SQUAD_REINFORCEMENT_RENDEZVOUS", "SQUAD", "P2", "reinforcement driving to the rendezvous"),
            new ReasonCode("SQUAD_REINFORCEMENT_JOINED", "SQUAD", "P2", "reinforcement joined"),
            new ReasonCode("SQUAD_REGROUP_COHESION", "SQUAD", "P2", "regroup for cohesion"),
            new ReasonCode("SQUAD_SPLIT_TWO_OBJECTIVES", "SQUAD", "P3", "split over two objectives"),
            new ReasonCode("SQUAD_CUE", "SQUAD", "P4", "a tactical communication cue (spec 215; presentation only)"),
            new ReasonCode("ROLE_MAIN_GUN_LOST_SCREEN", "ROLE", "P2", "main gun lost: screen role"),
            new ReasonCode("ROLE_ENGINE_CRIPPLED", "ROLE", "P2", "engine crippled"),
            new ReasonCode("ROLE_APS_LOST", "ROLE", "P2", "APS lost"),
            new ReasonCode("ROLE_CAPABILITY_RESTORED", "ROLE", "P2", "capability restored"),
        };

        private static Dictionary<string, ReasonCode>? _byCode;

        private static Dictionary<string, ReasonCode> ByCode
        {
            get
            {
                if (_byCode != null) return _byCode;
                var d = new Dictionary<string, ReasonCode>(StringComparer.Ordinal);
                foreach (var r in All)
                {
                    d[r.Code] = r;
                    if (r.Alias.Length > 0) d[r.Alias] = r;
                }
                return _byCode = d;
            }
        }

        /// <summary>Whether <paramref name="code"/> (or an alias) is registered.</summary>
        public static bool IsRegistered(string code) => ByCode.ContainsKey(code);

        /// <summary>The registered entry of a code or alias.</summary>
        public static bool TryGet(string code, out ReasonCode entry) => ByCode.TryGetValue(code, out entry);

        /// <summary>The first word of a log line (its code, or a section-94 verb), or "" for an empty line.</summary>
        public static string FirstWord(string line)
        {
            var end = 0;
            while (end < line.Length && line[end] != ' ' && line[end] != ':' && line[end] != '(') end++;
            return line.Substring(0, end);
        }

        /// <summary>Whether a word has the shape of a reason code (CAPITALS_AND_UNDERSCORES with at least one underscore).</summary>
        public static bool LooksLikeCode(string word)
        {
            if (word.Length < 3 || word.IndexOf('_') < 0) return false;
            foreach (var c in word)
                if (!(c is >= 'A' and <= 'Z' || c is >= '0' and <= '9' || c == '_')) return false;
            return true;
        }

        /// <summary>
        /// The codes in <paramref name="log"/> that look like codes but are not registered (a lane that wrote a new code without
        /// registering it): empty when the log is consistent. The tests and the lead's runs call it.
        /// </summary>
        public static List<string> Unregistered(DecisionLog log)
        {
            var bad = new SortedSet<string>(StringComparer.Ordinal);
            foreach (var e in log.Entries)
            {
                var w = FirstWord(e.Text);
                if (LooksLikeCode(w) && !IsRegistered(w)) bad.Add(w);
            }
            return new List<string>(bad);
        }

        /// <summary>Lines per namespace in <paramref name="log"/> (the Part V DecisionLog examples, the lead's counts).</summary>
        public static SortedDictionary<string, int> CountByNamespace(DecisionLog log)
        {
            var counts = new SortedDictionary<string, int>(StringComparer.Ordinal);
            foreach (var e in log.Entries)
                if (TryGet(FirstWord(e.Text), out var r))
                    counts[r.Namespace] = counts.TryGetValue(r.Namespace, out var n) ? n + 1 : 1;
            return counts;
        }

        /// <summary>The code of a boss hull reason (section 96 line; ships use the NAVAL_* names for their own reasons).</summary>
        public static string HullCode(Bosses.HullReason reason, bool naval) => reason switch
        {
            Bosses.HullReason.Route => "BOSS_HULL_ROUTE_OWNS_HEADING",
            Bosses.HullReason.Broadside => "NAVAL_BROADSIDE_OFFSET",
            Bosses.HullReason.Collision => naval ? "NAVAL_CPA_AVOID" : "BOSS_HULL_COLLISION",
            Bosses.HullReason.Phase => "BOSS_HULL_PHASE",
            Bosses.HullReason.Escape => "BOSS_HULL_ESCAPE",
            Bosses.HullReason.WeaponAlignment => "BOSS_HULL_WEAPON_ALIGNMENT",
            Bosses.HullReason.ArmourFacing => "BOSS_HULL_ARMOUR_FACING",
            Bosses.HullReason.Turnabout => naval ? "NAVAL_TURNABOUT_NO_REVERSE" : "BOSS_HULL_HOLD",
            _ => "BOSS_HULL_HOLD",
        };
    }

    /// <summary>AI MASTER P5 (Part O): the codes this lane writes (registered in <see cref="ReasonCodes.All"/>).</summary>
    public static class P5Reasons
    {
        public const string SquadZeroUtilization = "WATCHDOG_SQUAD_ZERO_UTILIZATION";
        public const string SquadStalledObjective = "WATCHDOG_SQUAD_STALLED_OBJECTIVE";
        public const string IdleAudit = "WATCHDOG_IDLE_AUDIT";
        public const string IdleTopReasons = "WATCHDOG_IDLE_TOP_REASONS";
        public const string TrafficEscalation = "WATCHDOG_TRAFFIC_ESCALATION";
        public const string ChurnDamped = "WATCHDOG_CHURN_DAMPED";
        public const string LowUtilizationClasses = "WATCHDOG_LOW_UTILIZATION_CLASSES";
        public const string NavalReverseForbidden = "NAVAL_REVERSE_FORBIDDEN";
        public const string ReloadHold = "POSITION_RELOAD_HOLD";
        public const string ReloadResume = "POSITION_RELOAD_RESUME";
        public const string KeepWhileReloading = "TARGET_KEEP_WHILE_RELOADING";
        public const string ScootDuringReload = "ARTILLERY_SCOOT_DURING_RELOAD";
        public const string BossPhaseRoute = "BOSS_PHASE_ROUTE";
        public const string EscortSpawnReject = "BOSS_ESCORT_SPAWN_REJECT";
    }
}
