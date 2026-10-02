#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim
{
    /// <summary>
    /// Prompt 31 L3: the battlefield's prebuilt ground states (<see cref="Navigation.NavStates"/>): a mission's sites are built
    /// as it loads (<see cref="BuildNavSites"/>), checked against its anchors, and switched by its events at a tick boundary.
    /// </summary>
    public sealed partial class SimWorld
    {
        private NavStates? _navStates;

        /// <summary>The prebuilt ground states (made on first use; a battle without sites never steps or mixes them).</summary>
        public NavStates NavStates => _navStates ??= new NavStates(Grid);

        /// <summary>The refusals of the last <see cref="BuildNavSites"/> check (the stuck report and the tests read them).</summary>
        public IReadOnlyList<string> NavSiteProblems { get; private set; } = Array.Empty<string>();

        /// <summary>
        /// Builds a mission's sites (campaign.json "navStates") and checks every state: the anchors are the sides' rallies,
        /// the map's capture points and <paramref name="extra"/> (the mission's goal points). Before the first step only.
        /// </summary>
        public void BuildNavSites(IReadOnlyList<NavSiteDef> sites, IEnumerable<Vector2>? extra = null)
        {
            if (sites.Count == 0 || NavStates.Locked) return;
            var added = 0;
            foreach (var s in sites)
            {
                if (NavStates.TryGet(s.Id, out _)) continue;
                NavStates.Define(s);
                added++;
            }
            if (added == 0) return;
            var anchors = new List<Vector2>();
            foreach (var team in Map.Teams) anchors.Add(team.Rally);
            foreach (var p in Map.Points) anchors.Add(p.Position);
            if (extra != null) anchors.AddRange(extra);
            NavSiteProblems = NavStates.Validate(anchors);
        }

        /// <summary>
        /// A fixed defence standing on prebuilt ground (a pod's tower on its landing site): its own anchor is lifted, so the
        /// site's state alone holds the ground (and opens it when the site goes back).
        /// </summary>
        internal void ReleaseGround(Entities.Vehicle v)
        {
            if (!v.BlocksRoutes) return;
            Grid.RemoveBlocker(v.Position, StaticFootprint(v.Def), StaticFootprint(v.Def), ObstacleClearance);
            v.BlocksRoutes = false;
        }
    }
}
