#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Bosses.BossBrain;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// AI MASTER P0-C (spec 49, 62): every boss always has a mission anchor, and its movement follows it, not its target.
    /// <list type="bullet">
    /// <item>At sea: the lane of its phase (<see cref="NavalDef.LaneFor"/>), its patrol end, the escape run's far lane
    /// (naval_escape_phase / naval_escape_speed_m_s / naval_lanes / naval_role, used as they are by NavalSystem.Flagship and
    /// PhaseBegins: a phase change is a new route goal), or a passing bay the traffic sent it to.</item>
    /// <item>On land: its own route's node (a mission's, the battlefield's), the structure its order names, the point its
    /// order sends it to, or its post.</item>
    /// </list>
    /// The anchor is the mission's; TacticalAi / the commanders never override a ship's route by an enemy target (the naval
    /// boss is scripted), and a land boss leaves its way for a target only within the chase leash
    /// (<see cref="BossMovementController.MayChase"/>).
    /// </summary>
    internal static class BossMissionController
    {
        internal static void Update(SimWorld world, Vehicle v, BossBrain b, double now)
        {
            b.MissionLocked = v.Escaping || now < b.PhaseMoveUntil;
            if (v.Def.Naval != null && world.Map.Sea is { } sea)
            {
                b.Anchor = sea.At(v.NavalGoal.X, v.NavalGoal.Y);
                b.LaneId = v.NavalLane;
                b.AnchorKind = v.Escaping ? MissionAnchorKind.Escape : v.SeaHold >= 0 ? MissionAnchorKind.Holding
                    : v.Flagship.IsValid ? MissionAnchorKind.EscortObjective : MissionAnchorKind.NavalLane;
                var lane = sea.Lane(v.NavalLane);
                if (lane != null && lane.Patrol > 0f)
                {
                    var u = sea.Frame(v.Position).X;
                    b.RouteProgress = SimMath.Clamp01((u * v.NavalDir + lane.Patrol) / (2f * lane.Patrol));
                }
                return;
            }
            b.LaneId = null;
            if (v.OwnRoute is { Count: > 0 } route)
            {
                var at = Math.Clamp(v.OwnRouteAt, 0, route.Count - 1);
                b.Anchor = route[at];
                b.AnchorKind = MissionAnchorKind.RouteNode;
                b.RouteProgress = route.Count > 1 ? at / (float)(route.Count - 1) : 1f;
                return;
            }
            switch (v.Order.Kind)
            {
                case OrderKind.Attack when world.TryGetVehicle(v.Order.Target, out var t) && t.Def.Static:
                    b.Anchor = t.Position;
                    b.AnchorKind = MissionAnchorKind.TargetStructure;
                    break;
                case OrderKind.Attack when world.TryGetVehicle(v.Order.Target, out var friend) && friend.Team == v.Team:
                    b.Anchor = friend.Position;
                    b.AnchorKind = MissionAnchorKind.EscortObjective;
                    break;
                case OrderKind.Move:
                case OrderKind.AttackMove:
                case OrderKind.Retreat:
                    b.Anchor = v.Order.Point;
                    b.AnchorKind = MissionAnchorKind.RouteNode;
                    break;
                case OrderKind.Idle:
                    b.Anchor = v.GuardPoint;
                    b.AnchorKind = MissionAnchorKind.ArenaCentre;
                    break;
                default:
                    b.Anchor = v.HasPath ? v.PathGoal : v.Position;
                    b.AnchorKind = MissionAnchorKind.RouteNode;
                    break;
            }
            b.RouteProgress = 0f;
        }
    }

    /// <summary>
    /// AI MASTER P0-C (spec 48 "BossPhaseController", 62): the boss's phases are its own data (Part A "boss phase data",
    /// kept: Vehicle.Phase, the transformations, NavalSystem.PhaseBegins' new lane and escape run). The brain notes each new
    /// phase and gives its route goal the hull for a moment (no chase, no weapon alignment), so nothing overrides the phase's
    /// movement while it begins.
    /// </summary>
    internal static class BossPhaseController
    {
        internal static void Update(SimWorld world, Vehicle v, BossBrain b, double now)
        {
            if (b.PhaseSeen == v.Phase) return;
            var first = b.PhaseSeen < 0;
            b.PhaseSeen = v.Phase;
            if (first) return;
            b.PhaseMoveUntil = now + Tun.PhaseMoveSeconds;
            world.AiLog.Add(new AI.DecisionEntry(now, v.Team, AI.AiLayer.Unit, v.Id.Value, AI.DecisionKind.Plan,
                $"boss phase {v.Phase}: new route goal ({(v.Def.Naval != null ? v.NavalLane ?? "-" : "route")})"));
        }
    }
}
