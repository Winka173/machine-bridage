#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// Turns orders into driving: follows paths, closes in on attack targets, handles
    /// arrival and getting stuck, and keeps hulls from overlapping. The traffic rules between
    /// friends (making way, head-on meetings, routing round parked hulls) are in
    /// MovementSystem.Traffic.cs.
    /// </summary>
    internal sealed partial class MovementSystem
    {
        private const float ArriveWaypoint = 1.6f;
        private const float ArriveFinal = 0.8f;
        private const float RepathInterval = 0.5f;
        private const float StuckWindow = 1.5f;
        private const float StuckDistance = 0.4f;

        /// <summary>Driving this far in one stuck window counts as progress even when it is not towards the waypoint (going round something).</summary>
        private const float StuckDetourDistance = 3f;

        /// <summary>A hull stuck this close to its goal (plus its own size) among others has arrived.</summary>
        private const float ArrivalReach = 5f;

        /// <summary>Stuck windows before a vehicle gives up its route: two routed round parked hulls, one backing off, then this.</summary>
        private const int StuckStrikesToGiveUp = 4;
        private const float SeparationSlack = 0.05f;

        /// <summary>A destination this close that lies beside or behind the hull counts as reached.</summary>
        private const float SettleDistance = 2.5f;

        /// <summary>Within this distance of its destination a hovering aircraft slides straight onto it.</summary>
        private const float HoverSlide = 6f;

        /// <summary>How long a detour round a blocker lasts after it was last seen, and how far it turns.</summary>
        private const double AvoidSeconds = 0.9;

        private const float AvoidAngle = 0.8f;

        /// <summary>Misalignment a driver ignores rather than turn for (radians, about 2.3 degrees).</summary>
        private const float HeadingDeadBand = 0.04f;
        private const float SeparationStiffness = 0.55f;

        /// <summary>Largest push per step, so a deep overlap resolves over a few steps instead of a jump.</summary>
        private const float MaxPush = 0.35f;

        /// <summary>How far an idle vehicle will drive from its post to fight.</summary>
        private const float GuardLeash = 16f;

        /// <summary>How long an idle vehicle remembers who shot it.</summary>
        private const float AnswerFireSeconds = 5f;

        /// <summary>After finishing a hand-given order, a vehicle stays out of the commander AI's hands this long.</summary>
        public const float ManualHoldSeconds = 20f;

        private readonly SimWorld _world;

        public MovementSystem(SimWorld world)
        {
            _world = world;
            _unitCosts = new Navigation.UnitCostField(world.Grid);
            _costFinder = new Navigation.PathFinder(world.Grid);
        }

        /// <summary>Living ground vehicles sorted by X, for the neighbour searches of avoidance and separation.</summary>
        private readonly List<Vehicle> _ground = new();

        private float _maxBound;

        public void Step(float dt)
        {
            SortGround();
            // Requests posted last step are served now, before anyone drives: two-phase, so no
            // outcome depends on the order vehicles are driven in.
            ServeHeadOns();
            ServeYieldRequests();
            PrepareGates();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                // Fixed defences only turn their guns (the combat system does that).
                if (v.Def.Static) continue;
                // A boss boring underground or landing troops: the boss system moves it (or holds it still).
                if (v.Burrow != Vehicle.BurrowState.Surface || v.Landing)
                {
                    v.Speed = 0f;
                    continue;
                }
                v.RepathTimer -= dt;
                if (!v.Flying) TrackTraffic(v);
                // Making way or backing out for a friend: the order waits (it is taken up again after).
                if (!TrafficOverlay(v)) UpdateOrder(v);
                if (v.ManualOrder && v.Order.Kind == OrderKind.Idle)
                {
                    v.ManualOrder = false;
                    v.ManualUntil = _world.Time + ManualHoldSeconds;
                }
                Drive(v, dt);
            }
            ResolveGates();
            RunPathQueue();
            SortGround();
            Separate();
        }

        /// <summary>
        /// Keeps <see cref="_ground"/> sorted by X. Positions change little between steps, so an
        /// insertion sort over the nearly sorted list is linear and allocates nothing.
        /// </summary>
        private void SortGround()
        {
            _ground.Clear();
            _maxBound = 0f;
            foreach (var v in _world.VehicleList)
            {
                // Underground, it is in nobody's way.
                if (!v.IsAlive || v.Flying || v.Burrowed) continue;
                _ground.Add(v);
                if (v.Def.HullBound > _maxBound) _maxBound = v.Def.HullBound;
            }
            for (var i = 1; i < _ground.Count; i++)
            {
                var item = _ground[i];
                var j = i - 1;
                while (j >= 0 && _ground[j].Position.X > item.Position.X)
                {
                    _ground[j + 1] = _ground[j];
                    j--;
                }
                _ground[j + 1] = item;
            }
        }

        /// <summary>First index in <see cref="_ground"/> whose X is at least <paramref name="x"/>.</summary>
        private int LowerBound(float x)
        {
            int lo = 0, hi = _ground.Count;
            while (lo < hi)
            {
                var mid = (lo + hi) >> 1;
                if (_ground[mid].Position.X < x) lo = mid + 1;
                else hi = mid;
            }
            return lo;
        }

        /// <summary>The ends of a vehicle's collision capsule spine.</summary>
        private static void Spine(Vehicle v, out Vector2 a, out Vector2 b)
        {
            var half = SimMath.Forward(v.Heading) * v.Def.HullHalf;
            a = v.Position - half;
            b = v.Position + half;
        }

        /// <summary>Closest points between segments p1-q1 and p2-q2 (Ericson, Real-Time Collision Detection 5.1.9).</summary>
        private static void ClosestPoints(Vector2 p1, Vector2 q1, Vector2 p2, Vector2 q2, out Vector2 c1, out Vector2 c2)
        {
            var d1 = q1 - p1;
            var d2 = q2 - p2;
            var r = p1 - p2;
            var a = Vector2.Dot(d1, d1);
            var e = Vector2.Dot(d2, d2);
            var f = Vector2.Dot(d2, r);
            float s, t;
            if (a <= 1e-6f && e <= 1e-6f)
            {
                c1 = p1;
                c2 = p2;
                return;
            }
            if (a <= 1e-6f)
            {
                s = 0f;
                t = Math.Clamp(f / e, 0f, 1f);
            }
            else
            {
                var c = Vector2.Dot(d1, r);
                if (e <= 1e-6f)
                {
                    t = 0f;
                    s = Math.Clamp(-c / a, 0f, 1f);
                }
                else
                {
                    var b = Vector2.Dot(d1, d2);
                    var denominator = a * e - b * b;
                    s = denominator > 1e-6f ? Math.Clamp((b * f - c * e) / denominator, 0f, 1f) : 0f;
                    t = (b * s + f) / e;
                    if (t < 0f)
                    {
                        t = 0f;
                        s = Math.Clamp(-c / a, 0f, 1f);
                    }
                    else if (t > 1f)
                    {
                        t = 1f;
                        s = Math.Clamp((b - c) / a, 0f, 1f);
                    }
                }
            }
            c1 = p1 + d1 * s;
            c2 = p2 + d2 * t;
        }

        /// <summary>
        /// The nearest ground vehicle whose hull the driver would run into within
        /// <paramref name="reach"/> metres ahead, or null.
        /// </summary>
        private Vehicle? Blocker(Vehicle v, Vector2 forward, float reach)
        {
            var front = v.Position + forward * v.Def.HullHalf;
            var probe = v.Position + forward * (v.Def.HullHalf + reach);
            var width = v.Def.HullRadius * 0.85f;
            var span = v.Def.HullBound + reach + _maxBound;
            Vehicle? nearest = null;
            var nearestAhead = float.MaxValue;
            for (var i = LowerBound(v.Position.X - span); i < _ground.Count; i++)
            {
                var o = _ground[i];
                if (o.Position.X > v.Position.X + span) break;
                if (o == v || !o.IsAlive) continue;
                var offset = o.Position - v.Position;
                var ahead = Vector2.Dot(offset, forward);
                if (ahead <= 0f || ahead > nearestAhead) continue;
                Spine(o, out var oa, out var ob);
                ClosestPoints(front, probe, oa, ob, out var c1, out var c2);
                if (Vector2.DistanceSquared(c1, c2) >= Square(width + o.Def.HullRadius)) continue;
                nearest = o;
                nearestAhead = ahead;
            }
            return nearest;
        }

        private static float Square(float x) => x * x;

        private void UpdateOrder(Vehicle v)
        {
            // Relocating (the SP gun's shoot-and-scoot): it drives to its new spot whatever the
            // order says, then takes the order up again from there.
            if (v.Relocating)
            {
                if (v.HasPath || v.PathQueued) return;
                v.Relocating = false;
                if (v.Order.Kind == OrderKind.Idle) v.GuardPoint = v.Position;
            }
            switch (v.Order.Kind)
            {
                case OrderKind.Move:
                case OrderKind.Retreat:
                    // Arrived (a route still waiting for its step is not an arrival).
                    if (v.PathCompleted && !v.PathQueued) v.SetOrder(Order.Idle);
                    break;

                case OrderKind.Attack:
                    if (!_world.TryGetTarget(v.Order.Target, out var target) || !target.IsAlive)
                    {
                        v.SetOrder(Order.Idle);
                        v.ClearPath();
                        break;
                    }
                    CloseIn(v, target);
                    break;

                case OrderKind.AttackMove:
                    UpdateAttackMove(v);
                    break;

                case OrderKind.Idle:
                    UpdateGuard(v);
                    break;
            }
        }

        /// <summary>
        /// Idle vehicles defend their post instead of standing still while being shot: they close
        /// in on enemies they can see, and on whoever just hit them, within a short leash, then
        /// drive back once the area is clear. Artillery keeps its position, since it already
        /// out-ranges everything, and harmless vehicles have nothing to fight with.
        /// </summary>
        private void UpdateGuard(Vehicle v)
        {
            if (!v.Flying)
            {
                // Never idle in a gate, a gap or their mouths (a post there would close the way for
                // everyone): stand beside it, and make that the post.
                var lanes = _world.Lanes;
                if (!v.HasPath && v.RepathTimer <= 0f && lanes.NoParkAt(v.Position) && TryStandBeside(v.Position, 16f, out var aside))
                {
                    v.GuardPoint = aside;
                    _world.PathTo(v, aside);
                    return;
                }
                if (lanes.NoParkAt(v.GuardPoint) && TryStandBeside(v.GuardPoint, 16f, out var post)) v.GuardPoint = post;
            }
            var weapon = v.Def.Weapon;
            if (weapon.MinRange > 0f || weapon.Damage <= 0f) return;
            if (v.Def.FixedWing)
            {
                // Aeroplanes circle their post and pick fights from there (see DriveAeroplane).
                var nearby = GuardThreat(v);
                v.Engaged = nearby?.Id ?? EntityId.None;
                return;
            }

            var threat = GuardThreat(v);
            var fromPost = Vector2.Distance(v.Position, v.GuardPoint);
            if (threat != null && fromPost <= GuardLeash + 4f)
            {
                v.Engaged = threat.Id;
                CloseIn(v, threat);
                return;
            }

            v.Engaged = EntityId.None;
            if (fromPost > 2f && !v.HasPath && v.RepathTimer <= 0f) _world.PathTo(v, v.GuardPoint);
        }

        /// <summary>
        /// Only anti-aircraft vehicles go after aircraft. Everything else shoots at one that comes
        /// into reach but never drives after it: a helicopter circling a tank would otherwise lead
        /// it round in circles (a machine gun can hit aircraft, so it counted as a target to chase).
        /// </summary>
        private static bool HuntsAircraft(Vehicle v) => Combat.CombatSystem.IsAntiAir(v.Def.Weapon);

        private Vehicle? GuardThreat(Vehicle v)
        {
            // Only threats that can be fought without leaving the leash, so the vehicle never
            // swings back and forth at its edge.
            var weapon = v.Def.Weapon;
            // A fighter on combat air patrol reaches out much further for enemy aircraft.
            var reach = GuardLeash + weapon.Range * (v.Def.Interceptor ? 2.4f : 0.9f);
            if (_world.Time - v.LastHitTime < AnswerFireSeconds && _world.TryGetVehicle(v.LastAttacker, out var attacker) &&
                attacker.IsAlive && !attacker.Invulnerable && attacker.IsVisibleTo(v.Team) && weapon.CanTarget(attacker.Flying) && (!attacker.Flying || HuntsAircraft(v)) &&
                Vector2.Distance(attacker.Position, v.GuardPoint) - attacker.Radius <= reach)
                return attacker;

            Vehicle? best = null;
            var bestDistance = float.MaxValue;
            foreach (var other in _world.VehicleList)
            {
                if (!other.IsAlive || other.Team == v.Team || !other.IsVisibleTo(v.Team) || !weapon.CanTarget(other.Flying)) continue;
                if ((other.Flying && !HuntsAircraft(v)) || other.Invulnerable) continue;
                if (v.Def.Interceptor && !other.Flying) continue;
                var distance = Vector2.Distance(v.Position, other.Position);
                if (distance > MathF.Max(v.Def.VisionRange, v.Def.Interceptor ? reach : 0f) || distance >= bestDistance) continue;
                if (Vector2.Distance(other.Position, v.GuardPoint) - other.Radius > reach) continue;
                best = other;
                bestDistance = distance;
            }
            return best;
        }

        private void UpdateAttackMove(Vehicle v)
        {
            var weapon = v.Def.Weapon;
            // (A fixed defence does not come for it: only vehicles make it take cover.)
            if (weapon.Targets == TargetLayers.Air && !v.Flying &&
                _world.FindNearestEnemy(v, v.Def.VisionRange * 0.7f, requireVisible: true, layers: TargetLayers.Ground, mobileOnly: true) != null)
            {
                // Anti-aircraft missiles cannot fight tanks: hold behind the line while ground enemies
                // are close, turning only on aircraft.
                var aircraft = _world.FindNearestEnemy(v, MathF.Max(v.Def.VisionRange, weapon.Range), requireVisible: true,
                    minRange: weapon.MinRange, layers: weapon.Targets);
                if (aircraft != null)
                {
                    v.Engaged = aircraft.Id;
                    CloseIn(v, aircraft);
                }
                else
                {
                    StayBehindArmour(v);
                }
                v.ResumeRoute = true;
                return;
            }
            var enemy = _world.FindNearestEnemy(v, MathF.Max(v.Def.VisionRange, weapon.Range), requireVisible: true,
                minRange: weapon.MinRange, layers: HuntsAircraft(v) ? weapon.Targets : weapon.Targets & TargetLayers.Ground);
            if (enemy != null)
            {
                v.Engaged = enemy.Id;
                v.ResumeRoute = true;
                CloseIn(v, enemy);
                return;
            }

            v.Engaged = EntityId.None;
            if (v.ResumeRoute)
            {
                v.ResumeRoute = false;
                if (!KeepCostedPath(v, v.Order.Point)) _world.PathTo(v, v.Order.Point);
            }
            else if (v.PathCompleted && !v.PathQueued)
            {
                v.SetOrder(Order.Idle);
            }
        }

        /// <summary>
        /// An anti-aircraft vehicle that cannot fight the tanks ahead keeps a few metres behind the
        /// nearest friendly ground unit that can (its umbrella moves with the army), instead of
        /// freezing on the spot; with none near, it holds where it is.
        /// </summary>
        private void StayBehindArmour(Vehicle v)
        {
            Vehicle? escort = null;
            var nearest = 30f;
            foreach (var other in _world.VehicleList)
            {
                if (other == v || !other.IsAlive || other.Team != v.Team || other.Flying || other.Def.Static) continue;
                if (other.Def.Weapon.Targets == TargetLayers.Air || other.Def.Weapon.MinRange > 0f) continue;
                var d = Vector2.Distance(other.Position, v.Position);
                if (d >= nearest) continue;
                nearest = d;
                escort = other;
            }
            if (escort == null)
            {
                v.ClearPath();
                return;
            }
            var threat = _world.FindNearestEnemy(escort, v.Def.VisionRange, requireVisible: true, layers: TargetLayers.Ground);
            var back = threat != null ? escort.Position - threat.Position : v.Position - escort.Position;
            back = back.LengthSquared() > 0.01f ? Vector2.Normalize(back) : SimMath.Forward(escort.Heading + MathF.PI);
            var spot = escort.Position + back * (escort.Def.HullBound + v.Def.HullBound + 5f);
            if (_world.Lanes.NoParkAt(spot) && TryStandBeside(spot, 10f, out var beside)) spot = beside;
            if (Vector2.Distance(spot, v.Position) < 4f)
            {
                v.ClearPath();
                return;
            }
            if (v.RepathTimer <= 0f && (!v.HasPath || Vector2.Distance(v.PathGoal, spot) > 4f))
            {
                v.RepathTimer = RepathInterval * 2f;
                _world.PathTo(v, _world.ClampToMap(spot));
            }
        }

        /// <summary>
        /// A standoff helicopter (the Ka-52): it holds between 60 % and 92 % of its missiles' reach
        /// from the target while no known enemy anti-air it outranges can reach it, and otherwise
        /// moves round the target to the spot on that ring furthest out of such guns' reach
        /// (smallest turn first). Anti-air that reaches as far as its missiles is not avoided:
        /// there is no standing outside it.
        /// </summary>
        private bool Standoff(Vehicle v, IDamageable target)
        {
            var reach = v.Def.Weapon.Range;
            var distance = Vector2.Distance(v.Position, target.Position) - target.Radius;
            _shortAa.Clear();
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying || !e.IsVisibleTo(v.Team)) continue;
                var aa = 0f;
                foreach (var m in e.Def.Mounts)
                    if (m.Weapon.CanTarget(true)) aa = MathF.Max(aa, m.Weapon.Range);
                if (aa > 0f && aa < reach - 2f) _shortAa.Add((e.Position, aa));
            }
            float Exposure(Vector2 at)
            {
                var worst = 0f;
                foreach (var (p, r) in _shortAa) worst += MathF.Max(0f, r + StandoffMargin - Vector2.Distance(at, p));
                return worst;
            }
            // The best spot on two rings round the target (82 % and 95 % of reach), smallest turn first.
            var bearing = SimMath.HeadingOf(v.Position - target.Position);
            var best = v.Position;
            var bestExposure = float.MaxValue;
            var bestScore = float.MaxValue;
            foreach (var share in Rings)
            {
                var ring = reach * share + target.Radius;
                for (var k = -4; k <= 4; k++)
                {
                    var spot = _world.ClampToMap(target.Position + SimMath.Forward(bearing + k * SimMath.DegToRad(22.5f)) * ring);
                    var exposure = Exposure(spot);
                    var score = exposure * 10f + MathF.Abs(k);
                    if (score >= bestScore) continue;
                    bestScore = score;
                    bestExposure = exposure;
                    best = spot;
                }
            }
            // In the band and no better placed anywhere on the rings: hold and fire.
            if (distance <= reach * 0.97f && distance >= reach * 0.6f && Exposure(v.Position) <= bestExposure + 0.5f &&
                _world.HasLineOfFire(v, target, v.Def.Weapon))
            {
                v.ClearPath();
                return true;
            }
            if (v.RepathTimer > 0f && v.HasPath) return true;
            v.RepathTimer = RepathInterval;
            _world.PathTo(v, best);
            return true;
        }

        private static readonly float[] Rings = { 0.82f, 0.95f };

        /// <summary>Metres a standoff helicopter keeps beyond the reach of anti-air it outranges.</summary>
        private const float StandoffMargin = 5f;

        private readonly List<(Vector2 at, float reach)> _shortAa = new();

        /// <summary>Holds position once in range; otherwise (re)paths towards the target.</summary>
        private void CloseIn(Vehicle v, IDamageable target)
        {
            if (v.Flying && v.Def.Standoff && Standoff(v, target)) return;
            var weapon = v.Def.Weapon;
            var distance = Vector2.Distance(v.Position, target.Position) - target.Radius;
            if (weapon.MinRange > 0f && distance < weapon.MinRange + 1f)
            {
                if (v.RepathTimer > 0f && v.HasPath) return;
                v.RepathTimer = RepathInterval;
                // Back off by the best way out; cornered, hold and let the machine gun fight.
                if (_world.EscapeRoute(v, target.Position, weapon.MinRange + 8f - distance) is { } escape) _world.PathTo(v, escape);
                return;
            }
            // In range and in the clear: hold here. In range but behind cover: keep driving (the
            // path leads round the building or rock) until the line of fire opens.
            var clear = _world.HasLineOfFire(v, target, weapon);
            if (distance <= weapon.Range * 0.9f && clear)
            {
                // Never stop in the doorway, nor in the road with friends coming up behind: step
                // off to the side first (a short drive; the turret keeps firing), or roll on through
                // a gate to the first place it may stop.
                if (!v.Flying && InTheWay(v, out var noPark))
                {
                    if (v.HasPath && _world.Time < v.Traffic.OffLaneUntil) return;
                    if (v.RepathTimer <= 0f && TryOffLaneSpot(v, target, out var spot))
                    {
                        _world.PathTo(v, spot);
                        v.RepathTimer = RepathInterval * 3f;
                        v.Traffic.OffLaneUntil = _world.Time + OffLaneSeconds;
                        return;
                    }
                    if (noPark)
                    {
                        if (!v.HasPath && v.RepathTimer <= 0f && TryStandBeside(v.Position, 16f, out var beside))
                        {
                            _world.PathTo(v, beside);
                            v.Traffic.OffLaneUntil = _world.Time + OffLaneSeconds;
                        }
                        return;
                    }
                }
                v.ClearPath();
                return;
            }
            // A fixed defence's ground is closed to routes, so a route ends a few metres short of it:
            // a weapon of very short reach (a car bomb's charge) drives the last metres straight at it.
            if (!v.Flying && !v.HasPath && target is Vehicle { BlocksRoutes: true } && distance <= weapon.Range + 4f)
            {
                _single.Clear();
                _single.Add(target.Position);
                v.SetPath(_single, target.Position);
                v.RepathTimer = RepathInterval;
                return;
            }
            var goalDrift = Vector2.Distance(v.PathGoal, target.Position);
            if (v.RepathTimer <= 0f && (!v.HasPath || goalDrift > 4f || (!clear && v.PathCompleted)))
            {
                v.RepathTimer = RepathInterval;
                // A route just planned round parked hulls is kept a moment (it would be planned straight back through them).
                if (goalDrift <= 10f && KeepCostedPath(v, v.PathGoal)) return;
                _world.PathTo(v, target.Position);
            }
        }

        private void Drive(Vehicle v, float dt)
        {
            var def = v.Def;
            if (v.Stunned)
            {
                v.Speed = 0f;
                return;
            }
            if (def.FixedWing)
            {
                DriveAeroplane(v, dt);
                return;
            }
            if (!def.Flying)
            {
                // Backing out of a doorway for a friend, or waiting beside its mouth afterwards.
                if (v.Traffic.Reversing(_world.Time))
                {
                    DriveReverse(v, dt);
                    return;
                }
                if (_world.Time < v.Traffic.HoldUntil)
                {
                    v.Speed = SimMath.MoveTowards(v.Speed, 0f, def.Speed * 2f * dt);
                    TryAdvance(v, v.Speed * dt);
                    return;
                }
            }
            if (!v.HasPath)
            {
                v.Traffic.WaitingOnYield = false;
                v.Traffic.WaitingForGate = false;
                v.Speed = SimMath.MoveTowards(v.Speed, 0f, def.Speed * 2f * dt);
                TryAdvance(v, v.Speed * dt);
                // Hovering aircraft turn to face their target so hull-mounted rockets and missiles bear.
                if (def.Mounts[0].Aim == MountAim.Hull && _world.TryGetTarget(v.Target, out var target) &&
                    (def.Flying || target is not Vehicle { Flying: true }))
                    v.Heading = SimMath.RotateTowards(v.Heading, SimMath.HeadingOf(target.Position - v.Position), def.TurnRate * v.TurnFactor * dt);
                return;
            }

            var waypoint = v.Path[v.PathIndex];
            var isFinal = v.PathIndex == v.Path.Count - 1;
            var toWaypoint = waypoint - v.Position;
            var distance = toWaypoint.Length();
            // Aircraft keep apart in the air, so a flight sent to one point spreads round it: when
            // others of the flight crowd the destination, anywhere within their own size of it is there.
            var arrive = isFinal ? (def.Flying && CrowdedInAir(v, waypoint) ? ArriveFinal + v.Radius * 0.9f : ArriveFinal) : ArriveWaypoint;
            if (distance <= arrive)
            {
                Vehicle.PathTrace?.Invoke(v, $"Arrive {v.PathIndex}/{v.Path.Count} d{distance:0.0}");
                v.PathIndex++;
                if (!v.HasPath) v.PathCompleted = true;
                return;
            }
            if (def.Flying && isFinal && distance < HoverSlide)
            {
                // A helicopter slides the last metres sideways rather than turning: with a slow
                // turn it could otherwise circle its destination for ever.
                v.Speed = SimMath.MoveTowards(v.Speed, MathF.Min(def.Speed * v.SpeedFactor, MathF.Max(1f, distance * 1.2f)), def.Speed * 2f * dt);
                var slide = toWaypoint / distance * MathF.Min(distance, v.Speed * dt);
                if (_world.Map.Contains(v.Position + slide)) v.Position += slide;
                return;
            }

            var desired = SimMath.HeadingOf(toWaypoint);
            var slowFor = float.MaxValue;
            var wasWaiting = v.Traffic.WaitingOnYield;
            v.Traffic.WaitingOnYield = false;
            if (!def.Flying && distance > 1.5f)
            {
                // A short doorway held by traffic the other way: wait short of it (one way at a time).
                GateCheck(v, toWaypoint / distance, ref slowFor);
                // Look ahead for a hull in the way. Follow a friend going the same way; steer round
                // anything parked, crossing or hostile instead of shoving into it.
                var forward = SimMath.Forward(v.Heading);
                var blocker = Blocker(v, forward, 1.2f + v.Speed * 0.7f);
                // Convoy trucks and bosses have right of way over their own side: the others
                // make room (they yield far more), so these keep to their route.
                if (blocker != null && blocker.Team == v.Team && (v.Scripted || v.Def.Boss)) blocker = null;
                if (blocker != null) NoteBlocker(v, blocker);
                // A parked friend in the way is asked to make way; while it does, crawl straight on
                // behind it rather than swerve (see MovementSystem.Traffic).
                if (blocker != null && blocker.Team == v.Team && !blocker.Def.Static && Negotiate(v, blocker, forward, wasWaiting, ref slowFor))
                    blocker = null;
                if (blocker != null)
                {
                    var sameWay = Vector2.Dot(SimMath.Forward(blocker.Heading), forward) > 0.4f;
                    if (blocker.Team == v.Team && blocker.IsMoving && sameWay) slowFor = blocker.Speed * 0.9f;
                    else
                    {
                        // Steer away from the side the blocker is on (headings turn clockwise), and
                        // keep the choice a moment so the hull does not weave. Oncoming traffic
                        // always passes on the right, so two drivers never both dodge into each other.
                        if (_world.Time >= v.AvoidUntil)
                        {
                            var offset = blocker.Position - v.Position;
                            var onLeft = forward.X * offset.Y - forward.Y * offset.X > 0f;
                            var oncoming = blocker.IsMoving && Vector2.Dot(SimMath.Forward(blocker.Heading), forward) < -0.5f;
                            v.AvoidSide = oncoming || onLeft ? 1f : -1f;
                        }
                        v.AvoidUntil = _world.Time + AvoidSeconds;
                        slowFor = def.Speed * 0.5f;
                    }
                }
            }
            // The detour fades out over a moment after the way last looked blocked. Dropping it
            // the instant the blocker leaves the look-ahead turned the hull straight back at it,
            // then away again: a wag every few steps.
            if (!def.Flying && _world.Time < v.AvoidUntil)
                desired += v.AvoidSide * AvoidAngle * (float)Math.Min(1.0, (v.AvoidUntil - _world.Time) / (AvoidSeconds * 0.5));
            var misalignment = MathF.Abs(SimMath.WrapAngle(desired - v.Heading));
            if (isFinal && distance < SettleDistance && MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(toWaypoint) - v.Heading)) > 1.2f)
            {
                // The destination is beside or behind the hull and only a few metres off: close
                // enough. Driving on would only circle it (a slow-turning tank cannot tighten
                // its turn under the final-approach speed), which reads as a hull going round
                // and round.
                Vehicle.PathTrace?.Invoke(v, $"Settle d{distance:0.0}");
                v.PathIndex++;
                v.PathCompleted = true;
                return;
            }
            // Close to the final point, small corrections would swing the hull back and forth:
            // hold the heading and let the vehicle roll in. While cruising, slivers of
            // misalignment (a shove from a neighbour shifting the bearing a degree) are not worth
            // a turn; a vehicle slowed or stopped (against a wall corner) always corrects.
            var cruising = v.Speed > def.Speed * 0.3f;
            if ((!isFinal || distance > 2.5f || misalignment > 0.6f) && (def.Flying || !cruising || misalignment > HeadingDeadBand))
                v.Heading = SimMath.RotateTowards(v.Heading, desired, def.TurnRate * v.TurnFactor * dt);

            // Slow right down for sharp turns so tanks pivot instead of drawing wide arcs.
            var alignment = MathF.Cos(MathF.Min(misalignment, MathF.PI * 0.5f));
            var targetSpeed = def.Speed * v.SpeedFactor * MathF.Max(alignment, def.Flying ? 0.4f : 0.15f);
            // Roll in slowly, and pivot (tracks can turn on the spot) rather than orbit the point.
            if (isFinal) targetSpeed = MathF.Min(targetSpeed, MathF.Max(misalignment > 0.6f ? 0.3f : 1.5f, distance * 1.5f));
            targetSpeed = MathF.Min(targetSpeed, slowFor);
            var acceleration = def.Speed / (targetSpeed > v.Speed ? 1.2f : 0.5f);
            v.Speed = SimMath.MoveTowards(v.Speed, targetSpeed, acceleration * dt);

            if (!TryAdvance(v, v.Speed * dt) && (def.Flying || !Sidestep(v, SimMath.HeadingOf(toWaypoint), dt))) v.Speed = 0f;
            if (!def.Flying) DetectStuck(v, dt);
        }

        /// <summary>
        /// Aeroplanes never stop. With a target they fly at it, fire as it bears, pull through
        /// past it and extend, then turn in for another run; with a destination they fly there;
        /// otherwise they circle their post. They turn back well before the map edge.
        /// </summary>
        private void DriveAeroplane(Vehicle v, float dt)
        {
            var def = v.Def;
            var turnRadius = def.Speed / def.TurnRate;
            var target = RunTarget(v);
            if (target != null && def.Vtol && Hover(v, target, dt)) return;
            Vector2 goal;
            var throttle = 1f;
            var half = _world.Map.HalfSize;
            var margin = turnRadius * 1.3f + 4f;
            var circling = false;
            if (target != null && def.Orbit)
            {
                // A gunship's pylon turn: round and round the target, anticlockwise so it stays on
                // the left where the guns are, far enough out to see it and to stay clear of the
                // short-range anti-aircraft round it. The circle is kept inside the map (a target
                // near the edge is circled from the inside), and its centre glides to a new target
                // at a few metres a second, so the turn never jerks.
                var radius = MathF.Max(turnRadius * 1.15f, def.Weapon.Range * 0.62f);
                var limit = MathF.Max(0f, half - radius - 4f);
                var want = new Vector2(Math.Clamp(target.Position.X, -limit, limit), Math.Clamp(target.Position.Y, -limit, limit));
                if (!v.Orbiting)
                {
                    v.OrbitCentre = want;
                    v.Orbiting = true;
                }
                var shift = want - v.OrbitCentre;
                var glide = OrbitGlide * dt;
                v.OrbitCentre = shift.LengthSquared() <= glide * glide ? want : v.OrbitCentre + Vector2.Normalize(shift) * glide;
                goal = OrbitAround(v, v.OrbitCentre, radius);
                circling = true;
            }
            else if (target != null)
            {
                var range = def.Weapon.Range;
                var toTarget = target.Position - v.Position;
                var distance = toTarget.Length();
                if (!v.RunExtending)
                {
                    // Pull through once too close to keep the nose on it, or once it slips behind.
                    var behind = Vector2.Dot(SimMath.Forward(v.Heading), toTarget) < 0f;
                    if (distance < MathF.Max(6f, range * 0.3f) || (behind && distance < range * 0.6f)) v.RunExtending = true;
                }
                else if (distance > MathF.Max(range * 0.85f, turnRadius * 2.2f))
                {
                    v.RunExtending = false;
                }
                goal = v.RunExtending ? v.Position + SimMath.Forward(v.Heading) * 10f : target.Position;
                // Throttle back through the attack run for more time on the target; full power to
                // extend and come round.
                if (!v.RunExtending && distance < range * 1.1f) throttle = 0.8f;
            }
            else if (v.HasPath)
            {
                goal = v.Path[v.Path.Count - 1];
                if (Vector2.Distance(v.Position, goal) < MathF.Max(8f, turnRadius))
                {
                    v.PathIndex = v.Path.Count;
                    v.PathCompleted = true;
                }
            }
            else
            {
                goal = OrbitPoint(v, MathF.Max(14f, turnRadius * 1.6f));
            }

            if (!circling) v.Orbiting = false;
            // Turn back towards the middle before running out of map (a pylon turn is already
            // kept inside it; turning it back as well made it jerk between the two).
            var nearEdge = MathF.Abs(v.Position.X) > half - margin || MathF.Abs(v.Position.Y) > half - margin;
            if (!circling && nearEdge && Vector2.Dot(SimMath.Forward(v.Heading), v.Position) > 0f) goal = Vector2.Zero;

            v.Heading = SimMath.RotateTowards(v.Heading, SimMath.HeadingOf(goal - v.Position), def.TurnRate * v.TurnFactor * dt);
            v.Speed = SimMath.MoveTowards(v.Speed, def.Speed * v.SpeedFactor * throttle, def.Speed * 0.8f * dt);
            v.Position = _world.ClampToMap(v.Position + SimMath.Forward(v.Heading) * v.Speed * dt);
        }

        /// <summary>How fast the centre of a pylon turn follows its target, in metres a second.</summary>
        private const float OrbitGlide = 6f;

        /// <summary>Seconds a VTOL jet holds in the air to shoot, and how long before it can again.</summary>
        private const double HoverSeconds = 6.0, HoverRest = 12.0;

        /// <summary>
        /// A VTOL jet (Harrier, F-35B) with a target in reach stops in the air, turns on the spot to
        /// keep its nose and guns on it, then flies on: the hover is short, since a hovering jet is
        /// slow, loud and easy to hit. True while it is holding.
        /// </summary>
        private bool Hover(Vehicle v, IDamageable target, float dt)
        {
            var def = v.Def;
            var now = _world.Time;
            var distance = Vector2.Distance(v.Position, target.Position);
            // Never stop dead inside an anti-aircraft gun's reach (a boss's flak): fire from outside it.
            var flak = UnderFlak(v);
            if (flak && now < v.HoverUntil) v.HoverUntil = now;
            if (!flak && now >= v.HoverUntil && now >= v.HoverReadyAt && distance < def.Weapon.Range * 0.8f && distance > 6f)
            {
                v.HoverUntil = now + HoverSeconds;
                v.HoverReadyAt = v.HoverUntil + HoverRest;
            }
            if (now >= v.HoverUntil) return false;
            v.Speed = SimMath.MoveTowards(v.Speed, 0f, def.Speed * 1.1f * dt);
            v.Heading = SimMath.RotateTowards(v.Heading, SimMath.HeadingOf(target.Position - v.Position), def.TurnRate * v.TurnFactor * 1.3f * dt);
            v.Position = _world.ClampToMap(v.Position + SimMath.Forward(v.Heading) * v.Speed * dt);
            // Leaving the hover, it flies straight out before turning back in.
            if (now + dt >= v.HoverUntil) v.RunExtending = true;
            return true;
        }

        /// <summary>An enemy anti-aircraft gun (not a guided missile) has this aircraft within its reach and a little more.</summary>
        private bool UnderFlak(Vehicle v)
        {
            foreach (var other in _world.VehicleList)
            {
                if (!other.IsAlive || other.Team == v.Team || other.Team < 0) continue;
                var d2 = Vector2.DistanceSquared(other.Position, v.Position);
                foreach (var mount in other.Def.Mounts)
                {
                    var w = mount.Weapon;
                    if (w.Guided || !w.CanTarget(true) || !Combat.CombatSystem.IsAntiAir(w)) continue;
                    var reach = w.Range + 6f;
                    if (d2 < reach * reach) return true;
                }
            }
            return false;
        }

        /// <summary>A point ahead on an anticlockwise circle of <paramref name="radius"/> round <paramref name="centre"/> (the centre kept on the left).</summary>
        private static Vector2 OrbitAround(Vehicle v, Vector2 centre, float radius)
        {
            var from = v.Position - centre;
            var distance = from.Length();
            var outward = distance > 0.1f ? from / distance : SimMath.Forward(v.Heading);
            var tangent = new Vector2(-outward.Y, outward.X);
            var pull = Math.Clamp((radius - distance) / radius, -1f, 1f) * 1.4f;
            var direction = Vector2.Normalize(tangent + outward * pull);
            return v.Position + direction * 10f;
        }

        /// <summary>The strafing-run target: an ordered one, else the current or last engaged enemy.</summary>
        private IDamageable? RunTarget(Vehicle v)
        {
            if (v.Order.Kind is OrderKind.Move or OrderKind.Retreat)
            {
                v.RunTarget = EntityId.None;
                return null;
            }
            if (v.Order.Kind == OrderKind.Attack && _world.TryGetTarget(v.Order.Target, out var ordered) && ordered.IsAlive)
                return ordered;
            var weapon = v.Def.Weapon;
            if (_world.TryGetVehicle(v.RunTarget, out var run) && run.IsAlive && !run.Invulnerable && run.IsVisibleTo(v.Team) &&
                weapon.CanTarget(run.Flying) && Vector2.Distance(run.Position, v.Position) < weapon.Range * 2.5f)
                return run;
            v.RunExtending = false;
            if (_world.TryGetVehicle(v.Target, out var current) && current.IsAlive)
            {
                v.RunTarget = current.Id;
                return current;
            }
            if (_world.TryGetVehicle(v.Engaged, out var engaged) && engaged.IsAlive && engaged.IsVisibleTo(v.Team))
            {
                v.RunTarget = engaged.Id;
                return engaged;
            }
            v.RunTarget = EntityId.None;
            return null;
        }

        /// <summary>A point ahead on a circle of <paramref name="radius"/> around the post.</summary>
        private static Vector2 OrbitPoint(Vehicle v, float radius)
        {
            var from = v.Position - v.GuardPoint;
            var distance = from.Length();
            var outward = distance > 0.1f ? from / distance : SimMath.Forward(v.Heading);
            var tangent = new Vector2(-outward.Y, outward.X);
            var pull = Math.Clamp((radius - distance) / radius, -1f, 1f) * 1.2f;
            var direction = Vector2.Normalize(tangent + outward * pull);
            return v.Position + direction * 10f;
        }

        /// <summary>
        /// The way straight ahead is blocked (a wall corner, a wreck, the edge of the map's
        /// outline, often after a shove or a detour turned the hull into it): edge along the
        /// nearest free bearing towards the waypoint, turning the hull with it, instead of standing
        /// pressed against the obstacle until the stuck check gives up on the route.
        /// </summary>
        private bool Sidestep(Vehicle v, float towards, float dt)
        {
            // Still swinging round towards the waypoint: pivot on the spot first (tracks can).
            if (MathF.Abs(SimMath.WrapAngle(v.Heading - towards)) > 0.6f) return false;
            var step = MathF.Max(v.Speed, v.Def.Speed * 0.3f) * dt;
            var probe = MathF.Max(1.5f, v.Def.HullRadius + 0.5f);
            // Keep to the side chosen a moment ago (else the side the hull leans to), so it edges
            // one way round the obstacle instead of hesitating between the two.
            var lean = _world.Time < v.SlideUntil ? v.SlideSide : SimMath.WrapAngle(v.Heading - towards) >= 0f ? 1f : -1f;
            for (var k = 0; k <= 6; k++)
            {
                for (var side = 0; side < (k == 0 ? 1 : 2); side++)
                {
                    var bearing = towards + (side == 0 ? lean : -lean) * k * 0.35f;
                    var direction = SimMath.Forward(bearing);
                    if (!_world.Grid.IsWalkable(v.Position + direction * probe) || HullNear(v, v.Position + direction * probe)) continue;
                    if (!TryPlace(v, v.Position + direction * step)) continue;
                    v.Heading = SimMath.RotateTowards(v.Heading, bearing, v.Def.TurnRate * v.TurnFactor * dt);
                    v.Speed = MathF.Min(MathF.Max(v.Speed, v.Def.Speed * 0.3f), v.Def.Speed * 0.6f);
                    if (k > 0)
                    {
                        v.SlideSide = side == 0 ? lean : -lean;
                        v.SlideUntil = _world.Time + 1.5;
                    }
                    return true;
                }
            }
            return false;
        }

        /// <summary>Another ground vehicle's hull covers <paramref name="point"/> (as far as this hull reaches).</summary>
        private bool HullNear(Vehicle v, Vector2 point)
        {
            var reach = v.Def.HullRadius + _maxBound;
            for (var i = LowerBound(point.X - reach); i < _ground.Count; i++)
            {
                var o = _ground[i];
                if (o.Position.X > point.X + reach) break;
                if (o == v || !o.IsAlive) continue;
                Spine(o, out var a, out var b);
                ClosestPoints(point, point, a, b, out _, out var c);
                if (Vector2.DistanceSquared(point, c) < Square(v.Def.HullRadius + o.Def.HullRadius)) return true;
            }
            return false;
        }

        /// <summary>
        /// A free spot a few metres away, in the open and in plain line to it, from which the next
        /// waypoint is in plain line too if possible: where a hull wedged against something backs
        /// off to before it tries again.
        /// </summary>
        private bool TryDetour(Vehicle v, Vector2 next, out Vector2 detour)
        {
            detour = default;
            var best = float.MaxValue;
            var grid = _world.Grid;
            for (var ring = 1; ring <= 2; ring++)
            for (var k = 0; k < 16; k++)
            {
                var p = v.Position + SimMath.Forward(k * SimMath.Tau / 16f) * (2.5f * ring + v.Def.HullRadius);
                if (!_world.Map.Contains(p) || !grid.IsWalkable(p) || !grid.LineOfSight(v.Position, p)) continue;
                var score = Vector2.Distance(p, next) + (grid.LineOfSight(p, next) ? 0f : 12f);
                if (score >= best) continue;
                best = score;
                detour = p;
            }
            return best < float.MaxValue;
        }

        private bool TryAdvance(Vehicle v, float distance)
        {
            if (distance <= 0f) return true;
            var next = v.Position + SimMath.Forward(v.Heading) * distance;
            if (!_world.Map.Contains(next) || (!v.Flying && !_world.Grid.IsWalkable(next))) return false;
            v.Position = next;
            return true;
        }

        /// <summary>
        /// Measures progress over a time window rather than per frame, so healthy movement is
        /// never misjudged at high frame rates. Asks a friend in the way to move, repaths twice
        /// (round the parked hulls), backs off, then gives up (V2 R05).
        /// </summary>
        private void DetectStuck(Vehicle v, float dt)
        {
            v.StuckTimer += dt;
            if (v.StuckTimer < StuckWindow || !v.HasPath) return;
            // Progress is getting closer to the waypoint, not merely moving: a hull edging back
            // and forth against a corner (or creeping sideways along it) moves every step and gets
            // nowhere, and used to pass the check for ever. A new waypoint, or a real stretch of
            // driving (round an obstacle), counts too.
            var toWaypoint = Vector2.Distance(v.Position, v.Path[v.PathIndex]);
            var moved = Vector2.Distance(v.Position, v.StuckSample);
            // (A new route every few seconds changes the waypoint without the hull going anywhere.)
            var progressed = moved >= StuckDetourDistance ||
                             (moved >= StuckDistance && (v.PathIndex != v.StuckWaypoint || v.StuckWaypointDistance - toWaypoint >= StuckDistance));
            v.StuckWaypoint = v.PathIndex;
            v.StuckWaypointDistance = toWaypoint;
            v.StuckSample = v.Position;
            v.StuckTimer = 0f;
            if (progressed)
            {
                v.StuckStrikes = 0;
                v.Traffic.YieldEscalations = 0;
                v.Traffic.TrafficBoost = 0;
                return;
            }

            // Waiting behind a friend that is making way (OpenRA's "the cell is being evacuated"),
            // or queued behind one where there is no way round: waiting is not being stuck.
            var traffic = v.Traffic;
            if (traffic.WaitingOnYield && _world.Time - traffic.WaitStarted < YieldWaitSeconds) return;
            if (traffic.WaitingForGate && _world.Time - traffic.GateWaitStarted < GateWaitMax) return;
            if (StillQueued(v)) return;

            // Arrival contagion (as in StarCraft II's movement): on the last leg, within a few metres
            // of the goal and pressed against other hulls already there, it has arrived. Pushing on
            // for the exact spot only keeps the whole group shuffling. Never in a doorway, though:
            // "arriving" there closes the way for everyone.
            if (v.PathIndex == v.Path.Count - 1 && Vector2.Distance(v.Position, v.PathGoal) < ArrivalReach + v.Def.HullBound && Crowded(v) &&
                !_world.Lanes.NoParkAt(v.Position))
            {
                v.ClearPath();
                v.StuckStrikes = 0;
                if (v.Order.Kind == OrderKind.Idle) v.GuardPoint = v.Position;
                return;
            }
            // Ask the friend in the way again, then route round the parked hulls, then back off,
            // then give up (MovementSystem.Traffic).
            OnNoProgress(v);
        }

        /// <summary>Queued behind a hull with no way round, and it is still there ahead: keep waiting, and keep asking it to move.</summary>
        private bool StillQueued(Vehicle v)
        {
            var t = v.Traffic;
            if (!t.QueueBehind.IsValid) return false;
            if (_world.Time < t.QueueUntil && _world.TryGetVehicle(t.QueueBehind, out var ahead) && ahead.IsAlive &&
                Vector2.Distance(ahead.Position, v.Position) < ahead.Def.HullBound + v.Def.HullBound + 8f)
            {
                PostYield(v, ahead, 0);
                return true;
            }
            t.QueueBehind = EntityId.None;
            return false;
        }

        /// <summary>The last rung of the stuck ladder: drop the route, and at least move out of a knot so the others can pass.</summary>
        private void GiveUp(Vehicle v)
        {
            v.ClearPath();
            var clear = v.Position;
            var unjammed = Crowded(v) && TryUnjam(v, out clear);
            if (unjammed) _world.PathTo(v, clear);
            // Guarding a post it cannot reach (another hull is parked on it): the post moves to
            // where it can stand, instead of it pushing back towards it for ever (never into a doorway).
            if (v.Order.Kind != OrderKind.Idle) return;
            var post = unjammed ? clear : v.Position;
            if (_world.Lanes.NoParkAt(post) && TryStandBeside(post, 16f, out var beside)) post = beside;
            v.GuardPoint = post;
        }

        /// <summary>Other ground hulls pressed close round this one.</summary>
        private bool Crowded(Vehicle v)
        {
            var reach = v.Def.HullBound * 2f + 1.5f;
            foreach (var other in _ground)
                if (other != v && other.IsAlive && Vector2.DistanceSquared(other.Position, v.Position) < reach * reach) return true;
            return false;
        }

        /// <summary>
        /// A random open spot 3.5 to 6 m away with the most room round it (walkable, inside the
        /// map, clear of other hulls): a step aside out of a jam.
        /// </summary>
        private bool TryUnjam(Vehicle v, out Vector2 spot)
        {
            spot = default;
            var bestRoom = 2.5f;
            var start = (float)_world.Random.NextDouble() * SimMath.Tau;
            for (var k = 0; k < 10; k++)
            {
                var angle = start + k * (SimMath.Tau / 10f);
                var reach = 3.5f + 2.5f * (float)_world.Random.NextDouble();
                var p = _world.ClampToMap(v.Position + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * reach);
                if (!_world.Map.Contains(p) || !_world.Grid.IsWalkable(p)) continue;
                var room = float.MaxValue;
                foreach (var other in _ground)
                    if (other != v && other.IsAlive) room = MathF.Min(room, Vector2.Distance(other.Position, p) - other.Def.HullBound);
                if (room <= bestRoom) continue;
                bestRoom = room;
                spot = p;
            }
            return bestRoom > 2.5f;
        }

        /// <summary>
        /// Pushes overlapping hulls apart. Ground vehicles collide as capsules along their
        /// heading (a tank is long and narrow, not a disc); parked vehicles yield more than moving
        /// ones, and fixed defences do not yield at all. Aircraft keep apart from each other only.
        /// </summary>
        private void Separate()
        {
            for (var i = 0; i < _ground.Count; i++)
            {
                var a = _ground[i];
                var reach = a.Def.HullBound + _maxBound;
                Spine(a, out var a0, out var a1);
                for (var j = i + 1; j < _ground.Count; j++)
                {
                    var b = _ground[j];
                    if (b.Position.X - a.Position.X > reach) break;
                    var bound = a.Def.HullBound + b.Def.HullBound;
                    if (Vector2.DistanceSquared(a.Position, b.Position) >= bound * bound) continue;
                    Spine(b, out var b0, out var b1);
                    ClosestPoints(a0, a1, b0, b1, out var ca, out var cb);
                    Push(a, b, cb - ca, a.Def.HullRadius + b.Def.HullRadius);
                }
            }

            var list = _world.VehicleList;
            for (var i = 0; i < list.Count; i++)
            {
                var a = list[i];
                if (!a.IsAlive || !a.Flying) continue;
                for (var j = i + 1; j < list.Count; j++)
                {
                    var b = list[j];
                    if (!b.IsAlive || !b.Flying) continue;
                    Push(a, b, b.Position - a.Position, a.Radius + b.Radius);
                }
            }
        }

        private void Push(Vehicle a, Vehicle b, Vector2 delta, float minimum)
        {
            var distanceSquared = delta.LengthSquared();
            if (distanceSquared >= minimum * minimum) return;

            Vector2 normal;
            float distance;
            if (distanceSquared < 1e-6f)
            {
                normal = SimMath.Forward((a.Id.Value * 2.39996f) % SimMath.Tau);
                distance = 0f;
            }
            else
            {
                distance = MathF.Sqrt(distanceSquared);
                normal = delta / distance;
            }

            // Resolve only part of the overlap per step and ignore slivers: full correction every
            // step makes packed groups shove each other back and forth (visible jitter).
            var overlap = MathF.Min((minimum - distance - SeparationSlack) * SeparationStiffness, MaxPush);
            if (overlap <= 0f) return;
            var weightA = Yield(a);
            var weightB = Yield(b);
            var total = weightA + weightB;
            if (total <= 0f) return;
            // Whoever cannot move (a wall behind it) passes its share to the other.
            var movedA = weightA > 0f && Nudge(a, -normal * (overlap * weightA / total));
            var movedB = weightB > 0f && Nudge(b, normal * (overlap * weightB / total));
            if (!movedA && weightB > 0f) Nudge(b, normal * (overlap * weightA / total));
            if (!movedB && weightA > 0f) Nudge(a, -normal * (overlap * weightB / total));
            Brake(a, -normal, weightA / total);
            Brake(b, normal, weightB / total);
        }

        /// <summary>
        /// A driver shoved back against its direction of travel eases off the throttle, instead
        /// of ramming straight back in next step: driving in and being pushed out at 20 Hz is
        /// what made packed hulls vibrate. Only as much as it is actually shoved (its
        /// <paramref name="share"/> of the push): a convoy truck or a boss that the others
        /// make way for keeps its speed and pushes through.
        /// </summary>
        private static void Brake(Vehicle v, Vector2 push, float share)
        {
            if (v.Flying || v.Speed <= 0f || share < 0.2f) return;
            var against = -Vector2.Dot(SimMath.Forward(v.Heading), push);
            if (against > 0.3f) v.Speed *= 1f - 0.5f * MathF.Min(1f, against) * share;
        }

        /// <summary>How readily a vehicle gives way: parked more than moving, bosses hardly, defences never.</summary>
        private static float Yield(Vehicle v)
        {
            if (v.Def.Static) return 0f;
            var weight = v.HasPath ? 0.3f : 0.7f;
            return v.Def.Boss || v.Scripted ? weight * 0.1f : weight;
        }

        /// <summary>Another aircraft of the same side is hovering close enough to <paramref name="point"/> to keep this one off it.</summary>
        private bool CrowdedInAir(Vehicle v, Vector2 point)
        {
            foreach (var other in _world.VehicleList)
            {
                if (other == v || !other.IsAlive || !other.Flying || other.Team != v.Team) continue;
                var reach = other.Radius + v.Radius;
                if (Vector2.DistanceSquared(other.Position, point) < reach * reach) return true;
            }
            return false;
        }

        /// <summary>Moves a vehicle by <paramref name="offset"/>, or slides it along a wall; false if it cannot move at all.</summary>
        private bool Nudge(Vehicle v, Vector2 offset)
        {
            if (TryPlace(v, v.Position + offset)) return true;
            // Blocked: slide along whichever axis is still free.
            return TryPlace(v, v.Position + new Vector2(offset.X, 0f)) || TryPlace(v, v.Position + new Vector2(0f, offset.Y));
        }

        private bool TryPlace(Vehicle v, Vector2 next)
        {
            if (!_world.Map.Contains(next) || (!v.Flying && !_world.Grid.IsWalkable(next))) return false;
            v.Position = next;
            return true;
        }
    }
}
