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

        /// <summary>
        /// Rounds of one mount already drawn this frame: a burst faster than the simulation's step
        /// (an anti-aircraft gun's 20 rounds a second) arrives several at once, and each later
        /// one is held back by one burst interval so the stream flows out of the barrel.
        /// </summary>
        private readonly System.Collections.Generic.Dictionary<(MachineBrigade.Sim.Core.EntityId, int), (float at, int count)> _sameFrame = new();

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

        /// <summary>Tests and tools: every round's start point as it is launched (shooter, mount, point).</summary>
        internal static Action<VehicleView, int, Vector3> Launched;

        public void Fired(in SimEvent e, ViewRegistry views, float now) =>
            Fired(e, views.TryGet(e.Entity, out var shooter) ? shooter : null, views, now);

        /// <summary>A shot by <paramref name="shooter"/> (null when it is not drawn): call once the shooter is drawn this frame.</summary>
        public void Fired(in SimEvent e, VehicleView shooter, ViewRegistry views, float now)
        {
            var weapon = e.DefId != null && _catalog.Weapons.TryGetValue(e.DefId, out var w) ? w : null;
            Vector3 from;
            float? groundY = 0f;
            var pitch = float.NaN;
            var barrel = Vector3.zero;
            if (shooter != null && shooter.Root == null) shooter = null;
            if (shooter != null)
            {
                // A blow (the bulldozer's blade): the blade strokes, no flash or tracer; the impact shows the hit.
                if (weapon != null && weapon.Melee)
                {
                    shooter.BladeStroke();
                    return;
                }
                if (e.Mount == 0) shooter.Recoil();
                // The barrel is laid first, so the round leaves from where its muzzle now is.
                if (e.Mount == 0 && !shooter.Flying)
                {
                    pitch = shooter.LayForShot();
                    barrel = shooter.BarrelDirectionOf(0);
                }
                from = shooter.MuzzleOf(e.Mount);
                groundY = shooter.Flying ? null : shooter.Position.y;
                Launched?.Invoke(shooter, e.Mount, from);
            }
            else
            {
                from = new Vector3(e.Position.X, 1.5f, e.Position.Y);
            }

            var to = AimPoint(e, views);
            var mountModel = shooter != null && e.Mount < shooter.Def.Mounts.Count ? shooter.Def.Mounts[e.Mount].ProjectileModel : null;
            string Model(string fallback)
            {
                var id = mountModel ?? weapon?.ProjectileModel;
                return id != null && _models.Has(id) ? id : fallback;
            }
            var scale = weapon?.ProjectileScale ?? 1f;
            var flat = to - from;
            flat.y = 0f;
            var forward = flat.sqrMagnitude > 1e-4f ? flat.normalized : Vector3.forward;
            var distance = Vector3.Distance(from, to);
            var aim = to - from; // the barrel's direction: down from an aircraft, up at one
            var kind = weapon?.Projectile ?? (e.Tier == ExplosionTier.Small ? ProjectileKind.Bullet : ProjectileKind.Shell);
            var targetId = e.Other;
            var lag = 0f;
            if (weapon != null && weapon.Burst > 1 && weapon.BurstInterval < 0.1f)
            {
                var key = (e.Entity, e.Mount);
                var count = _sameFrame.TryGetValue(key, out var seen) && Mathf.Approximately(seen.at, now) ? seen.count + 1 : 0;
                _sameFrame[key] = (now, count);
                if (_sameFrame.Count > 256) _sameFrame.Clear();
                lag = count * weapon.BurstInterval;
            }

            if (weapon != null && weapon.Charge > 0f && kind == ProjectileKind.Bullet)
            {
                Rail(weapon, from, to, aim, groundY, e.Value, now, Model(null));
                return;
            }
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
                    Bullets(weapon, from, to, aim, groundY, e.Value, now, lag);
                    break;

                case ProjectileKind.Missile:
                    // Guided: the missile bends towards wherever its target is now.
                    // It leaves the rail slowly and speeds up (launch, then boost), arriving on time.
                    var missile = Model("missile");
                    if (_hasMissile) _projectiles.Launch(_models.Merged(missile), from, to, e.Value, distance * 0.06f, 0.7f, now, Homing(views, targetId),
                        boost: 0.55f, scale: scale * SizeOf(weapon, kind, missile, shooter != null && shooter.Flying));
                    else _tracers.Launch(from, to, e.Value, distance * 0.06f, 0.2f, 1.2f, now, 0f, 0.7f);
                    _muzzle.Fire(MuzzleFx.Kind.Missile, from, aim, now, 1f, groundY);
                    _shake(from, 0.05f);
                    break;

                case ProjectileKind.Drone:
                    // A kamikaze drone climbs off the rack, then dives onto whatever it was sent at.
                    var drone = Model(_models.Has("fpv_drone") ? "fpv_drone" : _hasMissile ? "missile" : null);
                    if (drone != null) _projectiles.Launch(_models.Merged(drone), from, to, e.Value, distance * 0.12f, 0.35f, now, Homing(views, targetId), wobble: 0.6f,
                        scale: scale * SizeOf(weapon, kind, drone, false));
                    else _tracers.Launch(from, to, e.Value, distance * 0.12f, 0.15f, 0.8f, now, 0f, 0.4f);
                    _muzzle.Fire(MuzzleFx.Kind.Missile, from, aim, now, 0.5f, groundY);
                    break;

                case ProjectileKind.Rocket:
                    var artillery = weapon != null && weapon.MinRange > 0f;
                    var arc = artillery ? ArcFor(pitch, distance, 0.28f) : distance * 0.02f;
                    // Heavy rockets and ballistic missiles fly their own models where they exist.
                    var rocket = Model(weapon?.Id switch
                    {
                        "rockets_300mm" when _models.Has("heavy_rocket") => "heavy_rocket",
                        "ballistic_missile" when _models.Has("ballistic_missile") => "ballistic_missile",
                        _ => "rocket",
                    });
                    if (weapon?.Id == "ballistic_missile") arc = distance * 0.45f;
                    if (_hasRocket) _projectiles.Launch(_models.Merged(rocket), from, to, e.Value, arc, 0.55f, now, wobble: artillery ? 0.7f : 0.3f,
                        boost: artillery ? 0.2f : 0.3f, scale: scale * SizeOf(weapon, kind, rocket, false),
                        control: artillery && weapon.Id != "ballistic_missile" ? Bend(from, to, barrel) : null);
                    else _tracers.Launch(from, to, e.Value, arc, 0.18f, 1.0f, now, 0f, 0.55f);
                    _muzzle.Fire(MuzzleFx.Kind.Rocket, from, artillery ? Launch(barrel, forward, 0.8f) : aim, now, artillery ? 1.2f : 0.9f, groundY);
                    _shake(from, artillery ? 0.06f : 0.03f);
                    break;

                case ProjectileKind.Bomb:
                    // Released from the wing: it keeps some forward speed and falls onto the target.
                    if (_hasBomb) _projectiles.Launch(_models.Merged(Model("bomb")), from, to, Mathf.Max(0.4f, e.Value), 0f, 0f, now, scale: scale);
                    else _tracers.Launch(from, to, e.Value, 0f, 0.3f, 1f, now);
                    break;

                case ProjectileKind.Flame:
                    _emitters.FlameJet(from, to, Mathf.Max(0.15f, e.Value), weapon != null ? Mathf.Clamp(weapon.Cooldown, 0.1f, 0.4f) : 0.25f, now);
                    _muzzle.Fire(MuzzleFx.Kind.MachineGun, from, aim, now, 0.8f, groundY);
                    break;

                default:
                    Shells(weapon, e, from, to, forward, aim, groundY, distance, now, pitch, barrel, Model(null), scale);
                    break;
            }
        }

        /// <summary>
        /// A railgun (or the saucer's coilgun) lets go: a white core beam that hangs for a moment
        /// and thins away, a wider glow round it, a plasma blast and a cone of sparks at the
        /// muzzle, the slug riding the head of the beam; the barrel's charge glow is over.
        /// </summary>
        private void Rail(WeaponDef weapon, Vector3 from, Vector3 to, Vector3 aim, float? groundY, float travel, float now, string slug)
        {
            var heavy = weapon.Damage >= 300f;
            _tracers.Beam(from, to, 0.1f, heavy ? 0.22f : 0.14f, now);
            _tracers.Beam(from, to, 0.35f, heavy ? 0.11f : 0.07f, now, 0.1f);
            _tracers.Beam(from, to, 0.5f, heavy ? 0.05f : 0.035f, now, 0.45f);
            if (slug != null) _projectiles.Launch(_models.Merged(slug), from, to, Mathf.Max(0.08f, travel), 0f, 0.4f, now);
            _muzzle.Fire(MuzzleFx.Kind.Cannon, from, aim, now, heavy ? 1.8f : 1.2f, groundY);
            _muzzle.SparkBurst(from, aim.normalized, heavy ? 40 : 20, 12f, 30f);
            // Ionised air along the line, drifting off.
            var length = Vector3.Distance(from, to);
            for (var d = 3f; d < length; d += 4f) _emitters.Trail(Vector3.Lerp(from, to, d / length), heavy ? 0.5f : 0.35f);
            _shake(from, heavy ? 0.12f : 0.06f);
        }

        /// <summary>
        /// A charged weapon powering up: sparks drawn into the muzzle, a glow at the barrel's end
        /// that grows until it fires (see <see cref="Rail"/>).
        /// </summary>
        public void Charging(in SimEvent e, ViewRegistry views, float now) =>
            Charging(e, views.TryGet(e.Entity, out var shooter) ? shooter : null, now);

        /// <summary>A charge starting on <paramref name="shooter"/>: call once the shooter is drawn this frame.</summary>
        public void Charging(in SimEvent e, VehicleView shooter, float now)
        {
            if (shooter == null || shooter.Root == null) return;
            var muzzle = shooter.MuzzleOf(e.Mount);
            var back = -shooter.DirectionOf(e.Mount);
            _charges.Add((shooter, e.Mount, now, now + e.Value));

            _muzzle.SparkBurst(muzzle + back * 0.4f, back, 6, 1f, 3f, 0.6f);
        }

        private readonly System.Collections.Generic.List<(VehicleView view, int mount, float start, float end)> _charges = new();

        /// <summary>Per frame: charged weapons glow brighter and draw sparks in, faster towards the shot.</summary>
        public void Tick(float now)
        {
            for (var i = _charges.Count - 1; i >= 0; i--)
            {
                var (view, mount, start, end) = _charges[i];
                if (now >= end || view == null || view.Root == null)
                {

                    _charges.RemoveAt(i);
                    continue;
                }
                var k = Mathf.InverseLerp(start, end, now);
                var muzzle = view.MuzzleOf(mount);
                var dir = view.DirectionOf(mount);
                // The coils along the barrel light up one after another, breech to muzzle, and a
                // ball of light swells at the muzzle, flickering faster towards the shot.
                // (A little above the rails, so the glow is never buried in the barrel it sits on.)
                var lift = Vector3.up * 0.35f;
                for (var coil = 0; coil < 5; coil++)
                    if (k >= coil / 5f)
                        _emitters.Charge(muzzle - dir * (0.8f * (4 - coil)) + lift, 0.5f + 0.2f * k);
                var flicker = 0.85f + 0.3f * Mathf.Sin(now * (18f + 40f * k));
                _emitters.Charge(muzzle + dir * 0.4f + lift, Mathf.Lerp(0.6f, 1.9f, k) * flicker);
                var sparks = Mathf.RoundToInt(1 + 3 * k);
                for (var s = 0; s < sparks; s++)
                {
                    var ring = UnityEngine.Random.onUnitSphere * (1.6f - 0.8f * k);
                    _muzzle.SparkBurst(muzzle + ring, -ring.normalized, 1, 3f + 5f * k, 6f + 8f * k, 0.6f);
                }
            }
        }

        /// <summary>
        /// How much bigger than its model a flying munition is drawn, on top of the weapon's own
        /// projectileScale, so it reads at battle zoom: small anti-tank missiles and shoulder-fired
        /// SAMs 10 %, rockets 15 %, air-launched, surface-to-air and cruise missiles 20 %; drones
        /// sent off a drone vehicle (FPV, Lancet, Shahed, the mothership's) are drawn twice their size.
        /// </summary>
        internal static float SizeOf(WeaponDef weapon, ProjectileKind kind, string model, bool airLaunched)
        {
            switch (kind)
            {
                case ProjectileKind.Drone:
                    return 2f;
                case ProjectileKind.Rocket:
                    return 1.15f;
                case ProjectileKind.Missile:
                    if (model is "stinger" or "igla") return 1.1f;
                    if (airLaunched || model is "cruise_missile" or "jassm") return 1.2f;
                    return weapon != null && weapon.CanTarget(true) && !weapon.CanTarget(false) ? 1.2f : 1.1f;
                default:
                    return 1f;
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

        private void Bullets(WeaponDef weapon, Vector3 from, Vector3 to, Vector3 aim, float? groundY, float travel, float now, float lag = 0f)
        {
            var damage = weapon?.Damage ?? 9f;
            var forward = new Vector3(aim.x, 0f, aim.z);
            forward = forward.sqrMagnitude > 1e-4f ? forward.normalized : Vector3.forward;
            var side = Vector3.Cross(Vector3.up, forward);
            // Light machine guns show a pair of tracers per burst (nearly every vehicle carries one
            // now, firing five bursts a second); cannons one heavier tracer per shot.
            var rounds = damage < 12f ? 2 : 1;
            // Rifle-calibre tracers are fine streaks; autocannon ones a little heavier.
            var thickness = Mathf.Lerp(0.026f, 0.11f, Mathf.InverseLerp(6f, 30f, damage));
            var length = Mathf.Lerp(0.75f, 1.9f, Mathf.InverseLerp(6f, 30f, damage));
            for (var i = 0; i < rounds; i++)
            {
                var scatter = rounds > 1 ? side * UnityEngine.Random.Range(-0.7f, 0.7f) + forward * UnityEngine.Random.Range(-0.6f, 0.9f) : Vector3.zero;
                _tracers.Launch(from, to + scatter, travel, 0f, thickness, length, now, lag + i * MuzzleFx.RoundInterval);
            }
            // Later rounds of the same frame's burst: the flash of the first stands for them.
            if (lag > 0f) return;
            if (rounds > 1) _muzzle.Fire(MuzzleFx.Kind.MachineGun, from, aim, now, 1f, groundY);
            else _muzzle.Fire(MuzzleFx.Kind.Autocannon, from, aim, now, Mathf.Lerp(0.85f, 1.2f, Mathf.InverseLerp(12f, 30f, damage)), groundY);
        }

        /// <summary>
        /// The peak height of a lobbed round's path that leaves at the barrel's angle: the path
        /// rises at 4 x peak / distance at the start, so the peak is distance x tan(angle) / 4.
        /// Without a barrel angle, the old fixed share of the distance.
        /// </summary>
        private static float ArcFor(float pitch, float distance, float fallback)
        {
            if (float.IsNaN(pitch)) return distance * fallback;
            return distance * Mathf.Tan(Mathf.Clamp(pitch, 12f, 80f) * Mathf.Deg2Rad) * 0.25f;
        }

        /// <summary>
        /// The middle point of a lobbed round's curve that leaves along its drawn barrel: the aim
        /// point is scattered (and artillery brackets), so the round lands up to ten degrees off
        /// the line the barrel was laid on; the plain arc left the barrel sideways, away from its
        /// blast. Half the ground distance out along the barrel gives the arc's own height (the
        /// barrel's angle), and the curve then bends onto where the round lands. Null for a barrel
        /// that is not raised (the plain arc).
        /// </summary>
        internal static Vector3? Bend(Vector3 from, Vector3 to, Vector3 barrel)
        {
            if (barrel.sqrMagnitude < 0.01f || barrel.y < 0.05f) return null;
            barrel.Normalize();
            var flat = new Vector2(barrel.x, barrel.z).magnitude;
            var ground = new Vector2(to.x - from.x, to.z - from.z).magnitude;
            if (flat < 0.1f || ground < 1f) return null;
            return from + barrel * (0.5f * ground / flat);
        }

        /// <summary>The way a lobbing weapon's blast goes: up its barrel, else the old fixed slant.</summary>
        private static Vector3 Launch(Vector3 barrel, Vector3 forward, float rise) =>
            barrel.sqrMagnitude > 0.01f && barrel.y > 0.05f ? barrel : forward + Vector3.up * rise;

        private void Shells(WeaponDef weapon, in SimEvent e, Vector3 from, Vector3 to, Vector3 forward, Vector3 aim, float? groundY,
            float distance, float now, float pitch, Vector3 barrel, string model = null, float scale = 1f)
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
            // Artillery: a high arc, leaving at the barrel's angle, with a thin trail of hot gas;
            // the shell or mortar bomb itself where it has a model.
            if (model != null)
                _projectiles.Launch(_models.Merged(model), from, to, e.Value, ArcFor(pitch, distance, 0.3f), 0.35f, now, scale: scale,
                    control: Bend(from, to, barrel));
            else _tracers.Launch(from, to, e.Value, ArcFor(pitch, distance, 0.3f), 0.32f, 1.1f, now, 0f, 0.55f);
            _muzzle.Fire(MuzzleFx.Kind.Artillery, from, Launch(barrel, forward, 0.9f), now, 1f, groundY);
            _shake(from, 0.12f);
        }
    }
}
