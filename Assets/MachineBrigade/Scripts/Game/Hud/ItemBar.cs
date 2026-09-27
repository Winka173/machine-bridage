using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>What an item button shows this frame.</summary>
    public readonly struct ItemState
    {
        public ItemState(int count, float cooldown, bool selected)
        {
            Count = count;
            Cooldown = cooldown;
            Selected = selected;
        }

        public int Count { get; }

        /// <summary>Remaining cooldown as a fraction (0 = ready).</summary>
        public float Cooldown { get; }

        public bool Selected { get; }
    }

    /// <summary>
    /// Items bought with coins (MOAB, EMP, reinforcements...): a column of square buttons under
    /// the minimap tools, each with how many are left. Tapping one aims it like a support card.
    /// </summary>
    internal sealed class ItemBar
    {
        private sealed class Button
        {
            public VisualElement Root, Cooldown;
            public Label Count;
            public int ShownCount = -1;
            public float ShownCooldown = -1f;
        }

        private readonly List<Button> _buttons = new();

        public ItemBar(IReadOnlyList<string> items)
        {
            Root = UiKit.Box("item-strip", PickingMode.Ignore);
            for (var i = 0; i < items.Count; i++)
            {
                var index = i;
                var button = new Button { Root = UiKit.Button("item", () => Pressed?.Invoke(index)) };
                button.Cooldown = UiKit.Box("item-cooldown");
                button.Root.Add(button.Cooldown);
                button.Root.Add(UiKit.Icon(CardIcons.For(items[i]), UiKit.Ink, 1.5f));
                var badge = UiKit.Box("item-count");
                button.Count = UiKit.Text("", "item-count-text");
                badge.Add(button.Count);
                button.Root.Add(badge);
                Root.Add(button.Root);
                _buttons.Add(button);
            }
        }

        public VisualElement Root { get; }

        public event Action<int> Pressed;

        public void Update(IReadOnlyList<ItemState> states)
        {
            for (var i = 0; i < _buttons.Count && i < states.Count; i++)
            {
                var button = _buttons[i];
                var state = states[i];
                if (state.Count != button.ShownCount)
                {
                    button.ShownCount = state.Count;
                    button.Count.text = "x" + state.Count;
                    button.Root.EnableInClassList("empty", state.Count <= 0);
                }
                button.Root.EnableInClassList("selected", state.Selected);
                var cooldown = Mathf.Round(Mathf.Clamp01(state.Cooldown) * 100f);
                if (!Mathf.Approximately(cooldown, button.ShownCooldown)) button.Cooldown.style.height = Length.Percent(button.ShownCooldown = cooldown);
            }
        }
    }
}
