using System;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>A 4 px progress bar: a border-coloured track, a text-2 fill; the fill turns accent once it is enough to act on.</summary>
    public sealed class KitProgress : VisualElement
    {
        private readonly VisualElement _fill;

        public KitProgress(float value = 0f, bool ready = false)
        {
            AddToClassList("fc-progress");
            _fill = Kit.Box("fc-progress__fill");
            Add(_fill);
            Value = value;
            Ready = ready;
        }

        public float Value
        {
            set => _fill.style.width = Length.Percent(100f * Mathf.Clamp01(value));
        }

        /// <summary>Enough to do something with (an upgrade's blueprints): the accent fill.</summary>
        public bool Ready
        {
            set => EnableInClassList("fc-progress--ready", value);
        }
    }

    /// <summary>
    /// The notification dot: a red 8 px square in the corner, only while the player has something
    /// to do now (a reward to claim, an affordable upgrade, a free gift), never just for new content.
    /// </summary>
    public static class KitDot
    {
        public const string DotClass = "fc-dot";

        public static VisualElement Attach(VisualElement host, bool show)
        {
            var dot = Kit.Box(DotClass);
            host.Add(dot);
            Show(dot, show);
            return dot;
        }

        public static void Show(VisualElement dot, bool show) => dot.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
    }

    /// <summary>Panels, dialogs, toasts and tooltips: one surface (panel-raised background, 1 px strong border).</summary>
    public static class KitPanel
    {
        public const string SurfaceClass = "fc-surface";

        /// <summary>A panel with an optional title; add content to the returned body.</summary>
        public static VisualElement Create(string title, out VisualElement body, bool onBattlefield = false)
        {
            var panel = Kit.Box(SurfaceClass + " fc-panel" + (onBattlefield ? " fc-surface--field" : ""), PickingMode.Position);
            if (!string.IsNullOrEmpty(title)) panel.Add(Kit.Text(Kit.Caps(title), "fc-panel-title fc-panel__title"));
            body = Kit.Box("fc-panel__body");
            panel.Add(body);
            return panel;
        }
    }

    /// <summary>Modal dialogs over a dimmed screen: a title, a text and a row of buttons (secondary first, then the action).</summary>
    public static class KitDialog
    {
        public const string ScrimClass = "fc-scrim";

        /// <summary>Puts <paramref name="content"/> in the middle of the kit root <paramref name="anchor"/> belongs to, over a scrim; a tap on the scrim closes it.</summary>
        public static VisualElement Present(VisualElement anchor, VisualElement content, bool closeOnScrim = true)
        {
            var host = Kit.HostOf(anchor) ?? anchor;
            var scrim = Kit.Box(ScrimClass, PickingMode.Position);
            if (closeOnScrim)
                scrim.RegisterCallback<PointerDownEvent>(e =>
                {
                    if (e.target == scrim) scrim.RemoveFromHierarchy();
                });
            scrim.Add(content);
            host.Add(scrim);
            return scrim;
        }

        /// <summary>A dialog element (not shown): for <see cref="Present"/> and for the kit preview.</summary>
        public static VisualElement Build(string title, string body, params VisualElement[] buttons)
        {
            var dialog = Kit.Box(KitPanel.SurfaceClass + " fc-dialog", PickingMode.Position);
            dialog.Add(Kit.Text(Kit.Caps(title), "fc-panel-title fc-dialog__title"));
            dialog.Add(Kit.Text(body, "fc-body-2 fc-dialog__body"));
            var row = Kit.Box("fc-dialog__buttons");
            foreach (var b in buttons) row.Add(b);
            dialog.Add(row);
            return dialog;
        }

        /// <summary>A danger action's question: Cancel, and the red confirm button that runs <paramref name="onConfirm"/>.</summary>
        public static VisualElement Confirm(VisualElement anchor, string title, string body, string confirmLabel, Action onConfirm)
        {
            VisualElement scrim = null;
            var cancel = new KitButton(ButtonTier.Secondary, Strings.Get("kit.cancel"), () => scrim?.RemoveFromHierarchy());
            var confirm = KitButton.DangerConfirm(confirmLabel, () =>
            {
                scrim?.RemoveFromHierarchy();
                onConfirm?.Invoke();
            });
            scrim = Present(anchor, Build(title, body, cancel, confirm));
            return scrim;
        }
    }

    public enum ToastKind
    {
        Info,
        Reward,
        Alert,
    }

    /// <summary>
    /// A short message along the bottom (and, in battle, radio chatter, air-raid warnings and elite
    /// notices): the shared surface with an icon; the icon's colour tells the kind.
    /// </summary>
    public static class KitToast
    {
        public static VisualElement Build(string text, ToastKind kind = ToastKind.Info)
        {
            var toast = Kit.Box(KitPanel.SurfaceClass + " fc-toast fc-toast--" + kind.ToString().ToLowerInvariant());
            toast.Add(Kit.Icon(kind switch { ToastKind.Reward => "coin", ToastKind.Alert => "info", _ => "check" }));
            toast.Add(Kit.Body(text));
            return toast;
        }

        /// <summary>Shows a toast at the bottom of the kit root <paramref name="anchor"/> belongs to for <paramref name="seconds"/>.</summary>
        public static VisualElement Show(VisualElement anchor, string text, ToastKind kind = ToastKind.Info, float seconds = 3f)
        {
            var host = Kit.HostOf(anchor) ?? anchor;
            var holder = host.Q(className: "fc-toast-host");
            if (holder == null)
            {
                holder = Kit.Box("fc-toast-host");
                host.Add(holder);
            }
            holder.Clear();
            var toast = Build(text, kind);
            holder.Add(toast);
            holder.BringToFront();
            toast.schedule.Execute(() => toast.RemoveFromHierarchy()).StartingIn((long)(seconds * 1000f));
            return toast;
        }
    }

    /// <summary>A tooltip: the shared surface with an optional title and a short explanation (a long press shows it).</summary>
    public static class KitTooltip
    {
        public static VisualElement Build(string title, string text)
        {
            var tip = Kit.Box(KitPanel.SurfaceClass + " fc-tooltip");
            if (!string.IsNullOrEmpty(title)) tip.Add(Kit.Text(Kit.Caps(title), "fc-caption fc-tooltip__title"));
            tip.Add(Kit.Text(text, "fc-body"));
            return tip;
        }

        /// <summary>A long press (half a second) on <paramref name="target"/> shows the tooltip over the screen until the next tap.</summary>
        public static void Attach(VisualElement target, string title, string text)
        {
            IVisualElementScheduledItem pending = null;
            target.RegisterCallback<PointerDownEvent>(_ =>
            {
                pending?.Pause();
                pending = target.schedule.Execute(() => KitDialog.Present(target, Build(title, text))).StartingIn(500);
            });
            target.RegisterCallback<PointerUpEvent>(_ => pending?.Pause());
            target.RegisterCallback<PointerLeaveEvent>(_ => pending?.Pause());
        }
    }
}
