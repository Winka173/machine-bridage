using System;
using System.Collections.Generic;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>End-of-match card: the result, a few numbers and where to go next.</summary>
    internal sealed class ResultPanel
    {
        private readonly Label _title, _subtitle;
        private readonly VisualElement _rows, _head;
        private readonly IconElement _icon;

        public ResultPanel(Action again, Action menu)
        {
            Root = UiKit.Box("overlay", PickingMode.Position);
            var card = UiKit.Box("result-card");
            _head = UiKit.Box("result-head victory");
            _icon = UiKit.Icon("trophy", UiKit.Ink, 1.8f);
            _head.Add(_icon);
            _title = UiKit.Text("", "result-title");
            _head.Add(_title);
            card.Add(_head);
            _subtitle = UiKit.Text("", "result-sub");
            card.Add(_subtitle);
            _rows = UiKit.Box("result-rows");
            card.Add(_rows);
            var buttons = UiKit.Box("result-buttons");
            buttons.Add(UiKit.WideButton("wide primary", "restart", Strings.Get("result.again"), null, again));
            buttons.Add(UiKit.WideButton("wide", "home", Strings.Get("result.menu"), null, menu));
            card.Add(buttons);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible => Root.style.display == DisplayStyle.Flex;

        /// <param name="outcome">1 victory, 0 draw, -1 defeat.</param>
        public void Show(int outcome, string subtitle, IReadOnlyList<(string label, string value)> rows)
        {
            _title.text = Strings.Get(outcome > 0 ? "result.victory" : outcome < 0 ? "result.defeat" : "result.draw");
            _head.EnableInClassList("victory", outcome > 0);
            _head.EnableInClassList("defeat", outcome < 0);
            _icon.Name = outcome < 0 ? "skull" : outcome > 0 ? "trophy" : "flag";
            _subtitle.text = subtitle;
            _rows.Clear();
            foreach (var (label, value) in rows)
            {
                var row = UiKit.Box("result-row");
                row.Add(UiKit.Text(label, "result-label"));
                row.Add(UiKit.Text(value, "result-value"));
                _rows.Add(row);
            }
            Root.style.display = DisplayStyle.Flex;
        }
    }

    /// <summary>Pause menu: resume, restart or leave.</summary>
    internal sealed class PausePanel
    {
        public PausePanel(Action resume, Action restart, Action menu)
        {
            Root = UiKit.Box("overlay", PickingMode.Position);
            var card = UiKit.Box("result-card");
            var head = UiKit.Box("result-head");
            head.Add(UiKit.Icon("pause", UiKit.Ink, 1.8f));
            head.Add(UiKit.Text(Strings.Get("pause.title"), "result-title"));
            card.Add(head);
            var buttons = UiKit.Box("result-buttons");
            buttons.Add(UiKit.WideButton("wide primary", "play", Strings.Get("pause.resume"), null, resume));
            buttons.Add(UiKit.WideButton("wide", "restart", Strings.Get("result.again"), null, restart));
            buttons.Add(UiKit.WideButton("wide", "home", Strings.Get("result.menu"), null, menu));
            card.Add(buttons);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible
        {
            get => Root.style.display == DisplayStyle.Flex;
            set => Root.style.display = value ? DisplayStyle.Flex : DisplayStyle.None;
        }
    }
}
