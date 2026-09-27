using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Words for equipment in the menus: a piece's name (its base type or module), each stat line,
    /// its trait with its numbers, set brands and chips, and the short proc words shown in battle.
    /// Keys: gear.base.&lt;id&gt;, special.&lt;key&gt;(.info), trait.&lt;key&gt;(.info), stat.line.&lt;stat&gt;,
    /// stat.pen.&lt;stat&gt;, brand.&lt;id&gt;, proc.&lt;key&gt;.
    /// </summary>
    internal static class GearText
    {
        /// <summary>How each trait's and module's numbers are written, A then B then C: p percent, q percent with a decimal, s seconds, m metres, n a count, x a multiplier.</summary>
        private static readonly Dictionary<string, string> Formats = new()
        {
            ["ricochet_shells"] = "pm", ["cluster_warhead"] = "n", ["rapid_response"] = "xs", ["overpressure_chamber"] = "n", ["aegis_barrier"] = "ps",
            ["unbreakable"] = "s", ["dark_crown"] = "pp", ["reactive_blocks"] = "ns", ["angled_glacis"] = "n", ["siege_anchor"] = "pp", ["nitro_dash"] = "xs",
            ["shoot_and_scoot"] = "pp", ["rapid_deployment"] = "s", ["volatile_fuel_tanks"] = "pm", ["field_mechanics"] = "qm", ["ammo_carrier"] = "pm",
            ["damage_control"] = "s", ["laser_designator"] = "ps", ["ghillie_mode"] = "ps", ["counter_battery_radar"] = "pms", ["ew_jammer"] = "ssm",
            ["set_hit_and_run"] = "pp", ["set_firestorm"] = "pm", ["set_shared_shield"] = "psm", ["set_strafing_run"] = "ns", ["set_swarm"] = "s",
            ["set_salvage_rights"] = "pp", ["set_heavy_round"] = "np",
            ["auto_repair"] = "q", ["smoke_discharger"] = "m", ["trophy_aps"] = "ns", ["flare_dispenser"] = "ss", ["drone_escort"] = "ns", ["emp_payload"] = "sm",
            ["mine_dispenser"] = "ns", ["rally_horn"] = "pm", ["aegis_dome"] = "s", ["decoy_launcher"] = "ss", ["uplink_barrage"] = "ns",
        };

        private static string Number(char kind, float v) => kind switch
        {
            'q' => (v * 100f).ToString("0.0"),
            's' => v.ToString("0.#"),
            'm' or 'n' => Mathf.RoundToInt(v).ToString(),
            'x' => v.ToString("0.0#"),
            _ => Mathf.RoundToInt(v * 100f).ToString(),
        };

        private static object[] Args(string key, float a, float b, float c)
        {
            var f = Formats.TryGetValue(key, out var kinds) ? kinds : "p";
            char K(int i) => i < f.Length ? f[i] : 'p';
            return new object[] { Number(K(0), a), Number(K(1), b), Number(K(2), c) };
        }

        /// <summary>A piece's name: its base type ("Long Barrel") or module ("Trophy APS").</summary>
        public static string Name(GearItem item)
        {
            if (item.Slot == GearSlot.Special) return Strings.Get("special." + GearKeys.Module(item.Module));
            var b = Gear.BaseOf(item);
            return b != null ? Strings.Get("gear.base." + b.Id) : Strings.Get("gear.name." + item.Slot.ToString().ToLowerInvariant());
        }

        public static string SlotName(GearSlot slot) => Strings.Get("gear.slot." + slot.ToString().ToLowerInvariant());

        /// <summary>A stat line: "+8% range", "-6% speed" (a drawback), "-2 s regen delay".</summary>
        public static string Line(Gear.Line line) => Line(line.Stat, line.Value, line.Kind == Gear.LineKind.Penalty);

        public static string Line(StatId stat, float value, bool penalty = false)
        {
            var key = GearKeys.Snake(stat.ToString());
            var amount = stat switch
            {
                StatId.Regen => (Mathf.Abs(value) * 100f).ToString("0.00"),
                StatId.RegenDelay => Mathf.Abs(value).ToString("0.#"),
                _ => (Mathf.Abs(value) * 100f).ToString(Mathf.Abs(value) < 0.1f ? "0.#" : "0"),
            };
            return Strings.Format(penalty ? "stat.pen." + key : "stat.line." + key, amount);
        }

        /// <summary>A trait's name ("Ricochet Shells").</summary>
        public static string TraitName(string key) => Strings.Get("trait." + key);

        /// <summary>What a trait does, with its numbers.</summary>
        public static string TraitEffect(GearTrait t)
        {
            var key = GearKeys.Trait(t.Id);
            return Strings.Format("trait." + key + ".info", Args(key, t.A, t.B, t.C));
        }

        /// <summary>A piece's trait line: "Ricochet Shells: each hit bounces...", or empty.</summary>
        public static string TraitLine(GearItem item)
        {
            var t = Gear.TraitOf(item);
            return t.Id == TraitId.None ? "" : TraitName(GearKeys.Trait(t.Id)) + ": " + TraitEffect(t);
        }

        /// <summary>What a special module does at the piece's rarity, with its numbers.</summary>
        public static string ModuleEffect(GearItem item)
        {
            var key = GearKeys.Module(item.Module);
            var a = Gear.ModulePower(item.Module, item.Rarity);
            var b = Gear.ModulePower2(item.Module, item.Rarity);
            var text = Strings.Format("special." + key + ".info", Args(key, a, b, 0f));
            if (item.Module == SpecialModule.SmokeDischarger && b > 0f) text += " " + Strings.Get("special.smoke_discharger.again");
            return text;
        }

        public static string BrandName(BrandDef brand) => brand == null ? "" : Strings.Get("set." + brand.Id);

        /// <summary>A set chip: "Ironclad 2/4".</summary>
        public static string Chip(Gear.SetChip chip) => Strings.Format("gear.setChip", BrandName(chip.Brand), chip.Count);

        /// <summary>A brand's two bonuses: "2: +6% health · 4: Bulwark: ...".</summary>
        public static string BrandBonuses(BrandDef brand)
        {
            var four = brand.FourPiece;
            return Strings.Format("gear.brandBonuses", Line(brand.Stat, brand.Value), TraitName(GearKeys.Trait(four.Id)) + ": " + TraitEffect(four));
        }

        /// <summary>The word shown over a vehicle when its equipment goes off ("RICOCHET"), or null for none.</summary>
        public static string Proc(string key) => key != null && Strings.Has("proc." + key) ? Strings.Get("proc." + key) : null;
    }
}
