using System;
using UnityEngine;
using UnityEngine.UI;

namespace MachineBrigade.Game.Hud
{
    /// <summary>Builds uGUI elements from code so the HUD needs no prefabs or scene edits.</summary>
    internal static class UiFactory
    {
        private static Font _font;

        public static Font Font => _font != null ? _font : _font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");

        public static RectTransform Rect(Transform parent, string name, Vector2 anchor, Vector2 pivot, Vector2 position, Vector2 size)
        {
            var go = new GameObject(name, typeof(RectTransform));
            var rt = (RectTransform)go.transform;
            rt.SetParent(parent, false);
            rt.anchorMin = rt.anchorMax = anchor;
            rt.pivot = pivot;
            rt.anchoredPosition = position;
            rt.sizeDelta = size;
            return rt;
        }

        public static RectTransform Stretch(Transform parent, string name)
        {
            var go = new GameObject(name, typeof(RectTransform));
            var rt = (RectTransform)go.transform;
            rt.SetParent(parent, false);
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = rt.offsetMax = Vector2.zero;
            return rt;
        }

        public static Text Label(RectTransform rect, int fontSize, TextAnchor alignment)
        {
            var text = rect.gameObject.AddComponent<Text>();
            text.font = Font;
            text.fontSize = fontSize;
            text.alignment = alignment;
            text.color = Color.white;
            text.raycastTarget = false;
            var shadow = rect.gameObject.AddComponent<Shadow>();
            shadow.effectColor = new Color(0f, 0f, 0f, 0.8f);
            shadow.effectDistance = new Vector2(2f, -2f);
            return text;
        }

        public static Button Button(RectTransform rect, string label, Action onClick, out Text text, out Image background)
        {
            background = rect.gameObject.AddComponent<Image>();
            background.color = new Color(0.08f, 0.1f, 0.08f, 0.72f);
            var button = rect.gameObject.AddComponent<Button>();
            var colors = button.colors;
            colors.highlightedColor = new Color(1f, 1f, 1f, 1f);
            colors.pressedColor = new Color(0.7f, 0.9f, 0.7f, 1f);
            colors.disabledColor = new Color(0.6f, 0.6f, 0.6f, 0.5f);
            button.colors = colors;
            button.onClick.AddListener(() => onClick());

            var labelRect = Stretch(rect, "Label");
            text = Label(labelRect, 30, TextAnchor.MiddleCenter);
            text.text = label;
            return button;
        }
    }
}
