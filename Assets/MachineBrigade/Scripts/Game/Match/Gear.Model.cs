using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The affix model of a piece (docs/research 2.1): a base type with its implicit line, the
    /// main stat, 0/1/2/2/2 sub-stats by rarity that grow at levels 5, 10, 15 and 20, one trait on
    /// Epic and Legendary pieces, and a brand for set bonuses. Rolls, merges and old saves all come
    /// through here, and so do the lines the menus show.
    /// </summary>
    public static partial class Gear
    {
        /// <summary>Sub-stats a piece of each rarity carries.</summary>
        public static readonly int[] SubCount = { 0, 1, 2, 2, 2 };

        /// <summary>Levels at which every sub-stat grows by a quarter of its base roll.</summary>
        public static readonly int[] SubBumpLevels = { 5, 10, 15, 20 };

        /// <summary>Normal slots (the six that count for sets).</summary>
        public const int NormalSlots = 6;

        /// <summary>The plating base types' main stat (less damage taken) at each rarity's top level.</summary>
        private static readonly float[] PlatingTop = { 0.02f, 0.035f, 0.055f, 0.075f, 0.095f };

        /// <summary>A piece's base type (null for a piece that has none, such as one built by hand in a test).</summary>
        public static BaseTypeDef BaseOf(GearItem item) => item == null ? null : GearCatalog.Base(item.baseType);

        /// <summary>The stat a piece's main line raises: its slot's, or its base type's own (plating, an ammunition hoist).</summary>
        public static StatId MainStat(GearItem item)
        {
            var b = BaseOf(item);
            if (b != null && b.Main != StatId.Count) return b.Main;
            return DefaultMain(item.Slot, b?.Plating == true);
        }

        /// <summary>How far up its rarity's levels a piece is: 40 % of the top at level 1, all of it at the cap.</summary>
        public static float LevelShare(GearItem item)
        {
            var cap = LevelCap[Mathf.Clamp(item.rarity, 0, LevelCap.Length - 1)];
            var level = Mathf.Clamp(item.level, 1, cap);
            return 0.4f + 0.6f * (level - 1) / Mathf.Max(1, cap - 1);
        }

        /// <summary>The base type's implicit line now (grows with level like the main stat, unless it is a flat one).</summary>
        public static float ImplicitValue(GearItem item)
        {
            var b = BaseOf(item);
            if (b == null || b.Implicit == StatId.Count) return 0f;
            return b.Top[Mathf.Clamp(item.rarity, 0, 4)] * (b.Flat ? 1f : LevelShare(item));
        }

        /// <summary>A merged base type's second implicit line now (grows with level).</summary>
        public static float Implicit2Value(GearItem item)
        {
            var b = BaseOf(item);
            if (b == null || b.Implicit2 == StatId.Count || b.Top2 == null) return 0f;
            return b.Top2[Mathf.Clamp(item.rarity, 0, 4)] * LevelShare(item);
        }

        /// <summary>
        /// A trade-off's drawback (negative). It grows with the piece's level as its gain does (prompt 8
        /// I.7: a fresh piece is no longer all drawback), and with its rarity, always less than the gain.
        /// </summary>
        public static float PenaltyValue(GearItem item)
        {
            var b = BaseOf(item);
            return b != null && b.TradeOff ? b.PenaltyTop[Mathf.Clamp(item.rarity, 0, 4)] * LevelShare(item) : 0f;
        }

        /// <summary>Growth steps a piece's sub-stats have had: one at each of levels 5, 10, 15 and 20, up to one per rarity above Common.</summary>
        public static int SubBumps(GearItem item)
        {
            var n = 0;
            foreach (var t in SubBumpLevels)
                if (item.level >= t)
                    n++;
            return Mathf.Min(n, item.rarity);
        }

        /// <summary>A sub-stat's value now: its rarity's top times its roll (60 to 100 %), grown by the bumps it has had.</summary>
        public static float SubValue(GearItem item, GearSub sub)
        {
            var def = GearCatalog.Sub((StatId)sub.stat);
            if (def == null || item.rarity < 1) return 0f;
            var top = def.Values[Mathf.Clamp(item.rarity - 1, 0, def.Values.Length - 1)] * Mathf.Clamp(sub.roll, 0.6f, 1f);
            return top * (1f + 0.25f * SubBumps(item)) / (1f + 0.25f * item.rarity);
        }

        /// <summary>Where a sub-stat's roll landed between its worst and best (0 to 1): the roll-quality bar.</summary>
        public static float SubQuality(GearSub sub) => Mathf.Clamp01((sub.roll - 0.6f) / 0.4f);

        /// <summary>A piece's trait with its numbers at the piece's rarity (Epic or Legendary), or none.</summary>
        public static GearTrait TraitOf(GearItem item)
        {
            if (item == null || item.rarity < (int)Rarity.Epic || item.Slot == GearSlot.Special) return default;
            var def = GearCatalog.TraitFor(item.Slot, item.trait);
            return def?.At(item.Rarity) ?? default;
        }

        /// <summary>A special module's second number (a cooldown, a radius, a second charge).</summary>
        public static float ModulePower2(SpecialModule module, Rarity rarity)
        {
            var def = GearCatalog.Module(module);
            return def == null ? 0f : rarity >= Rarity.Legendary ? def.Legendary2 : def.Epic2;
        }

        // ------------------------------------------------------------------ lines for the menus

        public enum LineKind
        {
            Main,
            Implicit,
            Penalty,
            Sub,
        }

        /// <summary>One stat line of a piece: what it raises, by how much now, and (sub-stats) where its roll landed.</summary>
        public readonly struct Line
        {
            public Line(LineKind kind, StatId stat, float value, float quality = -1f)
            {
                Kind = kind;
                Stat = stat;
                Value = value;
                Quality = quality;
            }

            public LineKind Kind { get; }
            public StatId Stat { get; }
            public float Value { get; }

            /// <summary>0 to 1 for sub-stats (the roll bar), -1 for the other lines.</summary>
            public float Quality { get; }
        }

        /// <summary>Every stat line of a piece in the order the menus show them: main, implicit, drawback, sub-stats.</summary>
        public static List<Line> Lines(GearItem item)
        {
            var lines = new List<Line>();
            if (item == null || item.Slot == GearSlot.Special) return lines;
            lines.Add(new Line(LineKind.Main, MainStat(item), Value(item)));
            var b = BaseOf(item);
            if (b != null && b.Implicit != StatId.Count) lines.Add(new Line(LineKind.Implicit, b.Implicit, ImplicitValue(item)));
            if (b != null && b.Implicit2 != StatId.Count) lines.Add(new Line(LineKind.Implicit, b.Implicit2, Implicit2Value(item)));
            if (b != null && b.TradeOff) lines.Add(new Line(LineKind.Penalty, b.Penalty, PenaltyValue(item)));
            if (item.subs != null)
                foreach (var sub in item.subs)
                    lines.Add(new Line(LineKind.Sub, (StatId)sub.stat, SubValue(item, sub), SubQuality(sub)));
            return lines;
        }

        // ------------------------------------------------------------------ sets

        /// <summary>Pieces of each brand among a loadout's normal slots (index = brand, 1 to 13).</summary>
        public static int[] BrandCounts(IEnumerable<GearItem> loadout)
        {
            var counts = new int[GearCatalog.Brands.Length + 1];
            if (loadout == null) return counts;
            foreach (var item in loadout)
                if (item != null && item.Slot != GearSlot.Special && item.brand >= 1 && item.brand < counts.Length)
                    counts[item.brand]++;
            return counts;
        }

        /// <summary>A set chip for the loadout screen: the brand, its pieces worn, and which bonuses are on (2 and 4 pieces).</summary>
        public readonly struct SetChip
        {
            public SetChip(BrandDef brand, int count)
            {
                Brand = brand;
                Count = count;
            }

            public BrandDef Brand { get; }
            public int Count { get; }
            public bool TwoPiece => Count >= 2;
            public bool FourPiece => Count >= 4;
        }

        /// <summary>The brands a loadout wears, most pieces first (chips such as "Ironclad 2/4").</summary>
        public static List<SetChip> SetChips(IEnumerable<GearItem> loadout)
        {
            var counts = BrandCounts(loadout);
            var chips = new List<SetChip>();
            for (var b = 1; b < counts.Length; b++)
                if (counts[b] > 0)
                    chips.Add(new SetChip(GearCatalog.Brand(b), counts[b]));
            chips.Sort((x, y) => y.Count != x.Count ? y.Count.CompareTo(x.Count) : x.Brand.Index.CompareTo(y.Brand.Index));
            return chips;
        }

        // ------------------------------------------------------------------ rolls

        /// <summary>A generator for one piece's later rolls (a merge's new sub-stat and trait), the same every time.</summary>
        public static System.Random RngFor(GearItem item, int salt) =>
            new(unchecked(item.seed * 486187739 + item.id * 7919 + item.rarity * 104729 + salt * 31));

        /// <summary>A base type for a new piece of this slot and rarity, favouring the branches of the player's deck.</summary>
        public static BaseTypeDef PickBase(GearSlot slot, Rarity rarity, System.Random rng, BranchMask deck)
        {
            var pool = new List<(BaseTypeDef b, float w)>();
            var total = 0f;
            foreach (var b in GearCatalog.BasesFor(slot))
            {
                // Only what works for at least one branch drops (prompt 8 I.1).
                if ((int)rarity < b.MinRarity || b.Branches == BranchMask.None) continue;
                var w = (b.Branches & deck) != 0 ? 3f : 1f;
                pool.Add((b, w));
                total += w;
            }
            var x = (float)rng.NextDouble() * total;
            foreach (var (b, w) in pool)
            {
                x -= w;
                if (x < 0f) return b;
            }
            return pool.Count > 0 ? pool[pool.Count - 1].b : null;
        }

        /// <summary>A special module for a new Epic or Legendary piece, favouring the deck's branches.</summary>
        public static SpecialModule PickModule(System.Random rng, BranchMask deck)
        {
            var total = 0f;
            foreach (var m in GearCatalog.Modules) total += ModuleWeight(m, deck);
            var x = (float)rng.NextDouble() * total;
            foreach (var m in GearCatalog.Modules)
            {
                x -= ModuleWeight(m, deck);
                if (x < 0f) return m.Module;
            }
            return GearCatalog.Modules[GearCatalog.Modules.Length - 1].Module;
        }

        private static float ModuleWeight(ModuleDef m, BranchMask deck) => m.Branches == BranchMask.None ? 0f : (m.Branches & deck) != 0 ? 3f : 1f;

        /// <summary>Rolls sub-stats until the piece has as many as its rarity allows (never the main stat, the implicit or a repeat).</summary>
        public static void FillSubs(GearItem item, System.Random rng)
        {
            item.subs ??= new List<GearSub>();
            if (item.Slot == GearSlot.Special) return;
            var b = BaseOf(item);
            var want = b != null && b.NoSubs ? 0 : SubCount[Mathf.Clamp(item.rarity, 0, 4)];
            var main = MainStat(item);
            // A tower piece's sub-stats never ask more of a tower than its base type does.
            var tower = IsTower(item.Slot);
            var limit = tower ? TowerLimit(item) : TowerNeed.None;
            while (item.subs.Count < want)
            {
                var pool = new List<SubDef>();
                var total = 0f;
                foreach (var s in GearCatalog.Subs)
                {
                    if (!GearCatalog.RollsOn(s, item.Slot) || s.Stat == main || (b != null && (s.Stat == b.Implicit || s.Stat == b.Implicit2 || s.Stat == b.Penalty))) continue;
                    if (tower && !TowerFit.Within(TowerFit.Need(s.Stat), limit)) continue;
                    var taken = false;
                    foreach (var have in item.subs)
                        if (have.stat == (int)s.Stat)
                            taken = true;
                    if (taken) continue;
                    pool.Add(s);
                    total += s.Weight;
                }
                if (pool.Count == 0) break;
                var x = (float)rng.NextDouble() * total;
                var pick = pool[pool.Count - 1];
                foreach (var s in pool)
                {
                    x -= s.Weight;
                    if (x < 0f)
                    {
                        pick = s;
                        break;
                    }
                }
                item.subs.Add(new GearSub { stat = (int)pick.Stat, roll = 0.6f + 0.4f * (float)rng.NextDouble() });
            }
        }

        /// <summary>
        /// Up to <paramref name="count"/> different traits from a slot's pool that work for a branch the
        /// piece fits (<paramref name="fits"/>: its base type's branches), those for the deck's branches first.
        /// </summary>
        public static List<string> TraitCandidates(GearSlot slot, BranchMask deck, System.Random rng, int count = 3, BranchMask fits = BranchMask.All,
            BaseTypeDef baseType = null)
        {
            var suited = new List<TraitDef>();
            var others = new List<TraitDef>();
            foreach (var t in GearCatalog.TraitsFor(slot))
            {
                // It must work together with the piece's base type, on some class's vehicles.
                var together = baseType != null ? VehicleFit.BranchesFor(baseType, t) : t.Branches;
                if ((together & fits) == 0) continue;
                ((t.Branches & deck) != 0 ? suited : others).Add(t);
            }
            var picks = new List<string>();
            foreach (var list in new[] { suited, others })
                while (picks.Count < count && list.Count > 0)
                {
                    var i = rng.Next(list.Count);
                    picks.Add(list[i].Key);
                    list.RemoveAt(i);
                }
            return picks;
        }

        /// <summary>
        /// Gives an Epic or Legendary piece its trait: three candidates are rolled and kept (a menu can
        /// offer the choice later); for now one is chosen by the piece's own generator.
        /// </summary>
        public static void RollTrait(GearItem item, System.Random rng, BranchMask deck)
        {
            if (item.Slot == GearSlot.Special || item.rarity < (int)Rarity.Epic) return;
            var fits = BaseOf(item)?.Branches ?? BranchMask.All;
            if (fits == BranchMask.None) fits = BranchMask.All;
            item.traitOptions = IsTower(item.Slot) ? TowerTraitCandidates(item, rng)
                : TraitCandidates(item.Slot, deck == BranchMask.None ? BranchMask.All : deck, rng, 3, fits, BaseOf(item));
            item.trait = item.traitOptions.Count > 0 ? item.traitOptions[rng.Next(item.traitOptions.Count)] : "";
        }

        /// <summary>
        /// A piece just merged up a rarity: it keeps its base type, sub-stats and trait, gains the new
        /// sub-stat slot if the rarity allows one, and rolls its trait on reaching Epic (a Legendary
        /// keeps its trait at the Legendary value).
        /// </summary>
        public static void Promote(GearItem item, BranchMask deck)
        {
            var rng = RngFor(item, 1);
            FillSubs(item, rng);
            if (item.rarity >= (int)Rarity.Epic && string.IsNullOrEmpty(item.trait)) RollTrait(item, rng, deck);
        }

        /// <summary>A whole new piece: slot, base type (or module), brand, sub-stats and, from Epic, a trait.</summary>
        public static GearItem Create(Rarity rarity, System.Random rng, int id, BranchMask deck)
        {
            if (deck == BranchMask.None) deck = BranchMask.All;
            var slots = rarity >= Rarity.Epic ? Slots : Slots - 1;
            var slot = rng.Next(slots);
            var item = new GearItem { id = id, slot = slot, rarity = (int)rarity, level = 1, seed = rng.Next(1, int.MaxValue) };
            if ((GearSlot)slot == GearSlot.Special)
            {
                var module = PickModule(rng, deck);
                item.special = (int)module;
                item.baseType = GearKeys.Module(module);
                return item;
            }
            item.baseType = PickBase((GearSlot)slot, rarity, rng, deck)?.Id ?? "";
            item.brand = 1 + rng.Next(GearCatalog.VehicleBrandCount);
            FillSubs(item, rng);
            if (rarity >= Rarity.Epic) RollTrait(item, rng, deck);
            return item;
        }

        // ------------------------------------------------------------------ the deck's branches

        private static Dictionary<string, GearBranch> _branchOf;

        /// <summary>The branches of these vehicle cards (crates and merges favour them).</summary>
        public static BranchMask DeckMask(IEnumerable<string> vehicles)
        {
            var mask = BranchMask.None;
            try
            {
                if (_branchOf == null)
                {
                    var map = new Dictionary<string, GearBranch>();
                    foreach (var def in GameContent.LoadCatalog().Vehicles.Values) map[def.Id] = BranchOf(def);
                    _branchOf = map;
                }
                foreach (var id in vehicles)
                    if (id != null && _branchOf.TryGetValue(id, out var branch))
                        mask |= GearCatalog.MaskOf(branch);
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[Gear] Could not read the deck's branches: {e.Message}");
            }
            return mask == BranchMask.None ? BranchMask.All : mask;
        }

        // ------------------------------------------------------------------ old saves

        /// <summary>The plating base types, one of which an old Plating piece becomes (its main stat stays the same).</summary>
        private static readonly string[] OldPlating = { "slat_cage", "frontal_wedge", "overhead_screen", "underbelly_armor" };

        /// <summary>
        /// Brings a piece from before the affix model up to date: a Plating piece moves to the Armor
        /// slot as a plating base type (same main stat), every piece gets a base type, a brand, its
        /// rarity's sub-stats and (Epic and up) a trait, all rolled from its id so the result never
        /// changes. Its slot, rarity and level stay as they were.
        /// </summary>
        internal static void Migrate(GearItem item)
        {
            item.subs ??= new List<GearSub>();
            item.traitOptions ??= new List<string>();
            item.baseType ??= "";
            item.trait ??= "";
            if (item.seed == 0) item.seed = unchecked(item.id * 7919 + 17) | 1;
            var rng = RngFor(item, 7);
            // The old layout had Plating at index 3, where Optics is now.
            if (item.slot == LegacyPlatingSlot)
            {
                item.slot = (int)GearSlot.Armor;
                item.baseType = OldPlating[Mathf.Abs(item.id) % OldPlating.Length];
            }
            if (item.Slot == GearSlot.Special)
            {
                if (item.special <= 0) item.special = (int)SpecialModule.ReactiveArmor;
                item.baseType = GearKeys.Module((SpecialModule)item.special);
                item.brand = 0;
                return;
            }
            if (BaseOf(item) == null)
            {
                // Plain base types only (no trade-off): the piece keeps doing what it did.
                var plain = new List<BaseTypeDef>();
                foreach (var b in GearCatalog.BasesFor(item.Slot))
                    if (!b.TradeOff && !b.Plating) plain.Add(b);
                if (plain.Count > 0) item.baseType = plain[Mathf.Abs(item.id) % plain.Count].Id;
            }
            if (item.brand <= 0) item.brand = 1 + rng.Next(GearCatalog.VehicleBrandCount);
            FillSubs(item, rng);
            if (item.rarity >= (int)Rarity.Epic && string.IsNullOrEmpty(item.trait)) RollTrait(item, rng, BranchMask.All);
        }

        /// <summary>Where Plating sat in saves from before the Optics slot.</summary>
        internal const int LegacyPlatingSlot = 3;
    }
}
