using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 28 H.4, H.11, H.12, H.14: the player's tactic for the next battle. The tactics open with the story (H.11:
    /// by chapter or interlude; the test build opens all); the last one picked is kept per game mode (H.14); with none
    /// picked yet, the first open tactic that suits the commander (H.12), else Balanced. The player's own AI (Auto-buy,
    /// Support, the army) starts with it (<see cref="ModeSession"/>).
    /// </summary>
    public static class TacticPick
    {
        public const string Default = "balanced";

        /// <summary>The highest chapter the story has opened.</summary>
        public static int ChapterReached
        {
            get
            {
                var reached = 1;
                var count = Campaign.ChapterCount;
                for (var c = 2; c <= count; c++)
                    if (Campaign.ChapterOpen(c) || Campaign.ChapterDone(c - 1)) reached = c;
                return reached;
            }
        }

        /// <summary>The interludes reached (each opens once the chapter before it is done).</summary>
        public static int InterludesReached
        {
            get
            {
                var n = 0;
                foreach (var after in CommanderPick.InterludeAfter)
                    if (Campaign.ChapterDone(after)) n++;
                return n;
            }
        }

        public static bool Unlocked(TacticDef t) =>
            t != null && (Progression.TestUnlockAll || AiBehaviour.Unlocked(t, ChapterReached, InterludesReached));

        /// <summary>H.10: per-squad tactics open after chapter 6.</summary>
        public static bool SquadTacticsOpen => Progression.TestUnlockAll || Campaign.ChapterDone(6);

        /// <summary>Every tactic the picker lists, in the sheet's order (merged ones left out, H.3).</summary>
        public static List<TacticDef> Choices(Catalog catalog)
        {
            var list = new List<TacticDef>();
            foreach (var t in catalog.AiData.Tactics)
                if (t.MergedInto == null) list.Add(t);
            return list;
        }

        /// <summary>H.12: the 1-2 tactics that suit a commander (open or not).</summary>
        public static List<TacticDef> Suited(Catalog catalog, CommanderDef commander) =>
            commander != null ? catalog.AiData.SuitedTo(commander.Id) : new List<TacticDef>();

        /// <summary>The tactic the player's side starts a battle of <paramref name="mode"/> with.</summary>
        public static string For(Catalog catalog, GameModeKind mode, CommanderDef commander)
        {
            var data = catalog.AiData;
            var saved = PlayerProfile.LastTactic(mode);
            if (saved != null && data.HasTactic(saved) && Unlocked(data.Tactic(saved))) return data.Tactic(saved).Id;
            foreach (var t in Suited(catalog, commander))
                if (Unlocked(t)) return t.Id;
            return data.HasTactic(Default) ? Default : data.Tactics.Count > 0 ? data.Tactics[0].Id : Default;
        }

        /// <summary>
        /// Prompt 28 appendix B: whether the mode's AI profile lets a side play <paramref name="tactic"/> (the same rule as
        /// <c>AiCommander.AllowedTactic</c>: a profile with no tactics, or "noGeneralTactic", plays Balanced only). The menu
        /// has no world yet, so it reads the profile the battle will use: the mission's goal, else the mode's tag.
        /// </summary>
        public static bool ModeAllows(Catalog catalog, GameModeKind mode, MissionDef mission, string tactic) =>
            ProfileAllows(catalog.AiModes.For(mode.ToString(), mission != null ? mission.Goal.ToString() : null), tactic);

        /// <summary>The same check against a live battle's profile (<c>world.AiProfile</c>).</summary>
        public static bool ProfileAllows(AiModeProfile profile, string tactic)
        {
            if (profile == null) return true;
            if (profile.Tactics.Count == 0 || profile.HasFlag("noGeneralTactic")) return tactic == Default;
            return profile.Allows(tactic);
        }

        /// <summary>Picks a tactic for a mode (kept in the save, H.14).</summary>
        public static void Pick(GameModeKind mode, string tactic) => PlayerProfile.SetLastTactic(mode, tactic);
    }
}
