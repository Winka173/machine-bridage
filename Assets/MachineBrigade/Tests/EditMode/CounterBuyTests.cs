using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>The commander buys what answers the enemy's army: anti-air against aircraft, anti-armour against tanks.</summary>
    public class CounterBuyTests
    {
        private static readonly string[] Deck = { "aa_vehicle", "main_battle_tank", "tank_destroyer", "armored_car", "light_tank" };

        private static Dictionary<string, int> Bought(string enemy, int count)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 120f,
                new[] { new TeamStart(0, new Vector2(0f, -50f)), new TeamStart(1, new Vector2(0f, 50f)) },
                new List<PropPlacement>(), new List<UnitPlacement>(),
                new[] { new CapturePointDef("mid", "mid", new Vector2(0f, 0f), 8f) }));
            var mode = new ConquestMode(new ConquestRules
            {
                Tickets = 1000,
                StartCp = 70f,
                PlayerVehicles = Deck,
                BaseDefences = false,
                Outposts = false,
            });
            mode.Setup(world);
            // The enemy army parks where ours can see it; it is told to hold still.
            for (var i = 0; i < count; i++) world.SpawnVehicle(enemy, 1, new Vector2(i * 6f - 12f, -22f), 0f);
            var ai = new ConquestAi(mode, 0, 1, AiDifficulty.Normal, 3) { AutoStrike = false };
            for (var t = 0f; t < 25f; t += TestWorlds.Step)
            {
                mode.Tick(world, TestWorlds.Step);
                ai.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            var bought = new Dictionary<string, int>();
            foreach (var id in Deck) bought[id] = 0;
            foreach (var v in world.Vehicles)
                if (v.Team == 0 && bought.ContainsKey(v.Def.Id)) bought[v.Def.Id]++;
            return bought;
        }

        [Test]
        public void AgainstAircraftItBuysAntiAir()
        {
            var bought = Bought("attack_helicopter", 5);
            Assert.GreaterOrEqual(bought["aa_vehicle"], 2, string.Join(", ", bought));
        }

        [Test]
        public void AgainstTanksItBuysAntiArmourNotAntiAir()
        {
            var bought = Bought("heavy_tank", 4);
            Assert.AreEqual(0, bought["aa_vehicle"], string.Join(", ", bought));
            Assert.GreaterOrEqual(bought["tank_destroyer"] + bought["main_battle_tank"], 2, string.Join(", ", bought));
        }
    }
}
