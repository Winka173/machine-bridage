using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Shared world-space particle systems that effects emit into on demand: shell smoke trails,
    /// muzzle smoke and tread dust. One system per kind keeps the cost to a few draw calls no
    /// matter how many vehicles are firing or driving.
    /// </summary>
    internal sealed class Emitters
    {
        private readonly ParticleSystem _trail;
        private readonly ParticleSystem _muzzle;
        private readonly ParticleSystem _dust;

        public Emitters(MaterialLibrary m, Transform parent)
        {
            _trail = Continuous(parent, "Shell Trails", m.Smoke, 1500, PB.SmokeGradient(0.8f, 0.3f), 0.7f, 2.6f);
            _muzzle = Continuous(parent, "Muzzle Smoke", m.Smoke, 300, PB.SmokeGradient(0.62f, 0.5f), 0.7f, 2.8f);
            _dust = Continuous(parent, "Tread Dust", m.Smoke, 400,
                PB.Fade(new Color(0.62f, 0.56f, 0.44f), new Color(0.58f, 0.53f, 0.42f), new Color(0.55f, 0.5f, 0.4f), 0.45f), 0.8f, 2.4f);
        }

        public void Trail(Vector3 position, float size)
        {
            Emit(_trail, position, Random.insideUnitSphere * 0.2f + Vector3.up * 0.25f, size * Random.Range(0.7f, 1.2f),
                Random.Range(0.6f, 1.1f));
        }

        public void MuzzleSmoke(Vector3 position, Vector3 forward, float scale)
        {
            for (var i = 0; i < 4; i++)
            {
                var velocity = forward * Random.Range(1.5f, 4f) * scale + Random.insideUnitSphere * 0.6f + Vector3.up * 0.4f;
                Emit(_muzzle, position, velocity, Random.Range(0.6f, 1.2f) * scale, Random.Range(0.9f, 1.8f));
            }
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
