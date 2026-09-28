using System;
using System.Collections.Generic;
using System.IO;
using MachineBrigade.Game.Effects;
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
    /// The shields (prompt 11C) frozen at chosen moments, from the game's camera angle with its
    /// post-processing: the enemy's fortress dome over its keep and ours, ripples from hits, the
    /// flicker of a damaged generator, the shatter part-way, bubbles round vehicles, the Shield
    /// Dome item, and the Low graphics variant. Batch mode (with graphics): -executeMethod
    /// MachineBrigade.Editor.ShieldShots.Shields -mbShotsOut &lt;png&gt; (each panel is also written
    /// beside it as &lt;png&gt;-&lt;n&gt;.png).
    /// </summary>
    public static class ShieldShots
    {
        private const string ProfilePath = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset";
        private const float DomeRadius = 58f;
        private const float DomeHeight = 0.5f;

        private sealed class Panel
        {
            public string Name;
            public Vector3 Focus;
            public float View;
            public Action Prepare;
        }

        [MenuItem("Machine Brigade/Render Shield Shots")]
        public static void Shields()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/shields.png");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            UnityEngine.Random.InitState(20260929);
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Shots").transform;
            Stage(materials, root, 3000f);
            var panels = new List<Panel>();
            ShieldVisual.LiteOverride = false;

            // 1. Siege: the enemy's dome over its keep, the whole of it.
            {
                var at = new Vector3(0f, 0f, 0f);
                Keep(models, root, at, 1);
                var dome = Dome(root, at, DomeRadius, ours: false);
                panels.Add(new Panel { Name = "enemy dome (Siege)", Focus = at + Vector3.up * 8f, View = 40f, Prepare = () => dome.Tick(10f) });
            }
            // 2. Defend: ours, at the battle's zoom, over the keep's middle.
            {
                var at = new Vector3(400f, 0f, 0f);
                Keep(models, root, at, 0);
                var dome = Dome(root, at, DomeRadius, ours: true);
                panels.Add(new Panel { Name = "our dome (Defend), battle zoom", Focus = at + new Vector3(8f, 0f, -8f), View = 19f, Prepare = () => dome.Tick(10f) });
            }
            // 3. Hits: four ripples of different ages near the rim facing the attackers.
            {
                var at = new Vector3(800f, 0f, 0f);
                Keep(models, root, at, 1);
                var dome = Dome(root, at, DomeRadius, ours: false);
                var rim = at + new Vector3(-0.62f, 0f, -0.62f) * DomeRadius;
                panels.Add(new Panel
                {
                    Name = "hits: ripples", Focus = rim + new Vector3(10f, 4f, 10f), View = 19f, Prepare = () =>
                    {
                        dome.Hit(rim + new Vector3(3f, 1f, -2f), 9.4f);
                        dome.Hit(rim + new Vector3(-6f, 1f, 9f), 9.62f);
                        dome.Hit(rim + new Vector3(12f, 1f, 4f), 9.8f);
                        dome.Hit(rim + new Vector3(18f, 1f, 16f), 9.95f);
                        dome.Tick(10f);
                    },
                });
            }
            // 4. A generator badly damaged: the dome flickers (tiles drop out, the skin dips).
            {
                var at = new Vector3(1200f, 0f, 0f);
                Keep(models, root, at, 1);
                var dome = Dome(root, at, DomeRadius, ours: false);
                panels.Add(new Panel
                {
                    Name = "generators damaged: flicker", Focus = at + Vector3.up * 8f, View = 40f, Prepare = () =>
                    {
                        dome.Flicker = 0.85f;
                        dome.Tick(10.02f);
                    },
                });
            }
            // 5-6. The last generator falls: the shatter a third and two-thirds of the way.
            foreach (var (part, x) in new[] { (0.3f, 1600f), (0.62f, 2000f) })
            {
                var at = new Vector3(x, 0f, 0f);
                Keep(models, root, at, 1);
                var dome = Dome(root, at, DomeRadius, ours: false);
                var share = part;
                panels.Add(new Panel
                {
                    Name = $"collapse {share:0.00}", Focus = at + Vector3.up * 8f, View = 40f, Prepare = () =>
                    {
                        dome.Collapse(10f);
                        dome.Tick(10f + share * ShieldVisual.CollapseSeconds);
                    },
                });
            }
            // 7. Bubbles: the Tempest's shield skill (enemy) taking a hit, our tanks' from the item.
            {
                var at = new Vector3(0f, 0f, 400f);
                var boss = Vehicle(models, root, "behemoth_tempest", 1, at + new Vector3(-6f, 0f, 6f), 225f, 1.2f);
                var bossShield = Bubble(boss, 1.2f, ours: false);
                var tank = Vehicle(models, root, "main_battle_tank", 0, at + new Vector3(9f, 0f, -7f), 45f, 1f);
                var tankShield = Bubble(tank, 1f, ours: true);
                var tank2 = Vehicle(models, root, "heavy_tank", 0, at + new Vector3(15f, 0f, 1f), 30f, 1f);
                var tank2Shield = Bubble(tank2, 1f, ours: true);
                var camera = Quaternion.Euler(52f, -45f, 0f) * Vector3.back;
                panels.Add(new Panel
                {
                    Name = "bubbles: boss (enemy) hit, our tanks", Focus = at + Vector3.up * 2f, View = 16f, Prepare = () =>
                    {
                        bossShield.Hit(boss.position + new Vector3(2f, 2f, -3f), 9.75f, camera);
                        bossShield.Flicker = 0.3f;
                        bossShield.Tick(10f);
                        tankShield.Hit(tank.position + new Vector3(-2f, 1.5f, 2f), 9.85f, camera);
                        tankShield.Tick(10f);
                        tank2Shield.Tick(10f);
                    },
                });
            }
            // 8. The Shield Dome item over our group, a round landing on it, and one running out.
            {
                var at = new Vector3(400f, 0f, 400f);
                for (var i = 0; i < 5; i++)
                {
                    var a = i * 1.26f;
                    Vehicle(models, root, i % 2 == 0 ? "main_battle_tank" : "ifv", 0, at + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * 7f, 45f + i * 20f, 1f);
                }
                Vehicle(models, root, "main_battle_tank", 1, at + new Vector3(-24f, 0f, 18f), 135f, 1f);
                var item = Dome(root, at, 16f, ours: true);
                panels.Add(new Panel
                {
                    Name = "Shield Dome item, a hit", Focus = at + Vector3.up * 3f, View = 17f, Prepare = () =>
                    {
                        item.Hit(at + new Vector3(-9f, 1f, 7f), 9.8f);
                        item.Tick(10f);
                    },
                });
            }
            // 9. Low graphics: the same enemy dome and a bubble, the lighter variant.
            {
                ShieldVisual.LiteOverride = true;
                var at = new Vector3(800f, 0f, 400f);
                Keep(models, root, at, 1);
                var dome = Dome(root, at, DomeRadius, ours: false);
                var boss = Vehicle(models, root, "behemoth_tempest", 1, at + new Vector3(-30f, 0f, -30f), 225f, 1.2f);
                var bossShield = Bubble(boss, 1.2f, ours: false);
                panels.Add(new Panel
                {
                    Name = "Low graphics", Focus = at + new Vector3(-24f, 4f, -24f), View = 24f, Prepare = () =>
                    {
                        dome.Hit(at + new Vector3(-40f, 1f, -40f), 9.9f);
                        dome.Tick(10f);
                        bossShield.Tick(10f);
                    },
                });
                ShieldVisual.LiteOverride = null;
            }

            Render(root, panels, output);
            models.Dispose();
            materials.Dispose();
        }

        private static ShieldVisual Dome(Transform root, Vector3 at, float radius, bool ours)
        {
            var dome = new ShieldVisual("Dome", root, ShieldVisual.Shape.Dome, radius);
            dome.Transform.position = at;
            dome.Transform.localScale = new Vector3(radius, radius * DomeHeight, radius);
            dome.SetSide(ours);
            dome.Raise(0f, 0f);
            return dome;
        }

        private static ShieldVisual Bubble(Transform vehicle, float scale, bool ours)
        {
            // As VehicleView sizes it: the model's bounds in its own frame, a little larger.
            var bounds = new Bounds();
            var first = true;
            foreach (var filter in vehicle.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null) continue;
                var b = filter.sharedMesh.bounds;
                for (var i = 0; i < 8; i++)
                {
                    var corner = b.center + Vector3.Scale(b.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                    var p = vehicle.InverseTransformPoint(filter.transform.TransformPoint(corner));
                    if (first) bounds = new Bounds(p, Vector3.zero);
                    else bounds.Encapsulate(p);
                    first = false;
                }
            }
            var radii = MachineBrigade.Game.Views.VehicleView.ShieldRadii(bounds, scale);
            var shield = new ShieldVisual("Bubble", vehicle, ShieldVisual.Shape.Bubble, Mathf.Max(radii.x, radii.z) * scale);
            shield.Transform.localPosition = bounds.center;
            shield.Transform.localScale = radii;
            shield.SetSide(ours);
            shield.Raise(0f, 0f);
            return shield;
        }

        /// <summary>A keep: the HQ in the middle, guns, a radar and generators round it, a square of walls.</summary>
        private static void Keep(ModelLibrary models, Transform root, Vector3 at, int team)
        {
            Place(models, root, "headquarters", team, at, 0f);
            foreach (var (x, z) in new[] { (-18f, -18f), (18f, -18f), (-18f, 18f), (18f, 18f) })
                Place(models, root, "gun_turret", team, at + new Vector3(x, 0f, z), 45f);
            Place(models, root, "radar_dome", team, at + new Vector3(-26f, 0f, 4f), 0f);
            Place(models, root, "shield_generator", -1, at + new Vector3(26f, 0f, -4f), 0f);
            Place(models, root, "command_tent", -1, at + new Vector3(4f, 0f, -26f), 0f);
            const float half = 40f;
            for (var d = -half + 4f; d < half; d += 8f)
            {
                Place(models, root, "base_wall", -1, at + new Vector3(d, 0f, -half), 0f);
                Place(models, root, "base_wall", -1, at + new Vector3(d, 0f, half), 0f);
                Place(models, root, "base_wall", -1, at + new Vector3(-half, 0f, d), 90f);
                Place(models, root, "base_wall", -1, at + new Vector3(half, 0f, d), 90f);
            }
            // Attackers outside the walls.
            for (var i = 0; i < 4; i++)
                Place(models, root, i % 2 == 0 ? "main_battle_tank" : "ifv", 1 - team, at + new Vector3(-54f + i * 5f, 0f, -48f + i * 3f), 45f);
        }

        private static void Place(ModelLibrary models, Transform root, string id, int team, Vector3 at, float yaw)
        {
            if (!models.Has(id)) return;
            var instance = models.Spawn(id, team, root);
            instance.Root.transform.SetPositionAndRotation(at, Quaternion.Euler(0f, yaw, 0f));
        }

        private static Transform Vehicle(ModelLibrary models, Transform root, string id, int team, Vector3 at, float yaw, float scale)
        {
            var instance = models.Spawn(models.Has(id) ? id : "main_battle_tank", team, root);
            var t = instance.Root.transform;
            t.SetPositionAndRotation(at, Quaternion.Euler(0f, yaw, 0f));
            t.localScale = Vector3.one * scale;
            return t;
        }

        private static void Render(Transform root, List<Panel> panels, string output)
        {
            var size = new Vector2Int(640, 360);
            const int columns = 3;
            var rows = (panels.Count + columns - 1) / columns;
            var sheet = new Texture2D(size.x * columns, size.y * rows, TextureFormat.RGB24, false);
            var camera = Camera(root);
            var rt = new RenderTexture(size.x, size.y, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            // The first render compiles shaders: throw it away.
            camera.Render();
            var frame = new Texture2D(size.x, size.y, TextureFormat.RGB24, false);
            var stem = Path.Combine(Path.GetDirectoryName(Path.GetFullPath(output)) ?? ".", Path.GetFileNameWithoutExtension(output));
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output)) ?? ".");
            for (var i = 0; i < panels.Count; i++)
            {
                var panel = panels[i];
                panel.Prepare();
                camera.orthographicSize = panel.View;
                camera.transform.position = panel.Focus - camera.transform.forward * 150f;
                camera.Render();
                RenderTexture.active = rt;
                frame.ReadPixels(new Rect(0, 0, size.x, size.y), 0, 0);
                frame.Apply();
                sheet.SetPixels(i % columns * size.x, (rows - 1 - i / columns) * size.y, size.x, size.y, frame.GetPixels());
                File.WriteAllBytes($"{stem}-{i + 1}.png", frame.EncodeToPNG());
            }
            RenderTexture.active = null;
            sheet.Apply();
            File.WriteAllBytes(output, sheet.EncodeToPNG());
            Debug.Log($"[ShieldShots] wrote {Path.GetFullPath(output)}; panels: {string.Join(", ", panels.ConvertAll(p => p.Name))}");
            camera.targetTexture = null;
            rt.Release();
            Object.DestroyImmediate(frame);
        }

        private static void Stage(MaterialLibrary materials, Transform root, float groundSize)
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.transform.SetParent(root, false);
            ground.transform.position = new Vector3(1000f, 0f, 200f);
            ground.transform.localScale = new Vector3(groundSize / 10f, 1f, groundSize / 10f);
            var grass = new Material(materials.Ground);
            grass.SetColor("_BaseColor", new Color(0.46f, 0.5f, 0.34f));
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

        private static Camera Camera(Transform root)
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
            var args = Environment.GetCommandLineArgs();
            for (var i = 0; i < args.Length - 1; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }
    }
}
