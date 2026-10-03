using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>The four domains a unit lives in (prompt 34 L8): what its preview must stand it on.</summary>
    public enum PreviewDomain
    {
        Ground,
        Water,
        Rail,
        Air,
    }

    /// <summary>The scene a preview builds round a unit (<see cref="PreviewStage"/>).</summary>
    public enum PreviewSetting
    {
        /// <summary>Ground vehicles: the biome's ground.</summary>
        Ground,

        /// <summary>Ships and boats (sea bosses too): a wavy sea; the range's targets stand on the shore beyond.</summary>
        Sea,

        /// <summary>Amphibious and hover vehicles: on the water's edge, the rear over the water.</summary>
        WaterEdge,

        /// <summary>Trains and the rail bosses (Juggernaut, Nemesis, Gungnir): a stretch of track.</summary>
        Rail,

        /// <summary>Aircraft, helicopters and flying bosses: in the air, the biome's ground below.</summary>
        Air,

        /// <summary>Towers and fixed defences: on a base slot's pad.</summary>
        BasePad,

        /// <summary>A coastal gun that fires on ships only: on its pad on the shore, a ship out at sea for its target.</summary>
        Coast,
    }

    /// <summary>
    /// Prompt 34 L8 (DECISIONS "Prompt 34 L8 / L9"): which setting each unit's preview (the turntable, "In action") puts it in.
    /// Read from the unit's own data first (flying, a boss frame's movement, a rail route, a ship's naval block, static), then
    /// from the few ids the data does not mark (the river boats, the hovercraft and the amphibious vehicles move like
    /// ground vehicles in the Sim). View only.
    /// </summary>
    public static class PreviewSettings
    {
        /// <summary>
        /// Ground units that swim or hover: shown on the water's edge (their names say so; the Sim drives them on land).
        /// Play-test 14: the light tank is shown on land, where it fights (owner: "preview trên đất liền").
        /// </summary>
        public static readonly HashSet<string> Amphibious = new HashSet<string>
        {
            "hover_gunboat", "landing_hovercraft",
        };

        /// <summary>The rail bosses by id (their frame and route say so too; the list keeps a variant without them on its track).</summary>
        public static readonly HashSet<string> RailUnits = new HashSet<string> { "armored_train", "nuke_train" };

        public static PreviewSetting Of(VehicleDef def)
        {
            if (def == null) return PreviewSetting.Ground;
            var id = def.Id ?? "";
            if (def.Flying) return PreviewSetting.Air;
            if (def.Frame?.Move == BossMove.Rail || def.RouteName == "rail" || RailUnits.Contains(id) || Has(id, "train"))
                return PreviewSetting.Rail;
            if (def.Naval != null || def.Frame is { Sea: true }) return PreviewSetting.Sea;
            if (def.Frame?.Id == "hovercraft" || Amphibious.Contains(id) || Has(id, "hover") || Has(id, "amphib"))
                return PreviewSetting.WaterEdge;
            if (Has(id, "boat")) return PreviewSetting.Sea;
            if (def.NavalOnly) return PreviewSetting.Coast;
            if (def.Static) return PreviewSetting.BasePad;
            return PreviewSetting.Ground;
        }

        /// <summary>The domain a setting puts its unit in (a pad and a coastal gun's shore are ground).</summary>
        public static PreviewDomain DomainOf(PreviewSetting setting) => setting switch
        {
            PreviewSetting.Air => PreviewDomain.Air,
            PreviewSetting.Rail => PreviewDomain.Rail,
            PreviewSetting.Sea or PreviewSetting.WaterEdge => PreviewDomain.Water,
            _ => PreviewDomain.Ground,
        };

        public static PreviewDomain Domain(VehicleDef def) => DomainOf(Of(def));

        /// <summary>
        /// The biome the previews' ground is drawn in: the chosen map's theme when that map is there to play (the menu only
        /// lets an unlocked map be chosen), else the default temperate one.
        /// </summary>
        public static string Biome()
        {
            try
            {
                var theme = Match.MatchSettings.CurrentMap.Theme;
                return string.IsNullOrEmpty(theme) ? "temperate" : theme;
            }
            catch (Exception)
            {
                return "temperate";
            }
        }

        /// <summary>
        /// "In action": how far apart a ship and its targets stand, so the hull stays on the water and the targets on the
        /// shore beyond (its bow 14 m short of them), but never past most of its longest reach.
        /// </summary>
        public static float SeaDistance(VehicleDef def, float distance)
        {
            var reach = 0f;
            foreach (var m in def.Mounts)
                if (m.Weapon.Damage > 0f) reach = Math.Max(reach, m.Weapon.Range);
            var clear = def.Length * 0.5f + ShoreGap + 2f;
            return Math.Max(distance, Math.Min(clear, Math.Max(distance, reach * 0.9f)));
        }

        /// <summary>How far in front of the targets the sea's shore runs (the range's targets reach 6 m towards the shooter).</summary>
        public const float ShoreGap = 12f;

        private static bool Has(string id, string token) => id.IndexOf(token, StringComparison.Ordinal) >= 0;
    }
}
