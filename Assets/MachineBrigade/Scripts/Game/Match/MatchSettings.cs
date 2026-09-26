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
        Deathmatch,
        KingOfTheHill,
        Assault,

        /// <summary>A campaign mission (<see cref="MatchSettings.Mission"/>).</summary>
        Campaign,
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

        /// <summary>The player changed individual options (see <see cref="MatchSettings.Options"/>).</summary>
        Custom,
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
        private const int DeckVersion = 3;

        public static readonly string[] AllVehicles =
        {
            "scout_jeep", "armored_car", "rocket_technical", "apc", "light_tank", "main_battle_tank", "heavy_tank",
            "tank_destroyer", "flame_tank", "mortar_carrier", "artillery", "mlrs", "aa_vehicle", "sam_launcher",
            "scout_heli", "attack_helicopter", "gunship_heli", "strike_drone", "attack_jet",
        };

        public static readonly string[] AllSupports = { "artillery_barrage", "airstrike", "cruise_missile", "smoke_screen", "repair_drop" };

        // A new player's deck: the starter cards (the rest are won in the campaign or bought).
        private static readonly string[] DefaultVehicles = Progression.StarterVehicles;
        private static readonly string[] DefaultSupports = Progression.StarterSupports;

        /// <summary>The campaign mission to play when <see cref="Mode"/> is Campaign.</summary>
        public static string Mission { get; set; } = "m01";

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
        public static GraphicsQuality Tier => Graphics is GraphicsQuality.Auto or GraphicsQuality.Custom ? DetectTier() : Graphics;

        private static GraphicsOptions _custom;

        /// <summary>The graphics options in force: the preset's, or the player's own under Custom.</summary>
        public static GraphicsOptions Options => Graphics == GraphicsQuality.Custom && _custom != null ? _custom : GraphicsOptions.For(Tier);

        /// <summary>Changes one option: the current values become the Custom set.</summary>
        public static void Customise(System.Action<GraphicsOptions> change)
        {
            var options = Options.Copy();
            change(options);
            _custom = options;
            Graphics = GraphicsQuality.Custom;
        }

        public static bool HighQuality => Options.MaxEffects;

        /// <summary>Screen shake: 0 off, 1 low, 2 full.</summary>
        public static int ScreenShake { get; set; } = 2;

        public static float ShakeScale => ScreenShake switch { 0 => 0f, 1 => 0.35f, _ => 1f };

        /// <summary>Camera drag speed: 0 slow, 1 normal, 2 fast.</summary>
        public static int CameraSpeed { get; set; } = 1;

        public static float PanScale => CameraSpeed switch { 0 => 0.7f, 2 => 1.45f, _ => 1f };

        /// <summary>Battery saver: 0 off, 1 on, 2 automatic (on when the battery is low and not charging).</summary>
        public static int BatterySaver { get; set; } = 2;

        /// <summary>
        /// True while saving battery: 30 fps and 85% resolution. Effects are untouched. The
        /// automatic mode starts it under 20% charge while unplugged.
        /// </summary>
        public static bool SavingBattery => BatterySaver == 1 || (BatterySaver == 2 && SystemInfo.batteryLevel >= 0f &&
            SystemInfo.batteryLevel < 0.2f && SystemInfo.batteryStatus == BatteryStatus.Discharging);

        /// <summary>Brightness in percent (80 to 120).</summary>
        public static int Brightness { get; set; } = 100;

        /// <summary>Interface size: 0 small, 1 normal, 2 large.</summary>
        public static int UiSize { get; set; } = 1;

        public static float UiScale => UiSize switch { 0 => 0.9f, 2 => 1.1f, _ => 1f };

        public static GraphicsQuality DetectTier()
        {
            if (!Application.isMobilePlatform) return GraphicsQuality.High;
            var memory = SystemInfo.systemMemorySize;
            var cores = SystemInfo.processorCount;
            if (memory >= 7000 && cores >= 8) return GraphicsQuality.High;
            if (memory >= 3500 && cores >= 6) return GraphicsQuality.Medium;
            return GraphicsQuality.Low;
        }
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
                Graphics = (GraphicsQuality)Mathf.Clamp(PlayerPrefs.GetInt("mb.graphics", 0), 0, 4);
                if (Graphics == GraphicsQuality.Custom) _custom = GraphicsOptions.Load("mb.gfx.", GraphicsOptions.For(DetectTier()));
                // Reduced motion (older saves) became the low screen-shake setting.
                ScreenShake = Mathf.Clamp(PlayerPrefs.GetInt("mb.shake", PlayerPrefs.GetInt("mb.reducedMotion", 0) == 1 ? 1 : 2), 0, 2);
                CameraSpeed = Mathf.Clamp(PlayerPrefs.GetInt("mb.cameraSpeed", 1), 0, 2);
                UiSize = Mathf.Clamp(PlayerPrefs.GetInt("mb.uiSize", 1), 0, 2);
                BatterySaver = Mathf.Clamp(PlayerPrefs.GetInt("mb.battery", 2), 0, 2);
                Brightness = Mathf.Clamp(PlayerPrefs.GetInt("mb.brightness", 100), 80, 120);
                Map = PlayerPrefs.GetString("mb.map", Map);
                ShowFps = PlayerPrefs.GetInt("mb.fps", 0) == 1;
                Language = (LanguageChoice)PlayerPrefs.GetInt("mb.language", 0);
                Difficulty = (AiDifficulty)PlayerPrefs.GetInt("mb.difficulty", (int)AiDifficulty.Normal);
                Weather = (WeatherKind)PlayerPrefs.GetInt("mb.weather", (int)WeatherKind.Random);
                Mode = (GameModeKind)Mathf.Clamp(PlayerPrefs.GetInt("mb.mode", 0), 0, (int)GameModeKind.Assault);
                Mission = PlayerPrefs.GetString("mb.mission", Mission);
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
                if (Graphics == GraphicsQuality.Custom) _custom?.Save("mb.gfx.");
                PlayerPrefs.SetInt("mb.shake", ScreenShake);
                PlayerPrefs.SetInt("mb.cameraSpeed", CameraSpeed);
                PlayerPrefs.SetInt("mb.uiSize", UiSize);
                PlayerPrefs.SetInt("mb.battery", BatterySaver);
                PlayerPrefs.SetInt("mb.brightness", Brightness);
                PlayerPrefs.SetString("mb.map", Map);
                PlayerPrefs.SetInt("mb.fps", ShowFps ? 1 : 0);
                PlayerPrefs.SetInt("mb.language", (int)Language);
                PlayerPrefs.SetInt("mb.difficulty", (int)Difficulty);
                PlayerPrefs.SetInt("mb.weather", (int)Weather);
                // Campaign runs are started from the campaign page, never restored as the menu's mode.
                PlayerPrefs.SetInt("mb.mode", Mode == GameModeKind.Campaign ? 0 : (int)Mode);
                PlayerPrefs.SetString("mb.mission", Mission);
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
                if (Array.IndexOf(all, id) >= 0 && PlayerProfile.IsUnlocked(id) && !cards.Contains(id) && cards.Count < slots) cards.Add(id);
            // Decks saved before the deck grew to 8 vehicles are topped up from the defaults once;
            // a deck the player deliberately left short stays as it is.
            if (PlayerPrefs.GetInt("mb.deck.version", 1) < DeckVersion || cards.Count == 0)
                foreach (var id in defaults)
                    if (cards.Count < slots && !cards.Contains(id)) cards.Add(id);
            deck.Clear();
            deck.AddRange(cards);
        }
    }
}
