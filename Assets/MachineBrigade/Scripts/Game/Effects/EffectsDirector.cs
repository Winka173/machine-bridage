using System;
using System.Collections.Generic;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Effects
{
    /// <summary>Visual budgets from the game plan (section 6), per quality preset.</summary>
    public readonly struct EffectBudget
    {
        public EffectBudget(int debris, int decals, int wrecks)
        {
            Debris = debris;
            Decals = decals;
            Wrecks = wrecks;
        }

        public int Debris { get; }
        public int Decals { get; }

        /// <summary>Hulks left on the field before the oldest sinks away.</summary>
        public int Wrecks { get; }

        public static EffectBudget Eco => new EffectBudget(260, 96, 30);
        public static EffectBudget High => new EffectBudget(520, 160, 45);
    }

    /// <summary>
    /// Turns simulation events into fire, smoke, shells, debris, wrecks and camera shake.
    /// It only ever reads events: nothing here can change the battle (V2 rule 6).
    /// </summary>
    public sealed partial class EffectsDirector : IDisposable
    {
        private readonly Transform _root;
        private readonly MaterialLibrary _materials;
        private readonly ModelLibrary _models;
        private readonly Dictionary<string, ChunkModel> _chunks = new();
        private readonly RtsCamera _camera;
        private readonly Dictionary<ExplosionTier, ExplosionEffect> _explosions = new();

        /// <summary>Play-test 5: each gun point defence's last burst (the round's height, and when), for the air burst that ends it.</summary>
        private readonly Dictionary<MachineBrigade.Sim.Core.EntityId, (float height, float at)> _pointBursts = new();
        private readonly List<ExplosionEffect> _blasts = new();
        private readonly BlastLayers _layers;
        private readonly Catalog _catalog;
        private readonly MuzzleFx _muzzle;
        private readonly ExplosionEffect _airburst;
        private readonly ExplosionEffect _napalm;
        private readonly ExplosionEffect _kill;
        private readonly ExplosionEffect _pop;
        private readonly ExplosionEffect _collapse;
        private readonly ExplosionEffect _shellHit;
        private readonly ScreenCull _cull;
        private readonly TracerPool _tracers;
        private readonly DecalPool _decals;
        private readonly DebrisPool _debris;
        private readonly WreckManager _wrecks;

        /// <summary>Prompt 16: ships going down (they list, break and sink instead of leaving a wreck).</summary>
        private readonly ShipSinking _sinking = new();

        /// <summary>Play-test 8 A: loaned aircraft flying off the map after their time (see <see cref="VehicleView.Depart"/>).</summary>
        private readonly List<VehicleView> _departing = new();
        private readonly Emitters _emitters;

        /// <summary>Prompt 25 G, play-test 10: the air-burst rounds' bursts (a sharp flash, a black puff that hangs, a spark spray).</summary>
        private readonly FlakBursts _flakBursts;
        private readonly TrackMarks _tracks;
        private readonly NightLights _night;

        /// <summary>Night: blasts, gun flashes and fires light the ground, and flares drift over the fighting.</summary>
        public bool Night
        {
            set
            {
                _night.Night = value;
                _fires.Night = value;
            }
        }
        private readonly FireSpots _fires;
        private readonly HullFire _hullFire;
        private readonly ProjectilePool _projectiles;

        /// <summary>Fix prompt L6: the smoke and dust blasts leave behind (EffectLife's table).</summary>
        private readonly ImpactSmoke _smoke;

        /// <summary>Fix prompt L6: a blast's lingering smoke at its distance's detail (on screen, or a big column near it).</summary>
        private void Linger(int band, Vector3 at, float core, float now)
        {
            if (!_cull.Visible(at, band >= 4 ? 1.2f : 0.4f)) return;
            _smoke.Linger(band, at, core, now, TierFx.DetailAt(Vector3.Distance(at, _camera.Focus), _camera.Zoom));
        }
        private readonly WeaponEffects _weapons;
        private readonly LaserBeams _lasers;

        /// <summary>Prompt 29 G1: Gungnir's aiming line for its warning.</summary>
        private readonly AimLines _aimLines;
        private readonly StrikeEffects _strikes;
        private readonly AirDrops _drops;

        /// <summary>Prompt 33 L2: the scripted reinforcements' stand-ins on their gates' approaches (view only).</summary>
        private readonly IngressStandIns _ingress;
        private readonly GroundMark _marker;
        private float _markerStart = -10f;

        /// <summary>Half the map's side, for the troop transports' way in and out.</summary>
        public float MapHalfSize { set => _drops.HalfSize = value; }

        /// <summary>The map's rectangle, for the troop transports' way in and out (a long battlefield's, prompt 17).</summary>
        public void SetMapBounds(Vector3 centre, float halfX, float halfZ)
        {
            _drops.Centre = centre;
            _drops.HalfX = halfX;
            _drops.HalfZ = halfZ;
        }

        public EffectsDirector(Catalog catalog, MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, RtsCamera camera,
            Transform parent, EffectBudget budget)
        {
            _catalog = catalog;
            _materials = materials;
            _models = models;
            _camera = camera;
            _root = new GameObject("Effects").transform;
            _root.SetParent(parent, false);

            // Everything is built up front: creating particle systems mid-battle hitches the frame.
            _cull = new ScreenCull(camera.Camera);
            _layers = new BlastLayers(materials, _root);
            foreach (ExplosionTier tier in Enum.GetValues(typeof(ExplosionTier)))
            {
                _explosions[tier] = ExplosionEffect.Create(tier, _layers);
                _blasts.Add(_explosions[tier]);
            }
            _muzzle = new MuzzleFx(materials, _root);
            _airburst = ExplosionEffect.CreateAirburst(_layers);
            _blasts.Add(_airburst);
            _napalm = ExplosionEffect.CreateNapalm(_layers);
            _blasts.Add(_napalm);
            _kill = ExplosionEffect.CreateKill(_layers);
            _blasts.Add(_kill);
            _pop = ExplosionEffect.CreatePop(_layers);
            _blasts.Add(_pop);
            _collapse = ExplosionEffect.CreateCollapse(_layers);
            _blasts.Add(_collapse);
            _shellHit = ExplosionEffect.CreateShellHit(_layers);
            _blasts.Add(_shellHit);
            // Anti-aircraft guns fire 10-16 round bursts, every round a tracer.
            _tracers = new TracerPool(meshes.Box, materials.Tracer, _root, 320);
            // Flame streams are fed from their nozzles once the vehicles are drawn (LaunchShots).
            _emitters = new Emitters(materials, _root) { LateFeed = true };
            _flakBursts = new FlakBursts(materials, _root);
            _tracks = new TrackMarks(materials, _root);
            _night = new NightLights(materials, _emitters, _root);
            _fires = new FireSpots(materials, _root);
            _hullFire = new HullFire(materials, _root);

            _fires.Visible = p => _cull.Visible(p, 0.3f);
            _decals = new DecalPool(meshes.ScorchQuad, _root, budget.Decals);
            _debris = new DebrisPool(budget.Debris);
            _layers.Chunks = new ChunkThrower(_debris, materials, models, _fires, _root);
            _layers.Chunks.Trails.Visible = p => _cull.Visible(p, 0.3f);
            _wrecks = new WreckManager(_fires, _layers.Chunks, budget.Wrecks, _root);
            _projectiles = new ProjectilePool(_root, 96) { RotorMaterial = materials.SoftSmoke };
            _lasers = new LaserBeams(materials, _emitters, _decals, _root);
            _weapons = new WeaponEffects(catalog, models, _tracers, _projectiles, _emitters, _muzzle, Shake, _lasers);
            // Prompt 34 L5: the tiers' redrawn blasts and firing looks.
            InitTiers();
            _strikes = new StrikeEffects(catalog, materials, meshes, models, _emitters, _projectiles, _layers.Screens, _root);
            _bigZones = new BigAttackZones(materials, meshes, _root);
            // Prompt 34 L3: the T4+ rounds' escape warnings.
            _escape = new EscapeWarnings(materials, meshes, _root);
            // Fix prompt L6: the smoke and dust a blast leaves, by its size band.
            _smoke = new ImpactSmoke(_root);
            // Fix prompt L5: one gate decides which warning rings are drawn (data warningRules).
            InitWarningGate();
            _aimLines = new AimLines(materials, _root);
            _drops = new AirDrops(catalog, models, meshes, materials, _emitters, _root);
            _ingress = new IngressStandIns(catalog, models, _root);

            _marker = new GroundMark("Move Marker", _root, meshes, materials, GroundMark.Style.Move);
            _marker.Transform.localScale = Vector3.one * 2.2f;
            _marker.Visible = false;
        }

        public void Consume(IReadOnlyList<SimEvent> events, ViewRegistry views, MapView map)
        {
            var now = Time.time;
            _domeStruck.Clear();
            for (var index = 0; index < events.Count; index++)
            {
                var e = events[index];
                switch (e.Kind)
                {
                    case SimEventKind.WeaponCharging:
                    case SimEventKind.WeaponFired:
                        // Drawn once the vehicles are (see LaunchShots); the shooter is held now, in
                        // case it dies later in this step.
                        _shots.Add((e, views.TryGet(e.Entity, out var gunner) ? gunner : null));
                        break;

                    case SimEventKind.DeploymentQueued:
                        _drops.Queue(e, now);
                        break;

                    case SimEventKind.Ingress:
                        _ingress.Queue(e, now);
                        break;

                    case SimEventKind.ShellInbound:
                    {
                        // Fire support coming down: a glowing round falls steeply out of the sky from its
                        // guns' side onto the spot it hits. Smoke shells, mine rockets and the SEAD
                        // missile are drawn by StrikeEffects as what they are instead (DECISIONS 12C).
                        var land = Ground(e.Position, 0.2f);
                        var from = land + new Vector3(e.Target.X, 0f, e.Target.Y) * 24f + Vector3.up * 58f;
                        if (!_cull.Visible(land, 0.6f)) break;
                        if (_strikes.Inbound(e, from, land, now)) break;
                        var smoke = _catalog.TryGetSupport(e.DefId, out var inbound) && inbound.Kind == SupportKind.Smoke;
                        _tracers.Launch(from, land, e.Value, 0f, smoke ? 0.4f : 0.34f, smoke ? 2.2f : 3.6f, now, 0f, smoke ? 1.1f : 0.5f);
                        break;
                    }

                    case SimEventKind.ProjectileImpact:
                        // The shield it struck ripples (prompt 11C).
                        ShieldImpact(e, views, map, now);
                        if (e.Airborne)
                        {
                            // Flak and missiles bursting around an aircraft, at its height (a killing
                            // hit finds it among the wrecks); misses burst at a typical flying height.
                            // Fix prompt L4: a missile a flare decoyed (or one out of reach) bursts where it was sent, at its height.
                            var height = views.TryGet(e.Entity, out var struck) && struck.Flying ? struck.Altitude + 0.5f
                                : _wrecks.TryGetAircraftWreck(e.Entity, out var falling) ? falling.y + 0.5f
                                : DecoyHeight(e.Position, now, out var decoyed) ? decoyed : 15f;
                            var burst = new Vector3(e.Position.X, height, e.Position.Y);
                            // Play-test 10 (DECISIONS PT10 visuals): an air-burst round's burst is its own flak burst alone
                            // (a sharp flash, a black puff that hangs, a spark spray); no Small blast, lone ring or grey puffs.
                            var burstRound = e.DefId != null && _catalog.Weapons.TryGetValue(e.DefId, out var br) ? br : null;
                            if (burstRound != null && burstRound.Flak)
                            {
                                var flakAt = burst + UnityEngine.Random.insideUnitSphere * 0.6f;
                                if (!_cull.Visible(flakAt, 0.3f)) break;
                                _flakBursts.Burst(flakAt, burstRound.Size, e.Value);
                                _night.Blast(flakAt, 3f * FlakBursts.Scale(burstRound.Size), 0.15f);
                                break;
                            }
                            // Play-test 8 A (DECISIONS 22Q): an anti-aircraft missile's burst is drawn at its round's impact
                            // scale (the S-400's 48N6 twice the size, as big as the missile); other rounds as before.
                            var flak = e.DefId != null && _catalog.Weapons.TryGetValue(e.DefId, out var aaRound) && aaRound.Targets == TargetLayers.Air
                                ? Mathf.Max(1f, aaRound.ImpactScale) : 1f;
                            // Prompt 25 A5: its ring as wide as its blast reaches (the round's splash radius).
                            if (e.Tier >= ExplosionTier.Medium) Airburst(burst, e.Tier, now, flak, e.Value);
                            else Explode(e.Tier, burst, now, flak, radius: e.Value);
                            _emitters.Flak(burst);
                            break;
                        }
                        var round = e.DefId != null && _catalog.Weapons.TryGetValue(e.DefId, out var landed) ? landed : null;
                        // Prompt 25 G: an air-burst round fired at the ground bursts just over it.
                        if (round != null && round.Flak && _cull.Visible(Ground(e.Position, 1.4f), 0.3f)) _flakBursts.Burst(Ground(e.Position, 1.4f), round.Size, e.Value);
                        // A round a unit's dome took whole bursts on the dome's skin (as big as ever), not on the unit.
                        if (DomeTook(e.Position, out var onDome))
                        {
                            Explode(e.Tier < ExplosionTier.Medium ? ExplosionTier.Small : e.Tier, onDome, now, round?.ImpactScale ?? 1f, flash: false);
                            break;
                        }
                        var impact = Ground(e.Position, 0.15f);
                        var size = round?.ImpactScale ?? 1f;
                        // A gun's shell never flashes the screen, however big: only strikes and blasts do.
                        // Play-test 5 (DECISIONS 20V): drones, missiles, rockets, shells and the gun turret's rounds by BlastSizes.Round.
                        // Prompt 25 A5: every blast's ring on its damage radius (e.Value, the round's splash radius).
                        if (!ImpactOfKind(round, e, impact, now, size)) Explode(e.Tier, impact, now, size, flash: false, grow: BlastSizes.Round(round), radius: e.Value);
                        // Prompt 26 B.3: a two-layer blast shows its edge too, a second ring on the edge's radius beyond the core's.
                        EdgeRing(impact, e.Value, e.Target.X);
                        // Prompt 34 L5: its tier's redrawn blast on top, the exact shockwave rings, the shake.
                        TierImpact(TierFx.Of(round), impact, e.Value, e.Target.X, now, views);
                        // Fix prompt L6: the smoke and dust it leaves, as long as its size band says (EffectLife).
                        var band = EffectLife.BandOf(round, e.Tier);
                        Linger(band, impact, e.Value, now);
                        // Every blast from Medium up scorches the ground under it, as wide as it is drawn, for its band's time.
                        if (e.Tier >= ExplosionTier.Medium)
                            _decals.Place(impact, (e.Tier >= ExplosionTier.Large ? 5f : 2.2f) * size * BlastSizes.Ground(round) * BlastSizes.Round(round),
                                EffectLife.Crater(band));
                        // Play-test 5 (DECISIONS 20V): a railgun's slug leaves a burn on what it struck, like the focused laser's.
                        if (round != null && round.Family == "railgun" && _cull.Visible(impact, 0.3f))
                        {
                            views.TryGet(e.Entity, out var seared);
                            var onHull = seared != null && seared.Root != null ? Mathf.Min(1.3f, seared.Top * 0.55f) : 0.3f;
                            _lasers.Sear(impact + Vector3.up * onHull, e.Entity, seared, round.Damage >= 300f ? 1.3f : 1f, 2.6f, now);
                        }
                        if (round != null && round.Projectile == ProjectileKind.Flame && UnityEngine.Random.value < 0.35f)

                            _fires.Ignite(impact, round.SplashRadius > 3f ? 0.8f : 0.45f, 7f, now);
                        // Thermobaric rockets leave the impact area burning.
                        if (e.DefId == "thermobaric_rockets" && UnityEngine.Random.value < 0.6f) _fires.Ignite(impact, 1.1f, 14f, now);
                        // Heavy shells and rockets leave the ground burning now and then.
                        else if (e.Tier == ExplosionTier.Large && UnityEngine.Random.value < 0.5f) _fires.Ignite(impact, 0.6f, 10f, now);
                        else if (e.Tier == ExplosionTier.Medium && UnityEngine.Random.value < 0.15f) _fires.Ignite(impact, 0.35f, 5f, now);
                        break;

                    case SimEventKind.StrikeImpact when IsGentle(e.DefId):
                        Pulse(e.DefId, Ground(e.Position, 0.3f));
                        if (_catalog.TryGetSupport(e.DefId, out var gentle) && gentle.Kind == SupportKind.ShieldDome)
                            RaiseItemDome(e, gentle, views, now);
                        break;

                    case SimEventKind.StrikeImpact:
                        RippleItemDomes(e.Position, 1.5f, now);
                        var hit = Ground(e.Position, 0.3f);
                        var huge = e.Tier >= ExplosionTier.Ultimate;
                        // Drawn as big as the strike reaches (a heavier bomb, a bigger fireball).
                        var nominal = e.Tier switch { ExplosionTier.Large => 4.5f, ExplosionTier.Huge => 6.5f, ExplosionTier.Ultimate => 20f, _ => 3f };
                        var strikeScale = Mathf.Clamp(e.Value / nominal, 0.9f, 1.6f);
                        _catalog.TryGetSupport(e.DefId, out var strike);
                        // Bombs drawn bigger by their weight; a cruise missile (and the MOAB) as wide
                        // as the ground it wrecks: its shockwave reaches the edge of its blast radius.
                        var matched = strike != null && strike.Kind == SupportKind.CruiseMissile && e.Tier >= ExplosionTier.Ultimate;
                        var strikeGrow = matched ? BlastSizes.Reach(e.Value) : BlastSizes.Strike(strike);
                        if (matched) strikeScale = 1f;
                        // Its ground ring stays on the radius while the rest grows a tenth (DECISIONS 12C), and a cruise
                        // missile's fire and smoke a fifth more (play-test 5, DECISIONS 20V).
                        var missileGrow = matched && strike.Id != "moab" ? BlastSizes.MissileGrow : 1f;
                        // Prompt 25 A5: every strike's ring on its blast radius (a cruise missile's since 12C, now all of them).
                        Explode(e.Tier, hit, now, strikeScale, grow: strikeGrow * missileGrow, exact: matched, radius: e.Value);
                        // Fix prompt L6: its crater and its lingering smoke for its size band's time.
                        var strikeBand = EffectLife.BandOf(e.Tier);
                        _decals.Place(hit, Mathf.Max(4f, e.Value * (huge ? 1.4f : 1.1f)) * (matched ? 1f : strikeGrow), EffectLife.Crater(strikeBand));
                        Linger(strikeBand, hit, e.Value, now);
                        if (strike != null && strike.Kind == SupportKind.Sead) SeadKill(hit, views, now);
                        if (e.Tier >= ExplosionTier.Large) _fires.Ignite(hit, huge ? 2.2f : e.Tier >= ExplosionTier.Huge ? 1.2f : 0.7f, huge ? 35f : 16f, now);
                        if (e.DefId == "napalm_strike")
                        {
                            if (_cull.Visible(hit, 0.3f)) _napalm.Play(hit, now, 1f, BlastSizes.Bigger);
                            // Napalm: the ground itself burns in a wide strip for half a minute.
                            for (var i = 0; i < 3; i++)
                            {
                                var scatter = new Vector3(UnityEngine.Random.Range(-4f, 4f), 0f, UnityEngine.Random.Range(-4f, 4f));
                                _fires.Ignite(hit + scatter, UnityEngine.Random.Range(1.2f, 1.8f), UnityEngine.Random.Range(24f, 34f), now, napalm: true);
                            }
                        }
                        if (huge)
                        {
                            // A ring of fires around the crater of the heaviest strikes.
                            for (var i = 0; i < 5; i++)
                            {
                                var a = i * Mathf.PI * 2f / 5f + UnityEngine.Random.value;
                                var r = e.Value * UnityEngine.Random.Range(0.35f, 0.7f);
                                _fires.Ignite(hit + new Vector3(Mathf.Cos(a) * r, 0f, Mathf.Sin(a) * r), UnityEngine.Random.Range(0.6f, 1.1f),
                                    UnityEngine.Random.Range(14f, 26f), now);
                            }
                        }
                        break;

                    case SimEventKind.StrikeWarning:
                        _strikes.Consume(e, now);
                        // Prompt 34 L3: the core of a T5 salvo shell's warning.
                        StrikeCore(e, now);
                        break;
                    case SimEventKind.AircraftPass:
                    case SimEventKind.SmokeDeployed:
                        _strikes.Consume(e, now);
                        break;

                    case SimEventKind.Intercepted:
                        // Active protection: a launcher on the turret fires, and the incoming round
                        // bursts in the air a few metres short of the tank.
                        var interceptAt = Ground(e.Position, 1.8f);
                        if (views.TryGet(e.Entity, out var guard) && guard.Def.Weapon.Beam)
                        {
                            // A point-defence laser: the beam burns the round out of the air (its own beam, mount -1).
                            var emitter = guard.MuzzleOf(0);
                            _lasers.Fire(guard, -1, emitter, interceptAt, MachineBrigade.Sim.Core.EntityId.None, true, guard.Def.Weapon, now, 0.16f);
                        }
                        else if (guard != null && guard.Def.Aps is { Laser: true } && _catalog.Weapons.TryGetValue("hel_beam", out var pointBeam))
                        {
                            // Prompt 16 E: a boss's interceptor laser (the Tempest's) draws the Iron Beam's beam from its turret side.
                            var emitter = guard.Position + Vector3.up * 3.4f + guard.Root.right * (e.Value * 1.6f);
                            _lasers.Fire(guard, -1, emitter, interceptAt, MachineBrigade.Sim.Core.EntityId.None, true, pointBeam, now, 0.16f);
                        }
                        else if (guard != null && guard.Def.Aps is { Missiles: true })
                        {
                            // Prompt 20 L.1: the Iron Dome's interceptor climbs off its launcher and bursts high over the round's mark.
                            interceptAt = Ground(e.Position, 9f);
                            var from = guard.Position + Vector3.up * 3f + guard.Root.right * (e.Value * 1.1f);
                            _tracers.Launch(from, interceptAt, 0.16f, Vector3.Distance(from, interceptAt) * 0.1f, 0.3f, 3.2f, now, 0f, 0.6f);
                            _muzzle.Fire(MuzzleFx.Kind.Missile, from, interceptAt - from, now, 0.8f, guard.Position.y);
                        }
                        else if (guard != null && guard.Def.Aps is { Burst: > 0f } && _pointBursts.TryGetValue(e.Entity, out var burst) && now - burst.at < 0.3f)
                        {
                            // Play-test 5 (DECISIONS 20W): the C-RAM's stream has been on the round for its burst; it bursts where it flew.
                            interceptAt = Ground(e.Position, burst.height);
                        }
                        else if (guard != null && NearestPoint(guard.ApsPoints, interceptAt) is { } cassette)
                        {
                            // Prompt 29 5.5 (APS_EFFECT): a 0.1 s beam from the turret's cassette to the round, then the burst below.
                            var from = cassette.position;
                            _tracers.Launch(from, interceptAt, 0.1f, 0f, 0.12f, 1.2f, now);
                            _muzzle.Fire(MuzzleFx.Kind.Autocannon, from, interceptAt - from, now, 0.9f, guard.Position.y);
                        }
                        else if (guard != null)
                        {
                            var from = guard.Position + Vector3.up * 2.4f + guard.Root.right * (e.Value * 1.3f);
                            _tracers.Launch(from, interceptAt, 0.06f, 0f, 0.12f, 1.2f, now);
                            _muzzle.Fire(MuzzleFx.Kind.Autocannon, from, interceptAt - from, now, 0.9f, guard.Position.y);
                        }
                        Pop(_pop, interceptAt, now);
                        _emitters.Flak(interceptAt);
                        break;

                    case SimEventKind.PointDefenceFired:
                        // Play-test 5 (DECISIONS 20W): a C-RAM streams at an incoming round (Mount rounds this step).
                        if (views.TryGet(e.Entity, out var pd))
                        {
                            var at = Ground(e.Position, e.Value);
                            var muzzle = pd.MuzzleOf(0);
                            var speed = _catalog.Weapons.TryGetValue(e.DefId ?? "", out var pdGun) ? Mathf.Max(100f, pdGun.ProjectileSpeed) : 380f;
                            var flight = Vector3.Distance(muzzle, at) / speed;
                            for (var k = 0; k < Mathf.Max(1, e.Mount); k++)
                                _tracers.Launch(muzzle, at + UnityEngine.Random.insideUnitSphere * 0.7f, flight, 0f, 0.07f, 1.1f, now, k * 0.016f);
                            _muzzle.Fire(MuzzleFx.Kind.Autocannon, muzzle, at - muzzle, now, 0.75f, pd.Position.y);
                            _pointBursts[e.Entity] = (e.Value, now);
                        }
                        break;

                    case SimEventKind.GunRevealed:
                        // A counter-battery radar found a gun that fired: a red ping on it.
                        Ring(Ground(e.Position, 0.3f), 7f, new Color(2.4f, 0.4f, 0.25f, 0.8f));
                        break;

                    case SimEventKind.RoundSwitched:
                        // Prompt 25 G: the change-of-round glyph flashes on the unit's bar.
                        if (views.TryGet(e.Entity, out var switcher)) switcher.ShowRoundSwitch();
                        break;

                    case SimEventKind.Repaired:
                        if (views.TryGet(e.Entity, out var repaired))
                        {
                            _emitters.Repair(repaired.Position + Vector3.up);
                            repaired.ShowRepair();
                        }
                        break;

                    // A boss's part (prompt 9): its own blast at the part, and the sim's blast event after it skipped.
                    case SimEventKind.PartBroken:
                        PartBroke(e, views, now);
                        break;
                    case SimEventKind.PartRepaired:
                        PartBack(e, views);
                        break;
                    // Prompt 16: a patch of the Inferno's fire trail (FireSpots burns ground fires a fifth shorter).
                    case SimEventKind.FireTrail:
                    {
                        var trailAt = Ground(e.Position, 0.05f);
                        var trailRadius = e.Target.X;
                        _fires.Ignite(trailAt, 0.9f, e.Value, now);
                        for (var lick = 0; lick < 2; lick++)
                        {
                            var bearing = UnityEngine.Random.value * Mathf.PI * 2f;
                            var reach = trailRadius * UnityEngine.Random.Range(0.35f, 0.7f);
                            _fires.Ignite(trailAt + new Vector3(Mathf.Cos(bearing) * reach, 0f, Mathf.Sin(bearing) * reach), UnityEngine.Random.Range(0.45f, 0.7f),
                                e.Value * UnityEngine.Random.Range(0.8f, 1f), now);
                        }
                        break;
                    }
                    case SimEventKind.Explosion when _partBlasts.Remove(e.Entity):
                        break;
                    case SimEventKind.Explosion:
                        if (_dyingBosses.Remove(e.Entity))
                        {
                            BossFinale(e, now);
                            break;
                        }
                        if (_wrecks.TryGetAircraftWreck(e.Entity, out var inAir))
                        {
                            // A shot-down aircraft blows up where it is, in the air; the crash follows.
                            Airburst(inAir, ExplosionTier.Huge, now, 1f, e.Value);
                            break;
                        }
                        var blast = Ground(e.Position, 0.3f);
                        // A cluster bomblet: its own small fireball, not a spray of sparks.
                        if (e.Tier == ExplosionTier.Small)
                        {
                            Pop(_pop, blast + Vector3.up * 0.3f, now);
                            _decals.Place(blast, 1.8f, EffectLife.Crater(1));
                            break;
                        }
                        // Prompt 25 A5: a vehicle's, a mine's or a prop's blast drawn as wide as it reaches.
                        Explode(e.Tier, blast, now, radius: e.Value);
                        EdgeRing(blast, e.Value, e.Target.X);
                        // Prompt 34 L5: a salvo's shell (Leviathan's 406 mm) lands as its tier.
                        TierImpact(SalvoTier(e, views), blast, e.Value, e.Target.X, now, views);
                        _decals.Place(blast, Mathf.Max(3f, e.Value * 0.9f), EffectLife.Crater(EffectLife.BandOf(e.Tier)));
                        _wrecks.Blow(e.Entity, now);
                        if (e.Tier >= ExplosionTier.Huge)
                        {
                            _fires.Ignite(blast, 1.4f, 30f, now);
                        }
                        else if (e.Tier == ExplosionTier.Large && UnityEngine.Random.value < 0.8f)
                        {
                            _fires.Ignite(blast, 0.9f, 18f, now);
                        }
                        break;

                    case SimEventKind.RoundDiverted:
                        // Fix prompt L4: a guided round taken off its target in flight turns onto where it now goes off.
                        RoundDiverted(e, views, now);
                        break;

                    case SimEventKind.SkillUsed when e.Skill == SkillKind.Flares:
                        // Prompt 29 5.5 (FLARE_EFFECT): a flare charge used: every dispenser fires its fan at once.
                        if (views.TryGet(e.Entity, out var flarer) && flarer.Flying && _cull.Visible(flarer.Position, 0.3f)) FlareSalvo(flarer);
                        break;

                    case SimEventKind.SkillUsed when e.Skill == SkillKind.Emp:
                        Ring(Ground(e.Position, 0.3f), 30f, new Color(0.45f, 0.8f, 2.4f, 1f));
                        break;

                    case SimEventKind.SkillUsed when e.Skill == SkillKind.Shield:
                        // A shield skill: how long it lasts, so it flickers out in its last second.
                        if (views.TryGet(e.Entity, out var shielded)) shielded.ShieldFor(e.Value, now);
                        break;

                    // Prompt 17 C: the shield carrier's and generator's domes.
                    case SimEventKind.DomeHit:
                    case SimEventKind.DomeChanged:
                        DomeEvent(e, views, now);
                        break;

                    case SimEventKind.Damaged:
                        ShieldDamaged(e, views);
                        break;

                    case SimEventKind.VehicleRetired:
                        // A loaned escort flies home: it simply leaves, no wreck. Play-test 8 A (DECISIONS 22Q): an aircraft
                        // (the fire support's gunship) flies on off the map instead of vanishing where it was.
                        var leaving = views.Detach(e.Entity);
                        if (leaving == null) break;
                        if (leaving.Flying && leaving.Root != null)
                        {
                            leaving.Depart(now);
                            _departing.Add(leaving);
                        }
                        else Object.Destroy(leaving.Root.gameObject);
                        break;

                    case SimEventKind.VehicleDestroyed:
                        var view = views.Detach(e.Entity);
                        if (view == null) break;
                        // One death, one big blast. A vehicle with its own death explosion (the
                        // Explosion event a moment later) shows only the killing hit now, so the
                        // big blast does not look like this one restarting.
                        var blowsUp = e.DefId != null && _catalog.Vehicles.TryGetValue(e.DefId, out var lost) && lost.DeathExplosion != null;
                        // A boss goes up in stages until its great blast (the Explosion event, 2.6 s on).
                        if (view.Def.Boss) BossPartsDied(view, now);
                        if (view.Def.Boss && blowsUp) BossDeath(view, now);
                        if (view.Def.Static) FellDefence(view, now);
                        if (blowsUp) Pop(_kill, view.Position + Vector3.up * 0.8f, now);
                        // Aircraft burst into flames in the air, then fall (see Crash); a drone is a small blast (prompt 34 L7).
                        else Explode(view.Flying && WreckClasses.Of(view.Def) != WreckClass.Drone ? ExplosionTier.Large : ExplosionTier.Medium,
                            view.Position + Vector3.up, now);
                        // A ship lists, breaks and sinks (prompt 16); everything else leaves a burning wreck. Prompt 34 L7: a shot-down
                        // aircraft's wreck flies onto the Sim's crash plan (the event's Target, in Value seconds).
                        if (view.Def.Naval != null) _sinking.Add(view, now);
                        else if (view.Flying && e.Value > 0f) _wrecks.Add(view, now, Ground(e.Target, 0f), e.Value);
                        else _wrecks.Add(view, now);
                        break;

                    case SimEventKind.PropDestroyed when e.Tier == ExplosionTier.Small && e.Target != default:
                        // A tree or fence knocked down by a hull: it falls, a puff of dust and leaves.
                        if (map.Topple(e.Entity, new Vector3(e.Target.X, 0f, e.Target.Y)))
                        {
                            var at = new Vector3(e.Position.X, 0.3f, e.Position.Y);
                            _emitters.Dust(at, 1.2f);
                            if (_models.Has("debris_leaves"))
                                for (var k = 0; k < 3; k++)
                                    _debris.Throw(Chunk("debris_leaves"), at + Vector3.up * UnityEngine.Random.Range(1f, 3f), UnityEngine.Random.rotation,
                                        at - Vector3.up, 3f, now);
                        }
                        break;

                    case SimEventKind.PropDestroyed:
                        if (!map.TryDestroy(e.Entity, out var prop)) break;
                        var centre = prop.Transform.position;
                        if (prop.IsBuilding)
                        {
                            // A building comes down in its own dust (MapView sinks the walls into the heap).
                            if (_cull.Visible(centre, 0.4f)) _collapse.Play(centre, now, Mathf.Clamp(prop.Prop.Radius / 5f, 0.8f, 1.8f));
                            // The rubble keeps burning in a couple of places.
                            var reach = prop.Prop.Radius * 0.4f;
                            _fires.Ignite(centre + new Vector3(UnityEngine.Random.Range(-reach, reach), 0f, UnityEngine.Random.Range(-reach, reach)),
                                1.1f, 35f, now);
                            _fires.Ignite(centre + new Vector3(UnityEngine.Random.Range(-reach, reach), 0f, UnityEngine.Random.Range(-reach, reach)),
                                0.7f, 22f, now);
                        }
                        var spread = Mathf.Max(0.5f, prop.Prop.Radius * 0.6f);
                        var force = prop.IsBuilding ? 10f : 7f;
                        // Big buildings throw their chunk set twice over.
                        var throws = prop.IsBuilding && prop.Prop.Radius > 5f ? prop.Debris.Count * 2 : prop.Debris.Count;
                        for (var k = 0; k < throws; k++)
                        {
                            var id = prop.Debris[k % prop.Debris.Count];
                            var offset = new Vector3(UnityEngine.Random.Range(-spread, spread), UnityEngine.Random.Range(0.4f, 2.5f),
                                UnityEngine.Random.Range(-spread, spread));
                            _debris.Throw(Chunk(id), centre + offset, UnityEngine.Random.rotation, centre - Vector3.up, force, now);
                        }
                        break;
                }
            }
        }

        /// <summary>A shot-down aircraft hitting the ground: a big blast, burning wreckage and a crater.</summary>
        private void Crash(Vector3 at, float size, float now)
        {
            Explode(size >= 2.5f ? ExplosionTier.Huge : ExplosionTier.Large, at + Vector3.up * 0.6f, now);
            _decals.Place(new Vector3(at.x, 0.15f, at.z), 5f, EffectLife.Crater(EffectLife.Top));
            _fires.Ignite(at + new Vector3(UnityEngine.Random.Range(-1.5f, 1.5f), 0f, UnityEngine.Random.Range(-1.5f, 1.5f)), 0.8f, 20f, now);
            var metal = Chunk("debris_metal");
            for (var i = 0; i < 8; i++)
                _debris.Throw(metal, at + new Vector3(UnityEngine.Random.Range(-1f, 1f), 0.8f, UnityEngine.Random.Range(-1f, 1f)),
                    UnityEngine.Random.rotation, at - Vector3.up, 11f, now);
        }

        /// <summary>Draws what is not a scene object (flying debris); call every frame, paused or not.</summary>
        public void Draw() => _debris.Draw(Time.time);

        /// <summary>This frame's shots and charges, waiting for the vehicles to be drawn (see <see cref="LaunchShots"/>).</summary>
        private readonly List<(SimEvent e, VehicleView shooter)> _shots = new();

        /// <summary>
        /// Starts this frame's shots; called right after the vehicles are drawn (their frame's hull,
        /// turret, barrel and flight pose), so every round, flash and trail leaves from where its
        /// barrel's tip is on screen in this frame. Read during the step instead, the muzzle was
        /// the one drawn the frame before, a step behind the turret and the hull: rounds started
        /// off the barrel by however far the vehicle had moved, turned or climbed since.
        /// </summary>
        public void LaunchShots(ViewRegistry views)
        {
            var now = Time.time;
            // Muzzle flashes ride their barrels' tips and flame streams their nozzles as just drawn (DECISIONS 12A).
            _muzzle.Follow(now);
            _emitters.FeedFlames(now, Time.deltaTime);
            if (_shots.Count == 0) return;
            _volley.Clear();
            foreach (var (e, shooter) in _shots)
            {
                if (e.Kind == SimEventKind.WeaponCharging)
                {
                    _weapons.Charging(e, shooter, now);
                    continue;
                }
                // Prompt 29 G1 (ASSET_DEBT "Gungnir's line warning"): a pierce shot's FiredWith (the bombard's gun, the warning as its
                // travel time) draws its aiming line, gun to aim, for the warning; drawn even when both ends are off screen.
                if (shooter != null && e.Kind == SimEventKind.WeaponFired && shooter.Sim.Def.Bombard is { PierceMax: > 0 } pierce &&
                    e.DefId != null && e.DefId == pierce.Weapon && e.Value > 0.2f)
                    _aimLines.Show(Ground(e.Position, 0.6f), Ground(e.Target, 0.6f), e.Value, now);
                // Shots entirely off screen are not drawn (the sound still plays).
                if (!_cull.Visible(Ground(e.Position, 1f), 0.15f) && !_cull.Visible(Ground(e.Target, 1f), 0.15f)) continue;
                // Prompt 34 L4: a simultaneous volley's barrels flash one after another, BarrelGap apart.
                var stagger = shooter != null ? BarrelStagger(e, shooter) : 0f;
                if (stagger > 0f) LaterShot(e, shooter, views, now + stagger, stagger);
                else _weapons.Fired(e, shooter, views, now);
                // Prompt 34 L3, fix prompt L5: an enemy's T4+ round (a gun from 203 mm, a 400 kg bomb, a 300 mm rocket; any shooter,
                // not only a boss) warns by escape time, its edge and its core, for its whole warning. Nothing of ours, and no
                // small or medium shell (prompt 26 B.4's 0.8 s ring on a boss's 5 m shells is gone).
                if (shooter != null && shooter.Sim.Team != views.PlayerTeam && e.Kind == SimEventKind.WeaponFired && e.DefId != null &&
                    _catalog.Weapons.TryGetValue(e.DefId, out var big) && !big.Laid)
                    EscapeRing(e, shooter, big, now);
                // Prompt 34 L8: a preview shows every blast round of its unit landing inside its ring, at the round's real size.
                if (PreviewRings && shooter != null && e.Kind == SimEventKind.WeaponFired && shooter.Sim.Team == 0 && e.DefId != null &&
                    _catalog.Weapons.TryGetValue(e.DefId, out var shown))
                    PreviewRing(e, shooter, shown, now);
                // At night the flash lights the ground at the muzzle.
                if (shooter != null && shooter.Root != null && !shooter.Flying && e.DefId != null &&
                    _catalog.Weapons.TryGetValue(e.DefId, out var fired))
                    _night.Flash(shooter.LastMuzzleNode != null ? shooter.LastMuzzleNode.TransformPoint(shooter.LastMuzzleLocal)
                            : shooter.Position + shooter.Root.forward * shooter.Sim.Radius,
                        fired.Projectile == ProjectileKind.Bullet ? 1.6f : fired.Projectile == ProjectileKind.Shell ? 4.5f : 3.2f);
            }
            _shots.Clear();
        }

        /// <summary>The point nearest <paramref name="to"/>, or null when there are none.</summary>
        private static Transform NearestPoint(IReadOnlyList<Transform> points, Vector3 to)
        {
            Transform best = null;
            var bestDistance = float.MaxValue;
            for (var i = 0; i < points.Count; i++)
            {
                if (points[i] == null) continue;
                var d = (points[i].position - to).sqrMagnitude;
                if (d >= bestDistance) continue;
                bestDistance = d;
                best = points[i];
            }
            return best;
        }

        /// <summary>Brief ring at a commanded destination, confirming the order landed.</summary>
        public void ShowMoveMarker(Vector3 point)
        {
            _marker.Transform.position = new Vector3(point.x, 0.08f, point.z);
            _marker.Visible = true;
            _markerStart = Time.unscaledTime;
        }

        /// <summary>Device check for blasts and smoke screens drawn together: a screen at <paramref name="at"/>.</summary>
        public void DebugSmokeScreen(Vector3 at) => _strikes.DebugSmoke(at, Time.time);

        public void Tick(ViewRegistry views)
        {
            var now = Time.time;
            TickShields(views, now);
            TickUnitDomes(views, now);
            _tracers.Tick(now, _emitters);
            _projectiles.Tick(now, _emitters);
            _weapons.Tick(now);
            _lasers.Tick(now, Time.deltaTime, views);
            for (var i = _later.Count - 1; i >= 0; i--)
            {
                if (now < _later[i].at) continue;
                var run = _later[i].run;
                _later.RemoveAt(i);
                run();
            }
            _emitters.Tick(now, Time.deltaTime);
            _strikes.Tick(now);
            _bigZones.Tick(views, now);
            _escape.Tick(now);
            // Fix prompt L6: the lingering smoke columns and the craters' lives.
            _smoke.Tick(now);
            _decals.Tick(now);
            // Fix prompt L5: the rings offered this frame decide what is drawn next frame.
            _gate.PlayerTeam = views.PlayerTeam;
            _strikes.PlayerTeam = views.PlayerTeam;
            _gate.Resolve(views, _camera.Focus);
            _aimLines.Tick(now);
            TickBigCharge(views, now);
            _drops.Tick(now);
            _ingress.Tick(now);
            JetTrails(views, now);
            KeepBossInSight(views);
            _night.Tick(now, Time.deltaTime, _camera.Focus);
            foreach (var blast in _blasts) blast.Tick(now);
            _muzzle.Tick(now);
            _debris.Tick(now, Time.deltaTime);
            _wrecks.Focus = _camera.Focus;
            _wrecks.Tick(now, Time.deltaTime);
            // Prompt 34 L7: a wreck that has gone leaves a burn mark.
            while (_wrecks.TryBurnMark(out var mark, out var markSize)) _decals.Place(mark, markSize);
            _sinking.Tick(now);
            for (var i = _departing.Count - 1; i >= 0; i--)
            {
                if (_departing[i].Departing(now, Time.deltaTime)) continue;
                if (_departing[i].Root != null) Object.Destroy(_departing[i].Root.gameObject);
                _departing.RemoveAt(i);
            }
            _fires.Tick(now, Time.deltaTime);
            // Secondary explosions in burning hulks: small pops around the big blast, never another big one.
            while (_wrecks.TryCookOff(now, out var cookOff, out var pop))
            {
                if (pop) Pop(_pop, cookOff, now);
                else Explode(ExplosionTier.Small, cookOff, now);
            }
            while (_wrecks.TryCrash(out var crash, out var size)) Crash(crash, size, now);
            KickUpDust(views, now);
            PrintTracks(views);
            ShowDamage(views, now);
            ShowStunned(views, now);
            WarnLaunchers(views, now);
            TickBossParts(views, now, Time.deltaTime);

            var markerAge = Time.unscaledTime - _markerStart;
            if (markerAge < 0.6f) _marker.Set(new Color(0.7f, 2f, 1.3f, 1f), Color.white, markerAge / 0.6f);
            else _marker.Visible = false;
        }

        private static readonly int ClearId = Shader.PropertyToID("_MbClear");

        /// <summary>
        /// The boss nearest the view is never lost in the smoke and fire of the strikes on it: the
        /// particle shaders thin what lies over it on screen (MbClear.hlsl).
        /// </summary>
        private void KeepBossInSight(ViewRegistry views)
        {
            var clear = Vector4.zero;
            var best = float.MaxValue;
            foreach (var view in views.All)
            {
                if (!view.Def.Boss || view.IsWreck) continue;
                var d = (view.Position - _camera.Focus).sqrMagnitude;
                if (d >= best) continue;
                best = d;
                var centre = view.Position + Vector3.up * (view.Flying ? 0f : 2.5f);
                clear = new Vector4(centre.x, centre.y, centre.z, view.Def.Radius * 1.25f + 2f);
            }
            Shader.SetGlobalVector(ClearId, clear);
        }

        public void Dispose()
        {
            Shader.SetGlobalVector(ClearId, Vector4.zero);
            HeatLights.Clear();
            _wrecks.Clear();
            foreach (var leaving in _departing)
                if (leaving.Root != null) Object.Destroy(leaving.Root.gameObject);
            _departing.Clear();
            if (_root != null) Object.Destroy(_root.gameObject);
        }

        /// <summary>
        /// Damage shows on the hull: below 60 % health a vehicle smokes, pale at first and blacker
        /// as it weakens; below 30 % it burns (play-test 5, DECISIONS 20V: <see cref="HullFire"/>, a
        /// flame core, tongues of flame, embers and a dark smoke column on one to three fire points,
        /// growing with the damage); the hull itself darkens with soot. Aircraft trail their smoke. Play-test 8
        /// (DECISIONS 22R): a burning vehicle's fire lights its hull and the ground round it, every frame (HeatLights).
        /// </summary>
        private void ShowDamage(ViewRegistry views, float now)
        {
            var all = views.All;
            HeatLights.Begin();
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                var sim = view.Sim;
                var health = sim.MaxHp > 0f ? sim.Hp / sim.MaxHp : 1f;
                view.Scorch(health);
                if (health >= 0.6f) continue;
                var seen = _cull.Visible(view.Position, 0.15f);
                if (seen && health < HullFire.Burning && !view.IsWreck) HullFire.Light(view, health, now);
                if (now < view.DamageFxAt || !seen) continue;
                var burning = health < HullFire.Burning;
                view.DamageFxAt = now + (burning ? HullFire.Next : Mathf.Lerp(0.18f, 0.4f, (health - 0.3f) / 0.3f));
                var radius = sim.Radius;
                var root = view.Root;
                if (view.Def.Static)
                {
                    DefenceDamage(view, health, burning, now);
                    continue;
                }
                if (burning)
                {
                    // The fire brings its own black smoke column; a spark or a small pop now and then near death.
                    _hullFire.Feed(view, health, _fireBeat++);
                    if (health < 0.12f && UnityEngine.Random.value < 0.01f) Pop(_pop, view.Position + Vector3.up * view.Top * 0.6f, now);
                    continue;
                }
                var top = view.Position + Vector3.up * (view.Flying ? 0.4f : 1.4f) - root.forward * radius * 0.3f;
                _emitters.DamageSmoke(top, radius * 0.8f, Mathf.Clamp01((health - 0.3f) / 0.3f) * 0.8f + 0.2f);
            }
            HeatLights.Commit();
        }

        private int _fireBeat;

        private static readonly Color KillBlue = new(0.55f, 0.85f, 1f, 1f);

        private float _warnAt;

        /// <summary>
        /// Play-test 6 (DECISIONS 21H): launchers (VehicleView.Launchers) with an enemy of a layer they fire at inside a
        /// quarter past their reach are marked, five times a second, so they raise their launcher before the sim fires.
        /// </summary>
        private void WarnLaunchers(ViewRegistry views, float now)
        {
            if (now < _warnAt) return;
            _warnAt = now + 0.2f;
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var launcher = all[i];
                var reach = launcher.LauncherReach(out var layers);
                if (reach <= 0f || !launcher.Sim.IsAlive) continue;
                var at = launcher.Position;
                for (var j = 0; j < all.Count; j++)
                {
                    var enemy = all[j];
                    if (enemy.Sim.Team == launcher.Sim.Team || !enemy.Sim.IsAlive) continue;
                    if ((layers & (enemy.Flying ? TargetLayers.Air : TargetLayers.Ground)) == 0) continue;
                    var d = enemy.Position - at;
                    d.y = 0f;
                    if (d.sqrMagnitude > reach * reach) continue;
                    launcher.ThreatAt = Time.time;
                    break;
                }
            }
        }

        /// <summary>
        /// Play-test 6 (DECISIONS 21H): the SEAD strike's anti-radiation missile strikes its air defence: on top of the
        /// warhead's blast, an electronic kill (after the HARM hits of Battlefield and Wargame): a white-blue flash and
        /// two electric shock rings, arcs crawling over the vehicle, a shower of hot and blue sparks and the smoke of
        /// burnt-out electronics; the radar stops dead and slumps (VehicleView.Spin) while it is knocked out.
        /// </summary>
        private void SeadKill(Vector3 at, ViewRegistry views, float now)
        {
            VehicleView victim = null;
            var best = 16f;
            foreach (var view in views.All)
            {
                var d = (view.Position - at).sqrMagnitude;
                if (d < best && view.Sim.IsAlive) (best, victim) = (d, view);
            }
            var top = victim != null ? victim.Position + Vector3.up * victim.Top * 0.8f : at + Vector3.up * 1.6f;
            var reach = victim != null ? Mathf.Max(1.6f, victim.Sim.Radius) : 2f;
            _emitters.Charge(top, 5f);
            _emitters.Charge(top, 3f);
            Ring(at, 10f, new Color(0.45f, 0.8f, 2.6f, 1f));
            Ring(at, 6f, new Color(0.9f, 1.4f, 3f, 1f));
            for (var k = 0; k < (Low ? 3 : 7); k++) Arcs(top + UnityEngine.Random.insideUnitSphere * reach * 0.5f, reach * 1.4f, 5);
            for (var k = 0; k < (Low ? 20 : 48); k++)
                _layers.Sparks.Emit(new ParticleSystem.EmitParams
                {
                    position = top, velocity = (UnityEngine.Random.onUnitSphere + Vector3.up * 0.6f) * UnityEngine.Random.Range(5f, 14f),
                    startSize = UnityEngine.Random.Range(0.08f, 0.16f), startLifetime = UnityEngine.Random.Range(0.3f, 0.8f),
                    startColor = k % 3 == 0 ? KillBlue : new Color(1f, 0.8f, 0.45f, 1f), applyShapeToPosition = false,
                }, 1);
            _emitters.DamageSmoke(top, reach * 1.1f, 0.25f);
            _night.Blast(top, 9f, 0.5f);
        }

        /// <summary>
        /// Play-test 6: a vehicle knocked out (an EMP's or a SEAD strike's stun) shows it for as long as it lasts: electric
        /// arcs crackle over the hull, blue sparks spit off it and burnt electronics smoke; its radar hangs dead
        /// (VehicleView.Spin). Low: a glow point for the arcs, fewer sparks.
        /// </summary>
        private void ShowStunned(ViewRegistry views, float now)
        {
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                // Play-test 10: by KnockedOut, not Stunned, which a range dummy always is (every In action target crackled and smoked).
                if (!view.Sim.KnockedOut || !view.Sim.IsAlive || now < view.StunFxAt || !_cull.Visible(view.Position, 0.15f)) continue;
                view.StunFxAt = now + (Low ? 0.34f : 0.18f) * UnityEngine.Random.Range(0.8f, 1.3f);
                var r = Mathf.Max(1f, view.Sim.Radius * 0.6f);
                var top = view.Position + Vector3.up * view.Top * 0.75f + UnityEngine.Random.insideUnitSphere * r * 0.5f;
                if (Low) _emitters.Charge(top, 0.4f);
                else Arcs(top, r, 4);
                _layers.Sparks.Emit(new ParticleSystem.EmitParams
                {
                    position = top, velocity = Vector3.up * 3f + UnityEngine.Random.insideUnitSphere * 3.5f, startSize = 0.1f,
                    startLifetime = 0.45f, startColor = KillBlue, applyShapeToPosition = false,
                }, Low ? 2 : 4);
                if (UnityEngine.Random.value < 0.25f) _emitters.DamageSmoke(top, r * 0.7f, 0.5f);
            }
        }

        /// <summary>Dust clouds behind the tracks of moving vehicles.</summary>
        private void KickUpDust(ViewRegistry views, float now)
        {
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                var speed = view.Speed;
                if (!_cull.Visible(view.Position, 0.1f)) continue;
                if (view.Flying || speed < 1.2f || now < view.DustAt) continue;
                view.DustAt = now + Mathf.Lerp(0.2f, 0.07f, Mathf.Clamp01(speed / 10f));
                var root = view.Root;
                var radius = view.Sim.Radius;
                var rear = root.position - root.forward * radius * 0.8f + Vector3.up * 0.3f;
                var scale = radius * 0.75f;
                _emitters.Dust(rear + root.right * radius * 0.55f, scale);
                _emitters.Dust(rear - root.right * radius * 0.55f, scale);
            }
        }

        /// <summary>Two lines of track marks behind every ground vehicle on the move, printed every 0.8 m.</summary>
        private void PrintTracks(ViewRegistry views)
        {
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                if (view.Flying || view.Def.Static || view.Speed < 0.3f) continue;
                var at = view.Position;
                if ((at - view.TrackAt).sqrMagnitude < 0.64f) continue;
                view.TrackAt = at;
                if (!_cull.Visible(at, 0.1f)) continue;
                var root = view.Root;
                var gauge = view.Def.Width * view.DrawScale * 0.36f;
                var width = Mathf.Clamp(view.Def.Width * view.DrawScale * 0.2f, 0.28f, 0.75f);
                var heading = root.eulerAngles.y;
                _tracks.Print(at + root.right * gauge, heading, width);
                _tracks.Print(at - root.right * gauge, heading, width);
            }
        }

        private ChunkModel Chunk(string modelId)
        {
            if (!_chunks.TryGetValue(modelId, out var chunk)) _chunks[modelId] = chunk = _models.Chunk(modelId);
            return chunk;
        }

        /// <param name="radius">Prompt 25 A5: how far the blast reaches (its ring is drawn there); 0 for the recipe's ring.</param>
        private void Airburst(Vector3 position, ExplosionTier tier, float now, float size = 1f, float radius = 0f)
        {
            if (!_cull.Visible(position, 0.3f * size)) return;
            var scale = (tier >= ExplosionTier.Huge ? 1.8f : tier >= ExplosionTier.Large ? 1.35f : 1f) * size;
            _airburst.Play(position, now, scale, BlastSizes.Bigger, 1f, BlastSizes.RingFor(radius, _airburst.RingReach, scale));
            Shake(position, tier >= ExplosionTier.Large ? 0.3f : 0.1f);
        }

        /// <summary>Builds everything that would otherwise be created the first time it is needed mid-battle.</summary>
        public void Prewarm()
        {
            WarmUpPipelines();
            WarmUpShields();
            foreach (var id in new[] { "missile", "rocket", "bomb", "cruise_missile" })
                if (_models.Has(id)) _models.Merged(id);
            foreach (var id in new[] { "debris_concrete", "debris_plaster", "debris_roof", "debris_wood", "debris_metal", "debris_leaves" })
                if (_models.Has(id)) Chunk(id);
        }

        /// <summary>
        /// Draws every effect layer once, a speck too small to see, at the start of the battle. On
        /// Vulkan the driver builds a pipeline the first time each material and vertex layout is
        /// drawn, which stalls that frame: done here, under the load, instead of the first time a
        /// napalm strike or a burning wreck appears mid-fight.
        /// </summary>
        private void WarmUpPipelines()
        {
            var at = _camera.Focus + Vector3.up * 0.5f;
            foreach (var system in _root.GetComponentsInChildren<ParticleSystem>(true))
            {
                if (!system.gameObject.activeInHierarchy) continue;
                system.Emit(new ParticleSystem.EmitParams
                {
                    position = at, startSize = 0.005f, startLifetime = 0.05f, velocity = Vector3.zero, applyShapeToPosition = false,
                }, 1);
            }
        }

        /// <summary>
        /// A damaged fixed defence: smoke pours from its top, grey and then black; badly hit, it
        /// burns in two places, sparks spray and its ammunition pops now and then.
        /// </summary>
        private void DefenceDamage(VehicleView view, float health, bool burning, float now)
        {
            var radius = view.Sim.Radius;
            var top = view.Position + Vector3.up * view.Top;
            _emitters.DamageSmoke(top + UnityEngine.Random.insideUnitSphere * radius * 0.3f, radius * (burning ? 1.3f : 0.95f),
                burning ? 0f : Mathf.Clamp01((health - 0.3f) / 0.3f) * 0.8f + 0.2f);
            if (!burning) return;
            // A burning defence burns like a vehicle (play-test 5): its fire points on the roof, round its top.
            _hullFire.Feed(view, health, _fireBeat++);
            if (UnityEngine.Random.value < 0.12f)
                _layers.Sparks.Emit(new ParticleSystem.EmitParams
                {
                    position = top, velocity = Vector3.up * 5f + UnityEngine.Random.insideUnitSphere * 4f, startSize = 0.18f,
                    startLifetime = 0.9f, applyShapeToPosition = false,
                }, 10);
            if (health < 0.2f && UnityEngine.Random.value < 0.035f) Pop(_pop, top + UnityEngine.Random.insideUnitSphere * radius * 0.5f, now);
        }

        /// <summary>A fixed defence destroyed: a big blast at its top, a skirt of dust, and concrete and steel thrown out.</summary>
        private void FellDefence(VehicleView view, float now)
        {
            var at = view.Position;
            var radius = view.Sim.Radius;
            Explode(ExplosionTier.Huge, at + Vector3.up * view.Top * 0.6f, now, Mathf.Clamp(radius / 2.5f, 0.9f, 1.5f));
            if (_cull.Visible(at, 0.4f)) _collapse.Play(at, now, Mathf.Clamp(radius / 3f, 0.7f, 1.4f));
            // Play-test 5 (DECISIONS 20V): the ground scorched round the ruin.
            _decals.Place(new Vector3(at.x, 0.15f, at.z), Mathf.Max(4f, radius * 2.2f));
            var throws = 6 + (int)(radius * 3f);
            for (var k = 0; k < throws; k++)
            {
                var id = k % 3 == 0 ? "debris_metal" : "debris_concrete";
                if (!_models.Has(id)) continue;
                var offset = new Vector3(UnityEngine.Random.Range(-radius, radius), UnityEngine.Random.Range(0.5f, view.Top),
                    UnityEngine.Random.Range(-radius, radius));
                _debris.Throw(Chunk(id), at + offset, UnityEngine.Random.rotation, at - Vector3.up, 9f, now);
            }
        }

        /// <summary>Items that do no damage (EMP, shield dome, airdrops, loaned escorts) show a pulse, not a blast.</summary>
        private bool IsGentle(string defId) =>
            defId != null && _catalog.TryGetSupport(defId, out var support) &&
            support.Kind is SupportKind.Emp or SupportKind.ShieldDome or SupportKind.Reinforce or SupportKind.Escort
                or SupportKind.Scan or SupportKind.Tower or SupportKind.Minefield;

        private void Pulse(string defId, Vector3 at)
        {
            if (!_catalog.TryGetSupport(defId, out var support)) return;
            switch (support.Kind)
            {
                case SupportKind.Emp:
                    // An electric-blue shockwave the size of the blast, twice over.
                    Ring(at, support.Radius * 2.2f, new Color(0.45f, 0.8f, 2.6f, 1f));
                    Ring(at, support.Radius * 1.4f, new Color(0.9f, 1.4f, 3f, 1f));
                    break;
                case SupportKind.ShieldDome:
                    // Its dome comes up instead, with a ring in its side's colour (RaiseItemDome).
                    break;
                case SupportKind.Escort:
                    // An aircraft on its way: a small mark where it was called, no gust of dust.
                    Ring(at, 6f, new Color(0.7f, 1.2f, 1.6f, 0.6f));
                    break;
                case SupportKind.Scan:
                    // The drone's sensor sweep: a radar-cyan ring the size of what it sees.
                    Ring(at, support.Radius * 2f, new Color(0.3f, 1.4f, 2f, 0.7f));
                    break;
                case SupportKind.Minefield:
                    // Each mine thuds into the ground in a small puff of dirt.
                    Ring(at, 2.2f, new Color(1.1f, 0.95f, 0.75f, 0.7f));
                    _emitters.Dust(at, 2f);
                    break;
                case SupportKind.Tower:
                    Ring(at, 8f, new Color(1.2f, 1.1f, 0.9f, 0.8f));
                    break;
                default:
                    // Airdrops land in a gust of dust.
                    Ring(at, 14f, new Color(1.2f, 1.1f, 0.9f, 0.8f));
                    break;
            }
        }

        /// <summary>One expanding ground ring of the given size and colour (the shockwave layer, tinted).</summary>
        /// <summary>An ability's pulse on the ground (a jammer's field, a command aura; the In action range): a ring <paramref name="size"/> across.</summary>
        public void AbilityRing(Vector3 at, float size, Color colour) => Ring(at, size, colour);

        /// <summary>Prompt 25 A5: the faint ring a small splash round (flak, a grenade) shows its blast radius with.</summary>
        private static readonly Color LoneRing = new(0.95f, 0.9f, 0.75f, 0.35f);

        /// <summary>Prompt 26 B.4: a boss shell with at least this blast core warns of where it falls.</summary>
        private const float BossShellWarnFrom = 5f;



        /// <summary>Prompt 26 B.3: the ring of a two-layer blast's edge (a warm, fainter ring than the core's own), drawn when the edge is wider than the core.</summary>
        private static readonly Color EdgeRingColour = new(1f, 0.62f, 0.3f, 0.5f);

        private void EdgeRing(Vector3 at, float core, float edge)
        {
            if (!(edge > core) || core <= 0f) return;
            Ring(at, BlastSizes.RingQuad(edge), EdgeRingColour);
        }

        private void Ring(Vector3 at, float size, Color colour)
        {
            if (!_cull.Visible(at, 0.2f)) return;
            var emit = new ParticleSystem.EmitParams
            {
                position = at + Vector3.up * 0.2f, startSize = size, startColor = colour, startLifetime = 0.6f,
                applyShapeToPosition = false,
            };
            _layers.Shockwave.Emit(emit, 1);
        }

        /// <summary>Effects due later: the stages of a boss's death, a thermobaric ignition.</summary>
        private readonly List<(float at, Action run)> _later = new();

        private readonly HashSet<MachineBrigade.Sim.Core.EntityId> _dyingBosses = new();

        private void Later(float at, Action run) => _later.Add((at, run));

        /// <summary>
        /// A boss taking its death blows: blasts break out across its hull one after another,
        /// growing, with burning debris, for two and a half seconds before the great blast.
        /// </summary>
        private void BossDeath(VehicleView view, float now)
        {
            _dyingBosses.Add(view.Id);
            var centre = view.Position;
            var reach = Mathf.Max(3f, view.Sim.Radius * 0.8f);
            for (var i = 0; i < 6; i++)
            {
                var at = now + 0.1f + i * 0.4f + UnityEngine.Random.Range(0f, 0.15f);
                var offset = new Vector3(UnityEngine.Random.Range(-reach, reach), UnityEngine.Random.Range(0.5f, 2.5f), UnityEngine.Random.Range(-reach, reach));
                var tier = i < 3 ? ExplosionTier.Large : ExplosionTier.Huge;
                var grow = 0.8f + i * 0.12f;
                Later(at, () =>
                {
                    Explode(tier, centre + offset, at, grow, flash: false);
                    _muzzle.SparkBurst(centre + offset, Vector3.up, 20, 8f, 18f);
                });
            }
        }

        /// <summary>
        /// A boss's great blast: a white flash over the whole view, a shock ring racing across the
        /// ground, the fireball at twice the size and three more round it, a pillar of smoke.
        /// </summary>
        private void BossFinale(in SimEvent e, float now)
        {
            var blast = Ground(e.Position, 0.3f);
            var radius = Mathf.Max(8f, e.Value);
            Flash?.Invoke(0.75f);
            Ring(blast, radius * 4.5f, new Color(2.4f, 2.1f, 1.7f, 1f));
            Ring(blast, radius * 2.6f, new Color(2.6f, 1.4f, 0.5f, 1f));
            _explosions[ExplosionTier.Ultimate].Play(blast, now, 1.9f, BlastSizes.Bigger);
            _night.Blast(blast, 45f, 1.4f);
            Shake(blast, 1.4f);
            for (var i = 0; i < 3; i++)
            {
                var at = now + 0.15f + i * 0.18f;
                var angle = i * 2.1f + UnityEngine.Random.value;
                var offset = new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * radius * 0.6f;
                Later(at, () => Explode(ExplosionTier.Huge, blast + offset + Vector3.up, at, 1.2f, flash: false));
            }
            _decals.Place(blast, radius * 1.4f);
            // DECISIONS 20Y: the blaze as big, burning 24 s (was 40) under thinner, lighter smoke that clears soon after.
            _fires.Ignite(blast, 2f, 24f, now, smoke: FireSpots.BossSmoke);
            for (var i = 0; i < 3; i++)
                _emitters.DamageSmoke(blast + UnityEngine.Random.insideUnitSphere * radius * 0.4f + Vector3.up * 2f, radius * 0.45f, 0.35f);
        }

        /// <summary>
        /// A round's own impact, by what it is: true when it was drawn here. A tank's dart or an
        /// autocannon's AP round strikes sparks; a HEAT warhead flashes sharp and small; a high-
        /// explosive shell throws up earth and black smoke; a mortar bomb a round dust dome;
        /// thermobaric fuel ignites a second, bigger fireball; a bomb a shock ring and a column.
        /// </summary>
        private bool ImpactOfKind(WeaponDef round, in SimEvent e, Vector3 impact, float now, float size)
        {
            if (round == null || !_cull.Visible(impact, 0.3f)) return false;
            var from = new Vector3(e.Position.X, 0f, e.Position.Y);
            switch (round.Projectile)
            {
                case ProjectileKind.Shell when round.PiercingLook:
                case ProjectileKind.Bullet when round.PiercingLook && round.Damage >= 20f:
                {
                    var heavy = round.Damage >= 150f;
                    if (round.Projectile == ProjectileKind.Shell)
                    {
                        // A tank's round: a hot burst off the armour, sized by the tank (DECISIONS 11A), a
                        // tenth bigger again and its fire and smoke lingering by the tank's class (12C).
                        var grow = BlastSizes.TankShell(round) * BlastSizes.Bigger;
                        var hitAt = impact + Vector3.up * 0.8f;
                        var hitScale = (heavy ? 1f : 0.75f) * (0.9f + 0.2f * UnityEngine.Random.value);
                        _shellHit.Play(hitAt, now, hitScale, grow, BlastSizes.ShellLife(round), BlastSizes.RingFor(e.Value, _shellHit.RingReach, hitScale));
                        // Prompt 34 L5: an AP round's sparks grow by its tier (1 to T2, +15 % a tier above).
                        var sparks = Mathf.RoundToInt((heavy ? 36 : 16) * TierFx.Extra(TierFx.Of(round)));
                        sparks += Mathf.RoundToInt(sparks * (grow - 1f) * ExplosionEffect.Density);
                        _muzzle.SparkBurst(hitAt + Vector3.up * 0.2f, Vector3.up + UnityEngine.Random.insideUnitSphere * 0.5f, sparks, 8f * grow,
                            (heavy ? 24f : 16f) * grow);
                        _night.Blast(hitAt, 3.5f * hitScale * grow, 0.4f);
                        Shake(hitAt, 0.03f * grow);
                        return true;
                    }
                    // Kinetic: a white-hot spray of sparks off the armour, a puff of metal dust.
                    Explode(ExplosionTier.Small, impact + Vector3.up * 0.8f, now, heavy ? 0.9f : 0.6f, flash: false);
                    _muzzle.SparkBurst(impact + Vector3.up * 1f, Vector3.up + UnityEngine.Random.insideUnitSphere * 0.5f, heavy ? 36 : 16, 8f, heavy ? 24f : 16f);
                    return true;
                }
                case ProjectileKind.Drone when round.PiercingLook && BlastSizes.Fpv(round):
                case ProjectileKind.Drone when round.PiercingLook && round.Id == "mothership_drones":
                {
                    // Test feedback 19P: an FPV quadcopter's charge, not a missile's: a white-hot star where it
                    // struck, the shaped charge's jet stabbing down into the roof, the drone flying apart in bright
                    // bits all round, and a small black puff; the blast as big as before.
                    var at = impact + Vector3.up * 0.9f;
                    Explode(ExplosionTier.Medium, at, now, 0.8f * size, flash: false, grow: BlastSizes.Drone(round), radius: e.Value);
                    _emitters.Charge(at + Vector3.up * 0.5f, 2.4f);
                    _emitters.Charge(at + Vector3.up * 0.4f, 1.6f);
                    _muzzle.SparkBurst(at + Vector3.up * 1.4f, Vector3.down, 22, 14f, 30f);
                    for (var k = 0; k < 6; k++)
                    {
                        var angle = k * Mathf.PI / 3f + UnityEngine.Random.value;
                        _muzzle.SparkBurst(at + Vector3.up * 0.7f, new Vector3(Mathf.Cos(angle), 0.6f, Mathf.Sin(angle)), 4, 4f, 10f, 1.3f);
                    }
                    _emitters.DamageSmoke(impact + Vector3.up * 1.2f, 1.3f, 0.06f);
                    return true;
                }
                case ProjectileKind.Missile when round.PiercingLook:
                case ProjectileKind.Drone when round.PiercingLook:
                    // HEAT: a sharp star flash and a jet of sparks, a small black puff. Drones by the drone (DECISIONS 12C),
                    // missiles a fifth bigger (play-test 5, DECISIONS 20V).
                    Explode(ExplosionTier.Medium, impact + Vector3.up * 0.8f, now, 0.8f * size, flash: false, grow: BlastSizes.Round(round), radius: e.Value);
                    _muzzle.SparkBurst(impact + Vector3.up, Vector3.up, Mathf.RoundToInt(18 * TierFx.Extra(TierFx.Of(round))), 10f, 22f);
                    _emitters.DamageSmoke(impact + Vector3.up * 1.2f, 1.6f, 0.08f);
                    return true;
                case ProjectileKind.Shell when round.DamageType == DamageType.HighExplosive && round.Indirect:
                {
                    // An HE shell or mortar bomb: the blast, then earth and black smoke hanging over it.
                    // (The siege tank's 203 mm is drawn half as big again; DECISIONS 11A. It lingers like a
                    // heavy tank's round, and the ring and smoke are a tenth bigger again; 12C.)
                    // Artillery and mortar shells a fifth bigger again (play-test 5, DECISIONS 20V).
                    var siege = BlastSizes.Artillery(round);
                    Explode(e.Tier, impact, now, size, flash: false, grow: siege, life: BlastSizes.GroundLife(round), radius: e.Value);
                    siege *= BlastSizes.Bigger;
                    // Prompt 25 A5: the dust ring on the damage radius too (it was 1.2 times it).
                    Ring(impact, e.Value > 0f ? BlastSizes.RingQuad(e.Value) : 4f * 2.2f * siege, new Color(0.75f, 0.66f, 0.5f, 0.55f));
                    var mortar = round.Id.StartsWith("mortar");
                    for (var i = 0; i < (mortar ? 2 : 3); i++)
                        _emitters.DamageSmoke(impact + UnityEngine.Random.insideUnitSphere * 1.2f * siege + Vector3.up * (1f + i) * siege,
                            Mathf.Max(2f, e.Value * 0.55f) * size * Mathf.Pow(siege, 0.65f), mortar ? 0.35f : 0.1f);
                    return true;
                }
                case ProjectileKind.Rocket when round.Id.StartsWith("thermobaric"):
                    // Thermobaric: the pop that spreads the fuel, then the ignition, much bigger (a rocket's: +20 %, 20V).
                    Explode(ExplosionTier.Medium, impact, now, size, flash: false, grow: BlastSizes.MissileGrow, radius: e.Value);
                    var cloud = Mathf.Max(6f, e.Value);
                    var cloudRing = e.Value > 0f ? BlastSizes.RingQuad(e.Value) : cloud * 2.5f * BlastSizes.Bigger * BlastSizes.MissileGrow;
                    // Prompt 34 L5: the second fireball grows by the round's tier.
                    var fuel = TierFx.Extra(TierFx.Of(round));
                    Later(now + 0.15f, () =>
                    {
                        _napalm.Play(impact + Vector3.up * 0.5f, now + 0.15f, 1.4f * size, BlastSizes.Bigger * BlastSizes.MissileGrow * fuel);
                        Ring(impact, cloudRing, new Color(2.2f, 1.2f, 0.4f, 0.8f));
                    });

                    return true;
                case ProjectileKind.Bomb:
                {
                    // A bomb: the fireball, a shock ring on the ground and a column of dust and smoke,
                    // drawn bigger by the bomb's weight (DECISIONS 11A).
                    var bomb = BlastSizes.Bomb(round.Id);
                    Explode(e.Tier, impact, now, size, flash: false, grow: bomb, radius: e.Value);
                    // The column a tenth bigger again, like the blast (DECISIONS 12C); the shock ring on the damage radius
                    // (prompt 25 A5: it was twice it).
                    bomb *= BlastSizes.Bigger;
                    Ring(impact, e.Value > 0f ? BlastSizes.RingQuad(e.Value) : 6f * 3f * bomb, new Color(1.2f, 1.1f, 0.9f, 0.7f));
                    for (var i = 0; i < 3; i++)
                        _emitters.DamageSmoke(impact + (Vector3.up * (1.5f + i * 1.5f) + UnityEngine.Random.insideUnitSphere) * bomb,
                            Mathf.Max(2.5f, e.Value * 0.6f) * Mathf.Pow(bomb, 0.65f), 0.3f);
                    return true;
                }
                default:
                    return false;
            }
        }

        /// <summary>A small effect with no shake (the killing hit, a cook-off pop).</summary>
        private void Pop(ExplosionEffect effect, Vector3 position, float now)
        {
            // A small blast all the same: a tenth bigger (DECISIONS 12C).
            if (_cull.Visible(position, 0.2f)) effect.Play(position, now, 1f, BlastSizes.Bigger);
        }

        /// <param name="grow">Enlarges the blast without blowing its sprites up (<see cref="ExplosionEffect.Play"/>).
        /// Every blast above the Small tier (bullets and flak) is a tenth bigger again (<see cref="BlastSizes.Bigger"/>).</param>
        /// <param name="exact">Drawn to a set size (a cruise missile matched to its blast radius): hardly varied.</param>
        /// <param name="life">Lingers: its fire, smoke, dust and embers last that much longer (<see cref="ExplosionEffect.Play"/>).</param>
        /// <param name="ring">The grow its ground ring keeps (a blast matched to its radius), or 0 for grow.</param>
        /// <param name="radius">Prompt 25 A5 (DECISIONS 25A): how far the blast's damage reaches; its ring is drawn exactly there
        /// (<see cref="BlastSizes.RingFor"/>, after the scale's variation), whatever its size or grow. 0: the ring by <paramref name="ring"/>.</param>
        private void Explode(ExplosionTier tier, Vector3 position, float now, float scale = 1f, bool flash = true, float grow = 1f,
            bool exact = false, float life = 1f, float ring = 0f, float radius = 0f)
        {
            // Off screen, a blast leaves its crater and fires (they persist) but no particles.
            if (!_cull.Visible(position, tier >= ExplosionTier.Huge ? 0.4f : 0.25f)) return;
            if (tier > ExplosionTier.Small) grow = Mathf.Max(1f, grow) * BlastSizes.Bigger;
            // No two blasts alike: a little bigger or smaller, a little off the exact point.
            scale *= exact ? 0.97f + 0.06f * UnityEngine.Random.value : 0.85f + 0.35f * UnityEngine.Random.value;
            position += new Vector3(UnityEngine.Random.Range(-0.4f, 0.4f), 0f, UnityEngine.Random.Range(-0.4f, 0.4f)) * scale;
            if (radius > 0f) ring = BlastSizes.RingFor(radius, _explosions[tier].RingReach, scale);
            _explosions[tier].Play(position, now, scale, grow, life, ring);
            // A blast with no ring of its own (the Small tier: flak, grenades) gets a faint lone one on its radius.
            if (radius > 0f && _explosions[tier].RingReach <= 0f) Ring(position, BlastSizes.RingQuad(radius), LoneRing);
            scale *= Mathf.Max(1f, grow);
            _night.Blast(position, scale * tier switch
            {
                ExplosionTier.Small => 3f,
                ExplosionTier.Medium => 5.5f,
                ExplosionTier.Large => 9f,
                ExplosionTier.Huge => 13f,
                _ => 18f,
            }, tier >= ExplosionTier.Huge ? 0.9f : 0.45f);
            // The biggest blasts light the whole screen for a moment (no shake): stronger the nearer the view.
            if (flash && tier >= ExplosionTier.Huge && Flash != null)
                Flash((tier >= ExplosionTier.Ultimate ? 0.22f : 0.11f) / (1f + Vector3.Distance(position, _camera.Focus) / 40f));
            Shake(position, tier switch
            {
                ExplosionTier.Small => 0f,
                ExplosionTier.Medium => 0.12f,
                ExplosionTier.Large => 0.35f,
                ExplosionTier.Huge => 0.7f,
                _ => 1f,
            });
        }

        private float _nextJetPuff;

        /// <summary>
        /// Jets in flight: a hot exhaust and a thin vapour trail behind the engines, and vortices
        /// streaming off the wingtips when they pull hard into a turn.
        /// </summary>
        /// <summary>What an aircraft's engines leave behind.</summary>
        private enum Engine
        {
            /// <summary>A fighter's afterburning jet: a flame at full power, a heat shimmer otherwise.</summary>
            Afterburner,

            /// <summary>A turbojet without afterburner (Su-25): a dull glow.</summary>
            Hot,

            /// <summary>A turbofan: a thin grey smoke line.</summary>
            Fan,

            /// <summary>An old turbofan (the B-52's eight): thick dark smoke.</summary>
            Smoky,

            /// <summary>A turboprop or a drone's pusher propeller: a faint exhaust.</summary>
            Prop,

            /// <summary>A helicopter: turbine exhausts, and the rotor's downwash raising dust below.</summary>
            Rotor,
        }

        /// <summary>
        /// Each aircraft's engines: the kind, and where they sit as fractions of the model's half-span
        /// (x) and half-length (z, negative towards the tail) and height (y), from its drawn bounds.
        /// </summary>
        private static (Engine kind, float[] x, float z, float y) EnginesOf(string model) => model switch
        {
            "fighter_jet" => (Engine.Afterburner, new[] { -0.1f, 0.1f }, -1f, 0f),
            "attack_jet" => (Engine.Hot, new[] { -0.12f, 0.12f }, -0.95f, 0f),
            "tank_buster" => (Engine.Fan, new[] { -0.17f, 0.17f }, -0.45f, 0.55f),
            "heavy_bomber" => (Engine.Smoky, new[] { -0.62f, -0.34f, 0.34f, 0.62f }, -0.05f, -0.2f),
            "stealth_bomber" => (Engine.Fan, new[] { -0.16f, 0.16f }, -0.25f, 0.3f),
            // Prompt 17 C.
            "stealth_fighter" => (Engine.Afterburner, new[] { -0.09f, 0.09f }, -1f, 0f),
            "wingman_drone" => (Engine.Hot, new[] { 0f }, -1f, 0.1f),
            "swarm_carrier" => (Engine.Prop, new[] { -0.55f, -0.28f, 0.28f, 0.55f }, 0.05f, 0.35f),
            "sky_gunship" or "transport_plane" => (Engine.Prop, new[] { -0.5f, -0.25f, 0.25f, 0.5f }, 0.05f, 0.35f),
            "strike_drone" or "recon_drone" => (Engine.Prop, new[] { 0f }, -1f, 0f),
            "strike_jet" => (Engine.Hot, new[] { 0f }, -1f, 0f),
            _ => (Engine.Rotor, new[] { -0.14f, 0.14f }, -0.15f, 0.55f),
        };

        private void JetTrails(ViewRegistry views, float now)
        {
            if (now < _nextJetPuff) return;
            _nextJetPuff = now + 0.04f;
            _jetTick++;
            foreach (var view in views.All)
            {
                if (!view.Flying || !view.Sim.IsAlive || view.Body == null || view.Def.Boss) continue;
                var body = view.Body;
                var at = body.position;
                if (at.y < 3f || !_cull.Visible(at, 0.5f)) continue;
                var forward = body.forward;
                var b = view.ModelBounds;
                var scale = view.DrawScale;
                var (kind, xs, z, y) = EnginesOf(view.Def.Model);
                var speed = view.Sim.Speed / Mathf.Max(1f, view.Def.Speed);
                // Vapour trails where the air is cold enough: long ones at bomber heights, none low down.
                var contrail = view.Altitude > 28f;
                foreach (var x in xs)
                {
                    var local = new Vector3(b.center.x + x * b.extents.x, b.center.y + y * b.extents.y, b.center.z + z * b.extents.z);
                    var engine = body.TransformPoint(local);
                    switch (kind)
                    {
                        case Engine.Afterburner:
                            if (speed > 0.92f) _emitters.Afterburner(engine, forward, 0.7f + scale * 0.5f);
                            else if ((_jetTick & 1) == 0) _emitters.Afterburner(engine, forward, 0.3f);
                            break;
                        case Engine.Hot:
                            if ((_jetTick & 1) == 0) _emitters.Afterburner(engine, forward, 0.35f + scale * 0.2f);
                            break;
                        case Engine.Fan:
                            if ((_jetTick & 3) == 0) _emitters.Trail(engine - forward * 0.3f, 0.22f + scale * 0.1f);
                            break;
                        case Engine.Smoky:
                            if ((_jetTick & 1) == 0) _emitters.DamageSmoke(engine - forward * 0.4f, 0.32f + scale * 0.12f, 0.18f);
                            break;
                        case Engine.Prop:
                            if ((_jetTick & 3) == 0) _emitters.Trail(engine - forward * 0.8f, 0.16f + scale * 0.06f);
                            break;
                        case Engine.Rotor:
                            if ((_jetTick & 3) == 0) _emitters.Trail(engine - forward * 0.3f + Vector3.up * 0.2f, 0.12f + scale * 0.05f);
                            break;
                    }
                    if (contrail && view.Def.FixedWing) _emitters.Contrail(engine - forward * 0.8f, 0.3f + scale * 0.08f, view.Altitude > 38f ? 2.6f : 1.2f);
                }
                if (view.Def.FixedWing && Mathf.Abs(view.Bank) > 22f)
                {
                    // Wingtip vortices in a hard turn.
                    var tip = body.right * b.extents.x * scale * 0.95f;
                    _emitters.Contrail(at + tip, 0.24f, 0.8f);
                    _emitters.Contrail(at - tip, 0.24f, 0.8f);
                }
                if (kind == Engine.Rotor && speed < 0.5f && (_jetTick % 5) == 0)
                {
                    // Downwash: the rotor blows dust out in a ring on the ground below.
                    var radius = b.extents.x * scale * 1.1f + 2f;
                    var angle = UnityEngine.Random.Range(0f, Mathf.PI * 2f);
                    var ground = new Vector3(at.x, 0.2f, at.z) + new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * radius;
                    _emitters.Dust(ground, 1.4f);
                }
            }
        }

        private int _jetTick;

        /// <summary>A brief flash of the whole screen, of the given strength (0 to 1): huge and ultimate blasts on screen.</summary>
        public Action<float> Flash { get; set; }

        /// <summary>
        /// A blast the game stages rather than the simulation (the fortress super-gun's muzzle, the
        /// shield dome going down): the tier's explosion, its light at night, flash and shake.
        /// </summary>
        public void Blast(ExplosionTier tier, Vector3 at, float scale = 1f) => Explode(tier, at, Time.time, scale);

        /// <summary>One expanding ring on the ground of the given size and colour (HDR), for staged moments.</summary>
        public void Shockwave(Vector3 at, float size, Color colour) => Ring(at, size, colour);

        private void Shake(Vector3 at, float amount)
        {
            if (amount <= 0f) return;
            var distance = Vector3.Distance(at, _camera.Focus);
            _camera.AddTrauma(amount / (1f + distance / 25f));
        }

        private static Vector3 Ground(System.Numerics.Vector2 p, float height) => new Vector3(p.X, height, p.Y);
    }
}
