#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 15 B-C: what a hit does. Two parts multiplied: the <b>penetration</b> multiplier, by how far the
    /// round's penetration level is above or below the armour level of the face it strikes (one level or more
    /// above: all of it; level with it: three quarters; one under: 0.4; two under: 0.15; three or more under:
    /// 0.05), and the <b>damage type</b> multiplier against the kind of target (ground, air, structure). The
    /// thermobaric tag raises high explosive against structures.
    /// </summary>
    public sealed class DamageTable
    {
        private static readonly int DamageTypeCount = Enum.GetValues(typeof(DamageType)).Length;
        private static readonly int KindCount = Enum.GetValues(typeof(TargetKind)).Length;

        private readonly float[,] _types;

        /// <summary>The penetration multipliers: [0] one level or more above the armour, [1] level, [2] one under, [3] two under, [4] three or more under.</summary>
        private readonly float[] _pen;

        public DamageTable(float[,] types, float[]? penetration = null, float thermobaricStructure = 2f)
        {
            if (types.GetLength(0) != DamageTypeCount || types.GetLength(1) != KindCount)
                throw new ArgumentException($"Damage table must be {DamageTypeCount} x {KindCount}.");
            foreach (var m in types)
                if (!float.IsFinite(m) || m < 0f) throw new ArgumentException("Damage multipliers must be finite and non-negative.");
            _types = (float[,])types.Clone();
            _pen = penetration != null ? (float[])penetration.Clone() : (float[])DefaultPenetration.Clone();
            if (_pen.Length != 5) throw new ArgumentException("The penetration row must have 5 values (above, level, -1, -2, -3).");
            for (var i = 0; i < _pen.Length; i++)
                if (!float.IsFinite(_pen[i]) || _pen[i] < 0f || (i > 0 && _pen[i] > _pen[i - 1]))
                    throw new ArgumentException("Penetration multipliers must be non-negative and never rise as the armour gets thicker.");
            ThermobaricStructure = Guard.NonNegative(thermobaricStructure, "damageTable", "thermobaric");
        }

        private static readonly float[] DefaultPenetration = { 1f, 0.75f, 0.4f, 0.15f, 0.05f };

        /// <summary>The starting values (prompt 15 B.2 and C.7).</summary>
        public static DamageTable Default { get; } = new DamageTable(new[,]
        {
            //  Ground  Air   Structure
            { 1.00f, 0.30f, 0.60f }, // Kinetic
            { 1.00f, 0.30f, 0.60f }, // ShapedCharge
            { 1.00f, 0.00f, 1.50f }, // HighExplosive
            { 1.25f, 0.00f, 1.00f }, // Fire
            { 0.50f, 1.50f, 0.10f }, // Fragmentation
            { 1.00f, 1.50f, 0.50f }, // Energy
        });

        /// <summary>High explosive with the thermobaric tag against structures (instead of the type's structure value).</summary>
        public float ThermobaricStructure { get; }

        /// <summary>The damage type's multiplier against a kind of target.</summary>
        public float Type(DamageType damage, TargetKind kind) => _types[(int)damage, (int)kind];

        /// <summary>A weapon's damage-type multiplier against a kind of target (the thermobaric tag against structures).</summary>
        public float TypeOf(WeaponDef weapon, TargetKind kind) =>
            weapon.Thermobaric && kind == TargetKind.Structure && weapon.DamageType == DamageType.HighExplosive
                ? MathF.Max(ThermobaricStructure, Type(weapon.DamageType, kind))
                : Type(weapon.DamageType, kind);

        /// <summary>The penetration multiplier of a step, 0 (one level or more above) to 4 (three or more under).</summary>
        public float PenetrationStep(int step) => _pen[Math.Clamp(step, 0, 4)];

        /// <summary>
        /// The penetration multiplier of a round of <paramref name="penetration"/> against a face of
        /// <paramref name="armour"/>. Whole levels read the table; a part level (equipment adds some) lies
        /// between its two neighbours.
        /// </summary>
        public float Penetration(float penetration, float armour)
        {
            // Steps: diff >= 1 -> 0, diff 0 -> 1, -1 -> 2, -2 -> 3, <= -3 -> 4.
            var step = 1f - (penetration - armour);
            if (step <= 0f) return _pen[0];
            if (step >= 4f) return _pen[4];
            var low = (int)MathF.Floor(step);
            var t = step - low;
            return _pen[low] + (_pen[Math.Min(4, low + 1)] - _pen[low]) * t;
        }

        /// <summary>
        /// What one of a weapon's rounds does, as a multiplier, against a face of armour level
        /// <paramref name="armour"/> on a target of <paramref name="kind"/>: penetration times damage type.
        /// </summary>
        public float Effective(WeaponDef weapon, float armour, TargetKind kind) =>
            Penetration(weapon.Penetration, armour) * TypeOf(weapon, kind);

        /// <summary>The same for damage of a type and penetration without a weapon (a strike, a mine, a blast).</summary>
        public float Effective(DamageType damage, float penetration, float armour, TargetKind kind) =>
            Penetration(penetration, armour) * Type(damage, kind);
    }
}
