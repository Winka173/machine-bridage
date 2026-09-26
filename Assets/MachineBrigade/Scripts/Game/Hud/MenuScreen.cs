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
    internal sealed partial class MenuScreen
    {
        private readonly Catalog _catalog;
        private readonly VisualElement _main, _deck, _settings;
        private readonly Action _play;
        private readonly List<Label> _coinLabels = new(), _rankLabels = new();
        private readonly List<VisualElement> _rankFills = new();
        private Label _deckNote, _campaignBannerSub, _campaignBannerNext;
        private readonly List<(VisualElement element, Func<bool> selected)> _choices = new();
        private readonly Label _deckTitle;
        private readonly Dictionary<string, VisualElement> _deckCards = new();
        private readonly Dictionary<string, Label> _settingValues = new();
        private Label _customTag;

        public MenuScreen(Catalog catalog, Action play)
        {
            _catalog = catalog;
            Root = UiKit.Box("menu", PickingMode.Ignore);

            _play = play;

            // Main page: brand strip, the campaign, quick battle and its options, the dock ---------
            _main = UiKit.Box("menu-panel", PickingMode.Position);
            _main.Add(Brand());
            var body = Scroller();
            _main.Add(body);
            var content = body.contentContainer;
            content.Add(UiKit.Text(Strings.Get("menu.tagline"), "menu-tagline"));

            // The campaign banner: progress and the next mission, one tap to the campaign page.
            var banner = UiKit.Button("campaign-banner", () => Show(_campaign));
            banner.Add(UiKit.Icon("campaign", UiKit.Ink, 1.9f));
            var bannerText = UiKit.Box("campaign-banner-text");
            bannerText.Add(UiKit.Text(Strings.Get("campaign.title").ToUpperInvariant(), "campaign-banner-title"));
            _campaignBannerSub = UiKit.Text("", "campaign-banner-sub");
            bannerText.Add(_campaignBannerSub);
            banner.Add(bannerText);
            _campaignBannerNext = UiKit.Text("", "campaign-banner-next");
            banner.Add(_campaignBannerNext);
            content.Add(banner);

            content.Add(Section(1, "menu.quick"));
            var modes = UiKit.Box("menu-modes grid-modes");
            var modeList = new[]
            {
                (GameModeKind.Conquest, "flag", "mode.conquest", "mode.conquestSub"),
                (GameModeKind.Deathmatch, "swords", "mode.deathmatch", "mode.deathmatchSub"),
                (GameModeKind.KingOfTheHill, "crown", "mode.hill", "mode.hillSub"),
                (GameModeKind.Assault, "attack", "mode.assault", "mode.assaultSub"),
                (GameModeKind.Survival, "shield", "mode.survival", "mode.survivalSub"),
            };
            foreach (var (kind, icon, name, sub) in modeList)
                modes.Add(Choice(UiKit.WideButton("mode-card", icon, Strings.Get(name), Strings.Get(sub), () => Set(() => MatchSettings.Mode = kind)),
                    () => MatchSettings.Mode == kind));
            content.Add(modes);

            content.Add(Section(2, "menu.map"));
            var maps = UiKit.Box("maps");
            for (var i = 0; i < MatchSettings.AllMaps.Length; i++)
                maps.Add(MapCard(MatchSettings.AllMaps[i], i == MatchSettings.AllMaps.Length - 1));
            content.Add(maps);

            content.Add(Section(3, "menu.difficulty"));
            var difficulty = UiKit.Box("segments");
            var levels = new[] { (AiDifficulty.Easy, "menu.easy"), (AiDifficulty.Normal, "menu.normal"), (AiDifficulty.Hard, "menu.hard") };
            for (var i = 0; i < levels.Length; i++)
            {
                var (level, key) = levels[i];
                difficulty.Add(Choice(Segment(null, Strings.Get(key), () => Set(() => MatchSettings.Difficulty = level), i == levels.Length - 1),
                    () => MatchSettings.Difficulty == level));
            }
            content.Add(difficulty);

            content.Add(Section(4, "menu.weather"));
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
            content.Add(weather);

            var actions = UiKit.Box("menu-actions");
            actions.Add(UiKit.WideButton("wide primary big", "play", Strings.Get("menu.play"), null, () =>
            {
                if (MatchSettings.Mode == GameModeKind.Campaign) MatchSettings.Mode = GameModeKind.Conquest;
                MatchSettings.Save();
                play();
            }));
            var small = UiKit.Box("menu-small");
            small.Add(UiKit.WideButton("wide", "deck", Strings.Get("menu.deck"), null, () => Show(_deck)));
            small.Add(UiKit.WideButton("wide", "shop", Strings.Get("menu.shop"), null, () => Show(_shop)));
            small.Add(UiKit.WideButton("wide last-card", "settings", Strings.Get("menu.settings"), null, () => Show(_settings)));
            actions.Add(small);
            _main.Add(actions);
            Root.Add(_main);

            // Deck page: locked cards show how to get them ---------------------------------------
            _deck = UiKit.Box("menu-panel wide-panel", PickingMode.Position);
            _deck.Add(Brand());
            var deckScroll = Scroller();
            var deckBody = deckScroll.contentContainer;
            _deckTitle = UiKit.Text("", "menu-caps");
            deckBody.Add(_deckTitle);
            _deckNote = UiKit.Text(Strings.Get("deck.hint"), "menu-note");
            deckBody.Add(_deckNote);
            var grid = UiKit.Box("deck-grid");
            foreach (var id in MatchSettings.AllVehicles) grid.Add(DeckCard(id, support: false));
            foreach (var id in MatchSettings.AllSupports) grid.Add(DeckCard(id, support: true));
            deckBody.Add(grid);
            _deck.Add(deckScroll);
            var deckDock = UiKit.Box("menu-actions");
            deckDock.Add(UiKit.WideButton("wide", "retreat", Strings.Get("menu.back"), null, () =>
            {
                MatchSettings.Save();
                Show(_main);
            }));
            _deck.Add(deckDock);
            Root.Add(_deck);

            BuildCampaignPage();
            BuildShopPage();

            // Settings page: graphics, gameplay, sound and language in one scrolling list ---------
            _settings = UiKit.Box("menu-panel wide-panel", PickingMode.Position);
            _settings.Add(Brand());
            var scroll = new ScrollView(ScrollViewMode.Vertical)
            {
                horizontalScrollerVisibility = ScrollerVisibility.Hidden,
                verticalScrollerVisibility = ScrollerVisibility.Hidden,
                touchScrollBehavior = ScrollView.TouchScrollBehavior.Clamped,
            };
            scroll.AddToClassList("menu-body");
            scroll.AddToClassList("settings-scroll");
            _settings.Add(scroll);
            var settingsBody = scroll.contentContainer;

            settingsBody.Add(Section(1, "settings.section.graphics"));
            var presetRow = OptionRow("bolt", "settings.preset",
                new[] { Strings.Format("settings.autoTier", Level(MatchSettings.DetectTier())), Level(GraphicsQuality.Low),
                    Level(GraphicsQuality.Medium), Level(GraphicsQuality.High) },
                () => MatchSettings.Graphics == GraphicsQuality.Custom ? -1 : (int)MatchSettings.Graphics,
                i => MatchSettings.Graphics = (GraphicsQuality)i);
            _customTag = UiKit.Text(Strings.Get("settings.custom"), "custom-tag");
            presetRow.Insert(2, _customTag);
            settingsBody.Add(presetRow);
            settingsBody.Add(OptionRow("shadow", "settings.shadows",
                new[] { Strings.Get("settings.off"), Level(GraphicsQuality.Low), Level(GraphicsQuality.Medium), Level(GraphicsQuality.High) },
                () => (int)MatchSettings.Options.Shadows, i => MatchSettings.Customise(o => o.Shadows = (ShadowLevel)i)));
            settingsBody.Add(OptionRow("resolution", "settings.resolution", Array.ConvertAll(GraphicsOptions.RenderScales, v => v + "%"),
                () => Array.IndexOf(GraphicsOptions.RenderScales, MatchSettings.Options.RenderScale),
                i => MatchSettings.Customise(o => o.RenderScale = GraphicsOptions.RenderScales[i])));
            settingsBody.Add(OptionRow("edges", "settings.aa", new[] { Strings.Get("settings.off"), "2x", "4x" },
                () => Array.IndexOf(GraphicsOptions.AntiAliasingLevels, MatchSettings.Options.AntiAliasing),
                i => MatchSettings.Customise(o => o.AntiAliasing = GraphicsOptions.AntiAliasingLevels[i])));
            // Only caps the screen can show, and only divisors of its refresh (frame pacing).
            var refresh = Mathf.RoundToInt((float)Screen.currentResolution.refreshRateRatio.value);
            var rates = Array.FindAll(GraphicsOptions.FrameRates, r => r <= 60 || (refresh >= r && refresh % r == 0));
            settingsBody.Add(OptionRow("gauge", "settings.framerate", Array.ConvertAll(rates, v => v.ToString()),
                () => Array.IndexOf(rates, MatchSettings.Options.FrameRate),
                i => MatchSettings.Customise(o => o.FrameRate = rates[i])));
            settingsBody.Add(OptionRow("battery", "settings.battery",
                new[] { Strings.Get("settings.off"), Strings.Get("settings.on"), Strings.Get("settings.auto") },
                () => MatchSettings.BatterySaver, i => MatchSettings.BatterySaver = i));
            settingsBody.Add(OptionRow("sun", "settings.bloom",
                new[] { Strings.Get("settings.off"), Level(GraphicsQuality.Low), Level(GraphicsQuality.High) },
                () => MatchSettings.Options.Bloom, i => MatchSettings.Customise(o => o.Bloom = i)));
            settingsBody.Add(Stepper("brightness", "sun", Strings.Get("settings.brightness"), () => $"{MatchSettings.Brightness}%",
                step => MatchSettings.Brightness = Mathf.Clamp(MatchSettings.Brightness + step * 5, 80, 120)));
            settingsBody.Add(OptionRow("pine", "settings.scenery", new[] { Strings.Get("settings.sparse"), Strings.Get("settings.dense") },
                () => MatchSettings.Options.RichScenery ? 1 : 0, i => MatchSettings.Customise(o => o.RichScenery = i == 1)));
            settingsBody.Add(OptionRow("flame", "settings.effects", new[] { Strings.Get("settings.balanced"), Strings.Get("settings.max") },
                () => MatchSettings.Options.MaxEffects ? 1 : 0, i => MatchSettings.Customise(o => o.MaxEffects = i == 1)));

            settingsBody.Add(Section(2, "settings.section.game"));
            settingsBody.Add(OptionRow("move", "settings.shake",
                new[] { Strings.Get("settings.off"), Level(GraphicsQuality.Low), Strings.Get("settings.full") },
                () => MatchSettings.ScreenShake, i => MatchSettings.ScreenShake = i));
            settingsBody.Add(OptionRow("camera", "settings.camera",
                new[] { Strings.Get("settings.slow"), Strings.Get("settings.normal"), Strings.Get("settings.fast") },
                () => MatchSettings.CameraSpeed, i => MatchSettings.CameraSpeed = i));
            settingsBody.Add(OptionRow("resize", "settings.ui",
                new[] { Strings.Get("settings.small"), Strings.Get("settings.normal"), Strings.Get("settings.large") },
                () => MatchSettings.UiSize, i => MatchSettings.UiSize = i));
            settingsBody.Add(OptionRow("info", "settings.fps", new[] { Strings.Get("settings.off"), Strings.Get("settings.on") },
                () => MatchSettings.ShowFps ? 1 : 0, i => MatchSettings.ShowFps = i == 1));

            settingsBody.Add(Section(3, "settings.section.sound"));
            settingsBody.Add(Stepper("volume", "volume", Strings.Get("settings.volume"),
                () => $"{Mathf.RoundToInt(MatchSettings.Volume * 100f)}%",
                step => MatchSettings.Volume = Mathf.Clamp01(Mathf.Round((MatchSettings.Volume + step * 0.1f) * 10f) / 10f)));
            settingsBody.Add(OptionRow("globe", "settings.language", new[] { Strings.Get("settings.auto"), "English", "Tiếng Việt" },
                () => (int)MatchSettings.Language, i =>
                {
                    if ((int)MatchSettings.Language == i) return;
                    // Applies at once: the menu is rebuilt in the new language.
                    MatchSettings.Language = (LanguageChoice)i;
                    MatchSettings.Save();
                    _reopenSettings = true;
                    SettingsChanged?.Invoke();
                }, last: true));
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
            foreach (var p in new[] { _main, _deck, _settings, _campaign, _shop })
                if (p != null) p.style.display = p == page ? DisplayStyle.Flex : DisplayStyle.None;
            Refresh();
        }

        /// <summary>A vertical scrolling page body (touch-dragged, no scrollbars).</summary>
        private static ScrollView Scroller(string extra = null)
        {
            var scroll = new ScrollView(ScrollViewMode.Vertical)
            {
                horizontalScrollerVisibility = ScrollerVisibility.Hidden,
                verticalScrollerVisibility = ScrollerVisibility.Hidden,
                touchScrollBehavior = ScrollView.TouchScrollBehavior.Clamped,
            };
            scroll.AddToClassList("menu-body");
            scroll.AddToClassList("settings-scroll");
            if (extra != null) scroll.AddToClassList(extra);
            return scroll;
        }

        private void Set(Action change)
        {
            change();
            Refresh();
        }

        private void Refresh()
        {
            foreach (var (element, selected) in _choices) element.EnableInClassList("chosen", selected());
            foreach (var label in _coinLabels) label.text = PlayerProfile.Coins.ToString("N0");
            foreach (var label in _rankLabels) label.text = Strings.Format("profile.rank", PlayerProfile.Level);
            foreach (var fill in _rankFills)
                fill.style.width = Length.Percent(100f * PlayerProfile.Xp / Mathf.Max(1, PlayerProfile.XpForNext));
            if (_campaignBannerSub != null)
            {
                _campaignBannerSub.text = Strings.Format("campaign.progress", Campaign.Won, Campaign.All.Count, PlayerProfile.TotalStars);
                var next = Campaign.All[Campaign.Next];
                _campaignBannerNext.text = Strings.Format("campaign.next", Campaign.Next + 1, Strings.Get("mission." + next.Id + ".name"));
            }
            RefreshCampaign();
            RefreshShop();
            if (_customTag != null)
                _customTag.style.display = MatchSettings.Graphics == GraphicsQuality.Custom ? DisplayStyle.Flex : DisplayStyle.None;
            foreach (var (id, card) in _deckCards)
            {
                card.EnableInClassList("chosen", MatchSettings.DeckVehicles.Contains(id) || MatchSettings.DeckSupports.Contains(id));
                card.EnableInClassList("locked", !PlayerProfile.IsUnlocked(id));
            }
            _deckTitle.text = Strings.Format("menu.deckTitle", MatchSettings.DeckVehicles.Count, MatchSettings.DeckVehicleSlots,
                MatchSettings.DeckSupports.Count, MatchSettings.DeckSupportSlots);
        }

        /// <summary>The brand strip across the top of every menu page, with the player's rank and coins.</summary>
        private VisualElement Brand()
        {
            var brand = UiKit.Box("menu-brand");
            brand.Add(UiKit.Icon("logo", UiKit.Ink, 2.2f));
            var text = UiKit.Box("menu-brand-text");
            text.Add(UiKit.Text("MACHINE", "menu-title"));
            text.Add(UiKit.Text("BRIGADE", "menu-title accent"));
            brand.Add(text);
            var profile = UiKit.Box("brand-profile");
            var rank = UiKit.Box("rank-pill");
            rank.Add(UiKit.Icon("rank", UiKit.Ink, 1.8f));
            var rankText = UiKit.Box("rank-text");
            var rankLabel = UiKit.Text("", "rank-label");
            rankText.Add(rankLabel);
            var track = UiKit.Box("rank-track");
            var fill = UiKit.Box("rank-fill");
            track.Add(fill);
            rankText.Add(track);
            rank.Add(rankText);
            profile.Add(rank);
            var coins = UiKit.Box("coin-pill");
            coins.Add(UiKit.Icon("coin", UiKit.Ink, 1.8f));
            var coinLabel = UiKit.Text("", "coin-label");
            coins.Add(coinLabel);
            profile.Add(coins);
            brand.Add(profile);
            _rankLabels.Add(rankLabel);
            _rankFills.Add(fill);
            _coinLabels.Add(coinLabel);
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
                if (!PlayerProfile.IsUnlocked(id))
                {
                    _deckNote.text = LockReason(id);
                    _deckNote.AddToClassList("warn");
                    return;
                }
                _deckNote.RemoveFromClassList("warn");
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
            var lockBadge = UiKit.Box("card-lock");
            lockBadge.Add(UiKit.Icon("lock", UiKit.Ink, 1.8f));
            card.Add(lockBadge);
            _deckCards[id] = card;
            return card;
        }

        /// <summary>A settings row: a label on the left, its choices as segments on the right.</summary>
        private VisualElement OptionRow(string icon, string labelKey, string[] labels, Func<int> selected, Action<int> choose,
            bool last = false)
        {
            var row = UiKit.Box(last ? "setting-row option-row last-row" : "setting-row option-row");
            row.Add(UiKit.Icon(icon, UiKit.Ink, 1.6f));
            row.Add(UiKit.Text(Strings.Get(labelKey), "setting-label"));
            var group = UiKit.Box("options");
            for (var i = 0; i < labels.Length; i++)
            {
                var index = i;
                var option = UiKit.Button(i == labels.Length - 1 ? "option last-option" : "option", () => Set(() => choose(index)));
                option.Add(UiKit.Text(labels[i], "option-label"));
                group.Add(Choice(option, () => selected() == index));
            }
            row.Add(group);
            return row;
        }

        /// <summary>How to get a locked card: the mission that unlocks it, or the shop.</summary>
        private string LockReason(string id)
        {
            var name = Strings.Card(id);
            if (Progression.IsPremium(id)) return Strings.Format("deck.lockedPremium", name, Progression.Price(id, _catalog));
            var mission = Progression.UnlockMission(id);
            return mission != null
                ? Strings.Format("deck.lockedMission", name, Campaign.IndexOf(mission.Id) + 1, Progression.Price(id, _catalog))
                : Strings.Format("deck.lockedShop", name, Progression.Price(id, _catalog));
        }

        private static string Level(GraphicsQuality tier) => Strings.Get("settings." + tier.ToString().ToLowerInvariant());

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
