#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Part E2's answers to a friend in the line of fire, in the spec's order.</summary>
    public enum LaneResolution : byte
    {
        None,
        Wait,
        Sidestep,
        AlternateSlot,
        Retarget,
        MoveBlocker,
    }

    /// <summary>
    /// AI MASTER P2 Part E: friendly firing-lane / blocked-shot handling. A unit with a valid target and a friend standing in
    /// its direct line goes up the E2 ladder, one rung per ai.firingLane.cooldownSeconds while it stays blocked: (1) wait
    /// briefly when the blocker is driving through, (2) a small lateral sidestep, (3) the equivalent slot on the same ring
    /// round the target, (4) another target, (5) only then the idle blocker (an AI squad-mate, not firing, not the player's)
    /// steps aside. No oscillation: only the shooter farther from the target acts on a pair, a blocker asked to yield is not
    /// moved again for the cooldown, and the side is the one away from the blocker (fixed per pair). E3 (boss mounts) is the
    /// combat system's per-mount targeting: one blocked turret never stops the others. Deterministic.
    /// </summary>
    public sealed class FiringLaneResolver
    {
        private sealed class Entry
        {
            public int Rung;
            public double Since, NextAt;
            public EntityId Blocker;
        }

        private readonly SimWorld _world;
        private readonly Dictionary<EntityId, Entry> _state = new();
        private readonly Dictionary<EntityId, double> _yielding = new();

        internal FiringLaneResolver(SimWorld world) => _world = world;

        /// <summary>The nearest friendly ground hull in <paramref name="v"/>'s direct line to <paramref name="target"/> (null: clear).</summary>
        public Vehicle? Blocker(Vehicle v, Vector2 target)
        {
            var from = v.Position;
            var d = target - from;
            var length = d.Length();
            if (length < global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.BlockerLengthMax) return null;
            var dir = d / length;
            Vehicle? best = null;
            var bestAlong = float.MaxValue;
            foreach (var f in _world.VehicleList)
            {
                if (f == v || !f.IsAlive || f.Team != v.Team || f.Flying || f.Def.Static) continue;
                var rel = f.Position - from;
                var along = Vector2.Dot(rel, dir);
                if (along <= global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.BlockerAlongMax || along >= length - global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.BlockerLengthSub || along > global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.BlockerAlongMin) continue;
                if (MathF.Abs(rel.X * dir.Y - rel.Y * dir.X) >= f.Radius + 1f) continue;
                if (along < bestAlong)
                {
                    bestAlong = along;
                    best = f;
                }
            }
            return best;
        }

        /// <summary>
        /// The next E2 step for <paramref name="v"/> blocked on its way to <paramref name="target"/>: a point to move to
        /// (Sidestep, AlternateSlot), the blocker and its point (MoveBlocker), or Wait / Retarget / None (clear).
        /// </summary>
        public LaneResolution Resolve(Vehicle v, Vector2 target, out Vector2 point, out Vehicle? blocker)
        {
            point = v.Position;
            var now = _world.Time;
            blocker = Blocker(v, target);
            if (blocker == null)
            {
                _state.Remove(v.Id);
                return LaneResolution.None;
            }
            // A unit asked to yield holds still for the cooldown (no ping-pong with the one it yields to).
            if (_yielding.TryGetValue(v.Id, out var until) && until > now) return LaneResolution.Wait;
            // Only the rear shooter of a pair acts: a blocker that is itself blocked by this unit towards the same target waits.
            if (_state.TryGetValue(blocker.Id, out var other) && other.Blocker.Value == v.Id.Value &&
                Vector2.DistanceSquared(blocker.Position, target) > Vector2.DistanceSquared(v.Position, target)) return LaneResolution.Wait;
            if (!_state.TryGetValue(v.Id, out var e) || e.Blocker.Value != blocker.Id.Value)
            {
                e = new Entry { Rung = 0, Since = now, NextAt = now, Blocker = blocker.Id };
                _state[v.Id] = e;
                P2Reasons.Unit(_world, v, DecisionKind.State, P2Reasons.PositionFriendlyBlock, CombatReasons.Name(blocker.Id));
            }
            if (now < e.NextAt) return LaneResolution.Wait;
            var dir = target - v.Position;
            dir = dir.LengthSquared() > 1e-4f ? Vector2.Normalize(dir) : SimMath.Forward(v.Heading);
            var side = new Vector2(dir.Y, -dir.X);
            // Away from the blocker's side of the line (straight on: by id parity, fixed per pair).
            var offset = Vector2.Dot(blocker.Position - v.Position, side);
            var sign = MathF.Abs(offset) > global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.ResolveAbsMin ? -MathF.Sign(offset) : ((v.Id.Value & 1) == 0 ? 1f : -1f);
            while (true)
            {
                var rung = e.Rung++;
                e.NextAt = now + (rung == 0 ? Tun.FiringLane.WaitSeconds : Tun.FiringLane.CooldownSeconds);
                switch (rung)
                {
                    case 0:
                        // 1. The blocker is driving through: wait a moment.
                        if (blocker.IsMoving && MathF.Abs(Vector2.Dot(SimMath.Forward(blocker.Heading), side)) > 0.3f)
                        {
                            P2Reasons.Unit(_world, v, DecisionKind.Action, P2Reasons.PositionLaneWait);
                            return LaneResolution.Wait;
                        }
                        continue;
                    case 1:
                        // 2. A small lateral sidestep that clears the line: the tuned step first, then up to twice it (a hull a few
                        // metres ahead covers more of the line than one step clears; a sidestep that leaves it blocked is no rung).
                        for (var k = 2; k <= 4; k++)
                        {
                            var metres = Tun.FiringLane.SidestepMetres * k * global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.ResolveSidestepMetresScale;
                            if (Step(v, target, side * sign * metres, blocker, out point) || Step(v, target, -side * sign * metres, blocker, out point))
                            {
                                P2Reasons.Unit(_world, v, DecisionKind.Action, P2Reasons.PositionLaneSidestep, $"({point.X:0},{point.Y:0})");
                                return LaneResolution.Sidestep;
                            }
                        }
                        continue;
                    case 2:
                        // 3. The equivalent slot: same distance to the target, shifted round it.
                        if (Ring(v, target, sign, blocker, out point) || Ring(v, target, -sign, blocker, out point))
                        {
                            P2Reasons.Unit(_world, v, DecisionKind.Action, P2Reasons.PositionLaneAltSlot, $"({point.X:0},{point.Y:0})");
                            return LaneResolution.AlternateSlot;
                        }
                        continue;
                    case 3:
                        // 4. Another target.
                        P2Reasons.Unit(_world, v, DecisionKind.Target, P2Reasons.TargetSwitchFriendlyBlock);
                        return LaneResolution.Retarget;
                    default:
                        // 5. Only now, and only an idle AI squad-mate, the blocker steps aside; then the ladder starts again.
                        e.Rung = 1;
                        if (!blocker.IsMoving && _world.Time - blocker.LastFiredAt > global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.ResolveTimeMin && !blocker.UnderPlayerControl(now) && blocker.Def.Speed > 0f &&
                            !(_yielding.TryGetValue(blocker.Id, out var y) && y > now))
                        {
                            var nudge = blocker.Position - side * sign * Tun.FiringLane.BlockerNudgeMetres;
                            if (_world.Grid.IsWalkable(nudge))
                            {
                                point = nudge;
                                _yielding[blocker.Id] = now + Tun.FiringLane.CooldownSeconds;
                                P2Reasons.Unit(_world, blocker, DecisionKind.Action, P2Reasons.PositionLaneBlockerYield, "for " + CombatReasons.Name(v.Id));
                                return LaneResolution.MoveBlocker;
                            }
                        }
                        return LaneResolution.Wait;
                }
            }
        }

        private bool Step(Vehicle v, Vector2 target, Vector2 offset, Vehicle blocker, out Vector2 point)
        {
            point = _world.Map.Clamp(v.Position + offset, global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.StepMargin);
            return _world.Grid.IsWalkable(point) && !InLine(point, target, blocker);
        }

        private bool Ring(Vehicle v, Vector2 target, float sign, Vehicle blocker, out Vector2 point)
        {
            var r = Vector2.Distance(v.Position, target);
            point = v.Position;
            if (r < 4f) return false;
            var angle = Tun.FiringLane.SlotShiftMetres / r * sign;
            var rel = v.Position - target;
            var c = MathF.Cos(angle);
            var s = MathF.Sin(angle);
            point = _world.Map.Clamp(target + new Vector2(rel.X * c - rel.Y * s, rel.X * s + rel.Y * c), global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.RingMargin);
            return _world.Grid.IsWalkable(point) && !InLine(point, target, blocker);
        }

        private static bool InLine(Vector2 from, Vector2 target, Vehicle blocker)
        {
            var d = target - from;
            var length = d.Length();
            if (length < global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.InLineLengthMax) return false;
            var dir = d / length;
            var rel = blocker.Position - from;
            var along = Vector2.Dot(rel, dir);
            if (along <= global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.InLineAlongMax || along >= length - global::MachineBrigade.Sim.Content.SimTunables.Maps.FiringLaneResolver.InLineLengthSub) return false;
            return MathF.Abs(rel.X * dir.Y - rel.Y * dir.X) < blocker.Radius + 1f;
        }

        /// <summary>The E2 rung a unit is on (tests, debug); -1 when it is not blocked.</summary>
        public int RungOf(EntityId id) => _state.TryGetValue(id, out var e) ? e.Rung : -1;
    }
}
