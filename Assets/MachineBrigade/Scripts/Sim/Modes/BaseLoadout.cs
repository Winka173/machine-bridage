#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// A side's base as chosen before the battle, like its deck: the HQ level, the towers in the
    /// order they fill the hardpoints (front ones first), the utility modules, and the towers it
    /// flies onto an outpost's hardpoints. Nothing is built during the battle; a destroyed tower
    /// can be flown back in (see <see cref="BaseSystem"/>).
    /// </summary>
    public sealed class BaseLoadout
    {
        public int HqLevel { get; set; } = 1;
        public List<string> Towers { get; set; } = new();
        public List<string> Utilities { get; set; } = new();

        /// <summary>Towers for an outpost's hardpoints, in slot order.</summary>
        public List<string> Outpost { get; set; } = new() { "guard_tower", "gun_turret" };

        /// <summary>An HQ with nothing round it (tests, and modes that bring no loadout).</summary>
        public static BaseLoadout HqOnly(int level = 1) => new() { HqLevel = level };

        /// <summary>
        /// This loadout cut to what its HQ level allows: unknown ids and non-towers dropped, then
        /// towers in order while their points fit the budget, utility modules up to the slots.
        /// </summary>
        public BaseLoadout Fitted(Catalog catalog)
        {
            var rules = catalog.Base;
            var level = Math.Clamp(HqLevel, 1, rules.MaxLevel);
            var budget = rules.Points(level);
            var fitted = new BaseLoadout { HqLevel = level, Outpost = new List<string>(Outpost) };
            foreach (var id in Towers)
            {
                if (!catalog.Vehicles.TryGetValue(id, out var def) || def.Fort is not { Kind: FortKind.Tower } fort) continue;
                if (fort.Points > budget) continue;
                budget -= fort.Points;
                fitted.Towers.Add(id);
            }
            var slots = rules.UtilitySlots(level);
            foreach (var id in Utilities)
            {
                if (fitted.Utilities.Count >= slots) break;
                if (catalog.Vehicles.TryGetValue(id, out var def) && def.Fort is { Kind: FortKind.Utility }) fitted.Utilities.Add(id);
            }
            return fitted;
        }

        /// <summary>Fortification points the towers use.</summary>
        public int PointsUsed(Catalog catalog)
        {
            var used = 0;
            foreach (var id in Towers)
                if (catalog.Vehicles.TryGetValue(id, out var def) && def.Fort != null) used += def.Fort.Points;
            return used;
        }

        /// <summary>
        /// The AI's own base: its HQ level by difficulty, then towers drawn by the style's weights
        /// (a commander personality names its style; "default" otherwise) until the points run out,
        /// anti-air always among them. Deterministic for a seed.
        /// </summary>
        public static BaseLoadout ForAi(Catalog catalog, string difficulty, string style = "default", int seed = 1, int? level = null)
        {
            var rules = catalog.Base;
            var loadout = new BaseLoadout { HqLevel = Math.Clamp(level ?? rules.AiLevel(difficulty), 1, rules.MaxLevel) };
            var budget = rules.Points(loadout.HqLevel);
            var weights = rules.Style(style);
            var pool = new List<(string id, int points, float weight)>();
            foreach (var def in catalog.Vehicles.Values)
            {
                if (def.Fort is not { Kind: FortKind.Tower } fort || def.Id == "point_tower") continue;
                var weight = weights.TryGetValue(def.Id, out var w) ? w : weights.TryGetValue("*", out var any) ? any : 0f;
                if (weight > 0f) pool.Add((def.Id, fort.Points, weight));
            }
            pool.Sort((a, b) => string.CompareOrdinal(a.id, b.id));
            var random = new Random(seed * 7919 + budget);
            var antiAir = false;
            for (var guard = 0; guard < 40 && budget > 0; guard++)
            {
                var total = 0f;
                foreach (var p in pool)
                    if (p.points <= budget) total += p.weight;
                if (total <= 0f) break;
                var roll = (float)random.NextDouble() * total;
                foreach (var p in pool)
                {
                    if (p.points > budget) continue;
                    roll -= p.weight;
                    if (roll > 0f) continue;
                    // Anti-air first once the base is half built without any.
                    var pick = p.id;
                    if (!antiAir && budget <= rules.Points(loadout.HqLevel) / 2 && !IsAntiAir(catalog, pick))
                        foreach (var q in pool)
                            if (q.points <= budget && IsAntiAir(catalog, q.id)) { pick = q.id; break; }
                    antiAir |= IsAntiAir(catalog, pick);
                    loadout.Towers.Add(pick);
                    budget -= catalog.Vehicles[pick].Fort!.Points;
                    break;
                }
            }
            // The heaviest in front.
            loadout.Towers.Sort((a, b) => catalog.Vehicles[b].Fort!.Points.CompareTo(catalog.Vehicles[a].Fort!.Points));
            return loadout;
        }

        private static bool IsAntiAir(Catalog catalog, string id)
        {
            foreach (var m in catalog.Vehicles[id].Mounts)
                if (m.Weapon.CanTarget(true) && (m.Weapon.DamageType == DamageType.Flak || m.Weapon.Targets == TargetLayers.Air)) return true;
            return false;
        }

        public BaseLoadout Clone() => new()
        {
            HqLevel = HqLevel, Towers = new List<string>(Towers), Utilities = new List<string>(Utilities), Outpost = new List<string>(Outpost),
        };
    }
}
