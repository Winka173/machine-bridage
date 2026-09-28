using System;
using System.Globalization;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The weekly fortress: every week (ISO weeks, UTC) a different battlefield's fortress. Rings
    /// broken in one attack stay broken for the rest of the week, so it can be taken over several
    /// sittings; the first win of the week pays <see cref="Reward"/>.
    /// </summary>
    public static class WeeklyFortress
    {
        /// <summary>The first win of the week pays this (operations.json "weekly", one ledger with the weekly operation).</summary>
        public static int Reward => Operations.Data.WeeklyFortressReward;

        /// <summary>This week, as year x 100 + ISO week number.</summary>
        public static int Week
        {
            get
            {
                var now = DateTime.UtcNow;
                return ISOWeek.GetYear(now) * 100 + ISOWeek.GetWeekOfYear(now);
            }
        }

        /// <summary>This week's battlefield (a different one each week, round all of them).</summary>
        public static string MapId
        {
            get
            {
                var maps = MatchSettings.AllMaps;
                var week = Week;
                var index = (week / 100 * 53 + week % 100) % maps.Length;
                return maps[index].Id;
            }
        }
    }
}
