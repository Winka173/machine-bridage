using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The arsenal part of the profile: gems (the premium currency), card ranks and blueprints,
    /// equipment and the loadout of each branch, crates waiting to be opened with their pity
    /// counters, and the daily crate counters.
    /// </summary>
    public static partial class PlayerProfile
    {
        private const int Branches = 4;

        private static void FixArsenal(Data d)
        {
            while (d.ranks.Count < d.rankIds.Count) d.ranks.Add(1);
            while (d.prints.Count < d.rankIds.Count) d.prints.Add(0);
            while (d.loadout.Count < Branches * Gear.Slots) d.loadout.Add(0);
            var kinds = Enum.GetValues(typeof(CrateKind)).Length;
            while (d.crates.Count < kinds) d.crates.Add(0);
            while (d.sinceEpic.Count < kinds) d.sinceEpic.Add(0);
            while (d.sinceLegendary.Count < kinds) d.sinceLegendary.Add(0);
            foreach (var g in d.gear) d.nextGearId = Math.Max(d.nextGearId, g.id + 1);
        }

        private static Data A
        {
            get
            {
                var d = D;
                FixArsenal(d);
                return d;
            }
        }

        // ------------------------------------------------------------------ gems

        public static int Gems => A.gems;

        public static void AddGems(int amount)
        {
            if (amount == 0) return;
            A.gems = Mathf.Max(0, A.gems + amount);
            Save();
        }

        public static bool TrySpendGems(int amount)
        {
            if (amount < 0 || A.gems < amount) return false;
            A.gems -= amount;
            Save();
            return true;
        }

        // ------------------------------------------------------------------ card ranks

        public static int Rank(string cardId)
        {
            var i = A.rankIds.IndexOf(cardId);
            return i >= 0 ? Mathf.Clamp(A.ranks[i], 1, CardRanks.Max) : 1;
        }

        public static int Blueprints(string cardId)
        {
            var i = A.rankIds.IndexOf(cardId);
            return i >= 0 ? A.prints[i] : 0;
        }

        /// <summary>Blueprints that count for any card (from gold and legendary crates).</summary>
        public static int UniversalBlueprints => A.universal;

        private static int CardIndex(string cardId)
        {
            var i = A.rankIds.IndexOf(cardId);
            if (i >= 0) return i;
            A.rankIds.Add(cardId);
            A.ranks.Add(1);
            A.prints.Add(0);
            return A.rankIds.Count - 1;
        }

        public static void AddBlueprints(string cardId, int count)
        {
            if (count <= 0) return;
            var i = CardIndex(cardId);
            A.prints[i] += count;
            Save();
        }

        /// <summary>Whether a card can rank up now: enough coins, and blueprints (its own first, universal ones to make up the rest).</summary>
        public static bool CanRankUp(string cardId)
        {
            var rank = Rank(cardId);
            if (rank >= CardRanks.Max || !IsUnlocked(cardId)) return false;
            return Coins >= CardRanks.CoinsToNext(rank) && Blueprints(cardId) + UniversalBlueprints >= CardRanks.BlueprintsToNext(rank);
        }

        public static bool TryRankUp(string cardId)
        {
            if (!CanRankUp(cardId)) return false;
            var i = CardIndex(cardId);
            var rank = A.ranks[i];
            var need = CardRanks.BlueprintsToNext(rank);
            var own = Math.Min(need, A.prints[i]);
            A.prints[i] -= own;
            A.universal -= need - own;
            A.coins -= CardRanks.CoinsToNext(rank);
            A.ranks[i] = rank + 1;
            Save();
            return true;
        }

        // ------------------------------------------------------------------ equipment

        public static IReadOnlyList<GearItem> GearOwned => A.gear;

        public static GearItem FindGear(int id) => id <= 0 ? null : A.gear.Find(g => g.id == id);

        internal static int NextGearId() => A.nextGearId++;

        public static void AddGear(GearItem item)
        {
            if (item == null) return;
            if (item.id <= 0) item.id = NextGearId();
            A.gear.Add(item);
            Save();
        }

        /// <summary>The piece equipped in a branch's slot, or null.</summary>
        public static GearItem Equipped(GearBranch branch, GearSlot slot) => FindGear(A.loadout[(int)branch * Gear.Slots + (int)slot]);

        public static IEnumerable<GearItem> Loadout(GearBranch branch)
        {
            for (var s = 0; s < Gear.Slots; s++)
                if (FindGear(A.loadout[(int)branch * Gear.Slots + s]) is { } item) yield return item;
        }

        /// <summary>Equips a piece in its own slot of a branch (taking it off another branch that had it).</summary>
        public static void Equip(GearBranch branch, GearItem item)
        {
            if (item == null || !A.gear.Contains(item)) return;
            for (var i = 0; i < A.loadout.Count; i++)
                if (A.loadout[i] == item.id) A.loadout[i] = 0;
            A.loadout[(int)branch * Gear.Slots + item.slot] = item.id;
            Save();
        }

        public static void Unequip(GearBranch branch, GearSlot slot)
        {
            A.loadout[(int)branch * Gear.Slots + (int)slot] = 0;
            Save();
        }

        public static bool IsEquipped(GearItem item) => item != null && A.loadout.Contains(item.id);

        public static bool TryLevelGear(GearItem item)
        {
            var cost = Gear.LevelCost(item);
            if (item == null || cost <= 0 || !TrySpend(cost)) return false;
            item.level++;
            Save();
            return true;
        }

        /// <summary>
        /// Merges three identical pieces into one of the next rarity (always succeeds): the one
        /// kept is the equipped or highest-level one, it keeps its level, and the coins spent
        /// levelling the other two come back. Returns the merged piece, or null.
        /// </summary>
        public static GearItem TryMerge(GearItem item)
        {
            if (item == null) return null;
            var same = A.gear.FindAll(g => g != item && Gear.CanMerge(g, item));
            if (same.Count < 2) return null;
            // The two best partners (equipped, then higher level), and of the three the one to keep.
            same.Sort((x, y) => Worth(y).CompareTo(Worth(x)));
            var trio = new List<GearItem> { item, same[0], same[1] };
            var keep = trio[0];
            foreach (var g in trio)
                if (Worth(g) > Worth(keep)) keep = g;
            var fodder = trio;
            fodder.Remove(keep);
            foreach (var f in fodder)
            {
                A.coins += Gear.Spent(f);
                for (var i = 0; i < A.loadout.Count; i++)
                    if (A.loadout[i] == f.id) A.loadout[i] = 0;
                A.gear.Remove(f);
            }
            keep.rarity++;
            keep.level = Mathf.Min(keep.level, Gear.LevelCap[keep.rarity]);
            Save();
            return keep;
        }

        private static int Worth(GearItem g) => (IsEquipped(g) ? 1000 : 0) + g.level;

        /// <summary>Merges everything that can be merged, lowest rarity first; returns how many merges were made.</summary>
        public static int MergeAll()
        {
            var merges = 0;
            for (var pass = 0; pass < 50; pass++)
            {
                GearItem candidate = null;
                foreach (var g in A.gear)
                {
                    if (A.gear.FindAll(o => o != g && Gear.CanMerge(o, g)).Count < 2) continue;
                    if (candidate == null || g.rarity < candidate.rarity) candidate = g;
                }
                if (candidate == null || TryMerge(candidate) == null) break;
                merges++;
            }
            return merges;
        }

        /// <summary>What the player's upgrades do to a vehicle of this card: its rank and its branch's loadout.</summary>
        public static VehicleBoost BoostFor(VehicleDef def) => Gear.Boost(Rank(def.Id), Loadout(Gear.BranchOf(def)));

        /// <summary>How much harder a strike card hits at its rank.</summary>
        public static float StrikeBoost(string supportId) => 1f + CardRanks.Bonus(Rank(supportId));

        // ------------------------------------------------------------------ crates

        public static int CrateCount(CrateKind kind) => A.crates[(int)kind];

        public static void AddCrate(CrateKind kind, int count = 1)
        {
            A.crates[(int)kind] = Mathf.Max(0, A.crates[(int)kind] + count);
            Save();
        }

        /// <summary>Crates of this kind opened since the last epic (and legendary) piece: the pity counters shown on the odds screen.</summary>
        public static int SinceEpic(CrateKind kind) => A.sinceEpic[(int)kind];

        public static int SinceLegendary(CrateKind kind) => A.sinceLegendary[(int)kind];

        /// <summary>Opens a crate the player has: rolls it, pays it into the profile, and returns what came out (null if there was none).</summary>
        public static Crates.Loot OpenCrate(CrateKind kind, System.Random rng = null)
        {
            if (CrateCount(kind) <= 0) return null;
            A.crates[(int)kind]--;
            rng ??= new System.Random(Environment.TickCount ^ A.nextGearId * 7919);
            var cards = new List<string>();
            foreach (var id in MatchSettings.AllVehicles)
                if (IsUnlocked(id) && Rank(id) < CardRanks.Max) cards.Add(id);
            foreach (var id in MatchSettings.AllSupports)
                if (IsUnlocked(id) && Rank(id) < CardRanks.Max) cards.Add(id);
            var sinceEpic = A.sinceEpic[(int)kind];
            var sinceLegendary = A.sinceLegendary[(int)kind];
            var loot = Crates.Open(kind, rng, cards, ref sinceEpic, ref sinceLegendary, NextGearId);
            A.sinceEpic[(int)kind] = sinceEpic;
            A.sinceLegendary[(int)kind] = sinceLegendary;
            A.coins += loot.Coins;
            A.universal += loot.Universal;
            foreach (var (card, count) in loot.Blueprints) A.prints[CardIndex(card)] += count;
            A.gear.AddRange(loot.Gear);
            Save();
            return loot;
        }

        /// <summary>Buys a crate with gems or coins (where it is sold for coins).</summary>
        public static bool TryBuyCrate(CrateKind kind, bool withGems)
        {
            var price = withGems ? Crates.GemPrice[(int)kind] : Crates.CoinPrice[(int)kind];
            if (price <= 0) return false;
            if (withGems ? !TrySpendGems(price) : !TrySpend(price)) return false;
            AddCrate(kind);
            return true;
        }

        // ------------------------------------------------------------------ daily deals

        private static void DealReset()
        {
            if (A.dealDay == Today) return;
            A.dealDay = Today;
            A.freeDealClaimed = false;
            A.goldDealBought = false;
        }

        /// <summary>Today's free crate in the shop has not been taken yet (the deal that brings players back each day).</summary>
        public static bool FreeDealReady
        {
            get
            {
                DealReset();
                return !A.freeDealClaimed;
            }
        }

        /// <summary>Takes today's free battle crate (it is added, ready to open).</summary>
        public static bool TryClaimFreeDeal()
        {
            if (!FreeDealReady) return false;
            A.freeDealClaimed = true;
            A.crates[(int)CrateKind.Battle]++;
            Save();
            return true;
        }

        /// <summary>Today's gold crate at 30 % off, once a day.</summary>
        public static int GoldDealPrice => Crates.CoinPrice[(int)CrateKind.Gold] * 7 / 10;

        public static bool GoldDealReady
        {
            get
            {
                DealReset();
                return !A.goldDealBought;
            }
        }

        public static bool TryBuyGoldDeal()
        {
            if (!GoldDealReady || !TrySpend(GoldDealPrice)) return false;
            A.goldDealBought = true;
            A.crates[(int)CrateKind.Gold]++;
            Save();
            return true;
        }

        // ------------------------------------------------------------------ daily crates

        private static int Today => (int)(DateTime.Now.Date - new DateTime(2024, 1, 1)).TotalDays;

        /// <summary>A win: a battle crate for each of the first five of the day. Returns whether one was given.</summary>
        public static bool GrantWinCrate()
        {
            if (A.winCrateDay != Today)
            {
                A.winCrateDay = Today;
                A.winCrates = 0;
            }
            if (A.winCrates >= DailyCrates.WinCrates) return false;
            A.winCrates++;
            A.crates[(int)CrateKind.Battle]++;
            Save();
            return true;
        }

        public static int WinCratesLeft => A.winCrateDay != Today ? DailyCrates.WinCrates : DailyCrates.WinCrates - A.winCrates;

        public static int AdCratesLeft => A.adDay != Today ? DailyCrates.AdCrates : Math.Max(0, DailyCrates.AdCrates - A.ads);

        /// <summary>Time until the next ad crate may be watched (zero when ready).</summary>
        public static TimeSpan AdCrateWait
        {
            get
            {
                if (AdCratesLeft <= 0) return TimeSpan.Zero;
                var next = new DateTime(A.lastAdTicks) + DailyCrates.AdCooldown;
                var wait = next - DateTime.Now;
                return wait > TimeSpan.Zero ? wait : TimeSpan.Zero;
            }
        }

        /// <summary>An ad was watched to the end: its crate is added. Returns the crate, or null if none was due.</summary>
        public static CrateKind? GrantAdCrate()
        {
            if (A.adDay != Today)
            {
                A.adDay = Today;
                A.ads = 0;
            }
            if (A.ads >= DailyCrates.AdCrates || AdCrateWait > TimeSpan.Zero) return null;
            var kind = DailyCrates.AdCrate(A.ads);
            A.ads++;
            A.lastAdTicks = DateTime.Now.Ticks;
            A.crates[(int)kind]++;
            Save();
            return kind;
        }
    }
}
