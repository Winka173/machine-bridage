using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Which detail level a vehicle is drawn at, chosen by its size on screen: the full model
    /// (level 0), the simplified one-material model (level 1, <see cref="ModelLibrary.Lod"/>) and
    /// a camera-facing impostor from a pre-rendered atlas (level 2, <see cref="ImpostorAtlas"/>).
    /// The camera is orthographic, so a vehicle's size on screen depends only on the zoom and on
    /// the vehicle, not on how far it stands from the middle of the view; a band either side of
    /// each threshold keeps a vehicle from flickering between levels while the view zooms.
    /// Debug flags: -mb-no-lod (full detail only, nothing built), -mb-lod=0|1|2 (force a level
    /// where the vehicle has it), -mb-lod-colours (tint each level).
    /// </summary>
    public static class VehicleLod
    {
        public const int Full = 0;
        public const int Simple = 1;
        public const int Impostor = 2;

        /// <summary>Below this many pixels across, a vehicle is drawn at level 1.</summary>
        public const float DetailPixels = 128f;

        /// <summary>Below this many pixels across, a vehicle is drawn as an impostor.</summary>
        public const float ImpostorPixels = 24f;

        /// <summary>How far past a threshold (as a share of it) a vehicle must shrink or grow to change level.</summary>
        public const float Band = 0.12f;

        private static int _forced = int.MinValue;

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            _forced = int.MinValue;
            PixelsPerMetre = 0f;
        }

        /// <summary>Detail levels are built and used (not -mb-no-lod).</summary>
        public static bool Enabled => !Match.DebugFlags.Has("-mb-no-lod");

        /// <summary>-mb-lod-colours: level 1 drawn tinted cyan, impostors magenta.</summary>
        public static bool Colours => Match.DebugFlags.Has("-mb-lod-colours");

        /// <summary>The level -mb-lod=N forces, or -1.</summary>
        public static int Forced
        {
            get
            {
                if (_forced == int.MinValue)
                    _forced = int.TryParse(Match.DebugFlags.Value("-mb-lod="), out var level) ? Mathf.Clamp(level, Full, Impostor) : -1;
                return _forced;
            }
            set => _forced = value;
        }

        /// <summary>This frame's screen pixels per metre (set by the views each frame; 0 before the first).</summary>
        public static float PixelsPerMetre { get; set; }

        /// <summary>
        /// Pixels per metre on screen: rendered pixels (the resolution scale included) over the
        /// view's height. For a perspective camera, at the given distance.
        /// </summary>
        public static float PixelsPerMetreOf(Camera camera, float distance = 50f)
        {
            if (camera == null) return 0f;
            var height = camera.orthographic
                ? camera.orthographicSize * 2f
                : 2f * distance * Mathf.Tan(camera.fieldOfView * 0.5f * Mathf.Deg2Rad);
            return height > 0f ? camera.pixelHeight * RenderScale / height : 0f;
        }

        /// <summary>The pipeline's resolution scale (the graphics options' resolution).</summary>
        public static float RenderScale => GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp ? urp.renderScale : 1f;

        /// <summary>
        /// The level for a vehicle <paramref name="pixels"/> across that is now at <paramref name="current"/>:
        /// it drops a level once it is <see cref="Band"/> below a threshold and comes back once it
        /// is that far above, so a size at a threshold keeps whatever level it had.
        /// <paramref name="deepest"/> is the lowest level it has (1 without an impostor yet).
        /// </summary>
        public static int Choose(int current, float pixels, int deepest = Impostor)
        {
            var down = pixels < ImpostorPixels * (1f - Band) ? Impostor : pixels < DetailPixels * (1f - Band) ? Simple : Full;
            var up = pixels > DetailPixels * (1f + Band) ? Full : pixels > ImpostorPixels * (1f + Band) ? Simple : Impostor;
            // A vehicle without a level yet takes the one its size falls in.
            var level = current < Full || current > Impostor ? (pixels < ImpostorPixels ? Impostor : pixels < DetailPixels ? Simple : Full)
                : down > current ? down
                : up < current ? up
                : current;
            return Mathf.Clamp(level, Full, Mathf.Max(Full, deepest));
        }

        /// <summary>The -mb-lod-colours tint of a level.</summary>
        public static Color Tint(int level) => level switch
        {
            Simple => new Color(0.45f, 1f, 1f),
            Impostor => new Color(1f, 0.4f, 1f),
            _ => Color.white,
        };
    }
}
