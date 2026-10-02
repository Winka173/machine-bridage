using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 25 F2 batch B (DECISIONS 25F2-B): the 33 "Đề xuất thêm" Thấp-priority items, stand-in models (a
    /// borrowed model, a tint; the owner's choice). One row each of the 32 built this pass (dx23, a Super Tank
    /// module choice, is not in this pass). Compact: the sheet's health and CP, its texts and its one shop unlock;
    /// no per-mechanism scene (Prompt25NewContentTests covers that style for batch A). Written under the owner's
    /// rule of 30/09 (no test runs until the test phase): not run yet.
    /// </summary>
    public class Prompt25NewContentBTests
    {
        public sealed class Row
        {
            public Row(string id, float sheetHp, int cp, bool tower)
            {
                Id = id;
                SheetHp = sheetHp;
                Cp = cp;
                Tower = tower;
            }

            public string Id;
            public float SheetHp;
            public int Cp;
            public bool Tower;

            public override string ToString() => Id;
        }

        public static readonly Row[] Rows =
        {
            new Row("aa_57mm_vehicle", 1400, 6, false),
            new Row("mine_rocket_truck", 800, 7, false),
            new Row("prop_attack_plane", 900, 7, false),
            new Row("light_attack_heli", 1100, 7, false),
            new Row("next_gen_tank", 2300, 9, false),
            new Row("demolition_line_vehicle", 1200, 4, false),
            new Row("combat_wreck_car", 900, 4, false),
            new Row("drone_hijack_vehicle", 900, 6, false),
            new Row("manpads_tower", 1200, 0, true),
            new Row("river_patrol_boat", 800, 5, false),
            new Row("river_gunboat", 2500, 9, false),
            new Row("coastal_ashm_vehicle", 900, 10, false),
            new Row("auto_loader_howitzer", 1600, 8, false),
            new Row("amphib_light_vehicle", 1200, 6, false),
            new Row("airborne_light_tank", 1300, 5, false),
            new Row("stealth_naval_strike", 1500, 17, false),
            new Row("twin_rotor_gunship", 3500, 14, false),
            new Row("ground_drone_carrier", 900, 5, false),
            new Row("mobile_repair_vehicle", 1300, 4, false),
            new Row("radar_support_vehicle", 900, 5, false),
            new Row("towed_at_gun", 800, 4, false),
            new Row("flare_searchlight_tower", 1000, 0, true),
            new Row("recoilless_gun_tower", 1200, 0, true),
            new Row("bunker_shelter_tower", 4000, 0, true),
            new Row("dazzler_vehicle", 900, 5, false),
            new Row("ground_cruise_missile_vehicle", 1000, 12, false),
            new Row("aerial_tanker", 2500, 8, false),
            new Row("heavy_lift_helicopter", 1800, 7, false),
            new Row("bridging_vehicle", 1500, 4, false),
            new Row("gps_jammer_vehicle", 800, 5, false),
            new Row("drone_net_tower", 800, 0, true),
            new Row("one_shot_atgm_tower", 2000, 0, true),
        };

        /// <summary>The sheet's health (data x the vehicle toughness scale) and CP, its texts, and its one unlock source.</summary>
        [TestCaseSource(nameof(Rows))]
        public void MatchesTheSheetAndHasItsTextsAndShopPrice(Row row)
        {
            var catalog = GameContent.LoadCatalog();
            Assert.IsTrue(catalog.Vehicles.TryGetValue(row.Id, out var def), row.Id);
            Assert.AreEqual(row.SheetHp, def.MaxHp, row.SheetHp * 0.02f, "the sheet's health");
            Assert.AreEqual(row.Cp, def.CpCost);
            Assert.AreEqual(row.Tower, def.Static && def.Fort != null, "a tower card sits in a base slot");
            Assert.Greater(def.ModelLength, 0f, "modelSize");
            Assert.IsNotEmpty(def.Model, "a borrowed model");
            foreach (var key in new[] { "unit.", "short.", "note.", "guide." }) Assert.IsTrue(Strings.Has(key + row.Id), key + row.Id);
            foreach (var vi in new[] { false, true })
            {
                Strings.Vietnamese = vi;
                Assert.LessOrEqual(Strings.Short(row.Id).Length, 15, "a short name on one line");
                foreach (var other in Rows)
                    if (other.Id != row.Id) Assert.AreNotEqual(Strings.Card(other.Id), Strings.Card(row.Id), "a name of its own");
            }
            Strings.Vietnamese = false;
            // Prompt 32 L1: a tower folded into another card or retired from the roster is no longer sold.
            if (!CardMerges.TowerInto.ContainsKey(row.Id) && System.Array.IndexOf(CardMerges.RetiredTowers, row.Id) < 0)
                Assert.IsTrue(Progression.IsNewContent(row.Id) && Progression.Price(row.Id, catalog) > 0, "sold in the shop");
            Assert.IsNull(Progression.UnlockMission(row.Id), "the shop is its one source");
            Assert.IsTrue(Progression.EnemyMayUse(row.Id), "the enemy may field it");
            if (!row.Tower) CollectionAssert.Contains(MatchSettings.AllVehicles, row.Id);
            else Assert.IsTrue(Icons.Exists(TowerIcons.For(row.Id)), "a structure icon");
        }
    }
}
