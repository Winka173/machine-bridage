using System;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 16 A-D (DECISIONS 15A): Lighthouse Bay's sea lanes in reach as designed, Leviathan with its
    /// fleet and its armour by face, its CIWS against the right rounds, its phase 3 run with its clock, and
    /// Boss Rush going to sea for it.
    /// </summary>
    public class Prompt16NavalTests
    {
        private const float Step = 0.05f;

        private static SimWorld Bay(int seed = 1) => new(GameContent.LoadCatalog(), GameContent.LoadMap("lighthousebay_sandbox"), seed);

        private static Sim.Entities.Vehicle Leviathan(SimWorld world, string lane = "far", float u = -40f)
        {
            var sea = world.Map.Sea!;
            return world.SpawnVehicle("leviathan", 1, sea.At(u, sea.Lane(lane)!.W), 0f);
        }

        [Test]
        public void TheSeaLanesAreInReachAsDesigned()
        {
            var world = Bay();
            var sea = world.Map.Sea;
            Assert.IsNotNull(sea, "Lighthouse Bay has its sea");
            Assert.AreEqual(3, sea.Lanes.Count);
            Assert.AreEqual(2, sea.Batteries.Count);
            Assert.AreEqual(3, sea.Piers.Count);
            var catalog = world.Catalog;
            var ship = catalog.Vehicle("leviathan");
            var near = sea.Lane("near")!;
            var far = sea.Lane("far")!;
            var tank = catalog.Vehicle("main_battle_tank").Weapon.Range;
            // Short range: the direct-fire tanks and fighting vehicles (medium-range tank hunters, 38-42 m, also reach it
            // from the headland's rocky flanks beside the lighthouse: DECISIONS 15A).
            var longShort = new[] { "main_battle_tank", "heavy_tank", "twin_tank", "light_tank", "ifv", "armored_car" }
                .Max(id => catalog.Vehicle(id).Mounts.Where(m => m.Weapon.CanTarget(false)).Max(m => m.Weapon.Range));
            // From a pier head a battle tank reaches the near lane.
            foreach (var pier in sea.Piers.Take(2))
                Assert.LessOrEqual(near.W - sea.Frame(pier).Y - ship.Radius, tank, "a tank on a pier head reaches the near lane");
            // From anywhere else on land, not even the longest direct-fire gun does.
            var best = float.MaxValue;
            var farBest = float.MaxValue;
            for (var x = -148f; x <= 148f; x += 2f)
            for (var z = -148f; z <= 148f; z += 2f)
            {
                var p = new Vector2(x, z);
                if (!world.Grid.IsWalkable(p) || sea.IsSea(p)) continue;
                var f = sea.Frame(p);
                farBest = MathF.Min(farBest, far.W - f.Y);
                if (sea.Piers.Any(pier => MathF.Abs(sea.Frame(pier).X - f.X) < 10f)) continue;
                best = MathF.Min(best, near.W - f.Y);
            }
            Assert.Greater(best - ship.Radius, longShort, "off the pier heads no short-range gun reaches the near lane");
            Assert.LessOrEqual(farBest - ship.Radius, catalog.Vehicle("artillery").Weapon.Range, "artillery on the shore reaches the far lane");
            // The coastal batteries reach the far lane where it runs past them; aircraft fly out over it.
            var gun = catalog.Vehicle("coastal_battery");
            Assert.IsTrue(gun.NavalOnly);
            foreach (var b in sea.Batteries)
            {
                var f = sea.Frame(b.At);
                var nearest = sea.At(Math.Clamp(f.X, -far.Patrol, far.Patrol), far.W);
                Assert.LessOrEqual(Vector2.Distance(b.At, nearest) - ship.Radius, gun.Weapon.Range, b.Id + " reaches the far lane");
            }
            Assert.IsTrue(catalog.Vehicle("attack_jet").Flying);
        }

        [Test]
        public void LeviathanSailsWithItsFleetOnTheLanesAndItsArmourIsByFace()
        {
            var world = Bay();
            var boss = Leviathan(world);
            var sea = world.Map.Sea!;
            var clock = System.Diagnostics.Stopwatch.StartNew();
            for (var t = 0f; t < 20f; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
            }
            var ms = clock.Elapsed.TotalMilliseconds / (20f / Step);
            Debug.Log($"PROMPT16 fleet step {ms:0.00} ms");
            var ships = world.Vehicles.Where(v => v.IsAlive && v.Def.Naval != null).ToList();
            Assert.AreEqual(1, ships.Count(v => v.Def.Id == "sea_cruiser"), "DECISIONS 20Y: the missile cruiser");
            Assert.AreEqual(1, ships.Count(v => v.Def.Id == "sea_corvette"));
            Assert.AreEqual(3, ships.Count(v => v.Def.Id == "missile_boat"));
            foreach (var v in ships) Assert.IsTrue(sea.IsSea(v.Position), v.Def.Id + " stays on the water");
            Assert.AreEqual(sea.Lane("far")!.W, sea.Frame(boss.Position).Y, 3f, "phase 1: the far lane");
            // DECISIONS 20Y: no ship of the fleet sails inside another's hull (the escorts abeam on the shore side).
            for (var i = 0; i < ships.Count; i++)
            for (var k = i + 1; k < ships.Count; k++)
            {
                var a = sea.Frame(ships[i].Position);
                var b = sea.Frame(ships[k].Position);
                var apart = MathF.Abs(a.X - b.X) >= (ships[i].Def.Length + ships[k].Def.Length) * 0.5f ||
                            MathF.Abs(a.Y - b.Y) >= (ships[i].Def.Width + ships[k].Def.Width) * 0.5f;
                Assert.IsTrue(apart, $"{ships[i].Def.Id} and {ships[k].Def.Id} clear of each other");
            }
            Assert.AreEqual(14, boss.Def.Parts.Count);
            Assert.AreEqual(4, boss.ArmourOn(ArmorFace.Side), "its sides");
            Assert.AreEqual(2, boss.ArmourOn(ArmorFace.Top), "its deck");
            Assert.IsNotNull(boss.Aps, "its CIWS");
        }

        [Test]
        public void ItsCiwsTakesMissilesNeverShellsAndStopsWithBothMounts()
        {
            var world = Bay(3);
            world.RevealAll = true;
            world.SeaRules.FleetShare = 0f;
            var sea = world.Map.Sea!;
            var pier = sea.Frame(sea.Piers[0]);
            var boss = world.SpawnVehicle("leviathan", 1, sea.At(pier.X, pier.Y + 40f), 0f);
            boss.Landing = true;
            boss.HoldFire = true;
            var carrier = world.SpawnVehicle("atgm_tower", 0, sea.Piers[0], 0f);
            var gun = world.SpawnVehicle("artillery", 0, sea.At(pier.X, pier.Y - 40f), 0f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { carrier.Id, gun.Id }, target: boss.Id));
            int missiles = 0, shells = 0;
            void Run(float seconds)
            {
                for (var t = 0f; t < seconds; t += Step)
                {
                    world.Step(Step);
                    foreach (var e in world.Events)
                        if (e.Kind == SimEventKind.Intercepted)
                        {
                            if (e.DefId == "howitzer") shells++;
                            else missiles++;
                        }
                    world.ClearEvents();
                }
            }
            Run(16f);
            Assert.Greater(missiles, 0, "its CIWS shoots down the missiles");
            Assert.AreEqual(0, shells, "never the shells");
            for (var i = 0; i < boss.Def.Parts.Count; i++)
                if (boss.Def.Parts[i].Kind == "ciws") world.Bosses.Break(boss, i);
            Run(0.2f);
            Assert.IsNull(boss.Aps, "both CIWS broken: no point defence");
            missiles = 0;
            var before = boss.Hp;
            Run(16f);
            Assert.AreEqual(0, missiles, "nothing shot down any more");
            Assert.Less(boss.Hp, before, "the missiles get through");
        }

        [Test]
        public void InPhaseThreeItRunsForTheEdgeOnAClockAndGetsAway()
        {
            var world = Bay(5);
            world.SeaRules.FleetShare = 0f;
            var boss = Leviathan(world, "far", 20f);
            // Past its spawn grace (a newcomer takes a fifth of the damage for 5 s).
            for (var t = 0f; t < 6f; t += Step) world.Step(Step);
            // A raw blow (no armour in the way): past the first phase's mark.
            void Hit() => world.Damage.Apply(boss, boss.MaxHp * 0.35f, DamageType.HighExplosive, new HitInfo(null, 0, null, boss.Position, HitKind.Redirect, false));
            Hit();
            for (var t = 0f; t < 4f; t += Step) world.Step(Step);
            Assert.AreEqual("near", boss.NavalLane, "phase 2: in to the near lane");
            Hit();
            for (var t = 0f; t < 5f; t += Step) world.Step(Step);
            Assert.IsTrue(boss.Escaping, "phase 3: it runs");
            var first = boss.EscapeSeconds;
            Assert.That(first, Is.InRange(30f, 200f), "a clock the player can beat");
            for (var t = 0f; t < 10f; t += Step) world.Step(Step);
            Assert.Less(boss.EscapeSeconds, first, "the clock runs down");
            for (var t = 0f; t < 260f && !boss.Escaped; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.IsTrue(boss.Escaped, "it gets away at the end of the lane");
            Assert.IsTrue(boss.Invulnerable);
            Assert.AreEqual(1, world.SeaRules.Escapes);
        }

        [Test]
        public void BossRushGoesToSeaForLeviathanAndBack()
        {
            var catalog = GameContent.LoadCatalog();
            var land = new SimWorld(catalog, GameContent.LoadMap("ashfield_sandbox"), 1);
            var rules = new BossRushRules { Bosses = new[] { "leviathan", "behemoth" }, HomeMap = "ashfield" };
            var rush = new BossRushMode(rules);
            rush.Setup(land);
            for (var t = 0f; t < 12f && rush.SwitchTo == null; t += Step)
            {
                rush.Tick(land, Step);
                land.Step(Step);
            }
            Assert.IsNotNull(rush.SwitchTo, "a sea boss needs the sea");
            Assert.AreEqual("lighthousebay", rush.SwitchTo.Map);
            Assert.Greater(rush.SwitchTo.Army.Count, 0, "the army goes with it");
            var sea = new SimWorld(catalog, GameContent.LoadMap("lighthousebay_sandbox"), 1);
            var afloat = new BossRushMode(new BossRushRules { Bosses = rules.Bosses, HomeMap = "ashfield", Resume = rush.SwitchTo });
            afloat.Setup(sea);
            for (var t = 0f; t < 8f && !afloat.Boss.IsValid; t += Step)
            {
                afloat.Tick(sea, Step);
                sea.Step(Step);
            }
            Assert.IsTrue(sea.TryGetVehicle(afloat.Boss, out var ship) && ship.Def.Id == "leviathan", "Leviathan comes in on the sea");
            Assert.IsTrue(sea.Map.Sea!.IsSea(ship.Position));
            Assert.Greater(afloat.TimeUsed, 0.0, "the clock carries over");
            // Sunk: the next boss is back on the rush's own battlefield.
            ship.Hp = 0f;
            for (var t = 0f; t < 25f && afloat.SwitchTo == null; t += Step)
            {
                afloat.Tick(sea, Step);
                sea.Step(Step);
            }
            Assert.AreEqual("ashfield", afloat.SwitchTo?.Map);
            Assert.AreEqual(1, afloat.SwitchTo.Defeated);
        }
    }
}
