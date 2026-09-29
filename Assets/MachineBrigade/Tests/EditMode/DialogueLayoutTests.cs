// Needs the UI Toolkit test framework package (com.unity.ui.test-framework); without it the rest of the project still compiles.
#if MB_UI_TEST_FRAMEWORK
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Input;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEditor.UIElements.TestFramework;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 23 H.2 on a real panel at the narrowest screen the game supports (1280 panel px wide: 16:9 and 4:3): every
    /// in-battle line fits two lines of the subtitle, in both languages and at Large text; the subtitle sits above the
    /// tray, clear of the notices at the top, and above the selection strip and the strike prompt while they are up.
    /// </summary>
    public class DialogueLayoutTests
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

        private (BattleHud hud, VisualElement host) Build(bool vietnamese, bool large)
        {
            Strings.Vietnamese = vietnamese;
            MatchSettings.TextSize = large ? TextSize.Large : TextSize.Normal;
            var host = new VisualElement();
            host.AddToClassList("hud");
            host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
            host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Screens"));
            var hud = MachineBrigade.Editor.UiShots.BuildHud(_catalog, "hud-dialogue", host);
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

        /// <summary>Every line a battle says: the lines of the campaign, the bosses, the generals and the Radio events, and the commanders' first words.</summary>
        internal static List<string> BattleKeys() =>
            Strings.Keys.Distinct().Where(k => k.StartsWith("radio.") && !k.Contains(".taunt.") || Regex.IsMatch(k, @"^cmdr\.[a-z_.]+\.radio\.start$"))
                .OrderBy(k => k).ToList();

        [Test]
        public void NoLineTakesMoreThanTwoLines()
        {
            var keys = BattleKeys();
            Assert.Greater(keys.Count, 400, "the scan finds the lines");
            var failures = new List<string>();
            foreach (var vietnamese in new[] { false, true })
                foreach (var large in new[] { false, true })
                {
                    var (hud, _) = Build(vietnamese, large);
                    var label = hud.Dialogue.Label;
                    var strip = label.parent;
                    var width = hud.Dialogue.Root.contentRect.width - strip.resolvedStyle.paddingLeft - strip.resolvedStyle.paddingRight;
                    Assert.That(hud.Dialogue.Root.contentRect.width, Is.InRange(600f, 640.5f), "about half the screen");
                    Assert.AreEqual(large ? 29f : 24f, label.resolvedStyle.fontSize, 0.01f, "prompt 14's body size");
                    var one = label.MeasureTextSize("Ag", 0, VisualElement.MeasureMode.Undefined, 0, VisualElement.MeasureMode.Undefined).y;
                    // A placeholder gets the longest value the battle fills it with: a boss's call sign ({boss}, a broken part's
                    // report) or an elite's card name ({card}, Recon's report).
                    var boss = _catalog.Vehicles.Values.Where(v => v.Boss).Select(v => BossBar.CallSign(Strings.Card(v.Id))).OrderByDescending(n => n.Length).First();
                    var elite = _catalog.Vehicles.Values.Where(v => v.Elite && !v.Boss).Select(v => Strings.Card(v.Id)).OrderByDescending(n => n.Length).First();
                    foreach (var key in keys)
                    {
                        var names = Strings.PlaceholderNames(Strings.Get(key)).ToList();
                        hud.ShowLine(DialogueRules.Line(key, arg: names.Contains("card") ? elite : names.Count > 0 ? boss : null));
                        var height = label.MeasureTextSize(label.text, width, VisualElement.MeasureMode.Exactly, 0, VisualElement.MeasureMode.Undefined).y;
                        if (height > one * 2f + 2f)
                            failures.Add($"{(vietnamese ? "vi" : "en")}{(large ? " large" : "")} {key}: {height / one:0.#} lines \"{label.text}\"");
                    }
                }
            Assert.IsEmpty(failures, $"{failures.Count} lines over two lines:\n" + string.Join("\n", failures.Take(80)));
        }

        [Test]
        public void TheLineSitsAboveTheTrayClearOfTheNoticesAndTheOrders()
        {
            var failures = new List<string>();
            foreach (var large in new[] { false, true })
            {
                var (hud, host) = Build(true, large);
                // The name in its side's colour, the enemy's unlike ours (the line was shown before the first layout).
                var enemyColour = Regex.Match(hud.Dialogue.Label.text, "<color=(#[0-9A-F]{6})>").Groups[1].Value;
                hud.ShowLine(DialogueRules.Line("radio.khai.c9m02.1"));
                var allyColour = Regex.Match(hud.Dialogue.Label.text, "<color=(#[0-9A-F]{6})>").Groups[1].Value;
                if (enemyColour == "" || allyColour == "" || enemyColour == allyColour) failures.Add($"side colours \"{enemyColour}\" and \"{allyColour}\"");
                hud.ShowLine(DialogueRules.Line("radio.kessler.leviathan", team: 1));
                Frames();
                var strip = hud.Dialogue.Label.parent.worldBound;
                var tag = large ? "large" : "normal";
                var deck = host.Q(className: "fc-deck").worldBound;
                var notice = host.Q(className: "fc-hud__toast-face").worldBound;
                var boss = host.Q(className: "fc-boss").worldBound;
                if (strip.yMax > deck.yMin + 0.5f) failures.Add($"{tag}: over the tray ({strip.yMax:0} > {deck.yMin:0})");
                tag += $" (line {strip.yMin:0}-{strip.yMax:0})";
                if (strip.yMin < Mathf.Max(notice.yMax, boss.yMax)) failures.Add($"{tag}: over the notices at the top");
                if (deck.yMin - strip.yMax > 40f) failures.Add($"{tag}: not just above the tray ({deck.yMin - strip.yMax:0} px)");
                if (Mathf.Abs(strip.center.x - Narrowest.x / 2f) > 1f) failures.Add($"{tag}: not centred");
                hud.SetSelection(new SelectionSummary(3, "main_battle_tank", 1450f, 2000f));
                Frames();
                var command = host.Q(className: "fc-hud__command").worldBound;
                strip = hud.Dialogue.Label.parent.worldBound;
                if (strip.Overlaps(command)) failures.Add($"{tag}: over the selection strip ({strip.yMax:0} > {command.yMin:0})");
                hud.SetTargeting("Airstrike: tap the map");
                Frames();
                var prompt = host.Q(className: "fc-hud__targeting-face").worldBound;
                strip = hud.Dialogue.Label.parent.worldBound;
                if (strip.Overlaps(prompt) || strip.Overlaps(command)) failures.Add($"{tag}: over the strike prompt or the selection ({strip.yMax:0} > {prompt.yMin:0}, {command.yMin:0})");
                if (strip.yMin < Mathf.Max(notice.yMax, boss.yMax)) failures.Add($"{tag}: raised over the notices at the top");
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }
    }
}
#endif
