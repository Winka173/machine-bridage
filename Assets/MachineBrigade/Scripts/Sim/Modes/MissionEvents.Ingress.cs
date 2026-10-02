#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// Prompt 33 L2, the ingress contract for the scripted reinforcements: a group that drives in (over an edge, at a rail
    /// head, off the water, behind the allies' area) comes through its spawn point's entry gate. The first row (four abreast,
    /// 5 m apart) is created at the gate on the tick the event happens; every further row RowGap seconds after the one before
    /// it, at the gate again (never stacked outside the play area). Each vehicle exists only from its own entry tick. The
    /// view is told ahead (<see cref="SimEventKind.Ingress"/>): at the warning for the first rows (their stand-ins set off then),
    /// as the event happens for the later ones. Nothing the view does reaches back: the ticks are the simulation's.
    /// </summary>
    public sealed partial class MissionEventSystem
    {
        /// <summary>Seconds between two rows through a gate (20 ticks).</summary>
        public const double RowGap = 1.0;

        /// <summary>Half a tick: a row's due time sits half a tick early, so float sums never push it to the next tick.</summary>
        private const double HalfTick = 0.025;

        /// <summary>Whether reinforcements of a spawn point's kind drive in through its gate (the others drop, land or fly).</summary>
        internal static bool DrivesIn(SpawnKind kind) => kind is SpawnKind.Edge or SpawnKind.Rail or SpawnKind.Sea or SpawnKind.Behind;

        /// <summary>The <paramref name="index"/>th vehicle's spot at a gate: its place in a row of four across the way in.</summary>
        private static Vector2 GateSpot(SimWorld world, Vector2 gate, Vector2 inward, int index)
        {
            var across = new Vector2(-inward.Y, inward.X);
            return world.ClampToMap(gate + across * ((index % 4) - 1.5f) * 5f);
        }

        /// <summary>A later row: it comes through the gate <paramref name="row"/> x <see cref="RowGap"/> seconds from now.</summary>
        private void Enter(SimWorld world, EventState s, string defId, int team, Vector2 spot, Vector2 inward, bool ally, int row)
        {
            var seconds = row * RowGap;
            _drops.Add((world.Time + seconds - HalfTick, defId, team, spot, inward, s.Index, ally));
            world.Emit(SimEvent.Ingress(team, defId, spot, inward, (float)seconds, IngressLength(world, spot, inward)));
        }

        /// <summary>The view's approach to a spot: its gate's, else straight back out over the edge (as EntryGate.At).</summary>
        private static float IngressLength(SimWorld world, Vector2 spot, Vector2 inward)
        {
            foreach (var g in world.Map.EntryGates)
                if (Vector2.DistanceSquared(g.Position, spot) < 12f * 12f) return g.VisualIngressLength;
            return EntryGate.At(world.Map, "", EntryGateKind.Edge, spot, inward).VisualIngressLength;
        }

        /// <summary>
        /// At a wave's warning: the first row of each group that drives in is announced to the view, due at the event's start
        /// (<paramref name="lead"/> seconds). Reads the plan only (no random draw, no state changed). If the event has to wait
        /// (the player stands on the point) or takes a spot beside it, the stand-ins reach the gate and are gone; the real
        /// vehicles come in where and when the event does.
        /// </summary>
        private void AnnounceIngress(SimWorld world, EventState s, float lead)
        {
            if (s.Plan is not WavePlan plan) return;
            var team = s.Def.Kind == MissionEventKind.AllyWave ? Player : Enemy;
            foreach (var g in plan.Groups)
            {
                if (!DrivesIn(g.Kind) || g.Pods) continue;
                var gate = g.Point.Gate;
                var at = gate?.Position ?? g.Point.Position;
                var inward = g.Point.Inward;
                for (var i = 0; i < g.Units.Count && i < 4; i++)
                {
                    if (!world.Catalog.Vehicles.TryGetValue(g.Units[i], out var def) || def.Flying) continue;
                    var spot = GateSpot(world, at, inward, i);
                    world.Emit(SimEvent.Ingress(team, g.Units[i], spot, inward, lead, gate?.VisualIngressLength ?? IngressLength(world, spot, inward)));
                }
            }
        }
    }
}
