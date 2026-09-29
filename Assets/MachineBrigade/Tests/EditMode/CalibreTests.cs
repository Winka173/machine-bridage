using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 13 B.7: damage a round follows the real weapon. Within a family it never falls as the
    /// calibre (or a missile's, bomb's or drone's weight) rises; the same real weapon hits the same on
    /// every carrier; the calibre scale's anchors hold; autocannon rounds sit between a machine gun's
    /// and a tank gun's against armour.
    /// </summary>
    public class CalibreTests
    {
        private static readonly HashSet<string> Unscaled = new() { "melee", "special" };

        [Test]
        public void DamageRisesWithCalibreWithinEveryFamily()
        {
            var catalog = GameContent.LoadCatalog();
            var failures = new List<string>();
            foreach (var family in catalog.Weapons.Values.Where(w => w.Family != null && !Unscaled.Contains(w.Family)).GroupBy(w => w.Family))
            {
                var ordered = family.OrderBy(w => w.Size).ThenBy(w => w.Damage).ToList();
                for (var i = 1; i < ordered.Count; i++)
                    if (ordered[i].Damage < ordered[i - 1].Damage - 1e-4f && ordered[i].Size > ordered[i - 1].Size)
                        failures.Add($"{family.Key}: {ordered[i].Id} ({ordered[i].Size:g}, {ordered[i].Damage:g}) hits less than {ordered[i - 1].Id} ({ordered[i - 1].Size:g}, {ordered[i - 1].Damage:g})");
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        /// <summary>The real weapon without a variant note in brackets ("2A42 30 mm (twin)" is a 2A42).</summary>
        private static string Real(WeaponDef w) => Regex.Replace(w.RealName ?? "", @"\s*\([^)]*\)", "").Trim();

        [Test]
        public void TheSameRealWeaponHitsTheSameOnEveryCarrier()
        {
            var catalog = GameContent.LoadCatalog();
            var failures = new List<string>();
            foreach (var same in catalog.Weapons.Values.Where(w => !string.IsNullOrEmpty(w.RealName) && w.Family != null && !Unscaled.Contains(w.Family))
                         .GroupBy(w => (w.Family, w.Size, Real(w))))
            {
                var damages = same.Select(w => w.Damage).Distinct().ToList();
                if (damages.Count > 1)
                    failures.Add($"{same.Key.Item3}: " + string.Join(", ", same.Select(w => $"{w.Id} {w.Damage:g}")));
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        [Test]
        public void EveryWeaponThatFiresHasAFamilyAndACalibre()
        {
            var catalog = GameContent.LoadCatalog();
            var missing = catalog.Weapons.Values.Where(w => w.Damage > 0f && (w.Family == null || w.Size <= 0f || string.IsNullOrEmpty(w.RealName))).Select(w => w.Id).ToList();
            Assert.IsEmpty(missing, string.Join(", ", missing));
        }

        /// <summary>The owner's reference scale (per round, before armour); the numbers may move but stay in these bands.</summary>
        [TestCase("mg", 7.62f, 5f, 6f)]
        [TestCase("mg", 12.7f, 9f, 10f)]
        [TestCase("autocannon", 23f, 13f, 15f)]
        [TestCase("autocannon", 25f, 16f, 18f)]
        [TestCase("autocannon", 30f, 20f, 24f)]
        [TestCase("autocannon", 35f, 24f, 26f)]
        [TestCase("autocannon", 40f, 28f, 32f)]
        [TestCase("tank_gun", 57f, 60f, 80f)]
        [TestCase("tank_gun", 105f, 180f, 220f)]
        [TestCase("tank_gun", 120f, 220f, 260f)]
        [TestCase("tank_gun", 125f, 220f, 260f)]
        [TestCase("tank_gun", 140f, 270f, 290f)]
        [TestCase("tank_gun", 152f, 300f, 340f)]
        [TestCase("howitzer", 155f, 300f, 340f)]
        [TestCase("howitzer", 203f, 400f, 1000f)]
        [TestCase("rocket", 70f, 26f, 30f)]
        [TestCase("rocket", 80f, 30f, 34f)]
        [TestCase("rocket", 122f, 55f, 60f)]
        [TestCase("rocket", 227f, 95f, 105f)]
        [TestCase("rocket", 300f, 135f, 145f)]
        [TestCase("atgm", 22.6f, 180f, 200f)]
        [TestCase("atgm", 29f, 220f, 240f)]
        [TestCase("atgm", 49f, 240f, 260f)]
        [TestCase("atgm", 300f, 330f, 360f)]
        [TestCase("bomb", 110f, 190f, 210f)]
        [TestCase("bomb", 250f, 290f, 310f)]
        [TestCase("bomb", 500f, 380f, 420f)]
        public void TheCalibreScaleHolds(string family, float size, float low, float high)
        {
            var catalog = GameContent.LoadCatalog();
            var rounds = catalog.Weapons.Values.Where(w => w.Family == family && System.Math.Abs(w.Size - size) < 0.01f).ToList();
            Assert.IsNotEmpty(rounds, $"no {family} of {size}");
            foreach (var w in rounds)
                Assert.That(w.Damage, Is.InRange(low, high), $"{w.Id}: {family} {size:g}");
        }

        [Test]
        public void AutocannonRoundsSitBetweenMachineGunsAndTankGunsOnArmour()
        {
            var catalog = GameContent.LoadCatalog();
            var cannon = catalog.Weapons["autocannon_30"];
            var mg = catalog.Weapons["hmg_roof"];
            var tank = catalog.Weapons["gun_120mm"];
            Assert.IsTrue(cannon.Autocannon, "the 30 mm is an autocannon");
            Assert.IsFalse(mg.Autocannon, "a machine gun is not");
            var onArmour = catalog.Damage.Multiplier(cannon, ArmorClass.Heavy);
            Assert.That(onArmour, Is.InRange(0.35f, 0.4f), "autocannon rounds on heavy armour");
            Assert.Greater(onArmour, catalog.Damage.Multiplier(mg, ArmorClass.Heavy));
            Assert.Less(onArmour, catalog.Damage.Multiplier(tank, ArmorClass.Heavy));
            Assert.AreEqual(1f, catalog.Damage.Multiplier(cannon, ArmorClass.Light), 1e-4f, "on light armour as any kinetic round");
        }
    }
}
