#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// Prompt 32 L6: the opening squad (see <see cref="OpeningRules"/>). Each role of the commander's (or the enemy
    /// general's) row takes the deck's cheapest card of that role (baseCP, then id; a card of 0 CP, a fixed structure, a
    /// boss or an elite never); a role the deck has no card for is left out and its CP kept; the squad's baseCP never
    /// passes the share of the starting CP (a card that would is left out). The squad drops from tick 0 as bought vehicles.
    /// Deterministic: no random draw.
    /// </summary>
    public static class OpeningSquads
    {
        /// <summary>The squad's vehicles for <paramref name="roles"/> from <paramref name="deck"/> (empty deck: every card of the role), within <paramref name="budget"/> CP.</summary>
        public static List<string> Pick(Catalog catalog, IReadOnlyList<string> roles, IReadOnlyList<string> deck, float budget)
        {
            var squad = new List<string>();
            var spent = 0f;
            foreach (var roleId in roles)
            {
                if (!catalog.Opening.Roles.TryGetValue(roleId, out var role)) continue;
                VehicleDef? best = null;
                void Consider(string id)
                {
                    if (!catalog.Vehicles.TryGetValue(id, out var def) || !Eligible(def)) return;
                    if (role.MaxCp > 0 ? def.BaseCp > role.MaxCp : !Contains(role.Ids, id)) return;
                    if (best == null || def.BaseCp < best.BaseCp || (def.BaseCp == best.BaseCp && string.CompareOrdinal(def.Id, best.Id) < 0)) best = def;
                }
                if (deck.Count > 0)
                    foreach (var id in deck) Consider(id);
                else if (role.MaxCp > 0)
                    foreach (var def in catalog.Vehicles.Values) Consider(def.Id);
                else
                    foreach (var id in role.Ids) Consider(id);
                if (best == null || spent + best.BaseCp > budget + 1e-4f) continue;
                spent += best.BaseCp;
                squad.Add(best.Id);
            }
            return squad;
        }

        /// <summary>A card an opening squad may hold: bought for CP, not a fixed structure, a boss, an elite or a ship.</summary>
        public static bool Eligible(VehicleDef def) =>
            def.BaseCp > 0 && !def.Static && !def.Boss && !def.Elite && def.Fort == null && def.Naval == null;

        /// <summary>
        /// Drops a side's squad now (tick 0): its baseCP comes off the side's starting CP. Returns the vehicles dropped.
        /// </summary>
        /// <param name="startCp">The starting CP the share is of (null: the CP the side has now, at tick 0 its starting CP).</param>
        public static List<string> Apply(SimWorld world, int team, IReadOnlyList<string> roles, float? startCp = null)
        {
            var dropped = new List<string>();
            if (roles.Count == 0 || !world.TryGetEconomy(team, out var economy)) return dropped;
            var share = world.Catalog.Opening.Share;
            // At most the share of the starting CP, and never more than the side has.
            var budget = startCp is { } start ? MathF.Min(economy.Cp, world.Catalog.Opening.StartCp(world.ModeTag, start) * share) : economy.Cp * share;
            foreach (var id in Pick(world.Catalog, roles, economy.Vehicles, budget))
                if (world.Economy.DeployOpening(team, id).Accepted) dropped.Add(id);
            return dropped;
        }

        private static bool Contains(IReadOnlyList<string> list, string id)
        {
            foreach (var x in list)
                if (x == id) return true;
            return false;
        }
    }
}
