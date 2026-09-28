using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>A battle of the Operations mode (prompt 6): its tier, its mutators, and whether it is this week's operation.</summary>
    internal sealed class OperationRun
    {
        public string Mission;
        public int Tier;
        public readonly List<MutatorDef> Mutators = new();
        public bool Weekly;

        /// <summary>A mutator's weather, or null (the mission's own).</summary>
        public string Weather
        {
            get
            {
                foreach (var m in Mutators)
                    if (m.Weather != null) return m.Weather;
                return null;
            }
        }
    }

    /// <summary>
    /// The Operations mode (prompt 6). It replays the chapters' big operations and the notable
    /// story battles once they are won in the campaign, on four tiers: Normal, Heroic and Iron,
    /// and Legend once the campaign's last operation is won. A won battle is scored on its time,
    /// losses and the HQ's health, and the best score and time are kept per tier. Each week
    /// brings one operation with two mutators, drawn deterministically from the week number.
    /// </summary>
    internal static class Operations
    {
        private static OperationsData _data;

        public static OperationsData Data => _data ??= OperationsData.FromJson(Resources.Load<TextAsset>("Data/operations").text);

        public const int Legend = 3;

        public static OperationTier Tier(int tier) => Data.Tiers[Mathf.Clamp(tier, 0, Data.Tiers.Count - 1)];

        /// <summary>The chapters' big operations, in campaign order.</summary>
        public static IReadOnlyList<MissionDef> Big
        {
            get
            {
                var list = new List<MissionDef>();
                foreach (var m in Campaign.All)
                    if (m.Operation) list.Add(m);
                return list;
            }
        }

        /// <summary>Everything the mode offers: the big operations, then the notable story battles, in campaign order.</summary>
        public static IReadOnlyList<MissionDef> Replayable
        {
            get
            {
                var list = new List<MissionDef>(Big);
                foreach (var m in Campaign.All)
                    if (m.Replay && !m.Operation) list.Add(m);
                return list;
            }
        }

        /// <summary>Open once won in the campaign.</summary>
        public static bool Unlocked(MissionDef mission) => Progression.TestUnlockAll || PlayerProfile.Completed(mission.Id);

        /// <summary>The Legend tier: open once the campaign's last big operation is won.</summary>
        public static bool LegendOpen
        {
            get
            {
                if (Progression.TestUnlockAll) return true;
                var big = Big;
                return big.Count > 0 && PlayerProfile.Completed(big[big.Count - 1].Id);
            }
        }

        public static bool TierOpen(int tier) => tier < Legend || LegendOpen;

        /// <summary>This week's operation and its two mutators, or null while there are no operations.</summary>
        public static (MissionDef mission, MutatorDef a, MutatorDef b)? ThisWeek => Week(WeeklyFortress.Week);

        public static (MissionDef mission, MutatorDef a, MutatorDef b)? Week(int week)
        {
            var big = Big;
            if (Data.Weekly(week, big.Count) is not { } entry) return null;
            return (big[entry.operation], entry.a, entry.b);
        }

        /// <summary>A run of <paramref name="mission"/> at <paramref name="tier"/>; this week's operation brings its mutators.</summary>
        public static OperationRun Run(MissionDef mission, int tier, bool weekly)
        {
            var run = new OperationRun { Mission = mission.Id, Tier = tier, Weekly = weekly };
            if (weekly && ThisWeek is { } week && week.mission.Id == mission.Id)
            {
                run.Mutators.Add(week.a);
                run.Mutators.Add(week.b);
            }
            else run.Weekly = false;
            return run;
        }
    }
}
