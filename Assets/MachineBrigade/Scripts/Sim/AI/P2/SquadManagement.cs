#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Spec 19: a squad's internal lifecycle (beside, not instead of, the 7 tactical states).</summary>
    public enum SquadLifecycle : byte
    {
        Forming,
        Rallying,
        Ready,
        Committed,
        Reorganizing,
        Dissolving,
    }

    /// <summary>Spec 27: where a member stands in its squad's formation.</summary>
    public enum Placement : byte
    {
        Front,
        Middle,
        Outer,
        Rear,
    }

    /// <summary>Spec 23: a reinforcement on its way to its squad's rendezvous point.</summary>
    public readonly struct PendingMember
    {
        public PendingMember(EntityId id, Vector2 rendezvous, double since)
        {
            Id = id;
            Rendezvous = rendezvous;
            Since = since;
        }

        public EntityId Id { get; }
        public Vector2 Rendezvous { get; }
        public double Since { get; }
    }

    public sealed partial class Squad
    {
        public SquadLifecycle Lifecycle { get; internal set; } = SquadLifecycle.Forming;
        internal double LifecycleSince;

        /// <summary>Spec 25: C = 0.45 member distance + 0.30 role coverage + 0.25 route progress (0-1).</summary>
        public float Cohesion { get; internal set; } = 1f;

        internal double LowCohesionSince = double.NaN;

        /// <summary>Spec 68: CombatPower = DPS vs the local mix x survivability x availability x range x mobility access (normalised).</summary>
        public float Power { get; internal set; }

        /// <summary>The centre's speed over the last looks (spec 74's intercept).</summary>
        public Vector2 Velocity { get; internal set; }

        internal Vector2 LastCentre = new(float.NaN, float.NaN);
        internal double LastCentreAt;
        internal readonly List<PendingMember> PendingList = new();

        /// <summary>Spec 23: reinforcements on their way to the rendezvous.</summary>
        public IReadOnlyList<PendingMember> Pending => PendingList;

        internal double FormationSince = double.NegativeInfinity, MorphUntil = double.NegativeInfinity, UnderFireAt = double.NegativeInfinity;
        internal bool MorphPending;

        /// <summary>Part G: the reason code of the current formation.</summary>
        public string FormationReason { get; internal set; } = P2Reasons.FormationState;

        internal readonly Dictionary<EntityId, int> SlotOf = new();
        internal FormationMode SlotFormation = FormationMode.Regroup;
        internal readonly Dictionary<EntityId, Vector2> LastSlot = new();
        internal readonly List<EntityId> ColumnOrderList = new();
        internal bool ColumnDirty = true;
        internal readonly Dictionary<EntityId, double> ReleaseAt = new();
        internal readonly Dictionary<EntityId, float> GoalDistance = new();

        /// <summary>Spec 161: the stable longitudinal order of the travel column (front first).</summary>
        public IReadOnlyList<EntityId> ColumnOrder => ColumnOrderList;

        /// <summary>Spec 24: the commander keeps this squad as its reserve.</summary>
        public bool IsReserve => Task.Kind == TaskKind.Reserve;
    }

    /// <summary>
    /// AI MASTER P2, squad management (spec 19-25, 68-76): lifecycle, size 3-9 (desired 5-7), merge, split, reinforcement
    /// rendezvous, cohesion and the regroup point, the power estimate, the join intercept and the flank route check. The
    /// 7 states, 9 actions and their commit windows are untouched (Part A); nothing here reads health as a reason to leave.
    /// </summary>
    public sealed partial class SquadLayer
    {
        private static int DesiredSize => Math.Max(1, (Tun.Squads.DesiredMin + Tun.Squads.DesiredMax) / 2);

        // ------------------------------------------------------------------------------------------------ enlisting (23)

        /// <summary>
        /// Spec 23: a new vehicle reinforces the nearest squad of its kind with room (under the desired maximum) within
        /// ai.squads.reinforceReach: it joins at once inside the receive radius, otherwise drives to a rendezvous behind the
        /// squad's line (never at the leader); with no such squad, the old rule (nearest within 40 m under the desired maximum), else it forms one; only merges fill a squad past 7 (to 9).
        /// </summary>
        private void EnlistOne(SimWorld world, TeamIntel intel, Vehicle v)
        {
            var fast = v.Def.Speed >= 11f;
            Squad? best = null;
            var bestDistance = Tun.Squads.ReinforceReach;
            foreach (var s in _squads)
            {
                if (s.Fast != fast || s.Dodging || s.Lifecycle == SquadLifecycle.Dissolving || s.MemberList.Count == 0) continue;
                if (s.MemberList.Count + s.PendingList.Count >= Tun.Squads.DesiredMax) continue;
                if (!SameDomain(world, s, v)) continue;
                // Distance to the nearest member (a group that starts together joins at once, however it stands).
                var d = Vector2.Distance(s.Centre, v.Position);
                foreach (var id in s.MemberList)
                    if (world.TryGetVehicle(id, out var m)) d = MathF.Min(d, Vector2.Distance(m.Position, v.Position));
                if (d < bestDistance)
                {
                    best = s;
                    bestDistance = d;
                }
            }
            if (best != null)
            {
                _squadOf[v.Id] = best.Id;
                if (bestDistance <= Tun.Squads.ReceiveRadius)
                {
                    Receive(world, best, v.Id, false);
                    return;
                }
                var at = Rendezvous(world, intel, best, v);
                best.PendingList.Add(new PendingMember(v.Id, at, world.Time));
                world.Submit(new Command(CommandType.Move, _commander.Team, new[] { v.Id }, at));
                P2Reasons.Squad(world, _commander.Team, best.Id, DecisionKind.Action, P2Reasons.SquadReinforcementPending,
                    $"{CombatReasons.Name(v.Id)} at ({at.X:0},{at.Y:0})");
                return;
            }
            var near = 40f;
            foreach (var s in _squads)
            {
                if (s.Fast != fast || s.MemberList.Count + s.PendingList.Count >= Tun.Squads.DesiredMax || s.Dodging || s.Lifecycle == SquadLifecycle.Dissolving) continue;
                var d = Vector2.Distance(s.Centre, v.Position);
                if (d < near)
                {
                    best = s;
                    near = d;
                }
            }
            if (best == null)
            {
                best = new Squad(_nextId++, fast) { Centre = v.Position, Goal = v.Position, LifecycleSince = world.Time };
                _squads.Add(best);
            }
            _squadOf[v.Id] = best.Id;
            Receive(world, best, v.Id, false);
        }

        /// <summary>Tests and tools: a squad of exactly these vehicles (no enlisting rules), measured once.</summary>
        internal Squad Form(SimWorld world, IEnumerable<Vehicle> members, bool fast = false)
        {
            var s = new Squad(_nextId++, fast) { LifecycleSince = world.Time };
            _squads.Add(s);
            foreach (var v in members)
            {
                Release(v.Id);
                Insert(s.MemberList, v.Id);
                _squadOf[v.Id] = s.Id;
            }
            Measure(world, s);
            MeasureP2(world, world.Intel.For(_commander.Team), s);
            return s;
        }

        /// <summary>A member joins the squad's list (formation slots are given again; the column is rebuilt).</summary>
        private void Receive(SimWorld world, Squad s, EntityId id, bool log)
        {
            Insert(s.MemberList, id);
            _squadOf[id] = s.Id;
            s.ColumnDirty = true;
            s.IssuedGoal = new Vector2(float.NaN, float.NaN);
            if (s.MemberList.Count > 1) SetLifecycle(world, s, SquadLifecycle.Reorganizing);
            if (log) P2Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, P2Reasons.SquadReinforcementJoined, CombatReasons.Name(id));
        }

        /// <summary>
        /// Spec 23 / 74: the rendezvous behind the squad's line at its predicted position (pos + velocity x clamp(travel, 0,
        /// 6)): reachable from the reinforcement's ground, out of high threat, not in a doorway, not on a main traffic route.
        /// </summary>
        internal Vector2 Rendezvous(SimWorld world, TeamIntel intel, Squad s, Vehicle v)
        {
            var travel = Vector2.Distance(v.Position, s.Centre) / MathF.Max(1f, v.Def.Speed);
            var predicted = s.Centre + s.Velocity * Math.Clamp(travel, 0f, Tun.Squads.JoinPredictSeconds);
            var ahead = s.Task.Objective ?? NearestEnemy(intel, s.Centre) ?? s.Goal;
            var forward = Direction(predicted, ahead);
            if (Vector2.DistanceSquared(predicted, ahead) < 1f) forward = Direction(v.Position, predicted);
            var side = new Vector2(forward.Y, -forward.X);
            var component = GroundComponent(world, v.Position);
            Vector2? best = null;
            var bestScore = float.MinValue;
            var backs = new[] { Tun.Squads.RendezvousBack, Tun.Squads.RendezvousBack + 4f, Tun.Squads.RendezvousBack - 3f };
            var laterals = new[] { 0f, 8f, -8f, 16f, -16f };
            foreach (var b in backs)
                foreach (var l in laterals)
                {
                    var p = world.Map.Clamp(predicted - forward * b + side * l, 6f);
                    if (!world.Grid.IsWalkable(p) || world.Lanes.NoParkAt(p)) continue;
                    if (component > 0 && GroundComponent(world, p) != component) continue;
                    var threat = intel.ThreatAt(ThreatKind.AntiTank, p) + intel.ThreatAt(ThreatKind.Artillery, p) + intel.ThreatAt(ThreatKind.Splash, p);
                    var route = (world.Lanes.At(p) & LaneFlags.Route) != 0 ? 1f : 0f;
                    var score = -threat * 2f - route * 3f - MathF.Abs(l) * 0.05f - MathF.Abs(b - Tun.Squads.RendezvousBack) * 0.1f;
                    if (score > bestScore)
                    {
                        bestScore = score;
                        best = p;
                    }
                }
            return best ?? world.Map.Clamp(predicted - forward * Tun.Squads.RendezvousBack, 6f);
        }

        /// <summary>Spec 23: reinforcements are received inside the receive radius (or at the rendezvous with the squad near).</summary>
        private void ServePending(SimWorld world, TeamIntel intel, Squad s)
        {
            var now = world.Time;
            for (var i = s.PendingList.Count - 1; i >= 0; i--)
            {
                var p = s.PendingList[i];
                if (!world.TryGetVehicle(p.Id, out var v) || !v.IsAlive || v.Team != _commander.Team || v.UnderPlayerControl(now) || v.Flying)
                {
                    s.PendingList.RemoveAt(i);
                    _squadOf.Remove(p.Id);
                    continue;
                }
                var toSquad = Vector2.Distance(v.Position, s.Centre);
                var atPoint = Vector2.Distance(v.Position, p.Rendezvous) <= 6f && Vector2.Distance(s.Centre, p.Rendezvous) <= 20f;
                if (s.MemberList.Count == 0 || toSquad <= Tun.Squads.ReceiveRadius || atPoint || now - p.Since >= Tun.Squads.PendingTimeout)
                {
                    s.PendingList.RemoveAt(i);
                    if (s.MemberList.Count >= MaxSquad)
                    {
                        // No room left: a squad of its own (it will merge if it is too small).
                        var own = new Squad(_nextId++, s.Fast) { Centre = v.Position, Goal = v.Position, LifecycleSince = now };
                        _squads.Add(own);
                        Receive(world, own, p.Id, false);
                    }
                    else Receive(world, s, p.Id, true);
                    continue;
                }
                // The squad moved on: a new rendezvous at its predicted position (never chasing the centroid itself).
                if (Vector2.Distance(s.Centre, p.Rendezvous) > 30f || (!v.IsMoving && v.Order.Kind == OrderKind.Idle))
                {
                    var at = Vector2.Distance(s.Centre, p.Rendezvous) > 30f ? Rendezvous(world, intel, s, v) : p.Rendezvous;
                    s.PendingList[i] = new PendingMember(p.Id, at, p.Since);
                    world.Submit(new Command(CommandType.Move, _commander.Team, new[] { p.Id }, at));
                }
                world.CombatWatch.Explain(p.Id, CombatIdleReason.WaitingFormation, Interval * 2f + 0.5f);
            }
        }

        // ------------------------------------------------------------------------------------------------ managing

        /// <summary>Spec 19-22: reinforcements, splits, merges and the lifecycle, once per squad look (id order).</summary>
        private void Manage(SimWorld world, TeamIntel intel)
        {
            for (var i = 0; i < _squads.Count; i++) ServePending(world, intel, _squads[i]);
            for (var i = 0; i < _squads.Count; i++)
                if (_squads[i].MemberList.Count > MaxSquad) Split(world, _squads[i], "oversize");
            for (var i = 0; i < _squads.Count; i++)
                for (var j = i + 1; j < _squads.Count; j++)
                {
                    var a = _squads[i];
                    var b = _squads[j];
                    if (a.MemberList.Count == 0 || b.MemberList.Count == 0) continue;
                    if (!CanMerge(world, intel, a, b, Tun.Squads.MergeDistance, true)) continue;
                    // The smaller one goes into the larger (ties: into the older).
                    if (b.MemberList.Count > a.MemberList.Count) MergeP2(world, b, a, "understrength");
                    else MergeP2(world, a, b, "understrength");
                }
            foreach (var s in _squads) UpdateLifecycle(world, intel, s);
        }

        /// <summary>
        /// Spec 21: merge when one is under 45 % of the desired strength, tasks are compatible, closer than 35 m and not in
        /// combat; never a squad flanking the opposite side, a reserve, another mobility domain, or past the maximum size.
        /// </summary>
        internal bool CanMerge(SimWorld world, TeamIntel intel, Squad a, Squad b, float within, bool needUnderstrength)
        {
            if (a == b || a.Fast != b.Fast || a.IsReserve || b.IsReserve) return false;
            if ((a.Action == SquadAction.FlankLeft && b.Action == SquadAction.FlankRight) || (a.Action == SquadAction.FlankRight && b.Action == SquadAction.FlankLeft))
                return false;
            if (a.MemberList.Count + b.MemberList.Count > MaxSquad) return false;
            if (needUnderstrength && !Understrength(world, a) && !Understrength(world, b)) return false;
            if (Vector2.Distance(a.Centre, b.Centre) >= within) return false;
            if (InCombat(intel, a) || InCombat(intel, b)) return false;
            if (!CompatibleTasks(a.Task, b.Task)) return false;
            return DomainOf(world, a) == DomainOf(world, b);
        }

        /// <summary>Strength (power left) under ai.squads.mergeShare of the desired squad's (desired size x the members' mean power).</summary>
        internal static bool Understrength(SimWorld world, Squad s)
        {
            if (s.MemberList.Count == 0) return true;
            var full = 0f;
            var left = 0f;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v))
                {
                    full += MathF.Max(0.5f, v.Def.Power);
                    left += TeamIntel.StrengthOf(v);
                }
            var mean = full / s.MemberList.Count;
            return left < Tun.Squads.MergeShare * DesiredSize * mean;
        }

        private static bool InCombat(TeamIntel intel, Squad s) => s.State == SquadState.Combat || NearestEnemyDistance(intel, s.Centre) <= s.Reach;

        private static bool CompatibleTasks(SquadTask a, SquadTask b)
        {
            if (a.Kind != b.Kind) return false;
            if (a.Objective.HasValue != b.Objective.HasValue) return false;
            return !a.Objective.HasValue || Vector2.Distance(a.Objective.Value, b.Objective!.Value) < 30f;
        }

        private static MobilityDomain DomainOf(SimWorld world, Squad s)
        {
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) return MapTopology.DomainOf(v.Def);
            return MobilityDomain.Ground;
        }

        private static bool SameDomain(SimWorld world, Squad s, Vehicle v) => DomainOf(world, s) == MapTopology.DomainOf(v.Def);

        private static int GroundComponent(SimWorld world, Vector2 p) => world.Topology.Ground.ComponentAt(p);

        /// <summary>Spec 21: <paramref name="from"/> goes into <paramref name="into"/> (up to the maximum size), logged.</summary>
        private void MergeP2(SimWorld world, Squad into, Squad from, string why)
        {
            var moved = 0;
            for (var i = 0; i < from.MemberList.Count && into.MemberList.Count < MaxSquad; i++)
            {
                Insert(into.MemberList, from.MemberList[i]);
                _squadOf[from.MemberList[i]] = into.Id;
                moved++;
            }
            from.MemberList.RemoveAll(id => _squadOf.TryGetValue(id, out var sid) && sid == into.Id);
            foreach (var p in from.PendingList)
            {
                into.PendingList.Add(p);
                _squadOf[p.Id] = into.Id;
            }
            from.PendingList.Clear();
            into.ColumnDirty = true;
            into.IssuedGoal = new Vector2(float.NaN, float.NaN);
            SetLifecycle(world, into, SquadLifecycle.Reorganizing);
            SetLifecycle(world, from, SquadLifecycle.Dissolving);
            P2Reasons.Squad(world, _commander.Team, into.Id, DecisionKind.Action, P2Reasons.SquadMerge, $"squad {from.Id} +{moved} ({why})");
        }

        /// <summary>Spec 22: over the maximum size: every other member of the column forms a new squad with the same task.</summary>
        private void Split(SimWorld world, Squad s, string why)
        {
            RebuildColumn(world, s);
            var part = new Squad(_nextId++, s.Fast) { Centre = s.Centre, Goal = s.Goal, Task = s.Task, LifecycleSince = world.Time };
            var order = new List<EntityId>(s.ColumnOrderList);
            for (var i = 1; i < order.Count; i += 2)
            {
                s.MemberList.Remove(order[i]);
                Insert(part.MemberList, order[i]);
                _squadOf[order[i]] = part.Id;
            }
            _squads.Add(part);
            s.ColumnDirty = part.ColumnDirty = true;
            s.IssuedGoal = new Vector2(float.NaN, float.NaN);
            SetLifecycle(world, s, SquadLifecycle.Reorganizing);
            SetLifecycle(world, part, SquadLifecycle.Reorganizing);
            P2Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, P2Reasons.SquadSplit, $"-> squad {part.Id} ({why}, {s.MemberList.Count}+{part.MemberList.Count})");
        }

        private void SetLifecycle(SimWorld world, Squad s, SquadLifecycle next)
        {
            if (s.Lifecycle == next) return;
            P2Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.State, P2Reasons.SquadLifecycle, $"{s.Lifecycle} -> {next}");
            s.Lifecycle = next;
            s.LifecycleSince = world.Time;
        }

        /// <summary>Spec 19: Forming (under 3), Rallying (gathering), Ready, Committed (on the attack), Reorganizing (just merged / split / reinforced, 3 s), Dissolving.</summary>
        private void UpdateLifecycle(SimWorld world, TeamIntel intel, Squad s)
        {
            if (s.MemberList.Count == 0)
            {
                SetLifecycle(world, s, SquadLifecycle.Dissolving);
                return;
            }
            if (s.Lifecycle == SquadLifecycle.Reorganizing && world.Time - s.LifecycleSince < 3.0) return;
            SquadLifecycle next;
            if (s.MemberList.Count < MinSquad) next = s.Action == SquadAction.Join ? SquadLifecycle.Dissolving : SquadLifecycle.Forming;
            else if (s.Cohesion < Tun.Squads.CohesionRecover || s.Action == SquadAction.Regroup) next = SquadLifecycle.Rallying;
            else if (s.Action is SquadAction.Attack or SquadAction.FlankLeft or SquadAction.FlankRight or SquadAction.Support &&
                     (s.State is SquadState.Combat or SquadState.Approach or SquadState.Flank || s.Task.Window)) next = SquadLifecycle.Committed;
            else next = SquadLifecycle.Ready;
            SetLifecycle(world, s, next);
        }

        // ------------------------------------------------------------------------------------------------ measuring (25, 68)

        /// <summary>Velocity, cohesion (25), power (68), taking fire, and component changes of the members (Part F).</summary>
        private void MeasureP2(SimWorld world, TeamIntel intel, Squad s)
        {
            var now = world.Time;
            if (s.MemberList.Count == 0) return;
            if (!float.IsNaN(s.LastCentre.X) && now > s.LastCentreAt)
            {
                var v = (s.Centre - s.LastCentre) / (float)(now - s.LastCentreAt);
                s.Velocity = s.Velocity * 0.5f + v * 0.5f;
            }
            s.LastCentre = s.Centre;
            s.LastCentreAt = now;
            if (s.HoldReleased) s.UnderFireAt = now;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var m) && world.Components.Check(m, out _)) s.ColumnDirty = true;
            s.Cohesion = CohesionOf(world, s, now);
            if (s.Cohesion < Tun.Squads.CohesionRegroup)
            {
                if (double.IsNaN(s.LowCohesionSince)) s.LowCohesionSince = now;
            }
            else s.LowCohesionSince = double.NaN;
            s.Power = PowerOf(world, intel, s);
        }

        /// <summary>Spec 25's cohesion score.</summary>
        internal float CohesionOf(SimWorld world, Squad s, double now)
        {
            var w = Tun.Squads.CohesionWeights;
            float W(int i) => i < w.Length ? w[i] : 0f;
            var n = 0;
            var distance = 0f;
            var progress = 0f;
            var span = MathF.Max(1f, GatherRadius * 2f - GatheredRadius);
            _members.Clear();
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) _members.Add(v);
            foreach (var v in _members)
            {
                n++;
                var d = Vector2.Distance(v.Position, s.Centre);
                distance += Math.Clamp(1f - MathF.Max(0f, d - GatheredRadius) / span, 0f, 1f);
                // Route progress: firing, at its slot, or closing on the squad's goal.
                var toGoal = Vector2.Distance(v.Position, s.Goal);
                var closing = s.GoalDistance.TryGetValue(v.Id, out var before) && toGoal < before - 0.3f;
                s.GoalDistance[v.Id] = toGoal;
                var atSlot = !v.HasPath || Vector2.Distance(v.Position, v.Order.Point) < 15f;
                if (now - v.LastFiredAt < 3.0 || atSlot || closing) progress += 1f;
            }
            if (n == 0) return 1f;
            // Role coverage: rear roles (artillery, AA, EW, repair) within reach of a front / middle member; with none, mutual support.
            var rear = 0;
            var covered = 0;
            foreach (var v in _members)
            {
                var place = PlacementOf(world, v, s.Fast);
                var isRear = place == Placement.Rear;
                var reach = isRear ? Tun.Squads.SupportReach : GatherRadius;
                rear++;
                foreach (var o in _members)
                {
                    if (o == v) continue;
                    if (isRear && PlacementOf(world, o, s.Fast) == Placement.Rear) continue;
                    if (Vector2.DistanceSquared(o.Position, v.Position) <= reach * reach)
                    {
                        covered++;
                        break;
                    }
                }
            }
            var coverage = n == 1 ? 1f : covered / (float)Math.Max(1, rear);
            return W(0) * distance / n + W(1) * coverage + W(2) * progress / n;
        }

        /// <summary>Spec 68: the squad's combat power against the local mix (normalised: a fresh main battle tank is about 1).</summary>
        internal float PowerOf(SimWorld world, TeamIntel intel, Squad s)
        {
            Vehicle? sample = null;
            var near = float.MaxValue;
            foreach (var c in intel.Contacts)
            {
                if (!c.InSight || c.Flying) continue;
                var d = Vector2.DistanceSquared(c.Position, s.Centre);
                if (d < near && world.TryGetVehicle(c.Id, out var e) && e.IsAlive)
                {
                    near = d;
                    sample = e;
                }
            }
            var goalComponent = GroundComponent(world, s.Task.Objective ?? s.Goal);
            var total = 0f;
            foreach (var id in s.MemberList)
            {
                if (!world.TryGetVehicle(id, out var v)) continue;
                var weapon = v.Def.Weapon;
                var dps = weapon.Damage * MathF.Max(1, weapon.Burst) / MathF.Max(0.2f, weapon.Cooldown);
                var effect = sample != null ? MathF.Max(0.05f, world.Damage.Estimate(weapon, v, sample)) : 1f;
                var survive = v.Hp / 100f * (1f + v.Armour.Front * 0.25f);
                var state = world.Components.Of(v);
                var availability = (v.OutOfAmmo ? 0.2f : 1f) * (state.MainGunLost ? 0.4f : 1f) * (v.DeployBusy ? 0.7f : 1f);
                var range = Math.Clamp(weapon.Range / 40f, 0.5f, 1.5f);
                var mobility = goalComponent > 0 && GroundComponent(world, v.Position) != goalComponent && MapTopology.DomainOf(v.Def) == MobilityDomain.Ground ? 0.3f : 1f;
                total += dps * effect * survive * availability * range * mobility;
            }
            return total / 300f;
        }

        // ------------------------------------------------------------------------------------------------ places (75, 76, 74)

        /// <summary>
        /// Spec 75: the regroup point: behind the current combat line, reachable by every member (one ground component), not
        /// under splash, not in a choke or doorway, off the main traffic routes.
        /// </summary>
        internal Vector2 RegroupPoint(SimWorld world, TeamIntel intel, Squad s)
        {
            var enemy = NearestEnemy(intel, s.Centre);
            var away = enemy is { } e ? Direction(e, s.Centre) : -Direction(s.Centre, s.Task.Objective ?? s.Goal);
            var side = new Vector2(away.Y, -away.X);
            var components = new HashSet<int>();
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) components.Add(GroundComponent(world, v.Position));
            var chokes = world.Topology.Chokes;
            Vector2? best = null;
            var bestScore = float.MinValue;
            foreach (var back in new[] { 0f, 8f, 16f })
                foreach (var lat in new[] { 0f, 8f, -8f })
                {
                    var p = world.Map.Clamp(s.Centre + away * back + side * lat, 6f);
                    if (!world.Grid.IsWalkable(p) || world.Lanes.NoParkAt(p)) continue;
                    var c = GroundComponent(world, p);
                    if (components.Count == 1 && !components.Contains(c)) continue;
                    var splash = intel.ThreatAt(ThreatKind.Splash, p) + intel.ThreatAt(ThreatKind.Artillery, p);
                    var route = (world.Lanes.At(p) & LaneFlags.Route) != 0 ? 1f : 0f;
                    var choke = 0f;
                    foreach (var ch in chokes)
                        if (Vector2.Distance(ch.Centre, p) < ch.Width * 0.5f + 4f) choke = 1f;
                    var score = -splash * 3f - route * 2f - choke * 3f - back * 0.05f - MathF.Abs(lat) * 0.02f;
                    if (score > bestScore)
                    {
                        bestScore = score;
                        best = p;
                    }
                }
            return best ?? s.Centre;
        }

        /// <summary>Spec 74: where a joining squad meets the squad it joins (its predicted position, at most 6 s ahead).</summary>
        internal static Vector2 Intercept(Squad from, Squad into, float speed)
        {
            var travel = Vector2.Distance(from.Centre, into.Centre) / MathF.Max(1f, speed);
            return into.Centre + into.Velocity * Math.Clamp(travel, 0f, Tun.Squads.JoinPredictSeconds);
        }

        /// <summary>Spec 76: a flank route the squad does not fit through (its column width over the narrowest choke on the way) is invalid.</summary>
        private bool FlankRouteFits(SimWorld world, Squad s, Vector2 point)
        {
            var topology = world.Topology;
            var from = topology.CellIndex(s.Centre);
            var to = topology.CellIndex(point);
            if (from < 0 || to < 0) return true;
            var narrowest = topology.Bottleneck(from, to);
            return float.IsInfinity(narrowest) || narrowest >= RequiredWidth(world, s, FormationMode.Travel);
        }

        /// <summary>The slowest member's top speed (join intercepts).</summary>
        private float SlowestSpeed(SimWorld world, Squad s)
        {
            var slow = float.MaxValue;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) slow = MathF.Min(slow, v.Def.Speed);
            return slow == float.MaxValue ? 5f : slow;
        }

        /// <summary>Part F2: the share of members with a crippled engine.</summary>
        private float CrippledShare(SimWorld world, Squad s)
        {
            if (s.MemberList.Count == 0) return 0f;
            var n = 0;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v) && world.Components.Of(v).EngineCrippled) n++;
            return n / (float)s.MemberList.Count;
        }
    }
}
