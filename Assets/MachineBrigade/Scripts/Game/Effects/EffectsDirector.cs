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
        public EffectBudget(int debris, int lights, int decals, int wrecks)
        {
            Debris = debris;
            Lights = lights;
            Decals = decals;
            Wrecks = wrecks;
        }

        public int Debris { get; }
        public int Lights { get; }
        public int Decals { get; }

        /// <summary>Hulks left on the field before the oldest sinks away.</summary>
        public int Wrecks { get; }

        public static EffectBudget Eco => new EffectBudget(90, 3, 96, 45);
        public static EffectBudget High => new EffectBudget(220, 8, 160, 70);
    }

    /// <summary>
    /// Turns simulation events into fire, smoke, shells, debris, wrecks and camera shake.
    /// It only ever reads events: nothing here can change the battle (V2 rule 6).
    /// </summary>
    public sealed class EffectsDirector : IDisposable
    {
        private const float LightFadeSeconds = 0.3f;

        private readonly Transform _root;
        private readonly MaterialLibrary _materials;
        private readonly ModelLibrary _models;
        private readonly Dictionary<string, ChunkModel> _chunks = new();
        private readonly RtsCamera _camera;
        private readonly Dictionary<ExplosionTier, ExplosionEffect> _explosions = new();
        private readonly List<ExplosionEffect> _blasts = new();
        private readonly BlastLayers _layers;
        private readonly MuzzleFx _muzzle;
        private readonly ExplosionEffect _airburst;
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
        private readonly Light[] _lightPool;
        private readonly float[] _lightStart, _lightIntensity;
        private readonly GroundMark _marker;
        private float _markerStart = -10f;

        public EffectsDirector(Catalog catalog, MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, RtsCamera camera,
            Transform parent, EffectBudget budget)
        {
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
            _lightPool = new Light[budget.Lights];
            _lightStart = new float[budget.Lights];
            _lightIntensity = new float[budget.Lights];
            for (var i = 0; i < _lightPool.Length; i++) _lightPool[i] = CreateLight(_root);
            _tracers = new TracerPool(meshes.Box, materials.Tracer, _root, 192);
            _emitters = new Emitters(materials, _root);
            _fires = new FireSpots(materials, _root);
            _fires.Visible = p => _cull.Visible(p, 0.3f);
            _decals = new DecalPool(meshes.ScorchQuad, materials.Scorch, _root, budget.Decals);
            _debris = new DebrisPool(budget.Debris);
            _wrecks = new WreckManager(_fires, budget.Wrecks);
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

                    case SimEventKind.StrikeImpact:
                        var hit = Ground(e.Position, 0.3f);
                        var huge = e.Tier >= ExplosionTier.Ultimate;
                        Explode(e.Tier, hit, now);
                        _decals.Place(hit, Mathf.Max(4f, e.Value * (huge ? 1.4f : 1.1f)));
                        if (e.Tier >= ExplosionTier.Large) _fires.Ignite(hit, huge ? 2.2f : e.Tier >= ExplosionTier.Huge ? 1.2f : 0.7f, huge ? 35f : 16f, now);
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
                        Explode(e.Tier, blast, now);
                        _decals.Place(blast, Mathf.Max(3f, e.Value * 0.9f));
                        _wrecks.TossTurret(e.Entity, now);
                        if (e.Tier >= ExplosionTier.Huge)
                        {
                            _fires.Ignite(blast, 1.4f, 30f, now);
                        }
                        else if (e.Tier == ExplosionTier.Large && UnityEngine.Random.value < 0.8f)
                        {
                            _fires.Ignite(blast, 0.9f, 18f, now);
                        }
                        break;

                    case SimEventKind.VehicleDestroyed:
                        var view = views.Detach(e.Entity);
                        if (view == null) break;
                        // Aircraft burst into flames in the air, then fall (see Crash).
                        Explode(view.Flying ? ExplosionTier.Large : ExplosionTier.Medium, view.Position + Vector3.up, now);
                        _wrecks.Add(view, now);
                        break;

                    case SimEventKind.PropDestroyed:
                        if (!map.TryDestroy(e.Entity, out var prop)) break;
                        var centre = prop.Transform.position;
                        if (prop.IsBuilding)
                        {
                            Explode(ExplosionTier.Large, centre + Vector3.up * 2.5f, now);
                            // The rubble keeps burning in a couple of places.
                            var reach = prop.Prop.Radius * 0.4f;
                            _fires.Ignite(centre + new Vector3(UnityEngine.Random.Range(-reach, reach), 0f, UnityEngine.Random.Range(-reach, reach)),
                                1.1f, 35f, now);
                            _fires.Ignite(centre + new Vector3(UnityEngine.Random.Range(-reach, reach), 0f, UnityEngine.Random.Range(-reach, reach)),
                                0.7f, 22f, now);
                        }
                        var spread = Mathf.Max(0.5f, prop.Prop.Radius * 0.6f);
                        var force = prop.IsBuilding ? 10f : 7f;
                        foreach (var id in prop.Debris)
                        {
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
            if (_wrecks.TryCookOff(now, out var cookOff))
                Explode(UnityEngine.Random.value < 0.3f ? ExplosionTier.Medium : ExplosionTier.Small, cookOff, now);
            while (_wrecks.TryCrash(out var crash, out var size)) Crash(crash, size, now);
            KickUpDust(views, now);
            FadeLights(Time.unscaledTime);

            var markerAge = Time.unscaledTime - _markerStart;
            if (markerAge < 0.6f) _marker.Set(new Color(0.7f, 2f, 1.3f, 1f), Color.white, markerAge / 0.6f);
            else _marker.Visible = false;
        }

        public void Dispose()
        {
            _wrecks.Clear();
            if (_root != null) Object.Destroy(_root.gameObject);
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
            foreach (var id in new[] { "missile", "rocket", "bomb", "cruise_missile" })
                if (_models.Has(id)) _models.Merged(id);
            foreach (var id in new[] { "debris_concrete", "debris_plaster", "debris_roof", "debris_wood", "debris_metal", "debris_leaves" })
                if (_models.Has(id)) Chunk(id);
        }

        private void Explode(ExplosionTier tier, Vector3 position, float now, float scale = 1f)
        {
            // Off screen, a blast leaves its crater and fires (they persist) but no particles.
            if (!_cull.Visible(position, tier >= ExplosionTier.Huge ? 0.4f : 0.25f)) return;
            var effect = _explosions[tier];
            effect.Play(position, now, scale);
            if (effect.LightRange > 0f && _lightPool.Length > 0 && !Match.DebugFlags.Has("-mb-no-lights"))
            {
                // A free light, or the one closest to fading out.
                var pick = 0;
                for (var i = 0; i < _lightPool.Length; i++)
                {
                    if (!_lightPool[i].enabled) { pick = i; break; }
                    if (_lightStart[i] < _lightStart[pick]) pick = i;
                }
                var light = _lightPool[pick];
                light.transform.position = position + Vector3.up * 2f * scale;
                light.range = effect.LightRange * scale;
                light.intensity = effect.LightIntensity;
                light.enabled = true;
                _lightStart[pick] = Time.unscaledTime;
                _lightIntensity[pick] = effect.LightIntensity;
            }
            Shake(position, tier switch
            {
                ExplosionTier.Small => 0f,
                ExplosionTier.Medium => 0.12f,
                ExplosionTier.Large => 0.35f,
                ExplosionTier.Huge => 0.7f,
                _ => 1f,
            });
        }

        private void FadeLights(float realNow)
        {
            for (var i = 0; i < _lightPool.Length; i++)
            {
                var light = _lightPool[i];
                if (!light.enabled) continue;
                var t = (realNow - _lightStart[i]) / LightFadeSeconds;
                if (t >= 1f) light.enabled = false;
                else light.intensity = _lightIntensity[i] * (1f - t);
            }
        }

        private static Light CreateLight(Transform parent)
        {
            var go = new GameObject("Blast Light");
            go.transform.SetParent(parent, false);
            var light = go.AddComponent<Light>();
            light.type = LightType.Point;
            light.color = new Color(1f, 0.62f, 0.3f);
            light.shadows = LightShadows.None;
            light.enabled = false;
            return light;
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
