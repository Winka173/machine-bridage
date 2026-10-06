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
    /// Prompt 13 G: the generated ammunition and behaviour lines follow the data, and the hand-written
    /// notes and guides do not contradict it (a guide saying "12 bombs" when the bomber carries 9).
    /// </summary>
    public class UnitLinesTests
    {
        private static IEnumerable<VehicleDef> Described(Catalog catalog) =>
            catalog.Vehicles.Values.Where(v => !v.Boss && (v.Card || v.Elite || v.Static)).OrderBy(v => v.Id);

        [Test]
        public void TheGeneratedLinesFollowTheData()
        {
            var catalog = GameContent.LoadCatalog();
            var was = Strings.Vietnamese;
            try
            {
                foreach (var language in new[] { false, true })
                {
                    Strings.Vietnamese = language;
                    foreach (var def in Described(catalog))
                    {
                        var ammo = UnitLines.Ammo(catalog, def);
                        var behaviour = UnitLines.Behaviour(catalog, def);
                        Assert.IsNotEmpty(behaviour, def.Id + ": behaviour");
                        foreach (var line in ammo.Concat(behaviour))
                        {
                            StringAssert.DoesNotContain("ul.", line, def.Id + ": a raw key");
                            StringAssert.DoesNotContain("{", line, def.Id + ": an unfilled number");
                        }
                        var text = string.Join("\n", ammo);
                        foreach (var m in def.Mounts)
                        {
                            var w = m.Weapon;
                            if (w.Damage <= 0f) continue;
                            var load = def.LoadOf(w);
                            if (load > 0)
                            {
                                StringAssert.IsMatch(Word(load), text, def.Id + ": its stores");
                                StringAssert.Contains(((int)System.MathF.Round(def.RearmTime)).ToString(), text, def.Id + ": its rearm time");
                            }
                            else if (w.Clip > 0) StringAssert.IsMatch(Word(w.Clip * w.RoundsPerPull), text, def.Id + ": its magazine");
                            else if (w.Ammo > 0) StringAssert.IsMatch(Word(w.Ammo), text, def.Id + ": its shots");
                        }
                    }
                }
            }
            finally { Strings.Vietnamese = was; }
            // Spot checks against the balance data.
            var bomber = catalog.Vehicles["heavy_bomber"];
            Strings.Vietnamese = false;
            try
            {
                Assert.IsTrue(UnitLines.Ammo(catalog, bomber).Any(l => l.StartsWith(bomber.LoadOf(bomber.Weapon) + " bombs")), "the bomber's bombs");
                Assert.IsTrue(UnitLines.Behaviour(catalog, bomber).Any(l => l.Contains("two thirds")), "a bomber goes in with two thirds of its bombs");
                // Play-test 14: the airfield is an aura building (no landing pad): its lifts for every aircraft of its side.
                var field = catalog.Vehicles["airfield"];
                Assert.IsTrue(UnitLines.Ammo(catalog, field).Any(l => l.Contains("aircraft") && l.Contains("+10% damage")), "the airfield's damage lift");
                Assert.IsTrue(UnitLines.Ammo(catalog, field).Any(l => l.Contains("aircraft") && l.Contains("+10% speed")), "and its speed lift");
                Assert.IsTrue(UnitLines.Behaviour(catalog, catalog.Vehicles["ammo_carrier"]).Any(l => l.StartsWith("Launchers within")), "the carrier's aura");
            }
            finally { Strings.Vietnamese = was; }
        }

        /// <summary>The number as a whole word in a pattern.</summary>
        private static string Word(int n) => @"\b" + n + @"\b";

        private static readonly Regex Calibre = new(@"(\d{2,3}) ?mm");
        private static readonly Regex Count = new(@"\b(\d{1,3}) (bombs|rockets|missiles|quả bom|rốc-két|tên lửa)\b");

        /// <summary>The numbers a unit's own weapons carry: calibres, stores, magazines, shots, salvos.</summary>
        private static HashSet<int> Numbers(VehicleDef def)
        {
            var set = new HashSet<int>();
            foreach (var m in def.Mounts)
            {
                var w = m.Weapon;
                if (w.Size > 0f) set.Add((int)System.MathF.Round(w.Size));
                foreach (Match c in Calibre.Matches(w.RealName ?? "")) set.Add(int.Parse(c.Groups[1].Value));
                foreach (Match c in Regex.Matches(w.Id, @"\d{2,3}")) set.Add(int.Parse(c.Value));
                foreach (var n in new[] { def.LoadOf(w), w.Clip, w.Clip * w.RoundsPerPull, w.Ammo, w.Burst, w.RoundsPerCycle, w.Ammo * w.Burst }) if (n > 0) set.Add(n);
            }
            return set;
        }

        [Test]
        public void HandWrittenTextAgreesWithTheData()
        {
            var catalog = GameContent.LoadCatalog();
            var problems = new List<string>();
            foreach (var def in Described(catalog))
            {
                var numbers = Numbers(def);
                foreach (var key in new[] { "note." + def.Id, "guide." + def.Id })
                {
                    if (!Strings.Has(key)) continue;
                    var (en, vi) = Strings.Texts.TryGetValue(key, out var pair) ? pair : GuideText.Table[key];
                    foreach (var text in new[] { en, vi })
                    {
                        // Its own weapons only: the first paragraph (what it is and carries), not the tips about others.
                        var own = text.Split('\n')[0];
                        foreach (Match m in Calibre.Matches(own))
                            if (!numbers.Contains(int.Parse(m.Groups[1].Value))) problems.Add($"{key}: \"{m.Value}\" is none of its weapons");
                        foreach (Match m in Count.Matches(own))
                            if (!numbers.Contains(int.Parse(m.Groups[1].Value))) problems.Add($"{key}: \"{m.Value}\" is not what it carries");
                    }
                }
            }
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }
    }
}
