using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>The campaign page: missions grouped by battlefield, and the chosen one's briefing.</summary>
    internal sealed partial class MenuScreen
    {
        private VisualElement _campaign, _detailArt, _detailUnlocks, _detailStars, _startMission, _detailTiers;
        private int _tier;
        private Label _detailKicker, _detailName, _detailGoal, _detailBrief, _detailReward, _detailRules, _detailWeather, _detailPower;
        private IconElement _detailMapIcon, _detailGoalIcon, _detailWeatherIcon;
        private readonly List<(VisualElement row, int index)> _missionRows = new();
        private int _selectedMission = -1;

        private void BuildCampaignPage()
        {
            _campaign = TabPage(Tab.Campaign, "campaign-page opaque");
            var columns = UiKit.Box("campaign-columns");
            var list = Scroller("campaign-list");
            var content = list.contentContainer;
            content.Add(UiKit.Text(Strings.Get("campaign.title").ToUpperInvariant(), "menu-caps"));
            string group = null;
            for (var i = 0; i < Campaign.All.Count; i++)
            {
                var mission = Campaign.All[i];
                if (mission.Map != group)
                {
                    group = mission.Map;
                    var header = UiKit.Box("map-group");
                    var info = MapOf(mission.Map);
                    header.Add(UiKit.Box("map-group-swatch " + info.Theme));
                    header.Add(UiKit.Text(Strings.Get("map." + mission.Map).ToUpperInvariant(), "map-group-name"));
                    content.Add(header);
                }
                content.Add(MissionRow(i));
            }
            columns.Add(list);

            var detail = UiKit.Box("campaign-detail");
            _detailArt = UiKit.Box("detail-art");
            _detailMapIcon = UiKit.Icon("pine", UiKit.Ink, 1.8f);
            _detailArt.Add(_detailMapIcon);
            _detailKicker = UiKit.Text("", "detail-kicker");
            _detailArt.Add(_detailKicker);
            detail.Add(_detailArt);
            _detailName = UiKit.Text("", "detail-name");
            detail.Add(_detailName);
            var goal = UiKit.Box("detail-line");
            _detailGoalIcon = UiKit.Icon("flag", UiKit.Ink, 1.7f);
            goal.Add(_detailGoalIcon);
            _detailGoal = UiKit.Text("", "detail-goal");
            goal.Add(_detailGoal);
            _detailWeatherIcon = UiKit.Icon("sun", UiKit.Ink, 1.7f);
            goal.Add(_detailWeatherIcon);
            _detailWeather = UiKit.Text("", "detail-weather");
            goal.Add(_detailWeather);
            detail.Add(goal);
            _detailBrief = UiKit.Text("", "detail-brief");
            detail.Add(_detailBrief);
            _detailStars = UiKit.Box("detail-stars");
            detail.Add(_detailStars);
            _detailRules = UiKit.Text("", "detail-rules");
            detail.Add(_detailRules);
            _detailTiers = UiKit.Box("detail-tiers");
            detail.Add(_detailTiers);
            var reward = UiKit.Box("detail-line reward-line");
            reward.Add(UiKit.Icon("coin", UiKit.Ink, 1.7f));
            _detailReward = UiKit.Text("", "detail-reward");
            _detailPower = UiKit.Text("", "detail-power");
            reward.Add(_detailReward);
            detail.Add(reward);
            detail.Add(_detailPower);
            _detailUnlocks = UiKit.Box("detail-unlocks");
            detail.Add(_detailUnlocks);
            _startMission = UiKit.WideButton("wide primary big campaign-start", "play", Strings.Get("campaign.play"), null, StartMission);
            detail.Add(_startMission);
            columns.Add(detail);
            _campaign.Add(columns);
        }

        private VisualElement MissionRow(int index)
        {
            var mission = Campaign.All[index];
            var row = UiKit.Button("mission-row", () =>
            {
                _selectedMission = index;
                _tier = 0;
                Refresh();
            });
            row.Add(UiKit.Text((index + 1).ToString("00"), "mission-number"));
            var text = UiKit.Box("mission-text");
            text.Add(UiKit.Text(Strings.Get("mission." + mission.Id + ".name"), "mission-name"));
            text.Add(UiKit.Text(Strings.Get("goal." + mission.Goal.ToString().ToLowerInvariant()), "mission-goal-text"));
            row.Add(text);
            var stars = UiKit.Box("mission-stars");
            for (var s = 0; s < 3; s++) stars.Add(UiKit.Icon("star", UiKit.Ink, 1.8f));
            row.Add(stars);
            row.Add(UiKit.Text("", "mission-tier"));
            var lockIcon = UiKit.Icon("lock", UiKit.Ink, 1.8f);
            lockIcon.AddToClassList("mission-lock");
            row.Add(lockIcon);
            if (mission.Boss != null) row.AddToClassList("boss");
            _missionRows.Add((row, index));
            return row;
        }

        private void RefreshCampaign()
        {
            if (_campaign == null) return;
            if (_selectedMission < 0) _selectedMission = Campaign.Next;
            foreach (var (row, index) in _missionRows)
            {
                var mission = Campaign.All[index];
                var open = Campaign.IsOpen(index);
                row.EnableInClassList("locked", !open);
                row.EnableInClassList("chosen", index == _selectedMission);
                var stars = PlayerProfile.Stars(mission.Id);
                var best = PlayerProfile.MissionTier(mission.Id);
                if (row.Q<Label>(className: "mission-tier") is { } tierLabel)
                {
                    tierLabel.text = best > 0 ? Strings.Get("tier." + best + ".short") : "";
                    tierLabel.EnableInClassList("iron", best == 2);
                }
                var starBox = row.Q(className: "mission-stars");
                for (var s = 0; s < starBox.childCount; s++)
                {
                    starBox[s].EnableInClassList("star-on", s < stars);
                    starBox[s].EnableInClassList("star-off", s >= stars);
                }
            }

            var m = Campaign.All[_selectedMission];
            var map = MapOf(m.Map);
            foreach (var theme in new[] { "temperate", "desert", "snow", "harbor", "volcanic", "jungle", "urban" }) _detailArt.EnableInClassList(theme, map.Theme == theme);
            _detailMapIcon.Name = map.Icon;
            _detailKicker.text = Strings.Format("campaign.detailKicker", _selectedMission + 1, Strings.Get("map." + m.Map)).ToUpperInvariant();
            _detailName.text = Strings.Get("mission." + m.Id + ".name");
            _detailGoal.text = Strings.Get("goal." + m.Goal.ToString().ToLowerInvariant());
            _detailGoalIcon.Name = GoalIcon(m.Goal);
            _detailWeatherIcon.Name = WeatherIcon(m.Weather);
            _detailWeather.text = Strings.Get("menu." + m.Weather.ToLowerInvariant());
            _detailBrief.text = Strings.Get("mission." + m.Id + ".brief");
            _detailStars.Clear();
            var won = PlayerProfile.Stars(m.Id);
            for (var s = 0; s < 3; s++)
            {
                var star = UiKit.Icon("star", UiKit.Ink, 1.8f);
                star.AddToClassList(s < won ? "star-on" : "star-off");
                _detailStars.Add(star);
            }
            var third = m.Challenge switch
            {
                "NoStrikes" => Strings.Get("challenge.nostrikes"),
                "NoAircraft" => Strings.Get("challenge.noaircraft"),
                "Kills" => Strings.Format("challenge.kills", m.ChallengeValue),
                _ => Strings.Format("challenge.losses", System.Math.Max(0, m.StarLosses)),
            };
            _detailRules.text = m.StarTime > 0f
                ? Strings.Format("campaign.stars3", $"{(int)m.StarTime / 60}:{(int)m.StarTime % 60:00}", third)
                : Strings.Format("campaign.stars3NoTime", third);
            // Tiers: Heroic opens once the mission is won, Iron once Heroic is.
            var bestTier = PlayerProfile.MissionTier(m.Id);
            if (_tier > bestTier + 1) _tier = 0;
            MatchSettings.MissionTier = _tier;
            _detailTiers.Clear();
            for (var t = 0; t < 3; t++)
            {
                var tier = t;
                var open = tier <= bestTier + 1;
                var chip = UiKit.Button("tier-chip", () =>
                {
                    if (tier > PlayerProfile.MissionTier(Campaign.All[_selectedMission].Id) + 1) return;
                    _tier = tier;
                    Refresh();
                });
                chip.Add(UiKit.Text(Strings.Get("tier." + tier), "tier-name"));
                chip.EnableInClassList("chosen", tier == _tier);
                chip.EnableInClassList("locked", !open);
                _detailTiers.Add(chip);
            }
            _detailTiers.Add(UiKit.Text(_tier == 0 ? "" : Strings.Get("tier." + _tier + ".rules"), "tier-rules"));
            var first = !PlayerProfile.Completed(m.Id);
            _detailReward.text = first
                ? Strings.Format("campaign.rewards", UnityEngine.Mathf.RoundToInt(m.RewardCoins * Rewards.TierPay(_tier)))
                : Strings.Format("campaign.replayRewards", UnityEngine.Mathf.RoundToInt(m.RewardCoins * (PlayerProfile.MissionTier(m.Id) < _tier ? 1f : 0.35f) * Rewards.TierPay(_tier)));
            // Recommended power against the deck's (see Campaign.RecommendedPower).
            var deck = new System.Collections.Generic.List<Sim.Content.VehicleBoost>();
            foreach (var id in MatchSettings.DeckVehicles)
                if (_catalog.Vehicles.TryGetValue(id, out var card)) deck.Add(PlayerProfile.BoostFor(card));
            var ours = EnemyScaling.Power(deck);
            var wanted = Campaign.RecommendedPower(m, _tier);
            _detailPower.text = Strings.Format("campaign.power", wanted, ours);
            _detailPower.EnableInClassList("power-low", ours < wanted);
            _detailUnlocks.Clear();
            foreach (var id in m.Unlocks)
            {
                if (!_catalog.Vehicles.ContainsKey(id) && !_catalog.TryGetSupport(id, out _)) continue;
                var chip = UiKit.Box("unlock-chip");
                chip.Add(UiKit.Icon(CardIcons.For(id), UiKit.Ink, 1.6f));
                chip.Add(UiKit.Text(Strings.Format("campaign.unlocks", Strings.Card(id)), "unlock-text"));
                chip.EnableInClassList("owned", PlayerProfile.IsUnlocked(id));
                _detailUnlocks.Add(chip);
            }
            var openNow = Campaign.IsOpen(_selectedMission);
            _startMission.EnableInClassList("disabled", !openNow);
            _startMission.Q<Label>(className: "wide-title").text = Strings.Get(openNow ? "campaign.play" : "campaign.locked");
        }

        private void StartMission()
        {
            if (_selectedMission < 0 || !Campaign.IsOpen(_selectedMission)) return;
            MatchSettings.Mode = GameModeKind.Campaign;
            MatchSettings.Mission = Campaign.All[_selectedMission].Id;
            MatchSettings.Run = null;
            MatchSettings.Save();
            _play();
        }

        private static MapInfo MapOf(string id)
        {
            foreach (var map in MatchSettings.AllMaps)
                if (map.Id == id) return map;
            return MatchSettings.AllMaps[0];
        }

        private static string GoalIcon(MissionGoal goal) => goal switch
        {
            MissionGoal.Capture => "flag",
            MissionGoal.Hold => "shield",
            MissionGoal.Destroy => "flame",
            MissionGoal.Escort => "apc",
            MissionGoal.Survive => "shield",
            MissionGoal.Hunt => "crosshair",
            MissionGoal.Recon => "eye",
            MissionGoal.Protect => "home",
            MissionGoal.ShootDown => "aa",
            _ => "skull",
        };

        private static string WeatherIcon(string weather) => weather switch
        {
            "Overcast" => "cloud",
            "Rain" => "rain",
            "Storm" => "storm",
            "Snow" => "snow",
            "Sandstorm" => "wind",
            "Fog" => "fog",
            "Night" => "moon",
            _ => "sun",
        };
    }
}
