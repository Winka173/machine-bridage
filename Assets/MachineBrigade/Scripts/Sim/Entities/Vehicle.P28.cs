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

        /// <summary>Prompt 28 H.1: force groups its squad's tactic hunts first (SEAD first: anti-air; decapitation: support, artillery).</summary>
        internal System.Collections.Generic.IReadOnlyList<ForceGroup>? SquadTargets;

        /// <summary>Prompt 28 D.4: the heading a standing vehicle turns its front to (the biggest threat); null: none.</summary>
        internal float? FaceHeading;

        /// <summary>Prompt 28 E.1: a tower's targeting mode (from the data's default; the player may change it).</summary>
        public TowerMode TowerMode { get; internal set; } = TowerMode.Default;
    }
}
