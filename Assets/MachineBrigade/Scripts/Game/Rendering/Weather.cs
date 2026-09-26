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
    /// Snow drifts down in the wind; a sandstorm rolls dust clouds and blowing grit through an
    /// orange haze; fog closes in with low wisps; night leaves moonlight, so every fire and
    /// explosion lights up the field. Nothing here touches the simulation.
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
        private readonly ParticleSystem _rain, _splashes, _flakes, _dust, _grit, _wisps;
        private readonly Volume _volume;
        private float _nextLightning = float.MaxValue;
        private readonly float _dim = 1f;
        private float _flashStart = -10f;

        /// <summary>Light, fog and grading of one kind of weather.</summary>
        private readonly struct Mood
        {
            public Mood(float sun, float ambient, Color cast, Color fog, float fogStart, float fogEnd, Color sunTint, float tint,
                float saturation, float exposure, float vignette)
            {
                Sun = sun;
                Ambient = ambient;
                Cast = cast;
                Fog = fog;
                FogStart = fogStart;
                FogEnd = fogEnd;
                SunTint = sunTint;
                Tint = tint;
                Saturation = saturation;
                Exposure = exposure;
                Vignette = vignette;
            }

            public float Sun { get; }
            public float Ambient { get; }
            public Color Cast { get; }
            public Color Fog { get; }
            public float FogStart { get; }
            public float FogEnd { get; }
            public Color SunTint { get; }
            public float Tint { get; }
            public float Saturation { get; }
            public float Exposure { get; }
            public float Vignette { get; }
        }

        private static readonly Color Cool = new(0.86f, 0.92f, 1f);
        private static readonly Color CoolSun = new(0.78f, 0.85f, 0.95f);

        private static Mood MoodOf(WeatherKind kind) => kind switch
        {
            WeatherKind.Overcast => new Mood(0.62f, 0.88f, Cool, new Color(0.33f, 0.38f, 0.41f), 95f, 210f, CoolSun, 0.6f, -14f, -0.1f, 0.22f),
            WeatherKind.Rain => new Mood(0.5f, 0.88f, Cool, new Color(0.33f, 0.38f, 0.41f), 85f, 190f, CoolSun, 0.6f, -14f, -0.1f, 0.22f),
            WeatherKind.Storm => new Mood(0.36f, 0.75f, Cool, new Color(0.2f, 0.24f, 0.27f), 85f, 190f, CoolSun, 0.6f, -22f, -0.25f, 0.3f),
            WeatherKind.Snow => new Mood(0.78f, 0.98f, new Color(0.9f, 0.95f, 1.05f), new Color(0.74f, 0.79f, 0.84f), 70f, 185f,
                new Color(0.85f, 0.9f, 1f), 0.6f, -12f, 0.08f, 0.15f),
            WeatherKind.Sandstorm => new Mood(0.55f, 0.82f, new Color(1.1f, 0.9f, 0.7f), new Color(0.72f, 0.55f, 0.35f), 38f, 125f,
                new Color(1f, 0.72f, 0.45f), 0.7f, -6f, -0.05f, 0.32f),
            WeatherKind.Fog => new Mood(0.7f, 0.92f, new Color(0.92f, 0.96f, 1f), new Color(0.64f, 0.68f, 0.7f), 42f, 118f, CoolSun, 0.5f,
                -18f, 0.02f, 0.18f),
            WeatherKind.Night => new Mood(0.27f, 0.47f, new Color(0.52f, 0.64f, 1f), new Color(0.06f, 0.08f, 0.13f), 95f, 215f,
                new Color(0.55f, 0.66f, 1f), 1f, -10f, -0.04f, 0.34f),
            _ => new Mood(1f, 1f, Color.white, Atmosphere.Haze, 100f, 220f, Color.white, 0f, 0f, 0f, 0f),
        };

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
            var mood = MoodOf(kind);
            _dim = mood.Sun;
            if (kind != WeatherKind.Clear)
            {
                atmosphere.SetMood(mood.Ambient, mood.Cast, mood.Fog, mood.FogStart, mood.FogEnd);
                if (_sun != null)
                {
                    _sun.intensity = _sunIntensity * mood.Sun;
                    _sun.color = Color.Lerp(_sunColour, mood.SunTint, mood.Tint);
                    _sun.shadowStrength = kind == WeatherKind.Night ? 0.6f : Mathf.Lerp(0.85f, 0.45f, 1f - mood.Sun);
                }
                Grade(mood.Saturation, mood.Exposure, mood.Vignette);
            }
            var density = highQuality ? 1f : 0.55f;
            switch (kind)
            {
                case WeatherKind.Snow:
                    _flakes = Snowfall(materials, 1100f * density);
                    _audio.AmbientLevel = 0.18f;
                    for (var i = 0; i < _foliage.Length; i++) _foliage[i].SetFloat("_Wind", _foliageWind[i] * 1.3f);
                    break;
                case WeatherKind.Sandstorm:
                    _dust = DustClouds(materials, 7f * density);
                    _grit = Grit(materials, 1400f * density);
                    _audio.RainLevel = 0.22f; // the hiss of blowing sand
                    _audio.AmbientLevel = 0.5f;
                    for (var i = 0; i < _foliage.Length; i++) _foliage[i].SetFloat("_Wind", _foliageWind[i] * 3f);
                    break;
                case WeatherKind.Fog:
                    _wisps = FogWisps(materials, 4f * density);
                    break;
                case WeatherKind.Night:
                    _audio.AmbientLevel = 0.1f;
                    break;
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
            // Snow, dust and fog volumes follow the view too, upwind so they drift across it.
            if (_flakes != null) _flakes.transform.position = focus + new Vector3(-6f, 20f, -3f);
            if (_dust != null) _dust.transform.position = focus + new Vector3(-40f, 4f, -20f);
            if (_grit != null) _grit.transform.position = focus + new Vector3(-30f, 6f, -15f);
            if (_wisps != null) _wisps.transform.position = focus + new Vector3(-12f, 2f, -6f);

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
            _sun.intensity = _sunIntensity * _dim + flash * 3.5f;
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

        /// <summary>Flakes drifting down and sideways in the wind, swaying as they fall.</summary>
        private ParticleSystem Snowfall(MaterialLibrary m, float rate)
        {
            var ps = PB.Create(_root.transform, "Snowfall", m.Rain);
            var main = ps.main;
            main.loop = true;
            main.duration = 5f;
            main.maxParticles = (int)(rate * 8f);
            main.startLifetime = new ParticleSystem.MinMaxCurve(6f, 8f);
            main.startSpeed = 0f;
            main.startSize = new ParticleSystem.MinMaxCurve(0.14f, 0.28f);
            main.startColor = new Color(0.97f, 0.98f, 1f, 0.9f);
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(120f, 1f, 120f);
            var velocity = ps.velocityOverLifetime;
            velocity.enabled = true;
            velocity.space = ParticleSystemSimulationSpace.World;
            velocity.x = new ParticleSystem.MinMaxCurve(0.8f, 1.8f);
            velocity.y = new ParticleSystem.MinMaxCurve(-3.4f, -2.4f);
            velocity.z = new ParticleSystem.MinMaxCurve(0.3f, 0.9f);
            var noise = ps.noise;
            noise.enabled = true;
            noise.strength = 0.7f;
            noise.frequency = 0.35f;
            noise.quality = ParticleSystemNoiseQuality.Low;
            var emission = ps.emission;
            emission.rateOverTime = rate;
            ps.GetComponent<ParticleSystemRenderer>().maxParticleSize = 0.5f;
            main.prewarm = true;
            ps.Play();
            return ps;
        }

        /// <summary>Big dust clouds rolling low across the field with the gale.</summary>
        private ParticleSystem DustClouds(MaterialLibrary m, float rate)
        {
            var ps = PB.Create(_root.transform, "Dust Clouds", m.Smoke);
            var main = ps.main;
            main.loop = true;
            main.duration = 5f;
            main.maxParticles = (int)(rate * 12f) + 10;
            main.startLifetime = new ParticleSystem.MinMaxCurve(8f, 11f);
            main.startSpeed = 0f;
            main.startSize = new ParticleSystem.MinMaxCurve(9f, 16f);
            main.startColor = new Color(0.78f, 0.6f, 0.4f, 0.34f);
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(40f, 6f, 120f);
            var velocity = ps.velocityOverLifetime;
            velocity.enabled = true;
            velocity.space = ParticleSystemSimulationSpace.World;
            velocity.x = new ParticleSystem.MinMaxCurve(9f, 14f);
            velocity.y = new ParticleSystem.MinMaxCurve(-0.2f, 0.4f);
            velocity.z = new ParticleSystem.MinMaxCurve(3f, 6f);
            PB.Colors(ps, PB.Fade(new Color(0.82f, 0.64f, 0.42f), new Color(0.76f, 0.58f, 0.38f), new Color(0.7f, 0.54f, 0.36f), 0.34f));
            PB.Grow(ps, 0.8f, 1.4f);
            var emission = ps.emission;
            emission.rateOverTime = rate;
            ps.GetComponent<ParticleSystemRenderer>().maxParticleSize = 1.5f;
            main.prewarm = true;
            ps.Play();
            return ps;
        }

        /// <summary>Fine grit streaking past almost horizontally.</summary>
        private ParticleSystem Grit(MaterialLibrary m, float rate)
        {
            var ps = PB.Create(_root.transform, "Grit", m.Rain, ParticleSystemRenderMode.Stretch);
            var main = ps.main;
            main.loop = true;
            main.duration = 5f;
            main.maxParticles = (int)(rate * 3f);
            main.startLifetime = new ParticleSystem.MinMaxCurve(2f, 2.8f);
            main.startSpeed = 0f;
            main.startSize = new ParticleSystem.MinMaxCurve(0.05f, 0.09f);
            main.startColor = new Color(0.85f, 0.7f, 0.5f, 0.45f);
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(60f, 10f, 120f);
            var velocity = ps.velocityOverLifetime;
            velocity.enabled = true;
            velocity.space = ParticleSystemSimulationSpace.World;
            velocity.x = new ParticleSystem.MinMaxCurve(20f, 28f);
            velocity.y = new ParticleSystem.MinMaxCurve(-2.5f, -1f);
            velocity.z = new ParticleSystem.MinMaxCurve(8f, 12f);
            var emission = ps.emission;
            emission.rateOverTime = rate;
            var renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.velocityScale = 0.04f;
            renderer.lengthScale = 1f;
            renderer.maxParticleSize = 1f;
            main.prewarm = true;
            ps.Play();
            return ps;
        }

        /// <summary>
        /// A few huge, faint banks of mist drifting low over the ground. Kept sparse: every bank is
        /// a large transparent quad, and overdraw is what costs on phones.
        /// </summary>
        private ParticleSystem FogWisps(MaterialLibrary m, float rate)
        {
            var ps = PB.Create(_root.transform, "Fog Wisps", m.SoftSmoke);
            var main = ps.main;
            main.loop = true;
            main.duration = 5f;
            main.maxParticles = (int)(rate * 18f) + 10;
            main.startLifetime = new ParticleSystem.MinMaxCurve(13f, 17f);
            main.startSpeed = 0f;
            main.startSize = new ParticleSystem.MinMaxCurve(12f, 20f);
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(100f, 2f, 100f);
            var velocity = ps.velocityOverLifetime;
            velocity.enabled = true;
            velocity.space = ParticleSystemSimulationSpace.World;
            velocity.x = new ParticleSystem.MinMaxCurve(0.8f, 1.6f);
            velocity.y = new ParticleSystem.MinMaxCurve(0f, 0f);
            velocity.z = new ParticleSystem.MinMaxCurve(0.3f, 0.8f);
            PB.Colors(ps, PB.Plume(0.82f, 0.86f, 0.22f));
            PB.Grow(ps, 0.8f, 1.3f);
            var emission = ps.emission;
            emission.rateOverTime = rate;
            ps.GetComponent<ParticleSystemRenderer>().maxParticleSize = 2f;
            main.prewarm = true;
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
