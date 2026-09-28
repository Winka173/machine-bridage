using System.Collections.Generic;
using System.IO;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Where rounds leave from and how they fly, from the game's camera angle. headings.png: each
    /// shooter facing 0, 90, 180 and 270 degrees with its turret swung onto a target off to one
    /// side (the gun laid as it fires), frozen on the frame its first round leaves; a green ball
    /// marks the drawn barrel tip and a red one the round's first drawn position. flights.png:
    /// artillery, mortar and rocket rounds at four moments of their flight with their trails.
    /// Batch mode (with graphics): -executeMethod MachineBrigade.Editor.MuzzleShots.Run
    /// -mbShotsOut &lt;folder&gt; [-mbShotsIds a+b].
    /// <see cref="Flashes"/>: every weapon's muzzle flash against its drawn barrel tip, for every
    /// vehicle; <see cref="GroundFire"/>: a tank parked in a burning patch (DECISIONS 12A).
    /// </summary>
    public static class MuzzleShots
    {
        private const string ProfilePath = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset";
        private const int CellW = 400, CellH = 300;
        private static readonly int[] Headings = { 0, 90, 180, 270 };
        private static readonly float[] Moments = { 0.04f, 0.3f, 0.6f, 0.9f };

        private static readonly string[] HeadingIds =
            { "main_battle_tank", "ifv", "mortar_carrier", "artillery", "sam_launcher", "fpv_carrier", "attack_helicopter", "gun_turret" };

        private static readonly string[] FlightIds = { "mortar_carrier", "artillery", "mlrs", "siege_mortar", "siege_tank", "grad_truck" };

        private sealed class Kit
        {
            public Transform Holder;
            public SimWorld World;
            public ViewRegistry Views;
            public TracerPool Tracers;
            public ProjectilePool Projectiles;
            public Emitters Emitters;
            public MuzzleFx Muzzle;
            public WeaponEffects Weapons;
            public Vehicle Shooter;
            public Vector3 Target;
        }

        [MenuItem("Machine Brigade/Render Muzzle And Flight Shots")]
        public static void Run()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/muzzle_shots");
            Directory.CreateDirectory(output);
            var only = Argument("-mbShotsIds");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20260928);
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var catalog = GameContent.LoadCatalog();
            var root = new GameObject("Muzzle Shots").transform;
            Stage(materials, root);
            var camera = MakeCamera(root);
            var rt = new RenderTexture(CellW, CellH, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            camera.Render();
            var green = Unlit(new Color(0.1f, 2.4f, 0.2f));
            var red = Unlit(new Color(2.6f, 0.1f, 0.1f));
            var log = new System.Text.StringBuilder();

            var ids = Filter(HeadingIds, only, catalog);
            var sheet = new Texture2D(CellW * Headings.Length, CellH * Mathf.Max(1, ids.Count), TextureFormat.RGB24, false);
            for (var row = 0; row < ids.Count; row++)
                for (var col = 0; col < Headings.Length; col++)
                {
                    var kit = Build(catalog, models, meshes, materials, root, ids[row], Headings[col], 70f, 0.6f);
                    var launched = FireFirst(kit, camera, out var fromNode);
                    var line = $"{ids[row]} h{Headings[col]}: ";
                    if (launched.HasValue)
                    {
                        SimulateParticles(kit.Holder, 0.02f);
                        var first = FirstDrawn(kit, launched.Value);
                        Ball(kit.Holder, green, fromNode, 0.16f);
                        Ball(kit.Holder, red, first, 0.1f);
                        line += $"round start {Vector3.Distance(first, fromNode):0.000} m from the drawn tip";
                    }
                    else line += "no shot";
                    log.AppendLine(line);
                    var view = kit.Views.TryGet(kit.Shooter.Id, out var v) ? v : null;
                    var centre = view != null ? view.Position + Vector3.up * 1.2f : Vector3.zero;
                    Frame(camera, centre, view != null && view.Flying ? 9f : 6.5f);
                    Snap(camera, rt, sheet, col, ids.Count - 1 - row);
                    Object.DestroyImmediate(kit.Holder.gameObject);
                }
            sheet.Apply();
            File.WriteAllBytes(Path.Combine(output, "headings.png"), sheet.EncodeToPNG());

            ids = Filter(FlightIds, only, catalog);
            sheet = new Texture2D(CellW * Moments.Length, CellH * Mathf.Max(1, ids.Count), TextureFormat.RGB24, false);
            for (var row = 0; row < ids.Count; row++)
            {
                var kit = Build(catalog, models, meshes, materials, root, ids[row], 0f, 25f, 0.75f);
                var launched = FireFirst(kit, camera, out var fromNode);
                if (!launched.HasValue)
                {
                    log.AppendLine($"{ids[row]} flight: no shot");
                    Object.DestroyImmediate(kit.Holder.gameObject);
                    continue;
                }
                var e = launched.Value;
                var duration = Mathf.Max(0.05f, e.Value);
                var time = 0f;
                const float step = 1f / 60f;
                Ball(kit.Holder, green, fromNode, 0.16f);
                for (var m = 0; m < Moments.Length; m++)
                {
                    while (time + 1e-4f < Moments[m] * duration)
                    {
                        time += step;
                        kit.Tracers.Tick(time, kit.Emitters);
                        kit.Projectiles.Tick(time, kit.Emitters);
                        kit.Muzzle.Tick(time);
                        kit.Emitters.Tick(time, step);
                        SimulateParticles(kit.Holder, step);
                    }
                    // Close on the round, so the round and its trail can be judged together.
                    var round = FirstDrawn(kit, e);
                    Frame(camera, round, 3.2f);
                    Snap(camera, rt, sheet, m, ids.Count - 1 - row);
                }
                log.AppendLine($"{ids[row]} flight: {e.DefId} {duration:0.00} s over {Vector3.Distance(fromNode, kit.Target):0} m");
                Object.DestroyImmediate(kit.Holder.gameObject);
            }
            sheet.Apply();
            File.WriteAllBytes(Path.Combine(output, "flights.png"), sheet.EncodeToPNG());
            File.WriteAllText(Path.Combine(output, "shots.txt"), log.ToString());
            Debug.Log("[MuzzleShots] wrote " + Path.GetFullPath(output) + "\n" + log);
            camera.targetTexture = null;
            rt.Release();
            models.Dispose();
            materials.Dispose();
        }

        /// <summary>
        /// flashes_NN.png: one row per vehicle (every one with a gun, elites, bosses, towers and
        /// aircraft too), facing 0, 90, 180 and 270 degrees with its turret swung onto a dummy off
        /// to one side, frozen on the frame the most of its mounts show a live flash; a small green
        /// ball on each drawn barrel tip a flash rides. The fifth column is the last moment again
        /// through a perspective camera like the detail page's, the vehicle off the middle of its
        /// view. flashes.txt lists the worst flash offset per cell. Batch mode (with graphics):
        /// -executeMethod MachineBrigade.Editor.MuzzleShots.Flashes -mbShotsOut &lt;folder&gt; [-mbShotsIds a+b].
        /// </summary>
        public static void Flashes()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/muzzle_shots");
            Directory.CreateDirectory(output);
            var only = Argument("-mbShotsIds");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20260929);
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var catalog = GameContent.LoadCatalog();
            var root = new GameObject("Flash Shots").transform;
            Stage(materials, root);
            var camera = MakeCamera(root);
            var perspective = MakeCamera(root);
            perspective.orthographic = false;
            perspective.fieldOfView = 36f;
            perspective.nearClipPlane = 0.5f;
            var rt = new RenderTexture(CellW, CellH, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            perspective.targetTexture = rt;
            camera.Render();
            var green = Unlit(new Color(0.1f, 2.4f, 0.2f));
            var log = new System.Text.StringBuilder();
            var ids = new List<string>();
            foreach (var def in catalog.Vehicles.Values)
                if (def.Mounts.Count > 0 && System.Linq.Enumerable.Any(def.Mounts, m => !m.Weapon.Melee) &&
                    (string.IsNullOrEmpty(only) || System.Array.IndexOf(only.Split('+'), def.Id) >= 0))
                    ids.Add(def.Id);
            ids.Sort(System.StringComparer.Ordinal);
            const int rows = 10;
            var cols = Headings.Length + 1;
            for (var page = 0; page * rows < ids.Count; page++)
            {
                var count = Mathf.Min(rows, ids.Count - page * rows);
                var sheet = new Texture2D(CellW * cols, CellH * count, TextureFormat.RGB24, false);
                for (var r = 0; r < count; r++)
                {
                    var id = ids[page * rows + r];
                    var line = new System.Text.StringBuilder(id + ":");
                    for (var col = 0; col < Headings.Length; col++)
                    {
                        var kit = Build(catalog, models, meshes, materials, root, id, Headings[col], 70f, 0.6f);
                        kit.Emitters.LateFeed = true;
                        var worst = FlashMoment(kit, camera, rt, sheet, col, count - 1 - r, green,
                            col == Headings.Length - 1 ? perspective : null, Headings.Length, out var lit);
                        line.Append($" h{Headings[col]}={worst:0.000}m/{lit}");
                        Object.DestroyImmediate(kit.Holder.gameObject);
                    }
                    log.AppendLine(line.ToString());
                }
                sheet.Apply();
                File.WriteAllBytes(Path.Combine(output, $"flashes_{page + 1:00}.png"), sheet.EncodeToPNG());
                Object.DestroyImmediate(sheet);
            }
            File.WriteAllText(Path.Combine(output, "flashes.txt"), log.ToString());
            Debug.Log("[MuzzleShots] flashes in " + Path.GetFullPath(output) + "\n" + log);
            camera.targetTexture = null;
            perspective.targetTexture = null;
            rt.Release();
            models.Dispose();
            materials.Dispose();
        }

        /// <summary>
        /// Plays the fight for up to five seconds in the game's frame order and snaps the cell each
        /// time more mounts show a live flash than before; returns the worst flash offset seen.
        /// </summary>
        private static float FlashMoment(Kit kit, Camera camera, RenderTexture rt, Texture2D sheet, int col, int row, Material green,
            Camera perspective, int perspectiveCol, out int flashes)
        {
            const float frame = 1f / 30f;
            var measured = new List<MuzzleFx.Measured>();
            var balls = new List<GameObject>();
            var best = 0;
            var worst = 0f;
            var accumulator = 0f;
            var now = 1f;
            var shots = new List<SimEvent>();
            var systems = kit.Holder.GetComponentsInChildren<ParticleSystem>();
            flashes = 0;
            for (var f = 0; f < 150; f++)
            {
                accumulator += frame;
                while (accumulator >= 0.05f)
                {
                    accumulator -= 0.05f;
                    kit.World.Step(0.05f);
                    kit.Views.SnapshotAll();
                    foreach (var e in kit.World.Events)
                        if (e.Kind == SimEventKind.WeaponFired && e.Entity == kit.Shooter.Id) shots.Add(e);
                    kit.World.ClearEvents();
                }
                now += frame;
                kit.Muzzle.Tick(now);
                kit.Emitters.Tick(now, frame);
                kit.Tracers.Tick(now, kit.Emitters);
                kit.Projectiles.Tick(now, kit.Emitters);
                foreach (var ps in systems) ps.Simulate(frame, false, false, false);
                kit.Views.Render(accumulator / 0.05f, camera.transform.rotation);
                kit.Muzzle.Follow(now);
                kit.Emitters.FeedFlames(now, frame);
                if (!kit.Views.TryGet(kit.Shooter.Id, out var view)) break;
                foreach (var e in shots) kit.Weapons.Fired(e, view, kit.Views, now);
                flashes += shots.Count;
                shots.Clear();
                kit.Muzzle.Measure(measured);
                var tips = new List<Vector3>();
                foreach (var m in measured)
                {
                    worst = Mathf.Max(worst, Vector3.Distance(m.Flash, m.Muzzle));
                    if (!tips.Exists(t => (t - m.Muzzle).sqrMagnitude < 0.01f)) tips.Add(m.Muzzle);
                }
                if (tips.Count <= best) continue;
                best = tips.Count;
                foreach (var b in balls) Object.DestroyImmediate(b);
                balls.Clear();
                foreach (var t in tips)
                {
                    Ball(kit.Holder, green, t, 0.09f);
                    balls.Add(kit.Holder.GetChild(kit.Holder.childCount - 1).gameObject);
                }
                var centre = view.Position + Vector3.up * 1.2f;
                var span = Mathf.Clamp(view.Def.Radius * 2.2f, 4.5f, 16f) * (view.Flying ? 1.4f : 1f);
                Frame(camera, centre, span);
                Snap(camera, rt, sheet, col, row);
                if (perspective != null)
                {
                    // As the detail page's range sees it: from farther back and off to one side, so
                    // a flash pulled along the view axis would slide off its barrel.
                    perspective.transform.rotation = camera.transform.rotation;
                    var distance = span / Mathf.Tan(18f * Mathf.Deg2Rad);
                    perspective.transform.position = centre - perspective.transform.forward * distance
                        - perspective.transform.right * (span * 0.8f) - perspective.transform.up * (span * 0.45f);
                    Snap(perspective, rt, sheet, perspectiveCol, row);
                }
            }
            return worst;
        }

        /// <summary>
        /// groundfire.png: a main battle tank and a scout jeep parked in burning ground patches next
        /// to a patch on its own, from the game's camera, as the flames were drawn (left: pulled
        /// towards the camera, over the vehicles) and as they are now (right: lying on the ground
        /// in depth, under them). Batch mode (with graphics):
        /// -executeMethod MachineBrigade.Editor.MuzzleShots.GroundFire -mbShotsOut &lt;folder&gt;.
        /// </summary>
        public static void GroundFire()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/muzzle_shots");
            Directory.CreateDirectory(output);
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20260929);
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var catalog = GameContent.LoadCatalog();
            var root = new GameObject("Ground Fire").transform;
            Stage(materials, root);
            var camera = MakeCamera(root);
            var rt = new RenderTexture(CellW * 2, CellH * 2, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            camera.Render();
            var sheet = new Texture2D(CellW * 4, CellH * 2, TextureFormat.RGB24, false);
            for (var pass = 0; pass < 2; pass++)
            {
                var holder = new GameObject("pass" + pass).transform;
                holder.SetParent(root, false);
                var map = new MapDefinition("fire", 200f,
                    new[] { new TeamStart(0, new Vector2(0f, -80f)), new TeamStart(1, new Vector2(0f, 80f)) },
                    new List<PropPlacement>(), new List<UnitPlacement>());
                var world = new SimWorld(catalog, map, seed: 3);
                var views = new ViewRegistry(models, meshes, materials, holder, 0);
                var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-2.5f, 0f), 0.6f);
                var jeep = world.SpawnVehicle("scout_jeep", 0, new Vector2(4.5f, 3f), 2.2f);
                views.Add(tank);
                views.Add(jeep);
                var fires = new FireSpots(materials, holder);
                foreach (var ps in holder.GetComponentsInChildren<ParticleSystemRenderer>())
                    if (ps.sharedMaterial != null && ps.sharedMaterial.HasFloat("_OntoGround") && ps.sharedMaterial.GetFloat("_OntoGround") > 0.5f && pass == 0)
                        ps.sharedMaterial = new Material(ps.sharedMaterial) { hideFlags = HideFlags.DontSave };
                if (pass == 0)
                    foreach (var ps in holder.GetComponentsInChildren<ParticleSystemRenderer>())
                        if (ps.sharedMaterial != null && ps.sharedMaterial.HasFloat("_OntoGround")) ps.sharedMaterial.SetFloat("_OntoGround", 0f);
                fires.Ignite(new Vector3(-2.5f, 0.05f, 0f), 1.2f, 60f, 0f);
                fires.Ignite(new Vector3(4.5f, 0.05f, 3f), 0.8f, 60f, 0f);
                fires.Ignite(new Vector3(-1f, 0.05f, 7f), 1f, 60f, 0f);
                var systems = holder.GetComponentsInChildren<ParticleSystem>();
                var t = 0f;
                for (var f = 0; f < 60; f++)
                {
                    t += 1f / 30f;
                    world.Step(1f / 30f);
                    views.SnapshotAll();
                    world.ClearEvents();
                    fires.Tick(t, 1f / 30f);
                    foreach (var ps in systems) ps.Simulate(1f / 30f, false, false, false);
                    views.Render(1f, camera.transform.rotation);
                }
                Frame(camera, new Vector3(0.5f, 1f, 2.5f), 9f);
                camera.Render();
                RenderTexture.active = rt;
                var shot = new Texture2D(CellW * 2, CellH * 2, TextureFormat.RGB24, false);
                shot.ReadPixels(new Rect(0, 0, CellW * 2, CellH * 2), 0, 0);
                shot.Apply();
                sheet.SetPixels(pass * CellW * 2, 0, CellW * 2, CellH * 2, shot.GetPixels());
                RenderTexture.active = null;
                Object.DestroyImmediate(shot);
                Object.DestroyImmediate(holder.gameObject);
            }
            sheet.Apply();
            File.WriteAllBytes(Path.Combine(output, "groundfire.png"), sheet.EncodeToPNG());
            Debug.Log("[MuzzleShots] ground fire in " + Path.GetFullPath(output));
            camera.targetTexture = null;
            rt.Release();
            models.Dispose();
            materials.Dispose();
        }

        private static List<string> Filter(string[] ids, string only, Catalog catalog)
        {
            var list = new List<string>();
            foreach (var id in string.IsNullOrEmpty(only) ? ids : only.Split('+'))
                if (catalog.Vehicles.ContainsKey(id)) list.Add(id);
            return list;
        }

        private static Kit Build(Catalog catalog, ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials, Transform root,
            string id, float headingDegrees, float bearingDegrees, float reachShare)
        {
            var kit = new Kit { Holder = new GameObject(id).transform };
            kit.Holder.SetParent(root, false);
            var map = new MapDefinition("shots", 260f,
                new[] { new TeamStart(0, new Vector2(0f, -100f)), new TeamStart(1, new Vector2(0f, 100f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());
            kit.World = new SimWorld(catalog, map, seed: 5);
            kit.Views = new ViewRegistry(models, meshes, materials, kit.Holder, 0);
            kit.Tracers = new TracerPool(meshes.Box, materials.Tracer, kit.Holder, 64);
            kit.Projectiles = new ProjectilePool(kit.Holder, 32);
            kit.Emitters = new Emitters(materials, kit.Holder);
            kit.Muzzle = new MuzzleFx(materials, kit.Holder);
            kit.Weapons = new WeaponEffects(catalog, models, kit.Tracers, kit.Projectiles, kit.Emitters, kit.Muzzle, (_, _) => { });
            var def = catalog.Vehicles[id];
            var h = headingDegrees * Mathf.Deg2Rad;
            kit.Shooter = kit.World.SpawnVehicle(id, 0, Vector2.Zero, h);
            kit.Views.Add(kit.Shooter);
            var reach = Mathf.Max(def.Weapon.MinRange + 8f, Mathf.Min(def.Weapon.Range * reachShare, 45f));
            var bearing = h + bearingDegrees * Mathf.Deg2Rad;
            var air = !def.Weapon.CanTarget(false);
            var at = new Vector2(Mathf.Sin(bearing), Mathf.Cos(bearing)) * reach;
            var target = kit.World.SpawnVehicle(air ? "attack_helicopter" : "main_battle_tank", 1, at, h);
            kit.World.MakeDummy(target);
            kit.Views.Add(target);
            kit.Target = new Vector3(at.X, 0.4f, at.Y);
            kit.World.Submit(new Command(CommandType.Attack, 0, new[] { kit.Shooter.Id }, default, target.Id));
            return kit;
        }

        /// <summary>Steps the battle until the shooter's first round, drawing the views each step; starts it after the views are drawn, as the game does.</summary>
        private static SimEvent? FireFirst(Kit kit, Camera camera, out Vector3 tip)
        {
            tip = Vector3.zero;
            for (var i = 0; i < 20 * 25; i++)
            {
                kit.World.Step(0.05f);
                kit.Views.SnapshotAll();
                kit.Views.Render(1f, camera.transform.rotation);
                foreach (var e in kit.World.Events)
                {
                    if (e.Kind != SimEventKind.WeaponFired || e.Entity != kit.Shooter.Id || e.Mount != 0) continue;
                    if (!kit.Views.TryGet(kit.Shooter.Id, out var view)) continue;
                    kit.Weapons.Fired(e, view, kit.Views, 0f);
                    tip = view.LastMuzzleNode != null ? view.LastMuzzleNode.TransformPoint(view.LastMuzzleLocal) : view.MuzzleWorld;
                    kit.World.ClearEvents();
                    return e;
                }
                kit.World.ClearEvents();
            }
            return null;
        }

        /// <summary>Where the round is drawn on its first frame: the back of its tracer streak, or its model's middle.</summary>
        private static Vector3 FirstDrawn(Kit kit, SimEvent e)
        {
            foreach (Transform t in kit.Holder.Find("Projectiles"))
                if (t.gameObject.activeSelf) return t.position;
            foreach (var (back, _) in kit.Tracers.Streaks()) return back;
            return new Vector3(e.Position.X, 0f, e.Position.Y);
        }

        private static void SimulateParticles(Transform root, float dt)
        {
            foreach (var ps in root.GetComponentsInChildren<ParticleSystem>()) ps.Simulate(dt, false, false, false);
        }

        private static void Ball(Transform parent, Material material, Vector3 at, float size)
        {
            var ball = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            Object.DestroyImmediate(ball.GetComponent<Collider>());
            ball.transform.SetParent(parent, true);
            ball.transform.position = at;
            ball.transform.localScale = Vector3.one * size;
            ball.GetComponent<Renderer>().sharedMaterial = material;
            ball.GetComponent<Renderer>().shadowCastingMode = ShadowCastingMode.Off;
        }

        private static Material Unlit(Color colour)
        {
            var m = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
            m.SetColor("_BaseColor", colour);
            return m;
        }

        private static void Frame(Camera camera, Vector3 centre, float halfHeight)
        {
            camera.orthographicSize = halfHeight;
            camera.transform.position = centre - camera.transform.forward * 120f;
        }

        private static void Snap(Camera camera, RenderTexture rt, Texture2D sheet, int col, int row)
        {
            camera.Render();
            RenderTexture.active = rt;
            var frame = new Texture2D(CellW, CellH, TextureFormat.RGB24, false);
            frame.ReadPixels(new Rect(0, 0, CellW, CellH), 0, 0);
            frame.Apply();
            sheet.SetPixels(col * CellW, row * CellH, CellW, CellH, frame.GetPixels());
            Object.DestroyImmediate(frame);
            RenderTexture.active = null;
        }

        private static void Stage(MaterialLibrary materials, Transform root)
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.transform.SetParent(root, false);
            ground.transform.localScale = new Vector3(30f, 1f, 30f);
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

        private static Camera MakeCamera(Transform root)
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
            var args = System.Environment.GetCommandLineArgs();
            for (var i = 0; i < args.Length - 1; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }
    }
}
