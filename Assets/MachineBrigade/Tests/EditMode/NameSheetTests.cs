using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 25 D1: the unit names of the balance spreadsheet (sheet "Tên đề xuất", applied by
    /// Tools/balance/import_names.py, the data in <see cref="NameSheetData"/>). A unit has one name: its card, its short
    /// name and the head of its guide say the sheet's name, no two units share one, and no text of any table names a unit
    /// by its old name. A unit's own reference line (note.&lt;id&gt;) may keep the real model it is based on.
    /// </summary>
    public class NameSheetTests
    {
        /// <summary>One line of a card (LocalisationScanTests.EveryCardHasAShortName).</summary>
        private const int ShortMax = 15;

        private static Dictionary<string, (string en, string vi)> Texts()
        {
            var texts = new Dictionary<string, (string en, string vi)>();
            foreach (var (key, en, vi, _) in Strings.Entries)
                if (!texts.ContainsKey(key)) texts[key] = (en, vi);
            return texts;
        }

        private static string Head(string guide)
        {
            var m = Regex.Match(guide ?? "", @"^\[\[(.+?)\]\]");
            return m.Success ? m.Groups[1].Value : null;
        }

        [Test]
        public void EveryUnitHasTheSheetsNames()
        {
            var texts = Texts();
            var bad = new List<string>();
            foreach (var (id, en, vi, enShort, viShort) in NameSheetData.Names)
            {
                if (!texts.TryGetValue("unit." + id, out var name) || name != (en, vi))
                    bad.Add($"unit.{id}: {name} instead of ({en}, {vi})");
                if (!texts.TryGetValue("short." + id, out var shortName) || shortName != (enShort, viShort))
                    bad.Add($"short.{id}: {shortName} instead of ({enShort}, {viShort})");
                foreach (var s in new[] { enShort, viShort })
                    if (s.Length > ShortMax) bad.Add($"short.{id}: \"{s}\" is {s.Length} letters");
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [Test]
        public void NoIdHasTwoNames()
        {
            var texts = Texts();
            var bad = new List<string>();
            foreach (var (id, en, vi, _, _) in NameSheetData.Names)
                if (texts.TryGetValue("guide." + id, out var guide))
                {
                    if (Head(guide.en) != en) bad.Add($"guide.{id} opens with \"{Head(guide.en)}\", not \"{en}\"");
                    if (Head(guide.vi) != vi) bad.Add($"guide.{id} opens with \"{Head(guide.vi)}\", not \"{vi}\"");
                }
            // No two units share a name: the sheet's among themselves, and none with another card (a card merged into
            // one of them, CardMerges.Into, is the same card now and may keep the name it handed on).
            var sheetIds = new HashSet<string>(NameSheetData.Names.Select(n => n.id));
            var names = new Dictionary<string, string>();
            void Claim(string name, string key)
            {
                if (names.TryGetValue(name, out var other)) bad.Add($"\"{name}\" names {other} and {key}");
                else names[name] = key;
            }
            foreach (var (id, en, vi, enShort, viShort) in NameSheetData.Names)
            {
                Claim("en " + en, "unit." + id);
                Claim("vi " + vi, "unit." + id);
                Claim("en short " + enShort, "short." + id);
                Claim("vi short " + viShort, "short." + id);
            }
            foreach (var kv in texts)
            {
                if (!kv.Key.StartsWith("unit.")) continue;
                var id = kv.Key.Substring(5);
                if (sheetIds.Contains(id) || CardMerges.Into.ContainsKey(id)) continue;
                foreach (var name in new[] { "en " + kv.Value.en, "vi " + kv.Value.vi })
                    if (names.TryGetValue(name, out var other)) bad.Add($"\"{name.Substring(3)}\" names {other} and {kv.Key}");
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        /// <summary>
        /// No text names a unit by its old name. An old name that is only a name ("Xe phóng Lancet", "Hover gunboat") is
        /// written nowhere; one that is an everyday word too ("xe phòng không", "artillery") never as a card's name (a
        /// guide's head, or capitalised in mid-sentence); one that is the unit's short name now ("C-RAM") never at a
        /// guide's head. A current name that holds an old one ("Xe công sự triển khai") is not a hit.
        /// </summary>
        [Test]
        public void NoOldNameIsLeft()
        {
            var texts = Texts();
            var current = new HashSet<string>();
            foreach (var kv in texts)
                if (kv.Key.StartsWith("unit.") || kv.Key.StartsWith("short."))
                {
                    current.Add(kv.Value.en);
                    current.Add(kv.Value.vi);
                }
            var bad = new List<string>();
            foreach (var (id, english, old, mode) in NameSheetData.OldNames)
            {
                var own = new HashSet<string> { "unit." + id, "short." + id, "note." + id };
                var holders = current.Where(c => !string.Equals(c, old, System.StringComparison.OrdinalIgnoreCase)).ToList();
                foreach (var kv in texts)
                {
                    if (own.Contains(kv.Key)) continue;
                    var text = english ? kv.Value.en : kv.Value.vi;
                    var at = Find(text, old, mode, holders);
                    if (at >= 0)
                        bad.Add($"{kv.Key} ({(english ? "en" : "vi")}): \"{old}\" in \"…{text.Substring(System.Math.Max(0, at - 30), System.Math.Min(text.Length - System.Math.Max(0, at - 30), old.Length + 60))}…\"");
                }
            }
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(80)));
        }

        /// <summary>Where an old name is left in a text (-1: nowhere), as Tools/balance/import_names.py's scan finds it.</summary>
        internal static int Find(string text, string old, string mode, IReadOnlyCollection<string> holders)
        {
            if (string.IsNullOrEmpty(text)) return -1;
            var plural = NameSheetData.Plurals.Where(p => p.name == old).Select(p => p.plural).FirstOrDefault();
            if (text.IndexOf(old, System.StringComparison.OrdinalIgnoreCase) < 0 &&
                (plural == null || text.IndexOf(plural, System.StringComparison.OrdinalIgnoreCase) < 0)) return -1;
            var spans = new List<(int from, int to)>();
            foreach (var h in holders)
                for (var i = text.IndexOf(h, System.StringComparison.OrdinalIgnoreCase); i >= 0 && h.Length > 0;
                     i = text.IndexOf(h, i + 1, System.StringComparison.OrdinalIgnoreCase))
                    spans.Add((i, i + h.Length));
            bool Held(Match m) => spans.Any(s => s.from <= m.Index && m.Index + m.Length <= s.to);
            var next = NameSheetData.NotBefore.Where(n => n.old == old).Select(n => n.next).FirstOrDefault();
            bool RunsOn(Match m) => next != null && string.CompareOrdinal(text, m.Index + m.Length, next, 0, next.Length) == 0;

            if (mode == "any")
            {
                foreach (var name in plural == null ? new[] { old } : new[] { old, plural })
                    foreach (Match m in new Regex(@"(?<![\w-])" + Regex.Escape(name) + @"(s?)(?![\w-])", RegexOptions.IgnoreCase).Matches(text))
                        if (!Held(m) && !RunsOn(m)) return m.Index;
                return -1;
            }
            var head = text.IndexOf("[[" + old + "]]", System.StringComparison.Ordinal);
            if (head >= 0 || mode == "head") return head;
            foreach (Match m in new Regex(@"(?<![\w-])" + Regex.Escape(old) + @"(?![\w-])").Matches(text))
            {
                if (Held(m)) continue;
                var before = text.Substring(0, m.Index).TrimEnd(' ');
                if (before.Length > 0 && ".:!?\n([“\"·–—-*".IndexOf(before[before.Length - 1]) < 0 && !before.EndsWith("[[")) return m.Index;
            }
            return -1;
        }
    }
}
