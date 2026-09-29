// Needs the UI Toolkit test framework package (com.unity.ui.test-framework); without it the rest of the project still compiles.
#if MB_UI_TEST_FRAMEWORK
using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Input;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using NUnit.Framework;
using UnityEditor.UIElements.TestFramework;
using UnityEngine;
using UnityEngine.UIElements;
using Numerics = System.Numerics;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 23 F.2-F.5 (DECISIONS 23F): each event marker shows on its input and goes when it ends: the direction arrows
    /// (minimap and screen edge), the Accord's sign on its units and minimap blips, a general's name label and its speaking
    /// mark, the side objective's row and its notices; and none of them covers the dialogue line, the notices at the top or
    /// the tray, on a real panel at the narrowest screen the game supports.
    /// </summary>
    public class EventHudTests
    {
        private static readonly Vector2 Narrowest = new(1280, 720);

        private EditorPanelSimulator _panel;
        private bool _vietnamese;
        private TextSize _textSize;
        private Catalog _catalog;

        [OneTimeSetUp]
        public void LoadCatalog() => _catalog = GameContent.LoadCatalog();

        [SetUp]
        public void CreatePanel()
        {
            _vietnamese = Strings.Vietnamese;
            _textSize = MatchSettings.TextSize;
            _panel = new EditorPanelSimulator();
            _panel.rootVisualElement.styleSheets.Add(Resources.Load<ThemeStyleSheet>("UI/Theme"));
            DemoProfile.Use();
        }

        [TearDown]
        public void ReleasePanel()
        {
            Strings.Vietnamese = _vietnamese;
            MatchSettings.TextSize = _textSize;
            DemoProfile.Restore();
            _panel.Dispose();
        }

        private (BattleHud hud, VisualElement host) Build(string screen, bool vietnamese = false, bool large = false)
        {
            Strings.Vietnamese = vietnamese;
            MatchSettings.TextSize = large ? TextSize.Large : TextSize.Normal;
            var host = new VisualElement();
            host.AddToClassList("hud");
            host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
            host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Screens"));
            var hud = MachineBrigade.Editor.UiShots.BuildHud(_catalog, screen, host);
            var root = _panel.rootVisualElement;
            root.Clear();
            _panel.panelSize = Narrowest;
            _panel.ApplyPanelSize();
            host.style.position = Position.Absolute;
            host.style.left = host.style.top = host.style.right = host.style.bottom = 0;
            root.Add(host);
            Frames();
            return (hud, host);
        }

        private void Frames()
        {
            for (var i = 0; i < 3; i++) _panel.FrameUpdate();
        }

        /// <summary>The HUD's frame: what to keep clear of, the markers placed, and laid out again.</summary>
        private void Tick(BattleHud hud, float now)
        {
            hud.EventClock = now;
            Frames();
            hud.TickEvents();
            Frames();
        }

        [Test]
        public void ADirectionPutsUpArrowsOnTheMinimapAndAtTheEdgeUntilItsWarningEnds()
        {
            var (hud, _) = Build("hud-mission");
            var arrows = hud.DirectionArrows;
            hud.EventClock = 50f;
            hud.Toast("Enemy reinforcements inbound!", error: true, seconds: 10f, kind: NoticeKind.Reinforce, direction: new Numerics.Vector2(1f, 0f));
            hud.Toast("A notice with no direction");
            Tick(hud, 51f);
            Assert.AreEqual(1, arrows.Showing, "one indicator at the edge");
            Assert.AreEqual(1, hud.Minimap.Arrows.Count, "one arrow on the minimap");
            Assert.IsTrue(hud.Minimap.Arrows[0].Enemy, "an alert's arrow is the enemy's");
            // East, with the square maps' view (north-west up), is down and to the right of the middle.
            var east = arrows.Indicator(0).worldBound.center;
            Assert.That(east.x > Narrowest.x / 2f && east.y > Narrowest.y / 2f, $"east is down-right on screen, not at {east}");

            // The Accord's from the south at the same time; one more from nearly east keeps the first one up, no third.
            hud.Arrow(new Numerics.Vector2(0f, -1f), 6f, enemy: false);
            hud.Arrow(new Numerics.Vector2(0.98f, 0.17f), 4f);
            Tick(hud, 52f);
            Assert.AreEqual(2, arrows.Showing, "several at once, near-duplicates merged");
            Assert.IsTrue(arrows.Indicator(1).ClassListContains("fc-edge-arrow--ours"), "the Accord's in its own colour");
            Assert.IsFalse(hud.Minimap.Arrows[1].Enemy);

            // Each fades as its own warning ends (the Accord's after 6 s, the enemy's after 10).
            Tick(hud, 57.5f);
            Assert.AreEqual(1, arrows.Showing, "the Accord's warning is over");
            Tick(hud, 60.5f);
            Assert.AreEqual(0, arrows.Showing, "every warning is over");
            Assert.AreEqual(0, hud.Minimap.Arrows.Count);
        }

        [Test]
        public void AnAccordUnitWearsItsSignAndColourAndTheMinimapTellsItApart()
        {
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Accord").transform;
            try
            {
                var world = new SimWorld(_catalog, new MapDefinition("range", 220f,
                    new[] { new TeamStart(0, new Numerics.Vector2(0f, -90f)), new TeamStart(1, new Numerics.Vector2(0f, 90f)) },
                    new List<PropPlacement>(), new List<UnitPlacement>()), seed: 7);
                var views = new ViewRegistry(models, meshes, materials, root, 0);
                var allied = world.SpawnVehicle("main_battle_tank", 0, new Numerics.Vector2(-12f, 0f), 0f);
                allied.Ally = true;
                var mine = world.SpawnVehicle("main_battle_tank", 0, new Numerics.Vector2(12f, 0f), 0f);
                var enemy = world.SpawnVehicle("main_battle_tank", 1, new Numerics.Vector2(0f, 60f), 0f);
                var alliedView = views.Add(allied);
                var mineView = views.Add(mine);
                var enemyView = views.Add(enemy);
                void Render()
                {
                    views.SnapshotAll();
                    views.Render(1f, Quaternion.identity);
                }
                Render();
                Assert.IsTrue(alliedView.AccordMarkShown, "the allied-unit tag shows the Accord's sign");
                Assert.AreSame(materials.BarAccord, alliedView.BarFillMaterial, "and the Accord's bar");
                Assert.IsFalse(mineView.AccordMarkShown, "the player's own unit has no sign");
                Assert.AreSame(materials.BarAlly, mineView.BarFillMaterial);

                // The view-side flag for reinforcements the simulation does not tag.
                mineView.AccordMarked = true;
                Render();
                Assert.IsTrue(mineView.AccordMarkShown);
                Assert.AreSame(materials.BarAccord, mineView.BarFillMaterial);
                mineView.AccordMarked = false;
                Render();
                Assert.IsFalse(mineView.AccordMarkShown, "the flag off, the sign goes");
                Assert.AreSame(materials.BarAlly, mineView.BarFillMaterial, "and our green comes back");
                enemyView.AccordMarked = true;
                Render();
                Assert.IsFalse(enemyView.AccordMarkShown, "never on the enemy's side");

                var minimap = new Minimap();
                minimap.Begin(80f);
                minimap.Blip(new Vector2(-12f, 0f), Minimap.AccordTeam, false);
                minimap.Blip(new Vector2(12f, 0f), 0, false);
                Assert.AreEqual(1, minimap.AccordBlips, "the Accord's blip apart from ours");
            }
            finally
            {
                Object.DestroyImmediate(root.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }

        [Test]
        public void AGeneralsLabelShowsTheNameAndASpeakingMarkOnlyWhileTheyAreSpeaking()
        {
            var (hud, _) = Build("hud-mission", vietnamese: true);
            var tags = hud.GeneralTags;
            var field = new Vector2(760f, 330f);
            Tick(hud, 5f);
            tags.Begin(hud.KeepOut);
            Assert.IsTrue(tags.Place(field, "varga", false, 0f), "a label over the battlefield");
            tags.End();
            Frames();
            Assert.AreEqual(1, tags.Showing);
            Assert.AreEqual("VARGA", tags.NameShown(0));
            var mark = tags.Tag(0).Q(className: "fc-general-tag__mark");
            Assert.AreEqual(DisplayStyle.None, mark.resolvedStyle.display, "no mark while silent");

            // H.9: the director says who is speaking; the label shows the mark while the line is up.
            var director = new DialogueDirector();
            director.Say(DialogueRules.Line("radio.varga.behemoth", DialoguePriority.Event, "varga", 1), 100.0);
            Assert.IsTrue(director.IsSpeaking("varga"));
            tags.Begin(hud.KeepOut);
            tags.Place(field, "varga", director.IsSpeaking("varga"), 0.2f);
            tags.End();
            Frames();
            Assert.IsTrue(tags.SpeakingShown(0));
            Assert.AreEqual(DisplayStyle.Flex, mark.resolvedStyle.display, "the speaking mark");

            // Gone from the field (or out of sight): no label.
            tags.Begin(hud.KeepOut);
            tags.End();
            Assert.AreEqual(0, tags.Showing);
        }

        [Test]
        public void ASideObjectiveShowsItsClockOnTheMissionBarAndItsOutcome()
        {
            Strings.Vietnamese = false;
            MatchSettings.TextSize = TextSize.Normal;
            var host = new VisualElement();
            var hud = new BattleHud(new HudSpec { Mode = HudMode.Mission, Compact = true }, new List<CardInfo>(), _catalog, host);
            hud.EventClock = 10f;
            hud.SideObjective("convoy", "goal.escort", 90f, 1, 3);
            var row = hud.SideObjectiveRow;
            var clock = row.Q<Label>(className: "fc-mission-bar__side-clock");
            Assert.AreEqual(DisplayStyle.Flex, row.style.display.value, "the row is up");
            Assert.AreEqual("1:30", clock.text);
            Assert.AreEqual("1/3", row.Q<Label>(className: "fc-mission-bar__side-count").text, "how far along");
            Assert.IsTrue(hud.NoticeText == "Side objective: Escort the convoy" || hud.NoticesWaiting.Any(n => n.Text == "Side objective: Escort the convoy"), "its notice");

            hud.EventClock = 40f;
            hud.TickEvents();
            Assert.AreEqual("1:00", clock.text, "it counts down on the battle's clock");
            // The event system brings it up to date (the same id: no second notice).
            var waiting = hud.NoticesWaiting.Count();
            hud.SideObjective("convoy", "goal.escort", 58f, 2, 3);
            Assert.AreEqual("0:58", clock.text);
            Assert.AreEqual(waiting, hud.NoticesWaiting.Count(), "no second notice");
            hud.SideObjective("convoy", "goal.escort", 60f, 2, 3);
            hud.EventClock = 91.5f;
            hud.TickEvents();
            Assert.AreEqual("0:09", clock.text);
            Assert.IsTrue(clock.ClassListContains("fc-hud__clock--urgent"), "red in its last seconds");

            hud.SideObjectiveDone("convoy", true);
            Assert.AreEqual(DisplayStyle.None, row.style.display.value, "the row goes");
            Assert.IsTrue(hud.NoticeText == "Side objective complete: Escort the convoy" || hud.NoticesWaiting.Any(n => n.Text == "Side objective complete: Escort the convoy"));

            hud.SideObjective("tower", "goal.protect", 30f, announce: false);
            hud.SideObjectiveDone("tower", false);
            Assert.IsNull(hud.SideObjectiveId);
            Assert.IsTrue(hud.NoticesWaiting.Any(n => n.Text == "Side objective failed: Protect the buildings"), "a time-out says so");
        }

        [Test]
        public void TheMarkersKeepClearOfTheDialogueTheNoticesAndTheTray()
        {
            var failures = new List<string>();
            foreach (var (screen, large, selection) in new[]
                     {
                         ("hud-dialogue", false, false), ("hud-dialogue", false, true), ("hud-dialogue", true, false), ("hud-dialogue", true, true),
                         ("hud-dialogue-full", false, false), ("hud-dialogue-full", true, false), ("hud-mission", false, false), ("hud-mission", true, false),
                     })
            {
                var (hud, host) = Build(screen, vietnamese: true, large: large);
                var tag = $"{screen}{(large ? " large" : "")}{(selection ? " selection" : "")}";
                hud.EventClock = 20f;
                hud.SideObjective("side", "goal.escort", 75f, announce: false);
                if (selection) hud.SetSelection(new SelectionSummary(3, "main_battle_tank", 1450f, 2000f));
                Frames();
                Rect Of(string className) => host.Q(className: className)?.worldBound ?? Rect.zero;
                var deck = Of("fc-deck");
                var notice = Of("fc-hud__toast-face");
                var bar = Of("fc-mission-bar");
                var boss = Of("fc-boss");
                var strip = hud.Dialogue.Label.parent.worldBound;
                var keep = new List<(string what, Rect r)> { ("the dialogue line", strip), ("the notice", notice), ("the mission bar", bar), ("the boss bar", boss), ("the tray", deck) };

                // Every direction round the compass, four at a time (the most at once).
                for (var batch = 0; batch < 2; batch++)
                {
                    hud.DirectionArrows.Clear();
                    for (var i = 0; i < 4; i++)
                    {
                        var a = (batch * 4 + i) * Mathf.PI / 4f;
                        hud.Arrow(new Numerics.Vector2(Mathf.Cos(a), Mathf.Sin(a)), 10f, i % 2 == 0);
                    }
                    Tick(hud, 21f);
                    if (hud.DirectionArrows.Showing != 4) failures.Add($"{tag}: {hud.DirectionArrows.Showing} of 4 indicators found a place");
                    for (var i = 0; i < DirectionArrows.Max; i++)
                    {
                        var r = hud.DirectionArrows.Indicator(i).worldBound;
                        foreach (var (what, k) in keep)
                            if (k.width > 0f && r.Overlaps(k)) failures.Add($"{tag}: arrow {batch * 4 + i} ({r.xMin:0},{r.yMin:0}) over {what} ({k.xMin:0},{k.yMin:0}-{k.xMax:0},{k.yMax:0})");
                        if (r.xMin < -0.5f || r.yMin < -0.5f || r.xMax > Narrowest.x + 0.5f || r.yMax > Narrowest.y + 0.5f) failures.Add($"{tag}: arrow {batch * 4 + i} off screen at {r}");
                    }
                }

                // The side objective's row stays clear of the notices under the strip, and of the boss bar.
                var side = hud.SideObjectiveRow.worldBound;
                if (side.height > (large ? 36f : 31f)) failures.Add($"{tag}: the side objective takes {side.height:0} px (one line)");
                if (bar.yMax > notice.yMin) failures.Add($"{tag}: the mission bar (to {bar.yMax:0}) over the notice (from {notice.yMin:0})");
                if (side.Overlaps(notice)) failures.Add($"{tag}: the side objective ({side.yMin:0}-{side.yMax:0}, the bar to {bar.yMax:0}) over the notice ({notice.yMin:0}-{notice.yMax:0})");
                if (boss.width > 0f && side.Overlaps(boss)) failures.Add($"{tag}: the side objective ({side.xMin:0},{side.yMin:0}-{side.xMax:0},{side.yMax:0}) over the boss bar ({boss.xMin:0},{boss.yMin:0}-{boss.xMax:0},{boss.yMax:0})");

                // A general's label is hidden where it would touch the line, the notices or the tray, and shown on the field.
                var tags = hud.GeneralTags;
                foreach (var (what, k) in keep)
                {
                    if (k.width <= 0f) continue;
                    tags.Begin(hud.KeepOut);
                    if (tags.Place(new Vector2(k.center.x, k.yMax - 2f), "kessler", false, 0f)) failures.Add($"{tag}: a label over {what}");
                    tags.End();
                }
                tags.Begin(hud.KeepOut);
                var open = new Vector2(Narrowest.x * 0.55f, (notice.yMax + strip.yMin) * 0.5f + 15f);
                if (!tags.Place(open, "kessler", false, 0f)) failures.Add($"{tag}: no label on the open field at {open}");
                tags.End();
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }
    }
}
#endif
