using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 8's save upgrade for vehicle pieces: base types retired or merged become their
    /// replacement, and a piece a branch wears that no longer works for it is turned into one that does
    /// (same slot, rarity and level). Every choice comes from the piece's own id and seed, so the same
    /// save always upgrades the same way.
    /// </summary>
    public static partial class Gear
    {
        /// <summary>Brings a vehicle piece's base type up to date (retired and merged types, a trade-off below Rare).</summary>
        public static void Upgrade(GearItem item)
        {
            if (item == null || IsTower(item.Slot) || item.Slot == GearSlot.Special) return;
            if (!string.IsNullOrEmpty(item.baseType) && GearCatalog.Replaced.TryGetValue(item.baseType, out var into)) item.baseType = into;
            var b = BaseOf(item);
            // A trade-off is Rare and up: a lower one (an old save's) becomes a plain type of its slot.
            if (b != null && b.TradeOff && item.rarity < b.MinRarity)
            {
                var plain = new List<BaseTypeDef>();
                foreach (var p in GearCatalog.BasesFor(item.Slot))
                    if (!p.TradeOff && !p.Plating && p.Branches != BranchMask.None) plain.Add(p);
                if (plain.Count > 0) item.baseType = plain[Mathf.Abs(item.id) % plain.Count].Id;
            }
        }

        /// <summary>
        /// Makes a piece a branch wears work for it: its base type (or module) and its trait are swapped
        /// for ones of the same slot that fit the branch, picked from the piece's id. Returns whether it changed.
        /// </summary>
        public static bool MakeFit(GearItem item, GearBranch branch)
        {
            if (item == null || IsTower(item.Slot)) return false;
            var mask = GearCatalog.MaskOf(branch);
            var changed = false;
            if (item.Slot == GearSlot.Special)
            {
                var module = GearCatalog.Module(item.Module);
                if (module != null && !module.Hidden && (module.Branches & mask) != 0) return false;
                var fits = new List<ModuleDef>();
                foreach (var m in GearCatalog.ShownModules)
                    if ((m.Branches & mask) != 0) fits.Add(m);
                if (fits.Count == 0) return false;
                var pick = fits[Mathf.Abs(item.id) % fits.Count].Module;
                item.special = (int)pick;
                item.baseType = GearKeys.Module(pick);
                return true;
            }
            var b = BaseOf(item);
            if (b == null || (b.Branches & mask) == 0)
            {
                var fits = new List<BaseTypeDef>();
                foreach (var p in GearCatalog.BasesFor(item.Slot))
                    if ((p.Branches & mask) != 0 && item.rarity >= p.MinRarity && p.Plating == (b?.Plating ?? false)) fits.Add(p);
                if (fits.Count == 0)
                    foreach (var p in GearCatalog.BasesFor(item.Slot))
                        if ((p.Branches & mask) != 0 && item.rarity >= p.MinRarity) fits.Add(p);
                if (fits.Count > 0)
                {
                    item.baseType = fits[Mathf.Abs(item.id) % fits.Count].Id;
                    changed = true;
                }
            }
            if (item.rarity >= (int)Rarity.Epic && !string.IsNullOrEmpty(item.trait))
            {
                var t = GearCatalog.TraitFor(item.Slot, item.trait);
                if (t == null || (VehicleFit.BranchesFor(BaseOf(item), t) & mask) == 0)
                {
                    var rng = RngFor(item, 11);
                    var options = TraitCandidates(item.Slot, mask, rng, 3, mask, BaseOf(item));
                    if (options.Count > 0)
                    {
                        item.traitOptions = options;
                        item.trait = options[0];
                        changed = true;
                    }
                }
            }
            return changed;
        }

        /// <summary>Whether a piece works for a branch (tower pieces never do, nor hidden gear: see <see cref="IsHidden"/>).</summary>
        public static bool FitsBranch(GearItem item, GearBranch branch) => !IsHidden(item) && VehicleFit.Fits(item, branch);

        /// <summary>
        /// Play-test 14 lane I: whether a piece carries a hidden line (its base type, special module or trait has
        /// <c>Hidden</c> set in <see cref="GearCatalog"/>: the player's smoke gear). Such a piece is never worn into battle.
        /// </summary>
        public static bool IsHidden(GearItem item)
        {
            if (item == null) return false;
            if (item.Slot == GearSlot.Special) return GearCatalog.Module(item.Module) is { Hidden: true };
            if (BaseOf(item) is { Hidden: true }) return true;
            return !string.IsNullOrEmpty(item.trait) && GearCatalog.TraitFor(item.Slot, item.trait) is { Hidden: true };
        }

        /// <summary>
        /// Play-test 14 lane I (owner, 04/10: the player's smoke gear hidden, to come back later): an old save's piece of
        /// hidden gear becomes a shown one of the same slot, rarity and level, picked from its own id and seed (so the same
        /// save always comes out the same): a hidden module another module for the same vehicles, a hidden base type a
        /// plain one of its slot (sub-stats that clash with the new lines rolled again), a hidden trait a new roll. Hidden
        /// traits leave the trait choices too. Gear is never bought (crates, merges), so nothing is refunded and nothing
        /// is lost. Returns whether the piece changed.
        /// </summary>
        public static bool Unhide(GearItem item)
        {
            if (item == null) return false;
            if (item.Slot == GearSlot.Special)
            {
                var module = GearCatalog.Module(item.Module);
                if (module == null || !module.Hidden) return false;
                var fits = new List<ModuleDef>();
                foreach (var m in GearCatalog.ShownModules)
                    if ((m.Branches & module.Branches) != 0) fits.Add(m);
                if (fits.Count == 0)
                    foreach (var m in GearCatalog.ShownModules)
                        if (m.Branches != BranchMask.None) fits.Add(m);
                if (fits.Count == 0) return false;
                var pick = fits[Mathf.Abs(item.id) % fits.Count].Module;
                item.special = (int)pick;
                item.baseType = GearKeys.Module(pick);
                return true;
            }
            var changed = false;
            var b = BaseOf(item);
            if (b != null && b.Hidden)
            {
                var tower = IsTower(item.Slot);
                var all = new List<BaseTypeDef>(tower ? GearCatalog.TowerBasesFor(item.Slot) : GearCatalog.BasesFor(item.Slot));
                var fits = all.FindAll(p => !p.TradeOff && p.Plating == b.Plating && item.rarity >= p.MinRarity && (p.Branches & b.Branches) != 0);
                if (fits.Count == 0) fits = all.FindAll(p => !p.TradeOff && item.rarity >= p.MinRarity);
                if (fits.Count > 0)
                {
                    var into = fits[Mathf.Abs(item.id) % fits.Count];
                    item.baseType = into.Id;
                    var main = (int)MainStat(item);
                    item.subs?.RemoveAll(sub => sub.stat == main || sub.stat == (int)into.Implicit || sub.stat == (int)into.Implicit2 || sub.stat == (int)into.Penalty);
                    FillSubs(item, RngFor(item, 13));
                    changed = true;
                }
            }
            if (!string.IsNullOrEmpty(item.trait) && GearCatalog.TraitFor(item.Slot, item.trait) is { Hidden: true })
            {
                RollTrait(item, RngFor(item, 17), BranchMask.All);
                changed = true;
            }
            else if (item.traitOptions != null &&
                     item.traitOptions.RemoveAll(key => GearCatalog.TraitFor(item.Slot, key) is { Hidden: true }) > 0)
                changed = true;
            return changed;
        }

        /// <summary>The branches a vehicle piece works for (its base type or module, and its trait).</summary>
        public static BranchMask BranchesOf(GearItem item)
        {
            var mask = BranchMask.None;
            if (item == null || IsTower(item.Slot)) return mask;
            foreach (GearBranch branch in System.Enum.GetValues(typeof(GearBranch)))
                if (VehicleFit.Fits(item, branch)) mask |= GearCatalog.MaskOf(branch);
            return mask;
        }
    }
}
