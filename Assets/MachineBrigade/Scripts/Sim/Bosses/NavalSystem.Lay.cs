#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Play-test 14 ("Leviathan bắn trước khi súng quay xong"): a flagship's main turrets are trained, then fired. A real
    /// battleship's turret traverses at a few degrees a second and its salvo goes once the director has the guns on; the
    /// laid guns used to be set onto the aim in the same step as the shot, so the shells left while the drawn turret was
    /// still swinging round. Now the turrets traverse at the unit's turret rate (at least <see cref="LayRateMin"/>) onto the
    /// salvo's aim and <see cref="Salvo"/> fires once every standing turret is on it (or after <see cref="LayLongest"/>).
    /// Between salvos they follow the boss's current target inside their arcs, as fire control keeps them on.
    /// </summary>
    internal sealed partial class NavalSystem
    {
        /// <summary>Slowest traverse of a laid turret (radians a second; the view drew them at least this fast).</summary>
        private static readonly float LayRateMin = SimMath.DegToRad(global::MachineBrigade.Sim.Content.SimTunables.Bosses.NavalSystem.LayRateMinDegrees);

        /// <summary>How far off its aim a turret may still be when the salvo goes (radians).</summary>
        private static readonly float LayTolerance = SimMath.DegToRad(2f);

        /// <summary>The longest a salvo waits for its turrets (seconds): a jammed lay never stops the battery.</summary>
        private const double LayLongest = 10.0;

        /// <summary>Every step: each salvo-firing boss's standing main turrets traverse towards their aim.</summary>
        private void TrainLaid(float dt)
        {
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Def.Salvo == null) continue;
                var step = MathF.Max(LayRateMin, v.Def.TurretTurnRate) * v.TurretFactor * dt;
                if (v.Laying)
                {
                    foreach (var (part, mount, aim) in v.LayOrders)
                        if (!v.IsPartBroken(part)) Train(v, mount, SimMath.HeadingOf(aim - v.Position), step);
                    continue;
                }
                if (!_world.TryGetTarget(v.Target, out var target)) continue;
                var bearing = SimMath.HeadingOf(target.Position - v.Position);
                var parts = v.Def.Parts;
                for (var i = 0; i < parts.Count; i++)
                    if (parts[i].Kind == "maingun" && !v.IsPartBroken(i) && parts[i].Mounts.Count > 0) Train(v, parts[i].Mounts[0], bearing, step);
            }
        }

        /// <summary>Whether every standing turret of the salvo being laid is on its aim (or it has waited long enough).</summary>
        private bool LaidOn(Vehicle v, double now)
        {
            if (now - v.LayFrom >= LayLongest) return true;
            foreach (var (part, mount, aim) in v.LayOrders)
            {
                if (v.IsPartBroken(part)) continue;
                var want = InArc(v, mount, SimMath.HeadingOf(aim - v.Position));
                if (MathF.Abs(SimMath.WrapAngle(want - v.Weapons[mount].Heading)) > LayTolerance) return false;
            }
            return true;
        }

        /// <summary>Turns mount <paramref name="m"/> towards <paramref name="heading"/> (kept inside its arc) by at most <paramref name="step"/>.</summary>
        private static void Train(Vehicle v, int m, float heading, float step)
        {
            var state = v.Weapons[m];
            state.Heading = SimMath.RotateTowards(state.Heading, InArc(v, m, heading), step);
        }

        /// <summary>A heading kept inside mount <paramref name="m"/>'s own firing arc (as <see cref="Lay"/> keeps it).</summary>
        private static float InArc(Vehicle v, int m, float heading)
        {
            var mount = v.Def.Mounts[m];
            if (mount.ArcHalf <= 0f) return heading;
            var centre = v.Heading + mount.ArcCentre;
            return centre + Math.Clamp(SimMath.WrapAngle(heading - centre), -mount.ArcHalf, mount.ArcHalf);
        }
    }
}
