#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// A side's base as chosen before the battle, like its deck: the HQ level, a tower for each
    /// hardpoint by size (<see cref="Small"/>, <see cref="Medium"/>, <see cref="Large"/>, the most
    /// important slot of each size first), the utility modules, and the two towers it flies onto
    /// an outpost (a small one, then one for the medium slot). It does not depend on the map: the
    /// i-th small slot of the map's camp takes Small[i]. Nothing is built during the battle; a
    /// destroyed tower can be flown back in (see <see cref="BaseSystem"/>).
    /// </summary>
    public sealed class BaseLoadout
    {
        public int HqLevel { get; set; } = 1;

        /// <summary>
        /// Laid on a long battlefield's layered base (prompt 17 B.4): the HQ level opens the long table's slots
        /// (more of every size), and its forward strongpoints repeat the towers (<see cref="BaseRules.ForwardSlots"/>).
        /// </summary>
        public bool Layered { get; set; }

        /// <summary>Towers for the small hardpoints (light towers only).</summary>
        public List<string> Small { get; set; } = new();

        /// <summary>Towers for the medium hardpoints (light or medium).</summary>
        public List<string> Medium { get; set; } = new();

        /// <summary>Towers for the large hardpoints (any).</summary>
        public List<string> Large { get; set; } = new();

        public List<string> Utilities { get; set; } = new();

        /// <summary>Towers for an outpost's hardpoints: the small slot's, then the medium slot's.</summary>
        public List<string> Outpost { get; set; } = new() { "guard_tower", "gun_turret" };

        /// <summary>The rank-7 branch each tower fights as (tower id → branch def id); a tower not in it fights as itself.</summary>
        public Dictionary<string, string> Branches { get; set; } = new();

        /// <summary>The def a tower of the loadout is raised as: its chosen branch, else itself.</summary>
        public string DefFor(string towerId) => Branches.TryGetValue(towerId, out var branch) ? branch : towerId;

        /// <summary>The towers of one size's hardpoints.</summary>
        public List<string> Of(SlotSize size) => size switch { SlotSize.Small => Small, SlotSize.Medium => Medium, _ => Large };

        /// <summary>
        /// An entry for a slot left empty on purpose (the base screen): it keeps the towers after it
        /// in their own slots instead of moving them up one.
        /// </summary>
        public const string Empty = "";

        /// <summary>
        /// The tower a fortress raises in its <paramref name="index"/>-th hardpoint of a size (counted
        /// over the whole fortress): the towers this loadout lists for that size, in order and over
        /// again (a fortress has more hardpoints than a camp), empty entries skipped. A size the
        /// loadout has nothing for takes the next smaller size's towers (they fit). Null: none at all.
        /// </summary>
        public string? TowerForFortress(SlotSize size, int index)
        {
            for (var s = (int)size; s >= 0; s--)
            {
                var list = Of((SlotSize)s);
                var n = 0;
                foreach (var id in list)
                    if (!string.IsNullOrEmpty(id)) n++;
                if (n == 0) continue;
                var k = index % n;
                foreach (var id in list)
                {
                    if (string.IsNullOrEmpty(id)) continue;
                    // Prompt 17 C: a fortress repeats its towers, but raises each CP relay once (two at most).
                    if (k-- == 0) return index >= n && IsRelay(_catalogForRelays, id) ? NextNonRelay(list, id) : id;
                }
            }
            return null;
        }

        /// <summary>The module a fortress raises in its <paramref name="index"/>-th utility hardpoint: each of the loadout's once, in order.</summary>
        public string? UtilityForFortress(int index)
        {
            foreach (var id in Utilities)
            {
                if (string.IsNullOrEmpty(id)) continue;
                if (index-- == 0) return id;
            }
            return null;
        }

        /// <summary>Every tower in the loadout, large slots first (empty slots left out).</summary>
        public IEnumerable<string> Towers
        {
            get
            {
                foreach (var id in Large)
                    if (!string.IsNullOrEmpty(id)) yield return id;
                foreach (var id in Medium)
                    if (!string.IsNullOrEmpty(id)) yield return id;
                foreach (var id in Small)
                    if (!string.IsNullOrEmpty(id)) yield return id;
            }
        }

        /// <summary>Prompt 17 C: CP relays already in this loadout's tower lists.</summary>
        internal int RelayCount(Catalog catalog)
        {
            var count = 0;
            foreach (var id in Towers)
                if (IsRelay(catalog, id)) count++;
            return count;
        }

        internal static bool IsRelay(Catalog? catalog, string id) =>
            catalog != null && !string.IsNullOrEmpty(id) && catalog.Vehicles.TryGetValue(id, out var def) && def.Relay != null;

        /// <summary>The catalog the fortress lookups check relays against (set by <see cref="Fitted"/>; null: none checked).</summary>
        private Catalog? _catalogForRelays;

        /// <summary>The first tower of a list after <paramref name="relay"/> that is no relay (the relay itself when all are).</summary>
        private string NextNonRelay(List<string> list, string relay)
        {
            foreach (var id in list)
                if (!string.IsNullOrEmpty(id) && !IsRelay(_catalogForRelays, id)) return id;
            return relay;
        }

        /// <summary>An HQ with nothing round it (tests, and modes that bring no loadout).</summary>
        public static BaseLoadout HqOnly(int level = 1) => new() { HqLevel = level };

        /// <summary>
        /// This loadout cut to what its HQ level allows: in each size's list only towers that fit
        /// that size, and only as many as the level opens; utility modules up to the slots. An
        /// <see cref="Empty"/> entry keeps its slot empty (trailing ones are dropped).
        /// </summary>
        public BaseLoadout Fitted(Catalog catalog)
        {
            var rules = catalog.Base;
            var level = Math.Clamp(HqLevel, 1, rules.MaxLevel);
            var fitted = new BaseLoadout { HqLevel = level, Layered = Layered, Outpost = new List<string>(Outpost), Branches = new Dictionary<string, string>(Branches), _catalogForRelays = catalog };
            foreach (SlotSize size in Enum.GetValues(typeof(SlotSize)))
            {
                var open = rules.Slots(level, size, Layered);
                var list = fitted.Of(size);
                foreach (var id in Of(size))
                {
                    if (list.Count >= open) break;
                    if (string.IsNullOrEmpty(id)) list.Add(Empty);
                    // Prompt 17 C: at most two CP relays in a base; a third slot is left empty.
                    else if (IsRelay(catalog, id) && fitted.RelayCount(catalog) >= RelayDef.MaxPerBase) list.Add(Empty);
                    else if (IsTower(catalog, id, out var fort) && fort.Fits(size)) list.Add(id);
                }
                TrimGaps(list);
            }
            var slots = rules.UtilitySlots(level, Layered);
            foreach (var id in Utilities)
            {
                if (fitted.Utilities.Count >= slots) break;
                if (string.IsNullOrEmpty(id)) fitted.Utilities.Add(Empty);
                else if (catalog.Vehicles.TryGetValue(id, out var def) && def.Fort is { Kind: FortKind.Utility }) fitted.Utilities.Add(id);
            }
            TrimGaps(fitted.Utilities);
            return fitted;
        }

        /// <summary>Drops the empty entries at the end of a list (they mean nothing there).</summary>
        internal static void TrimGaps(List<string> list)
        {
            while (list.Count > 0 && string.IsNullOrEmpty(list[list.Count - 1])) list.RemoveAt(list.Count - 1);
        }

        private static bool IsTower(Catalog catalog, string id, out FortDef fort)
        {
            fort = null!;
            if (!catalog.Vehicles.TryGetValue(id, out var def) || def.Fort is not { Kind: FortKind.Tower } f) return false;
            fort = f;
            return true;
        }

        /// <summary>
        /// A loadout from before sized slots (one list of towers, points-limited): each tower into
        /// the smallest free slot of the top HQ level it fits (large towers into large slots, medium
        /// ones into medium then large, light ones into small, then medium, then large), in order.
        /// Whatever finds no slot is left out: its rank and equipment live on the tower's card.
        /// </summary>
        public static BaseLoadout FromTowerList(Catalog catalog, int hqLevel, IEnumerable<string> towers, IEnumerable<string> utilities, IEnumerable<string>? outpost)
        {
            var rules = catalog.Base;
            var loadout = new BaseLoadout { HqLevel = Math.Clamp(hqLevel, 1, rules.MaxLevel) };
            loadout.Utilities.AddRange(utilities);
            if (outpost != null)
            {
                loadout.Outpost.Clear();
                loadout.Outpost.AddRange(outpost);
            }
            // The largest first, so a light tower never takes the only slot a heavy one could use.
            var list = new List<string>(towers);
            var order = new List<(string id, SlotSize size, int index)>();
            for (var i = 0; i < list.Count; i++)
                if (IsTower(catalog, list[i], out var fort)) order.Add((list[i], fort.Size, i));
            order.Sort((a, b) => a.size != b.size ? b.size.CompareTo(a.size) : a.index.CompareTo(b.index));
            var top = rules.MaxLevel;
            foreach (var (id, size, _) in order)
                for (var slot = size; slot <= SlotSize.Large; slot++)
                {
                    if (loadout.Of(slot).Count >= rules.Slots(top, slot)) continue;
                    loadout.Of(slot).Add(id);
                    break;
                }
            return loadout;
        }

        /// <summary>
        /// The AI's own base: its HQ level by difficulty, then a tower for every open slot, drawn
        /// by the style's weights (a general's personality names its style; "default" otherwise)
        /// among the towers that fit the slot; the large and medium slots take the tower sizes made
        /// for them when the style has any, so a base mixes all three. Anti-air is always in it.
        /// Deterministic for a seed.
        /// </summary>
        /// <param name="allowed">Only towers it lets through (prompt 14's Auto-arrange: the player's own towers); null: any.</param>
        /// <param name="layered">For a long battlefield's layered base (prompt 17 B.4): the long table's slots.</param>
        /// <param name="against">The deck it will face (prompt 20 L.1): the AI chooses its point defence's rank-7 branch by it (see <see cref="ChooseAiBranches"/>); null: no branches.</param>
        public static BaseLoadout ForAi(Catalog catalog, string difficulty, string style = "default", int seed = 1, int? level = null,
            Predicate<string>? allowed = null, bool layered = false, IReadOnlyCollection<string>? against = null)
        {
            var rules = catalog.Base;
            var loadout = new BaseLoadout { HqLevel = Math.Clamp(level ?? rules.AiLevel(difficulty), 1, rules.MaxLevel), Layered = layered };
            var weights = rules.Style(style);
            var pool = new List<(string id, SlotSize size, float weight)>();
            foreach (var def in catalog.Vehicles.Values)
            {
                if (def.Fort is not { Kind: FortKind.Tower } fort || !TowerCards.IsCard(catalog, def)) continue;
                if (allowed != null && !allowed(def.Id)) continue;
                var weight = weights.TryGetValue(def.Id, out var w) ? w : weights.TryGetValue("*", out var any) ? any : 0f;
                if (weight > 0f) pool.Add((def.Id, fort.Size, weight));
            }
            pool.Sort((a, b) => string.CompareOrdinal(a.id, b.id));
            var random = new Random(seed * 7919 + loadout.HqLevel);
            foreach (var size in new[] { SlotSize.Large, SlotSize.Medium, SlotSize.Small })
            {
                var open = rules.Slots(loadout.HqLevel, size, layered);
                for (var k = 0; k < open; k++)
                {
                    // A slot's own size first; a smaller tower only when the style has none of it.
                    var exact = pool.Exists(p => p.size == size);
                    // Prompt 17 C: two CP relays at most.
                    var relays = loadout.RelayCount(catalog) >= RelayDef.MaxPerBase;
                    var pick = Draw(pool, random, p => (exact ? p.size == size : p.size <= size) && !(relays && IsRelay(catalog, p.id)));
                    if (pick != null) loadout.Of(size).Add(pick);
                }
            }
            // Prompt 13 F.1: its first utility slot takes a landing pad (its aircraft rearm and mend there).
            if (catalog.Base.UtilitySlots(loadout.HqLevel, layered) > 0 && catalog.Vehicles.ContainsKey("airfield")) loadout.Utilities.Add("airfield");
            // Anti-air: the last small slot turns into the style's best anti-air tower if there is none.
            var hasAa = false;
            foreach (var id in loadout.Towers) hasAa |= IsAntiAir(catalog, id);
            if (!hasAa && loadout.Small.Count > 0)
            {
                var aa = Draw(pool, random, p => p.size == SlotSize.Small && IsAntiAir(catalog, p.id)) ?? (catalog.Vehicles.ContainsKey("aa_turret") ? "aa_turret" : null);
                if (aa != null) loadout.Small[loadout.Small.Count - 1] = aa;
            }
            // Prompt 25 F2 batch A (DECISIONS 25F2-A): the style's utility modules (a fire-control centre, a visual jammer) take
            // the utility slots left, by their weights; only modules a style names (never "*"), one of each.
            var modules = new List<(string id, SlotSize size, float weight)>();
            foreach (var def in catalog.Vehicles.Values)
                if (def.Fort is { Kind: FortKind.Utility } module && def.BranchOf == null && (allowed == null || allowed(def.Id)) &&
                    weights.TryGetValue(def.Id, out var mw) && mw > 0f && !loadout.Utilities.Contains(def.Id)) modules.Add((def.Id, module.Size, mw));
            modules.Sort((a, b) => string.CompareOrdinal(a.id, b.id));
            while (modules.Count > 0 && loadout.Utilities.Count < catalog.Base.UtilitySlots(loadout.HqLevel, layered))
            {
                var pick = Draw(modules, random, _ => true);
                if (pick == null) break;
                loadout.Utilities.Add(pick);
                modules.RemoveAll(m => m.id == pick);
            }
            if (against != null && difficulty != "Easy") ChooseAiBranches(catalog, loadout, against, weights);
            return loadout;
        }

        /// <summary>
        /// The AI's rank-7 branches (prompt 20 L.1 for the C-RAM; the tower-branch rework, DECISIONS 19T A.5, for every
        /// tower): each tower in the loadout takes the branch <see cref="BranchChoice"/> scores best against the deck it
        /// will face, its general's style weighing the branches it likes.
        /// </summary>
        public static void ChooseAiBranches(Catalog catalog, BaseLoadout loadout, IReadOnlyCollection<string> against, IReadOnlyDictionary<string, float>? style = null)
        {
            var threat = BranchChoice.Of(catalog, against);
            var towers = System.Linq.Enumerable.Count(loadout.Towers);
            var seen = new HashSet<string>();
            foreach (var tower in loadout.Towers)
            {
                if (!seen.Add(tower)) continue;
                var pick = BranchChoice.Pick(catalog, tower, threat, towers, style);
                if (pick != null) loadout.Branches[tower] = pick;
            }
        }

        private static string? Draw(List<(string id, SlotSize size, float weight)> pool, Random random, Predicate<(string id, SlotSize size, float weight)> fits)
        {
            var total = 0f;
            foreach (var p in pool)
                if (fits(p)) total += p.weight;
            if (total <= 0f) return null;
            var roll = (float)random.NextDouble() * total;
            foreach (var p in pool)
            {
                if (!fits(p)) continue;
                roll -= p.weight;
                if (roll <= 0f) return p.id;
            }
            return null;
        }

        internal static bool IsAntiAir(Catalog catalog, string id)
        {
            foreach (var m in catalog.Vehicles[id].Mounts)
                if (m.Weapon.CanTarget(true) && (m.Weapon.DamageType == DamageType.Fragmentation || m.Weapon.Targets == TargetLayers.Air)) return true;
            return false;
        }

        public BaseLoadout Clone() => new()
        {
            HqLevel = HqLevel, Layered = Layered, Small = new List<string>(Small), Medium = new List<string>(Medium), Large = new List<string>(Large),
            Utilities = new List<string>(Utilities), Outpost = new List<string>(Outpost), Branches = new Dictionary<string, string>(Branches),
        };
    }

    /// <summary>
    /// Tower cards: which towers go into a loadout (a capture point's watchtower, merged towers and
    /// branch defs do not: a branch fights in its tower's slot), and each tower's two rank-7 branches.
    /// </summary>
    public static class TowerCards
    {
        private static readonly HashSet<string> NotCards = new() { "point_tower", "flak_tower", "spawn_bastion" };

        /// <summary>The rank a tower card must reach to choose its branch.</summary>
        public const int BranchRank = 7;

        public static bool IsLoadoutTower(string id) => !NotCards.Contains(id) && !id.Contains('.');

        /// <summary>
        /// Prompt 32 L1: a player's tower card: a tower (not a branch, not a utility module) on the data's roster
        /// ("base.roster"; without one, every loadout tower). A tower merged into another card or retired from the roster
        /// stays a def (a map's or a mission's structure) but is no card.
        /// </summary>
        public static bool IsCard(Catalog catalog, VehicleDef def)
        {
            if (def.Fort is not { Kind: FortKind.Tower } || def.BranchOf != null || !IsLoadoutTower(def.Id)) return false;
            var roster = catalog.Base.Roster;
            if (roster.Count == 0) return true;
            for (var i = 0; i < roster.Count; i++)
                if (roster[i] == def.Id) return true;
            return false;
        }

        /// <summary>Every tower card in the catalog (loadout towers, not branches, not utility modules): the roster's order when the data has one.</summary>
        public static List<string> All(Catalog catalog)
        {
            var list = new List<string>();
            var roster = catalog.Base.Roster;
            if (roster.Count > 0)
            {
                foreach (var id in roster)
                    if (catalog.Vehicles.TryGetValue(id, out var card) && IsCard(catalog, card)) list.Add(id);
                return list;
            }
            foreach (var def in catalog.Vehicles.Values)
                if (IsCard(catalog, def)) list.Add(def.Id);
            return list;
        }

        /// <summary>
        /// A tower's branch defs, in A/B order: the two its card declares (prompt 32 L1, "branches"), none for a card with
        /// noBranch, else (data without the field) every def naming it as "branchOf", in data order.
        /// </summary>
        public static List<string> Branches(Catalog catalog, string towerId)
        {
            var list = new List<string>();
            if (catalog.Vehicles.TryGetValue(towerId, out var tower) && (tower.NoBranch || tower.DeclaredBranches.Count > 0))
            {
                foreach (var id in tower.DeclaredBranches)
                    if (catalog.Vehicles.TryGetValue(id, out var b) && b.BranchOf == towerId) list.Add(id);
                return list;
            }
            foreach (var def in catalog.Vehicles.Values)
                if (def.BranchOf == towerId) list.Add(def.Id);
            return list;
        }
    }
}
