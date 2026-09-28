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
        public CardState(bool affordable, bool locked, float cooldown, bool selected, float cooldownSeconds = 0f)
        {
            Affordable = affordable;
            Locked = locked;
            Cooldown = cooldown;
            Selected = selected;
            CooldownSeconds = cooldownSeconds;
        }

        public bool Affordable { get; }

        /// <summary>The army is at the safety limit of vehicles, so no more can be bought.</summary>
        public bool Locked { get; }

        /// <summary>Remaining cooldown as a fraction (0 = ready).</summary>
        public float Cooldown { get; }

        /// <summary>Remaining cooldown in seconds (shown in the middle of the sweep).</summary>
        public float CooldownSeconds { get; }

        /// <summary>A support card waiting for its target.</summary>
        public bool Selected { get; }
    }

    /// <summary>
    /// The deck along the bottom on the kit (Field Command 2.0, G): the CP box (the points in big
    /// figures, the income a second, and the supply penalty or the underdog's boost in words; a tap
    /// explains it), then the vehicle cards and the support cards, each with its 3D render, its full
    /// name and its CP. A card the points pay for is bright; one they do not is dimmed and says how
    /// many are missing; a support card on cooldown is swept round like a clock with the seconds in
    /// the middle. Cards keep their size and place in every state.
    /// </summary>
    internal sealed class DeckBar
    {
        private sealed class Card
        {
            public CardInfo Info;
            public VisualElement Root;
            public CooldownSweep Sweep;
            public Label Short, Seconds;
            public int ShownShort = -1, ShownSeconds = -1;
            public float ShownCooldown = -1f;
        }

        private readonly List<Card> _cards = new();
        private readonly Label _cp, _income, _supply;
        private readonly KitProgress _bank;
        private int _shownCp = -1, _shownEarning = -1, _shownUpkeep = -1;
        private float _shownFill = -1f;

        public DeckBar(IReadOnlyList<CardInfo> cards)
        {
            Root = Kit.Box("fc-deck");

            // Solid, so a tap on the box does not go through to the battlefield; a tap explains the numbers.
            var box = Kit.Tappable(KitPanel.SurfaceClass + " fc-surface--field fc-cpbox", () => CpTapped?.Invoke());
            var head = Kit.Box("fc-cpbox__head");
            head.Add(Kit.Caption(Strings.Get("stat.cp")));
            _cp = Kit.Text("0", "fc-number fc-cpbox__value");
            head.Add(_cp);
            box.Add(head);
            _bank = new KitProgress();
            _bank.AddToClassList("fc-cpbox__bank");
            box.Add(_bank);
            _income = Kit.Text("", "fc-number-small fc-cpbox__income");
            box.Add(_income);
            _supply = Kit.Text("", "fc-small fc-cpbox__supply");
            box.Add(_supply);
            Root.Add(box);

            var row = Kit.Box("fc-deck__cards");
            for (var i = 0; i < cards.Count; i++)
            {
                var index = i;
                var info = cards[i];
                var card = new Card { Info = info };
                card.Root = Kit.Tappable("fc-hcard" + (info.Support ? " fc-hcard--support" : ""), () => CardPressed?.Invoke(index));
                var art = Kit.Box("fc-hcard__art");
                if (CardArt.For(info.Id) is { } render) art.style.backgroundImage = Background.FromTexture2D(render);
                else art.Add(Kit.Icon(info.Icon, "fc-hcard__icon"));
                card.Sweep = new CooldownSweep();
                art.Add(card.Sweep);
                card.Seconds = Kit.Text("", "fc-number-small fc-hcard__seconds");
                art.Add(card.Seconds);
                art.Add(Kit.Icon("lock", "fc-hcard__lock"));
                card.Short = Kit.Text("", "fc-caption fc-hcard__short");
                art.Add(card.Short);
                card.Root.Add(art);
                var cost = Kit.Box("fc-hcard__cost");
                cost.Add(Kit.Text(info.Cost.ToString(), "fc-number-small"));
                card.Root.Add(cost);
                card.Root.Add(Kit.Text(Kit.Caps(Strings.Card(info.Id)), "fc-caption fc-hcard__name"));
                if (i > 0 && info.Support && !cards[i - 1].Support) row.Add(Kit.Box("fc-deck__gap"));
                row.Add(card.Root);
                _cards.Add(card);
            }
            Root.Add(row);
        }

        public VisualElement Root { get; }

        public event Action<int> CardPressed;

        /// <summary>The CP box was tapped: what the numbers mean.</summary>
        public event Action CpTapped;

        public void Update(float cp, float bank, float earning, float upkeep, IReadOnlyList<CardState> states)
        {
            var whole = Mathf.FloorToInt(cp);
            if (whole != _shownCp)
            {
                _shownCp = whole;
                _cp.text = whole.ToString();
            }
            // Styles and text only change when the shown value does: each change costs a layout pass.
            var fill = Mathf.Round(Mathf.Clamp01(cp / Mathf.Max(1f, bank)) * 100f) / 100f;
            if (!Mathf.Approximately(fill, _shownFill)) _bank.Value = _shownFill = fill;
            // Income a second; the supply penalty (the army is bigger than its supply) or the underdog's
            // boost in words (upkeep here is the net modifier).
            var tenths = Mathf.RoundToInt(earning * 10f);
            var upkeepStep = Mathf.RoundToInt((1f - upkeep) * 20f);
            if (tenths != _shownEarning || upkeepStep != _shownUpkeep)
            {
                _shownEarning = tenths;
                _shownUpkeep = upkeepStep;
                _income.text = Strings.Format("hud.income", (tenths / 10f).ToString("0.0"));
                var percent = Mathf.RoundToInt(Mathf.Abs(1f - upkeep) * 100f);
                _supply.text = upkeepStep > 0 ? Strings.Format("hud.upkeep", percent) : upkeepStep < 0 ? Strings.Format("hud.boost", percent) : "";
                _supply.style.display = upkeepStep != 0 ? DisplayStyle.Flex : DisplayStyle.None;
                _supply.EnableInClassList("fc-danger-text", upkeepStep > 0);
                _supply.EnableInClassList("fc-positive-text", upkeepStep < 0);
            }

            for (var i = 0; i < _cards.Count && i < states.Count; i++)
            {
                var card = _cards[i];
                var state = states[i];
                var cooling = state.Cooldown > 0f;
                card.Root.EnableInClassList("fc-hcard--short", !state.Affordable && !state.Locked);
                card.Root.EnableInClassList("fc-hcard--locked", state.Locked);
                card.Root.EnableInClassList("fc-hcard--armed", state.Selected);
                card.Root.EnableInClassList("fc-hcard--cooling", cooling);
                var missing = state.Affordable || state.Locked || cooling ? 0 : Mathf.Max(1, Mathf.CeilToInt(card.Info.Cost - cp));
                if (missing != card.ShownShort)
                {
                    card.ShownShort = missing;
                    card.Short.text = missing > 0 ? Strings.Format("hud.cpShort", missing) : "";
                }
                var cooldown = Mathf.Round(Mathf.Clamp01(state.Cooldown) * 100f) / 100f;
                if (!Mathf.Approximately(cooldown, card.ShownCooldown)) card.Sweep.Share = card.ShownCooldown = cooldown;
                var seconds = cooling ? Mathf.CeilToInt(state.CooldownSeconds) : 0;
                if (seconds != card.ShownSeconds)
                {
                    card.ShownSeconds = seconds;
                    card.Seconds.text = seconds > 0 ? seconds.ToString() : "";
                }
            }
        }
    }

    /// <summary>
    /// A cooldown drawn as a clock sweep over a card's picture: the share still to wait, from twelve
    /// o'clock round. Its colour is the element's own text colour (the theme sets it).
    /// </summary>
    internal sealed class CooldownSweep : VisualElement
    {
        private float _share;

        public CooldownSweep()
        {
            AddToClassList("fc-hcard__sweep");
            pickingMode = PickingMode.Ignore;
            generateVisualContent += Draw;
        }

        /// <summary>0 ready .. 1 just used.</summary>
        public float Share
        {
            get => _share;
            set
            {
                _share = Mathf.Clamp01(value);
                MarkDirtyRepaint();
            }
        }

        private void Draw(MeshGenerationContext context)
        {
            if (_share <= 0.001f) return;
            var rect = contentRect;
            var centre = rect.center;
            // Big enough to cover the corners: the sweep is cut to the picture by overflow.
            var radius = Mathf.Sqrt(rect.width * rect.width + rect.height * rect.height) * 0.5f;
            var p = context.painter2D;
            p.fillColor = resolvedStyle.color;
            p.BeginPath();
            p.MoveTo(centre);
            p.Arc(centre, radius, -90f, -90f + 360f * _share);
            p.ClosePath();
            p.Fill();
        }
    }
}
