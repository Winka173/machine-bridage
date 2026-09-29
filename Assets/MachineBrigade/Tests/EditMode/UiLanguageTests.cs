using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Field Command 2.0, words and letters: no English left in the Vietnamese texts except the
    /// proper names listed in Docs/DECISIONS.md (section 10); the bundled Barlow fonts carry every
    /// Vietnamese letter and every character of the kit's texts; every font ships with its licence.
    /// Every text is checked strictly (the kit's and, since the screen rebuild, the rest of the game's).
    /// </summary>
    public class UiLanguageTests
    {
        private const string KitPrefix = "kit.";

        /// <summary>
        /// The names allowed in the Vietnamese texts (prompt 21 L): the kept names of <see cref="NameText.Kept"/>, the
        /// story's names of <see cref="NameText.Table"/>, and the language names on the language switch.
        /// </summary>
        internal static HashSet<string> AllowedNames()
        {
            var names = new HashSet<string>(System.StringComparer.OrdinalIgnoreCase) { "English" };
            foreach (var name in NameText.Kept.Concat(NameText.Table.Values.Select(v => v.en)))
                foreach (var word in Regex.Split(name, @"[^A-Za-z]+"))
                    if (word.Length > 0) names.Add(word);
            return names;
        }

        // A Vietnamese syllable written without marks: onset, vowels, coda. English words mostly fail it.
        private static readonly Regex VietnameseSyllable = new(@"^(ngh|ng|nh|ch|gh|gi|kh|ph|qu|th|tr|[bcdghklmnpqrstvx])?[aeiouy]{1,3}(ch|ng|nh|[cmnpt])?$");

        // English words that happen to fit the pattern.
        private static readonly HashSet<string> EnglishLookalikes = new() { "coin", "coins", "gem", "gems", "top", "hit", "boss", "pin", "man", "map", "set", "mod", "pro" };

        /// <summary>The English words of a Vietnamese text: unmarked Latin words that are not Vietnamese syllables and not allowed names.</summary>
        internal static List<string> EnglishIn(string vi, HashSet<string> allowed)
        {
            // Data placeholders ({{count}}: a support's numbers, the balance pass after prompt 18) are not words.
            var plain = Regex.Replace(vi, @"<[^>]+>|\{\{\w+\}\}|\{[^{}]*\}|\[\[|\]\]", " ");
            var words = new List<string>();
            foreach (Match m in Regex.Matches(plain, @"\p{L}+"))
            {
                var w = m.Value;
                // Roman numerals number the acts ("Hồi IV").
                if (w.Length < 2 || w.Any(c => c > 127) || allowed.Contains(w) || Regex.IsMatch(w, "^[IVX]+$")) continue;
                var lower = w.ToLowerInvariant();
                if (EnglishLookalikes.Contains(lower) || !VietnameseSyllable.IsMatch(lower)) words.Add(w);
            }
            return words;
        }

        /// <summary>Every text of every table (prompt 21: the boss, big-attack, orbital and name tables too).</summary>
        private static IEnumerable<(string key, string en, string vi)> AllTexts() => Strings.Entries.Select(e => (e.key, e.en, e.vi));

        [Test]
        public void TheKitsVietnameseHasNoEnglish()
        {
            var allowed = AllowedNames();
            var bad = new List<string>();
            foreach (var (key, _, vi) in AllTexts().Where(t => t.key.StartsWith(KitPrefix)))
            {
                var english = EnglishIn(vi, allowed);
                if (english.Count > 0) bad.Add($"{key}: \"{vi}\" ({string.Join(", ", english)})");
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        /// <summary>
        /// Section H: every Vietnamese text of the game (the menus', the guides', the campaign's) is
        /// Vietnamese: one Vietnamese name per map, "xu" not "coin", "Ngụy trang" not "Skin", the
        /// loanwords written the Vietnamese way (rốc-két, la-de, nhà chứa); only the listed names stay.
        /// </summary>
        [Test]
        public void EveryVietnameseTextHasNoEnglish()
        {
            var allowed = AllowedNames();
            var bad = new List<string>();
            foreach (var (key, _, vi) in AllTexts().Where(t => !t.key.StartsWith(KitPrefix)))
            {
                var english = EnglishIn(vi, allowed);
                if (english.Count > 0) bad.Add($"{key}: {string.Join(", ", english)}");
            }
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(80)));
        }

        [Test]
        public void TheWordCheckFindsEnglishAndPassesVietnamese()
        {
            var allowed = new HashSet<string> { "CP" };
            CollectionAssert.AreEqual(new[] { "coin" }, EnglishIn("Nhân đôi coin", allowed));
            CollectionAssert.AreEqual(new[] { "Skin" }, EnglishIn("Skin", allowed));
            Assert.IsEmpty(EnglishIn("Giá trung bình 6,4 CP · Xanh nhanh anh", allowed));
            Assert.IsEmpty(EnglishIn("<b>{0}</b> xu", allowed));
        }

        // ------------------------------------------------------------------ fonts

        private static readonly string[] KitFonts =
        {
            "Fonts/BarlowCondensed-SemiBold", "Fonts/BarlowCondensed-Bold", "Fonts/Barlow-Regular", "Fonts/Barlow-Medium", "Fonts/Barlow-SemiBold",
        };

        private static IEnumerable<char> VietnameseLetters()
        {
            const string bases = "aăâeêioôơuưyAĂÂEÊIOÔƠUƯY";
            var tones = new[] { "", "̀", "́", "̃", "̉", "̣" };
            foreach (var b in bases)
                foreach (var t in tones)
                {
                    var s = (b + t).Normalize(NormalizationForm.FormC);
                    if (s.Length == 1) yield return s[0];
                }
            yield return 'đ';
            yield return 'Đ';
        }

        private static List<string> Missing(Font font, IEnumerable<char> chars) =>
            chars.Where(c => !char.IsWhiteSpace(c) && !char.IsControl(c)).Distinct().Where(c => !font.HasCharacter(c)).Select(c => $"U+{(int)c:X4} '{c}'").ToList();

        [Test]
        public void TheKitFontsCarryEveryVietnameseLetterAndEveryKitCharacter()
        {
            var kitChars = AllTexts().Where(t => t.key.StartsWith(KitPrefix)).SelectMany(t => t.en + t.vi + t.en.ToUpper(CultureInfo.InvariantCulture) + t.vi.ToUpper(new CultureInfo("vi-VN"))).ToList();
            var bad = new List<string>();
            foreach (var path in KitFonts)
            {
                var font = Resources.Load<Font>(path);
                Assert.IsNotNull(font, path);
                var missing = Missing(font, VietnameseLetters().Concat(kitChars));
                if (missing.Count > 0) bad.Add(path + ": " + string.Join(" ", missing));
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [Test]
        public void OldTextsCharactersMissingFromTheKitFontsReport()
        {
            var chars = AllTexts().Where(t => !t.key.StartsWith(KitPrefix)).SelectMany(t => t.en + t.vi).Distinct().ToList();
            var font = Resources.Load<Font>("Fonts/Barlow-Regular");
            var missing = Missing(font, chars);
            if (missing.Count > 0) Assert.Ignore("Report only: characters in the game's texts that Barlow lacks (draw them as icons or change the text): " + string.Join(" ", missing));
        }

        /// <summary>
        /// Prompt 21 I.6: every font the game ships, at every weight, carries every Vietnamese letter in both cases, and the
        /// fonts the screens use carry every character of every text in both languages: no letter falls back to a box.
        /// </summary>
        [Test]
        public void EveryFontCarriesEveryVietnameseLetterAndEveryTextCharacter()
        {
            var folder = Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Fonts");
            var texts = AllTexts().SelectMany(t => t.en + t.vi + t.en.ToUpperInvariant() + t.vi.ToUpperInvariant())
                .Where(c => c < 0x2190 || c > 0x2BFF).Distinct().ToList();
            var bad = new List<string>();
            foreach (var file in Directory.GetFiles(folder, "*.ttf"))
            {
                var path = "Fonts/" + Path.GetFileNameWithoutExtension(file);
                var font = Resources.Load<Font>(path);
                Assert.IsNotNull(font, path);
                var missing = Missing(font, VietnameseLetters());
                if (missing.Count > 0) bad.Add(path + " (letters): " + string.Join(" ", missing));
                // The screens' fonts (Be Vietnam Pro for the text, Barlow Condensed for the titles) carry every character of the texts.
                if (path.Contains("BeVietnamPro") || path.Contains("BarlowCondensed"))
                {
                    var chars = Missing(font, texts);
                    if (chars.Count > 0) bad.Add(path + " (texts): " + string.Join(" ", chars));
                }
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [Test]
        public void EveryFontShipsWithItsLicence()
        {
            var fonts = Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Fonts");
            var licences = Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Licenses");
            var families = Directory.GetFiles(fonts, "*.ttf").Select(f => Path.GetFileNameWithoutExtension(f).Split('-')[0]).Distinct();
            foreach (var family in families)
            {
                var licence = Path.Combine(licences, "OFL-" + family + ".txt");
                Assert.IsTrue(File.Exists(licence), "licence for " + family);
                StringAssert.Contains("SIL Open Font License", File.ReadAllText(licence), family);
            }
        }
    }
}
