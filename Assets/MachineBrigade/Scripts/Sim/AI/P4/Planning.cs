#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Spec 132: what a probe left on a lane.</summary>
    public enum LaneState : byte
    {
        Unknown,
        Exploit,
        Hot,
        Blocked,
    }

    /// <summary>Spec 215: a tactical communication cue for the presentation (radio line, leader gesture, escort animation). No gameplay effect.</summary>
    public readonly struct TacticalCue
    {
        public TacticalCue(double time, string kind, Vector2 at, int squad)
        {
            Time = time;
            Kind = kind;
            At = at;
            Squad = squad;
        }

        public double Time { get; }
        public string Kind { get; }
        public Vector2 At { get; }
        public int Squad { get; }
    }

    /// <summary>Spec 225 metrics of the P4 lane (the lead's runs read them).</summary>
    public sealed class PlanningMetrics
    {
        public int PlansEvaluated, PlanSwitches, PlanHolds, Replans, ForecastCacheHits, ForecastsComputed;
        public int ProbeCount, ProbeSuccess, ProbeThreats, ProbeBlocked, FeintCount, FeintSuccess, FeintRejected;
        public int OpportunityWindows, PackageAbortsP4, RepeatPenalised, PlanFailures;
        public int SeadPackages, SeadSuccess, SeadReroutes, RiskReroutes, Egresses, CapReturns, Handoffs, AirIntercepts, BomberWaits, BomberRetargets;
        public int EscapeSectorPlans, PatternFollowUps, GunOwnershipBlocks, BuyHoldsEnough, BuyReservesBossPhase, Cues;
    }

    /// <summary>
    /// Spec 157 / Part M: same-match adaptation from observed data only, reset every match (it lives in the side's planning
    /// state): moving averages of route success, unit class utilization, kill efficiency by target group and support
    /// effectiveness, plus the player-pattern counters of Part M (bait chases, artillery camping, air-heavy army, repeated
    /// ambush on a route, tower defence). No machine learning, no cross-match memory, no hidden state.
    /// </summary>
    public sealed class AdaptationTracker
    {
        private readonly Dictionary<long, float> _routes = new();
        private readonly Dictionary<string, (float ema, double lowSince)> _use = new();
        private readonly Dictionary<int, float> _kills = new();
        private readonly Dictionary<int, float> _support = new();
        private readonly Dictionary<long, int> _bait = new();

        public float AirShare { get; internal set; }
        public int CampImpacts { get; internal set; }
        public int Towers { get; internal set; }
        public int AmbushRepeats { get; internal set; }

        public static float Ema(float old, float sample) => old + (sample - old) * Math.Clamp(Tun.Adaptation.EmaAlpha, 0f, 1f);

        public void RouteResult(long lane, bool success) =>
            _routes[lane] = Ema(_routes.TryGetValue(lane, out var r) ? r : 0.5f, success ? 1f : 0f);

        public float RouteSuccess(long lane) => _routes.TryGetValue(lane, out var r) ? r : 0.5f;

        /// <summary>One look at a unit class that had a legal target in reach: did it fire (utilization sample)?</summary>
        public void SampleUse(string unit, bool fired, double now)
        {
            var had = _use.TryGetValue(unit, out var u);
            var ema = Ema(had ? u.ema : 1f, fired ? 1f : 0f);
            var low = ema < Tun.Adaptation.LowUtilization ? (double.IsNaN(u.lowSince) || !had ? now : u.lowSince) : double.NaN;
            _use[unit] = (ema, low);
        }

        public float Utilization(string unit) => _use.TryGetValue(unit, out var u) ? u.ema : 1f;

        /// <summary>AI MASTER P5 Part K lowUtilizationUnitClasses: classes under the threshold for <c>lowUtilizationS</c> or longer.</summary>
        public int LowClasses(double now)
        {
            var n = 0;
            foreach (var u in _use.Values)
                if (!double.IsNaN(u.lowSince) && now - u.lowSince >= Tun.Adaptation.LowUtilizationS) n++;
            return n;
        }

        /// <summary>Spec 224 "utilization": a class under the threshold for <c>lowUtilizationS</c> buys less (down to the floor).</summary>
        public float PurchaseModifier(string unit, double now)
        {
            if (!_use.TryGetValue(unit, out var u) || double.IsNaN(u.lowSince) || now - u.lowSince < Tun.Adaptation.LowUtilizationS) return 1f;
            var t = MathF.Max(1e-3f, Tun.Adaptation.LowUtilization);
            return Math.Clamp(u.ema / t, Tun.Adaptation.PurchaseFloor, 1f);
        }

        public void Kill(int group) => _kills[group] = Ema(_kills.TryGetValue(group, out var k) ? k : 0f, 1f);

        public float KillEfficiency(int group) => _kills.TryGetValue(group, out var k) ? k : 0f;

        public void SupportResult(int kind, bool effective) => _support[kind] = Ema(_support.TryGetValue(kind, out var s) ? s : 0.5f, effective ? 1f : 0f);

        public float SupportEffect(int kind) => _support.TryGetValue(kind, out var s) ? s : 0.5f;

        private static long Cell(Vector2 p) => (long)MathF.Floor(p.X / 40f) * 100003L + (long)MathF.Floor(p.Y / 40f);

        /// <summary>Part M: a squad lost units while chasing near <paramref name="at"/> (a bait pattern when repeated).</summary>
        public void BaitLoss(Vector2 at) => _bait[Cell(at)] = (_bait.TryGetValue(Cell(at), out var n) ? n : 0) + 1;

        public int BaitCount(Vector2 at) => _bait.TryGetValue(Cell(at), out var n) ? n : 0;

        /// <summary>Part M: the pursuit leash where the player keeps baiting chases.</summary>
        public float LeashScale(Vector2 at) => BaitCount(at) >= Tun.Adaptation.BaitRepeat ? Tun.Adaptation.LeashScale : 1f;

        public bool AirHeavy => AirShare >= Tun.Adaptation.AirHeavyShare;
        public bool ArtilleryCamping => CampImpacts >= Tun.Adaptation.CampImpacts;
        public bool TowerPattern => Towers >= Tun.Adaptation.TowerCount;

        /// <summary>Part M: the scout-before-commit threshold drop under a repeated fixed-route ambush.</summary>
        public float ReconBoost => AmbushRepeats >= 2 ? Tun.Adaptation.ReconBoost : 0f;
    }

    /// <summary>
    /// AI MASTER P4 (lane A): one AI side's advanced-planning state, beside its P3 coordination: the forecast cache, plan
    /// anti-repetition, same-match adaptation, the boss pattern memory, intent ownership, opportunity windows, lane memory
    /// from probes, bomb-drop reservations and the presentation cues. Fed by observations (own / seen deaths, seen boss parts
    /// breaking, telegraphs) and refreshed by the commander once a second. Reset with the match (no cross-match memory).
    /// </summary>
    public sealed class TeamPlanning
    {
        private readonly SimWorld _world;
        private readonly List<OpportunityWindow> _windows = new();
        private readonly List<TacticalCue> _cues = new();
        private readonly Dictionary<long, (double at, CombatForecast f)> _forecasts = new();
        private readonly Dictionary<long, (LaneState state, double until)> _lanes = new();
        private readonly Dictionary<long, double> _warnSeen = new();
        private readonly Dictionary<int, (Vector2 centre, Vector2 axis, double at, int sig)> _firstZone = new();
        private readonly List<(Vector2 at, float value, double time)> _enemyLosses = new();
        private readonly Dictionary<long, (int events, double last)> _lossCells = new();
        private readonly List<(double time, float seen)> _objectiveSeen = new();
        private readonly List<(Vector2 at, float radius, double until)> _drops = new();
        private readonly Dictionary<string, double> _cueAt = new();
        private Vector2 _objectiveFor = new(float.NaN, float.NaN);
        private int _rubbleSeen;

        internal TeamPlanning(SimWorld world, int team)
        {
            _world = world;
            Team = team;
        }

        public int Team { get; }
        public RepetitionMemory Repetition { get; } = new();
        public AdaptationTracker Adaptation { get; } = new();
        public PatternMemory Patterns { get; } = new();
        public IntentOwnership Ownership { get; } = new();
        public PlanningMetrics Metrics { get; } = new();
        public IReadOnlyList<OpportunityWindow> Opportunities => _windows;

        /// <summary>Spec 215: the latest cues (newest last) for the presentation to show.</summary>
        public IReadOnlyList<TacticalCue> Cues => _cues;

        /// <summary>Spec 183 route version: changes when a probe finds a lane blocked (plus the nav grid's version, read by the commander).</summary>
        public int LaneVersion { get; private set; }

        /// <summary>A SEAD card used (where, when): spec 174's suppression window.</summary>
        public (Vector2 at, double time)? SeadUsed { get; internal set; }

        // ------------------------------------------------------------------------------------------------ forecast cache

        internal bool TryForecast(long key, double now, out CombatForecast f)
        {
            if (_forecasts.TryGetValue(key, out var c) && now - c.at < Tun.Forecast.CacheS)
            {
                f = c.f;
                Metrics.ForecastCacheHits++;
                return true;
            }
            f = default;
            return false;
        }

        internal void StoreForecast(long key, double now, in CombatForecast f)
        {
            if (_forecasts.Count > 128) _forecasts.Clear();
            _forecasts[key] = (now, f);
            Metrics.ForecastsComputed++;
        }

        // ------------------------------------------------------------------------------------------------ lanes (132)

        public static long LaneKey(Vector2 target, int side) =>
            ((long)MathF.Floor(target.X / 30f) * 100003L + (long)MathF.Floor(target.Y / 30f)) * 4L + (side + 1);

        public LaneState Lane(long key, double now) => _lanes.TryGetValue(key, out var l) && l.until > now ? l.state : LaneState.Unknown;

        internal void MarkLane(long key, LaneState state, double until)
        {
            _lanes[key] = (state, until);
            if (state == LaneState.Blocked) LaneVersion++;
        }

        // ------------------------------------------------------------------------------------------------ windows (156)

        /// <summary>An open window covering <paramref name="p"/> that needs one of <paramref name="roles"/> (null: none).</summary>
        public OpportunityWindow? WindowNear(Vector2 p, OpportunityRoles roles, float extra = 0f)
        {
            OpportunityWindow? best = null;
            foreach (var w in _windows)
                if ((w.Roles & roles) != 0 && w.Covers(p, extra) && (best == null || w.Confidence > best.Confidence)) best = w;
            return best;
        }

        /// <summary>Opens a window (one per kind and subject: a repeat extends it). True when it is new.</summary>
        internal bool Open(OpportunityWindow w)
        {
            foreach (var o in _windows)
                if (o.Kind == w.Kind && o.Subject == w.Subject && (w.Subject != 0 || Vector2.Distance(o.Centre, w.Centre) < global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.OpenDistanceMax))
                {
                    o.Expires = Math.Max(o.Expires, w.Expires);
                    return false;
                }
            _windows.Add(w);
            Metrics.OpportunityWindows++;
            P4Reasons.Commander(_world, Team, DecisionKind.Plan, P4Reasons.Opportunity, w.ToString());
            return true;
        }

        // ------------------------------------------------------------------------------------------------ bomb drops (178)

        internal bool DropClear(Vector2 at, float radius, double now)
        {
            foreach (var d in _drops)
                if (d.until > now && Vector2.Distance(d.at, at) < d.radius + radius) return false;
            return true;
        }

        internal void ReserveDrop(Vector2 at, float radius, double until)
        {
            _drops.RemoveAll(d => d.until <= _world.Time);
            _drops.Add((at, radius, until));
        }

        // ------------------------------------------------------------------------------------------------ cues (215)

        internal void Cue(string kind, Vector2 at, int squad)
        {
            if (!Tun.Cues.Enabled) return;
            var now = _world.Time;
            if (_cueAt.TryGetValue(kind, out var last) && now - last < Tun.Cues.CooldownS) return;
            _cueAt[kind] = now;
            _cues.Add(new TacticalCue(now, kind, at, squad));
            while (_cues.Count > Math.Max(1, Tun.Cues.Kept)) _cues.RemoveAt(0);
            Metrics.Cues++;
            P4Reasons.Squad(_world, Team, squad, DecisionKind.Hint, P4Reasons.Cue, kind);
        }

        // ------------------------------------------------------------------------------------------------ observations

        /// <summary>A vehicle destroyed: own (Part M repeated-ambush counter) or an enemy seen dying (kill efficiency, AA-down window, redeploy check).</summary>
        internal void ObserveDeath(Vehicle v, bool own, bool seen)
        {
            var now = _world.Time;
            if (own)
            {
                var cell = (long)MathF.Floor(v.Position.X / 40f) * 100003L + (long)MathF.Floor(v.Position.Y / 40f);
                _lossCells.TryGetValue(cell, out var c);
                if (c.events == 0 || now - c.last > global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveDeathNowMin)
                {
                    c.events++;
                    if (c.events == 2) Adaptation.AmbushRepeats++;
                }
                _lossCells[cell] = (c.events, now);
                if (_lossCells.Count > 256) _lossCells.Clear();
                return;
            }
            if (!seen) return;
            var value = v.Def.Boss ? v.MaxHp / global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveDeathMaxHpDivisor : MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveDeathPowerFloor, v.Def.Power);
            _enemyLosses.Add((v.Position, value, now));
            if (_enemyLosses.Count > global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveDeathCountMin2) _enemyLosses.RemoveAt(0);
            var group = TeamIntel.GroupOf(v.Def);
            if (group is { } g) Adaptation.Kill((int)g);
            if (group == ForceGroup.AntiAir || v.Def.Class == Content.UnitClass.AntiAir)
                Open(new OpportunityWindow(OpportunityKind.AntiAirDown, v.Position, MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveDeathRangeFloor, v.Def.Weapon.Range), global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveDeathConfidence,
                    now + Tun.Opportunity.AaDownS, OpportunityRoles.Air, v.Id.Value));
        }

        /// <summary>A boss part seen breaking: an APS / shield / radar part opens a window on the boss (spec 156).</summary>
        internal void ObservePartBroken(Vehicle boss, int part)
        {
            if (part < 0 || part >= boss.Def.Parts.Count || !WeakpointUtility.IsUtilityKind(boss.Def.Parts[part].Kind)) return;
            Open(new OpportunityWindow(OpportunityKind.BossPartDown, boss.Position, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObservePartBrokenRadiusAdd + boss.Radius, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObservePartBrokenConfidence, _world.Time + Tun.Opportunity.PartDownS,
                OpportunityRoles.Ground | OpportunityRoles.Air | OpportunityRoles.Artillery, boss.Id.Value * 16 + part));
        }

        /// <summary>Spec 214: the boss telegraphs seen; a zone of the same boss inside the pattern window after a first one is its follow-up.</summary>
        internal void ObserveWarnings(IReadOnlyList<WarningZone> warnings, double now)
        {
            foreach (var w in warnings)
            {
                if (!w.Big || w.Source == 0 || w.Team == Team || w.Due < now) continue;
                long key;
                unchecked
                {
                    key = ((long)w.Source * 1000003L + (long)MathF.Round(w.Centre.X * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveWarningsXScale) * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveWarningsRoundScale + (long)MathF.Round(w.Centre.Y * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveWarningsYScale)) * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveWarningsSourceScale2 + (long)Math.Round(w.Due * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveWarningsDueScale);
                }
                if (_warnSeen.ContainsKey(key)) continue;
                _warnSeen[key] = now;
                var axis = w.Centre - w.Origin;
                if (_firstZone.TryGetValue(w.Source, out var f) && now - f.at <= Tun.BossTactics.PatternWindowS &&
                    Vector2.Distance(f.centre, w.Centre) > MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveWarningsRadiusFloor, w.Radius * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveWarningsRadiusScale))
                {
                    Patterns.FollowUp(f.sig, f.centre, f.axis, w.Centre);
                    Metrics.PatternFollowUps++;
                    continue;
                }
                var sig = PatternMemory.Signature(w.Source, w.Radius);
                Patterns.Seen(sig);
                _firstZone[w.Source] = (w.Centre, axis, now, sig);
            }
            if (_warnSeen.Count > 256)
            {
                var old = new List<long>();
                foreach (var kv in _warnSeen)
                    if (now - kv.Value > global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.ObserveWarningsNowMin) old.Add(kv.Key);
                foreach (var k in old) _warnSeen.Remove(k);
            }
        }

        /// <summary>The seen (in sight now) enemy strength within <paramref name="radius"/> (ground and air).</summary>
        public static float SeenStrength(TeamIntel intel, Vector2 at, float radius)
        {
            var sum = 0f;
            foreach (var c in intel.Contacts)
                if (c.InSight && Vector2.Distance(c.Position, at) <= radius) sum += c.Strength;
            return sum;
        }

        private float EnemyLossesNear(Vector2 p, float radius, double since)
        {
            var sum = 0f;
            foreach (var l in _enemyLosses)
                if (l.time >= since && Vector2.Distance(l.at, p) <= radius) sum += l.value;
            return sum;
        }

        /// <summary>Once a second from the commander: windows from the intel (exposed guns, main force far, defenders leaving, gates), Part M counters.</summary>
        internal void Update(TeamIntel intel, Vector2? objective, TeamCoordination tc)
        {
            var now = _world.Time;
            _windows.RemoveAll(w => w.Expires <= now);
            Repetition.Prune(now);
            Ownership.Prune(now);
            if (_lanes.Count > global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateCountMin)
            {
                var old = new List<long>();
                foreach (var kv in _lanes)
                    if (kv.Value.until <= now) old.Add(kv.Key);
                foreach (var k in old) _lanes.Remove(k);
            }
            // Exposed enemy artillery: a gun in sight with no known enemy direct-fire unit round it.
            foreach (var c in intel.Contacts)
            {
                if (!c.InSight || !c.Artillery || c.Flying) continue;
                var escorted = false;
                foreach (var o in intel.Contacts)
                    if (o != c && !o.Artillery && !o.Flying && o.Age(now) < global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateAgeMax && Vector2.Distance(o.Position, c.Position) <= Tun.Opportunity.ExposedRadius)
                    {
                        escorted = true;
                        break;
                    }
                if (!escorted)
                    Open(new OpportunityWindow(OpportunityKind.ArtilleryExposed, c.Position, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateRadius, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateConfidence, now + Tun.Opportunity.ArtilleryExposedS,
                        OpportunityRoles.Fast | OpportunityRoles.Air, c.Id.Value));
            }
            if (objective is { } o2)
            {
                // The enemy main force far from the objective.
                var found = false;
                EnemyGroup main = default;
                foreach (var g in intel.EnemyGroups)
                    if (!g.Air && g.Confidence >= 0.5f && (!found || g.Strength > main.Strength))
                    {
                        main = g;
                        found = true;
                    }
                if (found && Vector2.Distance(main.Centre, o2) > Tun.Opportunity.MainFarDistance)
                    Open(new OpportunityWindow(OpportunityKind.MainForceFar, o2, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateRadius2, main.Confidence, now + Tun.Opportunity.MainFarS,
                        OpportunityRoles.Ground | OpportunityRoles.Fast, 1));
                // Defenders seen leaving: the seen strength at the objective fell (no seen losses explain it) while it was watched.
                if (float.IsNaN(_objectiveFor.X) || Vector2.Distance(_objectiveFor, o2) > global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateDistanceMin)
                {
                    _objectiveFor = o2;
                    _objectiveSeen.Clear();
                }
                var watched = intel.Seen[intel.CellIndex(o2)] >= now - global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateNowSub;
                if (watched)
                {
                    var seen = SeenStrength(intel, o2, 60f);
                    _objectiveSeen.RemoveAll(s => now - s.time > Tun.Opportunity.RedeployS);
                    var peak = 0f;
                    foreach (var s in _objectiveSeen) peak = MathF.Max(peak, s.seen);
                    _objectiveSeen.Add((now, seen));
                    if (peak > 0f && seen <= peak * (1f - Tun.Opportunity.RedeployDrop) &&
                        EnemyLossesNear(o2, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateRadius3, now - Tun.Opportunity.RedeployS) < (peak - seen) * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdatePeakScale)
                        Open(new OpportunityWindow(OpportunityKind.DefendersRedeploy, o2, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateRadius2, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateConfidence2, now + Tun.Opportunity.RedeployS,
                            OpportunityRoles.Ground | OpportunityRoles.Fast, 2));
                }
            }
            // A wall breached (a gate open): seen rubble.
            if (_world.HasWalls)
            {
                var areas = _world.Walls.RubbleAreas;
                for (var i = _rubbleSeen; i < areas.Count; i++)
                {
                    var centre = (areas[i].min + areas[i].max) * 0.5f;
                    if (intel.Seen[intel.CellIndex(centre)] >= now - global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateNowSub2)
                        Open(new OpportunityWindow(OpportunityKind.GateOpen, centre, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateRadius, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateConfidence3, now + Tun.Opportunity.GateS, OpportunityRoles.Ground, global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateIAdd + i));
                }
                _rubbleSeen = areas.Count;
            }
            // Part M counters (observed only).
            var total = 0f;
            foreach (var x in intel.EnemyComposition) total += x;
            Adaptation.AirShare = total > 0f ? (intel.EnemyComposition[(int)ForceGroup.Helicopter] + intel.EnemyComposition[(int)ForceGroup.Plane]) / total : 0f;
            var towers = 0;
            foreach (var c in intel.Contacts)
                if (_world.Catalog.Vehicles.TryGetValue(c.Unit, out var def) && def.Static && c.Reach > 0f) towers++;
            Adaptation.Towers = towers;
            var shots = 0;
            foreach (var e in tc.Battery.Estimates)
                if (now - e.LastAt < global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateNowMax) shots = Math.Max(shots, e.Shots);
            Adaptation.CampImpacts = shots;
            if (_enemyLosses.Count > 0 && now - _enemyLosses[0].time > global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateNowMin) _enemyLosses.RemoveAll(l => now - l.time > global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamPlanning.UpdateNowMin);
        }
    }
}
