#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 15 A: a unit's armour level on each face, 0 (none) to 4 (very thick), 5 for a boss's super-heavy plate
    /// (play-test 6, DECISIONS 21G) and, since Armour/Pen 5 (04/10), the front of the three super-heavy tanks the data names
    /// (titan_tank, elite_heavy_tank, mara_behemoth); no tower has it. Data "armour": one number
    /// (the front; the side one less, the rear and the roof two less, never under 0; a tower, a building or an
    /// aircraft the same all round) or four [front, side, rear, top].
    /// </summary>
    public readonly struct ArmourLevels : IEquatable<ArmourLevels>
    {
        public const int Max = 5;

        /// <summary>The thickest plate a tower, a building or a vehicle's side, rear and roof may have; <see cref="Max"/> is for bosses and a vehicle's front.</summary>
        public static int MaxUnit => global::MachineBrigade.Sim.Content.SimTunables.Weapons.ArmourLevels.MaxUnit;

        /// <summary>
        /// Armour/Pen 5 (04/10, DECISIONS "Armour/Pen 5 and splash/overpen 04/10"): the thickest level a face may carry. A boss any
        /// face to <see cref="Max"/>; a vehicle (not a structure) its front to <see cref="Max"/> (the data gives it to three
        /// super-heavy tanks only); every other face, and every tower or building, to <see cref="MaxUnit"/>.
        /// </summary>
        public static int CapFor(bool boss, bool structure, ArmorFace face) =>
            boss || (!structure && face == ArmorFace.Front) ? Max : MaxUnit;

        public ArmourLevels(int front, int side, int rear, int top)
        {
            Front = Clamp(front);
            Side = Clamp(side);
            Rear = Clamp(rear);
            Top = Clamp(top);
        }

        public int Front { get; }
        public int Side { get; }
        public int Rear { get; }
        public int Top { get; }

        public int this[ArmorFace face] => face switch
        {
            ArmorFace.Side => Side,
            ArmorFace.Rear => Rear,
            ArmorFace.Top => Top,
            _ => Front,
        };

        /// <summary>A vehicle's default faces from its front: side one less, rear and roof two less, none under 0.</summary>
        public static ArmourLevels Vehicle(int front) => new(front, front - 1, front - global::MachineBrigade.Sim.Content.SimTunables.Weapons.ArmourLevels.VehicleFrontSub, front - global::MachineBrigade.Sim.Content.SimTunables.Weapons.ArmourLevels.VehicleFrontSub);

        /// <summary>The same level all round (most towers, buildings and aircraft).</summary>
        public static ArmourLevels Uniform(int level) => new(level, level, level, level);

        /// <summary>A tower with embrasures (a bunker, a casemate): its front one level thicker than the rest.</summary>
        public static ArmourLevels Embrasured(int level) => new(level + 1, level, level, level);

        /// <summary>The same faces with the front raised (an elite's +1, never over 4).</summary>
        public ArmourLevels WithFront(int front) => new(front, Side, Rear, Top);

        /// <summary>The levels a broad class stood for before prompt 15 (hand-built test units, old data).</summary>
        public static ArmourLevels OfClass(ArmorClass armor) => armor switch
        {
            ArmorClass.Heavy => Vehicle(global::MachineBrigade.Sim.Content.SimTunables.Weapons.ArmourLevels.OfClassFront),
            ArmorClass.Light => Vehicle(1),
            ArmorClass.Structure => Uniform(global::MachineBrigade.Sim.Content.SimTunables.Weapons.ArmourLevels.OfClassLevel),
            _ => Uniform(0),
        };

        /// <summary>The broad class these levels stand for on the ground: heavy from front level 3.</summary>
        public ArmorClass GroundClass => Front >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.ArmourLevels.GroundClassFrontMin ? ArmorClass.Heavy : ArmorClass.Light;

        private static int Clamp(int level) => Math.Clamp(level, 0, Max);

        public bool Equals(ArmourLevels other) => Front == other.Front && Side == other.Side && Rear == other.Rear && Top == other.Top;

        public override bool Equals(object? obj) => obj is ArmourLevels other && Equals(other);

        public override int GetHashCode() => Front | (Side << 3) | (Rear << 6) | (Top << 9);

        public override string ToString() => $"{Front}/{Side}/{Rear}/{Top}";
    }

    /// <summary>
    /// Prompt 15 A-B, pure: which face a round strikes and how deep a weapon pierces. The damage table
    /// (<see cref="DamageTable"/>) turns penetration against armour into a multiplier.
    /// </summary>
    public static class Armour
    {
        /// <summary>
        /// The front arc (either side of the nose) and the rear arc (either side of the tail). DECISIONS 20X: the front
        /// 40 degrees (prompt 15's 50), so a round from off the nose strikes the thinner side more often.
        /// </summary>
        public static readonly float FrontArc = SimMath.DegToRad(40f);

        public static readonly float RearArc = SimMath.DegToRad(50f);

        /// <summary>
        /// The face a direct-fire round from <paramref name="from"/> strikes on a unit at <paramref name="at"/>
        /// facing <paramref name="heading"/>: within 40 degrees of the nose the front, within 50 of the tail the rear,
        /// else the side. A round from right on top of it (or a unit the same all round) strikes the front.
        /// </summary>
        public static ArmorFace FaceFrom(Vector2 at, float heading, Vector2 from)
        {
            var toShooter = from - at;
            if (toShooter.LengthSquared() < global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.FaceFromLengthSquaredMax) return ArmorFace.Front;
            var off = MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(toShooter) - heading));
            return off <= FrontArc ? ArmorFace.Front : off >= MathF.PI - RearArc ? ArmorFace.Rear : ArmorFace.Side;
        }

        /// <summary>
        /// Whether a weapon's rounds come down on the roof: top-attack weapons (top-attack missiles, diving drones,
        /// bomblets) and everything that falls from above (shells lobbed by artillery and mortars, artillery
        /// rockets, bombs).
        /// </summary>
        public static bool StrikesTop(WeaponDef weapon) => weapon.TopAttack || weapon.Indirect;

        /// <summary>
        /// Gear balance 04/10: whether a weapon is real indirect fire, the fire ResistIndirect (Overhead Screen, Blast Walls)
        /// cuts: artillery, mortars, lobbed shells and rockets, bombs (canonically indirect: they fall, WeaponDef.Indirect),
        /// anything with a minimum range or the lofted tag. Not a drone (Lancet, FPV, loitering munitions: WeaponDef.Indirect
        /// counts them because they fly over cover) and not a guided top-attack missile (Hellfire, top-attack ATGMs), whatever
        /// their flight. The topAttack flag alone never makes a weapon indirect.
        /// </summary>
        public static bool IndirectFire(WeaponDef weapon) =>
            weapon.Indirect && weapon.Projectile != ProjectileKind.Drone && !(weapon.TopAttack && weapon.Guided);

        /// <summary>
        /// The penetration a blast's fragments carry against a vehicle's armour (prompt 15 B.1: level 1, a heavy
        /// machine gun's), whatever made the blast; against structures and aircraft the blast keeps the round's own.
        /// </summary>
        public static int FragmentPenetration => global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.FragmentPenetration;

        /// <summary>Penetration of a splash from a round of <paramref name="penetration"/> against <paramref name="kind"/>.</summary>
        public static float SplashPenetration(float penetration, TargetKind kind) =>
            kind == TargetKind.Ground ? MathF.Min(penetration, FragmentPenetration) : penetration;

        /// <summary>
        /// Penetration of damage that came with no weapon (a cook-off, a mine, a called strike without its own):
        /// what its type usually carries.
        /// </summary>
        public static int DefaultPenetration(DamageType type) => type switch
        {
            DamageType.ShapedCharge => global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationTypeValue,
            DamageType.Energy => global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationTypeValue2,
            _ => 1,
        };

        /// <summary>
        /// Prompt 15 B.1: the penetration a weapon's rounds carry by what they are (the data's "pen" overrides):
        /// 0 a 7.62 mm machine gun; 1 12.7-14.5 mm, flamethrowers, 20-23 mm flak; 2 autocannons, 30-57 mm flak,
        /// unguided rockets, light shells and bombs, short-range anti-air missiles; 3 76-105 mm guns, light
        /// anti-tank missiles and FPV drones, 152-155 mm shells, heavy rockets and 500 kg bombs, long-range SAMs;
        /// 4 120 mm and up, heavy anti-tank missiles, railguns, 203 mm and up, the heaviest bombs.
        /// </summary>
        public static int DefaultPenetration(WeaponDef w)
        {
            var size = w.Size;
            switch (w.Family)
            {
                case "mg": return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin ? 1 : 0;
                case "autocannon":
                    if (w.DamageType == DamageType.Fragmentation) return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin2 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue : 1;
                    return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin3 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue2 : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeFalse;
                case "grenade": return global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationDefaultPenetration;
                case "tank_gun": return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin4 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue3 : size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin5 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue2 : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeFalse;
                case "howitzer": return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin6 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue3 : size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin7 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue2 : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeFalse;
                case "mortar": return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin6 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue3 : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeFalse;
                case "rocket": return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin6 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue2 : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeFalse;
                case "atgm": return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin8 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue3 : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeFalse2;
                case "aa_missile": return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin9 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue2 : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeFalse;
                case "bomb": return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin10 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue3 : size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin11 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue2 : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeFalse;
                case "cruise": return global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationDefaultPenetration2;
                case "ballistic": return global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationDefaultPenetration3;
                case "drone": return w.DamageType == DamageType.ShapedCharge ? (size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin12 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue3 : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeFalse2) : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationDamageTypeFalse;
                case "flame": return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin12 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue : 1;
                case "laser": return size >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeMin7 ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeTrue2 : global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationSizeFalse;
                case "railgun": return global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationDefaultPenetration3;
                case "melee": return global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationDefaultPenetration2;
                case "special": return global::MachineBrigade.Sim.Content.SimTunables.Weapons.Armour.DefaultPenetrationDefaultPenetration3;
                default: return DefaultPenetration(w.DamageType);
            }
        }

        /// <summary>Prompt 15 D.3: the shape of a weapon's round from its family and size (the data's "form" overrides).</summary>
        public static WeaponForm DefaultForm(WeaponDef w)
        {
            if (w.Damage <= 0f && w.Family == null) return WeaponForm.None;
            if (w.Cluster != null) return WeaponForm.Cluster;
            var size = w.Size;
            switch (w.Family)
            {
                case "mg": return size >= 12f ? WeaponForm.BulletBig : WeaponForm.BulletSmall;
                case "autocannon":
                    if (w.DamageType == DamageType.Fragmentation) return WeaponForm.Airburst;
                    return w.Projectile == ProjectileKind.Shell ? WeaponForm.HeShell : WeaponForm.BeltedAutocannon;
                case "grenade": return WeaponForm.Grenade;
                case "tank_gun": return size >= 120f ? WeaponForm.DoubleDart : WeaponForm.Dart;
                case "howitzer": return WeaponForm.HeShell;
                case "mortar": return WeaponForm.MortarBomb;
                case "rocket": return size >= 200f ? WeaponForm.RocketBig : WeaponForm.RocketSmall;
                case "atgm": return WeaponForm.Atgm;
                case "aa_missile": return WeaponForm.Sam;
                case "bomb": return size >= 900f ? WeaponForm.HeavyBomb : w.Projectile == ProjectileKind.Bomb && w.Guided ? WeaponForm.GuidedBomb : WeaponForm.Bomb;
                case "cruise": return WeaponForm.Cruise;
                case "ballistic": return WeaponForm.Ballistic;
                case "drone":
                    if (w.DamageType == DamageType.HighExplosive) return WeaponForm.Shahed;
                    return size >= 3f ? WeaponForm.Lancet : WeaponForm.Fpv;
                case "flame": return WeaponForm.Flame;
                case "laser": return WeaponForm.Energy;
                case "railgun": return WeaponForm.Rail;
                case "melee": return size >= 2f ? WeaponForm.Drill : WeaponForm.Blade;
                case "special": return WeaponForm.SuperShell;
                default: return WeaponForm.None;
            }
        }
    }
}
