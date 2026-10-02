using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 34 L3, fix prompt L5: the warning on the fall point of an enemy's T4+ round (203 mm and up, the Smerch, the
    /// 400 kg bombs, the 406 mm salvo): a ring exactly as wide as the blast's edge and one on its core, for the round's escape
    /// warning (<see cref="MachineBrigade.Sim.Content.WeaponDef.WarnSeconds"/>; the Sim holds the round in the air that long).
    /// Fix prompt L5's look: a thin edge and a faint fill (<see cref="GroundMark.Style.Warning"/>, not solid red), the core
    /// darker than the edge, fading in over <see cref="FadeIn"/> and gone the moment the round lands. One shooter's rounds
    /// fired within <see cref="SalvoMerge"/> whose rings touch are one ring round them all (the salvo's hull, its core the
    /// widest of theirs). Each ring is offered to the <see cref="WarningGate"/> and drawn only while it is shown; a T5 round's
    /// is a super weapon's (always shown, drawn above the others). View only; the minimap's mark is MatchRunner's.
    /// </summary>
    internal sealed class EscapeWarnings
    {
        private const int Pairs = 32;

        private static readonly Color EdgeColour = new(2.2f, 0.42f, 0.2f, 0.9f);
        private static readonly Color EdgeFill = new(1.6f, 0.36f, 0.16f, 0.55f);
        private static readonly Color CoreColour = new(1.5f, 0.12f, 0.06f, 1f);
        private static readonly Color CoreFill = new(1.1f, 0.08f, 0.04f, 1f);

        /// <summary>Super weapons' rings sit this much higher, so they draw over the others.</summary>
        private const float SuperLift = 0.03f;

        private sealed class Pair
        {
            public GroundMark Edge, Core;
            public Vector3 At;
            public float CoreRadius, EdgeRadius, Start, Due, Fired;
            public long Owner;
            public bool Active, Super;
        }

        private readonly List<Pair> _pairs = new();

        /// <summary>The gate that decides which rings are drawn (none: every ring is).</summary>
        public WarningGate Gate { get; set; }

        /// <summary>Data warningRules: seconds a ring takes to fade in, and the salvo window.</summary>
        public float FadeIn { get; set; } = 0.4f;
        public float SalvoMerge { get; set; } = 0.6f;

        public EscapeWarnings(MaterialLibrary materials, MeshLibrary meshes, Transform parent)
        {
            var root = new GameObject("Escape Warnings").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < Pairs; i++)
                _pairs.Add(new Pair
                {
                    Edge = new GroundMark("Warning Edge", root, meshes, materials, GroundMark.Style.Warning) { Visible = false },
                    Core = new GroundMark("Warning Core", root, meshes, materials, GroundMark.Style.Warning) { Visible = false },
                });
        }

        /// <summary>Rings live now (tests).</summary>
        internal int ActiveCount
        {
            get
            {
                var n = 0;
                foreach (var p in _pairs)
                    if (p.Active) n++;
                return n;
            }
        }

        /// <summary>
        /// A round falling on <paramref name="at"/> at <paramref name="due"/>, warned from <paramref name="start"/>, fired at
        /// <paramref name="now"/> by <paramref name="owner"/> (a shooter and mount; 0: none, never merged).
        /// </summary>
        public void Add(Vector3 at, float core, float edge, float start, float due, float now = 0f, long owner = 0, bool super = false)
        {
            if (due <= start || (core <= 0f && edge <= 0f)) return;
            var coreRadius = Mathf.Max(0.5f, core);
            var edgeRadius = Mathf.Max(coreRadius, edge);
            // A salvo: the same shooter's ring fired just before that this one touches grows to hold both.
            if (owner != 0)
                foreach (var p in _pairs)
                {
                    if (!p.Active || p.Owner != owner || now - p.Fired > SalvoMerge) continue;
                    var gap = Vector2.Distance(new Vector2(p.At.x, p.At.z), new Vector2(at.x, at.z));
                    if (gap > p.EdgeRadius + edgeRadius) continue;
                    Merge(p, at, coreRadius, edgeRadius, gap);
                    p.Start = Mathf.Min(p.Start, start);
                    p.Due = Mathf.Max(p.Due, due);
                    p.Super |= super;
                    return;
                }
            // A free pair, else the one that lands soonest (it is nearly done).
            Pair pick = null;
            foreach (var p in _pairs)
            {
                if (!p.Active)
                {
                    pick = p;
                    break;
                }
                if (pick == null || p.Due < pick.Due) pick = p;
            }
            pick.Active = true;
            pick.At = new Vector3(at.x, 0.13f, at.z);
            pick.CoreRadius = coreRadius;
            pick.EdgeRadius = edgeRadius;
            pick.Start = start;
            pick.Due = due;
            pick.Fired = now;
            pick.Owner = owner;
            pick.Super = super;
        }

        /// <summary>The smallest circle holding the pair's ring and a new one <paramref name="gap"/> m away (its core: the widest).</summary>
        private static void Merge(Pair p, Vector3 at, float core, float edge, float gap)
        {
            var outer = (gap + p.EdgeRadius + edge) * 0.5f;
            if (outer <= p.EdgeRadius) return; // the new ring is inside the old one
            if (outer <= edge)
            {
                // The old ring is inside the new one.
                p.At = new Vector3(at.x, p.At.y, at.z);
                p.EdgeRadius = edge;
                p.CoreRadius = Mathf.Max(p.CoreRadius, core);
                return;
            }
            var t = gap > 1e-3f ? (outer - p.EdgeRadius) / gap : 0f;
            p.At = new Vector3(Mathf.Lerp(p.At.x, at.x, t), p.At.y, Mathf.Lerp(p.At.z, at.z, t));
            p.EdgeRadius = outer;
            p.CoreRadius = Mathf.Max(p.CoreRadius, core);
        }

        public void Tick(float now)
        {
            foreach (var p in _pairs)
            {
                if (!p.Active) continue;
                // Off the moment it lands.
                if (now >= p.Due)
                {
                    p.Active = false;
                    p.Edge.Visible = p.Core.Visible = false;
                    continue;
                }
                var kind = p.Super ? WarningKind.Super : WarningKind.Round;
                Gate?.Offer(p, p.At, p.EdgeRadius, kind);
                if (now < p.Start || (Gate != null && !Gate.Shown(p, kind)))
                {
                    p.Edge.Visible = p.Core.Visible = false;
                    continue;
                }
                var progress = Mathf.Clamp01((now - p.Start) / Mathf.Max(0.05f, p.Due - p.Start));
                var urgency = Mathf.Clamp01(1f - (p.Due - now) / 1.5f);
                var fade = FadeIn > 0f ? Mathf.Clamp01((now - p.Start) / FadeIn) : 1f;
                var lift = p.Super ? SuperLift : 0f;
                p.Edge.Transform.position = p.At + Vector3.up * lift;
                p.Edge.Transform.localScale = Vector3.one * p.EdgeRadius;
                p.Edge.Set(Faded(EdgeColour, fade), EdgeFill, progress, urgency);
                p.Edge.Visible = true;
                var twoLayer = p.EdgeRadius > p.CoreRadius + 0.25f;
                if (twoLayer)
                {
                    p.Core.Transform.position = p.At + Vector3.up * (lift + 0.01f);
                    p.Core.Transform.localScale = Vector3.one * p.CoreRadius;
                    p.Core.Set(Faded(CoreColour, fade), CoreFill, progress, urgency);
                }
                p.Core.Visible = twoLayer;
            }
        }

        private static Color Faded(Color c, float fade) => new(c.r, c.g, c.b, c.a * fade);
    }
}
