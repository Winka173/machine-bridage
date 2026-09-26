using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Everything that keeps burning: craters, rubble, fuel depots and wrecks. All fires emit into
    /// three shared systems (flames, embers, smoke), so any number of them can burn at once and
    /// none is ever cut short to make room for another. A fire flares up, burns, dies down, then
    /// keeps smouldering smoke for a while before it is gone.
    /// </summary>
    internal sealed class FireSpots
    {
        private const float FlameRate = 18f;
        private const float SmokeRate = 5f;
        private const float EmberRate = 4f;
        private const float FlareSeconds = 0.4f;
        private const float DieDownSeconds = 3f;

        /// <summary>Hard cap on burning spots; far beyond what a battle reaches.</summary>
        private const int MaxFires = 160;

        private struct Fire
        {
            public Vector3 Position;
            public Transform Anchor;
            public Vector3 AnchorOffset;
            public float Size, Start, Until, SmokeUntil;
            public float FlameDebt, SmokeDebt, EmberDebt;
        }

        private readonly List<Fire> _fires = new();
        private readonly ParticleSystem _flames;
        private readonly ParticleSystem _embers;
        private readonly ParticleSystem _smoke;

        public FireSpots(MaterialLibrary m, Transform parent)
        {
            var root = new GameObject("Fires").transform;
            root.SetParent(parent, false);

            _flames = Shared(root, "Flames", m.Fire, 4000);
            PB.Colors(_flames, PB.FireGradient);
            PB.Grow(_flames, 1f, 0.3f);

            _embers = Shared(root, "Embers", m.Sparks, 800);
            PB.Colors(_embers, PB.Fade(new Color(1f, 0.8f, 0.4f), new Color(1f, 0.5f, 0.15f), new Color(0.6f, 0.15f, 0.05f)));
            var noise = _embers.noise;
            noise.enabled = true;
            noise.strength = 0.9f;
            noise.frequency = 0.5f;

            _smoke = Shared(root, "Smoke", m.Smoke, 3000);
            PB.Colors(_smoke, PB.Plume(0.14f, 0.45f, 0.34f));
            PB.Grow(_smoke, 0.7f, 2.4f);
            PB.Rise(_smoke, 1.8f, 2.8f);
        }

        public int Burning => _fires.Count;

        /// <summary>
        /// Starts a fire of <paramref name="size"/> (1 is a car-sized blaze) burning for
        /// <paramref name="seconds"/>. With an anchor it follows that transform (a falling wreck).
        /// </summary>
        public void Ignite(Vector3 position, float size, float seconds, float now, Transform anchor = null)
        {
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
                SmokeUntil = now + seconds + Mathf.Min(45f, 8f + seconds * 0.8f),
            });
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

                f.FlameDebt += dt * FlameRate * intensity * flame;
                f.EmberDebt += dt * EmberRate * intensity * flame * (f.Size >= 0.7f ? 1f : 0.3f);
                f.SmokeDebt += dt * SmokeRate * intensity * smoke;
                for (; f.FlameDebt >= 1f; f.FlameDebt -= 1f) EmitFlame(f);
                for (; f.EmberDebt >= 1f; f.EmberDebt -= 1f) EmitEmber(f);
                for (; f.SmokeDebt >= 1f; f.SmokeDebt -= 1f) EmitSmoke(f, smoke);
                _fires[i] = f;
            }
        }

        public void Clear()
        {
            _fires.Clear();
            _flames.Clear();
            _embers.Clear();
            _smoke.Clear();
        }

        private void EmitFlame(in Fire f)
        {
            var disc = Random.insideUnitCircle * 0.9f * f.Size;
            var lift = Mathf.Sqrt(f.Size);
            _flames.Emit(new ParticleSystem.EmitParams
            {
                position = f.Position + new Vector3(disc.x, 0.1f, disc.y),
                velocity = new Vector3(Random.Range(-0.25f, 0.25f), Random.Range(1.2f, 2.6f) * lift, Random.Range(-0.25f, 0.25f)),
                startSize = Random.Range(0.9f, 1.8f) * f.Size,
                startLifetime = Random.Range(0.5f, 1f),
                rotation = Random.Range(0f, 360f),
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
            var disc = Random.insideUnitCircle * 0.6f * f.Size;
            _smoke.Emit(new ParticleSystem.EmitParams
            {
                position = f.Position + new Vector3(disc.x, 1.1f * f.Size, disc.y),
                velocity = new Vector3(0f, Random.Range(0.2f, 0.5f), 0f),
                startSize = Random.Range(1f, 1.9f) * f.Size * Mathf.Lerp(0.7f, 1.2f, thickness),
                startLifetime = Random.Range(2.6f, 4.2f),
                rotation = Random.Range(0f, 360f),
            }, 1);
        }

        private static ParticleSystem Shared(Transform parent, string name, Material material, int max)
        {
            var ps = PB.Create(parent, name, material);
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
