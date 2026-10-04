using System.Collections.Generic;
using System.Globalization;
using System.Text;
using MachineBrigade.Game.Match;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 15 D: which icon of the armour and weapon set (<c>Icons.Combat.cs</c>, drawn by
    /// <c>Tools/art/combat_icons.py</c>) stands for an armour level, a weapon form, a damage type or a tag, and the
    /// words of their tooltips. No icon carries a number; with Settings > "Hiện số chi tiết" on
    /// (<see cref="MatchSettings.ShowCombatNumbers"/>) the tooltips add the levels and multipliers.
    /// </summary>
    public static class CombatIcons
    {
        /// <summary>The sim's WeaponForm names, in the enum's order, and their icons.</summary>
        public static readonly IReadOnlyDictionary<string, string> Forms = new Dictionary<string, string>
        {
            ["BulletSmall"] = "w_mg_light",
            ["BulletBig"] = "w_mg_heavy",
            ["BeltedAutocannon"] = "w_autocannon",
            ["Dart"] = "w_dart",
            ["DoubleDart"] = "w_dart_heavy",
            ["Rail"] = "w_rail",
            ["HeShell"] = "w_shell",
            ["MortarBomb"] = "w_mortar",
            ["Airburst"] = "w_airburst",
            ["RocketSmall"] = "w_rocket",
            ["RocketBig"] = "w_rocket_heavy",
            ["Atgm"] = "w_atgm",
            ["Sam"] = "w_sam",
            ["Cruise"] = "w_cruise",
            ["Ballistic"] = "w_ballistic",
            ["Bomb"] = "w_bomb",
            ["GuidedBomb"] = "w_bomb_guided",
            ["Cluster"] = "w_bomb_cluster",
            ["HeavyBomb"] = "w_bomb_heavy",
            ["Fpv"] = "w_fpv",
            ["Shahed"] = "w_shahed",
            ["Lancet"] = "w_lancet",
            ["Flame"] = "w_flame",
            ["Napalm"] = "w_napalm",
            ["Energy"] = "w_beam",
            ["Grenade"] = "w_grenade",
            ["Blade"] = "w_blade",
            ["Drill"] = "w_drill",
            ["SuperShell"] = "w_supergun",
            ["CarBomb"] = "w_charge",
        };

        /// <summary>The sim's DamageType names and their marks; kinetic has none (the round's shape says it).</summary>
        public static readonly IReadOnlyDictionary<string, string> Types = new Dictionary<string, string>
        {
            ["Kinetic"] = null,
            ["ShapedCharge"] = "d_shaped",
            ["HighExplosive"] = "d_he",
            ["Fire"] = "d_fire",
            ["Fragmentation"] = "d_frag",
            ["Energy"] = "d_energy",
        };

        public const string Thermobaric = "d_thermo";
        public const string TopAttack = "x_top";
        public const string Guided = "x_guided";
        public const string Splash = "x_splash";

        public static string Armour(int level, ArmourKind kind) =>
            (kind switch { ArmourKind.Air => "a_a", ArmourKind.Structure => "a_s", _ => "a_g" }) + ClampArmour(level);

        public static string Form(string form) => form != null && Forms.TryGetValue(form, out var icon) ? icon : null;

        /// <summary>The weapon's corner mark: the thermobaric tag's own, else its type's (none for kinetic).</summary>
        public static string Mark(WeaponFacts w) =>
            w == null ? null : w.Thermobaric ? Thermobaric : w.Damage != null && Types.TryGetValue(w.Damage, out var m) ? m : null;

        public static string Verdict(Verdict v) => v switch { Hud.Verdict.Good => "m_good", Hud.Verdict.Poor => "m_poor", _ => "m_none" };

        // ---------------------------------------------------------------- words

        private static int Clamp(int level) => level < 0 ? 0 : level > MachineBrigade.Sim.Content.ArmourLevels.Max ? MachineBrigade.Sim.Content.ArmourLevels.Max : level;

        /// <summary>Armour goes to 5 (a boss's plate, DECISIONS 21G; a super-heavy's front since 04/10); penetration too (Armour/Pen 5, 04/10).</summary>
        private static int ClampArmour(int level) => level < 0 ? 0 : level > MachineBrigade.Sim.Content.ArmourLevels.Max ? MachineBrigade.Sim.Content.ArmourLevels.Max : level;

        private static bool Numbers => MatchSettings.ShowCombatNumbers;

        private static string Num(float v) => v.ToString(v >= 10f ? "0" : "0.##", Strings.Culture);

        public static string ArmourName(int level, ArmourKind kind)
        {
            var name = Strings.Get("armour.level." + ClampArmour(level));
            if (kind != ArmourKind.Ground) name += " · " + Strings.Get(kind == ArmourKind.Air ? "armour.kind.air" : "armour.kind.structure");
            return Numbers ? name + " (" + ClampArmour(level) + ")" : name;
        }

        /// <summary>"Giáp dày · mặt trước" (face 0 front, 1 side, 2 rear, 3 top; -1 for no face).</summary>
        public static string ArmourTip(int level, ArmourKind kind, int face = -1) =>
            face < 0 ? ArmourName(level, kind) : ArmourName(level, kind) + " · " + Strings.Get("armour.face." + face);

        public static string PenName(int pen) =>
            Strings.Get("pen.level." + Clamp(pen)) + (Numbers ? " (" + Clamp(pen) + ")" : "");

        public static string FormName(string form) => Strings.Get("form." + (form ?? "None"));

        public static string TypeName(string damage) => Strings.Get("dtype." + (damage ?? "Kinetic"));

        /// <summary>"Tên lửa chống tăng · Nổ lõm · Xuyên rất cao · Đánh nóc · Dẫn đường".</summary>
        public static string WeaponTip(WeaponFacts w, bool withExtras = true)
        {
            if (w == null) return "";
            var sb = new StringBuilder(FormName(w.Form)).Append(" · ").Append(TypeName(w.Damage));
            if (w.Thermobaric) sb.Append(" · ").Append(Strings.Get("tag.thermo"));
            sb.Append(" · ").Append(PenName(w.Pen));
            if (withExtras)
            {
                if (w.TopAttack) sb.Append(" · ").Append(Strings.Get("tag.top"));
                if (w.Guided) sb.Append(" · ").Append(Strings.Get("tag.guided"));
                if (w.Splash) sb.Append(" · ").Append(Strings.Get("tag.splash"));
                // Prompt 25 G: a gun of two rounds.
                if (w.Rounds > 0) sb.Append(" · ").Append(Strings.Get("tag.swap"));
            }
            return sb.ToString();
        }

        public static string VerdictName(Verdict v) => Strings.Get("verdict." + v.ToString().ToLowerInvariant());

        /// <summary>The multiplier as the tooltips write it with the numbers on ("×0,75").</summary>
        public static string Times(float m) => "×" + Num(m);
    }
}
