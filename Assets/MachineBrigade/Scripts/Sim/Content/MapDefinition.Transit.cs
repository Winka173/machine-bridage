#nullable enable
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Prompt 33 L4-L5: the battlefield's own routes for big ships and trains (map data "seaRoutes", "rails").</summary>
    public sealed partial class MapDefinition
    {
        /// <summary>
        /// Prompt 33 L4: the big ships' route graph as the map file gives it (Tools/maps/transit.py), or null (a sea without
        /// one gets the graph built from its lanes: <see cref="SeaRouteGraph.FromSea"/>).
        /// </summary>
        public SeaRouteGraph? SeaRoutes { get; internal set; }
    }
}
