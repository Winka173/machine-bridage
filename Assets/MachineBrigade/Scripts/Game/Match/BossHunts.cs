using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 20 N (DECISIONS 19N): this build's Boss Hunts, from the chapters switched on. The week's hunt draws 3 main
    /// bosses and 7 mini bosses by the ISO week (<see cref="BossHunt.Weekly"/>); the full hunt is every chapter slot in
    /// story order and opens once the last chapter switched on is done. Both grow by themselves when an act is switched
    /// on or a chapter gains a boss (campaign.json "main" / "minis").
    /// </summary>
    public static class BossHunts
    {
        /// <summary>The week's clock (10 bosses at 2-5 minutes each and nine 20 s rests: a 30-40 minute run).</summary>
        public const float WeeklyMinutes = 45f;

        /// <summary>The first clear of the week pays this (once a week, the Operations ledger).</summary>
        public const int WeeklyReward = 1500;

        /// <summary>The first full clear pays this and a legendary crate.</summary>
        public const int FullReward = 10000;

        /// <summary>The full hunt's supports are drawn from this seed (the same run for everyone).</summary>
        public const int FullSeed = 2020;

        /// <summary>Kinds of run in the save.</summary>
        public const string WeeklyKey = "weekly", FullKey = "full";

        /// <summary>
        /// Every chapter slot of the chapters switched on, in story order: chapter by chapter, each boss where its first
        /// mission or stage fights it (a slot no mission fights, which the builder forbids, comes at its chapter's end).
        /// The trains (Nemesis, Juggernaut) are left out, as the old Boss Rush left them: they run on their mission's rail
        /// line, which no hunt battlefield has (DECISIONS 19N).
        /// </summary>
        public static IReadOnlyList<HuntBoss> Story
        {
            get
            {
                var catalog = GameContent.LoadCatalog();
                var list = new List<HuntBoss>();
                var seen = new HashSet<string>();
                foreach (var chapter in Campaign.Chapters)
                {
                    if (!Campaign.ChapterEnabled(chapter.Number)) continue;
                    var slots = new List<string>(chapter.Minis);
                    if (chapter.Main != null) slots.Add(chapter.Main);
                    void Add(string id)
                    {
                        if (slots.Contains(id) && catalog.Vehicles.TryGetValue(id, out var def) && !OnRails(def) && seen.Add(id))
                            list.Add(new HuntBoss(id, id == chapter.Main, chapter.Number));
                    }
                    foreach (var m in Campaign.MissionsOf(chapter.Number))
                        foreach (var b in Campaign.BossesOf(m))
                            Add(b.Def);
                    foreach (var id in slots) Add(id);
                    // Prompt 22 E: a new mini boss no chapter lists yet comes after the chapter its interlude follows.
                    foreach (var (id, after) in Unslotted)
                        if (after == chapter.Number && !seen.Contains(id) && !Listed(id) && catalog.Vehicles.TryGetValue(id, out var def) && def.Boss &&
                            seen.Add(id))
                            list.Add(new HuntBoss(id, false, chapter.Number));
                }
                return list;
            }
        }

        /// <summary>
        /// Prompt 22 E (DECISIONS 22E): the new mini bosses and the chapter whose interlude they fight in (Behemoth Mk.0 in
        /// interlude I after chapter 3, Morrigan in interlude III after chapter 9), for the hunts until the campaign lists
        /// them in a chapter's slots; once it does, the slot wins and this is not used.
        /// </summary>
        public static readonly (string id, int after)[] Unslotted = { ("behemoth_mk0", 3), ("morrigan", 9) };

        private static bool Listed(string id)
        {
            foreach (var chapter in Campaign.Chapters)
            {
                if (chapter.Main == id) return true;
                foreach (var mini in chapter.Minis)
                    if (mini == id) return true;
            }
            return false;
        }

        /// <summary>A boss that runs on rails (the train frame): only its own mission's line suits it.</summary>
        public static bool OnRails(VehicleDef def) => def.Frame?.Move == BossMove.Rail;

        public static IReadOnlyList<string> Weekly(int week) => BossHunt.Weekly(week, Story);

        public static IReadOnlyList<string> ThisWeek => Weekly(WeeklyFortress.Week);

        public static IReadOnlyList<string> Full => BossHunt.Full(Story);

        /// <summary>The full hunt opens once the operation of the last chapter switched on is won.</summary>
        public static bool FullOpen => Progression.TestUnlockAll || Campaign.ChapterDone(Campaign.LastChapter);

        /// <summary>How many of a run's bosses are main bosses.</summary>
        public static int MainsIn(IReadOnlyList<string> run)
        {
            var catalog = GameContent.LoadCatalog();
            var n = 0;
            foreach (var id in run)
                if (catalog.Vehicles.TryGetValue(id, out var def) && def.Rank == BossRank.Main) n++;
            return n;
        }
    }
}
