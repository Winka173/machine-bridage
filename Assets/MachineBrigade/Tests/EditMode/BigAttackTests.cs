using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 18: every boss's big attack. Its data and words, the difficulty's scaling, its rhythm (about 30 s,
    /// then its cooldown), its zones' shapes and sizes, cancelling it by breaking the part in time (each gun car its
    /// own shells), an EMP's delay, the missiles shot down in flight, smoke against the laser but not the railgun,
    /// units getting out and back (deterministic), and a measure of what each does at the centre of its zone.
    /// </summary>
    public class BigAttackTests
    {
        private const float Step = 0.05f;

        private static Catalog C => Lab.Catalog;

        private static SimWorld Field(int seed = 3)
        {
            var world = Lab.Field(seed);
            world.BigAttackSettings = BigAttackSettings.For(C.BigAttackRules, "Normal");
            // Our side's rounds do nothing: the boss lives through the test.
            world.SetBoosts(0, _ => Lab.Harmless);
            return world;
        }

        private static List<SimEvent> Run(SimWorld world, float seconds, System.Func<bool> until = null)
        {
            var events = new List<SimEvent>();
            for (var t = 0f; t < seconds; t += Step)
            {
                world.Step(Step);
                events.AddRange(world.Events);
                world.ClearEvents();
                if (until != null && until()) break;
            }
            return events;
        }

        /// <summary>Targets that cannot die or move: a group of <paramref name="def"/> round <paramref name="at"/>.</summary>
        private static List<Vehicle> Group(SimWorld world, string def, Vector2 at, int count = 5, bool still = true, float toughness = 60f)
        {
            var list = new List<Vehicle>();
            for (var i = 0; i < count; i++)
            {
                var offset = i == 0 ? Vector2.Zero : new Vector2(System.MathF.Cos(i * 1.3f) * 5f, System.MathF.Sin(i * 1.3f) * 5f);
                var v = world.SpawnVehicle(def, 0, at + offset, SimMath.HeadingOf(-at));
                v.HpScale = toughness;
                v.Hp = v.MaxHp;
                v.Scripted = still;
                list.Add(v);
            }
            return list;
        }

        private static IEnumerable<string> Bosses => BossPartsTests.Expected.Keys;

        // ------------------------------------------------------------------ data and words

        [Test]
        public void EveryBossHasOneBigAttackWithItsWordsAndItsNewParts()
        {
            foreach (var id in Bosses)
            {
                var def = C.Vehicle(id);
                Assert.IsNotNull(def.BigAttack, id + " has a big attack");
                var big = def.BigAttack;
                foreach (var key in new[] { big.NameKey, big.RadioKey, big.CancelledKey, big.GuideKey("how"), big.GuideKey("dodge"), big.GuideKey("stop"),
                             "guide.bigattack.target." + big.Target })
                    Assert.IsTrue(Strings.Has(key), $"{id}: text '{key}'");
                var stats = MenuScreen.BigAttackStats(big);
                Assert.IsFalse(stats.Contains("guide.") || stats.Contains("dtype."), $"{id}: no raw key in '{stats}'");
                Assert.IsTrue(def.Parts.Any(p => big.UsesPart(p.Id)), id + ": a part carries it (break it to stop it)");
            }
            // Prompt 20 F.3's new weapons come after them in the list.
            Assert.IsTrue(C.Vehicle("nuke_train").Parts.Any(p => p.Kind == "erector"));
            Assert.IsTrue(C.Vehicle("drone_mothership").Parts.Any(p => p.Kind == "bombbay"));
            Assert.IsTrue(C.Vehicle("command_airship").Parts.Any(p => p.Kind == "bombbay"));
            Assert.AreEqual("bug_rod_rain", C.Vehicle("silver_bug").BigAttack.Id, "prompt 19 F swapped the Silver Bug's entry for its rod rain");
        }

        [Test]
        public void TheDifficultyScalesDamageCooldownAndWarning()
        {
            var rules = C.BigAttackRules;
            void Check(string key, float damage, float cooldown, float warn)
            {
                var s = rules.For(key);
                Assert.AreEqual(damage, s.Damage, 1e-4f, key + " damage");
                Assert.AreEqual(cooldown, s.Cooldown, 1e-4f, key + " cooldown");
                Assert.AreEqual(warn, s.Warn, 1e-4f, key + " warning");
            }
            Check("Easy", 0.8f, 1.2f, 1f);
            Check("Normal", 1f, 1f, 0f);
            Check("Hard", 1f, 0.9f, 0f);
            Check("VeryHard", 1.1f, 0.8f, 0f);
            Assert.AreEqual(30f, rules.First, 1e-4f);
        }

        // ------------------------------------------------------------------ rhythm, cancelling, EMP

        [Test]
        public void TheFirstComesAtAboutThirtySecondsThenEveryCooldown()
        {
            var times = new List<double>();
            var world = Field();
            world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
            Group(world, "ifv", new Vector2(0f, 32f));
            for (var t = 0f; t < 100f; t += Step)
            {
                world.Step(Step);
                if (world.Events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 0)) times.Add(world.Time);
                world.ClearEvents();
            }
            Assert.That(times.Count, Is.GreaterThanOrEqualTo(2), "two big attacks in 100 s");
            Assert.AreEqual(30.0, times[0], 1.0, "the first about 30 s after it appears");
            // Play-test 6 (DECISIONS 21G): a main boss's rank brings it 15 % sooner.
            Assert.AreEqual(65.0 * C.Vehicle("behemoth").BigAttackScale.Cooldown, times[1] - times[0], 1.0, "then its cooldown, start to start");
        }

        [Test]
        public void BreakingThePartDuringTheWarningCancelsIt()
        {
            var world = Field();
            var boss = world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
            Group(world, "ifv", new Vector2(0f, 32f));
            Run(world, 40f, () => boss.BigAttack.Stage == BigStage.Charging);
            Assert.AreEqual(BigStage.Charging, boss.BigAttack.Stage, "it warns");
            Assert.IsFalse(boss.MountWorks(0), "the main gun holds its fire while it charges");
            world.Bosses.Break(boss, boss.Def.PartIndex("main_gun"));
            var events = Run(world, 6f);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 2), "cancelled");
            Assert.IsFalse(events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 1), "never fired");
            Assert.AreEqual(BigStage.Ready, boss.BigAttack.Stage);
            // Broken for good: no more until a self-repair.
            events = Run(world, 70f);
            Assert.IsFalse(events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 0), "lost with its part");
        }

        [Test]
        public void EachPartBringsItsOwnRounds()
        {
            // The Iron Bird (no self-repair to put the pod back): each rocket pod brings 24 of the 48.
            var world = Field();
            var bird = world.SpawnVehicle("mega_gunship", 1, Vector2.Zero, 0f);
            Group(world, "ifv", new Vector2(0f, 30f));
            Run(world, 40f, () => bird.BigAttack.Stage == BigStage.Charging);
            world.Bosses.Break(bird, bird.Def.PartIndex("pod_l"));
            Run(world, 8f, () => bird.BigAttack.Stage == BigStage.Firing);
            Assert.AreEqual(BigStage.Firing, bird.BigAttack.Stage, "one pod left: it still fires");
            Assert.AreEqual(24, bird.BigAttack.Rounds, "24 rockets of the 48");
        }

        [Test]
        public void AnEmpDelaysTheRailgun()
        {
            var world = Field();
            var tempest = world.SpawnVehicle("behemoth_tempest", 1, Vector2.Zero, 0f);
            Group(world, "main_battle_tank", new Vector2(0f, 40f));
            Run(world, 40f, () => tempest.BigAttack.Stage == BigStage.Charging);
            var due = tempest.BigAttack.FireAt;
            world.Status.Stun(tempest, world.Time + 1.0);
            Run(world, 0.2f);
            Assert.AreEqual(due + 2.0, tempest.BigAttack.FireAt, 1e-3, "2 s more to charge");
        }

        // ------------------------------------------------------------------ zones, shapes and sizes

        [Test]
        public void EveryZoneHasTheShapeAndSizeOfItsData()
        {
            foreach (var id in Bosses)
            {
                var world = Field();
                var boss = world.SpawnVehicle(id, 1, Vector2.Zero, 0f);
                Group(world, "main_battle_tank", new Vector2(0f, 16f));
                Run(world, 70f, () => boss.BigAttack.Stage != BigStage.Ready && boss.BigAttack.Zones.Count > 0);
                var big = boss.BigAttack;
                Assert.IsTrue(big.Stage != BigStage.Ready && big.Zones.Count > 0, id + ": it warned within 70 s");
                Assert.AreEqual(big.Def.First ?? 30.0, big.WarnStart, id.Contains("borer") ? 12.0 : id.Contains("supergun") ? 5.0 : 1.0, id + ": about 30 s in, or its own first (the borer waits for its dive, the supergun for its own shell in flight)");
                var zone = big.Zones[0];
                var s = big.Def.Strikes[0];
                switch (s.Shape)
                {
                    case BigShape.Strip:
                    case BigShape.Line:
                    case BigShape.Sweep:
                        Assert.IsTrue(zone.Rect, id + ": a rectangle");
                        Assert.AreEqual(s.Length * 0.5f, zone.HalfLength, 1e-3f, id + ": its length");
                        Assert.AreEqual(s.Width * 0.5f, zone.HalfWidth, 1e-3f, id + ": its width");
                        break;
                    case BigShape.Missile:
                        Assert.IsFalse(zone.Rect, id);
                        Assert.AreEqual(s.Radius, zone.Radius, 1e-3f, id + ": the landing's blast");
                        Assert.Greater(zone.Due, big.FireAt + s.Flight - 0.1, id + ": landing after its flight");
                        break;
                    case BigShape.Circle:
                        Assert.IsFalse(zone.Rect, id);
                        Assert.AreEqual(s.Area > 0f ? s.Area : s.Radius + s.Scatter, zone.Radius, 1e-3f, id + ": its circle");
                        break;
                    case BigShape.Charge:
                        Assert.IsTrue(zone.Rect, id + ": a charge warns along its path");
                        break;
                    case BigShape.Quake:
                        Assert.AreEqual(s.Radius, zone.Radius, 1e-3f, id + ": the quake's circle");
                        break;
                    case BigShape.Rods:
                        Assert.AreEqual(s.Count, big.Zones.Count, id + ": one ring a rod");
                        Assert.IsTrue(big.Zones.All(z => !z.Rect && System.Math.Abs(z.Radius - s.Radius) < 1e-3f), id + ": each its rod's radius");
                        break;
                    default:
                        Assert.IsFalse(zone.Rect, id);
                        break;
                }
            }
        }

        // ------------------------------------------------------------------ in flight, smoke

        [Test]
        public void TheDoomsdayMissileCanBeShotDown()
        {
            var world = Field();
            var train = world.SpawnVehicle("nuke_train", 1, new Vector2(-100f, -100f), 0f);
            var aim = new Vector2(40f, 40f);
            var tanks = Group(world, "main_battle_tank", aim);
            foreach (var at in new[] { new Vector2(30f, 40f), new Vector2(50f, 40f), new Vector2(40f, 52f) }) world.SpawnVehicle("c_ram", 0, at, 0f);
            var taken = 0f;
            DamageSystem.DamageLog = (attacker, victim, damage, kind, weapon) =>
            {
                if (attacker == train && weapon == null && victim.Team == 0) taken += damage;
            };
            try
            {
                var events = Run(world, 60f, () => train.BigAttack.Stage == BigStage.Ready && train.BigAttack.LastStart > 1.0);
                Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 1), "it launched");
                Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 5), "shot down in flight");
                Assert.AreEqual(0f, taken, 1e-3f, "nothing landed");
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
        }

        /// <summary>
        /// Prompt 19 F moved the Silver Bug off its laser sweep (the one big attack smoke cut), so no boss's big attack is
        /// stopped by smoke now (DECISIONS 18A); the railgun's slug still is not.
        /// </summary>
        [Test]
        public void SmokeDoesNothingToTheRailgun()
        {
            var dealt = new Dictionary<Vehicle, float>();
            DamageSystem.DamageLog = (attacker, victim, damage, kind, weapon) =>
            {
                if (weapon == null && kind == HitKind.Pierce) dealt[victim] = (dealt.TryGetValue(victim, out var d) ? d : 0f) + damage;
            };
            try
            {
                var world = Field();
                var tempest = world.SpawnVehicle("behemoth_tempest", 1, Vector2.Zero, 0f);
                var front = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 30f), SimMath.HeadingOf(new Vector2(0f, -1f)));
                var back = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 42f), SimMath.HeadingOf(new Vector2(0f, -1f)));
                foreach (var v in new[] { front, back })
                {
                    v.HpScale = 60f;
                    v.Hp = v.MaxHp;
                    v.Scripted = true;
                }
                dealt.Clear();
                Run(world, 40f, () => tempest.BigAttack.Stage == BigStage.Charging);
                world.Strikes.AddSmoke(0, front.Position, 5f, 30f);
                Run(world, 8f, () => tempest.BigAttack.Stage == BigStage.Ready);
                Assert.IsTrue(dealt.ContainsKey(front) && dealt.ContainsKey(back), "the slug went through both");
                Assert.AreEqual(0.85f, dealt[back] / dealt[front], 0.02f, "15 % less behind; smoke did nothing to it");
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
        }

        // ------------------------------------------------------------------ getting out of the way

        [Test]
        public void UnitsInTheZoneGetOutAndComeBackTheSameEveryTime()
        {
            (Vector2 during, Vector2 after, float hp) Once()
            {
                var world = Field(9);
                var boss = world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
                var group = Group(world, "ifv", new Vector2(0f, 34f), 3, still: false, toughness: 100f);
                var start = group[0].Position;
                Run(world, 40f, () => boss.BigAttack.Stage == BigStage.Charging);
                var zone = boss.BigAttack.Zones[0];
                Run(world, 10f, () => boss.BigAttack.Stage == BigStage.Firing);
                var during = group[0].Position;
                Assert.IsFalse(zone.Contains(during, group[0].Radius), "out of the circle when it lands");
                Run(world, 20f);
                Assert.Less(Vector2.Distance(group[0].Position, start), 4f, "back where it stood");
                return (during, group[0].Position, group[0].Hp);
            }
            var a = Once();
            var b = Once();
            Assert.AreEqual(a.during, b.during, "deterministic");
            Assert.AreEqual(a.after, b.after);
            Assert.AreEqual(a.hp, b.hp);
        }

        // ------------------------------------------------------------------ the measure

        /// <summary>Each boss's primary target by its entry's "target".</summary>
        private static string PrimaryOf(string target) => target switch
        {
            "light" or "thin" => "armored_car",
            "heavy" or "still" or "armour" or "tanks" => "main_battle_tank",
            "base" or "defences" => "gun_turret",
            _ => "ifv",
        };

        /// <summary>
        /// Prompt 18 A.4 and F: what each big attack does at the centre of its zone to five of its primary target
        /// (standing, not dodging), as a share of one's full health at rank 1, and that it never wipes out the lot.
        /// The shares are printed for the testing phase's 5-seed tuning (the goal is 40-60 %).
        /// </summary>
        [Test]
        public void EachBigAttackAtItsCentreHurtsButNeverWipesOutAGroup()
        {
            var lines = new List<string>();
            foreach (var id in Bosses)
            {
                var world = Field();
                var boss = world.SpawnVehicle(id, 1, Vector2.Zero, 0f);
                var primary = PrimaryOf(C.Vehicle(id).BigAttack.Target);
                var group = Group(world, primary, new Vector2(0f, 16f));
                var taken = new Dictionary<Vehicle, float>();
                DamageSystem.DamageLog = (attacker, victim, damage, kind, weapon) =>
                {
                    if (attacker == boss && weapon == null && kind != HitKind.Burn && boss.BigAttack.Stage != BigStage.Ready)
                        taken[victim] = (taken.TryGetValue(victim, out var d) ? d : 0f) + damage;
                };
                try
                {
                    Run(world, 70f, () => boss.BigAttack.Stage == BigStage.Firing ||
                                          (boss.BigAttack.Def.Strikes[0].Shape == BigShape.Quake && boss.BigAttack.LastStart > 1.0 && boss.BigAttack.Stage == BigStage.Ready));
                    Run(world, 14f, () => boss.BigAttack.Stage == BigStage.Ready);
                }
                finally
                {
                    DamageSystem.DamageLog = null;
                }
                var full = C.Vehicle(primary).MaxHp;
                var centre = taken.TryGetValue(group[0], out var c) ? c / full : 0f;
                var wiped = group.All(v => taken.TryGetValue(v, out var d) && d >= full);
                lines.Add($"{id} ({C.Vehicle(id).BigAttack.Id}) on {primary}: centre {centre:P0}, group {string.Join(" ", group.Select(v => (taken.TryGetValue(v, out var d) ? d / full : 0f).ToString("P0")))}");
                Assert.IsFalse(wiped, id + ": a full-health group is never wiped out");
            }
            Debug.Log("Prompt 18 centre damage (rank 1, Normal):\n" + string.Join("\n", lines));
            TestContext.WriteLine(string.Join("\n", lines));
        }
    }
}
