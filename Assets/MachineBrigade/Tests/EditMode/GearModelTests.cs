using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>The equipment affix model: old saves, rolls, sub-stat growth, caps, merging, sets and crates.</summary>
    public class GearModelTests
    {
        [SetUp]
        public void SetUp() => PlayerProfile.ResetForTests();

        [TearDown]
        public void TearDown() => PlayerProfile.Load();

        /// <summary>
        /// A save from before the affix model: five pieces (two of them old Plating), the Armor
        /// branch wearing an armour kit and a plating piece, the Light branch only a plating piece.
        /// </summary>
        private const string OldSave = "{\"version\":1,\"coins\":100,\"gear\":[" +
            "{\"id\":1,\"slot\":3,\"rarity\":2,\"level\":7,\"special\":0}," +
            "{\"id\":2,\"slot\":2,\"rarity\":1,\"level\":3,\"special\":0}," +
            "{\"id\":3,\"slot\":3,\"rarity\":0,\"level\":1,\"special\":0}," +
            "{\"id\":4,\"slot\":6,\"rarity\":3,\"level\":1,\"special\":4}," +
            "{\"id\":5,\"slot\":0,\"rarity\":4,\"level\":10,\"special\":0}]," +
            "\"nextGearId\":6,\"loadout\":[5,0,2,1,0,0,4, 0,0,0,3,0,0,0, 0,0,0,0,0,0,0, 0,0,0,0,0,0,0]}";

        [Test]
        public void AnOldSaveMigratesWithNothingLost()
        {
            PlayerProfile.LoadForTests(OldSave);
            var gear = PlayerProfile.GearOwned;
            Assert.AreEqual(5, gear.Count, "every piece is still there");
            var plating = PlayerProfile.FindGear(1);
            Assert.AreEqual(GearSlot.Armor, plating.Slot, "old plating becomes an armour piece");
            Assert.IsTrue(Gear.BaseOf(plating).Plating, "with a plating base type");
            Assert.AreEqual(Rarity.Rare, plating.Rarity);
            Assert.AreEqual(7, plating.level);
            Assert.AreEqual(StatId.DamageTaken, Gear.MainStat(plating), "it still cuts the damage taken");
            Assert.AreEqual(0.055f * (0.4f + 0.6f * 6f / 14f), Gear.Value(plating), 1e-5f, "by exactly as much as before");
            Assert.AreEqual(2, plating.subs.Count, "a rare piece gets its two sub-stats");

            // The Armor branch wore both: the armour kit stays, the plating goes back to the bag; Optics starts empty.
            Assert.AreEqual(2, PlayerProfile.Equipped(GearBranch.Armor, GearSlot.Armor).id);
            Assert.IsNull(PlayerProfile.Equipped(GearBranch.Armor, GearSlot.Optics));
            Assert.IsFalse(PlayerProfile.IsEquipped(plating));
            // The Light branch wore only plating: it now wears it as its armour.
            Assert.AreEqual(3, PlayerProfile.Equipped(GearBranch.Light, GearSlot.Armor).id);
            Assert.AreEqual(5, PlayerProfile.Equipped(GearBranch.Armor, GearSlot.Weapon).id);

            var kit = PlayerProfile.FindGear(2);
            Assert.IsFalse(Gear.BaseOf(kit).Plating);
            Assert.AreEqual(StatId.Health, Gear.MainStat(kit));
            Assert.AreEqual(1, kit.subs.Count);
            var smoke = PlayerProfile.FindGear(4);
            Assert.AreEqual(SpecialModule.SmokeDischarger, smoke.Module);
            Assert.AreEqual("smoke_discharger", smoke.baseType);
            Assert.AreEqual(4, PlayerProfile.Equipped(GearBranch.Armor, GearSlot.Special).id);
            var legendary = PlayerProfile.FindGear(5);
            Assert.AreEqual(GearSlot.Weapon, legendary.Slot);
            Assert.IsNotNull(Gear.BaseOf(legendary));
            Assert.AreEqual(2, legendary.subs.Count);
            Assert.AreEqual(GearSlot.Weapon, GearCatalog.Trait(legendary.trait).Slot, "a legendary gets a weapon trait");
            Assert.That(legendary.brand, Is.InRange(1, GearCatalog.VehicleBrandCount));

            // The migration is the same every time, and a migrated save loads unchanged.
            var first = gear.Select(g => g.baseType + "/" + g.trait + "/" + string.Join(",", g.subs.Select(s => s.stat + ":" + s.roll))).ToList();
            var saved = PlayerProfile.JsonForTests();
            StringAssert.Contains("\"gearVersion\":3", saved);
            PlayerProfile.LoadForTests(OldSave);
            Assert.AreEqual(first, PlayerProfile.GearOwned.Select(g => g.baseType + "/" + g.trait + "/" + string.Join(",", g.subs.Select(s => s.stat + ":" + s.roll))).ToList());
            PlayerProfile.LoadForTests(saved);
            Assert.AreEqual(first, PlayerProfile.GearOwned.Select(g => g.baseType + "/" + g.trait + "/" + string.Join(",", g.subs.Select(s => s.stat + ":" + s.roll))).ToList());
            Assert.AreEqual(3, PlayerProfile.Equipped(GearBranch.Light, GearSlot.Armor).id);
        }

        [Test]
        public void RollsFollowTheRarityRules()
        {
            var rng = new System.Random(11);
            for (var n = 0; n < 400; n++)
                foreach (Rarity rarity in System.Enum.GetValues(typeof(Rarity)))
                {
                    var item = Crates.Roll(rarity, rng, n);
                    if (item.Slot == GearSlot.Special)
                    {
                        Assert.GreaterOrEqual(rarity, Rarity.Epic, "modules only at epic and up");
                        Assert.AreNotEqual(SpecialModule.None, item.Module);
                        Assert.AreEqual(GearKeys.Module(item.Module), item.baseType);
                        continue;
                    }
                    var b = Gear.BaseOf(item);
                    Assert.IsNotNull(b, item.baseType);
                    Assert.AreEqual(item.Slot, b.Slot);
                    Assert.GreaterOrEqual((int)rarity, b.MinRarity, "trade-offs drop at rare and up only");
                    Assert.AreEqual(b.NoSubs ? 0 : Gear.SubCount[(int)rarity], item.subs.Count, $"{rarity} {item.baseType}");
                    Assert.AreEqual(item.subs.Count, item.subs.Select(s => s.stat).Distinct().Count(), "no sub-stat twice");
                    foreach (var sub in item.subs)
                    {
                        Assert.AreNotEqual((int)Gear.MainStat(item), sub.stat, "never the main stat");
                        Assert.AreNotEqual((int)b.Implicit, sub.stat, "never the implicit");
                        Assert.That(sub.roll, Is.InRange(0.6f, 1f));
                        Assert.IsTrue(GearCatalog.Sub(sub.Stat).RollsOn(item.Slot));
                    }
                    Assert.That(item.brand, Is.InRange(1, GearCatalog.VehicleBrandCount));
                    if (rarity >= Rarity.Epic)
                    {
                        Assert.AreEqual(3, item.traitOptions.Count, "three traits offered");
                        CollectionAssert.Contains(item.traitOptions, item.trait);
                        Assert.AreEqual(item.Slot, GearCatalog.Trait(item.trait).Slot);
                    }
                    else Assert.IsTrue(string.IsNullOrEmpty(item.trait), "no trait below epic");
                }
        }

        [Test]
        public void SubStatsGrowAtLevelsFiveTenFifteenAndTwenty()
        {
            var item = new GearItem { slot = (int)GearSlot.Weapon, rarity = (int)Rarity.Legendary, baseType = "long_barrel" };
            var sub = new GearSub { stat = (int)StatId.DamageVsHeavy, roll = 0.8f };
            item.subs.Add(sub);
            var top = 0.06f * 0.8f;
            float At(int level)
            {
                item.level = level;
                return Gear.SubValue(item, sub);
            }
            Assert.AreEqual(top / 2f, At(1), 1e-5f, "a new legendary sub is at half (four bumps to come)");
            Assert.AreEqual(At(1), At(4), 1e-6f);
            Assert.AreEqual(top * 1.25f / 2f, At(5), 1e-5f);
            Assert.AreEqual(top * 1.5f / 2f, At(10), 1e-5f);
            Assert.AreEqual(top, At(20), 1e-5f, "all of it after the fourth bump");
            Assert.AreEqual(top, At(25), 1e-5f);
            var uncommon = new GearItem { slot = (int)GearSlot.Weapon, rarity = (int)Rarity.Uncommon, level = 10 };
            uncommon.subs.Add(new GearSub { stat = (int)StatId.DamageVsHeavy, roll = 1f });
            Assert.AreEqual(0.03f, Gear.SubValue(uncommon, uncommon.subs[0]), 1e-5f, "an uncommon gets one bump");
            Assert.AreEqual(0.5f, Gear.SubQuality(sub), 1e-5f, "the roll bar sits halfway for a 0.8 roll");
        }

        [Test]
        public void NoLoadoutGoesPastTheCaps()
        {
            // Six top pieces with perfect rolls, four of one brand and two of another.
            var rng = new System.Random(5);
            for (var trial = 0; trial < 200; trial++)
            {
                var loadout = new List<GearItem>();
                for (var s = 0; s < Gear.NormalSlots; s++)
                {
                    var item = Crates.Roll(Rarity.Legendary, rng, s + 1);
                    while (item.Slot == GearSlot.Special || item.slot != s) item = Crates.Roll(Rarity.Legendary, rng, s + 1);
                    item.level = Gear.LevelCap[(int)Rarity.Legendary];
                    foreach (var sub in item.subs) sub.roll = 1f;
                    item.brand = s < 4 ? 1 + trial % 10 : 1 + (trial + 3) % 10;
                    loadout.Add(item);
                }
                var boost = Gear.Boost(1, loadout);
                for (var i = 0; i < (int)StatId.Count; i++)
                    Assert.LessOrEqual(boost.Stat((StatId)i), GearCatalog.StatCap[i] + 1e-5f, ((StatId)i).ToString());
                Assert.LessOrEqual(boost.Damage, 1.25f + 1e-5f);
                Assert.LessOrEqual(boost.FireRate, 1.15f + 1e-5f);
                Assert.LessOrEqual(boost.Hp, 1.25f + 1e-5f);
                Assert.GreaterOrEqual(boost.DamageTaken, 0.8f - 1e-5f);
                Assert.LessOrEqual(boost.Speed, 1.15f + 1e-5f);
            }
            // A trade-off's drawback comes after the cap: a capped engine still pays the heavy barrel's 6 %.
            var engine = new GearItem { slot = (int)GearSlot.Engine, rarity = 4, level = 25, baseType = "overtuned_engine" };
            var engine2 = new GearItem { slot = (int)GearSlot.Engine, rarity = 4, level = 25, baseType = "drivetrain" };
            var barrel = new GearItem { slot = (int)GearSlot.Weapon, rarity = 4, level = 25, baseType = "heavy_barrel" };
            var fast = Gear.Boost(1, new[] { engine, engine2, barrel });
            Assert.AreEqual(1f + 0.15f - 0.07f, fast.Speed, 1e-4f);
            Assert.AreEqual(1f - 0.06f, fast.Hp, 1e-4f, "the overtuned engine's drawback");
            Assert.AreEqual(0.12f, fast.Stat(StatId.Range), 1e-4f, "the heavy barrel's range, at the range cap");
        }

        [Test]
        public void MergingKeepsThePrimaryAndRollsATraitAtEpic()
        {
            PlayerProfile.AddCoins(10000);
            var pieces = new List<GearItem>();
            var rng = new System.Random(3);
            foreach (var type in new[] { "long_barrel", "bunker_buster", "tungsten_penetrator" })
            {
                var g = new GearItem { slot = (int)GearSlot.Weapon, rarity = (int)Rarity.Rare, baseType = type, brand = 2, seed = 77 };
                Gear.FillSubs(g, rng);
                PlayerProfile.AddGear(g);
                pieces.Add(g);
            }
            PlayerProfile.TryLevelGear(pieces[1]);
            PlayerProfile.Equip(GearBranch.Armor, pieces[2]);
            var subs = pieces[2].subs.Select(s => (s.stat, s.roll)).ToList();
            var before = PlayerProfile.Coins;
            var epic = PlayerProfile.TryMerge(pieces[0]);
            Assert.AreSame(pieces[2], epic, "different base types of one slot merge; the equipped one is kept");
            Assert.AreEqual(Rarity.Epic, epic.Rarity);
            Assert.AreEqual("tungsten_penetrator", epic.baseType, "it keeps its base type");
            Assert.AreEqual(subs, epic.subs.Select(s => (s.stat, s.roll)).ToList(), "and its sub-stats");
            Assert.AreEqual(3, epic.traitOptions.Count, "three traits were rolled for the player to pick from later");
            CollectionAssert.Contains(epic.traitOptions, epic.trait);
            Assert.AreEqual(GearSlot.Weapon, GearCatalog.Trait(epic.trait).Slot);
            Assert.AreEqual(before + Gear.Spent(new GearItem { level = 2 }), PlayerProfile.Coins, "the fodder's levels come back");
            // The player may pick another of the three offered, never one that was not.
            var other = epic.traitOptions.First(o => o != epic.trait);
            Assert.IsTrue(PlayerProfile.ChooseTrait(epic, other));
            Assert.AreEqual(other, epic.trait);
            Assert.IsFalse(PlayerProfile.ChooseTrait(epic, "not_a_trait"));

            // Two more epics of the slot: up to legendary, keeping the trait at its legendary value.
            for (var i = 0; i < 2; i++)
            {
                var g = new GearItem { slot = (int)GearSlot.Weapon, rarity = (int)Rarity.Epic, baseType = "long_barrel", seed = 5 + i };
                Gear.FillSubs(g, rng);
                Gear.RollTrait(g, rng, BranchMask.All);
                PlayerProfile.AddGear(g);
            }
            var trait = epic.trait;
            var epicValue = Gear.TraitOf(epic).A;
            var legendary = PlayerProfile.TryMerge(epic);
            Assert.AreSame(epic, legendary);
            Assert.AreEqual(Rarity.Legendary, legendary.Rarity);
            Assert.AreEqual(trait, legendary.trait, "the trait stays");
            Assert.AreEqual(GearCatalog.Trait(trait).Legendary[0], Gear.TraitOf(legendary).A, 1e-6f, "at its legendary value");
            Assert.GreaterOrEqual(Gear.TraitOf(legendary).A, epicValue - 1e-6f);
            Assert.AreEqual(subs, legendary.subs.Select(s => (s.stat, s.roll)).ToList());
            Assert.AreEqual(1, PlayerProfile.GearOwned.Count);
        }

        [Test]
        public void SetsCountTheSixNormalSlots()
        {
            GearItem Piece(GearSlot slot, int brand) => new() { slot = (int)slot, rarity = 1, level = 1, brand = brand };
            var two = new[] { Piece(GearSlot.Weapon, 1), Piece(GearSlot.Engine, 1), Piece(GearSlot.Loader, 3) };
            var boost = Gear.Boost(1, two);
            var plain = Gear.Boost(1, new[] { Piece(GearSlot.Weapon, 0), Piece(GearSlot.Engine, 0), Piece(GearSlot.Loader, 0) });
            Assert.AreEqual(plain.Hp * 1.06f, boost.Hp, 1e-4f, "Ironclad's two pieces: +6 % health");
            Assert.IsNull(boost.Traits, "no four-piece yet");
            var chips = Gear.SetChips(two);
            Assert.AreEqual(2, chips.Count);
            Assert.AreEqual("ironclad", chips[0].Brand.Id);
            Assert.IsTrue(chips[0].TwoPiece);
            Assert.IsFalse(chips[0].FourPiece);
            Assert.AreEqual(1, chips[1].Count);

            var four = new[]
            {
                Piece(GearSlot.Weapon, 10), Piece(GearSlot.Loader, 10), Piece(GearSlot.Armor, 10), Piece(GearSlot.Optics, 10),
                Piece(GearSlot.Engine, 4), Piece(GearSlot.Repair, 4),
                new GearItem { slot = (int)GearSlot.Special, rarity = 3, special = (int)SpecialModule.VeteranCrew, brand = 4 },
            };
            var full = Gear.Boost(1, four);
            Assert.IsNotNull(full.Traits);
            Assert.IsTrue(full.Traits.Any(t => t.Id == TraitId.SetHeavyRound), "Hammerfall's four pieces");
            Assert.AreEqual(0.08f, full.Stat(StatId.DamageVsStructure), 1e-5f, "and its two-piece");
            Assert.AreEqual(0.05f, full.Stat(StatId.Range), 1e-5f, "Longbow's two-piece");
            Assert.AreEqual(2, Gear.BrandCounts(four)[4], "the special slot does not count for sets");
            Assert.AreEqual(SpecialModule.VeteranCrew, full.Special);
        }

        [Test]
        public void CratesFavourTheDecksBranches()
        {
            int AirPieces(BranchMask deck)
            {
                var rng = new System.Random(9);
                var air = 0;
                for (var i = 0; i < 3000; i++)
                {
                    var item = Crates.Roll(Rarity.Common, rng, i, deck);
                    if ((Gear.BaseOf(item).Branches & BranchMask.Air) != 0) air++;
                }
                return air;
            }
            var any = AirPieces(BranchMask.All);
            var airDeck = AirPieces(BranchMask.Air);
            Assert.Greater(airDeck, any * 1.15f, $"an air deck finds more air equipment ({airDeck} against {any})");
        }

        [Test]
        public void EveryCatalogueEntryHasWords()
        {
            var missing = new List<string>();
            void Need(string key)
            {
                if (!MachineBrigade.Game.Hud.Strings.Has(key)) missing.Add(key);
            }
            foreach (var b in GearCatalog.Bases) Need("gear.base." + b.Id);
            foreach (var m in GearCatalog.Modules)
            {
                Need("special." + m.Key);
                Need("special." + m.Key + ".info");
            }
            foreach (var t in GearCatalog.Traits)
            {
                Need("trait." + t.Key);
                Need("trait." + t.Key + ".info");
            }
            foreach (var b in GearCatalog.Brands)
            {
                Need("set." + b.Id);
                Need("trait." + GearKeys.Trait(b.FourPiece.Id));
                Need("trait." + GearKeys.Trait(b.FourPiece.Id) + ".info");
            }
            for (var i = 0; i < (int)StatId.Count; i++) Need("stat.line." + GearKeys.Snake(((StatId)i).ToString()));
            foreach (var b in GearCatalog.Bases)
                if (b.TradeOff) Need("stat.pen." + GearKeys.Snake(b.Penalty.ToString()));
            Assert.That(missing, Is.Empty, "missing: " + string.Join(", ", missing));
            Assert.AreEqual(38, GearCatalog.Bases.Length, "38 stat base types (prompt 8: one retired, two merged, six new)");
            Assert.AreEqual(14, GearCatalog.Modules.Length, "14 special modules");
            Assert.AreEqual(45, GearCatalog.Traits.Length, "45 traits (prompt 8: three new lines)");
        }
    }
}
