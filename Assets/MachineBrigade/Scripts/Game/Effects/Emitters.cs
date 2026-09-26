using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Shared world-space particle systems that effects emit into on demand: shell smoke trails,
    /// rocket motors, flame jets and tread dust. One system per kind keeps the cost to a few draw calls no
    /// matter how many vehicles are firing or driving.
    /// </summary>
    internal sealed class Emitters
    {
        private readonly ParticleSystem _trail;
        private readonly ParticleSystem _dust;
        private readonly ParticleSystem _motor;
        private readonly ParticleSystem _flame;
        private readonly ParticleSystem _flak;
        private readonly ParticleSystem _repair;

        public Emitters(MaterialLibrary m, Transform parent)
        {
            _trail = Continuous(parent, "Shell Trails", m.Smoke, 3000, PB.SmokeGradient(0.8f, 0.3f), 0.7f, 2.6f);
            _motor = Continuous(parent, "Rocket Motors", m.Fire, 400, PB.FireGradient, 1f, 0.2f);
            _flame = Continuous(parent, "Flame Jets", m.Fire, 600, PB.FireGradient, 0.5f, 2.2f);
            _flak = Continuous(parent, "Flak Bursts", m.Smoke, 200, PB.Plume(0.08f, 0.3f, 0.8f), 0.6f, 1.8f);
            _repair = Continuous(parent, "Repair", m.Sparks, 200,
                PB.Fade(new Color(0.5f, 1.6f, 0.8f), new Color(0.3f, 1.2f, 0.6f), new Color(0.2f, 0.8f, 0.4f)), 1f, 0.3f);
            _dust = Continuous(parent, "Tread Dust", m.Smoke, 1500,
                PB.Fade(new Color(0.62f, 0.56f, 0.44f), new Color(0.58f, 0.53f, 0.42f), new Color(0.55f, 0.5f, 0.4f), 0.45f), 0.8f, 2.4f);
        }

        public void Trail(Vector3 position, float size)
        {
            Emit(_trail, position, Random.insideUnitSphere * 0.2f + Vector3.up * 0.25f, size * Random.Range(0.7f, 1.2f),
                Random.Range(0.6f, 1.1f));
        }

        /// <summary>The burning motor behind a flying missile or rocket.</summary>
        public void Motor(Vector3 position, Vector3 forward, float scale)
        {
            Emit(_motor, position, -forward * 3f + Random.insideUnitSphere * 0.5f, Random.Range(0.5f, 0.9f) * Mathf.Max(0.6f, scale),
                Random.Range(0.08f, 0.16f));
        }

        /// <summary>One gout of a flamethrower stream flying towards <paramref name="to"/>.</summary>
        public void FlameJet(Vector3 from, Vector3 to, float seconds)
        {
            var velocity = (to - from) / Mathf.Max(0.1f, seconds);
            for (var i = 0; i < 3; i++)
                Emit(_flame, from + Random.insideUnitSphere * 0.15f, velocity * Random.Range(0.85f, 1.1f) + Random.insideUnitSphere * 1.2f,
                    Random.Range(0.5f, 0.9f), seconds * Random.Range(0.9f, 1.25f));
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

        public void Dust(Vector3 position, float scale)
        {
            Emit(_dust, position, Random.insideUnitSphere * 0.4f + Vector3.up * 0.3f, Random.Range(0.7f, 1.3f) * scale,
                Random.Range(0.7f, 1.3f));
        }

        private static void Emit(ParticleSystem system, Vector3 position, Vector3 velocity, float size, float lifetime)
        {
            var emit = new ParticleSystem.EmitParams
            {
                position = position,
                velocity = velocity,
                startSize = size,
                startLifetime = lifetime,
                rotation = Random.Range(0f, 360f),
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
