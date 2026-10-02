#nullable enable
using System;

namespace MachineBrigade.Sim.Economy
{
    internal sealed partial class EconomySystem
    {
        /// <summary>Prompt 28 I.2: the army band's income factor for the side's vehicles out against its cap.</summary>
        private float ArmyFactor(TeamEconomy economy)
        {
            var ai = _world.Catalog.Ai;
            var edges = ai.ArmyBandEdges;
            if (edges.Count == 0 || economy.VehicleCap <= 0) return 1f;
            var share = economy.VehicleCount / (float)economy.VehicleCap;
            for (var i = edges.Count - 1; i >= 0; i--)
                if (share >= edges[i].from) return ai.Get($"economy.armyBands.{i}", 1f);
            return 1f;
        }
    }
}
