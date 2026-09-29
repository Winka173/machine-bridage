// Needs the UI Toolkit test framework package (com.unity.ui.test-framework); without it the rest of the project still compiles.
#if MB_UI_TEST_FRAMEWORK
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;
using UnityEngine.UIElements.TestFramework;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 6 (DECISIONS 21B): Start on a campaign mission reaches the battle through the real taps (Campaign, the
    /// chapter, the mission, Start, the chapter card, the briefing's Deploy), on a new profile, an old one migrated from
    /// before prompt 20 and one part-way through the campaign, also after a Back pressed first: a Back with no dialog open
    /// took the hidden story card out of the menu, and Start then showed nothing. A boss's page has no card controls.
    /// </summary>
    public class CampaignStartTests : UITestFixture
    {
        /// <summary>A save of the nine-chapter story and the old roster, chapter 1 half won.</summary>
        private const string OldSave =
            "{\"campaignVersion\":2,\"rosterVersion\":1,\"gearVersion\":4,\"coins\":900,\"xp\":600," +
            "\"missionIds\":[\"c1m01\",\"c1m02\",\"c1m03\"],\"missionStars\":[3,2,1],\"missionTiers\":[0,0,0],\"chaptersSeen\":[1]," +
            "\"unlocked\":[\"light_tank\",\"apc\"],\"owned\":[\"heavy_attack_heli\"]}";

        private MenuScreen Menu(System.Action play)
        {
            panelSize = new Vector2(1280, 720);
            rootVisualElement.styleSheets.Add(Resources.Load<ThemeStyleSheet>("UI/Theme"));
            var host = new VisualElement();
            host.AddToClassList("hud");
            host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
            host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Screens"));
            host.style.position = Position.Absolute;
            host.style.left = host.style.top = host.style.right = host.style.bottom = 0;
            var menu = new MenuScreen(GameContent.LoadCatalog(), play);
            host.Add(menu.Root);
            rootVisualElement.Add(host);
            menu.DebugShow("home");
            Frames(3);
            return menu;
        }

        private void Frames(int n)
        {
            for (var i = 0; i < n; i++) simulate.FrameUpdate();
        }

        private void Tap(VisualElement target, string what)
        {
            Assert.IsNotNull(target, what + " is on the screen");
            target.GetFirstAncestorOfType<ScrollView>()?.ScrollTo(target);
            Frames(2);
            simulate.Click(target);
            Frames(2);
        }

        [TestCase("fresh", "c1m01", false)]
        [TestCase("fresh", "c1m01", true)]
        [TestCase("old", "c1m01", true)]
        [TestCase("demo", "next", true)]
        public void StartReachesTheBattle(string profile, string missionId, bool backFirst)
        {
            MatchSettings.SaveSuspended = true;
            var (mode, mission, run) = (MatchSettings.Mode, MatchSettings.Mission, MatchSettings.Run);
            try
            {
                if (profile == "demo") DemoProfile.Use();
                else PlayerProfile.LoadForTests(profile == "old" ? OldSave : "{}");
                var target = missionId == "next" ? Campaign.All[Campaign.Next] : Campaign.Get(missionId);
                Assert.IsTrue(Campaign.IsOpen(Campaign.IndexOf(target.Id)), target.Id + " is open");
                var launched = 0;
                var menu = Menu(() => launched++);
                // Android's back button at home: nothing to close, and the story card stays in the menu.
                if (backFirst) menu.Back();
                var root = menu.Root;
                Tap(root.Query<KitNavItem>().ToList().FirstOrDefault(n => n.Q<Label>(className: "fc-nav-item__label")?.text == Kit.Caps(Strings.Get("nav.campaign"))), "Campaign");
                var at = Campaign.ShownChapters.ToList().FindIndex(c => c.Number == target.Chapter);
                Tap(root.Query(className: "fc-chapter").ToList().ElementAtOrDefault(at), "chapter " + target.Chapter);
                var label = Campaign.Label(target);
                Tap(root.Query(className: "fc-mission").ToList().FirstOrDefault(r => r.Q<Label>(className: "fc-mission__number")?.text == label), "mission " + label);
                var start = root.Q<KitButton>(className: "fc-campaign__start");
                Assert.IsFalse(start.Disabled, "Start is live: " + start.Reason);
                Tap(start, "Start");
                // The chapter card the first time, then the briefing: their main button each, until the battle starts.
                for (var card = 0; card < 3 && launched == 0; card++)
                {
                    var story = root.Q(className: "fc-story-scrim");
                    Assert.IsNotNull(story?.panel, "the story card is in the menu");
                    Assert.AreEqual(DisplayStyle.Flex, story.resolvedStyle.display, "Start shows the card");
                    Tap(story.Q(className: "fc-story__buttons").Query<KitButton>().ToList().Last(), "the card's main button");
                }
                Assert.AreEqual(1, launched, "Deploy starts the battle");
                Assert.AreEqual(GameModeKind.Campaign, MatchSettings.Mode);
                Assert.AreEqual(target.Id, MatchSettings.Mission);
            }
            finally
            {
                (MatchSettings.Mode, MatchSettings.Mission, MatchSettings.Run) = (mode, mission, run);
                MatchSettings.SaveSuspended = false;
                if (profile == "demo") DemoProfile.Restore();
                else PlayerProfile.Load();
            }
        }

        /// <summary>Back with a dialog open closes the dialog, not the hidden story card; with the card open, it hides it.</summary>
        [Test]
        public void BackClosesTheTopDialogAndKeepsTheStoryCard()
        {
            DemoProfile.Use();
            try
            {
                var menu = Menu(() => { });
                var dialog = KitDialog.Present(menu.Root, KitDialog.Build("T", "B"));
                Assert.IsTrue(menu.Back());
                Assert.IsNull(dialog.parent, "the dialog closed");
                var story = menu.Root.Q(className: "fc-story-scrim");
                Assert.IsNotNull(story, "the story card stays in the menu");
                menu.DebugShow("briefing");
                Frames(2);
                Assert.AreEqual(DisplayStyle.Flex, story.resolvedStyle.display);
                Assert.IsTrue(menu.Back());
                Frames(1);
                Assert.AreEqual(DisplayStyle.None, story.resolvedStyle.display, "hidden");
                Assert.IsNotNull(story.parent, "not taken out");
            }
            finally
            {
                DemoProfile.Restore();
            }
        }

        /// <summary>A boss's page: no Equipment tab, no level, blueprint, deck or upgrade controls; its file and numbers.</summary>
        [TestCase("detail-boss")]
        [TestCase("detail-boss-stats")]
        public void ABossPageHasNoCardControls(string screen)
        {
            DemoProfile.Use();
            try
            {
                var menu = Menu(() => { });
                menu.DebugShow(screen);
                Frames(3);
                var page = menu.Root.Q(className: "fc-detail");
                var tabs = page.Q<KitTabs>();
                Assert.AreEqual(DisplayStyle.None, tabs.Tabs[4].resolvedStyle.display, "no Equipment tab");
                Assert.IsEmpty(page.Query<KitButton>().ToList().Where(b => b.Label == Kit.Caps(Strings.Get("detail.levelUp")) || b.Label == Kit.Caps(Strings.Get("detail.addToDeck"))).ToList(), "no level-up or deck button");
                Assert.IsNull(page.Q(className: "fc-detail__prints"), "no blueprints");
                var text = string.Join("|", page.Query<Label>().ToList().Select(l => l.text));
                StringAssert.DoesNotContain(Strings.Format("kit.level", 1), text, "no level tag");
                if (screen == "detail-boss")
                {
                    StringAssert.Contains(Kit.Caps(Strings.Get("guide.boss.escorts")), text, "its escorts");
                    StringAssert.Contains(Kit.Caps(Strings.Get("guide.parts")), text, "its parts");
                }
                else
                {
                    StringAssert.Contains(Strings.Get("guide.boss.noCard"), text);
                    StringAssert.Contains(BossFile.Armour(GameContent.LoadCatalog().Vehicles["behemoth"].Armour), text, "its armour");
                    Assert.IsNull(page.Q(className: "fc-stat__gain"), "no equipment or next-level gains");
                }
            }
            finally
            {
                DemoProfile.Restore();
            }
        }

        /// <summary>The Sandbox's boss file: the same facts in a dialog.</summary>
        [Test]
        public void TheBossFileCardHasTheFacts()
        {
            var catalog = GameContent.LoadCatalog();
            var boss = catalog.Vehicles["behemoth"];
            var card = BossFile.Card(catalog, boss, () => { });
            var text = string.Join("|", card.Query<Label>().ToList().Select(l => l.text));
            StringAssert.Contains(Kit.Caps(Strings.Card("behemoth")), text);
            StringAssert.Contains(BossFile.Rank(boss), text);
            StringAssert.Contains(BossFile.Armour(boss.Armour), text);
            if (boss.Parts.Count > 0) StringAssert.Contains(BossFile.PartStats(boss, boss.Parts[0]), text);
            StringAssert.Contains(Kit.Caps(Strings.Get("guide.boss.escorts")), text);
        }
    }
}
#endif
