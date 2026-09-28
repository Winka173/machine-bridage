using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The base screen, built without a panel: a frame for every hardpoint of the map's camp
    /// (sized by class, utility and closed ones marked), only the slots a tower fits light up
    /// while it is carried, a tap places it, and Save writes a valid layout to the profile. The
    /// diagram's layout keeps frames apart and inside the panel.
    /// </summary>
    public class BaseScreenTests
    {
        [SetUp]
        public void TestProfile() => PlayerProfile.LoadForTests("{}");

        [TearDown]
        public void RestoreProfile() => PlayerProfile.Load();

        private static int Count(VisualElement root, string className) => root.Query(className: className).ToList().Count;

        [Test]
        public void EveryHardpointOfTheCampHasAFrame()
        {
            var catalog = GameContent.LoadCatalog();
            var screen = new BaseScreen(catalog, null, null);
            foreach (var map in MatchSettings.AllMaps)
            {
                screen.ShowMap(map.Id);
                var site = GameContent.LoadMap(map.Id + "_conquest").BaseOf(0);
                Assert.AreEqual(map.Id, screen.MapId);
                Assert.AreEqual(site.Slots.Count, Count(screen.Root, "base-camp-slot"), map.Id + ": a frame a hardpoint");
                Assert.AreEqual(site.Slots.Count, screen.CampSlots.Count);
                Assert.AreEqual(1, Count(screen.Root, "base-hq"), "the HQ");
                foreach (SlotSize size in System.Enum.GetValues(typeof(SlotSize)))
                    Assert.AreEqual(site.Slots.Count(s => s.Class == size), screen.CampSlots.Count(v => v.Element.ClassListContains("size-" + size.ToString().ToLowerInvariant())),
                        $"{map.Id}: {size} frames");
                Assert.AreEqual(site.Slots.Count(s => s.Kind == HardpointKind.Utility), screen.CampSlots.Count(v => v.Element.ClassListContains("utility")), "utility slots marked");
            }
            Assert.AreEqual(2, screen.OutpostSlots.Count, "the outpost's small and medium slot");
            Assert.IsTrue(screen.OutpostSlots[0].Element.ClassListContains("size-small") && screen.OutpostSlots[1].Element.ClassListContains("size-medium"));
        }

        [Test]
        public void SlotsBeyondTheHqLevelAreClosed()
        {
            var catalog = GameContent.LoadCatalog();
            var screen = new BaseScreen(catalog, null, null);
            screen.ShowMap("ashfield");
            screen.SetLevel(1);
            var rules = catalog.Base;
            var open = rules.Slots(1, SlotSize.Small) + rules.Slots(1, SlotSize.Medium) + rules.Slots(1, SlotSize.Large) + rules.UtilitySlots(1);
            Assert.AreEqual(screen.CampSlots.Count - open, screen.CampSlots.Count(v => v.Element.ClassListContains("closed")), "closed = beyond level 1");
            Assert.IsTrue(screen.Dirty, "a level change waits for Save");
        }

        [Test]
        public void OnlyTheSlotsATowerFitsLightUpAndATapPlacesIt()
        {
            var catalog = GameContent.LoadCatalog();
            string note = null;
            var screen = new BaseScreen(catalog, (text, _) => note = text, null);
            screen.ShowMap("ashfield");
            screen.SetLevel(5);
            screen.TapTower("heavy_turret");
            var lit = screen.CampSlots.Where(v => v.Element.ClassListContains("lit")).ToList();
            Assert.AreEqual(catalog.Base.Slots(5, SlotSize.Large), lit.Count, "a large tower: only the large slots");
            Assert.IsTrue(lit.All(v => v.Slot.Kind == LoadoutSlotKind.Tower && v.Slot.Size == SlotSize.Large));
            Assert.IsFalse(screen.OutpostSlots.Any(v => v.Element.ClassListContains("lit")), "nor the outpost's");
            screen.TapTower("heavy_turret");
            screen.TapTower("guard_tower");
            Assert.AreEqual(screen.CampSlots.Count(v => v.Open && !v.Utility) + 2, screen.CampSlots.Concat(screen.OutpostSlots).Count(v => v.Element.ClassListContains("lit")),
                "a small tower fits every open tower slot and the outpost's two");

            screen.TapSlot(LoadoutSlot.Tower(SlotSize.Large, 1));
            Assert.AreEqual("guard_tower", BaseLayout.At(screen.Layout, LoadoutSlot.Tower(SlotSize.Large, 1)), "the tap placed it");
            Assert.IsNotNull(note);
            Assert.IsFalse(screen.CampSlots.Any(v => v.Element.ClassListContains("lit")), "nothing is carried any more");

            // Slot first, then the tower: a medium tower does not go into a small slot.
            screen.TapSlot(LoadoutSlot.Tower(SlotSize.Small, 0));
            screen.TapTower("gun_turret");
            Assert.AreNotEqual("gun_turret", BaseLayout.At(screen.Layout, LoadoutSlot.Tower(SlotSize.Small, 0)));
            screen.TapTower("mg_bunker");
            Assert.AreEqual("mg_bunker", BaseLayout.At(screen.Layout, LoadoutSlot.Tower(SlotSize.Small, 0)));

            Assert.IsTrue(screen.Dirty);
            screen.Save();
            Assert.IsFalse(screen.Dirty);
            var saved = PlayerProfile.BaseLoadout;
            Assert.AreEqual("guard_tower", saved.Large[1], "Save wrote the layout");
            Assert.AreEqual("mg_bunker", saved.Small[0]);
            Assert.AreEqual(5, saved.HqLevel);
        }

        [Test]
        public void UtilitySlotsTakeModulesOnly()
        {
            // The utility modules are in the catalog: the utility slots are live, and only modules light them up.
            var catalog = GameContent.LoadCatalog();
            var screen = new BaseScreen(catalog, null, null);
            screen.ShowMap("ashfield");
            Assert.IsFalse(screen.CampSlots.Any(v => v.Element.ClassListContains("soon")));
            screen.TapTower("guard_tower");
            Assert.IsFalse(screen.CampSlots.Any(v => v.Utility && v.Element.ClassListContains("lit")), "a tower does not go into a utility slot");
            screen.TapTower("repair_bay");
            var lit = screen.CampSlots.Where(v => v.Element.ClassListContains("lit")).ToList();
            Assert.AreEqual(catalog.Base.UtilitySlots(5), lit.Count, "a module: the open utility slots only");
            Assert.IsTrue(lit.All(v => v.Utility));
            screen.TapSlot(LoadoutSlot.Utility(0));
            Assert.AreEqual("repair_bay", BaseLayout.At(screen.Layout, LoadoutSlot.Utility(0)));
            CollectionAssert.Contains(BaseLayout.ForSaving(screen.Layout, catalog).Utilities, "repair_bay", "and the module is saved");
        }

        [Test]
        public void TheDiagramKeepsFramesApartAndInside()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var map in MatchSettings.AllMaps)
            {
                var site = GameContent.LoadMap(map.Id + "_conquest").BaseOf(0);
                var world = new[] { site.Hq }.Concat(site.Slots.Select(s => s.Position)).Select(CampLayout.ToUnity).ToList();
                var sizes = new[] { 86f }.Concat(site.Slots.Select(s => s.Class switch { SlotSize.Small => 72f, SlotSize.Medium => 84f, _ => 96f })).ToList();
                foreach (var panel in new[] { new Vector2(544f, 440f), new Vector2(864f, 440f) })
                {
                    var fit = CampLayout.Arrange(CampLayout.ToUnity(site.Hq), site.Heading, world, sizes, panel, 6f, 10f);
                    Assert.IsFalse(CampLayout.Overlaps(fit.Centres, sizes), $"{map.Id} at {panel}: frames overlap");
                    for (var i = 0; i < sizes.Count; i++)
                    {
                        var c = fit.Centres[i];
                        Assert.IsTrue(c.x - sizes[i] / 2 >= -0.5f && c.x + sizes[i] / 2 <= panel.x + 0.5f && c.y - sizes[i] / 2 >= -0.5f && c.y + sizes[i] / 2 <= panel.y + 0.5f,
                            $"{map.Id} at {panel}: frame {i} inside");
                    }
                    // The front is up: the slots lie ahead of the HQ.
                    var ahead = fit.Centres.Skip(1).Count(c => c.y < fit.Centres[0].y);
                    Assert.Greater(ahead, site.Slots.Count / 2, $"{map.Id}: the camp faces up");
                }
            }
        }
    }
}
