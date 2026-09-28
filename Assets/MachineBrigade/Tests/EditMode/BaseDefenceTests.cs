using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>Capture modes protect each camp: an HQ that cannot fall (it replaced the two bastions), a home zone that repairs, no strikes on a camp.</summary>
    public class BaseDefenceTests
    {
        [Test]
        public void EachCampHasAnUnbreakableHeadquartersAndAHomeZone()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 3);
            var mode = new ConquestMode(new ConquestRules());
            mode.Setup(world);
            var hqs = world.VehicleList.Where(v => v.Def.Id == world.Catalog.Base.HqId).ToList();
            Assert.AreEqual(1, hqs.Count(v => v.Team == 0), "an HQ at the player's camp");
            Assert.AreEqual(1, hqs.Count(v => v.Team == 1), "and one at the enemy's");
            Assert.IsTrue(hqs.All(v => v.Invulnerable), "that cannot be destroyed in Conquest");
            Assert.IsFalse(world.VehicleList.Any(v => v.Def.Id == BaseDefences.Bastion), "the old bastions are gone");

            // No strike can be called onto the enemy's camp.
            world.TryGetRally(1, out var enemyCamp);
            if (world.TryGetEconomy(0, out var economy)) economy.Cp = 100f;
            var result = world.Submit(Command.Strike(0, "artillery_barrage", enemyCamp));
            Assert.IsFalse(result.Accepted, "strikes on the enemy camp are refused");

            // A damaged vehicle at home repairs once it is left alone; a new one shrugs off most damage.
            world.TryGetRally(0, out var home);
            var tank = world.SpawnVehicle("main_battle_tank", 0, home + new Vector2(6f, 0f), 0f);
            world.Damage.Apply(tank, 1000f, MachineBrigade.Sim.Content.DamageType.ArmorPiercing);
            Assert.Greater(tank.Hp, tank.MaxHp - 1000f * 0.21f, "a vehicle just arrived takes a fifth of the damage");
            var hurt = tank.Hp;
            for (var t = 0f; t < 8f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            Assert.Greater(tank.Hp, hurt, "and it repairs at home");
        }
    }
}
