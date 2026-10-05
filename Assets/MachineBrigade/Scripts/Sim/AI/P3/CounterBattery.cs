#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Spec 144: where enemy guns are thought to be: estimated origin, confidence, error radius, timestamp.</summary>
    public sealed class OriginEstimate
    {
        internal OriginEstimate(Vector2 centre, float error, double at)
        {
            Centre = centre;
            ErrorRadius = error;
            LastAt = at;
            Shots = 1;
        }

        public Vector2 Centre { get; internal set; }
        public float ErrorRadius { get; internal set; }
        public double LastAt { get; internal set; }
        public int Shots { get; internal set; }

        /// <summary>When the side last area-fired at it (no repeat barrage within the stale time).</summary>
        public double StruckAt { get; internal set; } = double.NegativeInfinity;

        /// <summary>1 - exp(-shots / 2), fading with <see cref="Tun.FireMissions.HalfLifeS"/> since the last shot seen.</summary>
        public float Confidence(double now) =>
            (1f - MathF.Exp(-Shots / 2f)) * MathF.Pow(0.5f, (float)(Math.Max(0.0, now - LastAt) / MathF.Max(0.1f, Tun.FireMissions.HalfLifeS)));

        public override string ToString() => $"origin ({Centre.X:0},{Centre.Y:0}) +-{ErrorRadius:0} m, {Shots} shots";
    }

    /// <summary>
    /// AI MASTER P3 spec 143-145, 213: the side's counter-battery picture. Each enemy shell the side saw land gives an origin
    /// estimate whose error is a share of the shell's flight (at least <see cref="Tun.FireMissions.MinError"/>), offset by a
    /// deterministic hash of the shot (no perfect origin, no reveal). Estimates within the merge radius are one battery: the
    /// centre averages by precision, the error shrinks with the square root of the shots, confidence grows with them. The
    /// impacts themselves are kept a few seconds for shoot-and-scoot threat and anti-artillery dispersion timing.
    /// </summary>
    public sealed class CounterBatteryTracker
    {
        private const int MaxEstimates = 16;
        private const int MaxImpacts = 64;
        private readonly List<OriginEstimate> _estimates = new();
        private readonly List<(Vector2 at, double time)> _impacts = new();

        public IReadOnlyList<OriginEstimate> Estimates => _estimates;

        /// <summary>Records an observed impact (spec 145 / 213).</summary>
        public void Impact(Vector2 at, double time)
        {
            if (_impacts.Count >= MaxImpacts) _impacts.RemoveAt(0);
            _impacts.Add((at, time));
        }

        /// <summary>An observed enemy impact within <paramref name="radius"/> of <paramref name="p"/> in the last <paramref name="window"/> seconds.</summary>
        public bool RecentImpactNear(Vector2 p, float radius, double now, float window)
        {
            for (var i = _impacts.Count - 1; i >= 0; i--)
            {
                var (at, time) = _impacts[i];
                if (now - time > window) break;
                if (Vector2.DistanceSquared(at, p) <= radius * radius) return true;
            }
            return false;
        }

        /// <summary>
        /// One observed shell: <paramref name="origin"/> is where it truly came from, used only through the error model
        /// (the estimate is off by up to the error radius, deterministic in <paramref name="key"/>).
        /// </summary>
        public OriginEstimate Observe(Vector2 origin, Vector2 impact, int key, double now)
        {
            var flight = Vector2.Distance(origin, impact);
            var error = MathF.Max(Tun.FireMissions.MinError, flight * Tun.FireMissions.ErrorShare);
            var h = (uint)key * 2654435761u;
            var angle = (h % 3600u) / 3600f * MathF.PI * 2f;
            var radius = ((h >> 12) % 1000u) / 1000f * error;
            var seen = origin + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * radius;
            OriginEstimate? best = null;
            var bestD = float.MaxValue;
            foreach (var e in _estimates)
            {
                var d = Vector2.Distance(e.Centre, seen);
                // Two estimates of one battery can each be off by a single shot's error: their circles overlap (plus the merge radius).
                if (d <= Tun.FireMissions.MergeRadius + 2f * MathF.Max(e.ErrorRadius, error) && d < bestD)
                {
                    best = e;
                    bestD = d;
                }
            }
            if (best == null)
            {
                if (_estimates.Count >= MaxEstimates) _estimates.RemoveAt(0);
                best = new OriginEstimate(seen, error, now);
                _estimates.Add(best);
                return best;
            }
            // Precision-weighted mean; the error shrinks with the shots (never under the minimum).
            var wOld = best.Shots / MathF.Max(1f, best.ErrorRadius * best.ErrorRadius);
            var wNew = 1f / (error * error);
            best.Centre = (best.Centre * wOld + seen * wNew) / (wOld + wNew);
            best.Shots++;
            best.ErrorRadius = MathF.Max(Tun.FireMissions.MinError, error / MathF.Sqrt(best.Shots));
            best.LastAt = now;
            return best;
        }

        /// <summary>The most confident estimate at or over <paramref name="minConfidence"/> (null: none).</summary>
        public OriginEstimate? Best(double now, float minConfidence)
        {
            OriginEstimate? best = null;
            var conf = minConfidence;
            foreach (var e in _estimates)
            {
                var c = e.Confidence(now);
                if (c >= conf)
                {
                    best = e;
                    conf = c;
                }
            }
            return best;
        }

        internal void Prune(double now)
        {
            _estimates.RemoveAll(e => e.Confidence(now) < 0.05f);
            while (_impacts.Count > 0 && now - _impacts[0].time > 60.0) _impacts.RemoveAt(0);
        }
    }

    /// <summary>Spec 127: which corridor each squad is using (friendly route occupancy).</summary>
    public sealed class RouteBook
    {
        private readonly Dictionary<int, (Vector2 mid, double until)> _book = new();

        public void Book(int squad, Vector2 mid, double now) => _book[squad] = (mid, now + Tun.Routes.BookSeconds);

        public void Unbook(int squad) => _book.Remove(squad);

        /// <summary>Other squads whose route middle is within the occupancy radius of <paramref name="mid"/>.</summary>
        public int Occupancy(Vector2 mid, int exceptSquad, double now)
        {
            var n = 0;
            var r = Tun.Routes.OccupancyRadius;
            foreach (var kv in _book)
                if (kv.Key != exceptSquad && kv.Value.until > now && Vector2.DistanceSquared(kv.Value.mid, mid) <= r * r) n++;
            return n;
        }

        internal void Prune(double now)
        {
            if (_book.Count < 64) return;
            var old = new List<int>();
            foreach (var kv in _book)
                if (kv.Value.until <= now) old.Add(kv.Key);
            foreach (var k in old) _book.Remove(k);
        }
    }
}
