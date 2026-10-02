#nullable enable
using System;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Economy
{
    /// <summary>Prompt 17 C: CP relays (a base's small tower; <see cref="RelayDef"/>).</summary>
    internal sealed partial class EconomySystem
    {
        /// <summary>
        /// Each side's relays pay it every step: the first standing relay in the vehicle list its income, the
        /// second the smaller second share, any more nothing; a relay hit within its quiet time pays nothing (its
        /// crew is under fire). A relay is never raised on an outpost (see BaseSystem).
        /// </summary>
        private void StepRelays()
        {
            var now = _world.Time;
            foreach (var economy in _teams.Values)
            {
                var pay = 0f;
                var counted = 0;
                // Prompt 32 L7: Showdown's minute 6: the CP relays stop paying.
                if (_world.RelaysOff)
                {
                    economy.Relay = 0f;
                    continue;
                }
                foreach (var v in _world.VehicleList)
                {
                    if (counted >= RelayDef.MaxPerBase) break;
                    if (!v.IsAlive || v.Team != economy.Team || v.Def.Relay is not { } relay) continue;
                    counted++;
                    if (now - v.LastHitTime < relay.Quiet) continue;
                    pay += counted == 1 ? relay.Income : relay.Second;
                }
                economy.Relay = pay;
            }
        }

        /// <summary>What a side's relays pay a second now (0: none, or all under fire).</summary>
        public float RelayIncome(int team) => _teams.TryGetValue(team, out var e) ? e.Relay : 0f;
    }
}
