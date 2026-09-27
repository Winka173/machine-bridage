#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>How a piece of damage arrived: what equipment modifiers and resistances look at.</summary>
    internal enum HitKind
    {
        /// <summary>Unknown or environmental (a cook-off, a scripted demolition): no modifiers.</summary>
        None,

        /// <summary>A round striking what it was aimed at.</summary>
        Direct,

        /// <summary>A blast round a weapon's impact.</summary>
        Splash,

        /// <summary>A railgun slug going on through.</summary>
        Pierce,

        /// <summary>A mine going off.</summary>
        Mine,

        /// <summary>Called fire support (artillery barrage, air strike).</summary>
        Strike,

        /// <summary>A fire burning on it (already worked out from the hit that lit it).</summary>
        Burn,

        /// <summary>A share of an ally's damage taken over (Guardian Link).</summary>
        Redirect,
    }

    /// <summary>Who dealt a piece of damage, with what, from where and how.</summary>
    internal readonly struct HitInfo
    {
        public HitInfo(Vehicle? attacker, int team, WeaponDef? weapon, Vector2 origin, HitKind kind, bool indirect, Projectile? projectile = null)
        {
            Attacker = attacker;
            Team = team;
            Weapon = weapon;
            Origin = origin;
            Kind = kind;
            Indirect = indirect;
            Projectile = projectile;
        }

        /// <summary>The vehicle that fired (it may have died since); null for strikes, mines and the environment.</summary>
        public Vehicle? Attacker { get; }

        public int Team { get; }
        public WeaponDef? Weapon { get; }
        public Vector2 Origin { get; }
        public HitKind Kind { get; }

        /// <summary>From above: artillery, bombs, drones, called fire.</summary>
        public bool Indirect { get; }

        public Projectile? Projectile { get; }

        public bool Known => Kind != HitKind.None;

        public HitInfo As(HitKind kind) => new(Attacker, Team, Weapon, Origin, kind, Indirect, Projectile);

        public static HitInfo Of(Projectile p, HitKind kind) => new(p.Shooter, p.OwnerTeam, p.Weapon, p.Origin, kind, p.Weapon.Indirect, p);
    }
}
