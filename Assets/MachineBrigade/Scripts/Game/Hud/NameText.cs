using System;
using System.Collections.Generic;
using System.Text;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Proper names (prompt 21 J1 and J5, prompt 22 A). Names stay the same in both languages, and none is Vietnamese.
    /// The story's names of prompt 21 are written <c>{@id}</c> in its texts and filled from <see cref="Table"/> when a
    /// text is read; prompt 22 swapped them here (the ids stay: <c>{@lyhan}</c> is Thorne now). The other names
    /// (bosses, generals, places, chapters, brands, the real weapons the units are modelled on, abbreviations) are
    /// written in the texts as they are; <see cref="Kept"/> lists them for the language scans, which allow them in
    /// both languages.
    /// </summary>
    public static class NameText
    {
        /// <summary>The story's names written as tokens; a text writes <c>{@dieuhau}</c> for <c>name.dieuhau</c>.</summary>
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            ["name.dieuhau"] = ("Hawk", "Hawk"),
            ["name.lephong"] = ("Jonah Reyes", "Jonah Reyes"),
            ["name.lyhan"] = ("Thorne", "Thorne"),
            ["name.trankhai"] = ("Marcus Kade", "Marcus Kade"),
            ["name.khai"] = ("Kade", "Kade"),
            ["name.linh"] = ("Nadia", "Nadia"),
            ["name.mai"] = ("Mara", "Mara"),
            ["name.quaden"] = ("Raven", "Raven"),
            ["name.lamthanh"] = ("Veyra", "Veyra"),
            ["name.bagia"] = ("Matilda", "Matilda"),
        };

        /// <summary>
        /// Names and abbreviations written as they are in both languages (the scans' exception list, prompt 21 L):
        /// units and abbreviations, the Vietnamese abbreviations of the short names, the real weapons and vehicles,
        /// the bosses' and branches' code names, the equipment brands, the story's people, call signs and factions,
        /// and the few words Vietnamese took in whole.
        /// </summary>
        public static readonly string[] Kept =
        {
            // Units and abbreviations.
            "CP", "HQ", "HP", "HUD", "UAV", "FPV", "SAM", "EMP", "SEAD", "MOAB", "APS", "ATGM", "IFV", "MLRS", "GMLRS", "EW", "CIWS", "FPS", "XP", "DPS",
            "mm", "cm", "km", "kg", "MW", "Mk", "Lv",
            // Vietnamese abbreviations in short names: phòng không, trực thăng, sát thương, tên lửa, sở chỉ huy, công trình, tinh nhuệ, tiêm kích.
            "PK", "TT", "ST", "TL", "SCH", "CT", "TN", "TK",
            // Real weapons and vehicles the units are modelled on.
            "AC-130", "Ka-52", "Kh", "Grad", "Smerch", "TOS", "Iskander", "Patriot", "PAC-3", "Tunguska", "ZU", "BMPT", "Terminator", "Ataka", "BTR", "Object",
            "Bradley", "TOW", "Centauro", "Sprut", "PzH", "Merkava", "Trophy", "Kornet", "Iron", "Dome", "Cobra", "Lancet", "Shahed", "Hellfire", "Stinger", "Apache",
            "Little Bird", "Reaper", "Maverick", "Alligator", "Vikhr", "Igla", "JASSM", "GBU", "Wolf", "Griffin", "Centurion", "C-RAM", "Pantsir", "Tor", "Buk",
            // Bosses' and branches' code names.
            "Argus", "Atlas", "Bastion", "Behemoth", "Caspian", "Charybdis", "Daedalus", "Fenrir", "Gungnir", "Harpy", "Hive", "Icarus", "Inferno", "Ixion",
            "Juggernaut", "Jötunn", "Kronos", "Leviathan", "Locust", "Matriarch", "Moloch", "Nemesis", "Roc", "Scylla", "Spectre", "Tartarus", "Tempest",
            "Typhon", "Titan", "Napalm", "Morrigan",
            // Equipment brands.
            "Ironclad", "Works", "Kestrel Dynamics", "Vulcan Arms", "Longbow Ordnance", "Aegis Systems", "Stormfront Aviation", "Hivemind Robotics",
            "Quartermaster", "Logistics", "Spectre Electronics", "Hammerfall Munitions", "Phoenix Recovery", "Wolfpack Tactics", "Bulwark Engineering",
            // The story's people, call signs and factions.
            "Anvil", "Winter", "Maelstrom", "Sol", "Queen", "Varga", "Viktor", "Kessler", "Magnus", "Orlov", "Ilya", "Aurel", "Lucien", "Brandt", "Wolff", "Kasimir", "Elara", "Hawk", "Raven",
            "Hegemon",
            // Prompt 22 A: the story's people and call signs, its factions and places, its chapters and acts, the new maps.
            "Marcus Kade", "Mara Lind", "Jonah Reyes", "Nadia Kerr", "Roland Thorne", "Venn", "Bulwark",
            "Otto Brenn", "Ledger", "Tomas Adler", "Flag", "Kaia Mendez", "Rush", "Piet Dahl", "Longshot", "Ines Varro", "Tide",
            "Lena Quist", "Magpie", "August Reyn", "Crown", "Selma Okoye", "Vault", "Matilda",
            "Meridian Coast", "Meridian Accord", "Meridian", "Accord", "7th Mechanized Brigade", "Project Icarus", "Veyra", "Veyra Old Quarter", "Foundry",
            "Ashfield", "Dunebreak", "Frostpeak", "Ironport", "Red Rock", "Whiteout Pass", "Greenvale", "Rust Yard", "Emberridge", "Jungle Pass",
            "Skyhold", "Metro City", "Stormbeach", "Hollow Dam", "Helion Launch Complex", "Helion", "Salt Flats", "Border Crossing", "Mirewood",
            "Coral Keys", "Beacon Bay", "Deepcut Mine", "Skygate Array", "Skygate",
            "Landfall", "Counteroffensive", "Betrayal", "Silver Sky", "Coast of Fire", "Black Gold", "The Long Winter", "Blueprints", "Iron Harbor",
            "Burning Canopy", "Counterstrike", "The Queen's Choice", "Underworld", "Rough Water", "Hawk and Raven", "War in the Sky",
            // The game.
            "Machine Brigade",
            // Words Vietnamese took in whole.
            "radar", "drone", "boss", "vonfram", "pin", "mini",
        };

        /// <summary>Fills the <c>{@id}</c> names of a text in the current language (<c>{@id}</c> is <c>name.id</c>; <c>{@map.id}</c> any key).</summary>
        public static string Expand(string text)
        {
            if (string.IsNullOrEmpty(text) || text.IndexOf("{@", StringComparison.Ordinal) < 0) return text;
            var sb = new StringBuilder(text.Length + 16);
            var i = 0;
            while (i < text.Length)
            {
                var open = text.IndexOf("{@", i, StringComparison.Ordinal);
                var close = open < 0 ? -1 : text.IndexOf('}', open);
                if (open < 0 || close < 0)
                {
                    sb.Append(text, i, text.Length - i);
                    break;
                }
                sb.Append(text, i, open - i);
                var id = text.Substring(open + 2, close - open - 2);
                var key = id.IndexOf('.') >= 0 ? id : "name." + id;
                if (Table.TryGetValue(key, out var name)) sb.Append(Strings.Vietnamese ? name.vi : name.en);
                else if (Strings.Has(key)) sb.Append(Strings.Get(key));
                else sb.Append(text, open, close - open + 1);
                i = close + 1;
            }
            return sb.ToString();
        }
    }
}
