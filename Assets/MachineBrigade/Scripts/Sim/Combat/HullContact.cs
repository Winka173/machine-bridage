using System;
using System.Numerics;
using MachineBrigade.Sim.Content;

#nullable enable

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Play-test 6 (DECISIONS 21F): where a round fired straight at a big target meets its hull. The hull is the
    /// footprint the data gives (length along the heading, width across: a capsule, round at the ends), and a round
    /// coming from a point meets it where the line from that point to the target's middle crosses its edge, so a
    /// missile at a boss, a big ship, a large aircraft or a big structure bursts on its side, not in its middle.
    /// The simulation places the blast there; the view flies the missile there.
    /// </summary>
    public static class HullContact
    {
        /// <summary>Below this reach from the middle to the edge a target counts as small: its middle is close enough.</summary>
        public const float BigFrom = 4f;

        /// <summary>A hull that big (a boss always is).</summary>
        public static bool Big(VehicleDef def) => def.Boss || Edge(def) + def.HullHalf >= BigFrom;

        /// <summary>The hull's half width: the capsule's radius.</summary>
        public static float Edge(VehicleDef def) => MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Weapons.HullContact.EdgeWidthFloor, def.Width * 0.5f);

        /// <summary>
        /// The point on the edge of a capsule (spine <paramref name="half"/> either way of <paramref name="centre"/>
        /// along <paramref name="heading"/>, radius <paramref name="radius"/>) where the line from
        /// <paramref name="from"/> to its middle crosses it; the middle when <paramref name="from"/> is inside.
        /// </summary>
        public static Vector2 On(Vector2 centre, float heading, float half, float radius, Vector2 from)
        {
            if (Inside(centre, heading, half, radius, from)) return centre;
            // The edge lies between the shooter (outside) and the middle (inside): halve the way to it.
            float outT = 0f, inT = 1f;
            for (var i = 0; i < 18; i++)
            {
                var mid = (outT + inT) * 0.5f;
                if (Inside(centre, heading, half, radius, Vector2.Lerp(from, centre, mid))) inT = mid;
                else outT = mid;
            }
            return Vector2.Lerp(from, centre, inT);
        }

        /// <summary>Where a round from <paramref name="from"/> meets a vehicle's hull (its middle for a small one).</summary>
        public static Vector2 On(VehicleDef def, Vector2 centre, float heading, Vector2 from) =>
            Big(def) ? On(centre, heading, def.HullHalf, Edge(def), from) : centre;

        private static bool Inside(Vector2 centre, float heading, float half, float radius, Vector2 p)
        {
            var axis = new Vector2(MathF.Sin(heading), MathF.Cos(heading));
            var along = Math.Clamp(Vector2.Dot(p - centre, axis), -half, half);
            return Vector2.DistanceSquared(p, centre + axis * along) <= radius * radius;
        }
    }
}
