using System.Linq;
using MachineBrigade.Game.Effects;
using NUnit.Framework;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The troop transport's route (the owner's play test, 2026-09-29): it must not cross the whole map
    /// and vanish half-way. It comes in from the edge nearest the drop, is over the drop, turns home
    /// and is removed only once it is past the map's edge.
    /// </summary>
    public sealed class TransportRouteTests
    {
        private const float Half = 150f;

        private static readonly Vector3[] Landings =
        {
            new(0f, 0f, 0f), new(100f, 0f, 20f), new(-130f, 0f, -140f), new(20f, 0f, 140f), new(-60f, 0f, 90f),
        };

        private static float Outside(Vector3 p) => Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.z)) - Half;

        [Test]
        public void ItAppearsAndLeavesBeyondTheEdge([ValueSource(nameof(Landings))] Vector3 landing)
        {
            var route = AirDrops.SampleRoute(Half, landing, release: 10f, now: 0f, step: 0.05f);
            Assert.GreaterOrEqual(Outside(route[0]), 30f, "it comes in from beyond the edge");
            Assert.GreaterOrEqual(Outside(route[^1]), 30f, "it is removed only once past the edge");
        }

        [Test]
        public void ItPassesOverTheDrop([ValueSource(nameof(Landings))] Vector3 landing)
        {
            var route = AirDrops.SampleRoute(Half, landing, release: 10f, now: 0f, step: 0.02f);
            var closest = route.Min(p => new Vector2(p.x - landing.x, p.z - landing.z).magnitude);
            Assert.Less(closest, 2.5f, "over the landing point");
        }

        [Test]
        public void ItNeverCrossesTheMap([ValueSource(nameof(Landings))] Vector3 landing)
        {
            // From the nearest edge it goes no further in than the drop plus its turn, then home the same way.
            var route = AirDrops.SampleRoute(Half, landing, release: 10f, now: 0f, step: 0.05f);
            var depth = Half - Mathf.Max(Mathf.Abs(landing.x), Mathf.Abs(landing.z));
            var deepest = route.Max(p => Half - Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.z)));
            Assert.LessOrEqual(deepest, depth + 33f, "no further in than the drop and its turn");
        }

        [Test]
        public void AShortDeliveryStillArrivesInTime()
        {
            // Two seconds from the order to the drop in the middle of the map: it comes in fast, not from half-way.
            var route = AirDrops.SampleRoute(Half, Vector3.zero, release: 2f, now: 0f, step: 0.05f);
            Assert.GreaterOrEqual(Outside(route[0]), 0f, "it still appears at or beyond the edge");
        }
    }
}
