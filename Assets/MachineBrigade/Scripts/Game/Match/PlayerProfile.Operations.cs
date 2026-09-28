using System;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The Operations mode's records (best score and best time per battle and tier) and the one
    /// weekly reward ledger it shares with the weekly fortress: each weekly reward (by key) pays
    /// once a week.
    /// </summary>
    public static partial class PlayerProfile
    {
        private static int OperationIndex(string id, int tier)
        {
            for (var i = 0; i < D.opsIds.Count; i++)
                if (D.opsIds[i] == id && D.opsTiers[i] == tier) return i;
            return -1;
        }

        /// <summary>The best score won on a battle at a tier (0: never won).</summary>
        public static int BestScore(string id, int tier)
        {
            var i = OperationIndex(id, tier);
            return i >= 0 ? D.opsScores[i] : 0;
        }

        /// <summary>The fastest win of a battle at a tier, in seconds (0: never won).</summary>
        public static float BestTime(string id, int tier)
        {
            var i = OperationIndex(id, tier);
            return i >= 0 ? D.opsTimes[i] : 0f;
        }

        /// <summary>Keeps a won battle's score and time where they beat the record; true for a new best score.</summary>
        public static bool RecordOperation(string id, int tier, int score, float seconds)
        {
            if (score <= 0) return false;
            var i = OperationIndex(id, tier);
            if (i < 0)
            {
                D.opsIds.Add(id);
                D.opsTiers.Add(tier);
                D.opsScores.Add(score);
                D.opsTimes.Add(seconds);
                Save();
                return true;
            }
            var best = score > D.opsScores[i];
            if (best) D.opsScores[i] = score;
            if (D.opsTimes[i] <= 0f || seconds < D.opsTimes[i]) D.opsTimes[i] = seconds;
            Save();
            return best;
        }

        /// <summary>Starts the ledger on a new week (the fortress's stage goes back to the first ring).</summary>
        private static void WeekOf(int week)
        {
            if (D.weeklyId == week) return;
            D.weeklyId = week;
            D.weeklyStage = 1;
            D.weeklyClaimed = false;
            D.weeklyClaims.Clear();
        }

        /// <summary>Whether this week's reward of this kind ("fortress", "operation") was paid.</summary>
        public static bool WeeklyPaid(int week, string key) =>
            D.weeklyId == week && (D.weeklyClaims.Contains(key) || (key == "fortress" && D.weeklyClaimed));

        /// <summary>Pays this week's reward of this kind once: true the first time.</summary>
        public static bool ClaimWeekly(int week, string key)
        {
            WeekOf(week);
            if (WeeklyPaid(week, key)) return false;
            D.weeklyClaims.Add(key);
            if (key == "fortress") D.weeklyClaimed = true;
            Save();
            return true;
        }
    }
}
