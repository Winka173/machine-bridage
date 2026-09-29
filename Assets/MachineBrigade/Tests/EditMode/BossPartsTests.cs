using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
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
    /// Prompt 9: parts on every boss (the general rules and each boss's list), the part order, the
    /// self-repair, Boss Rush's bounty, checkpoints and the replay, and the rule that the fire and
    /// smoke at the breaks are the view's alone.
    /// </summary>
    public class BossPartsTests
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

        /// <summary>Every boss and how many parts it has (prompt 9 B, fitted to each model's guns; prompt 16 E's new weapons are parts too).</summary>
        internal static readonly Dictionary<string, int> Expected = new()
        {
            ["armored_train"] = 6, ["nuke_train"] = 6, ["behemoth"] = 7, ["behemoth_tempest"] = 5, ["behemoth_inferno"] = 5,
            ["fortress_hive"] = 7, ["mobile_fortress"] = 7, ["fortress_bastion"] = 6, ["silver_bug"] = 6, ["sky_fortress"] = 9,
            ["mega_gunship"] = 8, ["drone_mothership"] = 7, ["rail_supergun"] = 8, ["earth_borer"] = 4, ["command_airship"] = 7,
            ["landing_hovercraft"] = 9, ["supreme_command"] = 3, ["leviathan"] = 9,
        };

        private static Catalog C => GameContent.LoadCatalog();

        [Test]
        public void EveryBossHasItsParts()
        {
            var catalog = C;
            foreach (var boss in catalog.Vehicles.Values.Where(v => v.Boss))
                Assert.IsTrue(Expected.ContainsKey(boss.Id), boss.Id + " has its part list in this test");
            foreach (var (id, count) in Expected)
            {
                var def = catalog.Vehicle(id);
                Assert.AreEqual(count, def.Parts.Count, id);
                var total = def.Parts.Sum(p => p.Hp);
                Assert.That(total, Is.InRange(0.3f, 0.71f), id + ": 50-70 % of the body in all (fewer for bosses with few guns)");
                foreach (var p in def.Parts)
                {
                    Assert.That(p.Hp, Is.InRange(0.07f, 0.15f), $"{id}.{p.Id}: 8-15 % of the body each");
                    Assert.IsTrue(p.Mounts.Count > 0 || p.Skills.Count > 0 || p.Stops.Count > 0 || p.Speed < 1f || p.Turn < 1f || p.Cadence > 1f || p.Spread > 1f,
                        $"{id}.{p.Id} does something when it breaks");
                    Assert.IsTrue(Game.Hud.Strings.Has("part." + p.Kind), $"{id}.{p.Id}: a name for its kind '{p.Kind}'");
                }
                // A mount is on one part at most.
                var mounts = def.Parts.SelectMany(p => p.Mounts).ToList();
                Assert.AreEqual(mounts.Count, mounts.Distinct().Count(), id + ": no mount on two parts");
                Assert.AreEqual(id == "command_airship" ? 0f : 0.3f, def.Parts[0].BreakDamage, 1e-4f, id + ": the body takes 30 % of a broken part");
            }
        }

        [Test]
        public void ABrokenPartsGunsFallSilentAndItsSkillsStop()
        {
            foreach (var id in Expected.Keys)
            {
                var world = Lab.Field(3, 300f);
                var boss = world.SpawnVehicle(id, 1, Vector2.Zero, 0f);
                // Targets of every kind round it, too tough to die in the time.
                var foes = new List<Vehicle>();
                for (var i = 0; i < 6; i++)
                {
                    var angle = i * MathF.PI / 3f;
                    var at = new Vector2(MathF.Sin(angle), MathF.Cos(angle)) * (boss.Radius + 18f);
                    var foe = world.SpawnVehicle(i % 3 == 2 ? "attack_helicopter" : "main_battle_tank", 0, at, angle + MathF.PI);
                    foe.HpScale = 200f;
                    foe.Hp = foe.MaxHp;
                    foes.Add(foe);
                }
                world.SetBoosts(0, _ => Lab.Harmless);
                var silenced = new HashSet<int>();
                var stopped = new HashSet<string>();
                for (var i = 0; i < boss.PartCount; i++)
                {
                    world.Bosses.Break(boss, i);
                    foreach (var m in boss.Def.Parts[i].Mounts) silenced.Add(m);
                    foreach (var s in boss.Def.Parts[i].Skills) stopped.Add(s);
                }
                boss.HpScale = 50f;
                boss.Hp = boss.MaxHp;
                var events = Run(world, 12f);
                // A self-repair may put one part back straight away (the train, the Bastion): its guns fire again, rightly.
                for (var i = 0; i < boss.PartCount; i++)
                    if (boss.IsPartPatched(i))
                        foreach (var m in boss.Def.Parts[i].Mounts) silenced.Remove(m);
                var fired = events.Where(e => e.Kind == SimEventKind.WeaponFired && e.Entity == boss.Id && silenced.Contains(e.Mount)).ToList();
                Assert.AreEqual(0, fired.Count, $"{id}: no round from a broken part's guns");
                foreach (var m in silenced) Assert.IsFalse(boss.MountWorks(m), $"{id}: mount {m} off");
                var used = events.Where(e => e.Kind == SimEventKind.SkillUsed && e.Entity == boss.Id && stopped.Contains(e.DefId)).ToList();
                Assert.AreEqual(0, used.Count, $"{id}: no skill of a broken part");
            }
        }

        [Test]
        public void TheBodyAlwaysTakesDamageExceptTheLockedAirship()
        {
            foreach (var id in Expected.Keys)
            {
                var world = Lab.Field(2);
                var boss = world.SpawnVehicle(id, 1, Vector2.Zero, 0f);
                var before = boss.Hp;
                world.Damage.Apply(boss, 500f, DamageType.ShapedCharge, new HitInfo(null, 0, null, boss.Position, HitKind.Direct, false));
                if (id == "command_airship") Assert.AreEqual(before, boss.Hp, 1e-3f, "the airship's hull is shut until two engines are down");
                else Assert.Less(boss.Hp, before, id + ": the body always takes damage");
            }
        }

        [Test]
        public void ABrokenPartHurtsTheBodyByAThirdOfIt()
        {
            var world = Lab.Field(2);
            var boss = world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
            var i = boss.Def.PartIndex("gun_120");
            var full = boss.PartFullHealth(i);
            Assert.AreEqual(boss.MaxHp * 0.10f, full, 1f);
            var before = boss.Hp;
            world.Bosses.Break(boss, i);
            Assert.AreEqual(full * 0.3f, before - boss.Hp, 1f, "30 % of the part's full health");
            Assert.IsTrue(boss.IsPartBroken(i));
        }

        [Test]
        public void OnlyADirectHitHurtsAPart()
        {
            var world = Lab.Field(2);
            var boss = world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -30f), 0f);
            var i = boss.Def.PartIndex("main_gun");
            var p = new Projectile(tank.Id, 0, tank.Weapon, boss.PartPosition(i), boss.Id, 0f, false) { Origin = tank.Position, Shooter = tank, Main = true, Part = i };
            var partBefore = boss.PartHealth(i);
            var bodyBefore = boss.Hp;
            world.Damage.ResolveImpact(p);
            Assert.Less(boss.PartHealth(i), partBefore, "the round struck the main gun");
            Assert.AreEqual(bodyBefore, boss.Hp, 1e-2f, "the body lost nothing to that round (its splash spares the boss it struck)");
            var parts = Enumerable.Range(0, boss.PartCount).Select(boss.PartHealth).ToArray();
            world.Damage.Splash(boss.PartPosition(i), 8f, 800f, DamageType.HighExplosive, 0, default, tank.Id, false,
                new HitInfo(tank, 0, tank.Weapon, tank.Position, HitKind.Splash, false));
            for (var k = 0; k < boss.PartCount; k++) Assert.AreEqual(parts[k], boss.PartHealth(k), 1e-3f, "a blast never hurts a part");
            Assert.Less(boss.Hp, bodyBefore, "it lands on the body");
            // A strike (the support AI's, anyone's) is a blast too: the parts are untouched.
            world.Damage.Apply(boss, 600f, DamageType.HighExplosive, new HitInfo(null, 0, null, boss.Position, HitKind.Strike, true));
            for (var k = 0; k < boss.PartCount; k++) Assert.AreEqual(parts[k], boss.PartHealth(k), 1e-3f);
        }

        [Test]
        public void PartsScaleWithTheBoss()
        {
            var world = Lab.Field(2);
            var boss = world.SpawnVehicle("fortress_bastion", 1, Vector2.Zero, 0f);
            var full = boss.PartFullHealth(0);
            boss.HpScale *= 1.5f;
            Assert.AreEqual(full * 1.5f, boss.PartFullHealth(0), 1f, "a tougher boss (a campaign's pace, a harder tier) has tougher parts");
        }

        // ------------------------------------------------------------------ what each part's loss does

        [Test]
        public void EachPartTakesItsMechanismWithIt()
        {
            var world = Lab.Field(2, 300f);
            var train = world.SpawnVehicle("armored_train", 1, new Vector2(-60f, 0f), 0f);
            world.Bosses.Break(train, train.Def.PartIndex("locomotive"));
            Assert.AreEqual(0.5f, train.PartSpeed, 1e-4f, "the locomotive down: half speed, not stopped");

            var heli = world.SpawnVehicle("mega_gunship", 1, new Vector2(60f, 0f), 0f);
            var turn = heli.TurnFactor;
            world.Bosses.Break(heli, heli.Def.PartIndex("rotor_rear"));
            Assert.AreEqual(turn * 0.5f, heli.TurnFactor, 1e-4f, "the rear rotor down: it turns at half the rate");

            var spectre = world.SpawnVehicle("sky_fortress", 1, new Vector2(0f, 80f), 0f);
            world.Bosses.Break(spectre, spectre.Def.PartIndex("engine_1"));
            world.Bosses.Break(spectre, spectre.Def.PartIndex("engine_2"));
            Assert.AreEqual(0.85f * 0.85f, spectre.PartSpeed, 1e-4f, "each engine 15 % slower");

            var worm = world.SpawnVehicle("earth_borer", 1, new Vector2(0f, -80f), 0f);
            world.Bosses.Break(worm, worm.Def.PartIndex("drill"));
            Assert.IsTrue(worm.BurrowOff);
            var craft = world.SpawnVehicle("landing_hovercraft", 1, new Vector2(100f, 100f), 0f);
            world.Bosses.Break(craft, craft.Def.PartIndex("ramp"));
            world.Bosses.Break(craft, craft.Def.PartIndex("fan_l"));
            Assert.IsTrue(craft.LandingOff);
            Assert.AreEqual(0.7f, craft.PartSpeed, 1e-4f, "a fan down: 30 % slower");
            var gun = world.SpawnVehicle("rail_supergun", 1, new Vector2(-100f, 100f), 0f);
            world.Bosses.Break(gun, gun.Def.PartIndex("fire_control"));
            world.Bosses.Break(gun, gun.Def.PartIndex("tractor_l"));
            Assert.IsTrue(gun.SpotterOff, "its shells fall wide");
            Assert.AreEqual(1.3f, gun.PartCadence, 1e-4f, "and come slower");
            world.Bosses.Break(gun, gun.Def.PartIndex("main_gun"));
            Assert.IsTrue(gun.BombardOff);

            var events = Run(world, 60f);
            Assert.IsFalse(events.Any(e => e.Kind == SimEventKind.Burrowing && e.Entity == worm.Id), "a worm without its drill never goes under");
            Assert.IsFalse(events.Any(e => e.Kind == SimEventKind.TroopsLanding && e.Entity == craft.Id), "no landings without the ramp");
            Assert.IsFalse(events.Any(e => e.Kind == SimEventKind.StrikeWarning && e.Team == 1), "no shells without the gun");
        }

        [Test]
        public void TheCommandAntennaTakesTheAuraWithIt()
        {
            var world = Lab.Field(2);
            var boss = world.SpawnVehicle("supreme_command", 1, Vector2.Zero, 0f);
            var near = world.SpawnVehicle("main_battle_tank", 1, new Vector2(20f, 0f), 0f);
            Run(world, 0.5f);
            Assert.AreEqual(1.2f, near.CommandDamage, 1e-4f);
            world.Bosses.Break(boss, boss.Def.PartIndex("antenna"));
            Run(world, 0.5f);
            Assert.AreEqual(1f, near.CommandDamage, 1e-4f, "the antenna down: no aura");
            Assert.AreEqual(1f, near.CommandFire, 1e-4f);
        }

        [Test]
        public void TheShieldGeneratorTakesTheShieldsWithIt()
        {
            var world = Lab.Field(2);
            var boss = world.SpawnVehicle("behemoth_tempest", 1, Vector2.Zero, 0f);
            world.Bosses.Break(boss, boss.Def.PartIndex("shield"));
            for (var k = 0; k < boss.Def.Skills.Count; k++)
                Assert.AreEqual(boss.Def.Skills[k].Kind == SkillKind.Shield, boss.SkillOff[k], boss.Def.Skills[k].Id);
        }

        [Test]
        public void TheBastionsTurretsEachCoverTheirOwnQuarter()
        {
            var world = Lab.Field(2);
            var bastion = world.SpawnVehicle("fortress_bastion", 1, Vector2.Zero, 0f);
            var behind = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -28f), 0f);
            behind.HpScale = 100f;
            behind.Hp = behind.MaxHp;
            world.SetBoosts(0, _ => Lab.Harmless);
            var events = Run(world, 12f);
            var fired = events.Where(e => e.Kind == SimEventKind.WeaponFired && e.Entity == bastion.Id).GroupBy(e => e.Mount).ToDictionary(g => g.Key, g => g.Count());
            Assert.IsFalse(fired.ContainsKey(1) || fired.ContainsKey(2), "the front turrets cannot bear on a tank dead astern");
            Assert.IsTrue(fired.ContainsKey(3) || fired.ContainsKey(4), "the rear ones fire on it");
        }

        // ------------------------------------------------------------------ the self-repair

        [Test]
        public void TheSelfRepairPatchesExactlyOnePartTheStrongest()
        {
            var world = Lab.Field(2);
            var train = world.SpawnVehicle("armored_train", 1, Vector2.Zero, 0f);
            var gun = train.Def.PartIndex("gun_car_front");
            var rockets = train.Def.PartIndex("rocket_car");
            var flak = train.Def.PartIndex("flak_car");
            world.Bosses.Break(train, rockets);
            world.Bosses.Break(train, flak);
            world.Bosses.Break(train, gun);
            var bodyBefore = train.Hp;
            var events = Run(world, 3f);
            var back = events.Where(e => e.Kind == SimEventKind.PartRepaired && e.Entity == train.Id).ToList();
            Assert.AreEqual(1, back.Count, "one part back");
            Assert.AreEqual(gun, back[0].Mount, "the one with the strongest gun (the 150 mm)");
            Assert.IsFalse(train.IsPartBroken(gun));
            Assert.IsTrue(train.IsPartPatched(gun));
            Assert.AreEqual(0.5f, train.PartShare(gun), 1e-4f, "at half its health");
            Assert.IsTrue(train.MountWorks(0), "its gun fires again");
            Assert.IsTrue(train.IsPartBroken(rockets) && train.IsPartBroken(flak));
            Assert.AreEqual(bodyBefore, train.Hp, 1f, "the body is not healed");
            events = Run(world, 20f);
            Assert.IsFalse(events.Any(e => e.Kind == SimEventKind.PartRepaired), "once a battle");
        }

        // ------------------------------------------------------------------ aiming and the part order

        [Test]
        public void ShootersGoForThePartMostDangerousToThem()
        {
            var world = Lab.Field(2);
            var boss = world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 26f), MathF.PI);
            var picks = Enumerable.Range(0, 200).Select(_ => world.Bosses.ChoosePart(tank, boss, tank.Weapon)).ToList();
            var body = picks.Count(p => p < 0) / 200f;
            Assert.That(body, Is.InRange(0.25f, 0.55f), "about two rounds in five at the body");
            var parts = picks.Where(p => p >= 0).GroupBy(p => boss.Def.Parts[p].Id).OrderByDescending(g => g.Count()).First().Key;
            Assert.AreEqual("main_gun", parts, "a tank goes for the twin main gun");
            var hunter = world.SpawnVehicle("tank_destroyer", 0, new Vector2(0f, 30f), MathF.PI);
            var hunted = Enumerable.Range(0, 60).Select(_ => world.Bosses.ChoosePart(hunter, boss, hunter.Weapon)).Where(p => p >= 0).ToList();
            Assert.IsTrue(hunted.All(p => boss.Def.Parts[p].Hp >= 0.14f), "a tank hunter goes for the toughest part");
        }

        [Test]
        public void ThePartOrderSendsEveryRoundInReachAtItAndCanBeCancelled()
        {
            var world = Lab.Field(2);
            var boss = world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
            var tanks = Enumerable.Range(0, 3).Select(i => world.SpawnVehicle("main_battle_tank", 0, new Vector2(-8f + i * 8f, 26f), MathF.PI)).ToList();
            var gun120 = boss.Def.PartIndex("gun_120");
            Assert.IsTrue(world.SubmitPlayer(Command.FocusPart(0, boss.Id, "gun_120")).Accepted);
            Assert.IsTrue(world.Bosses.TryGetFocus(0, out var focused, out var part) && focused == boss.Id && part == gun120);
            foreach (var t in tanks)
                for (var k = 0; k < 20; k++) Assert.AreEqual(gun120, world.Bosses.ChoosePart(t, boss, t.Weapon), "every round at the ordered part");
            Assert.IsFalse(world.Submit(Command.FocusPart(1, boss.Id, "gun_120")).Accepted, "not at one's own boss");
            Assert.IsFalse(world.Submit(Command.FocusPart(0, boss.Id, "no_such_part")).Accepted);
            // Cancelled: back to their own choice.
            Assert.IsTrue(world.SubmitPlayer(Command.FocusPart(0, boss.Id, null)).Accepted);
            Assert.IsFalse(world.Bosses.TryGetFocus(0, out _, out _));
            var free = Enumerable.Range(0, 60).Select(_ => world.Bosses.ChoosePart(tanks[1], boss, tanks[1].Weapon)).ToList();
            Assert.IsTrue(free.Any(p => p != gun120), "no longer all at it");
            // Broken: the order ends by itself.
            world.SubmitPlayer(Command.FocusPart(0, boss.Id, "gun_120"));
            world.Bosses.Break(boss, gun120);
            Assert.IsFalse(world.Bosses.TryGetFocus(0, out _, out _), "the part broke: the order is over");
            Assert.IsFalse(world.Submit(Command.FocusPart(0, boss.Id, "gun_120")).Accepted, "a broken part cannot be ordered at");
        }

        // ------------------------------------------------------------------ Boss Rush, checkpoints, the smoke

        [Test]
        public void BossRushPaysTwoCpForEachPartBroken()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(ModeSession.MapFile(GameModeKind.BossRush, "ashfield")), seed: 3);
            var rules = new BossRushRules { StepBounty = 0f };
            var mode = new BossRushMode(rules);
            mode.Setup(world);
            for (var t = 0f; t < 12f && !mode.Boss.IsValid; t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.IsTrue(world.TryGetVehicle(mode.Boss, out var boss));
            world.TryGetEconomy(0, out var ours);
            ours.Cp = 0f;
            world.Bosses.Break(boss, 0);
            world.Bosses.Break(boss, 1);
            mode.Tick(world, Step);
            Assert.AreEqual(2f * rules.PartBounty, ours.Cp, 0.05f, "2 CP a part");
            Assert.AreEqual(2f, rules.PartBounty, 1e-4f);
            mode.Tick(world, Step);
            Assert.AreEqual(4f, ours.Cp, 0.05f, "each part pays once");
        }

        [Test]
        public void ACheckpointsReplayBringsEveryPartBackTheSame()
        {
            SimWorld Battle(out Vehicle boss)
            {
                var world = Lab.Field(7);
                boss = world.SpawnVehicle("behemoth", 1, new Vector2(0f, 20f), MathF.PI);
                // Tough enough to live through the half minute.
                boss.HpScale = 4f;
                boss.Hp = boss.MaxHp;
                for (var i = 0; i < 5; i++) world.SpawnVehicle(i % 2 == 0 ? "main_battle_tank" : "tank_destroyer", 0, new Vector2(-16f + i * 8f, -20f), 0f);
                return world;
            }
            var first = Battle(out var boss);
            var ids = first.VehicleList.Where(v => v.Team == 0).Select(v => v.Id).ToArray();
            for (var t = 0; t < 700; t++)
            {
                if (t == 20) first.SubmitPlayer(new Command(CommandType.Attack, 0, ids, target: boss.Id));
                if (t == 60) first.SubmitPlayer(Command.FocusPart(0, boss.Id, "gun_120"));
                if (t == 300) first.SubmitPlayer(Command.FocusPart(0, boss.Id, null));
                first.Step(Step);
                first.ClearEvents();
            }
            Assert.IsTrue(boss.IsAlive, "the boss is still fighting");
            Assert.Greater(boss.BrokenParts, 0, "parts broke on the way");
            var journal = first.Journal.ToList();
            var again = Battle(out var boss2);
            var next = 0;
            while (again.Tick < first.Tick)
            {
                while (next < journal.Count && journal[next].tick == again.Tick) again.SubmitPlayer(journal[next++].command);
                again.Step(Step);
                again.ClearEvents();
            }
            Assert.AreEqual(first.StateHash(), again.StateHash(), "the same battle, step for step");
            for (var i = 0; i < boss.PartCount; i++)
            {
                Assert.AreEqual(boss.IsPartBroken(i), boss2.IsPartBroken(i), boss.Def.Parts[i].Id);
                Assert.AreEqual(boss.PartShare(i), boss2.PartShare(i), 1e-5f, boss.Def.Parts[i].Id);
                Assert.AreEqual(boss.IsPartPatched(i), boss2.IsPartPatched(i));
            }
            // And the fingerprint does see a part: one part a little hurt changes it.
            var hash = again.StateHash();
            var live = Enumerable.Range(0, boss2.PartCount).First(i => !boss2.IsPartBroken(i));
            boss2.PartFrac[live] -= 0.01f;
            Assert.AreNotEqual(hash, again.StateHash());
        }

        [Test]
        public void ABossNeverCarriesMoreFirePointsThanTheCap()
        {
            // Every part of the biggest boss broken and its body burning: 9 + 3 points, merged to 8 (5 on Low).
            var points = new List<Game.Effects.FireBudget.Point>();
            for (var i = 0; i < 12; i++) points.Add(new Game.Effects.FireBudget.Point(new UnityEngine.Vector3(i * 1.5f, 3f, i % 3), 0.8f, i % 2));
            var merged = Game.Effects.FireBudget.Merge(points, Game.Effects.FireBudget.Cap);
            Assert.AreEqual(Game.Effects.FireBudget.Cap, merged.Count);
            Assert.AreEqual(8, Game.Effects.FireBudget.Cap);
            Assert.AreEqual(5, Game.Effects.FireBudget.Merge(points, Game.Effects.FireBudget.LowCap).Count);
            Assert.AreEqual(12, points.Count, "the input is left as it is");
            // The fire is conserved roughly: merged sizes grow as the square root of the sum of squares.
            var before = points.Sum(p => p.Size * p.Size);
            var after = merged.Sum(p => p.Size * p.Size);
            Assert.AreEqual(before, after, 1e-3f);
            // Under the cap nothing changes.
            Assert.AreEqual(3, Game.Effects.FireBudget.Merge(points.Take(3).ToList(), 8).Count);
        }

        [Test]
        public void EveryBossHasAGuideTipAndItsPartsReadInWords()
        {
            foreach (var id in Expected.Keys)
            {
                var def = C.Vehicle(id);
                Assert.IsTrue(Game.Hud.Strings.Has("guide.parts.tip." + id), id + " has a tip for its parts");
                foreach (var p in def.Parts)
                {
                    var words = Game.Hud.MenuScreen.PartEffects(def, p);
                    Assert.IsFalse(string.IsNullOrWhiteSpace(words), $"{id}.{p.Id}");
                    Assert.IsFalse(words.Contains("part.fx"), $"{id}.{p.Id}: no raw key in '{words}'");
                }
                foreach (var p in def.Parts)
                    if (p.Radio != null) Assert.IsTrue(Game.Hud.Strings.Has(p.Radio), $"{id}.{p.Id}: its radio line {p.Radio}");
            }
        }

        [Test]
        public void TheFireAndSmokeAtTheBreaksNeverBlockSightOrAim()
        {
            var world = Lab.Field(2);
            world.RevealAll = false;
            var boss = world.SpawnVehicle("mobile_fortress", 1, Vector2.Zero, 0f);
            var a = world.SpawnVehicle("scout_jeep", 0, new Vector2(-25f, 0f), 0f);
            var watcher = world.SpawnVehicle("main_battle_tank", 1, new Vector2(25f, 0f), 0f);
            Run(world, 1f);
            var sawBefore = a.IsVisibleTo(1);
            var smokeBefore = world.Strikes.Smoke.Count;
            for (var i = 0; i < boss.PartCount; i++) world.Bosses.Break(boss, i);
            boss.Hp = boss.MaxHp * 0.2f;
            Run(world, 1f);
            Assert.AreEqual(smokeBefore, world.Strikes.Smoke.Count, "no smoke in the simulation from its breaks");
            Assert.AreEqual(sawBefore, a.IsVisibleTo(1), "what the boss's side sees across it is the same");
            Assert.IsFalse(world.Strikes.InSmoke(boss.Position), "its fires are the view's alone");
            Assert.IsTrue(watcher.IsAlive);
        }
    }
}
