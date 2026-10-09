#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    public sealed partial class Squad
    {
        /// <summary>AI MASTER P4 spec 132-133: its part in a probe or a feint (None: neither).</summary>
        public P4Role P4Role { get; internal set; }

        internal float P4PursuitStrength = float.NaN;
    }

    /// <summary>
    /// AI MASTER P4 (lane A), the squads' side of the advanced planning: opportunity-window and lane factors (156, 132), the
    /// route commitment window (184), the probe / feint envelope (132-133: never a suicide), the Part M bait-chase counter,
    /// and the boss telegraph reaction with escape-sector reservation (180-181), learnt patterns (214) and the deterministic
    /// human-like stagger (217). Off with ai.planning.enabled = false.
    /// </summary>
    public sealed partial class SquadLayer
    {
        private TeamPlanning? P4 => _commander.PlanningP4;
        private readonly Dictionary<long, Dictionary<EntityId, Vector2>> _escapePlans = new();

        /// <summary>Adds the P4 factors to the options just scored (after the P3 ones).</summary>
        private void AdjustP4(SimWorld world, TeamIntel intel, Squad s, Vector2 goal)
        {
            var tp = P4;
            if (tp == null || _options.Count == 0) return;
            var now = world.Time;
            // Part M: a squad losing units while it chases marks a bait pattern there (the leash shrinks after repeats).
            if (double.IsNaN(s.PursuitStart)) s.P4PursuitStrength = float.NaN;
            else if (float.IsNaN(s.P4PursuitStrength)) s.P4PursuitStrength = s.Strength;
            else if (s.Strength < s.P4PursuitStrength * 0.75f)
            {
                tp.Adaptation.BaitLoss(s.Centre);
                s.P4PursuitStrength = s.Strength;
                if (tp.Adaptation.BaitCount(s.Centre) == Tun.Adaptation.BaitRepeat)
                    P4Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, P4Reasons.AdaptBait, $"({s.Centre.X:0},{s.Centre.Y:0})");
            }
            var window = tp.WindowNear(goal, OpportunityRoles.Ground | OpportunityRoles.Fast, 20f);
            var routeCommit = CommitmentWindows.Seconds(Tun.Commitment.RouteS, s.Id, global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.AdjustP4Salt);
            for (var i = 0; i < _options.Count; i++)
            {
                var (action, score, factors) = _options[i];
                var before = factors.Count;
                switch (action)
                {
                    case SquadAction.Attack:
                        if (window != null) factors.Add(new Factor("window", Tun.Opportunity.AttackPoints * window.Confidence));
                        if (s.P4Role != P4Role.None) factors.Add(new Factor(s.P4Role == P4Role.Probe ? "probe" : "feint", 10f));
                        break;
                    case SquadAction.FlankLeft:
                    case SquadAction.FlankRight:
                    {
                        var side = action == SquadAction.FlankLeft ? -1 : 1;
                        switch (tp.Lane(TeamPlanning.LaneKey(goal, side), now))
                        {
                            case LaneState.Blocked: factors.Add(new Factor("laneBlocked", -50f)); break;
                            case LaneState.Hot: factors.Add(new Factor("laneHot", -10f)); break;
                            case LaneState.Exploit: factors.Add(new Factor("laneExploit", 10f)); break;
                        }
                        // Spec 184: a squad route (flank side) is kept 4-6 s (emergencies are handled before scoring).
                        if (s.Action == action && CommitmentWindows.Holds(s.ActionSince, now, routeCommit, false)) factors.Add(new Factor("routeCommit", global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.AdjustP4Points4));
                        break;
                    }
                }
                if (factors.Count == before) continue;
                for (var k = before; k < factors.Count; k++) score += factors[k].Points;
                _options[i] = (action, Math.Clamp(score, 0f, global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.AdjustP4ScoreMax), factors);
            }
        }

        /// <summary>Spec 132-133: a probe / feint never closes past its envelope of the nearest known enemy (it keeps its way back).</summary>
        private Vector2 EnvelopeP4(SimWorld world, TeamIntel intel, Squad s, Vector2 goal)
        {
            if (P4 == null || s.P4Role == P4Role.None) return goal;
            var now = world.Time;
            Vector2? nearest = null;
            var best = float.MaxValue;
            foreach (var c in intel.Contacts)
            {
                if (c.Flying || c.Age(now) > global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.EnvelopeP4AgeMin) continue;
                var d = Vector2.Distance(c.Position, goal);
                if (d < best)
                {
                    best = d;
                    nearest = c.Position;
                }
            }
            var kept = ProbeRules.EnvelopeGoal(s.Centre, nearest, goal, MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.EnvelopeP4ReachFloor, s.Reach));
            return world.Grid.IsWalkable(kept) ? kept : goal;
        }

        private static long WarningKey((int, int) key) => ((long)key.Item1 << 32) ^ (uint)key.Item2;

        /// <summary>Spec 217: a member's reaction waits its own deterministic 150-400 ms on top of the skill's delay.</summary>
        private bool StaggerWaitP4(EntityId id, (int, int) key, double seen, double now, float delay) =>
            P4 != null && now - seen < delay + HumanStagger.Delay(id.Value, (int)(WarningKey(key) & 0x7fffffff));

        /// <summary>
        /// Spec 180-181 / 214: the exit of a member inside a telegraphed ring: 3-5 sectors by difficulty (quality only), blocked
        /// ones dropped (off the map, unwalkable, inside another warning), members spread over them with a capacity (never one
        /// point), a learnt pattern's follow-up sectors cost more (Hard and up). Planned once per squad and warning. Null: the
        /// old radial way out.
        /// </summary>
        private Vector2? EscapeExitP4(SimWorld world, TeamIntel intel, Squad s, WarningZone w, (int, int) key, EntityId id)
        {
            var tp = P4;
            if (tp == null) return null;
            var plan = WarningKey(key) * global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.EscapeExitP4WarningKeyScale + s.Id;
            if (!_escapePlans.TryGetValue(plan, out var exits))
            {
                if (_escapePlans.Count > 64) _escapePlans.Clear();
                exits = new Dictionary<EntityId, Vector2>();
                _escapePlans[plan] = exits;
                var ids = new List<EntityId>();
                var spots = new List<Vector2>();
                var sorted = new List<EntityId>(s.MemberList);
                sorted.Sort((a, b) => a.Value.CompareTo(b.Value));
                foreach (var m in sorted)
                    if (world.TryGetVehicle(m, out var v) && Vector2.Distance(v.Position, w.Centre) <= w.Radius + v.Radius + global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.EscapeExitP4RadiusAdd)
                    {
                        ids.Add(m);
                        spots.Add(v.Position);
                    }
                if (ids.Count == 0) return null;
                var level = _commander.Level;
                var sectors = DifficultyGate.Sectors(level);
                var axis = w.Centre - w.Origin;
                var now = world.Time;
                bool Blocked(Vector2 p)
                {
                    if (Vector2.DistanceSquared(world.Map.Clamp(p, global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.EscapeExitP4Margin), p) > global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.EscapeExitP4DistanceSquaredMin || !world.Grid.IsWalkable(p)) return true;
                    foreach (var o in intel.Warnings)
                        if (o.Team != _commander.Team && o.Due >= now && (o.Centre != w.Centre || o.Radius != w.Radius) && Vector2.Distance(o.Centre, p) <= o.Radius + global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.EscapeExitP4RadiusAdd) return true;
                    return false;
                }
                float[]? extra = null;
                if (DifficultyGate.Pattern(level) && w.Source != 0)
                {
                    var sig = PatternMemory.Signature(w.Source, w.Radius);
                    extra = new float[sectors];
                    var a0 = axis.LengthSquared() > 1e-4f ? MathF.Atan2(axis.Y, axis.X) : 0f;
                    var learnt = false;
                    for (var k = 0; k < sectors; k++)
                    {
                        var a = a0 + k * MathF.PI * 2f / sectors;
                        extra[k] = tp.Patterns.Risk(sig, axis, new Vector2(MathF.Cos(a), MathF.Sin(a))) * Tun.BossTactics.PatternCost;
                        learnt |= extra[k] > 0f;
                    }
                    if (learnt) P4Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Emergency, P4Reasons.PatternLearnt, $"boss #{w.Source}");
                }
                var assigned = EscapeSectors.Assign(w.Centre, w.Radius, spots, sectors, axis, Blocked, extra, out var points);
                var used = new HashSet<int>();
                for (var i = 0; i < ids.Count; i++)
                    if (assigned[i] >= 0)
                    {
                        exits[ids[i]] = points[i];
                        used.Add(assigned[i]);
                    }
                if (exits.Count > 0)
                {
                    tp.Metrics.EscapeSectorPlans++;
                    P4Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Emergency, P4Reasons.EscapeSector,
                        $"{ids.Count} in the ring -> {used.Count} of {sectors} sectors");
                    if (used.Count > 1) tp.Cue("escape", w.Centre, s.Id);
                }
            }
            return exits.TryGetValue(id, out var exit) ? exit : null;
        }
    }
}
