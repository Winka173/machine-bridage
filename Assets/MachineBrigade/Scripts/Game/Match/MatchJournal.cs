using System.Collections.Generic;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// A multi-stage mission's way back to a checkpoint. The battle is rebuilt from the same seed,
    /// and the player's own commands and switches are replayed step for step up to it, behind the
    /// loading screen. That works because the simulation is deterministic. It is kept in memory
    /// only and lasts until the app closes.
    /// </summary>
    internal sealed class ResumePoint
    {
        public string Mission;
        public int Tier;
        public long Tick;
        public ulong Hash;
        public int Stage;
        public readonly List<(long tick, Command command)> Commands = new();
        public readonly List<(long tick, string input, string value)> Inputs = new();
    }

    /// <summary>
    /// Brings a rebuilt battle (the same mission, the same seed) back to a checkpoint: the
    /// player's commands and switches are fed in at the steps they were given, and the battle is
    /// stepped as it was played, with nothing drawn, up to the checkpoint's step.
    /// </summary>
    internal sealed class CheckpointReplay
    {
        private readonly ResumePoint _resume;
        private readonly ModeSession _session;
        private readonly SimWorld _world;
        private int _command, _input;

        public CheckpointReplay(ResumePoint resume, ModeSession session, SimWorld world)
        {
            _resume = resume;
            _session = session;
            _world = world;
        }

        /// <summary>How far the replay is (0 to 1).</summary>
        public float Progress => _resume.Tick <= 0 ? 1f : (float)_world.Tick / _resume.Tick;

        /// <summary>The battle is in the state the checkpoint kept (its fingerprint matches).</summary>
        public bool Matches => _world.StateHash() == _resume.Hash;

        /// <summary>Steps on, at most <paramref name="steps"/> this call; false once at the checkpoint.</summary>
        public bool Advance(float dt, int steps)
        {
            for (var i = 0; i < steps; i++)
            {
                Feed();
                if (_world.Tick >= _resume.Tick || _world.IsOver) return false;
                _session.Mode.Tick(_world, dt);
                _session.TickAi(_world, dt);
                _world.Step(dt);
                _world.ClearEvents();
            }
            Feed();
            return _world.Tick < _resume.Tick && !_world.IsOver;
        }

        /// <summary>The journal's commands and switches for the step the replay is on.</summary>
        private void Feed()
        {
            while (_command < _resume.Commands.Count && _resume.Commands[_command].tick <= _world.Tick)
                _world.SubmitPlayer(_resume.Commands[_command++].command);
            while (_input < _resume.Inputs.Count && _resume.Inputs[_input].tick <= _world.Tick)
            {
                var (_, input, value) = _resume.Inputs[_input++];
                if (input == "choose")
                {
                    (_session as MissionSession)?.Choose(_world, value);
                    continue;
                }
                MatchJournal.Record(_world, input, value);
                MatchJournal.Apply(_session.PlayerAi, input, value);
            }
        }
    }

    internal static class MatchJournal
    {
        /// <summary>The checkpoint the next battle starts from (set by the result screen, used once).</summary>
        public static ResumePoint Pending;

        /// <summary>
        /// The player's switches this battle, with the step each was made at: the commander's stance,
        /// auto deploy, auto strike, the focus point, a branch chosen. The commands go to
        /// <see cref="SimWorld.Journal"/>.
        /// </summary>
        public static readonly List<(long tick, string input, string value)> Inputs = new();

        public static void Record(SimWorld world, string input, string value) => Inputs.Add((world.Tick, input, value));

        /// <summary>A recorded switch put back on the player's commander.</summary>
        public static void Apply(MachineBrigade.Sim.AI.ConquestAi ai, string input, string value)
        {
            if (ai == null) return;
            switch (input)
            {
                case "stance":
                    ai.Stance = value == "defend" ? MachineBrigade.Sim.AI.CommanderStance.Defend : MachineBrigade.Sim.AI.CommanderStance.Attack;
                    break;
                case "autoDeploy":
                    ai.AutoDeploy = value == "1";
                    break;
                case "autoStrike":
                    ai.AutoStrike = value == "1";
                    break;
                case "focus":
                    ai.FocusPoint = string.IsNullOrEmpty(value) ? null : value;
                    break;
            }
        }

        /// <summary>The way back to the operation's last checkpoint, or null when it has none.</summary>
        public static ResumePoint Checkpoint(SimWorld world, string mission, int tier, OperationMode op)
        {
            if (op == null || op.Checkpoints.Count == 0) return null;
            var last = op.Checkpoints[op.Checkpoints.Count - 1];
            var point = new ResumePoint { Mission = mission, Tier = tier, Tick = last.Tick, Hash = last.Hash, Stage = last.Stage };
            foreach (var c in world.Journal)
                if (c.tick <= last.Tick) point.Commands.Add(c);
            foreach (var i in Inputs)
                if (i.tick <= last.Tick) point.Inputs.Add(i);
            return point;
        }
    }
}
