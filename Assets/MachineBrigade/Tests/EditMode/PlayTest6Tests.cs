using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 6 (DECISIONS 21F): jets that get behind an enemy jet and stay there, autocannon aircraft that keep
    /// firing, the C-RAM's gun only at incoming rounds, and the new rhythms, blasts and weapons.
    /// </summary>
    public class PlayTest6Tests
    {
        private static SimWorld Field(int seed = 3) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 260f,
                new[] { new TeamStart(0, new Vector2(-110f, -110f)), new TeamStart(1, new Vector2(110f, 110f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);

        private static void Tough(Vehicle v)
        {
            v.HpScale = 50f;
            v.Hp = v.MaxHp;
        }

        private static Dictionary<string, int> Rounds(SimWorld world, Vehicle shooter, float seconds, System.Action each = null)
        {
            var rounds = new Dictionary<string, int>();
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == shooter.Id)
                        rounds[e.DefId] = (rounds.TryGetValue(e.DefId, out var n) ? n : 0) + 1;
                world.ClearEvents();
                each?.Invoke();
            }
            return rounds;
        }

        private static int Of(Dictionary<string, int> rounds, string id) => rounds.TryGetValue(id, out var n) ? n : 0;

        [Test]
        public void TwoFightersHuntingEachOtherEndWithOneOnTheOthersTail()
        {
            var world = Field();
            world.RevealAll = true;
            var x = world.SpawnVehicle("fighter_jet", 0, new Vector2(-30f, -60f), 0f);
            var y = world.SpawnVehicle("fighter_jet", 1, new Vector2(30f, 60f), 3.14f);
            Tough(x);
            Tough(y);
            world.Step(TestWorlds.Step);
            world.Submit(new Command(CommandType.Attack, 0, new[] { x.Id }, y.Position, y.Id));
            world.Submit(new Command(CommandType.Attack, 1, new[] { y.Id }, x.Position, x.Id));
            float tail = 0f, longest = 0f, run = 0f;
            var cannon = 0;
            for (var t = 0f; t < 60f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.DefId == "fighter_cannon") cannon++;
                world.ClearEvents();
                x.Hp = x.MaxHp;
                y.Hp = y.MaxHp;
                var on = x.OnTail || y.OnTail;
                if (on) tail += TestWorlds.Step;
                run = on ? run + TestWorlds.Step : 0f;
                longest = System.Math.Max(longest, run);
            }
            // Before: they turned round one circle for the whole minute, neither ever on the other's tail (38 rounds each).
            Assert.Greater(tail, 30f, "one of them sits on the other's tail for most of the minute");
            Assert.Greater(longest, 10f, "and stays there, not a moment at a time");
            Assert.Greater(cannon, 200, "streaming its cannon");
        }

        [Test]
        public void AJetLowOnHealthKeepsFighting()
        {
            var world = Field();
            world.RevealAll = true;
            var x = world.SpawnVehicle("fighter_jet", 0, new Vector2(0f, -20f), 0f);
            var y = world.SpawnVehicle("fighter_jet", 1, new Vector2(0f, 20f), 0f);
            world.MakeSparring(y);
            y.HoldFire = true;
            world.Submit(new Command(CommandType.Move, 1, new[] { y.Id }, new Vector2(0f, 120f)));
            world.Submit(new Command(CommandType.Attack, 0, new[] { x.Id }, y.Position, y.Id));
            Rounds(world, x, 3f, () => y.Hp = y.MaxHp);
            x.Hp = x.MaxHp * 0.2f;
            var tail = 0f;
            Rounds(world, x, 6f, () =>
            {
                y.Hp = y.MaxHp;
                x.Hp = x.MaxHp * 0.2f;
                if (x.OnTail) tail += TestWorlds.Step;
            });
            // Balance pack (lane B, rule D): the locked "no retreat on health, aircraft too": no break-off.
            Assert.IsFalse(x.BreakingOff, "under 30 % of its health it does not break off");
            Assert.Greater(tail, 0f, "it keeps after the jet");
        }

        [Test]
        public void AFighterHangsOnAHelicopterUntilItDies()
        {
            var world = Field();
            world.RevealAll = true;
            var fighter = world.SpawnVehicle("fighter_jet", 0, new Vector2(0f, -60f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 30f), 3.14f);
            world.MakeDummy(heli);
            heli.HoldFire = true;
            world.Submit(new Command(CommandType.Attack, 0, new[] { fighter.Id }, heli.Position, heli.Id));
            var rounds = Rounds(world, fighter, 40f, () => heli.Hp = heli.MaxHp);
            // Before: a 4 s hold, a break-away and a loop, 124 rounds in 40 s.
            Assert.Greater(Of(rounds, "fighter_cannon"), 220, "it holds on it, streaming, instead of breaking away every 4 s");
        }

        [Test]
        public void AutocannonAircraftKeepFiringOnWhatTheyAttack()
        {
            foreach (var (id, gun, least) in new[] { ("attack_jet", "jet_cannon", 240) })
            {
                var world = Field();
                world.RevealAll = true;
                var s = world.SpawnVehicle(id, 0, new Vector2(0f, -40f), 0f);
                var target = world.SpawnVehicle("armored_car", 1, new Vector2(0f, 30f), 3.14f);
                world.MakeDummy(target);
                target.HoldFire = true;
                world.Submit(new Command(CommandType.AttackMove, 0, new[] { s.Id }, target.Position));
                var rounds = Rounds(world, s, 40f, () => target.Hp = target.MaxHp);
                // Before: the attack jet 210 rounds in 40 s.
                Assert.Greater(Of(rounds, gun), least, $"{id}: its cannon keeps firing ({string.Join(" ", rounds.Select(r => r.Key + "=" + r.Value))})");
            }
        }

        [Test]
        public void AStandoffHelicopterStillKeepsOutOfTheAntiAirsReach()
        {
            var world = Field();
            world.RevealAll = true;
            var heli = world.SpawnVehicle("attack_helicopter", 0, new Vector2(0f, -40f), 0f);
            var target = world.SpawnVehicle("armored_car", 1, new Vector2(0f, 30f), 3.14f);
            var aa = world.SpawnVehicle("aa_vehicle", 1, new Vector2(0f, 38f), 3.14f);
            foreach (var t in new[] { target, aa })
            {
                world.MakeDummy(t);
                t.HoldFire = true;
            }
            world.Submit(new Command(CommandType.Attack, 0, new[] { heli.Id }, target.Position, target.Id));
            var closest = float.MaxValue;
            Rounds(world, heli, 25f, () =>
            {
                target.Hp = target.MaxHp;
                aa.Hp = aa.MaxHp;
                closest = System.Math.Min(closest, Vector2.Distance(heli.Position, aa.Position));
            });
            Assert.Greater(closest, aa.Def.Weapon.Range, "with a flak gun covering its target it stays at its missiles' reach");
        }

        [Test]
        public void TheCRamNeverTakesAnAircraftButStillStopsRockets()
        {
            var world = Field();
            world.RevealAll = true;
            var cram = world.SpawnVehicle("c_ram", 0, Vector2.Zero, 0f);
            world.AnchorDefence(cram);
            world.MakeSparring(cram);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 14f), 3.14f);
            var jet = world.SpawnVehicle("attack_jet", 1, new Vector2(10f, 20f), 3.14f);
            foreach (var a in new[] { heli, jet })
            {
                world.MakeDummy(a);
                a.HoldFire = true;
            }
            var mlrs = world.SpawnVehicle("mlrs", 1, new Vector2(0f, 70f), 3.14f);
            world.MakeSparring(mlrs);
            var guarded = world.SpawnVehicle("gun_turret", 0, new Vector2(4f, -4f), 0f);
            world.AnchorDefence(guarded);
            world.MakeSparring(guarded);
            guarded.HoldFire = true;
            world.Step(TestWorlds.Step);
            world.Submit(new Command(CommandType.Attack, 1, new[] { mlrs.Id }, guarded.Position, guarded.Id));
            var fired = 0;
            var intercepted = 0;
            var targeted = 0;
            for (var t = 0f; t < 30f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                {
                    if (e.Entity != cram.Id) continue;
                    if (e.Kind == SimEventKind.WeaponFired) fired++;
                    if (e.Kind == SimEventKind.Intercepted) intercepted++;
                }
                world.ClearEvents();
                if (cram.Target.IsValid) targeted++;
                heli.Hp = heli.MaxHp;
                jet.Hp = jet.MaxHp;
            }
            Assert.IsFalse(GameContent.LoadCatalog().Weapons["c_ram_gatling"].CanTarget(true), "its gun takes no aircraft");
            Assert.AreEqual(0, fired, "it never fires at the helicopter or the jet over it");
            Assert.AreEqual(0, targeted, "nor lays on them");
            Assert.Greater(intercepted, 0, "but it still takes rockets down");
        }

        /// <summary>How far <paramref name="at"/> is from the edge of <paramref name="v"/>'s hull, or of the nearest part's hitbox.</summary>
        private static float OffTheHull(Vehicle v, Vector2 at)
        {
            var axis = new Vector2(System.MathF.Sin(v.Heading), System.MathF.Cos(v.Heading));
            var along = System.Math.Clamp(Vector2.Dot(at - v.Position, axis), -v.Def.HullHalf, v.Def.HullHalf);
            var off = System.Math.Abs(Vector2.Distance(at, v.Position + axis * along) - Sim.Combat.HullContact.Edge(v.Def));
            for (var i = 0; i < v.Def.Parts.Count; i++)
                off = System.Math.Min(off, System.Math.Abs(Vector2.Distance(at, v.PartPosition(i)) - v.Def.Parts[i].Radius));
            return off;
        }

        [TestCase("drone_mothership", "sam_launcher", 30f)]
        [TestCase("leviathan", "ifv", 22f)]
        public void AMissileAtABigHullBurstsOnItsEdge(string bossId, string shooterId, float standOff)
        {
            var world = Field();
            world.RevealAll = true;
            var boss = world.SpawnVehicle(bossId, 1, new Vector2(0f, 40f), 0f);
            world.MakeDummy(boss);
            boss.HoldFire = true;
            var edge = Sim.Combat.HullContact.Edge(boss.Def);
            var shooter = world.SpawnVehicle(shooterId, 0, new Vector2(-(edge + standOff), 40f), 1.57f);
            world.MakeSparring(shooter);
            world.Submit(new Command(CommandType.Attack, 0, new[] { shooter.Id }, boss.Position, boss.Id));
            var off = new List<float>();
            for (var t = 0f; t < 30f && off.Count < 6; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.ProjectileImpact && e.Entity == boss.Id && world.Catalog.Weapons.TryGetValue(e.DefId ?? "", out var w) &&
                        w.Projectile == ProjectileKind.Missile)
                        off.Add(OffTheHull(boss, e.Position));
                world.ClearEvents();
                boss.Hp = boss.MaxHp;
            }
            Assert.IsNotEmpty(off, $"{shooterId} hit {bossId} with a missile");
            Assert.IsTrue(Sim.Combat.HullContact.Big(boss.Def));
            Assert.That(off.Max(), Is.LessThan(1f),
                $"{bossId}: every missile bursts on the hull's (or the struck part's) edge, not in its middle ({edge:0.0} m in): " + string.Join(", ", off.Select(o => o.ToString("0.00"))));
        }

        [Test]
        public void TheRhythmsBlastsAndWeaponsOfPlayTestSix()
        {
            var catalog = GameContent.LoadCatalog();
            var w = catalog.Weapons;
            var v = catalog.Vehicles;
            Assert.AreEqual(1, w["gun_57mm"].Burst, "the light tank fires one round at a time");
            foreach (var id in new[] { "fpv_swarm", "shahed", "swarm_drones" })
                Assert.AreEqual(1, w[id].Burst, id + ": one drone at a time, steadily");
            Assert.Less(w["fpv_swarm"].Cooldown, 3f);
            // Machine guns: longer streams, quicker changes (hmg_roof: 25 rounds, 2.32 s before).
            Assert.Greater(w["hmg_roof"].Clip, 25);
            Assert.Less(w["hmg_roof"].ClipReload, 2.32f);
            Assert.Greater(w["mg_coax"].Clip, 36);
            Assert.Less(w["mg_coax"].ClipReload, 1.87f);
            // Slower rockets and missiles for the attack jet, the rocket technical, the scout and the heavy gunship.
            Assert.AreEqual(38.4f, w["technical_rockets"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(38.4f, w["scout_rockets"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(26.9f, w["gunship_rockets"].ProjectileSpeed, 1e-3f, "play-test 7: 30 % slower again");
            // Blasts.
            Assert.AreEqual(1.2f, w["lancet"].ImpactScale, 1e-4f, "the Lancet's blast a fifth bigger");
            Assert.GreaterOrEqual(w["sam_48n6"].SplashRadius, w["sam_long"].SplashRadius, "the long-range SAM's blast at least the SAM launcher's");
            // MB_FINAL blast sizes (owner 04/10: sizes follow the sheet): the 48N6 is T2 (sam_s_400_48n6), a Large burst, still
            // a band over the SAM launcher's Medium.
            Assert.AreEqual(ExplosionTier.Large, w["sam_48n6"].ImpactTier);
            Assert.Greater((int)w["sam_48n6"].ImpactTier, (int)w["sam_long"].ImpactTier, "the long-range SAM's burst bigger than the SAM launcher's");
            // The drone mothership drops bombs too.
            Assert.IsTrue(v["swarm_carrier"].Mounts.Any(m => m.Weapon.Projectile == ProjectileKind.Bomb), "the mothership has bombs");
            // Towers keep a machine gun only where the real one has it.
            foreach (var id in new[] { "rocket_turret", "missile_battery", "aa_turret.sam", "heavy_turret", "heavy_turret.coastal" })
                Assert.IsFalse(v[id].Mounts.Skip(1).Any(m => m.Weapon.Family == "mg"), id + " has no machine gun");
            // Play-test 7 (DECISIONS 22P): only the steel fortress keeps a second weapon (its two machine-gun turrets).
            foreach (var id in new[] { "mg_bunker", "guard_tower", "gun_turret" })
                Assert.AreEqual(1, v[id].Mounts.Count, id + " has its own gun only");
            Assert.AreEqual(3, v["heavy_turret.bastion"].Mounts.Count, "the steel fortress: its guns and two machine-gun turrets");
        }
    }
}

namespace MachineBrigade.Tests
{
    using MachineBrigade.Game.Effects;
    using MachineBrigade.Game.Rendering;
    using UnityEngine;

    /// <summary>Play-test 6 (DECISIONS 21F): a guided missile flies a smooth line onto a moving target, and a busy sky never makes one jump.</summary>
    public class PlayTest6FlightTests
    {
        [Test]
        public void AGuidedMissileFliesStraightOntoItsTarget()
        {
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var holder = new GameObject("flight").transform;
            try
            {
                var emitters = new Emitters(materials, holder);
                var chunk = models.Merged("hellfire");
                var report = new List<string>();
                foreach (var fps in new[] { 30f, 60f, 144f })
                {
                    var sky = new GameObject("sky " + fps).transform;
                    sky.SetParent(holder, false);
                    var pool = new ProjectilePool(sky, 4);
                    var now = 0f;
                    Vector3 Target() => new Vector3(-10f + 8f * now, 1f, 45f);
                    var from = new Vector3(0f, 15f, 0f);
                    var to = Target();
                    const float duration = 2f;
                    pool.Launch(chunk, from, to, duration, 45f * 0.06f, 0.7f, now, () => Target(), boost: 0.55f,
                        control: WeaponEffects.Leave(from, to, (to - from).normalized, 45f * 0.06f));
                    var shot = sky.GetComponentsInChildren<MeshFilter>(true).First(f => f.sharedMesh == chunk.Mesh).transform;
                    var random = new System.Random(5);
                    Vector3? last = null;
                    float lastTurn = 0f, worst = 0f;
                    var wags = 0;
                    pool.Tick(now, emitters);
                    while (now < duration * 0.97f)
                    {
                        now += 1f / fps * (1f + 0.2f * (float)(random.NextDouble() * 2.0 - 1.0));
                        pool.Tick(now, emitters);
                        var forward = shot.forward;
                        if (last.HasValue)
                        {
                            var turn = Vector3.SignedAngle(last.Value, forward, Vector3.up);
                            worst = Mathf.Max(worst, Vector3.Angle(last.Value, forward));
                            if (Mathf.Abs(turn) > 0.3f && Mathf.Abs(lastTurn) > 0.3f && Mathf.Sign(turn) != Mathf.Sign(lastTurn)) wags++;
                            if (Mathf.Abs(turn) > 0.3f) lastTurn = turn;
                        }
                        last = forward;
                    }
                    report.Add($"{fps} fps: worst {worst:0.00} deg a frame, {wags} wags");
                    Assert.AreEqual(0, wags, $"{fps} fps: its nose never wags");
                    Assert.Less(worst, 45f / fps, $"{fps} fps: no jerk ({worst:0.00} deg in a frame)");
                }
                Debug.Log("MISSILE LINE " + string.Join("; ", report));
            }
            finally
            {
                Object.DestroyImmediate(holder.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }

        [Test]
        public void AFullPoolGrowsInsteadOfTakingAMissileOutOfTheAir()
        {
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var holder = new GameObject("busy sky").transform;
            try
            {
                var emitters = new Emitters(materials, holder);
                var chunk = models.Merged("hellfire");
                var pool = new ProjectilePool(holder, 4);
                pool.Launch(chunk, new Vector3(0f, 10f, 0f), new Vector3(0f, 1f, 60f), 3f, 2f, 0.7f, 0f, boost: 0.55f);
                pool.Tick(1f, emitters);
                var first = holder.GetComponentsInChildren<MeshFilter>(true).First(f => f.sharedMesh == chunk.Mesh && f.gameObject.activeSelf).transform;
                var at = first.position;
                // Twelve more launches, far away, than the pool first had room for.
                for (var i = 0; i < 12; i++) pool.Launch(chunk, new Vector3(200f, 10f, i), new Vector3(200f, 1f, 60f + i), 3f, 2f, 0.7f, 1f, boost: 0.55f);
                pool.Tick(1.02f, emitters);
                Assert.GreaterOrEqual(pool.Capacity, 13, "the pool made room");
                Assert.Less(Vector3.Distance(first.position, at), 1.5f, "the first missile flew on along its own line (it used to jump to a launcher)");
            }
            finally
            {
                Object.DestroyImmediate(holder.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }
    }
}
