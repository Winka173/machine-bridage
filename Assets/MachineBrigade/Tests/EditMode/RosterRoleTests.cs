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
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The roster cleanup's new jobs: the Lancet hunts artillery and parked vehicles, the Iron Beam
    /// is point defence, the Ka-52 stands off, the four new vehicles and the four new supports do
    /// what their cards say, and the first balance fixes (car bombs on structures, the siege gun's
    /// bunker-buster, the airstrike's longer line from rank 7).
    /// </summary>
    public class RosterRoleTests
    {
        private static SimWorld Field(float size = 200f) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", size,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        private static void Run(SimWorld world, float seconds, System.Action<SimEvent> seen = null, params Vehicle[] keep)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                // Spotters kept alive: the test is about what they let the others see.
                foreach (var v in keep) v.Hp = v.MaxHp;
                world.Step(TestWorlds.Step);
                if (seen != null)
                    foreach (var e in world.Events) seen(e);
                world.ClearEvents();
            }
        }

        [Test]
        public void TheLancetHitsArtilleryAndParkedVehiclesTwiceAsHard()
        {
            var world = Field();
            var lancet = world.Catalog.Weapons["lancet"];
            var hunter = world.SpawnVehicle("lancet_truck", 0, new Vector2(-40f, 0f), 0f);
            var gun = world.SpawnVehicle("artillery", 1, new Vector2(40f, 0f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(40f, 20f), 0f);
            var tower = world.SpawnVehicle("gun_turret", 1, new Vector2(40f, -20f), 0f);
            Assert.AreEqual(2f, DamageSystem.BonusFor(lancet, hunter, gun, world.Time), 1e-4f, "double on artillery");
            Assert.AreEqual(1f, DamageSystem.BonusFor(lancet, hunter, tank, world.Time), 1e-4f, "a tank that just arrived: no bonus");
            Run(world, 3.5f);
            Assert.AreEqual(2f, DamageSystem.BonusFor(lancet, hunter, tank, world.Time), 1e-4f, "parked 3 s: double");
            Assert.AreEqual(2f, DamageSystem.BonusFor(lancet, hunter, gun, world.Time), 1e-4f, "never more than double (the bonuses do not stack)");
            Assert.AreEqual(1f, DamageSystem.BonusFor(lancet, hunter, tower, world.Time), 1e-4f, "a fixed defence does not count as parked");
        }

        [Test]
        public void TheWheeledGunHitsHarderOnAFlank()
        {
            var world = Field();
            var gun = world.Catalog.Weapons["gun_105_wheeled"];
            var hunter = world.SpawnVehicle("wheeled_gun", 0, new Vector2(0f, -30f), 0f);
            // A tank facing the hunter (heading pi: towards -y), then one showing its side.
            var facing = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 0f), 3.14159f);
            var side = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 0f), 1.5708f);
            Assert.AreEqual(1f, DamageSystem.BonusFor(gun, hunter, facing, world.Time), 1e-4f);
            Assert.AreEqual(1.25f, DamageSystem.BonusFor(gun, hunter, side, world.Time), 1e-4f);
            var dps = gun.Damage / gun.Cooldown * world.Catalog.Damage.Multiplier(DamageType.ArmorPiercing, ArmorClass.Heavy);
            Assert.That(dps, Is.InRange(60f, 70f), "about 65 damage a second on heavy armour");
        }

        [Test]
        public void CarBombsHalfOnStructuresAndTheSiegeGunBustsBunkers()
        {
            var world = Field();
            var bomb = world.SpawnVehicle("vbied", 0, new Vector2(0f, -10f), 0f);
            var siege = world.SpawnVehicle("siege_tank", 0, new Vector2(0f, -50f), 0f);
            var tower = world.SpawnVehicle("gun_turret", 1, new Vector2(0f, 0f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(10f, 0f), 0f);
            Assert.AreEqual(0.5f, DamageSystem.BonusFor(world.Catalog.Weapons["detonator"], bomb, tower, world.Time), 1e-4f);
            Assert.AreEqual(1f, DamageSystem.BonusFor(world.Catalog.Weapons["detonator"], bomb, tank, world.Time), 1e-4f);
            var shell = world.Catalog.Weapons["gun_203_siege"];
            var onStructures = shell.Damage / shell.Cooldown * world.Catalog.Damage.Multiplier(shell.DamageType, ArmorClass.Structure) *
                               DamageSystem.BonusFor(shell, siege, tower, world.Time);
            Assert.Greater(onStructures, 150f, "the siege gun does 150+ a second to structures");
            Assert.AreEqual(12, world.Catalog.Vehicles["siege_tank"].CpCost);
        }

        [Test]
        public void TheIronBeamShootsDownArtilleryRocketsOneEveryBeat()
        {
            var world = Field();
            var beam = world.SpawnVehicle("iron_beam", 1, new Vector2(0f, 0f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(6f, 0f), 0f);
            var mlrs = world.SpawnVehicle("mlrs", 0, new Vector2(0f, -80f), 0f);
            var spotter = world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, -28f), 0f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { mlrs.Id }, target: tank.Id));
            var intercepted = new List<double>();
            Run(world, 30f, e =>
            {
                if (e.Kind == SimEventKind.Intercepted && e.Entity == beam.Id) intercepted.Add(world.Time);
            }, spotter);
            Assert.Greater(intercepted.Count, 0, "it takes artillery rockets");
            for (var i = 1; i < intercepted.Count; i++)
                Assert.GreaterOrEqual(intercepted[i] - intercepted[i - 1], 1.15, "one round a beat (1.2 s)");
            Assert.Less(tank.Hp, tank.MaxHp, "a six-rocket salvo is more than it can stop");
        }

        [Test]
        public void TheKa52StandsOutsideShortRangeAntiAir()
        {
            var world = Field();
            var heli = world.SpawnVehicle("heavy_attack_heli", 0, new Vector2(0f, -70f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 0f), 3.14f);
            var aa = world.SpawnVehicle("aa_vehicle", 1, new Vector2(4f, 6f), 3.14f);
            var spotter = world.SpawnVehicle("scout_jeep", 0, new Vector2(-30f, -12f), 0f);
            world.Submit(new Command(CommandType.Stop, 1, new[] { tank.Id, aa.Id }));
            world.Submit(new Command(CommandType.Attack, 0, new[] { heli.Id }, target: tank.Id));
            var aaReach = aa.Def.Mounts.Where(m => m.Weapon.CanTarget(true)).Max(m => m.Weapon.Range);
            var closest = float.MaxValue;
            for (var t = 0f; t < 40f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                if (t > 8f) closest = System.MathF.Min(closest, Vector2.Distance(heli.Position, aa.Position));
                aa.Hp = aa.MaxHp;
                spotter.Hp = spotter.MaxHp;
            }
            Assert.Greater(closest, aaReach, "the Ka-52 never comes into the flak's reach");
            Assert.Less(tank.Hp, tank.MaxHp, "and still hits the tank from 55 m");
        }

        [Test]
        public void TheCommandVehicleSpeedsUpFireRoundItAndBecomesADropZone()
        {
            var world = Field();
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            var command = world.SpawnVehicle("command_vehicle", 0, new Vector2(0f, 0f), 0f);
            var near = world.SpawnVehicle("main_battle_tank", 0, new Vector2(15f, 0f), 0f);
            var far = world.SpawnVehicle("main_battle_tank", 0, new Vector2(40f, 0f), 0f);
            Run(world, 1f);
            Assert.AreEqual(1.1f, near.CommandFire, 1e-4f, "10 % faster within 25 m");
            Assert.AreEqual(1f, far.CommandFire, 1e-4f, "not beyond");
            Assert.IsTrue(world.Bases.TryGetDropZone(0, out var before));
            Run(world, 5f);
            Assert.IsTrue(world.Bases.TryGetDropZone(0, out var after));
            Assert.Less(Vector2.Distance(after, command.Position), 10f, "standing still 5 s it is the drop zone");
            Assert.Greater(Vector2.Distance(before, command.Position), 30f, "which it was not before");
            var second = world.Submit(Command.Deploy(0, "command_vehicle"));
            Assert.AreEqual(CommandError.UnitLimit, second.Error, "one per side");
        }

        [Test]
        public void TheRadarRevealsGunsThatFireAndOurArtilleryHitsThemHarder()
        {
            var world = Field();
            var radar = world.SpawnVehicle("counter_battery_radar", 0, new Vector2(0f, -40f), 0f);
            var gun = world.SpawnVehicle("artillery", 1, new Vector2(0f, 60f), 3.14f);
            var target = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var spotter = world.SpawnVehicle("scout_jeep", 1, new Vector2(0f, 26f), 3.14f);
            world.Submit(new Command(CommandType.Attack, 1, new[] { gun.Id }, target: target.Id));
            var revealed = false;
            Run(world, 15f, e => revealed |= e.Kind == SimEventKind.GunRevealed, spotter);
            Assert.IsTrue(revealed, "the gun that fired within 120 m was found");
            Assert.IsTrue(gun.IsVisibleTo(0), "and shows to the radar's side (100 m out, beyond its sight)");
            ref var reveal = ref gun.Statuses[(int)StatusKind.Reveal];
            Assert.AreEqual(0.15f, reveal.Value, 1e-4f, "our artillery does 15 % more to it");
        }

        [Test]
        public void TheLongRangeSamOnlyShootsAircraftFromFarOff()
        {
            var catalog = GameContent.LoadCatalog();
            var sam = catalog.Vehicles["long_sam"].Weapon;
            Assert.IsTrue(sam.CanTarget(true));
            Assert.IsFalse(sam.CanTarget(false), "air only");
            Assert.AreEqual(95f, sam.Range);
            Assert.AreEqual(20f, sam.MinRange);
            Assert.AreEqual(1, catalog.Vehicles["long_sam"].Mounts.Count, "nothing for the ground");
        }

        [Test]
        public void AUavScanShowsEverythingUnderItForTenSeconds()
        {
            var world = Field();
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            world.SpawnVehicle("scout_jeep", 0, new Vector2(-70f, -70f), 0f);
            var bomber = world.SpawnVehicle("stealth_bomber", 1, new Vector2(30f, 30f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(35f, 25f), 0f);
            world.Submit(new Command(CommandType.Stop, 1, new[] { bomber.Id, tank.Id }));
            Run(world, 0.5f);
            Assert.IsFalse(tank.IsVisibleTo(0), "far beyond our sight");
            Assert.IsTrue(world.Submit(Command.Strike(0, "uav_scan", new Vector2(32f, 28f))).Accepted);
            Run(world, 2.5f);
            Assert.IsTrue(tank.IsVisibleTo(0), "the scan shows it");
            Assert.IsTrue(bomber.IsVisibleTo(0) || Vector2.Distance(bomber.Position, new Vector2(32f, 28f)) > 30f, "stealth too, while inside");
            Run(world, 10.5f);
            Assert.IsFalse(tank.IsVisibleTo(0), "and stops after 10 s");
        }

        [Test]
        public void RemoteMinesAreScatteredAndClearThemselves()
        {
            var world = Field();
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            Assert.IsTrue(world.Submit(Command.Strike(0, "remote_mines", new Vector2(0f, 0f))).Accepted);
            Run(world, 3f);
            var mines = world.Mines.Where(m => m.IsAlive && m.Team == 0).ToList();
            Assert.AreEqual(8, mines.Count, "eight mines");
            Assert.IsTrue(mines.All(m => m.Position.Length() <= 12.01f), "within 12 m");
            var victim = world.SpawnVehicle("armored_car", 1, mines[0].Position + new Vector2(0f, 10f), 3.14f);
            world.Submit(new Command(CommandType.Move, 1, new[] { victim.Id }, mines[0].Position - new Vector2(0f, 8f)));
            Run(world, 6f);
            Assert.Less(victim.Hp, victim.MaxHp, "an enemy driving over one sets it off");
            Run(world, 55f);
            Assert.AreEqual(0, world.Mines.Count(m => m.IsAlive && m.Team == 0), "the rest clear themselves after 60 s");
        }

        [Test]
        public void AFieldTowerIsDroppedForAMinuteNeverIntoTheEnemyCamp()
        {
            var world = Field();
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            Assert.IsFalse(world.Submit(Command.Strike(0, "field_tower", new Vector2(78f, 78f))).Accepted, "not into the enemy camp");
            Assert.IsTrue(world.Submit(Command.Strike(0, "field_tower", new Vector2(0f, 0f))).Accepted);
            Run(world, 5f);
            var tower = world.VehicleList.FirstOrDefault(v => v.IsAlive && v.Team == 0 && v.Def.Static);
            Assert.IsNotNull(tower, "a tower landed");
            Assert.AreEqual("guard_tower", tower.Def.Id, "a guard tower below card rank 5");
            Run(world, 61f);
            Assert.IsFalse(tower.IsAlive, "gone after a minute");

            var ranked = Field();
            ranked.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            ranked.SetBoosts(0, null, strikeRank: _ => 5);
            Assert.IsTrue(ranked.Submit(Command.Strike(0, "field_tower", new Vector2(0f, 0f))).Accepted);
            Run(ranked, 5f);
            Assert.IsTrue(ranked.VehicleList.Any(v => v.IsAlive && v.Def.Id == "atgm_tower"), "an ATGM tower from rank 5");
        }

        [Test]
        public void SeadHitsTheNearestAirDefenceAndKnocksItOut()
        {
            var world = Field();
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
            var aa = world.SpawnVehicle("aa_vehicle", 1, new Vector2(10f, 0f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(2f, 0f), 0f);
            world.Submit(new Command(CommandType.Stop, 1, new[] { aa.Id, tank.Id }));
            var tankHp = tank.Hp;
            Assert.IsTrue(world.Submit(Command.Strike(0, "sead_strike", new Vector2(0f, 0f))).Accepted);
            Run(world, 3f);
            Assert.Less(aa.Hp, aa.MaxHp - 400f, "about 500 damage on the anti-air vehicle");
            Assert.IsTrue(aa.Stunned || !aa.IsAlive, "and knocked out");
            Assert.AreEqual(tankHp, tank.Hp, 1f, "the tank beside it is not the missile's target");
            Run(world, 8.5f);
            Assert.IsFalse(aa.Stunned, "for 8 s");
        }

        [Test]
        public void FromRankSevenTheAirstrikeLineIsLonger()
        {
            int Bombs(int rank)
            {
                var world = Field();
                world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f));
                world.SetBoosts(0, null, strikeRank: _ => rank);
                world.Submit(Command.Strike(0, "airstrike", new Vector2(-20f, 0f), new Vector2(20f, 0f)));
                var n = 0;
                Run(world, 6f, e =>
                {
                    if (e.Kind == SimEventKind.StrikeImpact && e.DefId == "airstrike") n++;
                });
                return n;
            }
            Assert.AreEqual(8, Bombs(6));
            Assert.AreEqual(11, Bombs(7), "40 % more bombs along a 40 % longer line");
        }
    }
}
