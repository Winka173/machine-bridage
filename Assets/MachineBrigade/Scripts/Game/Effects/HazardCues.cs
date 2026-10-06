using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// MVA W2-B (spec parts AF, BL; THREAT_CUES.md rows "mine detected" and "EMP", W1's gaps): the two hazards that had no cue.
    /// <list type="bullet">
    /// <item>Mine detected: a hostile mine the player's side has just spotted gets a pulsing amber ring exactly on its trigger
    /// radius for <see cref="MineSeconds"/> s (telegraph shape = danger shape), three slow pulses in amber (not a blast
    /// warning's red-orange, and pulsing where a blast ring closes); the mine's model stays on the ground after it. Audio:
    /// the P1 mine ping (AudioDirector).</item>
    /// <item>EMP: an EMP going off (a unit's skill or the support) draws an electric ring exactly on its radius for
    /// <see cref="EmpSeconds"/> s, snapping out from 0.85 of it (the units inside are the ones knocked out, which crackle
    /// on their own: EffectsDirector's KnockedOut sparks). It has no lead (it is instant); the support's strike zone is its
    /// telegraph. Audio: the P1 EMP burst when it reaches the player's units.</item>
    /// </list>
    /// Both are GroundMarks (drawn above smoke, decals and debris, spec part AG), on every graphics tier (spec part AN), and
    /// follow the warning-rings setting like the other non-super rings (Off hides them; their sounds and captions stay).
    /// </summary>
    internal sealed class HazardCues
    {
        internal const int Marks = 10;
        internal const float MineSeconds = 3f, EmpSeconds = 1.4f;

        private static readonly Color MineEdge = new(2.2f, 1.45f, 0.25f, 0.95f), MineFill = new(1.2f, 0.75f, 0.1f, 0.22f);
        private static readonly Color EmpEdge = new(1.1f, 1.9f, 3.2f, 1f), EmpFill = new(0.4f, 0.8f, 1.6f, 0.28f);

        private sealed class Mark
        {
            public GroundMark Ring;
            public Vector3 At;
            public float Radius, Start, End;
            public bool Emp;
        }

        private readonly List<Mark> _marks = new();

        /// <summary>The Settings choice for warning rings (2: off).</summary>
        public int Level { get; set; }

        public HazardCues(MaterialLibrary materials, MeshLibrary meshes, Transform parent)
        {
            var root = new GameObject("Hazard Cues").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < Marks; i++)
                _marks.Add(new Mark { Ring = new GroundMark("Hazard", root, meshes, materials, GroundMark.Style.Warning) { Visible = false } });
        }

        /// <summary>Marks live now (tests).</summary>
        internal int Live(float now)
        {
            var n = 0;
            foreach (var m in _marks)
                if (now < m.End) n++;
            return n;
        }

        public void MineFound(Vector3 at, float radius, float now) => Add(at, Mathf.Max(0.5f, radius), now, MineSeconds, false);

        public void Emp(Vector3 at, float radius, float now) => Add(at, Mathf.Max(1f, radius), now, EmpSeconds, true);

        private void Add(Vector3 at, float radius, float now, float seconds, bool emp)
        {
            Mark pick = null;
            foreach (var m in _marks)
            {
                // One ring a spot: a mine found again (or an EMP twice) keeps its ring.
                if (now < m.End && m.Emp == emp && (m.At - at).sqrMagnitude < 0.25f)
                {
                    m.End = Mathf.Max(m.End, now + seconds);
                    return;
                }
                if (now >= m.End && pick == null) pick = m;
            }
            if (pick == null)
                foreach (var m in _marks)
                    if (pick == null || m.End < pick.End) pick = m;
            pick.At = at;
            pick.Radius = radius;
            pick.Start = now;
            pick.End = now + seconds;
            pick.Emp = emp;
        }

        public void Tick(float now)
        {
            foreach (var m in _marks)
            {
                if (now >= m.End || Level >= 2)
                {
                    m.Ring.Visible = false;
                    continue;
                }
                var t = Mathf.Clamp01((now - m.Start) / Mathf.Max(0.05f, m.End - m.Start));
                float size;
                Color edge, fill;
                if (m.Emp)
                {
                    // Snaps out to its radius in the first fifth, then holds and fades.
                    size = m.Radius * Mathf.Lerp(0.85f, 1f, Mathf.Clamp01(t * 5f));
                    var fade = 1f - Mathf.Clamp01((t - 0.6f) / 0.4f);
                    edge = new Color(EmpEdge.r, EmpEdge.g, EmpEdge.b, EmpEdge.a * fade);
                    fill = new Color(EmpFill.r, EmpFill.g, EmpFill.b, EmpFill.a * fade);
                }
                else
                {
                    // Three slow pulses on the trigger radius (never a fast strobe: spec part AL).
                    size = m.Radius;
                    var pulse = 0.65f + 0.35f * Mathf.Cos(t * Mathf.PI * 6f);
                    var fade = 1f - Mathf.Clamp01((t - 0.75f) / 0.25f);
                    edge = new Color(MineEdge.r, MineEdge.g, MineEdge.b, MineEdge.a * pulse * fade);
                    fill = new Color(MineFill.r, MineFill.g, MineFill.b, MineFill.a * pulse * fade);
                }
                m.Ring.Transform.position = new Vector3(m.At.x, 0.15f, m.At.z);
                m.Ring.Transform.localScale = Vector3.one * size;
                m.Ring.Set(edge, fill, 1f - t, m.Emp ? 0f : 1f);
                m.Ring.Visible = true;
            }
        }
    }
}
