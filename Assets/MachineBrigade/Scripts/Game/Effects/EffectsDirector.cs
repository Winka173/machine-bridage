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
        private readonly Emitters _emitters;
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
        private readonly ProjectilePool _projectiles;
        private readonly WeaponEffects _weapons;
        private readonly LaserBeams _lasers;
        private readonly StrikeEffects _strikes;
        private readonly AirDrops _drops;
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
            _tracks = new TrackMarks(materials, _root);
            _night = new NightLights(materials, _emitters, _root);
            _fires = new FireSpots(materials, _root);
            _fires.Visible = p => _cull.Visible(p, 0.3f);
            _decals = new DecalPool(meshes.ScorchQuad, _root, budget.Decals);
            _debris = new DebrisPool(budget.Debris);
            _layers.Chunks = new ChunkThrower(_debris, materials, models, _fires, _root);
            _layers.Chunks.Trails.Visible = p => _cull.Visible(p, 0.3f);
            _wrecks = new WreckManager(_fires, _layers.Chunks, budget.Wrecks);
            _projectiles = new ProjectilePool(_root, 96);
            _lasers = new LaserBeams(materials, _emitters, _decals, _root);
            _weapons = new WeaponEffects(catalog, models, _tracers, _projectiles, _emitters, _muzzle, Shake, _lasers);
            _strikes = new StrikeEffects(catalog, materials, meshes, models, _emitters, _projectiles, _layers.Screens, _root);
            _drops = new AirDrops(catalog, models, meshes, materials, _emitters, _root);

            _marker = new GroundMark("Move Marker", _root, meshes, materials, GroundMark.Style.Move);
            _marker.Transform.localScale = Vector3.one * 2.2f;
            _marker.Visible = false;
        }

        public void Consume(IReadOnlyList<SimEvent> events, ViewRegistry views, MapView map)
        {
            var now = Time.time;
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
                            var height = views.TryGet(e.Entity, out var struck) && struck.Flying ? struck.Altitude + 0.5f
                                : _wrecks.TryGetAircraftWreck(e.Entity, out var falling) ? falling.y + 0.5f : 15f;
                            var burst = new Vector3(e.Position.X, height, e.Position.Y);
                            if (e.Tier >= ExplosionTier.Medium) Airburst(burst, e.Tier, now);
                            else Explode(e.Tier, burst, now);
                            _emitters.Flak(burst);
                            break;
                        }
                        var impact = Ground(e.Position, 0.15f);
                        var round = e.DefId != null && _catalog.Weapons.TryGetValue(e.DefId, out var landed) ? landed : null;
                        var size = round?.ImpactScale ?? 1f;
                        // A gun's shell never flashes the screen, however big: only strikes and blasts do.
                        if (!ImpactOfKind(round, e, impact, now, size)) Explode(e.Tier, impact, now, size, flash: false, grow: BlastSizes.Drone(round));
                        if (e.Tier >= ExplosionTier.Medium)
                            _decals.Place(impact, (e.Tier >= ExplosionTier.Large ? 5f : 2.2f) * size * BlastSizes.Ground(round));
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
                        // Its ground ring stays on the radius while the rest grows a tenth (DECISIONS 12C).
                        Explode(e.Tier, hit, now, strikeScale, grow: strikeGrow, exact: matched, ring: matched ? strikeGrow : 0f);
                        _decals.Place(hit, Mathf.Max(4f, e.Value * (huge ? 1.4f : 1.1f)) * (matched ? 1f : strikeGrow));
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
                        else if (guard != null)
                        {
                            var from = guard.Position + Vector3.up * 2.4f + guard.Root.right * (e.Value * 1.3f);
                            _tracers.Launch(from, interceptAt, 0.06f, 0f, 0.12f, 1.2f, now);
                            _muzzle.Fire(MuzzleFx.Kind.Autocannon, from, interceptAt - from, now, 0.9f, guard.Position.y);
                        }
                        Pop(_pop, interceptAt, now);
                        _emitters.Flak(interceptAt);
                        break;

                    case SimEventKind.GunRevealed:
                        // A counter-battery radar found a gun that fired: a red ping on it.
                        Ring(Ground(e.Position, 0.3f), 7f, new Color(2.4f, 0.4f, 0.25f, 0.8f));
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
                            Airburst(inAir, ExplosionTier.Huge, now);
                            break;
                        }
                        var blast = Ground(e.Position, 0.3f);
                        // A cluster bomblet: its own small fireball, not a spray of sparks.
                        if (e.Tier == ExplosionTier.Small)
                        {
                            Pop(_pop, blast + Vector3.up * 0.3f, now);
                            _decals.Place(blast, 1.8f);
                            break;
                        }
                        Explode(e.Tier, blast, now);
                        _decals.Place(blast, Mathf.Max(3f, e.Value * 0.9f));
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

                    case SimEventKind.SkillUsed when e.Skill == SkillKind.Emp:
                        Ring(Ground(e.Position, 0.3f), 30f, new Color(0.45f, 0.8f, 2.4f, 1f));
                        break;

                    case SimEventKind.SkillUsed when e.Skill == SkillKind.Shield:
                        // A shield skill: how long it lasts, so it flickers out in its last second.
                        if (views.TryGet(e.Entity, out var shielded)) shielded.ShieldFor(e.Value, now);
                        break;

                    case SimEventKind.Damaged:
                        ShieldDamaged(e, views);
                        break;

                    case SimEventKind.VehicleRetired:
                        // A loaned escort flies home: it simply leaves, no wreck.
                        var leaving = views.Detach(e.Entity);
                        if (leaving != null) Object.Destroy(leaving.Root.gameObject);
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
                        // Aircraft burst into flames in the air, then fall (see Crash).
                        else Explode(view.Flying ? ExplosionTier.Large : ExplosionTier.Medium, view.Position + Vector3.up, now);
                        _wrecks.Add(view, now);
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
            _decals.Place(new Vector3(at.x, 0.15f, at.z), 5f);
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
            foreach (var (e, shooter) in _shots)
            {
                if (e.Kind == SimEventKind.WeaponCharging)
                {
                    _weapons.Charging(e, shooter, now);
                    continue;
                }
                // Shots entirely off screen are not drawn (the sound still plays).
                if (!_cull.Visible(Ground(e.Position, 1f), 0.15f) && !_cull.Visible(Ground(e.Target, 1f), 0.15f)) continue;
                _weapons.Fired(e, shooter, views, now);
                // At night the flash lights the ground at the muzzle.
                if (shooter != null && shooter.Root != null && !shooter.Flying && e.DefId != null &&
                    _catalog.Weapons.TryGetValue(e.DefId, out var fired))
                    _night.Flash(shooter.LastMuzzleNode != null ? shooter.LastMuzzleNode.TransformPoint(shooter.LastMuzzleLocal)
                            : shooter.Position + shooter.Root.forward * shooter.Sim.Radius,
                        fired.Projectile == ProjectileKind.Bullet ? 1.6f : fired.Projectile == ProjectileKind.Shell ? 4.5f : 3.2f);
            }
            _shots.Clear();
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
            _drops.Tick(now);
            JetTrails(views, now);
            KeepBossInSight(views);
            _night.Tick(now, Time.deltaTime, _camera.Focus);
            foreach (var blast in _blasts) blast.Tick(now);
            _muzzle.Tick(now);
            _debris.Tick(now, Time.deltaTime);
            _wrecks.Tick(now, Time.deltaTime);
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
            _wrecks.Clear();
            if (_root != null) Object.Destroy(_root.gameObject);
        }

        /// <summary>
        /// Damage shows on the hull: below 60 % health a vehicle smokes, pale at first and blacker
        /// as it weakens; below 30 % it burns, flames licking out of it under thick black smoke and
        /// a spark now and then; the hull itself darkens with soot. Aircraft trail their smoke.
        /// </summary>
        private void ShowDamage(ViewRegistry views, float now)
        {
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                var sim = view.Sim;
                var health = sim.MaxHp > 0f ? sim.Hp / sim.MaxHp : 1f;
                view.Scorch(health);
                if (health >= 0.6f || now < view.DamageFxAt || !_cull.Visible(view.Position, 0.15f)) continue;
                var burning = health < 0.3f;
                view.DamageFxAt = now + (burning ? 0.12f : Mathf.Lerp(0.18f, 0.4f, (health - 0.3f) / 0.3f));
                var radius = sim.Radius;
                var root = view.Root;
                if (view.Def.Static)
                {
                    DefenceDamage(view, health, burning, now);
                    continue;
                }
                var top = view.Position + Vector3.up * (view.Flying ? 0.4f : 1.4f) - root.forward * radius * 0.3f;
                _emitters.DamageSmoke(top, radius * (burning ? 1.1f : 0.8f), burning ? 0f : Mathf.Clamp01((health - 0.3f) / 0.3f) * 0.8f + 0.2f);
                if (!burning) continue;
                var spot = view.Position + Vector3.up * (view.Flying ? 0.2f : 1f) +
                           root.right * UnityEngine.Random.Range(-0.5f, 0.5f) * radius + root.forward * UnityEngine.Random.Range(-0.6f, 0.4f) * radius;
                _emitters.DamageFire(spot, radius * 0.7f);
                if (UnityEngine.Random.value < 0.08f)
                {
                    _layers.Sparks.Emit(new ParticleSystem.EmitParams
                    {
                        position = spot, velocity = Vector3.up * 5f + UnityEngine.Random.insideUnitSphere * 3f, startSize = 0.15f,
                        startLifetime = 0.8f, applyShapeToPosition = false,
                    }, 6);
                }
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
                var gauge = view.Def.Width * view.Def.Scale * 0.36f;
                var width = Mathf.Clamp(view.Def.Width * view.Def.Scale * 0.2f, 0.28f, 0.75f);
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

        private void Airburst(Vector3 position, ExplosionTier tier, float now)
        {
            if (!_cull.Visible(position, 0.3f)) return;
            var scale = tier >= ExplosionTier.Huge ? 1.8f : tier >= ExplosionTier.Large ? 1.35f : 1f;
            _airburst.Play(position, now, scale, BlastSizes.Bigger);
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
            _emitters.DamageFire(top - Vector3.up * 0.4f + UnityEngine.Random.insideUnitSphere * radius * 0.35f, radius * 0.8f);
            _emitters.DamageFire(view.Position + Vector3.up * view.Top * 0.4f + UnityEngine.Random.insideUnitSphere * radius * 0.5f, radius * 0.6f);
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
            _fires.Ignite(blast, 2f, 40f, now);
            for (var i = 0; i < 5; i++)
                _emitters.DamageSmoke(blast + UnityEngine.Random.insideUnitSphere * radius * 0.4f + Vector3.up * 2f, radius * 0.5f, 0.05f);
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
                        _shellHit.Play(hitAt, now, hitScale, grow, BlastSizes.ShellLife(round));
                        var sparks = heavy ? 36 : 16;
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
                case ProjectileKind.Missile when round.PiercingLook:
                case ProjectileKind.Drone when round.PiercingLook:
                    // HEAT: a sharp star flash and a jet of sparks, a small black puff. Drones by the drone (DECISIONS 12C).
                    Explode(ExplosionTier.Medium, impact + Vector3.up * 0.8f, now, 0.8f * size, flash: false, grow: BlastSizes.Drone(round));
                    _muzzle.SparkBurst(impact + Vector3.up, Vector3.up, 18, 10f, 22f);
                    _emitters.DamageSmoke(impact + Vector3.up * 1.2f, 1.6f, 0.08f);
                    return true;
                case ProjectileKind.Shell when round.DamageType == DamageType.HighExplosive && round.Indirect:
                {
                    // An HE shell or mortar bomb: the blast, then earth and black smoke hanging over it.
                    // (The siege tank's 203 mm is drawn half as big again; DECISIONS 11A. It lingers like a
                    // heavy tank's round, and the ring and smoke are a tenth bigger again; 12C.)
                    var siege = BlastSizes.Ground(round);
                    Explode(e.Tier, impact, now, size, flash: false, grow: siege, life: BlastSizes.GroundLife(round));
                    siege *= BlastSizes.Bigger;
                    Ring(impact, Mathf.Max(4f, e.Value) * 2.2f * siege, new Color(0.75f, 0.66f, 0.5f, 0.55f));
                    var mortar = round.Id.StartsWith("mortar");
                    for (var i = 0; i < (mortar ? 2 : 3); i++)
                        _emitters.DamageSmoke(impact + UnityEngine.Random.insideUnitSphere * 1.2f * siege + Vector3.up * (1f + i) * siege,
                            Mathf.Max(2f, e.Value * 0.55f) * size * Mathf.Pow(siege, 0.65f), mortar ? 0.35f : 0.1f);
                    return true;
                }
                case ProjectileKind.Rocket when round.Id.StartsWith("thermobaric"):
                    // Thermobaric: the pop that spreads the fuel, then the ignition, much bigger.
                    Explode(ExplosionTier.Medium, impact, now, size, flash: false);
                    var cloud = Mathf.Max(6f, e.Value);
                    Later(now + 0.15f, () =>
                    {
                        _napalm.Play(impact + Vector3.up * 0.5f, now + 0.15f, 1.4f * size, BlastSizes.Bigger);
                        Ring(impact, cloud * 2.5f * BlastSizes.Bigger, new Color(2.2f, 1.2f, 0.4f, 0.8f));
                    });
                    return true;
                case ProjectileKind.Bomb:
                {
                    // A bomb: the fireball, a shock ring on the ground and a column of dust and smoke,
                    // drawn bigger by the bomb's weight (DECISIONS 11A).
                    var bomb = BlastSizes.Bomb(round.Id);
                    Explode(e.Tier, impact, now, size, flash: false, grow: bomb);
                    // The ring and the column a tenth bigger again, like the blast (DECISIONS 12C).
                    bomb *= BlastSizes.Bigger;
                    Ring(impact, Mathf.Max(6f, e.Value) * 3f * bomb, new Color(1.2f, 1.1f, 0.9f, 0.7f));
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
        private void Explode(ExplosionTier tier, Vector3 position, float now, float scale = 1f, bool flash = true, float grow = 1f,
            bool exact = false, float life = 1f, float ring = 0f)
        {
            // Off screen, a blast leaves its crater and fires (they persist) but no particles.
            if (!_cull.Visible(position, tier >= ExplosionTier.Huge ? 0.4f : 0.25f)) return;
            if (tier > ExplosionTier.Small) grow = Mathf.Max(1f, grow) * BlastSizes.Bigger;
            // No two blasts alike: a little bigger or smaller, a little off the exact point.
            scale *= exact ? 0.97f + 0.06f * UnityEngine.Random.value : 0.85f + 0.35f * UnityEngine.Random.value;
            position += new Vector3(UnityEngine.Random.Range(-0.4f, 0.4f), 0f, UnityEngine.Random.Range(-0.4f, 0.4f)) * scale;
            _explosions[tier].Play(position, now, scale, grow, life, ring);
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
            "sky_gunship" => (Engine.Prop, new[] { -0.5f, -0.25f, 0.25f, 0.5f }, 0.05f, 0.35f),
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
                var scale = view.Def.Scale;
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
