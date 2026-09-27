#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>One objective's live state. Progress runs from -1 (team 1 owns it) to +1 (team 0).</summary>
    public sealed class ObjectiveState
    {
        internal ObjectiveState(CapturePointDef def) => Def = def;

        public CapturePointDef Def { get; }

        /// <summary>Owning team, or -1 while neutral.</summary>
        public int Owner { get; internal set; } = -1;

        public float Progress { get; internal set; }

        /// <summary>Both sides have vehicles inside the circle, so nothing moves.</summary>
        public bool Contested { get; internal set; }

        /// <summary>Out of play for now (an Assault sector not yet live, or one already taken): it cannot change hands.</summary>
        public bool Locked { get; internal set; }
    }

    /// <summary>Tunable Conquest rules; defaults follow the game plan.</summary>
    public sealed class ConquestRules
    {
        public int Tickets { get; set; } = 400;

        /// <summary>Tickets lost per destroyed vehicle, as a fraction of its CP cost.</summary>
        public float KillTicketFactor { get; set; } = 0.5f;

        /// <summary>Seconds for one capture-rate-1 vehicle alone to turn a neutral point.</summary>
        public float CaptureSeconds { get; set; } = 10f;

        /// <summary>Tickets per second lost per objective the other side holds more.</summary>
        public float Bleed { get; set; } = 0.6f;

        public float PointIncome { get; set; } = 0.3f;

        /// <summary>Spawn bastions and home zones at both camps (see <see cref="Modes.BaseDefences"/>).</summary>
        public bool BaseDefences { get; set; } = true;

        /// <summary>A neutral watchtower on each point, firing on both sides (see <see cref="Modes.Outposts"/>).</summary>
        public bool Outposts { get; set; } = true;

        /// <summary>
        /// A side this many tickets behind gets a boss once (Battlefield 1's behemoths): a bounded
        /// comeback, not a rubber band. 0 turns it off.
        /// </summary>
        public int ComebackGap { get; set; } = 100;

        public string ComebackBoss { get; set; } = "behemoth";
        public float StartCp { get; set; } = 14f;
        public IReadOnlyList<string> PlayerVehicles { get; set; } = Array.Empty<string>();
        public IReadOnlyList<string> PlayerSupports { get; set; } = Array.Empty<string>();
        public IReadOnlyList<string> EnemyVehicles { get; set; } = Array.Empty<string>();
        public IReadOnlyList<string> EnemySupports { get; set; } = Array.Empty<string>();
    }

    /// <summary>
    /// Conquest (giữ cứ điểm): hold more capture points than the enemy to drain their tickets;
    /// losing vehicles costs tickets too. The side that reaches zero loses. Both sides buy
    /// vehicles and strikes with Command Points.
    /// </summary>
    public sealed class ConquestMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly ConquestRules _rules;
        private readonly List<ObjectiveState> _points = new();
        private readonly float[] _tickets = new float[2];
        private readonly KillLedger _ledger = new();

        public ConquestMode(ConquestRules? rules = null)
        {
            _rules = rules ?? new ConquestRules();
            // A destroyed vehicle costs its side tickets: its CP cost times the kill ticket factor (at least one).
            _ledger.Lost += (team, cost) => _tickets[team] -= MathF.Max(1f, MathF.Ceiling(cost * _rules.KillTicketFactor));
        }

        public IReadOnlyList<ObjectiveState> Points => _points;

        public MatchResult? Result { get; private set; }

        public int Tickets(int team) => (int)MathF.Ceiling(MathF.Max(0f, _tickets[team]));

        public int MaxTickets => _rules.Tickets;

        public int Held(int team) => PointCapture.Held(_points, team);

        public void Setup(SimWorld world)
        {
            _tickets[0] = _tickets[1] = _rules.Tickets;
            foreach (var def in world.Map.Points) _points.Add(new ObjectiveState(def));
            world.EnableEconomy(new TeamEconomy(PlayerTeam, _rules.StartCp, vehicles: _rules.PlayerVehicles, supports: _rules.PlayerSupports));
            world.EnableEconomy(new TeamEconomy(EnemyTeam, _rules.StartCp, vehicles: _rules.EnemyVehicles, supports: _rules.EnemySupports));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            if (_rules.BaseDefences) BaseDefences.Build(world, PlayerTeam, EnemyTeam);
            if (_rules.Outposts) _outposts = new Outposts(world, _points, neutral: true);
        }

        private Outposts? _outposts;

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            foreach (var point in _points) Capture(world, point, dt);

            var held0 = Held(PlayerTeam);
            var held1 = Held(EnemyTeam);
            if (held0 < held1) _tickets[PlayerTeam] -= _rules.Bleed * (held1 - held0) * dt;
            else if (held1 < held0) _tickets[EnemyTeam] -= _rules.Bleed * (held0 - held1) * dt;
            if (world.TryGetEconomy(PlayerTeam, out var e0)) e0.Bonus = _rules.PointIncome * held0;
            if (world.TryGetEconomy(EnemyTeam, out var e1)) e1.Bonus = _rules.PointIncome * held1;

            _outposts?.Tick(world);
            Comeback(world);
            var lost0 = _tickets[PlayerTeam] <= 0f;
            var lost1 = _tickets[EnemyTeam] <= 0f;
            if (!lost0 && !lost1) return;
            Result = new MatchResult(lost0 && lost1 ? -1 : lost0 ? EnemyTeam : PlayerTeam);
            world.IsOver = true;
        }

        private void Capture(SimWorld world, ObjectiveState point, float dt) => PointCapture.Tick(world, point, dt, _rules.CaptureSeconds);

        private readonly bool[] _comebackGiven = new bool[2];

        /// <summary>The side far behind on tickets gets its boss, once a match.</summary>
        private void Comeback(SimWorld world)
        {
            if (_rules.ComebackGap <= 0 || !world.Catalog.Vehicles.ContainsKey(_rules.ComebackBoss)) return;
            for (var team = 0; team < 2; team++)
            {
                if (_comebackGiven[team] || _tickets[1 - team] - _tickets[team] < _rules.ComebackGap) continue;
                if (!world.TryGetRally(team, out var rally)) continue;
                _comebackGiven[team] = true;
                var toward = rally.LengthSquared() > 1f ? Vector2.Normalize(-rally) : Vector2.UnitX;
                world.SpawnVehicle(_rules.ComebackBoss, team, rally + toward * 6f, SimMath.HeadingOf(toward));
                world.Emit(SimEvent.Alert(rally, team == PlayerTeam ? "comeback.ours" : "comeback.theirs"));
            }
        }
    }
}
