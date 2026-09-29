using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using NUnit.Framework;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Missiles and rockets after test feedback 2 (DECISIONS 12B): the boost-then-cruise flight
    /// arrives on the simulation's time, every missile and rocket burns a plume sized by type,
    /// the slower speeds keep every flight under its weapon's cooldown, and the drawn sizes fit
    /// their launchers.
    /// </summary>
    public class MissileFlightTests
    {
        [Test]
        public void ABoostedFlightLeavesSlowlyCruisesAndArrivesOnTime()
        {
            foreach (var boost in new[] { 0.2f, 0.3f, 0.55f, 0.6f, 1f })
            {
                Assert.AreEqual(0f, ProjectilePool.Progress(boost, 0f), 1e-5f, "starts on the rail");
                Assert.AreEqual(1f, ProjectilePool.Progress(boost, 1f), 1e-4f, $"boost {boost}: arrives when the simulation lands it");
                var last = 0f;
                for (var t = 0.01f; t <= 1f; t += 0.01f)
                {
                    var p = ProjectilePool.Progress(boost, t);
                    Assert.Greater(p, last, "always moving forward");
                    last = p;
                }
                Assert.AreEqual(ProjectilePool.RailSpeed, ProjectilePool.SpeedAt(boost, 0f), 1e-5f, "slow off the rail");
                Assert.AreEqual(1f, ProjectilePool.SpeedAt(boost, boost * ProjectilePool.BoostShare + 0.01f), 1e-5f, "then cruising");
                // Cruise is a steady speed: equal steps cover equal distances after the boost.
                var tb = boost * ProjectilePool.BoostShare;
                var a = ProjectilePool.Progress(boost, tb + 0.1f) - ProjectilePool.Progress(boost, tb + 0.05f);
                var b = ProjectilePool.Progress(boost, 0.95f) - ProjectilePool.Progress(boost, 0.9f);
                Assert.AreEqual(a, b, 1e-4f, "steady cruise");
            }
            Assert.AreEqual(0.37f, ProjectilePool.Progress(0f, 0.37f), 1e-6f, "no boost: one speed");
        }

        [Test]
        public void EveryMissileAndRocketBurnsAPlumeByType()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var w in catalog.Weapons.Values)
            {
                if (w.Projectile is not (ProjectileKind.Missile or ProjectileKind.Rocket)) continue;
                var plume = Plume.For(w, w.Projectile, w.ProjectileModel, false);
                Assert.IsTrue(plume.Burns, w.Id + " burns a flame");
                Assert.Greater(plume.Smoke, 0f, w.Id + " leaves smoke");
                Assert.Greater(plume.Burn, 0.5f, w.Id + " burns most of its flight");
            }
            float Length(string id, bool air = false) =>
                Plume.For(catalog.Weapons[id], catalog.Weapons[id].Projectile, catalog.Weapons[id].ProjectileModel, air).Length;
            // In the munition's own lengths (a SAM is twice an ATGM's length, so its flame is four times as long).
            Assert.GreaterOrEqual(Length("sam"), Length("atgm") * 2f, "a SAM's plume is long, an ATGM's short");
            Assert.Greater(Length("sam"), Length("heli_atgm", true), "air-to-ground missiles in between");
            // Play-test 5 (DECISIONS 20V): the heavy launchers' flames cut to 60 % of their type's, still in munition lengths.
            Assert.AreEqual(Length("sam") * Plume.ShortFlame, Length("sam_long"), 1e-4f, "the SAM launcher's Buk");
            foreach (var id in new[] { "buk_launcher", "thermobaric_rockets", "rockets_300mm", "ballistic_missile", "sam_48n6", "patriot", "sam_pac3" })
                Assert.IsTrue(Plume.Short(catalog.Weapons[id]), id + " has the short flame");
            Assert.IsFalse(Plume.Short(catalog.Weapons["grad_rockets"]), "other rockets keep theirs");
            Assert.IsFalse(Plume.For(catalog.Weapons["fpv_swarm"], ProjectileKind.Drone, "fpv_drone", false).Burns, "drones fly on propellers");
        }

        /// <summary>The speeds after DECISIONS 12B (ground SAMs 10 % slower again in 13C, with flare-resistant seekers; play-test 4, 19R: none faster than the attack helicopter's Hellfire), and every flight at full range still shorter than its weapon's cooldown.</summary>
        [Test]
        public void MissilesFlySlowerAndLandBeforeTheirCooldown()
        {
            var catalog = GameContent.LoadCatalog();
            var speeds = new Dictionary<string, float>
            {
                { "atgm", 19f }, { "kornet_twin", 20f }, { "sam", 24f }, { "sam_long", 24f }, { "sam_battery", 24f }, { "sam_48n6", 24f },
                { "heli_atgm", 21f }, { "hellfire_volley", 21f }, { "drone_missile", 21f }, { "vikhr", 24f }, { "maverick", 23f },
                { "air_to_air", 24f }, { "wvr_aam", 24f }, { "stinger_atas", 24f }, { "hellfire_standoff", 24f }, { "air_cruise_missile", 17f },
                { "heli_rockets", 48f }, { "s8_pods", 48f },
            };
            foreach (var (id, speed) in speeds)
                Assert.AreEqual(speed, catalog.Weapons[id].ProjectileSpeed, 1e-3f, id);
            foreach (var w in catalog.Weapons.Values)
                if (w.Projectile == ProjectileKind.Missile || w.Family == "ballistic")
                    Assert.LessOrEqual(w.ProjectileSpeed, catalog.Weapons["hellfire_standoff"].ProjectileSpeed + 1e-3f, w.Id + ": no faster than the attack helicopter's Hellfire");
            var longest = "";
            var share = 0f;
            foreach (var w in catalog.Weapons.Values)
            {
                if (w.Projectile is not (ProjectileKind.Missile or ProjectileKind.Rocket)) continue;
                var flight = w.Range / w.ProjectileSpeed;
                Assert.Less(flight, w.Cooldown, $"{w.Id}: {flight:0.00} s of flight at full range against a {w.Cooldown} s cooldown");
                if (flight / w.Cooldown > share)
                {
                    share = flight / w.Cooldown;
                    longest = w.Id;
                }
            }
            Debug.Log($"MISSILE FLIGHT longest against its cooldown: {longest}, {share:P0}");
        }

        /// <summary>
        /// The motor's flame stays on the drawn tail frame after frame, in the game's order at 30 and
        /// 60 fps (the effects' update, then Unity's particle update, then the draw): a fast direct
        /// rocket, the thermobaric launcher's and the MLRS's rockets on their lobbed paths, a SAM and an ATGM. The
        /// visible front of the newest flame quad (its particle, less the end the fire shader leaves
        /// unfilled) is measured against the model's tail on every frame of the flight. A frame
        /// that jumps (the frozen-moment tools' old way, or a hitch) puts the flame a frame's travel
        /// behind: that is the gap sheets showed, measured here too (DECISIONS 13E).
        /// </summary>
        [Test]
        public void PlumesStayOnTheirTailsFrameByFrame()
        {
            var catalog = GameContent.LoadCatalog();
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Plume Frame Test").transform;
            try
            {
                var cases = new[]
                {
                    ("heli_rockets", "hydra", ProjectileKind.Rocket, 36f),
                    ("thermobaric_rockets", "tos_rocket", ProjectileKind.Rocket, 60f),
                    ("mlrs_rockets", "gmlrs", ProjectileKind.Rocket, 70f),
                    ("sam_long", "buk", ProjectileKind.Missile, 55f),
                    ("atgm", "atgm_tow", ProjectileKind.Missile, 34f),
                };
                var report = new System.Text.StringBuilder();
                var worst = 0f;
                var worstAt = "";
                foreach (var fps in new[] { 30f, 60f })
                    foreach (var (id, model, kind, distance) in cases)
                    {
                        var (gap, side, frames) = Fly(catalog, models, materials, root, id, model, kind, distance, 1f / fps, jump: false);
                        report.Append($"{id} {fps} fps: flame front {gap:+0.000;-0.000} m from the tail (worst), {side:0.000} m off its line, {frames} frames; ");
                        if (Mathf.Abs(gap) > worst)
                        {
                            worst = Mathf.Abs(gap);
                            worstAt = $"{id} at {fps} fps";
                        }
                        Assert.Less(side, 0.05f, $"{id} at {fps} fps: the flame beside its missile");
                    }
                foreach (var (id, model, kind, distance) in cases)
                {
                    var (gap, _, _) = Fly(catalog, models, materials, root, id, model, kind, distance, 1f / 30f, jump: true);
                    report.Append($"{id} after a jump to mid-flight: {gap:+0.00;-0.00} m; ");
                }
                Debug.Log("PLUME ON THE TAIL " + report);
                Assert.Less(worst, 0.06f, $"the flame's front off the drawn tail: {worstAt}");
            }
            finally
            {
                Object.DestroyImmediate(root.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }

        /// <summary>
        /// One flight drawn frame by frame: the worst distance along the missile from its drawn tail to
        /// the visible front of the flame born that frame (+ ahead onto the body, - a gap behind it) and
        /// the worst distance of that front off the missile's line.
        /// </summary>
        private static (float gap, float side, int frames) Fly(Catalog catalog, ModelLibrary models, MaterialLibrary materials, Transform root,
            string id, string model, ProjectileKind kind, float distance, float dt, bool jump)
        {
            var holder = new GameObject(id).transform;
            holder.SetParent(root, false);
            try
            {
                var emitters = new Emitters(materials, holder);
                var pool = new ProjectilePool(holder, 4);
                var systems = holder.GetComponentsInChildren<ParticleSystem>();
                var flame = systems.First(ps => ps.name == "Motor Core");
                var weapon = catalog.Weapons[id];
                var chunk = models.Merged(model);
                var from = new Vector3(0f, 2.5f, 0f);
                var to = new Vector3(distance * 0.8f, 0.4f, distance * 0.6f);
                var duration = distance / weapon.ProjectileSpeed;
                var artillery = weapon.MinRange > 0f;
                var scale = weapon.ProjectileScale * WeaponEffects.SizeOf(weapon, kind, model, false);
                var barrel = (to - from).normalized + Vector3.up * (artillery ? 0.8f : 0.1f);
                pool.Launch(chunk, from, to, duration, kind == ProjectileKind.Missile ? distance * 0.06f : distance * 0.02f, 0.55f, 0f,
                    boost: kind == ProjectileKind.Missile ? 0.55f : artillery ? 0.2f : 0.3f, scale: scale,
                    control: artillery ? WeaponEffects.Bend(from, to, barrel.normalized) : WeaponEffects.Leave(from, to, barrel.normalized, distance * 0.02f),
                    plume: Plume.For(weapon, kind, model, false));
                var shot = holder.GetComponentsInChildren<MeshFilter>(true).First(f => f.sharedMesh == chunk.Mesh).transform;
                var tail = chunk.Mesh.bounds.min.z;
                var particles = new ParticleSystem.Particle[4096];
                float worstGap = 0f, worstSide = 0f;
                var frames = 0;
                var now = 0f;
                // The frozen-moment way: nothing drawn until half way, then one long frame.
                if (jump) now = duration * 0.5f - dt;
                pool.Tick(jump ? 0f : now, emitters);
                while (now + dt < duration * (jump ? 0.5f : 0.95f) + 1e-4f)
                {
                    now += dt;
                    // The frame's update (the missile placed, its flame emitted), then the particles' own step, then the draw.
                    pool.Tick(now, emitters);
                    foreach (var ps in systems) ps.Simulate(jump ? 1f / 30f : dt, false, false, false);
                    if (!shot.gameObject.activeSelf) break;
                    var forward = shot.forward;
                    var nozzle = shot.TransformPoint(new Vector3(0f, 0f, tail));
                    var count = flame.GetParticles(particles);
                    // The white-hot core born this frame: set a tenth of the flame's width behind the nozzle.
                    var front = float.MinValue;
                    var side = 0f;
                    for (var i = 0; i < count; i++)
                    {
                        var p = particles[i];
                        if (p.startLifetime - p.remainingLifetime > dt * 1.01f) continue;
                        var d = p.position - nozzle;
                        // (Its size is 0.8 of that width, give or take a tenth.)
                        var along = Vector3.Dot(d, forward) + p.startSize * 0.125f;
                        if (along <= front) continue;
                        front = along;
                        side = (d - forward * Vector3.Dot(d, forward)).magnitude;
                    }
                    if (front == float.MinValue) continue;
                    frames++;
                    if (Mathf.Abs(front) > Mathf.Abs(worstGap)) worstGap = front;
                    worstSide = Mathf.Max(worstSide, side);
                }
                return (worstGap, worstSide, frames);
            }
            finally
            {
                Object.DestroyImmediate(holder.gameObject);
            }
        }

        /// <summary>Drawn size of each flying munition as a share of its model (type table x the weapon's scale), fitted to its launcher.</summary>
        [Test]
        public void MissilesAreDrawnToFitTheirLaunchers()
        {
            var catalog = GameContent.LoadCatalog();
            float Drawn(string id, string model, bool air = false) =>
                catalog.Weapons[id].ProjectileScale * WeaponEffects.SizeOf(catalog.Weapons[id], catalog.Weapons[id].Projectile, model, air);
            // The SAM launcher's Buk (3.6 m model) out of its 2.45 m launcher box: 2.6 m, was 4.3 m.
            Assert.AreEqual(0.72f, Drawn("sam_long", "buk"), 0.01f, "the SAM launcher's missile");
            Assert.Less(Drawn("sam", "shorad_dart"), 1f, "SHORAD darts no bigger than their model");
            Assert.AreEqual(0.744f, Drawn("heli_atgm", "hellfire", true), 0.01f, "a helicopter's Hellfire (1.04 m, its rack 0.81 m)");
            Assert.AreEqual(0.696f, Drawn("maverick", "maverick", true), 0.01f, "the A-10's Maverick (1.39 m, its rack 1.1 m)");
            Assert.AreEqual(1.15f, Drawn("mlrs_rockets", "gmlrs"), 0.01f, "MLRS rockets as they were (they fit their pod)");
            Assert.AreEqual(1.2f, Drawn("air_cruise_missile", "cruise_missile", true), 0.01f, "cruise missiles as they were");
        }
    }
}
