using System.Collections.Generic;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Shields (prompt 11C) the effects draw or feed: the Shield Dome item's dome over the spot it
    /// was called on, for as long as it lasts (flickering in its last second, then shattering),
    /// and the ripples rounds leave on every shield they strike: the item's dome, a vehicle's own
    /// shield, a siege objective's. The fortress's dome takes its own ripples (FortressView).
    /// </summary>
    public sealed partial class EffectsDirector
    {
        /// <summary>How tall an item's dome stands for its radius (the fortress dome's shape).</summary>
        private const float ItemDomeHeight = 0.5f;

        /// <summary>Its last seconds, flickering as it runs out.</summary>
        private const float ItemDomeFading = 1.2f;

        private const int MaxItemDomes = 4;

        private sealed class ItemDome
        {
            public ShieldVisual Shield;
            public Vector3 Centre;
            public float Radius, Ends;
            public int Team;
            public bool Falling;
        }

        private readonly List<ItemDome> _itemDomes = new();

        /// <summary>Vehicles were marked as under a dome last frame (so they are cleared once none stands).</summary>
        private bool _covering;

        private ShieldVisual _warmShield;
        private float _warmShieldUntil;

        /// <summary>
        /// A staged moment without a blast (the fortress's dome giving way): the camera shakes by
        /// <paramref name="shake"/> and, when near the view, the screen flashes a little.
        /// </summary>
        public void Jolt(Vector3 at, float shake, float flash)
        {
            Shake(at, shake);
            if (flash > 0f) Flash?.Invoke(flash / (1f + Vector3.Distance(at, _camera.Focus) / 40f));
        }

        /// <summary>The Shield Dome item landed: its dome, as wide as the item reaches, for as long as it lasts.</summary>
        private void RaiseItemDome(in SimEvent e, SupportDef support, ViewRegistry views, float now)
        {
            var radius = Mathf.Max(2f, support.Radius);
            var centre = Ground(e.Position, 0f);
            if (_itemDomes.Count >= MaxItemDomes)
            {
                // Too many at once: the oldest gives way.
                var oldest = _itemDomes[0];
                if (!oldest.Falling)
                {
                    oldest.Falling = true;
                    oldest.Shield.Collapse(now);
                }
            }
            var shield = new ShieldVisual("Shield Dome Item", _root, ShieldVisual.Shape.Dome, radius);
            shield.Transform.position = centre;
            shield.Transform.localScale = new Vector3(radius, radius * ItemDomeHeight, radius);
            var ours = e.Team == views.PlayerTeam;
            shield.SetSide(ours);
            shield.Raise(now);
            // A ring of its light runs out over the ground as it comes up.
            var tint = ShieldVisual.SideColour(ours);
            Ring(centre, radius * 2f, new Color(tint.r * 2.2f, tint.g * 2.2f, tint.b * 2.2f, 1f));
            _itemDomes.Add(new ItemDome { Shield = shield, Centre = centre, Radius = radius, Ends = now + support.Duration, Team = e.Team });
            // The vehicles it covers carry the shield as long as it lasts, wherever they go (their
            // own shield flickers out with it).
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var v = all[i];
                if (v.Team != e.Team || v.IsWreck) continue;
                var flat = new Vector2(v.Position.x - centre.x, v.Position.z - centre.z);
                if (flat.magnitude <= radius + v.Sim.Radius) v.ShieldFor(support.Duration, now);
            }
        }

        /// <summary>
        /// A round landed: the shield it struck ripples where it hit (a vehicle's own, a siege
        /// objective's), and so does an item's dome it landed on or inside.
        /// </summary>
        private void ShieldImpact(in SimEvent e, ViewRegistry views, MapView map, float now)
        {
            if (e.Entity.IsValid)
            {
                if (views.TryGet(e.Entity, out var struck)) struck.ShieldHit(e.Position.X, e.Position.Y);
                else map?.ShieldHit(e.Entity, new Vector3(e.Position.X, 1f, e.Position.Y), now);
            }
            if (e.Airborne) return;
            RippleItemDomes(e.Position, e.Kind == SimEventKind.StrikeImpact ? 1.5f : 1f, now);
        }

        private void RippleItemDomes(System.Numerics.Vector2 at, float strength, float now)
        {
            for (var i = 0; i < _itemDomes.Count; i++)
            {
                var dome = _itemDomes[i];
                if (dome.Falling) continue;
                var flat = new Vector2(at.X - dome.Centre.x, at.Y - dome.Centre.z);
                if (flat.magnitude > dome.Radius * 1.05f) continue;
                // Test feedback 19P: the ripple and a flash on the skin over where it landed.
                var skin = DomeSkin(dome.Centre, dome.Radius, dome.Radius * ItemDomeHeight, new Vector3(at.X, 1f, at.Y), default, true, out var normal);
                dome.Shield.Hit(skin, now, default, strength);
                DomeFlash(skin, normal, strength);
            }
        }

        /// <summary>A shielded vehicle lost health (a splash, a burn): its shield shows the blow on the side the player sees.</summary>
        private static void ShieldDamaged(in SimEvent e, ViewRegistry views)
        {
            if (views.TryGet(e.Entity, out var hurt)) hurt.ShieldStruck();
        }

        /// <summary>Every frame: the item domes run out (flickering, then shattering); who stands under one of their side's.</summary>
        private void TickShields(ViewRegistry views, float now)
        {
            if (_warmShield != null && now >= _warmShieldUntil)
            {
                Object.Destroy(_warmShield.Transform.gameObject);
                _warmShield = null;
            }
            else _warmShield?.Tick(now);
            for (var i = _itemDomes.Count - 1; i >= 0; i--)
            {
                var dome = _itemDomes[i];
                if (!dome.Falling && now >= dome.Ends)
                {
                    dome.Falling = true;
                    dome.Shield.Collapse(now);
                }
                if (!dome.Falling) dome.Shield.Flicker = Mathf.Clamp01(1f - (dome.Ends - now) / ItemDomeFading);
                if (dome.Shield.Tick(now)) continue;
                Object.Destroy(dome.Shield.Transform.gameObject);
                _itemDomes.RemoveAt(i);
            }
            if (_itemDomes.Count == 0 && !_covering) return;
            // A vehicle under a standing dome of its side has the dome for its shield: its own
            // bubble is not drawn inside it, and comes up if it drives out.
            var covering = false;
            var all = views.All;
            for (var v = 0; v < all.Count; v++)
            {
                var view = all[v];
                var covered = false;
                for (var d = 0; d < _itemDomes.Count && !covered; d++)
                {
                    var dome = _itemDomes[d];
                    // Its shatter too: the shields it gave run out with it, so no bubble pops up as it goes.
                    if (dome.Team != view.Team) continue;
                    var flat = new Vector2(view.Position.x - dome.Centre.x, view.Position.z - dome.Centre.z);
                    covered = flat.magnitude <= dome.Radius - 1f && view.Position.y < dome.Radius * ItemDomeHeight * 0.7f;
                }
                view.ShieldCovered = covered;
                covering |= covered;
            }
            _covering = covering;
        }

        /// <summary>
        /// Builds the shield meshes and draws a speck of shield for a moment under the loading
        /// screen, so the first one to come up mid-battle does not stall the frame (Vulkan builds
        /// its pipeline on the first draw).
        /// </summary>
        private void WarmUpShields()
        {
            ShieldVisual.Prepare(ShieldVisual.Shape.Bubble, 4f);
            ShieldVisual.Prepare(ShieldVisual.Shape.Dome, 16f);
            _warmShield = new ShieldVisual("Shield Warm-up", _root, ShieldVisual.Shape.Bubble, 1f);
            _warmShield.Transform.position = _camera.Focus + Vector3.up * 0.5f;
            _warmShield.Transform.localScale = Vector3.one * 0.01f;
            _warmShield.Raise(Time.time, 0f);
            _warmShieldUntil = Time.time + 0.3f;
        }
    }
}
