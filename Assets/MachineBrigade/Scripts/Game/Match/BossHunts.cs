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
        /// The week's clock. Prompt 26 E.2: the targets come to about 18 minutes (7 minis at 66 s, 3 mains at 2.8 min, nine 15 s
        /// rests); 30 minutes leaves room for a weaker deck (50 before, for the old, longer hunt).
        /// </summary>
        public static float WeeklyMinutes => global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossHunts.WeeklyMinutes;

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
                            // Prompt 29 C11: a boss of the main rank counts as a main boss in the hunts even where its chapter
                            // lists it in a mini slot (Gungnir, chapter 11: 17 mains and 24 minis to draw 3 and 7 from).
                            list.Add(new HuntBoss(id, id == chapter.Main || def.Rank == BossRank.Main, chapter.Number, AirDefence(def)));
                    }
                    foreach (var m in Campaign.MissionsOf(chapter.Number))
                        foreach (var b in Campaign.BossesOf(m))
                            Add(b.Def);
                    foreach (var id in slots) Add(id);
                    // Prompt 22 E: a new mini boss no chapter lists yet comes after the chapter its interlude follows.
                    foreach (var (id, after) in Unslotted)
                        if (after == chapter.Number && !seen.Contains(id) && !Listed(id) && catalog.Vehicles.TryGetValue(id, out var def) && def.Boss &&
                            seen.Add(id))
                            list.Add(new HuntBoss(id, def.Rank == BossRank.Main, chapter.Number));
                }
                return list;
            }
        }

        /// <summary>
        /// Prompt 22 E (DECISIONS 22E): the new mini bosses and the chapter whose interlude they fight in (Behemoth Mk.0 in
        /// interlude I after chapter 3, Morrigan in interlude III after chapter 9), for the hunts until the campaign lists
        /// them in a chapter's slots; once it does, the slot wins and this is not used.
        /// </summary>
        public static readonly (string id, int after)[] Unslotted =
        {
            ("behemoth_mk0", 3), ("morrigan", 9),
            // Prompt 25 F2 batch D (DECISIONS 25F2-D): the eight new bosses, by the chapter their general or season belongs to.
            ("nyx", 4), ("stymphalos", 5), ("cerberus", 6), ("monster", 8), ("kraken", 9), ("hydra", 9), ("garuda", 10), ("hyperion", 12),
        };

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

        /// <summary>
        /// Prompt 29 C11 (checked in the G1 pass): the bosses the hunts count as main, the draw's own flag (a chapter's main, or
        /// a boss of the main rank in a mini slot: Gungnir), so the rules line and the roster's marks agree with the draw (17 mains).
        /// </summary>
        public static HashSet<string> MainIds()
        {
            var set = new HashSet<string>();
            foreach (var b in Story)
                if (b.Main) set.Add(b.Id);
            return set;
        }

        /// <summary>How many of a run's bosses are main bosses (as the draw counts them, see <see cref="MainIds"/>).</summary>
        public static int MainsIn(IReadOnlyList<string> run)
        {
            var mains = MainIds();
            var n = 0;
            foreach (var id in run)
                if (mains.Contains(id)) n++;
            return n;
        }
    }
}
