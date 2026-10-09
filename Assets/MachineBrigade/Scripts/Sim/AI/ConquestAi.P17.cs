#nullable enable
using System;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Prompt 17 C: when the commander buys the new cards (on top of the prompt 13 scoring every card gets).</summary>
    public sealed partial class ConquestAi
    {
        private float NewCardScore(VehicleDef def, bool owned, int ownManned, int ownTotal, Mix enemy, (int cannon, int machineGun, int antiAir) towers, int neutral)
        {
            var score = 0f;
            // A loyal wingman needs a manned aircraft of ours to fly with (it patrols alone otherwise, which it does poorly).
            if (def.Wingman != null) score += ownManned > 0 ? 1.2f : -4f;
            // A shield carrier pays once there is an army to cover; a second only for a big one.
            if (def.Dome != null && !def.Static) score += ownTotal >= 5 && (!owned || ownTotal >= 12) ? 1.4f : -2f;
            // A bunker vehicle digs in where it is sent: worth most holding ground (defending, or all points taken).
            if (def.Deploy != null && (Stance == CommanderStance.Defend || neutral == 0)) score += 0.8f;
            // The stealth fighter hunts air defences as well as aircraft: the enemy's anti-air makes it worth more
            // (and offsets the "no aircraft to hunt" rule for interceptors).
            if (def.Sead)
                score += MathF.Min(global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.NewCardScoreAntiAirCap, enemy.AntiAir / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.NewCardScoreTotalFloor, enemy.Total) * global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.NewCardScoreAntiAirScale + towers.antiAir * global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.NewCardScoreAntiAirScale2);
            return score;
        }
    }
}
