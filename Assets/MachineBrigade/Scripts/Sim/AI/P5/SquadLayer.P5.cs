#nullable enable
using System.Collections.Generic;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P5 Part L in the squad layer: a member whose meaningful magazine is empty / near empty (or reloading) does not
    /// drive on into an exposed advance: it stops where it is (an in-place magazine only reloads standing still, so this is also
    /// what gets it firing again soonest) and rejoins the squad's goal when reloaded, or at once in an emergency (objective
    /// urgency, overwhelmed, a dodge). Support weapons (artillery, anti-air, support roles) hold while they cannot fire even when
    /// their reload runs on the move. Lines: POSITION_RELOAD_HOLD / POSITION_RELOAD_RESUME.
    /// </summary>
    public sealed partial class SquadLayer
    {
        private readonly Dictionary<EntityId, int> _reloadHeld = new();
        private readonly List<EntityId> _reloadDone = new();

        private void UnitsP5(SimWorld world, Squad s, bool overwhelmed)
        {
            if (!Tun.Ammo.Enabled) return;
            var now = world.Time;
            var urgency = _commander.Urgency;
            var emergency = overwhelmed || s.Dodging;
            var advancing = s.Action is SquadAction.Attack or SquadAction.FlankLeft or SquadAction.FlankRight;
            var health = world.Health.Counters;
            foreach (var id in s.MemberList)
            {
                if (!world.TryGetVehicle(id, out var v) || !v.IsAlive || v.Flying || v.Def.Static) continue;
                var m = AmmoTactics.Read(world, v);
                if (!m.Limited) continue;
                if (_reloadHeld.TryGetValue(id, out var held))
                {
                    if (held != s.Id || !AmmoTactics.Resume(m, urgency, emergency) && advancing) continue;
                    // Reloaded, an emergency, or the squad no longer advancing: back to the squad's move.
                    _reloadHeld.Remove(id);
                    health.ReloadResumes++;
                    // Back to its own formation slot (spec 111: never two hulls sent to one point; the squad's goal is everyone's).
                    if (advancing && !float.IsNaN(s.Goal.X))
                        world.Submit(new Command(CommandType.AttackMove, _commander.Team, new[] { id },
                            UnsharedSlot(world, v, s.LastSlot.TryGetValue(id, out var own) ? own : s.Goal)));
                    P2Reasons.Unit(world, v, DecisionKind.Action, P5Reasons.ReloadResume, $"squad {s.Id} {(emergency ? "emergency" : "reloaded")}");
                    continue;
                }
                var moving = v.IsMoving || v.HasPath;
                var role = CombatRoleDoctrine.RoleOf(world, v);
                var support = role is DoctrineRole.FireSupport or DoctrineRole.AntiAir or DoctrineRole.Support;
                if (!AmmoTactics.HoldBack(m, advancing && moving, support, urgency, emergency)) continue;
                _reloadHeld[id] = s.Id;
                health.ReloadHolds++;
                world.Submit(new Command(CommandType.Stop, _commander.Team, new[] { id }, v.Position));
                P2Reasons.Unit(world, v, DecisionKind.Action, P5Reasons.ReloadHold,
                    $"squad {s.Id} mag={m.Fraction:0.00} reload={m.ReloadLeft:0.0}s{(m.ReloadsOnMove ? " (on the move)" : "")}");
            }
            // Members gone or moved to another squad leave the hold list.
            _reloadDone.Clear();
            foreach (var kv in _reloadHeld)
                if (kv.Value == s.Id && !s.MemberList.Contains(kv.Key)) _reloadDone.Add(kv.Key);
            foreach (var id in _reloadDone) _reloadHeld.Remove(id);
        }

        /// <summary>Whether <paramref name="unit"/> is held for its reload (tests, the debug view).</summary>
        public bool ReloadHeld(EntityId unit) => _reloadHeld.ContainsKey(unit);
    }
}
