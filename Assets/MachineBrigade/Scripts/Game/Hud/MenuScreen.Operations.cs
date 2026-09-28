using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The Operations part of the Tác chiến tab (prompt 6): this week's operation with its two
    /// mutators and reward, the list of battles the campaign has opened for replay, the four tier
    /// chips (Legend locked until the campaign's last operation is won), the record per tier, and
    /// one start button.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        /// <summary>The modes the Tác chiến tab starts itself (with the operations), for the menu's coverage test.</summary>
        internal static readonly GameModeKind[] OperationsModes = { GameModeKind.Weekly, GameModeKind.BossRush, GameModeKind.Campaign };

        private VisualElement _opsList, _opsTiers, _opsWeekly;
        private Label _opsDetail, _opsWeeklyTitle, _opsWeeklySub;
        private int _opsSelected = -1, _opsTier;
        private bool _opsWeeklySelected;

        private void BuildOperations(VisualElement into)
        {
            into.Add(UiKit.Text(Strings.Get("ops.title"), "menu-caps"));
            into.Add(UiKit.Text(Strings.Get("ops.sub"), "menu-note"));

            _opsWeekly = UiKit.Button("ops-weekly", () =>
            {
                if (Operations.ThisWeek is not { } week) return;
                _opsWeeklySelected = true;
                _opsSelected = IndexOfReplayable(week.mission.Id);
                RefreshOperations();
            });
            _opsWeeklyTitle = UiKit.Text("", "ops-weekly-title");
            _opsWeeklySub = UiKit.Text("", "ops-weekly-sub");
            _opsWeekly.Add(_opsWeeklyTitle);
            _opsWeekly.Add(_opsWeeklySub);
            into.Add(_opsWeekly);

            _opsList = UiKit.Box("ops-list");
            into.Add(_opsList);

            var foot = UiKit.Box("ops-foot");
            _opsTiers = UiKit.Box("ops-tiers");
            foot.Add(_opsTiers);
            _opsDetail = UiKit.Text("", "ops-detail");
            foot.Add(_opsDetail);
            var play = UiKit.Button("event-play primary", StartOperation);
            play.Add(UiKit.Icon("play", UiKit.Ink, 2f));
            play.Add(UiKit.Text(Strings.Get("events.play"), "event-play-text"));
            foot.Add(play);
            into.Add(foot);
        }

        private static int IndexOfReplayable(string id)
        {
            var list = Operations.Replayable;
            for (var i = 0; i < list.Count; i++)
                if (list[i].Id == id) return i;
            return -1;
        }

        private void StartOperation()
        {
            var list = Operations.Replayable;
            if (_opsSelected < 0 || _opsSelected >= list.Count) return;
            var mission = list[_opsSelected];
            if (!Operations.Unlocked(mission))
            {
                Note(Strings.Get("ops.locked"), true);
                return;
            }
            if (!Operations.TierOpen(_opsTier))
            {
                Note(Strings.Get("ops.legendLocked"), true);
                return;
            }
            MatchSettings.Mode = GameModeKind.Campaign;
            MatchSettings.Mission = mission.Id;
            MatchSettings.MissionTier = _opsTier;
            MatchSettings.Run = Operations.Run(mission, _opsTier, _opsWeeklySelected);
            MatchSettings.Save();
            _play();
        }

        private void RefreshOperations()
        {
            if (_opsList == null) return;
            var list = Operations.Replayable;
            if (Operations.ThisWeek is { } week)
            {
                _opsWeekly.style.display = DisplayStyle.Flex;
                _opsWeeklyTitle.text = Strings.Get("ops.weekly") + ": " + Strings.Get("mission." + week.mission.Id + ".name");
                _opsWeeklySub.text = Strings.Format("ops.weeklySub", Strings.Get("mutator." + week.a.Id), Strings.Get("mutator." + week.b.Id),
                    Operations.Data.WeeklyOperationReward);
                _opsWeekly.EnableInClassList("chosen", _opsWeeklySelected);
            }
            else _opsWeekly.style.display = DisplayStyle.None;

            _opsList.Clear();
            if (list.Count == 0) _opsList.Add(UiKit.Text(Strings.Get("ops.none"), "menu-note"));
            if (_opsSelected >= list.Count) _opsSelected = -1;
            if (_opsSelected < 0 && list.Count > 0) _opsSelected = 0;
            for (var i = 0; i < list.Count; i++)
            {
                var index = i;
                var m = list[i];
                var row = UiKit.Button(i == _opsSelected ? "ops-row chosen" : "ops-row", () =>
                {
                    _opsSelected = index;
                    _opsWeeklySelected = Operations.ThisWeek is { } w && w.mission.Id == list[index].Id && _opsWeeklySelected;
                    RefreshOperations();
                });
                row.Add(UiKit.Icon(m.Operation ? "flag" : "swords", UiKit.Ink, 1.6f));
                row.Add(UiKit.Text(Strings.Get("mission." + m.Id + ".name"), "ops-row-name"));
                var best = PlayerProfile.BestScore(m.Id, _opsTier);
                row.Add(UiKit.Text(!Operations.Unlocked(m) ? Strings.Get("ops.locked") : best > 0 ? $"{Strings.Get("ops.best")} {best:N0}" : "", "ops-row-best"));
                row.EnableInClassList("locked", !Operations.Unlocked(m));
                _opsList.Add(row);
            }

            _opsTiers.Clear();
            for (var t = 0; t < Operations.Data.Tiers.Count; t++)
            {
                var tier = t;
                var chip = UiKit.Button(t == _opsTier ? "tier-chip chosen" : "tier-chip", () =>
                {
                    _opsTier = tier;
                    RefreshOperations();
                });
                chip.Add(UiKit.Text(Strings.Get("tier." + t), "tier-name"));
                chip.EnableInClassList("locked", !Operations.TierOpen(t));
                _opsTiers.Add(chip);
            }
            _opsDetail.text = !Operations.TierOpen(_opsTier) ? Strings.Get("ops.legendLocked")
                : _opsSelected >= 0 && _opsSelected < list.Count && PlayerProfile.BestTime(list[_opsSelected].Id, _opsTier) is var time && time > 0f
                    ? $"{Strings.Get("ops.best")}: {PlayerProfile.BestScore(list[_opsSelected].Id, _opsTier):N0} · {(int)time / 60}:{(int)time % 60:00}"
                    : "";
        }
    }
}
