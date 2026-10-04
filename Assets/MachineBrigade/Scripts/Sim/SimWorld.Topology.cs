#nullable enable
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim
{
    public sealed partial class SimWorld
    {
        private MapTopology? _topology;
        private EngagementFeasibility? _feasibility;

        /// <summary>
        /// AI MASTER sections 4-5 (lane P0-B): the battlefield's mobility domains, components, chokes and objective regions.
        /// Built on first use and cached; built again after the ground changes (a wall down, a wreck in a lane), at most every
        /// <c>ai.topology.rebuildSeconds</c> of battle time, so a replay builds it at the same moments. Reading it changes
        /// nothing in the battle.
        /// </summary>
        public MapTopology Topology
        {
            get
            {
                if (_topology == null)
                {
                    _topology = MapTopology.Build(this);
                    _topology.FirstBuild();
                    _feasibility = null;
                }
                else if (_topology.GridVersion != Grid.Version &&
                         Time - _topology.BuiltAt >= Content.SimTunables.Ai.Topology.RebuildSeconds)
                {
                    _topology = _topology.Rebuilt(this);
                    _feasibility = null;
                }
                return _topology;
            }
        }

        /// <summary>
        /// AI MASTER sections 6-8 (lane P0-B): can a unit deploy, reach an objective or enemy, or fire on one from ground it can
        /// reach. The same service serves buying (ProcurementDirector), boss and factory spawns, and (later) targeting.
        /// </summary>
        public EngagementFeasibility Feasibility
        {
            get
            {
                var topology = Topology;
                if (_feasibility == null || !ReferenceEquals(_feasibility.Map, topology)) _feasibility = new EngagementFeasibility(this, topology);
                return _feasibility;
            }
        }
    }
}
