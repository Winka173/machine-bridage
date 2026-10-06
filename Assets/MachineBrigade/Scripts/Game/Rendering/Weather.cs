using System;
using System.Collections.Generic;
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
    /// The match's weather, all visual:
    /// - Overcast dims and cools the light and pulls the fog in.
    /// - Rain adds falling streaks round the camera, splashes, a wet sheen on the ground and its hiss.
    /// - A storm adds heavier rain, gusting foliage, lightning flashes and thunder.
    /// - Snow drifts down in the wind.
    /// - A sandstorm rolls dust clouds and blowing grit through an orange haze.
    /// - Fog closes in with low wisps.
    /// - Night leaves moonlight, so every fire and explosion lights up the field.
    ///
    /// When the weather turns mid-battle, the new weather rolls in over <see cref="TransitionSeconds"/>:
    /// light, fog, colour grading, wet ground, wind in the foliage and the weather's sound all ease
    /// from how the scene looks now to the new look. The old weather's rain or snow thins out while
    /// the new one thickens. Nothing here touches the simulation.
    /// </summary>
    public sealed class Weather : IDisposable
    {
        /// <summary>How long one weather takes to turn into the next.</summary>
        public const float TransitionSeconds = 8f;

        /// <summary>This weather's own roll-in time (and how long the one it replaces takes to thin out).</summary>
        private readonly float _transition;

        private readonly WeatherKind _kind;
        private readonly RtsCamera _camera;
        private readonly AudioDirector _audio;
        private readonly Atmosphere _atmosphere;
        private readonly Light _sun;
        private readonly Material[] _grounds;
        private readonly Material[] _foliage;
        private readonly GameObject _root;
        private readonly ParticleSystem _rain, _splashes, _flakes, _dust, _grit, _wisps;
        private readonly List<(ParticleSystem system, float rate)> _systems = new();
        private readonly Volume _volume;
        private readonly Baseline _base;
        private readonly Look _from, _to;
        private float _blend;
        private float _nextLightning = float.MaxValue;
        private float _flashStart = -10f;
        private ParticleSystemRenderer _rainRenderer;
        private float _retiredAt = -1f;

        /// <summary>The shortest a rain streak is drawn, in seconds of fall.</summary>
        private const float RainStreak = 0.04f;

        /// <summary>The scene before any weather: the map's own clear day, restored when the match ends.</summary>
        private sealed class Baseline
        {
            public float SunIntensity;
            public Color SunColour;
            public float Shadow;
            public float[] GroundRoughness;
            public Color[] GroundColour;
            public float[] FoliageWind;
            public float Saturation, Exposure, Vignette;
        }

        /// <summary>Everything a weather sets that can ease from one weather to the next.</summary>
        private struct Look
        {
            public float Sun, Shadow, Ambient, FogStart, FogEnd, Wet, Wind, Saturation, Exposure, Vignette, RainSound, AirSound;
            public Color SunColour, Cast, Fog;

            public static Look Lerp(in Look a, in Look b, float t) => new()
            {
                Sun = Mathf.Lerp(a.Sun, b.Sun, t),
                Shadow = Mathf.Lerp(a.Shadow, b.Shadow, t),
                Ambient = Mathf.Lerp(a.Ambient, b.Ambient, t),
                FogStart = Mathf.Lerp(a.FogStart, b.FogStart, t),
                FogEnd = Mathf.Lerp(a.FogEnd, b.FogEnd, t),
                Wet = Mathf.Lerp(a.Wet, b.Wet, t),
                Wind = Mathf.Lerp(a.Wind, b.Wind, t),
                Saturation = Mathf.Lerp(a.Saturation, b.Saturation, t),
                Exposure = Mathf.Lerp(a.Exposure, b.Exposure, t),
                Vignette = Mathf.Lerp(a.Vignette, b.Vignette, t),
                RainSound = Mathf.Lerp(a.RainSound, b.RainSound, t),
                AirSound = Mathf.Lerp(a.AirSound, b.AirSound, t),
                SunColour = Color.Lerp(a.SunColour, b.SunColour, t),
                Cast = Color.Lerp(a.Cast, b.Cast, t),
                Fog = Color.Lerp(a.Fog, b.Fog, t),
            };
        }

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

        /// <param name="clearCast">The map's own light on a clear day (its theme's cast), which Clear eases back to.</param>
        /// <param name="clearHaze">The map's own haze on a clear day.</param>
        /// <param name="previous">The weather this one replaces: it rolls in from how that one looks now.</param>
        /// <param name="seconds">How long the roll-in takes (prompt 23 D.9: a mission event's 20-30 s; 0: <see cref="TransitionSeconds"/>).</param>
        /// <summary>MVA W2-B: this weather's presentation metadata (Sim.Navigation.WeatherPresentation, W1-A).</summary>
        public Sim.Navigation.WeatherPresentation Presentation { get; }

        /// <summary>
        /// MVA W2-B (spec part Q1): the muzzle flashes' size factor in this weather (night a little brighter, a sandstorm a
        /// little more); MuzzleFx keeps Reduced flashes under 1 whatever the weather.
        /// </summary>
        public static float FlashVisibility { get; private set; } = 1f;

        public Weather(WeatherKind kind, Atmosphere atmosphere, MaterialLibrary materials, RtsCamera camera, AudioDirector audio,
            Transform parent, bool highQuality, Color clearCast, Color clearHaze, Weather previous = null, float seconds = 0f)
        {
            _kind = kind;
            _transition = seconds > 0f ? seconds : TransitionSeconds;
            _camera = camera;
            _audio = audio;
            // MVA W2-B (spec part Q): the weather's presentation metadata (W1-A), view and audio only; visibility stays the
            // campaign's weatherSight. The audio damps its tails, the warnings get the weather's telegraph boost.
            Presentation = Sim.Navigation.WeatherPresentation.Of(kind.ToString());
            if (_audio != null) _audio.WeatherLook = Presentation;
            GroundMark.TelegraphBoost = Presentation.TelegraphBoost;
            FlashVisibility = Mathf.Clamp(1f + (Presentation.MuzzleFlashVisibility - 1f) * 0.35f, 0.85f, 1.2f);
            _atmosphere = atmosphere;
            foreach (var light in Object.FindObjectsByType<Light>())
                if (light.type == LightType.Directional) _sun = light;
            _grounds = new[] { materials.Ground, materials.OuterGround };
            _foliage = new[] { materials.GrassTuft, materials.ForModel("Foliage", -1), materials.ForModel("FoliageLight", -1) };
            foreach (var v in Object.FindObjectsByType<Volume>()) _volume = v;
            // The clear-day scene is read once, before the first weather touches it; later weathers inherit it.
            _base = previous?._base ?? CaptureBaseline();
            _to = LookOf(kind, clearCast, clearHaze);
            _from = previous != null ? previous.Current : _to;
            _replaced = previous != null;
            _blend = previous != null ? 0f : 1f;

            _root = new GameObject("Weather");
            _root.transform.SetParent(parent, false);
            var density = highQuality ? 1f : 0.55f;
            switch (kind)
            {
                case WeatherKind.Snow:
                    _flakes = Keep(Snowfall(materials, 1100f * density), 1100f * density);
                    break;
                case WeatherKind.Sandstorm:
                    _dust = Keep(DustClouds(materials, 7f * density), 7f * density);
                    _grit = Keep(Grit(materials, 1400f * density), 1400f * density);
                    break;
                case WeatherKind.Fog:
                    _wisps = Keep(FogWisps(materials, 4f * density), 4f * density);
                    break;
            }
            if (kind is WeatherKind.Rain or WeatherKind.Storm)
            {
                var heavy = kind == WeatherKind.Storm;
                var rate = (heavy ? 2800f : 1800f) * density;
                _rain = Keep(RainSystem(materials, rate, heavy), rate);
                _splashes = Keep(SplashSystem(materials, rate * 0.35f), rate * 0.35f);
            }
            if (kind == WeatherKind.Storm) _nextLightning = Time.time + Random.Range(4f, 9f) + (previous != null ? _transition * 0.5f : 0f);
            previous?.Retire(_transition);
            Apply(Look.Lerp(_from, _to, Ease(_blend)));
            SetRates(_blend);
        }

        /// <summary>This weather's look at this moment (a transition in progress included).</summary>
        private Look Current => Look.Lerp(_from, _to, Ease(_blend));

        private static float Ease(float t) => t * t * (3f - 2f * t);

        /// <summary>The rain loop's level for a weather (play-test 6: under the music; 0.5, 0.35 and 0.22 before).</summary>
        internal static float RainLevel(WeatherKind kind) => kind switch
        {
            WeatherKind.Storm => 0.18f,
            WeatherKind.Rain => 0.15f,
            WeatherKind.Sandstorm => 0.1f,
            _ => 0f,
        };

        /// <summary>The wind loop's level for a weather (play-test 6: under the music; 0.4, 0.24, 0.5, 0.18, 0.1 and 0.16 before).</summary>
        internal static float AirLevel(WeatherKind kind) => kind switch
        {
            WeatherKind.Storm => 0.14f,
            WeatherKind.Rain => 0.12f,
            WeatherKind.Sandstorm => 0.2f,
            WeatherKind.Snow => 0.1f,
            WeatherKind.Night => 0.07f,
            _ => 0.1f,
        };

        private ParticleSystem Keep(ParticleSystem system, float rate)
        {
            _systems.Add((system, rate));
            return system;
        }

        private Baseline CaptureBaseline()
        {
            var b = new Baseline
            {
                SunIntensity = _sun != null ? _sun.intensity : 1f,
                SunColour = _sun != null ? _sun.color : Color.white,
                Shadow = _sun != null ? _sun.shadowStrength : 1f,
                GroundRoughness = Array.ConvertAll(_grounds, g => g.GetFloat("_Roughness")),
                GroundColour = Array.ConvertAll(_grounds, g => g.GetColor("_BaseColor")),
                FoliageWind = Array.ConvertAll(_foliage, m => m.GetFloat("_Wind")),
            };
            if (_volume != null)
            {
                var profile = _volume.profile; // instantiates a copy, leaving the asset untouched
                if (profile.TryGet<ColorAdjustments>(out var colour))
                {
                    b.Saturation = colour.saturation.value;
                    b.Exposure = colour.postExposure.value;
                }
                if (profile.TryGet<Vignette>(out var edge)) b.Vignette = edge.intensity.value;
            }
            return b;
        }

        private Look LookOf(WeatherKind kind, Color clearCast, Color clearHaze)
        {
            var mood = MoodOf(kind);
            var clear = kind == WeatherKind.Clear;
            var wet = kind is WeatherKind.Rain or WeatherKind.Storm;
            return new Look
            {
                Sun = _base.SunIntensity * mood.Sun,
                SunColour = Color.Lerp(_base.SunColour, mood.SunTint, mood.Tint),
                Shadow = clear ? _base.Shadow : kind == WeatherKind.Night ? 0.6f : Mathf.Lerp(0.85f, 0.45f, 1f - mood.Sun),
                Ambient = mood.Ambient,
                Cast = clear ? clearCast : mood.Cast,
                Fog = clear ? clearHaze : mood.Fog,
                FogStart = mood.FogStart,
                FogEnd = mood.FogEnd,
                Wet = wet ? 1f : 0f,
                Wind = kind switch
                {
                    WeatherKind.Snow => 1.3f,
                    WeatherKind.Sandstorm => 3f,
                    WeatherKind.Rain => 1.6f,
                    WeatherKind.Storm => 2.6f,
                    _ => 1f,
                },
                Saturation = _base.Saturation + mood.Saturation,
                Exposure = _base.Exposure + mood.Exposure,
                Vignette = clear ? _base.Vignette : mood.Vignette,
                // The rain loop is also the hiss of blowing sand. Play-test 6: the rain drowned the music (the music plays
                // at about 0.34), so the weather now sits under it: rain and wind together below the music.
                RainSound = RainLevel(kind),
                AirSound = AirLevel(kind),
            };
        }

        private void Apply(in Look look)
        {
            _atmosphere.SetMood(look.Ambient, look.Cast, look.Fog, look.FogStart, look.FogEnd);
            if (_sun != null)
            {
                _sun.intensity = look.Sun;
                _sun.color = look.SunColour;
                _sun.shadowStrength = look.Shadow;
            }
            // Wet ground: darker and glossier.
            for (var i = 0; i < _grounds.Length; i++)
            {
                _grounds[i].SetFloat("_Roughness", Mathf.Lerp(_base.GroundRoughness[i], 0.42f, look.Wet));
                _grounds[i].SetColor("_BaseColor", _base.GroundColour[i] * Mathf.Lerp(1f, 0.82f, look.Wet));
            }
            for (var i = 0; i < _foliage.Length; i++) _foliage[i].SetFloat("_Wind", _base.FoliageWind[i] * look.Wind);
            if (_volume != null)
            {
                var profile = _volume.profile;
                if (profile.TryGet<ColorAdjustments>(out var colour))
                {
                    colour.saturation.Override(look.Saturation);
                    colour.postExposure.Override(look.Exposure);
                }
                if (profile.TryGet<Vignette>(out var edge)) edge.intensity.Override(look.Vignette);
            }
            _audio.RainLevel = look.RainSound;
            _audio.AmbientLevel = look.AirSound;
        }

        /// <summary>This weather's particles at a share of their full rate (thickening as it rolls in).</summary>
        private void SetRates(float share)
        {
            foreach (var (system, rate) in _systems)
            {
                var emission = system.emission;
                emission.rateOverTime = rate * share;
            }
        }

        /// <summary>Replaced by the next weather: its particles thin out and it lets go of the scene.</summary>
        private void Retire(float seconds)
        {
            _leavingFor = seconds;
            _retiredAt = Time.time;
            _nextLightning = float.MaxValue;
        }

        private float _leavingFor = TransitionSeconds;

        /// <summary>A replaced weather thinning out; false once its last drops have fallen (then dispose it).</summary>
        public bool TickLeaving()
        {
            Follow();
            var t = (Time.time - _retiredAt) / (_leavingFor * 0.7f);
            SetRates(Mathf.Clamp01(1f - t));
            return t < 1.5f;
        }

        /// <summary>
        /// Prompt 31 L5: how much of this weather the view stands in (1: all of it). The sandstorm that rolls over one half of
        /// the map (SimWorld.StormSight) sets it low while the camera looks at the other half: the dust thins there and the
        /// look eases back towards the weather it replaced. Eased over <see cref="PresenceSeconds"/>.
        /// </summary>
        public float Presence { get; set; } = 1f;

        private float _presence = 1f;
        private const float PresenceSeconds = 2.5f;

        /// <summary>Prompt 31 L5: this weather rolled in over another one (which <see cref="Presence"/> eases back towards).</summary>
        public bool Replaced => _replaced;

        private readonly bool _replaced;

        public void Tick()
        {
            Follow();
            var target = Mathf.Clamp01(Presence);
            var shifting = Mathf.Abs(target - _presence) > 0.001f;
            if (shifting) _presence = Mathf.MoveTowards(_presence, target, Time.deltaTime / PresenceSeconds);
            if (_blend < 1f || shifting)
            {
                if (_blend < 1f) _blend = Mathf.Min(1f, _blend + Time.deltaTime / _transition);
                Apply(_presence >= 0.999f ? Current : Look.Lerp(_from, Current, _presence));
                SetRates(Ease(_blend) * _presence);
            }

            if (_kind != WeatherKind.Storm || _sun == null) return;
            if (Time.time >= _nextLightning)
            {
                _nextLightning = Time.time + Random.Range(6f, 15f);
                _flashStart = Time.time;
                _audio.Thunder(Random.Range(0.4f, 2.2f));
            }
            // One bright flash that dies away smoothly, with a softer after-glow: no strobing flicker.
            var ft = Time.time - _flashStart;
            var flash = ft < 0f ? 0f : Mathf.Exp(-ft * 9f) + 0.35f * Mathf.Exp(-Mathf.Abs(ft - 0.22f) * 14f) * (ft < 0.6f ? 1f : 0f);
            // MVA W2-B (spec parts AL, Q): the flash by the weather's lightning intensity; Reduced flashes keeps a third of it.
            var strength = Mathf.Lerp(0.6f, 1f, Mathf.Clamp01(Presentation.LightningIntensity)) * (Match.MatchSettings.ReducedFlash ? 0.33f : 1f);
            _sun.intensity = Current.Sun + Mathf.Clamp01(flash) * 3f * strength;
        }

        /// <summary>The weather's particle volumes follow the view.</summary>
        private void Follow()
        {
            var focus = _camera.Focus;
            if (_rain != null)
            {
                // The rain volume follows the view; drops are simulated in world space.
                _rain.transform.position = focus + new Vector3(0f, 26f, 0f);
                _splashes.transform.position = focus + Vector3.up * 0.1f;
                // Each streak is as long as the way its drop falls in one frame (a little more), so
                // a drop's streaks in consecutive frames touch: the rain reads as falling, not as
                // strobing dashes, at 30 fps or 60 alike.
                var frame = Mathf.Clamp(Time.smoothDeltaTime, 1f / 120f, 1f / 20f);
                _rainRenderer.velocityScale = Mathf.Max(RainStreak, frame * 1.25f);
            }
            // Snow, dust and fog volumes follow the view too, upwind so they drift across it.
            if (_flakes != null) _flakes.transform.position = focus + new Vector3(-6f, 20f, -3f);
            if (_dust != null) _dust.transform.position = focus + new Vector3(-40f, 4f, -20f);
            if (_grit != null) _grit.transform.position = focus + new Vector3(-30f, 6f, -15f);
            if (_wisps != null) _wisps.transform.position = focus + new Vector3(-12f, 2f, -6f);
        }

        /// <summary>
        /// Ends the weather. The current one puts the clear-day scene back; a replaced one only
        /// removes its particles, since the weather that replaced it owns the scene now.
        /// </summary>
        public void Dispose()
        {
            if (_retiredAt < 0f)
            {
                if (_sun != null)
                {
                    _sun.intensity = _base.SunIntensity;
                    _sun.color = _base.SunColour;
                    _sun.shadowStrength = _base.Shadow;
                }
                for (var i = 0; i < _grounds.Length; i++)
                {
                    _grounds[i].SetFloat("_Roughness", _base.GroundRoughness[i]);
                    _grounds[i].SetColor("_BaseColor", _base.GroundColour[i]);
                }
                for (var i = 0; i < _foliage.Length; i++) _foliage[i].SetFloat("_Wind", _base.FoliageWind[i]);
            }
            if (_root != null) Object.Destroy(_root);
        }

        private ParticleSystem RainSystem(MaterialLibrary m, float rate, bool heavy)
        {
            var ps = PB.Create(_root.transform, "Rain", m.Rain, ParticleSystemRenderMode.Stretch);
            var main = ps.main;
            main.loop = true;
            main.duration = 5f;
            main.maxParticles = (int)(rate * 1.2f);
            // 24 m/s from 26 m up: each drop lands in just over a second.
            main.startLifetime = new ParticleSystem.MinMaxCurve(1.05f, 1.15f);
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
            velocity.y = new ParticleSystem.MinMaxCurve(-24f);
            velocity.z = new ParticleSystem.MinMaxCurve(heavy ? 3f : 1.5f);
            var emission = ps.emission;
            emission.rateOverTime = rate;
            var renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.velocityScale = RainStreak;
            renderer.lengthScale = 1f;
            renderer.maxParticleSize = 1f;
            _rainRenderer = renderer;
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
