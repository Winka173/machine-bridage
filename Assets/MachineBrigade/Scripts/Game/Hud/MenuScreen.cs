using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The menus, laid out as mobile games lay them out (Clash Royale's bottom tabs, Brawl Stars'
    /// and War Robots' landscape lobby): a top bar with the rank and the currencies, five tabs along
    /// the bottom (Shop, Army, BATTLE in the middle, Campaign, Events), the live battle behind the
    /// Battle tab with Deploy one tap away in the bottom-right corner, and full-screen pages (a
    /// vehicle's details, the battle setup, settings) that hide the tabs and go back with Back.
    /// Choices are written to <see cref="MatchSettings"/>.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        public enum Tab
        {
            Shop,
            Army,
            Battle,
            Campaign,
            Events,
        }

        private readonly Catalog _catalog;
        private readonly Action _play;
        private readonly VisualElement _backdrop, _topBar, _tabBar, _profile, _backButton;
        private readonly Label _pageTitle;
        private readonly List<Label> _coinLabels = new(), _rankLabels = new();
        private readonly List<VisualElement> _rankFills = new();
        private readonly List<(VisualElement element, Func<bool> selected)> _choices = new();
        private readonly Dictionary<Tab, VisualElement> _tabPages = new();
        private readonly Dictionary<Tab, (VisualElement button, VisualElement dot)> _tabButtons = new();
        private readonly Stack<(VisualElement page, string title)> _overlays = new();
        private readonly Dictionary<string, Label> _settingValues = new();
        private VisualElement _settings;
        private Label _customTag;
        private Tab _tab = Tab.Battle;

        public MenuScreen(Catalog catalog, Action play)
        {
            _catalog = catalog;
            _play = play;
            Root = UiKit.Box("menu", PickingMode.Ignore);

            // Behind every opaque page: nothing of the battle shows through, so the lobby can rest.
            _backdrop = UiKit.Box("menu-backdrop");
            Root.Add(_backdrop);

            // The pages, between the bars.
            BuildBattlePage();
            BuildArmyPage();
            BuildShopPage();
            BuildCampaignPage();
            BuildEventsPage();
            BuildSetupPage();
            BuildDetailPage();
            BuildSettingsPage();

            // Top bar: rank on the left (Back on a full-screen page), the page's title, then coins, gems and settings.
            _topBar = UiKit.Box("nav-top", PickingMode.Position);
            _profile = UiKit.Box("nav-profile");
            _profile.Add(UiKit.Icon("rank", UiKit.Ink, 1.8f));
            var rankText = UiKit.Box("rank-text");
            var rankLabel = UiKit.Text("", "rank-label");
            rankText.Add(rankLabel);
            var track = UiKit.Box("rank-track");
            var fill = UiKit.Box("rank-fill");
            track.Add(fill);
            rankText.Add(track);
            _profile.Add(rankText);
            _rankLabels.Add(rankLabel);
            _rankFills.Add(fill);
            _topBar.Add(_profile);
            _backButton = UiKit.Button("nav-back", () => Back());
            _backButton.Add(UiKit.Icon("retreat", UiKit.Ink, 1.9f));
            _backButton.Add(UiKit.Text(Strings.Get("menu.back"), "nav-back-text"));
            _topBar.Add(_backButton);
            _pageTitle = UiKit.Text("", "nav-title");
            _topBar.Add(_pageTitle);
            _topBar.Add(UiKit.Box("nav-spacer"));
            _topBar.Add(CurrencyPill("coin", _coinLabels, () => OpenShop(ShopTab.Coins)));
            var gear = UiKit.Button("nav-icon", () => Open(_settings, Strings.Get("menu.settings")));
            gear.Add(UiKit.Icon("settings", UiKit.Ink, 1.9f));
            _topBar.Add(gear);
            Root.Add(_topBar);

            // The navigation rail down the left edge (landscape has width to spare, not height).
            _tabBar = UiKit.Box("nav-tabs", PickingMode.Position);
            foreach (var (tab, icon, key) in new[] { (Tab.Battle, "swords", "tab.battle"), (Tab.Army, "tank", "tab.army"),
                         (Tab.Campaign, "campaign", "tab.campaign"), (Tab.Events, "trophy", "tab.events"), (Tab.Shop, "shop", "tab.shop") })
            {
                var t = tab;
                var button = UiKit.Button("nav-tab", () => ShowTab(t));
                button.Add(UiKit.Icon(icon, UiKit.Ink, 1.9f));
                button.Add(UiKit.Text(Strings.Get(key), "nav-tab-label"));
                var dot = UiKit.Box("red-dot");
                button.Add(dot);
                _tabBar.Add(button);
                _tabButtons[tab] = (button, dot);
            }
            Root.Add(_tabBar);
            Root.Add(_note);

            // A language change rebuilds the menu; come back to the page the player was on.
            ShowTab(_reopenTab);
            UiKit.Uppercase(Root);
            if (_reopenSettings) Open(_settings, Strings.Get("menu.settings"));
            _reopenSettings = false;
        }

        private static bool _reopenSettings;
        private static Tab _reopenTab = Tab.Battle;

        public VisualElement Root { get; }

        /// <summary>The vehicle turntable for the detail page (set by the match once the models exist).</summary>
        public UnitPreview Preview { get; set; }

        /// <summary>An opaque page covers the lobby battle: it need not be drawn or run.</summary>
        public bool CoversBattle => _overlays.Count > 0 || _tab != Tab.Battle;

        /// <summary>Raised when settings were changed and saved (volume, quality, language).</summary>
        public event Action SettingsChanged;

        /// <summary>Raised while the volume is being adjusted, before anything is saved.</summary>
        public event Action VolumeChanged;

        // ------------------------------------------------------------------ navigation

        public void ShowTab(Tab tab)
        {
            while (_overlays.Count > 0) CloseTop();
            _tab = tab;
            _reopenTab = tab;
            foreach (var (t, page) in _tabPages) page.style.display = t == tab ? DisplayStyle.Flex : DisplayStyle.None;
            foreach (var (t, (button, _)) in _tabButtons) button.EnableInClassList("chosen", t == tab);
            _pageTitle.text = tab == Tab.Battle ? "" : Strings.Get("tab." + tab.ToString().ToLowerInvariant()).ToUpperInvariant();
            if (tab == Tab.Shop) SkinPreviewed?.Invoke(null);
            UpdateChrome();
            Refresh();
        }

        /// <summary>Opens a full-screen page over the tabs (Back closes it).</summary>
        private void Open(VisualElement page, string title)
        {
            if (_overlays.Count > 0 && _overlays.Peek().page == page) return;
            _overlays.Push((page, title));
            page.style.display = DisplayStyle.Flex;
            page.BringToFront();
            _topBar.BringToFront();
            _note.BringToFront();
            UpdateChrome();
            Refresh();
        }

        private void CloseTop()
        {
            if (_overlays.Count == 0) return;
            var (page, _) = _overlays.Pop();
            page.style.display = DisplayStyle.None;
            if (page == _detail) Preview?.Hide();
            if (page == _settings)
            {
                MatchSettings.Save();
                SettingsChanged?.Invoke();
            }
        }

        /// <summary>
        /// The Android back button (and the top bar's Back): closes the page on top, else goes to
        /// the Battle tab. Returns false on the Battle tab, where there is nothing to close.
        /// </summary>
        public bool Back()
        {
            if (_lootPanel != null && _lootPanel.style.display == DisplayStyle.Flex)
            {
                _lootPanel.style.display = DisplayStyle.None;
                return true;
            }
            if (_popover != null && _popover.style.display == DisplayStyle.Flex)
            {
                HidePopover();
                return true;
            }
            if (_overlays.Count > 0)
            {
                CloseTop();
                UpdateChrome();
                Refresh();
                return true;
            }
            if (_tab == Tab.Battle) return false;
            ShowTab(Tab.Battle);
            return true;
        }

        private void UpdateChrome()
        {
            var overlay = _overlays.Count > 0;
            _tabBar.style.display = overlay ? DisplayStyle.None : DisplayStyle.Flex;
            _profile.style.display = overlay ? DisplayStyle.None : DisplayStyle.Flex;
            _backButton.style.display = overlay ? DisplayStyle.Flex : DisplayStyle.None;
            if (overlay) _pageTitle.text = _overlays.Peek().title.ToUpperInvariant();
            _backdrop.style.display = CoversBattle ? DisplayStyle.Flex : DisplayStyle.None;
        }

        private VisualElement CurrencyPill(string icon, List<Label> labels, Action plus)
        {
            var pill = UiKit.Button("nav-pill " + icon, plus);
            pill.Add(UiKit.Icon(icon, UiKit.Ink, 1.8f));
            var label = UiKit.Text("", "nav-pill-value");
            pill.Add(label);
            var add = UiKit.Box("nav-pill-plus");
            add.Add(UiKit.Icon("plus", UiKit.Ink, 2.2f));
            pill.Add(add);
            labels.Add(label);
            return pill;
        }

        /// <summary>A tab's page: the area between the bars.</summary>
        private VisualElement TabPage(Tab tab, string classes = "")
        {
            var page = UiKit.Box("tab-page " + classes, PickingMode.Ignore);
            page.style.display = DisplayStyle.None;
            _tabPages[tab] = page;
            Root.Add(page);
            return page;
        }

        /// <summary>A full-screen page (under the top bar, over the tabs).</summary>
        private VisualElement FullPage(string classes = "")
        {
            var page = UiKit.Box("full-page " + classes, PickingMode.Position);
            page.style.display = DisplayStyle.None;
            Root.Add(page);
            return page;
        }

        // ------------------------------------------------------------------ refresh

        private void Refresh()
        {
            foreach (var (element, selected) in _choices) element.EnableInClassList("chosen", selected());
            foreach (var label in _coinLabels) label.text = PlayerProfile.Coins.ToString("N0");
            foreach (var label in _rankLabels) label.text = Strings.Format("profile.rank", PlayerProfile.Level);
            foreach (var fill in _rankFills)
                fill.style.width = Length.Percent(100f * PlayerProfile.Xp / Mathf.Max(1, PlayerProfile.XpForNext));
            if (_customTag != null)
                _customTag.style.display = MatchSettings.Graphics == GraphicsQuality.Custom ? DisplayStyle.Flex : DisplayStyle.None;
            RefreshBattle();
            RefreshArmy();
            RefreshShop();
            RefreshCampaign();
            RefreshEvents();
            RefreshDetail();
            RefreshDots();
            UiKit.Uppercase(Root);
        }

        /// <summary>Red dots only for something to do (Clash Royale's rule): an affordable rank-up, a reward to claim, a free crate.</summary>
        private void RefreshDots()
        {
            var upgrade = false;
            foreach (var id in MatchSettings.AllVehicles)
                if (PlayerProfile.CanRankUp(id)) upgrade = true;
            foreach (var id in MatchSettings.AllSupports)
                if (PlayerProfile.CanRankUp(id)) upgrade = true;
            var claim = false;
            for (var i = 0; i < DailyMissions.Current.Count; i++)
                if (DailyMissions.Done(i) && !DailyMissions.Claimed(i)) claim = true;
            var free = PlayerProfile.FreeDealReady || (PlayerProfile.AdCratesLeft > 0 && PlayerProfile.AdCrateWait <= TimeSpan.Zero) ||
                       PlayerProfile.CrateCount(CrateKind.Battle) + PlayerProfile.CrateCount(CrateKind.Silver) +
                       PlayerProfile.CrateCount(CrateKind.Gold) + PlayerProfile.CrateCount(CrateKind.Legendary) > 0;
            _tabButtons[Tab.Army].dot.style.display = upgrade ? DisplayStyle.Flex : DisplayStyle.None;
            _tabButtons[Tab.Events].dot.style.display = claim ? DisplayStyle.Flex : DisplayStyle.None;
            _tabButtons[Tab.Shop].dot.style.display = free ? DisplayStyle.Flex : DisplayStyle.None;
            _tabButtons[Tab.Battle].dot.style.display = DisplayStyle.None;
            _tabButtons[Tab.Campaign].dot.style.display = DisplayStyle.None;
        }

        // ------------------------------------------------------------------ settings (a full-screen page from the gear)

        private void BuildSettingsPage()
        {
            _settings = FullPage("settings-page");
            var scroll = Scroller();
            _settings.Add(scroll);
            var body = scroll.contentContainer;
            body.Add(Section(1, "settings.section.graphics"));
            var presetRow = OptionRow("bolt", "settings.preset",
                new[] { Strings.Format("settings.autoTier", Level(MatchSettings.DetectTier())), Level(GraphicsQuality.Low),
                    Level(GraphicsQuality.Medium), Level(GraphicsQuality.High) },
                () => MatchSettings.Graphics == GraphicsQuality.Custom ? -1 : (int)MatchSettings.Graphics,
                i => MatchSettings.Graphics = (GraphicsQuality)i);
            _customTag = UiKit.Text(Strings.Get("settings.custom"), "custom-tag");
            presetRow.Insert(2, _customTag);
            body.Add(presetRow);
            body.Add(OptionRow("shadow", "settings.shadows",
                new[] { Strings.Get("settings.off"), Level(GraphicsQuality.Low), Level(GraphicsQuality.Medium), Level(GraphicsQuality.High) },
                () => (int)MatchSettings.Options.Shadows, i => MatchSettings.Customise(o => o.Shadows = (ShadowLevel)i)));
            body.Add(OptionRow("resolution", "settings.resolution", Array.ConvertAll(GraphicsOptions.RenderScales, v => v + "%"),
                () => Array.IndexOf(GraphicsOptions.RenderScales, MatchSettings.Options.RenderScale),
                i => MatchSettings.Customise(o => o.RenderScale = GraphicsOptions.RenderScales[i])));
            body.Add(OptionRow("edges", "settings.aa", new[] { Strings.Get("settings.off"), "2x", "4x" },
                () => Array.IndexOf(GraphicsOptions.AntiAliasingLevels, MatchSettings.Options.AntiAliasing),
                i => MatchSettings.Customise(o => o.AntiAliasing = GraphicsOptions.AntiAliasingLevels[i])));
            // Only caps the screen can show, and only divisors of its refresh (frame pacing).
            var refresh = Mathf.RoundToInt((float)Screen.currentResolution.refreshRateRatio.value);
            var rates = Array.FindAll(GraphicsOptions.FrameRates, r => r <= 60 || (refresh >= r && refresh % r == 0));
            body.Add(OptionRow("gauge", "settings.framerate", Array.ConvertAll(rates, v => v.ToString()),
                () => Array.IndexOf(rates, MatchSettings.Options.FrameRate),
                i => MatchSettings.Customise(o => o.FrameRate = rates[i])));
            body.Add(OptionRow("battery", "settings.battery",
                new[] { Strings.Get("settings.off"), Strings.Get("settings.on"), Strings.Get("settings.auto") },
                () => MatchSettings.BatterySaver, i => MatchSettings.BatterySaver = i));
            body.Add(OptionRow("sun", "settings.bloom",
                new[] { Strings.Get("settings.off"), Level(GraphicsQuality.Low), Level(GraphicsQuality.High) },
                () => MatchSettings.Options.Bloom, i => MatchSettings.Customise(o => o.Bloom = i)));
            body.Add(Stepper("brightness", "sun", Strings.Get("settings.brightness"), () => $"{MatchSettings.Brightness}%",
                step => MatchSettings.Brightness = Mathf.Clamp(MatchSettings.Brightness + step * 5, 80, 120)));
            body.Add(OptionRow("pine", "settings.scenery", new[] { Strings.Get("settings.sparse"), Strings.Get("settings.dense") },
                () => MatchSettings.Options.RichScenery ? 1 : 0, i => MatchSettings.Customise(o => o.RichScenery = i == 1)));
            body.Add(OptionRow("flame", "settings.effects", new[] { Strings.Get("settings.balanced"), Strings.Get("settings.max") },
                () => MatchSettings.Options.MaxEffects ? 1 : 0, i => MatchSettings.Customise(o => o.MaxEffects = i == 1)));

            body.Add(Section(2, "settings.section.game"));
            // Camera shake is switched off for now (RtsCamera.ShakeEnabled), so its setting is hidden with it.
            if (CameraControl.RtsCamera.ShakeEnabled)
                body.Add(OptionRow("move", "settings.shake",
                    new[] { Strings.Get("settings.off"), Level(GraphicsQuality.Low), Strings.Get("settings.full") },
                    () => MatchSettings.ScreenShake, i => MatchSettings.ScreenShake = i));
            body.Add(OptionRow("bolt", "settings.haptics", new[] { Strings.Get("settings.off"), Strings.Get("settings.on") },
                () => MatchSettings.Haptics ? 1 : 0, i => MatchSettings.Haptics = i == 1));
            body.Add(OptionRow("eye", "settings.colorblind", new[] { Strings.Get("settings.colorsDefault"), Strings.Get("settings.colorsSafe") },
                () => MatchSettings.ColorBlind ? 1 : 0, i => MatchSettings.ColorBlind = i == 1));
            body.Add(OptionRow("camera", "settings.cinematic", new[] { Strings.Get("settings.off"), Strings.Get("settings.on") },
                () => MatchSettings.CinematicMoments ? 1 : 0, i => MatchSettings.CinematicMoments = i == 1));
            body.Add(OptionRow("camera", "settings.camera",
                new[] { Strings.Get("settings.slow"), Strings.Get("settings.normal"), Strings.Get("settings.fast") },
                () => MatchSettings.CameraSpeed, i => MatchSettings.CameraSpeed = i));
            body.Add(OptionRow("resize", "settings.ui",
                new[] { Strings.Get("settings.small"), Strings.Get("settings.normal"), Strings.Get("settings.large") },
                () => MatchSettings.UiSize, i => MatchSettings.UiSize = i));
            body.Add(OptionRow("info", "settings.fps", new[] { Strings.Get("settings.off"), Strings.Get("settings.on") },
                () => MatchSettings.ShowFps ? 1 : 0, i => MatchSettings.ShowFps = i == 1));

            body.Add(Section(3, "settings.section.sound"));
            body.Add(Stepper("volume", "volume", Strings.Get("settings.volume"),
                () => $"{Mathf.RoundToInt(MatchSettings.Volume * 100f)}%",
                step => MatchSettings.Volume = Mathf.Clamp01(Mathf.Round((MatchSettings.Volume + step * 0.1f) * 10f) / 10f)));
            body.Add(Stepper("music", "volume", Strings.Get("settings.music"),
                () => MatchSettings.MusicVolume <= 0f ? Strings.Get("settings.off") : $"{Mathf.RoundToInt(MatchSettings.MusicVolume * 100f)}%",
                step => MatchSettings.MusicVolume = Mathf.Clamp01(Mathf.Round((MatchSettings.MusicVolume + step * 0.1f) * 10f) / 10f)));
            body.Add(OptionRow("globe", "settings.language", new[] { Strings.Get("settings.auto"), "English", "Tiếng Việt" },
                () => (int)MatchSettings.Language, i =>
                {
                    if ((int)MatchSettings.Language == i) return;
                    // Applies at once: the menu is rebuilt in the new language.
                    MatchSettings.Language = (LanguageChoice)i;
                    MatchSettings.Save();
                    _reopenSettings = true;
                    SettingsChanged?.Invoke();
                }, last: true));
        }

        // ------------------------------------------------------------------ shared building blocks

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
            MouseDragScroll.Attach(scroll);
            return scroll;
        }

        private void Set(Action change)
        {
            change();
            Refresh();
        }

        /// <summary>A numbered section title: "02 // MAP".</summary>
        private static Label Section(int number, string key)
        {
            var title = Strings.Get(key).ToUpperInvariant();
            return UiKit.Text(number > 0 ? $"{number:00}  //  {title}" : title, "menu-caps");
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

        /// <summary>A short message along the bottom of the menu (what just happened, or why not).</summary>
        private void Note(string text, bool warn = false)
        {
            _note.text = text;
            _note.EnableInClassList("warn", warn);
            _note.style.display = DisplayStyle.Flex;
            _note.BringToFront();
            _noteShown = Time.unscaledTime;
            _note.schedule.Execute(() =>
            {
                if (Time.unscaledTime - _noteShown >= 2.9f) _note.style.display = DisplayStyle.None;
            }).StartingIn(3000);
        }

        private Label _note;
        private float _noteShown;
    }

    internal sealed partial class MenuScreen
    {
        internal static string DoctrineIcon(string id) => id switch
        {
            "armor" => "heavytank",
            "air" => "jet",
            "artillery" => "truckgun",
            "blitz" => "bolt",
            _ => "cp",
        };

        internal static string ClassIcon(UnitClass c) => c switch
        {
            UnitClass.Scout => "jeep",
            UnitClass.Light => "armoredcar",
            UnitClass.Tank => "tank",
            UnitClass.Heavy => "heavytank",
            UnitClass.TankHunter => "destroyer",
            UnitClass.Artillery => "artillery",
            UnitClass.AntiAir => "aa",
            UnitClass.Helicopter => "helicopter",
            UnitClass.Plane => "jet",
            UnitClass.Defense => "shield",
            UnitClass.Boss => "skull",
            _ => "repair",
        };
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
            "strike_drone" => "reaper",
            "flame_tank" => "flame",
            "ifv" => "ifv",
            "howitzer" => "artillery",
            "thermobaric_launcher" => "thermo",
            "heavy_aa" => "heavyaa",
            "titan_tank" => "titan",
            "twin_tank" => "twintank",
            "siege_tank" => "siegegun",
            "aps_tank" => "apstank",
            "grad_truck" => "grad",
            "atgm_carrier" => "atgm",
            "heavy_rocket_artillery" => "smerch",
            "ballistic_launcher" => "ballistic",
            "siege_mortar" => "siegemortar",
            "engineer_vehicle" => "engineer",
            "ew_jammer" => "jammer",
            "fpv_carrier" => "fpvtruck",
            "recon_drone" => "drone",
            "mine_layer" => "mine",
            "fighter_jet" => "fighter",
            "attack_jet" => "su25",
            "tank_buster" => "a10",
            "heavy_attack_heli" => "hind2",
            "heavy_bomber" => "b52",
            "stealth_bomber" => "b2",
            "sky_gunship" => "ac130",
            "vbied" => "vbied",
            "zu23_technical" => "zu23",
            "smoke_carrier" => "smokecar",
            "lancet_truck" => "lancet",
            "shahed_truck" => "shahed",
            "iron_beam" => "laser",
            "railgun_truck" => "railgun",
            "turtle_tank" => "turtle",
            "bmpt" => "bmpt",
            "sapper" => "sapper",
            "napalm_strike" => "flame",
            "moab" => "bomb",
            "cluster_strike" => "airstrike",
            "reinforcements" => "reinforce",
            "field_repair" => "repair",
            "emp_blast" => "bolt",
            "shield_dome" => "shield",
            "gunship_support" => "gunship",
            "carpet_bombing" => "airstrike",
            "artillery_barrage" => "barrage",
            "airstrike" => "airstrike",
            "cruise_missile" => "missile",
            "smoke_screen" => "smoke",
            "repair_drop" => "repair",
            _ => "tank",
        };
    }
}
