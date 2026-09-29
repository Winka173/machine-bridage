#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Prompt 15 E.5: how well a weapon deals with a target: ✓ pierces well, ~ poorly, ✕ not at all (or cannot reach it).</summary>
    public enum MatchVerdict
    {
        Good,
        Poor,
        None,
    }

    /// <summary>Prompt 15 E.2: the columns of a weapon's effect table: the five armour levels on the ground, then aircraft, then structures.</summary>
    public enum EffectColumn
    {
        Armour0,
        Armour1,
        Armour2,
        Armour3,
        Armour4,
        Air,
        Structure,
    }

    /// <summary>
    /// Prompt 15 E.2 "weak against": the kinds of weapon that hurt a unit, from the lightest to the heaviest.
    /// Each stands for a typical weapon (<see cref="Matchup.ThreatProfile"/>).
    /// </summary>
    public enum Threat
    {
        /// <summary>Rifle-calibre machine guns (7.62 mm, penetration 0).</summary>
        SmallArms,
        /// <summary>Heavy machine guns (12.7-14.5 mm, 1).</summary>
        HeavyMachineGuns,
        /// <summary>Flamethrowers and napalm (fire, 1).</summary>
        Fire,
        /// <summary>Flak, airburst and anti-air missiles (fragmentation, 2).</summary>
        Fragmentation,
        /// <summary>Autocannons (kinetic, 2).</summary>
        Autocannons,
        /// <summary>Artillery, mortars, rockets and bombs (high explosive, 2, on the roof).</summary>
        HighExplosive,
        /// <summary>Lasers and energy beams (2).</summary>
        Energy,
        /// <summary>Top-attack missiles, diving drones and bomblets (shaped charge, 4, on the roof).</summary>
        TopAttack,
        /// <summary>Anti-tank missiles, rockets and drones (shaped charge, 4).</summary>
        ShapedCharges,
        /// <summary>120 mm tank guns and railguns (kinetic, 4).</summary>
        TankGuns,
    }

    /// <summary>
    /// Prompt 15 E.2: a unit's "strong against / weak against", worked out from its armour, its weapons'
    /// penetration and their damage types (<see cref="Matchup.Summary"/>).
    /// </summary>
    public sealed class StrengthSummary
    {
        public StrengthSummary(IReadOnlyList<EffectColumn> strongVs, IReadOnlyList<Threat> weakTo, float[] best)
        {
            StrongVs = strongVs;
            WeakTo = weakTo;
            Best = best;
        }

        /// <summary>The columns its best weapon deals with well (✓), in column order.</summary>
        public IReadOnlyList<EffectColumn> StrongVs { get; }

        /// <summary>The kinds of weapon that pierce it well, lightest first (the cheapest counters first).</summary>
        public IReadOnlyList<Threat> WeakTo { get; }

        /// <summary>Its best weapon's effect in each column (<see cref="EffectColumn"/> order).</summary>
        public float[] Best { get; }
    }

    /// <summary>
    /// Prompt 15, pure helpers for the interface and the documents: a unit's armour by face, what a weapon does
    /// against an armour level, aircraft and structures, ✓ ~ ✕ against an enemy, and a unit's strong / weak
    /// summary. Everything reads the damage table the battle uses.
    /// </summary>
    public static class Matchup
    {
        /// <summary>The effect table's aircraft column is read at this armour level (most aircraft have none).</summary>
        public const int AirLevel = 0;

        /// <summary>The effect table's structure column is read at this armour level (a concrete tower).</summary>
        public const int StructureLevel = 2;

        /// <summary>From this multiplier a weapon counts as dealing well with a target (✓): level with its armour or better.</summary>
        public const float GoodAt = 0.6f;

        /// <summary>From this multiplier (up to <see cref="GoodAt"/>) poorly (~); under it, not at all (✕).</summary>
        public const float PoorAt = 0.12f;

        public static int ColumnCount => 7;

        /// <summary>A unit's armour on each face.</summary>
        public static ArmourLevels ArmourOf(VehicleDef def) => def.Armour;

        /// <summary>A unit's armour level on one face.</summary>
        public static int ArmourOf(VehicleDef def, ArmorFace face) => def.Armour[face];

        /// <summary>A boss part's armour level (the same all round).</summary>
        public static int PartArmour(VehicleDef boss, int part) =>
            part >= 0 && part < boss.Parts.Count ? boss.Parts[part].ArmourOn(boss) : boss.Armour.Front;

        /// <summary>The face a weapon's rounds strike on a unit facing it: the roof for top attacks and everything that falls from above, else the front.</summary>
        public static ArmorFace FaceStruck(WeaponDef weapon) => Armour.StrikesTop(weapon) ? ArmorFace.Top : ArmorFace.Front;

        /// <summary>
        /// A weapon's multiplier in a column of the effect table (penetration times damage type); 0 when it
        /// cannot reach that kind of target (a SAM on the ground, a tank gun in the air).
        /// </summary>
        public static float Effect(DamageTable table, WeaponDef weapon, EffectColumn column)
        {
            if (weapon.Damage <= 0f) return 0f;
            switch (column)
            {
                case EffectColumn.Air:
                    return weapon.CanTarget(true) ? table.Effective(weapon, AirLevel, TargetKind.Air) : 0f;
                case EffectColumn.Structure:
                    return weapon.CanTarget(false) ? table.Effective(weapon, StructureLevel, TargetKind.Structure) : 0f;
                default:
                    return weapon.CanTarget(false) ? table.Effective(weapon, (int)column, TargetKind.Ground) : 0f;
            }
        }

        /// <summary>A weapon's whole effect row (<see cref="EffectColumn"/> order).</summary>
        public static float[] EffectRow(DamageTable table, WeaponDef weapon)
        {
            var row = new float[ColumnCount];
            for (var c = 0; c < row.Length; c++) row[c] = Effect(table, weapon, (EffectColumn)c);
            return row;
        }

        /// <summary>
        /// A weapon's multiplier against a unit facing it (its front, or its roof for rounds that strike the roof and
        /// for an aeroplane's fire, <paramref name="fromAbove"/>); 0 when it cannot reach it.
        /// </summary>
        public static float Against(DamageTable table, WeaponDef weapon, VehicleDef target, bool fromAbove = false)
        {
            if (weapon.Damage <= 0f || !weapon.CanTarget(target.Flying)) return 0f;
            var face = fromAbove && !target.Flying ? ArmorFace.Top : FaceStruck(weapon);
            return table.Effective(weapon, target.Armour[face], target.Kind);
        }

        /// <summary>
        /// A weapon's multiplier against a typical unit of a broad class facing it (light: an armoured car, level 1;
        /// heavy: a battle tank, 3/2/1/1; air: level 0; structure: a concrete tower, 2): the design document's and
        /// the measurements' tables by class.
        /// </summary>
        public static float ClassEffect(DamageTable table, WeaponDef weapon, ArmorClass armor)
        {
            if (weapon.Damage <= 0f || !weapon.CanTarget(armor == ArmorClass.Air)) return 0f;
            var levels = armor == ArmorClass.Structure ? ArmourLevels.Uniform(StructureLevel) : ArmourLevels.OfClass(armor);
            var kind = armor switch { ArmorClass.Air => TargetKind.Air, ArmorClass.Structure => TargetKind.Structure, _ => TargetKind.Ground };
            var face = armor is ArmorClass.Air or ArmorClass.Structure ? ArmorFace.Front : FaceStruck(weapon);
            return table.Effective(weapon, levels[face], kind);
        }

        public static MatchVerdict Verdict(float effect) => effect >= GoodAt ? MatchVerdict.Good : effect >= PoorAt ? MatchVerdict.Poor : MatchVerdict.None;

        /// <summary>Prompt 15 E.5: ✓ ~ ✕ for our unit's main weapon against an enemy facing it.</summary>
        public static MatchVerdict Verdict(DamageTable table, VehicleDef ours, VehicleDef theirs) =>
            Verdict(Against(table, ours.Weapon, theirs, ours.Flying && ours.FixedWing));

        /// <summary>The typical weapon a threat stands for: its damage type, penetration and whether it strikes the roof.</summary>
        public static (DamageType type, int pen, bool top) ThreatProfile(Threat threat) => threat switch
        {
            Threat.SmallArms => (DamageType.Kinetic, 0, false),
            Threat.HeavyMachineGuns => (DamageType.Kinetic, 1, false),
            Threat.Fire => (DamageType.Fire, 1, false),
            Threat.Fragmentation => (DamageType.Fragmentation, 2, false),
            Threat.Autocannons => (DamageType.Kinetic, 2, false),
            Threat.HighExplosive => (DamageType.HighExplosive, 2, true),
            Threat.Energy => (DamageType.Energy, 2, false),
            Threat.TopAttack => (DamageType.ShapedCharge, 4, true),
            Threat.ShapedCharges => (DamageType.ShapedCharge, 4, false),
            _ => (DamageType.Kinetic, 4, false),
        };

        /// <summary>What a threat's typical weapon does to a unit (0 for those that cannot reach the air or the ground).</summary>
        public static float ThreatEffect(DamageTable table, Threat threat, VehicleDef target)
        {
            var (type, pen, top) = ThreatProfile(threat);
            // Aircraft are hit by what can shoot upwards: guns, flak, anti-air missiles, beams; roof hits do not apply.
            if (target.Flying && (top || type is DamageType.HighExplosive or DamageType.Fire or DamageType.ShapedCharge)) return 0f;
            var armour = target.Armour[top ? ArmorFace.Top : ArmorFace.Front];
            return table.Effective(type, pen, armour, target.Kind);
        }

        /// <summary>Prompt 15 E.2: a unit's strong / weak summary, from its armour and its weapons (main first).</summary>
        public static StrengthSummary Summary(DamageTable table, VehicleDef def)
        {
            var best = new float[ColumnCount];
            foreach (var mount in def.Mounts)
                for (var c = 0; c < best.Length; c++) best[c] = MathF.Max(best[c], Effect(table, mount.Weapon, (EffectColumn)c));
            var strong = new List<EffectColumn>();
            for (var c = 0; c < best.Length; c++)
                if (best[c] >= GoodAt) strong.Add((EffectColumn)c);
            var weak = new List<Threat>();
            foreach (Threat t in Enum.GetValues(typeof(Threat)))
            {
                // The roof only counts when it is thinner than the front (else "anti-tank missiles" says it).
                if (t == Threat.TopAttack && def.Armour.Top >= def.Armour.Front) continue;
                if (ThreatEffect(table, t, def) >= GoodAt) weak.Add(t);
            }
            return new StrengthSummary(strong, weak, best);
        }
    }
}
