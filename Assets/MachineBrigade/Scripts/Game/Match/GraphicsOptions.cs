using UnityEngine;

namespace MachineBrigade.Game.Match
{
    public enum ShadowLevel
    {
        Off,
        Low,
        Medium,
        High,
    }

    /// <summary>
    /// Every graphics option in force. A preset fills them all in; changing any one of them turns
    /// the preset into Custom. Explosions and fire are never reduced by any of these: they
    /// change resolution, edges, shadows, glow, scenery and how many effect lights and scorch
    /// marks are kept at once.
    /// </summary>
    public sealed class GraphicsOptions
    {
        public ShadowLevel Shadows { get; set; } = ShadowLevel.High;

        /// <summary>Render resolution in percent of the screen (70, 85 or 100).</summary>
        public int RenderScale { get; set; } = 100;

        /// <summary>MSAA samples: 1 (off), 2 or 4.</summary>
        public int AntiAliasing { get; set; } = 2;

        /// <summary>Frame rate cap: 30, 60, 90 or 120 (the display's limit applies).</summary>
        public int FrameRate { get; set; } = 60;

        /// <summary>Glow: 0 off, 1 low (quarter resolution, four passes), 2 high (half resolution, six passes).</summary>
        public int Bloom { get; set; } = 2;

        /// <summary>Forests and hills round the map at full density (false: half).</summary>
        public bool RichScenery { get; set; } = true;

        /// <summary>
        /// Maximum effect detail: more effect lights, scorch marks, debris and wrecks kept at once
        /// (false: the thrifty budget). The blasts themselves are the same either way.
        /// </summary>
        public bool MaxEffects { get; set; } = true;

        public static readonly int[] RenderScales = { 70, 85, 100 };
        public static readonly int[] AntiAliasingLevels = { 1, 2, 4 };
        public static readonly int[] FrameRates = { 30, 60, 90, 120 };

        public static GraphicsOptions For(GraphicsQuality tier) => tier switch
        {
            // Effects stay at maximum on every preset: fire and explosions are the game.
            GraphicsQuality.Low => new GraphicsOptions
            {
                Shadows = ShadowLevel.Low, RenderScale = 70, AntiAliasing = 1, FrameRate = 30, Bloom = 1, RichScenery = false,
                MaxEffects = true,
            },
            GraphicsQuality.Medium => new GraphicsOptions
            {
                Shadows = ShadowLevel.Medium, RenderScale = 85, AntiAliasing = 2, FrameRate = 60, Bloom = 1, RichScenery = true,
                MaxEffects = true,
            },
            _ => new GraphicsOptions
            {
                Shadows = ShadowLevel.High, RenderScale = 100, AntiAliasing = Application.isMobilePlatform ? 2 : 4, FrameRate = 60,
                Bloom = 2, RichScenery = true, MaxEffects = true,
            },
        };

        public GraphicsOptions Copy() => (GraphicsOptions)MemberwiseClone();

        public void Save(string prefix)
        {
            PlayerPrefs.SetInt(prefix + "shadows", (int)Shadows);
            PlayerPrefs.SetInt(prefix + "scale", RenderScale);
            PlayerPrefs.SetInt(prefix + "msaa", AntiAliasing);
            PlayerPrefs.SetInt(prefix + "fps", FrameRate);
            PlayerPrefs.SetInt(prefix + "bloom", Bloom);
            PlayerPrefs.SetInt(prefix + "scenery", RichScenery ? 1 : 0);
            PlayerPrefs.SetInt(prefix + "effects", MaxEffects ? 1 : 0);
        }

        public static GraphicsOptions Load(string prefix, GraphicsOptions fallback) => new()
        {
            Shadows = (ShadowLevel)Mathf.Clamp(PlayerPrefs.GetInt(prefix + "shadows", (int)fallback.Shadows), 0, 3),
            RenderScale = Snap(PlayerPrefs.GetInt(prefix + "scale", fallback.RenderScale), RenderScales),
            AntiAliasing = Snap(PlayerPrefs.GetInt(prefix + "msaa", fallback.AntiAliasing), AntiAliasingLevels),
            FrameRate = Snap(PlayerPrefs.GetInt(prefix + "fps", fallback.FrameRate), FrameRates),
            Bloom = Mathf.Clamp(PlayerPrefs.GetInt(prefix + "bloom", fallback.Bloom), 0, 2),
            RichScenery = PlayerPrefs.GetInt(prefix + "scenery", fallback.RichScenery ? 1 : 0) == 1,
            MaxEffects = PlayerPrefs.GetInt(prefix + "effects", fallback.MaxEffects ? 1 : 0) == 1,
        };

        /// <summary>The allowed value closest to <paramref name="value"/>.</summary>
        public static int Snap(int value, int[] allowed)
        {
            var best = allowed[0];
            foreach (var a in allowed)
                if (Mathf.Abs(a - value) < Mathf.Abs(best - value)) best = a;
            return best;
        }
    }
}
