using System;
using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The player's progress, saved on the device: coins, rank (XP), cards unlocked, items bought
    /// (skins and premium units), the equipped skin and the stars won on each campaign mission.
    /// </summary>
    public static partial class PlayerProfile
    {
        [Serializable]
        private sealed class Data
        {
            public int version = 1;
            public int coins;
            public int xp;
            public int level = 1;
            public List<string> unlocked = new();
            public List<string> owned = new();
            public string skin = Skins.Default;
            public List<string> missionIds = new();
            public List<int> missionStars = new();

            /// <summary>Best tier won per mission (0 normal, 1 heroic, 2 iron), alongside missionIds.</summary>
            public List<int> missionTiers = new();

            /// <summary>The weekly fortress: the week it is for, the stage reached, whether its reward was paid.</summary>
            public int weeklyId;
            public int weeklyStage = 1;
            public bool weeklyClaimed;

            /// <summary>The week's rewards paid ("fortress", "operation"): one ledger for every weekly reward.</summary>
            public List<string> weeklyClaims = new();

            /// <summary>The Operations mode's records: battle, tier, best score, fastest win (seconds).</summary>
            public List<string> opsIds = new();
            public List<int> opsTiers = new();
            public List<int> opsScores = new();
            public List<float> opsTimes = new();
            public List<string> itemIds = new();
            public int dailyDay;
            public List<int> dailyProgress = new();
            public List<bool> dailyClaimed = new();
            public List<int> itemCounts = new();

            // The arsenal (see PlayerProfile.Arsenal.cs): card ranks and blueprints,
            // equipment and loadouts, crates, pity counters and the daily crate counters.
            public int gems; // old saves only: turned into coins on load
            public List<string> rankIds = new();
            public List<int> ranks = new();
            public List<int> prints = new();
            public int universal;
            public List<GearItem> gear = new();
            public int nextGearId = 1;

            /// <summary>2: equipment in the affix model (base types, sub-stats, traits; Optics in slot 3). Older saves are brought up to date on load.</summary>
            public int gearVersion;
            public List<int> loadout = new();
            public List<int> crates = new();
            public List<int> sinceEpic = new();
            public List<int> sinceLegendary = new();
            public int winCrateDay;
            public int winCrates;

            /// <summary>Prompt 30 L5: the endless parts' coins paid today (all modes, capped), and the badges earned.</summary>
            public int endlessDay;
            public int endlessPaid;
            public List<string> endlessBadges = new();
            public int adDay;
            public int ads;
            public long lastAdTicks;
            public int dealDay;
            public bool freeDealClaimed;
            public bool goldDealBought;

            /// <summary>1: progress on the merged and retired cards has been moved (see CardMerges); 2: prompt 17 D's merges too.</summary>
            public int rosterVersion;

            /// <summary>
            /// The base loadout (see BaseLoadout): HQ level, a tower for each hardpoint by size,
            /// utility modules, outpost towers. baseTowers is the old point loadout (one list),
            /// moved into the sized lists once (baseVersion 2).
            /// </summary>
            public int baseLevel;
            public int baseVersion;
            public List<string> baseSmall = new();
            public List<string> baseMedium = new();
            public List<string> baseLarge = new();
            public List<string> baseTowers = new();

            /// <summary>Towers whose rank-7 branch was chosen, and the branch def each fights as.</summary>
            public List<string> branchTowers = new();
            public List<string> branchChoices = new();

            /// <summary>The tower-branch rework (DECISIONS 19T): towers whose next branch change is free, once each.</summary>
            public List<string> freeBranchSwaps = new();

            /// <summary>The reworked towers to tell the player about once ("what's new"); empty once shown.</summary>
            public List<string> branchNews = new();

            /// <summary>Prompt 32 L1: retired tower cards whose base slots were emptied, to tell the player once; empty once shown.</summary>
            public List<string> rosterNews = new();

            /// <summary>
            /// Prompt 32 L4: the HQ type ("fortress", "garrison", "shield"; empty: the data's default) and a Fortress's
            /// branch ("ground", "air"). hqTypeVersion 1: the HQ doctrine's change to the HQ type has been told once.
            /// </summary>
            public string hqType = "";
            public string hqBranch = "";

            /// <summary>Prompt 32 L3: each wall line's type, outer first ("none", "hesco", "t_wall", "gun_wall"; missing: the data's default).</summary>
            public List<string> wallTypes = new();
            public int hqTypeVersion;
            public bool hqTypeNews;
            public List<string> baseUtilities = new();
            public List<string> baseOutpost = new();

            /// <summary>
            /// Tower equipment (see PlayerProfile.TowerGear.cs): the tower types that have a loadout,
            /// and for each three piece ids in towerGear (Weapon, Structure, Systems; 0: empty).
            /// </summary>
            public List<string> towerGearIds = new();
            public List<int> towerGear = new();
            /// <summary>The player has set the base up on the base screen: an empty camp stays empty.</summary>
            public bool baseEdited;

            /// <summary>
            /// Prompt 14 G, version 3: the base as three plans (see PlayerProfile.BasePlans.cs) and the one in use; the
            /// sized lists above are what version 2 kept, moved into the first plan once.
            /// </summary>
            public List<PlanData> basePlans = new();
            public int basePlan;

            /// <summary>
            /// 2: mission progress is in the story campaign's ids; 3: in the twelve chapters' ids (prompt 20;
            /// see <see cref="MigrateCampaign"/>).
            /// </summary>
            public int campaignVersion;

            /// <summary>Prompt 20: the HQ level a save of the nine-chapter campaign had opened (kept when the levels moved).</summary>
            public int hqKept;

            /// <summary>Chapters whose opening card (the chapter transition) has been shown.</summary>
            public List<int> chaptersSeen = new();

            /// <summary>Prompt 22 D.5: the story's choices made, "choice=option" ("c4.pursuit=sea"); see PlayerProfile.Story.cs.</summary>
            public List<string> storyChoices = new();

            /// <summary>Prompt 23 E: intel files an interception recovered (prompt 22 D.7's ids), besides their own way of being found.</summary>
            public List<string> intelFiles = new();

            /// <summary>Prompt 20 N: the Boss Hunts' checkpoints (one a kind), the full hunt's best times and its first-clear pay.</summary>
            public List<HuntSave> hunts = new();
            public List<float> fullHuntTimes = new();
            public bool fullHuntPaid;

            /// <summary>Prompt 28 H.14: the last tactic per game mode (parallel lists); see PlayerProfile.Tactics.cs.</summary>
            public List<string> tacticModes = new();
            public List<string> tacticIds = new();

            /// <summary>Prompt 28 H.10: the per-squad tactics by squad number (after chapter 6).</summary>
            public List<string> squadTacticKeys = new();
            public List<string> squadTacticIds = new();

            /// <summary>Prompt 28 E.1: the targeting mode picked per tower type on the Base screen.</summary>
            public List<string> towerModeIds = new();
            public List<string> towerModes = new();
        }

        /// <summary>A new profile's base at HQ level 5: a mix of all three sizes (anti-air, guns, artillery, watchtowers).</summary>
        public static readonly string[] DefaultSmall = { "guard_tower", "aa_turret", "mg_bunker", "guard_tower", "aa_turret", "mg_bunker" };

        public static readonly string[] DefaultMedium = { "gun_turret", "rocket_turret", "atgm_tower" };

        /// <summary>
        /// The heavy fortress and the artillery emplacement: measured best of the candidates against
        /// a mixed army with the attackers knowing the towers (DECISIONS 3, "Base table").
        /// </summary>
        public static readonly string[] DefaultLarge = { "heavy_turret", "missile_battery" };

        /// <summary>2: the base loadout is in sized lists (see <see cref="Data.baseVersion"/>).</summary>
        internal const int BaseVersion = 2;

        /// <summary>Moves a base loadout saved as one list of towers (fortification points) into the sized lists, once.</summary>
        private static void MigrateBase(Data d)
        {
            if (d.baseVersion >= BaseVersion) return;
            if (d.baseTowers.Count > 0)
            {
                var moved = Sim.Modes.BaseLoadout.FromTowerList(GameContent.LoadCatalog(), d.baseLevel > 0 ? d.baseLevel : 5, d.baseTowers, d.baseUtilities, d.baseOutpost.Count > 0 ? d.baseOutpost : null);
                d.baseSmall = new List<string>(moved.Small);
                d.baseMedium = new List<string>(moved.Medium);
                d.baseLarge = new List<string>(moved.Large);
                d.baseTowers.Clear();
            }
            d.baseVersion = BaseVersion;
        }

        /// <summary>How a save before DECISIONS 23D kept a bought doctrine: "doctrine.air" and so on.</summary>
        internal const string OldDoctrinePrefix = "doctrine.";

        /// <summary>The four doctrines that were sold (the armoured one was free).</summary>
        internal static readonly string[] OldDoctrinesSold = { "air", "artillery", "blitz", "logistics" };

        internal const int OldDoctrinePrice = 1500;

        /// <summary>
        /// DECISIONS 23D: the doctrines are folded into the commanders. A save that bought any gets the 1,500 coins back
        /// for each, and every doctrine entry goes (the free one's too). Once only: the refund and the removal are
        /// saved together, so a later load finds nothing to pay. What was paid waits for the menu (<see cref="TakeRefundNews"/>).
        /// </summary>
        private static void RefundOldDoctrines(Data d)
        {
            if (d.owned == null) return;
            var paid = 0;
            foreach (var doctrine in OldDoctrinesSold)
                if (d.owned.Contains(OldDoctrinePrefix + doctrine)) paid += OldDoctrinePrice;
            var removed = d.owned.RemoveAll(id => id != null && id.StartsWith(OldDoctrinePrefix, StringComparison.Ordinal));
            if (removed == 0) return;
            d.coins += paid;
            _refundNews += paid;
            Save();
        }

        private static int _refundNews;

        /// <summary>Coins an old save got back for its doctrines at this load (0: none), once: the menu says so.</summary>
        public static int TakeRefundNews()
        {
            var coins = _refundNews;
            _refundNews = 0;
            return coins;
        }

        private const string Key = "mb.profile";
        private static Data _data;

        /// <summary>Raised whenever coins, rank, unlocks or the skin change.</summary>
        public static event Action Changed;

        private static Data D
        {
            get
            {
                if (_data == null) Load();
                return _data;
            }
        }

        public static int Coins => D.coins;
        public static int Level => D.level;
        public static int Xp => D.xp;

        /// <summary>XP needed from the start of this rank to the next.</summary>
        public static int XpForNext => XpForLevel(D.level);

        public static int XpForLevel(int level) => 300 + 200 * (Mathf.Max(1, level) - 1);

        /// <summary>Coins granted on reaching a rank.</summary>
        public static int LevelBonus(int level) => 150 * level;

        public static string EquippedSkin => D.skin;

        public static bool IsUnlocked(string cardId) =>
            Progression.TestUnlockAll || Progression.IsStarter(cardId) || D.unlocked.Contains(cardId) || D.owned.Contains(cardId);

        /// <summary>Owned items: skins and premium cards.</summary>
        public static bool Owns(string itemId) => itemId == Skins.Default || D.owned.Contains(itemId);

        public static int Stars(string missionId)
        {
            var i = D.missionIds.IndexOf(missionId);
            return i >= 0 ? D.missionStars[i] : 0;
        }

        public static bool Completed(string missionId) => Stars(missionId) > 0;

        private static void DailyReset(int day)
        {
            if (D.dailyDay == day && D.dailyProgress.Count == 3 && D.dailyClaimed.Count == 3) return;
            D.dailyDay = day;
            D.dailyProgress = new List<int> { 0, 0, 0 };
            D.dailyClaimed = new List<bool> { false, false, false };
        }

        public static int DailyProgress(int day, int index)
        {
            DailyReset(day);
            return D.dailyProgress[index];
        }

        public static bool DailyClaimed(int day, int index)
        {
            DailyReset(day);
            return D.dailyClaimed[index];
        }

        public static void AddDailyProgress(int day, int index, int amount, int cap)
        {
            DailyReset(day);
            var next = Mathf.Min(cap, D.dailyProgress[index] + amount);
            if (next == D.dailyProgress[index]) return;
            D.dailyProgress[index] = next;
            Save();
        }

        public static void ClaimDaily(int day, int index)
        {
            DailyReset(day);
            D.dailyClaimed[index] = true;
            Save();
        }

        /// <summary>How many of a single-use item (MOAB, EMP...) the player has.</summary>
        public static int ItemCount(string itemId)
        {
            var i = D.itemIds.IndexOf(itemId);
            return i >= 0 ? D.itemCounts[i] : 0;
        }

        public static void AddItems(string itemId, int count)
        {
            var i = D.itemIds.IndexOf(itemId);
            if (i < 0)
            {
                D.itemIds.Add(itemId);
                D.itemCounts.Add(0);
                i = D.itemIds.Count - 1;
            }
            D.itemCounts[i] = Mathf.Max(0, D.itemCounts[i] + count);
            Save();
        }

        /// <summary>Buys <paramref name="count"/> of an item for coins.</summary>
        public static bool TryBuyItems(string itemId, int count, int price)
        {
            if (!TrySpend(price)) return false;
            AddItems(itemId, count);
            return true;
        }

        /// <summary>One item was used in battle.</summary>
        public static void UseItem(string itemId) => AddItems(itemId, -1);

        public static int TotalStars
        {
            get
            {
                var total = 0;
                foreach (var s in D.missionStars) total += s;
                return total;
            }
        }

        public static void AddCoins(int amount)
        {
            if (amount == 0) return;
            D.coins = Mathf.Max(0, D.coins + amount);
            Save();
        }

        /// <summary>Spends coins if there are enough.</summary>
        public static bool TrySpend(int amount)
        {
            if (amount < 0 || D.coins < amount) return false;
            D.coins -= amount;
            Save();
            return true;
        }

        /// <summary>Adds XP, ranking up as often as it reaches. Returns the ranks gained (each already paid its bonus).</summary>
        public static List<int> AddXp(int amount)
        {
            var gained = new List<int>();
            D.xp += Mathf.Max(0, amount);
            while (D.xp >= XpForLevel(D.level))
            {
                D.xp -= XpForLevel(D.level);
                D.level++;
                D.coins += LevelBonus(D.level);
                gained.Add(D.level);
            }
            Save();
            return gained;
        }

        /// <summary>Unlocks a card; returns false if it already was.</summary>
        public static bool Unlock(string cardId)
        {
            // Prompt 22 E: a story unit (Mara's Behemoth) is never a card to unlock.
            if (GameContent.LoadCatalog().Vehicles.TryGetValue(cardId, out var story) && story.StoryOnly) return false;
            if (IsUnlocked(cardId)) return false;
            D.unlocked.Add(cardId);
            Save();
            return true;
        }

        /// <summary>Buys an item (skin, premium card or early unlock) for coins.</summary>
        public static bool TryBuy(string itemId, int price)
        {
            if (Owns(itemId)) return true;
            if (!TrySpend(price)) return false;
            D.owned.Add(itemId);
            Save();
            return true;
        }

        public static void Equip(string skinId)
        {
            if (!Owns(skinId) || D.skin == skinId) return;
            D.skin = skinId;
            Save();
        }

        /// <summary>Records a mission result, keeping the best star count and tier. Returns true on the first clear.</summary>
        public static bool RecordMission(string missionId, int stars, int tier = 0)
        {
            var i = D.missionIds.IndexOf(missionId);
            var first = i < 0 || D.missionStars[i] == 0;
            if (i < 0)
            {
                D.missionIds.Add(missionId);
                D.missionStars.Add(stars);
                D.missionTiers.Add(stars > 0 ? tier : -1);
            }
            else
            {
                if (stars > D.missionStars[i]) D.missionStars[i] = stars;
                if (stars > 0 && tier > D.missionTiers[i]) D.missionTiers[i] = tier;
            }
            Save();
            return first && stars > 0;
        }

        /// <summary>The hardest tier a mission has been won at (-1: not won yet).</summary>
        public static int MissionTier(string missionId)
        {
            var i = D.missionIds.IndexOf(missionId);
            return i >= 0 && D.missionStars[i] > 0 ? Math.Max(0, D.missionTiers[i]) : -1;
        }

        /// <summary>3: progress is kept under the twelve chapters' mission ids (prompt 20); 4: chapters of 9-18 missions and the interludes (prompt 22).</summary>
        internal const int CampaignVersion = 4;

        /// <summary>The HQ level a save of the nine-chapter campaign had opened (0: none kept).</summary>
        public static int HqLevelKept => D.hqKept;

        /// <summary>
        /// Moves a save's progress to the campaign as it is now, once. A save of the old 23-mission
        /// campaign (version 0 or 1): each old mission's stars and best tier go to the mission it
        /// became (<see cref="Sim.Content.MissionDef.Legacy"/>), keeping the better of the two when both
        /// were played. A save of the nine-chapter story (version 2, prompt 20 B.3): every mission's
        /// stars and tier follow it to its new id (campaign.json "migration", all at once), the chapter
        /// cards seen follow their chapters, and the HQ level it had opened is kept. Cards won stay
        /// unlocked (they are kept by id), so nothing the player had is lost; the new missions around
        /// them are open to play (a won mission opens the one after it). A save of the twelve chapters of ten
        /// (version 3, prompt 22 B): the missions that moved (a side mission made a main one, a mission moved to
        /// another chapter) take their stars along (campaign.json "migration22"); a version 2 save takes both steps.
        /// </summary>
        private static void MigrateCampaign(Data d)
        {
            if (d.campaignVersion >= CampaignVersion) return;
            if (d.campaignVersion == 2)
            {
                MoveToTwelveChapters(d);
                Move(d, Campaign.Meta.Moves22);
            }
            else if (d.campaignVersion == 3) Move(d, Campaign.Meta.Moves22);
            else FromOldCampaign(d);
            d.campaignVersion = CampaignVersion;
        }

        private static void MoveToTwelveChapters(Data d)
        {
            var meta = Campaign.Meta;
            foreach (var (old, level) in meta.OldHq)
            {
                var at = d.missionIds.IndexOf(old);
                if (at >= 0 && d.missionStars[at] > 0) d.hqKept = Math.Max(d.hqKept, level);
            }
            Move(d, meta.Moves);
            var seen = new List<int>();
            foreach (var c in d.chaptersSeen)
            {
                var n = meta.ChaptersSeen.TryGetValue(c, out var to) ? to : c;
                if (!seen.Contains(n)) seen.Add(n);
            }
            d.chaptersSeen = seen;
        }

        /// <summary>Every mission's stars and best tier to its new id (all at once), the better of two kept when two land on one.</summary>
        private static void Move(Data d, IReadOnlyDictionary<string, string> moves)
        {
            var ids = new List<string>();
            var stars = new List<int>();
            var tiers = new List<int>();
            for (var i = 0; i < d.missionIds.Count; i++)
            {
                var id = moves.TryGetValue(d.missionIds[i], out var moved) ? moved : d.missionIds[i];
                var star = d.missionStars[i];
                var tier = i < d.missionTiers.Count ? d.missionTiers[i] : 0;
                var j = ids.IndexOf(id);
                if (j < 0)
                {
                    ids.Add(id);
                    stars.Add(star);
                    tiers.Add(tier);
                }
                else
                {
                    stars[j] = Math.Max(stars[j], star);
                    tiers[j] = Math.Max(tiers[j], tier);
                }
            }
            d.missionIds = ids;
            d.missionStars = stars;
            d.missionTiers = tiers;
        }

        private static void FromOldCampaign(Data d)
        {
            foreach (var mission in Campaign.Everything)
            {
                if (mission.Legacy == null) continue;
                var old = d.missionIds.IndexOf(mission.Legacy);
                if (old < 0) continue;
                var stars = d.missionStars[old];
                var tier = old < d.missionTiers.Count ? d.missionTiers[old] : 0;
                d.missionIds.RemoveAt(old);
                d.missionStars.RemoveAt(old);
                if (old < d.missionTiers.Count) d.missionTiers.RemoveAt(old);
                var i = d.missionIds.IndexOf(mission.Id);
                if (i < 0)
                {
                    d.missionIds.Add(mission.Id);
                    d.missionStars.Add(stars);
                    d.missionTiers.Add(tier);
                }
                else
                {
                    d.missionStars[i] = Math.Max(d.missionStars[i], stars);
                    d.missionTiers[i] = Math.Max(d.missionTiers[i], tier);
                }
            }
        }

        /// <summary>The mark of the game's epilogue in the chapter cards seen (10 in the nine-chapter campaign).</summary>
        public const int EpilogueSeen = 100;

        /// <summary>Prompt 22 C.3: the mark of the flash-forward shown before the first mission.</summary>
        public const int PrologueSeen = 99;

        /// <summary>Prompt 30 L1: the mark of "Thorne's Arc Closes", the interlude card after c9m10 (before chapter 15).</summary>
        public const int ThorneArcSeen = 98;

        /// <summary>The mark of the "To be continued" card after a chapter (a release that ends before the story does).</summary>
        public static int ContinuedSeen(int chapter) => 100 + chapter;

        /// <summary>Whether a chapter's opening card has been shown.</summary>
        public static bool ChapterSeen(int chapter) => D.chaptersSeen.Contains(chapter);

        public static void MarkChapterSeen(int chapter)
        {
            if (D.chaptersSeen.Contains(chapter)) return;
            D.chaptersSeen.Add(chapter);
            Save();
        }

        /// <summary>The stage reached on this week's fortress (1 at the start of a week).</summary>
        public static int WeeklyStage(int week) => D.weeklyId == week ? D.weeklyStage : 1;

        public static bool WeeklyClaimed(int week) => WeeklyPaid(week, "fortress");

        /// <summary>Records an attack on the weekly fortress; returns true when it pays its weekly reward (the first win of the week).</summary>
        public static bool RecordWeekly(int week, int stage, bool won)
        {
            WeekOf(week);
            D.weeklyStage = Math.Max(D.weeklyStage, Math.Clamp(stage, 1, 3));
            // The same weekly ledger as the Operations mode's weekly operation.
            var pays = won && ClaimWeekly(week, "fortress");
            if (won) D.weeklyStage = 1;
            Save();
            return pays;
        }

        public static void Load()
        {
            _noSave = false;
            try
            {
                var json = PlayerPrefs.GetString(Key, "");
                _data = string.IsNullOrEmpty(json) ? new Data() : JsonUtility.FromJson<Data>(json) ?? new Data();
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[PlayerProfile] Could not read the profile: {e.Message}");
                _data = new Data();
            }
            if (!Skins.Exists(_data.skin)) _data.skin = Skins.Default;
            while (_data.missionStars.Count < _data.missionIds.Count) _data.missionStars.Add(0);
            while (_data.missionTiers.Count < _data.missionIds.Count) _data.missionTiers.Add(0);
            while (_data.itemCounts.Count < _data.itemIds.Count) _data.itemCounts.Add(0);
            FixArsenal(_data);
            MigrateBase(_data);
            MigrateToPlans(_data);
            MigrateCampaign(_data);
            RefundOldDoctrines(_data);
            MigrateHqType(_data);
        }

        public static void Save()
        {
            try
            {
                if (!_noSave)
                {
                    PlayerPrefs.SetString(Key, JsonUtility.ToJson(D));
                    PlayerPrefs.Save();
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[PlayerProfile] Could not save the profile: {e.Message}");
            }
            Changed?.Invoke();
        }

        /// <summary>
        /// Starts from an empty profile that is never written to the device (tests: the real
        /// profile, in the editor's prefs, stays as it was; <see cref="Load"/> brings it back).
        /// </summary>
        public static void ResetForTests()
        {
            _data = new Data();
            _noSave = true;
            MigrateToPlans(_data);
        }

        /// <summary>Tests: starts from a saved profile's JSON (an old save, say), never written to the device.</summary>
        internal static void LoadForTests(string json)
        {
            _data = JsonUtility.FromJson<Data>(json) ?? new Data();
            _noSave = true;
            FixArsenal(_data);
            MigrateBase(_data);
            MigrateToPlans(_data);
            MigrateCampaign(_data);
            RefundOldDoctrines(_data);
            MigrateHqType(_data);
        }

        /// <summary>Tests: the profile as it would be saved.</summary>
        internal static string JsonForTests() => JsonUtility.ToJson(D);

        private static bool _noSave;
    }
}
