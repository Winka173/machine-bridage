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
        private readonly LaserBeams _lasers;
        private readonly bool _hasMissile, _hasRocket, _hasBomb, _hasFlak;

        /// <summary>
        /// Rounds of one mount already drawn this frame: a burst faster than the simulation's step
        /// (an anti-aircraft gun's 20 rounds a second) arrives several at once, and each later
        /// one is held back by one burst interval so the stream flows out of the barrel.
        /// </summary>
        private readonly System.Collections.Generic.Dictionary<(MachineBrigade.Sim.Core.EntityId, int), (float at, int count)> _sameFrame = new();

        public WeaponEffects(Catalog catalog, ModelLibrary models, TracerPool tracers, ProjectilePool projectiles, Emitters emitters,
            MuzzleFx muzzle, Action<Vector3, float> shake, LaserBeams lasers = null)
        {
            _lasers = lasers;
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
            _hasFlak = models.Has(FlakModel);
            // Test feedback 19P: a jammed round losing its lock: a crackle of sparks and a flicker of light on it.
            projectiles.Jammed = (at, forward) =>
            {
                _muzzle.SparkBurst(at, Vector3.up - forward * 0.5f, 14, 3f, 9f, 0.8f);
                _emitters.Charge(at, 1.3f);
                _emitters.Charge(at + Vector3.up * 0.2f, 0.9f);
            };
        }

        /// <summary>
        /// Test feedback 19P: where a guided round that will miss comes down, off its target (the sim's miss), and
        /// when along its flight it bends away: a jammed one early (its lock goes as it reaches the jammer's field),
        /// one that lost its lock late.
        /// </summary>
        /// <summary>
        /// An FPV quadcopter was drawn a third bigger than other drones so its X of arms and rotors read at a glance;
        /// play-test 5 (DECISIONS 20V) made it a fifth smaller again (1.3 x 0.8), on a finer model that still reads.
        /// </summary>
        internal const float QuadScale = 1.3f * 0.8f;

        private void Veer(in SimEvent e, ViewRegistry views, MachineBrigade.Sim.Core.EntityId targetId)
        {
            if (e.Offset == default) return;
            var flies = views.TryGet(targetId, out var aimed) && aimed.Flying;
            _projectiles.Veer(new Vector3(e.Offset.X, flies ? 0f : -0.7f, e.Offset.Y), e.Jammed ? 0.35f : 0.6f, e.Jammed);
        }

        /// <summary>Tests and tools: every round's start point as it is launched (shooter, mount, point).</summary>
        internal static Action<VehicleView, int, Vector3> Launched;

        /// <summary>Tests: false points gun flashes at the aim point (the old behaviour) instead of along the drawn barrel.</summary>
        internal static bool AlongBarrel = true;

        /// <summary>The part the current shot's muzzle is drawn on, and its barrel as drawn (zero without a shooter).</summary>
        private Transform _shotNode;
        private Vector3 _shotBarrel;

        /// <summary>The way a gun's flash faces: along its barrel as drawn, else at the aim point.</summary>
        private Vector3 Barrel(Vector3 aim) => AlongBarrel && _shotBarrel.sqrMagnitude > 0.5f ? _shotBarrel : aim;

        /// <summary>The muzzle flash of the current shot, riding the part its muzzle is drawn on.</summary>
        private void Flash(MuzzleFx.Kind kind, Vector3 from, Vector3 direction, float now, float scale, float? groundY)
        {
            var anchor = new MuzzleFx.Anchor(_shotNode, from, direction);
            _muzzle.Fire(kind, from, direction, now, anchor, scale, groundY);
            // Prompt 34 L5: the first flash of the shot is where its tier's firing look goes (TierShot).
            if (_flashed) return;
            _flashed = true;
            _flashFrom = from;
            _flashDir = direction;
            _flashGround = groundY;
            _flashAnchor = anchor;
        }

        /// <summary>
        /// Prompt 34 L5: called after a shot of a T1+ round is drawn with a muzzle flash: the round, the shooter (null when
        /// not drawn), where the flash is and which way it faces, the ground under it (null in the air), its anchor and the
        /// time. EffectsDirector.Tiers draws the tier's firing look there.
        /// </summary>
        internal TierShotHandler TierShot { get; set; }

        internal delegate void TierShotHandler(WeaponDef round, VehicleView shooter, Vector3 from, Vector3 direction, float? groundY,
            MuzzleFx.Anchor anchor, float now);

        private bool _flashed;
        private Vector3 _flashFrom, _flashDir;
        private float? _flashGround;
        private MuzzleFx.Anchor _flashAnchor;

        /// <summary>
        /// Prompt 34 L4: seconds the shot being drawn is late (a simultaneous volley's later barrel, drawn
        /// <see cref="MachineBrigade.Sim.Content.WeaponDef.BarrelGap"/> after the one before): its shell flies that much less.
        /// </summary>
        internal float TravelCut { get; set; }

        /// <summary>Play-test 12: the shot being drawn is a boss's (its firing shakes nothing).</summary>
        private bool _bossFiring;

        /// <summary>The camera's kick from a shot fired at <paramref name="from"/>; none for a boss's.</summary>
        private void FiringShake(Vector3 from, float amount)
        {
            if (!_bossFiring) _shake(from, amount);
        }

        public void Fired(in SimEvent e, ViewRegistry views, float now) =>
            Fired(e, views.TryGet(e.Entity, out var shooter) ? shooter : null, views, now);

        /// <summary>A shot by <paramref name="shooter"/> (null when it is not drawn): call once the shooter is drawn this frame.</summary>
        public void Fired(in SimEvent e, VehicleView shooter, ViewRegistry views, float now)
        {
            _flashed = false;
            // Play-test 12: a boss's own guns never shake the camera (its rounds' impacts still do, by tier).
            _bossFiring = shooter != null && shooter.Def != null && shooter.Def.Boss;
            DrawShot(e, shooter, views, now);
            if (!_flashed || TierShot == null) return;
            var drawn = e.Round ?? e.DefId;
            if (drawn == null || !_catalog.Weapons.TryGetValue(drawn, out var round) || round.Tier < 1) return;
            TierShot(round, shooter != null && shooter.Root != null ? shooter : null, _flashFrom, _flashDir, _flashGround, _flashAnchor, now);
        }

        private void DrawShot(in SimEvent e, VehicleView shooter, ViewRegistry views, float now)
        {
            // Prompt 25 G: a second round (the air-burst round, the HE) is drawn as that round.
            var drawn = e.Round ?? e.DefId;
            var weapon = drawn != null && _catalog.Weapons.TryGetValue(drawn, out var w) ? w : null;
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
                if (e.Mount != 0) shooter.LaySideLauncher(e.Mount);
                from = shooter.MuzzleOf(e.Mount);
                _shotNode = shooter.LastMuzzleNode;
                _shotBarrel = shooter.DrawnBarrelOf(e.Mount);
                groundY = shooter.Flying ? null : shooter.Position.y;
                Launched?.Invoke(shooter, e.Mount, from);
            }
            else
            {
                from = new Vector3(e.Position.X, 1.5f, e.Position.Y);
                _shotNode = null;
                _shotBarrel = Vector3.zero;
            }

            var to = AimPoint(e, views);
            var mountModel = shooter != null && e.Mount < shooter.Def.Mounts.Count ? shooter.Def.Mounts[e.Mount].ProjectileModel : null;
            string Model(string fallback)
            {
                var id = mountModel ?? weapon?.ProjectileModel;
                if (id != null && !_models.Has(id) && RoundStandIns.TryGetValue(id, out var standIn)) id = standIn;
                return id != null && _models.Has(id) ? id : fallback;
            }
            var scale = weapon?.ProjectileScale ?? 1f;
            // Prompt 25 B3: a round with a length in the data is drawn that long whichever model flies it.
            float Sized(string id) => id == null ? scale : RoundScale(weapon, _models.Merged(id).Mesh.bounds.size.z);
            var flat = to - from;
            flat.y = 0f;
            var forward = flat.sqrMagnitude > 1e-4f ? flat.normalized : Vector3.forward;
            var distance = Vector3.Distance(from, to);
            var aim = to - from; // the barrel's direction: down from an aircraft, up at one
            var kind = weapon?.Projectile ?? (e.Tier == ExplosionTier.Small ? ProjectileKind.Bullet : ProjectileKind.Shell);
            var targetId = e.Other;
            var lag = 0f;
            if (weapon != null && weapon.RoundGap is > 0f and < 0.1f)
            {
                var key = (e.Entity, e.Mount);
                var count = _sameFrame.TryGetValue(key, out var seen) && Mathf.Approximately(seen.at, now) ? seen.count + 1 : 0;
                _sameFrame[key] = (now, count);
                if (_sameFrame.Count > 256) _sameFrame.Clear();
                lag = count * weapon.RoundGap;
            }

            if (weapon != null && weapon.Charge > 0f && kind == ProjectileKind.Bullet)
            {
                Rail(weapon, from, to, aim, groundY, e.Value, now, Model(null));
                return;
            }
            if (weapon != null && weapon.Beam)
            {
                if (_lasers != null)
                {
                    // A laser: one held beam onto the target, charged up, glowing and burning (LaserBeams).
                    var flies = views.TryGet(targetId, out var lit) && lit.Flying;
                    _lasers.Fire(shooter, e.Mount, from, to, targetId, flies, weapon, now, Mathf.Max(0.1f, weapon.Cooldown) * 1.6f);
                    return;
                }
                // A laser: a hard bright bar for a moment, the glow of the director at the muzzle.
                _tracers.Beam(from, to, 0.08f, 0.09f, now);
                Flash(MuzzleFx.Kind.MachineGun, from, Barrel(aim), now, 0.6f, groundY);
                return;
            }
            // Prompt 25 G: an air-burst round flies as itself (a short shell with its proximity fuse) on its tracer.
            if (weapon != null && weapon.Flak && lag <= 0f) FlakRound(weapon, from, to, e.Value, now);
            switch (kind)
            {
                case ProjectileKind.Bullet:
                    Bullets(weapon, from, to, aim, groundY, e.Value, now, lag);
                    break;

                case ProjectileKind.Missile:
                    // Guided: the missile bends towards wherever its target is now. It leaves the
                    // rail slowly, boosts hard and cruises, arriving on time, its motor burning a
                    // flame cone and leaving a smoke trail (Plume).
                    var missile = Model("missile");
                    var airborne = shooter != null && shooter.Flying;
                    // Play-test 13 follow-up (lane A): on its flight profile (WeaponDef.Flight), its hump the Sim's own
                    // (ArcShare x ground distance, CombatSystem.RoundHeight). Direct (an ATGM on its beam): a flat run that
                    // leaves along its tube or rail and turns onto the target. Loft (a top-attack, VLS or box-launched
                    // missile): a steep climb, over, and a dive onto the target. Ballistic: a high arc.
                    var flight = weapon?.Flight ?? FlightProfile.Direct;
                    var peak = Ground(from, to) * (weapon?.ArcShare ?? 0.04f);
                    if (_hasMissile)
                    {
                        _projectiles.Launch(_models.Merged(missile), from, to, e.Value, peak, 0.7f, now, Homing(views, targetId, weapon != null && weapon.TopAttack ? null : from),
                            boost: 0.55f, scale: Sized(missile) * SizeOf(weapon, kind, missile, airborne),
                            control: flight == FlightProfile.Direct ? Leave(from, to, _shotBarrel, peak) : null,
                            plume: Plume.For(weapon, kind, missile, airborne));
                        if (flight == FlightProfile.Loft) _projectiles.FlyLoft(LoftLaunch(from, to, _shotBarrel, airborne), peak);
                        else if (flight == FlightProfile.Ballistic) _projectiles.FlyBallistic(Raised(_shotBarrel), peak);
                        // Fix prompt L4: the Sim may divert it in flight (a flare, lost sight, out of reach).
                        _projectiles.Tag(targetId);
                        Veer(e, views, targetId);
                    }
                    else _tracers.Launch(from, to, e.Value, peak, 0.2f, 1.2f, now, 0f, 0.7f);
                    Flash(MuzzleFx.Kind.Missile, from, Tube(aim), now, 1f, groundY);
                    FiringShake(from, 0.05f);
                    break;

                case ProjectileKind.Drone:
                {
                    // A kamikaze drone climbs off the rack, then dives onto whatever it was sent at. Test feedback 19P:
                    // an FPV quadcopter (the swarms, the mothership's) flies as one, with no motor flame or smoke trail:
                    // level and nose-down under its rotors, weaving about a line of its own across the swarm.
                    var drone = Model(_models.Has("fpv_drone") ? "fpv_drone" : _hasMissile ? "missile" : null);
                    var quad = drone == "fpv_drone";
                    if (drone != null)
                    {
                        _projectiles.Launch(_models.Merged(drone), from, to, e.Value, distance * (quad ? 0.1f : 0.12f), quad ? 0f : 0.35f, now,
                            Homing(views, targetId), wobble: quad ? 0f : 0.6f, scale: Sized(drone) * SizeOf(weapon, kind, drone, false) * (quad ? QuadScale : 1f));
                        // Play-test 13 follow-up (lane A): a winged loitering drone (a Lancet, a Shahed) flies its Loft profile:
                        // up off the rack, over at the Sim's height, and down onto the target (the quadcopter keeps its own flight).
                        if (!quad) _projectiles.FlyLoft(LoftLaunch(from, to, _shotBarrel, false, DroneClimb), Ground(from, to) * (weapon?.ArcShare ?? 0.2f));
                        _projectiles.Tag(targetId);
                        if (quad)
                        {
                            var across = Vector3.Cross(Vector3.up, forward);
                            var width = Mathf.Min(6f, distance * 0.14f);
                            _projectiles.FlyAsDrone(across * UnityEngine.Random.Range(-width, width) + Vector3.up * UnityEngine.Random.Range(-0.5f, 2.5f));
                        }
                        Veer(e, views, targetId);
                    }
                    else _tracers.Launch(from, to, e.Value, distance * 0.12f, 0.15f, 0.8f, now, 0f, 0.4f);
                    // A quadcopter lifts off its rack in a puff of dust; a winged drone's booster flares.
                    if (quad) _emitters.Dust(from, 0.35f);
                    else Flash(MuzzleFx.Kind.Missile, from, aim, now, 0.5f, groundY);
                    break;
                }

                case ProjectileKind.Rocket:
                    // Play-test 13 follow-up (lane A): a ballistic rocket (an artillery rocket, a boss's Grad or Smerch pod, a
                    // ballistic missile: WeaponDef.Flight) flies a high arc at the Sim's height (ArcShare x ground distance), out
                    // along its raised tubes or erector; a direct one (a rocket pod, the APKWS) a flat run off its rail.
                    var artillery = weapon != null && weapon.Flight == FlightProfile.Ballistic;
                    var arc = Ground(from, to) * (weapon?.ArcShare ?? 0.02f);
                    // Heavy rockets and ballistic missiles fly their own models where they exist.
                    var rocket = Model(weapon?.Id switch
                    {
                        "rockets_300mm" when _models.Has("heavy_rocket") => "heavy_rocket",
                        "ballistic_missile" when _models.Has("ballistic_missile") => "ballistic_missile",
                        _ => "rocket",
                    });
                    var ballistic = weapon?.Id == "ballistic_missile";
                    // A second launcher (not the main, elevating one) lobs along its own tubes too.
                    if (barrel.sqrMagnitude < 0.01f) barrel = _shotBarrel;
                    // Fix prompt L4 rule A: a guided rocket (the APKWS) bends onto its target like a missile.
                    var steered = weapon != null && weapon.GuidedRocket;
                    if (_hasRocket)
                    {
                        _projectiles.Launch(_models.Merged(rocket), from, to, e.Value, arc, 0.55f, now, steered ? Homing(views, targetId, from) : null,
                            wobble: artillery && !ballistic ? 0.7f : steered ? 0f : 0.3f,
                            boost: ballistic ? 0.6f : artillery ? 0.2f : 0.3f, scale: Sized(rocket) * SizeOf(weapon, kind, rocket, false),
                            control: artillery ? null : Leave(from, to, _shotBarrel, arc),
                            plume: Plume.For(weapon, kind, rocket, false));
                        if (artillery) _projectiles.FlyBallistic(Raised(barrel), arc);
                        if (steered) _projectiles.Tag(targetId);
                    }
                    else _tracers.Launch(from, to, e.Value, arc, 0.18f, 1.0f, now, 0f, 0.55f);
                    Flash(MuzzleFx.Kind.Rocket, from, artillery ? Launch(barrel, forward, 0.8f) : Tube(aim), now, artillery ? 1.2f : 0.9f, groundY);
                    FiringShake(from, artillery ? 0.06f : 0.03f);
                    break;

                case ProjectileKind.Bomb:
                    // Released from the wing: play-test 8 A (DECISIONS 22Q), it keeps the aircraft's forward speed and falls,
                    // level at first and ever steeper (a steered bomb glides down onto its target on a flatter curve).
                    // The bomb-run fix, pass 3: an unguided bomb falls with a thin trail, a stick's bombs one after another on their
                    // release interval (each its own fired event), so the stick reads as it is dropped.
                    var bomb = Model("bomb");
                    if (_hasBomb)
                        _projectiles.Launch(_models.Merged(bomb), from, to, Mathf.Max(0.4f, e.Value), 0f, 0f, now, scale: Sized(bomb),
                            control: BombPath(from, to, weapon != null && weapon.GuidedBomb), streak: BombStreak(weapon));
                    else _tracers.Launch(from, to, e.Value, 0f, 0.3f, 1f, now);
                    break;

                case ProjectileKind.Flame:
                    // The stream rides the nozzle it leaves from (Emitters.FeedFlames), however the hull and turret move.
                    _emitters.FlameJet(from, to, Mathf.Max(0.15f, e.Value), weapon != null ? Mathf.Clamp(weapon.Cooldown, 0.1f, 0.4f) : 0.25f, now,
                        new MuzzleFx.Anchor(_shotNode, from, Barrel(aim)));
                    Flash(MuzzleFx.Kind.MachineGun, from, Barrel(aim), now, 0.8f, groundY);
                    break;

                default:
                    var shell = Model(null);
                    Shells(weapon, e, from, to, forward, aim, groundY, distance, now, pitch, barrel, shell, Sized(shell));
                    break;
            }
        }

        /// <summary>
        /// A railgun (or a boss's coilgun) lets go: a white core beam that hangs for a moment
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
            Flash(MuzzleFx.Kind.Cannon, from, Barrel(aim), now, heavy ? 1.8f : 1.2f, groundY);
            _muzzle.SparkBurst(from, Barrel(aim).normalized, heavy ? 40 : 20, 12f, 30f);
            // Ionised air along the line, drifting off.
            var length = Vector3.Distance(from, to);
            for (var d = 3f; d < length; d += 4f) _emitters.Trail(Vector3.Lerp(from, to, d / length), heavy ? 0.5f : 0.35f);
            FiringShake(from, heavy ? 0.12f : 0.06f);
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
        /// Prompt 25 B3 (DECISIONS 25B): round models the balance sheet asks for that are not built yet (ASSET_DEBT), and
        /// the model that flies for each until it is, at the round's own length (Tools/balance/steps_b.py STAND_IN).
        /// </summary>
        internal static readonly System.Collections.Generic.Dictionary<string, string> RoundStandIns = new()
        {
            ["kh29l"] = "maverick",
            ["gbu39"] = "gbu12",
        };

        /// <summary>
        /// Prompt 25 B3: how big a round's model <paramref name="modelLength"/> m long is drawn, before <see cref="SizeOf"/>:
        /// fitted to the weapon's roundLength where the data gives one (so any model flies at the sheet's length), else
        /// the weapon's projectileScale.
        /// </summary>
        internal static float RoundScale(WeaponDef weapon, float modelLength)
        {
            if (weapon == null) return 1f;
            return weapon.RoundLength > 0f && modelLength > 0.01f ? weapon.RoundLength / modelLength : weapon.ProjectileScale;
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
        private static Func<Vector3?> Homing(ViewRegistry views, MachineBrigade.Sim.Core.EntityId targetId, Vector3? from = null) =>
            () => views.TryGet(targetId, out var target) ? HomeOn(target, from) : (Vector3?)null;

        /// <summary>
        /// Where a guided round flies on its target: its middle, or (Play-test 6, DECISIONS 21F) for one fired straight at a
        /// big hull (a boss, a big ship, a large aircraft or structure) the point on the hull's edge towards where it was
        /// launched from, where the simulation bursts it.
        /// </summary>
        internal static Vector3 HomeOn(VehicleView target, Vector3? from)
        {
            var p = target.Position;
            var up = target.Flying ? 0.5f : 1f;
            if (from is not { } f || target.Def == null || target.Root == null) return p + Vector3.up * up;
            var c = MachineBrigade.Sim.Combat.HullContact.On(target.Def, new System.Numerics.Vector2(p.x, p.z), target.Root.eulerAngles.y * Mathf.Deg2Rad,
                new System.Numerics.Vector2(f.x, f.z));
            return new Vector3(c.X, p.y + up, c.Y);
        }

        /// <summary>Where the shot visibly goes: aircraft are hit at their flight height.</summary>
        public static Vector3 AimPoint(in SimEvent e, ViewRegistry views)
        {
            var height = views.TryGet(e.Other, out var target) && target.Flying ? target.Altitude + 0.4f : 0.4f;
            return new Vector3(e.Target.X, height, e.Target.Y);
        }

        /// <summary>Prompt 25 G: the air-burst round's model (Tools/blender/mb_munitions.py flak_round, built 0.5 m for 35 mm).</summary>
        internal const string FlakModel = "flak_round";

        /// <summary>How big the flak round is drawn: in step with its calibre, and twice its size so a 30 mm round reads from the battle camera.</summary>
        internal static float FlakScale(WeaponDef weapon) => Mathf.Clamp(weapon.Size, 20f, 57f) / 35f * 2f;

        private void FlakRound(WeaponDef weapon, Vector3 from, Vector3 to, float travel, float now)
        {
            if (!_hasFlak) return;
            _projectiles.Launch(_models.Merged(FlakModel), from, to, Mathf.Max(0.05f, travel), 0f, 0f, now, scale: FlakScale(weapon));
        }

        private void Bullets(WeaponDef weapon, Vector3 from, Vector3 to, Vector3 aim, float? groundY, float travel, float now, float lag = 0f)
        {
            var damage = weapon?.RoundWeight ?? 9f;
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
            if (rounds > 1) Flash(MuzzleFx.Kind.MachineGun, from, Barrel(aim), now, 1f, groundY);
            else Flash(MuzzleFx.Kind.Autocannon, from, Barrel(aim), now, Mathf.Lerp(0.85f, 1.2f, Mathf.InverseLerp(12f, 30f, damage)), groundY);
        }

        /// <summary>The ground distance a round covers (what the Sim's ArcShare is a share of: CombatSystem.RoundHeight).</summary>
        internal static float Ground(Vector3 from, Vector3 to) => new Vector2(to.x - from.x, to.z - from.z).magnitude;

        /// <summary>A raised barrel, tube or erector's direction (a lobbed round leaves along it), else zero (the plain arc's angle).</summary>
        internal static Vector3 Raised(Vector3 barrel) =>
            barrel.sqrMagnitude > 0.01f && barrel.normalized.y > 0.05f ? barrel.normalized : Vector3.zero;

        /// <summary>A lofted missile's least climb off a ground launcher (degrees): a flat tube's top-attack round still pitches up hard.</summary>
        internal const float LoftClimb = 45f;

        /// <summary>A winged loitering drone's least climb off its rack, and an air-launched lofted missile's (degrees).</summary>
        internal const float DroneClimb = 25f, AirLoftClimb = 12f;

        /// <summary>
        /// Play-test 13 follow-up (lane A): which way a lofted round climbs out: along its drawn tube or box (its heading, and
        /// its angle when steeper: a VLS cell straight up, a raised SAM box at its 40-60 degrees), pitched up to at least
        /// <paramref name="least"/> degrees (a ground launcher's <see cref="LoftClimb"/>; <see cref="AirLoftClimb"/> off an aircraft).
        /// </summary>
        internal static Vector3 LoftLaunch(Vector3 from, Vector3 to, Vector3 tube, bool airborne, float least = float.NaN)
        {
            if (float.IsNaN(least)) least = airborne ? AirLoftClimb : LoftClimb;
            var ahead = new Vector3(to.x - from.x, 0f, to.z - from.z);
            ahead = ahead.sqrMagnitude > 1e-4f ? ahead.normalized : Vector3.forward;
            var heading = ahead;
            var angle = least;
            if (tube.sqrMagnitude > 0.5f)
            {
                var dir = tube.normalized;
                var flat = new Vector3(dir.x, 0f, dir.z);
                if (flat.sqrMagnitude > 0.04f && Vector3.Dot(flat.normalized, ahead) > 0.5f) heading = flat.normalized;
                angle = Mathf.Max(least, Mathf.Asin(Mathf.Clamp(dir.y, -1f, 1f)) * Mathf.Rad2Deg);
            }
            var a = Mathf.Min(angle, 90f) * Mathf.Deg2Rad;
            return heading * Mathf.Cos(a) + Vector3.up * Mathf.Sin(a);
        }

        /// <summary>
        /// Play-test 8 A (DECISIONS 22Q): the middle point of a falling bomb's curve. Level with the release point halfway
        /// along the ground, the quadratic curve is the fall itself: the forward speed kept all the way down, no speed
        /// downwards at first, ever steeper as it drops. A steered bomb's point is set lower, a longer glide onto its target.
        /// </summary>
        internal static Vector3 BombPath(Vector3 from, Vector3 to, bool steered)
        {
            var level = new Vector3((from.x + to.x) * 0.5f, from.y, (from.z + to.z) * 0.5f);
            return steered ? Vector3.Lerp(level, (from + to) * 0.5f, 0.35f) : level;
        }

        /// <summary>
        /// The bomb-run fix, pass 3: the trail a falling bomb leaves (puff size, m): a free-falling bomb's by its weight
        /// (BlastSizes.Bomb), none for a guided or gliding one (they fly their own way onto the target).
        /// </summary>
        internal static float BombStreak(WeaponDef weapon)
        {
            if (weapon == null || weapon.GuidedBomb || weapon.Guided || weapon.Glides) return 0f;
            return 0.36f * Mathf.Clamp(BlastSizes.Bomb(weapon.Id), 0.8f, 1.6f);
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

        /// <summary>The way a launch's ignition and backblast face: along the drawn tube or rail, else at the aim point.</summary>
        private Vector3 Tube(Vector3 aim) => _shotBarrel.sqrMagnitude > 0.5f ? _shotBarrel : aim;

        /// <summary>
        /// The middle control point of a missile's or direct-fire rocket's path that leaves along its
        /// drawn tube or rail and bends onto the target, with the old arc's hump over the middle
        /// (<paramref name="arc"/>): pointing at the target it is the old path; a SAM box raised
        /// 40 degrees sends its missile up first. Null without a tube to go by (DECISIONS 13E).
        /// </summary>
        internal static Vector3? Leave(Vector3 from, Vector3 to, Vector3 tube, float arc)
        {
            var chord = to - from;
            var d = chord.magnitude;
            if (tube.sqrMagnitude < 0.5f || d < 1f) return null;
            return from + chord * 0.5f + Vector3.up * (2f * arc) + (tube.normalized * d - chord) * 0.3f;
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
            // Prompt 34 L4: a later barrel of a simultaneous volley is drawn a moment later and flies that much shorter (it lands with the Sim).
            var travel = Mathf.Max(0.05f, e.Value - TravelCut);
            if (!lobs)
            {
                var heavy = weapon != null && weapon.Damage >= 100f;
                var big = e.Tier >= ExplosionTier.Large;
                _tracers.Launch(from, to, travel, 0f, big ? 0.28f : heavy ? 0.22f : 0.16f, big ? 3.6f : heavy ? 3.2f : 2.6f, now, 0f,
                    big ? 1.1f : heavy ? 0.95f : 0.75f);
                Flash(MuzzleFx.Kind.Cannon, from, Barrel(aim), now, big ? 1.5f : heavy ? 1.25f : 1f, groundY);
                FiringShake(from, big ? 0.1f : heavy ? 0.08f : 0.05f);
                return;
            }
            // Artillery: a high arc, leaving at the barrel's angle, with a thin trail of hot gas;
            // the shell or mortar bomb itself where it has a model.
            // Play-test 13 follow-up (lane A): at the Sim's height (ArcShare x ground distance, CombatSystem.RoundHeight), so a
            // C-RAM's burst meets the shell where it is drawn; it leaves along the laid barrel (FlyBallistic).
            var peak = Ground(from, to) * (weapon != null && weapon.Flight == FlightProfile.Ballistic ? weapon.ArcShare : 0.3f);
            if (model != null)
            {
                _projectiles.Launch(_models.Merged(model), from, to, travel, peak, 0.35f, now, scale: scale);
                _projectiles.FlyBallistic(Raised(barrel), peak);
            }
            else _tracers.Launch(from, to, travel, peak, 0.32f, 1.1f, now, 0f, 0.55f);
            // A mortar's flash is small: at the artillery size it covered the carrier seen from above.
            var mortar = weapon != null && weapon.Id.Contains("mortar");
            Flash(MuzzleFx.Kind.Artillery, from, Launch(barrel, forward, 0.9f), now, mortar ? 0.55f : 1f, groundY);
            FiringShake(from, 0.12f);
        }
    }
}
