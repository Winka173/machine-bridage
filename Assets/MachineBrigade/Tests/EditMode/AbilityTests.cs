using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Tests
{
    /// <summary>Ammunition, support auras, mines, jammers and the skills of elite units and bosses.</summary>
    public class AbilityTests
    {
        /// <summary>An empty 160 m field with the shipped catalog; team 0 lives at (-60,-60).</summary>
        private static SimWorld Field() =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 160f,
                new[] { new TeamStart(0, new Vector2(-60f, -60f)), new TeamStart(1, new Vector2(60f, 60f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void LongRangeLauncherRunsDryThenFightsWithItsMachineGun()
        {
            var world = Field();
            var launcher = world.SpawnVehicle("heavy_rocket_artillery", 0, new Vector2(0f, -40f), 0f);
            var targets = new List<Vehicle>();
            for (var i = 0; i < 6; i++) targets.Add(world.SpawnVehicle("heavy_tank", 1, new Vector2(i * 8f - 20f, 60f), 3.14f));
            // A drone overhead spots for the launcher (team sight is shared).
            world.SpawnVehicle("recon_drone", 0, new Vector2(0f, -15f), 0f);
            Assert.AreEqual(3, launcher.Ammo(0), "starts with its salvos");
            var mg = 0;
            var jeep = false;
            for (var t = 0f; t < 90f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == launcher.Id && e.Mount == 1) mg++;
                world.ClearEvents();
                // One jeep comes close once the last salvo is away (the gun waits for the salvo to finish).
                if (launcher.OutOfAmmo && mg == 0 && !jeep)
                {
                    world.SpawnVehicle("scout_jeep", 1, launcher.Position + new Vector2(0f, 18f), 3.14f);
                    jeep = true;
                }
                if (launcher.OutOfAmmo && mg > 0) break;
            }
            Assert.IsTrue(launcher.OutOfAmmo, "three salvos and the rack is empty");
            Assert.Greater(mg, 0, "the machine gun keeps fighting once the rockets are gone");
        }

        [Test]
        public void VehiclesRearmAtHome()
        {
            var world = Field();
            var mortar = world.SpawnVehicle("mortar_carrier", 0, new Vector2(-58f, -58f), 0f);
            mortar.Weapons[0].Ammo = 0;
            // Three times as fast as its reload in the field (plus the half-second aura tick).
            Run(world, Sim.Combat.CombatSystem.ReloadSeconds(mortar.Def.Mounts[0].Weapon) / 3f + 1f);
            Assert.AreEqual(mortar.Def.Mounts[0].Weapon.Ammo, mortar.Ammo(0), "back at the rally point the empty mortar reloads its whole magazine three times as fast");
        }

        [Test]
        public void EngineerRepairsAndTheAmmunitionCarrierRearmsNearbyVehicles()
        {
            var world = Field();
            world.SpawnVehicle("engineer_vehicle", 0, new Vector2(0f, 0f), 0f);
            var tank = world.SpawnVehicle("siege_tank", 0, new Vector2(8f, 0f), 0f);
            tank.Hp = tank.MaxHp * 0.4f;
            tank.Weapons[0].Ammo = 0;
            Run(world, 10f);
            Assert.Greater(tank.Hp, tank.MaxHp * 0.55f, "the engineer patches up the tank beside it");
            // Prompt 13 F.2: the engineer no longer rearms (the reload runs at its own pace)...
            var full = Sim.Combat.CombatSystem.ReloadSeconds(tank.Def.Mounts[0].Weapon);
            Assert.Greater(tank.Weapons[0].ReloadLeft, full - 12f, "the engineer does not reload it");
            // ...the ammunition carrier does, three times as fast.
            var carried = Field();
            carried.SpawnVehicle("ammo_carrier", 0, new Vector2(0f, 0f), 0f);
            var gun = carried.SpawnVehicle("siege_tank", 0, new Vector2(8f, 0f), 0f);
            gun.Weapons[0].Ammo = 0;
            Run(carried, 10f);
            Assert.Less(gun.Weapons[0].ReloadLeft, full - 20f, "its crew reloads three times as fast beside the carrier");
        }

        [Test]
        public void MineLayerLaysMinesThatBlowUpEnemies()
        {
            var world = Field();
            var layer = world.SpawnVehicle("mine_layer", 0, new Vector2(0f, -30f), 0f);
            world.Submit(new Command(CommandType.Move, 0, new[] { layer.Id }, new Vector2(0f, 20f)));
            Run(world, 14f);
            Assert.GreaterOrEqual(world.Mines.Count, 2, "mines are dropped along the way");
            var mine = world.Mines[0];
            Assert.IsFalse(mine.IsVisibleTo(1), "the enemy cannot see a mine from afar");
            var victim = world.SpawnVehicle("armored_car", 1, mine.Position + new Vector2(0f, 12f), 3.14f);
            world.Submit(new Command(CommandType.Move, 1, new[] { victim.Id }, mine.Position - new Vector2(0f, 10f)));
            var detonated = false;
            for (var t = 0f; t < 8f && !detonated; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events) detonated |= e.Kind == SimEventKind.MineDetonated;
                world.ClearEvents();
            }
            Assert.IsTrue(detonated, "driving over a mine sets it off");
            Assert.Less(victim.Hp, victim.MaxHp * 0.5f, "and wrecks a light vehicle");
        }

        [Test]
        public void JammerMakesGuidedMissilesMiss()
        {
            int Hits(bool jammer)
            {
                var world = Field();
                var target = world.SpawnVehicle("heavy_tank", 0, new Vector2(0f, 0f), 0f);
                if (jammer) world.SpawnVehicle("ew_jammer", 0, new Vector2(0f, -10f), 0f);
                world.SpawnVehicle("fpv_carrier", 1, new Vector2(0f, 30f), 3.14f);
                var hits = 0;
                for (var t = 0f; t < 30f; t += TestWorlds.Step)
                {
                    world.Step(TestWorlds.Step);
                    foreach (var e in world.Events)
                        if (e.Kind == SimEventKind.ProjectileImpact && e.Entity == target.Id && e.DefId == "fpv_swarm") hits++;
                    world.ClearEvents();
                }
                return hits;
            }
            var clean = Hits(false);
            var jammed = Hits(true);
            Assert.Greater(clean, 2, "drones strike home without a jammer");
            Assert.Less(jammed, clean / 2 + 1, "a jammer scrambles most of them");
        }

        [Test]
        public void EliteShieldSoaksDamage()
        {
            var world = Field();
            var elite = world.SpawnVehicle("elite_mbt", 1, new Vector2(0f, 20f), 3.14f);
            for (var i = 0; i < 4; i++) world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 5f - 8f, 2f), 0f);
            var shieldUsed = false;
            for (var t = 0f; t < 20f && !shieldUsed; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events) shieldUsed |= e.Kind == SimEventKind.SkillUsed && e.Skill == SkillKind.Shield;
                world.ClearEvents();
            }
            Assert.IsTrue(shieldUsed, "an elite under fire raises its shield");
            Assert.IsTrue(elite.ShieldUp);
        }

        [Test]
        public void EmpStunsEnemyVehicles()
        {
            var world = Field();
            world.SpawnVehicle("elite_apc", 1, new Vector2(0f, 10f), 3.14f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var stunned = false;
            for (var t = 0f; t < 10f && !stunned; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                stunned |= tank.Stunned;
            }
            Assert.IsTrue(stunned, "the elite carrier's EMP knocks out a tank beside it");
        }
    }
}
