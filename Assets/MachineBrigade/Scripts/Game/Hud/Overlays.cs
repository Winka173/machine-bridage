using System;
using System.Collections.Generic;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>What a finished battle pays, for the result card.</summary>
    public sealed class RewardView
    {
        public int Coins { get; set; }
        public int Xp { get; set; }

        /// <summary>Stars won; negative for battles without stars.</summary>
        public int Stars { get; set; } = -1;

        public List<string> Unlocked { get; } = new();

        /// <summary>Crates the battle paid (their names).</summary>
        public List<string> Crates { get; } = new();

        /// <summary>The campaign's other pay-outs, as they read (blueprints, an HQ level, a tower piece, the Dossier's new file), each with its icon.</summary>
        public List<(string icon, string text)> Extras { get; } = new();

        /// <summary>A lost multi-stage mission with a checkpoint: offer to go back to it.</summary>
        public bool CanResume { get; set; }

        /// <summary>A rewarded ad may double the coins.</summary>
        public bool CanDouble { get; set; }

        /// <summary>A campaign win with another mission to go to.</summary>
        public bool HasNext { get; set; }
    }

    /// <summary>
    /// End-of-match card on the kit (Field Command 2.0, E10): the outcome and the mission's or the
    /// mode's name (never both), the stars, the numbers (a score says whose is whose), what it paid,
    /// after a defeat one or two things to change with a button to the deck, and the buttons: the one
    /// main action is CONTINUE after a win and PLAY AGAIN after a loss, back to the menu is secondary,
    /// and doubling the coins with an ad is a Claim button.
    /// </summary>
    internal sealed class ResultPanel
    {
        private readonly Action _again, _menu, _doubleCoins, _next, _checkpoint;
        private readonly Label _outcome, _title, _note, _coins, _xp;
        private readonly IconElement _outcomeIcon;
        private readonly VisualElement _head, _stars, _rows, _side, _rewardBox, _reward, _doubled, _unlocks, _hintBox, _hints, _buttons, _claim;
        private readonly KitButton _deck;
        private KitButton _double;
        private RewardView _shown;

        public ResultPanel(Action again, Action menu, Action doubleCoins, Action next, Action checkpoint, Action deck = null)
        {
            _again = again;
            _menu = menu;
            _doubleCoins = doubleCoins;
            _next = next;
            _checkpoint = checkpoint;
            Root = Kit.Root(KitDialog.ScrimClass + " fc-result");
            Root.pickingMode = PickingMode.Position;
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-result__card", PickingMode.Position);

            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-result__scroll");
            var columns = Kit.Box("fc-result__columns");
            var main = Kit.Box("fc-result__main");
            _head = Kit.Box("fc-result__outcome");
            _outcomeIcon = Kit.Icon("trophy");
            _head.Add(_outcomeIcon);
            _outcome = Kit.Text("", "fc-caption fc-row-text");
            _head.Add(_outcome);
            main.Add(_head);
            _title = Kit.Text("", "fc-title fc-result__title");
            main.Add(_title);
            _note = Kit.Text("", "fc-body-2 fc-result__note");
            main.Add(_note);
            _stars = Kit.Box("fc-stars fc-result__stars");
            main.Add(_stars);
            _rows = Kit.Box("fc-result__rows");
            main.Add(_rows);
            columns.Add(main);

            _side = Kit.Box("fc-result__side");
            _rewardBox = Kit.Box("fc-result__block");
            _rewardBox.Add(Kit.Caption(Strings.Get("result.rewards")));
            _reward = Kit.Box("fc-result__reward");
            var coins = Kit.Box("fc-result__pay");
            coins.Add(Kit.Icon("coin", "fc-result__coin"));
            _coins = Kit.Text("", "fc-number fc-coin-text");
            coins.Add(_coins);
            _doubled = Kit.Box("fc-tag fc-result__doubled");
            _doubled.Add(Kit.Text("×2", "fc-small"));
            coins.Add(_doubled);
            _reward.Add(coins);
            var xp = Kit.Box("fc-result__pay");
            xp.Add(Kit.Icon("rank"));
            _xp = Kit.Text("", "fc-number-small");
            xp.Add(_xp);
            _reward.Add(xp);
            _rewardBox.Add(_reward);
            _unlocks = Kit.Box("fc-row fc-row--wrap fc-result__unlocks");
            _rewardBox.Add(_unlocks);
            // Doubling the coins with an ad sits by the coins it doubles.
            _claim = Kit.Box("fc-result__claim");
            _rewardBox.Add(_claim);
            _side.Add(_rewardBox);

            _hintBox = Kit.Box("fc-result__block fc-result__hints");
            _hintBox.Add(Kit.Caption(Strings.Get("result.hints")));
            _hints = Kit.Box("");
            _hintBox.Add(_hints);
            _deck = new KitButton(ButtonTier.Text, Strings.Get("result.deck"), deck, "deck");
            _hintBox.Add(_deck);
            _side.Add(_hintBox);
            columns.Add(_side);
            scroll.Add(columns);
            card.Add(scroll);

            _buttons = Kit.Box("fc-result__buttons");
            card.Add(_buttons);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible => Root.style.display == DisplayStyle.Flex;

        /// <param name="outcome">1 victory, 0 draw, -1 defeat.</param>
        /// <param name="title">The mission's name or the mode's.</param>
        public void Show(int outcome, string title, IReadOnlyList<(string label, string value)> rows, RewardView reward,
            string note = null, IReadOnlyList<string> hints = null)
        {
            Kit.ApplyTextSize(Root);
            _shown = reward;
            _outcome.text = Kit.Caps(Strings.Get(outcome > 0 ? "result.victory" : outcome < 0 ? "result.defeat" : "result.draw"));
            _outcomeIcon.Name = outcome < 0 ? "skull" : outcome > 0 ? "trophy" : "flag";
            _head.EnableInClassList("fc-result__outcome--win", outcome > 0);
            _head.EnableInClassList("fc-result__outcome--loss", outcome < 0);
            _title.text = Kit.Caps(title ?? "");
            _title.style.display = string.IsNullOrEmpty(title) ? DisplayStyle.None : DisplayStyle.Flex;
            if (note == null && outcome <= 0 && reward is { CanResume: true }) note = Strings.Get("result.checkpointNote");
            _note.text = note ?? "";
            _note.style.display = string.IsNullOrEmpty(note) ? DisplayStyle.None : DisplayStyle.Flex;

            _rows.Clear();
            foreach (var (label, value) in rows)
            {
                var row = Kit.Box("fc-result__row");
                row.Add(Kit.Text(label, "fc-body-2 fc-row-text"));
                row.Add(Kit.Text(value, "fc-number-small fc-result__value"));
                _rows.Add(row);
            }

            _stars.Clear();
            _unlocks.Clear();
            var hasReward = reward != null;
            _stars.style.display = hasReward && reward.Stars >= 0 && outcome > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            _rewardBox.style.display = hasReward ? DisplayStyle.Flex : DisplayStyle.None;
            if (hasReward)
            {
                _coins.text = "+" + Kit.Count(reward.Coins);
                _xp.text = Strings.Format("result.xp", Kit.Count(reward.Xp));
                _doubled.style.display = DisplayStyle.None;
                for (var i = 0; i < 3 && reward.Stars >= 0; i++) _stars.Add(Kit.Icon("star", i < reward.Stars ? "fc-star fc-star--on" : "fc-star"));
                foreach (var name in reward.Unlocked) _unlocks.Add(Chip("lock", Strings.Format("result.unlocked", name)));
                foreach (var name in reward.Crates) _unlocks.Add(Chip("crate", Strings.Format("result.crate", name)));
                foreach (var (icon, text) in reward.Extras) _unlocks.Add(Chip(icon, text));
            }
            _unlocks.style.display = _unlocks.childCount > 0 ? DisplayStyle.Flex : DisplayStyle.None;

            _hints.Clear();
            if (outcome <= 0 && hints != null)
                foreach (var hint in hints)
                {
                    var line = Kit.Box("fc-result__hint");
                    line.Add(Kit.Icon("info"));
                    line.Add(Kit.Text(hint, "fc-body fc-row-text"));
                    _hints.Add(line);
                }
            _hintBox.style.display = _hints.childCount > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            _side.style.display = hasReward || _hints.childCount > 0 ? DisplayStyle.Flex : DisplayStyle.None;

            BuildButtons(outcome, reward);
            Root.style.display = DisplayStyle.Flex;
        }

        /// <summary>
        /// Secondary first, then the one main action (the kit's dialog order); the Claim is by the coins:
        /// a win goes on (the next mission, or back to the menu), a loss plays again (from the
        /// checkpoint when a multi-stage mission kept one).
        /// </summary>
        private void BuildButtons(int outcome, RewardView reward)
        {
            _buttons.Clear();
            var next = outcome > 0 && reward is { HasNext: true };
            var checkpoint = outcome <= 0 && reward is { CanResume: true };
            if (outcome > 0)
            {
                if (next) _buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("result.menu"), _menu, "home"));
                else _buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("result.again"), _again, "restart"));
            }
            else
            {
                _buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("result.menu"), _menu, "home"));
                if (checkpoint) _buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("result.fromStart"), _again, "restart"));
            }
            _claim.Clear();
            _double = null;
            if (reward is { CanDouble: true, Coins: > 0 })
            {
                _double = new KitButton(ButtonTier.Claim, Strings.Get("result.double"), _doubleCoins);
                _claim.Add(_double);
            }
            _claim.style.display = _double != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (outcome > 0) _buttons.Add(new KitButton(ButtonTier.Primary, Strings.Get("result.continue"), next ? _next : _menu, "arrow"));
            else if (checkpoint) _buttons.Add(new KitButton(ButtonTier.Primary, Strings.Get("result.again"), _checkpoint, "flag"));
            else _buttons.Add(new KitButton(ButtonTier.Primary, Strings.Get("result.again"), _again, "restart"));
        }

        /// <summary>The coins were paid: shows the final amount, and "×2" after an ad.</summary>
        public void ShowClaimed(int coins, bool doubled)
        {
            _coins.text = "+" + Kit.Count(coins);
            _doubled.style.display = doubled ? DisplayStyle.Flex : DisplayStyle.None;
            _claim.Clear();
            _claim.style.display = DisplayStyle.None;
            _double = null;
            if (_shown != null) _shown.CanDouble = false;
        }

        private static VisualElement Chip(string icon, string text)
        {
            var chip = Kit.Box("fc-tag");
            chip.Add(Kit.Icon(icon));
            chip.Add(Kit.Text(text, "fc-small"));
            return chip;
        }
    }

    /// <summary>
    /// A multi-stage mission's branching point: the ways on, and the seconds left before the first
    /// is taken. The battle does not stop for it. The first way is the main action.
    /// </summary>
    internal sealed class ChoicePanel
    {
        private readonly Label _title, _time;
        private readonly VisualElement _options;

        public ChoicePanel()
        {
            Root = Kit.Root(KitDialog.ScrimClass + " fc-choice");
            Root.pickingMode = PickingMode.Position;
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-dialog fc-choice__card", PickingMode.Position);
            var head = Kit.Box("fc-row fc-mb-2");
            head.Add(Kit.Icon("flag", "fc-choice__icon"));
            _title = Kit.Text("", "fc-panel-title fc-row-text");
            head.Add(_title);
            card.Add(head);
            _time = Kit.Text("", "fc-body-2 fc-mb-2");
            card.Add(_time);
            _options = Kit.Box("fc-choice__options");
            card.Add(_options);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible => Root.style.display == DisplayStyle.Flex;

        public void Show(string title, IReadOnlyList<(string label, string detail)> options, Action<int> chosen)
        {
            Kit.ApplyTextSize(Root);
            _title.text = Kit.Caps(title);
            _options.Clear();
            for (var i = 0; i < options.Count; i++)
            {
                var index = i;
                var option = Kit.Box("fc-choice__option");
                option.Add(new KitButton(i == 0 ? ButtonTier.Primary : ButtonTier.Secondary, options[i].label, () => chosen(index), "arrow"));
                if (!string.IsNullOrEmpty(options[i].detail)) option.Add(Kit.Text(options[i].detail, "fc-body-2 fc-choice__detail"));
                _options.Add(option);
            }
            Root.style.display = DisplayStyle.Flex;
        }

        public void SetTime(float seconds) => _time.text = Strings.Format("choice.auto", UnityEngine.Mathf.CeilToInt(seconds));

        public void Hide() => Root.style.display = DisplayStyle.None;
    }

    /// <summary>Pause menu on the kit: resume (the main action), restart or leave.</summary>
    internal sealed class PausePanel
    {
        public PausePanel(Action resume, Action restart, Action menu)
        {
            Root = Kit.Root(KitDialog.ScrimClass + " fc-pause");
            Root.pickingMode = PickingMode.Position;
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-dialog fc-pause__card", PickingMode.Position);
            var head = Kit.Box("fc-row fc-mb-2");
            head.Add(Kit.Icon("pause"));
            head.Add(Kit.Text(Kit.Caps(Strings.Get("pause.title")), "fc-title fc-row-text fc-pause__title"));
            card.Add(head);
            var buttons = Kit.Box("fc-pause__buttons");
            buttons.Add(new KitButton(ButtonTier.Primary, Strings.Get("pause.resume"), resume, "play"));
            buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("result.again"), restart, "restart"));
            buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("result.menu"), menu, "home"));
            card.Add(buttons);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible
        {
            get => Root.style.display == DisplayStyle.Flex;
            set
            {
                if (value) Kit.ApplyTextSize(Root);
                Root.style.display = value ? DisplayStyle.Flex : DisplayStyle.None;
            }
        }
    }
}
