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

        /// <summary>Tappable elements (they carry Tap's class) smaller than the touch target on either side.</summary>
        internal static List<string> SmallTargets(VisualElement root, float min)
        {
            var found = new List<string>();
            root.Query(className: Tap.TargetClass).ForEach(e =>
            {
                if (!Shown(e)) return;
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
        private static readonly string[] PrimaryClasses = { KitButton.PrimaryClass, "deploy-button", "campaign-start", "upgrade-big", "shop-buy" };

        /// <summary>Primary buttons on screen (a kit preview specimen does not count: it documents a state).</summary>
        internal static int Primaries(VisualElement root)
        {
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
            Assert.AreEqual(21f, body.resolvedStyle.fontSize, 0.01f, "--fc-fs-body reaches a body label");
            Assert.AreEqual("Barlow-Regular", body.resolvedStyle.unityFont?.name ?? body.resolvedStyle.unityFontDefinition.fontAsset?.name, "--fc-font-text");
            var title = preview.Root.Q<Label>(className: "fc-title");
            Assert.AreEqual("BarlowCondensed-Bold", title.resolvedStyle.unityFont?.name, "--fc-font-display");
            Assert.AreEqual(new Color(0x10 / 255f, 0x13 / 255f, 0x17 / 255f), preview.Root.resolvedStyle.backgroundColor, "--fc-bg");
            preview.Rebuild(KitPreview.Page.Tokens, false, true);
            for (var i = 0; i < 2; i++) _panel.FrameUpdate();
            body = preview.Root.Q<Label>(className: "fc-body");
            Assert.AreEqual(24f, body.resolvedStyle.fontSize, 0.01f, "Large text size");
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
                var root = preview.Root;
                failures.AddRange(CutTexts(root, size).Select(f => $"{name}: {f}"));
                failures.AddRange(SmallTargets(root, Kit.TouchTarget).Select(f => $"{name}: small target {f}"));
                failures.AddRange(SmallTexts(root, SmallestText(large)).Select(f => $"{name}: small text {f}"));
                var primaries = Primaries(root);
                if (primaries > 1) failures.Add($"{name}: {primaries} primary buttons");
                if (page == KitPreview.Page.Sample && primaries != 1) failures.Add($"{name}: the sample screen has {primaries} primary buttons, not one");
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

        // ------------------------------------------------------------------ the old menu: report only

        [Test]
        public void OldMenuScreensReport()
        {
            PlayerProfile.LoadForTests("{}");
            var lines = new List<string>();
            var counts = new Dictionary<string, int> { ["cut"] = 0, ["small target"] = 0, ["small text"] = 0, ["over one primary"] = 0 };
            try
            {
                foreach (var large in new[] { false, true })
                {
                    var hud = Kit.Box("hud");
                    hud.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
                    Kit.ApplyTextSize(hud, large);
                    MenuScreen menu;
                    try
                    {
                        menu = new MenuScreen(_catalog, null);
                    }
                    catch (Exception e)
                    {
                        Assert.Ignore("Report only: the old menu could not be built without a scene (" + e.GetType().Name + ": " + e.Message + ")");
                        return;
                    }
                    hud.Add(menu.Root);
                    Lay(hud, Shapes[0].size);
                    foreach (MenuScreen.Tab tab in Enum.GetValues(typeof(MenuScreen.Tab)))
                    {
                        menu.ShowTab(tab);
                        for (var i = 0; i < 2; i++) _panel.FrameUpdate();
                        var where = $"{tab}{(large ? " (Large)" : "")}";
                        void Add(string kind, IEnumerable<string> found)
                        {
                            foreach (var f in found)
                            {
                                counts[kind]++;
                                lines.Add($"{where} {kind}: {f}");
                            }
                        }
                        Add("cut", CutTexts(hud, Shapes[0].size));
                        Add("small target", SmallTargets(hud, Kit.TouchTarget));
                        Add("small text", SmallTexts(hud, SmallestText(false)));
                        var primaries = Primaries(hud);
                        if (primaries > 1) Add("over one primary", new[] { primaries + " primary buttons" });
                    }
                }
            }
            finally
            {
                PlayerProfile.Load();
            }
            Debug.Log("[UiLayoutTests] old menu at 16:9\n" + string.Join("\n", lines));
            if (lines.Count > 0)
                Assert.Ignore("Report only (the screen rebuild fixes these), the five tabs at 16:9 in Normal and Large: " +
                              string.Join(", ", counts.Select(p => $"{p.Value} {p.Key}")));
        }
    }
}
#endif
