using System;
using System.Collections.Generic;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 20 N/O.4: the Boss Hunt's rest between two bosses, a small strip under the top bar (prompt 11's compact
    /// HUD): the rest and its seconds, the boss coming next, the supports held. The battle goes on under it.
    /// </summary>
    internal sealed class HuntRestPanel
    {
        private readonly Label _title, _time, _next, _held;
        private string _shown;

        public HuntRestPanel()
        {
            Root = Kit.Box(KitPanel.SurfaceClass + " fc-hunt-rest");
            var head = Kit.Box("fc-row");
            head.Add(Kit.Icon("repair", "fc-hunt-rest__icon"));
            _title = Kit.Text("", "fc-panel-title fc-row-text fc-hunt-rest__title");
            head.Add(_title);
            _time = Kit.Text("", "fc-number-small fc-hunt-rest__time");
            head.Add(_time);
            Root.Add(head);
            _next = Kit.Text("", "fc-body-2 fc-hunt-rest__line");
            Root.Add(_next);
            _held = Kit.Text("", "fc-small fc-hunt-rest__line");
            Root.Add(_held);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        /// <summary>Shows the rest (<paramref name="seconds"/> left); a null title hides it.</summary>
        public void Set(string title, float seconds, string next, string held)
        {
            if (title == null)
            {
                Root.style.display = DisplayStyle.None;
                _shown = null;
                return;
            }
            var key = title + next + held;
            if (key != _shown)
            {
                _shown = key;
                _title.text = Kit.Caps(title);
                _next.text = next ?? "";
                _held.text = held ?? "";
                _held.style.display = string.IsNullOrEmpty(held) ? DisplayStyle.None : DisplayStyle.Flex;
            }
            _time.text = $"{(int)seconds / 60}:{(int)seconds % 60:00}";
            Root.style.display = DisplayStyle.Flex;
        }
    }

    /// <summary>
    /// Prompt 20 N/O.4: after a main boss, one of three combat supports for the rest of the run: three cards side by
    /// side (icon, name, what it does, the pick button), and the seconds before the first is taken by itself. Built
    /// from prompt 10's kit like the stage choice; it fits a phone held sideways (three 220 pt cards).
    /// </summary>
    internal sealed class SupportPickPanel
    {
        private readonly Label _title, _time;
        private readonly VisualElement _cards;

        public SupportPickPanel()
        {
            Root = Kit.Root(KitDialog.ScrimClass + " fc-overlay fc-support-pick");
            Root.pickingMode = PickingMode.Position;
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-dialog fc-support-pick__card", PickingMode.Position);
            var head = Kit.Box("fc-row fc-mb-2");
            head.Add(Kit.Icon("star", "fc-choice__icon"));
            _title = Kit.Text("", "fc-panel-title fc-row-text");
            head.Add(_title);
            card.Add(head);
            _time = Kit.Text("", "fc-body-2 fc-mb-2");
            card.Add(_time);
            _cards = Kit.Box("fc-support-pick__cards");
            card.Add(_cards);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible => Root.style.display == DisplayStyle.Flex;

        public void Show(string title, IReadOnlyList<(string icon, string name, string info)> options, Action<int> chosen)
        {
            Kit.ApplyTextSize(Root);
            _title.text = Kit.Caps(title);
            _cards.Clear();
            for (var i = 0; i < options.Count; i++)
            {
                var index = i;
                var tile = Kit.Tappable(KitPanel.SurfaceClass + " fc-support", () => chosen(index));
                tile.Add(Kit.Icon(options[i].icon, "fc-support__icon"));
                tile.Add(Kit.Text(Kit.Caps(options[i].name), "fc-panel-title fc-support__name"));
                tile.Add(Kit.Text(options[i].info, "fc-body-2 fc-support__info"));
                tile.Add(new KitButton(i == 0 ? ButtonTier.Primary : ButtonTier.Secondary, Strings.Get("hunt.pick"), () => chosen(index), "check"));
                _cards.Add(tile);
            }
            Root.style.display = DisplayStyle.Flex;
        }

        /// <summary>The seconds left, in the line <paramref name="key"/> gives (the support pick's by default).</summary>
        public void SetTime(float seconds, string key = null) => _time.text = Strings.Format(key ?? "hunt.pickAuto", UnityEngine.Mathf.CeilToInt(seconds));

        public void Hide() => Root.style.display = DisplayStyle.None;
    }
}
