using System.Collections.Generic;
using MachineBrigade.Game.Match;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The Events tab: today's challenges with their rewards on the left, and the special battles
    /// on the right (the weekly fortress, the boss rush, survival), each one tap from starting.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private readonly List<(Label text, Label progress, VisualElement claim, Label reward, VisualElement fill)> _eventDailies = new();
        private Label _weeklyStage;

        private void BuildEventsPage()
        {
            var page = TabPage(Tab.Events, "events-page opaque");
            var columns = UiKit.Box("events-columns");

            var left = UiKit.Box("events-left");
            left.Add(UiKit.Text(Strings.Get("daily.title"), "menu-caps"));
            for (var i = 0; i < 3; i++)
            {
                var index = i;
                var row = UiKit.Box("event-daily");
                var text = UiKit.Text("", "event-daily-text");
                var track = UiKit.Box("event-daily-track");
                var fill = UiKit.Box("event-daily-fill");
                track.Add(fill);
                var progress = UiKit.Text("", "event-daily-progress");
                var info = UiKit.Box("event-daily-info");
                info.Add(text);
                info.Add(track);
                info.Add(progress);
                row.Add(info);
                var claim = UiKit.Button("event-claim", () =>
                {
                    if (DailyMissions.Claim(index))
                    {
                        Note(Strings.Get("daily.claimedNote"));
                        Refresh();
                    }
                });
                claim.Add(UiKit.Icon("coin", UiKit.Ink, 1.7f));
                var reward = UiKit.Text("", "event-claim-text");
                claim.Add(reward);
                row.Add(claim);
                left.Add(row);
                _eventDailies.Add((text, progress, claim, reward, fill));
            }
            left.Add(UiKit.Text(Strings.Get("events.dailyNote"), "menu-note"));
            columns.Add(left);

            var right = UiKit.Box("events-right");
            // Tác chiến (prompt 6): the weekly fortress and the boss rush first (under the operations
            // block they were out of sight), then the operations. Survival and Endless are challenges
            // chosen on the battle setup with the skirmishes.
            right.Add(UiKit.Text(Strings.Get("events.special"), "menu-caps"));
            right.Add(EventCard("home", "mode.weekly", "mode.weeklySub", GameModeKind.Weekly, out _weeklyStage));
            right.Add(EventCard("skull", "mode.bossrush", "mode.bossrushSub", GameModeKind.BossRush, out _));
            BuildOperations(right);
            columns.Add(right);
            page.Add(columns);
        }

        private Label _endlessBest;

        private VisualElement EventCard(string icon, string name, string sub, GameModeKind mode, out Label extra)
        {
            var card = UiKit.Box("event-card");
            card.Add(UiKit.Icon(icon, UiKit.Ink, 2f));
            var text = UiKit.Box("event-card-text");
            text.Add(UiKit.Text(Strings.Get(name), "event-card-title"));
            text.Add(UiKit.Text(Strings.Get(sub), "event-card-sub"));
            extra = UiKit.Text("", "event-card-extra");
            text.Add(extra);
            card.Add(text);
            var play = UiKit.Button("event-play", () =>
            {
                MatchSettings.Mode = mode;
                MatchSettings.Save();
                _play();
            });
            play.Add(UiKit.Icon("play", UiKit.Ink, 2f));
            play.Add(UiKit.Text(Strings.Get("events.play"), "event-play-text"));
            card.Add(play);
            return card;
        }

        private void RefreshEvents()
        {
            var tasks = DailyMissions.Current;
            for (var i = 0; i < _eventDailies.Count && i < tasks.Count; i++)
            {
                var (text, progress, claim, reward, fill) = _eventDailies[i];
                text.text = Strings.Format("daily." + tasks[i].Kind, tasks[i].Target);
                progress.text = $"{DailyMissions.Progress(i)}/{tasks[i].Target}";
                fill.style.width = Length.Percent(100f * DailyMissions.Progress(i) / UnityEngine.Mathf.Max(1, tasks[i].Target));
                reward.text = DailyMissions.Claimed(i) ? Strings.Get("daily.claimed") : tasks[i].Reward.ToString("N0");
                claim.EnableInClassList("ready", DailyMissions.Done(i) && !DailyMissions.Claimed(i));
                claim.EnableInClassList("claimed", DailyMissions.Claimed(i));
            }
            if (_endlessBest != null)
                _endlessBest.text = DefendSession.BestWave > 0 ? Strings.Format("events.endlessBest", DefendSession.BestWave) : "";
            RefreshOperations();
            if (_weeklyStage != null)
                _weeklyStage.text = Strings.Format("events.weeklyStage", PlayerProfile.WeeklyStage(WeeklyFortress.Week));
        }
    }
}
