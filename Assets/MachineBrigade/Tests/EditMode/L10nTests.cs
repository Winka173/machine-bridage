using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine.UIElements;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 21 L, Vietnamese and English for the whole game: every key has both languages; no positional or
    /// leftover placeholder; the story's Vietnamese names are tokens of the name table; no Vietnamese in the English
    /// texts and no English in the Vietnamese ones (UiLanguageTests), but for the names of <see cref="NameText.Kept"/>;
    /// numbers and English plurals follow the language; every screen shows one language; switching the language on
    /// the menu and in a paused battle leaves no word of the old one.
    /// </summary>
    public class L10nTests
    {
        private static readonly Regex Positional = new(@"\{\d+(,[^}]*)?(:[^}]*)?\}");
        private static readonly Regex Token = new(@"\{@([a-z0-9_.]+)\}");
        private static readonly Regex Leftover = new(@"\{[A-Za-z@][^{}]*\}|\{\{|\}\}|\{\d+\}");

        /// <summary>The Vietnamese letters with marks (đ included): an English text holds none but in the kept names.</summary>
        internal static readonly Regex VietnameseLetter = new("[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]", RegexOptions.IgnoreCase);

        /// <summary>A text with every placeholder filled with 1 (a number: plurals and formats work) in the current language.</summary>
        internal static string Filled(string key)
        {
            var text = Strings.Get(key);
            var names = Strings.PlaceholderNames(text).Distinct().Select(n => (n, (object)1)).ToArray();
            return names.Length == 0 ? Strings.Fill(text, System.Array.Empty<(string, object)>(), null) : Strings.Format(key, names);
        }

        /// <summary>The kept names written with marks ("Jötunn", "Tiếng Việt", the story's Vietnamese names), taken out before the letter check.</summary>
        internal static string WithoutKeptNames(string text)
        {
            foreach (var name in NameText.Table.Values.Select(v => v.en).Concat(NameText.Kept).Concat(new[] { "Tiếng Việt" }).OrderByDescending(n => n.Length))
                text = Regex.Replace(text, Regex.Escape(name), " ", RegexOptions.IgnoreCase);
            return text;
        }

        [Test]
        public void EveryKeyHasBothLanguagesInOneTable()
        {
            var bad = new List<string>();
            foreach (var (key, en, vi, _) in Strings.Entries)
                if (string.IsNullOrWhiteSpace(en) || string.IsNullOrWhiteSpace(vi)) bad.Add(key + ": a language is empty");
            foreach (var twice in Strings.Entries.GroupBy(e => e.key).Where(g => g.Count() > 1))
                bad.Add(twice.Key + ": in " + string.Join(" and ", twice.Select(e => e.table)));
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [Test]
        public void EveryPlaceholderIsNamedAndTheSameInBothLanguages()
        {
            var bad = new List<string>();
            foreach (var (key, en, vi, _) in Strings.Entries)
            {
                if (Positional.IsMatch(en) || Positional.IsMatch(vi)) bad.Add(key + ": positional placeholder");
                var a = Strings.PlaceholderNames(en).Distinct().OrderBy(n => n);
                var b = Strings.PlaceholderNames(vi).Distinct().OrderBy(n => n);
                if (!a.SequenceEqual(b)) bad.Add($"{key}: en {{{string.Join(",", a)}}} vi {{{string.Join(",", b)}}}");
                foreach (Match m in Token.Matches(en + vi))
                {
                    var id = m.Groups[1].Value;
                    if (!Strings.Has(id.Contains('.') ? id : "name." + id)) bad.Add($"{key}: unknown name {m.Value}");
                }
            }
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(80)));
        }

        /// <summary>Every text, filled, in both languages: no placeholder, name token or brace is left.</summary>
        [Test]
        public void NoPlaceholderIsLeftOnceFilled()
        {
            var was = Strings.Vietnamese;
            var bad = new List<string>();
            try
            {
                foreach (var vietnamese in new[] { false, true })
                {
                    Strings.Vietnamese = vietnamese;
                    foreach (var key in Strings.Keys.Distinct())
                    {
                        var text = Filled(key);
                        if (Leftover.IsMatch(text)) bad.Add($"{(vietnamese ? "vi" : "en")} {key}: \"{text}\"");
                    }
                }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(80)));
        }

        [Test]
        public void NoVietnameseInTheEnglishTexts()
        {
            var was = Strings.Vietnamese;
            var bad = new List<string>();
            try
            {
                Strings.Vietnamese = false;
                foreach (var key in Strings.Keys.Distinct())
                {
                    if (key.StartsWith("name.")) continue;
                    var text = WithoutKeptNames(Filled(key));
                    var m = VietnameseLetter.Match(text);
                    if (m.Success) bad.Add($"{key}: \"{text.Substring(System.Math.Max(0, m.Index - 20), System.Math.Min(40, text.Length - System.Math.Max(0, m.Index - 20)))}\"");
                }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(80)));
        }

        /// <summary>
        /// J1: a boss keeps its name in both languages and has one translated subtitle, the same on its card and its boss
        /// bar ("Icarus · Orbital Spacecraft" / "Icarus · Phi thuyền quỹ đạo"), the English one in title case.
        /// </summary>
        [Test]
        public void EveryBossHasOneNameAndOneTranslatedSubtitle()
        {
            var small = new HashSet<string> { "a", "an", "the", "of", "and", "or", "on", "in", "to", "for" };
            var bad = new List<string>();
            var entries = Strings.Entries.GroupBy(e => e.key).ToDictionary(g => g.Key, g => g.First());
            foreach (var (key, en, vi, _) in entries.Values.Where(e => (e.key.StartsWith("boss.") || e.key.StartsWith("unit.")) && e.en.Contains(" · ")))
            {
                var e = en.Split(new[] { " · " }, System.StringSplitOptions.None);
                var v = vi.Split(new[] { " · " }, System.StringSplitOptions.None);
                if (e.Length != 2 || v.Length != 2) { bad.Add(key + ": name · subtitle"); continue; }
                if (e[0] != v[0]) bad.Add($"{key}: the name differs ({e[0]} / {v[0]})");
                if (e[1] == v[1]) bad.Add($"{key}: the subtitle is not translated ({e[1]})");
                var words = e[1].Split(' ');
                if (words.Where((w, i) => i == 0 || !small.Contains(w)).Any(w => char.IsLower(w[0]))) bad.Add($"{key}: \"{e[1]}\" is not in title case");
                if (key.StartsWith("boss.") && entries.TryGetValue("unit." + key.Substring(5), out var unit) && unit.en.Contains(" · ") && (unit.en != en || unit.vi != vi))
                    bad.Add($"{key}: differs from its unit name ({unit.en} / {en})");
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        // ------------------------------------------------------------------ numbers and plurals (I.4, I.5)

        [Test]
        public void NumbersFollowTheLanguage()
        {
            var was = Strings.Vietnamese;
            try
            {
                Strings.Vietnamese = true;
                Assert.AreEqual("184.172", Strings.Num(184172));
                Assert.AreEqual("0,75", Strings.Num(0.75f));
                Assert.AreEqual("1.234,5", Strings.Num(1234.5f, "#,0.#"));
                Assert.AreEqual("184.172 xu · 0,75 m", Strings.Fill("{coins} xu · {range} m", new (string, object)[] { ("coins", 184172), ("range", 0.75f) }, null));
                Assert.AreEqual("12,5 giây", Strings.Fill("{seconds:0.0} giây", new (string, object)[] { ("seconds", 12.5f) }, null));
                Assert.AreEqual("12.450", Kit.Count(12450));
                Strings.Vietnamese = false;
                Assert.AreEqual("184,172", Strings.Num(184172));
                Assert.AreEqual("0.75", Strings.Num(0.75f));
                Assert.AreEqual("1,234.5", Strings.Num(1234.5f, "#,0.#"));
                Assert.AreEqual("184,172 coins · 0.75 m", Strings.Fill("{coins} coins · {range} m", new (string, object)[] { ("coins", 184172), ("range", 0.75f) }, null));
                Assert.AreEqual("12,450", Kit.Count(12450));
                // A text formatted from a key, as the screens do.
                Assert.AreEqual("12,450 coins", Strings.Format("loot.coins", 12450));
                Strings.Vietnamese = true;
                Assert.AreEqual("12.450 xu", Strings.Format("loot.coins", 12450));
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        [Test]
        public void EnglishPluralsAreRight()
        {
            (string, object)[] N(object v) => new (string, object)[] { ("count", v) };
            const string text = "{count|# tank|# tanks}";
            Assert.AreEqual("1 tank", Strings.Fill(text, N(1), null));
            Assert.AreEqual("2 tanks", Strings.Fill(text, N(2), null));
            Assert.AreEqual("0 tanks", Strings.Fill(text, N(0), null));
            Assert.AreEqual("1 tank", Strings.Fill(text, N("1"), null));
            Assert.AreEqual("1,500 tanks", WithEnglish(() => Strings.Fill(text, N(1500), null)));
            Assert.AreEqual("{count|# tank|# tanks}", Strings.Fill(text, new (string, object)[0], null), "an unknown name stays for the checks");
            var was = Strings.Vietnamese;
            try
            {
                Strings.Vietnamese = false;
                Assert.AreEqual("Destroy 1 boss", Strings.Format("daily.bosses", 1));
                Assert.AreEqual("Destroy 3 bosses", Strings.Format("daily.bosses", 3));
                Assert.AreEqual("1 coin", Strings.Format("loot.coins", 1));
                Strings.Vietnamese = true;
                Assert.AreEqual(Strings.Format("daily.bosses", 3).Replace("3", "1"), Strings.Format("daily.bosses", 1), "Vietnamese has no plural");
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        /// <summary>An English count followed by a plural noun uses the plural form, so "1 coins" never shows.</summary>
        [Test]
        public void EnglishCountsUseThePluralForm()
        {
            var nouns = new Regex(@"(?<!/)\{(count|coins|prints|kills|stars|merges|rolls|universal|minis|mains|utility)(:[^}|]*)?\} ((?:[a-z]+ ){0,2}?)(coins|blueprints|vehicles|bosses|rounds|battles|merges|charges|drones|bomblets|blocks|crates|rolls|blasts|mines|supports|buildings|objectives|units|items|stars|shots|salvos|missions|towers|kills)\b");
            var bad = Strings.Entries.Where(e => nouns.IsMatch(e.en)).Select(e => e.key + ": " + nouns.Match(e.en).Value).ToList();
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        private static string WithEnglish(System.Func<string> f)
        {
            var was = Strings.Vietnamese;
            try
            {
                Strings.Vietnamese = false;
                return f();
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        [Test]
        public void TheDefaultFollowsTheDevice()
        {
            var was = MatchSettings.Language;
            var vi = Strings.Vietnamese;
            try
            {
                MatchSettings.Language = LanguageChoice.Auto;
                MatchSettings.ApplyLanguage();
                Assert.AreEqual(Strings.DeviceIsVietnamese, Strings.Vietnamese);
                MatchSettings.Language = LanguageChoice.English;
                MatchSettings.ApplyLanguage();
                Assert.IsFalse(Strings.Vietnamese);
                MatchSettings.Language = LanguageChoice.Vietnamese;
                MatchSettings.ApplyLanguage();
                Assert.IsTrue(Strings.Vietnamese);
            }
            finally
            {
                MatchSettings.Language = was;
                Strings.Vietnamese = vi;
            }
        }

        [Test]
        public void RelabelTurnsOldTextsIntoNewOnes()
        {
            var was = Strings.Vietnamese;
            try
            {
                Strings.Vietnamese = false;
                var root = new VisualElement();
                var plain = new Label(Strings.Get("pause.resume"));
                var caps = new Label(Kit.Caps(Strings.Get("pause.title")));
                var filled = new Label(Strings.Format("toast.wave", 3));
                var joined = new Label(Strings.Get("map.ashfield") + "  ·  " + Strings.Get("map.dunebreak"));
                var number = new Label(Strings.Format("loot.coins", 12450));
                var other = new Label("Wolff 7");
                foreach (var l in new[] { plain, caps, filled, joined, number, other }) root.Add(l);
                Strings.Vietnamese = true;
                Relabel.Apply(root, false);
                Assert.AreEqual(Strings.Get("pause.resume"), plain.text);
                Assert.AreEqual(Kit.Caps(Strings.Get("pause.title")), caps.text);
                Assert.AreEqual(Strings.Format("toast.wave", 3), filled.text);
                Assert.AreEqual(Strings.Get("map.ashfield") + "  ·  " + Strings.Get("map.dunebreak"), joined.text);
                Assert.AreEqual(Strings.Format("loot.coins", 12450), number.text);
                Assert.AreEqual("Wolff 7", other.text);
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        // ------------------------------------------------------------------ screens (H2, L)

#if MB_UI_TEST_FRAMEWORK
        /// <summary>Every menu and battle screen, with the demo profile, shows one language: no English word on a Vietnamese screen, no Vietnamese letter on an English one.</summary>
        [Test]
        public void EveryScreenShowsOneLanguage()
        {
            var catalog = GameContent.LoadCatalog();
            var was = Strings.Vietnamese;
            var bad = new List<string>();
            DemoProfile.Use();
            try
            {
                foreach (var vietnamese in new[] { true, false })
                {
                    Strings.Vietnamese = vietnamese;
                    foreach (var screen in MenuScreen.ScreenNames)
                        bad.AddRange(MixedWords(MachineBrigade.Editor.UiShots.BuildMenu(catalog, screen, out _), $"{(vietnamese ? "vi" : "en")} screen-{screen}"));
                    foreach (var screen in MachineBrigade.Editor.UiShots.BattleScreenNames)
                        bad.AddRange(MixedWords(MachineBrigade.Editor.UiShots.BuildBattle(catalog, screen, out _), $"{(vietnamese ? "vi" : "en")} battle-{screen}"));
                }
            }
            finally
            {
                Strings.Vietnamese = was;
                DemoProfile.Restore();
            }
            Assert.IsEmpty(bad, string.Join("\n", bad.Distinct().Take(120)));
        }

        /// <summary>The screenshot set of both languages (UiShots -mbShotsSet l10n) names real screens.</summary>
        [Test]
        public void TheLanguageShotsNameRealScreens()
        {
            CollectionAssert.IsSubsetOf(MachineBrigade.Editor.UiShots.LanguageMenuScreens, MenuScreen.ScreenNames);
            CollectionAssert.IsSubsetOf(MachineBrigade.Editor.UiShots.LanguageBattleScreens, MachineBrigade.Editor.UiShots.BattleScreenNames);
            Assert.AreEqual(2 * (MachineBrigade.Editor.UiShots.LanguageMenuScreens.Length + MachineBrigade.Editor.UiShots.LanguageBattleScreens.Length),
                MachineBrigade.Editor.UiShots.LanguageScreens().Count(), "every screen in both languages");
        }

        /// <summary>The words of the other language on a screen (texts and tooltips).</summary>
        internal static List<string> MixedWords(VisualElement root, string where)
        {
            var allowed = UiLanguageTests.AllowedNames();
            var bad = new List<string>();
            void Check(string text, string what)
            {
                if (string.IsNullOrWhiteSpace(text)) return;
                var plain = Regex.Replace(text, "<[^>]+>", " ");
                if (Strings.Vietnamese)
                {
                    var english = UiLanguageTests.EnglishIn(plain, allowed);
                    if (english.Count > 0) bad.Add($"{where}: {what}\"{Short(plain)}\" ({string.Join(", ", english.Distinct())})");
                }
                else if (VietnameseLetter.IsMatch(WithoutKeptNames(plain))) bad.Add($"{where}: {what}\"{Short(plain)}\"");
            }
            root.Query<VisualElement>().ForEach(e =>
            {
                if (Hidden(e)) return;
                if (e is TextElement t) Check(t.text, "");
                Check(e.tooltip, "tooltip ");
            });
            return bad;
        }

        /// <summary>Hidden by its own or a parent's inline style (the screens are scanned without a layout).</summary>
        private static bool Hidden(VisualElement e)
        {
            for (var v = e; v != null; v = v.hierarchy.parent)
                if (v.style.display == DisplayStyle.None || v.style.visibility == Visibility.Hidden) return true;
            return false;
        }

        private static string Short(string s) => s.Length > 90 ? s.Substring(0, 90) + "…" : s;
#endif
    }
}
