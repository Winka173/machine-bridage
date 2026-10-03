using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Movement;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The bomb-run fix, pass 2 (DECISIONS "Ném bom rải thảm"): the spec's nine tests. No battle is simulated: each test
    /// builds an empty field (five enemy tanks in a row along the track, 8 m apart, the middle one the target at (0, 0);
    /// the carrier on heading 0), and calls the game's own drop code directly: CombatSystem.Launch (private, by reflection)
    /// once per bomb, the carrier flown on one SalvoGap between bombs as Operate's salvo timer does, and
    /// MovementSystem.DriveAeroplane for the straight-flight test.
    /// </summary>
    public class BombStickTests
    {
        private const float Dt = 0.05f;
        private const BindingFlags Hidden = BindingFlags.NonPublic | BindingFlags.Instance;

        /// <summary>Each stick weapon on one carrier: a free-falling bomber's, an attack jet's pair, a boss airship's bay.</summary>
        private static readonly (string unit, string weapon)[] StickCarriers =
        {
            ("heavy_bomber", "bomber_payload"), ("attack_jet", "jet_bombs"), ("command_airship", "p26_roc_main_roc_bombs"),
        };

        /// <summary>The guided bombs (POINT) on one carrier each.</summary>
        private static readonly (string unit, string weapon)[] PointCarriers =
        {
            ("stealth_bomber", "stealth_payload"), ("strike_drone", "guided_bomb"), ("glide_bomber", "glide_fab500"),
        };

        private static Catalog _catalog;
        private static Catalog Cat => _catalog ??= GameContent.LoadCatalog();

        /// <summary>One drop: the planned line, and each bomb's index with where it lands (a bomb skipped for safety has none).</summary>
        private sealed class Drop
        {
            public SimWorld World;
            public Vehicle Carrier;
            public int Mount;
            public WeaponDef Round;
            public Vector2 Start, Dir;
            public readonly List<(int index, Vector2 at)> Impacts = new List<(int index, Vector2 at)>();
            public double ReleasedAt;
        }

        private static MapDefinition Field() =>
            new MapDefinition("field", 400f,
                new[] { new TeamStart(0, new Vector2(-160f, -160f)), new TeamStart(1, new Vector2(160f, 160f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());

        private static int MountOf(Vehicle v, string weapon)
        {
            for (var i = 0; i < v.Arms.Length; i++)
                if (v.Arms[i].Id == weapon) return i;
            Assert.Fail(v.Def.Id + " mounts no " + weapon);
            return -1;
        }

        /// <summary>
        /// Lays one stick (every bomb through CombatSystem.Launch). A free-falling carrier starts lead + half the stick short of
        /// the target, so the stick's middle falls on it (anchor CENTER); a boss bay fires from 30 m south of it.
        /// </summary>
        private static Drop Lay(string unit, string weapon, int seed, IList<Vector2> friends = null)
        {
            var world = new SimWorld(Cat, Field(), seed: seed);
            Vehicle target = null;
            foreach (var z in new[] { -16f, -8f, 0f, 8f, 16f })
            {
                var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, z), 0f);
                if (z == 0f) target = tank;
            }
            if (friends != null)
                foreach (var f in friends) world.SpawnVehicle("main_battle_tank", 0, f, 0f);
            var carrier = world.SpawnVehicle(unit, 0, new Vector2(0f, -60f), 0f);
            var mount = MountOf(carrier, weapon);
            var round = CombatSystem.Loaded(carrier, mount);
            Assert.IsNotNull(round.Stick, weapon + " has no stick data");
            carrier.Heading = 0f;
            var freeFall = CombatSystem.FreeFall(carrier, round);
            carrier.Speed = freeFall ? round.Stick.ReleaseSpeed : carrier.Def.Speed;
            carrier.Position = freeFall
                ? new Vector2(0f, -(carrier.Speed * CombatSystem.BombFall(carrier) + round.Stick.Length * 0.5f))
                : new Vector2(0f, -30f);
            var state = carrier.Weapons[mount];
            state.Cooldown = 0f;
            state.StickBombs = round.Stick.Bombs;
            var launch = typeof(CombatSystem).GetMethod("Launch", Hidden);
            Assert.IsNotNull(launch, "CombatSystem.Launch (private) not found");
            var drop = new Drop { World = world, Carrier = carrier, Mount = mount, Round = round, ReleasedAt = world.Time };
            for (var i = 0; i < round.Stick.Bombs; i++)
            {
                world.ClearEvents();
                launch.Invoke(world.Combat, new object[] { carrier, mount, target.Position, target.Id, false, 1f, i == 0, target });
                if (i == 0)
                {
                    drop.Start = state.StickStart;
                    drop.Dir = state.StickDir;
                }
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == carrier.Id) drop.Impacts.Add((i, e.Target));
                if (freeFall) carrier.Position += SimMath.Forward(carrier.Heading) * (carrier.Speed * round.SalvoGap);
            }
            world.ClearEvents();
            return drop;
        }

        private static float Along(Drop d, Vector2 p) => Vector2.Dot(p - d.Start, d.Dir);

        private static float Across(Drop d, Vector2 p)
        {
            var o = p - d.Start;
            return MathF.Abs(o.X * d.Dir.Y - o.Y * d.Dir.X);
        }

        private static IEnumerable<WeaponDef> StickWeapons() => Cat.Weapons.Values.Where(w => w.Stick is { Mode: StickMode.Stick, Bombs: > 1 });

        // 1 ------------------------------------------------------------------------------------------------------------------
        [Test, Category("BombStick")]
        public void AllBombsOfAStickLieOnOneLineAlongItsHeading()
        {
            foreach (var (unit, weapon) in StickCarriers)
            {
                var d = Lay(unit, weapon, 1);
                var s = d.Round.Stick;
                Assert.AreEqual(s.Bombs, d.Impacts.Count, weapon + ": every bomb of the stick dropped");
                Assert.AreEqual(1f, d.Dir.Length(), 1e-3f, weapon + ": the stick's way is a unit vector");
                // The row of tanks runs north, as does the approach: the stick runs north.
                Assert.Greater(Vector2.Dot(d.Dir, new Vector2(0f, 1f)), 0.999f, weapon + ": laid along the row and the approach");
                foreach (var (index, at) in d.Impacts)
                    Assert.LessOrEqual(Across(d, at), s.JitterAcross + 1e-3f, weapon + " bomb " + index + ": off the stick's line");
                var distinct = d.Impacts.Select(x => x.at).Distinct().Count();
                Assert.AreEqual(d.Impacts.Count, distinct, weapon + ": no two bombs share an aim point");
            }
            // The stick's way: a row's main axis within 45 degrees of the approach, else the approach.
            var row = new List<Vector2>();
            for (var k = -2; k <= 2; k++) row.Add(new Vector2(k * 8f * MathF.Sin(0.5f), k * 8f * MathF.Cos(0.5f)));
            var axis = CombatSystem.StickDirection(new Vector2(0f, 1f), row);
            Assert.Greater(Vector2.Dot(axis, new Vector2(MathF.Sin(0.5f), MathF.Cos(0.5f))), 0.999f, "a row 29 degrees off the approach: along the row");
            var across = new List<Vector2>();
            for (var k = -2; k <= 2; k++) across.Add(new Vector2(k * 8f, 0f));
            Assert.Greater(Vector2.Dot(CombatSystem.StickDirection(new Vector2(0f, 1f), across), new Vector2(0f, 1f)), 0.999f,
                "a row square to the approach: along the approach");
            var blob = new List<Vector2> { Vector2.Zero, new Vector2(-4f, -4f), new Vector2(4f, -4f), new Vector2(-4f, 4f), new Vector2(4f, 4f) };
            Assert.Greater(Vector2.Dot(CombatSystem.StickDirection(new Vector2(0f, 1f), blob), new Vector2(0f, 1f)), 0.999f,
                "a square cluster has no axis: along the approach");
            Assert.AreEqual(axis, CombatSystem.StickDirection(new Vector2(0f, 1f), row), "the axis is deterministic");
        }

        // 2 ------------------------------------------------------------------------------------------------------------------
        [Test, Category("BombStick")]
        public void TheStickIsNMinusOneSpacingsLong()
        {
            foreach (var w in StickWeapons())
                Assert.AreEqual((w.Stick.Bombs - 1) * w.Stick.Spacing, w.Stick.Length, 0.05f * w.Stick.Length, w.Id + ": data length");
            foreach (var (unit, weapon) in StickCarriers)
            {
                var d = Lay(unit, weapon, 2);
                var s = d.Round.Stick;
                var planned = Along(d, CombatSystem.StickPoint(d.Start, d.Dir, s.Spacing, s.Bombs - 1)) - Along(d, d.Start);
                Assert.AreEqual(s.Length, planned, 0.05f * s.Length, weapon + ": the laid stick's length");
                foreach (var (index, at) in d.Impacts)
                    Assert.AreEqual(index * s.Spacing, Along(d, at), s.JitterAlong + 1e-3f, weapon + " bomb " + index + ": on its own point along the stick");
                if (s.Bombs >= 5)
                {
                    // The fitted spacing (least squares of the along position on the index) times n - 1.
                    var mi = d.Impacts.Average(x => (double)x.index);
                    var ma = d.Impacts.Average(x => (double)Along(d, x.at));
                    var num = d.Impacts.Sum(x => (x.index - mi) * (Along(d, x.at) - ma));
                    var den = d.Impacts.Sum(x => (x.index - mi) * (x.index - mi));
                    Assert.AreEqual(s.Length, (float)(num / den) * (s.Bombs - 1), 0.05f * s.Length, weapon + ": the fallen stick's length");
                }
            }
        }

        // 3 ------------------------------------------------------------------------------------------------------------------
        [Test, Category("BombStick")]
        public void TheReleaseIntervalMatchesTheSpeed()
        {
            foreach (var w in StickWeapons())
            {
                var s = w.Stick;
                Assert.AreEqual(s.Spacing, s.ReleaseSpeed * s.Interval, 0.05f * s.Spacing, w.Id + ": spacing = release speed x interval");
                Assert.AreEqual(s.Interval, w.SalvoGap, 1e-5f, w.Id + ": the salvo's bombs go one stick interval apart");
            }
            // A free-falling stick's release speed is its carrier's run speed (0.8 throttle through the attack run).
            foreach (var (unit, weapon) in new[] { ("heavy_bomber", "bomber_payload"), ("attack_jet", "jet_bombs") })
            {
                var s = Cat.Weapons[weapon].Stick;
                Assert.AreEqual(Cat.Vehicle(unit).Speed * 0.8f, s.ReleaseSpeed, 0.05f * s.ReleaseSpeed, weapon + ": release speed");
                var d = Lay(unit, weapon, 3);
                // The carrier flew one SalvoGap between bombs: the bombs fall one spacing apart, as it went.
                var first = d.Impacts[0].at;
                var last = d.Impacts[d.Impacts.Count - 1].at;
                var flown = d.Carrier.Speed * d.Round.SalvoGap * (d.Impacts.Count - 1);
                Assert.AreEqual(flown, Along(d, last) - Along(d, first), 0.05f * flown + 2f * s.JitterAlong, weapon + ": the stick keeps pace with the carrier");
            }
        }

        // 4 ------------------------------------------------------------------------------------------------------------------
        [Test, Category("BombStick")]
        public void TheSameSeedDropsTheSameStick()
        {
            foreach (var (unit, weapon) in StickCarriers)
            {
                var a = Lay(unit, weapon, 5);
                var b = Lay(unit, weapon, 5);
                Assert.AreEqual(a.Impacts.Count, b.Impacts.Count, weapon);
                for (var i = 0; i < a.Impacts.Count; i++)
                {
                    Assert.AreEqual(a.Impacts[i].index, b.Impacts[i].index, weapon);
                    Assert.AreEqual(a.Impacts[i].at.X, b.Impacts[i].at.X, 0f, weapon + " bomb " + i + " x");
                    Assert.AreEqual(a.Impacts[i].at.Y, b.Impacts[i].at.Y, 0f, weapon + " bomb " + i + " z");
                }
                var c = Lay(unit, weapon, 6);
                Assert.IsTrue(a.Impacts.Zip(c.Impacts, (x, y) => x.at != y.at).Any(z => z), weapon + ": another seed jitters otherwise");
            }
        }

        // 5 ------------------------------------------------------------------------------------------------------------------
        [Test, Category("BombStick")]
        public void EveryImpactFallsInsideTheWarningRectangle()
        {
            foreach (var (unit, weapon) in StickCarriers)
            {
                var d = Lay(unit, weapon, 4);
                var s = d.Round.Stick;
                // The rectangle round the whole stick: its length and a blast's edge at each end, its width across.
                var edge = d.Round.WarnRadius;
                var inside = 0;
                foreach (var (index, at) in d.Impacts)
                {
                    var along = Along(d, at);
                    var outAlong = MathF.Max(0f, MathF.Max(-edge - along, along - (s.Length + edge)));
                    var outAcross = MathF.Max(0f, Across(d, at) - s.Width * 0.5f);
                    var outside = MathF.Max(outAlong, outAcross);
                    if (outside <= 0f) inside++;
                    Assert.LessOrEqual(outside, 1f, weapon + " bomb " + index + ": more than 1 m outside the warning rectangle");
                }
                Assert.GreaterOrEqual(inside, (int)MathF.Ceiling(0.95f * d.Impacts.Count), weapon + ": 95 % inside the warning rectangle");
            }
            foreach (var w in StickWeapons())
                if (w.WarheadKg >= 400f || w.Stick.Drop == StickDrop.Bay)
                    Assert.AreEqual(StickWarn.StickRect, w.Stick.Warn, w.Id + ": a 400 kg+ or boss stick warns with one rectangle");
        }

        // 6 ------------------------------------------------------------------------------------------------------------------
        [Test, Category("BombStick")]
        public void TheOverlapRatioIsBetween08And12()
        {
            var any = false;
            foreach (var w in StickWeapons())
            {
                any = true;
                var ratio = w.SplashRadius / w.Stick.Spacing;
                Assert.That(ratio, Is.InRange(0.8f, 1.2f), w.Id + ": core / spacing");
                Assert.AreEqual(ratio, w.Stick.Overlap, 0.02f, w.Id + ": the data's overlap");
            }
            Assert.IsTrue(any, "no stick weapon in the data");
        }

        // 7 ------------------------------------------------------------------------------------------------------------------
        [Test, Category("BombStick")]
        public void NoBombFallsInsideTheSafetyDistanceOfFriends()
        {
            foreach (var (unit, weapon) in StickCarriers)
            {
                var clean = Lay(unit, weapon, 7);
                var s = clean.Round.Stick;
                // A friendly tank half the safety distance behind the stick's first bomb and (a stick of 4 or more) beyond its
                // last: those bombs fall by it, the next ones a spacing further on do not (beside a bomb, 3 m off the line, a
                // friend was within the safety distance plus its own radius of the jet's second bomb too, 8.8 m on).
                var back = 0.5f * s.Safety;
                var friends = new List<Vector2> { CombatSystem.StickPoint(clean.Start, clean.Dir, s.Spacing, 0) - clean.Dir * back };
                if (s.Bombs >= 4) friends.Add(CombatSystem.StickPoint(clean.Start, clean.Dir, s.Spacing, s.Bombs - 1) + clean.Dir * back);
                var d = Lay(unit, weapon, 7, friends);
                Assert.Greater(d.Impacts.Count, 0, weapon + ": the safe bombs still drop");
                Assert.Less(d.Impacts.Count, s.Bombs, weapon + ": the bombs by friends are skipped");
                foreach (var (index, at) in d.Impacts)
                {
                    foreach (var f in friends)
                        Assert.GreaterOrEqual(Vector2.Distance(at, f), s.Safety, weapon + " bomb " + index + ": inside the safety distance of a friend");
                    // A skipped bomb does not shift the others: each keeps its own point.
                    Assert.AreEqual(index * s.Spacing, Along(d, at), s.JitterAlong + 1e-3f, weapon + " bomb " + index + ": moved along the stick");
                }
                Assert.AreEqual(clean.Start, d.Start, weapon + ": the same stick start with friends about");
            }
        }

        // 8 ------------------------------------------------------------------------------------------------------------------
        [Test, Category("BombStick")]
        public void GuidedBombsStayPoint()
        {
            var launch = typeof(CombatSystem).GetMethod("Launch", Hidden);
            Assert.IsNotNull(launch, "CombatSystem.Launch (private) not found");
            foreach (var (unit, weapon) in PointCarriers)
            {
                var world = new SimWorld(Cat, Field(), seed: 8);
                var target = world.SpawnVehicle("main_battle_tank", 1, Vector2.Zero, 0f);
                var carrier = world.SpawnVehicle(unit, 0, new Vector2(0f, -20f), 0f);
                var mount = MountOf(carrier, weapon);
                var round = CombatSystem.Loaded(carrier, mount);
                Assert.IsNotNull(round.Stick, weapon + " has no stick data");
                Assert.AreEqual(StickMode.Point, round.Stick.Mode, weapon + ": a guided bomb is POINT");
                Assert.IsFalse(CombatSystem.Sticks(carrier, round), weapon + ": laid as no stick");
                carrier.Speed = carrier.Def.Speed;
                var aims = new List<Vector2>();
                for (var i = 0; i < Math.Max(1, round.Burst); i++)
                {
                    world.ClearEvents();
                    launch.Invoke(world.Combat, new object[] { carrier, mount, target.Position, target.Id, false, 1f, i == 0, target });
                    foreach (var e in world.Events)
                        if (e.Kind == SimEventKind.WeaponFired && e.Entity == carrier.Id) aims.Add(e.Target);
                }
                Assert.AreEqual(Math.Max(1, round.Burst), aims.Count, weapon + ": every bomb dropped");
                foreach (var at in aims)
                    Assert.LessOrEqual(Vector2.Distance(at, target.Position), 3f, weapon + ": a guided bomb aims at its target (a few metres)");
            }
        }

        // 9 ------------------------------------------------------------------------------------------------------------------
        [Test, Category("BombStick")]
        public void TheBomberFliesStraightAndLevelThroughItsStick()
        {
            var drive = typeof(MovementSystem).GetMethod("DriveAeroplane", Hidden);
            var setTime = typeof(SimWorld).GetProperty("Time")?.GetSetMethod(true);
            Assert.IsNotNull(drive, "MovementSystem.DriveAeroplane (private) not found");
            Assert.IsNotNull(setTime, "SimWorld.Time has no setter to step the clock");
            foreach (var (unit, weapon) in new[] { ("heavy_bomber", "bomber_payload"), ("attack_jet", "jet_bombs") })
            {
                var d = Lay(unit, weapon, 9);
                var v = d.Carrier;
                var s = d.Round.Stick;
                Assert.Greater(s.StraightTime, 0f, weapon + ": a straight-flight time");
                Assert.AreEqual(d.ReleasedAt + s.StraightTime, v.StickStraightUntil, 1e-3, weapon + ": held straight for its straight-flight time");
                // The time it needs: the stick, the fall, a second more, and 40 m clear after its last bomb.
                var needed = Math.Max(s.Length / s.ReleaseSpeed + s.FallTime + 1f, s.Length / s.ReleaseSpeed + s.Exit / s.ReleaseSpeed);
                Assert.GreaterOrEqual(s.StraightTime, needed - 0.05f, weapon + ": straight long enough");
                Assert.GreaterOrEqual(s.Exit, 40f, weapon + ": 40 m clear after the last bomb");
                var heading = v.StraightHeading;
                var height = v.Height;
                var speed = v.Speed;
                var steps = (int)Math.Floor((s.StraightTime - 1e-3) / Dt);
                for (var k = 1; k <= steps; k++)
                {
                    setTime.Invoke(d.World, new object[] { d.ReleasedAt + k * Dt });
                    var before = v.Position;
                    drive.Invoke(d.World.Movement, new object[] { v, Dt });
                    Assert.AreEqual(heading, v.Heading, 1e-5f, weapon + ": heading held at step " + k);
                    Assert.AreEqual(height, v.Height, 1e-4f, weapon + ": height held at step " + k);
                    Assert.AreEqual(speed, v.Speed, 1e-4f, weapon + ": speed held at step " + k);
                    var moved = v.Position - before;
                    Assert.AreEqual(speed * Dt, moved.Length(), 1e-3f, weapon + ": flies on at step " + k);
                    Assert.Greater(Vector2.Dot(moved, SimMath.Forward(heading)), speed * Dt * 0.999f, weapon + ": straight ahead at step " + k);
                }
            }
        }

        // Play-test 13 (lane C) ------------------------------------------------------------------------------------------------
        // The anchor of a laid stick is unchanged (the free-falling stick still starts where its first bomb's fall puts it at
        // release; Lay above releases exactly centred, so the nine tests keep their expectations). What changed is WHEN a free
        // bomber lets go and WHERE a bay centres: on the best centre for the target group (CombatSystem.BestStickCentre).

        [Test]
        public void ALoneTargetFallsMidStick()
        {
            var dir = new Vector2(0f, 1f);
            var target = new Vector2(3f, 7f);
            var centre = CombatSystem.BestStickCentre(target, dir, 4, 10f, 6f, 3f, new List<Vector2> { target }, out var hits);
            Assert.AreEqual(1, hits);
            Assert.AreEqual(target.X, centre.X, 1e-4f, "no side offset for a lone target");
            Assert.AreEqual(target.Y, centre.Y, 1e-4f, "the stick's middle on it: bombs 2 and 3 either side, 1 before, 4 past");
        }

        [Test]
        public void ARowAheadIsCoveredFromItsFirstVehicle()
        {
            // The target leads a row running on along the track: the stick moves forward over the row, the target still inside.
            var dir = new Vector2(0f, 1f);
            var row = new List<Vector2> { new Vector2(0f, 0f), new Vector2(0f, 8f), new Vector2(0f, 16f), new Vector2(0f, 24f), new Vector2(0f, 32f) };
            var onTarget = 0;
            foreach (var p in row)
                for (var k = 0; k < 4; k++)
                    if (Vector2.Distance(p, new Vector2(0f, (k - 1.5f) * 11f)) <= 6f) { onTarget++; break; }
            var centre = CombatSystem.BestStickCentre(row[0], dir, 4, 11f, 6f, 0f, row, out var hits);
            Assert.Greater(hits, onTarget, "more of the row under the stick than with its middle on the target");
            Assert.Greater(centre.Y, 0f, "moved forward along the row");
            Assert.LessOrEqual(centre.Y, 1.5f * 11f + 1e-3f, "the target stays inside the stick");
            var again = CombatSystem.BestStickCentre(row[0], dir, 4, 11f, 6f, 0f, row, out var hitsAgain);
            Assert.AreEqual(centre, again, "deterministic");
            Assert.AreEqual(hits, hitsAgain);
        }

        [Test]
        public void TheBomberLetsGoWhenTheStickMiddleComesOverTheTarget()
        {
            // A lone tank: the bomber holds its stick until the middle of the stick it would drop is over the tank (not later).
            var world = new SimWorld(Cat, Field(), seed: 3);
            var target = world.SpawnVehicle("main_battle_tank", 1, Vector2.Zero, 0f);
            var carrier = world.SpawnVehicle("heavy_bomber", 0, new Vector2(0f, -80f), 0f);
            var mount = MountOf(carrier, "bomber_payload");
            var round = CombatSystem.Loaded(carrier, mount);
            carrier.Heading = 0f;
            carrier.Speed = round.Stick.ReleaseSpeed;
            var straddles = typeof(CombatSystem).GetMethod("StickStraddles", Hidden);
            Assert.IsNotNull(straddles, "CombatSystem.StickStraddles (private) not found");
            var bombs = (int)typeof(CombatSystem).GetMethod("StickBombs", Hidden, null, new[] { typeof(Vehicle), typeof(int), typeof(IDamageable) }, null)
                .Invoke(world.Combat, new object[] { carrier, mount, target });
            var middle = carrier.Speed * CombatSystem.BombFall(carrier) + CombatSystem.StickLength(carrier, round, bombs) * 0.5f;
            bool Lets(float along)
            {
                carrier.Position = new Vector2(0f, -along);
                return (bool)straddles.Invoke(world.Combat, new object[] { carrier, mount, target });
            }
            Assert.IsFalse(Lets(middle + 1f), "too early: the stick's middle would fall short of the tank");
            Assert.IsTrue(Lets(middle - 0.5f), "the stick's middle over the tank: let go");
        }
    }
}
