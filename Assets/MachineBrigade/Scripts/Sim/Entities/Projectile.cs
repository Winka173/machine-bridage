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

        /// <summary>Where the round was fired from (armour facing: which side of the target it strikes).</summary>
        public Vector2 Origin { get; set; }

        /// <summary>The damage this round is expected to do to its target (so other guns do not waste shots on it).</summary>
        public float Incoming { get; set; }
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

        /// <summary>A guided round that simply failed (lost lock at long range): it lands off target by <see cref="Miss"/>.</summary>
        public bool Failed { get; set; }

        /// <summary>Damage multiplier: machine-gun rounds carry the damage of the pause between bursts.</summary>
        public float DamageScale { get; set; } = 1f;

        /// <summary>The vehicle that fired it (it may have died since): its equipment's hit effects.</summary>
        public Vehicle? Shooter { get; set; }

        /// <summary>Fired from the shooter's main weapon (hit traits apply to it).</summary>
        public bool Main { get; set; }

        /// <summary>A tandem warhead: no active protection, reactive block or barrier stops it.</summary>
        public bool Tandem { get; set; }

        /// <summary>A heavy round (Overpressure Chamber, Heavy Round): it also bursts over this radius.</summary>
        public float ExtraSplash { get; set; }

        /// <summary>A bounce or a drone from equipment: it sets off no further hit traits.</summary>
        public bool NoProc { get; set; }

        /// <summary>A ricochet: it strikes its target only (no blast, no piercing, no bomblets).</summary>
        public bool Bounce { get; set; }

        /// <summary>Carries no bomblets (a cluster salvo's rounds after its first few, see Cluster Warhead).</summary>
        public bool NoCluster { get; set; }

        /// <summary>
        /// The boss part it was fired at (its index in the boss's parts), or -1 for the body: a direct
        /// hit strikes the part while it stands, and its blast lands on the body only.
        /// </summary>
        public int Part { get; set; } = -1;
    }
}
