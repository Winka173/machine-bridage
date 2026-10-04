#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Bosses.BossBrain;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>A boss mount as the broadside controller sees it (spec 56, 104): where it can bear and what it is worth.</summary>
    internal readonly struct MountSample
    {
        public MountSample(MountAim aim, float arcCentre, float arcHalf, float dps, float minRange, float range, bool air, bool ground)
        {
            Aim = aim;
            ArcCentre = arcCentre;
            ArcHalf = arcHalf;
            Dps = dps;
            MinRange = minRange;
            Range = range;
            Air = air;
            Ground = ground;
        }

        public MountAim Aim { get; }

        /// <summary>Its own firing arc (radians from the bow, clockwise; half width); 0: none.</summary>
        public float ArcCentre { get; }
        public float ArcHalf { get; }
        public float Dps { get; }
        public float MinRange { get; }
        public float Range { get; }
        public bool Air { get; }
        public bool Ground { get; }
    }

    /// <summary>An enemy the broadside controller weighs: where, how big, in the air or not.</summary>
    internal readonly struct TargetSample
    {
        public TargetSample(Vector2 at, float radius, bool flying)
        {
            At = at;
            Radius = radius;
            Flying = flying;
        }

        public Vector2 At { get; }
        public float Radius { get; }
        public bool Flying { get; }
    }

    /// <summary>The route around a ship for the broadside's route penalty (spec 56 "does not break the route, keeps a safe lane").</summary>
    internal readonly struct RouteContext
    {
        public RouteContext(Vector2 seaward, float lateralError, float halfCorridor, float shoreRoom, float planningRadius,
            float roomIn = float.PositiveInfinity, float roomOut = float.PositiveInfinity)
        {
            Seaward = seaward;
            LateralError = lateralError;
            HalfCorridor = halfCorridor;
            ShoreRoom = shoreRoom;
            PlanningRadius = planningRadius;
            RoomIn = roomIn;
            RoomOut = roomOut;
        }

        /// <summary>
        /// Metres it may drift off the lane's line inshore / out to sea before its own escorts' slots (prompt 33 L4: kept
        /// beside the lane, not beside the hull) are too close: a broadside never closes on its own fleet.
        /// </summary>
        public float RoomIn { get; }
        public float RoomOut { get; }

        /// <summary>Unit vector out to sea (the coast frame's +w).</summary>
        public Vector2 Seaward { get; }

        /// <summary>Metres off the lane's line, + out to sea.</summary>
        public float LateralError { get; }

        public float HalfCorridor { get; }

        /// <summary>Metres of water between the hull's inshore side and the waterline.</summary>
        public float ShoreRoom { get; }

        public float PlanningRadius { get; }

        public static RouteContext Open => new(new Vector2(0f, 1f), 0f, 10f, 1000f, 0f);
    }

    /// <summary>
    /// AI MASTER P0-C (spec 51-60, 103-104): the naval boss's own steering (not the ground vehicles'). Each step, for a
    /// boss ship on the water (<see cref="NavalSystem"/> calls <see cref="Steer"/> from its Sail):
    /// <list type="number">
    /// <item>Route: a point on its lane line a look-ahead ahead (clamp(speed x 6, 1.5 L, 4 L), spec 54), or straight at a goal
    /// off the lanes (a passing bay); the mission controller's goal (patrol end, a phase's lane, the escape run) is the only
    /// thing it steers by. The target never steers the hull.</item>
    /// <item>Broadside (spec 56-57, 104): the brain's smoothed hull offset from the route (mount arcs x DPS x suitability over
    /// -80..+80; the brain's tick computes it, <see cref="ChooseOffset"/>), only on its lane, not running, not holding.</item>
    /// <item>Collision: a sinking wreck ahead (lane J), then the closest point of approach of any ship not of its own fleet
    /// within 6-10 s (spec 60): an early turn away and a slow-down, never waiting for the hulls to touch.</item>
    /// <item>No reverse (spec 52): a desired heading behind it becomes a forward turn to one side (spec 103's
    /// PerpendicularForwardChoice), kept until lined up; its speed is never below 0, and any reverse is counted
    /// (<see cref="BossBrains.NavalReverseEvents"/>, which the tests assert is 0).</item>
    /// <item>Turn law (spec 53): under way it turns no tighter than planningRadius = max(hull radius, 1.1 Rmin), Rmin = speed /
    /// angular speed; coming about for a goal behind it, or held up (traffic gap, wreck), it slows to a quarter of its speed
    /// and turns at its full rate: spec 52's "slow down, turn harder, stop short" (the sea maps' corners leave too little
    /// water past the far lane for a 2 Rmin circle, and the escorts' rule of prompt 33 L4 is built on a ship coming about
    /// where it is).</item>
    /// </list>
    /// </summary>
    internal static class NavalBossMovementController
    {
        // ================================================================== pure rules (the tests call these)

        /// <summary>Spec 53: Rmin = speed / angular speed (radians a second).</summary>
        internal static float MinTurnRadius(float speed, float turnRate) => speed / MathF.Max(0.01f, turnRate);

        /// <summary>Spec 53: planningRadius = max(collision radius, Rmin x 1.1).</summary>
        internal static float PlanningRadius(float collisionRadius, float minTurnRadius) => MathF.Max(collisionRadius, minTurnRadius * Tun.PlanningFactor);

        /// <summary>Spec 54: clamp(speed x 6, length x 1.5, length x 4).</summary>
        internal static float LookAhead(float speed, float length)
        {
            var lo = length * Tun.LookAheadMinLengths;
            var hi = MathF.Max(lo, length * Tun.LookAheadMaxLengths);
            return Math.Clamp(speed * Tun.LookAheadSeconds, lo, hi);
        }

        /// <summary>
        /// Spec 53, the planner's check: the turn rate allowed under way at <paramref name="speed"/> (radians a second), so the
        /// radius it turns on (speed / rate) is never under <paramref name="planningRadius"/> while it keeps its cruise share.
        /// </summary>
        internal static float CruiseTurnRate(float turnRate, float speed, float fullSpeed, float planningRadius) =>
            MathF.Min(turnRate, MathF.Max(speed, fullSpeed * Tun.CruiseThrottleMin) / MathF.Max(0.1f, planningRadius));

        /// <summary>Spec 55: a new value within <paramref name="band"/> of the held one keeps the held one.</summary>
        internal static float Deadband(float held, float wanted, float band) => MathF.Abs(SimMath.WrapAngle(wanted - held)) <= band ? held : wanted;

        /// <summary>Spec 52, 103: a heading behind the bow (more than 90 degrees off) becomes square to the side it lies on.</summary>
        internal static float ForwardOnly(float heading, float desired, int side)
        {
            var delta = SimMath.WrapAngle(desired - heading);
            if (MathF.Abs(delta) <= MathF.PI * 0.5f) return desired;
            var s = side != 0 ? side : delta >= 0f ? 1 : -1;
            return heading + s * MathF.PI * 0.5f;
        }

        /// <summary>Whether a mount can bear on <paramref name="at"/> with the hull on <paramref name="hullHeading"/> (its arc, its side, its bow).</summary>
        internal static bool CanBear(in MountSample m, Vector2 from, float hullHeading, Vector2 at)
        {
            var off = at - from;
            if (off.LengthSquared() < 1e-6f) return true;
            var relative = SimMath.WrapAngle(SimMath.HeadingOf(off) - hullHeading);
            if (m.ArcHalf > 0f) return MathF.Abs(SimMath.WrapAngle(relative - m.ArcCentre)) <= m.ArcHalf;
            return m.Aim switch
            {
                MountAim.Left => MathF.Abs(SimMath.WrapAngle(relative + MathF.PI * 0.5f)) <= MathF.PI / 3f,
                MountAim.Right => MathF.Abs(SimMath.WrapAngle(relative - MathF.PI * 0.5f)) <= MathF.PI / 3f,
                MountAim.Hull => MathF.Abs(relative) <= SimMath.DegToRad(12f),
                _ => true,
            };
        }

        /// <summary>
        /// Spec 202 / 104: the share of the DPS that has something to shoot at (in reach, of its layer) which bears with the hull
        /// on <paramref name="hullHeading"/>; 1 when nothing is in reach. <paramref name="relevantDps"/>: that DPS.
        /// </summary>
        internal static float BearingShare(IReadOnlyList<MountSample> mounts, Vector2 from, float hullHeading, IReadOnlyList<TargetSample> targets,
            out float relevantDps)
        {
            var bearing = 0f;
            var relevant = 0f;
            for (var i = 0; i < mounts.Count; i++)
            {
                var m = mounts[i];
                if (m.Dps <= 0f) continue;
                var any = false;
                var bears = false;
                for (var k = 0; k < targets.Count; k++)
                {
                    var t = targets[k];
                    if (!(t.Flying ? m.Air : m.Ground)) continue;
                    var d = Vector2.Distance(from, t.At);
                    if (d < m.MinRange || d - t.Radius > m.Range) continue;
                    any = true;
                    if (!CanBear(m, from, hullHeading, t.At)) continue;
                    bears = true;
                    break;
                }
                if (!any) continue;
                relevant += m.Dps;
                if (bears) bearing += m.Dps;
            }
            relevantDps = relevant;
            return relevant > 0f ? bearing / relevant : 1f;
        }

        /// <summary>Spec 56 "does not break the route": what a hull offset costs (leaving the lane, past the corridor, at the shore).</summary>
        internal static float RoutePenalty(float routeHeading, float offset, in RouteContext route)
        {
            var w = Tun.BroadsideRoutePenalty;
            var penalty = w * 0.5f * MathF.Abs(MathF.Sin(offset));
            var drift = Vector2.Dot(SimMath.Forward(routeHeading + offset), route.Seaward);
            if (drift * route.LateralError > 0f)
                penalty += w * 4f * MathF.Abs(drift) * SimMath.Clamp01(MathF.Abs(route.LateralError) / MathF.Max(1f, route.HalfCorridor));
            if (drift < 0f && route.ShoreRoom < route.PlanningRadius) penalty += w * 4f * -drift;
            // Its own escorts' slots on that side: no drift past the room they leave (prohibitive).
            if (drift < -0.05f && -route.LateralError >= route.RoomIn - 3f) penalty += w * 8f * -drift;
            if (drift > 0.05f && route.LateralError >= route.RoomOut - 3f) penalty += w * 8f * drift;
            return penalty;
        }

        /// <summary>
        /// Spec 56 / 104: the best hull offset from the route (radians), sampled -80..+80 by 20 degrees: the share of the DPS
        /// bearing (mount arcs x DPS x suitability) less the turn cost (spec 104's 0.08, at the widest offset) and the route
        /// penalty; the held offset gets a small bonus while it already bears the target share (spec 202: not a lock).
        /// Ties keep the smaller offset, the port side first (deterministic).
        /// </summary>
        internal static float ChooseOffset(IReadOnlyList<MountSample> mounts, Vector2 from, float routeHeading, IReadOnlyList<TargetSample> targets,
            in RouteContext route, float held, out float bestScore, out float bestShare)
        {
            var max = SimMath.DegToRad(MathF.Max(0f, Tun.BroadsideMaxDeg));
            var step = SimMath.DegToRad(MathF.Max(1f, Tun.BroadsideStepDeg));
            var steps = (int)MathF.Floor(max / step + 1e-3f);
            var best = 0f;
            bestScore = float.NegativeInfinity;
            bestShare = 0f;
            for (var k = 0; k <= steps * 2; k++)
            {
                // 0, -20, +20, -40, +40 ...
                var n = (k + 1) / 2;
                var offset = (k % 2 == 1 ? -1f : 1f) * n * step;
                var share = BearingShare(mounts, from, routeHeading + offset, targets, out _);
                var score = share - Tun.BroadsideTurnCost * MathF.Abs(offset) / MathF.Max(step, max) - RoutePenalty(routeHeading, offset, route);
                if (MathF.Abs(offset - held) < step * 0.5f && share >= Tun.ActiveDpsTarget) score += Tun.HoldBonus;
                if (score <= bestScore + 1e-4f) continue;
                bestScore = score;
                bestShare = share;
                best = offset;
            }
            return best;
        }

        /// <summary>
        /// Spec 57 + 55: the brain tick's broadside update: a new best offset is taken only past the deadband (5 degrees; 15
        /// once engaged), the steered offset eases to it by the smoothing (0.15), and the broadside is entered within 8 degrees
        /// of the hull and left only beyond 15.
        /// </summary>
        internal static void UpdateBroadside(BossBrain b, float candidate, float hullHeading)
        {
            b.BroadsideCandidate = candidate;
            var band = SimMath.DegToRad(b.BroadsideEngaged ? Tun.BroadsideLeaveDeg : Tun.HeadingDeadbandDeg);
            b.BroadsideHeld = Deadband(b.BroadsideHeld, candidate, band);
            b.BroadsideOffset += (b.BroadsideHeld - b.BroadsideOffset) * SimMath.Clamp01(Tun.BroadsideSmoothing);
            if (MathF.Abs(b.BroadsideOffset - b.BroadsideHeld) < 1e-3f) b.BroadsideOffset = b.BroadsideHeld;
            var error = MathF.Abs(SimMath.WrapAngle(hullHeading - (b.RouteHeading + b.BroadsideOffset)));
            if (!b.BroadsideEngaged && MathF.Abs(b.BroadsideHeld) > 1e-3f && error <= SimMath.DegToRad(Tun.BroadsideEnterDeg)) b.BroadsideEngaged = true;
            else if (b.BroadsideEngaged && (error > SimMath.DegToRad(Tun.BroadsideLeaveDeg) || MathF.Abs(b.BroadsideHeld) <= 1e-3f)) b.BroadsideEngaged = false;
        }

        /// <summary>Clears the broadside (off the lane, running, holding, coming about).</summary>
        internal static void ResetBroadside(BossBrain b)
        {
            b.BroadsideCandidate = 0f;
            b.BroadsideHeld = 0f;
            b.BroadsideOffset = 0f;
            b.BroadsideEngaged = false;
        }

        /// <summary>
        /// Spec 59: the separation two ships want: max(rA + rB + 4 m, half the longer hull), + 8-15 m when one is a boss
        /// (r: half the hull's width).
        /// </summary>
        internal static float Separation(VehicleDef a, VehicleDef b)
        {
            var s = MathF.Max(a.Width * 0.5f + b.Width * 0.5f + Tun.ShipSeparationExtra, 0.5f * MathF.Max(a.Length, b.Length));
            return a.Boss || b.Boss ? s + Tun.BossSeparationExtra : s;
        }

        /// <summary>Spec 60: the closest-approach time (0..horizon) of two ships and whether they are closing at all.</summary>
        internal static bool Cpa(Vector2 relPos, Vector2 relVel, float horizon, out float t)
        {
            var vv = relVel.LengthSquared();
            var closing = Vector2.Dot(relPos, relVel);
            t = vv < 1e-6f ? 0f : Math.Clamp(-closing / vv, 0f, horizon);
            return closing < 0f && vv >= 1e-6f;
        }

        /// <summary>Spec 60: the look-ahead of the closest-approach check, 6 s for a short ship up to 10 s for a long one.</summary>
        internal static float CpaHorizon(float length) =>
            Math.Clamp(Tun.CpaHorizonMin + (length - 30f) / 20f, Tun.CpaHorizonMin, MathF.Max(Tun.CpaHorizonMin, Tun.CpaHorizonMax));

        /// <summary>
        /// Spec 60: whether two hulls (spines along their headings, half widths round them) on their courses come closer than the
        /// lateral clearance, or in line inside the spec-59 separation, within the horizon. <paramref name="clearance"/>: the
        /// hulls' gap at the closest approach (m, negative: overlapping); <paramref name="across"/>: + the other passes on the
        /// right (starboard).
        /// </summary>
        internal static bool CollisionCourse(Vector2 pa, float ha, float va, VehicleDef a, Vector2 pb, float hb, float vb, VehicleDef b, float horizon,
            out float t, out float clearance, out float across)
        {
            var fa = SimMath.Forward(ha);
            var fb = SimMath.Forward(hb);
            var relPos = pb - pa;
            var relVel = fb * vb - fa * va;
            var closing = Cpa(relPos, relVel, horizon, out t);
            var qa = pa + fa * va * t;
            var qb = pb + fb * vb * t;
            var gap = BrainMath.SegmentDistance(qa - fa * a.HullHalf, qa + fa * a.HullHalf, qb - fb * b.HullHalf, qb + fb * b.HullHalf);
            clearance = gap - a.Width * 0.5f - b.Width * 0.5f;
            var right = new Vector2(fa.Y, -fa.X);
            across = Vector2.Dot(qb - qa, right);
            if (!closing) return false;
            if (clearance < Tun.CpaLateralClear) return true;
            // In line ahead (within 30 degrees of the bow) inside the spec-59 separation.
            var ahead = qb - qa;
            var l = ahead.Length();
            return l < Separation(a, b) && l > 1e-3f && Vector2.Dot(ahead / l, fa) > 0.866f && MathF.Abs(across) < (a.Width + b.Width) * 0.5f + Tun.CpaLateralClear;
        }

        // ================================================================== the step

        /// <summary>
        /// A boss ship's heading and speed this step (see the class summary). <paramref name="goal"/> / <paramref name="distance"/>:
        /// the mission controller's goal (world) and how far it is; <paramref name="full"/>: its speed now (escape included);
        /// <paramref name="round"/> / <paramref name="wreckTurn"/>: a sinking wreck ahead and the turn away from it (lane J).
        /// </summary>
        internal static void Steer(SimWorld world, Vehicle v, SeaDef sea, BossBrain b, Vector2 goal, float distance, float full, bool round, float wreckTurn, float dt)
        {
            var def = v.Def;
            var omegaData = MathF.Max(0.01f, def.TurnRate);
            var omega = MathF.Max(0.01f, def.TurnRate * v.TurnFactor);
            b.MinTurnRadius = MinTurnRadius(def.Speed, omegaData);
            b.PlanningRadius = PlanningRadius(def.HullRadius, b.MinTurnRadius);
            b.LookAhead = LookAhead(def.Speed, def.Length);

            // 1. The route (spec 54, 61): a point on the lane line ahead, or straight at a goal off the lanes.
            var route = RouteHeading(v, sea, b, goal);
            b.RouteHeading = route;
            var desired = route;
            var reason = v.Escaping ? HullReason.Escape : v.SeaHold >= 0 ? HullReason.Hold : b.MissionLocked ? HullReason.Phase : HullReason.Route;

            // 2. The broadside offset (spec 56-57), on its lane only.
            if (OnLane(v, sea) && !v.Escaping && v.SeaHold < 0 && b.TurnSide == 0)
            {
                desired += b.BroadsideOffset;
                if (MathF.Abs(b.BroadsideOffset) > SimMath.DegToRad(0.5f) && reason == HullReason.Route) reason = HullReason.Broadside;
            }

            // 3. Collisions: a sinking wreck (lane J), then the closest point of approach (spec 60).
            var blocked = round;
            var cpaThrottle = 1f;
            if (round)
            {
                desired += wreckTurn;
                reason = HullReason.Collision;
            }
            if (CpaThreat(world, v, b, out var side, out var urgency))
            {
                desired += side * SimMath.DegToRad(Tun.CpaMaxTurnDeg) * urgency;
                cpaThrottle = MathF.Max(Tun.CpaMinThrottle, 1f - urgency * (1f - Tun.CpaMinThrottle));
                reason = HullReason.Collision;
                blocked |= urgency > 0.5f;
            }

            // 4. Never reverse (spec 52, 58): a goal behind it is a forward turn to one side, kept until lined up.
            var delta = SimMath.WrapAngle(desired - v.Heading);
            var turnabout = false;
            if (MathF.Abs(delta) > MathF.PI * 0.5f)
            {
                if (b.TurnSide == 0)
                {
                    b.TurnSide = MathF.Abs(delta) > SimMath.DegToRad(170f) ? TurnaboutSide(world, v, sea) : delta >= 0f ? 1 : -1;
                    b.ReverseRequestsTurned++;
                }
                desired = ForwardOnly(v.Heading, desired, b.TurnSide);
                turnabout = true;
                if (reason is HullReason.Route or HullReason.Broadside) reason = HullReason.Turnabout;
            }
            else if (b.TurnSide != 0 && MathF.Abs(delta) < SimMath.DegToRad(60f)) b.TurnSide = 0;
            if (b.TurnSide != 0) ResetBroadside(b);
            blocked |= v.SeaCap < full * 0.5f;

            // 5. The turn law (spec 53): under way no tighter than the planning radius; coming about or held up, slow and hard.
            var rate = turnabout || blocked ? omega : CruiseTurnRate(omega, v.Speed, full, b.PlanningRadius);
            var before = v.Heading;
            v.Heading = SimMath.RotateTowards(v.Heading, desired, rate * dt);
            var turned = MathF.Abs(SimMath.WrapAngle(v.Heading - before));
            b.DesiredHullHeading = SimMath.WrapAngle(desired);
            b.ActualHeading = v.Heading;
            b.HullReason = reason;

            // 6. Speed: never below 0; slower to come about, for the traffic gap, a wreck and a predicted collision.
            var misalign = MathF.Abs(SimMath.WrapAngle(desired - v.Heading));
            var throttle = turnabout ? Tun.TurnaboutThrottle : MathF.Max(Tun.CruiseThrottleMin, MathF.Cos(MathF.Min(misalign, MathF.PI * 0.5f)));
            var target = full * throttle * MathF.Min(1f, distance / 8f + 0.2f);
            target = MathF.Min(target, v.SeaCap);
            if (round) target = MathF.Min(target, full * 0.5f);
            target = MathF.Min(target, full * cpaThrottle);
            v.Speed += Math.Clamp(target - v.Speed, -def.Speed * dt, def.Speed * 0.5f * dt);
            if (v.Speed < 0f)
            {
                // Never: counted so the tests can assert it (spec 52, section 110 "Target behind").
                world.Bosses.Brains.NavalReverseEvents++;
                v.Speed = 0f;
            }
            b.TurnRadius = turned > 1e-6f ? v.Speed * dt / turned : float.PositiveInfinity;
        }

        /// <summary>Spec 61: a ship on its lane (the goal on the lane's line: its patrol, a phase's new lane, the escape run's far lane).</summary>
        internal static bool OnLane(Vehicle v, SeaDef sea)
        {
            if (v.SeaHold >= 0) return false;
            if (v.Escaping) return true;
            return sea.Lane(v.NavalLane) is { } lane && MathF.Abs(v.NavalGoal.Y - lane.W) < 0.5f;
        }

        /// <summary>Spec 54: towards the point a look-ahead ahead on the goal's lane line (straight at a goal off the lanes).</summary>
        private static float RouteHeading(Vehicle v, SeaDef sea, BossBrain b, Vector2 goal)
        {
            Vector2 to;
            if (OnLane(v, sea))
            {
                var f = sea.Frame(v.Position);
                var g = v.NavalGoal;
                var du = g.X - f.X;
                var dir = MathF.Abs(du) > 0.01f ? MathF.Sign(du) : v.NavalDir;
                var ahead = sea.At(f.X + dir * MathF.Min(b.LookAhead, MathF.Abs(du)), g.Y);
                to = ahead - v.Position;
            }
            else to = goal - v.Position;
            return to.LengthSquared() > 1e-6f ? SimMath.HeadingOf(to) : v.Heading;
        }

        /// <summary>
        /// The side a ship comes about to when its goal is dead astern: out to sea, unless one of its escorts holds a slot out
        /// there and none inshore, or the shore is too near on that side (deterministic).
        /// </summary>
        private static int TurnaboutSide(SimWorld world, Vehicle v, SeaDef sea)
        {
            var seaward = Vector2.Dot(SimMath.Forward(v.Heading + MathF.PI * 0.5f), sea.Out) >= 0f ? 1 : -1;
            var outside = 0;
            var inside = 0;
            foreach (var o in world.VehicleList)
            {
                if (!o.IsAlive || o.Flagship != v.Id || !o.OnStation) continue;
                if (o.StationAt.Y > 0f) outside++;
                else inside++;
            }
            return outside > 0 && inside == 0 ? -seaward : seaward;
        }

        /// <summary>
        /// Spec 60: the most urgent ship (not of its own fleet) on a collision course within the horizon: the side to turn to
        /// (away from it; starboard when dead ahead) and the urgency (1 now, 0 at the horizon). Written to the brain's debug.
        /// </summary>
        private static bool CpaThreat(SimWorld world, Vehicle v, BossBrain b, out int side, out float urgency)
        {
            side = 0;
            urgency = 0f;
            b.CpaThreat = EntityId.None;
            b.CpaTime = 0f;
            b.CpaDistance = 0f;
            var horizon = CpaHorizon(v.Def.Length);
            var bestT = float.MaxValue;
            foreach (var o in world.VehicleList)
            {
                if (o == v || !o.IsAlive || o.Def.Naval == null || o.Escaped || o.Burrow != Vehicle.BurrowState.Surface) continue;
                // Its own fleet keeps its slots (prompt 33 L4); a landing craft coming home is hoisted in alongside.
                if (o.Flagship == v.Id) continue;
                if (Vector2.DistanceSquared(o.Position, v.Position) > MathF.Pow(v.Def.Length + o.Def.Length + (v.Def.Speed + o.Def.Speed) * horizon, 2f)) continue;
                if (!CollisionCourse(v.Position, v.Heading, v.Speed, v.Def, o.Position, o.Heading, o.Speed, o.Def, horizon, out var t, out var clearance, out var across))
                    continue;
                if (t >= bestT) continue;
                bestT = t;
                b.CpaThreat = o.Id;
                b.CpaTime = t;
                b.CpaDistance = clearance;
                side = across > 0.5f ? -1 : 1;
                urgency = SimMath.Clamp01(1f - t / MathF.Max(0.1f, horizon));
            }
            return b.CpaThreat.IsValid;
        }
    }

    /// <summary>AI MASTER P0-C: small geometry for the boss brain (segment distances).</summary>
    internal static class BrainMath
    {
        /// <summary>Distance from <paramref name="p"/> to the segment a-b.</summary>
        internal static float DistanceToSegment(Vector2 p, Vector2 a, Vector2 b)
        {
            var ab = b - a;
            var l = ab.LengthSquared();
            var t = l < 1e-8f ? 0f : SimMath.Clamp01(Vector2.Dot(p - a, ab) / l);
            return Vector2.Distance(p, a + ab * t);
        }

        /// <summary>Distance between the segments a0-a1 and b0-b1 (0 when they cross).</summary>
        internal static float SegmentDistance(Vector2 a0, Vector2 a1, Vector2 b0, Vector2 b1)
        {
            if (Cross(a0, a1, b0, b1)) return 0f;
            return MathF.Min(MathF.Min(DistanceToSegment(a0, b0, b1), DistanceToSegment(a1, b0, b1)),
                MathF.Min(DistanceToSegment(b0, a0, a1), DistanceToSegment(b1, a0, a1)));
        }

        private static bool Cross(Vector2 a0, Vector2 a1, Vector2 b0, Vector2 b1)
        {
            static float Side(Vector2 p, Vector2 q, Vector2 r) => (q.X - p.X) * (r.Y - p.Y) - (q.Y - p.Y) * (r.X - p.X);
            var d1 = Side(b0, b1, a0);
            var d2 = Side(b0, b1, a1);
            var d3 = Side(a0, a1, b0);
            var d4 = Side(a0, a1, b1);
            return ((d1 > 0f && d2 < 0f) || (d1 < 0f && d2 > 0f)) && ((d3 > 0f && d4 < 0f) || (d3 < 0f && d4 > 0f));
        }
    }
}
