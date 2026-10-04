#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 15 B-C, combat final (04/10): what a hit does. Two parts multiplied: the <b>armour</b> multiplier, by how far
    /// the round's penetration level is above or below the armour level it meets, and the <b>damage type</b> multiplier
    /// against the kind of target (ground, air, structure). The armour multiplier comes from one of two tables, never both:
    /// <list type="bullet">
    /// <item>the <b>direct</b> penetration table (<see cref="Penetration"/>): seven steps, two levels or more above (the round
    /// overmatches the face), one above, level, one, two, three under and four or more under (1.20 / 1.00 / 0.85 / 0.65 /
    /// 0.40 / 0.15 / 0.08). The overmatch step is for the faces a round meets side on; a round that is not a top attack
    /// but still comes down on the roof (lobbed shells, an aeroplane's fire, a strike) and every hit on an aircraft stop
    /// at one level above (1.00);</item>
    /// <item>the <b>top attack</b> table (<see cref="TopAttack"/>), for weapons with the topAttack flag against the roof of a
    /// ground target or a structure: its own seven steps (1.15 / 1.10 / 0.95 / 0.75 / 0.50 / 0.25 / 0.12), no cap.</item>
    /// </list>
    /// The thermobaric tag replaces high explosive's structure value (2.0 instead of 1.60, not on top of it).
    /// Splash / overpenetration 04/10 (DECISIONS "Armour/Pen 5 and splash/overpen 04/10 (lane A)"): two more rows, neither
    /// touching the tables above:
    /// <list type="bullet">
    /// <item>the <b>splash falloff</b> (<see cref="SplashFalloff"/>), what share of a blast's damage reaches a target by its
    /// distance from the centre, by core and edge progress: 1.10 at the centre, 1.08 / 1.05 / 1.00 over the core's first
    /// quarter, second quarter and second half, 0.85 / 0.65 / 0.45 / 0.25 over the four quarters from the core to the edge,
    /// 0 at the edge and beyond. It multiplies a blast's damage only, never a direct hit (the struck target takes its
    /// direct hit and is left out of its own round's blast, as before);</item>
    /// <item>the <b>kinetic overpenetration</b> row (<see cref="Overpenetration"/>), for a direct Kinetic round (not a top
    /// attack, not a blast) by penetration - armour: +2 or less 1.00, +3 0.95, +4 0.85, +5 or more 0.75. It multiplies after
    /// the direct penetration table (never instead of it).</item>
    /// </list>
    /// </summary>
    public sealed class DamageTable
    {
        private static readonly int DamageTypeCount = Enum.GetValues(typeof(DamageType)).Length;
        private static readonly int KindCount = Enum.GetValues(typeof(TargetKind)).Length;

        private readonly float[,] _types;

        /// <summary>
        /// The direct penetration multipliers: [0] two levels or more above the armour (overmatch), [1] one above, [2] level,
        /// [3] one under, [4] two under, [5] three under, [6] four or more under.
        /// </summary>
        private readonly float[] _pen;

        /// <summary>The top attack multipliers, the same seven steps against the roof's armour level.</summary>
        private readonly float[] _top;

        /// <summary>The steps of each armour row, overmatch first.</summary>
        public const int PenetrationSteps = 7;

        /// <summary>Splash 04/10: the splash falloff steps: centre, core 0-25 %, 25-50 %, 50-100 %, edge 0-25 %, 25-50 %, 50-75 %, 75-100 %, outside.</summary>
        public const int SplashSteps = 9;

        /// <summary>Overpenetration 04/10: the steps by penetration - armour: +2 or less, +3, +4, +5 or more.</summary>
        public const int OverpenetrationSteps = 4;

        /// <summary>Splash 04/10: 110 / 108 / 105 / 100 / 85 / 65 / 45 / 25 / 0 (balance.json damageTable.splashFalloff says the same).</summary>
        private static readonly float[] DefaultSplash = { 1.10f, 1.08f, 1.05f, 1.00f, 0.85f, 0.65f, 0.45f, 0.25f, 0f };

        /// <summary>Overpenetration 04/10: 100 / 95 / 85 / 75 (balance.json damageTable.overpenetration says the same).</summary>
        private static readonly float[] DefaultOver = { 1.00f, 0.95f, 0.85f, 0.75f };

        /// <summary>The splash falloff multipliers (<see cref="SplashSteps"/>).</summary>
        private readonly float[] _splash;

        /// <summary>The kinetic overpenetration multipliers (<see cref="OverpenetrationSteps"/>).</summary>
        private readonly float[] _over;

        /// <summary>A row of exactly <paramref name="count"/> finite, non-negative values that never rise along it.</summary>
        private static float[] Fixed(float[]? row, float[] fallback, int count, string name)
        {
            var full = (float[])(row ?? fallback).Clone();
            if (full.Length != count) throw new ArgumentException($"The {name} row must have {count} values.");
            for (var i = 0; i < full.Length; i++)
                if (!float.IsFinite(full[i]) || full[i] < 0f || (i > 0 && full[i] > full[i - 1]))
                    throw new ArgumentException($"The {name} multipliers must be finite, non-negative and never rise along the row.");
            return full;
        }

        /// <summary>
        /// A row of seven, or an old row: six values ("three or more under" last, repeated for the seventh step) or five
        /// (no overmatch step: two above is then the same as one above).
        /// </summary>
        private static float[] Expand(float[] row, string name)
        {
            if (row.Length is not (5 or 6 or PenetrationSteps))
                throw new ArgumentException($"The {name} row must have 7 values (+2, +1, 0, -1, -2, -3, -4), or an old row of 6 or 5.");
            var full = new float[PenetrationSteps];
            var skip = row.Length == 5 ? 1 : 0;
            for (var i = 0; i < PenetrationSteps; i++) full[i] = row[Math.Clamp(i - skip, 0, row.Length - 1)];
            for (var i = 0; i < full.Length; i++)
                if (!float.IsFinite(full[i]) || full[i] < 0f || (i > 0 && full[i] > full[i - 1]))
                    throw new ArgumentException($"The {name} multipliers must be finite, non-negative and never rise as the armour gets thicker.");
            return full;
        }

        public DamageTable(float[,] types, float[]? penetration = null, float thermobaricStructure = 2f, float[]? topAttack = null,
            float[]? splashFalloff = null, float[]? overpenetration = null)
        {
            if (types.GetLength(0) != DamageTypeCount || types.GetLength(1) != KindCount)
                throw new ArgumentException($"Damage table must be {DamageTypeCount} x {KindCount}.");
            foreach (var m in types)
                if (!float.IsFinite(m) || m < 0f) throw new ArgumentException("Damage multipliers must be finite and non-negative.");
            _types = (float[,])types.Clone();
            _pen = Expand(penetration ?? DefaultPenetration, "penetration");
            _top = Expand(topAttack ?? DefaultTopAttack, "topAttack");
            ThermobaricStructure = Guard.NonNegative(thermobaricStructure, "damageTable", "thermobaric");
            _splash = Fixed(splashFalloff, DefaultSplash, SplashSteps, "splashFalloff");
            _over = Fixed(overpenetration, DefaultOver, OverpenetrationSteps, "overpenetration");
        }

        /// <summary>Combat final 04/10 (DECISIONS "Combat final 04/10 (lane A)"): the direct row 1.20 / 1.00 / 0.85 / 0.65 / 0.40 / 0.15 / 0.08.</summary>
        private static float[] DefaultPenetration => global::MachineBrigade.Sim.Content.SimTunables.Weapons.DamageTable.DefaultPenetration;

        /// <summary>Combat final 04/10 addendum: the top attack row 1.15 / 1.10 / 0.95 / 0.75 / 0.50 / 0.25 / 0.12.</summary>
        private static float[] DefaultTopAttack => global::MachineBrigade.Sim.Content.SimTunables.Weapons.DamageTable.DefaultTopAttack;

        /// <summary>The starting values (combat final 04/10; balance.json "damageTable" is the source of truth and says the same).</summary>
        public static DamageTable Default { get; } = new DamageTable(new[,]
        {
            //  Ground  Air   Structure
            { 1.20f, 0.30f, 0.70f }, // Kinetic
            { 1.30f, 0.20f, 0.45f }, // ShapedCharge
            { 1.00f, 0.00f, 1.60f }, // HighExplosive
            { 1.35f, 0.00f, 1.10f }, // Fire
            { 0.45f, 1.35f, 0.10f }, // Fragmentation
            { 0.90f, 1.50f, 0.40f }, // Energy
        });

        /// <summary>High explosive with the thermobaric tag against structures (instead of the type's structure value).</summary>
        public float ThermobaricStructure { get; }

        /// <summary>The damage type's multiplier against a kind of target.</summary>
        public float Type(DamageType damage, TargetKind kind) => _types[(int)damage, (int)kind];

        /// <summary>
        /// The damage type's multiplier with the thermobaric tag: high explosive against a structure takes
        /// <see cref="ThermobaricStructure"/> instead of the type's own structure value (it replaces it, never multiplies it).
        /// </summary>
        public float TypeOf(DamageType damage, TargetKind kind, bool thermobaric) =>
            thermobaric && kind == TargetKind.Structure && damage == DamageType.HighExplosive ? ThermobaricStructure : Type(damage, kind);

        /// <summary>A weapon's damage-type multiplier against a kind of target (the thermobaric tag against structures).</summary>
        public float TypeOf(WeaponDef weapon, TargetKind kind) => TypeOf(weapon.DamageType, kind, weapon.Thermobaric);

        /// <summary>The direct penetration multiplier of a step, 0 (two levels or more above) to 6 (four or more under).</summary>
        public float PenetrationStep(int step) => _pen[Math.Clamp(step, 0, PenetrationSteps - 1)];

        /// <summary>The top attack multiplier of a step, 0 (two levels or more above the roof) to 6 (four or more under).</summary>
        public float TopAttackStep(int step) => _top[Math.Clamp(step, 0, PenetrationSteps - 1)];

        /// <summary>
        /// The direct penetration multiplier of a round of <paramref name="penetration"/> against a face of
        /// <paramref name="armour"/>. Whole levels read the table; a part level (equipment adds some) lies
        /// between its two neighbours. Without <paramref name="overmatch"/> (a roof struck by a round that is not a top
        /// attack, an aircraft) one level above is the most.
        /// </summary>
        public float Penetration(float penetration, float armour, bool overmatch = true) => Read(_pen, penetration, armour, overmatch);

        /// <summary>
        /// The top attack multiplier of a round of <paramref name="penetration"/> against a roof of <paramref name="roof"/>:
        /// the top attack table (no cap at one level above), a part level between its two neighbours.
        /// </summary>
        public float TopAttack(float penetration, float roof) => Read(_top, penetration, roof, true);

        private static float Read(float[] row, float penetration, float armour, bool overmatch)
        {
            // Steps: diff >= 2 -> 0, 1 -> 1, 0 -> 2, -1 -> 3, -2 -> 4, -3 -> 5, <= -4 -> 6. A NaN level reads the last step.
            const int last = PenetrationSteps - 1;
            var step = 2f - (penetration - armour);
            if (float.IsNaN(step)) return row[last];
            if (!overmatch) step = MathF.Max(1f, step);
            if (step <= 0f) return row[0];
            if (step >= last) return row[last];
            var low = (int)MathF.Floor(step);
            var t = step - low;
            return row[low] + (row[Math.Min(last, low + 1)] - row[low]) * t;
        }

        /// <summary>
        /// The armour multiplier of a hit, in three separate branches: an aircraft (the direct table, no overmatch: the
        /// aircraft system as before); a top attack against a ground target or a structure (<paramref name="armour"/> is the
        /// roof's; the top attack table only); else the direct table against the face struck (no overmatch on the
        /// <paramref name="roof"/>). Never both tables.
        /// </summary>
        public float ArmourMultiplier(float penetration, float armour, TargetKind kind, bool roof, bool topAttack)
        {
            if (kind == TargetKind.Air) return Penetration(penetration, armour, false);
            if (topAttack) return TopAttack(penetration, armour);
            return Penetration(penetration, armour, !roof);
        }

        /// <summary>
        /// What one of a weapon's rounds does, as a multiplier, against armour level <paramref name="armour"/> (the roof's for
        /// a top-attack weapon) on a target of <paramref name="kind"/>: the armour multiplier, the kinetic overpenetration of a
        /// direct round (04/10), times the damage type.
        /// </summary>
        public float Effective(WeaponDef weapon, float armour, TargetKind kind, bool fromAbove = false) =>
            ArmourMultiplier(weapon.Penetration, armour, kind, fromAbove || Armour.StrikesTop(weapon), weapon.TopAttack) *
            (Overpenetrates(weapon) ? Overpenetration(weapon.Penetration, armour) : 1f) * TypeOf(weapon, kind);

        /// <summary>The splash falloff multiplier of a step, 0 (the centre) to 8 (outside the blast).</summary>
        public float SplashStep(int step) => _splash[Math.Clamp(step, 0, SplashSteps - 1)];

        /// <summary>The overpenetration multiplier of a step, 0 (+2 or less) to 3 (+5 or more).</summary>
        public float OverpenetrationStep(int step) => _over[Math.Clamp(step, 0, OverpenetrationSteps - 1)];

        /// <summary>
        /// Splash 04/10: the step of a target <paramref name="distance"/> m from a blast's centre (to its hull's edge, as the
        /// blast measures it) with a core of <paramref name="core"/> m and an edge reaching <paramref name="edge"/> m. In the core,
        /// coreProgress = r / core: r = 0 the centre, then up to 0.25, 0.50 and 1.00 (each bound inclusive). Past the core,
        /// edgeProgress = (r - core) / (edge - core): up to 0.25, 0.50, 0.75, under 1.00; at 1.00 or more, outside. A blast with
        /// one radius has a core of 0 and that radius as its edge (DamageSystem maps it): only r = 0 is the centre. Never
        /// divides by zero: no core, no core progress; an edge no wider than the core, no edge zone (outside past the core).
        /// NaN or a blast of no size reads outside; a negative distance reads as 0.
        /// </summary>
        public static int SplashStepAt(float distance, float core, float edge)
        {
            if (float.IsNaN(distance)) return SplashSteps - 1;
            if (distance < 0f) distance = 0f;
            if (!(core > 0f)) core = 0f;
            if (!(edge > 0f)) edge = 0f;
            if (!(MathF.Max(core, edge) > 0f)) return SplashSteps - 1;
            if (distance == 0f) return 0;
            if (distance <= core)
            {
                var p = distance / core;
                return p <= 0.25f ? 1 : p <= 0.5f ? 2 : 3;
            }
            if (edge > core && distance < edge)
            {
                var p = (distance - core) / (edge - core);
                return p <= 0.25f ? 4 : p <= 0.5f ? 5 : p <= 0.75f ? 6 : 7;
            }
            return SplashSteps - 1;
        }

        /// <summary>
        /// Splash 04/10: the share of a blast's damage that reaches a target <paramref name="distance"/> m from its centre
        /// (<see cref="SplashStepAt"/>): 1.10 / 1.08 / 1.05 / 1.00 in the core, 0.85 / 0.65 / 0.45 / 0.25 on the way to the
        /// edge, 0 beyond. A blast's damage only: never a direct hit's.
        /// </summary>
        public float SplashFalloff(float distance, float core, float edge) => _splash[SplashStepAt(distance, core, edge)];

        /// <summary>Overpenetration 04/10: whether a weapon's direct hits take the overpenetration row (Kinetic and not a top attack).</summary>
        public static bool Overpenetrates(WeaponDef? weapon) => weapon is { DamageType: DamageType.Kinetic, TopAttack: false };

        /// <summary>
        /// Overpenetration 04/10: a direct Kinetic round of <paramref name="penetration"/> against <paramref name="armour"/>, by
        /// penetration - armour: +2 or less 1.00, +3 0.95, +4 0.85, +5 or more 0.75; a part level (equipment adds some) lies
        /// between its two neighbours. Multiplies after the penetration table; a NaN reads +2 or less.
        /// </summary>
        public float Overpenetration(float penetration, float armour)
        {
            var diff = penetration - armour;
            if (float.IsNaN(diff) || diff <= 2f) return _over[0];
            if (diff >= 2f + (OverpenetrationSteps - 1)) return _over[OverpenetrationSteps - 1];
            var x = diff - 2f;
            var low = (int)MathF.Floor(x);
            var t = x - low;
            return _over[low] + (_over[Math.Min(OverpenetrationSteps - 1, low + 1)] - _over[low]) * t;
        }

        /// <summary>Whether a round that is not a top attack can overmatch the face it strikes: not on the roof, not on an aircraft.</summary>
        public static bool Overmatches(TargetKind kind, bool roof) => !roof && kind != TargetKind.Air;

        /// <summary>The same for damage of a type and penetration without a weapon (a strike, a mine, a blast, a threat profile).</summary>
        public float Effective(DamageType damage, float penetration, float armour, TargetKind kind, bool roof = false, bool topAttack = false) =>
            ArmourMultiplier(penetration, armour, kind, roof, topAttack) * Type(damage, kind);
    }
}
