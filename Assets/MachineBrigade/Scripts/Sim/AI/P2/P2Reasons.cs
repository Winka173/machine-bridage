#nullable enable
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P2 (Part O): the reason codes of the role / mode lane, written to the DecisionLog as plain lines (the
    /// DecisionLog class is unchanged, like P0-A's CombatReasons). Namespaces: MODE_*, ARTILLERY_*, POSITION_*, FORMATION_*,
    /// TARGET_*, BOSS_*, SUPPORT_*, and SQUAD_* / ROLE_* for the squad lifecycle and component-state role changes.
    /// </summary>
    public static class P2Reasons
    {
        // Mode doctrine (Part I).
        public const string ModeDoctrine = "MODE_DOCTRINE";
        public const string ModeDoctrineFallback = "MODE_DOCTRINE_FALLBACK";
        public const string ModePhaseRebuild = "MODE_PHASE_REBUILD";
        public const string ModeNoChase = "MODE_DEFEND_NO_CHASE";
        public const string ModeLeash = "MODE_LEASH";
        public const string ModeReserveHold = "MODE_RESERVE_HOLD";
        public const string ModeReserveCommit = "MODE_RESERVE_COMMIT";
        public const string ModeReconQuiet = "MODE_RECON_QUIET";

        // Fire support (Part J).
        public const string ArtilleryAnchorSet = "ARTILLERY_ANCHOR_SET";
        public const string ArtilleryAnchorKept = "ARTILLERY_ANCHOR_KEPT";
        public const string ArtilleryCounterbatteryScoot = "ARTILLERY_COUNTERBATTERY_SCOOT";

        // Positions and firing lanes (Parts D, E).
        public const string PositionHullDown = "POSITION_HULL_DOWN";
        public const string PositionCoverReserved = "POSITION_COVER_RESERVED";
        public const string PositionFriendlyBlock = "POSITION_FRIENDLY_BLOCK";
        public const string PositionLaneWait = "POSITION_FRIENDLY_BLOCK_WAIT";
        public const string PositionLaneSidestep = "POSITION_FRIENDLY_BLOCK_SIDESTEP";
        public const string PositionLaneAltSlot = "POSITION_FRIENDLY_BLOCK_ALT_SLOT";
        public const string PositionLaneBlockerYield = "POSITION_FRIENDLY_BLOCKER_YIELD";
        public const string TargetSwitchFriendlyBlock = "TARGET_SWITCH_FRIENDLY_BLOCK";

        // Component state (Part F).
        public const string RoleMainGunLost = "ROLE_MAIN_GUN_LOST_SCREEN";
        public const string RoleEngineCrippled = "ROLE_ENGINE_CRIPPLED";
        public const string RoleRadarLost = "SUPPORT_AA_COVERAGE_HANDOFF";
        public const string RoleApsLost = "ROLE_APS_LOST";
        public const string RoleRestored = "ROLE_CAPABILITY_RESTORED";
        public const string BossBroadsideRecompute = "BOSS_BROADSIDE_RECOMPUTE";

        // Formations (Part G, 86, 159-162).
        public const string FormationChokeTravel = "FORMATION_CHOKE_TRAVEL";
        public const string FormationSplashSpread = "FORMATION_SPLASH_SPREAD";
        public const string FormationStaticHold = "FORMATION_STATIC_HOLD";
        public const string FormationFlankOpen = "FORMATION_FLANK_OPEN";
        public const string FormationLowCohesion = "FORMATION_LOW_COHESION_REGROUP";
        public const string FormationState = "FORMATION_STATE";
        public const string FormationPackets = "FORMATION_CHOKE_PACKETS";

        // Squad lifecycle and management (19-25, 74).
        public const string SquadLifecycle = "SQUAD_LIFECYCLE";
        public const string SquadMerge = "SQUAD_MERGE";
        public const string SquadSplit = "SQUAD_SPLIT";
        public const string SquadReinforcementPending = "SQUAD_REINFORCEMENT_RENDEZVOUS";
        public const string SquadReinforcementJoined = "SQUAD_REINFORCEMENT_JOINED";
        public const string SquadRegroup = "SQUAD_REGROUP_COHESION";

        /// <summary>A unit's line (Unit layer).</summary>
        internal static void Unit(SimWorld world, Vehicle v, DecisionKind kind, string code, string detail = "") =>
            world.AiLog.Add(new DecisionEntry(world.Time, v.Team, AiLayer.Unit, (int)v.Id.Value, kind, detail.Length > 0 ? code + " " + detail : code));

        /// <summary>A squad's line (Squad layer).</summary>
        internal static void Squad(SimWorld world, int team, int squad, DecisionKind kind, string code, string detail = "") =>
            world.AiLog.Add(new DecisionEntry(world.Time, team, AiLayer.Squad, squad, kind, detail.Length > 0 ? code + " " + detail : code));

        /// <summary>A commander's (or the battle's, team -1) line.</summary>
        internal static void Commander(SimWorld world, int team, DecisionKind kind, string code, string detail = "") =>
            world.AiLog.Add(new DecisionEntry(world.Time, team, AiLayer.Commander, 0, kind, detail.Length > 0 ? code + " " + detail : code));
    }
}
