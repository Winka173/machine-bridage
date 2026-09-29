using System;
using System.Collections.Generic;
using System.Text;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Proper names (prompt 21 J1 and J5). Names stay the same in both languages. The story's Vietnamese names are
    /// written <c>{@id}</c> in every text and filled from <see cref="Table"/> when a text is read, so prompt 22 can
    /// swap each one here, in one place. The other names (bosses, generals, brands, the real weapons the units
    /// are modelled on, abbreviations) are written in the texts as they are; <see cref="Kept"/> lists them for the
    /// language scans, which allow them in both languages.
    /// </summary>
    public static partial class NameText
    {
        /// <summary>The story's Vietnamese names; a text writes <c>{@dieuhau}</c> for <c>name.dieuhau</c>.</summary>
        public static readonly Dictionary<string, (string en, string vi)> Table = new()
        {
            ["name.dieuhau"] = ("Diều Hâu", "Diều Hâu"),
            ["name.lephong"] = ("Lê Phong", "Lê Phong"),
            ["name.lyhan"] = ("Lý Hàn", "Lý Hàn"),
            ["name.trankhai"] = ("Trần Khải", "Trần Khải"),
            ["name.khai"] = ("Khải", "Khải"),
            ["name.linh"] = ("Linh", "Linh"),
            ["name.mai"] = ("Mai", "Mai"),
            ["name.quaden"] = ("Quạ Đen", "Quạ Đen"),
            ["name.lamthanh"] = ("Lam Thành", "Lam Thành"),
            ["name.bagia"] = ("Bà Già", "Bà Già"),
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
            "Typhon", "Titan", "Napalm",
            // Equipment brands.
            "Ironclad", "Works", "Kestrel Dynamics", "Vulcan Arms", "Longbow Ordnance", "Aegis Systems", "Stormfront Aviation", "Hivemind Robotics",
            "Quartermaster", "Logistics", "Spectre Electronics", "Hammerfall Munitions", "Phoenix Recovery", "Wolfpack Tactics", "Bulwark Engineering",
            // The story's people, call signs and factions (the Vietnamese ones are in the table above).
            "Anvil", "Winter", "Maelstrom", "Sol", "Queen", "Varga", "Viktor", "Kessler", "Magnus", "Orlov", "Ilya", "Aurel", "Lucien", "Brandt", "Wolff", "Kasimir", "Elara", "Sen", "Hawk", "Raven",
            "Hegemon",
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
