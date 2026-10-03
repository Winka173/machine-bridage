using System.Collections.Generic;
using System.IO;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Play-test 13: the water from the battle camera (52 degrees, the square maps' yaw, orthographic, fog on), out of each
    /// map's real scene (MapView and Surroundings, the game's sun and post-processing). One row a map, four frames: a shore
    /// of the map's own water close (14 m half-height) and at the battle's zoom (30 m), its open water close (with the
    /// Leviathan on a naval map, for scale and its shadow on the water), and the edge sea beyond the map at a SEA stretch.
    /// Judge: shallow turquoise at the shore to deep offshore, foam on the shore, waves breaking the sun's highlight into a
    /// glitter, the far sea fading into the haze; rivers calm.
    /// Batch mode (with graphics): -executeMethod MachineBrigade.Editor.SeaShots.Run [-mbShotsOut &lt;folder&gt;]
    /// [-mbSeaMaps id,id] (default lighthousebay_conquest, coralisles_conquest, borderbridge_conquest); writes sea.png.
    /// </summary>
    public static class SeaShots
    {
        private const string ProfilePath = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset";
        private const int CellW = 480, CellH = 300, Columns = 4;

        private static readonly string[] DefaultMaps = { "lighthousebay_conquest", "coralisles_conquest", "borderbridge_conquest" };

        [MenuItem("Machine Brigade/Render Sea Shots")]
        public static void Run()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/sea_shots");
            Directory.CreateDirectory(output);
            var maps = Argument("-mbSeaMaps")?.Split(',') ?? DefaultMaps;
            var catalog = GameContent.LoadCatalog();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var options = GraphicsOptions.For(GraphicsQuality.High);
            var qualityMsaa = QualitySettings.antiAliasing;
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.35f;
            sun.color = new Color(1f, 0.914f, 0.792f);
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.LookRotation(new Vector3(25f, -55f, 20f));
            var atmosphere = new Atmosphere(options);
            var volume = new GameObject("Post").AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
            var sheet = new Texture2D(CellW * Columns, CellH * maps.Length, TextureFormat.RGB24, false);
            var rt = new RenderTexture(CellW, CellH, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            var log = new System.Text.StringBuilder();
            var cameras = new List<GameObject>();
            try
            {
                for (var row = 0; row < maps.Length; row++)
                {
                    var id = maps[row].Trim();
                    MapDefinition map;
                    try { map = GameContent.LoadMap(id); }
                    catch (System.Exception e)
                    {
                        log.AppendLine($"{id}: no map ({e.Message})");
                        continue;
                    }
                    var world = new SimWorld(catalog, map, 1);
                    var materials = new MaterialLibrary();
                    var models = new ModelLibrary(materials);
                    var root = new GameObject("Sea " + id).transform;
                    try
                    {
                        var theme = MapTheme.For(map.Theme);
                        _ = new MapView(world, models, materials, theme, root, ShadowLevel.High);
                        var surroundings = new Surroundings(world, models, materials, theme, root, options);
                        atmosphere.SetMood(1f, theme.Cast, theme.Haze, 100f + RtsCamera.DepthShift, 220f + RtsCamera.DepthShift);
                        var camera = new GameObject("Sea Camera " + id).AddComponent<Camera>();
                        cameras.Add(camera.gameObject);
                        camera.orthographic = true;
                        camera.nearClipPlane = 1f;
                        camera.farClipPlane = 320f + RtsCamera.DepthShift;
                        camera.clearFlags = CameraClearFlags.SolidColor;
                        camera.backgroundColor = theme.Haze;
                        camera.allowHDR = true;
                        camera.enabled = false;
                        camera.GetUniversalAdditionalCameraData().renderPostProcessing = true;
                        camera.targetTexture = rt;

                        var (shore, open, line) = WaterPoints(world, map);
                        log.AppendLine($"{id}: {line}");
                        if (open.HasValue && map.Sea != null && models.Has("leviathan"))
                        {
                            var ship = models.Spawn("leviathan", 1, root);
                            ship.Root.transform.SetPositionAndRotation(open.Value, Quaternion.Euler(0f, 45f, 0f));
                        }
                        var frames = new (Vector3? at, float half)[]
                        {
                            (shore, 14f), (shore, 30f), (open, 14f), (EdgeSeaPoint(map), 30f),
                        };
                        for (var col = 0; col < Columns; col++)
                        {
                            var (at, half) = frames[col];
                            if (!at.HasValue) continue;
                            var rotation = Quaternion.Euler(52f, RtsCamera.SquareYaw, 0f);
                            camera.orthographicSize = half;
                            camera.transform.SetPositionAndRotation(at.Value - rotation * Vector3.forward * RtsCamera.Distance, rotation);
                            // The first renders of a new shader variant can come out magenta: warm up.
                            for (var k = 0; k < 3; k++) camera.Render();
                            surroundings.Draw(camera);
                            camera.Render();
                            RenderTexture.active = rt;
                            var frame = new Texture2D(CellW, CellH, TextureFormat.RGB24, false);
                            frame.ReadPixels(new Rect(0, 0, CellW, CellH), 0, 0);
                            frame.Apply();
                            sheet.SetPixels(col * CellW, (maps.Length - 1 - row) * CellH, CellW, CellH, frame.GetPixels());
                            Object.DestroyImmediate(frame);
                            RenderTexture.active = null;
                        }
                        camera.targetTexture = null;
                    }
                    finally
                    {
                        Object.DestroyImmediate(root.gameObject);
                        models.Dispose();
                        materials.Dispose();
                    }
                }
                sheet.Apply();
                File.WriteAllBytes(Path.Combine(output, "sea.png"), sheet.EncodeToPNG());
                File.WriteAllText(Path.Combine(output, "sea.txt"), log.ToString());
                Debug.Log("[SeaShots] wrote " + Path.GetFullPath(output) + "\n" + log);
            }
            finally
            {
                foreach (var c in cameras)
                    if (c != null) Object.DestroyImmediate(c);
                rt.Release();
                Object.DestroyImmediate(sheet);
                atmosphere.Dispose();
                QualitySettings.antiAliasing = qualityMsaa;
                Object.DestroyImmediate(volume.gameObject);
                Object.DestroyImmediate(sun.gameObject);
                ShaderUtil.allowAsyncCompilation = async;
            }
        }

        /// <summary>
        /// A shore of the map's own water (a water tile with land beside it, nearest the map's middle) and its most open water
        /// (the water tile farthest from any shore tile).
        /// </summary>
        private static (Vector3? shore, Vector3? open, string line) WaterPoints(SimWorld world, MapDefinition map)
        {
            var tiles = new List<Prop>();
            foreach (var p in world.Props)
                if (p.Def.Id is "river_water" or "river_ford") tiles.Add(p);
            if (tiles.Count == 0) return (null, null, "no water tiles");
            var at = new HashSet<(int, int)>();
            foreach (var t in tiles) at.Add((Mathf.RoundToInt(t.Position.X), Mathf.RoundToInt(t.Position.Y)));
            var centre = (map.Min + map.Max) * 0.5f;
            var shores = new List<Prop>();
            foreach (var t in tiles)
            {
                int x = Mathf.RoundToInt(t.Position.X), z = Mathf.RoundToInt(t.Position.Y);
                var step = Mathf.Max(1, Mathf.RoundToInt(t.Width));
                if (!at.Contains((x + step, z)) || !at.Contains((x - step, z)) || !at.Contains((x, z + step)) || !at.Contains((x, z - step)))
                {
                    var inside = t.Position.X > map.Min.X + 6f && t.Position.X < map.Max.X - 6f && t.Position.Y > map.Min.Y + 6f && t.Position.Y < map.Max.Y - 6f;
                    if (inside) shores.Add(t);
                }
            }
            Prop shore = null;
            var best = float.MaxValue;
            foreach (var s in shores)
            {
                var d = System.Numerics.Vector2.Distance(s.Position, centre);
                if (d < best) { best = d; shore = s; }
            }
            Prop open = null;
            var far = -1f;
            for (var i = 0; i < tiles.Count; i += Mathf.Max(1, tiles.Count / 600))
            {
                var t = tiles[i];
                var near = float.MaxValue;
                foreach (var s in shores) near = Mathf.Min(near, System.Numerics.Vector2.DistanceSquared(s.Position, t.Position));
                if (near > far) { far = near; open = t; }
            }
            Vector3? V(Prop p) => p == null ? (Vector3?)null : new Vector3(p.Position.X, 0f, p.Position.Y);
            return (V(shore), V(open), $"{tiles.Count} water tiles, {shores.Count} on a shore, open water {Mathf.Sqrt(Mathf.Max(0f, far)):0} m from it");
        }

        /// <summary>A point 24 m beyond the map's rectangle at the middle of its first SEA stretch, or null.</summary>
        private static Vector3? EdgeSeaPoint(MapDefinition map)
        {
            foreach (var s in map.Edges.Segments)
            {
                if (s.Type != EdgeType.Sea) continue;
                var along = (s.From + s.To) * 0.5f;
                return s.Side switch
                {
                    "N" => new Vector3(along, 0f, map.Max.Y + 24f),
                    "S" => new Vector3(along, 0f, map.Min.Y - 24f),
                    "E" => new Vector3(map.Max.X + 24f, 0f, along),
                    "W" => new Vector3(map.Min.X - 24f, 0f, along),
                    _ => (Vector3?)null,
                };
            }
            return null;
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
