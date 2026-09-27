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
    /// arrival and getting stuck, and keeps hulls from overlapping.
    /// </summary>
    internal sealed class MovementSystem
    {
        private const float ArriveWaypoint = 1.6f;
        private const float ArriveFinal = 0.8f;
        private const float RepathInterval = 0.5f;
        private const float StuckWindow = 1.5f;
        private const float StuckDistance = 0.4f;
        private const int StuckStrikesToGiveUp = 3;
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

        public MovementSystem(SimWorld world) => _world = world;

        /// <summary>Living ground vehicles sorted by X, for the neighbour searches of avoidance and separation.</summary>
        private readonly List<Vehicle> _ground = new();

        private float _maxBound;

        public void Step(float dt)
        {
            SortGround();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                // Fixed defences only turn their guns (the combat system does that).
                if (v.Def.Static) continue;
                v.RepathTimer -= dt;
                UpdateOrder(v);
                if (v.ManualOrder && v.Order.Kind == OrderKind.Idle)
                {
                    v.ManualOrder = false;
                    v.ManualUntil = _world.Time + ManualHoldSeconds;
                }
                Drive(v, dt);
            }
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
                if (!v.IsAlive || v.Flying) continue;
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
            switch (v.Order.Kind)
            {
                case OrderKind.Move:
                case OrderKind.Retreat:
                    if (v.PathCompleted) v.SetOrder(Order.Idle);
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
            var reach = GuardLeash + weapon.Range * 0.9f;
            if (_world.Time - v.LastHitTime < AnswerFireSeconds && _world.TryGetVehicle(v.LastAttacker, out var attacker) &&
                attacker.IsAlive && attacker.IsVisibleTo(v.Team) && weapon.CanTarget(attacker.Flying) && (!attacker.Flying || HuntsAircraft(v)) &&
                Vector2.Distance(attacker.Position, v.GuardPoint) - attacker.Radius <= reach)
                return attacker;

            Vehicle? best = null;
            var bestDistance = float.MaxValue;
            foreach (var other in _world.VehicleList)
            {
                if (!other.IsAlive || other.Team == v.Team || !other.IsVisibleTo(v.Team) || !weapon.CanTarget(other.Flying)) continue;
                if (other.Flying && !HuntsAircraft(v)) continue;
                var distance = Vector2.Distance(v.Position, other.Position);
                if (distance > v.Def.VisionRange || distance >= bestDistance) continue;
                if (Vector2.Distance(other.Position, v.GuardPoint) - other.Radius > reach) continue;
                best = other;
                bestDistance = distance;
            }
            return best;
        }

        private void UpdateAttackMove(Vehicle v)
        {
            var weapon = v.Def.Weapon;
            if (weapon.Targets == TargetLayers.Air && !v.Flying &&
                _world.FindNearestEnemy(v, v.Def.VisionRange * 0.7f, requireVisible: true, layers: TargetLayers.Ground) != null)
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
                _world.PathTo(v, v.Order.Point);
            }
            else if (v.PathCompleted)
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

        /// <summary>Holds position once in range; otherwise (re)paths towards the target.</summary>
        private void CloseIn(Vehicle v, IDamageable target)
        {
            var weapon = v.Def.Weapon;
            var distance = Vector2.Distance(v.Position, target.Position) - target.Radius;
            if (weapon.MinRange > 0f && distance < weapon.MinRange + 1f)
            {
                if (v.RepathTimer > 0f && v.HasPath) return;
                v.RepathTimer = RepathInterval;
                var away = v.Position - target.Position;
                away = away.LengthSquared() > 0.01f ? Vector2.Normalize(away) : SimMath.Forward(v.Heading + MathF.PI);
                _world.PathTo(v, _world.ClampToMap(target.Position + away * (weapon.MinRange + 8f)));
                return;
            }
            // In range and in the clear: hold here. In range but behind cover: keep driving (the
            // path leads round the building or rock) until the line of fire opens.
            var clear = _world.HasLineOfFire(v, target, weapon);
            if (distance <= weapon.Range * 0.9f && clear)
            {
                v.ClearPath();
                return;
            }
            var goalDrift = Vector2.Distance(v.PathGoal, target.Position);
            if (v.RepathTimer <= 0f && (!v.HasPath || goalDrift > 4f || (!clear && v.PathCompleted)))
            {
                v.RepathTimer = RepathInterval;
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
            if (!v.HasPath)
            {
                v.Speed = SimMath.MoveTowards(v.Speed, 0f, def.Speed * 2f * dt);
                TryAdvance(v, v.Speed * dt);
                // Hovering aircraft turn to face their target so hull-mounted rockets and missiles bear.
                if (def.Mounts[0].Aim == MountAim.Hull && _world.TryGetTarget(v.Target, out var target) &&
                    (def.Flying || target is not Vehicle { Flying: true }))
                    v.Heading = SimMath.RotateTowards(v.Heading, SimMath.HeadingOf(target.Position - v.Position), def.TurnRate * dt);
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
            if (!def.Flying && distance > 1.5f)
            {
                // Look ahead for a hull in the way. Follow a friend going the same way; steer round
                // anything parked, crossing or hostile instead of shoving into it.
                var forward = SimMath.Forward(v.Heading);
                var blocker = Blocker(v, forward, 1.2f + v.Speed * 0.7f);
                // Convoy trucks and bosses have right of way over their own side: the others
                // make room (they yield far more), so these keep to their route.
                if (blocker != null && blocker.Team == v.Team && (v.Scripted || v.Def.Boss)) blocker = null;
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
                v.Heading = SimMath.RotateTowards(v.Heading, desired, def.TurnRate * dt);

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
            Vector2 goal;
            if (target != null)
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

            // Turn back towards the middle before running out of map.
            var half = _world.Map.HalfSize;
            var margin = turnRadius * 1.3f + 4f;
            var nearEdge = MathF.Abs(v.Position.X) > half - margin || MathF.Abs(v.Position.Y) > half - margin;
            if (nearEdge && Vector2.Dot(SimMath.Forward(v.Heading), v.Position) > 0f) goal = Vector2.Zero;

            v.Heading = SimMath.RotateTowards(v.Heading, SimMath.HeadingOf(goal - v.Position), def.TurnRate * dt);
            v.Speed = SimMath.MoveTowards(v.Speed, def.Speed * v.SpeedFactor, def.Speed * 0.8f * dt);
            v.Position = _world.ClampToMap(v.Position + SimMath.Forward(v.Heading) * v.Speed * dt);
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
            if (_world.TryGetVehicle(v.RunTarget, out var run) && run.IsAlive && run.IsVisibleTo(v.Team) &&
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
                    v.Heading = SimMath.RotateTowards(v.Heading, bearing, v.Def.TurnRate * dt);
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
        /// never misjudged at high frame rates. Repaths twice, then gives up (V2 R05).
        /// </summary>
        private void DetectStuck(Vehicle v, float dt)
        {
            v.StuckTimer += dt;
            if (v.StuckTimer < StuckWindow) return;
            var progressed = Vector2.Distance(v.Position, v.StuckSample) >= StuckDistance;
            v.StuckSample = v.Position;
            v.StuckTimer = 0f;
            if (progressed)
            {
                v.StuckStrikes = 0;
                return;
            }

            v.StuckStrikes++;
            if (v.StuckStrikes >= StuckStrikesToGiveUp)
            {
                v.ClearPath();
                return;
            }
            var strikes = v.StuckStrikes;
            _world.PathTo(v, v.PathGoal);
            // Wedged a second time on a fresh route: back off to open ground a few metres away,
            // then take the route from there.
            if (strikes >= 2 && v.HasPath && TryDetour(v, v.Path[v.PathIndex], out var detour)) v.Path.Insert(v.PathIndex, detour);
            v.StuckStrikes = strikes;
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
