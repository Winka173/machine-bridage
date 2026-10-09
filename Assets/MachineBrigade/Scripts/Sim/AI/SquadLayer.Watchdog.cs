#nullable enable
namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P0-A (Part C2): a squad's explicit reasons for its members standing without firing: holding or watching
    /// over its ground (OBJECTIVE_HOLD) and regrouping (WAITING_FORMATION). The ambush hold is the members' own AiHoldFire
    /// flag (HOLD_FIRE_AMBUSH). Reasons only: nothing here changes what the squad does.
    /// </summary>
    public sealed partial class SquadLayer
    {
        private void ExplainHolds(SimWorld world)
        {
            var span = Interval * global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.ExplainHoldsIntervalScale + global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.ExplainHoldsIntervalAdd;
            foreach (var s in _squads)
            {
                CombatIdleReason reason;
                if (s.State == SquadState.Regroup || s.Action == SquadAction.Regroup) reason = CombatIdleReason.WaitingFormation;
                else if (s.State is SquadState.Hold or SquadState.Overwatch || s.Action is SquadAction.Hold or SquadAction.Overwatch) reason = CombatIdleReason.ObjectiveHold;
                else continue;
                foreach (var id in s.MemberList) world.CombatWatch.Explain(id, reason, span);
            }
        }
    }
}
