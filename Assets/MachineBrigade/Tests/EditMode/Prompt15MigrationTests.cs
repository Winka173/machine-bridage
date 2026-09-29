using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 15 C.9: equipment written for "heavy / light vehicles, aircraft" and the old damage types opens in a
    /// save from before and reads its new lines by level: every piece keeps its id, slot, rarity and level.
    /// </summary>
    public class Prompt15MigrationTests
    {
        // Slots: Weapon 0, Loader 1, Armor 2, Optics 3, Engine 4, Repair 5, Special 6; the loadout is branch x 7 + slot.
        // Stat numbers as they were saved: 7 damage vs heavy, 17 armour-piercing resistance, 20 flak resistance.
        private const string OldSave = @"{
            ""gearVersion"": 3, ""rosterVersion"": 1,
            ""gear"": [
                { ""id"": 1, ""slot"": 0, ""rarity"": 2, ""level"": 5, ""baseType"": ""tungsten_penetrator"", ""subs"": [ { ""stat"": 7, ""roll"": 0.9 }, { ""stat"": 17, ""roll"": 0.8 } ], ""seed"": 11 },
                { ""id"": 2, ""slot"": 2, ""rarity"": 3, ""level"": 4, ""baseType"": ""applique_steel"", ""subs"": [ { ""stat"": 20, ""roll"": 0.7 } ], ""seed"": 12 },
                { ""id"": 3, ""slot"": 2, ""rarity"": 1, ""level"": 2, ""baseType"": ""armoured_tub"", ""subs"": [], ""seed"": 13 },
                { ""id"": 4, ""slot"": 6, ""rarity"": 3, ""level"": 1, ""special"": 1, ""subs"": [], ""seed"": 14 },
                { ""id"": 5, ""slot"": 6, ""rarity"": 4, ""level"": 1, ""special"": 1, ""subs"": [], ""seed"": 15 },
                { ""id"": 6, ""slot"": 2, ""rarity"": 2, ""level"": 3, ""baseType"": ""composite_addon"", ""subs"": [], ""seed"": 16 }
            ],
            ""loadout"": [ 1, 0, 2, 0, 0, 0, 5,   0, 0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0, 0,   0, 0, 3, 0, 0, 0, 4 ]
        }";

        [TearDown]
        public void Reset() => PlayerProfile.ResetForTests();

        [Test]
        public void OldEquipmentReadsItsNewLinesBySlotRarityAndLevel()
        {
            PlayerProfile.LoadForTests(OldSave);
            var owned = PlayerProfile.GearOwned;
            Assert.AreEqual(6, owned.Count, "nothing lost");
            var expected = new[] { (1, 0, 2, 5), (2, 2, 3, 4), (3, 2, 1, 2), (4, 6, 3, 1), (5, 6, 4, 1), (6, 2, 2, 3) };
            foreach (var (id, slot, rarity, level) in expected)
            {
                var g = PlayerProfile.FindGear(id);
                Assert.IsNotNull(g, "piece " + id);
                Assert.AreEqual(slot, g.slot, id + ": same slot");
                Assert.AreEqual(rarity, g.rarity, id + ": same rarity");
                Assert.AreEqual(level, g.level, id + ": same level");
                if (g.Slot != GearSlot.Special) Assert.IsNotEmpty(Gear.Lines(g), id + ": its lines read");
            }

            // The Tungsten Penetrator: part levels of penetration (a whole level at the top), not a share on heavy vehicles.
            var tungsten = PlayerProfile.FindGear(1);
            Assert.AreEqual(StatId.Penetration, GearCatalog.Bases.First(b => b.Id == "tungsten_penetrator").Implicit);
            Assert.AreEqual(0.7f * Gear.LevelShare(tungsten), Gear.ImplicitValue(tungsten), 1e-4f, "a rare piece's share of 0.7 levels");
            Assert.AreEqual(StatId.DamageVsHeavy, (StatId)tungsten.subs[0].stat, "damage vs heavy reads as heavy armour (levels 3-4)");
            Assert.AreEqual(StatId.ResistShapedCharge, (StatId)tungsten.subs[1].stat, "armour-piercing resistance reads as shaped charges");
            // Appliqué Steel: side and rear armour levels; the Armoured Tub: armour all round; the composite add-on: shaped charges.
            Assert.AreEqual(StatId.ArmourSide, GearCatalog.Bases.First(b => b.Id == "applique_steel").Implicit);
            Assert.AreEqual(StatId.ResistFragmentation, (StatId)PlayerProfile.FindGear(2).subs[0].stat, "flak resistance reads as fragmentation");
            Assert.AreEqual(StatId.ArmourAll, GearCatalog.Bases.First(b => b.Id == "armoured_tub").Implicit);
            Assert.AreEqual(StatId.ResistShapedCharge, GearCatalog.Bases.First(b => b.Id == "composite_addon").Implicit);
            Assert.AreEqual(StatId.ResistShapedCharge, Stats.Resist(DamageType.ShapedCharge));
            Assert.AreEqual(StatId.ResistEnergy, Stats.Resist(DamageType.Energy));

            // Reactive armour is for the ground now: the Armour branch keeps its module; on aircraft it became another
            // module of the same rarity, still worn in the same slot.
            Assert.AreEqual(SpecialModule.ReactiveArmor, PlayerProfile.FindGear(5).Module);
            Assert.AreEqual(5, PlayerProfile.Equipped(GearBranch.Armor, GearSlot.Special).id);
            var air = PlayerProfile.FindGear(4);
            Assert.AreNotEqual(SpecialModule.ReactiveArmor, air.Module, "an aircraft's reactive armour became a module that works for it");
            Assert.AreNotEqual(SpecialModule.None, air.Module);
            Assert.AreEqual(4, PlayerProfile.Equipped(GearBranch.Air, GearSlot.Special).id, "still worn");
            Assert.AreEqual(3, PlayerProfile.Equipped(GearBranch.Air, GearSlot.Armor).id, "the cockpit tub stays on the aircraft");
            StringAssert.Contains("\"gearVersion\":4", PlayerProfile.JsonForTests(), "migrated once");

            // Loading again changes nothing.
            var once = PlayerProfile.JsonForTests();
            PlayerProfile.LoadForTests(once);
            Assert.AreEqual(once, PlayerProfile.JsonForTests());
        }
    }
}
