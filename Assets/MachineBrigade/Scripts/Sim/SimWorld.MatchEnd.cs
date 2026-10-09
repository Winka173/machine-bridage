#nullable enable
using System;

namespace MachineBrigade.Sim
{
    /// <summary>Prompt 30 L3: where a match is in its ending (sheet "Kết trận").</summary>
    public enum MatchPhase
    {
        /// <summary>The battle runs.</summary>
        Running,

        /// <summary>The tick the win or loss happened: result, rewards, stars and score are fixed; gameplay stands still.</summary>
        Resolved,

        /// <summary>Pictures only (camera, effects, animation, the boss's death chain, retreating proxies, the last lines).</summary>
        Presentation,

        /// <summary>The results panel.</summary>
        Results,
    }

    /// <summary>How long the presentation lasts (sheet "Kết trận"); the Game layer picks the kind.</summary>
    public enum EndKind
    {
        /// <summary>The first win of a main boss's mission or a big operation: 6-8 s.</summary>
        FirstBigWin,

        /// <summary>The first win of an ordinary mission: 4-5 s.</summary>
        FirstWin,

        /// <summary>A mission played again: 2.5-4 s.</summary>
        Replay,

        /// <summary>A loss: 3-4 s, no slow motion.</summary>
        Loss,
    }

    /// <summary>
    /// Prompt 30 L3: RUNNING -> RESOLVED -> PRESENTATION -> RESULTS. The world resolves on the tick a mode ends the match
    /// (<see cref="SimWorld.IsOver"/>); from then <see cref="SimWorld.Step"/> runs none of the battle's systems, so the result
    /// cannot depend on the presentation, and a replay of the same commands resolves on the same tick. The presentation's
    /// clock (<see cref="Elapsed"/>) is the view's; slow motion is the view's alone (it scales what is drawn, not this).
    /// </summary>
    public sealed class MatchEnd
    {
        /// <summary>A tap skips the presentation after this long.</summary>
        public const double SkipAfter = 0.75;

        public MatchPhase Phase { get; private set; } = MatchPhase.Running;

        /// <summary>The tick and battle time the match was resolved on (-1 / NaN while running).</summary>
        public long ResolvedTick { get; private set; } = -1;

        public double ResolvedTime { get; private set; } = double.NaN;

        public EndKind Kind { get; private set; }

        /// <summary>Seconds of presentation so far.</summary>
        public double Elapsed { get; private set; }

        public double Duration { get; private set; }

        /// <summary>The presentation was skipped (a story line it cut is shown in the results and the log).</summary>
        public bool Skipped { get; private set; }

        /// <summary>The presentation's length for a kind (the middle of the sheet's range).</summary>
        public static double DurationFor(EndKind kind) => kind switch
        {
            EndKind.FirstBigWin => global::MachineBrigade.Sim.Content.SimTunables.Modes.MatchEnd.DurationForKindValue,
            EndKind.FirstWin => global::MachineBrigade.Sim.Content.SimTunables.Modes.MatchEnd.DurationForKindValue2,
            EndKind.Replay => global::MachineBrigade.Sim.Content.SimTunables.Modes.MatchEnd.DurationForKindValue3,
            _ => global::MachineBrigade.Sim.Content.SimTunables.Modes.MatchEnd.DurationForKindValue4,
        };

        /// <summary>Whether the presentation may slow the pictures (boss, HQ and big operation wins; never a loss).</summary>
        public bool SlowMotion => Kind != EndKind.Loss && Kind != EndKind.Replay;

        internal void Resolve(SimWorld world)
        {
            if (Phase != MatchPhase.Running) return;
            Phase = MatchPhase.Resolved;
            ResolvedTick = world.Tick;
            ResolvedTime = world.Time;
        }

        /// <summary>Prompt 30 L5: back to running after "Continue" (the win stays recorded by the session).</summary>
        internal void Reopen()
        {
            Phase = MatchPhase.Running;
            ResolvedTick = -1;
            ResolvedTime = double.NaN;
            Elapsed = 0;
            Skipped = false;
            Continued++;
        }

        /// <summary>How many times the match was continued into its endless part.</summary>
        public int Continued { get; private set; }

        /// <summary>The view starts the presentation (from RESOLVED only).</summary>
        public void BeginPresentation(EndKind kind, double? seconds = null)
        {
            if (Phase != MatchPhase.Resolved) return;
            Kind = kind;
            Duration = Math.Max(SkipAfter, seconds ?? DurationFor(kind));
            Elapsed = 0;
            Phase = MatchPhase.Presentation;
        }

        /// <summary>A tap: skips to the results once <see cref="SkipAfter"/> has passed. True if it did.</summary>
        public bool Skip()
        {
            if (Phase != MatchPhase.Presentation || Elapsed < SkipAfter) return false;
            Skipped = true;
            Phase = MatchPhase.Results;
            return true;
        }

        /// <summary>Straight to the results (no presentation: a menu battle, a test).</summary>
        public void ShowResults()
        {
            if (Phase is MatchPhase.Resolved or MatchPhase.Presentation) Phase = MatchPhase.Results;
        }

        /// <summary>The presentation's clock: the view calls it with unscaled seconds (slow motion never stretches it).</summary>
        public void Advance(double dt)
        {
            if (Phase != MatchPhase.Presentation) return;
            Elapsed += dt;
            if (Elapsed >= Duration) Phase = MatchPhase.Results;
        }
    }

    public sealed partial class SimWorld
    {
        /// <summary>Prompt 30 L3: the match's ending.</summary>
        public MatchEnd Ending { get; } = new();
    }
}

namespace MachineBrigade.Sim
{
    public sealed partial class SimWorld
    {
        private readonly (float hp, float damage)[] _teamStats = { (1f, 1f), (1f, 1f) };

        /// <summary>Prompt 30 L5: mini bosses join without their big attack (Survival).</summary>
        public bool MiniBossesNoBigAttacks { get; set; }

        /// <summary>Prompt 30 L5: the endless part's stat growth for a side; vehicles that join from now on carry it.</summary>
        public void SetTeamStats(int team, float hp, float damage)
        {
            if (team is 0 or 1) _teamStats[team] = (hp, damage);
        }

        public (float hp, float damage) TeamStats(int team) => team is 0 or 1 ? _teamStats[team] : (1f, 1f);

        /// <summary>
        /// Prompt 30 L5: the results' "Continue": the battle runs again from where it stood (the win already recorded).
        /// Only from a resolved match.
        /// </summary>
        public bool ContinueMatch()
        {
            if (Ending.Phase == MatchPhase.Running) return false;
            _over = false;
            Ending.Reopen();
            return true;
        }
    }
}
