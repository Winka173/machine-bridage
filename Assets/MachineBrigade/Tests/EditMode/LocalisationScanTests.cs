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
    /// No raw key or unfilled placeholder reaches the player: every text has both languages with
    /// the same placeholders, every card has its name and guide entry, and every piece of
    /// equipment, module, trait and brand reads as words at every rarity, in both languages.
    /// </summary>
    public class LocalisationScanTests
    {
        private static readonly Regex Placeholder = new(@"\{\d+(:[^}]*)?\}");
        private static readonly Regex RawKey = new(@"(^|\s)[a-z][a-z0-9_]*(\.[a-z0-9_]+){1,4}(\s|$)");

        private static IEnumerable<string> Placeholders(string text) => Placeholder.Matches(text).Select(m => m.Value.Split(':')[0].TrimEnd('}') + "}").Distinct().OrderBy(x => x);

        [Test]
        public void EveryTextHasBothLanguagesWithTheSamePlaceholders()
        {
            var bad = new List<string>();
            foreach (var (key, (en, vi)) in Strings.Texts.Concat(GuideText.Table))
            {
                if (string.IsNullOrWhiteSpace(en) || string.IsNullOrWhiteSpace(vi)) bad.Add(key + ": empty");
                else if (!Placeholders(en).SequenceEqual(Placeholders(vi))) bad.Add(key + ": placeholders differ");
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [Test]
        public void EveryCardHasANameAndAGuideEntry()
        {
            var catalog = GameContent.LoadCatalog();
            var missing = new List<string>();
            foreach (var id in MatchSettings.AllVehicles)
            {
                if (!Strings.Has("unit." + id)) missing.Add("unit." + id);
                if (!Strings.Has("guide." + id)) missing.Add("guide." + id);
            }
            foreach (var id in MatchSettings.AllSupports.Concat(Progression.Items))
            {
                if (!Strings.Has("support." + id)) missing.Add("support." + id);
                if (!Strings.Has("guide." + id)) missing.Add("guide." + id);
            }
            foreach (var v in catalog.Vehicles.Values.Where(v => v.Static && v.Fort != null))
            {
                // A tower's branch is named as "tower · branch".
                var key = v.BranchOf != null ? "branch." + v.Id : "unit." + v.Id;
                if (!Strings.Has(key)) missing.Add(key);
                if (v.BranchOf != null && !Strings.Has(key + ".info")) missing.Add(key + ".info");
            }
            Assert.IsEmpty(missing, string.Join(", ", missing));
        }

        [Test]
        public void EquipmentReadsAsWordsAtEveryRarityInBothLanguages()
        {
            var was = Strings.Vietnamese;
            var bad = new List<string>();
            try
            {
                foreach (var vietnamese in new[] { false, true })
                {
                    Strings.Vietnamese = vietnamese;
                    var texts = new List<(string what, string text)>();
                    foreach (var b in GearCatalog.Bases)
                    {
                        texts.Add((b.Id, Strings.Get("gear.base." + b.Id)));
                        texts.Add((b.Id + " main", b.Implicit == StatId.Count ? GearText.BaseNote(b) : GearText.Line(b.Implicit, b.Top[b.Top.Length - 1])));
                    }
                    foreach (var m in GearCatalog.Modules)
                    {
                        texts.Add((m.Key, Strings.Get("special." + m.Key)));
                        foreach (Rarity r in new[] { Rarity.Epic, Rarity.Legendary }) texts.Add((m.Key + " " + r, GearText.ModuleEffect(m.Module, r)));
                    }
                    foreach (var t in GearCatalog.Traits)
                    {
                        texts.Add((t.Key, GearText.TraitName(t.Key)));
                        foreach (Rarity r in new[] { Rarity.Epic, Rarity.Legendary }) texts.Add((t.Key + " " + r, GearText.TraitEffect(t.At(r))));
                    }
                    for (var i = 1; i <= GearCatalog.Brands.Length; i++)
                        texts.Add(("brand " + i, GearText.BrandBonuses(GearCatalog.Brand(i))));
                    // Tower equipment: base types, the tower pools' traits and their proc words, slots, fit notes.
                    foreach (var b in GearCatalog.TowerBases)
                    {
                        texts.Add((b.Id, Strings.Get("gear.base." + b.Id)));
                        texts.Add((b.Id + " main", GearText.Line(Gear.MainStatOf(b), 0.1f)));
                        texts.Add((b.Id + " implicit", GearText.Line(b.Implicit, b.Top[b.Top.Length - 1])));
                    }
                    foreach (var t in GearCatalog.TowerTraits)
                    {
                        texts.Add((t.Key, GearText.TraitName(t.Key)));
                        texts.Add((t.Key + " proc", GearText.Proc(t.Key)));
                        foreach (Rarity r in new[] { Rarity.Epic, Rarity.Legendary }) texts.Add((t.Key + " " + r, GearText.TraitEffect(t.At(r))));
                    }
                    foreach (var slot in Gear.TowerSlots)
                    {
                        texts.Add((slot + " slot", GearText.SlotName(slot)));
                        texts.Add((slot + " tab", GearText.TowerSlotName(slot)));
                        texts.Add((slot + " name", GearText.Name(new GearItem { slot = (int)slot })));
                    }
                    foreach (var need in new[] { TowerNeed.None, TowerNeed.Armed, TowerNeed.HitsGround, TowerNeed.HitsAir, TowerNeed.Magazine, TowerNeed.Mobile })
                        texts.Add((need + " need", GearText.TowerNeedLine(need)));
                    foreach (StatId s in System.Enum.GetValues(typeof(StatId)))
                        if (s != StatId.Count) texts.Add((s.ToString(), GearText.Line(s, 0.1f)));
                    foreach (var (what, text) in texts)
                        if (string.IsNullOrWhiteSpace(text) || Placeholder.IsMatch(text) || RawKey.IsMatch(text))
                            bad.Add($"{(vietnamese ? "vi" : "en")} {what}: \"{text}\"");
                }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }
    }
}
