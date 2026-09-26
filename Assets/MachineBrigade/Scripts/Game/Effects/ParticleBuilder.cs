using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>Terse helpers for configuring particle systems from code.</summary>
    internal static class ParticleBuilder
    {
        /// <summary>
        /// UV plus the particle's age and a stable random value (TEXCOORD0.zw), which the
        /// particle shader uses to shape and evolve fire and smoke puffs.
        /// </summary>
        private static readonly List<ParticleSystemVertexStream> Streams = new()
        {
            ParticleSystemVertexStream.Position,
            ParticleSystemVertexStream.Color,
            ParticleSystemVertexStream.UV,
            ParticleSystemVertexStream.AgePercent,
            ParticleSystemVertexStream.StableRandomX,
        };

        /// <summary>Gentle breeze every smoke column leans into, so plumes drift off their source.</summary>
        public static readonly Vector3 Wind = new(0.9f, 0f, 0.6f);

        public static ParticleSystem Create(Transform parent, string name, Material material,
            ParticleSystemRenderMode mode = ParticleSystemRenderMode.Billboard)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var ps = go.AddComponent<ParticleSystem>();
            // A new system starts playing immediately; stop it so its settings can be changed.
            ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);

            var main = ps.main;
            main.playOnAwake = false;
            main.loop = false;
            main.duration = 1f;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.scalingMode = ParticleSystemScalingMode.Hierarchy;
            main.maxParticles = 128;
            main.startRotation = new ParticleSystem.MinMaxCurve(0f, Mathf.PI * 2f);

            var emission = ps.emission;
            emission.rateOverTime = 0f;

            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Sphere;
            shape.radius = 0.2f;

            var renderer = go.GetComponent<ParticleSystemRenderer>();
            renderer.sharedMaterial = material;
            renderer.renderMode = mode;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            // A cap on screen coverage (fraction of the view height): zoomed right in, a giant
            // puff would otherwise fill the screen several times over, the peak of overdraw.
            renderer.maxParticleSize = 0.75f;
            renderer.SetActiveVertexStreams(Streams);
            // Alpha-blended smoke needs a stable order, or dark young puffs pop in front of older haze.
            if (material.HasFloat("_DstBlend") && material.GetFloat("_DstBlend") > (float)BlendMode.One + 0.5f)
                renderer.sortMode = ParticleSystemSortMode.OldestInFront;
            if (mode == ParticleSystemRenderMode.Stretch)
            {
                renderer.velocityScale = 0.05f;
                renderer.lengthScale = 1.5f;
            }
            return ps;
        }

        public static void Burst(ParticleSystem ps, params (float time, int count)[] bursts)
        {
            var list = new ParticleSystem.Burst[bursts.Length];
            for (var i = 0; i < bursts.Length; i++) list[i] = new ParticleSystem.Burst(bursts[i].time, (short)bursts[i].count);
            var emission = ps.emission;
            emission.enabled = true;
            emission.SetBursts(list);
        }

        public static void Basics(ParticleSystem ps, Vector2 lifetime, Vector2 speed, Vector2 size, float gravity = 0f)
        {
            var main = ps.main;
            main.startLifetime = new ParticleSystem.MinMaxCurve(lifetime.x, lifetime.y);
            main.startSpeed = new ParticleSystem.MinMaxCurve(speed.x, speed.y);
            main.startSize = new ParticleSystem.MinMaxCurve(size.x, size.y);
            main.gravityModifier = gravity;
        }

        public static void Colors(ParticleSystem ps, Gradient gradient)
        {
            var col = ps.colorOverLifetime;
            col.enabled = true;
            col.color = new ParticleSystem.MinMaxGradient(gradient);
        }

        public static void Grow(ParticleSystem ps, float from, float to)
        {
            var sol = ps.sizeOverLifetime;
            sol.enabled = true;
            sol.size = new ParticleSystem.MinMaxCurve(1f, AnimationCurve.EaseInOut(0f, from, 1f, to));
        }

        public static void Rise(ParticleSystem ps, float min, float max)
        {
            var vol = ps.velocityOverLifetime;
            vol.enabled = true;
            vol.space = ParticleSystemSimulationSpace.World;
            vol.x = new ParticleSystem.MinMaxCurve(Wind.x - 0.3f, Wind.x + 0.3f);
            vol.y = new ParticleSystem.MinMaxCurve(min, max);
            vol.z = new ParticleSystem.MinMaxCurve(Wind.z - 0.3f, Wind.z + 0.3f);
        }

        public static Gradient Fade(Color start, Color middle, Color end, float peakAlpha = 1f)
        {
            var g = new Gradient();
            g.SetKeys(
                new[] { new GradientColorKey(start, 0f), new GradientColorKey(middle, 0.35f), new GradientColorKey(end, 1f) },
                new[] { new GradientAlphaKey(peakAlpha, 0f), new GradientAlphaKey(peakAlpha * 0.8f, 0.5f), new GradientAlphaKey(0f, 1f) });
            return g;
        }

        public static Gradient FireGradient => Fade(new Color(1f, 0.82f, 0.5f), new Color(1f, 0.45f, 0.1f), new Color(0.4f, 0.08f, 0.03f));

        /// <summary>
        /// Smoke column: dark and dense at the source, thinning into light grey haze. Fades in
        /// so puffs do not pop into existence.
        /// </summary>
        public static Gradient Plume(float dark, float light, float alpha)
        {
            var g = new Gradient();
            g.SetKeys(
                new[] { new GradientColorKey(new Color(dark, dark, dark), 0f), new GradientColorKey(new Color(light, light, light * 0.97f), 1f) },
                new[]
                {
                    new GradientAlphaKey(0f, 0f), new GradientAlphaKey(alpha, 0.12f), new GradientAlphaKey(alpha * 0.55f, 0.5f),
                    new GradientAlphaKey(0f, 1f),
                });
            return g;
        }

        public static Gradient SmokeGradient(float shade, float alpha) =>
            Fade(new Color(shade, shade, shade), new Color(shade * 0.9f, shade * 0.9f, shade * 0.9f), new Color(shade * 0.8f, shade * 0.8f, shade * 0.8f), alpha);
    }
}
