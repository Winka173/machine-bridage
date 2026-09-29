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
        /// <summary>
        /// The week's clock (10 bosses at 2-5 minutes each and nine 20 s rests: a 30-40 minute run). Play-test 6 (DECISIONS
        /// 21G): 45 -> 50 minutes for the tougher bosses (a geared army's Normal run takes about 40).
        /// </summary>
        public const float WeeklyMinutes = 50f;

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
        /// The trains (Nemesis, Juggernaut) are in since play-test 6 (DECISIONS 21G): the hunt switches to their line's
        /// battlefield (Metro City, Ironport: their data's "arena" and "route") as it does for the sea and the launch site.
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
                        if (slots.Contains(id) && catalog.Vehicles.TryGetValue(id, out var def) && (!OnRails(def) || def.Arena != null) && seen.Add(id))
                            list.Add(new HuntBoss(id, id == chapter.Main, chapter.Number, AirDefence(def)));
                    }
                    foreach (var m in Campaign.MissionsOf(chapter.Number))
                        foreach (var b in Campaign.BossesOf(m))
                            Add(b.Def);
                    foreach (var id in slots) Add(id);
                }
                return list;
            }
        }

        /// <summary>A boss that runs on rails (the train frame): only a battlefield with its line suits it.</summary>
        public static bool OnRails(VehicleDef def) => def.Frame?.Move == BossMove.Rail;

        /// <summary>
        /// Play-test 6 (DECISIONS 21G): a boss that answers aircraft itself: two or more mounts made for them (flak, SAMs,
        /// air-burst guns). A boss that flies but has none (the gunships) does not: fighters own it. The week's draw brings
        /// some of these every week.
        /// </summary>
        public static bool AirDefence(VehicleDef def)
        {
            var n = 0;
            foreach (var m in def.Mounts)
                if (m.Weapon.DamageType == DamageType.Fragmentation || m.Weapon.Targets == TargetLayers.Air) n++;
            return n >= 2;
        }

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
