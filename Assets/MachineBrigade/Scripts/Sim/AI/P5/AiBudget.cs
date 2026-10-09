#nullable enable
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Numerics;
using System.Text;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>AI MASTER P5 Part P: the systems the timing counters split the AI's cost into.</summary>
    public enum AiPerfSection
    {
        /// <summary>The movement step: steering, ORCA-lite, traffic coordinator, jam stages (10 Hz parts inside).</summary>
        Steering,
        /// <summary>Queued path searches served at the start of a step.</summary>
        PathRebuild,
        /// <summary>TacticalAi (unit layer, its decision interval) plus the watchdog requests it serves.</summary>
        Tactical,
        /// <summary>The squad layer (4 Hz tick, each squad thinks at 2 Hz in staggered buckets).</summary>
        Squad,
        /// <summary>The commander pass (1 Hz, teams half a second apart): P2-P4 planning included.</summary>
        Commander,
        /// <summary>Buying (rebuilds, support cards, procurement director) at the difficulty's interval.</summary>
        Procurement,
        /// <summary>The weapons' step: target search and scoring (P0-A filter, role / mode / P3 / P5 factors) and firing.</summary>
        Targeting,
        /// <summary>The combat activity watchdog (4 Hz looks).</summary>
        Watchdog,
        /// <summary>Boss brains and the rest of the boss system.</summary>
        Bosses,
        /// <summary>The AI Health Monitor (1 Hz).</summary>
        HealthMonitor,
    }

    /// <summary>
    /// AI MASTER P5 Part P: cheap per-system timing counters (Stopwatch ticks). Off by default (one bool test per section when
    /// off); the 48v48 harness and the lead's runs switch them on. Readings never feed a decision, so they cannot change a battle.
    /// </summary>
    public sealed class AiPerfCounters
    {
        public static readonly int Count = Enum.GetValues(typeof(AiPerfSection)).Length;

        private readonly double[] _ms = new double[Count];
        private readonly double[] _max = new double[Count];
        private readonly long[] _calls = new long[Count];

        public bool Enabled { get; set; } = Tun.Budget.PerfCounters;

        /// <summary>World steps counted while enabled (the per-step means divide by it).</summary>
        public long Steps { get; internal set; }

        /// <summary>A start stamp (0 when off: <see cref="End"/> then does nothing).</summary>
        public long Begin() => Enabled ? Stopwatch.GetTimestamp() : 0L;

        public void End(AiPerfSection section, long start)
        {
            if (start == 0L) return;
            var ms = (Stopwatch.GetTimestamp() - start) * 1000.0 / Stopwatch.Frequency;
            var i = (int)section;
            _ms[i] += ms;
            _calls[i]++;
            if (ms > _max[i]) _max[i] = ms;
        }

        public double TotalMs(AiPerfSection s) => _ms[(int)s];
        public double MaxMs(AiPerfSection s) => _max[(int)s];
        public long Calls(AiPerfSection s) => _calls[(int)s];

        /// <summary>Milliseconds per world step on average (0 before any step).</summary>
        public double PerStepMs(AiPerfSection s) => Steps > 0 ? _ms[(int)s] / Steps : 0.0;

        /// <summary>Every AI section's milliseconds per step together.</summary>
        public double TotalPerStepMs()
        {
            var t = 0.0;
            for (var i = 0; i < Count; i++) t += _ms[i];
            return Steps > 0 ? t / Steps : 0.0;
        }

        public void Reset()
        {
            Array.Clear(_ms, 0, Count);
            Array.Clear(_max, 0, Count);
            Array.Clear(_calls, 0, Count);
            Steps = 0;
        }

        /// <summary>One line per section: ms / step, worst call, calls (the lead's report reads it).</summary>
        public string Report()
        {
            var sb = new StringBuilder();
            sb.Append($"AI per-system cost over {Steps} steps (ms/step, max ms, calls); total {TotalPerStepMs():0.000} ms/step\n");
            for (var i = 0; i < Count; i++)
                sb.Append($"  {(AiPerfSection)i,-14} {(Steps > 0 ? _ms[i] / Steps : 0.0),8:0.000} {_max[i],8:0.000} {_calls[i],8}\n");
            return sb.ToString();
        }
    }

    /// <summary>
    /// AI MASTER P5 Part P / section 3: deterministic staggering. A subject (squad, unit) with a stable id runs on the ticks of its
    /// bucket only, so the work of one rate spreads over the frames instead of landing on one. Pure (the tests call it).
    /// </summary>
    public static class AiCadence
    {
        /// <summary>Whether <paramref name="subject"/> is due on layer tick <paramref name="layerTick"/> with <paramref name="buckets"/> buckets.</summary>
        public static bool Due(int subject, long layerTick, int buckets)
        {
            if (buckets <= 1) return true;
            var b = (int)(((uint)subject * 2654435761u) % (uint)buckets);
            return layerTick % buckets == b;
        }

        /// <summary>The rate a subject actually runs at: the layer's rate over the buckets.</summary>
        public static float RateHz(float layerHz, int buckets) => buckets <= 1 ? layerHz : layerHz / buckets;
    }

    /// <summary>
    /// AI MASTER P5 section 98: a uniform grid over the living vehicles (cell 8-12 m, <c>ai.budget.spatialCell</c>), rebuilt at most
    /// once a step on first use; buckets keep the vehicle-list order, so a query visits vehicles in a stable order (determinism).
    /// For bounded neighbour counts (clusters, crowds) instead of scanning every vehicle.
    /// </summary>
    public sealed class AiSpatialIndex
    {
        private readonly SimWorld _world;
        private readonly Dictionary<long, List<Vehicle>> _cells = new();
        private readonly Stack<List<Vehicle>> _spare = new();
        private long _builtTick = -1;
        private float _cell = 10f;

        internal AiSpatialIndex(SimWorld world) => _world = world;

        /// <summary>The vehicles moved (after the movement step): the next query rebuilds the grid.</summary>
        internal void Invalidate() => _builtTick = -1;

        /// <summary>Rebuilds the grid when the step changed since the last build.</summary>
        private void Ensure()
        {
            if (_builtTick == _world.Tick) return;
            _builtTick = _world.Tick;
            _cell = Math.Clamp(Tun.Budget.SpatialCell, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiSpatialIndex.EnsureSpatialCellMin, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiSpatialIndex.EnsureSpatialCellMax);
            foreach (var list in _cells.Values)
            {
                list.Clear();
                _spare.Push(list);
            }
            _cells.Clear();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                var key = Key(v.Position);
                if (!_cells.TryGetValue(key, out var list)) _cells[key] = list = _spare.Count > 0 ? _spare.Pop() : new List<Vehicle>();
                list.Add(v);
            }
        }

        private long Key(Vector2 p) => Key((int)MathF.Floor(p.X / _cell), (int)MathF.Floor(p.Y / _cell));

        private static long Key(int x, int y) => ((long)x << 32) ^ (uint)y;

        /// <summary>
        /// Counts living vehicles within <paramref name="radius"/> of <paramref name="at"/> that pass <paramref name="match"/>, up to
        /// <paramref name="limit"/> (stops early).
        /// </summary>
        public int Count(Vector2 at, float radius, Func<Vehicle, bool> match, int limit = int.MaxValue)
        {
            Ensure();
            var r2 = radius * radius;
            int x0 = (int)MathF.Floor((at.X - radius) / _cell), x1 = (int)MathF.Floor((at.X + radius) / _cell);
            int y0 = (int)MathF.Floor((at.Y - radius) / _cell), y1 = (int)MathF.Floor((at.Y + radius) / _cell);
            var n = 0;
            for (var x = x0; x <= x1; x++)
                for (var y = y0; y <= y1; y++)
                {
                    if (!_cells.TryGetValue(Key(x, y), out var list)) continue;
                    foreach (var v in list)
                    {
                        if (Vector2.DistanceSquared(v.Position, at) > r2 || !match(v)) continue;
                        if (++n >= limit) return n;
                    }
                }
            return n;
        }

        /// <summary>
        /// Living vehicles of <paramref name="e"/>'s side and layer (ground / air) within <paramref name="radius"/> of it, itself left
        /// out, up to <paramref name="limit"/>: the cluster / crowd counts of the role ladders and tower modes.
        /// </summary>
        public int CountSameSide(Vehicle e, float radius, int limit = int.MaxValue)
        {
            Ensure();
            var at = e.Position;
            var r2 = radius * radius;
            int x0 = (int)MathF.Floor((at.X - radius) / _cell), x1 = (int)MathF.Floor((at.X + radius) / _cell);
            int y0 = (int)MathF.Floor((at.Y - radius) / _cell), y1 = (int)MathF.Floor((at.Y + radius) / _cell);
            var n = 0;
            for (var x = x0; x <= x1; x++)
                for (var y = y0; y <= y1; y++)
                {
                    if (!_cells.TryGetValue(Key(x, y), out var list)) continue;
                    foreach (var o in list)
                    {
                        if (o == e || !o.IsAlive || o.Team != e.Team || o.Flying != e.Flying || Vector2.DistanceSquared(o.Position, at) > r2) continue;
                        if (++n >= limit) return n;
                    }
                }
            return n;
        }

        /// <summary>Adds the living vehicles within <paramref name="radius"/> to <paramref name="into"/>, sorted by id (stable).</summary>
        public void Near(Vector2 at, float radius, List<Vehicle> into)
        {
            Ensure();
            into.Clear();
            var r2 = radius * radius;
            int x0 = (int)MathF.Floor((at.X - radius) / _cell), x1 = (int)MathF.Floor((at.X + radius) / _cell);
            int y0 = (int)MathF.Floor((at.Y - radius) / _cell), y1 = (int)MathF.Floor((at.Y + radius) / _cell);
            for (var x = x0; x <= x1; x++)
                for (var y = y0; y <= y1; y++)
                    if (_cells.TryGetValue(Key(x, y), out var list))
                        foreach (var v in list)
                            if (Vector2.DistanceSquared(v.Position, at) <= r2) into.Add(v);
            into.Sort((a, b) => a.Id.Value.CompareTo(b.Id.Value));
        }
    }
}
