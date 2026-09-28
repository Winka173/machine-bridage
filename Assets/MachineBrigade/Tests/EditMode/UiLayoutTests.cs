// Needs the UI Toolkit test framework package (com.unity.ui.test-framework); without it the rest of the project still compiles.
#if MB_UI_TEST_FRAMEWORK
using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEditor.UIElements.TestFramework;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Field Command 2.0, laid out on a real panel (the UI test framework's editor panel) at the four
    /// screen shapes (16:9, 19.5:9, 20:9 and a 4:3 tablet, in panel pixels): no text is cut with an
    /// ellipsis or runs out of its box, every tappable element is a full touch target, no text is
    /// smaller than the secondary size, and a screen has at most one primary button. The kit preview
    /// (every page, both languages, both text sizes) must pass strictly; the old menu is measured
    /// and reported for the screen rebuild.
    /// </summary>
    public class UiLayoutTests
    {
        /// <summary>The panel sizes of the four shapes: phones scale with the height (720), a 4:3 tablet with the width (1280).</summary>
        public static readonly (string name, Vector2 size)[] Shapes =
        {
            ("16x9", new Vector2(1280, 720)), ("19.5x9", new Vector2(1560, 720)), ("20x9", new Vector2(1600, 720)), ("4x3", new Vector2(1280, 960)),
        };

        private EditorPanelSimulator _panel;
        private bool _vietnamese;
        private Catalog _catalog;

        [OneTimeSetUp]
        public void LoadCatalog() => _catalog = GameContent.LoadCatalog();

        [SetUp]
        public void CreatePanel()
        {
            _vietnamese = Strings.Vietnamese;
            _panel = new EditorPanelSimulator();
            var root = _panel.rootVisualElement;
            root.styleSheets.Add(Resources.Load<ThemeStyleSheet>("UI/Theme"));
        }

        [TearDown]
        public void ReleasePanel()
        {
            Strings.Vietnamese = _vietnamese;
            _panel.Dispose();
        }

        private void Lay(VisualElement content, Vector2 size)
        {
            var root = _panel.rootVisualElement;
            root.Clear();
            _panel.panelSize = size;
            _panel.ApplyPanelSize();
            content.style.position = Position.Absolute;
            content.style.left = content.style.top = content.style.right = content.style.bottom = 0;
            root.Add(content);
            for (var i = 0; i < 3; i++) _panel.FrameUpdate();
        }

        // ------------------------------------------------------------------ checks

        internal static bool Shown(VisualElement e)
        {
            for (var v = e; v != null; v = v.hierarchy.parent)
                if (v.resolvedStyle.display == DisplayStyle.None || v.resolvedStyle.visibility == Visibility.Hidden) return false;
            var b = e.worldBound;
            return b.width > 0.5f && b.height > 0.5f && !float.IsNaN(b.width);
        }

        internal static string Describe(VisualElement e)
        {
            var path = new List<string>();
            for (var v = e; v != null && path.Count < 4; v = v.hierarchy.parent)
            {
                var cls = v.GetClasses().FirstOrDefault(c => c.StartsWith("fc-") || !c.StartsWith("unity-"));
                path.Add(cls ?? v.GetType().Name);
            }
            path.Reverse();
            return string.Join(">", path);
        }

        /// <summary>
        /// Texts that do not show in full: cut with an ellipsis, one line running out of its box, a
        /// wrapped text squashed shorter than its lines, a word too wide for its box (UI Toolkit then
        /// breaks it inside the word), or a text below the bottom of the screen outside a scroll view.
        /// </summary>
        internal static List<string> CutTexts(VisualElement root, Vector2? screen = null)
        {
            var found = new List<string>();
            root.Query<Label>().ForEach(label =>
            {
                if (string.IsNullOrEmpty(label.text) || !Shown(label)) return;
                var text = label.text;
                var box = label.contentRect;
                if (label.isElided)
                {
                    found.Add($"elided \"{text}\" ({Describe(label)})");
                    return;
                }
                if (label.resolvedStyle.whiteSpace == WhiteSpace.NoWrap)
                {
                    var width = label.MeasureTextSize(text, 0, VisualElement.MeasureMode.Undefined, 0, VisualElement.MeasureMode.Undefined).x;
                    if (width > box.width + 1.5f) found.Add($"cut \"{text}\" {width:0}>{box.width:0} ({Describe(label)})");
                }
                else
                {
                    var height = label.MeasureTextSize(text, box.width, VisualElement.MeasureMode.Exactly, 0, VisualElement.MeasureMode.Undefined).y;
                    if (height > box.height + 1.5f) found.Add($"squashed \"{text}\" {height:0}>{box.height:0} ({Describe(label)})");
                    // A hyphen is a fair place to break ("COUNTER-/BATTERY"); inside a word is not.
                    foreach (var word in System.Text.RegularExpressions.Regex.Split(text, @"\s+|(?<=-)"))
                    {
                        if (word.Length < 2) continue;
                        var w = label.MeasureTextSize(word, 0, VisualElement.MeasureMode.Undefined, 0, VisualElement.MeasureMode.Undefined).x;
                        if (w <= box.width + 1.5f) continue;
                        found.Add($"word broken \"{word}\" {w:0}>{box.width:0} in \"{text}\" ({Describe(label)})");
                        break;
                    }
                }
                if (screen is { } size && label.GetFirstAncestorOfType<ScrollView>() == null &&
                    (label.worldBound.yMax > size.y + 0.5f || label.worldBound.xMax > size.x + 0.5f))
                    found.Add($"off screen \"{text}\" at {label.worldBound.xMax:0},{label.worldBound.yMax:0} ({Describe(label)})");
            });
            return found;
        }

        /// <summary>
        /// Tappable elements (they carry Tap's class) smaller than the touch target on either side. One that takes no
        /// pointer (picking ignored, like the compact boss bar's closed part icons, which only show state) is not a target.
        /// </summary>
        internal static List<string> SmallTargets(VisualElement root, float min)
        {
            var found = new List<string>();
            root.Query(className: Tap.TargetClass).ForEach(e =>
            {
                if (!Shown(e) || e.pickingMode == PickingMode.Ignore) return;
                var b = e.worldBound;
                if (b.width < min - 0.5f || b.height < min - 0.5f) found.Add($"{b.width:0}x{b.height:0} {Describe(e)}");
            });
            return found;
        }

        /// <summary>Texts drawn smaller than the secondary size.</summary>
        internal static List<string> SmallTexts(VisualElement root, float min)
        {
            var found = new List<string>();
            root.Query<Label>().ForEach(label =>
            {
                if (string.IsNullOrEmpty(label.text) || !Shown(label)) return;
                if (label.resolvedStyle.fontSize < min - 0.01f) found.Add($"{label.resolvedStyle.fontSize:0.#} px \"{label.text}\" ({Describe(label)})");
            });
            return found;
        }

        /// <summary>The old menu's amber main-action classes (Hud.uss "menu v5"), and the kit's.</summary>
        private static readonly string[] PrimaryClasses = { KitButton.PrimaryClass, "deploy-button", "campaign-start", "upgrade-big", "shop-buy", "base-save" };

        /// <summary>Primary buttons on screen (a kit preview specimen does not count: it documents a state).</summary>
        internal static int Primaries(VisualElement root)
        {
            // Under an open dialog the page is not the screen any more: count the top dialog's only.
            VisualElement modal = null;
            root.Query(className: KitDialog.ScrimClass).ForEach(scrim =>
            {
                if (Shown(scrim)) modal = scrim;
            });
            if (modal != null) root = modal;
            var count = 0;
            foreach (var cls in PrimaryClasses)
                root.Query(className: cls).ForEach(e =>
                {
                    if (!Shown(e)) return;
                    for (var v = e; v != null; v = v.hierarchy.parent)
                        if (v.ClassListContains(Kit.SpecimenClass)) return;
                    if (cls == "upgrade-big" && !e.ClassListContains("ready")) return;
                    count++;
                });
            return count;
        }

        private static float SmallestText(bool large) => large ? 22f : 19f;

        // ------------------------------------------------------------------ the kit: strict

        [Test]
        public void TheTokensReachTheComponents()
        {
            var preview = new KitPreview(_catalog, null, KitPreview.Page.Tokens, false, false);
            Lay(preview.Root, Shapes[0].size);
            var body = preview.Root.Q<Label>(className: "fc-body");
            Assert.IsNotNull(body);
            Assert.AreEqual(24f, body.resolvedStyle.fontSize, 0.01f, "--fc-fs-body reaches a body label");
            Assert.AreEqual("Barlow-Regular", body.resolvedStyle.unityFont?.name ?? body.resolvedStyle.unityFontDefinition.fontAsset?.name, "--fc-font-text");
            var title = preview.Root.Q<Label>(className: "fc-title");
            Assert.AreEqual("BarlowCondensed-Bold", title.resolvedStyle.unityFont?.name, "--fc-font-display");
            Assert.AreEqual(new Color(0x10 / 255f, 0x13 / 255f, 0x17 / 255f), preview.Root.resolvedStyle.backgroundColor, "--fc-bg");
            preview.Rebuild(KitPreview.Page.Tokens, false, true);
            for (var i = 0; i < 2; i++) _panel.FrameUpdate();
            body = preview.Root.Q<Label>(className: "fc-body");
            Assert.AreEqual(29f, body.resolvedStyle.fontSize, 0.01f, "Large text size");
        }

        /// <summary>Every check on a laid-out screen: cut texts, small targets and texts, primaries, clipping, the screen's edges.</summary>
        internal static List<string> Check(VisualElement root, string name, Vector2 size, bool large, int? primariesExpected = null)
        {
            var failures = new List<string>();
            failures.AddRange(CutTexts(root, size).Select(f => $"{name}: {f}"));
            failures.AddRange(SmallTargets(root, Kit.TouchTarget).Select(f => $"{name}: small target {f}"));
            failures.AddRange(SmallTexts(root, SmallestText(large)).Select(f => $"{name}: small text {f}"));
            var primaries = Primaries(root);
            if (primaries > 1) failures.Add($"{name}: {primaries} primary buttons");
            if (primariesExpected is { } expected && primaries != expected) failures.Add($"{name}: {primaries} primary buttons, not {expected}");
            // Nothing sticks out of the side of a vertical scroll view: it would be clipped, and never scrolls into view.
            root.Query<ScrollView>().ForEach(scroll =>
            {
                if (scroll.mode != ScrollViewMode.Vertical || !Shown(scroll)) return;
                var view = scroll.contentViewport.worldBound;
                scroll.contentContainer.Query<VisualElement>().ForEach(e =>
                {
                    if (e.GetFirstAncestorOfType<ScrollView>() != scroll || !Shown(e)) return;
                    if (e.worldBound.xMax > view.xMax + 0.5f || e.worldBound.xMin < view.xMin - 0.5f)
                        failures.Add($"{name}: clipped at the side of a scroll view: {Describe(e)} {e.worldBound.xMin:0}-{e.worldBound.xMax:0} outside {view.xMin:0}-{view.xMax:0}");
                });
            });
            // Nothing hangs off the edge of the screen (outside a scroll view).
            root.Query(className: Tap.TargetClass).ForEach(e =>
            {
                if (Shown(e) && (e.worldBound.xMax > size.x + 0.5f || e.worldBound.yMax > size.y + 0.5f) && e.GetFirstAncestorOfType<ScrollView>() == null)
                    failures.Add($"{name}: off screen {Describe(e)} at {e.worldBound.xMax:0},{e.worldBound.yMax:0}");
            });
            return failures;
        }

        [Test]
        public void EveryKitPreviewPagePassesEveryCheck(
            [Values] KitPreview.Page page, [Values(false, true)] bool vietnamese, [Values(false, true)] bool large)
        {
            var failures = new List<string>();
            foreach (var (name, size) in Shapes)
            {
                var preview = new KitPreview(_catalog, null, page, vietnamese, large);
                Lay(preview.Root, size);
                failures.AddRange(Check(preview.Root, name, size, large, page == KitPreview.Page.Sample ? 1 : null));
            }
            Assert.IsEmpty(failures, string.Join("\n", failures.Distinct()));
        }

        [Test]
        public void TheChecksCatchCutTextsSmallTargetsAndExtraPrimaries()
        {
            var host = Kit.Root("fc-screen");
            var elided = Kit.Body("A label far too long for its box");
            elided.style.width = 60;
            elided.style.whiteSpace = WhiteSpace.NoWrap;
            elided.style.textOverflow = TextOverflow.Ellipsis;
            elided.style.overflow = Overflow.Hidden;
            host.Add(elided);
            var word = Kit.Body("Unbreakablewordhere");
            word.style.width = 50;
            host.Add(word);
            var small = UiKit.Button("tiny", null);
            small.style.width = small.style.height = 40;
            host.Add(small);
            host.Add(new KitButton(ButtonTier.Primary, "One", null));
            host.Add(new KitButton(ButtonTier.Primary, "Two", null));
            Lay(host, Shapes[0].size);
            var cut = CutTexts(host, Shapes[0].size);
            Assert.IsTrue(cut.Any(c => c.StartsWith("elided") || c.StartsWith("cut")), string.Join(" | ", cut));
            Assert.IsTrue(cut.Any(c => c.StartsWith("word broken")), string.Join(" | ", cut));
            Assert.AreEqual(1, SmallTargets(host, Kit.TouchTarget).Count);
            Assert.AreEqual(2, Primaries(host));
        }

        [Test]
        public void TheOldStylesheetReadsTheAccentFromTheTokens()
        {
            var hud = Kit.Box("hud");
            hud.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
            var menu = Kit.Box("menu");
            var tab = Kit.Box("nav-tab chosen");
            menu.Add(tab);
            hud.Add(menu);
            Lay(hud, Shapes[0].size);
            Assert.AreEqual("F2A33A", ColorUtility.ToHtmlStringRGB(tab.resolvedStyle.borderLeftColor), "--accent: var(--fc-accent) resolves");
        }

        [Test]
        public void TheUpgradeMarkShowsOnlyWhenAffordableAndLockedCardsSayWhere()
        {
            var ready = new KitVehicleCard(new VehicleCardData { Id = "mlrs", Name = "MLRS", CanUpgrade = true });
            var notReady = new KitVehicleCard(new VehicleCardData { Id = "mlrs", Name = "MLRS", CanUpgrade = false });
            var locked = new KitVehicleCard(new VehicleCardData { Id = "mlrs", Name = "MLRS", CanUpgrade = true, Locked = true, UnlockWhere = "Unlocks in Chapter 3" });
            Assert.IsNotNull(ready.Q(className: "fc-vcard__upgrade"));
            Assert.IsNull(notReady.Q(className: "fc-vcard__upgrade"));
            Assert.IsNull(locked.Q(className: "fc-vcard__upgrade"), "a locked card has nothing to upgrade");
            var host = Kit.Root("fc-screen");
            host.Add(locked);
            Lay(host, Shapes[0].size);
            Assert.AreEqual(0.45f, locked.Q(className: "fc-vcard__content").resolvedStyle.opacity, 0.001f, "locked cards at 45 %");
            Assert.AreEqual(1f, locked.Q(className: "fc-vcard__lock").resolvedStyle.opacity, 0.001f, "the unlock line stays legible");
            Assert.AreEqual("Unlocks in Chapter 3", locked.Q<Label>(className: "fc-vcard__lock-text").text);
        }

        [Test]
        public void GearSortsAndFiltersBySlotRarityAndBrand()
        {
            var items = new List<GearItem>
            {
                new() { id = 1, slot = 0, rarity = 1, level = 3, brand = 2 }, new() { id = 2, slot = 1, rarity = 4, level = 1, brand = 1 },
                new() { id = 3, slot = 0, rarity = 4, level = 9, brand = 2 }, new() { id = 4, slot = 2, rarity = 0, level = 12, brand = 3 },
            };
            CollectionAssert.AreEqual(new[] { 3, 2, 1, 4 }, GearQuery.Sorted(items, GearQuery.Sort.Rarity).Select(i => i.id));
            CollectionAssert.AreEqual(new[] { 4, 3, 1, 2 }, GearQuery.Sorted(items, GearQuery.Sort.Level).Select(i => i.id));
            CollectionAssert.AreEqual(new[] { 1, 3 }, GearQuery.Filter(items, slot: (GearSlot)0).Select(i => i.id));
            CollectionAssert.AreEqual(new[] { 2, 3 }, GearQuery.Filter(items, rarity: 4).Select(i => i.id));
            CollectionAssert.AreEqual(new[] { 1, 3 }, GearQuery.Filter(items, brand: 2).Select(i => i.id));
        }

        [Test]
        public void TheSafeAreaInsetsFollowTheNotch()
        {
            // A 2340 x 1080 phone with a 90 px notch on the left and the gesture bar's 40 px at the bottom, on a 1560 x 720 panel.
            var insets = KitSafeArea.Insets(new Rect(90, 40, 2340 - 90, 1080 - 40), new Vector2(2340, 1080), new Vector2(1560, 720));
            Assert.AreEqual(60f, insets.x, 0.01f);
            Assert.AreEqual(0f, insets.y, 0.01f);
            Assert.AreEqual(0f, insets.z, 0.01f);
            Assert.AreEqual(26.67f, insets.w, 0.01f);
        }

        // ------------------------------------------------------------------ the rebuilt menu screens: strict

        public static IEnumerable<string> MenuScreenNames => MenuScreen.ScreenNames;

        /// <summary>The screens with one main action (the rest, lists and settings, have none).</summary>
        private static readonly HashSet<string> WithPrimary = new()
        {
            "home", "campaign-chapter", "briefing", "operations", "detail", "detail-tower", "detail-module", "detail-action", "detail-tower-action", "detail-module-action",
            "shop-skins", "shop-units", "shop-items",
        };

        /// <summary>
        /// Every rebuilt menu screen, with the demo profile: in Vietnamese at the four shapes, and in
        /// Large text and in English at 16:9, passes every check.
        /// </summary>
        [Test]
        public void EveryRebuiltScreenPassesEveryCheck([ValueSource(nameof(MenuScreenNames))] string screen)
        {
            var failures = new List<string>();
            var textSize = MatchSettings.TextSize;
            DemoProfile.Use();
            try
            {
                foreach (var (vietnamese, large, shapes) in new[] { (true, false, Shapes), (true, true, new[] { Shapes[0] }), (false, false, new[] { Shapes[0] }) })
                    foreach (var (name, size) in shapes)
                    {
                        Strings.Vietnamese = vietnamese;
                        MatchSettings.TextSize = large ? TextSize.Large : TextSize.Normal;
                        var host = MachineBrigade.Editor.UiShots.BuildMenu(_catalog, screen, out _);
                        Lay(host, size);
                        var label = $"{name}{(vietnamese ? "" : " en")}{(large ? " large" : "")}";
                        failures.AddRange(Check(host, label, size, large, WithPrimary.Contains(screen) ? 1 : 0));
                    }
            }
            finally
            {
                MatchSettings.TextSize = textSize;
                DemoProfile.Restore();
            }
            Assert.IsEmpty(failures, string.Join("\n", failures.Distinct().Take(60)));
        }

        public static IEnumerable<string> BattleScreenNames => MachineBrigade.Editor.UiShots.BattleScreenNames;

        /// <summary>The battle's screens (the HUD, the result, pause, the choice between stages), like the menu's: each overlay has its one main action, the HUD none.</summary>
        [Test]
        public void EveryBattleScreenPassesEveryCheck([ValueSource(nameof(BattleScreenNames))] string screen)
        {
            var failures = new List<string>();
            var textSize = MatchSettings.TextSize;
            DemoProfile.Use();
            try
            {
                foreach (var (vietnamese, large, shapes) in new[] { (true, false, Shapes), (true, true, new[] { Shapes[0] }), (false, false, new[] { Shapes[0] }) })
                    foreach (var (name, size) in shapes)
                    {
                        Strings.Vietnamese = vietnamese;
                        MatchSettings.TextSize = large ? TextSize.Large : TextSize.Normal;
                        var host = MachineBrigade.Editor.UiShots.BuildBattle(_catalog, screen, out _);
                        Lay(host, size);
                        var label = $"{name}{(vietnamese ? "" : " en")}{(large ? " large" : "")}";
                        failures.AddRange(Check(host, label, size, large, MachineBrigade.Editor.UiShots.WithoutPrimary(screen) ? 0 : 1));
                    }
            }
            finally
            {
                MatchSettings.TextSize = textSize;
                DemoProfile.Restore();
            }
            Assert.IsEmpty(failures, string.Join("\n", failures.Distinct().Take(60)));
        }

        // ------------------------------------------------------------------ prompt 11: the compact HUD, cards in line

        /// <summary>
        /// The share of the screen the HUD's drawn frames cover: the union (on a 4 px grid) of every shown element with
        /// a fill, an image or a border, every text and icon, and the minimap. Invisible touch targets do not count.
        /// </summary>
        internal static float Cover(VisualElement hud, Vector2 size)
        {
            const int cell = 4;
            var w = Mathf.CeilToInt(size.x / cell);
            var h = Mathf.CeilToInt(size.y / cell);
            var covered = new bool[w * h];
            hud.Query<VisualElement>().ForEach(e =>
            {
                if (!Shown(e) || !Opaque(e) || !Drawn(e)) return;
                var b = e.worldBound;
                int x0 = Mathf.Clamp(Mathf.FloorToInt(b.xMin / cell), 0, w), x1 = Mathf.Clamp(Mathf.CeilToInt(b.xMax / cell), 0, w);
                int y0 = Mathf.Clamp(Mathf.FloorToInt(b.yMin / cell), 0, h), y1 = Mathf.Clamp(Mathf.CeilToInt(b.yMax / cell), 0, h);
                for (var y = y0; y < y1; y++)
                    for (var x = x0; x < x1; x++) covered[y * w + x] = true;
            });
            return covered.Count(c => c) / (float)covered.Length;
        }

        private static bool Opaque(VisualElement e)
        {
            for (var v = e; v != null; v = v.hierarchy.parent)
                if (v.resolvedStyle.opacity < 0.05f) return false;
            return true;
        }

        private static bool Drawn(VisualElement e)
        {
            var s = e.resolvedStyle;
            if (s.backgroundColor.a > 0.05f) return true;
            var bg = s.backgroundImage;
            if (bg.texture != null || bg.sprite != null || bg.renderTexture != null || bg.vectorImage != null) return true;
            if ((s.borderTopWidth > 0f && s.borderTopColor.a > 0.05f) || (s.borderLeftWidth > 0f && s.borderLeftColor.a > 0.05f) ||
                (s.borderRightWidth > 0f && s.borderRightColor.a > 0.05f) || (s.borderBottomWidth > 0f && s.borderBottomColor.a > 0.05f)) return true;
            if (e is Label label) return !string.IsNullOrEmpty(label.text);
            return e is IconElement || e is Minimap;
        }

        /// <summary>
        /// Prompt 11 A: in a fight the compact HUD's frames cover at most 30 % of the screen at 16:9 and 20:9 (the
        /// brief's 25-30 %), in Conquest (a selection open), a boss battle (the boss bar, a notice), Siege and Defend.
        /// The full HUD is measured beside it and reported.
        /// </summary>
        [Test]
        public void TheCompactHudLeavesTheBattlefieldClear()
        {
            var report = new List<string>();
            var failures = new List<string>();
            var textSize = MatchSettings.TextSize;
            DemoProfile.Use();
            try
            {
                Strings.Vietnamese = true;
                MatchSettings.TextSize = TextSize.Normal;
                foreach (var screen in new[] { "hud-score", "hud-mission", "hud-siege", "hud-defend" })
                    foreach (var (name, size) in new[] { Shapes[0], Shapes[2] })
                        foreach (var full in new[] { false, true })
                        {
                            var host = MachineBrigade.Editor.UiShots.BuildBattle(_catalog, screen + (full ? "-full" : ""), out _);
                            Lay(host, size);
                            var cover = Cover(host.Q(className: "fc-hud"), size);
                            report.Add($"{screen}{(full ? " full" : "")} {name} {cover * 100f:0.0}%");
                            if (!full && cover > 0.30f) failures.Add($"{screen} {name}: the HUD covers {cover * 100f:0.0}% of the screen (at most 30%)");
                        }
            }
            finally
            {
                MatchSettings.TextSize = textSize;
                DemoProfile.Restore();
            }
            Debug.Log("[HudCover] " + string.Join(" | ", report));
            Assert.IsEmpty(failures, string.Join("\n", failures) + "\n" + string.Join("\n", report));
        }

        /// <summary>Each card kind and the parts that must sit in the same place on every card of a row (the cost box by its top right).</summary>
        private static readonly (string card, string[] parts)[] CardParts =
        {
            ("fc-vcard", new[] { "fc-vcard__art", "fc-vcard__cp", "fc-vcard__name", "fc-vcard__level" }),
            ("fc-gcard", new[] { "fc-gcard__art", "fc-gcard__level", "fc-gcard__name", "fc-gcard__stat" }),
            ("fc-hcard", new[] { "fc-hcard__art", "fc-hcard__cost", "fc-hcard__name" }),
        };

        private static bool RightAnchored(string part) => part is "fc-vcard__cp" or "fc-hcard__cost";

        /// <summary>
        /// Cards out of line (prompt 11 B2, B5): in each row or grid (the cards of one parent), the picture, the cost,
        /// the name area and the level sit at the same place relative to every card, the name areas are one height, and
        /// cards side by side share their top and their height.
        /// </summary>
        internal static List<string> Misaligned(VisualElement root)
        {
            var found = new List<string>();
            foreach (var (cardClass, parts) in CardParts)
            {
                var groups = new Dictionary<VisualElement, List<VisualElement>>();
                root.Query(className: cardClass).ForEach(c =>
                {
                    if (!Shown(c) || c.hierarchy.parent == null) return;
                    if (!groups.TryGetValue(c.hierarchy.parent, out var list)) groups[c.hierarchy.parent] = list = new List<VisualElement>();
                    list.Add(c);
                });
                foreach (var group in groups.Values)
                {
                    if (group.Count < 2) continue;
                    for (var i = 0; i < group.Count; i++)
                        for (var j = i + 1; j < group.Count; j++)
                        {
                            var a = group[i].worldBound;
                            var b = group[j].worldBound;
                            var dy = Mathf.Abs(a.yMin - b.yMin);
                            var sameRow = dy < Mathf.Min(a.height, b.height) * 0.5f;
                            if (sameRow && dy > 0.5f) found.Add($"{Describe(group[j])}: top {b.yMin:0} beside {a.yMin:0}");
                            else if (sameRow && Mathf.Abs(a.height - b.height) > 0.5f) found.Add($"{Describe(group[j])}: height {b.height:0} beside {a.height:0}");
                        }
                    foreach (var part in parts)
                    {
                        Rect? reference = null;
                        foreach (var card in group)
                        {
                            var q = card.Q(className: part);
                            if (q == null || !Shown(q)) continue;
                            var c = card.worldBound;
                            var p = q.worldBound;
                            var at = new Rect(RightAnchored(part) ? c.xMax - p.xMax : p.xMin - c.xMin, p.yMin - c.yMin, p.width, p.height);
                            if (reference is not { } r)
                            {
                                reference = at;
                                continue;
                            }
                            var fixedHeight = part.EndsWith("__art") || part.EndsWith("__name");
                            if (Mathf.Abs(at.x - r.x) > 0.5f || Mathf.Abs(at.y - r.y) > 0.5f || (fixedHeight && Mathf.Abs(at.height - r.height) > 0.5f))
                                found.Add($"{Describe(card)} {part}: at {at.x:0},{at.y:0} ({at.height:0} high), not {r.x:0},{r.y:0} ({r.height:0})");
                        }
                    }
                }
            }
            return found;
        }

        /// <summary>
        /// Prompt 14 A5: at 16:9 and 20:9 the main content of every out-of-battle screen (the shown page, less a row of
        /// tabs across its top) covers at least 70 % of the screen: the top bar, the rail and the tabs take the rest.
        /// </summary>
        [Test]
        public void TheContentKeepsSeventyPercentOfTheScreen()
        {
            var failures = new List<string>();
            var report = new List<string>();
            var textSize = MatchSettings.TextSize;
            DemoProfile.Use();
            try
            {
                Strings.Vietnamese = true;
                MatchSettings.TextSize = TextSize.Normal;
                foreach (var screen in MenuScreen.ScreenNames)
                    foreach (var (name, size) in new[] { Shapes[0], Shapes[2] })
                    {
                        var host = MachineBrigade.Editor.UiShots.BuildMenu(_catalog, screen, out _);
                        Lay(host, size);
                        var share = ContentShare(host, size);
                        report.Add($"{screen} {name} {share * 100f:0.0}%");
                        if (share < 0.695f) failures.Add($"{screen} {name}: content {share * 100f:0.0}% of the screen (70% wanted)");
                    }
            }
            finally
            {
                MatchSettings.TextSize = textSize;
                DemoProfile.Restore();
            }
            Debug.Log("[ContentShare] " + string.Join(" | ", report));
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        /// <summary>The top shown page's area less the row of tabs along its top, over the screen's.</summary>
        internal static float ContentShare(VisualElement root, Vector2 size)
        {
            VisualElement page = null;
            root.Query(className: "fc-page").ForEach(p =>
            {
                if (Shown(p)) page = p;
            });
            if (page == null) return 0f;
            var area = page.worldBound;
            var top = area.yMin;
            page.Query(className: "fc-tabs").ForEach(t =>
            {
                if (Shown(t) && t.worldBound.yMin <= top + 1f && t.worldBound.width > area.width * 0.5f) top = Mathf.Max(top, t.worldBound.yMax);
            });
            var height = Mathf.Max(0f, Mathf.Min(area.yMax, size.y) - top);
            var width = Mathf.Max(0f, Mathf.Min(area.xMax, size.x) - Mathf.Max(0f, area.xMin));
            return width * height / (size.x * size.y);
        }

        /// <summary>The screens with rows of cards: the deck strips, the collection, towers, equipment, a chapter's unlocks, the battle's tray.</summary>
        private static readonly string[] CardScreens = { "home", "army-deck", "army-towers", "army-gear", "campaign-chapter", "operations" };

        /// <summary>Prompt 11 B5: on every screen with cards, at the four shapes in Normal and Large text, every card of a row lines up.</summary>
        [Test]
        public void CardsInARowLineUp()
        {
            var failures = new List<string>();
            var textSize = MatchSettings.TextSize;
            DemoProfile.Use();
            try
            {
                Strings.Vietnamese = true;
                foreach (var large in new[] { false, true })
                {
                    MatchSettings.TextSize = large ? TextSize.Large : TextSize.Normal;
                    foreach (var (name, size) in Shapes)
                    {
                        var label = $"{name}{(large ? " large" : "")}";
                        foreach (var screen in CardScreens)
                        {
                            var host = MachineBrigade.Editor.UiShots.BuildMenu(_catalog, screen, out _);
                            Lay(host, size);
                            failures.AddRange(Misaligned(host).Select(f => $"{screen} {label}: {f}"));
                        }
                        foreach (var screen in new[] { "hud-score", "hud-score-full" })
                        {
                            var host = MachineBrigade.Editor.UiShots.BuildBattle(_catalog, screen, out _);
                            Lay(host, size);
                            failures.AddRange(Misaligned(host).Select(f => $"{screen} {label}: {f}"));
                        }
                    }
                }
            }
            finally
            {
                MatchSettings.TextSize = textSize;
                DemoProfile.Restore();
            }
            Assert.IsEmpty(failures, string.Join("\n", failures.Distinct().Take(60)));
        }
    }
}
#endif
