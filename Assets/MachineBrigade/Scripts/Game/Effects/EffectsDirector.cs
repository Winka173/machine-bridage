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
    public sealed class EffectsDirector : IDisposable
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
        private readonly ScreenCull _cull;
        private readonly TracerPool _tracers;
        private readonly DecalPool _decals;
        private readonly DebrisPool _debris;
        private readonly WreckManager _wrecks;
        private readonly Emitters _emitters;
        private readonly FireSpots _fires;
        private readonly ProjectilePool _projectiles;
        private readonly WeaponEffects _weapons;
        private readonly StrikeEffects _strikes;
        private readonly GroundMark _marker;
        private float _markerStart = -10f;

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
            _tracers = new TracerPool(meshes.Box, materials.Tracer, _root, 192);
            _emitters = new Emitters(materials, _root);
            _fires = new FireSpots(materials, _root);
            _fires.Visible = p => _cull.Visible(p, 0.3f);
            _decals = new DecalPool(meshes.ScorchQuad, _root, budget.Decals);
            _debris = new DebrisPool(budget.Debris);
            _layers.Chunks = new ChunkThrower(_debris, materials, models, _fires, _root);
            _layers.Chunks.Trails.Visible = p => _cull.Visible(p, 0.3f);
            _wrecks = new WreckManager(_fires, _layers.Chunks, budget.Wrecks);
            _projectiles = new ProjectilePool(_root, 96);
            _weapons = new WeaponEffects(catalog, models, _tracers, _projectiles, _emitters, _muzzle, Shake);
            _strikes = new StrikeEffects(catalog, materials, meshes, models, _emitters, _projectiles, _root);

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
                    case SimEventKind.WeaponFired:
                        // Shots entirely off screen are not drawn (the sound still plays).
                        if (_cull.Visible(Ground(e.Position, 1f), 0.15f) || _cull.Visible(Ground(e.Target, 1f), 0.15f))
                            _weapons.Fired(e, views, now);
                        break;

                    case SimEventKind.ProjectileImpact:
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
                        Explode(e.Tier, impact, now);
                        if (e.Tier >= ExplosionTier.Medium) _decals.Place(impact, e.Tier >= ExplosionTier.Large ? 5f : 2.2f);
                        if (e.DefId == "flamethrower" && UnityEngine.Random.value < 0.35f) _fires.Ignite(impact, 0.45f, 7f, now);
                        // Thermobaric rockets leave the impact area burning.
                        if (e.DefId == "thermobaric_rockets" && UnityEngine.Random.value < 0.6f) _fires.Ignite(impact, 1.1f, 14f, now);
                        // Heavy shells and rockets leave the ground burning now and then.
                        else if (e.Tier == ExplosionTier.Large && UnityEngine.Random.value < 0.5f) _fires.Ignite(impact, 0.6f, 10f, now);
                        else if (e.Tier == ExplosionTier.Medium && UnityEngine.Random.value < 0.15f) _fires.Ignite(impact, 0.35f, 5f, now);
                        break;

                    case SimEventKind.StrikeImpact when IsGentle(e.DefId):
                        Pulse(e.DefId, Ground(e.Position, 0.3f));
                        break;

                    case SimEventKind.StrikeImpact:
                        var hit = Ground(e.Position, 0.3f);
                        var huge = e.Tier >= ExplosionTier.Ultimate;
                        Explode(e.Tier, hit, now);
                        _decals.Place(hit, Mathf.Max(4f, e.Value * (huge ? 1.4f : 1.1f)));
                        if (e.Tier >= ExplosionTier.Large) _fires.Ignite(hit, huge ? 2.2f : e.Tier >= ExplosionTier.Huge ? 1.2f : 0.7f, huge ? 35f : 16f, now);
                        if (e.DefId == "napalm_strike")
                        {
                            if (_cull.Visible(hit, 0.3f)) _napalm.Play(hit, now);
                            // Napalm: the ground itself burns in a wide strip for half a minute.
                            for (var i = 0; i < 3; i++)
                            {
                                var scatter = new Vector3(UnityEngine.Random.Range(-4f, 4f), 0f, UnityEngine.Random.Range(-4f, 4f));
                                _fires.Ignite(hit + scatter, UnityEngine.Random.Range(1.2f, 1.8f), UnityEngine.Random.Range(24f, 34f), now);
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
                        if (views.TryGet(e.Entity, out var guard))
                        {
                            var from = guard.Position + Vector3.up * 2.4f + guard.Root.right * (e.Value * 1.3f);
                            _tracers.Launch(from, interceptAt, 0.06f, 0f, 0.12f, 1.2f, now);
                            _muzzle.Fire(MuzzleFx.Kind.Autocannon, from, interceptAt - from, now, 0.9f, guard.Position.y);
                        }
                        Pop(_pop, interceptAt, now);
                        _emitters.Flak(interceptAt);
                        break;

                    case SimEventKind.Repaired:
                        if (views.TryGet(e.Entity, out var repaired)) _emitters.Repair(repaired.Position + Vector3.up);
                        break;

                    case SimEventKind.Explosion:
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
                        if (blowsUp) Pop(_kill, view.Position + Vector3.up * 0.8f, now);
                        // Aircraft burst into flames in the air, then fall (see Crash).
                        else Explode(view.Flying ? ExplosionTier.Large : ExplosionTier.Medium, view.Position + Vector3.up, now);
                        _wrecks.Add(view, now);
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

        /// <summary>Brief ring at a commanded destination, confirming the order landed.</summary>
        public void ShowMoveMarker(Vector3 point)
        {
            _marker.Transform.position = new Vector3(point.x, 0.08f, point.z);
            _marker.Visible = true;
            _markerStart = Time.unscaledTime;
        }

        public void Tick(ViewRegistry views)
        {
            var now = Time.time;
            _tracers.Tick(now, _emitters);
            _projectiles.Tick(now, _emitters);
            _strikes.Tick(now);
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
            ShowDamage(views, now);

            var markerAge = Time.unscaledTime - _markerStart;
            if (markerAge < 0.6f) _marker.Set(new Color(0.7f, 2f, 1.3f, 1f), Color.white, markerAge / 0.6f);
            else _marker.Visible = false;
        }

        public void Dispose()
        {
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

        private ChunkModel Chunk(string modelId)
        {
            if (!_chunks.TryGetValue(modelId, out var chunk)) _chunks[modelId] = chunk = _models.Chunk(modelId);
            return chunk;
        }

        private void Airburst(Vector3 position, ExplosionTier tier, float now)
        {
            if (!_cull.Visible(position, 0.3f)) return;
            var scale = tier >= ExplosionTier.Huge ? 1.8f : tier >= ExplosionTier.Large ? 1.35f : 1f;
            _airburst.Play(position, now, scale);
            Shake(position, tier >= ExplosionTier.Large ? 0.3f : 0.1f);
        }

        /// <summary>Builds everything that would otherwise be created the first time it is needed mid-battle.</summary>
        public void Prewarm()
        {
            WarmUpPipelines();
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

        /// <summary>Items that do no damage (EMP, shield dome, airdrops, loaned escorts) show a pulse, not a blast.</summary>
        private bool IsGentle(string defId) =>
            defId != null && _catalog.TryGetSupport(defId, out var support) &&
            support.Kind is SupportKind.Emp or SupportKind.ShieldDome or SupportKind.Reinforce or SupportKind.Escort;

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
                    Ring(at, support.Radius * 2f, new Color(0.35f, 1.6f, 2.2f, 1f));
                    break;
                default:
                    // Airdrops land in a gust of dust.
                    Ring(at, 14f, new Color(1.2f, 1.1f, 0.9f, 0.8f));
                    break;
            }
        }

        /// <summary>One expanding ground ring of the given size and colour (the shockwave layer, tinted).</summary>
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

        /// <summary>A small effect with no shake (the killing hit, a cook-off pop).</summary>
        private void Pop(ExplosionEffect effect, Vector3 position, float now)
        {
            if (_cull.Visible(position, 0.2f)) effect.Play(position, now);
        }

        private void Explode(ExplosionTier tier, Vector3 position, float now, float scale = 1f)
        {
            // Off screen, a blast leaves its crater and fires (they persist) but no particles.
            if (!_cull.Visible(position, tier >= ExplosionTier.Huge ? 0.4f : 0.25f)) return;
            // No two blasts alike: a little bigger or smaller, a little off the exact point.
            scale *= 0.85f + 0.35f * UnityEngine.Random.value;
            position += new Vector3(UnityEngine.Random.Range(-0.4f, 0.4f), 0f, UnityEngine.Random.Range(-0.4f, 0.4f)) * scale;
            _explosions[tier].Play(position, now, scale);
            Shake(position, tier switch
            {
                ExplosionTier.Small => 0f,
                ExplosionTier.Medium => 0.12f,
                ExplosionTier.Large => 0.35f,
                ExplosionTier.Huge => 0.7f,
                _ => 1f,
            });
        }

        private void Shake(Vector3 at, float amount)
        {
            if (amount <= 0f) return;
            var distance = Vector3.Distance(at, _camera.Focus);
            _camera.AddTrauma(amount / (1f + distance / 25f));
        }

        private static Vector3 Ground(System.Numerics.Vector2 p, float height) => new Vector3(p.X, height, p.Y);
    }
}
