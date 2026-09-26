#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>A mode with capture points the commander AI can fight over.</summary>
    public interface IObjectiveMode
    {
        IReadOnlyList<ObjectiveState> Points { get; }
    }

    /// <summary>
    /// The capture rules every point-based mode shares: vehicles inside the circle push the point
    /// towards their side at their capture rate, both sides present freezes it, an unattended
    /// point drifts back to its owner, and ownership flips only at a full hold.
    /// </summary>
    public static class PointCapture
    {
        public const int TeamA = 0;
        public const int TeamB = 1;

        public static void Tick(SimWorld world, ObjectiveState point, float dt, float captureSeconds)
        {
            var power0 = 0f;
            var power1 = 0f;
            var r = point.Def.Radius;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Flying || Vector2.DistanceSquared(v.Position, point.Def.Position) > r * r) continue;
                if (v.Team == TeamA) power0 += v.Def.CaptureRate;
                else if (v.Team == TeamB) power1 += v.Def.CaptureRate;
            }

            point.Contested = power0 > 0f && power1 > 0f;
            var before = point.Owner;
            if (!point.Contested && (power0 > 0f || power1 > 0f))
            {
                var push = (power0 - power1) * dt / captureSeconds;
                point.Progress = Math.Clamp(point.Progress + push, -1f, 1f);
            }
            else if (!point.Contested)
            {
                // Unattended points drift back to their owner's full hold (or to neutral).
                var rest = point.Owner == TeamA ? 1f : point.Owner == TeamB ? -1f : 0f;
                point.Progress = SimMath.MoveTowards(point.Progress, rest, dt / (captureSeconds * 3f));
            }

            // Ownership flips only at a full hold; crossing zero neutralises the point first.
            if (point.Progress >= 1f) point.Owner = TeamA;
            else if (point.Progress <= -1f) point.Owner = TeamB;
            else if ((point.Owner == TeamA && point.Progress <= 0f) || (point.Owner == TeamB && point.Progress >= 0f))
                point.Owner = -1;
            if (point.Owner != before) world.Announce(SimEvent.Captured(point.Def.Id, point.Def.Position, point.Owner));
        }

        /// <summary>Starts a point fully held by <paramref name="team"/>.</summary>
        public static void Own(ObjectiveState point, int team)
        {
            point.Owner = team;
            point.Progress = team == TeamA ? 1f : team == TeamB ? -1f : 0f;
        }

        public static int Held(IReadOnlyList<ObjectiveState> points, int team)
        {
            var count = 0;
            foreach (var p in points)
                if (p.Owner == team) count++;
            return count;
        }
    }

    /// <summary>
    /// Notices vehicles that are gone since the last look and books them to their side: how many
    /// each side lost and what they cost. Destroyed and removed vehicles count the same.
    /// </summary>
    public sealed class KillLedger
    {
        private readonly Dictionary<EntityId, (int team, int cost)> _alive = new();
        private readonly List<EntityId> _gone = new();
        private readonly HashSet<EntityId> _seen = new();
        private readonly int[] _losses = new int[2];
        private readonly int[] _lostCp = new int[2];

        /// <summary>Called for every loss: its team and CP cost.</summary>
        public event Action<int, int>? Lost;

        public int Losses(int team) => team is 0 or 1 ? _losses[team] : 0;

        public int LostCp(int team) => team is 0 or 1 ? _lostCp[team] : 0;

        /// <summary>Vehicles the other side lost.</summary>
        public int Kills(int team) => Losses(1 - team);

        /// <summary>Vehicles excluded from the count (a scripted convoy, a boss counted on its own).</summary>
        public Func<Vehicle, bool>? Ignore { get; set; }

        public void Update(SimWorld world)
        {
            _seen.Clear();
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team < 0 || v.Team > 1 || (Ignore != null && Ignore(v))) continue;
                _seen.Add(v.Id);
                if (!_alive.ContainsKey(v.Id)) _alive[v.Id] = (v.Team, v.Def.CpCost);
            }
            _gone.Clear();
            foreach (var id in _alive.Keys)
                if (!_seen.Contains(id)) _gone.Add(id);
            foreach (var id in _gone)
            {
                var (team, cost) = _alive[id];
                _losses[team]++;
                _lostCp[team] += cost;
                Lost?.Invoke(team, cost);
                _alive.Remove(id);
            }
        }
    }

    /// <summary>Command Points, deck and income for one side of a mode.</summary>
    public sealed class SideSetup
    {
        public float StartCp { get; set; } = 14f;

        /// <summary>CP per second.</summary>
        public float Income { get; set; } = 1f;

        /// <summary>Most CP the army may field at once.</summary>
        public int ArmyCap { get; set; } = 24;

        public IReadOnlyList<string> Vehicles { get; set; } = Array.Empty<string>();
        public IReadOnlyList<string> Supports { get; set; } = Array.Empty<string>();

        internal Economy.TeamEconomy Build(int team) =>
            new(team, StartCp, income: Income, armyCap: ArmyCap, vehicles: Vehicles, supports: Supports);
    }
}
