using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>One card in the deck bar.</summary>
    public readonly struct CardInfo
    {
        public CardInfo(string id, bool support, int cost, string icon, int missiles = 0, int flares = 0)
        {
            Id = id;
            Support = support;
            Cost = cost;
            Icon = icon;
            Missiles = missiles;
            Flares = flares;
        }

        /// <summary>Prompt 29 L5: its own missile mount's load and its flare charges, for the card's badges (0: none).</summary>
        public int Missiles { get; }
        public int Flares { get; }

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

            // Prompt 32 L4: the HQ's skill, the one new button (beside the CP box, its icon by the HQ type); hidden until
            // the side has an HQ type in play. A tap uses it (a Fortress's barrage then waits for a tap on the map).
            _skill = new Card { Info = new CardInfo("hq.skill", true, 0, "hq") };
            _skill.Root = Kit.Box("fc-hcard fc-hcard--support fc-hcard--hqskill", PickingMode.Position);
            _skill.Root.AddManipulator(new Tap(() =>
            {
                UiKit.RaiseClicked();
                SkillPressed?.Invoke();
            }, held => ShowSkillTip(held)));
            var skillArt = Kit.Box("fc-hcard__art");
            _skillIcon = Kit.Icon("hq", "fc-hcard__icon");
            skillArt.Add(_skillIcon);
            _skill.Sweep = new CooldownSweep();
            skillArt.Add(_skill.Sweep);
            _skill.Seconds = Kit.Text("", "fc-number-small fc-hcard__seconds");
            skillArt.Add(_skill.Seconds);
            _skill.Root.Add(skillArt);
            _skillName = Kit.Text("", compact ? "fc-hcard__name fc-hcard__name--short" : "fc-caption fc-hcard__name");
            Kit.FixedLines(_skillName, compact ? 1 : 2);
            _skill.Root.Add(_skillName);
            _skill.Root.style.display = DisplayStyle.None;
            Root.Add(_skill.Root);

            // Play-test 14: the hangar rally point (only while the side has a vehicle or aircraft hangar): a tap arms it, the
            // next tap on the map sets it.
            _rally = Kit.Box("fc-hcard fc-hcard--support fc-hcard--rally", PickingMode.Position);
            _rally.AddManipulator(new Tap(() =>
            {
                UiKit.RaiseClicked();
                RallyPressed?.Invoke();
            }));
            var rallyArt = Kit.Box("fc-hcard__art");
            rallyArt.Add(Kit.Icon("flag", "fc-hcard__icon"));
            _rally.Add(rallyArt);
            var rallyName = Kit.Text(Strings.Get("hangar.rally"), compact ? "fc-hcard__name fc-hcard__name--short" : "fc-caption fc-hcard__name");
            Kit.FixedLines(rallyName, compact ? 1 : 2);
            _rally.Add(rallyName);
            _rally.style.display = DisplayStyle.None;
            Root.Add(_rally);

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
                }, held => ShowTip(root, held ? info.Id : null)));
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
                var badges = Kit.Box("fc-hcard__badges");
                // Prompt 29 L5: small flat marks for the missile mount's load and the flare charges.
                if (info.Missiles > 0) badges.Add(Badge("missile", info.Missiles));
                if (info.Flares > 0) badges.Add(Badge("flares", info.Flares));
                art.Add(badges);
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
            _tipRow = Kit.Box("fc-deck__tip-row");
            _tip.Add(_tipRow);
            _tip.style.display = DisplayStyle.None;
            Root.Add(_tip);
        }

        /// <summary>
        /// Prompt 15 E3: what a held card shows under its full name, its armour and every weapon's chip (the tray
        /// itself shows none, to keep the HUD low). Set by the HUD, which has the catalog; null shows the name only.
        /// </summary>
        internal Func<string, VisualElement> TipRow;

        private readonly VisualElement _tipRow;

        /// <summary>A badge in the card's top-left corner: a small icon and a number on the field panel.</summary>
        private static VisualElement Badge(string icon, int count)
        {
            var badge = Kit.Box("fc-hcard__badge", PickingMode.Ignore);
            badge.Add(Kit.Icon(icon, "fc-hcard__badge-icon", 2f));
            badge.Add(Kit.Text(count.ToString(), "fc-hcard__badge-text"));
            return badge;
        }

        /// <summary>Shows a held card's full name (and its armour and weapons) over it; null hides it.</summary>
        private void ShowTip(VisualElement card, string id)
        {
            if (id == null)
            {
                _tip.style.display = DisplayStyle.None;
                return;
            }
            _tipName.text = Strings.Card(id);
            _tipRow.Clear();
            if (TipRow?.Invoke(id) is { } row) _tipRow.Add(row);
            _tip.style.display = DisplayStyle.Flex;
            // Centred over the card, kept inside the tray.
            var x = card.worldBound.center.x - Root.worldBound.xMin;
            _tip.style.left = Mathf.Max(0f, x - 120f);
        }

        /// <summary>A card's full name shown as when held (the screenshot tool); -1 hides it.</summary>
        internal void PreviewHeld(int index)
        {
            if (index < 0 || index >= _cards.Count) ShowTip(null, null);
            else ShowTip(_cards[index].Root, _cards[index].Info.Id);
        }

        public VisualElement Root { get; }

        public event Action<int> CardPressed;

        /// <summary>Prompt 32 L4: the HQ skill button was tapped.</summary>
        public event Action SkillPressed;

        /// <summary>Play-test 14: the hangar rally button was tapped.</summary>
        public event Action RallyPressed;

        private readonly VisualElement _rally;
        private bool _rallyShown;

        /// <summary>Play-test 14: the hangar rally button: shown while the side has a hangar, armed while it waits for its point.</summary>
        public void SetRally(bool show, bool armed)
        {
            if (show != _rallyShown)
            {
                _rallyShown = show;
                _rally.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
            }
            _rally.EnableInClassList("fc-hcard--armed", show && armed);
        }

        private readonly Card _skill;
        private readonly VisualElement _skillIcon;
        private readonly Label _skillName;
        private string _skillShownIcon, _skillTip;
        private bool _skillShown;

        /// <summary>A held HQ skill button shows what the skill does over the tray.</summary>
        private void ShowSkillTip(bool held)
        {
            if (!held || string.IsNullOrEmpty(_skillTip))
            {
                _tip.style.display = DisplayStyle.None;
                return;
            }
            _tipName.text = _skillTip;
            _tipRow.Clear();
            _tip.style.display = DisplayStyle.Flex;
            var x = _skill.Root.worldBound.center.x - Root.worldBound.xMin;
            _tip.style.left = Mathf.Max(0f, x - 120f);
        }

        /// <summary>
        /// Prompt 32 L4: the HQ skill button: hidden without an HQ type (<paramref name="icon"/> null); else its icon and
        /// short name by the type, the cooldown's sweep and seconds, armed while a Fortress's barrage waits for its point.
        /// </summary>
        public void SetSkill(string icon, string name, string tip, float share, float seconds, bool armed)
        {
            var show = icon != null;
            if (show != _skillShown)
            {
                _skillShown = show;
                _skill.Root.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
            }
            if (!show) return;
            if (icon != _skillShownIcon)
            {
                _skillShownIcon = icon;
                var old = _skillIconNow ?? _skillIcon;
                var fresh = Kit.Icon(icon, "fc-hcard__icon");
                if (old.parent is { } parent)
                {
                    parent.Insert(parent.IndexOf(old), fresh);
                    old.RemoveFromHierarchy();
                }
                _skillIconNow = fresh;
            }
            if (_skillName.text != name) _skillName.text = name;
            _skillTip = tip;
            var cooling = share > 0f;
            _skill.Root.EnableInClassList("fc-hcard--armed", armed);
            _skill.Root.EnableInClassList("fc-hcard--cooling", cooling);
            var sweep = Mathf.Round(Mathf.Clamp01(share) * 100f) / 100f;
            if (!Mathf.Approximately(sweep, _skill.ShownCooldown)) _skill.Sweep.Share = _skill.ShownCooldown = sweep;
            var whole = cooling ? Mathf.CeilToInt(seconds) : 0;
            if (whole != _skill.ShownSeconds)
            {
                _skill.ShownSeconds = whole;
                _skill.Seconds.text = whole > 0 ? whole.ToString() : "";
            }
        }

        private VisualElement _skillIconNow;

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
                _income.text = Strings.Format("hud.income", (tenths / 10f).ToString("0.0", Strings.Culture));
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
