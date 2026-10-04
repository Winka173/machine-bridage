using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// How a munition's motor burns, in lengths of the munition as drawn: its flame's length at
    /// cruise and width at the nozzle, the size of its smoke puffs and how far apart they are,
    /// and the share of the flight it burns for (DECISIONS 12B).
    /// </summary>
    internal readonly struct Plume
    {
        public Plume(float length, float width, float smoke, float burn, float puffs = 0.3f)
        {
            // Play test 3: every plume 40 % longer and 20 % wider than first drawn (12B).
            Length = length * 1.4f;
            Width = width * 1.2f;
            Smoke = smoke;
            Burn = burn;
            Puffs = puffs;
        }

        /// <summary>Flame length at cruise speed, in munition lengths.</summary>
        public float Length { get; }

        /// <summary>Flame width at the nozzle, in munition lengths.</summary>
        public float Width { get; }

        /// <summary>A smoke puff's size when it leaves the flame, in flame widths; 0 for no smoke.</summary>
        public float Smoke { get; }

        /// <summary>Share of the flight the motor burns (the flame and the smoke stop after it).</summary>
        public float Burn { get; }

        /// <summary>Distance between smoke puffs in puff sizes on High (a salvo's many trails are sparser).</summary>
        public float Puffs { get; }

        public bool Burns => Length > 0f;

        /// <summary>
        /// Play-test 5 (DECISIONS 20V): how much of its flame a heavy launcher's munition keeps: the SAM launcher's Buk,
        /// the thermobaric launcher's and the heavy rocket artillery's rockets, the ballistic missile, the long-range
        /// SAM and the Patriot batteries (and the towers that share their missiles). The flame is still measured in the
        /// munition's own drawn lengths at its cruise speed, so it stays tied to the munition's size whatever its speed.
        /// </summary>
        public const float ShortFlame = 0.6f;

        /// <summary>The munitions drawn with a <see cref="ShortFlame"/>.</summary>
        public static bool Short(WeaponDef weapon) => weapon != null && weapon.Id is "buk_launcher" or "sam_long" or "sam_post"
            or "thermobaric_rockets" or "rockets_300mm" or "ballistic_missile" or "sam_48n6" or "patriot" or "sam_battery" or "sam_pac3"
            or "sam_battery_lrr";

        private Plume Shortened() => new(this, ShortFlame);

        private Plume(Plume p, float keep)
        {
            Length = p.Length * keep;
            Width = p.Width;
            Smoke = p.Smoke;
            Burn = p.Burn;
            Puffs = p.Puffs;
        }

        /// <summary>
        /// The motor of what <paramref name="weapon"/> fires: surface-to-air missiles and the
        /// ballistic missile a long plume, anti-tank missiles a short sharp one; rockets burn
        /// most of their flight, a cruise missile's jet is short and hot; drones fly on
        /// propellers and electric motors, with no flame.
        /// </summary>
        public static Plume For(WeaponDef weapon, ProjectileKind kind, string model, bool airLaunched)
        {
            var plume = Drawn(weapon, kind, model, airLaunched);
            return plume.Burns && Short(weapon) ? plume.Shortened() : plume;
        }

        private static Plume Drawn(WeaponDef weapon, ProjectileKind kind, string model, bool airLaunched)
        {
            switch (kind)

            {
                case ProjectileKind.Drone:
                    return default;
                case ProjectileKind.Rocket:
                    // Play-test 14: every rocket's motor and smoke trail last to the detonation (owner: "vệt khói phải kéo đến lúc
                    // nổ"); the artillery rockets and the ballistic missile used to burn out at 85 % and 75 % of the flight.
                    if (weapon?.Id == "ballistic_missile") return new Plume(1.5f, 0.24f, 1.8f, 1f, 0.3f);
                    return weapon != null && weapon.MinRange > 0f ? new Plume(1.6f, 0.26f, 1.7f, 1f, 0.45f) : new Plume(1.7f, 0.3f, 1.6f, 1f, 0.4f);
                case ProjectileKind.Missile:
                    if (model is "cruise_missile" or "jassm") return new Plume(0.6f, 0.13f, 1.4f, 1f, 0.35f);
                    if (model is "stinger" or "igla") return new Plume(2f, 0.28f, 1.7f, 1f);
                    var antiAir = weapon != null && weapon.CanTarget(true) && !weapon.CanTarget(false);
                    if (antiAir) return airLaunched ? new Plume(2.1f, 0.22f, 1.7f, 1f) : new Plume(2.6f, 0.24f, 1.9f, 1f);
                    // Anti-tank and air-to-ground missiles: a short, sharp flame.
                    return airLaunched ? new Plume(1.6f, 0.27f, 1.6f, 1f) : new Plume(1.3f, 0.28f, 1.6f, 1f);
                default:
                    return default;
            }
        }
    }

    /// <summary>
    /// The burning motor behind every missile and rocket in flight, in five shared systems: a
    /// white-hot core on the nozzle, a hot yellow tongue, a flame cone of stretched quads that
    /// tapers and reddens, flickers every frame and grows longer as the missile speeds up, a soft
    /// glow round it for the bloom, and a smoke trail that leaves the tip of the flame, lingers,
    /// spreads and drifts off with the wind. The flame's particles fly with the missile, so the
    /// cone stays on its tail. Particle counts follow the graphics tier (fewer cone quads, no glow
    /// and a sparser, shorter-lived trail on Low), never below the old single motor puff.
    /// </summary>
    internal sealed class MotorPlumes
    {
        /// <summary>A cone quad's length in its widths.</summary>
        private const float ConeStretch = 4.5f;

        /// <summary>The hot inner tongue's length in its widths.</summary>
        private const float TongueStretch = 3f;

        /// <summary>The glow's length in its widths: a soft body under the whole flame that bridges its quads.</summary>
        private const float GlowStretch = 4f;

        /// <summary>
        /// Where along a stretched quad its particle sits, from the quad's front: Unity draws a
        /// stretched billboard trailing back from its particle, against its velocity (the missile's).
        /// </summary>
        private const float Head = 0f;

        /// <summary>How much of a flame quad's length the fire shader fills (it tears the ends away).</summary>
        private const float Fill = 0.5f;

        private static Material _fire;

        private readonly ParticleSystem _core, _cone, _tongue, _glow, _smoke;

        public MotorPlumes(MaterialLibrary m, Transform parent)
        {
            var root = new GameObject("Motor Plumes").transform;
            root.SetParent(parent, false);
            _smoke = Shared(root, "Motor Smoke", m.Smoke, SmokeBudget, ParticleSystemRenderMode.Billboard);
            PB.Colors(_smoke, Smoke());
            // Spreads fast as it leaves the flame, then slowly as it hangs.
            var spread = _smoke.sizeOverLifetime;
            spread.enabled = true;
            spread.size = new ParticleSystem.MinMaxCurve(1f,
                new AnimationCurve(new Keyframe(0f, 0.8f), new Keyframe(0.12f, 1.7f), new Keyframe(0.5f, 2.7f), new Keyframe(1f, 3.6f)));
            var drift = _smoke.velocityOverLifetime;
            drift.enabled = true;
            drift.space = ParticleSystemSimulationSpace.World;
            drift.x = new ParticleSystem.MinMaxCurve(PB.Wind.x * 0.8f - 0.25f, PB.Wind.x * 0.8f + 0.25f);
            drift.y = new ParticleSystem.MinMaxCurve(0.25f, 0.6f);
            drift.z = new ParticleSystem.MinMaxCurve(PB.Wind.z * 0.8f - 0.25f, PB.Wind.z * 0.8f + 0.25f);
            // The exhaust leaves fast and is braked by the air within a fraction of a second.
            var brake = _smoke.limitVelocityOverLifetime;
            brake.enabled = true;
            brake.limit = 0.4f;
            brake.dampen = 0.12f;

            // A hotter copy of the fire material: a motor's flame burns brighter than a fire.
            if (_fire == null)
            {
                _fire = new Material(m.Fire) { name = "Motor Fire", hideFlags = HideFlags.DontSave };
                _fire.SetFloat("_Intensity", 2.5f);
            }
            _glow = Shared(root, "Motor Glow", m.Glow, 600, ParticleSystemRenderMode.Stretch);
            PB.Colors(_glow, Flat(0.6f));
            Stretch(_glow, GlowStretch);
            _cone = Shared(root, "Motor Flame", _fire, 2400, ParticleSystemRenderMode.Stretch);
            PB.Colors(_cone, Flat(1f));
            Stretch(_cone, ConeStretch);
            _tongue = Shared(root, "Motor Tongue", _fire, 900, ParticleSystemRenderMode.Stretch);
            PB.Colors(_tongue, Flat(1f));
            Stretch(_tongue, TongueStretch);
            _core = Shared(root, "Motor Core", _fire, 900, ParticleSystemRenderMode.Billboard);
            PB.Colors(_core, Flat(1f));
        }

        /// <summary>Most smoke puffs alive at once (a salvo of forty rockets fills it on Low).</summary>
        private static int SmokeBudget => MatchSettings.Tier switch
        {
            GraphicsQuality.Low => 2500,
            GraphicsQuality.Medium => 4000,
            _ => 6000,
        };

        /// <summary>
        /// Smoke puffs' spacing (times the plume's own) and how long a puff hangs, by tier (set once
        /// a frame by <see cref="Frame"/>): High the long lingering trail, Medium a little sparser,
        /// Low sparser and shorter-lived, still more smoke than the old trail (0.55 m apart, 0.85 s).
        /// </summary>
        public float SmokeSpacing { get; private set; } = 1f;

        private float _smokeLife = 3.2f * SmokeTimes.Trail * SmokeTimes.TrailLength;
        private int _segments = 4;
        private bool _glowOn = true;

        /// <summary>Reads the graphics tier once for the frame's motors and trails.</summary>
        public void Frame()
        {
            var tier = MatchSettings.Tier;
            SmokeSpacing = tier switch { GraphicsQuality.Low => 1.6f, GraphicsQuality.Medium => 1.25f, _ => 1f };
            // Play-test 14 session 5: the trail clears in half the time (SmokeTimes.Trail).
            // Play-test 14 (lane H): half as long again (SmokeTimes.TrailLength).
            _smokeLife = tier switch { GraphicsQuality.Low => 1.7f, GraphicsQuality.Medium => 2.5f, _ => 3.2f } * SmokeTimes.Trail * SmokeTimes.TrailLength;
            _segments = tier switch { GraphicsQuality.Low => 2, GraphicsQuality.Medium => 4, _ => 5 };
            _glowOn = tier != GraphicsQuality.Low;
        }

        /// <summary>
        /// One frame of a burning motor. <paramref name="nozzle"/> is the tail of the drawn munition,
        /// <paramref name="forward"/> its nose, <paramref name="velocity"/> its velocity (the flame
        /// flies with it), <paramref name="length"/> and <paramref name="width"/> the flame's size
        /// at cruise (metres), <paramref name="speed"/> the share of cruise speed it is flying at
        /// (slow off the rail, 1 at cruise) and <paramref name="dt"/> the frame's length.
        /// </summary>
        public void Burn(Vector3 nozzle, Vector3 forward, Vector3 velocity, float length, float width, float speed, float dt)
        {
            var life = Mathf.Clamp(dt * 2.4f, 0.05f, 0.12f);
            // Emitted one frame back: the particles fly with the missile and are moved on by this
            // frame's particle update before they are drawn (effects tick in Update).
            nozzle -= velocity * dt;
            speed = Mathf.Clamp01(speed);
            // Flicker: the flame's length and width change a little every frame.
            var total = length * Mathf.Lerp(0.55f, 1f, speed) * Random.Range(0.82f, 1.18f);
            // The boost burns fattest off the rail.
            var fat = Mathf.Lerp(1.3f, 1f, speed);
            var axis = -forward;
            var step = ConeStretch * Fill;
            var segments = Mathf.Clamp(Mathf.RoundToInt(total / (width * step)), 1, _segments);
            // Tapering quads end to end, each starting where the last one's fire fades: their
            // summed length is the flame's.
            var taper = 0f;
            for (var i = 0; i < segments; i++) taper += 1f - 0.45f * i / Mathf.Max(1, segments - 1);
            var baseWidth = Mathf.Clamp(total / (step * taper), width * 0.6f, width * 1.6f) * fat;
            // The first quad reaches forward over the nozzle by the end its fire leaves unfilled,
            // so the flame starts on the tail.
            var along = -baseWidth * ConeStretch * (1f - Fill) * 0.5f;
            for (var i = 0; i < segments; i++)
            {
                var k = segments > 1 ? i / (segments - 1f) : 0f;
                var w = baseWidth * (1f - 0.45f * k) * Random.Range(0.88f, 1.12f);
                var l = w * ConeStretch;
                var dir = (axis + Random.insideUnitSphere * 0.04f).normalized;
                var colour = Color.Lerp(new Color(1f, 0.7f, 0.3f), new Color(1f, 0.3f, 0.05f), k);
                colour.a = Mathf.Lerp(1f, 0.75f, k);
                Emit(_cone, nozzle + dir * (along + l * Head), velocity, w, life, colour);
                along += l * Fill;
            }
            // The hot tongue at the nozzle and a white core on it.
            var tongue = baseWidth * 0.7f * Random.Range(0.9f, 1.1f);
            Emit(_tongue, nozzle + axis * (tongue * TongueStretch * (Head - 0.1f)), velocity, tongue, life, new Color(1f, 0.86f, 0.52f));
            Emit(_core, nozzle + axis * (baseWidth * 0.1f), velocity, baseWidth * 0.8f * Random.Range(0.9f, 1.1f), life, new Color(1f, 0.9f, 0.62f));
            // A soft orange body under the whole flame for the bloom (skipped on Low).
            if (_glowOn)
            {
                var glow = Mathf.Max(baseWidth * 1.7f, total * 1.05f / GlowStretch);
                Emit(_glow, nozzle + axis * (glow * GlowStretch * (Head - 0.08f)), velocity, glow, life * 1.2f, new Color(1f, 0.5f, 0.16f, 0.9f));
            }
        }

        /// <summary>
        /// A puff of the motor's smoke at <paramref name="position"/>, <paramref name="size"/> across
        /// as it leaves the flame, thrown back along <paramref name="back"/>: it lingers, spreads and
        /// drifts off with the wind.
        /// </summary>
        public void Smoke(Vector3 position, Vector3 back, float size)
        {
            var life = _smokeLife * Random.Range(0.8f, 1.2f);
            // Play-test 14 (lane H): a quarter narrower (SmokeTimes.TrailWidth); the puffs keep their spacing.
            size *= SmokeTimes.TrailWidth;
            Emit(_smoke, position + Random.insideUnitSphere * (size * 0.12f), back * Random.Range(1f, 2.5f) + Random.insideUnitSphere * 0.35f,
                size * Random.Range(0.85f, 1.15f), life, Color.white, Random.Range(0f, 360f));
        }

        private static void Emit(ParticleSystem system, Vector3 position, Vector3 velocity, float size, float life, Color colour, float rotation = 0f)
        {
            system.Emit(new ParticleSystem.EmitParams
            {
                position = position,
                velocity = velocity,
                startSize = size,
                startLifetime = life,
                startColor = colour,
                rotation = rotation,
                applyShapeToPosition = false,
            }, 1);
        }

        /// <summary>White with the alpha held and then gone: the particle's own colour sets its hue.</summary>
        private static Gradient Flat(float alpha)
        {
            var g = new Gradient();
            g.SetKeys(new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                new[] { new GradientAlphaKey(alpha, 0f), new GradientAlphaKey(alpha * 0.85f, 0.6f), new GradientAlphaKey(0f, 1f) });
            return g;
        }

        /// <summary>
        /// Rocket smoke: warm and bright where it leaves the flame, then pale grey, thick at first
        /// and thinning out as it spreads.
        /// </summary>
        private static Gradient Smoke()
        {
            var g = new Gradient();
            g.SetKeys(
                new[]
                {
                    new GradientColorKey(new Color(1f, 0.88f, 0.72f), 0f), new GradientColorKey(new Color(0.9f, 0.89f, 0.87f), 0.1f),
                    new GradientColorKey(new Color(0.8f, 0.8f, 0.8f), 1f),
                },
                new[]
                {
                    new GradientAlphaKey(0f, 0f), new GradientAlphaKey(0.7f, 0.04f), new GradientAlphaKey(0.45f, 0.35f),
                    new GradientAlphaKey(0f, 1f),
                });
            return g;
        }

        private static void Stretch(ParticleSystem ps, float length)
        {
            var renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.velocityScale = 0f;
            renderer.lengthScale = length;
        }

        private static ParticleSystem Shared(Transform parent, string name, Material material, int max, ParticleSystemRenderMode mode)
        {
            var ps = PB.Create(parent, name, material, mode);
            var main = ps.main;
            main.loop = true;
            main.maxParticles = max;
            main.startRotation = 0f;
            var emission = ps.emission;
            emission.enabled = false;
            ps.Play();
            return ps;
        }
    }
}
