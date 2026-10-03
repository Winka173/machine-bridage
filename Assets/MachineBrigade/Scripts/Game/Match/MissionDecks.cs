using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 22 E (DECISIONS 22E): a mission that cuts the player's deck. A duel ("playerDeck": "air", chapter 10's
    /// Hawk and Raven) flies the deck's aircraft only, topped up to three from the fighters the player has unlocked
    /// (the fighter jet always), and takes no support cards: it is aircraft against aircraft.
    /// Prompt 31 L1 (DECISIONS "Prompt 31 L0/L1/L2"): a mission with a fixed deck (<see cref="MissionDef.FixedDeck"/>)
    /// fields that deck instead of the player's, its cards at the campaign's rank curve for the mission
    /// (<see cref="Campaign.ExpectedRank"/>, plus the deck's rank bonus) and with no equipment; loaned cards included.
    /// </summary>
    public static class MissionDecks
    {
        public static int AirMinimum => global::MachineBrigade.Sim.Content.SimTunables.Campaign.MissionDecks.AirMinimum;

        /// <summary>The aircraft a duel's deck is topped up from, best first.</summary>
        public static readonly string[] AirFallback = { "fighter_jet", "stealth_fighter", "attack_jet", "attack_helicopter" };

        public static bool AirOnly(MissionDef mission) => mission?.PlayerDeck == "air";

        /// <summary>The mission hands out its own deck (prompt 31).</summary>
        public static bool IsFixed(MissionDef mission) => mission?.FixedDeck != null;

        /// <summary>The vehicle cards the side fields: the mission's fixed deck, else <paramref name="deck"/> as it is.</summary>
        public static IReadOnlyList<string> Deck(MissionDef mission, IReadOnlyList<string> deck) =>
            mission?.FixedDeck is { } fixedDeck ? fixedDeck.Vehicles : deck;

        /// <summary>The support cards the side takes: the mission's fixed deck's, else <paramref name="deck"/> as it is.</summary>
        public static IReadOnlyList<string> SupportDeck(MissionDef mission, IReadOnlyList<string> deck) =>
            mission?.FixedDeck is { } fixedDeck ? fixedDeck.Supports : deck;

        /// <summary>The vehicle cards the player fields in <paramref name="mission"/> (the deck itself for most missions).</summary>
        public static List<string> Vehicles(Catalog catalog, MissionDef mission, IEnumerable<string> deck, System.Func<string, bool> unlocked = null)
        {
            if (mission?.FixedDeck is { } fixedDeck) return new List<string>(fixedDeck.Vehicles);
            var list = new List<string>(deck);
            if (!AirOnly(mission)) return list;
            list.RemoveAll(id => !(catalog.Vehicles.TryGetValue(id, out var def) && def.Flying && def.Card && !def.Boss && !def.StoryOnly));
            foreach (var id in AirFallback)
            {
                if (list.Count >= AirMinimum) break;
                if (list.Contains(id) || !catalog.Vehicles.ContainsKey(id)) continue;
                if (id == AirFallback[0] || unlocked == null || unlocked(id)) list.Add(id);
            }
            return list;
        }

        /// <summary>The support cards the player takes into <paramref name="mission"/> (none in a duel; a fixed deck's two).</summary>
        public static List<string> Supports(MissionDef mission, IEnumerable<string> deck)
        {
            if (mission?.FixedDeck is { } fixedDeck) return new List<string>(fixedDeck.Supports);
            return AirOnly(mission) ? new List<string>() : new List<string>(deck);
        }

        /// <summary>The rank every card of a fixed deck fights at: the campaign's curve by this mission, plus the deck's bonus.</summary>
        public static int FixedRank(MissionDef mission)
        {
            var bonus = mission?.FixedDeck?.RankBonus ?? 0;
            var curve = mission != null ? Mathf.FloorToInt(Campaign.ExpectedRank(mission)) : 1;
            return Mathf.Clamp(curve + bonus, 1, CardRanks.Max);
        }

        /// <summary>A card's rank in <paramref name="mission"/>: the fixed deck's, else the player's own.</summary>
        public static int Rank(MissionDef mission, string cardId) => IsFixed(mission) ? FixedRank(mission) : PlayerProfile.Rank(cardId);

        /// <summary>
        /// What the player's upgrades do to a vehicle in <paramref name="mission"/>: a fixed deck's cards their fixed rank and no
        /// equipment; the player's own base (towers) and every other mission the profile's ranks and loadouts.
        /// </summary>
        public static VehicleBoost BoostFor(MissionDef mission, VehicleDef def) =>
            IsFixed(mission) && def.Fort == null ? Gear.Boost(FixedRank(mission), new List<GearItem>()) : PlayerProfile.BoostFor(def);

        /// <summary>How much harder a fire support card hits in <paramref name="mission"/> (its rank's bonus).</summary>
        public static float StrikeBoost(MissionDef mission, string supportId) =>
            IsFixed(mission) ? 1f + CardRanks.Bonus(FixedRank(mission)) : PlayerProfile.StrikeBoost(supportId);

        /// <summary>A card the mission lends the player (shown "Loaned for this mission"; never unlocked by it).</summary>
        public static bool Loaned(MissionDef mission, string cardId) => mission?.FixedDeck != null && mission.FixedDeck.IsLoaned(cardId);
    }
}
