using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>The rest of the traits, modules and set behaviours: one quick check each that it does what its line says.</summary>
    public class GearTraitTests
    {
        private static VehicleBoost Traits(params GearTrait[] traits) =>
            new(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f, null, traits);

        private static VehicleBoost Module(SpecialModule module, float power, float power2 = 0f) =>
            new(1f, 1f, 1f, 1f, 1f, 0f, module, power, null, null, power2);

        private static SimWorld World(VehicleBoost boost, SimWorld world = null)
        {
            world ??= TestWorlds.World();
            world.SetBoosts(0, _ => boost);
            return world;
        }

        private static SimWorld RealWorld(VehicleBoost boost) =>
            World(boost, new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>())));

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

        private static float Hit(SimWorld world, Vehicle target, float amount, WeaponDef weapon, HitKind kind = HitKind.Direct, bool indirect = false,
            Vehicle attacker = null)
        {
            var before = target.Hp;
            world.Damage.Apply(target, amount, weapon.DamageType, new HitInfo(attacker, attacker?.Team ?? 1, weapon, target.Position + new Vector2(0f, 5f), kind, indirect));
            return before - target.Hp;
        }

        private static HitInfo Direct(Vehicle attacker, WeaponDef weapon) => new(attacker, attacker.Team, weapon, attacker.Position, HitKind.Direct, weapon.Indirect);

        // ------------------------------------------------------------------ weapon traits

        [Test]
        public void WeaponTraitsShapeTheirShots()
        {
            var world = World(Traits(new GearTrait(TraitId.Executioner, 0.4f), new GearTrait(TraitId.MomentumGun, 0.05f),
                new GearTrait(TraitId.TandemWarhead, 0.1f), new GearTrait(TraitId.SetDeepStrike, 0.15f)));
            var shooter = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var target = world.SpawnVehicle("decoy", 1, new Vector2(40f, 0f), 0f);
            Assert.AreEqual(1f, world.Gear.Outgoing(shooter, target, Direct(shooter, shooter.Weapon)), 1e-5f);
            target.Hp = target.MaxHp * 0.25f;
            Assert.AreEqual(1.4f, world.Gear.Outgoing(shooter, target, Direct(shooter, shooter.Weapon)), 1e-5f, "Executioner below 30 % health");

            // Momentum: three hits in a row on one target make the next shot 15 % harder.
            for (var i = 0; i < 3; i++)
            {
                var p = new Projectile(shooter.Id, 0, shooter.Weapon, target.Position, target.Id, 0f) { Origin = shooter.Position, Shooter = shooter, Main = true };
                world.Damage.ResolveImpact(p);
            }
            // A gun firing once a second counts two thirds of a step a hit (the proc coefficient).
            Assert.AreEqual(2, shooter.Gear.Streak);
            var near = world.Gear.Shot(shooter, 0, target.Id, shooter.Position + new Vector2(5f, 0f), shooter.Weapon, false);
            Assert.AreEqual(1.1f, near.Scale, 1e-3f);
            // Deep Strike: beyond 70 % of the range.
            var far = world.Gear.Shot(shooter, 0, target.Id, shooter.Position + new Vector2(18f, 0f), shooter.Weapon, false);
            Assert.AreEqual(1.1f * 1.15f, far.Scale, 1e-3f);
            // Tandem: missiles, not shells; and more against heavy armour.
            Assert.IsFalse(near.Tandem);
            Assert.IsTrue(world.Gear.Shot(shooter, 0, target.Id, target.Position, TestWorlds.Missile, false).Tandem);
            target.Hp = target.MaxHp;
            Assert.AreEqual(1.1f, world.Gear.Outgoing(shooter, target, Direct(shooter, TestWorlds.Missile)), 1e-5f);
        }

        [Test]
        public void TandemRoundsGoThroughActiveProtection()
        {
            var world = TestWorlds.World();
            world.SetBoosts(0, _ => Traits(new GearTrait(TraitId.TandemWarhead, 0.1f)));
            world.SetBoosts(1, _ => Module(SpecialModule.TrophyAps, 2f, 20f));
            var hunter = world.SpawnVehicle("hunter", 0, new Vector2(0f, 0f), 0f);
            var tank = world.SpawnVehicle("tank", 1, new Vector2(0f, 25f), 0f);
            var events = Run(world, 6f);
            Assert.AreEqual(0, events.Count(e => e.Kind == SimEventKind.Intercepted), "no interceptor stops a tandem warhead");
            Assert.Less(tank.Hp, tank.MaxHp);
            Assert.IsNotNull(hunter);
        }

        [Test]
        public void WeaponCopiesForClusterHotSwapAndPintle()
        {
            var arty = World(Traits(new GearTrait(TraitId.ClusterWarhead, 4f))).SpawnVehicle("arty", 0, new Vector2(0f, 0f), 0f);
            Assert.AreEqual(4, arty.Weapon.Cluster.Count, "Cluster Warhead on a howitzer");
            Assert.IsNull(TestWorlds.Howitzer.Cluster);
            var tank = World(Traits(new GearTrait(TraitId.ClusterWarhead, 4f))).SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            Assert.IsNull(tank.Weapon.Cluster, "no effect on a direct-fire gun");

            var real = RealWorld(Traits(new GearTrait(TraitId.HotSwap, 0.4f), new GearTrait(TraitId.SkywardPintle, 0.6f)));
            var mlrs = real.SpawnVehicle("mlrs", 0, new Vector2(0f, 0f), 0f);
            Assert.AreEqual(real.Catalog.Vehicle("mlrs").Weapon.MagazineReload * 0.6f, mlrs.Weapon.MagazineReload, 1e-3f);
            Assert.AreEqual(1f, real.Gear.ReloadRate(mlrs, out var onTheMove));
            Assert.IsTrue(onTheMove, "Hot Swap reloads on the move");

            // A vehicle with a secondary machine gun that cannot hit aircraft: the pintle lets it.
            var def = real.Catalog.Vehicles.Values.First(d => !d.Flying && !d.Static && d.Mounts.Skip(1).Any(m => m.Weapon.Projectile == ProjectileKind.Bullet && !m.Weapon.CanTarget(true)));
            var gunner = real.SpawnVehicle(def.Id, 0, new Vector2(20f, 0f), 0f);
            var mount = Enumerable.Range(1, def.Mounts.Count - 1).First(i => def.Mounts[i].Weapon.Projectile == ProjectileKind.Bullet && !def.Mounts[i].Weapon.CanTarget(true));
            Assert.IsTrue(gunner.Arm(mount).CanTarget(true), def.Id);
            Assert.AreEqual(0.6f, real.Gear.PintleScale(gunner, mount, true), 1e-5f);
            Assert.AreEqual(1f, real.Gear.PintleScale(gunner, mount, false), 1e-5f);
        }

        [Test]
        public void FireControlLeadsAndTightensAgainstMovingTargets()
        {
            var world = World(Traits(new GearTrait(TraitId.FireControlComputer, 0.5f)));
            var arty = world.SpawnVehicle("arty", 0, new Vector2(0f, 0f), 0f);
            var runner = world.SpawnVehicle("decoy", 1, new Vector2(30f, 0f), 0f);
            runner.Speed = 5f;
            runner.Heading = 0f;
            var lead = world.Gear.Lead(arty, 0, runner, runner.Position, arty.Weapon);
            Assert.Greater(lead.Y, runner.Position.Y + 1f, "aims ahead of the target along its heading");
            Assert.AreEqual(0.5f, world.Gear.SpreadFactor(arty, 0, runner, 0f), 1e-5f);
            runner.Speed = 0f;
            Assert.AreEqual(runner.Position, world.Gear.Lead(arty, 0, runner, runner.Position, arty.Weapon));
        }

        // ------------------------------------------------------------------ armour, engine and repair traits

        [Test]
        public void AdaptivePlatingLearnsTheDamageType()
        {
            var world = World(Traits(new GearTrait(TraitId.AdaptivePlating, 0.05f)));
            var tank = world.SpawnVehicle("decoy", 0, new Vector2(0f, 0f), 0f);
            for (var i = 0; i < 4; i++) Hit(world, tank, 10f, TestWorlds.Gun);
            Assert.AreEqual(80f, Hit(world, tank, 100f, TestWorlds.Gun), 1e-3f, "four stacks against armour-piercing");
            Assert.AreEqual(60f, Hit(world, tank, 100f, TestWorlds.Shell), 1e-3f, "high explosive is not resisted yet (0.6 against heavy)");
            Run(world, 6.5f);
            Assert.AreEqual(100f, Hit(world, tank, 100f, TestWorlds.Gun), 1e-3f, "and it fades after 6 s");
        }

        [Test]
        public void EngineTraitsBurstOnTheirCues()
        {
            var world = World(Traits(new GearTrait(TraitId.NitroDash, 1.6f, 25f), new GearTrait(TraitId.RapidDeployment, 10f)));
            var tank = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var plain = world.SpawnVehicle("tank", 1, new Vector2(60f, 60f), 0f);
            Run(world, 0.1f);
            Assert.AreEqual(1.4f, tank.SpeedGear, 1e-4f, "Rapid Deployment");
            Assert.AreEqual(0.8f, Hit(world, tank, 100f, TestWorlds.Gun) / Hit(world, plain, 100f, TestWorlds.Gun), 1e-3f);
            tank.LastHitTime = world.Time;
            Run(world, 0.1f);
            Assert.IsTrue(tank.Overdriven, "Nitro Dash when hit");
            Run(world, 10.5f);
            Assert.AreEqual(1f, tank.SpeedGear, 1e-4f, "the deployment window is over");

            var scoot = World(Traits(new GearTrait(TraitId.ShootAndScoot, 0.4f, 0.2f)));
            var gun = scoot.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var mark = scoot.SpawnVehicle("decoy", 1, new Vector2(10f, 0f), 0f);
            var events = Run(scoot, 1.2f);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "shoot_and_scoot"), "the first shot after stopping");
            Assert.AreEqual(1.2f, gun.SpeedGear, 1e-4f, "then a burst of speed");
            Assert.IsNotNull(mark);

            var jet = World(Traits(new GearTrait(TraitId.AfterburnerReserve, 0.5f)));
            var heli = jet.SpawnVehicle("heli", 0, new Vector2(0f, 0f), 0f);
            heli.Hp = heli.MaxHp * 0.3f;
            Run(jet, 0.1f);
            Assert.IsTrue(heli.Overdriven && heli.FlaresUp, "Afterburner Reserve below 40 %");
        }

        [Test]
        public void RepairTraitsMendAndRearm()
        {
            var world = World(new VehicleBoost(1f, 1f, 1f, 1f, 1f, 0.01f, SpecialModule.None, 0f, null,
                new[] { new GearTrait(TraitId.FieldMechanics, 0.01f, 12f), new GearTrait(TraitId.CombatWelder, 0.5f), new GearTrait(TraitId.AmmoCarrier, 0.5f, 12f) }));
            var medic = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var patient = world.SpawnVehicle("tank", 0, new Vector2(6f, 0f), 0f);
            patient.Gear = null;
            patient.Regen = 0f;
            patient.Hp = patient.MaxHp * 0.5f;
            patient.LastHitTime = -100.0;
            medic.Hp = medic.MaxHp * 0.5f;
            for (var i = 0; i < 20; i++)
            {
                medic.LastHitTime = world.Time; // under fire the whole second
                Run(world, TestWorlds.Step);
            }
            Assert.AreEqual(patient.MaxHp * 0.51f, patient.Hp, patient.MaxHp * 0.0051f, "Field Mechanics: 1 % a second to an ally out of combat");
            Assert.AreEqual(medic.MaxHp * (0.5f + 0.01f * 0.5f), medic.Hp, medic.MaxHp * 0.0011f, "Combat Welder: half its repair under fire");
            Assert.AreEqual(1.5f, world.Gear.ReloadRate(patient, out var moving), 1e-5f, "Ammo Carrier: allies reload half as fast again");
            Assert.IsTrue(moving);
        }

        // ------------------------------------------------------------------ optics

        [Test]
        public void OpticsSeeThroughSmokeMarkAndRevealArtillery()
        {
            SimWorld Watch(VehicleBoost boost, out Vehicle target)
            {
                var w = World(boost);
                w.SpawnVehicle("decoy", 0, new Vector2(0f, 0f), 0f);
                target = w.SpawnVehicle("decoy", 1, new Vector2(15f, 0f), 0f);
                w.Strikes.AddSmoke(1, target.Position, 6f, 30f);
                Run(w, 0.2f);
                return w;
            }
            Watch(Traits(new GearTrait(TraitId.ThermalImager, 1f)), out var seen);
            Assert.IsTrue(seen.IsVisibleTo(0), "a thermal imager sees into the smoke");
            Watch(VehicleBoost.None, out var hidden);
            Assert.IsFalse(hidden.IsVisibleTo(0), "plain optics do not");
            Watch(Traits(new GearTrait(TraitId.ThermalImager, 0.6f)), out var epic);
            Assert.IsTrue(epic.IsVisibleTo(0), "15 m is within 60 % of a 30 m sight");

            // Laser Designator: artillery reaches marked targets from further.
            var world = World(Traits(new GearTrait(TraitId.LaserDesignator, 0.1f, 4f)));
            var arty = world.SpawnVehicle("arty", 0, new Vector2(0f, 0f), 0f);
            var marked = world.SpawnVehicle("decoy", 1, new Vector2(30f, 0f), 0f);
            world.Status.Mark(marked, 0.1f, 4f, 0, 0.1f);
            Assert.AreEqual(1.1f, world.Gear.Reach(arty, marked, arty.Weapon), 1e-5f);
            Assert.AreEqual(1f, world.Gear.Reach(arty, marked, TestWorlds.Gun), 1e-5f, "direct fire is not helped");

            // Counter-battery radar: enemy artillery that fires nearby is revealed, and takes more from artillery.
            var radar = TestWorlds.World();
            radar.SetBoosts(0, _ => Traits(new GearTrait(TraitId.CounterBatteryRadar, 0.2f, 80f, 5f)));
            // The enemy gun sees further (45 m) than anything of ours (30 m): only the radar can show it.
            var far = new float[(int)StatId.Count];
            far[(int)StatId.Vision] = 0.5f;
            radar.SetBoosts(1, _ => new VehicleBoost(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f, far));
            var station = radar.SpawnVehicle("decoy", 0, new Vector2(0f, 0f), 0f);
            var ourGun = radar.SpawnVehicle("arty", 0, new Vector2(0f, -5f), 0f);
            var enemyGun = radar.SpawnVehicle("arty", 1, new Vector2(0f, 45f), 3.14f);
            radar.SpawnVehicle("decoy", 0, new Vector2(0f, 5f), 0f); // what the enemy gun shoots at, 40 m off
            radar.Step(TestWorlds.Step); // sight is worked out before anyone fires
            Assert.IsFalse(enemyGun.IsVisibleTo(0), "out of our sight at first");
            var events = Run(radar, 4f);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "counter_battery_radar"));
            Assert.IsTrue(enemyGun.IsVisibleTo(0), "the enemy gun is revealed beyond sight");
            Assert.AreEqual(1.2f, radar.Gear.Outgoing(ourGun, enemyGun, Direct(ourGun, ourGun.Weapon)), 1e-4f);
            Assert.IsNotNull(station);
        }

        [Test]
        public void JammersGhostNetsAndDecoysTurnRoundsAway()
        {
            var world = World(Traits(new GearTrait(TraitId.EwJammer, 2f, 15f, 12f), new GearTrait(TraitId.SetGhostNet, 0.15f)));
            var jammer = world.SpawnVehicle("decoy", 0, new Vector2(0f, 0f), 0f);
            var friend = world.SpawnVehicle("decoy", 0, new Vector2(5f, 0f), 0f);
            friend.Gear = null;
            world.SpawnVehicle("hunter", 1, new Vector2(0f, 28f), 0f);
            var events = Run(world, 4f);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "ew_jammer"), "a missile in the air sets the jammer off");
            Assert.AreEqual(jammer.MaxHp, jammer.Hp, "the first missile loses lock (Ghost Net) or is jammed");

            var ghost = World(Traits(new GearTrait(TraitId.SetGhostNet, 0.15f)));
            var target = ghost.SpawnVehicle("decoy", 0, new Vector2(0f, 0f), 0f);
            var shooter = ghost.SpawnVehicle("hunter", 1, new Vector2(0f, 20f), 0f);
            Projectile Missile() => new(shooter.Id, 1, TestWorlds.Missile, target.Position, target.Id, 0f) { Origin = shooter.Position, Miss = new Vector2(6f, 0f) };
            Assert.IsTrue(ghost.Gear.Lure(target, Missile(), out _), "the first missile each life loses lock");
            Assert.IsFalse(ghost.Gear.Lure(target, Missile(), out _), "but only the first");

            var decoy = World(Module(SpecialModule.DecoyLauncher, 4f, 35f));
            var tank = decoy.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var enemy = decoy.SpawnVehicle("arty", 1, new Vector2(0f, 25f), 0f);
            var decoyEvents = Run(decoy, 8f);
            Assert.IsTrue(decoyEvents.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "decoy_launcher"), "a shell on its way pops the decoy");
            Assert.Greater(tank.Gear.DecoyUntil, 0.0);
            Assert.IsNotNull(enemy);
        }

        // ------------------------------------------------------------------ set behaviours

        [Test]
        public void MoreSetBehaviours()
        {
            // Vulcan's Firestorm: burning enemies take 10 % more, and the fire jumps when one dies.
            var fire = World(Traits(new GearTrait(TraitId.IncendiaryRounds, 0.2f), new GearTrait(TraitId.SetFirestorm, 0.1f, 6f)));
            var torch = fire.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var burning = fire.SpawnVehicle("boomer", 1, new Vector2(40f, 0f), 0f);
            var neighbour = fire.SpawnVehicle("decoy", 1, new Vector2(44f, 0f), 0f);
            var plain = fire.SpawnVehicle("decoy", 1, new Vector2(40f, 30f), 0f);
            var p = new Projectile(torch.Id, 0, TestWorlds.Missile, burning.Position, burning.Id, 0f) { Origin = torch.Position, Shooter = torch, Main = true, DamageScale = 0.2f };
            fire.Damage.ResolveImpact(p);
            Assert.IsTrue(fire.Status.Burning(burning));
            Assert.IsTrue(burning.Statuses[(int)StatusKind.Burn].Flag);
            fire.Damage.Apply(burning, 10000f, DamageType.HighExplosive);
            Assert.IsTrue(fire.Status.Burning(neighbour), "the fire jumps to the nearest friend of the dead");
            Assert.AreEqual(1.1f, Hit(fire, neighbour, 100f, TestWorlds.Gun) / Hit(fire, plain, 100f, TestWorlds.Gun), 1e-3f);

            // Aegis Systems' Shared Shield: the weakest ally nearby gets a barrier.
            var shield = World(Traits(new GearTrait(TraitId.SetSharedShield, 0.12f, 25f, 12f)));
            shield.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var weak = shield.SpawnVehicle("mortar", 0, new Vector2(5f, 0f), 0f);
            weak.Gear = null;
            weak.Hp = weak.MaxHp * 0.3f;
            Run(shield, 0.1f);
            Assert.AreEqual(weak.MaxHp * 0.12f, weak.Barrier, 1e-3f);

            // Hivemind's Swarm: a kill launches a drone at the nearest enemy.
            var swarm = World(Traits(new GearTrait(TraitId.SetSwarm, 10f)));
            var hive = swarm.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var prey = swarm.SpawnVehicle("boomer", 1, new Vector2(10f, 0f), 0f);
            swarm.SpawnVehicle("decoy", 1, new Vector2(25f, 0f), 0f);
            var events = Run(swarm, 2f);
            Assert.IsFalse(prey.IsAlive);
            Assert.AreEqual(1, events.Count(e => e.Kind == SimEventKind.WeaponFired && e.DefId == "gear_drone"), "one drone for the kill");
            Assert.IsNotNull(hive);

            // Stormfront's Strafing Run: every fourth salvo twice over, and flares by themselves.
            var storm = World(Traits(new GearTrait(TraitId.SetStrafingRun, 2f, 30f)));
            var launcher = storm.SpawnVehicle("launcher", 0, new Vector2(0f, 0f), 0f);
            Assert.AreEqual(0, storm.Gear.ExtraRounds(launcher, launcher.Weapon, out _), "a plain first salvo");
            Assert.AreEqual(6, storm.Gear.ExtraRounds(launcher, launcher.Weapon, out var per), "the second pull doubles the salvo");
            Assert.AreEqual(1f, per, 1e-5f, "at full weight");
            var flyer = World(Traits(new GearTrait(TraitId.SetStrafingRun, 4f, 30f)));
            var heli = flyer.SpawnVehicle("heli", 0, new Vector2(0f, 0f), 0f);
            Run(flyer, 0.1f);
            Assert.IsTrue(heli.FlaresUp, "and flares by themselves");
        }

        // ------------------------------------------------------------------ modules

        [Test]
        public void MoreModules()
        {
            // Rally Horn: allies round it hit harder.
            var rally = World(Module(SpecialModule.RallyHorn, 0.1f, 12f));
            var horn = rally.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var buddy = rally.SpawnVehicle("tank", 0, new Vector2(6f, 0f), 0f);
            var target = rally.SpawnVehicle("decoy", 1, new Vector2(60f, 60f), 0f);
            Run(rally, 0.6f);
            Assert.AreEqual(1.1f, rally.Gear.Outgoing(buddy, target, Direct(buddy, buddy.Weapon)), 1e-5f);
            Assert.IsNotNull(horn);

            // Aegis Dome: three allies under fire round it, all invulnerable.
            var dome = World(Module(SpecialModule.AegisDome, 2f));
            var core = dome.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var a = dome.SpawnVehicle("tank", 0, new Vector2(4f, 0f), 0f);
            var b = dome.SpawnVehicle("tank", 0, new Vector2(-4f, 0f), 0f);
            foreach (var v in new[] { core, a, b }) v.LastHitTime = 0.0;
            Run(dome, 0.6f);
            Assert.Greater(a.ImmuneUntil, dome.Time);
            Assert.AreEqual(0f, Hit(dome, b, 100f, TestWorlds.Gun), "no damage under the dome");

            // Smoke Dischargers at Legendary fire twice.
            var smoke = World(Module(SpecialModule.SmokeDischarger, 10f, 1f));
            var tank = smoke.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            tank.Hp = tank.MaxHp * 0.45f;
            Run(smoke, 0.1f);
            Assert.AreEqual(1, smoke.Strikes.Smoke.Count);
            tank.Hp = tank.MaxHp * 0.2f;
            Run(smoke, 0.1f);
            Assert.AreEqual(2, smoke.Strikes.Smoke.Count, "again below a quarter");

            // Flare Dispenser: flares when a missile is on its way.
            var flares = World(Module(SpecialModule.FlareDispenser, 3f, 25f));
            var jet = flares.SpawnVehicle("decoy", 0, new Vector2(0f, 0f), 0f);
            flares.SpawnVehicle("hunter", 1, new Vector2(0f, 26f), 0f);
            var events = Run(flares, 4f);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "flare_dispenser"));
            Assert.IsNotNull(jet);

            // Mine Dispenser: mines on the move only.
            var mines = World(Module(SpecialModule.MineDispenser, 2f, 2f));
            var layer = mines.SpawnVehicle("tank", 0, new Vector2(-30f, 0f), 0f);
            Run(mines, 5f);
            Assert.AreEqual(0, mines.Mines.Count, "standing still: none");
            mines.Submit(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Move, 0, new[] { layer.Id }, new Vector2(30f, 0f)));
            Run(mines, 8f);
            Assert.That(mines.Mines.Count, Is.InRange(1, 2), "on the move: up to two");

            // Uplink Barrage: mortar rounds walk onto its target.
            var uplink = World(Module(SpecialModule.UplinkBarrage, 3f, 45f));
            uplink.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var anvil = uplink.SpawnVehicle("decoy", 1, new Vector2(12f, 0f), 0f);
            var shells = Run(uplink, 9f);
            Assert.GreaterOrEqual(shells.Count(e => e.Kind == SimEventKind.Explosion), 3, "three rounds");
            Assert.IsTrue(shells.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "uplink_barrage"));
            Assert.Less(anvil.Hp, anvil.MaxHp);

            // Mine Rollers at Epic: the first mine every 30 s goes off harmlessly, then the resistance counts.
            var roller = World(new VehicleBoost(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f, Stats(StatId.ResistMine, 0.5f),
                new[] { new GearTrait(TraitId.MineSweep, 1f) }));
            var sweeper = roller.SpawnVehicle("decoy", 0, new Vector2(0f, 0f), 0f);
            Assert.AreEqual(0f, Hit(roller, sweeper, 100f, TestWorlds.Shell, HitKind.Mine));
            Assert.AreEqual(30f, Hit(roller, sweeper, 100f, TestWorlds.Shell, HitKind.Mine), 1e-3f, "then half (HE is 0.6 against heavy)");
        }

        private static float[] Stats(StatId stat, float value)
        {
            var stats = new float[(int)StatId.Count];
            stats[(int)stat] = value;
            return stats;
        }
    }
}
