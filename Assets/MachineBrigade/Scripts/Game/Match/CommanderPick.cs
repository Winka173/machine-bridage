using System;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 22 F.1: the player's commander. The one picked is saved with the settings ("mb.commander"); a save made
    /// before commanders, or one naming a commander that is unknown or not open, starts with Colonel Kade. Commanders
    /// open with the story: each names the chapter id the story places it in (<see cref="CommanderDef.Unlock"/>). A
    /// story mission may set its own (chapter 10's duel is Hawk's); the Sandbox sets each side's in its scenario.
    /// </summary>
    public static class CommanderPick
    {
        public const string PrefKey = "mb.commander";

        /// <summary>The main chapter each interlude follows (prompt 22 B.2: I after 3, II after 6, III after 9).</summary>
        internal static readonly int[] InterludeAfter = { 3, 6, 9 };

        private static string _chosen;

        /// <summary>The commander picked for the next battles (always an open one: see <see cref="Resolve"/>).</summary>
        public static string Chosen
        {
            get
            {
                if (_chosen == null) Load();
                return Resolve(_chosen);
            }
            set => _chosen = value;
        }

        public static CommanderDef ChosenDef => Commanders.Get(Chosen) ?? Commanders.Get(Commanders.Default);

        public static void Load()
        {
            try
            {
                _chosen = PlayerPrefs.GetString(PrefKey, "");
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[CommanderPick] Could not read the commander: {e.Message}");
                _chosen = "";
            }
        }

        /// <summary>Picks a commander and saves the pick (a locked one is refused: false).</summary>
        public static bool Pick(string id)
        {
            if (Commanders.Get(id) is not { IsGeneral: false } c || !Unlocked(c)) return false;
            _chosen = c.Id;
            if (MatchSettings.SaveSuspended) return true;
            try
            {
                PlayerPrefs.SetString(PrefKey, c.Id);
                PlayerPrefs.Save();
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[CommanderPick] Could not save the commander: {e.Message}");
            }
            return true;
        }

        /// <summary>A saved id as the pick: an unknown id, a general's, a locked one or none (an old save) is Colonel Kade.</summary>
        public static string Resolve(string saved) =>
            Commanders.Get(saved) is { IsGeneral: false } c && Unlocked(c) ? c.Id : Commanders.Default;

        /// <summary>The commander is open: the test build opens all; otherwise the story has reached its chapter.</summary>
        public static bool Unlocked(CommanderDef c) => c != null && !c.IsGeneral && (Progression.TestUnlockAll || c.Id == Commanders.Default || Reached(c.Unlock));

        /// <summary>
        /// A chapter id reached: "c4" once chapter 4 opens, "c5+" once chapter 5 is done, "i2" once the chapter before
        /// the second interlude is done.
        /// </summary>
        public static bool Reached(string unlock)
        {
            if (string.IsNullOrEmpty(unlock)) return true;
            if (unlock[0] == 'i' && int.TryParse(unlock.Substring(1), out var interlude))
                return interlude >= 1 && interlude <= InterludeAfter.Length && Campaign.ChapterDone(InterludeAfter[interlude - 1]);
            if (unlock[0] != 'c') return false;
            var done = unlock.EndsWith("+", StringComparison.Ordinal);
            if (!int.TryParse(unlock.Substring(1).TrimEnd('+'), out var chapter)) return false;
            if (done) return Campaign.ChapterDone(chapter);
            return chapter <= 1 || Campaign.ChapterOpen(chapter) || Campaign.ChapterDone(chapter - 1);
        }

        /// <summary>The mission sets its own commander (the player cannot change it).</summary>
        public static bool Forced(MissionDef mission) => mission?.Commander != null && Commanders.Get(mission.Commander) is { IsGeneral: false };

        /// <summary>The player's commander in a battle: the mission's own, else the one picked.</summary>
        public static CommanderDef ForBattle(MissionDef mission) =>
            Forced(mission) ? Commanders.Get(mission.Commander) : ChosenDef;

        /// <summary>The enemy's: the passive of the general the mission is tied to (none for an untied mission or another mode).</summary>
        public static CommanderDef EnemyFor(MissionDef mission) => mission == null ? null : Commanders.General(mission.General);

        /// <summary>
        /// The commanders a Sandbox side may take (F.1): none, the player's open commanders (all of them in the internal
        /// build), and every enemy general.
        /// </summary>
        public static System.Collections.Generic.List<CommanderDef> SandboxChoices(bool everything)
        {
            var list = new System.Collections.Generic.List<CommanderDef> { null };
            foreach (var c in Commanders.All)
                if (everything || Unlocked(c)) list.Add(c);
            list.AddRange(Commanders.Generals);
            return list;
        }
    }
}
