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
    /// Every shot starts at its own mount's muzzle (coaxial gun, roof gun, launcher), with fire
    /// and smoke at the barrel (<see cref="MuzzleFx"/>) for vehicles and aircraft alike.
    /// </summary>
    internal sealed class WeaponEffects
    {
        private readonly Catalog _catalog;
        private readonly ModelLibrary _models;
        private readonly TracerPool _tracers;
        private readonly ProjectilePool _projectiles;
        private readonly Emitters _emitters;
        private readonly MuzzleFx _muzzle;
        private readonly Action<Vector3, float> _shake;
        private readonly bool _hasMissile, _hasRocket, _hasBomb;

        public WeaponEffects(Catalog catalog, ModelLibrary models, TracerPool tracers, ProjectilePool projectiles, Emitters emitters,
            MuzzleFx muzzle, Action<Vector3, float> shake)
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
            _hasBomb = models.Has("bomb");
        }

        public void Fired(in SimEvent e, ViewRegistry views, float now)
        {
            var weapon = e.DefId != null && _catalog.Weapons.TryGetValue(e.DefId, out var w) ? w : null;
            Vector3 from;
            float? groundY = 0f;
            if (views.TryGet(e.Entity, out var shooter))
            {
                if (e.Mount == 0) shooter.Recoil();
                from = shooter.MuzzleOf(e.Mount);
                groundY = shooter.Flying ? null : shooter.Position.y;
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
            var aim = to - from; // the barrel's direction: down from an aircraft, up at one
            var kind = weapon?.Projectile ?? (e.Tier == ExplosionTier.Small ? ProjectileKind.Bullet : ProjectileKind.Shell);
            var targetId = e.Other;

            if (weapon != null && weapon.Beam)
            {
                // A laser: a hard bright bar for a moment, the glow of the director at the muzzle.
                _tracers.Beam(from, to, 0.08f, 0.09f, now);
                _muzzle.Fire(MuzzleFx.Kind.MachineGun, from, aim, now, 0.6f, groundY);
                return;
            }
            switch (kind)
            {
                case ProjectileKind.Bullet:
                    Bullets(weapon, from, to, aim, groundY, e.Value, now);
                    break;

                case ProjectileKind.Missile:
                    // Guided: the missile bends towards wherever its target is now.
                    if (_hasMissile) _projectiles.Launch(_models.Merged("missile"), from, to, e.Value, distance * 0.06f, 0.7f, now, Homing(views, targetId));
                    else _tracers.Launch(from, to, e.Value, distance * 0.06f, 0.2f, 1.2f, now, 0f, 0.7f);
                    _muzzle.Fire(MuzzleFx.Kind.Missile, from, aim, now, 1f, groundY);
                    _shake(from, 0.05f);
                    break;

                case ProjectileKind.Drone:
                    // A kamikaze drone climbs off the rack, then dives onto whatever it was sent at.
                    var drone = _models.Has("fpv_drone") ? "fpv_drone" : _hasMissile ? "missile" : null;
                    if (drone != null) _projectiles.Launch(_models.Merged(drone), from, to, e.Value, distance * 0.12f, 0.35f, now, Homing(views, targetId), wobble: 0.6f);
                    else _tracers.Launch(from, to, e.Value, distance * 0.12f, 0.15f, 0.8f, now, 0f, 0.4f);
                    _muzzle.Fire(MuzzleFx.Kind.Missile, from, aim, now, 0.5f, groundY);
                    break;

                case ProjectileKind.Rocket:
                    var artillery = weapon != null && weapon.MinRange > 0f;
                    var arc = artillery ? distance * 0.28f : distance * 0.02f;
                    // Heavy rockets and ballistic missiles fly their own models where they exist.
                    var rocket = weapon?.Id switch
                    {
                        "rockets_300mm" when _models.Has("heavy_rocket") => "heavy_rocket",
                        "ballistic_missile" when _models.Has("ballistic_missile") => "ballistic_missile",
                        _ => "rocket",
                    };
                    if (weapon?.Id == "ballistic_missile") arc = distance * 0.45f;
                    if (_hasRocket) _projectiles.Launch(_models.Merged(rocket), from, to, e.Value, arc, 0.55f, now, wobble: artillery ? 0.7f : 0.3f);
                    else _tracers.Launch(from, to, e.Value, arc, 0.18f, 1.0f, now, 0f, 0.55f);
                    _muzzle.Fire(MuzzleFx.Kind.Rocket, from, artillery ? forward + Vector3.up * 0.8f : aim, now, artillery ? 1.2f : 0.9f, groundY);
                    _shake(from, artillery ? 0.06f : 0.03f);
                    break;

                case ProjectileKind.Bomb:
                    // Released from the wing: it keeps some forward speed and falls onto the target.
                    if (_hasBomb) _projectiles.Launch(_models.Merged("bomb"), from, to, Mathf.Max(0.4f, e.Value), 0f, 0f, now);
                    else _tracers.Launch(from, to, e.Value, 0f, 0.3f, 1f, now);
                    break;

                case ProjectileKind.Flame:
                    _emitters.FlameJet(from, to, Mathf.Max(0.15f, e.Value));
                    _muzzle.Fire(MuzzleFx.Kind.MachineGun, from, aim, now, 0.8f, groundY);
                    break;

                default:
                    Shells(weapon, e, from, to, forward, aim, groundY, distance, now);
                    break;
            }
        }

        /// <summary>The live aim point of a guided missile (built only for missiles, so other shots allocate nothing).</summary>
        private static Func<Vector3?> Homing(ViewRegistry views, MachineBrigade.Sim.Core.EntityId targetId) =>
            () => views.TryGet(targetId, out var target) ? target.Position + Vector3.up * (target.Flying ? 0.5f : 1f) : (Vector3?)null;

        /// <summary>Where the shot visibly goes: aircraft are hit at their flight height.</summary>
        public static Vector3 AimPoint(in SimEvent e, ViewRegistry views)
        {
            var height = views.TryGet(e.Other, out var target) && target.Flying ? target.Altitude + 0.4f : 0.4f;
            return new Vector3(e.Target.X, height, e.Target.Y);
        }

        private void Bullets(WeaponDef weapon, Vector3 from, Vector3 to, Vector3 aim, float? groundY, float travel, float now)
        {
            var damage = weapon?.Damage ?? 9f;
            var forward = new Vector3(aim.x, 0f, aim.z);
            forward = forward.sqrMagnitude > 1e-4f ? forward.normalized : Vector3.forward;
            var side = Vector3.Cross(Vector3.up, forward);
            // Light machine guns show a pair of tracers per burst (nearly every vehicle carries one
            // now, firing five bursts a second); cannons one heavier tracer per shot.
            var rounds = damage < 12f ? 2 : 1;
            // Rifle-calibre tracers are thin streaks; autocannon ones a little heavier.
            var thickness = Mathf.Lerp(0.05f, 0.12f, Mathf.InverseLerp(6f, 30f, damage));
            var length = Mathf.Lerp(1.1f, 2.0f, Mathf.InverseLerp(6f, 30f, damage));
            for (var i = 0; i < rounds; i++)
            {
                var scatter = rounds > 1 ? side * UnityEngine.Random.Range(-0.7f, 0.7f) + forward * UnityEngine.Random.Range(-0.6f, 0.9f) : Vector3.zero;
                _tracers.Launch(from, to + scatter, travel, 0f, thickness, length, now, i * MuzzleFx.RoundInterval);
            }
            if (rounds > 1) _muzzle.Fire(MuzzleFx.Kind.MachineGun, from, aim, now, 1f, groundY);
            else _muzzle.Fire(MuzzleFx.Kind.Autocannon, from, aim, now, Mathf.Lerp(0.85f, 1.2f, Mathf.InverseLerp(12f, 30f, damage)), groundY);
        }

        private void Shells(WeaponDef weapon, in SimEvent e, Vector3 from, Vector3 to, Vector3 forward, Vector3 aim, float? groundY,
            float distance, float now)
        {
            // Only guns that lob their shells (artillery with a minimum range, howitzers) fly an arc;
            // a tank or turret gun fires straight down its barrel however big its shell is.
            var lobs = weapon != null ? weapon.Indirect || weapon.Id.Contains("howitzer") : e.Tier > ExplosionTier.Medium;
            if (!lobs)
            {
                var heavy = weapon != null && weapon.Damage >= 100f;
                var big = e.Tier >= ExplosionTier.Large;
                _tracers.Launch(from, to, e.Value, 0f, big ? 0.28f : heavy ? 0.22f : 0.16f, big ? 3.6f : heavy ? 3.2f : 2.6f, now, 0f,
                    big ? 1.1f : heavy ? 0.95f : 0.75f);
                _muzzle.Fire(MuzzleFx.Kind.Cannon, from, aim, now, big ? 1.5f : heavy ? 1.25f : 1f, groundY);
                _shake(from, big ? 0.1f : heavy ? 0.08f : 0.05f);
                return;
            }
            // Artillery: a high arc with a thick trail.
            _tracers.Launch(from, to, e.Value, distance * 0.3f, 0.32f, 1.1f, now, 0f, 1.2f);
            _muzzle.Fire(MuzzleFx.Kind.Artillery, from, forward + Vector3.up * 0.9f, now, 1f, groundY);
            _shake(from, 0.12f);
        }
    }
}
