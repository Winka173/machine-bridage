#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    public sealed partial class Catalog
    {
        /// <summary>Prompt 34 L1: balance.json "weaponFamilyTable" by id (empty when the data has none).</summary>
        public IReadOnlyDictionary<string, WeaponFamilyInfo> WeaponFamilyTable { get; internal set; } = new Dictionary<string, WeaponFamilyInfo>();

        /// <summary>Prompt 34 L1: the family table (written by Tools/balance/p34_families.py).</summary>
        private static Dictionary<string, WeaponFamilyInfo> ParseFamilyTable(JsonObject root)
        {
            var table = new Dictionary<string, WeaponFamilyInfo>();
            if (!root.Has("weaponFamilyTable")) return table;
            foreach (var f in root.Array("weaponFamilyTable"))
            {
                var info = new WeaponFamilyInfo(f.String("id"), f.OptionalString("name") ?? f.String("id"), f.Int("tier", 0));
                if (f.Has("variants"))
                {
                    var variants = new Dictionary<string, string>();
                    var o = f.Object("variants");
                    foreach (var k in o.Keys) variants[k] = o.String(k);
                    info.Variants = variants;
                }
                if (f.Has("boss"))
                {
                    var b = f.Object("boss");
                    info.BossDamage = b.Float("damage");
                    info.BossCore = b.Float("core", 0f);
                    info.BossEdge = b.Float("edge", 0f);
                }
                if (!table.TryAdd(info.Id, info)) throw new FormatException($"{f.Path}: duplicate weapon family '{info.Id}'.");
            }
            return table;
        }

        /// <summary>Prompt 34 L1: a weapon's family and variant ("" or absent: none).</summary>
        private static void ParseWeaponP34(JsonObject w, WeaponDef def)
        {
            def.WeaponFamilyId = w.OptionalString("weaponFamilyId");
            def.WeaponVariantId = w.OptionalString("weaponVariantId");
            // Prompt 34 L4: the barrels and whether they fire together.
            def.Barrels = Math.Max(1, w.Int("barrels", 1));
            var mode = w.OptionalString("salvoMode") ?? "RIPPLE";
            def.Simultaneous = mode switch
            {
                "SIMULTANEOUS" => true,
                "RIPPLE" => false,
                _ => throw new FormatException($"{w.Path}.salvoMode: SIMULTANEOUS or RIPPLE, not '{mode}'."),
            };
            // Barrels pass (owner 06/10): a magazine gun may fire its barrels together; its "clip" then counts volleys.
        }

        /// <summary>
        /// Prompt 34 L1: every family a weapon names is in the table, every variant is one its family lists (with its reason),
        /// and the weapon takes the family's tier.
        /// </summary>
        private static void ApplyFamilyTable(Dictionary<string, WeaponFamilyInfo> table, Dictionary<string, WeaponDef> weapons)
        {
            if (table.Count == 0) return;
            foreach (var def in weapons.Values)
            {
                if (def.WeaponFamilyId == null)
                {
                    if (def.WeaponVariantId != null) throw new FormatException($"weapon '{def.Id}': a weaponVariantId without a weaponFamilyId.");
                    continue;
                }
                if (!table.TryGetValue(def.WeaponFamilyId, out var family))
                    throw new FormatException($"weapon '{def.Id}'.weaponFamilyId: unknown family '{def.WeaponFamilyId}'.");
                if (def.WeaponVariantId != null && !family.Variants.ContainsKey(def.WeaponVariantId))
                    throw new FormatException($"weapon '{def.Id}'.weaponVariantId: '{def.WeaponVariantId}' is not a variant of '{family.Id}' (list it with its reason).");
                def.Tier = family.Tier;
            }
        }
    }
}
