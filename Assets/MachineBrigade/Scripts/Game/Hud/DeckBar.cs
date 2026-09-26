using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>One card in the deck bar.</summary>
    public readonly struct CardInfo
    {
        public CardInfo(string id, bool support, int cost, string icon)
        {
            Id = id;
            Support = support;
            Cost = cost;
            Icon = icon;
        }

        public string Id { get; }
        public bool Support { get; }
        public int Cost { get; }
        public string Icon { get; }
    }

    /// <summary>What a card shows this frame.</summary>
    public readonly struct CardState
    {
        public CardState(bool affordable, bool locked, float cooldown, bool selected)
        {
            Affordable = affordable;
            Locked = locked;
            Cooldown = cooldown;
            Selected = selected;
        }

        public bool Affordable { get; }

        /// <summary>The army is at its unit cap, so vehicles cannot be bought.</summary>
        public bool Locked { get; }

        /// <summary>Remaining cooldown as a fraction (0 = ready).</summary>
        public float Cooldown { get; }

        /// <summary>A support card waiting for its target.</summary>
        public bool Selected { get; }
    }

    /// <summary>
    /// The deck: six vehicle cards and two support cards along the bottom, with the Command
    /// Point meter. Cards keep their size and place in every state (V2 R09); state is shown by
    /// colour, a cooldown sweep and the cost badge.
    /// </summary>
    internal sealed class DeckBar
    {
        private sealed class Card
        {
            public VisualElement Root, Cooldown;
            public Label Cost;
            public float ShownCooldown = -1f;
        }

        private readonly List<Card> _cards = new();
        private readonly Label _cp, _army;
        private readonly VisualElement _cpFill;
        private int _shownCp = -1, _shownArmy = -1, _shownCap = -1;
        private float _shownFill = -1f;

        public DeckBar(IReadOnlyList<CardInfo> cards)
        {
            Root = UiKit.Box("deck");

            // Solid, so a tap on the meter does not go through to the battlefield.
            var meter = UiKit.Box("cp-meter", PickingMode.Position);
            var top = UiKit.Box("cp-top");
            top.Add(UiKit.Icon("cp", UiKit.Amber, 1.9f));
            _cp = UiKit.Text("0", "cp-value");
            top.Add(_cp);
            meter.Add(top);
            var track = UiKit.Box("cp-track");
            _cpFill = UiKit.Box("cp-fill");
            track.Add(_cpFill);
            meter.Add(track);
            _army = UiKit.Text("", "cp-army");
            meter.Add(_army);
            Root.Add(meter);

            var row = UiKit.Box("cards");
            for (var i = 0; i < cards.Count; i++)
            {
                var index = i;
                var info = cards[i];
                var card = new Card { Root = UiKit.Button(info.Support ? "card support" : "card", () => CardPressed?.Invoke(index)) };
                card.Cooldown = UiKit.Box("card-cooldown");
                card.Root.Add(card.Cooldown);
                card.Root.Add(UiKit.Icon(info.Icon, UiKit.Ink, 1.6f));
                card.Root.Add(UiKit.Text(Strings.Card(info.Id), "card-name"));
                var cost = UiKit.Box("card-cost");
                card.Cost = UiKit.Text(info.Cost.ToString(), "card-cost-text");
                cost.Add(card.Cost);
                card.Root.Add(cost);
                if (i > 0 && info.Support && !cards[i - 1].Support) row.Add(UiKit.Box("card-gap"));
                row.Add(card.Root);
                _cards.Add(card);
            }
            Root.Add(row);
        }

        public VisualElement Root { get; }

        public event Action<int> CardPressed;

        public void Update(float cp, float bank, int armyCp, int armyCap, IReadOnlyList<CardState> states)
        {
            var whole = Mathf.FloorToInt(cp);
            if (whole != _shownCp)
            {
                _shownCp = whole;
                _cp.text = whole.ToString();
            }
            // Styles and text only change when the shown value does: each change costs a layout pass.
            var fill = Mathf.Round(Mathf.Clamp01(cp / Mathf.Max(1f, bank)) * 200f) / 2f;
            if (!Mathf.Approximately(fill, _shownFill)) _cpFill.style.width = Length.Percent(_shownFill = fill);
            if (armyCp != _shownArmy || armyCap != _shownCap)
            {
                _shownArmy = armyCp;
                _shownCap = armyCap;
                _army.text = Strings.Format("stat.army", armyCp, armyCap);
            }

            for (var i = 0; i < _cards.Count && i < states.Count; i++)
            {
                var card = _cards[i];
                var state = states[i];
                card.Root.EnableInClassList("unaffordable", !state.Affordable);
                card.Root.EnableInClassList("locked", state.Locked);
                card.Root.EnableInClassList("selected", state.Selected);
                card.Root.EnableInClassList("cooling", state.Cooldown > 0f);
                var cooldown = Mathf.Round(Mathf.Clamp01(state.Cooldown) * 100f);
                if (!Mathf.Approximately(cooldown, card.ShownCooldown)) card.Cooldown.style.height = Length.Percent(card.ShownCooldown = cooldown);
            }
        }
    }
}
