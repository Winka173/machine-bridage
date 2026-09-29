#nullable enable
using System.Collections.Generic;

namespace MachineBrigade.Sim.AI
{
    public sealed partial class ConquestAi
    {
        /// <summary>
        /// Prompt 21 E.6 (the internal Sandbox only): when set, the buyer writes each card's score here every time it
        /// weighs a purchase, for the overlay that shows why it bought what it did. Null in play (nothing is written).
        /// </summary>
        public Dictionary<string, float>? BuyScores { get; set; }
    }
}
