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
    /// everything), -mb-chapter=3 (a chapter's opening card), -mb-brief=c3m05 (a briefing card).
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private enum DossierTab
        {
            People,
            Bosses,
            Timeline,
            Files,
        }

        private VisualElement _dossier, _dossierBody;
        private readonly List<(VisualElement button, DossierTab tab)> _dossierTabs = new();
        private DossierTab _dossierTab;
        private bool _dossierAll;

        private void BuildDossierPage()
        {
            _dossier = FullPage("dossier-page");
            var tabs = UiKit.Box("dossier-tabs");
            foreach (var (tab, key) in new[] { (DossierTab.People, "dossier.people"), (DossierTab.Bosses, "dossier.bosses"),
                         (DossierTab.Timeline, "dossier.timeline"), (DossierTab.Files, "dossier.files") })
            {
                var t = tab;
                var button = UiKit.Button("segment dossier-tab", () =>
                {
                    _dossierTab = t;
                    FillDossier();
                });
                button.Add(UiKit.Text(Strings.Get(key), "segment-label"));
                tabs.Add(button);
                _dossierTabs.Add((button, tab));
            }
            _dossier.Add(tabs);
            var scroll = Scroller("dossier-scroll");
            _dossierBody = scroll.contentContainer;
            _dossier.Add(scroll);
            _dossierAll = DebugFlags.Has("-mb-dossier-all");
            Root.schedule.Execute(DebugStory).StartingIn(300);
        }

        private void OpenDossier()
        {
            Open(_dossier, Strings.Get("campaign.dossier").ToUpperInvariant());
            FillDossier();
        }

        private void FillDossier()
        {
            foreach (var (button, tab) in _dossierTabs) button.EnableInClassList("chosen", tab == _dossierTab);
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
                        _dossierBody.Add(Entry(null, Strings.Get("boss." + key), null, open ? Strings.Get("bossfile." + key) : Strings.Get("dossier.lockedBoss"), !open, true));
                    }
                    break;
                case DossierTab.Timeline:
                    _dossierBody.Add(Entry(null, Strings.Get("dossier.before"), null, Strings.Get("timeline.0"), false, false));
                    for (var c = 1; c <= Campaign.ChapterCount; c++)
                    {
                        var done = _dossierAll || Campaign.ChapterDone(c);
                        _dossierBody.Add(Entry(null, Strings.Format("dossier.chapterFiles", c) + " · " + Strings.Get($"chapter.{c}.title"), null,
                            done ? Strings.Get($"timeline.{c}") : Strings.Get("dossier.lockedChapter"), !done, false));
                    }
                    if (_dossierAll || Campaign.ChapterDone(Campaign.ChapterCount))
                        _dossierBody.Add(Entry(null, Strings.Get("campaign.epilogue.title"), null, Strings.Get("campaign.epilogue"), false, false));
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
                            _dossierBody.Add(UiKit.Text(Strings.Format("dossier.chapterFiles", chapter).ToUpperInvariant(), "menu-caps dossier-caps"));
                        }
                        any = true;
                        _dossierBody.Add(Entry(m.Speaker, Strings.Get($"mission.{m.Id}.fragment.title"), Campaign.Label(m) + " · " + Strings.Get($"mission.{m.Id}.name"),
                            Strings.Get($"mission.{m.Id}.fragment"), false, false));
                    }
                    if (!any) _dossierBody.Add(UiKit.Text(Strings.Get("dossier.empty"), "dossier-empty"));
                    break;
            }
            UiKit.Uppercase(_dossier);
        }

        private static VisualElement Entry(string portrait, string title, string sub, string body, bool locked, bool enemy)
        {
            var card = UiKit.Box("dossier-entry");
            card.EnableInClassList("locked", locked);
            card.EnableInClassList("enemy", enemy);
            if (portrait != null) card.Add(Portraits.Element(portrait, "dossier-portrait"));
            var text = UiKit.Box("dossier-text");
            text.Add(UiKit.Text(title, "dossier-title"));
            if (!string.IsNullOrEmpty(sub)) text.Add(UiKit.Text(sub, "dossier-sub"));
            text.Add(UiKit.Text(body, "dossier-body"));
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
                Refresh();
                ShowBriefing(mission);
            }
        }
    }
}
