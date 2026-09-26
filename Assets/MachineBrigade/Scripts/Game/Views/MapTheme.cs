using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>What lies beyond the battlefield's north edge.</summary>
    public enum ThemeWater
    {
        River,
        FrozenRiver,
        Sea,
        None,
    }

    /// <summary>
    /// The look of one kind of battlefield: ground palette and speckle, which trees grow on the
    /// map and round it, the ground clutter, the mountain colours, the water beyond the edge and
    /// the scenery houses. Presentation only; maps name their theme ("temperate", "desert",
    /// "snow", "harbor").
    /// </summary>
    public sealed class MapTheme
    {
        public string Id { get; private set; }
        public TerrainTheme Palette { get; private set; }
        public Color SpeckleLight { get; private set; }
        public Color SpeckleDark { get; private set; }

        /// <summary>The earth block under the map and the horizon ground.</summary>
        public Color Skirt { get; private set; }
        public Color Pebble { get; private set; }
        public Color GrassTuft { get; private set; }

        /// <summary>Grass tufts per unit of the temperate density (0 for none).</summary>
        public float Tufts { get; private set; }

        /// <summary>Decorative scatter in open ground on the map (null for none).</summary>
        public string Bush { get; private set; }

        /// <summary>Models the "tree" prop is drawn with.</summary>
        public string[] Trees { get; private set; }

        /// <summary>Chance a "tree" is drawn dead instead (0 for never).</summary>
        public float DeadTrees { get; private set; }

        // Beyond the map --------------------------------------------------------------------
        public string[] LowlandTrees { get; private set; }
        public string[] HighlandTrees { get; private set; }

        /// <summary>Scales how thickly forests grow round the map (1 = temperate woodland).</summary>
        public float Forest { get; private set; }

        public bool Fields { get; private set; }
        public Color[] Crops { get; private set; }
        public string[] Farmhouses { get; private set; }
        public ThemeWater Water { get; private set; }
        public Color WaterColour { get; private set; }
        public float WaterRoughness { get; private set; }
        public string[] Rocks { get; private set; }
        public string[] Crags { get; private set; }

        /// <summary>Mountain palette: low meadow, forested slopes, rock heights, cliffs, peaks.</summary>
        public Color Meadow { get; private set; }
        public Color ForestFloor { get; private set; }
        public Color Rock { get; private set; }
        public Color Cliff { get; private set; }
        public Color Peak { get; private set; }

        /// <summary>Height (0..1 of the palette) where the peak colour starts.</summary>
        public float PeakLine { get; private set; }

        /// <summary>Scales mountain heights (1 = the temperate range).</summary>
        public float Peaks { get; private set; }

        /// <summary>Fog and horizon colour on a clear day.</summary>
        public Color Haze { get; private set; }

        /// <summary>Tint of the ambient light on a clear day.</summary>
        public Color Cast { get; private set; }

        /// <summary>
        /// Colour for the models' Grass material (turf on cliff tops, mounds), or null to keep the
        /// kit's green: sand in the desert, snow in the mountains.
        /// </summary>
        public Color? ModelGrass { get; private set; }

        /// <summary>The battlefield square on the minimap.</summary>
        public Color Minimap => new(Palette.Grass.r * 0.5f, Palette.Grass.g * 0.5f, Palette.Grass.b * 0.5f, 0.9f);

        public static MapTheme For(string id) => id switch
        {
            "desert" => Desert,
            "snow" => Snow,
            "harbor" => Harbor,
            _ => Temperate,
        };

        public static MapTheme Temperate
        {
            get
            {
                var palette = TerrainTheme.Riverlands;
                return new MapTheme
                {
                    Id = "temperate",
                    Palette = palette,
                    SpeckleLight = Rgb(209, 188, 128),
                    SpeckleDark = Rgb(31, 58, 40),
                    Skirt = Hex("#424634"),
                    Pebble = Hex("#626957"),
                    GrassTuft = Hex("#515f40"),
                    Tufts = 1f,
                    Bush = "bush",
                    Trees = new[] { "tree", "tree", "tree_broad", "pine", "pine", "tree_round", "birch" },
                    DeadTrees = 1f / 14f,
                    LowlandTrees = new[] { "tree", "tree", "tree", "tree", "pine", "pine", "pine", "tree_round", "tree_round", "tree_broad", "birch" },
                    HighlandTrees = new[] { "pine", "pine", "pine", "pine", "pine", "pine", "tree", "tree", "tree_dead" },
                    Forest = 1f,
                    Fields = true,
                    Crops = new[] { new Color(0.62f, 0.6f, 0.36f), new Color(0.46f, 0.55f, 0.32f), new Color(0.66f, 0.55f, 0.36f) },
                    Farmhouses = new[] { "house_large", "house_small", "cottage", "barn", "cottage" },
                    Water = ThemeWater.River,
                    WaterColour = Hex("#2f6f78"),
                    WaterRoughness = 0.08f,
                    Rocks = new[] { "rock_a", "rock_b", "rock_c" },
                    Crags = new[] { "cliff_a", "cliff_b", "boulders" },
                    Meadow = palette.Grass * 0.92f,
                    ForestFloor = Color.Lerp(palette.Grass, new Color(0.24f, 0.33f, 0.2f), 0.6f),
                    Rock = Color.Lerp(palette.Stone, palette.Dirt, 0.35f),
                    Cliff = palette.Stone * 0.8f,
                    Peak = new Color(0.9f, 0.93f, 0.95f),
                    PeakLine = 0.8f,
                    Peaks = 1f,
                    Haze = Rendering.Atmosphere.Haze,
                    Cast = Color.white,
                };
            }
        }

        /// <summary>Sun-baked sand and red earth, sandstone ranges, palms and cacti.</summary>
        public static MapTheme Desert
        {
            get
            {
                var palette = new TerrainTheme("#cfae7c", "#b8875a", "#e0c595", "#a88c68", "#9c8a72");
                return new MapTheme
                {
                    Id = "desert",
                    Palette = palette,
                    SpeckleLight = Rgb(242, 222, 176),
                    SpeckleDark = Rgb(122, 82, 48),
                    Skirt = Hex("#8a6a48"),
                    Pebble = Hex("#9a7a58"),
                    GrassTuft = Hex("#a08c5a"),
                    Tufts = 0.3f,
                    Bush = "cactus",
                    Trees = new[] { "palm" },
                    DeadTrees = 0f,
                    LowlandTrees = new[] { "cactus", "cactus", "cactus", "palm", "tree_dead" },
                    HighlandTrees = new[] { "cactus", "tree_dead" },
                    Forest = 0.1f,
                    Fields = false,
                    Crops = new[] { new Color(0.7f, 0.62f, 0.4f) },
                    Farmhouses = new[] { "adobe_house", "adobe_large", "adobe_house", "market_stall" },
                    Water = ThemeWater.None,
                    WaterColour = Hex("#2f6f78"),
                    WaterRoughness = 0.08f,
                    Rocks = new[] { "rock_a", "rock_b", "rock_c" },
                    Crags = new[] { "mesa", "cliff_a", "boulders" },
                    Meadow = palette.Sand * 0.95f,
                    ForestFloor = Hex("#cf9d63"),
                    Rock = Hex("#b87444"),
                    Cliff = Hex("#8f5232"),
                    Peak = Hex("#c98f58"),
                    PeakLine = 0.9f,
                    Peaks = 0.8f,
                    ModelGrass = Hex("#c49c64"),
                    Haze = new Color(0.62f, 0.54f, 0.43f),
                    Cast = new Color(1.08f, 1f, 0.88f),
                };
            }
        }

        /// <summary>Deep snow, dark pine forests, a frozen river and white peaks.</summary>
        public static MapTheme Snow
        {
            get
            {
                var palette = new TerrainTheme("#e4eaee", "#b3bec5", "#f3f6f8", "#a9a49c", "#7d858a");
                return new MapTheme
                {
                    Id = "snow",
                    Palette = palette,
                    SpeckleLight = Rgb(255, 255, 255),
                    SpeckleDark = Rgb(96, 112, 128),
                    Skirt = Hex("#6c7780"),
                    Pebble = Hex("#7d858a"),
                    GrassTuft = Hex("#9aa6a0"),
                    Tufts = 0f,
                    Bush = null,
                    Trees = new[] { "snow_pine", "snow_pine", "snow_pine", "pine" },
                    DeadTrees = 1f / 20f,
                    LowlandTrees = new[] { "snow_pine", "snow_pine", "snow_pine", "snow_pine", "pine", "birch" },
                    HighlandTrees = new[] { "snow_pine", "snow_pine", "snow_pine", "snow_pine", "snow_pine", "tree_dead" },
                    Forest = 1.15f,
                    Fields = false,
                    Crops = new[] { new Color(0.85f, 0.88f, 0.9f) },
                    Farmhouses = new[] { "log_cabin", "log_cabin", "cottage", "barn" },
                    Water = ThemeWater.FrozenRiver,
                    WaterColour = Hex("#b4ccd6"),
                    WaterRoughness = 0.18f,
                    Rocks = new[] { "snow_rock", "snow_rock", "rock_a", "rock_c" },
                    Crags = new[] { "cliff_a", "cliff_b", "snow_rock" },
                    Meadow = palette.Grass,
                    ForestFloor = Hex("#dfe6ea"),
                    Rock = Hex("#9aa2a8"),
                    Cliff = Hex("#6f777d"),
                    Peak = Hex("#f6f9fb"),
                    PeakLine = 0.35f,
                    Peaks = 1.15f,
                    ModelGrass = Hex("#e6ecef"),
                    Haze = new Color(0.63f, 0.7f, 0.76f),
                    Cast = new Color(0.96f, 1f, 1.08f),
                };
            }
        }

        /// <summary>Grey-green coast: the sea beyond the north edge, low hills, industrial sprawl.</summary>
        public static MapTheme Harbor
        {
            get
            {
                var palette = new TerrainTheme("#6f7d63", "#7d766a", "#a39a80", "#6c6a66", "#6a6f70");
                return new MapTheme
                {
                    Id = "harbor",
                    Palette = palette,
                    SpeckleLight = Rgb(196, 190, 170),
                    SpeckleDark = Rgb(40, 48, 44),
                    Skirt = Hex("#454a44"),
                    Pebble = Hex("#686c66"),
                    GrassTuft = Hex("#56634a"),
                    Tufts = 0.6f,
                    Bush = "bush",
                    Trees = new[] { "tree", "tree_round", "birch", "pine" },
                    DeadTrees = 1f / 10f,
                    LowlandTrees = new[] { "tree", "tree", "tree_round", "birch", "pine", "pine" },
                    HighlandTrees = new[] { "pine", "pine", "pine", "tree", "tree_dead" },
                    Forest = 0.6f,
                    Fields = true,
                    Crops = new[] { new Color(0.52f, 0.56f, 0.38f), new Color(0.6f, 0.58f, 0.42f) },
                    Farmhouses = new[] { "warehouse", "factory", "office_block", "warehouse", "container_stack" },
                    Water = ThemeWater.Sea,
                    WaterColour = Hex("#29566a"),
                    WaterRoughness = 0.06f,
                    Rocks = new[] { "rock_a", "rock_b", "rock_c" },
                    Crags = new[] { "cliff_a", "cliff_b", "boulders" },
                    Meadow = palette.Grass * 0.92f,
                    ForestFloor = Color.Lerp(palette.Grass, new Color(0.24f, 0.33f, 0.2f), 0.55f),
                    Rock = Color.Lerp(palette.Stone, palette.Dirt, 0.35f),
                    Cliff = palette.Stone * 0.8f,
                    Peak = new Color(0.88f, 0.9f, 0.92f),
                    PeakLine = 0.86f,
                    Peaks = 0.7f,
                    Haze = new Color(0.37f, 0.46f, 0.5f),
                    Cast = new Color(0.95f, 0.98f, 1.03f),
                };
            }
        }

        private static Color Rgb(int r, int g, int b) => new(r / 255f, g / 255f, b / 255f);

        private static Color Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.magenta;
    }
}
