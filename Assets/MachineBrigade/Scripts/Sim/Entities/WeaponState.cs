#nullable enable
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>Per-mount firing state: its own cooldown, target, aim and salvo progress.</summary>
    internal sealed class WeaponState
    {
        public float Cooldown;
        public EntityId Target;

        /// <summary>World heading of a free mount (pintle gun, chin turret), in radians.</summary>
        public float Heading;

        /// <summary>Shots still to fire in the current salvo, and time until the next one.</summary>
        public int BurstLeft;
        public float BurstTimer;
        public EntityId BurstTarget;
        public System.Numerics.Vector2 BurstAim;

        /// <summary>The salvo was aimed at an aircraft: later rounds keep bursting in the air.</summary>
        public bool BurstFlying;
    }
}
