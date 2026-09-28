using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Text;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using UnityEditor;
using UnityEditor.Profiling;
using UnityEditor.SceneManagement;
using UnityEditorInternal;
using UnityEngine;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Batch-mode probe of the game's first seconds (test feedback 11D): plays the menu from a cold
    /// start with the profiler recording, and reports every frame's time from the first one, the
    /// hitches with the markers that took the most time in them, when the curtain lifted, and every
    /// second which audio sources are playing (music decks, effect voices, loops). Optionally opens
    /// the detail page's In action range on chosen vehicles and logs their range's events, to check
    /// what each clip shows and that it is heard without the menu battle.
    /// -executeMethod MachineBrigade.Editor.StartupProbe.Run -mbProbeOut &lt;txt&gt; [-mbProbeSeconds 20]
    /// [-mbProbeRange "ew_jammer+iron_beam"] [-mbProbeRangeSeconds 10]. Editor numbers are not phone numbers.
    /// </summary>
    public static class StartupProbe
    {
        private const float HitchMs = 33.3f;

        private static readonly StringBuilder Report = new();
        private static readonly List<float> Frames = new();

        /// <summary>Each frame's time less the editor's own loop (its throttle and windows): what the game itself spent.</summary>
        private static readonly List<float> Game = new();
        private static FiringRange _range;
        private static Camera _rangeCamera;
        private static double _rangeTicked;
        private static readonly List<string> Errors = new();
        private static string _out;
        private static float _seconds = 20f;
        private static float _rangeSeconds = 10f;
        private static double _start;
        private static int _processed = -1;
        private static int _openFrame = -1, _builtFrame = -1;
        private static double _nextCensus;
        private static readonly List<string> Range = new();
        private static int _rangeIndex = -1;
        private static double _rangeStart;
        private static readonly StringBuilder RangeLog = new();
        private static readonly Dictionary<string, int> RangeCounts = new();

        public static void Run()
        {
            _out = Arg("-mbProbeOut") ?? "probe.txt";
            if (float.TryParse(Arg("-mbProbeSeconds"), out var s)) _seconds = s;
            if (float.TryParse(Arg("-mbProbeRangeSeconds"), out var r)) _rangeSeconds = r;
            var range = Arg("-mbProbeRange");
            if (!string.IsNullOrEmpty(range)) Range.AddRange(range.Split('+'));
            Application.logMessageReceivedThreaded += OnLog;
            EditorSceneManager.OpenScene("Assets/MachineBrigade/Scenes/Sandbox.unity");
            MatchSettings.InMatch = false;
            ProfilerDriver.ClearAllFrames();
            ProfilerDriver.profileEditor = false;
            ProfilerDriver.enabled = true;
            EditorApplication.update += Tick;
            EditorApplication.isPlaying = true;
        }

        private static void OnLog(string message, string stack, LogType type)
        {
            if (type != LogType.Error && type != LogType.Exception) return;
            if (stack != null && stack.Contains("UnityEditor.Search.")) return;
            lock (Errors) Errors.Add(type + ": " + message + "\n" + stack);
        }

        private static void Tick()
        {
            if (!EditorApplication.isPlaying) return;
            var now = EditorApplication.timeSinceStartup;
            if (_start == 0) _start = now;
            Collect();
            var runner = UnityEngine.Object.FindFirstObjectByType<MatchRunner>();
            var built = runner != null && (bool)(Field(runner, "_built") ?? false);
            // Profiler frame indices run behind Time.frameCount by a fixed offset: this frame is about lastFrameIndex + 1.
            var index = ProfilerDriver.lastFrameIndex + 1;
            if (built && _builtFrame < 0) _builtFrame = index;
            if (built && _openFrame < 0 && !Curtain.Busy)
            {
                _openFrame = index;
                Line($"curtain lifted at {now - _start:0.00} s (profiler frame {index})");
            }
            if (now >= _nextCensus)
            {
                _nextCensus = now + 1.0;
                Line($"t={now - _start:0.0} s audio: {Census()}");
            }
            if (_rangeIndex < 0 && now - _start >= _seconds)
            {
                if (Range.Count == 0 || runner == null)
                {
                    Finish();
                    return;
                }
                _rangeIndex = 0;
                StartRange(runner);
                _rangeStart = now;
                return;
            }
            if (_range != null)
            {
                var dt = (float)Math.Min(0.1, now - _rangeTicked);
                _rangeTicked = now;
                _range.Tick(dt);
                var audio = Field(runner, "_audio") as MachineBrigade.Game.Audio.AudioDirector;
                if (audio != null) audio.FocusOverride = _range.Look;
            }
            if (_rangeIndex >= 0 && now - _rangeStart >= _rangeSeconds)
            {
                EndRange();
                _rangeIndex++;
                if (_rangeIndex >= Range.Count)
                {
                    Finish();
                    return;
                }
                StartRange(runner);
                _rangeStart = now;
            }
        }

        private static void StartRange(MatchRunner runner)
        {
            var id = Range[_rangeIndex];
            RangeCounts.Clear();
            RangeLog.Clear();
            FiringRange.Log = (t, e) =>
            {
                var key = e.Kind == Sim.Events.SimEventKind.SkillUsed ? "SkillUsed:" + e.Skill
                    : e.Kind == Sim.Events.SimEventKind.WeaponFired ? e.Kind + ":t" + e.Team + ":" + e.DefId
                    : e.Kind is Sim.Events.SimEventKind.Damaged or Sim.Events.SimEventKind.ProjectileImpact ? e.Kind + ":t" + e.Team
                    : e.Kind.ToString();
                RangeCounts[key] = RangeCounts.TryGetValue(key, out var n) ? n + 1 : 1;
                if (e.Kind is Sim.Events.SimEventKind.WeaponFired or Sim.Events.SimEventKind.Damaged or Sim.Events.SimEventKind.ProjectileImpact) return;
                if (RangeLog.Length < 3000) RangeLog.AppendLine($"    {t:0.00} {e.Kind} {e.DefId} team {e.Team}");
            };
            // The range as the detail page runs it, with a camera that never draws (batch mode
            // without graphics crashed drawing the preview's render texture).
            var world = Field(runner, "_world") as MachineBrigade.Sim.SimWorld;
            var audio = Field(runner, "_audio") as MachineBrigade.Game.Audio.AudioDirector;
            if (_rangeCamera == null)
            {
                _rangeCamera = new GameObject("Probe Range Camera").AddComponent<Camera>();
                _rangeCamera.enabled = false;
                _rangeCamera.transform.position = new Vector3(0f, -600f, 0f);
            }
            _range?.Dispose();
            _range = new FiringRange(world.Catalog, Field(runner, "_materials") as MaterialLibrary, Field(runner, "_meshes") as MeshLibrary,
                Field(runner, "_models") as ModelLibrary, _rangeCamera, 31, id);
            if (audio != null)
            {
                _range.Sounds = audio.ConsumeRange;
                audio.ViewOverride = _rangeCamera;
                audio.ReachOverride = 90f;
            }
            MachineBrigade.Game.Audio.MusicDirector.Current?.Duck(0.45f);
            _rangeTicked = EditorApplication.timeSinceStartup;
            Line($"range {id}: open");
        }

        private static void EndRange()
        {
            FiringRange.Log = null;
            _range?.Dispose();
            _range = null;
            MachineBrigade.Game.Audio.MusicDirector.Current?.Duck(1f);
            var counts = new StringBuilder();
            foreach (var (k, v) in RangeCounts) counts.Append(k).Append('=').Append(v).Append(' ');
            Line($"range {Range[_rangeIndex]}: events {counts}");
            Report.Append(RangeLog);
        }

        /// <summary>Every playing audio source: its name, clip and volume (music decks by their track).</summary>
        private static string Census()
        {
            var text = new StringBuilder();
            var music = 0;
            foreach (var source in UnityEngine.Object.FindObjectsByType<AudioSource>())
            {
                if (!source.isPlaying || source.volume <= 0.001f) continue;
                var name = source.gameObject.name;
                if (source.clip != null && source.clip.name is "menu" or "boss" or "siege" or "battle_1" or "battle_2" or "battle_3") music++;
                text.Append($"{name}[{(source.clip != null ? source.clip.name : "-")} {source.volume:0.00}] ");
            }
            return $"music tracks {music}, listener {AudioListener.volume:0.00}: {text}";
        }

        /// <summary>Reads the profiler's new frames: each one's time, and the heaviest markers of any hitch.</summary>
        private static void Collect()
        {
            var last = ProfilerDriver.lastFrameIndex;
            var first = Math.Max(ProfilerDriver.firstFrameIndex, _processed + 1);
            for (var f = first; f <= last; f++)
            {
                _processed = f;
                using var view = ProfilerDriver.GetHierarchyFrameDataView(f, 0, HierarchyFrameDataView.ViewModes.MergeSamplesWithTheSameName,
                    HierarchyFrameDataView.columnSelfTime, false);
                if (view == null || !view.valid) continue;
                var ms = view.frameTimeMs;
                Frames.Add(ms);
                var samples = new List<(string name, float self)>();
                Walk(view, view.GetRootItemID(), samples);
                var editor = 0f;
                foreach (var (name, self) in samples)
                    if (name == "EditorLoop") editor += self;
                var game = Mathf.Max(0f, ms - editor);
                Game.Add(game);
                if (game < HitchMs && Frames.Count > 80) continue;
                if (game < 8f) continue;
                samples.Sort((a, b) => b.self.CompareTo(a.self));
                var top = new StringBuilder();
                for (var i = 0; i < Math.Min(8, samples.Count); i++) top.Append($"{samples[i].name}={samples[i].self:0.0} ");
                Line($"  frame {f} ({Frames.Count}th) {ms:0.0} ms, game {game:0.0} ms: {top}");
            }
        }

        private static void Walk(HierarchyFrameDataView view, int id, List<(string, float)> into)
        {
            var children = new List<int>();
            view.GetItemChildren(id, children);
            foreach (var child in children)
            {
                var self = view.GetItemColumnDataAsFloat(child, HierarchyFrameDataView.columnSelfTime);
                if (self >= 1f) into.Add((view.GetItemName(child), self));
                Walk(view, child, into);
            }
        }

        private static void Finish()
        {
            EditorApplication.update -= Tick;
            Application.logMessageReceivedThreaded -= OnLog;
            Collect();
            ProfilerDriver.enabled = false;
            Summary("all frames", 0, Frames.Count);
            if (_openFrame >= 0)
            {
                // The frames after the curtain lifted: the menu as the player sees it.
                var open = Mathf.Clamp(_openFrame - (_processed - Frames.Count + 1), 0, Frames.Count);
                Summary("behind the curtain", 0, open);
                Summary("first 5 s after the curtain", open, FramesWithin(open, 5000f));
                Summary("after the curtain", open, Frames.Count - open);
            }
            lock (Errors)
            {
                Line($"errors: {Errors.Count}");
                foreach (var e in Errors) Report.AppendLine(e.Length > 600 ? e.Substring(0, 600) : e);
            }
            File.WriteAllText(_out, Report.ToString());
            EditorApplication.isPlaying = false;
            EditorApplication.Exit(0);
        }

        private static int FramesWithin(int from, float ms)
        {
            var sum = 0f;
            var n = 0;
            for (var i = from; i < Frames.Count && sum < ms; i++, n++) sum += Frames[i];
            return n;
        }

        private static void Summary(string label, int from, int count)
        {
            Summary(label + " (frame)", Frames, from, count);
            Summary(label + " (game)", Game, from, count);
        }

        private static void Summary(string label, List<float> frames, int from, int count)
        {
            count = Math.Min(count, frames.Count - from);
            if (count <= 0) return;
            var list = frames.GetRange(from, count);
            var total = 0f;
            var over33 = 0;
            var over50 = 0;
            var over100 = 0;
            foreach (var f in list)
            {
                total += f;
                if (f > 33.3f) over33++;
                if (f > 50f) over50++;
                if (f > 100f) over100++;
            }
            list.Sort();
            Line($"{label}: {count} frames over {total / 1000f:0.0} s, p50 {list[count / 2]:0.0} ms, p95 {list[Mathf.Min(count - 1, (int)(count * 0.95f))]:0.0} ms, " +
                 $"p99 {list[Mathf.Min(count - 1, (int)(count * 0.99f))]:0.0} ms, max {list[count - 1]:0.0} ms, >33 ms {over33}, >50 ms {over50}, >100 ms {over100}");
        }

        private static object Field(object o, string name) =>
            o.GetType().GetField(name, BindingFlags.NonPublic | BindingFlags.Instance)?.GetValue(o);

        private static void Line(string text)
        {
            Report.AppendLine(text);
            Debug.Log("[StartupProbe] " + text);
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
