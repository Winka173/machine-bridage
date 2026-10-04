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
        }
    }
}
