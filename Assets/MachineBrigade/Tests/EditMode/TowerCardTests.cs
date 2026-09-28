using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Tower cards: a branch def takes its tower's data with its own changes on top, every tower
    /// lists its branches, the branch is chosen from rank 7 (free the first time, coins to change),
    /// and a loadout tower fights as its branch and with its card's rank.
    /// </summary>
    public class TowerCardTests
    {
        [TearDown]
        public void Restore() => PlayerProfile.Load();

        [Test]
        public void ABranchInheritsItsTowerAndChangesItsWeapons()
        {
            var catalog = GameContent.LoadCatalog();
            var tower = catalog.Vehicles["aa_turret"];
            var flak = catalog.Vehicles["aa_turret.flak"];
            Assert.AreEqual("aa_turret", flak.BranchOf);
            Assert.AreEqual("aa_turret", flak.CardId, "it counts as its tower's card");
            Assert.AreEqual(tower.MaxHp, flak.MaxHp, "its tower's health");
            Assert.AreEqual(tower.Model, flak.Model, "and model");
            Assert.AreEqual(tower.Fort.Size, flak.Fort.Size, "a branch keeps its tower's size");
            Assert.AreEqual("flak_quad", flak.Weapon.Id, "with its own weapon");
            CollectionAssert.AreEqual(new[] { "aa_turret.flak", "aa_turret.sam" }, TowerCards.Branches(catalog, "aa_turret"));
            Assert.IsFalse(TowerCards.All(catalog).Contains("aa_turret.flak"), "a branch is not a card of its own");
        }

        [Test]
        public void TheBranchIsChosenFromRankSevenAndCostsCoinsToChange()
        {
            PlayerProfile.LoadForTests("{\"coins\":1000,\"rankIds\":[\"aa_turret\"],\"ranks\":[6],\"prints\":[0]}");
            Assert.IsFalse(PlayerProfile.TryChooseBranch("aa_turret", "aa_turret.flak"), "not below rank 7");
            PlayerProfile.LoadForTests("{\"coins\":1000,\"rankIds\":[\"aa_turret\"],\"ranks\":[7],\"prints\":[0]}");
            Assert.IsTrue(PlayerProfile.TryChooseBranch("aa_turret", "aa_turret.flak"));
            Assert.AreEqual(1000, PlayerProfile.Coins, "the first choice is free");
            Assert.AreEqual("aa_turret.flak", PlayerProfile.TowerBranch("aa_turret"));
            Assert.IsTrue(PlayerProfile.TryChooseBranch("aa_turret", "aa_turret.sam"));
            Assert.AreEqual(1000 - PlayerProfile.BranchSwapCoins, PlayerProfile.Coins, "changing it costs coins");
            Assert.AreEqual("aa_turret.sam", PlayerProfile.BaseLoadout.DefFor("aa_turret"), "the loadout takes the branch into battle");
        }

        [Test]
        public void ALoadoutTowerFightsAsItsBranchWithItsCardsRank()
        {
            var catalog = GameContent.LoadCatalog();
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: 2);
            world.SetBoosts(0, def => def.Fort != null && def.CardId == "aa_turret" ? new VehicleBoost(1.3f, 1.3f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f) : VehicleBoost.None);
            var loadout = new BaseLoadout { HqLevel = 5, Small = { "aa_turret" } };
            loadout.Branches["aa_turret"] = "aa_turret.flak";
            var b = world.Bases.Establish(0, loadout, BaseRole.Anchor);
            var slot = b.Slots.First(s => s.Tower != null && s.Def.Kind == HardpointKind.Tower);
            Assert.AreEqual("aa_turret.flak", slot.Tower, "raised as its branch");
            Assert.IsTrue(world.TryGetVehicle(slot.Structure, out var raised));
            Assert.AreEqual(catalog.Vehicles["aa_turret.flak"].MaxHp * 1.3f, raised.MaxHp, 1f, "a loadout tower carries its card's boost");
        }
    }
}
