using System;
using MachineBrigade.Game.Match;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The black curtain between scenes. Building a battle takes a moment in one frame (the map,
    /// the models, the effects), which used to freeze the menu mid-tap as if the button had not
    /// worked. Now the screen fades to black with the sound, shows what is being loaded, the new
    /// scene is built behind it, and once it has drawn a couple of frames (shader warm-up
    /// hitches included) the curtain fades away. It lives across scene loads.
    /// </summary>
    public sealed class Curtain : MonoBehaviour
    {
        private const float CloseSeconds = 0.3f;
        private const float OpenSeconds = 0.5f;

        /// <summary>Frames the new scene draws behind the curtain before it lifts.</summary>
        private const int HoldFrames = 3;

        private static Curtain _instance;

        private VisualElement _cover;
        private Label _status, _detail;
        private VisualElement _bar;
        private float _alpha, _target;
        private Action _then;
        private int _blackFrames;
        private int _holdFrames;

        /// <summary>How far the new scene's build has come (0-1), or below 0 for the sweeping bar.</summary>
        private float _progress = -1f;

        /// <summary>The scene being built behind the curtain reports how far it has come: the bar fills.</summary>
        public static void Progress(float done)
        {
            if (_instance == null) return;
            _instance._progress = Mathf.Clamp01(done);
        }

        /// <summary>The curtain is down or moving: a new request to leave the scene is ignored.</summary>
        public static bool Busy => _instance != null && (_instance._target > 0f || _instance._alpha > 0.001f);

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics() => _instance = null;

        /// <summary>
        /// Fades to black (and the sound out), then runs <paramref name="then"/> (a scene load)
        /// once a fully black frame is on screen. Ignored while the curtain is already coming down.
        /// </summary>
        public static void Close(string status, string detail, Action then)
        {
            var curtain = Ensure(0f);
            if (curtain._then != null) return;
            curtain._status.text = status ?? "";
            curtain._detail.text = detail ?? "";
            curtain._then = then;
            curtain._blackFrames = 0;
            curtain._progress = -1f;
            curtain._target = 1f;
            curtain._cover.pickingMode = PickingMode.Position;
            curtain._cover.style.display = DisplayStyle.Flex;
        }

        /// <summary>
        /// The curtain is down, black, at once (no fade): the first scene of a session is built
        /// behind it like every other, instead of its build showing frame by frame (test feedback
        /// 11D: the first open stuttered, the curtain only went up once the menu was built).
        /// </summary>
        public static void Cover()
        {
            var curtain = Ensure(1f);
            if (curtain._then != null) return;
            curtain._alpha = curtain._target = 1f;
            curtain._holdFrames = 0;
            if (curtain._progress < 0f) curtain._progress = 0f;
            curtain.Apply();
        }

        /// <summary>
        /// Lifts the curtain once this scene has drawn a few frames. The first scene of a session
        /// starts behind it too, so the game fades in instead of popping up.
        /// </summary>
        public static void Open()
        {
            var curtain = Ensure(1f);
            curtain._then = null;
            curtain._holdFrames = HoldFrames;
            curtain._target = 0f;
        }

        private static Curtain Ensure(float alpha)
        {
            if (_instance != null) return _instance;
            var host = new GameObject("Curtain");
            DontDestroyOnLoad(host);
            _instance = host.AddComponent<Curtain>();
            _instance.Build(host, alpha);
            return _instance;
        }

        private void Build(GameObject host, float alpha)
        {
            var settings = ScriptableObject.CreateInstance<PanelSettings>();
            settings.themeStyleSheet = Resources.Load<ThemeStyleSheet>("UI/Theme");
            settings.scaleMode = PanelScaleMode.ScaleWithScreenSize;
            settings.referenceResolution = new Vector2Int(1280, 720);
            settings.screenMatchMode = PanelScreenMatchMode.MatchWidthOrHeight;
            settings.match = 0.5f;
            settings.sortingOrder = 1000;
            var document = host.AddComponent<UIDocument>();
            document.panelSettings = settings;
            var root = document.rootVisualElement;
            root.pickingMode = PickingMode.Ignore;

            _cover = new VisualElement { pickingMode = PickingMode.Position };
            _cover.style.position = Position.Absolute;
            _cover.style.left = _cover.style.top = _cover.style.right = _cover.style.bottom = 0;
            _cover.style.backgroundColor = new Color(0.035f, 0.047f, 0.055f);
            _cover.style.alignItems = Align.Center;
            _cover.style.justifyContent = Justify.Center;
            root.Add(_cover);

            var bold = Resources.Load<Font>("Fonts/BeVietnamPro-Bold");
            var medium = Resources.Load<Font>("Fonts/BeVietnamPro-Medium");
            var logo = new IconElement("logo", 2.2f) { Tint = new Color(0.949f, 0.639f, 0.227f) };
            logo.style.width = logo.style.height = 54;
            logo.style.marginBottom = 14;
            _cover.Add(logo);
            var title = Text("MACHINE BRIGADE", bold, 26, new Color(0.945f, 0.925f, 0.886f));
            title.style.letterSpacing = 6;
            _cover.Add(title);
            _status = Text("", bold, 15, new Color(0.949f, 0.639f, 0.227f));
            _status.style.marginTop = 26;
            _status.style.letterSpacing = 3;
            _cover.Add(_status);
            _detail = Text("", medium, 13, new Color(0.62f, 0.66f, 0.68f));
            _detail.style.marginTop = 6;
            _cover.Add(_detail);
            var track = new VisualElement { pickingMode = PickingMode.Ignore };
            track.style.width = 220;
            track.style.height = 3;
            track.style.marginTop = 18;
            track.style.overflow = Overflow.Hidden;
            track.style.backgroundColor = new Color(1f, 1f, 1f, 0.08f);
            _bar = new VisualElement { pickingMode = PickingMode.Ignore };
            _bar.style.width = 70;
            _bar.style.height = 3;
            _bar.style.backgroundColor = new Color(0.949f, 0.639f, 0.227f);
            track.Add(_bar);
            _cover.Add(track);

            _alpha = _target = alpha;
            Apply();
        }

        private static Label Text(string text, Font font, int size, Color color)
        {
            var label = new Label(text) { pickingMode = PickingMode.Ignore };
            if (font != null) label.style.unityFontDefinition = FontDefinition.FromFont(font);
            label.style.fontSize = size;
            label.style.color = color;
            label.style.unityTextAlign = TextAnchor.MiddleCenter;
            return label;
        }

        private void Update()
        {
            // After a scene load the first frame's delta is the whole load; step as if it were one frame.
            var dt = Mathf.Min(Time.unscaledDeltaTime, 1f / 30f);
            if (_target < _alpha && _holdFrames > 0)
            {
                _holdFrames--;
            }
            else if (!Mathf.Approximately(_alpha, _target))
            {
                var speed = _target > _alpha ? 1f / CloseSeconds : 1f / OpenSeconds;
                _alpha = Mathf.MoveTowards(_alpha, _target, speed * dt);
            }
            // While the new scene builds, the bar fills as it goes; otherwise it sweeps across.
            if (_progress >= 0f)
            {
                _bar.style.left = 0f;
                _bar.style.width = Mathf.Lerp(_bar.resolvedStyle.width > 0f ? _bar.resolvedStyle.width : 0f, 220f * _progress, 0.5f);
                if (_target < _alpha && _alpha < 0.05f) _progress = -1f;
            }
            else
            {
                _bar.style.width = 70f;
                _bar.style.left = Mathf.Repeat(Time.unscaledTime * 180f, 290f) - 70f;
            }
            Apply();

            if (_then != null && _alpha >= 1f)
            {
                // One fully black frame on screen first, so the load happens behind black.
                if (++_blackFrames < 2) return;
                var then = _then;
                _then = null;
                then();
            }
        }

        private void Apply()
        {
            _cover.style.opacity = _alpha;
            var shown = _alpha > 0.001f || _target > 0f;
            _cover.style.display = shown ? DisplayStyle.Flex : DisplayStyle.None;
            _cover.pickingMode = shown ? PickingMode.Position : PickingMode.Ignore;
            // The sound fades with the picture.
            if (shown) AudioListener.volume = MatchSettings.Volume * (1f - _alpha);
        }
    }
}
