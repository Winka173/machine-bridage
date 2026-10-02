#nullable enable
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    public sealed partial class Vehicle
    {
        /// <summary>Prompt 28 H.9: its squad holds fire (an ambush, until the enemy is close or the squad is hit).</summary>
        public bool AiHoldFire { get; internal set; }

        /// <summary>Prompt 28 C.6: the target its squad concentrates on, and how strongly (the tactic's focus weight).</summary>
        public EntityId SquadFocus { get; internal set; }
        internal float SquadFocusWeight;

        /// <summary>Prompt 28 E.1: a tower's targeting mode (from the data's default; the player may change it).</summary>
        public TowerMode TowerMode { get; internal set; } = TowerMode.Default;
    }
}
