using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.AI;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The Battle tab (the lobby): the live battle fills the screen; on the left the campaign's next
    /// mission (one tap to play it), today's challenges and the weekly fortress; in the bottom-right
    /// corner the chosen battle (mode, map, difficulty, weather; one tap to change) and DEPLOY, one
    /// tap from launch (Brawl Stars and War Robots put Play there, under the right thumb). The
    /// battle setup is its own page: every mode, map, difficulty and weather.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private static readonly (GameModeKind kind, string icon, string name, string sub)[] QuickModes =
        {
            (GameModeKind.Conquest, "flag", "mode.conquest", "mode.conquestSub"),
            (GameModeKind.Deathmatch, "swords", "mode.deathmatch", "mode.deathmatchSub"),
            (GameModeKind.KingOfTheHill, "crown", "mode.hill", "mode.hillSub"),
            (GameModeKind.Assault, "attack", "mode.assault", "mode.assaultSub"),
            (GameModeKind.Defend, "shield", "mode.defend", "mode.defendSub"),
            (GameModeKind.Siege, "home", "mode.siege", "mode.siegeSub"),
            (GameModeKind.Endless, "trophy", "mode.endless", "mode.endlessSub"),
            (GameModeKind.Survival, "people", "mode.survival", "mode.survivalSub"),
            (GameModeKind.Weekly, "home", "mode.weekly", "mode.weeklySub"),
            (GameModeKind.BossRush, "skull", "mode.bossrush", "mode.bossrushSub"),
        };

        private VisualElement _setup;
        private Label _campaignCardTitle, _campaignCardSub, _modeName, _modeMap, _modeChips, _setupInfo;
        private IconElement _modeIcon;
        private readonly List<(Label text, Label progress, VisualElement claim, Label reward)> _dailyRows = new();

        private void BuildBattlePage()
        {
            var page = TabPage(Tab.Battle, "battle-page");

            // Left column: the campaign, today's challenges, the weekly fortress.
            var left = UiKit.Box("home-left");
            var campaign = UiKit.Button("home-card campaign-card", StartNextMission);
            campaign.Add(UiKit.Icon("campaign", UiKit.Ink, 1.9f));
            var campaignText = UiKit.Box("home-card-text");
            _campaignCardTitle = UiKit.Text("", "home-card-title");
            _campaignCardSub = UiKit.Text("", "home-card-sub");
            campaignText.Add(_campaignCardTitle);
            campaignText.Add(_campaignCardSub);
            campaign.Add(campaignText);
            var go = UiKit.Box("home-card-go");
            go.Add(UiKit.Icon("play", UiKit.Ink, 2f));
            campaign.Add(go);
            left.Add(campaign);

            var daily = UiKit.Box("home-card daily-card");
            daily.Add(UiKit.Text(Strings.Get("daily.title"), "home-card-caps"));
            for (var i = 0; i < 3; i++)
            {
                var index = i;
                var row = UiKit.Box("daily-row");
                var text = UiKit.Text("", "daily-text");
                var progress = UiKit.Text("", "daily-progress");
                var claim = UiKit.Button("daily-claim", () =>
                {
                    if (DailyMissions.Claim(index))
                    {
                        Note(Strings.Get("daily.claimedNote"));
                        Refresh();
                    }
                });
                claim.Add(UiKit.Icon("coin", UiKit.Ink, 1.6f));
                var reward = UiKit.Text("", "daily-reward");
                claim.Add(reward);
                row.Add(text);
                row.Add(progress);
                row.Add(claim);
                daily.Add(row);
                _dailyRows.Add((text, progress, claim, reward));
            }
            left.Add(daily);
            page.Add(left);

            // Bottom-right: the chosen battle and Deploy.
            var right = UiKit.Box("home-right");
            var mode = UiKit.Button("home-card mode-card", () => Open(_setup, Strings.Get("setup.title")));
            _modeIcon = UiKit.Icon("flag", UiKit.Ink, 1.9f);
            mode.Add(_modeIcon);
            var modeText = UiKit.Box("home-card-text");
            _modeName = UiKit.Text("", "home-card-title");
            _modeMap = UiKit.Text("", "home-card-sub");
            _modeChips = UiKit.Text("", "home-card-chips");
            modeText.Add(_modeName);
            modeText.Add(_modeMap);
            modeText.Add(_modeChips);
            mode.Add(modeText);
            var change = UiKit.Box("home-card-go change");
            change.Add(UiKit.Icon("settings", UiKit.Ink, 1.9f));
            mode.Add(change);
            right.Add(mode);
            right.Add(DeployButton("deploy-button"));
            page.Add(right);

            _note = UiKit.Text("", "menu-toast");
            _note.style.display = DisplayStyle.None;
        }

        private VisualElement DeployButton(string classes)
        {
            var button = UiKit.Button(classes, Deploy);
            button.Add(UiKit.Icon("play", UiKit.Ink, 2.2f));
            button.Add(UiKit.Text(Strings.Get("menu.play"), "deploy-text"));
            return button;
        }

        private void Deploy()
        {
            if (MatchSettings.Mode == GameModeKind.Campaign) MatchSettings.Mode = GameModeKind.Conquest;
            MatchSettings.Save();
            _play();
        }

        private void StartNextMission()
        {
            var next = Campaign.Next;
            if (!Campaign.IsOpen(next)) return;
            MatchSettings.Mode = GameModeKind.Campaign;
            MatchSettings.Mission = Campaign.All[next].Id;
            MatchSettings.Save();
            _play();
        }

        private void RefreshBattle()
        {
            var next = Campaign.All[Campaign.Next];
            _campaignCardTitle.text = Strings.Format("home.nextMission", Campaign.Next + 1, Strings.Get("mission." + next.Id + ".name"));
            _campaignCardSub.text = Strings.Format("campaign.progress", Campaign.Won, Campaign.All.Count, PlayerProfile.TotalStars);
            var tasks = DailyMissions.Current;
            for (var i = 0; i < _dailyRows.Count && i < tasks.Count; i++)
            {
                var (text, progress, claim, reward) = _dailyRows[i];
                text.text = Strings.Format("daily." + tasks[i].Kind, tasks[i].Target);
                progress.text = $"{DailyMissions.Progress(i)}/{tasks[i].Target}";
                reward.text = DailyMissions.Claimed(i) ? Strings.Get("daily.claimed") : tasks[i].Reward.ToString("N0");
                claim.EnableInClassList("ready", DailyMissions.Done(i) && !DailyMissions.Claimed(i));
                claim.EnableInClassList("claimed", DailyMissions.Claimed(i));
            }
            foreach (var (kind, icon, name, sub) in QuickModes)
            {
                if (kind != MatchSettings.Mode) continue;
                _modeIcon.Name = icon;
                _modeName.text = Strings.Get(name);
                if (_setupInfo != null) _setupInfo.text = Strings.Get(sub);
            }
            _modeMap.text = Strings.Get("map." + MatchSettings.CurrentMap.Id);
            _modeChips.text = Strings.Get("menu." + MatchSettings.Difficulty.ToString().ToLowerInvariant()) + "  ·  " +
                              Strings.Get("menu." + MatchSettings.Weather.ToString().ToLowerInvariant());
        }

        // ------------------------------------------------------------------ battle setup

        private void BuildSetupPage()
        {
            _setup = FullPage("setup-page");
            var columns = UiKit.Box("setup-columns");
            var left = Scroller("setup-left");
            var modes = UiKit.Box("setup-modes");
            foreach (var (kind, icon, name, _) in QuickModes)
            {
                var k = kind;
                var tile = UiKit.Button("setup-mode", () => Set(() => MatchSettings.Mode = k));
                tile.Add(UiKit.Icon(icon, UiKit.Ink, 1.9f));
                tile.Add(UiKit.Text(Strings.Get(name), "setup-mode-name"));
                modes.Add(Choice(tile, () => MatchSettings.Mode == k));
            }
            left.contentContainer.Add(UiKit.Text(Strings.Get("setup.mode"), "menu-caps"));
            left.contentContainer.Add(modes);
            _setupInfo = UiKit.Text("", "mode-info");
            left.contentContainer.Add(_setupInfo);
            columns.Add(left);

            var right = Scroller("setup-right");
            var body = right.contentContainer;
            body.Add(UiKit.Text(Strings.Get("menu.map").ToUpperInvariant(), "menu-caps"));
            var maps = UiKit.Box("setup-maps");
            for (var i = 0; i < MatchSettings.AllMaps.Length; i++) maps.Add(MapCard(MatchSettings.AllMaps[i]));
            body.Add(maps);
            body.Add(UiKit.Text(Strings.Get("menu.difficulty").ToUpperInvariant(), "menu-caps"));
            var difficulty = UiKit.Box("segments");
            var levels = new[] { (AiDifficulty.Easy, "menu.easy"), (AiDifficulty.Normal, "menu.normal"), (AiDifficulty.Hard, "menu.hard") };
            for (var i = 0; i < levels.Length; i++)
            {
                var (level, key) = levels[i];
                difficulty.Add(Choice(Segment(null, Strings.Get(key), () => Set(() => MatchSettings.Difficulty = level), i == levels.Length - 1),
                    () => MatchSettings.Difficulty == level));
            }
            body.Add(difficulty);
            body.Add(UiKit.Text(Strings.Get("menu.weather").ToUpperInvariant(), "menu-caps"));
            var weather = UiKit.Box("segments grid");
            foreach (var (kind, icon, key) in new[]
                     {
                         (WeatherKind.Clear, "sun", "menu.clear"), (WeatherKind.Overcast, "cloud", "menu.overcast"),
                         (WeatherKind.Rain, "rain", "menu.rain"), (WeatherKind.Storm, "storm", "menu.storm"),
                         (WeatherKind.Snow, "snow", "menu.snow"), (WeatherKind.Sandstorm, "wind", "menu.sandstorm"),
                         (WeatherKind.Fog, "fog", "menu.fog"), (WeatherKind.Night, "moon", "menu.night"),
                         (WeatherKind.Random, "dice", "menu.random"),
                     })
                weather.Add(Choice(Segment(icon, Strings.Get(key), () => Set(() => MatchSettings.Weather = kind)),
                    () => MatchSettings.Weather == kind));
            body.Add(weather);
            columns.Add(right);
            _setup.Add(columns);
            var dock = UiKit.Box("page-dock");
            dock.Add(DeployButton("deploy-button"));
            _setup.Add(dock);
        }

        private VisualElement MapCard(MapInfo map)
        {
            var available = MatchSettings.MapAvailable(map.Id);
            var card = UiKit.Button("map-card", () =>
            {
                if (available) Set(() => MatchSettings.Map = map.Id);
                else Note(Strings.Get("map.locked"), true);
            });
            card.EnableInClassList("locked", !available);
            var art = UiKit.Box("map-art " + map.Theme);
            art.Add(UiKit.Icon(map.Icon, UiKit.Ink, 1.8f));
            card.Add(art);
            card.Add(UiKit.Text(Strings.Get("map." + map.Id), "map-name"));
            card.Add(UiKit.Text(Strings.Get("map." + map.Id + ".sub"), "map-sub"));
            return Choice(card, () => MatchSettings.CurrentMap.Id == map.Id);
        }
    }
}
