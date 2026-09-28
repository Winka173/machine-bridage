using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Round 6: no two weapons of a vehicle fire together (the APC's cannon and coaxial gun were
    /// seen firing at once), for every vehicle; a tank's machine gun takes on aircraft when its
    /// main gun has nothing on the ground.
    /// </summary>
    public class WeaponTurnTests
    {
        private static SimWorld Range(Catalog catalog) =>
            new SimWorld(catalog, new MapDefinition("range", 220f,
                new[] { new TeamStart(0, new Vector2(0f, -90f)), new TeamStart(1, new Vector2(0f, 90f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: 7);

        [Test]
        public void NoTwoWeaponsOfAnyVehicleFireTogether()
        {
            var catalog = GameContent.LoadCatalog();
            var clashes = new List<string>();
            foreach (var def in catalog.Vehicles.Values)
            {
                if (def.Boss || def.Mounts.Count(m => m.Weapon.Damage > 0f) < 2) continue;
                var world = Range(catalog);
                var shooter = world.SpawnVehicle(def.Id, 0, new Vector2(0f, -12f), 0f);
                foreach (var (id, at) in new[] { ("main_battle_tank", new Vector2(-4f, 12f)), ("ifv", new Vector2(5f, 15f)), ("attack_helicopter", new Vector2(8f, 6f)) })
                    world.MakeDummy(world.SpawnVehicle(id, 1, at, System.MathF.PI));
                var last = new Dictionary<int, double>();
                var heavyAt = double.NegativeInfinity;
                var heavyMount = -1;
                for (var t = 0f; t < 25f && clashes.Count < 12; t += TestWorlds.Step)
                {
                    world.Step(TestWorlds.Step);
                    foreach (var e in world.Events)
                    {
                        if (e.Kind != SimEventKind.WeaponFired || e.Entity != shooter.Id) continue;
                        var now = world.Time;
                        var weapon = def.Mounts[e.Mount].Weapon;
                        var gun = weapon.Projectile == ProjectileKind.Bullet && weapon.Cooldown < 0.35f && weapon.Burst <= 1;
                        foreach (var (mount, at) in last)
                            if (mount != e.Mount && now - at < 0.199)
                            {
                                clashes.Add($"{def.Id}: mount {e.Mount} {now - at:0.00} s after mount {mount} ({now:0.0} s)");
                                break;
                            }
                        if (gun && heavyMount >= 0 && heavyMount != e.Mount && now - heavyAt < 0.4)
                            clashes.Add($"{def.Id}: machine gun {e.Mount} {now - heavyAt:0.00} s after heavy mount {heavyMount}");
                        last[e.Mount] = now;
                        if (!gun)
                        {
                            heavyAt = now;
                            heavyMount = e.Mount;
                        }
                    }
                    world.ClearEvents();
                }
            }
            Assert.IsEmpty(clashes, string.Join("\n", clashes));
        }

        [Test]
        public void ATankWithNothingOnTheGroundChasesAnAircraftWithItsCoaxialGun()
        {
            var world = Range(GameContent.LoadCatalog());
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(12f, 10f), System.MathF.PI);
            world.MakeDummy(heli);
            int coax = 0, main = 0;
            for (var t = 0f; t < 10f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == tank.Id)
                    {
                        if (e.Mount == 1) coax++;
                        if (e.Mount == 0) main++;
                    }
                world.ClearEvents();
            }
            Assert.Greater(coax, 0, "the coaxial gun fires at the helicopter, the turret swung after it");
            Assert.AreEqual(0, main, "the main gun cannot hit aircraft and does not try");
        }
    }
}
