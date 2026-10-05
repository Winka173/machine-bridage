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
    /// <summary>
    /// AI MASTER P3 (lane A), the commander's coordination pass, once a second right after P2's assignment (B.2 / spec
    /// 71-73), as adjustments of the tasks it just gave: counterattack windows (212), defence in depth (211), objective
    /// sunk-cost reset (172), economy of force and two-objective splits (171, P2 22), deadline-aware assignment and the
    /// intercept arrival filter (207, P2 I9), dynamic frontage (126), attack packages with synchronized ETA, staging,
    /// fix-and-flank and scout-before-commit (131, 134-137), committed power on the board (138), the AA coverage optimiser
    /// (141, 169), counter-battery missions (144) and the ranked reserve release (170, via P2's ReserveTrigger). Fog-fair:
    /// only the side's intel, memory and own units. Deterministic: squads in list / id order, no Random.
    /// </summary>
    public sealed partial class AiCommander
    {
        private TeamCoordination? _p3;
        private AttackPackage? _package;
        private Vector2 _packageDoneFor = new(float.NaN, float.NaN);
        private readonly Dictionary<int, (double until, Vector2 at)> _waves = new();
        private readonly Dictionary<int, double> _p3LogAt = new();
        private readonly Dictionary<int, (float progress, double at)> _pointProgress = new();
        private readonly HashSet<OriginEstimate> _missionLogged = new();
        private Vector2[] _depthLines = Array.Empty<Vector2>();
        private Vector2 _depthFor = new(float.NaN, float.NaN);
        private int _depthLine;
        private double _depthLostSince = double.NaN, _depthBackSince = double.NaN;
        private double _sunkUntil = double.NegativeInfinity, _splitReadyAt, _coverageAt = double.NegativeInfinity, _keptLogAt = double.NegativeInfinity;
        private Vector2 _sunkAt;
        private Vector2 _lastRelease = new(float.NaN, float.NaN);
        private SmokePurpose _smokePurpose = SmokePurpose.ScreenSquad;

        /// <summary>The side's P3 coordination state (null until the first commander look, or with ai.coordination.enabled off).</summary>
        public TeamCoordination? CoordinationP3 => Tun.Coordination.Enabled ? _p3 : null;

        /// <summary>The attack package in force (spec 136), if any.</summary>
        public AttackPackage? Package => _package;

        private void CoordinateP3(SimWorld world, TeamIntel intel)
        {
            if (!Tun.Coordination.Enabled) return;
            _p3 ??= world.Coordination.For(Team);
            world.Coordination.Step();
            _p3.Update(intel, Intent.PrimaryObjective);
            _p3.Memory.PruneRoutes(world.Time);
            foreach (var s in Squads.Squads)
            {
                s.P3Role = PackageRole.None;
                s.P3StageUntil = double.NegativeInfinity;
            }
            CounterattackP3(world, intel);
            DefenseInDepthP3(world, intel);
            SunkCostP3(world, intel);
            EconomyOfForceP3(world, intel);
            DeadlinesP3(world, intel);
            FrontageP3(world, intel);
            PackageP3(world, intel);
            ApplyWavesP3(world);
            CommittedPowerP3();
            CoverageP3(world, intel);
            CounterBatteryP3(world, intel);
        }

        private bool LogDue(int key, double every)
        {
            var now = _world!.Time;
            if (_p3LogAt.TryGetValue(key, out var at) && now - at < every) return false;
            _p3LogAt[key] = now;
            if (_p3LogAt.Count > 512) _p3LogAt.Clear();
            return true;
        }

        private static void SetTask(Squad s, TaskKind kind, Vector2? objective, bool hold, bool window, int flankSide = 0) =>
            s.Task = new SquadTask { Kind = kind, Objective = objective, Hold = hold, Window = window, FlankSide = flankSide };

        // ------------------------------------------------------------------------------------------------ 212

        private void CounterattackP3(SimWorld world, TeamIntel intel)
        {
            var tc = _p3!;
            var now = world.Time;
            var losses = tc.Memory.EnemyLosses;
            for (var i = losses.Count - 1; i >= 0; i--)
            {
                var l = losses[i];
                if (now - l.Time > Tun.Objectives.CounterLookS) break;
                if (tc.WindowNear(l.At) != null) continue;
                var lost = 0f;
                foreach (var o in losses)
                    if (now - o.Time <= Tun.Objectives.CounterLookS && Vector2.Distance(o.At, l.At) <= Tun.Objectives.CounterRadius) lost += o.Value;
                var (_, remaining) = intel.StrengthAround(l.At, Tun.Objectives.CounterRadius);
                if (!CounterattackWindow.Opens(lost, remaining, Tun.Objectives.CounterLossShare)) continue;
                var share = lost / MathF.Max(0.01f, lost + remaining);
                tc.OpenWindow(new CounterattackWindow(l.At, Tun.Objectives.CounterRadius, now + Tun.Objectives.CounterWindowS, share));
                tc.Metrics.CounterattackWindows++;
                P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.CounterattackWindow, $"({l.At.X:0},{l.At.Y:0}) enemy lost {share:0%}");
            }
        }

        // ------------------------------------------------------------------------------------------------ 211

        private void DefenseInDepthP3(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            var defends = Defending || world.AiProfile.Defends(Team);
            if (!defends || Intent.PrimaryObjective is not { } o || !world.TryGetRally(Team, out var home))
            {
                _depthLine = 0;
                return;
            }
            if (float.IsNaN(_depthFor.X) || Vector2.Distance(_depthFor, o) > 10f)
            {
                var raw = ObjectiveRules.DepthLines(o, home, Tun.Objectives.DepthLines, Tun.Objectives.DepthStep);
                _depthLines = new Vector2[raw.Length];
                for (var i = 0; i < raw.Length; i++)
                {
                    var p = i == 0 ? raw[i] : world.Lanes.OffLane(world.Map.Clamp(raw[i], 8f), 8f);
                    _depthLines[i] = world.Grid.IsWalkable(p) ? p : raw[i];
                }
                _depthFor = o;
                _depthLine = 0;
                _depthLostSince = _depthBackSince = double.NaN;
            }
            var line = _depthLines[_depthLine];
            var (own, enemy) = intel.StrengthAround(line, 25f);
            var pointLost = _depthLine == 0 && PointOwner(world, o) == EnemyTeam;
            if (_depthLine < _depthLines.Length - 1 && (pointLost || enemy > MathF.Max(own, 0.1f) * Tun.ReserveRelease.BreakthroughRatio))
            {
                if (double.IsNaN(_depthLostSince)) _depthLostSince = now;
                if (now - _depthLostSince >= Tun.Objectives.DepthLostS)
                {
                    _depthLine++;
                    _depthLostSince = double.NaN;
                    _p3!.Metrics.DepthLineChanges++;
                    P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.DepthNextLine,
                        $"line {_depthLine} ({_depthLines[_depthLine].X:0},{_depthLines[_depthLine].Y:0}) {(pointLost ? "point lost" : "line held by the enemy")}");
                }
            }
            else _depthLostSince = double.NaN;
            if (_depthLine > 0)
            {
                var back = _depthLines[_depthLine - 1];
                var (o2, e2) = intel.StrengthAround(back, 25f);
                if (e2 <= o2 * 0.5f && !(_depthLine - 1 == 0 && PointOwner(world, o) == EnemyTeam))
                {
                    if (double.IsNaN(_depthBackSince)) _depthBackSince = now;
                    if (now - _depthBackSince >= Tun.Objectives.DepthLostS)
                    {
                        _depthLine--;
                        _depthBackSince = double.NaN;
                        P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.DepthRestored, $"line {_depthLine}");
                    }
                }
                else _depthBackSince = double.NaN;
            }
            if (_depthLine == 0) return;
            foreach (var s in Squads.Squads)
                if (s.Task.Hold && !s.IsReserve) SetTask(s, s.Task.Kind, _depthLines[_depthLine], true, false);
        }

        private int PointOwner(SimWorld world, Vector2 at)
        {
            if (world.Intel.Objectives is not { } mode) return -1;
            foreach (var p in mode.Points)
                if (Vector2.Distance(p.Def.Position, at) <= p.Def.Radius + 5f) return p.Owner;
            return -1;
        }

        // ------------------------------------------------------------------------------------------------ 172

        private void SunkCostP3(SimWorld world, TeamIntel intel)
        {
            if (Intent.PrimaryObjective is not { } o) return;
            var tc = _p3!;
            var now = world.Time;
            var active = now < _sunkUntil && Vector2.Distance(_sunkAt, o) < 15f;
            if (!active)
            {
                var lost = tc.Memory.LossesNear(o, 40f, Tun.Objectives.SunkHalfLifeS, now);
                if (lost <= 0f || _urgency >= Tun.Pursuit.UrgencyDrop) return;
                var (own, enemy) = intel.StrengthAround(o, 60f);
                var cost = ObjectiveRules.RecoveryCost(lost, own, enemy);
                var value = Tun.Objectives.SunkValue * (1f + _urgency);
                if (enemy <= 0f || !ObjectiveRules.SunkCostReset(cost, value)) return;
                _sunkUntil = now + Tun.Objectives.SunkResetS;
                _sunkAt = o;
                tc.Metrics.SunkCostResets++;
                P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.SunkCostReset, $"({o.X:0},{o.Y:0}) cost {cost:0.#} > value {value:0.#}");
            }
            // No new reinforcement there: squads on it take the next task by the strategic state (never a health retreat).
            var home = world.TryGetRally(Team, out var h) ? h : o;
            foreach (var s in Squads.Squads)
            {
                if (s.Task.Kind != TaskKind.Primary || s.Task.Objective is not { } at || Vector2.Distance(at, o) > 15f) continue;
                if (Intent.SecondaryObjective is { } next) SetTask(s, TaskKind.Secondary, next, true, false);
                else
                {
                    var hold = world.Map.Clamp(s.Centre + Direction(s.Centre, home) * 20f, 8f);
                    SetTask(s, TaskKind.Secondary, world.Grid.IsWalkable(hold) ? hold : s.Centre, true, false);
                }
            }
        }

        // ------------------------------------------------------------------------------------------------ 171, P2 22

        private void EconomyOfForceP3(SimWorld world, TeamIntel intel)
        {
            if (Intent.SecondaryObjective is not { } sec || Intent.PrimaryObjective is not { } prim) return;
            var now = world.Time;
            var tc = _p3!;
            var decisive = Intent.AttackWindow || _urgency >= 0.5f;
            var total = 0f;
            var on = new List<Squad>();
            foreach (var s in Squads.Squads)
            {
                total += s.Strength;
                if (s.Task.Kind == TaskKind.Secondary && !s.IsReserve && s.Task.Objective is { } at && Vector2.Distance(at, sec) < 5f) on.Add(s);
            }
            var (_, enemyThere) = intel.StrengthAround(sec, 60f);
            if (decisive && on.Count > 1)
            {
                on.Sort((a, b) =>
                {
                    var c = a.Strength.CompareTo(b.Strength);
                    return c != 0 ? c : a.Id.CompareTo(b.Id);
                });
                var need = ObjectiveRules.SecondaryNeed(enemyThere, total);
                var kept = 0f;
                for (var i = 0; i < on.Count; i++)
                {
                    var s = on[i];
                    if (i == 0 || kept + s.Strength <= need)
                    {
                        kept += s.Strength;
                        continue;
                    }
                    SetTask(s, TaskKind.Primary, prim, false, Intent.AttackWindow);
                    tc.Metrics.EconomyOfForceMoves++;
                    if (LogDue(s.Id * 8 + 1, 20.0))
                        P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.EconomyOfForce, $"squad {s.Id} -> primary (secondary needs {need:0.#})");
                }
            }
            // A second simultaneous objective with nobody on it: a large squad splits (P2 22's scaffold).
            if (on.Count > 0 || now < _splitReadyAt || (enemyThere <= 0f && !Pressured(intel, sec))) return;
            Squad? big = null;
            foreach (var s in Squads.Squads)
                if (s.Task.Kind == TaskKind.Primary && !s.IsReserve && s.State != SquadState.Combat && s.MemberList.Count >= Tun.Objectives.SplitMinMembers &&
                    (big == null || s.MemberList.Count > big.MemberList.Count)) big = s;
            if (big == null) return;
            _splitReadyAt = now + 30.0;
            if (Squads.SplitP3(world, big, "two objectives") is not { } part) return;
            SetTask(part, TaskKind.Secondary, sec, true, false);
            tc.Metrics.TwoObjectiveSplits++;
            P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.TwoObjectiveSplit, $"squad {big.Id} -> {part.Id} on ({sec.X:0},{sec.Y:0})");
        }

        private static bool Pressured(TeamIntel intel, Vector2 at)
        {
            foreach (var e in intel.Events)
                if (e.Kind is IntelEventKind.ObjectivePressure or IntelEventKind.Threat && Vector2.Distance(e.Centre, at) <= e.Radius + 20f) return true;
            return false;
        }

        // ------------------------------------------------------------------------------------------------ 207

        private void DeadlinesP3(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            var tc = _p3!;
            if (world.Intel.Objectives is { } mode)
                for (var i = 0; i < mode.Points.Count; i++)
                {
                    var p = mode.Points[i];
                    if (!_pointProgress.ContainsKey(i)) _pointProgress[i] = (p.Progress, now);
                }
            foreach (var s in Squads.Squads)
            {
                if (s.IsReserve || s.Fast || s.MemberList.Count == 0 || s.Task.Objective is not { } o) continue;
                var deadline = DeadlineOf(world, intel, o);
                if (float.IsInfinity(deadline)) continue;
                var eta = SyncPlanner.Eta(Vector2.Distance(s.Centre, o) - s.Reach * 0.5f, Squads.SlowestP3(world, s));
                if (ObjectiveRules.DeadlineUseful(eta, deadline)) continue;
                // Not sent in vain: the next objective (or hold where it is); a fast squad takes the deadline instead.
                if (Intent.SecondaryObjective is { } next && Vector2.Distance(next, o) > 15f) SetTask(s, TaskKind.Secondary, next, true, false);
                else SetTask(s, TaskKind.Secondary, s.Centre, true, false);
                tc.Metrics.ObjectiveMissedDeadlineOrders++;
                if (now - s.P3DeadlineLogAt >= 10.0)
                {
                    s.P3DeadlineLogAt = now;
                    P3Reasons.Squad(world, Team, s.Id, DecisionKind.Action, P3Reasons.DeadlineSkip, $"eta {eta:0} s > deadline {deadline:0} s");
                }
                foreach (var f in Squads.Squads)
                {
                    if (!f.Fast || f.IsReserve || f.MemberList.Count == 0 || (f.Task.Objective is { } fo && Vector2.Distance(fo, o) < 5f)) continue;
                    var fe = SyncPlanner.Eta(Vector2.Distance(f.Centre, o) - f.Reach * 0.5f, Squads.SlowestP3(world, f));
                    if (!ObjectiveRules.DeadlineUseful(fe, deadline)) continue;
                    SetTask(f, TaskKind.Primary, o, false, true);
                    if (LogDue(f.Id * 8 + 2, 10.0)) P3Reasons.Squad(world, Team, f.Id, DecisionKind.Action, P3Reasons.DeadlineFast, $"eta {fe:0} s");
                    break;
                }
            }
            // Progress samples for the next look's capture rates.
            if (world.Intel.Objectives is { } m2)
                for (var i = 0; i < m2.Points.Count; i++)
                    if (now - _pointProgress[i].at >= 0.99) _pointProgress[i] = (m2.Points[i].Progress, now);
        }

        /// <summary>
        /// Spec 207 deadlines on an objective (seconds; infinity: none): the timed match's end, the time until the enemy
        /// flips a point there at its observed capture rate (the public capture bar), and for intercept doctrines (P2 I9 /
        /// I20) the observed ETA of an enemy group heading there.
        /// </summary>
        private float DeadlineOf(SimWorld world, TeamIntel intel, Vector2 o)
        {
            var now = world.Time;
            var deadline = float.PositiveInfinity;
            if (world.Intel.Objectives is Modes.ShowdownMode showdown)
            {
                var left = showdown.SecondsLeft(world);
                if (left > 0f) deadline = left;
            }
            if (world.Intel.Objectives is { } mode)
                for (var i = 0; i < mode.Points.Count; i++)
                {
                    var p = mode.Points[i];
                    if (Vector2.Distance(p.Def.Position, o) > p.Def.Radius + 5f || p.Owner == EnemyTeam || !_pointProgress.TryGetValue(i, out var prev)) continue;
                    var dt = now - prev.at;
                    if (dt <= 0.01) continue;
                    var enemySign = Team == Modes.PointCapture.TeamA ? -1f : 1f;
                    var enemyRate = (float)((p.Progress - prev.progress) / dt) * enemySign;
                    if (enemyRate <= 0.001f) continue;
                    var remaining = p.Owner == Team ? p.Progress * -enemySign : 1f - p.Progress * enemySign;
                    deadline = MathF.Min(deadline, MathF.Max(0f, remaining) / enemyRate);
                }
            if (world.Doctrine.For(Team).FireSupport == FireSupportPolicy.InterceptPredict)
                foreach (var g in intel.EnemyGroups)
                {
                    var speed = g.Velocity.Length();
                    if (g.Air || speed < 1f || g.Confidence < 0.5f || Vector2.Dot(g.Velocity, o - g.Centre) <= 0f) continue;
                    deadline = MathF.Min(deadline, Vector2.Distance(g.Centre, o) / speed);
                }
            return deadline;
        }

        // ------------------------------------------------------------------------------------------------ 126

        private void FrontageP3(SimWorld world, TeamIntel intel)
        {
            if (Intent.PrimaryObjective is not { } target) return;
            var now = world.Time;
            var tc = _p3!;
            var attackers = new List<Squad>();
            foreach (var s in Squads.Squads)
                if (s.Task.Kind == TaskKind.Primary && !s.Task.Hold && !s.IsReserve && s.MemberList.Count > 0) attackers.Add(s);
            if (attackers.Count < 2) return;
            attackers.Sort((a, b) =>
            {
                var c = b.Strength.CompareTo(a.Strength);
                return c != 0 ? c : a.Id.CompareTo(b.Id);
            });
            var usable = Tun.AttackSync.DefaultFrontage;
            var seg = tc.Frontline.Nearest(target);
            if (seg >= 0 && Vector2.Distance(tc.Frontline.Segments[seg].Centre, target) < 80f) usable = MathF.Min(usable, tc.Frontline.Segments[seg].Width);
            var centroid = Vector2.Zero;
            foreach (var s in attackers) centroid += s.Centre;
            centroid /= attackers.Count;
            var topology = world.Topology;
            int from = topology.CellIndex(centroid), to = topology.CellIndex(target);
            if (from >= 0 && to >= 0)
            {
                var narrowest = topology.Bottleneck(from, to);
                if (!float.IsInfinity(narrowest)) usable = MathF.Min(usable, MathF.Max(4f, narrowest));
            }
            var required = 0f;
            var wave = 0;
            var side = -1;
            foreach (var s in attackers)
            {
                var need = 0f;
                foreach (var id in s.MemberList)
                    if (world.TryGetVehicle(id, out var v)) need += v.Def.Width + Tun.AttackSync.FrontageSeparation;
                required += need;
                if (required - need <= 0f || required <= usable) continue;
                // 1. another route; 2-3. hold back as a staggered wave (the reserve is P2's); 4. fire support is the package's prep.
                if (Squads.FlankPointP3(world, intel, s, target, side, out _) || Squads.FlankPointP3(world, intel, s, target, -side, out _))
                {
                    var use = Squads.FlankPointP3(world, intel, s, target, side, out _) ? side : -side;
                    SetTask(s, s.Task.Kind, s.Task.Objective, false, s.Task.Window, use);
                    side = -side;
                    required -= need; // on its own route: not in this frontage
                    if (LogDue(s.Id * 8 + 3, 20.0))
                        P3Reasons.Squad(world, Team, s.Id, DecisionKind.Plan, P3Reasons.FrontageSecondRoute, $"frontage {required + need:0} m > usable {usable:0} m");
                    continue;
                }
                wave++;
                if (!_waves.TryGetValue(s.Id, out var w) || now - w.until > 60.0)
                {
                    _waves[s.Id] = (now + Tun.AttackSync.WaveGapS * wave, s.Centre);
                    P3Reasons.Squad(world, Team, s.Id, DecisionKind.Plan, P3Reasons.FrontageStagger, $"wave {wave} (+{Tun.AttackSync.WaveGapS * wave:0} s)");
                }
            }
        }

        private void ApplyWavesP3(SimWorld world)
        {
            var now = world.Time;
            foreach (var s in Squads.Squads)
            {
                if (!_waves.TryGetValue(s.Id, out var w) || w.until <= now) continue;
                if (w.until > s.P3StageUntil)
                {
                    s.P3StageUntil = w.until;
                    s.P3Staging = w.at;
                }
                if (s.P3Role == PackageRole.None) s.P3Role = PackageRole.Wave;
            }
            if (_waves.Count > 64) _waves.Clear();
        }

        // ------------------------------------------------------------------------------------------------ 131, 134-137

        private void PackageP3(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            var tc = _p3!;
            // A fixed objective only: a package on the moving enemy centre would be rebuilt (and staged) every look.
            var target = Intent.PrimaryObjective;
            if (!Intent.AttackWindow || target is not { } t || Defending)
            {
                AbortPackage(world, "window shut");
                return;
            }
            var members = new List<Squad>();
            foreach (var s in Squads.Squads)
                if (s.Task.Kind == TaskKind.Primary && !s.Task.Hold && !s.IsReserve && s.MemberList.Count > 0) members.Add(s);
            if (members.Count == 0)
            {
                AbortPackage(world, "no squads");
                return;
            }
            if (_package != null)
            {
                var mainAlive = members.Exists(s => s.Id == _package.Main);
                if (Vector2.Distance(_package.Target, t) >= 15f || !mainAlive)
                    AbortPackage(world, mainAlive ? "target moved" : "main effort gone");
                else if (now > _package.ExecuteAt + Tun.AttackSync.PackageSeconds)
                {
                    _packageDoneFor = _package.Target;
                    _package = null;
                    return;
                }
            }
            if (_package == null)
            {
                if (!float.IsNaN(_packageDoneFor.X) && Vector2.Distance(_packageDoneFor, t) < 15f) return;
                _package = BuildPackage(world, intel, members, t);
                if (_package == null) return;
            }
            ApplyPackage(world, intel, members);
        }

        private readonly Dictionary<int, (double until, Vector2 at, float eta)> _stage = new();

        private AttackPackage? BuildPackage(SimWorld world, TeamIntel intel, List<Squad> members, Vector2 target)
        {
            var now = world.Time;
            var tc = _p3!;
            members.Sort((a, b) =>
            {
                var c = b.Strength.CompareTo(a.Strength);
                return c != 0 ? c : a.Id.CompareTo(b.Id);
            });
            var main = members[0];
            var p = new AttackPackage { Main = main.Id, Target = target, CreatedAt = now };
            foreach (var s in members) p.Members.Add(s.Id);
            foreach (var s in Squads.Squads)
                if (s.IsReserve)
                {
                    p.Reserve = s.Id;
                    break;
                }
            var (_, enemyThere) = intel.StrengthAround(target, 60f);
            var stable = false;
            foreach (var g in intel.EnemyGroups)
                if (!g.Air && Vector2.Distance(g.Centre, target) < 40f && g.Velocity.Length() < 2f) stable = true;
            var own = 0f;
            foreach (var s in members) own += s.Strength;
            var access = 1;
            if (Squads.FlankPointP3(world, intel, main, target, -1, out _)) access++;
            if (Squads.FlankPointP3(world, intel, main, target, 1, out _)) access++;
            Vector2 flankPoint = default;
            // Spec 134: fix-and-flank.
            if (members.Count >= 2 && FixAndFlank.Viable(stable, access, own, enemyThere, AttackThreshold(null)))
            {
                Squad? best = null;
                var bestSide = 0;
                var bestCost = float.MaxValue;
                foreach (var s in members)
                {
                    if (s == main) continue;
                    for (var side = -1; side <= 1; side += 2)
                    {
                        if (!Squads.FlankPointP3(world, intel, s, target, side, out var fp)) continue;
                        var cost = tc.Memory.DeathAlong(s.Centre, fp, now) + intel.ThreatAt(ThreatKind.AntiTank, fp) / MathF.Max(1f, s.Strength) +
                                   tc.Routes.Occupancy(fp, s.Id, now) * Tun.Routes.OccupancyWeight - (s.Fast ? 0.5f : 0f);
                        if (cost < bestCost)
                        {
                            bestCost = cost;
                            best = s;
                            bestSide = side;
                            flankPoint = fp;
                        }
                    }
                }
                if (best != null)
                {
                    p.Flank = best.Id;
                    p.FlankSide = bestSide;
                    p.Fix = main.Id;
                    tc.Metrics.FixFlankCount++;
                    P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.FlankAssigned, $"fix {main.Id}, flank {best.Id} side {bestSide}");
                }
            }
            // ETAs (spec 135): ground squads to contact, the flank by its way round; artillery prep; air cover.
            var etas = new List<float>();
            var etaOf = new Dictionary<int, float>();
            foreach (var s in members)
            {
                var speed = Squads.SlowestP3(world, s);
                var eta = p.Flank == s.Id
                    ? SyncPlanner.Eta(Vector2.Distance(s.Centre, flankPoint) + Vector2.Distance(flankPoint, target) - s.Reach * 0.8f, speed)
                    : SyncPlanner.Eta(Vector2.Distance(s.Centre, target) - s.Reach * 0.8f, speed);
                etas.Add(eta);
                etaOf[s.Id] = eta;
            }
            float prep = 0f, air = float.MaxValue;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Team) continue;
                if (!v.Flying && v.Def.Weapon.MinRange > 0f && Vector2.Distance(v.Position, target) <= v.Def.Weapon.Range) prep = 0.01f;
                if (v.Flying && v.Def.Weapon.Damage > 0f) air = MathF.Min(air, Vector2.Distance(v.Position, target) / MathF.Max(1f, v.Def.Speed));
            }
            p.ArtilleryPrep = prep > 0f;
            p.AirCover = air < float.MaxValue;
            var delay = SyncPlanner.ExecuteDelay(etas, prep, p.AirCover ? air : 0f);
            // Spec 131: scout before committing into unknown / recent-death ground (never waiting past the cap).
            var unknown = tc.Memory.UnknownShare(intel, target, 40f, now);
            var danger = MathF.Max(tc.Memory.DeathDanger(target, now), tc.Memory.DeathAlong(main.Centre, target, now));
            var shortTimer = world.Intel.Objectives is Modes.ShowdownMode sd && sd.SecondsLeft(world) is var left && left > 0f && left < 60f;
            if (ScoutPlanner.Needed(unknown + ReconBoostP4(), danger, _urgency, shortTimer) && SendScout(world, intel, p, target) is { } scoutEta)
            {
                var wait = ScoutPlanner.Wait(scoutEta);
                p.ScoutUntil = now + wait;
                delay = MathF.Max(delay, wait);
                tc.Metrics.ScoutRequests++;
                P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.ScoutBeforeCommit,
                    $"unknown {unknown:0%} danger {danger:0.0}: wait {wait:0.0} s");
            }
            p.ExecuteAt = now + delay;
            p.Staging = StagingP3(world, intel, target, main.Centre);
            var lateral = new Vector2(-Direction(target, main.Centre).Y, Direction(target, main.Centre).X);
            _stage.Clear();
            for (var k = 0; k < members.Count; k++)
            {
                var s = members[k];
                var stage = s.Id == p.Flank ? 0f : SyncPlanner.StageSeconds(delay, etaOf[s.Id]);
                var at = p.Staging + lateral * ((k - (members.Count - 1) * 0.5f) * Tun.AttackSync.SubZoneSpacing);
                if (!world.Grid.IsWalkable(at)) at = p.Staging;
                _stage[s.Id] = (stage > 0f ? now + stage : double.NegativeInfinity, at, etaOf[s.Id]);
            }
            tc.Metrics.AttackPackagesCreated++;
            tc.Metrics.SyncArrivalDeltaMax = MathF.Max(tc.Metrics.SyncArrivalDeltaMax, SyncPlanner.ContactDelta(etas, delay));
            P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.PackageCreated, p.ToString());
            return p;
        }

        private void ApplyPackage(SimWorld world, TeamIntel intel, List<Squad> members)
        {
            var p = _package!;
            var now = world.Time;
            if (p.ScoutUntil > double.NegativeInfinity && now >= p.ScoutUntil && now < p.ScoutUntil + 1.5 &&
                _p3!.Memory.UnknownShare(intel, p.Target, 40f, now) >= Tun.AttackSync.ScoutUnknownShare)
                P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.ScoutTimeout, "commit with the uncertainty known");
            foreach (var s in members)
            {
                if (s.Id == p.Main) s.P3Role = p.Fix.HasValue ? PackageRole.Fix : PackageRole.Main;
                else if (s.Id == p.Flank)
                {
                    s.P3Role = PackageRole.Flank;
                    SetTask(s, s.Task.Kind, s.Task.Objective, s.Task.Hold, s.Task.Window, p.FlankSide);
                }
                else if (p.Members.Contains(s.Id)) s.P3Role = PackageRole.Wave;
                if (_stage.TryGetValue(s.Id, out var st))
                {
                    s.P3StageUntil = st.until;
                    s.P3Staging = st.at;
                }
            }
            if (p.Scout is { } scout && Squads.Find(scout) is { } sq && now < p.ScoutUntil)
            {
                sq.P3Role = PackageRole.Scout;
                SetTask(sq, TaskKind.Secondary, ScoutPoint(world, sq.Centre, p.Target, 25f), false, false);
            }
        }

        private void AbortPackage(SimWorld world, string why)
        {
            if (_package == null) return;
            // Only an attack that had not reached its execute time is an abort; afterwards it simply ends.
            if (world.Time < _package.ExecuteAt)
            {
                _p3!.Metrics.AttackPackagesAborted++;
                P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.PackageAborted, why);
            }
            _package = null;
            _stage.Clear();
        }

        /// <summary>Spec 131: a recon squad (fast, not in the package's main / flank) or a recon vehicle outside squads goes to look; its ETA (null: none).</summary>
        private float? SendScout(SimWorld world, TeamIntel intel, AttackPackage p, Vector2 target)
        {
            Squad? best = null;
            var bestD = float.MaxValue;
            foreach (var s in Squads.Squads)
            {
                if (!s.Fast || s.IsReserve || s.MemberList.Count == 0 || s.Id == p.Main || s.Id == p.Flank) continue;
                var d = Vector2.Distance(s.Centre, target);
                if (d < bestD)
                {
                    best = s;
                    bestD = d;
                }
            }
            if (best != null)
            {
                p.Scout = best.Id;
                var at = ScoutPoint(world, best.Centre, target, 25f);
                return SyncPlanner.Eta(Vector2.Distance(best.Centre, at), Squads.SlowestP3(world, best));
            }
            Vehicle? scout = null;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Team || v.Flying || v.Def.Static || Squads.SquadOf(v.Id) != null || v.UnderPlayerControl(world.Time)) continue;
                if (CombatRoleDoctrine.BaseRole(world, v) != DoctrineRole.Recon) continue;
                var d = Vector2.Distance(v.Position, target);
                if (d < bestD)
                {
                    scout = v;
                    bestD = d;
                }
            }
            if (scout == null) return null;
            var point = ScoutPoint(world, scout.Position, target, scout.Def.VisionRange * 0.7f);
            world.Submit(new Command(CommandType.Move, Team, new[] { scout.Id }, point));
            return SyncPlanner.Eta(Vector2.Distance(scout.Position, point), scout.Def.Speed);
        }

        private static Vector2 ScoutPoint(SimWorld world, Vector2 from, Vector2 target, float standoff)
        {
            var p = world.Map.Clamp(target - Direction(from, target) * MathF.Max(10f, standoff), 6f);
            return world.Grid.IsWalkable(p) ? p : world.Map.Clamp(Vector2.Lerp(from, target, 0.6f), 6f);
        }

        /// <summary>
        /// Spec 137: a staging area outside the known enemy reach round the target (plus a band), reachable from the main
        /// effort, off chokes, passages, lanes and spawn exits, least threatened; the squads get sub-zones beside it.
        /// </summary>
        private Vector2 StagingP3(SimWorld world, TeamIntel intel, Vector2 target, Vector2 from)
        {
            var reach = 0f;
            foreach (var c in intel.Contacts)
                if (!c.Flying && Vector2.Distance(c.Position, target) <= 80f) reach = MathF.Max(reach, c.Reach);
            var distance = MathF.Max(40f, reach + Tun.AttackSync.StagingBand);
            var dir = Direction(target, from);
            var component = world.Topology.Ground.ComponentAt(from);
            Vector2? best = null;
            var bestScore = float.MaxValue;
            foreach (var k in new[] { 0, 1, -1, 2, -2 })
            {
                var angle = k * MathF.PI / 9f;
                var d = new Vector2(dir.X * MathF.Cos(angle) - dir.Y * MathF.Sin(angle), dir.X * MathF.Sin(angle) + dir.Y * MathF.Cos(angle));
                var p = world.Lanes.OffLane(world.Map.Clamp(target + d * distance, 8f), 10f);
                if (!world.Grid.IsWalkable(p) || (component > 0 && world.Topology.Ground.ComponentAt(p) != component)) continue;
                if (InChoke(world, p) || world.Traffic.InPassage(p)) continue;
                var exit = false;
                foreach (var e in world.Traffic.Exits)
                    if (e.InExitBox(p)) exit = true;
                if (exit) continue;
                var score = intel.ThreatAt(ThreatKind.AntiTank, p) + intel.ThreatAt(ThreatKind.Artillery, p) + 0.5f * Math.Abs(k);
                if (score < bestScore)
                {
                    bestScore = score;
                    best = p;
                }
            }
            return best ?? world.Map.Clamp(Vector2.Lerp(from, target, 0.5f), 8f);
        }

        private static bool InChoke(SimWorld world, Vector2 p)
        {
            foreach (var ch in world.Topology.Chokes)
                if (Vector2.Distance(ch.Centre, p) < ch.Width * 0.5f + Tun.FireMissions.ChokeMargin + 4f) return true;
            return false;
        }

        private static Vector2 Direction(Vector2 from, Vector2 to) => FrontlineModel.Dir(from, to);

        // ------------------------------------------------------------------------------------------------ 138

        private void CommittedPowerP3()
        {
            var board = _p3!.Board;
            var sums = new Dictionary<long, float>();
            foreach (var s in Squads.Squads)
                if (s.Task.Objective is { } o)
                {
                    var key = TacticalMemory.RouteKey(o, 0);
                    sums[key] = (sums.TryGetValue(key, out var v) ? v : 0f) + s.Strength;
                }
            foreach (var kv in sums) board.SetCommitted(kv.Key, kv.Value);
        }

        // ------------------------------------------------------------------------------------------------ 170

        /// <summary>
        /// Spec 170: the ranked reserve release (1 HQ / boss critical, 2 breakthrough, 3 primary objective collapse, 4 high-value
        /// exploit, 5 secondary objective), never into a fight already clearly won. Replaces P2's trigger list when P3 is on.
        /// </summary>
        private Vector2? ReserveReleaseP3(SimWorld world, TeamIntel intel, Vector2? home)
        {
            var tc = _p3!;
            var d = world.Doctrine.For(Team);
            var list = new List<ReserveCandidate>();
            void Add(int rank, Vector2 at, string code)
            {
                var (own, enemy) = intel.StrengthAround(at, 40f);
                list.Add(new ReserveCandidate(rank, at, own, enemy, code));
            }
            foreach (var e in intel.Events)
                if (e.Kind == IntelEventKind.Threat && e.Priority >= 70f && e.Confidence >= 0.5f && home is { } h && Vector2.Distance(e.Centre, h) < 60f)
                    Add(1, e.Centre, "hq");
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Team && v.Def.Boss)
                {
                    var (own, enemy) = intel.StrengthAround(v.Position, 40f);
                    if (enemy > own) Add(1, v.Position, "boss");
                }
            if (!d.ReserveEmergencyOnly)
            {
                foreach (var seg in tc.Frontline.Segments)
                {
                    if (seg.EnemyPressure <= seg.FriendlyPressure * Tun.ReserveRelease.BreakthroughRatio || home is not { } hh) continue;
                    foreach (var g in intel.EnemyGroups)
                        if (!g.Air && Vector2.Distance(g.Centre, seg.Centre) < 40f && Vector2.Dot(g.Velocity, hh - g.Centre) > 0f)
                        {
                            Add(2, seg.Centre, "breakthrough");
                            break;
                        }
                }
                foreach (var e in intel.Events)
                    if (e.Kind == IntelEventKind.Threat && e.Priority >= 70f && e.Confidence >= 0.5f)
                        foreach (var s in Squads.Squads)
                            if (!s.IsReserve && Vector2.Distance(s.Centre, e.Centre) < 50f)
                            {
                                Add(2, e.Centre, "threat on a squad");
                                break;
                            }
                if (Intent.PrimaryObjective is { } prim)
                {
                    var (own, enemy) = intel.StrengthAround(prim, 60f);
                    if (enemy > 0f && own / enemy < Tun.ReserveRelease.CollapseRatio) Add(3, prim, "primary collapse");
                }
                foreach (var e in intel.Events)
                    if (e.Kind == IntelEventKind.ObjectivePressure && e.Priority >= 75f) Add(3, e.Centre, "losing point");
                foreach (var w in tc.Windows) Add(4, w.Centre, "counterattack");
                // AI MASTER P4 spec 153 / 156: the forecast says the package in contact loses; opportunity windows to exploit.
                if (ForecastCollapseP4(world, intel) is { } collapse) Add(3, collapse, "forecast collapse");
                if (PlanningP4 is { } tp4)
                    foreach (var w in tp4.Opportunities)
                        if ((w.Roles & (OpportunityRoles.Ground | OpportunityRoles.Fast)) != 0 && w.Confidence >= Tun.ReserveRelease.ExploitConfidence) Add(4, w.Centre, "exploit " + w.Kind);
                if (Intent.PrimaryObjective is { } goal)
                    foreach (var e in intel.Events)
                        if (e.Kind == IntelEventKind.Window && e.Confidence >= Tun.ReserveRelease.ExploitConfidence && Vector2.Distance(e.Centre, goal) < 80f)
                            Add(4, e.Centre, "exploit");
                foreach (var s in Squads.Squads)
                {
                    if (s.IsReserve || s.State != SquadState.Combat) continue;
                    var (own, enemy) = intel.StrengthAround(s.Centre, MathF.Max(40f, s.Reach));
                    if (enemy > 0f && own / enemy < 0.6f) Add(5, s.Centre, "squad losing");
                }
            }
            var pick = ReserveLogic.Pick(list);
            if (pick < 0)
            {
                if (list.Count > 0 && world.Time - _keptLogAt >= 10.0)
                {
                    _keptLogAt = world.Time;
                    tc.Metrics.ReserveKeptWon++;
                    P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.ReserveKeptWon, list[0].Code);
                }
                return null;
            }
            var c = list[pick];
            if (float.IsNaN(_lastRelease.X) || Vector2.Distance(_lastRelease, c.At) > 20f)
            {
                _lastRelease = c.At;
                tc.Metrics.ReserveReleases++;
                P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.ReserveRelease, $"rank {c.Rank} {c.Code} ({c.At.X:0},{c.At.Y:0})");
            }
            return c.At;
        }

        // ------------------------------------------------------------------------------------------------ 141, 169

        private void CoverageP3(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            if (now - _coverageAt < Tun.Coverage.UpdateS - 1e-6) return;
            _coverageAt = now;
            var board = _p3!.Board;
            var aa = new List<Vehicle>();
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Team && !v.Flying && !v.Def.Static && !v.UnderPlayerControl(now) &&
                    CombatRoleDoctrine.BaseRole(world, v) == DoctrineRole.AntiAir && !world.Components.Of(v).RadarLost) aa.Add(v);
            var enemyAir = intel.EnemyComposition[(int)ForceGroup.Helicopter] + intel.EnemyComposition[(int)ForceGroup.Plane] > 0f;
            if (!enemyAir || aa.Count == 0)
            {
                foreach (var v in aa)
                {
                    v.P3CoverAt = null;
                    board.Uncover(v.Id);
                }
                return;
            }
            var worth = Tun.Coverage.AssetWorth;
            float W(int i) => i < worth.Length ? worth[i] : 1f;
            var assets = new List<(CoverageKind kind, Vector2 at, float worth)>();
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Team && v.Def.Boss) assets.Add((CoverageKind.BossCover, v.Position, W(0)));
            if (ArtilleryCentre(world) is { } guns) assets.Add((CoverageKind.ArtilleryCover, guns, W(2)));
            Squad? mainForce = null;
            foreach (var s in Squads.Squads)
                if (s.MemberList.Count > 0 && (mainForce == null || s.Strength > mainForce.Strength)) mainForce = s;
            if (mainForce != null) assets.Add((CoverageKind.MainForceCover, mainForce.Centre, W(1)));
            if (Intent.PrimaryObjective is { } obj) assets.Add((CoverageKind.ObjectiveCover, obj, W(3)));
            if (assets.Count == 0) return;
            assets.Sort((a, b) => b.worth.CompareTo(a.worth));
            var count = new int[assets.Count];
            var taken = new HashSet<int>();
            var assignment = new Dictionary<int, int>();
            // One anti-air per asset first (nearest), then the rest where worth per cover is highest: not every AA on one aircraft.
            for (var i = 0; i < assets.Count; i++)
            {
                Vehicle? best = null;
                var bestD = float.MaxValue;
                foreach (var v in aa)
                {
                    if (taken.Contains(v.Id.Value)) continue;
                    var d = Vector2.Distance(v.Position, assets[i].at);
                    if (d < bestD)
                    {
                        best = v;
                        bestD = d;
                    }
                }
                if (best == null) break;
                taken.Add(best.Id.Value);
                assignment[best.Id.Value] = i;
                count[i]++;
            }
            foreach (var v in aa)
            {
                if (taken.Contains(v.Id.Value)) continue;
                var pick = 0;
                var bestScore = float.MinValue;
                for (var i = 0; i < assets.Count; i++)
                {
                    var score = assets[i].worth / (1f + count[i]) - Vector2.Distance(v.Position, assets[i].at) / 200f;
                    if (score > bestScore)
                    {
                        bestScore = score;
                        pick = i;
                    }
                }
                assignment[v.Id.Value] = pick;
                count[pick]++;
            }
            foreach (var v in aa)
            {
                var (kind, at, _) = assets[assignment[v.Id.Value]];
                var had = board.CoverageOf(v.Id, out var oldKind, out _);
                board.Cover(v.Id, kind, at);
                v.P3CoverAt = at;
                v.P3CoverRadius = MathF.Max(10f, v.Def.Weapon.Range);
                if (!had || oldKind != kind) P3Reasons.Unit(world, v, DecisionKind.Plan, P3Reasons.CoverageAssigned, kind.ToString());
                // Spec 169: free anti-air (outside squads, idle) moves to the best coverage spot round its asset.
                if (Squads.SquadOf(v.Id) != null || v.IsMoving || v.HasPath || v.Target.IsValid || v.Order.Kind != OrderKind.Idle) continue;
                var spot = CoverageSpot(world, intel, v, at, assets, aa);
                if (Vector2.Distance(spot, v.Position) > 8f) world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, spot));
            }
        }

        /// <summary>Spec 169: CoverageScore = FriendlyValueCovered - Exposure - Congestion - RedundantCoverage over 8 spots round the asset (and here).</summary>
        private Vector2 CoverageSpot(SimWorld world, TeamIntel intel, Vehicle v, Vector2 asset, List<(CoverageKind kind, Vector2 at, float worth)> assets, List<Vehicle> aa)
        {
            var reach = MathF.Max(10f, v.Def.Weapon.Range);
            var best = v.Position;
            var bestScore = float.MinValue;
            for (var k = -1; k < 8; k++)
            {
                var p = k < 0 ? v.Position : world.Map.Clamp(asset + new Vector2(MathF.Cos(k * MathF.PI / 4f), MathF.Sin(k * MathF.PI / 4f)) * reach * Tun.Coverage.ReachShare, 6f);
                if (k >= 0 && !world.Grid.IsWalkable(p)) continue;
                var covered = 0f;
                foreach (var a in assets)
                    if (Vector2.Distance(a.at, p) <= reach) covered += a.worth;
                var exposure = (intel.ThreatAt(ThreatKind.AntiTank, p) + intel.ThreatAt(ThreatKind.Artillery, p)) / MathF.Max(1f, TeamIntel.StrengthOf(v));
                var crowd = 0;
                foreach (var o in world.VehicleList)
                    if (o != v && o.IsAlive && o.Team == Team && Vector2.DistanceSquared(o.Position, p) < 36f) crowd++;
                var redundant = 0;
                foreach (var o in aa)
                    if (o != v && Vector2.Distance(o.Position, p) < reach * 0.5f) redundant++;
                var score = covered - Tun.Coverage.ExposureWeight * exposure - Tun.Coverage.CongestionWeight * crowd - Tun.Coverage.RedundantWeight * redundant;
                if (!_p3!.Frontline.Behind(p, 0f)) score -= 2f;
                if (score > bestScore + 1e-4f)
                {
                    bestScore = score;
                    best = p;
                }
            }
            return best;
        }

        // ------------------------------------------------------------------------------------------------ 142-145

        private void CounterBatteryP3(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            var tc = _p3!;
            foreach (var e in tc.Battery.Estimates)
            {
                if (e.Confidence(now) < Tun.FireMissions.MissionConfidence || _missionLogged.Contains(e)) continue;
                _missionLogged.Add(e);
                tc.Metrics.CounterBatteryMissions++;
                P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.CounterBatteryMission, e.ToString());
            }
            if (_missionLogged.Count > 64) _missionLogged.Clear();
        }

        /// <summary>Spec 144: an unseen battery confident and tight enough for area fire (a support barrage; guns cannot fire at ground).</summary>
        private Vector2? CounterBatteryStrikeP3(SimWorld world)
        {
            if (CoordinationP3 is not { } tc) return null;
            var now = world.Time;
            var e = tc.Battery.Best(now, Tun.FireMissions.StrikeConfidence);
            if (e == null || e.ErrorRadius > Tun.FireMissions.StrikeMaxError || now - e.StruckAt < 15.0) return null;
            var intel = world.Intel.For(Team);
            foreach (var c in intel.Contacts)
                if (c.InSight && c.Artillery && Vector2.Distance(c.Position, e.Centre) <= e.ErrorRadius + 10f) return null; // seen: the guns take it
            return e.Centre;
        }

        /// <summary>Spec 142: smoke wanted at <paramref name="at"/> is already covered by a running / planned screen or cloud.</summary>
        private bool SmokeTakenP3(SimWorld world, Vector2 at, SmokePurpose purpose)
        {
            if (CoordinationP3 is not { } tc) return false;
            _smokePurpose = purpose;
            if (!tc.Board.SmokeCovered(at, world.Time, world.SmokeClouds())) return false;
            tc.Metrics.SmokeDeconflicted++;
            if (LogDue(-7, 10.0)) P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.SmokeDeconflicted, $"({at.X:0},{at.Y:0}) {purpose}");
            return true;
        }

        /// <summary>Spec 142 / 144: a support card the side's AI just used: the smoke mission is planned, the battery marked struck.</summary>
        public void NoteSupportP3(SimWorld world, SupportKind kind, Vector2 at)
        {
            NoteSupportP4(world, kind, at);
            if (CoordinationP3 is not { } tc) return;
            var now = world.Time;
            if (kind == SupportKind.Smoke)
            {
                tc.Board.PlanSmoke(new SmokeMission(at, Tun.Board.SmokeSpacing, now, now + Tun.Board.SmokeSeconds, _smokePurpose));
                P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.SmokePlanned, $"({at.X:0},{at.Y:0}) {_smokePurpose}");
                return;
            }
            foreach (var e in tc.Battery.Estimates)
                if (Vector2.Distance(e.Centre, at) < 1f)
                {
                    e.StruckAt = now;
                    tc.Metrics.CounterBatteryStrikes++;
                    P3Reasons.Commander(world, Team, DecisionKind.Plan, P3Reasons.CounterBatteryStrike, e.ToString());
                }
        }

        /// <summary>Spec 142 AssaultObjective: smoke over the approach while the package goes in against known anti-tank fire.</summary>
        private Vector2? AssaultSmokeP3(SimWorld world)
        {
            if (_package is not { } p || CoordinationP3 == null) return null;
            var now = world.Time;
            if (now < p.ExecuteAt - 2.0 || now > p.ExecuteAt + 6.0) return null;
            var mid = Vector2.Lerp(p.Staging, p.Target, 0.6f);
            return world.Intel.For(Team).ThreatAt(ThreatKind.AntiTank, mid) > 0f ? mid : (Vector2?)null;
        }

        /// <summary>
        /// Spec 143-145 for one gun outside squads (1 Hz): shoot-and-scoot after its 2-4 salvos when enemy artillery is
        /// known, or after one under a counter-battery threat (observed enemy shells landing beside it, an enemy counter-battery
        /// radar seen); the scoot spot (12-30 m) keeps out of chokes, passages, other firing reservations and stays behind the
        /// frontline. Then the fire mission scheduler: a seen enemy battery in the preferred band (counter-battery), else a
        /// near-dead seen target (finish), at most two guns a target; an Attack on a target unseen past the stale time is
        /// dropped (no barrage on a stale remembered position).
        /// </summary>
        private void ArtilleryP3(SimWorld world, TeamIntel intel, Vehicle v, bool enemyGuns)
        {
            var tc = _p3!;
            var now = world.Time;
            if (v.Def.Scoot == null)
            {
                if (!_guns.TryGetValue(v.Id, out var g)) g = (v.LastFiredAt, 0, v.Hp);
                if (v.LastFiredAt > g.lastFired) g = (v.LastFiredAt, g.shots + 1, g.hp);
                if (v.Hp < g.hp - 1f && !v.IsMoving && enemyGuns)
                {
                    _marked.Add(v.Position);
                    if (_marked.Count > MarkedKept) _marked.RemoveAt(0);
                }
                g.hp = v.Hp;
                var threat = tc.Battery.RecentImpactNear(v.Position, Tun.FireMissions.ThreatRadius, now, Tun.FireMissions.ImpactMemoryS);
                foreach (var c in intel.Contacts)
                    if (c.Unit.Contains("counter_battery") && Vector2.Distance(c.Position, v.Position) <= c.Reach + 20f) threat = true;
                var marked = Near(v.Position, 15f);
                var known = enemyGuns || tc.Battery.Best(now, 0.3f) != null;
                // AI MASTER P5 Part L: also inside a reload window that runs on the move (the scoot then costs no firing time).
                var reloadScoot = known && !threat && AmmoTactics.ScootDuringReload(AmmoTactics.Read(world, v), g.shots);
                if ((ShootAndScoot.Due(g.shots, v.Id.Value, threat, known) || (marked && g.shots > 0) || reloadScoot) && !v.IsMoving && !v.HasPath &&
                    ScootP3(world, tc, v, threat))
                {
                    g.shots = 0;
                    if (reloadScoot)
                    {
                        world.Health.Counters.ScootsDuringReload++;
                        P3Reasons.Unit(world, v, DecisionKind.Action, P5Reasons.ScootDuringReload);
                    }
                }
                _guns[v.Id] = g;
            }
            FireMissionP3(world, intel, tc, v);
        }

        private bool ScootP3(SimWorld world, TeamCoordination tc, Vehicle v, bool counterBattery)
        {
            var aim = world.TryGetVehicle(v.Target, out var target) ? target.Position : v.Position + SimMath.Forward(v.Heading) * 50f;
            var back = aim - v.Position;
            back = back.LengthSquared() > 0.01f ? -Vector2.Normalize(back) : -SimMath.Forward(v.Heading);
            var side = new Vector2(back.Y, -back.X);
            var first = ((v.Id.Value + (int)world.Time / 10) & 1) == 0 ? 1f : -1f;
            Vector2[] tries = { side * first, -side * first, Vector2.Normalize(side * first + back), back };
            var distance = ShootAndScoot.Distance(v.Id.Value);
            var w = v.Def.Weapon;
            foreach (var dir in tries)
            {
                var spot = world.Map.Clamp(v.Position + dir * distance, 6f);
                if (!world.Grid.IsWalkable(spot) || Near(spot, 15f)) continue;
                if (target != null)
                {
                    var reach = Vector2.Distance(spot, aim);
                    if (reach > RangeBands.PreferredMax(w) || reach < RangeBands.PreferredMin(w)) continue;
                }
                if (InChoke(world, spot) || world.Traffic.InPassage(spot)) continue;
                if (!tc.Frontline.Behind(spot, Tun.FireMissions.FrontMargin)) continue;
                if (world.Positions.ReservedByOther(spot, v.Id) || !world.Traffic.CanPark(spot, v)) continue;
                if (!ClaimGunP4(world, v, IntentOwner.Scoot, Tun.Ownership.ScootClaimS)) return false;
                world.Submit(new Command(CommandType.Move, Team, new[] { v.Id }, spot));
                tc.Metrics.ArtilleryScoots++;
                P3Reasons.Unit(world, v, DecisionKind.Action, counterBattery ? P3Reasons.CounterBatteryScoot : P3Reasons.Scoot, $"{distance:0} m");
                return true;
            }
            return false;
        }

        private void FireMissionP3(SimWorld world, TeamIntel intel, TeamCoordination tc, Vehicle v)
        {
            if (v.IsMoving || v.HasPath) return;
            var now = world.Time;
            if (v.Order.Kind == OrderKind.Attack && v.Order.Target.IsValid)
            {
                if (intel.Find(v.Order.Target) is { InSight: false } stale && stale.Age(now) > Tun.FireMissions.StaleSeconds && !GunHeldByOtherP4(world, v, IntentOwner.FireMission))
                {
                    world.Submit(new Command(CommandType.Stop, Team, new[] { v.Id }));
                    tc.Metrics.StaleTargetsDropped++;
                    P3Reasons.Unit(world, v, DecisionKind.Target, P3Reasons.StaleTarget, $"#{stale.Id.Value} unseen {stale.Age(now):0} s");
                }
                return;
            }
            var w = v.Def.Weapon;
            float max = RangeBands.PreferredMax(w), min = RangeBands.PreferredMin(w);
            Contact? pick = null;
            var finish = false;
            var bestD = float.MaxValue;
            for (var pass = 0; pass < 2 && pick == null; pass++)
                foreach (var c in intel.Contacts)
                {
                    if (!c.InSight || c.Flying) continue;
                    var d = Vector2.Distance(c.Position, v.Position);
                    if (d > max || d < min || d >= bestD) continue;
                    if (tc.Board.MissionGuns(c.Id.Value, now) >= Tun.FireMissions.MaxGunsPerTarget && !tc.Board.OnMission(c.Id.Value, v.Id, now)) continue;
                    if (pass == 0 && !c.Artillery) continue;
                    if (pass == 1)
                    {
                        if (!world.TryGetVehicle(c.Id, out var t) || t.Hp > t.MaxHp * Tun.Board.NearKillShare) continue;
                        if (tc.Board.PlannedDamage(c.Id, v.Id, now) >= t.Hp) continue;
                    }
                    pick = c;
                    finish = pass == 1;
                    bestD = d;
                }
            if (pick == null) return;
            // AI MASTER P4 (P3 leftover a): one owner orders a gun at a time; the mission owns it while it runs.
            if (!ClaimGunP4(world, v, IntentOwner.FireMission, Tun.Ownership.MissionClaimS)) return;
            world.Submit(new Command(CommandType.Attack, Team, new[] { v.Id }, pick.Position, pick.Id));
            tc.Board.AssignMission(pick.Id.Value, v.Id, now + 10.0);
            P3Reasons.Unit(world, v, DecisionKind.Target, finish ? P3Reasons.FinishMission : P3Reasons.CounterBatteryMission, $"#{pick.Id.Value}");
        }
    }
}
