#nullable enable
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim
{
    public sealed partial class SimWorld
    {
        private GameplayTopology? _gameplay;
        private MapTelemetry? _mapTelemetry;

        /// <summary>The lane map as it stands, without the rebuild check of <see cref="Lanes"/> (the gameplay topology reads it).</summary>
        internal LaneMap LanesNoRebuild => _lanes;

        /// <summary>
        /// Map / visual / audio W1-A (spec C-P): the battlefield's gameplay topology on the AI MASTER topology. Built on first use
        /// and again when the topology or the lane map was rebuilt; it never forces either rebuild (it uses the topology the world
        /// has and the lane map as it stands), so reading it moves no rebuild moment. The quick load gates (spec BW) run at the
        /// first build; failures go to <see cref="MapTelemetry"/>, never an exception.
        /// </summary>
        public GameplayTopology GameplayTopology
        {
            get
            {
                var topology = _topology ?? Topology;
                if (_gameplay != null && ReferenceEquals(_gameplay.Map, topology) && _gameplay.LanesBuild == _lanes.Builds) return _gameplay;
                var first = _gameplay == null;
                _gameplay = GameplayTopology.Build(this, topology, _lanes, (_gameplay?.Generation ?? 0) + 1);
                if (first)
                    foreach (var g in _gameplay.LoadGates)
                        if (!g.Pass) MapTelemetry.LoadGateFailures.Add(g.ToString());
                return _gameplay;
            }
        }

        /// <summary>Spec CA / prompt 64: the map telemetry counters (reads only).</summary>
        public MapTelemetry MapTelemetry => _mapTelemetry ??= new MapTelemetry();
    }
}
