using System.Collections.Generic;
using System.IO;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Test feedback 2 (DECISIONS 12F): an aircraft's attack hold from the game's camera angle, with
    /// its fire drawn. One row per aircraft, six moments: coming in, early in the hold, mid-hold, the
    /// end of the hold, breaking away (the climb), turning back in. The moments are found by a dry
    /// run of the same deterministic battle. Batch mode (with graphics): -executeMethod
    /// MachineBrigade.Editor.AirHoldShots.Run -mbShotsOut &lt;folder&gt;.
    /// </summary>
    public static class AirHoldShots
    {
        private const string ProfilePath = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset";
        private const int CellW = 400, CellH = 300, Moments = 6;
        private const float Step = 0.05f;

        private static readonly (string shooter, string target)[] Cases =
            { ("fighter_jet", "attack_helicopter"), ("attack_jet", "main_battle_tank") };

        [MenuItem("Machine Brigade/Render Air Attack Hold Shots")]
        public static void Run()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/air_hold_shots");
            Directory.CreateDirectory(output);
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20260929);
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var catalog = GameContent.LoadCatalog();
            var root = new GameObject("Air Hold Shots").transform;
            Stage(materials, root);
            var camera = MakeCamera(root);
            var rt = new RenderTexture(CellW, CellH, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            camera.Render();
            var log = new System.Text.StringBuilder();
            var sheet = new Texture2D(CellW * Moments, CellH * Cases.Length, TextureFormat.RGB24, false);
            VehicleView.ShotStep = Step;
            try
            {
                for (var row = 0; row < Cases.Length; row++)
                {
                    var (shooterId, targetId) = Cases[row];
                    var times = FindMoments(catalog, shooterId, targetId);
                    log.AppendLine($"{shooterId} vs {targetId}: moments {string.Join(", ", times)}");
                    Shoot(catalog, models, meshes, materials, root, camera, rt, sheet, shooterId, targetId, times, Cases.Length - 1 - row, log);
                }
            }
            finally
            {
                VehicleView.ShotStep = -1f;
            }
            sheet.Apply();
            File.WriteAllBytes(Path.Combine(output, "air_hold.png"), sheet.EncodeToPNG());
            File.WriteAllText(Path.Combine(output, "air_hold.txt"), log.ToString());
            Debug.Log("[AirHoldShots] wrote " + Path.GetFullPath(output) + "\n" + log);
            camera.targetTexture = null;
            rt.Release();
            models.Dispose();
            materials.Dispose();
        }

        private static SimWorld World(Catalog catalog, string shooterId, string targetId, out Vehicle shooter, out Vehicle target)
        {
            var map = new MapDefinition("shots", 260f,
                new[] { new TeamStart(0, new Vector2(0f, -100f)), new TeamStart(1, new Vector2(0f, 100f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());
            var world = new SimWorld(catalog, map, seed: 5);
            shooter = world.SpawnVehicle(shooterId, 0, new Vector2(0f, -35f), 0f);
            target = world.SpawnVehicle(targetId, 1, new Vector2(0f, 35f), Mathf.PI);
            // A dummy: it never fires back and is never destroyed.
            world.MakeDummy(target);
            world.Submit(new Command(CommandType.AttackMove, 0, new[] { shooter.Id }, target.Position));
            return world;
        }

        /// <summary>A dry run: the sim times of the six moments of the second hold (the first after a full loop).</summary>
        private static List<double> FindMoments(Catalog catalog, string shooterId, string targetId)
        {
            var world = World(catalog, shooterId, targetId, out var shooter, out _);
            var starts = new List<double>();
            var ends = new List<double>();
            var turns = new List<double>();
            bool wasHold = false, wasBreak = false;
            for (var t = 0f; t < 40f; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
                if (shooter.InAttackHold && !wasHold) starts.Add(world.Time);
                if (!shooter.InAttackHold && wasHold) ends.Add(world.Time);
                if (!shooter.Breaking && wasBreak) turns.Add(world.Time);
                wasHold = shooter.InAttackHold;
                wasBreak = shooter.Breaking;
            }
            var k = starts.Count > 1 ? 1 : 0;
            var start = starts.Count > k ? starts[k] : 5.0;
            var end = ends.Count > k ? ends[k] : start + 3.5;
            var turn = turns.Count > k ? turns[k] : end + 2.0;
            return new List<double> { start - 1.0, start + 0.6, (start + end) * 0.5, end - 0.15, end + 0.9, turn + 0.9 };
        }

        private static void Shoot(Catalog catalog, ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials, Transform root,
            Camera camera, RenderTexture rt, Texture2D sheet, string shooterId, string targetId, List<double> times, int row,
            System.Text.StringBuilder log)
        {
            var holder = new GameObject(shooterId).transform;
            holder.SetParent(root, false);
            var world = World(catalog, shooterId, targetId, out var shooter, out var target);
            var views = new ViewRegistry(models, meshes, materials, holder, 0);
            var tracers = new TracerPool(meshes.Box, materials.Tracer, holder, 128);
            var projectiles = new ProjectilePool(holder, 48);
            var emitters = new Emitters(materials, holder);
            var muzzle = new MuzzleFx(materials, holder);
            var weapons = new WeaponEffects(catalog, models, tracers, projectiles, emitters, muzzle, (_, _) => { });
            views.Add(shooter);
            views.Add(target);
            var col = 0;
            for (var t = 0f; t < 40f && col < times.Count; t += Step)
            {
                world.Step(Step);
                VehicleView.ShotClock += Step;
                views.SnapshotAll();
                views.Render(1f, camera.transform.rotation);
                var now = (float)world.Time;
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired) weapons.Fired(e, views, now);
                world.ClearEvents();
                tracers.Tick(now, emitters);
                projectiles.Tick(now, emitters);
                muzzle.Tick(now);
                emitters.Tick(now, Step);
                foreach (var ps in holder.GetComponentsInChildren<ParticleSystem>()) ps.Simulate(Step, false, false, false);
                if (world.Time + 1e-6 < times[col]) continue;
                if (!views.TryGet(shooter.Id, out var jet) || !views.TryGet(target.Id, out var aimed)) break;
                var a = jet.Position;
                var b = aimed.Position;
                var span = Vector3.Distance(new Vector3(a.x, 0f, a.z), new Vector3(b.x, 0f, b.z));
                Frame(camera, (a + b) * 0.5f, Mathf.Clamp(span * 0.62f, 12f, 34f));
                Snap(camera, rt, sheet, col, row);
                log.AppendLine($"  t {world.Time:0.00}: speed {shooter.Speed:0.0} gap {Vector2.Distance(shooter.Position, target.Position):0.0} " +
                               $"{(shooter.InAttackHold ? "hold" : shooter.Breaking ? "break" : "run")} pitch/bank {jet.Body.localEulerAngles.x:0}/{jet.Body.localEulerAngles.z:0} alt {jet.Altitude:0.0}");
                col++;
            }
            Object.DestroyImmediate(holder.gameObject);
        }

        private static void Frame(Camera camera, Vector3 centre, float halfHeight)
        {
            camera.orthographicSize = halfHeight;
            camera.transform.position = centre - camera.transform.forward * 160f;
        }

        private static void Snap(Camera camera, RenderTexture rt, Texture2D sheet, int col, int row)
        {
            camera.Render();
            RenderTexture.active = rt;
            var frame = new Texture2D(CellW, CellH, TextureFormat.RGB24, false);
            frame.ReadPixels(new Rect(0, 0, CellW, CellH), 0, 0);
            frame.Apply();
            sheet.SetPixels(col * CellW, row * CellH, CellW, CellH, frame.GetPixels());
            Object.DestroyImmediate(frame);
            RenderTexture.active = null;
        }

        private static void Stage(MaterialLibrary materials, Transform root)
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.transform.SetParent(root, false);
            ground.transform.localScale = new Vector3(40f, 1f, 40f);
            var grass = new Material(materials.Ground);
            grass.SetColor("_BaseColor", new Color(0.46f, 0.52f, 0.36f));
            ground.GetComponent<Renderer>().sharedMaterial = grass;
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.transform.SetParent(root, false);
            sun.type = LightType.Directional;
            sun.intensity = 1.6f;
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.55f, 0.58f, 0.62f);
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
            if (profile == null) return;
            var volume = new GameObject("Post").AddComponent<Volume>();
            volume.transform.SetParent(root, false);
            volume.isGlobal = true;
            volume.sharedProfile = profile;
        }

        private static Camera MakeCamera(Transform root)
        {
            var camera = new GameObject("Shot Camera").AddComponent<Camera>();
            camera.transform.SetParent(root, false);
            camera.orthographic = true;
            camera.transform.rotation = Quaternion.Euler(52f, -45f, 0f);
            camera.nearClipPlane = 1f;
            camera.farClipPlane = 400f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.5f, 0.55f, 0.6f);
            camera.allowHDR = true;
            camera.GetUniversalAdditionalCameraData().renderPostProcessing = true;
            return camera;
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
