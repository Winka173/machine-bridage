#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
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
    public sealed class OperationMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = MissionMode.PlayerTeam;
        public const int EnemyTeam = MissionMode.EnemyTeam;

        /// <summary>Seconds the player has to choose a branch before the first option is taken.</summary>
        public const double ChoiceSeconds = 15.0;

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

        public OperationMode(MissionDef def, SideSetup player, SideSetup? enemy)
        {
            _def = def;
            _player = player;
            _enemy = enemy;
            // A mission with an ally but no stages is one stage: itself.
            _stages = def.Stages.Count > 0 ? def.Stages : new[] { new StageDef { Id = "main", Mission = def, Checkpoint = false } };
        }

        public MissionDef Def => _def;

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

        /// <summary>The ally has turned on the player.</summary>
        public bool Betrayed { get; private set; }

        /// <summary>A later stage began (its index): the commanders are set for its goal, in the same step.</summary>
        public event Action<int>? StageChanged;

        public void Setup(SimWorld world)
        {
            _startedAt = world.Time;
            if (_def.PlayArea is { } area) world.Expand(area);
            Begin(world, 0, true);
            // A big operation's enemy may field more vehicles (its own ceiling, else the operations').
            if (_def.Stages.Count > 0 && world.TryGetEconomy(EnemyTeam, out var enemy))
                enemy.VehicleCap = _def.EnemyCap > 0 ? _def.EnemyCap : world.Catalog.VehicleCapFor("Operation");
            // A staged mission's own units are placed once (a mission of one stage places them itself).
            if (_def.Stages.Count > 0)
                foreach (var u in _def.Units) world.SpawnVehicle(u.DefId, u.Team, u.Position, u.Heading);
            if (_def.Ally is { } ally)
            {
                // Its base first: the HQ at its site, its towers round it (fixed defences, like a camp's).
                if (ally.Hq != null) Raise(world, ally.Hq, ally.Site, ally.Heading);
                foreach (var s in ally.Structures) Raise(world, s.DefId, s.Position, s.Heading);
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
            }
            StageIndex = index;
            _path.Add(index);
            var stage = _stages[index];
            Current = new MissionMode(stage.Mission, _player, _enemy) { Staged = true };
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
            }
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
            foreach (var v in turned) world.Defect(v, EnemyTeam);
            world.Emit(SimEvent.RadioMessage("radio.betrayal"));
        }

        private static void Raise(SimWorld world, string defId, Vector2 at, float heading)
        {
            if (!world.Catalog.Vehicles.ContainsKey(defId)) return;
            var v = world.SpawnVehicle(defId, PlayerTeam, at, heading);
            v.Ally = true;
            if (v.Def.Static) world.AnchorDefence(v);
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
