using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Field Command 2.0, the theme file (Resources/UI/Tokens.uss): the brief's colours are there
    /// exactly, every text-on-background pair of tokens reaches its contrast (4.5:1, 3:1 from 24 px
    /// at the 1400 px reference), the type scale and touch targets match the brief once converted,
    /// and no colour or font size is written anywhere but the token blocks. The kit is checked
    /// strictly; the old screens (Hud.uss, the menu and HUD code) are only reported, to be fixed
    /// by the screen rebuild.
    /// </summary>
    public class UiThemeTests
    {
        private static string ProjectPath(string relative) => Path.GetFullPath(Path.Combine(Application.dataPath, "..", relative));

        private static string TokensText => File.ReadAllText(ProjectPath(KitTokens.AssetPath));

        private static Dictionary<string, string> RootTokens => KitTokens.Declarations(KitTokens.Block(TokensText, ":root"));

        private static Dictionary<string, string> LargeTokens => KitTokens.Declarations(KitTokens.Block(TokensText, ".fc-text-large"));

        private static Color Colour(string token)
        {
            Assert.IsTrue(RootTokens.TryGetValue(token, out var value), "missing token --" + token);
            Assert.IsTrue(KitTokens.TryColour(value, out var c), $"--{token}: not a colour ({value})");
            return c;
        }

        private static float Px(Dictionary<string, string> tokens, string token)
        {
            Assert.IsTrue(tokens.TryGetValue(token, out var value), "missing token --" + token);
            Assert.IsTrue(KitTokens.TryPixels(value, out var px), $"--{token}: not a pixel size ({value})");
            return px;
        }

        private static float Reference(float panelPx) => panelPx / Kit.PanelPxPerReferencePx;

        private static float Points(float panelPx) => panelPx / Kit.PanelPxPerPoint;

        private static Dictionary<string, string> HudTokens => KitTokens.Declarations(KitTokens.Block(TokensText, ".fc-hud"));

        [Test]
        public void TheBriefsColoursAreTheTokens()
        {
            var expected = new Dictionary<string, string>
            {
                ["fc-bg"] = "#101317", ["fc-bg-2"] = "#121519", ["fc-panel"] = "#171b20", ["fc-panel-raised"] = "#1b2026",
                ["fc-panel-selected"] = "#1f252c", ["fc-border"] = "#2c333b", ["fc-border-strong"] = "#3a424b",
                ["fc-text"] = "#e9e6df", ["fc-text-2"] = "#aab2ba", ["fc-text-dim"] = "#8a939b",
                ["fc-accent"] = "#f2a33a", ["fc-accent-press"] = "#d88a22", ["fc-coin"] = "#e8c15a", ["fc-danger"] = "#e0513a",
                ["fc-branch-armor"] = "#8fb3d6", ["fc-branch-light"] = "#a9cf7a", ["fc-branch-artillery"] = "#e0956a",
                ["fc-branch-air"] = "#bba6e6", ["fc-branch-support"] = "#cfc8b8",
            };
            var tokens = RootTokens;
            foreach (var (token, hex) in expected)
                Assert.AreEqual(hex, tokens.TryGetValue(token, out var v) ? v.ToLowerInvariant() : null, "--" + token);
            // The battlefield panel is #12161b at 92-94 %.
            var field = Colour("fc-panel-field");
            Assert.AreEqual("12161B", ColorUtility.ToHtmlStringRGB(field));
            Assert.That(field.a, Is.InRange(0.92f, 0.94f));
            // Legendary is redder than the accent, so it never reads as the main button.
            var legendary = Colour("fc-rarity-legendary");
            Color.RGBToHSV(legendary, out var hl, out _, out _);
            Color.RGBToHSV(Colour("fc-accent"), out var ha, out _, out _);
            Assert.Less(hl, ha - 0.03f, "legendary's hue sits towards red of the accent's");
        }

        /// <summary>Surfaces text is drawn on. The battlefield panel is judged over black, grey and white battlefields.</summary>
        private static IEnumerable<(string name, Color colour)> Surfaces()
        {
            foreach (var t in new[] { "fc-bg", "fc-bg-2", "fc-panel", "fc-panel-raised", "fc-panel-selected" }) yield return (t, Colour(t));
            var field = Colour("fc-panel-field");
            yield return ("fc-panel-field over black", KitTokens.Over(field, Color.black));
            yield return ("fc-panel-field over grey", KitTokens.Over(field, new Color(0.5f, 0.5f, 0.5f)));
            yield return ("fc-panel-field over white", KitTokens.Over(field, Color.white));
        }

        [Test]
        public void EveryTextOnBackgroundPairReachesItsContrast()
        {
            var smallest = Px(RootTokens, "fc-fs-small");
            var body = Px(RootTokens, "fc-fs-body");
            var failures = new List<string>();
            void Check(string fg, string bgName, Color bg, float size)
            {
                var ratio = KitTokens.Contrast(Colour(fg), bg);
                var need = KitTokens.RequiredContrast(size);
                if (ratio < need) failures.Add($"--{fg} on {bgName}: {ratio:0.00}:1 < {need}:1 at {size} px");
            }
            // Text colours at the smallest size they are used at, on every surface.
            foreach (var (name, colour) in Surfaces())
            {
                foreach (var fg in new[] { "fc-text", "fc-text-2", "fc-accent", "fc-accent-press", "fc-coin", "fc-danger-text", "fc-positive",
                             "fc-rarity-common", "fc-rarity-uncommon", "fc-rarity-rare", "fc-rarity-epic", "fc-rarity-legendary" })
                    Check(fg, name, colour, smallest);
                // Dim text only from 18 px at the reference (the body size) up.
                Check("fc-text-dim", name, colour, body);
            }
            // Dark text on the filled faces: primary, claim, a chosen chip, the upgrade mark.
            foreach (var face in new[] { "fc-accent", "fc-accent-press", "fc-coin", "fc-coin-press", "fc-coin-glow", "fc-text", "fc-text-2" })
                Check("fc-ink", "--" + face, Colour(face), smallest);
            // Disabled primary and claim faces: the label and its reason in text-2 on border-strong.
            Check("fc-text-2", "--fc-border-strong", Colour("fc-border-strong"), smallest);
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        [Test]
        public void TheBriefsDangerRedIsTooDarkForSmallTextSoTextUsesItsOwnToken()
        {
            // Recorded fix (DECISIONS 10): #e0513a reads 4.45:1 on the panel. It stays for borders,
            // the dot and icons (3:1 for graphics); text in danger colour uses --fc-danger-text.
            var panel = Colour("fc-panel");
            Assert.Less(KitTokens.Contrast(Colour("fc-danger"), panel), 4.5f);
            Assert.GreaterOrEqual(KitTokens.Contrast(Colour("fc-danger"), panel), 3f);
            Assert.GreaterOrEqual(KitTokens.Contrast(Colour("fc-danger-text"), Colour("fc-panel-selected")), 4.5f);
            var tail = TokensText.Substring(TokensText.IndexOf("Components.", System.StringComparison.Ordinal));
            Assert.IsFalse(Regex.IsMatch(tail, @"(?<!-)color:\s*var\(--fc-danger\)"), "text never in --fc-danger");
        }

        [Test]
        public void OursAndTheirsDifferInLightnessNotJustHue()
        {
            var ally = KitTokens.Luminance(Colour("fc-ally"));
            var enemy = KitTokens.Luminance(Colour("fc-enemy"));
            Assert.GreaterOrEqual((ally + 0.05f) / (enemy + 0.05f), 1.8f, "ally blue clearly lighter than enemy red");
        }

        /// <summary>
        /// Prompt 14: the out-of-battle type scale and sizes in device points (main button 18-20 pt, screen title
        /// 17-20, panel title 14-15, body 13-14, secondary 11 and nothing under 10; top bar 44-48, rail 72-80 with
        /// 22-24 pt icons, tabs about 40, buttons 40-44, targets 44), Large about 1.2 times, and the battle HUD
        /// keeping its own sizes (prompt 11).
        /// </summary>
        [Test]
        public void TheTypeScaleAndTouchTargetsMatchTheBrief()
        {
            var normal = RootTokens;
            Assert.AreEqual(44f, Points(Kit.TouchTarget), 0.01f, "the checked touch target is 44 pt");
            Assert.That(Points(Px(normal, "fc-fs-primary")), Is.InRange(18f, 20f), "main button 18-20 pt");
            Assert.That(Points(Px(normal, "fc-fs-title")), Is.InRange(17f, 20f), "screen title 17-20 pt");
            Assert.That(Points(Px(normal, "fc-fs-panel-title")), Is.InRange(14f, 15f), "panel title 14-15 pt");
            Assert.That(Points(Px(normal, "fc-fs-body")), Is.InRange(13f, 14f), "body 13-14 pt");
            Assert.That(Points(Px(normal, "fc-fs-small")), Is.InRange(10.5f, 11.5f), "secondary 11 pt");
            foreach (var t in normal.Keys.Where(k => k.StartsWith("fc-fs-")))
                Assert.GreaterOrEqual(Points(Px(normal, t)), 10f, "nothing under 10 pt: --" + t);
            Assert.That(Points(Px(normal, "fc-topbar")), Is.InRange(44f, 48f), "top bar 44-48 pt");
            Assert.That(Points(Px(normal, "fc-nav-width")), Is.InRange(72f, 80f), "rail 72-80 pt");
            Assert.That(Points(Px(normal, "fc-nav-icon")), Is.InRange(22f, 24f), "rail icons 22-24 pt");
            Assert.That(Points(Px(normal, "fc-tab")), Is.InRange(38f, 42f), "tabs about 40 pt");
            Assert.That(Points(Px(normal, "fc-touch")), Is.InRange(44f, 44.8f), "buttons and targets 44 pt");
            Assert.GreaterOrEqual(Px(normal, "fc-touch"), Kit.TouchTarget, "the token reaches the checked minimum");
            // The battle HUD keeps prompt 11's sizes (it scales with the screen, not in points).
            var hud = HudTokens;
            Assert.AreEqual(21f, Px(hud, "fc-fs-body"), "the HUD's body text");
            Assert.AreEqual(82f, Px(hud, "fc-touch"), "the HUD's touch target");
            Assert.That(Reference(Px(normal, "fc-chamfer")), Is.InRange(16.5f, 19.5f), "chamfer about 18");
            Assert.That(Px(normal, "fc-progress"), Is.InRange(3f, 4f), "progress 3-4 px");
            Assert.AreEqual(8f, Px(normal, "fc-dot"));
            Assert.AreEqual(1f, Px(normal, "fc-line"));
            var spacing = Enumerable.Range(1, 7).Select(i => Px(normal, "fc-space-" + i)).ToArray();
            CollectionAssert.AreEqual(new[] { 4f, 8f, 12f, 16f, 20f, 24f, 32f }, spacing);
            // Large: the whole scale about 1.2 times.
            var large = LargeTokens;
            foreach (var t in new[] { "fc-fs-primary", "fc-fs-title", "fc-fs-panel-title", "fc-fs-button", "fc-fs-body", "fc-fs-small", "fc-fs-number", "fc-fs-number-small" })
                Assert.That(Px(large, t) / Px(normal, t), Is.InRange(1.12f, 1.28f), "Large --" + t);
            foreach (var t in large.Keys) Assert.IsTrue(t.StartsWith("fc-fs-"), "Large changes type sizes only: --" + t);
        }

        // ------------------------------------------------------------------ nothing hard-coded

        private static readonly Regex LiteralColour = new(@"#[0-9a-fA-F]{3,8}\b|rgba?\(");
        private static readonly Regex LiteralFontSize = new(@"font-size:(?!\s*var\()");

        [Test]
        public void TheKitsRulesUseTokensOnly()
        {
            var text = TokensText;
            var marker = text.IndexOf("Components. Nothing below", System.StringComparison.Ordinal);
            Assert.Greater(marker, 0, "the components marker");
            var bad = new List<string>();
            var lines = KitTokens.StripComments(text.Substring(marker + 40)).Split('\n');
            foreach (var line in lines)
            {
                if (LiteralColour.IsMatch(line)) bad.Add("colour: " + line.Trim());
                if (LiteralFontSize.IsMatch(line)) bad.Add("font size: " + line.Trim());
                if (Regex.IsMatch(line, @"text-overflow:\s*ellipsis")) bad.Add("ellipsis: " + line.Trim());
                if (Regex.IsMatch(line, @"-unity-font:\s*resource")) bad.Add("font: " + line.Trim());
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        /// <summary>The rebuilt screens' sheet (Screens.uss) holds no literal colour, font size, font file or ellipsis either: tokens only.</summary>
        [Test]
        public void TheScreensRulesUseTokensOnly()
        {
            var text = File.ReadAllText(ProjectPath("Assets/MachineBrigade/Resources/UI/Screens.uss"));
            var bad = new List<string>();
            foreach (var line in KitTokens.StripComments(text).Split('\n'))
            {
                if (LiteralColour.IsMatch(line)) bad.Add("colour: " + line.Trim());
                if (LiteralFontSize.IsMatch(line)) bad.Add("font size: " + line.Trim());
                if (Regex.IsMatch(line, @"text-overflow:\s*ellipsis")) bad.Add("ellipsis: " + line.Trim());
                if (Regex.IsMatch(line, @"-unity-font:\s*resource")) bad.Add("font: " + line.Trim());
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        private static readonly Regex[] CodeColour =
        {
            new(@"new\s+Color\(\s*-?[\d.]+f?\s*,"), new(@"new\s+Color32\("),
            new(@"\bColor\.(white|black|red|green|blue|yellow|cyan|magenta|gray|grey|clear)\b"),
            new("\"#[0-9a-fA-F]{6}"), new(@"<color=#"),
            new(@"\bUiKit\.(Mint|Amber|Danger|Dim)\b"),
            new(@"\.style\.(color|backgroundColor|unityBackgroundImageTintColor|border(Top|Right|Bottom|Left)?Color)\s*="),
        };

        private static readonly Regex CodeFontSize = new(@"\.style\.(fontSize|unityFont|unityFontDefinition)\s*=");
        private static readonly Regex CodeSpacing = new(@"\.style\.(margin|padding)\w*\s*=");

        private static List<string> CodeFindings(IEnumerable<string> files, bool spacing)
        {
            var found = new List<string>();
            foreach (var file in files)
            {
                var lines = File.ReadAllLines(file);
                for (var i = 0; i < lines.Length; i++)
                {
                    var line = lines[i];
                    if (line.TrimStart().StartsWith("//") || line.TrimStart().StartsWith("///")) continue;
                    var what = CodeColour.Any(r => r.IsMatch(line)) ? "colour"
                        : CodeFontSize.IsMatch(line) ? "font size"
                        : spacing && CodeSpacing.IsMatch(line) ? "spacing" : null;
                    if (what != null) found.Add($"{Path.GetFileName(file)}:{i + 1} {what}: {line.Trim()}");
                }
            }
            return found;
        }

        private static string HudFolder => Path.Combine(Application.dataPath, "MachineBrigade", "Scripts", "Game", "Hud");

        [Test]
        public void TheKitsCodeSetsNoColourFontSizeOrSpacing()
        {
            var kit = Directory.GetFiles(Path.Combine(HudFolder, "Kit"), "*.cs")
                .Where(f => Path.GetFileName(f) != "KitTokens.cs"); // the token parser builds colours from the file's values
            var found = CodeFindings(kit, spacing: true);
            Assert.IsEmpty(found, string.Join("\n", found));
        }

        [Test]
        public void OldScreensHardCodedStylesReport()
        {
            var found = CodeFindings(Directory.GetFiles(HudFolder, "*.cs"), spacing: false);
            // Hud.uss: literal colours outside :root blocks and literal font sizes.
            var hud = KitTokens.StripComments(File.ReadAllText(ProjectPath("Assets/MachineBrigade/Resources/UI/Hud.uss")));
            var withoutRoots = Regex.Replace(hud, @":root\s*\{[^}]*\}", "");
            var colours = 0;
            var sizes = 0;
            foreach (var line in withoutRoots.Split('\n'))
            {
                colours += LiteralColour.Matches(line).Count;
                sizes += Regex.Matches(line, @"font-size:\s*[\d.]+px").Count;
            }
            var total = found.Count + colours + sizes;
            Debug.Log($"[UiThemeTests] old screens: {found.Count} hard-coded styles in Hud C#, {colours} literal colours and {sizes} literal font sizes in Hud.uss\n" + string.Join("\n", found));
            if (total > 0)
                Assert.Ignore($"Report only (the screen rebuild fixes these): {found.Count} hard-coded colours/font sizes in the Hud C# files, " +
                              $"{colours} literal colours and {sizes} literal font sizes in Hud.uss. First: " + string.Join(" | ", found.Take(8)));
        }
    }
}
