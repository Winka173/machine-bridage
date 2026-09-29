namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The line icon of every tower, utility module, the HQ and every fixed defence (prompt 14 I): a set
    /// of their own in the vehicle icons' style (Icons, "t_" names), never a vehicle's or a support's icon.
    /// They are for small places (counters, chips, tags, a card's corner); cards, slots and the detail
    /// panel keep the 3D renders (<see cref="CardArt"/>). A branch ("aa_turret.flak") shows its tower's icon.
    /// </summary>
    public static class TowerIcons
    {
        /// <summary>The structure's icon, or null when <paramref name="id"/> is not a structure.</summary>
        public static string For(string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            var dot = id.IndexOf('.');
            return (dot > 0 ? id.Substring(0, dot) : id) switch
            {
                "headquarters" => "hq",
                // Towers.
                "guard_tower" => "t_guard",
                "mg_bunker" => "t_mg",
                "aa_turret" => "t_aa",
                "ew_tower" => "t_ew",
                "dragons_teeth" => "t_teeth",
                "minefield" => "t_mines",
                "gun_turret" => "t_gun",
                "atgm_tower" => "t_atgm",
                "rocket_turret" => "t_rockets",
                "c_ram" => "t_cram",
                "gun_pit" => "t_pit",
                "artillery_emplacement" => "t_artillery",
                "missile_battery" => "t_patriot",
                "drone_hangar" => "t_hangar",
                "heavy_turret" => "t_fortress",
                // Utility modules.
                "repair_bay" => "t_repair",
                "ammo_depot" => "t_ammo",
                "airfield" => "t_airfield",
                "logistics_station" => "t_logistics",
                "radar_station" => "t_radar",
                // Fixed defences of the modes and bosses.
                "spawn_bastion" => "t_bastion",
                "bulwark_post" => "t_post",
                "super_gun" => "t_supergun",
                "rail_supergun" => "t_supergun",
                "targeting_station" => "t_targeting",
                _ => null,
            };
        }
    }
}
