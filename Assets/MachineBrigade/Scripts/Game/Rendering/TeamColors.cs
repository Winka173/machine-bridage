using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Army colours. The Team material multiplies these by the models' baked grey lighting, so
    /// they are authored a little brighter than they read on screen.
    /// </summary>
    public static class TeamColors
    {
        public static Color32 Main(int team) => team switch
        {
            0 => new Color32(122, 150, 84, 255),  // olive
            1 => new Color32(190, 86, 62, 255),   // rust red
            _ => new Color32(150, 150, 140, 255),
        };

        /// <summary>Bright tint for health bars, markers and the HUD.</summary>
        public static Color Ui(int team) => team == 0 ? new Color(0.55f, 0.95f, 0.62f) : new Color(1f, 0.42f, 0.34f);
    }
}
