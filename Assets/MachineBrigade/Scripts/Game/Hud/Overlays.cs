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

        /// <summary>A rewarded ad may double the coins.</summary>
        public bool CanDouble { get; set; }

        /// <summary>A campaign win with another mission to go to.</summary>
        public bool HasNext { get; set; }
    }

    /// <summary>
    /// End-of-match card: the result, a few numbers, what it paid (coins, XP, stars, unlocks),
    /// the offer to double the coins with an ad, and where to go next.
    /// </summary>
    internal sealed class ResultPanel
    {
        private readonly Label _title, _subtitle, _coins, _xp, _doubled;
        private readonly VisualElement _rows, _head, _reward, _stars, _unlocks, _double, _next, _again;
        private readonly IconElement _icon;

        public ResultPanel(Action again, Action menu, Action doubleCoins, Action next)
        {
            Root = UiKit.Box("overlay", PickingMode.Position);
            var card = UiKit.Box("result-card");
            _head = UiKit.Box("result-head victory");
            _icon = UiKit.Icon("trophy", UiKit.Ink, 1.8f);
            _head.Add(_icon);
            _title = UiKit.Text("", "result-title");
            _head.Add(_title);
            card.Add(_head);
            _subtitle = UiKit.Text("", "result-sub");
            card.Add(_subtitle);
            _stars = UiKit.Box("result-stars");
            card.Add(_stars);
            _rows = UiKit.Box("result-rows");
            card.Add(_rows);

            _reward = UiKit.Box("result-reward");
            var coins = UiKit.Box("reward-item coins");
            coins.Add(UiKit.Icon("coin", UiKit.Ink, 1.8f));
            _coins = UiKit.Text("", "reward-value");
            coins.Add(_coins);
            _doubled = UiKit.Text("x2", "reward-doubled");
            _doubled.style.display = DisplayStyle.None;
            coins.Add(_doubled);
            _reward.Add(coins);
            var xp = UiKit.Box("reward-item xp");
            xp.Add(UiKit.Icon("rank", UiKit.Ink, 1.8f));
            _xp = UiKit.Text("", "reward-value");
            xp.Add(_xp);
            _reward.Add(xp);
            card.Add(_reward);
            _unlocks = UiKit.Box("result-unlocks");
            card.Add(_unlocks);

            var buttons = UiKit.Box("result-buttons");
            _double = UiKit.WideButton("wide ad-button", "ad", Strings.Get("result.double"), Strings.Get("result.doubleSub"), doubleCoins);
            buttons.Add(_double);
            _next = UiKit.WideButton("wide primary", "arrow", Strings.Get("result.next"), null, next);
            buttons.Add(_next);
            _again = UiKit.WideButton("wide primary", "restart", Strings.Get("result.again"), null, again);
            buttons.Add(_again);
            buttons.Add(UiKit.WideButton("wide", "home", Strings.Get("result.menu"), null, menu));
            card.Add(buttons);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible => Root.style.display == DisplayStyle.Flex;

        /// <param name="outcome">1 victory, 0 draw, -1 defeat.</param>
        public void Show(int outcome, string subtitle, IReadOnlyList<(string label, string value)> rows, RewardView reward)
        {
            _title.text = Strings.Get(outcome > 0 ? "result.victory" : outcome < 0 ? "result.defeat" : "result.draw");
            _head.EnableInClassList("victory", outcome > 0);
            _head.EnableInClassList("defeat", outcome < 0);
            _icon.Name = outcome < 0 ? "skull" : outcome > 0 ? "trophy" : "flag";
            _subtitle.text = subtitle;
            _rows.Clear();
            foreach (var (label, value) in rows)
            {
                var row = UiKit.Box("result-row");
                row.Add(UiKit.Text(label, "result-label"));
                row.Add(UiKit.Text(value, "result-value"));
                _rows.Add(row);
            }

            _stars.Clear();
            _unlocks.Clear();
            var hasReward = reward != null;
            _reward.style.display = hasReward ? DisplayStyle.Flex : DisplayStyle.None;
            _stars.style.display = hasReward && reward.Stars >= 0 ? DisplayStyle.Flex : DisplayStyle.None;
            if (hasReward)
            {
                _coins.text = "+" + reward.Coins;
                _xp.text = $"+{reward.Xp} XP";
                _doubled.style.display = DisplayStyle.None;
                for (var i = 0; i < 3 && reward.Stars >= 0; i++)
                {
                    var star = UiKit.Icon("star", UiKit.Ink, 1.8f);
                    star.AddToClassList(i < reward.Stars ? "star-on" : "star-off");
                    _stars.Add(star);
                }
                foreach (var name in reward.Unlocked)
                {
                    var chip = UiKit.Box("unlock-chip");
                    chip.Add(UiKit.Icon("lock", UiKit.Ink, 1.6f));
                    chip.Add(UiKit.Text(Strings.Format("result.unlocked", name), "unlock-text"));
                    _unlocks.Add(chip);
                }
                foreach (var name in reward.Crates)
                {
                    var chip = UiKit.Box("unlock-chip crate-chip");
                    chip.Add(UiKit.Icon("crate", UiKit.Ink, 1.6f));
                    chip.Add(UiKit.Text(Strings.Format("result.crate", name), "unlock-text"));
                    _unlocks.Add(chip);
                }
            }
            _unlocks.style.display = hasReward && reward.Unlocked.Count + reward.Crates.Count > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            _double.style.display = hasReward && reward.CanDouble && reward.Coins > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            var next = hasReward && reward.HasNext;
            _next.style.display = next ? DisplayStyle.Flex : DisplayStyle.None;
            _again.EnableInClassList("primary", !next);
            Root.style.display = DisplayStyle.Flex;
        }

        /// <summary>The coins were paid: shows the final amount, and "x2" after an ad.</summary>
        public void ShowClaimed(int coins, bool doubled)
        {
            _coins.text = "+" + coins;
            _doubled.style.display = doubled ? DisplayStyle.Flex : DisplayStyle.None;
            _double.style.display = DisplayStyle.None;
        }
    }

    /// <summary>Pause menu: resume, restart or leave.</summary>
    internal sealed class PausePanel
    {
        public PausePanel(Action resume, Action restart, Action menu)
        {
            Root = UiKit.Box("overlay", PickingMode.Position);
            var card = UiKit.Box("result-card");
            var head = UiKit.Box("result-head");
            head.Add(UiKit.Icon("pause", UiKit.Ink, 1.8f));
            head.Add(UiKit.Text(Strings.Get("pause.title"), "result-title"));
            card.Add(head);
            var buttons = UiKit.Box("result-buttons");
            buttons.Add(UiKit.WideButton("wide primary", "play", Strings.Get("pause.resume"), null, resume));
            buttons.Add(UiKit.WideButton("wide", "restart", Strings.Get("result.again"), null, restart));
            buttons.Add(UiKit.WideButton("wide", "home", Strings.Get("result.menu"), null, menu));
            card.Add(buttons);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible
        {
            get => Root.style.display == DisplayStyle.Flex;
            set => Root.style.display = value ? DisplayStyle.Flex : DisplayStyle.None;
        }
    }
}
