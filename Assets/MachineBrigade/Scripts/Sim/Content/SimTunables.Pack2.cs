#nullable enable
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Balance pack 2 (lane A): the registry of the literals moved out of the code by Tools/export/mbconst (move). Each
    /// domain has its own generated file SimTunables.Pack2.&lt;Domain&gt;.cs (fields + Entry array), so lanes moving
    /// different domains never edit the same file. Same rules as the other entries: the default is the old literal,
    /// tunables.json sets it at catalog load, values never change during a battle.
    /// </summary>
    public static partial class SimTunables
    {
        private static IEnumerable<Entry> Pack2Entries()
        {
            foreach (var e in Pack2Weapons) yield return e;
            foreach (var e in Pack2Vehicles) yield return e;
            foreach (var e in Pack2Bosses) yield return e;
            foreach (var e in Pack2Bases) yield return e;
            foreach (var e in Pack2Modes) yield return e;
            foreach (var e in Pack2Ai) yield return e;
            foreach (var e in Pack2Campaign) yield return e;
            foreach (var e in Pack2Maps) yield return e;
            foreach (var e in AiMasterP0B) yield return e;
            // AI MASTER P0-A (lane A): targeting and the combat watchdog (SimTunables.AiP0A.cs).
            foreach (var e in AiP0AEntries) yield return e;
            // AI MASTER P2 (lane C): role / mode doctrine, fire support, positions, firing lanes, formations, squads.
            foreach (var e in AiMasterP2) yield return e;
            // AI MASTER P0-D + P1 (lane B): jam stages, traffic, corridors (SimTunables.AiMasterP1.cs).
            foreach (var e in AiMasterP1) yield return e;
            // AI MASTER P3 (lane A): coordination: frontline, memory, board, packages, fire missions, pursuit (SimTunables.AiMasterP3.cs).
            foreach (var e in AiMasterP3) yield return e;
            // AI MASTER P4 (lane A): advanced planning: forecast, plans, probe / feint, adaptation, air packages, boss tactics (SimTunables.AiMasterP4.cs).
            foreach (var e in AiMasterP4) yield return e;
            // AI MASTER P5 (lane A): health monitor, ammo-aware tactics, tower coordination, update budget (SimTunables.AiMasterP5.cs).
            foreach (var e in AiMasterP5) yield return e;
            // Map / visual / audio W1-A (lane A): GameplayTopology audits, terrain semantics, weather presentation (SimTunables.MapTopology.cs).
            foreach (var e in MapTopologyW1A) yield return e;
        }
    }
}
