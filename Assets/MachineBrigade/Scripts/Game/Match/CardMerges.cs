using System;
using System.Collections.Generic;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The roster cleanup: cards folded into another card, and cards retired outright. Saved
    /// progress on them moves across once (see PlayerProfile.MigrateRoster): the unlock, the
    /// blueprints and the higher of the two ranks go to the card it became, the coins and
    /// blueprints spent on the lower rank come back, and a card bought with coins that no longer
    /// exists is refunded. Saved decks swap them for the card they became.
    /// </summary>
    public static class CardMerges
    {
        /// <summary>Old card → the card it became.</summary>
        public static readonly IReadOnlyDictionary<string, string> Into = new Dictionary<string, string>
        {
            ["apc"] = "ifv",
            ["aps_tank"] = "main_battle_tank",
            ["grad_truck"] = "mlrs",
            ["howitzer"] = "artillery",
            ["siege_mortar"] = "siege_tank",
            ["carpet_bombing"] = "airstrike",
        };

        /// <summary>Cards gone with nothing in their place (the sky gunship is only the Gunship item's aircraft now).</summary>
        public static readonly string[] Retired = { "sky_gunship" };

        /// <summary>What the retired and merged premium cards cost: a player who bought one gets it back.</summary>
        public static readonly IReadOnlyDictionary<string, int> PremiumPrices = new Dictionary<string, int>
        {
            ["sky_gunship"] = 4500,
            ["carpet_bombing"] = 3000,
        };

        /// <summary>Owners of the APS tank get this piece: its active protection as an Epic Trophy APS module.</summary>
        public const string ApsTank = "aps_tank";

        /// <summary>The card an old id stands for now (itself when it was not merged; null when it was retired).</summary>
        public static string Resolve(string id)
        {
            if (id == null) return null;
            if (Into.TryGetValue(id, out var to)) return to;
            return Array.IndexOf(Retired, id) >= 0 ? null : id;
        }

        public static bool IsGone(string id) => id != null && (Into.ContainsKey(id) || Array.IndexOf(Retired, id) >= 0);
    }
}
