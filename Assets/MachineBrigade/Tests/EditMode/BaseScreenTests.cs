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
    /// The Base screen (prompt 14), built without a panel: a slot for every hardpoint of the map's camp at its place
    /// (sized by class, utility ones as hexagons, closed ones by the HQ level), only the slots a tower fits light up
    /// while it is carried, a tap places it and the change is saved at once, faces keep their ratio (medium 1.4,
    /// large 2) and never touch, the range cover is the towers' own reach, and the strength shown is the one the
    /// Defend and Endless waves scale with (<see cref="BaseStrength.Score(Catalog, BaseLoadout, System.Func{VehicleDef, VehicleBoost})"/>).
    /// </summary>
    public class BaseScreenTests
    {
        [SetUp]
        public void TestProfile() => PlayerProfile.LoadForTests("{}");

        [TearDown]
        public void RestoreProfile() => PlayerProfile.Load();

        private static int Count(VisualElement root, string className) => root.Query(className: className).ToList().Count;

        [Test]
        public void EveryHardpointOfTheCampHasASlotAndTheClosedOnesFollowTheHqLevel()
        {
            var catalog = GameContent.LoadCatalog();
            var screen = new BaseScreen(catalog, null, null);
            foreach (var map in MatchSettings.AllMaps)
            {
                screen.ShowMap(map.Id);
                var site = BaseSites.CampOf(map.Id);
                Assert.AreEqual(map.Id, screen.MapId);
                Assert.AreEqual(site.Slots.Count, Count(screen.Root, "fc-base-slot"), map.Id + ": a slot a hardpoint");
                Assert.AreEqual(1, Count(screen.Root, "fc-base-hq"), "the HQ");
                foreach (SlotSize size in System.Enum.GetValues(typeof(SlotSize)))
                    Assert.AreEqual(site.Slots.Count(s => s.Class == size && s.Kind == HardpointKind.Tower),
                        screen.CampSlots.Count(v => v.Element.ClassListContains("fc-base-slot--" + size.ToString().ToLowerInvariant())), $"{map.Id}: {size} slots");
                Assert.AreEqual(site.Slots.Count(s => s.Kind == HardpointKind.Utility), screen.CampSlots.Count(v => v.Element.ClassListContains("fc-base-slot--utility")), "utility slots");
                var open = BaseLayout.Camp(site, catalog.Base, Campaign.HqLevelCap);
                Assert.AreEqual(open.Count(s => !s.Open), screen.CampSlots.Count(v => v.Element.ClassListContains("fc-base-slot--closed")), map.Id + ": closed = beyond the HQ level");
            }
        }

        [Test]
        public void OnlyTheSlotsATowerFitsLightUpAndATapPlacesAndSavesIt()
        {
            var catalog = GameContent.LoadCatalog();
            string note = null;
            var screen = new BaseScreen(catalog, (text, _) => note = text, null);
            screen.ShowMap("ashfield");
            var slots = screen.CampSlots;
            screen.TapTower("heavy_turret");
            var lit = slots.Where(v => v.Element.ClassListContains("fc-base-slot--lit")).ToList();
            Assert.AreEqual(slots.Count(v => v.Open && !v.Utility && v.Size == SlotSize.Large), lit.Count, "a large tower: only the large slots");
            Assert.IsTrue(slots.Where(v => !lit.Contains(v)).All(v => v.Element.ClassListContains("fc-base-slot--dim")), "the others dimmed");
            screen.TapTower("heavy_turret");
            screen.TapTower("guard_tower");
            Assert.AreEqual(slots.Count(v => v.Open && !v.Utility), slots.Count(v => v.Element.ClassListContains("fc-base-slot--lit")), "a small tower fits every open tower slot");

            var large = slots.First(v => v.Open && !v.Utility && v.Size == SlotSize.Large);
            screen.TapSlot(large);
            Assert.AreEqual("guard_tower", PlayerProfile.ActivePlan.At("ashfield", BaseSites.CampOf("ashfield"), large.Hardpoint), "the tap placed it");
            Assert.IsNotNull(note);
            Assert.IsFalse(slots.Any(v => v.Element.ClassListContains("fc-base-slot--lit")), "nothing is carried any more");
            PlayerProfile.LoadForTests(PlayerProfile.JsonForTests());
            Assert.AreEqual("guard_tower", PlayerProfile.ActivePlan.At("ashfield", BaseSites.CampOf("ashfield"), large.Hardpoint), "saved at once");

            // Slot first, then the tower: a medium tower does not go into a small slot.
            screen = new BaseScreen(catalog, (text, _) => note = text, null);
            screen.ShowMap("ashfield");
            var small = screen.CampSlots.First(v => v.Open && !v.Utility && v.Size == SlotSize.Small);
            screen.TapSlot(small);
            screen.TapTower("gun_turret");
            Assert.AreNotEqual("gun_turret", PlayerProfile.ActivePlan.At("ashfield", BaseSites.CampOf("ashfield"), small.Hardpoint));
            screen.TapTower("mg_bunker");
            Assert.AreEqual("mg_bunker", PlayerProfile.ActivePlan.At("ashfield", BaseSites.CampOf("ashfield"), small.Hardpoint));

            // The range cover: every tower in an open slot with its own reach from the data.
            screen.ToggleRanges();
            var layout = screen.Layout;
            var towers = BasePlan.ToAssignment(BaseSites.CampOf("ashfield"), layout);
            Assert.AreEqual(towers.Count(t => t != null && catalog.Vehicles[t].Fort.Kind == FortKind.Tower) + towers.Count(t => t != null && catalog.Vehicles[t].Fort.Kind == FortKind.Utility),
                screen.Map.Cover.Count, "a circle for everything placed");
            foreach (var id in towers.Where(t => t != null))
            {
                var (ground, air, _) = BaseRoles.Reach(catalog.Vehicles[layout.DefFor(id)]);
                Assert.IsTrue(screen.Map.Cover.Any(c => Mathf.Approximately(c.ground, ground) && Mathf.Approximately(c.air, air)), id + ": its reach");
            }
        }

        [Test]
        public void UtilitySlotsTakeModulesOnly()
        {
            var catalog = GameContent.LoadCatalog();
            var screen = new BaseScreen(catalog, null, null);
            screen.ShowMap("ashfield");
            screen.TapTower("guard_tower");
            Assert.IsFalse(screen.CampSlots.Any(v => v.Utility && v.Element.ClassListContains("fc-base-slot--lit")), "a tower does not go into a utility slot");
            screen.TapTower("guard_tower");
            screen.TapTower("repair_bay");
            var lit = screen.CampSlots.Where(v => v.Element.ClassListContains("fc-base-slot--lit")).ToList();
            Assert.AreEqual(screen.CampSlots.Count(v => v.Utility && v.Open), lit.Count, "a module: the open utility slots only");
            Assert.IsTrue(lit.All(v => v.Utility));
            screen.TapSlot(lit[0]);
            Assert.AreEqual("repair_bay", PlayerProfile.ActivePlan.At("ashfield", BaseSites.CampOf("ashfield"), lit[0].Hardpoint));
        }

        /// <summary>Prompt 14 B3: a medium slot's face is 1.4 times a small one's, a large one's twice, and on no map do two faces (or the HQ) touch at any zoom.</summary>
        [Test]
        public void SlotFacesKeepTheirRatioAndNeverTouch()
        {
            var catalog = GameContent.LoadCatalog();
            var screen = new BaseScreen(catalog, null, null);
            foreach (var map in MatchSettings.AllMaps)
            {
                var site = BaseSites.CampOf(map.Id);
                screen.ShowMap(map.Id);
                var unit = BaseScreen.FaceMetres(site);
                Assert.Greater(unit, 8f, map.Id + ": faces big enough to read");
                var views = screen.CampSlots;
                foreach (var v in views)
                    Assert.AreEqual(v.Utility ? BaseScreen.UtilityRatio : v.Size switch { SlotSize.Small => 1f, SlotSize.Medium => BaseScreen.MediumRatio, _ => BaseScreen.LargeRatio },
                        BaseScreen.RatioOf(v), 1e-4f);
                for (var i = 0; i < views.Count; i++)
                {
                    var a = site.Slots[views[i].Hardpoint].Position;
                    Assert.GreaterOrEqual(System.Numerics.Vector2.Distance(a, site.Hq), 0.5f * unit * (BaseScreen.RatioOf(views[i]) + BaseScreen.HqRatio), map.Id + ": clear of the HQ");
                    for (var j = i + 1; j < views.Count; j++)
                    {
                        var b = site.Slots[views[j].Hardpoint].Position;
                        Assert.GreaterOrEqual(System.Numerics.Vector2.Distance(a, b), 0.5f * unit * (BaseScreen.RatioOf(views[i]) + BaseScreen.RatioOf(views[j])),
                            $"{map.Id}: slots {views[i].Hardpoint} and {views[j].Hardpoint} apart");
                    }
                }
            }
        }

        /// <summary>Prompt 14 E2: the strength shown is BaseStrength's score of the base the player takes onto that map, rank and equipment in.</summary>
        [Test]
        public void TheStrengthShownIsTheOneTheWavesScaleWith()
        {
            var catalog = GameContent.LoadCatalog();
            var screen = new BaseScreen(catalog, null, null);
            foreach (var map in new[] { "ashfield", "capital", "whiteout" })
            {
                screen.ShowMap(map);
                var expected = BaseStrength.Score(catalog, PlayerProfile.BaseLoadoutFor(map), PlayerProfile.BoostFor);
                Assert.AreEqual(Mathf.RoundToInt(expected).ToString(), screen.StrengthLabel.text, map);
                Assert.AreEqual(expected, screen.Strength, 1e-3f);
            }
            // A stronger base shows a bigger number.
            screen.ShowMap("ashfield");
            var before = screen.Strength;
            var empty = screen.CampSlots.FirstOrDefault(v => v.Open && !v.Utility && v.Size == SlotSize.Large);
            screen.TapTower("heavy_turret");
            screen.TapSlot(empty);
            Assert.GreaterOrEqual(screen.Strength, before);
        }
    }
}
