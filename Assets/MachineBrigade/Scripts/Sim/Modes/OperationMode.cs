#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// A checkpoint of a multi-stage mission: the stage it follows, the step and the battle's
    /// fingerprint then. It is taken at the start of the step after the stage ended, before any
    /// command of that step, so a replay of the battle's commands up to <see cref="Tick"/> lands on
    /// the same state.
    /// </summary>
    public readonly struct Checkpoint
    {
        public Checkpoint(int stage, long tick, ulong hash)
        {
            Stage = stage;
            Tick = tick;
            Hash = hash;
        }

        /// <summary>The stage finished just before the checkpoint (its index in the mission's list).</summary>
        public int Stage { get; }

        public long Tick { get; }
        public ulong Hash { get; }
    }

    /// <summary>
    /// A multi-stage mission (prompt 5): its stages played one after another in one battle, each a
    /// <see cref="MissionMode"/> of its own on the same world. A finished stage pays its CP, fires
    /// its end events, keeps a checkpoint and leads on (the next stage, or a choice the player makes,
    /// the first option if nobody does). A timed event fires on the stage's clock. An allied
    /// commander's units fight on the player's side under their own AI and may change sides.
    /// Losing a stage loses the mission; finishing the last wins it.
    /// </summary>
    public sealed class OperationMode : IGameMode, IObjectiveMode, IMissionEventHost
    {
        public const int PlayerTeam = MissionMode.PlayerTeam;
        public const int EnemyTeam = MissionMode.EnemyTeam;

        /// <summary>Seconds the player has to choose a branch before the first option is taken.</summary>
        public static double ChoiceSeconds => global::MachineBrigade.Sim.Content.SimTunables.Campaign.OperationMode.ChoiceSeconds;

        private readonly MissionDef _def;
        private readonly SideSetup _player;
        private readonly SideSetup? _enemy;
        private readonly IReadOnlyList<StageDef> _stages;
        private readonly HashSet<StageEventDef> _fired = new();
        private readonly List<Checkpoint> _checkpoints = new();
        private readonly List<int> _path = new();
        private int _kills, _losses, _allyWave;
        private int _dueStage = -1;
        private double _choiceDeadline, _startedAt;

        /// <summary>Fire support that comes again and again (a choice opened allied air strikes): the event and its next time.</summary>
        private readonly List<(StageEventDef e, double next)> _standing = new();

        /// <summary>The ally's HQ (none without one).</summary>
        private EntityId _allyHq;

        public OperationMode(MissionDef def, SideSetup player, SideSetup? enemy)
        {
            _def = def;
            _player = player;
            _enemy = enemy;
            // A mission with an ally but no stages is one stage: itself.
            _stages = def.Stages.Count > 0 ? def.Stages : new[] { new StageDef { Id = "main", Mission = def, Checkpoint = false } };
        }

        public MissionDef Def => _def;

        /// <summary>Prompt 23: the level its events and its stages' events play at (C.3; the session sets it before Setup).</summary>
        public EventLevel EventLevel { get; set; }

        /// <summary>Prompt 23 A: the operation's own events, over every stage (null: none).</summary>
        public MissionEventSystem? Events { get; private set; }

        /// <summary>When the operation began.</summary>
        public double StartedAt => _startedAt;

        /// <summary>How far the operation is: its stages done and the current one's share (0 to 1).</summary>
        public float Progress(SimWorld world) =>
            Math.Clamp((Math.Max(0, _path.Count - 1) + Current.Progress(world)) / Math.Max(1f, _stages.Count), 0f, 1f);

        public EntityId Boss => Current.Boss;
        public Vector2? PlayerGoal(SimWorld world) => Current.PlayerGoal(world);
        public Vector2? EnemyGoal(SimWorld world) => Current.EnemyGoal(world);

        /// <summary>D.8: a new plan moves the operation on to the stage it names (the stage under way is left unpaid).</summary>
        public bool ChangePlan(SimWorld world, MissionEventDef e)
        {
            if (e.Stage == null || Result != null) return false;
            var next = IndexOf(e.Stage);
            if (next < 0) return false;
            PendingChoice = null;
            Begin(world, next, false);
            return true;
        }

        /// <summary>The stage being played (or the last one, once the mission is over).</summary>
        public MissionMode Current { get; private set; } = null!;

        /// <summary>Its index in the mission's list.</summary>
        public int StageIndex { get; private set; }

        public StageDef Stage => _stages[StageIndex];

        public int StageCount => _stages.Count;

        /// <summary>The stages played so far, in order (their indices), the current one last.</summary>
        public IReadOnlyList<int> Path => _path;

        /// <summary>A finished stage waiting on the player's choice (null when none).</summary>
        public StageDef? PendingChoice { get; private set; }

        /// <summary>Seconds left to choose (0 when there is no choice).</summary>
        public float ChoiceLeft(SimWorld world) => PendingChoice == null ? 0f : (float)Math.Max(0.0, _choiceDeadline - world.Time);

        public IReadOnlyList<Checkpoint> Checkpoints => _checkpoints;

        public IReadOnlyList<ObjectiveState> Points => Current.Points;

        public MatchResult? Result { get; private set; }

        /// <summary>The player's kills and losses over every stage so far.</summary>
        public int Kills => _kills + Current.Kills;

        public int Losses => _losses + Current.Losses;

        /// <summary>Prompt 30 L4: the base CP lost over every stage so far.</summary>
        public int LostBaseCp => _lostBaseCp + Current.LostBaseCp;

        private int _lostBaseCp;

        /// <summary>The ally has turned on the player.</summary>
        public bool Betrayed { get; private set; }

        /// <summary>The allied commander's HQ (invalid when the mission has none).</summary>
        public EntityId AllyHq => _allyHq;

        /// <summary>Strikes called by the operation itself so far (allied air support), for the tests and the log.</summary>
        public int FreeStrikes { get; private set; }

        /// <summary>A later stage began (its index): the commanders are set for its goal, in the same step.</summary>
        public event Action<int>? StageChanged;

        public void Setup(SimWorld world)
        {
            _startedAt = world.Time;
            if (_def.PlayArea is { } area) world.Expand(area);
            // Prompt 31 L3: the operation's prebuilt ground states (its stages share the battlefield), before the first stage.
            world.BuildNavSites(_def.NavSites);
            Begin(world, 0, true);
            // Prompt 23: the operation's own events (its stages' own run in each stage).
            // (A mission with an ally and no stages is its own one stage: that stage runs its events.)
            if (_def.Stages.Count > 0 && _def.Events.Count > 0) Events = new MissionEventSystem(world, this, _def.Events, EventLevel);
            // A big operation's enemy may field more vehicles (its own ceiling, else the operations').
            if (_def.Stages.Count > 0 && world.TryGetEconomy(EnemyTeam, out var enemy))
                enemy.VehicleCap = _def.EnemyCap > 0 ? _def.EnemyCap : world.Catalog.VehicleCapFor("Operation");
            // A staged mission's own units are placed once (a mission of one stage places them itself).
            if (_def.Stages.Count > 0)
                foreach (var u in _def.Units) world.SpawnVehicle(u.DefId, u.Team, u.Position, u.Heading);
            if (_def.Ally is { } ally)
            {
                // The ally's camp: its HQ at the site and its towers round it, then its army.
                if (ally.Hq != null && world.Catalog.Vehicles.ContainsKey(ally.Hq))
                {
                    var hq = world.SpawnVehicle(ally.Hq, PlayerTeam, ally.Site, ally.Heading);
                    hq.Ally = true;
                    _allyHq = hq.Id;
                    Current.AllyHq = _allyHq;
                }
                foreach (var s in ally.Structures)
                {
                    var tower = world.SpawnVehicle(s.DefId, PlayerTeam, s.Position, s.Heading);
                    tower.Ally = true;
                }
                foreach (var u in ally.Units)
                {
                    var v = world.SpawnVehicle(u.DefId, PlayerTeam, u.Position, u.Heading);
                    v.Ally = true;
                }
            }
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            if (_dueStage >= 0)
            {
                _checkpoints.Add(new Checkpoint(_dueStage, world.Tick, world.StateHash()));
                _dueStage = -1;
            }
            AllyReinforcements(world);
            StandingStrikes(world);
            Events?.Tick(world, dt);
            if (PendingChoice != null)
            {
                if (world.Time >= _choiceDeadline) Choose(world, PendingChoice.Choices[0].Key);
                return;
            }
            Current.Tick(world, dt);
            var now = world.Time - Current.StartedAt;
            foreach (var e in Stage.Events)
                if (e.At == StageMoment.Time && now >= e.Seconds && _fired.Add(e)) Fire(world, e);
            if (Current.Result is not { } result) return;
            if (result.WinningTeam != PlayerTeam)
            {
                End(world, result.WinningTeam);
                return;
            }
            Complete(world);
        }

        /// <summary>The player picks a branch (by its key) at a stage's end; unknown keys are ignored.</summary>
        public bool Choose(SimWorld world, string key)
        {
            if (PendingChoice == null) return false;
            foreach (var c in PendingChoice.Choices)
            {
                if (c.Key != key) continue;
                var next = IndexOf(c.Next);
                if (next < 0) return false;
                PendingChoice = null;
                Begin(world, next, false);
                return true;
            }
            return false;
        }

        private void Complete(SimWorld world)
        {
            var stage = Stage;
            if (stage.Cp > 0 && world.TryGetEconomy(PlayerTeam, out var economy)) economy.Cp += stage.Cp;
            foreach (var e in stage.Events)
                if (e.At == StageMoment.End && _fired.Add(e)) Fire(world, e);
            if (stage.Choices.Count > 0)
            {
                Keep(world, stage);
                PendingChoice = stage;
                _choiceDeadline = world.Time + ChoiceSeconds;
                return;
            }
            var next = stage.Next != null ? IndexOf(stage.Next) : StageIndex + 1;
            if (next < 0 || next >= _stages.Count)
            {
                End(world, PlayerTeam);
                return;
            }
            Keep(world, stage);
            Begin(world, next, false);
        }

        private void Keep(SimWorld world, StageDef finished)
        {
            if (finished.Checkpoint) _dueStage = StageIndex;
        }

        private void Begin(SimWorld world, int index, bool first)
        {
            Dictionary<string, int>? owners = null;
            if (!first)
            {
                owners = Current.Owners();
                _kills += Current.Kills;
                _losses += Current.Losses;
                _lostBaseCp += Current.LostBaseCp;
            }
            StageIndex = index;
            _path.Add(index);
            var stage = _stages[index];
            Current = new MissionMode(stage.Mission, _player, _enemy) { Staged = true, AllyHq = _allyHq, EventLevel = EventLevel };
            Current.SetupStage(world, first, owners);
            world.Emit(SimEvent.StageBegan(stage.Id, _path.Count));
            foreach (var e in stage.Events)
                if (e.At == StageMoment.Start && _fired.Add(e)) Fire(world, e);
            if (!first) StageChanged?.Invoke(index);
        }

        private void End(SimWorld world, int winner)
        {
            Result = new MatchResult(winner);
            world.IsOver = true;
        }

        private int IndexOf(string id)
        {
            for (var i = 0; i < _stages.Count; i++)
                if (_stages[i].Id == id) return i;
            return -1;
        }

        private void Fire(SimWorld world, StageEventDef e)
        {
            switch (e.Kind)
            {
                case StageEventKind.Reinforce:
                {
                    var at = e.Position ?? (world.TryGetRally(e.Team, out var rally) ? rally : Vector2.Zero);
                    foreach (var id in e.Units) world.Economy.Airlift(e.Team, id, at);
                    if (e.Team == EnemyTeam) world.Emit(SimEvent.Alert(at, "toast.enemyReinforce"));
                    break;
                }
                case StageEventKind.AllyReinforce:
                    if (Betrayed || _def.Ally is not { } ally) break;
                    foreach (var id in e.Units) world.Economy.Airlift(PlayerTeam, id, e.Position ?? ally.Site, ally: true);
                    break;
                case StageEventKind.Expand:
                    world.Expand(e.Area);
                    break;
                case StageEventKind.Betrayal:
                    Betray(world);
                    break;
                case StageEventKind.Radio:
                    if (e.Key != null) world.Emit(SimEvent.RadioMessage(e.Key, e.Team));
                    break;
                case StageEventKind.Cp:
                    if (world.TryGetEconomy(e.Team, out var economy)) economy.Cp += e.Amount;
                    break;
                case StageEventKind.Income:
                    if (e.Amount > 0f && world.TryGetEconomy(e.Team, out var earner)) earner.ScaleIncome(e.Amount);
                    break;
                case StageEventKind.Strike:
                    Strike(world, e);
                    if (e.Every > 0.0) _standing.Add((e, world.Time + e.Every));
                    break;
            }
        }

        /// <summary>Repeating fire support, on the operation's clock, while the battle lasts.</summary>
        private void StandingStrikes(SimWorld world)
        {
            for (var i = 0; i < _standing.Count; i++)
            {
                var (e, next) = _standing[i];
                if (world.Time < next) continue;
                Strike(world, e);
                _standing[i] = (e, next + e.Every);
            }
        }

        /// <summary>
        /// Fire support at no cost for a side: at the event's spot, else on the other side's biggest
        /// group on the ground that none of the side's own vehicles stands near; nothing when there is none.
        /// </summary>
        private void Strike(SimWorld world, StageEventDef e)
        {
            if (e.Support == null || !world.Catalog.TryGetSupport(e.Support, out var support)) return;
            var target = e.Position ?? StrikeTarget(world, e.Team, support.IsLine ? support.Length * 0.5f : support.Radius);
            if (target is not { } at) return;
            world.TryGetRally(e.Team, out var home);
            var along = at - home;
            along = along.LengthSquared() > 1f ? Vector2.Normalize(along) : Vector2.UnitX;
            var start = support.IsLine ? at - along * (support.Length * 0.5f) : at;
            world.Strikes.Launch(support, e.Team, world.ClampToMap(start), start + along);
            FreeStrikes++;
        }

        /// <summary>The other side's vehicle with the most of its own round it (12 m), clear of <paramref name="team"/>'s by <paramref name="reach"/>.</summary>
        internal static Vector2? StrikeTarget(SimWorld world, int team, float reach)
        {
            var foe = team == PlayerTeam ? EnemyTeam : PlayerTeam;
            Vector2? best = null;
            var bestCount = 0;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != foe || v.Flying) continue;
                var count = 0;
                var clear = true;
                foreach (var o in world.VehicleList)
                {
                    if (!o.IsAlive || o.Flying) continue;
                    var d = Vector2.DistanceSquared(o.Position, v.Position);
                    if (o.Team == foe && d < 12f * 12f) count++;
                    else if (o.Team == team && d < (reach + 4f) * (reach + 4f))
                    {
                        clear = false;
                        break;
                    }
                }
                if (!clear || count <= bestCount) continue;
                bestCount = count;
                best = v.Position;
            }
            return best;
        }

        /// <summary>
        /// The ally changes sides: every one of its vehicles (and its HQ) now fights for the enemy,
        /// dropping what it was doing; nothing of the player's is touched.
        /// </summary>
        public void Betray(SimWorld world)
        {
            if (Betrayed) return;
            Betrayed = true;
            var turned = new List<Vehicle>();
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Ally) turned.Add(v);
            foreach (var v in turned)
            {
                world.Defect(v, EnemyTeam);
                // The traitor's base (its HQ and towers) is marked: the one to strike back at.
                if (v.Def.Static) v.Marked = true;
            }
            world.Emit(SimEvent.RadioMessage("radio.betrayal", 0, LinePriority.Story));
        }

        /// <summary>The ally's own reinforcements, on the operation's clock.</summary>
        private void AllyReinforcements(SimWorld world)
        {
            if (Betrayed || _def.Ally is not { } ally) return;
            while (_allyWave < ally.Reinforcements.Count && world.Time - _startedAt >= ally.Reinforcements[_allyWave].at)
            {
                foreach (var id in ally.Reinforcements[_allyWave].units) world.Economy.Airlift(PlayerTeam, id, ally.Site, ally: true);
                _allyWave++;
            }
        }
    }
}
