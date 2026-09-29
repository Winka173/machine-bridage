#nullable enable

namespace MachineBrigade.Sim.Entities
{
    public sealed partial class Vehicle
    {
        /// <summary>
        /// Prompt 23 C.4: it came as a mission event's reinforcement: outside its side's army cap (the events keep a cap of
        /// their own). On the player's side it is the Meridian Accord's (F.4's mark; its own AI commands it).
        /// </summary>
        public bool Reinforcement { get; internal set; }

        /// <summary>F.4: an Accord reinforcement on the player's side.</summary>
        public bool Accord => Reinforcement && Team == 0 && Ally;

        /// <summary>D.2 and F.5: the enemy general driving it on the field (their id: varga, orlov ...), or null.</summary>
        public string? General { get; internal set; }
    }
}
