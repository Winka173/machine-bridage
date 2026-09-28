using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using MachineBrigade.Game;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
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
    /// Renders the card pictures (Field Command 2.0, section F): every fieldable vehicle, elite,
    /// tower and boss, from its high-detail model where one ships, through one 3/4 orthographic
    /// camera and one set of lights, on a transparent background with a soft shadow under it,
    /// 512 px square, into Resources/UI/Cards/&lt;model&gt;.png with a manifest (card id, model, source,
    /// the source file's SHA-1). A model whose file changed is rendered again on import (in an
    /// editor with graphics) or by the batch run; CardRenderTests fail while a picture is stale.
    /// Batch mode, with graphics: -executeMethod MachineBrigade.Editor.CardRenders.RenderBatch
    /// [-mbCardsForce] [-mbCardsOnly id,id].
    /// </summary>
    public static class CardRenders
    {
        public const string OutFolder = "Assets/MachineBrigade/Resources/UI/Cards";
        public const string ModelsFolder = "Assets/MachineBrigade/Resources/Models";
        public const int Size = 512;

        /// <summary>Bumped when the camera, lights or compositing change, so every picture is rendered again.</summary>
        public const int Version = 2;

        private const int Super = 2;
        private const float Pitch = 26f;
        private const float Yaw = -142f;
        private const string CameraNote = "orthographic 3/4, pitch 26, yaw -142 (the front to the right), framed on the silhouette; key light 44/-105, fill 18/60, rim 12/150, flat ambient; contact shadow from above, blurred; elites and bosses in the enemy colours";

        public static readonly (string kind, Func<VehicleDef, bool> test)[] Kinds =
        {
            ("elite", d => d.Elite),
            ("boss", d => d.Boss),
            ("tower", d => d.Static && d.Fort != null),
        };

        /// <summary>Every card that needs a picture: (card id, kind, model id).</summary>
        public static List<(string id, string kind, string model)> Cards(Catalog catalog)
        {
            var cards = new List<(string id, string kind, string model)>();
            var seen = new HashSet<string>();
            foreach (var id in MatchSettings.AllVehicles)
                if (catalog.Vehicles.TryGetValue(id, out var def) && seen.Add(id))
                    cards.Add((id, "vehicle", def.Model));
            foreach (var def in catalog.Vehicles.Values.OrderBy(d => d.Id, StringComparer.Ordinal))
                foreach (var (kind, test) in Kinds)
                    if (test(def) && seen.Add(def.Id))
                        cards.Add((def.Id, kind, def.Model));
            return cards;
        }

        /// <summary>The model resource a picture is rendered from: the high-detail variant where one ships.</summary>
        public static string SourceOf(string modelId)
        {
            var hd = modelId + ModelLibrary.HighDetailSuffix;
            return File.Exists(ModelFile(hd)) ? hd : modelId;
        }

        public static string ModelFile(string resource) => Path.Combine(ModelsFolder, resource + ".glb").Replace('\\', '/');

        /// <summary>SHA-1 of the model file and the render version: a new model or a new camera both make it stale.</summary>
        public static string Hash(string source)
        {
            var path = ModelFile(source);
            if (!File.Exists(path)) return "";
            using var sha = SHA1.Create();
            var bytes = File.ReadAllBytes(path);
            var hash = sha.ComputeHash(bytes);
            return "v" + Version + ":" + BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
        }

        [MenuItem("Machine Brigade/Render Card Images (stale)")]
        public static void RenderStaleMenu() => Render(false, null);

        [MenuItem("Machine Brigade/Render Card Images (all)")]
        public static void RenderAllMenu() => Render(true, null);

        /// <summary>Batch entry point (with graphics).</summary>
        public static void RenderBatch()
        {
            var args = Environment.GetCommandLineArgs();
            var force = args.Contains("-mbCardsForce");
            var only = Argument(args, "-mbCardsOnly");
            Render(force, only?.Split(',').Select(s => s.Trim()).Where(s => s.Length > 0).ToHashSet());
        }

        /// <summary>Renders the pictures that are missing or stale (all with <paramref name="force"/>), then rewrites the manifest.</summary>
        public static int Render(bool force, HashSet<string> only)
        {
            if (SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            {
                Debug.LogError("[CardRenders] needs a graphics device: run the batch without -nographics.");
                return 0;
            }
            var catalog = GameContent.LoadCatalog();
            var cards = Cards(catalog);
            var old = ReadManifest();
            Directory.CreateDirectory(OutFolder);

            // Which models need a picture: missing, stale (hash), forced or asked for.
            var models = new Dictionary<string, (string source, string hash)>();
            foreach (var (_, _, model) in cards)
            {
                if (models.ContainsKey(model)) continue;
                var source = SourceOf(model);
                models[model] = (source, Hash(source));
            }
            var todo = models.Where(m =>
            {
                if (only != null) return only.Contains(m.Key) || cards.Any(c => c.model == m.Key && only.Contains(c.id));
                var png = Path.Combine(OutFolder, m.Key + ".png");
                var had = old.entries.FirstOrDefault(e => e.model == m.Key);
                return force || !File.Exists(png) || had == null || had.hash != m.Value.hash;
            }).Select(m => m.Key).ToList();

            var done = new List<string>();
            if (todo.Count > 0)
            {
                var previousScene = EditorSceneManager.GetActiveScene().path;
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var detail = ModelLibrary.HighDetail;
                ModelLibrary.HighDetail = true;
                var materials = new MaterialLibrary();
                var library = new ModelLibrary(materials);
                var stage = new Stage();
                try
                {
                    foreach (var model in todo)
                    {
                        if (!File.Exists(ModelFile(models[model].source)))
                        {
                            Debug.LogWarning($"[CardRenders] no model file for {model}; skipped");
                            continue;
                        }
                        // Elites and bosses only ever fight for the enemy: they wear the enemy's colours.
                        var enemy = cards.Where(c => c.model == model).All(c => c.kind is "elite" or "boss");
                        var png = stage.Render(library, model, enemy ? 1 : 0);
                        File.WriteAllBytes(Path.Combine(OutFolder, model + ".png"), png);
                        done.Add(model);
                    }
                }
                finally
                {
                    stage.Dispose();
                    library.Dispose();
                    materials.Dispose();
                    ModelLibrary.HighDetail = detail;
                }
                if (!string.IsNullOrEmpty(previousScene) && !Application.isBatchMode) EditorSceneManager.OpenScene(previousScene);
            }

            // Each picture keeps the hash of the model file it was rendered from, so one kept from an
            // older model still reads as stale to the test.
            var renderedFrom = new Dictionary<string, string>();
            foreach (var e in old.entries)
                if (!string.IsNullOrEmpty(e.model) && !renderedFrom.ContainsKey(e.model)) renderedFrom[e.model] = e.hash;
            foreach (var model in done) renderedFrom[model] = models[model].hash;
            var manifest = new CardArt.Manifest { version = Version, size = Size, camera = CameraNote };
            foreach (var (id, kind, model) in cards)
            {
                if (!File.Exists(Path.Combine(OutFolder, model + ".png"))) continue;
                manifest.entries.Add(new CardArt.Entry
                {
                    id = id, kind = kind, model = model, source = "Models/" + models[model].source,
                    hash = renderedFrom.TryGetValue(model, out var hash) ? hash : "",
                });
            }
            File.WriteAllText(Path.Combine(OutFolder, "manifest.json"), JsonUtility.ToJson(manifest, true) + "\n");
            AssetDatabase.Refresh();
            CardArt.Reload();
            Debug.Log($"[CardRenders] rendered {done.Count} of {models.Count} models for {manifest.entries.Count} cards into {OutFolder}");
            return done.Count;
        }

        public static CardArt.Manifest ReadManifest()
        {
            var path = Path.Combine(OutFolder, "manifest.json");
            if (!File.Exists(path)) return new CardArt.Manifest();
            return JsonUtility.FromJson<CardArt.Manifest>(File.ReadAllText(path)) ?? new CardArt.Manifest();
        }

        private static string Argument(string[] args, string name)
        {
            for (var i = 0; i < args.Length - 1; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }

        /// <summary>The render set: lights, the card camera, the shadow camera and their targets.</summary>
        private sealed class Stage : IDisposable
        {
            private const int Layer = 30;
            private readonly Transform _root;
            private readonly Camera _camera, _top;
            private readonly RenderTexture _rt, _topRt;
            private readonly Texture2D _read, _topRead;
            private readonly int _big = Size * Super;
            private const int TopSize = 256;

            public Stage()
            {
                _root = new GameObject("Card Stage").transform;
                AddLight("Key", new Vector3(44f, -105f, 0f), 1.45f, new Color(1f, 0.96f, 0.9f));
                AddLight("Fill", new Vector3(18f, 60f, 0f), 0.45f, new Color(0.78f, 0.86f, 1f));
                AddLight("Rim", new Vector3(12f, 150f, 0f), 0.55f, new Color(0.95f, 0.95f, 1f));
                RenderSettings.ambientMode = AmbientMode.Flat;
                RenderSettings.ambientLight = new Color(0.46f, 0.49f, 0.54f);
                RenderSettings.fog = false;
                DynamicGI.UpdateEnvironment();

                _rt = new RenderTexture(_big, _big, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4, name = "Card" };
                _camera = MakeCamera("Card Camera", _rt);
                _topRt = new RenderTexture(TopSize, TopSize, 24, RenderTextureFormat.ARGB32) { antiAliasing = 1, name = "Card Shadow" };
                _top = MakeCamera("Shadow Camera", _topRt);
                _read = new Texture2D(_big, _big, TextureFormat.RGBA32, false);
                _topRead = new Texture2D(TopSize, TopSize, TextureFormat.RGBA32, false);
            }

            private void AddLight(string name, Vector3 euler, float intensity, Color colour)
            {
                var light = new GameObject(name).AddComponent<Light>();
                light.transform.SetParent(_root, false);
                light.type = LightType.Directional;
                light.intensity = intensity;
                light.color = colour;
                light.shadows = LightShadows.None;
                light.transform.rotation = Quaternion.Euler(euler);
            }

            private Camera MakeCamera(string name, RenderTexture target)
            {
                var camera = new GameObject(name).AddComponent<Camera>();
                camera.transform.SetParent(_root, false);
                camera.orthographic = true;
                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = new Color(0f, 0f, 0f, 0f);
                camera.allowHDR = false;
                camera.allowMSAA = true;
                camera.cullingMask = 1 << Layer;
                camera.nearClipPlane = 0.1f;
                camera.farClipPlane = 400f;
                camera.targetTexture = target;
                camera.enabled = false;
                var data = camera.GetUniversalAdditionalCameraData();
                data.renderPostProcessing = false;
                data.renderShadows = false;
                data.antialiasing = AntialiasingMode.None;
                return camera;
            }

            public byte[] Render(ModelLibrary library, string modelId, int team)
            {
                var instance = library.Spawn(modelId, team, _root, castShadows: false);
                var model = instance.Root;
                SetLayer(model.transform);
                model.transform.position = Vector3.zero;
                model.transform.rotation = Quaternion.identity;
                // Rotors and radars at rest; the model's own pose otherwise.
                var bounds = Bounds(model);
                model.transform.position -= new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
                bounds = Bounds(model);

                // The model from the 3/4 camera.
                FitCamera(bounds);
                Capture(_camera, _rt, _read);
                // Renderer bounds can be loose (thin masts, empties with meshes): frame the silhouette
                // as drawn, then render again.
                if (Refit(_read.GetPixels32())) Capture(_camera, _rt, _read);
                var colour = _read.GetPixels32();

                // Its footprint from straight above, for the shadow.
                var reach = Mathf.Max(bounds.extents.x, bounds.extents.z) * 1.6f + 1f;
                _top.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
                _top.transform.position = new Vector3(0f, bounds.max.y + 20f, 0f);
                _top.orthographicSize = reach;
                Capture(_top, _topRt, _topRead);
                var mask = Blur(_topRead.GetPixels32().Select(p => p.a / 255f).ToArray(), TopSize, Mathf.Max(2, TopSize / 40));

                Object.DestroyImmediate(model);
                return Composite(colour, mask, reach, bounds);
            }

            private static Bounds Bounds(GameObject model)
            {
                var renderers = model.GetComponentsInChildren<Renderer>();
                var b = renderers.Length > 0 ? renderers[0].bounds : new Bounds(Vector3.zero, Vector3.one);
                foreach (var r in renderers) b.Encapsulate(r.bounds);
                return b;
            }

            /// <summary>Points the card camera from the 3/4 angle and fits the model and its ground shadow into the square with a margin.</summary>
            private void FitCamera(Bounds b)
            {
                var rotation = Quaternion.Euler(Pitch, Yaw, 0f);
                var right = rotation * Vector3.right;
                var up = rotation * Vector3.up;
                var points = new List<Vector3>();
                for (var i = 0; i < 8; i++)
                    points.Add(new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y, (i & 4) == 0 ? b.min.z : b.max.z));
                // The shadow's spread on the ground.
                var ground = new Vector2(b.extents.x, b.extents.z) * 1.12f;
                foreach (var sx in new[] { -1f, 1f })
                    foreach (var sz in new[] { -1f, 1f })
                        points.Add(new Vector3(b.center.x + sx * ground.x, 0f, b.center.z + sz * ground.y));
                float minX = float.MaxValue, maxX = float.MinValue, minY = float.MaxValue, maxY = float.MinValue;
                foreach (var p in points)
                {
                    var x = Vector3.Dot(p, right);
                    var y = Vector3.Dot(p, up);
                    minX = Mathf.Min(minX, x);
                    maxX = Mathf.Max(maxX, x);
                    minY = Mathf.Min(minY, y);
                    maxY = Mathf.Max(maxY, y);
                }
                var half = Mathf.Max(maxX - minX, maxY - minY) * 0.5f * 1.08f;
                var centre = right * ((minX + maxX) * 0.5f) + up * ((minY + maxY) * 0.5f);
                _camera.transform.rotation = rotation;
                _camera.transform.position = centre - (rotation * Vector3.forward) * 150f;
                _camera.orthographicSize = half;
            }

            /// <summary>Centres the drawn silhouette and scales it to fill the square with a margin for the shadow.</summary>
            private bool Refit(Color32[] pixels)
            {
                var n = _big;
                int minX = n, minY = n, maxX = -1, maxY = -1;
                for (var y = 0; y < n; y++)
                for (var x = 0; x < n; x++)
                {
                    if (pixels[y * n + x].a < 10) continue;
                    if (x < minX) minX = x;
                    if (x > maxX) maxX = x;
                    if (y < minY) minY = y;
                    if (y > maxY) maxY = y;
                }
                if (maxX < 0) return false;
                var half = _camera.orthographicSize;
                float ToWorld(float p) => ((p + 0.5f) / n * 2f - 1f) * half;
                var cu = (ToWorld(minX) + ToWorld(maxX)) * 0.5f;
                var cv = (ToWorld(minY) + ToWorld(maxY)) * 0.5f;
                var extent = Mathf.Max(ToWorld(maxX) - ToWorld(minX), ToWorld(maxY) - ToWorld(minY)) * 0.5f;
                var t = _camera.transform;
                // A little low in the frame: the shadow falls below the model.
                t.position += t.right * cu + t.up * (cv - extent * 0.04f);
                _camera.orthographicSize = extent * 1.14f;
                return true;
            }

            private static void Capture(Camera camera, RenderTexture rt, Texture2D into)
            {
                // The first render of a new shader variant can come out magenta: render twice.
                camera.Render();
                camera.Render();
                var was = RenderTexture.active;
                RenderTexture.active = rt;
                into.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
                into.Apply(false);
                RenderTexture.active = was;
            }

            private static float[] Blur(float[] src, int n, int radius)
            {
                var a = src;
                for (var pass = 0; pass < 3; pass++)
                {
                    a = BoxBlur(a, n, radius, true);
                    a = BoxBlur(a, n, radius, false);
                }
                return a;
            }

            private static float[] BoxBlur(float[] src, int n, int r, bool horizontal)
            {
                var dst = new float[src.Length];
                for (var line = 0; line < n; line++)
                {
                    float sum = 0f;
                    var count = 0;
                    for (var i = -r; i <= r; i++)
                    {
                        var j = Mathf.Clamp(i, 0, n - 1);
                        sum += horizontal ? src[line * n + j] : src[j * n + line];
                        count++;
                    }
                    for (var i = 0; i < n; i++)
                    {
                        if (horizontal) dst[line * n + i] = sum / count;
                        else dst[i * n + line] = sum / count;
                        var outIndex = Mathf.Clamp(i - r, 0, n - 1);
                        var inIndex = Mathf.Clamp(i + r + 1, 0, n - 1);
                        sum += horizontal ? src[line * n + inIndex] - src[line * n + outIndex] : src[inIndex * n + line] - src[outIndex * n + line];
                    }
                }
                return dst;
            }

            /// <summary>
            /// The model over its shadow, then halved to 512 px with premultiplied alpha. The shadow is
            /// the blurred footprint projected onto the ground along the camera's view, a little behind
            /// the model (away from the key light).
            /// </summary>
            private byte[] Composite(Color32[] colour, float[] mask, float reach, Bounds bounds)
            {
                var n = _big;
                var rotation = _camera.transform.rotation;
                var forward = rotation * Vector3.forward;
                var right = rotation * Vector3.right;
                var up = rotation * Vector3.up;
                var origin = _camera.transform.position;
                var half = _camera.orthographicSize;
                var push = new Vector2(-0.2f, 0.25f) * Mathf.Clamp(bounds.size.y * 0.12f, 0.1f, 1.2f);
                var outPixels = new Color32[Size * Size];
                for (var y = 0; y < Size; y++)
                for (var x = 0; x < Size; x++)
                {
                    float r = 0f, g = 0f, b = 0f, a = 0f;
                    for (var sy = 0; sy < Super; sy++)
                    for (var sx = 0; sx < Super; sx++)
                    {
                        var px = x * Super + sx;
                        var py = y * Super + sy;
                        var c = colour[py * n + px];
                        var ma = c.a / 255f;
                        // Ground point under this pixel.
                        var u = ((px + 0.5f) / n * 2f - 1f) * half;
                        var v = ((py + 0.5f) / n * 2f - 1f) * half;
                        var p = origin + right * u + up * v;
                        var t = -p.y / forward.y;
                        var hit = p + forward * t;
                        var shadow = Sample(mask, TopSize, (hit.x - push.x) / reach * 0.5f + 0.5f, (hit.z - push.y) / reach * 0.5f + 0.5f) * 0.62f;
                        var outA = ma + shadow * (1f - ma);
                        r += c.r / 255f; // premultiplied by coverage already (cleared to transparent black)
                        g += c.g / 255f;
                        b += c.b / 255f;
                        a += outA;
                    }
                    var k = 1f / (Super * Super);
                    r *= k;
                    g *= k;
                    b *= k;
                    a *= k;
                    var inv = a > 1e-4f ? 1f / a : 0f;
                    outPixels[y * Size + x] = new Color32((byte)Mathf.Clamp(Mathf.RoundToInt(r * inv * 255f), 0, 255),
                        (byte)Mathf.Clamp(Mathf.RoundToInt(g * inv * 255f), 0, 255), (byte)Mathf.Clamp(Mathf.RoundToInt(b * inv * 255f), 0, 255),
                        (byte)Mathf.Clamp(Mathf.RoundToInt(a * 255f), 0, 255));
                }
                var tex = new Texture2D(Size, Size, TextureFormat.RGBA32, false);
                tex.SetPixels32(outPixels);
                tex.Apply(false);
                var png = tex.EncodeToPNG();
                Object.DestroyImmediate(tex);
                return png;
            }

            private static float Sample(float[] mask, int n, float u, float v)
            {
                if (u <= 0f || v <= 0f || u >= 1f || v >= 1f) return 0f;
                var fx = u * n - 0.5f;
                var fy = v * n - 0.5f;
                var x0 = Mathf.Clamp(Mathf.FloorToInt(fx), 0, n - 1);
                var y0 = Mathf.Clamp(Mathf.FloorToInt(fy), 0, n - 1);
                var x1 = Mathf.Min(x0 + 1, n - 1);
                var y1 = Mathf.Min(y0 + 1, n - 1);
                var tx = Mathf.Clamp01(fx - x0);
                var ty = Mathf.Clamp01(fy - y0);
                var top = Mathf.Lerp(mask[y0 * n + x0], mask[y0 * n + x1], tx);
                var bottom = Mathf.Lerp(mask[y1 * n + x0], mask[y1 * n + x1], tx);
                return Mathf.Lerp(top, bottom, ty);
            }

            private static void SetLayer(Transform t)
            {
                t.gameObject.layer = Layer;
                foreach (Transform child in t) SetLayer(child);
            }

            public void Dispose()
            {
                _camera.targetTexture = null;
                _top.targetTexture = null;
                _rt.Release();
                _topRt.Release();
                Object.DestroyImmediate(_read);
                Object.DestroyImmediate(_topRead);
                Object.DestroyImmediate(_root.gameObject);
            }
        }
    }

    /// <summary>
    /// Keeps the card pictures in step with the models: when a model file is imported and its hash
    /// no longer matches the manifest, an editor with graphics renders it again at once; in batch
    /// mode it is logged (run CardRenders.RenderBatch with graphics).
    /// </summary>
    public sealed class CardRenderWatch : AssetPostprocessor
    {
        private static void OnPostprocessAllAssets(string[] imported, string[] deleted, string[] moved, string[] movedFrom)
        {
            var changed = imported.Where(p => p.StartsWith(CardRenders.ModelsFolder + "/") && p.EndsWith(".glb")).ToList();
            if (changed.Count == 0) return;
            var manifest = CardRenders.ReadManifest();
            var stale = new HashSet<string>();
            foreach (var path in changed)
            {
                var resource = Path.GetFileNameWithoutExtension(path);
                foreach (var e in manifest.entries)
                    if (e.source == "Models/" + resource && e.hash != CardRenders.Hash(resource)) stale.Add(e.model);
            }
            if (stale.Count == 0) return;
            if (Application.isBatchMode || SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            {
                Debug.LogWarning("[CardRenders] card pictures out of date for " + string.Join(", ", stale) +
                                 ": run -executeMethod MachineBrigade.Editor.CardRenders.RenderBatch with graphics");
                return;
            }
            EditorApplication.delayCall += () => CardRenders.Render(false, stale);
        }
    }

    /// <summary>
    /// Import settings for the card pictures: UI textures (no mipmaps, clamped, alpha as
    /// transparency so the edges filter cleanly), 512 px at most, high-quality compression.
    /// </summary>
    public sealed class CardArtImport : AssetPostprocessor
    {
        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(CardRenders.OutFolder + "/")) return;
            var importer = (TextureImporter)assetImporter;
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Bilinear;
            importer.maxTextureSize = CardRenders.Size;
            importer.textureCompression = TextureImporterCompression.CompressedHQ;
        }
    }
}
