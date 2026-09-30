using System;
using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The menus, Field Command 2.0 (built on the UI kit, styled by Tokens.uss and Screens.uss):
    /// one top bar (the screen's title, or the logo at home; the rank badge and its XP bar; the
    /// coins and their plus; one settings gear), a rail of five items down the left edge (Home,
    /// Campaign, Operations, Army, Shop), each tab's page between them, and full-screen pages (a
    /// vehicle's details, the Dossier, settings) that hide the rail and go back with Back. The live
    /// battle shows behind Home, dimmed. Choices are written to <see cref="MatchSettings"/>.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        public enum Tab
        {
            Home,
            Campaign,
            Operations,
            Army,
            Shop,
        }

        private static readonly (Tab tab, string icon, string key)[] NavItems =
        {
            (Tab.Home, "home", "nav.home"), (Tab.Campaign, "campaign", "nav.campaign"), (Tab.Operations, "swords", "nav.operations"),
            (Tab.Army, "tank", "nav.army"), (Tab.Shop, "shop", "nav.shop"),
        };

        private readonly Catalog _catalog;
        private readonly Action _play;
        private readonly VisualElement _topBar, _topLead, _logo, _nav, _homeScrim;
        private readonly KitIconButton _backButton;
        private readonly Label _pageTitle, _rankLabel, _xpLabel;
        private readonly KitProgress _xpBar;
        private readonly KitCurrency _coins;
        private readonly List<Action> _refreshers = new();
        private readonly Dictionary<Tab, VisualElement> _tabPages = new();
        private readonly Dictionary<Tab, KitNavItem> _navItems = new();
        private readonly Stack<(VisualElement page, string title)> _overlays = new();
        private VisualElement _settings;
        private Tab _tab = Tab.Home;

        public MenuScreen(Catalog catalog, Action play)
        {
            _catalog = catalog;
            _play = play;
            Root = Kit.Root("menu fc-menu");
            Root.pickingMode = PickingMode.Ignore;

            // Behind every opaque page: nothing of the battle shows through, so the lobby can rest.
            // BattleHud puts it under the safe area, so it covers a notch's side too.
            Backdrop = Kit.Box("fc-backdrop");
            _homeScrim = Kit.Box("fc-home-scrim");
            Root.Add(_homeScrim);

            _note = Kit.Box("fc-toast-host");

            // The pages, between the bars.
            BuildHomePage();
            BuildCampaignPage();
            BuildOperationsPage();
            BuildArmyPage();
            BuildShopPage();
            BuildDetailPage();
            BuildSettingsPage();
            BuildLegendPage();

            // Top bar: the logo at home, the screen's title elsewhere, Back on a full page; the rank,
            // the coins and the one settings gear on the right.
            _topBar = Kit.Box("fc-top", PickingMode.Position);
            _topLead = Kit.Box("fc-top__lead");
            // The top bar is 44 pt: its icon buttons are small faces inside their 44 pt targets (prompt 14 A3).
            _backButton = new KitIconButton("retreat", Strings.Get("menu.back"), () => Back(), plain: true);
            _topLead.Add(_backButton);
            _logo = Kit.Box("fc-top__logo");
            _logo.Add(Kit.Icon("logo"));
            _logo.Add(Kit.Text("MACHINE BRIGADE", "fc-top__brand"));
            _topLead.Add(_logo);
            _pageTitle = Kit.Text("", "fc-title fc-top__title");
            _topLead.Add(_pageTitle);
            _topBar.Add(_topLead);
            var rank = Kit.Box("fc-top__rank", PickingMode.Position);
            rank.Add(Kit.Icon("rank"));
            var rankText = Kit.Box("fc-top__rank-text");
            _rankLabel = Kit.Text("", "fc-panel-title");
            rankText.Add(_rankLabel);
            _xpBar = new KitProgress();
            _xpBar.AddToClassList("fc-top__xp");
            rankText.Add(_xpBar);
            _xpLabel = Kit.Text("", "fc-small fc-top__xp-text");
            rankText.Add(_xpLabel);
            rank.Add(rankText);
            _profile = rank;
            _topBar.Add(rank);
            _coins = new KitCurrency(0, () => OpenShop(ShopTab.Coins));
            _topBar.Add(_coins);
            var gear = new KitIconButton("settings", Strings.Get("menu.settings"), () => Open(_settings, Strings.Get("menu.settings")), plain: true);
            gear.AddToClassList("fc-top__gear");
            _topBar.Add(gear);
            Root.Add(_topBar);

            // The navigation rail down the left edge (landscape has width to spare, not height).
            _nav = Kit.Box("fc-nav fc-menu-nav", PickingMode.Position);
            foreach (var (tab, icon, key) in NavItems)
            {
                var t = tab;
                var item = new KitNavItem(icon, Strings.Get(key), false, () => ShowTab(t));
                _nav.Add(item);
                _navItems[tab] = item;
            }
            Root.Add(_nav);
            Root.Add(_note);
            ShowBranchNews();
            ShowRefundNews();

            // A language change rebuilds the menu; come back to the page the player was on.
            if (_reopenDeck) _armyView = ArmyView.Deck;
            _reopenDeck = false;
            ShowTab(_reopenTab);
            if (_reopenSettings) Open(_settings, Strings.Get("menu.settings"));
            _reopenSettings = false;
            // Device check of a detail page: -mb-detail=apc (and -mb-detail-guide for its Guide tab, -mb-detail-firing for In action).
            var detail = Match.DebugFlags.Value("-mb-detail=");
            if (!string.IsNullOrEmpty(detail) && (catalog.Vehicles.ContainsKey(detail) || catalog.TryGetSupport(detail, out _)))
            {
                if (Match.DebugFlags.Has("-mb-detail-guide")) _detailTab = DetailTab.Guide;
                if (Match.DebugFlags.Has("-mb-detail-firing")) _detailTab = DetailTab.Firing;
                OpenDetail(detail);
                Refresh();
            }
            // Device check of the base screen: -mb-base (-mb-base-map=redrock, -mb-base-gear, -mb-base-pick=aa_turret).
            if (Match.DebugFlags.Has("-mb-base"))
            {
                _armyView = ArmyView.Base;
                ShowTab(Tab.Army);
                _base.DebugOpen();
            }
            // The UI kit preview (Field Command 2.0): -mb-ui-kit[=page], or five quick taps on the rank badge.
            _profile.RegisterCallback<PointerDownEvent>(_ => CountKitTap());
            var kitPage = Match.DebugFlags.Value(KitPreview.DebugFlag + "=");
            if (Match.DebugFlags.Has(KitPreview.DebugFlag) || !string.IsNullOrEmpty(kitPage))
                OpenKitPreview(KitPreview.ParsePage(kitPage), Match.DebugFlags.Has("-mb-ui-large"));
        }

        private readonly VisualElement _profile;
        private int _kitTaps;
        private float _kitTapStart;

        private void CountKitTap()
        {
            if (Time.unscaledTime - _kitTapStart > 3f)
            {
                _kitTapStart = Time.unscaledTime;
                _kitTaps = 0;
            }
            if (++_kitTaps < 5) return;
            _kitTaps = 0;
            OpenKitPreview(KitPreview.Page.Buttons, MatchSettings.LargeText);
        }

        /// <summary>The kit preview over the menu (a developer page: not in the navigation).</summary>
        private void OpenKitPreview(KitPreview.Page page, bool large)
        {
            var preview = new KitPreview(_catalog, null, page, Strings.Vietnamese, large);
            Root.Add(preview.Root);
            preview.Root.BringToFront();
        }

        private static bool _reopenSettings;
        private static bool _reopenDeck;

        /// <summary>The next menu opens on the Army tab's deck (the result screen's "open the deck" after a defeat).</summary>
        internal static void OpenDeckNext()
        {
            _reopenTab = Tab.Army;
            _reopenDeck = true;
        }
        private static Tab _reopenTab = Tab.Home;

        public VisualElement Root { get; }

        /// <summary>The opaque screen behind the menu's pages (the battle hides behind it), for BattleHud to place under the safe area.</summary>
        public VisualElement Backdrop { get; }

        /// <summary>The vehicle turntable for the detail page (set by the match once the models exist).</summary>
        public UnitPreview Preview
        {
            get => _preview;
            set
            {
                _preview = value;
                // A detail page opened before the preview existed (-mb-detail): show its model now.
                if (value != null && _detailId != null && _detail.style.display != DisplayStyle.None) ShowPreview();
            }
        }

        private UnitPreview _preview;

        /// <summary>An opaque page covers the lobby battle: it need not be drawn or run.</summary>
        public bool CoversBattle => _overlays.Count > 0 || _tab != Tab.Home;

        public Tab CurrentTab => _tab;

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
            foreach (var (t, item) in _navItems) item.Selected = t == tab;
            if (tab == Tab.Shop) SkinPreviewed?.Invoke(null);
            if (tab == Tab.Campaign) CampaignShown();
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
        /// The Android back button (and the top bar's Back): closes what is on top (a dialog, a page,
        /// a campaign chapter), else goes home. Returns false at home, where there is nothing to close.
        /// </summary>
        public bool Back()
        {
            // The topmost dialog closes. The story card is a scrim too and stays in the menu while hidden:
            // it hides, never leaves (a Back that took it out left Start with nothing to show, DECISIONS 21B).
            VisualElement dialog = null;
            foreach (var scrim in Root.Query(className: KitDialog.ScrimClass).ToList())
                if (_story == null || scrim != _story.Root || _story.Visible) dialog = scrim;
            if (dialog != null)
            {
                if (_story != null && dialog == _story.Root) _story.Hide();
                else dialog.RemoveFromHierarchy();
                return true;
            }
            if (_overlays.Count == 0 && _tab == Tab.Army && _armyView == ArmyView.Base && _base.Back()) return true;
            if (_overlays.Count == 0 && _tab == Tab.Army && _armyView == ArmyView.Outpost && _outpost.Back()) return true;
            if (_overlays.Count > 0)
            {
                CloseTop();
                UpdateChrome();
                Refresh();
                return true;
            }
            if (_tab == Tab.Campaign && CampaignBack()) return true;
            if (_tab == Tab.Home) return false;
            ShowTab(Tab.Home);
            return true;
        }

        private void UpdateChrome()
        {
            var overlay = _overlays.Count > 0;
            _nav.style.display = overlay ? DisplayStyle.None : DisplayStyle.Flex;
            // A page opened over the tabs covers them: the tab under it is hidden (not drawn, not tapped), its state kept.
            foreach (var (_, page) in _tabPages) page.style.visibility = overlay ? Visibility.Hidden : Visibility.Visible;
            _backButton.style.display = overlay || (_tab == Tab.Campaign && _campaignChapter > 0) ? DisplayStyle.Flex : DisplayStyle.None;
            var home = !overlay && _tab == Tab.Home;
            _logo.style.display = home ? DisplayStyle.Flex : DisplayStyle.None;
            _pageTitle.style.display = home ? DisplayStyle.None : DisplayStyle.Flex;
            _pageTitle.text = Kit.Caps(overlay ? _overlays.Peek().title : TabTitle());
            Backdrop.style.display = CoversBattle ? DisplayStyle.Flex : DisplayStyle.None;
            _homeScrim.style.display = CoversBattle ? DisplayStyle.None : DisplayStyle.Flex;
        }

        private string TabTitle() => _tab == Tab.Campaign && _campaignChapter > 0
            ? Strings.Format("campaign.chapterTitle", ("chapter", Campaign.ChapterName(_campaignChapter)), ("title", Strings.Get($"chapter.{_campaignChapter}.title")))
            : Strings.Get(NavKey(_tab));

        private static string NavKey(Tab tab)
        {
            foreach (var (t, _, key) in NavItems)
                if (t == tab)
                    return key;
            return "nav.home";
        }

        /// <summary>A tab's page: the area right of the rail, under the top bar.</summary>
        private VisualElement TabPage(Tab tab, string classes = "")
        {
            var page = Kit.Box("fc-page " + classes, PickingMode.Ignore);
            page.style.display = DisplayStyle.None;
            _tabPages[tab] = page;
            Root.Add(page);
            return page;
        }

        /// <summary>A full-screen page (under the top bar, over the rail).</summary>
        private VisualElement FullPage(string classes = "")
        {
            var page = Kit.Box("fc-page fc-page--full fc-page--opaque " + classes, PickingMode.Position);
            page.style.display = DisplayStyle.None;
            Root.Add(page);
            return page;
        }

        // ------------------------------------------------------------------ refresh

        private void Refresh()
        {
            foreach (var refresh in _refreshers) refresh();
            _coins.Coins = PlayerProfile.Coins;
            _rankLabel.text = Kit.Caps(Strings.Format("profile.rank", PlayerProfile.Level));
            _xpBar.Value = PlayerProfile.Xp / (float)Mathf.Max(1, PlayerProfile.XpForNext);
            _xpLabel.text = Strings.Format("profile.xp", ("xp", Kit.Count(PlayerProfile.Xp)), ("next", Kit.Count(PlayerProfile.XpForNext)));
            RefreshHome();
            RefreshArmy();
            RefreshShop();
            RefreshCampaign();
            RefreshOperationsTab();
            RefreshDetail();
            RefreshDots();
        }

        /// <summary>Red dots only for something to do now (Clash Royale's rule): an affordable rank-up, a reward to claim, a free crate.</summary>
        private void RefreshDots()
        {
            var upgrade = false;
            foreach (var id in MatchSettings.AllVehicles)
                if (PlayerProfile.CanRankUp(id)) upgrade = true;
            foreach (var id in MatchSettings.AllSupports)
                if (PlayerProfile.CanRankUp(id)) upgrade = true;
            var claim = DailyClaimable();
            var free = PlayerProfile.FreeDealReady || (PlayerProfile.AdCratesLeft > 0 && PlayerProfile.AdCrateWait <= TimeSpan.Zero) ||
                       PlayerProfile.CrateCount(CrateKind.Battle) + PlayerProfile.CrateCount(CrateKind.Silver) +
                       PlayerProfile.CrateCount(CrateKind.Gold) + PlayerProfile.CrateCount(CrateKind.Legendary) > 0;
            _navItems[Tab.Army].ShowDot(upgrade);
            _navItems[Tab.Operations].ShowDot(claim);
            _navItems[Tab.Shop].ShowDot(free);
            _navItems[Tab.Home].ShowDot(false);
            _navItems[Tab.Campaign].ShowDot(false);
        }

        private static bool DailyClaimable()
        {
            for (var i = 0; i < DailyMissions.Current.Count; i++)
                if (DailyMissions.Done(i) && !DailyMissions.Claimed(i)) return true;
            return false;
        }

        // ------------------------------------------------------------------ settings (a full-screen page from the gear)

        private void BuildSettingsPage()
        {
            _settings = FullPage("fc-settings-page");
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            _settings.Add(scroll);
            var body = Kit.Box("fc-page__body fc-settings");
            scroll.Add(body);

            var display = Section(body, "settings.section.display");
            display.Add(OptionRow("resize", "settings.textSize", new[] { Strings.Get("kit.textNormal"), Strings.Get("kit.textLarge") },
                () => (int)MatchSettings.TextSize, i =>
                {
                    MatchSettings.TextSize = (TextSize)i;
                    // Applies at once: every kit screen reads its type sizes from the root's class.
                    Kit.ApplyTextSize(Root);
                }));
            display.Add(OptionRow("resize", "settings.ui",
                new[] { Strings.Get("settings.small"), Strings.Get("settings.normal"), Strings.Get("settings.large") },
                () => MatchSettings.UiSize, i => MatchSettings.UiSize = i));
            display.Add(OptionRow("globe", "settings.language", new[] { Strings.Get("settings.auto"), "English", "Tiếng Việt" },
                () => (int)MatchSettings.Language, i =>
                {
                    if ((int)MatchSettings.Language == i) return;
                    // Applies at once: the menu is rebuilt in the new language.
                    MatchSettings.Language = (LanguageChoice)i;
                    MatchSettings.Save();
                    _reopenSettings = true;
                    SettingsChanged?.Invoke();
                }));
            // Prompt 11 A9: the compact battle HUD, on by default; off shows the full one.
            display.Add(ToggleRow("expand", "settings.compactHud", () => MatchSettings.CompactHud, on => MatchSettings.CompactHud = on));
            display.Add(ToggleRow("a_g3", "settings.showNumbers", () => MatchSettings.ShowCombatNumbers, on => MatchSettings.ShowCombatNumbers = on));
            var legendRow = Kit.Box("fc-setting");
            legendRow.Add(Kit.Icon("info"));
            legendRow.Add(Kit.Text(Strings.Get("combat.legend.open"), "fc-body fc-setting__label"));
            legendRow.Add(new KitButton(ButtonTier.Text, Strings.Get("combat.legend"), OpenLegend));
            display.Add(legendRow);
            display.Add(OptionRow("eye", "settings.colorblind", new[] { Strings.Get("settings.colorsDefault"), Strings.Get("settings.colorsSafe") },
                () => MatchSettings.ColorBlind ? 1 : 0, i => MatchSettings.ColorBlind = i == 1));

            var graphics = Section(body, "settings.section.graphics");
            var preset = OptionRow("bolt", "settings.preset",
                new[] { Strings.Format("settings.autoTier", Level(MatchSettings.DetectTier())), Level(GraphicsQuality.Low),
                    Level(GraphicsQuality.Medium), Level(GraphicsQuality.High) },
                () => MatchSettings.Graphics == GraphicsQuality.Custom ? -1 : (int)MatchSettings.Graphics,
                i => MatchSettings.Graphics = (GraphicsQuality)i);
            var custom = Kit.Caption(Strings.Get("settings.custom"));
            custom.AddToClassList("fc-setting__tag");
            preset.Insert(2, custom);
            _refreshers.Add(() => custom.style.display = MatchSettings.Graphics == GraphicsQuality.Custom ? DisplayStyle.Flex : DisplayStyle.None);
            graphics.Add(preset);
            graphics.Add(OptionRow("shadow", "settings.shadows",
                new[] { Strings.Get("settings.off"), Level(GraphicsQuality.Low), Level(GraphicsQuality.Medium), Level(GraphicsQuality.High) },
                () => (int)MatchSettings.Options.Shadows, i => MatchSettings.Customise(o => o.Shadows = (ShadowLevel)i)));
            graphics.Add(OptionRow("resolution", "settings.resolution", Array.ConvertAll(GraphicsOptions.RenderScales, v => v + "%"),
                () => Array.IndexOf(GraphicsOptions.RenderScales, MatchSettings.Options.RenderScale),
                i => MatchSettings.Customise(o => o.RenderScale = GraphicsOptions.RenderScales[i])));
            graphics.Add(OptionRow("edges", "settings.aa", new[] { Strings.Get("settings.off"), "2x", "4x" },
                () => Array.IndexOf(GraphicsOptions.AntiAliasingLevels, MatchSettings.Options.AntiAliasing),
                i => MatchSettings.Customise(o => o.AntiAliasing = GraphicsOptions.AntiAliasingLevels[i])));
            // Only caps the screen can show, and only divisors of its refresh (frame pacing).
            var refresh = Mathf.RoundToInt((float)Screen.currentResolution.refreshRateRatio.value);
            var rates = Array.FindAll(GraphicsOptions.FrameRates, r => r <= 60 || (refresh >= r && refresh % r == 0));
            graphics.Add(OptionRow("gauge", "settings.framerate", Array.ConvertAll(rates, v => v.ToString()),
                () => Array.IndexOf(rates, MatchSettings.Options.FrameRate),
                i => MatchSettings.Customise(o => o.FrameRate = rates[i])));
            graphics.Add(OptionRow("battery", "settings.battery",
                new[] { Strings.Get("settings.off"), Strings.Get("settings.on"), Strings.Get("settings.auto") },
                () => MatchSettings.BatterySaver, i => MatchSettings.BatterySaver = i));
            graphics.Add(OptionRow("sun", "settings.bloom",
                new[] { Strings.Get("settings.off"), Level(GraphicsQuality.Low), Level(GraphicsQuality.High) },
                () => MatchSettings.Options.Bloom, i => MatchSettings.Customise(o => o.Bloom = i)));
            graphics.Add(Stepper("sun", Strings.Get("settings.brightness"), () => $"{MatchSettings.Brightness}%",
                step => MatchSettings.Brightness = Mathf.Clamp(MatchSettings.Brightness + step * 5, 80, 120)));
            graphics.Add(OptionRow("pine", "settings.scenery", new[] { Strings.Get("settings.sparse"), Strings.Get("settings.dense") },
                () => MatchSettings.Options.RichScenery ? 1 : 0, i => MatchSettings.Customise(o => o.RichScenery = i == 1)));
            graphics.Add(OptionRow("flame", "settings.effects", new[] { Strings.Get("settings.balanced"), Strings.Get("settings.max") },
                () => MatchSettings.Options.MaxEffects ? 1 : 0, i => MatchSettings.Customise(o => o.MaxEffects = i == 1)));

            var game = Section(body, "settings.section.game");
            // Camera shake is switched off for now (RtsCamera.ShakeEnabled), so its setting is hidden with it.
            if (CameraControl.RtsCamera.ShakeEnabled)
                game.Add(OptionRow("move", "settings.shake",
                    new[] { Strings.Get("settings.off"), Level(GraphicsQuality.Low), Strings.Get("settings.full") },
                    () => MatchSettings.ScreenShake, i => MatchSettings.ScreenShake = i));
            game.Add(ToggleRow("bolt", "settings.haptics", () => MatchSettings.Haptics, on => MatchSettings.Haptics = on));
            game.Add(ToggleRow("camera", "settings.cinematic", () => MatchSettings.CinematicMoments, on => MatchSettings.CinematicMoments = on));
            // Prompt 23 H.7: the battle's dialogue; story lines show whatever is chosen.
            game.Add(OptionRow("info", "settings.dialogue",
                new[] { Strings.Get("settings.dialogue.full"), Strings.Get("settings.dialogue.important"), Strings.Get("settings.off") },
                () => (int)MatchSettings.Dialogue, i => MatchSettings.Dialogue = (DialogueSetting)i));
            game.Add(OptionRow("camera", "settings.camera",
                new[] { Strings.Get("settings.slow"), Strings.Get("settings.normal"), Strings.Get("settings.fast") },
                () => MatchSettings.CameraSpeed, i => MatchSettings.CameraSpeed = i));
            game.Add(ToggleRow("info", "settings.fps", () => MatchSettings.ShowFps, on => MatchSettings.ShowFps = on));
            game.Add(OptionRow("ammo", "settings.ammoIcons",
                new[] { Strings.Get("settings.ammoIcons.all"), Strings.Get("settings.ammoIcons.air") },
                () => MatchSettings.AmmoIcons, i => MatchSettings.AmmoIcons = i));

            var sound = Section(body, "settings.section.sound");
            sound.Add(Stepper("volume", Strings.Get("settings.volume"), () => $"{Mathf.RoundToInt(MatchSettings.Volume * 100f)}%",
                step => MatchSettings.Volume = Mathf.Clamp01(Mathf.Round((MatchSettings.Volume + step * 0.1f) * 10f) / 10f)));
            sound.Add(Stepper("volume", Strings.Get("settings.music"),
                () => MatchSettings.MusicVolume <= 0f ? Strings.Get("settings.off") : $"{Mathf.RoundToInt(MatchSettings.MusicVolume * 100f)}%",
                step => MatchSettings.MusicVolume = Mathf.Clamp01(Mathf.Round((MatchSettings.MusicVolume + step * 0.1f) * 10f) / 10f)));
        }

        // ------------------------------------------------------------------ shared building blocks

        /// <summary>A section with its panel title; add rows to the returned box.</summary>
        private static VisualElement Section(VisualElement parent, string key)
        {
            var section = Kit.Box("fc-section");
            section.Add(Kit.Text(Kit.Caps(Strings.Get(key)), "fc-panel-title fc-section__title"));
            parent.Add(section);
            return section;
        }

        private void Set(Action change)
        {
            change();
            Refresh();
        }

        /// <summary>A settings row: an icon and a label, then its choices as chips (the chosen one filled).</summary>
        private VisualElement OptionRow(string icon, string labelKey, string[] labels, Func<int> selected, Action<int> choose)
        {
            var row = Kit.Box("fc-setting");
            row.Add(Kit.Icon(icon));
            row.Add(Kit.Text(Strings.Get(labelKey), "fc-body fc-setting__label"));
            var group = Kit.Box("fc-setting__choices");
            var chips = new List<KitChip>();
            for (var i = 0; i < labels.Length; i++)
            {
                var index = i;
                var chip = new KitChip(labels[i], false, () => Set(() => choose(index)));
                chips.Add(chip);
                group.Add(chip);
            }
            _refreshers.Add(() =>
            {
                var chosen = selected();
                for (var i = 0; i < chips.Count; i++) chips[i].Selected = i == chosen;
            });
            row.Add(group);
            return row;
        }

        /// <summary>An on/off setting: the kit's switch.</summary>
        private VisualElement ToggleRow(string icon, string labelKey, Func<bool> on, Action<bool> set)
        {
            var row = Kit.Box("fc-setting");
            row.Add(Kit.Icon(icon));
            var toggle = new KitToggle(Strings.Get(labelKey), on(), value => Set(() => set(value)));
            toggle.AddToClassList("fc-grow");
            row.Add(toggle);
            _refreshers.Add(() => toggle.On = on());
            return row;
        }

        private VisualElement Stepper(string icon, string label, Func<string> value, Action<int> step)
        {
            var row = Kit.Box("fc-setting");
            row.Add(Kit.Icon(icon));
            row.Add(Kit.Text(label, "fc-body fc-setting__label"));
            var text = Kit.Text(value(), "fc-number-small fc-setting__value");
            row.Add(new KitIconButton("minus", Strings.Format("settings.less", label), () =>
            {
                step(-1);
                text.text = value();
                VolumeChanged?.Invoke();
            }));
            row.Add(text);
            row.Add(new KitIconButton("plus", Strings.Format("settings.more", label), () =>
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
            if (Progression.IsPremium(id)) return Strings.Format("deck.lockedPremium", ("name", name), ("coins", Kit.Count(Progression.Price(id, _catalog))));
            var mission = Progression.UnlockMission(id);
            // Prompt 25 D2: story loot is won in its mission only.
            if (mission != null && Progression.IsStoryLoot(id)) return Strings.Format("deck.lockedLoot", ("name", name), ("mission", Campaign.Label(mission)));
            return mission != null
                ? Strings.Format("deck.lockedMission", ("name", name), ("mission", Campaign.Label(mission)), ("coins", Kit.Count(Progression.Price(id, _catalog))))
                : Strings.Format("deck.lockedShop", ("name", name), ("coins", Kit.Count(Progression.Price(id, _catalog))));
        }

        /// <summary>Where a locked card is won, in a few words ("Mở ở Chương 3").</summary>
        private string UnlockWhere(string id)
        {
            if (Progression.IsPremium(id)) return Strings.Get("kit.unlockShop");
            var mission = Progression.UnlockMission(id);
            // Prompt 25 D2: a card may open in an interlude ("Opens in Interlude I").
            if (mission != null && Campaign.Chapter(mission.Chapter) is { IsInterlude: true } interlude)
                return Strings.Format("kit.unlockInterlude", ("interlude", interlude.Short));
            return mission != null && mission.Chapter > 0 ? Strings.Format("kit.unlockChapter", mission.Chapter)
                : mission != null ? Strings.Format("kit.unlockMission", Campaign.Label(mission))
                : Strings.Get("kit.unlockShop");
        }

        private static string Level(GraphicsQuality tier) => Strings.Get("settings." + tier.ToString().ToLowerInvariant());

        /// <summary>A short message along the bottom of the menu (what just happened, or why not).</summary>
        /// <summary>
        /// The tower-branch rework (DECISIONS 19T, E.3): once, the towers whose remade branches moved the player's choice, and
        /// that their next change is free.
        /// </summary>
        private void ShowBranchNews()
        {
            var news = PlayerProfile.TakeBranchNews();
            if (news.Count == 0) return;
            var names = string.Join(", ", news.Select(t => Strings.Card(t) + (PlayerProfile.TowerBranch(t) is { } b ? " (" + Strings.Branch(b) + ")" : "")));
            VisualElement scrim = null;
            var ok = new KitButton(ButtonTier.Primary, Strings.Get("kit.ok"), () => scrim?.RemoveFromHierarchy());
            scrim = KitDialog.Present(Root, KitDialog.Build(Strings.Get("news.branches.title"), Strings.Format("news.branches", names), ok));
        }

        /// <summary>DECISIONS 23D: an old save's doctrines were refunded at this load; say so once.</summary>
        private void ShowRefundNews()
        {
            var coins = PlayerProfile.TakeRefundNews();
            if (coins <= 0) return;
            VisualElement scrim = null;
            var ok = new KitButton(ButtonTier.Primary, Strings.Get("kit.ok"), () => scrim?.RemoveFromHierarchy());
            scrim = KitDialog.Present(Root, KitDialog.Build(Strings.Get("news.refund.title"), Strings.Format("news.refund", ("coins", Kit.Count(coins))), ok));
        }

        private void Note(string text, bool warn = false) => KitToast.Show(_note, text, warn ? ToastKind.Alert : ToastKind.Info, 3f);

        private readonly VisualElement _note;

        // ------------------------------------------------------------------ the screenshot tool's and the checks' way in

        /// <summary>The screens the rebuild covers, by name (UiShots and UiLayoutTests open each in turn).</summary>
        internal static readonly string[] ScreenNames =
        {
            "home", "setup-mode", "setup-map", "campaign", "campaign-chapter", "briefing", "dossier", "dossier-intel", "comic", "operations", "army-deck", "army-deck-supports", "army-deck-air", "army-towers", "army-gear", "army-gear-picked", "army-base", "army-base-picked", "army-base-ranges", "army-outpost", "detail-tower", "detail-module",
            "detail", "detail-action", "detail-tower-action", "detail-module-action", "shop-deals", "shop-crates", "shop-coins", "shop-skins", "shop-units", "shop-items", "settings",
            "legend", "detail-weapons", "detail-armour", "detail-boss", "detail-boss-stats",
            // Prompt 22 F.4: the commander picker and the dossier's commander pages.
            "commanders", "dossier-commanders",
        };

        /// <summary>Opens one of <see cref="ScreenNames"/> (a fresh menu shows home).</summary>
        internal void DebugShow(string screen)
        {
            switch (screen)
            {
                case "campaign":
                    _campaignChapter = 0;
                    ShowTab(Tab.Campaign);
                    break;
                case "campaign-chapter":
                    ShowTab(Tab.Campaign);
                    OpenChapter(Math.Max(1, Campaign.All[Campaign.Next].Chapter));
                    break;
                case "briefing":
                    ShowTab(Tab.Campaign);
                    OpenChapter(Math.Max(1, Campaign.All[Campaign.Next].Chapter));
                    ShowBriefing(Campaign.All[Campaign.Next]);
                    break;
                case "dossier":
                    ShowTab(Tab.Campaign);
                    OpenDossier();
                    break;
                case "commanders":
                    ShowTab(Tab.Army);
                    OpenCommanders();
                    break;
                case "dossier-commanders":
                    ShowTab(Tab.Campaign);
                    _dossierTab = DossierTab.Commanders;
                    OpenDossier();
                    break;
                case "dossier-intel":
                    // Prompt 22 D.7: the intel files.
                    ShowTab(Tab.Campaign);
                    _dossierTab = DossierTab.Intel;
                    OpenDossier();
                    break;
                case "comic":
                    // Prompt 22 D.8: a chapter's comic panels, all of them showing.
                    ShowTab(Tab.Campaign);
                    _comic.Show(1, null);
                    while (_comic.Shown < Narrative.ComicOf(1).Count) _comic.Next();
                    break;
                case "operations":
                    ShowTab(Tab.Operations);
                    break;
                case "army-deck":
                case "army-towers":
                case "army-gear":
                case "army-base":
                case "army-outpost":
                    _armyView = screen switch
                    {
                        "army-deck" => ArmyView.Deck, "army-towers" => ArmyView.Towers, "army-gear" => ArmyView.Equipment, "army-outpost" => ArmyView.Outpost,
                        _ => ArmyView.Base,
                    };
                    ShowTab(Tab.Army);
                    break;
                case "army-gear-picked":
                    // Play-test 10: the Equipment tab with a piece picked (its lines, the equip button, the list under them).
                    _armyView = ArmyView.Equipment;
                    _gearSelected = PlayerProfile.VehicleGearOwned.FirstOrDefault(g => Gear.FitsBranch(g, _branch) && !PlayerProfile.IsEquipped(g))
                                    ?? PlayerProfile.VehicleGearOwned.FirstOrDefault();
                    ShowTab(Tab.Army);
                    break;
                case "army-deck-supports":
                case "army-deck-air":
                    // Play-test 6: the collection filtered to the supports; play-test 7: to the aircraft (the AC-130 among them).
                    _armyView = ArmyView.Deck;
                    _filter = screen == "army-deck-air" ? CardFilter.Air : CardFilter.Support;
                    ShowTab(Tab.Army);
                    break;
                case "army-base-picked":
                case "army-base-ranges":
                case "army-base-ranges-picked":
                    // The base with a filled slot picked (its panel and range rings), or with the whole base's cover shown
                    // (play-test 8 A: both, the picked tower's range pulsing among the others).
                    _armyView = ArmyView.Base;
                    ShowTab(Tab.Army);
                    if (screen != "army-base-picked") _base.ToggleRanges();
                    if (screen != "army-base-ranges") _base.DebugPickFilled();
                    break;
                case "detail-armour-leviathan":
                    // Play-test 8 A: a big boss's page (the Leviathan framed by its bounds, its armour on a ship's outline).
                    ShowTab(Tab.Army);
                    DebugScrollDetail(true);
                    OpenDetail("leviathan");
                    break;
                case "detail":
                case "detail-action":
                case "detail-weapons":
                case "detail-armour":
                    ShowTab(Tab.Army);
                    // The In action tab: the theatre (DECISIONS 12E); the Weapons tab with its chips and effectiveness table (prompt 15 E2).
                    if (screen == "detail-action") _detailTab = DetailTab.Firing;
                    if (screen == "detail-weapons") _detailTab = DetailTab.Weapons;
                    if (screen is "detail-weapons" or "detail-armour") DebugScrollDetail(screen == "detail-armour");
                    OpenDetail("main_battle_tank");
                    break;
                case "detail-tower":
                case "detail-module":
                case "detail-tower-action":
                case "detail-module-action":
                    // A structure's page, opened from the base screen (its Equipment tab: branches and gear; a module's numbers; or In action).
                    _armyView = ArmyView.Base;
                    ShowTab(Tab.Army);
                    _detailTab = screen.EndsWith("-action") ? DetailTab.Firing : screen == "detail-tower" ? DetailTab.Equipment : DetailTab.Stats;
                    OpenDetail(screen.StartsWith("detail-tower") ? "aa_turret" : "repair_bay");
                    break;
                case "detail-boss":
                case "detail-boss-stats":
                    // Play-test 6 (DECISIONS 21B): a boss's page as the Boss Hunt's list opens it: its file, or its numbers.
                    ShowTab(Tab.Operations);
                    OpenBossGuide("behemoth");
                    if (screen == "detail-boss-stats")
                    {
                        _detailTab = DetailTab.Stats;
                        Refresh();
                    }
                    break;
                case "settings":
                    Open(_settings, Strings.Get("menu.settings"));
                    break;
                case "legend":
                    OpenLegend();
                    break;
                case "setup-mode":
                case "setup-map":
                    // The match setup (E7): the home's pickers, open.
                    ShowTab(Tab.Home);
                    (screen == "setup-mode" ? _modeDrop : _mapDrop).Open();
                    break;
                default:
                    if (screen.StartsWith("shop-") && Enum.TryParse<ShopTab>(screen.Substring(5), true, out var shop)) OpenShop(shop);
                    else ShowTab(Tab.Home);
                    break;
            }
        }
    }

    internal sealed partial class MenuScreen
    {
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

    /// <summary>Which icon each card shows. Towers, modules, the HQ and fixed defences have their own (<see cref="TowerIcons"/>).</summary>
    public static class CardIcons
    {
        public static string For(string id) => TowerIcons.For(id) ?? id switch
        {
            "scout_jeep" => "jeep",
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
            "command_vehicle" => "command",
            "wheeled_gun" => "wheeledgun",
            "counter_battery_radar" => "cbradar",
            "long_sam" => "longsam",
            "uav_scan" => "drone",
            "remote_mines" => "mine",
            "field_tower" => "tower",
            "sead_strike" => "sead",
            "thermobaric_launcher" => "thermo",
            "heavy_aa" => "heavyaa",
            "titan_tank" => "titan",
            "twin_tank" => "twintank",
            "siege_tank" => "siegetank",
            "atgm_carrier" => "atgm",
            "heavy_rocket_artillery" => "smerch",
            "ballistic_launcher" => "ballistic",
            "engineer_vehicle" => "engineer",
            "ammo_carrier" => "engineer",
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
            // Prompt 17 C.
            "stealth_fighter" => "fighter",
            "wingman_drone" => "drone",
            "laser_tank" => "laser",
            "shield_carrier" => "shield",
            "bunker_vehicle" => "siegegun",
            "swarm_carrier" => "fpvtruck",
            // Prompt 25 F2 batch A (DECISIONS 25F2-A).
            "aa_gun_vehicle" => "aa",
            "shorad_vehicle" => "sam",
            "microwave_vehicle" => "jammer",
            "nlos_atgm_vehicle" => "atgm",
            "radar_atgm_vehicle" => "atgm",
            "recoilless_jeep" => "jeep",
            "airborne_vehicle" => "ifv",
            "wheeled_howitzer" => "artillery",
            "sp_mortar" => "mortar",
            "glide_bomber" => "b52",
            "recon_jet" => "fighter",
            "interceptor_jet" => "fighter",
            "radar_scout" => "armoredcar",
            "fibre_fpv_carrier" => "fpvtruck",
            "interceptor_drone_vehicle" => "drone",
            // (batch A icons: new entries above)
            // Prompt 25 F2 batch B (DECISIONS 25F2-B): the 26 non-tower stand-ins, an existing glyph each.
            "aa_57mm_vehicle" => "aa",
            "mine_rocket_truck" => "mlrs",
            "prop_attack_plane" => "su25",
            "light_attack_heli" => "gunship",
            "next_gen_tank" => "titan",
            "demolition_line_vehicle" => "engineer",
            "combat_wreck_car" => "armoredcar",
            "drone_hijack_vehicle" => "jammer",
            "river_patrol_boat" => "technical",
            "river_gunboat" => "artillery",
            "coastal_ashm_vehicle" => "missile",
            "auto_loader_howitzer" => "artillery",
            "amphib_light_vehicle" => "ifv",
            "airborne_light_tank" => "lighttank",
            "stealth_naval_strike" => "b2",
            "twin_rotor_gunship" => "ac130",
            "ground_drone_carrier" => "drone",
            "mobile_repair_vehicle" => "engineer",
            "radar_support_vehicle" => "armoredcar",
            "towed_at_gun" => "destroyer",
            "dazzler_vehicle" => "jammer",
            "ground_cruise_missile_vehicle" => "missile",
            "aerial_tanker" => "b52",
            "heavy_lift_helicopter" => "gunship",
            "bridging_vehicle" => "engineer",
            "gps_jammer_vehicle" => "jammer",
            // (batch B icons: new entries above)
            "napalm_strike" => "flame",
            "moab" => "bomb",
            "cluster_strike" => "airstrike",
            "reinforcements" => "reinforce",
            "field_repair" => "repair",
            "emp_blast" => "bolt",
            "shield_dome" => "shield",
            "gunship_support" => "gunship",
            "artillery_barrage" => "barrage",
            "airstrike" => "airstrike",
            "cruise_missile" => "missile",
            "smoke_screen" => "smoke",
            "repair_drop" => "repair",
            // Prompt 25 F2 batch C (DECISIONS 25F2-C): new support cards.
            "glide_bomb_strike" => "bomb",
            "guided_shell_strike" => "barrage",
            "cluster_at_strike" => "airstrike",
            "uav_loiter_strike_support" => "drone",
            "uav_loiter_strike" => "reaper",
            "ammo_resupply" => "ammo",
            "jam_storm" => "jammer",
            "illum_flare_strike" => "eye",
            "decoy_paradrop" => "reinforce",
            "decoy_tank" => "tank",
            "instant_counter_battery" => "barrage",
            "drone_intercept_strike" => "drone",
            "chaff_strike" => "smoke",
            _ when id.Contains('.') => For(id.Substring(0, id.IndexOf('.'))),
            _ => "tank",
        };
    }
}
