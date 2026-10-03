using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Tower equipment: the three tower slots and their catalogue, which tower types a piece works
    /// for, one loadout per tower type shared by all its towers (and its branch), the tower caps,
    /// each tower line in battle (Fire Link, Counter-Battery, Modular, Smoke Launchers, Backup
    /// Generator), tower pieces from crates and the odds, and the loadouts across a save.
    /// </summary>
    public class TowerGearTests
    {
        [SetUp]
        public void SetUp() => PlayerProfile.ResetForTests();

        [TearDown]
        public void TearDown() => PlayerProfile.Load();

        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static GearItem Piece(GearSlot slot, string baseType, Rarity rarity = Rarity.Rare, int level = 1) =>
            new() { slot = (int)slot, rarity = (int)rarity, level = level, baseType = baseType };

        private static VehicleBoost Traits(params GearTrait[] traits) =>
            new(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f, null, traits);

        /// <summary>An open field with nothing on it, big enough to keep a gun out of everything's reach.</summary>
        private static SimWorld Field(float size = 240f) =>
            new(Catalog, new MapDefinition("field", size,
                new[] { new TeamStart(0, new Vector2(-size * 0.4f, -size * 0.4f)), new TeamStart(1, new Vector2(size * 0.4f, size * 0.4f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        private static List<SimEvent> Run(SimWorld world, float seconds)
        {
            var events = new List<SimEvent>();
            var steps = (int)(seconds / TestWorlds.Step + 0.5f);
            for (var i = 0; i < steps; i++)
            {
                world.Step(TestWorlds.Step);
                events.AddRange(world.Events);
                world.ClearEvents();
            }
            return events;
        }

        private static bool Procced(IEnumerable<SimEvent> events, TraitId id) =>
            events.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == GearKeys.Trait(id));

        // ------------------------------------------------------------------ catalogue and pieces

        [Test]
        public void TowerPiecesHaveThreeSlotsOfTheirOwn()
        {
            CollectionAssert.AreEqual(new[] { GearSlot.TowerWeapon, GearSlot.TowerStructure, GearSlot.TowerSystems }, Gear.TowerSlots);
            Assert.AreEqual(13, GearCatalog.TowerBases.Length, "13 tower base types");
            foreach (var slot in Gear.TowerSlots)
            {
                Assert.GreaterOrEqual(GearCatalog.TowerBasesFor(slot).Count(), 3, slot + " has a choice of base types");
                Assert.GreaterOrEqual(GearCatalog.TowerTraitsFor(slot).Count(), 3, slot + " offers three traits at Epic");
            }
            foreach (var b in GearCatalog.TowerBases)
            {
                Assert.IsTrue(Gear.IsTower(b.Slot), b.Id);
                Assert.AreSame(b, GearCatalog.Base(b.Id), "found by id like any base type");
            }
            foreach (var id in new[] { TraitId.TowerFireLink, TraitId.TowerCounterBattery, TraitId.TowerModular, TraitId.TowerSmokeLaunchers, TraitId.TowerBackupGenerator })
                Assert.IsTrue(GearCatalog.TowerTraits.Any(t => t.Id == id), id + " is a tower line");
            Assert.AreEqual(GearSlot.TowerWeapon, GearCatalog.Trait(TraitId.TowerFireLink).Slot);
            Assert.AreEqual(GearSlot.Weapon, GearCatalog.Trait(TraitId.Executioner).Slot, "a vehicle trait in a tower pool keeps its vehicle entry");
            Assert.AreEqual(GearSlot.TowerWeapon, GearCatalog.TraitFor(GearSlot.TowerWeapon, "executioner").Slot, "and a tower piece reads its tower entry");
            // The vehicle catalogue and its rolls are untouched.
            Assert.AreEqual(38, GearCatalog.Bases.Length);
            Assert.AreEqual(45, GearCatalog.Traits.Length);
            var rng = new Random(9);
            for (var i = 0; i < 300; i++) Assert.IsFalse(Gear.IsTower(Crates.Roll((Rarity)(i % 5), rng, i + 1).Slot), "a vehicle roll is never a tower piece");
        }

        [Test]
        public void TowerMainStatsFollowTheirBaseTypeAndGrowWithLevel()
        {
            Assert.AreEqual(StatId.Damage, Gear.MainStat(Piece(GearSlot.TowerWeapon, "fortress_barrel")));
            Assert.AreEqual(StatId.FireRate, Gear.MainStat(Piece(GearSlot.TowerWeapon, "ammo_hoist")));
            Assert.AreEqual(StatId.Health, Gear.MainStat(Piece(GearSlot.TowerStructure, "reinforced_concrete")));
            Assert.AreEqual(StatId.DamageTaken, Gear.MainStat(Piece(GearSlot.TowerStructure, "blast_walls")));
            Assert.AreEqual(StatId.Regen, Gear.MainStat(Piece(GearSlot.TowerStructure, "engineer_bay")));
            Assert.AreEqual(StatId.Vision, Gear.MainStat(Piece(GearSlot.TowerSystems, "search_radar")));
            Assert.AreEqual(StatId.TurretRate, Gear.MainStat(Piece(GearSlot.TowerSystems, "traverse_motors")));
            Assert.AreEqual(StatId.MagazineReload, Gear.MainStat(Piece(GearSlot.TowerSystems, "ammo_handling")));
            var cap = Gear.LevelCap[(int)Rarity.Legendary];
            Assert.AreEqual(0.14f * 0.4f, Gear.Value(Piece(GearSlot.TowerWeapon, "fortress_barrel", Rarity.Legendary)), 1e-4f, "40% of the top at level 1");
            Assert.AreEqual(0.14f, Gear.Value(Piece(GearSlot.TowerWeapon, "fortress_barrel", Rarity.Legendary, cap)), 1e-4f, "as a vehicle's gun upgrade");
            Assert.AreEqual(0.095f, Gear.Value(Piece(GearSlot.TowerStructure, "blast_walls", Rarity.Legendary, cap)), 1e-4f, "screens as plating");
            Assert.AreEqual(0.01f, Gear.Value(Piece(GearSlot.TowerStructure, "engineer_bay", Rarity.Legendary, cap)), 1e-5f, "repairs as a repair kit");
            Assert.AreEqual(0.21f, Gear.Value(Piece(GearSlot.TowerSystems, "traverse_motors", Rarity.Legendary, cap)), 1e-4f, "traverse at 1.5 times");
            Assert.IsNotEmpty(Gear.Lines(Piece(GearSlot.TowerSystems, "search_radar")), "its lines read like any piece's");
        }

        [Test]
        public void EveryLineOfARolledTowerPieceWorksWhereverThePieceFits()
        {
            var rng = new Random(11);
            var traits = new HashSet<string>();
            for (var n = 0; n < 1500; n++)
            {
                var rarity = (Rarity)(n % 5);
                var item = Gear.CreateTower(rarity, rng, n + 1);
                Assert.IsTrue(Gear.IsTower(item.Slot));
                var b = Gear.BaseOf(item);
                Assert.IsNotNull(b, "a tower base type");
                Assert.AreEqual(item.Slot, b.Slot);
                Assert.That(item.brand, Is.EqualTo(0).Or.EqualTo(GearCatalog.BulwarkBrand), "no vehicle brand: only the tower brand, Bulwark Engineering");
                Assert.AreEqual(b.NoSubs ? 0 : Gear.SubCount[(int)rarity], item.subs.Count, "its rarity's sub-stats");
                var need = TowerFit.Need(b);
                foreach (var sub in item.subs)
                {
                    Assert.IsTrue(TowerFit.Within(TowerFit.Need(sub.Stat), need), $"{sub.Stat} on {b.Id} asks no more than its base type");
                    Assert.AreNotEqual(Gear.MainStat(item), sub.Stat);
                }
                if (rarity >= Rarity.Epic)
                {
                    var t = GearCatalog.TraitFor(item.Slot, item.trait);
                    Assert.IsNotNull(t, "an Epic tower piece has a trait");
                    Assert.AreEqual(item.Slot, t.Slot, "from its own tower slot's pool");
                    Assert.IsTrue(TowerFit.Within(t.Need, need), $"{t.Key} on {b.Id} asks no more than its base type");
                    traits.Add(t.Key);
                }
                else Assert.AreEqual(TraitId.None, Gear.TraitOf(item).Id);
                Assert.AreEqual(need, TowerFit.Need(item), "so the piece fits wherever its base type does");
            }
            Assert.AreEqual(GearCatalog.TowerTraits.Length, traits.Count, "every tower trait turns up");
        }

        [Test]
        public void ThreeTowerPiecesMergeIntoTheNextRarityButNeverWithVehiclePieces()
        {
            PlayerProfile.AddCoins(10000);
            var pieces = new List<GearItem>();
            for (var i = 0; i < 3; i++)
            {
                var g = Piece(GearSlot.TowerWeapon, "fortress_barrel");
                PlayerProfile.AddGear(g);
                pieces.Add(g);
            }
            var vehicle = new GearItem { slot = (int)GearSlot.Weapon, rarity = (int)Rarity.Rare, baseType = "long_barrel" };
            PlayerProfile.AddGear(vehicle);
            Assert.IsFalse(Gear.CanMerge(vehicle, pieces[0]), "a gun upgrade and a tower gun are different slots");
            PlayerProfile.TryLevelGear(pieces[0]);
            Assert.IsTrue(PlayerProfile.EquipTower("guard_tower", pieces[2]));
            var before = PlayerProfile.Coins;
            var merged = PlayerProfile.TryMerge(pieces[1]);
            Assert.AreSame(pieces[2], merged, "the equipped piece is kept");
            Assert.AreEqual(Rarity.Epic, merged.Rarity);
            Assert.AreEqual(GearSlot.TowerWeapon, GearCatalog.TraitFor(merged.Slot, merged.trait).Slot, "it rolls a tower weapon trait at Epic");
            Assert.AreEqual(before + Gear.Spent(new GearItem { level = 2 }), PlayerProfile.Coins, "the levels spent on the fodder come back");
            Assert.AreSame(merged, PlayerProfile.TowerEquipped("guard_tower", GearSlot.TowerWeapon), "still worn");
            CollectionAssert.AreEquivalent(new[] { merged, vehicle }, PlayerProfile.GearOwned, "the vehicle piece is left alone");
        }

        // ------------------------------------------------------------------ fit

        [Test]
        public void WhatATowerHasComesFromItsWeapons()
        {
            TowerNeed Of(string id) => TowerFit.Of(Catalog.Vehicles[id]);
            Assert.IsTrue(TowerFit.Within(TowerNeed.HitsGround | TowerNeed.HitsAir, Of("guard_tower")), "a guard tower's machine gun shoots at both");
            Assert.IsTrue(TowerFit.Within(TowerNeed.HitsGround | TowerNeed.HitsAir, Of("aa_turret")), "so does the AA tower's flak");
            Assert.IsTrue(TowerFit.Within(TowerNeed.HitsGround, Of("gun_turret")));
            Assert.IsFalse(TowerFit.Within(TowerNeed.HitsAir, Of("gun_turret")), "a coaxial machine gun does not make a gun tower anti-air");
            Assert.IsTrue(TowerFit.Within(TowerNeed.HitsAir, Of("missile_battery")));
            Assert.IsFalse(TowerFit.Within(TowerNeed.HitsGround, Of("missile_battery")), "a SAM battery is not for ground targets");
            Assert.IsFalse(TowerFit.Within(TowerNeed.HitsGround, Of("aa_turret.sam")), "nor is the AA tower's SAM branch");
            Assert.IsTrue(TowerFit.Within(TowerNeed.Magazine, Of("c_ram.dome")), "the Iron Dome branch's interceptors have a magazine");
            Assert.IsFalse(TowerFit.Within(TowerNeed.Magazine, Of("gun_turret")));

            // An obstacle: a tower with no weapon at all.
            var teeth = new VehicleDef("test_obstacle", ArmorClass.Structure, maxHp: 900f, speed: 1f, turnRateDegrees: 1f, turretTurnRateDegrees: 1f, radius: 1.8f, cpCost: 0,
                visionRange: 10f, firesWhileMoving: false, TestWorlds.Stub, deathExplosion: null, isStatic: true) { Fort = new FortDef(SlotSize.Small, FortKind.Tower) };
            Assert.AreEqual(TowerNeed.None, TowerFit.Of(teeth), "nothing to aim");
            Assert.IsTrue(TowerFit.Fits(Piece(GearSlot.TowerStructure, "reinforced_concrete"), teeth), "walls work on it");
            Assert.IsTrue(TowerFit.Fits(Piece(GearSlot.TowerStructure, "engineer_bay"), teeth));
            Assert.IsFalse(TowerFit.Fits(Piece(GearSlot.TowerWeapon, "fortress_barrel"), teeth), "a gun upgrade does not");
            Assert.IsFalse(TowerFit.Fits(Piece(GearSlot.TowerSystems, "search_radar"), teeth), "nor sights");
            var generator = Piece(GearSlot.TowerStructure, "reinforced_concrete", Rarity.Epic);
            generator.trait = GearKeys.Trait(TraitId.TowerModular);
            Assert.IsTrue(TowerFit.Fits(generator, teeth), "Modular works on any tower");
        }

        [Test]
        public void EachPieceDeclaresTheTowerTypesItWorksFor()
        {
            var fuze = Piece(GearSlot.TowerWeapon, "flak_proximity_fuze");
            var towers = TowerFit.TowersFor(fuze, Catalog);
            CollectionAssert.IsSubsetOf(new[] { "aa_turret", "guard_tower", "mg_bunker", "missile_battery" }, towers, "towers whose weapon hits aircraft");
            foreach (var id in new[] { "gun_turret", "heavy_turret", "atgm_tower", "rocket_turret" })
                CollectionAssert.DoesNotContain(towers, id, id + " cannot hit aircraft: a proximity fuze does nothing on it");
            var sabot = TowerFit.TowersFor(Piece(GearSlot.TowerWeapon, "sabot_rounds"), Catalog);
            CollectionAssert.DoesNotContain(sabot, "missile_battery");
            CollectionAssert.Contains(sabot, "gun_turret");
            CollectionAssert.AreEquivalent(TowerCards.All(Catalog), TowerFit.TowersFor(Piece(GearSlot.TowerStructure, "blast_walls"), Catalog), "walls work on every tower");
            Assert.IsEmpty(TowerFit.TowersFor(new GearItem { slot = (int)GearSlot.Armor, baseType = "spall_liner" }, Catalog), "a vehicle piece fits no tower");
            foreach (var id in TowerFit.TowersFor(Piece(GearSlot.TowerSystems, "ammo_handling"), Catalog))
                Assert.IsTrue(TowerFit.Within(TowerNeed.Magazine, TowerFit.Of(Catalog.Vehicles[id])), id + ": magazine handling only where there is a magazine");

            // The matrix the fit screen reads: every tower card and branch, with what works for it.
            var matrix = TowerFit.Matrix(Catalog);
            var rows = matrix.ToDictionary(r => r.Tower);
            foreach (var id in TowerCards.All(Catalog))
            {
                Assert.IsTrue(rows.ContainsKey(id), id + " has a row");
                CollectionAssert.IsSubsetOf(GearCatalog.TowerBasesFor(GearSlot.TowerStructure).Select(b => b.Id), rows[id].Bases, "structure fits all");
                CollectionAssert.Contains(rows[id].Traits, GearKeys.Trait(TraitId.TowerModular));
            }
            Assert.IsTrue(rows.ContainsKey("aa_turret.flak"), "branches have their own rows");
            CollectionAssert.DoesNotContain(rows["gun_turret"].Bases, "flak_proximity_fuze");
            CollectionAssert.Contains(rows["aa_turret"].Bases, "flak_proximity_fuze");
            CollectionAssert.Contains(rows["c_ram.dome"].Bases, "ammo_handling");
            Assert.IsFalse(rows.ContainsKey("headquarters"), "the HQ wears no tower equipment");
        }

        // ------------------------------------------------------------------ the loadout of a tower type

        [Test]
        public void ATowerTypesThreePiecesAreSharedByEveryTowerOfTheTypeInTheBase()
        {
            var top = Gear.LevelCap[(int)Rarity.Legendary];
            var weapon = Piece(GearSlot.TowerWeapon, "fortress_barrel", Rarity.Legendary, top);
            var walls = Piece(GearSlot.TowerStructure, "reinforced_concrete", Rarity.Legendary, top);
            var radar = Piece(GearSlot.TowerSystems, "search_radar", Rarity.Legendary, top);
            foreach (var g in new[] { weapon, walls, radar }) PlayerProfile.AddGear(g);
            Assert.IsTrue(PlayerProfile.EquipTower("guard_tower", GearSlot.TowerWeapon, weapon.id));
            Assert.IsTrue(PlayerProfile.EquipTower("guard_tower", walls));
            Assert.IsTrue(PlayerProfile.EquipTower("guard_tower", radar));
            CollectionAssert.AreEquivalent(new[] { weapon, walls, radar }, PlayerProfile.TowerGear("guard_tower"));
            Assert.AreSame(walls, PlayerProfile.TowerEquipped("guard_tower", GearSlot.TowerStructure));
            Assert.AreEqual("guard_tower", PlayerProfile.TowerWearing(walls));
            Assert.IsTrue(PlayerProfile.IsEquipped(walls));
            CollectionAssert.AreEquivalent(new[] { weapon, walls, radar }, PlayerProfile.TowerGearOwned);
            Assert.IsEmpty(PlayerProfile.VehicleGearOwned, "the army's screens do not list tower pieces");

            var world = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            world.SetBoosts(0, PlayerProfile.BoostFor);
            var b = world.Bases.Establish(0, new BaseLoadout { HqLevel = 5, Small = { "guard_tower", "guard_tower", "guard_tower", "aa_turret" } }, BaseRole.Anchor);
            var guards = world.Bases.Towers(0).Where(t => t.Def.Id == "guard_tower").ToList();
            Assert.AreEqual(3, guards.Count, "a base may hold several towers of one type");
            var def = Catalog.Vehicles["guard_tower"];
            foreach (var guard in guards)
            {
                Assert.AreEqual(def.MaxHp * 1.14f, guard.MaxHp, 1f, "each wears the type's walls");
                Assert.AreEqual(1.14f, guard.DamageBoost, 1e-3f, "and its gun upgrade");
                Assert.AreEqual(1.14f, guard.VisionFactor, 1e-3f, "and its radar");
            }
            var aa = world.Bases.Towers(0).Single(t => t.Def.Id == "aa_turret");
            Assert.AreEqual(Catalog.Vehicles["aa_turret"].MaxHp, aa.MaxHp, 1f, "another type wears its own (none)");

            // A guard tower flown back in wears them too.
            var slot = b.Slots.First(s => s.Tower == "guard_tower");
            world.TryGetVehicle(slot.Structure, out var first);
            world.Damage.Apply(first, 1e7f, DamageType.HighExplosive);
            Run(world, Catalog.Base.RebuildCooldown(def) + 0.5f);
            world.TryGetEconomy(0, out var economy);
            economy.Cp = 20f;
            Assert.IsTrue(world.Submit(new Command(CommandType.CallTower, 0, Array.Empty<EntityId>(), slot.Def.Position)).Accepted);
            Run(world, Catalog.Base.RebuildDelay + 0.5f);
            Assert.IsTrue(world.TryGetVehicle(slot.Structure, out var back) && back.IsAlive);
            Assert.AreEqual(def.MaxHp * 1.14f, back.MaxHp, 1f, "the re-dropped tower wears them too");
        }

        [Test]
        public void APieceGoesOnlyOnATowerTypeItWorksFor()
        {
            var fuze = Piece(GearSlot.TowerWeapon, "flak_proximity_fuze");
            var sabot = Piece(GearSlot.TowerWeapon, "sabot_rounds");
            var walls = Piece(GearSlot.TowerStructure, "blast_walls");
            var kit = new GearItem { slot = (int)GearSlot.Weapon, rarity = (int)Rarity.Rare, baseType = "long_barrel" };
            foreach (var g in new[] { fuze, sabot, walls, kit }) PlayerProfile.AddGear(g);
            Assert.IsFalse(PlayerProfile.EquipTower("gun_turret", fuze), "a gun tower cannot hit aircraft");
            Assert.IsTrue(PlayerProfile.EquipTower("guard_tower", fuze), "a guard tower can");
            Assert.IsFalse(PlayerProfile.EquipTower("headquarters", walls), "the HQ is not a tower card");
            Assert.IsFalse(PlayerProfile.EquipTower("guard_tower", kit), "a vehicle piece is not a tower piece");
            Assert.IsFalse(PlayerProfile.EquipTower("guard_tower", GearSlot.TowerWeapon, walls.id), "a piece goes only into its own slot");
            Assert.IsFalse(PlayerProfile.EquipTower("no_such_tower", walls));
            CollectionAssert.AreEquivalent(new[] { fuze, sabot }, PlayerProfile.TowerGearFor("guard_tower", GearSlot.TowerWeapon));
            CollectionAssert.AreEquivalent(new[] { sabot }, PlayerProfile.TowerGearFor("gun_turret", GearSlot.TowerWeapon), "what the gun tower can use");

            // A piece is worn by one tower type at a time.
            Assert.IsTrue(PlayerProfile.EquipTower("mg_bunker", fuze));
            Assert.IsNull(PlayerProfile.TowerEquipped("guard_tower", GearSlot.TowerWeapon), "it moved");
            Assert.AreEqual("mg_bunker", PlayerProfile.TowerWearing(fuze));
            PlayerProfile.UnequipTower("mg_bunker", GearSlot.TowerWeapon);
            Assert.IsNull(PlayerProfile.TowerWearing(fuze));

            // The vehicle loadout takes no tower pieces.
            PlayerProfile.Equip(GearBranch.Armor, walls);
            Assert.IsFalse(PlayerProfile.Loadout(GearBranch.Armor).Any(), "a branch never wears a tower piece");
            Assert.IsNull(PlayerProfile.Equipped(GearBranch.Air, GearSlot.TowerSystems), "and has no tower slots");
        }

        [Test]
        public void ABranchWearsItsTowersPiecesAndTheFitFollowsTheBranch()
        {
            PlayerProfile.LoadForTests("{\"coins\":1000,\"rankIds\":[\"aa_turret\"],\"ranks\":[7],\"prints\":[0]}");
            var sabot = Piece(GearSlot.TowerWeapon, "sabot_rounds", Rarity.Legendary, Gear.LevelCap[(int)Rarity.Legendary]);
            var walls = Piece(GearSlot.TowerStructure, "reinforced_concrete", Rarity.Legendary, Gear.LevelCap[(int)Rarity.Legendary]);
            PlayerProfile.AddGear(sabot);
            PlayerProfile.AddGear(walls);
            Assert.IsTrue(PlayerProfile.EquipTower("aa_turret", sabot), "the AA tower's flak hits ground targets");
            Assert.IsTrue(PlayerProfile.EquipTower("aa_turret.flak", walls), "a branch id means its tower");
            CollectionAssert.AreEquivalent(new[] { sabot, walls }, PlayerProfile.TowerGear("aa_turret.flak"), "the branch wears its tower's pieces");
            var boost = PlayerProfile.BoostFor(Catalog.Vehicles["aa_turret.flak"]);
            Assert.AreEqual(1.3f * 1.14f, boost.Hp, 1e-3f, "rank 7 (+30%) and the walls");
            Assert.IsTrue(PlayerProfile.TryChooseBranch("aa_turret", "aa_turret.sam"));
            Assert.IsFalse(PlayerProfile.TowerFits("aa_turret", sabot), "the SAM branch has no gun for ground targets");
            PlayerProfile.UnequipTower("aa_turret", GearSlot.TowerWeapon);
            Assert.IsFalse(PlayerProfile.EquipTower("aa_turret", sabot), "so the sabot rounds no longer go on");
        }

        [Test]
        public void TowerLoadoutsSurviveASave()
        {
            var weapon = Piece(GearSlot.TowerWeapon, "ammo_hoist", Rarity.Epic);
            weapon.trait = GearKeys.Trait(TraitId.TowerFireLink);
            var systems = Piece(GearSlot.TowerSystems, "traverse_motors");
            var walls = Piece(GearSlot.TowerStructure, "slat_screens");
            foreach (var g in new[] { weapon, systems, walls }) PlayerProfile.AddGear(g);
            PlayerProfile.EquipTower("gun_turret", weapon);
            PlayerProfile.EquipTower("gun_turret", systems);
            PlayerProfile.EquipTower("rocket_turret", walls);
            var json = PlayerProfile.JsonForTests();
            PlayerProfile.ResetForTests();
            Assert.IsEmpty(PlayerProfile.TowerGear("gun_turret"));
            PlayerProfile.LoadForTests(json);
            Assert.AreEqual(weapon.id, PlayerProfile.TowerEquipped("gun_turret", GearSlot.TowerWeapon)?.id);
            Assert.AreEqual(systems.id, PlayerProfile.TowerEquipped("gun_turret", GearSlot.TowerSystems)?.id);
            Assert.IsNull(PlayerProfile.TowerEquipped("gun_turret", GearSlot.TowerStructure));
            Assert.AreEqual(walls.id, PlayerProfile.TowerEquipped("rocket_turret", GearSlot.TowerStructure)?.id);
            var loaded = PlayerProfile.TowerEquipped("gun_turret", GearSlot.TowerWeapon);
            Assert.AreEqual(GearSlot.TowerWeapon, loaded.Slot);
            Assert.AreEqual("ammo_hoist", loaded.baseType);
            Assert.AreEqual(TraitId.TowerFireLink, Gear.TraitOf(loaded).Id, "with its trait");
            // A save from before tower equipment loads with none.
            PlayerProfile.LoadForTests("{\"coins\":5,\"gear\":[{\"id\":4,\"slot\":0,\"rarity\":1,\"level\":1,\"baseType\":\"long_barrel\"}],\"nextGearId\":5}");
            Assert.IsEmpty(PlayerProfile.TowerGear("gun_turret"));
            Assert.IsEmpty(PlayerProfile.TowerGearOwned);
            var fresh = Piece(GearSlot.TowerStructure, "blast_walls");
            PlayerProfile.AddGear(fresh);
            Assert.IsTrue(PlayerProfile.EquipTower("gun_turret", fresh), "and takes one on");
        }

        // ------------------------------------------------------------------ caps

        [Test]
        public void TowerLoadoutsAreCapped()
        {
            var top = Gear.LevelCap[(int)Rarity.Legendary];
            GearItem Ranged(GearSlot slot, string baseType)
            {
                var g = Piece(slot, baseType, Rarity.Legendary, top);
                g.subs.Add(new GearSub { stat = (int)StatId.Range, roll = 1f });
                return g;
            }
            // Barrel +8% range and two range sub-stats of +4%: 16% in all.
            var loadout = new[] { Ranged(GearSlot.TowerWeapon, "fortress_barrel"), Ranged(GearSlot.TowerSystems, "search_radar"), Ranged(GearSlot.TowerStructure, "reinforced_concrete") };
            Assert.AreEqual(GearCatalog.TowerStatCap[(int)StatId.Range], Gear.TowerBoost(1, loadout).Stat(StatId.Range), 1e-5f, "a tower type's range stops at its cap");
            Assert.AreEqual(0.1f, GearCatalog.TowerStatCap[(int)StatId.Range], 1e-6f);
            Assert.AreEqual(0.12f, Gear.Boost(1, loadout).Stat(StatId.Range), 1e-5f, "a vehicle's cap is higher");
            var bays = new[] { Piece(GearSlot.TowerStructure, "engineer_bay", Rarity.Legendary, top), Piece(GearSlot.TowerStructure, "engineer_bay", Rarity.Legendary, top) };
            Assert.AreEqual(0.01f, Gear.TowerBoost(1, bays).Regen, 1e-6f, "repairs stop at 1% a second on a tower");
            var guns = new[] { Piece(GearSlot.TowerWeapon, "fortress_barrel", Rarity.Legendary, top), Piece(GearSlot.TowerWeapon, "sabot_rounds", Rarity.Legendary, top) };
            Assert.AreEqual(1.25f, Gear.TowerBoost(1, guns).Damage, 1e-4f, "and the vehicle caps hold for the rest");
            Assert.AreEqual(1.45f * 1.25f, Gear.TowerBoost(10, guns).Damage, 1e-4f, "the card's rank multiplies on top");
        }

        // ------------------------------------------------------------------ the tower lines in battle

        [Test]
        public void FireLinkHitsHarderOnATargetAnotherTowerHasJustHit()
        {
            var world = Field();
            world.SetBoosts(0, def => def.Id == "gun_turret" ? Traits(new GearTrait(TraitId.TowerFireLink, 0.15f, 3f)) : VehicleBoost.None);
            var linked = world.SpawnVehicle("gun_turret", 0, new Vector2(-10f, -80f), 0f);
            var partner = world.SpawnVehicle("guard_tower", 0, new Vector2(10f, -80f), 0f);
            var target = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 60f), 0f);
            float Hit(Vehicle from) =>
                world.Damage.Apply(target, 20f, from.Weapon.DamageType, new HitInfo(from, from.Team, from.Weapon, from.Position, HitKind.Direct, false));
            var plain = Hit(linked);
            Assert.AreEqual(plain, Hit(linked), 1e-3f, "its own hits do not link");
            Hit(partner);
            Assert.AreEqual(plain * 1.15f, Hit(linked), 1e-3f, "+15% once another friendly tower has hit it");
            Assert.IsTrue(Procced(world.Events, TraitId.TowerFireLink), "the FIRE LINK word");
            Run(world, 3.2f);
            Assert.AreEqual(plain, Hit(linked), 1e-3f, "the link lasts 3 s");
            Assert.IsTrue(target.IsAlive);
        }

        [Test]
        public void CounterBatteryShowsTheGunThatShelledTheTower()
        {
            var world = Field();
            world.SetBoosts(0, def => def.Id == "gun_turret" ? Traits(new GearTrait(TraitId.TowerCounterBattery, 6f)) : VehicleBoost.None);
            var tower = world.SpawnVehicle("gun_turret", 0, new Vector2(0f, -60f), 0f);
            var gun = world.SpawnVehicle("artillery", 1, new Vector2(0f, 70f), 3.14f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(60f, 70f), 3.14f);
            Run(world, 0.5f);
            Assert.IsFalse(gun.IsVisibleTo(0), "far out of sight");
            world.Damage.Apply(tower, 30f, tank.Weapon.DamageType, new HitInfo(tank, 1, tank.Weapon, tank.Position, HitKind.Direct, false));
            Assert.IsFalse(gun.Statuses[(int)StatusKind.Reveal].Active(world.Time) || tank.Statuses[(int)StatusKind.Reveal].Active(world.Time), "a tank's shot is not counter-battery work");
            world.Damage.Apply(tower, 30f, gun.Weapon.DamageType, new HitInfo(gun, 1, gun.Weapon, tower.Position, HitKind.Splash, true));
            Assert.IsTrue(Procced(world.Events, TraitId.TowerCounterBattery), "the COUNTER-BATTERY word");
            Run(world, 0.3f);
            Assert.IsTrue(gun.IsVisibleTo(0), "the shelled tower shows the gun to its side");
            Assert.AreEqual(world.Time + 6.0 - 0.3, gun.Statuses[(int)StatusKind.Reveal].Until, 0.06, "for 6 s");
            Run(world, 6f);
            Assert.IsFalse(gun.Statuses[(int)StatusKind.Reveal].Active(world.Time), "then it is hidden again");
        }

        [Test]
        public void ModularFliesTheFirstFallenTowerOfItsTypeBackInFreeOnce()
        {
            var world = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            world.SetBoosts(0, def => def.Fort != null && def.CardId == "gun_turret" ? Traits(new GearTrait(TraitId.TowerModular, 1f)) : VehicleBoost.None);
            var b = world.Bases.Establish(0, new BaseLoadout { HqLevel = 5, Medium = { "gun_turret", "gun_turret" } }, BaseRole.Anchor);
            var slots = b.Slots.Where(s => s.Tower == "gun_turret").ToList();
            Assert.AreEqual(2, slots.Count);
            world.TryGetEconomy(0, out var economy);
            void Knock(HardpointState s)
            {
                world.TryGetVehicle(s.Structure, out var t);
                world.Damage.Apply(t, 1e7f, DamageType.HighExplosive);
            }
            Knock(slots[0]);
            var events = Run(world, 0.5f);
            Assert.IsTrue(Procced(events, TraitId.TowerModular), "the MODULAR word");
            Assert.IsTrue(slots[0].Down && slots[0].FreeCall);
            Assert.AreEqual(0, world.Bases.CostOf(slots[0]), "its re-drop is free");
            Assert.IsTrue(world.Bases.CanCall(slots[0]), "and has no cooldown");
            economy.Cp = 10f;
            Assert.IsTrue(world.Submit(new Command(CommandType.CallTower, 0, Array.Empty<EntityId>(), slots[0].Def.Position)).Accepted);
            Assert.AreEqual(10f, economy.Cp, 1e-3f, "no CP spent");
            Assert.IsFalse(slots[0].FreeCall);

            Knock(slots[1]);
            Run(world, 0.5f);
            Assert.IsFalse(slots[1].FreeCall, "once a battle for the type: the second one pays");
            Assert.AreEqual(Catalog.Base.RebuildCost(Catalog.Vehicles["gun_turret"]), world.Bases.CostOf(slots[1]));
            Assert.IsFalse(world.Bases.CanCall(slots[1]), "and waits");
            Run(world, Catalog.Base.RebuildDelay);
            Assert.IsTrue(world.TryGetVehicle(slots[0].Structure, out var back) && back.IsAlive, "the free one landed");
            Knock(slots[0]);
            Run(world, 0.5f);
            Assert.IsFalse(slots[0].FreeCall, "and falling again is not free either");

            // At Epic the free re-drop waits half the cooldown.
            var epic = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            epic.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            epic.SetBoosts(0, def => def.Fort != null && def.CardId == "gun_turret" ? Traits(new GearTrait(TraitId.TowerModular, 0.5f)) : VehicleBoost.None);
            var eb = epic.Bases.Establish(0, new BaseLoadout { HqLevel = 5, Medium = { "gun_turret" } }, BaseRole.Anchor);
            var slot = eb.Slots.First(s => s.Tower == "gun_turret");
            epic.TryGetVehicle(slot.Structure, out var epicTower);
            epic.Damage.Apply(epicTower, 1e7f, DamageType.HighExplosive);
            Run(epic, 0.05f);
            Assert.IsTrue(slot.FreeCall);
            Assert.AreEqual(Catalog.Base.RebuildCooldown(Catalog.Vehicles["gun_turret"]) * 0.5, slot.ReadyAt - epic.Time, 0.1, "half the wait at Epic");
        }

        [Test]
        public void SmokeLaunchersScreenTheTowerOnceBelowHalfHealth()
        {
            var world = Field();
            world.SetBoosts(0, def => def.Id == "gun_turret" ? Traits(new GearTrait(TraitId.TowerSmokeLaunchers, 14f, 16f)) : VehicleBoost.None);
            var tower = world.SpawnVehicle("gun_turret", 0, new Vector2(0f, -60f), 0f);
            var smoke = world.Strikes.Smoke.Count;
            tower.Hp = tower.MaxHp * 0.6f;
            Run(world, 0.2f);
            Assert.AreEqual(smoke, world.Strikes.Smoke.Count, "not above half health");
            tower.Hp = tower.MaxHp * 0.45f;
            var events = Run(world, 0.2f);
            Assert.AreEqual(smoke + 1, world.Strikes.Smoke.Count, "a smoke screen goes up");
            var cloud = world.Strikes.Smoke[world.Strikes.Smoke.Count - 1];
            Assert.AreEqual(14f, cloud.Radius, 1e-3f);
            Assert.Less(Vector2.Distance(cloud.Centre, tower.Position), 0.01f, "round the tower");
            Assert.AreEqual(world.Time + 16.0 - 0.2, cloud.Until, 0.11);
            Assert.IsTrue(Procced(events, TraitId.TowerSmokeLaunchers), "the SMOKE word");
            tower.Hp = tower.MaxHp * 0.2f;
            Run(world, 0.2f);
            Assert.AreEqual(smoke + 1, world.Strikes.Smoke.Count, "once a life");
        }

        [Test]
        public void ABackupGeneratorKeepsTheTowerRunningThroughEmpsAndStuns()
        {
            var world = Field();
            world.EnableEconomy(new TeamEconomy(1, 30f, bank: 60f));
            world.SetBoosts(0, def => def.Id switch
            {
                "aa_turret" => Traits(new GearTrait(TraitId.TowerBackupGenerator, 1f)),
                "gun_turret" => Traits(new GearTrait(TraitId.TowerBackupGenerator, 0.5f)),
                _ => VehicleBoost.None,
            });
            var immune = world.SpawnVehicle("aa_turret", 0, new Vector2(0f, 0f), 0f);
            var halved = world.SpawnVehicle("gun_turret", 0, new Vector2(-60f, -60f), 0f);
            var plain = world.SpawnVehicle("mg_bunker", 0, new Vector2(60f, -60f), 0f);
            var now = world.Time;
            world.Status.Stun(immune, now + 5.0);
            world.Status.Stun(halved, now + 4.0);
            world.Status.Stun(plain, now + 4.0);
            var events = Run(world, 0.1f);
            Assert.IsFalse(immune.Stunned, "Legendary: the stun does not take");
            Assert.AreEqual(now + 2.0, halved.StunnedUntil, 1e-3, "Epic: half as long");
            Assert.AreEqual(now + 4.0, plain.StunnedUntil, 1e-3, "a tower without it is out for the whole time");
            Assert.IsTrue(Procced(events, TraitId.TowerBackupGenerator), "the BACKUP POWER word");
        }

        // ------------------------------------------------------------------ crates

        [Test]
        public void CratesDropTowerPiecesAtTheirShareAndTheOddsAddUp()
        {
            foreach (CrateKind kind in Enum.GetValues(typeof(CrateKind)))
                for (var roll = 0; roll < Crates.Rolls[(int)kind]; roll++)
                {
                    var sum = 0f;
                    for (var r = 0; r < 5; r++) sum += Crates.PieceOdds(kind, roll, (Rarity)r, true) + Crates.PieceOdds(kind, roll, (Rarity)r, false);
                    Assert.AreEqual(1f, sum, 1e-4f, $"{kind} roll {roll}: every rarity of both kinds adds up to 1");
                }
            Assert.AreEqual(1f - Math.Pow(0.8, 4), Crates.AtLeastOneTower(CrateKind.Gold), 1e-4, "a gold crate's four rolls");

            var rng = new Random(21);
            var cards = new List<string> { "main_battle_tank", "ifv" };
            int id = 1, sinceEpic = 0, sinceLegendary = 0, total = 0, towers = 0;
            for (var n = 0; n < 500; n++)
            {
                var loot = Crates.Open(CrateKind.Silver, rng, cards, ref sinceEpic, ref sinceLegendary, () => id++);
                Assert.AreEqual(Crates.Rolls[(int)CrateKind.Silver], loot.Gear.Count, "as many rolls as before");
                foreach (var g in loot.Gear)
                {
                    total++;
                    if (!Gear.IsTower(g)) continue;
                    towers++;
                    Assert.IsTrue(GearCatalog.TowerBasesFor(g.Slot).Any(b => b.Id == g.baseType), "a tower base type of its slot");
                    Assert.That(g.brand, Is.EqualTo(0).Or.EqualTo(GearCatalog.BulwarkBrand));
                }
            }
            var share = (float)towers / total;
            Assert.AreEqual(Crates.TowerShare[(int)CrateKind.Silver], share, 0.04f, "a fifth of the rolls are tower pieces");

            // Crates favour pieces that work for a tower of the player's base.
            var air = new List<TowerNeed> { TowerFit.Of(Catalog.Vehicles["missile_battery"]) };
            int fuzes = 0, sabots = 0;
            for (var n = 0; n < 3000; n++)
            {
                var g = Gear.CreateTower(Rarity.Common, rng, n + 1, air);
                if (g.baseType == "flak_proximity_fuze") fuzes++;
                if (g.baseType == "sabot_rounds") sabots++;
            }
            Assert.Greater(fuzes, sabots * 2, "a SAM battery's player sees proximity fuzes more than sabot rounds");
        }

        [Test]
        public void OpeningACrateFromTheProfileBringsTowerPiecesIntoTheBag()
        {
            PlayerProfile.AddCrate(CrateKind.Legendary, 12);
            var rng = new Random(4);
            for (var i = 0; i < 12; i++) PlayerProfile.OpenCrate(CrateKind.Legendary, rng);
            Assert.IsNotEmpty(PlayerProfile.TowerGearOwned, "72 rolls bring tower pieces");
            Assert.AreEqual(PlayerProfile.GearOwned.Count, PlayerProfile.TowerGearOwned.Count + PlayerProfile.VehicleGearOwned.Count);
        }
    }
}
