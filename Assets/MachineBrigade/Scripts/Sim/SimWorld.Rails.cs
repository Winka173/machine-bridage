#nullable enable

namespace MachineBrigade.Sim
{
    /// <summary>Prompt 33 L5: the railway lines and their trains and level crossings (<see cref="Movement.RailSystem"/>).</summary>
    public sealed partial class SimWorld
    {
        private Movement.RailSystem? _rails;

        /// <summary>The rails, their trains and crossings (built with the world, before its first step: the crossings are prebuilt ground states).</summary>
        public Movement.RailSystem Rails => _rails ??= new Movement.RailSystem(this);
    }
}
