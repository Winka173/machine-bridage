using System;
using System.Collections.Generic;
using MachineBrigade.Game.Input;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.UIElements;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Hud
{
    public enum HudMode
    {
        /// <summary>Main menu over an AI battle; no battle controls.</summary>
        Menu,

        /// <summary>Both sides' score as bars round the objective chips (Conquest, Deathmatch, King of the Hill, Assault).</summary>
        Score,

        /// <summary>Army, enemies, wave and the next wave's countdown (Survival).</summary>
        Waves,

        /// <summary>A campaign mission's objective, clock and boss.</summary>
        Mission,
    }

    /// <summary>
    /// The battle HUD, built with UI Toolkit and styled by Resources/UI/Hud.uss in the 3d_astra
    /// look: top bar with the score, minimap and tools on the left, the deck along the bottom and
    /// the selection panel with command buttons on the right. Buttons keep fixed size and position
    /// in every state (V2 R09).
    /// </summary>
    public sealed class BattleHud : IDisposable
    {
        private readonly GameObject _host;
        private readonly GameObject _eventSystem;
        private readonly PanelSettings _settings;
        private readonly VisualElement _root;
        private readonly VisualElement _safe;
        private readonly Label _allies, _enemies, _wave, _next, _fps;
        private readonly IconElement _portraitIcon;
        private readonly Label _unitName, _selectedCount, _hpText;
        private readonly VisualElement _hpFill;
        private readonly VisualElement _attackMove;
        private readonly VisualElement _boxTool;
        private readonly VisualElement _toast;
        private readonly Label _toastText;
        private readonly Label _hint;
        private readonly VisualElement _hintBar;
        private readonly VisualElement _selectionBox;
        private readonly VisualElement _targeting;
        private readonly Label _targetingText;
        private readonly VisualElement _banner;
        private readonly ScoreBar _score;
        private readonly MissionBar _missionBar;
        private readonly BossBar _boss;
        private readonly VisualElement _attackStance, _defendStance, _autoDeploy, _autoStrike;
        private readonly DeckBar _deck;
        private readonly ResultPanel _result;
        private readonly PausePanel _pause;
        private readonly MenuScreen _menu;
        private readonly string _autoHint = "hint.auto";
        private float _toastUntil, _bannerUntil;
        private bool _attackArmed, _boxMode;
        private Rect _appliedSafeArea;

        public BattleHud(HudSpec spec, IReadOnlyList<CardInfo> cards, Catalog catalog)
        {
            var mode = spec.Mode;
            Mode = mode;
            Catalog = catalog;
            if (EventSystem.current == null)
                _eventSystem = new GameObject("EventSystem", typeof(EventSystem), typeof(InputSystemUIInputModule));

            _settings = ScriptableObject.CreateInstance<PanelSettings>();
            _settings.themeStyleSheet = Resources.Load<ThemeStyleSheet>("UI/Theme");
            _settings.scaleMode = PanelScaleMode.ScaleWithScreenSize;
            _settings.referenceResolution = new Vector2Int(1280, 720);
            _settings.screenMatchMode = PanelScreenMatchMode.MatchWidthOrHeight;
            _settings.match = 1f;
            _settings.scale = Match.MatchSettings.UiScale;
            _settings.sortingOrder = 10;

            _host = new GameObject("HUD");
            var document = _host.AddComponent<UIDocument>();
            document.panelSettings = _settings;
            _root = document.rootVisualElement;
            if (Match.DebugFlags.Has("-mb-no-hud")) _root.style.display = DisplayStyle.None;
            _root.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
            _root.pickingMode = PickingMode.Ignore;
            // Colour-blind safe teams re-tint every ally and enemy colour in the styles.
            _root.EnableInClassList("cb", Match.MatchSettings.ColorBlind);

            var hud = UiKit.Box("hud");
            _root.Add(hud);
            _safe = UiKit.Box("safe");
            hud.Add(_safe);

            if (mode == HudMode.Menu)
            {
                _menu = new MenuScreen(catalog, () => PlayPressed?.Invoke());
                _menu.SettingsChanged += () => SettingsChanged?.Invoke();
                _menu.VolumeChanged += () => VolumeChanged?.Invoke();
                _menu.SkinPreviewed += id => SkinPreviewed?.Invoke(id);
                _safe.Add(_menu.Root);
                _toast = UiKit.Box("toast");
                _toastText = UiKit.Text("", "toast-text");
                _selectionBox = UiKit.Box("selection-box");
                return;
            }

            // Top bar ---------------------------------------------------------------------------
            var top = UiKit.Box("topbar", PickingMode.Position);
            _safe.Add(top);
            var brand = UiKit.Box("brand");
            brand.Add(UiKit.Icon("logo", UiKit.Mint, 2f));
            var brandText = UiKit.Box("brand-text");
            brandText.Add(UiKit.Text(Strings.Get("brand.top"), "brand-top"));
            brandText.Add(UiKit.Text(Strings.Get("brand.bottom"), "brand-bottom"));
            brand.Add(brandText);
            top.Add(brand);

            var stats = UiKit.Box("stats");
            if (mode == HudMode.Score)
            {
                _score = new ScoreBar(spec.ScoreLabel);
                stats.Add(_score.Root);
            }
            else if (mode == HudMode.Mission)
            {
                _missionBar = new MissionBar();
                _missionBar.PointPressed += id => PointPressed?.Invoke(id);
                stats.Add(_missionBar.Root);
            }
            else
            {
                _allies = Stat(stats, "tank", Strings.Get("stat.allies"), UiKit.Mint);
                stats.Add(UiKit.Box("stat-divider"));
                _enemies = Stat(stats, "crosshair", Strings.Get("stat.enemies"), UiKit.Danger);
                stats.Add(UiKit.Box("stat-divider"));
                _wave = Stat(stats, "flag", Strings.Get("stat.wave"), UiKit.Amber);
                stats.Add(UiKit.Box("stat-divider"));
                _next = Stat(stats, "bolt", Strings.Get("stat.next"), UiKit.Ink);
            }
            top.Add(stats);

            var right = UiKit.Box("topbar-right");
            _fps = UiKit.Text("", "fps");
            right.Add(_fps);
            right.Add(UiKit.IconButton("pause", () => PausePressed?.Invoke()));
            top.Add(right);

            if (mode == HudMode.Mission)
            {
                _boss = new BossBar();
                _safe.Add(_boss.Root);
            }

            // Left column: minimap and tools -------------------------------------------------------
            var left = UiKit.Box("left-column");
            Minimap = new Minimap();
            Minimap.Clicked += p => MinimapClicked?.Invoke(p);
            left.Add(Minimap);
            var tools = UiKit.Box("tools");
            tools.Add(Tool("people", Strings.Get("tool.army"), () => SelectAllPressed?.Invoke()));
            _boxTool = Tool("expand", Strings.Get("tool.box"), () => BoxModeToggled?.Invoke());
            tools.Add(_boxTool);
            tools.Add(Tool("plus", "", () => ZoomPressed?.Invoke(1.25f)));
            tools.Add(Tool("minus", "", () => ZoomPressed?.Invoke(0.8f)));
            left.Add(tools);
            _safe.Add(left);

            // Commander panel: the army fights on its own; the player sets intent -------------------
            var commander = UiKit.Box("commander", PickingMode.Position);
            var commanderHead = UiKit.Box("panel-header");
            commanderHead.Add(UiKit.Text(Strings.Get("panel.commander"), "caps"));
            commander.Add(commanderHead);
            var commanderBody = UiKit.Box("commander-body");
            var stance = UiKit.Box("commander-row");
            _attackStance = Toggle(stance, "attack", Strings.Get("stance.attack"), () => StancePressed?.Invoke(false));
            _defendStance = Toggle(stance, "shield", Strings.Get("stance.defend"), () => StancePressed?.Invoke(true), "last-toggle");
            commanderBody.Add(stance);
            var autos = UiKit.Box("commander-row last-row");
            _autoDeploy = Toggle(autos, "reinforce", Strings.Get("auto.deploy"), () => AutoDeployToggled?.Invoke(), "switch");
            _autoStrike = Toggle(autos, "barrage", Strings.Get("auto.strike"), () => AutoStrikeToggled?.Invoke(), "switch last-toggle");
            commanderBody.Add(autos);
            commander.Add(commanderBody);
            _safe.Add(commander);
            if (_score != null) _score.PointPressed += id => PointPressed?.Invoke(id);

            // Command panel (hand orders for selected vehicles) -------------------------------------
            var command = UiKit.Box("command", PickingMode.Position);
            var header = UiKit.Box("command-header");
            header.Add(UiKit.Text(Strings.Get("panel.selection"), "caps"));
            _selectedCount = UiKit.Text("", "caps");
            header.Add(_selectedCount);
            command.Add(header);
            var commandBody = UiKit.Box("command-body");
            command.Add(commandBody);

            var details = UiKit.Box("details");
            var portrait = UiKit.Box("portrait");
            _portraitIcon = UiKit.Icon("tank", UiKit.Mint, 1.6f);
            portrait.Add(_portraitIcon);
            details.Add(portrait);
            var detailsText = UiKit.Box("details-text");
            _unitName = UiKit.Text("", "unit-name");
            detailsText.Add(_unitName);
            var track = UiKit.Box("hp-track");
            _hpFill = UiKit.Box("hp-fill");
            track.Add(_hpFill);
            detailsText.Add(track);
            _hpText = UiKit.Text("", "hp-text");
            detailsText.Add(_hpText);
            _counterText = UiKit.Text("", "counter-text");
            detailsText.Add(_counterText);
            details.Add(detailsText);
            commandBody.Add(details);

            var buttons = UiKit.Box("buttons");
            _attackMove = Command(buttons, "crosshair", Strings.Get("cmd.attackMove"), () => AttackMovePressed?.Invoke());
            Command(buttons, "stop", Strings.Get("cmd.stop"), () => StopPressed?.Invoke());
            Command(buttons, "retreat", Strings.Get("cmd.retreat"), () => RetreatPressed?.Invoke()).AddToClassList("last");
            commandBody.Add(buttons);
            _safe.Add(command);

            // Deck -------------------------------------------------------------------------------
            if (cards != null && cards.Count > 0)
            {
                _deck = new DeckBar(cards);
                _deck.CardPressed += i => CardPressed?.Invoke(i);
                _safe.Add(_deck.Root);
            }

            // Overlays -----------------------------------------------------------------------------
            _autoHint = spec.HintKey;
            _hint = UiKit.Text(Strings.Get(_autoHint), "hint");
            _hintBar = UiKit.Box("hint-bar");
            _hintBar.Add(_hint);
            _safe.Add(_hintBar);

            _targeting = UiKit.Box("targeting", PickingMode.Position);
            _targetingText = UiKit.Text("", "targeting-text");
            _targeting.Add(_targetingText);
            _targeting.Add(UiKit.WideButton("wide small-wide", "close", Strings.Get("target.cancel"), null, () => TargetCancelled?.Invoke()));
            _targeting.style.display = DisplayStyle.None;
            _safe.Add(_targeting);

            _banner = UiKit.Box("banner");
            _safe.Add(_banner);

            _toast = UiKit.Box("toast");
            var toastBox = UiKit.Box("toast-box");
            _toastText = UiKit.Text("", "toast-text");
            toastBox.Add(_toastText);
            _toast.Add(toastBox);
            _safe.Add(_toast);

            _pause = new PausePanel(() => ResumePressed?.Invoke(), () => RestartPressed?.Invoke(), () => MenuPressed?.Invoke());
            _safe.Add(_pause.Root);
            _result = new ResultPanel(() => RestartPressed?.Invoke(), () => MenuPressed?.Invoke(), () => DoubleRewardPressed?.Invoke(),
                () => NextMissionPressed?.Invoke());
            _safe.Add(_result.Root);

            _selectionBox = UiKit.Box("selection-box");
            _root.Add(_selectionBox);

            SetSelection(default);
        }

        public HudMode Mode { get; }

        /// <summary>Null in the menu.</summary>
        public Minimap Minimap { get; }

        public event Action SelectAllPressed;
        public event Action StopPressed;
        public event Action RetreatPressed;
        public event Action AttackMovePressed;
        public event Action RestartPressed;
        public event Action BoxModeToggled;
        public event Action<float> ZoomPressed;
        public event Action<int> CardPressed;
        public event Action TargetCancelled;
        public event Action PausePressed;
        public event Action ResumePressed;
        public event Action MenuPressed;
        public event Action PlayPressed;
        public event Action SettingsChanged;
        public event Action VolumeChanged;
        public event Action<Vector2> MinimapClicked;
        public event Action<bool> StancePressed;
        public event Action AutoDeployToggled;
        public event Action AutoStrikeToggled;
        public event Action<string> PointPressed;

        /// <summary>The shop is trying a skin on (null: back to the equipped one).</summary>
        public event Action<string> SkinPreviewed;

        /// <summary>The result screen's "watch an ad for double coins" button.</summary>
        public event Action DoubleRewardPressed;

        /// <summary>The result screen's "next mission" button (campaign).</summary>
        public event Action NextMissionPressed;

        /// <summary>Shows the commander's current intent.</summary>
        public void SetCommander(bool defend, bool autoDeploy, bool autoStrike, string focus)
        {
            if (_attackStance == null) return;
            _attackStance.EnableInClassList("on", !defend);
            _defendStance.EnableInClassList("on", defend);
            _autoDeploy.EnableInClassList("on", autoDeploy);
            _autoStrike.EnableInClassList("on", autoStrike);
            _score?.SetFocus(focus);
        }

        public bool ShowFps { get; set; }

        public void SetStats(int allies, int enemies, int wave, float secondsToNextWave, float fps)
        {
            if (_allies != null)
            {
                var seconds = Mathf.CeilToInt(secondsToNextWave);
                if (allies != _shownAllies) _allies.text = (_shownAllies = allies).ToString();
                if (enemies != _shownEnemies) _enemies.text = (_shownEnemies = enemies).ToString();
                if (wave != _shownWave) _wave.text = (_shownWave = wave).ToString();
                if (seconds != _shownSeconds) _next.text = $"{(_shownSeconds = seconds) / 60}:{seconds % 60:00}";
            }
            var shownFps = ShowFps ? Mathf.RoundToInt(fps) : -1;
            if (_fps != null && shownFps != _shownFps) _fps.text = (_shownFps = shownFps) >= 0 ? $"{shownFps} FPS" : "";
        }

        private int _shownAllies = -1, _shownEnemies = -1, _shownWave = -1, _shownSeconds = -1, _shownFps = -2;
        private SelectionSummary _shownSelection = new(-1, null, 0f, 0f);

        public void SetScore(int ours, int theirs, int max, IReadOnlyList<PointInfo> points) => _score?.Update(ours, theirs, max, points);

        /// <summary>Time left under the objective chips (negative hides it).</summary>
        public void SetTimer(float secondsLeft) => _score?.SetTimer(secondsLeft);

        public void SetMission(string goal, string detail, float progress, float secondsLeft, IReadOnlyList<PointInfo> points) =>
            _missionBar?.Update(goal, detail, progress, secondsLeft, points);

        /// <summary>The boss's health bar, hidden when <paramref name="name"/> is null.</summary>
        public void SetBoss(string name, float health) => _boss?.Set(name, health);

        public void SetDeck(float cp, float bank, int armyCp, int armyCap, IReadOnlyList<CardState> states) =>
            _deck?.Update(cp, bank, armyCp, armyCap, states);

        /// <summary>Shows the strike-targeting prompt, or hides it when <paramref name="message"/> is null.</summary>
        public void SetTargeting(string message)
        {
            if (_targeting == null) return;
            _targeting.style.display = message != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (message != null) _targetingText.text = message;
            _hintBar.style.display = message != null ? DisplayStyle.None : DisplayStyle.Flex;
        }

        /// <summary>Closes an open menu page; false when there is none (main menu or in a match).</summary>
        public bool MenuBack() => _menu != null && _menu.Back();

        public void SetPaused(bool paused)
        {
            if (_pause != null) _pause.Visible = paused;
        }

        public void ShowResult(int outcome, string subtitle, IReadOnlyList<(string, string)> rows, RewardView reward = null)
        {
            if (_pause != null) _pause.Visible = false;
            _result?.Show(outcome, subtitle, rows, reward);
        }

        private VisualElement _letterTop, _letterBottom;
        private float _shownLetterbox = -1f;

        /// <summary>Cinematic bars sliding in from the top and bottom (0 hidden, 1 fully in).</summary>
        public void SetLetterbox(float amount)
        {
            if (Mathf.Abs(amount - _shownLetterbox) < 0.01f) return;
            _shownLetterbox = amount;
            if (_letterTop == null)
            {
                _letterTop = UiKit.Box("letterbox top");
                _letterBottom = UiKit.Box("letterbox bottom");
                _root.Add(_letterTop);
                _root.Add(_letterBottom);
            }
            var height = Length.Percent(amount * 9f);
            _letterTop.style.height = height;
            _letterBottom.style.height = height;
            var display = amount > 0.001f ? DisplayStyle.Flex : DisplayStyle.None;
            _letterTop.style.display = display;
            _letterBottom.style.display = display;
        }

        private VisualElement _ad, _adClaim;
        private Label _adCount;
        private Action<bool> _adDone;
        private float _adUntil;

        /// <summary>
        /// The stand-in rewarded ad: a solid screen with a five-second countdown, then a claim
        /// button. Closing it early reports false.
        /// </summary>
        public void ShowPlaceholderAd(Action<bool> done)
        {
            if (_ad == null)
            {
                _ad = UiKit.Box("overlay ad-screen", PickingMode.Position);
                var card = UiKit.Box("ad-card");
                card.Add(UiKit.Icon("ad", UiKit.Ink, 1.8f));
                card.Add(UiKit.Text(Strings.Get("ad.title"), "ad-title"));
                card.Add(UiKit.Text(Strings.Get("ad.body"), "ad-body"));
                _adCount = UiKit.Text("", "ad-count");
                card.Add(_adCount);
                _adClaim = UiKit.WideButton("wide primary", "coin", Strings.Get("ad.claim"), null, () => CloseAd(true));
                card.Add(_adClaim);
                card.Add(UiKit.WideButton("wide", "close", Strings.Get("ad.close"), null, () => CloseAd(false)));
                _ad.Add(card);
                _safe.Add(_ad);
            }
            _adDone = done;
            _adUntil = Time.unscaledTime + 5f;
            _adClaim.style.display = DisplayStyle.None;
            _ad.style.display = DisplayStyle.Flex;
        }

        private void CloseAd(bool watched)
        {
            if (_ad == null || _ad.style.display == DisplayStyle.None) return;
            _ad.style.display = DisplayStyle.None;
            var done = _adDone;
            _adDone = null;
            done?.Invoke(watched);
        }

        private void TickAd()
        {
            if (_ad == null || _ad.style.display == DisplayStyle.None) return;
            var left = Mathf.CeilToInt(_adUntil - Time.unscaledTime);
            _adCount.text = left > 0 ? left.ToString() : "";
            if (left <= 0 && _adClaim.style.display == DisplayStyle.None) _adClaim.style.display = DisplayStyle.Flex;
        }

        /// <summary>The reward was paid (doubled after an ad): the result screen updates its numbers.</summary>
        public void ShowRewardClaimed(int coins, bool doubled) => _result?.ShowClaimed(coins, doubled);

        public bool ResultVisible => _result != null && _result.Visible;

        /// <summary>Big mission title across the screen for a few seconds.</summary>
        public void ShowBanner(string kicker, string title, string subtitle, float seconds = 3.5f)
        {
            if (_banner == null) return;
            _banner.Clear();
            var strip = UiKit.Box("mission-strip");
            strip.Add(UiKit.Text(kicker, "kicker"));
            strip.Add(UiKit.Text(title, "mission-title"));
            strip.Add(UiKit.Text(subtitle, "mission-sub"));
            var mission = UiKit.Box("mission");
            mission.Add(strip);
            _banner.Add(mission);
            _banner.AddToClassList("visible");
            _bannerUntil = Time.unscaledTime + seconds;
        }

        public void SetSelection(SelectionSummary summary)
        {
            if (_unitName == null) return;
            // Only rebuild the panel when what it shows has changed (whole hit points).
            if (summary.Count == _shownSelection.Count && summary.DefId == _shownSelection.DefId &&
                Mathf.CeilToInt(summary.Hp) == Mathf.CeilToInt(_shownSelection.Hp) &&
                Mathf.CeilToInt(summary.MaxHp) == Mathf.CeilToInt(_shownSelection.MaxHp)) return;
            _shownSelection = summary;
            if (summary.Count == 0)
            {
                _selectedCount.text = "";
                _unitName.text = Strings.Get("panel.none");
                _unitName.AddToClassList("empty");
                _hpText.text = Strings.Get("panel.noneHint");
                _hpText.AddToClassList("hint-text");
                _hpFill.style.width = Length.Percent(0f);
                _portraitIcon.Name = "tank";
                _portraitIcon.Tint = new Color(UiKit.Mint.r, UiKit.Mint.g, UiKit.Mint.b, 0.35f);
                _counterText.text = "";
                return;
            }

            _unitName.RemoveFromClassList("empty");
            _hpText.RemoveFromClassList("hint-text");
            _selectedCount.text = Strings.Format("panel.selected", summary.Count);
            _unitName.text = summary.DefId != null ? Strings.Unit(summary.DefId) : Strings.Get("panel.mixed");
            _portraitIcon.Name = summary.DefId != null ? CardIcons.For(summary.DefId) : "people";
            _portraitIcon.Tint = UiKit.Mint;
            var health = summary.MaxHp > 0f ? Mathf.Clamp01(summary.Hp / summary.MaxHp) : 0f;
            _hpFill.style.width = Length.Percent(health * 100f);
            _hpFill.EnableInClassList("hurt", health < 0.6f && health >= 0.3f);
            _hpFill.EnableInClassList("critical", health < 0.3f);
            _hpText.text = Strings.Format("panel.hp", Mathf.CeilToInt(summary.Hp), Mathf.CeilToInt(summary.MaxHp));
            // What this unit is for: who it beats and who beats it.
            _counterText.text = summary.DefId != null && Catalog != null && Catalog.Vehicles.TryGetValue(summary.DefId, out var def)
                ? MachineBrigade.Game.Match.Counters.Line(def) : "";
        }

        private Label _counterText;
        private ItemBar _items;

        /// <summary>An item button was tapped (index into the list given to <see cref="SetupItems"/>).</summary>
        public event Action<int> ItemPressed;

        /// <summary>Builds the item strip for the items the player brought into this match.</summary>
        public void SetupItems(IReadOnlyList<string> items)
        {
            if (_items != null || items.Count == 0 || _safe == null) return;
            _items = new ItemBar(items);
            _items.Pressed += i => ItemPressed?.Invoke(i);
            _safe.Add(_items.Root);
        }

        public void SetItems(IReadOnlyList<ItemState> states) => _items?.Update(states);

        /// <summary>The loaded catalog, for card and unit details.</summary>
        private Catalog Catalog { get; }

        public void SetModes(bool attackMoveArmed, bool boxMode)
        {
            if (_attackMove == null || (_attackArmed == attackMoveArmed && _boxMode == boxMode)) return;
            _attackArmed = attackMoveArmed;
            _boxMode = boxMode;
            _attackMove.EnableInClassList("armed", attackMoveArmed);
            _boxTool.EnableInClassList("on", boxMode);
            _hint.text = Strings.Get(attackMoveArmed ? "hint.attackMove" : boxMode ? "hint.box" : _autoHint);
        }

        public void ShowError(CommandError error) => Toast(Strings.Error(error), error: true);

        /// <summary>
        /// Shows a message. One that arrives while another is fresh waits its turn (a few at
        /// most), so "point lost" is not wiped by "APC on the way"; errors go straight up.
        /// </summary>
        public void Toast(string message, bool error = false, float seconds = 2.2f)
        {
            var busy = _toast.ClassListContains("visible") && Time.unscaledTime - _toastShownAt < 1.2f;
            if (busy && !error)
            {
                if (_toastQueue.Count < 3 && _toastText.text != message) _toastQueue.Enqueue((message, false, seconds));
                return;
            }
            ShowToast(message, error, seconds);
        }

        private readonly Queue<(string message, bool error, float seconds)> _toastQueue = new();
        private float _toastShownAt = -10f;

        private void ShowToast(string message, bool error, float seconds)
        {
            _toastText.text = message;
            _toastText.parent?.EnableInClassList("error", error);
            _toast.AddToClassList("visible");
            _toastShownAt = Time.unscaledTime;
            _toastUntil = Time.unscaledTime + seconds;
        }

        public void ShowSelectionBox(Vector2 fromScreen, Vector2 toScreen)
        {
            var a = ToPanel(fromScreen);
            var b = ToPanel(toScreen);
            _selectionBox.style.left = Mathf.Min(a.x, b.x);
            _selectionBox.style.top = Mathf.Min(a.y, b.y);
            _selectionBox.style.width = Mathf.Abs(b.x - a.x);
            _selectionBox.style.height = Mathf.Abs(b.y - a.y);
            _selectionBox.style.display = DisplayStyle.Flex;
        }

        public void HideSelectionBox() => _selectionBox.style.display = DisplayStyle.None;

        /// <summary>True when a screen point is over an interactive HUD element.</summary>
        public bool IsOverUi(Vector2 screen)
        {
            var panel = _root.panel;
            return panel != null && panel.Pick(ToPanel(screen)) != null;
        }

        public void Tick()
        {
            var toastDone = Time.unscaledTime > _toastUntil || (_toastQueue.Count > 0 && Time.unscaledTime - _toastShownAt > 1.2f);
            if (toastDone && _toastQueue.Count > 0)
            {
                var (message, error, seconds) = _toastQueue.Dequeue();
                ShowToast(message, error, seconds);
            }
            else if (_toast.ClassListContains("visible") && Time.unscaledTime > _toastUntil)
            {
                _toast.RemoveFromClassList("visible");
            }
            if (_banner != null && _banner.ClassListContains("visible") && Time.unscaledTime > _bannerUntil)
                _banner.RemoveFromClassList("visible");
            TickAd();
            if (Screen.safeArea != _appliedSafeArea) ApplySafeArea();
        }

        public void Dispose()
        {
            if (_host != null) Object.Destroy(_host);
            if (_eventSystem != null) Object.Destroy(_eventSystem);
            if (_settings != null) Object.Destroy(_settings);
        }

        private Vector2 ToPanel(Vector2 screen)
        {
            var panel = _root.panel;
            return panel == null ? screen : RuntimePanelUtils.ScreenToPanel(panel, new Vector2(screen.x, Screen.height - screen.y));
        }

        private void ApplySafeArea()
        {
            _appliedSafeArea = Screen.safeArea;
            if (_root.panel == null) return;
            var min = ToPanel(new Vector2(_appliedSafeArea.xMin, _appliedSafeArea.yMax));
            var max = ToPanel(new Vector2(_appliedSafeArea.xMax, _appliedSafeArea.yMin));
            var size = ToPanel(new Vector2(Screen.width, 0f));
            _safe.style.left = min.x;
            _safe.style.top = min.y;
            _safe.style.right = Mathf.Max(0f, size.x - max.x);
            _safe.style.bottom = Mathf.Max(0f, ToPanel(new Vector2(0f, 0f)).y - max.y);
        }

        private static Label Stat(VisualElement parent, string icon, string label, Color tint)
        {
            var stat = UiKit.Box("stat");
            stat.Add(UiKit.Icon(icon, tint, 1.7f));
            var column = UiKit.Box("stat-text");
            var number = UiKit.Text("0", "stat-number");
            column.Add(number);
            column.Add(UiKit.Text(label, "stat-label"));
            stat.Add(column);
            parent.Add(stat);
            return number;
        }

        private static VisualElement Tool(string icon, string label, Action onClick)
        {
            var tool = UiKit.Button("tool", onClick);
            tool.Add(UiKit.Icon(icon, UiKit.Ink, 1.7f));
            if (!string.IsNullOrEmpty(label)) tool.Add(UiKit.Text(label, "tool-label"));
            return tool;
        }

        private static VisualElement Toggle(VisualElement parent, string icon, string label, Action onClick, string extra = null)
        {
            var toggle = UiKit.Button(extra == null ? "toggle" : "toggle " + extra, onClick);
            toggle.Add(UiKit.Icon(icon, UiKit.Ink, 1.6f));
            toggle.Add(UiKit.Text(label, "toggle-label"));
            parent.Add(toggle);
            return toggle;
        }

        private static VisualElement Command(VisualElement parent, string icon, string label, Action onClick)
        {
            var button = UiKit.Button("cmd", onClick);
            button.Add(UiKit.Icon(icon, UiKit.Ink, 1.7f));
            button.Add(UiKit.Text(label, "cmd-label"));
            parent.Add(button);
            return button;
        }
    }
}
