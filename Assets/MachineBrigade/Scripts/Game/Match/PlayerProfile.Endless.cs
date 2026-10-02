using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Game.Match
{
    /// <summary>Prompt 30 L5: the endless parts' daily coin cap (600 over every mode) and their badges.</summary>
    public static partial class PlayerProfile
    {
        /// <summary>Coins the endless parts paid today.</summary>
        public static int EndlessPaidToday => D.endlessDay == Today ? D.endlessPaid : 0;

        /// <summary>Pays what the cap allows of <paramref name="coins"/>; returns what was paid.</summary>
        public static int PayEndless(int coins)
        {
            if (D.endlessDay != Today)
            {
                D.endlessDay = Today;
                D.endlessPaid = 0;
            }
            var paid = EndlessRules.Capped(coins, D.endlessPaid);
            if (paid <= 0) return 0;
            D.endlessPaid += paid;
            AddCoins(paid);
            return paid;
        }

        /// <summary>A badge ("defend.10", "bossrush.5"), once; true when new.</summary>
        public static bool AwardEndlessBadge(string id)
        {
            D.endlessBadges ??= new System.Collections.Generic.List<string>();
            if (D.endlessBadges.Contains(id)) return false;
            D.endlessBadges.Add(id);
            Save();
            return true;
        }

        public static bool HasEndlessBadge(string id) => D.endlessBadges != null && D.endlessBadges.Contains(id);
    }
}
