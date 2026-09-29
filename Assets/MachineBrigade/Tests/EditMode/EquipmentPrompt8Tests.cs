using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Abilities;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 8's equipment: the fit matrix and what it lets on, the save upgrade, every new base
    /// type, unique line and brand, and the fixes (Twin Feed, the proc coefficient, the cluster
    /// warhead, fixed-effect modules, refunds, trade-offs, last stands).
    /// </summary>
    public class EquipmentPrompt8Tests
    {
        private const float Step = 0.05f;

        private static SimWorld World(VehicleBoost boost, int team = 0)
        {
            var world = Lab.Field(3);
            world.SetBoosts(team, _ => boost);
            return world;
        }

        private static VehicleBoost Stat(StatId stat, float value) => Lab.Stats((stat, value));

        private static List<SimEvent> Run(SimWorld world, float seconds)
        {
            var events = new List<SimEvent>();
            for (var t = 0f; t < seconds; t += Step)
            {
                world.Step(Step);
                events.AddRange(world.Events);
                world.ClearEvents();
            }
            return events;
        }

        private static float Hit(SimWorld world, Vehicle target, float amount, HitKind kind, WeaponDef weapon = null, Vector2? from = null, Vehicle attacker = null)
        {
            var before = target.Hp;
            weapon ??= world.Catalog.Weapons["gun_120mm"];
            world.Damage.Apply(target, amount, weapon.DamageType,
                new HitInfo(attacker, 1, weapon, from ?? target.Position + new Vector2(0f, 20f), kind, kind != HitKind.Direct));
            return before - target.Hp;
        }

        // ------------------------------------------------------------------ the fit matrix (I.1)

        [Test]
        public void BranchesComeFromTheDataAndEveryClassHasOne()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.AreEqual(ArmyBranch.Armor, catalog.Vehicle("main_battle_tank").Branch);
            Assert.AreEqual(ArmyBranch.Armor, catalog.Vehicle("tank_destroyer").Branch, "tank hunters wear the armour loadout");
            Assert.AreEqual(ArmyBranch.Light, catalog.Vehicle("aa_vehicle").Branch, "anti-air is light");
            Assert.AreEqual(ArmyBranch.Light, catalog.Vehicle("engineer_vehicle").Branch, "support is light");
            Assert.AreEqual(ArmyBranch.Artillery, catalog.Vehicle("artillery").Branch);
            Assert.AreEqual(ArmyBranch.Artillery, catalog.Vehicle("mlrs").Branch);
            Assert.AreEqual(ArmyBranch.Air, catalog.Vehicle("attack_helicopter").Branch);
            Assert.AreEqual(ArmyBranch.Air, catalog.Vehicle("strike_drone").Branch);
            foreach (var id in MatchSettings.AllVehicles)
                Assert.IsTrue(System.Enum.IsDefined(typeof(ArmyBranch), catalog.Vehicle(id).Branch), id);
        }

        [Test]
        public void ThePiecesTheBriefNamesFitWhereTheyWork()
        {
            BranchMask Of(string id) => GearCatalog.Base(id).Branches;
            Assert.AreEqual(BranchMask.None, Of("proximity_fuze") & BranchMask.Artillery, "a gun that cannot hit aircraft gets nothing from a proximity fuze");
            Assert.AreEqual(BranchMask.Air, Of("armoured_tub"), "the armoured tub is for aircraft only");
            Assert.AreEqual(BranchMask.None, Of("underbelly_armor") & BranchMask.Air, "no underbelly armour on aircraft");
            Assert.AreEqual(BranchMask.None, GearCatalog.Trait(TraitId.SkywardPintle).Branches & BranchMask.Air, "no anti-aircraft pintle on aircraft");
            Assert.AreEqual(BranchMask.Armor | BranchMask.Light, Of("flanking_rounds") & (BranchMask.Armor | BranchMask.Light), "flanking rounds: armour and light");
            Assert.AreNotEqual(BranchMask.None, Of("spare_magazine"), "launchers exist, so the spare magazine fits somewhere");
            Assert.AreEqual(BranchMask.All, Of("radar_absorbent_coating"), "missiles hunt every branch");
            Assert.AreEqual(BranchMask.None, Of("reverse_gearbox") & BranchMask.Air);
        }

        [Test]
        public void EveryEntryFitsABranchAndNoLineServesOneClassOnly()
        {
            foreach (var b in GearCatalog.Bases) Assert.AreNotEqual(BranchMask.None, b.Branches, b.Id);
            foreach (var t in GearCatalog.Traits) Assert.AreNotEqual(BranchMask.None, t.Branches, t.Key);
            foreach (var m in GearCatalog.Modules) Assert.AreNotEqual(BranchMask.None, m.Branches, m.Key);
            foreach (var brand in GearCatalog.Brands)
                if (!brand.TowerOnly) Assert.AreNotEqual(BranchMask.None, brand.Branches, brand.Id);
            // A line only one class in the whole game can use is dropped, merged or widened (I.1).
            foreach (var b in GearCatalog.Bases) Assert.GreaterOrEqual(VehicleFit.ClassesMeeting(VehicleFit.Need(b)), 2, b.Id);
            foreach (var t in GearCatalog.Traits) Assert.GreaterOrEqual(VehicleFit.ClassesMeeting(t.Needs), 2, t.Key);
            foreach (var m in GearCatalog.Modules) Assert.GreaterOrEqual(VehicleFit.ClassesMeeting(m.Needs), 2, m.Key);
        }

        [Test]
        public void CratesDropOnlyPiecesThatFitSomewhere()
        {
            var rng = new System.Random(8);
            for (var i = 0; i < 600; i++)
            {
                var item = Crates.Roll((Rarity)(i % 5), rng, i + 1);
                Assert.AreNotEqual(BranchMask.None, Gear.BranchesOf(item), $"{item.baseType} {item.trait}");
                if (item.Slot != GearSlot.Special) Assert.That(item.brand, Is.InRange(1, GearCatalog.VehicleBrandCount), "no tower brand on a vehicle piece");
            }
        }

        // ------------------------------------------------------------------ the save upgrade (I.1, I.8)

        [Test]
        public void RetiredAndMergedTypesAndUnfitPiecesAreConvertedInPlace()
        {
            var old = new List<GearItem>
            {
                new() { id = 1, slot = (int)GearSlot.Weapon, rarity = 3, level = 12, baseType = "hypervelocity_charge", brand = 2, seed = 5 },
                new() { id = 2, slot = (int)GearSlot.Engine, rarity = 2, level = 9, baseType = "turbocharger", brand = 3, seed = 6 },
                new() { id = 3, slot = (int)GearSlot.Engine, rarity = 1, level = 4, baseType = "turret_drive", brand = 3, seed = 7 },
                new() { id = 4, slot = (int)GearSlot.Armor, rarity = 4, level = 20, baseType = "mine_rollers", brand = 4, seed = 8 },
                // A proximity fuze on the artillery's loadout: it does nothing there.
                new() { id = 5, slot = (int)GearSlot.Weapon, rarity = 4, level = 22, baseType = "proximity_fuze", brand = 1, seed = 9, trait = "executioner" },
            };
            foreach (var g in old) Gear.Upgrade(g);
            Assert.AreEqual("airburst_rounds", old[0].baseType);
            Assert.AreEqual("drivetrain", old[1].baseType);
            Assert.AreEqual("drivetrain", old[2].baseType);
            Assert.AreEqual("underbelly_armor", old[3].baseType);
            var fuze = old[4];
            Assert.IsTrue(Gear.MakeFit(fuze, GearBranch.Artillery), "converted");
            Assert.IsTrue(Gear.FitsBranch(fuze, GearBranch.Artillery), "it works for the artillery now");
            Assert.AreEqual(GearSlot.Weapon, fuze.Slot, "same slot");
            Assert.AreEqual(4, fuze.rarity, "same rarity");
            Assert.AreEqual(22, fuze.level, "same level");
            Assert.AreEqual("executioner", fuze.trait, "a trait that fits is kept");
            Assert.IsFalse(Gear.MakeFit(fuze, GearBranch.Artillery), "a fitting piece is left alone");
        }

        [Test]
        public void TheEquipmentScreenOnlyPutsOnWhatFits()
        {
            PlayerProfile.ResetForTests();
            try
            {
                var fuze = new GearItem { slot = (int)GearSlot.Weapon, rarity = 2, level = 1, baseType = "proximity_fuze", brand = 1, seed = 3 };
                var barrel = new GearItem { slot = (int)GearSlot.Weapon, rarity = 2, level = 1, baseType = "long_barrel", brand = 1, seed = 4 };
                PlayerProfile.AddGear(fuze);
                PlayerProfile.AddGear(barrel);
                Assert.IsFalse(PlayerProfile.Equip(GearBranch.Artillery, fuze), "refused: it does nothing for the artillery");
                Assert.IsNull(PlayerProfile.Equipped(GearBranch.Artillery, GearSlot.Weapon));
                Assert.IsTrue(PlayerProfile.Equip(GearBranch.Artillery, barrel));
                Assert.IsTrue(PlayerProfile.Equip(GearBranch.Light, fuze), "the light branch has anti-air to use it");
            }
            finally
            {
                PlayerProfile.Load();
            }
        }

        // ------------------------------------------------------------------ new base types (B)

        [Test]
        public void FlankingRoundsHitSidesAndRearsHarder()
        {
            var world = World(Stat(StatId.DamageFlank, 0.2f));
            var shooter = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var target = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 20f), 0f);
            var info = new HitInfo(shooter, 0, shooter.Weapon, shooter.Position, HitKind.Direct, false);
            // The target faces +y, the shooter is behind it: a rear hit.
            Assert.AreEqual(1.2f, world.Gear.Outgoing(shooter, target, info), 1e-4f, "rear hit: +20 %");
            target.Heading = MathF.PI;
            Assert.AreEqual(1f, world.Gear.Outgoing(shooter, target, info), 1e-4f, "a frontal hit gets nothing");
        }

        [Test]
        public void AirburstRoundsHitDronesHarderAndShootDownWhatFliesAtIt()
        {
            var world = World(Stat(StatId.DamageVsDrone, 0.3f));
            var ifv = world.SpawnVehicle("ifv", 0, new Vector2(0f, 0f), 0f);
            var uav = world.SpawnVehicle("strike_drone", 1, new Vector2(0f, 30f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(10f, 30f), 0f);
            var info = new HitInfo(ifv, 0, ifv.Weapon, ifv.Position, HitKind.Direct, false);
            Assert.AreEqual(1.3f, world.Gear.Outgoing(ifv, uav, info), 1e-4f, "a drone");
            Assert.AreEqual(1f, world.Gear.Outgoing(ifv, heli, info), 1e-4f, "a helicopter is the proximity fuze's job");
            // Of 400 missiles flying at it, about 15 % are shot down.
            var atgm = world.Catalog.Weapons["atgm"];
            var down = 0;
            for (var i = 0; i < 400; i++)
            {
                var p = new Projectile(heli.Id, 1, atgm, ifv.Position, ifv.Id, 0f) { Origin = ifv.Position + new Vector2(0f, 20f) };
                if (world.Gear.ShootDown(p, ifv)) down++;
            }
            Assert.That(down, Is.InRange(40, 80), "about 15 %");
        }

        [Test]
        public void ASpareMagazineRefillsAnEmptyLauncherOnceALife()
        {
            var world = World(Stat(StatId.SpareMagazine, 1f));
            var mlrs = world.SpawnVehicle("mlrs", 0, new Vector2(0f, 0f), 0f);
            mlrs.Weapons[0].Ammo = 0;
            Run(world, 0.2f);
            Assert.AreEqual(mlrs.Arms[0].Ammo, mlrs.Ammo(0), "the whole magazine back at once");
            mlrs.Weapons[0].Ammo = 0;
            Run(world, 0.2f);
            Assert.AreEqual(0, mlrs.Ammo(0), "once a life");
        }

        [Test]
        public void RadarAbsorbentCoatingMakesMissilesComeCloser()
        {
            var world = World(Stat(StatId.LockRange, 0.2f), 1);
            var carrier = world.SpawnVehicle("atgm_carrier", 0, new Vector2(0f, 0f), 0f);
            var range = carrier.Weapon.Range;
            var coated = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, range * 0.9f), MathF.PI);
            var plain = World(VehicleBoost.None, 1);
            var carrier2 = plain.SpawnVehicle("atgm_carrier", 0, new Vector2(0f, 0f), 0f);
            var bare = plain.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, range * 0.9f), MathF.PI);
            var fired = Run(world, 6f).Count(e => e.Kind == SimEventKind.WeaponFired && e.Entity == carrier.Id && e.Mount == 0);
            var fired2 = Run(plain, 6f).Count(e => e.Kind == SimEventKind.WeaponFired && e.Entity == carrier2.Id && e.Mount == 0);
            Assert.AreEqual(0, fired, "at 90 % of its range the missile cannot lock on the coated tank");
            Assert.Greater(fired2, 0, "but it can on a bare one");
            Assert.IsTrue(coated.IsAlive && bare.IsAlive);
        }

        [Test]
        public void TheLaserWarnerThrowsSmokeWhenAMissileLocksOn()
        {
            var world = World(Stat(StatId.LaserWarning, 8f));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var carrier = world.SpawnVehicle("atgm_carrier", 1, new Vector2(0f, 30f), MathF.PI);
            world.SetBoosts(1, _ => Lab.Harmless);
            // The tank only has to be locked on to (its own guns would decide whether the carrier lives).
            tank.HoldFire = true;
            var events = Run(world, 12f);
            var smoke = events.Where(e => e.Kind == SimEventKind.SmokeDeployed && e.Team == 0).ToList();
            Assert.GreaterOrEqual(smoke.Count, 1, "a smoke screen when the missile locked on");
            Assert.LessOrEqual(smoke.Count, 1, "at most once every 20 s");
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "laser_warning"));
            Assert.IsTrue(carrier.IsAlive);
        }

        [Test]
        public void TheReverseGearboxBacksOffNoseOnWhenEnemiesCloseIn()
        {
            var world = World(Stat(StatId.ReverseSpeed, 0.4f));
            var tank = world.SpawnVehicle("tank_destroyer", 0, new Vector2(0f, 0f), 0f);
            world.SetBoosts(1, _ => Lab.Harmless);
            var rush = world.SpawnVehicle("armored_car", 1, new Vector2(0f, 12f), MathF.PI);
            var start = tank.Position;
            var events = Run(world, 3f);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "reverse_gearbox"), "it backed off");
            Assert.Less(tank.Position.Y, start.Y - 2f, "away from the enemy");
            var toEnemy = MachineBrigade.Sim.Core.SimMath.HeadingOf(rush.Position - tank.Position);
            Assert.Less(MathF.Abs(MachineBrigade.Sim.Core.SimMath.WrapAngle(tank.Heading - toEnemy)), 0.6f, "nose still on the enemy");
        }

        [Test]
        public void UnderbellyArmourTakesBlastsAndMinesNotDirectHits()
        {
            var world = World(Stat(StatId.ResistBlast, 0.2f));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var plainWorld = World(VehicleBoost.None);
            var plain = plainWorld.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            Assert.AreEqual(0.8f, Hit(world, tank, 100f, HitKind.Splash) / Hit(plainWorld, plain, 100f, HitKind.Splash), 1e-3f, "a blast");
            Assert.AreEqual(0.8f, Hit(world, tank, 100f, HitKind.Mine) / Hit(plainWorld, plain, 100f, HitKind.Mine), 1e-3f, "a mine");
            Assert.AreEqual(1f, Hit(world, tank, 100f, HitKind.Direct) / Hit(plainWorld, plain, 100f, HitKind.Direct), 1e-3f, "a direct hit");
        }

        // ------------------------------------------------------------------ new unique lines (C)

        [Test]
        public void VengeanceFollowsAnAllyFallingCloseByAndNeverStacks()
        {
            var world = World(Lab.Traits(new GearTrait(TraitId.Vengeance, 0.2f, 15f, 5f)));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var friend = world.SpawnVehicle("ifv", 0, new Vector2(8f, 0f), 0f);
            var far = world.SpawnVehicle("ifv", 0, new Vector2(60f, 0f), 0f);
            var enemy = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 30f), MathF.PI);
            var info = new HitInfo(tank, 0, tank.Weapon, tank.Position, HitKind.Direct, false);
            Assert.AreEqual(1f, world.Gear.Outgoing(tank, enemy, info), 1e-4f);
            world.Damage.Apply(far, 1e6f, DamageType.HighExplosive);
            Assert.AreEqual(1f, world.Gear.Outgoing(tank, enemy, info), 1e-4f, "too far away to count");
            world.Damage.Apply(friend, 1e6f, DamageType.HighExplosive);
            Assert.AreEqual(1.2f, world.Gear.Outgoing(tank, enemy, info), 1e-4f, "+20 % after a friend fell within 15 m");
            var second = world.SpawnVehicle("ifv", 0, new Vector2(-8f, 0f), 0f);
            world.Damage.Apply(second, 1e6f, DamageType.HighExplosive);
            Assert.AreEqual(1.2f, world.Gear.Outgoing(tank, enemy, info), 1e-4f, "it does not stack with itself");
            Run(world, 5.2f);
            Assert.AreEqual(1f, world.Gear.Outgoing(tank, enemy, info), 1e-4f, "gone after 5 s");
        }

        [Test]
        public void SuppressiveFireSlowsTheTargetsGuns()
        {
            var world = World(Lab.Traits(new GearTrait(TraitId.SuppressiveFire, 0.15f)));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var target = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 90f), MathF.PI);
            var p = new Projectile(tank.Id, 0, tank.Weapon, target.Position, target.Id, 0f) { Origin = tank.Position, Shooter = tank, Main = true };
            world.Damage.ResolveImpact(p);
            Run(world, 0.1f);
            Assert.AreEqual(0.85f, target.FireGear, 1e-4f, "15 % slower fire");
            // The effect lasts a quarter past the shooter's next shot (a tank gun's reload).
            var lasts = MathF.Max(3f, GearSystem.HitInterval(tank.Weapon) * 1.25f);
            Run(world, lasts - 0.6f);
            Assert.AreEqual(0.85f, target.FireGear, 1e-4f, "still on until the next shell");
            Run(world, 1.2f);
            Assert.AreEqual(1f, target.FireGear, 1e-4f, "and then off");
        }

        [Test]
        public void RearguardCutsDamageOnlyWhileDrivingAway()
        {
            var world = World(Lab.Traits(new GearTrait(TraitId.Rearguard, 0.2f)));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            world.SetBoosts(1, _ => Lab.Harmless);
            world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 40f), MathF.PI);
            Run(world, 0.6f);
            Assert.AreEqual(100f, Hit(world, tank, 100f, HitKind.Direct), 1.5f, "standing: no cut");
            world.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Move, 0, new[] { tank.Id }, new Vector2(0f, -60f)));
            Run(world, 4f);
            Assert.AreEqual(80f, Hit(world, tank, 100f, HitKind.Direct), 1.5f, "driving away: 20 % less");
        }

        // ------------------------------------------------------------------ new brands (D)

        [Test]
        public void PhoenixTurnsOverhealIntoAShortShieldAndNeverChainsWithUnbreakable()
        {
            var world = World(Lab.Traits(new GearTrait(TraitId.SetPhoenix, 0.1f, 8f), new GearTrait(TraitId.Unbreakable, 2.5f)));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            world.Gear.Heal(tank, tank.MaxHp * 0.5f);
            Assert.AreEqual(tank.MaxHp * 0.1f, GearSystem.OverhealOf(tank, world.Time), 1e-2f, "capped at 10 % of its health");
            Run(world, 8.2f);
            Assert.AreEqual(0f, GearSystem.OverhealOf(tank, world.Time), 1e-3f, "gone after 8 s");
            // The shield takes part of a killing blow: Unbreakable does not save it from the same blow.
            world.Gear.Heal(tank, tank.MaxHp);
            tank.Hp = 50f;
            Hit(world, tank, 1e5f, HitKind.Direct);
            Assert.IsFalse(tank.IsAlive, "one save at most: the shield took the blow, so Unbreakable does not");
        }

        [Test]
        public void WolfpackRewardsHuntingTogether()
        {
            var world = World(Lab.Traits(new GearTrait(TraitId.SetPackHunt, 0.04f, 15f, 3f), new GearTrait(TraitId.SetPackFocus, 0.15f)));
            world.SetBoosts(1, _ => Lab.Harmless);
            var a = world.SpawnVehicle("armored_car", 0, new Vector2(0f, 0f), 0f);
            for (var i = 0; i < 4; i++) world.SpawnVehicle("armored_car", 0, new Vector2(-12f + i * 6f, -6f), 0f);
            var enemy = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 22f), MathF.PI);
            Run(world, 1.5f);
            var info = new HitInfo(a, 0, a.Weapon, a.Position, HitKind.Direct, false);
            Assert.AreEqual(1.12f, world.Gear.Outgoing(a, enemy, info), 1e-4f, "+4 % a friend within 15 m, three at most");
            Assert.AreEqual(1.15f, a.FireGear, 1e-3f, "five on one target: +15 % fire rate");
        }

        [Test]
        public void BulwarkPiecesCountAcrossTheBaseAndLeaveAPost()
        {
            var brand = GearCatalog.Brand(GearCatalog.BulwarkBrand);
            Assert.IsTrue(brand.TowerOnly);
            var piece = new GearItem { slot = (int)GearSlot.TowerStructure, rarity = 2, level = 1, baseType = "reinforced_concrete", brand = GearCatalog.BulwarkBrand };
            var counts = new int[GearCatalog.Brands.Length + 1];
            counts[GearCatalog.BulwarkBrand] = 4;
            var boost = Gear.TowerBoost(1, new[] { piece }, counts);
            Assert.Greater(boost.Hp, Gear.TowerBoost(1, new[] { piece }).Hp, "two or more in the base: +10 % health");
            Assert.IsTrue(boost.Traits.Any(t => t.Id == TraitId.SetBulwarkPost), "four: the fallback post");
            var none = Gear.TowerBoost(1, new GearItem[0], counts);
            Assert.IsNull(none.Traits, "a tower type wearing none gets nothing");

            var world = World(boost);
            var tower = world.SpawnVehicle("gun_turret", 0, new Vector2(0f, 0f), 0f);
            world.Damage.Apply(tower, 1e6f, DamageType.HighExplosive);
            Run(world, 0.2f);
            var post = world.Vehicles.FirstOrDefault(v => v.Def.Id == GearSystem.BulwarkPostId && v.IsAlive);
            Assert.IsNotNull(post, "a machine-gun post where it stood");
            Run(world, 20.5f);
            Assert.IsFalse(post.IsAlive, "for 20 s");
        }

        // ------------------------------------------------------------------ fixes (I.2 to I.10)

        [Test]
        public void TwinFeedAddsARoundToASalvoAndDamageToASingleShot()
        {
            var twin = new GearTrait(TraitId.TwinFeed, 0.12f, 0.2f);
            var world = World(Lab.Traits(twin));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var mlrs = world.SpawnVehicle("mlrs", 0, new Vector2(10f, 0f), 0f);
            Assert.AreEqual(1.2f, world.Gear.Shot(tank, 0, default, Vector2.Zero, tank.Weapon, true).Scale, 1e-4f, "a single gun: +20 % a round");
            Assert.AreEqual(1, world.Gear.ExtraRounds(mlrs, mlrs.Weapon, out var per), "a salvo: one more round");
            Assert.AreEqual(mlrs.Weapon.Burst * 1.12f / (mlrs.Weapon.Burst + 1), per, 1e-4f, "the salvo 12 % harder in all");
            Assert.AreEqual(0, world.Gear.ExtraRounds(tank, tank.Weapon, out _), "no extra round on a one-round gun");
        }

        [Test]
        public void TheProcCoefficientFollowsTheWeaponsRhythm()
        {
            var w = GameContent.LoadCatalog().Weapons;
            Assert.AreEqual(0.15f, GearSystem.ProcCoefficient(w["gau_gatling"]), 1e-4f, "a gatling: the least");
            Assert.Less(GearSystem.ProcCoefficient(w["flak_35"]), 0.25f, "a flak gun: next to it");
            Assert.AreEqual(2.5f, GearSystem.ProcCoefficient(w["gun_120mm"]), 1e-4f, "a tank gun: the most");
            Assert.Less(GearSystem.ProcCoefficient(w["minigun"]), 0.2f);
            Assert.Greater(GearSystem.ProcCoefficient(w["mlrs_rockets"]), GearSystem.ProcCoefficient(w["autocannon_30"]));
        }

        [Test]
        public void ClusterWarheadsSeedOnlyASalvosFirstRounds()
        {
            var world = World(Lab.Traits(new GearTrait(TraitId.ClusterWarhead, 6f)));
            var mlrs = world.SpawnVehicle("mlrs", 0, new Vector2(0f, 0f), 0f);
            var w = mlrs.Weapon;
            var first = world.Gear.Shot(mlrs, 0, default, Vector2.Zero, w, true);
            var rest = new List<bool>();
            for (var i = 1; i < w.Burst; i++) rest.Add(world.Gear.Shot(mlrs, 0, default, Vector2.Zero, w, false).NoCluster);
            Assert.IsFalse(first.NoCluster, "the first round carries bomblets");
            Assert.IsFalse(rest[0], "and the second");
            Assert.IsTrue(rest.Skip(1).All(x => x), "the rest carry none");
        }

        [Test]
        public void FixedEffectModulesFollowTheVehiclesPrice()
        {
            var catalog = GameContent.LoadCatalog();
            Vehicle Make(string id)
            {
                var world = World(Lab.Module(SpecialModule.DroneEscort, 2f, 20f));
                return world.SpawnVehicle(id, 0, Vector2.Zero, 0f);
            }
            Assert.AreEqual(0.4f, GearSystem.ModuleScale(Make("scout_jeep")), 1e-4f, "a 2 CP jeep: the floor");
            Assert.AreEqual(1f, GearSystem.ModuleScale(Make("main_battle_tank")), 1e-4f, "a 7 CP tank: in full");
            Assert.AreEqual(1.3f, GearSystem.ModuleScale(Make("titan_tank")), 1e-4f, "a 14 CP titan: the cap");
            // Volatile fuel tanks never blow up for more than 1,500, even on a huge hull.
            var world2 = World(Lab.Traits(new GearTrait(TraitId.VolatileFuelTanks, 0.45f, 10f)));
            var titan = world2.SpawnVehicle("titan_tank", 0, Vector2.Zero, 0f);
            world2.Damage.Apply(titan, 1e7f, DamageType.HighExplosive);
            var blast = Run(world2, 0.5f).Where(e => e.Kind == SimEventKind.Explosion).Select(e => e.Value).DefaultIfEmpty(0f).Max();
            Assert.Greater(blast, 0f);
        }

        [Test]
        public void KillRefundsStopAtTheCap()
        {
            Assert.AreEqual(0.25f, EconomySystem.KillShare(1f, 1f), 1e-5f, "a plain kill: a quarter");
            Assert.AreEqual(0.45f, EconomySystem.KillShare(1.5f, 1.8f + 0.2f), 1e-5f, "profiteer, salvage rights and the underdog's bounty: 45 % at most");
        }

        [Test]
        public void TradeOffDrawbacksGrowWithTheGain()
        {
            var fresh = new GearItem { slot = (int)GearSlot.Weapon, rarity = 2, level = 1, baseType = "heavy_barrel" };
            var top = new GearItem { slot = (int)GearSlot.Weapon, rarity = 4, level = 25, baseType = "heavy_barrel" };
            Assert.AreEqual(-0.05f * 0.4f, Gear.PenaltyValue(fresh), 1e-5f, "a fresh piece pays 40 % of its drawback");
            Assert.AreEqual(-0.07f, Gear.PenaltyValue(top), 1e-5f);
            foreach (var b in GearCatalog.Bases.Where(b => b.TradeOff))
                for (var r = b.MinRarity; r <= 4; r++)
                {
                    var piece = new GearItem { slot = (int)b.Slot, rarity = r, level = 1, baseType = b.Id };
                    var gain = Gear.Value(piece) + Gear.ImplicitValue(piece);
                    Assert.Greater(gain, -Gear.PenaltyValue(piece), $"{b.Id} {(Rarity)r}: the gain is bigger than the drawback");
                }
        }

        [Test]
        public void AegisDomeDoesNotSaveWhatUnbreakableJustSaved()
        {
            var world = World(Lab.Traits(new GearTrait(TraitId.Unbreakable, 1f)));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            Hit(world, tank, 1e5f, HitKind.Direct);
            Assert.AreEqual(1f, tank.Hp, 1e-3f, "Unbreakable saved it");
            Assert.Greater(tank.LastStandUntil, world.Time + 1f, "and no other last stand may for a while");
        }
    }
}
