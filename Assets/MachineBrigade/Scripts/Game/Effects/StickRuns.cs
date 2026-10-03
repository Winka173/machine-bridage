using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// The bomb-run fix, pass 3 (DECISIONS "Ném bom rải thảm"): the sticks being laid, as the view sees them from the fired
    /// events alone (the Sim's stick state is its own). A stick's first bomb fixes its line: where that bomb lands and the
    /// way the stick runs (a free-falling bomber's heading; a boss bay's from its first bomb to its aim, the stick being laid
    /// round the aim); every later bomb of the mount is put on its section of that line (the nearest free one). Each
    /// section is due when its bomb lands (its release plus its fall); a section whose bomb never comes (dropped for a
    /// friend's safety, or the stick cut to a few bombs on few targets) is let go a little after its bomb should have left.
    /// Times are on the owning director's shot clock, as the rounds they warn of. Pure: no scene objects (tests).
    /// </summary>
    internal sealed class StickRuns
    {
        /// <summary>Sticks tracked at once at most (the oldest gives way).</summary>
        internal const int Most = 16;

        internal sealed class Run
        {
            /// <summary>The shooter and mount (EffectsDirector's owner key).</summary>
            public long Owner;

            /// <summary>The round's id and its stick.</summary>
            public string Weapon;
            public StickDef Stick;

            /// <summary>Where bomb 0 lands (on the ground) and the way the stick runs (unit, flat).</summary>
            public Vector3 Start, Dir;

            /// <summary>Bombs the stick may drop (its data count), the blast's core and edge radii (m).</summary>
            public int Bombs;
            public float Core, Edge;

            /// <summary>Bomb 0's release on the shot clock, and its fall (s).</summary>
            public float First, Travel;

            /// <summary>When each section's bomb lands (shot clock), and whether its bomb has been seen.</summary>
            public float[] Due;
            public bool[] Fired;

            /// <summary>The stick shows its warning rectangle; a super weapon's (always shown, on top).</summary>
            public bool Warn, Super;

            /// <summary>Bombs seen so far.</summary>
            public int Seen;

            /// <summary>
            /// The view's own: where the drawn rectangle's front edge is along the stick (m from bomb 0; NaN: not drawn yet) and
            /// when it was last moved (shot clock), so it glides on to the next section as a bomb lands instead of jumping.
            /// </summary>
            public float ShownFrom = float.NaN, ShownAt;

            public bool Live(float now)
            {
                for (var i = 0; i < Due.Length; i++)
                    if (Due[i] > now) return true;
                return false;
            }

            /// <summary>When bomb <paramref name="i"/> should leave (shot clock).</summary>
            public float ReleaseOf(int i) => First + i * Stick.Interval;
        }

        private readonly List<Run> _runs = new();

        internal IReadOnlyList<Run> Runs => _runs;

        /// <summary>The owning director's shot clock (none: the times given are used as they are).</summary>
        internal ShotClock Clock { get; set; }

        /// <summary>Seconds a run is kept after its last section is due.</summary>
        internal const float KeepAfter = 1f;

        /// <summary>How long after its release time a bomb not seen is given up (s).</summary>
        internal static float Grace(StickDef stick) => Mathf.Max(0.35f, 0.75f * stick.Interval);

        /// <summary>
        /// A bomb of <paramref name="round"/>'s stick released by <paramref name="owner"/> at <paramref name="now"/> (render
        /// clock), landing on <paramref name="bomb"/> after <paramref name="travel"/> s; <paramref name="way"/> is the way a new
        /// stick runs. The run it belongs to (a new one for a stick's first bomb) and its section.
        /// </summary>
        public Run Fired(long owner, WeaponDef round, Vector3 bomb, Vector3 way, float now, float travel, bool warn, bool super,
            out int index)
        {
            var stick = round.Stick;
            now = ShotClock.Map(Clock, now);
            travel = Mathf.Max(0.05f, travel);
            bomb.y = 0f;
            var run = Continuing(owner, round, bomb, now, out index);
            if (run == null)
            {
                run = Fresh();
                way.y = 0f;
                run.Owner = owner;
                run.Weapon = round.Id;
                run.Stick = stick;
                run.Start = bomb;
                run.Dir = way.sqrMagnitude > 1e-6f ? way.normalized : Vector3.forward;
                run.Bombs = Mathf.Max(1, stick.Bombs);
                run.Core = Mathf.Max(0.5f, round.SplashRadius);
                run.Edge = Mathf.Max(run.Core, round.WarnRadius);
                run.First = now;
                run.Travel = travel;
                run.Due = new float[run.Bombs];
                run.Fired = new bool[run.Bombs];
                for (var i = 0; i < run.Bombs; i++) run.Due[i] = run.ReleaseOf(i) + travel;
                run.Seen = 0;
                run.ShownFrom = float.NaN;
                run.ShownAt = now;
                run.Warn = false;
                run.Super = false;
                index = 0;
            }
            run.Warn |= warn;
            run.Super |= super;
            run.Fired[index] = true;
            run.Due[index] = now + travel;
            run.Seen++;
            return run;
        }

        /// <summary>The live run of <paramref name="owner"/> this bomb falls on (the nearest free section along its line), or null.</summary>
        private Run Continuing(long owner, WeaponDef round, Vector3 bomb, float now, out int index)
        {
            index = -1;
            var stick = round.Stick;
            foreach (var run in _runs)
            {
                if (run.Owner != owner || run.Weapon != round.Id || !run.Live(now)) continue;
                var offset = bomb - run.Start;
                var across = Mathf.Abs(offset.x * run.Dir.z - offset.z * run.Dir.x);
                if (across > Mathf.Max(stick.Width * 0.5f, run.Edge)) continue;
                var along = Vector3.Dot(offset, run.Dir) / Mathf.Max(0.1f, stick.Spacing);
                var k = Mathf.RoundToInt(along);
                if (k < 0 || k >= run.Bombs || Mathf.Abs(along - k) > 0.5f) continue;
                // A section taken already (a jitter put it near the next one): the next free one.
                while (k < run.Bombs && run.Fired[k]) k++;
                if (k >= run.Bombs) continue;
                // Past its release time and its grace: the stick is over, this is a new one.
                if (now > run.ReleaseOf(k) + Grace(stick) + stick.Interval) continue;
                index = k;
                return run;
            }
            return null;
        }

        private Run Fresh()
        {
            if (_runs.Count < Most)
            {
                var made = new Run();
                _runs.Add(made);
                return made;
            }
            // Every slot in use: the one that ends soonest.
            Run pick = null;
            var end = float.MaxValue;
            foreach (var run in _runs)
            {
                var last = 0f;
                foreach (var d in run.Due) last = Mathf.Max(last, d);
                if (last >= end) continue;
                end = last;
                pick = run;
            }
            return pick;
        }

        /// <summary>The frame's update (render clock): lets go of sections whose bomb never came and of finished runs.</summary>
        public void Tick(float now)
        {
            now = ShotClock.Map(Clock, now);
            for (var r = _runs.Count - 1; r >= 0; r--)
            {
                var run = _runs[r];
                var grace = Grace(run.Stick);
                for (var i = 0; i < run.Bombs; i++)
                    if (!run.Fired[i] && run.Due[i] > now && now > run.ReleaseOf(i) + grace) run.Due[i] = now;
                // Kept a moment after its last bomb lands, so that bomb's blast still finds its run (Landed).
                if (!run.Live(now - KeepAfter)) _runs.RemoveAt(r);
            }
        }

        /// <summary>
        /// The ground still to be hit at <paramref name="now"/> (shot clock): the sections from the first whose bomb has not
        /// landed to the last, as a rectangle round the stick's line: its middle, half its length (the end bombs' blast edge
        /// and their jitter along included) and the first and last section. False once every section has landed.
        /// </summary>
        public static bool Span(Run run, float now, float reach, out Vector3 centre, out float halfLength, out int front, out int last)
        {
            centre = run.Start;
            halfLength = 0f;
            if (!Range(run, now, reach, out var from, out var to, out front, out last)) return false;
            centre = run.Start + run.Dir * ((from + to) * 0.5f);
            halfLength = (to - from) * 0.5f;
            return true;
        }

        /// <summary>
        /// <see cref="Span"/> as distances along the stick from bomb 0's point: the near end (the front bomb's blast reach and
        /// jitter before it) and the far end (the last bomb's after it). False once every section has landed.
        /// </summary>
        public static bool Range(Run run, float now, float reach, out float from, out float to, out int front, out int last)
        {
            front = -1;
            last = -1;
            for (var i = 0; i < run.Bombs; i++)
            {
                if (run.Due[i] <= now) continue;
                if (front < 0) front = i;
                last = i;
            }
            from = 0f;
            to = 0f;
            if (front < 0) return false;
            var spacing = run.Stick.Spacing;
            var pad = reach + run.Stick.JitterAlong;
            from = front * spacing - pad;
            to = last * spacing + pad;
            return true;
        }

        /// <summary>
        /// The run and section a landing bomb of <paramref name="round"/> at <paramref name="impact"/> belongs to (the nearest
        /// section within half a spacing and its jitter), or null (not a stick's bomb, or not seen fired).
        /// </summary>
        public Run Landed(WeaponDef round, Vector3 impact, out int index)
        {
            index = -1;
            if (round?.Stick == null) return null;
            Run best = null;
            var bestGap = float.MaxValue;
            foreach (var run in _runs)
            {
                if (run.Weapon != round.Id) continue;
                var offset = new Vector3(impact.x - run.Start.x, 0f, impact.z - run.Start.z);
                var spacing = Mathf.Max(0.1f, run.Stick.Spacing);
                var k = Mathf.Clamp(Mathf.RoundToInt(Vector3.Dot(offset, run.Dir) / spacing), 0, run.Bombs - 1);
                var gap = (offset - run.Dir * (k * spacing)).magnitude;
                if (gap > spacing * 0.5f + run.Stick.JitterAlong + run.Stick.JitterAcross + 1f || gap >= bestGap) continue;
                bestGap = gap;
                best = run;
                index = k;
            }
            return best;
        }

        public void Clear() => _runs.Clear();
    }
}
