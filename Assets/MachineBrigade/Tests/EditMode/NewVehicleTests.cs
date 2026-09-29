using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The round 5 vehicles do what their cards say: the car bomb blows up on the enemy and
    /// spares its own side, the turtle tank's shed stops drones, the engineer mends towers, the
    /// railgun's slug goes through a line of vehicles.
    /// </summary>
    public class NewVehicleTests
    {
        private static SimWorld Field()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
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
        public void TheCarBombBlowsUpOnTheEnemyAndSparesItsOwnSide()
        {
            // The enemy here is a fixed tower.
            var world = Field();
            var bomb = world.SpawnVehicle("vbied", 0, new Vector2(-14f, 0f), 1.57f);
            var enemy = world.SpawnVehicle("guard_tower", 1, new Vector2(0f, 0f), 0f);
            var enemyHp = enemy.Hp;
            // Knocked out, so it cannot shoot the tank either: only the blast could hurt it.
            enemy.StunnedUntil = 1e9;
            world.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Attack, 0, new[] { bomb.Id }, default, enemy.Id));
            MachineBrigade.Sim.Entities.Vehicle friend = null;
            var friendHp = 0f;
            for (var t = 0f; t < 8f && bomb.IsAlive; t += TestWorlds.Step)
            {
                // Once the car is almost there, a friendly tank pulls up beside it.
                if (friend == null && System.Numerics.Vector2.Distance(bomb.Position, enemy.Position) < 7f)
                {
                    friend = world.SpawnVehicle("main_battle_tank", 0, bomb.Position + new Vector2(0f, 3.5f), 1.57f);
                    friendHp = friend.Hp;
                }
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            Run(world, 0.5f);
            Assert.IsFalse(bomb.IsAlive, "it went off");
            Assert.Less(enemy.Hp, enemyHp * 0.5f, "and wrecked the tower");
            Assert.IsNotNull(friend);
            Assert.AreEqual(friendHp, friend.Hp, "its own tank beside the blast is unhurt");
        }

        [Test]
        public void TheTurtleShedStopsMostOfADronesDamage()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.Less(catalog.Vehicles["turtle_tank"].DroneArmor, 0.5f);
            Assert.IsTrue(catalog.Vehicles["turtle_tank"].MineProof);
            Assert.AreEqual(MountAim.Hull, catalog.Vehicles["turtle_tank"].Mounts[0].Aim, "its gun cannot turn under the shed");
        }

        [Test]
        public void TheEngineerMendsATowerSlowly()
        {
            var world = Field();
            var tower = world.SpawnVehicle("guard_tower", 0, new Vector2(0f, 0f), 0f);
            world.SpawnVehicle("engineer_vehicle", 0, new Vector2(6f, 0f), 0f);
            world.Damage.Apply(tower, tower.MaxHp * 0.5f, DamageType.HighExplosive);
            var hurt = tower.Hp;
            Run(world, 10f);
            Assert.Greater(tower.Hp, hurt, "the tower is being repaired");
            Assert.Less(tower.Hp, tower.MaxHp, "but not all at once");
        }

        [Test]
        public void TheRailgunSlugGoesThroughALineOfVehicles()
        {
            var world = Field();
            var gun = world.SpawnVehicle("railgun_truck", 0, new Vector2(-24f, 0f), 1.57f);
            var first = world.SpawnVehicle("ifv", 1, new Vector2(10f, 0f), 0f);
            var second = world.SpawnVehicle("ifv", 1, new Vector2(18f, 0.5f), 0f);
            var a = first.Hp;
            var b = second.Hp;
            world.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Attack, 0, new[] { gun.Id }, default, first.Id));
            Run(world, 12f);
            Assert.Less(first.Hp, a, "the target is hit");
            Assert.Less(second.Hp, b, "and so is the vehicle behind it on the line");
        }
    }
}
