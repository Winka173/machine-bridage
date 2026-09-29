using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.AI;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// E1, the home screen: the live battle behind, dimmed 38 %. On the right the current campaign
    /// mission (the whole card is the way in, no button of its own) and today's challenges with the
    /// time to their reset; under them the chosen battle (mode, battlefield, difficulty, weather:
    /// dropdowns, E7) and the one main button, DEPLOY. Along the bottom left the deck: eight
    /// vehicles and two supports with their renders, names and cost, and "Edit deck".
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
            // Also on Operations (test feedback 2, DECISIONS 12E); it fights on the chosen map's sandbox.
            // The weekly fortress stays on Operations only: its map and stage are the week's, not the picker's.
            (GameModeKind.BossRush, "skull", "mode.bossrush", "mode.bossrushSub"),
        };

        /// <summary>A mode's one line under its name in the picker (Boss Rush says how many bosses).</summary>
        private static string ModeLine(GameModeKind kind, string key) =>
            kind == GameModeKind.BossRush ? Strings.Format(key, BossHunts.ThisWeek.Count) : Strings.Get(key);

        /// <summary>The modes the home screen's mode dropdown offers (skirmishes and challenges), for the menu's coverage test.</summary>
        internal static IEnumerable<GameModeKind> BattleModes
        {
            get
            {
                foreach (var m in QuickModes) yield return m.kind;
            }
        }

        private static readonly (AiDifficulty level, string key)[] Difficulties =
            { (AiDifficulty.Easy, "menu.easy"), (AiDifficulty.Normal, "menu.normal"), (AiDifficulty.Hard, "menu.hard"), (AiDifficulty.VeryHard, "menu.veryhard") };

        private static readonly (WeatherKind kind, string key)[] Weathers =
        {
            (WeatherKind.Random, "menu.random"), (WeatherKind.Clear, "menu.clear"), (WeatherKind.Overcast, "menu.overcast"),
            (WeatherKind.Rain, "menu.rain"), (WeatherKind.Storm, "menu.storm"), (WeatherKind.Snow, "menu.snow"),
            (WeatherKind.Sandstorm, "menu.sandstorm"), (WeatherKind.Fog, "menu.fog"), (WeatherKind.Night, "menu.night"),
        };

        private Label _homeChapter, _homeMission, _homeMissionSub, _homeChapterCount, _homeDailyReset, _homeDeckNote;
        private VisualElement _homeUnlocks, _homeDailyRows, _homeDeckStrip;
        private KitProgress _homeChapterBar;
        private KitDropdown _modeDrop, _mapDrop, _difficultyDrop, _weatherDrop;
        private readonly List<KitChip> _basePlanChips = new();
        private List<MapInfo> _homeMaps;

        private void BuildHomePage()
        {
            var page = TabPage(Tab.Home, "fc-home");

            // Right: the campaign and today's challenges (they scroll when the text is large), then the battle and Deploy.
            var right = Kit.Box("fc-home__right");
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-home__right-scroll");
            var campaign = Kit.Tappable(KitPanel.SurfaceClass + " fc-surface--field fc-campaign-card", StartNextMission);
            _homeChapter = Kit.Caption("");
            campaign.Add(_homeChapter);
            _homeMission = Kit.Text("", "fc-panel-title fc-mt-1");
            campaign.Add(_homeMission);
            _homeMissionSub = Kit.Small("");
            campaign.Add(_homeMissionSub);
            _homeUnlocks = Kit.Box("fc-campaign-card__unlocks");
            campaign.Add(_homeUnlocks);
            var progress = Kit.Box("fc-campaign-card__progress");
            _homeChapterBar = new KitProgress();
            progress.Add(_homeChapterBar);
            _homeChapterCount = Kit.Small("");
            progress.Add(_homeChapterCount);
            campaign.Add(progress);
            scroll.Add(campaign);

            var daily = KitPanel.Create(null, out var dailyBody, onBattlefield: true);
            daily.AddToClassList("fc-daily");
            var head = Kit.Box("fc-daily__head");
            head.Add(Kit.Text(Kit.Caps(Strings.Get("daily.titleShort")), "fc-panel-title fc-row-text"));
            _homeDailyReset = Kit.Small("");
            head.Add(_homeDailyReset);
            dailyBody.Add(head);
            _homeDailyRows = Kit.Box("");
            dailyBody.Add(_homeDailyRows);
            scroll.Add(daily);
            right.Add(scroll);

            var launch = Kit.Box("fc-home__launch");
            var grid = Kit.Box("fc-home__grid");
            var modes = new List<KitOption>();
            foreach (var (kind, _, name, sub) in QuickModes) modes.Add(new KitOption(Strings.Get(name), ModeLine(kind, sub)));
            _modeDrop = new KitDropdown(Strings.Get("setup.mode"), modes, 0, i => Set(() => MatchSettings.Mode = QuickModes[i].kind));
            grid.Add(_modeDrop);
            _homeMaps = new List<MapInfo>();
            var maps = new List<KitOption>();
            foreach (var map in MatchSettings.AllMaps)
            {
                if (!MatchSettings.MapAvailable(map.Id)) continue;
                _homeMaps.Add(map);
                maps.Add(new KitOption(Strings.Get("map." + map.Id), Strings.Get("map." + map.Id + ".sub"), MapArt.For(map.Id)));
            }
            _mapDrop = new KitDropdown(Strings.Get("menu.map"), maps, 0, i => Set(() => MatchSettings.Map = _homeMaps[i].Id), thumbnail: false);
            grid.Add(_mapDrop);
            var levels = new List<KitOption>();
            foreach (var (_, key) in Difficulties) levels.Add(new KitOption(Strings.Get(key)));
            _difficultyDrop = new KitDropdown(Strings.Get("menu.difficulty"), levels, 1, i => Set(() => MatchSettings.Difficulty = Difficulties[i].level));
            grid.Add(_difficultyDrop);
            var weathers = new List<KitOption>();
            foreach (var (_, key) in Weathers) weathers.Add(new KitOption(Strings.Get(key)));
            _weatherDrop = new KitDropdown(Strings.Get("menu.weather"), weathers, 0, i => Set(() => MatchSettings.Weather = Weathers[i].kind));
            grid.Add(_weatherDrop);
            launch.Add(grid);
            launch.Add(new KitButton(ButtonTier.Primary, Strings.Get("menu.play"), Deploy, "play"));
            right.Add(launch);
            page.Add(right);

            // Bottom left: the deck at a glance.
            var deck = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-home__deck", PickingMode.Position);
            var deckHead = Kit.Box("fc-home__deck-head");
            deckHead.Add(Kit.Text(Kit.Caps(Strings.Get("army.deck")), "fc-panel-title fc-row-text"));
            // Prompt 14 G4: the base set taken into the battle, switched here as on the Base screen.
            var plans = Kit.Box("fc-home__plans");
            plans.Add(Kit.Caption(Strings.Get("setup.base")));
            for (var i = 0; i < PlayerProfile.BasePlanCount; i++)
            {
                var index = i;
                var chip = new KitChip(Strings.Format("camp.plan", i + 1), i == PlayerProfile.ActiveBasePlan, () => Set(() => PlayerProfile.ActiveBasePlan = index));
                plans.Add(chip);
                _basePlanChips.Add(chip);
            }
            deckHead.Add(plans);
            deckHead.Add(new KitButton(ButtonTier.Text, Strings.Get("home.editDeck"), () =>
            {
                _armyView = ArmyView.Deck;
                ShowTab(Tab.Army);
            }));
            deck.Add(deckHead);
            _homeDeckNote = Kit.Text("", "fc-small fc-danger-text");
            deck.Add(_homeDeckNote);
            var strip = Kit.Scroll(ScrollViewMode.Horizontal, "fc-home__deck-strip");
            _homeDeckStrip = strip.contentContainer;
            deck.Add(strip);
            page.Add(deck);

            // The countdown to the challenges' reset, every second while home shows.
            page.schedule.Execute(() =>
            {
                if (_tab == Tab.Home && _overlays.Count == 0) _homeDailyReset.text = DailyResetText();
            }).Every(1000);
        }

        private static string DailyResetText()
        {
            var left = DateTime.Today.AddDays(1) - DateTime.Now;
            return Strings.Format("home.dailyReset", (int)left.TotalHours, left.Minutes);
        }

        private void Deploy()
        {
            // What the picker shows is what starts (a campaign run or the weekly fortress left behind reads as Conquest there).
            MatchSettings.Mode = QuickModes[_modeDrop.Selected].kind;
            MatchSettings.Save();
            // The picker's Boss Hunt is the week's (the full hunt starts from Operations).
            BossRushSession.Full = false;
            BossRushSession.Pending = null;
            _play();
        }

        /// <summary>The home card's next mission: the campaign's way in (the chapter card, the briefing, deploy).</summary>
        private void StartNextMission()
        {
            var next = Campaign.Next;
            if (!Campaign.IsOpen(next)) return;
            _selectedMission = next;
            _tier = 0;
            ShowTab(Tab.Campaign);
            OpenChapter(Math.Max(1, Campaign.All[next].Chapter));
            StartMission();
        }

        private void RefreshHome()
        {
            if (_homeMission == null) return;
            var next = Campaign.All[Campaign.Next];
            var chapter = Campaign.Chapter(next.Chapter);
            _homeChapter.text = Kit.Caps(next.Chapter > 0
                ? Strings.Format("campaign.chapterTitle", next.Chapter, Strings.Get($"chapter.{next.Chapter}.title"))
                : Strings.Get("campaign.story.title"));
            _homeMission.text = Kit.Caps(Strings.Format("home.nextMission", Campaign.Label(next), Strings.Get("mission." + next.Id + ".name")));
            _homeMissionSub.text = Strings.Get("map." + next.Map) + "  ·  " + Strings.Get("goal." + next.Goal.ToString().ToLowerInvariant());
            _homeUnlocks.Clear();
            foreach (var id in next.Unlocks)
            {
                if (!_catalog.Vehicles.ContainsKey(id) && !_catalog.TryGetSupport(id, out _)) continue;
                _homeUnlocks.Add(Tag(CardIcons.For(id), Strings.Format("campaign.unlocks", Strings.Card(id))));
            }
            var main = Campaign.MissionsOf(next.Chapter, side: false);
            var won = 0;
            foreach (var m in main)
                if (PlayerProfile.Completed(m.Id)) won++;
            _homeChapterBar.Value = main.Count > 0 ? won / (float)main.Count : 0f;
            _homeChapterCount.text = Strings.Format("home.chapterProgress", won, main.Count);
            _ = chapter;

            // Today's challenges: text and progress, the claim button once one is done.
            _homeDailyRows.Clear();
            var tasks = DailyMissions.Current;
            for (var i = 0; i < tasks.Count; i++) _homeDailyRows.Add(DailyRow(i, tasks[i]));
            _homeDailyReset.text = DailyResetText();

            // The battle: the mode (a campaign run left behind reads as Conquest), battlefield, difficulty, weather.
            var mode = 0;
            for (var i = 0; i < QuickModes.Length; i++)
                if (QuickModes[i].kind == MatchSettings.Mode) mode = i;
            _modeDrop.Select(mode, false);
            var map = _homeMaps.FindIndex(m => m.Id == MatchSettings.CurrentMap.Id);
            _mapDrop.Select(Math.Max(0, map), false);
            _difficultyDrop.Select(Array.FindIndex(Difficulties, d => d.level == MatchSettings.Difficulty), false);
            _weatherDrop.Select(Math.Max(0, Array.FindIndex(Weathers, w => w.kind == MatchSettings.Weather)), false);
            for (var i = 0; i < _basePlanChips.Count; i++)
            {
                _basePlanChips[i].Selected = i == PlayerProfile.ActiveBasePlan;
                _basePlanChips[i].tooltip = BasePlanLine(i);
            }

            // The deck: eight vehicles, two supports; a short deck still deploys, with a note.
            _homeDeckStrip.Clear();
            foreach (var id in MatchSettings.DeckLayout(false)) _homeDeckStrip.Add(DeckCard(id, false, compact: true));
            _homeDeckStrip.Add(Kit.Box("fc-deck-divider"));
            foreach (var id in MatchSettings.DeckLayout(true)) _homeDeckStrip.Add(DeckCard(id, true, compact: true));
            var count = MatchSettings.DeckVehicles.Count;
            _homeDeckNote.text = count < MatchSettings.DeckVehicleSlots ? Strings.Format("home.deckShort", count, MatchSettings.DeckVehicleSlots) : "";
            _homeDeckNote.style.display = count < MatchSettings.DeckVehicleSlots ? DisplayStyle.Flex : DisplayStyle.None;
        }

        private VisualElement DailyRow(int index, DailyTask task)
        {
            var row = Kit.Box("fc-daily__row");
            var text = Kit.Box("fc-daily__text");
            text.Add(Kit.Text(Strings.Format("daily." + task.Kind, task.Target), "fc-body"));
            var done = DailyMissions.Done(index);
            var claimed = DailyMissions.Claimed(index);
            if (!done) text.Add(new KitProgress(DailyMissions.Progress(index) / (float)Mathf.Max(1, task.Target)));
            row.Add(text);
            var side = Kit.Box("fc-daily__side");
            if (done && !claimed)
            {
                side.Add(new KitButton(ButtonTier.Claim, Kit.Count(task.Reward), () =>
                {
                    if (DailyMissions.Claim(index))
                    {
                        Note(Strings.Get("daily.claimedNote"));
                        Refresh();
                    }
                }));
            }
            else
            {
                side.Add(Kit.Text(claimed ? Strings.Get("daily.claimed") : $"{DailyMissions.Progress(index)}/{task.Target}", "fc-number-small"));
                if (!claimed)
                {
                    var reward = Kit.Box("fc-currency");
                    reward.Add(Kit.Icon("coin"));
                    reward.Add(Kit.Text(Kit.Count(task.Reward), "fc-small"));
                    side.Add(reward);
                }
            }
            row.Add(side);
            return row;
        }

        /// <summary>A small labelled tag: an icon and a few words (unlock cards, roles, the armour type).</summary>
        private static VisualElement Tag(string icon, string text, string extra = null)
        {
            var tag = Kit.Box("fc-tag" + (extra != null ? " " + extra : ""));
            if (icon != null) tag.Add(Kit.Icon(icon));
            tag.Add(Kit.Text(text, "fc-small"));
            return tag;
        }

        /// <summary>A deck card: the render, name, cost and level; an empty slot is a plus that opens the deck.</summary>
        private VisualElement DeckCard(string id, bool support, bool compact, bool showLevel = false, bool combat = false)
        {
            if (id == null)
            {
                var empty = Kit.Tappable("fc-vcard fc-vcard--empty" + (compact ? " fc-vcard--compact" : ""), () =>
                {
                    _armyView = ArmyView.Deck;
                    ShowTab(Tab.Army);
                });
                empty.Add(Kit.Icon("plus", "fc-vcard__plus", 2.2f));
                return empty;
            }
            var data = CardData(id);
            data.Combat = combat;
            return new KitVehicleCard(data, () => OpenDetail(id), compact, showLevel);
        }

        /// <summary>A base set in a line: its towers and modules, and how many maps it sets up on their own.</summary>
        private static string BasePlanLine(int index)
        {
            var plan = PlayerProfile.BasePlanAt(index);
            return Strings.Format("camp.planLine", plan.Places.Count, plan.Custom.Count);
        }

        /// <summary>A card's picture and numbers for the kit's vehicle card: vehicles from the catalog, supports by hand.</summary>
        private VehicleCardData CardData(string id)
        {
            if (_catalog.Vehicles.TryGetValue(id, out var def))
            {
                var data = VehicleCardData.From(def, UnlockWhere(id));
                data.Name = Strings.Card(id);
                return data;
            }
            var unlocked = PlayerProfile.IsUnlocked(id);
            return new VehicleCardData
            {
                Id = id,
                Name = Strings.Card(id),
                ShortName = Strings.Short(id),
                Branch = KitBranch.Support,
                ClassIcon = CardIcons.For(id),
                Cp = CostOf(id),
                Level = PlayerProfile.Rank(id),
                CanUpgrade = unlocked && PlayerProfile.CanRankUp(id),
                Locked = !unlocked,
                UnlockWhere = unlocked ? null : UnlockWhere(id),
                Art = CardArt.For(id),
            };
        }
    }
}
