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

        /// <summary>
        /// Flipbook systems: this frame's UV and the next one's (TEXCOORD0), the blend between them,
        /// the age and a stable random value (TEXCOORD1), for <c>MachineBrigade/Flipbook</c>.
        /// </summary>
        private static readonly List<ParticleSystemVertexStream> FlipbookStreams = new()
        {
            ParticleSystemVertexStream.Position,
            ParticleSystemVertexStream.Color,
            ParticleSystemVertexStream.UV,
            ParticleSystemVertexStream.UV2,
            ParticleSystemVertexStream.AnimBlend,
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

        /// <summary>
        /// Plays a flipbook sheet (<see cref="FxMaterials"/>) on the particles. Once: the sheet runs
        /// from <paramref name="from"/> to <paramref name="to"/> (fractions of it) over each
        /// particle's life. Looping: each particle starts on a random frame and runs through the
        /// sheet <paramref name="cycles"/> times. Particles stay upright (the sheets rise), with a
        /// little random tilt, and half are mirrored so no two neighbours look alike.
        /// </summary>
        public static void Flipbook(ParticleSystem ps, bool loop, float cycles = 1f, float from = 0f, float to = 1f,
            float tilt = 12f, float pivotY = 0f)
        {
            var tsa = ps.textureSheetAnimation;
            tsa.enabled = true;
            tsa.mode = ParticleSystemAnimationMode.Grid;
            tsa.numTilesX = FxMaterials.Tiles;
            tsa.numTilesY = FxMaterials.Tiles;
            tsa.animation = ParticleSystemAnimationType.WholeSheet;
            tsa.timeMode = ParticleSystemAnimationTimeMode.Lifetime;
            const int frames = FxMaterials.Tiles * FxMaterials.Tiles;
            if (loop)
            {
                tsa.frameOverTime = new ParticleSystem.MinMaxCurve(1f, AnimationCurve.Linear(0f, 0f, 1f, 1f));
                tsa.startFrame = new ParticleSystem.MinMaxCurve(0f, frames - 1);
                tsa.cycleCount = Mathf.Max(1, Mathf.RoundToInt(cycles));
            }
            else
            {
                // Stop just short of the end, where the frame index would wrap back to the first.
                tsa.frameOverTime = new ParticleSystem.MinMaxCurve(1f, AnimationCurve.Linear(0f, from, 1f, Mathf.Min(to, 0.999f)));
                tsa.startFrame = 0f;
                tsa.cycleCount = 1;
            }

            var main = ps.main;
            main.startRotation = new ParticleSystem.MinMaxCurve(-tilt * Mathf.Deg2Rad, tilt * Mathf.Deg2Rad);
            var renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.SetActiveVertexStreams(FlipbookStreams);
            renderer.flip = new Vector3(0.5f, 0f, 0f);
            renderer.pivot = new Vector3(0f, pivotY, 0f);
            // Premultiplied smoke needs a stable order, or young puffs pop in front of older ones.
            renderer.sortMode = ParticleSystemSortMode.OldestInFront;
        }

        /// <summary>
        /// Particles bounce off the ground (y = 0) and skitter to a stop instead of sinking
        /// through it. One plane test per particle: far cheaper than world collision.
        /// </summary>
        public static void BounceOffGround(ParticleSystem ps, Transform ground, float bounce = 0.35f, float dampen = 0.45f,
            float lifetimeLoss = 0f)
        {
            var collision = ps.collision;
            collision.enabled = true;
            collision.type = ParticleSystemCollisionType.Planes;
            collision.SetPlane(0, ground);
            collision.bounce = bounce;
            collision.dampen = dampen;
            collision.lifetimeLoss = lifetimeLoss;
            collision.radiusScale = 0.3f;
            collision.enableDynamicColliders = false;
            collision.sendCollisionMessages = false;
        }

        /// <summary>The plane particles bounce off: the battlefield ground.</summary>
        public static Transform GroundPlane(Transform parent)
        {
            var plane = new GameObject("Ground Plane").transform;
            plane.SetParent(parent, false);
            plane.SetPositionAndRotation(new Vector3(0f, 0.04f, 0f), Quaternion.identity);
            return plane;
        }

        /// <summary>Alpha that fades in quickly, holds, then fades out: flipbook fire and smoke (colour is kept).</summary>
        public static Gradient Hold(Color start, Color end, float fadeIn = 0.08f, float fadeOut = 0.7f, float alpha = 1f)
        {
            var g = new Gradient();
            g.SetKeys(
                new[] { new GradientColorKey(start, 0f), new GradientColorKey(end, 1f) },
                new[] { new GradientAlphaKey(0f, 0f), new GradientAlphaKey(alpha, fadeIn), new GradientAlphaKey(alpha, fadeOut), new GradientAlphaKey(0f, 1f) });
            return g;
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
