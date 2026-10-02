using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using MachineBrigade.Game;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Fix pass 8 (Docs/prompts/fix_full_vi.txt "Lượt 8"; DECISIONS "Sửa lỗi tổng hợp L8 prep"): the model scan.
    /// For every model a vehicle def draws (vehicles, aircraft, ships, bosses, towers and their branch models,
    /// structures) and the two HQs - or the models named with -mbScan - one 3-up sheet (3 x 512 px cells) at the normal
    /// gameplay camera distance: the battle camera's default zoom (orthographic size 19 on a 1080 px screen, 28.4 px per
    /// metre; a model bigger than a cell is fitted and its JSON says so), LodShots' battle sun, ground and
    /// post-processing, the model drawn at its in-game size (<see cref="VehicleView.DrawScaleOf(VehicleDef, GameObject)"/>)
    /// and in its side's colours (elites and bosses the enemy's). Cells, all with the battle camera's yaw and the sun
    /// fixed, the model turned instead (as units turn in battle):
    ///   1 "play": pitch 52 (the battle camera), the model's front-left three-quarter;
    ///   2 "side": pitch 10, the left profile (proportions);
    ///   3 "rear": pitch 30, the rear-right three-quarter.
    /// The same for the old model when Builds/scan_old_models/&lt;id&gt;.glb exists (scan_prep.py --old): it is copied
    /// with the current model's import settings (its .meta, a fresh guid) into a temporary Resources folder
    /// (Assets/ScanOld, deleted afterwards and on the next run), loaded through the same ModelLibrary, drawn at the same
    /// def size, and written as &lt;id&gt;_old.png. Beside each sheet a JSON: per view the pixels per metre, whether it
    /// was fitted, the model's coverage, width and height in pixels and its mean luma; per model the LOD0 / LOD1
    /// triangles (the run-time LOD1, <see cref="ModelLod"/>) for the LOD ~50 % rule. index.json lists every sheet.
    /// No property blocks, no tints: shared materials as the game draws them.
    ///
    /// Batch mode, with graphics (no -nographics), in the runner tree:
    ///   Unity.exe -batchmode -force-d3d11 -quit -projectPath . -executeMethod MachineBrigade.Editor.ModelScan.RenderBatch
    ///     [-mbScan "id,id"]              only these models (default: all, see above)
    ///     [-mbScanOut Builds/scan]       output folder (git-ignored)
    ///     [-mbScanOld Builds/scan_old_models]  where the old GLBs are
    ///     [-mbScanNoOld]                 skip the old models
    ///     [-mbScanZoom 19]               the battle camera's orthographic size the scale is taken from (9 = closest)
    ///     -logFile scan.log
    /// Expected run time: about 1 s per sheet after a 1-2 min start (import of the old GLBs included): roughly
    /// 8-15 min for the ~230 current models and ~150 old ones; 1 min for a handful named with -mbScan.
    /// </summary>
    public static class ModelScan
    {
        public const string DefaultOut = "Builds/scan";
        public const string DefaultOld = "Builds/scan_old_models";
        public const int Version = 1;
        /// <summary>Resource suffix of a staged old model (Resources/Models/&lt;id&gt;__scanold).</summary>
        public const string OldSuffix = "__scanold";
        private const string StagingRoot = "Assets/ScanOld";
        private const string StagingFolder = StagingRoot + "/Resources/Models";
        private const int Cell = 512;
        private const int Cells = 3;
        private const float PcHeight = 1080f;
        private const float DefaultZoom = 19f;
        private const float FitMargin = 0.92f;
        private static readonly string[] Hqs = { "headquarters", "command_hq" };
        private static readonly Color Key = new(0f, 1f, 0f, 1f);

        /// <summary>The three cells: name, camera pitch, the camera's yaw seen from the model (180 = from the front).</summary>
        public static readonly (string name, float pitch, float relativeYaw)[] Shots =
        {
            ("play", 52f, 145f), ("side", 10f, 90f), ("rear", 30f, -45f),
        };

        [Serializable]
        public sealed class View
        {
            public string name;
            public float pitch, relativeYaw, heading;
            public float orthographicSize, pixelsPerMetre;
            public bool fitted;
            public int coveragePx, widthPx, heightPx;
            public float luma;
            public int cell;
        }

        [Serializable]
        public sealed class Sheet
        {
            public int version = Version;
            public string model, variant, resource, sheet, def;
            public int team;
            public float drawScale;
            public float zoom;
            public float gameplayPixelsPerMetre;
            public int triangles0, triangles1, draws0, draws1;
            public float lod1Share;
            public float[] size;
            public string note = "Cells: play (pitch 52, front-left 3/4), side (pitch 10, left profile), rear (pitch 30, rear-right 3/4); the battle camera's yaw and sun, the model turned. pixelsPerMetre: the battle camera's at the zoom (1080 px screen) unless fitted. triangles0/1: LOD0 and the run-time LOD1 (ModelLibrary.Lod). luma: mean Rec. 709 luma of the lit pixels over the model's mask.";
            public List<View> views = new();
        }

        [Serializable]
        private sealed class ScanIndex
        {
            public int version = Version;
            public string pipeline;
            public float zoom;
            public List<string> sheets = new();
            public List<string> missing = new();
        }

        private sealed class Job
        {
            public string Id, Resource, Variant;
            public VehicleDef Def;
            public int Team;
        }

        /// <summary>The batch entry (flags in the class summary).</summary>
        public static void RenderBatch()
        {
            var args = Environment.GetCommandLineArgs();
            var list = Argument(args, "-mbScan");
            var output = Argument(args, "-mbScanOut") ?? DefaultOut;
            var old = Argument(args, "-mbScanOld") ?? DefaultOld;
            var withOld = !args.Contains("-mbScanNoOld");
            var zoom = DefaultZoom;
            var zoomText = Argument(args, "-mbScanZoom");
            if (zoomText != null && float.TryParse(zoomText, System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out var parsed) && parsed > 1f)
                zoom = parsed;
            List<string> ids = null;
            if (!string.IsNullOrWhiteSpace(list))
                ids = list.Split(new[] { ',', ' ', ';' }, StringSplitOptions.RemoveEmptyEntries).Distinct().ToList();
            var written = Render(ids, output, withOld ? old : null, zoom);
            if (written == 0 && Application.isBatchMode) EditorApplication.Exit(1);
        }

        /// <summary>Renders the sheets; <paramref name="ids"/> null = every scanned model. Returns how many were written.</summary>
        public static int Render(IReadOnlyList<string> ids, string output, string oldFolder, float zoom)
        {
            if (SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            {
                Debug.LogError("[ModelScan] needs a graphics device: run the batch without -nographics.");
                return 0;
            }
            Directory.CreateDirectory(output);
            var catalog = GameContent.LoadCatalog();
            var owners = Owners(catalog);
            var wanted = ids ?? owners.Keys.ToList();
            var index = new ScanIndex
            {
                zoom = zoom,
                pipeline = GraphicsSettings.currentRenderPipeline != null ? GraphicsSettings.currentRenderPipeline.name : "none",
            };
            var jobs = new List<Job>();
            foreach (var id in wanted)
            {
                if (!File.Exists(CardRenders.ModelFile(id)))
                {
                    Debug.LogWarning($"[ModelScan] no model file for {id}; skipped");
                    index.missing.Add(id);
                    continue;
                }
                owners.TryGetValue(id, out var owner);
                var team = owner != null && (owner.Elite || owner.Boss) ? 1 : 0;
                jobs.Add(new Job { Id = id, Resource = id, Variant = "new", Def = owner, Team = team });
            }

            var staged = 0;
            try
            {
                if (oldFolder != null && Directory.Exists(oldFolder))
                {
                    var oldIds = jobs.Select(j => j.Id).Where(j => File.Exists(Path.Combine(oldFolder, j + ".glb"))).ToList();
                    staged = StageOld(oldIds, oldFolder);
                    foreach (var id in oldIds)
                    {
                        if (Resources.Load<GameObject>("Models/" + id + OldSuffix) == null)
                        {
                            Debug.LogWarning($"[ModelScan] the old {id} did not import; skipped");
                            continue;
                        }
                        var current = jobs.First(j => j.Id == id && j.Variant == "new");
                        jobs.Add(new Job { Id = id, Resource = id + OldSuffix, Variant = "old", Def = current.Def, Team = current.Team });
                    }
                }
                Debug.Log($"[ModelScan] {jobs.Count} sheets ({staged} old models staged), zoom {zoom}");
                var written = Shoot(jobs, output, zoom, index);
                File.WriteAllText(Path.Combine(output, "index.json"), JsonUtility.ToJson(index, true) + "\n");
                return written;
            }
            finally
            {
                if (staged > 0 || AssetDatabase.IsValidFolder(StagingRoot)) CleanStaging();
            }
        }

        /// <summary>{model: the def that draws it (its own def first)} for every shipped model a def draws, plus the HQs.</summary>
        private static Dictionary<string, VehicleDef> Owners(Catalog catalog)
        {
            bool Ships(string id) => File.Exists(CardRenders.ModelFile(id));
            var owners = new Dictionary<string, VehicleDef>();
            foreach (var def in catalog.Vehicles.Values.OrderBy(d => d.Id, StringComparer.Ordinal))
            {
                var model = TowerArt.ModelFor(def, Ships);
                if (string.IsNullOrEmpty(model) || !Ships(model)) continue;
                if (!owners.TryGetValue(model, out var had) || (had != null && had.Id != model && def.Id == model))
                    owners[model] = def;
            }
            foreach (var hq in Hqs)
                if (Ships(hq) && !owners.ContainsKey(hq)) owners[hq] = null;
            return owners.OrderBy(p => p.Key, StringComparer.Ordinal).ToDictionary(p => p.Key, p => p.Value);
        }

        /// <summary>Copies the old GLBs with the current model's .meta (fresh guid) into Assets/ScanOld and imports them.</summary>
        private static int StageOld(List<string> ids, string oldFolder)
        {
            CleanStaging();
            if (ids.Count == 0) return 0;
            Directory.CreateDirectory(StagingFolder);
            var guidLine = new Regex(@"(?m)^guid: [0-9a-f]{32}");
            foreach (var id in ids)
            {
                var target = StagingFolder + "/" + id + OldSuffix + ".glb";
                File.Copy(Path.Combine(oldFolder, id + ".glb"), target, true);
                var meta = CardRenders.ModelFile(id) + ".meta";
                if (File.Exists(meta))
                    File.WriteAllText(target + ".meta", guidLine.Replace(File.ReadAllText(meta), "guid: " + GUID.Generate(), 1));
            }
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            return ids.Count;
        }

        private static void CleanStaging()
        {
            if (AssetDatabase.IsValidFolder(StagingRoot)) AssetDatabase.DeleteAsset(StagingRoot);
            if (Directory.Exists(StagingRoot)) Directory.Delete(StagingRoot, true);
            if (File.Exists(StagingRoot + ".meta")) File.Delete(StagingRoot + ".meta");
            AssetDatabase.Refresh();
        }

        private static int Shoot(List<Job> jobs, string output, float zoom, ScanIndex index)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("Scan").transform;
            var sun = LodShots.Stage(root);
            var ground = root.GetComponentsInChildren<Renderer>().FirstOrDefault();
            var atmosphere = new Atmosphere(GraphicsOptions.For(GraphicsQuality.High));
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var camera = LodShots.Camera(root);
            var rt = new RenderTexture(Cell, Cell, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            var read = new Texture2D(Cell, Cell, TextureFormat.RGBA32, false);
            var detail = ModelLibrary.HighDetail;
            ModelLibrary.HighDetail = false;
            var ppm = PcHeight / (2f * zoom);
            var written = 0;
            var warm = true;
            try
            {
                foreach (var job in jobs)
                {
                    var name = job.Variant == "old" ? job.Id + "_old" : job.Id;
                    var data = new Sheet
                    {
                        model = job.Id, variant = job.Variant, resource = "Models/" + job.Resource, sheet = name + ".png",
                        def = job.Def != null ? job.Def.Id : "", team = job.Team, zoom = zoom, gameplayPixelsPerMetre = ppm,
                    };
                    var pixels = new Color32[Cells * Cell * Cell];
                    ModelInstance model;
                    try
                    {
                        model = models.Spawn(job.Resource, job.Team, root, lod: true);
                    }
                    catch (Exception e)
                    {
                        Debug.LogWarning($"[ModelScan] {name}: {e.Message}");
                        index.missing.Add(name);
                        continue;
                    }
                    var t = model.Root.transform;
                    t.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
                    var scale = job.Def != null ? VehicleView.DrawScaleOf(job.Def, model.Root) : 1f;
                    t.localScale = Vector3.one * scale;
                    data.drawScale = scale;
                    foreach (var r in model.Renderers) r.enabled = true;
                    foreach (var r in model.Lod1Renderers) r.gameObject.SetActive(false);
                    if (model.Lod != null)
                    {
                        data.triangles0 = model.Lod.Triangles0;
                        data.triangles1 = model.Lod.Triangles1;
                        data.draws0 = model.Lod.Draws0;
                        data.draws1 = model.Lod.Draws1;
                        data.lod1Share = model.Lod.Triangles0 > 0 ? (float)model.Lod.Triangles1 / model.Lod.Triangles0 : 0f;
                    }
                    var rest = BoundsOf(model.Root);
                    data.size = new[] { rest.size.z, rest.size.x, rest.size.y };
                    // Aircraft lifted clear of the ground; ships stay at the waterline; anything else stands on y = 0.
                    var flying = job.Def != null && job.Def.Flying;
                    var naval = job.Def != null && Naval(job.Def);
                    var lift = flying ? 1.5f - rest.min.y : naval ? 0f : rest.min.y < -0.25f * rest.size.y ? -rest.min.y : 0f;
                    t.position = new Vector3(0f, lift, 0f);

                    for (var i = 0; i < Shots.Length; i++)
                    {
                        var (shotName, pitch, relativeYaw) = Shots[i];
                        // Camera yaw fixed (the battle's); the model turned so the camera sees it from relativeYaw.
                        var heading = RtsCamera.SquareYaw - relativeYaw;
                        t.rotation = Quaternion.Euler(0f, heading, 0f);
                        camera.transform.rotation = Quaternion.Euler(pitch, RtsCamera.SquareYaw, 0f);
                        var bounds = BoundsOf(model.Root);
                        var radius = Mathf.Max(bounds.extents.magnitude, 0.5f);
                        var size = Cell / (2f * ppm);
                        var fitted = false;
                        if (radius > size * FitMargin)
                        {
                            size = radius / FitMargin;
                            fitted = true;
                        }
                        camera.orthographicSize = size;
                        var distance = Mathf.Max(80f, radius * 3f);
                        camera.transform.position = bounds.center - camera.transform.forward * distance;
                        camera.farClipPlane = distance + radius * 2f + 50f;
                        camera.targetTexture = rt;
                        atmosphere.FitShadows(camera);
                        if (warm)
                        {
                            camera.Render(); // the first render compiles shaders
                            warm = false;
                        }
                        var lit = Capture(camera, rt, read, false, ground);
                        var mask = Capture(camera, rt, read, true, ground);
                        var view = new View
                        {
                            name = shotName, pitch = pitch, relativeYaw = relativeYaw, heading = heading,
                            orthographicSize = size, pixelsPerMetre = Cell / (2f * size), fitted = fitted, cell = i,
                        };
                        Measure(lit, mask, view);
                        data.views.Add(view);
                        Blit(pixels, lit, i);
                    }
                    camera.targetTexture = null;
                    Object.DestroyImmediate(model.Root);

                    var tex = new Texture2D(Cells * Cell, Cell, TextureFormat.RGBA32, false);
                    tex.SetPixels32(pixels);
                    tex.Apply(false);
                    File.WriteAllBytes(Path.Combine(output, name + ".png"), tex.EncodeToPNG());
                    Object.DestroyImmediate(tex);
                    File.WriteAllText(Path.Combine(output, name + ".json"), JsonUtility.ToJson(data, true) + "\n");
                    index.sheets.Add(name);
                    written++;
                    if (written % 25 == 0) Debug.Log($"[ModelScan] {written} / {jobs.Count} sheets");
                }
            }
            finally
            {
                ModelLibrary.HighDetail = detail;
                camera.targetTexture = null;
                rt.Release();
                Object.DestroyImmediate(rt);
                Object.DestroyImmediate(read);
                models.Dispose();
                materials.Dispose();
                atmosphere.Dispose();
                Object.DestroyImmediate(sun.gameObject);
                Object.DestroyImmediate(root.gameObject);
            }
            Debug.Log($"[ModelScan] wrote {written} sheets to {output}");
            return written;
        }

        /// <summary>Ships: a naval def (the "naval" flag) - read by name so this tool does not depend on the property's spelling.</summary>
        private static bool Naval(VehicleDef def)
        {
            var property = typeof(VehicleDef).GetProperty("Naval");
            return property != null && property.PropertyType == typeof(bool) && (bool)property.GetValue(def);
        }

        /// <summary>One render: lit (the battle look) or as a mask (ground hidden, no post-processing, the key colour).</summary>
        private static Color32[] Capture(Camera camera, RenderTexture rt, Texture2D read, bool mask, Renderer ground)
        {
            var data = camera.GetUniversalAdditionalCameraData();
            var post = data.renderPostProcessing;
            var background = camera.backgroundColor;
            if (mask)
            {
                data.renderPostProcessing = false;
                camera.backgroundColor = Key;
                if (ground != null) ground.enabled = false;
            }
            camera.targetTexture = rt;
            camera.Render();
            var was = RenderTexture.active;
            RenderTexture.active = rt;
            read.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
            read.Apply(false);
            RenderTexture.active = was;
            var result = read.GetPixels32();
            if (mask)
            {
                data.renderPostProcessing = post;
                camera.backgroundColor = background;
                if (ground != null) ground.enabled = true;
            }
            return result;
        }

        /// <summary>Coverage, extent and mean luma of the model's pixels (the mask's non-key pixels).</summary>
        private static void Measure(Color32[] lit, Color32[] mask, View view)
        {
            int minX = Cell, minY = Cell, maxX = -1, maxY = -1, covered = 0;
            double sum = 0;
            for (var p = 0; p < mask.Length; p++)
            {
                var m = mask[p];
                if (m.r < 8 && m.g > 247 && m.b < 8) continue;
                var x = p % Cell;
                var y = p / Cell;
                if (x < minX) minX = x;
                if (x > maxX) maxX = x;
                if (y < minY) minY = y;
                if (y > maxY) maxY = y;
                var c = lit[p];
                sum += (0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b) / 255.0;
                covered++;
            }
            view.coveragePx = covered;
            view.widthPx = maxX >= minX ? maxX - minX + 1 : 0;
            view.heightPx = maxY >= minY ? maxY - minY + 1 : 0;
            view.luma = covered > 0 ? (float)(sum / covered) : -1f;
        }

        /// <summary>Copies a cell-sized image into cell <paramref name="cell"/> of the one-row sheet (opaque renders).</summary>
        private static void Blit(Color32[] sheet, Color32[] image, int cell)
        {
            var width = Cells * Cell;
            for (var y = 0; y < Cell; y++)
            for (var x = 0; x < Cell; x++)
            {
                var c = image[y * Cell + x];
                c.a = 255;
                sheet[y * width + cell * Cell + x] = c;
            }
        }

        private static Bounds BoundsOf(GameObject model)
        {
            var renderers = model.GetComponentsInChildren<Renderer>().Where(r => r.enabled).ToArray();
            var b = renderers.Length > 0 ? renderers[0].bounds : new Bounds(model.transform.position, Vector3.one);
            foreach (var r in renderers) b.Encapsulate(r.bounds);
            return b;
        }

        private static string Argument(string[] args, string name)
        {
            for (var i = 0; i < args.Length - 1; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }
    }
}
