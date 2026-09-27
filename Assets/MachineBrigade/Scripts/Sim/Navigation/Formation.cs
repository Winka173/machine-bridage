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
        /// buildings): a group sent there stops beside it, where it does not close the way.
        /// </summary>
        public static List<Vector2> Slots(Vector2 center, int count, float spacing, NavGrid grid, LaneMap? lanes = null)
        {
            var slots = new List<Vector2>(count);
            if (count <= 0) return slots;
            if (grid.TryNearestWalkable(center, 16, out var first))
            {
                if (lanes != null && lanes.NoParkAt(first) && lanes.TryParkable(first, 12f, out var beside)) first = beside;
                slots.Add(first);
            }

            for (var ring = 1; slots.Count < count && ring <= 24; ring++)
            {
                var around = 6 * ring;
                for (var k = 0; k < around && slots.Count < count; k++)
                {
                    var angle = k * SimMath.Tau / around + ring * 0.5f;
                    var candidate = center + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (ring * spacing);
                    if (!grid.IsWalkable(candidate) || !IsFree(slots, candidate, spacing * 0.8f)) continue;
                    if (lanes != null && lanes.NoParkAt(candidate)) continue;
                    slots.Add(candidate);
                }
            }
            return slots;
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
        }

        private static bool IsFree(List<Vector2> slots, Vector2 candidate, float minDistance)
        {
            foreach (var s in slots)
                if (Vector2.DistanceSquared(s, candidate) < minDistance * minDistance) return false;
            return true;
        }
    }
}
