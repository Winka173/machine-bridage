using System.Collections.Generic;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 26 E.1 (DECISIONS 26E): P, the player's effective damage a second on a boss, ESTIMATED once from the carried deck
    /// (its cards, their ranks, gear and the commander: the boosts), with no battle fought. A Boss Hunt then sets each boss's
    /// health to P x its target seconds x 0.6 x m (<see cref="Sim.Modes.BossRushRules.Power"/>).
    /// </summary>
    public static class HuntPower
    {
        /// <summary>How many of the deck's vehicles are in the fight at once (a hunt's army, about a third of the army cap).</summary>
        public const float Fielded = 10f;

        /// <summary>The share of paper damage that lands on a boss (moving, range, armour, misses): a starting value, to measure.</summary>
        public const float Uptime = 0.3f;

        /// <summary>The least P: a deck of nothing still gets a boss it can bring down.</summary>
        public const float Floor = 60f;

        /// <summary>
        /// One vehicle's paper damage a second as its card rank, gear and commander make it (the main weapon's sustained damage
        /// x the boost's damage and fire rate).
        /// </summary>
        public static float Dps(VehicleDef def, VehicleBoost boost) =>
            def.Weapon == null ? 0f : FirePower.Sustained(def.Weapon, def) * boost.Damage * boost.FireRate;

        /// <summary>
        /// P for a deck: the mean paper damage of its combat cards, times the vehicles fielded, times the share that lands. The cards
        /// without a gun, fixed defences and bosses do not count; an empty deck gives the floor.
        /// </summary>
        public static float Estimate(IEnumerable<(VehicleDef def, VehicleBoost boost)> deck)
        {
            var sum = 0f;
            var n = 0;
            foreach (var (def, boost) in deck)
            {
                if (def.Static || def.Boss || def.CpCost <= 0) continue;
                var dps = Dps(def, boost);
                if (dps <= 0f) continue;
                sum += dps;
                n++;
            }
            return n == 0 ? Floor : UnityEngine.Mathf.Max(Floor, sum / n * Fielded * Uptime);
        }

        /// <summary>P for the deck being carried now: the profile's ranks and gear, and the commander picked (null: none).</summary>
        public static float ForDeck(Catalog catalog, IEnumerable<string> deckVehicles, CommanderDef commander)
        {
            var cards = new List<(VehicleDef, VehicleBoost)>();
            foreach (var id in deckVehicles)
                if (catalog.Vehicles.TryGetValue(id, out var def))
                    cards.Add((def, CommanderRules.Merge(PlayerProfile.BoostFor(def), commander, def, GearCatalog.StatCap)));
            return Estimate(cards);
        }
    }
}
