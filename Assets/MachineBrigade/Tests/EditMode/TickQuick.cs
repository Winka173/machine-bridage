using System.Linq;
using System.Text;
using NUnit.Framework;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// A quick tick-budget reading (prompt 12): two 40 s battles with 48 enemies and one with 64
    /// (TickBudgetTests.Measure; the full sweep is TheEnemyCeilingFitsTheTickBudget), to compare the
    /// sim before and after a change on one machine. Run by name.
    /// </summary>
    public class TickQuick
    {
        [Test, Explicit("measurement"), Timeout(3600000)]
        public void Measure()
        {
            TickBudgetTests.Measure(24, 1, 5f);
            var parts = new StringBuilder();
            var runs = new[] { TickBudgetTests.Measure(48, 3, 40f, parts), TickBudgetTests.Measure(48, 4, 40f, parts), TickBudgetTests.Measure(64, 3, 40f, parts) };
            Debug.Log("TICKQUICK " + string.Join(" | ", runs.Select(r => $"mean {r.mean:0.000} p99 {r.p99:0.000} alive {r.alive}")) + "\n" + parts);
        }
    }
}
