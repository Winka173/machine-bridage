#nullable enable
using System;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// Map spec Q (lane W1-A): a weather's presentation metadata (maps.weatherPresentation.&lt;weather&gt;) for the view and the
    /// audio. Never a gameplay value: visibility stays campaign.json eventLibrary.rules.weatherSight, accuracy and damage are
    /// untouched. <see cref="TelegraphBoost"/> is the least boost a danger telegraph gets so it never vanishes in that weather
    /// (spec Q1); the audio profile ids follow the naming rule amb_weather_&lt;weather&gt; and the reverb families below.
    /// </summary>
    public readonly struct WeatherPresentation
    {
        private WeatherPresentation(string weather, float[] v)
        {
            Weather = weather;
            float At(int i) => i < v.Length ? v[i] : 0f;
            FogDensity = At(0);
            AmbientLight = At(1);
            Cloudiness = At(2);
            RainIntensity = At(3);
            SnowIntensity = At(4);
            WindStrength = At(5);
            WindDirectionDeg = At(6);
            LightningIntensity = At(7);
            DustIntensity = At(8);
            ContrailVisibility = At(9);
            MuzzleFlashVisibility = At(10);
            LowpassEnvironmentAmount = At(11);
            TelegraphBoost = Math.Max(1f, At(12));
        }

        /// <summary>The weathers with presentation metadata (the game's WeatherKind names, Random excepted).</summary>
        public static readonly string[] Kinds = { "Clear", "Overcast", "Rain", "Storm", "Snow", "Sandstorm", "Fog", "Night" };

        public string Weather { get; }
        public float FogDensity { get; }
        public float AmbientLight { get; }
        public float Cloudiness { get; }
        public float RainIntensity { get; }
        public float SnowIntensity { get; }
        public float WindStrength { get; }
        public float WindDirectionDeg { get; }
        public float LightningIntensity { get; }
        public float DustIntensity { get; }
        public float ContrailVisibility { get; }
        public float MuzzleFlashVisibility { get; }
        public float LowpassEnvironmentAmount { get; }
        public float TelegraphBoost { get; }

        public string AmbientAudioProfile => "amb_weather_" + Weather.ToLowerInvariant();

        public string ReverbProfile => Weather switch
        {
            "Rain" or "Storm" => "reverb_wet",
            "Snow" or "Fog" => "reverb_damped",
            "Sandstorm" => "reverb_dust",
            _ => "reverb_open",
        };

        /// <summary>The metadata of a weather by name (case-insensitive); unknown names read as Clear.</summary>
        public static WeatherPresentation Of(string weather)
        {
            foreach (var k in Kinds)
                if (string.Equals(k, weather, StringComparison.OrdinalIgnoreCase))
                    return new WeatherPresentation(k, k switch
                    {
                        "Overcast" => SimTunables.Maps.WeatherPresentation.Overcast,
                        "Rain" => SimTunables.Maps.WeatherPresentation.Rain,
                        "Storm" => SimTunables.Maps.WeatherPresentation.Storm,
                        "Snow" => SimTunables.Maps.WeatherPresentation.Snow,
                        "Sandstorm" => SimTunables.Maps.WeatherPresentation.Sandstorm,
                        "Fog" => SimTunables.Maps.WeatherPresentation.Fog,
                        "Night" => SimTunables.Maps.WeatherPresentation.Night,
                        _ => SimTunables.Maps.WeatherPresentation.Clear,
                    });
            return new WeatherPresentation("Clear", SimTunables.Maps.WeatherPresentation.Clear);
        }
    }
}
