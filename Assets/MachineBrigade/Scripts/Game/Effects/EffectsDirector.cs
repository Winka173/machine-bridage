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
        public EffectBudget(int explosionsPerTier, int debris, int lights, int decals, int wrecks)
        {
            ExplosionsPerTier = explosionsPerTier;
            Debris = debris;
            Lights = lights;
            Decals = decals;
            Wrecks = wrecks;
        }

        public int ExplosionsPerTier { get; }
        public int Debris { get; }
        public int Lights { get; }
        public int Decals { get; }
        public int Wrecks { get; }

        public static EffectBudget Eco => new EffectBudget(10, 60, 2, 64, 12);
        public static EffectBudget High => new EffectBudget(25, 200, 8, 128, 20);
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
        private readonly EffectBudget _budget;
        private readonly Dictionary<ExplosionTier, EffectPool> _explosions = new();
        private readonly EffectPool _muzzle;
        private readonly TracerPool _tracers;
        private readonly DecalPool _decals;
        private readonly DebrisPool _debris;
        private readonly WreckManager _wrecks;
        private readonly Emitters _emitters;
        private readonly FireSpots _fires;
        private readonly ProjectilePool _projectiles;
        private readonly WeaponEffects _weapons;
        private readonly StrikeEffects _strikes;
        private readonly SlowMotion _slowMotion = new();
        private readonly List<(Light light, float start, float intensity)> _lights = new();
        private readonly Transform _marker;
        private float _markerStart = -10f;

        public EffectsDirector(Catalog catalog, MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, RtsCamera camera,
            Transform parent, EffectBudget budget)
        {
            _materials = materials;
            _models = models;
            _camera = camera;
            _budget = budget;
            _root = new GameObject("Effects").transform;
            _root.SetParent(parent, false);

            foreach (ExplosionTier tier in Enum.GetValues(typeof(ExplosionTier)))
            {
                var t = tier;
                var capacity = tier >= ExplosionTier.Huge ? Math.Max(2, budget.ExplosionsPerTier / 3) : budget.ExplosionsPerTier;
                _explosions[tier] = new EffectPool(() => ExplosionEffect.Create(t, materials, _root), capacity);
            }
            _muzzle = new EffectPool(() => ExplosionEffect.CreateMuzzleFlash(materials, _root), 24);
            _tracers = new TracerPool(meshes.Box, materials.Tracer, _root, 192);
            _emitters = new Emitters(materials, _root);
            _fires = new FireSpots(materials, _root, budget.Lights + 6);
            _decals = new DecalPool(meshes.ScorchQuad, materials.Scorch, _root, budget.Decals);
            _debris = new DebrisPool(_root, budget.Debris);
            _wrecks = new WreckManager(materials, budget.Wrecks);
            _projectiles = new ProjectilePool(_root, 96);
            _weapons = new WeaponEffects(catalog, models, _tracers, _projectiles, _emitters, _muzzle, Shake);
            _strikes = new StrikeEffects(catalog, materials, meshes, models, _emitters, _projectiles, _root);

            _marker = VehicleView.CreateMesh("Move Marker", _root, meshes.Ring, materials.MoveMarker, false);
            _marker.gameObject.SetActive(false);
        }

        public bool ReducedMotion
        {
            get => !_slowMotion.Enabled;
            set => _slowMotion.Enabled = !value;
        }

        public void Consume(IReadOnlyList<SimEvent> events, ViewRegistry views, MapView map)
        {
            var now = Time.time;
            foreach (var e in events)
            {
                switch (e.Kind)
                {
                    case SimEventKind.WeaponFired:
                        _weapons.Fired(e, views, now);
                        break;

                    case SimEventKind.ProjectileImpact:
                        if (e.Airborne)
                        {
                            // Flak and missiles bursting around an aircraft.
                            // The hit aircraft gives the height; misses burst at flying height.
                            var height = views.TryGet(e.Entity, out var struck) && struck.Flying ? struck.Altitude + 0.5f : 9f;
                            Explode(e.Tier, new Vector3(e.Position.X, height, e.Position.Y), now);
                            _emitters.Flak(new Vector3(e.Position.X, height, e.Position.Y));
                            break;
                        }
                        var impact = Ground(e.Position, 0.15f);
                        Explode(e.Tier, impact, now);
                        if (e.Tier >= ExplosionTier.Medium) _decals.Place(impact, e.Tier >= ExplosionTier.Large ? 5f : 2.2f);
                        if (e.DefId == "flamethrower" && UnityEngine.Random.value < 0.08f) _fires.Ignite(impact, 0.35f, 5f, now);
                        break;

                    case SimEventKind.StrikeImpact:
                        var hit = Ground(e.Position, 0.3f);
                        var huge = e.Tier >= ExplosionTier.Ultimate;
                        Explode(huge ? ExplosionTier.Huge : e.Tier, hit, now, huge ? 1.8f : 1f);
                        _decals.Place(hit, Mathf.Max(4f, e.Value * (huge ? 1.4f : 1.1f)));
                        if (e.Tier >= ExplosionTier.Huge) _fires.Ignite(hit, huge ? 2f : 0.9f, huge ? 30f : 14f, now);
                        if (huge) _slowMotion.Trigger(Time.unscaledTime);
                        break;

                    case SimEventKind.StrikeWarning:
                    case SimEventKind.AircraftPass:
                    case SimEventKind.SmokeDeployed:
                        _strikes.Consume(e, now);
                        break;

                    case SimEventKind.Repaired:
                        if (views.TryGet(e.Entity, out var repaired)) _emitters.Repair(repaired.Position + Vector3.up * (repaired.Altitude + 1f));
                        break;

                    case SimEventKind.Explosion:
                        var blast = Ground(e.Position, 0.3f);
                        Explode(e.Tier, blast, now);
                        _decals.Place(blast, Mathf.Max(3f, e.Value * 0.9f));
                        _wrecks.TossTurret(e.Entity, now);
                        if (e.Tier >= ExplosionTier.Huge)
                        {
                            _slowMotion.Trigger(Time.unscaledTime);
                            _fires.Ignite(blast, 1.4f, 30f, now);
                        }
                        else if (e.Tier == ExplosionTier.Large && UnityEngine.Random.value < 0.35f)
                        {
                            _fires.Ignite(blast, 0.7f, 12f, now);
                        }
                        break;

                    case SimEventKind.VehicleDestroyed:
                        var view = views.Detach(e.Entity);
                        if (view == null) break;
                        Explode(ExplosionTier.Medium, view.Position + Vector3.up, now);
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

        /// <summary>Brief ring at a commanded destination, confirming the order landed.</summary>
        public void ShowMoveMarker(Vector3 point)
        {
            _marker.position = new Vector3(point.x, 0.08f, point.z);
            _marker.gameObject.SetActive(true);
            _markerStart = Time.unscaledTime;
        }

        public void Tick(ViewRegistry views)
        {
            var now = Time.time;
            _tracers.Tick(now, _emitters);
            _projectiles.Tick(now, _emitters);
            _strikes.Tick(now);
            _debris.Tick(now);
            _wrecks.Tick(now);
            _fires.Tick(now);
            if (_wrecks.TryCookOff(now, out var cookOff))
                Explode(UnityEngine.Random.value < 0.3f ? ExplosionTier.Medium : ExplosionTier.Small, cookOff, now);
            KickUpDust(views, now);
            _slowMotion.Tick(Time.unscaledTime);
            FadeLights(Time.unscaledTime);

            var markerAge = Time.unscaledTime - _markerStart;
            if (markerAge < 0.45f) _marker.localScale = Vector3.one * Mathf.Lerp(2.2f, 0.6f, markerAge / 0.45f);
            else if (_marker.gameObject.activeSelf) _marker.gameObject.SetActive(false);
        }

        public void Dispose()
        {
            _slowMotion.Reset();
            _wrecks.Clear();
            if (_root != null) Object.Destroy(_root.gameObject);
        }

        /// <summary>Dust clouds behind the tracks of moving vehicles.</summary>
        private void KickUpDust(ViewRegistry views, float now)
        {
            foreach (var view in views.All)
            {
                var speed = view.Speed;
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

        private void Explode(ExplosionTier tier, Vector3 position, float now, float scale = 1f)
        {
            var effect = _explosions[tier].Acquire(now);
            effect.Play(position, now, scale);
            if (effect.Light != null && _lights.Count < _budget.Lights && !Match.DebugFlags.Has("-mb-no-lights"))
            {
                effect.Light.enabled = true;
                effect.Light.intensity = effect.LightIntensity;
                _lights.Add((effect.Light, Time.unscaledTime, effect.LightIntensity));
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
            for (var i = _lights.Count - 1; i >= 0; i--)
            {
                var (light, start, intensity) = _lights[i];
                var t = (realNow - start) / LightFadeSeconds;
                if (t >= 1f || light == null)
                {
                    if (light != null) light.enabled = false;
                    _lights.RemoveAt(i);
                }
                else
                {
                    light.intensity = intensity * (1f - t);
                }
            }
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
