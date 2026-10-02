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
    }
}
