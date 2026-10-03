#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// The safety net for stuck vehicles (prompt 12 C.3). It only catches what the causes fixed
    /// elsewhere leave over: a ground vehicle with somewhere to go that has not moved more than
    /// <see cref="RescueMove"/> metres in <see cref="RescueAfter"/> seconds is helped out, one rung
    /// at a time, <see cref="RescueAfter"/> seconds apart:
    /// <list type="number">
    /// <item>standing on blocked ground (a tower came down on it): put on the nearest open, free
    /// ground at once;</item>
    /// <item>otherwise it drives through its own side's hulls for a few seconds (and they through
    /// it), its waits at doorways and behind friends are dropped and its route is planned again;</item>
    /// <item>still stuck: it is put a few metres on along its route (or on the nearest free open
    /// ground), and the route is planned again.</item>
    /// </list>
    /// Every activation is logged (<see cref="RescueLog"/>), and the stuck report lists them: each
    /// one is a case to fix at its cause.
    /// </summary>
    internal sealed partial class MovementSystem
    {
        /// <summary>Seconds without headway before the safety net steps in (and between its rungs).</summary>
        internal const double RescueAfter = 10.0;

        /// <summary>Moving this far from where it last got going counts as headway.</summary>
        private const float RescueMove = 2.5f;

        /// <summary>Seconds without a goal after the stuck rules gave up that still count as stuck (see StuckWatch.Grace).</summary>
        private const double RescueGrace = 6.0;

        /// <summary>How long a rescued vehicle drives through its own side's hulls.</summary>
        private static double GhostSeconds => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.GhostSeconds;

        /// <summary>A second rescue within this long of a first is the next rung.</summary>
        private const double RungMemory = 25.0;

        internal readonly struct RescueEntry
        {
            public RescueEntry(long tick, double at, int vehicle, string defId, int team, string kind, Vector2 from, Vector2 to)
            {
                Tick = tick;
                At = at;
                Vehicle = vehicle;
                DefId = defId;
                Team = team;
                Kind = kind;
                From = from;
                To = to;
            }

            public long Tick { get; }
            public double At { get; }
            public int Vehicle { get; }
            public string DefId { get; }
            public int Team { get; }

            /// <summary>"place" (off blocked ground), "ghost" (through friends, route again) or "hop" (on along its route).</summary>
            public string Kind { get; }
            public Vector2 From { get; }
            public Vector2 To { get; }
        }

        /// <summary>Every time the safety net stepped in this battle.</summary>
        internal List<RescueEntry> RescueLog { get; } = new();

        /// <summary>Off only to measure the causes on their own (the stuck report's "before" runs).</summary>
        internal bool RescueEnabled { get; set; } = true;

        /// <summary>Driving through its own side's hulls (the safety net's first rung).</summary>
        private bool Ghosting(Vehicle v) => _world.Time < v.Traffic.GhostUntil;

        /// <summary>Two hulls that do not collide this step: the same side, and one of them rescued a moment ago.</summary>
        private bool PassThrough(Vehicle a, Vehicle b) => a.Team == b.Team && (Ghosting(a) || Ghosting(b));

        /// <summary>Checks one vehicle (every half second, staggered by id) and steps in when it has been stuck long enough.</summary>
        private void WatchRescue(Vehicle v)
        {
            if (!RescueEnabled || v.Flying || v.Def.Static || v.Scripted || ((_world.Tick + v.Id.Value) % 10) != 0) return;
            var t = v.Traffic;
            var now = _world.Time;
            var held = v.Burrow != Vehicle.BurrowState.Surface || v.Landing || v.Stunned || t.YieldingTo.IsValid || t.Reversing(now);
            var wants = StuckWatch.Wants(_world, v, out var goal);
            // Given up on (or no route found) a moment ago: its commander sends it again, still stuck.
            var between = !wants && now - Math.Max(t.GaveUpAt, t.PathFailedAt) < RescueGrace;
            if (held || (!wants && !between) || double.IsNaN(t.RescueSince) ||
                Vector2.DistanceSquared(v.Position, t.RescueAnchor) > RescueMove * RescueMove)
            {
                t.RescueAnchor = v.Position;
                t.RescueSince = now;
                return;
            }
            if (between) return;
            if (now - t.RescueSince < RescueAfter) return;
            t.RescueSince = now;
            Rescue(v, goal);
        }

        private double LastRescue(Vehicle v)
        {
            for (var i = RescueLog.Count - 1; i >= 0; i--)
                if (RescueLog[i].Vehicle == v.Id.Value) return RescueLog[i].At;
            return double.NegativeInfinity;
        }

        private void Rescue(Vehicle v, Vector2 goal)
        {
            var t = v.Traffic;
            var from = v.Position;
            string kind;
            if (!_world.Grid.IsWalkable(v.Position))
            {
                kind = "place";
                if (TryFreeGround(v, v.Position, out var open)) v.Position = open;
            }
            else if (_world.Time - LastRescue(v) > RungMemory)
            {
                kind = "ghost";
                t.GhostUntil = _world.Time + GhostSeconds;
            }
            else
            {
                kind = "hop";
                if (TryHop(v, out var ahead) || TryFreeGround(v, v.Position, out ahead)) v.Position = ahead;
            }
            t.Rescues++;
            RescueLog.Add(new RescueEntry(_world.Tick, _world.Time, v.Id.Value, v.Def.Id, v.Team, kind, from, v.Position));
            Vehicle.PathTrace?.Invoke(v, $"Rescue {kind}");
            // Whatever held it (a doorway's turn, a queue, a stale route) is dropped: it plans its way again.
            t.WaitingForGate = false;
            t.GateWaitId = 0;
            t.QueueBehind = EntityId.None;
            t.HoldUntil = double.NegativeInfinity;
            v.StuckStrikes = 0;
            v.Speed = 0f;
            _world.PathTo(v, goal);
        }

        /// <summary>The nearest open cell to <paramref name="near"/> (up to 10 rings out) that no other hull stands on.</summary>
        private bool TryFreeGround(Vehicle v, Vector2 near, out Vector2 spot)
        {
            var grid = _world.Grid;
            var (cx, cy) = grid.CellOf(near);
            for (var ring = 0; ring <= 10; ring++)
            {
                var best = float.MaxValue;
                spot = default;
                for (var y = cy - ring; y <= cy + ring; y++)
                for (var x = cx - ring; x <= cx + ring; x++)
                {
                    if (Math.Abs(x - cx) != ring && Math.Abs(y - cy) != ring) continue;
                    if (!grid.IsWalkable(x, y)) continue;
                    var c = grid.CellCenter(x, y);
                    if (!_world.Map.Contains(c) || HullNear(v, c)) continue;
                    var d = Vector2.DistanceSquared(c, near);
                    if (d >= best) continue;
                    best = d;
                    spot = c;
                }
                if (best < float.MaxValue) return true;
            }
            spot = near;
            return false;
        }

        /// <summary>A free open spot 3 to 9 m on along its route, in plain line of the waypoint after it.</summary>
        private bool TryHop(Vehicle v, out Vector2 spot)
        {
            spot = default;
            if (!v.HasPath) return false;
            var grid = _world.Grid;
            var next = v.Path[v.PathIndex];
            var way = next - v.Position;
            var length = way.Length();
            if (length < 1f) return false;
            way /= length;
            for (var d = MathF.Min(9f, length); d >= 3f; d -= 1.5f)
            {
                var p = v.Position + way * d;
                if (!_world.Map.Contains(p) || !grid.IsWalkable(p) || HullNear(v, p) || !grid.LineOfSight(p, next)) continue;
                spot = p;
                return true;
            }
            return false;
        }
    }
}
