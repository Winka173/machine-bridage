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
            // Play-test 7 (roster version 5, DECISIONS 22P): the Gunship support card became the AC-130 aircraft card again.
            ["gunship_strike"] = "sky_gunship",
        };

        /// <summary>
        /// Cards gone with nothing in their place. None now: the sky gunship, retired in prompt 2, is the AC-130 aircraft card
        /// again (play-test 7); a save migrated before kept the refund, one not yet migrated keeps the card.
        /// </summary>
        public static readonly string[] Retired = System.Array.Empty<string>();

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

        /// <summary>
        /// Prompt 32 L1 (roster version 7, DECISIONS "Prompt 32 L0/L1/L2"): the tower roster 32 -> 22. A tower card folded
        /// into another: the card it became keeps the higher rank, the unlock moves across (a bought card stays bought), and
        /// when the player already had the card it became, the duplicate's coins come back (<see cref="TowerPrices"/>).
        /// </summary>
        public static readonly IReadOnlyDictionary<string, string> TowerInto = new Dictionary<string, string>
        {
            ["recoilless_gun_tower"] = "at_gun_emplacement",
            ["manpads_tower"] = "aa_turret",
            ["flare_tower"] = "searchlight",
            ["flare_searchlight_tower"] = "searchlight",
            ["barrage_balloon"] = "inflatable_decoy",
            ["aa_gun_tower"] = "heavy_flak_tower",
            ["drone_net_tower"] = "laser_ad_station",
            ["bunker_shelter_tower"] = "troop_shelter",
        };

        /// <summary>Prompt 32 L1: tower cards gone from the roster (still map and mission structures): coins back at the price paid, slots emptied.</summary>
        public static readonly string[] RetiredTowers = { "blast_wall", "one_shot_atgm_tower" };

        /// <summary>Prompt 32 L1: what the folded and retired tower cards cost in the shop (prompt 25 F2's prices), for the refunds.</summary>
        public static readonly IReadOnlyDictionary<string, int> TowerPrices = new Dictionary<string, int>
        {
            ["recoilless_gun_tower"] = 2000, ["manpads_tower"] = 2000, ["flare_tower"] = 2000, ["flare_searchlight_tower"] = 2000,
            ["barrage_balloon"] = 2000, ["aa_gun_tower"] = 3000, ["drone_net_tower"] = 2000, ["bunker_shelter_tower"] = 3000,
            ["blast_wall"] = 2000, ["one_shot_atgm_tower"] = 3000,
        };

        /// <summary>Prompt 32 L1: towers left without branches: a choice on one is dropped (the card fights as itself).</summary>
        public static readonly string[] NoBranchTowers = { "minefield", "cp_relay", "troop_shelter" };

        /// <summary>Prompt 32 L1: branches gone with them.</summary>
        public static readonly string[] RetiredBranchesP32 = { "minefield.at", "minefield.scatter", "cp_relay.hardened", "cp_relay.loot" };

        /// <summary>
        /// Prompt 32 L1: branches that changed what they do (the AA tower's SAM post is the Stinger post; the gun turret's
        /// 57 mm fires at light vehicles only): a player who chose one keeps it, with one free change and a news line.
        /// </summary>
        public static readonly string[] ReworkedBranchesP32 = { "aa_turret.sam", "gun_turret.auto" };

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
