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

            // Main page ------------------------------------------------------------------------
            _main = UiKit.Box("menu-panel", PickingMode.Position);
            var title = UiKit.Box("menu-brand");
            title.Add(UiKit.Icon("logo", UiKit.Mint, 2.2f));
            var titleText = UiKit.Box("menu-brand-text");
            titleText.Add(UiKit.Text("MACHINE", "menu-title"));
            titleText.Add(UiKit.Text("BRIGADE", "menu-title accent"));
            title.Add(titleText);
            _main.Add(title);
            _main.Add(UiKit.Text(Strings.Get("menu.tagline"), "menu-tagline"));

            _main.Add(UiKit.Text(Strings.Get("menu.mode"), "caps menu-caps"));
            var modes = UiKit.Box("menu-modes");
            modes.Add(Choice(UiKit.WideButton("mode-card", "flag", Strings.Get("menu.conquest"), Strings.Get("menu.conquestSub"),
                () => Set(() => MatchSettings.Mode = GameModeKind.Conquest)), () => MatchSettings.Mode == GameModeKind.Conquest));
            modes.Add(Choice(UiKit.WideButton("mode-card", "shield", Strings.Get("menu.survival"), Strings.Get("menu.survivalSub"),
                () => Set(() => MatchSettings.Mode = GameModeKind.Survival)), () => MatchSettings.Mode == GameModeKind.Survival));
            _main.Add(modes);

            _main.Add(UiKit.Text(Strings.Get("menu.difficulty"), "caps menu-caps"));
            var difficulty = UiKit.Box("segments");
            foreach (var (level, key) in new[] { (AiDifficulty.Easy, "menu.easy"), (AiDifficulty.Normal, "menu.normal"), (AiDifficulty.Hard, "menu.hard") })
                difficulty.Add(Choice(Segment(null, Strings.Get(key), () => Set(() => MatchSettings.Difficulty = level)),
                    () => MatchSettings.Difficulty == level));
            _main.Add(difficulty);

            _main.Add(UiKit.Text(Strings.Get("menu.weather"), "caps menu-caps"));
            var weather = UiKit.Box("segments");
            foreach (var (kind, icon, key) in new[]
                     {
                         (WeatherKind.Clear, "sun", "menu.clear"), (WeatherKind.Overcast, "cloud", "menu.overcast"),
                         (WeatherKind.Rain, "rain", "menu.rain"), (WeatherKind.Storm, "storm", "menu.storm"),
                         (WeatherKind.Random, "dice", "menu.random"),
                     })
                weather.Add(Choice(Segment(icon, Strings.Get(key), () => Set(() => MatchSettings.Weather = kind)),
                    () => MatchSettings.Weather == kind));
            _main.Add(weather);

            var actions = UiKit.Box("menu-actions");
            actions.Add(UiKit.WideButton("wide primary big", "play", Strings.Get("menu.play"), null, () =>
            {
                MatchSettings.Save();
                play();
            }));
            var small = UiKit.Box("menu-small");
            small.Add(UiKit.WideButton("wide", "deck", Strings.Get("menu.deck"), null, () => Show(_deck)));
            small.Add(UiKit.WideButton("wide", "settings", Strings.Get("menu.settings"), null, () => Show(_settings)));
            actions.Add(small);
            _main.Add(actions);
            Root.Add(_main);

            // Deck page ------------------------------------------------------------------------
            _deck = UiKit.Box("menu-panel wide-panel", PickingMode.Position);
            _deckTitle = UiKit.Text("", "caps menu-caps");
            _deck.Add(_deckTitle);
            var grid = UiKit.Box("deck-grid");
            foreach (var id in MatchSettings.AllVehicles) grid.Add(DeckCard(id, support: false));
            foreach (var id in MatchSettings.AllSupports) grid.Add(DeckCard(id, support: true));
            _deck.Add(grid);
            _deck.Add(UiKit.WideButton("wide", "retreat", Strings.Get("menu.back"), null, () =>
            {
                MatchSettings.Save();
                Show(_main);
            }));
            Root.Add(_deck);

            // Settings page ----------------------------------------------------------------------
            _settings = UiKit.Box("menu-panel", PickingMode.Position);
            _settings.Add(UiKit.Text(Strings.Get("menu.settings").ToUpperInvariant(), "caps menu-caps"));
            _settings.Add(Stepper("volume", "volume", Strings.Get("settings.volume"),
                () => $"{Mathf.RoundToInt(MatchSettings.Volume * 100f)}%",
                step => MatchSettings.Volume = Mathf.Clamp01(Mathf.Round((MatchSettings.Volume + step * 0.1f) * 10f) / 10f)));
            _settings.Add(Toggle("quality", "bolt", Strings.Get("settings.quality"),
                () => Strings.Get(MatchSettings.HighQuality ? "settings.high" : "settings.eco"),
                () => MatchSettings.HighQuality = !MatchSettings.HighQuality));
            _settings.Add(Toggle("motion", "move", Strings.Get("settings.motion"),
                () => Strings.Get(MatchSettings.ReducedMotion ? "settings.on" : "settings.off"),
                () => MatchSettings.ReducedMotion = !MatchSettings.ReducedMotion));
            _settings.Add(Toggle("fps", "info", Strings.Get("settings.fps"),
                () => Strings.Get(MatchSettings.ShowFps ? "settings.on" : "settings.off"),
                () => MatchSettings.ShowFps = !MatchSettings.ShowFps));
            _settings.Add(Toggle("language", "globe", Strings.Get("settings.language"),
                () => MatchSettings.Language switch
                {
                    LanguageChoice.English => "English",
                    LanguageChoice.Vietnamese => "Tiếng Việt",
                    _ => Strings.Get("settings.auto"),
                },
                () => MatchSettings.Language = (LanguageChoice)(((int)MatchSettings.Language + 1) % 3)));
            _settings.Add(UiKit.WideButton("wide", "retreat", Strings.Get("menu.back"), null, () =>
            {
                MatchSettings.Save();
                SettingsChanged?.Invoke();
                Show(_main);
            }));
            Root.Add(_settings);

            Show(_main);
        }

        public VisualElement Root { get; }

        /// <summary>Raised when settings were changed and saved (volume, quality, language).</summary>
        public event Action SettingsChanged;

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

        private VisualElement Choice(VisualElement element, Func<bool> selected)
        {
            _choices.Add((element, selected));
            return element;
        }

        private static VisualElement Segment(string icon, string label, Action onClick)
        {
            var segment = UiKit.Button("segment", onClick);
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
                SettingsChanged?.Invoke();
            }));
            row.Add(text);
            row.Add(UiKit.IconButton("plus", () =>
            {
                step(1);
                text.text = value();
                SettingsChanged?.Invoke();
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
