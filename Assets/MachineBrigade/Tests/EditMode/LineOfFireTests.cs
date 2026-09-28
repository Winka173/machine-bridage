using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Direct fire does not go through buildings and rock: a tank behind a house cannot shoot
    /// what is on the other side, a round that meets a wall bursts on it, and the tank drives
    /// round to a firing position. Artillery lobs over; low cover does not stop anything.
    /// </summary>
    public class LineOfFireTests
    {
        /// <summary>An open 120 m field with one prop in the middle.</summary>
        private static SimWorld FieldWith(string prop) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 120f,
                new[] { new TeamStart(0, new Vector2(-50f, -50f)), new TeamStart(1, new Vector2(50f, 50f)) },
                new List<PropPlacement> { new(prop, Vector2.Zero, 0) }, new List<UnitPlacement>()));

        private static Prop OnlyProp(SimWorld world) => world.PropList[0];

        [Test]
        public void ATankCannotShootThroughAHouseButArtilleryCan()
        {
            var world = FieldWith("house_large");
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -16f), 0f);
            var howitzer = world.SpawnVehicle("artillery", 0, new Vector2(-4f, -40f), 0f);
            var enemy = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 16f), 3.14f);
            Assert.IsTrue(OnlyProp(world).Def.BlocksFire);
            Assert.IsFalse(world.HasLineOfFire(tank, enemy, tank.Def.Weapon), "the house is in the way");
            Assert.IsTrue(world.HasLineOfFire(howitzer, enemy, howitzer.Def.Weapon), "a howitzer lobs its shells over");
        }

        [Test]
        public void LowCoverDoesNotStopAShot()
        {
            var world = FieldWith("sandbags");
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -16f), 0f);
            var enemy = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 16f), 3.14f);
            Assert.IsFalse(OnlyProp(world).Def.BlocksFire);
            Assert.IsTrue(world.HasLineOfFire(tank, enemy, tank.Def.Weapon), "tanks fire over sandbags");
        }

        [Test]
        public void AHiddenTargetTakesNoFireButTheBuildingCanBeShot()
        {
            // Ordered onto a target hidden behind the house, the tank holds its fire until it has
            // a line; ordered onto the house itself, it shells the house.
            var world = FieldWith("house_large");
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -16f), 0f);
            var enemy = world.SpawnVehicle("heavy_tank", 1, new Vector2(0f, 14f), 3.14f);
            var house = OnlyProp(world);
            var enemyHp = enemy.Hp;
            world.Submit(new Command(CommandType.Attack, 0, new[] { tank.Id }, Vector2.Zero, enemy.Id));
            for (var t = 0f; t < 4f && !world.HasLineOfFire(tank, enemy, tank.Def.Weapon); t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                Assert.AreEqual(enemyHp, enemy.Hp, 0.01f, "no damage through the house");
            }

            var siege = FieldWith("house_large");
            var gunner = siege.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -18f), 0f);
            var target = OnlyProp(siege);
            siege.Submit(new Command(CommandType.Attack, 0, new[] { gunner.Id }, Vector2.Zero, target.Id));
            for (var t = 0f; t < 8f; t += TestWorlds.Step)
            {
                siege.Step(TestWorlds.Step);
                siege.ClearEvents();
            }
            Assert.Less(target.Hp, target.MaxHp, "a building is not in its own way");
        }

        [Test]
        public void ATankDrivesRoundCoverToGetItsShot()
        {
            var world = FieldWith("house_large");
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -18f), 0f);
            var enemy = world.SpawnVehicle("armored_car", 1, new Vector2(0f, 16f), 3.14f);
            world.Submit(new Command(CommandType.AttackMove, 0, new[] { tank.Id }, new Vector2(0f, 30f)));
            var hadNoShot = !world.HasLineOfFire(tank, enemy, tank.Def.Weapon);
            for (var t = 0f; t < 45f && enemy.IsAlive; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            Assert.IsTrue(hadNoShot, "the house hid the enemy at the start");
            Assert.IsFalse(enemy.IsAlive, "the tank found a firing position and won");
        }

        [Test]
        public void ADestroyedBuildingNoLongerBlocks()
        {
            var world = FieldWith("house_small");
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -16f), 0f);
            var enemy = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 16f), 3.14f);
            Assert.IsFalse(world.HasLineOfFire(tank, enemy, tank.Def.Weapon));
            var house = OnlyProp(world);
            world.Damage.Apply(house, house.MaxHp * 100f, DamageType.HighExplosive);
            Assert.IsFalse(house.IsAlive);
            Assert.IsTrue(world.HasLineOfFire(tank, enemy, tank.Def.Weapon), "rubble does not stop a shell");
        }
    }
}
