#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// Gives each vehicle in a group its own destination around the ordered point, so a
    /// group settles into a cluster instead of every vehicle shoving towards one spot.
    /// </summary>
    public static class Formation
    {
        /// <summary>
        /// Destinations round <paramref name="center"/>, spaced <paramref name="spacing"/> apart.
        /// With <paramref name="lanes"/>, none lies in a doorway or its mouth (a gate, a gap between
        /// buildings): a group sent there stops beside it, where it does not close the way. With
        /// <paramref name="region"/> (the group's ground, see <see cref="NavGrid.RegionOf(int, int)"/>)
        /// every slot is ground the group can reach, and none lies behind a wall from the first
        /// slot (over the ground at most half as far again as in a straight line): a slot on the
        /// far side of a wall sent its vehicle the long way round, or nowhere (prompt 12).
        /// </summary>
        public static List<Vector2> Slots(Vector2 center, int count, float spacing, NavGrid grid, LaneMap? lanes = null, int region = 0)
        {
            var slots = new List<Vector2>(count);
            if (count <= 0) return slots;
            var near = region > 0;
            if (grid.TryNearestInRegion(center, region, 16, out var first))
            {
                if (lanes != null && lanes.NoParkAt(first) && lanes.TryParkable(first, 12f, out var beside) &&
                    (region <= 0 || grid.RegionOf(beside) == region)) first = beside;
                slots.Add(first);
            }
            else near = false;
            // How far over the ground each cell is from the first slot (out to where the rings may go):
            // walked only once a slot is not in plain line of the first one (in the open it never is).
            var rings = (int)MathF.Ceiling(MathF.Sqrt(count / 3f)) + 3;
            var walkReach = MathF.Min(80f, rings * spacing + 8f);
            var walked = false;
            var origin = near ? first : center;

            for (var ring = 1; slots.Count < count && ring <= 24; ring++)
            {
                var around = 6 * ring;
                for (var k = 0; k < around && slots.Count < count; k++)
                {
                    var angle = k * SimMath.Tau / around + ring * 0.5f;
                    var candidate = center + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (ring * spacing);
                    if (!grid.IsWalkable(candidate) || !IsFree(slots, candidate, spacing * 0.8f)) continue;
                    if (lanes != null && lanes.NoParkAt(candidate)) continue;
                    if (near && !grid.LineOfSight(origin, candidate))
                    {
                        if (!walked)
                        {
                            grid.WalkFrom(origin, walkReach);
                            walked = true;
                        }
                        if (!Near(grid, origin, candidate, ring)) continue;
                    }
                    slots.Add(candidate);
                }
            }
            return slots;
        }

        /// <summary>
        /// Reached by the last walk from the first slot, over the ground no more than half as far
        /// again as straight (plus two cells) on the first three rings; further out (a big group in
        /// a small yard, a garrison round the keep's HQ) up to two and a half times, so it spreads out
        /// through a gate instead of packing the yard.
        /// </summary>
        private static bool Near(NavGrid grid, Vector2 origin, Vector2 candidate, int ring)
        {
            var steps = grid.StepsTo(candidate);
            if (steps < 0) return false;
            // (Four-neighbour steps: a diagonal line takes up to 1.41 times its cells.)
            var straight = Vector2.Distance(origin, candidate) / grid.CellSize;
            return steps <= straight * (ring <= 3 ? 1.5f : 2.5f) * 1.42f + 2f;
        }

        /// <summary>
        /// Greedy assignment: vehicles nearest the centre choose first and take the free slot
        /// closest to themselves. Vehicles left without a slot are not added to the result.
        /// </summary>
        public static void Assign(IReadOnlyList<Vehicle> units, List<Vector2> slots, Vector2 center,
            Dictionary<EntityId, Vector2> result)
        {
            result.Clear();
            var order = new List<Vehicle>(units);
            order.Sort((a, b) => Vector2.DistanceSquared(a.Position, center)
                .CompareTo(Vector2.DistanceSquared(b.Position, center)));
            var taken = new bool[slots.Count];
            foreach (var unit in order)
            {
                var best = -1;
                var bestDistance = float.MaxValue;
                for (var i = 0; i < slots.Count; i++)
                {
                    if (taken[i]) continue;
                    var d = Vector2.DistanceSquared(unit.Position, slots[i]);
                    if (d < bestDistance)
                    {
                        bestDistance = d;
                        best = i;
                    }
                }
                if (best < 0) continue;
                taken[best] = true;
                result[unit.Id] = slots[best];
            }
            Untangle(order, result);
        }

        /// <summary>
        /// Swaps two vehicles' slots wherever that shortens their two drives together: the greedy
        /// pick crosses paths, and two hulls sent to each other's slots met head-on and each queued
        /// behind the other (prompt 12). Two passes in a fixed order, so it stays deterministic; only
        /// for groups of up to 12 (the commanders re-send the whole army every decision, and pair by
        /// pair it doubled the tick's 99th percentile).
        /// </summary>
        private static void Untangle(List<Vehicle> order, Dictionary<EntityId, Vector2> result)
        {
            if (order.Count > UntangleMost) return;
            for (var pass = 0; pass < 2; pass++)
            {
                var swapped = false;
                for (var i = 0; i < order.Count; i++)
                {
                    if (!result.TryGetValue(order[i].Id, out var si)) continue;
                    for (var j = i + 1; j < order.Count; j++)
                    {
                        if (!result.TryGetValue(order[j].Id, out var sj)) continue;
                        var a = order[i].Position;
                        var b = order[j].Position;
                        var now = Vector2.Distance(a, si) + Vector2.Distance(b, sj);
                        var then = Vector2.Distance(a, sj) + Vector2.Distance(b, si);
                        if (then >= now - 0.5f) continue;
                        result[order[i].Id] = sj;
                        result[order[j].Id] = si;
                        si = sj;
                        swapped = true;
                    }
                }
                if (!swapped) break;
            }
        }

        /// <summary>The biggest group whose slots are untangled.</summary>
        private const int UntangleMost = 12;

        private static bool IsFree(List<Vector2> slots, Vector2 candidate, float minDistance)
        {
            foreach (var s in slots)
                if (Vector2.DistanceSquared(s, candidate) < minDistance * minDistance) return false;
            return true;
        }
    }
}
