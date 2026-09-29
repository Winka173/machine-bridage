using System;
using System.Globalization;
using System.Text.RegularExpressions;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The balance pass after prompt 18 (C.3): a support card's texts (its guide entry and its one-line
    /// info) take their numbers from the data, as prompt 13 G's unit lines do. The hand-written text
    /// carries named placeholders, <c>{{count}}</c>, <c>{{length}}</c> and the rest below, which
    /// <see cref="Strings.Get"/> fills from the support's definition, so a balance change can never leave
    /// the text behind ("fourteen bombs" when the data drops ten). <c>SupportTextTests</c> fails on any
    /// number still written by hand that is none of the support's own.
    /// </summary>
    public static class SupportLines
    {
        private static Catalog _catalog;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics() => _catalog = null;

        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static readonly Regex Placeholder = new(@"\{\{(\w+)\}\}");

        private static CultureInfo Culture => Strings.Culture;

        /// <summary>The support a text key belongs to: "guide.&lt;id&gt;", "support.&lt;id&gt;.info" or "support.&lt;id&gt;".</summary>
        public static string SupportOf(string key)
        {
            string id = null;
            if (key.StartsWith("guide.", StringComparison.Ordinal)) id = key.Substring(6);
            else if (key.StartsWith("support.", StringComparison.Ordinal))
                id = key.EndsWith(".info", StringComparison.Ordinal) ? key.Substring(8, key.Length - 13) : key.Substring(8);
            return id != null && Catalog.Supports.ContainsKey(id) ? id : null;
        }

        /// <summary>A text with its placeholders filled from the support the key belongs to (unchanged without any).</summary>
        public static string Fill(string key, string text)
        {
            if (text == null || text.IndexOf("{{", StringComparison.Ordinal) < 0) return text;
            var id = SupportOf(key);
            if (id == null) return text;
            var s = Catalog.Supports[id];
            return Placeholder.Replace(text, m => Value(s, m.Groups[1].Value) ?? m.Value);
        }

        /// <summary>The names a text may use, and the number each stands for.</summary>
        public static readonly string[] Names =
        {
            "count", "rankCount", "length", "rankLength", "rank", "linePercent", "radius", "width", "blast", "duration", "delay",
            "cooldown", "cp", "damage", "percent", "units", "unitRank",
        };

        public static float? Number(SupportDef s, string name) => name switch
        {
            "count" => s.Count,
            // From the card rank that lengthens the bomb line (the strike system rounds its bombs the same way).
            "rankCount" => MathF.Round(s.Count * s.LineScale),
            "length" => s.Length,
            "rankLength" => s.Length * s.LineScale,
            "rank" => s.LineRank,
            "linePercent" => MathF.Round((s.LineScale - 1f) * 100f),
            "radius" => s.Radius,
            "width" => s.Radius * 2f,
            "blast" => s.BlastRadius,
            "duration" => s.Duration,
            "delay" => s.Delay,
            "cooldown" => s.Cooldown,
            "cp" => s.CpCost,
            "damage" => s.Damage,
            // A share of health (repair) or of damage taken off (a shield dome), as a percentage.
            "percent" => MathF.Round(s.Damage * 100f),
            "units" => s.Units.Count,
            "unitRank" => s.UnitRank,
            _ => null,
        };

        private static string Value(SupportDef s, string name) => Number(s, name) is { } v ? N(v) : null;

        private static string N(float value) => value.ToString(value >= 10f || Math.Abs(value - MathF.Round(value)) < 0.05f ? "0" : "0.#", Culture);
    }
}
