using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Hud
{
    /// <summary>What a deck covers: tank killers, anti-air, artillery, repair and recon.</summary>
    public readonly struct RoleCover
    {
        public RoleCover(bool antiTank, bool antiAir, bool artillery, bool repair, bool recon)
        {
            AntiTank = antiTank;
            AntiAir = antiAir;
            Artillery = artillery;
            Repair = repair;
            Recon = recon;
        }

        public bool AntiTank { get; }
        public bool AntiAir { get; }
        public bool Artillery { get; }
        public bool Repair { get; }
        public bool Recon { get; }

        /// <summary>The five roles in the Army screen's order: their name key, icon, and whether the deck has one.</summary>
        public IReadOnlyList<(string key, string icon, bool has)> Rows => new List<(string, string, bool)>
        {
            ("army.role.antiTank", "destroyer", AntiTank), ("army.role.antiAir", "aa", AntiAir), ("army.role.artillery", "artillery", Artillery),
            ("army.role.repair", "repair", Repair), ("army.role.recon", "eye", Recon),
        };
    }

    /// <summary>
    /// The deck's role cover, shared by the Army screen's overview and the result screen's defeat
    /// hints (Field Command 2.0, E3 and E10).
    /// </summary>
    public static class DeckRoles
    {
        public static RoleCover Of(Catalog catalog, IEnumerable<string> vehicles, IEnumerable<string> supports)
        {
            bool antiTank = false, air = false, artillery = false, repair = false, recon = false;
            foreach (var id in vehicles)
            {
                if (!catalog.Vehicles.TryGetValue(id, out var def)) continue;
                if (AntiAir(def)) air = true;
                if (def.Class is UnitClass.TankHunter or UnitClass.Heavy or UnitClass.Tank || def.Weapon.AntiArmour) antiTank = true;
                if (def.Weapon.MinRange > 0f) artillery = true;
                if (def.RepairAura != null) repair = true;
                if (def.Class == UnitClass.Scout || def.VisionRange >= 44f) recon = true;
            }
            foreach (var id in supports)
            {
                if (id is "repair_drop" or "field_repair") repair = true;
                if (id is "artillery_barrage") artillery = true;
            }
            return new RoleCover(antiTank, air, artillery, repair, recon);
        }

        /// <summary>A vehicle that shoots at aircraft with flak, or is an anti-air vehicle.</summary>
        public static bool AntiAir(VehicleDef def)
        {
            foreach (var m in def.Mounts)
                if (m.Weapon.CanTarget(true) && (m.Weapon.DamageType == DamageType.Fragmentation || def.Class == UnitClass.AntiAir)) return true;
            return false;
        }
    }
}
