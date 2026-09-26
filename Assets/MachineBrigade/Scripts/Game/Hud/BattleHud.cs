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
        Conquest,
        Survival,
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
        private readonly VisualElement _selectionBox;
        private readonly VisualElement _targeting;
        private readonly Label _targetingText;
        private readonly VisualElement _banner;
        private readonly ScoreBar _score;
        private readonly DeckBar _deck;
        private readonly ResultPanel _result;
        private readonly PausePanel _pause;
        private readonly MenuScreen _menu;
        private float _toastUntil, _bannerUntil;
        private bool _attackArmed, _boxMode;
        private Rect _appliedSafeArea;

        public BattleHud(HudMode mode, IReadOnlyList<CardInfo> cards, Catalog catalog)
        {
            Mode = mode;
            if (EventSystem.current == null)
                _eventSystem = new GameObject("EventSystem", typeof(EventSystem), typeof(InputSystemUIInputModule));

            _settings = ScriptableObject.CreateInstance<PanelSettings>();
            _settings.themeStyleSheet = Resources.Load<ThemeStyleSheet>("UI/Theme");
            _settings.scaleMode = PanelScaleMode.ScaleWithScreenSize;
            _settings.referenceResolution = new Vector2Int(1280, 720);
            _settings.screenMatchMode = PanelScreenMatchMode.MatchWidthOrHeight;
            _settings.match = 1f;
            _settings.sortingOrder = 10;

            _host = new GameObject("HUD");
            var document = _host.AddComponent<UIDocument>();
            document.panelSettings = _settings;
            _root = document.rootVisualElement;
            _root.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
            _root.pickingMode = PickingMode.Ignore;

            var hud = UiKit.Box("hud");
            _root.Add(hud);
            _safe = UiKit.Box("safe");
            hud.Add(_safe);

            if (mode == HudMode.Menu)
            {
                _menu = new MenuScreen(catalog, () => PlayPressed?.Invoke());
                _menu.SettingsChanged += () => SettingsChanged?.Invoke();
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
            if (mode == HudMode.Conquest)
            {
                _score = new ScoreBar();
                stats.Add(_score.Root);
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

            // Command panel ------------------------------------------------------------------------
            var command = UiKit.Box("command", PickingMode.Position);
            var header = UiKit.Box("command-header");
            header.Add(UiKit.Text(Strings.Get("panel.selection"), "caps"));
            _selectedCount = UiKit.Text("", "caps");
            header.Add(_selectedCount);
            command.Add(header);

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
            details.Add(detailsText);
            command.Add(details);

            var buttons = UiKit.Box("buttons");
            _attackMove = Command(buttons, "crosshair", Strings.Get("cmd.attackMove"), () => AttackMovePressed?.Invoke());
            Command(buttons, "stop", Strings.Get("cmd.stop"), () => StopPressed?.Invoke());
            Command(buttons, "retreat", Strings.Get("cmd.retreat"), () => RetreatPressed?.Invoke()).AddToClassList("last");
            command.Add(buttons);
            _safe.Add(command);

            // Deck -------------------------------------------------------------------------------
            if (cards != null && cards.Count > 0)
            {
                _deck = new DeckBar(cards);
                _deck.CardPressed += i => CardPressed?.Invoke(i);
                _safe.Add(_deck.Root);
            }

            // Overlays -----------------------------------------------------------------------------
            _hint = UiKit.Text(Strings.Get("hint"), "hint");
            _safe.Add(_hint);

            _targeting = UiKit.Box("targeting");
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
            _result = new ResultPanel(() => RestartPressed?.Invoke(), () => MenuPressed?.Invoke());
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
        public event Action<Vector2> MinimapClicked;

        public bool ShowFps { get; set; }

        public void SetStats(int allies, int enemies, int wave, float secondsToNextWave, float fps)
        {
            if (_allies != null)
            {
                _allies.text = allies.ToString();
                _enemies.text = enemies.ToString();
                _wave.text = wave.ToString();
                var seconds = Mathf.CeilToInt(secondsToNextWave);
                _next.text = $"{seconds / 60}:{seconds % 60:00}";
            }
            if (_fps != null) _fps.text = ShowFps ? $"{fps:0} FPS" : "";
        }

        public void SetScore(int ours, int theirs, int max, IReadOnlyList<PointInfo> points) => _score?.Update(ours, theirs, max, points);

        public void SetDeck(float cp, float bank, int armyCp, int armyCap, IReadOnlyList<CardState> states) =>
            _deck?.Update(cp, bank, armyCp, armyCap, states);

        /// <summary>Shows the strike-targeting prompt, or hides it when <paramref name="message"/> is null.</summary>
        public void SetTargeting(string message)
        {
            if (_targeting == null) return;
            _targeting.style.display = message != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (message != null) _targetingText.text = message;
            _hint.style.display = message != null ? DisplayStyle.None : DisplayStyle.Flex;
        }

        public void SetPaused(bool paused)
        {
            if (_pause != null) _pause.Visible = paused;
        }

        public void ShowResult(int outcome, string subtitle, IReadOnlyList<(string, string)> rows)
        {
            if (_pause != null) _pause.Visible = false;
            _result?.Show(outcome, subtitle, rows);
        }

        public bool ResultVisible => _result != null && _result.Visible;

        /// <summary>Big mission title across the screen for a few seconds.</summary>
        public void ShowBanner(string kicker, string title, string subtitle, float seconds = 3.5f)
        {
            if (_banner == null) return;
            _banner.Clear();
            _banner.Add(UiKit.Text(kicker, "kicker"));
            _banner.Add(UiKit.Text(title, "mission-title"));
            _banner.Add(UiKit.Text(subtitle, "mission-sub"));
            _banner.AddToClassList("visible");
            _bannerUntil = Time.unscaledTime + seconds;
        }

        public void SetSelection(SelectionSummary summary)
        {
            if (_unitName == null) return;
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
        }

        public void SetModes(bool attackMoveArmed, bool boxMode)
        {
            if (_attackMove == null || (_attackArmed == attackMoveArmed && _boxMode == boxMode)) return;
            _attackArmed = attackMoveArmed;
            _boxMode = boxMode;
            _attackMove.EnableInClassList("armed", attackMoveArmed);
            _boxTool.EnableInClassList("on", boxMode);
            _hint.text = Strings.Get(attackMoveArmed ? "hint.attackMove" : boxMode ? "hint.box" : "hint");
        }

        public void ShowError(CommandError error) => Toast(Strings.Error(error), error: true);

        public void Toast(string message, bool error = false, float seconds = 2.2f)
        {
            _toastText.text = message;
            _toastText.parent?.EnableInClassList("error", error);
            _toast.AddToClassList("visible");
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
            if (_toast.ClassListContains("visible") && Time.unscaledTime > _toastUntil) _toast.RemoveFromClassList("visible");
            if (_banner != null && _banner.ClassListContains("visible") && Time.unscaledTime > _bannerUntil)
                _banner.RemoveFromClassList("visible");
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
