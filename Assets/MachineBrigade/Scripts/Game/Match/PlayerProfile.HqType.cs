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
