using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Mathf = UnityEngine.Mathf;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Test feedback 19P, the In action clips and effects: what the simulation now tells the presentation (a
    /// jammed round's miss, where a round struck a dome), the range's hooks (mortal targets, a never-empty
    /// magazine, held fire), the sky gunship's turn and the clips' readouts in both languages.
    /// </summary>
    public class InActionTests
    {
        private static SimWorld Field() =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 160f,
                new[] { new TeamStart(0, new Vector2(-60f, -60f)), new TeamStart(1, new Vector2(60f, 60f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        private static List<SimEvent> Run(SimWorld world, float seconds)
        {
            var events = new List<SimEvent>();
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                events.AddRange(world.Events);
                world.ClearEvents();
            }
            return events;
        }

        [Test]
        public void JammedRoundsAreFiredWithTheirMiss()
        {
            var world = Field();
            world.SpawnVehicle("heavy_tank", 0, new Vector2(0f, 0f), 0f);
            world.SpawnVehicle("ew_jammer", 0, new Vector2(0f, -10f), 0f);
            world.SpawnVehicle("fpv_carrier", 1, new Vector2(0f, 30f), 3.14f);
            int fired = 0, jammed = 0;
            foreach (var e in Run(world, 25f))
            {
                if (e.Kind != SimEventKind.WeaponFired || e.DefId != "fpv_swarm") continue;
                fired++;
                if (!e.Jammed) continue;
                jammed++;
                Assert.Greater(e.Offset.Length(), 4f, "a jammed round lands wide: the view is told how far");
            }
            Assert.Greater(fired, 0, "the carrier launched");
            Assert.Greater(jammed, fired / 2, "most of them are scrambled");
        }

        [Test]
        public void MortalTargetsGoDownAndDummiesDoNot()
        {
            var world = Field();
            var dummy = world.SpawnVehicle("ifv", 1, new Vector2(-8f, 0f), 0f);
            var mortal = world.SpawnVehicle("ifv", 1, new Vector2(8f, 0f), 0f);
            world.MakeDummy(dummy);
            world.MakeDummy(mortal);
            world.MakeMortal(mortal);
            world.DebugDamage(dummy, 20f);
            world.DebugDamage(mortal, 20f);
            Run(world, 0.5f);
            Assert.IsTrue(dummy.IsAlive, "a plain range target stops at a sliver");
            Assert.IsFalse(mortal.IsAlive, "the In action clip's enemies can be knocked out");
        }

        [Test]
        public void RefilledLauncherNeverRunsDryAndHeldFireHolds()
        {
            var world = Field();
            var launcher = world.SpawnVehicle("heavy_rocket_artillery", 0, new Vector2(0f, -40f), 0f);
            world.SpawnVehicle("recon_drone", 0, new Vector2(0f, -15f), 0f);
            for (var i = 0; i < 4; i++) world.SpawnVehicle("heavy_tank", 1, new Vector2(i * 8f - 12f, 50f), 3.14f);
            var full = launcher.Ammo(0);
            var salvos = 0;
            for (var t = 0f; t < 60f; t += TestWorlds.Step)
            {
                world.Refill(launcher);
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == launcher.Id && e.Mount == 0) salvos++;
                world.ClearEvents();
            }
            Assert.Greater(salvos, full, "it fires more salvos than it carries");
            world.HoldFire(launcher, true);
            var held = 0;
            foreach (var e in Run(world, 20f))
                if (e.Kind == SimEventKind.WeaponFired && e.Entity == launcher.Id) held++;
            Assert.AreEqual(0, held, "held fire holds");
        }

        [Test]
        public void DomeHitsSayWhereTheRoundCameFrom()
        {
            var world = Field();
            var generator = world.SpawnVehicle("shield_tower", 0, new Vector2(0f, 0f), 0f);
            world.SpawnVehicle("ifv", 0, new Vector2(4f, 3f), 0f);
            world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 29f), 3.14f);
            world.SpawnVehicle("recon_drone", 1, new Vector2(0f, 20f), 3.14f);
            int hits = 0, fromOutside = 0;
            foreach (var e in Run(world, 20f))
            {
                if (e.Kind != SimEventKind.DomeHit) continue;
                hits++;
                Assert.AreEqual(generator.Id, e.Entity);
                // A shell's own hit comes from where it was fired; its blast's splash from where it burst.
                if (Vector2.Distance(e.Target, generator.Position) > generator.Def.Dome.Radius - 1f && e.Target.Y > 10f) fromOutside++;
            }
            Assert.Greater(hits, 0, "the dome took hits");
            Assert.Greater(fromOutside, 0, "a hit says it came from the gun outside the dome");
        }

        [Test]
        public void SkyGunshipCirclesCloseWithAllItsGunsInReach()
        {
            var catalog = GameContent.LoadCatalog();
            var gunship = catalog.Vehicles["sky_gunship"];
            Assert.IsTrue(gunship.Orbit);
            Assert.Greater(gunship.OrbitRadius, 0f);
            var guns = new HashSet<string>();
            foreach (var m in gunship.Mounts)
            {
                guns.Add(m.Weapon.Id);
                if (m.Weapon.CanTarget(false)) Assert.Greater(m.Weapon.Range, gunship.OrbitRadius + 8f, m.Weapon.Id + " reaches across the turn");
            }
            foreach (var id in new[] { "gunship_105", "gunship_40mm", "gunship_25mm" }) Assert.IsTrue(guns.Contains(id), id);
            // It fires every one of them at a ground fight it circles.
            var world = Field();
            var ship = world.SpawnVehicle("sky_gunship", 0, new Vector2(0f, -10f), 0f);
            // The 25 mm is for light vehicles (it cannot get through a tank's armour).
            foreach (var (id, x) in new[] { ("ifv", -6f), ("armored_car", 0f), ("main_battle_tank", 6f) })
                world.SpawnVehicle(id, 1, new Vector2(x, 10f), 3.14f);
            world.SpawnVehicle("recon_drone", 0, new Vector2(0f, 0f), 0f);
            var fired = new HashSet<string>();
            foreach (var e in Run(world, 30f))
                if (e.Kind == SimEventKind.WeaponFired && e.Entity == ship.Id) fired.Add(e.DefId);
            foreach (var id in new[] { "gunship_105", "gunship_40mm", "gunship_25mm" }) Assert.IsTrue(fired.Contains(id), id + " fired (fired: " + string.Join(",", fired) + ")");
        }

        [Test]
        public void CalledGunshipStaysOverItsSpot()
        {
            var world = Field();
            var economy = new TeamEconomy(0, 999f, income: 50f, bank: 999f);
            economy.Items["gunship_support"] = 1;
            world.EnableEconomy(economy);
            world.EnableEconomy(new TeamEconomy(1));
            world.SpawnVehicle("recon_drone", 0, new Vector2(0f, -10f), 0f);
            for (var i = 0; i < 2; i++) world.SpawnVehicle("armored_car", 1, new Vector2(i * 6f - 3f, 0f), 3.14f);
            // A juicier group 55 m off, which it used to fly off to.
            for (var i = 0; i < 3; i++) world.SpawnVehicle("heavy_tank", 1, new Vector2(40f + i * 5f, 38f), 3.14f);
            Assert.IsTrue(world.Submit(Command.Strike(0, "gunship_support", new Vector2(0f, 0f), default)).Accepted);
            var farthest = 0f;
            for (var t = 0f; t < 28f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                if (t < 8f) continue;
                foreach (var v in world.Vehicles)
                    if (v.IsAlive && v.Def.Id == "sky_gunship") farthest = Mathf.Max(farthest, v.Position.Length());
            }
            Assert.Greater(farthest, 0f, "the gunship came");
            Assert.Less(farthest, 48f, "it circles over the spot it was called to");
        }

        [Test]
        public void RangeReadoutsAreInBothLanguages()
        {
            foreach (var key in new[] { "range.relay", "range.relay.quiet", "range.depot", "range.supply" })
            {
                var was = Strings.Vietnamese;
                try
                {
                    Strings.Vietnamese = false;
                    // Named placeholders (prompt 21 I.3): each name of the text gets 1, 2, ...
                    var args = System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Select(System.Linq.Enumerable.Distinct(Strings.PlaceholderNames(Strings.Get(key))), (n, i) => (n, (object)(i + 1))));
                    var en = Strings.Format(key, args);
                    Strings.Vietnamese = true;
                    var vi = Strings.Format(key, args);
                    Assert.AreNotEqual(en, vi, key);
                    Assert.IsFalse(en.Contains(key), key);
                }
                finally
                {
                    Strings.Vietnamese = was;
                }
            }
        }
    }
}
