using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using Unity.Profiling;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Debug = UnityEngine.Debug;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Renders the vehicles' detail levels side by side from the game's camera angle, with the
    /// game's lighting and post-processing, so a level change that pops can be seen and fixed:
    /// full model, simplified model and impostor at the sizes where each takes over, the impostor
    /// atlas itself, and a hundred-vehicle crowd at each level with its triangle and draw counts.
    /// Batch mode (with graphics): -executeMethod MachineBrigade.Editor.LodShots.Compare -mbShotsOut &lt;folder&gt;.
    /// </summary>
    public static class LodShots
    {
        private const string ProfilePath = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset";

        private static readonly string[] Models =
        {
            "main_battle_tank", "light_tank", "scout_jeep", "artillery", "sam_launcher", "attack_helicopter", "fighter_jet",
            "heavy_aa", "grad_truck", "guard_tower", "behemoth",
        };

        private static readonly string[] Crowd =
        {
            "main_battle_tank", "light_tank", "heavy_tank", "apc", "ifv", "scout_jeep", "artillery", "mlrs", "aa_vehicle",
            "tank_destroyer", "armored_car", "sam_launcher", "attack_helicopter", "grad_truck", "flame_tank", "heavy_aa",
            "mortar_carrier", "howitzer", "twin_tank", "rocket_technical",
        };

        [MenuItem("Machine Brigade/Render LOD Shots")]
        public static void Compare()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/lod");
            Directory.CreateDirectory(output);
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("Shots").transform;
            var sun = Stage(root);
            var atmosphere = new Atmosphere(GraphicsOptions.For(GraphicsQuality.High));
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var atlas = new ImpostorAtlas(materials);
            var camera = Camera(root);
            try
            {
                var rotation = camera.transform.rotation;
                // Full detail up close, the simplified model where it takes over and just past it, and the impostor.
                Sheet(output, "lod_near.png", models, atlas, atmosphere, camera, root, 150f, 3, 1);
                Sheet(output, "lod_switch.png", models, atlas, atmosphere, camera, root, VehicleLod.DetailPixels * 0.86f, 3, 1);
                Sheet(output, "lod_far.png", models, atlas, atmosphere, camera, root, VehicleLod.ImpostorPixels * 0.86f, 3, 4);
                Sheet(output, "lod_impostor_switch.png", models, atlas, atmosphere, camera, root, VehicleLod.ImpostorPixels * 1.2f, 3, 4);
                DumpAtlas(output, atlas);
                CrowdStats(output, models, atlas, atmosphere, camera, root, rotation);
            }
            finally
            {
                atlas.Dispose();
                models.Dispose();
                materials.Dispose();
                atmosphere.Dispose();
                Object.DestroyImmediate(sun.gameObject);
            }
        }

        /// <summary>One row per model: full, simplified, impostor, each <paramref name="pixels"/> across, shown <paramref name="zoom"/> times.</summary>
        private static void Sheet(string folder, string name, ModelLibrary models, ImpostorAtlas atlas, Atmosphere atmosphere, Camera camera,
            Transform root, float pixels, int levels, int zoom)
        {
            var cell = Mathf.CeilToInt(pixels * 1.6f / 8f) * 8;
            var shown = cell * zoom;
            var sheet = new Texture2D(shown * levels, shown * Models.Length, TextureFormat.RGB24, false);
            var rt = new RenderTexture(cell, cell, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            var frame = new Texture2D(cell, cell, TextureFormat.RGB24, false);
            for (var row = 0; row < Models.Length; row++)
            {
                var id = Models[row];
                if (!models.Has(id)) continue;
                var model = models.Spawn(id, 1, root, lod: true);
                var t = model.Root.transform;
                // Between two baked headings, so the impostor's blend is on show too.
                t.rotation = Quaternion.Euler(0f, 20f, 0f);
                var lod = model.Lod;
                var page = atlas.Request(lod, 1);
                atlas.BakePending(camera.transform.rotation, 64);
                var size = Mathf.Max(lod.Length, 1f);
                var centre = page != null ? page.Centre : Vector3.up;
                if (lod.BakeBounds.size.y > 6f) centre = new Vector3(0f, lod.BakeBounds.center.y, 0f);
                camera.orthographicSize = cell / (2f * pixels / size);
                camera.transform.position = centre - camera.transform.forward * 80f;
                atmosphere.FitShadows(camera);
                for (var level = 0; level < levels; level++)
                {
                    foreach (var r in model.Renderers) r.enabled = level == 0;
                    foreach (var r in model.Lod1Renderers) r.gameObject.SetActive(level == 1);
                    atlas.Begin();
                    if (level == 2 && page != null) atlas.Add(page, t.position + Vector3.up * page.Centre.y, 1f, t.eulerAngles.y, Color.white);
                    atlas.Flush();
                    camera.Render();
                    RenderTexture.active = rt;
                    frame.ReadPixels(new Rect(0, 0, cell, cell), 0, 0);
                    frame.Apply();
                    RenderTexture.active = null;
                    var pixelsOut = frame.GetPixels();
                    for (var y = 0; y < shown; y++)
                    for (var x = 0; x < shown; x++)
                        sheet.SetPixel(level * shown + x, (Models.Length - 1 - row) * shown + y, pixelsOut[(y / zoom) * cell + x / zoom]);
                }
                Object.DestroyImmediate(model.Root);
            }
            atlas.Begin();
            atlas.Flush();
            sheet.Apply();
            File.WriteAllBytes(Path.Combine(folder, name), sheet.EncodeToPNG());
            Debug.Log($"[LodShots] wrote {Path.Combine(folder, name)} ({pixels:0} px across)");
            camera.targetTexture = null;
            rt.Release();
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(frame);
            Object.DestroyImmediate(sheet);
        }

        private static void DumpAtlas(string folder, ImpostorAtlas atlas)
        {
            var index = 0;
            foreach (var (albedo, surface) in atlas.Sheets())
            {
                foreach (var (texture, kind) in new[] { (albedo, "albedo"), (surface, "surface") })
                {
                    if (texture == null) continue;
                    var read = new Texture2D(texture.width, texture.height, TextureFormat.RGBA32, false, kind == "surface");
                    RenderTexture.active = texture;
                    read.ReadPixels(new Rect(0, 0, texture.width, texture.height), 0, 0);
                    read.Apply();
                    RenderTexture.active = null;
                    // Coverage shown against grey, so empty cells read as empty.
                    var pixels = read.GetPixels();
                    for (var i = 0; i < pixels.Length; i++)
                        pixels[i] = Color.Lerp(new Color(0.3f, 0.3f, 0.32f), new Color(pixels[i].r, pixels[i].g, pixels[i].b), pixels[i].a > 0f ? 1f : 0f);
                    read.SetPixels(pixels);
                    read.Apply();
                    File.WriteAllBytes(Path.Combine(folder, $"atlas_{index}_{kind}.png"), read.EncodeToPNG());
                    Object.DestroyImmediate(read);
                }
                index++;
            }
        }

        /// <summary>A hundred vehicles in a grid at the widest game zoom (1080 px high), each level in turn: triangles, draws and render time.</summary>
        private static void CrowdStats(string folder, ModelLibrary models, ImpostorAtlas atlas, Atmosphere atmosphere, Camera camera,
            Transform root, Quaternion rotation)
        {
            var spawned = new List<ModelInstance>();
            var pages = new List<ImpostorPage>();
            for (var i = 0; i < 100; i++)
            {
                var id = Crowd[i % Crowd.Length];
                if (!models.Has(id)) continue;
                var m = models.Spawn(id, i % 2, root, lod: true);
                m.Root.transform.position = new Vector3((i % 10 - 4.5f) * 10f, 0f, (i / 10 - 4.5f) * 10f);
                m.Root.transform.rotation = Quaternion.Euler(0f, i * 37f, 0f);
                if (id == "attack_helicopter") m.Root.transform.position += Vector3.up * 8f;
                spawned.Add(m);
                pages.Add(atlas.Request(m.Lod, i % 2));
            }
            atlas.BakePending(rotation, 256);
            var rt = new RenderTexture(1920, 1080, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            camera.orthographicSize = 42f;
            camera.transform.position = -camera.transform.forward * 130f;
            atmosphere.FitShadows(camera);
            var report = new StringBuilder();
            using var draws = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Draw Calls Count");
            using var batches = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Batches Count");
            using var triangles = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Triangles Count");
            using var setPass = ProfilerRecorder.StartNew(ProfilerCategory.Render, "SetPass Calls Count");
            for (var level = 0; level < 3; level++)
            {
                foreach (var m in spawned)
                {
                    foreach (var r in m.Renderers) r.enabled = level == 0;
                    foreach (var r in m.Lod1Renderers) r.gameObject.SetActive(level == 1);
                }
                var watch = new Stopwatch();
                var frames = 20;
                for (var f = 0; f < frames + 2; f++)
                {
                    atlas.Begin();
                    if (level == 2)
                        for (var i = 0; i < spawned.Count; i++)
                        {
                            var t = spawned[i].Root.transform;
                            atlas.Add(pages[i], t.position + Vector3.up * pages[i].Centre.y, 1f, t.eulerAngles.y, Color.white);
                        }
                    atlas.Flush();
                    if (f == 2) watch.Start();
                    camera.Render();
                }
                watch.Stop();
                long tris = 0, meshTris = 0;
                var renderers = 0;
                foreach (var m in spawned)
                    foreach (var r in level == 0 ? m.Renderers : level == 1 ? m.Lod1Renderers : new Renderer[0])
                    {
                        var mesh = r.GetComponent<MeshFilter>().sharedMesh;
                        renderers++;
                        for (var s = 0; s < mesh.subMeshCount; s++) meshTris += mesh.GetIndexCount(s) / 3;
                    }
                if (level == 2) meshTris = spawned.Count * 2;
                tris = triangles.Valid ? triangles.LastValue : -1;
                report.AppendLine($"level {level}: vehicles={spawned.Count} renderers={renderers} meshTriangles={meshTris} " +
                                  $"recorder: draws={(draws.Valid ? draws.LastValue : -1)} batches={(batches.Valid ? batches.LastValue : -1)} " +
                                  $"setpass={(setPass.Valid ? setPass.LastValue : -1)} tris={tris} " +
                                  $"stats: draws={UnityStats.drawCalls} setpass={UnityStats.setPassCalls} tris={UnityStats.triangles} " +
                                  $"cpu={watch.Elapsed.TotalMilliseconds / frames:0.00} ms/frame");
                RenderTexture.active = rt;
                var shot = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
                shot.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
                shot.Apply();
                RenderTexture.active = null;
                File.WriteAllBytes(Path.Combine(folder, $"crowd_lod{level}.png"), shot.EncodeToPNG());
                Object.DestroyImmediate(shot);
            }
            File.WriteAllText(Path.Combine(folder, "crowd_stats.txt"), report.ToString());
            Debug.Log("[LodShots] crowd\n" + report);
            camera.targetTexture = null;
            rt.Release();
            foreach (var m in spawned) Object.DestroyImmediate(m.Root);
        }

        private static Light Stage(Transform root)
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.transform.SetParent(root, false);
            ground.transform.localScale = new Vector3(40f, 1f, 40f);
            var sand = new Material(Shader.Find("MachineBrigade/Lit"));
            sand.SetColor("_BaseColor", new Color(0.55f, 0.5f, 0.38f));
            sand.SetFloat("_Roughness", 0.95f);
            ground.GetComponent<Renderer>().sharedMaterial = sand;

            // As SceneBuilder lights the battle scene.
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.35f;
            sun.color = new Color(1f, 0.914f, 0.792f);
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.85f;
            sun.transform.rotation = Quaternion.LookRotation(new Vector3(25f, -55f, 20f));

            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
            if (profile != null)
            {
                var volume = new GameObject("Post").AddComponent<Volume>();
                volume.transform.SetParent(root, false);
                volume.isGlobal = true;
                volume.sharedProfile = profile;
            }
            return sun;
        }

        private static Camera Camera(Transform root)
        {
            var camera = new GameObject("Shot Camera").AddComponent<Camera>();
            camera.transform.SetParent(root, false);
            camera.orthographic = true;
            camera.transform.rotation = Quaternion.Euler(52f, -45f, 0f);
            camera.nearClipPlane = 1f;
            camera.farClipPlane = 400f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Atmosphere.Haze;
            camera.allowHDR = true;
            var data = camera.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = true;
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
