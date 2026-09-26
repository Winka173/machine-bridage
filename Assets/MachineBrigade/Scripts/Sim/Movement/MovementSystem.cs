#nullable enable
using System;
using System.Numerics;
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

        private readonly SimWorld _world;

        public MovementSystem(SimWorld world) => _world = world;

        public void Step(float dt)
        {
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                v.RepathTimer -= dt;
                UpdateOrder(v);
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
            }
        }

        private void UpdateAttackMove(Vehicle v)
        {
            var weapon = v.Def.Weapon;
            var enemy = _world.FindNearestEnemy(v, MathF.Max(v.Def.VisionRange, weapon.Range), requireVisible: true,
                minRange: weapon.MinRange);
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
            if (!v.HasPath)
            {
                v.Speed = SimMath.MoveTowards(v.Speed, 0f, def.Speed * 2f * dt);
                TryAdvance(v, v.Speed * dt);
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
            v.Heading = SimMath.RotateTowards(v.Heading, desired, def.TurnRate * dt);

            // Slow right down for sharp turns so tanks pivot instead of drawing wide arcs.
            var alignment = MathF.Cos(MathF.Min(misalignment, MathF.PI * 0.5f));
            var targetSpeed = def.Speed * MathF.Max(alignment, 0.15f);
            if (isFinal) targetSpeed = MathF.Min(targetSpeed, MathF.Max(1.5f, distance * 1.5f));
            var acceleration = def.Speed / (targetSpeed > v.Speed ? 1.2f : 0.5f);
            v.Speed = SimMath.MoveTowards(v.Speed, targetSpeed, acceleration * dt);

            if (!TryAdvance(v, v.Speed * dt)) v.Speed = 0f;
            DetectStuck(v, dt);
        }

        private bool TryAdvance(Vehicle v, float distance)
        {
            if (distance <= 0f) return true;
            var next = v.Position + SimMath.Forward(v.Heading) * distance;
            if (!_world.Grid.IsWalkable(next) || !_world.Map.Contains(next)) return false;
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
                    if (!b.IsAlive) continue;
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

                    var overlap = minimum - distance;
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
            if (_world.Grid.IsWalkable(next) && _world.Map.Contains(next)) v.Position = next;
        }
    }
}
