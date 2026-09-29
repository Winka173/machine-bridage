using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The tower roster (prompt 3): what each new tower does, the guard tower's and the light
    /// towers' own jobs, the cannon towers' weaknesses, the Patriot, the utility modules, engineers
    /// on towers, mines and obstacles, and the merged point tower.
    /// </summary>
    public class TowerRosterTests
    {
        private static SimWorld Field(float size = 200f) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", size,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        private static void Run(SimWorld world, float seconds, System.Action<SimEvent> seen = null, params Vehicle[] keep)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                foreach (var v in keep) v.Hp = v.MaxHp;
                world.Step(TestWorlds.Step);
                if (seen != null)
                    foreach (var e in world.Events) seen(e);
                world.ClearEvents();
            }
        }

        private static Vehicle Tower(SimWorld world, string id, int team, Vector2 at)
        {
            var t = world.SpawnVehicle(id, team, at, 0f);
            world.AnchorDefence(t);
            return t;
        }

        [Test]
        public void EveryTowerHasASizeAndTwoBranches()
        {
            var catalog = GameContent.LoadCatalog();
            var towers = TowerCards.All(catalog);
            foreach (var id in new[] { "guard_tower", "mg_bunker", "aa_turret", "ew_tower", "dragons_teeth", "minefield", "gun_turret", "atgm_tower",
                         "rocket_turret", "c_ram", "gun_pit", "artillery_emplacement", "missile_battery", "drone_hangar", "heavy_turret" })
            {
                Assert.Contains(id, towers, id);
                Assert.AreEqual(2, TowerCards.Branches(catalog, id).Count, $"{id} has two branches");
                foreach (var b in TowerCards.Branches(catalog, id))
                    Assert.AreEqual(catalog.Vehicles[id].Fort.Size, catalog.Vehicles[b].Fort.Size, $"{b} keeps {id}'s size");
            }
            Assert.IsFalse(catalog.Vehicles.ContainsKey("flak_tower") || catalog.Vehicles.ContainsKey("point_tower"), "the merged towers are gone");
            var sizes = new Dictionary<string, SlotSize>
            {
                ["ew_tower"] = SlotSize.Small, ["dragons_teeth"] = SlotSize.Small, ["minefield"] = SlotSize.Small,
                ["c_ram"] = SlotSize.Medium, ["gun_pit"] = SlotSize.Medium, ["drone_hangar"] = SlotSize.Large,
            };
            foreach (var (id, size) in sizes) Assert.AreEqual(size, catalog.Vehicles[id].Fort.Size, id);
        }

        [Test]
        public void CannonTowersCannotShootAircraftAndTurnSlowly()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var id in new[] { "gun_turret", "heavy_turret", "gun_pit" })
            {
                var def = catalog.Vehicles[id];
                Assert.IsFalse(def.Mounts.Any(m => m.Weapon.Damage > 0f && m.Weapon.CanTarget(true)), $"{id} has nothing for aircraft");
                Assert.LessOrEqual(def.TurretTurnRate, 60f, $"{id} turns slowly");
            }
            var patriot = catalog.Vehicles["missile_battery"].Weapon;
            Assert.AreEqual(90f, patriot.Range);
            Assert.AreEqual(20f, patriot.MinRange);
        }

        [Test]
        public void TheGuardTowerSeesStealthAndLendsNearbyTowersReach()
        {
            var world = Field();
            var guard = Tower(world, "guard_tower", 0, new Vector2(0f, 0f));
            var near = Tower(world, "gun_turret", 0, new Vector2(15f, 0f));
            var far = Tower(world, "rocket_turret", 0, new Vector2(40f, 0f));
            var second = Tower(world, "guard_tower", 0, new Vector2(10f, 8f));
            var bomber = world.SpawnVehicle("stealth_bomber", 1, new Vector2(0f, 20f), 0f);
            world.Submit(new Command(CommandType.Stop, 1, new[] { bomber.Id }));
            Run(world, 1f);
            Assert.IsTrue(bomber.IsVisibleTo(0), "a stealth bomber inside its guns' reach shows");
            Assert.AreEqual(1.1f, near.RangeFactor, 1e-3f, "a tower within 25 m reaches 10 % further");
            Assert.AreEqual(1f, far.RangeFactor, 1e-3f, "not beyond");
            Assert.AreEqual(1.1f, second.RangeFactor, 1e-3f, "two guard towers do not add up");
        }

        [Test]
        public void LightTowersHitHelicoptersAndDronesHarder()
        {
            var world = Field();
            var aa = Tower(world, "aa_turret", 0, new Vector2(0f, 0f));
            var gun = Tower(world, "c_ram", 0, new Vector2(10f, 0f));
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 20f), 0f);
            var jet = world.SpawnVehicle("fighter_jet", 1, new Vector2(0f, 30f), 0f);
            Assert.AreEqual(1.25f, DamageSystem.BonusFor(aa.Def.Weapon, aa, heli, world.Time), 1e-4f, "a light tower on a helicopter");
            Assert.AreEqual(1f, DamageSystem.BonusFor(aa.Def.Weapon, aa, jet, world.Time), 1e-4f, "not on a jet");
            Assert.AreEqual(1f, DamageSystem.BonusFor(gun.Def.Weapon, gun, heli, world.Time), 1e-4f, "a medium tower gets none");
        }

        [Test]
        public void AGunPitHidesUntilAnEnemyComesCloseThenAmbushes()
        {
            var world = Field();
            var pit = Tower(world, "gun_pit.ambush", 1, new Vector2(0f, 0f));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -45f), 0f);
            world.Submit(new Command(CommandType.Stop, 0, new[] { tank.Id }));
            Run(world, 1f);
            Assert.IsTrue(pit.Lowered, "down with the enemy 45 m away");
            Assert.IsFalse(pit.IsVisibleTo(0), "and unseen by a tank");
            var before = pit.Hp;
            world.Damage.Apply(pit, 1000f, DamageType.HighExplosive);
            var hidden = before - pit.Hp;
            pit.Hp = pit.MaxHp;
            world.Submit(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(0f, -30f)));
            Run(world, 5f);
            Assert.IsFalse(pit.Lowered, "up once the enemy is within 35 m");
            Assert.IsTrue(pit.AmbushReady || pit.Weapons[0].Cooldown > 0f, "its first shot is an ambush (or already fired)");
            before = pit.Hp;
            world.Damage.Apply(pit, 1000f, DamageType.HighExplosive);
            Assert.AreEqual(0.4f, hidden / (before - pit.Hp), 0.01f, "down, it takes 60 % less");
        }

        [Test]
        public void AFixedMinefieldKeepsItsMinesAndIsNoTarget()
        {
            var world = Field();
            var field = Tower(world, "minefield", 0, new Vector2(0f, 0f));
            Run(world, 1f);
            var mines = world.Mines.Where(m => m.IsAlive && m.Layer == field.Id).ToList();
            Assert.AreEqual(8, mines.Count, "eight mines at once");
            Assert.IsTrue(mines.All(m => Vector2.Distance(m.Position, field.Position) <= 5.01f), "round it");
            Assert.IsTrue(field.Def.Untargetable && field.Def.Passable && field.Def.Passive, "no target, no blocker, no gun");
            var victim = world.SpawnVehicle("armored_car", 1, mines[0].Position + new Vector2(0f, 10f), 3.14f);
            world.Submit(new Command(CommandType.Move, 1, new[] { victim.Id }, mines[0].Position - new Vector2(0f, 8f)));
            Run(world, 6f);
            Assert.Less(world.Mines.Count(m => m.IsAlive && m.Layer == field.Id), 8, "one went off");
            Run(world, 46f);
            Assert.AreEqual(8, world.Mines.Count(m => m.IsAlive && m.Layer == field.Id), "and the field is laid again within 45 s");
        }

        [Test]
        public void DragonsTeethBlockTheWayAndEngineersBreachThemFaster()
        {
            var world = Field();
            var teeth = Tower(world, "dragons_teeth", 1, new Vector2(0f, 0f));
            Assert.IsTrue(teeth.BlocksRoutes, "it blocks the way");
            var engineer = world.SpawnVehicle("engineer_vehicle", 0, new Vector2(0f, -10f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(4f, -10f), 0f);
            Assert.AreEqual(3f, DamageSystem.BonusFor(engineer.Def.Weapon, engineer, teeth, world.Time), 1e-4f, "an engineer breaches three times as fast");
            Assert.AreEqual(1f, DamageSystem.BonusFor(tank.Def.Weapon, tank, teeth, world.Time), 1e-4f);
            var wire = Tower(world, "dragons_teeth.wire", 1, new Vector2(40f, 0f));
            Assert.IsFalse(wire.BlocksRoutes, "wire does not block");
            var runner = world.SpawnVehicle("armored_car", 0, new Vector2(40f, 3f), 0f);
            world.Submit(new Command(CommandType.Stop, 0, new[] { runner.Id }));
            Run(world, 1f);
            Assert.Greater(Sim.Combat.StatusSystem.SlowShare(runner, world.Time), 0.4f, "but slows what is in it");
        }

        [Test]
        public void TheCRamShootsDownRocketsAndSomeShells()
        {
            var world = Field();
            var cram = Tower(world, "c_ram", 1, new Vector2(0f, 0f));
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(8f, 0f), 0f);
            var mlrs = world.SpawnVehicle("mlrs", 0, new Vector2(0f, -80f), 0f);
            // Two guns: since prompt 13 B a 155 mm shell is one every 11 s (it was 7), and the C-RAM takes a
            // share of them (30 %), so one gun's four shells in 40 s were too few to count on one being taken.
            // The C-RAM is kept standing: the 155 mm splash beside it is not what this test is about.
            var gun = world.SpawnVehicle("artillery", 0, new Vector2(20f, -80f), 0f);
            var gun2 = world.SpawnVehicle("artillery", 0, new Vector2(-20f, -80f), 0f);
            var spotter = world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, -28f), 0f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { mlrs.Id, gun.Id, gun2.Id }, target: tank.Id));
            var kinds = new HashSet<string>();
            Run(world, 40f, e =>
            {
                if (e.Kind == SimEventKind.Intercepted && e.DefId != null) kinds.Add(e.DefId);
            }, spotter, cram);
            Assert.Contains("mlrs_rockets", kinds.ToList(), "rockets");
            Assert.Contains("howitzer", kinds.ToList(), "and some shells");
        }

        [Test]
        public void TheDroneHangarSendsDrones()
        {
            var world = Field();
            Tower(world, "drone_hangar", 0, new Vector2(0f, 0f));
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 40f), 3.14f);
            world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 25f), 0f);
            var drones = 0;
            Run(world, 42f, e =>
            {
                if (e.Kind == SimEventKind.WeaponFired && e.DefId == "fpv_hangar") drones++;
            });
            Assert.That(drones, Is.InRange(4, 6), "two drones every 20 s");
        }

        [Test]
        public void UtilityModulesServeTheBase()
        {
            var catalog = GameContent.LoadCatalog();
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            var b = world.Bases.Establish(0, new BaseLoadout
            {
                HqLevel = 5, Utilities = { "repair_bay", "logistics_station", "airfield" },
            }, BaseRole.Anchor);
            Assert.AreEqual(3, world.Bases.Towers(0).Count(t => t.Def.Utility != null), "three modules stand");
            world.TryGetEconomy(0, out var economy);
            var supply = economy.ArmyCap;
            var tank = world.SpawnVehicle("main_battle_tank", 0, b.HqPosition + new Vector2(8f, 0f), 0f);
            world.Damage.Apply(tank, tank.MaxHp * 0.5f / world.Catalog.Damage.Multiplier(DamageType.ArmorPiercing, ArmorClass.Heavy), DamageType.ArmorPiercing);
            var hurt = tank.Hp;
            Run(world, 2f);
            Assert.Greater(economy.ArmyCap, supply, "the logistics station adds supply");
            Assert.Greater(tank.Hp, hurt + tank.MaxHp * 0.02f, "the repair bay mends vehicles in the base, even straight after a hit");
            var field = world.Bases.Towers(0).First(t => t.Def.Id == "airfield");
            var heli = world.SpawnVehicle("attack_helicopter", 0, field.Position, 0f);
            heli.Hp = heli.MaxHp * 0.3f;
            world.Submit(new Command(CommandType.Stop, 0, new[] { heli.Id }));
            Run(world, 5f);
            Assert.Greater(heli.Hp, heli.MaxHp * 0.3f + heli.MaxHp * 0.1f, "the airfield repairs aircraft over it");
        }

        [Test]
        public void EngineersRepairTowersAndClearMines()
        {
            var world = Field();
            var tower = Tower(world, "gun_turret", 0, new Vector2(0f, 0f));
            tower.Hp = tower.MaxHp * 0.5f;
            var field = Tower(world, "minefield", 1, new Vector2(20f, 0f));
            Run(world, 1f);
            var engineer = world.SpawnVehicle("engineer_vehicle", 0, new Vector2(6f, 0f), 0f);
            world.Submit(new Command(CommandType.Stop, 0, new[] { engineer.Id }));
            Run(world, 4f);
            Assert.Greater(tower.Hp, tower.MaxHp * 0.5f, "a tower beside an engineer is patched up");
            var mines = world.Mines.Count(m => m.IsAlive && m.Layer == field.Id);
            world.Submit(new Command(CommandType.Move, 0, new[] { engineer.Id }, new Vector2(14f, 0f)));
            Run(world, 12f);
            Assert.Less(world.Mines.Count(m => m.IsAlive && m.Layer == field.Id), mines, "and clears the mines it finds");
        }

        [Test]
        public void APointsWatchtowerIsATougherGuardTower()
        {
            Assert.AreEqual("guard_tower", Outposts.Tower);
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 3);
            var mode = new ConquestMode(new ConquestRules { Outposts = true });
            mode.Setup(world);
            for (var t = 0f; t < 3f; t += TestWorlds.Step)
            {
                mode.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            var neutral = world.VehicleList.Where(v => v.Def.Id == "guard_tower" && v.Team == MachineBrigade.Sim.Entities.Teams.Hostile).ToList();
            if (neutral.Count == 0) Assert.Ignore("this map raises no neutral watchtowers");
            Assert.AreEqual(world.Catalog.Vehicles["guard_tower"].MaxHp * 2f, neutral[0].MaxHp, 1f, "twice a guard tower's health while neutral");
        }
    }
}
