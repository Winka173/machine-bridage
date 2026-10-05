using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 14 after lane H (lane I, DECISIONS "Play-test 14 after lane H (lane I)"): the flying bosses' engine flames at a
    /// quarter of their size; the player's smoke gear hidden (kept behind its Hidden flag, never rolled, worn or fired, old
    /// pieces re-rolled); the missiles the owner still found too fast (Typhon's sail Buk, Nemesis' and Juggernaut's missile
    /// and rocket cars) traced to their weapons and slowed. Written, not run.
    /// </summary>
    public class PlayTest14LaneITests
    {
        [Test]
        public void TheEngineFlamesBurnAtAQuarterOfTheirSize()
        {
            Assert.AreEqual(0.25f, EngineFlames.FlameScale, 1e-4f);
        }

        [Test]
        public void TheSmokeGearIsKeptButHidden()
        {
            var warning = GearCatalog.Base("laser_warning");
            Assert.IsNotNull(warning, "the laser warning receiver stays in the catalogue");
            Assert.IsTrue(warning.Hidden);
            Assert.IsFalse(GearCatalog.BasesFor(GearSlot.Optics).Any(b => b.Id == "laser_warning"), "never offered");
            Assert.IsTrue(GearCatalog.Module(SpecialModule.SmokeDischarger) is { Hidden: true }, "the smoke discharger stays, hidden");
            Assert.IsFalse(GearCatalog.ShownModules.Any(m => m.Module == SpecialModule.SmokeDischarger));
            Assert.IsTrue(GearCatalog.TowerTraits.Any(t => t.Id == TraitId.TowerSmokeLaunchers && t.Hidden), "the tower smoke launchers stay, hidden");
            Assert.IsFalse(GearCatalog.TowerTraitsFor(GearSlot.TowerStructure).Any(t => t.Id == TraitId.TowerSmokeLaunchers));
            // Everything else is still offered.
            Assert.Greater(GearCatalog.BasesFor(GearSlot.Optics).Count(), 3);
            Assert.AreEqual(GearCatalog.Modules.Length - 1, GearCatalog.ShownModules.Count());

            var rng = new System.Random(5);
            for (var i = 0; i < 2000; i++)
                Assert.AreNotEqual(SpecialModule.SmokeDischarger, Gear.PickModule(rng, BranchMask.All), "never rolled");
        }

        [Test]
        public void AnOldSavesSmokeGearIsRerolledAndNeverFired()
        {
            var module = new GearItem { id = 41, slot = (int)GearSlot.Special, rarity = (int)Rarity.Epic, special = (int)SpecialModule.SmokeDischarger, baseType = "smoke_discharger", seed = 7 };
            Assert.IsTrue(Gear.IsHidden(module));
            Assert.AreEqual(SpecialModule.None, Gear.Boost(1, new[] { module }).Special, "a hidden module never rides into battle");
            Assert.IsTrue(Gear.Unhide(module));
            Assert.AreEqual(GearSlot.Special, module.Slot);
            Assert.AreEqual((int)Rarity.Epic, module.rarity, "same rarity");
            Assert.IsFalse(Gear.IsHidden(module));
            Assert.AreEqual(GearKeys.Module(module.Module), module.baseType);
            Assert.IsFalse(Gear.Unhide(module), "once is enough");

            var optics = new GearItem { id = 42, slot = (int)GearSlot.Optics, rarity = (int)Rarity.Rare, level = 3, baseType = "laser_warning", seed = 9 };
            Assert.IsFalse(Gear.FitsBranch(optics, GearBranch.Armor), "a hidden piece fits no branch");
            Assert.IsTrue(Gear.Unhide(optics));
            Assert.AreNotEqual("laser_warning", optics.baseType);
            Assert.AreEqual(GearSlot.Optics, optics.Slot);
            Assert.AreEqual(3, optics.level, "same level");
            Assert.IsFalse(Gear.IsHidden(optics));

            var structure = GearCatalog.TowerBasesFor(GearSlot.TowerStructure).First();
            var tower = new GearItem
            {
                id = 43, slot = (int)GearSlot.TowerStructure, rarity = (int)Rarity.Epic, baseType = structure.Id, seed = 11,
                trait = GearKeys.Trait(TraitId.TowerSmokeLaunchers),
                traitOptions = new List<string> { GearKeys.Trait(TraitId.TowerSmokeLaunchers) },
            };
            Assert.IsTrue(Gear.IsHidden(tower));
            Assert.IsTrue(Gear.Unhide(tower));
            Assert.AreNotEqual(GearKeys.Trait(TraitId.TowerSmokeLaunchers), tower.trait);
            Assert.IsFalse(tower.traitOptions.Contains(GearKeys.Trait(TraitId.TowerSmokeLaunchers)));
            Assert.IsFalse(Gear.IsHidden(tower));
        }

        [Test]
        public void TheMissilesTheOwnerSawFlyAtReadableSpeeds()
        {
            var c = Lab.Catalog;
            // Typhon: its main mount (Mount_missile on top of Part_sail) is the Buk post, at aircraft only, flying straight.
            var typhon = c.Vehicle("typhon");
            Assert.AreEqual("sam_post", typhon.Mounts[0].Weapon.Id);
            Assert.AreEqual("missile", typhon.Mounts[0].Slot);
            Assert.AreEqual(145f, c.Weapons["sam_post"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(FlightProfile.Direct, c.Weapons["sam_post"].Flight);
            // Nemesis: the rocket car (mount 3) and the SAM car (mount 4).
            var nemesis = c.Vehicle("nuke_train");
            Assert.AreEqual("p26_nemesis_sec_boss_rockets", nemesis.Mounts[3].Weapon.Id);
            Assert.AreEqual("sam_battery", nemesis.Mounts[4].Weapon.Id);
            Assert.AreEqual(80f, c.Weapons["p26_nemesis_sec_boss_rockets"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(FlightProfile.Ballistic, c.Weapons["p26_nemesis_sec_boss_rockets"].Flight);
            Assert.AreEqual(165f, c.Weapons["sam_battery"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(FlightProfile.Loft, c.Weapons["sam_battery"].Flight);
            // Juggernaut: the rocket car (mount 1).
            var juggernaut = c.Vehicle("armored_train");
            Assert.AreEqual("pt14_train_grad", juggernaut.Mounts[1].Weapon.Id);
            Assert.AreEqual(80f, c.Weapons["pt14_train_grad"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(FlightProfile.Ballistic, c.Weapons["pt14_train_grad"].Flight);
            // Flight feel 05/10 (lane B): every speed above now follows the owner's flight-feel spec (boss barrage 80, Buk 145, Patriot 165).
            Assert.AreEqual(80f, c.Weapons["boss_rockets"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(165f, c.Weapons["patriot"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(165f, c.Weapons["sam_pac3"].ProjectileSpeed, 1e-3f);
            foreach (var id in new[] { "sam_post", "sam_battery", "p26_nemesis_sec_boss_rockets", "pt14_train_grad" })
            {
                var w = c.Weapons[id];
                Assert.Less(w.Range / w.ProjectileSpeed, w.Cooldown, id + " lands before its next shot");
            }
        }
    }
}
