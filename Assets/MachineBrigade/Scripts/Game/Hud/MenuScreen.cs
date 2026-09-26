using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The main menu, drawn over a live AI-versus-AI battle: pick a mode, difficulty and weather,
    /// edit the deck, change settings, deploy. Choices are written to <see cref="MatchSettings"/>.
    /// </summary>
    internal sealed class MenuScreen
    {
        private readonly Catalog _catalog;
        private readonly VisualElement _main, _deck, _settings;
        private readonly List<(VisualElement element, Func<bool> selected)> _choices = new();
        private readonly Label _deckTitle;
        private readonly Dictionary<string, VisualElement> _deckCards = new();
        private readonly Dictionary<string, Label> _settingValues = new();

        public MenuScreen(Catalog catalog, Action play)
        {
            _catalog = catalog;
            Root = UiKit.Box("menu", PickingMode.Ignore);

            // Main page: brand strip, numbered sections, and the deploy dock ---------------------
            _main = UiKit.Box("menu-panel", PickingMode.Position);
            _main.Add(Brand());
            var body = UiKit.Box("menu-body");
            body.Add(UiKit.Text(Strings.Get("menu.tagline"), "menu-tagline"));

            body.Add(Section(1, "menu.mode"));
            var modes = UiKit.Box("menu-modes");
            modes.Add(Choice(UiKit.WideButton("mode-card", "flag", Strings.Get("menu.conquest"), Strings.Get("menu.conquestSub"),
                () => Set(() => MatchSettings.Mode = GameModeKind.Conquest)), () => MatchSettings.Mode == GameModeKind.Conquest));
            modes.Add(Choice(UiKit.WideButton("mode-card last-card", "shield", Strings.Get("menu.survival"), Strings.Get("menu.survivalSub"),
                () => Set(() => MatchSettings.Mode = GameModeKind.Survival)), () => MatchSettings.Mode == GameModeKind.Survival));
            body.Add(modes);

            body.Add(Section(2, "menu.map"));
            var maps = UiKit.Box("maps");
            for (var i = 0; i < MatchSettings.AllMaps.Length; i++)
                maps.Add(MapCard(MatchSettings.AllMaps[i], i == MatchSettings.AllMaps.Length - 1));
            body.Add(maps);

            body.Add(Section(3, "menu.difficulty"));
            var difficulty = UiKit.Box("segments");
            var levels = new[] { (AiDifficulty.Easy, "menu.easy"), (AiDifficulty.Normal, "menu.normal"), (AiDifficulty.Hard, "menu.hard") };
            for (var i = 0; i < levels.Length; i++)
            {
                var (level, key) = levels[i];
                difficulty.Add(Choice(Segment(null, Strings.Get(key), () => Set(() => MatchSettings.Difficulty = level), i == levels.Length - 1),
                    () => MatchSettings.Difficulty == level));
            }
            body.Add(difficulty);

            body.Add(Section(4, "menu.weather"));
            var weather = UiKit.Box("segments grid");
            foreach (var (kind, icon, key) in new[]
                     {
                         (WeatherKind.Clear, "sun", "menu.clear"), (WeatherKind.Overcast, "cloud", "menu.overcast"),
                         (WeatherKind.Rain, "rain", "menu.rain"), (WeatherKind.Storm, "storm", "menu.storm"),
                         (WeatherKind.Snow, "snow", "menu.snow"), (WeatherKind.Sandstorm, "wind", "menu.sandstorm"),
                         (WeatherKind.Fog, "fog", "menu.fog"), (WeatherKind.Night, "moon", "menu.night"),
                         (WeatherKind.Random, "dice", "menu.random"),
                     })
                weather.Add(Choice(Segment(icon, Strings.Get(key), () => Set(() => MatchSettings.Weather = kind)),
                    () => MatchSettings.Weather == kind));
            body.Add(weather);
            _main.Add(body);

            var actions = UiKit.Box("menu-actions");
            actions.Add(UiKit.WideButton("wide primary big", "play", Strings.Get("menu.play"), null, () =>
            {
                MatchSettings.Save();
                play();
            }));
            var small = UiKit.Box("menu-small");
            small.Add(UiKit.WideButton("wide", "deck", Strings.Get("menu.deck"), null, () => Show(_deck)));
            small.Add(UiKit.WideButton("wide last-card", "settings", Strings.Get("menu.settings"), null, () => Show(_settings)));
            actions.Add(small);
            _main.Add(actions);
            Root.Add(_main);

            // Deck page ------------------------------------------------------------------------
            _deck = UiKit.Box("menu-panel wide-panel", PickingMode.Position);
            _deck.Add(Brand());
            var deckBody = UiKit.Box("menu-body");
            _deckTitle = UiKit.Text("", "menu-caps");
            deckBody.Add(_deckTitle);
            var grid = UiKit.Box("deck-grid");
            foreach (var id in MatchSettings.AllVehicles) grid.Add(DeckCard(id, support: false));
            foreach (var id in MatchSettings.AllSupports) grid.Add(DeckCard(id, support: true));
            deckBody.Add(grid);
            _deck.Add(deckBody);
            var deckDock = UiKit.Box("menu-actions");
            deckDock.Add(UiKit.WideButton("wide", "retreat", Strings.Get("menu.back"), null, () =>
            {
                MatchSettings.Save();
                Show(_main);
            }));
            _deck.Add(deckDock);
            Root.Add(_deck);

            // Settings page ----------------------------------------------------------------------
            _settings = UiKit.Box("menu-panel", PickingMode.Position);
            _settings.Add(Brand());
            var settingsBody = UiKit.Box("menu-body");
            _settings.Add(settingsBody);
            settingsBody.Add(Section(0, "menu.settings"));
            settingsBody.Add(Stepper("volume", "volume", Strings.Get("settings.volume"),
                () => $"{Mathf.RoundToInt(MatchSettings.Volume * 100f)}%",
                step => MatchSettings.Volume = Mathf.Clamp01(Mathf.Round((MatchSettings.Volume + step * 0.1f) * 10f) / 10f)));
            settingsBody.Add(Toggle("quality", "bolt", Strings.Get("settings.quality"),
                () => MatchSettings.Graphics == GraphicsQuality.Auto
                    ? Strings.Format("settings.autoTier", Strings.Get("settings." + MatchSettings.Tier.ToString().ToLowerInvariant()))
                    : Strings.Get("settings." + MatchSettings.Graphics.ToString().ToLowerInvariant()),
                () => MatchSettings.Graphics = (GraphicsQuality)(((int)MatchSettings.Graphics + 1) % 4)));
            settingsBody.Add(Toggle("motion", "move", Strings.Get("settings.motion"),
                () => Strings.Get(MatchSettings.ReducedMotion ? "settings.on" : "settings.off"),
                () => MatchSettings.ReducedMotion = !MatchSettings.ReducedMotion));
            settingsBody.Add(Toggle("fps", "info", Strings.Get("settings.fps"),
                () => Strings.Get(MatchSettings.ShowFps ? "settings.on" : "settings.off"),
                () => MatchSettings.ShowFps = !MatchSettings.ShowFps));
            settingsBody.Add(Toggle("language", "globe", Strings.Get("settings.language"),
                () => MatchSettings.Language switch
                {
                    LanguageChoice.English => "English",
                    LanguageChoice.Vietnamese => "Tiếng Việt",
                    _ => Strings.Get("settings.auto"),
                },
                () =>
                {
                    // Applies at once: the menu is rebuilt in the new language.
                    MatchSettings.Language = (LanguageChoice)(((int)MatchSettings.Language + 1) % 3);
                    MatchSettings.Save();
                    _reopenSettings = true;
                    SettingsChanged?.Invoke();
                }));
            var settingsDock = UiKit.Box("menu-actions");
            settingsDock.Add(UiKit.WideButton("wide", "retreat", Strings.Get("menu.back"), null, () =>
            {
                MatchSettings.Save();
                SettingsChanged?.Invoke();
                Show(_main);
            }));
            _settings.Add(settingsDock);
            Root.Add(_settings);

            // A language change rebuilds the menu; come back to the page the player was on.
            Show(_reopenSettings ? _settings : _main);
            _reopenSettings = false;
        }

        private static bool _reopenSettings;

        public VisualElement Root { get; }

        /// <summary>Raised when settings were changed and saved (volume, quality, language).</summary>
        public event Action SettingsChanged;

        /// <summary>Raised while the volume is being adjusted, before anything is saved.</summary>
        public event Action VolumeChanged;

        /// <summary>
        /// The Android back button: from the deck or settings page back to the main page (saving
        /// as the Back buttons do). Returns false on the main page, where there is nothing to close.
        /// </summary>
        public bool Back()
        {
            if (_main.style.display == DisplayStyle.Flex) return false;
            MatchSettings.Save();
            SettingsChanged?.Invoke();
            Show(_main);
            return true;
        }

        private void Show(VisualElement page)
        {
            foreach (var p in new[] { _main, _deck, _settings }) p.style.display = p == page ? DisplayStyle.Flex : DisplayStyle.None;
            Refresh();
        }

        private void Set(Action change)
        {
            change();
            Refresh();
        }

        private void Refresh()
        {
            foreach (var (element, selected) in _choices) element.EnableInClassList("chosen", selected());
            foreach (var (id, card) in _deckCards)
                card.EnableInClassList("chosen", MatchSettings.DeckVehicles.Contains(id) || MatchSettings.DeckSupports.Contains(id));
            _deckTitle.text = Strings.Format("menu.deckTitle", MatchSettings.DeckVehicles.Count, MatchSettings.DeckVehicleSlots,
                MatchSettings.DeckSupports.Count, MatchSettings.DeckSupportSlots);
        }

        /// <summary>The brand strip across the top of every menu page.</summary>
        private static VisualElement Brand()
        {
            var brand = UiKit.Box("menu-brand");
            brand.Add(UiKit.Icon("logo", UiKit.Ink, 2.2f));
            var text = UiKit.Box("menu-brand-text");
            text.Add(UiKit.Text("MACHINE", "menu-title"));
            text.Add(UiKit.Text("BRIGADE", "menu-title accent"));
            brand.Add(text);
            return brand;
        }

        /// <summary>A numbered section title: "02 // MAP".</summary>
        private static Label Section(int number, string key)
        {
            var title = Strings.Get(key).ToUpperInvariant();
            return UiKit.Text(number > 0 ? $"{number:00}  //  {title}" : title, "menu-caps");
        }

        private VisualElement MapCard(MapInfo map, bool last)
        {
            var available = MatchSettings.MapAvailable(map.Id);
            var card = UiKit.Button(last ? "map-card last-card" : "map-card", () =>
            {
                if (available) Set(() => MatchSettings.Map = map.Id);
            });
            card.EnableInClassList("locked", !available);
            var art = UiKit.Box("map-art " + map.Theme);
            art.Add(UiKit.Icon(map.Icon, UiKit.Ink, 1.8f));
            card.Add(art);
            card.Add(UiKit.Text(Strings.Get("map." + map.Id), "map-name"));
            card.Add(UiKit.Text(Strings.Get("map." + map.Id + ".sub"), "map-sub"));
            return Choice(card, () => MatchSettings.CurrentMap.Id == map.Id);
        }

        private VisualElement Choice(VisualElement element, Func<bool> selected)
        {
            _choices.Add((element, selected));
            return element;
        }

        private static VisualElement Segment(string icon, string label, Action onClick, bool last = false)
        {
            var segment = UiKit.Button(last ? "segment last-segment" : "segment", onClick);
            if (icon != null) segment.Add(UiKit.Icon(icon, UiKit.Ink, 1.6f));
            segment.Add(UiKit.Text(label, "segment-label"));
            return segment;
        }

        private VisualElement DeckCard(string id, bool support)
        {
            var cost = support
                ? _catalog.TryGetSupport(id, out var s) ? s.CpCost : 0
                : _catalog.Vehicles.TryGetValue(id, out var v) ? v.CpCost : 0;
            var card = UiKit.Button(support ? "card support deck-card" : "card deck-card", () =>
            {
                var deck = support ? MatchSettings.DeckSupports : MatchSettings.DeckVehicles;
                var slots = support ? MatchSettings.DeckSupportSlots : MatchSettings.DeckVehicleSlots;
                if (deck.Contains(id)) deck.Remove(id);
                else if (deck.Count < slots) deck.Add(id);
                Refresh();
            });
            card.Add(UiKit.Icon(CardIcons.For(id), UiKit.Ink, 1.6f));
            card.Add(UiKit.Text(Strings.Card(id), "card-name"));
            var badge = UiKit.Box("card-cost");
            badge.Add(UiKit.Text(cost.ToString(), "card-cost-text"));
            card.Add(badge);
            _deckCards[id] = card;
            return card;
        }

        private VisualElement Toggle(string key, string icon, string label, Func<string> value, Action toggle)
        {
            var row = UiKit.Button("setting-row", () =>
            {
                toggle();
                _settingValues[key].text = value();
            });
            row.Add(UiKit.Icon(icon, UiKit.Ink, 1.6f));
            row.Add(UiKit.Text(label, "setting-label"));
            var text = UiKit.Text(value(), "setting-value");
            _settingValues[key] = text;
            row.Add(text);
            return row;
        }

        private VisualElement Stepper(string key, string icon, string label, Func<string> value, Action<int> step)
        {
            var row = UiKit.Box("setting-row");
            row.Add(UiKit.Icon(icon, UiKit.Ink, 1.6f));
            row.Add(UiKit.Text(label, "setting-label"));
            var text = UiKit.Text(value(), "setting-value");
            _settingValues[key] = text;
            row.Add(UiKit.IconButton("minus", () =>
            {
                step(-1);
                text.text = value();
                VolumeChanged?.Invoke();
            }));
            row.Add(text);
            row.Add(UiKit.IconButton("plus", () =>
            {
                step(1);
                text.text = value();
                VolumeChanged?.Invoke();
            }));
            return row;
        }
    }

    /// <summary>Which icon each card shows.</summary>
    public static class CardIcons
    {
        public static string For(string id) => id switch
        {
            "scout_jeep" => "jeep",
            "apc" => "apc",
            "artillery" => "artillery",
            "mlrs" => "mlrs",
            "aa_vehicle" => "aa",
            "attack_helicopter" => "helicopter",
            "light_tank" => "lighttank",
            "armored_car" => "armoredcar",
            "tank_destroyer" => "destroyer",
            "heavy_tank" => "heavytank",
            "sam_launcher" => "sam",
            "mortar_carrier" => "mortar",
            "rocket_technical" => "technical",
            "gunship_heli" => "gunship",
            "scout_heli" => "scoutheli",
            "attack_jet" => "jet",
            "strike_drone" => "drone",
            "flame_tank" => "flame",
            "artillery_barrage" => "barrage",
            "airstrike" => "airstrike",
            "cruise_missile" => "missile",
            "smoke_screen" => "smoke",
            "repair_drop" => "repair",
            _ => "tank",
        };
    }
}
