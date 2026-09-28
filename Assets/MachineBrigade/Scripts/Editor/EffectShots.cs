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
    /// Renders effects frozen at chosen moments into a contact sheet, from the game's camera angle
    /// with its post-processing, so a flash that lasts a few frames can be judged and tuned.
    /// Batch mode (with graphics): -executeMethod MachineBrigade.Editor.EffectShots.Muzzles
    /// -mbShotsOut &lt;png path&gt;.
    /// </summary>
    public static class EffectShots
    {
        private const string ProfilePath = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset";
        private static readonly float[] Moments = { 0.02f, 0.06f, 0.25f, 0.9f };

        private readonly struct Shooter
        {
            public Shooter(string model, MuzzleFx.Kind kind, Vector3 position, float altitude = 0f, float scale = 1f)
            {
                Model = model;
                Kind = kind;
                Position = position;
                Altitude = altitude;
                Scale = scale;
            }

            public string Model { get; }
            public MuzzleFx.Kind Kind { get; }
            public Vector3 Position { get; }
            public float Altitude { get; }
            public float Scale { get; }
        }

        [MenuItem("Machine Brigade/Render Muzzle Shots")]
        public static void Muzzles()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/muzzles.png");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Shots").transform;

            Stage(materials, root);
            var fx = new MuzzleFx(materials, root);
            var shooters = new[]
            {
                new Shooter("main_battle_tank", MuzzleFx.Kind.Cannon, new Vector3(-9f, 0f, 6f)),
                new Shooter("heavy_tank", MuzzleFx.Kind.Cannon, new Vector3(3f, 0f, 9f), scale: 1.25f),
                new Shooter("artillery", MuzzleFx.Kind.Artillery, new Vector3(-12f, 0f, -6f)),
                new Shooter("ifv", MuzzleFx.Kind.Autocannon, new Vector3(0f, 0f, -2f)),
                new Shooter("scout_jeep", MuzzleFx.Kind.MachineGun, new Vector3(9f, 0f, 2f)),
                new Shooter("sam_launcher", MuzzleFx.Kind.Missile, new Vector3(-3f, 0f, -12f)),
                new Shooter("attack_helicopter", MuzzleFx.Kind.Autocannon, new Vector3(10f, 0f, -9f), altitude: 7f),
            };

            var size = new Vector2Int(960, 540);
            var sheet = new Texture2D(size.x * 2, size.y * 2, TextureFormat.RGB24, false);
            var camera = Camera(root);
            var rt = new RenderTexture(size.x, size.y, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;

            // The first render compiles shaders and draws them magenta: throw it away.
            camera.Render();
            var fired = false;
            var time = 0f;
            const float step = 1f / 120f;
            for (var shot = 0; shot < Moments.Length; shot++)
            {
                if (!fired)
                {
                    foreach (var s in shooters) Fire(models, fx, root, s, 0f);
                    fired = true;
                }
                while (time + 1e-4f < Moments[shot])
                {
                    time += step;
                    fx.Tick(time);
                    foreach (var ps in root.GetComponentsInChildren<ParticleSystem>()) ps.Simulate(step, false, false, false);
                }
                camera.Render();
                RenderTexture.active = rt;
                var frame = new Texture2D(size.x, size.y, TextureFormat.RGB24, false);
                frame.ReadPixels(new Rect(0, 0, size.x, size.y), 0, 0);
                frame.Apply();
                sheet.SetPixels((shot % 2) * size.x, (1 - shot / 2) * size.y, size.x, size.y, frame.GetPixels());
                Object.DestroyImmediate(frame);
            }
            RenderTexture.active = null;
            sheet.Apply();
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output)) ?? ".");
            File.WriteAllBytes(output, sheet.EncodeToPNG());
            Debug.Log("[EffectShots] wrote " + Path.GetFullPath(output));
            camera.targetTexture = null;
            rt.Release();
            models.Dispose();
            materials.Dispose();
        }

        /// <summary>
        /// Explosions of every tier, a tank dying, a wreck burning and a napalm run, each in its own
        /// row, frozen at <see cref="BlastMoments"/> seconds after it starts. Batch mode (with
        /// graphics): -executeMethod MachineBrigade.Editor.EffectShots.Blasts -mbShotsOut &lt;png&gt;.
        /// </summary>
        [MenuItem("Machine Brigade/Render Blast Shots")]
        public static void Blasts()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/blasts.png");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20260927);
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Shots").transform;
            Stage(materials, root, 1200f);
            var rig = new BlastRig(materials, meshes, models, root);
            var scenes = BlastScenes.All(rig);

            var size = new Vector2Int(480, 270);
            var sheet = new Texture2D(size.x * BlastMoments.Length, size.y * scenes.Length, TextureFormat.RGB24, false);
            var camera = Camera(root);
            var rt = new RenderTexture(size.x, size.y, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            camera.Render();

            // Every scene runs on one clock; each starts at Start + its own offset, so a wreck can
            // have burned for a while before its row is photographed.
            const float step = 1f / 60f;
            var time = 0f;
            var frame = new Texture2D(size.x, size.y, TextureFormat.RGB24, false);
            var systems = root.GetComponentsInChildren<ParticleSystem>(true);
            for (var shot = 0; shot < BlastMoments.Length; shot++)
            {
                var until = BlastScenes.Start + BlastMoments[shot];
                while (time + 1e-4f < until)
                {
                    time += step;
                    foreach (var scene in scenes) scene.Run(time);
                    rig.Tick(time, step);
                    foreach (var ps in systems) ps.Simulate(step, false, false, false);
                }
                for (var row = 0; row < scenes.Length; row++)
                {
                    var scene = scenes[row];
                    camera.orthographicSize = scene.View;
                    camera.transform.position = scene.Focus - camera.transform.forward * 80f;
                    rig.Draw(time);
                    camera.Render();
                    RenderTexture.active = rt;
                    frame.ReadPixels(new Rect(0, 0, size.x, size.y), 0, 0);
                    frame.Apply();
                    sheet.SetPixels(shot * size.x, (scenes.Length - 1 - row) * size.y, size.x, size.y, frame.GetPixels());
                }
            }
            RenderTexture.active = null;
            sheet.Apply();
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output)) ?? ".");
            File.WriteAllBytes(output, sheet.EncodeToPNG());
            Debug.Log($"[EffectShots] wrote {Path.GetFullPath(output)}; rows: {string.Join(", ", System.Array.ConvertAll(scenes, s => s.Name))}; " +
                $"peak particles {rig.PeakParticles}, peak big quads {rig.PeakBig}, peak quad area {rig.PeakFill:F0} m2, " +
                $"peak chunks {rig.PeakChunks}; per blast: {rig.Budget}; at the peak: {rig.PeakBreakdown}");
            camera.targetTexture = null;
            rt.Release();
            Object.DestroyImmediate(frame);
            rig.Dispose();
            models.Dispose();
            meshes.Dispose();
            materials.Dispose();
        }

        /// <summary>
        /// The second play-test fix (DECISIONS 12C) against the first (11A), before and after in
        /// pairs of rows: tank rounds striking tanks (light, main battle, heavy: a tenth bigger and
        /// lingering longer), the siege tank's 203 mm and a howitzer's 155 mm, drones (FPV, Lancet,
        /// Shahed), aircraft bombs (GBU-12, FAB-500, JDAM) and the cruise missile inside a red circle
        /// of its blast radius; the Mk 84 and the MOAB after. Frozen at <see cref="ImpactMoments"/>,
        /// late ones included so the longer life shows. Batch mode (with graphics): -executeMethod
        /// MachineBrigade.Editor.EffectShots.Impacts -mbShotsOut &lt;png&gt;.
        /// </summary>
        [MenuItem("Machine Brigade/Render Impact Shots")]
        public static void Impacts()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/impacts.png");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20260928);
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Shots").transform;
            Stage(materials, root, 1800f);
            var rig = new BlastRig(materials, meshes, models, root);

            var scenes = new System.Collections.Generic.List<BlastScene>();
            Vector3 Row(int i) => new(-715f + i * 130f, 0f, 0f);
            var shells = new[] { ("light_tank", "gun_57mm"), ("main_battle_tank", "gun_120mm"), ("heavy_tank", "gun_152") };
            for (var pass = 0; pass < 2; pass++)
            {
                var before = pass == 0;
                var p = Row(pass);
                var scene = new BlastScene(before ? "tank rounds light / MBT / heavy, before" : "tank rounds, after", p, 8f);
                for (var k = 0; k < shells.Length; k++)
                {
                    // Along the view's horizontal, the (1, 0, 1) diagonal.
                    var at = p + new Vector3(0.7071f, 0f, 0.7071f) * ((k - 1) * 9.5f);
                    rig.Spawn(shells[k].Item1, at);
                    var weapon = shells[k].Item2;
                    scene.At(0f, t => rig.TankHit(weapon, at, t, before));
                }
                scenes.Add(scene);
            }
            var landings = new[] { "gun_203_siege", "howitzer" };
            for (var pass = 0; pass < 2; pass++)
            {
                var before = pass == 0;
                var p = Row(8 + pass);
                var scene = new BlastScene(before ? "siege 203 mm / howitzer 155 mm, before" : "shells landing, after", p, 14f);
                for (var k = 0; k < landings.Length; k++)
                {
                    var at = p + new Vector3(0.7071f, 0f, 0.7071f) * ((k - 0.5f) * 16f) + Vector3.up * 0.15f;
                    var weapon = landings[k];
                    scene.At(0f, t => rig.ShellLanding(weapon, at, t, before));
                }
                scenes.Add(scene);
            }
            var drones = new[] { "fpv_swarm", "lancet", "shahed" };
            for (var pass = 0; pass < 2; pass++)
            {
                var before = pass == 0;
                var p = Row(10 + pass);
                var scene = new BlastScene(before ? "drones FPV / Lancet / Shahed, before" : "drones, after", p, 13f);
                for (var k = 0; k < drones.Length; k++)
                {
                    var at = p + new Vector3(0.7071f, 0f, 0.7071f) * ((k - 1) * 12f) + Vector3.up * 0.15f;
                    var weapon = drones[k];
                    scene.At(0f, t => rig.DroneHit(weapon, at, t, before));
                }
                scenes.Add(scene);
            }
            var bombs = new[] { "guided_bomb", "jet_bombs", "stealth_payload" };
            for (var pass = 0; pass < 2; pass++)
            {
                var before = pass == 0;
                var p = Row(2 + pass);
                var scene = new BlastScene(before ? "bombs GBU-12 / FAB-500 / JDAM, before" : "bombs, after", p, 17f);
                for (var k = 0; k < bombs.Length; k++)
                {
                    var at = p + new Vector3(0.7071f, 0f, 0.7071f) * ((k - 1) * 14f) + Vector3.up * 0.15f;
                    var weapon = bombs[k];
                    scene.At(0f, t => rig.BombHit(weapon, at, t, before));
                }
                scenes.Add(scene);
            }
            for (var pass = 0; pass < 2; pass++)
            {
                var before = pass == 0;
                var p = Row(4 + pass);
                rig.Marker(p, 18f);
                scenes.Add(new BlastScene(before ? "cruise missile (18 m blast), before" : "cruise missile, after", p, 24f)
                    .At(0f, t => rig.Strike("cruise_missile", MachineBrigade.Sim.Content.ExplosionTier.Ultimate, 18f, p + Vector3.up * 0.3f, t, before)));
            }
            {
                var p = Row(6);
                scenes.Add(new BlastScene("airstrike Mk 84, after", p, 14f)
                    .At(0f, t => rig.Strike("airstrike", MachineBrigade.Sim.Content.ExplosionTier.Huge, 8f, p + Vector3.up * 0.3f, t)));
                var q = Row(7);
                rig.Marker(q, 27f);
                scenes.Add(new BlastScene("MOAB (27 m blast), after", q, 34f)
                    .At(0f, t => rig.Strike("moab", MachineBrigade.Sim.Content.ExplosionTier.Ultimate, 27f, q + Vector3.up * 0.3f, t)));
            }
            Render(rig, root, scenes.ToArray(), output, ImpactMoments);
            rig.Dispose();
            models.Dispose();
            meshes.Dispose();
            materials.Dispose();
        }

        /// <summary>
        /// Every fire-support card's own round (DECISIONS 12C), one card a row, each row timed so
        /// its first impact falls at 0: mid-fall (the aircraft or rounds on their way in), bursting
        /// or opening, arriving and after, frozen at <see cref="SupportMoments"/> seconds from it.
        /// Batch mode (with graphics): -executeMethod MachineBrigade.Editor.EffectShots.Supports
        /// -mbShotsOut &lt;png&gt;.
        /// </summary>
        [MenuItem("Machine Brigade/Render Support Shots")]
        public static void Supports()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/supports.png");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20260929);
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Shots").transform;
            Stage(materials, root, 1900f);
            var rig = new BlastRig(materials, meshes, models, root);
            var supports = new SupportRig(rig, materials, meshes, models, root);
            var scenes = new System.Collections.Generic.List<BlastScene>();
            // Rows one behind another along Z: the aircraft run along X and stay in their own row.
            for (var i = 0; i < SupportRig.Cards.Length; i++)
            {
                var (id, view) = SupportRig.Cards[i];
                scenes.Add(supports.Scene(id, new Vector3(0f, 0f, -845f + i * 130f), view));
            }
            Render(rig, root, scenes.ToArray(), output, SupportMoments, supports.Tick);
            rig.Dispose();
            models.Dispose();
            meshes.Dispose();
            materials.Dispose();
        }

        private static readonly float[] SupportMoments = { -1.3f, -0.5f, -0.15f, 0.06f, 0.45f, 1.6f };

        /// <summary>Renders <paramref name="scenes"/> as rows of a sheet frozen at <see cref="BlastMoments"/>.</summary>
        /// <param name="tick">More to run each step (fire support); its new particle systems are picked up as they appear.</param>
        private static void Render(BlastRig rig, Transform root, BlastScene[] scenes, string output, float[] moments,
            System.Action<float, float> tick = null)
        {
            var size = new Vector2Int(480, 270);
            var sheet = new Texture2D(size.x * moments.Length, size.y * scenes.Length, TextureFormat.RGB24, false);
            var camera = Camera(root);
            var rt = new RenderTexture(size.x, size.y, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            camera.Render();
            const float step = 1f / 60f;
            var time = 0f;
            var frame = new Texture2D(size.x, size.y, TextureFormat.RGB24, false);
            var systems = root.GetComponentsInChildren<ParticleSystem>(true);
            for (var shot = 0; shot < moments.Length; shot++)
            {
                var until = BlastScenes.Start + moments[shot];
                while (time + 1e-4f < until)
                {
                    time += step;
                    foreach (var scene in scenes) scene.Run(time);
                    rig.Tick(time, step);
                    if (tick != null)
                    {
                        tick(time, step);
                        systems = root.GetComponentsInChildren<ParticleSystem>(false);
                    }
                    foreach (var ps in systems) ps.Simulate(step, false, false, false);
                }
                for (var row = 0; row < scenes.Length; row++)
                {
                    var scene = scenes[row];
                    camera.orthographicSize = scene.View;
                    camera.transform.position = scene.Focus - camera.transform.forward * 80f;
                    rig.Draw(time);
                    camera.Render();
                    RenderTexture.active = rt;
                    frame.ReadPixels(new Rect(0, 0, size.x, size.y), 0, 0);
                    frame.Apply();
                    sheet.SetPixels(shot * size.x, (scenes.Length - 1 - row) * size.y, size.x, size.y, frame.GetPixels());
                }
            }
            RenderTexture.active = null;
            sheet.Apply();
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output)) ?? ".");
            File.WriteAllBytes(output, sheet.EncodeToPNG());
            Debug.Log($"[EffectShots] wrote {Path.GetFullPath(output)}; rows: {string.Join(", ", System.Array.ConvertAll(scenes, s => s.Name))}; " +
                $"peak particles {rig.PeakParticles}, peak quad area {rig.PeakFill:F0} m2; per blast: {rig.Budget}");
            camera.targetTexture = null;
            rt.Release();
            Object.DestroyImmediate(frame);
        }

        /// <summary>
        /// A flame tank pouring fire onto a tank 13 m off, from the game's camera (top row) and
        /// from the side (bottom row), frozen at <see cref="FlameMoments"/> seconds. Batch mode
        /// (with graphics): -executeMethod MachineBrigade.Editor.EffectShots.Flames -mbShotsOut &lt;png&gt;.
        /// </summary>
        [MenuItem("Machine Brigade/Render Flame Shots")]
        public static void Flames()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/flames.png");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20260928);
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Shots").transform;
            Stage(materials, root);
            var emitters = new Emitters(materials, root);
            var fx = new MuzzleFx(materials, root);
            var tank = models.Spawn("flame_tank", 0, root);
            tank.Root.transform.SetPositionAndRotation(new Vector3(-6.5f, 0f, 0f), Quaternion.Euler(0f, 90f, 0f));
            tank.Root.transform.localScale = Vector3.one * 0.95f;
            var target = models.Spawn("main_battle_tank", 1, root);
            target.Root.transform.SetPositionAndRotation(new Vector3(6.5f, 0f, 0f), Quaternion.Euler(0f, -90f, 0f));
            target.Root.transform.localScale = Vector3.one * 0.85f;
            var muzzle = tank.Muzzles.TryGetValue("main", out var m) ? m.position : tank.Root.transform.TransformPoint(tank.Muzzle);
            var aimAt = new Vector3(6.5f, 1f, 0f);

            var size = new Vector2Int(640, 360);
            var sheet = new Texture2D(size.x * FlameMoments.Length, size.y * 2, TextureFormat.RGB24, false);
            var camera = Camera(root);
            var rt = new RenderTexture(size.x, size.y, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            camera.Render();
            const float step = 1f / 60f;
            var time = 0f;
            var nextPull = 0.1f;
            var frame = new Texture2D(size.x, size.y, TextureFormat.RGB24, false);
            for (var shot = 0; shot < FlameMoments.Length; shot++)
            {
                while (time + 1e-4f < FlameMoments[shot])
                {
                    time += step;
                    if (time >= nextPull && time < 1.6f)
                    {
                        nextPull += 0.25f + Random.Range(0f, 0.05f);
                        emitters.FlameJet(muzzle, aimAt, Vector3.Distance(muzzle, aimAt) / 36f, 0.25f, time);
                        fx.Fire(MuzzleFx.Kind.MachineGun, muzzle, aimAt - muzzle, time, 0.8f, 0f);
                    }
                    emitters.Tick(time, step);
                    fx.Tick(time);
                    foreach (var ps in root.GetComponentsInChildren<ParticleSystem>()) ps.Simulate(step, false, false, false);
                }
                for (var row = 0; row < 2; row++)
                {
                    if (row == 0)
                    {
                        camera.orthographicSize = 9f;
                        camera.transform.rotation = Quaternion.Euler(52f, -45f, 0f);
                    }
                    else
                    {
                        camera.orthographicSize = 7f;
                        camera.transform.rotation = Quaternion.Euler(8f, 0f, 0f);
                    }
                    camera.transform.position = new Vector3(0f, 1.5f, 0f) - camera.transform.forward * 80f;
                    camera.Render();
                    RenderTexture.active = rt;
                    frame.ReadPixels(new Rect(0, 0, size.x, size.y), 0, 0);
                    frame.Apply();
                    sheet.SetPixels(shot * size.x, (1 - row) * size.y, size.x, size.y, frame.GetPixels());
                }
            }
            RenderTexture.active = null;
            sheet.Apply();
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output)) ?? ".");
            File.WriteAllBytes(output, sheet.EncodeToPNG());
            Debug.Log("[EffectShots] wrote " + Path.GetFullPath(output));
            camera.targetTexture = null;
            rt.Release();
            models.Dispose();
            materials.Dispose();
        }

        private static readonly float[] FlameMoments = { 0.15f, 0.45f, 0.9f, 1.4f, 2.4f };

        /// <summary>
        /// Lasers (DECISIONS 11A): an Iron Beam burning a helicopter out of the air (top row, the
        /// game's camera) and the silver bug's laser burning into the ground by a tank (bottom
        /// row), firing every 0.1 s until 1 s, frozen at <see cref="LaserMoments"/>: the charge-up,
        /// the full beam, and the afterglow once it stops. Batch mode (with graphics):
        /// -executeMethod MachineBrigade.Editor.EffectShots.Lasers -mbShotsOut &lt;png&gt;.
        /// </summary>
        [MenuItem("Machine Brigade/Render Laser Shots")]
        public static void Lasers()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/lasers.png");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20260929);
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Shots").transform;
            Stage(materials, root, 400f);
            var emitters = new Emitters(materials, root);
            var decals = new DecalPool(meshes.ScorchQuad, root, 32);
            var lasers = new LaserBeams(materials, emitters, decals, root);
            var catalog = MachineBrigade.Game.Match.GameContent.LoadCatalog();
            var ironBeam = catalog.Weapons["hel_beam"];
            var saucer = catalog.Weapons["saucer_laser"];

            // Row 1: the Iron Beam on a helicopter 12 m up. Row 2: the saucer's beam from 20 m up into the ground.
            var focusA = new Vector3(0f, 4f, 0f);
            var launcher = models.Spawn(models.Has("iron_beam") ? "iron_beam" : "sam_launcher", 0, root);
            launcher.Root.transform.SetPositionAndRotation(new Vector3(-8f, 0f, -8f), Quaternion.Euler(0f, 45f, 0f));
            var emitterA = launcher.Muzzles.TryGetValue("main", out var ma) ? ma.position : launcher.Root.transform.TransformPoint(launcher.Muzzle);
            var heli = models.Spawn("attack_helicopter", 1, root);
            var heliAt = new Vector3(7f, 12f, 7f);
            heli.Root.transform.SetPositionAndRotation(heliAt, Quaternion.Euler(0f, -135f, 0f));
            var focusB = new Vector3(80f, 2f, 0f);
            var tank = models.Spawn("main_battle_tank", 1, root);
            tank.Root.transform.SetPositionAndRotation(focusB + new Vector3(3f, -2f, 3f), Quaternion.Euler(0f, 45f, 0f));
            var emitterB = focusB + new Vector3(-10f, 20f, -10f);
            var groundAt = focusB + new Vector3(0.5f, -1.4f, 0.5f);

            var size = new Vector2Int(640, 360);
            var sheet = new Texture2D(size.x * LaserMoments.Length, size.y * 2, TextureFormat.RGB24, false);
            var camera = Camera(root);
            var rt = new RenderTexture(size.x, size.y, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            camera.Render();
            const float step = 1f / 60f;
            var time = 0f;
            var nextShot = 0.02f;
            var frame = new Texture2D(size.x, size.y, TextureFormat.RGB24, false);
            var systems = root.GetComponentsInChildren<ParticleSystem>(true);
            for (var shot = 0; shot < LaserMoments.Length; shot++)
            {
                while (time + 1e-4f < LaserMoments[shot])
                {
                    time += step;
                    if (time >= nextShot && time < 1f)
                    {
                        nextShot += 0.1f;
                        // The helicopter drifts, so the beam is seen following it.
                        var hit = heliAt + new Vector3(Mathf.Sin(time * 1.5f) * 1.5f, 0.4f, 0f);
                        heli.Root.transform.position = hit - Vector3.up * 0.4f;
                        lasers.Fire(null, 0, emitterA, hit, MachineBrigade.Sim.Core.EntityId.None, true, ironBeam, time, 0.16f);
                        var sweep = groundAt + new Vector3(Mathf.Sin(time * 2f) * 1.5f, 0f, -Mathf.Sin(time * 2f) * 1.5f);
                        lasers.Fire(null, 0, emitterB, sweep, MachineBrigade.Sim.Core.EntityId.None, false, saucer, time, 0.16f);
                    }
                    lasers.Tick(time, step, null);
                    emitters.Tick(time, step);
                    foreach (var ps in systems) ps.Simulate(step, false, false, false);
                }
                for (var row = 0; row < 2; row++)
                {
                    camera.orthographicSize = 11f;
                    camera.transform.position = (row == 0 ? focusA : focusB) - camera.transform.forward * 80f;
                    camera.Render();
                    RenderTexture.active = rt;
                    frame.ReadPixels(new Rect(0, 0, size.x, size.y), 0, 0);
                    frame.Apply();
                    sheet.SetPixels(shot * size.x, (1 - row) * size.y, size.x, size.y, frame.GetPixels());
                }
            }
            RenderTexture.active = null;
            sheet.Apply();
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output)) ?? ".");
            File.WriteAllBytes(output, sheet.EncodeToPNG());
            Debug.Log("[EffectShots] wrote " + Path.GetFullPath(output));
            camera.targetTexture = null;
            rt.Release();
            Object.DestroyImmediate(frame);
            models.Dispose();
            meshes.Dispose();
            materials.Dispose();
        }

        private static readonly float[] LaserMoments = { 0.06f, 0.16f, 0.5f, 1.12f, 1.4f };

        /// <summary>The impact sheet's columns: the flash, the fireball at its hottest, rolling into smoke, the smoke, the scar.</summary>
        private static readonly float[] ImpactMoments = { 0.04f, 0.14f, 0.35f, 0.9f, 1.5f, 2.5f, 3.2f };

        /// <summary>Seconds after a scene starts at which each column is taken.</summary>
        private static readonly float[] BlastMoments = { 0.05f, 0.25f, 0.7f, 1.6f, 4f };

        private static void Fire(ModelLibrary models, MuzzleFx fx, Transform root, in Shooter s, float now)
        {
            var instance = models.Spawn(s.Model, 0, root);
            var t = instance.Root.transform;
            t.position = s.Position + Vector3.up * s.Altitude;
            // Everyone faces the camera's right, so the flame is seen side-on.
            t.rotation = Quaternion.Euler(s.Altitude > 0f ? 12f : 0f, 45f, 0f);
            var muzzle = instance.Muzzles.TryGetValue("main", out var m) ? m.position
                : instance.Muzzles.TryGetValue("gun", out var g) ? g.position
                : t.TransformPoint(instance.Muzzle);
            var aim = s.Kind == MuzzleFx.Kind.Artillery ? t.forward + Vector3.up * 0.9f
                : s.Altitude > 0f ? t.forward * 2f + Vector3.down
                : t.forward;
            fx.Fire(s.Kind, muzzle, aim, now, s.Scale, s.Altitude > 0f ? (float?)null : 0f);
        }

        private static void Stage(MaterialLibrary materials, Transform root, float groundSize = 80f)
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.transform.SetParent(root, false);
            ground.transform.localScale = new Vector3(groundSize / 10f, 1f, groundSize / 10f);
            var sand = new Material(materials.Ground);
            sand.SetColor("_BaseColor", new Color(0.66f, 0.58f, 0.44f));
            ground.GetComponent<Renderer>().sharedMaterial = sand;

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
            camera.orthographicSize = 13f;
            camera.transform.rotation = Quaternion.Euler(52f, -45f, 0f);
            camera.transform.position = -camera.transform.forward * 80f;
            camera.nearClipPlane = 1f;
            camera.farClipPlane = 200f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.5f, 0.55f, 0.6f);
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
