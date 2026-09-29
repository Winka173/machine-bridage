using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using MachineBrigade.Game.Match;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// A Play-mode smoke run in batch mode (with graphics): opens the Sandbox scene, plays the menu
    /// with its AI battle behind it, then each listed match for a while, and writes every error,
    /// exception and failed assertion to a report. Exit code 0 when none were logged.
    /// -executeMethod MachineBrigade.Editor.PlaySmoke.Run -mbSmokeOut &lt;path&gt;
    /// [-mbSmokeSteps "menu:20,Conquest:60,Campaign=c11m05:60"] (a mode, optionally =mission, and seconds).
    /// [-mbSmokePreview &lt;png&gt;]: at the end of the first menu step, the detail page's preview texture
    /// (with -mb-detail=id -mb-detail-firing, the In action theatre) is written there and its size reported.
    /// </summary>
    public static class PlaySmoke
    {
        private static readonly List<string> Errors = new();
        private static readonly StringBuilder Report = new();
        private static readonly List<(string mode, string mission, float seconds)> Steps = new();
        private static int _step = -1;
        private static double _stepStart;
        private static string _out;
        private static int _frames;

        public static void Run()
        {
            _out = Arg("-mbSmokeOut") ?? "smoke.txt";
            foreach (var bit in (Arg("-mbSmokeSteps") ?? "menu:20,Conquest:60,Siege:60,Defend:40,BossRush:50,Campaign=c11m05:60,Campaign=c1m10:60").Split(','))
            {
                var parts = bit.Split(':');
                var head = parts[0].Split('=');
                Steps.Add((head[0], head.Length > 1 ? head[1] : null, parts.Length > 1 ? float.Parse(parts[1]) : 30f));
            }
            Application.logMessageReceivedThreaded += OnLog;
            EditorSceneManager.OpenScene("Assets/MachineBrigade/Scenes/Sandbox.unity");
            EditorApplication.update += Tick;
            EditorApplication.isPlaying = true;
        }

        private static void OnLog(string message, string stack, LogType type)
        {
            if (type != LogType.Error && type != LogType.Exception && type != LogType.Assert) return;
            // The editor's own search indexer fails at start-up in batch mode; not the game's.
            if (stack != null && stack.Contains("UnityEditor.Search.")) return;
            lock (Errors)
            {
                var step = _step >= 0 && _step < Steps.Count ? Steps[_step].mode + (Steps[_step].mission != null ? "=" + Steps[_step].mission : "") : "start";
                Errors.Add($"[{step}] {type}: {message}\n{stack}");
            }
        }

        private static void Tick()
        {
            if (!EditorApplication.isPlaying) return;
            var now = EditorApplication.timeSinceStartup;
            if (_step < 0)
            {
                _step = 0;
                _stepStart = now;
                Line($"step 0 {Steps[0].mode}: menu for {Steps[0].seconds:0} s");
                return;
            }
            if (now - _stepStart < Steps[_step].seconds) return;
            Line($"  done after {now - _stepStart:0} s, {Time.frameCount - _frames} frames, {State()}, {Errors.Count} errors so far, {Playing()}");
            if (_step == 0 && Arg("-mbSmokePreview") is { } png) SavePreview(png);
            _frames = Time.frameCount;
            _step++;
            if (_step >= Steps.Count)
            {
                Finish();
                return;
            }
            var (mode, mission, seconds) = Steps[_step];
            Line($"step {_step} {mode}{(mission != null ? "=" + mission : "")} for {seconds:0} s");
            _stepStart = now;
            if (mode == "menu")
            {
                MatchSettings.InMatch = false;
            }
            else
            {
                MatchSettings.Mode = (GameModeKind)Enum.Parse(typeof(GameModeKind), mode);
                if (mission != null) MatchSettings.Mission = mission;
                MatchSettings.InMatch = true;
            }
            SceneManager.LoadScene(0);
        }

        private static void Finish()
        {
            EditorApplication.update -= Tick;
            Application.logMessageReceivedThreaded -= OnLog;
            lock (Errors)
            {
                Line($"errors: {Errors.Count}");
                var seen = new HashSet<string>();
                foreach (var e in Errors)
                {
                    var key = e.Length > 300 ? e.Substring(0, 300) : e;
                    if (seen.Add(key)) Report.AppendLine(e).AppendLine();
                }
            }
            File.WriteAllText(_out, Report.ToString());
            EditorApplication.isPlaying = false;
            EditorApplication.Exit(Errors.Count == 0 ? 0 : 1);
        }

        /// <summary>The running match: its mode, sim tick and vehicles on the field (proof the battle ran).</summary>
        private static string State()
        {
            var runner = UnityEngine.Object.FindFirstObjectByType<MatchRunner>();
            if (runner == null) return "no MatchRunner";
            var field = typeof(MatchRunner).GetField("_world", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var world = field?.GetValue(runner) as MachineBrigade.Sim.SimWorld;
            if (world == null) return "no world";
            int alive = 0, t0 = 0, t1 = 0;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive) continue;
                alive++;
                if (v.Team == 0) t0++;
                else t1++;
            }
            return $"in match {MatchSettings.InMatch}, mode {MatchSettings.Mode}, tick {world.Tick} ({world.Tick / 20f:0} s), vehicles {alive} ({t0} v {t1})";
        }

        /// <summary>The audio sources playing now (test feedback 11D: one music track at a time, a silent lobby).</summary>
        private static string Playing()
        {
            var music = new List<string>();
            var effects = 0;
            foreach (var source in UnityEngine.Object.FindObjectsByType<AudioSource>())
            {
                if (!source.isPlaying || source.volume <= 0.001f || source.clip == null) continue;
                if (source.gameObject.name == "Music") music.Add(source.clip.name);
                else if (source.gameObject.name.StartsWith("Voice")) effects++;
            }
            return $"music playing [{string.Join(" ", music)}], effect voices {effects}";
        }

        /// <summary>The unit preview camera's texture as a PNG, and its size, samples and the screen's.</summary>
        private static void SavePreview(string path)
        {
            var camera = GameObject.Find("Preview Camera")?.GetComponent<Camera>();
            var rt = camera != null ? camera.targetTexture : null;
            if (rt == null)
            {
                Line("  preview: no preview camera or texture");
                return;
            }
            var active = RenderTexture.active;
            RenderTexture.active = rt;
            var shot = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
            shot.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
            shot.Apply(false);
            RenderTexture.active = active;
            File.WriteAllBytes(path, shot.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(shot);
            Line($"  preview: texture {rt.width}x{rt.height}, {rt.antiAliasing}x MSAA, camera aspect {camera.aspect:0.00}, enabled {camera.enabled}, screen {Screen.width}x{Screen.height} -> {path}");
        }

        private static void Line(string text)
        {
            Report.AppendLine(text);
            Debug.Log("[PlaySmoke] " + text);
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
