#nullable enable

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// A rule set on top of the shared simulation (Conquest, Assault, Survival, ...). Modes
    /// spawn forces and judge results, but units never contain mode-specific code.
    /// </summary>
    public interface IGameMode
    {
        void Setup(SimWorld world);

        /// <summary>Runs once per fixed step, before the world advances.</summary>
        void Tick(SimWorld world, float dt);

        MatchResult? Result { get; }
    }

    public readonly struct MatchResult
    {
        public MatchResult(int winningTeam) => WinningTeam = winningTeam;

        /// <summary>Winning team, or -1 for a draw.</summary>
        public int WinningTeam { get; }

        public bool IsDraw => WinningTeam < 0;
    }
}
