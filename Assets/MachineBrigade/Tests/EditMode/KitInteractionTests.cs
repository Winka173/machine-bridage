using System;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
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
    }
}
