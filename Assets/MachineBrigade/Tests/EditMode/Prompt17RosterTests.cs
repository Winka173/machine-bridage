using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 17 D, the roster review: the merged cards (A-10 into the attack jet, Ka-52 into the attack helicopter,
    /// the ATGM carrier into the FPV carrier, the sapper into the engineer, the hidden gun pit into the gun turret),
    /// the save migration (the higher rank, the refunds, the base slots and the tower equipment), the merged cards'
    /// data and kept models, the heavy tank's two rounds, and the follow-ups (Lighthouse Bay's long map, the
    /// hovercraft escort's boat).
    /// </summary>
    public class Prompt17RosterTests
    {
        [TearDown]
        public void Restore()
        {
            Progression.TestUnlockAll = true;
            PlayerProfile.Load();
        }

        private static readonly string[] Gone = { "tank_buster", "heavy_attack_heli", "atgm_carrier", "sapper", "gun_pit" };

        [Test]
        public void MergedVehicleCardsMoveRanksUnlocksAndRefunds()
        {
            // A-10 at rank 6 with 10 blueprints over a rank-3 attack jet; a Ka-52 bought for coins at rank 4; the ATGM
            // carrier and the sapper unlocked in the campaign. A roster-1 save (the earlier merges already done).
            PlayerProfile.LoadForTests("{\"coins\":0,\"rosterVersion\":1,\"gearVersion\":4,\"owned\":[\"heavy_attack_heli\"]," +
                                       "\"unlocked\":[\"atgm_carrier\",\"sapper\",\"attack_jet\"]," +
                                       "\"rankIds\":[\"tank_buster\",\"attack_jet\",\"heavy_attack_heli\"],\"ranks\":[6,3,4],\"prints\":[10,2,1]}");
            Assert.AreEqual(6, PlayerProfile.Rank("attack_jet"), "the attack jet takes the A-10's higher rank");
            Assert.AreEqual(10 + 2 + CardRanks.BlueprintsSpent(3), PlayerProfile.Blueprints("attack_jet"), "and its blueprints, and the lower rank's");
            Assert.AreEqual(4, PlayerProfile.Rank("attack_helicopter"), "the attack helicopter takes the Ka-52's rank");
            Assert.AreEqual(3500 + CardRanks.CoinsSpent(3) + CardRanks.CoinsSpent(1), PlayerProfile.Coins,
                "the Ka-52's price comes back, with the coins spent on each lower rank");
            Assert.IsFalse(PlayerProfile.Owns("heavy_attack_heli"));
            Progression.TestUnlockAll = false;
            Assert.IsTrue(PlayerProfile.IsUnlocked("attack_helicopter"), "a Ka-52 owner has the attack helicopter");
            Assert.IsTrue(PlayerProfile.IsUnlocked("fpv_carrier"), "the ATGM carrier's unlock is the FPV carrier's");
            Assert.IsTrue(PlayerProfile.IsUnlocked("engineer_vehicle"), "the sapper's is the engineer's");
            foreach (var id in Gone) Assert.IsFalse(PlayerProfile.IsUnlocked(id), id);
            Progression.TestUnlockAll = true;

            // Saved decks and loadouts read the card each became; the migration runs once.
            Assert.AreEqual("attack_jet", CardMerges.Resolve("tank_buster"));
            Assert.AreEqual("attack_helicopter", CardMerges.Resolve("heavy_attack_heli"));
            Assert.AreEqual("fpv_carrier", CardMerges.Resolve("atgm_carrier"));
            Assert.AreEqual("engineer_vehicle", CardMerges.Resolve("sapper"));
            Assert.AreEqual("gun_turret", CardMerges.Resolve("gun_pit"));
            var coins = PlayerProfile.Coins;
            PlayerProfile.LoadForTests(PlayerProfile.JsonForTests());
            Assert.AreEqual(coins, PlayerProfile.Coins, "a migrated save is not refunded twice");
        }

        [Test]
        public void GunPitPlayersGetGunTurretsWithTheirSlotsAndEquipment()
        {
            // Gun pit rank 7 (branch chosen) wearing a weapon piece (1) and a structure piece (2); the gun turret at rank 2
            // already wears a structure piece (3). The pit stands in a plan's slot, the outpost and a map's own set-up.
            int w = (int)GearSlot.TowerWeapon, s = (int)GearSlot.TowerStructure;
            var json = "{\"coins\":0,\"rosterVersion\":1,\"gearVersion\":4,\"baseVersion\":3," +
                       "\"rankIds\":[\"gun_pit\",\"gun_turret\"],\"ranks\":[7,2],\"prints\":[5,0]," +
                       "\"branchTowers\":[\"gun_pit\"],\"branchChoices\":[\"gun_pit.ambush\"]," +
                       $"\"gear\":[{{\"id\":1,\"slot\":{w},\"rarity\":1,\"level\":1}},{{\"id\":2,\"slot\":{s},\"rarity\":1,\"level\":1}},{{\"id\":3,\"slot\":{s},\"rarity\":1,\"level\":1}}]," +
                       "\"towerGearIds\":[\"gun_pit\",\"gun_turret\"],\"towerGear\":[1,2,0,0,3,0]," +
                       "\"baseMedium\":[\"gun_pit\"]," +
                       "\"basePlans\":[{\"places\":[{\"place\":0,\"size\":1,\"ordinal\":0,\"tower\":\"gun_pit\"}],\"outpost\":[\"gun_pit\",\"guard_tower\"]," +
                       "\"custom\":[{\"map\":\"ashfield\",\"small\":[],\"medium\":[\"gun_pit\",\"c_ram\"],\"large\":[],\"utilities\":[]}]}]}";
            PlayerProfile.LoadForTests(json);
            Assert.AreEqual(7, PlayerProfile.Rank("gun_turret"), "the turret takes the pit's higher rank");
            Assert.AreEqual(5 + CardRanks.BlueprintsSpent(2), PlayerProfile.Blueprints("gun_turret"));
            Assert.AreEqual(1, PlayerProfile.TowerEquipped("gun_turret", GearSlot.TowerWeapon)?.id, "the pit's weapon piece goes into the turret's empty slot");
            Assert.AreEqual(3, PlayerProfile.TowerEquipped("gun_turret", GearSlot.TowerStructure)?.id, "the turret keeps its own structure piece");
            var spare = PlayerProfile.GearOwned.FirstOrDefault(g => g.id == 2);
            Assert.IsNotNull(spare, "the pit's other piece is still owned");
            Assert.IsNull(PlayerProfile.TowerWearing(spare), "and back in the bag, worn by nothing");
            var saved = PlayerProfile.JsonForTests();
            StringAssert.DoesNotContain("gun_pit", saved, "no slot, outpost, set-up, branch or equipment list names the pit");
            StringAssert.Contains("\"tower\":\"gun_turret\"", saved, "the plan's slot holds the turret");
            Assert.IsNull(PlayerProfile.TowerBranch("gun_turret"), "the pit's branch choice is not the turret's");
        }

        [Test]
        public void TheMergedCardsKeepBothWeaponSetsAndTheOtherModel()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var id in Gone)
            {
                Assert.IsFalse(catalog.Vehicles.ContainsKey(id), $"{id} is out of the catalog");
                Assert.IsFalse(MatchSettings.AllVehicles.Contains(id), $"{id} is no card");
            }
            var jet = catalog.Vehicle("attack_jet");
            var weapons = jet.Mounts.Select(m => m.Weapon.Id).ToList();
            CollectionAssert.IsSubsetOf(new[] { "jet_cannon", "s8_pods", "jet_bombs", "kh29", "r60" }, weapons, "gun, rockets, bombs, anti-tank missiles, self-defence");
            CollectionAssert.Contains(jet.AltModels.ToList(), "tank_buster");
            var heli = catalog.Vehicle("attack_helicopter");
            Assert.IsTrue(heli.Standoff, "the Ka-52's stand-off");
            Assert.AreEqual(55f, heli.Weapon.Range, 0.01f, "anti-tank missiles from 55 m");
            Assert.IsTrue(heli.Mounts.Any(m => m.Weapon.CanTarget(true) && m.Weapon.Projectile == ProjectileKind.Missile), "and anti-air missiles to defend itself");
            CollectionAssert.Contains(heli.AltModels.ToList(), "heavy_attack_heli");
            var engineer = catalog.Vehicle("engineer_vehicle");
            Assert.IsNotNull(engineer.RepairAura, "the engineer repairs (vehicles, and towers at half the rate) and clears mines");
            Assert.IsNull(engineer.RearmAura, "it does not rearm");
            CollectionAssert.Contains(engineer.AltModels.ToList(), "sapper");
            foreach (var model in jet.AltModels.Concat(heli.AltModels).Concat(engineer.AltModels))
                Assert.IsNotNull(UnityEngine.Resources.Load<UnityEngine.GameObject>("Models/" + model), $"the {model} model is kept");
            // The twin tank hunts tanks, the heavy tank breaks through.
            var twin = catalog.Vehicle("twin_tank");
            var heavy = catalog.Vehicle("heavy_tank");
            Assert.AreEqual(2, twin.Weapon.Burst, "two 120 mm rounds as one volley");
            Assert.AreEqual(120f, twin.Weapon.Size, 0.01f);
            // The balance pass after prompt 18 (B.1): 7 -> 5.5 s, still the longest wait of a heavy tank's main gun.
            Assert.GreaterOrEqual(twin.Weapon.Cooldown, 5f, "a long reload between its volleys");
            Assert.AreEqual(3, twin.Armour.Front);
            Assert.AreEqual(4, heavy.Armour.Front);
            Assert.AreEqual(3, heavy.Armour.Side);
            Assert.Greater(twin.Speed, heavy.Speed);
            Assert.Greater(twin.TurretTurnRate, heavy.TurretTurnRate);
            Assert.IsNotNull(heavy.Weapon.HeRound, "the heavy tank's gun has a high-explosive round");
        }

        [Test]
        public void TheHeavyTankLoadsHighExplosiveForStructuresAndLightVehicles()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), 1);
            var heavy = world.SpawnVehicle("heavy_tank", 0, new Vector2(0f, 0f), 0f);
            var gun = heavy.Arms[0];
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(-10f, 25f), 3.14f);
            var car = world.SpawnVehicle("armored_car", 1, new Vector2(0f, 25f), 3.14f);
            var tower = world.SpawnVehicle("guard_tower", 1, new Vector2(10f, 25f), 3.14f);
            Assert.AreEqual("gun_152", world.Combat.RoundFor(gun, tank.Id, tank).Id, "armour-piercing at a battle tank");
            Assert.AreEqual("gun_152_he", world.Combat.RoundFor(gun, car.Id, car).Id, "high explosive at a light vehicle");
            Assert.AreEqual("gun_152_he", world.Combat.RoundFor(gun, tower.Id, tower).Id, "and at a tower");
            Assert.AreSame(tank.Arms[0], world.Combat.RoundFor(tank.Arms[0], car.Id, car), "a gun with one round keeps it");
        }

        [Test]
        public void LighthouseBayHasALongSiegeMapAndTheHovercraftEscortsRideMissileBoats()
        {
            var map = GameContent.LoadMap("lighthousebay_long");
            Assert.IsTrue(map.IsLong);
            Assert.AreEqual(300f, map.Width, 0.01f);
            Assert.That(map.Length, Is.InRange(450f, 500f));
            Assert.AreEqual("missile_boat", GameContent.LoadCatalog().Vehicle("hover_gunboat").Model);
        }
    }
}
