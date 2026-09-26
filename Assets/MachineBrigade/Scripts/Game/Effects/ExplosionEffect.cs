using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// The particle systems every blast shares, one per kind of layer (flash, fireball, smoke,
    /// sparks...). All explosion tiers and muzzle flashes emit into these few world-space
    /// systems, so a battle's explosions cost about a dozen draw calls, and no blast is ever cut
    /// short to make room for another. Each system holds the look of its layer (material,
    /// colour, growth, gravity, shape); a blast recipe only supplies counts, sizes and speeds.
    /// </summary>
    internal sealed class BlastLayers
    {
        public BlastLayers(MaterialLibrary m, Transform parent)
        {
            var root = new GameObject("Blasts").transform;
            root.SetParent(parent, false);

            Flash = Shared(root, "Flash", m.Fire, 300);
            var flash = Flash.main;
            flash.startColor = new Color(1f, 0.92f, 0.75f);

            Fireball = Shared(root, "Fireball", m.Fire, 6000, -0.15f);
            PB.Colors(Fireball, PB.FireGradient);
            PB.Grow(Fireball, 0.6f, 1.3f);

            Smoke = Shared(root, "Smoke", m.Smoke, 3500);
            PB.Colors(Smoke, PB.Plume(0.2f, 0.5f, 0.55f));
            PB.Grow(Smoke, 0.8f, 2f);
            PB.Rise(Smoke, 1f, 2.4f);

            // Glowing sparks thrown out and falling, drawn as round points: stretched streaks
            // read as scratch marks radiating from every hit.
            Sparks = Shared(root, "Sparks", m.Sparks, 6000, 2.2f);
            var sparks = Sparks.main;
            sparks.startColor = new ParticleSystem.MinMaxGradient(new Color(1f, 0.85f, 0.4f), new Color(1f, 0.55f, 0.15f));
            PB.Grow(Sparks, 1f, 0.3f);

            Dust = Shared(root, "Dust", m.Smoke, 1200);
            PB.Colors(Dust, PB.Fade(new Color(0.5f, 0.45f, 0.36f), new Color(0.46f, 0.42f, 0.34f), new Color(0.42f, 0.4f, 0.33f), 0.55f));
            PB.Grow(Dust, 0.8f, 1.6f);

            // Clods of earth thrown out of the crater.
            Dirt = Shared(root, "Dirt", m.Smoke, 2500, 2.8f);
            var dirt = Dirt.main;
            dirt.startColor = new ParticleSystem.MinMaxGradient(new Color(0.3f, 0.25f, 0.18f), new Color(0.42f, 0.36f, 0.26f));
            Cone(Dirt, 35f, 0.2f);

            // Low dust ring rolling outward along the ground.
            DustRing = Shared(root, "Dust Ring", m.Smoke, 2000);
            var ring = DustRing.shape;
            ring.shapeType = ParticleSystemShapeType.Circle;
            ring.rotation = new Vector3(90f, 0f, 0f);
            PB.Colors(DustRing, PB.Fade(new Color(0.55f, 0.5f, 0.4f), new Color(0.5f, 0.46f, 0.38f), new Color(0.45f, 0.42f, 0.36f), 0.5f));
            PB.Grow(DustRing, 0.6f, 1.8f);

            Debris = Shared(root, "Debris", m.Smoke, 2500, 2.5f);
            var debris = Debris.main;
            debris.startColor = new Color(0.08f, 0.07f, 0.06f, 1f);
            var hemisphere = Debris.shape;
            hemisphere.shapeType = ParticleSystemShapeType.Hemisphere;
            hemisphere.rotation = new Vector3(-90f, 0f, 0f);

            BurningDebris = CreateBurningDebris(root, m);

            // Glowing embers that drift up and linger after the fireball.
            Embers = Shared(root, "Embers", m.Sparks, 3000, -0.08f);
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

            All = new[] { Flash, Fireball, Smoke, Sparks, Dust, Dirt, DustRing, Debris, BurningDebris, Embers, Shockwave };
        }

        public ParticleSystem Flash { get; }
        public ParticleSystem Fireball { get; }
        public ParticleSystem Smoke { get; }
        public ParticleSystem Sparks { get; }
        public ParticleSystem Dust { get; }
        public ParticleSystem Dirt { get; }
        public ParticleSystem DustRing { get; }
        public ParticleSystem Debris { get; }
        public ParticleSystem BurningDebris { get; }
        public ParticleSystem Embers { get; }
        public ParticleSystem Shockwave { get; }
        public IReadOnlyList<ParticleSystem> All { get; }

        public void Clear()
        {
            foreach (var system in All) system.Clear(true);
        }

        /// <summary>
        /// Blazing chunks flung high on arcs, each trailing smoke through a birth sub-emitter,
        /// which sells the scale of big blasts.
        /// </summary>
        private static ParticleSystem CreateBurningDebris(Transform parent, MaterialLibrary m)
        {
            var ps = Shared(parent, "Burning Debris", m.Fire, 800, 2.1f);
            Cone(ps, 38f, 0.6f);
            PB.Colors(ps, PB.Fade(new Color(1f, 0.85f, 0.5f), new Color(1f, 0.5f, 0.15f), new Color(0.6f, 0.18f, 0.05f)));
            PB.Grow(ps, 1f, 0.45f);

            // Soft grey puffs, dense enough to merge into a smooth ribbon rather than a dotted scratch.
            var trail = PB.Create(ps.transform, "Smoke Trail", m.SoftSmoke);
            var main = trail.main;
            main.loop = true;
            main.maxParticles = 5000;
            PB.Basics(trail, new Vector2(0.5f, 0.8f), new Vector2(0f, 0.2f), new Vector2(0.5f, 0.8f));
            PB.Colors(trail, PB.Plume(0.3f, 0.55f, 0.32f));
            PB.Grow(trail, 1f, 2.6f);
            var emission = trail.emission;
            emission.rateOverTime = 60f;
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
    /// One kind of blast (an explosion tier, or the muzzle flash): a recipe of bursts emitted
    /// into the shared <see cref="BlastLayers"/>. Bigger tiers add layers (debris, shockwave,
    /// light, a second fireball) rather than only scaling up. Later bursts (secondary pops, a
    /// rolling fireball) are scheduled and emitted by <see cref="Tick"/>.
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

        private ExplosionEffect()
        {
        }

        /// <summary>Range of the flash of light this blast casts (0: none).</summary>
        public float LightRange { get; private set; }

        public float LightIntensity { get; private set; }

        public void Play(Vector3 position, float now, float scale = 1f)
        {
            for (var i = 0; i < _bursts.Count; i++)
            {
                if (_bursts[i].Time <= 0f) Emit(_bursts[i], position, scale);
                else _pending.Add(new Pending(now + _bursts[i].Time, i, position, scale));
            }
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
            if (shape.enabled) shape.radius = b.Radius * scale;
            ps.Emit(new ParticleSystem.EmitParams { position = position + Vector3.up * (b.Lift * scale), applyShapeToPosition = true },
                b.Count);
        }

        // Layer recipes. Sizes and speeds are in metres; each mirrors a tuned layer of the old
        // per-tier systems.
        private void Flash(BlastLayers l, float size) =>
            _bursts.Add(new Burst(l.Flash, 0f, 1, new Vector2(size, size * 1.2f), Vector2.zero, new Vector2(0.06f, 0.09f), 0.2f));

        private void Fireball(BlastLayers l, int count, Vector2 size, Vector2 speed, float radius, Vector2 lifetime, float time = 0f) =>
            _bursts.Add(new Burst(l.Fireball, time, count, size, speed, lifetime, radius));

        private void Smoke(BlastLayers l, int count, Vector2 size, Vector2 lifetime) =>
            _bursts.Add(new Burst(l.Smoke, 0.05f, count, size, new Vector2(0.5f, 1.8f), lifetime, 0.2f));

        private void Sparks(BlastLayers l, int count, Vector2 speed, float size) =>
            _bursts.Add(new Burst(l.Sparks, 0f, count, new Vector2(size * 1.1f, size * 2f), speed * 0.7f, new Vector2(0.3f, 0.8f), 0.2f));

        private void Dust(BlastLayers l, int count, Vector2 size) =>
            _bursts.Add(new Burst(l.Dust, 0f, count, size, new Vector2(0.3f, 1f), new Vector2(0.5f, 0.9f), 0.2f));

        private void Dirt(BlastLayers l, int count, Vector2 speed) =>
            _bursts.Add(new Burst(l.Dirt, 0f, count, new Vector2(0.2f, 0.5f), speed, new Vector2(0.7f, 1.3f), 0.2f));

        private void DustRing(BlastLayers l, float size) =>
            _bursts.Add(new Burst(l.DustRing, 0f, (int)(size * 2f), new Vector2(1.2f, 2f), new Vector2(3f, 5f), new Vector2(0.8f, 1.4f), 0.5f));

        /// <summary>Smaller blasts popping around a big one for a second: a chain of secondary explosions.</summary>
        private void Secondaries(BlastLayers l, float radius, float size)
        {
            foreach (var (time, count) in new[] { (0.25f, 5), (0.45f, 4), (0.7f, 5), (0.95f, 3), (1.2f, 3) })
                _bursts.Add(new Burst(l.Fireball, time, count, new Vector2(size * 0.7f, size * 1.2f), new Vector2(0.5f, 2f),
                    new Vector2(0.35f, 0.6f), radius));
        }

        private void Debris(BlastLayers l, int count, Vector2 speed) =>
            _bursts.Add(new Burst(l.Debris, 0f, count, new Vector2(0.15f, 0.4f), speed, new Vector2(0.8f, 1.6f), 0.2f));

        private void BurningDebris(BlastLayers l, int count, Vector2 speed) =>
            _bursts.Add(new Burst(l.BurningDebris, 0f, count, new Vector2(0.45f, 0.8f), speed, new Vector2(1.3f, 2.4f), 0.6f));

        private void Embers(BlastLayers l, int count, float scale) =>
            _bursts.Add(new Burst(l.Embers, 0.05f, count, new Vector2(0.08f, 0.18f), new Vector2(1f, 4f) * scale, new Vector2(1.2f, 3f),
                1.2f * scale));

        private void Shockwave(BlastLayers l, float size) =>
            _bursts.Add(new Burst(l.Shockwave, 0f, 1, new Vector2(size, size), Vector2.zero, new Vector2(0.35f, 0.35f), 0f, 0.3f));

        public static ExplosionEffect Create(ExplosionTier tier, BlastLayers l)
        {
            var e = new ExplosionEffect();
            switch (tier)
            {
                case ExplosionTier.Small:
                    e.Sparks(l, 8, new Vector2(4f, 10f), 0.12f);
                    e.Dust(l, 3, new Vector2(0.8f, 1.6f));
                    break;

                case ExplosionTier.Medium:
                    e.Flash(l, 5f);
                    e.Fireball(l, 18, new Vector2(1.6f, 3.4f), new Vector2(1.5f, 5.5f), 0.45f, new Vector2(0.45f, 0.9f));
                    e.Smoke(l, 8, new Vector2(1.8f, 3.4f), new Vector2(1.8f, 3.2f));
                    e.Sparks(l, 20, new Vector2(7f, 16f), 0.16f);
                    e.Dirt(l, 8, new Vector2(4f, 9f));
                    e.DustRing(l, 6f);
                    break;

                case ExplosionTier.Large:
                    e.Flash(l, 10f);
                    e.Fireball(l, 28, new Vector2(3.2f, 6f), new Vector2(2.5f, 9f), 0.9f, new Vector2(0.6f, 1.2f));
                    e.Secondaries(l, 3.5f, 2.4f);
                    e.Smoke(l, 14, new Vector2(2.6f, 4.4f), new Vector2(3f, 5f));
                    e.Sparks(l, 44, new Vector2(9f, 22f), 0.2f);
                    e.Debris(l, 14, new Vector2(6f, 13f));
                    e.BurningDebris(l, 9, new Vector2(7f, 13f));
                    e.Dirt(l, 12, new Vector2(5f, 12f));
                    e.Embers(l, 18, 1f);
                    e.Shockwave(l, 18f);
                    e.LightRange = 18f;
                    e.LightIntensity = 10f;
                    break;

                default: // Huge and above
                    var s = tier == ExplosionTier.Huge ? 1f : 1.6f;
                    e.Flash(l, 16f * s);
                    // A fireball that keeps rolling up for half a second.
                    foreach (var (time, count) in new[] { (0f, 38), (0.15f, 16), (0.32f, 12), (0.5f, 8) })
                        e.Fireball(l, count, new Vector2(4.8f, 9f) * s, new Vector2(3.5f, 11f) * s, 1.4f * s, new Vector2(0.75f, 1.5f), time);
                    e.Secondaries(l, 6f * s, 3.4f * s);
                    e.Smoke(l, 22, new Vector2(4.5f, 7.5f) * s, new Vector2(5f, 8f));
                    e.Sparks(l, 80, new Vector2(12f, 30f), 0.26f);
                    e.Debris(l, 24, new Vector2(8f, 20f));
                    e.BurningDebris(l, 18, new Vector2(9f, 18f) * s);
                    e.Dirt(l, 18, new Vector2(6f, 15f));
                    e.Embers(l, 40, 1.6f);
                    e.Shockwave(l, 34f * s);
                    e.LightRange = 30f * s;
                    e.LightIntensity = 16f;
                    break;
            }
            return e;
        }

        /// <summary>A burst in the air (anti-aircraft hits, an aircraft blowing up): no dirt or ground dust.</summary>
        public static ExplosionEffect CreateAirburst(BlastLayers l)
        {
            var e = new ExplosionEffect();
            e.Flash(l, 6f);
            e.Fireball(l, 16, new Vector2(1.8f, 3.6f), new Vector2(2f, 6f), 0.5f, new Vector2(0.45f, 0.9f));
            e.Smoke(l, 6, new Vector2(1.8f, 3.2f), new Vector2(1.6f, 3f));
            e.Sparks(l, 24, new Vector2(7f, 16f), 0.16f);
            e.Debris(l, 8, new Vector2(4f, 9f));
            e.Embers(l, 10, 0.8f);
            e.LightRange = 14f;
            e.LightIntensity = 7f;
            return e;
        }

        /// <summary>Barrel-mounted flash; played (scaled) for every shot.</summary>
        public static ExplosionEffect CreateMuzzleFlash(BlastLayers l)
        {
            var e = new ExplosionEffect();
            e.Flash(l, 1.7f);
            e.Sparks(l, 4, new Vector2(3f, 7f), 0.07f);
            return e;
        }
    }
}
