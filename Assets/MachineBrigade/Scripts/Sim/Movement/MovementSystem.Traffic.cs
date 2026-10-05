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
        private static int MaxYieldDepth => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.MaxYieldDepth;

        /// <summary>Sideways steps of a yield, in multiples of both hulls' radii plus a metre, and steps along the mover's way.</summary>
        private static readonly float[] LateralSteps = { 1.0f, 1.6f, 2.4f };

        private static readonly float[] AlongSteps = { 0f, 4f, 8f, -4f };

        /// <summary>Yield-spot score per radian the yielder has to turn to drive there.</summary>
        private const float YieldTurnCost = 3f;

        /// <summary>A yield lasts at most this long (which also bounds the reload it pauses).</summary>
        private static double YieldMaxSeconds => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.YieldMaxSeconds;

        /// <summary>Once at its spot, the yielding vehicle holds until the mover is past, or this long.</summary>
        private static double YieldHoldSeconds => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.YieldHoldSeconds;

        /// <summary>After making way it is not asked again for this long (except by priority 80 and up).</summary>
        private static double YieldCooldown => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.YieldCooldown;

        /// <summary>How long a mover waits behind a friend making way before it counts as stuck.</summary>
        private static double YieldWaitSeconds => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.YieldWaitSeconds;

        /// <summary>Priorities from this up are obeyed even by a vehicle already yielding or resting after a yield.</summary>
        private const int OverridePriority = 80;

        /// <summary>Friends standing this close to a mover's destination are not asked to make way (the group's rendezvous, as in TacticalAi).</summary>
        private static float GatherReach => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.GatherReach;

        /// <summary>A unit's routes planned round parked hulls come at least this far apart.</summary>
        private static double MinCostRepathGap => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.MinCostRepathGap;

        /// <summary>A route planned round parked hulls is kept this long before a plain replan may replace it.</summary>
        private const double CostPathKeep = 3.0;

        /// <summary>Cells all routes planned round hulls may expand in one step, and one of them at most.</summary>
        internal static int PathNodeBudgetPerTick => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.PathNodeBudgetPerTick;

        private static int MaxNodesPerSearch => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.MaxNodesPerSearch;

        /// <summary>A queued search starts only with this much of the step's budget left (the first always runs).</summary>
        private static int MinSearchBudget => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.MinSearchBudget;

        /// <summary>
        /// Extra step cost of the cells under the hull in the way (x13 at the path finder's 0.1
        /// scale), and of one that cannot move at all (x26: a detour of a few dozen metres is cheaper).
        /// </summary>
        private const int BlockerCost = 120, ImmovableBlockerCost = 250;

        /// <summary>A route round the hulls longer than this share of the plain one (plus a few metres) is no way round.</summary>
        private static float DetourCap => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.DetourCap;

        /// <summary>The detour cap on the second route planned round the hulls: still stuck behind it, a longer way round is worth it.</summary>
        private const float DetourCapLate = 3f;

        private const float DetourSlack = 8f;

        /// <summary>A route round that still passes the blocker within this many metres is no way round either.</summary>
        private static float NoAlternativeLength => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.NoAlternativeLength;

        /// <summary>How long a vehicle with no way round waits behind the hull before it tries anything else.</summary>
        private static double QueueSeconds => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.QueueSeconds;

        /// <summary>A head-on loser backs out at most this far, at this share of its speed, then waits this long.</summary>
        private static float HeadOnReverseMax => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.HeadOnReverseMax;

        private static float ReverseSpeedShare => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.ReverseSpeedShare;
        private static double HeadOnWait => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.HeadOnWait;

        /// <summary>A plain back-off when wedged: this many metres straight back.</summary>
        private static float BackOffDistance => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.BackOffDistance;

        /// <summary>Holding on a main route, a friend coming along it this close behind means stepping off.</summary>
        private static float TrafficBehindReach => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.TrafficBehindReach;

        /// <summary>Sideways offsets and steps ahead tried when stepping off the lane to hold fire position.</summary>
        private static readonly float[] OffLaneLateral = { 4f, 7f, 10f };

        private static readonly float[] OffLaneAlong = { 0f, 4f };

        private static double OffLaneSeconds => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.OffLaneSeconds;

        private readonly List<(Vehicle blocker, EntityId mover, Vector2 dir, int depth, bool forced)> _serving = new();
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
            public PathRequest(EntityId vehicle, Vector2 goal, EntityId blocker, bool aside, int strikes, double at, CostedKind kind = CostedKind.Stuck)
            {
                Kind = kind;
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

            /// <summary>AI MASTER P1: why it was asked (a stuck window, a stage 4 corridor replan, a wreck across the route).</summary>
            public CostedKind Kind { get; }
        }

        /// <summary>AI MASTER P1: what a route planned round the hulls is for.</summary>
        internal enum CostedKind : byte
        {
            /// <summary>The stuck ladder (prompt 12): may queue behind a hull with no way round.</summary>
            Stuck,

            /// <summary>Stage 4 / 5 (spec 38): taken only when under ai.navigation.corridorAltMax times the current route.</summary>
            Corridor,

            /// <summary>A new wreck on the route (spec 39): planned at once, whatever the gap since the last one.</summary>
            Wreck,
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
            // On its way somewhere, held up or not, it has a mover's right of way: movers do not ask
            // each other to make way (a column would shuffle itself), only after getting nowhere
            // (see OnNoProgress) do they ask with more weight.
            if (v.HasPath) return v.ManualOrder ? 65 : v.Engaged.IsValid ? 60 : 50;
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
            return !t.Reversing(now) && now >= t.HoldUntil && !t.WaitingOnYield && !t.QueueBehind.IsValid && t.GateWaitId == 0;
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
            // AI MASTER P1: a new order starts a new jam episode and a new anomaly watch (spec 185).
            t.OrderAt = _world.Time;
            t.AnomalyLogged = false;
            t.Jam.Reset();
            t.NoProgressWindows = 0;
            if (t.YieldingTo.IsValid) EndYield(v, resume: false);
            t.GateWaitId = 0;
            t.WaitingForGate = false;
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
            if (t.GateWaitId != 0) return UpdateGateWait(v);
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
            // One standing where the mover is going is part of the group gathering there: it is not
            // sent away (the mover settles beside it, see the arrival rule in DetectStuck).
            if (mover.HasPath && Vector2.DistanceSquared(blocker.Position, mover.PathGoal) < GatherReach * GatherReach) return;
            // Nor is a member of the same group bound for the same place: the ones there first hold
            // their slots and the rest settle round them (asking each other to make way, a marching
            // group never comes to rest).
            if (SameDestination(mover, blocker)) return;
            // One holding its ground in the open (arrived, gathering, dug in) is driven round, not
            // sent away: only on a road, in a narrow pass or a doorway does it make way.
            if (Holding(blocker) && (_world.Lanes.At(blocker.Position) & (LaneFlags.Road | LaneFlags.Narrow | LaneFlags.NoPark)) == 0) return;
            var bt = blocker.Traffic;
            if (bt.YieldingTo == mover.Id || mover.Traffic.YieldingTo == blocker.Id) return;
            var pm = TrafficPriority(mover) + mover.Traffic.TrafficBoost;
            if ((_world.Time < bt.YieldCooldownUntil || bt.YieldingTo.IsValid) && pm < OverridePriority) return;
            if (pm <= TrafficPriority(blocker)) return;
            if (bt.PendingYield.IsValid && (bt.PendingForced ||
                pm < bt.PendingPriority || (pm == bt.PendingPriority && mover.Id.Value > bt.PendingYield.Value))) return;
            bt.PendingYield = mover.Id;
            bt.PendingPriority = pm;
            bt.PendingDepth = depth;
            bt.PendingDir = MoverDirection(mover, blocker);
        }

        /// <summary>Both are on the same kind of order to (nearly) the same point: one group on the way to one place.</summary>
        private static bool SameDestination(Vehicle a, Vehicle b) =>
            a.Order.Kind is OrderKind.Move or OrderKind.AttackMove or OrderKind.Retreat && b.Order.Kind == a.Order.Kind &&
            Vector2.DistanceSquared(a.Order.Point, b.Order.Point) < SameGoalReach * SameGoalReach;

        /// <summary>Not on its way anywhere: idle, or at the end of its order's path.</summary>
        private static bool Holding(Vehicle v) => v.Order.Kind == OrderKind.Idle || !v.HasPath;

        /// <summary>Order points this close belong to one group's move (its formation slots).</summary>
        private static float SameGoalReach => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.SameGoalReach;

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
                _serving.Add((b, t.PendingYield, t.PendingDir, t.PendingDepth, t.PendingForced));
                t.PendingYield = EntityId.None;
                t.PendingForced = false;
            }
            foreach (var (b, moverId, dir, depth, forced) in _serving)
            {
                // AI MASTER P1: the coordinator's requests (stage 3, deadlocks) are served even to one not askable.
                if (!b.IsAlive || (!forced && !Askable(b)) || !_world.TryGetVehicle(moverId, out var mover) || !mover.IsAlive) continue;
                if (forced && b.Traffic.YieldingTo.IsValid) continue;
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
                    // (A spot behind costs a slow pivot there and another back: worth several metres.)
                    var turn = MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(p - b.Position) - b.Heading));
                    var score = Vector2.Distance(b.Position, p) + turn * YieldTurnCost + (pass == 1 ? 6f : 0f) +
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
            ResumeOrder(v);
        }

        /// <summary>
        /// Takes up the order a traffic overlay interrupted: on the way somewhere, on to the order's
        /// destination (a chase picks its own route again next step); holding, guarding or firing,
        /// from here.
        /// </summary>
        private void ResumeOrder(Vehicle v)
        {
            if (v.Order.Kind is OrderKind.Move or OrderKind.Retreat or OrderKind.AttackMove && (v.Traffic.ResumeHadPath || v.Order.Kind == OrderKind.AttackMove))
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
            // (One waiting its turn at a doorway is as good as parked: it is asked to step aside.)
            if (!bt.WaitingForGate && !t.WaitingForGate && Oncoming(v, blocker, forward))
            {
                // Head-on: in a doorway one of the two backs out (decided next step); elsewhere
                // both keep right as before. One already making way for the other is left to it.
                if (!t.YieldingTo.IsValid && !bt.YieldingTo.IsValid &&
                    ((_world.Lanes.At(v.Position) & (LaneFlags.Narrow | LaneFlags.NoPark)) != 0 ||
                     (_world.Lanes.At(blocker.Position) & (LaneFlags.Narrow | LaneFlags.NoPark)) != 0 ||
                     // In the open too once keeping right has failed: both pressed nose to nose.
                     (now - t.ParkedSince > HeadOnOpenWait && now - bt.ParkedSince > HeadOnOpenWait)))
                    t.HeadOn = blocker.Id;
                return false;
            }
            if (bt.ReverseFor == v.Id && bt.Reversing(now))
            {
                // It is backing out for us: follow it in.
                slowFor = MathF.Min(slowFor, MathF.Abs(blocker.Speed) * 0.9f);
                return true;
            }
            if (t.QueueBehind == blocker.Id && now >= t.QueueUntil) t.QueueBehind = EntityId.None;
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

        /// <summary>
        /// The friend ahead is coming the other way and means to come past: facing us, and its
        /// next waypoint is on our side of it (not a hull that is only turning round, or backing).
        /// </summary>
        private static bool Oncoming(Vehicle v, Vehicle blocker, Vector2 forward)
        {
            if (!blocker.HasPath || Vector2.Dot(SimMath.Forward(blocker.Heading), forward) >= -0.5f) return false;
            var towards = blocker.Path[blocker.PathIndex] - blocker.Position;
            return towards.LengthSquared() > 1f && Vector2.Dot(Vector2.Normalize(towards), forward) < -0.5f &&
                   Vector2.Dot(towards, v.Position - blocker.Position) > 0f;
        }

        private void NoteBlocker(Vehicle v, Vehicle blocker)
        {
            v.Traffic.LastBlocker = blocker.Id;
            v.Traffic.LastBlockerTime = _world.Time;
        }

        /// <summary>The hull that last stood in the way, if that was within the last <paramref name="maxAge"/> seconds.</summary>
        private Vehicle? RecentBlocker(Vehicle v, double maxAge = 1.0)
        {
            var t = v.Traffic;
            if (_world.Time - t.LastBlockerTime > maxAge || !_world.TryGetVehicle(t.LastBlocker, out var b) || !b.IsAlive) return null;
            return b;
        }

        // ------------------------------------------------------------------ taking turns through a doorway

        /// <summary>A doorway stays one-way this many steps after the last vehicle going that way was in it or about to enter.</summary>
        private static int GateHoldTicks => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.GateHoldTicks;

        /// <summary>One way holds a doorway at most this long while vehicles wait on the other side.</summary>
        private static double GateTurnSeconds => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.GateTurnSeconds;

        /// <summary>After waiting this long at a doorway a vehicle counts as stuck after all.</summary>
        private static double GateWaitMax => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.GateWaitMax;

        /// <summary>How far past its own nose a vehicle looks for the doorway it is about to enter.</summary>
        private const float GateLookAhead = 2f;

        private int _gateBuild = -1;

        /// <summary>Per doorway: the way it is held (+1 or -1 along its way through, 0 free), the step that way was last used, and since when it has held.</summary>
        private int[] _gateDir = Array.Empty<int>();
        private long[] _gateSeen = Array.Empty<long>();
        private double[] _gateSince = Array.Empty<double>();

        /// <summary>Per doorway, bit 1 for +1 and bit 2 for -1: the ways vehicles claimed it this step, and the ways they waited at it this step and the last.</summary>
        private int[] _gateClaims = Array.Empty<int>();
        private int[] _gateWaiting = Array.Empty<int>();
        private int[] _gateWaitingPrev = Array.Empty<int>();

        /// <summary>
        /// Starts a step's doorway bookkeeping: fresh tables when the lane map was rebuilt (its
        /// doorways are numbered anew), and no claims yet.
        /// </summary>
        private void PrepareGates()
        {
            var lanes = _world.Lanes;
            if (lanes.Builds != _gateBuild)
            {
                _gateBuild = lanes.Builds;
                var n = lanes.DoorwayCount + 1;
                _gateDir = new int[n];
                _gateSeen = new long[n];
                _gateSince = new double[n];
                _gateClaims = new int[n];
                _gateWaiting = new int[n];
                _gateWaitingPrev = new int[n];
            }
            Array.Clear(_gateClaims, 0, _gateClaims.Length);
            Array.Clear(_gateWaiting, 0, _gateWaiting.Length);
        }

        /// <summary>Which way through doorway <paramref name="id"/> a vehicle heading along <paramref name="dir"/> goes: +1, -1, or 0 (along it).</summary>
        private int GateSide(int id, Vector2 dir)
        {
            var along = Vector2.Dot(dir, _world.Lanes.DoorwayThrough(id));
            return along > 0.3f ? 1 : along < -0.3f ? -1 : 0;
        }

        private static int WayBit(int way) => way > 0 ? 1 : 2;

        /// <summary>
        /// A single-lane bridge rule for short doorways (a fortress gate): one way at a time. Inside
        /// one, a vehicle keeps it open for its own way; about to enter one held the other way (or
        /// held its own way for long while others wait opposite), it stops short and waits. Claims
        /// are only collected here and settled at the end of the step, so the outcome does not
        /// depend on the order vehicles are driven in.
        /// </summary>
        private void GateCheck(Vehicle v, Vector2 moveDir, ref float slowFor)
        {
            var t = v.Traffic;
            var lanes = _world.Lanes;
            var tick = _world.Tick;
            var here = lanes.DoorwayAt(v.Position);
            if (here > 0 && here < _gateDir.Length)
            {
                var side = GateSide(here, moveDir);
                if (side != 0 && _gateDir[here] == side) _gateSeen[here] = tick;
                else if (side != 0) _gateClaims[here] |= WayBit(side);
                t.WaitingForGate = false;
                return;
            }
            var probe = v.Position + SimMath.Forward(v.Heading) * (v.Def.HullHalf + v.Def.HullRadius + GateLookAhead);
            var ahead = lanes.DoorwayAt(probe);
            var way = ahead > 0 && ahead < _gateDir.Length ? GateSide(ahead, moveDir) : 0;
            if (way == 0)
            {
                t.WaitingForGate = false;
                return;
            }
            var heldOther = _gateDir[ahead] == -way && tick - _gateSeen[ahead] <= GateHoldTicks;
            var turnOver = _gateDir[ahead] == way && (_gateWaitingPrev[ahead] & WayBit(-way)) != 0 &&
                           _world.Time - _gateSince[ahead] > GateTurnSeconds;
            _gateClaims[ahead] |= WayBit(way);
            if (heldOther || turnOver)
            {
                slowFor = 0f;
                if (!t.WaitingForGate) t.GateWaitStarted = _world.Time;
                t.WaitingForGate = true;
                _gateWaiting[ahead] |= WayBit(way);
                // Out of the way of the traffic coming out: wait beside the route, not in its mouth.
                if (TryGateWaitSpot(v, moveDir, out var spot)) StartGateWait(v, ahead, way, spot);
                return;
            }
            t.WaitingForGate = false;
            if (_gateDir[ahead] == way) _gateSeen[ahead] = tick;
        }

        /// <summary>
        /// Ends a step's doorway bookkeeping: a doorway nobody used its way for a moment is free and
        /// goes to the way claimed this step; claimed both ways, to the way that did not have it
        /// last (turn and turn about).
        /// </summary>
        private void ResolveGates()
        {
            var tick = _world.Tick;
            for (var id = 1; id < _gateDir.Length; id++)
            {
                if (_gateDir[id] != 0 && tick - _gateSeen[id] <= GateHoldTicks) continue;
                var claims = _gateClaims[id];
                var way = claims == 3 ? (_gateDir[id] > 0 ? -1 : 1) : claims == 1 ? 1 : claims == 2 ? -1 : 0;
                if (way != 0 && way != _gateDir[id]) _gateSince[id] = _world.Time;
                _gateDir[id] = way;
                if (way != 0) _gateSeen[id] = tick;
            }
            Array.Copy(_gateWaiting, _gateWaitingPrev, _gateWaiting.Length);
        }

        /// <summary>Sideways offsets and steps back tried for a place to wait beside a doorway, off the route.</summary>
        private static float[] GateWaitLateral => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.GateWaitLateral;

        private static float[] GateWaitBack => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.GateWaitBack;

        /// <summary>
        /// A place to wait for a doorway: to the side of the way in (the traffic coming out keeps to
        /// the route), a little back, off doorways and the main routes where possible, clear of other
        /// hulls and in plain line.
        /// </summary>
        private bool TryGateWaitSpot(Vehicle v, Vector2 moveDir, out Vector2 spot)
        {
            spot = default;
            var lanes = _world.Lanes;
            var grid = _world.Grid;
            var side = new Vector2(-moveDir.Y, moveDir.X);
            var best = float.MaxValue;
            foreach (var lateral in GateWaitLateral)
            foreach (var back in GateWaitBack)
                for (var s = -1; s <= 1; s += 2)
                {
                    var p = v.Position + side * (s * lateral) - moveDir * back;
                    if (!_world.Map.Contains(p) || !grid.IsWalkable(p) || !grid.LineOfSight(v.Position, p)) continue;
                    var f = lanes.At(p);
                    if ((f & LaneFlags.NoPark) != 0) continue;
                    var turn = MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(p - v.Position) - v.Heading));
                    var score = lateral + back * 0.5f + turn * YieldTurnCost + ((f & LaneFlags.Route) != 0 ? 8f * lanes.RouteCountAt(p) : 0f);
                    if (score >= best || HullAt(v, p) != null) continue;
                    best = score;
                    spot = p;
                }
            return best < float.MaxValue;
        }

        private void StartGateWait(Vehicle v, int id, int way, Vector2 spot)
        {
            var t = v.Traffic;
            t.OrderAtYield = v.Order;
            t.ResumeHadPath = v.HasPath;
            t.GateWaitId = id;
            t.GateWaitWay = way;
            t.GateWaitBuild = _gateBuild;
            Vehicle.PathTrace?.Invoke(v, $"Wait for doorway {id}");
            _single.Clear();
            _single.Add(spot);
            v.SetPath(_single, spot);
        }

        /// <summary>
        /// Waiting beside a doorway: it keeps claiming its way (so the doorway turns to it next), and
        /// goes on once the doorway is no longer held the other way, or after waiting long enough.
        /// False once the wait is over.
        /// </summary>
        private bool UpdateGateWait(Vehicle v)
        {
            var t = v.Traffic;
            var id = t.GateWaitId;
            var stale = t.GateWaitBuild != _gateBuild || id >= _gateDir.Length;
            if (!stale)
            {
                _gateClaims[id] |= WayBit(t.GateWaitWay);
                _gateWaiting[id] |= WayBit(t.GateWaitWay);
            }
            if (!stale && GateWay(id) == -t.GateWaitWay && _world.Time - t.GateWaitStarted < GateWaitMax) return true;
            t.GateWaitId = 0;
            t.WaitingForGate = false;
            Vehicle.PathTrace?.Invoke(v, "Doorway free");
            ResumeOrder(v);
            return false;
        }

        /// <summary>The way doorway <paramref name="id"/> is held (+1 or -1 along its way through), 0 when free (tests).</summary>
        internal int GateWay(int id) => id > 0 && id < _gateDir.Length && _world.Tick - _gateSeen[id] <= GateHoldTicks ? _gateDir[id] : 0;

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
                // AI MASTER P1 (spec 32, 111 heavy + scout): equal movers: the right of way decides (the scout backs out).
                if (pv == po && JamStagesOn)
                {
                    pv = _world.Traffic.RightOfWay(v);
                    po = _world.Traffic.RightOfWay(o);
                    if (pv == po)
                    {
                        pv = _world.Traffic.BaseRightOfWay(v);
                        po = _world.Traffic.BaseRightOfWay(o);
                    }
                }
                var dv = ReverseRoom(v);
                var d2 = ReverseRoom(o);
                Vehicle loser;
                if (pv != po) loser = pv < po ? v : o;
                else if (MathF.Abs(dv - d2) > 0.5f) loser = dv < d2 ? v : o;
                else loser = v.Id.Value > o.Id.Value ? v : o;
                // Boxed in behind: the other one backs out instead.
                if (float.IsPositiveInfinity(loser == v ? dv : d2)) loser = loser == v ? o : v;
                var room = loser == v ? dv : d2;
                var winner = loser == v ? o : v;
                // AI MASTER (spec 32 / 111): the winner is in the doorway (the middle of the choke ranks 90) and the loser
                // is still out on open ground beyond the mouth's no-park cells: the loser keeps its road and waits there; it
                // neither backs out nor steps aside (a heavy outside the gate is not pushed back by a scout already in it).
                if (!InDoorway(loser) && InDoorway(winner))
                {
                    loser.Traffic.HoldUntil = now + HeadOnWait;
                    continue;
                }
                // In the open (prompt 12): the loser steps aside, off the winner's way, rather than
                // backing up in front of it; with no room to the side it backs off as in a doorway.
                if (!InDoorway(loser) && !InDoorway(winner))
                {
                    var dir = MoverDirection(winner, loser);
                    if (TryYieldSpot(loser, winner, dir, MaxYieldDepth, out var aside))
                    {
                        StartYield(loser, winner, dir, aside);
                        continue;
                    }
                    if (float.IsPositiveInfinity(room)) room = CanReverse(loser, BackOffDistance) ? BackOffDistance : room;
                }
                if (float.IsPositiveInfinity(room)) continue;
                StartReverse(loser, winner, room);
            }
        }

        /// <summary>Two hulls nose to nose in the open both standing this long: one steps aside (keeping right failed).</summary>
        private static double HeadOnOpenWait => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.HeadOnOpenWait;

        private bool InDoorway(Vehicle v) => (_world.Lanes.At(v.Position) & (LaneFlags.Narrow | LaneFlags.NoPark)) != 0;

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
            // AI MASTER P0-C (spec 52, 63): a boss backs up only if its frame is made to (tracks, wheels), at most once in a
            // while, never continuously; a ship, an aircraft or a train never.
            if (v.Brain != null && !Bosses.BossMovementController.MayReverse(_world, v)) return;
            var t = v.Traffic;
            t.ReverseFor = forWhom?.Id ?? EntityId.None;
            t.ReverseLeft = distance;
            t.ReverseUntil = _world.Time + distance / MathF.Max(0.5f, v.Def.Speed * ReverseShare(v)) + 1.5;
            if (forWhom != null) t.Yields++;
            Vehicle.PathTrace?.Invoke(v, $"Reverse {distance:0.0} for #{t.ReverseFor.Value}");
        }

        /// <summary>How fast a vehicle backs up, as a share of its speed (a Reverse Gearbox makes it faster).</summary>
        private static float ReverseShare(Vehicle v) => ReverseSpeedShare * (1f + (v.Gear?.Stat(StatId.ReverseSpeed) ?? 0f)) * v.SpeedFactor;

        /// <summary>
        /// Backs away from an enemy that has closed in, nose towards it (the Reverse Gearbox): at most
        /// <paramref name="distance"/> metres, and only when the way behind is free. False when it cannot.
        /// </summary>
        internal bool BackAway(Vehicle v, Vector2 threat, float distance)
        {
            if (v.Flying || v.Def.Static || v.Stunned || v.Traffic.Reversing(_world.Time)) return false;
            var face = SimMath.HeadingOf(threat - v.Position);
            // The way out is straight back from the nose pointed at it; turned too far off, the hull swings as it goes.
            var back = -SimMath.Forward(face);
            for (var d = 1f; d <= distance; d += 1f)
            {
                var p = v.Position + back * d;
                if (!_world.Map.Contains(p) || !_world.Grid.IsWalkable(p) || HullAt(v, p) != null) return false;
            }
            StartReverse(v, null, distance);
            v.Traffic.ReverseFacing = true;
            v.Traffic.ReverseFace = threat;
            return true;
        }

        /// <summary>Backs straight out along the hull's axis (tracks need not turn round), then waits beside the mouth.</summary>
        private void DriveReverse(Vehicle v, float dt)
        {
            var t = v.Traffic;
            var def = v.Def;
            // Backing away from an enemy: the hull swings to keep its nose (and its thick front plate) on it.
            if (t.ReverseFacing)
                v.Heading = SimMath.RotateTowards(v.Heading, SimMath.HeadingOf(t.ReverseFace - v.Position), def.TurnRate * v.TurnFactor * dt);
            var back = -SimMath.Forward(v.Heading);
            v.Speed = SimMath.MoveTowards(v.Speed, -def.Speed * ReverseShare(v), def.Speed * 2f * dt);
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
            t.ReverseFacing = false;
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
            var blocker = RecentBlocker(v);
            if (blocker != null && blocker.Team == v.Team && !blocker.HasPath && !_world.Lanes.NoParkAt(v.Position) &&
                Vector2.DistanceSquared(blocker.Position, v.PathGoal) < GatherReach * GatherReach &&
                Vector2.Distance(v.Position, v.PathGoal) < GatherReach + v.Def.HullBound * 2f)
            {
                // Held up by a friend already standing where it is going: the group has gathered,
                // and this one has arrived too (it is not asked to leave, see PostYield).
                v.ClearPath();
                v.StuckStrikes = 0;
                if (v.Order.Kind == OrderKind.Idle) v.GuardPoint = v.Position;
                return;
            }
            if (blocker != null && blocker.Team == v.Team && blocker.Traffic.YieldingTo != v.Id && t.YieldEscalations < 2 && Askable(blocker))
            {
                t.YieldEscalations++;
                t.TrafficBoost += 10;
                PostYield(v, blocker, 0);
                return;
            }
            v.StuckStrikes++;
            if (JamStagesOn)
            {
                // AI MASTER P0-D (spec 38, 108): under the jam stages the ladder keeps planning routes round the hulls;
                // the back-off waits for stage 5 (a vehicle that may reverse) and the give-up comes after it (or after
                // 10 windows without progress whatever the stage), so neither is the first reaction any more.
                var jam = t.Jam;
                var emergencyHeld = jam.Stage == JamStage.Emergency && _world.Time - jam.StageSince >= SimTunables.Ai.Navigation.GiveUpAfterEmergencyS;
                if (emergencyHeld || t.NoProgressWindows >= 10)
                {
                    GiveUp(v);
                    return;
                }
                if (v.StuckStrikes > 2) v.StuckStrikes = 2;
                RequestCostedPath(v, blocker ?? RecentBlocker(v, 3.0), aside: v.StuckStrikes >= 2);
                return;
            }
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
                // (The hull that held it up a few seconds ago still counts: pressed against it at an
                // angle, it may not be dead ahead any more.)
                RequestCostedPath(v, blocker ?? RecentBlocker(v, 3.0), aside: v.StuckStrikes >= 2);
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
        private void RequestCostedPath(Vehicle v, Vehicle? blocker, bool aside, CostedKind kind = CostedKind.Stuck)
        {
            var t = v.Traffic;
            if (kind == CostedKind.Stuck && _world.Time - t.LastCostRepath < MinCostRepathGap) return;
            for (var i = _queueHead; i < _pathQueue.Count; i++)
                if (_pathQueue[i].Vehicle == v.Id) return;
            t.LastCostRepath = _world.Time;
            _pathQueue.Add(new PathRequest(v.Id, v.PathGoal, blocker?.Id ?? EntityId.None, aside, v.StuckStrikes, _world.Time, kind));
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
                    // A hull that cannot move at all (knocked out) is as good as a wall.
                    _costs.BlockerCost = blocker.Stunned || blocker.Def.Static ? ImmovableBlockerCost : BlockerCost;
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
            Vehicle.PathTrace?.Invoke(v, $"Costed route round #{blocker?.Id.Value ?? 0}: {(found ? $"{_costBuffer.Count} points, {PathLength(v.Position, _costBuffer):0} m" : "none")}");
            if (request.Kind == CostedKind.Corridor)
            {
                // AI MASTER P1 (spec 38 stage 4): a way round the jam only under corridorAltMax times the route it has
                // (plus a few metres); otherwise it keeps its route and the yield / queue rules carry on.
                if (found && PathLength(v.Position, _costBuffer) <= RemainingLength(v) * SimTunables.Ai.Navigation.CorridorAltMax + DetourSlack)
                {
                    v.SetPath(_costBuffer, request.Goal);
                    v.StuckStrikes = strikes;
                    t.CostPathUntil = _world.Time + CostPathKeep;
                    t.CostGoal = request.Goal;
                    t.Jam.Reason = "JAM_CORRIDOR_ALTERNATIVE";
                    if (request.Aside) StepAside(v);
                }
                else t.Jam.Reason = "JAM_CORRIDOR_NO_ALTERNATIVE";
                return;
            }
            if (request.Kind == CostedKind.Wreck)
            {
                // AI MASTER P1 (spec 39): round the new wreck at once; with no way round in budget, the route it has.
                if (found)
                {
                    v.SetPath(_costBuffer, request.Goal);
                    v.StuckStrikes = strikes;
                    t.CostPathUntil = _world.Time + CostPathKeep;
                    t.CostGoal = request.Goal;
                }
                return;
            }
            if (!found)
            {
                // No cheaper way found in budget: the plain replan, as before.
                _world.PathTo(v, request.Goal);
                v.StuckStrikes = strikes;
                if (request.Aside) StepAside(v);
                return;
            }
            // A friend that can still move is worth waiting for rather than a long way round; one
            // that cannot (knocked out) is not, and the second time round a longer detour will do.
            // Only a hull that is going to clear (on its way, making way, or one that can be asked) is
            // worth queueing behind.
            var mayMove = blocker != null && !blocker.Stunned && !blocker.Def.Static &&
                          (blocker.HasPath || blocker.Traffic.YieldingTo.IsValid || Askable(blocker));
            var cap = request.Strikes >= 2 ? DetourCapLate : DetourCap;
            // Never queue behind a hull that is queued behind us, or coming the other way: each
            // would wait for the other for ever (two tanks sent to each other's slots; prompt 12).
            if (blocker != null && (blocker.Traffic.QueueBehind == v.Id || Oncoming(v, blocker, SimMath.Forward(v.Heading)))) mayMove = false;
            if (blocker != null && blocker.Team == v.Team && mayMove &&
                (PassesNear(v, _costBuffer, blocker, NoAlternativeLength) ||
                 PathLength(v.Position, _costBuffer) > RemainingLength(v) * cap + DetourSlack))
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
