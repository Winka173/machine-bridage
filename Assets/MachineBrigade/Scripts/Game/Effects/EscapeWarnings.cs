using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 34 L3: the warning on the fall point of a boss's T4+ round (203 mm and up, the Smerch, the 400 kg bombs, the
    /// 406 mm salvo): a red ring exactly as wide as the blast's edge, a brighter ring on its core, both filling as the round
    /// comes down, for the round's escape warning (<see cref="MachineBrigade.Sim.Content.WeaponDef.WarnSeconds"/>; the Sim
    /// holds the round in the air that long). Every round of a salvo gets its own pair. View only; the minimap's mark is
    /// MatchRunner's. Pooled marks (the big attacks' style), no fill over the player's units.
    /// </summary>
    internal sealed class EscapeWarnings
    {
        private const int Pairs = 32;

        private static readonly Color EdgeColour = new(2.4f, 0.32f, 0.16f, 0.85f);
        private static readonly Color EdgeFill = new(2.2f, 0.6f, 0.2f, 0.7f);
        private static readonly Color CoreColour = new(3f, 0.9f, 0.3f, 1f);
        private static readonly Color CoreFill = new(3f, 1.2f, 0.4f, 1f);

        private sealed class Pair
        {
            public GroundMark Edge, Core;
            public Vector3 At;
            public float CoreRadius, EdgeRadius, Start, Due;
            public bool Active;
        }

        private readonly List<Pair> _pairs = new();

        public EscapeWarnings(MaterialLibrary materials, MeshLibrary meshes, Transform parent)
        {
            var root = new GameObject("Escape Warnings").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < Pairs; i++)
                _pairs.Add(new Pair
                {
                    Edge = new GroundMark("Warning Edge", root, meshes, materials, GroundMark.Style.Strike) { Visible = false },
                    Core = new GroundMark("Warning Core", root, meshes, materials, GroundMark.Style.Strike) { Visible = false },
                });
        }

        /// <summary>A round falling on <paramref name="at"/> at <paramref name="due"/>, warned from <paramref name="start"/>.</summary>
        public void Add(Vector3 at, float core, float edge, float start, float due)
        {
            if (due <= start || (core <= 0f && edge <= 0f)) return;
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
            pick.CoreRadius = Mathf.Max(0.5f, core);
            pick.EdgeRadius = Mathf.Max(pick.CoreRadius, edge);
            pick.Start = start;
            pick.Due = due;
        }

        public void Tick(float now)
        {
            foreach (var p in _pairs)
            {
                if (!p.Active) continue;
                if (now >= p.Due)
                {
                    p.Active = false;
                    p.Edge.Visible = p.Core.Visible = false;
                    continue;
                }
                if (now < p.Start)
                {
                    p.Edge.Visible = p.Core.Visible = false;
                    continue;
                }
                var progress = Mathf.Clamp01((now - p.Start) / Mathf.Max(0.05f, p.Due - p.Start));
                var urgency = Mathf.Clamp01(1f - (p.Due - now) / 1.5f);
                p.Edge.Transform.position = p.At;
                p.Edge.Transform.localScale = Vector3.one * p.EdgeRadius;
                p.Edge.Set(EdgeColour, EdgeFill, progress, urgency);
                p.Edge.Visible = true;
                var twoLayer = p.EdgeRadius > p.CoreRadius + 0.25f;
                if (twoLayer)
                {
                    p.Core.Transform.position = p.At + Vector3.up * 0.01f;
                    p.Core.Transform.localScale = Vector3.one * p.CoreRadius;
                    p.Core.Set(CoreColour, CoreFill, progress, urgency);
                }
                p.Core.Visible = twoLayer;
            }
        }
    }
}
