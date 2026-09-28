using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// E8, the Tác chiến tab: everything played again and again. On the left the entries, each with
    /// its picture, a line of what it is and its clock: this week's operation, the campaign's
    /// operations to replay, the weekly fortress, Boss Rush and today's challenges. On the right the
    /// chosen one: its rules as they are now, its reward, its tiers and records, and the one main
    /// button, START (the challenges have claim buttons instead).
    /// </summary>
    internal sealed partial class MenuScreen
    {
        /// <summary>The modes the Tác chiến tab starts itself (with the operations), for the menu's coverage test.</summary>
        internal static readonly GameModeKind[] OperationsModes = { GameModeKind.Weekly, GameModeKind.BossRush, GameModeKind.Campaign };

        private enum OpsEntry
        {
            WeeklyOperation,
            Operations,
            WeeklyFortress,
            BossRush,
            Daily,
        }

        private VisualElement _opsEntries, _opsDetail;
        private OpsEntry _opsEntry = OpsEntry.WeeklyOperation;
        private int _opsSelected = -1, _opsTier;

        private void BuildOperationsPage()
        {
            var page = TabPage(Tab.Operations, "fc-page--opaque fc-ops");
            var list = Kit.Scroll(ScrollViewMode.Vertical, "fc-ops__list");
            _opsEntries = list.contentContainer;
            page.Add(list);
            _opsDetail = Kit.Box(KitPanel.SurfaceClass + " fc-ops__detail", PickingMode.Position);
            page.Add(_opsDetail);
            page.schedule.Execute(() =>
            {
                if (_tab == Tab.Operations && _overlays.Count == 0)
                    foreach (var clock in _opsEntries.Query<Label>(className: "fc-ops__clock").ToList()) clock.text = WeekResetText();
            }).Every(1000);
        }

        /// <summary>The time left this ISO week (UTC): the weekly operation and fortress change then.</summary>
        private static string WeekResetText()
        {
            var now = DateTime.UtcNow;
            var daysToMonday = ((int)DayOfWeek.Monday - (int)now.DayOfWeek + 7) % 7;
            if (daysToMonday == 0) daysToMonday = 7;
            var left = now.Date.AddDays(daysToMonday) - now;
            return Strings.Format("ops.weekLeft", left.Days, left.Hours);
        }

        private void RefreshOperationsTab()
        {
            if (_opsEntries == null || _tab != Tab.Operations) return;
            if (_opsEntry == OpsEntry.WeeklyOperation && Operations.ThisWeek == null) _opsEntry = OpsEntry.Operations;
            _opsEntries.Clear();
            if (Operations.ThisWeek is { } week)
                _opsEntries.Add(OpsCard(OpsEntry.WeeklyOperation, MapArt.For(week.mission.Map), Strings.Get("ops.weekly"),
                    Strings.Get("mission." + week.mission.Id + ".name"), true));
            var replay = Operations.Replayable;
            _opsEntries.Add(OpsCard(OpsEntry.Operations, replay.Count > 0 ? MapArt.For(replay[0].Map) : null, Strings.Get("ops.replayTitle"),
                Strings.Format("ops.count", replay.Count), false));
            _opsEntries.Add(OpsCard(OpsEntry.WeeklyFortress, MapArt.For(WeeklyFortress.MapId), Strings.Get("mode.weekly"),
                Strings.Format("events.weeklyStage", PlayerProfile.WeeklyStage(WeeklyFortress.Week)), true));
            _opsEntries.Add(OpsCard(OpsEntry.BossRush, CardArt.For("behemoth"), Strings.Get("mode.bossrush"),
                Strings.Format("mode.bossrushSub", BossRushRules.Kinds.Count), false));
            var dailyCard = OpsCard(OpsEntry.Daily, null, Strings.Get("daily.titleShort"), DailyResetText(), false);
            KitDot.Attach(dailyCard, DailyClaimable());
            _opsEntries.Add(dailyCard);
            FillOpsDetail();
        }

        private VisualElement OpsCard(OpsEntry entry, Texture2D picture, string title, string line, bool weekly)
        {
            var card = Kit.Tappable(KitPanel.SurfaceClass + " fc-ops__card" + (entry == _opsEntry ? " fc-ops__card--chosen" : ""), () =>
            {
                _opsEntry = entry;
                Refresh();
            });
            var art = Kit.Box("fc-ops__art");
            if (picture != null) art.style.backgroundImage = Background.FromTexture2D(picture);
            else art.Add(Kit.Icon(entry == OpsEntry.Daily ? "check" : "swords", "fc-ops__art-icon"));
            card.Add(art);
            var text = Kit.Box("fc-ops__text");
            text.Add(Kit.Text(Kit.Caps(title), "fc-panel-title"));
            text.Add(Kit.Small(line));
            if (weekly)
            {
                var clock = Kit.Box("fc-row fc-mt-1");
                clock.Add(Kit.Icon("restart", "fc-rule-icon"));
                clock.Add(Kit.Text(WeekResetText(), "fc-small fc-ops__clock fc-ml-2"));
                text.Add(clock);
            }
            card.Add(text);
            return card;
        }

        private void FillOpsDetail()
        {
            _opsDetail.Clear();
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-ops__detail-scroll");
            var body = Kit.Box("fc-ops__detail-body");
            scroll.Add(body);
            _opsDetail.Add(scroll);
            KitButton start = null;
            switch (_opsEntry)
            {
                case OpsEntry.WeeklyOperation when Operations.ThisWeek is { } week:
                    body.Add(Kit.Caption(Strings.Get("ops.weekly")));
                    body.Add(Kit.Text(Kit.Caps(Strings.Get("mission." + week.mission.Id + ".name")), "fc-title"));
                    body.Add(Kit.Text(Strings.Format("ops.weeklySub", Strings.Get("mutator." + week.a.Id), Strings.Get("mutator." + week.b.Id),
                        Kit.Count(Operations.Data.WeeklyOperationReward)), "fc-body fc-mt-2"));
                    body.Add(Rule("restart", WeekResetText()));
                    body.Add(Rule("coin", Strings.Format("ops.reward", Kit.Count(Operations.Data.WeeklyOperationReward))));
                    OpsTiers(body);
                    start = new KitButton(ButtonTier.Primary, Strings.Get("ops.start"), () =>
                    {
                        _opsSelected = IndexOfReplayable(week.mission.Id);
                        StartOperation(true);
                    }, "play");
                    break;
                case OpsEntry.WeeklyFortress:
                    body.Add(Kit.Caption(Strings.Get("mode.weekly")));
                    body.Add(Kit.Text(Kit.Caps(Strings.Get("map." + WeeklyFortress.MapId)), "fc-title"));
                    body.Add(Kit.Text(Strings.Get("mode.weeklySub"), "fc-body fc-mt-2"));
                    body.Add(Rule("home", Strings.Format("events.weeklyStage", PlayerProfile.WeeklyStage(WeeklyFortress.Week))));
                    body.Add(Rule("restart", WeekResetText()));
                    body.Add(Rule("coin", Strings.Format("ops.rewardFirstWin", Kit.Count(WeeklyFortress.Reward))));
                    start = PlayButton(GameModeKind.Weekly);
                    break;
                case OpsEntry.BossRush:
                    body.Add(Kit.Caption(Strings.Get("mode.bossrush")));
                    body.Add(Kit.Text(Kit.Caps(Strings.Format("mode.bossrushSub", BossRushRules.Kinds.Count)), "fc-title"));
                    body.Add(Kit.Text(Strings.Format("ops.bossRushRules", BossRushRules.Kinds.Count, Mathf.RoundToInt(new BossRushRules().TimeLimit / 60f)), "fc-body fc-mt-2"));
                    var bosses = Kit.Box("fc-row fc-row--wrap fc-row--top fc-mt-3");
                    foreach (var kind in BossRushRules.Kinds)
                    {
                        var id = kind[0];
                        bosses.Add(new KitVehicleCard(new VehicleCardData
                        {
                            Id = id, Name = Strings.Unit(id), Branch = KitBranch.Armor, ClassIcon = "skull", Art = CardArt.For(id), Level = 1,
                        }, null, compact: true));
                    }
                    body.Add(bosses);
                    start = PlayButton(GameModeKind.BossRush);
                    break;
                case OpsEntry.Daily:
                    body.Add(Kit.Caption(Strings.Get("daily.titleShort")));
                    body.Add(Kit.Text(DailyResetText(), "fc-body-2 fc-mb-3"));
                    var tasks = DailyMissions.Current;
                    for (var i = 0; i < tasks.Count; i++) body.Add(DailyRow(i, tasks[i]));
                    body.Add(Kit.Small(Strings.Get("events.dailyNote")));
                    break;
                default:
                    OperationsDetail(body);
                    start = new KitButton(ButtonTier.Primary, Strings.Get("ops.start"), () => StartOperation(false), "play");
                    break;
            }
            if (start == null) return;
            start.AddToClassList("fc-ops__start");
            _opsDetail.Add(start);
        }

        private static VisualElement Rule(string icon, string text)
        {
            var row = Kit.Box("fc-row fc-mt-2");
            row.Add(Kit.Icon(icon, "fc-rule-icon"));
            row.Add(Kit.Text(text, "fc-body fc-row-text fc-ml-2"));
            return row;
        }

        private KitButton PlayButton(GameModeKind mode) => new(ButtonTier.Primary, Strings.Get("ops.start"), () =>
        {
            MatchSettings.Mode = mode;
            MatchSettings.Save();
            _play();
        }, "play");

        /// <summary>The campaign's operations to replay: the list, the tier chips and the record per tier.</summary>
        private void OperationsDetail(VisualElement body)
        {
            var list = Operations.Replayable;
            body.Add(Kit.Caption(Strings.Get("ops.replayTitle")));
            body.Add(Kit.Text(Strings.Get("ops.sub"), "fc-body-2 fc-mb-3"));
            if (list.Count == 0) body.Add(Kit.Body2(Strings.Get("ops.none")));
            if (_opsSelected >= list.Count) _opsSelected = -1;
            if (_opsSelected < 0 && list.Count > 0) _opsSelected = 0;
            for (var i = 0; i < list.Count; i++)
            {
                var index = i;
                var m = list[i];
                var row = Kit.Tappable("fc-mission" + (i == _opsSelected ? " fc-mission--chosen" : "") + (Operations.Unlocked(m) ? "" : " fc-mission--locked"), () =>
                {
                    _opsSelected = index;
                    Refresh();
                });
                row.Add(Kit.Icon(m.Operation ? "flag" : "swords", "fc-mission__icon"));
                var text = Kit.Box("fc-mission__text");
                text.Add(Kit.Text(Strings.Get("mission." + m.Id + ".name"), "fc-body"));
                var best = PlayerProfile.BestScore(m.Id, _opsTier);
                text.Add(Kit.Small(!Operations.Unlocked(m) ? Strings.Get("ops.locked") : best > 0 ? $"{Strings.Get("ops.best")} {Kit.Count(best)}" : Strings.Get("ops.noRecord")));
                row.Add(text);
                body.Add(row);
            }
            OpsTiers(body);
        }

        private void OpsTiers(VisualElement body)
        {
            body.Add(Kit.Text(Kit.Caps(Strings.Get("campaign.tierTitle")), "fc-panel-title fc-section__title fc-mt-4"));
            var chips = new List<VisualElement>();
            for (var t = 0; t < Operations.Data.Tiers.Count; t++)
            {
                var tier = t;
                chips.Add(new KitChip(Strings.Get("tier." + t), t == _opsTier, () =>
                {
                    _opsTier = tier;
                    Refresh();
                }, Operations.TierOpen(t) ? null : "lock"));
            }
            body.Add(new KitChipRow(chips));
            var list = Operations.Replayable;
            var detail = !Operations.TierOpen(_opsTier) ? Strings.Get("ops.legendLocked")
                : _opsSelected >= 0 && _opsSelected < list.Count && PlayerProfile.BestTime(list[_opsSelected].Id, _opsTier) is var time && time > 0f
                    ? $"{Strings.Get("ops.best")}: {Kit.Count(PlayerProfile.BestScore(list[_opsSelected].Id, _opsTier))} · {(int)time / 60}:{(int)time % 60:00}"
                    : "";
            if (detail.Length > 0) body.Add(Kit.Small(detail));
        }

        private static int IndexOfReplayable(string id)
        {
            var list = Operations.Replayable;
            for (var i = 0; i < list.Count; i++)
                if (list[i].Id == id) return i;
            return -1;
        }

        private void StartOperation(bool weekly)
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
            MatchSettings.Run = Operations.Run(mission, _opsTier, weekly);
            MatchSettings.Save();
            _play();
        }
    }
}
