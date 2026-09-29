using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Hud
{
    /// <summary>What the damage-type table reads a target as (the sim's <see cref="TargetKind"/>, same order).</summary>
    public enum ArmourKind
    {
        Ground,
        Air,
        Structure,
    }

    /// <summary>How well a weapon pierces a target, for the enemy tooltip's marks (the sim's <see cref="MatchVerdict"/>, same order).</summary>
    public enum Verdict
    {
        /// <summary>✓ from <see cref="Matchup.GoodAt"/> up.</summary>
        Good,

        /// <summary>~ from <see cref="Matchup.PoorAt"/> up.</summary>
        Poor,

        /// <summary>✕ below that, or a target it cannot reach.</summary>
        None,
    }

    /// <summary>A unit's armour levels (0-4) by face, and how the damage table reads it.</summary>
    public readonly struct ArmourFaces
    {
        public ArmourFaces(int front, int side, int rear, int top, ArmourKind kind)
        {
            Front = front;
            Side = side;
            Rear = rear;
            Top = top;
            Kind = kind;
        }

        public int Front { get; }
        public int Side { get; }
        public int Rear { get; }
        public int Top { get; }
        public ArmourKind Kind { get; }

        /// <summary>0 front, 1 side, 2 rear, 3 top (the sim's <see cref="ArmorFace"/> order).</summary>
        public int this[int face] => face switch { 0 => Front, 1 => Side, 2 => Rear, _ => Top };

        public bool Uniform => Front == Side && Side == Rear && Rear == Top;
    }

    /// <summary>One weapon as the icons show it: its form, its damage type and tags, its penetration.</summary>
    public sealed class WeaponFacts
    {
        public string Id;

        /// <summary>The sim's <see cref="WeaponForm"/> name ("Atgm", "DoubleDart"...).</summary>
        public string Form;

        /// <summary>The sim's <see cref="DamageType"/> name ("Kinetic", "ShapedCharge"...).</summary>
        public string Damage;

        /// <summary>Penetration level 0-4.</summary>
        public int Pen;

        public bool Thermobaric, TopAttack, Guided, Splash;

        /// <summary>The weapon (null for a threat's typical weapon on the Weak line).</summary>
        public WeaponDef Def;
    }

    /// <summary>
    /// The UI's one door to the combat data of prompt 15: the sim's armour levels by face (<see cref="VehicleDef.Armour"/>),
    /// its weapons' penetration, damage types, forms and tags, and its <see cref="Matchup"/> helpers (the multipliers, the
    /// effect table, ✓ ~ ✕, strong / weak). Nothing is worked out here that the sim does not say.
    /// </summary>
    public static class CombatFacts
    {
        public const int Levels = ArmourLevels.Max + 1;

        public const float GoodFrom = Matchup.GoodAt;
        public const float PoorFrom = Matchup.PoorAt;

        private static DamageTable _table;

        /// <summary>The balance's damage table (the catalog's; loaded once).</summary>
        public static DamageTable Table
        {
            get => _table ??= GameContent.LoadCatalog().Damage;
            set => _table = value;
        }

        public static Verdict Judge(float multiplier) => (Verdict)(int)Matchup.Verdict(multiplier);

        public static ArmourKind KindOf(TargetKind kind) => (ArmourKind)(int)kind;

        public static TargetKind KindOf(ArmourKind kind) => (TargetKind)(int)kind;

        public static ArmourFaces Armour(VehicleDef def)
        {
            if (def == null) return new ArmourFaces(0, 0, 0, 0, ArmourKind.Ground);
            var a = def.Armour;
            return new ArmourFaces(a.Front, a.Side, a.Rear, a.Top, KindOf(def.Kind));
        }

        /// <summary>A boss part's armour (the same all round).</summary>
        public static (int level, ArmourKind kind) PartArmour(VehicleDef boss, int part) => (Matchup.PartArmour(boss, part), KindOf(boss.Kind));

        /// <summary>Every weapon that does damage, main first (a mount that fires nothing has no chip).</summary>
        public static List<WeaponFacts> Weapons(VehicleDef def)
        {
            var list = new List<WeaponFacts>();
            if (def == null) return list;
            var seen = new HashSet<string>();
            foreach (var mount in def.Mounts)
            {
                var w = Of(mount.Weapon);
                if (w != null && seen.Add(w.Id)) list.Add(w);
            }
            return list;
        }

        public static WeaponFacts Of(WeaponDef def)
        {
            if (def == null || def.Damage <= 0f || def.Form == WeaponForm.None) return null;
            return new WeaponFacts
            {
                Id = def.Id,
                Def = def,
                Form = def.Form.ToString(),
                Damage = def.DamageType.ToString(),
                Pen = def.Penetration,
                Thermobaric = def.Thermobaric,
                TopAttack = def.TopAttack,
                Guided = def.Guided,
                Splash = def.Splashes,
            };
        }

        /// <summary>The weapon's real multiplier in a column of the effect table (0 when it cannot reach that kind of target).</summary>
        public static float Effect(WeaponFacts weapon, EffectColumn column) =>
            weapon?.Def == null ? 0f : Matchup.Effect(Table, weapon.Def, column);

        /// <summary>The weapon's real multiplier against armour <paramref name="level"/> of that kind (0 when it cannot reach it).</summary>
        public static float Multiplier(WeaponFacts weapon, int level, ArmourKind kind)
        {
            if (weapon?.Def == null || weapon.Def.Damage <= 0f || !weapon.Def.CanTarget(kind == ArmourKind.Air)) return 0f;
            return Table.Effective(weapon.Def, level, KindOf(kind));
        }

        /// <summary>✓ ~ ✕ of our unit's main weapon against an enemy facing it (its front, or its roof for rounds from above).</summary>
        public static Verdict Judge(VehicleDef ours, VehicleDef theirs) => (Verdict)(int)Matchup.Verdict(Table, ours, theirs);

        /// <summary>The multiplier behind <see cref="Judge(VehicleDef, VehicleDef)"/>.</summary>
        public static float Against(VehicleDef ours, VehicleDef theirs) => Matchup.Against(Table, ours.Weapon, theirs);

        public static StrengthSummary Summary(VehicleDef def) => Matchup.Summary(Table, def);

        /// <summary>A threat of the Weak line as a chip: the typical weapon's form and damage type.</summary>
        public static WeaponFacts ThreatChip(Threat threat)
        {
            var (type, pen, top) = Matchup.ThreatProfile(threat);
            var form = threat switch
            {
                Threat.SmallArms => WeaponForm.BulletSmall,
                Threat.HeavyMachineGuns => WeaponForm.BulletBig,
                Threat.Fire => WeaponForm.Flame,
                Threat.Fragmentation => WeaponForm.Airburst,
                Threat.Autocannons => WeaponForm.BeltedAutocannon,
                Threat.HighExplosive => WeaponForm.HeShell,
                Threat.Energy => WeaponForm.Energy,
                Threat.TopAttack => WeaponForm.Atgm,
                Threat.ShapedCharges => WeaponForm.Atgm,
                _ => WeaponForm.DoubleDart,
            };
            return new WeaponFacts { Id = "threat." + threat, Form = form.ToString(), Damage = type.ToString(), Pen = pen, TopAttack = top };
        }
    }
}
