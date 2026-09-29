// Needs the UI Toolkit test framework package (com.unity.ui.test-framework), like UiShots: its runtime panel draws the HUD.
#if MB_UI_TEST_FRAMEWORK
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Entities;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UIElements;
using UnityEngine.UIElements.TestFramework;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// In-battle screenshots from Play mode (batch with graphics, modelled on <see cref="PlaySmoke"/>): each scene starts a
    /// real match (fixed map, deck and the match's fixed seed), waits for a sim tick, puts the camera on a view worked out
    /// from the sim (the closest fight, a base, the boss, the aircraft, the barrage's target), renders Camera.main into a
    /// 1600 x 900 texture, lends the live compact HUD to an off-screen runtime panel of the same size for that frame (the
    /// game's own panel does not draw into a texture in batch mode) and blends it over. Writes
    /// Docs/ui-screens/battle3d-&lt;scene&gt;.png and a report of every error logged.
    /// -executeMethod MachineBrigade.Editor.PlayShots.Run [-mbShotsDir &lt;folder&gt;] [-mbPlayShotsOnly conquest,boss]
    /// [-mbPlayShotsOut &lt;report&gt;] (no -quit: it exits by itself).
    /// </summary>
    public static class PlayShots
    {
        private const int Width = 1600, Height = 900;

        private sealed class Scene
        {
            public string Name;
            public GameModeKind Mode;
            public string Map = "ashfield";
            public string[] Deck;
            public int Tick;
            public Func<SimWorld, List<(string suffix, Vector3 focus, float zoom)>> Views;
        }

        /// <summary>The deck of the scenes that do not set their own (the saved one differs from editor to editor).</summary>
        private static readonly string[] StandardDeck =
            { "scout_jeep", "armored_car", "ifv", "light_tank", "main_battle_tank", "tank_destroyer", "aa_vehicle", "artillery" };

        private static readonly string[] AirDeck =
            { "attack_helicopter", "gunship_heli", "attack_jet", "fighter_jet", "heavy_attack_heli", "tank_buster", "scout_heli", "strike_drone" };

        private static readonly string[] ArtilleryDeck =
            { "mlrs", "artillery", "heavy_rocket_artillery", "thermobaric_launcher", "mortar_carrier", "main_battle_tank", "light_tank", "aa_vehicle" };

        private static readonly List<Scene> All = new()
        {
            new Scene { Name = "conquest", Mode = GameModeKind.Conquest, Tick = 1100, Views = w => One(Fight(w), 24f) },
            new Scene { Name = "siege", Mode = GameModeKind.Siege, Tick = 500, Views = w => One(Hq(w, 1), 40f) },
            new Scene
            {
                Name = "defend", Mode = GameModeKind.Defend, Tick = 1300,
                Views = w =>
                {
                    var hq = Hq(w, 0);
                    var attacker = Nearest(w, hq, v => v.Team != 0 && !v.Def.Flying);
                    var views = new List<(string, Vector3, float)> { ("", attacker is { } a ? Vector3.Lerp(hq, a, 0.5f) : hq, 30f) };
                    // The close views of the base: the HQ, then the two towers nearest it that stand apart from each other.
                    views.Add(("-base-hq", hq, 13f));
                    var towers = new List<Vector3>();
                    foreach (var p in w.Vehicles.Where(v => v.IsAlive && v.Team == 0 && v.Def.Fort != null && !v.Def.Boss).Select(Of)
                                 .Where(p => Vector3.Distance(p, hq) > 10f).OrderBy(p => Vector3.Distance(p, hq)))
                    {
                        if (towers.Any(t => Vector3.Distance(t, p) < 22f)) continue;
                        towers.Add(p);
                        if (towers.Count == 2) break;
                    }
                    for (var i = 0; i < towers.Count; i++) views.Add(("-base-" + (i + 1), Vector3.Lerp(hq, towers[i], 0.8f), 13f));
                    return views;
                },
            },
            new Scene
            {
                Name = "boss", Mode = GameModeKind.BossRush, Tick = 800,
                Views = w => One(w.Vehicles.FirstOrDefault(v => v.IsAlive && v.Def.Boss) is { } boss ? Of(boss) : Centroid(w, v => v.Team != 0), 28f),
            },
            new Scene { Name = "air", Mode = GameModeKind.Conquest, Deck = AirDeck, Tick = 1300, Views = w => One(Centroid(w, v => v.Def.Flying), 26f) },
            new Scene
            {
                Name = "barrage", Mode = GameModeKind.Conquest, Deck = ArtilleryDeck, Tick = 1400,
                Views = w =>
                {
                    var guns = Centroid(w, v => v.Team == 0 && v.Def.Weapon.MinRange > 0f);
                    var target = Nearest(w, guns, v => v.Team != 0 && !v.Def.Flying);
                    return One(target is { } t ? Vector3.Lerp(guns, t, 0.75f) : guns, 30f);
                },
            },
        };

        private static readonly List<string> Errors = new();
        private static readonly StringBuilder Report = new();
        private static List<Scene> _scenes;
        private static int _scene = -1, _view, _waitFrame;
        private static double _deadline;
        private static List<(string suffix, Vector3 focus, float zoom)> _views;
        private static RenderTexture _camTexture, _uiTexture;
        private static SimWorld _previous;
        private static string _folder, _out;
        private static int _state; // 0 wait for the match, 1 place the camera, 2 capture

        public static void Run()
        {
            _folder = Arg("-mbShotsDir") ?? Path.Combine(Directory.GetParent(Application.dataPath)!.FullName, "Docs", "ui-screens");
            _out = Arg("-mbPlayShotsOut") ?? Path.Combine(_folder, "..", "..", "Temp", "playshots.txt");
            var only = Arg("-mbPlayShotsOnly")?.Split(',');
            _scenes = All.Where(s => only == null || only.Contains(s.Name)).ToList();
            Directory.CreateDirectory(_folder);
            Application.logMessageReceivedThreaded += OnLog;
            EditorSceneManager.OpenScene("Assets/MachineBrigade/Scenes/Sandbox.unity");
            EditorApplication.update += Tick;
            EditorApplication.isPlaying = true;
        }

        private static void Tick()
        {
            if (!EditorApplication.isPlaying) return;
            var now = EditorApplication.timeSinceStartup;
            if (_scene < 0)
            {
                // The menu comes up first; then the first match.
                if (Time.frameCount < 30) return;
                Next(now);
                return;
            }
            if (now > _deadline)
            {
                Line($"  {_scenes[_scene].Name}: timed out ({State()})");
                Next(now);
                return;
            }
            var world = World();
            if (world == null) return;
            var scene = _scenes[_scene];
            switch (_state)
            {
                case 0:
                    // Just after the scene loads, the last match's world is still found for a frame.
                    if (world == _previous || world.Tick < scene.Tick) return;
                    _views = scene.Views(world);
                    _view = 0;
                    _state = 1;
                    return;
                case 1:
                    Place(_views[_view]);
                    BeginCapture();
                    _waitFrame = Time.frameCount + 3;
                    _state = 2;
                    return;
                case 2:
                    Place(_views[_view]);
                    if (Time.frameCount < _waitFrame) return;
                    var name = "battle3d-" + scene.Name + _views[_view].suffix + ".png";
                    File.WriteAllBytes(Path.Combine(_folder, name), EndCapture());
                    Line($"  wrote {name} at tick {world.Tick}, focus {_views[_view].focus}, zoom {_views[_view].zoom} ({State()})");
                    _view++;
                    if (_view < _views.Count) _state = 1;
                    else Next(now);
                    return;
            }
        }

        private static void Next(double now)
        {
            _scene++;
            _state = 0;
            if (_scene >= _scenes.Count)
            {
                Finish();
                return;
            }
            var s = _scenes[_scene];
            Line($"scene {s.Name}: {s.Mode} on {s.Map}, shot at tick {s.Tick}");
            MatchSettings.Mode = s.Mode;
            MatchSettings.Map = s.Map;
            MatchSettings.Difficulty = AiDifficulty.Normal;
            MatchSettings.CompactHud = true;
            MatchSettings.AutoDeploy = true;
            MatchSettings.AutoStrike = true;
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(s.Deck ?? StandardDeck);
            Strings.Vietnamese = true;
            _previous = World();
            MatchSettings.InMatch = true;
            _deadline = now + s.Tick / 20.0 + 90.0;
            SceneManager.LoadScene(0);
        }

        // ---------------------------------------------------------------- views

        private static List<(string, Vector3, float)> One(Vector3 focus, float zoom) => new() { ("", focus, zoom) };

        private static Vector3 Of(Vehicle v) => new(v.Position.X, 0f, v.Position.Y);

        private static Vector3 Hq(SimWorld w, int team) =>
            w.Bases.Of(team) is { } b ? new Vector3(b.HqPosition.X, 0f, b.HqPosition.Y) : Centroid(w, v => v.Team == team);

        private static Vector3 Centroid(SimWorld w, Func<Vehicle, bool> which)
        {
            var list = w.Vehicles.Where(v => v.IsAlive && which(v)).ToList();
            if (list.Count == 0) return Vector3.zero;
            var sum = Vector3.zero;
            foreach (var v in list) sum += Of(v);
            return sum / list.Count;
        }

        private static Vector3? Nearest(SimWorld w, Vector3 from, Func<Vehicle, bool> which)
        {
            Vector3? best = null;
            var bestDistance = float.MaxValue;
            foreach (var v in w.Vehicles)
            {
                if (!v.IsAlive || !which(v)) continue;
                var d = Vector3.Distance(from, Of(v));
                if (d >= bestDistance) continue;
                bestDistance = d;
                best = Of(v);
            }
            return best;
        }

        /// <summary>The closest pair of ground units of the two sides: where the fighting is.</summary>
        private static Vector3 Fight(SimWorld w)
        {
            var ours = w.Vehicles.Where(v => v.IsAlive && v.Team == 0 && !v.Def.Flying && !v.Def.Static).ToList();
            var theirs = w.Vehicles.Where(v => v.IsAlive && v.Team != 0 && !v.Def.Flying && !v.Def.Static).ToList();
            var best = Centroid(w, v => !v.Def.Static);
            var bestDistance = float.MaxValue;
            foreach (var a in ours)
            foreach (var b in theirs)
            {
                var d = Vector3.Distance(Of(a), Of(b));
                if (d >= bestDistance) continue;
                bestDistance = d;
                best = (Of(a) + Of(b)) * 0.5f;
            }
            return best;
        }

        private static void Place((string suffix, Vector3 focus, float zoom) view)
        {
            var camera = Field<RtsCamera>("_camera");
            camera?.Glide(view.focus, view.zoom, 100f, 1f);
            camera?.Apply(0f);
        }

        // ---------------------------------------------------------------- capture

        private static void BeginCapture()
        {
            _camTexture ??= new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = 4 };
            if (Camera.main != null) Camera.main.targetTexture = _camTexture;
        }

        /// <summary>
        /// The HUD drawn off-screen: the HUD document's children move to a runtime panel with the same theme, sheets and
        /// scaling at 1600 x 900 for a few frames, are drawn into a clear texture, and move back.
        /// </summary>
        private static Color32[] DrawHud()
        {
            var document = UnityEngine.Object.FindObjectsByType<UIDocument>(FindObjectsSortMode.None)
                .FirstOrDefault(d => d.gameObject.name == "HUD" && d.rootVisualElement != null);
            _uiTexture ??= new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            if (document == null) return new Color32[Width * Height];
            var source = document.rootVisualElement;
            var settings = ScriptableObject.CreateInstance<PanelSettings>();
            settings.themeStyleSheet = document.panelSettings.themeStyleSheet;
            settings.scaleMode = PanelScaleMode.ScaleWithScreenSize;
            settings.referenceResolution = new Vector2Int(1280, 720);
            settings.screenMatchMode = PanelScreenMatchMode.MatchWidthOrHeight;
            settings.match = BattleHud.MatchFor(Width, Height);
            settings.targetTexture = _uiTexture;
            settings.clearColor = true;
            settings.colorClearValue = Color.clear;
            var simulator = new RuntimePanelSimulator(settings) { needsRendering = true };
            var host = new VisualElement();
            host.style.position = Position.Absolute;
            host.style.left = host.style.top = host.style.right = host.style.bottom = 0;
            for (var i = 0; i < source.styleSheets.count; i++) host.styleSheets.Add(source.styleSheets[i]);
            foreach (var c in source.GetClasses()) host.AddToClassList(c);
            var children = source.Children().ToList();
            foreach (var c in children) host.Add(c);
            simulator.rootVisualElement.Add(host);
            try
            {
                for (var i = 0; i < 6; i++) simulator.FrameUpdate();
                return Read(_uiTexture);
            }
            finally
            {
                foreach (var c in children) source.Add(c);
                host.RemoveFromHierarchy();
                settings.targetTexture = null;
                UnityEngine.Object.DestroyImmediate(settings);
            }
        }

        private static byte[] EndCapture()
        {
            var scene = Read(_camTexture);
            var hud = DrawHud();
            if (Camera.main != null) Camera.main.targetTexture = null;
            // The panel is drawn with premultiplied alpha over a clear texture: hud + scene x (1 - hud alpha).
            for (var i = 0; i < scene.Length; i++)
            {
                var a = hud[i].a / 255f;
                scene[i] = new Color32((byte)Mathf.Min(255, hud[i].r + scene[i].r * (1f - a)), (byte)Mathf.Min(255, hud[i].g + scene[i].g * (1f - a)),
                    (byte)Mathf.Min(255, hud[i].b + scene[i].b * (1f - a)), 255);
            }
            var shot = new Texture2D(Width, Height, TextureFormat.RGB24, false);
            shot.SetPixels32(scene);
            shot.Apply(false);
            var png = shot.EncodeToPNG();
            UnityEngine.Object.DestroyImmediate(shot);
            return png;
        }

        private static Color32[] Read(RenderTexture rt)
        {
            var active = RenderTexture.active;
            RenderTexture.active = rt;
            var tex = new Texture2D(rt.width, rt.height, TextureFormat.RGBA32, false);
            tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
            tex.Apply(false);
            RenderTexture.active = active;
            var pixels = tex.GetPixels32();
            UnityEngine.Object.DestroyImmediate(tex);
            return pixels;
        }

        // ---------------------------------------------------------------- plumbing

        private static SimWorld World() => Field<SimWorld>("_world");

        private static T Field<T>(string name) where T : class
        {
            var runner = UnityEngine.Object.FindFirstObjectByType<MatchRunner>();
            if (runner == null || !MatchSettings.InMatch) return null;
            return typeof(MatchRunner).GetField(name, BindingFlags.NonPublic | BindingFlags.Instance)?.GetValue(runner) as T;
        }

        private static string State()
        {
            var w = World();
            return w == null ? "no match" : $"{MatchSettings.Mode}, tick {w.Tick}, vehicles {w.Vehicles.Count(v => v.IsAlive)}";
        }

        private static void OnLog(string message, string stack, LogType type)
        {
            if (type != LogType.Error && type != LogType.Exception && type != LogType.Assert) return;
            if (stack != null && stack.Contains("UnityEditor.Search.")) return;
            lock (Errors) Errors.Add($"[{(_scenes != null && _scene >= 0 && _scene < _scenes.Count ? _scenes[_scene].Name : "start")}] {type}: {message}\n{stack}");
        }

        private static void Finish()
        {
            EditorApplication.update -= Tick;
            Application.logMessageReceivedThreaded -= OnLog;
            lock (Errors)
            {
                Line($"errors: {Errors.Count}");
                foreach (var e in Errors.Distinct().Take(40)) Report.AppendLine(e).AppendLine();
            }
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(_out))!);
            File.WriteAllText(_out, Report.ToString());
            EditorApplication.isPlaying = false;
            EditorApplication.Exit(0);
        }

        private static void Line(string text)
        {
            Report.AppendLine(text);
            Debug.Log("[PlayShots] " + text);
        }

        private static string Arg(string name)
        {
            var args = Environment.GetCommandLineArgs();
            for (var i = 0; i + 1 < args.Length; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }
    }
}
#endif
