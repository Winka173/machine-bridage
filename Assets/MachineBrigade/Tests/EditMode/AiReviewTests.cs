using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The AI review: artillery that backs off along the map's edge instead of into it, crowds
    /// that step apart instead of locking up, invulnerable bastions nobody shoots at, and the
    /// quick modes' catch-up for the side that is losing.
    /// </summary>
    public class AiReviewTests
    {
        private static SimWorld Field(float size = 200f) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", size,
                new[] { new TeamStart(0, new Vector2(-size * 0.4f, -size * 0.4f)), new TeamStart(1, new Vector2(size * 0.4f, size * 0.4f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        private static void Run(SimWorld world, float seconds, Action each = null)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                each?.Invoke();
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void ArtilleryCaughtAtTheEdgeSlipsAlongItInsteadOfPushingOut()
        {
            var world = Field();
            var gun = world.SpawnVehicle("artillery", 0, new Vector2(-93f, 0f), MathF.PI * 0.5f);
            var threat = new Vector2(-76f, 0f);
            var escape = world.EscapeRoute(gun, threat, 30f);
            Assert.IsTrue(escape.HasValue, "there is a way out along the edge");
            var p = escape!.Value;
            Assert.Greater(Vector2.Distance(p, threat), Vector2.Distance(gun.Position, threat) + 8f, "it gains ground from the threat");
            Assert.Less(MathF.Max(MathF.Abs(p.X), MathF.Abs(p.Y)), world.Map.HalfSize - 4f, "and stays off the very edge");
            Assert.Greater(MathF.Abs(p.Y), 10f, "by sliding along the edge, not into it");
        }

        [Test]
        public void ArtilleryUnderTheGunsOfATankNeverDrivesIntoTheEdge()
        {
            var world = Field();
            var gun = world.SpawnVehicle("artillery", 0, new Vector2(-90f, -20f), MathF.PI * 1.5f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(-74f, -20f), MathF.PI * 1.5f);
            // Shielded so the tank leaves it alone: this is about where it drives, not whether it survives.
            gun.Invulnerable = true;
            var ai = new TacticalAi(0, 1);
            var closest = float.MaxValue;
            var gap = 0f;
            Run(world, 25f, () =>
            {
                ai.Tick(world, TestWorlds.Step);
                if (!gun.IsAlive) return;
                closest = MathF.Min(closest, world.Map.HalfSize - MathF.Max(MathF.Abs(gun.Position.X), MathF.Abs(gun.Position.Y)));
                if (tank.IsAlive) gap = MathF.Max(gap, Vector2.Distance(gun.Position, tank.Position));
            });
            Assert.Greater(closest, 2f, "backing away from the tank, the gun never ends up against the map's edge");
            // Straight back is the edge 10 m behind it (at most 22 m from the tank): it has to slide along it to open the range.
            Assert.Greater(gap, 25f, "it opens the range by sliding along the edge");
        }

        [Test]
        public void SiegeTankShellsAKnownTurretFromOutsideItsReach()
        {
            var world = Field();
            var turret = world.SpawnVehicle("heavy_turret", 1, new Vector2(0f, 30f), MathF.PI);
            var tank = world.SpawnVehicle("siege_tank", 0, new Vector2(0f, -55f), 0f);
            // Seen once (a scout drove past): it stays known.
            turret.VisibleToMask |= 1;
            var ai = new TacticalAi(0, 1);
            var reach = turret.Def.Weapon.Range + turret.Radius;
            var closest = float.MaxValue;
            var start = turret.Hp;
            Run(world, 120f, () =>
            {
                ai.Tick(world, TestWorlds.Step);
                closest = MathF.Min(closest, Vector2.Distance(tank.Position, turret.Position));
            });
            Assert.IsTrue(turret.IsVisibleTo(0), "a fixed defence once seen stays known");
            Assert.Greater(closest, reach, "the siege tank never drives into the turret's reach");
            Assert.Less(turret.Hp, start * 0.5f, "it shells the turret from outside it");
        }

        [Test]
        public void EmptyLauncherStandsStillAndReloadsItsWholeMagazine()
        {
            var world = Field();
            var grad = world.SpawnVehicle("grad_truck", 0, new Vector2(0f, 0f), 0f);
            grad.Weapons[0].Ammo = 0;
            var ai = new TacticalAi(0, 1);
            var seconds = Sim.Combat.CombatSystem.ReloadSeconds(grad.Def.Mounts[0].Weapon);
            Run(world, seconds * 0.5f, () => ai.Tick(world, TestWorlds.Step));
            Assert.IsTrue(grad.OutOfAmmo, "halfway through, still reloading");
            Assert.Greater(grad.ReloadProgress, 0.4f, "and the reload shows its progress");
            Run(world, seconds * 0.6f, () => ai.Tick(world, TestWorlds.Step));
            Assert.AreEqual(grad.Def.Mounts[0].Weapon.Ammo, grad.Ammo(0), "the whole magazine comes back at once");
        }

        [Test]
        public void FortressBuildingsPayABountyWhenKnockedDown()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_siege"), seed: 4);
            var mode = new SiegeMode();
            mode.Setup(world);
            Assert.GreaterOrEqual(mode.BountyTargets.Count, 10, "the fortress is full of buildings worth knocking down");
            world.TryGetEconomy(SiegeMode.PlayerTeam, out var economy);
            economy.Cp = 0f;
            world.TryGetProp(mode.BountyTargets[0], out var building);
            world.Damage.Apply(building, 1e7f, DamageType.HighExplosive);
            Run(world, 0.2f, () => mode.Tick(world, TestWorlds.Step));
            Assert.AreEqual(1, mode.BuildingsRazed);
            Assert.GreaterOrEqual(economy.Cp, 2f, "and pays the attacker on the spot");
        }

        [Test]
        public void TwoPackedGroupsSwappingSidesDoNotLockUp()
        {
            var world = Field(120f);
            var north = new List<EntityId>();
            var south = new List<EntityId>();
            for (var i = 0; i < 5; i++)
            {
                south.Add(world.SpawnVehicle("heavy_tank", 0, new Vector2(i * 3.2f - 6.4f, -7f), 0f).Id);
                north.Add(world.SpawnVehicle("heavy_tank", 0, new Vector2(i * 3.2f - 6.4f, 7f), MathF.PI).Id);
            }
            world.Submit(new Command(CommandType.Move, 0, south.ToArray(), new Vector2(0f, 26f)));
            world.Submit(new Command(CommandType.Move, 0, north.ToArray(), new Vector2(0f, -26f)));
            Run(world, 60f);
            var arrived = south.Count(id => world.TryGetVehicle(id, out var v) && v.Position.Y > 14f) +
                          north.Count(id => world.TryGetVehicle(id, out var v) && v.Position.Y < -14f);
            Assert.GreaterOrEqual(arrived, 9, "a knot of hulls pushing against each other breaks up and gets through");
        }

        [Test]
        public void NobodyShootsAtTheInvulnerableBastions()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 3);
            var mode = new ConquestMode(new ConquestRules { Outposts = false });
            mode.Setup(world);
            var bastion = world.VehicleList.First(v => v.Team == 1 && v.Invulnerable);
            var tanks = new List<Vehicle>();
            for (var i = 0; i < 3; i++)
                tanks.Add(world.SpawnVehicle("main_battle_tank", 0, bastion.Position + new Vector2(-24f + i * 5f, -24f), 0f));
            var ai = new TacticalAi(0, 1);
            var aimed = 0;
            Assert.IsFalse(world.Submit(new Command(CommandType.Attack, 0, new[] { tanks[0].Id }, target: bastion.Id)).Accepted,
                "an order to attack it is refused");
            Run(world, 12f, () =>
            {
                mode.Tick(world, TestWorlds.Step);
                ai.Tick(world, TestWorlds.Step);
                foreach (var t in tanks)
                    if (t.IsAlive && (t.Target == bastion.Id || t.Engaged == bastion.Id)) aimed++;
            });
            Assert.AreEqual(0, aimed, "no tank picks it as a target");
        }

        [Test]
        public void TheLosingSideIsReinforcedFasterAndPaidMoreForItsKills()
        {
            Assert.AreEqual(1f, EconomySystem.CatchUpFor(20, 24), 1e-4f, "a close fight changes nothing");
            Assert.AreEqual(1f, EconomySystem.CatchUpFor(2, 10), 1e-4f, "nor a board too small to judge");
            Assert.Greater(EconomySystem.CatchUpFor(20, 50), 1.1f, "a side at two fifths is boosted");
            Assert.AreEqual(1f + EconomySystem.MaxCatchUp, EconomySystem.CatchUpFor(5, 60), 1e-4f, "up to the cap");

            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 5);
            var mode = new ConquestMode(new ConquestRules { BaseDefences = false, Outposts = false });
            mode.Setup(world);
            Assert.IsTrue(world.CatchUp, "the quick modes turn it on");
            world.TryGetEconomy(0, out var small);
            world.TryGetEconomy(1, out var big);
            foreach (var v in world.VehicleList.ToList()) world.RemoveQuietly(v);
            world.SpawnVehicle("light_tank", 0, new Vector2(-60f, -60f), 0f);
            for (var i = 0; i < 8; i++) world.SpawnVehicle("heavy_tank", 1, new Vector2(60f + i * 4f, 60f), 0f);
            Run(world, 12f);
            Assert.Greater(small.CatchUp, 1.3f, "the outnumbered side's income is boosted");
            Assert.AreEqual(1f, big.CatchUp, 1e-3f, "the bigger army's is not");

            // The underdog's kill pays more than the same kill made by the bigger army.
            var victim = world.VehicleList.First(v => v.Team == 1);
            small.Cp = 0f;
            victim.LastAttackerTeam = 0;
            victim.LastHitTime = world.Time;
            world.Damage.Apply(victim, 1e7f, DamageType.HighExplosive);
            Run(world, TestWorlds.Step);
            var underdogPay = small.Cp;
            var prey = world.SpawnVehicle("heavy_tank", 0, new Vector2(-60f, -50f), 0f);
            Run(world, TestWorlds.Step);
            big.Cp = 0f;
            prey.LastAttackerTeam = 1;
            prey.LastHitTime = world.Time;
            world.Damage.Apply(prey, 1e7f, DamageType.HighExplosive);
            Run(world, TestWorlds.Step);
            Assert.Greater(underdogPay, big.Cp * 1.5f, "the bounty follows the odds");
        }
    }
}
