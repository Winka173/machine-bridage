using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The full fix prompt, lane A (DECISIONS "Sửa lỗi tổng hợp L2" / "L3"): the calibre and warhead fields and the card that
    /// reads them; the boss weapons at their real cadence. Written under the owner's rule of 30/09 and not run until the
    /// test phase.
    /// </summary>
    public class FixFullTests
    {
        private static Catalog C => GameContent.LoadCatalog();

        private static readonly HashSet<string> GunFamilies = new HashSet<string>
            { "mg", "autocannon", "tank_gun", "howitzer", "mortar", "naval_gun", "grenade", "recoilless", "rocket" };

        private static readonly HashSet<string> WarheadFamilies = new HashSet<string>
            { "atgm", "aa_missile", "missile", "cruise", "cruise_missile", "ballistic", "bomb", "drone" };

        // ------------------------------------------------------------------------------------------------ L2

        [Test]
        public void EveryWeaponShowsTheCalibreOrWarheadOfItsData()
        {
            foreach (var w in C.Weapons.Values)
            {
                var fields = (w.CaliberMm > 0f ? 1 : 0) + (w.WarheadKg > 0f ? 1 : 0) + (w.PowerKw > 0f ? 1 : 0) + (w.EnergyMj > 0f ? 1 : 0);
                Assert.That(fields, Is.LessThanOrEqualTo(1), w.Id + ": one display field at most (mm and kg never mixed)");
                if (w.Family != null && GunFamilies.Contains(w.Family) && w.Size > 0f)
                    Assert.That(w.CaliberMm, Is.EqualTo(w.Size), w.Id + ": a gun's calibre is its round size");
                if (w.Family != null && WarheadFamilies.Contains(w.Family) && w.Size > 0f)
                {
                    Assert.That(w.WarheadKg, Is.GreaterThan(0f), w.Id + ": a missile, bomb or drone has its warhead");
                    Assert.That(w.CaliberMm, Is.EqualTo(0f), w.Id);
                }
                if (w.Family == "laser")
                {
                    Assert.That(w.PowerKw, Is.GreaterThan(0f), w.Id);
                    Assert.That(w.CaliberMm, Is.EqualTo(0f), w.Id);
                }
                var spec = WeaponInfo.Spec(w);
                var name = WeaponInfo.Describe(w).Name;
                if (spec.Length > 0) Assert.That(name, Does.Contain(spec), w.Id + ": the card prints the data's field");
                if (w.CaliberMm <= 0f) Assert.That(name, Does.Not.Contain(" mm"), w.Id + ": no calibre from the id's digits");
            }
        }

        [Test]
        public void MainGunOnlyOnTheMainMount()
        {
            var main = Strings.Get("wpn.gun");
            foreach (var v in C.Vehicles.Values)
            {
                var lines = WeaponInfo.Of(v);
                for (var i = 1; i < lines.Count; i++)
                    Assert.That(lines[i].Name.StartsWith(main), Is.False, v.Id + " mount " + i + ": " + lines[i].Name);
            }
        }

        [Test]
        public void TheNameFixes()
        {
            var c = C;
            var bombs = UnitLines.WeaponName(c.Weapons["p26_roc_main_roc_bombs"]);
            Assert.That(bombs, Does.Contain("400 kg"));
            Assert.That(bombs, Does.Not.Contain("mm"));
            foreach (var w in c.Weapons.Values.Where(x => x.Family == "laser"))
            {
                Assert.That(UnitLines.WeaponName(w), Does.Not.Contain("mm"), w.Id);
                Assert.That(WeaponInfo.Describe(w).Name, Does.Contain("kW"), w.Id);
            }
            var behemoth = WeaponInfo.Describe(c.Weapons["p26_behemoth_main_be152"]).Name;
            Assert.That(behemoth, Does.Contain("152 mm"));
            Assert.That(behemoth, Does.Not.Contain("26 mm"));
            Assert.That(c.Weapons["heli_atgm"].WarheadKg, Is.EqualTo(9f), "a Hellfire's warhead, not the missile's 49 kg");
        }

        // ------------------------------------------------------------------------------------------------ L3

        /// <summary>A barrel's time for one round: the cycle times the barrels the rounds come out of, over the rounds.</summary>
        private static float PerBarrel(WeaponDef w) => w.CycleSeconds * w.RoundsPerPull / System.Math.Max(1, w.RoundsPerCycle);

        [TestCase("p26_behemoth_main_be152", 8.9f)]
        [TestCase("p26_behemoth_direct_be120", 7.4f)]
        [TestCase("p26_moloch_main_mo120", 7.4f)]
        [TestCase("p26_ixion_125", 7.4f)]
        [TestCase("p26_jotunn_direct_jo125", 7.4f)]
        [TestCase("p26_jotunn_jo203", 23.9f)]
        [TestCase("p26_bastion_sec_b240", 59.9f)]
        [TestCase("p26_bastion_main_b155", 14.9f)]
        [TestCase("p26_nemesis_main_ne152", 7.4f)]
        [TestCase("p26_roc_roc105", 5.9f)]
        public void TheBigBossGunsFireAtTheirRealCadence(string id, float seconds)
        {
            var w = C.Weapons[id];
            Assert.That(PerBarrel(w), Is.GreaterThanOrEqualTo(seconds), id + ": a barrel's round no faster than the real gun's");
            Assert.That(PerBarrel(w), Is.LessThanOrEqualTo(seconds * 1.2f), id + ": and not much slower");
        }

        [Test]
        public void NoBossGunOf120MmAndUpFiresFasterThanReal()
        {
            // The real gap at the maximum rate (7.5 s for 120-155 mm, 24 s for 203 mm, 60 s for 240 mm) x 0.6 / 0.7: the
            // audit's TOO FAST, with the game's 30 % rule. Weapons a player vehicle also carries wait for the owner.
            var c = C;
            var players = new HashSet<string>();
            foreach (var v in c.Vehicles.Values.Where(v => !v.Boss))
                foreach (var m in v.Mounts)
                    players.Add(m.Weapon.Id);
            var floor = new Dictionary<string, float>
            {
                ["cal_120_he"] = 7.5f, ["cal_120_ap"] = 7.5f, ["cal_125_ap"] = 7.5f, ["cal_152_155"] = 7.5f, ["cal_203"] = 24f, ["cal_240"] = 60f,
            };
            foreach (var boss in c.Vehicles.Values.Where(v => v.Boss))
                foreach (var m in boss.Mounts)
                {
                    var w = m.Weapon;
                    if (w.Laid || players.Contains(w.Id) || w.WeaponFamilyId == null || !floor.TryGetValue(w.WeaponFamilyId, out var gap)) continue;
                    if (w.WeaponFamilyId == "cal_152_155" && w.WeaponVariantId != null) continue;
                    Assert.That(PerBarrel(w), Is.GreaterThanOrEqualTo(gap * 0.6f / 0.7f - 0.01f), boss.Id + ": " + w.Id);
                }
        }

        [Test]
        public void TheMakeUpBarrelsFireTogether()
        {
            var c = C;
            foreach (var id in new[] { "p26_behemoth_main_be152", "p26_behemoth_direct_be120", "p26_moloch_main_mo120", "p26_moloch_direct_mo120ap",
                                       "p26_typhon_sec_ty57", "p26_daedalus_sec_dae57", "p26_bastion_direct_b100" })
            {
                var w = c.Weapons[id];
                Assert.That(w.Simultaneous, Is.True, id);
                Assert.That(w.Barrels, Is.EqualTo(2), id);
            }
            // A full BM-21 pack: 40 tubes, 0.5 s apart.
            foreach (var id in new[] { "p26_behemoth_sec_be_rockets", "p26_nemesis_sec_boss_rockets" })
            {
                Assert.That(c.Weapons[id].Burst, Is.EqualTo(40), id);
                Assert.That(c.Weapons[id].BurstInterval, Is.EqualTo(0.5f).Within(1e-3f), id);
            }
        }

        [Test]
        public void TheCardShowsTheFullCycle()
        {
            Assert.That(Strings.Get("detail.weaponLineSalvo"), Is.Not.EqualTo("detail.weaponLineSalvo"));
            Assert.That(Strings.Get("detail.sustained"), Is.Not.EqualTo("detail.sustained"));
            var behemoth = C.Vehicle("behemoth");
            var main = behemoth.Mounts[0].Weapon;
            var facts = MenuScreen.WeaponFacts(behemoth, main);
            Assert.That(facts, Does.Contain(Strings.Format("detail.barrels", ("count", 2))));
            Assert.That(main.CycleSeconds, Is.EqualTo(8.98f).Within(1e-3f));
        }
    }
}
