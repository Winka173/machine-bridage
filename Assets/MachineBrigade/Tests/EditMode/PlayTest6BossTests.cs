using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 6, the boss and mode pass (DECISIONS 21G): escorts that are vehicles, the boss ranks' reloads, air
    /// defence and strike cap, armour level 5, the endless run after Boss Rush's last boss, the trains in the hunts
    /// and the attack helicopter coming in to its gun.
    /// </summary>
    public class PlayTest6BossTests
    {
        private const float Step = 0.05f;

        [Test]
        public void EscortsAreVehiclesNeverTowers()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var escort in catalog.Escorts.Values)
            {
                var waves = new List<EscortWaveDef>(escort.Phases);
                if (escort.Arrive != null) waves.Add(escort.Arrive);
                foreach (var wave in waves)
                    foreach (var unit in wave.Units)
                    {
                        Assert.IsTrue(catalog.Vehicles.TryGetValue(unit.Unit, out var def), escort.Boss + ": " + unit.Unit);
                        Assert.IsFalse(def.Static, escort.Boss + " is escorted by a tower: " + unit.Unit);
                    }
            }
            // Every boss meets aircraft with something: its own air defence, or air cover among its escorts.
            foreach (var boss in catalog.Vehicles.Values.Where(v => v.Boss && !v.Static && catalog.Escorts.ContainsKey(v.Id)))
            {
                var escort = catalog.Escorts[boss.Id];
                var cover = escort.Phases.Append(escort.Arrive).Where(w => w != null).SelectMany(w => w.Units)
                    .Any(u => u.Role == EscortRole.Cover || catalog.Vehicles[u.Unit].Mounts.Any(m => m.Weapon.CanTarget(true) && m.Weapon.DamageType == DamageType.Fragmentation));
                Assert.IsTrue(cover || BossHunts.AirDefence(boss), boss.Id + " has no answer to aircraft");
            }
        }

        /// <summary>Play-test 8: whatever a boss brings onto the field (escorts, their drops, summons, a big attack's landing party, its factory, pods, landing craft) is a vehicle, never a tower.</summary>
        [Test]
        public void NoBossSummonsOrIsEscortedByATower()
        {
            var catalog = GameContent.LoadCatalog();
            var brought = new List<(string from, string unit)>();
            foreach (var escort in catalog.Escorts.Values)
                foreach (var wave in escort.Phases.Append(escort.Arrive).Where(w => w != null))
                {
                    foreach (var u in wave.Units) brought.Add((escort.Boss + " escort", u.Unit));
                    if (wave.Support != null && catalog.Supports.TryGetValue(wave.Support, out var drop))
                        foreach (var u in drop.Units) brought.Add((escort.Boss + " drop " + drop.Id, u));
                }
            foreach (var s in catalog.Supports.Values.Where(s => s.Id.StartsWith("escort_drop.")))
                foreach (var u in s.Units) brought.Add((s.Id, u));
            foreach (var boss in catalog.Vehicles.Values.Where(v => v.Boss))
            {
                foreach (var k in boss.Skills.Where(k => k.Unit != null)) brought.Add((boss.Id + " " + k.Id, k.Unit));
                if (boss.BigAttack != null)
                    foreach (var st in boss.BigAttack.Strikes)
                        foreach (var u in st.Units) brought.Add((boss.Id + " " + boss.BigAttack.Id, u));
                if (boss.Factory != null)
                    foreach (var list in boss.Factory.Units)
                        foreach (var u in list) brought.Add((boss.Id + " factory", u));
                if (boss.Landing != null)
                    foreach (var u in boss.Landing.Units) brought.Add((boss.Id + " landing", u));
                if (boss.Pods != null) brought.Add((boss.Id + " pods", boss.Pods.Unit));
                if (boss.Craft is { } craft)
                {
                    brought.Add((boss.Id + " craft", craft.Unit));
                    foreach (var u in craft.Carries) brought.Add((boss.Id + " craft", u));
                }
            }
            Assert.Greater(brought.Count, 50);
            foreach (var (from, unit) in brought)
            {
                Assert.IsTrue(catalog.Vehicles.TryGetValue(unit, out var def), from + ": " + unit);
                Assert.IsFalse(def.Static || def.Fort != null, from + " brings a tower or structure: " + unit);
            }
        }

        [Test]
        public void BossRanksReloadFasterHitAircraftHarderAndShrugOffStrikes()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var rank in new[] { "main", "mini" })
            {
                var r = catalog.BossRanks[rank];
                Assert.Greater(r.FireRate, 1f, rank);
                Assert.Greater(r.AirDamage, 1f, rank);
                Assert.Less(r.StrikeTaken, 1f, rank);
                Assert.Greater(r.StrikeCap, 0f, rank);
            }
            var world = BossBalanceMeasure.Lab(catalog, 5);
            var boss = world.SpawnVehicle("behemoth", 1, new Vector2(0f, 20f), MathF.PI);
            Assert.AreEqual(catalog.BossRanks["main"].FireRate, boss.FireFactor, 1e-4f, "its weapons cycle faster");
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(40f, 20f), MathF.PI);
            Assert.AreEqual(1f, tank.FireFactor, 1e-4f, "a vehicle's do not");
            // One barrage and one bomber's load at rank 7 take a little of a boss, never the bar.
            foreach (var id in new[] { "behemoth", "armored_train", "behemoth_inferno" })
            {
                Assert.Less(BossBalanceMeasure.StrikeShare(catalog, id, "artillery_barrage", 3), 0.2f, id + ": one barrage");
                Assert.Less(BossBalanceMeasure.BomberShare(catalog, id, 3), 0.3f, id + ": one bomber's load");
            }
        }

        [Test]
        public void ArmourLevelFiveIsABossesOnly()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.AreEqual(5, ArmourLevels.Max);
            foreach (var v in catalog.Vehicles.Values.Where(v => !v.Boss))
                Assert.LessOrEqual(new[] { v.Armour.Front, v.Armour.Side, v.Armour.Rear, v.Armour.Top }.Max(), ArmourLevels.MaxUnit, v.Id);
            Assert.AreEqual(5, catalog.Vehicles["behemoth"].Armour.Front, "the Behemoth's glacis");
            // The penetration table covers it: a 120 mm dart (4) on level 5 is one under.
            var gun = catalog.Weapons["gun_120mm"];
            Assert.Less(catalog.Damage.Penetration(gun.Penetration, 5), catalog.Damage.Penetration(gun.Penetration, 4));
            // Named and drawn.
            Assert.AreNotEqual("armour.level.5", Strings.Get("armour.level.5"));
            foreach (var kind in new[] { ArmourKind.Ground, ArmourKind.Air, ArmourKind.Structure })
                Assert.IsTrue(Icons.Exists(CombatIcons.Armour(5, kind)), kind + " level 5 icon");
            // A vehicle's data may not ask for it.
            var text = UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/balance").text;
            var bad = text.Replace("\"id\": \"main_battle_tank\", \"value\": 0.92, \"scale\": 0.85, \"armour\": 3,", "\"id\": \"main_battle_tank\", \"value\": 0.92, \"scale\": 0.85, \"armour\": 5,");
            Assert.AreNotEqual(text, bad);
            Assert.Throws<FormatException>(() => Catalog.FromJson(bad));
        }

        [Test]
        public void AfterTheLastBossTheRushMayGoOnEndlessEachBossStronger()
        {
            var catalog = GameContent.LoadCatalog();
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_sandbox"), 3);
            world.EscortSettings = EscortSettings.For(catalog.EscortRules, "Normal", bossRush: true);
            var rules = new BossRushRules { Bosses = new[] { "behemoth_inferno", "bastion_mk0" }, HomeMap = "ashfield", Breather = 3f, EndlessOffer = true, EndlessChoice = 5f };
            var rush = new BossRushMode(rules);
            rush.Setup(world);
            var first = Kill(rush, world);
            Kill(rush, world);
            Assert.IsTrue(rush.EndlessOpen, "the choice after the last boss");
            Assert.IsNull(rush.Result, "not over while the player chooses");
            var cap = world.EscortSettings.Cap;
            Assert.IsTrue(rush.ChooseEndless(world, true));
            Assert.IsTrue(rush.Endless);
            var again = Kill(rush, world);
            Assert.AreEqual("behemoth_inferno", again.id, "the roster again from the top");
            Assert.AreEqual(first.maxHp * (1f + rules.EndlessHp), again.maxHp, first.maxHp * 0.01f, "stronger each step");
            Assert.AreEqual(1, rush.EndlessDefeated);
            Assert.GreaterOrEqual(world.EscortSettings.Cap, cap, "escorts grow with it");
            Assert.AreEqual(1f, world.EscortSettings.Guards, "every guard comes");
            // Its army gone, the endless run ends and the rush stays won.
            foreach (var v in world.VehicleList.Where(v => v.Team == BossRushMode.PlayerTeam && v.IsAlive && !v.Def.Static)) v.Hp = 0f;
            Run(rush, world, () => rush.Result != null, 30f);
            Assert.AreEqual(BossRushMode.PlayerTeam, rush.Result?.WinningTeam);

            // Unanswered, the choice ends the rush there, won.
            var other = new SimWorld(catalog, GameContent.LoadMap("ashfield_sandbox"), 4);
            var once = new BossRushMode(new BossRushRules { Bosses = new[] { "behemoth_inferno" }, HomeMap = "ashfield", Breather = 3f, EndlessOffer = true, EndlessChoice = 2f });
            once.Setup(other);
            Kill(once, other);
            Run(once, other, () => once.Result != null, 5f);
            Assert.AreEqual(BossRushMode.PlayerTeam, once.Result?.WinningTeam);
            Assert.IsFalse(once.Endless);
        }

        [Test]
        public void TheTrainsJoinTheHuntsOnTheirLines()
        {
            var catalog = GameContent.LoadCatalog();
            var story = BossHunts.Story.Select(b => b.Id).ToList();
            Assert.Contains("nuke_train", story);
            Assert.Contains("armored_train", story);
            foreach (var id in new[] { "nuke_train", "armored_train" })
            {
                var def = catalog.Vehicles[id];
                Assert.IsNotNull(def.Arena, id);
                var map = GameContent.LoadMap(def.Arena + "_sandbox");
                Assert.GreaterOrEqual(map.Route(def.RouteName)?.Count ?? 0, 2, id + " has its line on " + def.Arena);
            }
            // Elsewhere the hunt switches to the train's battlefield, carrying the run over.
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_sandbox"), 3);
            var rush = new BossRushMode(new BossRushRules { Bosses = new[] { "nuke_train" }, HomeMap = "ashfield", Breather = 3f });
            rush.Setup(world);
            Run(rush, world, () => rush.SwitchTo != null, 15f);
            Assert.AreEqual("metrocity", rush.SwitchTo?.Map);
            // There it comes in at the start of its line and runs it, and back.
            var metro = new SimWorld(catalog, GameContent.LoadMap("metrocity_sandbox"), 3);
            var onLine = new BossRushMode(new BossRushRules { Bosses = new[] { "nuke_train" }, HomeMap = "ashfield", Resume = rush.SwitchTo });
            onLine.Setup(metro);
            Run(onLine, metro, () => onLine.Boss.IsValid, 15f);
            Assert.IsTrue(metro.TryGetVehicle(onLine.Boss, out var train));
            var line = metro.Map.Route("rail");
            Assert.Less(Vector2.Distance(train.Position, line[0]), 8f, "at the start of its line");
            Assert.IsNotNull(train.OwnRoute, "it drives its line");
        }

        [Test]
        public void TheAttackHelicopterComesInToItsGunWhereNoAirDefenceCovers()
        {
            var catalog = GameContent.LoadCatalog();
            float Closest(bool flak)
            {
                var world = BossBalanceMeasure.Lab(catalog, 7, geared: false);
                var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 30f), MathF.PI);
                tank.HoldFire = true;
                if (flak)
                {
                    var aa = world.SpawnVehicle("aa_vehicle", 1, new Vector2(6f, 34f), MathF.PI);
                    aa.HoldFire = true;
                }
                var heli = world.SpawnVehicle("attack_helicopter", 0, new Vector2(0f, -70f), 0f);
                var closest = float.MaxValue;
                for (var t = 0f; t < 45f && tank.IsAlive; t += Step)
                {
                    if (world.Tick % 20 == 0) world.Submit(new Command(CommandType.Attack, 0, new[] { heli.Id }, target: tank.Id));
                    world.Step(Step);
                    world.ClearEvents();
                    if (t > 8f) closest = MathF.Min(closest, Vector2.Distance(heli.Position, tank.Position));
                }
                return closest;
            }
            var gun = catalog.Weapons["heli_gun"].Range;
            Assert.LessOrEqual(Closest(false), gun + 3f, "in the open it comes in to its cannon");
            Assert.Greater(Closest(true), gun + 3f, "flak by the target: it keeps its standoff");
        }

        // ------------------------------------------------------------------ helpers

        private static void Run(BossRushMode mode, SimWorld world, Func<bool> until, float seconds)
        {
            for (var t = 0f; t < seconds && !until(); t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
        }

        /// <summary>Waits for the next boss and brings it down: its id and full health.</summary>
        private static (string id, float maxHp) Kill(BossRushMode mode, SimWorld world)
        {
            Run(mode, world, () => mode.Boss.IsValid, 40f);
            Assert.IsTrue(world.TryGetVehicle(mode.Boss, out var boss), "a boss came");
            var result = (boss.Def.Id, boss.MaxHp);
            boss.Hp = 0f;
            var before = mode.Defeated;
            Run(mode, world, () => mode.Defeated > before, 2f);
            Assert.AreEqual(before + 1, mode.Defeated);
            return result;
        }
    }
}
