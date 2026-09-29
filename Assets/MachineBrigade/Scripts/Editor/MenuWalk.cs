using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// A Play-mode walk through the real menu to a campaign battle (play-test 6, DECISIONS 21B): taps
    /// go to the panel at an element's centre, so whatever is on top there takes them, as a finger's
    /// would. Home, Campaign, the mission's chapter, its row, Start, then each story card's main button
    /// until the battle loads; every tap reports what was on top, and every error is logged. The
    /// profile is in memory only and nothing is saved (the editor's prefs are shared by every tree).
    /// -executeMethod MachineBrigade.Editor.MenuWalk.Run -mbWalkOut &lt;txt&gt; [-mbWalkProfile fresh|old|demo|prefs]
    /// [-mbWalkMission c1m01|next] [-mbWalkBack &lt;n&gt;] (Back pressed n times at home first). Exit code 0 when the battle started clean.
    /// </summary>
    public static class MenuWalk
    {
        private static readonly StringBuilder Report = new();
        private static readonly List<string> Errors = new();
        private static readonly BindingFlags Any = BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance;
        private static string _out, _mission;
        private static int _backs, _step, _storyTaps;
        private static double _wait, _deadline, _battleAt;
        private static bool _pressed;
        private static BattleHud _hookedHud;
        private static MatchRunner _pressedIn;

        /// <summary>A save from before prompt 20 (the nine-chapter story, the old roster): chapter 1 half won.</summary>
        private const string OldSave =
            "{\"campaignVersion\":2,\"rosterVersion\":1,\"gearVersion\":4,\"coins\":900,\"xp\":600," +
            "\"missionIds\":[\"c1m01\",\"c1m02\",\"c1m03\"],\"missionStars\":[3,2,1],\"missionTiers\":[0,0,0],\"chaptersSeen\":[1]," +
            "\"unlocked\":[\"light_tank\",\"apc\"],\"owned\":[\"heavy_attack_heli\"]}";

        public static void Run()
        {
            _out = Arg("-mbWalkOut") ?? "walk.txt";
            _mission = Arg("-mbWalkMission") ?? "c1m01";
            _backs = int.TryParse(Arg("-mbWalkBack"), out var b) ? b : 0;
            var profile = Arg("-mbWalkProfile") ?? "fresh";
            MatchSettings.SaveSuspended = true;
            switch (profile)
            {
                case "old": PlayerProfile.LoadForTests(OldSave); break;
                case "demo": DemoProfile.Use(); break;
                case "prefs": PlayerProfile.LoadForTests(PlayerPrefs.GetString("mb.profile", "{}")); break;
                default: PlayerProfile.LoadForTests("{}"); break;
            }
            Line($"profile {profile}, mission {_mission}, back x{_backs}");
            Application.logMessageReceivedThreaded += OnLog;
            EditorSceneManager.OpenScene("Assets/MachineBrigade/Scenes/Sandbox.unity");
            EditorApplication.update += Tick;
            _deadline = EditorApplication.timeSinceStartup + 240;
            EditorApplication.isPlaying = true;
        }

        private static void OnLog(string message, string stack, LogType type)
        {
            if (type != LogType.Error && type != LogType.Exception && type != LogType.Assert) return;
            if (stack != null && stack.Contains("UnityEditor.Search.")) return;
            lock (Errors) Errors.Add($"[step {_step}] {type}: {message}\n{stack}");
        }

        private static void Tick()
        {
            if (!EditorApplication.isPlaying) return;
            var now = EditorApplication.timeSinceStartup;
            if (now > _deadline)
            {
                Line($"TIMEOUT at step {_step}");
                Finish(false);
                return;
            }
            if (now < _wait) return;
            var runner = UnityEngine.Object.FindFirstObjectByType<MatchRunner>();
            if (runner == null || !(bool)Field(runner, "_built") || Curtain.Busy) return;
            var hud = Field(runner, "_hud") as BattleHud;
            if (hud != _hookedHud && hud != null)
            {
                _hookedHud = hud;
                hud.PlayPressed += () =>
                {
                    _pressed = true;
                    _pressedIn = UnityEngine.Object.FindFirstObjectByType<MatchRunner>();
                    Line($"  PlayPressed: mode {MatchSettings.Mode}, mission {MatchSettings.Mission}, curtain busy {Curtain.Busy}");
                };
            }
            if (_pressed)
            {
                // The battle scene: report it once it has run a few seconds.
                if (runner == _pressedIn) return;
                if (_battleAt == 0) _battleAt = now + 5;
                if (now < _battleAt) return;
                Line($"battle: {State(runner)}");
                Finish(MatchSettings.Mode == GameModeKind.Campaign && MatchSettings.Mission == _mission);
                return;
            }
            var menu = Field(hud, "_menu") as MenuScreen;
            if (_pressed) return;
            if (menu == null) return;
            var root = menu.Root;
            _wait = now + 0.6;
            var mission = _mission == "next" ? Campaign.All[Campaign.Next] : Campaign.Get(_mission);
            if (_mission == "next") _mission = mission.Id;
            switch (_step)
            {
                case 0:
                    Line($"menu up; mission {mission.Id} ({Campaign.Label(mission)}) open {Campaign.IsOpen(Campaign.IndexOf(mission.Id))}, map {Campaign.MapExists(mission)}, chapter {mission.Chapter} seen {PlayerProfile.ChapterSeen(mission.Chapter)}");
                    Line($"  deck {string.Join(" ", MatchSettings.DeckVehicles)} | {string.Join(" ", MatchSettings.DeckSupports)}");
                    for (var i = 0; i < _backs; i++) Line($"  Back -> {hud.MenuBack()}");
                    Line($"  story card in the menu: {Story(menu)}");
                    _step++;
                    break;
                case 1:
                    Tap(root.Query<KitNavItem>().ToList().FirstOrDefault(n => n.Q<Label>(className: "fc-nav-item__label")?.text == Kit.Caps(Strings.Get("nav.campaign"))), "nav Campaign");
                    _step++;
                    break;
                case 2:
                {
                    var shown = Campaign.ShownChapters.ToList();
                    var at = shown.FindIndex(c => c.Number == mission.Chapter);
                    var cards = root.Query(className: "fc-chapter").ToList();
                    Tap(at >= 0 && at < cards.Count ? cards[at] : null, $"chapter {mission.Chapter} card ({at}/{cards.Count})");
                    _step++;
                    break;
                }
                case 3:
                {
                    var label = Campaign.Label(mission);
                    var row = root.Query(className: "fc-mission").ToList().FirstOrDefault(r => r.Q<Label>(className: "fc-mission__number")?.text == label);
                    row?.GetFirstAncestorOfType<ScrollView>()?.ScrollTo(row);
                    _wait = now + 0.3;
                    _step++;
                    break;
                }
                case 4:
                {
                    var label = Campaign.Label(mission);
                    var row = root.Query(className: "fc-mission").ToList().FirstOrDefault(r => r.Q<Label>(className: "fc-mission__number")?.text == label);
                    Tap(row, $"mission row {label}");
                    _step++;
                    break;
                }
                case 5:
                {
                    var start = root.Q<KitButton>(className: "fc-campaign__start");
                    Line($"  start: disabled {start?.Disabled} reason '{start?.Reason}'");
                    Tap(start, "Start");
                    _step++;
                    break;
                }
                default:
                {
                    // The chapter card and the briefing: their main button, until PlayPressed.
                    Line($"  story card: {Story(menu)}");
                    var story = root.Q(className: "fc-story-scrim");
                    if (story == null || story.resolvedStyle.display == DisplayStyle.None || _storyTaps >= 3)
                    {
                        Line("  STUCK: no story card on screen and no battle launched");
                        Finish(false);
                        return;
                    }
                    var buttons = story.Q(className: "fc-story__buttons").Query<KitButton>().ToList();
                    Tap(buttons.LastOrDefault(), $"story main button '{buttons.LastOrDefault()?.Label}'");
                    _storyTaps++;
                    _step++;
                    break;
                }
            }
        }

        private static string Story(MenuScreen menu)
        {
            var card = Field(menu, "_story");
            var element = card?.GetType().GetProperty("Root")?.GetValue(card) as VisualElement;
            if (element == null) return "none";
            return $"attached {element.panel != null}, parent {Describe(element.parent)}, display {element.style.display.value}";
        }

        /// <summary>A pointer press and release at the element's centre, sent to its panel: the element on top there takes it.</summary>
        private static void Tap(VisualElement target, string what)
        {
            if (target == null || target.panel == null)
            {
                Line($"  tap {what}: NOT FOUND");
                return;
            }
            var panel = target.panel;
            var at = target.worldBound.center;
            var top = panel.Pick(at);
            var hit = top != null && (top == target || target.Contains(top));
            Line($"  tap {what} at {at}: top {Describe(top)} -> {(hit ? "ok" : "COVERED")}");
            Send(panel, EventType.MouseDown, at);
            Send(panel, EventType.MouseUp, at);
        }

        private static void Send(IPanel panel, EventType type, Vector2 at)
        {
            var e = new Event { type = type, mousePosition = at, button = 0, clickCount = 1 };
            if (type == EventType.MouseDown)
            {
                using var down = PointerDownEvent.GetPooled(e);
                panel.visualTree.SendEvent(down);
            }
            else
            {
                using var up = PointerUpEvent.GetPooled(e);
                panel.visualTree.SendEvent(up);
            }
        }

        private static string Describe(VisualElement e) =>
            e == null ? "null" : $"{e.GetType().Name}#{e.name}.{string.Join(".", e.GetClasses().Take(3))}";

        private static object Field(object o, string name) => o?.GetType().GetField(name, Any)?.GetValue(o);

        private static string State(MatchRunner runner)
        {
            var world = Field(runner, "_world") as MachineBrigade.Sim.SimWorld;
            return world == null ? "no world" : $"mode {MatchSettings.Mode}, mission {MatchSettings.Mission}, tick {world.Tick}, vehicles {world.Vehicles.Count(v => v.IsAlive)}";
        }

        private static void Finish(bool launched)
        {
            EditorApplication.update -= Tick;
            Application.logMessageReceivedThreaded -= OnLog;
            lock (Errors)
            {
                Line($"launched {launched}, errors {Errors.Count}");
                foreach (var e in Errors.Distinct().Take(20)) Report.AppendLine(e.Length > 1500 ? e.Substring(0, 1500) : e).AppendLine();
            }
            File.WriteAllText(_out, Report.ToString());
            MatchSettings.SaveSuspended = false;
            EditorApplication.isPlaying = false;
            EditorApplication.Exit(launched && Errors.Count == 0 ? 0 : 1);
        }

        private static void Line(string text) => Report.AppendLine(text);

        private static string Arg(string name)
        {
            var args = Environment.GetCommandLineArgs();
            for (var i = 0; i < args.Length - 1; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }
    }
}
