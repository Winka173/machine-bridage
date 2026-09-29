#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// The Inferno's fire trail (prompt 16 E, <see cref="FireTrailDef"/>): as it drives it leaves patches
    /// of burning fuel behind its hull that set enemy ground vehicles in them on fire. A patch burns for
    /// the ground fires' time (a fifth shorter than it is lit for, 12A); the trail stops with its fuel
    /// tanks (the part that carries "trail").
    /// </summary>
    internal sealed partial class BossSystem
    {
        /// <summary>At most this many patches of one boss burn at once (the oldest goes out first).</summary>
        private const int TrailPatches = 12;

        private readonly List<(Vector2 at, double until, float radius, float dps, Vehicle source)> _trails = new();

        private void Trail(Vehicle v, FireTrailDef trail, double now)
        {
            if (v.TrailOff || v.Transforming || v.Burrowed || v.Flying)
            {
                v.TrailFrom = v.Position;
                return;
            }
            if (Vector2.DistanceSquared(v.Position, v.TrailFrom) < trail.Every * trail.Every) return;
            v.TrailFrom = v.Position;
            // Behind the hull, where it has just been.
            var at = _world.ClampToMap(v.Position - SimMath.Forward(v.Heading) * (v.Def.Length * 0.5f + trail.Radius * 0.5f));
            var own = 0;
            var oldest = -1;
            for (var i = 0; i < _trails.Count; i++)
            {
                if (_trails[i].source != v) continue;
                own++;
                if (oldest < 0) oldest = i;
            }
            if (own >= TrailPatches && oldest >= 0) _trails.RemoveAt(oldest);
            _trails.Add((at, now + trail.Burns, trail.Radius, trail.Dps, v));
            _world.Emit(SimEvent.FireTrail(v, at, trail.Seconds, trail.Radius));
        }

        /// <summary>Twice a second: the patches set enemy ground vehicles in them burning, and go out in time.</summary>
        private void StepTrails(double now)
        {
            if (_trails.Count == 0 || _world.Tick % 10 != 5) return;
            for (var i = _trails.Count - 1; i >= 0; i--)
            {
                var (at, until, radius, dps, source) = _trails[i];
                if (now >= until)
                {
                    _trails.RemoveAt(i);
                    continue;
                }
                foreach (var e in _world.VehicleList)
                {
                    if (!e.IsAlive || e.Team == source.Team || e.Team < 0 || e.Flying || e.Def.Boss) continue;
                    var reach = radius + e.Def.HullRadius;
                    if (Vector2.DistanceSquared(e.Position, at) > reach * reach) continue;
                    // A second of fire, renewed while it stands in the patch.
                    _world.Status.Burn(e, dps, 1.2f, source.Team, source.Id);
                }
            }
        }
    }
}
