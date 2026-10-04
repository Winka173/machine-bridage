#nullable enable
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P0-A (spec 42, 105): why a candidate target failed the hard feasibility filter (run before any score). Each
    /// maps to a TARGET_* reason code (Part O) through <see cref="CombatReasons.Code(TargetReject)"/>.
    /// </summary>
    public enum TargetReject : byte
    {
        None,
        Invalid,
        WrongWeaponDomain,
        NotVisible,
        OutOfReach,
        MinRange,
        NoLineOfFire,
        OutsideArc,
        AimTooLong,
        Unreachable,
    }

    /// <summary>
    /// AI MASTER P0-A, Part C2: the reason an armed unit is not shooting. Every armed unit the watchdog looks at has one;
    /// <see cref="Unexplained"/> is the state-machine bug Part C2 forbids (the watchdog recovers it and counts it).
    /// </summary>
    public enum CombatIdleReason : byte
    {
        /// <summary>Not idle: firing, moving or reloading within the window.</summary>
        Active,
        Firing,
        Moving,
        Reloading,
        WaitingResupply,
        Disabled,
        DisabledMainWeapon,
        Deploying,
        HoldFireOrder,
        HoldFireAmbush,
        ObjectiveHold,
        WaitingFormation,
        WaitingFireMission,
        GuardPost,

        /// <summary>A role without an engagement band (recon, support): it watches rather than closes in.</summary>
        Spotting,
        NoValidWeaponTarget,
        NoReachableTarget,
        WaitingMinRange,
        BlockedByFriend,
        BlockedByLos,
        BlockedByArc,
        Aiming,
        BossControlled,

        /// <summary>Target, firing solution and a ready weapon, yet no shot past the aim window (Part C1 COMBAT_ANOMALY).</summary>
        StaleAim,

        /// <summary>No reason found: the bug Part C2 forbids. Recovered automatically.</summary>
        Unexplained,
    }

    /// <summary>
    /// AI MASTER P0-A, Part O: the reason codes of the combat lane (TARGET_*, COMBAT_IDLE_*, WATCHDOG_*) and the helper that
    /// writes them to the <see cref="DecisionLog"/>. Writing a code never feeds back into a decision.
    /// </summary>
    public static class CombatReasons
    {
        public const string TargetNoFiringSolution = "TARGET_NO_FIRING_SOLUTION";
        public const string TargetWrongWeaponDomain = "TARGET_WRONG_WEAPON_DOMAIN";
        public const string TargetUnreachableDropped = "TARGET_UNREACHABLE_DROPPED";
        public const string TargetOverkillSpread = "TARGET_OVERKILL_SPREAD";
        public const string TargetBreachHeld = "TARGET_BREACH_HELD";
        public const string WatchdogCombatAnomaly = "WATCHDOG_COMBAT_ANOMALY";
        public const string WatchdogRecoveryEscalated = "WATCHDOG_RECOVERY_ESCALATED";
        public const string WatchdogIdleUnexplained = "WATCHDOG_IDLE_UNEXPLAINED";
        public const string PositionTransitFallback = "POSITION_TRANSIT_FALLBACK";

        public static string Code(TargetReject reject) => reject switch
        {
            TargetReject.None => "TARGET_OK",
            TargetReject.Invalid => "TARGET_INVALID",
            TargetReject.WrongWeaponDomain => TargetWrongWeaponDomain,
            TargetReject.NotVisible => "TARGET_NOT_VISIBLE",
            TargetReject.OutOfReach => "TARGET_OUT_OF_REACH",
            TargetReject.MinRange => "TARGET_MIN_RANGE",
            TargetReject.NoLineOfFire => TargetNoFiringSolution,
            TargetReject.OutsideArc => "TARGET_OUTSIDE_ARC",
            TargetReject.AimTooLong => "TARGET_AIM_TOO_LONG",
            TargetReject.Unreachable => "TARGET_UNREACHABLE",
            _ => "TARGET_" + reject.ToString().ToUpperInvariant(),
        };

        /// <summary>The Part C2 code of an idle reason ("COMBAT_IDLE_RELOADING", "COMBAT_IDLE_HOLD_FIRE_AMBUSH", ...).</summary>
        public static string Code(CombatIdleReason reason) => reason switch
        {
            CombatIdleReason.Active => "COMBAT_ACTIVE",
            CombatIdleReason.Firing => "COMBAT_FIRING",
            CombatIdleReason.Moving => "COMBAT_MOVING",
            CombatIdleReason.Reloading => "COMBAT_IDLE_RELOADING",
            CombatIdleReason.WaitingResupply => "COMBAT_IDLE_WAITING_RESUPPLY",
            CombatIdleReason.Disabled => "COMBAT_IDLE_DISABLED",
            CombatIdleReason.DisabledMainWeapon => "COMBAT_IDLE_DISABLED_MAIN_WEAPON",
            CombatIdleReason.Deploying => "COMBAT_IDLE_DEPLOYING",
            CombatIdleReason.HoldFireOrder => "COMBAT_IDLE_HOLD_FIRE_ORDER",
            CombatIdleReason.HoldFireAmbush => "COMBAT_IDLE_HOLD_FIRE_AMBUSH",
            CombatIdleReason.ObjectiveHold => "COMBAT_IDLE_OBJECTIVE_HOLD",
            CombatIdleReason.WaitingFormation => "COMBAT_IDLE_WAITING_FORMATION",
            CombatIdleReason.WaitingFireMission => "COMBAT_IDLE_WAITING_FIRE_MISSION",
            CombatIdleReason.GuardPost => "COMBAT_IDLE_GUARD_POST",
            CombatIdleReason.Spotting => "COMBAT_IDLE_SPOTTING",
            CombatIdleReason.NoValidWeaponTarget => "COMBAT_IDLE_NO_VALID_WEAPON_TARGET",
            CombatIdleReason.NoReachableTarget => "COMBAT_IDLE_NO_REACHABLE_TARGET",
            CombatIdleReason.WaitingMinRange => "COMBAT_IDLE_WAITING_MIN_RANGE",
            CombatIdleReason.BlockedByFriend => "COMBAT_IDLE_BLOCKED_BY_FRIEND",
            CombatIdleReason.BlockedByLos => "COMBAT_IDLE_BLOCKED_BY_LOS",
            CombatIdleReason.BlockedByArc => "COMBAT_IDLE_BLOCKED_BY_ARC",
            CombatIdleReason.Aiming => "COMBAT_IDLE_AIMING",
            CombatIdleReason.BossControlled => "COMBAT_IDLE_BOSS_CONTROLLED",
            CombatIdleReason.StaleAim => "COMBAT_IDLE_STALE_AIM",
            CombatIdleReason.Unexplained => "COMBAT_IDLE_UNEXPLAINED",
            _ => "COMBAT_IDLE_" + reason.ToString().ToUpperInvariant(),
        };

        /// <summary>Whether a reason is a valid explanation for standing without shooting (Part C2's list and kin).</summary>
        public static bool Explains(CombatIdleReason reason) => reason != CombatIdleReason.Unexplained && reason != CombatIdleReason.StaleAim;

        /// <summary>Writes one reason line for a unit (Unit layer, kind Emergency for the watchdog's, Target for targeting).</summary>
        internal static void Log(SimWorld world, Entities.Vehicle v, DecisionKind kind, string code, string detail = "")
        {
            world.AiLog.Add(new DecisionEntry(world.Time, v.Team, AiLayer.Unit, (int)v.Id.Value, kind,
                detail.Length > 0 ? code + " " + detail : code));
        }

        internal static string Name(EntityId id) => "#" + id.Value;
    }
}
