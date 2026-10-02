using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 26 C and D (DECISIONS 26CD): the era rule and the two redesigned mini bosses. The game is set from the end of the
    /// Second World War to the present and the future, so no reference, profile, Guide card, general's line or model note may name a
    /// pre-1945 design. Written under the owner's rule of 30/09 and not run until the test phase.
    /// </summary>
    public class Prompt26CDTests
    {
        private static Catalog C => GameContent.LoadCatalog();

        /// <summary>The pre-1945 designs (prompt 26 D.13 and similar): a match in any reference or description text fails the test.</summary>
        private static readonly Regex Forbidden = new(
            @"\b(?:Landkreuzer|Ratte|Maus|Schwerer Gustav|Gustav|Krupp K ?5|Tsar Tank|Lebedenko|Yamato|Musashi|Zeppelin|Hindenburg|USS Akron|USS Macon|" +
            @"Snow Cruiser|Churchill|Crocodile|Pantherturm|Maxim Gorky|Batterie Todt|Flak ?3[67]|Flak ?88|8[.,]8 ?cm|Pak ?40|Horten|Ho ?229|" +
            @"Sturmtiger|Karl-Ger|Bismarck|Tirpitz|Enola|Fat Man|Nebelwerfer)\b",
            RegexOptions.IgnoreCase | RegexOptions.CultureInvariant);

        /// <summary>
        /// The exceptions the prompt keeps (D intro): equipment built before 1945 that still serves after the war. They are cut out of a
        /// text before it is scanned, so a text may name them; they are not in <see cref="Forbidden"/> and any other pre-1945 name
        /// beside them still fails.
        /// </summary>
        private static readonly string[] Exceptions = { "Bofors 40 mm", "Bofors L/60 40 mm", "Bofors L/70 40 mm", "M2 Browning", "M2 machine gun" };

        private static string Strip(string text)
        {
            foreach (var keep in Exceptions) text = text.Replace(keep, "");
            return text;
        }

        private static string RepoFile(string relative) => Path.GetFullPath(Path.Combine(Application.dataPath, "..", relative));

        [Test]
        public void NoGameTextNamesAPre1945Design()
        {
            var bad = new List<string>();
            foreach (var (key, en, vi, table) in Strings.Entries)
            {
                if (Forbidden.IsMatch(Strip(en)) || Forbidden.IsMatch(Strip(vi))) bad.Add(table + ":" + key);
            }
            Assert.IsEmpty(bad, "pre-1945 designs in the texts: " + string.Join(", ", bad));
        }

        [Test]
        public void NoWeaponReferenceNamesAPre1945Design()
        {
            var bad = new List<string>();
            var data = File.ReadAllText(RepoFile("Assets/MachineBrigade/Resources/Data/balance.json"));
            foreach (Match m in Regex.Matches(data, "\"real\": \"([^\"]*)\""))
                if (Forbidden.IsMatch(Strip(m.Groups[1].Value))) bad.Add(m.Groups[1].Value);
            Assert.IsEmpty(bad, "pre-1945 weapons: " + string.Join(", ", bad));
        }

        [Test]
        public void NoReferenceLineShapeNoteOrTrackerNamesAPre1945Design()
        {
            var bad = new List<string>();
            foreach (var file in new[] { "Tools/docs/unit_refs.json", "Tools/docs/unit_sheet.json", "Docs/backlog/new_content.json" })
                foreach (Match m in Forbidden.Matches(Strip(File.ReadAllText(RepoFile(file)))))
                    bad.Add(file + ": " + m.Value);
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [Test]
        public void TheExceptionsAreNotInTheForbiddenList()
        {
            foreach (var keep in Exceptions)
                Assert.IsFalse(Forbidden.IsMatch(keep), keep + " is kept (the AC-130's Bofors 40 mm, the M2 machine gun)");
        }

        [Test]
        public void LeviathansMainGunIs406MillimetresWithA12m20mBlast()
        {
            var gun = C.Weapons["p26_leviathan_lev406"];
            Assert.AreEqual(406f, gun.Size, 1e-3f);
            Assert.AreEqual(12f, gun.SplashRadius, 1e-3f, "the core");
            Assert.AreEqual(20f, gun.SplashEdge, 1e-3f, "the edge");
            Assert.IsFalse(Regex.IsMatch(Strings.Get("guide.leviathan"), "460"), "no 460 mm left in its Guide card");
        }

        [Test]
        public void GungnirFiresOneElectromagneticSlugEveryTwentyFiveSecondsThroughALineAndBlastsAtTheLastHit()
        {
            var def = C.Vehicle("rail_supergun");
            var b = def.Bombard;
            Assert.IsNotNull(b);
            Assert.AreEqual("p26_gungnir_emrg", b.Weapon);
            Assert.AreEqual(25f, b.Every, 1e-3f);
            Assert.Greater(b.PierceMax, 1, "it goes through several targets");
            Assert.Greater(b.PierceDamage, 0f);
            Assert.AreEqual(BossRank.Mini, def.Rank);
            Assert.IsNull(def.BigAttack, "a mini boss has no super weapon");
        }

        [Test]
        public void IxionIsTheArmouredMineTruckOf26By12By10Metres()
        {
            var def = C.Vehicle("ixion");
            Assert.AreEqual(26f, def.ModelLength, 1e-3f);
            Assert.AreEqual(12f, def.ModelWidth, 1e-3f);
            Assert.AreEqual(10f, def.ModelHeight, 1e-3f);
            Assert.AreEqual(4f, def.Armour.Front);
            Assert.AreEqual(3f, def.Armour.Side);
            Assert.AreEqual(2f, def.Armour.Rear);
            Assert.AreEqual(2f, def.Armour.Top);
            Assert.AreEqual(7f, def.Speed, 1e-3f);
            var gun = def.Mounts[0].Weapon;
            Assert.AreEqual(780f, gun.Damage, 1e-3f);
            Assert.AreEqual(2f, gun.Cooldown, 1e-3f);
            Assert.AreEqual(1, gun.Rounds.Count, "an HE round for a crowd, the AP shell for a single target");
            Assert.AreEqual(5f, gun.Rounds[0].Round.SplashRadius, 1e-3f);
            Assert.AreEqual(10f, gun.Rounds[0].Round.SplashEdge, 1e-3f);
            Assert.AreEqual(2, def.Mounts.Count(m => m.Slot == "mg"), "two roof machine guns");
        }
    }
}
