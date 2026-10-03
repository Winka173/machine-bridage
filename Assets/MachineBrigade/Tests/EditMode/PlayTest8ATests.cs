using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Sandbox;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 8 A (DECISIONS 22Q): weapons re-weigh their targets (an anti-air gun on a tank turns on the helicopter
    /// that comes in, without flickering between equals), the SAM launcher's In action range, the siege tank's and the
    /// long-range SAM's blasts, the Sandbox's coastal test range, the armour diagram's outlines, and bombs that fall.
    /// </summary>
    public class PlayTest8ATests
    {
        private static SimWorld Field(float size = 200f, int seed = 3) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", size,
                new[] { new TeamStart(0, new Vector2(-size * 0.4f, -size * 0.4f)), new TeamStart(1, new Vector2(size * 0.4f, size * 0.4f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);

        private static void Run(SimWorld world, float seconds, System.Action<SimEvent> each = null)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                if (each != null)
                    foreach (var e in world.Events)
                        each(e);
                world.ClearEvents();
            }
        }

        private static Vehicle Dummy(SimWorld world, string id, int team, Vector2 at)
        {
            var v = world.SpawnVehicle(id, team, at, System.MathF.PI);
            world.MakeDummy(v);
            return v;
        }

        [Test]
        public void AntiAirOnATankTurnsOnTheAircraftThatComesIn()
        {
            var world = Field();
            var aa = world.SpawnVehicle("aa_vehicle", 0, new Vector2(0f, 0f), 0f);
            var car = Dummy(world, "armored_car", 1, new Vector2(0f, 20f));
            Run(world, 3f);
            Assert.AreEqual(car.Id, aa.Target, "with nothing else about, the flak gun shoots at the armoured car");
            var heli = Dummy(world, "attack_helicopter", 1, new Vector2(6f, 24f));
            Run(world, 1.2f);
            Assert.AreEqual(heli.Id, aa.Target, "within a look or two (every half second) it turns on the helicopter");
        }

        [Test]
        public void ATargetIsHeldBetweenTwoOfTheSameWorth()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            Dummy(world, "light_tank", 1, new Vector2(-8f, 22f));
            Dummy(world, "light_tank", 1, new Vector2(8f, 22f));
            var switches = 0;
            var last = default(Sim.Core.EntityId);
            for (var t = 0f; t < 8f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                if (tank.Target.IsValid && tank.Target != last)
                {
                    if (last.IsValid) switches++;
                    last = tank.Target;
                }
            }
            Assert.LessOrEqual(switches, 2, "the hysteresis keeps the gun on one of two equal targets (a kill may move it on)");
        }

        [Test]
        public void TheSamLauncherFiresInItsInActionRange()
        {
            var catalog = GameContent.LoadCatalog();
            var def = catalog.Vehicle("sam_launcher");
            var distance = FiringRange.TargetDistance(def);
            Assert.Greater(distance, 30f, "the targets stand at the missiles' distance, not the 18 m self-defence gun's");
            var world = new SimWorld(catalog, new MapDefinition("range", 90f,
                new[] { new TeamStart(0, new Vector2(0f, -70f)), new TeamStart(1, new Vector2(0f, 70f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: 11);
            var sam = world.SpawnVehicle("sam_launcher", 0, new Vector2(0f, -distance * 0.5f), 0f);
            var far = new Vector2(0f, distance * 0.5f);
            foreach (var (id, at) in FiringRange.GroundTargets) Dummy(world, id, 1, far + at);
            var heli = Dummy(world, "attack_helicopter", 1, far + new Vector2(10f, -6f));
            world.Submit(new Command(CommandType.Attack, 0, new[] { sam.Id }, default, heli.Id));
            var missiles = 0;
            Run(world, 12f, e =>
            {
                if (e.Kind == SimEventKind.WeaponFired && e.Entity == sam.Id && e.Mount == 0) missiles++;
            });
            Assert.Greater(missiles, 0, "the Buk's missiles fly at the helicopter");
        }

        [Test]
        public void SiegeBlastIsSmallerAndTheLongRangeSamsBigger()
        {
            var catalog = GameContent.LoadCatalog();
            // Play-test 8 A cut it to 7.2 m; prompt 25 A3 (DECISIONS "25A", "A3 Weapon families": one family a real weapon, its
            // members share the blast) gave it back its 2B8 240 mm family's 9 m, and the owner keeps it (play-test 12).
            Assert.AreEqual(9f, catalog.Weapons["siege_mortar_240"].SplashRadius, 1e-3f, "the siege mortar's blast is its 2B8 family's 9 m");
            Assert.AreEqual("siege_mortar_240", catalog.Vehicle("siege_tank").Weapon.Id);
            var s400 = catalog.Weapons["sam_48n6"];
            Assert.AreEqual(7.2f, s400.SplashRadius, 1e-3f, "the 48N6's blast doubled from 3.6 m");
            Assert.AreEqual(2f, s400.ImpactScale, 1e-3f, "and drawn twice as big");
        }

        [Test]
        public void TheCoastalTestRangeTakesShipsAndNavalBosses()
        {
            var catalog = GameContent.LoadCatalog();
            var leviathan = catalog.Vehicle("leviathan");
            var none = new List<SandboxUnit>();
            var heading = 0f;
            Assert.AreEqual(SandboxRefusal.NoSea, SandboxRules.Place(SandboxMaps.Flat(), leviathan, none, new Vector2(120f, 0f), false, out _, ref heading));
            var coast = SandboxMaps.Coast();
            Assert.IsTrue(SandboxMaps.IsFlat(coast.Id), "the coastal range is a test range (grid, towers anywhere)");
            Assert.AreEqual(SandboxRefusal.NotOnSea, SandboxRules.Place(coast, leviathan, none, new Vector2(40f, 0f), false, out _, ref heading));
            Assert.AreEqual(SandboxRefusal.None, SandboxRules.Place(coast, leviathan, none, new Vector2(125f, 10f), false, out var spot, ref heading));
            Assert.IsTrue(coast.Sea.IsSea(spot, 2f), "a ship goes onto a sea lane");
            var world = new SimWorld(catalog, coast, seed: 5);
            var ship = world.SpawnVehicle("leviathan", 1, spot, 0f);
            Run(world, 3f);
            Assert.IsTrue(ship.IsAlive && coast.Sea.IsSea(ship.Position), "the Leviathan sails the coastal range's sea");
        }

        [Test]
        public void TheArmourDiagramDrawsEachUnitsOwnOutline()
        {
            var catalog = GameContent.LoadCatalog();
            ArmourDiagram.Shape Of(string id) => ArmourDiagram.ShapeOf(catalog.Vehicle(id), CombatFacts.Armour(catalog.Vehicle(id)).Kind);
            Assert.AreEqual(ArmourDiagram.Shape.Ship, Of("leviathan"));
            Assert.AreEqual(ArmourDiagram.Shape.Aircraft, Of("heavy_bomber"));
            Assert.AreEqual(ArmourDiagram.Shape.Helicopter, Of("attack_helicopter"));
            Assert.AreEqual(ArmourDiagram.Shape.Tank, Of("main_battle_tank"));
        }

        [Test]
        public void BombsOfAStickFallAlongThePathWhereTheirDropPutsThem()
        {
            var world = Field(300f, seed: 7);
            var bomber = world.SpawnVehicle("heavy_bomber", 0, new Vector2(-36f, -10f), System.MathF.PI * 0.5f);
            // A tank driving off north across the bomber's track: the bombs do not follow it.
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(10f, -10f), 0f);
            world.HoldFire(tank, true);
            Run(world, 0.1f);
            world.Submit(new Command(CommandType.Move, 1, new[] { tank.Id }, new Vector2(10f, 120f)));
            Assert.IsTrue(world.Submit(new Command(CommandType.Attack, 0, new[] { bomber.Id }, default, tank.Id)).Accepted, "the bomber is sent at the tank");
            var aims = new List<(double at, Vector2 aim, Vector2 from)>();
            var impacts = new List<Vector2>();
            Run(world, 40f, e =>
            {
                if (e.DefId != "bomber_payload") return;
                if (e.Kind == SimEventKind.WeaponFired) aims.Add((world.Time, e.Target, e.Position));
                if (e.Kind == SimEventKind.ProjectileImpact) impacts.Add(e.Position);
            });
            Assert.GreaterOrEqual(aims.Count, 3, "the bomber let a stick go");
            // The first stick: its bombs one after another, spaced along the track, each ahead of where it was let go.
            // The bomb-run fix: a stick's bombs go spacing / release speed apart (0.625 s for the FAB-500 stick).
            var stick = aims.TakeWhile((a, i) => i == 0 || a.at - aims[i - 1].at < 1.0).ToList();
            Assert.GreaterOrEqual(stick.Count, 3, "one stick, bomb after bomb");
            // The track: from where the first bomb was let go to where the last one was.
            var track = Vector2.Normalize(stick[stick.Count - 1].from - stick[0].from);
            for (var i = 1; i < stick.Count; i++) Assert.Greater(stick[i].at - stick[i - 1].at, 0.1, "spaced in time");
            // Along the track (each bomb scatters a few metres round its own point, so taken half against half).
            var along = stick.Select(a => Vector2.Dot(a.aim - stick[0].aim, track)).ToList();
            var half = along.Count / 2;
            Assert.Greater(along.Skip(along.Count - half).Average() - along.Take(half).Average(), 6f, "the later bombs land further along the track");
            Assert.Greater(along.Max() - along.Min(), 10f, "the stick is spread along the ground");
            foreach (var (_, aim, from) in stick)
                Assert.Greater(Vector2.Distance(aim, from), 10f, "a bomb carries on ahead of its drop point as it falls");
            // Unguided: every bomb comes down on the point its drop gave it, wherever the tank has driven by then.
            Assert.GreaterOrEqual(impacts.Count, stick.Count);
            foreach (var hit in impacts)
                Assert.Less(aims.Min(a => Vector2.Distance(a.aim, hit)), 0.05f, "a bomb lands where it was dropped towards, not on the moving tank");
        }
    }
}
