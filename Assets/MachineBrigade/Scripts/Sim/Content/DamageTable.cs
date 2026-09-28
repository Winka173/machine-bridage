#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Effectiveness of each damage type against each armour class. This is what makes
    /// counters work: AP shells for tanks, HE for light vehicles and buildings, flak for air.
    /// </summary>
    public sealed class DamageTable
    {
        private static readonly int DamageTypeCount = Enum.GetValues(typeof(DamageType)).Length;
        private static readonly int ArmorClassCount = Enum.GetValues(typeof(ArmorClass)).Length;

        private readonly float[,] _multipliers;

        public DamageTable(float[,] multipliers)
        {
            if (multipliers.GetLength(0) != DamageTypeCount || multipliers.GetLength(1) != ArmorClassCount)
                throw new ArgumentException($"Damage table must be {DamageTypeCount} x {ArmorClassCount}.");
            foreach (var m in multipliers)
                if (!float.IsFinite(m) || m < 0f) throw new ArgumentException("Damage multipliers must be finite and non-negative.");
            _multipliers = (float[,])multipliers.Clone();
        }

        /// <summary>The starting values from the game plan (section 4).</summary>
        public static DamageTable Default { get; } = new DamageTable(new[,]
        {
            //  Light  Heavy  Air   Structure
            { 1.00f, 0.25f, 0.5f, 0.3f }, // Kinetic
            { 0.75f, 1.00f, 0.5f, 0.6f }, // ArmorPiercing
            { 1.00f, 0.60f, 0.0f, 1.5f }, // HighExplosive
            { 1.25f, 0.50f, 0.0f, 1.0f }, // Fire
            { 0.40f, 0.10f, 1.5f, 0.1f }, // Flak
        });

        public float Multiplier(DamageType damage, ArmorClass armor) => _multipliers[(int)damage, (int)armor];

        /// <summary>What one of this weapon's rounds does against an armour class (its damage type's row).</summary>
        public float Multiplier(WeaponDef weapon, ArmorClass armor) => Multiplier(weapon.DamageType, armor);
    }
}
