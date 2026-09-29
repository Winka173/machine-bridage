// Needs the UI Toolkit test framework package (com.unity.ui.test-framework); without it the rest of the project still compiles.
#if MB_UI_TEST_FRAMEWORK
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
            // Prompt 15 E8: the icon legend is a long page; read at once.
            yield return ("screen-legend-vi-full", Menu("legend", true, false), new[] { Shapes[0] }, 1);
            foreach (var screen in new[] { "home", "campaign-chapter", "army-deck", "army-towers", "army-base", "army-outpost", "detail", "detail-tower", "detail-module", "detail-action", "detail-tower-action", "settings", "shop-crates" })
            {
                yield return ("screen-" + screen + "-vi-large", Menu(screen, true, true), new[] { Shapes[0] }, 0);
                yield return ("screen-" + screen + "-en", Menu(screen, false, false), new[] { Shapes[0] }, 0);
            }
        }

        /// <summary>
        /// The battle's own screens (E10 and G, prompt 11 A): the compact HUD in Conquest (hud-score), a boss battle
        /// (hud-mission, and hud-boss-open with its bar opened by a tap), Siege, Defend and Survival (hud-waves), the full
        /// HUD for comparison (hud-*-full), the result after a win and a loss, the checkpoint's offer, pause, the choice
        /// between stages.
        /// </summary>
        public static readonly string[] BattleScreenNames =
        {
            "hud-score", "hud-mission", "hud-boss-open", "hud-siege", "hud-defend", "hud-waves", "hud-score-full", "hud-mission-full",
            "hud-enemy",
            "result-win", "result-loss", "result-checkpoint", "result-endless", "pause", "choice",
        };

        /// <summary>The battle screens with no main action: the HUD itself.</summary>
        public static bool WithoutPrimary(string screen) => screen.StartsWith("hud-");

        /// <summary>The battle's screens with the demo profile, in Vietnamese at the four shapes, and a few in Large text and in English.</summary>
        public static IEnumerable<(string file, Builder build, Shape[] shapes, int tallHeight)> BattleScreens()
        {
            var catalog = GameContent.LoadCatalog();
            Builder Battle(string screen, bool vi, bool large) => (out Action<Vector4> insets) =>
            {
                Strings.Vietnamese = vi;
                MatchSettings.TextSize = large ? TextSize.Large : TextSize.Normal;
                DemoProfile.Use();
                var host = BuildBattle(catalog, screen, out var safe);
                insets = v => KitSafeArea.Apply(safe, v);
                return host;
            };
            foreach (var screen in BattleScreenNames)
                yield return ("battle-" + screen + "-vi", Battle(screen, true, false), screen.EndsWith("-full") ? new[] { Shapes[0], Shapes[2] } : Shapes, 0);
            foreach (var screen in new[] { "hud-score", "hud-mission", "hud-siege", "hud-defend", "result-win", "result-loss" })
            {
                yield return ("battle-" + screen + "-vi-large", Battle(screen, true, true), new[] { Shapes[0] }, 0);
                yield return ("battle-" + screen + "-en", Battle(screen, false, false), new[] { Shapes[0] }, 0);
            }
        }

        /// <summary>A battle screen over the battlefield's picture, as BattleHud lays it out (the sheets on the root, the panels in the safe area).</summary>
        public static VisualElement BuildBattle(Catalog catalog, string screen, out VisualElement safe)
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
            if (screen.StartsWith("hud-"))
            {
                // The HUD builds itself into the host, sheets and safe area included.
                var hud = BuildHud(catalog, screen, host);
                safe = hud.SafeArea;
                return host;
            }
            safe = new VisualElement();
            safe.style.position = Position.Absolute;
            safe.style.left = safe.style.top = safe.style.right = safe.style.bottom = 0;
            host.Add(safe);
            switch (screen)
            {
                case "pause":
                    var pause = new PausePanel(null, null, null);
                    safe.Add(pause.Root);
                    pause.Visible = true;
                    break;
                case "choice":
                    var choice = new ChoicePanel();
                    safe.Add(choice.Root);
                    choice.Show(Strings.Get("choice.title"), new List<(string, string)>
                    {
                        (Strings.Get("mode.assault"), Strings.Get("mode.assaultSub")),
                        (Strings.Get("mode.defend"), Strings.Get("mode.defendSub")),
                    }, _ => { });
                    choice.SetTime(12f);
                    break;
                default:
                    var result = new ResultPanel(null, null, null, null, null, null);
                    safe.Add(result.Root);
                    ShowDemoResult(catalog, result, screen);
                    break;
            }
            return host;
        }

        private static string Clock(int seconds) => $"{seconds / 60}:{seconds % 60:00}";

        /// <summary>
        /// The battle HUD with the demo deck, part-way through a battle: the CP box over supply, cards the
        /// points pay for and cards they do not, a support card cooling down and one being aimed; the score
        /// with three objectives (hud-score, a selection open), a boss with its phases and parts and an elite
        /// notice (hud-mission), the waves with the strike prompt and a tower to fly back in (hud-waves).
        /// </summary>
        private static BattleHud BuildHud(Catalog catalog, string screen, VisualElement host)
        {
            var cards = new List<CardInfo>();
            foreach (var id in MatchSettings.DeckVehicles)
                if (catalog.Vehicles.TryGetValue(id, out var v)) cards.Add(new CardInfo(id, false, v.CpCost, CardIcons.For(id)));
            // Another test may have left the deck without supports; the demo always shows the starter ones then.
            var supports = MatchSettings.DeckSupports.Any(id => catalog.TryGetSupport(id, out _)) ? (IEnumerable<string>)MatchSettings.DeckSupports : Progression.StarterSupports;
            foreach (var id in supports)
                if (catalog.TryGetSupport(id, out var sup)) cards.Add(new CardInfo(id, true, sup.CpCost, CardIcons.For(id)));
            // The compact HUD unless the shot is of the full one; the first-match hint only on Conquest's.
            var full = screen.EndsWith("-full");
            if (full) screen = screen.Substring(0, screen.Length - "-full".Length);
            var spec = screen switch
            {
                "hud-mission" or "hud-boss-open" or "hud-siege" or "hud-defend" => new HudSpec { Mode = HudMode.Mission, HintKey = "hint.auto" },
                "hud-waves" => new HudSpec { Mode = HudMode.Waves },
                _ => new HudSpec { Mode = HudMode.Score, ScoreLabel = "stat.tickets" },
            };
            spec.Compact = !full;
            spec.StartHint = screen == "hud-score";
            var hud = new BattleHud(spec, cards, catalog, host);
            const float cp = 7.4f;
            var states = new List<CardState>();
            for (var i = 0; i < cards.Count; i++)
            {
                var card = cards[i];
                var aiming = screen == "hud-waves" && card.Support && states.Count(s => s.Selected) == 0;
                var cooling = card.Support && !aiming && i == cards.Count - 1;
                states.Add(new CardState(card.Cost <= cp, false, cooling ? 0.4f : 0f, aiming, cooling ? 12f : 0f));
            }
            hud.SetDeck(cp, 20f, 2.4f, 0.71f, states);
            hud.SetCommander(false, true, false, "town");
            var points = new List<PointInfo> { new("west", 0, 1f, false), new("town", -1, 0.35f, true), new("east", 1, -1f, false) };
            switch (screen)
            {
                case "hud-siege":
                    hud.SetMission(Strings.Format("mode.siege.stage", 2, Strings.Get("siege.goal2")), "46%", 0.46f, 522f, new List<PointInfo>());
                    hud.SetSuperGun(38f, false, false);
                    hud.SetSelection(new MachineBrigade.Game.Input.SelectionSummary(4, "siege_tank", 3100f, 3600f));
                    hud.Toast(Strings.Get("toast.raid"), error: true, seconds: 5f);
                    break;
                case "hud-defend":
                {
                    hud.SetMission(Strings.Format("base.line", 1, Strings.Get("base.goal1")), Strings.Format("base.waveOf", 4) + "  ·  82%", 0.82f, 431f,
                        new List<PointInfo>());
                    var wave = new List<(string, int)> { ("armored_car", 4), ("rocket_technical", 3), ("light_tank", 2), ("fpv_carrier", 1) };
                    var elite = catalog.Vehicles.Values.Where(v => v.Elite && !v.Boss).OrderBy(v => v.Id).First();
                    wave.Add((elite.Id, 1));
                    hud.SetWavePreview(wave, 21f, 5, 3);
                    hud.SetSuperGun(64f, false, true);
                    hud.SetTowers(1, 40);
                    break;
                }
                case "hud-mission":
                case "hud-boss-open":
                {
                    hud.SetMission(Strings.Get("goal.boss"), Strings.Format("result.sides", 2, 1), 0.45f, 312f, new List<PointInfo>());
                    var boss = catalog.Vehicles.Values.Where(v => v.Boss && v.Parts.Count >= 5).OrderBy(v => v.Id).First();
                    hud.SetBoss(Strings.Card(boss.Id), 0.62f, 1, new List<float> { 0.66f, 0.33f }, false);
                    hud.SetBossHp(37200f, 60000f);
                    var shares = new List<float>();
                    var broken = new List<bool>();
                    for (var i = 0; i < boss.Parts.Count; i++)
                    {
                        shares.Add(i == 1 ? 0f : 1f - 0.15f * i);
                        broken.Add(i == 1);
                    }
                    hud.PreviewBossParts(boss, shares, broken, 2);
                    if (screen == "hud-boss-open") hud.PreviewBossExpanded();
                    var elite = catalog.Vehicles.Values.Where(v => v.Elite && !v.Boss).OrderBy(v => v.Id).First();
                    hud.Toast(Strings.Format("radio.elite", Strings.Card(elite.Id)), error: true, seconds: 5f);
                    break;
                }
                case "hud-waves":
                    hud.SetStats(14, 23, 6, 34f, 60f);
                    hud.SetTowers(1, 40);
                    var aimed = cards.First(c => c.Support);
                    hud.SetTargeting(Strings.Format("target.hint", Strings.Support(aimed.Id)));
                    break;
                default:
                    hud.SetScore(412, 356, 600, points);
                    hud.SetTimer(245f);
                    hud.SetSelection(new MachineBrigade.Game.Input.SelectionSummary(3, "main_battle_tank", 1450f, 2000f));
                    if (screen == "hud-enemy")
                    {
                        // Prompt 15 E3 and E5: an enemy heavy tank tapped (our deck against it), and a tray card held.
                        hud.ShowEnemyTip(catalog.Vehicles["heavy_tank"],
                            MatchSettings.DeckVehicles.Where(catalog.Vehicles.ContainsKey).Select(id => catalog.Vehicles[id]));
                        hud.PreviewHeld(1);
                    }
                    break;
            }
            return hud;
        }

        private static void ShowDemoResult(Catalog catalog, ResultPanel result, string screen)
        {
            switch (screen)
            {
                case "result-win":
                {
                    var mission = Campaign.All[Campaign.Next];
                    var reward = new RewardView { Coins = 1250, Xp = 320, Stars = 2, CanDouble = true, HasNext = true };
                    reward.Unlocked.Add(Strings.Card("tank_destroyer"));
                    reward.Crates.Add(Strings.Get("crate.silver"));
                    reward.Extras.Add(("star", $"{Strings.Get("result.prints")} +3"));
                    result.Show(1, Strings.Get("mission." + mission.Id + ".name"), new List<(string, string)>
                    {
                        (Strings.Get("result.kills"), "42"), (Strings.Get("result.losses"), "7"), (Strings.Get("result.time"), Clock(504)),
                        (Strings.Get("result.stages"), "3"),
                    }, reward);
                    break;
                }
                case "result-endless":
                {
                    var reward = new RewardView { Coins = 640, Xp = 150, CanDouble = true };
                    result.Show(-1, Strings.Get("mode.endless"), new List<(string, string)>
                    {
                        (Strings.Get("result.kills"), "96"), (Strings.Get("result.losses"), "38"), (Strings.Get("result.time"), Clock(1122)),
                        (Strings.Get("result.waves"), "14"), (Strings.Get("endless.best"), "14"),
                    }, reward, Strings.Format("endless.record", 14), DemoHints(catalog));
                    break;
                }
                default:
                {
                    var checkpoint = screen == "result-checkpoint";
                    var reward = new RewardView { Coins = 180, Xp = 60, CanDouble = true, CanResume = checkpoint, Stars = checkpoint ? 0 : -1 };
                    var title = checkpoint ? Strings.Get("mission." + Campaign.All[Campaign.Next].Id + ".name") : Strings.Get("mode.conquest");
                    var rows = new List<(string, string)>();
                    if (!checkpoint) rows.Add((Strings.Get("stat.score"), Strings.Format("result.sides", 0, 331)));
                    rows.Add((Strings.Get("result.kills"), "18"));
                    rows.Add((Strings.Get("result.losses"), "31"));
                    rows.Add((Strings.Get("result.time"), Clock(760)));
                    result.Show(-1, title, rows, reward, null, DemoHints(catalog));
                    break;
                }
            }
        }

        /// <summary>The hints of a lost battle against many aircraft and heavy armour, with the demo deck (seven of eight).</summary>
        private static List<string> DemoHints(Catalog catalog)
        {
            var tally = new BattleTally();
            var air = catalog.Vehicles.Values.First(v => v.Flying && !v.Boss && !v.Elite);
            var heavy = catalog.Vehicles.Values.First(v => v.Class == UnitClass.Heavy && !v.Boss && !v.Elite);
            for (var i = 0; i < 6; i++) tally.Saw(air);
            for (var i = 0; i < 10; i++) tally.Saw(heavy);
            return DefeatHints.For(tally, catalog, MatchSettings.DeckVehicles, MatchSettings.DeckSupports, MatchSettings.DeckVehicleSlots, 18, 31, false);
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
            if (set is "all" or "battle") list.AddRange(BattleScreens());
            var only = Argument("-mbShotsOnly");
            // One name part, or several separated by commas.
            if (only != null) list = list.FindAll(s => only.Split(',').Any(o => s.file.Contains(o)));
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
#endif
