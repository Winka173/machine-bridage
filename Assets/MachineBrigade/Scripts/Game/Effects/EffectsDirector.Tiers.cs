using System.Collections.Generic;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 34 L5 (DECISIONS "Prompt 34 L5/L6/L7"): rounds fire and land by their tier (<see cref="TierFx"/>). On top of
    /// what every round always drew (never cut or shrunk), a T2+ landing plays its tier's redrawn blast
    /// (<see cref="ExplosionEffect.CreateTier"/>) and a T3+ shot its tier's firing look (<see cref="MuzzleFx.TierShot"/>,
    /// the pressure wave, the dust or water ring, the light on the ground). The shockwave rings are drawn exactly on the
    /// blast's edge (T4) and on its core and then its edge (T5, two rings). Detail falls with distance and with the big
    /// blasts already going (<see cref="TierBudget"/>); the camera shakes for T4+ only, near and on screen.
    /// </summary>
    public sealed partial class EffectsDirector
    {
        /// <summary>The tier overlays, T2-T5 (T0 and T1 have none); built up front like every recipe.</summary>
        private readonly ExplosionEffect[] _tierBlasts = new ExplosionEffect[TierFx.Top + 1];

        /// <summary>The dust ring and ground light a T3+ shot throws round its gun, T3-T5.</summary>
        private readonly ExplosionEffect[] _tierFire = new ExplosionEffect[TierFx.Top + 1];

        private readonly TierBudget _tierBudget = new();

        /// <summary>When each shooter last threw its tier's ground look (a volley's other barrels and turrets draw the muzzle only).</summary>
        private readonly Dictionary<EntityId, float> _tierGround = new();

        /// <summary>A volley's barrels and a ship's turrets within this of the first throw no second ground ring, light or shake.</summary>
        private const float TierGroundGap = 0.35f;

        private static readonly Color TierShockColour = new(1.35f, 1.05f, 0.7f, 0.95f);
        private static readonly Color TierDustRingColour = new(0.8f, 0.7f, 0.55f, 0.6f);
        private static readonly Color WaterRingColour = new(0.85f, 0.95f, 1.1f, 0.7f);

        /// <summary>Tests and tools: each tier overlay played (tier, detail, position).</summary>
        internal static System.Action<int, TierFx.Detail, Vector3> TierPlayed;

        private void InitTiers()
        {
            for (var tier = 2; tier <= TierFx.Top; tier++)
            {
                _tierBlasts[tier] = ExplosionEffect.CreateTier(tier, _layers);
                _blasts.Add(_tierBlasts[tier]);
                if (tier < 3) continue;
                _tierFire[tier] = ExplosionEffect.CreateTierFire(tier, _layers);
                _blasts.Add(_tierFire[tier]);
            }
            _weapons.TierShot = TierShot;
        }

        /// <summary>The tier of the round a blast event came from when it is a salvo's (Leviathan's 406 mm), else -1.</summary>
        private int SalvoTier(in SimEvent e, ViewRegistry views)
        {
            if (!views.TryGet(e.Entity, out var source) || source.Def.Salvo?.Weapon is not { } gun) return -1;
            return _catalog.Weapons.TryGetValue(gun, out var w) ? TierFx.Of(w) : -1;
        }

        /// <summary>
        /// A round of <paramref name="tier"/> landed at <paramref name="at"/> (its core and edge radii, m): its tier's blast on
        /// top of the round's own, the exact rings, the crater, the shake and the light vehicles rocked.
        /// </summary>
        /// <param name="stick">The bomb-run fix, pass 3: the bombs of the stick this blast is one of (0: none); a long stick's far
        /// bombs get their overlay one level lighter before the budget counts them (<see cref="TierFx.StickDetail"/>).</param>
        private void TierImpact(int tier, Vector3 at, float core, float edge, float now, ViewRegistry views, int stick = 0)
        {
            if (tier < 2) return;
            var reach = edge > core ? edge : core;
            var distance = Vector3.Distance(at, _camera.Focus);
            var onScreen = _cull.Visible(at, tier >= 4 ? 0.4f : 0.25f);
            if (tier >= 4)
            {
                // The shockwave exactly on the edge (T4); T5's two rings, the core's first and the edge's after it.
                if (tier >= 5 && core > 0f && edge > core)
                {
                    TierRing(at, core, TierShockColour, 0.6f);
                    Later(now + 0.25f, () => TierRing(at, edge, TierShockColour, 0.85f));
                }
                else if (reach > 0f) TierRing(at, reach, TierShockColour, 0.7f);
                if (reach > 0f) Later(now + (tier >= 5 ? 0.4f : 0.12f), () => TierRing(at, reach, TierDustRingColour, 1.2f));
                // A big crater, very big and lasting for T5.
                // Fix prompt L6: for its band's time (45 s, 60 s for T5), closing slowly.
                _decals.Place(at, Mathf.Max(4f, (core > 0f ? core : 4f) * (tier >= 5 ? 1.5f : 1.2f)), EffectLife.Crater(tier));
                _camera.AddTierTrauma(TierFx.Shake(tier, distance, onScreen), TierFx.ShakeCap);
                RockLight(views, at, reach > 0f ? reach : 8f, tier);
                if (tier >= 5 && onScreen && Flash != null) Flash(0.16f / (1f + distance / 40f));
            }
            if (!onScreen) return;
            var detail = _tierBudget.Admit(tier, TierFx.StickDetail(TierFx.DetailAt(distance, _camera.Zoom), stick, distance), now);
            TierPlayed?.Invoke(tier, detail, at);
            var scale = TierFx.OverlayScale(tier, core);
            if (detail == TierFx.Detail.Far)
            {
                // Far off: the flash of light alone (its round's own blast still plays whole).
                _night.Blast(at, 6f * tier * scale, 0.5f);
                return;
            }
            // A lower graphics tier draws its share of the overlay too (all on High, 80 % on Medium, half on Low).
            _tierBlasts[tier].Play(at, now, scale, 1f, 1f, 0f, TierFx.ShareOf(detail) * ExplosionEffect.RichShare);
            _night.Blast(at, 6f * tier * scale, tier >= 4 ? 1.1f : 0.6f);
            if (tier >= 3 && detail == TierFx.Detail.Full)
                _fires.Ignite(at, tier >= 5 ? 2f : tier >= 4 ? 1.3f : 0.6f, tier >= 5 ? 40f : tier >= 4 ? 24f : 10f, now);
        }

        /// <summary>A T4+ blast rocks the light vehicles near it (view only): scouts, light vehicles and small hulls within its reach and a third.</summary>
        private static void RockLight(ViewRegistry views, Vector3 at, float reach, int tier)
        {
            var within = reach * 1.35f;
            foreach (var v in views.All)
            {
                if (v == null || v.Root == null || v.Flying || v.IsWreck || v.Def.Static || v.Def.Boss) continue;
                if (!(v.Def.Class is UnitClass.Scout or UnitClass.Light || v.Sim.Radius < 2.2f)) continue;
                var d = Vector3.Distance(v.Position, at);
                if (d > within) continue;
                v.Rock(at, (tier >= 5 ? 5f : 3f) * (1f - d / within) + 1f);
            }
        }

        /// <summary>A shockwave ring on the ground reaching exactly <paramref name="radius"/> m.</summary>
        private void TierRing(Vector3 at, float radius, Color colour, float life)
        {
            if (radius <= 0f || !_cull.Visible(at, 0.4f)) return;
            _layers.Shockwave.Emit(new ParticleSystem.EmitParams
            {
                position = at + Vector3.up * 0.25f, startSize = BlastSizes.RingQuad(radius), startColor = colour, startLifetime = life,
                applyShapeToPosition = false,
            }, 1);
        }

        /// <summary>A shot of a T1+ round was drawn (WeaponEffects.TierShot): its tier's firing look.</summary>
        private void TierShot(WeaponDef round, VehicleView shooter, Vector3 from, Vector3 direction, float? groundY, MuzzleFx.Anchor anchor,
            float now)
        {
            var tier = TierFx.Of(round);
            if (tier < 1) return;
            var distance = Vector3.Distance(from, _camera.Focus);
            var detail = TierFx.DetailAt(distance, _camera.Zoom);
            var share = Mathf.Max(0.3f, TierFx.ShareOf(detail) * ExplosionEffect.RichShare);
            _muzzle.TierShot(tier, from, direction, now, anchor, groundY, share);
            if (tier < 3) return;
            var look = TierFx.FireOf(tier);
            var dir = direction.sqrMagnitude > 1e-4f ? direction.normalized : Vector3.forward;
            // The hull squats back on its springs (each barrel of a volley).
            shooter?.Rock(from + dir * 5f, look.Squat);
            // One ground look per volley: the other barrels and turrets fire into the same dust.
            if (shooter != null)
            {
                if (_tierGround.TryGetValue(shooter.Id, out var last) && now - last < TierGroundGap) return;
                _tierGround[shooter.Id] = now;
                if (_tierGround.Count > 128) _tierGround.Clear();
            }
            if (look.Pressure > 0f) Pressure(from, look.Pressure, tier);
            var onWater = shooter != null && shooter.Def.Naval != null;
            if (groundY.HasValue && detail != TierFx.Detail.Far)
            {
                var ground = new Vector3(from.x, groundY.Value + 0.1f, from.z);
                if (onWater && look.Water > 0f)
                {
                    // A ship's guns flatten the water round them: a pale ring spreading out and spray blown off it.
                    TierRing(ground, look.Water * 0.5f, WaterRingColour, 0.9f);
                    if (tier >= 5) Later(now + 0.15f, () => TierRing(ground, look.Water * 0.75f, WaterRingColour, 1.1f));
                    _muzzle.WaterSpray(ground + new Vector3(dir.x, 0f, dir.z) * look.Water * 0.15f, look.Water * 0.35f,
                        Mathf.RoundToInt((tier >= 5 ? 26 : 14) * share));
                }
                else if (!onWater) _tierFire[tier].Play(ground + new Vector3(dir.x, 0f, dir.z) * 1.5f, now, 1f, 1f, 1f, 0f, share);
            }
            // The flash lights the ground round the gun at night (and the scene for T5).
            _night.Flash(from, look.Light * 0.5f);
            var onScreen = _cull.Visible(from, 0.1f);
            if (tier >= 5 && onScreen && Flash != null) Flash(0.07f / (1f + distance / 40f));
            // Play-test 12: a boss firing shakes nothing (its impacts still do, by tier).
            if (shooter == null || !shooter.Def.Boss) _camera.AddTierTrauma(TierFx.Shake(tier, distance, onScreen, shot: true), TierFx.ShakeCap);
        }

        /// <summary>The air's pressure wave round a big gun's muzzle: a ring snapping out (T5: two).</summary>
        private void Pressure(Vector3 at, float size, int tier)
        {
            if (!_cull.Visible(at, 0.2f)) return;
            _layers.AirShock.Emit(new ParticleSystem.EmitParams
            {
                position = at, startSize = size, startLifetime = 0.22f, applyShapeToPosition = false,
            }, 1);
            if (tier < 5) return;
            _layers.AirShock.Emit(new ParticleSystem.EmitParams
            {
                position = at, startSize = size * 1.5f, startLifetime = 0.34f, applyShapeToPosition = false,
            }, 1);
        }
    }
}
