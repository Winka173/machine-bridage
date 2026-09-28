using System;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>Small builders shared by every HUD and menu panel, so elements are made one way.</summary>
    internal static class UiKit
    {
        // The command-console palette (see Hud.uss).
        public static readonly Color Mint = new(0.561f, 0.839f, 0.580f);
        public static readonly Color Ink = new(0.929f, 0.937f, 0.941f);
        public static readonly Color Amber = new(0.949f, 0.639f, 0.227f);
        public static readonly Color Danger = new(0.898f, 0.325f, 0.235f);
        public static readonly Color Dim = new(0.663f, 0.706f, 0.729f);

        public static VisualElement Box(string classNames, PickingMode picking = PickingMode.Ignore)
        {
            var element = new VisualElement { pickingMode = picking };
            AddClasses(element, classNames);
            return element;
        }

        public static Label Text(string text, string classNames)
        {
            var label = new Label(text) { pickingMode = PickingMode.Ignore };
            AddClasses(label, classNames);
            return label;
        }

        /// <summary>AddToClassList takes one class; this accepts a space-separated list.</summary>
        public static void AddClasses(VisualElement element, string classNames)
        {
            if (string.IsNullOrEmpty(classNames)) return;
            foreach (var name in classNames.Split(' ', StringSplitOptions.RemoveEmptyEntries)) element.AddToClassList(name);
        }

        /// <summary>A vector icon. Ink (the default) lets the stylesheet colour it; any other tint is fixed.</summary>
        public static IconElement Icon(string name, Color tint, float stroke = 1.7f)
        {
            var icon = new IconElement(name, stroke);
            if (tint != Ink) icon.Tint = tint;
            return icon;
        }

        /// <summary>Anything tappable: a box with a tap handler (see <see cref="Tap"/>) that also plays the UI tick.</summary>
        public static VisualElement Button(string className, Action onClick)
        {
            var button = Box(className, PickingMode.Position);
            button.AddManipulator(new Tap(() =>
            {
                Clicked?.Invoke();
                onClick?.Invoke();
            }));
            return button;
        }

        public static VisualElement IconButton(string icon, Action onClick)
        {
            var button = Button("icon-button", onClick);
            button.Add(Icon(icon, Ink));
            return button;
        }

        /// <summary>A wide button with an icon, a title and an optional subtitle.</summary>
        public static VisualElement WideButton(string className, string icon, string title, string subtitle, Action onClick)
        {
            var button = Button("wide " + className, onClick);
            button.Add(Icon(icon, Ink, 1.8f));
            var text = Box("wide-text");
            text.Add(Text(title, "wide-title"));
            if (!string.IsNullOrEmpty(subtitle)) text.Add(Text(subtitle, "wide-sub"));
            button.Add(text);
            return button;
        }

        /// <summary>
        /// Labels drawn in uppercase condensed type (USS has no text-transform): buttons, tabs,
        /// section captions and card names. Their text is uppercased wherever it was set.
        /// </summary>
        private static readonly string[] CapsClasses =
        {
            "wide-title", "segment-label", "option-label", "rail-label", "gear-branch-name", "setup-mode-name", "nav-back-text",
            "nav-tab-label", "crate-button-text", "upgrade-big-text", "event-play-text", "menu-caps", "home-card-caps", "map-name",
            "unit-card-name", "shop-name", "tier-name", "deploy-text", "home-card-title", "mission-name", "detail-name",
            "event-card-title", "gear-info-title", "weapon-name", "detail-role", "crate-name", "loot-title",
            "base-tower-name", "base-head-name", "base-map-name", "base-branch-name", "base-front-text", "base-slot-caption",
            "base-hq-level", "base-branch-tag", "base-gear-name",
        };

        public static void Uppercase(VisualElement root)
        {
            root.Query<Label>().ForEach(label =>
            {
                if (string.IsNullOrEmpty(label.text)) return;
                foreach (var c in CapsClasses)
                {
                    if (!label.ClassListContains(c)) continue;
                    var upper = label.text.ToUpperInvariant();
                    if (upper != label.text) label.text = upper;
                    return;
                }
            });
        }

        /// <summary>Raised by every button built here, for the UI click sound.</summary>
        public static event Action Clicked;

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            Clicked = null;
        }

    }
}
