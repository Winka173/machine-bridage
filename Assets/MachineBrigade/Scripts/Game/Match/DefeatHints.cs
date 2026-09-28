using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>What the enemy brought to a battle, counted as its vehicles came on (for the defeat hints).</summary>
    internal sealed class BattleTally
    {
        public int Enemies { get; private set; }
        public int Air { get; private set; }
        public int Armour { get; private set; }

        public void Saw(VehicleDef def)
        {
            if (def == null || def.Class == UnitClass.Defense) return;
            Enemies++;
            if (def.Flying) Air++;
            else if (def.Class is UnitClass.Tank or UnitClass.Heavy or UnitClass.Boss || def.Armor == ArmorClass.Heavy) Armour++;
        }
    }

    /// <summary>
    /// After a defeat, one or two things to change, from the battle just fought: the enemy flew a
    /// lot of aircraft and the deck has no anti-air, its armour was heavy and the deck has no tank
    /// killer, a fortress stood and there is no artillery, the deck is short, and so on (Field
    /// Command 2.0, E10). The result screen puts a button to the deck under them.
    /// </summary>
    internal static class DefeatHints
    {
        public const int Most = 2;

        /// <param name="attacking">The player had to break a fortress (Siege, Assault, the weekly fortress).</param>
        public static List<string> For(BattleTally tally, Catalog catalog, IReadOnlyList<string> vehicles, IReadOnlyList<string> supports,
            int vehicleSlots, int kills, int losses, bool attacking)
        {
            var cover = DeckRoles.Of(catalog, vehicles, supports);
            var hints = new List<string>();

            void Add(string text)
            {
                if (hints.Count < Most && !hints.Contains(text)) hints.Add(text);
            }

            var enemies = System.Math.Max(1, tally.Enemies);
            if (tally.Air >= 4 && tally.Air >= 0.2f * enemies) Add(Strings.Get(cover.AntiAir ? "result.hint.airMore" : "result.hint.air"));
            if (tally.Armour >= 6 && tally.Armour >= 0.3f * enemies && !cover.AntiTank) Add(Strings.Get("result.hint.armour"));
            if (attacking && !cover.Artillery) Add(Strings.Get("result.hint.artillery"));
            if (vehicles.Count < vehicleSlots) Add(Strings.Format("result.hint.deckShort", vehicles.Count, vehicleSlots));
            if (!cover.Repair && losses >= 12) Add(Strings.Get("result.hint.repair"));
            if (hints.Count == 0) Add(Strings.Get(losses > kills ? "result.hint.trade" : "result.hint.upgrade"));
            return hints;
        }
    }
}
