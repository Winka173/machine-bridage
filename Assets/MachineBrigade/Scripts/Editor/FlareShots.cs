using System.IO;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Play-test 13: decoy flares from the game's camera angle. A fighter flies across and fires one salvo from both sides; the
    /// sheet's columns are 0.1 / 0.5 / 1.2 s after the release (close), 1.2 s at the battle's zoom, then 2.5 / 3.6 s (close);
    /// the top row by day over sand, the bottom row at night. Judge: a small white-hot point (never orange), a faint warm halo,
    /// a short thin white trail. Batch mode (with graphics):
    /// -executeMethod MachineBrigade.Editor.FlareShots.Run [-mbShotsOut &lt;folder&gt;] (default Builds/flare_shots; writes flares.png).
    /// </summary>
    public static class FlareShots
    {
        private const string ProfilePath = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset";
        private const int CellW = 400, CellH = 300;
        private const float Step = 1f / 60f;
        private const float Height = 30f;
        private const float Speed = 18f;

        private static readonly float[] Moments = { 0.1f, 0.5f, 1.2f, 1.2f, 2.5f, 3.6f };

        /// <summary>The column taken at the battle's zoom (the same moment as the one before it).</summary>
        private const int BattleZoomColumn = 3;

        [MenuItem("Machine Brigade/Render Flare Shots")]
        public static void Run()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/flare_shots");
            Directory.CreateDirectory(output);
            var sheet = new Texture2D(CellW * Moments.Length, CellH * 2, TextureFormat.RGB24, false);
            for (var row = 0; row < 2; row++) Row(sheet, row == 1, 1 - row);
            sheet.Apply();
            var path = Path.Combine(output, "flares.png");
            File.WriteAllBytes(path, sheet.EncodeToPNG());
            Object.DestroyImmediate(sheet);
            Debug.Log("[FlareShots] wrote " + Path.GetFullPath(path));
        }

        private static void Row(Texture2D sheet, bool night, int sheetRow)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20261003);
            var fog = RenderSettings.fog;
            RenderSettings.fog = false;
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Flare Shots").transform;
            var rt = new RenderTexture(CellW, CellH, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            try
            {
                Stage(materials, root, night);
                var camera = MakeCamera(root, night);
                camera.targetTexture = rt;
                var holder = new GameObject("Effects").transform;
                holder.SetParent(root, false);
                var emitters = new Emitters(materials, holder);

                // The jet, for scale: flying along +X at the battle's low altitude.
                var jet = new GameObject("Jet").transform;
                jet.SetParent(root, false);
                jet.position = new Vector3(-20f, Height, 0f);
                jet.rotation = Quaternion.LookRotation(Vector3.right, Vector3.up);
                try { models.Spawn("fighter_jet", 0, jet); }
                catch (System.Exception e) { Debug.LogWarning("[FlareShots] no fighter_jet model: " + e.Message); }

                // One salvo, both sides, as EffectsDirector.FlareSalvo fires it for a fighter (3-4 s burn, data flareBurn).
                var carrier = jet.forward * Speed;
                var below = jet.position - jet.up * 0.3f - jet.forward * 1.2f;
                for (var s = -1; s <= 1; s += 2)
                {
                    var look = jet.right * s - jet.up * 1.2f - jet.forward * 0.3f;
                    emitters.Flares(below + jet.right * (s * 0.9f), look, 1f, 3, carrier, 3f, 4f);
                }

                var time = 0f;
                for (var col = 0; col < Moments.Length; col++)
                {
                    var at = Moments[col];
                    while (time + 1e-4f < at)
                    {
                        time += Step;
                        jet.position += carrier * Step;
                        emitters.Tick(time, Step);
                        foreach (var ps in holder.GetComponentsInChildren<ParticleSystem>()) ps.Simulate(Step, false, false, false);
                    }
                    var centre = Centre(holder, jet.position);
                    var battleZoom = col == BattleZoomColumn;
                    camera.orthographicSize = battleZoom ? 22f : 7f;
                    camera.transform.position = centre - camera.transform.forward * 150f;
                    camera.Render();
                    RenderTexture.active = rt;
                    var frame = new Texture2D(CellW, CellH, TextureFormat.RGB24, false);
                    frame.ReadPixels(new Rect(0, 0, CellW, CellH), 0, 0);
                    frame.Apply();
                    sheet.SetPixels(col * CellW, sheetRow * CellH, CellW, CellH, frame.GetPixels());
                    Object.DestroyImmediate(frame);
                    RenderTexture.active = null;
                }
                camera.targetTexture = null;
            }
            finally
            {
                rt.Release();
                Object.DestroyImmediate(rt);
                models.Dispose();
                materials.Dispose();
                RenderSettings.fog = fog;
            }
        }

        /// <summary>The middle of the live flares (the halo system's particles), else the jet.</summary>
        private static Vector3 Centre(Transform holder, Vector3 fallback)
        {
            var glow = holder.Find("Decoy Flare Glow");
            var ps = glow != null ? glow.GetComponent<ParticleSystem>() : null;
            if (ps == null || ps.particleCount == 0) return fallback;
            var particles = new ParticleSystem.Particle[ps.particleCount];
            var n = ps.GetParticles(particles);
            var sum = Vector3.zero;
            for (var i = 0; i < n; i++) sum += particles[i].position;
            return sum / Mathf.Max(1, n);
        }

        private static void Stage(MaterialLibrary materials, Transform root, bool night)
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.transform.SetParent(root, false);
            ground.transform.localScale = new Vector3(60f, 1f, 60f);
            var sand = new Material(materials.Ground);
            sand.SetColor("_BaseColor", night ? new Color(0.2f, 0.19f, 0.17f) : new Color(0.66f, 0.58f, 0.44f));
            ground.GetComponent<Renderer>().sharedMaterial = sand;
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.transform.SetParent(root, false);
            sun.type = LightType.Directional;
            sun.intensity = night ? 0.12f : 1.6f;
            sun.color = night ? new Color(0.6f, 0.7f, 1f) : Color.white;
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = night ? new Color(0.08f, 0.09f, 0.13f) : new Color(0.55f, 0.58f, 0.62f);
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
            if (profile == null) return;
            var volume = new GameObject("Post").AddComponent<Volume>();
            volume.transform.SetParent(root, false);
            volume.isGlobal = true;
            volume.sharedProfile = profile;
        }

        private static Camera MakeCamera(Transform root, bool night)
        {
            var camera = new GameObject("Shot Camera").AddComponent<Camera>();
            camera.transform.SetParent(root, false);
            camera.orthographic = true;
            camera.transform.rotation = Quaternion.Euler(52f, -45f, 0f);
            camera.nearClipPlane = 1f;
            camera.farClipPlane = 500f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = night ? new Color(0.03f, 0.04f, 0.07f) : new Color(0.5f, 0.55f, 0.6f);
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
