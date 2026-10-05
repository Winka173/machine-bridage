#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P3 (lane A): the battle-wide part of the coordination layer. It keeps one <see cref="TeamCoordination"/>
    /// per AI side and turns two kinds of world events into observations (never reveals):
    /// <list type="bullet">
    /// <item>an own vehicle destroyed: a recent-death danger mark for its side (spec 129); an enemy destroyed while in a
    /// side's sight: an observed loss for that side's counterattack windows (spec 212);</item>
    /// <item>an indirect (artillery) round fired: queued until it lands; a side that saw the impact area gets an origin
    /// estimate with an error radius (spec 144: confidence grows with shots from the same area; "perfect artillery origin"
    /// is not accepted, spec 227), and the impact itself (shoot-and-scoot threat, dispersion timing, spec 145 / 213).</item>
    /// </list>
    /// Deterministic: lists in event order, no Random (the error offset is a hash of the shooter and its shot count).
    /// </summary>
    public sealed class CoordinationState
    {
        private const int MaxShells = 256;
        private readonly SimWorld _world;
        private readonly TeamCoordination?[] _teams = new TeamCoordination?[3];
        private readonly List<Shell> _shells = new();
        private readonly Dictionary<int, int> _shotCount = new();
        private double _steppedAt = double.NegativeInfinity;

        private readonly struct Shell
        {
            public Shell(int team, Vector2 origin, Vector2 aim, double lands, int key)
            {
                Team = team;
                Origin = origin;
                Aim = aim;
                Lands = lands;
                Key = key;
            }

            public int Team { get; }
            public Vector2 Origin { get; }
            public Vector2 Aim { get; }
            public double Lands { get; }
            public int Key { get; }
        }

        internal CoordinationState(SimWorld world) => _world = world;

        /// <summary>The side's coordination (made on first use; teams outside 0-2 share the last slot).</summary>
        public TeamCoordination For(int team)
        {
            var i = Math.Clamp(team, 0, _teams.Length - 1);
            return _teams[i] ??= new TeamCoordination(_world, team);
        }

        /// <summary>The side's coordination if one of its AI layers made it (null otherwise: a player side).</summary>
        public TeamCoordination? Peek(int team) => team >= 0 && team < _teams.Length ? _teams[team] : null;

        internal void Observe(in SimEvent e)
        {
            if (e.Kind == SimEventKind.VehicleDestroyed)
            {
                if (!_world.TryGetVehicle(e.Entity, out var v)) return;
                var value = v.Def.Boss ? v.MaxHp / 150f : MathF.Max(0.5f, v.Def.Power);
                for (var t = 0; t < _teams.Length; t++)
                {
                    var tc = _teams[t];
                    if (tc == null) continue;
                    if (t == v.Team) tc.Memory.AddDeath(v.Position, value, _world.Time);
                    else if (v.IsVisibleTo(t)) tc.Memory.AddEnemyLoss(v.Position, value, _world.Time);
                }
                return;
            }
            // WeaponFired: only ground artillery (a gun with a minimum range or a lofted round); bombs and drones are not batteries.
            if (e.DefId == null || !_world.Catalog.Weapons.TryGetValue(e.DefId, out var w)) return;
            if (!(w.MinRange > 0f || w.Lofted) || w.Guided) return;
            if (!_world.TryGetVehicle(e.Entity, out var shooter) || shooter.Flying) return;
            if (_shells.Count >= MaxShells) _shells.RemoveAt(0);
            _shotCount.TryGetValue(shooter.Id.Value, out var n);
            _shotCount[shooter.Id.Value] = n + 1;
            _shells.Add(new Shell(shooter.Team, e.Position, e.Target, _world.Time + MathF.Max(0f, e.Value), shooter.Id.Value * 131 + n));
        }

        /// <summary>Lands the shells due (once per sim time, whichever AI side asks first).</summary>
        internal void Step()
        {
            var now = _world.Time;
            if (now <= _steppedAt) return;
            _steppedAt = now;
            for (var i = 0; i < _shells.Count; i++)
            {
                var s = _shells[i];
                if (s.Lands > now) continue;
                for (var t = 0; t < _teams.Length; t++)
                {
                    var tc = _teams[t];
                    if (tc == null || t == s.Team) continue;
                    // Observed only where the side had sight of the impact area when it landed (or a vehicle beside it).
                    var intel = _world.Intel.Peek(t);
                    var seen = intel != null && intel.Seen[intel.CellIndex(s.Aim)] >= s.Lands - 1.5;
                    if (!seen) continue;
                    tc.Battery.Impact(s.Aim, s.Lands);
                    tc.Battery.Observe(s.Origin, s.Aim, s.Key, s.Lands);
                }
                _shells.RemoveAt(i--);
            }
            if (_shotCount.Count > 1024) _shotCount.Clear();
        }
    }

    /// <summary>
    /// AI MASTER P3: one side's coordination state, read by its commander, squads and (through the targeting factor) its
    /// weapons: the tactical memory (127-130), the frontline model (124), the planned action board (138-142), the
    /// counter-battery tracker (143-145), route bookings (127) and counterattack windows (212). Refreshed by the commander
    /// (1 Hz); the frontline every <see cref="Tun.Coordination.FrontlineUpdateS"/>.
    /// </summary>
    public sealed class TeamCoordination
    {
        private readonly SimWorld _world;
        private double _frontlineAt = double.NegativeInfinity;
        private readonly List<CounterattackWindow> _windows = new();

        internal TeamCoordination(SimWorld world, int team)
        {
            _world = world;
            Team = team;
            Memory = new TacticalMemory();
            Frontline = new FrontlineModel();
            Board = new PlannedActionBoard();
            Battery = new CounterBatteryTracker();
            Routes = new RouteBook();
        }

        public int Team { get; }
        public TacticalMemory Memory { get; }
        public FrontlineModel Frontline { get; }
        public PlannedActionBoard Board { get; }
        public CounterBatteryTracker Battery { get; }
        public RouteBook Routes { get; }

        /// <summary>Spec 212: the counterattack opportunities open now.</summary>
        public IReadOnlyList<CounterattackWindow> Windows => _windows;

        /// <summary>Spec 225 metrics of this side.</summary>
        public readonly CoordinationMetrics Metrics = new();

        internal void Update(TeamIntel intel, Vector2? objective)
        {
            var now = _world.Time;
            Memory.Refresh(_world, intel, now);
            if (now - _frontlineAt >= Tun.Coordination.FrontlineUpdateS - 1e-6)
            {
                Frontline.Rebuild(_world, intel, Memory, objective, now);
                _frontlineAt = now;
            }
            Board.Prune(now);
            Battery.Prune(now);
            Routes.Prune(now);
            _windows.RemoveAll(w => w.Until <= now);
        }

        /// <summary>Spec 212: an open window at <paramref name="p"/> (within its radius), if any.</summary>
        public CounterattackWindow? WindowNear(Vector2 p, float extra = 0f)
        {
            foreach (var w in _windows)
                if (Vector2.Distance(w.Centre, p) <= w.Radius + extra) return w;
            return null;
        }

        internal void OpenWindow(CounterattackWindow w) => _windows.Add(w);
    }

    /// <summary>Spec 212: a short window after the enemy lost much of its local power (observed losses only).</summary>
    public sealed class CounterattackWindow
    {
        public CounterattackWindow(Vector2 centre, float radius, double until, float lostShare)
        {
            Centre = centre;
            Radius = radius;
            Until = until;
            LostShare = lostShare;
        }

        public Vector2 Centre { get; }
        public float Radius { get; }
        public double Until { get; }
        public float LostShare { get; }

        /// <summary>Opens when the observed loss is at least <paramref name="share"/> of the local power before it.</summary>
        public static bool Opens(float lost, float remaining, float share) => lost > 0f && lost / MathF.Max(0.01f, lost + MathF.Max(0f, remaining)) >= share;
    }

    /// <summary>Spec 225: the advanced metrics a side counts (the lead's runs read them).</summary>
    public sealed class CoordinationMetrics
    {
        public int AttackPackagesCreated, AttackPackagesAborted, SyncStages, FixFlankCount, ScoutRequests;
        public int PlannedOverkillPrevented, DuplicateRepairPrevented, SmokeDeconflicted;
        public int CounterBatteryMissions, CounterBatteryStrikes, ArtilleryScoots, StaleTargetsDropped;
        public int PursuitAbortCount, InterceptCount, CutoffCount, HandoffCount;
        public int ReserveReleases, ReserveKeptWon, ObjectiveMissedDeadlineOrders, SunkCostResets, DepthLineChanges, CounterattackWindows;
        public int RouteRepeatAfterFailure, RouteDiversityChoices, EconomyOfForceMoves, TwoObjectiveSplits;
        public float SyncArrivalDeltaMax;
    }
}
