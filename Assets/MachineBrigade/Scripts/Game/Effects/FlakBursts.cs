using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 25 G (DECISIONS 25G): an air-burst (flak) round going off by its target: a hot flash, a dark puff that
    /// hangs and spreads, a ring of sparks flung out flat round the burst and streaks of fragments thrown every way,
    /// sized by the round's calibre (20 mm small, 57 mm half as big again as 35 mm). Drawn on top of the impact the round
    /// already had (never in place of it). Four shared systems, emitted into on demand.
    /// </summary>
    internal sealed class FlakBursts
    {
        private readonly ParticleSystem _flash;
        private readonly ParticleSystem _puff;
        private readonly ParticleSystem _ring;
        private readonly ParticleSystem _fragments;

        public FlakBursts(MaterialLibrary m, Transform parent)
        {
            _flash = Shared(parent, "Flak Flash", m.Glow, 200, PB.Fade(new Color(1f, 0.85f, 0.55f), new Color(1f, 0.6f, 0.2f), new Color(0.8f, 0.3f, 0.05f)),
                ParticleSystemRenderMode.Billboard, 0.8f, 1.3f);
            // The puff: near-black at first, easing to a dark grey as it spreads (flak's smoke, not a fireball's).
            _puff = Shared(parent, "Flak Puffs", m.Smoke, 600, PB.Plume(0.05f, 0.24f, 0.85f), ParticleSystemRenderMode.Billboard, 0.55f, 1.9f);
            _ring = Shared(parent, "Flak Spark Rings", m.Sparks, 1200,
                PB.Fade(new Color(1f, 0.92f, 0.6f), new Color(1f, 0.62f, 0.2f), new Color(0.7f, 0.2f, 0.04f)), ParticleSystemRenderMode.Stretch, 1f, 0.6f);
            _fragments = Shared(parent, "Flak Fragments", m.Sparks, 1200,
                PB.Fade(new Color(1f, 0.8f, 0.45f), new Color(0.9f, 0.42f, 0.1f), new Color(0.3f, 0.12f, 0.05f)), ParticleSystemRenderMode.Stretch, 1f, 0.7f);
            var falling = _fragments.main;
            falling.gravityModifier = 0.6f;
            Streak(_ring, 0.04f, 1.6f);
            Streak(_fragments, 0.05f, 2.2f);
        }

        /// <summary>How big a burst of this calibre is drawn: 1 at 35 mm, 0.75 at 20 mm, 1.5 at 57 mm.</summary>
        internal static float Scale(float calibre) =>
            calibre <= 35f ? Mathf.Lerp(0.75f, 1f, Mathf.InverseLerp(20f, 35f, calibre)) : Mathf.Lerp(1f, 1.5f, Mathf.InverseLerp(35f, 57f, calibre));

        /// <summary>
        /// A burst at <paramref name="at"/> of a round of <paramref name="calibre"/> mm; <paramref name="reach"/> is its
        /// blast's radius (the fragments' reach), which the spark ring is flung out to.
        /// </summary>
        public void Burst(Vector3 at, float calibre, float reach)
        {
            var s = Scale(calibre);
            var ring = Mathf.Max(1.5f, reach) * 1.1f;
            Emit(_flash, at, Vector3.zero, 1.1f * s, 0.07f);
            for (var i = 0; i < 3; i++)
                Emit(_puff, at + Random.insideUnitSphere * 0.35f * s, Random.insideUnitSphere * 0.5f + Vector3.up * 0.25f,
                    Random.Range(1.1f, 1.6f) * s, Random.Range(1.8f, 2.6f));
            // The ring: flat round the burst in a tilted plane, flung out to about the blast's reach in its short life.
            var tilt = Quaternion.Euler(Random.Range(-35f, 35f), Random.Range(0f, 360f), Random.Range(-35f, 35f));
            var sparks = Mathf.RoundToInt(16 * s);
            for (var i = 0; i < sparks; i++)
            {
                var a = (i + Random.Range(-0.3f, 0.3f)) / sparks * Mathf.PI * 2f;
                var dir = tilt * new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
                var life = Random.Range(0.14f, 0.2f);
                Emit(_ring, at + dir * 0.2f, dir * (ring / life), Random.Range(0.12f, 0.18f) * s, life);
            }
            var bits = Mathf.RoundToInt(12 * s);
            for (var i = 0; i < bits; i++)
            {
                var dir = Random.onUnitSphere;
                Emit(_fragments, at, dir * Random.Range(16f, 28f) * s, Random.Range(0.08f, 0.14f) * s, Random.Range(0.18f, 0.34f));
            }
        }

        private static void Streak(ParticleSystem ps, float velocityScale, float lengthScale)
        {
            var r = ps.GetComponent<ParticleSystemRenderer>();
            r.velocityScale = velocityScale;
            r.lengthScale = lengthScale;
        }

        private static void Emit(ParticleSystem system, Vector3 position, Vector3 velocity, float size, float lifetime)
        {
            var emit = new ParticleSystem.EmitParams
            {
                position = position,
                velocity = velocity,
                startSize = size,
                startLifetime = lifetime,
                rotation = Random.Range(0f, 360f),
                applyShapeToPosition = false,
            };
            system.Emit(emit, 1);
        }

        private static ParticleSystem Shared(Transform parent, string name, Material material, int max, Gradient colour,
            ParticleSystemRenderMode mode, float growFrom, float growTo)
        {
            var ps = PB.Create(parent, name, material, mode);
            var main = ps.main;
            main.loop = true;
            main.maxParticles = max;
            var emission = ps.emission;
            emission.enabled = false;
            PB.Colors(ps, colour);
            PB.Grow(ps, growFrom, growTo);
            ps.Play();
            return ps;
        }
    }
}
