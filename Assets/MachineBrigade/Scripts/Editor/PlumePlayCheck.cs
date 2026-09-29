using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.LowLevel;
using UnityEngine.SceneManagement;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Whether a motor's flame sits on its missile's tail in real frames (DECISIONS 13E): in Play mode, through
    /// Unity's own player loop at a fixed 30 and then 60 fps (Time.captureFramerate). The effects are driven
    /// in Update as the game does (ProjectilePool.Tick, then Emitters.Tick), Unity's particle update runs
    /// as in the game, and each frame, just before it is drawn (the end of PostLateUpdate), the white-hot
    /// core born that frame is measured against the drawn tail; a camera follows the round, so the
    /// plume's systems are never culled. New rounds are launched in the late phase, as LaunchShots does.
    /// Fast rockets (thermobaric, MLRS, Hydra) and a SAM and an ATGM. Batch mode with graphics:
    /// -executeMethod MachineBrigade.Editor.PlumePlayCheck.Run -mbPlumeOut &lt;file&gt; (without -quit).
    /// </summary>
    public static class PlumePlayCheck
    {
        private static readonly (string weapon, string model, ProjectileKind kind, float distance)[] Cases =
        {
            ("thermobaric_rockets", "tos_rocket", ProjectileKind.Rocket, 60f),
            ("mlrs_rockets", "gmlrs", ProjectileKind.Rocket, 70f),
            ("heli_rockets", "hydra", ProjectileKind.Rocket, 36f),
            ("sam_long", "buk", ProjectileKind.Missile, 55f),
            ("atgm", "atgm_tow", ProjectileKind.Missile, 34f),
        };

        private static readonly int[] Rates = { 30, 60 };

        private sealed class Drive { }

        private sealed class Measure { }

        private static string _out;
        private static PlayerLoopSystem _original;
        private static bool _hooked, _done;
        private static Catalog _catalog;
        private static MaterialLibrary _materials;
        private static ModelLibrary _models;
        private static Transform _holder;
        private static Emitters _emitters;
        private static ProjectilePool _pool;
        private static ParticleSystem _core;
        private static Camera _camera;
        private static int _case = -1, _rate;
        private static Transform _shot;
        private static float _tail, _gap, _side, _dtSeen;
        private static int _frames, _skip;
        private static bool _launched;
        private static readonly ParticleSystem.Particle[] Particles = new ParticleSystem.Particle[4096];
        private static readonly StringBuilder Report = new();
        private static readonly List<float> Worst = new();

        public static void Run()
        {
            _out = Argument("-mbPlumeOut") ?? "plume_play.txt";
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            EditorApplication.update += Tick;
            EditorApplication.isPlaying = true;
        }

        private static void Tick()
        {
            if (_done)
            {
                if (!EditorApplication.isPlaying)
                {
                    EditorApplication.update -= Tick;
                    EditorApplication.Exit(0);
                }
                return;
            }
            if (!EditorApplication.isPlaying || _hooked) return;
            _hooked = true;
            _catalog = GameContent.LoadCatalog();
            _materials = new MaterialLibrary();
            _models = new ModelLibrary(_materials);
            _holder = new GameObject("Plume Play Check").transform;
            _emitters = new Emitters(_materials, _holder);
            _pool = new ProjectilePool(_holder, 8);
            _core = _holder.GetComponentsInChildren<ParticleSystem>().First(p => p.name == "Motor Core");
            _camera = new GameObject("Plume Camera").AddComponent<Camera>();
            _camera.orthographic = true;
            _camera.orthographicSize = 6f;
            var light = new GameObject("Sun").AddComponent<Light>();
            light.type = LightType.Directional;
            Report.AppendLine($"Motor Core: cullingMode {_core.main.cullingMode}, loop {_core.main.loop}, procedural {_core.proceduralSimulationSupported}");
            _original = PlayerLoop.GetCurrentPlayerLoop();
            var loop = _original;
            Append(ref loop, typeof(UnityEngine.PlayerLoop.Update), new PlayerLoopSystem { type = typeof(Drive), updateDelegate = OnUpdate });
            Append(ref loop, typeof(UnityEngine.PlayerLoop.PostLateUpdate), new PlayerLoopSystem { type = typeof(Measure), updateDelegate = OnDraw });
            PlayerLoop.SetPlayerLoop(loop);
            _rate = 0;
            Time.captureFramerate = Rates[_rate];
            Next();
        }

        private static void Append(ref PlayerLoopSystem loop, System.Type phase, PlayerLoopSystem system)
        {
            var subs = loop.subSystemList;
            for (var i = 0; i < subs.Length; i++)
            {
                if (subs[i].type != phase) continue;
                var list = new List<PlayerLoopSystem>(subs[i].subSystemList ?? new PlayerLoopSystem[0]) { system };
                subs[i].subSystemList = list.ToArray();
            }
            loop.subSystemList = subs;
        }

        /// <summary>Moves to the next case (and rate); the round is launched in the late phase.</summary>
        private static void Next()
        {
            if (_case >= 0)
            {
                var (weapon, _, _, _) = Cases[_case];
                Report.AppendLine($"{weapon} at {Rates[_rate]} fps (dt {_dtSeen * 1000f:0.0} ms): {_frames} frames, flame core front {_gap:+0.000;-0.000} m from the drawn tail (worst), {_side:0.000} m off its line");
                Worst.Add(Mathf.Abs(_gap));
            }
            _case++;
            if (_case >= Cases.Length)
            {
                _case = 0;
                _rate++;
                if (_rate >= Rates.Length)
                {
                    Finish();
                    return;
                }
                Time.captureFramerate = Rates[_rate];
            }
            _launched = false;
            _shot = null;
            _gap = 0f;
            _side = 0f;
            _frames = 0;
            _skip = 3; // let the frame rate settle before launching
        }

        private static void OnUpdate()
        {
            if (_done || !EditorApplication.isPlaying || _pool == null) return;
            // As EffectsDirector.Tick: the rounds, then the emitters.
            _pool.Tick(Time.time, _emitters);
            _emitters.Tick(Time.time, Time.deltaTime);
            if (_shot != null)
            {
                _camera.transform.rotation = Quaternion.Euler(52f, -45f, 0f);
                _camera.transform.position = _shot.position - _camera.transform.forward * 40f;
            }
        }

        private static void OnDraw()
        {
            if (_done || !EditorApplication.isPlaying || _pool == null) return;
            if (!_launched)
            {
                if (_skip-- > 0) return;
                Launch();
                return;
            }
            if (_shot == null || !_shot.gameObject.activeSelf)
            {
                Next();
                return;
            }
            _dtSeen = Time.deltaTime;
            var forward = _shot.forward;
            var nozzle = _shot.TransformPoint(new Vector3(0f, 0f, _tail));
            var count = _core.GetParticles(Particles);
            var front = float.MinValue;
            var side = 0f;
            for (var i = 0; i < count; i++)
            {
                var p = Particles[i];
                if (p.startLifetime - p.remainingLifetime > Time.deltaTime * 1.01f) continue;
                var d = p.position - nozzle;
                // The core is set a tenth of the flame's width behind the nozzle, its size 0.8 of that width.
                var along = Vector3.Dot(d, forward) + p.startSize * 0.125f;
                if (along <= front) continue;
                front = along;
                side = (d - forward * Vector3.Dot(d, forward)).magnitude;
            }
            if (front == float.MinValue) return;
            _frames++;
            if (Mathf.Abs(front) > Mathf.Abs(_gap)) _gap = front;
            _side = Mathf.Max(_side, side);
        }

        private static void Launch()
        {
            var (id, model, kind, distance) = Cases[_case];
            var weapon = _catalog.Weapons[id];
            var chunk = _models.Merged(model);
            var from = new Vector3(0f, 2.5f, 0f);
            var to = new Vector3(distance * 0.8f, 0.4f, distance * 0.6f);
            var artillery = weapon.MinRange > 0f;
            var barrel = ((to - from).normalized + Vector3.up * (artillery ? 0.8f : 0.1f)).normalized;
            _pool.Launch(chunk, from, to, distance / weapon.ProjectileSpeed, kind == ProjectileKind.Missile ? distance * 0.06f : distance * 0.02f, 0.55f, Time.time,
                boost: kind == ProjectileKind.Missile ? 0.55f : artillery ? 0.2f : 0.3f,
                scale: weapon.ProjectileScale * WeaponEffects.SizeOf(weapon, kind, model, false),
                control: artillery ? WeaponEffects.Bend(from, to, barrel) : WeaponEffects.Leave(from, to, barrel, distance * 0.02f),
                plume: Plume.For(weapon, kind, model, false));
            _shot = _holder.GetComponentsInChildren<MeshFilter>(true).First(f => f.sharedMesh == chunk.Mesh && f.gameObject.activeSelf).transform;
            _tail = chunk.Mesh.bounds.min.z;
            _launched = true;
        }

        private static void Finish()
        {
            _done = true;
            Time.captureFramerate = 0;
            PlayerLoop.SetPlayerLoop(_original);
            var worst = Worst.Count > 0 ? Worst.Max() : float.NaN;
            Report.AppendLine($"PLUME PLAY worst {worst:0.000} m");
            File.WriteAllText(_out, Report.ToString());
            Debug.Log("PLUME PLAY\n" + Report);
            EditorApplication.isPlaying = false;
        }

        private static string Argument(string name)
        {
            var args = System.Environment.GetCommandLineArgs();
            for (var i = 0; i < args.Length - 1; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }
    }
}
