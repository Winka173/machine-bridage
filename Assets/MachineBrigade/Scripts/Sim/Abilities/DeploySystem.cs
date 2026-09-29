#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Abilities
{
    /// <summary>
    /// Prompt 17 C: vehicles that dig in (the bunker vehicle; <see cref="DeployDef"/>). Stepped after the
    /// equipment (which sets each step's speed and reach) and before combat. A vehicle on its tracks that has
    /// stood still for a second with an enemy on the ground within its dug-in reach, or that has stood guard for
    /// four seconds away from its own drop zone (a point, a choke, a siege position the commander sent it to),
    /// digs in: 3 s, no driving, no firing, its moving armour. Dug in: front two levels up (at most 4), reach
    /// x1.3, turret all round. Given a route more than a few metres away (the commander moved it on, the target
    /// moved, the player ordered it), it packs up: 3 s the same way, then drives. A route given while it digs in
    /// turns it back in as long as it had dug. The same rules for both sides; deterministic.
    /// </summary>
    internal sealed class DeploySystem
    {
        /// <summary>Seconds standing still before it digs in with an enemy in reach, and standing guard with none.</summary>
        internal const double StandBefore = 1.0, GuardBefore = 4.0;

        /// <summary>A route ending closer than this is not worth packing up for: it is dropped.</summary>
        internal const float StayWithin = 6f;

        private readonly SimWorld _world;

        public DeploySystem(SimWorld world) => _world = world;

        public void Step()
        {
            var now = _world.Time;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Def.Deploy is not { } dep) continue;
                switch (v.Deploy)
                {
                    case DeployState.Mobile:
                        if (!v.HasPath && !v.PathQueued && !v.IsMoving && Wants(v, dep, now - v.StillSince)) Begin(v, DeployState.Deploying, dep.Seconds, now);
                        break;
                    case DeployState.Deploying:
                        if (Leaving(v)) Begin(v, DeployState.Packing, (float)Math.Max(0.2, now - v.DeployFrom), now);
                        else if (now >= v.DeployUntil) v.Deploy = DeployState.Deployed;
                        break;
                    case DeployState.Deployed:
                        if (Leaving(v)) Begin(v, DeployState.Packing, dep.Seconds, now);
                        break;
                    case DeployState.Packing:
                        if (now >= v.DeployUntil) v.Deploy = DeployState.Mobile;
                        break;
                }
                if (v.Deploy != DeployState.Mobile) v.SpeedGear = 0f;
                if (v.Deploy == DeployState.Deployed) v.RangeFactor *= dep.Range;
            }
        }

        private static void Begin(Vehicle v, DeployState state, float seconds, double now)
        {
            v.Deploy = state;
            v.DeployFrom = now;
            v.DeployUntil = now + seconds;
        }

        /// <summary>It has a route worth leaving for; a short one is dropped (it stays dug in).</summary>
        private static bool Leaving(Vehicle v)
        {
            if (!v.HasPath) return false;
            if (Vector2.Distance(v.Position, v.PathGoal) > StayWithin) return true;
            v.ClearPath();
            return false;
        }

        private bool Wants(Vehicle v, DeployDef dep, double stillFor)
        {
            if (stillFor < StandBefore || v.Stunned) return false;
            var reach = v.Def.Weapon.Range * dep.Range + 4f;
            if (_world.FindNearestEnemy(v, reach, requireVisible: true, layers: TargetLayers.Ground) != null) return true;
            if (v.Order.Kind != OrderKind.Idle || stillFor < GuardBefore) return false;
            // Standing guard, but not at its own drop zone waiting to be sent somewhere.
            return !_world.TryGetRally(v.Team, out var rally) || Vector2.Distance(rally, v.Position) > SimWorld.HomeRadius;
        }
    }
}
