using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The Dossier ("Hồ sơ"): the people of the story (their bios once met), the boss files (once the
    /// boss is beaten), the timeline (a line for each chapter finished) and the story files every
    /// won mission adds. Device checks: -mb-dossier (-mb-dossier-tab=bosses, -mb-dossier-all shows
    /// everything), -mb-chapter=3 (a chapter's opening card), -mb-brief=c3m05 (a briefing card),
    /// -mb-campaign (the campaign page; -mb-campaign=c5m10 with that mission chosen).
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private enum DossierTab
        {
            People,
            Bosses,
            Timeline,
            Files,

            /// <summary>Prompt 20 O.5 (DECISIONS 19L): every battlefield, its picture and its guide.</summary>
            Maps,

            /// <summary>Prompt 22 F.4: a page for each of the player's commanders and each enemy general.</summary>
            Commanders,
        }

        private VisualElement _dossier, _dossierBody;
        private KitTabs _dossierTabs;
        private DossierTab _dossierTab;
        private bool _dossierAll;

        private void BuildDossierPage()
        {
            _dossier = FullPage("fc-dossier");
            _dossierTabs = new KitTabs(new[] { Strings.Get("dossier.people"), Strings.Get("dossier.bosses"), Strings.Get("dossier.timeline"), Strings.Get("dossier.files"), Strings.Get("dossier.maps"),
                    Strings.Get("cmdr.dossier.tab") },
                0, i =>
                {
                    _dossierTab = (DossierTab)i;
                    FillDossier();
                });
            _dossier.Add(_dossierTabs);
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-page__scroll");
            _dossierBody = Kit.Box("fc-page__body");
            scroll.Add(_dossierBody);
            _dossier.Add(scroll);
            _dossierAll = DebugFlags.Has("-mb-dossier-all");
            Root.schedule.Execute(DebugStory).StartingIn(300);
            BuildCommanderPage();
        }

        private void OpenDossier()
        {
            Open(_dossier, Strings.Get("campaign.dossier"));
            FillDossier();
        }

        private void FillDossier()
        {
            _dossierTabs.Select((int)_dossierTab, false);
            _dossierBody.Clear();
            switch (_dossierTab)
            {
                case DossierTab.People:
                    foreach (var id in CampaignText.Speakers)
                    {
                        if (id == "hq") continue;
                        var met = _dossierAll || Met(id);
                        _dossierBody.Add(Entry(id, Strings.Get($"char.{id}.name"), Strings.Get($"char.{id}.role"),
                            met ? Strings.Get($"char.{id}.bio") : Strings.Get("dossier.locked"), !met, IsEnemy(id)));
                    }
                    break;
                case DossierTab.Bosses:
                    foreach (var (key, beaten) in BossFiles())
                    {
                        var open = _dossierAll || beaten;
                        // Prompt 20 O.3: its rank and general under the name; once open, links to its Guide page and to the boss it is a variant of.
                        var def = _catalog.Vehicles.TryGetValue(key, out var d) && d.Boss ? d : null;
                        var entry = Entry(null, Strings.Get("boss." + key), def != null ? BossLine(def) : null,
                            open ? Strings.Get("bossfile." + key) : Strings.Get("dossier.lockedBoss"), !open, true);
                        if (open && def != null) entry.Q(className: "fc-dossier__text")?.Add(BossLinks(def));
                        _dossierBody.Add(entry);
                    }
                    break;
                case DossierTab.Timeline:
                    _dossierBody.Add(Entry(null, Strings.Get("dossier.before"), null, Strings.Get("timeline.0"), false, false));
                    for (var c = 1; c <= Campaign.LastChapter; c++)
                    {
                        if (!Campaign.ChapterEnabled(c)) continue;
                        var done = _dossierAll || Campaign.ChapterDone(c);
                        _dossierBody.Add(Entry(null, Strings.Format("dossier.chapterFiles", c) + " · " + Strings.Get($"chapter.{c}.title"), null,
                            done ? Strings.Get($"timeline.{c}") : Strings.Get("dossier.lockedChapter"), !done, false));
                    }
                    // The game's epilogue, or "To be continued" when the build ends before the story does.
                    if (_dossierAll || Campaign.ChapterDone(Campaign.LastChapter))
                        _dossierBody.Add(Campaign.StoryComplete
                            ? Entry(null, Strings.Get("campaign.epilogue.title"), null, Strings.Get("campaign.epilogue"), false, false)
                            : Entry(null, Strings.Get("campaign.tbc.title"), null, Strings.Get("campaign.tbc"), false, false));
                    break;
                case DossierTab.Files:
                    var any = false;
                    var chapter = 0;
                    foreach (var m in Campaign.All)
                    {
                        if (!_dossierAll && !PlayerProfile.Completed(m.Id)) continue;
                        if (m.Chapter != chapter)
                        {
                            chapter = m.Chapter;
                            _dossierBody.Add(Kit.Caption(Strings.Format("dossier.chapterFiles", chapter)));
                        }
                        any = true;
                        _dossierBody.Add(Entry(m.Speaker, Strings.Get($"mission.{m.Id}.fragment.title"), Campaign.Label(m) + " · " + Strings.Get($"mission.{m.Id}.name"),
                            Strings.Get($"mission.{m.Id}.fragment"), false, false));
                    }
                    if (!any) _dossierBody.Add(Kit.Body2(Strings.Get("dossier.empty")));
                    break;
                case DossierTab.Maps:
                    foreach (var map in MatchSettings.AllMaps) _dossierBody.Add(MapEntry(map.Id));
                    break;
                case DossierTab.Commanders:
                    FillCommanderFiles();
                    break;
            }
        }

        /// <summary>Opens the dossier on its battlefields tab (the Guide tab's button).</summary>
        private void OpenBattlefields()
        {
            _dossierTab = DossierTab.Maps;
            OpenDossier();
        }

        /// <summary>A boss's rank and general, "Boss · General Viktor Varga" (the general's call sign and naming theme are on its Guide page).</summary>
        private static string BossLine(VehicleDef boss)
        {
            var rank = Strings.Get(boss.RankDef?.Label ?? (boss.MiniBoss ? "boss.rank.mini" : "boss.rank.main"));
            return boss.General is { } general && Strings.Has($"char.{general}.name")
                ? rank + " · " + Strings.Format("guide.boss.general", Strings.Get($"char.{general}.name"))
                : rank;
        }

        /// <summary>A boss file's links: its Guide page, and the main boss it is a variant of.</summary>
        private VisualElement BossLinks(VehicleDef boss)
        {
            var row = Kit.Box("fc-row fc-row--wrap fc-mt-2");
            var id = boss.Id;
            row.Add(new KitButton(ButtonTier.Text, Strings.Get("guide.boss.open"), () => OpenBossGuide(id), "info"));
            if (boss.VariantOf is { } parent && _catalog.Vehicles.ContainsKey(parent))
                row.Add(new KitButton(ButtonTier.Text, Strings.Format("guide.boss.variantOf", Strings.Short(parent)), () => OpenBossGuide(parent), "arrow"));
            return row;
        }

        /// <summary>A battlefield: its picture, name and line, the chapters that fight on it, and its guide where it has one.</summary>
        private static VisualElement MapEntry(string id)
        {
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-dossier__entry fc-dossier__map");
            var art = Kit.Box("fc-dossier__map-art");
            if (MapArt.For(id) is { } picture) art.style.backgroundImage = Background.FromTexture2D(picture);
            card.Add(art);
            var text = Kit.Box("fc-dossier__text");
            text.Add(Kit.Text(Kit.Caps(Strings.Get("map." + id)), "fc-panel-title"));
            var chapters = Campaign.Chapters.Where(c => Campaign.ChapterEnabled(c.Number) && Campaign.MissionsOf(c.Number).Any(m => m.Map == id))
                .Select(c => c.Number.ToString()).ToList();
            var sub = Strings.Has("map." + id + ".sub") ? Strings.Get("map." + id + ".sub") + " · " : "";
            text.Add(Kit.Caption(sub + (chapters.Count > 0 ? Strings.Format("guide.map.chapters", string.Join(", ", chapters)) : Strings.Get("guide.map.skirmish"))));
            if (Strings.Has("guide.map." + id))
            {
                var lines = Strings.Get("guide.map." + id).Split('\n');
                for (var i = 1; i < lines.Length; i++)
                {
                    var label = Kit.Text(Strings.Highlight(lines[i].Trim()), "fc-body fc-mt-1");
                    label.enableRichText = true;
                    text.Add(label);
                }
            }
            card.Add(text);
            return card;
        }

        private static VisualElement Entry(string portrait, string title, string sub, string body, bool locked, bool enemy)
        {
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-dossier__entry" + (locked ? " fc-dossier__entry--locked" : "") + (enemy ? " fc-dossier__entry--enemy" : ""));
            if (portrait != null) card.Add(Portraits.Element(portrait, "fc-portrait"));
            var text = Kit.Box("fc-dossier__text");
            text.Add(Kit.Text(Kit.Caps(title), "fc-panel-title"));
            if (!string.IsNullOrEmpty(sub)) text.Add(Kit.Caption(sub));
            text.Add(Kit.Text(body, locked ? "fc-body-2" : "fc-body"));
            card.Add(text);
            return card;
        }

        private static bool IsEnemy(string id) => id is "varga" or "orlov" or "kessler" or "sen" or "quaden" or "aurel";

        /// <summary>A character is met once a chapter where they speak or command has been reached.</summary>
        private static bool Met(string id)
        {
            if (id == "khai") return true;
            foreach (var m in Campaign.All)
            {
                var speaks = m.Speaker == id || m.General == id;
                if (!speaks)
                    foreach (var r in m.Radio)
                        if (RadioDirector.SpeakerOf(r.Key) == id)
                        {
                            speaks = true;
                            break;
                        }
                if (speaks && Campaign.ChapterOpen(m.Chapter)) return true;
            }
            return false;
        }

        /// <summary>Every boss the story fields, in the order met, and whether it has been beaten (a mission with it won).</summary>
        private static List<(string key, bool beaten)> BossFiles()
        {
            var list = new List<(string, bool)>();
            var seen = new HashSet<string>();
            void Add(ScriptedUnitDef boss, MissionDef mission)
            {
                if (boss == null) return;
                var key = boss.Name ?? boss.Def;
                if (!Strings.Has("bossfile." + key) || !seen.Add(key)) return;
                list.Add((key, PlayerProfile.Completed(mission.Id)));
                // Prompt 16: a flagship's fleet has its own files, under the flagship's.
                if (GameContent.LoadCatalog().Vehicles.TryGetValue(boss.Def, out var flagship))
                    foreach (var ship in flagship.Fleet)
                        if (Strings.Has("bossfile." + ship.Unit) && seen.Add(ship.Unit)) list.Add((ship.Unit, PlayerProfile.Completed(mission.Id)));
                if (flagship?.Craft is { } craft && Strings.Has("bossfile." + craft.Unit) && seen.Add(craft.Unit))
                    list.Add((craft.Unit, PlayerProfile.Completed(mission.Id)));
            }
            foreach (var m in Campaign.All)
            {
                Add(m.Boss, m);
                foreach (var s in m.Stages) Add(s.Mission.Boss, m);
            }
            // A boss met again later counts as beaten once any of its fights is won.
            for (var i = 0; i < list.Count; i++)
            {
                var (key, beaten) = list[i];
                if (beaten) continue;
                foreach (var m in Campaign.All)
                    if (PlayerProfile.Completed(m.Id) && ((m.Boss != null && (m.Boss.Name ?? m.Boss.Def) == key) || m.Stages.Any(s => s.Mission.Boss != null && (s.Mission.Boss.Name ?? s.Mission.Boss.Def) == key)))
                        list[i] = (key, true);
            }
            return list;
        }

        /// <summary>The device checks of the story screens (see the class summary).</summary>
        private void DebugStory()
        {
            if (DebugFlags.Has("-mb-dossier"))
            {
                ShowTab(Tab.Campaign);
                var tab = DebugFlags.Value("-mb-dossier-tab=");
                if (System.Enum.TryParse<DossierTab>(tab, true, out var t)) _dossierTab = t;
                OpenDossier();
                return;
            }
            var chapter = DebugFlags.Value("-mb-chapter=");
            if (int.TryParse(chapter, out var c) && Campaign.Chapter(c) != null)
            {
                ShowTab(Tab.Campaign);
                ShowChapterCard(c, null);
                return;
            }
            var brief = DebugFlags.Value("-mb-brief=");
            if (!string.IsNullOrEmpty(brief) && Campaign.Get(brief) is { } mission)
            {
                ShowTab(Tab.Campaign);
                _selectedMission = Campaign.IndexOf(mission.Id);
                OpenChapter(System.Math.Max(1, mission.Chapter));
                ShowBriefing(mission);
                return;
            }
            // The campaign page itself, a mission chosen: -mb-campaign (-mb-campaign=c5m10).
            if (DebugFlags.Has("-mb-campaign") || DebugFlags.Value("-mb-campaign=") != null)
            {
                ShowTab(Tab.Campaign);
                if (Campaign.Get(DebugFlags.Value("-mb-campaign=")) is { } chosen)
                {
                    _selectedMission = Campaign.IndexOf(chosen.Id);
                    OpenChapter(System.Math.Max(1, chosen.Chapter));
                }
            }
        }
    }
}
