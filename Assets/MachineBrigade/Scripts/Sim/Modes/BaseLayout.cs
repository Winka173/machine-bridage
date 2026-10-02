#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>Which part of a base loadout a place stands for.</summary>
    public enum LoadoutSlotKind
    {
        /// <summary>A hardpoint of the camp: the i-th of its size (<see cref="BaseLoadout.Of"/>).</summary>
        Tower,

        /// <summary>A utility hardpoint: the i-th utility module.</summary>
        Utility,

        /// <summary>One of an outpost's two towers: 0 its small slot, 1 its medium slot.</summary>
        Outpost,
    }

    /// <summary>One place of a base loadout, as the base screen edits it.</summary>
    public readonly struct LoadoutSlot : IEquatable<LoadoutSlot>
    {
        private LoadoutSlot(LoadoutSlotKind kind, SlotSize size, int index)
        {
            Kind = kind;
            Size = size;
            Index = index;
        }

        public LoadoutSlotKind Kind { get; }

        /// <summary>The largest tower size it takes.</summary>
        public SlotSize Size { get; }

        /// <summary>Its index in its list (Small, Medium, Large, Utilities or Outpost).</summary>
        public int Index { get; }

        public static LoadoutSlot Tower(SlotSize size, int index) => new(LoadoutSlotKind.Tower, size, index);

        public static LoadoutSlot Utility(int index, SlotSize size = SlotSize.Medium) => new(LoadoutSlotKind.Utility, size, index);

        /// <summary>An outpost's tower: 0 its small slot, 1 its medium slot (the order of <see cref="BaseLoadout.Outpost"/>).</summary>
        public static LoadoutSlot Outpost(int index) => new(LoadoutSlotKind.Outpost, index == 0 ? SlotSize.Small : SlotSize.Medium, index);

        public bool Equals(LoadoutSlot other) => Kind == other.Kind && Size == other.Size && Index == other.Index;
        public override bool Equals(object? obj) => obj is LoadoutSlot other && Equals(other);
        public override int GetHashCode() => ((int)Kind * 7 + (int)Size) * 31 + Index;
        public override string ToString() => $"{Kind} {Size} #{Index}";
    }

    /// <summary>A hardpoint of a map's camp with the loadout place it takes its tower from.</summary>
    public readonly struct CampSlot
    {
        public CampSlot(int hardpoint, HardpointDef def, LoadoutSlot slot, bool open)
        {
            Hardpoint = hardpoint;
            Def = def;
            Slot = slot;
            Open = open;
        }

        /// <summary>Its index in <see cref="BaseSiteDef.Slots"/>.</summary>
        public int Hardpoint { get; }

        public HardpointDef Def { get; }
        public LoadoutSlot Slot { get; }

        /// <summary>Whether the HQ level opens it (a closed one keeps its tower for a higher level).</summary>
        public bool Open { get; }
    }

    /// <summary>
    /// The base screen's rules, kept out of the UI: which loadout place each hardpoint of a camp
    /// reads (the i-th hardpoint of a size takes the i-th tower of that size, as
    /// <see cref="BaseSystem.Establish"/> raises them), what fits where, placing, clearing and
    /// moving towers (a gap stays a gap, so no tower moves by itself), and the layout that is saved.
    /// </summary>
    public static class BaseLayout
    {
        /// <summary>The outpost towers a layout falls back to (the loadout's own default).</summary>
        public static readonly string[] DefaultOutpost = { "guard_tower", "gun_turret" };

        /// <summary>Every hardpoint of a camp in map order, with its loadout place and whether this HQ level opens it.</summary>
        public static List<CampSlot> Camp(BaseSiteDef site, BaseRules rules, int level)
        {
            var list = new List<CampSlot>(site.Slots.Count);
            var seen = new int[3];
            var utility = 0;
            for (var i = 0; i < site.Slots.Count; i++)
            {
                var def = site.Slots[i];
                if (def.Kind == HardpointKind.Utility)
                {
                    list.Add(new CampSlot(i, def, LoadoutSlot.Utility(utility, def.Class), utility < rules.UtilitySlots(level, site.Layered)));
                    utility++;
                    continue;
                }
                var k = seen[(int)def.Class]++;
                list.Add(new CampSlot(i, def, LoadoutSlot.Tower(def.Class, k), k < rules.Slots(level, def.Class, site.Layered)));
            }
            return list;
        }

        private static List<string> ListOf(BaseLoadout loadout, LoadoutSlot slot) => slot.Kind switch
        {
            LoadoutSlotKind.Tower => loadout.Of(slot.Size),
            LoadoutSlotKind.Utility => loadout.Utilities,
            _ => loadout.Outpost,
        };

        /// <summary>What is in a place, or null when it is empty.</summary>
        public static string? At(BaseLoadout loadout, LoadoutSlot slot)
        {
            var list = ListOf(loadout, slot);
            return slot.Index < list.Count && !string.IsNullOrEmpty(list[slot.Index]) ? list[slot.Index] : null;
        }

        /// <summary>
        /// Whether a card goes into a place: a tower card (not a branch, not a point's watchtower)
        /// no bigger than the place for a tower or outpost place, a utility module for a utility one.
        /// </summary>
        public static bool Fits(Catalog catalog, string id, LoadoutSlot slot)
        {
            if (string.IsNullOrEmpty(id) || !catalog.Vehicles.TryGetValue(id, out var def) || def.Fort is not { } fort) return false;
            if (slot.Kind == LoadoutSlotKind.Utility) return fort.Kind == FortKind.Utility && fort.Fits(slot.Size);
            // Prompt 17 C: a CP relay is a base's, never an outpost's.
            if (slot.Kind == LoadoutSlotKind.Outpost && def.Relay != null) return false;
            return fort.Kind == FortKind.Tower && TowerCards.IsCard(catalog, def) && fort.Fits(slot.Size);
        }

        /// <summary>Puts a card into a place (replacing what was there); false when it does not fit.</summary>
        public static bool Place(BaseLoadout loadout, Catalog catalog, LoadoutSlot slot, string id)
        {
            if (!Fits(catalog, id, slot)) return false;
            var list = ListOf(loadout, slot);
            while (list.Count <= slot.Index) list.Add(BaseLoadout.Empty);
            list[slot.Index] = id;
            return true;
        }

        /// <summary>An outpost always flies in with its two towers: its places are replaced, never emptied.</summary>
        public static bool CanClear(LoadoutSlot slot) => slot.Kind != LoadoutSlotKind.Outpost;

        /// <summary>Empties a place (the others keep theirs); false for an outpost's.</summary>
        public static bool Clear(BaseLoadout loadout, LoadoutSlot slot)
        {
            if (!CanClear(slot)) return false;
            var list = ListOf(loadout, slot);
            if (slot.Index >= list.Count) return true;
            list[slot.Index] = BaseLoadout.Empty;
            BaseLoadout.TrimGaps(list);
            return true;
        }

        /// <summary>
        /// Moves a tower from one place to another. What was there goes back into the first place
        /// if it fits (a swap); otherwise the first place is left empty. False when the tower does
        /// not fit, or when the move would leave an outpost place empty.
        /// </summary>
        public static bool Move(BaseLoadout loadout, Catalog catalog, LoadoutSlot from, LoadoutSlot to)
        {
            if (from.Equals(to)) return false;
            var moving = At(loadout, from);
            if (moving == null || !Fits(catalog, moving, to)) return false;
            var displaced = At(loadout, to);
            var swap = displaced != null && Fits(catalog, displaced, from);
            if (!swap && !CanClear(from)) return false;
            Place(loadout, catalog, to, moving);
            if (swap) Place(loadout, catalog, from, displaced!);
            else Clear(loadout, from);
            return true;
        }

        /// <summary>How many of the camp's tower places hold this card (every HQ level's).</summary>
        public static int Placed(BaseLoadout loadout, string id)
        {
            var count = 0;
            foreach (var tower in loadout.Towers)
                if (tower == id) count++;
            return count;
        }

        /// <summary>
        /// The layout as it is saved: every size's list cut to the top HQ level's hardpoints (the
        /// level can go up again, so the towers of closed slots are kept), a card that does not fit
        /// its place emptied rather than moved up, trailing gaps dropped, utility modules alike,
        /// and the outpost's two towers each fitting its place (the default otherwise).
        /// </summary>
        public static BaseLoadout ForSaving(BaseLoadout loadout, Catalog catalog)
        {
            var rules = catalog.Base;
            var saved = new BaseLoadout
            {
                HqLevel = Math.Clamp(loadout.HqLevel, 1, rules.MaxLevel),
                Branches = new Dictionary<string, string>(loadout.Branches),
            };
            foreach (SlotSize size in Enum.GetValues(typeof(SlotSize)))
                Copy(loadout.Of(size), saved.Of(size), rules.Slots(rules.MaxLevel, size), i => LoadoutSlot.Tower(size, i), catalog);
            Copy(loadout.Utilities, saved.Utilities, rules.UtilitySlots(rules.MaxLevel), i => LoadoutSlot.Utility(i), catalog);
            saved.Outpost.Clear();
            for (var i = 0; i < DefaultOutpost.Length; i++)
            {
                var id = i < loadout.Outpost.Count ? loadout.Outpost[i] : null;
                saved.Outpost.Add(id != null && Fits(catalog, id, LoadoutSlot.Outpost(i)) ? id : DefaultOutpost[i]);
            }
            return saved;
        }

        private static void Copy(List<string> from, List<string> to, int slots, Func<int, LoadoutSlot> place, Catalog catalog)
        {
            for (var i = 0; i < from.Count && i < slots; i++)
                to.Add(Fits(catalog, from[i], place(i)) ? from[i] : BaseLoadout.Empty);
            BaseLoadout.TrimGaps(to);
        }
    }
}
