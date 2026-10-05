#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>The 7 squad states of the sheet "Trạng thái đội" (in its order). There is no RETREAT.</summary>
    public enum SquadState
    {
        Travel,
        Approach,
        Combat,
        Overwatch,
        Flank,
        Hold,
        Regroup,
    }

    /// <summary>The squad actions of the sheet "Hành động đội" (C.1).</summary>
    public enum SquadAction
    {
        Attack,
        Hold,
        FlankLeft,
        FlankRight,
        Overwatch,
        Reposition,
        Support,
        Join,
        Regroup,
    }

    /// <summary>The 5 formation modes of the sheet "Đội hình" (C.5).</summary>
    public enum FormationMode
    {
        Travel,
        Spread,
        Hold,
        Flank,
        Regroup,
    }

    /// <summary>What the commander gives a squad (B.2): the squads choose how.</summary>
    public enum TaskKind
    {
        Primary,
        Secondary,
        Reserve,
    }

    public struct SquadTask
    {
        public TaskKind Kind;

        /// <summary>Where the task points (the objective, the point to hold, the artillery to cover); null: the enemy.</summary>
        public Vector2? Objective;

        /// <summary>Hold the objective rather than take it.</summary>
        public bool Hold;

        /// <summary>The commander's attack window is open (B.1 ATTACK_WINDOW).</summary>
        public bool Window;

        /// <summary>A pincer's side (-1 left, 1 right, 0 none).</summary>
        public int FlankSide;
    }

    /// <summary>One squad of the squad layer: a handful of ground vehicles that fight as one (prompt 28 C).</summary>
    public sealed partial class Squad
    {
        internal readonly List<EntityId> MemberList = new();

        internal Squad(int id, bool fast)
        {
            Id = id;
            Fast = fast;
        }

        public int Id { get; }

        /// <summary>A squad of fast vehicles (scouts, light vehicles): the commander's flankers.</summary>
        public bool Fast { get; }
        public IReadOnlyList<EntityId> Members => MemberList;
        public SquadState State { get; internal set; }
        public SquadAction Action { get; internal set; } = SquadAction.Regroup;
        public float Score { get; internal set; }
        public FormationMode Formation { get; internal set; } = FormationMode.Regroup;
        public SquadTask Task;
        public Vector2 Centre { get; internal set; }
        public float Spread { get; internal set; }
        public Vector2 Goal { get; internal set; }

        /// <summary>The target the squad concentrates on (C.6).</summary>
        public EntityId Focus { get; internal set; }

        /// <summary>The tactic this squad plays (H.10: its own, else the side's).</summary>
        public string? TacticOverride { get; set; }

        /// <summary>H.10: the squad's own tactic may switch again after this.</summary>
        public double OwnTacticReadyAt { get; internal set; }

        internal double ActionSince = double.NegativeInfinity, StateSince = double.NegativeInfinity, EmergencyReadyAt;
        internal double IdleSince = double.NaN, LastScored = double.NegativeInfinity;
        internal Vector2 IssuedGoal = new(float.NaN, float.NaN);
        internal SquadAction IssuedAction = SquadAction.Regroup;
        internal bool Dodging, HoldReleased, BlockedLeft, BlockedRight, FlankReached, BoundPhase;
        internal double BoundSwapAt, StaggerUntil;
        internal int JoinTarget;
        internal Vector2 Waypoint;
        internal float Strength, Reach, LastHp;
        internal readonly Dictionary<EntityId, (Vector2 at, double since, int rung)> Progress = new();

        /// <summary>AI MASTER P1 (spec 31, 85-86): the passage it holds or queues for (0: none), which way, since when.</summary>
        internal int PassageId, PassageDir;
        internal bool PassageQueued;
        internal double PassageSince;

        /// <summary>Members waiting at a queue position for their packet: when they go, to which slot, with which order.</summary>
        internal readonly Dictionary<EntityId, (double at, Vector2 slot, CommandType type)> Packets = new();

        public override string ToString() => $"Squad {Id} {State} {Action} {Score:0} ({MemberList.Count})";
    }

    /// <summary>
    /// Prompt 28 C: the squad layer, about 4 times a second. Each squad: World Model and events -> the valid actions ->
    /// scoring (0-100, factors kept for "VÌ SAO") -> the anti-churn rules (switch margin, minimum commitment, emergencies
    /// only) -> the state -> formation and orders to the units. Emergency Reposition (dodge a warning, gather on
    /// friends) is an action, not an eighth state. Nothing here looks at health: no squad and no vehicle retreats on it.
    /// </summary>
    public sealed partial class SquadLayer
    {
        public static float Interval => global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.Interval;
        public static int MinSquad => global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.MinSquad;
        public static int MaxSquad => global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.MaxSquad;
        private static float GatherRadius => global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.GatherRadius;
        private static float GatheredRadius => global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.GatheredRadius;
        private static float JoinReach => global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.JoinReach;
        private static float SupportReach => global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.SupportReach;

        private readonly AiCommander _commander;
        private readonly List<Squad> _squads = new();
        private readonly List<(SquadAction action, float score, List<Factor> factors)> _options = new();
        private readonly List<Vehicle> _members = new();
        private readonly Dictionary<EntityId, int> _squadOf = new();
        private readonly Dictionary<(int, int), double> _warningsSeen = new();
        private int _nextId = 1;
        private float _timer;

        internal SquadLayer(AiCommander commander)
        {
            _commander = commander;
            _timer = commander.Team == 1 ? Interval * 0.5f : 0f;
        }

        public IReadOnlyList<Squad> Squads => _squads;

        public Squad? SquadOf(EntityId vehicle) => _squadOf.TryGetValue(vehicle, out var id) ? Find(id) : null;

        public Squad? Find(int id)
        {
            foreach (var s in _squads)
                if (s.Id == id) return s;
            return null;
        }

        /// <summary>The valid actions of the last scoring of <paramref name="squad"/> (the viewer's list; invalid ones never enter it).</summary>
        public IReadOnlyList<(SquadAction action, float score)> LastOptions(Squad squad) =>
            _lastOptions.TryGetValue(squad.Id, out var list) ? list : Array.Empty<(SquadAction, float)>();

        private readonly Dictionary<int, List<(SquadAction, float)>> _lastOptions = new();

        /// <summary>Puts new vehicles in squads: the nearest squad of their kind with room, else a new one (B.2).</summary>
        internal void Enlist(SimWorld world, IReadOnlyList<Vehicle> pool)
        {
            // AI MASTER P2 (spec 20, 23): sizes 3-9 (desired 5-7) and reinforcements through a rendezvous (SquadManagement).
            var intel = world.Intel.For(_commander.Team);
            foreach (var v in pool)
            {
                if (_squadOf.ContainsKey(v.Id) || v.Flying) continue;
                EnlistOne(world, intel, v);
            }
        }

        /// <summary>Takes a vehicle out of its squad (a helper of TacticalAi needs it, or it became an aircraft's).</summary>
        internal void Release(EntityId id)
        {
            if (!_squadOf.TryGetValue(id, out var sid)) return;
            _squadOf.Remove(id);
            if (Find(sid) is { } squad)
            {
                squad.MemberList.Remove(id);
                squad.PendingList.RemoveAll(p => p.Id.Value == id.Value);
                squad.ColumnDirty = true;
            }
        }

        public void Tick(SimWorld world, float dt)
        {
            _timer -= dt;
            if (_timer > 0f) return;
            _timer = Interval;
            var intel = world.Intel.For(_commander.Team);
            for (var i = _squads.Count - 1; i >= 0; i--)
            {
                var s = _squads[i];
                Measure(world, s);
                MeasureP2(world, intel, s);
            }
            // AI MASTER P2 (spec 19-23): reinforcements, splits, merges, the lifecycle.
            Manage(world, intel);
            for (var i = _squads.Count - 1; i >= 0; i--)
            {
                var s = _squads[i];
                if (s.MemberList.Count == 0 && s.PendingList.Count == 0)
                {
                    world.AiLog.Forget(AiLayer.Squad, _commander.Team, s.Id);
                    _lastOptions.Remove(s.Id);
                    _squads.RemoveAt(i);
                }
            }
            foreach (var s in _squads)
            {
                if (s.MemberList.Count == 0) continue;
                // AI MASTER P1: passage turns and packets first (spec 31, 85-86).
                TrafficTick(world, s);
                Think(world, intel, s);
            }
            // AI MASTER P0-A (Part C2): the reasons the squads hold their members for.
            ExplainHolds(world);
        }

        // ------------------------------------------------------------------------------------------------ measuring

        private void Measure(SimWorld world, Squad s)
        {
            _members.Clear();
            for (var i = s.MemberList.Count - 1; i >= 0; i--)
            {
                var id = s.MemberList[i];
                if (!world.TryGetVehicle(id, out var v) || !v.IsAlive || v.Team != _commander.Team || v.UnderPlayerControl(world.Time))
                {
                    if (v != null)
                    {
                        // Out of the squad: nothing of the squad's stays on it.
                        v.FaceHeading = null;
                        v.AiHoldFire = false;
                        v.AiKiting = false;
                        v.SquadFocus = EntityId.None;
                        v.SquadTargets = null;
                        v.P3Stance = UnitStance.AttackAnything;
                        v.P3HandoffUntil = double.NegativeInfinity;
                    }
                    s.MemberList.RemoveAt(i);
                    s.Progress.Remove(id);
                    s.SlotOf.Remove(id);
                    s.LastSlot.Remove(id);
                    s.ReleaseAt.Remove(id);
                    s.GoalDistance.Remove(id);
                    s.ColumnDirty = true;
                    _squadOf.Remove(id);
                }
            }
            Vector2 centre = Vector2.Zero;
            float strength = 0f, hp = 0f;
            var reaches = new List<float>();
            foreach (var id in s.MemberList)
            {
                world.TryGetVehicle(id, out var v);
                centre += v.Position;
                strength += TeamIntel.StrengthOf(v);
                hp += v.Hp;
                reaches.Add(v.Def.Weapon.Range);
            }
            if (s.MemberList.Count == 0) return;
            s.Centre = centre / s.MemberList.Count;
            var spread = 0f;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) spread = MathF.Max(spread, Vector2.Distance(v.Position, s.Centre));
            s.Spread = spread;
            s.Strength = strength;
            reaches.Sort();
            s.Reach = reaches[reaches.Count / 2];
            // Taking fire since the last look (releases an ambush's held fire).
            if (hp < s.LastHp - 0.5f) s.HoldReleased = true;
            s.LastHp = hp;
        }

        // ------------------------------------------------------------------------------------------------ deciding

        private void Think(SimWorld world, TeamIntel intel, Squad s)
        {
            var now = world.Time;
            var ai = world.Catalog.Ai;
            var tactic = _commander.TacticFor(s);

            // Emergency 1: dodge a warning ring over the squad (no cooldown; only the reaction delay), then resume.
            if (Dodge(world, intel, s, now)) return;

            // Emergency 2: overwhelmed, or a high THREAT on the squad: gather on the nearest friendly squad, then REGROUP.
            if (now >= s.EmergencyReadyAt && s.Action != SquadAction.Regroup && Overwhelmed(intel, s, ai) && GatherOnFriends(world, s, now))
                return;

            var options = Score(world, intel, s, tactic);
            var current = -1;
            for (var i = 0; i < options.Count; i++)
                if (options[i].action == s.Action) current = i;
            var best = 0;
            for (var i = 1; i < options.Count; i++)
                if (options[i].score > options[best].score) best = i;
            if (options.Count == 0) return;

            // Anti-churn (C.3): change only when the current action is no longer valid, or the new one beats it by the
            // switch margin after the state's minimum commitment, or an urgent event says so.
            var commit = MathF.Max(ai.MinCommit, world.Catalog.AiData.States[(int)s.State].Commit);
            var idle = IdleTooLong(world, s, now, ai.IdleReassess);
            var urgent = Urgent(world, s);
            var change = current < 0 || urgent || idle;
            if (!change && best != current && now - s.ActionSince >= commit)
                change = options[best].score >= options[current].score + ai.SwitchMargin;
            var pick = change ? best : current;
            // An idle reassessment may keep the action (G.3: it re-scores, it does not force a move).
            if (idle) s.IdleSince = double.NaN;
            var (action, score, factors) = options[pick];
            if (action != s.Action)
            {
                world.AiLog.CountSwitch(_commander.Team, s.Id, DecisionKind.Action, now);
                world.AiLog.Add(new DecisionEntry(now, _commander.Team, AiLayer.Squad, s.Id, DecisionKind.Action,
                    $"{s.Action} {(current >= 0 ? options[current].score : 0f):0} -> {action} {score:0}{(urgent ? " (urgent)" : idle ? " (idle)" : current < 0 ? " (invalid)" : "")}"));
                s.Action = action;
                s.ActionSince = now;
                s.FlankReached = false;
                s.HoldReleased = false;
            }
            s.Score = score;
            Explain(world, s, options, pick);
            SetState(world, intel, s, now);
            // AI MASTER P2 Part G / 86: the formation by threat, choke and cohesion, with hysteresis.
            ChooseFormation(world, intel, s, s.Task.Objective ?? NearestEnemy(intel, s.Centre) ?? s.Goal);
            Execute(world, intel, s, tactic);
            Focus(world, intel, s, tactic);
            Units(world, intel, s, tactic);
        }

        private List<(SquadAction action, float score, List<Factor> factors)> Score(SimWorld world, TeamIntel intel, Squad s, TacticDef tactic)
        {
            _options.Clear();
            var ai = world.Catalog.Ai;
            var m = tactic.Modules;
            var skill = _commander.Skill;
            var goal = s.Task.Objective ?? NearestEnemy(intel, s.Centre) ?? s.Centre;
            var radius = MathF.Max(40f, s.Reach * 1.2f);
            var (_, enemyHere) = intel.StrengthAround(s.Centre, radius);
            var (ownGoal, enemyGoal) = intel.StrengthAround(goal, radius);
            var own = s.Strength + ownGoal * 0.5f;
            var threshold = _commander.AttackThreshold(s);
            var ratio = own / MathF.Max(0.01f, enemyGoal);
            var confidence = Confidence(intel, goal, radius, world.Time);
            var transitioning = _commander.InTransition;
            var crippled = CrippledShare(world, s);

            // ATTACK: an objective or a known enemy within the squad's reach of action.
            if (s.Task.Objective.HasValue || NearestEnemy(intel, s.Centre).HasValue)
            {
                var f = new List<Factor>();
                if (enemyGoal > 0f) f.Add(new Factor("ratio", Math.Clamp((ratio / threshold - 1f) * 25f, -25f, 25f)));
                else f.Add(new Factor("undefended", 12f));
                if (s.Task.Window) f.Add(new Factor("window", 15f));
                if (HighValueNear(intel, goal, radius)) f.Add(new Factor("highValue", 10f));
                if (s.Task.Kind == TaskKind.Primary && !s.Task.Hold) f.Add(new Factor("primary", 8f));
                if (m.Counterattack > 0f && enemyGoal > 0f && ratio >= m.Counterattack) f.Add(new Factor("counterattack", 15f));
                if (m.Hold || s.Task.Hold) f.Add(new Factor("holdTactic", -12f));
                if (enemyGoal > 0f) f.Add(new Factor("lowConfidence", -(1f - confidence) * 15f));
                var routeThreat = RouteThreat(intel, s.Centre, goal);
                if (routeThreat > 0f) f.Add(new Factor("routeThreat", -MathF.Min(15f, routeThreat / MathF.Max(1f, s.Strength) * 6f)));
                if (s.Cohesion < SimTunables.Ai.Squads.CohesionRegroup && m.Cohesion > 0f) f.Add(new Factor("notGathered", -10f * m.Cohesion));
                if (transitioning) f.Add(new Factor("transition", -30f));
                if (_commander.WaitingForAir) f.Add(new Factor("waitAir", -20f));
                if (_commander.WaitingForArtillery) f.Add(new Factor("artilleryPrep", -15f));
                Add(SquadAction.Attack, 40f, f);
            }

            // HOLD: a point to hold, or cover close by (a squad can always stand where it is).
            {
                var f = new List<Factor>();
                if (s.Task.Hold || m.Hold) f.Add(new Factor("holdTask", 25f));
                if (m.Stance == FireStance.HoldFire) f.Add(new Factor("ambush", 15f));
                if (_commander.WaitingForAir || _commander.WaitingForArtillery || transitioning) f.Add(new Factor("waiting", 10f));
                if (PointPressure(intel, goal)) f.Add(new Factor("losingPoint", -20f));
                if (intel.ThreatAt(ThreatKind.Splash, s.Centre) > 0f || intel.ThreatAt(ThreatKind.Artillery, s.Centre) > 0f)
                    f.Add(new Factor("inSplash", -15f));
                if (!s.Task.Hold && !m.Hold && s.Task.Window) f.Add(new Factor("window", -10f));
                // Part F2: most of the squad crippled: hold / support rather than a long move (capability, not health).
                if (crippled > 0.5f) f.Add(new Factor("crippled", SimTunables.Ai.ComponentState.HoldBonus));
                Add(SquadAction.Hold, 30f, f);
            }

            // FLANK_LEFT / FLANK_RIGHT: only with a route round that is open and not under too much threat (filtered first).
            if (s.MemberList.Count >= 2 && Vector2.Distance(s.Centre, goal) > 30f)
                for (var side = -1; side <= 1; side += 2)
                {
                    if ((side < 0 && s.BlockedLeft) || (side > 0 && s.BlockedRight)) continue;
                    if (!FlankPoint(world, intel, s, goal, side, out var point, out var threat)) continue;
                    // Spec 76: no flank whose way is too narrow for the squad's column.
                    if (!FlankRouteFits(world, s, point)) continue;
                    var f = new List<Factor>();
                    var (_, sideEnemy) = intel.StrengthAround(point, radius);
                    if (enemyGoal > 0f) f.Add(new Factor("weakFlank", Math.Clamp((enemyGoal - sideEnemy) / enemyGoal * 15f, -10f, 15f)));
                    if (s.Fast) f.Add(new Factor("mobile", 12f));
                    var weight = ai.FlankWeight * m.Flank * skill.Flank;
                    if (MathF.Abs(weight - 1f) > 0.01f) f.Add(new Factor("flankTactic", (weight - 1f) * 20f));
                    if (s.Task.FlankSide == side) f.Add(new Factor("pincer", 15f));
                    f.Add(new Factor("cohesionRisk", -8f * ai.Cohesion));
                    if (sideEnemy > 0f) f.Add(new Factor("reserveThatWay", -MathF.Min(10f, sideEnemy / MathF.Max(1f, s.Strength) * 5f)));
                    if (threat > 0f) f.Add(new Factor("routeThreat", -MathF.Min(10f, threat / MathF.Max(1f, s.Strength) * 4f)));
                    if (transitioning) f.Add(new Factor("transition", -30f));
                    // Part F2: no long flank with a crippled engine in the squad.
                    if (crippled > 0f) f.Add(new Factor("crippled", -SimTunables.Ai.ComponentState.FlankPenalty));
                    Add(side < 0 ? SquadAction.FlankLeft : SquadAction.FlankRight, 30f, f);
                }

            // OVERWATCH: a friendly squad close by is advancing.
            if (s.Reach >= 40f && AdvancingFriend(intel, s) is { } friend)
            {
                var f = new List<Factor>();
                if (intel.Know(ThreatKind.AntiTank, friend.Goal) == Knowledge.Unknown) f.Add(new Factor("unknownGround", 15f));
                if (m.Bounding) f.Add(new Factor("bounding", 20f));
                if (s.Task.Kind == TaskKind.Primary && s.Task.Window) f.Add(new Factor("window", -10f));
                Add(SquadAction.Overwatch, 25f, f);
            }

            // REPOSITION: a better spot within a short distance (less splash, artillery or anti-tank fire), or the line behind.
            if (BetterSpot(world, intel, s, out var better, out var gain, out var fallback, m))
            {
                var f = new List<Factor>();
                if (fallback) f.Add(new Factor("fallbackLine", 35f));
                if (gain > 0f) f.Add(new Factor("underFire", MathF.Min(25f, gain)));
                if (s.Focus.IsValid) f.Add(new Factor("focusing", -15f));
                Add(SquadAction.Reposition, 20f, f);
                s.Waypoint = better;
            }

            // SUPPORT: a friendly squad nearby is losing its fight.
            if (LosingFriend(intel, s) is { } losing)
            {
                var f = new List<Factor>();
                var (fo, fe) = intel.StrengthAround(losing.Centre, radius);
                f.Add(new Factor("friendLosing", Math.Clamp((1f - fo / MathF.Max(0.01f, fe)) * 25f, 0f, 25f)));
                if (enemyHere <= 0f) f.Add(new Factor("free", 10f));
                if (s.Task.Kind == TaskKind.Primary) f.Add(new Factor("leavesTask", -15f));
                Add(SquadAction.Support, 30f, f);
            }

            // JOIN: too small, with another squad of its kind close by.
            if (s.MemberList.Count < MinSquad && JoinableSquad(world, intel, s) is { } join)
            {
                s.JoinTarget = join.Id;
                Add(SquadAction.Join, 35f, new List<Factor> { new("belowMinimum", 25f) });
            }

            // REGROUP: scattered (and, once regrouping, until gathered again).
            // AI MASTER P2 spec 25: cohesion under 0.55 for over 2 s (not in an immediate survival fight), until it is back over 0.7.
            var lowCohesion = !double.IsNaN(s.LowCohesionSince) && world.Time - s.LowCohesionSince > SimTunables.Ai.Squads.CohesionSeconds &&
                              !(s.State == SquadState.Combat && world.Time - s.UnderFireAt < 2.0);
            if (lowCohesion || (s.Action == SquadAction.Regroup && s.Cohesion < SimTunables.Ai.Squads.CohesionRecover) || transitioning)
            {
                var f = new List<Factor> { new("scattered", MathF.Min(25f, (1f - s.Cohesion) * 40f)) };
                if (transitioning) f.Add(new Factor("tacticChanged", 20f));
                if (s.Task.Window) f.Add(new Factor("window", -15f));
                Add(SquadAction.Regroup, 25f, f);
            }

            // AI MASTER P3: confidence, route diversity, posture, package and dispersion factors (SquadLayer.P3).
            AdjustP3(world, intel, s, goal);
            AdjustP4(world, intel, s, goal);
            var list = new List<(SquadAction, float)>();
            foreach (var o in _options) list.Add((o.action, o.score));
            _lastOptions[s.Id] = list;
            return _options;

            void Add(SquadAction a, float baseScore, List<Factor> factors)
            {
                var score = baseScore;
                foreach (var f in factors) score += f.Points;
                _options.Add((a, Math.Clamp(score, 0f, 100f), factors));
            }
        }

        private void Explain(SimWorld world, Squad s, List<(SquadAction action, float score, List<Factor> factors)> options, int pick)
        {
            var (plus, minus) = Why.Split(options[pick].factors);
            var runner = -1;
            for (var i = 0; i < options.Count; i++)
                if (i != pick && (runner < 0 || options[i].score > options[runner].score)) runner = i;
            world.AiLog.Record(new Why
            {
                Layer = AiLayer.Squad, Team = _commander.Team, Subject = s.Id, Time = world.Time, Choice = options[pick].action.ToString(),
                Score = options[pick].score, Plus = plus, Minus = minus,
                RunnerUp = runner >= 0 ? options[runner].action.ToString() : null, RunnerUpScore = runner >= 0 ? options[runner].score : 0f,
                // AI MASTER P2 section 97: task, state, formation (and why), lifecycle, cohesion, power, members.
                Context = $"{s.Task.Kind} {s.State} {s.Formation} ({s.FormationReason}) {s.Lifecycle} C{s.Cohesion:0.00} P{s.Power:0.0} n{s.MemberList.Count}+{s.PendingList.Count}",
            });
        }

        /// <summary>Urgent events that let a squad change at once (C.3): its focus died, its objective moved, its route is blocked.</summary>
        private static bool Urgent(SimWorld world, Squad s)
        {
            if (s.Focus.IsValid && !(world.TryGetVehicle(s.Focus, out var f) && f.IsAlive)) return true;
            if (s.Task.Objective is { } o && !float.IsNaN(s.IssuedGoal.X) && s.Action is SquadAction.Attack or SquadAction.Hold &&
                Vector2.Distance(o, s.Goal) > 30f) return true;
            return (s.Action == SquadAction.FlankLeft && s.BlockedLeft) || (s.Action == SquadAction.FlankRight && s.BlockedRight);
        }

        /// <summary>G.3: standing without a reason (not firing, holding, reloading, deploying or in ambush) for too long.</summary>
        private static bool IdleTooLong(SimWorld world, Squad s, double now, float after)
        {
            var reason = s.Action == SquadAction.Hold || s.Action == SquadAction.Overwatch || s.Dodging;
            foreach (var id in s.MemberList)
            {
                if (!world.TryGetVehicle(id, out var v)) continue;
                if (v.IsMoving || now - v.LastFiredAt < 3.0 || v.OutOfAmmo || v.DeployBusy || v.Target.IsValid) reason = true;
            }
            if (reason)
            {
                s.IdleSince = double.NaN;
                return false;
            }
            if (double.IsNaN(s.IdleSince)) s.IdleSince = now;
            return now - s.IdleSince >= after;
        }

        private void SetState(SimWorld world, TeamIntel intel, Squad s, double now)
        {
            var nearest = NearestEnemyDistance(intel, s.Centre);
            SquadState next;
            switch (s.Action)
            {
                case SquadAction.Regroup:
                    next = SquadState.Regroup;
                    break;
                case SquadAction.Hold:
                    next = SquadState.Hold;
                    break;
                case SquadAction.Overwatch:
                    next = SquadState.Overwatch;
                    break;
                case SquadAction.FlankLeft:
                case SquadAction.FlankRight:
                    next = s.FlankReached || nearest <= s.Reach ? SquadState.Combat : SquadState.Flank;
                    break;
                default:
                    next = nearest <= s.Reach ? SquadState.Combat : nearest <= s.Reach * 1.5f ? SquadState.Approach : SquadState.Travel;
                    break;
            }
            if (next == s.State) return;
            // A state is held for its minimum commitment unless the new one ranks at least as high (contact always wins).
            var states = world.Catalog.AiData.States;
            var lower = states[(int)next].Priority < states[(int)s.State].Priority;
            if (lower && now - s.StateSince < states[(int)s.State].Commit) return;
            world.AiLog.CountSwitch(_commander.Team, s.Id, DecisionKind.State, now);
            s.State = next;
            s.StateSince = now;
            // AI MASTER P2: the formation follows in ChooseFormation (Part G triggers, hysteresis, morphing).
        }

        // ------------------------------------------------------------------------------------------------ emergencies

        private bool Dodge(SimWorld world, TeamIntel intel, Squad s, double now)
        {
            var delay = _commander.Skill.ReactionDelay;
            var any = false;
            foreach (var w in intel.Warnings)
            {
                if (w.Team == _commander.Team || w.Due < now) continue;
                var key = ((int)MathF.Round(w.Centre.X * 4f) * 7919 + (int)MathF.Round(w.Centre.Y * 4f), (int)(w.Due * 10.0));
                if (!_warningsSeen.TryGetValue(key, out var seen)) _warningsSeen[key] = seen = now;
                if (now - seen < delay) continue;
                foreach (var id in s.MemberList)
                {
                    if (!world.TryGetVehicle(id, out var v) || Vector2.Distance(v.Position, w.Centre) > w.Radius + v.Radius + 2f) continue;
                    // AI MASTER P4 spec 217: each member reacts after its own deterministic stagger (the squad stays dodging meanwhile).
                    if (StaggerWaitP4(id, key, seen, now, delay))
                    {
                        any = true;
                        continue;
                    }
                    // The shortest way out of the ring.
                    var away = v.Position - w.Centre;
                    away = away.LengthSquared() > 0.01f ? Vector2.Normalize(away) : SimMath.Forward(v.Heading + MathF.PI * 0.5f);
                    var exit = world.Map.Clamp(w.Centre + away * (w.Radius + v.Radius + 6f), 4f);
                    // AI MASTER P4 spec 181: the squad's escape sectors (spread over 3-5 safe sectors) instead of one radial point each.
                    if (EscapeExitP4(world, intel, s, w, key, id) is { } sector) exit = sector;
                    if (!v.HasPath || Vector2.Distance(v.Order.Point, exit) > 4f)
                        world.Submit(new Command(CommandType.Move, _commander.Team, new[] { id }, exit));
                    any = true;
                }
            }
            if (_warningsSeen.Count > 64) Prune(now);
            if (any && !s.Dodging)
                world.AiLog.Add(new DecisionEntry(now, _commander.Team, AiLayer.Squad, s.Id, DecisionKind.Emergency, "dodge warning ring"));
            if (!any && s.Dodging)
            {
                // Out of the ring: back to exactly the action and state it had, without re-scoring.
                s.IssuedGoal = new Vector2(float.NaN, float.NaN);
            }
            s.Dodging = any;
            return any;
        }

        private void Prune(double now)
        {
            var old = new List<(int, int)>();
            foreach (var kv in _warningsSeen)
                if (now - kv.Value > 30.0) old.Add(kv.Key);
            foreach (var k in old) _warningsSeen.Remove(k);
        }

        private static bool Overwhelmed(TeamIntel intel, Squad s, AiParams ai)
        {
            var (own, enemy) = intel.StrengthAround(s.Centre, MathF.Max(40f, s.Reach));
            if (enemy >= MathF.Max(own, s.Strength) * ai.OverwhelmRatio && enemy > 0f) return true;
            foreach (var e in intel.Events)
                if (e.Kind == IntelEventKind.Threat && e.Priority >= 80f && e.Confidence >= 0.5f &&
                    Vector2.Distance(e.Centre, s.Centre) <= e.Radius + s.Spread + 10f) return true;
            return false;
        }

        private bool GatherOnFriends(SimWorld world, Squad s, double now)
        {
            // The nearest friendly squad within the fight (never home, never off the field).
            Squad? friend = null;
            var best = 120f;
            foreach (var o in _squads)
            {
                if (o == s || o.MemberList.Count == 0) continue;
                var d = Vector2.Distance(o.Centre, s.Centre);
                if (d < best && d > 8f)
                {
                    friend = o;
                    best = d;
                }
            }
            if (friend == null) return false;
            s.EmergencyReadyAt = now + world.Catalog.Ai.EmergencyCooldown;
            world.AiLog.CountSwitch(_commander.Team, s.Id, DecisionKind.Action, now);
            world.AiLog.Add(new DecisionEntry(now, _commander.Team, AiLayer.Squad, s.Id, DecisionKind.Emergency, $"gather on squad {friend.Id}"));
            s.Action = SquadAction.Regroup;
            s.ActionSince = now;
            s.State = SquadState.Regroup;
            s.StateSince = now;
            s.Formation = FormationMode.Regroup;
            s.Goal = friend.Centre;
            s.IssuedGoal = s.Goal;
            s.IssuedAction = SquadAction.Regroup;
            Slots(world, s, friend.Centre, Direction(s.Centre, friend.Centre), FormationMode.Regroup, CommandType.Move);
            return true;
        }

        // ------------------------------------------------------------------------------------------------ executing

        private void Execute(SimWorld world, TeamIntel intel, Squad s, TacticDef tactic)
        {
            var m = tactic.Modules;
            var target = s.Task.Objective ?? NearestEnemy(intel, s.Centre) ?? s.Centre;
            var forward = Direction(s.Centre, target);
            var enemyDir = NearestEnemy(intel, s.Centre) is { } e ? Direction(s.Centre, e) : forward;
            Vector2 goal;
            var type = CommandType.AttackMove;
            var mode = s.Formation;
            switch (s.Action)
            {
                case SquadAction.Attack:
                case SquadAction.Support:
                {
                    if (s.Action == SquadAction.Support && LosingFriend(intel, s) is { } f) target = f.Centre;
                    goal = target;
                    // Prompt 32 L3: the way into a walled base: through the gate, or through a wall the squad breaks.
                    if (s.Action == SquadAction.Attack && Breach(world, intel, s, target)) return;
                    // AI MASTER P3 spec 135-137: early for the package's execute time: stage at the sub-zone (overwatch).
                    if (s.Action == SquadAction.Attack && StageP3(world, s, ref goal, ref type)) break;
                    if (s.State == SquadState.Combat && NearestEnemy(intel, s.Centre) is { } enemy)
                    {
                        // Engagement distance (D.5): stand at the role's (or the tactic's) share of the reach.
                        var band = Engage(world, s, m);
                        var nearest = Vector2.Distance(s.Centre, enemy);
                        if (band > 0f && (m.Standoff || m.Kite > 0f || nearest < s.Reach * band * 0.8f))
                            goal = enemy - Direction(s.Centre, enemy) * s.Reach * band;
                        if (m.Kite > 0f && nearest < s.Reach * m.Kite) type = CommandType.Move;
                        SetKiting(world, s, type == CommandType.Move);
                    }
                    else if (m.Cohesion > 0f && s.State == SquadState.Travel && Vector2.Distance(s.Centre, target) > 40f)
                    {
                        // Squad cohesion: advance in bounds so the fast wait for the slow (blitz does not wait).
                        var step = (m.Bounding ? 24f : 32f) * m.Pace;
                        // The bound already ordered stands until the squad is near it (no new route every look).
                        goal = !float.IsNaN(s.IssuedGoal.X) && s.IssuedAction == s.Action && Vector2.Distance(s.Centre, s.IssuedGoal) > 12f
                            ? s.IssuedGoal
                            : s.Centre + forward * step;
                        if (m.Bounding && Bound(world, s, goal, forward)) return;
                    }
                    // AI MASTER P3 spec 146-148 / 206: pursuit discipline, interception, cutoff; spec 134: the Fix envelope.
                    if (s.Action == SquadAction.Attack && (s.Task.Objective == null || s.State == SquadState.Combat) &&
                        NearestContact(intel, s.Centre) is { } chased) goal = PursuitP3(world, intel, s, goal, chased);
                    if (s.Action == SquadAction.Attack) goal = FixP3(world, s, target, goal);
                    // AI MASTER P4 spec 132-133: a probe / feint keeps its envelope.
                    goal = EnvelopeP4(world, intel, s, goal);
                    break;
                }
                case SquadAction.Hold:
                    goal = s.Task.Hold && s.Task.Objective is { } hold ? hold
                        : !float.IsNaN(s.IssuedGoal.X) && s.IssuedAction == SquadAction.Hold ? s.IssuedGoal : s.Centre;
                    type = CommandType.Move;
                    Stance(world, intel, s, m);
                    break;
                case SquadAction.FlankLeft:
                case SquadAction.FlankRight:
                    if (!s.FlankReached && FlankPoint(world, intel, s, target, s.Action == SquadAction.FlankLeft ? -1 : 1, out var w, out _))
                    {
                        if (Vector2.Distance(s.Centre, w) < 12f) s.FlankReached = true;
                        else
                        {
                            goal = w;
                            type = CommandType.Move;
                            break;
                        }
                    }
                    else if (!s.FlankReached)
                    {
                        if (s.Action == SquadAction.FlankLeft) s.BlockedLeft = true;
                        else s.BlockedRight = true;
                    }
                    goal = target;
                    break;
                case SquadAction.Overwatch:
                    goal = AdvancingFriend(intel, s) is { } friend ? friend.Centre - Direction(friend.Centre, friend.Goal) * 20f : s.Centre;
                    type = CommandType.Move;
                    break;
                case SquadAction.Reposition:
                    goal = s.Waypoint;
                    type = CommandType.Move;
                    break;
                case SquadAction.Join:
                    var into = Find(s.JoinTarget);
                    if (into == null || into.MemberList.Count >= MaxSquad)
                    {
                        s.ActionSince = double.NegativeInfinity;
                        return;
                    }
                    // Spec 21 / 74: merge inside 35 m; otherwise drive to the intercept point, never the moving centroid.
                    if (Vector2.Distance(into.Centre, s.Centre) < SimTunables.Ai.Squads.MergeDistance)
                    {
                        MergeP2(world, into, s, "join");
                        return;
                    }
                    goal = Intercept(s, into, SlowestSpeed(world, s));
                    type = CommandType.Move;
                    mode = FormationMode.Travel;
                    break;
                default: // Regroup: on the point first ordered, unless the squad has drifted far from it
                    goal = !float.IsNaN(s.IssuedGoal.X) && s.IssuedAction == SquadAction.Regroup && Vector2.Distance(s.IssuedGoal, s.Centre) < GatherRadius * 2f
                        ? s.IssuedGoal
                        : RegroupPoint(world, intel, s);
                    type = CommandType.Move;
                    break;
            }
            // AI MASTER P2 Part I: a no-chase / leash doctrine keeps the squad near its anchor.
            goal = Leash(world, s, goal);
            if (s.MorphPending && world.Time >= s.MorphUntil) s.IssuedGoal = new Vector2(float.NaN, float.NaN);
            goal = world.Map.Clamp(goal, 6f);
            // AI MASTER P1 (spec 40): never a rally or holding point in a spawn's exit box.
            if (type == CommandType.Move) goal = world.Traffic.OutOfExit(goal, _commander.Team);
            // Release an ambush's hold the moment the squad does anything else; kiting only while it backs off.
            if (s.Action != SquadAction.Hold) SetHoldFire(world, s, false);
            if (type != CommandType.Move || s.State != SquadState.Combat) SetKiting(world, s, false);
            // Orders only when the goal or the action changed, or a member has nothing to do (no reshuffling every look).
            var changed = s.Action != s.IssuedAction || float.IsNaN(s.IssuedGoal.X) ||
                          Vector2.Distance(goal, s.IssuedGoal) > (s.State == SquadState.Combat ? 10f : 6f);
            s.Goal = goal;
            if (changed)
            {
                s.IssuedGoal = goal;
                s.IssuedAction = s.Action;
                Slots(world, s, goal, s.State == SquadState.Combat || s.State == SquadState.Hold ? enemyDir : forward, mode, type);
            }
            else Unstick(world, intel, s, goal, mode, type, s.State == SquadState.Combat ? enemyDir : forward);
        }

        /// <summary>Bounding overwatch (C.8): half the squad stands and covers while the other half moves up to its cover range.</summary>
        private bool Bound(SimWorld world, Squad s, Vector2 goal, Vector2 forward)
        {
            if (s.MemberList.Count < 2) return false;
            var now = world.Time;
            if (now < s.BoundSwapAt) return true;
            s.BoundPhase = !s.BoundPhase;
            s.BoundSwapAt = now + 6.0;
            var moving = new List<EntityId>();
            var standing = new List<EntityId>();
            for (var i = 0; i < s.MemberList.Count; i++)
                (i % 2 == (s.BoundPhase ? 0 : 1) ? moving : standing).Add(s.MemberList[i]);
            var cover = MathF.Min(s.Reach * 0.8f, 30f);
            var to = world.Map.Clamp(s.Centre + forward * cover, 6f);
            world.Submit(new Command(CommandType.AttackMove, _commander.Team, moving.ToArray(), to));
            world.Submit(new Command(CommandType.Stop, _commander.Team, standing.ToArray()));
            s.IssuedGoal = goal;
            s.IssuedAction = s.Action;
            s.Goal = goal;
            return true;
        }

        /// <summary>Gives each member its slot of the formation around <paramref name="goal"/>, facing <paramref name="facing"/> (AI MASTER P2: SlotsP2).</summary>
        private void Slots(SimWorld world, Squad s, Vector2 goal, Vector2 facing, FormationMode mode, CommandType type) =>
            SlotsP2(world, s, goal, facing, mode, type);

        /// <summary>The spread-out distance before splash (L: a multiple of the strongest known blast), from 6 m.</summary>
        private float SpreadDistance(SimWorld world, Squad s)
        {
            var intel = world.Intel.For(_commander.Team);
            var m = _commander.TacticFor(s).Modules;
            var blast = intel.EnemySplash * world.Catalog.Ai.SplashSpread * m.Spread * _commander.Skill.Spread;
            var spacing = MathF.Max(6f, blast * 2f);
            // AI MASTER P2 spec 162: against direct anti-tank fire with little splash, no useless spread (cover and flank instead).
            var splashHere = intel.ThreatAt(ThreatKind.Splash, s.Centre) + intel.ThreatAt(ThreatKind.Artillery, s.Centre);
            if (splashHere <= 0f && intel.ThreatAt(ThreatKind.AntiTank, s.Centre) > 0f) spacing = MathF.Min(spacing, MathF.Max(6f, SimTunables.Ai.Formation.DirectAtMaxSpread));
            return spacing;
        }

        /// <summary>
        /// G.3: a member with a move order that makes no headway for the stuck time is helped, one rung at a time: back off
        /// and retry, a new route (a side step), out of the cluster; then the squad re-scores with this route marked bad.
        /// The movement system's own safety net still nudges a vehicle stuck past its limit and logs it for the map.
        /// </summary>
        private void Unstick(SimWorld world, TeamIntel intel, Squad s, Vector2 goal, FormationMode mode, CommandType type, Vector2 facing)
        {
            var now = world.Time;
            var stuckTime = world.Catalog.Ai.StuckTime;
            var blocked = 0;
            foreach (var id in s.MemberList)
            {
                if (!world.TryGetVehicle(id, out var v)) continue;
                if (!s.Progress.TryGetValue(id, out var p)) s.Progress[id] = p = (v.Position, now, 0);
                // AI MASTER P1: queued for a passage, waiting for its packet, or in jam stages 1-4: the traffic layer has it.
                if (TrafficOwns(s, v))
                {
                    s.Progress[id] = (v.Position, now, p.rung);
                    continue;
                }
                var moving = v.HasPath && Vector2.Distance(v.Position, v.Order.Point) > 6f;
                if (!moving || Vector2.Distance(v.Position, p.at) > 2f)
                {
                    s.Progress[id] = (v.Position, now, moving ? p.rung : 0);
                    // A member left with nothing to do while its squad still has a goal: send it again.
                    if (!moving && v.Order.Kind == OrderKind.Idle && !v.Target.IsValid && Vector2.Distance(v.Position, goal) > 15f && now >= s.StaggerUntil &&
                        now >= ReleaseOf(s, id) &&
                        s.Action != SquadAction.Hold && s.Action != SquadAction.Overwatch)
                        world.Submit(new Command(type, _commander.Team, new[] { id }, goal));
                    continue;
                }
                if (now - p.since < stuckTime) continue;
                var away = SimMath.Forward(v.Heading);
                switch (p.rung)
                {
                    case 0: // back off a little and try again
                        world.Submit(new Command(CommandType.Move, _commander.Team, new[] { id }, world.Map.Clamp(v.Position - away * 4f, 4f)));
                        break;
                    case 1: // another route: a side step towards the goal
                        var sideStep = new Vector2(away.Y, -away.X) * ((id.Value & 1) == 0 ? 8f : -8f);
                        world.Submit(new Command(type, _commander.Team, new[] { id }, world.Map.Clamp(goal + sideStep, 4f)));
                        break;
                    case 2: // out of the cluster
                        var out_ = v.Position - s.Centre;
                        out_ = out_.LengthSquared() > 0.01f ? Vector2.Normalize(out_) : new Vector2(away.Y, -away.X);
                        world.Submit(new Command(CommandType.Move, _commander.Team, new[] { id }, world.Map.Clamp(v.Position + out_ * 8f, 4f)));
                        break;
                    default:
                        blocked++;
                        break;
                }
                s.Progress[id] = (v.Position, now, Math.Min(3, p.rung + 1));
            }
            if (blocked == 0) return;
            // Still stuck: the squad re-scores with this route marked invalid.
            if (s.Action == SquadAction.FlankLeft) s.BlockedLeft = true;
            else if (s.Action == SquadAction.FlankRight) s.BlockedRight = true;
            s.ActionSince = double.NegativeInfinity;
            s.IssuedGoal = new Vector2(float.NaN, float.NaN);
            foreach (var id in s.MemberList)
                if (s.Progress.TryGetValue(id, out var p) && p.rung >= 3) s.Progress[id] = (p.at, now, 0);
            world.AiLog.Add(new DecisionEntry(now, _commander.Team, AiLayer.Squad, s.Id, DecisionKind.Action, "route blocked: re-score"));
        }

        /// <summary>H.9: an ambush holds fire until the enemy is inside its share of the reach, or the squad is hit.</summary>
        private void Stance(SimWorld world, TeamIntel intel, Squad s, TacticModules m)
        {
            // AI MASTER P3 spec 205: ambush discipline (range band, high-value target, detection, synchronized volley).
            if (SimTunables.Ai.Coordination.Enabled && _commander.CoordinationP3 != null)
            {
                StanceP3(world, intel, s, m);
                return;
            }
            var stance = _commander.StanceFor(s);
            if (stance != FireStance.HoldFire || s.HoldReleased)
            {
                SetHoldFire(world, s, false);
                return;
            }
            var share = m.HoldFire > 0f ? m.HoldFire : world.Catalog.Ai.HoldFire > 0f ? world.Catalog.Ai.HoldFire : 0.6f;
            if (NearestEnemyDistance(intel, s.Centre) <= s.Reach * share)
            {
                s.HoldReleased = true;
                SetHoldFire(world, s, false);
                world.AiLog.Add(new DecisionEntry(world.Time, _commander.Team, AiLayer.Squad, s.Id, DecisionKind.Action, "ambush: open fire"));
                return;
            }
            SetHoldFire(world, s, true);
        }

        private static void SetKiting(SimWorld world, Squad s, bool kiting)
        {
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) v.AiKiting = kiting;
        }

        private static void SetHoldFire(SimWorld world, Squad s, bool hold)
        {
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v)) v.AiHoldFire = hold;
        }

        /// <summary>C.6: the squad's focus: the most valuable target it can bring down quickly, nearly dead first.</summary>
        private void Focus(SimWorld world, TeamIntel intel, Squad s, TacticDef tactic)
        {
            var weight = world.Catalog.Ai.FocusWeight * tactic.Modules.Focus * _commander.Skill.Focus;
            var old = s.Focus;
            s.Focus = EntityId.None;
            if (weight > 0.01f && s.State == SquadState.Combat)
            {
                var best = 0f;
                foreach (var c in intel.Contacts)
                {
                    if (!c.InSight || c.Flying || Vector2.Distance(c.Position, s.Centre) > s.Reach + 10f) continue;
                    if (!world.TryGetVehicle(c.Id, out var v) || !v.IsAlive) continue;
                    // Worth over time to kill: the squad's strength against its health, its value, nearly dead first.
                    var value = MathF.Max(0.5f, c.Strength) * (1.6f - v.Hp / MathF.Max(1f, v.MaxHp));
                    if (c.Group is { } g)
                        foreach (var t in tactic.Modules.Targets)
                            if (t == g) value *= 2f;
                    var score = value * s.Strength / MathF.Max(1f, v.Hp) / (1f + Vector2.Distance(c.Position, s.Centre) / MathF.Max(10f, s.Reach));
                    if (c.Id == old) score *= 1.3f; // keep the focus unless another is clearly better
                    if (score > best)
                    {
                        best = score;
                        s.Focus = c.Id;
                    }
                }
            }
            // AI MASTER P3 spec 199: mass fire only where it pays; otherwise the focus weight is cut (spread fire).
            var share = FocusShareP3(world, intel, s);
            if (s.Focus.Value != old.Value || MathF.Abs(share - s.P3FocusShare) > 1e-4f)
            {
                s.P3FocusShare = share;
                if (s.Focus.IsValid) world.AiLog.CountSwitch(_commander.Team, s.Id, DecisionKind.Target, world.Time);
                foreach (var id in s.MemberList)
                    if (world.TryGetVehicle(id, out var v))
                    {
                        v.SquadFocus = s.Focus;
                        v.SquadFocusWeight = weight * share;
                    }
            }
        }

        // ------------------------------------------------------------------------------------------------ helpers

        private static void Insert(List<EntityId> list, EntityId id)
        {
            var at = list.Count;
            while (at > 0 && list[at - 1].Value > id.Value) at--;
            list.Insert(at, id);
        }

        private float Engage(SimWorld world, Squad s, TacticModules m)
        {
            if (m.EngageMax > 0f) return (m.EngageMin + m.EngageMax) * 0.5f;
            float sum = 0f;
            var n = 0;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v) && world.Catalog.AiData.RoleOf(v.Def.Id) is { EngageMax: > 0f } role)
                {
                    sum += (role.EngageMin + role.EngageMax) * 0.5f;
                    n++;
                }
            return n > 0 ? sum / n : 0f;
        }

        private static Vector2? NearestEnemy(TeamIntel intel, Vector2 from)
        {
            Vector2? best = null;
            var bestDistance = float.MaxValue;
            foreach (var c in intel.Contacts)
            {
                if (c.Displaced || c.Flying) continue;
                var d = Vector2.DistanceSquared(c.Position, from);
                if (d < bestDistance)
                {
                    bestDistance = d;
                    best = c.Position;
                }
            }
            return best;
        }

        private static float NearestEnemyDistance(TeamIntel intel, Vector2 from) =>
            NearestEnemy(intel, from) is { } e ? Vector2.Distance(e, from) : float.MaxValue;

        private static float Confidence(TeamIntel intel, Vector2 at, float radius, double now)
        {
            float sum = 0f, weight = 0f;
            foreach (var c in intel.Contacts)
            {
                if (Vector2.Distance(c.Position, at) > radius) continue;
                sum += c.Confidence(now, intel.ConfidenceDecay) * c.Strength;
                weight += c.Strength;
            }
            return weight > 0f ? sum / weight : 1f;
        }

        private static bool HighValueNear(TeamIntel intel, Vector2 at, float radius)
        {
            foreach (var c in intel.Contacts)
                if (c.HighValue && !c.Displaced && Vector2.Distance(c.Position, at) <= radius) return true;
            return false;
        }

        private static bool PointPressure(TeamIntel intel, Vector2 at)
        {
            foreach (var e in intel.Events)
                if (e.Kind == IntelEventKind.ObjectivePressure && Vector2.Distance(e.Centre, at) <= e.Radius + 20f) return true;
            return false;
        }

        /// <summary>Anti-tank and artillery reach along the straight way (sampled every cell).</summary>
        private static float RouteThreat(TeamIntel intel, Vector2 from, Vector2 to)
        {
            var d = Vector2.Distance(from, to);
            var steps = Math.Max(1, (int)(d / intel.Cell));
            var threat = 0f;
            for (var i = 1; i < steps; i++)
            {
                var p = Vector2.Lerp(from, to, i / (float)steps);
                threat = MathF.Max(threat, intel.ThreatAt(ThreatKind.AntiTank, p) + intel.ThreatAt(ThreatKind.Artillery, p));
            }
            return threat;
        }

        /// <summary>A flank waypoint beside the goal, on open ground, with the threat on the way under the squad's strength x 1.5.</summary>
        private static bool FlankPoint(SimWorld world, TeamIntel intel, Squad s, Vector2 goal, int side, out Vector2 point, out float threat)
        {
            var forward = Direction(s.Centre, goal);
            var lateral = new Vector2(forward.Y, -forward.X) * side;
            var distance = Vector2.Distance(s.Centre, goal);
            point = world.Map.Clamp(goal - forward * MathF.Min(30f, distance * 0.4f) + lateral * Math.Clamp(distance * 0.5f, 25f, 45f), 8f);
            threat = RouteThreat(intel, s.Centre, point);
            if (!world.Grid.IsWalkable(point) || Vector2.Distance(point, goal) < 15f) return false;
            return threat <= MathF.Max(1f, s.Strength) * 1.5f;
        }

        private Squad? AdvancingFriend(TeamIntel intel, Squad s)
        {
            foreach (var o in _squads)
                if (o != s && o.MemberList.Count > 0 && (o.Action is SquadAction.Attack or SquadAction.FlankLeft or SquadAction.FlankRight) &&
                    (o.State is SquadState.Travel or SquadState.Approach) && Vector2.Distance(o.Centre, s.Centre) <= 60f) return o;
            return null;
        }

        private Squad? LosingFriend(TeamIntel intel, Squad s)
        {
            Squad? worst = null;
            var worstRatio = 1f;
            foreach (var o in _squads)
            {
                if (o == s || o.State != SquadState.Combat || Vector2.Distance(o.Centre, s.Centre) > SupportReach) continue;
                var (own, enemy) = intel.StrengthAround(o.Centre, MathF.Max(40f, o.Reach));
                var ratio = own / MathF.Max(0.01f, enemy);
                if (enemy > 0f && ratio < worstRatio)
                {
                    worst = o;
                    worstRatio = ratio;
                }
            }
            return worst;
        }

        /// <summary>Spec 21 / 74: the nearest compatible squad within the join reach that a small squad may join.</summary>
        private Squad? JoinableSquad(SimWorld world, TeamIntel intel, Squad s)
        {
            Squad? best = null;
            var bestDistance = JoinReach;
            foreach (var o in _squads)
            {
                if (o == s || o.MemberList.Count == 0 || !CanMerge(world, intel, s, o, JoinReach, false)) continue;
                var d = Vector2.Distance(o.Centre, s.Centre);
                if (d < bestDistance)
                {
                    best = o;
                    bestDistance = d;
                }
            }
            return best;
        }

        /// <summary>A spot within 25 m with clearly less splash and artillery reach on it; or, for a tactic with lines, the line behind.</summary>
        private bool BetterSpot(SimWorld world, TeamIntel intel, Squad s, out Vector2 spot, out float gain, out bool fallback, TacticModules m)
        {
            spot = s.Centre;
            gain = 0f;
            fallback = false;
            if (m.Fallback > 0f && s.Action == SquadAction.Hold)
            {
                var (own, enemy) = intel.StrengthAround(s.Centre, MathF.Max(40f, s.Reach));
                if (enemy > 0f && own / enemy < m.Fallback && world.TryGetRally(_commander.Team, out var home))
                {
                    // The whole squad moves to the line behind (C.9); no vehicle falls back on its own.
                    spot = world.Map.Clamp(s.Centre + Direction(s.Centre, home) * 35f, 6f);
                    fallback = true;
                    return true;
                }
            }
            float Danger(Vector2 p) => intel.ThreatAt(ThreatKind.Splash, p) + intel.ThreatAt(ThreatKind.Artillery, p) + 0.5f * intel.ThreatAt(ThreatKind.AntiTank, p);
            var here = Danger(s.Centre);
            if (here <= 0f) return false;
            var best = here;
            for (var k = 0; k < 8; k++)
            {
                var angle = k * MathF.PI / 4f;
                var p = world.Map.Clamp(s.Centre + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * 25f, 6f);
                if (!world.Grid.IsWalkable(p)) continue;
                var d = Danger(p);
                if (d < best * 0.6f)
                {
                    best = d;
                    spot = p;
                }
            }
            if (best >= here) return false;
            gain = (here - best) / MathF.Max(1f, s.Strength) * 10f;
            return true;
        }

        private static Vector2 Direction(Vector2 from, Vector2 to)
        {
            var d = to - from;
            return d.LengthSquared() > 0.01f ? Vector2.Normalize(d) : Vector2.UnitY;
        }
    }
}
