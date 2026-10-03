using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 14 G: one loadout for every map. The old loadout (version 2, one set of sized lists) becomes the
    /// first plan with nothing changed on any of the twenty maps; the plan lays itself on every camp by place
    /// (a tower whose place a map lacks goes to the nearest slot of its size, and the map is marked); a map set
    /// up on its own keeps its towers when the plan changes; the three plans are apart; Auto-arrange gives a
    /// loadout that fits.
    /// </summary>
    public class BasePlanTests
    {
        [TearDown]
        public void RestoreProfile() => PlayerProfile.Load();

        private static IEnumerable<(string id, BaseSiteDef site)> Camps() =>
            MatchSettings.AllMaps.Select(m => (m.Id, BaseSites.CampOf(m.Id))).Where(c => c.Item2 != null);

        private static List<string> Trim(IEnumerable<string> list)
        {
            var l = list.Select(x => x ?? "").ToList();
            while (l.Count > 0 && l[l.Count - 1] == "") l.RemoveAt(l.Count - 1);
            return l;
        }

        [Test]
        public void TheOldLoadoutBecomesThePlanAndNoMapChanges()
        {
            // A version 2 profile with its own base: a gap in the small slots, one module, its own outpost.
            string[] small = { "mg_bunker", "aa_turret", "guard_tower", "", "ew_tower", "cp_relay" };
            string[] medium = { "atgm_tower", "gun_turret", "rocket_turret" };
            string[] large = { "missile_battery", "heavy_turret" };
            string[] utilities = { "repair_bay" };
            string Json(IEnumerable<string> l) => "[" + string.Join(",", l.Select(x => "\"" + x + "\"")) + "]";
            PlayerProfile.LoadForTests("{\"baseVersion\":2,\"baseEdited\":true,\"baseLevel\":5,\"baseSmall\":" + Json(small) + ",\"baseMedium\":" + Json(medium) +
                                       ",\"baseLarge\":" + Json(large) + ",\"baseUtilities\":" + Json(utilities) + ",\"baseOutpost\":[\"mg_bunker\",\"atgm_tower\"]}");
            var plan = PlayerProfile.ActivePlan;
            var custom = 0;
            foreach (var (id, site) in Camps())
            {
                var now = plan.Resolve(id, site, 5);
                CollectionAssert.AreEqual(Trim(small), Trim(now.Small), id + ": small slots as before");
                CollectionAssert.AreEqual(Trim(medium), Trim(now.Medium), id + ": medium slots as before");
                CollectionAssert.AreEqual(Trim(large), Trim(now.Large), id + ": large slots as before");
                CollectionAssert.AreEqual(Trim(utilities), Trim(now.Utilities), id + ": modules as before");
                CollectionAssert.AreEqual(new[] { "mg_bunker", "atgm_tower" }, now.Outpost, id + ": the outpost");
                if (plan.Custom.ContainsKey(id)) custom++;
            }
            Debug.Log($"[BasePlan] migrated: {plan.Places.Count} places, {custom} of {Camps().Count()} maps kept on their own");
            Assert.Less(custom, Camps().Count(), "the plan's own map needs no set-up of its own");
            Assert.AreEqual(PlayerProfile.BasePlanCount, Enumerable.Range(0, PlayerProfile.BasePlanCount).Count(i => PlayerProfile.BasePlanAt(i) != null));
            CollectionAssert.AreEquivalent(plan.Places, PlayerProfile.BasePlanAt(1).Places, "the other plans start as copies");
            // Saved and read back, the plans are the same.
            PlayerProfile.SaveBasePlans();
            var json = PlayerProfile.JsonForTests();
            PlayerProfile.LoadForTests(json);
            CollectionAssert.AreEquivalent(plan.Places, PlayerProfile.ActivePlan.Places, "the plan survives a save");
            Assert.AreEqual(custom, PlayerProfile.ActivePlan.Custom.Count);
        }

        [Test]
        public void ThePlanFitsEveryMapAndMapsOfTheirOwnKeepTheirs()
        {
            PlayerProfile.LoadForTests("{}");
            var catalog = GameContent.LoadCatalog();
            var camps = Camps().ToList();
            Assert.AreEqual(MatchSettings.AllMaps.Count(), camps.Count, "every map has a camp");
            // Auto-arrange on the first map: the AI's pick among the towers, laid out by place.
            var (firstId, firstSite) = camps[0];
            var ai = BaseLoadout.ForAi(catalog, "Normal", "default", 3, 5, id => id != "ew_tower");
            var plan = new BasePlan();
            plan.FromCamp(firstSite, BasePlan.ToAssignment(firstSite, ai));
            Assert.IsFalse(plan.Places.Values.Contains("ew_tower"), "only the towers allowed");
            foreach (var (id, site) in camps)
            {
                var towers = plan.Assign(site, out var misfit);
                var keys = SlotPlaces.Keys(site);
                for (var i = 0; i < towers.Length; i++)
                {
                    if (towers[i] == null) continue;
                    var slot = site.Slots[i];
                    var def = catalog.Vehicles[towers[i]];
                    Assert.IsTrue(slot.Kind == HardpointKind.Utility ? def.Fort.Kind == FortKind.Utility : def.Fort.Kind == FortKind.Tower && def.Fort.Fits(slot.Class),
                        $"{id}: {towers[i]} fits slot {i} ({keys[i]})");
                }
                // Every tower of the plan stands on every map (all camps have the same slot counts), moved at most.
                CollectionAssert.AreEquivalent(plan.Places.Values.OrderBy(x => x), towers.Where(t => t != null).OrderBy(x => x), id + ": every planned tower placed");
                if (id == firstId) Assert.IsFalse(misfit, "the map it was laid out on fits exactly");
            }
            // A map of its own keeps its towers when the plan changes.
            var (otherId, otherSite) = camps[1];
            plan.SetCustom(otherId, otherSite, true, 5);
            var before = plan.Resolve(otherId, otherSite, 5);
            plan.Set(firstId, firstSite, 0, "guard_tower");
            var after = plan.Resolve(otherId, otherSite, 5);
            CollectionAssert.AreEqual(before.Small, after.Small, "its own set-up is kept");
            Assert.AreEqual("guard_tower", plan.At(firstId, firstSite, 0), "the plan changed");
            // The three plans are apart.
            PlayerProfile.BasePlanAt(0).Places.Clear();
            PlayerProfile.BasePlanAt(1).Places[new PlaceKey(SlotPlace.Gate, SlotSize.Small, 0)] = "mg_bunker";
            Assert.AreEqual(0, PlayerProfile.BasePlanAt(0).Places.Count);
            PlayerProfile.ActiveBasePlan = 1;
            Assert.AreEqual("mg_bunker", PlayerProfile.ActivePlan.Places[new PlaceKey(SlotPlace.Gate, SlotSize.Small, 0)]);
        }
    }
}
