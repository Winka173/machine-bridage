using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The counter system in practice: equal-CP skirmishes on an open field, each commanded by
    /// the tactical AI, where the counter must win. These are the balance targets.
    /// </summary>
    public class CounterTests
    {
        private static SimWorld Field() =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        /// <summary>Runs a fight and returns the winning team (-1: nobody within the time).</summary>
        internal static int Skirmish(string a, int countA, string b, int countB, out string summary, float seconds = 150f,
            string spotter = null)
        {
            var world = Field();
            // Artillery needs eyes: a drone circling well out of the fight's reach.
            if (spotter != null) world.SpawnVehicle(spotter, 0, new Vector2(-40f, 0f), 0f);
            var sideA = new List<Vehicle>();
            var sideB = new List<Vehicle>();
            for (var i = 0; i < countA; i++) sideA.Add(world.SpawnVehicle(a, 0, new Vector2((i % 4) * 7f - 10f, -45f - (i / 4) * 9f), 0f));
            for (var i = 0; i < countB; i++) sideB.Add(world.SpawnVehicle(b, 1, new Vector2((i % 4) * 7f - 10f, 45f + (i / 4) * 9f), 3.14f));
            var aiA = new TacticalAi(0, 1) { Objective = _ => new Vector2(0f, 40f) };
            var aiB = new TacticalAi(1, 0) { Objective = _ => new Vector2(0f, -40f) };
            var t = 0f;
            for (; t < seconds; t += TestWorlds.Step)
            {
                aiA.Tick(world, TestWorlds.Step);
                aiB.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                if (Alive(sideA) == 0 || Alive(sideB) == 0) break;
            }
            float Hp(List<Vehicle> side)
            {
                var sum = 0f;
                foreach (var v in side) if (v.IsAlive) sum += v.Hp / v.MaxHp;
                return sum;
            }
            summary = $"{countA}x {a} vs {countB}x {b}: {Alive(sideA)} ({Hp(sideA):0.0}) - {Alive(sideB)} ({Hp(sideB):0.0}) after {t:0} s";
            Debug.Log("SKIRMISH " + summary);
            if (Alive(sideB) == 0 && Alive(sideA) > 0) return 0;
            if (Alive(sideA) == 0 && Alive(sideB) > 0) return 1;
            // Time out: whoever kept more of their strength.
            var ha = Hp(sideA) / countA;
            var hb = Hp(sideB) / countB;
            return ha > hb * 1.2f ? 0 : hb > ha * 1.2f ? 1 : -1;
        }

        private static int Alive(List<Vehicle> side)
        {
            var n = 0;
            foreach (var v in side) if (v.IsAlive) n++;
            return n;
        }

        [Test]
        public void EveryCardSaysWhatItBeatsAndWhatBeatsIt()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var id in MatchSettings.AllVehicles)
                Assert.IsNotEmpty(Counters.Line(catalog.Vehicle(id)), id);
            CollectionAssert.Contains(Counters.WeakVs(UnitClass.Tank), UnitClass.TankHunter);
            CollectionAssert.Contains(Counters.WeakVs(UnitClass.Helicopter), UnitClass.AntiAir);
            Assert.AreEqual(UnitClass.TankHunter, catalog.Vehicle("tank_destroyer").Class);
            Assert.AreEqual(UnitClass.Artillery, catalog.Vehicle("ballistic_launcher").Class);
            Assert.AreEqual(UnitClass.Defense, catalog.Vehicle("gun_turret").Class);
        }

        [TestCase("main_battle_tank", 3, "armored_car", 7, TestName = "Tanks beat light vehicles")]
        [TestCase("tank_destroyer", 7, "main_battle_tank", 6, TestName = "Tank destroyers beat tanks")]
        [TestCase("aa_vehicle", 3, "attack_helicopter", 2, TestName = "Anti-air beats helicopters")]
        [TestCase("attack_helicopter", 7, "main_battle_tank", 6, TestName = "Helicopters beat tanks")]
        [TestCase("armored_car", 4, "artillery", 2, TestName = "Light vehicles beat artillery")]
        [TestCase("artillery", 3, "gun_turret", 2, "recon_drone", TestName = "Artillery beats fixed defences")]
        [TestCase("fighter_jet", 2, "attack_helicopter", 3, TestName = "Fighters beat helicopters")]
        [TestCase("heavy_tank", 2, "main_battle_tank", 3, TestName = "Heavy tanks beat medium tanks")]
        [TestCase("sam_launcher", 3, "attack_jet", 2, TestName = "SAM beats jets")]
        [TestCase("ifv", 3, "scout_jeep", 7, TestName = "IFVs beat scouts")]
        [TestCase("fpv_carrier", 4, "heavy_tank", 2, TestName = "FPV drones beat heavy tanks")]
        [TestCase("tank_buster", 2, "heavy_tank", 2, TestName = "Tank busters beat heavy tanks")]
        public void CounterWins(string counter, int count, string victim, int victims, string spotter = null)
        {
            var winner = Skirmish(counter, count, victim, victims, out var summary, spotter: spotter);
            Assert.AreEqual(0, winner, summary);
        }
    }
}
