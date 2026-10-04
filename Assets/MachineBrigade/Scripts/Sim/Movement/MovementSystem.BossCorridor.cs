#nullable enable
using System;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// AI MASTER P0-C (spec 33, 63): a moving ground boss reserves its corridor ahead (half its width + 2.5 m either side,
    /// 25-35 m long; <see cref="Bosses.BossBrains.Corridors"/>). Every few steps its friends standing in it (parked, free to be
    /// asked: the same rule as any request to make way) step aside off its way through the ordinary yield, and take up their
    /// order again after. Movers are not stopped (the boss has the right of way over its side, as before), so a jeep never
    /// stands in front of a boss's bow making it turn or stop. The P1 traffic lane builds its corridor rules on the same list.
    /// </summary>
    internal sealed partial class MovementSystem
    {
        private void ClearBossCorridors()
        {
            var corridors = _world.Bosses.Brains.Corridors;
            if (corridors.Count == 0 || _world.Tick % Math.Max(1, Content.SimTunables.Bosses.BossBrain.CorridorTicks) != 0) return;
            foreach (var c in corridors)
            {
                if (!_world.TryGetVehicle(c.Boss, out var boss) || !boss.IsAlive) continue;
                var dir = c.Direction;
                foreach (var o in _world.VehicleList)
                {
                    if (!o.IsAlive || o == boss || o.Team != c.Team || o.Flying || o.Def.Static || o.Def.Boss || o.Def.Naval != null || o.OnRail) continue;
                    if (!c.Holds(o.Position, o.Def.HullRadius) || !Askable(o) || o.Traffic.YieldingTo.IsValid) continue;
                    if (!TryYieldSpot(o, boss, dir, MaxYieldDepth, out var spot)) continue;
                    StartYield(o, boss, dir, spot);
                    _world.Bosses.Brains.CorridorYields++;
                }
            }
        }
    }
}
