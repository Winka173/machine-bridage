using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Tower equipment: pieces for the three slots of a tower type (Weapon, Structure, Systems),
    /// shared by every tower of that type in the base. They are ordinary <see cref="GearItem"/>s
    /// in the same bag as vehicle equipment, told apart by their slot: rarities, levels, merging
    /// (three of one tower slot and rarity), sub-stats and Epic traits work as for vehicles; they
    /// carry no brand (sets belong to six-slot vehicle loadouts), and the tower caps apply
    /// (<see cref="GearCatalog.TowerStatCap"/>). Every line a piece rolls works on every tower type
    /// it fits (<see cref="TowerFit"/>).
    /// </summary>
    public static partial class Gear
    {
        /// <summary>A tower type's three slots, in the order its loadout keeps them.</summary>
        public static readonly GearSlot[] TowerSlots = { GearSlot.TowerWeapon, GearSlot.TowerStructure, GearSlot.TowerSystems };

        public const int TowerSlotCount = 3;

        public static bool IsTower(GearSlot slot) => slot >= GearSlot.TowerWeapon && slot <= GearSlot.TowerSystems;

        public static bool IsTower(GearItem item) => item != null && IsTower(item.Slot);

        /// <summary>A tower slot's place in a tower type's loadout (0 Weapon, 1 Structure, 2 Systems), or -1.</summary>
        public static int TowerIndex(GearSlot slot) => IsTower(slot) ? slot - GearSlot.TowerWeapon : -1;

        // A tower piece's main stat at each rarity's top level: most stats as a vehicle's weapon
        // or armour kit, less damage taken as plating, regeneration as a repair kit.
        private static readonly float[] StandardTop = { 0.03f, 0.05f, 0.08f, 0.11f, 0.14f };
        private static readonly float[] RepairTop = { 0.002f, 0.004f, 0.006f, 0.008f, 0.01f };

        private static float TowerTop(StatId main, int rarity)
        {
            var r = Mathf.Clamp(rarity, 0, 4);
            return main switch
            {
                StatId.DamageTaken => PlatingTop[r],
                StatId.Regen => RepairTop[r],
                _ => StandardTop[r],
            };
        }

        /// <summary>The stat a slot's main line raises by default (plating base types: less damage taken).</summary>
        public static StatId DefaultMain(GearSlot slot, bool plating) => slot switch
        {
            GearSlot.Weapon or GearSlot.TowerWeapon => StatId.Damage,
            GearSlot.Loader => StatId.FireRate,
            GearSlot.Armor or GearSlot.TowerStructure => plating ? StatId.DamageTaken : StatId.Health,
            GearSlot.Optics or GearSlot.TowerSystems => StatId.Vision,
            GearSlot.Engine => StatId.Speed,
            GearSlot.Repair => StatId.Regen,
            _ => StatId.Count,
        };

        /// <summary>The stat a base type's main line raises.</summary>
        public static StatId MainStatOf(BaseTypeDef b) => b.Main != StatId.Count ? b.Main : DefaultMain(b.Slot, b.Plating);

        /// <summary>What a tower type's loadout and its card's rank do to each tower of the type (the tower caps).</summary>
        public static VehicleBoost TowerBoost(int rank, IEnumerable<GearItem> loadout) => Boost(rank, loadout, GearCatalog.TowerStatCap);

        /// <summary>
        /// A base type for a new tower piece of this slot and rarity: those that work for a tower
        /// of the player's base (<paramref name="towers"/>: what each tower type there has) three
        /// times as likely as the others.
        /// </summary>
        public static BaseTypeDef PickTowerBase(GearSlot slot, Rarity rarity, System.Random rng, IReadOnlyList<TowerNeed> towers)
        {
            var pool = new List<(BaseTypeDef b, float w)>();
            var total = 0f;
            foreach (var b in GearCatalog.TowerBasesFor(slot))
            {
                if ((int)rarity < b.MinRarity) continue;
                var w = 1f;
                if (towers != null)
                {
                    var need = TowerFit.Need(b);
                    foreach (var has in towers)
                        if (TowerFit.Within(need, has))
                        {
                            w = 3f;
                            break;
                        }
                }
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

        /// <summary>A whole new tower piece: one of the three tower slots, a base type, its sub-stats and, from Epic, a trait (no brand).</summary>
        public static GearItem CreateTower(Rarity rarity, System.Random rng, int id, IReadOnlyList<TowerNeed> towers = null)
        {
            var slot = TowerSlots[rng.Next(TowerSlots.Length)];
            var item = new GearItem { id = id, slot = (int)slot, rarity = (int)rarity, level = 1, seed = rng.Next(1, int.MaxValue) };
            item.baseType = PickTowerBase(slot, rarity, rng, towers)?.Id ?? "";
            FillSubs(item, rng);
            if (rarity >= Rarity.Epic) RollTrait(item, rng, BranchMask.All);
            return item;
        }

        /// <summary>What a tower piece's lines may need: its base type's (sub-stats and traits are rolled within it).</summary>
        private static TowerNeed TowerLimit(GearItem item)
        {
            var b = BaseOf(item);
            return b != null ? TowerFit.Need(b) : TowerFit.Need(MainStat(item));
        }

        /// <summary>Up to <paramref name="count"/> different traits from a tower slot's pool that work wherever the piece's base type does.</summary>
        public static List<string> TowerTraitCandidates(GearItem item, System.Random rng, int count = 3)
        {
            var limit = TowerLimit(item);
            var pool = new List<TraitDef>();
            foreach (var t in GearCatalog.TowerTraitsFor(item.Slot))
                if (TowerFit.Within(t.Need, limit))
                    pool.Add(t);
            var picks = new List<string>();
            while (picks.Count < count && pool.Count > 0)
            {
                var i = rng.Next(pool.Count);
                picks.Add(pool[i].Key);
                pool.RemoveAt(i);
            }
            return picks;
        }
    }
}
