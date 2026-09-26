using System;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// What a shot looks like, by what the weapon fires: machine-gun bursts and autocannon
    /// tracers, tank shells with smoke trails, arcing artillery, missiles that home in with a
    /// burning motor, rocket salvos that corkscrew out of their pods, and flamethrower streams.
    /// Every shot starts at its own mount's muzzle (coaxial gun, roof gun, launcher).
    /// </summary>
    internal sealed class WeaponEffects
    {
        private readonly Catalog _catalog;
        private readonly ModelLibrary _models;
        private readonly TracerPool _tracers;
        private readonly ProjectilePool _projectiles;
        private readonly Emitters _emitters;
        private readonly EffectPool _muzzle;
        private readonly Action<Vector3, float> _shake;
        private readonly bool _hasMissile, _hasRocket;

        public WeaponEffects(Catalog catalog, ModelLibrary models, TracerPool tracers, ProjectilePool projectiles, Emitters emitters,
            EffectPool muzzle, Action<Vector3, float> shake)
        {
            _catalog = catalog;
            _models = models;
            _tracers = tracers;
            _projectiles = projectiles;
            _emitters = emitters;
            _muzzle = muzzle;
            _shake = shake;
            _hasMissile = models.Has("missile");
            _hasRocket = models.Has("rocket");
        }

        public void Fired(in SimEvent e, ViewRegistry views, float now)
        {
            var weapon = e.DefId != null && _catalog.Weapons.TryGetValue(e.DefId, out var w) ? w : null;
            Vector3 from;
            if (views.TryGet(e.Entity, out var shooter))
            {
                if (e.Mount == 0) shooter.Recoil();
                from = shooter.MuzzleOf(e.Mount);
            }
            else
            {
                from = new Vector3(e.Position.X, 1.5f, e.Position.Y);
            }

            var to = AimPoint(e, views);
            var flat = to - from;
            flat.y = 0f;
            var forward = flat.sqrMagnitude > 1e-4f ? flat.normalized : Vector3.forward;
            var distance = Vector3.Distance(from, to);
            var kind = weapon?.Projectile ?? (e.Tier == ExplosionTier.Small ? ProjectileKind.Bullet : ProjectileKind.Shell);
            var targetId = e.Other;

            switch (kind)
            {
                case ProjectileKind.Bullet:
                    Bullets(weapon, from, to, forward, e.Value, now);
                    break;

                case ProjectileKind.Missile:
                    // Guided: the missile bends towards wherever its target is now.
                    Func<Vector3?> homing = () =>
                        views.TryGet(targetId, out var target) ? target.Position + Vector3.up * (target.Flying ? 0.5f : 1f) : (Vector3?)null;
                    if (_hasMissile) _projectiles.Launch(_models.Merged("missile"), from, to, e.Value, distance * 0.06f, 0.7f, now, homing);
                    else _tracers.Launch(from, to, e.Value, distance * 0.06f, 0.2f, 1.2f, now, 0f, 0.7f);
                    _emitters.MuzzleSmoke(from, -forward, 0.9f); // back-blast
                    _muzzle.Acquire(now).Play(from, now, 0.6f);
                    _shake(from, 0.05f);
                    break;

                case ProjectileKind.Rocket:
                    var artillery = weapon != null && weapon.MinRange > 0f;
                    var arc = artillery ? distance * 0.28f : distance * 0.02f;
                    if (_hasRocket) _projectiles.Launch(_models.Merged("rocket"), from, to, e.Value, arc, 0.55f, now, wobble: artillery ? 0.7f : 0.3f);
                    else _tracers.Launch(from, to, e.Value, arc, 0.18f, 1.0f, now, 0f, 0.55f);
                    _emitters.MuzzleSmoke(from, forward + Vector3.up * (artillery ? 0.8f : 0.1f), artillery ? 1.4f : 0.8f);
                    _muzzle.Acquire(now).Play(from, now, 0.55f);
                    _shake(from, artillery ? 0.06f : 0.03f);
                    break;

                case ProjectileKind.Flame:
                    _emitters.FlameJet(from, to, Mathf.Max(0.15f, e.Value));
                    break;

                default:
                    Shells(weapon, e, from, to, forward, distance, now);
                    break;
            }
        }

        /// <summary>Where the shot visibly goes: aircraft are hit at their flight height.</summary>
        public static Vector3 AimPoint(in SimEvent e, ViewRegistry views)
        {
            var height = views.TryGet(e.Other, out var target) && target.Flying ? target.Altitude + 0.4f : 0.4f;
            return new Vector3(e.Target.X, height, e.Target.Y);
        }

        private void Bullets(WeaponDef weapon, Vector3 from, Vector3 to, Vector3 forward, float travel, float now)
        {
            var damage = weapon?.Damage ?? 9f;
            var side = Vector3.Cross(Vector3.up, forward);
            // Light machine guns show a burst of three; cannons one heavier tracer per shot.
            var rounds = damage < 12f ? 3 : 1;
            var thickness = Mathf.Lerp(0.08f, 0.17f, Mathf.InverseLerp(6f, 30f, damage));
            var length = Mathf.Lerp(1.6f, 2.6f, Mathf.InverseLerp(6f, 30f, damage));
            for (var i = 0; i < rounds; i++)
            {
                var scatter = rounds > 1 ? side * UnityEngine.Random.Range(-0.7f, 0.7f) + forward * UnityEngine.Random.Range(-0.6f, 0.9f) : Vector3.zero;
                _tracers.Launch(from, to + scatter, travel, 0f, thickness, length, now, i * 0.055f);
            }
            _muzzle.Acquire(now).Play(from, now, Mathf.Lerp(0.4f, 0.8f, Mathf.InverseLerp(6f, 30f, damage)));
            if (damage >= 20f) _emitters.MuzzleSmoke(from, forward, 0.5f);
        }

        private void Shells(WeaponDef weapon, in SimEvent e, Vector3 from, Vector3 to, Vector3 forward, float distance, float now)
        {
            if (e.Tier <= ExplosionTier.Medium)
            {
                var heavy = weapon != null && weapon.Damage >= 100f;
                _tracers.Launch(from, to, e.Value, 0f, heavy ? 0.22f : 0.16f, heavy ? 3.2f : 2.6f, now, 0f, heavy ? 0.95f : 0.75f);
                _emitters.MuzzleSmoke(from, forward, heavy ? 1.3f : 1f);
                _muzzle.Acquire(now).Play(from, now, heavy ? 1.2f : 1f);
                _shake(from, heavy ? 0.08f : 0.05f);
                return;
            }
            // Artillery: a high arc with a thick trail.
            _tracers.Launch(from, to, e.Value, distance * 0.3f, 0.32f, 1.1f, now, 0f, 1.2f);
            _emitters.MuzzleSmoke(from, forward + Vector3.up * 0.6f, 1.7f);
            _muzzle.Acquire(now).Play(from, now, 1.4f);
            _shake(from, 0.12f);
        }
    }
}
