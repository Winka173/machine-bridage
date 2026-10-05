#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    public sealed partial class Squad
    {
        /// <summary>AI MASTER P3 spec 125: tactical confidence at the last look (0-1, mechanical; never morale).</summary>
        public float Confidence { get; internal set; } = 0.5f;

        /// <summary>Spec 136: its part in the side's attack package.</summary>
        public PackageRole P3Role { get; internal set; }

        internal double P3StageUntil = double.NegativeInfinity;
        internal Vector2 P3Staging;
        internal bool P3StageLogged;
        internal double PursuitStart = double.NaN, PursuitBlockedUntil = double.NegativeInfinity;
        internal Vector2 PursuitAnchor;
        internal bool PursuitLogged;
        internal float P3RouteStrength;
        internal long P3RouteKey;
        internal SquadAction P3RouteAction = (SquadAction)255;
        internal double DisperseLoggedUntil = double.NegativeInfinity;
        internal float P3FocusShare = 1f;
        internal double P3DeadlineLogAt = double.NegativeInfinity;
    }

    /// <summary>
    /// AI MASTER P3 (lane A), the squads' side of the coordination layer, as factors and small overrides inside the existing
    /// squad loop (Part A: integrate, never rewrite): tactical confidence (125), route diversity with occupancy, congestion,
    /// recent losses, unknown ground and failed routes (127-130, P2 76 traffic-aware flank costs), threat-specific posture
    /// (173), package staging and the fix envelope (134-137), pursuit discipline / interception / cutoff (146-148, 206),
    /// the focus-fire coordinator (199), target handoff (200), stances (149), ambush discipline (205) and anti-artillery
    /// dispersion timing (213). Every rule reads the side's own intel and memory (fog-fair) and is off with
    /// ai.coordination.enabled = false.
    /// </summary>
    public sealed partial class SquadLayer
    {
        private TeamCoordination? P3 => Tun.Coordination.Enabled ? _commander.CoordinationP3 : null;

        // ------------------------------------------------------------------------------------------------ 125 confidence

        /// <summary>Spec 125 / 219 for <paramref name="s"/> against <paramref name="goal"/>.</summary>
        internal float ConfidenceOf(SimWorld world, TeamIntel intel, TeamCoordination tc, Squad s, Vector2 goal)
        {
            var now = world.Time;
            var radius = MathF.Max(Tun.Coordination.LocalRadius, s.Reach);
            var (own, enemy) = intel.StrengthAround(s.Centre, radius);
            var local = TacticalConfidence.NormalizeForceRatio(MathF.Max(own, s.Strength), enemy);
            // Role coverage: anti-tank against the armour, anti-air against the aircraft known round the goal.
            float armour = 0f, air = 0f, all = 0f;
            foreach (var c in intel.Contacts)
            {
                if (Vector2.DistanceSquared(c.Position, goal) > 80f * 80f) continue;
                all += c.Strength;
                if (c.Flying) air += c.Strength;
                else if (c.Group == ForceGroup.Armour) armour += c.Strength;
            }
            bool hasAt = false, hasAa = false;
            foreach (var id in s.MemberList)
            {
                if (!world.TryGetVehicle(id, out var v)) continue;
                var role = CombatRoleDoctrine.BaseRole(world, v);
                if (role is DoctrineRole.TankDestroyer or DoctrineRole.MainBattle) hasAt = true;
                if (role == DoctrineRole.AntiAir || v.Def.Weapon.CanTarget(true)) hasAa = true;
            }
            var roleCoverage = all <= 0f ? 1f : Math.Clamp(1f - armour / all * (hasAt ? 0f : 0.8f) - air / all * (hasAa ? 0f : 1f), 0f, 1f);
            // Support: guns that reach the goal, anti-air and repair close by.
            float support = 0f;
            bool guns = false, aa = false, repair = false;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != _commander.Team || v.Def.Static) continue;
                if (!guns && v.Def.Weapon.MinRange > 0f && Vector2.DistanceSquared(v.Position, goal) <= v.Def.Weapon.Range * v.Def.Weapon.Range) guns = true;
                var near = Vector2.DistanceSquared(v.Position, s.Centre) <= 40f * 40f;
                if (!aa && near && !v.Flying && v.Def.Weapon.CanTarget(true) && !v.Def.Weapon.CanTarget(false)) aa = true;
                if (!repair && near && v.Def.RepairAura != null) repair = true;
            }
            if (guns) support += 0.4f;
            if (aa || air <= 0f) support += 0.3f;
            if (repair) support += 0.3f;
            var position = tc.Frontline.PositionalAdvantage(s.Centre, goal);
            var intelConfidence = (1f - tc.Memory.UnknownShare(intel, goal, 30f, now)) * Confidence(intel, goal, radius, now);
            return TacticalConfidence.Compute(local, roleCoverage, support, position, _commander.Urgency, intelConfidence);
        }

        // ------------------------------------------------------------------------------------------------ 127-130, 173 options

        /// <summary>Adds the P3 factors to the options just scored (called at the end of Score).</summary>
        private void AdjustP3(SimWorld world, TeamIntel intel, Squad s, Vector2 goal)
        {
            var tc = P3;
            if (tc == null || _options.Count == 0) return;
            var now = world.Time;
            var conf = s.Confidence = ConfidenceOf(world, intel, tc, s, goal);
            var m = _commander.TacticFor(s).Modules;
            var pts = Tun.Confidence.Points;
            var urgent = _commander.Urgency >= Tun.Pursuit.UrgencyDrop;
            var unknownModifier = TacticalMemory.UnknownModifier(m);
            var heavy = HeavyShare(world, s) > 0.5f;
            var enemyAir = intel.EnemyComposition[(int)ForceGroup.Helicopter] + intel.EnemyComposition[(int)ForceGroup.Plane] > 0f;
            var umbrella = !enemyAir || OwnAntiAirNear(world, s.Centre, 40f);

            // Route costs of the attack corridors (direct, left, right).
            var costs = new float[_options.Count];
            var minCost = float.MaxValue;
            for (var i = 0; i < _options.Count; i++)
            {
                costs[i] = float.NaN;
                var side = SideOf(_options[i].action);
                if (side == 2) continue;
                Vector2 via;
                if (side == 0) via = Vector2.Lerp(s.Centre, goal, 0.5f);
                else if (!FlankPoint(world, intel, s, goal, side, out via, out _)) continue;
                costs[i] = RouteCostP3(world, intel, tc, s, goal, via, side, unknownModifier);
                minCost = MathF.Min(minCost, costs[i]);
            }
            for (var i = 0; i < _options.Count; i++)
            {
                var (action, score, factors) = _options[i];
                var before = factors.Count;
                if (!float.IsNaN(costs[i]) && costs[i] - minCost > 0.01f) factors.Add(new Factor("route", -(costs[i] - minCost) * Tun.Routes.Points));
                switch (action)
                {
                    case SquadAction.Attack:
                        factors.Add(new Factor("confidence", (conf - 0.5f) * 2f * pts));
                        if (!TacticalConfidence.MayCommit(conf, urgent) && s.Action != SquadAction.Attack) factors.Add(new Factor("noCommit", -2f * pts));
                        if (tc.WindowNear(goal, 20f) != null) factors.Add(new Factor("counterattack", pts));
                        if (heavy && intel.ThreatAt(ThreatKind.AntiTank, Vector2.Lerp(s.Centre, goal, 0.5f)) > 0f) factors.Add(new Factor("atFrontal", -0.5f * pts));
                        if (!umbrella) factors.Add(new Factor("noAaUmbrella", -0.5f * pts));
                        if (s.P3Role is PackageRole.Main or PackageRole.Fix) factors.Add(new Factor("package", 5f));
                        break;
                    case SquadAction.FlankLeft:
                    case SquadAction.FlankRight:
                        if (conf < Tun.Confidence.Cautious) factors.Add(new Factor("lowConfidence", -pts));
                        if (s.P3Role == PackageRole.Flank) factors.Add(new Factor("packageFlank", 15f));
                        if (heavy && intel.ThreatAt(ThreatKind.AntiTank, Vector2.Lerp(s.Centre, goal, 0.5f)) > 0f) factors.Add(new Factor("avoidFrontalAt", 0.3f * pts));
                        if (!umbrella) factors.Add(new Factor("noAaUmbrella", -0.5f * pts));
                        if (FlankPoint(world, intel, s, goal, action == SquadAction.FlankLeft ? -1 : 1, out var fp, out _))
                        {
                            var seg = tc.Frontline.Nearest(fp);
                            if (seg >= 0 && tc.Frontline.Segments[seg].EnemyPressure < tc.Frontline.Segments[seg].FriendlyPressure) factors.Add(new Factor("frontWeak", 5f));
                        }
                        break;
                    case SquadAction.Hold:
                        if (conf < Tun.Confidence.Cautious) factors.Add(new Factor("cautious", (Tun.Confidence.Cautious - conf) / MathF.Max(0.01f, Tun.Confidence.Cautious) * pts));
                        break;
                    case SquadAction.Regroup:
                        if (DisperseHoldP3(world, intel, s)) factors.Add(new Factor("artilleryWindow", -40f));
                        break;
                }
                if (factors.Count == before) continue;
                for (var k = before; k < factors.Count; k++) score += factors[k].Points;
                _options[i] = (action, Math.Clamp(score, 0f, 100f), factors);
            }
            TrackRouteP3(world, tc, s, goal);
        }

        private static int SideOf(SquadAction a) => a switch
        {
            SquadAction.Attack => 0,
            SquadAction.FlankLeft => -1,
            SquadAction.FlankRight => 1,
            _ => 2,
        };

        /// <summary>Spec 127 PathCost of one corridor (centre -> via -> goal).</summary>
        private float RouteCostP3(SimWorld world, TeamIntel intel, TeamCoordination tc, Squad s, Vector2 goal, Vector2 via, int side, float unknownModifier)
        {
            var now = world.Time;
            var distance = side == 0 ? Vector2.Distance(s.Centre, goal) : Vector2.Distance(s.Centre, via) + Vector2.Distance(via, goal);
            var threat = (side == 0 ? RouteThreat(intel, s.Centre, goal) : MathF.Max(RouteThreat(intel, s.Centre, via), RouteThreat(intel, via, goal))) /
                         MathF.Max(1f, s.Strength);
            var congestion = side == 0 ? CongestionAlong(world, intel, s.Centre, goal) : CongestionAlong(world, intel, s.Centre, via) + CongestionAlong(world, intel, via, goal);
            var occupancy = tc.Routes.Occupancy(via, s.Id, now);
            var losses = side == 0 ? tc.Memory.DeathAlong(s.Centre, goal, now) : MathF.Max(tc.Memory.DeathAlong(s.Centre, via, now), tc.Memory.DeathAlong(via, goal, now));
            var unknown = (side == 0 ? tc.Memory.UnknownAlong(intel, s.Centre, goal, now) : tc.Memory.UnknownAlong(intel, s.Centre, via, now)) * unknownModifier;
            var repeat = tc.Memory.RoutePenalty(TacticalMemory.RouteKey(goal, side), now);
            return RouteDiversity.Cost(distance, threat, congestion, occupancy, losses, unknown, repeat);
        }

        /// <summary>
        /// P2 76 / spec 127 Congestion: traffic-aware cost of a way: passages near it with many arrivals or overloaded (P1's
        /// TrafficCoordinator), crowded narrow cells (the World Model's chokepoints).
        /// </summary>
        private float CongestionAlong(SimWorld world, TeamIntel intel, Vector2 from, Vector2 to)
        {
            var cost = 0f;
            if (Tun.Traffic.Enabled)
                foreach (var p in world.Traffic.Passages)
                {
                    if (DistanceToSegment(p.Centre, from, to) > p.Reach + 4f) continue;
                    var arrivals = world.Traffic.ArrivalsAt(p, _commander.Team);
                    cost += MathF.Min(1f, arrivals / MathF.Max(1f, p.Lanes(3f) * 3f));
                }
            foreach (var c in intel.Chokepoints)
                if (DistanceToSegment(intel.CellCentre(c), from, to) <= intel.Cell) cost += 0.2f * MathF.Min(3, intel.Density[c] - 1);
            return MathF.Min(3f, cost);
        }

        private static float DistanceToSegment(Vector2 p, Vector2 a, Vector2 b)
        {
            var ab = b - a;
            var len2 = ab.LengthSquared();
            if (len2 < 1e-4f) return Vector2.Distance(p, a);
            var t = Math.Clamp(Vector2.Dot(p - a, ab) / len2, 0f, 1f);
            return Vector2.Distance(p, a + ab * t);
        }

        /// <summary>Spec 127: books the squad's corridor and marks a route failed when it cost the squad dearly.</summary>
        private void TrackRouteP3(SimWorld world, TeamCoordination tc, Squad s, Vector2 goal)
        {
            var now = world.Time;
            var side = SideOf(s.Action);
            if (side == 2)
            {
                tc.Routes.Unbook(s.Id);
                s.P3RouteAction = (SquadAction)255;
                return;
            }
            var key = TacticalMemory.RouteKey(goal, side);
            if (s.P3RouteAction != s.Action || s.P3RouteKey != key)
            {
                if (tc.Memory.RoutePenalty(key, now) > 0.1f) tc.Metrics.RouteRepeatAfterFailure++;
                s.P3RouteAction = s.Action;
                s.P3RouteKey = key;
                s.P3RouteStrength = s.Strength;
            }
            var via = side == 0 ? Vector2.Lerp(s.Centre, goal, 0.5f) : s.Goal;
            tc.Routes.Book(s.Id, via, now);
            if (s.P3RouteStrength > 0f && s.Strength < s.P3RouteStrength * (1f - Tun.Memory.RouteFailShare))
            {
                tc.Memory.Fail(key, now);
                P3Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, P3Reasons.RouteFailed, $"{s.Action} lost {1f - s.Strength / s.P3RouteStrength:0%}");
                s.P3RouteStrength = s.Strength;
            }
        }

        private static float HeavyShare(SimWorld world, Squad s)
        {
            if (s.MemberList.Count == 0) return 0f;
            var n = 0;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v) && v.Def.Class is UnitClass.Tank or UnitClass.Heavy) n++;
            return n / (float)s.MemberList.Count;
        }

        private bool OwnAntiAirNear(SimWorld world, Vector2 p, float radius)
        {
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == _commander.Team && !v.Flying && v.Def.Weapon.CanTarget(true) && Vector2.DistanceSquared(v.Position, p) <= radius * radius)
                    return true;
            return false;
        }

        // ------------------------------------------------------------------------------------------------ 134-137 staging / fix

        /// <summary>Spec 135 / 137: a package member early for the execute time stands at its staging sub-zone (overwatch), not in the fight.</summary>
        private bool StageP3(SimWorld world, Squad s, ref Vector2 goal, ref CommandType type)
        {
            var tc = P3;
            var now = world.Time;
            if (tc == null || now >= s.P3StageUntil || s.State == SquadState.Combat)
            {
                if (s.P3StageLogged)
                {
                    s.P3StageLogged = false;
                    P3Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, P3Reasons.SyncGo, s.P3Role.ToString());
                }
                return false;
            }
            goal = s.P3Staging;
            type = CommandType.Move;
            foreach (var id in s.MemberList) world.CombatWatch.Explain(id, CombatIdleReason.WaitingFormation, 1.5f);
            if (!s.P3StageLogged)
            {
                s.P3StageLogged = true;
                tc.Metrics.SyncStages++;
                P3Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, P3Reasons.SyncStage,
                    $"{s.P3Role} {s.P3StageUntil - now:0.0} s at ({goal.X:0},{goal.Y:0})");
            }
            return true;
        }

        /// <summary>Spec 134: the Fix squad keeps pressure inside its engagement envelope, never closer.</summary>
        private Vector2 FixP3(SimWorld world, Squad s, Vector2 target, Vector2 goal)
        {
            if (P3 == null || s.P3Role != PackageRole.Fix) return goal;
            var kept = FixAndFlank.FixGoal(s.Centre, target, goal, MathF.Max(10f, s.Reach));
            return world.Grid.IsWalkable(kept) ? kept : goal;
        }

        // ------------------------------------------------------------------------------------------------ 146-148, 206 pursuit

        /// <summary>
        /// Spec 148 / 223 pursuit discipline on a goal that follows an enemy: max seconds, max distance from the task anchor
        /// (shrunk by recent losses round the chase: spec 206 bait resistance), objective relevance under urgency; then spec
        /// 146 interception of a moving target and spec 147 cutoff at a choke for fast squads.
        /// </summary>
        private Vector2 PursuitP3(SimWorld world, TeamIntel intel, Squad s, Vector2 goal, Contact enemy)
        {
            var tc = P3;
            if (tc == null) return goal;
            var now = world.Time;
            var reach = MathF.Max(10f, s.Reach);
            var anchor = double.IsNaN(s.PursuitStart) ? s.Task.Objective ?? s.Centre : s.PursuitAnchor;
            if (now < s.PursuitBlockedUntil)
                return Vector2.Distance(goal, anchor) <= reach ? goal : anchor + Direction(anchor, goal) * reach;
            if (Vector2.Distance(goal, anchor) <= reach && double.IsNaN(s.PursuitStart)) return goal;
            if (double.IsNaN(s.PursuitStart))
            {
                s.PursuitStart = now;
                s.PursuitAnchor = anchor;
                s.PursuitLogged = false;
            }
            var aa = AntiAirSquad(world, s);
            var maxSeconds = aa ? Tun.Pursuit.AaMaxSeconds : Tun.Pursuit.MaxSeconds;
            var maxDistance = PursuitDiscipline.BaitLeash(aa ? Tun.Pursuit.AaMaxDistance : Tun.Pursuit.MaxDistance,
                tc.Memory.DeathDanger(enemy.Position, now));
            var alive = enemy.InSight || enemy.Age(now) < Tun.Pursuit.AgeFadeS;
            var threatens = s.Task.Objective is { } o && Vector2.Distance(enemy.Position, o) <= 30f;
            var verdict = PursuitDiscipline.Check(alive, now, s.PursuitStart, maxSeconds, enemy.Position, s.PursuitAnchor, maxDistance,
                _commander.Urgency, threatens);
            if (verdict != PursuitVerdict.Continue)
            {
                var back = s.PursuitAnchor;
                s.PursuitBlockedUntil = now + Tun.Pursuit.RetrySeconds;
                s.PursuitStart = double.NaN;
                tc.Metrics.PursuitAbortCount++;
                P3Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action,
                    verdict == PursuitVerdict.NotMissionRelevant ? P3Reasons.PursuitIrrelevant : P3Reasons.PursuitAbort,
                    $"{verdict} -> ({back.X:0},{back.Y:0})");
                return back;
            }
            // Spec 146: a moving target out of reach: the intercept point, not its current position.
            if (enemy.Velocity.LengthSquared() > 1f && Vector2.Distance(s.Centre, enemy.Position) > reach)
            {
                var speed = SlowestSpeed(world, s);
                var p = PursuitDiscipline.Intercept(s.Centre, speed, enemy.Position, enemy.Velocity, Tun.Pursuit.HorizonS, enemy.Age(now), out var t);
                if (s.Fast && CutoffP3(world, intel, s, enemy, speed, t, out var choke))
                {
                    if (!s.PursuitLogged)
                    {
                        s.PursuitLogged = true;
                        tc.Metrics.CutoffCount++;
                        P3Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, P3Reasons.Cutoff, $"({choke.X:0},{choke.Y:0})");
                    }
                    return choke;
                }
                if (!s.PursuitLogged)
                {
                    s.PursuitLogged = true;
                    tc.Metrics.InterceptCount++;
                    P3Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, P3Reasons.Intercept, $"t {t:0.0} s");
                }
                var standoff = Vector2.Distance(goal, enemy.Position);
                var aim = p - Direction(s.Centre, p) * standoff;
                return world.Grid.IsWalkable(aim) ? aim : goal;
            }
            return goal;
        }

        /// <summary>Spec 147: the choke ahead of the enemy group that this squad reaches first, sooner than catching it directly.</summary>
        private bool CutoffP3(SimWorld world, TeamIntel intel, Squad s, Contact enemy, float speed, float interceptT, out Vector2 choke)
        {
            choke = default;
            EnemyGroup? group = null;
            foreach (var g in intel.EnemyGroups)
                if (!g.Air && Vector2.Distance(g.Centre, enemy.Position) <= 25f)
                {
                    group = g;
                    break;
                }
            if (group is not { } eg || eg.Confidence < Tun.Pursuit.CutoffConfidence) return false;
            var v = eg.Velocity.Length();
            if (v < 2f) return false;
            var dir = eg.Velocity / v;
            var best = float.MaxValue;
            foreach (var ch in world.Topology.Chokes)
            {
                var rel = ch.Centre - eg.Centre;
                var along = Vector2.Dot(rel, dir);
                if (along <= 0f || along > v * Tun.Pursuit.CutoffLookS) continue;
                if (MathF.Abs(rel.X * dir.Y - rel.Y * dir.X) > ch.Width + 10f) continue;
                var ours = SyncPlanner.Eta(Vector2.Distance(s.Centre, ch.Centre), speed);
                if (!PursuitDiscipline.CutoffBetter(ours, along / v, interceptT) || ours >= best) continue;
                best = ours;
                choke = ch.Centre;
            }
            return best < float.MaxValue;
        }

        private static bool AntiAirSquad(SimWorld world, Squad s)
        {
            var n = 0;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v) && CombatRoleDoctrine.BaseRole(world, v) == DoctrineRole.AntiAir) n++;
            return n * 2 > s.MemberList.Count;
        }

        private static Contact? NearestContact(TeamIntel intel, Vector2 from)
        {
            Contact? best = null;
            var bestDistance = float.MaxValue;
            foreach (var c in intel.Contacts)
            {
                if (c.Displaced || c.Flying) continue;
                var d = Vector2.DistanceSquared(c.Position, from);
                if (d < bestDistance)
                {
                    bestDistance = d;
                    best = c;
                }
            }
            return best;
        }

        // ------------------------------------------------------------------------------------------------ 199 focus

        /// <summary>Spec 199: the share of the squad focus weight: full on a high threat, boss part, near kill or strategic unit; spread otherwise.</summary>
        private float FocusShareP3(SimWorld world, TeamIntel intel, Squad s)
        {
            var tc = P3;
            if (tc == null || !s.Focus.IsValid || !world.TryGetVehicle(s.Focus, out var v) || intel.Find(s.Focus) is not { } c) return 1f;
            var shootsUs = world.TryGetVehicle(v.Target, out var victim) && victim.Team == _commander.Team;
            var highThreat = shootsUs && (c.Group is ForceGroup.AntiTank or ForceGroup.Armour || c.Strength >= s.Strength * 0.5f);
            var strong = FocusRules.Strong(highThreat, v.Def.Boss || v.HasParts, v.Hp / MathF.Max(1f, v.MaxHp), c.HighValue);
            var share = strong ? 1f : Tun.Board.SpreadFocusShare;
            if (MathF.Abs(share - s.P3FocusShare) > 1e-4f)
                P3Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Target, strong ? P3Reasons.FocusFire : P3Reasons.SpreadFire, $"#{s.Focus.Value}");
            return share;
        }

        // ------------------------------------------------------------------------------------------------ 205 ambush

        /// <summary>
        /// Spec 205 ambush discipline: hold fire, open inside 55-70 % of the effective range, when a high-value target is deep in
        /// reach, or when detected (hit); every ambush squad close by opens in the same look (synchronized volley; the planned
        /// damage board spreads its targets).
        /// </summary>
        private void StanceP3(SimWorld world, TeamIntel intel, Squad s, TacticModules m)
        {
            var stance = _commander.StanceFor(s);
            var holding = false;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v) && v.AiHoldFire) holding = true;
            if (stance != FireStance.HoldFire || s.HoldReleased)
            {
                if (holding && s.HoldReleased) OpenAmbush(world, s, P3Reasons.AmbushDetected);
                else SetHoldFire(world, s, false);
                return;
            }
            var band = Tun.Stance.AmbushRange;
            var share = m.HoldFire > 0f ? m.HoldFire : world.Catalog.Ai.HoldFire > 0f ? world.Catalog.Ai.HoldFire : 0.6f;
            if (band.Length >= 2) share = Math.Clamp(share, band[0], band[1]);
            string? why = null;
            if (NearestEnemyDistance(intel, s.Centre) <= s.Reach * share) why = P3Reasons.AmbushRange;
            else
                foreach (var c in intel.Contacts)
                    if (c.InSight && c.HighValue && !c.Flying && Vector2.Distance(c.Position, s.Centre) <= s.Reach * Tun.Stance.HighValueReach)
                    {
                        why = P3Reasons.AmbushHighValue;
                        break;
                    }
            if (why == null)
            {
                SetHoldFire(world, s, true);
                return;
            }
            OpenAmbush(world, s, why);
        }

        private void OpenAmbush(SimWorld world, Squad s, string why)
        {
            s.HoldReleased = true;
            SetHoldFire(world, s, false);
            P3Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.Action, why);
            foreach (var o in _squads)
            {
                if (o == s || o.HoldReleased || o.MemberList.Count == 0 || Vector2.Distance(o.Centre, s.Centre) > Tun.Stance.AmbushSyncRadius) continue;
                if (_commander.StanceFor(o) != FireStance.HoldFire || o.Action != SquadAction.Hold) continue;
                o.HoldReleased = true;
                SetHoldFire(world, o, false);
                P3Reasons.Squad(world, _commander.Team, o.Id, DecisionKind.Action, P3Reasons.AmbushSync, $"with squad {s.Id}");
            }
        }

        // ------------------------------------------------------------------------------------------------ 149 / 200 units

        /// <summary>Spec 149 stances per member and spec 200 target handoff by suitability (short lock window, no churn).</summary>
        private void UnitsP3(SimWorld world, Squad s)
        {
            var tc = P3;
            if (tc == null) return;
            var now = world.Time;
            var quiet = world.Doctrine.For(_commander.Team).QuietStrikes;
            foreach (var id in s.MemberList)
            {
                if (!world.TryGetVehicle(id, out var v)) continue;
                v.P3Stance = StanceRules.For(CombatRoleDoctrine.BaseRole(world, v), s.Action, v.AiHoldFire, quiet);
                if (v.P3Stance == UnitStance.ReturnFire && !v.Target.IsValid) world.CombatWatch.Explain(id, CombatIdleReason.HoldFireOrder, 1.5f);
            }
            if (s.MemberList.Count < 2) return;
            foreach (var aid in s.MemberList)
            {
                if (!world.TryGetVehicle(aid, out var a) || now < a.P3HandoffUntil || !world.TryGetVehicle(a.Target, out var x) || !x.IsAlive) continue;
                var suitA = world.Damage.Estimate(a.Def.Weapon, a, x);
                foreach (var bid in s.MemberList)
                {
                    if (bid == aid || !world.TryGetVehicle(bid, out var b) || now < b.P3HandoffUntil || b.Target == x.Id) continue;
                    var w = b.Def.Weapon;
                    if (w.Damage <= 0f || !w.CanTarget(x.Flying) || Vector2.Distance(b.Position, x.Position) > w.Range) continue;
                    var suitB = world.Damage.Estimate(w, b, x);
                    if (suitB < 0.2f || suitB < suitA * Tun.Board.HandoffRatio) continue;
                    if (world.TryGetVehicle(b.Target, out var y) && y.IsAlive && world.Damage.Estimate(w, b, y) >= suitB) continue;
                    var until = now + Tun.Board.HandoffLockS;
                    b.P3Prefer = x.Id;
                    b.P3Avoid = EntityId.None;
                    a.P3Avoid = x.Id;
                    a.P3Prefer = EntityId.None;
                    a.P3HandoffUntil = b.P3HandoffUntil = until;
                    tc.Metrics.HandoffCount++;
                    P3Reasons.Unit(world, b, DecisionKind.Target, P3Reasons.Handoff, $"#{x.Id.Value} from #{a.Id.Value} ({suitB:0.00} vs {suitA:0.00})");
                    break;
                }
            }
        }

        // ------------------------------------------------------------------------------------------------ 213 dispersion

        /// <summary>Spec 213: enemy shells landed near the squad lately, or a strike warning is up: stay spread, no regroup yet.</summary>
        internal bool DisperseHoldP3(SimWorld world, TeamIntel intel, Squad s)
        {
            var tc = P3;
            if (tc == null) return false;
            var now = world.Time;
            var hold = tc.Battery.RecentImpactNear(s.Centre, s.Spread + 20f, now, Tun.Stance.DispersalHoldS);
            if (!hold)
                foreach (var w in intel.Warnings)
                    if (w.Team != _commander.Team && w.Due >= now && Vector2.Distance(w.Centre, s.Centre) <= w.Radius + s.Spread + 10f)
                    {
                        hold = true;
                        break;
                    }
            if (hold && now >= s.DisperseLoggedUntil)
            {
                s.DisperseLoggedUntil = now + Tun.Stance.DispersalHoldS;
                P3Reasons.Squad(world, _commander.Team, s.Id, DecisionKind.State, P3Reasons.DisperseHold);
            }
            return hold;
        }

        // ------------------------------------------------------------------------------------------------ commander helpers

        /// <summary>A flank point the squad fits through (spec 76), for the commander's packages and frontage.</summary>
        internal bool FlankPointP3(SimWorld world, TeamIntel intel, Squad s, Vector2 goal, int side, out Vector2 point) =>
            FlankPoint(world, intel, s, goal, side, out point, out _) && FlankRouteFits(world, s, point);

        internal float SlowestP3(SimWorld world, Squad s) => SlowestSpeed(world, s);

        /// <summary>P2 22's split for a second simultaneous objective; the new part (null if none was made).</summary>
        internal Squad? SplitP3(SimWorld world, Squad s, string why)
        {
            var count = _squads.Count;
            Split(world, s, why);
            return _squads.Count > count ? _squads[_squads.Count - 1] : null;
        }
    }
}
