using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using NUnit.Framework;

namespace MachineBrigade.Tests
{
    /// <summary>A shot-down aircraft crashes on whatever is under it when it hits the ground.</summary>
    public class CrashTests
    {
        private static SimWorld Field()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 160f,
                new[] { new TeamStart(0, new Vector2(-60f, -60f)), new TeamStart(1, new Vector2(60f, 60f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));
            world.EnableEconomy(new TeamEconomy(0));
            world.EnableEconomy(new TeamEconomy(1));
            return world;
        }

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void AFallingHelicopterHurtsTheJeepUnderIt()
        {
            var world = Field();
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 0f), 0f);
            var jeep = world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var full = jeep.Hp;
            world.Damage.Apply(heli, 1e7f, DamageType.Flak);
            Run(world, 0.5f);
            Assert.IsFalse(heli.IsAlive);
            Assert.AreEqual(full, jeep.Hp, "nothing yet: it is still falling");
            Run(world, 3f);
            Assert.Less(jeep.Hp, full, "the wreck lands on it");
        }

        [Test]
        public void HeavierAircraftHitHarder()
        {
            var catalog = GameContent.LoadCatalog();
            var heli = DamageSystem.CrashBlast(catalog.Vehicles["scout_heli"]);
            var bomber = DamageSystem.CrashBlast(catalog.Vehicles["heavy_bomber"]);
            Assert.Greater(bomber.Damage, heli.Damage);
            Assert.Greater(bomber.Radius, heli.Radius);
        }
    }
}
