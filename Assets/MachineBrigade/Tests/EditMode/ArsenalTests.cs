using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>Card ranks, equipment (values, caps, merging), crates (odds, pity) and what they do in battle.</summary>
    public class ArsenalTests
    {
        [SetUp]
        public void SetUp() => PlayerProfile.ResetForTests();

        [TearDown]
        public void TearDown() => PlayerProfile.Load();

        [Test]
        public void RankingUpCostsCoinsAndBlueprintsAndAddsFivePercent()
        {
            const string card = "main_battle_tank";
            Assert.AreEqual(1, PlayerProfile.Rank(card));
            Assert.IsFalse(PlayerProfile.TryRankUp(card), "no coins, no blueprints");
            PlayerProfile.AddCoins(1000);
            PlayerProfile.AddBlueprints(card, CardRanks.BlueprintsToNext(1));
            Assert.IsTrue(PlayerProfile.TryRankUp(card));
            Assert.AreEqual(2, PlayerProfile.Rank(card));
            Assert.AreEqual(1000 - CardRanks.CoinsToNext(1), PlayerProfile.Coins);
            Assert.AreEqual(0, PlayerProfile.Blueprints(card));
            Assert.AreEqual(0.05f, CardRanks.Bonus(2), 1e-5f);
            Assert.AreEqual(0.45f, CardRanks.Bonus(CardRanks.Max), 1e-5f, "rank 10 is +45%");
        }

        [Test]
        public void EquipmentGrowsWithLevelAndALoadoutIsCapped()
        {
            var low = new GearItem { slot = (int)GearSlot.Weapon, rarity = (int)Rarity.Legendary, level = 1 };
            var top = new GearItem { slot = (int)GearSlot.Weapon, rarity = (int)Rarity.Legendary, level = Gear.LevelCap[(int)Rarity.Legendary] };
            Assert.AreEqual(0.14f * 0.4f, Gear.Value(low), 1e-4f, "a new piece gives 40% of its rarity's top");
            Assert.AreEqual(0.14f, Gear.Value(top), 1e-4f);
            // Two top weapons would be +28%: the loadout caps damage at +25%.
            var boost = Gear.Boost(1, new[] { top, top });
            Assert.AreEqual(1.25f, boost.Damage, 1e-4f);
            var ranked = Gear.Boost(5, new[] { top });
            Assert.AreEqual(1.2f * 1.14f, ranked.Damage, 1e-4f, "rank and equipment multiply");
            Assert.AreEqual(1.2f, ranked.Hp, 1e-4f);
        }

        [Test]
        public void ThreeIdenticalPiecesMergeIntoTheNextRarityAndRefundTheirLevels()
        {
            PlayerProfile.AddCoins(10000);
            var pieces = new List<GearItem>();
            for (var i = 0; i < 3; i++)
            {
                var g = new GearItem { slot = (int)GearSlot.Armor, rarity = (int)Rarity.Rare };
                PlayerProfile.AddGear(g);
                pieces.Add(g);
            }
            PlayerProfile.TryLevelGear(pieces[1]);
            PlayerProfile.TryLevelGear(pieces[1]);
            PlayerProfile.Equip(GearBranch.Armor, pieces[2]);
            var before = PlayerProfile.Coins;
            var merged = PlayerProfile.TryMerge(pieces[0]);
            Assert.IsNotNull(merged);
            Assert.AreEqual(Rarity.Epic, merged.Rarity);
            Assert.AreSame(pieces[2], merged, "the equipped piece is the one kept");
            Assert.AreEqual(1, PlayerProfile.GearOwned.Count);
            Assert.AreEqual(before + Gear.Spent(new GearItem { level = 3 }), PlayerProfile.Coins, "the levels spent on the fodder come back");
            Assert.AreSame(merged, PlayerProfile.Equipped(GearBranch.Armor, GearSlot.Armor));
        }

        [Test]
        public void CrateOddsAreProperAndPityHolds()
        {
            foreach (var table in Crates.Odds) Assert.AreEqual(1f, table.Sum(), 1e-4f);
            Assert.AreEqual(1f, Crates.GoldGuaranteed.Sum(), 1e-4f);
            Assert.AreEqual(1f, Crates.LegendaryGuaranteed.Sum(), 1e-4f);
            var cards = new List<string> { "main_battle_tank", "ifv", "artillery" };
            var id = 1;
            // Whatever the luck, five gold crates in a row hold an epic and four legendary crates a legendary.
            for (var seed = 0; seed < 40; seed++)
            {
                var rng = new System.Random(seed);
                int sinceEpic = 0, sinceLegendary = 0, epicRun = 0;
                for (var n = 0; n < 30; n++)
                {
                    var loot = Crates.Open(CrateKind.Gold, rng, cards, ref sinceEpic, ref sinceLegendary, () => id++);
                    epicRun = loot.Gear.Any(g => g.Rarity >= Rarity.Epic) ? 0 : epicRun + 1;
                    Assert.Less(epicRun, Crates.EpicPity[(int)CrateKind.Gold]);
                    Assert.Less(sinceLegendary, Crates.LegendaryPity[(int)CrateKind.Gold]);
                    Assert.AreEqual(Crates.Rolls[(int)CrateKind.Gold], loot.Gear.Count);
                    Assert.AreEqual(Crates.PrintCount[(int)CrateKind.Gold], loot.Blueprints.Sum(b => b.count));
                }
                int e2 = 0, l2 = 0;
                for (var n = 0; n < 12; n++)
                {
                    Crates.Open(CrateKind.Legendary, rng, cards, ref e2, ref l2, () => id++);
                    Assert.Less(l2, Crates.LegendaryPity[(int)CrateKind.Legendary]);
                }
            }
        }

        [Test]
        public void SpecialModulesOnlyComeAtEpicAndUp()
        {
            var rng = new System.Random(3);
            for (var i = 0; i < 500; i++)
            {
                Assert.AreNotEqual(GearSlot.Special, Crates.Roll(Rarity.Rare, rng, i).Slot);
                var epic = Crates.Roll(Rarity.Epic, rng, i);
                if (epic.Slot == GearSlot.Special) Assert.AreNotEqual(SpecialModule.None, epic.Module);
            }
        }

        [Test]
        public void UpgradesToughenAndSharpenTheSidesVehicles()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 160f,
                new[] { new TeamStart(0, new Vector2(-60f, -60f)), new TeamStart(1, new Vector2(60f, 60f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));
            var plain = world.SpawnVehicle("main_battle_tank", 1, new Vector2(20f, 0f), 0f);
            world.SetBoosts(0, _ => new VehicleBoost(1.3f, 1.2f, 1.1f, 1.05f, 0.9f, 0.01f, SpecialModule.SmokeDischarger, 8f));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-20f, 0f), 0f);
            Assert.AreEqual(plain.MaxHp * 1.3f, tank.MaxHp, 1f, "more health");
            Assert.AreEqual(tank.MaxHp, tank.Hp, 1e-3f, "and it starts at full health");
            var before = tank.Hp;
            world.Damage.Apply(tank, 100f, DamageType.HighExplosive);
            var taken = before - tank.Hp;
            var plainBefore = plain.Hp;
            world.Damage.Apply(plain, 100f, DamageType.HighExplosive);
            Assert.AreEqual((plainBefore - plain.Hp) * 0.9f, taken, 0.5f, "plating takes a share off every hit");
            // Below half health its smoke dischargers fire, once.
            world.Damage.Apply(tank, tank.Hp * 0.6f / world.Catalog.Damage.Type(DamageType.HighExplosive, tank.Kind) / 0.9f, DamageType.HighExplosive);
            var smoke = world.Strikes.Smoke.Count;
            world.Step(0.05f);
            Assert.AreEqual(smoke + 1, world.Strikes.Smoke.Count, "the smoke screen goes up");
        }
    }
}
