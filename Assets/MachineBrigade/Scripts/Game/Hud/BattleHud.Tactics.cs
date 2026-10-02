using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 28 on the battle HUD: the compact tactic-switch control on the commander's rail with its cooldown and
    /// transition (H.6), the low-priority AI hint line (B.7, on the start hint's bar, off in Settings), and one small
    /// picker panel shared by the tactic switch (with the enemy's tactic once scouted, H.8, and the per-squad tactics,
    /// H.10) and a tower's targeting mode (E.1).
    /// </summary>
    public sealed partial class BattleHud
    {
        private VisualElement _tacticMini;
        private Label _tacticMiniText;
        private KitButton _tacticButton;
        private PickPanel _pick;
        private string _tacticShown;

        /// <summary>The tactic control was tapped.</summary>
        public event Action TacticPressed;

        /// <summary>The picker is open (the battle keeps running under it).</summary>
        public bool PickerShown => _pick != null && _pick.Visible;

        /// <summary>Puts the tactic control on the commander's rail (compact: an icon with the seconds left; full: a button).</summary>
        private void AddTacticControl(VisualElement rail, bool compact)
        {
            if (compact)
            {
                _tacticMini = Kit.Tappable("fc-hud__tool fc-hud__tactic", () => TacticPressed?.Invoke());
                var face = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-hud__tool-face");
                face.Add(Kit.Icon("flag"));
                _tacticMiniText = Kit.Text("", "fc-number-small fc-hud__tool-text");
                face.Add(_tacticMiniText);
                _tacticMini.Add(face);
                _tacticMini.tooltip = Strings.Get("tactic.switch");
                _tacticMini.style.display = DisplayStyle.None;
                rail.Add(_tacticMini);
            }
            else
            {
                _tacticButton = new KitButton(ButtonTier.Secondary, Strings.Get("tactic.switch"), () => TacticPressed?.Invoke(), "flag");
                _tacticButton.AddToClassList("fc-hud__tower");
                _tacticButton.style.display = DisplayStyle.None;
                rail.Add(_tacticButton);
            }
        }

        private void AddPickPanel()
        {
            _pick = new PickPanel();
            _safe.Add(_pick.Root);
        }

        /// <summary>
        /// The tactic control: hidden without a tactic (no layered AI); the seconds until the next switch, the
        /// transition's regrouping, or a free switch (Boss Hunt's rest) in its tooltip.
        /// </summary>
        public void SetTactic(string name, float cooldown, bool transition, bool free)
        {
            var shown = name != null;
            var line = !shown ? "" : free ? Strings.Get("tactic.switch") : transition ? Strings.Get("tactic.transition")
                : cooldown > 0f ? Strings.Format("tactic.cooldown", ("seconds", Mathf.CeilToInt(cooldown))) : Strings.Get("tactic.switch");
            var key = shown ? name + "|" + line : null;
            if (key == _tacticShown) return;
            _tacticShown = key;
            if (_tacticMini != null)
            {
                _tacticMini.style.display = shown ? DisplayStyle.Flex : DisplayStyle.None;
                _tacticMiniText.text = shown && !free && cooldown > 0f ? Mathf.CeilToInt(cooldown).ToString() : "";
                _tacticMini.tooltip = shown ? name + " · " + line : "";
                _tacticMini.EnableInClassList("fc-hud__tactic--busy", transition);
            }
            if (_tacticButton != null)
            {
                _tacticButton.style.display = shown ? DisplayStyle.Flex : DisplayStyle.None;
                if (shown) _tacticButton.Label = !free && cooldown > 0f ? name + " · " + Mathf.CeilToInt(cooldown) : name;
                _tacticButton.tooltip = line;
            }
        }

        /// <summary>B.7: one AI hint on the hint bar for a few seconds (never over an attack-move or box-select hint).</summary>
        public void ShowAiHint(string text, float seconds = 5f)
        {
            if (_hint == null || string.IsNullOrEmpty(text) || _hintUntil == float.MaxValue) return;
            _hint.text = text;
            _hintUntil = Time.unscaledTime + seconds;
        }

        /// <summary>
        /// The shared picker: a title, status lines, the options (the current one marked), and an extra block (the
        /// per-squad tactics). A choice calls <paramref name="chosen"/> and closes it; a tap beside the card closes it.
        /// </summary>
        public void ShowPicker(string title, IReadOnlyList<string> status, IReadOnlyList<(string label, string detail, bool current)> options,
            Action<int> chosen, VisualElement extra = null)
        {
            if (_pick == null) return;
            _pick.Show(title, status, options, chosen, extra);
        }

        public void HidePicker() => _pick?.Hide();
    }

    /// <summary>The prompt 28 picker panel (tactic switch, tower targeting mode): a scrolling card over a scrim.</summary>
    internal sealed class PickPanel
    {
        private readonly Label _title;
        private readonly VisualElement _status, _options, _extra;

        public PickPanel()
        {
            Root = Kit.Root(KitDialog.ScrimClass + " fc-overlay fc-choice fc-pick");
            Root.pickingMode = PickingMode.Position;
            Root.RegisterCallback<PointerDownEvent>(e =>
            {
                if (e.target == Root) Hide();
            });
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-dialog fc-pick__card", PickingMode.Position);
            var head = Kit.Box("fc-row fc-mb-2");
            head.Add(Kit.Icon("flag", "fc-choice__icon"));
            _title = Kit.Text("", "fc-panel-title fc-row-text fc-grow");
            head.Add(_title);
            head.Add(new KitButton(ButtonTier.Text, Strings.Get("target.cancel"), Hide, "close"));
            card.Add(head);
            _status = Kit.Box("fc-pick__status");
            card.Add(_status);
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-pick__scroll");
            _options = Kit.Box("fc-pick__options");
            scroll.Add(_options);
            _extra = Kit.Box("fc-pick__extra");
            scroll.Add(_extra);
            card.Add(scroll);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible => Root.style.display == DisplayStyle.Flex;

        public void Show(string title, IReadOnlyList<string> status, IReadOnlyList<(string label, string detail, bool current)> options,
            Action<int> chosen, VisualElement extra)
        {
            Kit.ApplyTextSize(Root);
            _title.text = Kit.Caps(title);
            _status.Clear();
            if (status != null)
                foreach (var line in status)
                    if (!string.IsNullOrEmpty(line)) _status.Add(Kit.Text(line, "fc-body-2 fc-row-text"));
            _options.Clear();
            for (var i = 0; i < options.Count; i++)
            {
                var index = i;
                var option = Kit.Box("fc-pick__option");
                var button = new KitButton(options[i].current ? ButtonTier.Primary : ButtonTier.Secondary, options[i].label, () =>
                {
                    Hide();
                    chosen(index);
                }, options[i].current ? "check" : null);
                option.Add(button);
                if (!string.IsNullOrEmpty(options[i].detail)) option.Add(Kit.Text(options[i].detail, "fc-small fc-choice__detail"));
                _options.Add(option);
            }
            _extra.Clear();
            if (extra != null) _extra.Add(extra);
            Root.style.display = DisplayStyle.Flex;
        }

        public void Hide() => Root.style.display = DisplayStyle.None;
    }
}
