using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UIElements;
using UnityEngine.UIElements.TestFramework;
using Object = UnityEngine.Object;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Screenshots of UI Toolkit screens at the four screen shapes of the brief (16:9, 19.5:9 with a
    /// notch, 20:9 with a punch-hole camera and the gesture bar, a 4:3 tablet), rendered through a
    /// runtime panel with the game's panel settings (1280 x 720 reference, scaled like
    /// BattleHud.MatchFor) into Docs/ui-screens/. Batch mode with graphics:
    /// -executeMethod MachineBrigade.Editor.UiShots.KitScreens [-mbShotsDir &lt;folder&gt;].
    /// The screen rebuild adds its screens to <see cref="Screens"/>.
    /// </summary>
    public static class UiShots
    {
        public readonly struct Shape
        {
            public Shape(string name, int width, int height, Rect? safeArea = null)
            {
                Name = name;
                Width = width;
                Height = height;
                SafeArea = safeArea ?? new Rect(0, 0, width, height);
            }

            public string Name { get; }
            public int Width { get; }
            public int Height { get; }

            /// <summary>The safe area in screen pixels (origin bottom-left), as Screen.safeArea gives it.</summary>
            public Rect SafeArea { get; }
        }

        /// <summary>
        /// The four shapes, at 1080 px tall: a plain 16:9; a 19.5:9 phone with a 96 px notch on the left;
        /// a 20:9 phone with a punch-hole camera (a 72 px inset on the left) and the gesture bar
        /// (36 px at the bottom); a 4:3 tablet.
        /// </summary>
        public static readonly Shape[] Shapes =
        {
            new("16x9", 1920, 1080),
            new("19.5x9-notch", 2340, 1080, new Rect(96, 0, 2340 - 96, 1080)),
            new("20x9-punchhole", 2400, 1080, new Rect(72, 36, 2400 - 72, 1080 - 36)),
            new("4x3", 1440, 1080),
        };

        private static string Argument(string name)
        {
            var args = Environment.GetCommandLineArgs();
            for (var i = 0; i < args.Length - 1; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }

        public static string OutputFolder()
        {
            var args = Environment.GetCommandLineArgs();
            for (var i = 0; i < args.Length - 1; i++)
                if (args[i] == "-mbShotsDir") return args[i + 1];
            return Path.GetFullPath(Path.Combine(Application.dataPath, "..", "Docs", "ui-screens"));
        }

        /// <summary>A screen to photograph: its file name and a builder that returns its root (and an optional hook to set the safe area).</summary>
        public delegate VisualElement Builder(out Action<Vector4> setInsets);

        public static IEnumerable<(string file, Builder build, Shape[] shapes, int tallHeight)> Screens()
        {
            var catalog = GameContent.LoadCatalog();
            Builder Kit(KitPreview.Page page, bool vi, bool large) => (out Action<Vector4> insets) =>
            {
                var preview = new KitPreview(catalog, null, page, vi, large);
                insets = preview.SetSafeInsets;
                return preview.Root;
            };
            foreach (KitPreview.Page page in Enum.GetValues(typeof(KitPreview.Page)))
            {
                var name = "kit-" + page.ToString().ToLowerInvariant();
                yield return (name + "-vi", Kit(page, true, false), Shapes, 0);
                yield return (name + "-vi-large", Kit(page, true, true), new[] { Shapes[0] }, 0);
                if (page != KitPreview.Page.Sample) yield return (name + "-vi-full", Kit(page, true, false), new[] { Shapes[0] }, 1);
            }
            yield return ("kit-buttons-en", Kit(KitPreview.Page.Buttons, false, false), new[] { Shapes[0] }, 0);
            yield return ("kit-sample-en", Kit(KitPreview.Page.Sample, false, false), new[] { Shapes[0] }, 0);
        }

        /// <summary>
        /// The rebuilt menu screens (MenuScreen.ScreenNames) with the demo profile, in Vietnamese at the
        /// four shapes, and a few in Large text and in English. Home's live battle is stood in for
        /// by its battlefield's picture.
        /// </summary>
        public static IEnumerable<(string file, Builder build, Shape[] shapes, int tallHeight)> MenuScreens()
        {
            var catalog = GameContent.LoadCatalog();
            Builder Menu(string screen, bool vi, bool large) => (out Action<Vector4> insets) =>
            {
                Strings.Vietnamese = vi;
                MatchSettings.TextSize = large ? TextSize.Large : TextSize.Normal;
                DemoProfile.Use();
                var host = BuildMenu(catalog, screen, out var safe);
                insets = v => KitSafeArea.Apply(safe, v);
                return host;
            };
            foreach (var screen in MenuScreen.ScreenNames) yield return ("screen-" + screen + "-vi", Menu(screen, true, false), Shapes, 0);
            foreach (var screen in new[] { "home", "campaign-chapter", "army-deck", "detail", "settings", "shop-crates" })
            {
                yield return ("screen-" + screen + "-vi-large", Menu(screen, true, true), new[] { Shapes[0] }, 0);
                yield return ("screen-" + screen + "-en", Menu(screen, false, false), new[] { Shapes[0] }, 0);
            }
        }

        /// <summary>The menu as BattleHud lays it out (the old HUD sheet on the root, the backdrop under the safe area), opened on a screen.</summary>
        public static VisualElement BuildMenu(Catalog catalog, string screen, out VisualElement safe)
        {
            var host = new VisualElement();
            host.AddToClassList("hud");
            host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Hud"));
            host.styleSheets.Add(Resources.Load<StyleSheet>("UI/Screens"));
            var battle = new VisualElement();
            battle.style.position = Position.Absolute;
            battle.style.left = battle.style.top = battle.style.right = battle.style.bottom = 0;
            if (MapArt.For(MatchSettings.CurrentMap.Id) is { } picture) battle.style.backgroundImage = Background.FromTexture2D(picture);
            battle.style.unityBackgroundScaleMode = ScaleMode.ScaleAndCrop;
            host.Add(battle);
            var menu = new MenuScreen(catalog, () => { });
            host.Add(menu.Backdrop);
            safe = new VisualElement();
            safe.style.position = Position.Absolute;
            safe.style.left = safe.style.top = safe.style.right = safe.style.bottom = 0;
            safe.Add(menu.Root);
            host.Add(safe);
            menu.DebugShow(screen);
            return host;
        }

        [MenuItem("Machine Brigade/UI Screenshots")]
        public static void KitScreens()
        {
            if (SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            {
                Debug.LogError("[UiShots] needs a graphics device: run the batch without -nographics.");
                return;
            }
            var folder = OutputFolder();
            Directory.CreateDirectory(folder);
            var was = Strings.Vietnamese;
            var textSize = MatchSettings.TextSize;
            var set = Argument("-mbShotsSet") ?? "all";
            var list = new List<(string file, Builder build, Shape[] shapes, int tallHeight)>();
            if (set is "all" or "kit") list.AddRange(Screens());
            if (set is "all" or "menu") list.AddRange(MenuScreens());
            var only = Argument("-mbShotsOnly");
            if (only != null) list = list.FindAll(s => s.file.Contains(only));
            var count = 0;
            try
            {
                var onlyShape = Argument("-mbShotsShape");
                foreach (var (file, build, shapes, tall) in list)
                    foreach (var shape in shapes)
                    {
                        if (onlyShape != null && !shape.Name.StartsWith(onlyShape)) continue;
                        var suffix = shapes.Length > 1 ? "-" + shape.Name : tall > 0 ? "" : "-" + shape.Name;
                        var path = Path.Combine(folder, file + suffix + ".png");
                        File.WriteAllBytes(path, Shoot(build, shape, tall > 0));
                        count++;
                    }
            }
            finally
            {
                Strings.Vietnamese = was;
                MatchSettings.TextSize = textSize;
                DemoProfile.Restore();
            }
            Debug.Log($"[UiShots] wrote {count} screenshots to {folder}");
        }

        /// <summary>
        /// Lays a screen out on a runtime panel of the shape and renders it. A tall shot first lays the
        /// page out at 16:9, then grows the panel to the page's full scroll height, so everything on a
        /// long page shows at once (at the panel's own scale).
        /// </summary>
        public static byte[] Shoot(Builder build, Shape shape, bool tall)
        {
            var width = shape.Width;
            var height = shape.Height;
            var root = build(out var setInsets);
            if (tall)
            {
                // One layout pass at the reference size to find the page's height.
                var probe = Render(root, 1280, 720, shape, setInsets, measureOnly: true, out var full);
                Object.DestroyImmediate(probe);
                width = 1280;
                height = Mathf.Clamp(Mathf.CeilToInt(full), 720, 6000);
                root = build(out setInsets);
                return Render(root, width, height, shape, setInsets, measureOnly: false, out _, scrollOpen: true).EncodeToPNG();
            }
            return Render(root, width, height, shape, setInsets, measureOnly: false, out _).EncodeToPNG();
        }

        private static Texture2D Render(VisualElement root, int width, int height, Shape shape, Action<Vector4> setInsets, bool measureOnly,
            out float contentHeight, bool scrollOpen = false)
        {
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32) { name = "UI Shot" };
            rt.Create();
            var settings = ScriptableObject.CreateInstance<PanelSettings>();
            settings.themeStyleSheet = Resources.Load<ThemeStyleSheet>("UI/Theme");
            settings.scaleMode = PanelScaleMode.ScaleWithScreenSize;
            settings.referenceResolution = new Vector2Int(1280, 720);
            settings.screenMatchMode = PanelScreenMatchMode.MatchWidthOrHeight;
            settings.match = scrollOpen ? 0f : Mathf.Clamp01((width / (float)height - 4f / 3f) / (16f / 9f - 4f / 3f));
            settings.targetTexture = rt;
            settings.clearColor = true;
            settings.colorClearValue = Color.black;
            var simulator = new RuntimePanelSimulator(settings) { needsRendering = true };
            var panelRoot = simulator.rootVisualElement;
            root.style.position = Position.Absolute;
            root.style.left = root.style.top = root.style.right = root.style.bottom = 0;
            panelRoot.Add(root);
            for (var i = 0; i < 3; i++) simulator.FrameUpdate();
            // The shape's safe area, in panel pixels.
            var panelSize = panelRoot.layout.size;
            setInsets?.Invoke(KitSafeArea.Insets(shape.SafeArea, new Vector2(shape.Width, shape.Height), panelSize));
            for (var i = 0; i < 3; i++) simulator.FrameUpdate();
            contentHeight = 0f;
            var scroll = root.Q<ScrollView>();
            if (scroll != null)
                contentHeight = panelSize.y + Mathf.Max(0f, scroll.contentContainer.layout.height - scroll.contentViewport.layout.height) + 8f;
            Texture2D shot = null;
            if (!measureOnly)
            {
                // Two more frames so fonts and images that load on the first draw are in.
                for (var i = 0; i < 4; i++) simulator.FrameUpdate();
                var active = RenderTexture.active;
                RenderTexture.active = rt;
                shot = new Texture2D(width, height, TextureFormat.RGB24, false);
                shot.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                shot.Apply(false);
                RenderTexture.active = active;
            }
            root.RemoveFromHierarchy();
            settings.targetTexture = null;
            Object.DestroyImmediate(settings);
            rt.Release();
            Object.DestroyImmediate(rt);
            return shot ?? new Texture2D(1, 1);
        }
    }
}
