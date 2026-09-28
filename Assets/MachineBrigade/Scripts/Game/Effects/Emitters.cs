using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Shared world-space particle systems that effects emit into on demand: shell smoke trails,
    /// rocket motors, flame jets and tread dust. One system per kind keeps the cost to a few draw calls no
    /// matter how many vehicles are firing or driving. A flamethrower's stream is a rod of burning
    /// fuel wrapped in heat glow, with rolling balls of fire (the explosion flipbook's burning
    /// frames, napalm-coloured) that swell as they fly, splash onto the target and roll up into
    /// black smoke; flames lick up the target and the ground round it (DECISIONS 11A).
    /// </summary>
    internal sealed class Emitters
    {
        private readonly ParticleSystem _trail;
        private readonly ParticleSystem _contrail;
        private readonly ParticleSystem _dust;
        private readonly ParticleSystem _motor;
        private readonly ParticleSystem _flame;
        private readonly ParticleSystem _flameCore;
        private readonly ParticleSystem _flameBalls;
        private readonly ParticleSystem _flameGlow;
        private readonly ParticleSystem _flamePool;
        private readonly ParticleSystem _flameEmbers;
        private readonly ParticleSystem _charge;

        /// <summary>A flamethrower's stream, fed until the next pull of the trigger.</summary>
        private sealed class FlameStream
        {
            public Vector3 From, To;
            public float Travel, Until, RodDebt, BallDebt, SmokeDebt, GlowDebt;
        }

        private readonly System.Collections.Generic.List<FlameStream> _streams = new();
        private readonly ParticleSystem _flak;
        private readonly ParticleSystem _repair;
        private readonly ParticleSystem _damageSmoke;
        private readonly ParticleSystem _damageFire;

        public Emitters(MaterialLibrary m, Transform parent)
        {
            _trail = Continuous(parent, "Shell Trails", m.Smoke, 3000, PB.SmokeGradient(0.8f, 0.3f), 0.7f, 2.6f);
            _motor = Continuous(parent, "Rocket Motors", m.Fire, 400, PB.FireGradient, 1f, 0.2f);
            // Jets' vapour: thin white trails that spread and fade behind the engines and wingtips.
            _contrail = Continuous(parent, "Contrails", m.Smoke, 1600,
                PB.Fade(new Color(0.97f, 0.98f, 1f), new Color(0.94f, 0.96f, 0.99f), new Color(0.9f, 0.92f, 0.96f), 0.5f), 0.45f, 2.4f);
            // Flames licking up where the stream lands, on the target and the ground by it: the fire
            // sheet's upright flames standing on their base. Never spun: a flame turned on its side
            // or upside down read as an orange petal.
            _flame = Continuous(parent, "Flame Licks", FxMaterials.Shared.Napalm, 1200,
                PB.Hold(new Color(0.42f, 0.36f, 0.3f), new Color(0.3f, 0.26f, 0.22f), 0.08f, 0.7f), 0.8f, 1.15f);
            PB.Flipbook(_flame, loop: true, tilt: 8f, pivotY: 0.3f);
            // Rolling balls of burning fuel down the stream: small at the nozzle, swelling as they
            // fly, splashing onto the target and rolling up off it into black smoke.
            _flameBalls = PB.Create(parent, "Flame Balls", FxMaterials.Shared.FlameBall);
            var balls = _flameBalls.main;
            balls.loop = true;
            balls.maxParticles = 1500;
            var ballEmission = _flameBalls.emission;
            ballEmission.enabled = false;
            PB.Flipbook(_flameBalls, loop: false, tilt: 20f, from: 0.02f, to: 0.38f);
            PB.Colors(_flameBalls, PB.Hold(new Color(0.4f, 0.34f, 0.3f), new Color(0.22f, 0.2f, 0.19f), 0.04f, 0.78f));
            var swell = _flameBalls.sizeOverLifetime;
            swell.enabled = true;
            swell.size = new ParticleSystem.MinMaxCurve(1f, new AnimationCurve(new Keyframe(0f, 0.3f), new Keyframe(0.5f, 1f), new Keyframe(1f, 1.45f)));
            Splash(_flameBalls);
            _flameBalls.Play();
            // The rod of fuel itself: thick burning streaks along the stream, spreading as they go
            // and falling a little in an arc; orange, not white (a white rod read as a laser).
            _flameCore = PB.Create(parent, "Flame Rod", m.Fire, ParticleSystemRenderMode.Stretch);
            var core = _flameCore.main;
            core.loop = true;
            core.maxParticles = 2400;
            core.gravityModifier = FlameGravity;
            var rod = _flameCore.GetComponent<ParticleSystemRenderer>();
            rod.velocityScale = 0.05f;
            rod.lengthScale = 2.2f;
            var coreEmission = _flameCore.emission;
            coreEmission.enabled = false;
            PB.Colors(_flameCore, PB.Fade(new Color(2.2f, 1.25f, 0.45f), new Color(2f, 0.7f, 0.12f), new Color(1.1f, 0.22f, 0.03f), 0.9f));
            PB.Grow(_flameCore, 0.45f, 2.2f);
            _flameCore.Play();
            // Heat round the stream: a soft orange halo for the bloom to spread (additive, over the smoke).
            var heat = new Material(m.Glow) { name = "Flame Heat", renderQueue = 3010, hideFlags = HideFlags.DontSave };
            _flameGlow = Continuous(parent, "Flame Heat", heat, 600,
                PB.Fade(new Color(1f, 0.5f, 0.15f), new Color(1f, 0.38f, 0.08f), new Color(0.7f, 0.15f, 0.03f), 0.32f), 0.6f, 1.4f);
            // The ground lit orange where the fire lands.
            _flamePool = PB.Create(parent, "Flame Light", m.Glow, ParticleSystemRenderMode.HorizontalBillboard);
            var pool = _flamePool.main;
            pool.loop = true;
            pool.maxParticles = 200;
            var poolEmission = _flamePool.emission;
            poolEmission.enabled = false;
            PB.Colors(_flamePool, PB.Fade(new Color(1f, 0.55f, 0.2f), new Color(1f, 0.42f, 0.12f), new Color(0.6f, 0.18f, 0.04f), 0.55f));
            PB.Grow(_flamePool, 0.9f, 1.05f);
            _flamePool.Play();
            // Embers thrown up off the burning target.
            _flameEmbers = Continuous(parent, "Flame Embers", m.Sparks, 600,
                PB.Fade(new Color(1f, 0.8f, 0.4f), new Color(1f, 0.5f, 0.15f), new Color(0.6f, 0.15f, 0.05f)), 1f, 0.4f);
            var embers = _flameEmbers.main;
            embers.gravityModifier = -0.1f;
            var drift = _flameEmbers.noise;
            drift.enabled = true;
            drift.strength = 0.8f;
            drift.frequency = 0.6f;
            // A railgun's coils glowing up before the shot: pale blue-white points of light.
            // (The spark material: a flat additive glow, never faded where it meets the model.)
            _charge = Continuous(parent, "Rail Charge", m.Sparks, 300,
                PB.Fade(new Color(0.75f, 0.95f, 1f), new Color(0.6f, 0.85f, 1f), new Color(0.4f, 0.6f, 1f)), 1f, 0.4f);
            _flak = Continuous(parent, "Flak Bursts", m.Smoke, 200, PB.Plume(0.08f, 0.3f, 0.8f), 0.6f, 1.8f);
            _repair = Continuous(parent, "Repair", m.Sparks, 200,
                PB.Fade(new Color(0.5f, 1.6f, 0.8f), new Color(0.3f, 1.2f, 0.6f), new Color(0.2f, 0.8f, 0.4f)), 1f, 0.3f);
            // A damaged vehicle's smoke: billows off the engine deck, grey while it is only hurt,
            // black and thick once it is burning (the particle colour sets how dark).
            _damageSmoke = Continuous(parent, "Damage Smoke", FxMaterials.Shared.Smoke, 1200,
                PB.Hold(Color.white, new Color(0.85f, 0.85f, 0.85f), 0.12f, 0.5f, 0.85f), 0.6f, 2.2f);
            PB.Flipbook(_damageSmoke, loop: false, tilt: 25f);
            PB.Rise(_damageSmoke, 1.2f, 2.4f);
            // Flames licking out of a badly damaged hull.
            _damageFire = Continuous(parent, "Damage Fire", FxMaterials.Shared.Flames, 600,
                PB.Hold(new Color(0.3f, 0.27f, 0.24f), new Color(0.26f, 0.24f, 0.22f), 0.1f, 0.6f), 0.7f, 1.2f);
            PB.Flipbook(_damageFire, loop: true, tilt: 10f, pivotY: -0.1f);
            _dust = Continuous(parent, "Tread Dust", m.Smoke, 1500,
                PB.Fade(new Color(0.62f, 0.56f, 0.44f), new Color(0.58f, 0.53f, 0.42f), new Color(0.55f, 0.5f, 0.4f), 0.45f), 0.8f, 2.4f);
        }

        public void Trail(Vector3 position, float size)
        {
            Emit(_trail, position, Random.insideUnitSphere * 0.2f + Vector3.up * 0.25f, size * Random.Range(0.7f, 1.2f),
                Random.Range(0.6f, 1.1f));
        }

        /// <summary>A puff of a jet's vapour trail (engine or wingtip), lingering <paramref name="life"/> seconds.</summary>
        public void Contrail(Vector3 position, float size, float life)
        {
            Emit(_contrail, position, Random.insideUnitSphere * 0.15f, size * Random.Range(0.85f, 1.15f), life * Random.Range(0.85f, 1.1f));
        }

        /// <summary>A jet engine's hot exhaust: a short tongue of flame out of the nozzle.</summary>
        public void Afterburner(Vector3 position, Vector3 forward, float scale)
        {
            Emit(_motor, position, -forward * 7f + Random.insideUnitSphere * 0.3f, Random.Range(0.35f, 0.55f) * scale, Random.Range(0.05f, 0.09f));
        }

        /// <summary>The burning motor behind a flying missile or rocket.</summary>
        public void Motor(Vector3 position, Vector3 forward, float scale)
        {
            Emit(_motor, position, -forward * 3f + Random.insideUnitSphere * 0.5f, Random.Range(0.5f, 0.9f) * Mathf.Max(0.6f, scale),
                Random.Range(0.08f, 0.16f));
        }

        /// <summary>How much of gravity pulls the burning fuel down: the stream arcs a little on its way.</summary>
        private const float FlameGravity = 0.5f;

        /// <summary>Particles a second in a flame stream: the bright rod, the balls of fire rolling along it, black smoke, heat glow.</summary>
        private const float RodRate = 90f, BallRate = 42f, SmokeRate = 10f, GlowRate = 24f;

        /// <summary>
        /// A ball of fire flies at the stream's speed until it reaches the target, about half way
        /// through its life (its life is 1.8 to 2.2 flights), then brakes hard and billows up and
        /// off with the wind: fire splashing onto the target instead of flying through it.
        /// </summary>
        private static void Splash(ParticleSystem ps)
        {
            var limit = ps.limitVelocityOverLifetime;
            limit.enabled = true;
            limit.limit = new ParticleSystem.MinMaxCurve(1f,
                new AnimationCurve(new Keyframe(0f, 80f), new Keyframe(0.47f, 80f), new Keyframe(0.56f, 2.5f), new Keyframe(1f, 2.5f)));
            limit.dampen = 0.35f;
            var rise = new AnimationCurve(new Keyframe(0f, 0f), new Keyframe(0.5f, 0f), new Keyframe(1f, 1f));
            var vol = ps.velocityOverLifetime;
            vol.enabled = true;
            vol.space = ParticleSystemSimulationSpace.World;
            vol.x = new ParticleSystem.MinMaxCurve(PB.Wind.x, rise);
            vol.y = new ParticleSystem.MinMaxCurve(2.6f, rise);
            vol.z = new ParticleSystem.MinMaxCurve(PB.Wind.z, rise);
        }

        /// <summary>
        /// One pull of a flamethrower's trigger: the stream from <paramref name="from"/> to
        /// <paramref name="to"/>, flying <paramref name="seconds"/>, fed from the nozzle for the
        /// <paramref name="gap"/> seconds until the next pull so it reads as one unbroken jet
        /// (see <see cref="Tick"/>). A bright rod of fuel arcs onto the target (thrown a little
        /// high so it falls onto it), balls of fire roll along it and swell, fire splashes where
        /// it lands and black smoke rises off the burning stream.
        /// </summary>
        public void FlameJet(Vector3 from, Vector3 to, float seconds, float gap, float now)
        {
            var travel = Mathf.Max(0.12f, seconds);
            // The same flamethrower pulling again takes over its stream.
            FlameStream stream = null;
            foreach (var s in _streams)
                if ((s.From - from).sqrMagnitude < 4f) stream = s;
            if (stream == null) _streams.Add(stream = new FlameStream());
            stream.From = from;
            stream.To = to;
            stream.Travel = travel;
            // Fed a little past the next pull, so one pull runs into the next without a gap.
            stream.Until = now + gap * 1.6f;
            // Where it lands: flames licking up the target and off the ground round it, the ground
            // lit orange and embers thrown up (EffectsDirector also leaves the ground burning).
            for (var i = 0; i < 2; i++)
                Emit(_flame, to + Random.insideUnitSphere * 0.5f - Vector3.up * 0.4f, Vector3.up * Random.Range(0.3f, 0.9f) + Random.insideUnitSphere * 0.4f,
                    Random.Range(2f, 2.8f), Random.Range(0.55f, 0.85f), Random.Range(-8f, 8f));
            var disc = Random.insideUnitCircle * 1.6f;
            Emit(_flame, new Vector3(to.x + disc.x, 0.05f, to.z + disc.y), Vector3.up * 0.2f, Random.Range(1.4f, 2.1f), Random.Range(0.6f, 0.9f),
                Random.Range(-6f, 6f));
            _flamePool.Emit(new ParticleSystem.EmitParams
            {
                position = new Vector3(to.x, 0.08f, to.z), startSize = Random.Range(5f, 6.5f), startLifetime = 0.45f,
                rotation = Random.Range(0f, 360f), applyShapeToPosition = false,
            }, 1);
            var embers = Mathf.RoundToInt(4f * ExplosionEffect.Density);
            for (var i = 0; i < embers; i++)
                Emit(_flameEmbers, to + Random.insideUnitSphere * 0.6f, new Vector3(Random.Range(-1.5f, 1.5f), Random.Range(2f, 5f), Random.Range(-1.5f, 1.5f)),
                    Random.Range(0.08f, 0.15f), Random.Range(0.8f, 1.4f));
        }

        /// <summary>One point of a railgun's charge glow, <paramref name="size"/> across.</summary>
        public void Charge(Vector3 position, float size) =>
            Emit(_charge, position + Random.insideUnitSphere * 0.05f, Vector3.zero, size * Random.Range(0.8f, 1.2f), 0.12f);

        /// <summary>Per frame: feeds the flame streams from their nozzles.</summary>
        public void Tick(float now, float dt)
        {
            if (_streams.Count == 0) return;
            var fall = Physics.gravity * FlameGravity;
            var density = ExplosionEffect.Density;
            for (var k = _streams.Count - 1; k >= 0; k--)
            {
                var s = _streams[k];
                if (now > s.Until)
                {
                    _streams.RemoveAt(k);
                    continue;
                }
                var launch = (s.To - s.From) / s.Travel - fall * (0.5f * s.Travel);
                var straight = (s.To - s.From) / s.Travel;
                s.RodDebt += RodRate * dt;
                s.BallDebt += BallRate * dt;
                for (; s.RodDebt >= 1f; s.RodDebt -= 1f)
                {
                    // Spread over the frame so a slow frame does not bunch the rod up at the nozzle.
                    var tau = Random.value * dt;
                    Emit(_flameCore, s.From + launch * tau, launch + Random.insideUnitSphere * 0.7f, Random.Range(0.5f, 0.7f),
                        (s.Travel - tau) * Random.Range(0.95f, 1.05f));
                }
                for (; s.BallDebt >= 1f; s.BallDebt -= 1f)
                {
                    var tau = Random.value * dt;
                    // Balls of fire roll down the stream, splash onto the target and roll up off it (Splash).
                    Emit(_flameBalls, s.From + straight * tau + Random.insideUnitSphere * 0.12f,
                        straight * Random.Range(0.94f, 1.04f) + Random.insideUnitSphere * 0.9f,
                        Random.Range(2.4f, 3.2f), s.Travel * Random.Range(1.8f, 2.2f), Random.Range(-20f, 20f));
                }
                // Heat glowing round the stream (fewer on the Low tier).
                s.GlowDebt += GlowRate * density * dt;
                for (; s.GlowDebt >= 1f; s.GlowDebt -= 1f)
                {
                    var tau = Random.value * dt;
                    Emit(_flameGlow, s.From + straight * tau, straight * Random.Range(0.9f, 1f), Random.Range(1.8f, 2.6f),
                        s.Travel * Random.Range(1f, 1.2f));
                }
                // Thick black smoke rolling up off the far half of the stream and the burning target.
                s.SmokeDebt += SmokeRate * dt;
                for (; s.SmokeDebt >= 1f; s.SmokeDebt -= 1f)
                    DamageSmoke(Vector3.Lerp(s.From, s.To, Random.Range(0.55f, 1.05f)) + Vector3.up * 1.1f, Random.Range(2.1f, 3f), 0.02f);
            }
        }

        /// <summary>The black puff of an anti-aircraft shell bursting.</summary>
        public void Flak(Vector3 position)
        {
            for (var i = 0; i < 3; i++)
                Emit(_flak, position + Random.insideUnitSphere * 0.6f, Random.insideUnitSphere * 0.8f, Random.Range(1.2f, 2f),
                    Random.Range(1.4f, 2.4f));
        }

        /// <summary>Green sparkle rising off a vehicle being repaired.</summary>
        public void Repair(Vector3 position)
        {
            for (var i = 0; i < 6; i++)
                Emit(_repair, position + Random.insideUnitSphere * 1.2f, Vector3.up * Random.Range(1.5f, 3f), Random.Range(0.15f, 0.3f),
                    Random.Range(0.6f, 1f));
        }

        /// <summary>One billow of smoke off a damaged vehicle; <paramref name="shade"/> 1 is pale grey, 0 black.</summary>
        public void DamageSmoke(Vector3 position, float size, float shade)
        {
            var emit = new ParticleSystem.EmitParams
            {
                position = position + Random.insideUnitSphere * 0.3f,
                velocity = Vector3.up * Random.Range(0.6f, 1.2f) + Random.insideUnitSphere * 0.3f,
                startSize = size * Random.Range(0.8f, 1.2f),
                startLifetime = Random.Range(1.6f, 2.4f),
                startColor = new Color(0.12f + 0.4f * shade, 0.12f + 0.39f * shade, 0.12f + 0.38f * shade, 0.85f),
                rotation = Random.Range(0f, 360f),
                applyShapeToPosition = false,
            };
            _damageSmoke.Emit(emit, 1);
        }

        /// <summary>A lick of flame out of a burning hull.</summary>
        public void DamageFire(Vector3 position, float size)
        {
            Emit(_damageFire, position, Vector3.up * Random.Range(0.4f, 0.9f) + Random.insideUnitSphere * 0.2f, size * Random.Range(0.8f, 1.2f),
                Random.Range(0.45f, 0.75f), Random.Range(-10f, 10f));
        }

        public void Dust(Vector3 position, float scale)
        {
            Emit(_dust, position, Random.insideUnitSphere * 0.4f + Vector3.up * 0.3f, Random.Range(0.7f, 1.3f) * scale,
                Random.Range(0.7f, 1.3f));
        }

        /// <param name="rotation">Degrees; random all round by default (upright flame sheets pass a small tilt).</param>
        private static void Emit(ParticleSystem system, Vector3 position, Vector3 velocity, float size, float lifetime, float? rotation = null)
        {
            var emit = new ParticleSystem.EmitParams
            {
                position = position,
                velocity = velocity,
                startSize = size,
                startLifetime = lifetime,
                rotation = rotation ?? Random.Range(0f, 360f),
                applyShapeToPosition = false,
            };
            system.Emit(emit, 1);
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
