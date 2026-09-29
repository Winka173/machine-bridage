using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Play-test 6 (DECISIONS 21H): a burning vehicle's fire, drawn anew as fire that belongs to the vehicle, after the
    /// burning tanks of World of Tanks, Battlefield and Company of Heroes (play-test 5's hull fire read as ground fire
    /// lifted on to the hull). Below 30 % health a vehicle burns at its sources, in the order a hit tank catches: the
    /// engine deck (flames licking up out of the grilles across the deck), then the turret's hatch (a tall tongue out
    /// of the open hatch, turning with the turret), then a breach in a flank (flames licking out sideways and up).
    /// Every source is placed on the hull each beat and every flame carries the hull's own velocity, so the fire is
    /// fixed to the vehicle and moves with it; the flames are short-lived narrow tongues (tall, not round, pinned at
    /// their base) over a hot glow on the metal, with small flickers dancing in the opening. Dark smoke pours out of
    /// the source and rises, keeping little of the hull's speed, so it streams out behind a vehicle on the move.
    /// Sparks spit out of it and now and then the fire flares up (a burst of flame, a pop of light, a shower of sparks
    /// and a gout of black smoke). Everything grows with the damage (<see cref="Severity"/>). Bosses burn the same way
    /// at their broken parts (<see cref="FeedPoint"/>, EffectsDirector.BossParts). No heat shimmer: a refraction pass
    /// needs the camera's opaque texture, which the phone renderer leaves off. Low: at most two sources, a slower
    /// beat, one tongue a beat, no flickers, half the sparks and embers, smoke every other beat, smaller flare-ups.
    /// </summary>
    internal sealed class HullFire
    {
        /// <summary>Below this share of its health a vehicle burns (it smokes from 60 %; EffectsDirector.ShowDamage).</summary>
        public const float Burning = 0.3f;

        /// <summary>How often a burning vehicle's fire is fed, in seconds, on High and Medium, and on Low.</summary>
        public const float Beat = 0.08f, LowBeat = 0.12f;

        /// <summary>How much of the hull's velocity its embers and smoke keep (the smoke streams out behind); flames keep all of it.</summary>
        public const float EmberCarry = 0.6f, SmokeCarry = 0.25f;

        private readonly ParticleSystem _glow, _tongues, _flicker, _sparks, _embers, _smoke;

        /// <summary>The sources in the hull's own frame: (across, along) in hull radii, height in its top, spread in radii; the engine deck first.</summary>
        private static readonly (Vector2 at, float height, float spread)[] Sources =
        {
            (new Vector2(0.1f, -0.55f), 0.56f, 0.42f), // the engine deck, a wide grille
            (new Vector2(-0.12f, 0.05f), 0.92f, 0.16f), // the turret's hatch
            (new Vector2(0.62f, 0.2f), 0.42f, 0.22f), // a breach in the flank
        };

        public HullFire(MaterialLibrary m, Transform parent)
        {
            var root = new GameObject("Hull Fires").transform;
            root.SetParent(parent, false);
            var fx = FxMaterials.Shared;
            // The glow on the metal at the source: soft, additive, yellow-white going to orange.
            _glow = Continuous(root, "Hull Fire Glow", m.Flash, 500,
                PB.Fade(new Color(1f, 0.86f, 0.55f), new Color(1f, 0.56f, 0.18f), new Color(0.7f, 0.22f, 0.05f)), 0.85f, 1.1f);
            // The tongues: tall narrow looping fire sheets pinned at their base, bright and nearly opaque at the root.
            var hot = new Material(fx.Flames) { name = "Hull Flames", hideFlags = HideFlags.DontSave };
            hot.SetFloat("_FireIntensity", 4.6f);
            hot.SetFloat("_FireOpacity", 0.7f);
            _tongues = Continuous(root, "Hull Fire Tongues", hot, 1200,
                PB.Hold(new Color(0.36f, 0.32f, 0.27f), new Color(0.26f, 0.22f, 0.2f), 0.06f, 0.55f), 0.7f, 1.05f);
            PB.Flipbook(_tongues, loop: true, cycles: 1f, tilt: 6f, pivotY: 0.33f);
            var tongues = _tongues.main;
            tongues.startSize3D = true;
            // Flickers: small additive licks jumping about in the opening.
            _flicker = Continuous(root, "Hull Fire Flicker", m.Flash, 500,
                PB.Fade(new Color(1f, 0.9f, 0.6f), new Color(1f, 0.6f, 0.2f), new Color(0.9f, 0.3f, 0.05f)), 1f, 0.5f);
            // Sparks spat out of the fire: fast bright streaks falling back.
            _sparks = Continuous(root, "Hull Fire Sparks", m.Sparks, 700,
                PB.Fade(new Color(1f, 0.92f, 0.6f), new Color(1f, 0.62f, 0.2f), new Color(0.8f, 0.2f, 0.05f)), 1f, 0.6f,
                ParticleSystemRenderMode.Stretch);
            var sparks = _sparks.main;
            sparks.gravityModifier = 0.55f;
            var streak = _sparks.GetComponent<ParticleSystemRenderer>();
            streak.velocityScale = 0.035f;
            streak.lengthScale = 1.2f;
            // Embers: lifted by the heat, wandering as they rise and dimming to red.
            _embers = Continuous(root, "Hull Fire Embers", m.Sparks, 900,
                PB.Fade(new Color(1f, 0.82f, 0.42f), new Color(1f, 0.5f, 0.14f), new Color(0.6f, 0.14f, 0.04f)), 1f, 0.35f);
            var embers = _embers.main;
            embers.gravityModifier = -0.12f;
            var drift = _embers.noise;
            drift.enabled = true;
            drift.strength = 0.9f;
            drift.frequency = 0.7f;
            // The smoke: black and dense at the source, greying as it climbs and spreads, leaning downwind.
            _smoke = Continuous(root, "Hull Fire Smoke", fx.Smoke, 1800,
                PB.Hold(new Color(0.1f, 0.095f, 0.09f), new Color(0.34f, 0.33f, 0.32f), 0.08f, 0.55f, 0.92f), 0.55f, 2.6f);
            PB.Flipbook(_smoke, loop: false, tilt: 22f);
            PB.Rise(_smoke, 1.4f, 2.6f);
        }

        /// <summary>How hard a vehicle at <paramref name="health"/> burns: 0 just under <see cref="Burning"/>, 1 near death.</summary>
        public static float Severity(float health) => Mathf.Clamp01(Mathf.InverseLerp(Burning, 0.03f, health));

        /// <summary>How many sources burn at <paramref name="severity"/> (at most two on Low).</summary>
        public static int PointsAt(float severity, bool low)
        {
            var n = severity < 0.34f ? 1 : severity < 0.68f ? 2 : 3;
            return low ? Mathf.Min(2, n) : n;
        }

        /// <summary>The seconds to the next feed of a burning vehicle's fire on this tier.</summary>
        public static float Next => MatchSettings.Tier == GraphicsQuality.Low ? LowBeat : Beat;

        /// <summary>The chance a beat that a source flares up: every few seconds, more often as it worsens (less on Low).</summary>
        public static float FlareChance(float severity, bool low) => (0.012f + 0.022f * severity) * (low ? 0.6f : 1f);

        /// <summary>One beat of a burning vehicle's fire (EffectsDirector calls it every <see cref="Next"/> seconds).</summary>
        public void Feed(VehicleView view, float health, int beat)
        {
            if (view.Root == null) return;
            var velocity = view.Root.forward * view.Speed;
            Feed(view.Root, view.Sim.Radius, view.Top, view.Flying, view.Id.GetHashCode(), health, beat, velocity, view.Turret);
        }

        /// <summary>
        /// One beat of the fire on a hull at <paramref name="root"/>, <paramref name="radius"/> across and
        /// <paramref name="top"/> high, moving at <paramref name="velocity"/>; <paramref name="seed"/> turns its sources
        /// (two burning tanks side by side do not burn alike); the hatch source rides <paramref name="turret"/>.
        /// </summary>
        public void Feed(Transform root, float radius, float top, bool flying, int seed, float health, int beat,
            Vector3 velocity = default, Transform turret = null)
        {
            var low = MatchSettings.Tier == GraphicsQuality.Low;
            var s = Severity(health);
            radius = Mathf.Max(0.8f, radius);
            var height = Mathf.Min(top, 2.8f);
            var points = flying ? 1 : PointsAt(s, low);
            var flip = (seed & 1) == 0 ? 1f : -1f;
            var carry = flying ? 0.7f : 1f;
            for (var k = 0; k < points; k++)
            {
                var (p, h, spread) = Sources[k];
                Vector3 at, across;
                if (k == 1 && turret != null)
                {
                    // Out of the turret's hatch: it turns with the turret.
                    at = turret.position + turret.right * (p.x * flip * radius * 0.6f) - turret.forward * (0.15f * radius);
                    at.y = root.position.y + height * h;
                    across = turret.right;
                }
                else
                {
                    at = root.position + Vector3.up * (flying ? 0.2f : height * h) + root.right * (p.x * flip * radius) +
                         root.forward * (p.y * radius);
                    across = root.right;
                }
                // A breach in the flank licks out sideways as well as up.
                var up = k == 2 ? (Vector3.up + root.right * (flip * 0.45f)).normalized : Vector3.up;
                // The first source is the biggest; the others join smaller and grow with the damage.
                var size = radius * (k == 0 ? 0.5f : 0.4f) * Mathf.Lerp(0.8f, 1.45f, s);
                Source(at, across * (spread * radius), up, size, s, velocity * carry, low, beat + k);
            }
        }

        /// <summary>
        /// One beat of a fire at <paramref name="point"/> (a boss's broken part: prompt 9's part fires, drawn the same
        /// way), <paramref name="size"/> big (about a tank's engine fire at 1), moving at <paramref name="velocity"/>.
        /// </summary>
        public void FeedPoint(Vector3 point, float size, float severity, Vector3 velocity, int beat)
        {
            var low = MatchSettings.Tier == GraphicsQuality.Low;
            var across = Vector3.Cross(Vector3.up, velocity.sqrMagnitude > 0.01f ? velocity.normalized : Vector3.forward);
            Source(point, across * size * 0.6f, Vector3.up, size * 1.2f, severity, velocity, low, beat);
        }

        /// <summary>One source's beat: glow, tongues, flickers, sparks, embers, smoke, and now and then a flare-up.</summary>
        private void Source(Vector3 at, Vector3 across, Vector3 up, float size, float s, Vector3 velocity, bool low, int beat)
        {
            Glow(at + up * size * 0.15f, size * Random.Range(1.0f, 1.3f), Mathf.Lerp(0.5f, 0.85f, s), velocity);
            Tongue(at + across * Random.Range(-1f, 1f), up, size, velocity);
            if (!low) Tongue(at + across * Random.Range(-1f, 1f), up, size * 0.75f, velocity);
            if (!low && beat % 2 == 0) Flicker(at + across * Random.Range(-1f, 1f) + up * size * 0.2f, size, velocity);
            var sparks = Mathf.RoundToInt(Mathf.Lerp(0.2f, 1.2f, s) * (low ? 0.5f : 1f) + Random.value * 0.5f);
            for (var i = 0; i < sparks; i++) Spark(at + up * size * 0.3f, up, velocity, 1f);
            var embers = Mathf.RoundToInt(Mathf.Lerp(0.3f, 1.6f, s) * (low ? 0.5f : 1f) + Random.value * 0.5f);
            for (var i = 0; i < embers; i++) Ember(at + up * size * 0.6f, s, velocity);
            if (!low || beat % 2 == 0) Smoke(at + up * size * 0.8f, size, s, velocity);
            if (Random.value < FlareChance(s, low)) FlareUp(at, across, up, size, s, velocity, low);
        }

        /// <summary>A flare-up: a burst of taller flames, a pop of light, a shower of sparks and a gout of black smoke.</summary>
        private void FlareUp(Vector3 at, Vector3 across, Vector3 up, float size, float s, Vector3 velocity, bool low)
        {
            var big = size * (low ? 1.3f : 1.6f);
            Glow(at + up * size * 0.4f, big * 1.8f, 1f, velocity);
            for (var i = 0; i < (low ? 2 : 4); i++) Tongue(at + across * Random.Range(-1f, 1f), up, big, velocity);
            for (var i = 0; i < (low ? 5 : 12); i++) Spark(at + up * size * 0.4f, up, velocity, 1.6f);
            for (var i = 0; i < (low ? 1 : 2); i++) Smoke(at + up * size, big, Mathf.Max(s, 0.8f), velocity);
        }

        private void Glow(Vector3 at, float size, float alpha, Vector3 velocity)
        {
            _glow.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = velocity, startSize = size, startColor = new Color(1f, 0.72f, 0.36f, alpha),
                startLifetime = Random.Range(0.12f, 0.2f), applyShapeToPosition = false,
            }, 1);
        }

        private void Tongue(Vector3 at, Vector3 up, float size, Vector3 velocity)
        {
            var width = size * Random.Range(0.75f, 0.95f);
            _tongues.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = velocity + up * Random.Range(0.2f, 0.5f) + Random.insideUnitSphere * 0.08f,
                startSize3D = new Vector3(width, size * Random.Range(1.15f, 1.4f), 1f), startLifetime = Random.Range(0.55f, 0.85f),
                rotation = Random.Range(-7f, 7f), applyShapeToPosition = false,
            }, 1);
        }

        private void Flicker(Vector3 at, float size, Vector3 velocity)
        {
            _flicker.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = velocity + Vector3.up * Random.Range(1.2f, 2.4f) + Random.insideUnitSphere * 0.4f,
                startSize = size * Random.Range(0.3f, 0.5f), startLifetime = Random.Range(0.12f, 0.22f), applyShapeToPosition = false,
            }, 1);
        }

        private void Spark(Vector3 at, Vector3 up, Vector3 velocity, float kick)
        {
            _sparks.Emit(new ParticleSystem.EmitParams
            {
                position = at + Random.insideUnitSphere * 0.2f,
                velocity = velocity + (up * Random.Range(2.5f, 5.5f) + Random.insideUnitSphere * 2.2f) * kick,
                startSize = Random.Range(0.04f, 0.08f), startLifetime = Random.Range(0.45f, 0.9f), applyShapeToPosition = false,
            }, 1);
        }

        private void Ember(Vector3 at, float severity, Vector3 velocity)
        {
            _embers.Emit(new ParticleSystem.EmitParams
            {
                position = at + Random.insideUnitSphere * 0.3f,
                velocity = velocity * EmberCarry + Vector3.up * Random.Range(1.6f, 3.4f) + Random.insideUnitSphere * 1.1f,
                startSize = Random.Range(0.06f, 0.12f) * (1f + severity * 0.4f), startLifetime = Random.Range(0.9f, 1.8f),
                applyShapeToPosition = false,
            }, 1);
        }

        private void Smoke(Vector3 at, float size, float severity, Vector3 velocity)
        {
            var shade = Mathf.Lerp(0.2f, 0.05f, severity);
            _smoke.Emit(new ParticleSystem.EmitParams
            {
                position = at + Random.insideUnitSphere * size * 0.15f,
                velocity = velocity * SmokeCarry + Vector3.up * Random.Range(0.6f, 1.1f) + Random.insideUnitSphere * 0.25f,
                startSize = size * Random.Range(0.9f, 1.2f) * Mathf.Lerp(0.85f, 1.25f, severity),
                startLifetime = Random.Range(2.4f, 3.6f) * Mathf.Lerp(0.9f, 1.25f, severity),
                startColor = new Color(shade * 4f + 0.2f, shade * 4f + 0.2f, shade * 4f + 0.2f, Mathf.Lerp(0.62f, 0.86f, severity)),
                rotation = Random.Range(0f, 360f), applyShapeToPosition = false,
            }, 1);
        }

        private ParticleSystem[] All => new[] { _glow, _tongues, _flicker, _sparks, _embers, _smoke };

        /// <summary>Particles alive in the fire's systems (for tests and the budget log).</summary>
        internal int Alive
        {
            get
            {
                var n = 0;
                foreach (var ps in All) n += ps.particleCount;
                return n;
            }
        }

        /// <summary>Lets the systems run their emitted particles (tests).</summary>
        internal void Simulate(float seconds)
        {
            foreach (var ps in All) ps.Simulate(seconds, false, false);
        }

        private static ParticleSystem Continuous(Transform parent, string name, Material material, int max, Gradient colour,
            float growFrom, float growTo, ParticleSystemRenderMode mode = ParticleSystemRenderMode.Billboard)
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
