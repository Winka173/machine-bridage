using System;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>The five button tiers of Field Command 2.0.</summary>
    public enum ButtonTier
    {
        /// <summary>The accent face with two cut corners: the one main action of a screen (at most one).</summary>
        Primary,

        /// <summary>An outline in the text colour, no fill.</summary>
        Secondary,

        /// <summary>The coin face with a coin icon and a slow pulse: only while there is a reward to take.</summary>
        Claim,

        /// <summary>Accent text, no face; still a full touch target.</summary>
        Text,

        /// <summary>A red outline; it always opens a confirmation first.</summary>
        Danger,
    }

    /// <summary>What a danger button asks before it acts.</summary>
    public readonly struct KitConfirm
    {
        public KitConfirm(string title, string body, string confirmLabel)
        {
            Title = title;
            Body = body;
            ConfirmLabel = confirmLabel;
        }

        public string Title { get; }
        public string Body { get; }
        public string ConfirmLabel { get; }
    }

    /// <summary>
    /// A button of one of the five tiers, in one of its states: normal, pressed (darker and 2 px
    /// down while the finger is on it; phones have no hover), disabled with a short reason under
    /// the label ("320 coins short", "Needs HQ level 3"), or loading (a turning arc, taps ignored).
    /// </summary>
    public sealed class KitButton : VisualElement
    {
        public const string BaseClass = "fc-btn";
        public const string PrimaryClass = "fc-btn--primary";
        public const string DisabledClass = "fc-btn--disabled";
        public const string LoadingClass = "fc-btn--loading";
        public const string PressedClass = "fc-btn--pressed";

        private readonly Label _label, _reason;
        private readonly IconElement _spinner;
        private readonly Action _onClick;
        private readonly KitConfirm? _confirm;
        private IVisualElementScheduledItem _spin, _pulse;
        private float _angle;

        public KitButton(ButtonTier tier, string label, Action onClick, string icon = null)
            : this(tier, label, onClick, icon, null)
        {
            if (tier == ButtonTier.Danger)
                throw new ArgumentException("A danger button asks first: build it with KitButton.Danger.");
        }

        private KitButton(ButtonTier tier, string label, Action onClick, string icon, KitConfirm? confirm)
        {
            Tier = tier;
            _onClick = onClick;
            _confirm = confirm;
            pickingMode = PickingMode.Position;
            AddToClassList(BaseClass);
            AddToClassList("fc-btn--" + TierName(tier));
            if (tier == ButtonTier.Claim && icon == null) icon = "coin";
            var row = Kit.Box("fc-btn__row");
            _spinner = Kit.Icon("spinner", "fc-btn__spinner", 2.2f);
            row.Add(_spinner);
            if (icon != null) row.Add(Kit.Icon(icon, "fc-btn__icon"));
            _label = Kit.Text("", "fc-btn__label");
            row.Add(_label);
            Add(row);
            _reason = Kit.Text("", "fc-btn__reason");
            Add(_reason);
            Label = label;
            this.AddManipulator(new Tap(OnTap));
            RegisterCallback<AttachToPanelEvent>(_ => Animate());
            RegisterCallback<DetachFromPanelEvent>(_ => StopAnimations());
        }

        /// <summary>A danger button: a tap opens <paramref name="confirm"/>; only its confirm button runs <paramref name="onConfirmed"/>.</summary>
        public static KitButton Danger(string label, KitConfirm confirm, Action onConfirmed, string icon = null) =>
            new(ButtonTier.Danger, label, onConfirmed, icon, confirm);

        /// <summary>The confirm button inside a danger dialog: danger-styled, acts at once.</summary>
        internal static KitButton DangerConfirm(string label, Action onConfirmed) =>
            new(ButtonTier.Danger, label, onConfirmed, null, null);

        public ButtonTier Tier { get; }

        public bool Disabled { get; private set; }
        public string Reason => Disabled ? _reason.text : null;
        public bool Loading { get; private set; }

        /// <summary>A danger button's question, or null.</summary>
        public KitConfirm? Confirm => _confirm;

        public string Label
        {
            get => _label.text;
            set => _label.text = Kit.Caps(value);
        }

        /// <summary>Greys the button out with the reason it cannot be used (required: a disabled button always says why).</summary>
        public KitButton Disable(string reason)
        {
            if (string.IsNullOrWhiteSpace(reason)) throw new ArgumentException("A disabled button says why.", nameof(reason));
            Disabled = true;
            _reason.text = reason;
            AddToClassList(DisabledClass);
            Animate();
            return this;
        }

        public KitButton Enable()
        {
            Disabled = false;
            _reason.text = "";
            RemoveFromClassList(DisabledClass);
            Animate();
            return this;
        }

        /// <summary>Shows the turning arc and ignores taps until it is switched off.</summary>
        public KitButton SetLoading(bool loading)
        {
            Loading = loading;
            EnableInClassList(LoadingClass, loading);
            Animate();
            return this;
        }

        /// <summary>Holds the pressed look (the kit preview's specimens).</summary>
        public KitButton ShowPressed(bool pressed = true)
        {
            EnableInClassList(PressedClass, pressed);
            return this;
        }

        private void OnTap()
        {
            if (Disabled || Loading) return;
            UiKit.RaiseClicked();
            if (_confirm is { } question)
                KitDialog.Confirm(this, question.Title, question.Body, question.ConfirmLabel, _onClick);
            else
                _onClick?.Invoke();
        }

        /// <summary>Starts or stops the loading arc and the claim pulse to match the state.</summary>
        private void Animate()
        {
            if (panel == null) return;
            if (Loading && _spin == null)
                _spin = schedule.Execute(() =>
                {
                    _angle = (_angle + 12f) % 360f;
                    _spinner.style.rotate = new Rotate(new Angle(_angle, AngleUnit.Degree));
                }).Every(33);
            else if (!Loading && _spin != null)
            {
                _spin.Pause();
                _spin = null;
            }
            var pulse = Tier == ButtonTier.Claim && !Disabled && !Loading;
            if (pulse && _pulse == null) _pulse = schedule.Execute(() => ToggleInClassList("fc-btn--glow")).Every(900);
            else if (!pulse && _pulse != null)
            {
                _pulse.Pause();
                _pulse = null;
                RemoveFromClassList("fc-btn--glow");
            }
        }

        private void StopAnimations()
        {
            _spin?.Pause();
            _pulse?.Pause();
            _spin = _pulse = null;
        }

        internal static string TierName(ButtonTier tier) => tier switch
        {
            ButtonTier.Primary => "primary",
            ButtonTier.Secondary => "secondary",
            ButtonTier.Claim => "claim",
            ButtonTier.Text => "text",
            _ => "danger",
        };
    }

    /// <summary>
    /// A square icon button of fixed size with its accessibility label (read out by screen readers,
    /// shown as the tooltip). The plain variant is a small face inside a full-size transparent
    /// target, for the plus beside a number.
    /// </summary>
    public sealed class KitIconButton : VisualElement
    {
        public const string BaseClass = "fc-icon-btn";

        private readonly Action _onClick;

        public KitIconButton(string icon, string accessibilityLabel, Action onClick, bool plain = false)
        {
            if (string.IsNullOrWhiteSpace(accessibilityLabel))
                throw new ArgumentException("An icon button needs an accessibility label.", nameof(accessibilityLabel));
            AccessibilityLabel = accessibilityLabel;
            tooltip = accessibilityLabel;
            _onClick = onClick;
            pickingMode = PickingMode.Position;
            AddToClassList(BaseClass);
            if (plain)
            {
                AddToClassList("fc-icon-btn--plain");
                var face = Kit.Box("fc-icon-btn__face");
                face.Add(Kit.Icon(icon, null, 2.2f));
                Add(face);
            }
            else Add(Kit.Icon(icon));
            this.AddManipulator(new Tap(OnTap));
        }

        /// <summary>What the button does, in words: the tooltip and the screen reader's label.</summary>
        public string AccessibilityLabel { get; }

        public bool Disabled { get; private set; }

        public KitIconButton SetDisabled(bool disabled)
        {
            Disabled = disabled;
            EnableInClassList(KitButton.DisabledClass, disabled);
            return this;
        }

        public KitIconButton ShowPressed(bool pressed = true)
        {
            EnableInClassList(KitButton.PressedClass, pressed);
            return this;
        }

        private void OnTap()
        {
            if (Disabled) return;
            UiKit.RaiseClicked();
            _onClick?.Invoke();
        }
    }
}
