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
            ["tower_fire_link"] = "ps", ["tower_counter_battery"] = "s", ["tower_modular"] = "p", ["tower_smoke_launchers"] = "ms",
            ["tower_backup_generator"] = "p",
            ["twin_feed"] = "pp", ["vengeance"] = "pms", ["set_pack_hunt"] = "pmn", ["set_phoenix"] = "ps", ["set_bulwark_post"] = "s",
        };

        private static string Number(char kind, float v) => kind switch
        {
            'q' => Strings.Num(v * 100f, "0.0"),
            's' => Strings.Num(v, "0.#"),
            'm' or 'n' => Strings.Num(Mathf.RoundToInt(v)),
            'x' => Strings.Num(v, "0.0#"),
            _ => Strings.Num(Mathf.RoundToInt(v * 100f)),
        };

        /// <summary>A number's placeholder name by its kind (prompt 21 I.3): {percent}, {seconds}, {metres}, {count}, {times}.</summary>
        private static string KindName(char kind) => kind switch
        {
            's' => "seconds",
            'm' => "metres",
            'n' => "count",
            'x' => "times",
            _ => "percent",
        };

        /// <summary>A trait's or module's three numbers, named by their kinds; a second one of a kind is "{percent2}".</summary>
        private static (string name, object value)[] Args(string key, float a, float b, float c)
        {
            var f = Formats.TryGetValue(key, out var kinds) ? kinds : "p";
            char K(int i) => i < f.Length ? f[i] : 'p';
            var values = new[] { a, b, c };
            var args = new (string name, object value)[3];
            var seen = new Dictionary<string, int>();
            for (var i = 0; i < 3; i++)
            {
                var name = KindName(K(i));
                seen[name] = seen.TryGetValue(name, out var n) ? n + 1 : 1;
                args[i] = (seen[name] == 1 ? name : name + seen[name], Number(K(i), values[i]));
            }
            return args;
        }

        /// <summary>A piece's name: its base type ("Long Barrel") or module ("Trophy APS").</summary>
        public static string Name(GearItem item)
        {
            if (item.Slot == GearSlot.Special) return Strings.Get("special." + GearKeys.Module(item.Module));
            var b = Gear.BaseOf(item);
            return b != null ? Strings.Get("gear.base." + b.Id) : Strings.Get("gear.name." + item.Slot.ToString().ToLowerInvariant());
        }

        public static string SlotName(GearSlot slot) => Strings.Get("gear.slot." + slot.ToString().ToLowerInvariant());

        /// <summary>A tower slot's short name on a tower type's screen: "Weapon", "Structure", "Systems".</summary>
        public static string TowerSlotName(GearSlot slot) => Strings.Get("gear.towerSlot." + slot.ToString().ToLowerInvariant());

        /// <summary>Which of these tower types a tower piece works for, by name ("Guard Tower, AA Tower"), or a note that none can use it.</summary>
        public static string TowerFitLine(GearItem item, IEnumerable<string> towerIds)
        {
            var names = new List<string>();
            foreach (var id in towerIds)
                if (PlayerProfile.TowerFits(id, item))
                    names.Add(Strings.Card(id));
            return names.Count == 0 ? Strings.Get("gear.towerFitsNone") : string.Join(", ", names);
        }

        /// <summary>"Worn by: Guard Tower" for a tower piece a tower type wears, else empty.</summary>
        public static string TowerWornLine(GearItem item) =>
            PlayerProfile.TowerWearing(item) is { } tower ? Strings.Format("gear.towerWornBy", Strings.Card(tower)) : "";

        /// <summary>"Armour: tanks, heavy tanks, tank hunters" (which classes wear a branch's loadout).</summary>
        public static string BranchClasses(GearBranch branch)
        {
            var names = new List<string>();
            foreach (var (cls, _) in VehicleFit.ClassesOf(branch)) names.Add(Strings.Get("class." + cls));
            return Strings.Format("gear.branchClasses", ("gear", Strings.Get("gear.branch." + branch.ToString().ToLowerInvariant())), ("names", string.Join(", ", names)));
        }

        /// <summary>"Works for: Armour, Light" or "Works for no branch" (a vehicle piece's fit).</summary>
        public static string FitLine(GearItem item)
        {
            var names = new List<string>();
            var mask = Gear.BranchesOf(item);
            foreach (GearBranch b in System.Enum.GetValues(typeof(GearBranch)))
                if ((mask & GearCatalog.MaskOf(b)) != 0) names.Add(Strings.Get("gear.branch." + b.ToString().ToLowerInvariant()));
            return names.Count == 0 ? Strings.Get("gear.fitsNone") : Strings.Format("gear.fitsFor", string.Join(", ", names));
        }

        /// <summary>A stat line: "+8% range", "-6% speed" (a drawback), "-2 s regen delay".</summary>
        public static string Line(Gear.Line line) => Line(line.Stat, line.Value, line.Kind == Gear.LineKind.Penalty);

        public static string Line(StatId stat, float value, bool penalty = false)
        {
            // No stat of its own (the Monolith Plate): nothing to print rather than a raw key.
            if (stat == StatId.Count) return "";
            var key = GearKeys.Snake(stat.ToString());
            var amount = stat switch
            {
                StatId.Regen => Strings.Num(Mathf.Abs(value) * 100f, "0.00"),
                StatId.RegenDelay or StatId.LaserWarning => Strings.Num(Mathf.Abs(value), "0.#"),
                _ when Stats.InLevels(stat) => Strings.Num(Mathf.Abs(value), "0.0#"),
                _ => Strings.Num(Mathf.Abs(value) * 100f, Mathf.Abs(value) < 0.1f ? "0.#" : "0"),
            };
            return Strings.Format(penalty ? "stat.pen." + key : "stat.line." + key, amount);
        }

        /// <summary>A trait's name ("Ricochet Shells").</summary>
        public static string TraitName(string key) => Strings.Get("trait." + key);

        /// <summary>What a trait does, with its numbers (a tower line at its full strength has its own words: "no wait", "immune").</summary>
        public static string TraitEffect(GearTrait t)
        {
            var key = GearKeys.Trait(t.Id);
            var info = "trait." + key + ".info";
            if (t.Id is TraitId.TowerModular or TraitId.TowerBackupGenerator && t.A >= 1f && Strings.Has(info + ".full")) info += ".full";
            return Strings.Format(info, Args(key, t.A, t.B, t.C));
        }

        /// <summary>What a tower must have for a piece or line to work ("Needs a weapon that can hit aircraft"), for the tower equipment screens.</summary>
        public static string TowerNeedLine(TowerNeed need)
        {
            if ((need & TowerNeed.Mobile) != 0) return Strings.Get("gear.towerNeed.never");
            if (TowerFit.Within(TowerNeed.Magazine, need)) return Strings.Get("gear.towerNeed.magazine");
            if (TowerFit.Within(TowerNeed.HitsAir, need)) return Strings.Get("gear.towerNeed.hitsAir");
            if (TowerFit.Within(TowerNeed.HitsGround, need)) return Strings.Get("gear.towerNeed.hitsGround");
            if (TowerFit.Within(TowerNeed.Armed, need)) return Strings.Get("gear.towerNeed.armed");
            return Strings.Get("gear.towerNeed.none");
        }

        /// <summary>A piece's trait line: "Ricochet Shells: each hit bounces...", or empty.</summary>
        public static string TraitLine(GearItem item)
        {
            var t = Gear.TraitOf(item);
            return t.Id == TraitId.None ? "" : TraitName(GearKeys.Trait(t.Id)) + ": " + TraitEffect(t);
        }

        /// <summary>What a base type does besides its main stat, for a codex (the Monolith Plate: a bigger main stat, no sub-stats).</summary>
        public static string BaseNote(BaseTypeDef b)
        {
            if (b.MainScale != 1f && b.NoSubs) return Strings.Format("gear.base.bigMain", Strings.Num((b.MainScale - 1f) * 100f, "0"));
            return "";
        }

        /// <summary>What a module does at a rarity, with its numbers (no piece needed).</summary>
        public static string ModuleEffect(SpecialModule module, Rarity rarity) =>
            ModuleEffect(new GearItem { slot = (int)GearSlot.Special, rarity = (int)rarity, special = (int)module, baseType = GearKeys.Module(module) });

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
        public static string Chip(Gear.SetChip chip) => Strings.Format("gear.setChip", ("brand", BrandName(chip.Brand)), ("count", chip.Count));

        /// <summary>A brand's two bonuses: "2: +6% health · 4: Bulwark: ...".</summary>
        public static string BrandBonuses(BrandDef brand)
        {
            var four = brand.FourPiece;
            var two = brand.TwoPiece.Id != TraitId.None ? TraitName(GearKeys.Trait(brand.TwoPiece.Id)) + ": " + TraitEffect(brand.TwoPiece) : Line(brand.Stat, brand.Value);
            // A tower brand's pieces count across the whole base.
            var text = Strings.Format("gear.brandBonuses", ("two", two), ("four", TraitName(GearKeys.Trait(four.Id)) + ": " + TraitEffect(four)));
            return brand.TowerOnly ? text + " " + Strings.Get("gear.brandBase") : text;
        }

        /// <summary>The word shown over a vehicle when its equipment goes off ("RICOCHET"), or null for none.</summary>
        public static string Proc(string key) => key != null && Strings.Has("proc." + key) ? Strings.Get("proc." + key) : null;
    }
}
