#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Spec 124: one stretch of the front.</summary>
    public readonly struct FrontSegment
    {
        public FrontSegment(Vector2 centre, Vector2 normal, float friendlyPressure, float enemyPressure, float stability, float width, float confidence)
        {
            Centre = centre;
            Normal = normal;
            FriendlyPressure = friendlyPressure;
            EnemyPressure = enemyPressure;
            Stability = stability;
            Width = width;
            Confidence = confidence;
        }

        public Vector2 Centre { get; }

        /// <summary>Unit vector from the own side towards the enemy's.</summary>
        public Vector2 Normal { get; }
        public float FriendlyPressure { get; }
        public float EnemyPressure { get; }

        /// <summary>0-1: how long this stretch has stood where it is (10 s = 1).</summary>
        public float Stability { get; }

        /// <summary>Usable width (m), narrowed by a choke on it.</summary>
        public float Width { get; }

        /// <summary>0-1: how sure the side is of the enemy behind it (contact confidence; 0.3 for a provisional front).</summary>
        public float Confidence { get; }

        public override string ToString() => $"front ({Centre.X:0},{Centre.Y:0}) F{FriendlyPressure:0.#}/E{EnemyPressure:0.#} w{Width:0} s{Stability:0.00} c{Confidence:0.00}";
    }

    /// <summary>
    /// AI MASTER P3 spec 124: the tactical frontline of one side, from its World Model's estimated front cells (own blurred
    /// strength next to the enemy's), its remembered threat (spec 128: recent combat), the objective and the chokes. Never
    /// from hidden enemies. Segments are the connected runs of front cells; with none, a provisional segment between the own
    /// centre and the objective (confidence 0.3). Tells front / flank / rear (<see cref="Depth"/>), where the line is about to
    /// break (<see cref="Weakest"/>), and the positional advantage of an approach (<see cref="PositionalAdvantage"/>).
    /// </summary>
    public sealed class FrontlineModel
    {
        private readonly List<FrontSegment> _segments = new();
        private readonly List<FrontSegment> _previous = new();
        private readonly List<double> _since = new();
        private readonly List<double> _previousSince = new();

        public IReadOnlyList<FrontSegment> Segments => _segments;

        internal void Rebuild(SimWorld world, TeamIntel intel, TacticalMemory memory, Vector2? objective, double now)
        {
            _previous.Clear();
            _previous.AddRange(_segments);
            _previousSince.Clear();
            _previousSince.AddRange(_since);
            _segments.Clear();
            _since.Clear();
            var front = intel.Front;
            var cell = intel.Cell;
            var n = intel.Columns * intel.Rows;
            if (front.Count > 0)
            {
                var inFront = new bool[n];
                foreach (var i in front) inFront[i] = true;
                var used = new bool[n];
                var queue = new List<int>();
                foreach (var start in front)
                {
                    if (used[start]) continue;
                    queue.Clear();
                    queue.Add(start);
                    used[start] = true;
                    for (var q = 0; q < queue.Count; q++)
                    {
                        int c = queue[q], x = c % intel.Columns, y = c / intel.Columns;
                        for (var dy = -1; dy <= 1; dy++)
                        for (var dx = -1; dx <= 1; dx++)
                        {
                            int nx = x + dx, ny = y + dy;
                            if (nx < 0 || ny < 0 || nx >= intel.Columns || ny >= intel.Rows) continue;
                            var j = ny * intel.Columns + nx;
                            if (!inFront[j] || used[j]) continue;
                            used[j] = true;
                            queue.Add(j);
                        }
                    }
                    AddSegment(world, intel, memory, queue, cell, now);
                }
            }
            else if (objective is { } goal && OwnCentre(world, intel.Team) is { } own && intel.EnemyTotal > 0f)
            {
                var normal = Dir(own, goal);
                var centre = Vector2.Lerp(own, goal, 0.6f);
                var (f, e) = intel.StrengthAround(centre, cell * 3f);
                AddFinal(centre, normal, f, e, 60f, 0.3f, now);
            }
        }

        private void AddSegment(SimWorld world, TeamIntel intel, TacticalMemory memory, List<int> cells, float cell, double now)
        {
            var centre = Vector2.Zero;
            foreach (var c in cells) centre += intel.CellCentre(c);
            centre /= cells.Count;
            var radius = cell * 3f;
            // Own and enemy weight round it give the normal (own -> enemy); remembered threat counts for the enemy (recent combat).
            Vector2 ownSum = Vector2.Zero, enemySum = Vector2.Zero;
            float own = 0f, enemy = 0f;
            var steps = 3;
            var cx = intel.CellIndex(centre);
            int x0 = cx % intel.Columns, y0 = cx / intel.Columns;
            for (var dy = -steps; dy <= steps; dy++)
            for (var dx = -steps; dx <= steps; dx++)
            {
                int x = x0 + dx, y = y0 + dy;
                if (x < 0 || y < 0 || x >= intel.Columns || y >= intel.Rows) continue;
                var i = y * intel.Columns + x;
                var p = intel.CellCentre(i);
                var e = MathF.Max(intel.Enemy[i], 0.5f * memory.ThreatMemory(p, now));
                ownSum += p * intel.Own[i];
                enemySum += p * e;
                own += intel.Own[i];
                enemy += e;
            }
            var normal = own > 0f && enemy > 0f ? Dir(ownSum / own, enemySum / enemy) : Vector2.UnitY;
            var tangent = new Vector2(-normal.Y, normal.X);
            float lo = float.MaxValue, hi = float.MinValue;
            foreach (var c in cells)
            {
                var t = Vector2.Dot(intel.CellCentre(c) - centre, tangent);
                lo = MathF.Min(lo, t);
                hi = MathF.Max(hi, t);
            }
            var width = hi - lo + cell;
            // A choke on the segment narrows what can actually fight there (spec 126).
            foreach (var ch in world.Topology.Chokes)
                if (Vector2.Distance(ch.Centre, centre) <= radius) width = MathF.Min(width, MathF.Max(ch.Width, 4f));
            // Confidence: the contacts behind it.
            float sum = 0f, w = 0f;
            foreach (var c in intel.Contacts)
            {
                if (Vector2.Distance(c.Position, centre) > radius * 1.5f) continue;
                sum += c.Confidence(world.Time, intel.ConfidenceDecay) * MathF.Max(0.1f, c.Strength);
                w += MathF.Max(0.1f, c.Strength);
            }
            AddFinal(centre, normal, own, enemy, width, w > 0f ? sum / w : 0.4f, now);
        }

        private void AddFinal(Vector2 centre, Vector2 normal, float own, float enemy, float width, float confidence, double now)
        {
            var since = now;
            for (var i = 0; i < _previous.Count; i++)
                if (Vector2.Distance(_previous[i].Centre, centre) < 12f) since = Math.Min(since, _previousSince[i]);
            _segments.Add(new FrontSegment(centre, normal, own, enemy, (float)Math.Clamp((now - since) / 10.0, 0.0, 1.0), width, confidence));
            _since.Add(since);
        }

        /// <summary>The segment nearest <paramref name="p"/> (-1: none).</summary>
        public int Nearest(Vector2 p)
        {
            var best = -1;
            var bestD = float.MaxValue;
            for (var i = 0; i < _segments.Count; i++)
            {
                var d = Vector2.DistanceSquared(_segments[i].Centre, p);
                if (d < bestD)
                {
                    bestD = d;
                    best = i;
                }
            }
            return best;
        }

        /// <summary>Signed depth of <paramref name="p"/> past the nearest segment (positive: the enemy side). 0 with no front.</summary>
        public float Depth(Vector2 p)
        {
            var i = Nearest(p);
            return i < 0 ? 0f : Vector2.Dot(p - _segments[i].Centre, _segments[i].Normal);
        }

        /// <summary>Behind the front by at least <paramref name="margin"/> (always true with no front known).</summary>
        public bool Behind(Vector2 p, float margin) => _segments.Count == 0 || Depth(p) <= -margin;

        /// <summary>The segment where the enemy presses hardest against own strength (-1: none with enemy pressure).</summary>
        public int Weakest()
        {
            var best = -1;
            var bestRatio = 0f;
            for (var i = 0; i < _segments.Count; i++)
            {
                var s = _segments[i];
                if (s.EnemyPressure <= 0f) continue;
                var ratio = s.EnemyPressure / MathF.Max(0.1f, s.FriendlyPressure);
                if (ratio > bestRatio)
                {
                    bestRatio = ratio;
                    best = i;
                }
            }
            return best;
        }

        /// <summary>
        /// Spec 125 / 219 PositionalAdvantage, 0-1, of attacking <paramref name="target"/> from <paramref name="from"/>: straight
        /// into the front's normal 0.3, from the side 0.8, from behind 1; 0.5 with no front.
        /// </summary>
        public float PositionalAdvantage(Vector2 from, Vector2 target)
        {
            var i = Nearest(target);
            if (i < 0) return 0.5f;
            var approach = Dir(from, target);
            var dot = Vector2.Dot(approach, _segments[i].Normal); // 1: frontal (own -> enemy), -1: from the enemy's rear
            return dot >= 0.7f ? 0.3f : dot >= -0.3f ? 0.8f : 1f;
        }

        private static Vector2? OwnCentre(SimWorld world, int team)
        {
            var sum = Vector2.Zero;
            var n = 0;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == team && !v.Def.Static && !v.Flying)
                {
                    sum += v.Position;
                    n++;
                }
            return n > 0 ? sum / n : (Vector2?)null;
        }

        internal static Vector2 Dir(Vector2 from, Vector2 to)
        {
            var d = to - from;
            return d.LengthSquared() > 0.01f ? Vector2.Normalize(d) : Vector2.UnitY;
        }
    }
}
