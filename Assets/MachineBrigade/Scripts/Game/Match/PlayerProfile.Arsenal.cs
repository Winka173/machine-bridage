using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The arsenal part of the profile: card ranks and blueprints,
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
            while (d.branchChoices.Count < d.branchTowers.Count) d.branchChoices.Add("");
            while (d.loadout.Count < Branches * Gear.Slots) d.loadout.Add(0);
            FixTowerGear(d);
            var kinds = Enum.GetValues(typeof(CrateKind)).Length;
            while (d.crates.Count < kinds) d.crates.Add(0);
            while (d.sinceEpic.Count < kinds) d.sinceEpic.Add(0);
            while (d.sinceLegendary.Count < kinds) d.sinceLegendary.Add(0);
            foreach (var g in d.gear) d.nextGearId = Math.Max(d.nextGearId, g.id + 1);
            if (d.gearVersion < 2) MigrateGear(d);
            if (d.gearVersion < GearVersion) MigrateFit(d);
            if (d.rosterVersion < RosterVersion) MigrateRoster(d);
            // Gems are gone (one currency now): a save that still holds some gets coins for them.
            if (d.gems > 0)
            {
                d.coins += d.gems * GemToCoins;
                d.gems = 0;
            }
        }

        /// <summary>Coins for each gem an old save still held (a legendary crate was 500 gems, now 8,000 coins).</summary>
        public const int GemToCoins = 15;

        /// <summary>The roster the save is in (see <see cref="Data.rosterVersion"/> and <see cref="CardMerges"/>).</summary>
        internal const int RosterVersion = 8;

        /// <summary>
        /// Moves progress off the cards folded into others or retired (once per save). A merged
        /// card's unlock and blueprints go to the card it became, which keeps the higher of the two
        /// ranks; the coins and blueprints spent on the lower rank come back (the blueprints as the
        /// new card's). A retired card's coins come back and its blueprints turn universal. Cards
        /// bought with coins that no longer exist are refunded. Owners of the APS tank get an Epic
        /// Trophy APS module. Version 6 (prompt 25 D2): a save that has played keeps the cards a new
        /// player no longer starts with (<see cref="Progression.FormerStarters"/>).
        /// </summary>
        private static void MigrateRoster(Data d)
        {
            foreach (var pair in CardMerges.Into)
            {
                var from = pair.Key;
                var to = pair.Value;
                var bought = d.owned.RemoveAll(id => id == from) > 0;
                var had = d.unlocked.RemoveAll(id => id == from) > 0 || bought;
                var price = 0;
                var refunded = bought && CardMerges.PremiumPrices.TryGetValue(from, out price);
                if (refunded) d.coins += price;
                if (had && !Progression.IsStarter(to))
                {
                    // A card bought and not refunded stays bought (prompt 25 D2: the AC-130 is a campaign card now, bought early).
                    var list = Progression.IsPremium(to) || (bought && !refunded) ? d.owned : d.unlocked;
                    if (!list.Contains(to)) list.Add(to);
                }
                var ranked = MergeRank(d, from, to);
                if (from == CardMerges.ApsTank && (had || ranked))
                {
                    var module = SpecialModule.TrophyAps;
                    d.gear.Add(new GearItem
                    {
                        id = d.nextGearId++, slot = (int)GearSlot.Special, rarity = (int)Rarity.Epic, level = 1,
                        special = (int)module, baseType = GearKeys.Module(module), seed = unchecked(d.nextGearId * 7919 + 17) | 1,
                    });
                }
            }
            foreach (var gone in CardMerges.Retired)
            {
                if (d.owned.RemoveAll(id => id == gone) > 0 && CardMerges.PremiumPrices.TryGetValue(gone, out var price)) d.coins += price;
                d.unlocked.RemoveAll(id => id == gone);
                var i = d.rankIds.IndexOf(gone);
                if (i < 0) continue;
                var rank = Mathf.Clamp(d.ranks[i], 1, CardRanks.Max);
                d.coins += CardRanks.CoinsSpent(rank);
                d.universal += d.prints[i] + CardRanks.BlueprintsSpent(rank);
                d.rankIds.RemoveAt(i);
                d.ranks.RemoveAt(i);
                d.prints.RemoveAt(i);
            }
            // Version 2 (prompt 17 D.4): the hidden gun pit's slots and equipment go to the gun turret.
            MergeTower(d, CardMerges.GunPit, CardMerges.GunTurret);
            // Version 3 (prompt 20 L.1): a retired branch's choice is dropped; the tower fights as itself and its next choice is free.
            foreach (var gone in CardMerges.RetiredBranches)
            {
                var k = d.branchChoices.IndexOf(gone);
                if (k < 0 || k >= d.branchTowers.Count) continue;
                d.branchChoices.RemoveAt(k);
                d.branchTowers.RemoveAt(k);
            }
            // Version 4 (the tower-branch rework, DECISIONS 19T): a remade branch's choice moves to the nearest new one, and
            // every reworked tower with a choice gets one free change and a line in the "what's new" notice.
            if (d.rosterVersion < 4)
            {
                for (var k = 0; k < d.branchChoices.Count; k++)
                    if (d.branchChoices[k] != null && CardMerges.RenamedBranches.TryGetValue(d.branchChoices[k], out var to)) d.branchChoices[k] = to;
                d.freeBranchSwaps ??= new List<string>();
                d.branchNews ??= new List<string>();
                for (var k = 0; k < d.branchTowers.Count && k < d.branchChoices.Count; k++)
                {
                    var tower = d.branchTowers[k];
                    if (string.IsNullOrEmpty(d.branchChoices[k]) || Array.IndexOf(CardMerges.ReworkedBranchTowers, tower) < 0) continue;
                    if (!d.freeBranchSwaps.Contains(tower)) d.freeBranchSwaps.Add(tower);
                    if (!d.branchNews.Contains(tower)) d.branchNews.Add(tower);
                }
            }
            // Version 6 (prompt 25 D2): the balance sheet opens the light tank, the AA vehicle and the SP gun in the campaign;
            // a player who has already played keeps them.
            if (d.rosterVersion < 6 && (d.missionIds.Count > 0 || d.unlocked.Count > 0 || d.owned.Count > 0 || d.rankIds.Count > 0))
                foreach (var id in Progression.FormerStarters)
                    if (!d.unlocked.Contains(id) && !d.owned.Contains(id)) d.unlocked.Add(id);
            if (d.rosterVersion < 7) MigrateTowerRoster(d);
            d.rosterVersion = RosterVersion;
        }

        /// <summary>
        /// Version 7 (prompt 32 L1, DECISIONS "Prompt 32 L0/L1/L2"): the tower roster 32 -> 22. A folded card's rank,
        /// slots and equipment move to the card it became (the higher rank kept); its unlock moves across, and a card the
        /// player already had makes the folded one a duplicate whose coins come back. A retired card's coins come back
        /// (with what its rank cost, its blueprints universal), its slots are emptied and its equipment returns to the
        /// bag; the menu says so once. A branch chosen on a card left without branches is dropped; a choice of a branch
        /// that changed what it does is kept with one free change and a news line.
        /// </summary>
        private static void MigrateTowerRoster(Data d)
        {
            var refund = 0;
            foreach (var pair in CardMerges.TowerInto)
            {
                var from = pair.Key;
                var to = pair.Value;
                var had = Progression.IsStarter(to) || d.owned.Contains(to) || d.unlocked.Contains(to);
                var bought = d.owned.RemoveAll(id => id == from) > 0;
                var unlocked = d.unlocked.RemoveAll(id => id == from) > 0;
                if (bought || unlocked)
                {
                    if (had)
                    {
                        if (bought && CardMerges.TowerPrices.TryGetValue(from, out var price)) refund += price;
                    }
                    else (bought ? d.owned : d.unlocked).Add(to);
                }
                MergeRank(d, from, to);
                MergeTower(d, from, to);
            }
            d.rosterNews ??= new List<string>();
            foreach (var gone in CardMerges.RetiredTowers)
            {
                if (d.owned.RemoveAll(id => id == gone) > 0 && CardMerges.TowerPrices.TryGetValue(gone, out var price)) refund += price;
                d.unlocked.RemoveAll(id => id == gone);
                var i = d.rankIds.IndexOf(gone);
                if (i >= 0)
                {
                    var rank = Mathf.Clamp(d.ranks[i], 1, CardRanks.Max);
                    refund += CardRanks.CoinsSpent(rank);
                    d.universal += d.prints[i] + CardRanks.BlueprintsSpent(rank);
                    d.rankIds.RemoveAt(i);
                    d.ranks.RemoveAt(i);
                    d.prints.RemoveAt(i);
                }
                if (EmptyTower(d, gone) && !d.rosterNews.Contains(gone)) d.rosterNews.Add(gone);
            }
            for (var k = d.branchTowers.Count - 1; k >= 0; k--)
            {
                var choice = k < d.branchChoices.Count ? d.branchChoices[k] : null;
                if (Array.IndexOf(CardMerges.NoBranchTowers, d.branchTowers[k]) < 0 && Array.IndexOf(CardMerges.RetiredBranchesP32, choice) < 0) continue;
                d.branchTowers.RemoveAt(k);
                if (k < d.branchChoices.Count) d.branchChoices.RemoveAt(k);
            }
            d.freeBranchSwaps ??= new List<string>();
            d.branchNews ??= new List<string>();
            for (var k = 0; k < d.branchTowers.Count && k < d.branchChoices.Count; k++)
            {
                if (Array.IndexOf(CardMerges.ReworkedBranchesP32, d.branchChoices[k]) < 0) continue;
                var tower = d.branchTowers[k];
                if (!d.freeBranchSwaps.Contains(tower)) d.freeBranchSwaps.Add(tower);
                if (!d.branchNews.Contains(tower)) d.branchNews.Add(tower);
            }
            if (refund <= 0) return;
            d.coins += refund;
            _rosterRefund += refund;
        }

        /// <summary>Prompt 32 L1: coins the roster change paid back at this load (duplicates and retired cards), for the menu's notice.</summary>
        private static int _rosterRefund;

        /// <summary>Prompt 32 L1: a retired tower leaves every base slot, outpost and map set-up empty (its equipment stays in the bag); true when a slot held it.</summary>
        private static bool EmptyTower(Data d, string gone)
        {
            var emptied = false;
            string Clear(string id)
            {
                if (id != gone && (id == null || !id.StartsWith(gone + "."))) return id;
                emptied = true;
                return Sim.Modes.BaseLoadout.Empty;
            }
            void ClearAll(List<string> list)
            {
                if (list == null) return;
                for (var k = 0; k < list.Count; k++) list[k] = Clear(list[k]);
            }
            ClearAll(d.baseSmall);
            ClearAll(d.baseMedium);
            ClearAll(d.baseLarge);
            ClearAll(d.baseTowers);
            ClearAll(d.baseOutpost);
            if (d.basePlans != null)
                foreach (var plan in d.basePlans)
                {
                    if (plan == null) continue;
                    foreach (var place in plan.places) place.tower = Clear(place.tower);
                    ClearAll(plan.outpost);
                    foreach (var map in plan.custom)
                    {
                        ClearAll(map.small);
                        ClearAll(map.medium);
                        ClearAll(map.large);
                    }
                }
            FixTowerGear(d);
            var i = d.towerGearIds.IndexOf(gone);
            if (i >= 0)
            {
                // Its pieces stay in the bag (d.gear); only the tower's loadout row goes.
                var n = Gear.TowerSlotCount;
                d.towerGearIds.RemoveAt(i);
                d.towerGear.RemoveRange(i * n, n);
            }
            return emptied;
        }

        /// <summary>Prompt 32 L1: the retired tower cards whose slots were emptied, for the menu's one notice; empty once taken.</summary>
        public static (List<string> emptied, int coins) TakeRosterNews()
        {
            var d = A;
            var coins = _rosterRefund;
            _rosterRefund = 0;
            if (d.rosterNews == null || d.rosterNews.Count == 0) return (new List<string>(), coins);
            var news = new List<string>(d.rosterNews);
            d.rosterNews.Clear();
            Save();
            return (news, coins);
        }

        /// <summary>
        /// A tower card folded into another (its rank went with <see cref="MergeRank"/>): every base slot, outpost and
        /// map set-up that holds it holds the other now; its equipment moves into the other's empty slots (a piece that
        /// finds its slot taken, or does not fit, goes back to the bag); its rank-7 branch choice is dropped.
        /// </summary>
        private static void MergeTower(Data d, string from, string to)
        {
            string Swap(string id) => id == from || (id != null && id.StartsWith(from + ".")) ? to : id;
            void SwapAll(List<string> list)
            {
                if (list == null) return;
                for (var k = 0; k < list.Count; k++) list[k] = Swap(list[k]);
            }
            SwapAll(d.baseSmall);
            SwapAll(d.baseMedium);
            SwapAll(d.baseLarge);
            SwapAll(d.baseTowers);
            SwapAll(d.baseOutpost);
            if (d.basePlans != null)
                foreach (var plan in d.basePlans)
                {
                    if (plan == null) continue;
                    foreach (var place in plan.places) place.tower = Swap(place.tower);
                    SwapAll(plan.outpost);
                    foreach (var map in plan.custom)
                    {
                        SwapAll(map.small);
                        SwapAll(map.medium);
                        SwapAll(map.large);
                    }
                }
            var branch = d.branchTowers.IndexOf(from);
            if (branch >= 0)
            {
                d.branchTowers.RemoveAt(branch);
                if (branch < d.branchChoices.Count) d.branchChoices.RemoveAt(branch);
            }
            FixTowerGear(d);
            var i = d.towerGearIds.IndexOf(from);
            if (i < 0) return;
            var n = Gear.TowerSlotCount;
            var j = d.towerGearIds.IndexOf(to);
            if (j < 0)
            {
                d.towerGearIds.Add(to);
                for (var k = 0; k < n; k++) d.towerGear.Add(0);
                j = d.towerGearIds.Count - 1;
            }
            TowerFit.GameCatalog.Vehicles.TryGetValue(to, out var toDef);
            for (var k = 0; k < n; k++)
            {
                var piece = d.towerGear[i * n + k];
                if (piece == 0 || d.towerGear[j * n + k] != 0) continue;
                var item = d.gear.Find(g => g != null && g.id == piece);
                if (item != null && (toDef == null || TowerFit.Fits(item, toDef))) d.towerGear[j * n + k] = piece;
            }
            d.towerGearIds.RemoveAt(i);
            d.towerGear.RemoveRange(i * n, n);
        }

        /// <summary>Folds one card's rank and blueprints into another's; false when the old card had none.</summary>
        private static bool MergeRank(Data d, string from, string to)
        {
            var i = d.rankIds.IndexOf(from);
            if (i < 0) return false;
            var fromRank = Mathf.Clamp(d.ranks[i], 1, CardRanks.Max);
            var fromPrints = d.prints[i];
            d.rankIds.RemoveAt(i);
            d.ranks.RemoveAt(i);
            d.prints.RemoveAt(i);
            var j = d.rankIds.IndexOf(to);
            if (j < 0)
            {
                d.rankIds.Add(to);
                d.ranks.Add(1);
                d.prints.Add(0);
                j = d.rankIds.Count - 1;
            }
            var toRank = Mathf.Clamp(d.ranks[j], 1, CardRanks.Max);
            var lower = Math.Min(fromRank, toRank);
            d.ranks[j] = Math.Max(fromRank, toRank);
            d.prints[j] += fromPrints + CardRanks.BlueprintsSpent(lower);
            d.coins += CardRanks.CoinsSpent(lower);
            return true;
        }

        /// <summary>
        /// The equipment model the save is in (see <see cref="Data.gearVersion"/>; 3: prompt 8's cleanup and fit matrix;
        /// 4: prompt 15's lines by armour and penetration level: every piece keeps its id, slot, rarity and level, its
        /// base type reads its new line, and a piece a branch wears that no longer fits it, such as reactive armour on
        /// aircraft, becomes one that does in the same slot, of the same rarity and level).
        /// </summary>
        internal const int GearVersion = 4;

        /// <summary>
        /// Prompt 8 (I.1, I.8): pieces of a retired or merged base type become their replacement (same
        /// slot, rarity and level); a trade-off below Rare becomes a plain type of its slot; then every
        /// piece a branch wears that no longer works for it is turned into one that does, in the same
        /// slot, of the same rarity and level (its base type, trait or module re-rolled from its own
        /// seed among those that fit), and stays on. Nothing is lost or taken off.
        /// </summary>
        private static void MigrateFit(Data d)
        {
            foreach (var g in d.gear)
                if (g != null && !Gear.IsTower(g.Slot)) Gear.Upgrade(g);
            for (var b = 0; b < Branches; b++)
                for (var s = 0; s < Gear.Slots; s++)
                {
                    var i = b * Gear.Slots + s;
                    if (i >= d.loadout.Count) continue;
                    var item = d.gear.Find(g => g != null && g.id == d.loadout[i]);
                    if (item != null) Gear.MakeFit(item, (GearBranch)b);
                }
            d.gearVersion = GearVersion;
        }

        /// <summary>
        /// Equipment from before the affix model: every piece gets a base type, a brand, its sub-stats
        /// and (Epic and up) a trait (see <see cref="Gear.Migrate"/>); Plating pieces become Armor
        /// pieces with a plating base type. A branch that wore both keeps its armour kit in the Armor
        /// slot and the plating goes back to the bag; one that wore only plating wears it as armour.
        /// The old Plating slot is now Optics, left empty. Nothing is lost.
        /// </summary>
        private static void MigrateGear(Data d)
        {
            var wasPlating = new HashSet<int>();
            foreach (var g in d.gear)
            {
                if (g == null) continue;
                if (g.slot == Gear.LegacyPlatingSlot) wasPlating.Add(g.id);
                Gear.Migrate(g);
            }
            d.gear.RemoveAll(g => g == null);
            for (var b = 0; b < Branches; b++)
            {
                var armor = b * Gear.Slots + (int)GearSlot.Armor;
                var old = b * Gear.Slots + Gear.LegacyPlatingSlot;
                if (old >= d.loadout.Count) continue;
                var plating = d.loadout[old];
                d.loadout[old] = 0;
                if (plating != 0 && wasPlating.Contains(plating) && d.loadout[armor] == 0) d.loadout[armor] = plating;
            }
            d.gearVersion = GearVersion;
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

        /// <summary>Universal blueprints (a side mission's rare blueprints).</summary>
        public static void AddUniversalBlueprints(int count)
        {
            if (count <= 0) return;
            A.universal += count;
            Save();
        }

        /// <summary>
        /// The main deck the campaign's blueprints go to: the battle deck's vehicles and supports,
        /// then the base's first six tower types.
        /// </summary>
        public static List<string> MainDeck()
        {
            var cards = new List<string>();
            foreach (var id in MatchSettings.DeckVehicles)
                if (!cards.Contains(id)) cards.Add(id);
            foreach (var id in MatchSettings.DeckSupports)
                if (!cards.Contains(id)) cards.Add(id);
            var towers = 0;
            foreach (var id in BaseLoadout.Towers)
            {
                if (towers >= 6 || string.IsNullOrEmpty(id) || cards.Contains(id)) continue;
                cards.Add(id);
                towers++;
            }
            return cards;
        }

        /// <summary>
        /// A mission's blueprints for the main deck: an even share each, the rest one apiece to the
        /// cards furthest behind (lowest rank, then fewest blueprints). Returns what each card got.
        /// </summary>
        public static List<(string card, int count)> AddDeckBlueprints(int count)
        {
            var paid = new List<(string, int)>();
            var cards = MainDeck();
            if (count <= 0 || cards.Count == 0) return paid;
            var each = count / cards.Count;
            var rest = count - each * cards.Count;
            var behind = new List<string>(cards);
            behind.Sort((a, b) =>
            {
                var byRank = Rank(a).CompareTo(Rank(b));
                return byRank != 0 ? byRank : Blueprints(a).CompareTo(Blueprints(b));
            });
            foreach (var card in cards)
            {
                var n = each + (behind.IndexOf(card) < rest ? 1 : 0);
                if (n <= 0) continue;
                A.prints[CardIndex(card)] += n;
                paid.Add((card, n));
            }
            Save();
            return paid;
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

        /// <summary>The piece equipped in a branch's slot, or null (always null for a tower slot).</summary>
        public static GearItem Equipped(GearBranch branch, GearSlot slot) =>
            (int)slot < Gear.Slots ? FindGear(A.loadout[(int)branch * Gear.Slots + (int)slot]) : null;

        public static IEnumerable<GearItem> Loadout(GearBranch branch)
        {
            for (var s = 0; s < Gear.Slots; s++)
                if (FindGear(A.loadout[(int)branch * Gear.Slots + s]) is { } item) yield return item;
        }

        /// <summary>
        /// Equips a piece in its own slot of a branch (taking it off another branch that had it). Refused
        /// (false) for a piece that does not work for the branch (prompt 8 I.1). Tower pieces go on tower
        /// types (<see cref="EquipTower(string, GearItem)"/>).
        /// </summary>
        public static bool Equip(GearBranch branch, GearItem item)
        {
            if (item == null || !A.gear.Contains(item) || Gear.IsTower(item.Slot) || !VehicleFit.Fits(item, branch)) return false;
            for (var i = 0; i < A.loadout.Count; i++)
                if (A.loadout[i] == item.id) A.loadout[i] = 0;
            A.loadout[(int)branch * Gear.Slots + item.slot] = item.id;
            Save();
            return true;
        }

        public static void Unequip(GearBranch branch, GearSlot slot)
        {
            if ((int)slot >= Gear.Slots) return;
            A.loadout[(int)branch * Gear.Slots + (int)slot] = 0;
            Save();
        }

        /// <summary>Whether a branch or a tower type wears the piece.</summary>
        public static bool IsEquipped(GearItem item) => item != null && item.id > 0 && (A.loadout.Contains(item.id) || A.towerGear.Contains(item.id));

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
                for (var i = 0; i < A.towerGear.Count; i++)
                    if (A.towerGear[i] == f.id) A.towerGear[i] = 0;
                A.gear.Remove(f);
            }
            keep.rarity++;
            keep.level = Mathf.Min(keep.level, Gear.LevelCap[keep.rarity]);
            // It keeps its base type, sub-stats and trait; a new sub-stat slot and (at Epic) a trait are rolled.
            Gear.Promote(keep, DeckBranches | WornBy(keep));
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

        /// <summary>
        /// Sets an Epic or Legendary piece's trait to one of the three it was offered when it reached
        /// Epic (<see cref="GearItem.traitOptions"/>): for a trait-choice screen. Returns whether it took.
        /// </summary>
        public static bool ChooseTrait(GearItem item, string traitKey)
        {
            if (item == null || !A.gear.Contains(item) || item.traitOptions == null || !item.traitOptions.Contains(traitKey)) return false;
            item.trait = traitKey;
            Save();
            return true;
        }

        /// <summary>The branches of the battle deck (crates and merges favour them).</summary>
        public static BranchMask DeckBranches => Gear.DeckMask(MatchSettings.DeckVehicles);

        /// <summary>The branches whose loadouts wear this piece.</summary>
        private static BranchMask WornBy(GearItem item)
        {
            var mask = BranchMask.None;
            for (var i = 0; i < A.loadout.Count; i++)
                if (A.loadout[i] == item.id)
                    mask |= GearCatalog.MaskOf((GearBranch)(i / Gear.Slots));
            return mask;
        }

        /// <summary>The set brands a branch's loadout wears, for chips such as "Ironclad 2/4".</summary>
        public static List<Gear.SetChip> SetChips(GearBranch branch) => Gear.SetChips(Loadout(branch));

        /// <summary>
        /// What the player's upgrades do to a vehicle of this card: its rank and its branch's loadout;
        /// a tower (or its branch def) its card's rank and its type's three pieces, under the tower caps.
        /// </summary>
        public static VehicleBoost BoostFor(VehicleDef def) =>
            def.Fort != null ? Gear.TowerBoost(Rank(def.CardId), TowerGear(def.CardId), BaseBrandCounts()) : Gear.Boost(Rank(def.Id), Loadout(Gear.BranchOf(def)));

        // ------------------------------------------------------------------ tower cards

        /// <summary>The branch def a tower fights as, once its card reached rank 7 and one was chosen; null otherwise.</summary>
        public static string TowerBranch(string towerId)
        {
            var i = A.branchTowers.IndexOf(towerId);
            if (i < 0 || Rank(towerId) < Sim.Modes.TowerCards.BranchRank) return null;
            return A.branchChoices[i];
        }

        /// <summary>A tower branch may be chosen: no campaign mission opens it, or it has been won.</summary>
        public static bool BranchOpen(string branchId) => Progression.UnlockMission(branchId) == null || IsUnlocked(branchId);

        /// <summary>Coins to change a tower's branch once one was chosen (the first choice is free).</summary>
        public const int BranchSwapCoins = 800;

        /// <summary>The tower's next branch change is free (the tower-branch rework's one free change, DECISIONS 19T).</summary>
        public static bool FreeBranchSwap(string towerId) => A.freeBranchSwaps != null && A.freeBranchSwaps.Contains(towerId);

        /// <summary>The reworked towers the player has not been told about yet, and marks them told.</summary>
        public static List<string> TakeBranchNews()
        {
            var d = A;
            if (d.branchNews == null || d.branchNews.Count == 0) return new List<string>();
            var news = new List<string>(d.branchNews);
            d.branchNews.Clear();
            Save();
            return news;
        }

        /// <summary>Chooses a tower's branch (rank 7 and up): free the first time (and once after the rework), <see cref="BranchSwapCoins"/> to change it.</summary>
        public static bool TryChooseBranch(string towerId, string branchId)
        {
            if (Rank(towerId) < Sim.Modes.TowerCards.BranchRank) return false;
            // A branch the campaign opens (prompt 16: the long-range coastal battery, from Leviathan) waits for it.
            if (!BranchOpen(branchId)) return false;
            var d = A;
            var i = d.branchTowers.IndexOf(towerId);
            if (i >= 0 && d.branchChoices[i] == branchId) return true;
            var free = i >= 0 && FreeBranchSwap(towerId);
            if (i >= 0 && !free && !TrySpend(BranchSwapCoins)) return false;
            if (free) d.freeBranchSwaps.Remove(towerId);
            // One reference for both lists: A re-checks them between reads.
            if (i < 0)
            {
                d.branchTowers.Add(towerId);
                d.branchChoices.Add(branchId);
            }
            else d.branchChoices[i] = branchId;
            Save();
            return true;
        }

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
            var loot = Crates.Open(kind, rng, cards, ref sinceEpic, ref sinceLegendary, NextGearId, DeckBranches, BaseTowerNeeds());
            A.sinceEpic[(int)kind] = sinceEpic;
            A.sinceLegendary[(int)kind] = sinceLegendary;
            A.coins += loot.Coins;
            A.universal += loot.Universal;
            foreach (var (card, count) in loot.Blueprints) A.prints[CardIndex(card)] += count;
            A.gear.AddRange(loot.Gear);
            Save();
            return loot;
        }

        /// <summary>Buys a crate with coins (battle crates are not sold).</summary>
        public static bool TryBuyCrate(CrateKind kind)
        {
            var price = Crates.CoinPrice[(int)kind];
            if (price <= 0 || !TrySpend(price)) return false;
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
