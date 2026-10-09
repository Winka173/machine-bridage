using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// What a vehicle must have for a piece of vehicle equipment, a stat line, a trait, a module or a
    /// brand to do anything (the vehicle counterpart of <see cref="TowerNeed"/>). The weapon needs
    /// include <see cref="Armed"/>.
    /// </summary>
    [Flags]
    public enum VehicleNeed
    {
        /// <summary>Works on anything (health, resistances, vision, repairs, economy).</summary>
        None = 0,

        /// <summary>A main weapon that does damage.</summary>
        Armed = 1,

        /// <summary>A main weapon for ground targets.</summary>
        HitsGround = 2 | Armed,

        /// <summary>A main weapon that hits aircraft, or an anti-aircraft secondary (flak, a SAM).</summary>
        HitsAir = 4 | Armed,

        /// <summary>A main weapon with a magazine that runs dry and reloads (a launcher).</summary>
        Magazine = 8 | Armed,

        /// <summary>A main weapon that fires more than one round a pull.</summary>
        Burst = 16 | Armed,

        /// <summary>A main weapon that lobs over cover or drops: artillery, mortars, rocket artillery, bombs, drones.</summary>
        Lobs = 32 | Armed,

        /// <summary>A main weapon that fires straight at its target (not over cover).</summary>
        Direct = 64 | Armed,

        /// <summary>A main weapon of rockets, missiles or drones.</summary>
        RocketLike = 128 | Armed,

        /// <summary>A main weapon whose rounds fly unguided (a spread to tighten, a target to lead).</summary>
        Unguided = 256 | Armed,

        /// <summary>A turret that turns on its own.</summary>
        Turret = 512,

        /// <summary>A ground vehicle.</summary>
        Ground = 1024,

        /// <summary>An aircraft.</summary>
        Flying = 2048,

        /// <summary>It can take objectives.</summary>
        Captures = 4096,

        /// <summary>A secondary gun (bullets).</summary>
        SecondaryGun = 8192,

        /// <summary>Heavy armour.</summary>
        Heavy = 16384,

        /// <summary>A secondary weapon that does damage.</summary>
        Secondary = 32768,

        /// <summary>Prompt 29 L5: flares as charges (<see cref="VehicleDef.FlareCharges"/> above 0); the heat decoys need them.</summary>
        Flares = 65536,

        /// <summary>Prompt 29 L5: an APS of its own or room for one (<see cref="VehicleDef.ApsCapability"/> not None); Trophy needs it.</summary>
        ApsMount = 131072,
    }

    /// <summary>
    /// The equipment fit matrix for vehicles (prompt 8 I.1), read from the data: each card's weapons
    /// and body say what it has (<see cref="Of(VehicleDef)"/>), each line what it needs. A class of
    /// vehicles meets a need when at least a third of its cards do (a real share of the class, not a
    /// lone oddity such as the BMPT's anti-aircraft cannon among the tanks); a branch fits a piece when one of its
    /// classes meets the piece's need. Pieces that fit no branch never drop; the equipment screen
    /// only puts a piece on a branch it fits. Which branch each class belongs to is data too
    /// (balance.json "branches", <see cref="VehicleDef.Branch"/>).
    /// </summary>
    public static class VehicleFit
    {
        public static bool Within(VehicleNeed need, VehicleNeed has) => (need & ~has) == 0;

        /// <summary>
        /// Prompt 29 L5 (DECISIONS "Prompt 29 local UI"): hardware a few cards carry (flares as charges, an APS mount). A class
        /// meets a need with hardware when a third of its cards meet the rest and at least one card has the hardware too, so
        /// the module still goes on the branch; <see cref="WorksOn"/> says which vehicles it does anything for.
        /// </summary>
        public const VehicleNeed Hardware = VehicleNeed.Flares | VehicleNeed.ApsMount;

        /// <summary>Whether a vehicle piece does anything on this vehicle's hardware (only the hardware needs are checked here).</summary>
        public static bool WorksOn(GearItem item, VehicleDef def)
        {
            if (item == null || def == null) return true;
            var need = Need(item);
            return (need & Hardware) == 0 || Within(need, Of(def));
        }

        /// <summary>The cards of a branch a piece with hardware needs works on (empty for a piece without them).</summary>
        public static List<string> CardsFor(GearItem item, GearBranch branch)
        {
            var list = new List<string>();
            var need = Need(item);
            if ((need & Hardware) == 0) return list;
            var catalog = TowerFit.GameCatalog;
            foreach (var id in MatchSettings.AllVehicles)
                if (catalog.Vehicles.TryGetValue(id, out var def) && !def.Boss && !def.Static && !def.Elite && Gear.BranchOf(def) == branch && Within(need, Of(def)))
                    list.Add(id);
            return list;
        }

        /// <summary>
        /// What a vehicle def has. Its main weapon counts for everything it can hit; a secondary only
        /// for what it is made for (a coaxial machine gun that can also shoot at aircraft does not make
        /// a tank an anti-air vehicle; a SAM or flak on the roof does).
        /// </summary>
        public static VehicleNeed Of(VehicleDef def)
        {
            var has = VehicleNeed.None;
            if (def == null) return has;
            has |= def.Flying ? VehicleNeed.Flying : VehicleNeed.Ground;
            if (def.CaptureRate > 0f && !def.Flying) has |= VehicleNeed.Captures;
            if (def.Armor == ArmorClass.Heavy) has |= VehicleNeed.Heavy;
            if (def.Mounts[0].Aim == MountAim.Turret && !def.Flying) has |= VehicleNeed.Turret;
            if (def.FlareCharges > 0) has |= VehicleNeed.Flares;
            if (def.ApsCapability != ApsCapability.None) has |= VehicleNeed.ApsMount;
            for (var i = 0; i < def.Mounts.Count; i++)
            {
                var w = def.Mounts[i].Weapon;
                if (w == null || w.Damage <= 0f) continue;
                if (i == 0)
                {
                    has |= VehicleNeed.Armed;
                    if (w.CanTarget(false)) has |= VehicleNeed.HitsGround;
                    if (w.CanTarget(true)) has |= VehicleNeed.HitsAir;
                    if (w.Ammo > 0) has |= VehicleNeed.Magazine;
                    if (w.Burst > 1) has |= VehicleNeed.Burst;
                    if (w.Indirect) has |= VehicleNeed.Lobs;
                    else has |= VehicleNeed.Direct;
                    if (w.Projectile is ProjectileKind.Rocket or ProjectileKind.Missile or ProjectileKind.Drone) has |= VehicleNeed.RocketLike;
                    if (!w.Guided && !w.Beam) has |= VehicleNeed.Unguided;
                    continue;
                }
                has |= VehicleNeed.Secondary;
                if (w.Projectile == ProjectileKind.Bullet) has |= VehicleNeed.SecondaryGun;
                if (w.CanTarget(true) && (w.DamageType == DamageType.Fragmentation || w.Targets == TargetLayers.Air)) has |= VehicleNeed.HitsAir;
            }
            return has;
        }

        /// <summary>What a vehicle needs for this stat line to change anything.</summary>
        public static VehicleNeed Need(StatId stat) => stat switch
        {
            StatId.Damage or StatId.FireRate or StatId.Range or StatId.ProjectileSpeed or StatId.Splash or StatId.BurnDamage => VehicleNeed.Armed,
            StatId.Spread or StatId.SpreadLong => VehicleNeed.Unguided,
            StatId.SpreadMoving => VehicleNeed.Unguided | VehicleNeed.Ground,
            StatId.DamageVsLight or StatId.DamageVsHeavy or StatId.DamageVsStructure => VehicleNeed.HitsGround,
            StatId.DamageVsAir => VehicleNeed.HitsAir,
            StatId.Magazine or StatId.MagazineReload or StatId.SpareMagazine => VehicleNeed.Magazine,
            StatId.SecondaryFireRate => VehicleNeed.Secondary,
            StatId.SalvoInterval => VehicleNeed.Burst,
            StatId.TurretRate => VehicleNeed.Turret,
            StatId.CaptureRate => VehicleNeed.Captures,
            StatId.ResistIndirect or StatId.ResistMine or StatId.ResistFrontal or StatId.ResistBlast or StatId.ReverseSpeed or StatId.LaserWarning => VehicleNeed.Ground,
            StatId.ResistFragmentation or StatId.ArmourAll => VehicleNeed.Flying,
            StatId.Penetration => VehicleNeed.Armed,
            StatId.ArmourSide => VehicleNeed.Ground,
            StatId.DamageFlank => VehicleNeed.Direct | VehicleNeed.HitsGround | VehicleNeed.Ground,
            StatId.DamageVsDrone => VehicleNeed.Armed | VehicleNeed.Ground,
            _ => VehicleNeed.None,
        };

        /// <summary>What a base type's main and implicit lines need (its drawback does not count).</summary>
        public static VehicleNeed Need(BaseTypeDef b)
        {
            if (b == null) return VehicleNeed.None;
            // The implicit line is what sets a base type apart: it fits where that works. A merged type
            // (two implicit lines) fits where either works.
            var implicitNeed = b.Implicit != StatId.Count ? Need(b.Implicit) : VehicleNeed.None;
            if (b.Implicit2 != StatId.Count) implicitNeed &= Need(b.Implicit2);
            return Need(Gear.MainStatOf(b)) | implicitNeed;
        }

        /// <summary>What a brand's two-piece (<paramref name="four"/> false) or four-piece bonus needs.</summary>
        public static VehicleNeed Need(BrandDef brand, bool four)
        {
            if (four) return TraitNeed(brand.FourPiece.Id);
            if (brand.TwoPiece.Id != TraitId.None) return TraitNeed(brand.TwoPiece.Id);
            return brand.Stat == StatId.Count ? VehicleNeed.None : Need(brand.Stat);
        }

        /// <summary>What a trait or a set behaviour needs (the catalogue's traits say theirs; the set behaviours are listed here).</summary>
        public static VehicleNeed TraitNeed(TraitId id)
        {
            if (GearCatalog.Trait(id) is { } t && !Gear.IsTower(t.Slot)) return t.Needs;
            return id switch
            {
                TraitId.SetBulwark or TraitId.SetHitAndRun => VehicleNeed.Ground,
                TraitId.SetFirestorm or TraitId.SetDeepStrike or TraitId.SetHeavyRound or TraitId.SetSwarm or TraitId.SetPackHunt or TraitId.SetPackFocus
                    or TraitId.SetSalvageRights => VehicleNeed.Armed,
                TraitId.SetStrafingRun => VehicleNeed.Armed,
                _ => VehicleNeed.None,
            };
        }

        /// <summary>What a piece needs: its base type (or module) and its trait (sub-stats are extras that may or may not tell).</summary>
        public static VehicleNeed Need(GearItem item)
        {
            if (item == null) return VehicleNeed.None;
            if (item.Slot == GearSlot.Special) return GearCatalog.Module(item.Module)?.Needs ?? VehicleNeed.None;
            var need = Gear.BaseOf(item) is { } b ? Need(b) : Need(Gear.MainStat(item));
            if (item.rarity >= (int)Rarity.Epic && !string.IsNullOrEmpty(item.trait)) need |= TraitNeed(GearKeys.ParseTrait(item.trait));
            return need;
        }

        // ------------------------------------------------------------------ the roster

        private static Dictionary<(UnitClass cls, GearBranch branch), List<VehicleNeed>> _classes;
        private static Catalog _for;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            _classes = null;
            _for = null;
        }

        /// <summary>The cards a player can field, by class and branch, each with what it has.</summary>
        private static Dictionary<(UnitClass cls, GearBranch branch), List<VehicleNeed>> Classes()
        {
            var catalog = TowerFit.GameCatalog;
            if (_classes != null && _for == catalog) return _classes;
            _for = catalog;
            _classes = new Dictionary<(UnitClass, GearBranch), List<VehicleNeed>>();
            foreach (var id in MatchSettings.AllVehicles)
            {
                if (!catalog.Vehicles.TryGetValue(id, out var def) || def.Boss || def.Static || def.Elite) continue;
                var key = (def.Class, Gear.BranchOf(def));
                if (!_classes.TryGetValue(key, out var list)) _classes[key] = list = new List<VehicleNeed>();
                list.Add(Of(def));
            }
            return _classes;
        }

        /// <summary>The classes of a branch (with how many cards each has), in the order the roster lists them.</summary>
        public static List<(UnitClass cls, int cards)> ClassesOf(GearBranch branch)
        {
            var list = new List<(UnitClass, int)>();
            foreach (var pair in Classes())
                if (pair.Key.branch == branch) list.Add((pair.Key.cls, pair.Value.Count));
            list.Sort((a, b) => a.Item1.CompareTo(b.Item1));
            return list;
        }

        /// <summary>Whether a class of a branch meets a need: at least a third of its cards have everything it asks.</summary>
        public static bool ClassMeets(UnitClass cls, GearBranch branch, VehicleNeed need)
        {
            if (!Classes().TryGetValue((cls, branch), out var cards) || cards.Count == 0) return false;
            var n = 0;
            var hardware = (need & Hardware) == 0;
            foreach (var has in cards)
            {
                if (Within(need & ~Hardware, has)) n++;
                if (Within(need, has)) hardware = true;
            }
            return hardware && n * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.VehicleFit.ClassMeetsNScale >= cards.Count;
        }

        /// <summary>Whether a branch fits a need: one of its classes meets it.</summary>
        public static bool Fits(VehicleNeed need, GearBranch branch)
        {
            foreach (var pair in Classes())
                if (pair.Key.branch == branch && ClassMeets(pair.Key.cls, branch, need)) return true;
            return false;
        }

        /// <summary>The branches where a trait works together with a base type (both on one class's vehicles).</summary>
        public static BranchMask BranchesFor(BaseTypeDef b, TraitDef t) => BranchesFor((b != null ? Need(b) : VehicleNeed.None) | (t?.Needs ?? VehicleNeed.None));

        /// <summary>The branches that fit a need.</summary>
        public static BranchMask BranchesFor(VehicleNeed need)
        {
            var mask = BranchMask.None;
            foreach (GearBranch branch in Enum.GetValues(typeof(GearBranch)))
                if (Fits(need, branch)) mask |= GearCatalog.MaskOf(branch);
            return mask;
        }

        /// <summary>Whether a vehicle piece works for a branch (a tower piece never does).</summary>
        public static bool Fits(GearItem item, GearBranch branch) => item != null && !Gear.IsTower(item.Slot) && Fits(Need(item), branch);

        /// <summary>How many classes, over the whole roster, meet a need (a line that suits only one is dropped, merged or widened).</summary>
        public static int ClassesMeeting(VehicleNeed need)
        {
            var n = 0;
            foreach (var pair in Classes())
                if (ClassMeets(pair.Key.cls, pair.Key.branch, need)) n++;
            return n;
        }
    }
}
