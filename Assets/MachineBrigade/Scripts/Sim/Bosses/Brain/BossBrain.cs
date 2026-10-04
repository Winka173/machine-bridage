#nullable enable
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>AI MASTER P0-C (spec 49): what a boss's movement is anchored to (the target never is).</summary>
    public enum MissionAnchorKind
    {
        None,
        /// <summary>A node of its own route (a mission's, the battlefield's) or the point its order sends it to.</summary>
        RouteNode,
        /// <summary>Its post (no order): the arena it holds.</summary>
        ArenaCentre,
        /// <summary>The structure its order names (a base, a gate).</summary>
        TargetStructure,
        /// <summary>A sea lane (its phase's patrol).</summary>
        NavalLane,
        /// <summary>The flagship it escorts.</summary>
        EscortObjective,
        /// <summary>Its run out of the battle (a phase's escape lane).</summary>
        Escape,
        /// <summary>A passing bay the sea traffic sent it to.</summary>
        Holding,
    }

    /// <summary>AI MASTER P0-C (spec 50, section 96 "HullTargetReason"): why the hull points where it does.</summary>
    public enum HullReason
    {
        /// <summary>Following its route / lane (the default).</summary>
        Route,
        /// <summary>The broadside controller's offset from the route (spec 56).</summary>
        Broadside,
        /// <summary>Turning away from a predicted collision (spec 60) or a wreck.</summary>
        Collision,
        /// <summary>A new phase's route goal (spec 62).</summary>
        Phase,
        /// <summary>Its scripted escape run.</summary>
        Escape,
        /// <summary>A hull-dependent weapon's alignment request, granted (Part U).</summary>
        WeaponAlignment,
        /// <summary>Standing, its front turned to the heaviest fire (prompt 28 F.4), granted.</summary>
        ArmourFacing,
        /// <summary>Coming about for a goal behind it (no reverse, spec 52).</summary>
        Turnabout,
        /// <summary>In a passing bay, or stopped (stunned, landing, arrived).</summary>
        Hold,
    }

    /// <summary>AI MASTER P0-C (spec 64): the steering law a boss's body keeps.</summary>
    public enum BossCraft
    {
        /// <summary>Tracks or wheels: reverse only if designed, never continuously towards a target.</summary>
        Ground,
        /// <summary>A train: its rail decides (the rail system).</summary>
        Rail,
        /// <summary>A ship or a surfaced submarine: never reverses (spec 52).</summary>
        Naval,
        /// <summary>A rotor / hover craft: may turn on the spot for a hull-fixed weapon, never flipping back and forth.</summary>
        Rotor,
        /// <summary>An aeroplane: attack runs and orbits (no hover turns).</summary>
        FixedWing,
        /// <summary>An airship / warship in the air: holds its heading to fire, turns only on its route.</summary>
        Airship,
    }

    /// <summary>
    /// AI MASTER P0-C (spec 48, Part U "boss/naval"): one moving boss's brain. The parts are the controllers in this folder:
    /// <see cref="BossMissionController"/> (anchor, escape and phase lanes), <see cref="BossMovementController"/> (hull
    /// arbitration, ground and air laws, the corridor; <see cref="NavalBossMovementController"/> at sea),
    /// <see cref="BossWeaponDirector"/> (active-DPS bearing, fire cadence), <see cref="BossPhaseController"/>,
    /// <see cref="BossEscortCoordinator"/> (rings) and <see cref="BossTargetDirector"/> (target worth). This class only holds
    /// their state and the section-96 debug fields; nothing here is read back by the battle except through those controllers.
    /// Core principle (Part U): the hull decides where the platform goes and how the body turns; turrets decide what they
    /// shoot; only hull-dependent weapons may request body alignment, and the movement / mission controller arbitrates it.
    /// </summary>
    public sealed class BossBrain
    {
        internal BossBrain(BossCraft craft) => Craft = craft;

        public BossCraft Craft { get; }

        // ------------------------------------------------------------ mission (spec 49, 62)

        public MissionAnchorKind AnchorKind { get; internal set; }
        public Vector2 Anchor { get; internal set; }

        /// <summary>Section 96 "LaneId": its sea lane (null on land).</summary>
        public string? LaneId { get; internal set; }

        /// <summary>Section 96 "RouteProgress": 0-1 along its patrol / route.</summary>
        public float RouteProgress { get; internal set; }

        /// <summary>The phase the brain last saw, and until when its new route goal owns the hull (spec 62).</summary>
        internal int PhaseSeen = -1;
        internal double PhaseMoveUntil = double.NegativeInfinity;

        /// <summary>The mission owns the hull now (escape run, a new phase's goal): no chasing, no weapon alignment.</summary>
        public bool MissionLocked { get; internal set; }

        // ------------------------------------------------------------ hull (spec 50, 53-58)

        /// <summary>Section 96 "DesiredHullHeading" (radians, the game's convention).</summary>
        public float DesiredHullHeading { get; internal set; }

        /// <summary>Section 96 "ActualHeading" (radians) at the brain's last look.</summary>
        public float ActualHeading { get; internal set; }

        /// <summary>Section 96 "HullTargetReason".</summary>
        public HullReason HullReason { get; internal set; }

        /// <summary>The route's own heading (lane tangent or straight to the goal), before the broadside offset.</summary>
        public float RouteHeading { get; internal set; }

        /// <summary>Spec 53: Rmin = speed / angular speed (m), and the planner's radius = max(collision radius, 1.1 Rmin).</summary>
        public float MinTurnRadius { get; internal set; }
        public float PlanningRadius { get; internal set; }

        /// <summary>Section 96 "TurnRadius": the radius it is turning on now (m; +inf going straight).</summary>
        public float TurnRadius { get; internal set; } = float.PositiveInfinity;

        /// <summary>Spec 54: the look-ahead distance along the lane (m).</summary>
        public float LookAhead { get; internal set; }

        /// <summary>Coming about for a goal behind it (spec 52, 58): the side it turns to (+1 clockwise, -1), kept until lined up.</summary>
        internal int TurnSide;

        // ------------------------------------------------------------ broadside (spec 55-57, 104, 202)

        /// <summary>Section 96 "BroadsideCandidate" (radians): the best sampled hull offset this brain tick.</summary>
        public float BroadsideCandidate { get; internal set; }

        /// <summary>The held offset (radians, changes only past the deadband / the leave band) and the smoothed one steered.</summary>
        public float BroadsideHeld { get; internal set; }
        public float BroadsideOffset { get; internal set; }

        /// <summary>Spec 55: in broadside (entered within 8 degrees of it, left only beyond 15).</summary>
        public bool BroadsideEngaged { get; internal set; }

        /// <summary>Spec 202: DPS bearing now / DPS with something to shoot at (1 when nothing is in reach).</summary>
        public float ActiveDpsFraction { get; internal set; } = 1f;

        // ------------------------------------------------------------ targets (spec 65, section 96)

        /// <summary>Section 96 "TargetId": the main mount's target.</summary>
        public EntityId TargetId { get; internal set; }

        /// <summary>Section 96 "TurretTargets[]": each mount's target (None when it has none).</summary>
        public IReadOnlyList<EntityId> TurretTargets => _turretTargets;
        internal readonly List<EntityId> _turretTargets = new();

        // ------------------------------------------------------------ traffic (spec 33, 59-60)

        /// <summary>Section 96 "CPA threat": the ship it is avoiding, when, and how close the hulls would come (m across).</summary>
        public EntityId CpaThreat { get; internal set; }
        public float CpaTime { get; internal set; }
        public float CpaDistance { get; internal set; }

        /// <summary>Spec 33: its corridor ahead (ground bosses under way), refreshed every step.</summary>
        public bool HasCorridor { get; internal set; }
        public BossCorridor Corridor { get; internal set; }

        // ------------------------------------------------------------ weapon alignment / reverse (Part U, spec 52, 63)

        /// <summary>The last hull alignment granted to a hull-dependent weapon (radians) and when.</summary>
        internal float AlignGranted;
        internal double AlignGrantedAt = double.NegativeInfinity;

        /// <summary>Hull alignment requests refused (mission locked, airship law, a flip too soon): the tests read it.</summary>
        public int AlignRefused { get; internal set; }

        /// <summary>Reverses it made (ground, designed only) and reverses refused (never at sea; too soon on land).</summary>
        public int Reverses { get; internal set; }
        public int ReversesRefused { get; internal set; }
        internal double LastReverseAt = double.NegativeInfinity;

        /// <summary>Goals behind a ship turned into a forward turn instead of a reverse (spec 52, 103's PerpendicularForwardChoice).</summary>
        public int ReverseRequestsTurned { get; internal set; }

        /// <summary>Times a chase off its way was refused (anchor before target, spec 49).</summary>
        public int ChasesRefused { get; internal set; }

        /// <summary>The reason last written to the decision log (a line is added only when it changes).</summary>
        internal HullReason LoggedReason = (HullReason)(-1);
        internal bool LoggedBroadside;

        /// <summary>Section 96's fields as one line (the debug overlay, the decision log's context).</summary>
        public string DebugLine()
        {
            var c = CultureInfo.InvariantCulture;
            var turrets = new System.Text.StringBuilder();
            for (var i = 0; i < _turretTargets.Count; i++)
            {
                if (i > 0) turrets.Append(',');
                turrets.Append(_turretTargets[i].IsValid ? _turretTargets[i].Value.ToString(c) : "-");
            }
            return string.Format(c,
                "lane={0} progress={1:0.00} desired={2:0} actual={3:0} broadside={4:0}{5} turnR={6:0.0} target={7} reason={8} turrets=[{9}] cpa={10}@{11:0.0}s/{12:0.0}m dps={13:0.00} anchor={14}",
                LaneId ?? "-", RouteProgress, Deg(DesiredHullHeading), Deg(ActualHeading), Deg(BroadsideCandidate), BroadsideEngaged ? "*" : "",
                float.IsPositiveInfinity(TurnRadius) ? -1f : TurnRadius, TargetId.IsValid ? TargetId.Value.ToString(c) : "-", HullReason, turrets,
                CpaThreat.IsValid ? CpaThreat.Value.ToString(c) : "-", CpaTime, CpaDistance, ActiveDpsFraction, AnchorKind);
        }

        private static float Deg(float radians) => radians * (180f / MathF.PI);
    }

    /// <summary>AI MASTER P0-C (spec 33): a moving boss's corridor ahead: a capsule its friends keep clear of.</summary>
    public readonly struct BossCorridor
    {
        public BossCorridor(EntityId boss, int team, Vector2 from, Vector2 to, float halfWidth)
        {
            Boss = boss;
            Team = team;
            From = from;
            To = to;
            HalfWidth = halfWidth;
        }

        public EntityId Boss { get; }
        public int Team { get; }

        /// <summary>The boss's middle and the far end of the stretch its friends clear (25-35 m ahead).</summary>
        public Vector2 From { get; }
        public Vector2 To { get; }

        /// <summary>Half the boss's width + 2.5 m.</summary>
        public float HalfWidth { get; }

        /// <summary>Whether a hull of <paramref name="radius"/> at <paramref name="p"/> reaches into the corridor.</summary>
        public bool Holds(Vector2 p, float radius) => BrainMath.DistanceToSegment(p, From, To) < HalfWidth + radius;

        /// <summary>The way the boss is going along it (unit; its middle to the far end).</summary>
        public Vector2 Direction
        {
            get
            {
                var d = To - From;
                var l = d.Length();
                return l > 1e-4f ? d / l : new Vector2(0f, 1f);
            }
        }
    }
}
