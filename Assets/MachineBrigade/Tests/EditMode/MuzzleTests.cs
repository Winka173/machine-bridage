using System.Collections.Generic;
using System.Linq;
using System.Text;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using NUnit.Framework;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Rounds leave from the barrel as it is drawn: a battle is stepped and drawn in the match's
    /// order (steps, events, effects, views) with the vehicle facing each way and its turret turned
    /// onto a target off to one side, and every round's start is compared with where the tip of
    /// the barrel it left from is drawn in that same frame.
    /// </summary>
    public class MuzzleTests
    {
        private const float Step = 0.05f;
        private const float Frame = 1f / 30f;

        /// <summary>How far a round may start from its barrel's drawn tip, in metres.</summary>
        private const float Tolerance = 0.05f;

        private static readonly string[] Shooters =
        {
            "main_battle_tank", "ifv", "twin_tank", "mortar_carrier", "artillery", "mlrs", "sam_launcher", "fpv_carrier",
            "attack_helicopter", "attack_jet", "gun_turret",
        };

        /// <summary>A lobbed round leaves along its raised barrel even when its aim point is scattered off the barrel's line, and lands on it.</summary>
        [Test]
        public void ALobbedRoundLeavesAlongItsBarrel()
        {
            var from = new Vector3(0f, 2.5f, 0f);
            var to = new Vector3(8f, 0.4f, 40f);
            // Laid 60 degrees up, straight north: the round lands 11 degrees east of that line.
            var barrel = Quaternion.Euler(-60f, 0f, 0f) * Vector3.forward;
            var control = WeaponEffects.Bend(from, to, barrel);
            Assert.IsTrue(control.HasValue, "a raised barrel bends the path");
            var start = (control.Value - from).normalized;
            Debug.Log($"BEND start {Vector3.Angle(start, barrel):0.00} deg off the barrel, peak {control.Value.y * 0.5f + (from.y + to.y) * 0.25f:0.0} m");
            Assert.Less(Vector3.Angle(start, barrel), 0.5f, "the round leaves down the barrel");
            Assert.IsNull(WeaponEffects.Bend(from, to, Vector3.forward), "a level barrel keeps the plain arc");
        }

        /// <summary>Drones are drawn twice their size; missiles and rockets 10-20 % bigger by type.</summary>
        [Test]
        public void MunitionsAreDrawnBiggerByType()
        {
            var catalog = GameContent.LoadCatalog();
            float Size(string weapon, string model, bool air = false) =>
                WeaponEffects.SizeOf(catalog.Weapons[weapon], catalog.Weapons[weapon].Projectile, model, air);
            Assert.AreEqual(2f, Size("fpv_swarm", "fpv_drone"), 1e-4f, "FPV drones");
            Assert.AreEqual(2f, Size("lancet", "lancet"), 1e-4f, "Lancets");
            Assert.AreEqual(2f, Size("shahed", "shahed"), 1e-4f, "Shaheds");
            Assert.AreEqual(2f, Size("mothership_drones", "fpv_drone"), 1e-4f, "the mothership's drones");
            Assert.AreEqual(1.1f, Size("atgm", "atgm_tow"), 1e-4f, "a ground ATGM");
            Assert.AreEqual(1.1f, Size("stinger_atas", "stinger"), 1e-4f, "MANPADS");
            Assert.AreEqual(1.2f, Size("sam", "shorad_dart"), 1e-4f, "a SAM");
            Assert.AreEqual(1.2f, Size("heli_atgm", "hellfire", air: true), 1e-4f, "air-to-ground");
            Assert.AreEqual(1.2f, Size("air_cruise_missile", "cruise_missile", air: true), 1e-4f, "a cruise missile");
            Assert.AreEqual(1.15f, Size("grad_rockets", "grad"), 1e-4f, "rockets in between");
            Assert.AreEqual(1f, Size("howitzer", "shell_155"), 1e-4f, "gun shells as they were");
        }

        /// <summary>A tracer's streak leaves from the barrel's tip on its first frame and ends on the target as it lands.</summary>
        [Test]
        public void AStreakStartsAtTheMuzzleAndEndsOnTheTarget()
        {
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var root = new GameObject("Tracer Test").transform;
            try
            {
                var pool = new TracerPool(meshes.Box, materials.Tracer, root, 4);
                var emitters = new Emitters(materials, root);
                var from = new Vector3(1f, 2f, 3f);
                var to = from + new Vector3(30f, -1.6f, 12f);
                pool.Launch(from, to, 0.3f, 0f, 0.2f, 3.2f, 0f);
                var (back, front) = pool.Streaks().Single();
                Debug.Log($"TRACER first frame: back {Vector3.Distance(back, from):0.000} m from the muzzle, {Vector3.Distance(back, front):0.00} m long");
                Assert.Less(Vector3.Distance(back, from), 0.01f, "first frame: the streak leaves the barrel's tip");
                Assert.Greater(Vector3.Dot(front - back, to - from), 0f, "and reaches out towards the target");
                pool.Tick(0.2999f, emitters);
                (back, front) = pool.Streaks().Single();
                Assert.Less(Vector3.Distance(front, to), 0.05f, "it ends on the target as it lands");
                // A laser's beam stays one bar along the whole line.
                pool.Beam(from, to, 0.1f, 0.1f, 1f);
                Assert.IsTrue(pool.Streaks().Any(s => Vector3.Distance(s.back, from) < 0.01f && Vector3.Distance(s.front, to) < 0.01f), "the beam spans the line");
            }
            finally
            {
                Object.DestroyImmediate(root.gameObject);
                materials.Dispose();
            }
        }

        /// <summary>
        /// Before the shots waited for the vehicles to be drawn, rounds started 0.10-0.24 m off the
        /// barrel of a ground vehicle turning onto its target, 2.4 m off a helicopter's and 4.7 m
        /// off a jet's (30 fps).
        /// </summary>
        [Test]
        public void RoundsStartAtTheDrawnBarrelTipAtEveryHeading()
        {
            var catalog = GameContent.LoadCatalog();
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Muzzle Test").transform;
            var camera = new GameObject("Muzzle Camera").AddComponent<Camera>();
            var report = new StringBuilder();
            var worst = 0f;
            var worstAt = "";
            var shots = 0;
            var launched = new List<(VehicleView view, Vector3 from, Transform node, Vector3 local)>();
            WeaponEffects.Launched = (view, mount, from) => launched.Add((view, from, view.LastMuzzleNode, view.LastMuzzleLocal));
            try
            {
                var rts = new RtsCamera(camera, 120f, Vector3.zero, 60f);
                camera.orthographic = true;
                camera.orthographicSize = 120f;
                camera.transform.SetPositionAndRotation(new Vector3(0f, 200f, 0f), Quaternion.Euler(90f, 0f, 0f));
                camera.farClipPlane = 500f;
                foreach (var id in Shooters)
                {
                    var def = catalog.Vehicles[id];
                    var line = new StringBuilder($"{id}:");
                    var mostOfVehicle = 0f;
                    for (var heading = 0; heading < 360; heading += 90)
                    {
                        var holder = new GameObject(id).transform;
                        holder.SetParent(root, false);
                        var map = new MapDefinition("muzzle", 260f,
                            new[] { new TeamStart(0, new Vector2(0f, -100f)), new TeamStart(1, new Vector2(0f, 100f)) },
                            new List<PropPlacement>(), new List<UnitPlacement>());
                        var world = new SimWorld(catalog, map, seed: 5);
                        var views = new ViewRegistry(models, meshes, materials, holder, 0);
                        var effects = new EffectsDirector(catalog, materials, meshes, models, rts, holder, EffectBudget.Eco);
                        var h = heading * Mathf.Deg2Rad;
                        var shooter = world.SpawnVehicle(id, 0, Vector2.Zero, h);
                        views.Add(shooter);
                        // A target off to one side, so the turret (or the hull) has to swing onto it.
                        var reach = Mathf.Max(def.Weapon.MinRange + 8f, Mathf.Min(def.Weapon.Range * 0.6f, 40f));
                        var bearing = h + 70f * Mathf.Deg2Rad;
                        var air = !def.Weapon.CanTarget(false);
                        var target = world.SpawnVehicle(air ? "attack_helicopter" : "main_battle_tank", 1,
                            new Vector2(Mathf.Sin(bearing), Mathf.Cos(bearing)) * reach, h);
                        world.MakeDummy(target);
                        views.Add(target);
                        world.Submit(new Command(CommandType.Attack, 0, new[] { shooter.Id }, default, target.Id));
                        launched.Clear();
                        var accumulator = 0f;
                        var most = 0f;
                        var count = 0;
                        for (var frame = 0; frame < 30 * 12 && count < 12; frame++)
                        {
                            accumulator += Frame;
                            while (accumulator >= Step)
                            {
                                accumulator -= Step;
                                world.Step(Step);
                                views.SnapshotAll();
                                effects.Consume(world.Events, views, null);
                                world.ClearEvents();
                            }
                            effects.Tick(views);
                            views.Render(accumulator / Step, camera.transform.rotation);
                            effects.LaunchShots(views);
                            foreach (var (view, from, node, local) in launched)
                            {
                                if (!views.TryGet(shooter.Id, out var drawn) || view != drawn || node == null) continue;
                                var off = Vector3.Distance(from, node.TransformPoint(local));
                                most = Mathf.Max(most, off);
                                count++;
                                if (off > worst)
                                {
                                    worst = off;
                                    worstAt = $"{id} heading {heading}";
                                }
                            }
                            launched.Clear();
                        }
                        shots += count;
                        mostOfVehicle = Mathf.Max(mostOfVehicle, most);
                        line.Append($" h{heading}={most:0.000}m/{count}");
                        // (Their Dispose calls Destroy, which edit mode refuses: the holder goes whole.)
                        Object.DestroyImmediate(holder.gameObject);
                    }
                    report.AppendLine(line.Append($" max={mostOfVehicle:0.000}").ToString());
                }
                Debug.Log($"MUZZLE OFFSETS (round start to drawn barrel tip, {shots} rounds)\n{report}");
                Assert.Greater(shots, 40, "the shooters fired");
                Assert.Less(worst, Tolerance, $"worst {worst:0.000} m at {worstAt}\n{report}");
            }
            finally
            {
                WeaponEffects.Launched = null;
                Object.DestroyImmediate(camera.gameObject);
                Object.DestroyImmediate(root.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }
    }
}
