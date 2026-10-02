using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using MachineBrigade.Game;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Prompt 27 Unity preview (DECISIONS "27 preview + budgets + art bible"): one contact sheet per model and tier
    /// (the normal file and its <c>_hd</c> twin where one ships), for the models named on the command line only.
    /// Rows 1-2: eight angles through the card stage (<see cref="CardRenders.Stage"/>: card lights, orthographic,
    /// pitch 26) - front, front-right, right, rear-right / rear, rear-left, left, front-left, on a neutral grey.
    /// Row 3: three gameplay views through the battle camera (<see cref="RtsCamera"/>'s orthographic pitch 52, yaw -45;
    /// LodShots' sun, ground and post-processing) at the sizes where each <see cref="VehicleLod"/> level is drawn:
    /// detail (the model as seen at the closest zoom, 9, on a 1080 px screen, kept between 144 and 300 px across),
    /// LOD1 (just under the 128 px switch) and impostor (just under the 24 px switch), each shown enlarged with
    /// whole pixels. A JSON beside each sheet gives every view's mean luma over the model's own pixels, its size,
    /// level and the zoom it equals on a 1080 px PC screen and a 720 px phone at the Low tier's 70 % render scale.
    /// No property blocks and no tints: models are drawn with their shared materials as the game draws them.
    /// Batch mode, with graphics: -executeMethod MachineBrigade.Editor.ModelPreview.RenderBatch -mbPreview "id,id"
    /// [-mbPreviewOut folder] (default Builds/preview, git-ignored).
    /// </summary>
    public static class ModelPreview
    {
        public const string DefaultOut = "Builds/preview";
        public const int Version = 1;
        private const int Cell = 512;
        private const int Columns = 4, Rows = 3;
        private const float AnglePitch = 26f;

        /// <summary>The eight angles, as card-stage camera yaws (180 looks at the model's front, +Z).</summary>
        public static readonly (string name, float yaw)[] Angles =
        {
            ("front", 180f), ("front_right", -135f), ("right", -90f), ("rear_right", -45f),
            ("rear", 0f), ("rear_left", 45f), ("left", 90f), ("front_left", 135f),
        };

        // The battle camera (RtsCamera, MatchRunner): orthographic size 9 at the closest zoom, 19 by default, 42 at the
        // widest on square maps and 50 on long ones; PC renders 1080 px high at 100 %, the Low tier at 70 %.
        private const float PcHeight = 1080f, PhoneHeight = 720f, PhoneScale = 0.7f;
        private const float ClosestZoom = 9f, WidestZoom = 50f;
        private const float CloseMax = 300f;
        private const float Heading = 20f;
        private static readonly Color Backdrop = new(0.62f, 0.64f, 0.66f, 1f);
        private static readonly Color Key = new(0f, 1f, 0f, 1f);

        [Serializable]
        public sealed class View
        {
            public string name, kind;
            public float yaw, pitch;
            public float pixels;
            public int level;
            public float zoomPc, zoomPhone;
            public bool inPlayPc, inPlayPhone;
            public float luma;
            public int cellX, cellY;
        }

        [Serializable]
        public sealed class Sheet
        {
            public int version = Version;
            public string model, tier, file, sheet, pipeline;
            public int team;
            public float length;
            public int cell = Cell;
            public string note = "luma: mean Rec. 709 luma of the stored sRGB values over the model's pixels (angles before the ground shadow; gameplay views with the battle lighting and post-processing). zoomPc / zoomPhone: the battle camera's orthographic size at which the model is this many pixels across (1080 px at 100 %; 720 px at 70 %); inPlay: within the camera's 9-50 range.";
            public List<View> views = new();
        }

        private sealed class Job
        {
            public string Id, File;
            public bool Hd;
            public int Team;
            public Color32[] Pixels;
            public Sheet Data;
            public string Name => Hd ? Id + ModelLibrary.HighDetailSuffix : Id;
        }

        /// <summary>The batch entry: -mbPreview "id,id" [-mbPreviewOut folder].</summary>
        public static void RenderBatch()
        {
            var args = Environment.GetCommandLineArgs();
            var ids = Argument(args, "-mbPreview");
            var output = Argument(args, "-mbPreviewOut") ?? DefaultOut;
            if (string.IsNullOrWhiteSpace(ids))
            {
                Debug.LogError("[ModelPreview] name the models: -mbPreview \"id,id\".");
                if (Application.isBatchMode) EditorApplication.Exit(1);
                return;
            }
            var list = ids.Split(new[] { ',', ' ', ';' }, StringSplitOptions.RemoveEmptyEntries).Distinct().ToList();
            var written = Render(list, output);
            if (written == 0 && Application.isBatchMode) EditorApplication.Exit(1);
        }

        /// <summary>Renders the sheets of <paramref name="ids"/> into <paramref name="output"/>; returns how many were written.</summary>
        public static int Render(IReadOnlyList<string> ids, string output)
        {
            if (SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            {
                Debug.LogError("[ModelPreview] needs a graphics device: run the batch without -nographics.");
                return 0;
            }
            Directory.CreateDirectory(output);
            var cards = CardRenders.Cards(GameContent.LoadCatalog());
            var jobs = new List<Job>();
            foreach (var id in ids)
            {
                if (!File.Exists(CardRenders.ModelFile(id)))
                {
                    Debug.LogWarning($"[ModelPreview] no model file for {id}; skipped");
                    continue;
                }
                // Elites and bosses only ever fight for the enemy: the enemy's colours, as on their cards.
                var drawn = cards.Where(c => c.model == id).ToList();
                var team = drawn.Count > 0 && drawn.All(c => c.kind is "elite" or "boss") ? 1 : 0;
                jobs.Add(NewJob(id, false, team));
                if (File.Exists(CardRenders.ModelFile(id + ModelLibrary.HighDetailSuffix))) jobs.Add(NewJob(id, true, team));
            }
            if (jobs.Count == 0) return 0;

            var detail = ModelLibrary.HighDetail;
            try
            {
                RenderAngles(jobs);
                RenderGameplay(jobs);
            }
            finally
            {
                ModelLibrary.HighDetail = detail;
            }

            foreach (var job in jobs)
            {
                var tex = new Texture2D(Columns * Cell, Rows * Cell, TextureFormat.RGBA32, false);
                tex.SetPixels32(job.Pixels);
                tex.Apply(false);
                File.WriteAllBytes(Path.Combine(output, job.Name + ".png"), tex.EncodeToPNG());
                Object.DestroyImmediate(tex);
                File.WriteAllText(Path.Combine(output, job.Name + ".json"), JsonUtility.ToJson(job.Data, true) + "\n");
                Debug.Log($"[ModelPreview] wrote {Path.Combine(output, job.Name)}.png/.json ({job.Data.views.Count} views)");
            }
            return jobs.Count;
        }

        private static Job NewJob(string id, bool hd, int team)
        {
            var job = new Job { Id = id, Hd = hd, Team = team, Pixels = new Color32[Columns * Cell * Rows * Cell] };
            job.File = "Models/" + job.Name + ".glb";
            job.Data = new Sheet
            {
                model = id, tier = hd ? "hd" : "normal", file = job.File, sheet = job.Name + ".png", team = team,
                pipeline = GraphicsSettings.currentRenderPipeline != null ? GraphicsSettings.currentRenderPipeline.name : "none",
            };
            Fill(job.Pixels, Backdrop);
            return job;
        }

        /// <summary>Rows 1-2: the eight angles through the card stage, over the neutral grey.</summary>
        private static void RenderAngles(List<Job> jobs)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var materials = new MaterialLibrary();
            var library = new ModelLibrary(materials);
            var stage = new CardRenders.Stage();
            var decode = new Texture2D(2, 2, TextureFormat.RGBA32, false);
            try
            {
                foreach (var job in jobs)
                {
                    ModelLibrary.HighDetail = job.Hd;
                    for (var i = 0; i < Angles.Length; i++)
                    {
                        var (name, yaw) = Angles[i];
                        var png = stage.Render(library, job.Id, job.Team, null, yaw, AnglePitch);
                        decode.LoadImage(png);
                        var cx = i % Columns;
                        var cy = i / Columns;
                        Blit(job.Pixels, decode.GetPixels32(), decode.width, cx, cy, 1, Backdrop);
                        job.Data.views.Add(new View
                        {
                            name = name, kind = "angle", yaw = yaw, pitch = AnglePitch, level = VehicleLod.Full,
                            luma = stage.LastLuma, cellX = cx, cellY = cy, pixels = CardRenders.Size,
                        });
                    }
                }
            }
            finally
            {
                Object.DestroyImmediate(decode);
                stage.Dispose();
                library.Dispose();
                materials.Dispose();
            }
        }

        /// <summary>Row 3: detail, LOD1 and impostor through the battle camera, lighting and post-processing.</summary>
        private static void RenderGameplay(List<Job> jobs)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("Preview").transform;
            var sun = LodShots.Stage(root);
            var ground = root.GetComponentsInChildren<Renderer>().FirstOrDefault();
            var atmosphere = new Atmosphere(GraphicsOptions.For(GraphicsQuality.High));
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var atlas = new ImpostorAtlas(materials);
            var camera = LodShots.Camera(root);
            var first = true;
            try
            {
                foreach (var job in jobs)
                {
                    ModelLibrary.HighDetail = job.Hd;
                    var model = models.Spawn(job.Id, job.Team, root, lod: true);
                    var t = model.Root.transform;
                    // Between two baked impostor headings, as LodShots shows them.
                    t.rotation = Quaternion.Euler(0f, Heading, 0f);
                    var lod = model.Lod;
                    var bounds = BoundsOf(model.Root);
                    var length = lod != null ? Mathf.Max(lod.Length, 0.1f) : Mathf.Max(bounds.size.x, Mathf.Max(bounds.size.y, bounds.size.z));
                    job.Data.length = length;
                    var page = lod != null ? atlas.Request(lod, job.Team) : null;
                    atlas.BakePending(camera.transform.rotation, 64);

                    var closest = length * PcHeight / (2f * ClosestZoom);
                    var views = new (string name, int level, float pixels)[]
                    {
                        ("detail", VehicleLod.Full, Mathf.Clamp(closest, VehicleLod.DetailPixels * (1f + VehicleLod.Band) + 1f, CloseMax)),
                        ("lod1", VehicleLod.Simple, VehicleLod.DetailPixels * (1f - VehicleLod.Band) * 0.95f),
                        ("impostor", VehicleLod.Impostor, VehicleLod.ImpostorPixels * (1f - VehicleLod.Band) * 0.95f),
                    };
                    for (var i = 0; i < views.Length; i++)
                    {
                        var (name, level, pixels) = views[i];
                        var view = new View
                        {
                            name = name, kind = "gameplay", yaw = RtsCamera.SquareYaw, pitch = 52f, pixels = pixels, level = level,
                            zoomPc = PcHeight * length / (2f * pixels), zoomPhone = PhoneHeight * PhoneScale * length / (2f * pixels),
                            cellX = i, cellY = 2, luma = -1f,
                        };
                        view.inPlayPc = view.zoomPc >= ClosestZoom && view.zoomPc <= WidestZoom;
                        view.inPlayPhone = view.zoomPhone >= ClosestZoom && view.zoomPhone <= WidestZoom;
                        job.Data.views.Add(view);
                        var hasLevel = level == VehicleLod.Full || (level == VehicleLod.Simple && model.Lod1Renderers.Length > 0)
                            || (level == VehicleLod.Impostor && page != null);
                        if (!hasLevel) continue;

                        var size = Mathf.CeilToInt(pixels * 1.6f / 8f) * 8;
                        var rt = new RenderTexture(size, size, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
                        camera.targetTexture = rt;
                        camera.orthographicSize = size / (2f * pixels / length);
                        camera.transform.position = bounds.center - camera.transform.forward * Mathf.Max(80f, length * 2.5f);
                        atmosphere.FitShadows(camera);
                        foreach (var r in model.Renderers) r.enabled = level == VehicleLod.Full;
                        foreach (var r in model.Lod1Renderers) r.gameObject.SetActive(level == VehicleLod.Simple);

                        // Impostors are queued instanced draws: a fresh camera of their own, warmed up (LodShots).
                        Camera shot = camera;
                        if (level == VehicleLod.Impostor)
                        {
                            shot = LodShots.Twin(camera, root);
                            for (var w = 0; w < 3; w++) shot.Render();
                        }
                        if (first)
                        {
                            shot.Render(); // the first render compiles shaders
                            first = false;
                        }
                        var lit = Shoot(shot, rt, level, atlas, page, t, false, ground);
                        var mask = Shoot(shot, rt, level, atlas, page, t, true, ground);
                        if (shot != camera) Object.DestroyImmediate(shot.gameObject);
                        camera.targetTexture = null;
                        rt.Release();
                        Object.DestroyImmediate(rt);

                        double sum = 0;
                        var count = 0;
                        for (var p = 0; p < lit.Length; p++)
                        {
                            var m = mask[p];
                            if (m.r < 8 && m.g > 247 && m.b < 8) continue; // the key colour: not the model
                            var c = lit[p];
                            sum += (0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b) / 255.0;
                            count++;
                        }
                        view.luma = count > 0 ? (float)(sum / count) : -1f;
                        var zoom = Mathf.Max(1, Cell / size);
                        Blit(job.Pixels, lit, size, i, 2, zoom, Atmosphere.Haze);
                    }
                    Object.DestroyImmediate(model.Root);
                }
            }
            finally
            {
                camera.targetTexture = null;
                atlas.Dispose();
                models.Dispose();
                materials.Dispose();
                atmosphere.Dispose();
                Object.DestroyImmediate(sun.gameObject);
                Object.DestroyImmediate(root.gameObject);
            }
        }

        /// <summary>
        /// One render of the current level: lit (the battle look) or as a mask (ground hidden, no post-processing,
        /// cleared to the key colour), read back as pixels.
        /// </summary>
        private static Color32[] Shoot(Camera camera, RenderTexture rt, int level, ImpostorAtlas atlas, ImpostorPage page, Transform t,
            bool mask, Renderer ground)
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
            if (level == VehicleLod.Impostor && page != null)
            {
                atlas.Begin();
                atlas.Add(page, t.position + Vector3.up * page.Centre.y, 1f, t.eulerAngles.y, Color.white);
                atlas.Flush(camera);
            }
            camera.Render();
            var was = RenderTexture.active;
            RenderTexture.active = rt;
            var read = new Texture2D(rt.width, rt.height, TextureFormat.RGBA32, false);
            read.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
            read.Apply(false);
            RenderTexture.active = was;
            var pixels = read.GetPixels32();
            Object.DestroyImmediate(read);
            if (mask)
            {
                data.renderPostProcessing = post;
                camera.backgroundColor = background;
                if (ground != null) ground.enabled = true;
            }
            return pixels;
        }

        /// <summary>Copies a square image into cell (cx, cy) (row 0 at the top), enlarged <paramref name="zoom"/> times, centred, over <paramref name="under"/>.</summary>
        private static void Blit(Color32[] sheet, Color32[] image, int size, int cx, int cy, int zoom, Color under)
        {
            var width = Columns * Cell;
            var shown = size * zoom;
            var offset = (Cell - shown) / 2;
            Color32 bg = under;
            for (var y = 0; y < Cell; y++)
            for (var x = 0; x < Cell; x++)
            {
                var sx = x - offset;
                var sy = y - offset;
                var c = bg;
                if (sx >= 0 && sy >= 0 && sx < shown && sy < shown)
                {
                    var p = image[(sy / zoom) * size + sx / zoom];
                    // Alpha over the backdrop (the angle renders are transparent; the gameplay views opaque).
                    var a = p.a / 255f;
                    c = new Color32((byte)(p.r * a + bg.r * (1f - a)), (byte)(p.g * a + bg.g * (1f - a)), (byte)(p.b * a + bg.b * (1f - a)), 255);
                }
                var row = (Rows - 1 - cy) * Cell + y;
                sheet[row * width + cx * Cell + x] = c;
            }
        }

        private static void Fill(Color32[] pixels, Color colour)
        {
            Color32 c = colour;
            for (var i = 0; i < pixels.Length; i++) pixels[i] = c;
        }

        private static Bounds BoundsOf(GameObject model)
        {
            var renderers = model.GetComponentsInChildren<Renderer>();
            var b = renderers.Length > 0 ? renderers[0].bounds : new Bounds(Vector3.zero, Vector3.one);
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
