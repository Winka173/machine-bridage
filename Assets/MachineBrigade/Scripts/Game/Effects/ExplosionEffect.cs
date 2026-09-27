using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// The particle systems every blast shares, one per kind of layer (flash, fireball, smoke,
    /// sparks...). All explosion tiers and airbursts emit into these few world-space systems, so a
    /// battle's explosions cost about a dozen draw calls, and no blast is ever cut short to make
    /// room for another. Each system holds the look of its layer (material, colour, growth,
    /// gravity, shape); a blast recipe only supplies counts, sizes and speeds.
    /// Fireballs, smoke and dust are flipbooks rendered from fire simulations
    /// (<see cref="FxMaterials"/>): a handful of big animated billboards instead of a cloud of
    /// small puffs. Solid chunks (earth, rubble, burning wreckage) are meshes thrown by
    /// <see cref="Chunks"/>.
    /// </summary>
    internal sealed class BlastLayers
    {
        /// <summary>
        /// Where the ground sits in a fireball frame, as a pivot offset in particle sizes: the
        /// quad is lifted so the blast rises from the point it is emitted at.
        /// </summary>
        public const float FireballPivot = 0.32f;

        public BlastLayers(MaterialLibrary m, Transform parent)
        {
            var fx = FxMaterials.Shared;
            var root = new GameObject("Blasts").transform;
            root.SetParent(parent, false);
            var ground = PB.GroundPlane(root);

            Flash = Shared(root, "Flash", m.Fire, 300);
            var flash = Flash.main;
            flash.startColor = new Color(1f, 0.9f, 0.7f);

            // Fireballs: each particle plays a whole simulated explosion, from the burst of flame
            // to the black smoke it rolls up into.
            Fireball = Shared(root, "Fireball", fx.Blast, 700, -0.02f);
            PB.Flipbook(Fireball, loop: false, tilt: 10f, pivotY: FireballPivot);
            PB.Colors(Fireball, PB.Hold(new Color(0.34f, 0.31f, 0.28f), new Color(0.3f, 0.29f, 0.28f), 0.02f, 0.72f));
            PB.Grow(Fireball, 0.82f, 1.12f);
            Drag(Fireball, 0.12f);

            HotFireball = Shared(root, "Hot Fireball", fx.HotBlast, 300, -0.02f);
            PB.Flipbook(HotFireball, loop: false, tilt: 8f, pivotY: FireballPivot);
            PB.Colors(HotFireball, PB.Hold(new Color(0.3f, 0.28f, 0.26f), new Color(0.27f, 0.26f, 0.25f), 0.02f, 0.72f));
            PB.Grow(HotFireball, 0.85f, 1.15f);
            Drag(HotFireball, 0.12f);

            // Black smoke billowing up out of the blast and drifting off with the wind.
            Smoke = Shared(root, "Smoke", fx.Smoke, 1500);
            PB.Flipbook(Smoke, loop: false, tilt: 25f);
            PB.Colors(Smoke, PB.Hold(new Color(0.13f, 0.12f, 0.115f), new Color(0.42f, 0.41f, 0.4f), 0.1f, 0.55f, 0.95f));
            PB.Grow(Smoke, 0.7f, 1.9f);
            PB.Rise(Smoke, 1.1f, 2.6f);
            Drag(Smoke, 0.1f);

            // Glowing sparks thrown out, bouncing and skittering along the ground, drawn as round
            // points: stretched streaks read as scratch marks radiating from every hit.
            Sparks = Shared(root, "Sparks", m.Sparks, 7000, 2.2f);
            var sparks = Sparks.main;
            sparks.startColor = new ParticleSystem.MinMaxGradient(new Color(1f, 0.85f, 0.4f), new Color(1f, 0.55f, 0.15f));
            PB.Grow(Sparks, 1f, 0.3f);
            PB.BounceOffGround(Sparks, ground, 0.4f, 0.35f, 0.15f);

            Dust = Shared(root, "Dust", fx.Dust, 900);
            PB.Flipbook(Dust, loop: false, tilt: 30f, from: 0.05f, to: 0.95f);
            PB.Colors(Dust, PB.Hold(new Color(0.62f, 0.55f, 0.43f), new Color(0.6f, 0.55f, 0.46f), 0.06f, 0.5f, 0.85f));
            PB.Grow(Dust, 0.7f, 1.7f);
            Drag(Dust, 0.15f);

            // Clods of earth thrown out of the crater; they land and bounce.
            Dirt = Shared(root, "Dirt", m.Smoke, 3000, 2.8f);
            var dirt = Dirt.main;
            dirt.startColor = new ParticleSystem.MinMaxGradient(new Color(0.3f, 0.25f, 0.18f), new Color(0.42f, 0.36f, 0.26f));
            Cone(Dirt, 35f, 0.2f);
            PB.BounceOffGround(Dirt, ground, 0.2f, 0.6f, 0.1f);

            // The dust skirt: a low ring of dust rolling outward along the ground and slowing.
            DustRing = Shared(root, "Dust Ring", fx.Dust, 1500);
            var ring = DustRing.shape;
            ring.shapeType = ParticleSystemShapeType.Circle;
            ring.rotation = new Vector3(90f, 0f, 0f);
            ring.radiusThickness = 0.2f;
            PB.Flipbook(DustRing, loop: false, tilt: 40f, from: 0.1f, to: 0.95f);
            PB.Colors(DustRing, PB.Hold(new Color(0.66f, 0.6f, 0.48f), new Color(0.62f, 0.58f, 0.5f), 0.05f, 0.45f, 0.8f));
            PB.Grow(DustRing, 0.55f, 1.9f);
            Drag(DustRing, 0.09f);

            Debris = Shared(root, "Debris", m.Smoke, 3000, 2.5f);
            var debris = Debris.main;
            debris.startColor = new Color(0.08f, 0.07f, 0.06f, 1f);
            var hemisphere = Debris.shape;
            hemisphere.shapeType = ParticleSystemShapeType.Hemisphere;
            hemisphere.rotation = new Vector3(-90f, 0f, 0f);
            PB.BounceOffGround(Debris, ground, 0.25f, 0.55f, 0.1f);

            BurningDebris = CreateBurningDebris(root, m, fx);

            // Glowing embers that drift up and linger after the fireball.
            Embers = Shared(root, "Embers", m.Sparks, 4000, -0.08f);
            var embers = Embers.main;
            embers.startColor = new ParticleSystem.MinMaxGradient(new Color(1f, 0.7f, 0.25f), new Color(1f, 0.45f, 0.1f));
            PB.Colors(Embers, PB.Fade(new Color(1f, 0.8f, 0.4f), new Color(1f, 0.5f, 0.15f), new Color(0.6f, 0.15f, 0.05f)));
            var noise = Embers.noise;
            noise.enabled = true;
            noise.strength = 0.8f;
            noise.frequency = 0.6f;

            Shockwave = Shared(root, "Shockwave", m.Shockwave, 200, 0f, ParticleSystemRenderMode.HorizontalBillboard);
            var shock = Shockwave.main;
            shock.startRotation = 0f;
            shock.startColor = new Color(1f, 0.85f, 0.6f, 0.9f);
            var none = Shockwave.shape;
            none.enabled = false;
            PB.Grow(Shockwave, 0.1f, 1f);
            PB.Colors(Shockwave, PB.Fade(Color.white, Color.white, Color.white, 0.9f));

            // The crater floor glowing hot for a few seconds, cooling and shrinking.
            CraterGlow = Shared(root, "Crater Glow", m.Fire, 300, 0f, ParticleSystemRenderMode.HorizontalBillboard);
            var glow = CraterGlow.shape;
            glow.enabled = false;
            PB.Colors(CraterGlow, PB.Fade(new Color(0.8f, 0.24f, 0.05f), new Color(0.55f, 0.12f, 0.03f), new Color(0.25f, 0.04f, 0.01f), 0.45f));
            PB.Grow(CraterGlow, 1f, 0.75f);

            All = new[]
            {
                Flash, Fireball, HotFireball, Smoke, Sparks, Dust, Dirt, DustRing, Debris, BurningDebris, Embers, Shockwave, CraterGlow,
            };
        }

        public ParticleSystem Flash { get; }
        public ParticleSystem Fireball { get; }
        public ParticleSystem HotFireball { get; }
        public ParticleSystem Smoke { get; }
        public ParticleSystem Sparks { get; }
        public ParticleSystem Dust { get; }
        public ParticleSystem Dirt { get; }
        public ParticleSystem DustRing { get; }
        public ParticleSystem Debris { get; }
        public ParticleSystem BurningDebris { get; }
        public ParticleSystem Embers { get; }
        public ParticleSystem Shockwave { get; }
        public ParticleSystem CraterGlow { get; }
        public IReadOnlyList<ParticleSystem> All { get; }

        /// <summary>Throws solid chunks (earth, rubble, wreckage); null leaves blasts particle-only.</summary>
        public ChunkThrower Chunks { get; set; }

        public void Clear()
        {
            foreach (var system in All) system.Clear(true);
        }

        /// <summary>
        /// Blazing chunks flung high on arcs, each trailing smoke through a birth sub-emitter,
        /// which sells the scale of big blasts.
        /// </summary>
        private static ParticleSystem CreateBurningDebris(Transform parent, MaterialLibrary m, FxMaterials fx)
        {
            var ps = Shared(parent, "Burning Debris", m.Fire, 900, 2.1f);
            Cone(ps, 38f, 0.6f);
            PB.Colors(ps, PB.Fade(new Color(1f, 0.85f, 0.5f), new Color(1f, 0.5f, 0.15f), new Color(0.6f, 0.18f, 0.05f)));
            PB.Grow(ps, 1f, 0.45f);

            // Billowing smoke puffs from the smoke flipbook, big enough to overlap into a ribbon:
            // a quarter of the puffs the old soft dots needed.
            var trail = PB.Create(ps.transform, "Smoke Trail", fx.Smoke);
            var main = trail.main;
            main.loop = true;
            main.maxParticles = 3000;
            PB.Basics(trail, new Vector2(0.9f, 1.4f), new Vector2(0f, 0.2f), new Vector2(1f, 1.35f));
            PB.Flipbook(trail, loop: false, tilt: 30f, from: 0.1f);
            PB.Colors(trail, PB.Hold(new Color(0.16f, 0.15f, 0.14f), new Color(0.45f, 0.44f, 0.43f), 0.08f, 0.4f, 0.8f));
            PB.Grow(trail, 0.6f, 1.9f);
            var emission = trail.emission;
            emission.rateOverTime = 12f;
            var sub = ps.subEmitters;
            sub.enabled = true;
            sub.AddSubEmitter(trail, ParticleSystemSubEmitterType.Birth, ParticleSystemSubEmitterProperties.InheritNothing);
            ps.Play(true);
            return ps;
        }

        private static void Cone(ParticleSystem ps, float angle, float radius)
        {
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Cone;
            shape.angle = angle;
            shape.radius = radius;
            shape.rotation = new Vector3(-90f, 0f, 0f);
        }

        /// <summary>Air drag: puffs thrown out fast are braked and then drift.</summary>
        private static void Drag(ParticleSystem ps, float dampen)
        {
            var limit = ps.limitVelocityOverLifetime;
            limit.enabled = true;
            limit.limit = 0.5f;
            limit.dampen = dampen;
        }

        private static ParticleSystem Shared(Transform parent, string name, Material material, int max, float gravity = 0f,
            ParticleSystemRenderMode mode = ParticleSystemRenderMode.Billboard)
        {
            var ps = PB.Create(parent, name, material, mode);
            var main = ps.main;
            main.loop = true;
            main.maxParticles = max;
            main.gravityModifier = gravity;
            var emission = ps.emission;
            emission.enabled = false;
            ps.Play(true);
            return ps;
        }
    }

    /// <summary>
    /// One kind of blast (an explosion tier, an airburst, a napalm canister): a recipe of bursts
    /// emitted into the shared <see cref="BlastLayers"/>, plus solid chunks. Bigger tiers add
    /// layers (debris, shockwave, a glowing crater, light, a rolling fireball) rather than only
    /// scaling up. Later bursts (secondary pops, the fireball rolling on) are scheduled and
    /// emitted by <see cref="Tick"/>.
    /// </summary>
    internal sealed class ExplosionEffect
    {
        private readonly struct Burst
        {
            public Burst(ParticleSystem system, float time, int count, Vector2 size, Vector2 speed, Vector2 lifetime, float radius,
                float lift = 0f)
            {
                System = system;
                Time = time;
                Count = count;
                Size = size;
                Speed = speed;
                Lifetime = lifetime;
                Radius = radius;
                Lift = lift;
            }

            public ParticleSystem System { get; }
            public float Time { get; }
            public int Count { get; }
            public Vector2 Size { get; }
            public Vector2 Speed { get; }
            public Vector2 Lifetime { get; }
            public float Radius { get; }
            public float Lift { get; }
        }

        private readonly struct Pending
        {
            public Pending(float at, int burst, Vector3 position, float scale)
            {
                At = at;
                BurstIndex = burst;
                Position = position;
                Scale = scale;
            }

            public float At { get; }
            public int BurstIndex { get; }
            public Vector3 Position { get; }
            public float Scale { get; }
        }

        private readonly List<Burst> _bursts = new();
        private readonly List<Pending> _pending = new();
        private readonly BlastLayers _layers;
        private ChunkThrower.Recipe _chunks;

        private ExplosionEffect(BlastLayers layers)
        {
            _layers = layers;
        }

        /// <summary>Range of the flash of light this blast casts (0: none).</summary>
        public float LightRange { get; private set; }

        public float LightIntensity { get; private set; }

        /// <summary>Particles this blast emits in all (its budget; smoke trails of burning chunks come on top).</summary>
        public int ParticleCount
        {
            get
            {
                var total = 0;
                foreach (var b in _bursts) total += b.Count;
                return total;
            }
        }

        /// <summary>Solid chunks this blast throws.</summary>
        public int ChunkCount => _chunks.Earth + _chunks.Wreckage + _chunks.Burning;

        public void Play(Vector3 position, float now, float scale = 1f)
        {
            for (var i = 0; i < _bursts.Count; i++)
            {
                if (_bursts[i].Time <= 0f) Emit(_bursts[i], position, scale);
                else _pending.Add(new Pending(now + _bursts[i].Time, i, position, scale));
            }
            _layers.Chunks?.Throw(_chunks, position, scale, now);
        }

        /// <summary>Emits the later bursts that are due.</summary>
        public void Tick(float now)
        {
            for (var i = _pending.Count - 1; i >= 0; i--)
            {
                var p = _pending[i];
                if (now < p.At) continue;
                Emit(_bursts[p.BurstIndex], p.Position, p.Scale);
                _pending[i] = _pending[_pending.Count - 1];
                _pending.RemoveAt(_pending.Count - 1);
            }
        }

        public void Clear() => _pending.Clear();

        private static void Emit(in Burst b, Vector3 position, float scale)
        {
            var ps = b.System;
            var main = ps.main;
            main.startSize = new ParticleSystem.MinMaxCurve(b.Size.x * scale, b.Size.y * scale);
            main.startSpeed = new ParticleSystem.MinMaxCurve(b.Speed.x * scale, b.Speed.y * scale);
            main.startLifetime = new ParticleSystem.MinMaxCurve(b.Lifetime.x, b.Lifetime.y);
            var shape = ps.shape;
            if (shape.enabled) shape.radius = Mathf.Max(0.01f, b.Radius * scale);
            ps.Emit(new ParticleSystem.EmitParams { position = position + Vector3.up * (b.Lift * scale), applyShapeToPosition = true },
                b.Count);
        }

        // Layer recipes. Sizes and speeds are in metres.
        private void Flash(float size) =>
            _bursts.Add(new Burst(_layers.Flash, 0f, 1, new Vector2(size, size * 1.2f), Vector2.zero, new Vector2(0.06f, 0.09f), 0.2f));

        /// <summary>
        /// Fireball flipbooks. Each is a whole explosion over its life; a few overlapping ones of
        /// different sizes and ages make one irregular blast. <paramref name="lift"/> lowers
        /// airbursts back onto their centre (the quads are lifted to stand on the ground).
        /// </summary>
        private void Fireball(int count, Vector2 size, Vector2 lifetime, float radius, float time = 0f, bool hot = false,
            float lift = 0f, Vector2? speed = null) =>
            _bursts.Add(new Burst(hot ? _layers.HotFireball : _layers.Fireball, time, count, size, speed ?? new Vector2(0.5f, 2.5f),
                lifetime, radius, lift));

        private void Smoke(int count, Vector2 size, Vector2 lifetime, float time = 0.12f) =>
            _bursts.Add(new Burst(_layers.Smoke, time, count, size, new Vector2(0.8f, 2.8f), lifetime, size.x * 0.25f, size.x * 0.15f));

        private void Sparks(int count, Vector2 speed, float size) =>
            _bursts.Add(new Burst(_layers.Sparks, 0f, count, new Vector2(size * 1.1f, size * 2f), speed * 0.7f, new Vector2(0.4f, 1.2f), 0.2f));

        private void Dust(int count, Vector2 size) =>
            _bursts.Add(new Burst(_layers.Dust, 0f, count, size, new Vector2(0.6f, 2.2f), new Vector2(1f, 1.8f), 0.3f));

        private void Dirt(int count, Vector2 speed) =>
            _bursts.Add(new Burst(_layers.Dirt, 0f, count, new Vector2(0.2f, 0.5f), speed, new Vector2(1.2f, 2.2f), 0.2f));

        /// <summary>The dust skirt rolling out along the ground from a big blast.</summary>
        private void DustRing(float size, int count) =>
            _bursts.Add(new Burst(_layers.DustRing, 0.02f, count, new Vector2(size * 0.16f, size * 0.26f),
                new Vector2(size * 0.45f, size * 0.85f), new Vector2(1.6f, 2.8f), size * 0.08f, 0.3f));

        /// <summary>Fireballs popping around a big blast for a second: a chain of secondary explosions.</summary>
        private void Secondaries(float radius, float size)
        {
            foreach (var (time, count) in new[] { (0.22f, 2), (0.42f, 1), (0.62f, 2), (0.85f, 1), (1.1f, 1), (1.35f, 1) })
                _bursts.Add(new Burst(_layers.Fireball, time, count, new Vector2(size * 0.8f, size * 1.25f), new Vector2(0.5f, 2f),
                    new Vector2(0.8f, 1.1f), radius));
        }

        private void Debris(int count, Vector2 speed) =>
            _bursts.Add(new Burst(_layers.Debris, 0f, count, new Vector2(0.15f, 0.4f), speed, new Vector2(1.2f, 2.2f), 0.2f));

        private void BurningDebris(int count, Vector2 speed) =>
            _bursts.Add(new Burst(_layers.BurningDebris, 0f, count, new Vector2(0.45f, 0.8f), speed, new Vector2(1.3f, 2.4f), 0.6f));

        private void Embers(int count, float scale) =>
            _bursts.Add(new Burst(_layers.Embers, 0.05f, count, new Vector2(0.08f, 0.18f), new Vector2(1f, 4f) * scale,
                new Vector2(1.5f, 3.5f), 1.2f * scale));

        private void Shockwave(float size) =>
            _bursts.Add(new Burst(_layers.Shockwave, 0f, 1, new Vector2(size, size), Vector2.zero, new Vector2(0.35f, 0.35f), 0f, 0.3f));

        private void CraterGlow(float size, float seconds) =>
            _bursts.Add(new Burst(_layers.CraterGlow, 0.05f, 1, new Vector2(size, size * 1.1f), Vector2.zero,
                new Vector2(seconds, seconds * 1.3f), 0f, 0.12f));

        public static ExplosionEffect Create(ExplosionTier tier, BlastLayers l)
        {
            var e = new ExplosionEffect(l);
            switch (tier)
            {
                case ExplosionTier.Small:
                    // Bullets and flak: frequent, so cheap. A spray of sparks and a puff of dust.
                    e.Sparks(12, new Vector2(4f, 10f), 0.12f);
                    e.Dust(2, new Vector2(1.2f, 2f));
                    break;

                case ExplosionTier.Medium:
                    e.Flash(5f);
                    e.Fireball(2, new Vector2(4.2f, 5.6f), new Vector2(0.95f, 1.25f), 0.35f);
                    e.Smoke(3, new Vector2(3.2f, 4.6f), new Vector2(2.6f, 3.6f));
                    e.Sparks(28, new Vector2(7f, 16f), 0.16f);
                    e.Dust(2, new Vector2(2.2f, 3.2f));
                    e.Dirt(12, new Vector2(4f, 9f));
                    e.Debris(6, new Vector2(4f, 9f));
                    e.Embers(8, 0.8f);
                    e.DustRing(8f, 7);
                    e._chunks = new ChunkThrower.Recipe(earth: 6, wreckage: 0, burning: 0, new Vector2(5f, 10f), 0.7f);
                    break;

                case ExplosionTier.Large:
                    e.Flash(10f);
                    e.Fireball(3, new Vector2(7.5f, 9.5f), new Vector2(1.25f, 1.6f), 0.8f);
                    e.Fireball(2, new Vector2(4.5f, 6f), new Vector2(0.9f, 1.2f), 1.6f, 0.12f);
                    e.Secondaries(3.5f, 3.4f);
                    e.Smoke(6, new Vector2(5f, 7f), new Vector2(4f, 6f));
                    e.Sparks(64, new Vector2(9f, 22f), 0.2f);
                    e.Debris(18, new Vector2(6f, 13f));
                    e.BurningDebris(8, new Vector2(7f, 13f));
                    e.Dirt(18, new Vector2(5f, 12f));
                    e.Embers(26, 1f);
                    e.Shockwave(18f);
                    e.DustRing(16f, 14);
                    e.CraterGlow(5.5f, 4.5f);
                    e._chunks = new ChunkThrower.Recipe(earth: 12, wreckage: 4, burning: 3, new Vector2(7f, 14f), 1f);
                    e.LightRange = 18f;
                    e.LightIntensity = 10f;
                    break;

                default: // Huge and above
                    var ultimate = tier != ExplosionTier.Huge;
                    var s = ultimate ? 1.6f : 1f;
                    e.Flash(16f * s);
                    // A fireball that keeps rolling up for half a second, around a white-hot core.
                    e.Fireball(2, new Vector2(11f, 14f) * s, new Vector2(1.5f, 1.9f), 1.2f * s, 0f, hot: true);
                    e.Fireball(3, new Vector2(8f, 11f) * s, new Vector2(1.3f, 1.7f), 2.4f * s);
                    e.Fireball(2, new Vector2(7f, 9.5f) * s, new Vector2(1.2f, 1.5f), 3f * s, 0.14f);
                    e.Fireball(2, new Vector2(6f, 8f) * s, new Vector2(1.1f, 1.4f), 3.4f * s, 0.3f);
                    e.Fireball(1, new Vector2(8f, 10f) * s, new Vector2(1.3f, 1.6f), 1.5f * s, 0.48f, hot: ultimate);
                    e.Secondaries(6f * s, 4.2f * s);
                    e.Smoke(ultimate ? 12 : 9, new Vector2(7f, 10f) * s, new Vector2(5f, 8f));
                    e.Sparks(ultimate ? 150 : 110, new Vector2(12f, 30f), 0.26f);
                    e.Debris(ultimate ? 40 : 30, new Vector2(8f, 20f));
                    e.BurningDebris(ultimate ? 16 : 12, new Vector2(9f, 18f) * s);
                    e.Dirt(ultimate ? 34 : 24, new Vector2(6f, 15f));
                    e.Embers(ultimate ? 70 : 50, 1.6f);
                    e.Shockwave(34f * s);
                    if (ultimate) e.Shockwave(22f * s);
                    e.DustRing(26f * s, ultimate ? 30 : 22);
                    e.CraterGlow(9f * s, 6f);
                    e._chunks = ultimate
                        ? new ChunkThrower.Recipe(earth: 30, wreckage: 12, burning: 9, new Vector2(10f, 22f), 1.4f)
                        : new ChunkThrower.Recipe(earth: 20, wreckage: 8, burning: 6, new Vector2(9f, 18f), 1.2f);
                    e.LightRange = 30f * s;
                    e.LightIntensity = 16f;
                    break;
            }
            return e;
        }

        /// <summary>A burst in the air (anti-aircraft hits, an aircraft blowing up): no dirt or ground dust.</summary>
        public static ExplosionEffect CreateAirburst(BlastLayers l)
        {
            var e = new ExplosionEffect(l);
            e.Flash(6f);
            // The fireball quads stand on their emission point; lower them onto the burst's centre.
            e.Fireball(2, new Vector2(4.5f, 6f), new Vector2(0.9f, 1.2f), 0.5f, lift: -2.6f);
            e.Fireball(1, new Vector2(3.2f, 4.2f), new Vector2(0.8f, 1f), 1f, 0.1f, lift: -1.8f);
            e.Smoke(3, new Vector2(2.6f, 3.6f), new Vector2(2f, 3f));
            e.Sparks(30, new Vector2(7f, 16f), 0.16f);
            e.Debris(10, new Vector2(4f, 9f));
            e.Embers(12, 0.8f);
            e._chunks = new ChunkThrower.Recipe(earth: 0, wreckage: 4, burning: 2, new Vector2(4f, 9f), 0.8f);
            e.LightRange = 14f;
            e.LightIntensity = 7f;
            return e;
        }

        /// <summary>
        /// A napalm canister bursting: a wide, low, rolling wall of fire under heavy black smoke,
        /// and burning gobs of fuel flung out (the ground keeps burning; see <see cref="FireSpots"/>).
        /// </summary>
        public static ExplosionEffect CreateNapalm(BlastLayers l)
        {
            var e = new ExplosionEffect(l);
            e.Fireball(4, new Vector2(7f, 10f), new Vector2(1.4f, 1.9f), 4.5f, speed: new Vector2(2f, 5f));
            e.Fireball(3, new Vector2(6f, 8.5f), new Vector2(1.3f, 1.7f), 6f, 0.15f, speed: new Vector2(2f, 4f));
            e.Smoke(6, new Vector2(7f, 10f), new Vector2(6f, 9f), 0.3f);
            e.BurningDebris(10, new Vector2(6f, 12f));
            e.Embers(40, 1.4f);
            e.CraterGlow(12f, 8f);
            e._chunks = new ChunkThrower.Recipe(earth: 0, wreckage: 0, burning: 8, new Vector2(5f, 11f), 0.6f, fuel: true);
            return e;
        }
    }
}
