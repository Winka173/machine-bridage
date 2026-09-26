using System;
using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.AI;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    public enum GameModeKind
    {
        Conquest,
        Survival,
    }

    public enum WeatherKind
    {
        Clear,
        Overcast,
        Rain,
        Storm,
        Random,
        Snow,
        Sandstorm,
        Fog,
        Night,
    }

    /// <summary>A battlefield the menu offers: data files are Data/maps/{Id}_conquest and {Id}_sandbox.</summary>
    public readonly struct MapInfo
    {
        public MapInfo(string id, string theme, string icon, WeatherKind[] weathers)
        {
            Id = id;
            Theme = theme;
            Icon = icon;
            Weathers = weathers;
        }

        public string Id { get; }

        /// <summary>temperate, desert, snow or harbor: picks ground, scenery and palettes.</summary>
        public string Theme { get; }

        public string Icon { get; }

        /// <summary>The weather Random draws from on this map (first entries most often).</summary>
        public WeatherKind[] Weathers { get; }
    }

    /// <summary>Graphics setting; Auto picks a tier from the device.</summary>
    public enum GraphicsQuality
    {
        Auto,
        Low,
        Medium,
        High,
    }

    public enum LanguageChoice
    {
        Auto,
        English,
        Vietnamese,
    }

    /// <summary>
    /// What the next match should be (chosen in the menu) and the player's settings. The match
    /// choice lives for the session; settings and the deck are saved with PlayerPrefs, so they
    /// survive restarts. Scene reloads read from here, which keeps every match a clean restart.
    /// </summary>
    public static class MatchSettings
    {
        public const int DeckVehicleSlots = 8;
        public const int DeckSupportSlots = 2;

        /// <summary>Saved-deck format: 2 since decks hold 8 vehicles.</summary>
        private const int DeckVersion = 2;

        public static readonly string[] AllVehicles =
        {
            "scout_jeep", "armored_car", "rocket_technical", "apc", "light_tank", "main_battle_tank", "heavy_tank",
            "tank_destroyer", "flame_tank", "mortar_carrier", "artillery", "mlrs", "aa_vehicle", "sam_launcher",
            "scout_heli", "attack_helicopter", "gunship_heli", "strike_drone", "attack_jet",
        };

        public static readonly string[] AllSupports = { "artillery_barrage", "airstrike", "cruise_missile", "smoke_screen", "repair_drop" };

        private static readonly string[] DefaultVehicles =
        {
            "apc", "light_tank", "main_battle_tank", "heavy_tank", "aa_vehicle", "attack_helicopter", "gunship_heli", "attack_jet",
        };
        private static readonly string[] DefaultSupports = { "artillery_barrage", "airstrike" };

        private static bool _loaded;

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            _loaded = false;
            InMatch = false;
        }

        /// <summary>False shows the menu over an AI-versus-AI battle; true plays the chosen match.</summary>
        public static bool InMatch { get; set; }

        public static GameModeKind Mode { get; set; } = GameModeKind.Conquest;

        public static readonly MapInfo[] AllMaps =
        {
            new("ashfield", "temperate", "pine",
                new[] { WeatherKind.Clear, WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Storm, WeatherKind.Fog, WeatherKind.Night }),
            new("dunebreak", "desert", "dune",
                new[] { WeatherKind.Clear, WeatherKind.Clear, WeatherKind.Sandstorm, WeatherKind.Overcast, WeatherKind.Night }),
            new("frostpeak", "snow", "snow",
                new[] { WeatherKind.Snow, WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Fog, WeatherKind.Night }),
            new("ironport", "harbor", "anchor",
                new[] { WeatherKind.Clear, WeatherKind.Overcast, WeatherKind.Rain, WeatherKind.Storm, WeatherKind.Fog, WeatherKind.Night }),
        };

        public static string Map { get; set; } = "ashfield";

        public static MapInfo CurrentMap
        {
            get
            {
                foreach (var map in AllMaps)
                    if (map.Id == Map && MapAvailable(map.Id)) return map;
                return AllMaps[0];
            }
        }

        public static bool MapAvailable(string id) => Resources.Load<TextAsset>("Data/maps/" + id + "_conquest") != null;
        public static AiDifficulty Difficulty { get; set; } = AiDifficulty.Normal;
        public static WeatherKind Weather { get; set; } = WeatherKind.Random;

        public static List<string> DeckVehicles { get; } = new(DefaultVehicles);
        public static List<string> DeckSupports { get; } = new(DefaultSupports);

        public static float Volume { get; set; } = 0.8f;
        public static GraphicsQuality Graphics { get; set; } = GraphicsQuality.Auto;

        /// <summary>
        /// The tier in force: the player's choice, or one picked from the device (memory and CPU
        /// cores, the usual proxies for GPU class on Android). Explosions and fires are never cut;
        /// tiers change resolution, anti-aliasing, shadows, bloom and far scenery.
        /// </summary>
        public static GraphicsQuality Tier => Graphics != GraphicsQuality.Auto ? Graphics : DetectTier();

        public static bool HighQuality => Tier == GraphicsQuality.High;

        public static GraphicsQuality DetectTier()
        {
            if (!Application.isMobilePlatform) return GraphicsQuality.High;
            var memory = SystemInfo.systemMemorySize;
            var cores = SystemInfo.processorCount;
            if (memory >= 7000 && cores >= 8) return GraphicsQuality.High;
            if (memory >= 3500 && cores >= 6) return GraphicsQuality.Medium;
            return GraphicsQuality.Low;
        }
        public static bool ReducedMotion { get; set; }
        public static bool ShowFps { get; set; }
        public static LanguageChoice Language { get; set; } = LanguageChoice.Auto;

        /// <summary>The commander AI buys vehicles from the deck.</summary>
        public static bool AutoDeploy { get; set; } = true;

        /// <summary>The commander AI calls fire support.</summary>
        public static bool AutoStrike { get; set; } = true;

        public static void Load()
        {
            if (_loaded) return;
            _loaded = true;
            try
            {
                Volume = PlayerPrefs.GetFloat("mb.volume", Volume);
                Graphics = (GraphicsQuality)Mathf.Clamp(PlayerPrefs.GetInt("mb.graphics", 0), 0, 3);
                Map = PlayerPrefs.GetString("mb.map", Map);
                ReducedMotion = PlayerPrefs.GetInt("mb.reducedMotion", 0) == 1;
                ShowFps = PlayerPrefs.GetInt("mb.fps", 0) == 1;
                Language = (LanguageChoice)PlayerPrefs.GetInt("mb.language", 0);
                Difficulty = (AiDifficulty)PlayerPrefs.GetInt("mb.difficulty", (int)AiDifficulty.Normal);
                Weather = (WeatherKind)PlayerPrefs.GetInt("mb.weather", (int)WeatherKind.Random);
                Mode = (GameModeKind)PlayerPrefs.GetInt("mb.mode", 0);
                AutoDeploy = PlayerPrefs.GetInt("mb.autoDeploy", 1) == 1;
                AutoStrike = PlayerPrefs.GetInt("mb.autoStrike", 1) == 1;
                ReadDeck("mb.deck.vehicles", DeckVehicles, AllVehicles, DefaultVehicles, DeckVehicleSlots);
                ReadDeck("mb.deck.supports", DeckSupports, AllSupports, DefaultSupports, DeckSupportSlots);
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[MatchSettings] Could not read settings: {e.Message}");
            }
            ApplyLanguage();
        }

        public static void Save()
        {
            // An empty deck would mean "anything" to the simulation; refill it instead.
            if (DeckVehicles.Count == 0) DeckVehicles.AddRange(DefaultVehicles);
            if (DeckSupports.Count == 0) DeckSupports.AddRange(DefaultSupports);
            try
            {
                PlayerPrefs.SetFloat("mb.volume", Volume);
                PlayerPrefs.SetInt("mb.graphics", (int)Graphics);
                PlayerPrefs.SetString("mb.map", Map);
                PlayerPrefs.SetInt("mb.reducedMotion", ReducedMotion ? 1 : 0);
                PlayerPrefs.SetInt("mb.fps", ShowFps ? 1 : 0);
                PlayerPrefs.SetInt("mb.language", (int)Language);
                PlayerPrefs.SetInt("mb.difficulty", (int)Difficulty);
                PlayerPrefs.SetInt("mb.weather", (int)Weather);
                PlayerPrefs.SetInt("mb.mode", (int)Mode);
                PlayerPrefs.SetInt("mb.autoDeploy", AutoDeploy ? 1 : 0);
                PlayerPrefs.SetInt("mb.autoStrike", AutoStrike ? 1 : 0);
                PlayerPrefs.SetString("mb.deck.vehicles", string.Join(",", DeckVehicles));
                PlayerPrefs.SetString("mb.deck.supports", string.Join(",", DeckSupports));
                PlayerPrefs.SetInt("mb.deck.version", DeckVersion);
                PlayerPrefs.Save();
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[MatchSettings] Could not save settings: {e.Message}");
            }
            ApplyLanguage();
        }

        /// <summary>Picks the weather for this match, resolving Random.</summary>
        public static WeatherKind ResolveWeather(int seed)
        {
            if (Weather != WeatherKind.Random) return Weather;
            var choices = CurrentMap.Weathers;
            return choices[new System.Random(seed).Next(choices.Length)];
        }

        public static void ApplyLanguage()
        {
            Strings.Vietnamese = Language switch
            {
                LanguageChoice.English => false,
                LanguageChoice.Vietnamese => true,
                _ => Application.systemLanguage == SystemLanguage.Vietnamese,
            };
        }

        private static void ReadDeck(string key, List<string> deck, string[] all, string[] defaults, int slots)
        {
            var saved = PlayerPrefs.GetString(key, "");
            if (string.IsNullOrEmpty(saved)) return;
            var cards = new List<string>();
            foreach (var id in saved.Split(','))
                if (Array.IndexOf(all, id) >= 0 && !cards.Contains(id) && cards.Count < slots) cards.Add(id);
            // Decks saved before the deck grew to 8 vehicles are topped up from the defaults once;
            // a deck the player deliberately left short stays as it is.
            if (PlayerPrefs.GetInt("mb.deck.version", 1) < DeckVersion)
                foreach (var id in defaults)
                    if (cards.Count < slots && !cards.Contains(id)) cards.Add(id);
            deck.Clear();
            deck.AddRange(cards);
        }
    }
}
