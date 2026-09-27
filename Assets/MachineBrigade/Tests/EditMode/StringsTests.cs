using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The text table is written as an indexer initialiser, which silently keeps the last of two
    /// equal keys: these checks read the sources so a repeated or missing key fails here instead.
    /// </summary>
    public class StringsTests
    {
        private static string Scripts => Path.Combine(Application.dataPath, "MachineBrigade", "Scripts");

        private static List<string> TableKeys()
        {
            var source = File.ReadAllText(Path.Combine(Scripts, "Game", "Hud", "Strings.cs"));
            return Regex.Matches(source, @"\[""([^""]+)""\]\s*=\s*\(").Select(m => m.Groups[1].Value).ToList();
        }

        [Test]
        public void NoKeyIsWrittenTwice()
        {
            var twice = TableKeys().GroupBy(k => k).Where(g => g.Count() > 1).Select(g => g.Key).ToList();
            Assert.That(twice, Is.Empty, "repeated keys: " + string.Join(", ", twice));
        }

        [Test]
        public void EveryVehicleHasANameAndARoleNote()
        {
            var missing = new List<string>();
            foreach (var id in MachineBrigade.Game.Match.MatchSettings.AllVehicles)
                foreach (var key in new[] { "unit." + id, "short." + id, "note." + id })
                    if (!MachineBrigade.Game.Hud.Strings.Has(key)) missing.Add(key);
            Assert.That(missing, Is.Empty, "missing: " + string.Join(", ", missing));
        }

        [Test]
        public void EveryLiteralKeyInTheCodeExists()
        {
            var keys = new HashSet<string>(TableKeys());
            var missing = new SortedSet<string>();
            foreach (var file in Directory.GetFiles(Scripts, "*.cs", SearchOption.AllDirectories))
            {
                var source = File.ReadAllText(file);
                foreach (Match m in Regex.Matches(source, @"Strings\.(?:Get|Format)\(""([^""]+)""\s*[,)]"))
                    if (!keys.Contains(m.Groups[1].Value))
                        missing.Add(m.Groups[1].Value + " (" + Path.GetFileName(file) + ")");
            }
            Assert.That(missing, Is.Empty, "missing keys: " + string.Join(", ", missing));
        }
    }
}
