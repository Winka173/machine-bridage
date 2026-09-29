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
            // Prompt 17 D (roster version 2): the A-10 into the attack jet, the Ka-52 into the attack helicopter, the ATGM
            // carrier into the FPV carrier, the fortification sapper into the engineer, the hidden gun pit into the gun turret.
            ["tank_buster"] = "attack_jet",
            ["heavy_attack_heli"] = "attack_helicopter",
            ["atgm_carrier"] = "fpv_carrier",
            ["sapper"] = "engineer_vehicle",
            [GunPit] = GunTurret,
        };

        /// <summary>Cards gone with nothing in their place (the sky gunship is only the Gunship item's aircraft now).</summary>
        public static readonly string[] Retired = { "sky_gunship" };

        /// <summary>Tower branches gone (prompt 20 L.1: the C-RAM's Hunter made way for the Iron Dome): a choice of one is dropped.</summary>
        public static readonly string[] RetiredBranches = { "c_ram.hunter" };

        /// <summary>
        /// The tower-branch rework (DECISIONS 19T): remade branches and the nearest new one a choice moves to (the same
        /// slot, A or B; the ids that still describe their branch were kept: the gun turret's, the Patriot's, the heavy
        /// fortress's, the counter-battery howitzer's).
        /// </summary>
        public static readonly IReadOnlyDictionary<string, string> RenamedBranches = new Dictionary<string, string>
        {
            ["rocket_turret.thermo"] = "rocket_turret.guided",
            ["artillery_emplacement.ext"] = "artillery_emplacement.mortar",
            ["shield_tower.pulse"] = "shield_tower.ward",
            ["cp_relay.express"] = "cp_relay.loot",
        };

        /// <summary>The towers whose branches changed in the rework: a player's choice on one earns a free change and a news line.</summary>
        public static readonly string[] ReworkedBranchTowers =
            { "gun_turret", "rocket_turret", "artillery_emplacement", "missile_battery", "heavy_turret", "shield_tower", "cp_relay" };

        /// <summary>What the retired and merged premium cards cost: a player who bought one gets it back.</summary>
        public static readonly IReadOnlyDictionary<string, int> PremiumPrices = new Dictionary<string, int>
        {
            ["sky_gunship"] = 4500,
            ["carpet_bombing"] = 3000,
            ["heavy_attack_heli"] = 3500,
        };

        /// <summary>Prompt 17 D.4: the hidden gun pit, gone from the towers, and the tower its players get instead.</summary>
        public const string GunPit = "gun_pit";

        public const string GunTurret = "gun_turret";

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
