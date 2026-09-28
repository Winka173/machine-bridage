using System.Collections.Generic;
using System.Linq;
using System.Text;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using NUnit.Framework;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Muzzle flashes sit on the barrel's tip the round leaves from, face along the barrel and stay
    /// there as the hull drives and the turret turns; a flame stream starts on its nozzle (DECISIONS
    /// 12A). Every vehicle in the catalogue (elites, bosses, towers and aircraft too) fights a dummy
    /// twice, once turning onto it where it stands and once driving past it, drawn in the game's
    /// order (steps, the frame's update, particles, views, then shots and flashes), and every live
    /// flash particle is measured against the drawn muzzle on every frame. The same battles with
    /// the flashes left where they were lit (the old behaviour) give the before numbers.
    /// </summary>
    public class FlashTests
    {
        private const float Step = 0.05f;
        private const float Frame = 1f / 30f;

        /// <summary>How far a flash may sit from its barrel's drawn tip, in metres.</summary>
        private const float Tolerance = 0.03f;

        /// <summary>How far a forward flame tongue may point off its barrel (its own random jitter is under 5 degrees).</summary>
        private const float AxisTolerance = 6f;

        private sealed class Tally
        {
            public int Flashes, Particles, Streams;
            public float Lit, Riding, Axis, Aim, Nozzle, RodBehind;
            public string LitAt = "", RidingAt = "", AxisAt = "", NozzleAt = "", RodAt = "";

            public void Max(ref float field, ref string at, float value, string where)
            {
                if (value <= field) return;
                field = value;
                at = where;
            }
        }

        /// <summary>A stretched particle is drawn trailing back from its position (its tip), size x lengthScale + speed x velocityScale long.</summary>
        [Test]
        public void StretchedFlamesTrailBehindTheirParticle()
        {
            var materials = new MaterialLibrary();
            var root = new GameObject("Stretch Test").transform;
            var camera = new GameObject("Stretch Camera").AddComponent<Camera>();
            try
            {
                camera.transform.SetPositionAndRotation(new Vector3(0f, 30f, 0f), Quaternion.Euler(90f, 0f, 0f));
                var lengths = new List<(float expected, float back, float front)>();
                foreach (var (lengthScale, velocityScale, speed) in new[] { (4.2f, 0f, 1.5f), (2.2f, 0.05f, 40f) })
                {
                    var ps = PB.Create(root, "Stretch", materials.Fire, ParticleSystemRenderMode.Stretch);
                    var renderer = ps.GetComponent<ParticleSystemRenderer>();
                    renderer.lengthScale = lengthScale;
                    renderer.velocityScale = velocityScale;
                    var main = ps.main;
                    main.loop = true;
                    ps.Play();
                    ps.Emit(new ParticleSystem.EmitParams
                    {
                        position = Vector3.zero, velocity = Vector3.right * speed, startSize = 0.5f, startLifetime = 1f, applyShapeToPosition = false,
                    }, 1);
                    ps.Simulate(0f, false, false, false);
                    var mesh = new Mesh();
                    renderer.BakeMesh(mesh, camera, ParticleSystemBakeMeshOptions.BakeRotationAndScale | ParticleSystemBakeMeshOptions.BakePosition);
                    var xs = mesh.vertices.Select(v => v.x).ToArray();
                    Assert.Greater(xs.Length, 0, "the particle was baked");
                    var expected = 0.5f * lengthScale + speed * velocityScale;
                    Debug.Log($"STRETCH lengthScale {lengthScale} velocityScale {velocityScale} speed {speed}: x {xs.Min():0.000}..{xs.Max():0.000} (expected {-expected:0.000}..0)");
                    lengths.Add((expected, xs.Min(), xs.Max()));
                    Object.DestroyImmediate(mesh);
                    Object.DestroyImmediate(ps.gameObject);
                }
                foreach (var (expected, back, front) in lengths)
                {
                    Assert.AreEqual(-expected, back, 0.02f, "the back end, a length behind the particle");
                    Assert.AreEqual(0f, front, 0.02f, "the tip, on the particle");
                }
            }
            finally
            {
                Object.DestroyImmediate(camera.gameObject);
                Object.DestroyImmediate(root.gameObject);
                materials.Dispose();
            }
        }

        /// <summary>
        /// Fires on the ground burn a fifth shorter than they are lit for, napalm excepted; fires on a
        /// hull keep their time. Ground flames and firelight lie on the ground in depth (under the
        /// vehicles in them); a hull's flames do not.
        /// </summary>
        [Test]
        public void GroundFiresBurnAFifthShorterAndLieUnderVehicles()
        {
            var materials = new MaterialLibrary();
            var root = new GameObject("Fire Test").transform;
            try
            {
                var fires = new FireSpots(materials, root);
                var ground = new Vector3(0f, 0.05f, 0f);
                Assert.AreEqual(8f, fires.FlamesUntil(fires.Ignite(ground, 1f, 10f, 0f)), 1e-4f, "a ground fire");
                Assert.AreEqual(10f, fires.FlamesUntil(fires.Ignite(ground, 1f, 10f, 0f, napalm: true)), 1e-4f, "napalm");
                Assert.AreEqual(10f, fires.FlamesUntil(fires.Ignite(new Vector3(0f, 1.6f, 0f), 1f, 10f, 0f)), 1e-4f, "a fire up on a wreck");
                Assert.AreEqual(10f, fires.FlamesUntil(fires.Ignite(ground, 1f, 10f, 0f, root)), 1e-4f, "a fire riding a hull");
                var renderers = root.GetComponentsInChildren<ParticleSystemRenderer>();
                float Onto(string name) => renderers.Single(r => r.name == name).sharedMaterial.GetFloat("_OntoGround");
                Assert.AreEqual(1f, Onto("Ground Flames"), "ground flames lie on the ground");
                Assert.AreEqual(1f, Onto("Ground Fire Glow"), "and their firelight");
                Assert.AreEqual(0f, Onto("Flames"), "a hull's flames stand up in front of it");
                var emitters = new Emitters(materials, root);
                Assert.AreEqual(1f, root.GetComponentsInChildren<ParticleSystemRenderer>().Single(r => r.name == "Ground Flame Licks").sharedMaterial.GetFloat("_OntoGround"),
                    "a flame stream's fire on the ground too");
            }
            finally
            {
                Object.DestroyImmediate(root.gameObject);
                materials.Dispose();
            }
        }

        [Test]
        public void FlashesRideTheDrawnMuzzleOfEveryWeapon()
        {
            var catalog = GameContent.LoadCatalog();
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Flash Test").transform;
            try
            {
                var before = new Tally();
                var perVehicleBefore = new Dictionary<string, float>();
                MuzzleFx.RideMuzzles = false;
                WeaponEffects.AlongBarrel = false;
                Emitters.RideNozzles = false;
                foreach (var def in Fieldable(catalog)) perVehicleBefore[def.Id] = Fight(catalog, models, meshes, materials, root, def, before);

                MuzzleFx.RideMuzzles = true;
                WeaponEffects.AlongBarrel = true;
                Emitters.RideNozzles = true;
                var after = new Tally();
                var report = new StringBuilder();
                var silent = new List<string>();
                foreach (var def in Fieldable(catalog))
                {
                    var flashes = after.Flashes;
                    var worst = Fight(catalog, models, meshes, materials, root, def, after);
                    if (after.Flashes == flashes) silent.Add(def.Id);
                    report.Append($"{def.Id} {perVehicleBefore[def.Id]:0.00}->{worst:0.000}; ");
                }
                Debug.Log("FLASH OFFSETS (flash to drawn barrel tip, worst over its life, before -> after, m)\n" + report +
                    $"\nBEFORE {before.Flashes} flashes, {before.Particles} particle-frames: lit {before.Lit:0.000} m, riding {before.Riding:0.000} m ({before.RidingAt}), " +
                    $"tongue axis {before.Axis:0.0} deg ({before.AxisAt}), flash vs drawn barrel at lighting {before.Aim:0.0} deg; flame origin {before.Nozzle:0.00} m ({before.NozzleAt}), rod behind the nozzle {before.RodBehind:0.00} m ({before.RodAt})" +
                    $"\nAFTER {after.Flashes} flashes, {after.Particles} particle-frames: lit {after.Lit:0.000} m ({after.LitAt}), riding {after.Riding:0.000} m ({after.RidingAt}), " +
                    $"tongue axis {after.Axis:0.0} deg ({after.AxisAt}), flash vs drawn barrel at lighting {after.Aim:0.0} deg; flame origin {after.Nozzle:0.000} m ({after.NozzleAt}), rod behind the nozzle {after.RodBehind:0.000} m ({after.RodAt})" +
                    $"\nno flash: {string.Join(", ", silent)}");
                Assert.Greater(after.Flashes, 500, "the vehicles fired");
                Assert.Greater(after.Streams, 10, "the flamethrowers fired");
                Assert.Less(after.Lit, Tolerance, $"a flash lit off the round's start: {after.LitAt}");
                Assert.Less(after.Riding, Tolerance, $"a flash off its drawn barrel tip: {after.RidingAt}");
                Assert.Less(after.Axis, AxisTolerance, $"a flame tongue off its barrel: {after.AxisAt}");
                Assert.Less(after.Aim, 1f, "gun flashes are lit along the drawn barrel");
                Assert.Less(after.Nozzle, Tolerance, $"a flame stream off its nozzle: {after.NozzleAt}");
                Assert.Less(after.RodBehind, 0.05f, $"a flame streak starting behind its nozzle: {after.RodAt}");
            }
            finally
            {
                MuzzleFx.RideMuzzles = true;
                WeaponEffects.AlongBarrel = true;
                Emitters.RideNozzles = true;
                WeaponEffects.Launched = null;
                MuzzleFx.Flashed = null;
                Object.DestroyImmediate(root.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }

        /// <summary>Every vehicle with a weapon that shoots (not a blade).</summary>
        private static IEnumerable<VehicleDef> Fieldable(Catalog catalog) =>
            catalog.Vehicles.Values.Where(d => d.Mounts.Count > 0 && d.Mounts.Any(m => !m.Weapon.Melee)).OrderBy(d => d.Id);

        /// <summary>
        /// Two short fights for one vehicle: turning onto a dummy off to one side, then driving past one.
        /// Returns the worst distance of a live flash from its drawn muzzle.
        /// </summary>
        private static float Fight(Catalog catalog, ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials, Transform root,
            VehicleDef def, Tally tally)
        {
            var worst = 0f;
            for (var scenario = 0; scenario < 2; scenario++)
            {
                if (scenario == 1 && (def.Static || def.Speed <= 0f)) break;
                var holder = new GameObject(def.Id).transform;
                holder.SetParent(root, false);
                var map = new MapDefinition("flash", 300f,
                    new[] { new TeamStart(0, new Vector2(0f, -120f)), new TeamStart(1, new Vector2(0f, 120f)) },
                    new List<PropPlacement>(), new List<UnitPlacement>());
                var world = new SimWorld(catalog, map, seed: 7 + scenario);
                var views = new ViewRegistry(models, meshes, materials, holder, 0);
                var tracers = new TracerPool(meshes.Box, materials.Tracer, holder, 64);
                var projectiles = new ProjectilePool(holder, 32);
                var emitters = new Emitters(materials, holder) { LateFeed = true };
                var muzzle = new MuzzleFx(materials, holder);
                var weapons = new WeaponEffects(catalog, models, tracers, projectiles, emitters, muzzle, (_, _) => { });
                var systems = holder.GetComponentsInChildren<ParticleSystem>();

                var heading = (scenario == 0 ? 20f : 135f) * Mathf.Deg2Rad;
                var shooter = world.SpawnVehicle(def.Id, 0, Vector2.Zero, heading);
                views.Add(shooter);
                var air = !def.Weapon.CanTarget(false);
                var range = Mathf.Max(def.Weapon.MinRange + 8f, Mathf.Min(def.Weapon.Range * 0.6f, 40f));
                Vector2 at;
                if (scenario == 0)
                {
                    var bearing = heading + 70f * Mathf.Deg2Rad;
                    at = new Vector2(Mathf.Sin(bearing), Mathf.Cos(bearing)) * range;
                }
                else
                {
                    // Abeam of its path, a little ahead: it fires on the move (or stops to).
                    var ahead = new Vector2(Mathf.Sin(heading), Mathf.Cos(heading));
                    var side = new Vector2(ahead.Y, -ahead.X);
                    at = ahead * 12f + side * Mathf.Min(range, 18f);
                }
                var target = world.SpawnVehicle(air ? "attack_helicopter" : "main_battle_tank", 1, at, heading);
                world.MakeDummy(target);
                views.Add(target);
                if (scenario == 0) world.Submit(new Command(CommandType.Attack, 0, new[] { shooter.Id }, default, target.Id));
                else
                    world.Submit(new Command(CommandType.Move, 0, new[] { shooter.Id },
                        new Vector2(Mathf.Sin(heading), Mathf.Cos(heading)) * 70f));

                var shots = new List<SimEvent>();
                var lit = new List<(VehicleView view, int mount, Vector3 from)>();
                var flashed = new List<(Vector3 point, Vector3 dir)>();
                WeaponEffects.Launched = (view, mount, from) => lit.Add((view, mount, from));
                MuzzleFx.Flashed = (point, dir) => flashed.Add((point, dir));
                var measured = new List<MuzzleFx.Measured>();
                var nozzles = new List<(Vector3 from, Vector3 nozzle)>();
                var rods = new List<(Vector3 tail, Vector3 axis, float age)>();
                var accumulator = 0f;
                var now = 1f;
                var fired = 0;
                var quietFrames = 0;
                for (var frame = 0; frame < 30 * 7 && quietFrames < 12; frame++)
                {
                    accumulator += Frame;
                    while (accumulator >= Step)
                    {
                        accumulator -= Step;
                        world.Step(Step);
                        views.SnapshotAll();
                        foreach (var e in world.Events)
                            if (e.Kind == SimEventKind.WeaponFired && e.Entity == shooter.Id) shots.Add(e);
                        world.ClearEvents();
                    }
                    now += Frame;
                    // The frame's update (later rounds of a burst), the particles' own step, the views drawn.
                    muzzle.Tick(now);
                    emitters.Tick(now, Frame);
                    foreach (var ps in systems) ps.Simulate(Frame, false, false, false);
                    views.Render(accumulator / Step, Quaternion.Euler(52f, -45f, 0f));
                    // Then as EffectsDirector.LaunchShots: flashes and streams follow, this frame's shots leave.
                    muzzle.Follow(now);
                    emitters.FeedFlames(now, Frame);
                    if (!views.TryGet(shooter.Id, out var drawn))
                    {
                        shots.Clear();
                        break;
                    }
                    foreach (var e in shots) weapons.Fired(e, drawn, views, now);
                    shots.Clear();

                    // Each flash as it is lit: on the round's start, facing along the drawn barrel.
                    for (var i = 0; i < Mathf.Min(lit.Count, flashed.Count); i++)
                    {
                        var (view, mount, from) = lit[i];
                        var (point, dir) = flashed[i];
                        tally.Flashes++;
                        fired++;
                        tally.Max(ref tally.Lit, ref tally.LitAt, Vector3.Distance(point, from), $"{def.Id} mount {mount}");
                        var weapon = def.Mounts[mount].Weapon;
                        var gun = weapon.Projectile is ProjectileKind.Bullet or ProjectileKind.Flame || (weapon.Projectile == ProjectileKind.Shell && !weapon.Indirect && !weapon.Id.Contains("howitzer"));
                        if (gun)
                        {
                            var off = Vector3.Angle(dir, view.DrawnBarrelOf(mount));
                            var ignored = "";
                            tally.Max(ref tally.Aim, ref ignored, off, "");
                        }
                    }
                    lit.Clear();
                    flashed.Clear();

                    // Every live flash particle against its muzzle as drawn now.
                    muzzle.Measure(measured);
                    if (measured.Count == 0) quietFrames = fired > 12 ? quietFrames + 1 : 0;
                    foreach (var m in measured)
                    {
                        tally.Particles++;
                        var off = Vector3.Distance(m.Flash, m.Muzzle);
                        worst = Mathf.Max(worst, off);
                        tally.Max(ref tally.Riding, ref tally.RidingAt, off, $"{def.Id} s{scenario} {(m.Tongue ? "tongue" : "core")}");
                        if (m.Forward) tally.Max(ref tally.Axis, ref tally.AxisAt, Vector3.Angle(m.Axis, m.Barrel), $"{def.Id} s{scenario}");
                    }

                    // Flame streams: fed from the nozzle as drawn, their newest streaks starting on it.
                    emitters.Nozzles(nozzles);
                    if (nozzles.Count > 0)
                    {
                        emitters.RodTails(rods);
                        foreach (var (from, nozzle) in nozzles)
                        {
                            tally.Streams++;
                            var off = Vector3.Distance(from, nozzle);
                            worst = Mathf.Max(worst, off);
                            tally.Max(ref tally.Nozzle, ref tally.NozzleAt, off, $"{def.Id} s{scenario}");
                        }
                        // Each streak born this frame against the nozzle it left (the nearest).
                        foreach (var (tail, axis, age) in rods)
                        {
                            if (age > 0.001f) continue;
                            var nearest = nozzles.OrderBy(n => (n.nozzle - tail).sqrMagnitude).First().nozzle;
                            if ((tail - nearest).sqrMagnitude > 16f) continue;
                            tally.Max(ref tally.RodBehind, ref tally.RodAt, -Vector3.Dot(tail - nearest, axis), $"{def.Id} s{scenario}");
                        }
                    }
                }
                WeaponEffects.Launched = null;
                MuzzleFx.Flashed = null;
                // (Their Dispose calls Destroy, which edit mode refuses: the holder goes whole.)
                Object.DestroyImmediate(holder.gameObject);
            }
            return worst;
        }
    }
}
