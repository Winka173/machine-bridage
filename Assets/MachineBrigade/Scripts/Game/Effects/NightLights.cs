using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Light at night, after World in Conflict's night battles: blasts, gun flashes and fires throw
    /// pools of warm light on the ground, and illumination flares drift down over the fighting,
    /// lighting a wide circle under them. The pools are additive quads lying on the ground (no
    /// real lights, which would shade every lit material again on a phone); vehicles above them
    /// stay as they are.
    /// </summary>
    internal sealed class NightLights
    {
        private sealed class Flare
        {
            public Vector3 Position;
            public float Born, Life, Drift;
            public Vector3 Wind;
        }

        private const float FlareAltitude = 34f;
        private const float FlareFall = 1.9f;

        private readonly ParticleSystem _pools;
        private readonly ParticleSystem _flarePools;
        private readonly ParticleSystem _stars;
        private readonly Emitters _emitters;
        private readonly List<Flare> _flares = new();
        private readonly ParticleSystem.Particle[] _poolBuffer = new ParticleSystem.Particle[8];
        private readonly ParticleSystem.Particle[] _starBuffer = new ParticleSystem.Particle[8];
        private float _nextFlare;
        private float _nextTrail;

        public NightLights(MaterialLibrary materials, Emitters emitters, Transform parent)
        {
            _emitters = emitters;
            var root = new GameObject("Night Lights").transform;
            root.SetParent(parent, false);

            // Short warm pools: blasts and gun flashes.
            _pools = PB.Create(root, "Light Pools", materials.Glow, ParticleSystemRenderMode.HorizontalBillboard);
            var main = _pools.main;
            main.loop = true;
            main.maxParticles = 300;
            main.startSpeed = 0f;
            main.startRotation = 0f;
            var emission = _pools.emission;
            emission.enabled = false;
            var shape = _pools.shape;
            shape.enabled = false;
            PB.Colors(_pools, PB.Fade(new Color(1f, 0.66f, 0.34f), new Color(1f, 0.52f, 0.22f), new Color(0.6f, 0.24f, 0.08f), 1f));
            PB.Grow(_pools, 0.8f, 1.1f);
            _pools.GetComponent<ParticleSystemRenderer>().maxParticleSize = 8f;
            _pools.Play();

            // The flares' circles of pale light, and the flares themselves: set by hand each frame.
            _flarePools = Manual(root, "Flare Pools", materials.Glow, ParticleSystemRenderMode.HorizontalBillboard);
            _stars = Manual(root, "Flare Stars", materials.Flash, ParticleSystemRenderMode.Billboard);
            _nextFlare = Time.time + 6f;
        }

        /// <summary>It is night: the pools and flares show. By day nothing is drawn.</summary>
        public bool Night { get; set; }

        /// <summary>A blast lights the ground round it for a moment.</summary>
        public void Blast(Vector3 at, float radius, float seconds)
        {
            if (!Night) return;
            _pools.Emit(new ParticleSystem.EmitParams
            {
                position = new Vector3(at.x, 0.12f, at.z), startSize = radius * 2f, startLifetime = seconds,
                startColor = new Color(1f, 1f, 1f, 0.9f), applyShapeToPosition = false, velocity = Vector3.zero,
            }, 1);
        }

        /// <summary>A gun's flash lights the ground at its muzzle for a blink.</summary>
        public void Flash(Vector3 at, float radius)
        {
            if (!Night) return;
            _pools.Emit(new ParticleSystem.EmitParams
            {
                position = new Vector3(at.x, 0.12f, at.z), startSize = radius * 2f, startLifetime = 0.12f,
                startColor = new Color(1f, 1f, 1f, 0.7f), applyShapeToPosition = false, velocity = Vector3.zero,
            }, 1);
        }

        /// <summary>
        /// Per frame: a new illumination flare over the fighting every 10 to 16 s (at
        /// <paramref name="fight"/>, the camera's focus), and every flare drifting down, flickering
        /// and lighting a 30 m circle under it until it burns out.
        /// </summary>
        public void Tick(float now, float dt, Vector3 fight)
        {
            if (!Night)
            {
                if (_flares.Count > 0)
                {
                    _flares.Clear();
                    _flarePools.Clear();
                    _stars.Clear();
                }
                return;
            }
            if (now >= _nextFlare && _flares.Count < 3)
            {
                _nextFlare = now + Random.Range(10f, 16f);
                var at = fight + new Vector3(Random.Range(-14f, 14f), 0f, Random.Range(-14f, 14f));
                _flares.Add(new Flare
                {
                    Position = new Vector3(at.x, FlareAltitude, at.z), Born = now, Life = Random.Range(13f, 17f), Drift = Random.Range(0f, 10f),
                    Wind = new Vector3(Random.Range(-0.6f, 0.6f), 0f, Random.Range(-0.6f, 0.6f)),
                });
            }
            var trail = now >= _nextTrail;
            if (trail) _nextTrail = now + 0.18f;
            var n = 0;
            for (var i = _flares.Count - 1; i >= 0; i--)
            {
                var f = _flares[i];
                var age = now - f.Born;
                if (age > f.Life || f.Position.y < 2f)
                {
                    _flares.RemoveAt(i);
                    continue;
                }
                // Under its parachute: a slow fall, swinging and drifting with the wind.
                f.Position += (Vector3.down * FlareFall + f.Wind) * dt;
                var swing = new Vector3(Mathf.Sin(now * 1.3f + f.Drift), 0f, Mathf.Cos(now * 1.1f + f.Drift)) * 0.6f;
                var fade = Mathf.Clamp01(age / 0.6f) * Mathf.Clamp01((f.Life - age) / 1.5f);
                var flicker = 0.85f + 0.15f * Mathf.PerlinNoise(now * 9f, f.Drift);
                if (n < _poolBuffer.Length)
                {
                    // The lit circle widens as the flare comes down, and brightens.
                    var height = Mathf.InverseLerp(FlareAltitude, 4f, f.Position.y);
                    _poolBuffer[n] = new ParticleSystem.Particle
                    {
                        position = new Vector3(f.Position.x, 0.14f, f.Position.z) + swing, startSize = Mathf.Lerp(26f, 36f, height),
                        startColor = new Color(0.78f, 0.84f, 0.95f, (0.34f + 0.2f * height) * fade * flicker),
                        remainingLifetime = 1f, startLifetime = 1f, rotation3D = Vector3.zero,
                    };
                    _starBuffer[n] = new ParticleSystem.Particle
                    {
                        position = f.Position + swing, startSize = 2.4f * flicker, startColor = new Color(1f, 0.96f, 0.85f, fade),
                        remainingLifetime = 1f, startLifetime = 1f,
                    };
                    n++;
                }
                if (trail) _emitters.Trail(f.Position + swing + Vector3.up * 0.5f, 0.9f);
            }
            _flarePools.SetParticles(_poolBuffer, n);
            _stars.SetParticles(_starBuffer, n);
        }

        private static ParticleSystem Manual(Transform root, string name, Material material, ParticleSystemRenderMode mode)
        {
            var ps = PB.Create(root, name, material, mode);
            var main = ps.main;
            main.loop = true;
            main.maxParticles = 8;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            var emission = ps.emission;
            emission.enabled = false;
            var shape = ps.shape;
            shape.enabled = false;
            ps.GetComponent<ParticleSystemRenderer>().maxParticleSize = 10f;
            ps.Play();
            // The particles are set by hand each frame; keep the system from ageing them away.
            main.simulationSpeed = 0f;
            return ps;
        }
    }
}
