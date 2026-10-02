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
    }
}
