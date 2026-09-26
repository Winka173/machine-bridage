using System;
using MachineBrigade.Game.Audio;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Match;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;
using Random = UnityEngine.Random;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// The match's weather, all visual: an overcast sky dims and cools the light and pulls the
    /// fog in; rain adds falling streaks around the camera, splashes, a wet sheen on the ground
    /// and its hiss; storms add heavier rain, gusting foliage, lightning flashes and thunder.
    /// Nothing here touches the simulation.
    /// </summary>
    public sealed class Weather : IDisposable
    {
        private readonly WeatherKind _kind;
        private readonly RtsCamera _camera;
        private readonly AudioDirector _audio;
        private readonly Light _sun;
        private readonly float _sunIntensity;
        private readonly Color _sunColour;
        private readonly Material[] _grounds;
        private readonly float[] _groundRoughness;
        private readonly Color[] _groundColour;
        private readonly Material[] _foliage;
        private readonly float[] _foliageWind;
        private readonly GameObject _root;
        private readonly ParticleSystem _rain, _splashes;
        private readonly Volume _volume;
        private float _nextLightning = float.MaxValue;
        private float _flashStart = -10f;

        public Weather(WeatherKind kind, Atmosphere atmosphere, MaterialLibrary materials, RtsCamera camera, AudioDirector audio,
            Transform parent, bool highQuality)
        {
            _kind = kind;
            _camera = camera;
            _audio = audio;
            foreach (var light in Object.FindObjectsByType<Light>())
                if (light.type == LightType.Directional) _sun = light;
            if (_sun != null)
            {
                _sunIntensity = _sun.intensity;
                _sunColour = _sun.color;
            }
            _grounds = new[] { materials.Ground, materials.OuterGround };
            _groundRoughness = Array.ConvertAll(_grounds, g => g.GetFloat("_Roughness"));
            _groundColour = Array.ConvertAll(_grounds, g => g.GetColor("_BaseColor"));
            _foliage = new[] { materials.GrassTuft, materials.ForModel("Foliage", -1), materials.ForModel("FoliageLight", -1) };
            _foliageWind = Array.ConvertAll(_foliage, m => m.GetFloat("_Wind"));
            foreach (var v in Object.FindObjectsByType<Volume>()) _volume = v;

            _root = new GameObject("Weather");
            _root.transform.SetParent(parent, false);

            var wet = kind is WeatherKind.Rain or WeatherKind.Storm;
            var dim = kind switch { WeatherKind.Overcast => 0.62f, WeatherKind.Rain => 0.5f, WeatherKind.Storm => 0.36f, _ => 1f };
            if (kind != WeatherKind.Clear)
            {
                var cast = new Color(0.86f, 0.92f, 1f);
                var fog = kind == WeatherKind.Storm ? new Color(0.2f, 0.24f, 0.27f) : new Color(0.33f, 0.38f, 0.41f);
                atmosphere.SetMood(kind == WeatherKind.Storm ? 0.75f : 0.88f, cast, fog, wet ? 85f : 95f, wet ? 190f : 210f);
                if (_sun != null)
                {
                    _sun.intensity = _sunIntensity * dim;
                    _sun.color = Color.Lerp(_sunColour, new Color(0.78f, 0.85f, 0.95f), 0.6f);
                    _sun.shadowStrength = Mathf.Lerp(0.85f, 0.45f, 1f - dim);
                }
                Grade(kind == WeatherKind.Storm ? -22f : -14f, kind == WeatherKind.Storm ? -0.25f : -0.1f, kind == WeatherKind.Storm ? 0.3f : 0.22f);
            }
            if (wet)
            {
                // Wet ground: darker and glossier.
                for (var i = 0; i < _grounds.Length; i++)
                {
                    _grounds[i].SetFloat("_Roughness", 0.42f);
                    _grounds[i].SetColor("_BaseColor", _groundColour[i] * 0.82f);
                }
                var heavy = kind == WeatherKind.Storm;
                var rate = (heavy ? 3800f : 2000f) * (highQuality ? 1f : 0.55f);
                _rain = RainSystem(materials, rate, heavy);
                _splashes = SplashSystem(materials, rate * 0.35f);
                _audio.RainLevel = heavy ? 0.5f : 0.35f;
                _audio.AmbientLevel = heavy ? 0.4f : 0.24f;
                for (var i = 0; i < _foliage.Length; i++) _foliage[i].SetFloat("_Wind", _foliageWind[i] * (heavy ? 2.6f : 1.6f));
            }
            if (kind == WeatherKind.Storm) _nextLightning = Time.time + Random.Range(4f, 9f);
        }

        public void Tick()
        {
            var focus = _camera.Focus;
            if (_rain != null)
            {
                // The rain volume follows the view; drops are simulated in world space.
                _rain.transform.position = focus + new Vector3(0f, 26f, 0f);
                _splashes.transform.position = focus + Vector3.up * 0.1f;
            }

            if (_kind != WeatherKind.Storm || _sun == null) return;
            if (Time.time >= _nextLightning)
            {
                _nextLightning = Time.time + Random.Range(6f, 15f);
                _flashStart = Time.time;
                _audio.Thunder(Random.Range(0.4f, 2.2f));
            }
            // Two quick flickers, then the storm light returns.
            var t = Time.time - _flashStart;
            var flash = t < 0.35f ? (t < 0.07f || (t > 0.14f && t < 0.2f) ? 1f : 0.25f) * (1f - t / 0.35f) : 0f;
            _sun.intensity = _sunIntensity * 0.36f + flash * 3.5f;
        }

        public void Dispose()
        {
            if (_sun != null)
            {
                _sun.intensity = _sunIntensity;
                _sun.color = _sunColour;
            }
            for (var i = 0; i < _grounds.Length; i++)
            {
                _grounds[i].SetFloat("_Roughness", _groundRoughness[i]);
                _grounds[i].SetColor("_BaseColor", _groundColour[i]);
            }
            for (var i = 0; i < _foliage.Length; i++) _foliage[i].SetFloat("_Wind", _foliageWind[i]);
            if (_root != null) Object.Destroy(_root);
        }

        /// <summary>Colour grading for dull weather, on a per-match copy of the volume profile.</summary>
        private void Grade(float saturation, float exposure, float vignette)
        {
            if (_volume == null) return;
            var profile = _volume.profile; // instantiates a copy, leaving the asset untouched
            if (profile.TryGet<ColorAdjustments>(out var colour))
            {
                colour.saturation.Override(colour.saturation.value + saturation);
                colour.postExposure.Override(colour.postExposure.value + exposure);
            }
            if (profile.TryGet<Vignette>(out var edge)) edge.intensity.Override(vignette);
        }

        private ParticleSystem RainSystem(MaterialLibrary m, float rate, bool heavy)
        {
            var ps = PB.Create(_root.transform, "Rain", m.Rain, ParticleSystemRenderMode.Stretch);
            var main = ps.main;
            main.loop = true;
            main.duration = 5f;
            main.maxParticles = (int)(rate * 1.2f);
            main.startLifetime = new ParticleSystem.MinMaxCurve(0.85f, 1.0f);
            main.startSpeed = 0f;
            main.startSize = new ParticleSystem.MinMaxCurve(0.05f, 0.08f);
            main.startColor = new Color(0.78f, 0.84f, 0.9f, heavy ? 0.5f : 0.38f);
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(110f, 1f, 110f);
            var velocity = ps.velocityOverLifetime;
            velocity.enabled = true;
            velocity.space = ParticleSystemSimulationSpace.World;
            velocity.x = new ParticleSystem.MinMaxCurve(heavy ? 6f : 3f);
            velocity.y = new ParticleSystem.MinMaxCurve(-30f);
            velocity.z = new ParticleSystem.MinMaxCurve(heavy ? 3f : 1.5f);
            var emission = ps.emission;
            emission.rateOverTime = rate;
            var renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.velocityScale = 0.035f;
            renderer.lengthScale = 1f;
            renderer.maxParticleSize = 1f;
            ps.Play();
            return ps;
        }

        private ParticleSystem SplashSystem(MaterialLibrary m, float rate)
        {
            var ps = PB.Create(_root.transform, "Splashes", m.Splash);
            var main = ps.main;
            main.loop = true;
            main.duration = 5f;
            main.maxParticles = (int)(rate * 0.5f) + 50;
            PB.Basics(ps, new Vector2(0.2f, 0.3f), Vector2.zero, new Vector2(0.25f, 0.45f));
            main.startColor = new Color(0.85f, 0.9f, 0.95f, 0.45f);
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(90f, 0f, 90f);
            PB.Grow(ps, 0.2f, 1.4f);
            PB.Colors(ps, PB.Fade(Color.white, Color.white, Color.white, 0.5f));
            var renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.renderMode = ParticleSystemRenderMode.HorizontalBillboard;
            var emission = ps.emission;
            emission.rateOverTime = rate;
            ps.Play();
            return ps;
        }
    }
}
