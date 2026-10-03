using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>Neutral watchtowers on the points, the air cap, ground units that ignore circling aircraft, bombs that land under the bomber.</summary>
    public class AirAndTowerTests
    {
        private static SimWorld Field() =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        private static void Run(SimWorld world, float seconds, System.Action each = null)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                each?.Invoke();
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void NeutralTowersGuardEveryPointFireOnBothSidesAndComeBack()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 7);
            var mode = new ConquestMode(new ConquestRules { BaseDefences = false });
            mode.Setup(world);
            var towers = world.VehicleList.Where(v => v.Team == Teams.Hostile).ToList();
            Assert.AreEqual(mode.Points.Count, towers.Count, "one neutral tower per point");

            var tower = towers[0];
            foreach (var team in new[] { 0, 1 })
            {
                var tank = world.SpawnVehicle("main_battle_tank", team, tower.Position + new Vector2(14f, 0f), 0f);
                var before = tank.Hp;
                Run(world, 6f, () => mode.Tick(world, TestWorlds.Step));
                Assert.Less(tank.Hp, before, $"the tower fires on team {team}");
                world.Damage.Apply(tank, 1e7f, DamageType.HighExplosive);
            }

            world.Damage.Apply(tower, 1e7f, DamageType.HighExplosive);
            Run(world, 1f, () => mode.Tick(world, TestWorlds.Step));
            Assert.AreEqual(mode.Points.Count - 1, world.VehicleList.Count(v => v.IsAlive && v.Team == Teams.Hostile));
            Run(world, Outposts.RespawnSeconds + 2f, () => mode.Tick(world, TestWorlds.Step));
            Assert.AreEqual(mode.Points.Count, world.VehicleList.Count(v => v.IsAlive && v.Team == Teams.Hostile), "and it stands again");
        }

        [Test]
        public void ASideFieldsAtMostSixAircraft()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 8);
            var mode = new ConquestMode(new ConquestRules { BaseDefences = false, Outposts = false });
            mode.Setup(world);
            world.TryGetEconomy(0, out var economy);
            for (var i = 0; i < TeamEconomy.MaxAircraft; i++)
            {
                economy.Cp = 100f;
                Assert.IsTrue(world.Submit(Command.Deploy(0, "scout_heli")).Accepted, $"aircraft {i + 1}");
            }
            economy.Cp = 100f;
            var refused = world.Submit(Command.Deploy(0, "scout_heli"));
            Assert.AreEqual(CommandError.AirAtCapacity, refused.Error, "the seventh is refused");
            Assert.IsTrue(world.Submit(Command.Deploy(0, "main_battle_tank")).Accepted, "ground vehicles still come");
        }

        [Test]
        public void GroundVehiclesDoNotChaseAircraftButAntiAirDoes()
        {
            var world = Field();
            var car = world.SpawnVehicle("armored_car", 0, new Vector2(0f, 0f), 0f);
            var aa = world.SpawnVehicle("aa_vehicle", 0, new Vector2(-6f, -8f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 30f), 3.14f);
            var carFrom = car.Position;
            var aaFrom = aa.Position;
            Run(world, 12f);
            Assert.Less(Vector2.Distance(car.Position, carFrom), 3f, "the armoured car holds its ground (its machine gun only fires if the helicopter is in reach)");
            Assert.IsTrue(!heli.IsAlive || Vector2.Distance(aa.Position, aaFrom) > 3f, "the anti-air vehicle goes after the helicopter");
        }

        [Test]
        public void BombsLandUnderTheBomber()
        {
            var world = Field();
            var target = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 0f), 0f);
            var bomber = world.SpawnVehicle("heavy_bomber", 0, new Vector2(-45f, 0f), 0f);
            world.Step(TestWorlds.Step);
            world.ClearEvents();
            world.Submit(new Command(CommandType.Attack, 0, new[] { bomber.Id }, target.Position, target.Id));
            // The bomb-run fix (DECISIONS "Ném bom rải thảm", pass 2 follow-up): a stick's bomb i falls on the bomber's track,
            // the lead (its speed over the fall) ahead of where the first bomb was let go, plus i spacings. The FAB-500's
            // escape warning (T4) holds each landing back to its warning time, by when the bomber has flown on, so the bombs
            // are measured against the track at release, not against the bomber at impact.
            var stick = bomber.Arms[0].Stick;
            Assert.IsNotNull(stick, "bomber_payload lays a stick");
            var drops = new List<(double at, Vector2 origin, Vector2 aim, float heading, float speed)>();
            var impacts = new List<Vector2>();
            var start = Vector2.Zero;
            for (var t = 0f; t < 40f && impacts.Count < 3; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                {
                    if (e.DefId != "bomber_payload" || !bomber.IsAlive) continue;
                    if (e.Kind == SimEventKind.ProjectileImpact) impacts.Add(e.Position);
                    if (e.Kind != SimEventKind.WeaponFired) continue;
                    // The stick's line as the game fixed it with its first bomb (the mount's state).
                    if (drops.Count == 0) start = bomber.Weapons[0].StickStart;
                    drops.Add((world.Time, e.Position, e.Target, bomber.StraightHeading, bomber.Speed));
                }
                world.ClearEvents();
            }
            Assert.GreaterOrEqual(drops.Count, 2, "the bomber drops its load");
            var first = drops.TakeWhile((d, i) => i == 0 || d.at - drops[i - 1].at < 1.0).ToList();
            var forward = MachineBrigade.Sim.Core.SimMath.Forward(first[0].heading);
            var side = new Vector2(-forward.Y, forward.X);
            // The stick starts the lead ahead of where the first bomb was let go (the event's origin is the bomber's position
            // plus its radius along the mount, so within a radius of it).
            var lead = first[0].speed * MachineBrigade.Sim.Combat.CombatSystem.BombFall(bomber);
            Assert.AreEqual(lead, Vector2.Dot(start - first[0].origin, forward), bomber.Radius + 0.1f, "the stick starts the lead ahead of the release");
            for (var i = 0; i < first.Count; i++)
            {
                Assert.AreEqual(first[0].heading, first[i].heading, 1e-5f, "bomb " + i + ": the bomber holds its heading through the stick");
                var off = first[i].aim - start;
                Assert.AreEqual(i * stick.Spacing, Vector2.Dot(off, forward), stick.JitterAlong + 0.05f, "bomb " + i + ": on the track at the lead plus i spacings");
                Assert.LessOrEqual(System.MathF.Abs(Vector2.Dot(off, side)), stick.JitterAcross + 0.05f, "bomb " + i + ": not off the track");
                Assert.Greater(Vector2.Dot(first[i].aim - first[i].origin, forward), 0f, "bomb " + i + ": falls ahead of where it was let go");
            }
            foreach (var hit in impacts)
                Assert.Less(drops.Min(d => Vector2.Distance(d.aim, hit)), 0.05f, "a bomb lands where it was dropped towards");
        }
    }
}
