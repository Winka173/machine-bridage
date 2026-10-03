using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 32 L4: the player's HQ type (Fortress, Garrison, Shield) and a Fortress's branch, chosen free on the Base
    /// screen; every base the player takes into battle carries it.
    /// </summary>
    public static partial class PlayerProfile
    {
        /// <summary>The HQ type in the save (the data's default when none is set).</summary>
        public static HqType HqType
        {
            get => HqTypeRules.TryParse(D.hqType, out var t) ? t : GameContent.LoadCatalog().Base.HqTypes.Default;
            set
            {
                D.hqType = HqTypeRules.Key(value);
                Save();
            }
        }

        /// <summary>A Fortress HQ's branch: its ground guns or its anti-air guns.</summary>
        public static HqBranch HqBranch
        {
            get => System.Enum.TryParse(D.hqBranch ?? "", true, out HqBranch b) ? b : HqBranch.Ground;
            set
            {
                D.hqBranch = value.ToString().ToLowerInvariant();
                Save();
            }
        }

        /// <summary>
        /// Play-test 14: the light unit a Garrison HQ calls, chosen on the HQ tab (null: the level's mixed squad). Only a
        /// unit the HQ may call (<see cref="HqTypeRules.Callable"/>) counts.
        /// </summary>
        public static string HqUnit
        {
            get => string.IsNullOrEmpty(D.hqUnit) ? null : D.hqUnit;
            set
            {
                D.hqUnit = value ?? "";
                Save();
            }
        }

        /// <summary>
        /// Play-test 14: the units a call the player fills drops (its Units called tab): the saved drop with what is no longer
        /// in the call's list or not unlocked left out, cut to the call's cap; nothing saved: the support's own units, so cut.
        /// </summary>
        public static List<string> CallUnits(string supportId, SupportDef support, Catalog catalog)
        {
            var saved = new List<string>();
            var found = false;
            foreach (var entry in D.calls)
            {
                var at = entry.IndexOf('=');
                if (at <= 0 || entry.Substring(0, at) != supportId) continue;
                found = true;
                foreach (var u in entry.Substring(at + 1).Split(','))
                    if (!string.IsNullOrEmpty(u)) saved.Add(u);
            }
            var list = new List<string>();
            var total = 0f;
            foreach (var u in found ? saved : new List<string>(support.Units))
            {
                if (!catalog.Vehicles.TryGetValue(u, out var def)) continue;
                if (found && (System.Linq.Enumerable.Contains(support.CallChoices, u) == false || !IsUnlocked(u))) continue;
                if (total + def.BaseCp > support.CallMaxCp + 1e-4f) continue;
                total += def.BaseCp;
                list.Add(u);
            }
            return list;
        }

        public static void SetCallUnits(string supportId, List<string> units)
        {
            D.calls.RemoveAll(e => e.StartsWith(supportId + "=", System.StringComparison.Ordinal));
            D.calls.Add(supportId + "=" + string.Join(",", units));
            Save();
        }

        /// <summary>Play-test 14: the unit a hangar card turns out (null: its first, the data's default).</summary>
        public static string HangarUnit(string hangarId)
        {
            var i = D.hangarIds.IndexOf(hangarId);
            return i >= 0 && i < D.hangarUnits.Count && !string.IsNullOrEmpty(D.hangarUnits[i]) ? D.hangarUnits[i] : null;
        }

        public static void SetHangarUnit(string hangarId, string unit)
        {
            var i = D.hangarIds.IndexOf(hangarId);
            if (i < 0)
            {
                D.hangarIds.Add(hangarId);
                D.hangarUnits.Add(unit ?? "");
            }
            else
            {
                while (D.hangarUnits.Count <= i) D.hangarUnits.Add("");
                D.hangarUnits[i] = unit ?? "";
            }
            Save();
        }

        /// <summary>
        /// The next choice on the Base screen's HQ: Fortress (ground), Fortress (anti-air), Garrison, Shield, round again.
        /// Free: a choice in the loadout, as a deck's cards are.
        /// </summary>
        public static void NextHqType()
        {
            if (HqType == HqType.Fortress && HqBranch == HqBranch.Ground) HqBranch = HqBranch.Air;
            else if (HqType == HqType.Fortress)
            {
                HqBranch = HqBranch.Ground;
                HqType = HqType.Garrison;
            }
            else HqType = HqType == HqType.Garrison ? HqType.Shield : HqType.Fortress;
        }

        /// <summary>
        /// The move from the HQ doctrine to the HQ type, once: no save holds a doctrine any more (DECISIONS 23D refunded
        /// them), so nothing is to pay back; a save that had played before is told once that the HQ's type is now chosen
        /// on the Base screen, free (the free re-pick the prompt asks for: every choice of type is free).
        /// </summary>
        private static void MigrateHqType(Data d)
        {
            if (d.hqTypeVersion >= 1) return;
            d.hqTypeVersion = 1;
            var played = d.missionIds.Count > 0 || d.baseEdited || d.rosterVersion > 0;
            if (played && string.IsNullOrEmpty(d.hqType)) d.hqTypeNews = true;
        }

        /// <summary>Whether to tell the player once about the HQ types (then not again).</summary>
        public static bool TakeHqTypeNews()
        {
            if (!D.hqTypeNews) return false;
            D.hqTypeNews = false;
            Save();
            return true;
        }
    }
}
