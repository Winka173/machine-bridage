using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Hud
{
    /// <summary>What the damage-type table reads a target as (the sim's TargetKind).</summary>
    public enum ArmourKind
    {
        Ground,
        Air,
        Structure,
    }

    /// <summary>How well a weapon pierces a target, for the enemy tooltip's marks (prompt 15 E5).</summary>
    public enum Verdict
    {
        /// <summary>✓ at least ×0.7: it pierces (a level above, or level with the armour).</summary>
        Good,

        /// <summary>~ ×0.3 to 0.7: one level short.</summary>
        Poor,

        /// <summary>✕ under ×0.3: two levels short or more, or a type the target shrugs off.</summary>
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

        /// <summary>0 front, 1 side, 2 rear, 3 top.</summary>
        public int this[int face] => face switch { 0 => Front, 1 => Side, 2 => Rear, _ => Top };

        public bool Uniform => Front == Side && Side == Rear && Rear == Top;
    }

    /// <summary>One weapon as the icons show it: its form, its damage type and tags, its penetration.</summary>
    public sealed class WeaponFacts
    {
        public string Id;

        /// <summary>The sim's WeaponForm name ("Atgm", "DoubleDart"...).</summary>
        public string Form;

        /// <summary>The sim's DamageType name ("Kinetic", "ShapedCharge"...).</summary>
        public string Damage;

        /// <summary>Penetration level 0-4.</summary>
        public int Pen;

        public bool Thermobaric, TopAttack, Guided, Splash;

        public WeaponDef Def;
    }

    /// <summary>
    /// The UI's one door to the combat data of prompt 15 (armour levels by face, penetration, damage types, weapon
    /// forms and tags, the multiplier). The icons and screens ask only this class, so the sim's model is read in one
    /// place.
    /// </summary>
    public static class CombatFacts
    {
        public const int Levels = 5;

        /// <summary>✓ from this multiplier up.</summary>
        public const float GoodFrom = 0.7f;

        /// <summary>~ from this multiplier up (✕ below).</summary>
        public const float PoorFrom = 0.3f;

        public static Verdict Judge(float multiplier) =>
            multiplier >= GoodFrom ? Verdict.Good : multiplier >= PoorFrom ? Verdict.Poor : Verdict.None;

        /// <summary>The verdict of <paramref name="weapon"/> against the target's front armour.</summary>
        public static Verdict Judge(WeaponFacts weapon, ArmourFaces target) =>
            weapon == null ? Verdict.None : Judge(Multiplier(weapon, target.Front, target.Kind));

        /// <summary>The penetration factor of prompt 15 B.2: pen above armour x1, level x0.75, one short x0.4, two x0.15, three or more x0.05.</summary>
        public static float PenFactor(int pen, int armour)
        {
            var gap = pen - armour;
            return gap >= 1 ? 1f : gap == 0 ? 0.75f : gap == -1 ? 0.4f : gap == -2 ? 0.15f : 0.05f;
        }

        public static ArmourFaces Armour(VehicleDef def)
        {
            if (def == null) return new ArmourFaces(0, 0, 0, 0, ArmourKind.Ground);
            var kind = def.Flying ? ArmourKind.Air : def.Static || def.Armor == ArmorClass.Structure ? ArmourKind.Structure : ArmourKind.Ground;
            var front = StubFront(def, kind);
            if (kind != ArmourKind.Ground) return new ArmourFaces(front, front, front, front, kind);
            return new ArmourFaces(front, Math.Max(0, front - 1), Math.Max(0, front - 2), Math.Max(0, front - 2), kind);
        }

        /// <summary>A boss part's armour (prompt 15 A.5).</summary>
        public static (int level, ArmourKind kind) PartArmour(VehicleDef boss, int part)
        {
            var armour = Armour(boss);
            return (armour.Front, armour.Kind);
        }

        /// <summary>Every weapon that does damage, main first (a mount that fires nothing has no chip).</summary>
        public static List<WeaponFacts> Weapons(VehicleDef def)
        {
            var list = new List<WeaponFacts>();
            if (def == null) return list;
            var seen = new HashSet<string>();
            foreach (var mount in def.Mounts)
            {
                var w = Of(mount.Weapon);
                if (w == null || !seen.Add(w.Id)) continue;
                list.Add(w);
            }
            return list;
        }

        public static WeaponFacts Of(WeaponDef def)
        {
            if (def == null || def.Id == "none" || def.Damage <= 0f && def.Cluster == null) return null;
            var form = StubForm(def);
            if (form == "None") return null;
            var damage = StubDamage(def, form);
            return new WeaponFacts
            {
                Id = def.Id,
                Def = def,
                Form = form,
                Damage = damage,
                Pen = StubPen(def, form, damage),
                Thermobaric = def.Id.Contains("thermo"),
                TopAttack = def.Projectile is ProjectileKind.Drone or ProjectileKind.Bomb || def.Id.EndsWith("_top", StringComparison.Ordinal),
                Guided = def.Guided,
                Splash = def.SplashRadius > 0.5f,
            };
        }

        /// <summary>The damage multiplier of <paramref name="weapon"/> against armour <paramref name="level"/> of that kind.</summary>
        public static float Multiplier(WeaponFacts weapon, int level, ArmourKind kind)
        {
            if (weapon == null) return 0f;
            return PenFactor(weapon.Pen, level) * StubTypeFactor(weapon, level, kind);
        }

        // ---------------------------------------------------------------- stub (until the sim's prompt 15 model is merged)

        private static int StubFront(VehicleDef def, ArmourKind kind) => kind switch
        {
            ArmourKind.Air => 0,
            ArmourKind.Structure => 2,
            _ => def.Armor == ArmorClass.Heavy ? (def.MaxHp >= 1400f || def.Boss ? 4 : 3) : def.Speed >= 11f ? 0 : 1,
        };

        private static string StubForm(WeaponDef w)
        {
            var size = w.Size;
            var id = w.Id;
            switch (w.Family)
            {
                case "mg": return size < 10f ? "BulletSmall" : "BulletBig";
                case "autocannon": return w.DamageType == DamageType.Flak ? "Airburst" : "BeltedAutocannon";
                case "tank_gun": return size >= 120f ? "DoubleDart" : "Dart";
                case "atgm": return "Atgm";
                case "flame": return "Flame";
                case "howitzer": return "HeShell";
                case "mortar": return "MortarBomb";
                case "rocket": return w.Cluster != null ? "Cluster" : size >= 200f ? "RocketBig" : "RocketSmall";
                case "aa_missile": return "Sam";
                case "cruise": return "Cruise";
                case "ballistic": return "Ballistic";
                case "bomb": return id == "detonator" ? "CarBomb" : id == "guided_bomb" ? "GuidedBomb" : size >= 900f ? "HeavyBomb" : "Bomb";
                case "drone": return id.Contains("lancet") || id.Contains("mothership") ? "Lancet" : id == "shahed" ? "Shahed" : "Fpv";
                case "laser": return "Energy";
                case "railgun": return "Rail";
                case "melee": return id.Contains("drill") ? "Drill" : "Blade";
                case "grenade": return "Grenade";
                case "special": return "SuperShell";
                default: return w.Beam ? "Energy" : "BulletBig";
            }
        }

        private static string StubDamage(WeaponDef w, string form) => form switch
        {
            "Energy" => "Energy",
            "Flame" or "Napalm" => "Fire",
            "Airburst" or "Sam" => "Fragmentation",
            "Atgm" or "Fpv" or "Lancet" => "ShapedCharge",
            _ => w.DamageType switch
            {
                DamageType.HighExplosive => "HighExplosive",
                DamageType.Fire => "Fire",
                DamageType.Flak => "Fragmentation",
                _ => "Kinetic",
            },
        };

        private static int StubPen(WeaponDef w, string form, string damage) => form switch
        {
            "BulletSmall" => 0,
            "BulletBig" => 1,
            "BeltedAutocannon" or "Airburst" or "RocketSmall" => 2,
            "Dart" or "Blade" or "Drill" => 3,
            "DoubleDart" or "Rail" or "Atgm" or "Lancet" => 4,
            "Fpv" => 3,
            _ => damage == "Energy" ? 2 : 1,
        };

        private static float StubTypeFactor(WeaponFacts w, int level, ArmourKind kind)
        {
            switch (w.Damage)
            {
                case "HighExplosive": return kind == ArmourKind.Structure ? (w.Thermobaric ? 2f : 1.5f) : kind == ArmourKind.Air ? 0.25f : 1f;
                case "Fire": return kind == ArmourKind.Air ? 0f : level <= 1 ? 1.2f : 0.5f;
                case "Fragmentation": return kind == ArmourKind.Air ? 1.5f : level == 0 ? 1.2f : 0.6f;
                case "ShapedCharge": return kind == ArmourKind.Air ? 0.5f : 1f;
                default: return kind == ArmourKind.Air && w.Def != null && !w.Def.CanTarget(true) ? 0f : 1f;
            }
        }
    }
}
