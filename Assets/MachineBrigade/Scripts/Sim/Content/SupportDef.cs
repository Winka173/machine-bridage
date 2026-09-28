#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    public enum SupportKind
    {
        /// <summary>Shells rain on a circle for a few seconds.</summary>
        Barrage,

        /// <summary>A jet drops a line of bombs along the chosen direction.</summary>
        Airstrike,

        /// <summary>One huge blast after a long warning.</summary>
        CruiseMissile,

        /// <summary>A cloud that hides everything inside it.</summary>
        Smoke,

        /// <summary>Restores health to friendly vehicles in a circle over a few seconds.</summary>
        Repair,

        /// <summary>Knocks out enemy ground vehicles in the circle for Duration seconds.</summary>
        Emp,

        /// <summary>Friendly vehicles in the circle take Damage (0-1) less damage for Duration seconds.</summary>
        ShieldDome,

        /// <summary>Units are dropped on the point.</summary>
        Reinforce,

        /// <summary>An aircraft (Units) joins the fight for Duration seconds, then leaves.</summary>
        Escort,
    }

    /// <summary>
    /// A fire-support card (game plan section 5). Every strike is telegraphed and lands after a
    /// delay, so both sides can react.
    /// </summary>
    public sealed class SupportDef
    {
        public SupportDef(string id, SupportKind kind, int cpCost, float cooldown, float delay, float radius,
            int count, float duration, float damage, DamageType damageType, ExplosionTier tier, float length = 0f,
            float blastRadius = 0f)
        {
            Id = Guard.Id(id);
            Kind = kind;
            CpCost = cpCost >= 0 ? cpCost : throw new ArgumentException($"Support '{id}': cp must not be negative.");
            Cooldown = Guard.NonNegative(cooldown, id, nameof(cooldown));
            Delay = Guard.NonNegative(delay, id, nameof(delay));
            Radius = Guard.Positive(radius, id, nameof(radius));
            Count = count >= 1 ? count : throw new ArgumentException($"Support '{id}': count must be at least 1.");
            Duration = Guard.NonNegative(duration, id, nameof(duration));
            Damage = Guard.NonNegative(damage, id, nameof(damage));
            DamageType = damageType;
            Tier = tier;
            Length = Guard.NonNegative(length, id, nameof(length));
            BlastRadius = blastRadius > 0f ? blastRadius : Math.Min(radius, 6f);
        }

        public string Id { get; }
        public SupportKind Kind { get; }
        public int CpCost { get; }

        /// <summary>Seconds before the same side may call this support again.</summary>
        public float Cooldown { get; }

        /// <summary>Telegraph time between the call and the first impact.</summary>
        public float Delay { get; }

        /// <summary>Target circle radius (barrage, smoke, repair, cruise missile) or half-width of a bomb line.</summary>
        public float Radius { get; }

        /// <summary>Shells, bombs or healing ticks.</summary>
        public int Count { get; }

        /// <summary>Seconds over which the impacts are spread (smoke: how long it lingers).</summary>
        public float Duration { get; }

        /// <summary>Damage per impact, or total health restored as a fraction of max HP for Repair.</summary>
        public float Damage { get; }

        public DamageType DamageType { get; }
        public ExplosionTier Tier { get; }

        /// <summary>Length of an airstrike's bomb line.</summary>
        public float Length { get; }

        /// <summary>Radius of each individual blast.</summary>
        public float BlastRadius { get; }

        /// <summary>Whether the call needs a direction as well as a point.</summary>
        public bool IsLine => Kind == SupportKind.Airstrike;

        /// <summary>A single-use item bought with coins: it costs no CP and is not in the deck.</summary>
        public bool Consumable { get; internal set; }

        /// <summary>Only battle events call it (a neutral bomber raid); never a card.</summary>
        public bool EventOnly { get; internal set; }

        /// <summary>Vehicles dropped (Reinforce) or flown in (Escort).</summary>
        public IReadOnlyList<string> Units { get; internal set; } = Array.Empty<string>();
    }

    /// <summary>An objective circle from the map (Conquest).</summary>
    public readonly struct CapturePointDef
    {
        public CapturePointDef(string id, string name, System.Numerics.Vector2 position, float radius,
            IReadOnlyList<HardpointDef>? outpost = null)
        {
            Id = id;
            Name = name;
            Position = position;
            Radius = radius;
            Outpost = outpost ?? Array.Empty<HardpointDef>();
        }

        /// <summary>Hardpoints beside the point for an outpost (1-2, tower slots), where the map has them.</summary>
        public IReadOnlyList<HardpointDef> Outpost { get; }

        public string Id { get; }

        /// <summary>Localisation key suffix or display name, for example "farm".</summary>
        public string Name { get; }

        public System.Numerics.Vector2 Position { get; }
        public float Radius { get; }
    }
}
