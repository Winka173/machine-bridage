using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The campaign page: the nine chapters and their missions (main and side), the chosen one's
    /// briefing, and the way into a battle: a chapter's opening card the first time, then the
    /// mission's briefing card, then deploy. The Dossier opens from here.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private VisualElement _campaign, _detailArt, _detailUnlocks, _detailStars, _startMission, _detailTiers, _detailSpeaker;
        private int _tier;
        private Label _detailKicker, _detailName, _detailGoal, _detailBrief, _detailReward, _detailRules, _detailWeather, _detailPower, _detailOpponent;
        private IconElement _detailMapIcon, _detailGoalIcon, _detailWeatherIcon;
        private readonly List<(VisualElement row, int index)> _missionRows = new();
        private readonly List<(VisualElement header, int chapter)> _chapterHeaders = new();
        private ScrollView _campaignScroll;
        private int _selectedMission = -1;
        private bool _scrolledToNext;
        private StoryCard _story;

        private void BuildCampaignPage()
        {
            _campaign = TabPage(Tab.Campaign, "campaign-page opaque");
            var columns = UiKit.Box("campaign-columns");
            var left = UiKit.Box("campaign-left");
            var top = UiKit.Box("campaign-top");
            top.Add(UiKit.Text(Strings.Get("campaign.story.title").ToUpperInvariant(), "menu-caps campaign-top-title"));
            var dossier = UiKit.Button("dossier-button", OpenDossier);
            dossier.Add(UiKit.Icon("eye", UiKit.Ink, 1.8f));
            dossier.Add(UiKit.Text(Strings.Get("campaign.dossier"), "dossier-button-text"));
            top.Add(dossier);
            left.Add(top);
            _campaignScroll = Scroller("campaign-list");
            var content = _campaignScroll.contentContainer;
            var act = 0;
            var chapter = -1;
            for (var i = 0; i < Campaign.All.Count; i++)
            {
                var mission = Campaign.All[i];
                if (mission.Chapter != chapter)
                {
                    chapter = mission.Chapter;
                    var info = Campaign.Chapter(chapter);
                    if (info != null && info.Act != act)
                    {
                        act = info.Act;
                        content.Add(UiKit.Text(Strings.Get("act." + act).ToUpperInvariant(), "act-header"));
                    }
                    content.Add(ChapterHeader(chapter, info));
                }
                content.Add(MissionRow(i));
            }
            left.Add(_campaignScroll);
            columns.Add(left);

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
            var brief = UiKit.Box("detail-briefing");
            _detailSpeaker = Portraits.Element("khai", "detail-speaker");
            brief.Add(_detailSpeaker);
            _detailBrief = UiKit.Text("", "detail-brief");
            brief.Add(_detailBrief);
            detail.Add(brief);
            _detailOpponent = UiKit.Text("", "detail-opponent");
            detail.Add(_detailOpponent);
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

            _story = new StoryCard();
            Root.Add(_story.Root);
            BuildDossierPage();
        }

        private VisualElement ChapterHeader(int chapter, ChapterDef info)
        {
            var header = UiKit.Box("chapter-header");
            header.Add(UiKit.Text(chapter.ToString(), "chapter-number"));
            var text = UiKit.Box("chapter-text");
            text.Add(UiKit.Text(Strings.Get($"chapter.{chapter}.title").ToUpperInvariant(), "chapter-title"));
            var maps = new List<string>();
            if (info != null)
                foreach (var map in info.Maps) maps.Add(Strings.Get("map." + map));
            text.Add(UiKit.Text(string.Join(" · ", maps), "chapter-maps"));
            header.Add(text);
            header.Add(UiKit.Text("", "chapter-progress"));
            if (info?.General != null) header.Add(Portraits.Element(info.General, "chapter-general"));
            _chapterHeaders.Add((header, chapter));
            return header;
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
            var label = Campaign.Label(mission);
            row.Add(UiKit.Text(mission.Side ? label.Substring(label.IndexOf('-') + 1) : label, "mission-number"));
            var text = UiKit.Box("mission-text");
            text.Add(UiKit.Text(Strings.Get("mission." + mission.Id + ".name"), "mission-name"));
            var kind = mission.Operation ? Strings.Get("campaign.operation") : mission.Side ? Strings.Get("campaign.side") : null;
            var goal = Strings.Get("goal." + mission.Goal.ToString().ToLowerInvariant());
            text.Add(UiKit.Text(kind != null ? kind + " · " + goal : goal, "mission-goal-text"));
            row.Add(text);
            var stars = UiKit.Box("mission-stars");
            for (var s = 0; s < 3; s++) stars.Add(UiKit.Icon("star", UiKit.Ink, 1.8f));
            row.Add(stars);
            row.Add(UiKit.Text("", "mission-tier"));
            var lockIcon = UiKit.Icon("lock", UiKit.Ink, 1.8f);
            lockIcon.AddToClassList("mission-lock");
            row.Add(lockIcon);
            if (mission.Boss != null || mission.Goal is MissionGoal.Boss or MissionGoal.Intercept) row.AddToClassList("boss");
            if (mission.Operation) row.AddToClassList("operation");
            if (mission.Side) row.AddToClassList("side");
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
            foreach (var (header, chapter) in _chapterHeaders)
            {
                var won = 0;
                foreach (var cm in Campaign.MissionsOf(chapter, side: false))
                    if (PlayerProfile.Completed(cm.Id)) won++;
                if (header.Q<Label>(className: "chapter-progress") is { } progress) progress.text = Strings.Format("campaign.progressChapter", won);
                header.EnableInClassList("locked", !Campaign.ChapterOpen(chapter));
                header.EnableInClassList("done", Campaign.ChapterDone(chapter));
            }
            // The first time the page shows, the list starts at the mission to play next.
            if (!_scrolledToNext && _selectedMission >= 0 && _selectedMission < _missionRows.Count)
            {
                _scrolledToNext = true;
                var target = _missionRows[_selectedMission].row;
                _campaignScroll.schedule.Execute(() => _campaignScroll.ScrollTo(target)).StartingIn(60);
            }

            var m = Campaign.All[_selectedMission];
            var map = MapOf(m.Map);
            foreach (var theme in new[] { "temperate", "desert", "snow", "harbor", "volcanic", "jungle", "urban" }) _detailArt.EnableInClassList(theme, map.Theme == theme);
            _detailMapIcon.Name = map.Icon;
            _detailKicker.text = Strings.Format("campaign.missionKicker", m.Chapter, Campaign.Label(m), Strings.Get("map." + m.Map)).ToUpperInvariant();
            _detailName.text = Strings.Get("mission." + m.Id + ".name");
            _detailGoal.text = Strings.Get("goal." + m.Goal.ToString().ToLowerInvariant());
            _detailGoalIcon.Name = GoalIcon(m.Goal);
            _detailWeatherIcon.Name = WeatherIcon(m.Weather);
            _detailWeather.text = Strings.Get("menu." + m.Weather.ToLowerInvariant());
            Portraits.Set(_detailSpeaker, m.Speaker);
            _detailBrief.text = Strings.Get("mission." + m.Id + ".brief");
            _detailOpponent.text = m.General != null ? Strings.Format("campaign.opponent", Strings.Get("char." + m.General + ".name")) : "";
            _detailOpponent.style.display = m.General != null ? DisplayStyle.Flex : DisplayStyle.None;
            _detailStars.Clear();
            var won3 = PlayerProfile.Stars(m.Id);
            for (var s = 0; s < 3; s++)
            {
                var star = UiKit.Icon("star", UiKit.Ink, 1.8f);
                star.AddToClassList(s < won3 ? "star-on" : "star-off");
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
            var coins = first
                ? UnityEngine.Mathf.RoundToInt(m.RewardCoins * Rewards.TierPay(_tier))
                : UnityEngine.Mathf.RoundToInt(m.RewardCoins * (PlayerProfile.MissionTier(m.Id) < _tier ? 1f : 0.35f) * Rewards.TierPay(_tier));
            _detailReward.text = Strings.Format(first ? "campaign.rewardFirst" : "campaign.rewardReplay", coins, first ? m.Prints : m.Prints / 3);
            // Recommended power against the deck's (see Campaign.RecommendedPower).
            var deck = new List<VehicleBoost>();
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
            void Extra(string icon, string text)
            {
                var chip = UiKit.Box("unlock-chip");
                chip.Add(UiKit.Icon(icon, UiKit.Ink, 1.6f));
                chip.Add(UiKit.Text(text, "unlock-text"));
                chip.EnableInClassList("owned", !first);
                _detailUnlocks.Add(chip);
            }
            if (m.HqLevel > 0) Extra("home", Strings.Format("campaign.hqLevel", m.HqLevel));
            if (m.RarePrints > 0) Extra("star", Strings.Format("campaign.rareReward", m.RarePrints));
            if (m.TowerGear != null) Extra("shield", Strings.Format("campaign.gearReward", Strings.Get("rarity." + m.TowerGear.ToLowerInvariant())));
            var hasMap = Campaign.MapExists(m);
            var openNow = Campaign.IsOpen(_selectedMission) && hasMap;
            _startMission.EnableInClassList("disabled", !openNow);
            _startMission.Q<Label>(className: "wide-title").text = !hasMap ? Strings.Get("campaign.noMap")
                : openNow ? Strings.Get("campaign.play")
                : m.Side ? Strings.Format("campaign.sideAfter", Campaign.Label(Campaign.Get(m.After)))
                : Strings.Get("campaign.locked");
            ShowEpilogueOnce();
        }

        /// <summary>Start pressed: the chapter's opening card the first time, then the briefing, then the battle.</summary>
        private void StartMission()
        {
            if (_selectedMission < 0 || !Campaign.IsOpen(_selectedMission)) return;
            var mission = Campaign.All[_selectedMission];
            if (!Campaign.MapExists(mission)) return;
            if (mission.Chapter > 0 && !PlayerProfile.ChapterSeen(mission.Chapter))
            {
                PlayerProfile.MarkChapterSeen(mission.Chapter);
                ShowChapterCard(mission.Chapter, () => ShowBriefing(mission));
                return;
            }
            ShowBriefing(mission);
        }

        /// <summary>A chapter's opening: its act, its title, three or four sentences, its battlefields.</summary>
        private void ShowChapterCard(int chapter, System.Action then)
        {
            var info = Campaign.Chapter(chapter);
            var maps = new List<string>();
            if (info != null)
                foreach (var map in info.Maps) maps.Add(Strings.Get("map." + map));
            _story.Show(Strings.Format("campaign.chapterKicker", Strings.Get("act." + (info?.Act ?? 1)), chapter), Strings.Get($"chapter.{chapter}.title"),
                info?.General, Strings.Get($"chapter.{chapter}.summary"), maps, null,
                (Strings.Get("campaign.continue"), then), null);
        }

        /// <summary>The mission's briefing card: who gives it, what it is, who waits on the other side.</summary>
        private void ShowBriefing(MissionDef mission)
        {
            var chips = new List<string>
            {
                Strings.Get("goal." + mission.Goal.ToString().ToLowerInvariant()),
                Strings.Get("menu." + mission.Weather.ToLowerInvariant()),
                Strings.Get("map." + mission.Map),
            };
            if (mission.Operation) chips.Insert(0, Strings.Get("campaign.operation"));
            (string, string)? aside = null;
            if (mission.General != null)
            {
                var n = 1;
                foreach (var c in mission.Id) n = (n * 31 + c) % 997;
                aside = (mission.General, Strings.Get($"radio.{mission.General}.taunt.{n % 3 + 1}"));
            }
            _story.Show(Strings.Format("campaign.missionKicker", mission.Chapter, Campaign.Label(mission), Strings.Get("map." + mission.Map)),
                Strings.Get("mission." + mission.Id + ".name"), mission.Speaker, Strings.Get("mission." + mission.Id + ".brief"), chips, aside,
                (Strings.Get("campaign.deploy"), () => Deploy(mission)), (Strings.Get("campaign.back"), null));
        }

        private void Deploy(MissionDef mission)
        {
            MatchSettings.Mode = GameModeKind.Campaign;
            MatchSettings.Mission = mission.Id;
            MatchSettings.Save();
            _play();
        }

        /// <summary>Once the last operation is won: the epilogue, once.</summary>
        private void ShowEpilogueOnce()
        {
            const int epilogue = 10;
            if (_story == null || _story.Visible || _tab != Tab.Campaign || !Campaign.ChapterDone(Campaign.ChapterCount) || PlayerProfile.ChapterSeen(epilogue)) return;
            PlayerProfile.MarkChapterSeen(epilogue);
            _story.Show(Strings.Get("campaign.story.title"), Strings.Get("campaign.epilogue.title"), "khai", Strings.Get("campaign.epilogue"), null, null,
                (Strings.Get("campaign.epilogueGo"), null), null);
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
            MissionGoal.Outpost => "home",
            MissionGoal.Relieve => "shield",
            MissionGoal.Evacuate => "people",
            MissionGoal.Duel => "swords",
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
