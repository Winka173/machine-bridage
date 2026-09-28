using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using MachineBrigade.Game.Match;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Object = UnityEngine.Object;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// A real match in Play mode, photographed from the battle camera at chosen moments (prompt
    /// 11C: the shields where the game puts them). Batch mode (with graphics): -executeMethod
    /// MachineBrigade.Editor.ShieldPlayShots.Run -mbShotsOut &lt;folder&gt; [-mbShotMode Siege]
    /// [-mbShotGraphics Low] [-mbShotTimes 6,9.2,9.6] (seconds after the match loads), plus debug flags such
    /// as -mb-domedown (the relays, then the generators, go down so the dome falls). Errors and
    /// exceptions logged during the run are counted in the log line at the end.
    /// </summary>
    public static class ShieldPlayShots
    {
        private static readonly List<float> Times = new();
        private static int _next;
        private static string _folder;
        private static string _mode;
        private static int _errors;
        private static GraphicsQuality _graphics = GraphicsQuality.High;

        /// <summary>When the match's scene was loaded (play time); negative until then.</summary>
        private static float _loadedAt = -1f;

        public static void Run()
        {
            _folder = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/shield-play");
            _mode = Argument("-mbShotMode") ?? "Siege";
            foreach (var bit in (Argument("-mbShotTimes") ?? "6,9,9.4,9.8,11").Split(','))
                Times.Add(float.Parse(bit, CultureInfo.InvariantCulture));
            Directory.CreateDirectory(_folder);
            if (Enum.TryParse<GraphicsQuality>(Argument("-mbShotGraphics") ?? "High", out var graphics)) _graphics = graphics;
            Application.logMessageReceivedThreaded += OnLog;
            EditorSceneManager.OpenScene("Assets/MachineBrigade/Scenes/Sandbox.unity");
            EditorApplication.update += Tick;
            EditorApplication.isPlaying = true;
        }

        private static void OnLog(string message, string stack, LogType type)
        {
            if (type is LogType.Error or LogType.Exception or LogType.Assert && (stack == null || !stack.Contains("UnityEditor.Search.")))
            {
                _errors++;
                Debug.Log("[ShieldPlayShots] logged: " + message);
            }
        }

        private static void Tick()
        {
            if (!EditorApplication.isPlaying) return;
            if (_loadedAt < 0f)
            {
                // As PlaySmoke: the menu loads first (and the saved settings with it); then the match.
                if (Time.time < 2f) return;
                MatchSettings.Graphics = _graphics;
                MatchSettings.Mode = (GameModeKind)Enum.Parse(typeof(GameModeKind), _mode);
                MatchSettings.InMatch = true;
                UnityEngine.SceneManagement.SceneManager.LoadScene(0);
                _loadedAt = Time.time;
                return;
            }
            if (_next >= Times.Count)
            {
                EditorApplication.update -= Tick;
                Application.logMessageReceivedThreaded -= OnLog;
                Debug.Log($"[ShieldPlayShots] done: {Times.Count} shots in {_folder}, {_errors} errors logged");
                EditorApplication.isPlaying = false;
                EditorApplication.Exit(_errors == 0 ? 0 : 1);
                return;
            }
            if (Time.time - _loadedAt < Times[_next]) return;
            var camera = Camera.main;
            if (camera == null) return;
            var rt = new RenderTexture(1280, 720, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            var target = camera.targetTexture;
            camera.targetTexture = rt;
            camera.Render();
            camera.targetTexture = target;
            var active = RenderTexture.active;
            RenderTexture.active = rt;
            var shot = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
            shot.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
            shot.Apply(false);
            RenderTexture.active = active;
            var path = Path.Combine(_folder, $"{_mode.ToLowerInvariant()}-{_graphics.ToString().ToLowerInvariant()}-{_next + 1:00}-{Time.time - _loadedAt:0.0}s.png");
            File.WriteAllBytes(path, shot.EncodeToPNG());
            Object.DestroyImmediate(shot);
            rt.Release();
            Object.DestroyImmediate(rt);
            Debug.Log($"[ShieldPlayShots] {path}");
            _next++;
        }

        private static string Argument(string name)
        {
            var args = Environment.GetCommandLineArgs();
            for (var i = 0; i + 1 < args.Length; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }
    }
}
