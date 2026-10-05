#nullable enable
using System.Collections.Generic;
using System.Numerics;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P2 Part I, the squads' side of the mode doctrine: a Leash / NoChase pursuit policy keeps a squad's goal
    /// within its leash of the doctrine's anchor (the held point, the convoy, the task's objective); the escort profile's
    /// maxAdvanceDistance or the profile's leashDistance wins over ai.modeDoctrine.defendLeash. Logged once per squad change.
    /// </summary>
    public sealed partial class SquadLayer
    {
        private readonly Dictionary<int, bool> _leashed = new();

        private Vector2 Leash(SimWorld world, Squad s, Vector2 goal)
        {
            var d = world.Doctrine.For(_commander.Team);
            if (d.Pursuit == PursuitPolicy.Normal || s.Action is SquadAction.Regroup or SquadAction.Join or SquadAction.Reposition)
            {
                _leashed.Remove(s.Id);
                return goal;
            }
            var profile = world.AiProfile;
            Vector2? anchor = null;
            var leash = profile.LeashDistance > 0f ? profile.LeashDistance : Tun.ModeDoctrine.DefendLeash;
            if (d.Frontline == FrontlinePolicy.ConvoyScreen && world.ConvoySafeZone != null)
            {
                var sum = Vector2.Zero;
                var n = 0;
                foreach (var p in world.ConvoySafeZone())
                {
                    sum += p;
                    n++;
                }
                if (n > 0) anchor = sum / n;
                if (profile.Escort is { } e) leash = e.MaxAdvanceDistance;
            }
            anchor ??= s.Task.Hold || d.Pursuit == PursuitPolicy.NoChase ? s.Task.Objective : null;
            if (anchor is not { } a || Vector2.Distance(a, goal) <= leash)
            {
                _leashed.Remove(s.Id);
                return goal;
            }
            var clamped = a + Direction(a, goal) * leash;
            if (!_leashed.ContainsKey(s.Id))
            {
                _leashed[s.Id] = true;
                P2Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, d.Pursuit == PursuitPolicy.NoChase ? P2Reasons.ModeNoChase : P2Reasons.ModeLeash,
                    $"{d.Id} leash {leash:0} m");
            }
            return world.Grid.IsWalkable(clamped) ? clamped : a;
        }
    }
}
