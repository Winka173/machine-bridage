#nullable enable
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>Per-mount firing state: its own cooldown, target, aim and salvo progress.</summary>
    internal sealed class WeaponState
    {
        public float Cooldown;

        /// <summary>Artillery walking its fire onto a target: which one, and how many rounds it has put near it.</summary>
        public EntityId BracketTarget;
        public int BracketShots;

        /// <summary>Rounds left, or -1 for a weapon with unlimited ammunition.</summary>
        public int Ammo = -1;

        /// <summary>An empty magazine being reloaded in place: seconds still to go (0: not reloading).</summary>
        public float ReloadLeft;
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

        /// <summary>Damage of each round of the salvo under way against a plain round (Twin Feed spreads its bonus over the extra round).</summary>
        public float BurstScale = 1f;

        /// <summary>
        /// Machine guns fire in bursts: rounds left in the current run of fire (0: pausing, or not
        /// started), and whether the gun has fired yet (its first run starts after a random delay).
        /// </summary>
        public int RunLeft;
        public bool Started;

        /// <summary>A charged weapon powering up: seconds still to go (0: not charging).</summary>
        public float ChargeLeft;
    }
}
