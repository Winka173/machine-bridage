using NUnit.Framework;
using MachineBrigade.Game.Match;

namespace MachineBrigade.Tests
{
    /// <summary>Graphics presets and the Custom set behave like the big games' menus.</summary>
    public class SettingsTests
    {
        private GraphicsQuality _graphics;

        [SetUp]
        public void SetUp() => _graphics = MatchSettings.Graphics;

        [TearDown]
        public void TearDown() => MatchSettings.Graphics = _graphics;

        [Test]
        public void EveryPresetKeepsEffectsAtMaximum()
        {
            foreach (var tier in new[] { GraphicsQuality.Low, GraphicsQuality.Medium, GraphicsQuality.High })
                Assert.IsTrue(GraphicsOptions.For(tier).MaxEffects, $"{tier}: fire and explosions are never cut by a preset");
        }

        [Test]
        public void PresetsRiseInCost()
        {
            var low = GraphicsOptions.For(GraphicsQuality.Low);
            var high = GraphicsOptions.For(GraphicsQuality.High);
            Assert.Less(low.RenderScale, high.RenderScale);
            Assert.Less((int)low.Shadows, (int)high.Shadows);
            Assert.LessOrEqual(low.FrameRate, high.FrameRate);
        }

        [Test]
        public void ChangingOneOptionKeepsTheRestAndSwitchesToCustom()
        {
            MatchSettings.Graphics = GraphicsQuality.Medium;
            var before = MatchSettings.Options;
            MatchSettings.Customise(o => o.Shadows = ShadowLevel.Off);
            Assert.AreEqual(GraphicsQuality.Custom, MatchSettings.Graphics);
            Assert.AreEqual(ShadowLevel.Off, MatchSettings.Options.Shadows);
            Assert.AreEqual(before.RenderScale, MatchSettings.Options.RenderScale, "the other options stay where the preset put them");

            MatchSettings.Graphics = GraphicsQuality.High;
            Assert.AreEqual(ShadowLevel.High, MatchSettings.Options.Shadows, "picking a preset again replaces the custom set");
        }

        [Test]
        public void SavedValuesSnapToOffered()
        {
            Assert.AreEqual(85, GraphicsOptions.Snap(83, GraphicsOptions.RenderScales));
            Assert.AreEqual(60, GraphicsOptions.Snap(59, GraphicsOptions.FrameRates));
            Assert.AreEqual(1, GraphicsOptions.Snap(0, GraphicsOptions.AntiAliasingLevels));
        }
    }
}
