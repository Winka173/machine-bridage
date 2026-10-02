#nullable enable
using System;
using MachineBrigade.Sim.AI;

namespace MachineBrigade.Sim
{
    public sealed partial class SimWorld
    {
        private WorldModel? _intel;

        /// <summary>Prompt 28 A: the shared battlefield picture the AI layers read (refreshed on demand, read-only).</summary>
        public WorldModel Intel => _intel ??= new WorldModel(this);

        /// <summary>
        /// Prompt 28 N: a random stream for one AI layer of one side, from the battle's seed. Each layer has its own
        /// stream, so adding or reordering a draw in one never shifts another's (or the battle's own), and a replay of
        /// the same seed draws the same numbers. Layers: 0 commander, 1 squads, 2 units, 3 tactic choice; free above.
        /// </summary>
        public Random AiRandom(int team, int layer) => new(unchecked(Seed * 7919 + (team + 3) * 104729 + layer * 1299709));
    }
}
