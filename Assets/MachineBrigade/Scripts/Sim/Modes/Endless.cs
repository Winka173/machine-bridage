#nullable enable
using System;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// Prompt 30 L5 (sheet "Vô hạn"): the optional endless part after winning Defend, Survival or Boss Rush. The win, its
    /// rewards and stars are recorded at the resolve; "Continue" reopens the battle (<see cref="SimWorld.ContinueMatch"/>)
    /// and the mode goes on; losing later takes nothing back. Endless (the menu entry) is Defend started in its endless part.
    /// </summary>
    public interface IEndlessMode
    {
        /// <summary>Won its finite part and may go on.</summary>
        bool CanContinue { get; }

        /// <summary>In the endless part.</summary>
        bool InEndless { get; }

        /// <summary>Waves (or bosses) beyond the finite part.</summary>
        int EndlessSteps { get; }

        /// <summary>Goes on after the results' "Continue" (the world reopened first).</summary>
        void ContinueEndless(SimWorld world);
    }

    /// <summary>The endless part's numbers (sheet "Vô hạn"): stats only, never more vehicles than the finite part's last wave.</summary>
    public static class EndlessRules
    {
        /// <summary>Defend, Endless, Survival: the enemy +4 % a wave beyond the finite part.</summary>
        public static float EnemyPerWave => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.EnemyPerWave;

        /// <summary>The player +2 % a wave, at most +30 %.</summary>
        public static float PlayerPerWave => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.PlayerPerWave;
        public static float PlayerMax => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.PlayerMax;

        /// <summary>Boss Rush: the enemy +8 % a boss; the player gets nothing more (its support already goes to +40 %).</summary>
        public static float EnemyPerBoss => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.EnemyPerBoss;

        /// <summary>Survival: a mini boss every 5 waves, a main boss every 10 (instead of the mini boss); 10 waves finite.</summary>
        public static int MiniBossEvery => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.MiniBossEvery;
        public static int BossEvery => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.BossEvery;
        public static int SurvivalWaves => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.SurvivalWaves;

        /// <summary>Endless (the menu entry): the waves stop growing in number after this one (Defend's finite length).</summary>
        public static int DefendFiniteWaves => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.DefendFiniteWaves;

        /// <summary>Coins: 18 x 0.9^k a wave beyond (Boss Rush 60 x 0.9^k a boss), at most 600 a day over every mode.</summary>
        public static int WaveCoins => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.WaveCoins;
        public static int BossCoins => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.BossCoins;
        public static int DailyCap => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.DailyCap;

        public static double CoinDecay => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.CoinDecay;

        /// <summary>Badges at +10, +20, +30 waves and +5, +10 bosses.</summary>
        public static int[] WaveBadges => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.WaveBadges;
        public static int[] BossBadges => global::MachineBrigade.Sim.Content.SimTunables.Modes.EndlessRules.BossBadges;

        public static float EnemyScale(int steps, bool bosses = false) => 1f + Math.Max(0, steps) * (bosses ? EnemyPerBoss : EnemyPerWave);

        public static float PlayerScale(int steps, bool bosses = false) =>
            bosses ? 1f : 1f + Math.Min(PlayerMax, Math.Max(0, steps) * PlayerPerWave);

        /// <summary>The coins for the k-th wave (or boss) beyond the finite part (k from 0).</summary>
        public static int Coins(int k, bool bosses = false) => (int)Math.Round((bosses ? BossCoins : WaveCoins) * Math.Pow(CoinDecay, Math.Max(0, k)));

        /// <summary>What may still be paid today, given what the endless parts already paid today.</summary>
        public static int Capped(int coins, int paidToday) => Math.Max(0, Math.Min(coins, DailyCap - paidToday));

        /// <summary>The badge reached at exactly this many steps beyond, or 0.</summary>
        public static int BadgeAt(int steps, bool bosses = false) => Array.IndexOf(bosses ? BossBadges : WaveBadges, steps) >= 0 ? steps : 0;

        /// <summary>Survival: what a wave brings: 2 a main boss, 1 a mini boss, 0 none.</summary>
        public static int BossOfWave(int wave) => wave <= 0 ? 0 : wave % BossEvery == 0 ? 2 : wave % MiniBossEvery == 0 ? 1 : 0;
    }
}
