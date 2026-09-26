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
    public sealed class ConquestMode : IGameMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly ConquestRules _rules;
        private readonly List<ObjectiveState> _points = new();
        private readonly float[] _tickets = new float[2];
        private readonly Dictionary<EntityId, (int team, int cost)> _alive = new();
        private readonly List<EntityId> _gone = new();
        private readonly HashSet<EntityId> _seen = new();

        public ConquestMode(ConquestRules? rules = null) => _rules = rules ?? new ConquestRules();

        public IReadOnlyList<ObjectiveState> Points => _points;

        public MatchResult? Result { get; private set; }

        public int Tickets(int team) => (int)MathF.Ceiling(MathF.Max(0f, _tickets[team]));

        public int MaxTickets => _rules.Tickets;

        public int Held(int team)
        {
            var count = 0;
            foreach (var p in _points)
                if (p.Owner == team) count++;
            return count;
        }

        public void Setup(SimWorld world)
        {
            _tickets[0] = _tickets[1] = _rules.Tickets;
            foreach (var def in world.Map.Points) _points.Add(new ObjectiveState(def));
            world.EnableEconomy(new TeamEconomy(PlayerTeam, _rules.StartCp, vehicles: _rules.PlayerVehicles, supports: _rules.PlayerSupports));
            world.EnableEconomy(new TeamEconomy(EnemyTeam, _rules.StartCp, vehicles: _rules.EnemyVehicles, supports: _rules.EnemySupports));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            CountLosses(world);
            foreach (var point in _points) Capture(world, point, dt);

            var held0 = Held(PlayerTeam);
            var held1 = Held(EnemyTeam);
            if (held0 < held1) _tickets[PlayerTeam] -= _rules.Bleed * (held1 - held0) * dt;
            else if (held1 < held0) _tickets[EnemyTeam] -= _rules.Bleed * (held0 - held1) * dt;
            if (world.TryGetEconomy(PlayerTeam, out var e0)) e0.Bonus = _rules.PointIncome * held0;
            if (world.TryGetEconomy(EnemyTeam, out var e1)) e1.Bonus = _rules.PointIncome * held1;

            var lost0 = _tickets[PlayerTeam] <= 0f;
            var lost1 = _tickets[EnemyTeam] <= 0f;
            if (!lost0 && !lost1) return;
            Result = new MatchResult(lost0 && lost1 ? -1 : lost0 ? EnemyTeam : PlayerTeam);
            world.IsOver = true;
        }

        /// <summary>A destroyed vehicle costs its side tickets equal to its CP cost.</summary>
        private void CountLosses(SimWorld world)
        {
            _seen.Clear();
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Team < 0 || v.Team > 1) continue;
                _seen.Add(v.Id);
                if (!_alive.ContainsKey(v.Id)) _alive[v.Id] = (v.Team, v.Def.CpCost);
            }
            _gone.Clear();
            foreach (var id in _alive.Keys)
                if (!_seen.Contains(id)) _gone.Add(id);
            foreach (var id in _gone)
            {
                var (team, cost) = _alive[id];
                _tickets[team] -= MathF.Max(1f, MathF.Ceiling(cost * _rules.KillTicketFactor));
                _alive.Remove(id);
            }
        }

        private void Capture(SimWorld world, ObjectiveState point, float dt)
        {
            var power0 = 0f;
            var power1 = 0f;
            var r = point.Def.Radius;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Flying || Vector2.DistanceSquared(v.Position, point.Def.Position) > r * r) continue;
                if (v.Team == PlayerTeam) power0 += v.Def.CaptureRate;
                else if (v.Team == EnemyTeam) power1 += v.Def.CaptureRate;
            }

            point.Contested = power0 > 0f && power1 > 0f;
            var before = point.Owner;
            if (!point.Contested && (power0 > 0f || power1 > 0f))
            {
                var push = (power0 - power1) * dt / _rules.CaptureSeconds;
                point.Progress = Math.Clamp(point.Progress + push, -1f, 1f);
            }
            else if (!point.Contested)
            {
                // Unattended points drift back to their owner's full hold (or to neutral).
                var rest = point.Owner == PlayerTeam ? 1f : point.Owner == EnemyTeam ? -1f : 0f;
                point.Progress = SimMath.MoveTowards(point.Progress, rest, dt / (_rules.CaptureSeconds * 3f));
            }

            // Ownership flips only at a full hold; crossing zero neutralises the point first.
            if (point.Progress >= 1f) point.Owner = PlayerTeam;
            else if (point.Progress <= -1f) point.Owner = EnemyTeam;
            else if ((point.Owner == PlayerTeam && point.Progress <= 0f) || (point.Owner == EnemyTeam && point.Progress >= 0f))
                point.Owner = -1;
            if (point.Owner != before) world.Announce(SimEvent.Captured(point.Def.Id, point.Def.Position, point.Owner));
        }
    }
}
