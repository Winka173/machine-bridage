using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The next enemy wave before it lands (Defend, Endless): its number and countdown, then one
    /// chip per kind of vehicle in it (its icon and how many), elite ones marked; how many of the
    /// waves already sent still wait off the map for room. The wave is drawn one ahead in the
    /// simulation, so this is exactly what comes. Styled in Hud.uss (.wave-preview).
    /// </summary>
    internal sealed class WavePreview
    {
        private const int MaxChips = 8;

        private readonly Label _title, _clock, _held;
        private readonly VisualElement _chips;
        private readonly List<(VisualElement root, IconElement icon, Label count)> _slots = new();
        private readonly List<(string id, int count)> _shown = new();
        private string _shownTitle, _shownClock, _shownHeld;
        private readonly System.Func<string, (string icon, bool elite)> _describe;
        private bool _visible;

        /// <param name="describe">A vehicle's icon, and whether it is an elite (marked on its chip).</param>
        public WavePreview(System.Func<string, (string icon, bool elite)> describe)
        {
            _describe = describe;
            Root = UiKit.Box("wave-preview");
            var head = UiKit.Box("wave-preview-head");
            _title = UiKit.Text("", "wave-preview-title");
            _clock = UiKit.Text("", "wave-preview-clock");
            head.Add(_title);
            head.Add(_clock);
            Root.Add(head);
            _chips = UiKit.Box("wave-preview-chips");
            Root.Add(_chips);
            _held = UiKit.Text("", "wave-preview-held");
            Root.Add(_held);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        /// <param name="wave">The next wave (vehicle, how many), in the order it lands; empty hides the preview.</param>
        /// <param name="seconds">Seconds until it lands (negative: no waves).</param>
        /// <param name="number">Its number.</param>
        /// <param name="held">Vehicles of earlier waves still waiting off the map.</param>
        public void Set(IReadOnlyList<(string id, int count)> wave, float seconds, int number, int held)
        {
            var show = wave != null && wave.Count > 0 && seconds >= 0f;
            if (show != _visible) Root.style.display = (_visible = show) ? DisplayStyle.Flex : DisplayStyle.None;
            if (!show) return;
            var title = Strings.Format("hud.nextWave", number);
            if (title != _shownTitle) _title.text = _shownTitle = title;
            var clock = $"{(int)seconds / 60}:{(int)seconds % 60:00}";
            if (clock != _shownClock) _clock.text = _shownClock = clock;
            _clock.EnableInClassList("urgent", seconds < 10f);
            var heldText = held > 0 ? Strings.Format("hud.wavesHeld", held) : "";
            if (heldText != _shownHeld)
            {
                _held.text = _shownHeld = heldText;
                _held.style.display = heldText.Length > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            }
            if (Same(wave)) return;
            _shown.Clear();
            for (var i = 0; i < wave.Count && i < MaxChips; i++) _shown.Add(wave[i]);
            while (_slots.Count < _shown.Count)
            {
                var chip = UiKit.Box("wave-chip");
                var icon = UiKit.Icon("tank", UiKit.Ink, 1.6f);
                var count = UiKit.Text("", "wave-chip-count");
                chip.Add(icon);
                chip.Add(count);
                _chips.Add(chip);
                _slots.Add((chip, icon, count));
            }
            for (var i = 0; i < _slots.Count; i++)
            {
                var (chip, icon, count) = _slots[i];
                if (i >= _shown.Count)
                {
                    chip.style.display = DisplayStyle.None;
                    continue;
                }
                var (id, n) = _shown[i];
                chip.style.display = DisplayStyle.Flex;
                var (name, elite) = _describe(id);
                icon.Name = name;
                count.text = "×" + n;
                chip.EnableInClassList("elite", elite);
            }
        }

        private bool Same(IReadOnlyList<(string id, int count)> wave)
        {
            if (wave.Count != _shown.Count && !(wave.Count > MaxChips && _shown.Count == MaxChips)) return false;
            for (var i = 0; i < _shown.Count; i++)
                if (wave[i] != _shown[i]) return false;
            return true;
        }
    }
}
