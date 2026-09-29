using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 22 E (DECISIONS 22E): a mission that cuts the player's deck. A duel ("playerDeck": "air", chapter 10's
    /// Hawk and Raven) flies the deck's aircraft only, topped up to three from the fighters the player has unlocked
    /// (the fighter jet always), and takes no support cards: it is aircraft against aircraft.
    /// </summary>
    public static class MissionDecks
    {
        public const int AirMinimum = 3;

        /// <summary>The aircraft a duel's deck is topped up from, best first.</summary>
        public static readonly string[] AirFallback = { "fighter_jet", "stealth_fighter", "wingman_drone", "attack_jet", "attack_helicopter" };

        public static bool AirOnly(MissionDef mission) => mission?.PlayerDeck == "air";

        /// <summary>The vehicle cards the player fields in <paramref name="mission"/> (the deck itself for most missions).</summary>
        public static List<string> Vehicles(Catalog catalog, MissionDef mission, IEnumerable<string> deck, System.Func<string, bool> unlocked = null)
        {
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

        /// <summary>The support cards the player takes into <paramref name="mission"/> (none in a duel).</summary>
        public static List<string> Supports(MissionDef mission, IEnumerable<string> deck) =>
            AirOnly(mission) ? new List<string>() : new List<string>(deck);
    }
}
