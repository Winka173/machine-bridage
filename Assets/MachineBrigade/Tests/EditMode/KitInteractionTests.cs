// Needs the UI Toolkit test framework package (com.unity.ui.test-framework); without it the rest of the project still compiles.
#if MB_UI_TEST_FRAMEWORK
using System;
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
    /// Field Command 2.0, taps on kit controls (the UI test framework's fixture, whose simulated
    /// clicks go through the panel like a finger's): a danger button only asks, and its dialog's red
    /// button acts; disabled and loading buttons ignore taps and a disabled one says why.
    /// </summary>
    public class KitInteractionTests : UITestFixture
    {
        private void Mount(VisualElement content)
        {
            panelSize = new Vector2(1280, 720);
            rootVisualElement.styleSheets.Add(Resources.Load<ThemeStyleSheet>("UI/Theme"));
            content.style.position = Position.Absolute;
            content.style.left = content.style.top = content.style.right = content.style.bottom = 0;
            rootVisualElement.Add(content);
            for (var i = 0; i < 3; i++) simulate.FrameUpdate();
        }

        [Test]
        public void ADangerButtonAsksFirst()
        {
            var ran = 0;
            var host = Kit.Root("fc-screen");
            var danger = KitButton.Danger("Sell", new KitConfirm("Sell?", "You get 40 coins.", "Sell"), () => ran++);
            host.Add(danger);
            Mount(host);
            simulate.Click(danger);
            simulate.FrameUpdate();
            Assert.AreEqual(0, ran, "the tap only asks");
            var scrim = host.Q(className: KitDialog.ScrimClass);
            Assert.IsNotNull(scrim, "a confirmation opened");
            var buttons = scrim.Query<KitButton>().ToList();
            Assert.AreEqual(2, buttons.Count, "Cancel and the red confirm");
            Assert.AreEqual(ButtonTier.Secondary, buttons[0].Tier);
            Assert.AreEqual(ButtonTier.Danger, buttons[1].Tier);
            simulate.Click(buttons[1]);
            simulate.FrameUpdate();
            Assert.AreEqual(1, ran, "confirmed");
            Assert.IsNull(host.Q(className: KitDialog.ScrimClass), "the dialog closed");
            Assert.Throws<ArgumentException>(() => _ = new KitButton(ButtonTier.Danger, "Reset", null));
        }

        [Test]
        public void DisabledAndLoadingButtonsIgnoreTapsAndSayWhy()
        {
            var taps = 0;
            var host = Kit.Root("fc-screen");
            var disabled = new KitButton(ButtonTier.Primary, "Upgrade", () => taps++).Disable("320 coins short");
            var loading = new KitButton(ButtonTier.Secondary, "Save", () => taps++).SetLoading(true);
            host.Add(disabled);
            host.Add(loading);
            Mount(host);
            simulate.Click(disabled);
            simulate.Click(loading);
            Assert.AreEqual(0, taps);
            Assert.AreEqual("320 coins short", disabled.Reason);
            Assert.IsTrue(UiLayoutTests.Shown(disabled.Q<Label>(className: "fc-btn__reason")), "the reason shows under the label");
            Assert.Throws<ArgumentException>(() => new KitButton(ButtonTier.Secondary, "X", null).Disable(""));
            Assert.Throws<ArgumentException>(() => _ = new KitIconButton("close", " ", null));
        }

        /// <summary>
        /// Test feedback 2 (DECISIONS 12E): the home screen's mode picker lists Boss Rush with its line,
        /// and a tap on it sets the battle Deploy starts (Deploy starts the picker's mode).
        /// </summary>
        [Test]
        public void TheSetupModePickerOffersBossRush()
        {
            var mode = MatchSettings.Mode;
            var vietnamese = Strings.Vietnamese;
            DemoProfile.Use();
            try
            {
                Strings.Vietnamese = true;
                var host = new VisualElement();
                host.AddToClassList("hud");
                host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
                host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Screens"));
                var menu = new MenuScreen(GameContent.LoadCatalog(), () => { });
                host.Add(menu.Root);
                Mount(host);
                menu.DebugShow("home");
                simulate.FrameUpdate();
                var drop = host.Query<KitDropdown>().ToList().First(d => d.Q<Label>(className: "fc-dropdown__label").text == Kit.Caps(Strings.Get("setup.mode")));
                simulate.Click(drop);
                simulate.FrameUpdate();
                var rows = rootVisualElement.Query(className: "fc-option").ToList();
                Assert.IsNotEmpty(rows, "the mode list opened");
                var row = rows.FirstOrDefault(r => r.Query<Label>().ToList().Any(l => l.text == Strings.Get("mode.bossrush")));
                Assert.IsNotNull(row, "Boss Rush is in the list: " + string.Join(", ", rows.Select(r => r.Q<Label>()?.text)));
                StringAssert.Contains(Strings.Format("mode.bossrushSub", MachineBrigade.Sim.Modes.BossRushRules.Kinds.Count),
                    string.Join("|", row.Query<Label>().ToList().Select(l => l.text)), "with its line");
                row.GetFirstAncestorOfType<ScrollView>()?.ScrollTo(row);
                for (var i = 0; i < 2; i++) simulate.FrameUpdate();
                simulate.Click(row);
                simulate.FrameUpdate();
                Assert.AreEqual(GameModeKind.BossRush, MatchSettings.Mode, "picked");
                Assert.AreEqual(Strings.Get("mode.bossrush"), drop.Q<Label>(className: "fc-dropdown__value").text, "the picker shows it");
            }
            finally
            {
                MatchSettings.Mode = mode;
                Strings.Vietnamese = vietnamese;
                DemoProfile.Restore();
            }
        }
    }
}
#endif
