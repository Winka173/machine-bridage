using System;
using System.Collections.Generic;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using UnityEngine;
using Object = UnityEngine.Object;
using Random = UnityEngine.Random;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// The battle's effect systems without the rest of the match, driven by an explicit clock so
    /// <see cref="EffectShots"/> can freeze them at chosen moments. Each method mirrors what
    /// <see cref="EffectsDirector"/> does for one kind of simulation event.
    /// </summary>
    internal sealed class BlastRig : IDisposable
    {
        private readonly Dictionary<ExplosionTier, ExplosionEffect> _tiers = new();
        private readonly List<ExplosionEffect> _all = new();
        private readonly BlastLayers _layers;
        private readonly ExplosionEffect _airburst;
        private readonly ExplosionEffect _napalm;
        private readonly FireSpots _fires;
        private readonly DebrisPool _debris;
        private readonly DecalPool _decals;
        private readonly WreckManager _wrecks;
        private readonly ModelLibrary _models;
        private readonly MeshLibrary _meshes;
        private readonly MaterialLibrary _materials;
        private readonly Transform _root;
        private readonly SimWorld _world;
        private readonly ParticleSystem[] _systems;

        public BlastRig(MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, Transform root)
        {
            _materials = materials;
            _meshes = meshes;
            _models = models;
            _root = root;
            var budget = EffectBudget.High;
            _layers = new BlastLayers(materials, root);
            foreach (ExplosionTier tier in Enum.GetValues(typeof(ExplosionTier)))
            {
                _tiers[tier] = ExplosionEffect.Create(tier, _layers);
                _all.Add(_tiers[tier]);
            }
            _airburst = ExplosionEffect.CreateAirburst(_layers);
            _all.Add(_airburst);
            _napalm = ExplosionEffect.CreateNapalm(_layers);
            _all.Add(_napalm);
            _fires = new FireSpots(materials, root);
            _decals = new DecalPool(meshes.ScorchQuad, root, budget.Decals);
            _debris = new DebrisPool(budget.Debris);
            _layers.Chunks = new ChunkThrower(_debris, materials, models, _fires, root);
            _wrecks = new WreckManager(_fires, _layers.Chunks, budget.Wrecks);
            _world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("shots", 200f,
                new[] { new TeamStart(0, new System.Numerics.Vector2(-80f, -80f)), new TeamStart(1, new System.Numerics.Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));
            _systems = root.GetComponentsInChildren<ParticleSystem>(true);
        }

        /// <summary>The most particles alive at once over the run (all shared systems together).</summary>
        public int PeakParticles { get; private set; }

        /// <summary>The most solid chunks alive at once.</summary>
        public int PeakChunks { get; private set; }

        /// <summary>The most big quads (a metre or more across: fire, smoke, dust) alive at once; they cost the fill rate.</summary>
        public int PeakBig { get; private set; }

        /// <summary>
        /// The most quad area alive at once, in square metres: an overdraw proxy (the camera is
        /// orthographic, so area on screen is proportional to area in the world).
        /// </summary>
        public float PeakFill { get; private set; }

        private readonly ParticleSystem.Particle[] _buffer = new ParticleSystem.Particle[20000];

        /// <summary>Particles per system at the moment of peak quad area, busiest first.</summary>
        public string PeakBreakdown { get; private set; } = string.Empty;

        /// <summary>Particles and chunks each kind of blast emits, for the log.</summary>
        public string Budget
        {
            get
            {
                var parts = new List<string>();
                foreach (var pair in _tiers) parts.Add($"{pair.Key} {pair.Value.ParticleCount}p/{pair.Value.ChunkCount}c");
                parts.Add($"Airburst {_airburst.ParticleCount}p/{_airburst.ChunkCount}c");
                parts.Add($"Napalm {_napalm.ParticleCount}p/{_napalm.ChunkCount}c");
                return string.Join(", ", parts);
            }
        }

        public void Explode(ExplosionTier tier, Vector3 at, float now) => _tiers[tier].Play(at, now);

        public void Airburst(Vector3 at, ExplosionTier tier, float now)
        {
            var scale = tier >= ExplosionTier.Huge ? 1.8f : tier >= ExplosionTier.Large ? 1.35f : 1f;
            _airburst.Play(at, now, scale);
        }

        /// <summary>A shell or rocket hitting the ground (ProjectileImpact).</summary>
        public void Impact(ExplosionTier tier, Vector3 at, float now, string weapon = null)
        {
            Explode(tier, at, now);
            if (tier >= ExplosionTier.Medium) _decals.Place(at, tier >= ExplosionTier.Large ? 5f : 2.2f);
            if (weapon == "thermobaric_rockets") _fires.Ignite(at, 1.1f, 14f, now);
            else if (tier == ExplosionTier.Large) _fires.Ignite(at, 0.6f, 10f, now);
        }

        /// <summary>A fire-support impact (StrikeImpact); <paramref name="blast"/> is its radius.</summary>
        public void Strike(string support, ExplosionTier tier, float blast, Vector3 at, float now)
        {
            var huge = tier >= ExplosionTier.Ultimate;
            Explode(tier, at, now);
            _decals.Place(at, Mathf.Max(4f, blast * (huge ? 1.4f : 1.1f)));
            if (tier >= ExplosionTier.Large) _fires.Ignite(at, huge ? 2.2f : tier >= ExplosionTier.Huge ? 1.2f : 0.7f, huge ? 35f : 16f, now);
            if (support == "napalm_strike")
            {
                _napalm.Play(at, now);
                for (var i = 0; i < 3; i++)
                {
                    var scatter = new Vector3(Random.Range(-4f, 4f), 0f, Random.Range(-4f, 4f));
                    _fires.Ignite(at + scatter, Random.Range(1.2f, 1.8f), Random.Range(24f, 34f), now);
                }
            }
            if (!huge) return;
            for (var i = 0; i < 5; i++)
            {
                var a = i * Mathf.PI * 2f / 5f + Random.value;
                var r = blast * Random.Range(0.35f, 0.7f);
                _fires.Ignite(at + new Vector3(Mathf.Cos(a) * r, 0f, Mathf.Sin(a) * r), Random.Range(0.6f, 1.1f), Random.Range(14f, 26f), now);
            }
        }

        /// <summary>A live vehicle of the given kind standing at <paramref name="at"/>, facing the camera's right.</summary>
        public VehicleView Spawn(string vehicle, Vector3 at)
        {
            var sim = _world.SpawnVehicle(vehicle, 1, System.Numerics.Vector2.Zero, 0f);
            var view = new VehicleView(sim, _models, _meshes, _materials, _root, 0);
            view.Root.SetPositionAndRotation(at, Quaternion.Euler(0f, 45f, 0f));
            return view;
        }

        /// <summary>VehicleDestroyed: the kill blast and the hulk left behind.</summary>
        public void Destroyed(VehicleView view, float now)
        {
            Explode(view.Flying ? ExplosionTier.Large : ExplosionTier.Medium, view.Position + Vector3.up, now);
            _wrecks.Add(view, now);
        }

        /// <summary>Explosion: the vehicle's death explosion a moment after the kill.</summary>
        public void DeathExplosion(VehicleView view, ExplosionTier tier, float radius, float now)
        {
            var blast = new Vector3(view.Position.x, 0.3f, view.Position.z);
            Explode(tier, blast, now);
            _decals.Place(blast, Mathf.Max(3f, radius * 0.9f));
            _wrecks.Blow(view.Id, now);
            if (tier >= ExplosionTier.Huge) _fires.Ignite(blast, 1.4f, 30f, now);
            else if (tier == ExplosionTier.Large) _fires.Ignite(blast, 0.9f, 18f, now);
        }

        public void Tick(float now, float dt)
        {
            foreach (var blast in _all) blast.Tick(now);
            _debris.Tick(now, dt);
            _wrecks.Tick(now, dt);
            _fires.Tick(now, dt);
            if (_wrecks.TryCookOff(now, out var cookOff, out var cookOffTier)) Explode(cookOffTier, cookOff, now);
            var alive = 0;
            var big = 0;
            var fill = 0f;
            foreach (var ps in _systems)
            {
                alive += ps.particleCount;
                var n = ps.GetParticles(_buffer);
                for (var i = 0; i < n; i++)
                {
                    var size = _buffer[i].GetCurrentSize(ps);
                    if (size < 1f) continue;
                    big++;
                    fill += size * size;
                }
            }
            PeakParticles = Mathf.Max(PeakParticles, alive);
            PeakBig = Mathf.Max(PeakBig, big);
            if (fill > PeakFill)
            {
                var parts = new List<(int count, string name)>();
                foreach (var ps in _systems)
                    if (ps.particleCount > 0) parts.Add((ps.particleCount, ps.name));
                parts.Sort((a, b) => b.count.CompareTo(a.count));
                PeakBreakdown = string.Join(", ", parts.ConvertAll(p => $"{p.name} {p.count}"));
            }
            PeakFill = Mathf.Max(PeakFill, fill);
            PeakChunks = Mathf.Max(PeakChunks, _debris.Active);
        }

        /// <summary>Draws what is not a scene object (flying debris); call before each render.</summary>
        public void Draw(float now) => _debris.Draw(now);

        /// <summary>Solid chunks flying or lying about now.</summary>
        public int Chunks => _debris.Active;

        public void Dispose() => Object.DestroyImmediate(_root.gameObject);
    }

    /// <summary>One row of the blast sheet: a place, a zoom and a timed script of events.</summary>
    internal sealed class BlastScene
    {
        private readonly List<(float at, Action<float> act)> _script = new();
        private int _next;

        public BlastScene(string name, Vector3 focus, float view, float offset = 0f)
        {
            Name = name;
            Focus = focus;
            View = view;
            Offset = offset;
        }

        public string Name { get; }
        public Vector3 Focus { get; }

        /// <summary>Orthographic half-height of the view, in metres.</summary>
        public float View { get; }

        /// <summary>Seconds before (negative) or after the common start at which the script begins.</summary>
        public float Offset { get; }

        public BlastScene At(float seconds, Action<float> act)
        {
            _script.Add((seconds, act));
            _script.Sort((a, b) => a.at.CompareTo(b.at));
            return this;
        }

        public void Run(float time)
        {
            while (_next < _script.Count && time >= BlastScenes.Start + Offset + _script[_next].at) _script[_next++].act(time);
        }
    }

    internal static class BlastScenes
    {
        /// <summary>When on the shared clock the scenes begin (room for a wreck to burn beforehand).</summary>
        public const float Start = 16f;

        private const float Spacing = 130f;

        public static BlastScene[] All(BlastRig rig)
        {
            Vector3 Row(int i) => new(-390f + i * Spacing, 0f, 0f);
            var scenes = new List<BlastScene>();

            var p = Row(0);
            scenes.Add(new BlastScene("small, medium, airburst", p, 9f)
                .At(0f, t => rig.Impact(ExplosionTier.Small, p + new Vector3(-5f, 0.15f, -5f), t))
                .At(0f, t => rig.Impact(ExplosionTier.Medium, p + new Vector3(0f, 0.15f, 0f), t))
                .At(0f, t => rig.Airburst(p + new Vector3(5f, 7f, 5f), ExplosionTier.Medium, t)));

            var large = Row(1);
            scenes.Add(new BlastScene("large", large, 11f).At(0f, t => rig.Impact(ExplosionTier.Large, large + Vector3.up * 0.15f, t)));

            var huge = Row(2);
            scenes.Add(new BlastScene("huge (airstrike bomb)", huge, 14f)
                .At(0f, t => rig.Strike("airstrike", ExplosionTier.Huge, 6f, huge + Vector3.up * 0.3f, t)));

            var ultimate = Row(3);
            scenes.Add(new BlastScene("ultimate (cruise missile)", ultimate, 22f)
                .At(0f, t => rig.Strike("cruise_missile", ExplosionTier.Ultimate, 15f, ultimate + Vector3.up * 0.3f, t)));

            // A main battle tank killed: the kill blast, then its Huge death explosion 0.45 s later.
            var tankAt = Row(4);
            var tank = rig.Spawn("main_battle_tank", tankAt);
            scenes.Add(new BlastScene("tank death", tankAt, 11f)
                .At(0f, t => rig.Destroyed(tank, t))
                .At(0.45f, t => rig.DeathExplosion(tank, ExplosionTier.Huge, 7f, t)));

            // A heavy tank killed 14 s before the common start: its row shows the hulk burning.
            var wreckAt = Row(5);
            var wreck = rig.Spawn("heavy_tank", wreckAt);
            scenes.Add(new BlastScene("burning wreck", wreckAt, 9f, -14f)
                .At(0f, t => rig.Destroyed(wreck, t))
                .At(0.5f, t => rig.DeathExplosion(wreck, ExplosionTier.Huge, 8f, t)));

            // Napalm: ten bombs along a line over 1.4 s.
            var napalm = Row(6);
            var run = new BlastScene("napalm", napalm, 19f);
            for (var i = 0; i < 10; i++)
            {
                var at = napalm + new Vector3(-16f + i * 3.6f, 0.3f, -16f + i * 3.6f);
                run.At(i * 1.4f / 9f, t => rig.Strike("napalm_strike", ExplosionTier.Huge, 7f, at, t));
            }
            scenes.Add(run);

            // Close up on a heavy tank blowing apart, to judge the debris.
            var closeAt = Row(7);
            var close = rig.Spawn("heavy_tank", closeAt);
            scenes.Add(new BlastScene("tank death, close", closeAt, 6.5f)
                .At(0f, t => rig.Destroyed(close, t))
                .At(0.3f, t => rig.DeathExplosion(close, ExplosionTier.Huge, 8f, t)));
            return scenes.ToArray();
        }
    }
}
