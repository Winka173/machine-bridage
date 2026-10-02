using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// An air-burst (flak) round going off by its target. Prompt 25 G drew it first (DECISIONS 25G); play-test 10
    /// (DECISIONS PT10 visuals) drew it again after footage of real flak (WWII 88 mm and 40 mm Bofors barrages, Cold War
    /// ZSU-23 and Gepard fire, 35 mm AHEAD, the Bofors 40 mm 3P proximity round) and the flak of War Thunder and
    /// Battlefield. What a real burst looks like:
    /// <list type="bullet">
    /// <item>A flash: a small, sharp orange-white pop that is gone within a few frames (the charge burns out at once;
    /// there is no fireball).</item>
    /// <item>The puff: a dense, round ball of black to charcoal smoke that blooms in a tenth of a second, then hangs where
    /// the round burst and drifts off on the wind for seconds, slowly greying and thinning at its edge. The bigger the
    /// calibre, the bigger, rounder and blacker the ball (a 20 mm burst is a small grey tuft, a 57 mm one a heavy black
    /// ball).</item>
    /// <item>The fragments: a quick spray of bright sparks flung out every way, most gone in a tenth of a second, a few
    /// hot ones arcing down a little longer. No ring: fragments do not fly out in a plane.</item>
    /// </list>
    /// For flak rounds this is the whole burst in the air (EffectsDirector no longer lays the Small blast, its lone ring
    /// or the generic grey puffs under it); a flak round fired at the ground bursts just over it, on top of its ground
    /// impact. Three shared systems emitted into on demand, about 40 particles a 35 mm burst; Low: fewer puffs and sparks.
    /// </summary>
    internal sealed class FlakBursts
    {
        private readonly ParticleSystem _flash;
        private readonly ParticleSystem _puff;
        private readonly ParticleSystem _sparks;

        /// <summary>The puff's shade: a heavy round's core, a light round's (a greyer tuft) and the skirt (times the colour over its life, 0.55 to 1).</summary>
        private const float CoreShade = 0.16f, LightShade = 0.45f, EdgeShade = 0.45f;

        public FlakBursts(MaterialLibrary m, Transform parent)
        {
            // The flash: orange-white, gone in its short life (the gradient only has to dim it).
            _flash = Shared(parent, "Flak Flash", m.Flash, 120,
                Fade(new Color(1f, 0.62f, 0.26f), new Color(1f, 0.38f, 0.08f), 0.5f), ParticleSystemRenderMode.Billboard, 0.8f, 1.25f);
            // The puff: blooms to full size in the first tenth of its life, then swells slowly as it hangs and drifts.
            _puff = Shared(parent, "Flak Puffs", m.Smoke, 900, PuffColour(), ParticleSystemRenderMode.Billboard, 1f, 1f);
            var bloom = _puff.sizeOverLifetime;
            bloom.size = new ParticleSystem.MinMaxCurve(1f, new AnimationCurve(new Keyframe(0f, 0.35f), new Keyframe(0.06f, 0.9f),
                new Keyframe(0.25f, 1f), new Keyframe(1f, 1.5f)));
            // The fragments: stretched sparks, yellow-white to orange, a little gravity for the slower ones.
            _sparks = Shared(parent, "Flak Fragments", m.Sparks, 1600,
                Fade(new Color(1f, 0.68f, 0.3f), new Color(0.9f, 0.3f, 0.06f), 0.5f), ParticleSystemRenderMode.Stretch, 1f, 0.6f);
            var main = _sparks.main;
            main.gravityModifier = 0.5f;
            var r = _sparks.GetComponent<ParticleSystemRenderer>();
            r.velocityScale = 0.025f;
            r.lengthScale = 1.2f;
        }

        /// <summary>
        /// How big a burst of this calibre is drawn: 0.8 at 20 mm, 1 at 35 mm, 1.5 at 57 mm, 1.8 at 76 mm and over (never
        /// smaller than prompt 25 G's 0.75 to 1.5).
        /// </summary>
        internal static float Scale(float calibre) =>
            calibre <= 35f ? Mathf.Lerp(0.8f, 1f, Mathf.InverseLerp(20f, 35f, calibre))
            : calibre <= 57f ? Mathf.Lerp(1f, 1.5f, Mathf.InverseLerp(35f, 57f, calibre))
            : Mathf.Lerp(1.5f, 1.8f, Mathf.InverseLerp(57f, 76f, calibre));

        /// <summary>How heavy the puff is, 0 at 20 mm to 1 at 57 mm and over: more, tighter, blacker and longer-lived balls.</summary>
        internal static float Weight(float calibre) => Mathf.InverseLerp(20f, 57f, calibre);

        /// <summary>
        /// A burst at <paramref name="at"/> of a round of <paramref name="calibre"/> mm; <paramref name="reach"/> is its
        /// blast's radius (the fragments' reach), which the spark spray is flung out to.
        /// </summary>
        public void Burst(Vector3 at, float calibre, float reach)
        {
            var s = Scale(calibre);
            var w = Weight(calibre);
            var low = MatchSettings.Tier == GraphicsQuality.Low;

            // The flash: a hot core and a wider orange pop, both gone in under a tenth of a second.
            Emit(_flash, at, Vector3.zero, 1.4f * s, 0.05f, Color.white);
            Emit(_flash, at, Vector3.zero, 2.6f * s, 0.08f, new Color(1f, 0.55f, 0.3f, 0.55f));

            // The puff: a tight cluster of dark balls (tighter and blacker for bigger rounds) with a paler, looser skirt.
            var drift = PB.Wind * 0.35f + Vector3.up * 0.12f;
            var core = Mathf.RoundToInt(Mathf.Lerp(5f, 8f, w)) - (low ? 2 : 0);
            var life = Mathf.Lerp(3.2f, 5.2f, w);
            var spread = 0.32f * s * Mathf.Lerp(1f, 0.75f, w);
            var shade = Mathf.Lerp(LightShade, CoreShade, w);
            for (var i = 0; i < core; i++)
            {
                var off = Random.insideUnitSphere * spread;
                Emit(_puff, at + off, drift + off * 0.6f + Random.insideUnitSphere * 0.12f,
                    Random.Range(1.5f, 1.9f) * s * Mathf.Lerp(1f, 1.15f, w), life * Random.Range(0.85f, 1.1f), new Color(shade, shade, shade, 1f));
            }
            var skirt = low ? 1 : 3;
            for (var i = 0; i < skirt; i++)
            {
                var off = Random.onUnitSphere * spread * 1.6f;
                Emit(_puff, at + off, drift + off * 0.5f, Random.Range(2.1f, 2.6f) * s, life * Random.Range(1f, 1.25f),
                    new Color(EdgeShade, EdgeShade, EdgeShade, 0.5f));
            }

            // The fragments: a quick spray out to about the blast's reach, and a few hot ones that fall a little longer.
            var fling = Mathf.Max(1.5f, reach);
            var sparks = Mathf.RoundToInt(28f * s * (low ? 0.6f : 1f));
            for (var i = 0; i < sparks; i++)
            {
                var dir = Random.onUnitSphere;
                var slow = i % 4 == 0;
                var t = slow ? Random.Range(0.25f, 0.4f) : Random.Range(0.07f, 0.14f);
                var speed = slow ? Random.Range(7f, 12f) : fling / t * Random.Range(0.8f, 1.1f);
                Emit(_sparks, at + dir * 0.15f * s, dir * speed, Random.Range(0.04f, 0.07f) * s, t, Color.white);
            }
        }

        /// <summary>Particles alive in the three systems (the editor's shots).</summary>
        internal int Alive => _flash.particleCount + _puff.particleCount + _sparks.particleCount;

        /// <summary>From <paramref name="start"/> to <paramref name="end"/>, its alpha gone by the end (<paramref name="hold"/>: where it is still near full).</summary>
        private static Gradient Fade(Color start, Color end, float hold)
        {
            var g = new Gradient();
            g.SetKeys(
                new[] { new GradientColorKey(start, 0f), new GradientColorKey(end, 1f) },
                new[] { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(0.85f, hold), new GradientAlphaKey(0f, 1f) });
            return g;
        }

        /// <summary>
        /// The puff over its life (times each puff's own shade): in at once, dense for the first third, thinning after,
        /// greying a little as it thins.
        /// </summary>
        private static Gradient PuffColour()
        {
            var g = new Gradient();
            g.SetKeys(
                new[] { new GradientColorKey(new Color(0.55f, 0.55f, 0.55f), 0f), new GradientColorKey(Color.white, 1f) },
                new[]
                {
                    new GradientAlphaKey(0f, 0f), new GradientAlphaKey(0.88f, 0.025f), new GradientAlphaKey(0.82f, 0.35f),
                    new GradientAlphaKey(0.4f, 0.7f), new GradientAlphaKey(0f, 1f),
                });
            return g;
        }

        private static void Emit(ParticleSystem system, Vector3 position, Vector3 velocity, float size, float lifetime, Color colour)
        {
            var emit = new ParticleSystem.EmitParams
            {
                position = position,
                velocity = velocity,
                startSize = size,
                startLifetime = lifetime,
                startColor = colour,
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
