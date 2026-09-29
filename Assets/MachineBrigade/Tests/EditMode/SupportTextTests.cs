using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The balance pass after prompt 18 (C.3, C.4): a support card's texts agree with its data. Their numbers
    /// are placeholders filled from the data (<see cref="SupportLines"/>); a number still written by hand,
    /// in digits or in words ("fourteen", "mười bốn"), before a count, a distance, a time, CP or a share, must
    /// be one of the support's own. And no support shows a raw key as its name.
    /// </summary>
    public class SupportTextTests
    {
        private static IEnumerable<string> Keys(string id)
        {
            yield return "guide." + id;
            yield return "support." + id + ".info";
        }

        private static (string en, string vi)? Raw(string key)
        {
            if (Strings.Texts.TryGetValue(key, out var p)) return p;
            if (GuideText.Table.TryGetValue(key, out p)) return p;
            return null;
        }

        [Test]
        public void EveryPlaceholderIsFilledAndBothLanguagesUseTheSameOnes()
        {
            var catalog = GameContent.LoadCatalog();
            var bad = new List<string>();
            var was = Strings.Vietnamese;
            try
            {
                foreach (var id in catalog.Supports.Keys)
                    foreach (var key in Keys(id))
                    {
                        if (Raw(key) is not { } pair) continue;
                        var names = new Regex(@"\{\{(\w+)\}\}");
                        var en = names.Matches(pair.en).Select(m => m.Groups[1].Value).OrderBy(x => x).ToList();
                        var vi = names.Matches(pair.vi).Select(m => m.Groups[1].Value).OrderBy(x => x).ToList();
                        if (!en.SequenceEqual(vi)) bad.Add($"{key}: English and Vietnamese placeholders differ");
                        foreach (var n in en.Where(n => !SupportLines.Names.Contains(n))) bad.Add($"{key}: unknown placeholder {{{{{n}}}}}");
                        foreach (var vietnamese in new[] { false, true })
                        {
                            Strings.Vietnamese = vietnamese;
                            if (Strings.Get(key).Contains("{{")) bad.Add($"{key}: a placeholder is left ({(vietnamese ? "vi" : "en")})");
                        }
                    }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [Test]
        public void HandWrittenNumbersAgreeWithTheData()
        {
            var catalog = GameContent.LoadCatalog();
            var bad = new List<string>();
            foreach (var (id, s) in catalog.Supports)
            {
                var allowed = new HashSet<float>(SupportLines.Names.Select(n => SupportLines.Number(s, n)).Where(v => v.HasValue).Select(v => Round(v.Value)));
                // "two battle tanks and an IFV": how many of each vehicle a drop brings.
                foreach (var g in s.Units.GroupBy(u => u)) allowed.Add(g.Count());
                foreach (var key in Keys(id))
                {
                    if (Raw(key) is not { } pair) continue;
                    foreach (var (text, vi) in new[] { (pair.en, false), (pair.vi, true) })
                        foreach (var (value, what) in Numbers(text, vi, s.Kind is SupportKind.Repair or SupportKind.ShieldDome))
                            if (!allowed.Contains(Round(value))) bad.Add($"{key}: \"{what}\" is none of the support's numbers");
                }
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        /// <summary>The scanner reads the numbers the old texts had wrong ("fourteen bombs", "bốn mươi bom con"), so the check above would have caught them.</summary>
        [Test]
        public void TheScannerReadsNumbersInWordsAndDigits()
        {
            Assert.AreEqual(new[] { 14f, 70f, 4f }, Numbers("a neutral bomber wave lays fourteen [[bombs]] along a 70 m line, 4 s after the warning", false, false).Select(x => x.value).ToArray());
            Assert.AreEqual(new[] { 40f, 60f, 20f }, Numbers("bốn mươi [[bom con]] rải thảm một dải dài 60 m, rộng 20 m", true, false).Select(x => x.value).ToArray());
            Assert.AreEqual(new[] { 14f, 1.5f }, Numbers("mười bốn quả [[bom]], 1,5 giây", true, false).Select(x => x.value).ToArray());
            Assert.AreEqual(new[] { 12f }, Numbers("Twelve shells rain on a circle", false, false).Select(x => x.value).ToArray());
            Assert.IsEmpty(Numbers("its 105, 40 and 25 mm guns; fire burns light vehicles (125%)", false, false).ToArray());
        }

        /// <summary>The texts that caught the owner's eye: the air raid's bombs and the cluster strike's bomblets come from the data.</summary>
        [Test]
        public void TheAirRaidAndTheClusterBombsSayWhatTheyDrop()
        {
            var catalog = GameContent.LoadCatalog();
            var was = Strings.Vietnamese;
            try
            {
                Strings.Vietnamese = false;
                StringAssert.Contains($" {catalog.Supports["air_raid"].Count} [[bombs]]", Strings.Get("guide.air_raid"));
                StringAssert.Contains($" {catalog.Supports["cluster_strike"].Count} [[bomblets]]", Strings.Get("guide.cluster_strike"));
                StringAssert.StartsWith($"{catalog.Supports["cluster_strike"].Count} bomblets", Strings.Get("support.cluster_strike.info"));
                Strings.Vietnamese = true;
                StringAssert.Contains($" {catalog.Supports["air_raid"].Count} quả [[bom]]", Strings.Get("guide.air_raid"));
                StringAssert.Contains($" {catalog.Supports["cluster_strike"].Count} [[bom con]]", Strings.Get("guide.cluster_strike"));
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        /// <summary>C.4: every support in the data has a name in both languages, never its raw key (the escorts' drops, the bosses' shells).</summary>
        [Test]
        public void NoSupportShowsARawKey()
        {
            var catalog = GameContent.LoadCatalog();
            var bad = new List<string>();
            var was = Strings.Vietnamese;
            try
            {
                foreach (var id in catalog.Supports.Keys)
                    foreach (var vietnamese in new[] { false, true })
                    {
                        Strings.Vietnamese = vietnamese;
                        var name = Strings.Support(id);
                        if (name.StartsWith("support.") || name.Contains("unit.") || name.Contains("{0}")) bad.Add($"{id} ({(vietnamese ? "vi" : "en")}): \"{name}\"");
                        if (Strings.Card(id).StartsWith("support.")) bad.Add($"{id}: its card name is a raw key");
                    }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        // ------------------------------------------------------------------ numbers in a text

        private static float Round(float v) => System.MathF.Round(v * 10f) / 10f;

        private static readonly Dictionary<string, int> EnglishWords = new()
        {
            ["one"] = 1, ["two"] = 2, ["three"] = 3, ["four"] = 4, ["five"] = 5, ["six"] = 6, ["seven"] = 7, ["eight"] = 8, ["nine"] = 9, ["ten"] = 10,
            ["eleven"] = 11, ["twelve"] = 12, ["thirteen"] = 13, ["fourteen"] = 14, ["fifteen"] = 15, ["sixteen"] = 16, ["seventeen"] = 17,
            ["eighteen"] = 18, ["nineteen"] = 19, ["twenty"] = 20, ["thirty"] = 30, ["forty"] = 40, ["fifty"] = 50, ["sixty"] = 60,
        };

        private static readonly Dictionary<string, int> VietnameseDigits = new()
        {
            ["một"] = 1, ["mốt"] = 1, ["hai"] = 2, ["ba"] = 3, ["bốn"] = 4, ["tư"] = 4, ["năm"] = 5, ["lăm"] = 5, ["sáu"] = 6, ["bảy"] = 7, ["tám"] = 8, ["chín"] = 9,
        };

        // What a counted number stands before: rounds, bombs, vehicles; a distance; a time; CP; a share.
        private const string EnglishNouns = "bombs?|shells?|bomblets?|missiles?|rockets?|mines?|canisters?|vehicles?|drones?|rounds?|bombers?|towers?";
        private const string VietnameseNouns = "quả|bom|đạn|tên lửa|rốc-két|mìn|xe|drone|máy bay|tháp";
        private const string Units = @"m\b|s\b|seconds?\b|giây\b|CP\b|%";

        /// <summary>Each number (digits or words) before a counted noun, a distance, a time, CP or (for repair and shields) a share.</summary>
        internal static IEnumerable<(float value, string what)> Numbers(string text, bool vietnamese, bool shares)
        {
            text = Regex.Replace(text, @"\{\{\w+\}\}", "#");
            var words = vietnamese
                ? @"(?:(?:một|hai|ba|bốn|năm|sáu|bảy|tám|chín)\s+mươi(?:\s+(?:mốt|hai|ba|tư|bốn|lăm|năm|sáu|bảy|tám|chín))?|mười(?:\s+(?:một|hai|ba|bốn|lăm|năm|sáu|bảy|tám|chín))?|một|hai|ba|bốn|năm|sáu|bảy|tám|chín)"
                : @"(?:(?:twenty|thirty|forty|fifty|sixty)(?:-(?:one|two|three|four|five|six|seven|eight|nine))?|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|one|two|three|four|five|six|seven|eight|nine|ten)";
            var nouns = vietnamese ? VietnameseNouns : EnglishNouns;
            var pattern = $@"(?<![\w.,])(?<n>\d+(?:[.,]\d+)?|{words})\s*(?:\[\[)?\s*(?<u>{Units}|(?:{nouns})\b)";
            foreach (Match m in Regex.Matches(text, pattern, RegexOptions.IgnoreCase))
            {
                var unit = m.Groups["u"].Value;
                if (unit == "%" && !shares) continue;
                var n = m.Groups["n"].Value;
                var isDigits = char.IsDigit(n[0]);
                var value = isDigits ? float.Parse(n.Replace(',', '.'), CultureInfo.InvariantCulture) : vietnamese ? Vietnamese(n) : English(n);
                yield return (value, m.Value.Trim());
            }
        }

        private static float English(string n)
        {
            n = n.ToLowerInvariant();
            if (EnglishWords.TryGetValue(n, out var v)) return v;
            var parts = n.Split('-');
            return EnglishWords[parts[0]] + (parts.Length > 1 ? EnglishWords[parts[1]] : 0);
        }

        private static float Vietnamese(string n)
        {
            var parts = n.ToLowerInvariant().Split(new[] { ' ' }, System.StringSplitOptions.RemoveEmptyEntries);
            if (parts[0] == "mười") return 10 + (parts.Length > 1 ? VietnameseDigits[parts[1]] : 0);
            if (parts.Length >= 2 && parts[1] == "mươi") return VietnameseDigits[parts[0]] * 10 + (parts.Length > 2 ? VietnameseDigits[parts[2]] : 0);
            return VietnameseDigits[parts[0]];
        }
    }
}
