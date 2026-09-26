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

        public void Play(Vector3 position, float now)
        {
            Root.transform.position = position;
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
                    systems.Add(Sparks(t, m, 6, new Vector2(4f, 9f), 0.1f));
                    systems.Add(Dust(t, m, 2, new Vector2(0.6f, 1.2f)));
                    duration = 1f;
                    break;

                case ExplosionTier.Medium:
                    systems.Add(Flash(t, m, 3.5f));
                    systems.Add(Fireball(t, m, 8, new Vector2(1f, 2.2f), new Vector2(1f, 4f), 0.3f));
                    systems.Add(Smoke(t, m, 6, new Vector2(1.2f, 2.4f), new Vector2(1.2f, 2.2f), 0.26f));
                    systems.Add(Sparks(t, m, 10, new Vector2(6f, 14f), 0.14f));
                    duration = 2.5f;
                    break;

                case ExplosionTier.Large:
                    systems.Add(Flash(t, m, 7f));
                    systems.Add(Fireball(t, m, 14, new Vector2(2f, 4f), new Vector2(2f, 6f), 0.6f));
                    systems.Add(Smoke(t, m, 10, new Vector2(2.5f, 4.5f), new Vector2(2.5f, 4f), 0.2f));
                    systems.Add(Sparks(t, m, 22, new Vector2(8f, 18f), 0.18f));
                    systems.Add(Debris(t, m, 10, new Vector2(5f, 11f)));
                    systems.Add(Shockwave(t, m, 14f));
                    light = AddLight(t, 14f);
                    lightIntensity = 8f;
                    duration = 4.5f;
                    break;

                default: // Huge and above
                    var s = tier == ExplosionTier.Huge ? 1f : 1.6f;
                    systems.Add(Flash(t, m, 12f * s));
                    var fireball = Fireball(t, m, 24, new Vector2(3f, 6f) * s, new Vector2(3f, 9f) * s, 1f * s);
                    PB.Burst(fireball, (0f, 24), (0.15f, 10), (0.3f, 6));
                    systems.Add(fireball);
                    systems.Add(Smoke(t, m, 16, new Vector2(4f, 7f) * s, new Vector2(4f, 7f), 0.16f));
                    systems.Add(Sparks(t, m, 36, new Vector2(10f, 24f), 0.22f));
                    systems.Add(Debris(t, m, 18, new Vector2(7f, 16f)));
                    systems.Add(Shockwave(t, m, 26f * s));
                    light = AddLight(t, 24f * s);
                    lightIntensity = 14f;
                    duration = 7f;
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

        private static ParticleSystem Fireball(Transform parent, MaterialLibrary m, int count, Vector2 size, Vector2 speed, float radius)
        {
            var ps = PB.Create(parent, "Fireball", m.Fire);
            PB.Basics(ps, new Vector2(0.3f, 0.65f), speed, size, -0.1f);
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
            PB.Colors(ps, PB.SmokeGradient(shade, 0.7f));
            PB.Grow(ps, 0.8f, 2.4f);
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
