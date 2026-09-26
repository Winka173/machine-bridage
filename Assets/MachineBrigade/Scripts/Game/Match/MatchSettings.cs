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
        public const int DeckVehicleSlots = 6;
        public const int DeckSupportSlots = 2;

        public static readonly string[] AllVehicles =
        {
            "scout_jeep", "apc", "light_tank", "main_battle_tank", "flame_tank", "artillery", "mlrs", "aa_vehicle",
            "attack_helicopter",
        };

        public static readonly string[] AllSupports = { "artillery_barrage", "airstrike", "cruise_missile", "smoke_screen", "repair_drop" };

        private static readonly string[] DefaultVehicles = { "scout_jeep", "apc", "light_tank", "main_battle_tank", "aa_vehicle", "attack_helicopter" };
        private static readonly string[] DefaultSupports = { "artillery_barrage", "airstrike" };

        private static bool _loaded;

        /// <summary>False shows the menu over an AI-versus-AI battle; true plays the chosen match.</summary>
        public static bool InMatch { get; set; }

        public static GameModeKind Mode { get; set; } = GameModeKind.Conquest;
        public static AiDifficulty Difficulty { get; set; } = AiDifficulty.Normal;
        public static WeatherKind Weather { get; set; } = WeatherKind.Random;

        public static List<string> DeckVehicles { get; } = new(DefaultVehicles);
        public static List<string> DeckSupports { get; } = new(DefaultSupports);

        public static float Volume { get; set; } = 0.8f;
        public static bool HighQuality { get; set; } = !Application.isMobilePlatform;
        public static bool ReducedMotion { get; set; }
        public static bool ShowFps { get; set; }
        public static LanguageChoice Language { get; set; } = LanguageChoice.Auto;

        public static void Load()
        {
            if (_loaded) return;
            _loaded = true;
            try
            {
                Volume = PlayerPrefs.GetFloat("mb.volume", Volume);
                HighQuality = PlayerPrefs.GetInt("mb.quality", HighQuality ? 1 : 0) == 1;
                ReducedMotion = PlayerPrefs.GetInt("mb.reducedMotion", 0) == 1;
                ShowFps = PlayerPrefs.GetInt("mb.fps", 0) == 1;
                Language = (LanguageChoice)PlayerPrefs.GetInt("mb.language", 0);
                Difficulty = (AiDifficulty)PlayerPrefs.GetInt("mb.difficulty", (int)AiDifficulty.Normal);
                Weather = (WeatherKind)PlayerPrefs.GetInt("mb.weather", (int)WeatherKind.Random);
                Mode = (GameModeKind)PlayerPrefs.GetInt("mb.mode", 0);
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
                PlayerPrefs.SetInt("mb.quality", HighQuality ? 1 : 0);
                PlayerPrefs.SetInt("mb.reducedMotion", ReducedMotion ? 1 : 0);
                PlayerPrefs.SetInt("mb.fps", ShowFps ? 1 : 0);
                PlayerPrefs.SetInt("mb.language", (int)Language);
                PlayerPrefs.SetInt("mb.difficulty", (int)Difficulty);
                PlayerPrefs.SetInt("mb.weather", (int)Weather);
                PlayerPrefs.SetInt("mb.mode", (int)Mode);
                PlayerPrefs.SetString("mb.deck.vehicles", string.Join(",", DeckVehicles));
                PlayerPrefs.SetString("mb.deck.supports", string.Join(",", DeckSupports));
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
            var roll = new System.Random(seed).Next(10);
            return roll < 4 ? WeatherKind.Clear : roll < 6 ? WeatherKind.Overcast : roll < 9 ? WeatherKind.Rain : WeatherKind.Storm;
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
            deck.Clear();
            deck.AddRange(cards.Count > 0 ? cards : defaults);
        }
    }
}
