namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 22 F: the commanders' and generals' names and call signs as name tokens (<c>{@kade}</c>, <c>{@tide}</c>),
    /// the same in both languages, in one place. The story's own tokens (A.3, A.4) keep theirs; where the story names a
    /// character too, its entry in <see cref="Table"/> is the one kept (these are only added when missing).
    /// </summary>
    public static partial class NameText
    {
        private static readonly (string key, string name)[] CommanderNames =
        {
            // People (prompt 22 F.2, F.3).
            ("name.kade", "Marcus Kade"), ("name.lind", "Mara Lind"), ("name.reyes", "Jonah Reyes"), ("name.kerr", "Nadia Kerr"),
            ("name.venn", "Elara Venn"), ("name.mendez", "Kaia Mendez"), ("name.brandt", "Brandt"), ("name.dahl", "Piet Dahl"),
            ("name.brenn", "Otto Brenn"), ("name.adler", "Tomas Adler"), ("name.varro", "Ines Varro"), ("name.reyn", "August Reyn"),
            ("name.quist", "Lena Quist"), ("name.okoye", "Selma Okoye"), ("name.thorne", "Roland Thorne"), ("name.wolff", "Kasimir Wolff"),
            // Call signs.
            ("name.iron", "Iron"), ("name.hawk", "Hawk"), ("name.rush", "Rush"), ("name.bulwark", "Bulwark"), ("name.longshot", "Longshot"),
            ("name.ledger", "Ledger"), ("name.flag", "Flag"), ("name.tide", "Tide"), ("name.crown", "Crown"), ("name.magpie", "Magpie"),
            ("name.vault", "Vault"), ("name.anvil", "Anvil"), ("name.winter", "Winter"), ("name.maelstrom", "Maelstrom"), ("name.queen", "Queen"),
            ("name.raven", "Raven"), ("name.titan", "Titan"), ("name.sol", "Sol"),
        };

        static NameText()
        {
            foreach (var (key, name) in CommanderNames)
                if (!Table.ContainsKey(key)) Table[key] = (name, name);
        }
    }
}
