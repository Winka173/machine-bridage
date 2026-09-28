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
