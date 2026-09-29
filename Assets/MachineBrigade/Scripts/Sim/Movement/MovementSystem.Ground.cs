#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// Ground that changes under the traffic (prompt 12, the stuck report's causes): a tower
    /// raised where vehicles stand puts them off its ground, a route planned across ground closed
    /// since is planned again, and steering round a hull never turns the nose into a wall.
    /// </summary>
    internal sealed partial class MovementSystem
    {
        /// <summary>Closed rectangles of the grid (see NavGrid.Closed) already looked at; -1 before the first step.</summary>
        private int _closedSeen = -1;

        /// <summary>Vehicles put off the ground of a defence raised on them (tests and the report).</summary>
        internal int GroundCleared { get; private set; }

        /// <summary>Routes planned again because ground they crossed was closed (tests and the report).</summary>
        internal int RoutesReplanned { get; private set; }

        /// <summary>
        /// A fixed defence has just been anchored on its ground (a tower landing in its hardpoint):
        /// every ground vehicle whose centre is now on blocked ground there is put on the nearest
        /// free open ground (it could never drive off it) and plans its route again.
        /// </summary>
        internal void ClearGround(Vehicle defence)
        {
            var reach = MathF.Max(defence.Def.Length, defence.Def.Width) * 0.4f + SimWorld.ObstacleClearance + _world.Grid.CellSize;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Flying || v.Def.Static || v == defence || _world.Grid.IsWalkable(v.Position)) continue;
                if (MathF.Abs(v.Position.X - defence.Position.X) > reach || MathF.Abs(v.Position.Y - defence.Position.Y) > reach) continue;
                if (!TryFreeGround(v, v.Position, out var open)) continue;
                v.Position = open;
                v.Speed = 0f;
                GroundCleared++;
                Vehicle.PathTrace?.Invoke(v, "Put off a defence's ground");
                if (v.HasPath) _world.PathTo(v, v.PathGoal);
            }
        }

        /// <summary>
        /// Ground closed since the last step (a tower raised, a defence anchored): every ground
        /// route still to be driven across it is planned again (the budgeted way). Before, a route
        /// planned round the old ground led the hull into the new footprint, where it pushed until
        /// the stuck rules gave up on it.
        /// </summary>
        private void ReplanClosedRoutes()
        {
            var closed = _world.Grid.Closed;
            if (_closedSeen < 0)
            {
                // The map's own buildings and the defences set up before the battle: nobody has a route yet.
                _closedSeen = closed.Count;
                return;
            }
            for (; _closedSeen < closed.Count; _closedSeen++)
            {
                var (min, max) = closed[_closedSeen];
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Flying || v.Def.Static || !v.HasPath || v.PathQueued) continue;
                    var t = v.Traffic;
                    if (t.YieldingTo.IsValid || t.GateWaitId != 0 || t.Reversing(_world.Time)) continue;
                    if (!RouteCrosses(v, min, max)) continue;
                    RoutesReplanned++;
                    Vehicle.PathTrace?.Invoke(v, "Route crosses closed ground");
                    _world.PathTo(v, v.PathGoal);
                }
            }
        }

        /// <summary>Whether the rest of a vehicle's route (from where it stands) crosses the rectangle.</summary>
        private static bool RouteCrosses(Vehicle v, Vector2 min, Vector2 max)
        {
            var from = v.Position;
            for (var i = v.PathIndex; i < v.Path.Count; i++)
            {
                if (SegmentHitsBox(from, v.Path[i], min, max)) return true;
                from = v.Path[i];
            }
            return false;
        }

        /// <summary>Segment against an axis-aligned box (slab test).</summary>
        private static bool SegmentHitsBox(Vector2 a, Vector2 b, Vector2 min, Vector2 max)
        {
            float t0 = 0f, t1 = 1f;
            var d = b - a;
            for (var axis = 0; axis < 2; axis++)
            {
                var p = axis == 0 ? a.X : a.Y;
                var dd = axis == 0 ? d.X : d.Y;
                var lo = axis == 0 ? min.X : min.Y;
                var hi = axis == 0 ? max.X : max.Y;
                if (MathF.Abs(dd) < 1e-6f)
                {
                    if (p < lo || p > hi) return false;
                    continue;
                }
                var ta = (lo - p) / dd;
                var tb = (hi - p) / dd;
                if (ta > tb) (ta, tb) = (tb, ta);
                t0 = MathF.Max(t0, ta);
                t1 = MathF.Min(t1, tb);
                if (t0 > t1) return false;
            }
            return true;
        }

        /// <summary>
        /// The turn a detour round a hull adds to the heading: its chosen side, or the other when
        /// that side runs the nose into a wall just ahead and the other does not (both closed: the
        /// chosen side, as before; steering straight on pushed into the hull and cost route searches). A titan steering
        /// round a parked friend into the fortress wall stood there, its nose off the waypoint, and
        /// never pivoted back (prompt 12).
        /// </summary>
        private float AvoidTurn(Vehicle v, float desired, float turn)
        {
            if (OpenTowards(v, desired + turn)) return turn;
            if (OpenTowards(v, desired - turn))
            {
                v.AvoidSide = -v.AvoidSide;
                return -turn;
            }
            return turn;
        }

        private bool OpenTowards(Vehicle v, float heading)
        {
            var forward = SimMath.Forward(heading);
            var grid = _world.Grid;
            // Just ahead of the nose: a wall right there is what a hull pressed against it runs into
            // (further out, a narrow street's far side, it may still swerve).
            return grid.IsWalkable(v.Position + forward * (v.Def.HullHalf * 0.5f + 1f));
        }
    }
}
