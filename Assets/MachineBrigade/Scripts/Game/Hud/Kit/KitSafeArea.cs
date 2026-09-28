using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Keeps a kit screen's content inside the safe area in landscape (notch, punch-hole camera,
    /// the system navigation bar): the element (class fc-safe, absolutely placed over the screen)
    /// is inset by the parts of the screen outside <see cref="Screen.safeArea"/>, converted to
    /// panel pixels. The left rail and the right-edge buttons live inside it.
    /// </summary>
    public static class KitSafeArea
    {
        /// <summary>Insets (left, top, right, bottom) in panel pixels for a safe area given in screen pixels (origin bottom-left).</summary>
        public static Vector4 Insets(Rect safeArea, Vector2 screenSize, Vector2 panelSize)
        {
            if (screenSize.x <= 0f || screenSize.y <= 0f) return Vector4.zero;
            var sx = panelSize.x / screenSize.x;
            var sy = panelSize.y / screenSize.y;
            return new Vector4(
                Mathf.Max(0f, safeArea.xMin) * sx,
                Mathf.Max(0f, screenSize.y - safeArea.yMax) * sy,
                Mathf.Max(0f, screenSize.x - safeArea.xMax) * sx,
                Mathf.Max(0f, safeArea.yMin) * sy);
        }

        /// <summary>Places a full-screen element inside the given insets (panel pixels).</summary>
        public static void Apply(VisualElement element, Vector4 insets)
        {
            element.style.position = Position.Absolute;
            element.style.left = insets.x;
            element.style.top = insets.y;
            element.style.right = insets.z;
            element.style.bottom = insets.w;
        }

        /// <summary>Follows the device's safe area (a rotation, another screen) while the element is on a panel.</summary>
        public static IVisualElementScheduledItem Track(VisualElement element)
        {
            Rect applied = default;
            var size = Vector2.zero;
            return element.schedule.Execute(() =>
            {
                var root = element.panel?.visualTree;
                if (root == null) return;
                var panelSize = root.layout.size;
                if (Screen.safeArea == applied && panelSize == size) return;
                applied = Screen.safeArea;
                size = panelSize;
                Apply(element, Insets(applied, new Vector2(Screen.width, Screen.height), panelSize));
            }).Every(250);
        }
    }
}
