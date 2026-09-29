using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.Rendering;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Laser weapons (the Iron Beam, point-defence lasers, the Silver Bug's orbital laser) as one
    /// held beam per emitter, not a bar flashed for each 0.1 s shot (DECISIONS 11A):
    /// <list type="bullet">
    /// <item>Three camera-facing lines (MachineBrigade/Beam): a white-hot core, a coloured glow and
    /// a wide faint haze, with energy ripples running down them. The width pulses and the light
    /// flickers every frame.</item>
    /// <item>A charge-up when a beam starts: a ball of light swells at the emitter, sparks are
    /// drawn into it, and the beam grows from a thin pilot line to full width in 0.22 s.</item>
    /// <item>At the hit: a white-hot spot inside a coloured halo, a steady spray of sparks and
    /// molten drops bouncing off the ground, smoke curling off the burn, the ground lit and, on a
    /// ground target, a scorch mark.</item>
    /// <item>An afterglow when it stops: the core goes at once, the glow widens and fades over
    /// 0.28 s, the burn keeps glowing a moment and ionised air hangs along the line.</item>
    /// </list>
    /// The beam follows the emitter's turret and its target between shots. The view's alone: the
    /// simulation's shots and damage are unchanged. Low emits fewer sparks.
    /// </summary>
    internal sealed class LaserBeams
    {
        private const float ChargeSeconds = 0.22f;
        private const float AfterglowSeconds = 0.28f;
        private const float BurnInterval = 0.7f;
        private const int Capacity = 12;

        private readonly struct Palette
        {
            public Palette(Color core, Color glow, float width)
            {
                Core = core;
                Glow = glow;
                Width = width;
            }

            public Color Core { get; }
            public Color Glow { get; }
            public float Width { get; }
        }

        /// <summary>The Iron Beam and point defence: white core in a red glow. The Silver Bug's orbital laser: green, and heavier.</summary>
        private static Palette PaletteOf(WeaponDef weapon) => weapon != null && weapon.Id == "orbital_laser"
            ? new Palette(new Color(0.85f, 1f, 0.9f), new Color(0.25f, 1f, 0.42f), 1.5f)
            : new Palette(new Color(1f, 0.93f, 0.86f), new Color(1f, 0.3f, 0.09f), 1f);

        private sealed class Beam
        {
            public LineRenderer Core, Glow, Haze;
            public VehicleView Shooter;
            public int Mount;
            public EntityId Target;
            public bool Flies, Active, Stopped;
            public Vector3 From, To, BurnPoint;
            public float Start, Until, Seed, BurnAt, SparkDebt, SmokeAt;
            public Palette Colour;
        }

        private static Material _coreMaterial, _glowMaterial, _hazeMaterial;

        private readonly List<Beam> _beams = new();
        private readonly ParticleSystem _glow, _sparks, _light;
        private readonly Emitters _emitters;
        private readonly DecalPool _decals;

        public LaserBeams(MaterialLibrary m, Emitters emitters, DecalPool decals, Transform parent)
        {
            _emitters = emitters;
            _decals = decals;
            var root = new GameObject("Lasers").transform;
            root.SetParent(parent, false);
            if (_coreMaterial == null)
            {
                var shader = Shader.Find("MachineBrigade/Beam");
                _coreMaterial = shader != null ? BeamMaterial(shader, "Beam Core", 5f, 0.55f, 0.2f) : m.Tracer;
                _glowMaterial = shader != null ? BeamMaterial(shader, "Beam Glow", 5f, 1.5f, 0.45f) : m.Tracer;
                _hazeMaterial = shader != null ? BeamMaterial(shader, "Beam Haze", 2f, 2.4f, 0.3f) : m.Tracer;
            }
            for (var i = 0; i < Capacity; i++)
                _beams.Add(new Beam
                {
                    Haze = Line(root, _hazeMaterial, "Beam Haze"), Glow = Line(root, _glowMaterial, "Beam Glow"),
                    Core = Line(root, _coreMaterial, "Beam Core"),
                });

            // Round light at the emitter and the hit: a soft additive dot, fading over its brief life.
            _glow = Shared(root, "Laser Glow", m.Flash, 600);
            PB.Colors(_glow, PB.Fade(Color.white, Color.white, Color.white, 1f));
            // Sparks and molten drops spraying off the burn, bouncing along the ground.
            _sparks = Shared(root, "Laser Sparks", m.Sparks, 2000, 1.6f);
            PB.Grow(_sparks, 1f, 0.25f);
            PB.BounceOffGround(_sparks, PB.GroundPlane(root), 0.35f, 0.4f, 0.1f);
            // The ground lit under a burn on the ground.
            _light = Shared(root, "Laser Light", m.Glow, 200, 0f, ParticleSystemRenderMode.HorizontalBillboard);
            PB.Colors(_light, PB.Fade(Color.white, Color.white, Color.white, 0.8f));
        }

        /// <summary>
        /// One shot of a laser: the beam from <paramref name="from"/> onto <paramref name="to"/>, held
        /// <paramref name="hold"/> seconds (a little past the next shot, so a firing laser is one
        /// unbroken beam). The same emitter firing again takes over its beam.
        /// </summary>
        public void Fire(VehicleView shooter, int mount, Vector3 from, Vector3 to, EntityId target, bool flies, WeaponDef weapon, float now,
            float hold)
        {
            Beam beam = null;
            foreach (var b in _beams)
                if (b.Active && b.Shooter == shooter && b.Mount == mount && (shooter != null || (b.From - from).sqrMagnitude < 4f))
                {
                    beam = b;
                    break;
                }
            if (beam == null)
            {
                beam = Free();
                beam.Active = true;
                beam.Shooter = shooter;
                beam.Mount = mount;
                beam.Start = now;
                beam.Seed = Random.value * 100f;
                beam.BurnAt = now + 0.15f;
                beam.BurnPoint = new Vector3(1e6f, 0f, 0f);
                beam.SparkDebt = 0f;
                beam.SmokeAt = now + 0.1f;
                beam.Colour = PaletteOf(weapon);
                beam.Core.enabled = beam.Glow.enabled = beam.Haze.enabled = true;
            }
            beam.Stopped = false;
            beam.Target = target;
            beam.Flies = flies;
            beam.From = from;
            beam.To = to;
            beam.Until = Mathf.Max(beam.Until, now + hold);
        }

        /// <summary>
        /// Play-test 5 (DECISIONS 20V): a burn left where a slug struck (the railgun truck's, the coilgun's), like the
        /// focused laser's: a white-hot spot on the target cooling through orange over <paramref name="seconds"/>, a
        /// spray of sparks and molten drops dying down with it, smoke curling off, and a scorch on the ground under a
        /// ground target. It rides the target while it lives.
        /// </summary>
        public void Sear(Vector3 at, EntityId target, VehicleView struck, float width, float seconds, float now)
        {
            var burn = new Burn
            {
                Target = target, At = at, Offset = struck != null && struck.Root != null ? at - struck.Position : Vector3.zero,
                Flies = struck != null && struck.Flying, Start = now, Until = now + seconds, Width = width, SmokeAt = now,
            };
            if (_burns.Count >= Capacity) _burns.RemoveAt(0);
            _burns.Add(burn);
            if (!burn.Flies && _decals != null) _decals.Place(new Vector3(at.x, 0.15f, at.z), 1.6f * width);
        }

        private sealed class Burn
        {
            public EntityId Target;
            public Vector3 At, Offset;
            public bool Flies;
            public float Start, Until, Width, SparkDebt, SmokeAt;
        }

        private readonly List<Burn> _burns = new();

        /// <summary>Burns glowing now (for tests).</summary>
        internal int Burns => _burns.Count;

        private void TickBurns(float now, float dt, ViewRegistry views, float sparkRate)
        {
            for (var i = _burns.Count - 1; i >= 0; i--)
            {
                var b = _burns[i];
                if (now >= b.Until)
                {
                    _burns.RemoveAt(i);
                    continue;
                }
                if (views != null && b.Target != EntityId.None && views.TryGet(b.Target, out var target) && target.Root != null)
                    b.At = target.Position + b.Offset;
                var heat = 1f - Mathf.Clamp01((now - b.Start) / (b.Until - b.Start));
                var hot = heat * heat;
                // White-hot at first, then orange, then a dull red as it cools.
                var core = Color.Lerp(new Color(1f, 0.35f, 0.08f), new Color(1f, 0.95f, 0.85f), hot);
                Glow(b.At, 1.5f * b.Width * (0.5f + 0.5f * heat), core, 0.4f + 0.6f * heat, dt);
                Glow(b.At, 3.6f * b.Width * (0.4f + 0.6f * heat), new Color(1f, 0.5f, 0.16f), 0.65f * heat, dt);
                for (b.SparkDebt += sparkRate * 0.6f * b.Width * hot * dt; b.SparkDebt >= 1f; b.SparkDebt -= 1f)
                {
                    var dir = (Vector3.up + Random.insideUnitSphere * 1.2f).normalized;
                    var drop = Random.value < 0.3f;
                    Spark(b.At, dir * Random.Range(drop ? 2f : 4f, drop ? 6f : 11f) + Vector3.up,
                        drop ? Random.Range(0.14f, 0.24f) : Random.Range(0.08f, 0.15f), drop ? Random.Range(0.5f, 0.9f) : Random.Range(0.2f, 0.45f),
                        new Color(1f, Random.Range(0.55f, 0.8f), 0.3f));
                }
                if (now >= b.SmokeAt)
                {
                    b.SmokeAt = now + 0.14f;
                    _emitters.DamageSmoke(b.At + Vector3.up * 0.3f, 0.7f * b.Width, 0.2f);
                }
                if (!b.Flies) Light(new Vector3(b.At.x, 0.08f, b.At.z), 3.8f * b.Width * heat, new Color(1f, 0.5f, 0.16f), 0.5f * heat, dt);
            }
        }

        public void Tick(float now, float dt, ViewRegistry views)
        {
            if (dt <= 0f) return;
            var sparkRate = 50f + 70f * ExplosionEffect.Density;
            TickBurns(now, dt, views, sparkRate);

            foreach (var b in _beams)
            {
                if (!b.Active) continue;
                // The beam rides the emitter's turret and follows its target between shots.
                if (b.Shooter != null)
                {
                    if (b.Shooter.Root != null && b.Shooter.Sim.IsAlive) b.From = b.Shooter.MuzzleOf(Mathf.Max(0, b.Mount));
                    else b.Until = Mathf.Min(b.Until, now);
                }
                if (views != null && b.Target != EntityId.None && views.TryGet(b.Target, out var target) && target.Root != null)
                {
                    var p = target.Position;
                    b.To = new Vector3(p.x, b.Flies ? target.Altitude + 0.4f : b.To.y, p.z);
                }

                var on = now <= b.Until;
                var after = on ? 0f : (now - b.Until) / AfterglowSeconds;
                if (after >= 1f)
                {
                    b.Active = false;
                    b.Core.enabled = b.Glow.enabled = b.Haze.enabled = false;
                    continue;
                }
                var charge = Mathf.SmoothStep(0f, 1f, (now - b.Start) / ChargeSeconds);
                var w = 1f + 0.13f * Mathf.Sin(now * 43f + b.Seed) + 0.07f * Mathf.Sin(now * 97f + b.Seed * 1.7f) + Random.Range(-0.05f, 0.05f);
                var flicker = Random.Range(0.86f, 1f);
                var width = b.Colour.Width;
                var fade = 1f - after;

                // Core: gone within a few frames of the last shot. Glow: widens as it fades. Haze: faint and wide.
                Set(b.Core, b.From, b.To, 0.3f * width * w * Mathf.Lerp(0.3f, 1f, charge), b.Colour.Core,
                    flicker * Mathf.Lerp(0.55f, 1f, charge) * Mathf.Clamp01(1f - after * 3.5f));
                Set(b.Glow, b.From, b.To, 1.25f * width * w * Mathf.Lerp(0.25f, 1f, charge) * (1f + 0.4f * after), b.Colour.Glow,
                    0.85f * flicker * charge * fade);
                Set(b.Haze, b.From, b.To, 3.4f * width * (0.9f + 0.1f * w), b.Colour.Glow, 0.26f * charge * fade);

                // The emitter: a ball of light swelling through the charge-up (past its steady size), then pulsing.
                var ball = charge < 1f ? Mathf.Lerp(0.5f, 1.9f, charge) : 1.2f + 0.15f * w;
                Glow(b.From, ball * 1.5f * width * fade, b.Colour.Glow, 0.75f * fade, dt);
                Glow(b.From, ball * 0.7f * width * fade, b.Colour.Core, fade, dt);
                if (on && charge < 1f)
                    for (var s = 0; s < 2; s++)
                    {
                        var ring = Random.onUnitSphere * 1.3f * width;
                        Spark(b.From + ring, -ring * Random.Range(4f, 6f), 0.08f, 0.2f, b.Colour.Glow);
                    }

                if (on && charge > 0.4f)
                {
                    // The hit: a white-hot spot in a coloured halo, sparks and molten drops, smoke off the burn.
                    Glow(b.To, 1.9f * width * w, b.Colour.Core, 1f, dt);
                    Glow(b.To, 4.6f * width * w, b.Colour.Glow, 0.7f, dt);
                    var back = (b.From - b.To).normalized;
                    for (b.SparkDebt += sparkRate * width * dt; b.SparkDebt >= 1f; b.SparkDebt -= 1f)
                    {
                        var dir = (back + Random.insideUnitSphere * 1.1f).normalized;
                        // Mostly quick bright sparks; one in four a fat molten drop that arcs down and bounces.
                        var drop = Random.value < 0.25f;
                        Spark(b.To, dir * Random.Range(drop ? 3f : 6f, drop ? 8f : 16f) + Vector3.up * 2f,
                            drop ? Random.Range(0.18f, 0.28f) : Random.Range(0.1f, 0.18f), drop ? Random.Range(0.6f, 1f) : Random.Range(0.25f, 0.55f),
                            new Color(1f, Random.Range(0.6f, 0.85f), 0.35f));
                    }
                    if (now >= b.SmokeAt)
                    {
                        b.SmokeAt = now + 0.12f;
                        _emitters.DamageSmoke(b.To + Vector3.up * 0.3f, 0.75f * width, 0.22f);
                    }
                    if (!b.Flies)
                    {
                        Light(new Vector3(b.To.x, 0.08f, b.To.z), 4.5f * width * w, b.Colour.Glow, 0.55f, dt);
                        // A scorch where it burns, one each 0.7 s at most and only where it has moved on.
                        if (_decals != null && now >= b.BurnAt && (b.BurnPoint - b.To).sqrMagnitude > 2.25f)
                        {
                            _decals.Place(b.To, 1.1f * width);
                            b.BurnPoint = b.To;
                            b.BurnAt = now + BurnInterval;
                        }
                    }
                }
                else if (!on)
                {
                    // Afterglow: the burn cools from white through orange; ionised air hangs along the line once.
                    Glow(b.To, 1.7f * width * fade, new Color(1f, 0.45f, 0.12f), 0.9f * fade, dt);
                    if (!b.Stopped)
                    {
                        b.Stopped = true;
                        var length = Vector3.Distance(b.From, b.To);
                        for (var d = 2f; d < length; d += 3f) _emitters.Trail(Vector3.Lerp(b.From, b.To, d / length), 0.3f * width);
                    }
                }
            }
        }

        /// <summary>Beams burning now (for tests).</summary>
        internal int ActiveBeams
        {
            get
            {
                var n = 0;
                foreach (var b in _beams)
                    if (b.Active) n++;
                return n;
            }
        }

        private Beam Free()
        {
            Beam oldest = _beams[0];
            foreach (var b in _beams)
            {
                if (!b.Active) return b;
                if (b.Until < oldest.Until) oldest = b;
            }
            return oldest;
        }

        private static void Set(LineRenderer line, Vector3 from, Vector3 to, float width, Color colour, float alpha)
        {
            line.SetPosition(0, from);
            line.SetPosition(1, to);
            line.widthMultiplier = Mathf.Max(0.001f, width);
            colour.a = Mathf.Clamp01(alpha);
            line.startColor = colour;
            line.endColor = colour;
        }

        private void Glow(Vector3 at, float size, Color colour, float alpha, float dt)
        {
            if (size <= 0.01f || alpha <= 0.01f) return;
            colour.a = Mathf.Clamp01(alpha);
            _glow.Emit(new ParticleSystem.EmitParams
            {
                position = at, startSize = size, startColor = colour, startLifetime = Mathf.Max(0.04f, dt * 1.6f), applyShapeToPosition = false,
            }, 1);
        }

        private void Light(Vector3 at, float size, Color colour, float alpha, float dt)
        {
            colour.a = Mathf.Clamp01(alpha);
            _light.Emit(new ParticleSystem.EmitParams
            {
                position = at, startSize = size, startColor = colour, startLifetime = Mathf.Max(0.04f, dt * 1.6f),
                rotation = Random.Range(0f, 360f), applyShapeToPosition = false,
            }, 1);
        }

        private void Spark(Vector3 at, Vector3 velocity, float size, float life, Color colour)
        {
            _sparks.Emit(new ParticleSystem.EmitParams
            {
                position = at, velocity = velocity, startSize = size, startLifetime = life, startColor = colour, applyShapeToPosition = false,
            }, 1);
        }

        private static Material BeamMaterial(Shader shader, string name, float intensity, float softness, float ripple)
        {
            var m = new Material(shader) { name = name, hideFlags = HideFlags.DontSave, renderQueue = 3010 };
            m.SetFloat("_Intensity", intensity);
            m.SetFloat("_Softness", softness);
            m.SetFloat("_Ripple", ripple);
            return m;
        }

        private static LineRenderer Line(Transform parent, Material material, string name)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var line = go.AddComponent<LineRenderer>();
            line.sharedMaterial = material;
            line.useWorldSpace = true;
            line.positionCount = 2;
            line.alignment = LineAlignment.View;
            line.textureMode = LineTextureMode.Tile;
            line.numCapVertices = 0;
            line.shadowCastingMode = ShadowCastingMode.Off;
            line.receiveShadows = false;
            line.enabled = false;
            return line;
        }

        private static ParticleSystem Shared(Transform parent, string name, Material material, int max, float gravity = 0f,
            ParticleSystemRenderMode mode = ParticleSystemRenderMode.Billboard)
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
