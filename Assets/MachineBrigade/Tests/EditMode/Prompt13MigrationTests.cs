using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 13 J, the migrations: the sky gunship is no card any more, the engineer lost its rearm aura
    /// to the ammunition carrier, Deathmatch is scored in CP, and the difficulty names are one ladder (saved
    /// difficulties keep their meaning, Very Hard came after them).
    /// </summary>
    public class Prompt13MigrationTests
    {
        [Test]
        public void TheSkyGunshipIsNoCardAndNoDeckOrAiPicksIt()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.IsTrue(catalog.Vehicles.TryGetValue("sky_gunship", out var gunship), "the Gunship item still flies it");
            Assert.IsFalse(gunship.Card, "no card");
            CollectionAssert.DoesNotContain(MatchSettings.AllVehicles, "sky_gunship");
            Assert.IsNull(CardMerges.Resolve("sky_gunship"), "a saved deck drops it");
            var pool = catalog.Vehicles.Keys.ToList();
            foreach (AiDifficulty difficulty in System.Enum.GetValues(typeof(AiDifficulty)))
                for (var seed = 1; seed <= 4; seed++)
                    CollectionAssert.DoesNotContain(ConquestAi.PickDeck(catalog, pool, difficulty, seed, MatchSettings.AllVehicles), "sky_gunship",
                        $"{difficulty} seed {seed}");
        }

        [Test]
        public void TheEngineerRepairsAndTheAmmunitionCarrierRearms()
        {
            var catalog = GameContent.LoadCatalog();
            var engineer = catalog.Vehicles["engineer_vehicle"];
            var carrier = catalog.Vehicles["ammo_carrier"];
            Assert.IsNotNull(engineer.RepairAura, "the engineer keeps its repairs");
            Assert.IsNull(engineer.RearmAura, "its rearm aura moved");
            Assert.IsNull(engineer.AirRearm);
            Assert.IsNotNull(carrier.RearmAura, "launchers reload beside the carrier");
            Assert.IsNotNull(carrier.AirRearm, "helicopters rearm beside it");
            Assert.IsTrue(carrier.Card);
            CollectionAssert.Contains(MatchSettings.AllVehicles, "ammo_carrier");
        }

        [Test]
        public void DeathmatchScoresTheCpOfWhatWasDestroyed()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("range", 300f,
                new[] { new TeamStart(0, new Vector2(0f, -130f)), new TeamStart(1, new Vector2(0f, 130f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: 5);
            var mode = new DeathmatchMode(new DeathmatchRules());
            mode.Setup(world);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 60f), 0f);
            var buggy = world.SpawnVehicle("light_tank", 1, new Vector2(20f, 60f), 0f);
            mode.Tick(world, 0.05f);
            world.Step(0.05f);
            var before = mode.Score(0);
            tank.Hp = 0f;
            buggy.Hp = 0f;
            for (var i = 0; i < 4; i++)
            {
                world.Step(0.05f);
                mode.Tick(world, 0.05f);
            }
            Assert.AreEqual(tank.Def.ArmyCost + buggy.Def.ArmyCost, mode.Score(0) - before, "two kills score their price, not two");
            Assert.AreEqual(2, mode.Kills(0));
            Assert.GreaterOrEqual(mode.ScoreTarget, 300, "the target is in CP now (it was 30 kills)");
        }

        [Test]
        public void SavedDifficultiesKeepTheirMeaningAndTheNamesAreOneLadder()
        {
            Assert.AreEqual(AiDifficulty.Easy, MatchSettings.DifficultyFromSave(0));
            Assert.AreEqual(AiDifficulty.Normal, MatchSettings.DifficultyFromSave(1));
            Assert.AreEqual(AiDifficulty.Hard, MatchSettings.DifficultyFromSave(2));
            Assert.AreEqual(AiDifficulty.VeryHard, MatchSettings.DifficultyFromSave(3));
            Assert.AreEqual(AiDifficulty.Normal, MatchSettings.DifficultyFromSave(9), "anything unknown: Normal");
            Assert.AreEqual(AiDifficulty.Normal, MatchSettings.DifficultyFromSave(-1));
            // The campaign's and Operations' tiers carry the same names as the skirmish difficulties.
            var was = Strings.Vietnamese;
            foreach (var language in new[] { false, true })
            {
                Strings.Vietnamese = language;
                try
                {
                    Assert.AreEqual(Strings.Get("menu.normal"), Strings.Get("tier.0"));
                    Assert.AreEqual(Strings.Get("menu.hard"), Strings.Get("tier.1"));
                    Assert.AreEqual(Strings.Get("menu.veryhard"), Strings.Get("tier.2"));
                }
                finally { Strings.Vietnamese = was; }
            }
            Assert.Greater(Rewards.DifficultyFactor(AiDifficulty.VeryHard), Rewards.DifficultyFactor(AiDifficulty.Hard));
        }
    }
}
