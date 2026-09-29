using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Everything that keeps burning: craters, rubble, fuel depots, wrecks and napalm. All fires
    /// emit into a few shared systems (flames, smoke, embers, the glow they cast on the ground), so
    /// any number of them can burn at once and none is ever cut short to make room for another.
    /// Flames and smoke are flipbooks rendered from a fire simulation (<see cref="FxMaterials"/>):
    /// a few overlapping looping flame billboards per fire, each on its own frame, under a column
    /// of billowing black smoke. A fire flares up, burns, dies down, then keeps smouldering smoke
    /// for a while before it is gone. Fires burning on the ground (not riding a wreck or a hull)
    /// draw their flames and firelight lying on the ground in depth, so a vehicle driving through
    /// one is drawn on top of it rather than swallowed by it, and burn a fifth shorter than they
    /// are lit for, napalm excepted (DECISIONS 12A).
    /// </summary>
    internal sealed class FireSpots
    {
        private const float FlameRate = 2.4f;
        private const float SmokeRate = 1.3f;
        private const float EmberRate = 4f;
        private const float GlowRate = 2.2f;
        private const float FlareSeconds = 0.4f;
        private const float DieDownSeconds = 3f;
        private const float JetInterval = 1f / 26f;

        /// <summary>Where the base of the flames sits in a flame frame, as a pivot offset in particle sizes.</summary>
        private const float FlamePivot = 0.33f;

        /// <summary>Hard cap on burning spots; far beyond what a battle reaches.</summary>
        private const int MaxFires = 160;

        private struct Fire
        {
            public Vector3 Position;
            public Transform Anchor;
            public Vector3 AnchorOffset;
            public float Size, Start, Until, SmokeUntil;
            public float FlameDebt, SmokeDebt, EmberDebt, GlowDebt;
            public int Id;

            /// <summary>Its smoke's share (1: the full black column; less: a boss's death fires, thinner and lighter).</summary>
            public float Smoke;
        }

        /// <summary>
        /// DECISIONS 20Y: a boss's death fires smoke at this share, lighter and for a fraction of the smoulder (the owner:
        /// "the smoke lasts too long and covers everything"; the flames stay as big).
        /// </summary>
        internal const float BossSmoke = 0.35f;

        private int _nextId = 1;

        /// <summary>A ground fire burns this share of the time it is lit for (napalm burns in full).</summary>
        internal const float GroundBurn = 0.8f;

        /// <summary>Below this height an unanchored fire burns on the ground (wreck and hull fires sit higher or ride their hull).</summary>
        private const float GroundHeight = 0.7f;

        /// <summary>A copy of a flame or firelight material that lies on the ground in depth (see MbDepth.hlsl).</summary>
        internal static Material OnGround(Material source)
        {
            if (source == null) return null;
            if (Grounded.TryGetValue(source, out var made) && made != null) return made;
            made = new Material(source) { name = source.name + " (ground)", hideFlags = HideFlags.DontSave };
            made.SetFloat("_OntoGround", 1f);
            Grounded[source] = made;
            return made;
        }

        private static readonly Dictionary<Material, Material> Grounded = new();

        private static bool OnTheGround(in Fire f) => f.Anchor == null && f.Position.y < GroundHeight;

        private readonly List<Fire> _fires = new();
        private readonly ParticleSystem _flames;
        private readonly ParticleSystem _embers;
        private readonly ParticleSystem _smoke;

        /// <summary>Thinner, greyer smoke for the fires lit with less than the full smoke (a boss's death, DECISIONS 20Y).</summary>
        private readonly ParticleSystem _lightSmoke;
        private readonly ParticleSystem _glow;

        /// <summary>The flames and firelight of fires burning on the ground: under the vehicles in them.</summary>
        private readonly ParticleSystem _groundFlames, _groundGlow;

        /// <summary>Night: the firelight on the ground spreads twice as far.</summary>
        public bool Night { get; set; }

        public FireSpots(MaterialLibrary m, Transform parent)
        {
            var fx = FxMaterials.Shared;
            var root = new GameObject("Fires").transform;
            root.SetParent(parent, false);

            // Looping flame sheets standing on the fire's base; the sooty fringe takes this colour.
            _flames = Shared(root, "Flames", fx.Flames, 2500);
            PB.Flipbook(_flames, loop: true, tilt: 4f, pivotY: FlamePivot);
            PB.Colors(_flames, PB.Hold(new Color(0.24f, 0.21f, 0.19f), new Color(0.2f, 0.18f, 0.17f), 0.15f, 0.62f));
            PB.Grow(_flames, 0.92f, 1.06f);
            _groundFlames = Shared(root, "Ground Flames", OnGround(fx.Flames), 2500);
            PB.Flipbook(_groundFlames, loop: true, tilt: 4f, pivotY: FlamePivot);
            PB.Colors(_groundFlames, PB.Hold(new Color(0.24f, 0.21f, 0.19f), new Color(0.2f, 0.18f, 0.17f), 0.15f, 0.62f));
            PB.Grow(_groundFlames, 0.92f, 1.06f);

            _embers = Shared(root, "Embers", m.Sparks, 1200);
            PB.Colors(_embers, PB.Fade(new Color(1f, 0.8f, 0.4f), new Color(1f, 0.5f, 0.15f), new Color(0.6f, 0.15f, 0.05f)));
            var noise = _embers.noise;
            noise.enabled = true;
            noise.strength = 0.9f;
            noise.frequency = 0.5f;

            // A column of black smoke billowing up and leaning off with the wind.
            _smoke = Shared(root, "Smoke", fx.Smoke, 2500);
            PB.Flipbook(_smoke, loop: false, tilt: 20f);
            PB.Colors(_smoke, PB.Hold(new Color(0.09f, 0.085f, 0.08f), new Color(0.42f, 0.41f, 0.4f), 0.1f, 0.5f, 0.92f));
            PB.Grow(_smoke, 0.6f, 2.5f);
            PB.Rise(_smoke, 1.8f, 2.9f);
            _lightSmoke = Shared(root, "Light Smoke", fx.Smoke, 900);
            PB.Flipbook(_lightSmoke, loop: false, tilt: 20f);
            PB.Colors(_lightSmoke, PB.Hold(new Color(0.3f, 0.29f, 0.28f), new Color(0.58f, 0.57f, 0.56f), 0.1f, 0.4f, 0.55f));
            PB.Grow(_lightSmoke, 0.6f, 2.1f);
            PB.Rise(_lightSmoke, 1.8f, 2.9f);

            // Firelight flickering on the ground around each fire.
            _glow = Shared(root, "Fire Glow", m.Fire, 800, ParticleSystemRenderMode.HorizontalBillboard);
            PB.Colors(_glow, PB.Fade(new Color(1f, 0.5f, 0.15f), new Color(0.9f, 0.35f, 0.08f), new Color(0.6f, 0.15f, 0.03f), 0.32f));
            PB.Grow(_glow, 0.9f, 1.05f);
            _groundGlow = Shared(root, "Ground Fire Glow", OnGround(m.Fire), 800, ParticleSystemRenderMode.HorizontalBillboard);
            PB.Colors(_groundGlow, PB.Fade(new Color(1f, 0.5f, 0.15f), new Color(0.9f, 0.35f, 0.08f), new Color(0.6f, 0.15f, 0.03f), 0.32f));
            PB.Grow(_groundGlow, 0.9f, 1.05f);
        }

        public int Burning => _fires.Count;

        /// <summary>Tests: when fire <paramref name="id"/>'s flames go out (NaN once it is gone).</summary>
        internal float FlamesUntil(int id)
        {
            foreach (var f in _fires)
                if (f.Id == id) return f.Until;
            return float.NaN;
        }

        /// <summary>Only fires that could be seen emit particles; the rest keep burning silently.</summary>
        public System.Func<Vector3, bool> Visible { get; set; }

        /// <summary>
        /// Starts a fire of <paramref name="size"/> (1 is a car-sized blaze) burning for
        /// <paramref name="seconds"/>. With an anchor it follows that transform (a falling wreck).
        /// <paramref name="smoke"/> below 1 thins, lightens and shortens its smoke (a boss's death fires).
        /// </summary>
        /// <returns>A handle for <see cref="Extinguish"/>.</returns>
        public int Ignite(Vector3 position, float size, float seconds, float now, Transform anchor = null, bool napalm = false, float smoke = 1f)
        {
            smoke = Mathf.Clamp(smoke, 0.05f, 1f);
            // Ground fires burn a fifth shorter (the owner's second play test); napalm keeps its time.
            if (anchor == null && position.y < GroundHeight && !napalm) seconds *= GroundBurn;
            if (_fires.Count >= MaxFires)
            {
                // Drop whichever fire ends soonest; it was nearly out anyway.
                var soonest = 0;
                for (var i = 1; i < _fires.Count; i++)
                    if (_fires[i].SmokeUntil < _fires[soonest].SmokeUntil) soonest = i;
                _fires.RemoveAt(soonest);
            }
            _fires.Add(new Fire
            {
                Position = position,
                Anchor = anchor,
                AnchorOffset = anchor != null ? position - anchor.position : Vector3.zero,
                Size = size,
                Start = now,
                Until = now + seconds,
                SmokeUntil = now + seconds + Mathf.Min(45f, 8f + seconds * 0.8f) * smoke * smoke,
                Smoke = smoke,
                // Start part way through a flame, so a new fire shows at once.
                FlameDebt = 0.8f,
                Id = _nextId,
            });
            return _nextId++;
        }

        /// <summary>Puts a fire out: the flames stop and its smoke clears within a few seconds.</summary>
        public void Extinguish(int id, float now)
        {
            for (var i = 0; i < _fires.Count; i++)
            {
                if (_fires[i].Id != id) continue;
                var f = _fires[i];
                f.Until = Mathf.Min(f.Until, now);
                f.SmokeUntil = Mathf.Min(f.SmokeUntil, now + 3f);
                f.Anchor = null;
                _fires[i] = f;
                return;
            }
        }

        public void Tick(float now, float dt)
        {
            if (dt <= 0f) return;
            for (var i = _fires.Count - 1; i >= 0; i--)
            {
                var f = _fires[i];
                if (now >= f.SmokeUntil)
                {
                    _fires.RemoveAt(i);
                    continue;
                }
                if (f.Anchor != null) f.Position = f.Anchor.position + f.AnchorOffset;

                // Flare up quickly, burn, then die down over the last seconds.
                var flame = now < f.Until
                    ? Mathf.Clamp01((now - f.Start) / FlareSeconds) * Mathf.Clamp01((f.Until - now) / DieDownSeconds)
                    : 0f;
                // Smoke thickens with the fire and thins out while it smoulders.
                var smoke = now < f.Until ? Mathf.Max(0.4f, flame) : Mathf.Clamp01((f.SmokeUntil - now) / (f.SmokeUntil - f.Until)) * 0.55f;
                var intensity = Mathf.Sqrt(Mathf.Max(0.2f, f.Size));
                if (Visible != null && !Visible(f.Position))
                {
                    f.FlameDebt = f.EmberDebt = f.SmokeDebt = f.GlowDebt = 0f;
                    _fires[i] = f;
                    continue;
                }

                f.FlameDebt += dt * FlameRate * intensity * flame;
                f.EmberDebt += dt * EmberRate * intensity * flame * (f.Size >= 0.7f ? 1f : 0.3f);
                f.SmokeDebt += dt * SmokeRate * intensity * smoke * f.Smoke;
                f.GlowDebt += dt * GlowRate * flame;
                for (; f.FlameDebt >= 1f; f.FlameDebt -= 1f) EmitFlame(f, flame);
                for (; f.EmberDebt >= 1f; f.EmberDebt -= 1f) EmitEmber(f);
                for (; f.SmokeDebt >= 1f; f.SmokeDebt -= 1f) EmitSmoke(f, smoke);
                for (; f.GlowDebt >= 1f; f.GlowDebt -= 1f) EmitGlow(f);
                _fires[i] = f;
            }
        }

        /// <summary>
        /// Ammunition cooking off inside a hull: a roaring fountain of flame out of the turret ring,
        /// with sparks and smoke. Call every frame while it lasts; <paramref name="debt"/> carries
        /// the emission between frames.
        /// </summary>
        public void Jet(Vector3 at, float strength, ref float debt, float dt)
        {
            if (Visible != null && !Visible(at)) return;
            for (debt += dt; debt >= JetInterval; debt -= JetInterval)
            {
                var spread = Random.insideUnitCircle * 0.9f;
                _flames.Emit(new ParticleSystem.EmitParams
                {
                    position = at + new Vector3(spread.x * 0.2f, 0f, spread.y * 0.2f),
                    velocity = new Vector3(spread.x, Random.Range(7f, 12f) * strength, spread.y),
                    startSize = Random.Range(1.3f, 2.1f) * strength,
                    startLifetime = Random.Range(0.35f, 0.6f),
                }, 1);
                _embers.Emit(new ParticleSystem.EmitParams
                {
                    position = at,
                    velocity = new Vector3(Random.Range(-2.5f, 2.5f), Random.Range(8f, 15f), Random.Range(-2.5f, 2.5f)),
                    startSize = Random.Range(0.1f, 0.2f),
                    startLifetime = Random.Range(0.8f, 1.6f),
                }, 2);
                if (Random.value < 0.35f)
                    _smoke.Emit(new ParticleSystem.EmitParams
                    {
                        position = at + Vector3.up * 4f * strength,
                        velocity = new Vector3(0f, Random.Range(2f, 3.5f), 0f),
                        startSize = Random.Range(2f, 3f) * strength,
                        startLifetime = Random.Range(3f, 4.5f),
                    }, 1);
            }
        }

        public void Clear()
        {
            _fires.Clear();
            _flames.Clear();
            _embers.Clear();
            _smoke.Clear();
            _lightSmoke.Clear();
            _glow.Clear();
            _groundFlames.Clear();
            _groundGlow.Clear();
        }

        private void EmitFlame(in Fire f, float strength)
        {
            var disc = Random.insideUnitCircle * 0.35f * f.Size;
            (OnTheGround(f) ? _groundFlames : _flames).Emit(new ParticleSystem.EmitParams
            {
                position = f.Position + new Vector3(disc.x, 0.05f, disc.y),
                velocity = new Vector3(Random.Range(-0.1f, 0.1f), Random.Range(0.1f, 0.35f), Random.Range(-0.1f, 0.1f)),
                startSize = Random.Range(2.7f, 3.5f) * f.Size * Mathf.Lerp(0.75f, 1f, strength),
                startLifetime = Random.Range(1.6f, 2.4f),
            }, 1);
        }

        private void EmitEmber(in Fire f)
        {
            var disc = Random.insideUnitCircle * 0.7f * f.Size;
            _embers.Emit(new ParticleSystem.EmitParams
            {
                position = f.Position + new Vector3(disc.x, 0.6f * f.Size, disc.y),
                velocity = new Vector3(Random.Range(-0.6f, 0.6f), Random.Range(2f, 4.5f), Random.Range(-0.6f, 0.6f)),
                startSize = Random.Range(0.07f, 0.16f),
                startLifetime = Random.Range(1.2f, 2.6f),
            }, 1);
        }

        private void EmitSmoke(in Fire f, float thickness)
        {
            var disc = Random.insideUnitCircle * 0.5f * f.Size;
            (f.Smoke < 1f ? _lightSmoke : _smoke).Emit(new ParticleSystem.EmitParams
            {
                position = f.Position + new Vector3(disc.x, 1.5f * f.Size, disc.y),
                velocity = new Vector3(0f, Random.Range(0.3f, 0.7f), 0f),
                startSize = Random.Range(2f, 3f) * f.Size * Mathf.Lerp(0.7f, 1.15f, thickness),
                startLifetime = Random.Range(4.5f, 7f),
            }, 1);
        }

        private void EmitGlow(in Fire f)
        {
            (OnTheGround(f) ? _groundGlow : _glow).Emit(new ParticleSystem.EmitParams
            {
                position = new Vector3(f.Position.x, 0.08f, f.Position.z),
                // At night the firelight reaches much farther.
                startSize = Random.Range(2.6f, 3.4f) * f.Size * (Night ? 2f : 1f),
                startLifetime = Random.Range(0.7f, 1f),
                rotation = Random.Range(0f, 360f),
            }, 1);
        }

        private static ParticleSystem Shared(Transform parent, string name, Material material, int max,
            ParticleSystemRenderMode mode = ParticleSystemRenderMode.Billboard)
        {
            var ps = PB.Create(parent, name, material, mode);
            var main = ps.main;
            main.loop = true;
            main.maxParticles = max;
            var emission = ps.emission;
            emission.enabled = false;
            ps.Play();
            return ps;
        }
    }
}
