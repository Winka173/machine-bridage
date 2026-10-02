using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 32 L3: the player's wall lines (outer, inner, and a fortress's keep line in Defend), chosen free on the Base
    /// screen like the HQ type; every base the player takes into battle carries them. No currency of their own.
    /// </summary>
    public static partial class PlayerProfile
    {
        /// <summary>Lines a loadout carries: a camp reads the first two, a fortress all three.</summary>
        public const int WallLines = 3;

        /// <summary>A line's type in the save (the data's default when none is set).</summary>
        public static WallType WallOf(int line)
        {
            var list = D.wallTypes;
            if (line >= 0 && list != null && line < list.Count && WallRules.TryParse(list[line], out var t)) return t;
            return GameContent.LoadCatalog().Base.Walls.Default;
        }

        /// <summary>Every line's type, outer first.</summary>
        public static List<WallType> WallTypes()
        {
            var list = new List<WallType>(WallLines);
            for (var i = 0; i < WallLines; i++) list.Add(WallOf(i));
            return list;
        }

        /// <summary>The next type of a line on the Base screen: none, HESCO, T-wall, gun wall, round again (free).</summary>
        public static void NextWallType(int line)
        {
            if (line < 0 || line >= WallLines) return;
            D.wallTypes ??= new List<string>();
            while (D.wallTypes.Count < WallLines) D.wallTypes.Add(WallRules.Key(WallOf(D.wallTypes.Count)));
            D.wallTypes[line] = WallRules.Key(WallRules.Next(WallOf(line)));
            Save();
        }
    }
}
