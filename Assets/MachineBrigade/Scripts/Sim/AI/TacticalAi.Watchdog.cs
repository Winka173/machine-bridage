#nullable enable
using System.Collections.Generic;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P0-A (Part C): the tactical AI's side of the combat watchdog. It marks its side as AI-controlled, gives the
    /// explicit reasons it holds units for (an objective hold, the fall-back regroup, reinforcements gathering, a gun waiting
    /// for a fire mission: Part C2's OBJECTIVE_HOLD / WAITING_FORMATION / WAITING_FIRE_MISSION), and carries out the
    /// watchdog's requests (C1 step 5/7: a sidestep for a stalled shooter; C2: a push for an unexplained idle unit).
    /// </summary>
    public sealed partial class TacticalAi
    {
        private readonly List<WatchdogRequest> _watchdog = new();

        /// <summary>How long a reason given at one decision lasts: past the next decision.</summary>
        private static float ExplainSpan => DecisionInterval * 2f + 0.5f;

        /// <summary>First thing of a decision: this side is the AI's; the watchdog's requests are carried out.</summary>
        private void ServeWatchdog(SimWorld world)
        {
            var watch = world.CombatWatch;
            watch.MarkAiTeam(_team);
            _watchdog.Clear();
            watch.TakeRequests(_team, _watchdog);
            foreach (var r in _watchdog)
            {
                if (!world.TryGetVehicle(r.Unit, out var v) || !v.IsAlive || v.UnderPlayerControl(world.Time)) continue;
                Issue(world, r.Kind == WatchdogRequestKind.Sidestep ? CommandType.Move : CommandType.AttackMove, v.Id, Clamp(world, r.Point));
                _idleSince.Remove(v.Id);
            }
        }

        /// <summary>The line and fast vehicles stand for <paramref name="reason"/> (a held point, the fall-back regroup).</summary>
        private void ExplainLine(SimWorld world, CombatIdleReason reason)
        {
            foreach (var v in _line) world.CombatWatch.Explain(v.Id, reason, ExplainSpan);
            foreach (var v in _fast) world.CombatWatch.Explain(v.Id, reason, ExplainSpan);
        }

        /// <summary>Last thing of a decision: reinforcements gathering wait for their group; idle guns wait for a fire mission.</summary>
        private void ExplainWaits(SimWorld world)
        {
            foreach (var v in _joining) world.CombatWatch.Explain(v.Id, CombatIdleReason.WaitingFormation, ExplainSpan);
            foreach (var a in _artillery)
                if (!a.Target.IsValid && a.Order.Kind == OrderKind.Idle) world.CombatWatch.Explain(a.Id, CombatIdleReason.WaitingFireMission, ExplainSpan);
        }
    }
}
