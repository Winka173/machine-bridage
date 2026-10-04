using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Sandbox;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Combat final 04/10 (Docs/prompts/combat_rebalance_vi.md sections 1-15 and the addendum, DECISIONS "Combat final 04/10
    /// (lane A)"): the direct penetration table (1.20 / 1.00 / 0.85 / 0.65 / 0.40 / 0.15 / 0.08), the separate top attack
    /// table (1.15 / 1.10 / 0.95 / 0.75 / 0.50 / 0.25 / 0.12), the damage type table, thermobaric replacing high explosive on
    /// structures, the bombs and Hellfire as top attacks, the ATGM changes, the Kh-29 and big-missile blasts, the runtime /
    /// AI estimate / generated pack parity, no NaN, deterministic replay, boss armour and health unchanged.
    /// Deterministic and EditMode. Written by lane A, not run (the lead runs them).
    /// </summary>
    public class CombatFinalTests
    {
        private const float Eps = 1e-5f;

        private static Catalog C => GameContent.LoadCatalog();

        /// <summary>Both the shipped data's table and the code's default (the fallback without balance.json's).</summary>
        private static IEnumerable<(string name, DamageTable table)> Tables()
        {
            yield return ("balance.json", C.Damage);
            yield return ("DamageTable.Default", DamageTable.Default);
        }

        // ------------------------------------------------------------------------------------------ 1. direct penetration

        private static readonly (int diff, float mult)[] Direct =
        {
            (3, 1.20f), (2, 1.20f), (1, 1.00f), (0, 0.85f), (-1, 0.65f), (-2, 0.40f), (-3, 0.15f), (-4, 0.08f), (-5, 0.08f), (-6, 0.08f),
        };

        private static readonly (int diff, float mult)[] Top =
        {
            (3, 1.15f), (2, 1.15f), (1, 1.10f), (0, 0.95f), (-1, 0.75f), (-2, 0.50f), (-3, 0.25f), (-4, 0.12f), (-5, 0.12f), (-6, 0.12f),
        };

        [Test]
        public void DirectPenetrationBucketsPlus3ToMinus6()
        {
            foreach (var (name, table) in Tables())
            {
                Assert.AreEqual(7, DamageTable.PenetrationSteps, "seven steps: the <= -4 bucket is its own");
                foreach (var (diff, mult) in Direct)
                {
                    // The same difference read at several armour levels (a boss's 5 included).
                    foreach (var armour in new[] { 0, 2, 5 })
                        Assert.AreEqual(mult, table.Penetration(armour + diff, armour), Eps, $"{name}: direct pen-armour {diff:+0;-0;0} at armour {armour}");
                }
                var steps = new[] { 1.20f, 1.00f, 0.85f, 0.65f, 0.40f, 0.15f, 0.08f };
                for (var i = 0; i < steps.Length; i++) Assert.AreEqual(steps[i], table.PenetrationStep(i), Eps, $"{name}: direct step {i}");
            }
        }

        [Test]
        public void RoofAndAircraftWithoutTopAttackNeverOvermatch()
        {
            // Section 1's roof rule now holds for every roof hit that is not a top attack (lobbed shells, an aeroplane's
            // fire, strikes) and for aircraft; a topAttack weapon reads its own table (see TopAttack* below).
            foreach (var (name, table) in Tables())
            {
                Assert.AreEqual(1.00f, table.Penetration(4, 2, overmatch: false), Eps, $"{name}: pen 4 on roof 2");
                Assert.AreEqual(1.00f, table.Penetration(4, 3, overmatch: false), Eps, $"{name}: pen 4 on roof 3");
                Assert.AreEqual(0.85f, table.Penetration(4, 4, overmatch: false), Eps, $"{name}: pen 4 on roof 4");
                Assert.AreEqual(0.65f, table.Penetration(4, 5, overmatch: false), Eps, $"{name}: pen 4 on roof 5");
                Assert.AreEqual(0.08f, table.Penetration(0, 4, overmatch: false), Eps, $"{name}: <= -4 on a roof");
                Assert.AreEqual(1.00f, table.ArmourMultiplier(4, 2, TargetKind.Ground, roof: true, topAttack: false), Eps, $"{name}: lobbed on a roof");
                Assert.AreEqual(1.00f, table.ArmourMultiplier(6, 0, TargetKind.Air, roof: false, topAttack: false), Eps, $"{name}: an aircraft");
                Assert.AreEqual(1.00f, table.ArmourMultiplier(6, 0, TargetKind.Air, roof: true, topAttack: true), Eps,
                    $"{name}: aircraft keep their own system even for a top-attack round");
            }
        }

        // ------------------------------------------------------------------------------------------ addendum: top attack table

        [Test]
        public void TopAttackBucketsPlus3ToMinus6()
        {
            foreach (var (name, table) in Tables())
            {
                foreach (var (diff, mult) in Top)
                    foreach (var roof in new[] { 0, 2, 5 })
                    {
                        Assert.AreEqual(mult, table.TopAttack(roof + diff, roof), Eps, $"{name}: top attack pen-roof {diff:+0;-0;0} at roof {roof}");
                        Assert.AreEqual(mult, table.ArmourMultiplier(roof + diff, roof, TargetKind.Ground, roof: true, topAttack: true), Eps, $"{name}: ground");
                        Assert.AreEqual(mult, table.ArmourMultiplier(roof + diff, roof, TargetKind.Structure, roof: true, topAttack: true), Eps, $"{name}: structure");
                    }
                var steps = new[] { 1.15f, 1.10f, 0.95f, 0.75f, 0.50f, 0.25f, 0.12f };
                for (var i = 0; i < steps.Length; i++) Assert.AreEqual(steps[i], table.TopAttackStep(i), Eps, $"{name}: top step {i}");
                // No cap at one level above and no product of the two tables.
                Assert.Greater(table.TopAttack(6, 2), 1.0f, "no x1 cap for a top attack");
                foreach (var (diff, _) in Top)
                {
                    var one = table.ArmourMultiplier(2 + diff, 2, TargetKind.Ground, roof: true, topAttack: true);
                    var direct = table.Penetration(2 + diff, 2, overmatch: false);
                    Assert.AreEqual(table.TopAttack(2 + diff, 2), one, Eps, $"{name}: the top attack table alone at {diff}");
                    if (Math.Abs(direct - 1f) > Eps)
                        Assert.AreNotEqual(table.TopAttack(2 + diff, 2) * direct, one, $"{name}: never both tables at {diff}");
                }
            }
        }

        [Test]
        public void DirectRegressionIsUnchangedByTheTopAttackTable()
        {
            foreach (var (name, table) in Tables())
                foreach (var (diff, mult) in Direct)
                    Assert.AreEqual(mult, table.ArmourMultiplier(3 + diff, 3, TargetKind.Ground, roof: false, topAttack: false), Eps, $"{name}: direct {diff}");
        }

        // ------------------------------------------------------------------------------------------ 2. damage type table

        [Test]
        public void DamageTypeTableIsTheFinalOne()
        {
            var expected = new Dictionary<DamageType, (float g, float a, float s)>
            {
                [DamageType.Kinetic] = (1.20f, 0.30f, 0.70f),
                [DamageType.ShapedCharge] = (1.30f, 0.20f, 0.45f),
                [DamageType.HighExplosive] = (1.00f, 0.00f, 1.60f),
                [DamageType.Fragmentation] = (0.45f, 1.35f, 0.10f),
                [DamageType.Fire] = (1.35f, 0.00f, 1.10f),
                [DamageType.Energy] = (0.90f, 1.50f, 0.40f),
            };
            foreach (var (name, table) in Tables())
                foreach (var (type, (g, a, s)) in expected)
                {
                    Assert.AreEqual(g, table.Type(type, TargetKind.Ground), Eps, $"{name}: {type} ground");
                    Assert.AreEqual(a, table.Type(type, TargetKind.Air), Eps, $"{name}: {type} air");
                    Assert.AreEqual(s, table.Type(type, TargetKind.Structure), Eps, $"{name}: {type} structure");
                }
        }

        [Test]
        public void ThermobaricReplacesHighExplosiveOnStructures()
        {
            foreach (var (name, table) in Tables())
            {
                Assert.AreEqual(2.0f, table.ThermobaricStructure, Eps, name);
                Assert.AreEqual(2.0f, table.TypeOf(DamageType.HighExplosive, TargetKind.Structure, thermobaric: true), Eps, $"{name}: 2.0, not 1.60 x 2.0");
                Assert.AreEqual(1.6f, table.TypeOf(DamageType.HighExplosive, TargetKind.Structure, thermobaric: false), Eps, name);
                Assert.AreEqual(1.0f, table.TypeOf(DamageType.HighExplosive, TargetKind.Ground, thermobaric: true), Eps, $"{name}: only structures");
            }
            var tos = C.Weapons.Values.First(w => w.Thermobaric && w.DamageType == DamageType.HighExplosive);
            Assert.AreEqual(2.0f, C.Damage.TypeOf(tos, TargetKind.Structure), Eps, tos.Id);
        }

        // ------------------------------------------------------------------------------------------ combined

        [Test]
        public void DamageTypeTimesPenetration()
        {
            foreach (var (name, t) in Tables())
            {
                Assert.AreEqual(1.02f, t.Effective(DamageType.Kinetic, 3, 3, TargetKind.Ground), Eps, $"{name}: kinetic level");
                Assert.AreEqual(1.105f, t.Effective(DamageType.ShapedCharge, 3, 3, TargetKind.Ground), Eps, $"{name}: shaped charge level");
                Assert.AreEqual(0.78f, t.Effective(DamageType.Kinetic, 2, 3, TargetKind.Ground), Eps, $"{name}: kinetic -1");
                Assert.AreEqual(0.845f, t.Effective(DamageType.ShapedCharge, 2, 3, TargetKind.Ground), Eps, $"{name}: shaped charge -1");
                Assert.AreEqual(0.52f, t.Effective(DamageType.ShapedCharge, 1, 3, TargetKind.Ground), Eps, $"{name}: shaped charge -2");
                // Addendum: top attack, shaped charge 1.30 and high explosive 1.00 on the ground times the top attack table.
                var sc = new[] { 1.495f, 1.495f, 1.43f, 1.235f, 0.975f, 0.65f, 0.325f, 0.156f, 0.156f, 0.156f };
                var he = new[] { 1.15f, 1.15f, 1.10f, 0.95f, 0.75f, 0.50f, 0.25f, 0.12f, 0.12f, 0.12f };
                for (var i = 0; i < Top.Length; i++)
                {
                    var diff = Top[i].diff;
                    Assert.AreEqual(sc[i], t.Effective(DamageType.ShapedCharge, 1 + diff, 1, TargetKind.Ground, roof: true, topAttack: true), Eps, $"{name}: SC top {diff}");
                    Assert.AreEqual(he[i], t.Effective(DamageType.HighExplosive, 1 + diff, 1, TargetKind.Ground, roof: true, topAttack: true), Eps, $"{name}: HE top {diff}");
                }
            }
        }

        // ------------------------------------------------------------------------------------------ 4-6. weapons

        [Test]
        public void AirDroppedBombsAreTopAttacks()
        {
            var w = C.Weapons;
            Assert.AreEqual(250f, w["guided_bomb"].Damage, Eps, "guided_bomb 210 -> 250");
            Assert.AreEqual(DamageType.HighExplosive, w["guided_bomb"].DamageType);
            Assert.AreEqual(3, w["guided_bomb"].Penetration, "penetration kept");
            foreach (var id in new[] { "guided_bomb", "jet_bombs", "bomber_payload", "stealth_payload", "hellfire_standoff" })
                Assert.IsTrue(w[id].TopAttack, id);
            Assert.AreEqual(310f, w["jet_bombs"].Damage, Eps, "raw damage kept");
            Assert.AreEqual(420f, w["bomber_payload"].Damage, Eps);
            Assert.AreEqual(892f, w["stealth_payload"].Damage, Eps);
            // Every air-dropped ground bomb is a top attack (the car bomb is not dropped).
            foreach (var bomb in w.Values.Where(x => x.Family == "bomb" && x.Projectile == ProjectileKind.Bomb && x.CanTarget(false)))
                Assert.IsTrue(bomb.TopAttack, bomb.Id);
            // Kept: the top attacks the data had.
            foreach (var id in new[] { "kornet_top", "lancet", "fpv_swarm" })
                Assert.IsTrue(w[id].TopAttack, id);
            // Not turned into top attacks.
            foreach (var id in new[] { "atgm", "gun_launched_atgm", "kornet_twin", "atgm_heavy", "tower_kornet", "kh29", "maverick", "jassm", "air_cruise_missile", "cruise_missile_ground" })
                Assert.IsFalse(w[id].TopAttack, id);
        }

        [Test]
        public void BasicAtgmRebalance()
        {
            var w = C.Weapons;
            Assert.AreEqual(210f, w["atgm"].Damage, Eps, "atgm 190 -> 210");
            Assert.AreEqual(4, w["atgm"].Penetration, "atgm penetration kept");
            Assert.AreEqual(230f, w["gun_launched_atgm"].Damage, Eps, "gun_launched_atgm 200 -> 230");
            Assert.AreEqual(4, w["gun_launched_atgm"].Penetration, "gun_launched_atgm 3 -> 4");
            Assert.AreEqual(260f, w["hellfire_standoff"].Damage, Eps, "Hellfire not buffed");
            Assert.AreEqual(345f, w["maverick"].Damage, Eps, "Maverick not buffed");
        }

        [Test]
        public void Kh29AndBigMissileBlasts()
        {
            var kh29 = C.Weapons["kh29"];
            Assert.AreEqual(378f, kh29.Damage, Eps, "direct damage unchanged");
            Assert.AreEqual(4, kh29.Penetration, "penetration unchanged");
            Assert.AreEqual(DamageType.ShapedCharge, kh29.DamageType, "damage type unchanged");
            Assert.AreEqual(7f, kh29.SplashRadius, Eps, "core 7 m");
            Assert.AreEqual(14f, kh29.SplashEdge, Eps, "edge 14 m");
            Assert.AreEqual(3.5f, C.Weapons["maverick"].SplashRadius, Eps, "Maverick-class core 3-4 m");
            var typhon = C.Weapons["cruise_missile_ground"];
            Assert.AreEqual(8f, typhon.SplashRadius, Eps, "450 kg cruise missile core 8-10 m");
            Assert.AreEqual(16f, typhon.SplashEdge, Eps, "edge 16-20 m");
            // Small ATGMs keep no splash.
            foreach (var id in new[] { "atgm", "gun_launched_atgm", "kornet_twin", "hellfire_standoff" })
                Assert.AreEqual(0f, C.Weapons[id].SplashRadius, Eps, id);
        }

        // ------------------------------------------------------------------------------------------ runtime, AI, export

        [Test]
        public void EveryTopAttackWeaponGoesThroughTheTopAttackTable()
        {
            var t = C.Damage;
            var count = 0;
            foreach (var w in C.Weapons.Values.Where(x => x.TopAttack && x.CanTarget(false) && x.Damage > 0f))
            {
                count++;
                for (var roof = 0; roof <= ArmourLevels.Max; roof++)
                {
                    var expected = t.TopAttack(w.Penetration, roof) * t.TypeOf(w, TargetKind.Ground);
                    Assert.AreEqual(expected, t.Effective(w, roof, TargetKind.Ground), Eps, $"{w.Id} on roof {roof}");
                    Assert.AreEqual(t.TopAttack(w.Penetration, roof) * t.TypeOf(w, TargetKind.Structure), t.Effective(w, roof, TargetKind.Structure), Eps, $"{w.Id} on a structure");
                }
            }
            Assert.Greater(count, 10, "the drones, kornet_top, the bombs and hellfire_standoff");
            foreach (var w in C.Weapons.Values.Where(x => !x.TopAttack && !x.Indirect && x.CanTarget(false) && x.Damage > 0f))
                for (var a = 0; a <= ArmourLevels.Max; a++)
                    Assert.AreEqual(t.Penetration(w.Penetration, a) * t.TypeOf(w, TargetKind.Ground), t.Effective(w, a, TargetKind.Ground), Eps, $"{w.Id}: direct");
        }

        private static SimWorld Proving(out Vehicle tank, out Vehicle shooter)
        {
            var world = new SimWorld(C, SandboxMaps.Flat(), 5);
            tank = world.SpawnVehicle("main_battle_tank", 1, Vector2.Zero, 0f);
            shooter = world.SpawnVehicle("ifv", 0, new Vector2(0f, 20f), (float)Math.PI);
            return world;
        }

        [Test]
        public void RuntimeHitsAndTheAiEstimateMatchTheTables()
        {
            var world = Proving(out var tank, out var shooter);
            var t = world.Catalog.Damage;
            var a = tank.Armour;
            Assert.AreEqual(new ArmourLevels(3, 2, 1, 1), a, "a battle tank's 3 / 2 / 1 / 1");
            float Runtime(WeaponDef w) =>
                world.Damage.HitMultiplier(tank, w.DamageType, new HitInfo(shooter, 0, w, shooter.Position, HitKind.Direct, w.Indirect));
            // Top attacks: the roof (1), the top attack table, the damage type; the AI's estimate is the same number.
            foreach (var id in new[] { "kornet_top", "lancet", "fpv_swarm", "guided_bomb", "jet_bombs", "bomber_payload", "stealth_payload", "hellfire_standoff" })
            {
                var w = world.Catalog.Weapons[id];
                var expected = t.TopAttack(w.Penetration, a.Top) * t.Type(w.DamageType, TargetKind.Ground);
                Assert.AreEqual(expected, Runtime(w), Eps, $"{id}: runtime");
                Assert.AreEqual(expected, world.Damage.Estimate(w, shooter, tank), Eps, $"{id}: AI estimate");
                Assert.AreEqual(expected, Matchup.Against(t, w, tank.Def), Eps, $"{id}: matchup");
            }
            Assert.AreEqual(1.3f * 1.15f, Runtime(world.Catalog.Weapons["kornet_top"]), Eps, "pen 4 on roof 1: +3 -> 1.15 x 1.30");
            Assert.AreEqual(1.0f * 1.15f, Runtime(world.Catalog.Weapons["guided_bomb"]), Eps, "pen 3 on roof 1: +2 -> 1.15 x HE 1.00");
            // Direct fire from the front: the front (3), the direct table.
            foreach (var id in new[] { "atgm", "gun_launched_atgm", "kornet_twin", "kh29", "maverick" })
            {
                var w = world.Catalog.Weapons[id];
                var expected = t.Penetration(w.Penetration, a.Front) * t.Type(w.DamageType, TargetKind.Ground);
                Assert.AreEqual(expected, Runtime(w), Eps, $"{id}: runtime");
                Assert.AreEqual(expected, world.Damage.Estimate(w, shooter, tank), Eps, $"{id}: AI estimate");
            }
            Assert.AreEqual(1.0f * 1.3f, Runtime(world.Catalog.Weapons["atgm"]), Eps, "pen 4 on front 3: +1 -> 1.00 x 1.30");
            // A lobbed shell that is not a top attack: the roof, the direct table, no overmatch.
            var shell = world.Catalog.Weapons.Values.First(w => w.Indirect && !w.TopAttack && w.Projectile == ProjectileKind.Shell && w.CanTarget(false) && w.Penetration >= 3);
            Assert.AreEqual(t.Penetration(shell.Penetration, a.Top, overmatch: false) * t.Type(shell.DamageType, TargetKind.Ground), Runtime(shell), Eps, shell.Id);
        }

        [Test]
        public void ATopAttackOnAStructureMeetsItsRoof()
        {
            var world = new SimWorld(C, SandboxMaps.Flat(), 5);
            var def = world.Catalog.Vehicles.Values.FirstOrDefault(v => v.Kind == TargetKind.Structure && !v.Boss && v.Armour.Front > v.Armour.Top);
            Assume.That(def, Is.Not.Null, "a structure with a thicker front than roof (an embrasured tower)");
            var tower = world.SpawnVehicle(def.Id, 1, Vector2.Zero, 0f);
            var shooter = world.SpawnVehicle("ifv", 0, new Vector2(0f, 20f), (float)Math.PI);
            var t = world.Catalog.Damage;
            var w = world.Catalog.Weapons["kornet_top"];
            var got = world.Damage.HitMultiplier(tower, w.DamageType, new HitInfo(shooter, 0, w, shooter.Position, HitKind.Direct, false));
            Assert.AreEqual(t.TopAttack(w.Penetration, def.Armour.Top) * t.Type(DamageType.ShapedCharge, TargetKind.Structure), got, Eps);
        }

        /// <summary>The generated balance pack (Tools/export, Docs/export/current/01_chien_dau.md) shows the runtime's tables.</summary>
        [Test]
        public void TheGeneratedPackMatchesTheRuntime()
        {
            var md = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "Docs", "export", "current", "01_chien_dau.md"));
            Assume.That(File.Exists(md), md);
            var lines = File.ReadAllLines(md);
            List<string[]> Sheet(string name)
            {
                var start = Array.FindIndex(lines, l => l.StartsWith("Sheet 01_chien_dau/" + name + " "));
                Assert.GreaterOrEqual(start, 0, name);
                var rows = new List<string[]>();
                for (var i = start + 1; i < lines.Length && !lines[i].StartsWith("Sheet "); i++)
                {
                    if (!lines[i].StartsWith("| ") || lines[i].StartsWith("| id ")) continue;
                    rows.Add(lines[i].Trim('|', ' ').Split('|').Select(c => c.Trim()).ToArray());
                }
                return rows;
            }
            float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);
            var t = C.Damage;
            var direct = Sheet("Bang_xuyen_giap");
            var top = Sheet("Bang_danh_noc");
            Assert.AreEqual(DamageTable.PenetrationSteps, direct.Count, "seven direct steps in the pack");
            Assert.AreEqual(DamageTable.PenetrationSteps, top.Count, "seven top attack steps in the pack");
            for (var i = 0; i < DamageTable.PenetrationSteps; i++)
            {
                Assert.AreEqual(t.PenetrationStep(i), F(direct[i][2]), Eps, $"direct buoc_{i}");
                Assert.AreEqual(t.TopAttackStep(i), F(top[i][2]), Eps, $"top attack buoc_{i}");
            }
            foreach (var row in Sheet("Bang_sat_thuong"))
            {
                var type = (DamageType)Enum.Parse(typeof(DamageType), row[0]);
                Assert.AreEqual(t.Type(type, TargetKind.Ground), F(row[1]), Eps, $"{type} ground");
                Assert.AreEqual(t.Type(type, TargetKind.Air), F(row[2]), Eps, $"{type} air");
                Assert.AreEqual(t.Type(type, TargetKind.Structure), F(row[3]), Eps, $"{type} structure");
            }
        }

        // ------------------------------------------------------------------------------------------ regression

        [Test]
        public void NoNaNAndNoDivisionByZero()
        {
            foreach (var (name, t) in Tables())
            {
                foreach (var v in new[] { float.NaN, float.PositiveInfinity, float.NegativeInfinity, -100f, 100f, 0f })
                {
                    Assert.IsTrue(float.IsFinite(t.Penetration(v, 3)), $"{name}: direct pen {v}");
                    Assert.IsTrue(float.IsFinite(t.Penetration(3, v)), $"{name}: direct armour {v}");
                    Assert.IsTrue(float.IsFinite(t.TopAttack(v, 1)), $"{name}: top pen {v}");
                    Assert.IsTrue(float.IsFinite(t.TopAttack(1, v)), $"{name}: top roof {v}");
                }
                for (var p = -2f; p <= 7f; p += 0.25f)
                    for (var a = 0; a <= ArmourLevels.Max; a++)
                    {
                        var d = t.Penetration(p, a);
                        var s = t.TopAttack(p, a);
                        Assert.IsTrue(d >= 0.08f - Eps && d <= 1.2f + Eps, $"{name}: direct {p} on {a} = {d}");
                        Assert.IsTrue(s >= 0.12f - Eps && s <= 1.15f + Eps, $"{name}: top {p} on {a} = {s}");
                    }
            }
            foreach (var w in C.Weapons.Values)
                foreach (TargetKind kind in Enum.GetValues(typeof(TargetKind)))
                    for (var a = 0; a <= ArmourLevels.Max; a++)
                    {
                        var e = C.Damage.Effective(w, a, kind);
                        Assert.IsTrue(float.IsFinite(e) && e >= 0f, $"{w.Id} on {kind} {a}: {e}");
                    }
        }

        [Test]
        public void ReplayIsDeterministic()
        {
            long Play()
            {
                var catalog = C;
                var world = new SimWorld(catalog, SandboxMaps.Flat(), 17);
                var shooters = new[] { "ifv", "light_tank", "attack_jet", "strike_drone", "heavy_bomber" }
                    .Concat(catalog.Vehicles.Values.Where(v => v.Weapon != null && v.Weapon.Id == "hellfire_standoff").Select(v => v.Id).Take(1));
                var x = -30f;
                foreach (var id in shooters) world.SpawnVehicle(id, 0, new Vector2(x += 10f, -40f), 0f);
                for (var i = 0; i < 4; i++) world.SpawnVehicle("main_battle_tank", 1, new Vector2(-15f + i * 10f, 20f), (float)Math.PI);
                long hash = 17;
                for (var i = 0; i < 60 * 20; i++)
                {
                    world.Step(TestWorlds.Step);
                    world.ClearEvents();
                    foreach (var v in world.VehicleList)
                        Assert.IsTrue(float.IsFinite(v.Hp), $"{v.Def.Id}: health stays a number");
                    if (i % 50 != 0) continue;
                    foreach (var v in world.VehicleList)
                        hash = hash * 31 + (long)(v.Position.X * 100f) * 7 + (long)(v.Position.Y * 100f) + (long)(v.Hp * 10f);
                }
                return hash;
            }
            Assert.AreEqual(Play(), Play(), "same seed, same battle");
        }

        // ------------------------------------------------------------------------------------------ 9. bosses unchanged

        /// <summary>Every boss's armour (front, side, rear, roof) and health as before the rebalance (the Unity export of 04/10).</summary>
        private static readonly (string id, int front, int side, int rear, int top, float hp)[] Bosses =
        {
            ("bastion_mk0", 4, 4, 4, 3, 8999.375f),
            ("behemoth_inferno", 4, 3, 2, 2, 11500.5f),
            ("mega_gunship", 2, 2, 2, 2, 14001.625f),
            ("fenrir", 4, 4, 3, 2, 14001.625f),
            ("behemoth_mk0", 3, 3, 2, 1, 15848.25f),
            ("armored_train", 4, 3, 3, 2, 17648.125f),
            ("behemoth_tempest", 4, 3, 2, 2, 17648.125f),
            ("scylla", 4, 4, 3, 2, 17648.125f),
            ("nyx", 4, 4, 3, 2, 17648.125f),
            ("locust", 1, 1, 1, 1, 21341.375f),
            ("fortress_bastion", 5, 3, 2, 3, 22015f),
            ("landing_hovercraft", 3, 2, 1, 1, 25011.25f),
            ("behemoth_mk2", 4, 3, 2, 2, 25011.25f),
            ("behemoth", 5, 3, 2, 2, 30418.9512f),
            ("earth_borer", 4, 3, 2, 2, 33660f),
            ("hydra", 4, 3, 2, 2, 38007.75f),
            ("mobile_fortress", 5, 3, 2, 2, 38522f),
            ("icarus_mk0", 4, 4, 4, 4, 44342.375f),
            ("argus", 2, 2, 2, 2, 44342.375f),
            ("theia", 4, 4, 4, 4, 44342.375f),
            ("coeus", 4, 4, 4, 4, 44342.375f),
            ("leviathan", 5, 3, 2, 2, 51765f),
            ("drone_mothership", 2, 2, 2, 2, 66149.5547f),
            ("moloch", 5, 3, 2, 2, 79781f),
            ("ixion", 4, 3, 2, 2, 83640f),
            ("nuke_train", 5, 3, 2, 2, 100470f),
            ("monster", 5, 3, 2, 3, 134373.9531f),
            ("typhon", 5, 3, 2, 2, 143337.2031f),
            ("kraken", 5, 3, 2, 2, 143337.2031f),
            ("command_airship", 2, 2, 2, 2, 174993.75f),
            ("daedalus", 3, 3, 3, 3, 204493f),
            ("silver_bug", 4, 4, 4, 4, 239972f),
            ("hyperion", 4, 4, 4, 4, 239972f),
        };

        [Test]
        public void BossArmourAndHealthAreUnchanged()
        {
            var catalog = C;
            foreach (var (id, front, side, rear, top, hp) in Bosses)
            {
                Assert.IsTrue(catalog.Vehicles.TryGetValue(id, out var def), id);
                Assert.AreEqual(new ArmourLevels(front, side, rear, top), def.Armour, $"{id}: armour");
                Assert.AreEqual(hp, def.MaxHp, 0.01f, $"{id}: health");
            }
        }
    }
}
