#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 15 B-C: what a hit does. Two parts multiplied: the <b>penetration</b> multiplier, by how far the
    /// round's penetration level is above or below the armour level of the face it strikes (DECISIONS 20X: two
    /// levels or more above, the round overmatches the face; one above; level; one, two, three or more under;
    /// the data's six values), and the <b>damage type</b> multiplier against the kind of target (ground, air,
    /// structure). The thermobaric tag raises high explosive against structures. The overmatch step is for the faces
    /// a round meets side on (front, side, rear): not the roof (top attacks, everything lobbed or dropped, an
    /// aeroplane's fire) and not an aircraft (the same all round), where one level above is the most.
    /// </summary>
    public sealed class DamageTable
    {
        private static readonly int DamageTypeCount = Enum.GetValues(typeof(DamageType)).Length;
        private static readonly int KindCount = Enum.GetValues(typeof(TargetKind)).Length;

        private readonly float[,] _types;

        /// <summary>
        /// The penetration multipliers: [0] two levels or more above the armour (overmatch), [1] one above, [2] level,
        /// [3] one under, [4] two under, [5] three or more under. Five values (prompt 15's row) have no overmatch
        /// step: two above is then the same as one above.
        /// </summary>
        private readonly float[] _pen;

        /// <summary>The steps of the penetration row, overmatch first.</summary>
        public const int PenetrationSteps = 6;

        public DamageTable(float[,] types, float[]? penetration = null, float thermobaricStructure = 2f)
        {
            if (types.GetLength(0) != DamageTypeCount || types.GetLength(1) != KindCount)
                throw new ArgumentException($"Damage table must be {DamageTypeCount} x {KindCount}.");
            foreach (var m in types)
                if (!float.IsFinite(m) || m < 0f) throw new ArgumentException("Damage multipliers must be finite and non-negative.");
            _types = (float[,])types.Clone();
            var row = penetration ?? DefaultPenetration;
            if (row.Length is not (5 or PenetrationSteps))
                throw new ArgumentException("The penetration row must have 6 values (two above, one above, level, -1, -2, -3) or 5 (no overmatch step).");
            _pen = new float[PenetrationSteps];
            var skip = PenetrationSteps - row.Length;
            for (var i = 0; i < PenetrationSteps; i++) _pen[i] = row[Math.Max(0, i - skip)];
            for (var i = 0; i < _pen.Length; i++)
                if (!float.IsFinite(_pen[i]) || _pen[i] < 0f || (i > 0 && _pen[i] > _pen[i - 1]))
                    throw new ArgumentException("Penetration multipliers must be non-negative and never rise as the armour gets thicker.");
            ThermobaricStructure = Guard.NonNegative(thermobaricStructure, "damageTable", "thermobaric");
        }

        /// <summary>DECISIONS 20X: the armour and damage balance pass (prompt 15's row was 1, 0.75, 0.4, 0.15, 0.05).</summary>
        private static float[] DefaultPenetration => global::MachineBrigade.Sim.Content.SimTunables.Weapons.DamageTable.DefaultPenetration;

        /// <summary>The starting values (prompt 15 B.2 and C.7; the penetration row from DECISIONS 20X).</summary>
        public static DamageTable Default { get; } = new DamageTable(new[,]
        {
            //  Ground  Air   Structure
            { 1.00f, 0.30f, 0.60f }, // Kinetic
            { 1.00f, 0.30f, 0.60f }, // ShapedCharge
            { 1.00f, 0.00f, 1.50f }, // HighExplosive
            { 1.50f, 0.00f, 1.00f }, // Fire
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

        /// <summary>The penetration multiplier of a step, 0 (two levels or more above) to 5 (three or more under).</summary>
        public float PenetrationStep(int step) => _pen[Math.Clamp(step, 0, PenetrationSteps - 1)];

        /// <summary>
        /// The penetration multiplier of a round of <paramref name="penetration"/> against a face of
        /// <paramref name="armour"/>. Whole levels read the table; a part level (equipment adds some) lies
        /// between its two neighbours. Without <paramref name="overmatch"/> (the roof, an aircraft) one level
        /// above is the most.
        /// </summary>
        public float Penetration(float penetration, float armour, bool overmatch = true)
        {
            // Steps: diff >= 2 -> 0, diff 1 -> 1, 0 -> 2, -1 -> 3, -2 -> 4, <= -3 -> 5.
            const int last = PenetrationSteps - 1;
            var step = 2f - (penetration - armour);
            if (!overmatch) step = MathF.Max(1f, step);
            if (step <= 0f) return _pen[0];
            if (step >= last) return _pen[last];
            var low = (int)MathF.Floor(step);
            var t = step - low;
            return _pen[low] + (_pen[Math.Min(last, low + 1)] - _pen[low]) * t;
        }

        /// <summary>
        /// What one of a weapon's rounds does, as a multiplier, against a face of armour level
        /// <paramref name="armour"/> on a target of <paramref name="kind"/>: penetration times damage type.
        /// </summary>
        public float Effective(WeaponDef weapon, float armour, TargetKind kind, bool fromAbove = false) =>
            Penetration(weapon.Penetration, armour, Overmatches(kind, fromAbove || Armour.StrikesTop(weapon))) * TypeOf(weapon, kind);

        /// <summary>Whether a round can overmatch the face it strikes: not on the roof, not on an aircraft.</summary>
        public static bool Overmatches(TargetKind kind, bool roof) => !roof && kind != TargetKind.Air;

        /// <summary>The same for damage of a type and penetration without a weapon (a strike, a mine, a blast).</summary>
        public float Effective(DamageType damage, float penetration, float armour, TargetKind kind, bool roof = false) =>
            Penetration(penetration, armour, Overmatches(kind, roof)) * Type(damage, kind);
    }
}
