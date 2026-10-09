using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 8's new content: the armoured bulldozer, the SP howitzer's shoot-and-scoot and marked-target
    /// accuracy, and the five bosses (the rail supergun, the Earth Worm, the command airship with the
    /// general part mechanism, the landing hovercraft, the Supreme Commander) and Boss Rush.
    /// </summary>
    public class Prompt8ContentTests
    {
        private const float Step = 0.05f;

        private static List<SimEvent> Run(SimWorld world, float seconds, Action each = null)
        {
            var events = new List<SimEvent>();
            for (var t = 0f; t < seconds; t += Step)
            {
                each?.Invoke();
                world.Step(Step);
                events.AddRange(world.Events);
                world.ClearEvents();
            }
            return events;
        }

        private static SimWorld Field(int seed = 4) => Lab.Field(seed);

        // ------------------------------------------------------------------ the armoured bulldozer (A.1)

        [Test]
        public void TheBulldozerIsWhatTheBriefAsks()
        {
            var catalog = GameContent.LoadCatalog();
            var d = catalog.Vehicle("armored_bulldozer");
            Assert.AreEqual(7, d.CpCost);
            // The brief asked for 3,500; 3,250 (the turtle tank's) keeps the turtle the better sponge (see DECISIONS).
            // DECISIONS 20X: toughness 2.2 (was 2.5), so 1,300 in the data is 2,860 in game.
            Assert.AreEqual(2860f, d.MaxHp, 1f, "2,860 health in game");
            Assert.AreEqual(ArmorClass.Heavy, d.Armor);
            Assert.AreEqual(4f, d.Speed, 1e-3f, "prompt 25's balance sheet: 4 m/s (a D9R does about 15 km/h)");
            Assert.AreEqual(UnitClass.Heavy, d.Class);
            Assert.IsTrue(d.Breacher && d.Weapon.Melee, "the blade is a blow, not a gun");
            Assert.AreEqual(4.5f, d.Weapon.Range, 0.6f, "4 m reach");
            Assert.AreEqual(ProjectileKind.Bullet, d.Mounts[1].Weapon.Projectile, "a machine gun besides the blade");
            Assert.AreEqual(2, d.Mounts.Count);
            Assert.AreEqual(0.5f, d.MineArmor, 1e-3f);
            Assert.IsFalse(d.MineProof, "it does not clear mines: that is the engineer's job");
            CollectionAssert.Contains(MatchSettings.AllVehicles, "armored_bulldozer");
            Assert.IsNotNull(Progression.UnlockMission("armored_bulldozer"), "won in the campaign");
        }

        [Test]
        public void TheBladeTearsDownATowerFasterThanATanksGunAndNotATank()
        {
            float Seconds(string attacker, string target)
            {
                var world = Field();
                world.SetBoosts(1, _ => Lab.Harmless);
                var v = world.SpawnVehicle(attacker, 0, new Vector2(0f, -6f), 0f);
                var t = world.SpawnVehicle(target, 1, new Vector2(0f, 12f), (float)Math.PI);
                world.Submit(new Command(CommandType.Attack, 0, new[] { v.Id }, t.Position, t.Id));
                var s = 0f;
                for (; s < 240f && t.IsAlive; s += Step)
                {
                    world.Step(Step);
                    world.ClearEvents();
                }
                return s;
            }
            var dozer = Seconds("armored_bulldozer", "gun_turret");
            var gunned = Seconds("main_battle_tank", "gun_turret");
            UnityEngine.Debug.Log($"BULLDOZER gun tower down in {dozer:0.0} s (battle tank {gunned:0.0} s)");
            Assert.Less(dozer * 2f, gunned, "at least twice as fast as a battle tank's gun (play-test 14 deleted the turtle tank)");
            var tank = Seconds("armored_bulldozer", "main_battle_tank");
            Assert.Greater(tank, dozer, "a tank takes it longer than a tower: it is no tank killer");
        }

        [Test]
        public void TheBulldozerTakesHalfAMinesBlast()
        {
            float Taken(string id)
            {
                var world = Field();
                var v = world.SpawnVehicle(id, 0, Vector2.Zero, 0f);
                var before = v.Hp;
                world.Damage.Splash(v.Position, 5f, 1000f, DamageType.ShapedCharge, 1, default, default, false,
                    new HitInfo(null, 1, null, v.Position, HitKind.Mine, false));
                return before - v.Hp;
            }
            Assert.AreEqual(0.5f, Taken("armored_bulldozer") / Taken("heavy_tank"), 0.01f);
        }

        [Test]
        public void TheCommanderSendsTheBulldozerAheadIntoTheDefences()
        {
            var world = Field();
            world.SetBoosts(1, _ => Lab.Harmless);
            var line = new List<Vehicle>();
            for (var i = 0; i < 4; i++) line.Add(world.SpawnVehicle("main_battle_tank", 0, new Vector2(-12f + i * 8f, -40f), 0f));
            var dozer = world.SpawnVehicle("armored_bulldozer", 0, new Vector2(0f, -48f), 0f);
            var tower = world.SpawnVehicle("heavy_turret", 1, new Vector2(0f, 20f), (float)Math.PI);
            var ai = new TacticalAi(0, 1) { Objective = _ => new Vector2(0f, 30f) };
            Run(world, 20f, () => ai.Tick(world, Step));
            Assert.AreEqual(OrderKind.Attack, dozer.Order.Kind, "sent at the bunker");
            Assert.AreEqual(tower.Id, dozer.Order.Target);
        }

        // ------------------------------------------------------------------ the SP howitzer (A.2)

        [Test]
        public void TheSpGunMovesAfterThreeRoundsAndKeepsItsTargetInReach()
        {
            var world = Field();
            world.SetBoosts(1, _ => Lab.Harmless);
            var gun = world.SpawnVehicle("artillery", 0, new Vector2(0f, -30f), 0f);
            var target = world.SpawnVehicle("gun_turret", 1, new Vector2(0f, 30f), (float)Math.PI);
            world.Submit(new Command(CommandType.Attack, 0, new[] { gun.Id }, target.Position, target.Id));
            // Each relocation: from where it stood when it set off to where it stopped.
            var hops = new List<float>();
            var from = gun.Position;
            var relocating = false;
            var events = Run(world, 45f, () =>
            {
                target.Hp = target.MaxHp;
                if (gun.Relocating && !relocating) from = gun.Position;
                if (!gun.Relocating && relocating) hops.Add(Vector2.Distance(from, gun.Position));
                relocating = gun.Relocating;
            });
            var fired = events.Count(e => e.Kind == SimEventKind.WeaponFired && e.Entity == gun.Id && e.Mount == 0);
            Assert.GreaterOrEqual(fired, 4, "it fires on after moving");
            Assert.GreaterOrEqual(hops.Count, 1, "it moved after its rounds");
            foreach (var hop in hops) Assert.That(hop, Is.InRange(12f, 23f), "15 to 20 m each time");
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.TraitProc && e.DefId == "scoot"));
            Assert.LessOrEqual(Vector2.Distance(gun.Position, target.Position), gun.Weapon.Range, "still in reach");
        }

        [Test]
        public void AMarkedTargetIsHitAlmostDeadOn()
        {
            float MeanMiss(bool mark)
            {
                var world = Field(9);
                world.SetBoosts(1, _ => Lab.Harmless);
                var gun = world.SpawnVehicle("artillery", 0, new Vector2(0f, -35f), 0f);
                var target = world.SpawnVehicle("gun_turret", 1, new Vector2(0f, 40f), 0f);
                world.Submit(new Command(CommandType.Attack, 0, new[] { gun.Id }, target.Position, target.Id));
                var misses = new List<float>();
                var events = Run(world, 60f, () =>
                {
                    target.Hp = target.MaxHp;
                    if (mark) world.Status.Mark(target, 0.1f, 5f, 0, 0f);
                });
                foreach (var e in events)
                    if (e.Kind == SimEventKind.ProjectileImpact && e.DefId == gun.Weapon.Id) misses.Add(Vector2.Distance(e.Position, target.Position));
                Assert.Greater(misses.Count, 3);
                return misses.Average();
            }
            var plain = MeanMiss(false);
            var marked = MeanMiss(true);
            UnityEngine.Debug.Log($"SPGUN mean miss {plain:0.00} m, marked {marked:0.00} m");
            Assert.Less(marked, plain * 0.4f, "a marked target barely scatters");
        }

        // ------------------------------------------------------------------ the command airship: parts and the lock

        [Test]
        public void TheAirshipsHullIsShutUntilTwoEnginesAreDown()
        {
            var world = Field();
            var ship = world.SpawnVehicle("command_airship", 1, Vector2.Zero, 0f);
            Assert.AreEqual(10, ship.PartCount, "four engines, two bays and a radar, the bomb bay (prompt 18) and two gun pods (prompt 20 F.3)");
            Assert.IsTrue(ship.BodyLocked);
            var hp = ship.Hp;
            world.Damage.Apply(ship, 5000f, DamageType.Fragmentation, new HitInfo(null, 0, null, ship.Position, HitKind.Direct, false));
            Assert.AreEqual(hp, ship.Hp, 1e-3f, "the hull shrugs it off");
            world.Bosses.Break(ship, 0);
            Assert.IsTrue(ship.BodyLocked, "one engine is not enough");
            world.Bosses.Break(ship, 1);
            Assert.IsFalse(ship.BodyLocked, "two engines down: the hull is open");
            world.Damage.Apply(ship, 1000f, DamageType.Fragmentation, new HitInfo(null, 0, null, ship.Position, HitKind.Direct, false));
            Assert.Less(ship.Hp, hp);
            Assert.Less(ship.PartSpeed, 0.75f, "each engine lost slows it");
        }

        [Test]
        public void OnlyADirectHitHurtsAPartAndABlastLandsOnTheBody()
        {
            var world = Field();
            var ship = world.SpawnVehicle("command_airship", 1, Vector2.Zero, 0f);
            world.Bosses.Break(ship, 0);
            world.Bosses.Break(ship, 1);
            var aa = world.SpawnVehicle("aa_vehicle", 0, new Vector2(0f, -30f), 0f);
            var radar = ship.Def.PartIndex("pod_105_l");
            var partBefore = ship.PartHealth(radar);
            var bodyBefore = ship.Hp;
            var p = new Projectile(aa.Id, 0, aa.Weapon, ship.PartPosition(radar), ship.Id, 0f, true) { Origin = aa.Position, Shooter = aa, Main = true, Part = radar };
            world.Damage.ResolveImpact(p);
            Assert.Less(ship.PartHealth(radar), partBefore, "the direct hit struck the gun pod");
            Assert.AreEqual(bodyBefore, ship.Hp, 1e-2f, "its blast does not also hurt the part");
            var splashBefore = ship.PartHealth(radar);
            world.Damage.Splash(ship.PartPosition(radar), 6f, 500f, DamageType.Fragmentation, 0, default, aa.Id, true, new HitInfo(aa, 0, aa.Weapon, aa.Position, HitKind.Splash, false));
            Assert.AreEqual(splashBefore, ship.PartHealth(radar), 1e-3f, "a blast never hurts a part");
            Assert.Less(ship.Hp, bodyBefore, "it lands on the body");
        }

        [Test]
        public void BrokenBaysStopTheirDrones()
        {
            var world = Field();
            var ship = world.SpawnVehicle("command_airship", 1, Vector2.Zero, 0f);
            var left = ship.Def.PartIndex("hangar_l");
            var right = ship.Def.PartIndex("hangar_r");
            world.Bosses.Break(ship, left);
            world.Bosses.Break(ship, right);
            foreach (var m in ship.Def.Parts[left].Mounts.Concat(ship.Def.Parts[right].Mounts)) Assert.IsFalse(ship.MountWorks(m));
            Assert.IsTrue(ship.SkillOff.All(x => x), "both bays' launches stop");
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -30f), 0f);
            var events = Run(world, 20f);
            var bays = ship.Def.Parts[left].Mounts.Concat(ship.Def.Parts[right].Mounts).ToHashSet();
            Assert.IsFalse(events.Any(e => e.Kind == SimEventKind.WeaponFired && e.Entity == ship.Id && bays.Contains(e.Mount)), "no drones from broken bays");
            Assert.IsFalse(world.Vehicles.Any(v => v.Def.Id == "strike_drone"), "and no strike drones launched");
            Assert.AreEqual(-1, ship.Def.PartIndex("radar"), "no destructible radar part (boss design 09/10)");
        }

        [Test]
        public void ShooterAimAtTheEnginesWhileTheHullIsShut()
        {
            var world = Field();
            var ship = world.SpawnVehicle("command_airship", 1, Vector2.Zero, 0f);
            var aa = world.SpawnVehicle("heavy_aa", 0, new Vector2(0f, -30f), 0f);
            for (var i = 0; i < 20; i++)
            {
                var part = world.Bosses.ChoosePart(aa, ship, aa.Weapon);
                Assert.GreaterOrEqual(part, 0);
                Assert.AreEqual("engine", ship.Def.Parts[part].Kind);
            }
        }

        // ------------------------------------------------------------------ the Earth Worm

        [Test]
        public void TheEarthWormBoresUnderTheBiggestGroupWarnsAndBreaksOutStunning()
        {
            var world = Field();
            world.SetBoosts(1, _ => Lab.Harmless);
            world.SetBoosts(0, _ => Lab.Harmless);
            var worm = world.SpawnVehicle("earth_borer", 1, new Vector2(0f, 60f), (float)Math.PI);
            var group = new List<Vehicle>();
            for (var i = 0; i < 4; i++) group.Add(world.SpawnVehicle("main_battle_tank", 0, new Vector2(-40f + i * 5f, -40f), 0f));
            world.SpawnVehicle("armored_car", 0, new Vector2(60f, -40f), 0f);
            var burrowed = false;
            var events = Run(world, 40f, () => { if (worm.Burrowed) burrowed = true; });
            Assert.IsTrue(burrowed, "it went under");
            var crack = events.FirstOrDefault(e => e.Kind == SimEventKind.Burrowing && e.Value == 1f);
            Assert.AreEqual(SimEventKind.Burrowing, crack.Kind, "the ground cracked first");
            Assert.Less(Vector2.Distance(crack.Position, new Vector2(-32.5f, -40f)), 12f, "under the group, not the lone car");
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.Burrowing && e.Value == 2f), "and it broke out");
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.Damaged && group.Any(g => g.Id == e.Entity)), "the quake hurt the group");
        }

        [Test]
        public void UndergroundTheWormIsOutOfReachAndOutOfSight()
        {
            var world = Field();
            world.RevealAll = false;
            var worm = world.SpawnVehicle("earth_borer", 1, new Vector2(0f, 40f), 0f);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -10f), 0f);
            Run(world, 17.5f);
            Assert.IsTrue(worm.Burrowed || worm.BurrowStage == Vehicle.BurrowState.Diving);
            Run(world, 1f);
            Assert.IsTrue(worm.Burrowed);
            Assert.IsFalse(worm.IsVisibleTo(0), "unseen");
            var hp = worm.Hp;
            world.Damage.Apply(worm, 1000f, DamageType.ShapedCharge);
            Assert.AreEqual(hp, worm.Hp, "untouchable");
        }

        [Test]
        public void JustOutTheWormTakesHalfAsMuchAgain()
        {
            var world = Field();
            var worm = world.SpawnVehicle("earth_borer", 1, new Vector2(0f, 40f), 0f);
            var hp = worm.Hp;
            world.Damage.Apply(worm, 100f, DamageType.ShapedCharge);
            var plain = hp - worm.Hp;
            worm.ExposedUntil = world.Time + 5.0;
            hp = worm.Hp;
            world.Damage.Apply(worm, 100f, DamageType.ShapedCharge);
            Assert.AreEqual(plain * 1.5f, hp - worm.Hp, 1e-2f);
        }

        // ------------------------------------------------------------------ the landing hovercraft

        [Test]
        public void TheHovercraftLandsItsTroopsAFewTimesOnly()
        {
            var world = Field();
            var craft = world.SpawnVehicle("landing_hovercraft", 1, new Vector2(0f, 60f), (float)Math.PI);
            var events = Run(world, 200f);
            var landings = events.Where(e => e.Kind == SimEventKind.TroopsLanding).ToList();
            Assert.AreEqual(craft.Def.Landing.Landings, landings.Count, "five landings, then no more");
            Assert.IsTrue(landings.All(l => l.Value >= 3f && l.Value <= 4f), "3 or 4 vehicles each");
            var landed = world.Vehicles.Count(v => v.Team == 1 && !v.Def.Boss && !v.Def.Static);
            Assert.GreaterOrEqual(landed, 15);
        }

        // ------------------------------------------------------------------ Boss Rush and the guide

        [Test]
        public void BossRushBringsPrompt8sBosses()
        {
            var all = BossRushRules.Everyone().ToList();
            // Play-test 14 deleted two of the five (the rail supergun, the Supreme Commander).
            foreach (var id in new[] { "earth_borer", "command_airship", "landing_hovercraft" })
            {
                CollectionAssert.Contains(all, id);
                Assert.IsTrue(GameContent.LoadCatalog().Escorts.ContainsKey(id), id + " has its escort table (prompt 16 F)");
                Assert.IsTrue(Game.Hud.Strings.Has("guide." + id), id + " has a guide card");
                Assert.IsTrue(Game.Hud.Strings.Has("unit." + id), id + " has a name");
                var def = GameContent.LoadCatalog().Vehicle(id);
                Assert.IsTrue(def.Boss);
                Assert.IsNotNull(def.General, id + " belongs to a general (its radio lines)");
                Assert.IsTrue(Game.Hud.Strings.Has(def.RadioSpawn), id + "'s general speaks");
                Assert.Greater(def.Phases.Count, 0, id + " has a multi-phase bar");
            }
            Assert.AreEqual(BossRushRules.Kinds.Count, BossRushRules.Roster(3).Count, "one of each kind");
        }
    }
}
