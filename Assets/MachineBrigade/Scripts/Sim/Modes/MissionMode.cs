#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// A campaign mission: one goal (capture, hold, destroy, escort, survive, boss, intercept),
    /// the enemy's waves, a scripted convoy or boss, a clock, and the losing conditions (the
    /// army wiped out, the clock, the objective lost). The Game layer adds the commander AIs and
    /// points them at <see cref="PlayerGoal"/> and <see cref="EnemyGoal"/>.
    /// </summary>
    public sealed class MissionMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;
        private const float CaptureSeconds = 10f;
        private const float WaypointReach = 5f;

        private readonly MissionDef _def;
        private readonly SideSetup _player;
        private readonly SideSetup? _enemy;
        private readonly List<ObjectiveState> _points = new();
        private readonly List<EntityId> _targets = new();
        private readonly List<(EntityId id, int waypoint)> _convoy = new();
        private readonly HashSet<EntityId> _halted = new();

        /// <summary>A truck drives on only with a friendly vehicle this close: the army leads, the convoy follows.</summary>
        private const float EscortReach = 22f;
        private readonly KillLedger _ledger = new();
        private readonly List<string> _single = new();
        private float _held, _waveTimer, _convoyTimer;
        private int _convoySpawned, _arrived, _wave;
        private double _wipedSince = -1, _heldByEnemySince = -1;
        private EntityId _boss;
        private int _bossWaypoint;

        /// <param name="player">The player's CP and deck (the Game layer passes the unlocked cards).</param>
        /// <param name="enemy">The enemy's economy when it has a commander; null when it only sends waves.</param>
        public MissionMode(MissionDef def, SideSetup player, SideSetup? enemy)
        {
            _def = def;
            _player = player;
            _enemy = enemy;
            _ledger.Ignore = v => v.Scripted || v.Def.Boss;
        }

        public MissionDef Def => _def;

        public IReadOnlyList<ObjectiveState> Points => _points;

        public MatchResult? Result { get; private set; }

        /// <summary>The player's losses so far (scripted trucks and the boss not counted).</summary>
        public int Losses => _ledger.Losses(PlayerTeam);

        public int Kills => _ledger.Kills(PlayerTeam);

        public int Wave => _wave;

        /// <summary>The boss vehicle once it is on the field (invalid before and after).</summary>
        public EntityId Boss => _boss;

        public float SecondsLeft(SimWorld world) => _def.TimeLimit > 0f ? MathF.Max(0f, _def.TimeLimit - (float)world.Time) : -1f;

        /// <summary>How far the goal is (0 to 1).</summary>
        public float Progress(SimWorld world) => _def.Goal switch
        {
            MissionGoal.Capture => _points.Count == 0 ? 0f : PointCapture.Held(_points, PlayerTeam) / (float)_points.Count,
            MissionGoal.Hold => MathF.Min(1f, _held / MathF.Max(1f, _def.HoldSeconds)),
            MissionGoal.Destroy => _targets.Count == 0 ? 1f : 1f - AliveTargets(world) / (float)_targets.Count,
            MissionGoal.Escort => MathF.Min(1f, _arrived / (float)Math.Max(1, _def.ConvoyNeeded)),
            MissionGoal.Survive => MathF.Min(1f, (float)world.Time / MathF.Max(1f, _def.SurviveSeconds)),
            _ => world.TryGetVehicle(_boss, out var boss) ? 1f - boss.Hp / boss.MaxHp : _boss.IsValid ? 1f : 0f,
        };

        /// <summary>Goal counters for the objective panel: done out of needed (e.g. trucks, targets, seconds).</summary>
        public (int done, int needed) Count(SimWorld world) => _def.Goal switch
        {
            MissionGoal.Capture => (PointCapture.Held(_points, PlayerTeam), _points.Count),
            MissionGoal.Hold => ((int)_held, (int)_def.HoldSeconds),
            MissionGoal.Destroy => (_targets.Count - AliveTargets(world), _targets.Count),
            MissionGoal.Escort => (_arrived, _def.ConvoyNeeded),
            MissionGoal.Survive => ((int)world.Time, (int)_def.SurviveSeconds),
            _ => (Result?.WinningTeam == PlayerTeam ? 1 : 0, 1),
        };

        /// <summary>Convoy trucks still driving.</summary>
        public int ConvoyAlive(SimWorld world)
        {
            var alive = 0;
            foreach (var (id, _) in _convoy)
                if (world.TryGetVehicle(id, out var v) && v.IsAlive) alive++;
            return alive;
        }

        public void Setup(SimWorld world)
        {
            world.EnableEconomy(_player.Build(PlayerTeam));
            if (_enemy != null) world.EnableEconomy(_enemy.Build(EnemyTeam));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            foreach (var unit in _def.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);

            // Objectives: the listed ones (all of them when none are listed) for capture; the one
            // held for hold. Other goals fight over none.
            if (_def.Goal is MissionGoal.Capture or MissionGoal.Hold)
                foreach (var p in world.Map.Points)
                {
                    if (_def.Points.Count > 0 && !Contains(_def.Points, p.Id)) continue;
                    if (_def.Goal == MissionGoal.Hold && _points.Count > 0) break;
                    var state = new ObjectiveState(p);
                    if (Contains(_def.EnemyOwns, p.Id)) PointCapture.Own(state, EnemyTeam);
                    else if (_def.Goal == MissionGoal.Hold) PointCapture.Own(state, PlayerTeam);
                    _points.Add(state);
                }
            if (_def.Goal == MissionGoal.Destroy)
                foreach (var prop in world.Props)
                    if (prop.IsAlive && Contains(_def.Targets, prop.Def.Id))
                    {
                        _targets.Add(prop.Id);
                        if (_def.TargetHealth > 1f) prop.Harden(_def.TargetHealth);
                    }

            if (_def.Boss != null)
            {
                var boss = world.SpawnVehicle(_def.Boss.Def, EnemyTeam, _def.Boss.Position, _def.Boss.Heading);
                _boss = boss.Id;
                if (_def.Boss.Route.Count > 0)
                {
                    boss.Scripted = true;
                    Drive(world, boss, _def.Boss.Route[0]);
                }
            }
            _waveTimer = _def.Waves?.First ?? float.MaxValue;
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            foreach (var point in _points) PointCapture.Tick(world, point, dt, CaptureSeconds);
            if (world.TryGetEconomy(PlayerTeam, out var e0)) e0.Bonus = 0.25f * PointCapture.Held(_points, PlayerTeam);
            SpawnWaves(world, dt);
            DriveConvoy(world, dt);
            DriveBoss(world);

            var won = _def.Goal switch
            {
                MissionGoal.Capture => _points.Count > 0 && PointCapture.Held(_points, PlayerTeam) == _points.Count,
                MissionGoal.Hold => (_held += _points.Count > 0 && _points[0].Owner == PlayerTeam ? dt : 0f) >= _def.HoldSeconds,
                MissionGoal.Destroy => AliveTargets(world) == 0,
                MissionGoal.Escort => _arrived >= _def.ConvoyNeeded,
                MissionGoal.Survive => world.Time >= _def.SurviveSeconds,
                _ => _boss.IsValid && (!world.TryGetVehicle(_boss, out var b) || !b.IsAlive),
            };
            if (won)
            {
                Finish(world, PlayerTeam);
                return;
            }
            if (Lost(world)) Finish(world, EnemyTeam);
        }

        /// <summary>Where the player's commander should take the army, or null to let it choose.</summary>
        public Vector2? PlayerGoal(SimWorld world) => _def.Goal switch
        {
            MissionGoal.Hold => _points.Count > 0 ? _points[0].Def.Position : null,
            MissionGoal.Destroy => NearestTarget(world),
            MissionGoal.Escort => ConvoyFront(world),
            MissionGoal.Boss or MissionGoal.Intercept => world.TryGetVehicle(_boss, out var b) && b.IsAlive ? b.Position : null,
            _ => null,
        };

        /// <summary>Where the enemy goes: the held point, the convoy, the player's camp when surviving.</summary>
        public Vector2? EnemyGoal(SimWorld world)
        {
            switch (_def.Goal)
            {
                case MissionGoal.Hold:
                    return _points.Count > 0 ? _points[0].Def.Position : null;
                case MissionGoal.Escort:
                    return ConvoyFront(world);
                case MissionGoal.Destroy:
                    return NearestTarget(world);
                case MissionGoal.Survive:
                case MissionGoal.Boss:
                case MissionGoal.Intercept:
                    return world.TryGetRally(PlayerTeam, out var home) ? PlayerCentre(world) ?? home : null;
                default:
                    return null;
            }
        }

        private bool Lost(SimWorld world)
        {
            if (_def.TimeLimit > 0f && world.Time >= _def.TimeLimit && _def.Goal != MissionGoal.Survive) return true;
            // The held objective is lost only when the enemy keeps it for a while: time to hit back.
            if (_def.Goal == MissionGoal.Hold && _points.Count > 0)
            {
                var enemyHolds = _points[0].Owner == EnemyTeam;
                _heldByEnemySince = enemyHolds ? (_heldByEnemySince < 0 ? world.Time : _heldByEnemySince) : -1;
                if (_heldByEnemySince >= 0 && world.Time - _heldByEnemySince > 25.0) return true;
            }
            if (_def.Goal == MissionGoal.Escort && _convoySpawned >= _def.ConvoyCount && _arrived + ConvoyAlive(world) < _def.ConvoyNeeded)
                return true;
            if (_def.Goal == MissionGoal.Intercept && world.TryGetVehicle(_boss, out var train) && train.IsAlive &&
                _def.Boss != null && _bossWaypoint >= _def.Boss.Route.Count) return true;
            // The army wiped out for a while (nothing alive or on the way).
            var wiped = world.TryGetEconomy(PlayerTeam, out var economy) && economy.ArmyCp == 0 && world.Time > 5.0;
            _wipedSince = wiped ? (_wipedSince < 0 ? world.Time : _wipedSince) : -1;
            return _wipedSince >= 0 && world.Time - _wipedSince > 12.0;
        }

        private void Finish(SimWorld world, int winner)
        {
            Result = new MatchResult(winner);
            world.IsOver = true;
        }

        private void SpawnWaves(SimWorld world, float dt)
        {
            var waves = _def.Waves;
            if (waves == null || waves.Roster.Count == 0) return;
            _waveTimer -= dt;
            if (_waveTimer > 0f) return;
            _waveTimer = waves.Interval;
            if (world.CountAlive(EnemyTeam) >= waves.MaxAlive) return;
            _wave++;
            var count = Math.Min(waves.MaxSize, waves.Size + (int)MathF.Floor(waves.Grow * (_wave - 1)));
            Vector2 origin;
            if (waves.Spawns.Count > 0) origin = waves.Spawns[_wave % waves.Spawns.Count];
            else if (!world.TryGetRally(EnemyTeam, out origin)) return;
            for (var i = 0; i < count; i++)
            {
                var def = waves.Roster[(_wave * 3 + i) % waves.Roster.Count];
                var angle = i * SimMath.Tau / Math.Max(1, count);
                var at = world.ClampToMap(origin + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * 8f);
                world.SpawnVehicle(def, EnemyTeam, at, SimMath.DegToRad(225f));
            }
        }

        private void DriveConvoy(SimWorld world, float dt)
        {
            var convoy = _def.Convoy;
            if (convoy == null || _def.Goal != MissionGoal.Escort) return;
            _convoyTimer -= dt;
            if (_convoySpawned < _def.ConvoyCount && _convoyTimer <= 0f)
            {
                // One truck every few seconds, so they leave as a column instead of a pile.
                _convoyTimer = 4f;
                _convoySpawned++;
                var truck = world.SpawnVehicle(convoy.Def, PlayerTeam, convoy.Position, convoy.Heading);
                truck.Scripted = true;
                _convoy.Add((truck.Id, 0));
                if (convoy.Route.Count > 0) Drive(world, truck, convoy.Route[0]);
            }
            for (var i = 0; i < _convoy.Count; i++)
            {
                var (id, waypoint) = _convoy[i];
                if (waypoint >= convoy.Route.Count || !world.TryGetVehicle(id, out var truck) || !truck.IsAlive) continue;
                // Unescorted trucks stop and wait rather than drive alone into an ambush.
                var escorted = Escorted(world, truck);
                if (!escorted && !_halted.Contains(id))
                {
                    _halted.Add(id);
                    world.Submit(new Command(CommandType.Stop, PlayerTeam, new[] { id }));
                }
                else if (escorted && _halted.Remove(id)) Drive(world, truck, convoy.Route[waypoint]);
                if (!escorted) continue;
                if (Vector2.Distance(truck.Position, convoy.Route[waypoint]) > WaypointReach) continue;
                waypoint++;
                _convoy[i] = (id, waypoint);
                if (waypoint >= convoy.Route.Count) _arrived++;
                else Drive(world, truck, convoy.Route[waypoint]);
            }
        }

        private static bool Escorted(SimWorld world, Vehicle truck)
        {
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == PlayerTeam && !v.Scripted && !v.Flying &&
                    Vector2.DistanceSquared(v.Position, truck.Position) < EscortReach * EscortReach) return true;
            return false;
        }

        private void DriveBoss(SimWorld world)
        {
            var route = _def.Boss?.Route;
            if (route == null || route.Count == 0 || _bossWaypoint >= route.Count) return;
            if (!world.TryGetVehicle(_boss, out var boss) || !boss.IsAlive) return;
            if (Vector2.Distance(boss.Position, route[_bossWaypoint]) > WaypointReach) return;
            _bossWaypoint++;
            if (_bossWaypoint < route.Count) Drive(world, boss, route[_bossWaypoint]);
        }

        private void Drive(SimWorld world, Vehicle vehicle, Vector2 to)
        {
            var units = new[] { vehicle.Id };
            world.Submit(new Command(CommandType.Move, vehicle.Team, units, world.ClampToMap(to)));
        }

        private int AliveTargets(SimWorld world)
        {
            var alive = 0;
            foreach (var id in _targets)
                if (world.TryGetProp(id, out var p) && p.IsAlive) alive++;
            return alive;
        }

        /// <summary>The demolition target the player's commander should shoot at, or none.</summary>
        public EntityId PlayerDemolish(SimWorld world) => _def.Goal == MissionGoal.Destroy ? NearestTargetId(world) : EntityId.None;

        private Vector2? NearestTarget(SimWorld world) =>
            world.TryGetProp(NearestTargetId(world), out var p) ? p.Position : null;

        private EntityId NearestTargetId(SimWorld world)
        {
            var best = EntityId.None;
            var bestDistance = float.MaxValue;
            var from = PlayerCentre(world) ?? Vector2.Zero;
            foreach (var id in _targets)
            {
                if (!world.TryGetProp(id, out var p) || !p.IsAlive) continue;
                var d = Vector2.DistanceSquared(from, p.Position);
                if (d >= bestDistance) continue;
                bestDistance = d;
                best = id;
            }
            return best;
        }

        /// <summary>The lead truck still driving, a little ahead of it along its route.</summary>
        private Vector2? ConvoyFront(SimWorld world)
        {
            foreach (var (id, waypoint) in _convoy)
            {
                if (!world.TryGetVehicle(id, out var truck) || !truck.IsAlive || _def.Convoy == null) continue;
                if (waypoint >= _def.Convoy.Route.Count) continue;
                var next = _def.Convoy.Route[waypoint];
                var ahead = next - truck.Position;
                return ahead.LengthSquared() > 1f ? truck.Position + Vector2.Normalize(ahead) * 8f : truck.Position;
            }
            return null;
        }

        private static Vector2? PlayerCentre(SimWorld world)
        {
            var sum = Vector2.Zero;
            var count = 0;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != PlayerTeam || v.Flying) continue;
                sum += v.Position;
                count++;
            }
            return count > 0 ? sum / count : null;
        }

        private static bool Contains(IReadOnlyList<string> list, string id)
        {
            foreach (var s in list)
                if (s == id) return true;
            return false;
        }
    }
}
