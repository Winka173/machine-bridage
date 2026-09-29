using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 20 N: the Boss Hunts' checkpoints, kept in the save so a run can be taken up again in a later sitting
    /// (the full hunt over many; the week's until the week ends), the full hunt's best total times (the leaderboard,
    /// on this device) and its first-clear reward.
    /// </summary>
    public static partial class PlayerProfile
    {
        /// <summary>A run's checkpoint as saved: the run it belongs to (kind, week, bosses) and the carry to start from.</summary>
        [Serializable]
        internal sealed class HuntSave
        {
            public string kind;
            public int week;
            public List<string> roster = new();
            public string map;
            public int defeated;
            public double time;
            public float cp;
            public int paid;
            public List<string> army = new();
            public List<float> health = new();
            public List<string> supports = new();
        }

        /// <summary>How many best times the full hunt keeps.</summary>
        public const int FullHuntBoard = 5;

        private static HuntSave HuntOf(string kind)
        {
            foreach (var h in D.hunts)
                if (h.kind == kind) return h;
            return null;
        }

        private static bool Same(IReadOnlyList<string> a, List<string> b)
        {
            if (a.Count != b.Count) return false;
            for (var i = 0; i < a.Count; i++)
                if (a[i] != b[i]) return false;
            return true;
        }

        /// <summary>Keeps a run's newest checkpoint (the week's hunt by its week; the full hunt's at any time).</summary>
        public static void SaveHuntCheckpoint(string kind, int week, IReadOnlyList<string> roster, BossRushCarry carry)
        {
            var old = HuntOf(kind);
            if (old != null) D.hunts.Remove(old);
            var save = new HuntSave
            {
                kind = kind, week = week, roster = new List<string>(roster), map = carry.Map, defeated = carry.Defeated, time = carry.TimeUsed,
                cp = carry.Cp, paid = Math.Max(carry.Paid, old != null && Same(roster, old.roster) ? old.paid : 0),
            };
            foreach (var (def, health) in carry.Army)
            {
                save.army.Add(def);
                save.health.Add(health);
            }
            save.supports.AddRange(carry.Supports);
            D.hunts.Add(save);
            Save();
        }

        /// <summary>The checkpoint to take a run up from, or null (none, another week's, or the bosses have changed since).</summary>
        public static BossRushCarry HuntCheckpoint(string kind, int week, IReadOnlyList<string> roster)
        {
            var h = HuntOf(kind);
            if (h == null || (kind == BossHunts.WeeklyKey && h.week != week) || !Same(roster, h.roster) || h.defeated >= roster.Count) return null;
            var carry = new BossRushCarry { Map = h.map, Defeated = h.defeated, TimeUsed = h.time, Cp = h.cp, Paid = h.paid, Checkpoint = true };
            for (var i = 0; i < h.army.Count && i < h.health.Count; i++) carry.Army.Add((h.army[i], h.health[i]));
            carry.Supports.AddRange(h.supports);
            return carry;
        }

        /// <summary>A sitting paid for the bosses up to <paramref name="defeated"/>: a later resume does not pay them again.</summary>
        public static void HuntPaidUpTo(string kind, int defeated)
        {
            if (HuntOf(kind) is not { } h || h.paid >= defeated) return;
            h.paid = defeated;
            Save();
        }

        public static void ClearHuntCheckpoint(string kind)
        {
            if (HuntOf(kind) is not { } h) return;
            D.hunts.Remove(h);
            Save();
        }

        /// <summary>The full hunt's best total times in seconds, best first.</summary>
        public static IReadOnlyList<float> FullHuntTimes => D.fullHuntTimes;

        /// <summary>A full clear's total time on the board; true when it is the new best.</summary>
        public static bool RecordFullHunt(float seconds)
        {
            var best = D.fullHuntTimes.Count == 0 || seconds < D.fullHuntTimes[0];
            D.fullHuntTimes.Add(seconds);
            D.fullHuntTimes.Sort();
            if (D.fullHuntTimes.Count > FullHuntBoard) D.fullHuntTimes.RemoveRange(FullHuntBoard, D.fullHuntTimes.Count - FullHuntBoard);
            Save();
            return best;
        }

        /// <summary>The full hunt's first-clear reward: true the first time only.</summary>
        public static bool ClaimFullHunt()
        {
            if (D.fullHuntPaid) return false;
            D.fullHuntPaid = true;
            Save();
            return true;
        }
    }
}
