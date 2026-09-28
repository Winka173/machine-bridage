using System.Collections.Generic;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
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
            Assert.GreaterOrEqual(Length("sam_long"), Length("atgm") * 2f, "a SAM's plume is long, an ATGM's short");
            Assert.Greater(Length("sam_long"), Length("heli_atgm", true), "air-to-ground missiles in between");
            Assert.IsFalse(Plume.For(catalog.Weapons["fpv_swarm"], ProjectileKind.Drone, "fpv_drone", false).Burns, "drones fly on propellers");
        }

        /// <summary>The speeds after DECISIONS 12B, and every flight at full range still shorter than its weapon's cooldown.</summary>
        [Test]
        public void MissilesFlySlowerAndLandBeforeTheirCooldown()
        {
            var catalog = GameContent.LoadCatalog();
            var speeds = new Dictionary<string, float>
            {
                { "atgm", 19f }, { "kornet_twin", 20f }, { "sam", 32f }, { "sam_long", 37f }, { "sam_battery", 37f }, { "sam_48n6", 50f },
                { "heli_atgm", 21f }, { "hellfire_volley", 21f }, { "drone_missile", 21f }, { "vikhr", 24f }, { "maverick", 23f },
                { "air_to_air", 34f }, { "wvr_aam", 34f }, { "stinger_atas", 29f }, { "air_cruise_missile", 17f },
                { "heli_rockets", 48f }, { "s8_pods", 48f },
            };
            foreach (var (id, speed) in speeds)
                Assert.AreEqual(speed, catalog.Weapons[id].ProjectileSpeed, 1e-3f, id);
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
