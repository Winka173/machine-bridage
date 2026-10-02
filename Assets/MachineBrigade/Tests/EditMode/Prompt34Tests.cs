using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

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
        public void TheAreaBonusSlowsTheSmerchAndTheBombs()
        {
            var c = C;
            // Smerch: 8 x 130 every 6.1 s (170 a second) before; 8 x 450, the cycle for 170 a second times 1.6 (core 5 -> 8 m).
            var smerch = c.Weapons["p26_jotunn_sec_jo_rockets"];
            Assert.AreEqual(450f, smerch.Damage, 1e-3f);
            Assert.AreEqual(170f / 1.6f, smerch.SustainedDps, 3f);
            // Bombs: 8 x 320 every 8.1 s (316) before; 8 x 700, the cycle times 2 (core 5 -> 10 m).
            var bombs = c.Weapons["p26_roc_main_roc_bombs"];
            Assert.AreEqual(700f, bombs.Damage, 1e-3f);
            Assert.AreEqual(316f / 2f, bombs.SustainedDps, 3f);
            // Leviathan's 155 mm/60: 600 x 3 at the old 131 a second.
            Assert.AreEqual(131f, c.Weapons["p26_leviathan_sec_lev155"].SustainedDps, 2f);
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
    }
}
