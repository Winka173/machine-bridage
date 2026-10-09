#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// AI MASTER P0-D + P1 (lane B): the staged jam detector's actions (spec 37-38, 102), wreck-aware route invalidation
    /// (39), ORCA-lite steering with the deterministic passing side (34-36, 87), the deadlock wait-for graph (190) and unit
    /// state anomalies (185). The old stuck ladder (ask again, route round parked hulls, back off, give up) and the safety
    /// net are kept and folded under the stages: stage 1 and 2 are the ladder's first rungs, the back-off waits for stage
    /// 5, the give-up comes after it, and any relocation is the last fail-safe, logged SEVERE_UNSTUCK.
    /// </summary>
    internal sealed partial class MovementSystem
    {
        private static bool JamStagesOn => SimTunables.Ai.Navigation.JamStages;

        private readonly List<(WreckSpot spot, bool added)> _wreckChanges = new();

        /// <summary>The per-side path costs of routes planned round hulls (parked hulls, wrecks, jams, boss corridors), refreshed if stale.</summary>
        internal byte[] CostLayer(int team)
        {
            _unitCosts.RefreshIfStale(_world);
            return _unitCosts.For(team);
        }

        // ------------------------------------------------------------------ spec 37-38: the stages

        /// <summary>Looks at a ground vehicle's progress at the tactical rate (4 Hz, staggered by id) and runs a new stage's action.</summary>
        private void TrackJam(Vehicle v, float dt)
        {
            if (!JamStagesOn || v.Flying || v.Def.Static || v.Def.Naval != null || v.OnRail) return;
            var every = Math.Max(1, SimTunables.Ai.Navigation.JamEvalTicks);
            if ((_world.Tick + v.Id.Value) % every != 0) return;
            var t = v.Traffic;
            var jam = t.Jam;
            var now = _world.Time;
            var dtEval = dt * every;
            var held = v.Stunned || t.YieldingTo.IsValid || t.Reversing(now) || now < t.HoldUntil || t.GateWaitId != 0 || DeployHeld(v) ||
                       v.Burrow != Vehicle.BurrowState.Surface || v.Landing;
            var waiting = held || v.PathQueued ||
                          (t.WaitingOnYield && now - t.WaitStarted < YieldWaitSeconds) ||
                          (t.WaitingForGate && now - t.GateWaitStarted < GateWaitMax) ||
                          (t.QueueBehind.IsValid && now < t.QueueUntil);
            var intent = v.HasPath;
            var engaging = (v.Target.IsValid || v.Engaged.IsValid) && now - v.LastFiredAt < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.TrackJamNowMax;
            var remaining = intent ? RemainingLength(v) : 0f;
            var actual = jam.SampleCount < 0 ? MathF.Abs(v.Speed) : Vector2.Distance(v.Position, jam.SamplePos) / dtEval;
            var samePath = jam.SampleCount == v.Path.Count && !float.IsNaN(jam.SampleRemaining) &&
                           Vector2.DistanceSquared(jam.SampleGoal, v.PathGoal) < 1f;
            var progress = samePath ? (jam.SampleRemaining - remaining) / dtEval : actual;
            jam.SamplePos = v.Position;
            jam.SampleRemaining = remaining;
            jam.SampleGoal = v.PathGoal;
            jam.SampleCount = v.Path.Count;
            jam.Tick(intent, engaging, waiting, v.Def.Speed * v.SpeedFactor, actual, progress, dtEval, now);
            if (jam.Waiting && t.QueueBehind.IsValid) jam.Reason = "JAM_CHOKE_QUEUE";
            if (jam.Stage > jam.Handled)
            {
                var stage = jam.Stage;
                jam.Handled = stage;
                RunJamStage(v, stage);
            }
            CheckAnomaly(v, held || waiting);
        }

        private void RunJamStage(Vehicle v, JamStage stage)
        {
            var t = v.Traffic;
            var now = _world.Time;
            var stats = _world.Traffic.Stats;
            stats.JamActions[(int)stage]++;
            var reason = JamTracker.Code(stage);
            switch (stage)
            {
                case JamStage.Soft:
                    // More room and a looser formation for a moment; pressed among hulls, a side-step.
                    t.LoosenUntil = now + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.RunJamStageNowAdd;
                    if (v.HasPath && Crowded(v) && TryLocalWaypoint(v, 2.5f, 3.5f, out var aside))
                    {
                        v.Path.Insert(v.PathIndex, aside);
                        reason = "JAM_SOFT_SIDESTEP";
                    }
                    break;
                case JamStage.LocalReplan:
                    // A local waypoint 3-6 m off the line round the occupied cells; the strategic target stays.
                    if (v.HasPath && TryLocalWaypoint(v, SimTunables.Ai.Navigation.LocalReplanMin, SimTunables.Ai.Navigation.LocalReplanMax, out var local))
                        v.Path.Insert(v.PathIndex, local);
                    else if (v.HasPath) RequestCostedPath(v, RecentBlocker(v, 3.0), aside: false);
                    break;
                case JamStage.Yield:
                    reason = YieldStage(v);
                    break;
                case JamStage.CorridorReplan:
                    // The jam's cells are dear for a while (for this route, its squad's corridor and anyone else's), and
                    // the route is planned again: a way round is taken only under 1.5 x the current one.
                    _world.Traffic.AddCongestion(v.Team, v.Position + SimMath.Forward(v.Heading) * v.Def.HullBound);
                    _unitCosts.Invalidate();
                    if (v.HasPath) RequestCostedPath(v, RecentBlocker(v, 3.0), aside: false, kind: CostedKind.Corridor);
                    break;
                case JamStage.Emergency:
                    reason = EmergencyStage(v);
                    break;
            }
            t.Jam.Reason = reason;
            Vehicle.PathTrace?.Invoke(v, reason);
            if (stage >= JamStage.Yield)
                _world.Traffic.Log(v.Team, (int)v.Id.Value, $"{reason} low={t.Jam.LowProgressSeconds:0.0}s blk#{t.LastBlocker.Value}", AiLayer.Unit);
        }

        /// <summary>
        /// Stage 3: with a friend in the way, the higher right of way keeps the road and the other gives way (a boss never);
        /// one parked where the mover is going is its group gathering: the mover goes round it instead.
        /// </summary>
        private string YieldStage(Vehicle v)
        {
            var b = RecentBlocker(v, 3.0);
            if (b == null || b.Team != v.Team || b.Def.Static || b.Flying)
            {
                if (v.HasPath) RequestCostedPath(v, b, aside: true);
                return "JAM_YIELD_NO_FRIEND";
            }
            if (!b.HasPath && v.HasPath && Vector2.DistanceSquared(b.Position, v.PathGoal) < GatherReach * GatherReach)
            {
                if (TryLocalWaypoint(v, 3f, 6f, out var round)) v.Path.Insert(v.PathIndex, round);
                return "JAM_YIELD_GATHERING";
            }
            var traffic = _world.Traffic;
            var pv = traffic.RightOfWay(v);
            var pb = traffic.RightOfWay(b);
            if (pv == pb)
            {
                pv = traffic.BaseRightOfWay(v);
                pb = traffic.BaseRightOfWay(b);
            }
            // A parked friend is no traffic: it gives way to the mover (it has nowhere to be).
            var loser = !b.HasPath && v.HasPath ? b : pv != pb ? (pv < pb ? v : b) : (v.Id.Value > b.Id.Value ? v : b);
            if (loser.Def.Boss || loser.Scripted) loser = loser == v ? b : v;
            if (loser.Def.Boss || loser.Scripted) return "JAM_YIELD_BOSSES";
            var winner = loser == v ? b : v;
            if (loser == b)
            {
                PostForcedYield(b, v);
            }
            else
            {
                var dir = MoverDirection(b, v);
                if (TryYieldSpot(v, b, dir, MaxYieldDepth, out var spot)) StartYield(v, b, dir, spot);
                else if (v.HasPath && TryLocalWaypoint(v, 3f, 6f, out var local)) v.Path.Insert(v.PathIndex, local);
            }
            return $"JAM_YIELD winner=#{winner.Id.Value} loser=#{loser.Id.Value}";
        }

        /// <summary>
        /// Stage 5: out of formation; a short reverse only for a vehicle that may reverse with room behind; otherwise pivot
        /// and drive to another local target. Ships never come here (the naval controller widens its turn, P0-C).
        /// </summary>
        private string EmergencyStage(Vehicle v)
        {
            var t = v.Traffic;
            t.FormationBreakUntil = _world.Time + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.EmergencyStageTimeAdd;
            var stats = _world.Traffic.Stats;
            var distance = SimTunables.Ai.Navigation.EmergencyReverseM;
            var move = JamPolicy.Emergency(v.Def, v.OnRail, CanReverse(v, distance));
            if (move == EmergencyMove.ShortReverse)
            {
                StartReverse(v, null, distance);
                if (t.Reversing(_world.Time))
                {
                    stats.EmergencyReverses++;
                    return "JAM_EMERGENCY_REVERSE";
                }
            }
            if (v.HasPath && TryLocalWaypoint(v, 4f, 8f, out var spot))
            {
                v.Path.Insert(v.PathIndex, spot);
                stats.EmergencyAlternates++;
                return "JAM_EMERGENCY_ALTERNATE";
            }
            if (v.HasPath) RequestCostedPath(v, RecentBlocker(v, 3.0), aside: true, kind: CostedKind.Corridor);
            return "JAM_EMERGENCY_REPLAN";
        }

        /// <summary>
        /// A free spot <paramref name="min"/>-<paramref name="max"/> m to the side of the line to the next waypoint (a little
        /// ahead first), away from the hull in the way (else on the side the pair hash or the id picks: never random), in plain
        /// line of both the vehicle and that waypoint, off hulls and wrecks.
        /// </summary>
        private bool TryLocalWaypoint(Vehicle v, float min, float max, out Vector2 spot)
        {
            spot = default;
            var grid = _world.Grid;
            var next = v.HasPath ? v.Path[v.PathIndex] : v.Position + SimMath.Forward(v.Heading) * 8f;
            var way = next - v.Position;
            var dir = way.LengthSquared() > global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.TryLocalWaypointLengthSquaredMin ? Vector2.Normalize(way) : SimMath.Forward(v.Heading);
            var right = new Vector2(dir.Y, -dir.X);
            var blocker = RecentBlocker(v, 3.0);
            int side;
            if (blocker != null)
            {
                var lateral = Vector2.Dot(blocker.Position - v.Position, right);
                side = MathF.Abs(lateral) > 0.3f ? (lateral > 0f ? -1 : 1) : _world.Traffic.PassingSide(v, blocker);
            }
            else side = (v.Id.Value & 1) == 0 ? 1 : -1;
            var mid = (min + max) * 0.5f;
            Span<float> laterals = stackalloc float[] { min, mid, max };
            Span<float> alongs = stackalloc float[] { 2f, 4f, 0f };
            for (var pass = 0; pass < 2; pass++)
            {
                var s = pass == 0 ? side : -side;
                foreach (var lateral in laterals)
                foreach (var along in alongs)
                {
                    var p = v.Position + dir * along + right * (s * lateral);
                    if (!_world.Map.Contains(p) || !grid.IsWalkable(p) || !grid.LineOfSight(v.Position, p)) continue;
                    if (Vector2.DistanceSquared(p, next) > global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.TryLocalWaypointDistanceSquaredMin && !grid.LineOfSight(p, next)) continue;
                    if (HullAt(v, p) != null) continue;
                    if (_world.Wrecks.GroundCount > 0 && _world.Wrecks.Blocks(p, v.Def.HullBound, false)) continue;
                    spot = p;
                    return true;
                }
            }
            return false;
        }

        /// <summary>
        /// The coordinator's request that <paramref name="b"/> make way for <paramref name="mover"/> (stage 3, a deadlock):
        /// served next step like any request, but even if b is not askable (waiting, queued, resting after a yield).
        /// </summary>
        private bool PostForcedYield(Vehicle b, Vehicle mover)
        {
            if (b.Def.Boss || b.Scripted || b.Def.Static || b.Stunned || b.Flying || !b.IsAlive) return false;
            var bt = b.Traffic;
            if (bt.YieldingTo.IsValid) return false;
            bt.QueueBehind = EntityId.None;
            bt.WaitingOnYield = false;
            bt.PendingYield = mover.Id;
            bt.PendingPriority = OverridePriority + 20;
            bt.PendingDepth = 0;
            bt.PendingDir = MoverDirection(mover, b);
            bt.PendingForced = true;
            _world.Traffic.Stats.ForcedYields++;
            return true;
        }

        // ------------------------------------------------------------------ spec 39: wrecks

        /// <summary>
        /// A wreck fell or went since the last step: the path costs are refreshed at the next use, and every ground route
        /// that runs through a new wreck within the look-ahead is planned again at once (not 10 s later when it is stuck).
        /// Squad corridors through it are marked to be planned again.
        /// </summary>
        private void OnWreckChanges()
        {
            _wreckChanges.Clear();
            _world.Wrecks.TakeChanges(_wreckChanges);
            if (_wreckChanges.Count == 0) return;
            _unitCosts.Invalidate();
            foreach (var (spot, added) in _wreckChanges)
            {
                if (spot.Naval) continue;
                _world.Traffic.Corridors.MarkDirtyNear(-1, spot.Position, spot.Bound + 4f);
                if (!added) continue;
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Flying || v.Def.Static || v.Def.Naval != null || !v.HasPath || v.PathQueued || v.OnRail) continue;
                    if (v.Id == spot.Id) continue;
                    var t = v.Traffic;
                    if (t.YieldingTo.IsValid || t.GateWaitId != 0 || t.Reversing(_world.Time)) continue;
                    if (!RouteThrough(v, spot.A, spot.B, spot.Radius + v.Def.HullRadius, SimTunables.Ai.Navigation.WreckLookAhead)) continue;
                    _world.Traffic.Stats.WreckReplans++;
                    Vehicle.PathTrace?.Invoke(v, "ROUTE_WRECK_REPLAN");
                    RequestCostedPath(v, null, aside: false, kind: CostedKind.Wreck);
                    if (v.Traffic.SquadPriority > 0 || v.Traffic.CorridorId > 0)
                        _world.Traffic.Log(v.Team, (int)v.Id.Value, $"ROUTE_WRECK_REPLAN wreck#{spot.Id.Value}", AiLayer.Unit);
                }
            }
        }

        /// <summary>Whether the next <paramref name="lookAhead"/> m of a route pass within <paramref name="clear"/> of a capsule.</summary>
        private static bool RouteThrough(Vehicle v, Vector2 a, Vector2 b, float clear, float lookAhead)
        {
            var from = v.Position;
            var left = lookAhead;
            for (var i = v.PathIndex; i < v.Path.Count && left > 0f; i++)
            {
                var to = v.Path[i];
                var length = Vector2.Distance(from, to);
                if (length > left && length > 1e-3f) to = from + (to - from) * (left / length);
                ClosestPoints(from, to, a, b, out var c1, out var c2);
                if (Vector2.DistanceSquared(c1, c2) < clear * clear) return true;
                left -= length;
                from = to;
            }
            return false;
        }

        // ------------------------------------------------------------------ spec 34-36, 87: ORCA-lite

        private readonly Vehicle?[] _neighbours = new Vehicle?[16];
        private readonly float[] _neighbourDist = new float[16];

        /// <summary>
        /// Spec 35: the heading change that keeps a moving ground vehicle off the moving hulls round it over the next 1.5 s:
        /// the nearest 8-12 movers (sorted list, bounded), each pair's passing side fixed (spec 36), responsibility by right of
        /// way, the minimum separation of spec 87. Worked out at 10 Hz (every other step, staggered) and held between. Pairs
        /// following one another the same way, and anything in a doorway, are left to the traffic rules.
        /// </summary>
        private float OrcaTurn(Vehicle v, float desired)
        {
            var t = v.Traffic;
            var def = v.Def;
            var preferred = MathF.Max(MathF.Abs(v.Speed), def.Speed * v.SpeedFactor * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.OrcaTurnSpeedScale);
            var forward = SimMath.Forward(desired);
            t.DesiredVelocity = forward * def.Speed * v.SpeedFactor;
            if (!SimTunables.Ai.Navigation.OrcaLite || v.Flying)
            {
                t.SafeVelocity = t.DesiredVelocity;
                return 0f;
            }
            if ((_world.Tick + v.Id.Value) % 2 != 0) return t.OrcaTurn;
            t.OrcaTurn = 0f;
            t.SafeVelocity = t.DesiredVelocity;
            if (InDoorway(v)) return 0f;
            var horizon = SimTunables.Ai.Navigation.AvoidanceHorizonGroundS;
            var reach = (preferred + def.Speed) * horizon + def.HullBound + _maxBound + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.OrcaTurnPreferredAdd;
            var max = Math.Min(_neighbours.Length, Math.Max(1, SimTunables.Ai.Navigation.OrcaNeighbours));
            var count = 0;
            for (var i = LowerBound(v.Position.X - reach); i < _ground.Count; i++)
            {
                var o = _ground[i];
                if (o.Position.X > v.Position.X + reach) break;
                if (o == v || !o.IsAlive || PassThrough(v, o) || MathF.Abs(o.Speed) < Navigation.UnitCostField.ParkedSpeed) continue;
                var d = Vector2.DistanceSquared(o.Position, v.Position);
                if (d > reach * reach) continue;
                // (Following a friend the same way: the follow rule slows it behind instead.)
                var oForward = SimMath.Forward(o.Heading);
                if (o.Team == v.Team && Vector2.Dot(oForward, forward) > 0.7f && Vector2.Dot(o.Position - v.Position, forward) > 0f) continue;
                // Bounded insertion: the nearest few, ties by id.
                int k;
                if (count < max) k = count++;
                else
                {
                    k = max - 1;
                    if (d > _neighbourDist[k] || (d == _neighbourDist[k] && o.Id.Value > _neighbours[k]!.Id.Value)) continue;
                }
                while (k > 0 && (_neighbourDist[k - 1] > d || (_neighbourDist[k - 1] == d && _neighbours[k - 1]!.Id.Value > o.Id.Value)))
                {
                    _neighbours[k] = _neighbours[k - 1];
                    _neighbourDist[k] = _neighbourDist[k - 1];
                    k--;
                }
                _neighbours[k] = o;
                _neighbourDist[k] = d;
            }
            if (count == 0) return 0f;
            var traffic = _world.Traffic;
            var mine = traffic.RightOfWay(v);
            var splash = traffic.SplashThreat(v.Team);
            var selfVel = forward * preferred;
            var sum = Vector2.Zero;
            for (var i = 0; i < count; i++)
            {
                var o = _neighbours[i]!;
                _neighbours[i] = null;
                var combined = TrafficSteering.MinSeparation(def.HullRadius, o.Def.HullRadius, splash && o.Team == v.Team,
                    t.InColumn && o.Traffic.InColumn);
                // A capsule is longer than its radius: the nose-to-tail half of the longer hull counts too.
                combined += MathF.Min(def.HullHalf, o.Def.HullHalf) * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.OrcaTurnMinScale;
                var otherVel = SimMath.Forward(o.Heading) * o.Speed;
                var theirs = o.Team == v.Team ? traffic.RightOfWay(o) : mine;
                sum += TrafficSteering.Avoid(v.Position, selfVel, def.HullRadius, mine, (int)v.Id.Value,
                    o.Position, otherVel, o.Def.HullRadius, theirs, (int)o.Id.Value, horizon, combined, traffic.PassingSide(v, o));
            }
            var turn = TrafficSteering.TurnFor(sum, forward, AvoidAngle);
            // Only into open ground: never steer a hull into a wall to dodge.
            if (turn != 0f && !OpenTowards(v, desired + turn)) turn = 0f;
            t.OrcaTurn = turn;
            t.SafeVelocity = SimMath.Forward(desired + turn) * preferred;
            return turn;
        }

        // ------------------------------------------------------------------ spec 190: deadlock wait-for graph

        private readonly Dictionary<long, int> _waitIndex = new();
        private readonly List<Vehicle> _waitNodes = new();
        private readonly List<int> _waitNext = new();
        private readonly List<int> _waitMark = new();
        private readonly List<Vehicle> _cycle = new();

        /// <summary>
        /// Spec 190: once a second, who waits for whom (queued behind, jammed against): a cycle A -> B -> C -> A is a deadlock;
        /// its lowest right of way (ties: the higher id; never a boss) gives way to the one waiting on it, or takes a local
        /// waypoint. Built and resolved before anyone drives, in the vehicle list's order: deterministic.
        /// </summary>
        private void ResolveDeadlocks()
        {
            if (!JamStagesOn || _world.Tick % Math.Max(1, SimTunables.Ai.Traffic.DeadlockTicks) != global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.ResolveDeadlocksTickIs) return;
            _waitIndex.Clear();
            _waitNodes.Clear();
            _waitNext.Clear();
            _waitMark.Clear();
            var now = _world.Time;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Flying || v.Def.Static || v.Def.Naval != null) continue;
                var target = WaitsFor(v, now);
                if (target == null) continue;
                _waitIndex[v.Id.Value] = _waitNodes.Count;
                _waitNodes.Add(v);
                _waitNext.Add(-1);
                _waitMark.Add(0);
            }
            if (_waitNodes.Count < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.ResolveDeadlocksCountMax) return;
            for (var i = 0; i < _waitNodes.Count; i++)
            {
                var target = WaitsFor(_waitNodes[i], now);
                if (target != null && _waitIndex.TryGetValue(target.Id.Value, out var j)) _waitNext[i] = j;
            }
            // A functional graph (one edge out per node): walk from each unvisited node, marking the walk with its start.
            for (var start = 0; start < _waitNodes.Count; start++)
            {
                if (_waitMark[start] != 0) continue;
                var i = start;
                while (i >= 0 && _waitMark[i] == 0)
                {
                    _waitMark[i] = start + 1;
                    i = _waitNext[i];
                }
                if (i < 0 || _waitMark[i] != start + 1) continue;
                // i is on a cycle found on this walk.
                _cycle.Clear();
                var c = i;
                do
                {
                    _cycle.Add(_waitNodes[c]);
                    c = _waitNext[c];
                } while (c != i && _cycle.Count <= _waitNodes.Count);
                if (_cycle.Count >= global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.ResolveDeadlocksCountMin) BreakCycle();
            }
        }

        private Vehicle? WaitsFor(Vehicle v, double now)
        {
            var t = v.Traffic;
            if (t.QueueBehind.IsValid && now < t.QueueUntil && _world.TryGetVehicle(t.QueueBehind, out var q) && q.IsAlive) return q;
            if (t.Jam.Stage >= JamStage.Soft && v.HasPath && RecentBlocker(v, global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.WaitsForMaxAge) is { } b && b.Team == v.Team && !b.Def.Static) return b;
            return null;
        }

        private void BreakCycle()
        {
            var traffic = _world.Traffic;
            var loserIndex = -1;
            var loserPriority = int.MaxValue;
            for (var k = 0; k < _cycle.Count; k++)
            {
                var v = _cycle[k];
                if (v.Def.Boss || v.Scripted) continue;
                var p = traffic.RightOfWay(v);
                if (p > loserPriority || (p == loserPriority && v.Id.Value < _cycle[loserIndex].Id.Value)) continue;
                loserIndex = k;
                loserPriority = p;
            }
            traffic.Stats.Deadlocks++;
            var names = string.Join(">", _cycle.ConvertAll(x => "#" + x.Id.Value));
            if (loserIndex < 0)
            {
                // Only bosses: none reverses; each takes another local waypoint.
                foreach (var v in _cycle)
                    if (v.HasPath && TryLocalWaypoint(v, 4f, 8f, out var spot)) v.Path.Insert(v.PathIndex, spot);
                traffic.Log(_cycle[0].Team, (int)_cycle[0].Id.Value, $"TRAFFIC_DEADLOCK_CYCLE {names} bosses: local replan", AiLayer.Unit);
                return;
            }
            var loser = _cycle[loserIndex];
            // The one waiting on the loser is the one it makes way for.
            var waiter = _cycle[(loserIndex + _cycle.Count - 1) % _cycle.Count];
            loser.Traffic.QueueBehind = EntityId.None;
            var dir = MoverDirection(waiter, loser);
            string how;
            if (!loser.Traffic.YieldingTo.IsValid && TryYieldSpot(loser, waiter, dir, MaxYieldDepth, out var aside))
            {
                StartYield(loser, waiter, dir, aside);
                how = "yield";
            }
            else if (loser.HasPath && TryLocalWaypoint(loser, 3f, 6f, out var local))
            {
                loser.Path.Insert(loser.PathIndex, local);
                how = "local replan";
            }
            else how = "none";
            traffic.Log(loser.Team, (int)loser.Id.Value, $"TRAFFIC_DEADLOCK_CYCLE {names} loser=#{loser.Id.Value} {how}", AiLayer.Unit);
        }

        // ------------------------------------------------------------------ spec 185: unit state anomalies

        /// <summary>
        /// Spec 185: a move order must get the hull going within ai.navigation.anomalyAccelS: one that stands still with a
        /// route (and nothing holding it on purpose) is logged once per order (ANOMALY_NO_ACCEL), and one with no route found
        /// (ANOMALY_NO_PATH). Recovery is the jam stages' (no command is sent again: spec 186).
        /// </summary>
        private void CheckAnomaly(Vehicle v, bool held)
        {
            var t = v.Traffic;
            if (t.AnomalyLogged || held) return;
            if (v.Order.Kind is not (OrderKind.Move or OrderKind.AttackMove or OrderKind.Retreat)) return;
            var since = _world.Time - t.OrderAt;
            if (since < SimTunables.Ai.Navigation.AnomalyAccelS + 0.25 || since > 3.0) return;
            string? code = null;
            if (v.HasPath && MathF.Abs(v.Speed) < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.CheckAnomalyAbsMax && !v.Engaged.IsValid && !(v.Def.HoldsToFire && _world.Time - v.LastFiredAt < HoldToFireSeconds))
                code = "ANOMALY_NO_ACCEL";
            else if (!v.HasPath && !v.PathQueued && !v.PathCompleted && _world.Time - t.PathFailedAt < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.MovementSystem.CheckAnomalyTimeMax)
                code = "ANOMALY_NO_PATH";
            if (code == null) return;
            t.AnomalyLogged = true;
            _world.Traffic.Stats.Anomalies++;
            _world.Traffic.Log(v.Team, (int)v.Id.Value, $"{code} order={v.Order.Kind} after={since:0.0}s", AiLayer.Unit);
        }
    }
}
