using System;
using System.Globalization;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The bomb-run fix, pass 4 (DECISIONS "Ném bom rải thảm"): an aircraft card's stick of bombs read from the data, as the
    /// support cards' numbers are (<see cref="SupportLines"/>). A unit's guide text writes <c>{{stick}}</c> where its bombs
    /// are named; <see cref="Strings.Get"/> fills it from the first weapon of the unit that lays a stick (weapons[*].stick):
    /// "thả N quả, cách nhau X m, dải Y m" / "N bombs X m apart, a Y m stick". So the card can never say twelve bombs again
    /// when the data drops seven.
    /// </summary>
    public static class StickLines
    {
        private static Catalog _catalog;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics() => _catalog = null;

        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        /// <summary>The placeholder a unit's guide text puts where its stick is named.</summary>
        public const string Placeholder = "{{stick}}";

        /// <summary>The stick a unit lays (its first mount whose weapon lays one), or null.</summary>
        public static StickDef StickOf(VehicleDef def)
        {
            if (def == null) return null;
            foreach (var mount in def.Mounts)
                if (mount.Weapon?.Stick is { Laid: true } stick) return stick;
            return null;
        }

        /// <summary>The words for a stick in the language asked: "thả 7 quả, cách nhau 11 m, dải 66 m".</summary>
        public static string Words(StickDef stick, bool vietnamese)
        {
            var culture = vietnamese ? Strings.Culture : CultureInfo.InvariantCulture;
            string N(float v) => v.ToString(v >= 10f || Math.Abs(v - MathF.Round(v)) < 0.05f ? "0" : "0.#", culture);
            var length = Math.Max(0, stick.Bombs - 1) * stick.Spacing;
            return vietnamese
                ? $"thả {stick.Bombs} quả, cách nhau {N(stick.Spacing)} m, dải {N(length)} m"
                : $"{stick.Bombs} bombs {N(stick.Spacing)} m apart, a {N(length)} m stick";
        }

        /// <summary>A unit's guide text with its stick filled in (unchanged without the placeholder or a stick).</summary>
        public static string Fill(string key, string text, bool vietnamese)
        {
            if (text == null || text.IndexOf(Placeholder, StringComparison.Ordinal) < 0) return text;
            if (!key.StartsWith("guide.", StringComparison.Ordinal)) return text;
            if (!Catalog.Vehicles.TryGetValue(key.Substring(6), out var def) || StickOf(def) is not { } stick) return text;
            return text.Replace(Placeholder, Words(stick, vietnamese));
        }
    }
}
