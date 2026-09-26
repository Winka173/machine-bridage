using System;
using MachineBrigade.Game.Input;
using MachineBrigade.Sim.Commands;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.UIElements;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The battle HUD, built with UI Toolkit and styled by Resources/UI/Hud.uss in the 3d_astra
    /// look: top bar with army counters, mission title, a tool column, and the selection panel
    /// with command buttons. Buttons keep fixed size and position in every state (V2 R09).
    /// </summary>
    public sealed class BattleHud : IDisposable
    {
        private static readonly Color Mint = new(0.647f, 0.89f, 0.749f);
        private static readonly Color Ink = new(0.89f, 0.925f, 0.9f);
        private static readonly Color Amber = new(0.875f, 0.718f, 0.463f);
        private static readonly Color Danger = new(0.94f, 0.54f, 0.45f);

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
        private readonly VisualElement _reinforce, _reinforceFill;
        private readonly Label _reinforceSub;
        private readonly VisualElement _boxTool;
        private readonly VisualElement _toast;
        private readonly Label _toastText;
        private readonly Label _hint;
        private readonly VisualElement _selectionBox;
        private float _toastUntil;
        private bool _attackArmed, _boxMode;
        private Rect _appliedSafeArea;

        public BattleHud()
        {
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

            var hud = Box("hud");
            _root.Add(hud);
            _safe = Box("safe");
            hud.Add(_safe);

            // Top bar ---------------------------------------------------------------------------
            var top = Box("topbar", PickingMode.Position);
            _safe.Add(top);
            var brand = Box("brand");
            brand.Add(Icon("logo", Mint, 2f));
            var brandText = Box("brand-text");
            brandText.Add(Text(Strings.Get("brand.top"), "brand-top"));
            brandText.Add(Text(Strings.Get("brand.bottom"), "brand-bottom"));
            brand.Add(brandText);
            top.Add(brand);

            var stats = Box("stats");
            _allies = Stat(stats, "tank", Strings.Get("stat.allies"), Mint);
            stats.Add(Box("stat-divider"));
            _enemies = Stat(stats, "crosshair", Strings.Get("stat.enemies"), Danger);
            stats.Add(Box("stat-divider"));
            _wave = Stat(stats, "flag", Strings.Get("stat.wave"), Amber);
            stats.Add(Box("stat-divider"));
            _next = Stat(stats, "bolt", Strings.Get("stat.next"), Ink);
            top.Add(stats);

            var right = Box("topbar-right");
            _fps = Text("60 FPS", "fps");
            right.Add(_fps);
            right.Add(IconButton("restart", () => RestartPressed?.Invoke()));
            top.Add(right);

            // Mission title ----------------------------------------------------------------------
            var mission = Box("mission");
            mission.Add(Text(Strings.Get("mission.kicker"), "kicker"));
            mission.Add(Text(Strings.Get("mission.title"), "mission-title"));
            mission.Add(Text(Strings.Get("mission.sub"), "mission-sub"));
            _safe.Add(mission);

            // Tools --------------------------------------------------------------------------------
            var tools = Box("tools");
            tools.Add(Tool("people", Strings.Get("tool.army"), () => SelectAllPressed?.Invoke()));
            _boxTool = Tool("expand", Strings.Get("tool.box"), () => BoxModeToggled?.Invoke());
            tools.Add(_boxTool);
            tools.Add(Tool("plus", "", () => ZoomPressed?.Invoke(1.25f)));
            tools.Add(Tool("minus", "", () => ZoomPressed?.Invoke(0.8f)));
            _safe.Add(tools);

            // Command panel ------------------------------------------------------------------------
            var command = Box("command", PickingMode.Position);
            var header = Box("command-header");
            header.Add(Text(Strings.Get("panel.selection"), "caps"));
            _selectedCount = Text("", "caps");
            header.Add(_selectedCount);
            command.Add(header);

            var details = Box("details");
            var portrait = Box("portrait");
            _portraitIcon = Icon("tank", Mint, 1.6f);
            portrait.Add(_portraitIcon);
            details.Add(portrait);
            var detailsText = Box("details-text");
            _unitName = Text("", "unit-name");
            detailsText.Add(_unitName);
            var track = Box("hp-track");
            _hpFill = Box("hp-fill");
            track.Add(_hpFill);
            detailsText.Add(track);
            _hpText = Text("", "hp-text");
            detailsText.Add(_hpText);
            details.Add(detailsText);
            command.Add(details);

            var buttons = Box("buttons");
            _attackMove = Command(buttons, "crosshair", Strings.Get("cmd.attackMove"), () => AttackMovePressed?.Invoke());
            Command(buttons, "stop", Strings.Get("cmd.stop"), () => StopPressed?.Invoke());
            Command(buttons, "retreat", Strings.Get("cmd.retreat"), () => RetreatPressed?.Invoke()).AddToClassList("last");
            command.Add(buttons);

            _reinforce = Box("reinforce", PickingMode.Position);
            _reinforceFill = Box("reinforce-fill");
            _reinforce.Add(_reinforceFill);
            _reinforce.Add(Icon("reinforce", Mint, 1.7f));
            var reinforceText = Box("reinforce-text");
            reinforceText.Add(Text(Strings.Get("cmd.reinforce"), "reinforce-title"));
            _reinforceSub = Text(Strings.Get("cmd.reinforceReady"), "reinforce-sub");
            reinforceText.Add(_reinforceSub);
            _reinforce.Add(reinforceText);
            _reinforce.AddManipulator(new Clickable(() => ReinforcePressed?.Invoke()));
            command.Add(_reinforce);
            _safe.Add(command);

            // Overlays -----------------------------------------------------------------------------
            _hint = Text(Strings.Get("hint"), "hint");
            _safe.Add(_hint);
            _toast = Box("toast");
            var toastBox = Box("toast-box");
            _toastText = Text("", "toast-text");
            toastBox.Add(_toastText);
            _toast.Add(toastBox);
            _safe.Add(_toast);
            _selectionBox = Box("selection-box");
            _root.Add(_selectionBox);

            SetSelection(default);
        }

        public event Action SelectAllPressed;
        public event Action StopPressed;
        public event Action RetreatPressed;
        public event Action AttackMovePressed;
        public event Action ReinforcePressed;
        public event Action RestartPressed;
        public event Action BoxModeToggled;
        public event Action<float> ZoomPressed;

        public void SetStats(int allies, int enemies, int wave, float secondsToNextWave, float fps)
        {
            _allies.text = allies.ToString();
            _enemies.text = enemies.ToString();
            _wave.text = wave.ToString();
            var seconds = Mathf.CeilToInt(secondsToNextWave);
            _next.text = $"{seconds / 60}:{seconds % 60:00}";
            _fps.text = $"{fps:0} FPS";
        }

        public void SetSelection(SelectionSummary summary)
        {
            if (summary.Count == 0)
            {
                _selectedCount.text = "";
                _unitName.text = Strings.Get("panel.none");
                _unitName.AddToClassList("empty");
                _hpText.text = Strings.Get("panel.noneHint");
                _hpText.AddToClassList("hint-text");
                _hpFill.style.width = Length.Percent(0f);
                _portraitIcon.Name = "tank";
                _portraitIcon.Tint = new Color(Mint.r, Mint.g, Mint.b, 0.35f);
                return;
            }

            _unitName.RemoveFromClassList("empty");
            _hpText.RemoveFromClassList("hint-text");
            _selectedCount.text = Strings.Format("panel.selected", summary.Count);
            _unitName.text = summary.DefId != null ? Strings.Unit(summary.DefId) : Strings.Get("panel.mixed");
            _portraitIcon.Name = PortraitIcon(summary.DefId);
            _portraitIcon.Tint = Mint;
            var health = summary.MaxHp > 0f ? Mathf.Clamp01(summary.Hp / summary.MaxHp) : 0f;
            _hpFill.style.width = Length.Percent(health * 100f);
            _hpFill.EnableInClassList("hurt", health < 0.6f && health >= 0.3f);
            _hpFill.EnableInClassList("critical", health < 0.3f);
            _hpText.text = Strings.Format("panel.hp", Mathf.CeilToInt(summary.Hp), Mathf.CeilToInt(summary.MaxHp));
        }

        public void SetReinforceCooldown(float remaining, float total)
        {
            var waiting = remaining > 0f;
            _reinforce.EnableInClassList("waiting", waiting);
            _reinforceFill.style.width = Length.Percent(waiting ? (1f - remaining / Mathf.Max(total, 0.01f)) * 100f : 0f);
            _reinforceSub.text = waiting
                ? Strings.Format("cmd.reinforceWait", Mathf.CeilToInt(remaining))
                : Strings.Get("cmd.reinforceReady");
        }

        public void SetModes(bool attackMoveArmed, bool boxMode)
        {
            if (_attackArmed == attackMoveArmed && _boxMode == boxMode) return;
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
            _toastText.parent.EnableInClassList("error", error);
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

        private static string PortraitIcon(string defId) => defId switch
        {
            "scout_jeep" => "jeep",
            "artillery" => "artillery",
            null => "people",
            _ => "tank",
        };

        private static VisualElement Box(string className, PickingMode picking = PickingMode.Ignore)
        {
            var element = new VisualElement { pickingMode = picking };
            element.AddToClassList(className);
            return element;
        }

        private static Label Text(string text, string className)
        {
            var label = new Label(text) { pickingMode = PickingMode.Ignore };
            label.AddToClassList(className);
            return label;
        }

        private static IconElement Icon(string name, Color tint, float stroke)
        {
            return new IconElement(name, stroke) { Tint = tint };
        }

        private static Label Stat(VisualElement parent, string icon, string label, Color tint)
        {
            var stat = Box("stat");
            stat.Add(Icon(icon, tint, 1.7f));
            var column = Box("stat-text");
            var number = Text("0", "stat-number");
            column.Add(number);
            column.Add(Text(label, "stat-label"));
            stat.Add(column);
            parent.Add(stat);
            return number;
        }

        private static VisualElement IconButton(string icon, Action onClick)
        {
            var button = Box("icon-button", PickingMode.Position);
            button.Add(Icon(icon, Ink, 1.7f));
            button.AddManipulator(new Clickable(onClick));
            return button;
        }

        private static VisualElement Tool(string icon, string label, Action onClick)
        {
            var tool = Box("tool", PickingMode.Position);
            tool.Add(Icon(icon, Ink, 1.7f));
            if (!string.IsNullOrEmpty(label)) tool.Add(Text(label, "tool-label"));
            tool.AddManipulator(new Clickable(onClick));
            return tool;
        }

        private static VisualElement Command(VisualElement parent, string icon, string label, Action onClick)
        {
            var button = Box("cmd", PickingMode.Position);
            button.Add(Icon(icon, Ink, 1.7f));
            button.Add(Text(label, "cmd-label"));
            button.AddManipulator(new Clickable(onClick));
            parent.Add(button);
            return button;
        }
    }
}
