#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// Prompt 25 F2 batch A (DECISIONS 25F2-A): when the commander (the enemy's, and the player's Auto-buy) buys the new
    /// cards, and where it drops an airborne vehicle.
    /// </summary>
    public sealed partial class ConquestAi
    {
        private float P25CardScore(VehicleDef def, bool owned, Mix enemy, int neutral)
        {
            var score = 0f;
            // The drone killers (the microwave, the interceptor drones): worth it against drones, dead weight without them.
            if (def.Microwave != null || def.DroneHunt != null)
            {
                var drones = 0;
                foreach (var e in _tactics.KnownEnemies)
                    if (e.IsAlive && (e.Def.Drone || Catalog.FliesDrones(e.Def))) drones++;
                score += drones > 0 ? MathF.Min(global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreDronesCap, drones * global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreDronesScale) - global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreMinSub : global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreDronesFalse;
            }
            // Fibre-optic drones against a jamming enemy; the radar-guided missiles against one that hides in smoke.
            foreach (var m in def.Mounts)
                if (m.Weapon.JamProof)
                {
                    score += enemy.Jammers > 0f ? MathF.Min(global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreJammersCap, enemy.Jammers / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreTotalFloor, enemy.Total) * global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreJammersScale + global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreJammersAdd) : 0f;
                    break;
                }
            if (def.SmokeSight && enemy.Smoke > 0f) score += MathF.Min(global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreSmokeCap, enemy.Smoke / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreTotalFloor, enemy.Total) * global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreSmokeScale + global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreSmokeAdd);
            // One reconnaissance pass at a time, when the enemy is out of sight.
            if (def.ReconPass != null) score += owned ? global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreOwnedTrue : _tactics.KnownEnemies.Count < global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreCountMax ? global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreCountTrue : global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.P25CardScoreCountFalse;
            // An airborne vehicle is best dropped on a point to take.
            if (def.Paradrop != null && neutral > 0) score += 0.4f;
            return score;
        }

        /// <summary>
        /// Buys a card: an airborne vehicle is dropped by parachute on the nearest point its side does not hold that it
        /// sees (outside the enemy's base), a little short of it on its own side; everything else (and a drop with nowhere
        /// to go) comes to the drop zone.
        /// </summary>
        private void DeployOrDrop(SimWorld world, string id)
        {
            if (world.Catalog.Vehicles.TryGetValue(id, out var def) && def.Paradrop is { } drop && _mode != null && world.TryGetRally(_team, out var home))
            {
                Vector2? best = null;
                var bestD2 = float.MaxValue;
                foreach (var p in _mode.Points)
                {
                    if (p.Owner == _team) continue;
                    var toHome = home - p.Def.Position;
                    var at = toHome.LengthSquared() > 1f ? p.Def.Position + Vector2.Normalize(toHome) * global::MachineBrigade.Sim.Content.SimTunables.Ai.ConquestAi.DeployOrDropNormalizeScale : p.Def.Position;
                    if (!world.Works.SeenBy(_team, at) || world.Works.NearEnemyBase(_team, at, drop.BaseKeepOut)) continue;
                    var d2 = Vector2.DistanceSquared(home, at);
                    if (d2 >= bestD2) continue;
                    best = at;
                    bestD2 = d2;
                }
                if (best is { } point && world.Submit(Command.Paradrop(_team, id, point)).Accepted) return;
            }
            world.Submit(Command.Deploy(_team, id));
        }
    }
}
