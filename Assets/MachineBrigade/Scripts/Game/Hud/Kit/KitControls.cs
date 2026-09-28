using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>Tabs on the panel background; the chosen one carries a 2 px accent underline.</summary>
    public sealed class KitTabs : VisualElement
    {
        private readonly List<VisualElement> _tabs = new();
        private readonly Action<int> _changed;

        public KitTabs(IReadOnlyList<string> labels, int selected, Action<int> changed)
        {
            _changed = changed;
            AddToClassList("fc-tabs");
            for (var i = 0; i < labels.Count; i++)
            {
                var index = i;
                var tab = Kit.Tappable("fc-tab", () => Select(index, true));
                tab.Add(Kit.Text(Kit.Caps(labels[i]), "fc-tab__label"));
                _tabs.Add(tab);
                Add(tab);
            }
            Select(selected, false);
        }

        public int Selected { get; private set; }

        public IReadOnlyList<VisualElement> Tabs => _tabs;

        public void Select(int index, bool notify)
        {
            Selected = Mathf.Clamp(index, 0, _tabs.Count - 1);
            for (var i = 0; i < _tabs.Count; i++) _tabs[i].EnableInClassList("fc-tab--selected", i == Selected);
            if (notify) _changed?.Invoke(Selected);
        }
    }

    /// <summary>
    /// A filter chip: an outline, or when chosen a text-colour face with dark text. A branch chip
    /// adds the branch's colour swatch and its class icon (a colour is never shown alone). The
    /// face is smaller than the chip's touch target.
    /// </summary>
    public sealed class KitChip : VisualElement
    {
        private readonly Action _onClick;

        public KitChip(string label, bool selected, Action onClick, string icon = null, KitBranch? branch = null)
        {
            _onClick = onClick;
            pickingMode = PickingMode.Position;
            AddToClassList("fc-chip");
            var face = Kit.Box("fc-chip__face");
            if (branch is { } b) face.Add(Kit.Box("fc-chip__swatch " + KitBranches.ColourClass(b)));
            if (icon != null) face.Add(Kit.Icon(icon, "fc-chip__icon"));
            face.Add(Kit.Text(Kit.Caps(label), "fc-chip__label"));
            Add(face);
            Selected = selected;
            this.AddManipulator(new Tap(() =>
            {
                UiKit.RaiseClicked();
                _onClick?.Invoke();
            }));
        }

        /// <summary>A branch filter: the branch's name, colour swatch and class icon.</summary>
        public static KitChip Branch(KitBranch branch, bool selected, Action onClick) =>
            new(KitBranches.Name(branch), selected, onClick, KitBranches.Icon(branch), branch);

        public bool Selected
        {
            get => ClassListContains("fc-chip--selected");
            set => EnableInClassList("fc-chip--selected", value);
        }
    }

    /// <summary>The sort button ("Sort: Level ▾"): a separate control beside the filter chips, with a caret, not a state.</summary>
    public sealed class KitSortButton : VisualElement
    {
        private readonly Label _label;

        public KitSortButton(string value, Action onClick)
        {
            pickingMode = PickingMode.Position;
            AddToClassList("fc-chip");
            AddToClassList("fc-sort");
            var face = Kit.Box("fc-chip__face");
            face.Add(Kit.Icon("sort", "fc-chip__icon"));
            _label = Kit.Text("", "fc-chip__label");
            face.Add(_label);
            face.Add(Kit.Icon("caret", "fc-chip__caret", 2.2f));
            Add(face);
            Value = value;
            this.AddManipulator(new Tap(() =>
            {
                UiKit.RaiseClicked();
                onClick?.Invoke();
            }));
        }

        public string Value
        {
            set => _label.text = Kit.Caps(Strings.Format("kit.sortBy", value));
        }
    }

    /// <summary>A row of filter chips, then a divider and the sort button on its own.</summary>
    public sealed class KitChipRow : VisualElement
    {
        public KitChipRow(IEnumerable<VisualElement> chips, KitSortButton sort = null)
        {
            AddToClassList("fc-chip-row");
            var group = Kit.Box("fc-chip-row__chips");
            foreach (var chip in chips) group.Add(chip);
            Add(group);
            if (sort == null) return;
            Add(Kit.Box("fc-chip-row__divider"));
            Add(sort);
        }
    }

    /// <summary>One choice of a dropdown: its name, an optional one-line detail and thumbnail (a map picture).</summary>
    public readonly struct KitOption
    {
        public KitOption(string label, string detail = null, Texture2D thumbnail = null)
        {
            Label = label;
            Detail = detail;
            Thumbnail = thumbnail;
        }

        public string Label { get; }
        public string Detail { get; }
        public Texture2D Thumbnail { get; }
    }

    /// <summary>
    /// A dropdown for mode, map and difficulty: its label, the current value, a caret and the
    /// value's thumbnail if it has one. A tap opens the list of choices in a dialog surface.
    /// </summary>
    public sealed class KitDropdown : VisualElement
    {
        private readonly string _label;
        private readonly IReadOnlyList<KitOption> _options;
        private readonly Action<int> _changed;
        private readonly Label _value;
        private readonly VisualElement _thumb;

        public KitDropdown(string label, IReadOnlyList<KitOption> options, int selected, Action<int> changed)
        {
            _label = label;
            _options = options;
            _changed = changed;
            pickingMode = PickingMode.Position;
            AddToClassList("fc-dropdown");
            _thumb = Kit.Box("fc-dropdown__thumb");
            Add(_thumb);
            var text = Kit.Box("fc-dropdown__text");
            text.Add(Kit.Text(Kit.Caps(label), "fc-dropdown__label"));
            _value = Kit.Text("", "fc-dropdown__value");
            text.Add(_value);
            Add(text);
            Add(Kit.Icon("caret", "fc-dropdown__caret", 2.2f));
            Select(selected, false);
            this.AddManipulator(new Tap(() =>
            {
                UiKit.RaiseClicked();
                Open();
            }));
        }

        public int Selected { get; private set; }

        public void Select(int index, bool notify)
        {
            Selected = Mathf.Clamp(index, 0, _options.Count - 1);
            var option = _options[Selected];
            _value.text = option.Label;
            var hasThumb = _options.Count > 0 && HasThumbnails();
            _thumb.style.display = hasThumb ? DisplayStyle.Flex : DisplayStyle.None;
            _thumb.style.backgroundImage = option.Thumbnail != null ? Background.FromTexture2D(option.Thumbnail) : new StyleBackground(StyleKeyword.None);
            if (notify) _changed?.Invoke(Selected);
        }

        private bool HasThumbnails()
        {
            foreach (var o in _options)
                if (o.Thumbnail != null) return true;
            return false;
        }

        /// <summary>The list of choices, over the screen; a tap on one picks it and closes the list.</summary>
        public VisualElement Open()
        {
            VisualElement scrim = null;
            var sheet = Kit.Box("fc-surface fc-picker", PickingMode.Position);
            sheet.Add(Kit.Text(Kit.Caps(_label), "fc-panel-title fc-panel__title"));
            var scroll = Kit.Scroll(ScrollViewMode.Vertical);
            scroll.AddToClassList("fc-picker__scroll");
            for (var i = 0; i < _options.Count; i++)
            {
                var index = i;
                var option = _options[i];
                var row = Kit.Tappable("fc-option", () =>
                {
                    scrim?.RemoveFromHierarchy();
                    Select(index, true);
                });
                row.EnableInClassList("fc-option--selected", i == Selected);
                if (option.Thumbnail != null)
                {
                    var thumb = Kit.Box("fc-dropdown__thumb");
                    thumb.style.backgroundImage = Background.FromTexture2D(option.Thumbnail);
                    row.Add(thumb);
                }
                var text = Kit.Box("fc-option__text");
                text.Add(Kit.Text(option.Label, "fc-body"));
                if (!string.IsNullOrEmpty(option.Detail)) text.Add(Kit.Small(option.Detail));
                row.Add(text);
                row.Add(Kit.Icon("check", "fc-option__check", 2.2f));
                scroll.Add(row);
            }
            sheet.Add(scroll);
            scrim = KitDialog.Present(this, sheet);
            return scrim;
        }
    }

    /// <summary>An on/off switch with its label (settings, Auto buy, Support): one look for every toggle.</summary>
    public sealed class KitToggle : VisualElement
    {
        private readonly Label _state;
        private readonly Action<bool> _changed;

        public KitToggle(string label, bool on, Action<bool> changed)
        {
            _changed = changed;
            pickingMode = PickingMode.Position;
            AddToClassList("fc-toggle");
            Add(Kit.Text(label, "fc-body fc-toggle__label"));
            _state = Kit.Text("", "fc-toggle__state");
            Add(_state);
            var track = Kit.Box("fc-toggle__track");
            track.Add(Kit.Box("fc-toggle__knob"));
            Add(track);
            On = on;
            this.AddManipulator(new Tap(() =>
            {
                UiKit.RaiseClicked();
                On = !On;
                _changed?.Invoke(On);
            }));
        }

        public bool On
        {
            get => ClassListContains("fc-toggle--on");
            set
            {
                EnableInClassList("fc-toggle--on", value);
                _state.text = Kit.Caps(Strings.Get(value ? "kit.on" : "kit.off"));
            }
        }
    }

    /// <summary>
    /// An item of the left navigation rail: icon and label; the chosen one on the selected panel
    /// with a 3 px accent bar on its left and its icon and label in the accent.
    /// </summary>
    public sealed class KitNavItem : VisualElement
    {
        private readonly VisualElement _dot;

        public KitNavItem(string icon, string label, bool selected, Action onClick)
        {
            pickingMode = PickingMode.Position;
            AddToClassList("fc-nav-item");
            Add(Kit.Icon(icon));
            Add(Kit.Text(Kit.Caps(label), "fc-nav-item__label"));
            _dot = KitDot.Attach(this, false);
            Selected = selected;
            this.AddManipulator(new Tap(() =>
            {
                UiKit.RaiseClicked();
                onClick?.Invoke();
            }));
        }

        public bool Selected
        {
            get => ClassListContains("fc-nav-item--selected");
            set => EnableInClassList("fc-nav-item--selected", value);
        }

        /// <summary>The red dot: only for something the player can do now (see <see cref="KitDot"/>).</summary>
        public void ShowDot(bool show) => KitDot.Show(_dot, show);
    }

    /// <summary>The coin count with its plus (buy coins): the plus is a full touch target round a small face.</summary>
    public sealed class KitCurrency : VisualElement
    {
        private readonly Label _value;

        public KitCurrency(int coins, Action buy)
        {
            AddToClassList("fc-currency");
            Add(Kit.Icon("coin"));
            _value = Kit.Text("", "fc-currency__value");
            Add(_value);
            Add(new KitIconButton("plus", Strings.Get("kit.buyCoins"), buy, plain: true));
            Coins = coins;
        }

        public int Coins
        {
            set => _value.text = Kit.Count(value);
        }
    }
}
