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
        private readonly ExplosionEffect _kill;
        private readonly ExplosionEffect _pop;
        private readonly FireSpots _fires;
        private readonly DebrisPool _debris;
        private readonly DecalPool _decals;
        private readonly WreckManager _wrecks;
        private readonly ModelLibrary _models;
        private readonly MeshLibrary _meshes;
        private readonly MaterialLibrary _materials;
        private readonly Transform _root;
        private readonly SimWorld _world;
        private readonly Catalog _catalog;
        private readonly MuzzleFx _muzzle;
        private readonly Emitters _emitters;
        private readonly ExplosionEffect _shellHit;
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
            _kill = ExplosionEffect.CreateKill(_layers);
            _all.Add(_kill);
            _pop = ExplosionEffect.CreatePop(_layers);
            _all.Add(_pop);
            _shellHit = ExplosionEffect.CreateShellHit(_layers);
            _all.Add(_shellHit);
            _muzzle = new MuzzleFx(materials, root);
            _emitters = new Emitters(materials, root);
            _fires = new FireSpots(materials, root);
            _decals = new DecalPool(meshes.ScorchQuad, root, budget.Decals);
            _debris = new DebrisPool(budget.Debris);
            _layers.Chunks = new ChunkThrower(_debris, materials, models, _fires, root);
            _wrecks = new WreckManager(_fires, _layers.Chunks, budget.Wrecks);
            _catalog = GameContent.LoadCatalog();
            _world = new SimWorld(_catalog, new MapDefinition("shots", 200f,
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
                // Enlarged (DECISIONS 11A, a tenth bigger again and lingering in 12C), High / Medium / Low tier:
                // particles, then particle-seconds of the lingering layers (fire, smoke, dust, embers) and of the rest.
                string At(string name, ExplosionEffect e, float grow, float life = 1f)
                {
                    string Tier(float d)
                    {
                        var (lingering, quick) = e.ParticleSecondsAt(grow, life, d);
                        return $"{e.ParticleCountAt(grow, d)}p {lingering:F0}+{quick:F0}ps";
                    }
                    return $"{name} x{grow:F2} life {life:F2}: {Tier(1f)} / {Tier(0.75f)} / {Tier(0.4f)}";
                }
                var bigger = BlastSizes.Bigger;
                parts.Add(At("ShellHit 11A light", _shellHit, BlastSizes.LightTank));
                parts.Add(At("ShellHit 11A main", _shellHit, BlastSizes.MainTank));
                parts.Add(At("ShellHit 11A heavy", _shellHit, BlastSizes.HeavyTank));
                parts.Add(At("ShellHit light", _shellHit, BlastSizes.LightTank * bigger, BlastSizes.LightLife));
                parts.Add(At("ShellHit main", _shellHit, BlastSizes.MainTank * bigger, BlastSizes.MainLife));
                parts.Add(At("ShellHit heavy", _shellHit, BlastSizes.HeavyTank * bigger, BlastSizes.HeavyLife));
                parts.Add(At("Siege 11A", _tiers[ExplosionTier.Huge], BlastSizes.HeavyTank));
                parts.Add(At("Siege", _tiers[ExplosionTier.Huge], BlastSizes.HeavyTank * bigger, BlastSizes.HeavyLife));
                parts.Add(At("Medium", _tiers[ExplosionTier.Medium], bigger));
                parts.Add(At("Large GBU-12", _tiers[ExplosionTier.Large], 1.3f * bigger));
                parts.Add(At("Huge Mk 84", _tiers[ExplosionTier.Huge], 1.5f * bigger));
                parts.Add(At("Ultimate JDAM", _tiers[ExplosionTier.Ultimate], 1.5f * bigger));
                parts.Add(At("Ultimate cruise", _tiers[ExplosionTier.Ultimate], BlastSizes.Reach(18f) * bigger));
                parts.Add(At("Ultimate MOAB", _tiers[ExplosionTier.Ultimate], BlastSizes.Reach(27f) * bigger));
                parts.Add(At("FPV (Medium)", _tiers[ExplosionTier.Medium], BlastSizes.FpvDrone * bigger));
                parts.Add(At("Lancet (Medium)", _tiers[ExplosionTier.Medium], BlastSizes.LancetDrone * bigger));
                parts.Add(At("Shahed (Huge)", _tiers[ExplosionTier.Huge], BlastSizes.HeavyDrone * bigger));
                return string.Join(", ", parts);
            }
        }

        /// <summary>
        /// A blast as EffectsDirector.Explode draws it: above the Small tier a tenth bigger again
        /// (DECISIONS 12C) unless <paramref name="before"/> (as it was after 11A).
        /// </summary>
        public void Explode(ExplosionTier tier, Vector3 at, float now, float scale = 1f, float grow = 1f, float life = 1f, float ring = 0f,
            bool before = false)
        {
            if (!before && tier > ExplosionTier.Small) grow = Mathf.Max(1f, grow) * BlastSizes.Bigger;
            _tiers[tier].Play(at, now, scale, grow, before ? 1f : life, ring);
        }

        /// <summary>
        /// A tank's round striking a hull (ProjectileImpact of an armour-piercing shell): the
        /// shell-hit blast sized by the tank's class; <paramref name="before"/> draws it as after
        /// the first play test (11A), otherwise a tenth bigger and lingering by the class (12C).
        /// Mirrors EffectsDirector.ImpactOfKind.
        /// </summary>
        public void TankHit(string weapon, Vector3 at, float now, bool before)
        {
            var round = _catalog.Weapons[weapon];
            var heavy = round.Damage >= 150f;
            var hit = at + Vector3.up * 0.8f;
            var grow = BlastSizes.TankShell(round) * (before ? 1f : BlastSizes.Bigger);
            _shellHit.Play(hit, now, heavy ? 1f : 0.75f, grow, before ? 1f : BlastSizes.ShellLife(round));
            var sparks = heavy ? 36 : 16;
            sparks += Mathf.RoundToInt(sparks * (grow - 1f));
            _muzzle.SparkBurst(hit + Vector3.up * 0.2f, Vector3.up + Random.insideUnitSphere * 0.5f, sparks, 8f * grow, (heavy ? 24f : 16f) * grow);
        }

        /// <summary>
        /// A drone diving onto its target (ProjectileImpact of a Drone, or the strike drone's
        /// missile): armour-piercing ones as a HEAT hit, the Shahed as its plain blast, grown by the
        /// drone after 12C. Mirrors EffectsDirector.
        /// </summary>
        public void DroneHit(string weapon, Vector3 at, float now, bool before)
        {
            var round = _catalog.Weapons[weapon];
            var grow = before ? 1f : BlastSizes.Drone(round);
            if (round.DamageType == DamageType.ArmorPiercing)
            {
                Explode(ExplosionTier.Medium, at + Vector3.up * 0.8f, now, 0.8f * round.ImpactScale, grow, before: before);
                _muzzle.SparkBurst(at + Vector3.up, Vector3.up, 18, 10f, 22f);
                _emitters.DamageSmoke(at + Vector3.up * 1.2f, 1.6f, 0.08f);
                return;
            }
            Explode(round.ImpactTier, at, now, round.ImpactScale, grow, before: before);
        }

        /// <summary>
        /// A high-explosive shell landing (the siege tank's 203 mm, a howitzer's 155 mm): the blast, a
        /// dust ring and smoke hanging over it; after 12C a tenth bigger and the siege tank's lingering.
        /// Mirrors EffectsDirector.ImpactOfKind.
        /// </summary>
        public void ShellLanding(string weapon, Vector3 at, float now, bool before)
        {
            var round = _catalog.Weapons[weapon];
            var siege = BlastSizes.Ground(round);
            Explode(round.ImpactTier, at, now, round.ImpactScale, siege, BlastSizes.GroundLife(round), before: before);
            if (!before) siege *= BlastSizes.Bigger;
            Ring(at, Mathf.Max(4f, round.SplashRadius) * 2.2f * siege, new Color(0.75f, 0.66f, 0.5f, 0.55f));
            for (var i = 0; i < 3; i++)
                _emitters.DamageSmoke(at + Random.insideUnitSphere * 1.2f * siege + Vector3.up * (1f + i) * siege,
                    Mathf.Max(2f, round.SplashRadius * 0.55f) * round.ImpactScale * Mathf.Pow(siege, 0.65f), 0.1f);
        }

        /// <summary>An aircraft's bomb landing (ProjectileImpact of a Bomb), as after 11A (before) or after 12C. Mirrors EffectsDirector.</summary>
        public void BombHit(string weapon, Vector3 at, float now, bool before)
        {
            var round = _catalog.Weapons[weapon];
            var bomb = BlastSizes.Bomb(round.Id);
            Explode(round.ImpactTier, at, now, round.ImpactScale, bomb, before: before);
            if (!before) bomb *= BlastSizes.Bigger;
            Ring(at, Mathf.Max(6f, round.SplashRadius) * 3f * bomb, new Color(1.2f, 1.1f, 0.9f, 0.7f));
            for (var i = 0; i < 3; i++)
                _emitters.DamageSmoke(at + (Vector3.up * (1.5f + i * 1.5f) + Random.insideUnitSphere) * bomb,
                    Mathf.Max(2.5f, round.SplashRadius * 0.6f) * Mathf.Pow(bomb, 0.65f), 0.3f);
            if (round.ImpactTier >= ExplosionTier.Medium) _decals.Place(at, (round.ImpactTier >= ExplosionTier.Large ? 5f : 2.2f) * bomb);
        }

        private void Ring(Vector3 at, float size, Color colour) =>
            _layers.Shockwave.Emit(new ParticleSystem.EmitParams
            {
                position = at + Vector3.up * 0.2f, startSize = size, startColor = colour, startLifetime = 0.6f, applyShapeToPosition = false,
            }, 1);

        /// <summary>A thin red circle on the ground: the blast radius the simulation deals damage in, to judge a blast against.</summary>
        public void Marker(Vector3 at, float radius)
        {
            var line = new GameObject("Radius").AddComponent<LineRenderer>();
            line.transform.SetParent(_root, false);
            line.sharedMaterial = _materials.StrikeWarning;
            line.loop = true;
            line.useWorldSpace = true;
            line.widthMultiplier = 0.3f;
            line.positionCount = 72;
            for (var i = 0; i < 72; i++)
            {
                var a = i * Mathf.PI * 2f / 72f;
                line.SetPosition(i, at + new Vector3(Mathf.Cos(a) * radius, 0.12f, Mathf.Sin(a) * radius));
            }
        }

        public void Airburst(Vector3 at, ExplosionTier tier, float now)
        {
            var scale = tier >= ExplosionTier.Huge ? 1.8f : tier >= ExplosionTier.Large ? 1.35f : 1f;
            _airburst.Play(at, now, scale, BlastSizes.Bigger);
        }

        /// <summary>A shell or rocket hitting the ground (ProjectileImpact).</summary>
        public void Impact(ExplosionTier tier, Vector3 at, float now, string weapon = null)
        {
            Explode(tier, at, now);
            if (tier >= ExplosionTier.Medium) _decals.Place(at, tier >= ExplosionTier.Large ? 5f : 2.2f);
            if (weapon == "thermobaric_rockets") _fires.Ignite(at, 1.1f, 14f, now);
            else if (tier == ExplosionTier.Large) _fires.Ignite(at, 0.6f, 10f, now);
        }

        /// <summary>
        /// A fire-support impact (StrikeImpact); <paramref name="blast"/> is its radius. Mirrors
        /// EffectsDirector; <paramref name="before"/> draws it as after the first play test (11A):
        /// after the second (12C) it is a tenth bigger, a cruise missile's ring still on its radius.
        /// </summary>
        public void Strike(string support, ExplosionTier tier, float blast, Vector3 at, float now, bool before = false)
        {
            var huge = tier >= ExplosionTier.Ultimate;
            var nominal = tier switch { ExplosionTier.Large => 4.5f, ExplosionTier.Huge => 6.5f, ExplosionTier.Ultimate => 20f, _ => 3f };
            var scale = Mathf.Clamp(blast / nominal, 0.9f, 1.6f);
            _catalog.TryGetSupport(support, out var def);
            var matched = def != null && def.Kind == SupportKind.CruiseMissile && huge;
            var grow = matched ? BlastSizes.Reach(blast) : BlastSizes.Strike(def);
            if (matched) scale = 1f;
            Explode(tier, at, now, scale, grow, ring: matched ? grow : 0f, before: before);
            _decals.Place(at, Mathf.Max(4f, blast * (huge ? 1.4f : 1.1f)) * (matched ? 1f : grow));
            if (tier >= ExplosionTier.Large) _fires.Ignite(at, huge ? 2.2f : tier >= ExplosionTier.Huge ? 1.2f : 0.7f, huge ? 35f : 16f, now);
            if (support == "napalm_strike")
            {
                _napalm.Play(at, now, 1f, before ? 1f : BlastSizes.Bigger);
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

        /// <summary>
        /// VehicleDestroyed: the killing hit (its death explosion follows) or, for a vehicle with
        /// none, the kill blast; and the hulk left behind. Mirrors EffectsDirector.
        /// </summary>
        public void Destroyed(VehicleView view, float now, bool blowsUp = true)
        {
            if (blowsUp) _kill.Play(view.Position + Vector3.up * 0.8f, now, 1f, BlastSizes.Bigger);
            else Explode(view.Flying ? ExplosionTier.Large : ExplosionTier.Medium, view.Position + Vector3.up, now);
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
            _muzzle.Tick(now);
            _emitters.Tick(now, dt);
            _debris.Tick(now, dt);
            _wrecks.Tick(now, dt);
            _fires.Tick(now, dt);
            while (_wrecks.TryCookOff(now, out var cookOff, out var pop))
            {
                if (pop) _pop.Play(cookOff, now, 1f, BlastSizes.Bigger);
                else Explode(ExplosionTier.Small, cookOff, now);
            }
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
