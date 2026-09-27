#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// The traffic rules between ground vehicles of one side, after the coordinated movement of
    /// Age of Empires II, the push priorities of StarCraft II and OpenRA's notify, wait, then
    /// repath (ideas only; nothing is copied from GPL code):
    /// <list type="bullet">
    /// <item>A moving vehicle blocked by a parked friend of lower traffic priority asks it to make
    /// way. Requests are collected during one step and served at the start of the next, so the
    /// outcome never depends on the order vehicles were driven in. The asked vehicle steps
    /// sideways, to its own side of the mover's route and off the lane, holds until the mover
    /// is past, then carries on with its order; the mover crawls behind instead of swerving
    /// into a wall.</item>
    /// <item>Two friends meeting head-on in a doorway: the one with less right of way backs
    /// straight out (tracks need not turn round) and waits beside the mouth.</item>
    /// <item>Stuck all the same: ask again with more weight, then plan a route round the parked
    /// hulls (a unit cost field, budgeted by searched cells per step), then back off, then give
    /// up. With no way round (a single gate) it queues behind the hull instead of ramming it.</item>
    /// </list>
    /// Aircraft take no part: they keep apart in the air.
    /// </summary>
    internal sealed partial class MovementSystem
    {
        /// <summary>A vehicle standing this long (no route, or slower than a parked hull) can be asked to make way.</summary>
        private const double ParkedForAsk = 0.3;

        /// <summary>A request passed on: A asks B, B asks C, then it stops.</summary>
        private const int MaxYieldDepth = 2;

        /// <summary>Sideways steps of a yield, in multiples of both hulls' radii plus a metre, and steps along the mover's way.</summary>
        private static readonly float[] LateralSteps = { 1.0f, 1.6f, 2.4f };

        private static readonly float[] AlongSteps = { 0f, 4f, 8f, -4f };

        /// <summary>A yield lasts at most this long (which also bounds the reload it pauses).</summary>
        private const double YieldMaxSeconds = 4.0;

        /// <summary>Once at its spot, the yielding vehicle holds until the mover is past, or this long.</summary>
        private const double YieldHoldSeconds = 2.5;

        /// <summary>After making way it is not asked again for this long (except by priority 80 and up).</summary>
        private const double YieldCooldown = 4.0;

        /// <summary>How long a mover waits behind a friend making way before it counts as stuck.</summary>
        private const double YieldWaitSeconds = 3.0;

        /// <summary>Priorities from this up are obeyed even by a vehicle already yielding or resting after a yield.</summary>
        private const int OverridePriority = 80;

        /// <summary>A unit's routes planned round parked hulls come at least this far apart.</summary>
        private const double MinCostRepathGap = 1.0;

        /// <summary>A route planned round parked hulls is kept this long before a plain replan may replace it.</summary>
        private const double CostPathKeep = 3.0;

        /// <summary>Cells all routes planned round hulls may expand in one step, and one of them at most.</summary>
        internal const int PathNodeBudgetPerTick = 20000;

        private const int MaxNodesPerSearch = 8000;

        /// <summary>A queued search starts only with this much of the step's budget left (the first always runs).</summary>
        private const int MinSearchBudget = 2000;

        /// <summary>A route round the hulls longer than this share of the plain one (plus a few metres) is no way round.</summary>
        private const float DetourCap = 1.5f;

        private const float DetourSlack = 8f;

        /// <summary>A route round that still passes the blocker within this many metres is no way round either.</summary>
        private const float NoAlternativeLength = 12f;

        /// <summary>How long a vehicle with no way round waits behind the hull before it tries anything else.</summary>
        private const double QueueSeconds = 6.0;

        /// <summary>A head-on loser backs out at most this far, at this share of its speed, then waits this long.</summary>
        private const float HeadOnReverseMax = 12f;

        private const float ReverseSpeedShare = 0.5f;
        private const double HeadOnWait = 1.5;

        /// <summary>A plain back-off when wedged: this many metres straight back.</summary>
        private const float BackOffDistance = 4f;

        /// <summary>Holding on a main route, a friend coming along it this close behind means stepping off.</summary>
        private const float TrafficBehindReach = 25f;

        /// <summary>Sideways offsets and steps ahead tried when stepping off the lane to hold fire position.</summary>
        private static readonly float[] OffLaneLateral = { 4f, 7f, 10f };

        private static readonly float[] OffLaneAlong = { 0f, 4f };

        private const double OffLaneSeconds = 4.0;

        private readonly List<(Vehicle blocker, EntityId mover, Vector2 dir, int depth)> _serving = new();
        private readonly List<Vector2> _single = new();

        private readonly UnitCostField _unitCosts;
        private readonly PathFinder _costFinder;
        private readonly PathCosts _costs = new();
        private readonly List<Vector2> _costBuffer = new();
        private readonly List<PathRequest> _pathQueue = new();
        private int _queueHead;

        /// <summary>Cells expanded by the routes planned round hulls this step, and the most in any step (tests).</summary>
        internal int PathNodesThisTick { get; private set; }

        internal int PathNodesMaxTick { get; private set; }

        /// <summary>Requests still waiting for the path budget.</summary>
        internal int PathQueueLength => _pathQueue.Count - _queueHead;

        /// <summary>Longest a request has waited for the path budget (seconds; tests).</summary>
        internal double PathQueueLongestWait { get; private set; }

        private readonly struct PathRequest
        {
            public PathRequest(EntityId vehicle, Vector2 goal, EntityId blocker, bool aside, int strikes, double at)
            {
                Vehicle = vehicle;
                Goal = goal;
                Blocker = blocker;
                Aside = aside;
                Strikes = strikes;
                At = at;
            }

            public EntityId Vehicle { get; }
            public Vector2 Goal { get; }
            public EntityId Blocker { get; }
            public bool Aside { get; }
            public int Strikes { get; }
            public double At { get; }
        }

        // ------------------------------------------------------------------ priorities

        /// <summary>
        /// Right of way: a vehicle is only asked to make way by a moving friend with a higher number.
        /// Moving beats parked; a long-range gun has range to spare and moves first; a direct-fire
        /// vehicle in contact is not sent sideways under fire; convoys and bosses never make way.
        /// </summary>
        internal int TrafficPriority(Vehicle v)
        {
            if (v.Def.Static) return int.MaxValue;
            if (v.Scripted || v.Def.Boss) return 100;
            var weapon = v.Def.Weapon;
            if (v.Order.Kind == OrderKind.Retreat || (weapon.MinRange > 0f && v.HasPath &&
                    _world.FindNearestEnemy(v, weapon.MinRange + 6f, requireVisible: true, layers: TargetLayers.Ground) != null))
                return 80;
            // A mover held up by the hull ahead still has a mover's right of way.
            if (v.HasPath && (MathF.Abs(v.Speed) > 0.3f || _world.Time - v.Traffic.LastBlockerTime < 1.0))
                return v.ManualOrder ? 65 : v.Engaged.IsValid ? 60 : 50;
            if (v.Traffic.YieldingTo.IsValid) return 40;
            if (v.OutOfAmmo) return 15;
            if (v.Target.IsValid)
            {
                var longRange = weapon.MinRange > 0f || weapon.Range >= 45f || v.Def.Class is UnitClass.TankHunter or UnitClass.Artillery;
                if (longRange) return 20;
                return _world.FindNearestEnemy(v, weapon.Range * 0.5f, requireVisible: true, layers: TargetLayers.Ground) != null ? 45 : 30;
            }
            return 10;
        }

        /// <summary>Standing still long enough, and not itself waiting, queued or backing out: it can be asked to make way.</summary>
        private bool Askable(Vehicle b)
        {
            if (b.Flying || b.Def.Static || b.Scripted || b.Def.Boss || b.Stunned || !b.IsAlive) return false;
            var t = b.Traffic;
            var now = _world.Time;
            if (now - t.ParkedSince < ParkedForAsk) return false;
            return !t.Reversing(now) && now >= t.HoldUntil && !t.WaitingOnYield && !t.QueueBehind.IsValid;
        }

        /// <summary>Keeps <see cref="TrafficState.ParkedSince"/> and notices new orders (a new order cancels any traffic overlay).</summary>
        private void TrackTraffic(Vehicle v)
        {
            var t = v.Traffic;
            if (!v.HasPath || MathF.Abs(v.Speed) < UnitCostField.ParkedSpeed)
            {
                if (double.IsPositiveInfinity(t.ParkedSince)) t.ParkedSince = _world.Time;
            }
            else
            {
                t.ParkedSince = double.PositiveInfinity;
            }
            if (SameOrder(v.Order, t.OrderSeen)) return;
            t.OrderSeen = v.Order;
            if (t.YieldingTo.IsValid) EndYield(v, resume: false);
            t.ReverseUntil = double.NegativeInfinity;
            t.HoldUntil = double.NegativeInfinity;
            t.QueueBehind = EntityId.None;
            t.YieldEscalations = 0;
            t.TrafficBoost = 0;
            t.OffLaneUntil = double.NegativeInfinity;
        }

        private static bool SameOrder(Order a, Order b) => a.Kind == b.Kind && a.Target == b.Target && a.Point == b.Point;

        /// <summary>
        /// Runs the traffic overlay for this step: backing out, waiting after backing out, or making
        /// way. True while one is active (the order's own driving waits).
        /// </summary>
        private bool TrafficOverlay(Vehicle v)
        {
            if (v.Flying) return false;
            var t = v.Traffic;
            var now = _world.Time;
            if (t.Reversing(now) || now < t.HoldUntil) return true;
            return t.YieldingTo.IsValid && UpdateYield(v);
        }

        // ------------------------------------------------------------------ asking to make way

        /// <summary>
        /// Posts a request for <paramref name="blocker"/> to make way for <paramref name="mover"/>,
        /// served at the start of the next step. Only a strictly higher priority asks; of several
        /// requests the strongest wins, ties to the lower id, whatever order they came in.
        /// </summary>
        private void PostYield(Vehicle mover, Vehicle blocker, int depth)
        {
            if (depth > MaxYieldDepth || blocker.Team != mover.Team || mover.Flying || !Askable(blocker)) return;
            var bt = blocker.Traffic;
            if (bt.YieldingTo == mover.Id || mover.Traffic.YieldingTo == blocker.Id) return;
            var pm = TrafficPriority(mover) + mover.Traffic.TrafficBoost;
            if ((_world.Time < bt.YieldCooldownUntil || bt.YieldingTo.IsValid) && pm < OverridePriority) return;
            if (pm <= TrafficPriority(blocker)) return;
            if (bt.PendingYield.IsValid &&
                (pm < bt.PendingPriority || (pm == bt.PendingPriority && mover.Id.Value > bt.PendingYield.Value))) return;
            bt.PendingYield = mover.Id;
            bt.PendingPriority = pm;
            bt.PendingDepth = depth;
            bt.PendingDir = MoverDirection(mover, blocker);
        }

        /// <summary>Which way the mover is going past the blocker: towards its first waypoint beyond it.</summary>
        private static Vector2 MoverDirection(Vehicle mover, Vehicle blocker)
        {
            var toBlocker = blocker.Position - mover.Position;
            if (mover.HasPath)
                for (var i = mover.PathIndex; i < mover.Path.Count; i++)
                {
                    var w = mover.Path[i];
                    if (Vector2.Dot(w - blocker.Position, toBlocker) <= 0f && i < mover.Path.Count - 1) continue;
                    var d = w - mover.Position;
                    if (d.LengthSquared() > 0.25f) return Vector2.Normalize(d);
                }
            return toBlocker.LengthSquared() > 0.01f ? Vector2.Normalize(toBlocker) : SimMath.Forward(mover.Heading);
        }

        /// <summary>Serves the requests posted last step, in the vehicle list's order (each one's outcome is decided by its own request only).</summary>
        private void ServeYieldRequests()
        {
            _serving.Clear();
            foreach (var b in _world.VehicleList)
            {
                var t = b.Traffic;
                if (!t.PendingYield.IsValid) continue;
                _serving.Add((b, t.PendingYield, t.PendingDir, t.PendingDepth));
                t.PendingYield = EntityId.None;
            }
            foreach (var (b, moverId, dir, depth) in _serving)
            {
                if (!b.IsAlive || !Askable(b) || !_world.TryGetVehicle(moverId, out var mover) || !mover.IsAlive) continue;
                if (!TryYieldSpot(b, mover, dir, depth, out var spot) &&
                    (!_world.Lanes.NoParkAt(b.Position) || !TryClearForward(b, mover, dir, out spot))) continue;
                StartYield(b, mover, dir, spot);
            }
        }

        /// <summary>
        /// The best place to make way to: sideways, on the side of the mover's route it already
        /// stands on (so it never crosses in front of it), off the route, clear of other hulls, off
        /// doorways, and for a gun one from which it can still shoot. A spot only another parked
        /// friend is in the way of passes the request on to that friend.
        /// </summary>
        private bool TryYieldSpot(Vehicle b, Vehicle mover, Vector2 dir, int depth, out Vector2 spot)
        {
            spot = default;
            var lanes = _world.Lanes;
            var grid = _world.Grid;
            var side = new Vector2(-dir.Y, dir.X);
            var lateralNow = Vector2.Dot(b.Position - mover.Position, side);
            var mySide = MathF.Abs(lateralNow) > 0.3f ? MathF.Sign(lateralNow) : (b.Id.Value & 1) == 0 ? 1f : -1f;
            var clear = b.Def.HullRadius + mover.Def.HullRadius + 1f;
            var best = float.MaxValue;
            Vehicle? passOn = null;
            var passOnScore = float.MaxValue;
            for (var pass = 0; pass < 2; pass++)
            {
                var s = pass == 0 ? mySide : -mySide;
                foreach (var k in LateralSteps)
                foreach (var along in AlongSteps)
                {
                    var p = b.Position + side * (s * k * clear) + dir * along;
                    if (!_world.Map.Contains(p) || !grid.IsWalkable(p) || !grid.LineOfSight(b.Position, p)) continue;
                    if (DistanceToRoute(mover, p, 25f) < clear) continue;
                    var f = lanes.At(p);
                    var score = Vector2.Distance(b.Position, p) + (pass == 1 ? 6f : 0f) +
                                ((f & LaneFlags.NoPark) != 0 ? 50f : 0f) + ((f & LaneFlags.Route) != 0 ? 8f : 0f) +
                                (KeepsTargetInReach(b, p) ? 0f : 10f);
                    if (score >= best) continue;
                    if (HullAt(b, p) is { } other)
                    {
                        if (other.Team == b.Team && score < passOnScore)
                        {
                            passOn = other;
                            passOnScore = score;
                        }
                        continue;
                    }
                    best = score;
                    spot = p;
                }
            }
            if (best < float.MaxValue) return true;
            // Hemmed in by another parked friend: it makes way first (the request is passed on once).
            if (passOn != null && passOn != mover) PostYield(mover, passOn, depth + 1);
            return false;
        }

        /// <summary>
        /// No room to the side in a doorway: clear it forwards, the way the mover is going, to the
        /// first open ground past it (then to its side there if possible).
        /// </summary>
        private bool TryClearForward(Vehicle b, Vehicle mover, Vector2 dir, out Vector2 spot)
        {
            spot = default;
            var lanes = _world.Lanes;
            var grid = _world.Grid;
            var side = new Vector2(-dir.Y, dir.X);
            var clear = b.Def.HullRadius + mover.Def.HullRadius + 1f;
            for (var along = 4f; along <= 24f; along += 2f)
            {
                var ahead = b.Position + dir * along;
                if (!_world.Map.Contains(ahead) || !grid.IsWalkable(ahead) || !grid.LineOfSight(b.Position, ahead)) return false;
                if (lanes.NoParkAt(ahead)) continue;
                foreach (var k in LateralSteps)
                    for (var s = -1; s <= 1; s += 2)
                    {
                        var p = ahead + side * (s * k * clear);
                        if (!_world.Map.Contains(p) || !grid.IsWalkable(p) || !grid.LineOfSight(ahead, p) || lanes.NoParkAt(p)) continue;
                        if (HullAt(b, p) != null || DistanceToRoute(mover, p, 30f) < clear) continue;
                        spot = p;
                        return true;
                    }
                if (HullAt(b, ahead) != null) return false;
                spot = ahead;
                return true;
            }
            return false;
        }

        /// <summary>The ground hull (other than <paramref name="v"/>) that would overlap <paramref name="v"/> standing at <paramref name="point"/>.</summary>
        private Vehicle? HullAt(Vehicle v, Vector2 point)
        {
            var reach = v.Def.HullBound + _maxBound;
            var half = SimMath.Forward(v.Heading) * v.Def.HullHalf;
            for (var i = LowerBound(point.X - reach); i < _ground.Count; i++)
            {
                var o = _ground[i];
                if (o.Position.X > point.X + reach) break;
                if (o == v || !o.IsAlive) continue;
                Spine(o, out var a, out var b);
                ClosestPoints(point - half, point + half, a, b, out var c1, out var c2);
                if (Vector2.DistanceSquared(c1, c2) < Square(v.Def.HullRadius + o.Def.HullRadius + 0.3f)) return o;
            }
            return null;
        }

        /// <summary>How close <paramref name="p"/> comes to the mover's route over the next <paramref name="lookAhead"/> metres.</summary>
        private static float DistanceToRoute(Vehicle mover, Vector2 p, float lookAhead)
        {
            var from = mover.Position;
            var best = Vector2.Distance(p, from);
            var left = lookAhead;
            if (mover.HasPath)
            {
                for (var i = mover.PathIndex; i < mover.Path.Count && left > 0f; i++)
                {
                    var to = mover.Path[i];
                    var length = Vector2.Distance(from, to);
                    if (length > left) to = from + (to - from) * (left / length);
                    best = MathF.Min(best, SegmentDistance(p, from, to));
                    left -= length;
                    from = to;
                }
            }
            else
            {
                best = MathF.Min(best, SegmentDistance(p, from, from + SimMath.Forward(mover.Heading) * lookAhead));
            }
            return best;
        }

        private static float SegmentDistance(Vector2 p, Vector2 a, Vector2 b)
        {
            var ab = b - a;
            var length = ab.LengthSquared();
            var t = length > 1e-6f ? Math.Clamp(Vector2.Dot(p - a, ab) / length, 0f, 1f) : 0f;
            return Vector2.Distance(p, a + ab * t);
        }

        /// <summary>A gun with something to shoot keeps it in reach from <paramref name="p"/>.</summary>
        private bool KeepsTargetInReach(Vehicle b, Vector2 p)
        {
            var id = b.Order.Kind == OrderKind.Attack ? b.Order.Target : b.Target;
            if (!_world.TryGetTarget(id, out var target) || !target.IsAlive) return true;
            var weapon = b.Def.Weapon;
            var d = Vector2.Distance(p, target.Position);
            return d >= weapon.MinRange && d - target.Radius <= weapon.Range * 0.95f;
        }

        private void StartYield(Vehicle b, Vehicle mover, Vector2 dir, Vector2 spot)
        {
            var t = b.Traffic;
            // Already making way (backed out, now stepping aside): the order it will take up again stays the first one.
            if (!t.YieldingTo.IsValid)
            {
                t.OrderAtYield = b.Order;
                t.ResumeHadPath = b.HasPath;
            }
            t.YieldingTo = mover.Id;
            t.YieldOrigin = b.Position;
            t.YieldSpot = spot;
            t.YieldDir = dir;
            t.YieldUntil = _world.Time + YieldMaxSeconds;
            t.YieldArrivedAt = double.PositiveInfinity;
            t.Yields++;
            Vehicle.PathTrace?.Invoke(b, $"Yield to #{mover.Id.Value}");
            _single.Clear();
            _single.Add(spot);
            b.SetPath(_single, spot);
            // A spot it had to leave is no longer its post: it would only drive straight back.
            if (b.Order.Kind == OrderKind.Idle) b.GuardPoint = spot;
        }

        /// <summary>
        /// A yield in progress: it ends once the mover is past (or gone), the vehicle has held at
        /// its spot long enough, or the yield ran out of time. False once it has ended.
        /// </summary>
        private bool UpdateYield(Vehicle v)
        {
            var t = v.Traffic;
            var now = _world.Time;
            if (!v.HasPath && double.IsPositiveInfinity(t.YieldArrivedAt)) t.YieldArrivedAt = now;
            var done = now >= t.YieldUntil || now - t.YieldArrivedAt >= YieldHoldSeconds ||
                       !_world.TryGetVehicle(t.YieldingTo, out var mover) || !mover.IsAlive ||
                       Vector2.Dot(mover.Position - t.YieldOrigin, t.YieldDir) > mover.Def.HullBound + v.Def.HullBound;
            if (!done) return true;
            EndYield(v, resume: true);
            return false;
        }

        /// <summary>Ends a yield; with <paramref name="resume"/> the vehicle takes up its order again from where it now stands.</summary>
        private void EndYield(Vehicle v, bool resume)
        {
            var t = v.Traffic;
            t.YieldingTo = EntityId.None;
            t.YieldCooldownUntil = _world.Time + YieldCooldown;
            t.YieldArrivedAt = double.PositiveInfinity;
            if (!resume) return;
            Vehicle.PathTrace?.Invoke(v, "Yield done");
            // On the way somewhere: on to the order's destination (a chase picks its own route
            // again next step). Holding, guarding or firing: from here.
            if (v.Order.Kind is OrderKind.Move or OrderKind.Retreat or OrderKind.AttackMove && (t.ResumeHadPath || v.Order.Kind == OrderKind.AttackMove))
                _world.PathTo(v, v.Order.Point);
            else v.ClearPath();
            v.RepathTimer = 0f;
        }

        // ------------------------------------------------------------------ the mover's side

        /// <summary>
        /// The hull ahead is a friend: ask it to make way, wait for it, queue behind it, or note a
        /// head-on meeting in a doorway. True when the mover should hold its line (crawl or wait)
        /// rather than steer round.
        /// </summary>
        private bool Negotiate(Vehicle v, Vehicle blocker, Vector2 forward, bool wasWaiting, ref float slowFor)
        {
            var t = v.Traffic;
            var bt = blocker.Traffic;
            var now = _world.Time;
            if (blocker.HasPath && Vector2.Dot(SimMath.Forward(blocker.Heading), forward) < -0.5f)
            {
                // Head-on: in a doorway one of the two backs out (decided next step); elsewhere
                // both keep right as before. One already making way for the other is left to it.
                if (!t.YieldingTo.IsValid && !bt.YieldingTo.IsValid &&
                    ((_world.Lanes.At(v.Position) & (LaneFlags.Narrow | LaneFlags.NoPark)) != 0 ||
                     (_world.Lanes.At(blocker.Position) & (LaneFlags.Narrow | LaneFlags.NoPark)) != 0))
                    t.HeadOn = blocker.Id;
                return false;
            }
            if (bt.ReverseFor == v.Id && bt.Reversing(now))
            {
                // It is backing out for us: follow it in.
                slowFor = MathF.Min(slowFor, MathF.Abs(blocker.Speed) * 0.9f);
                return true;
            }
            if (t.QueueBehind == blocker.Id)
            {
                var gap = Vector2.Distance(v.Position, blocker.Position) - v.Def.HullBound - blocker.Def.HullBound;
                slowFor = MathF.Min(slowFor, gap > 2f ? MathF.Max(0f, blocker.Speed) : 0f);
                PostYield(v, blocker, 0);
                return true;
            }
            PostYield(v, blocker, 0);
            if (bt.YieldingTo == v.Id)
            {
                slowFor = MathF.Min(slowFor, v.Def.Speed * 0.25f);
                if (!wasWaiting) t.WaitStarted = now;
                t.WaitingOnYield = true;
                // Crawl straight on behind it: a swerve started a moment ago would only run into a wall.
                if (v.AvoidUntil > now) v.AvoidUntil = now;
                return true;
            }
            return false;
        }

        private void NoteBlocker(Vehicle v, Vehicle blocker)
        {
            v.Traffic.LastBlocker = blocker.Id;
            v.Traffic.LastBlockerTime = _world.Time;
        }

        /// <summary>The hull that last stood in the way, if that was within the last second.</summary>
        private Vehicle? RecentBlocker(Vehicle v)
        {
            var t = v.Traffic;
            if (_world.Time - t.LastBlockerTime > 1.0 || !_world.TryGetVehicle(t.LastBlocker, out var b) || !b.IsAlive) return null;
            return b;
        }

        // ------------------------------------------------------------------ head-on in a doorway

        /// <summary>
        /// Resolves the head-on meetings noted last step. The loser (lower priority; on a tie the
        /// one nearer open ground behind it; then the higher id) backs straight out.
        /// </summary>
        private void ServeHeadOns()
        {
            var now = _world.Time;
            foreach (var v in _world.VehicleList)
            {
                var t = v.Traffic;
                if (!t.HeadOn.IsValid) continue;
                var otherId = t.HeadOn;
                t.HeadOn = EntityId.None;
                if (!v.IsAlive || !_world.TryGetVehicle(otherId, out var o) || !o.IsAlive) continue;
                if (o.Traffic.HeadOn == v.Id) o.Traffic.HeadOn = EntityId.None;
                if (t.Reversing(now) || o.Traffic.Reversing(now) || now < t.HoldUntil || now < o.Traffic.HoldUntil ||
                    t.YieldingTo.IsValid || o.Traffic.YieldingTo.IsValid) continue;
                var pv = TrafficPriority(v);
                var po = TrafficPriority(o);
                var dv = ReverseRoom(v);
                var d2 = ReverseRoom(o);
                Vehicle loser;
                if (pv != po) loser = pv < po ? v : o;
                else if (MathF.Abs(dv - d2) > 0.5f) loser = dv < d2 ? v : o;
                else loser = v.Id.Value > o.Id.Value ? v : o;
                // Boxed in behind: the other one backs out instead.
                if (float.IsPositiveInfinity(loser == v ? dv : d2)) loser = loser == v ? o : v;
                var room = loser == v ? dv : d2;
                if (float.IsPositiveInfinity(room)) continue;
                StartReverse(loser, loser == v ? o : v, room);
            }
        }

        /// <summary>How far a vehicle must back up to get its whole hull out of the doorway (+inf when it cannot: a wall or a hull behind).</summary>
        private float ReverseRoom(Vehicle v)
        {
            var back = -SimMath.Forward(v.Heading);
            var lanes = _world.Lanes;
            for (var d = 1f; d <= HeadOnReverseMax; d += 1f)
            {
                var p = v.Position + back * d;
                if (!_world.Map.Contains(p) || !_world.Grid.IsWalkable(p) || HullAt(v, p) != null) return float.PositiveInfinity;
                if ((lanes.At(p) & (LaneFlags.Narrow | LaneFlags.NoPark)) == 0) return MathF.Min(HeadOnReverseMax, d + v.Def.HullHalf);
            }
            return HeadOnReverseMax;
        }

        private void StartReverse(Vehicle v, Vehicle? forWhom, float distance)
        {
            var t = v.Traffic;
            t.ReverseFor = forWhom?.Id ?? EntityId.None;
            t.ReverseLeft = distance;
            t.ReverseUntil = _world.Time + distance / MathF.Max(0.5f, v.Def.Speed * ReverseSpeedShare) + 1.5;
            if (forWhom != null) t.Yields++;
            Vehicle.PathTrace?.Invoke(v, $"Reverse {distance:0.0} for #{t.ReverseFor.Value}");
        }

        /// <summary>Backs straight out along the hull's axis (tracks need not turn round), then waits beside the mouth.</summary>
        private void DriveReverse(Vehicle v, float dt)
        {
            var t = v.Traffic;
            var def = v.Def;
            var back = -SimMath.Forward(v.Heading);
            v.Speed = SimMath.MoveTowards(v.Speed, -def.Speed * ReverseSpeedShare, def.Speed * 2f * dt);
            var step = MathF.Max(0f, -v.Speed) * dt;
            var next = v.Position + back * step;
            if (t.ReverseLeft <= 0f || !_world.Map.Contains(next) || !_world.Grid.IsWalkable(next) ||
                (step > 0f && HullAt(v, next) is { } behind && Vector2.Dot(behind.Position - v.Position, back) > 0f))
            {
                EndReverse(v);
                return;
            }
            v.Position = next;
            t.ReverseLeft -= step;
        }

        private void EndReverse(Vehicle v)
        {
            var t = v.Traffic;
            t.ReverseUntil = double.NegativeInfinity;
            v.Speed = 0f;
            v.StuckTimer = 0f;
            v.StuckSample = v.Position;
            var forId = t.ReverseFor;
            t.ReverseFor = EntityId.None;
            if (!forId.IsValid || !_world.TryGetVehicle(forId, out var winner) || !winner.IsAlive) return;
            // Out of the doorway: step aside for the other one if there is room, else wait here.
            var dir = MoverDirection(winner, v);
            if (TryYieldSpot(v, winner, dir, MaxYieldDepth, out var spot)) StartYield(v, winner, dir, spot);
            else t.HoldUntil = _world.Time + HeadOnWait;
        }

        // ------------------------------------------------------------------ stuck: escalate, route round, back off

        /// <summary>
        /// A stuck window with no progress. Waiting for a friend making way, or queued behind one,
        /// is not being stuck. Otherwise: ask the friend in the way again with more weight (twice),
        /// then plan a route round the parked hulls (twice), then back off, then give up.
        /// </summary>
        private void OnNoProgress(Vehicle v)
        {
            var t = v.Traffic;
            var now = _world.Time;
            var blocker = RecentBlocker(v);
            if (blocker != null && blocker.Team == v.Team && blocker.Traffic.YieldingTo != v.Id && t.YieldEscalations < 2 && Askable(blocker))
            {
                t.YieldEscalations++;
                t.TrafficBoost += 10;
                PostYield(v, blocker, 0);
                return;
            }
            v.StuckStrikes++;
            if (v.StuckStrikes >= StuckStrikesToGiveUp)
            {
                GiveUp(v);
            }
            else if (v.StuckStrikes == StuckStrikesToGiveUp - 1)
            {
                // Wedged: back straight off if the way behind is free (tracks need not pivot), else detour.
                if (CanReverse(v, BackOffDistance)) StartReverse(v, null, BackOffDistance);
                else if (TryDetour(v, v.Path[v.PathIndex], out var back)) v.Path.Insert(v.PathIndex, back);
            }
            else
            {
                RequestCostedPath(v, blocker, aside: v.StuckStrikes >= 2);
            }
        }

        private bool CanReverse(Vehicle v, float distance)
        {
            var back = -SimMath.Forward(v.Heading);
            for (var d = 1f; d <= distance; d += 1f)
            {
                var p = v.Position + back * d;
                if (!_world.Map.Contains(p) || !_world.Grid.IsWalkable(p) || HullAt(v, p) != null) return false;
            }
            return true;
        }

        /// <summary>
        /// Queues a route to the same goal planned round the parked hulls (and dearer still round
        /// the one in the way). It is planned at the end of this step, or a later one if the step's
        /// search budget is spent.
        /// </summary>
        private void RequestCostedPath(Vehicle v, Vehicle? blocker, bool aside)
        {
            var t = v.Traffic;
            if (_world.Time - t.LastCostRepath < MinCostRepathGap) return;
            for (var i = _queueHead; i < _pathQueue.Count; i++)
                if (_pathQueue[i].Vehicle == v.Id) return;
            t.LastCostRepath = _world.Time;
            _pathQueue.Add(new PathRequest(v.Id, v.PathGoal, blocker?.Id ?? EntityId.None, aside, v.StuckStrikes, _world.Time));
        }

        /// <summary>
        /// Plans the queued routes, first in first out, until the step's budget of searched cells is
        /// spent (the rest wait for the next step). The budget counts cells, never milliseconds, so
        /// the outcome is the same on every machine.
        /// </summary>
        private void RunPathQueue()
        {
            PathNodesThisTick = 0;
            var first = true;
            while (_queueHead < _pathQueue.Count)
            {
                var remaining = PathNodeBudgetPerTick - PathNodesThisTick;
                if (remaining <= 1 || (!first && remaining < MinSearchBudget)) break;
                var request = _pathQueue[_queueHead++];
                PathQueueLongestWait = Math.Max(PathQueueLongestWait, _world.Time - request.At);
                if (!_world.TryGetVehicle(request.Vehicle, out var v) || !v.IsAlive || !v.HasPath ||
                    Vector2.DistanceSquared(v.PathGoal, request.Goal) > 1f) continue;
                first = false;
                _unitCosts.RefreshIfStale(_world);
                var blocker = _world.TryGetVehicle(request.Blocker, out var b) && b.IsAlive && !b.Flying ? b : null;
                _costs.Extra = _unitCosts.For(v.Team);
                _costs.Start = v.Position;
                _costs.StartSkip = v.Def.HullBound + 1f;
                _costs.HasBlocker = blocker != null;
                if (blocker != null)
                {
                    Spine(blocker, out _costs.BlockerA, out _costs.BlockerB);
                    _costs.BlockerRadius = blocker.Def.HullRadius + v.Def.HullRadius + 0.5f;
                }
                _costs.MaxExpansions = Math.Min(MaxNodesPerSearch, remaining - 1);
                var found = _costFinder.TryFindPath(v.Position, request.Goal, _costBuffer, _costs);
                PathNodesThisTick += _costs.Expansions;
                ApplyCostedPath(v, request, blocker, found);
            }
            PathNodesMaxTick = Math.Max(PathNodesMaxTick, PathNodesThisTick);
            if (_queueHead < _pathQueue.Count) return;
            _pathQueue.Clear();
            _queueHead = 0;
        }

        private void ApplyCostedPath(Vehicle v, PathRequest request, Vehicle? blocker, bool found)
        {
            var t = v.Traffic;
            var strikes = request.Strikes;
            if (!found)
            {
                // No cheaper way found in budget: the plain replan, as before.
                _world.PathTo(v, request.Goal);
                v.StuckStrikes = strikes;
                if (request.Aside) StepAside(v);
                return;
            }
            if (blocker != null && blocker.Team == v.Team &&
                (PathLength(v.Position, _costBuffer) > RemainingLength(v) * DetourCap + DetourSlack ||
                 PassesNear(v, _costBuffer, blocker, NoAlternativeLength)))
            {
                // No real way round (a single gate): wait behind it, and keep asking it to move.
                t.QueueBehind = blocker.Id;
                t.QueueUntil = _world.Time + QueueSeconds;
                PostYield(v, blocker, 0);
                return;
            }
            v.SetPath(_costBuffer, request.Goal);
            v.StuckStrikes = strikes;
            t.CostPathUntil = _world.Time + CostPathKeep;
            t.CostGoal = request.Goal;
            if (request.Aside) StepAside(v);
        }

        /// <summary>Wedged in a crowd, or against something, a second time: a step aside first, then the route.</summary>
        private void StepAside(Vehicle v)
        {
            if (!v.HasPath) return;
            if (Crowded(v) && TryUnjam(v, out var aside)) v.Path.Insert(v.PathIndex, aside);
            else if (TryDetour(v, v.Path[v.PathIndex], out var detour)) v.Path.Insert(v.PathIndex, detour);
        }

        private static float PathLength(Vector2 from, List<Vector2> path)
        {
            var length = 0f;
            foreach (var p in path)
            {
                length += Vector2.Distance(from, p);
                from = p;
            }
            return length;
        }

        private static float RemainingLength(Vehicle v)
        {
            var length = 0f;
            var from = v.Position;
            for (var i = v.PathIndex; i < v.Path.Count; i++)
            {
                length += Vector2.Distance(from, v.Path[i]);
                from = v.Path[i];
            }
            return length;
        }

        /// <summary>Whether the first <paramref name="length"/> metres of a route still pass through the blocker's hull.</summary>
        private static bool PassesNear(Vehicle v, List<Vector2> path, Vehicle blocker, float length)
        {
            Spine(blocker, out var a, out var b);
            var reach = blocker.Def.HullRadius + v.Def.HullRadius;
            var from = v.Position;
            var left = length;
            foreach (var p in path)
            {
                if (left <= 0f) break;
                var to = p;
                var d = Vector2.Distance(from, to);
                if (d > left) to = from + (to - from) * (left / d);
                ClosestPoints(from, to, a, b, out var c1, out var c2);
                if (Vector2.DistanceSquared(c1, c2) < reach * reach) return true;
                left -= d;
                from = to;
            }
            return false;
        }

        /// <summary>A route planned round parked hulls moments ago, to about the same goal: a plain replan must not undo it yet.</summary>
        private bool KeepCostedPath(Vehicle v, Vector2 goal) =>
            v.HasPath && _world.Time < v.Traffic.CostPathUntil && Vector2.DistanceSquared(goal, v.Traffic.CostGoal) < 64f;

        // ------------------------------------------------------------------ holding fire position off the lanes

        /// <summary>
        /// Standing in the way where it holds to fire: in a doorway or its mouth, or on a main route
        /// with a friend coming along it close behind.
        /// </summary>
        private bool InTheWay(Vehicle v, out bool noPark)
        {
            var f = _world.Lanes.At(v.Position);
            noPark = (f & LaneFlags.NoPark) != 0;
            return noPark || ((f & LaneFlags.Route) != 0 && FriendlyTrafficBehind(v));
        }

        /// <summary>A friend driving along a route that passes through where this vehicle stands, within 25 m.</summary>
        private bool FriendlyTrafficBehind(Vehicle v)
        {
            foreach (var o in _ground)
            {
                if (o == v || o.Team != v.Team || !o.IsAlive || o.Def.Static || !o.HasPath || o.Speed < 0.5f) continue;
                if (Vector2.DistanceSquared(o.Position, v.Position) > TrafficBehindReach * TrafficBehindReach) continue;
                if (DistanceToRoute(o, v.Position, TrafficBehindReach) < v.Def.HullRadius + o.Def.HullRadius + 0.5f) return true;
            }
            return false;
        }

        /// <summary>
        /// A spot a few metres to the side (and a little ahead) from which the target is still in
        /// reach and in sight, off the doorways and on a less used lane than here, clear of other
        /// hulls and in plain line to drive to.
        /// </summary>
        private bool TryOffLaneSpot(Vehicle v, IDamageable target, out Vector2 spot)
        {
            spot = default;
            var lanes = _world.Lanes;
            var grid = _world.Grid;
            var weapon = v.Def.Weapon;
            var here = lanes.At(v.Position);
            var hereNoPark = (here & LaneFlags.NoPark) != 0;
            var hereCount = (here & LaneFlags.Route) != 0 ? lanes.RouteCountAt(v.Position) : 0;
            var forward = SimMath.Forward(v.Heading);
            var side = new Vector2(-forward.Y, forward.X);
            var best = float.MaxValue;
            foreach (var lateral in OffLaneLateral)
            foreach (var along in OffLaneAlong)
                for (var s = -1; s <= 1; s += 2)
                {
                    var p = v.Position + side * (s * lateral) + forward * along;
                    if (!_world.Map.Contains(p) || !grid.IsWalkable(p) || !grid.LineOfSight(v.Position, p)) continue;
                    var f = lanes.At(p);
                    if ((f & LaneFlags.NoPark) != 0) continue;
                    var count = (f & LaneFlags.Route) != 0 ? lanes.RouteCountAt(p) : 0;
                    if (!hereNoPark && count >= hereCount) continue;
                    var reach = Vector2.Distance(p, target.Position) - target.Radius;
                    if (reach > weapon.Range * 0.95f || Vector2.Distance(p, target.Position) < weapon.MinRange + 1f) continue;
                    var score = lateral + along * 0.5f + ((f & LaneFlags.Road) != 0 ? 6f : 0f) + count * 8f -
                                (lanes.ClearanceAt(p) >= 4 ? 3f : 0f);
                    if (score >= best || HullAt(v, p) != null || !ClearShotFrom(v, p, target, weapon)) continue;
                    best = score;
                    spot = p;
                }
            return best < float.MaxValue;
        }

        /// <summary>Whether the weapon would have a clear line of fire at the target from <paramref name="p"/>.</summary>
        private bool ClearShotFrom(Vehicle v, Vector2 p, IDamageable target, WeaponDef weapon)
        {
            if (v.Flying || target is Vehicle { Flying: true } || weapon.Indirect) return true;
            return !_world.Cover.TryFirstHit(p, target.Position, v.Radius * 0.6f, target is Vehicle ? target.Radius * 0.5f : 0f, target as Prop, out _);
        }

        /// <summary>A parkable spot near <paramref name="p"/>, one cell further out than the nearest so it is not on the doorway's edge.</summary>
        private bool TryStandBeside(Vector2 p, float reach, out Vector2 spot)
        {
            var lanes = _world.Lanes;
            if (!lanes.TryParkable(p, reach, out spot)) return false;
            var away = spot - p;
            if (away.LengthSquared() < 0.01f) return true;
            var further = spot + Vector2.Normalize(away) * _world.Grid.CellSize;
            if (_world.Grid.IsWalkable(further) && !lanes.NoParkAt(further) && _world.Grid.LineOfSight(spot, further)) spot = further;
            return true;
        }
    }
}
