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
                if (module != null && (module.Branches & mask) != 0) return false;
                var fits = new List<ModuleDef>();
                foreach (var m in GearCatalog.Modules)
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

        /// <summary>Whether a piece works for a branch (tower pieces never do).</summary>
        public static bool FitsBranch(GearItem item, GearBranch branch) => VehicleFit.Fits(item, branch);

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
