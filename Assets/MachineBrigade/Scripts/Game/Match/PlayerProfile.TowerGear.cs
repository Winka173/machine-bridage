using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Tower equipment in the profile: each tower type (card) keeps three pieces, one per tower
    /// slot (Weapon, Structure, Systems), worn by every tower of that type in the base, camp and
    /// outposts alike, and by its rank-7 branch. The pieces live in the one equipment bag
    /// (<see cref="GearOwned"/>), told apart by their slot; a piece is worn by one tower type at a
    /// time, and only by a type it works for (<see cref="TowerFit"/>).
    /// </summary>
    public static partial class PlayerProfile
    {
        private static void FixTowerGear(Data d)
        {
            d.towerGearIds ??= new List<string>();
            d.towerGear ??= new List<int>();
            var want = d.towerGearIds.Count * Gear.TowerSlotCount;
            while (d.towerGear.Count < want) d.towerGear.Add(0);
            if (d.towerGear.Count > want) d.towerGear.RemoveRange(want, d.towerGear.Count - want);
        }

        /// <summary>Every tower piece in the bag.</summary>
        public static List<GearItem> TowerGearOwned => A.gear.FindAll(g => Gear.IsTower(g.Slot));

        /// <summary>Every vehicle piece in the bag (what the army's equipment screen lists).</summary>
        public static List<GearItem> VehicleGearOwned => A.gear.FindAll(g => !Gear.IsTower(g.Slot));

        /// <summary>A tower card's id for a card or one of its branch defs ("aa_turret.flak" is "aa_turret"'s); null when it is not a tower card.</summary>
        public static string TowerCardOf(string towerId)
        {
            if (string.IsNullOrEmpty(towerId) || !TowerFit.GameCatalog.Vehicles.TryGetValue(towerId, out var def) || !TowerFit.IsTowerCard(def)) return null;
            return def.CardId;
        }

        /// <summary>The def a tower card fights as now: its chosen rank-7 branch, else itself (null when it is not a tower card).</summary>
        public static VehicleDef TowerDef(string towerId)
        {
            var card = TowerCardOf(towerId);
            if (card == null) return null;
            var vehicles = TowerFit.GameCatalog.Vehicles;
            return TowerBranch(card) is { } branch && vehicles.TryGetValue(branch, out var fights) ? fights : vehicles[card];
        }

        /// <summary>Whether a piece works for a tower type as it fights now (its branch if one was chosen).</summary>
        public static bool TowerFits(string towerId, GearItem item) => TowerDef(towerId) is { } def && TowerFit.Fits(item, def);

        /// <summary>The tower pieces in the bag that work for a tower type, of one tower slot or all three, best first.</summary>
        public static List<GearItem> TowerGearFor(string towerId, GearSlot? slot = null)
        {
            var list = new List<GearItem>();
            var def = TowerDef(towerId);
            if (def == null) return list;
            foreach (var g in A.gear)
                if (Gear.IsTower(g.Slot) && (slot == null || g.Slot == slot) && TowerFit.Fits(g, def))
                    list.Add(g);
            list.Sort((x, y) => x.rarity != y.rarity ? y.rarity.CompareTo(x.rarity) : y.level.CompareTo(x.level));
            return list;
        }

        private static int TowerIndexOf(string towerId, bool add)
        {
            var d = A;
            var i = d.towerGearIds.IndexOf(towerId);
            // A branch def wears its tower's pieces.
            if (i < 0 && towerId != null && towerId.IndexOf('.') > 0) i = d.towerGearIds.IndexOf(towerId.Substring(0, towerId.IndexOf('.')));
            if (i >= 0 || !add) return i;
            d.towerGearIds.Add(towerId);
            for (var k = 0; k < Gear.TowerSlotCount; k++) d.towerGear.Add(0);
            return d.towerGearIds.Count - 1;
        }

        /// <summary>The piece a tower type wears in a tower slot, or null.</summary>
        public static GearItem TowerEquipped(string towerId, GearSlot slot)
        {
            var k = Gear.TowerIndex(slot);
            var i = TowerIndexOf(towerId, false);
            return k < 0 || i < 0 ? null : FindGear(A.towerGear[i * Gear.TowerSlotCount + k]);
        }

        /// <summary>
        /// The equipment a tower type wears (its Weapon, Structure and Systems pieces), shared by
        /// every tower of that type in the base; a branch def wears its tower's.
        /// </summary>
        public static IEnumerable<GearItem> TowerGear(string towerId)
        {
            var i = TowerIndexOf(towerId, false);
            if (i < 0) yield break;
            for (var k = 0; k < Gear.TowerSlotCount; k++)
                if (FindGear(A.towerGear[i * Gear.TowerSlotCount + k]) is { } item)
                    yield return item;
        }

        /// <summary>Equips the piece with this id in a tower type's slot (see <see cref="EquipTower(string, GearItem)"/>).</summary>
        public static bool EquipTower(string towerId, GearSlot slot, int itemId)
        {
            var item = FindGear(itemId);
            return item != null && item.Slot == slot && EquipTower(towerId, item);
        }

        /// <summary>
        /// Equips a tower piece in its slot of a tower type (a card, or one of its branch defs),
        /// taking it off another tower type that wore it. Refused (false) for a piece that is not a
        /// tower piece, not in the bag, or does not work for the tower as it fights now.
        /// </summary>
        public static bool EquipTower(string towerId, GearItem item)
        {
            if (item == null || !Gear.IsTower(item.Slot) || !A.gear.Contains(item)) return false;
            var card = TowerCardOf(towerId);
            if (card == null || !TowerFits(card, item)) return false;
            var d = A;
            for (var j = 0; j < d.towerGear.Count; j++)
                if (d.towerGear[j] == item.id) d.towerGear[j] = 0;
            var i = TowerIndexOf(card, true);
            d.towerGear[i * Gear.TowerSlotCount + Gear.TowerIndex(item.Slot)] = item.id;
            Save();
            return true;
        }

        public static void UnequipTower(string towerId, GearSlot slot)
        {
            var k = Gear.TowerIndex(slot);
            var i = TowerIndexOf(towerId, false);
            if (k < 0 || i < 0) return;
            A.towerGear[i * Gear.TowerSlotCount + k] = 0;
            Save();
        }

        /// <summary>The tower type (card id) that wears this piece, or null.</summary>
        public static string TowerWearing(GearItem item)
        {
            if (item == null || item.id <= 0) return null;
            var d = A;
            var j = d.towerGear.IndexOf(item.id);
            return j < 0 ? null : d.towerGearIds[j / Gear.TowerSlotCount];
        }

        /// <summary>What a tower type's rank and pieces do to each of its towers (for a stat preview).</summary>
        public static VehicleBoost TowerBoost(string towerId) => Gear.TowerBoost(Rank(TowerCardOf(towerId) ?? towerId), TowerGear(towerId), BaseBrandCounts());

        /// <summary>
        /// The brand pieces worn by every tower type of the base together (Bulwark Engineering's bonuses
        /// count across the whole base: three slots a tower type could never hold four pieces).
        /// </summary>
        public static int[] BaseBrandCounts()
        {
            var d = A;
            var counts = new int[GearCatalog.Brands.Length + 1];
            foreach (var id in d.towerGear)
                if (FindGear(id) is { } item && item.brand >= 1 && item.brand < counts.Length)
                    counts[item.brand]++;
            return counts;
        }

        /// <summary>What each tower type of the player's base has (crates favour tower pieces that work for one of them).</summary>
        internal static List<TowerNeed> BaseTowerNeeds()
        {
            var needs = new List<TowerNeed>();
            var seen = new HashSet<string>();
            var loadout = BaseLoadout;
            foreach (var id in loadout.Towers)
                if (seen.Add(id))
                    needs.Add(TowerFit.Of(loadout.DefFor(id)));
            foreach (var id in loadout.Outpost)
                if (seen.Add(id))
                    needs.Add(TowerFit.Of(loadout.DefFor(id)));
            return needs;
        }
    }
}
