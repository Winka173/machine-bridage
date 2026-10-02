using System.Collections.Generic;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 28 H.14, H.10, E.1: the player's last tactic per game mode, the per-squad tactics (after chapter 6) and the
    /// targeting mode chosen for each tower type on the Base screen, kept in the save.
    /// </summary>
    public static partial class PlayerProfile
    {
        /// <summary>The last tactic picked for a mode (null: none yet).</summary>
        public static string LastTactic(GameModeKind mode) => Lookup(TacticData.tacticModes, D.tacticIds, mode.ToString());

        public static void SetLastTactic(GameModeKind mode, string tactic)
        {
            Store(TacticData.tacticModes, D.tacticIds, mode.ToString(), tactic);
            Save();
        }

        /// <summary>H.10: a squad's own tactic by the squad's number in the battle (null: the side's).</summary>
        public static string SquadTactic(int squad) => Lookup(TacticData.squadTacticKeys, D.squadTacticIds, squad.ToString());

        public static void SetSquadTactic(int squad, string tactic)
        {
            Store(TacticData.squadTacticKeys, D.squadTacticIds, squad.ToString(), tactic);
            Save();
        }

        /// <summary>E.1: the targeting mode picked for a tower type ("Default" or none: the data's own).</summary>
        public static string TowerModeFor(string towerId) => Lookup(TacticData.towerModeIds, D.towerModes, towerId ?? "");

        public static void SetTowerModeFor(string towerId, string mode)
        {
            if (string.IsNullOrEmpty(towerId)) return;
            Store(TacticData.towerModeIds, D.towerModes, towerId, mode == "Default" ? null : mode);
            Save();
        }

        /// <summary>The save with the prompt 28 lists made (a save from before them has none).</summary>
        private static Data TacticData
        {
            get
            {
                var d = D;
                d.tacticModes ??= new List<string>();
                d.tacticIds ??= new List<string>();
                d.squadTacticKeys ??= new List<string>();
                d.squadTacticIds ??= new List<string>();
                d.towerModeIds ??= new List<string>();
                d.towerModes ??= new List<string>();
                return d;
            }
        }

        private static string Lookup(List<string> keys, List<string> values, string key)
        {
            if (keys == null || values == null) return null;
            var i = keys.IndexOf(key);
            return i >= 0 && i < values.Count && !string.IsNullOrEmpty(values[i]) ? values[i] : null;
        }

        /// <summary>Sets (or with null removes) a key in two parallel lists, the way JsonUtility keeps a map.</summary>
        private static void Store(List<string> keys, List<string> values, string key, string value)
        {
            while (values.Count < keys.Count) values.Add("");
            var i = keys.IndexOf(key);
            if (string.IsNullOrEmpty(value))
            {
                if (i < 0) return;
                keys.RemoveAt(i);
                values.RemoveAt(i);
                return;
            }
            if (i >= 0) values[i] = value;
            else
            {
                keys.Add(key);
                values.Add(value);
            }
        }
    }
}
