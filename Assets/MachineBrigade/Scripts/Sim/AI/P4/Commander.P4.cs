#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Spec 132-133: a squad's part in a probe or a feint.</summary>
    public enum P4Role : byte
    {
        None,
        Probe,
        Feint,
    }

    /// <summary>
    /// AI MASTER P4 (lane A), the commander's advanced-planning pass, once a second right after P3's coordination: the
    /// short-horizon combat forecast and the shallow counterfactual plans on the attack package (152-154), plan validity
    /// dependencies, abort before contact, interrupt / replan and commitment windows (155, 182-184), plan anti-repetition and
    /// same-match adaptation (157-158, Part M), opportunity windows (156), probe-and-exploit (132) and the conditional feint
    /// (133). Fog-fair: the side's intel, memory and own units only. Deterministic: squads in list / id order, hashes, no
    /// Random. Off with ai.planning.enabled = false (P3 behaviour exactly).
    /// </summary>
    public sealed partial class AiCommander
    {
        private TeamPlanning? _p4;
        private PlanRecord? _plan;
        private double _planHoldUntil = double.NegativeInfinity;
        private Vector2 _holdFor;
        private ProbeState? _probe;
        private FeintState? _feint;
        private double _probeReadyAt, _feintReadyAt, _feintRejectLogAt = double.NegativeInfinity;
        private bool _adaptAir, _adaptCamp, _adaptTowers, _adaptRecon;
        private bool _enough;
        private double _enoughSince = double.NaN, _phaseReserveSince = double.NaN;
        private int _weakpointLogged = -1;
        private double _warnTriggeredDue = double.NaN;

        private sealed class PlanRecord
        {
            public double PackageCreated;
            public Vector2 Target;
            public PlanKind Kind;
            public int FlankSide;
            public PlanDependencies Deps;
            public double ChosenAt;
            public float CommitS;
            public float StartStrength, StartEnemy;
            public long Key;
            public bool Executed;
            public readonly List<int> MemberIds = new();
        }

        private sealed class ProbeState
        {
            public int Squad, Side;
            public Vector2 Point;
            public long Lane;
            public double Start, ProgressAt;
            public float StartStrength, Best;
        }

        private sealed class FeintState
        {
            public int Squad;
            public Vector2 At, Main;
            public double Start, SuccessAt = double.NaN;
            public float MainBefore, FeintBefore;
        }

        /// <summary>The side's P4 planning state (null until the first look, or with ai.planning / ai.coordination off).</summary>
        public TeamPlanning? PlanningP4 => Tun.Planning.Enabled && Tun.Coordination.Enabled ? _p4 : null;

        /// <summary>The difficulty level the advanced gating reads (spec 216).</summary>
        internal int Level => Skill.Level;

        private void PlanP4(SimWorld world, TeamIntel intel)
        {
            if (!Tun.Planning.Enabled || CoordinationP3 is not { } tc) return;
            _p4 ??= tc.Planning;
            _p4.Update(intel, Intent.PrimaryObjective, tc);
            _p4.ObserveWarnings(intel.Warnings, world.Time);
            if (DifficultyGate.Adaptation(Level)) AdaptP4(world, intel);
            PackagePlanP4(world, intel);
            ProbeP4(world, intel);
            FeintP4(world, intel);
            EnoughP4(world, intel);
            WeakpointLogP4(world, intel);
        }

        // ------------------------------------------------------------------------------------------------ 152 forecast inputs

        private static float WeaponDps(WeaponDef w) => w.Damage <= 0f ? 0f : w.Damage * Math.Max(1, w.RoundsPerCycle) / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.WeaponDpsCycleSecondsFloor, w.CycleSeconds);

        private readonly List<(VehicleDef def, float hp, float strength, bool flying)> _ownUnits = new(), _enemyUnits = new(), _reinforceUnits = new();
        private readonly float[] _levelsOwn = new float[ArmourLevels.Max + 1], _levelsEnemy = new float[ArmourLevels.Max + 1], _levelsReinforce = new float[ArmourLevels.Max + 1];

        /// <summary>The hp-weighted armour mix (front levels) of a force (normalised), and its air share.</summary>
        private static float Profile(List<(VehicleDef def, float hp, float strength, bool flying)> units, float[] levels)
        {
            Array.Clear(levels, 0, levels.Length);
            float all = 0f, air = 0f;
            foreach (var u in units)
            {
                all += u.hp;
                if (u.flying)
                {
                    air += u.hp;
                    continue;
                }
                levels[Math.Clamp(u.def.Armour.Front, 0, levels.Length - 1)] += u.hp;
            }
            var ground = all - air;
            for (var i = 0; i < levels.Length; i++) levels[i] = ground > 0f ? levels[i] / ground : 0f;
            return all > 0f ? air / all : 0f;
        }

        /// <summary>Spec 152 inputs of one side against the other's armour mix: hit points, damage a second (armour / penetration), reach, speed, splash.</summary>
        private static ForceEstimate Estimate(SimWorld world, List<(VehicleDef def, float hp, float strength, bool flying)> units, float[] targetLevels, float targetAir)
        {
            var e = new ForceEstimate { Speed = float.MaxValue };
            float splash = 0f, reachW = 0f, air = 0f;
            var damage = world.Catalog.Damage;
            foreach (var u in units)
            {
                e.Hp += u.hp;
                e.Strength += u.strength;
                e.Count++;
                if (u.flying) air += u.hp;
                else e.Speed = MathF.Min(e.Speed, MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.EstimateSpeedFloor, u.def.Speed));
                var reach = 0f;
                var mounts = u.def.Mounts;
                var n = mounts.Count > 0 ? mounts.Count : 1;
                for (var k = 0; k < n; k++)
                {
                    var w = mounts.Count > 0 ? mounts[k].Weapon : u.def.Weapon;
                    var dps = WeaponDps(w);
                    if (dps <= 0f) continue;
                    if (w.CanTarget(false))
                    {
                        var eff = 0f;
                        for (var l = 0; l < targetLevels.Length; l++)
                            if (targetLevels[l] > 0f) eff += targetLevels[l] * damage.Effective(w, l, TargetKind.Ground);
                        e.DpsGround += dps * eff;
                        reach = MathF.Max(reach, w.Range);
                        if (w.SplashRadius > global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.EstimateSplashRadiusMin) splash += dps * eff;
                    }
                    if (w.CanTarget(true) && targetAir > 0f) e.DpsAir += dps * damage.Effective(w, 1, TargetKind.Air);
                }
                reachW += reach * u.hp;
            }
            if (e.Hp > 0f)
            {
                e.AirShare = air / e.Hp;
                e.Reach = reachW / e.Hp;
            }
            if (e.Speed == float.MaxValue) e.Speed = global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.EstimateSpeed;
            e.SplashShare = e.DpsGround + e.DpsAir > 0f ? Math.Clamp(splash / (e.DpsGround + e.DpsAir), 0f, 1f) : 0f;
            return e;
        }

        /// <summary>A known contact as the forecast counts it (its def's armour and weapons are public; hp from its seen strength).</summary>
        private static bool ContactUnit(SimWorld world, Contact c, out (VehicleDef def, float hp, float strength, bool flying) unit)
        {
            unit = default;
            if (!world.Catalog.Vehicles.TryGetValue(c.Unit, out var def)) return false;
            var hp = def.Boss ? c.Strength * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ContactUnitStrengthScale : def.Power > 0f ? def.MaxHp * Math.Clamp(c.Strength / def.Power, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ContactUnitStrengthMin, 1f) : def.MaxHp;
            unit = (def, hp, c.Strength, c.Flying);
            return true;
        }

        private static (VehicleDef def, float hp, float strength, bool flying) OwnUnit(Vehicle v) => (v.Def, v.Hp, TeamIntel.StrengthOf(v), v.Flying);

        /// <summary>
        /// Spec 152 / 222: the forecast of the package's squads against the known enemy round the target, with the guns in
        /// reach as support, repair near, the unknown-ground margin and (depth 2) the known enemy groups that can join.
        /// </summary>
        private void ForcesFor(SimWorld world, TeamIntel intel, IReadOnlyList<Squad> members, Vector2 target, out ForceEstimate own, out ForceEstimate enemy,
            out ForceEstimate reinforcement, out float distance)
        {
            var now = world.Time;
            _ownUnits.Clear();
            _enemyUnits.Clear();
            _reinforceUnits.Clear();
            distance = 0f;
            var centre = Vector2.Zero;
            foreach (var s in members)
            {
                distance += Vector2.Distance(s.Centre, target);
                centre += s.Centre;
                foreach (var id in s.MemberList)
                    if (world.TryGetVehicle(id, out var v) && v.IsAlive) _ownUnits.Add(OwnUnit(v));
            }
            if (members.Count > 0)
            {
                distance /= members.Count;
                centre /= members.Count;
            }
            foreach (var c in intel.Contacts)
            {
                if (c.Age(now) > global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForcesForAgeMin || c.Displaced) continue;
                var d = Vector2.Distance(c.Position, target);
                if (d > Tun.Forecast.ReinforceRadius) continue;
                if (!ContactUnit(world, c, out var u)) continue;
                if (d <= global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForcesForDMax) _enemyUnits.Add(u);
                else _reinforceUnits.Add(u);
            }
            var ownAir = Profile(_ownUnits, _levelsOwn);
            var enemyAir = Profile(_enemyUnits, _levelsEnemy);
            Profile(_reinforceUnits, _levelsReinforce);
            own = Estimate(world, _ownUnits, _levelsEnemy, enemyAir);
            enemy = Estimate(world, _enemyUnits, _levelsOwn, ownAir);
            reinforcement = Estimate(world, _reinforceUnits, _levelsOwn, ownAir);
            // Support: the side's guns (outside the package) that reach the target; repair auras near the package.
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Team || v.Def.Static) continue;
                if (v.Def.Weapon.MinRange > 0f && Vector2.Distance(v.Position, target) <= v.Def.Weapon.Range)
                {
                    var eff = 0f;
                    for (var l = 0; l < _levelsEnemy.Length; l++)
                        if (_levelsEnemy[l] > 0f) eff += _levelsEnemy[l] * world.Catalog.Damage.Effective(v.Def.Weapon, l, TargetKind.Ground);
                    own.SupportDps += WeaponDps(v.Def.Weapon) * eff;
                }
                if (v.Def.RepairAura is { } aura && members.Count > 0 && Vector2.Distance(v.Position, centre) <= global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForcesForDistanceMax && own.Count > 0)
                    own.RepairPerS += aura.Rate * own.Hp / own.Count;
            }
            // Unknown ground round the cluster: the enemy may be more than is seen (spec 130 / 152 "local threat").
            if (CoordinationP3 is { } tc && tc.Memory.UnknownShare(intel, target, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForcesForRadius, now) >= global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForcesForUnknownShareMin) enemy = enemy.Scaled(Tun.Forecast.UnknownMargin);
        }

        private long ForecastKey(PlanKind kind, int side, Vector2 target, float distance, in ForceEstimate own, in ForceEstimate enemy)
        {
            unchecked
            {
                long h = (long)kind * 31 + side + 1;
                h = h * 1000003L + (long)MathF.Floor(target.X / 10f) * 7919L + (long)MathF.Floor(target.Y / 10f);
                h = h * 1000003L + (long)MathF.Floor(distance / global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForecastKeyDistanceDivisor);
                h = h * 1000003L + own.Count * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForecastKeyCountScale + (long)MathF.Round(own.Hp / global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForecastKeyHpDivisor);
                return h * 1000003L + enemy.Count * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForecastKeyCountScale + (long)MathF.Round(enemy.Hp / global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForecastKeyHpDivisor);
            }
        }

        private CombatForecast CachedForecast(long key, Func<CombatForecast> compute)
        {
            var now = _world!.Time;
            if (_p4!.TryForecast(key, now, out var f)) return f;
            f = compute();
            _p4.StoreForecast(key, now, f);
            return f;
        }

        // ------------------------------------------------------------------------------------------------ 154 plans

        private List<Squad> PackageSquadsP4(AttackPackage p)
        {
            var list = new List<Squad>();
            foreach (var s in Squads.Squads)
                if (p.Members.Contains(s.Id) && s.MemberList.Count > 0) list.Add(s);
            return list;
        }

        private List<Squad> PrimaryMembersP4()
        {
            var members = new List<Squad>();
            foreach (var s in Squads.Squads)
                if (s.Task.Kind == TaskKind.Primary && !s.Task.Hold && !s.IsReserve && s.MemberList.Count > 0) members.Add(s);
            return members;
        }

        private float OpportunityGain(Vector2 at, OpportunityRoles roles)
        {
            var w = _p4!.WindowNear(at, roles, 20f);
            return w == null ? 0f : Tun.Opportunity.PlanGain * w.Confidence;
        }

        /// <summary>Spec 154: the candidate plans (2-4 by difficulty), each one forecast and scored.</summary>
        private List<PlanCandidate> EvaluatePlans(SimWorld world, TeamIntel intel, AttackPackage p, List<Squad> squads)
        {
            var now = world.Time;
            var tc = CoordinationP3!;
            var tp = _p4!;
            var target = p.Target;
            var plans = new List<PlanCandidate>();
            ForcesFor(world, intel, squads, target, out var own, out var enemy, out var reinforcement, out var distance);
            var horizon = Tun.Forecast.Seconds;
            var deep = DifficultyGate.Depth(Level) >= 2;
            var main = squads.Find(s => s.Id == p.Main) ?? (squads.Count > 0 ? squads[0] : null);
            var from = main?.Centre ?? target;
            var speed = main != null ? MathF.Max(1f, Squads.SlowestP3(world, main)) : global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.EvaluatePlansMainFalse;
            var count = ShallowPlanner.Count(Level);
            CombatForecast Run(PlanKind kind, int side, float fScale, float eUptime, float preLoss, float dist) =>
                CachedForecast(ForecastKey(kind, side, target, dist, own, enemy), () =>
                {
                    var f = CombatForecaster.Forecast(own, enemy, horizon, dist, fScale, eUptime, preLoss);
                    return deep ? CombatForecaster.Deepen(f, own, enemy, reinforcement, horizon) : f;
                });
            var ground = OpportunityRoles.Ground | OpportunityRoles.Fast;
            for (var i = 0; i < count; i++)
            {
                var kind = ShallowPlanner.Kind(i);
                var penalty = tp.Repetition.Penalty(RepetitionMemory.Key(kind, target), now);
                switch (kind)
                {
                    case PlanKind.AttackNow:
                    {
                        var lane = tp.Lane(TeamPlanning.LaneKey(target, 0), now);
                        var f = Run(kind, 0, 1f, 1f, 0f, distance);
                        var gain = OpportunityGain(target, ground) + (lane == LaneState.Exploit ? Tun.Opportunity.PlanGain : 0f);
                        plans.Add(ShallowPlanner.Score(kind, f, own.Strength, enemy.Strength, 0f, _urgency, tc.Routes.Occupancy(Vector2.Lerp(from, target, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.EvaluatePlansFromLerp), -1, now),
                            tc.Memory.UnknownAlong(intel, from, target, now) + (lane == LaneState.Hot ? global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.EvaluatePlansLaneTrue : 0f), gain, penalty, lane != LaneState.Blocked));
                        break;
                    }
                    case PlanKind.Flank:
                    {
                        PlanCandidate? best = null;
                        if (main != null)
                            for (var side = -1; side <= 1; side += 2)
                            {
                                if (!Squads.FlankPointP3(world, intel, main, target, side, out var fp)) continue;
                                var lane = tp.Lane(TeamPlanning.LaneKey(target, side), now);
                                var extra = MathF.Max(0f, Vector2.Distance(from, fp) + Vector2.Distance(fp, target) - Vector2.Distance(from, target));
                                var f = Run(kind, side, Tun.Planning.FlankDpsBonus, Tun.Planning.FlankEnemyUptime, 0f, distance + extra);
                                var gain = OpportunityGain(fp, ground) + (lane == LaneState.Exploit ? Tun.Opportunity.PlanGain : 0f);
                                var c = ShallowPlanner.Score(kind, f, own.Strength, enemy.Strength, extra / speed, _urgency, tc.Routes.Occupancy(fp, -1, now),
                                    tc.Memory.UnknownAlong(intel, from, fp, now) + (lane == LaneState.Hot ? global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.EvaluatePlansLaneTrue : 0f), gain, penalty, lane != LaneState.Blocked, side);
                                if (best == null || (c.Valid && (!best.Value.Valid || c.Utility > best.Value.Utility + 1e-4f))) best = c;
                            }
                        plans.Add(best ?? new PlanCandidate { Kind = kind, Valid = false });
                        break;
                    }
                    case PlanKind.WaitArtillery:
                    {
                        var barrage = BarrageReadyP4(world);
                        var support = own.SupportDps;
                        if (support <= 0f && barrage) support = own.DpsGround * 0.25f + 1f;
                        var pre = MathF.Min(enemy.Hp, support * Tun.Planning.WaitArtilleryS);
                        var f = CachedForecast(ForecastKey(kind, 0, target, distance, own, enemy), () =>
                        {
                            var g = CombatForecaster.Forecast(own, enemy, horizon, distance, 1f, 1f, pre);
                            return deep ? CombatForecaster.Deepen(g, own, enemy, reinforcement, horizon) : g;
                        });
                        // A probe found the lanes hot (anti-tank / ambush): the guns first is what spec 132 asks for.
                        var hot = tp.Lane(TeamPlanning.LaneKey(target, -1), now) == LaneState.Hot || tp.Lane(TeamPlanning.LaneKey(target, 0), now) == LaneState.Hot ||
                                  tp.Lane(TeamPlanning.LaneKey(target, 1), now) == LaneState.Hot;
                        plans.Add(ShallowPlanner.Score(kind, f, own.Strength, enemy.Strength, Tun.Planning.WaitArtilleryS, _urgency, 0f,
                            tc.Memory.UnknownAlong(intel, from, target, now), OpportunityGain(target, ground) + (hot ? Tun.Opportunity.PlanGain * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.EvaluatePlansPlanGainScale : 0f), penalty, support > 0f));
                        break;
                    }
                    case PlanKind.SplitHold:
                        plans.Add(ShallowPlanner.Score(kind, CombatForecast.None, own.Strength, enemy.Strength, horizon * 2f, _urgency, 0f, 0f, 0f, penalty,
                            _urgency < Tun.Pursuit.UrgencyDrop));
                        break;
                }
            }
            tp.Metrics.PlansEvaluated++;
            return plans;
        }

        private bool BarrageReadyP4(SimWorld world)
        {
            if (!world.TryGetEconomy(Team, out var economy)) return false;
            foreach (var id in economy.Supports)
                if (world.Catalog.Supports.TryGetValue(id, out var s) && s.Kind == SupportKind.Barrage) return true;
            return false;
        }

        private bool SeadMeansP4(SimWorld world)
        {
            if (!world.TryGetEconomy(Team, out var economy)) return false;
            foreach (var id in economy.Supports)
                if (world.Catalog.Supports.TryGetValue(id, out var s) && s.Kind == SupportKind.Sead) return true;
            return false;
        }

        /// <summary>Spec 183: what the package rests on now.</summary>
        private PlanDependencies DepsP4(SimWorld world, TeamIntel intel, AttackPackage p)
        {
            var now = world.Time;
            var route = _p4!.LaneVersion * 7919 + world.Grid.Version;
            int objective;
            unchecked
            {
                objective = ((int)MathF.Floor(p.Target.X / 15f) * 397 ^ (int)MathF.Floor(p.Target.Y / 15f)) * 31 + PointOwner(world, p.Target);
            }
            var sum = Vector2.Zero;
            var strength = 0f;
            foreach (var c in intel.Contacts)
            {
                if (c.Age(now) > global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.DepsP4AgeMin || c.Flying || Vector2.Distance(c.Position, p.Target) > global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.DepsP4DistanceMin) continue;
                sum += c.Position * c.Strength;
                strength += c.Strength;
            }
            var centre = strength > 0f ? sum / strength : p.Target;
            bool guns = false, air = false;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Team || v.Def.Static) continue;
                if (!v.Flying && v.Def.Weapon.MinRange > 0f && Vector2.Distance(v.Position, p.Target) <= v.Def.Weapon.Range) guns = true;
                if (v.Flying && v.Def.Weapon.Damage > 0f) air = true;
            }
            return new PlanDependencies(route, objective, centre, strength, guns || BarrageReadyP4(world), air);
        }

        private void PackagePlanP4(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            var tp = _p4!;
            // A forecast hold in force (plan D): the primary squads hold until it runs out (never under an emergency objective).
            if (_planHoldUntil > now)
            {
                if (Intent.PrimaryObjective is { } ht && Vector2.Distance(ht, _holdFor) < global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.PackagePlanP4DistanceMax && _urgency < Tun.Pursuit.UrgencyDrop)
                {
                    foreach (var s in PrimaryMembersP4()) SetTask(s, s.Task.Kind, s.Task.Objective, true, s.Task.Window, s.Task.FlankSide);
                    return;
                }
                _planHoldUntil = now;
            }
            if (_planHoldUntil > double.NegativeInfinity && now >= _planHoldUntil)
            {
                _planHoldUntil = double.NegativeInfinity;
                if (!float.IsNaN(_packageDoneFor.X) && Vector2.Distance(_packageDoneFor, _holdFor) < global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.PackagePlanP4DistanceMax) _packageDoneFor = new Vector2(float.NaN, float.NaN);
            }
            if (_plan != null && (_package == null || _package.CreatedAt != _plan.PackageCreated))
            {
                JudgePlanP4(world, intel, _plan);
                _plan = null;
            }
            if (_package is not { } p) return;
            var squads = PackageSquadsP4(p);
            var inCombat = squads.Exists(s => s.State == SquadState.Combat);
            var beforeContact = now < p.ExecuteAt || !inCombat;
            if (_plan == null)
            {
                ChoosePlanP4(world, intel, p, squads, null, ReplanTrigger.None);
                return;
            }
            if (!beforeContact)
            {
                if (!_plan.Executed) Cue(world, "attack_go", p.Target, p.Main);
                _plan.Executed = true;
                ReapplyPlanP4(world, p, false);
                return;
            }
            // Spec 155 / 183: abort before contact when an important dependency broke (never for one unit's health).
            var deps = DepsP4(world, intel, p);
            var broken = PlanDependencies.Broken(_plan.Deps, deps, _plan.Kind);
            var mainLost = !squads.Exists(s => s.Id == p.Main);
            var flankBlocked = _plan.Kind == PlanKind.Flank &&
                               ((p.Flank is { } fid && Squads.Find(fid) is not { MemberList: { Count: > 0 } }) || tp.Lane(TeamPlanning.LaneKey(p.Target, _plan.FlankSide), now) == LaneState.Blocked);
            var supportFailed = _plan.Kind == PlanKind.WaitArtillery && _plan.Deps.Artillery && !deps.Artillery;
            var abort = AbortRules.Check(true, broken, mainLost, flankBlocked, supportFailed);
            if (abort != null)
            {
                tp.Metrics.PackageAbortsP4++;
                // A plan whose assumption broke because the enemy proved stronger is remembered (lightly) as a failure.
                if (abort == P4Reasons.DepEnemyRise || abort == P4Reasons.AbortFlankBlocked) tp.Repetition.Fail(_plan.Key, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.PackagePlanP4Severity, now);
                P4Reasons.Commander(world, Team, DecisionKind.Plan, abort, $"{_plan.Kind} deps {_plan.Deps.Hash:x8} -> {deps.Hash:x8}");
                AbortPackage(world, abort);
                _plan = null;
                return;
            }
            // Spec 182: an interrupt re-scores the plans now; otherwise only once the commitment window ran out (spec 184).
            var trigger = TriggerP4(world, intel, p, deps);
            if (trigger != ReplanTrigger.None || !CommitmentWindows.Holds(_plan.ChosenAt, now, _plan.CommitS, false))
                ChoosePlanP4(world, intel, p, squads, _plan, trigger);
            else ReapplyPlanP4(world, p, false);
        }

        /// <summary>Spec 182: a significant change (target cluster gone, a new lethal warning on the package, support lost); small changes are none.</summary>
        private ReplanTrigger TriggerP4(SimWorld world, TeamIntel intel, AttackPackage p, in PlanDependencies deps)
        {
            var now = world.Time;
            if (_plan!.Deps.ClusterStrength > 0f && deps.ClusterStrength <= 0.01f) return ReplanTrigger.TargetDead;
            if (_plan.Deps.Artillery && !deps.Artillery) return ReplanTrigger.SupportLost;
            foreach (var w in intel.Warnings)
            {
                if (w.Team == Team || w.Due < now) continue;
                var pad = w.Radius + Tun.PackageAbort.LethalWarningPad;
                var hit = Vector2.Distance(w.Centre, p.Staging) <= pad;
                if (!hit)
                    foreach (var s in Squads.Squads)
                        if (p.Members.Contains(s.Id) && Vector2.Distance(w.Centre, s.Centre) <= pad + s.Spread)
                        {
                            hit = true;
                            break;
                        }
                if (!hit || w.Due == _warnTriggeredDue) continue;
                _warnTriggeredDue = w.Due;
                // The package does not go into a telegraphed blow: its execute time waits for the warning to land.
                if (p.ExecuteAt < w.Due + 1.0) p.ExecuteAt = w.Due + 1.0;
                return ReplanTrigger.LethalWarning;
            }
            return ReplanTrigger.None;
        }

        private void ChoosePlanP4(SimWorld world, TeamIntel intel, AttackPackage p, List<Squad> squads, PlanRecord? current, ReplanTrigger trigger)
        {
            var now = world.Time;
            var tp = _p4!;
            var plans = EvaluatePlans(world, intel, p, squads);
            var currentIndex = current == null ? -1 : plans.FindIndex(c => c.Kind == current.Kind);
            var pick = ShallowPlanner.Pick(plans, trigger == ReplanTrigger.None ? currentIndex : -1);
            if (pick < 0)
            {
                if (current != null) ReapplyPlanP4(world, p, false);
                return;
            }
            var chosen = plans[pick];
            if (trigger != ReplanTrigger.None)
            {
                tp.Metrics.Replans++;
                P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.Replan, $"{trigger}: {chosen}");
            }
            if (current != null && current.Kind == chosen.Kind && current.FlankSide == chosen.FlankSide)
            {
                current.ChosenAt = now;
                ReapplyPlanP4(world, p, false);
                return;
            }
            if (current != null) tp.Metrics.PlanSwitches++;
            var rec = new PlanRecord
            {
                PackageCreated = p.CreatedAt,
                Target = p.Target,
                Kind = chosen.Kind,
                FlankSide = chosen.FlankSide,
                Deps = DepsP4(world, intel, p),
                ChosenAt = now,
                CommitS = CommitmentWindows.Seconds(Tun.Commitment.PackageS, p.Main, (int)(p.CreatedAt * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ChoosePlanP4CreatedAtScale)),
                Key = RepetitionMemory.Key(chosen.Kind, p.Target),
            };
            foreach (var s in squads)
            {
                rec.StartStrength += s.Strength;
                rec.MemberIds.Add(s.Id);
            }
            rec.StartEnemy = rec.Deps.ClusterStrength;
            _plan = rec;
            var detail = new System.Text.StringBuilder();
            foreach (var c in plans) detail.Append(detail.Length > 0 ? " | " : "").Append(c.ToString());
            if (chosen.RepeatPenalty > 0.01f) tp.Metrics.RepeatPenalised++;
            P4Reasons.Commander(world, Team, DecisionKind.Plan, chosen.Kind == PlanKind.SplitHold ? P4Reasons.PlanHold : P4Reasons.PlanChosen,
                $"{chosen.Kind} of [{detail}] commit {rec.CommitS:0.0} s");
            ApplyPlanP4(world, intel, p, squads, chosen);
        }

        /// <summary>Spec 154: the plan turns into the P3 package's shape (frontal, fix-and-flank, artillery wait) or a hold.</summary>
        private void ApplyPlanP4(SimWorld world, TeamIntel intel, AttackPackage p, List<Squad> squads, in PlanCandidate plan)
        {
            var now = world.Time;
            switch (plan.Kind)
            {
                case PlanKind.AttackNow:
                    p.Flank = null;
                    p.Fix = null;
                    p.FlankSide = 0;
                    break;
                case PlanKind.Flank:
                {
                    p.FlankSide = plan.FlankSide;
                    Squad? best = null;
                    var bestCost = float.MaxValue;
                    foreach (var s in squads)
                    {
                        if (s.Id == p.Main || !Squads.FlankPointP3(world, intel, s, p.Target, plan.FlankSide, out var fp)) continue;
                        var cost = Vector2.Distance(s.Centre, fp) - (s.Fast ? global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ApplyPlanP4FastTrue : 0f);
                        if (cost < bestCost)
                        {
                            bestCost = cost;
                            best = s;
                        }
                    }
                    if (best != null)
                    {
                        p.Flank = best.Id;
                        p.Fix = p.Main;
                        _stage.Remove(best.Id);
                    }
                    else
                    {
                        // One squad: the main effort itself goes round (its task's flank side, kept each look).
                        p.Flank = null;
                        p.Fix = null;
                    }
                    Cue(world, "flank", p.Target, best?.Id ?? p.Main);
                    break;
                }
                case PlanKind.WaitArtillery:
                {
                    var delay = MathF.Max((float)(p.ExecuteAt - now), Tun.Planning.WaitArtilleryS);
                    p.ExecuteAt = now + delay;
                    p.ArtilleryPrep = true;
                    var keys = new List<int>(_stage.Keys);
                    keys.Sort();
                    foreach (var id in keys)
                    {
                        var st = _stage[id];
                        if (p.Flank == id) continue;
                        var stage = SyncPlanner.StageSeconds(delay, st.eta);
                        _stage[id] = (stage > 0f ? now + stage : st.until, st.at, st.eta);
                    }
                    break;
                }
                case PlanKind.SplitHold:
                    _planHoldUntil = now + (_plan?.CommitS ?? global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ApplyPlanP4CommitSDefault);
                    _holdFor = p.Target;
                    _p4!.Metrics.PlanHolds++;
                    AbortPackage(world, P4Reasons.PlanHold);
                    _packageDoneFor = _holdFor;
                    _plan = null;
                    foreach (var s in PrimaryMembersP4()) SetTask(s, s.Task.Kind, s.Task.Objective, true, s.Task.Window, s.Task.FlankSide);
                    return;
            }
            ReapplyPlanP4(world, p);
        }

        /// <summary>Re-applies the package's roles after a P4 change (P3 applied them earlier in this look).</summary>
        private void ReapplyPlanP4(SimWorld world, AttackPackage p, bool full = true)
        {
            if (full)
            {
                var intel = world.Intel.For(Team);
                foreach (var s in Squads.Squads)
                    if (p.Members.Contains(s.Id))
                    {
                        s.P3Role = PackageRole.None;
                        s.P3StageUntil = double.NegativeInfinity;
                    }
                var members = PrimaryMembersP4();
                if (members.Count > 0) ApplyPackage(world, intel, members);
            }
            if (_plan is { Kind: PlanKind.Flank } rec && p.Flank == null && rec.FlankSide != 0 && Squads.Find(p.Main) is { } main)
                SetTask(main, main.Task.Kind, main.Task.Objective, main.Task.Hold, main.Task.Window, rec.FlankSide);
        }

        /// <summary>Spec 158: a package that ended: taken / enemy gutted = success; heavy losses with the enemy still there = a failure remembered.</summary>
        private void JudgePlanP4(SimWorld world, TeamIntel intel, PlanRecord rec)
        {
            if (!rec.Executed) return;
            var now = world.Time;
            var tp = _p4!;
            var (_, enemy) = intel.StrengthAround(rec.Target, 60f);
            var strength = 0f;
            foreach (var id in rec.MemberIds)
                if (Squads.Find(id) is { } s) strength += s.Strength;
            var lost = rec.StartStrength > 0f ? 1f - strength / rec.StartStrength : 0f;
            var taken = PointOwner(world, rec.Target) == Team || enemy <= rec.StartEnemy * 0.4f;
            var lane = TeamPlanning.LaneKey(rec.Target, rec.Kind == PlanKind.Flank ? rec.FlankSide : 0);
            if (taken)
            {
                tp.Adaptation.RouteResult(lane, true);
                P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.PlanSucceeded, $"{rec.Kind} lost {lost:0%}");
                return;
            }
            if (lost < 0.3f && enemy < rec.StartEnemy * 0.8f) return;
            tp.Adaptation.RouteResult(lane, false);
            tp.Repetition.Fail(rec.Key, Math.Clamp(lost / global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.JudgePlanP4LostDivisor, 0f, 1f), now);
            tp.Metrics.PlanFailures++;
            P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.PlanFailed, $"{rec.Kind} lost {lost:0%}, enemy {enemy:0.0} of {rec.StartEnemy:0.0}");
        }

        // ------------------------------------------------------------------------------------------------ 153 forecast usage

        /// <summary>Spec 153 "release reserve": the package in contact is forecast to lose the fight: a rank-3 reserve candidate at the target.</summary>
        private Vector2? ForecastCollapseP4(SimWorld world, TeamIntel intel)
        {
            if (PlanningP4 == null || _package is not { } p || _plan is not { Executed: true }) return null;
            var squads = PackageSquadsP4(p);
            if (squads.Count == 0) return null;
            ForcesFor(world, intel, squads, p.Target, out var own, out var enemy, out _, out _);
            var f = CachedForecast(ForecastKey(PlanKind.AttackNow, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ForecastCollapseP4Side, p.Target, 0f, own, enemy), () => CombatForecaster.Forecast(own, enemy, Tun.Forecast.Seconds, 0f));
            if (f.FriendlyPowerAfter >= Tun.Planning.HoldPowerFloor || f.EnemyPowerAfter < 0.5f) return null;
            if (LogDue(0x4E2, 10.0)) P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.ReserveForecast, f.ToString());
            return p.Target;
        }

        /// <summary>Spec 153 "support need" and Part M: the support card the P4 layer wants (SEAD for an air package, a barrage on a camping battery or for plan B).</summary>
        private (SupportKind kind, Vector2 at)? SupportWantedP4(SimWorld world)
        {
            if (PlanningP4 is not { } tp || CoordinationP3 is not { } tc) return null;
            var now = world.Time;
            if (_seadWanted is { } sead && now - _seadWantedAt < global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.SupportWantedP4NowMax && SeadMeansP4(world)) return (SupportKind.Sead, sead);
            if (!BarrageReadyP4(world)) return null;
            if (DifficultyGate.Adaptation(Level) && tp.Adaptation.ArtilleryCamping && tc.Battery.Best(now, Tun.FireMissions.StrikeConfidence * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.SupportWantedP4StrikeConfidenceScale) is { } e &&
                e.ErrorRadius <= Tun.FireMissions.StrikeMaxError * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.SupportWantedP4StrikeMaxErrorScale && now - e.StruckAt > global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.SupportWantedP4NowMin)
            {
                if (LogDue(0x4E3, 10.0)) P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.AdaptCounterBattery, e.ToString());
                return (SupportKind.Barrage, e.Centre);
            }
            if (_plan is { Kind: PlanKind.WaitArtillery, Executed: false } && _package is { } p && now < p.ExecuteAt && !_plan.Deps.Artillery)
            {
                foreach (var c in world.Intel.For(Team).Contacts)
                    if (c.InSight && !c.Flying && Vector2.Distance(c.Position, p.Target) <= global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.SupportWantedP4DistanceMax)
                    {
                        if (LogDue(0x4E4, 10.0)) P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.SupportForecast, $"#{c.Id.Value}");
                        return (SupportKind.Barrage, c.Position);
                    }
            }
            return null;
        }

        /// <summary>A support card used: a SEAD opens the suppression window (spec 174); effectiveness counted (spec 157).</summary>
        private void NoteSupportP4(SimWorld world, SupportKind kind, Vector2 at)
        {
            if (PlanningP4 is not { } tp) return;
            if (kind == SupportKind.Sead)
            {
                tp.SeadUsed = (at, world.Time);
                _seadWanted = null;
            }
        }

        // ------------------------------------------------------------------------------------------------ 132 probe

        private void ProbeP4(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            var tp = _p4!;
            var tc = CoordinationP3!;
            if (_probe != null)
            {
                StepProbeP4(world, intel, _probe);
                return;
            }
            if (!DifficultyGate.Probe(Level) || now < _probeReadyAt || _urgency >= Tun.Pursuit.UrgencyDrop || Defending || Intent.PrimaryObjective is not { } target) return;
            if (_package != null && now >= _package.ExecuteAt) return;
            Squad? main = null;
            var army = 0f;
            foreach (var s in Squads.Squads)
            {
                if (s.IsReserve || s.MemberList.Count == 0) continue;
                army += s.Strength;
                if (s.Task.Kind == TaskKind.Primary && (main == null || s.Strength > main.Strength)) main = s;
            }
            if (main == null) return;
            // The most unknown lane not probed yet (direct, left, right).
            var bestSide = 2;
            var bestUnknown = Tun.Probe.MinUnknown;
            var bestPoint = Vector2.Zero;
            for (var side = -1; side <= 1; side++)
            {
                Vector2 point;
                if (side == 0) point = Vector2.Lerp(main.Centre, target, 0.6f);
                else if (!Squads.FlankPointP3(world, intel, main, target, side, out point)) continue;
                if (tp.Lane(TeamPlanning.LaneKey(target, side), now) != LaneState.Unknown) continue;
                var unknown = tc.Memory.UnknownShare(intel, point, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ProbeP4Radius, now);
                if (unknown >= bestUnknown + 1e-4f)
                {
                    bestUnknown = unknown;
                    bestSide = side;
                    bestPoint = point;
                }
            }
            if (bestSide == 2) return;
            Squad? probe = null;
            foreach (var s in Squads.Squads)
            {
                if (s == main || s.IsReserve || s.MemberList.Count == 0 || s.P3Role is PackageRole.Flank or PackageRole.Fix or PackageRole.Scout || s.P4Role != P4Role.None) continue;
                if (!ProbeRules.ShareFits(s.Strength, army)) continue;
                if (probe == null || (s.Fast && !probe.Fast) || (s.Fast == probe.Fast && (s.Strength < probe.Strength - 1e-3f || (MathF.Abs(s.Strength - probe.Strength) <= 1e-3f && s.Id < probe.Id))))
                    probe = s;
            }
            if (probe == null) return;
            _probe = new ProbeState
            {
                Squad = probe.Id,
                Side = bestSide,
                Point = bestPoint,
                Lane = TeamPlanning.LaneKey(target, bestSide),
                Start = now,
                ProgressAt = now,
                StartStrength = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.ProbeP4StrengthFloor, probe.Strength),
                Best = Vector2.Distance(probe.Centre, bestPoint),
            };
            probe.P4Role = P4Role.Probe;
            SetTask(probe, TaskKind.Secondary, bestPoint, false, false);
            tp.Metrics.ProbeCount++;
            P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.ProbeSent,
                $"squad {probe.Id} ({probe.Strength / MathF.Max(0.01f, army):0%} power) lane {bestSide} unknown {bestUnknown:0%}");
            Cue(world, "probe", bestPoint, probe.Id);
        }

        private void StepProbeP4(SimWorld world, TeamIntel intel, ProbeState pr)
        {
            var now = world.Time;
            var tp = _p4!;
            var s = Squads.Find(pr.Squad);
            ProbeOutcome outcome;
            if (s == null || s.MemberList.Count == 0) outcome = ProbeOutcome.Threat;
            else
            {
                s.P4Role = P4Role.Probe;
                SetTask(s, TaskKind.Secondary, pr.Point, false, false);
                var d = Vector2.Distance(s.Centre, pr.Point);
                if (d < pr.Best - 3f)
                {
                    pr.Best = d;
                    pr.ProgressAt = now;
                }
                var blocked = now - pr.ProgressAt >= Tun.Probe.BlockedS && d > global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepProbeP4DMin && s.State != SquadState.Combat;
                var arrived = d <= global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepProbeP4DMax || s.State == SquadState.Combat;
                outcome = ProbeRules.Judge(TeamPlanning.SeenStrength(intel, pr.Point, 40f), intel.ThreatAt(ThreatKind.AntiTank, pr.Point), s.Strength,
                    1f - s.Strength / pr.StartStrength, blocked, arrived, now - pr.Start >= Tun.Probe.MaxSeconds);
            }
            if (outcome == ProbeOutcome.Pending) return;
            switch (outcome)
            {
                case ProbeOutcome.Exploit:
                    tp.MarkLane(pr.Lane, LaneState.Exploit, now + Tun.Probe.ExploitS);
                    tp.Open(new OpportunityWindow(OpportunityKind.ProbeExploit, pr.Point, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepProbeP4Radius, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepProbeP4Confidence, now + Tun.Probe.ExploitS,
                        OpportunityRoles.Ground | OpportunityRoles.Fast, (int)(pr.Lane & 0x3fffffff)));
                    tp.Metrics.ProbeSuccess++;
                    tp.Adaptation.RouteResult(pr.Lane, true);
                    P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.ProbeExploit, $"lane {pr.Side} ({pr.Point.X:0},{pr.Point.Y:0})");
                    // The main effort shifts: the next plan choice sees the window (the commitment window is cut short).
                    if (_plan != null) _plan.ChosenAt = double.NegativeInfinity;
                    break;
                case ProbeOutcome.Threat:
                    tp.MarkLane(pr.Lane, LaneState.Hot, now + Tun.Probe.LaneMemoryS);
                    tp.Metrics.ProbeThreats++;
                    tp.Adaptation.RouteResult(pr.Lane, false);
                    P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.ProbeThreat, $"lane {pr.Side}: artillery / flank / SEAD first");
                    if (_plan != null) _plan.ChosenAt = double.NegativeInfinity;
                    break;
                case ProbeOutcome.Blocked:
                    tp.MarkLane(pr.Lane, LaneState.Blocked, now + Tun.Probe.LaneMemoryS);
                    tp.Metrics.ProbeBlocked++;
                    P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.ProbeBlocked, $"lane {pr.Side}: no main force through it");
                    break;
                default:
                    P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.ProbeInconclusive, $"lane {pr.Side}");
                    break;
            }
            if (s != null) s.P4Role = P4Role.None;
            _probe = null;
            _probeReadyAt = now + Tun.Probe.CooldownS;
        }

        // ------------------------------------------------------------------------------------------------ 133 feint

        private void FeintP4(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            var tp = _p4!;
            var tc = CoordinationP3!;
            if (_feint != null)
            {
                StepFeintP4(world, intel, _feint);
                return;
            }
            if (now < _feintReadyAt || Defending || Intent.PrimaryObjective is not { } target || _package is not { } p || now >= p.ExecuteAt - 1.0) return;
            var m = CurrentTactic.Modules;
            var fits = m.Pincer || m.Flank > 1f;
            if (!DifficultyGate.Feint(Level, fits)) return;
            var main = Squads.Find(p.Main);
            var from = main?.Centre ?? target;
            var approach = Direction(from, target);
            var lateral = new Vector2(-approach.Y, approach.X);
            var bestUtility = 0f;
            var bestPoint = Vector2.Zero;
            var bestWhy = "";
            void Consider(Vector2 point, bool contests, bool threatens)
            {
                if (!world.Grid.IsWalkable(point)) return;
                var unknown = tc.Memory.UnknownShare(intel, point, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.FeintP4Radius, now);
                var pins = false;
                foreach (var c in intel.Contacts)
                {
                    if (c.Reach <= 0f || Vector2.Distance(c.Position, point) > global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.FeintP4DistanceMin || !world.Catalog.Vehicles.TryGetValue(c.Unit, out var def) || !def.Static) continue;
                    var toFeint = Direction(c.Position, point);
                    var toMain = Direction(c.Position, from);
                    if (Vector2.Dot(toFeint, toMain) < 0.7f) pins = true;
                }
                var u = FeintRules.Utility(contests, unknown, threatens, pins);
                if (u > bestUtility + 1e-4f)
                {
                    bestUtility = u;
                    bestPoint = point;
                    bestWhy = $"{(contests ? "secondary " : "")}{(threatens ? "flank " : "")}{(pins ? "arc " : "")}unknown {unknown:0%}";
                }
            }
            if (Intent.SecondaryObjective is { } sec && PointOwner(world, sec) != Team) Consider(sec, true, false);
            var side = p.FlankSide != 0 ? -p.FlankSide : ((p.Main & 1) == 0 ? 1 : -1);
            Consider(world.Map.Clamp(target + lateral * (global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.FeintP4SideScale * side) - approach * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.FeintP4ApproachScale, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.FeintP4Margin), false, true);
            if (!FeintRules.Allowed(Level, fits, _urgency, bestUtility))
            {
                if (bestUtility > 0f && now - _feintRejectLogAt > global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.FeintP4NowMin)
                {
                    _feintRejectLogAt = now;
                    tp.Metrics.FeintRejected++;
                    P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.FeintRejected, $"utility {bestUtility:0.00} < {Tun.Feint.MinUtility:0.00}");
                }
                return;
            }
            var army = 0f;
            foreach (var s in Squads.Squads)
                if (!s.IsReserve) army += s.Strength;
            Squad? pick = null;
            foreach (var s in Squads.Squads)
            {
                if (s.IsReserve || s.MemberList.Count == 0 || s.Id == p.Main || s.Id == p.Flank || s.Id == p.Fix || s.P4Role != P4Role.None || s.P3Role == PackageRole.Scout) continue;
                if (army <= 0f || s.Strength / army > Tun.Feint.PowerShareMax) continue;
                if (pick == null || (s.Fast && !pick.Fast) || (s.Fast == pick.Fast && (s.Strength < pick.Strength - 1e-3f || (MathF.Abs(s.Strength - pick.Strength) <= 1e-3f && s.Id < pick.Id))))
                    pick = s;
            }
            if (pick == null) return;
            _feint = new FeintState
            {
                Squad = pick.Id,
                At = bestPoint,
                Main = target,
                Start = now,
                MainBefore = TeamPlanning.SeenStrength(intel, target, 60f),
                FeintBefore = TeamPlanning.SeenStrength(intel, bestPoint, 60f),
            };
            pick.P4Role = P4Role.Feint;
            SetTask(pick, TaskKind.Secondary, bestPoint, false, false);
            tp.Metrics.FeintCount++;
            P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.FeintSent, $"squad {pick.Id} utility {bestUtility:0.00} ({bestWhy})");
            Cue(world, "feint", bestPoint, pick.Id);
        }

        private void StepFeintP4(SimWorld world, TeamIntel intel, FeintState f)
        {
            var now = world.Time;
            var tp = _p4!;
            var s = Squads.Find(f.Squad);
            var over = s == null || s.MemberList.Count == 0 || now - f.Start >= Tun.Feint.MaxSeconds || _urgency >= Tun.Pursuit.UrgencyDrop ||
                       (!double.IsNaN(f.SuccessAt) && now - f.SuccessAt >= global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepFeintP4NowMin);
            if (!over)
            {
                s!.P4Role = P4Role.Feint;
                SetTask(s, TaskKind.Secondary, f.At, false, false);
                // Only what is seen counts (no hidden reaction): the objective watched now, its defenders seen fewer, more seen at the feint.
                var mainNow = TeamPlanning.SeenStrength(intel, f.Main, 60f);
                var watched = intel.Seen[intel.CellIndex(f.Main)] >= now - global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepFeintP4NowSub;
                if (now - f.Start < global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepFeintP4NowMax) f.MainBefore = MathF.Max(f.MainBefore, mainNow);
                else if (double.IsNaN(f.SuccessAt) && watched && FeintRules.Succeeded(f.MainBefore, mainNow, f.FeintBefore, TeamPlanning.SeenStrength(intel, f.At, 60f)))
                {
                    f.SuccessAt = now;
                    tp.Metrics.FeintSuccess++;
                    tp.Open(new OpportunityWindow(OpportunityKind.FeintSuccess, f.Main, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepFeintP4Radius2, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepFeintP4Confidence, now + global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepFeintP4NowAdd, OpportunityRoles.Ground | OpportunityRoles.Fast, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.StepFeintP4Subject));
                    P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.FeintSuccess, $"seen at the objective {f.MainBefore:0.0} -> {mainNow:0.0}");
                    // The main package goes now (the window is short).
                    if (_package is { } p && now < p.ExecuteAt)
                    {
                        p.ExecuteAt = now + 1.0;
                        var keys = new List<int>(_stage.Keys);
                        keys.Sort();
                        foreach (var id in keys)
                        {
                            var st = _stage[id];
                            if (st.until > now + 1.0) _stage[id] = (now + 1.0, st.at, st.eta);
                        }
                        foreach (var sq in Squads.Squads)
                            if (p.Members.Contains(sq.Id) && sq.P3StageUntil > now + 1.0) sq.P3StageUntil = now + 1.0;
                    }
                }
                return;
            }
            if (double.IsNaN(f.SuccessAt)) P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.FeintEnded, $"squad {f.Squad}");
            if (s != null) s.P4Role = P4Role.None;
            _feint = null;
            _feintReadyAt = now + Tun.Feint.CooldownS;
        }

        // ------------------------------------------------------------------------------------------------ 157 / Part M adaptation

        private readonly List<Contact> _seenNow = new();

        private void AdaptP4(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            var tp = _p4!;
            _seenNow.Clear();
            foreach (var c in intel.Contacts)
                if (c.InSight) _seenNow.Add(c);
            if (_seenNow.Count > 0)
                foreach (var v in world.VehicleList)
                {
                    if (!v.IsAlive || v.Team != Team || v.Def.Static || v.Scripted || v.Def.Weapon.Damage <= 0f) continue;
                    var w = v.Def.Weapon;
                    var chance = false;
                    foreach (var c in _seenNow)
                        if (w.CanTarget(c.Flying) && Vector2.Distance(c.Position, v.Position) <= w.Range * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AdaptP4RangeScale)
                        {
                            chance = true;
                            break;
                        }
                    if (chance) tp.Adaptation.SampleUse(v.Def.Id, now - v.LastFiredAt <= global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.AdaptP4NowMax, now);
                }
            var a = tp.Adaptation;
            if (a.AirHeavy != _adaptAir && (_adaptAir = a.AirHeavy)) P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.AdaptAir, $"air {a.AirShare:0%}");
            if (a.ArtilleryCamping != _adaptCamp && (_adaptCamp = a.ArtilleryCamping)) P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.AdaptCounterBattery, $"{a.CampImpacts} shells from one battery");
            if (a.TowerPattern != _adaptTowers && (_adaptTowers = a.TowerPattern)) P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.AdaptTowers, $"{a.Towers} towers");
            if (a.ReconBoost > 0f != _adaptRecon && (_adaptRecon = a.ReconBoost > 0f)) P4Reasons.Commander(world, Team, DecisionKind.Plan, P4Reasons.AdaptRecon, $"{a.AmbushRepeats} repeated ambushes");
        }

        /// <summary>Part M: the pursuit leash scale where the player keeps baiting (1: none).</summary>
        internal float LeashScaleP4(Vector2 at) => PlanningP4 is { } tp && DifficultyGate.Adaptation(Level) ? tp.Adaptation.LeashScale(at) : 1f;

        /// <summary>Part M: the extra unknown share that makes scout-before-commit ask a scout (0: none).</summary>
        internal float ReconBoostP4() => PlanningP4 is { } tp && DifficultyGate.Adaptation(Level) ? tp.Adaptation.ReconBoost : 0f;

        /// <summary>
        /// Spec 157 / 224 utilization and Part M "adjust procurement role deficit": score points on a card: an under-used class
        /// (legal targets in reach but it does not fire) buys less, anti-air more against an air-heavy army, guns and breachers
        /// more against a tower defence. 0 below the adaptation level.
        /// </summary>
        public float PurchaseAdjustP4(SimWorld world, VehicleDef def)
        {
            if (PlanningP4 is not { } tp || !DifficultyGate.Adaptation(Level)) return 0f;
            var a = tp.Adaptation;
            var points = -(1f - a.PurchaseModifier(def.Id, world.Time)) * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.PurchaseAdjustP4PurchaseModifierScale;
            if (a.AirHeavy && (def.Class == UnitClass.AntiAir || Combat.CombatSystem.IsAntiAir(def.Weapon))) points += 1.5f;
            if (a.TowerPattern && (def.Weapon.MinRange > 0f || def.Breacher)) points += 1f;
            return points;
        }

        // ------------------------------------------------------------------------------------------------ P0-B section 18 leftovers

        /// <summary>Once a second: is the own force enough by the forecast (whole army against everything known)?</summary>
        private void EnoughP4(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            _ownUnits.Clear();
            _enemyUnits.Clear();
            var known = 0;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Team && !v.Def.Static && !v.Scripted) _ownUnits.Add(OwnUnit(v));
            foreach (var c in intel.Contacts)
                if (c.Age(now) <= global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.EnoughP4AgeMax && ContactUnit(world, c, out var u))
                {
                    _enemyUnits.Add(u);
                    known++;
                }
            var ownAir = Profile(_ownUnits, _levelsOwn);
            var enemyAir = Profile(_enemyUnits, _levelsEnemy);
            var own = Estimate(world, _ownUnits, _levelsEnemy, enemyAir);
            var enemy = Estimate(world, _enemyUnits, _levelsOwn, ownAir).Scaled(Tun.Forecast.UnknownMargin);
            var f = CachedForecast(ForecastKey(PlanKind.AttackNow, global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.EnoughP4Side, Vector2.Zero, 0f, own, enemy), () => CombatForecaster.Forecast(own, enemy, Tun.Forecast.Seconds, 0f));
            var enough = CombatForecaster.Enough(own.Strength, enemy.Strength, known, f);
            if (enough && !_enough) _enoughSince = now;
            if (!enough) _enoughSince = double.NaN;
            _enough = enough;
        }

        /// <summary>
        /// P0-B section 18's open items: hold the purchase when the forecast says the force is enough (never past
        /// <c>enoughMaxHoldS</c> at a time, never with a thin army or CP about to overflow), and keep a share of the bank back
        /// while a seen boss nears its next phase mark (its health bar is public).
        /// </summary>
        public bool HoldPurchaseP4(SimWorld world, TeamEconomy economy, float price, int ownTotal)
        {
            if (PlanningP4 is not { } tp) return false;
            var now = world.Time;
            if (ownTotal < 4 || economy.Cp >= economy.Bank - 3f) return false;
            if (_enough && !double.IsNaN(_enoughSince))
            {
                var cycle = Tun.Forecast.EnoughMaxHoldS + global::MachineBrigade.Sim.Content.SimTunables.Ai.AiCommander.HoldPurchaseP4EnoughMaxHoldSAdd;
                if ((now - _enoughSince) % cycle < Tun.Forecast.EnoughMaxHoldS)
                {
                    if (LogDue(0x4E0, 10.0))
                    {
                        tp.Metrics.BuyHoldsEnough++;
                        P4Reasons.Commander(world, Team, DecisionKind.Purchase, P4Reasons.BuyEnough, $"forecast enough ({economy.Cp:0} CP kept)");
                    }
                    return true;
                }
            }
            if (BossPhaseSoonP4(world) is { } boss)
            {
                if (double.IsNaN(_phaseReserveSince)) _phaseReserveSince = now;
                if (now - _phaseReserveSince < Tun.BossTactics.PhaseReserveMaxS && economy.Cp - price < economy.Bank * Tun.BossTactics.PhaseReserveShare)
                {
                    if (LogDue(0x4E1, 10.0))
                    {
                        tp.Metrics.BuyReservesBossPhase++;
                        P4Reasons.Commander(world, Team, DecisionKind.Purchase, P4Reasons.BuyBossPhase,
                            $"#{boss.Id.Value} {boss.Hp / MathF.Max(1f, boss.MaxHp):0%} near phase {boss.Phase + 1}: keep {economy.Bank * Tun.BossTactics.PhaseReserveShare:0} CP");
                    }
                    return true;
                }
            }
            else _phaseReserveSince = double.NaN;
            return false;
        }

        /// <summary>A seen boss (not ours) whose health is within the phase margin above its next phase mark.</summary>
        private Vehicle? BossPhaseSoonP4(SimWorld world)
        {
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || !v.Def.Boss || v.Team == Team || !v.IsVisibleTo(Team) || v.MaxHp <= 0f) continue;
                var phases = v.Def.Phases;
                if (v.Phase >= phases.Count) continue;
                var next = phases[v.Phase];
                var share = v.Hp / v.MaxHp;
                if (share > next.At && share - next.At <= Tun.BossTactics.PhaseMargin) return v;
            }
            return null;
        }

        // ------------------------------------------------------------------------------------------------ 179 weakpoint (log)

        /// <summary>Spec 179: the side's top boss weakpoint (for the log; the shooters pick by the same utility in BossSystem.ChoosePart).</summary>
        private void WeakpointLogP4(SimWorld world, TeamIntel intel)
        {
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || !v.Def.Boss || !v.HasParts || v.Team == Team || !v.IsVisibleTo(Team)) continue;
                var best = world.Bosses.BestWeakpointP4(v, out var score);
                var key = v.Id.Value * 64 + best;
                if (best >= 0 && key != _weakpointLogged && LogDue(0x4F0 + (v.Id.Value & 0xff), 5.0))
                {
                    _weakpointLogged = key;
                    P4Reasons.Commander(world, Team, DecisionKind.Target, P4Reasons.Weakpoint, $"#{v.Id.Value} part {v.Def.Parts[best].Id} ({v.Def.Parts[best].Kind}) {score:0}");
                }
                return;
            }
        }

        // ------------------------------------------------------------------------------------------------ 215 cues

        private void Cue(SimWorld world, string kind, Vector2 at, int squad) => _p4?.Cue(kind, at, squad);
    }
}
