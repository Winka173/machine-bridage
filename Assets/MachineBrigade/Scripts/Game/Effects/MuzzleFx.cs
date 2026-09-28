using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Fire and smoke at the gun whenever a weapon fires: a white-hot core, a tongue of flame
    /// shot out along the barrel (plus side jets out of a cannon's muzzle brake), sparks, and a
    /// smoke puff that bursts forward, slows and hangs in the air. Big guns also blow dust off the
    /// ground, and launchers throw their back-blast behind them. Machine guns flicker once per
    /// round of the burst. Aircraft use the same recipes, aimed down at their target. Five shared
    /// systems draw every muzzle in the battle. The white-hot core and the flame tongues ride
    /// their muzzle for their short life (<see cref="Follow"/>): the systems are in world space,
    /// and a flash left where it was lit trailed a fast jeep or a jet by a metre or more, the
    /// later rounds of a burst appearing where the barrel had been (DECISIONS 12A). Sparks,
    /// smoke, the fireball and dust stay in the air they were thrown into.
    /// </summary>
    internal sealed class MuzzleFx
    {
        public enum Kind
        {
            MachineGun,
            Autocannon,
            Cannon,
            Artillery,
            Rocket,
            Missile,
        }

        private readonly struct Pending
        {
            public Pending(float at, Vector3 position, Vector3 direction, float scale, Anchor anchor)
            {
                At = at;
                Position = position;
                Direction = direction;
                Scale = scale;
                Anchor = anchor;
            }

            public float At { get; }
            public Vector3 Position { get; }
            public Vector3 Direction { get; }
            public float Scale { get; }
            public Anchor Anchor { get; }
        }

        /// <summary>
        /// The drawn part a flash rides on (the muzzle node the round left from, a launch rail, the
        /// hull), with the muzzle's point and the barrel's direction in that part's own space, so
        /// both can be found again as the hull drives on and the turret turns.
        /// </summary>
        internal readonly struct Anchor
        {
            public Anchor(Transform node, Vector3 world, Vector3 direction)
            {
                Node = node;
                Local = node != null ? node.InverseTransformPoint(world) : world;
                Axis = node != null ? node.InverseTransformDirection(direction) : direction;
            }

            public Transform Node { get; }
            public Vector3 Local { get; }
            public Vector3 Axis { get; }
            public bool Valid => Node != null;

            /// <summary>The muzzle where it is drawn now.</summary>
            public Vector3 Point => Node.TransformPoint(Local);

            /// <summary>The barrel's direction as drawn now.</summary>
            public Vector3 Direction => Node.TransformDirection(Axis);

            /// <summary>A world direction in the part's own space.</summary>
            public Vector3 ToLocal(Vector3 world) => Node.InverseTransformDirection(world);
        }

        /// <summary>A flash particle riding its muzzle: along its (local) axis from the muzzle, drifting out at Drift m/s.</summary>
        private readonly struct Riding
        {
            public Riding(ParticleSystem system, Anchor anchor, Vector3 axis, float along, float drift, float until)
            {
                System = system;
                Anchor = anchor;
                Axis = axis;
                Along = along;
                Drift = drift;
                Until = until;
            }

            public ParticleSystem System { get; }
            public Anchor Anchor { get; }
            public Vector3 Axis { get; }
            public float Along { get; }
            public float Drift { get; }
            public float Until { get; }
        }

        /// <summary>Tests: false leaves flashes where they were lit (the old behaviour), for before-and-after measurements.</summary>
        internal static bool RideMuzzles = true;

        /// <summary>Tests and tools: every flash as it is lit (muzzle point, the direction it faces).</summary>
        internal static System.Action<Vector3, Vector3> Flashed;

        /// <summary>Gap between machine-gun rounds; matches the tracer burst.</summary>
        public const float RoundInterval = 0.055f;

        /// <summary>Length of a flame tongue, in widths.</summary>
        private const float FlameLength = 4.2f;

        /// <summary>The share of its width a tongue is born at (it grows to 1.1 over its life).</summary>
        private const float TongueGrowFrom = 0.85f;

        /// <summary>
        /// The flame shape (Particle.shader, shape 3) fades out over about the last tenth of its quad
        /// at each end: the visible back end of a streak is this share of its length in from the
        /// quad's end, and that is what sits on the muzzle.
        /// </summary>
        internal const float FlameShapeMargin = 0.1f;

        private readonly ParticleSystem _core, _tongue, _sparks, _smoke, _dust, _fireball;
        private readonly List<Pending> _pending = new();

        /// <summary>Flash particles riding their muzzles, by the particle's seed.</summary>
        private readonly Dictionary<uint, Riding> _riding = new();
        private readonly List<uint> _gone = new();
        private ParticleSystem.Particle[] _buffer = new ParticleSystem.Particle[256];
        private uint _seed = (uint)Random.Range(1, int.MaxValue);

        /// <summary>The muzzle the shot being drawn now rides on (set for the length of one <see cref="Fire"/>).</summary>
        private Anchor _anchor;
        private float _now;

        public MuzzleFx(MaterialLibrary m, Transform parent)
        {
            var root = new GameObject("Muzzles").transform;
            root.SetParent(parent, false);

            _core = Shared(root, "Muzzle Core", m.Fire, 500);
            // Orange rather than white: the fire shader doubles it and whitens the hot centre itself.
            PB.Colors(_core, PB.Fade(new Color(1f, 0.66f, 0.28f), new Color(1f, 0.5f, 0.16f), new Color(0.9f, 0.3f, 0.08f)));
            PB.Grow(_core, 1f, 0.7f);

            // A slow particle stretched to several times its width along the barrel: a jet of flame
            // that stays on the muzzle instead of flying off.
            _tongue = Shared(root, "Muzzle Flame", m.Fire, 800, ParticleSystemRenderMode.Stretch);
            PB.Colors(_tongue, PB.Fade(new Color(1f, 0.78f, 0.4f), new Color(1f, 0.55f, 0.18f), new Color(0.9f, 0.3f, 0.07f)));
            PB.Grow(_tongue, TongueGrowFrom, 1.1f);
            var flame = _tongue.GetComponent<ParticleSystemRenderer>();
            flame.velocityScale = 0f;
            flame.lengthScale = FlameLength;

            _sparks = Shared(root, "Muzzle Sparks", m.Sparks, 600, gravity: 1.6f);
            var sparks = _sparks.main;
            sparks.startColor = new ParticleSystem.MinMaxGradient(new Color(1f, 0.85f, 0.45f), new Color(1f, 0.55f, 0.15f));
            PB.Grow(_sparks, 1f, 0.3f);

            // Light gunsmoke bursts out fast, is braked by the air and then drifts up with the wind.
            _smoke = Shared(root, "Muzzle Puffs", m.SoftSmoke, 1500);
            PB.Colors(_smoke, PB.Plume(0.6f, 0.82f, 0.78f));
            PB.Grow(_smoke, 0.8f, 2.5f);
            Brake(_smoke, 0.14f);
            PB.Rise(_smoke, 0.3f, 0.8f);

            // Big guns belch a ball of fire that rolls into smoke: the first half of the explosion flipbook.
            _fireball = Shared(root, "Muzzle Fireball", FxMaterials.Shared.Blast, 300);
            PB.Flipbook(_fireball, loop: false, to: 0.5f, tilt: 20f, pivotY: 0.12f);
            PB.Colors(_fireball, PB.Hold(new Color(0.55f, 0.53f, 0.5f), new Color(0.6f, 0.58f, 0.56f), 0.02f, 0.6f));
            PB.Grow(_fireball, 0.7f, 1.25f);
            Brake(_fireball, 0.2f);

            _dust = Shared(root, "Muzzle Dust", m.Smoke, 700);
            PB.Colors(_dust, PB.Fade(new Color(0.6f, 0.54f, 0.42f), new Color(0.56f, 0.51f, 0.4f), new Color(0.52f, 0.48f, 0.4f), 0.5f));
            PB.Grow(_dust, 0.6f, 2.1f);
            Brake(_dust, 0.1f);
        }

        /// <summary>
        /// Plays the muzzle effect of one shot at <paramref name="from"/>, pointing along
        /// <paramref name="direction"/>. <paramref name="groundY"/> is the height of the ground
        /// under a vehicle, or null for aircraft (no dust).
        /// </summary>
        public void Fire(Kind kind, Vector3 from, Vector3 direction, float now, float scale = 1f, float? groundY = null) =>
            Fire(kind, from, direction, now, default, scale, groundY);

        /// <summary>
        /// As above, the core and flame tongues riding <paramref name="anchor"/> (the part the
        /// muzzle is drawn on) for their life, so they stay on the barrel's tip as it moves.
        /// </summary>
        public void Fire(Kind kind, Vector3 from, Vector3 direction, float now, Anchor anchor, float scale = 1f, float? groundY = null)
        {
            var dir = direction.sqrMagnitude > 1e-4f ? direction.normalized : Vector3.forward;
            Flashed?.Invoke(from, dir);
            _anchor = anchor;
            _now = now;
            switch (kind)
            {
                case Kind.MachineGun:
                    // One flicker per round of the three-round burst.
                    Round(from, dir, scale, smoke: true);
                    _pending.Add(new Pending(now + RoundInterval, from, dir, scale, anchor));
                    _pending.Add(new Pending(now + RoundInterval * 2f, from, dir, scale, anchor));
                    break;

                case Kind.Autocannon:
                    Core(from, 2.1f * scale, 2.6f * scale, 0.07f, 0.1f);
                    Tongue(from, dir, 1, 0.72f * scale, 0.11f);
                    Sparks(from, dir, 3, 5f, 12f, scale);
                    Puffs(from, dir, 3, new Vector2(2f, 5f), new Vector2(0.6f, 0.95f), new Vector2(0.9f, 1.5f), scale);
                    break;

                case Kind.Cannon:
                    Cannon(from, dir, scale, groundY, artillery: false);
                    break;

                case Kind.Artillery:
                    Cannon(from, dir, scale, groundY, artillery: true);
                    break;

                case Kind.Rocket:
                case Kind.Missile:
                    // Launch flash at the tube, flame and a smoke cloud thrown out behind.
                    var s = kind == Kind.Missile ? 0.9f * scale : scale;
                    Core(from, 2.2f * s, 2.8f * s, 0.08f, 0.12f);
                    Tongue(from, -dir, 1, 0.8f * s, 0.15f);
                    Tongue(from, dir, 1, 0.5f * s, 0.1f);
                    Sparks(from, -dir, 4, 3f, 9f, s);
                    Puffs(from, -dir, 6, new Vector2(2.5f, 6.5f), new Vector2(0.9f, 1.5f), new Vector2(1.6f, 2.6f), s);
                    Puffs(from, dir, 2, new Vector2(1f, 3f), new Vector2(0.6f, 1f), new Vector2(1f, 1.8f), s);
                    if (groundY.HasValue) Dust(from, groundY.Value, -dir, 4, s);
                    break;
            }
            _anchor = default;
        }

        /// <summary>Emits the later machine-gun rounds that are due, each from where its barrel's tip is now.</summary>
        public void Tick(float now)
        {
            for (var i = _pending.Count - 1; i >= 0; i--)
            {
                var p = _pending[i];
                if (now < p.At) continue;
                _anchor = p.Anchor;
                _now = now;
                var riding = RideMuzzles && p.Anchor.Valid;
                Round(riding ? p.Anchor.Point : p.Position, riding ? p.Anchor.Direction.normalized : p.Direction, p.Scale, smoke: false);
                _anchor = default;
                _pending[i] = _pending[_pending.Count - 1];
                _pending.RemoveAt(_pending.Count - 1);
            }
        }

        /// <summary>
        /// Keeps each live core and flame tongue on its muzzle: called once the vehicles are drawn
        /// this frame (EffectsDirector.LaunchShots), it puts them back on the barrel's tip as drawn
        /// and turns the tongues along the barrel, however far the hull has driven or the turret
        /// turned since the flash was lit.
        /// </summary>
        public void Follow(float now)
        {
            if (_riding.Count == 0) return;
            if (RideMuzzles)
            {
                Follow(_core);
                Follow(_tongue);
            }
            _gone.Clear();
            foreach (var pair in _riding)
                if (now > pair.Value.Until || !pair.Value.Anchor.Valid) _gone.Add(pair.Key);
            foreach (var seed in _gone) _riding.Remove(seed);
        }

        private void Follow(ParticleSystem system)
        {
            var count = system.particleCount;
            if (count == 0) return;
            if (_buffer.Length < count) _buffer = new ParticleSystem.Particle[Mathf.NextPowerOfTwo(count)];
            count = system.GetParticles(_buffer, count);
            var moved = false;
            for (var i = 0; i < count; i++)
            {
                if (!_riding.TryGetValue(_buffer[i].randomSeed, out var ride) || ride.System != system || !ride.Anchor.Valid) continue;
                var axis = ride.Anchor.Node.TransformDirection(ride.Axis);
                // A stretched quad trails back from its particle by its whole length (the particle
                // is its tip), and a tongue grows: a length out keeps its base on the muzzle all its
                // life. A core sits on the muzzle.
                var along = ride.Along > 0f ? _buffer[i].GetCurrentSize(system) * FlameLength * (1f - FlameShapeMargin) : 0f;
                _buffer[i].position = ride.Anchor.Point + axis * along;
                if (ride.Drift > 0f) _buffer[i].velocity = axis * ride.Drift;
                moved = true;
            }
            if (moved) system.SetParticles(_buffer, count);
        }

        /// <summary>
        /// Tests: every live flash particle riding a muzzle, measured from its particle as it will
        /// be drawn: the base of a core (its centre) or of a stretched tongue (its back end along
        /// its velocity), the muzzle's point as drawn now, the way the particle points, and the
        /// barrel's direction as drawn now. A tongue's quad runs back from the particle (its tip)
        /// size x lengthScale (velocityScale 0; FlashTests.StretchedFlamesTrailBehindTheirParticle);
        /// its visible end is <see cref="FlameShapeMargin"/> of that in from the quad's end.
        /// </summary>
        internal struct Measured
        {
            /// <summary>The core's centre or the tongue's back end, as drawn.</summary>
            public Vector3 Flash;

            /// <summary>The muzzle it rides, as drawn now.</summary>
            public Vector3 Muzzle;

            /// <summary>The way a tongue points (a core: the barrel).</summary>
            public Vector3 Axis;

            /// <summary>The way the flash was lit to face (the barrel, or a launcher's line), as drawn now.</summary>
            public Vector3 Barrel;

            public bool Tongue;

            /// <summary>A tongue along the barrel (not a side jet out of the brake or a launcher's back-blast).</summary>
            public bool Forward;
        }

        internal void Measure(List<Measured> into)
        {
            into.Clear();
            Collect(_core, false, into);
            Collect(_tongue, true, into);
        }

        private void Collect(ParticleSystem system, bool tongue, List<Measured> into)
        {
            var count = system.particleCount;
            if (count == 0) return;
            if (_buffer.Length < count) _buffer = new ParticleSystem.Particle[Mathf.NextPowerOfTwo(count)];
            count = system.GetParticles(_buffer, count);
            var length = system.GetComponent<ParticleSystemRenderer>().lengthScale;
            for (var i = 0; i < count; i++)
            {
                if (!_riding.TryGetValue(_buffer[i].randomSeed, out var ride) || ride.System != system || !ride.Anchor.Valid) continue;
                var p = _buffer[i];
                var axis = p.velocity.sqrMagnitude > 1e-6f ? p.velocity.normalized : Vector3.zero;
                var flash = tongue ? p.position - axis * (p.GetCurrentSize(system) * length * (1f - FlameShapeMargin)) : p.position;
                // A side jet or a launcher's back-blast leaves the muzzle sideways or backwards on purpose.
                var barrel = ride.Anchor.Direction.normalized;
                into.Add(new Measured
                {
                    Flash = flash,
                    Muzzle = ride.Anchor.Point,
                    Axis = tongue ? axis : barrel,
                    Barrel = barrel,
                    Tongue = tongue,
                    Forward = tongue && Vector3.Dot(ride.Anchor.Node.TransformDirection(ride.Axis), barrel) > 0.9f,
                });
            }
        }

        private void Round(Vector3 from, Vector3 dir, float scale, bool smoke)
        {
            Core(from, 1.25f * scale, 1.6f * scale, 0.05f, 0.075f);
            Tongue(from, dir, 1, 0.48f * scale, 0.07f);
            if (Random.value < 0.35f) Sparks(from, dir, 1, 4f, 9f, scale);
            if (smoke) Puffs(from, dir, 2, new Vector2(1.5f, 3.5f), new Vector2(0.4f, 0.6f), new Vector2(0.6f, 1f), scale);
        }

        private void Cannon(Vector3 from, Vector3 dir, float scale, float? groundY, bool artillery)
        {
            var s = artillery ? 1.35f * scale : scale;
            Core(from, 3.8f * s, 4.5f * s, 0.09f, 0.12f);
            Tongue(from, dir, 2, 1.2f * s, 0.13f);
            // Side jets out of the muzzle brake.
            var side = Vector3.Cross(Vector3.up, dir);
            if (side.sqrMagnitude < 0.01f) side = Vector3.right;
            side.Normalize();
            Tongue(from, side, 1, 0.65f * s, 0.1f);
            Tongue(from, -side, 1, 0.65f * s, 0.1f);
            Sparks(from, dir, artillery ? 12 : 8, 6f, 15f, s);
            // Upright (the sheet's own tilt), unlike the round puffs, which spin freely.
            _fireball.Emit(new ParticleSystem.EmitParams
            {
                position = from + dir * (0.9f * s),
                velocity = dir * (6f * s),
                startSize = Random.Range(2.4f, 3f) * s,
                startLifetime = Random.Range(0.4f, 0.55f),
                applyShapeToPosition = false,
            }, 1);
            // A thick puff straight ahead and a ring blown out of the brake.
            Puffs(from, dir, artillery ? 12 : 9, new Vector2(3f, 9f), new Vector2(1.1f, 1.8f), new Vector2(2f, 3.2f) * (artillery ? 1.4f : 1f), s);
            Puffs(from, side, 2, new Vector2(2f, 5f), new Vector2(0.8f, 1.2f), new Vector2(1.4f, 2.4f), s);
            Puffs(from, -side, 2, new Vector2(2f, 5f), new Vector2(0.8f, 1.2f), new Vector2(1.4f, 2.4f), s);
            if (groundY.HasValue) Dust(from, groundY.Value, dir, artillery ? 12 : 7, s);
        }

        private void Core(Vector3 at, float minSize, float maxSize, float minLife, float maxLife)
        {
            var life = Random.Range(minLife, maxLife);
            Ride(_core, at, Vector3.zero, 0f, 0f, Random.Range(minSize, maxSize), life);
        }

        private void Tongue(Vector3 from, Vector3 dir, int count, float size, float life)
        {
            for (var i = 0; i < count; i++)
            {
                var width = size * Random.Range(0.85f, 1.15f);
                var axis = (dir + Random.insideUnitSphere * 0.08f).normalized;
                // A stretched quad trails back from its particle by its whole length: place the
                // particle a flame out so the tongue's base sits on the barrel's tip. (Placed half a
                // flame out, as if centred, half of every tongue burned back over the barrel: 1 m
                // on a machine gun, 3 m on a tank gun.) It drifts only slightly (the velocity sets
                // its direction). The old placement stays for the before measurements.
                var along = RideMuzzles ? width * TongueGrowFrom * FlameLength * (1f - FlameShapeMargin) : width * FlameLength * 0.5f;
                Ride(_tongue, from, axis, along, 1.5f, width, life * Random.Range(0.85f, 1.2f));
            }
        }

        /// <summary>
        /// Emits a core or tongue particle <paramref name="along"/> out from <paramref name="from"/>
        /// on <paramref name="axis"/>, riding the current shot's muzzle when it has one.
        /// </summary>
        private void Ride(ParticleSystem system, Vector3 from, Vector3 axis, float along, float drift, float size, float life)
        {
            if (!_anchor.Valid)
            {
                Emit(system, from + axis * along, axis * drift, size, life);
                return;
            }
            _seed = _seed * 1664525u + 1013904223u;
            system.Emit(new ParticleSystem.EmitParams
            {
                position = from + axis * along,
                velocity = axis * drift,
                startSize = size,
                startLifetime = life,
                rotation = Random.Range(0f, 360f),
                randomSeed = _seed,
                applyShapeToPosition = false,
            }, 1);
            _riding[_seed] = new Riding(system, _anchor, _anchor.ToLocal(axis), along, drift, _now + life + 0.05f);
        }

        /// <summary>A spray of sparks from <paramref name="from"/> along <paramref name="dir"/> (a dart striking armour, a railgun's hit).</summary>
        public void SparkBurst(Vector3 from, Vector3 dir, int count, float minSpeed, float maxSpeed, float scale = 1f) =>
            Sparks(from, dir, count, minSpeed, maxSpeed, scale);

        private void Sparks(Vector3 from, Vector3 dir, int count, float minSpeed, float maxSpeed, float scale)
        {
            for (var i = 0; i < count; i++)
            {
                var v = (dir + Random.insideUnitSphere * 0.45f).normalized * Random.Range(minSpeed, maxSpeed) * scale;
                Emit(_sparks, from, v, Random.Range(0.08f, 0.14f) * Mathf.Sqrt(scale), Random.Range(0.2f, 0.5f));
            }
        }

        private void Puffs(Vector3 from, Vector3 dir, int count, Vector2 speed, Vector2 size, Vector2 life, float scale)
        {
            for (var i = 0; i < count; i++)
            {
                var v = (dir + Random.insideUnitSphere * 0.3f) * Random.Range(speed.x, speed.y) * scale;
                Emit(_smoke, from + dir * 0.3f, v, Random.Range(size.x, size.y) * scale, Random.Range(life.x, life.y));
            }
        }

        private void Dust(Vector3 from, float groundY, Vector3 dir, int count, float scale)
        {
            var ground = new Vector3(from.x, groundY + 0.3f, from.z) + new Vector3(dir.x, 0f, dir.z) * 1.5f;
            for (var i = 0; i < count; i++)
            {
                var out2 = Random.insideUnitCircle.normalized;
                var outward = new Vector3(out2.x, 0f, out2.y) + new Vector3(dir.x, 0f, dir.z) * 0.8f;
                Emit(_dust, ground, outward * Random.Range(3f, 7f) * scale + Vector3.up * 0.4f, Random.Range(1.1f, 1.9f) * scale,
                    Random.Range(0.9f, 1.7f));
            }
        }

        private static void Emit(ParticleSystem system, Vector3 position, Vector3 velocity, float size, float lifetime)
        {
            system.Emit(new ParticleSystem.EmitParams
            {
                position = position,
                velocity = velocity,
                startSize = size,
                startLifetime = lifetime,
                rotation = Random.Range(0f, 360f),
                applyShapeToPosition = false,
            }, 1);
        }

        /// <summary>Air drag: the particle shoots out and stops within a fraction of a second.</summary>
        private static void Brake(ParticleSystem ps, float dampen)
        {
            var limit = ps.limitVelocityOverLifetime;
            limit.enabled = true;
            limit.limit = 0.3f;
            limit.dampen = dampen;
        }

        private static ParticleSystem Shared(Transform parent, string name, Material material, int max,
            ParticleSystemRenderMode mode = ParticleSystemRenderMode.Billboard, float gravity = 0f)
        {
            var ps = PB.Create(parent, name, material, mode);
            var main = ps.main;
            main.loop = true;
            main.maxParticles = max;
            main.gravityModifier = gravity;
            var emission = ps.emission;
            emission.enabled = false;
            ps.Play();
            return ps;
        }
    }
}
