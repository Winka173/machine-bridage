using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// The bomb-run fix, pass 3 (DECISIONS "Ném bom rải thảm"): a stick's warning (stick.warnShape STICK_RECT: the 500 kg
    /// stick, the boss bays) is one rectangle round the whole stick in place of a ring per bomb (the escape rings of one
    /// shooter merged into one big circle): a thin edge on the blast's edge and a faint fill
    /// (<see cref="GroundMark.Style.WarningRect"/>), a darker band along its middle as wide as the blast's core, the flight
    /// line dashed down the middle and running the way the bombs walk, and the next bomb's core ring with its countdown
    /// (the escape ring's look) riding the front of the stick. It shows from the stick's first bomb and gives up its ground
    /// section by section as the bombs land (<see cref="StickRuns.Range"/>), its front edge gliding on to the next bomb in
    /// <see cref="FrontGlide"/> s rather than jumping. Each stick is offered to the <see cref="WarningGate"/> as a rectangle
    /// (the player's units inside it count as threatened; the Settings level applies; a T5 or a preview's is a super
    /// weapon's). View only.
    /// </summary>
    internal sealed class StickWarnings
    {
        private const int Sets = 8;

        // The escape rings' colours (EscapeWarnings), so a stick reads as the same warning.
        private static readonly Color EdgeColour = new(2.2f, 0.42f, 0.2f, 0.9f);
        private static readonly Color EdgeFill = new(1.6f, 0.36f, 0.16f, 0.55f);
        private static readonly Color CoreColour = new(1.5f, 0.12f, 0.06f, 1f);
        private static readonly Color CoreFill = new(1.1f, 0.08f, 0.04f, 1f);
        private static readonly Color NextColour = new(2.6f, 0.3f, 0.12f, 1f);
        private static readonly Color NextFill = new(1.4f, 0.14f, 0.06f, 0.8f);

        private const float Height = 0.13f, SuperLift = 0.03f;

        /// <summary>Seconds the front edge takes to move on to the next section once a bomb has landed.</summary>
        internal const float FrontGlide = 0.15f;

        private sealed class Set
        {
            public GroundMark Edge, Core, Next;
        }

        private readonly List<Set> _sets = new();

        public WarningGate Gate { get; set; }

        /// <summary>Data warningRules: seconds the rectangle takes to fade in.</summary>
        public float FadeIn { get; set; } = 0.4f;

        /// <summary>Rectangles drawn now (tests).</summary>
        internal int Drawn { get; private set; }

        public StickWarnings(MaterialLibrary materials, MeshLibrary meshes, Transform parent)
        {
            var root = new GameObject("Stick Warnings").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < Sets; i++)
                _sets.Add(new Set
                {
                    Edge = new GroundMark("Stick Edge", root, meshes, materials, GroundMark.Style.WarningRect) { Visible = false },
                    Core = new GroundMark("Stick Core", root, meshes, materials, GroundMark.Style.WarningRect) { Visible = false },
                    Next = new GroundMark("Stick Next Bomb", root, meshes, materials, GroundMark.Style.Warning) { Visible = false },
                });
        }

        /// <summary>
        /// Where the drawn front edge is now (m along the stick from bomb 0): the front section's edge, reached from the last
        /// drawn one in <see cref="FrontGlide"/> s (a spacing's worth a glide), never behind it. Pure (tests).
        /// </summary>
        internal static float Glide(StickRuns.Run run, float from, float now)
        {
            if (float.IsNaN(run.ShownFrom) || from <= run.ShownFrom) return from;
            var step = Mathf.Max(0f, now - run.ShownAt) * Mathf.Max(1f, run.Stick.Spacing) / FrontGlide;
            return Mathf.Min(from, run.ShownFrom + step);
        }

        /// <summary>The frame's rectangles for the warned runs of <paramref name="runs"/>; <paramref name="now"/> on the shot clock.</summary>
        public void Tick(IReadOnlyList<StickRuns.Run> runs, float now)
        {
            var used = 0;
            for (var r = 0; r < runs.Count; r++)
            {
                var run = runs[r];
                if (!run.Warn || !StickRuns.Range(run, now, run.Edge, out var target, out var to, out var front, out _)) continue;
                var from = Mathf.Min(Glide(run, target, now), to - 0.5f);
                run.ShownFrom = from;
                run.ShownAt = now;
                var centre = run.Start + run.Dir * ((from + to) * 0.5f);
                var halfLength = (to - from) * 0.5f;
                var halfWidth = Mathf.Max(run.Edge, run.Stick.Width * 0.5f);
                var kind = run.Super ? WarningKind.Super : WarningKind.Round;
                Gate?.OfferRect(run, centre, run.Dir, halfLength, halfWidth, kind);
                if (used >= _sets.Count || (Gate != null && !Gate.Shown(run, kind))) continue;
                var set = _sets[used++];
                var fade = FadeIn > 0f ? Mathf.Clamp01((now - run.First) / FadeIn) : 1f;
                var due = run.Due[front];
                var urgency = Mathf.Clamp01(1f - (due - now) / 1.5f);
                var lift = run.Super ? SuperLift : 0f;
                var turn = Quaternion.LookRotation(run.Dir, Vector3.up);
                set.Edge.Transform.SetPositionAndRotation(new Vector3(centre.x, Height + lift, centre.z), turn);
                set.Edge.Transform.localScale = new Vector3(halfWidth, 1f, halfLength);
                set.Edge.Set(Faded(EdgeColour, fade), EdgeFill, 0f, urgency);
                set.Edge.Visible = true;
                // The core band: the stick's line as wide as the blast's core and its jitter across, from the front bomb's core
                // to the last one's (the edge band less the edge beyond the core at each end).
                var inset = run.Edge - run.Core;
                var coreFrom = from + inset;
                var coreTo = to - inset;
                var coreWidth = run.Core + run.Stick.JitterAcross;
                var twoLayer = halfWidth > coreWidth + 0.25f && coreTo > coreFrom + 0.5f;
                if (twoLayer)
                {
                    var coreCentre = run.Start + run.Dir * ((coreFrom + coreTo) * 0.5f);
                    set.Core.Transform.SetPositionAndRotation(new Vector3(coreCentre.x, Height + lift + 0.01f, coreCentre.z), turn);
                    set.Core.Transform.localScale = new Vector3(coreWidth, 1f, (coreTo - coreFrom) * 0.5f);
                    set.Core.Set(Faded(CoreColour, fade), CoreFill, 0f, urgency);
                }
                set.Core.Visible = twoLayer;
                // The next bomb: its core ring on its point, the time to its landing running round it (from the blast before it,
                // the first from the stick's release), so the eye follows the blasts along the line in their rhythm.
                var next = run.Start + run.Dir * (front * run.Stick.Spacing);
                var since = front > 0 ? Mathf.Min(run.Due[front - 1], due - 0.05f) : run.First;
                var span = Mathf.Max(0.05f, due - since);
                set.Next.Transform.position = new Vector3(next.x, Height + lift + 0.02f, next.z);
                set.Next.Transform.localScale = Vector3.one * run.Core;
                set.Next.Set(Faded(NextColour, fade), NextFill, Mathf.Clamp01((now - since) / span), urgency);
                set.Next.Visible = true;
            }
            Drawn = used;
            for (var i = used; i < _sets.Count; i++) _sets[i].Edge.Visible = _sets[i].Core.Visible = _sets[i].Next.Visible = false;
        }

        private static Color Faded(Color c, float fade) => new(c.r, c.g, c.b, c.a * fade);
    }
}
