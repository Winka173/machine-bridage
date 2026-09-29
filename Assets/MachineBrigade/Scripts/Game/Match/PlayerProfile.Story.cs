namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 22 D: the story's state in the save. The choices made (D.5), kept as "choice=option" so an old save
    /// simply has none; the comic panels seen after each chapter (D.8), as marks among the chapter cards seen.
    /// Nothing here takes a card or a unit away (D.9): the story only ever adds.
    /// </summary>
    public static partial class PlayerProfile
    {
        /// <summary>The option chosen for a story choice ("sea"), or null while it is still to be made.</summary>
        public static string StoryChoice(string choice)
        {
            if (string.IsNullOrEmpty(choice)) return null;
            var prefix = choice + "=";
            foreach (var entry in D.storyChoices)
                if (entry.StartsWith(prefix, System.StringComparison.Ordinal)) return entry.Substring(prefix.Length);
            return null;
        }

        /// <summary>Makes a story choice, once: a choice already made stays as it was (false).</summary>
        public static bool ChooseStory(string choice, string option)
        {
            if (string.IsNullOrEmpty(choice) || string.IsNullOrEmpty(option) || StoryChoice(choice) != null) return false;
            D.storyChoices.Add(choice + "=" + option);
            Save();
            return true;
        }

        /// <summary>Every choice made, in the order it was made.</summary>
        public static System.Collections.Generic.IReadOnlyList<string> StoryChoices => D.storyChoices;

        /// <summary>The mark of a chapter's (or interlude's) comic panels in the chapter cards seen.</summary>
        public static int ComicSeen(int chapter) => 200 + chapter;
    }
}
