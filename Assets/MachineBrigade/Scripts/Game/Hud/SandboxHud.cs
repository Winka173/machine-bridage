using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Commands;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.UI;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Sandbox HUD: status line, command buttons, reinforcement call, restart, error toast
    /// and the box-selection rectangle. Buttons keep fixed positions and sizes in every
    /// state (V2 R09) and are at least ~110 px tall at 1080p, well above 44 pt.
    /// Text is English for now; it moves to the localisation tables with the real menus.
    /// </summary>
    public sealed class SandboxHud : IDisposable
    {
        private static readonly Color Idle = new Color(0.08f, 0.1f, 0.08f, 0.72f);
        private static readonly Color Armed = new Color(0.55f, 0.22f, 0.12f, 0.9f);

        private readonly GameObject _root;
        private readonly RectTransform _canvas;
        private readonly RectTransform _safeArea;
        private readonly RectTransform _box;
        private readonly Text _status;
        private readonly Text _toast;
        private readonly Button _reinforce;
        private readonly Text _reinforceLabel;
        private readonly Image _attackMoveBackground;
        private readonly List<RaycastResult> _hits = new();
        private GameObject _eventSystem;
        private PointerEventData _pointer;
        private Rect _appliedSafeArea;
        private float _toastUntil;

        public SandboxHud()
        {
            EnsureEventSystem();
            _root = new GameObject("HUD", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            var canvas = _root.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 10;
            var scaler = _root.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920f, 1080f);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = 1f;
            _canvas = (RectTransform)_root.transform;

            _box = UiFactory.Rect(_canvas, "Selection Box", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero);
            var boxImage = _box.gameObject.AddComponent<Image>();
            boxImage.color = new Color(0.45f, 1f, 0.5f, 0.18f);
            boxImage.raycastTarget = false;
            _box.gameObject.SetActive(false);

            _safeArea = UiFactory.Stretch(_canvas, "Safe Area");

            _status = UiFactory.Label(UiFactory.Rect(_safeArea, "Status", new Vector2(0f, 1f), new Vector2(0f, 1f),
                new Vector2(28f, -20f), new Vector2(1100f, 110f)), 30, TextAnchor.UpperLeft);

            _toast = UiFactory.Label(UiFactory.Rect(_safeArea, "Toast", new Vector2(0.5f, 1f), new Vector2(0.5f, 1f),
                new Vector2(0f, -130f), new Vector2(1100f, 70f)), 36, TextAnchor.MiddleCenter);
            _toast.color = new Color(1f, 0.85f, 0.6f);
            _toast.gameObject.SetActive(false);

            var size = new Vector2(200f, 120f);
            const float gap = 16f;
            var labels = new (string label, Action action)[]
            {
                ("All", () => SelectAllPressed?.Invoke()),
                ("Retreat", () => RetreatPressed?.Invoke()),
                ("Stop", () => StopPressed?.Invoke()),
                ("Attack\nmove", () => AttackMovePressed?.Invoke()),
            };
            for (var i = 0; i < labels.Length; i++)
            {
                var rect = UiFactory.Rect(_safeArea, labels[i].label, new Vector2(1f, 0f), new Vector2(1f, 0f),
                    new Vector2(-28f - i * (size.x + gap), 28f), size);
                UiFactory.Button(rect, labels[i].label, labels[i].action, out _, out var background);
                if (i == labels.Length - 1) _attackMoveBackground = background;
            }

            var reinforceRect = UiFactory.Rect(_safeArea, "Reinforce", new Vector2(0f, 0f), new Vector2(0f, 0f),
                new Vector2(28f, 28f), new Vector2(280f, 120f));
            _reinforce = UiFactory.Button(reinforceRect, "Reinforce", () => ReinforcePressed?.Invoke(), out _reinforceLabel, out _);

            var restartRect = UiFactory.Rect(_safeArea, "Restart", new Vector2(1f, 1f), new Vector2(1f, 1f),
                new Vector2(-28f, -20f), new Vector2(200f, 90f));
            UiFactory.Button(restartRect, "Restart", () => RestartPressed?.Invoke(), out _, out _);

            ApplySafeArea();
        }

        public event Action SelectAllPressed;
        public event Action StopPressed;
        public event Action RetreatPressed;
        public event Action AttackMovePressed;
        public event Action ReinforcePressed;
        public event Action RestartPressed;

        public void SetStatus(string text) => _status.text = text;

        public void SetReinforceCooldown(float seconds)
        {
            var ready = seconds <= 0f;
            _reinforce.interactable = ready;
            _reinforceLabel.text = ready ? "Reinforce\n+2 vehicles" : $"Reinforce\n{Mathf.CeilToInt(seconds)} s";
        }

        public void SetAttackMoveArmed(bool armed) => _attackMoveBackground.color = armed ? Armed : Idle;

        public void ShowError(CommandError error) => Toast(Describe(error));

        public void Toast(string message, float seconds = 1.6f)
        {
            _toast.text = message;
            _toast.gameObject.SetActive(true);
            _toastUntil = Time.unscaledTime + seconds;
        }

        public void ShowSelectionBox(Vector2 fromScreen, Vector2 toScreen)
        {
            RectTransformUtility.ScreenPointToLocalPointInRectangle(_canvas, fromScreen, null, out var a);
            RectTransformUtility.ScreenPointToLocalPointInRectangle(_canvas, toScreen, null, out var b);
            _box.anchoredPosition = (a + b) * 0.5f;
            _box.sizeDelta = new Vector2(Mathf.Abs(b.x - a.x), Mathf.Abs(b.y - a.y));
            _box.gameObject.SetActive(true);
        }

        public void HideSelectionBox() => _box.gameObject.SetActive(false);

        /// <summary>True when a screen point is over any HUD element, checked with a real UI raycast.</summary>
        public bool IsOverUi(Vector2 screen)
        {
            var eventSystem = EventSystem.current;
            if (eventSystem == null) return false;
            _pointer ??= new PointerEventData(eventSystem);
            _pointer.position = screen;
            _hits.Clear();
            eventSystem.RaycastAll(_pointer, _hits);
            return _hits.Count > 0;
        }

        public void Tick()
        {
            if (_toast.gameObject.activeSelf && Time.unscaledTime > _toastUntil) _toast.gameObject.SetActive(false);
            if (Screen.safeArea != _appliedSafeArea) ApplySafeArea();
        }

        public void Dispose()
        {
            if (_root != null) Object.Destroy(_root);
            if (_eventSystem != null) Object.Destroy(_eventSystem);
        }

        private void ApplySafeArea()
        {
            var area = Screen.safeArea;
            _appliedSafeArea = area;
            if (Screen.width <= 0 || Screen.height <= 0) return;
            _safeArea.anchorMin = new Vector2(area.xMin / Screen.width, area.yMin / Screen.height);
            _safeArea.anchorMax = new Vector2(area.xMax / Screen.width, area.yMax / Screen.height);
        }

        private void EnsureEventSystem()
        {
            if (EventSystem.current != null) return;
            _eventSystem = new GameObject("EventSystem", typeof(EventSystem), typeof(InputSystemUIInputModule));
        }

        private static string Describe(CommandError error) => error switch
        {
            CommandError.NoUnits => "Select your vehicles first",
            CommandError.InvalidTarget => "That can't be attacked",
            CommandError.TargetNotVisible => "Target not visible",
            CommandError.OutOfBounds => "Outside the battlefield",
            CommandError.InvalidPoint => "Invalid destination",
            CommandError.NoRallyPoint => "No rally point",
            CommandError.MatchOver => "The match is over",
            _ => "Order refused",
        };
    }
}
