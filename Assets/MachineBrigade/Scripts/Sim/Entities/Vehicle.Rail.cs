#nullable enable

namespace MachineBrigade.Sim.Entities
{
    /// <summary>Prompt 33 L5: a train on its rail (<see cref="Navigation.RailSpline"/>): which line, how far along, which way.</summary>
    public sealed partial class Vehicle
    {
        /// <summary>The rail it runs on (an index into the map's rails), or -1: it is not on a rail.</summary>
        internal int Rail = -1;

        /// <summary>Its middle's place along the rail (metres) and the way it last ran (+1 towards growing s, -1 back).</summary>
        internal float RailS;
        internal int RailDir = 1;

        /// <summary>When it was last pushed off a rail by a train (a boss train's ram hurts once a pass).</summary>
        internal double RailPushedAt = double.NegativeInfinity;

        /// <summary>When it was last told to get off the line before a train (its emergency move).</summary>
        internal double RailToldAt = double.NegativeInfinity;

        /// <summary>A train held on its rail: the rail system moves it, nothing else does.</summary>
        public bool OnRail => Rail >= 0;
    }
}
