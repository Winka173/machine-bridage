using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>Siege and Boss Rush play to an end under the commander AI.</summary>
    public class SiegeModeTests
    {
        private static readonly string[] Army =
            { "main_battle_tank", "heavy_tank", "tank_destroyer", "siege_mortar", "attack_helicopter", "engineer_vehicle" };

        [Test]
        public void AttackersBreakAFortressOfFixedDefences()
        {
            // A fortress of defences in the enemy corner (the fallback target when a map has no HQ).
            var units = new List<UnitPlacement>();
            foreach (var (def, x, z) in new[] { ("gun_turret", 40f, 30f), ("gun_turret", 30f, 40f), ("aa_turret", 45f, 45f),
                         ("mg_bunker", 25f, 25f), ("rocket_turret", 50f, 35f), ("guard_tower", 35f, 50f) })
                units.Add(new UnitPlacement(def, 1, new Vector2(x, z), 3.9f));
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("fort", 160f,
                new[] { new TeamStart(0, new Vector2(-60f, -60f)), new TeamStart(1, new Vector2(60f, 60f)) },
                new List<PropPlacement>(), units), seed: 4);
            var mode = new SiegeMode(new SiegeRules
            {
                Attacker = new SideSetup { StartCp = 30f, Income = 1.5f, ArmyCap = 34, Vehicles = Army },
                Defender = new SideSetup { StartCp = 10f, Income = 0.6f, Vehicles = new[] { "main_battle_tank", "apc" } },
            });
            mode.Setup(world);
            var defender = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, 3) { Stance = CommanderStance.Defend, DefendPoint = mode.Fortress };
            var attacker = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 4) { Goal = _ => mode.Fortress };
            var t = 0f;
            for (; t < 16 * 60 && mode.Result == null; t += TestWorlds.Step)
            {
                mode.Tick(world, TestWorlds.Step);
                defender.Tick(world, TestWorlds.Step);
                attacker.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            Debug.Log($"Siege: {(mode.Result?.WinningTeam == 0 ? "WON" : "LOST")} after {t / 60f:0.0} min, progress {mode.Progress(world):P0}, losses {mode.Losses}");
            Assert.IsNotNull(mode.Result, "a siege always ends");
            Assert.AreEqual(0, mode.Result.Value.WinningTeam, "a strong army levels a small fortress");
        }

        [Test]
        public void BossRushSendsBossesOneAfterAnother()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("dunebreak_sandbox"), seed: 6);
            var mode = new BossRushMode(new BossRushRules
            {
                Bosses = new[] { "behemoth", "mega_gunship" },
                Player = new SideSetup { StartCp = 30f, Income = 1.6f, ArmyCap = 36, Vehicles = Army },
            });
            mode.Setup(world);
            world.TryGetRally(0, out var home);
            var waves = new TacticalAi(1, 0, 6) { Objective = _ => home };
            var player = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 7)
            {
                Goal = w => w.TryGetVehicle(mode.Boss, out var b) && b.IsAlive ? b.Position : null,
            };
            var t = 0f;
            for (; t < 22 * 60 && mode.Result == null; t += TestWorlds.Step)
            {
                mode.Tick(world, TestWorlds.Step);
                waves.Tick(world, TestWorlds.Step);
                player.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            Debug.Log($"Boss rush: {mode.Defeated}/{mode.Total} bosses after {t / 60f:0.0} min, losses {mode.Losses}");
            Assert.GreaterOrEqual(mode.Defeated, 1, "the first boss falls and the next one comes");
        }
    }
}
