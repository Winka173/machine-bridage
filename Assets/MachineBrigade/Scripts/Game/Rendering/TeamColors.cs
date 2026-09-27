using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Army colours. The Team material multiplies these by the models' baked grey lighting, so
    /// they are authored a little brighter than they read on screen.
    /// </summary>
    public static class TeamColors
    {
        /// <summary>0: olive against rust red; 1: blue against orange (colour-blind safe).</summary>
        public static int Palette { get; set; }

        public static Color32 Main(int team) => Palette == 1 ? team switch
        {
            0 => new Color32(70, 120, 190, 255),  // steel blue
            1 => new Color32(222, 128, 36, 255),  // orange
            _ => new Color32(150, 150, 140, 255),
        } : team switch
        {
            0 => new Color32(122, 150, 84, 255),  // olive
            1 => new Color32(190, 86, 62, 255),   // rust red
            _ => new Color32(150, 150, 140, 255),
        };

        /// <summary>Bright tint for health bars, markers and the HUD.</summary>
        public static Color Ui(int team) => Palette == 1
            ? team == 0 ? new Color(0.45f, 0.72f, 1f) : new Color(1f, 0.62f, 0.2f)
            : team == 0 ? new Color(0.55f, 0.95f, 0.62f) : new Color(1f, 0.42f, 0.34f);
    }
}
