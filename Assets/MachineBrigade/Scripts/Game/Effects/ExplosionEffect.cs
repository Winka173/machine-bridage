using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>A pooled, replayable blast made of several particle layers and an optional light.</summary>
    internal sealed class ExplosionEffect
    {
        private readonly ParticleSystem[] _systems;

        public ExplosionEffect(GameObject root, ParticleSystem[] systems, Light light, float lightIntensity, float duration)
        {
            Root = root;
            _systems = systems;
            Light = light;
            LightIntensity = lightIntensity;
            Duration = duration;
            PlayedAt = -1000f;
        }

        public GameObject Root { get; }
        public Light Light { get; }
        public float LightIntensity { get; }
        public float Duration { get; }
        public float PlayedAt { get; private set; }

        public bool IsBusy(float now) => now - PlayedAt < Duration;

        public void Play(Vector3 position, float now, float scale = 1f)
        {
            Root.transform.position = position;
            Root.transform.localScale = Vector3.one * scale;
            foreach (var s in _systems)
            {
                s.Clear(true);
                s.Play(true);
            }
            PlayedAt = now;
        }

        /// <summary>
        /// Builds the layered blast for a tier. Bigger tiers add layers (debris, shockwave,
        /// light, a second fireball) rather than only scaling up.
        /// </summary>
        public static ExplosionEffect Create(ExplosionTier tier, MaterialLibrary m, Transform parent)
        {
            var root = new GameObject($"Explosion {tier}");
            root.transform.SetParent(parent, false);
            var t = root.transform;
            var systems = new List<ParticleSystem>();
            Light light = null;
            float lightIntensity = 0f, duration;

            switch (tier)
            {
                case ExplosionTier.Small:
                    systems.Add(Sparks(t, m, 8, new Vector2(4f, 10f), 0.12f));
                    systems.Add(Dust(t, m, 3, new Vector2(0.8f, 1.6f)));
                    duration = 1.2f;
                    break;

                case ExplosionTier.Medium:
                    systems.Add(Flash(t, m, 5f));
                    systems.Add(Fireball(t, m, 12, new Vector2(1.4f, 3f), new Vector2(1.5f, 5f), 0.4f, new Vector2(0.4f, 0.85f)));
                    systems.Add(Smoke(t, m, 8, new Vector2(1.8f, 3.4f), new Vector2(1.8f, 3.2f), 0.24f));
                    systems.Add(Sparks(t, m, 14, new Vector2(7f, 16f), 0.16f));
                    systems.Add(Dirt(t, m, 8, new Vector2(4f, 9f)));
                    systems.Add(DustRing(t, m, 6f));
                    duration = 3.5f;
                    break;

                case ExplosionTier.Large:
                    systems.Add(Flash(t, m, 10f));
                    systems.Add(Fireball(t, m, 20, new Vector2(3f, 5.5f), new Vector2(2.5f, 8f), 0.8f, new Vector2(0.55f, 1.1f)));
                    systems.Add(Smoke(t, m, 14, new Vector2(2.6f, 4.4f), new Vector2(3f, 5f), 0.2f));
                    systems.Add(Sparks(t, m, 30, new Vector2(9f, 22f), 0.2f));
                    systems.Add(Debris(t, m, 14, new Vector2(6f, 13f)));
                    systems.Add(BurningDebris(t, m, 7, new Vector2(7f, 13f)));
                    systems.Add(Dirt(t, m, 12, new Vector2(5f, 12f)));
                    systems.Add(Embers(t, m, 18, 1f));
                    systems.Add(Shockwave(t, m, 18f));
                    light = AddLight(t, 18f);
                    lightIntensity = 10f;
                    duration = 6f;
                    break;

                default: // Huge and above
                    var s = tier == ExplosionTier.Huge ? 1f : 1.6f;
                    systems.Add(Flash(t, m, 16f * s));
                    var fireball = Fireball(t, m, 32, new Vector2(4.5f, 8.5f) * s, new Vector2(3.5f, 11f) * s, 1.3f * s,
                        new Vector2(0.7f, 1.4f));
                    PB.Burst(fireball, (0f, 32), (0.15f, 14), (0.32f, 10), (0.5f, 6));
                    systems.Add(fireball);
                    systems.Add(Smoke(t, m, 22, new Vector2(4.5f, 7.5f) * s, new Vector2(5f, 8f), 0.16f));
                    systems.Add(Sparks(t, m, 48, new Vector2(12f, 30f), 0.26f));
                    systems.Add(Debris(t, m, 24, new Vector2(8f, 20f)));
                    systems.Add(BurningDebris(t, m, 14, new Vector2(9f, 18f) * s));
                    systems.Add(Dirt(t, m, 18, new Vector2(6f, 15f)));
                    systems.Add(Embers(t, m, 40, 1.6f));
                    systems.Add(Shockwave(t, m, 34f * s));
                    light = AddLight(t, 30f * s);
                    lightIntensity = 16f;
                    duration = 10f;
                    break;
            }

            return new ExplosionEffect(root, systems.ToArray(), light, lightIntensity, duration);
        }

        /// <summary>Barrel-mounted flash; kept separate because every shot plays one.</summary>
        public static ExplosionEffect CreateMuzzleFlash(MaterialLibrary m, Transform parent)
        {
            var root = new GameObject("Muzzle Flash");
            root.transform.SetParent(parent, false);
            var flash = Flash(root.transform, m, 1.4f);
            var sparks = Sparks(root.transform, m, 3, new Vector2(3f, 7f), 0.06f);
            return new ExplosionEffect(root, new[] { flash, sparks }, null, 0f, 0.3f);
        }

        private static ParticleSystem Flash(Transform parent, MaterialLibrary m, float size)
        {
            var ps = PB.Create(parent, "Flash", m.Fire);
            PB.Basics(ps, new Vector2(0.06f, 0.09f), Vector2.zero, new Vector2(size, size * 1.2f));
            var main = ps.main;
            main.startColor = new Color(1f, 0.92f, 0.75f);
            PB.Burst(ps, (0f, 1));
            return ps;
        }

        private static ParticleSystem Fireball(Transform parent, MaterialLibrary m, int count, Vector2 size, Vector2 speed, float radius,
            Vector2 lifetime)
        {
            var ps = PB.Create(parent, "Fireball", m.Fire);
            PB.Basics(ps, lifetime, speed, size, -0.15f);
            var shape = ps.shape;
            shape.radius = radius;
            PB.Colors(ps, PB.FireGradient);
            PB.Grow(ps, 0.6f, 1.3f);
            PB.Burst(ps, (0f, count));
            return ps;
        }

        private static ParticleSystem Smoke(Transform parent, MaterialLibrary m, int count, Vector2 size, Vector2 lifetime, float shade)
        {
            var ps = PB.Create(parent, "Smoke", m.Smoke);
            PB.Basics(ps, lifetime, new Vector2(0.5f, 1.8f), size);
            PB.Colors(ps, PB.Plume(shade, Mathf.Min(0.6f, shade + 0.3f), 0.55f));
            PB.Grow(ps, 0.8f, 2f);
            PB.Rise(ps, 1f, 2.4f);
            PB.Burst(ps, (0.05f, count));
            return ps;
        }

        private static ParticleSystem Dust(Transform parent, MaterialLibrary m, int count, Vector2 size)
        {
            var ps = PB.Create(parent, "Dust", m.Smoke);
            PB.Basics(ps, new Vector2(0.5f, 0.9f), new Vector2(0.3f, 1f), size);
            PB.Colors(ps, PB.Fade(new Color(0.5f, 0.45f, 0.36f), new Color(0.46f, 0.42f, 0.34f), new Color(0.42f, 0.4f, 0.33f), 0.55f));
            PB.Grow(ps, 0.8f, 1.6f);
            PB.Burst(ps, (0f, count));
            return ps;
        }

        private static ParticleSystem Sparks(Transform parent, MaterialLibrary m, int count, Vector2 speed, float size)
        {
            var ps = PB.Create(parent, "Sparks", m.Sparks, ParticleSystemRenderMode.Stretch);
            PB.Basics(ps, new Vector2(0.15f, 0.45f), speed, new Vector2(size * 0.6f, size), 1.8f);
            var main = ps.main;
            main.startColor = new ParticleSystem.MinMaxGradient(new Color(1f, 0.85f, 0.4f), new Color(1f, 0.55f, 0.15f));
            PB.Burst(ps, (0f, count));
            return ps;
        }

        private static ParticleSystem Debris(Transform parent, MaterialLibrary m, int count, Vector2 speed)
        {
            var ps = PB.Create(parent, "Debris", m.Smoke);
            PB.Basics(ps, new Vector2(0.8f, 1.6f), speed, new Vector2(0.15f, 0.4f), 2.5f);
            var main = ps.main;
            main.startColor = new Color(0.08f, 0.07f, 0.06f, 1f);
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Hemisphere;
            shape.rotation = new Vector3(-90f, 0f, 0f);
            PB.Burst(ps, (0f, count));
            return ps;
        }

        /// <summary>
        /// Blazing chunks flung high on arcs, each trailing black smoke through a birth
        /// sub-emitter, which sells the scale of big blasts.
        /// </summary>
        private static ParticleSystem BurningDebris(Transform parent, MaterialLibrary m, int count, Vector2 speed)
        {
            var ps = PB.Create(parent, "Burning Debris", m.Fire);
            PB.Basics(ps, new Vector2(1.3f, 2.4f), speed, new Vector2(0.45f, 0.8f), 2.1f);
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Cone;
            shape.angle = 38f;
            shape.radius = 0.6f;
            shape.rotation = new Vector3(-90f, 0f, 0f);
            PB.Colors(ps, PB.Fade(new Color(1f, 0.85f, 0.5f), new Color(1f, 0.5f, 0.15f), new Color(0.6f, 0.18f, 0.05f)));
            PB.Grow(ps, 1f, 0.45f);
            PB.Burst(ps, (0f, count));

            var trail = PB.Create(ps.transform, "Smoke Trail", m.Smoke);
            var main = trail.main;
            main.loop = true;
            main.maxParticles = 400;
            PB.Basics(trail, new Vector2(0.7f, 1.3f), new Vector2(0f, 0.3f), new Vector2(0.45f, 0.8f));
            PB.Colors(trail, PB.Plume(0.08f, 0.35f, 0.7f));
            PB.Grow(trail, 0.8f, 2.4f);
            var emission = trail.emission;
            emission.rateOverTime = 34f;
            var sub = ps.subEmitters;
            sub.enabled = true;
            sub.AddSubEmitter(trail, ParticleSystemSubEmitterType.Birth, ParticleSystemSubEmitterProperties.InheritNothing);
            return ps;
        }

        /// <summary>Clods of earth thrown out of the crater.</summary>
        private static ParticleSystem Dirt(Transform parent, MaterialLibrary m, int count, Vector2 speed)
        {
            var ps = PB.Create(parent, "Dirt", m.Smoke);
            PB.Basics(ps, new Vector2(0.7f, 1.3f), speed, new Vector2(0.2f, 0.5f), 2.8f);
            var main = ps.main;
            main.startColor = new ParticleSystem.MinMaxGradient(new Color(0.3f, 0.25f, 0.18f), new Color(0.42f, 0.36f, 0.26f));
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Cone;
            shape.angle = 35f;
            shape.rotation = new Vector3(-90f, 0f, 0f);
            PB.Burst(ps, (0f, count));
            return ps;
        }

        /// <summary>Glowing embers that drift up and linger after the fireball.</summary>
        private static ParticleSystem Embers(Transform parent, MaterialLibrary m, int count, float scale)
        {
            var ps = PB.Create(parent, "Embers", m.Sparks);
            PB.Basics(ps, new Vector2(1.2f, 3f), new Vector2(1f, 4f) * scale, new Vector2(0.08f, 0.18f), -0.08f);
            var main = ps.main;
            main.startColor = new ParticleSystem.MinMaxGradient(new Color(1f, 0.7f, 0.25f), new Color(1f, 0.45f, 0.1f));
            var shape = ps.shape;
            shape.radius = 1.2f * scale;
            PB.Colors(ps, PB.Fade(new Color(1f, 0.8f, 0.4f), new Color(1f, 0.5f, 0.15f), new Color(0.6f, 0.15f, 0.05f)));
            var noise = ps.noise;
            noise.enabled = true;
            noise.strength = 0.8f;
            noise.frequency = 0.6f;
            PB.Burst(ps, (0.05f, count));
            return ps;
        }

        /// <summary>Low dust ring rolling outward along the ground.</summary>
        private static ParticleSystem DustRing(Transform parent, MaterialLibrary m, float size)
        {
            var ps = PB.Create(parent, "Dust Ring", m.Smoke);
            PB.Basics(ps, new Vector2(0.8f, 1.4f), new Vector2(3f, 5f), new Vector2(1.2f, 2f));
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = 0.5f;
            shape.rotation = new Vector3(90f, 0f, 0f);
            PB.Colors(ps, PB.Fade(new Color(0.55f, 0.5f, 0.4f), new Color(0.5f, 0.46f, 0.38f), new Color(0.45f, 0.42f, 0.36f), 0.5f));
            PB.Grow(ps, 0.6f, 1.8f);
            PB.Burst(ps, (0f, (int)(size * 2f)));
            return ps;
        }

        private static ParticleSystem Shockwave(Transform parent, MaterialLibrary m, float size)
        {
            var ps = PB.Create(parent, "Shockwave", m.Shockwave, ParticleSystemRenderMode.HorizontalBillboard);
            PB.Basics(ps, new Vector2(0.35f, 0.35f), Vector2.zero, new Vector2(size, size));
            var main = ps.main;
            main.startRotation = 0f;
            main.startColor = new Color(1f, 0.85f, 0.6f, 0.9f);
            var shape = ps.shape;
            shape.enabled = false;
            PB.Grow(ps, 0.1f, 1f);
            PB.Colors(ps, PB.Fade(Color.white, Color.white, Color.white, 0.9f));
            PB.Burst(ps, (0f, 1));
            ps.transform.localPosition = new Vector3(0f, 0.3f, 0f);
            return ps;
        }

        private static Light AddLight(Transform parent, float range)
        {
            var go = new GameObject("Light");
            go.transform.SetParent(parent, false);
            go.transform.localPosition = new Vector3(0f, 2f, 0f);
            var light = go.AddComponent<Light>();
            light.type = LightType.Point;
            light.range = range;
            light.color = new Color(1f, 0.62f, 0.3f);
            light.shadows = LightShadows.None;
            light.enabled = false;
            return light;
        }
    }
}
