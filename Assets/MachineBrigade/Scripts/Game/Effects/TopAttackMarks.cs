using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// MVA W1-B (spec part AE, ThreatCues TopAttack): a top-attack round's own cue, distinct from direct fire: over the dive (its
    /// last <see cref="DiveShare"/> of the flight, at least <see cref="MinDive"/> s) a ring rides on the targeted unit of the
    /// player's and closes from <see cref="OpenScale"/> to <see cref="ClosedScale"/> of its size as the round comes down. Shape
    /// and motion carry it (a closing ring on a moving unit, not the escape warning's fixed ground ring), its pale violet
    /// only adds to that. Only weapons marked top attack ever get one; ordinary direct fire never does. View only; on every
    /// graphics tier (spec part AN); the warning-rings setting Off hides it like the other non-super rings.
    /// </summary>
    internal sealed class TopAttackMarks
    {
        private const int Marks = 12;
        internal const float DiveShare = 0.4f, MinDive = 0.9f, OpenScale = 2.6f, ClosedScale = 1.15f;

        // MVA W2-B: a deeper violet, so the hue survives HDR clipping on snow (it read near white there: contrast_audit.py).
        private static readonly Color Edge = new(1.25f, 0.3f, 2.2f, 0.95f);
        private static readonly Color Fill = new(0.75f, 0.2f, 1.4f, 0.35f);

        private sealed class Mark
        {
            public GroundMark Ring;

            /// <summary>MVA W2-B (spec part AE): the vertical approach marker, a dive line coming down onto the target.</summary>
            public LineRenderer Dive;
            public EntityId Target;
            public float Start, Due;
            public bool Active;
        }

        private readonly List<Mark> _marks = new();
        private readonly Vector3[] _ends = new Vector3[2];

        /// <summary>MVA W2-B: how high above the target the dive line starts (m).</summary>
        internal const float DiveTop = 16f;

        private static Material _diveMaterial;

        /// <summary>The dive line: a view-facing line on its own unlit HDR violet (never a property block).</summary>
        private static LineRenderer DiveLine(MaterialLibrary materials, Transform root)
        {
            if (_diveMaterial == null)
            {
                _diveMaterial = new Material(materials.StrikeWarning) { name = "Top Attack Dive" };
                _diveMaterial.SetColor("_Color", new Color(1.4f, 0.35f, 2.6f));
            }
            var go = new GameObject("Top Attack Dive");
            go.transform.SetParent(root, false);
            var line = go.AddComponent<LineRenderer>();
            line.sharedMaterial = _diveMaterial;
            line.useWorldSpace = true;
            line.positionCount = 2;
            line.alignment = LineAlignment.View;
            line.numCapVertices = 2;
            line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            line.receiveShadows = false;
            line.enabled = false;
            return line;
        }

        /// <summary>The owning EffectsDirector's shot clock (none: the times given are used as they are).</summary>
        internal ShotClock Clock { get; set; }

        /// <summary>The Settings choice for warning rings (2: off).</summary>
        public int Level { get; set; }

        public TopAttackMarks(MaterialLibrary materials, MeshLibrary meshes, Transform parent)
        {
            var root = new GameObject("Top Attack Marks").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < Marks; i++)
                _marks.Add(new Mark
                {
                    Ring = new GroundMark("Top Attack", root, meshes, materials, GroundMark.Style.Warning) { Visible = false },
                    Dive = DiveLine(materials, root),
                });
        }

        /// <summary>Marks live now (tests).</summary>
        internal int ActiveCount
        {
            get
            {
                var n = 0;
                foreach (var m in _marks)
                    if (m.Active) n++;
                return n;
            }
        }

        /// <summary>A top-attack round on <paramref name="target"/> fired at <paramref name="now"/>, landing <paramref name="flight"/> s later.</summary>
        public void Add(EntityId target, float now, float flight)
        {
            if (flight <= 0.05f) return;
            now = ShotClock.Map(Clock, now);
            var due = now + flight;
            var start = due - Mathf.Min(flight, Mathf.Max(MinDive, flight * DiveShare));
            Mark pick = null;
            foreach (var m in _marks)
            {
                // One mark a target: a second round on it keeps the mark up to the later landing.
                if (m.Active && m.Target.Equals(target))
                {
                    m.Start = Mathf.Min(m.Start, start);
                    m.Due = Mathf.Max(m.Due, due);
                    return;
                }
                if (!m.Active && pick == null) pick = m;
            }
            if (pick == null)
                foreach (var m in _marks)
                    if (pick == null || m.Due < pick.Due) pick = m;
            pick.Active = true;
            pick.Target = target;
            pick.Start = start;
            pick.Due = due;
        }

        public void Tick(ViewRegistry views, float now)
        {
            now = ShotClock.Map(Clock, now);
            foreach (var m in _marks)
            {
                if (!m.Active) continue;
                // Off the moment it lands, or with its target gone (cancel: spec part AF).
                if (now >= m.Due || !views.TryGet(m.Target, out var view) || view.Root == null || view.IsWreck)
                {
                    m.Active = false;
                    m.Ring.Visible = false;
                    m.Dive.enabled = false;
                    continue;
                }
                if (now < m.Start || Level >= 2)
                {
                    m.Ring.Visible = false;
                    m.Dive.enabled = false;
                    continue;
                }
                var progress = Mathf.Clamp01((now - m.Start) / Mathf.Max(0.05f, m.Due - m.Start));
                var size = Mathf.Max(1f, view.Sim.Radius) * Mathf.Lerp(OpenScale, ClosedScale, progress * progress);
                var p = view.Position;
                m.Ring.Transform.position = new Vector3(p.x, 0.16f, p.z);
                m.Ring.Transform.localScale = Vector3.one * size;
                m.Ring.Set(Edge, Fill, progress, progress);
                m.Ring.Visible = true;
                // MVA W2-B: the overhead approach: a violet line straight above the target whose top comes down with the round
                // (from DiveTop m to the target's roof), so the attack reads as from above, not along the ground like an ATGM.
                var roof = Mathf.Max(1.2f, view.Sim.Radius * 0.8f);
                var top = Mathf.Lerp(DiveTop, roof + 1.5f, progress * progress);
                _ends[0] = new Vector3(p.x, top, p.z);
                _ends[1] = new Vector3(p.x, roof, p.z);
                m.Dive.SetPositions(_ends);
                m.Dive.widthMultiplier = Mathf.Lerp(0.18f, 0.45f, progress);
                m.Dive.enabled = true;
            }
        }
    }
}
