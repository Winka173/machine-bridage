using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 15 D-E, kept to two tests (the owner's token rule): every weapon form, armour level and damage type has
    /// an icon and no two icons of the game share their path data; and the enemy tooltip's ✓ ~ ✕ follow the real
    /// multipliers.
    /// </summary>
    public class CombatIconTests
    {
        [SetUp]
        public void TestProfile() => PlayerProfile.LoadForTests("{}");

        [TearDown]
        public void RestoreProfile() => PlayerProfile.Load();

        [Test]
        public void EveryFormLevelAndTypeHasAnIconAndNoTwoIconsAreAlike()
        {
            var catalog = GameContent.LoadCatalog();
            var needed = new Dictionary<string, string>();
            // Every form and damage type of the sim's enums (the icons' names follow them).
            foreach (WeaponForm form in System.Enum.GetValues(typeof(WeaponForm)))
                if (form != WeaponForm.None) needed["form " + form] = CombatIcons.Form(form.ToString());
            foreach (DamageType type in System.Enum.GetValues(typeof(DamageType)))
                Assert.IsTrue(CombatIcons.Types.ContainsKey(type.ToString()), "no mark entry for " + type);
            foreach (ArmourKind kind in System.Enum.GetValues(typeof(ArmourKind)))
                for (var level = 0; level < CombatFacts.Levels; level++)
                    needed[$"armour {kind} {level}"] = CombatIcons.Armour(level, kind);
            foreach (var (type, mark) in CombatIcons.Types)
                if (type != "Kinetic") needed["type " + type] = mark;
            needed["thermobaric"] = CombatIcons.Thermobaric;
            needed["top attack"] = CombatIcons.TopAttack;
            needed["guided"] = CombatIcons.Guided;
            needed["splash"] = CombatIcons.Splash;
            foreach (Verdict v in System.Enum.GetValues(typeof(Verdict))) needed["verdict " + v] = CombatIcons.Verdict(v);

            // Every weapon of the roster that does damage reads as a form with an icon, and a damage type the marks know.
            foreach (var weapon in catalog.Vehicles.Values.SelectMany(CombatFacts.Weapons))
            {
                Assert.IsNotNull(CombatIcons.Form(weapon.Form), $"{weapon.Id}: form {weapon.Form} has no icon");
                Assert.IsTrue(CombatIcons.Types.ContainsKey(weapon.Damage), $"{weapon.Id}: damage type {weapon.Damage} has no mark entry");
            }

            var missing = needed.Where(n => n.Value == null || !Icons.Exists(n.Value)).Select(n => n.Key).ToList();
            Assert.IsEmpty(missing, "without an icon: " + string.Join(", ", missing));
            Assert.AreEqual(needed.Count, needed.Values.Distinct().Count(), "two meanings share one icon");

            // No two icons of the whole game (the kit's, the vehicles', the towers', the combat set) have the same path data.
            var byShape = new Dictionary<string, string>();
            var twins = new List<string>();
            foreach (var name in Icons.Names)
            {
                var shape = Normalise(Icons.Source(name));
                if (byShape.TryGetValue(shape, out var other)) twins.Add(other + " = " + name);
                else byShape[shape] = name;
            }
            var combatTwins = twins.Where(t => needed.Values.Any(n => t.Contains(n))).ToList();
            Assert.IsEmpty(combatTwins, "icons with the same shape: " + string.Join(", ", combatTwins));
        }

        private static string Normalise(string svg) => string.Concat(svg.Where(c => !char.IsWhiteSpace(c)));

        [Test]
        public void TheEnemyTooltipsMarksFollowTheRealMultipliers()
        {
            var catalog = GameContent.LoadCatalog();
            var deck = new[] { "scout_jeep", "light_tank", "main_battle_tank", "tank_destroyer", "aa_vehicle", "artillery", "fpv_carrier", "flame_tank", "attack_jet" }
                .Select(id => catalog.Vehicles[id]).ToList();
            var enemies = new[] { "scout_jeep", "light_tank", "main_battle_tank", "heavy_tank", "attack_helicopter", "attack_jet", "gun_turret", "headquarters" }
                .Where(catalog.Vehicles.ContainsKey).Select(id => catalog.Vehicles[id]).ToList();
            Assert.GreaterOrEqual(enemies.Count, 6);
            var seen = new HashSet<Verdict>();
            foreach (var enemy in enemies)
            {
                var tip = KitCombat.EnemyTip(enemy, deck);
                var marks = tip.Query<IconElement>(className: "fc-verdict").ToList();
                Assert.AreEqual(deck.Count, marks.Count, enemy.Id + ": one mark per deck vehicle");
                for (var i = 0; i < deck.Count; i++)
                {
                    // The sim's own verdict and multiplier: the main weapon against the enemy's front (or roof for rounds from above).
                    var m = Matchup.Against(catalog.Damage, deck[i].Weapon, enemy, deck[i].Flying && deck[i].FixedWing);
                    var expected = (Verdict)(int)Matchup.Verdict(catalog.Damage, deck[i], enemy);
                    Assert.AreEqual(expected, m >= Matchup.GoodAt ? Verdict.Good : m >= Matchup.PoorAt ? Verdict.Poor : Verdict.None, "thresholds");
                    seen.Add(expected);
                    Assert.AreEqual(CombatIcons.Verdict(expected), marks[i].Name, $"{deck[i].Id} against {enemy.Id} (x{m:0.###})");
                }
            }
            Assert.AreEqual(3, seen.Count, "the sample shows all three marks");
        }
    }
}
