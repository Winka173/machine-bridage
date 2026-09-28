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
            public int adDay;
            public int ads;
            public long lastAdTicks;
            public int dealDay;
            public bool freeDealClaimed;
            public bool goldDealBought;

            /// <summary>1: progress on the merged and retired cards has been moved (see CardMerges).</summary>
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
        }

        /// <summary>
        /// The base the player takes into battle, like the deck: every HQ level is open for now
        /// (the campaign unlocks them later), so a new profile starts at the top level with a mix
        /// of towers. The sim cuts it to what the level allows.
        /// </summary>
        public static Sim.Modes.BaseLoadout BaseLoadout
        {
            get
            {
                var loadout = new Sim.Modes.BaseLoadout { HqLevel = D.baseLevel > 0 ? D.baseLevel : 5 };
                var empty = !D.baseEdited && D.baseSmall.Count + D.baseMedium.Count + D.baseLarge.Count == 0;
                loadout.Small.AddRange(empty ? DefaultSmall : D.baseSmall);
                loadout.Medium.AddRange(empty ? DefaultMedium : D.baseMedium);
                loadout.Large.AddRange(empty ? DefaultLarge : D.baseLarge);
                loadout.Utilities.AddRange(D.baseUtilities);
                foreach (var id in loadout.Towers)
                    if (TowerBranch(id) is { } branch) loadout.Branches[id] = branch;
                if (D.baseOutpost.Count > 0)
                {
                    loadout.Outpost.Clear();
                    loadout.Outpost.AddRange(D.baseOutpost);
                }
                return loadout;
            }
            set
            {
                D.baseLevel = value.HqLevel;
                D.baseSmall = new List<string>(value.Small);
                D.baseMedium = new List<string>(value.Medium);
                D.baseLarge = new List<string>(value.Large);
                D.baseTowers.Clear();
                D.baseVersion = BaseVersion;
                D.baseUtilities = new List<string>(value.Utilities);
                D.baseOutpost = new List<string>(value.Outpost);
                D.baseEdited = true;
                Save();
            }
        }

        /// <summary>A new profile's base at HQ level 5: a mix of all three sizes (anti-air, guns, artillery, watchtowers).</summary>
        public static readonly string[] DefaultSmall = { "guard_tower", "aa_turret", "mg_bunker", "guard_tower", "aa_turret", "mg_bunker" };

        public static readonly string[] DefaultMedium = { "gun_turret", "rocket_turret", "atgm_tower" };

        /// <summary>
        /// The heavy fortress and the artillery emplacement: measured best of the candidates against
        /// a mixed army with the attackers knowing the towers (DECISIONS 3, "Base table").
        /// </summary>
        public static readonly string[] DefaultLarge = { "heavy_turret", "artillery_emplacement" };

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

        /// <summary>Owned items: skins, doctrines and premium cards (in test builds every doctrine is).</summary>
        public static bool Owns(string itemId) =>
            itemId == Skins.Default || D.owned.Contains(itemId) || (Progression.TestUnlockAll && itemId.StartsWith("doctrine."));

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

        /// <summary>The stage reached on this week's fortress (1 at the start of a week).</summary>
        public static int WeeklyStage(int week) => D.weeklyId == week ? D.weeklyStage : 1;

        public static bool WeeklyClaimed(int week) => D.weeklyId == week && D.weeklyClaimed;

        /// <summary>Records an attack on the weekly fortress; returns true when it pays its weekly reward (the first win of the week).</summary>
        public static bool RecordWeekly(int week, int stage, bool won)
        {
            if (D.weeklyId != week)
            {
                D.weeklyId = week;
                D.weeklyStage = 1;
                D.weeklyClaimed = false;
            }
            D.weeklyStage = Math.Max(D.weeklyStage, Math.Clamp(stage, 1, 3));
            var pays = won && !D.weeklyClaimed;
            if (pays) D.weeklyClaimed = true;
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
        }

        /// <summary>Tests: starts from a saved profile's JSON (an old save, say), never written to the device.</summary>
        internal static void LoadForTests(string json)
        {
            _data = JsonUtility.FromJson<Data>(json) ?? new Data();
            _noSave = true;
            FixArsenal(_data);
            MigrateBase(_data);
        }

        /// <summary>Tests: the profile as it would be saved.</summary>
        internal static string JsonForTests() => JsonUtility.ToJson(D);

        private static bool _noSave;
    }
}
