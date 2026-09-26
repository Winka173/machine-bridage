#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>
    /// A shot in flight. It lands on a fixed aim point after its travel time, so a fast
    /// target can dodge slow shells and damage timing matches what the player sees.
    /// </summary>
    internal sealed class Projectile
    {
        public Projectile(EntityId owner, int ownerTeam, WeaponDef weapon, Vector2 aimPoint, EntityId target, float travelTime,
            bool targetFlying = false)
        {
            TargetFlying = targetFlying;
            Owner = owner;
            OwnerTeam = ownerTeam;
            Weapon = weapon;
            AimPoint = aimPoint;
            Target = target;
            TimeLeft = travelTime;
        }

        public EntityId Owner { get; }
        public int OwnerTeam { get; }
        public WeaponDef Weapon { get; }
        public Vector2 AimPoint { get; }
        public EntityId Target { get; }
        public float TimeLeft { get; set; }

        /// <summary>Aimed at an aircraft: ground splash cannot reach it and the shot bursts in the air.</summary>
        public bool TargetFlying { get; }

        /// <summary>A guided round fired into (or out of) an enemy jammer's bubble: it loses lock and misses.</summary>
        public bool Jammed { get; set; }

        /// <summary>How far off a decoyed or jammed guided round lands from its target.</summary>
        public Vector2 Miss { get; set; }
    }
}
