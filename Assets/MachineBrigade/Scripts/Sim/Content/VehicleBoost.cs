#nullable enable
namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// What a side's upgrades (card ranks and equipment) do to one of its vehicles: multipliers on
    /// its health, damage, rate of fire and speed and on the damage it takes, self-repair as a
    /// share of health a second out of combat, and a special module. Applied when the vehicle
    /// enters the battle; the defaults change nothing.
    /// </summary>
    public readonly struct VehicleBoost
    {
        public VehicleBoost(float hp, float damage, float fireRate, float speed, float damageTaken, float regen, SpecialModule special, float specialPower)
        {
            Hp = hp;
            Damage = damage;
            FireRate = fireRate;
            Speed = speed;
            DamageTaken = damageTaken;
            Regen = regen;
            Special = special;
            SpecialPower = specialPower;
        }

        public float Hp { get; }
        public float Damage { get; }
        public float FireRate { get; }
        public float Speed { get; }
        public float DamageTaken { get; }
        public float Regen { get; }
        public SpecialModule Special { get; }

        /// <summary>The module's strength (a damage cut, a repair rate, a bonus, a smoke radius).</summary>
        public float SpecialPower { get; }

        public static VehicleBoost None => new(1f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f);
    }

    /// <summary>The special module of an equipment loadout (its seventh slot).</summary>
    public enum SpecialModule
    {
        None,

        /// <summary>Explosive reactive armour: takes less damage.</summary>
        ReactiveArmor,

        /// <summary>Repairs itself a little every second once it has not been hit for a few seconds.</summary>
        AutoRepair,

        /// <summary>A veteran crew: hits harder and fires faster.</summary>
        VeteranCrew,

        /// <summary>Throws a smoke screen round itself the first time it drops below half health.</summary>
        SmokeDischarger,
    }
}
