using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 14 I: every tower, branch, utility module, the HQ and every fixed defence has a line icon
    /// of its own (TowerIcons), one that exists, that no vehicle, support or vehicle class uses, and that
    /// every card and tag picks up through CardIcons and VehicleCardData.
    /// </summary>
    public class TowerIconTests
    {
        [SetUp]
        public void TestProfile() => PlayerProfile.LoadForTests("{}");

        [TearDown]
        public void RestoreProfile() => PlayerProfile.Load();

        [Test]
        public void EveryStructureHasALineIconOfItsOwn()
        {
            var catalog = GameContent.LoadCatalog();
            bool Structure(VehicleDef v) => v.Fort != null || v.Static || v.BranchOf != null && Structure(catalog.Vehicles[v.BranchOf]);
            var structures = catalog.Vehicles.Values.Where(Structure).ToList();
            Assert.Greater(structures.Count(v => v.BranchOf == null), 20, "the towers, modules, HQ and fixed defences");

            // Every icon a vehicle, a support or a vehicle class shows.
            var taken = new Dictionary<string, string>();
            foreach (var v in catalog.Vehicles.Values.Where(v => !Structure(v))) taken[CardIcons.For(v.Id)] = v.Id;
            foreach (var id in catalog.Supports.Keys) taken[CardIcons.For(id)] = id;
            foreach (UnitClass c in Enum.GetValues(typeof(UnitClass))) taken[MenuScreen.ClassIcon(c)] = "class " + c;

            var byIcon = new Dictionary<string, string>();
            foreach (var v in structures)
            {
                var icon = TowerIcons.For(v.Id);
                Assert.IsNotNull(icon, v.Id + ": no tower icon");
                Assert.IsTrue(Icons.Exists(icon), $"{v.Id}: icon {icon} is not drawn");
                Assert.IsFalse(taken.TryGetValue(icon, out var owner), $"{v.Id}: {icon} is {owner}'s icon");
                Assert.AreEqual(icon, CardIcons.For(v.Id), v.Id + ": CardIcons");
                // A branch shows its own icon by its letter (tower-branch C.4) where one is drawn, else its tower's.
                if (v.BranchOf != null)
                    Assert.AreEqual(MachineBrigade.Game.Rendering.TowerArt.BranchIcon(v.Id, TowerIcons.For(v.BranchOf), Icons.Exists) ?? TowerIcons.For(v.BranchOf),
                        icon, v.Id + ": a branch's icon");
                if (v.Fort != null) Assert.AreEqual(icon, VehicleCardData.From(v).ClassIcon, v.Id + ": the card's corner icon");
                // One icon a structure; the rail supergun is the fortress super gun on rails.
                if (v.BranchOf == null && v.Id != "rail_supergun")
                {
                    Assert.IsFalse(byIcon.TryGetValue(icon, out var other), $"{v.Id} and {other} share {icon}");
                    byIcon[icon] = v.Id;
                }
            }
            Assert.IsNull(TowerIcons.For("main_battle_tank"), "a vehicle is not a structure");

            // The ones the owner named: the EW tower showed a tank, the AA tower the AA vehicle's icon.
            Assert.AreEqual("t_ew", CardIcons.For("ew_tower"));
            Assert.AreEqual("t_aa", CardIcons.For("aa_turret"));
            Assert.AreNotEqual(CardIcons.For("aa_vehicle"), CardIcons.For("aa_turret.flak"));
        }
    }
}
