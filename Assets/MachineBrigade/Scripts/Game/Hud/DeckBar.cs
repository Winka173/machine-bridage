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
    /// <para>
    /// Compact (prompt 11 A3): about a third lower. A card is its render, its CP and its short name on
    /// one line; holding a card shows its full name over it (a held card is not played). The CP box is
    /// the points, the bar and the income; the supply penalty (or the underdog's boost) is a small chip
    /// over the box, shown only while it applies. Every card has a <c>fc-hcard__badges</c> row in the
    /// picture's top-left corner, empty for now, for later marks (prompt 13's ammo).
    /// </para>
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
        private readonly VisualElement _tip;
        private readonly Label _tipName;
        private int _shownCp = -1, _shownEarning = -1, _shownUpkeep = -1;
        private float _shownFill = -1f;

        public DeckBar(IReadOnlyList<CardInfo> cards, bool compact = false)
        {
            Root = Kit.Box("fc-deck" + (compact ? " fc-deck--compact" : ""));

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
            _income = Kit.Text("", (compact ? "fc-small" : "fc-number-small") + " fc-cpbox__income");
            box.Add(_income);
            // Compact: the penalty is a chip over the box, only while it applies (the box keeps its height).
            _supply = Kit.Text("", compact ? "fc-small fc-deck__chip" : "fc-small fc-cpbox__supply");
            _supply.style.display = DisplayStyle.None;
            box.Add(_supply);
            Root.Add(box);

            var row = Kit.Box("fc-deck__cards");
            for (var i = 0; i < cards.Count; i++)
            {
                var index = i;
                var info = cards[i];
                var card = new Card { Info = info };
                card.Root = Kit.Box("fc-hcard" + (info.Support ? " fc-hcard--support" : ""), PickingMode.Position);
                var root = card.Root;
                // A tap plays the card; a hold shows its full name over it (compact: the card shows its short name).
                card.Root.AddManipulator(new Tap(() =>
                {
                    UiKit.RaiseClicked();
                    CardPressed?.Invoke(index);
                }, held => ShowTip(root, held ? Strings.Card(info.Id) : null)));
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
                art.Add(Kit.Box("fc-hcard__badges"));
                card.Root.Add(art);
                var cost = Kit.Box("fc-hcard__cost");
                cost.Add(Kit.Text(info.Cost.ToString(), "fc-number-small"));
                card.Root.Add(cost);
                // Compact: the short name on one line (two in Large text, where no width fits every name on one
                // line across the tray); full: the name in capitals, two lines, the short name if it needs more.
                // Either way the name area is one height on every card, so the cards line up (prompt 11 B2).
                Label name;
                if (compact)
                {
                    name = Kit.Text(Strings.Short(info.Id), "fc-hcard__name fc-hcard__name--short");
                    Kit.FixedLines(name, Match.MatchSettings.LargeText ? 2 : 1);
                }
                else
                {
                    name = Kit.Text(Kit.Caps(Strings.Card(info.Id)), "fc-caption fc-hcard__name");
                    Kit.FixedLines(name, 2, Kit.Caps(Strings.Short(info.Id)));
                }
                card.Root.Add(name);
                if (i > 0 && info.Support && !cards[i - 1].Support) row.Add(Kit.Box("fc-deck__gap"));
                row.Add(card.Root);
                _cards.Add(card);
            }
            Root.Add(row);
            // The full name of a held card, over the tray.
            _tip = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-deck__tip");
            _tipName = Kit.Text("", "fc-body fc-row-text");
            _tip.Add(_tipName);
            _tip.style.display = DisplayStyle.None;
            Root.Add(_tip);
        }

        /// <summary>Shows a held card's full name over it (null hides it).</summary>
        private void ShowTip(VisualElement card, string name)
        {
            if (name == null)
            {
                _tip.style.display = DisplayStyle.None;
                return;
            }
            _tipName.text = name;
            _tip.style.display = DisplayStyle.Flex;
            // Centred over the card, kept inside the tray.
            var x = card.worldBound.center.x - Root.worldBound.xMin;
            _tip.style.left = Mathf.Max(0f, x - 120f);
        }

        /// <summary>A card's full name shown as when held (the screenshot tool); -1 hides it.</summary>
        internal void PreviewHeld(int index)
        {
            if (index < 0 || index >= _cards.Count) ShowTip(null, null);
            else ShowTip(_cards[index].Root, Strings.Card(_cards[index].Info.Id));
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
