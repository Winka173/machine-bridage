#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>The Part B doctrine a combat unit fights by (from its AI role, its kind, and its component state).</summary>
    public enum DoctrineRole : byte
    {
        Generic,
        Breacher,
        Siege,
        TankDestroyer,
        MainBattle,
        LightCombat,
        AntiAir,
        FireSupport,
        Recon,
        Support,
        Bomber,
        Fighter,
        LoiterAntiArmour,
        LoiterAntiArtillery,

        /// <summary>Part F1: the main gun is lost: secondary weapons, self-defence, screen / objective body.</summary>
        Screen,
    }

    /// <summary>What a target is, for the role ladders of Part B.</summary>
    public enum TargetClass : byte
    {
        Other,
        SuperHeavy,
        Armour4,
        Heavy,
        Mbt,
        AntiTank,
        Medium,
        Light,
        Recon,
        Artillery,
        SamRadar,
        Support,
        Tower,
        Structure,
        Blocking,
        Boss,
        Bomber,
        StrikeAir,
        Fighter,
        Helicopter,
        Drone,
    }

    /// <summary>
    /// AI MASTER P2 Part B (all roles): RoleDoctrine as a multiplier on the existing target score (which already is B1's
    /// product: weapon suitability x finishing x worth x threat x focus x distance, P0-A's aim / stickiness / objective /
    /// overkill factors). Each role has its priority ladder: rung 1 x <see cref="Tun.RoleDoctrine.RankTop"/>, each lower rung
    /// x <see cref="Tun.RoleDoctrine.RankStep"/>, targets the ladder does not name one rung below its last, and "only when no
    /// better target" classes x <see cref="Tun.RoleDoctrine.LastResort"/> unless they are an immediate survival threat or a
    /// critical objective threat. A multiplier, so a last-resort target is still shot when it is the only one (never an idle
    /// gun). B2 breacher and B3 siege stay P0-A's (CombatSystem.DoctrineWorth); this class adds B4-B13 and F1's screen.
    /// Applied to the main weapon only: secondary mounts (a tank's machine gun) keep the generic score.
    /// </summary>
    public static class CombatRoleDoctrine
    {
        /// <summary>The doctrine of <paramref name="v"/>, its component state applied (F1: a lost main gun makes it a screen).</summary>
        public static DoctrineRole RoleOf(SimWorld world, Vehicle v)
        {
            var role = BaseRole(world, v);
            if (role is DoctrineRole.Generic or DoctrineRole.Support or DoctrineRole.Recon) return role;
            return world.Components.Of(v).MainGunLost ? DoctrineRole.Screen : role;
        }

        /// <summary>The doctrine from the unit's AI role id (balance.json aiBehaviour.units), its flags and its class.</summary>
        public static DoctrineRole BaseRole(SimWorld world, Vehicle v)
        {
            var def = v.Def;
            if (def.Breacher || def.WallBreaker) return DoctrineRole.Breacher;
            var role = world.Catalog.AiData.RoleOf(def.Id)?.Id;
            if (def.Deploy is { Siege: true } || role == "Siege") return DoctrineRole.Siege;
            if (def.Id.IndexOf("lancet", StringComparison.Ordinal) >= 0) return DoctrineRole.LoiterAntiArtillery;
            switch (role)
            {
                case "TD":
                case "Rail":
                    return DoctrineRole.TankDestroyer;
                case "MBT":
                case "Heavy":
                    return DoctrineRole.MainBattle;
                case "IFV":
                case "Light":
                case "Flame":
                    return DoctrineRole.LightCombat;
                case "SPAAG":
                case "SAM":
                case "Laser":
                    return DoctrineRole.AntiAir;
                case "Arty":
                case "MLRS":
                case "Strike":
                    return DoctrineRole.FireSupport;
                case "Recon":
                case "ScoutHeli":
                    return DoctrineRole.Recon;
                case "UAV":
                    return def.Weapon.Damage > 0f && def.Id.IndexOf("strike", StringComparison.Ordinal) >= 0 ? DoctrineRole.LoiterAntiArmour : DoctrineRole.Recon;
                case "Drone":
                    return DoctrineRole.LoiterAntiArmour;
                case "Support":
                    return DoctrineRole.Support;
                case "Bomber":
                case "CAS":
                    return DoctrineRole.Bomber;
                case "Fighter":
                case "Stealth":
                    return DoctrineRole.Fighter;
            }
            switch (def.Class)
            {
                case UnitClass.Tank:
                case UnitClass.Heavy:
                    return DoctrineRole.MainBattle;
                case UnitClass.TankHunter:
                    return DoctrineRole.TankDestroyer;
                case UnitClass.Scout:
                    return DoctrineRole.Recon;
                case UnitClass.Light:
                    return DoctrineRole.LightCombat;
                case UnitClass.AntiAir:
                    return DoctrineRole.AntiAir;
                case UnitClass.Artillery:
                    return DoctrineRole.FireSupport;
                case UnitClass.Support:
                    return DoctrineRole.Support;
            }
            return def.Weapon.MinRange > 0f && !def.Static ? DoctrineRole.FireSupport : DoctrineRole.Generic;
        }

        /// <summary>What <paramref name="t"/> is for the ladders.</summary>
        public static TargetClass ClassOf(SimWorld world, Vehicle t)
        {
            var def = t.Def;
            if (def.Boss || t.HasParts) return TargetClass.Boss;
            if (def.Static)
            {
                if (def.Wall || def.Obstacle) return TargetClass.Blocking;
                return def.Weapon.Damage > 0f ? TargetClass.Tower : TargetClass.Structure;
            }
            var role = world.Catalog.AiData.RoleOf(def.Id)?.Id;
            if (t.Flying)
            {
                switch (role)
                {
                    case "Bomber": return TargetClass.Bomber;
                    case "CAS":
                    case "Strike": return TargetClass.StrikeAir;
                    case "Fighter":
                    case "Stealth": return TargetClass.Fighter;
                    case "UAV":
                    case "Drone": return TargetClass.Drone;
                }
                return def.Class == UnitClass.Helicopter ? TargetClass.Helicopter : def.Class == UnitClass.Plane ? TargetClass.StrikeAir : TargetClass.Drone;
            }
            if (role is "Arty" or "MLRS" or "Strike" || def.Class == UnitClass.Artillery || def.Weapon.MinRange > 0f) return TargetClass.Artillery;
            if (role is "SAM" or "SPAAG" or "Laser" || def.Class == UnitClass.AntiAir) return TargetClass.SamRadar;
            if (role is "TD" or "Rail" || def.Class == UnitClass.TankHunter) return TargetClass.AntiTank;
            if (role == "Support" || def.Class == UnitClass.Support) return TargetClass.Support;
            if (role == "Recon" || def.Class == UnitClass.Scout) return TargetClass.Recon;
            var front = t.Armour.Front;
            if (front >= 5) return TargetClass.SuperHeavy;
            if (front >= 4) return TargetClass.Armour4;
            if (role == "Heavy" || def.Class == UnitClass.Heavy) return TargetClass.Heavy;
            if (role == "MBT" || def.Class == UnitClass.Tank) return TargetClass.Mbt;
            return t.Armor == ArmorClass.Light ? TargetClass.Light : TargetClass.Medium;
        }

        private static bool HeavyArmour(TargetClass c) => c is TargetClass.SuperHeavy or TargetClass.Armour4 or TargetClass.Heavy or TargetClass.Mbt;

        private static bool LightTarget(TargetClass c) => c is TargetClass.Light or TargetClass.Recon or TargetClass.Support;

        private static bool Air(TargetClass c) => c is TargetClass.Bomber or TargetClass.StrikeAir or TargetClass.Fighter or TargetClass.Helicopter or TargetClass.Drone;

        /// <summary>The multiplier for a rung (1-based); 0: one rung below the ladder's last (<paramref name="rungs"/>).</summary>
        private static float Rung(int rung, int rungs)
        {
            var r = rung > 0 ? rung : rungs + 1;
            return Tun.RoleDoctrine.RankTop * MathF.Pow(Tun.RoleDoctrine.RankStep, r - 1);
        }

        /// <summary>
        /// Part B: the role's factor on the score of <paramref name="other"/> for <paramref name="v"/>'s main weapon.
        /// <paramref name="survival"/>: the target is an immediate survival threat; <paramref name="objectiveThreat"/>: Part H's
        /// ThreatToObjective (0-1); <paramref name="clustered"/>: other enemies stand around it (B8, B11).
        /// </summary>
        public static float Worth(DoctrineRole role, TargetClass c, bool survival, float objectiveThreat, bool clustered, bool targetsOwnHeavy,
            bool moving, float targetWorth, bool salvoWeapon)
        {
            var critical = survival || objectiveThreat >= 0.7f;
            float LastResort() => critical ? Rung(0, 6) : Tun.RoleDoctrine.LastResort;
            switch (role)
            {
                case DoctrineRole.TankDestroyer:
                    // B4: Armour5, Armour4, heavy, boss, MBT, medium; light only when nothing better or critical.
                    return c switch
                    {
                        TargetClass.SuperHeavy => Rung(1, 6),
                        TargetClass.Armour4 => Rung(2, 6),
                        TargetClass.Heavy => Rung(3, 6),
                        TargetClass.Boss => Rung(4, 6),
                        TargetClass.Mbt => Rung(5, 6),
                        TargetClass.Medium or TargetClass.AntiTank => Rung(6, 6),
                        TargetClass.Light or TargetClass.Recon or TargetClass.Support or TargetClass.Drone => LastResort(),
                        _ => Rung(0, 6),
                    };
                case DoctrineRole.MainBattle:
                    // B5: immediate threat, heavy / MBT, TD threatening our heavies, objective defender, structure, light.
                    if (survival) return Rung(1, 6);
                    if (HeavyArmour(c)) return Rung(2, 6);
                    if (c == TargetClass.AntiTank) return targetsOwnHeavy ? Rung(3, 6) : Rung(4, 6);
                    if (objectiveThreat > 0f) return Rung(4, 6);
                    if (c is TargetClass.Tower or TargetClass.Structure or TargetClass.Boss) return Rung(5, 6);
                    return Rung(6, 6);
                case DoctrineRole.LightCombat:
                    // B6: light, recon, drone / low air, fragile support, medium; heavy only with nothing suitable or in self-defence.
                    return c switch
                    {
                        TargetClass.Light => Rung(1, 5),
                        TargetClass.Recon => Rung(2, 5),
                        TargetClass.Drone or TargetClass.Helicopter => Rung(3, 5),
                        TargetClass.Support or TargetClass.Artillery or TargetClass.SamRadar => Rung(4, 5),
                        TargetClass.Medium or TargetClass.AntiTank => Rung(5, 5),
                        _ when HeavyArmour(c) || c == TargetClass.Boss => LastResort(),
                        _ => Rung(0, 5),
                    };
                case DoctrineRole.AntiAir:
                    // B7: aircraft attacking a protected asset, bomber / strike, gunship, fighter, drone; no ground chase.
                    if (Air(c) && objectiveThreat > 0f) return Rung(1, 5);
                    return c switch
                    {
                        TargetClass.Bomber or TargetClass.StrikeAir => Rung(2, 5),
                        TargetClass.Helicopter => Rung(3, 5),
                        TargetClass.Fighter => Rung(4, 5),
                        TargetClass.Drone => Rung(5, 5),
                        _ => survival ? Rung(0, 5) : Tun.RoleDoctrine.LastResort,
                    };
                case DoctrineRole.FireSupport:
                {
                    // B8: counter-battery, tower / defensive cluster, dense cluster, static heavy, objective defenders,
                    // isolated light only if urgent; heavy salvo weapons keep a minimum target value.
                    if (salvoWeapon && !clustered && !critical && c != TargetClass.Tower && c != TargetClass.Artillery &&
                        targetWorth < Tun.RoleDoctrine.HeavySalvoMinWorth) return Tun.RoleDoctrine.LastResort;
                    if (c == TargetClass.Artillery) return Rung(1, 6);
                    if (c is TargetClass.Tower or TargetClass.SamRadar) return Rung(2, 6);
                    if (clustered) return Rung(3, 6);
                    if (HeavyArmour(c) && !moving) return Rung(4, 6);
                    if (objectiveThreat > 0f) return Rung(5, 6);
                    if (LightTarget(c)) return LastResort();
                    return Rung(6, 6);
                }
                case DoctrineRole.Bomber:
                    // B11: high-value structure, artillery, SAM / radar, heavy cluster, objective cluster; single light only if urgent.
                    if (c is TargetClass.Structure or TargetClass.Tower or TargetClass.Boss) return Rung(1, 5);
                    if (c == TargetClass.Artillery) return Rung(2, 5);
                    if (c == TargetClass.SamRadar) return Rung(3, 5);
                    if (HeavyArmour(c) && clustered) return Rung(4, 5);
                    if (objectiveThreat > 0f && clustered) return Rung(5, 5);
                    return clustered ? Rung(0, 5) : LastResort();
                case DoctrineRole.Fighter:
                    // B12: bomber, strike aircraft, fighter, gunship / helicopter, drone; ground only if the weapon supports it.
                    return c switch
                    {
                        TargetClass.Bomber => Rung(1, 5),
                        TargetClass.StrikeAir => Rung(2, 5),
                        TargetClass.Fighter => Rung(3, 5),
                        TargetClass.Helicopter => Rung(4, 5),
                        TargetClass.Drone => Rung(5, 5),
                        _ => Rung(0, 5),
                    };
                case DoctrineRole.LoiterAntiArmour:
                    // B13 anti-armour: heavy armour, TD / artillery, expensive support, tower.
                    if (HeavyArmour(c)) return Rung(1, 4);
                    if (c is TargetClass.AntiTank or TargetClass.Artillery) return Rung(2, 4);
                    if (c is TargetClass.Support or TargetClass.SamRadar) return Rung(3, 4);
                    if (c == TargetClass.Tower) return Rung(4, 4);
                    return LightTarget(c) ? LastResort() : Rung(0, 4);
                case DoctrineRole.LoiterAntiArtillery:
                    // B13 Lancet-like: artillery, SAM / radar, parked support, tower, heavy.
                    return c switch
                    {
                        TargetClass.Artillery => Rung(1, 5),
                        TargetClass.SamRadar => Rung(2, 5),
                        TargetClass.Support => Rung(3, 5),
                        TargetClass.Tower => Rung(4, 5),
                        _ when HeavyArmour(c) => Rung(5, 5),
                        _ => LastResort(),
                    };
                case DoctrineRole.Screen:
                    // F1: self-defence and screening: what threatens it or the objective, then light targets its secondaries hurt.
                    if (survival || objectiveThreat > 0f) return Rung(1, 3);
                    if (LightTarget(c) || c == TargetClass.Drone) return Rung(2, 3);
                    return Rung(3, 3);
                default:
                    // Recon (B9: opportunity fire / self-defence only), support (B10), generic: no ladder.
                    return 1f;
            }
        }

        /// <summary>Whether two or more other enemies of <paramref name="t"/>'s side stand within the cluster radius of it.</summary>
        internal static bool Clustered(SimWorld world, Vehicle t)
        {
            var r = Tun.RoleDoctrine.ClusterRadius;
            var n = 0;
            foreach (var o in world.VehicleList)
            {
                if (o == t || !o.IsAlive || o.Team != t.Team || o.Flying != t.Flying) continue;
                if (Vector2.DistanceSquared(o.Position, t.Position) > r * r) continue;
                if (++n >= 2) return true;
            }
            return false;
        }
    }
}
