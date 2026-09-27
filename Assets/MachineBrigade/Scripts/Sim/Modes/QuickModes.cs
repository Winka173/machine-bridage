#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Modes
{
    public sealed class DeathmatchRules
    {
        /// <summary>Vehicles to destroy to win outright.</summary>
        public int KillTarget { get; set; } = 100;

        /// <summary>Seconds; when time runs out the side with more kills wins.</summary>
        public float TimeLimit { get; set; } = 12 * 60f;

        public SideSetup Player { get; set; } = new() { StartCp = 18f, Income = 1.35f };
        public SideSetup Enemy { get; set; } = new() { StartCp = 18f, Income = 1.35f };
    }

    /// <summary>
    /// Deathmatch (tử chiến): no objectives, just destruction. Command Points flow faster, and
    /// the first side to destroy the target number of enemy vehicles wins; at the time limit the
    /// side with more kills does.
    /// </summary>
    public sealed class DeathmatchMode : IGameMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly DeathmatchRules _rules;
        private readonly KillLedger _ledger = new();

        public DeathmatchMode(DeathmatchRules? rules = null) => _rules = rules ?? new DeathmatchRules();

        public MatchResult? Result { get; private set; }

        public int KillTarget => _rules.KillTarget;

        public int Kills(int team) => _ledger.Kills(team);

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, _rules.TimeLimit - (float)world.Time);

        public void Setup(SimWorld world)
        {
            world.EnableEconomy(_rules.Player.Build(PlayerTeam));
            world.EnableEconomy(_rules.Enemy.Build(EnemyTeam));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            BaseDefences.Build(world, PlayerTeam, EnemyTeam);
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            var ours = Kills(PlayerTeam);
            var theirs = Kills(EnemyTeam);
            var winner = ours >= _rules.KillTarget ? PlayerTeam : theirs >= _rules.KillTarget ? EnemyTeam : (int?)null;
            if (winner == null && world.Time >= _rules.TimeLimit) winner = ours == theirs ? -1 : ours > theirs ? PlayerTeam : EnemyTeam;
            if (winner == null) return;
            Result = new MatchResult(winner.Value);
            world.IsOver = true;
        }
    }

    public sealed class KingOfTheHillRules
    {
        /// <summary>Score to win; the sole holder of the hill scores <see cref="ScorePerSecond"/>.</summary>
        public float ScoreTarget { get; set; } = 100f;

        public float ScorePerSecond { get; set; } = 0.75f;
        public float CaptureSeconds { get; set; } = 8f;

        /// <summary>Seconds; at the limit the higher score wins.</summary>
        public float TimeLimit { get; set; } = 15 * 60f;

        /// <summary>Id of the map objective that becomes the hill.</summary>
        public string Hill { get; set; } = "town";

        public SideSetup Player { get; set; } = new() { StartCp = 16f, Income = 1.2f };
        public SideSetup Enemy { get; set; } = new() { StartCp = 16f, Income = 1.2f };
    }

    /// <summary>
    /// King of the Hill (vua đồi): one objective in the middle of the map. Holding it alone builds
    /// score; the first side to the target wins. Everything converges on one spot, so it is the
    /// most explosive mode.
    /// </summary>
    public sealed class KingOfTheHillMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly KingOfTheHillRules _rules;
        private readonly List<ObjectiveState> _points = new();
        private readonly float[] _score = new float[2];

        public KingOfTheHillMode(KingOfTheHillRules? rules = null) => _rules = rules ?? new KingOfTheHillRules();

        public IReadOnlyList<ObjectiveState> Points => _points;

        public MatchResult? Result { get; private set; }

        public float ScoreTarget => _rules.ScoreTarget;

        public int Score(int team) => (int)MathF.Floor(_score[team]);

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, _rules.TimeLimit - (float)world.Time);

        public void Setup(SimWorld world)
        {
            CapturePointDef? hill = null;
            foreach (var def in world.Map.Points)
                if (def.Id == _rules.Hill) hill = def;
            hill ??= world.Map.Points.Count > 0 ? world.Map.Points[0] : null;
            if (hill != null) _points.Add(new ObjectiveState(hill.Value));
            world.EnableEconomy(_rules.Player.Build(PlayerTeam));
            world.EnableEconomy(_rules.Enemy.Build(EnemyTeam));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            BaseDefences.Build(world, PlayerTeam, EnemyTeam);
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null || _points.Count == 0) return;
            var hill = _points[0];
            PointCapture.Tick(world, hill, dt, _rules.CaptureSeconds);
            if (hill.Owner is PlayerTeam or EnemyTeam && !hill.Contested) _score[hill.Owner] += _rules.ScorePerSecond * dt;
            // The holder also earns a little more, so a strong hold snowballs a bit.
            if (world.TryGetEconomy(PlayerTeam, out var e0)) e0.Bonus = hill.Owner == PlayerTeam ? 0.35f : 0f;
            if (world.TryGetEconomy(EnemyTeam, out var e1)) e1.Bonus = hill.Owner == EnemyTeam ? 0.35f : 0f;

            int? winner = _score[PlayerTeam] >= _rules.ScoreTarget ? PlayerTeam : _score[EnemyTeam] >= _rules.ScoreTarget ? EnemyTeam : null;
            if (winner == null && world.Time >= _rules.TimeLimit)
                winner = Score(PlayerTeam) == Score(EnemyTeam) ? -1 : Score(PlayerTeam) > Score(EnemyTeam) ? PlayerTeam : EnemyTeam;
            if (winner == null) return;
            Result = new MatchResult(winner.Value);
            world.IsOver = true;
        }
    }

    public sealed class AssaultRules
    {
        /// <summary>Seconds the attacker has to take every objective.</summary>
        public float TimeLimit { get; set; } = 14 * 60f;

        public float CaptureSeconds { get; set; } = 12f;

        /// <summary>The attacker (the player) buys faster; the defender starts dug in with more CP.</summary>
        public SideSetup Attacker { get; set; } = new() { StartCp = 20f, Income = 1.45f };

        public SideSetup Defender { get; set; } = new() { StartCp = 26f, Income = 1.05f };
    }

    /// <summary>
    /// Assault (công phá): the enemy holds every objective when the battle starts. The player's
    /// army must own all of them at the same time before the clock runs out; the defender wins
    /// by holding on.
    /// </summary>
    public sealed class AssaultMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly AssaultRules _rules;
        private readonly List<ObjectiveState> _points = new();

        public AssaultMode(AssaultRules? rules = null) => _rules = rules ?? new AssaultRules();

        public IReadOnlyList<ObjectiveState> Points => _points;

        public MatchResult? Result { get; private set; }

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, _rules.TimeLimit - (float)world.Time);

        public int Taken => PointCapture.Held(_points, PlayerTeam);

        public void Setup(SimWorld world)
        {
            foreach (var def in world.Map.Points)
            {
                var point = new ObjectiveState(def);
                PointCapture.Own(point, EnemyTeam);
                _points.Add(point);
            }
            world.EnableEconomy(_rules.Attacker.Build(PlayerTeam));
            world.EnableEconomy(_rules.Defender.Build(EnemyTeam));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            foreach (var point in _points) PointCapture.Tick(world, point, dt, _rules.CaptureSeconds);
            if (world.TryGetEconomy(PlayerTeam, out var e0)) e0.Bonus = 0.25f * Taken;
            if (_points.Count > 0 && Taken == _points.Count) Result = new MatchResult(PlayerTeam);
            else if (world.Time >= _rules.TimeLimit) Result = new MatchResult(EnemyTeam);
            if (Result != null) world.IsOver = true;
        }
    }
}
