using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// A burning vehicle's fire. Play-test 8 (DECISIONS 22R) drew it a third time, after the burning tanks of War
    /// Thunder, World of Tanks and Company of Heroes and after footage of real vehicle fires (diesel and hydraulic oil:
    /// a low bed of flame over the engine grilles, white-yellow at the grille, orange in the body, dark red tips that
    /// tear straight into thick black smoke; flames that flicker ten times a second and shed licks off their tops; the
    /// hull and the ground round it lit orange; embers climbing and sparks spitting). Play-test 6's fire (DECISIONS 21H)
    /// read as a few separate candle flames under a blot of smoke.
    /// <list type="bullet">
    /// <item>The flames: at each source a bed of short-lived tongues side by side, tallest in the middle, so they merge
    /// into one ragged sheet of fire; each tongue cools as it rises (the flame material's heat falls with age: yellow-white
    /// at the root, orange, red at the tip), over a white-hot root pinned low in the opening, with flame licks breaking off
    /// the tips. Everything carries the hull's velocity (the fire rides the vehicle), the flames a little less so they
    /// lean back when it drives.</item>
    /// <item>The heat: a warm light on the hull and the ground round the fire (<see cref="HeatLights"/>, drawn by the
    /// Lit shader; up to four fires at once, two on Low), flickering, plus a soft glow in the air over the opening.</item>
    /// <item>The smoke: out of the flame tips, lit brown-orange from below at first, then black, greying as it climbs and
    /// spreads downwind; spread along the path the hull covered in the beat, so a vehicle on the move trails one plume
    /// instead of a row of puffs.</item>
    /// <item>Embers wander up, sparks spit out and fall, and now and then the fire flares up (a burst of taller flames,
    /// a pop of light, a shower of sparks and a gout of smoke).</item>
    /// </list>
    /// It burns in three stages by the damage (<see cref="Stage"/>): catching (30 to 20 % health: the engine deck, a
    /// low bed, grey-black smoke), burning (20 to 11 %: the deck and the turret's hatch, black smoke, embers, the hull
    /// lit) and ablaze (below 11 %: a breach in the flank too, tall flames, a heavy black column, frequent flare-ups, a
    /// wide light); within a stage it keeps growing (<see cref="Severity"/>). Bosses burn the same way at their broken
    /// parts (<see cref="FeedPoint"/>, EffectsDirector.BossParts). No heat shimmer: a refraction pass needs the camera's
    /// opaque texture, which the phone renderer leaves off. Low: at most two sources, a slower beat, fewer tongues and
    /// licks, half the sparks and embers, smoke every other beat, smaller flare-ups, two lights.
    /// </summary>
    internal sealed class HullFire
    {
        /// <summary>Below this share of its health a vehicle burns (it smokes from 60 %; EffectsDirector.ShowDamage).</summary>
        public const float Burning = 0.3f;

        /// <summary>How often a burning vehicle's fire is fed, in seconds, on High and Medium, and on Low.</summary>
        public const float Beat = 0.08f, LowBeat = 0.12f;

        /// <summary>How much of the hull's velocity its embers and smoke keep (the smoke streams out behind) and its flames (they lean back a little).</summary>
        public const float EmberCarry = 0.6f, SmokeCarry = 0.25f, FlameCarry = 0.93f;

        private readonly ParticleSystem _root, _halo, _tongues, _licks, _sparks, _embers, _smoke;

        /// <summary>The sources in the hull's own frame: (across, along) in hull radii, height in its top, spread in radii; the engine deck first.</summary>
        private static readonly (Vector2 at, float height, float spread)[] Sources =
        {
            (new Vector2(0.1f, -0.55f), 0.56f, 0.46f), // the engine deck, a wide grille
            (new Vector2(-0.12f, 0.05f), 0.92f, 0.2f), // the turret's hatch
            (new Vector2(0.62f, 0.2f), 0.42f, 0.24f), // a breach in the flank
        };

        /// <summary>What each stage looks like (index <see cref="Stage"/> - 1).</summary>
        private static readonly StageLook[] Looks =
        {
            // Catching: a low bed on the deck, grey-black smoke, a faint light.
            new(bodies: 1, tongues: 1, lowTongues: 1, size: 1f, smokeShade: 0.34f, smokeAlpha: 0.6f, smokeSize: 1f, embers: 0.5f, sparks: 0.25f,
                reach: 4.5f, power: 2.8f),
            // Burning: the deck and the hatch, black smoke, embers, the hull lit.
            new(bodies: 1, tongues: 2, lowTongues: 1, size: 1.2f, smokeShade: 0.16f, smokeAlpha: 0.74f, smokeSize: 1.15f, embers: 1.1f, sparks: 0.7f,
                reach: 6f, power: 4f),
            // Ablaze: three sources, tall flames, a heavy black column, a wide light.
            new(bodies: 2, tongues: 2, lowTongues: 2, size: 1.45f, smokeShade: 0.06f, smokeAlpha: 0.8f, smokeSize: 1.35f, embers: 1.8f, sparks: 1.2f,
                reach: 7.5f, power: 5.2f),
        };

        private readonly struct StageLook
        {
            public readonly int Bodies, Tongues, LowTongues;
            public readonly float Size, SmokeShade, SmokeAlpha, SmokeSize, Embers, Sparks, Reach, Power;

            public StageLook(int bodies, int tongues, int lowTongues, float size, float smokeShade, float smokeAlpha, float smokeSize, float embers,
                float sparks, float reach, float power)
            {
                Bodies = bodies;
                Tongues = tongues;
                LowTongues = lowTongues;
                Size = size;
                SmokeShade = smokeShade;
                SmokeAlpha = smokeAlpha;
                SmokeSize = smokeSize;
                Embers = embers;
                Sparks = sparks;
                Reach = reach;
                Power = power;
            }
        }

        public HullFire(MaterialLibrary m, Transform parent)
        {
            var root = new GameObject("Hull Fires").transform;
            root.SetParent(parent, false);
            var fx = FxMaterials.Shared;
            // The root of the fire: a white-hot core pinned low in the opening, wide and flat.
            _root = Continuous(root, "Hull Fire Root", m.Flash, 400,
                PB.Fade(new Color(1f, 0.94f, 0.74f), new Color(1f, 0.72f, 0.3f), new Color(1f, 0.42f, 0.1f)), 0.9f, 1.05f);
            var core = _root.main;
            core.startSize3D = true;
            // The glow in the air over the opening: big, soft and faint, orange.
            _halo = Continuous(root, "Hull Fire Glow", m.Flash, 400,
                PB.Fade(new Color(1f, 0.62f, 0.26f), new Color(1f, 0.46f, 0.14f), new Color(0.7f, 0.2f, 0.05f)), 0.9f, 1.1f);
            // The flames: narrow looping fire sheets pinned at their base, cooling as they rise (yellow-white, orange,
            // red), nearly opaque at the root, with less of the sheet's own sooty fringe (the smoke is drawn apart).
            var hot = new Material(fx.Flames) { name = "Hull Flames", hideFlags = HideFlags.DontSave };
            hot.SetColor("_FireHot", new Color(1f, 0.95f, 0.78f));
            hot.SetColor("_FireMid", new Color(1f, 0.52f, 0.12f));
            hot.SetColor("_FireDeep", new Color(0.62f, 0.09f, 0.015f));
            hot.SetFloat("_FireIntensity", 4.6f);
            hot.SetFloat("_HeatScale", 1.2f);
            hot.SetFloat("_HeatCool", 0.5f);
            hot.SetFloat("_FireOpacity", 0.72f);
            hot.SetFloat("_Density", 0.75f);
            _tongues = Continuous(root, "Hull Fire Tongues", hot, 1400,
                PB.Hold(new Color(0.3f, 0.26f, 0.22f), new Color(0.2f, 0.18f, 0.16f), 0.05f, 0.6f), 0.75f, 1.05f);
            PB.Flipbook(_tongues, loop: true, cycles: 1f, tilt: 5f, pivotY: 0.34f);
            var tongues = _tongues.main;
            tongues.startSize3D = true;
            // Licks: flame-shaped scraps breaking off the tips and vanishing as they rise.
            _licks = Continuous(root, "Hull Fire Flicker", m.Fire, 600,
                PB.Fade(new Color(1f, 0.82f, 0.45f), new Color(1f, 0.5f, 0.14f), new Color(0.75f, 0.16f, 0.03f)), 1f, 0.45f);
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
            // The smoke: lit brown-orange by the flames under it, then black, greying as it climbs and spreads downwind.
            _smoke = Continuous(root, "Hull Fire Smoke", fx.Smoke, 1800, SmokeRamp(), 0.5f, 2.7f);
            PB.Flipbook(_smoke, loop: false, tilt: 22f, to: 0.85f);
            PB.Rise(_smoke, 1.4f, 2.6f);
        }

        /// <summary>The smoke's colour over its life: fire-lit brown at the flame tips, soot black, then grey haze.</summary>
        private static Gradient SmokeRamp()
        {
            var g = new Gradient();
            g.SetKeys(
                new[]
                {
                    new GradientColorKey(new Color(0.46f, 0.27f, 0.15f), 0f), new GradientColorKey(new Color(0.11f, 0.1f, 0.095f), 0.16f),
                    new GradientColorKey(new Color(0.42f, 0.41f, 0.4f), 1f),
                },
                new[] { new GradientAlphaKey(0f, 0f), new GradientAlphaKey(0.92f, 0.06f), new GradientAlphaKey(0.92f, 0.52f), new GradientAlphaKey(0f, 1f) });
            return g;
        }

        /// <summary>How hard a vehicle at <paramref name="health"/> burns: 0 just under <see cref="Burning"/>, 1 near death.</summary>
        public static float Severity(float health) => Mathf.Clamp01(Mathf.InverseLerp(Burning, 0.03f, health));

        /// <summary>The stage a fire of <paramref name="severity"/> burns at: 1 catching, 2 burning, 3 ablaze.</summary>
        public static int Stage(float severity) => severity < 0.34f ? 1 : severity < 0.68f ? 2 : 3;

        /// <summary>How many sources burn at <paramref name="severity"/>: one a stage (at most two on Low).</summary>
        public static int PointsAt(float severity, bool low)
        {
            var n = Stage(severity);
            return low ? Mathf.Min(2, n) : n;
        }

        /// <summary>Tongues of flame a source puts out each beat at <paramref name="severity"/> on a tier (its bodies come every other beat).</summary>
        public static int TonguesAt(float severity, bool low)
        {
            var look = Looks[Stage(severity) - 1];
            return low ? look.LowTongues : look.Tongues;
        }

        /// <summary>Bodies of flame (the wide sheets the tongues rise out of) a source puts out every other beat at <paramref name="severity"/>.</summary>
        public static int BodiesAt(float severity) => Looks[Stage(severity) - 1].Bodies;

        /// <summary>How big a source's flames are at <paramref name="severity"/>, in hull radii times its share (by stage, growing within it).</summary>
        public static float FlameSize(float severity) => Looks[Stage(severity) - 1].Size * Mathf.Lerp(0.9f, 1.15f, severity);

        /// <summary>How far the fire's light reaches on the hull and the ground at <paramref name="severity"/>, in metres.</summary>
        public static float LightReach(float severity) => Looks[Stage(severity) - 1].Reach * Mathf.Lerp(1f, 1.15f, severity);

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
        /// The fire's light on a burning vehicle this frame (EffectsDirector, every frame, so it rides the hull smoothly):
        /// over the engine deck, flickering.
        /// </summary>
        public static void Light(VehicleView view, float health, float time)
        {
            if (view.Root == null) return;
            Light(view.Root, view.Sim.Radius, view.Top, view.Flying, view.Id.GetHashCode(), health, time);
        }

        /// <summary>The fire's light on a hull at <paramref name="root"/> (see <see cref="Light(VehicleView, float, float)"/>).</summary>
        public static void Light(Transform root, float radius, float top, bool flying, int seed, float health, float time)
        {
            var s = Severity(health);
            var look = Looks[Stage(s) - 1];
            radius = Mathf.Max(0.8f, radius);
            var height = Mathf.Min(top, 2.8f);
            var (p, h, _) = Sources[0];
            var flip = (seed & 1) == 0 ? 1f : -1f;
            // Over the deck, a little above it, so the light falls on the hull's top and on the ground beside it.
            var at = root.position + Vector3.up * (flying ? 0.3f : height * h + 0.5f) + root.right * (p.x * flip * radius) +
                     root.forward * (p.y * radius);
            var scale = Mathf.Clamp(radius / 2.2f, 0.8f, 2f);
            HeatLights.Add(at, LightReach(s) * scale, look.Power * Mathf.Lerp(0.9f, 1.15f, s), seed, time);
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
            var look = Looks[Stage(s) - 1];
            for (var k = 0; k < points; k++)
            {
                var (p, h, spread) = Sources[k];
                Vector3 at, across, along;
                if (k == 1 && turret != null)
                {
                    // Out of the turret's hatch: it turns with the turret.
                    at = turret.position + turret.right * (p.x * flip * radius * 0.6f) - turret.forward * (0.15f * radius);
                    at.y = root.position.y + height * h;
                    across = turret.right;
                    along = turret.forward;
                }
                else
                {
                    at = root.position + Vector3.up * (flying ? 0.2f : height * h) + root.right * (p.x * flip * radius) +
                         root.forward * (p.y * radius);
                    across = root.right;
                    along = root.forward;
                }
                // A breach in the flank licks out sideways as well as up.
                var up = k == 2 ? (Vector3.up + root.right * (flip * 0.45f)).normalized : Vector3.up;
                // The first source is the biggest; the others join smaller; all grow with the damage, by stage and within it.
                var size = radius * (k == 0 ? 0.5f : 0.4f) * FlameSize(s);
                // The fire covers the opening both ways (a deck is about as long as it is wide), so it reads from any side.
                Source(at, across * (spread * radius), along * (spread * radius * 0.6f), up, size, s, look, velocity * carry, low, beat + k,
                    k == 0);
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
            var s = Mathf.Clamp01(severity);
            var along = Vector3.Cross(across, Vector3.up);
            Source(point, across * size * 0.6f, along * size * 0.4f, Vector3.up, size * 1.2f, s, Looks[Stage(s) - 1], velocity, low, beat, true);
        }

        /// <summary>
        /// One source's beat: root and glow, the fire's wide bodies and the tongues rising out of them, licks, sparks,
        /// embers, smoke, and now and then a flare-up.
        /// </summary>
        private void Source(Vector3 at, Vector3 across, Vector3 along, Vector3 up, float size, float s, in StageLook look, Vector3 velocity,
            bool low, int beat, bool main)
        {
            var flame = velocity * FlameCarry;
            Root(at + up * size * 0.08f, across, size, Random.Range(0.55f, 0.95f), velocity);
            if (main && beat % 2 == 0) Halo(at + up * size * 0.5f, size * Random.Range(2f, 2.4f), Mathf.Lerp(0.14f, 0.24f, s), velocity);
            // The bodies: wide sheets of fire over the opening (the flipbook's own shape: a broad burning base breaking
            // into flames), every other beat, overlapping into one mass.
            if (beat % 2 == 0)
                for (var i = 0; i < look.Bodies; i++)
                    Body(at + across * Random.Range(-0.6f, 0.6f) + along * Random.Range(-0.6f, 0.6f), up, size, flame);
            // The tongues: taller, narrower flames out of the middle of the fire, tallest in the middle.
            var n = low ? look.LowTongues : look.Tongues;
            for (var i = 0; i < n; i++)
            {
                var u = Random.Range(-0.75f, 0.75f);
                var tall = Mathf.Lerp(1.2f, 0.8f, Mathf.Abs(u)) * Random.Range(0.85f, 1.2f);
                Tongue(at + across * u + along * Random.Range(-0.5f, 0.5f), up, size, tall, flame);
            }
            if (!low || beat % 2 == 0)
                Lick(at + across * Random.Range(-0.7f, 0.7f) + up * size * Random.Range(0.8f, 1.3f), size, flame);
            var sparks = Mathf.RoundToInt(look.Sparks * (low ? 0.5f : 1f) + Random.value * 0.5f);
            for (var i = 0; i < sparks; i++) Spark(at + up * size * 0.3f, up, velocity, 1f);
            var embers = Mathf.RoundToInt(look.Embers * (low ? 0.5f : 1f) + Random.value * 0.5f);
            for (var i = 0; i < embers; i++) Ember(at + up * size * 0.6f, s, velocity);
            if (!low || beat % 2 == 0) Smoke(at + up * size * 1.3f, size, s, look, velocity, low);
            if (Random.value < FlareChance(s, low)) FlareUp(at, across, up, size, s, look, velocity, low);
        }

        /// <summary>A flare-up: a burst of taller flames, a pop of light, a shower of sparks and a gout of black smoke.</summary>
        private void FlareUp(Vector3 at, Vector3 across, Vector3 up, float size, float s, in StageLook look, Vector3 velocity, bool low)
        {
            var big = size * (low ? 1.3f : 1.6f);
            Halo(at + up * size * 0.5f, big * 2.2f, 0.7f, velocity);
            Root(at + up * size * 0.1f, across, big, 1f, velocity);
            Body(at, up, big, velocity * FlameCarry);
            for (var i = 0; i < (low ? 2 : 4); i++) Tongue(at + across * Random.Range(-1f, 1f), up, big, Random.Range(1f, 1.3f), velocity * FlameCarry);
            for (var i = 0; i < (low ? 5 : 12); i++) Spark(at + up * size * 0.4f, up, velocity, 1.6f);
            for (var i = 0; i < (low ? 1 : 2); i++) Smoke(at + up * size * 1.3f, big, Mathf.Max(s, 0.8f), look, velocity, low);
        }

        private void Root(Vector3 at, Vector3 across, float size, float alpha, Vector3 velocity)
        {
            var wide = Mathf.Max(size * 1.1f, across.magnitude * 1.4f);
            _root.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = velocity, startSize3D = new Vector3(wide * Random.Range(0.9f, 1.1f), size * Random.Range(0.5f, 0.65f), 1f),
                startColor = new Color(1f, 1f, 1f, alpha), startLifetime = Random.Range(0.1f, 0.16f), rotation = Random.Range(-4f, 4f),
                applyShapeToPosition = false,
            }, 1);
        }

        private void Halo(Vector3 at, float size, float alpha, Vector3 velocity)
        {
            _halo.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = velocity, startSize = size, startColor = new Color(1f, 0.8f, 0.55f, alpha),
                startLifetime = Random.Range(0.14f, 0.22f), applyShapeToPosition = false,
            }, 1);
        }

        private void Body(Vector3 at, Vector3 up, float size, Vector3 velocity)
        {
            var width = size * Random.Range(1.5f, 1.9f);
            _tongues.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = velocity + up * Random.Range(0.15f, 0.35f) + Random.insideUnitSphere * 0.05f,
                startSize3D = new Vector3(width, width * Random.Range(0.85f, 1f), 1f), startLifetime = Random.Range(0.55f, 0.8f),
                rotation = Random.Range(-4f, 4f), applyShapeToPosition = false,
            }, 1);
        }

        private void Tongue(Vector3 at, Vector3 up, float size, float tall, Vector3 velocity)
        {
            var width = size * Random.Range(0.8f, 1.05f);
            _tongues.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = velocity + up * Random.Range(0.3f, 0.7f) + Random.insideUnitSphere * 0.08f,
                startSize3D = new Vector3(width, size * 1.45f * tall, 1f), startLifetime = Random.Range(0.36f, 0.55f),
                rotation = Random.Range(-6f, 6f), applyShapeToPosition = false,
            }, 1);
        }

        private void Lick(Vector3 at, float size, Vector3 velocity)
        {
            _licks.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = velocity + Vector3.up * Random.Range(1.5f, 2.8f) + Random.insideUnitSphere * 0.35f,
                startSize = size * Random.Range(0.35f, 0.55f), startLifetime = Random.Range(0.14f, 0.26f),
                rotation = Random.Range(-8f, 8f), applyShapeToPosition = false,
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

        private void Smoke(Vector3 at, float size, float severity, in StageLook look, Vector3 velocity, bool low)
        {
            // Spread along the path the source covered since the last puff, so a moving vehicle trails one plume.
            var gap = velocity * (Random.value * (low ? LowBeat * 2f : Beat));
            var shade = look.SmokeShade * 3f + 0.35f;
            _smoke.Emit(new ParticleSystem.EmitParams
            {
                position = at - gap + Random.insideUnitSphere * size * 0.15f,
                velocity = velocity * SmokeCarry + Vector3.up * Random.Range(0.7f, 1.2f) + Random.insideUnitSphere * 0.25f,
                startSize = size * Random.Range(0.95f, 1.25f) * look.SmokeSize,
                startLifetime = Random.Range(2.4f, 3.6f) * Mathf.Lerp(0.95f, 1.25f, severity) * SmokeTimes.Fire,
                startColor = new Color(shade, shade, shade, look.SmokeAlpha),
                rotation = Random.Range(0f, 360f), applyShapeToPosition = false,
            }, 1);
        }

        private ParticleSystem[] All => new[] { _root, _halo, _tongues, _licks, _sparks, _embers, _smoke };

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
