using System.Collections.Generic;
using System.IO;
using System.Text;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Where every vehicle's rounds leave from: each vehicle is built as the game builds it
    /// (<see cref="VehicleView"/>), and a coloured ball is drawn at each point its mounts fire
    /// from (every pod, rail and twin barrel), with a line along the direction they fire. It is
    /// rendered from the side and from above, so a round that would leave from beside the barrel,
    /// from inside the hull or from the wrong gun stands out. Batch mode (with graphics):
    /// -executeMethod MachineBrigade.Editor.MuzzleAudit.Run -mbAuditOut &lt;folder&gt; [-mbAuditIds a+b].
    /// Writes &lt;id&gt;.png per vehicle and mounts.txt (the colour of each mount).
    /// </summary>
    public static class MuzzleAudit
    {
        private static readonly Color[] Colours =
        {
            new(2.4f, 0.1f, 0.1f), new(0.1f, 2.2f, 2.4f), new(2.4f, 2.2f, 0.1f), new(2.4f, 0.1f, 2.4f),
            new(0.2f, 2.4f, 0.2f), new(2.4f, 1.1f, 0.1f), new(0.4f, 0.5f, 2.4f),
        };

        private const int Size = 640;

        [MenuItem("Machine Brigade/Render Muzzle Audit")]
        public static void Run()
        {
            var output = Argument("-mbAuditOut") ?? Path.Combine(Application.dataPath, "../Builds/muzzle_audit");
            Directory.CreateDirectory(output);
            var only = Argument("-mbAuditIds");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var catalog = GameContent.LoadCatalog();
            var root = new GameObject("Audit").transform;
            Light(root);
            var unlit = Shader.Find("Universal Render Pipeline/Unlit");
            var marks = new List<Material>();
            foreach (var c in Colours)
            {
                var m = new Material(unlit);
                m.SetColor("_BaseColor", c);
                marks.Add(m);
            }
            var camera = new GameObject("Audit Camera").AddComponent<Camera>();
            camera.orthographic = true;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.36f, 0.38f, 0.4f);
            camera.nearClipPlane = 0.1f;
            camera.farClipPlane = 400f;
            var rt = new RenderTexture(Size, Size, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            var sheet = new Texture2D(Size * 3, Size, TextureFormat.RGB24, false);
            var frame = new Texture2D(Size, Size, TextureFormat.RGB24, false);
            var manifest = new StringBuilder();

            var map = new MapDefinition("audit", 200f,
                new[] { new TeamStart(0, new Vector2(0f, -80f)), new TeamStart(1, new Vector2(0f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());
            camera.Render();
            foreach (var id in catalog.Vehicles.Keys)
            {
                if (!string.IsNullOrEmpty(only) && System.Array.IndexOf(only.Split('+'), id) < 0) continue;
                var def = catalog.Vehicles[id];
                var world = new SimWorld(catalog, map, seed: 3);
                var holder = new GameObject(id).transform;
                holder.SetParent(root, false);
                var views = new ViewRegistry(models, meshes, materials, holder, 0);
                var vehicle = world.SpawnVehicle(id, 0, Vector2.Zero, 0f);
                var view = views.Add(vehicle);
                views.SnapshotAll();
                views.SnapshotAll();
                views.Render(1f, Quaternion.identity);
                // The health bar and ground rings are not the vehicle.
                foreach (var r in view.Root.GetComponentsInChildren<Renderer>())
                    if (Decoration(r.transform, view.Root)) r.enabled = false;

                manifest.Append(id);
                var bounds = Bounds(view.Root);
                for (var i = 0; i < def.Mounts.Count; i++)
                {
                    var mount = def.Mounts[i];
                    manifest.Append($" | {i}:{mount.Slot}:{mount.Weapon.Id}:{mount.Aim}");
                    var seen = new List<Vector3>();
                    for (var k = 0; k < 12; k++)
                    {
                        // A twin gun fires its barrels in turn, as a shot does in the game.
                        if (i == 0) view.Recoil();
                        var at = view.MuzzleOf(i);
                        if (seen.Exists(p => (p - at).sqrMagnitude < 0.0025f)) continue;
                        seen.Add(at);
                        var direction = i == 0 ? view.BarrelDirectionOf(0) : view.DirectionOf(i);
                        Mark(holder, meshes, marks[i % marks.Count], at, direction, bounds.size.magnitude);
                    }
                }
                manifest.AppendLine();

                // Three views: from the front-right, from the side, from above.
                bounds = Bounds(view.Root);
                var span = Mathf.Max(bounds.extents.x, bounds.extents.y, bounds.extents.z) * 1.25f + 0.5f;
                camera.orthographicSize = span;
                var views3 = new[] { Quaternion.Euler(28f, -135f, 0f), Quaternion.Euler(6f, -90f, 0f), Quaternion.Euler(90f, 0f, 0f) };
                for (var v = 0; v < views3.Length; v++)
                {
                    camera.transform.rotation = views3[v];
                    camera.transform.position = bounds.center - camera.transform.forward * 150f;
                    camera.Render();
                    RenderTexture.active = rt;
                    frame.ReadPixels(new Rect(0, 0, Size, Size), 0, 0);
                    frame.Apply();
                    sheet.SetPixels(v * Size, 0, Size, Size, frame.GetPixels());
                }
                RenderTexture.active = null;
                sheet.Apply();
                File.WriteAllBytes(Path.Combine(output, id + ".png"), sheet.EncodeToPNG());
                views.Dispose();
                Object.DestroyImmediate(holder.gameObject);
            }
            File.WriteAllText(Path.Combine(output, "mounts.txt"), manifest.ToString());
            Debug.Log("[MuzzleAudit] wrote " + Path.GetFullPath(output));
            camera.targetTexture = null;
            rt.Release();
            models.Dispose();
            meshes.Dispose();
            materials.Dispose();
        }

        private static void Mark(Transform parent, MeshLibrary meshes, Material material, Vector3 at, Vector3 direction, float size)
        {
            var ball = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            Object.DestroyImmediate(ball.GetComponent<Collider>());
            ball.transform.SetParent(parent, true);
            ball.transform.position = at;
            ball.transform.localScale = Vector3.one * Mathf.Clamp(size * 0.018f, 0.1f, 0.5f);
            ball.GetComponent<Renderer>().sharedMaterial = material;
            ball.GetComponent<Renderer>().shadowCastingMode = ShadowCastingMode.Off;
            var line = GameObject.CreatePrimitive(PrimitiveType.Cube);
            Object.DestroyImmediate(line.GetComponent<Collider>());
            line.transform.SetParent(parent, true);
            var length = Mathf.Clamp(size * 0.35f, 1.5f, 8f);
            var dir = direction.sqrMagnitude > 1e-4f ? direction.normalized : Vector3.forward;
            line.transform.position = at + dir * (length * 0.5f);
            line.transform.rotation = Quaternion.LookRotation(dir);
            line.transform.localScale = new Vector3(0.035f, 0.035f, length);
            line.GetComponent<Renderer>().sharedMaterial = material;
            line.GetComponent<Renderer>().shadowCastingMode = ShadowCastingMode.Off;
        }

        private static Bounds Bounds(Transform root)
        {
            var renderers = root.GetComponentsInChildren<Renderer>();
            var b = new Bounds(root.position, Vector3.one);
            var first = true;
            foreach (var r in renderers)
            {
                if (r is ParticleSystemRenderer || !r.enabled) continue;
                if (first)
                {
                    b = r.bounds;
                    first = false;
                }
                else b.Encapsulate(r.bounds);
            }
            return b;
        }

        private static bool Decoration(Transform t, Transform root)
        {
            for (; t != null && t != root; t = t.parent)
                if (t.name == "HealthBar" || t.name.Contains("Ring") || t.name.Contains("Selection") || t.name.Contains("Mark")) return true;
            return false;
        }

        private static void Light(Transform root)
        {
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.transform.SetParent(root, false);
            sun.type = LightType.Directional;
            sun.intensity = 1.4f;
            sun.shadows = LightShadows.None;
            sun.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.6f, 0.62f, 0.66f);
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
