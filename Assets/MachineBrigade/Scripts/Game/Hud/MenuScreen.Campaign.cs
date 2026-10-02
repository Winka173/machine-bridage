using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// E2, the campaign. First the fifteen chapters (three of them interludes) in their four acts, each with its battlefield's
    /// picture, its progress and stars, its boss and whether it is open; then a chapter's missions:
    /// the list on the left (a boss mid-chapter, the big operation and the side missions marked),
    /// the chosen one on the right with its briefing, objectives and three stars, the Normal /
    /// Heroic / Iron tiers, the recommended power against the deck's, the rewards with the cards it
    /// unlocks, and the one main button, START. The way into a battle stays: a chapter's opening
    /// card the first time, then the mission's briefing card, then deploy. The Dossier opens here. Prompt 22 D: the map of
    /// the front heads the chapters (D.1); a story choice is made here once the mission that offers it is won (D.5); the
    /// comic panels of a chapter just finished show here (D.8); a mission's page says what the story hands out (D.6), what
    /// an earlier choice changes in it and whose story it ends (D.3).
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private VisualElement _campaign, _chapterGrid, _chapterView, _missionList, _missionDetail;
        private int _campaignChapter;
        private int _tier;
        private int _selectedMission = -1;
        private StoryCard _story;
        private ScrollView _missionScroll;
        private FrontMapView _front;
        private Label _frontCaption;
        private VisualElement _frontThorne;
        private ComicPage _comic;

        private void BuildCampaignPage()
        {
            _campaign = TabPage(Tab.Campaign, "fc-page--opaque fc-campaign");

            // The chapters.
            var chapters = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            var body = Kit.Box("fc-page__body");
            var head = Kit.Box("fc-row fc-row--spread fc-mb-3");
            head.Add(Kit.Text(Strings.Get("campaign.chooseChapter"), "fc-body-2 fc-row-text"));
            head.Add(new KitButton(ButtonTier.Secondary, Strings.Get("campaign.dossier"), OpenDossier, "eye"));
            body.Add(head);
            // Prompt 22 D.1: the front.
            var front = Kit.Box("fc-front");
            _frontCaption = Kit.Caption("");
            front.Add(_frontCaption);
            _front = new FrontMapView(ChapterTapped);
            front.Add(_front);
            var legend = Kit.Box("fc-row fc-row--wrap fc-front__legend");
            legend.Add(LegendItem("fc-front__swatch--ours", "frontmap.ours"));
            legend.Add(LegendItem("fc-front__swatch--enemy", "frontmap.enemy"));
            _frontThorne = LegendItem("fc-front__swatch--thorne", "frontmap.betrayed");
            legend.Add(_frontThorne);
            legend.Add(LegendItem("fc-front__swatch--line", "frontmap.front"));
            var flagItem = Kit.Box("fc-row fc-front__legend-item");
            flagItem.Add(Kit.Icon("flag", "fc-front__legend-flag"));
            flagItem.Add(Kit.Small(Strings.Get("frontmap.flag")));
            legend.Add(flagItem);
            front.Add(legend);
            body.Add(front);
            _chapterGrid = Kit.Box("");
            body.Add(_chapterGrid);
            chapters.Add(body);
            _campaign.Add(chapters);

            // A chapter's missions.
            _chapterView = Kit.Box("fc-campaign__chapter");
            _missionScroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-campaign__list");
            _missionList = _missionScroll.contentContainer;
            _chapterView.Add(_missionScroll);
            _missionDetail = Kit.Box(KitPanel.SurfaceClass + " fc-campaign__detail", PickingMode.Position);
            _chapterView.Add(_missionDetail);
            _campaign.Add(_chapterView);

            _story = new StoryCard(Root);
            Root.Add(_story.Root);
            _comic = new ComicPage(Root);
            Root.Add(_comic.Root);
            BuildDossierPage();
        }

        private void CampaignShown()
        {
            if (_selectedMission < 0) _selectedMission = Campaign.Next;
        }

        /// <summary>Back from a chapter's missions to the chapters (true), or nothing to go back to (false).</summary>
        private bool CampaignBack()
        {
            if (_campaignChapter <= 0) return false;
            _campaignChapter = 0;
            UpdateChrome();
            Refresh();
            return true;
        }

        private void OpenChapter(int chapter)
        {
            _campaignChapter = chapter;
            if (_selectedMission < 0 || Campaign.All[_selectedMission].Chapter != chapter)
            {
                _selectedMission = -1;
                var list = Campaign.MissionsOf(chapter);
                foreach (var m in list)
                {
                    var index = Campaign.IndexOf(m.Id);
                    if (!m.Side && Campaign.IsOpen(index) && !PlayerProfile.Completed(m.Id))
                    {
                        _selectedMission = index;
                        break;
                    }
                }
                if (_selectedMission < 0 && list.Count > 0) _selectedMission = Campaign.IndexOf(list[0].Id);
            }
            UpdateChrome();
            Refresh();
            // Start the list at the chosen mission.
            _missionScroll.schedule.Execute(() =>
            {
                var chosen = _missionList.Q(className: "fc-mission--chosen");
                if (chosen != null) _missionScroll.ScrollTo(chosen);
            }).StartingIn(60);
        }

        private void RefreshCampaign()
        {
            if (_campaign == null) return;
            if (_selectedMission < 0) _selectedMission = Campaign.Next;
            var inChapter = _campaignChapter > 0;
            _chapterView.style.display = inChapter ? DisplayStyle.Flex : DisplayStyle.None;
            _campaign.Q<ScrollView>(className: "fc-page__scroll").style.display = inChapter ? DisplayStyle.None : DisplayStyle.Flex;
            if (_tab != Tab.Campaign) return;
            if (inChapter)
            {
                FillMissionList();
                FillMissionDetail();
            }
            else FillChapters();
            ShowStoryMomentsOnce();
        }

        /// <summary>
        /// Prompt 22 D: what the story shows on the campaign page, one thing at a time: the comic panels of the chapter just
        /// finished, a story choice to make, then the epilogue or "To be continued".
        /// </summary>
        private void ShowStoryMomentsOnce()
        {
            if (_story == null || _story.Visible || _comic.Visible || _tab != Tab.Campaign) return;
            var comic = Narrative.ComicPending;
            if (comic > 0)
            {
                // A save that finished several chapters before the panels came sees the latest; the dossier has the others.
                foreach (var c in Campaign.Chapters)
                {
                    if (Campaign.ChapterDone(c.Number)) PlayerProfile.MarkChapterSeen(PlayerProfile.ComicSeen(c.Number));
                    if (c.Number == comic) break;
                }
                _comic.Show(comic, () => Root.schedule.Execute(ShowStoryMomentsOnce).StartingIn(30));
                return;
            }
            if (Narrative.Pending is { } choice)
            {
                ShowChoice(choice);
                return;
            }
            ShowEpilogueOnce();
        }

        private static VisualElement LegendItem(string swatch, string key)
        {
            var item = Kit.Box("fc-row fc-front__legend-item");
            item.Add(Kit.Box("fc-front__swatch " + swatch));
            item.Add(Kit.Small(Strings.Get(key)));
            return item;
        }

        /// <summary>A chapter's card or its pin on the map: open it, or say why not.</summary>
        private void ChapterTapped(int number)
        {
            if (Campaign.ChapterEnabled(number) && Campaign.ChapterOpen(number)) OpenChapter(number);
            else if (!Campaign.ChapterEnabled(number)) Note(Strings.Get("campaign.comingSoonNote"), true);
            else Note(Strings.Format("campaign.chapterLocked", ("chapter", Campaign.ChapterName(Campaign.PreviousChapter(number)))), true);
        }

        // ------------------------------------------------------------------ D.5 the story's choices

        /// <summary>A choice's two options on the story card: who asks, what is at stake, what each leads to.</summary>
        private void ShowChoice(string choice)
        {
            var offer = Narrative.OfferOf(choice);
            var options = Campaign.OptionsOf(choice);
            if (offer == null || options.Count < 2) return;
            string OptionLabel(MissionDef m) => Strings.Get($"storychoice.{choice}.{m.Option}");
            string OptionInfo(MissionDef m) => Strings.Format($"storychoice.{choice}.{m.Option}.info", ("cp", Narrative.MinersCp), ("share", (int)System.Math.Round((1f - Narrative.RadarVision) * 100f)));
            var body = Strings.Get($"storychoice.{choice}.body") + "\n\n" + OptionLabel(options[0]) + ": " + OptionInfo(options[0]) + "\n" + OptionLabel(options[1]) + ": " + OptionInfo(options[1]);
            _story.Show(Strings.Format("campaign.choiceKicker", ("chapter", Campaign.ChapterName(offer.Chapter))), Strings.Get($"storychoice.{choice}.title"),
                Narrative.SpeakerOf(choice), body, null, null,
                (OptionLabel(options[0]), () => MakeChoice(choice, options[0])), (OptionLabel(options[1]), () => MakeChoice(choice, options[1])), options[0].Map, "arrow");
        }

        private void MakeChoice(string choice, MissionDef option)
        {
            Narrative.Choose(choice, option.Option);
            _selectedMission = Campaign.IndexOf(option.Id);
            _tier = 0;
            if (_campaignChapter > 0) _campaignChapter = option.Chapter;
            UpdateChrome();
            Refresh();
        }

        // ------------------------------------------------------------------ the chapters

        private void FillChapters()
        {
            // Prompt 22 D.1: the front, as the save has it.
            _front.Refresh();
            int won = 0, total = 0;
            foreach (var s in _front.Sectors)
            {
                total++;
                if (PlayerProfile.Completed(s.Mission.Id)) won++;
            }
            _frontCaption.text = Kit.Caps(Strings.Format("frontmap.caption", ("won", won), ("total", total)));
            _frontThorne.style.display = FrontMap.Betrayed ? DisplayStyle.Flex : DisplayStyle.None;
            _chapterGrid.Clear();
            var act = 0;
            VisualElement row = null;
            // Prompt 20 C: a chapter switched off shows as "Coming soon" or not at all (release.json).
            foreach (var chapter in Campaign.ShownChapters)
            {
                if (chapter.Act != act)
                {
                    act = chapter.Act;
                    _chapterGrid.Add(Kit.Text(Kit.Caps(Strings.Get("act." + act)), "fc-caption fc-campaign__act"));
                    row = Kit.Box("fc-campaign__chapters");
                    _chapterGrid.Add(row);
                }
                row?.Add(ChapterCard(chapter));
            }
        }

        private VisualElement ChapterCard(ChapterDef chapter)
        {
            var number = chapter.Number;
            var soon = !Campaign.ChapterEnabled(number);
            var open = !soon && Campaign.ChapterOpen(number);
            var card = Kit.Tappable("fc-chapter" + (open ? "" : " fc-chapter--locked"), () => ChapterTapped(number));
            var art = Kit.Box("fc-chapter__art");
            if (chapter.Maps.Count > 0 && MapArt.For(chapter.Maps[0]) is { } picture) art.style.backgroundImage = Background.FromTexture2D(picture);
            art.Add(Kit.Text(chapter.Short, "fc-number fc-chapter__number"));
            if (!open)
            {
                var lockBox = Kit.Box("fc-chapter__lock");
                lockBox.Add(Kit.Icon("lock"));
                art.Add(lockBox);
            }
            card.Add(art);
            var text = Kit.Box("fc-chapter__body");
            text.Add(Kit.Text(Kit.Caps(Strings.Get($"chapter.{number}.title")), "fc-panel-title"));
            if (soon)
            {
                text.Add(Kit.Text(Strings.Get("campaign.comingSoon"), "fc-small"));
                card.Add(text);
                return card;
            }
            var main = Campaign.MissionsOf(number, side: false);
            int won = 0, stars = 0, playable = 0;
            foreach (var m in Campaign.MissionsOf(number))
            {
                // Prompt 22 D.5: of a choice's two missions, the one taken (or the first while it is to be made).
                if (!Campaign.OnPath(m)) continue;
                playable++;
                if (!m.Side && PlayerProfile.Completed(m.Id)) won++;
                stars += PlayerProfile.Stars(m.Id);
            }
            var progress = Kit.Box("fc-row fc-mt-2");
            var bar = new KitProgress(main.Count > 0 ? won / (float)main.Count : 0f);
            bar.AddToClassList("fc-grow");
            progress.Add(bar);
            text.Add(progress);
            var facts = Kit.Box("fc-row fc-row--wrap fc-mt-2");
            facts.Add(Tag("flag", Strings.Format("home.chapterProgress", ("count", won), ("total", main.Count))));
            facts.Add(Tag("star", Strings.Format("campaign.starCount", ("count", stars), ("total", playable * 3))));
            if (ChapterBoss(number) is { } boss) facts.Add(Tag("skull", Strings.Get("boss." + boss)));
            // Prompt 20 O.1: its mini bosses (campaign.json "minis").
            if (chapter.Minis.Count > 0) facts.Add(Tag("elite", Strings.Format("campaign.minis", chapter.Minis.Count)));
            text.Add(facts);
            if (!open) text.Add(Kit.Text(Strings.Format("campaign.chapterLocked", ("chapter", Campaign.ChapterName(Campaign.PreviousChapter(number)))), "fc-small"));
            card.Add(text);
            return card;
        }

        /// <summary>A chapter's boss (the dossier's key): its main boss (prompt 20), else the last boss its missions name, or null.</summary>
        private static string ChapterBoss(int chapter)
        {
            if (Campaign.Chapter(chapter)?.Main is { } main && Strings.Has("boss." + main)) return main;
            string found = null;
            foreach (var m in Campaign.MissionsOf(chapter, side: false))
            {
                var boss = m.Boss;
                if (boss == null)
                    foreach (var stage in m.Stages)
                        if (stage.Mission.Boss != null)
                            boss = stage.Mission.Boss;
                if (boss == null) continue;
                var key = boss.Name ?? boss.Def;
                if (Strings.Has("boss." + key)) found = key;
            }
            return found;
        }

        // ------------------------------------------------------------------ a chapter's missions

        private void FillMissionList()
        {
            _missionList.Clear();
            var sideHeader = false;
            foreach (var mission in Campaign.MissionsOf(_campaignChapter))
            {
                if (mission.Side && !sideHeader)
                {
                    sideHeader = true;
                    _missionList.Add(Kit.Text(Kit.Caps(Strings.Get("campaign.sideMissions")), "fc-caption fc-campaign__act"));
                }
                _missionList.Add(MissionRow(Campaign.IndexOf(mission.Id)));
            }
        }

        private VisualElement MissionRow(int index)
        {
            var mission = Campaign.All[index];
            var open = Campaign.IsOpen(index);
            var row = Kit.Tappable("fc-mission", () =>
            {
                _selectedMission = index;
                _tier = 0;
                Refresh();
            });
            row.EnableInClassList("fc-mission--chosen", index == _selectedMission);
            row.EnableInClassList("fc-mission--locked", !open);
            var notTaken = Campaign.NotTaken(mission);
            var label = Campaign.Label(mission);
            row.Add(Kit.Text(mission.Side ? label.Substring(label.IndexOf('-') + 1) : label, "fc-number-small fc-mission__number"));
            var text = Kit.Box("fc-mission__text");
            text.Add(Kit.Text(Strings.Get("mission." + mission.Id + ".name"), "fc-body"));
            var marks = Kit.Box("fc-row fc-row--wrap");
            if (IsBossMission(mission)) marks.Add(Tag("skull", Strings.Get("campaign.boss"), "fc-tag--boss"));
            if (mission.Operation) marks.Add(Tag("flag", Strings.Get("campaign.operation"), "fc-tag--operation"));
            if (mission.Side) marks.Add(Tag(null, Strings.Get("campaign.side")));
            // Prompt 22 D.5: a story choice's option, and the one not taken.
            if (mission.Branch != null) marks.Add(Tag("arrow", Strings.Get(notTaken ? "campaign.notTaken" : "campaign.choiceTag")));
            if (!notTaken) marks.Add(Tag(GoalIcon(mission.Goal), Strings.Get("goal." + mission.Goal.ToString().ToLowerInvariant())));
            text.Add(marks);
            row.Add(text);
            var side = Kit.Box("fc-mission__side");
            if (!open) side.Add(Kit.Icon("lock", "fc-mission__lock"));
            else
            {
                var stars = Kit.Box("fc-stars");
                var won = PlayerProfile.Stars(mission.Id);
                for (var s = 0; s < 3; s++) stars.Add(Kit.Icon("star", s < won ? "fc-star fc-star--on" : "fc-star"));
                side.Add(stars);
                var best = PlayerProfile.MissionTier(mission.Id);
                if (best > 0) side.Add(Kit.Text(Strings.Get("tier." + best + ".short"), "fc-small"));
            }
            row.Add(side);
            return row;
        }

        /// <summary>The bosses a mission fights (its own, then its stages'), each once: the ones with a page.</summary>
        private List<string> MissionBosses(MissionDef m)
        {
            var ids = new List<string>();
            void Add(string id)
            {
                if (id != null && !ids.Contains(id) && _catalog.Vehicles.TryGetValue(id, out var def) && def.Boss) ids.Add(id);
            }
            Add(m.Boss?.Def);
            foreach (var stage in m.Stages) Add(stage.Mission.Boss?.Def);
            return ids;
        }

        private static bool IsBossMission(MissionDef m) => m.Boss != null || m.Goal is MissionGoal.Boss or MissionGoal.Intercept;

        private void FillMissionDetail()
        {
            _missionDetail.Clear();
            if (_selectedMission < 0) return;
            var m = Campaign.All[_selectedMission];
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-campaign__detail-scroll");
            var body = Kit.Box("fc-campaign__detail-body");

            // The battlefield, the name, the objective and the weather.
            var art = Kit.Box("fc-campaign__art");
            if (MapArt.For(m.Map) is { } picture) art.style.backgroundImage = Background.FromTexture2D(picture);
            body.Add(art);
            body.Add(Kit.Caption(Strings.Format("campaign.missionKicker", ("chapter", Campaign.ChapterName(m.Chapter)), ("mission", Campaign.Label(m)), ("map", Strings.Get("map." + m.Map)))));
            body.Add(Kit.Text(Kit.Caps(Strings.Get("mission." + m.Id + ".name")), "fc-title"));
            var tags = Kit.Box("fc-row fc-row--wrap fc-mt-2");
            tags.Add(Tag(GoalIcon(m.Goal), Strings.Get("goal." + m.Goal.ToString().ToLowerInvariant())));
            tags.Add(Tag(WeatherIcon(m.Weather), Strings.Get("menu." + m.Weather.ToLowerInvariant())));
            if (IsBossMission(m)) tags.Add(Tag("skull", Strings.Get("campaign.boss"), "fc-tag--boss"));
            if (m.Operation) tags.Add(Tag("flag", Strings.Get("campaign.operation"), "fc-tag--operation"));
            if (m.Branch != null) tags.Add(Tag("arrow", Strings.Get(Campaign.NotTaken(m) ? "campaign.notTaken" : "campaign.choiceTag")));
            // Prompt 22 D.3: whose story this mission ends.
            foreach (var beat in Narrative.PayoffsAt(m.Id)) tags.Add(Tag("star", Strings.Get($"arc.{beat.Who}.title")));
            body.Add(tags);
            // Prompt 22 D.5: what an earlier choice changes here.
            foreach (var (key, args) in Narrative.Effects(m)) body.Add(Kit.Text(Strings.Format(key, args), "fc-body-2 fc-mt-2"));

            // The briefing: who gives it, what it says, who waits on the other side.
            var brief = Kit.Box("fc-briefing");
            brief.Add(Portraits.Element(m.Speaker, "fc-portrait"));
            var briefText = Kit.Box("fc-briefing__text");
            briefText.Add(Kit.Text(Kit.Caps(Strings.Get("char." + (m.Speaker ?? "hq") + ".name")), "fc-caption"));
            briefText.Add(Kit.Text(Strings.Get("mission." + m.Id + ".brief"), "fc-body"));
            if (m.General != null) briefText.Add(Kit.Text(Strings.Format("campaign.opponent", Strings.Get("char." + m.General + ".name")), "fc-small fc-mt-2"));
            // Prompt 22 F.4: the enemy general's strength and weakness.
            if (GeneralLines(m) is { } general) briefText.Add(Kit.Text(general, "fc-small fc-row-text"));
            // Prompt 28 H.7: the general's favourite tactic.
            if (GeneralTacticLine(m) is { } favourite) briefText.Add(Kit.Text(favourite, "fc-small fc-row-text"));
            brief.Add(briefText);
            body.Add(brief);
            // Prompt 22 F.1: the player's commander for it (the mission's own when the story sets one).
            body.Add(CommanderSlot(m));
            // Prompt 28 H.4: the tactic the mission starts with.
            body.Add(TacticSlot(m));
            // Play-test 6 (DECISIONS 21B): each boss it fights, a link to its file.
            foreach (var boss in MissionBosses(m))
                body.Add(new KitButton(ButtonTier.Text, Strings.Format("guide.boss.file", Strings.Card(boss)), () => OpenBossGuide(boss), "skull"));

            // Three stars.
            body.Add(Kit.Text(Kit.Caps(Strings.Get("campaign.starsTitle")), "fc-panel-title fc-section__title fc-mt-4"));
            var won = PlayerProfile.Stars(m.Id);
            var third = m.Challenge switch
            {
                "NoStrikes" => Strings.Get("challenge.nostrikes"),
                "NoAircraft" => Strings.Get("challenge.noaircraft"),
                "Kills" => Strings.Format("challenge.kills", m.ChallengeValue),
                _ => Strings.Format("challenge.losses", System.Math.Max(0, m.StarLosses)),
            };
            var goals = new List<string> { Strings.Get("campaign.starWin") };
            if (m.StarTime > 0f) goals.Add(Strings.Format("campaign.starTime", $"{(int)m.StarTime / 60}:{(int)m.StarTime % 60:00}"));
            goals.Add(third);
            for (var s = 0; s < goals.Count; s++)
            {
                var line = Kit.Box("fc-row fc-mb-2");
                line.Add(Kit.Icon("star", s < won ? "fc-star fc-star--on" : "fc-star"));
                var text = Kit.Text(goals[s], "fc-body fc-row-text fc-ml-2");
                line.Add(text);
                body.Add(line);
            }

            // Tiers: Hard (once Heroic) opens once the mission is won, Very hard (once Iron) once Hard is.
            var bestTier = PlayerProfile.MissionTier(m.Id);
            if (_tier > bestTier + 1) _tier = 0;
            MatchSettings.MissionTier = _tier;
            body.Add(Kit.Text(Kit.Caps(Strings.Get("campaign.tierTitle")), "fc-panel-title fc-section__title fc-mt-4"));
            var tiers = new List<VisualElement>();
            for (var t = 0; t < 3; t++)
            {
                var tier = t;
                var open = tier <= bestTier + 1;
                var chip = new KitChip(Strings.Get("tier." + tier), tier == _tier, () =>
                {
                    if (tier > PlayerProfile.MissionTier(Campaign.All[_selectedMission].Id) + 1)
                    {
                        Note(Strings.Get(tier == 1 ? "campaign.heroicLocked" : "campaign.ironLocked"), true);
                        return;
                    }
                    _tier = tier;
                    Refresh();
                }, open ? null : "lock");
                tiers.Add(chip);
            }
            body.Add(new KitChipRow(tiers));
            if (_tier > 0) body.Add(Kit.Text(Strings.Get("tier." + _tier + ".rules"), "fc-small"));

            // The recommended power (Campaign.RecommendedPower) against the deck's.
            var deck = new List<VehicleBoost>();
            foreach (var id in MatchSettings.DeckVehicles)
                if (_catalog.Vehicles.TryGetValue(id, out var card)) deck.Add(PlayerProfile.BoostFor(card));
            var ours = EnemyScaling.Power(deck);
            var wanted = Campaign.RecommendedPower(m, _tier);
            var power = Kit.Box("fc-row fc-mt-4");
            power.Add(Kit.Text(Strings.Format("campaign.power", ("wanted", wanted), ("ours", ours)), "fc-body fc-row-text" + (ours < wanted ? " fc-danger-text" : "")));
            body.Add(power);

            // Rewards, with the cards it unlocks as cards.
            body.Add(Kit.Text(Kit.Caps(Strings.Get("campaign.rewardsTitle")), "fc-panel-title fc-section__title fc-mt-4"));
            var first = !PlayerProfile.Completed(m.Id);
            var coins = first
                ? Mathf.RoundToInt(m.RewardCoins * Rewards.TierPay(_tier))
                : Mathf.RoundToInt(m.RewardCoins * (PlayerProfile.MissionTier(m.Id) < _tier ? 1f : 0.35f) * Rewards.TierPay(_tier));
            var pay = Kit.Box("fc-row fc-row--wrap");
            pay.Add(Tag("coin", Strings.Format("campaign.rewardCoins", Kit.Count(coins))));
            pay.Add(Tag("blueprint", Strings.Format("campaign.rewardPrints", first ? m.Prints : m.Prints / 3)));
            if (m.HqLevel > 0) pay.Add(Tag("home", Strings.Format("campaign.hqLevel", m.HqLevel)));
            if (m.RarePrints > 0) pay.Add(Tag("star", Strings.Format("campaign.rareReward", m.RarePrints)));
            if (m.TowerGear != null) pay.Add(Tag("shield", Strings.Format("campaign.gearReward", Strings.Get("rarity." + m.TowerGear.ToLowerInvariant()))));
            body.Add(pay);
            var unlocks = Kit.Box("fc-row fc-row--wrap fc-row--top fc-mt-2");
            foreach (var id in m.Unlocks)
            {
                if (!_catalog.Vehicles.ContainsKey(id) && !_catalog.TryGetSupport(id, out _)) continue;
                var data = CardData(id);
                data.Locked = false;
                unlocks.Add(new KitVehicleCard(data, () => OpenDetail(id), compact: true));
            }
            if (unlocks.childCount > 0) body.Add(unlocks);
            // Prompt 22 D.6: why the story hands these cards out.
            foreach (var id in m.Unlocks)
                if (Narrative.LootReason(id) is { } reason)
                {
                    var line = Kit.Box("fc-row fc-row--top fc-mt-2");
                    line.Add(Tag("star", Strings.Get("campaign.storyLoot")));
                    line.Add(Kit.Text(Strings.Get(reason), "fc-body-2 fc-row-text fc-ml-2"));
                    body.Add(line);
                }
            scroll.Add(body);
            _missionDetail.Add(scroll);

            // START, pinned under the scrolling text; a story choice still to make is made here first (prompt 22 D.5).
            var hasMap = Campaign.MapExists(m);
            var openNow = Campaign.IsOpen(_selectedMission) && hasMap;
            var pending = Campaign.ChoicePending(m);
            var start = pending != null
                ? new KitButton(ButtonTier.Primary, Strings.Get("campaign.choose"), () => ShowChoice(pending), "arrow")
                : new KitButton(ButtonTier.Primary, Strings.Get("campaign.play"), StartMission, "play");
            start.AddToClassList("fc-campaign__start");
            if (pending == null && !openNow)
                start.Disable(!hasMap ? Strings.Get("campaign.noMap")
                    : Campaign.NotTaken(m) ? Strings.Get("campaign.notTakenNote")
                    : m.Side ? Strings.Format("campaign.sideAfter", Campaign.Label(Campaign.Get(m.After)))
                    : Strings.Get("campaign.locked"));
            _missionDetail.Add(start);
        }

        /// <summary>Start pressed: the chapter's opening card the first time, then the briefing, then the battle.</summary>
        private void StartMission()
        {
            if (_selectedMission < 0) return;
            if (Campaign.ChoicePending(Campaign.All[_selectedMission]) is { } choice)
            {
                ShowChoice(choice);
                return;
            }
            if (!Campaign.IsOpen(_selectedMission)) return;
            var mission = Campaign.All[_selectedMission];
            if (!Campaign.MapExists(mission)) return;
            if (mission.Chapter > 0 && !PlayerProfile.ChapterSeen(mission.Chapter))
            {
                // Prompt 22 C.3: the flash-forward to Helion before the story's first chapter card, once.
                var first = Campaign.All.Count > 0 && Campaign.All[0].Chapter == mission.Chapter;
                PlayerProfile.MarkChapterSeen(mission.Chapter);
                if (first && !PlayerProfile.ChapterSeen(PlayerProfile.PrologueSeen))
                {
                    PlayerProfile.MarkChapterSeen(PlayerProfile.PrologueSeen);
                    ShowFlashForward(() => ShowChapterCard(mission.Chapter, () => ShowBriefing(mission)));
                    return;
                }
                ShowChapterCard(mission.Chapter, () => ShowBriefing(mission));
                return;
            }
            ShowBriefing(mission);
        }

        /// <summary>Prompt 22 C.3: a few seconds of the end (the sky over Helion, a tungsten rod falling, Aurel's voice), then back three years.</summary>
        private void ShowFlashForward(System.Action then)
        {
            _story.Show(Strings.Get("campaign.flash.kicker"), Strings.Get("campaign.flash.title"), "aurel", Strings.Get("campaign.flash"),
                null, null, (Strings.Get("campaign.continue"), then), null, "launchsite");
        }

        /// <summary>A chapter's opening: its act, its title, three or four sentences, its battlefields.</summary>
        private void ShowChapterCard(int chapter, System.Action then)
        {
            var info = Campaign.Chapter(chapter);
            var maps = new List<string>();
            if (info != null)
                foreach (var map in info.Maps) maps.Add(Strings.Get("map." + map));
            _story.Show(Strings.Format("campaign.chapterKicker", ("act", Strings.Get("act." + (info?.Act ?? 1))), ("chapter", Campaign.ChapterName(chapter))), Strings.Get($"chapter.{chapter}.title"),
                info?.General, Strings.Get($"chapter.{chapter}.summary"), maps, null,
                (Strings.Get("campaign.continue"), then), null, info != null && info.Maps.Count > 0 ? info.Maps[0] : null);
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
            // Prompt 22 F: who leads the player's side.
            chips.Add(Strings.Format("cmdr.yours", ("name", CommanderText.Call(CommanderPick.ForBattle(mission)))));
            (string, string)? aside = null;
            if (mission.General != null)
            {
                var n = 1;
                foreach (var c in mission.Id) n = (n * 31 + c) % 997;
                var taunt = Strings.Get($"radio.{mission.General}.taunt.{n % 3 + 1}");
                // Prompt 22 F.4: the enemy general's strength and weakness under their line.
                aside = (mission.General, GeneralLines(mission) is { } lines ? taunt + "\n" + lines : taunt);
            }
            _story.Show(Strings.Format("campaign.missionKicker", ("chapter", Campaign.ChapterName(mission.Chapter)), ("mission", Campaign.Label(mission)), ("map", Strings.Get("map." + mission.Map))),
                Strings.Get("mission." + mission.Id + ".name"), mission.Speaker, Strings.Get("mission." + mission.Id + ".brief"), chips, aside,
                (Strings.Get("campaign.deploy"), () => Deploy(mission)), (Strings.Get("campaign.back"), null), mission.Map);
        }

        private void Deploy(MissionDef mission)
        {
            MatchSettings.Mode = GameModeKind.Campaign;
            MatchSettings.Mission = mission.Id;
            MatchSettings.Run = null;
            MatchSettings.Save();
            _play();
        }

        /// <summary>
        /// Once the last operation switched on is won: the game's epilogue, once, or "To be continued"
        /// when the build ends before the story does (prompt 20 C.3; after the act's interlude, prompt 22).
        /// </summary>
        private void ShowEpilogueOnce()
        {
            var last = Campaign.FinalChapter;
            var complete = Campaign.StoryComplete;
            var mark = complete ? PlayerProfile.EpilogueSeen : PlayerProfile.ContinuedSeen(last);
            if (_story == null || _story.Visible || _tab != Tab.Campaign || last <= 0 || !Campaign.ChapterDone(last) || PlayerProfile.ChapterSeen(mark)) return;
            PlayerProfile.MarkChapterSeen(mark);
            _story.Show(Strings.Get("campaign.story.title"), Strings.Get(complete ? "campaign.epilogue.title" : "campaign.tbc.title"), "khai",
                Strings.Get(complete ? "campaign.epilogue" : "campaign.tbc"), null, null, (Strings.Get("campaign.epilogueGo"), null), null, null);
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
