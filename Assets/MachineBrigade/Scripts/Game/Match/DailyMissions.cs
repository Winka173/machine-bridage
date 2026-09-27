using System;
using System.Collections.Generic;

namespace MachineBrigade.Game.Match
{
    /// <summary>One of today's challenges: what to do, how much, and the coins it pays.</summary>
    public readonly struct DailyTask
    {
        public DailyTask(string kind, int target, int reward)
        {
            Kind = kind;
            Target = target;
            Reward = reward;
        }

        /// <summary>kills, wins, strikes, buildings, captures, bosses, elites or items.</summary>
        public string Kind { get; }

        public int Target { get; }
        public int Reward { get; }
    }

    /// <summary>
    /// Three daily challenges, the same for everyone on a given date, paying coins when claimed.
    /// Progress lives in the profile and resets when the date changes.
    /// </summary>
    public static class DailyMissions
    {
        private static readonly (string kind, int[] targets, int reward)[] Pool =
        {
            ("kills", new[] { 40, 60, 90 }, 150),
            ("wins", new[] { 1, 2, 3 }, 180),
            ("strikes", new[] { 6, 10, 15 }, 120),
            ("buildings", new[] { 12, 20, 30 }, 120),
            ("captures", new[] { 4, 8, 12 }, 130),
            ("bosses", new[] { 1, 1, 2 }, 250),
            ("elites", new[] { 3, 5, 8 }, 160),
            ("items", new[] { 1, 2, 3 }, 100),
        };

        /// <summary>Today as yyyymmdd (local date).</summary>
        public static int Today => int.Parse(DateTime.Now.ToString("yyyyMMdd"));

        /// <summary>The three challenges for <paramref name="day"/> (distinct kinds, sizes scaled 0-2).</summary>
        public static IReadOnlyList<DailyTask> For(int day)
        {
            var rng = new Random(day * 31 + 7);
            var order = new List<int>();
            for (var i = 0; i < Pool.Length; i++) order.Add(i);
            var tasks = new List<DailyTask>();
            for (var n = 0; n < 3; n++)
            {
                var pick = order[rng.Next(order.Count)];
                order.Remove(pick);
                var (kind, targets, reward) = Pool[pick];
                var size = rng.Next(targets.Length);
                tasks.Add(new DailyTask(kind, targets[size], reward + size * reward / 2));
            }
            return tasks;
        }

        public static IReadOnlyList<DailyTask> Current => For(Today);

        /// <summary>Counts <paramref name="amount"/> towards today's challenges of this kind.</summary>
        public static void Record(string kind, int amount = 1)
        {
            var tasks = Current;
            for (var i = 0; i < tasks.Count; i++)
                if (tasks[i].Kind == kind) PlayerProfile.AddDailyProgress(Today, i, amount, tasks[i].Target);
        }

        public static int Progress(int index) => PlayerProfile.DailyProgress(Today, index);

        public static bool Claimed(int index) => PlayerProfile.DailyClaimed(Today, index);

        public static bool Done(int index) => Progress(index) >= Current[index].Target;

        /// <summary>Pays a finished, unclaimed challenge; false otherwise.</summary>
        public static bool Claim(int index)
        {
            if (!Done(index) || Claimed(index)) return false;
            PlayerProfile.ClaimDaily(Today, index);
            PlayerProfile.AddCoins(Current[index].Reward);
            return true;
        }
    }
}
