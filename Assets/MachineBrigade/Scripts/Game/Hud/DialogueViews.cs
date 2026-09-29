using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 23 H.2: the in-battle dialogue's one subtitle line, centred just above the tray: the speaker's short name in
    /// capitals and bold, in their side's colour (ours brighter blue, theirs a darker red), then the words in the main text
    /// colour, on a dim strip that hugs the text. At most half the screen wide and two lines, in the body size of prompt 14.
    /// No portrait, no frame, no tap: it never takes a touch. While the selection strip or the strike prompt is up it
    /// rises above them. The side colours come from the stylesheet (two hidden probes), so the colour-blind palette holds.
    /// </summary>
    internal sealed class DialogueStrip
    {
        public const string VisibleClass = "fc-dialogue--visible";

        private readonly Label _text, _ally, _enemy;
        private DialogueLine? _line;

        public DialogueStrip()
        {
            Root = Kit.Box("fc-dialogue");
            var strip = Kit.Box("fc-dialogue__strip");
            _text = Kit.Text("", "fc-dialogue__text");
            _text.enableRichText = true;
            strip.Add(_text);
            Root.Add(strip);
            _ally = Probe(Root, false);
            _enemy = Probe(Root, true);
        }

        public VisualElement Root { get; }

        /// <summary>The label with the line (the checks measure it).</summary>
        internal Label Label => _text;

        public bool Visible => Root.ClassListContains(VisibleClass);

        public void Show(in DialogueLine line)
        {
            _line = line;
            Render();
            Root.AddToClassList(VisibleClass);
        }

        /// <summary>Fades out (the words stay while they fade).</summary>
        public void Hide() => Root.RemoveFromClassList(VisibleClass);

        /// <summary>The language changed: the line on show is read again.</summary>
        public void Refresh()
        {
            if (_line != null) Render();
        }

        /// <summary>Above the selection strip (<paramref name="selection"/>) or, higher, above the strike prompt (<paramref name="targeting"/>).</summary>
        public void Raise(bool selection, bool targeting)
        {
            Root.EnableInClassList("fc-dialogue--raised", selection && !targeting);
            Root.EnableInClassList("fc-dialogue--high", targeting);
        }

        private void Render()
        {
            var line = _line.Value;
            _text.text = DialogueText.Subtitle(line.Name, line.Words, Colour(line.Enemy ? _enemy : _ally));
        }

        /// <summary>A hidden label in a side's name colour, read when a line is drawn.</summary>
        internal static Label Probe(VisualElement parent, bool enemy)
        {
            var probe = Kit.Text("", "fc-dialogue__probe " + (enemy ? "fc-dialogue__name--enemy" : "fc-dialogue__name--ally"));
            parent.Add(probe);
            return probe;
        }

        /// <summary>A probe's colour as rich text wants it ("#RRGGBB"), or null before the stylesheet reached it.</summary>
        internal static string Colour(Label probe) =>
            probe.panel == null ? null : "#" + ColorUtility.ToHtmlStringRGB(probe.resolvedStyle.color);
    }

    /// <summary>
    /// Prompt 23 H.6: the last lines of the battle, newest first, opened from the pause menu only (never from the HUD, so a
    /// tap in the fight cannot open it by mistake). Over the pause menu; Back returns to it.
    /// </summary>
    internal sealed class DialogueLogPanel
    {
        private readonly VisualElement _rows;
        private readonly Label _ally, _enemy;

        public DialogueLogPanel()
        {
            Root = Kit.Root(KitDialog.ScrimClass + " fc-overlay fc-dialogue-log");
            Root.pickingMode = PickingMode.Position;
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-dialog fc-dialogue-log__card", PickingMode.Position);
            card.Add(Kit.Text(Kit.Caps(Strings.Get("dialogue.log")), "fc-panel-title fc-dialog__title"));
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-dialogue-log__scroll");
            _rows = Kit.Box("fc-dialogue-log__rows");
            scroll.Add(_rows);
            card.Add(scroll);
            var buttons = Kit.Box("fc-dialog__buttons");
            buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("menu.back"), Hide, "retreat"));
            card.Add(buttons);
            Root.Add(card);
            _ally = DialogueStrip.Probe(Root, false);
            _enemy = DialogueStrip.Probe(Root, true);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible => Root.style.display == DisplayStyle.Flex;

        /// <summary>The rows on show (the checks read them).</summary>
        internal VisualElement Rows => _rows;

        public void Show(IReadOnlyList<DialogueEntry> log)
        {
            Kit.ApplyTextSize(Root);
            Root.style.display = DisplayStyle.Flex;
            Root.BringToFront();
            _rows.Clear();
            if (log == null || log.Count == 0)
            {
                _rows.Add(Kit.Text(Strings.Get("dialogue.log.empty"), "fc-body-2"));
                return;
            }
            for (var i = log.Count - 1; i >= 0; i--)
            {
                var line = log[i].Line;
                var row = Kit.Text(DialogueText.Subtitle(line.Name, line.Words, DialogueStrip.Colour(line.Enemy ? _enemy : _ally)),
                    "fc-body fc-dialogue-log__row");
                row.enableRichText = true;
                _rows.Add(row);
            }
        }

        public void Hide() => Root.style.display = DisplayStyle.None;
    }
}
