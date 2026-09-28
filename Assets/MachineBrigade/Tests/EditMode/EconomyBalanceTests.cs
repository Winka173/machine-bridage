using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Balance checks for the economy's pace, run only with MB_BALANCE=1 (they play whole matches).
    /// MB_INCOME overrides balance.json's income scale, to compare settings side by side.
    /// </summary>
    public class EconomyBalanceTests
    {
        private static readonly string[] Army =
            { "main_battle_tank", "heavy_tank", "tank_destroyer", "aa_vehicle", "artillery", "ifv", "mlrs", "attack_helicopter" };

        private static readonly string[] Strikes = { "artillery_barrage", "airstrike" };

        private static void OnlyWhenAsked()
        {
            if (System.Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance check: set MB_BALANCE=1 to run it");
        }

        private static void Pace(SimWorld world)
        {
            var income = System.Environment.GetEnvironmentVariable("MB_INCOME");
            if (string.IsNullOrEmpty(income) || !float.TryParse(income, System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out var scale)) return;
            for (var team = 0; team < 2; team++)
                if (world.TryGetEconomy(team, out var economy)) economy.IncomeScale = scale;
        }

        [Test]
        public void BossRushOverSeeds()
        {
            OnlyWhenAsked();
            var won = 0;
            var defeated = 0;
            for (var seed = 1; seed <= 4; seed++)
            {
                var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("dunebreak_sandbox"), seed: seed);
                var mode = new BossRushMode(new BossRushRules
                {
                    Player = new SideSetup { StartCp = 30f, Income = 1.6f, ArmyCap = 36, Vehicles = Army, Supports = Strikes },
                });
                mode.Setup(world);
                Pace(world);
                world.TryGetRally(0, out var home);
                var waves = new TacticalAi(1, 0, seed) { Objective = _ => home };
                var player = new ConquestAi(mode, 0, 1, AiDifficulty.Normal, seed + 10)
                {
                    Goal = w => w.TryGetVehicle(mode.Boss, out var b) && b.IsAlive ? b.Position : null,
                };
                var t = 0f;
                for (; t < 27 * 60 && mode.Result == null; t += TestWorlds.Step)
                {
                    mode.Tick(world, TestWorlds.Step);
                    waves.Tick(world, TestWorlds.Step);
                    player.Tick(world, TestWorlds.Step);
                    world.Step(TestWorlds.Step);
                    world.ClearEvents();
                }
                var win = mode.Result?.WinningTeam == 0;
                if (win) won++;
                defeated += mode.Defeated;
                world.TryGetEconomy(0, out var economy);
                Debug.Log($"BALANCE boss rush seed {seed}: {(win ? "WON" : "lost")}, {mode.Defeated}/{mode.Total} bosses, " +
                          $"{t / 60f:0.0} min, losses {mode.Losses}, income scale {economy.IncomeScale:0.00}");
            }
            Debug.Log($"BALANCE boss rush: {won}/4 won, {defeated} bosses in all");
        }
    }
}
