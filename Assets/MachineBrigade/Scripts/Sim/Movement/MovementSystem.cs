#nullable enable
using System;
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
        private const float SeparationSlack = 0.08f;
        private const float SeparationStiffness = 0.35f;

        /// <summary>How far an idle vehicle will drive from its post to fight.</summary>
        private const float GuardLeash = 16f;

        /// <summary>How long an idle vehicle remembers who shot it.</summary>
        private const float AnswerFireSeconds = 5f;

        /// <summary>After finishing a hand-given order, a vehicle stays out of the commander AI's hands this long.</summary>
        public const float ManualHoldSeconds = 20f;

        private readonly SimWorld _world;

        public MovementSystem(SimWorld world) => _world = world;

        public void Step(float dt)
        {
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                v.RepathTimer -= dt;
                UpdateOrder(v);
                if (v.ManualOrder && v.Order.Kind == OrderKind.Idle)
                {
                    v.ManualOrder = false;
                    v.ManualUntil = _world.Time + ManualHoldSeconds;
                }
                Drive(v, dt);
            }
            Separate();
        }

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

        private Vehicle? GuardThreat(Vehicle v)
        {
            // Only threats that can be fought without leaving the leash, so the vehicle never
            // swings back and forth at its edge.
            var weapon = v.Def.Weapon;
            var reach = GuardLeash + weapon.Range * 0.9f;
            if (_world.Time - v.LastHitTime < AnswerFireSeconds && _world.TryGetVehicle(v.LastAttacker, out var attacker) &&
                attacker.IsAlive && attacker.IsVisibleTo(v.Team) && weapon.CanTarget(attacker.Flying) &&
                Vector2.Distance(attacker.Position, v.GuardPoint) - attacker.Radius <= reach)
                return attacker;

            Vehicle? best = null;
            var bestDistance = float.MaxValue;
            foreach (var other in _world.VehicleList)
            {
                if (!other.IsAlive || other.Team == v.Team || !other.IsVisibleTo(v.Team) || !weapon.CanTarget(other.Flying)) continue;
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
                    v.ClearPath();
                }
                v.ResumeRoute = true;
                return;
            }
            var enemy = _world.FindNearestEnemy(v, MathF.Max(v.Def.VisionRange, weapon.Range), requireVisible: true,
                minRange: weapon.MinRange, layers: weapon.Targets);
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
            if (distance <= weapon.Range * 0.9f)
            {
                v.ClearPath();
                return;
            }
            var goalDrift = Vector2.Distance(v.PathGoal, target.Position);
            if (v.RepathTimer <= 0f && (!v.HasPath || goalDrift > 4f))
            {
                v.RepathTimer = RepathInterval;
                _world.PathTo(v, target.Position);
            }
        }

        private void Drive(Vehicle v, float dt)
        {
            var def = v.Def;
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
                if (def.Mounts[0].Aim == MountAim.Hull && _world.TryGetTarget(v.Target, out var target))
                    v.Heading = SimMath.RotateTowards(v.Heading, SimMath.HeadingOf(target.Position - v.Position), def.TurnRate * dt);
                return;
            }

            var waypoint = v.Path[v.PathIndex];
            var isFinal = v.PathIndex == v.Path.Count - 1;
            var toWaypoint = waypoint - v.Position;
            var distance = toWaypoint.Length();
            if (distance <= (isFinal ? ArriveFinal : ArriveWaypoint))
            {
                v.PathIndex++;
                if (!v.HasPath) v.PathCompleted = true;
                return;
            }

            var desired = SimMath.HeadingOf(toWaypoint);
            var misalignment = MathF.Abs(SimMath.WrapAngle(desired - v.Heading));
            // Close to the final point, small corrections would swing the hull back and forth:
            // hold the heading and let the vehicle roll in.
            if (!isFinal || distance > 2.5f || misalignment > 0.6f)
                v.Heading = SimMath.RotateTowards(v.Heading, desired, def.TurnRate * dt);

            // Slow right down for sharp turns so tanks pivot instead of drawing wide arcs.
            var alignment = MathF.Cos(MathF.Min(misalignment, MathF.PI * 0.5f));
            var targetSpeed = def.Speed * MathF.Max(alignment, def.Flying ? 0.4f : 0.15f);
            if (isFinal) targetSpeed = MathF.Min(targetSpeed, MathF.Max(1.5f, distance * 1.5f));
            var acceleration = def.Speed / (targetSpeed > v.Speed ? 1.2f : 0.5f);
            v.Speed = SimMath.MoveTowards(v.Speed, targetSpeed, acceleration * dt);

            if (!TryAdvance(v, v.Speed * dt)) v.Speed = 0f;
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
            v.Speed = SimMath.MoveTowards(v.Speed, def.Speed, def.Speed * 0.8f * dt);
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
            v.StuckStrikes = strikes;
        }

        /// <summary>Pushes overlapping hulls apart; parked vehicles yield more than moving ones.</summary>
        private void Separate()
        {
            var list = _world.VehicleList;
            for (var i = 0; i < list.Count; i++)
            {
                var a = list[i];
                if (!a.IsAlive) continue;
                for (var j = i + 1; j < list.Count; j++)
                {
                    var b = list[j];
                    // Aircraft only keep apart from each other; they fly over ground vehicles.
                    if (!b.IsAlive || a.Flying != b.Flying) continue;
                    var delta = b.Position - a.Position;
                    var minimum = a.Radius + b.Radius;
                    var distanceSquared = delta.LengthSquared();
                    if (distanceSquared >= minimum * minimum) continue;

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

                    // Resolve only part of the overlap per step and ignore slivers: full correction
                    // every step makes packed groups shove each other back and forth (visible jitter).
                    var overlap = (minimum - distance - SeparationSlack) * SeparationStiffness;
                    if (overlap <= 0f) continue;
                    var weightA = a.HasPath ? 0.3f : 0.7f;
                    var weightB = b.HasPath ? 0.3f : 0.7f;
                    var total = weightA + weightB;
                    Nudge(a, -normal * (overlap * weightA / total));
                    Nudge(b, normal * (overlap * weightB / total));
                }
            }
        }

        private void Nudge(Vehicle v, Vector2 offset)
        {
            var next = v.Position + offset;
            if (_world.Map.Contains(next) && (v.Flying || _world.Grid.IsWalkable(next))) v.Position = next;
        }
    }
}
