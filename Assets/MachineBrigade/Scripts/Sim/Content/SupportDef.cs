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

        /// <summary>A drone circles the point: everything within Radius, stealth and hidden too, shows to the caller's side for Duration seconds.</summary>
        Scan,

        /// <summary>Count mines are scattered within Radius; each blows up for Damage (Blast radius) and clears itself after Duration seconds.</summary>
        Minefield,

        /// <summary>A light tower (Units[0], Units[1] from card rank UnitRank) is dropped on the point for Duration seconds. Never into the enemy camp.</summary>
        Tower,

        /// <summary>An anti-radiation missile on the enemy anti-air nearest the point within Radius: Damage, and knocked out for Duration seconds.</summary>
        Sead,

        /// <summary>
        /// Prompt 25 F2 batch C (ht03, ht10): up to Count self-seeking submunitions, the nearest distinct enemy
        /// targets within Radius each taking Damage (DronesOnly: flying drones only; otherwise ground vehicles).
        /// </summary>
        Homing,

        /// <summary>Prompt 25 F2 batch C (ht05): every friendly vehicle within Radius has its weapons refilled at once.</summary>
        Resupply,

        /// <summary>
        /// Prompt 25 F2 batch C (ht06): every enemy drone within Radius is downed at once, and the circle hides
        /// what is in it (as Smoke) for Duration seconds.
        /// </summary>
        JamStorm,

        /// <summary>
        /// Prompt 25 F2 batch C (ht09): every enemy artillery piece that fired within the last 10 s, anywhere
        /// within Radius of the point, takes Count rounds of Damage (Blast radius each).
        /// </summary>
        CounterBattery,
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

        /// <summary>
        /// Prompt 15 B: its rounds' penetration level (data "pen"; -1: its damage type's usual,
        /// <see cref="Armour.DefaultPenetration(DamageType)"/>). Its bombs and shells fall on the roof.
        /// </summary>
        public int Penetration
        {
            get => _penetration >= 0 ? _penetration : Armour.DefaultPenetration(DamageType);
            internal set => _penetration = Math.Min(value, ArmourLevels.Max);
        }

        private int _penetration = -1;

        /// <summary>Prompt 15 C.3: a thermobaric strike (more against structures, cages do not stop it).</summary>
        public bool Thermobaric { get; internal set; }
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

        /// <summary>
        /// Play-test 14: a call the player fills (0: <see cref="Units"/> as they are): units of <see cref="CallChoices"/> worth at
        /// most this many CP in all (base CP), the call's price in CP <see cref="CallPriceScale"/> times their total, rounded up.
        /// </summary>
        public float CallMaxCp { get; internal set; }

        public float CallPriceScale { get; internal set; } = 1.5f;

        public IReadOnlyList<string> CallChoices { get; internal set; } = Array.Empty<string>();

        /// <summary>The CP a filled call of units worth <paramref name="total"/> base CP costs.</summary>
        public int CallPrice(float total) => (int)Math.Ceiling(total * CallPriceScale - 1e-4);

        /// <summary>A Tower drop: from this card rank (0: never) it drops its second tower.</summary>
        public int UnitRank { get; internal set; }

        /// <summary>From this card rank (0: never) an airstrike's bomb line is <see cref="LineScale"/> times as long, with as many more bombs.</summary>
        public int LineRank { get; internal set; }

        public float LineScale { get; internal set; } = 1f;

        /// <summary>Prompt 25 F2 batch C: a Homing strike's targets are flying drones only, not ground vehicles.</summary>
        public bool DronesOnly { get; internal set; }
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
