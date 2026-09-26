#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Movement;
using MachineBrigade.Sim.Navigation;
using MachineBrigade.Sim.Strikes;

namespace MachineBrigade.Sim
{
    /// <summary>
    /// The authoritative battlefield. Advances in fixed steps, accepts commands through
    /// <see cref="Submit"/> and reports what happened through <see cref="Events"/>.
    /// Contains no engine types, so it runs identically in tests and in the game.
    /// </summary>
    public sealed class SimWorld
    {
        /// <summary>Extra margin around blocking props so hulls stay out of walls.</summary>
        public const float ObstacleClearance = 1.5f;

        private readonly Dictionary<EntityId, Vehicle> _vehicles = new();
        private readonly List<Vehicle> _vehicleList = new();
        private readonly Dictionary<EntityId, Prop> _props = new();
        private readonly List<Prop> _propList = new();
        private readonly List<SimEvent> _events = new();
        private readonly Dictionary<int, Vector2> _rally = new();
        private readonly PathFinder _pathFinder;
        private readonly List<Vector2> _pathBuffer = new();
        private readonly List<Vehicle> _unitBuffer = new();
        private readonly Dictionary<EntityId, Vector2> _slotBuffer = new();
        private readonly MovementSystem _movement;
        private readonly CombatSystem _combat;
        private int _nextId = 1;

        public SimWorld(Catalog catalog, MapDefinition map, int seed = 1, int generation = 1)
        {
            Catalog = catalog ?? throw new ArgumentNullException(nameof(catalog));
            Map = map ?? throw new ArgumentNullException(nameof(map));
            Generation = generation;
            Random = new Random(seed);
            Grid = new NavGrid(map.Size, 2f);
            _pathFinder = new PathFinder(Grid);
            Damage = new DamageSystem(this);
            _movement = new MovementSystem(this);
            _combat = new CombatSystem(this);
            Economy = new EconomySystem(this);
            Strikes = new StrikeSystem(this);

            foreach (var team in map.Teams) _rally[team.Team] = team.Rally;
            foreach (var placement in map.Props) SpawnProp(placement.DefId, placement.Position, placement.Rotation);
        }

        public Catalog Catalog { get; }
        public MapDefinition Map { get; }
        public NavGrid Grid { get; }

        /// <summary>Distinguishes matches, so references from before a restart never apply.</summary>
        public int Generation { get; }

        public long Tick { get; private set; }

        /// <summary>Simulated seconds since the match started.</summary>
        public double Time { get; private set; }

        /// <summary>Set by the game mode when the match ends; commands are refused afterwards.</summary>
        public bool IsOver { get; set; }

        /// <summary>Vehicles that are alive (dead ones leave at the end of the step they die in).</summary>
        public IReadOnlyList<Vehicle> Vehicles => _vehicleList;

        /// <summary>All props, including destroyed ones (check <see cref="Prop.IsAlive"/>).</summary>
        public IReadOnlyList<Prop> Props => _propList;

        /// <summary>Events since the last <see cref="ClearEvents"/>.</summary>
        public IReadOnlyList<SimEvent> Events => _events;

        public int PendingExplosionCount => Damage.PendingCount;

        internal Random Random { get; }
        internal DamageSystem Damage { get; }
        internal EconomySystem Economy { get; }
        internal StrikeSystem Strikes { get; }

        /// <summary>Gives a side Command Points and a deck; modes without an economy never call this.</summary>
        public void EnableEconomy(TeamEconomy economy) => Economy.Enable(economy);

        public bool TryGetEconomy(int team, out TeamEconomy economy) => Economy.TryGet(team, out economy);

        /// <summary>Smoke clouds on the field: (centre, radius).</summary>
        public IEnumerable<(Vector2 centre, float radius)> SmokeClouds()
        {
            foreach (var zone in Strikes.Smoke) yield return (zone.Centre, zone.Radius);
        }
        internal List<Vehicle> VehicleList => _vehicleList;
        internal List<Prop> PropList => _propList;

        public void ClearEvents() => _events.Clear();

        public bool TryGetVehicle(EntityId id, out Vehicle vehicle) => _vehicles.TryGetValue(id, out vehicle!);

        public bool TryGetProp(EntityId id, out Prop prop) => _props.TryGetValue(id, out prop!);

        public bool TryGetTarget(EntityId id, out IDamageable target)
        {
            if (_vehicles.TryGetValue(id, out var v)) { target = v; return true; }
            if (_props.TryGetValue(id, out var p)) { target = p; return true; }
            target = null!;
            return false;
        }

        public bool TryGetRally(int team, out Vector2 rally) => _rally.TryGetValue(team, out rally);

        public int CountAlive(int team)
        {
            var count = 0;
            foreach (var v in _vehicleList)
                if (v.IsAlive && v.Team == team) count++;
            return count;
        }

        /// <summary>Places a vehicle; used by game modes for starting forces and reinforcements.</summary>
        public Vehicle SpawnVehicle(string defId, int team, Vector2 position, float heading)
        {
            var def = Catalog.Vehicle(defId);
            var at = def.Flying ? ClampToMap(position) : Grid.TryNearestWalkable(position, 8, out var walkable) ? walkable : position;
            var vehicle = new Vehicle(NextId(), def, team, at, heading);
            _vehicles.Add(vehicle.Id, vehicle);
            _vehicleList.Add(vehicle);
            Emit(SimEvent.Spawned(vehicle));
            return vehicle;
        }

        public CommandResult Submit(Command command)
        {
            if (IsOver) return CommandResult.Rejected(CommandError.MatchOver);
            if (command.Type == CommandType.Deploy) return Economy.Deploy(command.Team, command.DefId);
            if (command.Type == CommandType.Strike) return Strikes.Call(command);

            _unitBuffer.Clear();
            foreach (var id in command.Units)
                if (_vehicles.TryGetValue(id, out var v) && v.IsAlive && v.Team == command.Team && !_unitBuffer.Contains(v))
                    _unitBuffer.Add(v);
            if (_unitBuffer.Count == 0) return CommandResult.Rejected(CommandError.NoUnits);
            if (command.Manual)
                foreach (var v in _unitBuffer) v.ManualOrder = true;

            switch (command.Type)
            {
                case CommandType.Stop:
                    foreach (var v in _unitBuffer)
                    {
                        v.SetOrder(Order.Idle);
                        v.ClearPath();
                        v.Target = EntityId.None;
                    }
                    return CommandResult.Ok;

                case CommandType.Move:
                case CommandType.AttackMove:
                    if (!SimMath.IsFinite(command.Point)) return CommandResult.Rejected(CommandError.InvalidPoint);
                    if (!Map.Contains(command.Point)) return CommandResult.Rejected(CommandError.OutOfBounds);
                    IssueGroupMove(command.Point, command.Type == CommandType.Move ? OrderKind.Move : OrderKind.AttackMove);
                    return CommandResult.Ok;

                case CommandType.Retreat:
                    if (!_rally.TryGetValue(command.Team, out var rally)) return CommandResult.Rejected(CommandError.NoRallyPoint);
                    IssueGroupMove(rally, OrderKind.Retreat);
                    return CommandResult.Ok;

                case CommandType.Attack:
                    if (!TryGetTarget(command.Target, out var target) || !target.IsAlive || target.Team == command.Team)
                        return CommandResult.Rejected(CommandError.InvalidTarget);
                    if (target is Vehicle enemy && !enemy.IsVisibleTo(command.Team))
                        return CommandResult.Rejected(CommandError.TargetNotVisible);
                    if (target is Prop { Def: { Indestructible: true } }) return CommandResult.Rejected(CommandError.InvalidTarget);
                    // Only vehicles whose main weapon can reach it (tank guns cannot hit aircraft) take the order.
                    var flying = target is Vehicle { Flying: true };
                    var ordered = 0;
                    foreach (var v in _unitBuffer)
                    {
                        if (!v.Def.Weapon.CanTarget(flying)) continue;
                        v.SetOrder(new Order(OrderKind.Attack, target.Position, target.Id));
                        ordered++;
                    }
                    return ordered > 0 ? CommandResult.Ok : CommandResult.Rejected(CommandError.InvalidTarget);

                default:
                    throw new ArgumentOutOfRangeException(nameof(command), command.Type, "Unknown command type.");
            }
        }

        /// <summary>Advances the battlefield by one fixed step of <paramref name="dt"/> seconds.</summary>
        public void Step(float dt)
        {
            Tick++;
            Time += dt;
            RefreshVisibility();
            Economy.Step(dt);
            _movement.Step(dt);
            _combat.Step(dt);
            Strikes.Step();
            Damage.Step();
            RemoveDead();
        }

        internal void Emit(in SimEvent e) => _events.Add(e);

        /// <summary>Lets game modes report what they decide (objectives changing hands).</summary>
        public void Announce(in SimEvent e) => _events.Add(e);

        /// <summary>Paths a vehicle towards <paramref name="goal"/>; on failure it simply stops.</summary>
        internal bool PathTo(Vehicle vehicle, Vector2 goal)
        {
            vehicle.RepathTimer = 0.5f;
            if (vehicle.Flying)
            {
                // Aircraft fly straight over buildings, wrecks and rivers.
                _pathBuffer.Clear();
                _pathBuffer.Add(ClampToMap(goal));
                vehicle.SetPath(_pathBuffer, goal);
                return true;
            }
            if (_pathFinder.TryFindPath(vehicle.Position, goal, _pathBuffer))
            {
                vehicle.SetPath(_pathBuffer, goal);
                return true;
            }
            vehicle.ClearPath();
            return false;
        }

        /// <summary>Nearest living enemy vehicle within <paramref name="range"/> of the edge of its hull.</summary>
        internal Vehicle? FindNearestEnemy(Vehicle from, float range, bool requireVisible, float minRange = 0f,
            TargetLayers layers = TargetLayers.All)
        {
            Vehicle? best = null;
            var bestDistance = float.MaxValue;
            foreach (var other in _vehicleList)
            {
                if (!other.IsAlive || other.Team == from.Team) continue;
                if ((layers & (other.Flying ? TargetLayers.Air : TargetLayers.Ground)) == 0) continue;
                if (requireVisible && !other.IsVisibleTo(from.Team)) continue;
                var centre = Vector2.Distance(from.Position, other.Position);
                if (centre < minRange || centre - other.Radius > range || centre >= bestDistance) continue;
                best = other;
                bestDistance = centre;
            }
            return best;
        }

        private void IssueGroupMove(Vector2 point, OrderKind kind)
        {
            var spacing = 1.5f;
            foreach (var v in _unitBuffer) spacing = MathF.Max(spacing, v.Radius * 2f + 1.5f);
            var slots = Formation.Slots(point, _unitBuffer.Count, spacing, Grid);
            Formation.Assign(_unitBuffer, slots, point, _slotBuffer);
            foreach (var v in _unitBuffer)
            {
                var goal = _slotBuffer.TryGetValue(v.Id, out var slot) ? slot : point;
                v.SetOrder(new Order(kind, goal, EntityId.None));
                PathTo(v, goal);
            }
        }

        private void SpawnProp(string defId, Vector2 position, int rotation)
        {
            var prop = new Prop(NextId(), Catalog.Prop(defId), position, rotation);
            _props.Add(prop.Id, prop);
            _propList.Add(prop);
            if (prop.Def.BlocksMovement) Grid.AddBlocker(prop.Position, prop.Width, prop.Depth, ObstacleClearance);
        }

        private void RefreshVisibility()
        {
            foreach (var target in _vehicleList)
            {
                var mask = 0;
                foreach (var spotter in _vehicleList)
                {
                    if (!spotter.IsAlive || spotter.Team < 0 || spotter.Team > 30) continue;
                    if (spotter.Team == target.Team ||
                        (Vector2.DistanceSquared(spotter.Position, target.Position) <= spotter.Def.VisionRange * spotter.Def.VisionRange &&
                         !Strikes.Obscures(spotter.Position, target.Position)))
                        mask |= 1 << spotter.Team;
                }
                target.VisibleToMask = mask;
            }
        }

        private void RemoveDead()
        {
            for (var i = _vehicleList.Count - 1; i >= 0; i--)
            {
                var v = _vehicleList[i];
                if (v.IsAlive) continue;
                _vehicleList.RemoveAt(i);
                _vehicles.Remove(v.Id);
            }
        }

        private EntityId NextId() => new EntityId(_nextId++);

        internal Vector2 ClampToMap(Vector2 p)
        {
            var limit = Map.HalfSize - 1f;
            return new Vector2(Math.Clamp(p.X, -limit, limit), Math.Clamp(p.Y, -limit, limit));
        }
    }
}
