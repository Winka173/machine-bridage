#nullable enable
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Movement;

namespace MachineBrigade.Sim
{
    public sealed partial class SimWorld
    {
        private TrafficCoordinator? _traffic;
        private readonly List<Vector2> _corridorBuffer = new();

        /// <summary>
        /// AI MASTER spec 30 (lane P1): the TrafficCoordinator: passages and their reservations, spawn exits, boss corridors,
        /// parking rules, dynamic path costs, shared squad corridors and the traffic counters.
        /// </summary>
        public TrafficCoordinator Traffic => _traffic ??= new TrafficCoordinator(this);

        /// <summary>SEVERE_UNSTUCK: relocations by the last movement fail-safe this battle (the lead reads it; 0 is the goal).</summary>
        public int SevereUnstuckCount => _traffic?.Stats.SevereUnstuck ?? 0;

        /// <summary>
        /// Spec 28: gives a ground vehicle a move order to <paramref name="slot"/> along a shared squad corridor, without a
        /// route search of its own. False (nothing changed) when it cannot join or leave the corridor in plain line: the
        /// caller sends the ordinary command.
        /// </summary>
        internal bool IssueAlongCorridor(Vehicle v, OrderKind kind, Vector2 slot, SquadCorridor corridor)
        {
            if (!v.IsAlive || v.Flying || v.Def.Static || v.Def.Naval != null || v.OnRail || v.ManualOrder) return false;
            if (v.Team == 0 && PlayArea is { } area) slot = area.Clamp(slot);
            slot = Rails.OffRail(v, slot);
            if (!Map.Contains(slot) || !Grid.IsWalkable(slot)) return false;
            if (!Traffic.Corridors.Compose(corridor, v.Position, slot, _corridorBuffer)) return false;
            v.SetOrder(new Order(kind, slot, Core.EntityId.None));
            v.RepathTimer = 0.5f;
            v.SetPath(_corridorBuffer, slot);
            v.Traffic.CorridorId = corridor.Id;
            Traffic.Stats.CorridorRoutes++;
            return true;
        }
    }
}
