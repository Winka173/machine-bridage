using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>How a card becomes available.</summary>
    public enum CardRoute
    {
        /// <summary>Owned from the start.</summary>
        Starter,

        /// <summary>Won in the campaign, or unlocked early for coins.</summary>
        Campaign,

        /// <summary>Bought with coins only.</summary>
        Premium,
    }

    /// <summary>
    /// Which cards a new player has, which the campaign hands out (and what unlocking one early
    /// costs), and the premium units and strikes sold for coins.
    /// </summary>
    public static class Progression
    {
        public static readonly string[] StarterVehicles =
            { "scout_jeep", "armored_car", "apc", "light_tank", "main_battle_tank", "aa_vehicle", "artillery" };

        public static readonly string[] StarterSupports = { "artillery_barrage", "smoke_screen" };

        private static readonly Dictionary<string, int> PremiumPrices = new()
        {
            ["titan_tank"] = 3000,
            ["heavy_bomber"] = 4000,
            ["sky_gunship"] = 4500,
            ["stealth_bomber"] = 5000,
            ["siege_tank"] = 4500,
            ["ballistic_launcher"] = 5000,
            ["heavy_attack_heli"] = 3500,
            ["napalm_strike"] = 1500,
            ["carpet_bombing"] = 3000,
        };

        public static bool IsStarter(string id) =>
            System.Array.IndexOf(StarterVehicles, id) >= 0 || System.Array.IndexOf(StarterSupports, id) >= 0;

        public static bool IsPremium(string id) => PremiumPrices.ContainsKey(id);

        public static CardRoute Route(string id) => IsStarter(id) ? CardRoute.Starter : IsPremium(id) ? CardRoute.Premium : CardRoute.Campaign;

        /// <summary>Coins for a premium card, or for unlocking a campaign card before winning it.</summary>
        public static int Price(string id, Catalog catalog)
        {
            if (PremiumPrices.TryGetValue(id, out var premium)) return premium;
            var cp = catalog.Vehicles.TryGetValue(id, out var v) ? v.CpCost : catalog.TryGetSupport(id, out var s) ? s.CpCost : 5;
            return 300 + 150 * cp;
        }

        /// <summary>The campaign mission that unlocks a card, or null.</summary>
        public static MissionDef UnlockMission(string id)
        {
            foreach (var mission in Campaign.All)
                foreach (var unlock in mission.Unlocks)
                    if (unlock == id) return mission;
            return null;
        }

        public static bool Available(string id) => PlayerProfile.IsUnlocked(id);
    }

    /// <summary>The campaign missions in order, and which ones the player may start.</summary>
    public static class Campaign
    {
        private static IReadOnlyList<MissionDef> _all;

        public static IReadOnlyList<MissionDef> All => _all ??= GameContent.LoadCampaign();

        public static MissionDef Get(string id)
        {
            foreach (var m in All)
                if (m.Id == id) return m;
            return null;
        }

        public static int IndexOf(string id)
        {
            for (var i = 0; i < All.Count; i++)
                if (All[i].Id == id) return i;
            return -1;
        }

        /// <summary>The first mission, and every mission after one already won.</summary>
        public static bool IsOpen(int index) => index == 0 || (index > 0 && index < All.Count && PlayerProfile.Completed(All[index - 1].Id));

        /// <summary>The next mission to play: the first not yet won (or the last).</summary>
        public static int Next
        {
            get
            {
                for (var i = 0; i < All.Count; i++)
                    if (!PlayerProfile.Completed(All[i].Id)) return i;
                return All.Count - 1;
            }
        }

        public static int Won
        {
            get
            {
                var won = 0;
                foreach (var m in All)
                    if (PlayerProfile.Completed(m.Id)) won++;
                return won;
            }
        }
    }
}
