using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Navigation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using NVector2 = System.Numerics.Vector2;
using Object = UnityEngine.Object;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Renders the Base screen's map pictures (prompt 14 B.1-B.2): for every map, the player's
    /// camp (team 0 of its Conquest variant) from straight above, out of the map's real scene
    /// (MapView: ground, roads, props; Surroundings: the country past the edge; the HQ model),
    /// with the game's materials, sun, ambient and post-processing but no fog or vignette and a
    /// little darker, so the slots and arrows the interface draws over it stand out. The camp's
    /// front (the HQ's heading) points up. Each picture is 1024 x 640 (16:10), supersampled 2x,
    /// in Resources/UI/Bases/&lt;map&gt;.png with &lt;map&gt;.json beside it (see
    /// <see cref="BaseMapArt.Data"/>): the frame, the camp's edge, the drop zone, the enemy
    /// approach arrows and the SHA-1 of the map file. A map whose file is unchanged is skipped.
    /// Batch mode, with graphics: -executeMethod MachineBrigade.Editor.BaseMapShots.RenderAll
    /// [-mbBaseMaps id,id] [-mbBaseMapsForce] [-mbBaseMapsDataOnly (the JSON only, pictures untouched)].
    /// </summary>
    public static class BaseMapShots
    {
        public const string OutFolder = "Assets/MachineBrigade/Resources/UI/Bases";
        public const string MapsFolder = "Assets/MachineBrigade/Resources/Data/maps";

        /// <summary>Bumped when the camera, lights, framing or arrows change, so every picture is made again.</summary>
        public const int Version = 1;

        private const int Super = 2;

        /// <summary>The camera stands this high over the ground (above every prop and hill in a frame).</summary>
        private const float CameraHeight = 150f;

        private const string ProfilePath = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset";

        /// <summary>Darker than the game (post exposure, stops) and a little less saturated, under the interface.</summary>
        private const float ExposureShift = -0.35f;

        private const float SaturationShift = -8f;
        private const float ShadowStrength = 0.7f;

        /// <summary>Beyond the battlefield's outline the picture is dimmed to this brightness (and greyed), so the camp reads first.</summary>
        private const float OutsideBrightness = 0.5f;

        private const float OutsideGrey = 0.4f;

        private const string CameraNote = "orthographic, straight down, front (HQ heading) up; the map's clear-day light (sun 1.35 #ffe9ca, " +
                                          "soft shadows 0.7, the theme's cast), no fog, no vignette, exposure -0.35, saturation -8; 2x supersampled; " +
                                          "beyond the battlefield's outline dimmed to 50% and greyed 40%";

        // The arrows: the band round the camp's edge where the routes are looked at, and how close two
        // crossings may be before they count as one way in.
        private const float BandIn = 4f;
        private const float BandOut = 12f;
        private const float MergeDistance = 22f;

        public static string MapFile(string mapId) => MapsFolder + "/" + mapId + "_conquest.json";

        public static string PicturePath(string mapId) => OutFolder + "/" + mapId + ".png";

        public static string DataPath(string mapId) => OutFolder + "/" + mapId + ".json";

        /// <summary>SHA-1 of the map file with its carriage returns dropped, so a CRLF checkout hashes the same.</summary>
        public static string Hash(string mapId)
        {
            var path = MapFile(mapId);
            if (!File.Exists(path)) return "";
            var bytes = File.ReadAllBytes(path).Where(b => b != (byte)'\r').ToArray();
            using var sha = SHA1.Create();
            return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        /// <summary>The maps with a player camp in their Conquest variant: (id, map).</summary>
        public static List<(string id, MapDefinition map)> Camps()
        {
            var camps = new List<(string, MapDefinition)>();
            foreach (var info in MatchSettings.AllMaps)
            {
                if (!File.Exists(MapFile(info.Id))) continue;
                var map = GameContent.LoadMap(info.Id + "_conquest");
                if (map.BaseOf(0) != null) camps.Add((info.Id, map));
            }
            return camps;
        }

        /// <summary>The drop zone of a side: its rally point (deliveries land round it).</summary>
        public static NVector2 DropZone(MapDefinition map, int team = 0)
        {
            foreach (var t in map.Teams)
                if (t.Team == team) return t.Rally;
            return map.BaseOf(team)?.Hq ?? NVector2.Zero;
        }

        public static BaseMapArt.Data ReadData(string mapId)
        {
            var path = DataPath(mapId);
            if (!File.Exists(path)) return null;
            try
            {
                return JsonUtility.FromJson<BaseMapArt.Data>(File.ReadAllText(path));
            }
            catch (ArgumentException)
            {
                return null;
            }
        }

        [MenuItem("Machine Brigade/Render Base Map Pictures (stale)")]
        public static void RenderStaleMenu() => Render(false, null, false);

        [MenuItem("Machine Brigade/Render Base Map Pictures (all)")]
        public static void RenderAllMenu() => Render(true, null, false);

        /// <summary>Batch entry point (with graphics).</summary>
        public static void RenderAll()
        {
            var args = Environment.GetCommandLineArgs();
            var only = Argument(args, "-mbBaseMaps")?.Split(',').Select(s => s.Trim()).Where(s => s.Length > 0).ToHashSet();
            Render(args.Contains("-mbBaseMapsForce"), only, args.Contains("-mbBaseMapsDataOnly"));
        }

        /// <summary>
        /// Makes the pictures and JSON that are missing or stale (all with <paramref name="force"/>,
        /// the named ones with <paramref name="only"/>); <paramref name="dataOnly"/> rewrites the
        /// JSON (frame and arrows) of the chosen maps and leaves the pictures and their hashes alone.
        /// </summary>
        public static int Render(bool force, HashSet<string> only, bool dataOnly)
        {
            if (!dataOnly && SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            {
                Debug.LogError("[BaseMapShots] needs a graphics device: run the batch without -nographics.");
                return 0;
            }
            var catalog = GameContent.LoadCatalog();
            Directory.CreateDirectory(OutFolder);
            var todo = new List<(string id, MapDefinition map, string hash)>();
            foreach (var (id, map) in Camps())
            {
                if (only != null && !only.Contains(id)) continue;
                var hash = Hash(id);
                var old = ReadData(id);
                var stale = force || only != null || dataOnly || old == null || old.version != Version || old.sha1 != hash || !File.Exists(PicturePath(id));
                if (stale) todo.Add((id, map, hash));
            }
            if (todo.Count == 0)
            {
                Debug.Log("[BaseMapShots] every base map picture is up to date");
                return 0;
            }

            var done = 0;
            if (dataOnly)
            {
                foreach (var (id, map, hash) in todo)
                {
                    // The hash stays the picture's: rewriting the arrows must not make an old picture look fresh.
                    var old = ReadData(id);
                    var data = Describe(id, map, new SimWorld(catalog, map, 1), old?.sha1 ?? "");
                    if (old != null)
                    {
                        data.version = old.version;
                        data.brightness = old.brightness;
                    }
                    Write(id, data);
                    done++;
                }
            }
            else done = RenderPictures(catalog, todo);
            AssetDatabase.Refresh();
            BaseMapArt.Reload();
            Debug.Log($"[BaseMapShots] wrote {done} of {todo.Count} base maps into {OutFolder}");
            return done;
        }

        private static int RenderPictures(Catalog catalog, List<(string id, MapDefinition map, string hash)> todo)
        {
            var previousScene = EditorSceneManager.GetActiveScene().path;
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var detail = ModelLibrary.HighDetail;
            ModelLibrary.HighDetail = true;
            var options = GraphicsOptions.For(GraphicsQuality.High);
            // The atmosphere sets the pipeline's MSAA, which URP copies into the quality settings
            // (saved with the project): put it back afterwards.
            var qualityMsaa = QualitySettings.antiAliasing;

            // The match scene's sun (SceneBuilder), found by the atmosphere.
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.35f;
            sun.color = new Color(1f, 0.914f, 0.792f);
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.LookRotation(new Vector3(25f, -55f, 20f));
            var atmosphere = new Atmosphere(options);
            sun.shadowStrength = ShadowStrength;
            var sunData = sun.GetUniversalAdditionalLightData();
            if (sunData != null) sunData.softShadowQuality = SoftShadowQuality.High;
            var pipeline = GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            var scale = pipeline != null ? pipeline.renderScale : 1f;
            var shadowDistance = pipeline != null ? pipeline.shadowDistance : 0f;
            if (pipeline != null) pipeline.renderScale = 1f;

            var volume = new GameObject("Post").AddComponent<Volume>();
            volume.isGlobal = true;
            var profileAsset = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
            if (profileAsset != null)
            {
                volume.sharedProfile = profileAsset;
                var profile = volume.profile; // a copy: the asset stays as it is
                if (profile.TryGet<ColorAdjustments>(out var colour))
                {
                    colour.postExposure.Override(colour.postExposure.value + ExposureShift);
                    colour.saturation.Override(colour.saturation.value + SaturationShift);
                }
                if (profile.TryGet<Vignette>(out var vignette)) vignette.intensity.Override(0f);
            }

            var big = new Vector2Int(BaseMapArt.Width * Super, BaseMapArt.Height * Super);
            var rt = new RenderTexture(big.x, big.y, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4, name = "Base Map" };
            var read = new Texture2D(big.x, big.y, TextureFormat.RGBA32, false);
            var cameras = new List<GameObject>();
            var done = 0;
            try
            {
                foreach (var (id, map, hash) in todo)
                {
                    var world = new SimWorld(catalog, map, 1);
                    var data = Describe(id, map, world, hash);
                    var materials = new MaterialLibrary();
                    var models = new ModelLibrary(materials);
                    var root = new GameObject("Base " + id).transform;
                    try
                    {
                        var (camera, surroundings) = Scene(world, map, catalog, models, materials, atmosphere, options, root, data, pipeline);
                        cameras.Add(camera.gameObject);
                        camera.targetTexture = rt;
                        // A new camera's first frames leave out queued instanced draws, and the first
                        // render of a new shader variant can come out magenta: warm it up first.
                        for (var k = 0; k < 3; k++) camera.Render();
                        surroundings.Draw(camera);
                        camera.Render();
                        var was = RenderTexture.active;
                        RenderTexture.active = rt;
                        read.ReadPixels(new Rect(0, 0, big.x, big.y), 0, 0);
                        read.Apply(false);
                        RenderTexture.active = was;
                        camera.targetTexture = null;
                        var (outside, camp) = Masks(map, data);
                        File.WriteAllBytes(PicturePath(id), Downsample(read.GetPixels32(), big.x, big.y, outside, camp, out var brightness));
                        data.brightness = Round(brightness);
                        Write(id, data);
                        done++;
                        Debug.Log($"[BaseMapShots] {id}: {data.metresWide:F0} x {data.metresHigh:F0} m, {data.arrows.Count} arrows ({data.arrowsFrom})");
                    }
                    finally
                    {
                        Object.DestroyImmediate(root.gameObject);
                        models.Dispose();
                        materials.Dispose();
                    }
                }
            }
            finally
            {
                // Each map's camera is kept to the end: the scenery queued for it stays queued.
                foreach (var c in cameras)
                    if (c != null) Object.DestroyImmediate(c);
                rt.Release();
                Object.DestroyImmediate(read);
                if (pipeline != null)
                {
                    pipeline.renderScale = scale;
                    pipeline.shadowDistance = shadowDistance;
                }
                atmosphere.Dispose();
                QualitySettings.antiAliasing = qualityMsaa;
                Object.DestroyImmediate(volume.gameObject);
                Object.DestroyImmediate(sun.gameObject);
                ModelLibrary.HighDetail = detail;
                ShaderUtil.allowAsyncCompilation = async;
                if (!string.IsNullOrEmpty(previousScene) && !Application.isBatchMode) EditorSceneManager.OpenScene(previousScene);
            }
            return done;
        }

        /// <summary>Builds one map's scene under <paramref name="root"/> and its camera over the camp.</summary>
        private static (Camera camera, Surroundings surroundings) Scene(SimWorld world, MapDefinition map, Catalog catalog, ModelLibrary models, MaterialLibrary materials,
            Atmosphere atmosphere, GraphicsOptions options, Transform root, BaseMapArt.Data data, UniversalRenderPipelineAsset pipeline)
        {
            var theme = MapTheme.For(map.Theme);
            if (theme.ModelGrass.HasValue) materials.ForModel("Grass", -1).SetColor("_BaseColor", theme.ModelGrass.Value);
            _ = new MapView(world, models, materials, theme, root, ShadowLevel.High);
            var surroundings = new Surroundings(world, models, materials, theme, root, options);

            // The HQ as the battle raises it (a static vehicle in the player's colours).
            var site = map.BaseOf(0);
            var hqModel = catalog.Vehicles.TryGetValue(catalog.Base.HqId, out var hqDef) ? hqDef.Model : catalog.Base.HqId;
            if (models.Has(hqModel))
            {
                var hq = models.Spawn(hqModel, 0, root);
                hq.Root.transform.SetPositionAndRotation(new Vector3(site.Hq.X, 0f, site.Hq.Y), Quaternion.Euler(0f, site.Heading * Mathf.Rad2Deg, 0f));
                if (hqDef != null && !Mathf.Approximately(hqDef.Scale, 1f)) hq.Root.transform.localScale *= hqDef.Scale;
            }

            // The map's clear day (Weather's Clear look), without the fog.
            atmosphere.SetMood(1f, theme.Cast, theme.Haze, 100f, 220f);
            RenderSettings.fog = false;

            var camera = new GameObject("Base Map Camera " + data.map).AddComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = data.metresHigh * 0.5f;
            camera.aspect = (float)BaseMapArt.Width / BaseMapArt.Height;
            var up = new Vector3(data.up.x, 0f, data.up.z);
            camera.transform.SetPositionAndRotation(new Vector3(data.centre.x, CameraHeight, data.centre.z), Quaternion.LookRotation(Vector3.down, up));
            camera.nearClipPlane = 1f;
            camera.farClipPlane = CameraHeight + 40f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = theme.Haze;
            camera.allowHDR = true;
            camera.allowMSAA = true;
            camera.enabled = false;
            var cameraData = camera.GetUniversalAdditionalCameraData();
            cameraData.renderPostProcessing = true;
            cameraData.renderShadows = true;
            cameraData.antialiasing = AntialiasingMode.None;
            // The shadow map reaches the farthest ground corner (URP fades shadows by distance from the camera).
            if (pipeline != null)
            {
                var corner = Mathf.Sqrt(CameraHeight * CameraHeight + data.metresWide * data.metresWide * 0.25f + data.metresHigh * data.metresHigh * 0.25f);
                pipeline.shadowDistance = corner / 0.95f + 2f;
            }
            return (camera, surroundings);
        }

        /// <summary>The frame, the camp's edge, the drop zone and the approach arrows of one map.</summary>
        public static BaseMapArt.Data Describe(string mapId, MapDefinition map, SimWorld world, string hash)
        {
            var site = map.BaseOf(0);
            var drop = DropZone(map);
            var frame = BaseMapArt.FrameFor(site, drop);
            var outline = BaseMapArt.Outline(site, drop);
            var from = "route";
            var arrows = Approaches(world, site, outline, LaneFlags.Route);
            if (arrows.Count == 0)
            {
                from = "road";
                arrows = Approaches(world, site, outline, LaneFlags.Road);
            }
            var data = new BaseMapArt.Data
            {
                version = Version, map = mapId, source = "Data/maps/" + mapId + "_conquest", sha1 = hash,
                width = BaseMapArt.Width, height = BaseMapArt.Height,
                centre = new BaseMapArt.XZ(frame.Centre), up = new BaseMapArt.XZ(frame.Up),
                metresWide = Round(frame.MetresWide), metresHigh = Round(frame.MetresHigh),
                hq = new BaseMapArt.XZ(site.Hq), heading = Round(site.Heading * Mathf.Rad2Deg),
                dropZone = new BaseMapArt.XZ(drop), dropRadius = BaseMapArt.DropRadius,
                arrowsFrom = from, camera = CameraNote,
            };
            foreach (var p in outline) data.outline.Add(new BaseMapArt.XZ(p));
            foreach (var (at, dir, routes) in arrows)
                data.arrows.Add(new BaseMapArt.Arrow { at = new BaseMapArt.XZ(at), dir = new BaseMapArt.XZ(dir), routes = routes });
            return data;
        }

        /// <summary>
        /// The ways into the camp: the lane map's cells flagged <paramref name="flag"/> in a band
        /// round the camp's edge (from 4 m inside to 12 m outside), grouped into connected runs;
        /// each run that goes right through the band is a crossing. Its arrow's head is where the
        /// run meets the edge, pointing from its outer cells to its inner ones. Crossings closer
        /// than 22 m are one way in. Ordered left to right across the camp's front.
        /// </summary>
        public static List<(NVector2 at, NVector2 dir, int routes)> Approaches(SimWorld world, BaseSiteDef site, IReadOnlyList<NVector2> outline,
            LaneFlags flag)
        {
            var grid = world.Grid;
            var lanes = world.Lanes;
            var min = new NVector2(float.MaxValue);
            var max = new NVector2(float.MinValue);
            foreach (var p in outline)
            {
                min = NVector2.Min(min, p);
                max = NVector2.Max(max, p);
            }
            var (x0, y0) = grid.CellOf(min - new NVector2(BandOut + 2f));
            var (x1, y1) = grid.CellOf(max + new NVector2(BandOut + 2f));
            x0 = Math.Max(0, x0);
            y0 = Math.Max(0, y0);
            x1 = Math.Min(grid.Width - 1, x1);
            y1 = Math.Min(grid.Height - 1, y1);
            int w = x1 - x0 + 1, h = y1 - y0 + 1;
            var s = new float[w * h];
            var on = new bool[w * h];
            for (var y = 0; y < h; y++)
            for (var x = 0; x < w; x++)
            {
                if ((lanes.FlagsOf(x0 + x, y0 + y) & flag) == 0) continue;
                var d = BaseMapArt.EdgeDistance(outline, grid.CellCenter(x0 + x, y0 + y));
                if (d < -BandIn || d > BandOut) continue;
                on[y * w + x] = true;
                s[y * w + x] = d;
            }

            var crossings = new List<(NVector2 at, NVector2 dir, int routes, float weight)>();
            var seen = new bool[w * h];
            var queue = new List<int>();
            for (var start = 0; start < on.Length; start++)
            {
                if (!on[start] || seen[start]) continue;
                queue.Clear();
                queue.Add(start);
                seen[start] = true;
                for (var head = 0; head < queue.Count; head++)
                {
                    int cx = queue[head] % w, cy = queue[head] / w;
                    for (var dy = -1; dy <= 1; dy++)
                    for (var dx = -1; dx <= 1; dx++)
                    {
                        int nx = cx + dx, ny = cy + dy;
                        if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
                        var j = ny * w + nx;
                        if (!on[j] || seen[j]) continue;
                        seen[j] = true;
                        queue.Add(j);
                    }
                }
                NVector2 inner = NVector2.Zero, outer = NVector2.Zero;
                int innerCount = 0, outerCount = 0, routes = 0;
                foreach (var i in queue)
                {
                    var c = grid.CellCenter(x0 + i % w, y0 + i / w);
                    if (s[i] <= 0f)
                    {
                        inner += c;
                        innerCount++;
                    }
                    else if (s[i] >= BandOut * 0.5f)
                    {
                        outer += c;
                        outerCount++;
                    }
                    routes = Math.Max(routes, lanes.RouteCountAt(c));
                }
                // Only a run that goes right through the band is a way in.
                if (innerCount == 0 || outerCount == 0) continue;
                inner /= innerCount;
                outer /= outerCount;
                if (NVector2.DistanceSquared(inner, outer) < 1f) continue;
                var at = Crossing(outline, outer, inner);
                crossings.Add((at, Inward(outline, at, NVector2.Normalize(inner - outer)), Math.Max(1, routes), queue.Count));
            }

            // Crossings close together are one way in (two routes leaving side by side).
            for (var merged = true; merged;)
            {
                merged = false;
                var best = MergeDistance;
                int bi = -1, bj = -1;
                for (var i = 0; i < crossings.Count; i++)
                for (var j = i + 1; j < crossings.Count; j++)
                {
                    var d = NVector2.Distance(crossings[i].at, crossings[j].at);
                    if (d >= best) continue;
                    best = d;
                    bi = i;
                    bj = j;
                }
                if (bi < 0) break;
                var a = crossings[bi];
                var b = crossings[bj];
                var weight = a.weight + b.weight;
                var mid = (a.at * a.weight + b.at * b.weight) / weight;
                var dir = NVector2.Normalize(a.dir * a.weight + b.dir * b.weight);
                var at = Crossing(outline, mid - dir * (BandOut + 6f), mid + dir * (BandOut + 6f));
                crossings[bi] = (at, Inward(outline, at, dir), Math.Max(a.routes, b.routes), weight);
                crossings.RemoveAt(bj);
                merged = true;
            }

            var up = BaseMapArt.Front(site.Heading);
            var right = BaseMapArt.RightOf(up);
            return crossings
                .OrderBy(c => MathF.Atan2(NVector2.Dot(c.at - site.Hq, right), NVector2.Dot(c.at - site.Hq, up)))
                .Select(c => (c.at, c.dir, c.routes)).ToList();
        }

        /// <summary>Where the segment from <paramref name="outside"/> to <paramref name="inside"/> meets the camp's edge (bisection).</summary>
        private static NVector2 Crossing(IReadOnlyList<NVector2> outline, NVector2 outside, NVector2 inside)
        {
            var dOut = BaseMapArt.EdgeDistance(outline, outside);
            var dIn = BaseMapArt.EdgeDistance(outline, inside);
            if (dOut < 0f || dIn > 0f) return dIn > 0f ? inside : outside;
            float lo = 0f, hi = 1f;
            for (var k = 0; k < 30; k++)
            {
                var t = (lo + hi) * 0.5f;
                if (BaseMapArt.EdgeDistance(outline, NVector2.Lerp(outside, inside, t)) > 0f) lo = t;
                else hi = t;
            }
            return NVector2.Lerp(outside, inside, (lo + hi) * 0.5f);
        }

        /// <summary>
        /// The arrow's direction: the route's own, turned in towards the camp where it runs nearly
        /// along the edge (at least 60 degrees off it), so every arrow points into the camp.
        /// </summary>
        private static NVector2 Inward(IReadOnlyList<NVector2> outline, NVector2 at, NVector2 dir)
        {
            // The edge's inward normal here: down the distance field.
            const float e = 0.5f;
            var gx = BaseMapArt.EdgeDistance(outline, at + new NVector2(e, 0f)) - BaseMapArt.EdgeDistance(outline, at - new NVector2(e, 0f));
            var gy = BaseMapArt.EdgeDistance(outline, at + new NVector2(0f, e)) - BaseMapArt.EdgeDistance(outline, at - new NVector2(0f, e));
            var g = new NVector2(gx, gy);
            if (g.LengthSquared() < 1e-6f) return dir;
            var inward = -NVector2.Normalize(g);
            for (var k = 0; k < 40 && NVector2.Dot(dir, inward) < 0.5f; k++) dir = NVector2.Normalize(dir + inward * 0.1f);
            return dir;
        }

        /// <summary>Writes the JSON, its numbers to the millimetre (JsonUtility prints floats as doubles).</summary>
        private static void Write(string mapId, BaseMapArt.Data data)
        {
            var json = JsonUtility.ToJson(data, true).Replace("\r\n", "\n");
            json = Regex.Replace(json, @"-?\d+\.\d{4,}(?:[eE][-+]?\d+)?", m =>
                Math.Round(double.Parse(m.Value, CultureInfo.InvariantCulture), 3).ToString("0.###", CultureInfo.InvariantCulture));
            File.WriteAllText(DataPath(mapId), json + "\n");
        }

        private static float Round(float v) => Mathf.Round(v * 1000f) / 1000f;

        /// <summary>
        /// Per picture pixel (rows bottom-up like the texture): how far it is past the battlefield's
        /// outline, as a dimming weight 0..1 (a 3 m fade), and whether it lies inside the camp's edge.
        /// </summary>
        private static (float[] outside, bool[] camp) Masks(MapDefinition map, BaseMapArt.Data data)
        {
            var field = BoundaryField.For(map);
            int w = BaseMapArt.Width, h = BaseMapArt.Height;
            var up = NVector2.Normalize(data.up.V);
            var right = BaseMapArt.RightOf(up);
            var shade = new float[w * h];
            var camp = new bool[w * h];
            var outline = data.outline.Select(p => p.V).ToList();
            for (var y = 0; y < h; y++)
            for (var x = 0; x < w; x++)
            {
                var u = (x + 0.5f) / w;
                var v = 1f - (y + 0.5f) / h;
                var p = data.centre.V + right * ((u - 0.5f) * data.metresWide) + up * ((0.5f - v) * data.metresHigh);
                var d = field.Distance(new Vector2(p.X, p.Y));
                shade[y * w + x] = Mathf.Clamp01((d - 0.5f) / 3f);
                camp[y * w + x] = BaseMapArt.EdgeDistance(outline, p) <= 0f;
            }
            return (shade, camp);
        }

        /// <summary>
        /// The supersampled render halved to the picture's size (box filter), the ground past the
        /// outline dimmed by <paramref name="outside"/>, as an opaque PNG; <paramref name="brightness"/>
        /// is the mean luma (0..1, as stored) of the pixels inside the camp's edge.
        /// </summary>
        private static byte[] Downsample(Color32[] pixels, int width, int height, float[] outside, bool[] camp, out float brightness)
        {
            var w = width / Super;
            var h = height / Super;
            var result = new Color32[w * h];
            double lumaSum = 0;
            var lumaCount = 0;
            for (var y = 0; y < h; y++)
            for (var x = 0; x < w; x++)
            {
                int r = 0, g = 0, b = 0;
                for (var sy = 0; sy < Super; sy++)
                for (var sx = 0; sx < Super; sx++)
                {
                    var p = pixels[(y * Super + sy) * width + x * Super + sx];
                    r += p.r;
                    g += p.g;
                    b += p.b;
                }
                const float n = Super * Super;
                var c = new Color(r / n / 255f, g / n / 255f, b / n / 255f);
                var k = outside[y * w + x];
                if (k > 0f)
                {
                    var grey = c.r * 0.3f + c.g * 0.59f + c.b * 0.11f;
                    var dim = Color.Lerp(c, new Color(grey, grey, grey), OutsideGrey) * OutsideBrightness;
                    c = Color.Lerp(c, dim, k);
                }
                result[y * w + x] = new Color32((byte)Mathf.Clamp(Mathf.RoundToInt(c.r * 255f), 0, 255),
                    (byte)Mathf.Clamp(Mathf.RoundToInt(c.g * 255f), 0, 255), (byte)Mathf.Clamp(Mathf.RoundToInt(c.b * 255f), 0, 255), 255);
                if (!camp[y * w + x]) continue;
                lumaSum += Mathf.Clamp01(c.r * 0.2126f + c.g * 0.7152f + c.b * 0.0722f);
                lumaCount++;
            }
            brightness = lumaCount > 0 ? (float)(lumaSum / lumaCount) : 0f;
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.SetPixels32(result);
            tex.Apply(false);
            var png = tex.EncodeToPNG();
            Object.DestroyImmediate(tex);
            return png;
        }

        private static string Argument(string[] args, string name)
        {
            for (var i = 0; i < args.Length - 1; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }
    }

    /// <summary>
    /// Keeps the base map pictures in step with the maps: when a Conquest map file is imported
    /// (Tools/maps/build_maps.py rewrote it) and its hash no longer matches its picture's JSON, an
    /// editor with graphics makes it again (after offering to save the open scene, which the
    /// render replaces for a moment); in batch mode it is logged (run BaseMapShots.RenderAll with graphics).
    /// </summary>
    public sealed class BaseMapWatch : AssetPostprocessor
    {
        private static void OnPostprocessAllAssets(string[] imported, string[] deleted, string[] moved, string[] movedFrom)
        {
            const string suffix = "_conquest.json";
            var stale = new HashSet<string>();
            foreach (var path in imported)
            {
                if (!path.StartsWith(BaseMapShots.MapsFolder + "/") || !path.EndsWith(suffix)) continue;
                var id = Path.GetFileName(path);
                id = id.Substring(0, id.Length - suffix.Length);
                if (MatchSettings.AllMaps.All(m => m.Id != id)) continue;
                var data = BaseMapShots.ReadData(id);
                if (data == null || data.sha1 != BaseMapShots.Hash(id)) stale.Add(id);
            }
            if (stale.Count == 0) return;
            if (Application.isBatchMode || SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            {
                Debug.LogWarning("[BaseMapShots] base map pictures out of date for " + string.Join(", ", stale) +
                                 ": run -executeMethod MachineBrigade.Editor.BaseMapShots.RenderAll with graphics");
                return;
            }
            EditorApplication.delayCall += () =>
            {
                if (EditorApplication.isPlayingOrWillChangePlaymode || !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
                BaseMapShots.Render(false, stale, false);
            };
        }
    }

    /// <summary>
    /// Import settings for the base map pictures: opaque UI textures (no mipmaps, clamped,
    /// bilinear), kept at 1024 x 640 (no power-of-two rescale), high-quality compression.
    /// </summary>
    public sealed class BaseMapArtImport : AssetPostprocessor
    {
        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(BaseMapShots.OutFolder + "/")) return;
            var importer = (TextureImporter)assetImporter;
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.alphaSource = TextureImporterAlphaSource.None;
            importer.mipmapEnabled = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Bilinear;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.maxTextureSize = BaseMapArt.Width;
            importer.textureCompression = TextureImporterCompression.CompressedHQ;
        }
    }
}
