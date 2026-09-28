using System.Collections.Generic;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>What a finished battle pays out, before it is claimed.</summary>
    public sealed class MatchReward
    {
        public int Coins { get; set; }
        public int Xp { get; set; }

        /// <summary>Stars won (campaign missions only; 0 otherwise).</summary>
        public int Stars { get; set; }

        public string MissionId { get; set; }

        /// <summary>The tier the mission was fought at (0 normal, 1 heroic, 2 iron).</summary>
        public int Tier { get; set; }

        /// <summary>Cards this battle unlocks (a campaign mission's first win).</summary>
        public List<string> Unlocks { get; } = new();

        /// <summary>Blueprints the elites destroyed dropped (a card id each), paid with the rest.</summary>
        public List<string> Blueprints { get; } = new();

        public bool Claimed { get; private set; }

        /// <summary>Ranks reached while claiming (each already paid its coin bonus).</summary>
        public List<int> RanksGained { get; } = new();

        /// <summary>Pays the reward into the profile; <paramref name="multiplier"/> 2 after a rewarded ad. Only once.</summary>
        public void Claim(int multiplier = 1)
        {
            if (Claimed) return;
            Claimed = true;
            PlayerProfile.AddCoins(Coins * multiplier);
            RanksGained.AddRange(PlayerProfile.AddXp(Xp));
            foreach (var id in Unlocks) PlayerProfile.Unlock(id);
            foreach (var id in Blueprints) PlayerProfile.AddBlueprints(id, 1);
            if (MissionId != null) PlayerProfile.RecordMission(MissionId, Stars, Tier);
        }
    }

    /// <summary>
    /// Pay-outs. Winning pays best, harder AI pays more, and kills add a little; a loss still
    /// pays something so a bad run is never wasted. Campaign missions pay their full reward on
    /// the first win and a third of it on replays, plus a bonus per star.
    /// </summary>
    public static class Rewards
    {
        public static float DifficultyFactor(AiDifficulty difficulty) => difficulty switch
        {
            AiDifficulty.Easy => 0.7f,
            AiDifficulty.Hard => 1.45f,
            _ => 1f,
        };

        /// <param name="outcome">1 win, 0 draw, -1 loss.</param>
        public static MatchReward Quick(AiDifficulty difficulty, int outcome, int kills, float minutes)
        {
            var coins = outcome > 0 ? 120f : outcome == 0 ? 70f : 40f;
            coins += Mathf.Min(kills, 120) * 1.5f;
            // Longer battles pay a little more, up to a quarter hour.
            coins += Mathf.Clamp(minutes, 0f, 15f) * 4f;
            coins *= DifficultyFactor(difficulty);
            return new MatchReward { Coins = Mathf.RoundToInt(coins), Xp = Mathf.RoundToInt(coins * 0.8f) };
        }

        public static MatchReward Survival(AiDifficulty difficulty, int waves, int kills)
        {
            var coins = (30f + waves * 18f + Mathf.Min(kills, 150) * 1.5f) * DifficultyFactor(difficulty);
            return new MatchReward { Coins = Mathf.RoundToInt(coins), Xp = Mathf.RoundToInt(coins * 0.8f) };
        }

        /// <summary>Stars for a won mission: one for the win, one for speed, one for few losses.</summary>
        /// <summary>Stars: one for the win, one for the time, one for the mission's own challenge (or for few losses).</summary>
        public static int Stars(MissionDef mission, bool won, float seconds, int losses, bool challenge = true)
        {
            if (!won) return 0;
            var stars = 1;
            if (mission.StarTime <= 0f || seconds <= mission.StarTime) stars++;
            if (mission.Challenge != null ? challenge : mission.StarLosses < 0 || losses <= mission.StarLosses) stars++;
            return stars;
        }

        /// <summary>
        /// The elites destroyed (prompt 8 H.5): a small bounty each, for the first few (the data's
        /// elites.bountyCap, so a long battle's pay stays near the curve prompt 7 set), and a small
        /// chance each of a blueprint of the elite's base card (a card the player can own). Rows for
        /// the result card. <paramref name="seed"/> makes the drops repeatable.
        /// </summary>
        public static void AddElites(MatchReward reward, List<(string label, string value)> rows, IReadOnlyList<string> baseCards,
            Catalog catalog, int seed)
        {
            if (reward == null || baseCards.Count == 0) return;
            var rules = catalog.Elites;
            var paid = Mathf.Min(baseCards.Count, rules.BountyCap);
            var coins = paid * rules.Coins;
            reward.Coins += coins;
            rows?.Add((Hud.Strings.Get("result.elites"), Hud.Strings.Format("result.elitesValue", baseCards.Count, coins)));
            var random = new System.Random(seed);
            foreach (var card in baseCards)
            {
                if (random.NextDouble() >= rules.BlueprintChance || System.Array.IndexOf(MatchSettings.AllVehicles, card) < 0) continue;
                reward.Blueprints.Add(card);
                rows?.Add((Hud.Strings.Get("result.blueprint"), Hud.Strings.Card(card)));
            }
        }

        /// <summary>Reward multiplier of a mission tier: Heroic pays half as much again, Iron double.</summary>
        public static float TierPay(int tier) => tier switch { 1 => 1.5f, 2 => 2f, _ => 1f };

        public static MatchReward Mission(MissionDef mission, bool won, float seconds, int losses, bool challenge = true, int tier = 0)
        {
            var stars = Stars(mission, won, seconds, losses, challenge);
            // A tier's first win pays in full, like the mission's first win.
            var first = won && (!PlayerProfile.Completed(mission.Id) || PlayerProfile.MissionTier(mission.Id) < tier);
            var reward = new MatchReward { MissionId = mission.Id, Stars = stars, Tier = tier };
            if (!won)
            {
                reward.Coins = 30;
                reward.Xp = 40;
                return reward;
            }
            var share = first ? 1f : 0.35f;
            reward.Coins = Mathf.RoundToInt((mission.RewardCoins * share + 50 * stars) * TierPay(tier));
            reward.Xp = Mathf.RoundToInt((mission.RewardXp * share + 30 * stars) * TierPay(tier));
            if (!PlayerProfile.Completed(mission.Id)) reward.Unlocks.AddRange(mission.Unlocks);
            return reward;
        }
    }
}
