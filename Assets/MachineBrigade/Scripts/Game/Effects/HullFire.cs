using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Play-test 5 (DECISIONS 20V): a badly damaged vehicle on fire, drawn anew to read on a phone. It burns at fixed
    /// fire points on its hull (the engine deck first, then the turret ring, then a flank: one, two or three as its
    /// health falls), each in four layers: a bright flame core glowing on the hull, upright tongues of flame licking
    /// off it, embers rising and drifting, and a column of dark smoke climbing out of it and leaning with the wind.
    /// Everything grows with the damage (<see cref="Severity"/>): a small fire on one point just under 30 % health,
    /// three big ones and a thick black column near death. Low graphics keep every layer and shape with fewer
    /// particles: at most two fire points, a slower beat, half the embers and smoke every other beat.
    /// </summary>
    internal sealed class HullFire
    {
        /// <summary>Below this share of its health a vehicle burns (it smokes from 60 %; EffectsDirector.ShowDamage).</summary>
        public const float Burning = 0.3f;

        /// <summary>How often a burning vehicle's fire is fed, in seconds, on High and Medium, and on Low.</summary>
        public const float Beat = 0.08f, LowBeat = 0.12f;

        private readonly ParticleSystem _core, _flames, _embers, _smoke;

        /// <summary>The fire points in the hull's own frame: (across, along) in hull radii; the engine deck first.</summary>
        private static readonly Vector2[] Points = { new(0.12f, -0.5f), new(-0.18f, 0.05f), new(0.42f, 0.28f) };

        public HullFire(MaterialLibrary m, Transform parent)
        {
            var root = new GameObject("Hull Fires").transform;
            root.SetParent(parent, false);
            // The core: a soft additive glow where the fire sits, yellow-white in the middle of the flames. It is
            // what makes a small fire read at a phone's battle zoom.
            _core = Continuous(root, "Hull Fire Core", m.Flash, 400,
                PB.Fade(new Color(1f, 0.85f, 0.5f), new Color(1f, 0.58f, 0.2f), new Color(0.8f, 0.28f, 0.06f)), 0.8f, 1.15f);
            // The flames: upright looping fire sheets, brighter and more opaque than the old licks, fanned a little.
            var fx = FxMaterials.Shared;
            var hot = new Material(fx.Flames) { name = "Hull Flames", hideFlags = HideFlags.DontSave };
            hot.SetFloat("_FireIntensity", 4.2f);
            hot.SetFloat("_FireOpacity", 0.62f);
            _flames = Continuous(root, "Hull Fire Flames", hot, 900,
                PB.Hold(new Color(0.34f, 0.3f, 0.26f), new Color(0.28f, 0.25f, 0.22f), 0.08f, 0.62f), 0.75f, 1.2f);
            PB.Flipbook(_flames, loop: true, tilt: 8f, pivotY: -0.12f);
            // Embers: sparks lifted by the heat, wandering as they rise and dimming to red.
            _embers = Continuous(root, "Hull Fire Embers", m.Sparks, 900,
                PB.Fade(new Color(1f, 0.82f, 0.42f), new Color(1f, 0.5f, 0.14f), new Color(0.6f, 0.14f, 0.04f)), 1f, 0.35f);
            var embers = _embers.main;
            embers.gravityModifier = -0.12f;
            var drift = _embers.noise;
            drift.enabled = true;
            drift.strength = 0.9f;
            drift.frequency = 0.7f;
            // The smoke: black and dense at the fire, greying as it climbs, spreading wide and leaning downwind.
            _smoke = Continuous(root, "Hull Fire Smoke", fx.Smoke, 1600,
                PB.Hold(new Color(0.11f, 0.105f, 0.1f), new Color(0.36f, 0.35f, 0.34f), 0.1f, 0.55f, 0.9f), 0.7f, 2.4f);
            PB.Flipbook(_smoke, loop: false, tilt: 22f);
            PB.Rise(_smoke, 1.4f, 2.6f);
        }

        /// <summary>How hard a vehicle at <paramref name="health"/> burns: 0 just under <see cref="Burning"/>, 1 near death.</summary>
        public static float Severity(float health) => Mathf.Clamp01(Mathf.InverseLerp(Burning, 0.03f, health));

        /// <summary>How many fire points burn at <paramref name="severity"/> (at most two on Low).</summary>
        public static int PointsAt(float severity, bool low)
        {
            var n = severity < 0.34f ? 1 : severity < 0.68f ? 2 : 3;
            return low ? Mathf.Min(2, n) : n;
        }

        /// <summary>The seconds to the next feed of a burning vehicle's fire on this tier.</summary>
        public static float Next => MatchSettings.Tier == GraphicsQuality.Low ? LowBeat : Beat;

        /// <summary>One beat of a burning vehicle's fire (EffectsDirector calls it every <see cref="Next"/> seconds).</summary>
        public void Feed(VehicleView view, float health, int beat)
        {
            if (view.Root == null) return;
            Feed(view.Root, view.Sim.Radius, view.Top, view.Flying, view.Id.GetHashCode(), health, beat);
        }

        /// <summary>
        /// One beat of the fire on a hull at <paramref name="root"/>, <paramref name="radius"/> across and
        /// <paramref name="top"/> high; <paramref name="seed"/> turns its fire points (two burning tanks side by
        /// side do not burn alike).
        /// </summary>
        public void Feed(Transform root, float radius, float top, bool flying, int seed, float health, int beat)
        {
            var low = MatchSettings.Tier == GraphicsQuality.Low;
            var s = Severity(health);
            radius = Mathf.Max(0.8f, radius);
            var height = flying ? 0.2f : Mathf.Min(top * 0.62f, 1.6f);
            var points = flying ? 1 : PointsAt(s, low);
            var flip = (seed & 1) == 0 ? 1f : -1f;
            for (var k = 0; k < points; k++)
            {
                var p = Points[k];
                var at = root.position + Vector3.up * height + root.right * (p.x * flip * radius) + root.forward * (p.y * radius);
                // The first point is the biggest; the others join smaller and grow with the damage.
                var size = radius * (k == 0 ? 0.62f : 0.46f) * Mathf.Lerp(0.8f, 1.45f, s);
                Glow(at + Vector3.up * size * 0.25f, size * Random.Range(1.1f, 1.4f), Mathf.Lerp(0.55f, 0.9f, s));
                Flame(at, size);
                if (!low || (beat + k) % 2 == 0) Flame(at + Random.insideUnitSphere * size * 0.25f, size * 0.7f);
                var sparks = Mathf.RoundToInt(Mathf.Lerp(0.3f, 2.2f, s) * (low ? 0.5f : 1f) + Random.value * 0.6f);
                for (var i = 0; i < sparks; i++) Ember(at + Vector3.up * size * 0.5f, s);
                if (!low || beat % 2 == 0) Smoke(at + Vector3.up * size * 0.9f, size, s);
            }
        }

        private void Glow(Vector3 at, float size, float alpha)
        {
            var colour = new Color(1f, 0.72f, 0.35f, alpha);
            _core.Emit(new ParticleSystem.EmitParams
            {
                position = at, startSize = size, startColor = colour, startLifetime = Random.Range(0.14f, 0.22f), applyShapeToPosition = false,
            }, 1);
        }

        private void Flame(Vector3 at, float size)
        {
            _flames.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = Vector3.up * Random.Range(0.6f, 1.3f) + Random.insideUnitSphere * 0.2f,
                startSize = size * Random.Range(0.85f, 1.2f), startLifetime = Random.Range(0.42f, 0.7f), rotation = Random.Range(-9f, 9f),
                applyShapeToPosition = false,
            }, 1);
        }

        private void Ember(Vector3 at, float severity)
        {
            _embers.Emit(new ParticleSystem.EmitParams
            {
                position = at + Random.insideUnitSphere * 0.3f,
                velocity = Vector3.up * Random.Range(1.6f, 3.4f) + Random.insideUnitSphere * 1.1f,
                startSize = Random.Range(0.06f, 0.12f) * (1f + severity * 0.4f), startLifetime = Random.Range(0.9f, 1.8f),
                applyShapeToPosition = false,
            }, 1);
        }

        private void Smoke(Vector3 at, float size, float severity)
        {
            var shade = Mathf.Lerp(0.2f, 0.05f, severity);
            _smoke.Emit(new ParticleSystem.EmitParams
            {
                position = at + Random.insideUnitSphere * size * 0.2f,
                velocity = Vector3.up * Random.Range(0.4f, 0.9f) + Random.insideUnitSphere * 0.25f,
                startSize = size * Random.Range(0.9f, 1.2f) * Mathf.Lerp(0.85f, 1.2f, severity),
                startLifetime = Random.Range(2.4f, 3.6f) * Mathf.Lerp(0.9f, 1.25f, severity),
                startColor = new Color(shade * 4f + 0.2f, shade * 4f + 0.2f, shade * 4f + 0.2f, Mathf.Lerp(0.65f, 0.9f, severity)),
                rotation = Random.Range(0f, 360f), applyShapeToPosition = false,
            }, 1);
        }

        /// <summary>Particles alive in the fire's systems (for tests and the budget log).</summary>
        internal int Alive => _core.particleCount + _flames.particleCount + _embers.particleCount + _smoke.particleCount;

        /// <summary>Lets the systems run their emitted particles (tests).</summary>
        internal void Simulate(float seconds)
        {
            foreach (var ps in new[] { _core, _flames, _embers, _smoke }) ps.Simulate(seconds, false, false);
        }

        private static ParticleSystem Continuous(Transform parent, string name, Material material, int max, Gradient colour,
            float growFrom, float growTo)
        {
            var ps = PB.Create(parent, name, material);
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
