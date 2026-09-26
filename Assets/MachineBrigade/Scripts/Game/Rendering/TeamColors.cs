using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>Army colours: olive for the player, brick red for the enemy, grey for anyone else.</summary>
    public static class TeamColors
    {
        public static Color32 Main(int team) => team switch
        {
            0 => new Color32(98, 114, 60, 255),
            1 => new Color32(152, 60, 46, 255),
            _ => new Color32(120, 120, 110, 255),
        };

        public static Color32 Dark(int team) => team switch
        {
            0 => new Color32(64, 76, 40, 255),
            1 => new Color32(98, 38, 30, 255),
            _ => new Color32(80, 80, 72, 255),
        };

        /// <summary>Bright tint for health bars and markers.</summary>
        public static Color Ui(int team) => team == 0 ? new Color(0.45f, 0.95f, 0.45f) : new Color(1f, 0.35f, 0.3f);
    }
}
