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
            ReplanClosedRoutes();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                // Fixed defences only turn their guns (the combat system does that); ships are the naval system's.
                if (v.Def.Static || v.Def.Naval != null) continue;
                // A boss boring underground or landing troops: the boss system moves it (or holds it still).
                // Prompt 19: a tiered boss falling to its crash site (the boss system moves it) or down on the ground,
                // and a drop pod on its way down.
                if (v.Burrow != Vehicle.BurrowState.Surface || v.Landing || v.Crashing || v.Crashed || v.IsPod || v.Charging)
                {
                    v.Speed = 0f;
                    continue;
                }
                // Prompt 25 F2 batch A: a reconnaissance jet flies its one straight pass (and leaves the battle at the far edge).
                if (v.Flying && _world.Works.FlyPass(v, dt)) continue;
                v.RepathTimer -= dt;
                if (!v.Flying) TrackTraffic(v);
                // Out of stores (prompt 13 C): the aircraft flies to its holding pattern and circles there,
                // its order kept for when it comes back.
                if (v.Flying && v.Supply != SupplyState.Fighting) SteerToRearm(v);
                // Making way or backing out for a friend: the order waits (it is taken up again after).
                else if (!TrafficOverlay(v)) UpdateOrder(v);
                if (v.ManualOrder && v.Order.Kind == OrderKind.Idle)
                {
                    v.ManualOrder = false;
                    v.ManualUntil = _world.Time + ManualHoldSeconds;
                }
                // Prompt 17 C: a bunker vehicle digging in, dug in or packing up stays put.
                if (DeployHeld(v)) continue;
                Drive(v, dt);
                // Prompt 25 F2 batch A: helicopters keep out of an enemy barrage balloon's ground.
                if (v.Flying && !v.Def.FixedWing) _world.Works.KeepOffBalloons(v, dt);
                // The safety net for what the traffic rules leave stuck (MovementSystem.Rescue).
                WatchRescue(v);
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
                // Underground, it is in nobody's way; nor is a ship at sea.
                if (!v.IsAlive || v.Flying || v.Burrowed || v.Def.Naval != null) continue;
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
                if (o == v || !o.IsAlive || PassThrough(v, o)) continue;
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
                var nearby = GuardThreat(v) ?? SeadTarget(v);
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
                Vector2.Distance(attacker.Position, v.GuardPoint) - attacker.Radius <= reach && !OffPost(v, attacker))
                return attacker;

            Vehicle? best = null;
            var bestDistance = float.MaxValue;
            foreach (var other in _world.VehicleList)
            {
                if (!other.IsAlive || other.Team == v.Team || !other.IsVisibleTo(v.Team) || !weapon.CanTarget(other.Flying)) continue;
                if ((other.Flying && !HuntsAircraft(v)) || other.Invulnerable) continue;
                if (v.Def.Interceptor && !other.Flying) continue;
                if (OffPost(v, other)) continue;
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
            // A bomber picks its run by what its bombs would hit (prompt 13 D.2): a group or a structure.
            var enemy = v.Def.FixedWing && weapon.Projectile == ProjectileKind.Bomb && weapon.Burst > 1 ? BombTarget(v)
                : _world.FindNearestEnemy(v, MathF.Max(v.Def.VisionRange, weapon.Range), requireVisible: true,
                    minRange: weapon.MinRange, layers: HuntsAircraft(v) ? weapon.Targets : weapon.Targets & TargetLayers.Ground);
            // Prompt 17 C: the stealth fighter with no aircraft about goes for the air defences.
            enemy ??= SeadTarget(v);
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
        /// Prompt 13 D.2: a bomber's run: the known ground enemy in sight whose surroundings its bombs are
        /// worth most on (groups and structures first, a lone light vehicle last, not ground it just
        /// bombed), nearer ones a little ahead of farther.
        /// </summary>
        private Vehicle? BombTarget(Vehicle v)
        {
            var weapon = v.Def.Weapon;
            var reach = MathF.Max(v.Def.VisionRange, 60f);
            Vehicle? best = null;
            var bestScore = 0f;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying || e.Invulnerable || e.Def.Untargetable || !e.IsVisibleTo(v.Team)) continue;
                var d = Vector2.Distance(e.Position, v.Position);
                if (d > reach) continue;
                var score = _world.Combat.BombWorth(v.Team, e, weapon) * MathF.Sqrt(Math.Clamp(Combat.CombatSystem.Worth(e), 2f, 25f)) / (1f + d / 200f);
                if (score <= bestScore) continue;
                best = e;
                bestScore = score;
            }
            return best;
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
        /// Play-test 6 (DECISIONS 21G, the owner's call): it opens from that ring (its first missiles away,
        /// <see cref="StandoffOpening"/> s in the band), then, while no such anti-air covers the ground at its
        /// gun's reach from the target, it comes in and fights with the cannon and rockets as well (false:
        /// the ordinary approach, to its gun's reach). Anti-air turning up sends it back out to the ring.
        /// </summary>
        private bool Standoff(Vehicle v, IDamageable target)
        {
            var reach = v.Def.Weapon.Range;
            var distance = Vector2.Distance(v.Position, target.Position) - target.Radius;
            _shortAa.Clear();
            _airDefence.Clear();
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying || !e.IsVisibleTo(v.Team)) continue;
                var aa = 0f;
                var made = 0f;
                foreach (var m in e.Def.Mounts)
                {
                    if (m.Weapon.CanTarget(true)) aa = MathF.Max(aa, m.Weapon.Range);
                    if (m.Weapon.CanTarget(true) && (Combat.CombatSystem.IsAntiAir(m.Weapon) || m.Weapon.Penetration >= 2))
                        made = MathF.Max(made, m.Weapon.Range);
                }
                if (aa > 0f && aa < reach - 2f) _shortAa.Add((e.Position, aa));
                // Play-test 6: guns and missiles that hurt a helicopter (flak, SAMs, autocannons), not a tank's machine gun.
                if (made > 0f) _airDefence.Add((e.Position, made));
            }
            float Exposure(Vector2 at)
            {
                var worst = 0f;
                foreach (var (p, r) in _shortAa) worst += MathF.Max(0f, r + StandoffMargin - Vector2.Distance(at, p));
                return worst;
            }
            // A new target: the missile phase again, from the ring.
            var targetId = target.Id;
            if (v.StandoffTarget != targetId)
            {
                v.StandoffTarget = targetId;
                v.StandoffSince = double.PositiveInfinity;
            }
            var gun = GunReach(v, target);
            if (gun < reach && _world.Time - v.StandoffSince >= StandoffOpening)
            {
                var toward = v.Position - target.Position;
                var close = target.Position + (toward.LengthSquared() > 0.01f ? Vector2.Normalize(toward) : Vector2.UnitX) * (gun * 0.85f + target.Radius);
                var covered = false;
                foreach (var (p, r) in _airDefence)
                    if (Vector2.Distance(close, p) < r + StandoffMargin || Vector2.Distance(v.Position, p) < r + StandoffMargin) covered = true;
                if (!covered) return false;
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
                if (double.IsPositiveInfinity(v.StandoffSince)) v.StandoffSince = _world.Time;
                v.ClearPath();
                return true;
            }
            if (v.RepathTimer > 0f && v.HasPath) return true;
            v.RepathTimer = RepathInterval;
            _world.PathTo(v, best);
            return true;
        }

        private static readonly float[] Rings = { 0.82f, 0.95f };

        /// <summary>Play-test 6: seconds a standoff helicopter fires from its ring before it comes in to its gun.</summary>
        private const double StandoffOpening = 6.0;

        /// <summary>Play-test 6: the shortest reach of the forward weapons a standoff helicopter brings in with it (its cannon's).</summary>
        private static float GunReach(Vehicle v, IDamageable target)
        {
            var flying = target is Vehicle { Flying: true };
            var reach = v.Arms[0].Range;
            var mounts = v.Def.Mounts;
            for (var i = 1; i < mounts.Count; i++)
            {
                var w = v.Arms[i];
                if (mounts[i].Aim is MountAim.Left or MountAim.Right || mounts[i].ArcHalf > 0f) continue;
                if (w.Damage <= 0f || !w.CanTarget(flying) || v.Weapons[i].Ammo == 0) continue;
                reach = MathF.Min(reach, w.Range);
            }
            return reach;
        }

        /// <summary>
        /// Test feedback 2 (DECISIONS 12F): the reach a helicopter hovers at to fight. Holding at its
        /// missile's reach left the gun and the rockets, which reach less far, silent (the attack
        /// helicopter's gun is nearly half its firepower); it now comes in to the shortest reach of
        /// the weapons it faces the target with (not the door guns, not a launcher that is empty or
        /// cannot hit this target), but never nearer than 60 % of its main weapon's.
        /// </summary>
        private static float HoverReach(Vehicle v, IDamageable target)
        {
            var flying = target is Vehicle { Flying: true };
            var main = v.Arms[0].Range;
            var reach = main;
            var mounts = v.Def.Mounts;
            for (var i = 1; i < mounts.Count; i++)
            {
                var w = v.Arms[i];
                if (mounts[i].Aim is MountAim.Left or MountAim.Right || mounts[i].ArcHalf > 0f) continue;
                if (w.Damage <= 0f || !w.CanTarget(flying) || v.Weapons[i].Ammo == 0) continue;
                reach = MathF.Min(reach, w.Range);
            }
            // Play-test 6: a standoff helicopter that has come in goes all the way to its cannon's reach.
            return v.Def.Standoff ? reach : MathF.Max(reach, main * 0.6f);
        }

        /// <summary>Metres a standoff helicopter keeps beyond the reach of anti-air it outranges.</summary>
        private const float StandoffMargin = 5f;

        private readonly List<(Vector2 at, float reach)> _shortAa = new();

        /// <summary>Play-test 6: the enemy's air defence proper round a standoff helicopter's target (where it will not come in).</summary>
        private readonly List<(Vector2 at, float reach)> _airDefence = new();

        /// <summary>Holds position once in range; otherwise (re)paths towards the target.</summary>
        private void CloseIn(Vehicle v, IDamageable target)
        {
            if (v.Flying && v.Def.Standoff && Standoff(v, target)) return;
            var weapon = v.Def.Weapon;
            var distance = Vector2.Distance(v.Position, target.Position) - target.Radius;
            if (weapon.MinRange > 0f && distance < weapon.MinRange + 1f)
            {
                // Play-test 5 (DECISIONS 20W): a siege tank does not back off: its tank-mode gun fights it (sieged, it
                // packs up for that once nothing else is left to shell).
                if (v.Def.Deploy is { Siege: true } siege && siege.TankMount < v.Arms.Length && distance <= v.Arms[siege.TankMount].Range)
                {
                    v.ClearPath();
                    return;
                }
                if (v.RepathTimer > 0f && v.HasPath) return;
                v.RepathTimer = RepathInterval;
                // Back off by the best way out; cornered, hold and let the machine gun fight.
                if (_world.EscapeRoute(v, target.Position, weapon.MinRange + 8f - distance) is { } escape) _world.PathTo(v, escape);
                return;
            }
            // In range and in the clear: hold here. In range but behind cover: keep driving (the
            // path leads round the building or rock) until the line of fire opens. A helicopter
            // comes in until its gun and rockets reach as well (see HoverReach).
            var clear = _world.HasLineOfFire(v, target, weapon);
            var reach = v.Flying && !v.Def.FixedWing && !v.Def.Boss ? HoverReach(v, target) : weapon.Range;
            // Prompt 17 C: dug in, it reaches further (and does not pack up for what it can already hit).
            if (v.Deploy == DeployState.Deployed) reach *= v.RangeFactor;
            if (distance <= reach * 0.9f && clear)
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
                // Prompt 28 D.4: a standing ground vehicle with directional armour turns its front to the biggest threat.
                else if (!def.Flying && v.FaceHeading is { } face && v.Speed < 0.1f)
                    v.Heading = SimMath.RotateTowards(v.Heading, face, def.TurnRate * v.TurnFactor * 0.5f * dt);
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
                desired += AvoidTurn(v, desired, v.AvoidSide * AvoidAngle * (float)Math.Min(1.0, (v.AvoidUntil - _world.Time) / (AvoidSeconds * 0.5)));
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
        /// Aeroplanes never stop (a VTOL jet only in its attack hold). With a target they fly at
        /// it, fire as it bears, hold their guns on it (see <see cref="AttackHold"/>) or pull
        /// through past it, extend, then turn in for another run; behind a fast jet they match its
        /// speed; with a destination they fly there; otherwise they circle their post. They turn
        /// back well before the map edge.
        /// </summary>
        private void DriveAeroplane(Vehicle v, float dt)
        {
            var def = v.Def;
            var turnRadius = def.Speed / def.TurnRate;
            var target = RunTarget(v);
            // Prompt 17 C: a loyal wingman flies on its leader's wing when it has nothing of its own to attack.
            if (target == null && def.Wingman != null && FlyWing(v, dt)) return;
            v.InAttackHold = false;
            v.OnTail = false;
            if (target != null && def.AttackHold > 0f && !def.Orbit && AttackHold(v, target, dt)) return;
            if (target == null && v.HoldUntil > _world.Time) v.HoldUntil = _world.Time;
            if (target == null) v.Defending = v.BreakingOff = false;
            Vector2 goal;
            var throttle = 1f;
            // The map's middle and half extents (a long battlefield's are its own, prompt 17).
            var centre = _world.Map.Centre;
            float halfX = _world.Map.Width * 0.5f, halfZ = _world.Map.Length * 0.5f;
            var margin = turnRadius * 1.3f + 4f;
            var circling = false;
            var turnBoost = 1f;
            var chasingJet = false;
            if (target != null && def.Orbit)
            {
                // A gunship's pylon turn: round and round the target, anticlockwise so it stays on
                // the left where the guns are, far enough out to see it and to stay clear of the
                // short-range anti-aircraft round it. The circle is kept inside the map (a target
                // near the edge is circled from the inside), and its centre glides to a new target
                // at a few metres a second, so the turn never jerks.
                var radius = MathF.Max(turnRadius * 1.15f, def.OrbitRadius > 0f ? def.OrbitRadius : def.Weapon.Range * 0.62f);
                var limitX = MathF.Max(0f, halfX - radius - 4f);
                var limitZ = MathF.Max(0f, halfZ - radius - 4f);
                var want = new Vector2(Math.Clamp(target.Position.X, centre.X - limitX, centre.X + limitX),
                    Math.Clamp(target.Position.Y, centre.Y - limitZ, centre.Y + limitZ));
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
                // The run is flown to the reach of its guns (a fighter's cannon, not its long-range missiles).
                var range = AttackReach(v, target);
                var toTarget = target.Position - v.Position;
                var distance = toTarget.Length();
                var ahead = Vector2.Dot(SimMath.Forward(v.Heading), toTarget);
                var mover = FastMover(v, target);
                // Prompt 25 F2 batch A: a stand-off bomber turns away before it is over its target.
                if (def.GlideRelease) GlideAway(v, target, range, distance);
                // Play-test 5 (DECISIONS 20W): a jet whose cannon reaches aircraft gets on an enemy jet's tail: in its rear
                // cone it keeps the nose on it (the cannon streams), else it flies for a point behind it (lag pursuit).
                var tail = mover != null && TailGun(v, flying: true) >= 0 ? mover : null;
                // Play-test 6 (DECISIONS 21F): two jets hunting each other no longer turn round one circle for ever: the
                // worse placed out of the merge runs out, jinking (Defending), and the other gets on its tail; low on
                // health, either breaks off and flies away from the enemy jet.
                if (tail == null) v.Defending = v.BreakingOff = false;
                if (tail != null && Dogfight(v, tail, range, distance, dt, out var away, out var run))
                {
                    goal = v.Position + away * 10f;
                    throttle = run;
                    v.RunExtending = false;
                }
                else
                {
                    var behind = tail != null && Vector2.Dot(SimMath.Forward(tail.Heading), v.Position - tail.Position) < -TailCone * distance;
                    if (!v.RunExtending)
                    {
                        // Pull through once too close to keep the nose on it, or once it slips behind (not a jet on its tail).
                        if (distance < MathF.Max(6f, range * 0.3f) || (tail == null && ahead < 0f && distance < range * 0.6f)) v.RunExtending = true;
                    }
                    else if (distance > MathF.Max(range * 0.85f, turnRadius * 2.2f))
                    {
                        v.RunExtending = false;
                        v.BreakAway = false;
                    }
                    // Out of a hover it turns away first rather than fly on through its target.
                    goal = v.RunExtending ? v.Position + SimMath.Forward(v.BreakAway ? v.BreakHeading : v.Heading) * 10f : target.Position;
                    if (tail != null && !v.RunExtending && !(behind && distance < range * TailClose))
                        goal = tail.Position - SimMath.Forward(tail.Heading) * (range * ChaseShare);
                    var gap = distance - target.Radius;
                    v.OnTail = tail != null && behind && !v.RunExtending && gap <= range && ahead > distance * 0.9f;
                    // Play-test 6 (DECISIONS 21F): in the jet's rear cone and close, it follows the jet's turns (it no longer
                    // drops off the tail when the jet turns back from the map's edge).
                    if (tail != null && behind && !v.RunExtending && distance < range * TailClose) turnBoost = TailTurn;
                    chasingJet = tail != null && !v.RunExtending;
                    if (!v.RunExtending && mover != null && gap < range * 1.3f && ahead > distance * 0.6f)
                    {
                        // Behind a fast jet: match its speed to keep it on the nose at a little over half
                        // the guns' reach (the cannon streams for as long as it stays there).
                        var want = (mover.Speed + (gap - range * ChaseShare) * 1.5f) / MathF.Max(1f, def.Speed * v.SpeedFactor);
                        throttle = Math.Clamp(want, def.Vtol ? 0.3f : 0.45f, 1f);
                    }
                    else if (!v.RunExtending && def.AttackHold > 0f && mover == null)
                    {
                        // Coming in for a hold: easing off from half as far again as its reach, so it
                        // is at half speed when the hold begins.
                        throttle = Math.Clamp((gap - range) / range + 0.5f, 0.5f, 1f);
                    }
                    // Throttle back through the attack run for more time on the target; full power to
                    // extend and come round.
                    else if (!v.RunExtending && distance < range * 1.1f) throttle = 0.8f;
                }
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
            var fromCentre = v.Position - centre;
            var nearEdge = MathF.Abs(fromCentre.X) > halfX - margin || MathF.Abs(fromCentre.Y) > halfZ - margin;
            // Play-test 6 (DECISIONS 21F): not a jet chasing another (it lost the tail there); the jet it chases turns back itself.
            if (!circling && !chasingJet && nearEdge && Vector2.Dot(SimMath.Forward(v.Heading), fromCentre) > 0f) goal = centre;

            v.Heading = SimMath.RotateTowards(v.Heading, SimMath.HeadingOf(goal - v.Position), def.TurnRate * v.TurnFactor * turnBoost * dt);
            v.Speed = SimMath.MoveTowards(v.Speed, def.Speed * v.SpeedFactor * throttle, def.Speed * 0.8f * dt);
            v.Position = _world.ClampToMap(v.Position + SimMath.Forward(v.Heading) * v.Speed * dt);
        }

        /// <summary>How fast the centre of a pylon turn follows its target, in metres a second.</summary>
        private const float OrbitGlide = 6f;

        /// <summary>Seconds after an attack hold before the next may begin (it must have flown its loop as well).</summary>
        private const double HoldRest = 1.5;

        /// <summary>Slowest and fastest crawl (shares of its speed) of a jet that cannot hover in its hold; under flak it keeps at least the faster.</summary>
        private const float HangSlowest = 0.15f, HangFastest = 0.5f;

        /// <summary>How far off the nose (radians) the target may be for a jet that cannot hover to begin its hold.</summary>
        private const float HoldCone = 0.6f;

        /// <summary>Share of its guns' reach a hovering jet glides in to, and a chasing one keeps behind a fast jet.</summary>
        private const float HoverShare = 0.6f, ChaseShare = 0.55f;

        /// <summary>
        /// Play-test 5: on a jet's tail within this cosine of dead astern (about 60 degrees), and closer than this share of
        /// its guns' reach it stops flying for the point behind and keeps its nose on the jet itself.
        /// </summary>
        private const float TailCone = 0.5f, TailClose = 1.4f;

        /// <summary>
        /// The mount of an aeroplane's hull-fixed cannon firing from a magazine that can hit a target in the air
        /// (<paramref name="flying"/>) or on the ground; -1 when it has none (a fighter's GAU-22, an attack jet's cannon on the ground).
        /// </summary>
        internal static int TailGun(Vehicle v, bool flying)
        {
            var mounts = v.Def.Mounts;
            for (var i = 0; i < mounts.Count; i++)
            {
                var w = v.Arms[i];
                if (mounts[i].Aim == MountAim.Hull && w.Projectile == ProjectileKind.Bullet && w.Clip > 0 && w.Damage > 0f && w.CanTarget(flying)) return i;
            }
            return -1;
        }

        /// <summary>
        /// Play-test 6 (DECISIONS 21F): a jet chasing an enemy jet. Below <see cref="BreakOffHealth"/> of its health it
        /// breaks off: it flies away from the enemy jet at full power and chases it no more. When the enemy jet is hunting
        /// it too (its cannon reaches aircraft) and it came out of the merge the worse placed (the enemy further astern of
        /// it than it is of the enemy; level, the later-spawned one), it defends: it runs out at part power, jinking, so the
        /// other gets on its tail and streams its cannon at it, until it is out past <see cref="DefendOut"/> of the guns'
        /// reach or the enemy slips in front (an overshoot), and then turns in again. Never head-on, where both fire.
        /// True when it does not chase: <paramref name="away"/> is the way it flies, <paramref name="throttle"/> its power.
        /// </summary>
        private bool Dogfight(Vehicle v, Vehicle enemy, float range, float distance, float dt, out Vector2 away, out float throttle)
        {
            away = SimMath.Forward(v.Heading);
            throttle = 1f;
            var from = distance > 0.1f ? (v.Position - enemy.Position) / distance : -away;
            if (v.Hp < v.MaxHp * BreakOffHealth)
            {
                v.BreakingOff = true;
                v.Defending = false;
                away = Vector2.Normalize(from * 2f + away);
                return true;
            }
            v.BreakingOff = false;
            var hunted = (enemy.RunTarget == v.Id || enemy.Target == v.Id) && !enemy.BreakingOff && TailGun(enemy, flying: true) >= 0;
            if (!hunted)
            {
                v.Defending = false;
                return false;
            }
            // How far astern (-1: dead astern): this jet of the enemy, and the enemy of this jet.
            var mine = Vector2.Dot(SimMath.Forward(enemy.Heading), from);
            var theirs = Vector2.Dot(away, -from);
            if (v.Defending)
            {
                if (distance > range * DefendOut || theirs > 0.6f) v.Defending = false;
            }
            else if (distance < range * DefendIn && !(mine > 0.5f && theirs > 0.5f) && !enemy.Defending &&
                     (theirs < mine - AspectMargin || (MathF.Abs(theirs - mine) <= AspectMargin && v.Id.Value > enemy.Id.Value)))
                v.Defending = true;
            if (!v.Defending) return false;
            // Straight out, bending away from the enemy, weaving a little either side.
            var weave = MathF.Sin((float)_world.Time * 1.6f + v.Id.Value) * 0.6f;
            var side = new Vector2(-away.Y, away.X);
            away = Vector2.Normalize(away * 2f + from + side * weave);
            throttle = DefendPower;
            return true;
        }

        /// <summary>Play-test 6: below this share of its health a jet breaks off a dogfight.</summary>
        internal const float BreakOffHealth = 0.3f;

        /// <summary>
        /// Play-test 6: within this share of its guns' reach a dogfight's roles are decided, and a defending jet turns in
        /// again past <see cref="DefendOut"/>; the astern measures must differ by <see cref="AspectMargin"/> for a clear
        /// winner; a defending jet runs at <see cref="DefendPower"/> (its jinking costs speed, so the chaser closes).
        /// </summary>
        private const float DefendIn = 2.2f, DefendOut = 2.6f, AspectMargin = 0.25f, DefendPower = 0.82f;

        /// <summary>Play-test 6: how much quicker a jet on another's tail turns with it.</summary>
        private const float TailTurn = 1.3f;

        /// <summary>How far (radians) a jet leaving its hover turns away before it extends.</summary>
        private const float BreakTurn = 1.1f;

        /// <summary>
        /// Test feedback 2 (DECISIONS 12F): an aeroplane with its target in reach holds its guns on
        /// it for <see cref="VehicleDef.AttackHold"/> seconds, so the cannon streams a whole magazine
        /// and the rockets, missiles and bombs all get their turn, instead of a pass of about a
        /// second. A VTOL jet (Harrier, F-35B) hovers: it glides in to a little over half its guns'
        /// reach, stops and turns on the spot to keep its nose on the target. Any other slows to a
        /// crawl with its nose on the target, paced to come over it as the hold ends, then pulls
        /// through. Either then breaks away at full power, comes round and holds again. Inside a
        /// flak gun's reach it never hangs there: it slows only to half speed (a quicker run, since a
        /// hovering jet is easy to hit). A target that gets out of reach (a fast jet) ends the hold
        /// and the chase goes on. True while it holds.
        /// </summary>
        private bool AttackHold(Vehicle v, IDamageable target, float dt)
        {
            var def = v.Def;
            var now = _world.Time;
            var reach = AttackReach(v, target);
            var toTarget = target.Position - v.Position;
            var distance = toTarget.Length();
            var gap = distance - target.Radius;
            var off = MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(toTarget) - v.Heading));
            var pullThrough = MathF.Max(5f, reach * 0.2f);
            if (now >= v.HoldUntil)
            {
                if (v.RunExtending || now < v.HoldReadyAt || gap > reach * 0.95f || distance < pullThrough + 3f ||
                    (!def.Vtol && off > HoldCone) || FastMover(v, target) != null)
                    return false;
                v.HoldUntil = now + HoldSeconds(v, target);
            }
            // It got away (a jet flying on, a helicopter moving off): the chase goes on.
            if (gap > reach * 1.25f)
            {
                v.HoldUntil = now;
                v.HoldReadyAt = now + HoldRest;
                return false;
            }
            var flak = UnderFlak(v);
            var hover = def.Vtol && !flak;
            // Over the target (or it slipped past the nose): pull through and fly on.
            if (!hover && (distance < pullThrough || off > MathF.PI * 0.5f))
            {
                EndHold(v, now, false);
                return false;
            }
            var cruise = def.Speed * v.SpeedFactor;
            float want;
            if (hover) want = Math.Clamp((gap - reach * HoverShare) * 1.5f, 0f, cruise * 0.5f);
            else
            {
                // Paced to reach the target as the hold runs out.
                var left = (float)Math.Max(0.3, v.HoldUntil - now);
                want = Math.Clamp((distance - pullThrough) / left, cruise * (flak ? HangFastest : HangSlowest), cruise * HangFastest);
            }
            v.Speed = SimMath.MoveTowards(v.Speed, want, def.Speed * 1.1f * dt);
            v.Heading = SimMath.RotateTowards(v.Heading, SimMath.HeadingOf(toTarget), def.TurnRate * v.TurnFactor * 1.4f * dt);
            v.Position = _world.ClampToMap(v.Position + SimMath.Forward(v.Heading) * v.Speed * dt);
            v.InAttackHold = true;
            if (now + dt >= v.HoldUntil)
            {
                // Play-test 6 (DECISIONS 21F): on an aircraft (a helicopter it hangs on) with its cannon, out of flak, it holds
                // on for another spell while it keeps the target in reach, firing until it dies or gets away.
                if (target is Vehicle { Flying: true } && TailGun(v, flying: true) >= 0 && !flak && (hover || distance > pullThrough * 2f))
                    v.HoldUntil = now + dt + HoldSeconds(v, target);
                else EndHold(v, now + dt, hover);
            }
            return true;
        }

        /// <summary>
        /// Play-test 6 (DECISIONS 21F): how long an attack hold lasts: the data's, or for a jet whose main weapon is its
        /// hull cannon firing from a magazine (the attack jet's), long enough for a whole magazine's stream.
        /// </summary>
        private static float HoldSeconds(Vehicle v, IDamageable target)
        {
            var hold = v.Def.AttackHold;
            var gun = v.Arms[0];
            if (TailGun(v, target is Vehicle { Flying: true }) == 0)
                hold = MathF.Max(hold, (gun.Clip - 1) * gun.Cooldown + 0.6f);
            return hold;
        }

        /// <summary>The hold is over: fly on (a hovering jet turns away first, to alternate sides) and come round.</summary>
        private static void EndHold(Vehicle v, double at, bool hovered)
        {
            v.HoldUntil = at;
            v.HoldReadyAt = at + HoldRest;
            v.RunExtending = true;
            v.BreakAway = hovered;
            if (!hovered) return;
            v.BreakHeading = v.Heading + v.BreakSide * BreakTurn;
            v.BreakSide = -v.BreakSide;
        }

        /// <summary>
        /// The reach an aeroplane's attack is flown to: its shortest-reaching hull-mounted gun that
        /// can hit the target (a fighter's cannon rather than its long-range missiles), else its main weapon's.
        /// </summary>
        private static float AttackReach(Vehicle v, IDamageable target)
        {
            var flying = target is Vehicle { Flying: true };
            var reach = 0f;
            var mounts = v.Def.Mounts;
            for (var i = 0; i < mounts.Count; i++)
            {
                var w = v.Arms[i];
                if (mounts[i].Aim != MountAim.Hull || w.Projectile != ProjectileKind.Bullet || w.Damage <= 0f || !w.CanTarget(flying)) continue;
                reach = reach > 0f ? MathF.Min(reach, w.Range) : w.Range;
            }
            return reach > 0f ? reach : v.Arms[0].Range;
        }

        /// <summary>The target is a jet flying fast (not hovering or crawling in its own hold): it is chased, not held on.</summary>
        private static Vehicle? FastMover(Vehicle v, IDamageable target) =>
            target is Vehicle jet && jet.Def.FixedWing && jet.Speed > v.Def.Speed * 0.35f ? jet : null;

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

        /// <summary>
        /// Prompt 13 C: an aircraft on its way to rearm or rearming flies to its holding pattern (or pad,
        /// HQ, carrier): an aeroplane then circles it as it circles a post, a helicopter hovers over it.
        /// </summary>
        private void SteerToRearm(Vehicle v)
        {
            var at = v.HoldPoint;
            v.GuardPoint = at;
            v.Engaged = EntityId.None;
            var distance = Vector2.Distance(v.Position, at);
            // An aeroplane flies there and then circles it (its circle pulls it round; routing it back to
            // the centre each time it swung wide would wag its nose); a helicopter hovers on the spot.
            var near = v.Def.FixedWing ? Abilities.SupplySystem.Orbit(v) * 2f + 10f : 2.5f;
            if (distance <= near)
            {
                if (v.HasPath && (!v.Def.FixedWing || distance < Abilities.SupplySystem.Orbit(v) + 4f)) v.ClearPath();
                return;
            }
            if (!v.HasPath || Vector2.Distance(v.PathGoal, at) > 8f) _world.PathTo(v, at);
        }

        /// <summary>The strafing-run target: an ordered one, else the current or last engaged enemy.</summary>
        private IDamageable? RunTarget(Vehicle v)
        {
            // Out to rearm: no attack runs (its guns still fire at what comes into reach).
            if (v.Supply != SupplyState.Fighting)
            {
                v.RunTarget = EntityId.None;
                return null;
            }
            if (v.Order.Kind is OrderKind.Move or OrderKind.Retreat)
            {
                v.RunTarget = EntityId.None;
                return null;
            }
            if (v.Order.Kind == OrderKind.Attack && _world.TryGetTarget(v.Order.Target, out var ordered) && ordered.IsAlive)
                return ordered;
            var weapon = v.Def.Weapon;
            if (_world.TryGetVehicle(v.RunTarget, out var run) && run.IsAlive && !run.Invulnerable && run.IsVisibleTo(v.Team) &&
                weapon.CanTarget(run.Flying) && Vector2.Distance(run.Position, v.Position) < weapon.Range * 2.5f && !OffPost(v, run))
                return run;
            v.RunExtending = false;
            if (_world.TryGetVehicle(v.Target, out var current) && current.IsAlive && !OffPost(v, current))
            {
                v.RunTarget = current.Id;
                return current;
            }
            if (_world.TryGetVehicle(v.Engaged, out var engaged) && engaged.IsAlive && engaged.IsVisibleTo(v.Team) && !OffPost(v, engaged))
            {
                v.RunTarget = engaged.Id;
                return engaged;
            }
            v.RunTarget = EntityId.None;
            return null;
        }

        /// <summary>A called escort's target beyond its post (see <see cref="Vehicle.PostRadius"/>).</summary>
        private static bool OffPost(Vehicle v, Vehicle target) =>
            v.PostRadius > 0f && Vector2.Distance(target.Position, v.GuardPoint) > v.PostRadius + target.Radius;

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
            v.Traffic.GaveUpAt = _world.Time;
            v.Traffic.GaveUpGoal = v.PathGoal;
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
                    if (Vector2.DistanceSquared(a.Position, b.Position) >= bound * bound || PassThrough(a, b)) continue;
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
            if (v.Def.Static || v.Crashed) return 0f;
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
