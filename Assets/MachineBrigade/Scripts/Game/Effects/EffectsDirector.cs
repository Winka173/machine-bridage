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
        private readonly RtsCamera _camera;
        private readonly EffectBudget _budget;
        private readonly Dictionary<ExplosionTier, EffectPool> _explosions = new();
        private readonly EffectPool _muzzle;
        private readonly TracerPool _tracers;
        private readonly DecalPool _decals;
        private readonly DebrisPool _debris;
        private readonly WreckManager _wrecks;
        private readonly SlowMotion _slowMotion = new();
        private readonly List<(Light light, float start, float intensity)> _lights = new();
        private readonly Transform _marker;
        private float _markerStart = -10f;

        public EffectsDirector(MaterialLibrary materials, MeshLibrary meshes, RtsCamera camera, Transform parent, EffectBudget budget)
        {
            _materials = materials;
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
            _tracers = new TracerPool(meshes.Box, materials.Tracer, _root, 64);
            _decals = new DecalPool(meshes.ScorchQuad, materials.Scorch, _root, budget.Decals);
            _debris = new DebrisPool(_root, budget.Debris);
            _wrecks = new WreckManager(materials, budget.Wrecks);

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
                        OnFired(e, views, now);
                        break;

                    case SimEventKind.ProjectileImpact:
                        var impact = Ground(e.Position, 0.15f);
                        Explode(e.Tier, impact, now);
                        if (e.Tier >= ExplosionTier.Medium) _decals.Place(impact, e.Tier >= ExplosionTier.Large ? 5f : 2.2f);
                        break;

                    case SimEventKind.Explosion:
                        var blast = Ground(e.Position, 0.3f);
                        Explode(e.Tier, blast, now);
                        _decals.Place(blast, Mathf.Max(3f, e.Value * 0.9f));
                        _wrecks.TossTurret(e.Entity, now);
                        if (e.Tier >= ExplosionTier.Huge) _slowMotion.Trigger(Time.unscaledTime);
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
                        if (prop.Meshes.Rubble != null) Explode(ExplosionTier.Large, centre + Vector3.up * 2f, now);
                        foreach (var chunk in prop.Meshes.Chunks)
                            _debris.Throw(chunk, prop.Transform.TransformPoint(chunk.LocalCenter), prop.Transform.rotation,
                                centre - Vector3.up, _materials.Voxel, prop.Meshes.Rubble != null ? 9f : 6f, now);
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

        public void Tick()
        {
            var now = Time.time;
            _tracers.Tick(now);
            _debris.Tick(now);
            _wrecks.Tick(now);
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

        private void OnFired(SimEvent e, ViewRegistry views, float now)
        {
            var muzzleHeight = views.TryGet(e.Entity, out var shooter) ? shooter.Meshes.MuzzleHeight : 1.5f;
            var from = Ground(e.Position, muzzleHeight);
            var to = Ground(e.Target, 0.4f);
            switch (e.Tier)
            {
                case ExplosionTier.Small:
                    _tracers.Launch(from, to, e.Value, 0f, 0.05f, 1.1f, now);
                    break;
                case ExplosionTier.Medium:
                    _tracers.Launch(from, to, e.Value, 0f, 0.12f, 1.8f, now);
                    Shake(from, 0.05f);
                    break;
                default:
                    _tracers.Launch(from, to, e.Value, Vector3.Distance(from, to) * 0.3f, 0.25f, 0.7f, now);
                    Shake(from, 0.1f);
                    break;
            }
            _muzzle.Acquire(now).Play(from, now);
        }

        private void Explode(ExplosionTier tier, Vector3 position, float now)
        {
            var effect = _explosions[tier].Acquire(now);
            effect.Play(position, now);
            if (effect.Light != null && _lights.Count < _budget.Lights)
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
