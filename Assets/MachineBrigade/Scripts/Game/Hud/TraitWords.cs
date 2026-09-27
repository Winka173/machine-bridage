using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The short words equipment shows over a vehicle when it goes off in battle ("RICOCHET",
    /// "BLOCKED", "EXECUTE"), after Archero's and Brawl Stars' proc pop-ups: a small pool of
    /// labels under the HUD controls, each rising and fading over a second and a bit, following
    /// the spot it was shown at as the camera moves. The simulation already sends at most one word
    /// per vehicle every two seconds, so the pool stays small.
    /// </summary>
    internal sealed class TraitWords
    {
        private const int Pool = 10;
        private const float Life = 1.3f;

        private readonly VisualElement _layer;
        private readonly Label[] _labels = new Label[Pool];
        private readonly Vector3[] _at = new Vector3[Pool];
        private readonly float[] _born = new float[Pool];
        private readonly bool[] _live = new bool[Pool];
        private Camera _camera;
        private int _next;

        public TraitWords(VisualElement parent)
        {
            _layer = UiKit.Box("trait-pop-layer");
            for (var i = 0; i < Pool; i++)
            {
                var label = UiKit.Text("", "trait-pop");
                label.style.display = DisplayStyle.None;
                _labels[i] = label;
                _layer.Add(label);
            }
            parent.Add(_layer);
        }

        /// <summary>Shows <paramref name="word"/> at a world point (above a vehicle); the enemy's in a warmer colour.</summary>
        public void Show(Vector3 world, string word, bool ours, Camera camera)
        {
            if (string.IsNullOrEmpty(word) || camera == null) return;
            _camera = camera;
            var i = _next++ % Pool;
            var label = _labels[i];
            label.text = word;
            label.EnableInClassList("theirs", !ours);
            _at[i] = world;
            _born[i] = Time.unscaledTime;
            _live[i] = true;
            Place(i);
        }

        public void Tick()
        {
            for (var i = 0; i < Pool; i++)
                if (_live[i])
                    Place(i);
        }

        private void Place(int i)
        {
            var label = _labels[i];
            var age = Time.unscaledTime - _born[i];
            var panel = _layer.panel;
            if (age > Life || _camera == null || panel == null)
            {
                _live[i] = false;
                label.style.display = DisplayStyle.None;
                return;
            }
            var screen = _camera.WorldToScreenPoint(_at[i] + Vector3.up * (age * 1.6f));
            if (screen.z <= 0f)
            {
                label.style.display = DisplayStyle.None;
                return;
            }
            var p = RuntimePanelUtils.ScreenToPanel(panel, new Vector2(screen.x, Screen.height - screen.y));
            label.style.display = DisplayStyle.Flex;
            label.style.left = p.x;
            label.style.top = p.y;
            // A quick pop in, then a fade over the last half.
            var grow = Mathf.Clamp01(age / 0.12f);
            label.style.scale = new Scale(Vector3.one * Mathf.Lerp(1.35f, 1f, grow));
            label.style.opacity = Mathf.Clamp01((Life - age) / (Life * 0.5f));
        }
    }
}
