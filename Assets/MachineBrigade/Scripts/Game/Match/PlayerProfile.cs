using System;
using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The player's progress, saved on the device: coins, rank (XP), cards unlocked, items bought
    /// (skins and premium units), the equipped skin and the stars won on each campaign mission.
    /// </summary>
    public static class PlayerProfile
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
            public List<string> itemIds = new();
            public List<int> itemCounts = new();
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

        public static bool IsUnlocked(string cardId) => Progression.IsStarter(cardId) || D.unlocked.Contains(cardId) || D.owned.Contains(cardId);

        public static bool Owns(string itemId) => itemId == Skins.Default || D.owned.Contains(itemId);

        public static int Stars(string missionId)
        {
            var i = D.missionIds.IndexOf(missionId);
            return i >= 0 ? D.missionStars[i] : 0;
        }

        public static bool Completed(string missionId) => Stars(missionId) > 0;

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

        /// <summary>Records a mission result, keeping the best star count. Returns true on the first clear.</summary>
        public static bool RecordMission(string missionId, int stars)
        {
            var i = D.missionIds.IndexOf(missionId);
            var first = i < 0 || D.missionStars[i] == 0;
            if (i < 0)
            {
                D.missionIds.Add(missionId);
                D.missionStars.Add(stars);
            }
            else if (stars > D.missionStars[i]) D.missionStars[i] = stars;
            Save();
            return first && stars > 0;
        }

        public static void Load()
        {
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
            while (_data.itemCounts.Count < _data.itemIds.Count) _data.itemCounts.Add(0);
        }

        public static void Save()
        {
            try
            {
                PlayerPrefs.SetString(Key, JsonUtility.ToJson(D));
                PlayerPrefs.Save();
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[PlayerProfile] Could not save the profile: {e.Message}");
            }
            Changed?.Invoke();
        }

        /// <summary>Forgets everything (tests and a future "reset progress" button).</summary>
        public static void ResetForTests()
        {
            _data = new Data();
        }
    }
}
