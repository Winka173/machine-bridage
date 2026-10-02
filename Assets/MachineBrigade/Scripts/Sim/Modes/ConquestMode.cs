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

        /// <summary>Bases and home zones at both camps (see <see cref="Modes.BaseDefences"/>).</summary>
        public bool BaseDefences { get; set; } = true;

        /// <summary>Each side's base loadout and role; null: a bare HQ each.</summary>
        public BaseSetup? Bases { get; set; }

        /// <summary>A neutral watchtower on each point, firing on both sides (see <see cref="Modes.Outposts"/>).</summary>
        public bool Outposts { get; set; } = true;

        /// <summary>
        /// A side this many tickets behind gets a boss once (Battlefield 1's behemoths): a bounded
        /// comeback, not a rubber band. 0 turns it off.
        /// </summary>
        public int ComebackGap { get; set; } = 100;

        public string ComebackBoss { get; set; } = "behemoth";
        public float StartCp { get; set; } = 14f;

        /// <summary>After this long the side behind gets its one-off help (prompt 13 H.12); 0: the old sliding boost only (the menu battle).</summary>
        public float UnderdogAfter { get; set; } = 240f;
        public IReadOnlyList<string> PlayerVehicles { get; set; } = Array.Empty<string>();
        public IReadOnlyList<string> PlayerSupports { get; set; } = Array.Empty<string>();
        public IReadOnlyList<string> EnemyVehicles { get; set; } = Array.Empty<string>();
        public IReadOnlyList<string> EnemySupports { get; set; } = Array.Empty<string>();

        /// <summary>Prompt 30 L4: the rules row of balance.json "matchRules" that sets the numbers below; null keeps them (the menu battle).</summary>
        public string? RulesId { get; set; } = "conquest";

        /// <summary>Seconds; 0: no clock (the side with more points wins at the limit, then overtime).</summary>
        public float TimeLimit { get; set; }

        /// <summary>The last seconds of the clock in which points count <see cref="FinalScale"/> times.</summary>
        public float FinalPhaseSeconds { get; set; } = 120f;

        public float FinalScale { get; set; } = 2f;

        /// <summary>Tied at the limit: up to this long, the first side to take one more point wins; else a draw.</summary>
        public float Overtime { get; set; } = 60f;

        /// <summary>Sets the numbers from the data (sheet "Luật trận"), and the world's catch-up ceiling.</summary>
        public void Apply(SimWorld world)
        {
            if (RulesId == null || world.Catalog.MatchRules.For(RulesId) is not { } r) return;
            Tickets = (int)r.Get("points", Tickets);
            Bleed = r.Get("bleed", Bleed);
            KillTicketFactor = r.Get("killTicketFactor", KillTicketFactor);
            TimeLimit = r.Get("timeLimit", TimeLimit);
            FinalPhaseSeconds = r.Get("finalPhase", FinalPhaseSeconds);
            FinalScale = r.Get("finalScale", FinalScale);
            Overtime = r.Get("overtime", Overtime);
            world.CatchUpMax = r.Get("catchUpMax", world.CatchUpMax);
        }
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
            _ledger.Lost += (team, cost) =>
            {
                if (_rules.KillTicketFactor > 0f) _tickets[team] -= MathF.Max(1f, MathF.Ceiling(cost * _rules.KillTicketFactor));
            };
        }

        public IReadOnlyList<ObjectiveState> Points => _points;

        public MatchResult? Result { get; private set; }

        /// <summary>
        /// Prompt 28 I.7: the final phase. Conquest has no clock, so it starts when the losing side's tickets would run out
        /// within economy.finalPhase seconds at the current bleed; points then count economy.finalPhaseScale times.
        /// </summary>
        public bool InFinalPhase { get; private set; }

        private float FinalPhase(SimWorld world, int held0, int held1)
        {
            // Prompt 30 L4: with a clock, the final phase is its last minutes ("2 phút cuối x2").
            if (_rules.TimeLimit > 0f)
            {
                InFinalPhase = world.Time >= _rules.TimeLimit - _rules.FinalPhaseSeconds;
                return InFinalPhase ? _rules.FinalScale : 1f;
            }
            var ai = world.Catalog.Ai;
            if (!InFinalPhase && held0 != held1)
            {
                var low = held0 < held1 ? _tickets[PlayerTeam] : _tickets[EnemyTeam];
                var eta = low / MathF.Max(0.01f, _rules.Bleed * world.PointScale * Math.Abs(held0 - held1));
                if (eta <= ai.Get("economy.finalPhase", 120f)) InFinalPhase = true;
            }
            return InFinalPhase ? ai.Get("economy.finalPhaseScale", 2f) : 1f;
        }

        public int Tickets(int team) => (int)MathF.Ceiling(MathF.Max(0f, _tickets[team]));

        public int MaxTickets => _rules.Tickets;

        public int Held(int team) => PointCapture.Held(_points, team);

        public void Setup(SimWorld world)
        {
            _rules.Apply(world);
            _tickets[0] = _tickets[1] = _rules.Tickets;
            foreach (var def in world.Map.Points) _points.Add(new ObjectiveState(def));
            world.CatchUp = true;
            world.EnableEconomy(new TeamEconomy(PlayerTeam, _rules.StartCp, vehicles: _rules.PlayerVehicles, supports: _rules.PlayerSupports));
            world.EnableEconomy(new TeamEconomy(EnemyTeam, _rules.StartCp, vehicles: _rules.EnemyVehicles, supports: _rules.EnemySupports));
            if (_rules.UnderdogAfter > 0f) world.Economy.Underdog = new Economy.UnderdogRules { After = _rules.UnderdogAfter };
            foreach (var unit in world.MapUnits) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            if (_rules.BaseDefences) BaseDefences.Build(world, _rules.Bases, PlayerTeam, EnemyTeam);
            world.Bases.PointOwner = OwnerOf;
            if (_rules.Outposts) _outposts = new Outposts(world, _points, neutral: true);
        }

        private Outposts? _outposts;

        private int OwnerOf(string id)
        {
            foreach (var p in _points)
                if (p.Def.Id == id) return p.Owner;
            return -1;
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            foreach (var point in _points) Capture(world, point, dt);

            var held0 = Held(PlayerTeam);
            var held1 = Held(EnemyTeam);
            // Prompt 28 I.6 / I.7: points are worth more under pressure and in the final phase.
            var bleed = _rules.Bleed * world.PointScale * FinalPhase(world, held0, held1);
            if (held0 < held1) _tickets[PlayerTeam] -= bleed * (held1 - held0) * dt;
            else if (held1 < held0) _tickets[EnemyTeam] -= bleed * (held0 - held1) * dt;
            if (world.TryGetEconomy(PlayerTeam, out var e0)) e0.Bonus = _rules.PointIncome * held0 * world.PointScale;
            if (world.TryGetEconomy(EnemyTeam, out var e1)) e1.Bonus = _rules.PointIncome * held1 * world.PointScale;

            _outposts?.Tick(world);
            Comeback(world);
            var lost0 = _tickets[PlayerTeam] <= 0f;
            var lost1 = _tickets[EnemyTeam] <= 0f;
            int? winner = lost0 || lost1 ? lost0 && lost1 ? -1 : lost0 ? EnemyTeam : PlayerTeam : null;
            winner ??= AtTheLimit(world, held0, held1);
            if (winner == null) return;
            Result = new MatchResult(winner.Value);
            world.IsOver = true;
        }

        private double _overtimeUntil = double.NaN;
        private readonly int[] _heldAtOvertime = new int[2];

        /// <summary>The clock is out (or in overtime): seconds left of it, 0 without a clock.</summary>
        public float SecondsLeft(SimWorld world) => _rules.TimeLimit > 0f ? MathF.Max(0f, _rules.TimeLimit - (float)world.Time) : 0f;

        public bool InOvertime => !double.IsNaN(_overtimeUntil);

        /// <summary>
        /// Prompt 30 L4 at the time limit: more points wins; level, an overtime of up to <see cref="ConquestRules.Overtime"/> s
        /// in which the first side to take one more point than it held wins; still level after it, a draw.
        /// </summary>
        internal int? AtTheLimit(SimWorld world, int held0, int held1)
        {
            if (_rules.TimeLimit <= 0f || world.Time < _rules.TimeLimit) return null;
            if (!InOvertime)
            {
                if (Tickets(PlayerTeam) != Tickets(EnemyTeam)) return Tickets(PlayerTeam) > Tickets(EnemyTeam) ? PlayerTeam : EnemyTeam;
                _overtimeUntil = world.Time + _rules.Overtime;
                _heldAtOvertime[PlayerTeam] = held0;
                _heldAtOvertime[EnemyTeam] = held1;
                return null;
            }
            var gain0 = held0 > _heldAtOvertime[PlayerTeam];
            var gain1 = held1 > _heldAtOvertime[EnemyTeam];
            if (gain0 != gain1) return gain0 ? PlayerTeam : EnemyTeam;
            return world.Time >= _overtimeUntil ? -1 : null;
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
