using System;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>Small builders shared by every HUD and menu panel, so elements are made one way.</summary>
    internal static class UiKit
    {
        public static readonly Color Mint = new(0.647f, 0.89f, 0.749f);
        public static readonly Color Ink = new(0.89f, 0.925f, 0.9f);
        public static readonly Color Amber = new(0.875f, 0.718f, 0.463f);
        public static readonly Color Danger = new(0.94f, 0.54f, 0.45f);
        public static readonly Color Dim = new(0.545f, 0.604f, 0.569f);

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

        public static IconElement Icon(string name, Color tint, float stroke = 1.7f) => new(name, stroke) { Tint = tint };

        /// <summary>Anything tappable: a box with a click handler that also plays the UI tick.</summary>
        public static VisualElement Button(string className, Action onClick)
        {
            var button = Box(className, PickingMode.Position);
            button.AddManipulator(new Clickable(() =>
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

        /// <summary>Raised by every button built here, for the UI click sound.</summary>
        public static event Action Clicked;
    }
}
