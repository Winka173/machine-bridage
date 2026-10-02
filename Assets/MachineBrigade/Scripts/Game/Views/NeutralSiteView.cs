using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 30 L6: the neutral sites on the battlefield (radar dome, field workshop, abandoned AA site, ammo depot). Each is a
    /// ground ring of the capture radius in its holder's colour (pale while nobody holds it) with the capture sweeping round
    /// it in the colour of the side taking it, like a capture point's but without the flag; the site's own building (the
    /// map's radar dome, garage or ammo dump) stands inside it. The abandoned AA site has no building until it is taken: its
    /// ring pulses softly so the empty spot reads as something to take, and it dims while it waits to be rebuilt. The
    /// contested supply drop gets a strike-style ring on its landing spot for the 15 s it falls (the crate itself is
    /// <see cref="CrateViews"/>'). Ground marks only (the GroundMark shader), so nothing here tints a MachineBrigade/Lit renderer.
    /// </summary>
    internal sealed class NeutralSiteView
    {
        private static readonly Color Pale = new(0.85f, 0.85f, 0.78f, 1f);
        private static readonly Color DropEdge = new(1.6f, 1.05f, 0.3f, 1f);
        private static readonly Color DropFill = new(1f, 0.72f, 0.2f, 0.35f);

        /// <summary>How long the contested supply drop falls (BattleEvents.CrateFall): the marker's sweep.</summary>
        private const float DropSeconds = 15f;

        private readonly MeshLibrary _meshes;
        private readonly MaterialLibrary _materials;
        private readonly Transform _root;
        private readonly List<GroundMark> _sites = new();
        private readonly List<GroundMark> _drops = new();

        public NeutralSiteView(MeshLibrary meshes, MaterialLibrary materials, Transform parent)
        {
            _meshes = meshes;
            _materials = materials;
            _root = new GameObject("Neutral Sites").transform;
            _root.SetParent(parent, false);
        }

        public void Render(SimWorld world, float time)
        {
            var used = 0;
            if (world.Map.Neutrals.Count > 0)
            {
                var radius = world.Neutrals.CaptureRadius;
                foreach (var (kind, at, team, taking, progress, waiting) in world.Neutrals.SiteStates)
                {
                    var mark = Take(_sites, used++, "Neutral Site", GroundMark.Style.Objective);
                    mark.Transform.position = new Vector3(at.X, 0.085f, at.Y);
                    mark.Transform.localScale = Vector3.one * radius;
                    var rim = team is 0 or 1 ? TeamColors.Ui(team) * 1.15f : Pale;
                    rim.a = waiting ? 0.45f : 1f;
                    var sweep = taking is 0 or 1 ? TeamColors.Ui(taking) : Pale;
                    // The empty AA spot pulses while it can be taken; a capture under way pulses too.
                    var pulse = taking is 0 or 1 && progress > 0f ? 1f : kind == "aa_site" && team < 0 && !waiting ? 0.5f : 0f;
                    mark.Set(rim, sweep, progress > 0f && progress < 0.999f ? progress : 0f, pulse);
                    mark.Visible = true;
                }
            }
            for (var i = used; i < _sites.Count; i++) _sites[i].Visible = false;

            var drops = 0;
            var now = world.Time;
            foreach (var crate in world.Crates)
            {
                var left = (float)(crate.LandsAt - now);
                if (!crate.IsAlive || left <= 0f) continue;
                var mark = Take(_drops, drops++, "Supply Drop Mark", GroundMark.Style.Strike);
                mark.Transform.position = new Vector3(crate.Position.X, 0.11f, crate.Position.Y);
                mark.Transform.localScale = Vector3.one * (5f + 0.15f * Mathf.Sin(time * 4f));
                mark.Set(DropEdge, DropFill, Mathf.Clamp01(1f - left / DropSeconds), Mathf.Clamp01(1f - left / 5f));
                mark.Visible = true;
            }
            for (var i = drops; i < _drops.Count; i++) _drops[i].Visible = false;
        }

        private GroundMark Take(List<GroundMark> pool, int index, string name, GroundMark.Style style)
        {
            while (pool.Count <= index) pool.Add(new GroundMark(name, _root, _meshes, _materials, style) { Visible = false });
            return pool[index];
        }
    }
}
