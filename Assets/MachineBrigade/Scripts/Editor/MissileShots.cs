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
    /// Missiles and rockets in flight, from the game's camera angle (DECISIONS 12B): each launcher
    /// fires its first missile or rocket at a target (an aircraft for anti-air weapons), frozen at
    /// launch beside its launcher (to judge its size), then at three moments of its flight closed
    /// on the round, its flame and its smoke trail. Several sheets of up to six launchers
    /// (missiles_N.png). Play-test 13 follow-up (lane A): a fifth column seen side-on at 0.8 of the flight, framed on the
    /// whole path (launcher to target), to judge its flight profile (Direct flat, Loft climb-and-dive, Ballistic high arc);
    /// missiles.txt gives each round's profile, its drawn peak against the Sim's (ArcShare x ground distance) and when and
    /// where it lands against the Sim's flight time and aim point. Batch mode (with graphics):
    /// -executeMethod MachineBrigade.Editor.MissileShots.Run -mbShotsOut &lt;folder&gt; [-mbShotsIds a+b].
    /// </summary>
    public static class MissileShots
    {
        private const string ProfilePath = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset";
        private const int CellW = 400, CellH = 300, RowsPerSheet = 6;

        /// <summary>Moments after launch: the first in seconds, the rest as shares of the flight.</summary>
        private static readonly float[] Moments = { 0.2f, 0.25f, 0.5f, 0.8f };

        private static readonly (string id, bool air)[] Launchers =
        {
            ("sam_launcher", true), ("aa_vehicle", true), ("heavy_aa", true), ("missile_battery", true), ("long_sam", true), ("aa_turret.sam", true),
            ("ifv", false), ("atgm_tower", false), ("titan_tank", false), ("mg_bunker", false),
            ("attack_helicopter", false), ("elite_attack_helicopter", false), ("scout_heli", false), ("strike_drone", false),
            ("attack_jet", false), ("fighter_jet", true), ("recon_drone", false), ("stealth_bomber", false), ("heavy_bomber", false),
            ("mlrs", false), ("thermobaric_launcher", false), ("heavy_rocket_artillery", false), ("ballistic_launcher", false), ("rocket_turret", false), ("rocket_technical", false),
            // Play-test 13 follow-up (lane A): the lofted box launchers (NSM, Typhon) and the PAC-3 tower.
            ("ground_cruise_missile_vehicle", false), ("missile_battery.pac3", true),
        };

        /// <summary>The side-on column showing the whole flight path (after the moments' columns).</summary>
        private const int PathColumn = 4;

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
        }

        [MenuItem("Machine Brigade/Render Missile Shots")]
        public static void Run()
        {
            var output = Argument("-mbShotsOut") ?? Path.Combine(Application.dataPath, "../Builds/missile_shots");
            Directory.CreateDirectory(output);
            var only = Argument("-mbShotsIds");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20260929);
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var catalog = GameContent.LoadCatalog();
            var root = new GameObject("Missile Shots").transform;
            Stage(materials, root);
            var camera = MakeCamera(root);
            var rt = new RenderTexture(CellW, CellH, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            camera.targetTexture = rt;
            camera.Render();
            var log = new System.Text.StringBuilder();

            var rows = new List<(string id, bool air)>();
            foreach (var l in Launchers)
                if (catalog.Vehicles.ContainsKey(l.id) && (string.IsNullOrEmpty(only) || System.Array.IndexOf(only.Split('+'), l.id) >= 0)) rows.Add(l);
            for (int first = 0, n = 1; first < rows.Count; first += RowsPerSheet, n++)
            {
                var count = Mathf.Min(RowsPerSheet, rows.Count - first);
                var sheet = new Texture2D(CellW * (PathColumn + 1), CellH * count, TextureFormat.RGB24, false);
                for (var r = 0; r < count; r++)
                {
                    var (id, air) = rows[first + r];
                    var kit = Build(catalog, models, meshes, materials, root, id, air);
                    var shot = FireFirst(kit, catalog, camera);
                    if (!shot.HasValue)
                    {
                        log.AppendLine($"{id}: no missile or rocket");
                        Object.DestroyImmediate(kit.Holder.gameObject);
                        continue;
                    }
                    var e = shot.Value;
                    var duration = Mathf.Max(0.05f, e.Value);
                    var time = 0f;
                    const float step = 1f / 60f;
                    var line = $"{id}: {e.DefId} {duration:0.00} s";
                    // Play-test 13 follow-up (lane A): the drawn path against the Sim's (its peak over the line, where and when it lands).
                    var aim = WeaponEffects.AimPoint(e, kit.Views);
                    var start = Round(kit, out _, out _);
                    var top = 0f;
                    var last = start;
                    var landed = -1f;
                    void Advance(float until)
                    {
                        while (time + 1e-4f < until)
                        {
                            time += step;
                            kit.Tracers.Tick(time, kit.Emitters);
                            kit.Projectiles.Tick(time, kit.Emitters);
                            kit.Muzzle.Tick(time);
                            kit.Emitters.Tick(time, step);
                            SimulateParticles(kit.Holder, step);
                            if (!Flying(kit))
                            {
                                if (landed < 0f) landed = time;
                                continue;
                            }
                            var p = Round(kit, out _, out _);
                            var run = WeaponEffects.Ground(start, aim);
                            var share = run > 1e-3f ? Mathf.Clamp01(WeaponEffects.Ground(start, p) / run) : 0f;
                            top = Mathf.Max(top, p.y - Mathf.Lerp(start.y, aim.y, share));
                            last = p;
                        }
                    }
                    for (var m = 0; m < Moments.Length; m++)
                    {
                        var at = m == 0 ? Mathf.Min(Moments[0], duration * 0.3f) : Moments[m] * duration;
                        Advance(at);
                        var round = Round(kit, out var forward, out var length);
                        if (m == 0)
                        {
                            // Beside its launcher, to judge its size.
                            var view = kit.Views.TryGet(kit.Shooter.Id, out var v) ? v : null;
                            var centre = view != null ? Vector3.Lerp(view.Position + Vector3.up * 1.2f, round, 0.5f) : round;
                            Frame(camera, centre, view != null && view.Flying ? 8f : 6f);
                            line += $", drawn {length:0.00} m";
                        }
                        else Frame(camera, round - forward * 3f, 6f);
                        Snap(camera, rt, sheet, m, count - 1 - r);
                        if (m == 1)
                        {
                            line += " | particles";
                            foreach (var ps in kit.Holder.GetComponentsInChildren<ParticleSystem>())
                                if (ps.name.StartsWith("Motor")) line += $" {ps.name.Substring(6)} {ps.particleCount}";
                        }
                        if (m == Moments.Length - 1) SideOn(camera, rt, sheet, count - 1 - r, start, aim, top);
                    }
                    // On to the end of the flight: it must land on the Sim's aim point when the Sim scores it.
                    Advance(duration + 0.5f);
                    var weapon = catalog.Weapons.TryGetValue(e.DefId, out var fired) ? fired : null;
                    var simPeak = weapon != null ? weapon.ArcShare * WeaponEffects.Ground(start, aim) : 0f;
                    line += $" | {weapon?.Flight} peak {top:0.0} m (Sim {simPeak:0.0} m), lands {landed:0.00} s (Sim {duration:0.00} s)"
                            + $" {Vector3.Distance(last, aim):0.0} m from its aim point";
                    log.AppendLine(line);
                    Object.DestroyImmediate(kit.Holder.gameObject);
                }
                sheet.Apply();
                File.WriteAllBytes(Path.Combine(output, $"missiles_{n}.png"), sheet.EncodeToPNG());
                Object.DestroyImmediate(sheet);
            }
            File.WriteAllText(Path.Combine(output, "missiles.txt"), log.ToString());
            Debug.Log("[MissileShots] wrote " + Path.GetFullPath(output) + "\n" + log);
            camera.targetTexture = null;
            rt.Release();
            models.Dispose();
            materials.Dispose();
        }

        private static Kit Build(Catalog catalog, ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials, Transform root, string id, bool air)
        {
            var kit = new Kit { Holder = new GameObject(id).transform };
            kit.Holder.SetParent(root, false);
            var map = new MapDefinition("shots", 260f,
                new[] { new TeamStart(0, new Vector2(0f, -100f)), new TeamStart(1, new Vector2(0f, 100f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());
            kit.World = new SimWorld(catalog, map, seed: 5);
            kit.Views = new ViewRegistry(models, meshes, materials, kit.Holder, 0);
            kit.Tracers = new TracerPool(meshes.Box, materials.Tracer, kit.Holder, 64);
            kit.Projectiles = new ProjectilePool(kit.Holder, 48);
            kit.Emitters = new Emitters(materials, kit.Holder);
            kit.Muzzle = new MuzzleFx(materials, kit.Holder);
            kit.Weapons = new WeaponEffects(catalog, models, kit.Tracers, kit.Projectiles, kit.Emitters, kit.Muzzle, (_, _) => { });
            var def = catalog.Vehicles[id];
            kit.Shooter = kit.World.SpawnVehicle(id, 0, Vector2.Zero, 0f);
            kit.Views.Add(kit.Shooter);
            var reach = Mathf.Clamp(def.Weapon.Range * 0.85f, def.Weapon.MinRange + 10f, 45f);
            // Off to the right of the camera's view, so the flight crosses the frame.
            var at = new Vector2(0.7f, 0.7f) * reach;
            var target = kit.World.SpawnVehicle(air ? "attack_helicopter" : "main_battle_tank", 1, at, 0f);
            kit.World.MakeDummy(target);
            kit.Views.Add(target);
            kit.World.Submit(new Command(CommandType.Attack, 0, new[] { kit.Shooter.Id }, default, target.Id));
            return kit;
        }

        /// <summary>Steps the battle until the shooter's first missile or rocket (other rounds are drawn too), starting it after the views are drawn.</summary>
        private static SimEvent? FireFirst(Kit kit, Catalog catalog, Camera camera)
        {
            for (var i = 0; i < 20 * 40; i++)
            {
                kit.World.Step(0.05f);
                kit.Views.SnapshotAll();
                kit.Views.Render(1f, camera.transform.rotation);
                foreach (var e in kit.World.Events)
                {
                    if (e.Kind != SimEventKind.WeaponFired || e.Entity != kit.Shooter.Id) continue;
                    if (e.DefId == null || !catalog.Weapons.TryGetValue(e.DefId, out var w)) continue;
                    if (w.Projectile is not (ProjectileKind.Missile or ProjectileKind.Rocket)) continue;
                    if (!kit.Views.TryGet(kit.Shooter.Id, out var view)) continue;
                    kit.Weapons.Fired(e, view, kit.Views, 0f);
                    kit.World.ClearEvents();
                    return e;
                }
                kit.World.ClearEvents();
            }
            return null;
        }

        /// <summary>The round in flight: its middle, its nose's direction and its drawn length.</summary>
        private static Vector3 Round(Kit kit, out Vector3 forward, out float length)
        {
            foreach (Transform t in kit.Holder.Find("Projectiles"))
            {
                if (!t.gameObject.activeSelf) continue;
                forward = t.forward;
                var mesh = t.GetComponent<MeshFilter>().sharedMesh;
                length = mesh != null ? mesh.bounds.size.z * t.localScale.z : 0f;
                return t.position;
            }
            forward = Vector3.forward;
            length = 0f;
            return Vector3.zero;
        }

        /// <summary>Whether a round is still in the air.</summary>
        private static bool Flying(Kit kit)
        {
            foreach (Transform t in kit.Holder.Find("Projectiles"))
                if (t.gameObject.activeSelf) return true;
            return false;
        }

        /// <summary>
        /// Play-test 13 follow-up (lane A): the whole flight seen side-on (a little from above), framed on the launcher, the
        /// target and the path's peak, so the smoke trail draws the profile; the game's camera angle is put back after.
        /// </summary>
        private static void SideOn(Camera camera, RenderTexture rt, Texture2D sheet, int row, Vector3 from, Vector3 to, float top)
        {
            var rotation = camera.transform.rotation;
            var size = camera.orthographicSize;
            var chord = new Vector3(to.x - from.x, 0f, to.z - from.z);
            var ahead = chord.sqrMagnitude > 1e-4f ? chord.normalized : Vector3.forward;
            var side = Vector3.Cross(Vector3.up, ahead);
            camera.transform.rotation = Quaternion.LookRotation(side * Mathf.Cos(10f * Mathf.Deg2Rad) - Vector3.up * Mathf.Sin(10f * Mathf.Deg2Rad));
            var centre = (from + to) * 0.5f + Vector3.up * (Mathf.Max(top, 1f) * 0.5f);
            var half = Mathf.Max((chord.magnitude * 0.5f + 4f) * CellH / (float)CellW, Mathf.Max(top, 1f) * 0.5f + 4f);
            Frame(camera, centre, half);
            Snap(camera, rt, sheet, PathColumn, row);
            camera.transform.rotation = rotation;
            camera.orthographicSize = size;
        }

        private static void SimulateParticles(Transform root, float dt)
        {
            foreach (var ps in root.GetComponentsInChildren<ParticleSystem>()) ps.Simulate(dt, false, false, false);
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
            ground.transform.localScale = new Vector3(40f, 1f, 40f);
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
