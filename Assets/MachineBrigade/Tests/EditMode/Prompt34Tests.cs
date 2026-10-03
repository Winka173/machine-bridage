using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 34 (DECISIONS "Prompt 34 L1" ... "L4"): weapon families and variants, the boss family table, warnings by escape
    /// time, barrels fired together. Written under the owner's rule of 30/09 and not run until the test phase.
    /// </summary>
    public class Prompt34Tests
    {
        private static Catalog C => GameContent.LoadCatalog();

        private static string RealBase(WeaponDef w) => Regex.Replace(w.RealName ?? "", @"\s*\(.*?\)", "").Trim();

        // ------------------------------------------------------------------------------------------------ L1 families

        [Test]
        public void EveryWeaponHasAFamilyFromTheTable()
        {
            var c = C;
            Assert.That(c.WeaponFamilyTable.Count, Is.GreaterThan(30));
            var missing = c.Weapons.Values.Where(w => w.WeaponFamilyId == null).Select(w => w.Id).ToList();
            Assert.That(missing, Is.Empty, "weapons without a weaponFamilyId: " + string.Join(", ", missing));
            foreach (var w in c.Weapons.Values)
            {
                Assert.That(c.WeaponFamilyTable.ContainsKey(w.WeaponFamilyId), Is.True, w.Id);
                Assert.That(w.Tier, Is.InRange(0, 5), w.Id);
            }
        }

        [Test]
        public void TheSameRealWeaponIsTheSameFamily()
        {
            var byReal = new Dictionary<string, HashSet<string>>();
            foreach (var w in C.Weapons.Values)
            {
                var real = RealBase(w);
                if (real.Length == 0) continue;
                if (!byReal.TryGetValue(real, out var set)) byReal[real] = set = new HashSet<string>();
                set.Add(w.WeaponFamilyId);
            }
            var clashes = byReal.Where(p => p.Value.Count > 1).Select(p => p.Key + ": " + string.Join("/", p.Value)).ToList();
            Assert.That(clashes, Is.Empty, string.Join("; ", clashes));
        }

        [Test]
        public void EveryVariantHasItsReason()
        {
            var c = C;
            foreach (var w in c.Weapons.Values)
            {
                if (w.WeaponVariantId == null) continue;
                var family = c.WeaponFamilyTable[w.WeaponFamilyId];
                Assert.That(family.Variants.TryGetValue(w.WeaponVariantId, out var why), Is.True, w.Id + " / " + w.WeaponVariantId);
                Assert.That(why, Is.Not.Empty, w.Id);
            }
        }

        [Test]
        public void TableTiers()
        {
            var t = C.WeaponFamilyTable;
            Assert.That(t["cal_12_7"].Tier, Is.EqualTo(0));
            Assert.That(t["cal_30"].Tier, Is.EqualTo(1));
            Assert.That(t["cal_57"].Tier, Is.EqualTo(2));
            Assert.That(t["cal_152_155"].Tier, Is.EqualTo(3));
            Assert.That(t["rkt_grad_122"].Tier, Is.EqualTo(3));
            Assert.That(t["cal_203"].Tier, Is.EqualTo(4));
            Assert.That(t["rkt_smerch_300"].Tier, Is.EqualTo(4));
            Assert.That(t["bomb_400"].Tier, Is.EqualTo(4));
            Assert.That(t["cal_406"].Tier, Is.EqualTo(5));
            Assert.That(t["gungnir_emrg"].Tier, Is.EqualTo(5));
            Assert.That(C.Weapons["p26_gungnir_emrg"].Tier, Is.EqualTo(5));
        }

        [Test]
        public void DisplayNamesFixed()
        {
            var c = C;
            var bombs = UnitLines.WeaponName(c.Weapons["p26_roc_main_roc_bombs"]);
            Assert.That(bombs, Does.Contain("400 kg"));
            Assert.That(bombs, Does.Not.Contain(" mm"));
            foreach (var w in c.Weapons.Values.Where(w => w.Family == "laser"))
                Assert.That(UnitLines.WeaponName(w), Does.Not.Contain(" mm"), w.Id);
            Assert.That(c.Weapons["p26_jotunn_sec_jo_rockets"].Size, Is.EqualTo(300f));
        }

        // ------------------------------------------------------------------------------------------------ L2 the boss table

        /// <summary>The weapons player vehicles carry (bosses share a few; those keep their numbers).</summary>
        private static HashSet<string> PlayerWeapons(Catalog c)
        {
            var set = new HashSet<string>();
            foreach (var v in c.Vehicles.Values.Where(v => !v.Boss))
                foreach (var m in v.Mounts)
                    set.Add(m.Weapon.Id);
            return set;
        }

        [Test]
        public void TheSameFamilyFiresTheSameRoundOnEveryBoss()
        {
            var c = C;
            var players = PlayerWeapons(c);
            var gungnir = new HashSet<string>(c.Vehicle("rail_supergun").Mounts.Select(m => m.Weapon.Id));
            var seen = new Dictionary<string, (string id, float damage, float speed, float core, float edge, DamageType type)>();
            foreach (var boss in c.Vehicles.Values.Where(v => v.Boss))
                foreach (var m in boss.Mounts)
                {
                    var w = m.Weapon;
                    if (w.WeaponFamilyId == null || players.Contains(w.Id) || gungnir.Contains(w.Id) || (w.Laid && w.Id != "p26_leviathan_lev406")) continue;
                    var family = c.WeaponFamilyTable[w.WeaponFamilyId];
                    if (family.BossDamage == null) continue;
                    Assert.AreEqual(family.BossDamage.Value, w.Damage, 1e-3f, boss.Id + ": " + w.Id);
                    if (w.WeaponVariantId != null) continue;
                    Assert.AreEqual(family.BossCore, w.SplashRadius, 1e-3f, boss.Id + ": " + w.Id + " core");
                    var key = family.Id;
                    var round = (w.Id, w.Damage, w.ProjectileSpeed, w.SplashRadius, w.SplashEdge, w.DamageType);
                    if (!seen.TryGetValue(key, out var first)) seen[key] = round;
                    else
                    {
                        Assert.AreEqual(first.speed, round.Item3, 1e-3f, key + ": " + first.id + " / " + w.Id + " speed");
                        Assert.AreEqual(first.edge, round.Item5, 1e-3f, key + ": " + first.id + " / " + w.Id + " edge");
                        Assert.AreEqual(first.type, round.Item6, key + ": " + first.id + " / " + w.Id + " type");
                    }
                }
            Assert.That(seen.Count, Is.GreaterThan(10));
        }

        [Test]
        public void LeviathansTurretsFireTheir406InThreesEveryMinute()
        {
            var s = C.Vehicle("leviathan").Salvo;
            Assert.IsNotNull(s);
            Assert.AreEqual(3, s.Shells);
            Assert.AreEqual(2400f, s.Damage, 1e-3f);
            Assert.AreEqual(14f, s.Radius, 1e-3f);
            Assert.AreEqual(24f, s.Edge, 1e-3f);
            Assert.AreEqual(60f, s.Every, 1e-3f);
            Assert.AreEqual(24f, s.Blast(ExplosionTier.Huge).Edge, 1e-3f);
            // 3 turrets x 3 x 2,400 / 60 s: the 360 a second of 3 x 1,200 / 10 s kept.
            Assert.AreEqual(360f, 3 * s.Shells * s.Damage / s.Every, 1f);
        }

        [Test]
        public void TheSmerchTheBombsAndThe155AtTheirCadence()
        {
            // Full fix L3 (DECISIONS "Sửa lỗi tổng hợp L3") replaces prompt 34 L2's area bonus: the real cadence first, the DPS
            // the result. Smerch: 8 x 450, the real 3.17 s between rockets, wave 1's 15.76 s after the ripple.
            var c = C;
            var smerch = c.Weapons["p26_jotunn_sec_jo_rockets"];
            Assert.AreEqual(450f, smerch.Damage, 1e-3f);
            Assert.AreEqual(3.17f, smerch.BurstInterval, 1e-3f);
            Assert.AreEqual(8f * 450f / (15.76f + 7f * 3.17f), smerch.SustainedDps, 1f);
            // Bombs: 8 x 700, the 35.4 s cycle kept (no real rate for an airship's bay).
            var bombs = c.Weapons["p26_roc_main_roc_bombs"];
            Assert.AreEqual(700f, bombs.Damage, 1e-3f);
            Assert.AreEqual(8f * 700f / 35.44f, bombs.SustainedDps, 3f);
            // Leviathan's 155 mm/60: the triple turret, 3 x 600 every 10.5 s (wave 1).
            Assert.AreEqual(3f * 600f / 10.5f, c.Weapons["p26_leviathan_sec_lev155"].SustainedDps, 1f);
        }

        [Test]
        public void GungnirKeepsItsSuperWeapon()
        {
            var c = C;
            var gun = c.Weapons["p26_gungnir_emrg"];
            Assert.AreEqual(2000f, gun.Damage, 1e-3f);
            Assert.AreEqual(12f, gun.SplashRadius, 1e-3f);
            Assert.AreEqual(20f, gun.SplashEdge, 1e-3f);
            Assert.AreEqual(45f, c.Vehicle("rail_supergun").Bombard.Every, 1e-3f);
            Assert.AreEqual("gungnir_emrg", gun.WeaponFamilyId);
        }

        // ------------------------------------------------------------------------------------------------ L3 warnings

        [Test]
        public void TheEscapeWarningFormula()
        {
            Assert.AreEqual(0f, WeaponDef.EscapeWarning(3, "cal_152_155", 7f), 1e-4f, "T3: none");
            Assert.AreEqual(2.5f, WeaponDef.EscapeWarning(4, "cal_203", 8.5f), 1e-3f, "203 mm: the T4 floor");
            Assert.AreEqual(2.5f, WeaponDef.EscapeWarning(4, "rkt_smerch_300", 8f), 1e-3f, "Smerch: the floor");
            Assert.AreEqual(0.5f + 10f / 4.5f, WeaponDef.EscapeWarning(4, "bomb_400", 10f), 1e-3f, "400 kg: 0.5 + 10 / 4.5");
            Assert.AreEqual(0.5f + 14f / 4.5f, WeaponDef.EscapeWarning(5, "cal_406", 14f), 1e-3f, "406 mm: above its 3.5 s floor");
            Assert.AreEqual(4f, WeaponDef.EscapeWarning(5, "gungnir_emrg", 12f), 1e-3f, "a T5 super weapon: the 4 s floor");
            Assert.AreEqual(6f, WeaponDef.EscapeWarning(4, "cal_240", 40f), 1e-3f, "capped at 6 s");
        }

        [Test]
        public void EveryT4RoundABossFiresHasAWarningAndARing()
        {
            var c = C;
            var any = 0;
            foreach (var boss in c.Vehicles.Values.Where(v => v.Boss))
                foreach (var m in boss.Mounts)
                {
                    var w = m.Weapon;
                    if (w.Tier < 4 || w.Laid || w.Guided) continue;
                    any++;
                    Assert.That(w.WarnSeconds, Is.GreaterThanOrEqualTo(WeaponDef.EscapeWarning(w.Tier, w.WeaponFamilyId, w.SplashRadius) - 1e-4f), boss.Id + ": " + w.Id);
                    Assert.That(w.WarnSeconds, Is.GreaterThanOrEqualTo(2.5f), boss.Id + ": " + w.Id);
                    Assert.That(w.SplashRadius, Is.GreaterThan(0f), boss.Id + ": " + w.Id + " has a core to warn of");
                    Assert.That(w.WarnRadius, Is.GreaterThanOrEqualTo(w.SplashRadius), w.Id);
                }
            Assert.That(any, Is.GreaterThan(4));
        }

        [Test]
        public void LeviathansSalvoIsGunfireWithNoRing()
        {
            // Play-test 13 (lane C): the turrets' salvo is the guns' ordinary fire: no warning ring, the shells fly their own
            // flight (the 406 mm's speed); the big attack (leviathan_volley) keeps its warned strike.
            var c = C;
            var s = c.Vehicle("leviathan").Salvo;
            Assert.IsNull(s.Warning, "no ring on a gun salvo");
            Assert.That(c.Weapons[s.Weapon].ProjectileSpeed, Is.GreaterThan(s.Range / s.Warn), "it lands sooner than the old warning");
            Assert.That(c.BigAttacks.ContainsKey("leviathan_volley"), Is.True, "the big attack still warns");
        }

        [Test]
        public void JotunnsHowitzerShellsFlyTheirOwnFlight()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 2);
            foreach (var v in world.VehicleList) v.Hp = 0f;
            world.Step(0.05f);
            world.ClearEvents();
            var boss = world.SpawnVehicle("mobile_fortress", 1, new Vector2(60f, 60f), 0f);
            world.SpawnVehicle("heavy_tank", 0, new Vector2(60f, 20f), 0f);
            var gun = boss.Def.Mounts.Select(m => m.Weapon).First(w => w.WeaponFamilyId == "cal_203");
            var shots = 0;
            for (var t = 0f; t < 60f && shots < 2; t += 0.05f)
            {
                world.Step(0.05f);
                foreach (var e in world.Events)
                {
                    if (e.Kind != SimEventKind.WeaponFired || e.Entity != boss.Id || e.DefId != gun.Id) continue;
                    shots++;
                    // Play-test 13 (lane C): ordinary gunfire is not held for a warning: its flight is distance / shell speed.
                    Assert.That(e.Value, Is.LessThanOrEqualTo(gun.Range * 1.2f / gun.ProjectileSpeed + 0.05f), "the shell is not held for a warning");
                }
                world.ClearEvents();
            }
            Assert.That(shots, Is.GreaterThan(0), "the 203 mm fired");
        }

        // ------------------------------------------------------------------------------------------------ L4 barrels together

        [TestCase("p26_leviathan_lev406", 3)]
        [TestCase("p26_leviathan_sec_lev155", 3)]
        [TestCase("naval_130_twin", 2)]
        [TestCase("cruiser_203", 2)]
        [TestCase("gun_155_twin_ap", 2)]
        [TestCase("gun_155_twin_coastlr", 2)]
        [TestCase("bastion_gun", 2)]
        [TestCase("gun_140_twin", 2)]
        public void ShipsHeavyTurretsAndTheSuperTankFireTheirBarrelsTogether(string id, int barrels)
        {
            var w = C.Weapons[id];
            Assert.IsTrue(w.Simultaneous, id);
            Assert.AreEqual(barrels, w.Barrels, id);
            Assert.AreEqual(barrels, w.RoundsPerPull, id);
            Assert.AreEqual(1, w.Burst, id + ": one volley a pull");
            Assert.AreEqual(barrels, w.RoundsPerCycle, id);
        }

        [Test]
        public void TheVolleysKeepTheirDamageASecond()
        {
            var c = C;
            // Full fix L3: Scylla's AK-130 twin at the real 20 rpm a barrel, 2 x 380 every 3 s (4.75 s was too slow).
            Assert.AreEqual(2f * 380f / 3f, c.Weapons["naval_130_twin"].SustainedDps, 1f);
            // The heavy turret's twin 155 mm AP: 2 x 300 over 5.5 s + 0.05 s.
            Assert.AreEqual(2f * 300f / 5.55f, c.Weapons["gun_155_twin_ap"].SustainedDps, 1f);
            // A guided shell still goes one at a time.
            Assert.IsFalse(c.Weapons["gun_155_twin_fort_guided"].Simultaneous);
        }

        [Test]
        public void TheSuperTanksTwoBarrelsFireInTheSameTick()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 2);
            foreach (var v in world.VehicleList) v.Hp = 0f;
            world.Step(0.05f);
            world.ClearEvents();
            var tank = world.SpawnVehicle("titan_tank", 0, new Vector2(60f, 40f), 0f);
            world.SpawnVehicle("heavy_tank", 1, new Vector2(60f, 70f), 3.14f);
            var volleys = 0;
            for (var t = 0f; t < 30f && volleys < 2; t += 0.05f)
            {
                world.Step(0.05f);
                var main = world.Events.Count(e => e.Kind == SimEventKind.WeaponFired && e.Entity == tank.Id && e.Mount == 0);
                if (main > 0)
                {
                    Assert.AreEqual(2, main, "both barrels in one step");
                    volleys++;
                }
                world.ClearEvents();
            }
            Assert.That(volleys, Is.GreaterThan(0), "the twin 140 mm fired");
        }
    }
}
