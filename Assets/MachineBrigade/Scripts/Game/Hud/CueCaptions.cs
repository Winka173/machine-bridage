using System;
using MachineBrigade.Game.Effects;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// MVA W2-B (spec parts BG, BH, BQ; Settings "Warning captions"): captions for the critical non-speech cues, read off
    /// CueFeed the moment each warning sound starts: "[Incoming artillery] ←", "[Top attack]", "[Boss super weapon charging]",
    /// "[Mine detected]", "[EMP]". At most <see cref="Lines"/> at once, newest on top; one kind within <see cref="MergeSeconds"/>
    /// s is one line with a count (a salvo is not a wall of text). An arrow gives the side the cue comes from when its spot is
    /// off the screen (spec part BH's optional direction). The P0 lines (super weapons, super-heavy strikes) carry a thick
    /// amber bar as well as their colour (spec part AM: never colour alone). Small arms are never captioned (only CueFeed
    /// cues are). The radio's spoken lines already show as text (DialogueViews), so speech needs no caption here.
    /// </summary>
    internal sealed class CueCaptions : IDisposable
    {
        internal const int Lines = 3;
        internal const float Seconds = 2.6f;
        internal const float MergeSeconds = 1.5f;

        private readonly VisualElement _box;
        private readonly Label[] _labels = new Label[Lines];
        private readonly ThreatType[] _type = new ThreatType[Lines];
        private readonly float[] _until = new float[Lines];
        private readonly float[] _last = new float[Lines];
        private readonly int[] _count = new int[Lines];
        private readonly Vector3[] _at = new Vector3[Lines];
        private bool _dirty;

        public CueCaptions(VisualElement root)
        {
            _box = new VisualElement { name = "cue-captions", pickingMode = PickingMode.Ignore };
            _box.style.position = Position.Absolute;
            _box.style.left = 0;
            _box.style.right = 0;
            _box.style.bottom = Length.Percent(24f);
            _box.style.alignItems = Align.Center;
            for (var i = 0; i < Lines; i++)
            {
                var label = new Label { pickingMode = PickingMode.Ignore };
                label.style.backgroundColor = new Color(0.04f, 0.05f, 0.06f, 0.78f);
                label.style.color = Color.white;
                label.style.fontSize = 22;
                label.style.unityFontStyleAndWeight = FontStyle.Bold;
                label.style.paddingLeft = 12;
                label.style.paddingRight = 12;
                label.style.paddingTop = 3;
                label.style.paddingBottom = 3;
                label.style.marginTop = 4;
                label.style.borderTopLeftRadius = 4;
                label.style.borderTopRightRadius = 4;
                label.style.borderBottomLeftRadius = 4;
                label.style.borderBottomRightRadius = 4;
                label.style.display = DisplayStyle.None;
                _labels[i] = label;
                _box.Add(label);
            }
            root.Add(_box);
            CueFeed.Raised += OnCue;
        }

        /// <summary>Lines showing now (tests).</summary>
        internal int Showing
        {
            get
            {
                var n = 0;
                for (var i = 0; i < Lines; i++)
                    if (_until[i] > Time.unscaledTime) n++;
                return n;
            }
        }

        private void OnCue(CueEvent e)
        {
            if (!Match.MatchSettings.Captions) return;
            for (var i = 0; i < Lines; i++)
                if (_until[i] > e.Time && _type[i] == e.Type && e.Time - _last[i] < MergeSeconds)
                {
                    _count[i]++;
                    _last[i] = e.Time;
                    _until[i] = e.Time + Seconds;
                    _at[i] = e.At;
                    _dirty = true;
                    return;
                }
            for (var i = Lines - 1; i > 0; i--)
            {
                _type[i] = _type[i - 1];
                _until[i] = _until[i - 1];
                _last[i] = _last[i - 1];
                _count[i] = _count[i - 1];
                _at[i] = _at[i - 1];
            }
            _type[0] = e.Type;
            _until[0] = e.Time + Seconds;
            _last[0] = e.Time;
            _count[0] = 1;
            _at[0] = e.At;
            _dirty = true;
            ViewTelemetry.Caption();
        }

        public void Tick()
        {
            var now = Time.unscaledTime;
            var camera = Camera.main;
            for (var i = 0; i < Lines; i++)
            {
                var label = _labels[i];
                var live = _until[i] > now && Match.MatchSettings.Captions;
                if (!live)
                {
                    if (label.style.display != DisplayStyle.None) label.style.display = DisplayStyle.None;
                    continue;
                }
                var text = Strings.Get("caption." + _type[i]) + Arrow(camera, _at[i]) + (_count[i] > 1 ? " x" + _count[i] : string.Empty);
                if (_dirty || label.text != text) label.text = text;
                var critical = ThreatCues.For(_type[i]).Priority == Audio.AudioClass.P0;
                label.style.borderLeftWidth = critical ? 6 : 2;
                label.style.borderLeftColor = critical ? new Color(1f, 0.62f, 0.1f) : new Color(0.9f, 0.9f, 0.9f, 0.8f);
                // The last half second fades out.
                label.style.opacity = Mathf.Clamp01((_until[i] - now) / 0.5f);
                label.style.display = DisplayStyle.Flex;
            }
            _dirty = false;
        }

        /// <summary>" ←" / " →" / " ↑" / " ↓" when the cue's spot is off the screen; nothing when it is on it.</summary>
        internal static string Arrow(Camera camera, Vector3 at)
        {
            if (camera == null) return string.Empty;
            var p = camera.WorldToViewportPoint(at);
            if (p.z > 0f && p.x >= 0.05f && p.x <= 0.95f && p.y >= 0.05f && p.y <= 0.95f) return string.Empty;
            var dx = p.x - 0.5f;
            var dy = p.y - 0.5f;
            if (p.z < 0f)
            {
                dx = -dx;
                dy = -dy;
            }
            return Mathf.Abs(dx) >= Mathf.Abs(dy) ? (dx < 0f ? " ←" : " →") : (dy < 0f ? " ↓" : " ↑");
        }

        public void Dispose()
        {
            CueFeed.Raised -= OnCue;
            _box.RemoveFromHierarchy();
        }
    }
}
