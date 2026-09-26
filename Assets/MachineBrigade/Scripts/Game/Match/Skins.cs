using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>How a skin's second and third colours are laid over the base.</summary>
    public enum CamoPattern
    {
        Plain = 0,
        Blotches = 1,
        Stripes = 2,
        Digital = 3,
    }

    /// <summary>One army paint scheme sold for coins. The Lit shader draws the pattern procedurally.</summary>
    public readonly struct Skin
    {
        public Skin(string id, int price, string baseHex, string secondHex, string thirdHex, CamoPattern pattern, float scale = 0.35f,
            float metallic = 0.25f, float roughness = 0.42f)
        {
            Id = id;
            Price = price;
            Base = Hex(baseHex);
            Second = Hex(secondHex);
            Third = Hex(thirdHex);
            Pattern = pattern;
            Scale = scale;
            Metallic = metallic;
            Roughness = roughness;
        }

        public string Id { get; }
        public int Price { get; }
        public Color Base { get; }
        public Color Second { get; }
        public Color Third { get; }
        public CamoPattern Pattern { get; }
        public float Scale { get; }
        public float Metallic { get; }
        public float Roughness { get; }

        private static Color Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.magenta;
    }

    /// <summary>
    /// Army skins for the player's side. None is red: the enemy is painted rust red, and the
    /// battlefield must stay readable.
    /// </summary>
    public static class Skins
    {
        public const string Default = "olive";

        public static readonly Skin[] All =
        {
            new("olive", 0, "#7a9654", "#7a9654", "#7a9654", CamoPattern.Plain),
            new("desert", 500, "#c7a46a", "#9a7646", "#6f5535", CamoPattern.Blotches, 0.32f),
            new("woodland", 800, "#617540", "#3c4a29", "#6d5436", CamoPattern.Blotches, 0.36f),
            new("arctic", 900, "#e4e9ec", "#b4bec5", "#7b8790", CamoPattern.Blotches, 0.34f),
            new("urban", 1200, "#8b9197", "#5a6066", "#b9bdc1", CamoPattern.Digital, 0.55f),
            new("ocean", 1500, "#4b6b8c", "#2c435e", "#8aa7c4", CamoPattern.Digital, 0.55f),
            new("tiger", 2500, "#d9832c", "#1e1b18", "#d9832c", CamoPattern.Stripes, 0.5f),
            new("midnight", 3000, "#272b31", "#3b4550", "#4fd7ff", CamoPattern.Digital, 0.6f, 0.35f, 0.35f),
            new("steel", 4500, "#b3bcc3", "#8c969e", "#d7dde2", CamoPattern.Plain, 0.35f, 0.9f, 0.24f),
            new("gold", 6000, "#d5a63c", "#b8872a", "#f0cd6c", CamoPattern.Plain, 0.35f, 0.92f, 0.26f),
        };

        public static bool Exists(string id)
        {
            foreach (var s in All)
                if (s.Id == id) return true;
            return false;
        }

        public static Skin Get(string id)
        {
            foreach (var s in All)
                if (s.Id == id) return s;
            return All[0];
        }
    }
}
