#nullable enable
using System;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>What a vehicle skill does when it fires.</summary>
    public enum SkillKind
    {
        /// <summary>Restores Amount of max health over Duration.</summary>
        Repair,

        /// <summary>Takes Amount (0-1) less damage for Duration.</summary>
        Shield,

        /// <summary>Pops a smoke cloud of Radius around itself for Duration.</summary>
        Smoke,

        /// <summary>Drives Amount times faster and fires 1.3x as often for Duration.</summary>
        Overdrive,

        /// <summary>Fires Amount times as often for Duration.</summary>
        Barrage,

        /// <summary>Guided missiles and drones aimed at it miss for Duration.</summary>
        Flares,

        /// <summary>Calls in Count vehicles of Unit around itself.</summary>
        Summon,

        /// <summary>Stuns enemy ground vehicles within Radius for Duration: no driving, no firing.</summary>
        Emp,
    }

    /// <summary>When a skill fires (checked every step; then it waits out its cooldown).</summary>
    public enum SkillTrigger
    {
        /// <summary>As soon as it is ready.</summary>
        Always,

        /// <summary>Health below Threshold (a fraction of max).</summary>
        HpBelow,

        /// <summary>Hit within the last second.</summary>
        UnderFire,

        /// <summary>A visible enemy inside its main weapon's range (or Radius, if set).</summary>
        EnemyInRange,

        /// <summary>A guided missile or drone is flying at it.</summary>
        MissileIncoming,
    }

    /// <summary>
    /// A special ability of elite units and bosses. The simulation uses them on its own when the
    /// trigger condition is met, for the player's units as much as the enemy's.
    /// </summary>
    public sealed class SkillDef
    {
        public SkillDef(string id, SkillKind kind, SkillTrigger trigger, float threshold, float cooldown, float duration,
            float amount, float radius, int count, string? unit, bool once)
        {
            Id = Guard.Id(id);
            Kind = kind;
            Trigger = trigger;
            Threshold = Guard.NonNegative(threshold, id, nameof(threshold));
            Cooldown = Guard.NonNegative(cooldown, id, nameof(cooldown));
            Duration = Guard.NonNegative(duration, id, nameof(duration));
            Amount = Guard.NonNegative(amount, id, nameof(amount));
            Radius = Guard.NonNegative(radius, id, nameof(radius));
            Count = count >= 0 ? count : throw new ArgumentException($"Skill '{id}': count must not be negative.");
            Unit = unit;
            Once = once;
            if (kind == SkillKind.Summon && (unit == null || count < 1))
                throw new ArgumentException($"Skill '{id}': a summon needs a unit and a count.");
        }

        public string Id { get; }
        public SkillKind Kind { get; }
        public SkillTrigger Trigger { get; }

        /// <summary>Health fraction for <see cref="SkillTrigger.HpBelow"/>.</summary>
        public float Threshold { get; }

        public float Cooldown { get; }
        public float Duration { get; }

        /// <summary>Strength: heal fraction, damage reduction, speed or fire-rate multiplier.</summary>
        public float Amount { get; }

        public float Radius { get; }
        public int Count { get; }

        /// <summary>Vehicle id a summon calls in.</summary>
        public string? Unit { get; }

        /// <summary>Fires at most once per vehicle: a boss phase.</summary>
        public bool Once { get; }
    }

    /// <summary>An effect a support vehicle spreads around itself.</summary>
    public sealed class AuraDef
    {
        public AuraDef(float radius, float rate)
        {
            Radius = Guard.Positive(radius, "aura", nameof(radius));
            Rate = Guard.Positive(rate, "aura", nameof(rate));
        }

        public float Radius { get; }

        /// <summary>Repair: fraction of max health per second. Rearm: seconds per round.</summary>
        public float Rate { get; }
    }

    /// <summary>
    /// An active protection system (Trophy, Afganit): shoots down incoming missiles, drones and
    /// direct-fire rockets aimed at anything within <see cref="Radius"/> of the vehicle. It holds
    /// <see cref="Charges"/> interceptors, each reloaded <see cref="Recharge"/> seconds after use.
    /// </summary>
    public sealed class ApsDef
    {
        public ApsDef(float radius, int charges, float recharge)
        {
            Radius = Guard.Positive(radius, "aps", nameof(radius));
            Charges = charges >= 1 ? charges : throw new ArgumentException("aps: charges must be at least 1.");
            Recharge = Guard.Positive(recharge, "aps", nameof(recharge));
        }

        public float Radius { get; }
        public int Charges { get; }
        public float Recharge { get; }

        /// <summary>Also takes artillery rockets (a point-defence laser), not only direct-fire ones.</summary>
        public bool Rockets { get; internal set; }

        /// <summary>Share of incoming shells and mortar bombs it can also take (0: none; a C-RAM).</summary>
        public float Shells { get; internal set; }
    }

    /// <summary>
    /// A tower that hides (the gun pit): it stays down while no enemy on the ground is within
    /// <see cref="Rise"/>, taking <see cref="Cut"/> less damage and seen only by scouts, radars,
    /// scans and guard towers; up, it fires, its first shot <see cref="FirstShot"/> times as hard.
    /// </summary>
    public sealed class HiddenDef
    {
        public HiddenDef(float rise, float cut, float firstShot)
        {
            Rise = Guard.Positive(rise, "hidden", nameof(rise));
            Cut = Math.Clamp(cut, 0f, 0.95f);
            FirstShot = MathF.Max(1f, firstShot);
        }

        public float Rise { get; }
        public float Cut { get; }
        public float FirstShot { get; }
    }

    /// <summary>
    /// A base's utility module: what it does for its side (each field 0 when it does not):
    /// vehicles in the base repair <see cref="Repair"/> of their health a second; reload
    /// <see cref="Rearm"/> times as fast there; aircraft within <see cref="AirReach"/> repair
    /// <see cref="AirRepair"/> a second and rearm; the side's supply grows by <see cref="Supply"/>;
    /// stealth in the base shows (<see cref="RevealBase"/>).
    /// </summary>
    public sealed class UtilityDef
    {
        public float Repair { get; internal set; }
        public float Rearm { get; internal set; }
        public float AirRepair { get; internal set; }
        public float AirReach { get; internal set; }
        public int Supply { get; internal set; }
        public bool RevealBase { get; internal set; }
    }

    /// <summary>
    /// A command vehicle's aura: friendly vehicles within Radius fire FireRate faster and hit Damage
    /// harder (several auras do not add up: the best of each counts).
    /// </summary>
    public sealed class CommandAuraDef
    {
        public CommandAuraDef(float radius, float fireRate, float damage = 0f)
        {
            Radius = Guard.Positive(radius, "commandAura", nameof(radius));
            FireRate = Guard.NonNegative(fireRate, "commandAura", nameof(fireRate));
            Damage = Guard.NonNegative(damage, "commandAura", nameof(damage));
        }

        public float Radius { get; }
        public float FireRate { get; }

        /// <summary>Share more damage for friendly vehicles in reach (the Supreme Commander's).</summary>
        public float Damage { get; }
    }

    /// <summary>
    /// A counter-battery radar: enemy artillery firing within Range is shown to the radar's side
    /// for Seconds, and that side's artillery does Bonus more damage to it.
    /// </summary>
    public sealed class CounterBatteryDef
    {
        public CounterBatteryDef(float range, float seconds, float bonus)
        {
            Range = Guard.Positive(range, "counterBattery", nameof(range));
            Seconds = Guard.Positive(seconds, "counterBattery", nameof(seconds));
            Bonus = Guard.NonNegative(bonus, "counterBattery", nameof(bonus));
        }

        public float Range { get; }
        public float Seconds { get; }
        public float Bonus { get; }
    }

    /// <summary>
    /// A weapon's extra damage against some targets: a class (the Lancet on artillery), an armour
    /// (a car bomb on structures), a target that has stood still a while, or a hit from the side or
    /// rear. Every condition set must hold. Of the bonuses that apply the biggest counts, of the
    /// penalties the smallest (they never stack).
    /// </summary>
    public sealed class DamageBonus
    {
        public float Mult { get; internal set; } = 1f;
        public UnitClass? Class { get; internal set; }
        public ArmorClass? Armor { get; internal set; }

        /// <summary>The target has not moved for at least this many seconds (0: any).</summary>
        public float StillFor { get; internal set; }

        /// <summary>Only a hit on the target's side or rear.</summary>
        public bool Flank { get; internal set; }
    }

    /// <summary>A mine layer's charges: laid every Interval seconds, at most Max alive per layer.</summary>
    public sealed class MineLayerDef
    {
        public MineLayerDef(float interval, int max, ExplosionDef blast, float trigger)
        {
            Interval = Guard.Positive(interval, "mines", nameof(interval));
            Max = max >= 1 ? max : throw new ArgumentException("mines: max must be at least 1.");
            Blast = blast ?? throw new ArgumentNullException(nameof(blast));
            Trigger = Guard.Positive(trigger, "mines", nameof(trigger));
        }

        public float Interval { get; }
        public int Max { get; }
        public ExplosionDef Blast { get; }

        /// <summary>An enemy ground vehicle this close sets the mine off.</summary>
        public float Trigger { get; }

        /// <summary>A fixed minefield lays its mines anywhere within this many metres of itself (0: a mine layer drops them behind it).</summary>
        public float Spread { get; internal set; }
    }
}
