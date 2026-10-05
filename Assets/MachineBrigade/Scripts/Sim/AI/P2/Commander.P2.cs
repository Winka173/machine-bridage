#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P2, the commander's squad management: spec 24's reserve (15-25 % of the combat power where the mode
    /// doctrine allows it; committed to a flank threat / breakthrough, a losing squad or an HQ threat, I16 Endless only to
    /// an HQ emergency, I12 Showdown's final stage cuts it), spec 70's urgency (attack threshold x lerp(1, 0.75, urgency),
    /// never under the tactic's floor), spec 71 / 72's assignment utility (role fit against the objective's demand +
    /// distance fit + current-task compatibility + domain access - reassignment cost) and spec 73's commitment (a squad's
    /// task changes inside its commit window only for an emergency, an invalid task or a phase change).
    /// </summary>
    public sealed partial class AiCommander
    {
        private float _urgency;
        private int _assignGeneration = -1;
        private readonly Dictionary<int, double> _reserveCommitted = new();
        private readonly Dictionary<int, (TaskKind kind, double since)> _taskSince = new();
        private readonly List<Squad> _order = new();

        /// <summary>Spec 70: the objective urgency now (0-1).</summary>
        public float Urgency => _urgency;

        /// <summary>
        /// Own/enemy strength for an attack: the tactic's (else the parameter), lowered by "use it or lose it" (I.4) where the
        /// profile has advancePressure, and by spec 70's urgency: x lerp(1, 0.75, urgency), never under the tactic's own
        /// threshold x 0.75.
        /// </summary>
        public float AttackThreshold(Squad? s)
        {
            var t = AttackThresholdBase(s);
            if (_urgency <= 0f || _world == null) return t;
            var floor = Tun.ModeDoctrine.UrgencyFloor;
            var tactic = (s != null ? TacticFor(s) : CurrentTactic).Modules.AttackThreshold ?? _world.Catalog.Ai.AttackThreshold;
            return MathF.Max(tactic * floor, t * (1f + (floor - 1f) * Math.Clamp(_urgency, 0f, 1f)));
        }

        /// <summary>Spec 70: time near the end, an objective bleeding, the HQ threatened, a boss phase that asks for pressure.</summary>
        private void UpdateUrgency(SimWorld world, TeamIntel intel)
        {
            var u = 0f;
            if (world.TryGetRally(Team, out var home))
                foreach (var e in intel.Events)
                    if (e.Kind is IntelEventKind.Threat or IntelEventKind.ObjectivePressure && e.Priority >= 60f && Vector2.Distance(e.Centre, home) < 50f) u = MathF.Max(u, 1f);
            if (world.Intel.Objectives is { } objectives)
            {
                var lost = 0;
                foreach (var p in objectives.Points)
                    if (p.Owner == EnemyTeam) lost++;
                if (objectives.Points.Count > 0) u = MathF.Max(u, 0.5f * lost / objectives.Points.Count);
            }
            if (world.Intel.Objectives is Modes.ShowdownMode showdown)
            {
                var left = showdown.SecondsLeft(world);
                if (left < Tun.ModeDoctrine.UrgencyEndSeconds) u = MathF.Max(u, 1f - left / MathF.Max(1f, Tun.ModeDoctrine.UrgencyEndSeconds));
            }
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Def.Boss && v.Team == EnemyTeam && v.Phase >= 2) u = MathF.Max(u, 0.5f);
            _urgency = Math.Clamp(u, 0f, 1f);
        }

        /// <summary>B.2 squads to tasks with the P2 reserve and the assignment utility.</summary>
        private void AssignP2(SimWorld world, TeamIntel intel)
        {
            var squads = Squads.Squads;
            if (squads.Count == 0) return;
            var now = world.Time;
            var m = CurrentTactic.Modules;
            var total = 0f;
            foreach (var s in squads) total += s.Strength;
            var share = MainEffort(world);
            var target = Intent.PrimaryObjective;
            var home = world.TryGetRally(Team, out var rally) ? rally : (Vector2?)null;
            var doctrine = world.Doctrine;
            var gen = doctrine.Generation;
            // Spec 73: a phase change frees every commitment (I11: nothing stale carried over).
            var phaseChanged = gen != _assignGeneration;
            _assignGeneration = gen;
            if (phaseChanged) _taskSince.Clear();
            // Spec 73: an emergency of severity High (a threat event of priority 90+, as the plan's own rule) frees commitments.
            var emergency = false;
            foreach (var e in intel.Events)
                if (e.Kind == IntelEventKind.Threat && e.Priority >= 90f) emergency = true;

            // Spec 24: the reserve.
            var reserve = PickReserve(world, intel, squads, total, home, target);
            var reservePoint = home.HasValue && target.HasValue ? ReserveSpot(world, home.Value, target.Value) : home;
            var trigger = ReserveTrigger(world, intel, home);

            // Spec 72: assignment utility for the primary effort (stable order; reassignment costs).
            var to = target ?? (EnemyCentre(intel) ?? Vector2.Zero);
            _order.Clear();
            foreach (var s in squads)
                if (!reserve.Contains(s)) _order.Add(s);
            var demand = Demand(intel, to);
            var utility = new Dictionary<int, float>();
            foreach (var s in _order) utility[s.Id] = AssignmentScore(world, s, to, demand, emergency || phaseChanged, now);
            _order.Sort((a, b) =>
            {
                var c = utility[b.Id].CompareTo(utility[a.Id]);
                return c != 0 ? c : a.Id.CompareTo(b.Id);
            });
            var assigned = 0f;
            var pincer = 0;
            foreach (var s in _order)
            {
                var primary = assigned < total * share || Intent.SecondaryObjective == null || m.Together;
                SquadTask task;
                if (m.HoldBase && home.HasValue) task = new SquadTask { Kind = TaskKind.Secondary, Objective = home, Hold = true };
                else if (primary)
                {
                    task = new SquadTask { Kind = TaskKind.Primary, Objective = target, Window = Intent.AttackWindow, Hold = Defending || m.Hold };
                    if (m.Pincer && pincer < 3) task.FlankSide = pincer++ % 2 == 0 ? -1 : 1;
                    assigned += s.Strength;
                }
                else task = new SquadTask { Kind = TaskKind.Secondary, Objective = Intent.SecondaryObjective, Hold = true, Window = false };
                SetTask(s, task, now);
            }
            foreach (var s in reserve)
            {
                // A committed reserve keeps its new task for the commit window (spec 73).
                if (_reserveCommitted.TryGetValue(s.Id, out var until) && now < until) continue;
                if (trigger is { } at)
                {
                    _reserveCommitted[s.Id] = now + Tun.ModeDoctrine.ReserveCommitSeconds;
                    SetTask(s, new SquadTask { Kind = TaskKind.Secondary, Objective = at, Window = true, Hold = false }, now);
                    s.ActionSince = double.NegativeInfinity;
                    P2Reasons.Commander(world, Team, DecisionKind.Plan, P2Reasons.ModeReserveCommit, $"squad {s.Id} -> ({at.X:0},{at.Y:0})");
                    trigger = null; // one reserve squad per trigger and look
                    continue;
                }
                if (s.Task.Kind != TaskKind.Reserve)
                    P2Reasons.Commander(world, Team, DecisionKind.Plan, P2Reasons.ModeReserveHold, $"squad {s.Id}");
                SetTask(s, new SquadTask { Kind = TaskKind.Reserve, Objective = reservePoint, Hold = true }, now);
            }
            if (_reserveCommitted.Count > 32) _reserveCommitted.Clear();
        }

        private void SetTask(Squad s, SquadTask task, double now)
        {
            if (!_taskSince.TryGetValue(s.Id, out var held) || held.kind != task.Kind) _taskSince[s.Id] = (task.Kind, now);
            s.Task = task;
        }

        /// <summary>
        /// Spec 24: squads held back so their strength is within the doctrine's reserve share (15-25 %; none where the mode does
        /// not allow one; never the only squad). Fast squads first where the doctrine asks a fast response package (I3), then the
        /// ones nearest home. Committed reserves keep counting as reserve until their commit window ends.
        /// </summary>
        private List<Squad> PickReserve(SimWorld world, TeamIntel intel, IReadOnlyList<Squad> squads, float total, Vector2? home, Vector2? target)
        {
            var list = new List<Squad>();
            var (min, max) = world.Doctrine.ReserveShareOf(Team);
            if (max <= 0f || squads.Count < 2 || total <= 0f || !home.HasValue || CurrentTactic.Modules.HoldBase) return list;
            var d = world.Doctrine.For(Team);
            var candidates = new List<Squad>();
            foreach (var s in squads)
                if (s.MemberList.Count > 0 && s.State != SquadState.Combat) candidates.Add(s);
            var h = home.Value;
            candidates.Sort((a, b) =>
            {
                // Keep the current reserve first (no churn), then fast ones if asked, then nearest home.
                var ra = a.IsReserve || _reserveCommitted.ContainsKey(a.Id) ? 0 : 1;
                var rb = b.IsReserve || _reserveCommitted.ContainsKey(b.Id) ? 0 : 1;
                if (ra != rb) return ra.CompareTo(rb);
                if (d.FastReserve && a.Fast != b.Fast) return a.Fast ? -1 : 1;
                var c = Vector2.DistanceSquared(a.Centre, h).CompareTo(Vector2.DistanceSquared(b.Centre, h));
                return c != 0 ? c : a.Id.CompareTo(b.Id);
            });
            var held = 0f;
            foreach (var s in candidates)
            {
                if (list.Count >= squads.Count - 1 || held >= min * total) break;
                if (held + s.Strength > max * total) continue;
                list.Add(s);
                held += s.Strength;
            }
            return list;
        }

        /// <summary>The reserve's place: a third of the way from home to the main objective, on open ground off the routes.</summary>
        private static Vector2 ReserveSpot(SimWorld world, Vector2 home, Vector2 target)
        {
            var p = world.Map.Clamp(Vector2.Lerp(home, target, 0.35f), 8f);
            return world.Lanes.OffLane(p, 12f);
        }

        /// <summary>
        /// Spec 24: what a reserve is for: a high threat / breakthrough near home or a friendly squad (a flank to patch), a
        /// squad losing clearly, an HQ threat. Endless (I16): only an HQ / base emergency.
        /// </summary>
        private Vector2? ReserveTrigger(SimWorld world, TeamIntel intel, Vector2? home)
        {
            var d = world.Doctrine.For(Team);
            foreach (var e in intel.Events)
            {
                if (e.Kind != IntelEventKind.Threat || e.Priority < 70f || e.Confidence < 0.5f) continue;
                if (home is { } h && Vector2.Distance(e.Centre, h) < 60f) return e.Centre;
                if (d.ReserveEmergencyOnly) continue;
                foreach (var s in Squads.Squads)
                    if (!s.IsReserve && Vector2.Distance(s.Centre, e.Centre) < 50f) return e.Centre;
            }
            if (d.ReserveEmergencyOnly) return null;
            foreach (var s in Squads.Squads)
            {
                if (s.IsReserve || s.State != SquadState.Combat) continue;
                var (own, enemy) = intel.StrengthAround(s.Centre, MathF.Max(40f, s.Reach));
                if (enemy > 0f && own / enemy < 0.6f) return s.Centre;
            }
            return null;
        }

        /// <summary>Spec 71: the objective's demand: anti-air when enemy aircraft are near it, anti-tank against armour, recon in the unknown.</summary>
        private static (float aa, float at, float recon) Demand(TeamIntel intel, Vector2 at)
        {
            float air = 0f, armour = 0f, all = 0f;
            foreach (var c in intel.Contacts)
            {
                if (Vector2.Distance(c.Position, at) > 80f) continue;
                all += c.Strength;
                if (c.Flying) air += c.Strength;
                else if (c.Group == ForceGroup.Armour) armour += c.Strength;
            }
            if (all <= 0f) return (0f, 0f, 1f);
            return (air / all, armour / all, 0f);
        }

        /// <summary>
        /// Spec 72: RoleFit + DistanceFit + CurrentTaskCompatibility + DomainAccess - ReassignmentCost. Spec 73: inside the
        /// task's commit window a change costs the full reassignment cost unless an emergency or a phase change.
        /// </summary>
        private float AssignmentScore(SimWorld world, Squad s, Vector2 to, (float aa, float at, float recon) demand, bool free, double now)
        {
            float aa = 0f, at = 0f, recon = 0f;
            foreach (var id in s.MemberList)
            {
                if (!world.TryGetVehicle(id, out var v)) continue;
                var role = CombatRoleDoctrine.BaseRole(world, v);
                if (role == DoctrineRole.AntiAir) aa = 1f;
                if (role is DoctrineRole.TankDestroyer or DoctrineRole.MainBattle) at = 1f;
                if (role == DoctrineRole.Recon) recon = 1f;
            }
            var roleFit = (aa * demand.aa + at * demand.at + recon * demand.recon) * 10f;
            var distanceFit = 10f * (1f - Math.Clamp(Vector2.Distance(s.Centre, to) / 300f, 0f, 1f));
            var current = s.Task.Kind == TaskKind.Primary ? 5f : 0f;
            var topology = world.Topology;
            var domain = 0f;
            if (s.MemberList.Count > 0 && world.TryGetVehicle(s.MemberList[0], out var lead) && MapTopology.DomainOf(lead.Def) == MobilityDomain.Ground)
            {
                var goal = topology.Ground.ComponentAt(to);
                if (goal > 0 && topology.Ground.ComponentAt(s.Centre) != goal) domain = -20f;
            }
            var cost = 0f;
            if (s.Task.Kind != TaskKind.Primary && !free && _taskSince.TryGetValue(s.Id, out var held) &&
                now - held.since < world.Catalog.Ai.MinCommit) cost = Tun.Squads.ReassignmentCost;
            return roleFit + distanceFit + current + domain - cost;
        }
    }
}
