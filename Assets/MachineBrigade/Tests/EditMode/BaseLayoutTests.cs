using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The base screen's rules (BaseLayout): each hardpoint of a camp reads the loadout place the
    /// battle raises it from, towers go only where they fit, an emptied slot stays empty without
    /// moving the others, and only a valid layout is saved (an empty camp stays empty).
    /// </summary>
    public class BaseLayoutTests
    {
        [TearDown]
        public void RestoreProfile() => PlayerProfile.Load();

        private static Catalog Catalog => GameContent.LoadCatalog();

        /// <summary>A full camp with a gap in every size, so a wrong index shows.</summary>
        private static BaseLoadout Mixed(int level) => new()
        {
            HqLevel = level,
            Small = { "aa_turret", BaseLoadout.Empty, "mg_bunker", "guard_tower", "aa_turret", "mg_bunker" },
            Medium = { "rocket_turret", BaseLoadout.Empty, "atgm_tower" },
            Large = { BaseLoadout.Empty, "missile_battery" },
        };

        [Test]
        public void EveryHardpointShowsTheTowerTheBattleRaisesThere()
        {
            var catalog = Catalog;
            foreach (var map in MatchSettings.AllMaps)
                for (var level = 1; level <= catalog.Base.MaxLevel; level++)
                {
                    if (map.Id != "ashfield" && level != catalog.Base.MaxLevel) continue;
                    var world = new SimWorld(catalog, GameContent.LoadMap(map.Id + "_conquest"), seed: 1);
                    var site = world.Map.BaseOf(0);
                    Assert.IsNotNull(site, map.Id);
                    var loadout = Mixed(level);
                    var camp = BaseLayout.Camp(site, catalog.Base, level);
                    Assert.AreEqual(site.Slots.Count, camp.Count, "one entry a hardpoint");
                    var b = world.Bases.Establish(0, loadout, BaseRole.Anchor);
                    foreach (var slot in camp)
                    {
                        var raised = b.Slots.FirstOrDefault(s => s.Index == slot.Hardpoint);
                        Assert.AreEqual(slot.Open, raised != null, $"{map.Id} L{level} hardpoint {slot.Hardpoint} open");
                        if (raised == null) continue;
                        Assert.AreEqual(slot.Def.Class, slot.Slot.Size, "a tower place is its hardpoint's size");
                        Assert.AreEqual(BaseLayout.At(loadout, slot.Slot), raised.Tower, $"{map.Id} L{level} hardpoint {slot.Hardpoint} ({slot.Slot})");
                    }
                }
        }

        [Test]
        public void AnEmptiedSlotKeepsTheTowersAfterItInPlace()
        {
            var catalog = Catalog;
            var fitted = new BaseLoadout { HqLevel = 1, Small = { BaseLoadout.Empty, "aa_turret", "guard_tower", "mg_bunker" } }.Fitted(catalog);
            CollectionAssert.AreEqual(new[] { "", "aa_turret", "guard_tower" }, fitted.Small, "a gap counts as a slot");
            var trailing = new BaseLoadout { HqLevel = 5, Medium = { "gun_turret", BaseLoadout.Empty, BaseLoadout.Empty } }.Fitted(catalog);
            CollectionAssert.AreEqual(new[] { "gun_turret" }, trailing.Medium, "trailing gaps mean nothing");
            CollectionAssert.AreEqual(new[] { "missile_battery", "rocket_turret", "atgm_tower", "aa_turret", "mg_bunker", "guard_tower", "aa_turret", "mg_bunker" },
                Mixed(5).Towers.ToList(), "Towers leaves the gaps out");
        }

        [Test]
        public void TowersGoOnlyWhereTheyFit()
        {
            var catalog = Catalog;
            var loadout = new BaseLoadout();
            Assert.IsFalse(BaseLayout.Place(loadout, catalog, LoadoutSlot.Tower(SlotSize.Small, 0), "heavy_turret"), "a large tower not into a small slot");
            Assert.IsFalse(BaseLayout.Place(loadout, catalog, LoadoutSlot.Tower(SlotSize.Medium, 0), "missile_battery"));
            Assert.IsTrue(BaseLayout.Place(loadout, catalog, LoadoutSlot.Tower(SlotSize.Large, 0), "guard_tower"), "a light tower goes anywhere");
            Assert.IsFalse(BaseLayout.Fits(catalog, "aa_turret.flak", LoadoutSlot.Tower(SlotSize.Large, 0)), "a branch is not a card");
            Assert.IsFalse(BaseLayout.Fits(catalog, "point_tower", LoadoutSlot.Tower(SlotSize.Large, 0)), "nor a point's watchtower");
            Assert.IsFalse(BaseLayout.Fits(catalog, "light_tank", LoadoutSlot.Tower(SlotSize.Large, 0)), "nor a vehicle");
            Assert.IsFalse(BaseLayout.Fits(catalog, "guard_tower", LoadoutSlot.Utility(0)), "a tower is not a utility module");
            Assert.IsTrue(BaseLayout.Fits(catalog, "gun_turret", LoadoutSlot.Outpost(1)), "the outpost's medium slot");
            Assert.IsFalse(BaseLayout.Fits(catalog, "gun_turret", LoadoutSlot.Outpost(0)), "not its small one");

            Assert.IsTrue(BaseLayout.Place(loadout, catalog, LoadoutSlot.Tower(SlotSize.Small, 3), "aa_turret"));
            CollectionAssert.AreEqual(new[] { "", "", "", "aa_turret" }, loadout.Small, "placing further along leaves the slots before it empty");
            Assert.IsNull(BaseLayout.At(loadout, LoadoutSlot.Tower(SlotSize.Small, 1)));
            Assert.AreEqual("aa_turret", BaseLayout.At(loadout, LoadoutSlot.Tower(SlotSize.Small, 3)));
            Assert.IsTrue(BaseLayout.Place(loadout, catalog, LoadoutSlot.Tower(SlotSize.Small, 3), "mg_bunker"), "dropping replaces what was there");
            Assert.AreEqual("mg_bunker", BaseLayout.At(loadout, LoadoutSlot.Tower(SlotSize.Small, 3)));
            Assert.IsTrue(BaseLayout.Clear(loadout, LoadoutSlot.Tower(SlotSize.Small, 3)));
            Assert.IsEmpty(loadout.Small, "clearing the last one drops the trailing gaps");
            Assert.IsFalse(BaseLayout.Clear(loadout, LoadoutSlot.Outpost(0)), "an outpost keeps its two towers");
        }

        [Test]
        public void MovingSwapsWhenBothFitAndOtherwiseLeavesAGap()
        {
            var catalog = Catalog;
            var loadout = new BaseLoadout { Small = { "aa_turret", "guard_tower" }, Medium = { "gun_turret" }, Large = { "heavy_turret" } };
            var s0 = LoadoutSlot.Tower(SlotSize.Small, 0);
            var s1 = LoadoutSlot.Tower(SlotSize.Small, 1);
            var m0 = LoadoutSlot.Tower(SlotSize.Medium, 0);
            var l0 = LoadoutSlot.Tower(SlotSize.Large, 0);
            Assert.IsTrue(BaseLayout.Move(loadout, catalog, s0, s1));
            CollectionAssert.AreEqual(new[] { "guard_tower", "aa_turret" }, loadout.Small, "two small towers swap");
            Assert.IsFalse(BaseLayout.Move(loadout, catalog, l0, s0), "a large tower does not go into a small slot");
            Assert.IsTrue(BaseLayout.Move(loadout, catalog, s0, m0), "a small tower into a medium slot");
            Assert.AreEqual("guard_tower", BaseLayout.At(loadout, m0));
            Assert.IsNull(BaseLayout.At(loadout, s0), "the medium tower cannot go back into the small slot: it is left empty");
            Assert.AreEqual("aa_turret", BaseLayout.At(loadout, s1), "the others stay where they are");
            Assert.AreEqual(0, BaseLayout.Placed(loadout, "gun_turret"), "the displaced medium tower left the camp");
            Assert.AreEqual(1, BaseLayout.Placed(loadout, "guard_tower"), "and the moved one is not doubled");
            loadout.Outpost[0] = "guard_tower";
            Assert.IsFalse(BaseLayout.Move(loadout, catalog, LoadoutSlot.Outpost(0), LoadoutSlot.Tower(SlotSize.Small, 5)), "moving out would leave the outpost short");
        }

        [Test]
        public void OnlyAValidLayoutIsSavedAndAnEmptyCampStaysEmpty()
        {
            var catalog = Catalog;
            var messy = new BaseLoadout
            {
                HqLevel = 9,
                Small = { "heavy_turret", "aa_turret", "nonsense", "guard_tower", "guard_tower", "guard_tower", "guard_tower", "guard_tower" },
                Medium = { "gun_turret", BaseLoadout.Empty, "light_tank" },
                Utilities = { "guard_tower" },
                Outpost = { "gun_turret" },
            };
            var saved = BaseLayout.ForSaving(messy, catalog);
            Assert.AreEqual(catalog.Base.MaxLevel, saved.HqLevel, "the level is clamped");
            CollectionAssert.AreEqual(new[] { "", "aa_turret", "", "guard_tower", "guard_tower", "guard_tower" }, saved.Small,
                "what does not fit becomes a gap (the others keep their slots) and the list stops at the top level's slots");
            CollectionAssert.AreEqual(new[] { "gun_turret" }, saved.Medium, "trailing gaps dropped");
            Assert.IsEmpty(saved.Utilities, "no utility module is a tower");
            CollectionAssert.AreEqual(new[] { "guard_tower", "gun_turret" }, saved.Outpost, "the outpost keeps two towers that fit");

            PlayerProfile.LoadForTests("{}");
            PlayerProfile.BaseLoadout = BaseLayout.ForSaving(new BaseLoadout { HqLevel = 2 }, catalog);
            PlayerProfile.LoadForTests(PlayerProfile.JsonForTests());
            var back = PlayerProfile.BaseLoadout;
            // Prompt 14 F: no level to choose any more; the base stands at the level the campaign has opened.
            Assert.AreEqual(Campaign.HqLevelCap, back.HqLevel);
            Assert.IsEmpty(back.Towers, "a camp cleared on the base screen does not come back as the default");

            var gaps = new BaseLoadout { HqLevel = 4, Small = { BaseLoadout.Empty, "aa_turret" }, Large = { "heavy_turret" } };
            PlayerProfile.BaseLoadout = BaseLayout.ForSaving(gaps, catalog);
            PlayerProfile.LoadForTests(PlayerProfile.JsonForTests());
            CollectionAssert.AreEqual(new[] { "", "aa_turret" }, PlayerProfile.BaseLoadout.Small, "a gap survives the save");
            CollectionAssert.AreEqual(new[] { "heavy_turret" }, PlayerProfile.BaseLoadout.Large);
        }
    }
}
