#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P3, one side's tactical memory (fog-fair: built from its own sight, contacts and losses only):
    /// <list type="bullet">
    /// <item>spec 128 temporal influence: a contact's threat stays painted on its cell after it leaves sight and fades with a
    /// half-life by kind (mobile 10 s, suspected artillery 20 s, static 45 s); a cell seen empty decays fast (ConfirmedAbsent);</item>
    /// <item>spec 129 recent-death danger: each own loss is StrategicValue x exp-decay (half-life 18 s) within 20 m; it raises
    /// scout demand and route cost, never a morale or panic state;</item>
    /// <item>spec 130 Unknown != Safe: ground not seen for a while carries an uncertainty cost (tactic modifier);</item>
    /// <item>spec 127 failed routes: a route that just cost a squad dearly costs more for a while (repeat penalty, half-life 45 s);</item>
    /// <item>spec 212 observed enemy losses (counterattack windows).</item>
    /// </list>
    /// Values decay when read (no per-step loops); the cell grid is the side's <see cref="TeamIntel"/> grid.
    /// </summary>
    public sealed class TacticalMemory
    {
        private const int MaxMarks = 64;
        private float[] _threat = Array.Empty<float>();
        private double[] _threatAt = Array.Empty<double>();
        private float[] _threatHalf = Array.Empty<float>();
        private bool[] _stamped = Array.Empty<bool>();
        private TeamIntel? _intel;
        private readonly List<Mark> _deaths = new();
        private readonly List<Mark> _enemyLosses = new();
        private readonly Dictionary<long, (float penalty, double at)> _failed = new();

        public readonly struct Mark
        {
            public Mark(Vector2 at, float value, double time)
            {
                At = at;
                Value = value;
                Time = time;
            }

            public Vector2 At { get; }
            public float Value { get; }
            public double Time { get; }
        }

        public IReadOnlyList<Mark> Deaths => _deaths;
        public IReadOnlyList<Mark> EnemyLosses => _enemyLosses;

        private static float Decay(double age, float halfLife) => age <= 0 ? 1f : MathF.Pow(0.5f, (float)(age / MathF.Max(0.1f, halfLife)));

        // ------------------------------------------------------------------------------------------------ spec 128

        internal void Refresh(SimWorld world, TeamIntel intel, double now)
        {
            _intel = intel;
            var n = intel.Columns * intel.Rows;
            if (_threat.Length != n)
            {
                _threat = new float[n];
                _threatAt = new double[n];
                _threatHalf = new float[n];
                _stamped = new bool[n];
            }
            Array.Clear(_stamped, 0, n);
            foreach (var c in intel.Contacts)
            {
                if (!c.InSight || c.Displaced) continue;
                var i = intel.CellIndex(c.Position);
                var half = c.Artillery ? Tun.Memory.ArtilleryHalfLifeS
                    : world.Catalog.Vehicles.TryGetValue(c.Unit, out var def) && def.Static ? Tun.Memory.StaticHalfLifeS
                    : Tun.Memory.MobileHalfLifeS;
                var value = _stamped[i] ? _threat[i] + c.Strength : c.Strength;
                if (_stamped[i] || value >= ThreatCell(i, now))
                {
                    _threat[i] = value;
                    _threatAt[i] = now;
                    _threatHalf[i] = _stamped[i] ? MathF.Max(_threatHalf[i], half) : half;
                }
                _stamped[i] = true;
            }
            // ConfirmedAbsent: a remembered cell seen this refresh with nothing in it fades fast.
            for (var i = 0; i < n; i++)
            {
                if (_stamped[i] || _threat[i] <= 0f || intel.Seen[i] < intel.UpdatedAt) continue;
                _threat[i] = ThreatCell(i, now) * Tun.Memory.AbsentDecay;
                _threatAt[i] = now;
                if (_threat[i] < 0.05f) _threat[i] = 0f;
            }
        }

        private float ThreatCell(int i, double now) => _threat[i] <= 0f ? 0f : _threat[i] * Decay(now - _threatAt[i], _threatHalf[i]);

        /// <summary>Spec 128: the remembered enemy strength on the cell of <paramref name="p"/> now.</summary>
        public float ThreatMemory(Vector2 p, double now) => _intel == null || _threat.Length == 0 ? 0f : ThreatCell(_intel.CellIndex(p), now);

        // ------------------------------------------------------------------------------------------------ spec 129

        /// <summary>A friendly death of <paramref name="value"/> (CP-like strategic value) at <paramref name="at"/>.</summary>
        public void AddDeath(Vector2 at, float value, double now) => Add(_deaths, new Mark(at, value, now));

        /// <summary>An enemy loss the side saw (spec 212).</summary>
        public void AddEnemyLoss(Vector2 at, float value, double now) => Add(_enemyLosses, new Mark(at, value, now));

        private static void Add(List<Mark> list, Mark m)
        {
            if (list.Count >= MaxMarks) list.RemoveAt(0);
            list.Add(m);
        }

        /// <summary>
        /// Spec 129: DeathInfluence = sum of StrategicValue x exp-decay within the death radius (linear fall-off), in units of a
        /// 10 CP vehicle (1 = one such vehicle lost there just now).
        /// </summary>
        public float DeathDanger(Vector2 p, double now)
        {
            var r = MathF.Max(1f, Tun.Memory.DeathRadius);
            var sum = 0f;
            foreach (var d in _deaths)
            {
                var dist = Vector2.Distance(d.At, p);
                if (dist > r) continue;
                sum += d.Value / 10f * Decay(now - d.Time, Tun.Memory.DeathHalfLifeS) * (1f - 0.5f * dist / r);
            }
            return sum;
        }

        /// <summary>The highest death danger along a straight way (sampled every half death radius).</summary>
        public float DeathAlong(Vector2 from, Vector2 to, double now)
        {
            if (_deaths.Count == 0) return 0f;
            var step = MathF.Max(2f, Tun.Memory.DeathRadius * 0.5f);
            var n = Math.Max(1, (int)(Vector2.Distance(from, to) / step));
            var max = 0f;
            for (var i = 0; i <= n; i++) max = MathF.Max(max, DeathDanger(Vector2.Lerp(from, to, i / (float)n), now));
            return max;
        }

        /// <summary>Losses (decayed with <paramref name="halfLife"/>) within <paramref name="radius"/>: spec 172's ledger.</summary>
        public float LossesNear(Vector2 p, float radius, float halfLife, double now)
        {
            var sum = 0f;
            foreach (var d in _deaths)
                if (Vector2.Distance(d.At, p) <= radius) sum += d.Value * Decay(now - d.Time, halfLife);
            return sum;
        }

        // ------------------------------------------------------------------------------------------------ spec 130

        /// <summary>Spec 130: the share of cells within <paramref name="radius"/> not seen for <see cref="Tun.Memory.UnknownSeconds"/> (and with no remembered threat).</summary>
        public float UnknownShare(TeamIntel intel, Vector2 p, float radius, double now)
        {
            int all = 0, unknown = 0;
            var cell = intel.Cell;
            var steps = Math.Max(0, (int)(radius / cell));
            for (var dy = -steps; dy <= steps; dy++)
            for (var dx = -steps; dx <= steps; dx++)
            {
                var q = p + new Vector2(dx, dy) * cell;
                if (Vector2.DistanceSquared(q, p) > radius * radius + 1f) continue;
                all++;
                var i = intel.CellIndex(q);
                if (now - intel.Seen[i] > Tun.Memory.UnknownSeconds && intel.Threat[(int)ThreatKind.AntiTank][i] <= 0f) unknown++;
            }
            return all == 0 ? 0f : unknown / (float)all;
        }

        /// <summary>Spec 130 along a way: the share of sampled cells that are Unknown.</summary>
        public float UnknownAlong(TeamIntel intel, Vector2 from, Vector2 to, double now)
        {
            var n = Math.Max(1, (int)(Vector2.Distance(from, to) / intel.Cell));
            var unknown = 0;
            for (var i = 1; i <= n; i++)
                if (now - intel.Seen[intel.CellIndex(Vector2.Lerp(from, to, i / (float)n))] > Tun.Memory.UnknownSeconds) unknown++;
            return unknown / (float)n;
        }

        /// <summary>Spec 130: the tactic's modifier (blitz low, balanced middle, attrition / recon / ambush high).</summary>
        public static float UnknownModifier(Content.TacticModules m)
        {
            var k = Tun.Memory.UnknownRisk;
            if (k.Length < 4) return 0.6f;
            if (m.Stance == Content.FireStance.HoldFire) return k[3];
            if (m.Pace >= 1.2f) return k[0];
            if (m.Standoff || m.Bounding) return k[2];
            return k[1];
        }

        // ------------------------------------------------------------------------------------------------ spec 127

        /// <summary>A route key: the route's middle on a 20 m lattice and its side.</summary>
        public static long RouteKey(Vector2 mid, int side) => ((long)MathF.Floor(mid.X / 20f) * 100003L + (long)MathF.Floor(mid.Y / 20f)) * 4L + (side + 1);

        /// <summary>Marks a route failed: its repeat penalty rises (capped at 1) and decays with the half-life.</summary>
        public void Fail(long key, double now) => _failed[key] = (MathF.Min(1f, RoutePenalty(key, now) + Tun.Memory.RepeatPlanPenalty), now);

        /// <summary>Spec 127 / 218: the repeat penalty of a route now (0: none).</summary>
        public float RoutePenalty(long key, double now) =>
            _failed.TryGetValue(key, out var f) ? f.penalty * Decay(now - f.at, Tun.Memory.RepeatPlanHalfLifeS) : 0f;

        internal void PruneRoutes(double now)
        {
            if (_failed.Count < 64) return;
            var old = new List<long>();
            foreach (var kv in _failed)
                if (RoutePenalty(kv.Key, now) < 0.02f) old.Add(kv.Key);
            foreach (var k in old) _failed.Remove(k);
        }
    }
}
