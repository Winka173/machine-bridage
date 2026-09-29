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
    /// Prompt 21 L: the language switched with a tap, on the settings screen (the menu is then built again in the new
    /// language, as the reload does) and in a paused battle (the HUD relabels itself in place; the battle goes on):
    /// the screen shows only the new language afterwards, and the pause stays open and usable.
    /// </summary>
    public class L10nSwitchTests : UITestFixture
    {
        private Catalog _catalog;
        private LanguageChoice _choice;
        private bool _vietnamese;

        [OneTimeSetUp]
        public void LoadCatalog() => _catalog = GameContent.LoadCatalog();

        [SetUp]
        public void Remember()
        {
            _choice = MatchSettings.Language;
            _vietnamese = Strings.Vietnamese;
            DemoProfile.Use();
        }

        [TearDown]
        public void Restore()
        {
            MatchSettings.Language = _choice;
            MatchSettings.Save();
            Strings.Vietnamese = _vietnamese;
            DemoProfile.Restore();
        }

        private void Mount(VisualElement content)
        {
            panelSize = new Vector2(1280, 720);
            rootVisualElement.Clear();
            rootVisualElement.styleSheets.Add(Resources.Load<ThemeStyleSheet>("UI/Theme"));
            content.style.position = Position.Absolute;
            content.style.left = content.style.top = content.style.right = content.style.bottom = 0;
            rootVisualElement.Add(content);
            for (var i = 0; i < 3; i++) simulate.FrameUpdate();
        }

        private static KitChip Chip(VisualElement root, string label) =>
            root.Query<KitChip>().ToList().FirstOrDefault(c => c.Q<TextElement>()?.text == Kit.Caps(label));

        [Test]
        public void SwitchingOnTheSettingsScreenRebuildsTheMenuInTheNewLanguage()
        {
            foreach (var (from, to, label) in new[] { (false, true, "Tiếng Việt"), (true, false, "English") })
            {
                MatchSettings.Language = from ? LanguageChoice.Vietnamese : LanguageChoice.English;
                MatchSettings.ApplyLanguage();
                var host = MachineBrigade.Editor.UiShots.BuildMenu(_catalog, "settings", out _);
                Mount(host);
                var chip = Chip(host, label);
                Assert.IsNotNull(chip, "the language chip " + label);
                simulate.Click(chip);
                simulate.FrameUpdate();
                Assert.AreEqual(to, Strings.Vietnamese, "the language switched at once");
                Assert.AreEqual(to ? LanguageChoice.Vietnamese : LanguageChoice.English, MatchSettings.Language, "and was saved");
                // The menu reloads in the new language: every screen reads it.
                foreach (var screen in new[] { "settings", "home", "army-base" })
                {
                    var rebuilt = MachineBrigade.Editor.UiShots.BuildMenu(_catalog, screen, out _);
                    Mount(rebuilt);
                    var mixed = L10nTests.MixedWords(rebuilt, $"{(to ? "vi" : "en")} {screen}");
                    Assert.IsEmpty(mixed, string.Join("\n", mixed.Take(30)));
                }
            }
        }

        [Test]
        public void SwitchingInAPausedBattleRelabelsTheHudInPlace()
        {
            foreach (var (from, to, label) in new[] { (false, true, "Tiếng Việt"), (true, false, "English") })
            {
                MatchSettings.Language = from ? LanguageChoice.Vietnamese : LanguageChoice.English;
                MatchSettings.ApplyLanguage();
                foreach (var screen in new[] { "hud-score", "hud-mission" })
                {
                    Strings.Vietnamese = from;
                    MatchSettings.Language = from ? LanguageChoice.Vietnamese : LanguageChoice.English;
                    var host = new VisualElement();
                    host.AddToClassList("hud");
                    host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
                    host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Screens"));
                    var hud = MachineBrigade.Editor.UiShots.BuildHud(_catalog, screen, host);
                    Mount(host);
                    hud.SetPaused(true);
                    simulate.FrameUpdate();
                    var switched = 0;
                    hud.LanguageSwitched += () => switched++;
                    var chip = Chip(hud.Pause.Root, label);
                    Assert.IsNotNull(chip, "the pause menu's language chip " + label);
                    simulate.Click(chip);
                    simulate.FrameUpdate();
                    Assert.AreEqual(to, Strings.Vietnamese, screen + ": the language switched");
                    Assert.AreEqual(1, switched, screen + ": the HUD relabelled itself once");
                    Assert.IsTrue(hud.Pause.Visible, screen + ": the pause stays open");
                    var mixed = L10nTests.MixedWords(host, $"{(to ? "vi" : "en")} {screen} paused");
                    Assert.IsEmpty(mixed, string.Join("\n", mixed.Take(30)));
                    hud.Dispose();
                }
            }
        }
    }
}
#endif
