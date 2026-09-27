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
        private readonly Abilities.AbilitySystem _abilities;
        private int _nextId = 1;

        public SimWorld(Catalog catalog, MapDefinition map, int seed = 1, int generation = 1)
        {
            Catalog = catalog ?? throw new ArgumentNullException(nameof(catalog));
            Map = map ?? throw new ArgumentNullException(nameof(map));
            Generation = generation;
            Random = new Random(seed);
            Grid = new NavGrid(map.Size, 2f);
            Cover = new CoverGrid(map.Size);
            if (map.Boundary.Count >= 3)
            {
                // Beyond the outline is terrain: no driving there, and it stops direct fire.
                Grid.BlockWhere(map.InsideBoundary);
                Cover.BlockWhere(map.InsideBoundary);
            }
            _pathFinder = new PathFinder(Grid);
            _lanes = new LaneMap(Grid);
            Damage = new DamageSystem(this);
            _movement = new MovementSystem(this);
            _combat = new CombatSystem(this);
            _abilities = new Abilities.AbilitySystem(this);
            Economy = new EconomySystem(this);
            Strikes = new StrikeSystem(this);

            foreach (var team in map.Teams) _rally[team.Team] = team.Rally;
            foreach (var placement in map.Props) SpawnProp(placement.DefId, placement.Position, placement.Rotation);
        }

        public Catalog Catalog { get; }
        public MapDefinition Map { get; }
        public NavGrid Grid { get; }

        /// <summary>Where direct fire cannot pass (tall props); see <see cref="CoverGrid"/>.</summary>
        public CoverGrid Cover { get; }

        private readonly LaneMap _lanes;

        /// <summary>
        /// Roads, main routes and doorways (where nobody may stop), rebuilt when a wall falls; see
        /// <see cref="LaneMap"/>.
        /// </summary>
        public LaneMap Lanes
        {
            get
            {
                _lanes.RebuildIfDirty(this);
                return _lanes;
            }
        }

        /// <summary>Whether <paramref name="shooter"/> has a clear line of fire at <paramref name="target"/> with <paramref name="weapon"/>.</summary>
        internal bool HasLineOfFire(Vehicle shooter, IDamageable target, WeaponDef weapon) => _combat.HasLineOfFire(shooter, target, weapon);

        /// <summary>The fire-blocking prop standing at <paramref name="p"/>, if any.</summary>
        internal Prop? CoverAt(Vector2 p)
        {
            foreach (var prop in _propList)
                if (prop.IsAlive && prop.Def.BlocksFire && CoverGrid.Inside(prop, p)) return prop;
            return null;
        }

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

        /// <summary>The driving and traffic rules (tests read its path-search budget).</summary>
        internal MovementSystem Movement => _movement;

        internal DamageSystem Damage { get; }
        internal EconomySystem Economy { get; }
        internal StrikeSystem Strikes { get; }
        internal Abilities.AbilitySystem Abilities => _abilities;

        internal readonly List<Crate> CrateList = new();

        /// <summary>Supply crates falling or waiting on the field (battle events).</summary>
        public IReadOnlyList<Crate> Crates => CrateList;

        /// <summary>Mines on the field (see <see cref="Mine.IsVisibleTo"/> for who can see them).</summary>
        public IReadOnlyList<Mine> Mines => _abilities.Mines;

        /// <summary>A guided missile or drone is flying at this vehicle.</summary>
        internal bool MissileIncoming(EntityId vehicle) => _combat.MissileIncoming(vehicle);

        /// <summary>Gives a side Command Points and a deck; modes without an economy never call this.</summary>
        /// <summary>
        /// Home zones (the capture modes): within <see cref="HomeRadius"/> of its own camp a
        /// vehicle repairs 2 % of its health a second once it has not been hit for 3 s, a newly
        /// arrived vehicle takes a fifth of the damage for its first 5 s, and the enemy cannot call
        /// strikes into the zone.
        /// </summary>
        public bool HomeZones { get; set; }

        public const float HomeRadius = 35f;

        /// <summary>
        /// Catch-up (the quick modes): the side losing the war of armies is reinforced faster and
        /// paid more for its kills (see <see cref="Economy.EconomySystem"/>).
        /// </summary>
        public bool CatchUp { get; set; }

        private readonly int[] _strikesCalled = new int[2];
        private readonly int[] _aircraftBought = new int[2];

        /// <summary>Fire support a side has called this battle (a mission's "no strikes" star).</summary>
        public int StrikesCalled(int team) => team is 0 or 1 ? _strikesCalled[team] : 0;

        /// <summary>Aircraft a side has bought this battle (a mission's "no aircraft" star).</summary>
        public int AircraftBought(int team) => team is 0 or 1 ? _aircraftBought[team] : 0;

        internal void CountStrike(int team)
        {
            if (team is 0 or 1) _strikesCalled[team]++;
        }

        internal void CountAircraft(int team)
        {
            if (team is 0 or 1) _aircraftBought[team]++;
        }

        /// <summary>
        /// Takes a vehicle off the field without a trace (no blast, no wreck, no event): a
        /// defence already destroyed in an earlier attack on the weekly fortress.
        /// </summary>
        internal void RemoveQuietly(Vehicle v)
        {
            if (!_vehicles.ContainsKey(v.Id)) return;
            v.Hp = 0f;
            _vehicleList.Remove(v);
            _vehicles.Remove(v.Id);
            if (v.BlocksRoutes) Grid.RemoveBlocker(v.Position, StaticFootprint(v.Def), StaticFootprint(v.Def), ObstacleClearance);
        }

        /// <summary>Knocks a prop down without a blast: its ground and line of fire open (the view shows its rubble).</summary>
        internal void RemoveQuietly(Prop prop)
        {
            if (!prop.IsAlive) return;
            prop.Hp = 0f;
            if (prop.Def.BlocksMovement) Grid.RemoveBlocker(prop.Position, prop.Width, prop.Depth, ObstacleClearance);
            if (prop.Def.BlocksFire) Cover.Remove(prop);
        }

        /// <summary>Device check: takes a share of a vehicle's health (a defence burning down on camera).</summary>
        public void DebugDamage(Vehicle v, float fraction) => Damage.Apply(v, v.MaxHp * fraction, DamageType.HighExplosive);

        private readonly bool[] _entrench = new bool[2];

        /// <summary>
        /// A side told to dig in (its commander's Defend stance): its ground vehicles that have
        /// stood still for <see cref="EntrenchSeconds"/> go hull-down and take
        /// <see cref="EntrenchReduction"/> less damage from direct fire (guns and bullets; not
        /// artillery, rockets or bombs, the way to dig them out), until they move again.
        /// </summary>
        public void Entrench(int team, bool on)
        {
            if (team >= 0 && team < _entrench.Length) _entrench[team] = on;
        }

        public const float EntrenchSeconds = 3f;
        public const float EntrenchReduction = 0.2f;

        /// <summary>Hull-down: its side is dug in and it has not moved for a while.</summary>
        public bool IsEntrenched(Vehicle v) =>
            v.Team >= 0 && v.Team < _entrench.Length && _entrench[v.Team] && !v.Flying && !v.Def.Static &&
            Time - v.StillSince >= EntrenchSeconds;

        /// <summary>Whether a point lies in another side's home zone (strikes cannot be called there).</summary>
        internal bool InEnemyHome(Vector2 point, int team)
        {
            if (!HomeZones) return false;
            foreach (var start in Map.Teams)
                if (start.Team != team && Vector2.Distance(start.Rally, point) < HomeRadius) return true;
            return false;
        }

        public void EnableEconomy(TeamEconomy economy)
        {
            // The catalog sets the pace of every economy (see balance.json "economy").
            economy.IncomeScale = Catalog.IncomeScale;
            economy.SupplyScale = Catalog.SupplyScale;
            Economy.Enable(economy);
        }

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

        /// <summary>Moves a side's drop zone (an Assault attacker moving up behind the sector it took).</summary>
        public void SetRally(int team, Vector2 rally) => _rally[team] = ClampToMap(rally);

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
            if (!def.Flying && !def.Static) at = FreeSpot(def, at);
            var vehicle = new Vehicle(NextId(), def, team, at, heading);
            if (team >= 0 && team < _boosts.Length && _boosts[team] is { } boosts && !def.Boss && !def.Static) Upgrade(vehicle, boosts(def));
            if (Economy.TryGet(team, out var economy) && economy.Doctrine is { } doctrine && !def.Boss && !def.Static)
            {
                vehicle.HpScale = doctrine.Toughness(def.Class) * vehicle.BoostHp;
                vehicle.DoctrineSpeed = doctrine.Speed * vehicle.BoostSpeed;
            }
            vehicle.Hp = vehicle.MaxHp;
            _vehicles.Add(vehicle.Id, vehicle);
            _vehicleList.Add(vehicle);
            // A fixed defence stands on its ground like a building from the start, wherever it came
            // from (a map's fortress as much as a mode's tower): routes go round it instead of into it.
            if (def.Static) AnchorDefence(vehicle);
            Emit(SimEvent.Spawned(vehicle));
            if (HomeZones && !vehicle.Def.Static) vehicle.GraceUntil = Time + 5.0;
            return vehicle;
        }

        private readonly Func<VehicleDef, VehicleBoost>?[] _boosts = new Func<VehicleDef, VehicleBoost>?[3];
        private readonly Func<string, float>?[] _strikeBoosts = new Func<string, float>?[3];

        /// <summary>
        /// A side's upgrades (card ranks and equipment): what each of its vehicles gets as it enters
        /// the battle (null: none). Set before the forces are placed.
        /// </summary>
        public void SetBoosts(int team, Func<VehicleDef, VehicleBoost>? boosts, Func<string, float>? strikeDamage = null)
        {
            if (team < 0 || team >= _boosts.Length) return;
            _boosts[team] = boosts;
            _strikeBoosts[team] = strikeDamage;
        }

        /// <summary>How much harder a side's fire support of this kind hits (its card's rank).</summary>
        internal float StrikeDamage(int team, string supportId) =>
            team >= 0 && team < _strikeBoosts.Length && _strikeBoosts[team] is { } boost ? boost(supportId) : 1f;

        private static void Upgrade(Vehicle v, VehicleBoost b)
        {
            v.BoostHp = b.Hp;
            v.BoostSpeed = b.Speed;
            v.HpScale = b.Hp;
            v.DoctrineSpeed = b.Speed;
            v.DamageBoost = b.Damage;
            v.FireBoost = b.FireRate;
            v.DamageTaken = b.DamageTaken;
            v.Regen = b.Regen;
            v.Special = b.Special;
            v.SpecialPower = b.SpecialPower;
            switch (b.Special)
            {
                case SpecialModule.ReactiveArmor:
                    v.DamageTaken *= 1f - b.SpecialPower;
                    break;
                case SpecialModule.AutoRepair:
                    v.Regen += b.SpecialPower;
                    break;
                case SpecialModule.VeteranCrew:
                    v.DamageBoost *= 1f + b.SpecialPower;
                    v.FireBoost *= 1f + b.SpecialPower;
                    break;
            }
        }

        /// <summary>
        /// Gives a side its doctrine for the battle; vehicles already on the field are toughened
        /// (or sped up) in place, keeping their share of health.
        /// </summary>
        public void SetDoctrine(int team, Doctrine? doctrine)
        {
            if (!Economy.TryGet(team, out var economy)) return;
            economy.Doctrine = doctrine;
            foreach (var v in _vehicleList)
            {
                if (!v.IsAlive || v.Team != team || v.Def.Boss || v.Def.Static) continue;
                var share = v.Hp / v.MaxHp;
                v.HpScale = (doctrine?.Toughness(v.Def.Class) ?? 1f) * v.BoostHp;
                v.DoctrineSpeed = (doctrine?.Speed ?? 1f) * v.BoostSpeed;
                v.Hp = v.MaxHp * share;
            }
        }

        /// <summary>
        /// The nearest walkable spot to <paramref name="at"/> where a new hull does not land on top
        /// of another vehicle (searching outwards in rings), or <paramref name="at"/> if none is near.
        /// </summary>
        private Vector2 FreeSpot(VehicleDef def, Vector2 at)
        {
            for (var ring = 0; ring <= 6; ring++)
            {
                var steps = ring == 0 ? 1 : ring * 8;
                for (var k = 0; k < steps; k++)
                {
                    var angle = k * SimMath.Tau / steps;
                    var p = at + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (ring * 2.5f);
                    if (!Map.Contains(p) || !Grid.IsWalkable(p)) continue;
                    var clear = true;
                    foreach (var other in _vehicleList)
                    {
                        if (!other.IsAlive || other.Flying) continue;
                        var gap = def.HullBound * 0.8f + other.Def.HullBound * 0.8f;
                        if (Vector2.DistanceSquared(other.Position, p) < gap * gap) { clear = false; break; }
                    }
                    if (clear) return p;
                }
            }
            return at;
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
            var result = Apply(command);
            // Only units that actually took the order are kept out of the commander AI's hands.
            if (command.Manual && result.Accepted)
                foreach (var v in _unitBuffer)
                    if (command.Type != CommandType.Attack || v.Order.Kind == OrderKind.Attack) v.ManualOrder = true;
            return result;
        }

        private CommandResult Apply(Command command)
        {

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
                    if (target is Prop { Def: { Indestructible: true } } or Vehicle { Invulnerable: true }) return CommandResult.Rejected(CommandError.InvalidTarget);
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
            CrushVegetation();
            _abilities.Step(dt);
            _combat.Step(dt);
            Strikes.Step();
            Damage.Step();
            RemoveDead();
        }

        internal void Emit(in SimEvent e) => _events.Add(e);

        /// <summary>Turns a vehicle into a firing-range target (see <see cref="Vehicle.Dummy"/>).</summary>
        public void MakeDummy(Vehicle v)
        {
            v.Dummy = true;
            v.RefreshEffects(Time);
        }

        private const float CrushCell = 6f;
        private Dictionary<(int, int), List<Prop>>? _crushable;

        /// <summary>Ground vehicles knock down the trees, bushes, hedges and fences they drive into.</summary>
        private void CrushVegetation()
        {
            if (_crushable == null)
            {
                _crushable = new Dictionary<(int, int), List<Prop>>();
                foreach (var prop in _propList)
                {
                    if (!prop.IsAlive || !prop.Def.Crushable) continue;
                    var key = ((int)MathF.Floor(prop.Position.X / CrushCell), (int)MathF.Floor(prop.Position.Y / CrushCell));
                    if (!_crushable.TryGetValue(key, out var list)) _crushable[key] = list = new List<Prop>();
                    list.Add(prop);
                }
            }
            if (_crushable.Count == 0) return;
            foreach (var v in _vehicleList)
            {
                if (!v.IsAlive || v.Flying || v.Def.Static || v.Speed < 0.5f) continue;
                var cx = (int)MathF.Floor(v.Position.X / CrushCell);
                var cy = (int)MathF.Floor(v.Position.Y / CrushCell);
                for (var dx = -1; dx <= 1; dx++)
                    for (var dy = -1; dy <= 1; dy++)
                    {
                        if (!_crushable.TryGetValue((cx + dx, cy + dy), out var list)) continue;
                        foreach (var prop in list)
                        {
                            if (!prop.IsAlive) continue;
                            var reach = v.Def.HullRadius + 0.3f + prop.Radius * 0.5f;
                            if (Vector2.DistanceSquared(v.Position, prop.Position) < reach * reach)
                                Damage.Crush(prop, SimMath.Forward(v.Heading));
                        }
                    }
            }
        }

        /// <summary>Development only (the -mb-demolish device check): blows a prop apart as a heavy shell would.</summary>
        public void DebugDestroyProp(Prop prop)
        {
            if (prop.IsAlive) Damage.Apply(prop, prop.Hp * 10f + 10000f, DamageType.HighExplosive);
        }

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
        private static readonly float[] EscapeBearings =
        {
            0f, SimMath.DegToRad(35f), -SimMath.DegToRad(35f), SimMath.DegToRad(70f), -SimMath.DegToRad(70f),
            SimMath.DegToRad(110f), -SimMath.DegToRad(110f),
        };

        /// <summary>
        /// Where a vehicle can back off to from a threat, up to <paramref name="distance"/> away:
        /// of the bearings away from it (straight back, then angled up to 110 degrees either side)
        /// and the way to its own camp, the open spot that gains the most distance from the threat,
        /// kept off the map's edge. Null when it is cornered (no way out of 4 m or more): it
        /// stands and fights with what it has instead of pushing into the edge.
        /// </summary>
        internal Vector2? EscapeRoute(Vehicle v, Vector2 threat, float distance)
        {
            distance = MathF.Max(distance, 6f);
            var away = v.Position - threat;
            var back = away.LengthSquared() > 0.01f ? Vector2.Normalize(away) : SimMath.Forward(v.Heading + MathF.PI);
            var bearings = new List<Vector2>(EscapeBearings.Length + 1);
            foreach (var turn in EscapeBearings)
            {
                var c = MathF.Cos(turn);
                var s = MathF.Sin(turn);
                bearings.Add(new Vector2(back.X * c - back.Y * s, back.X * s + back.Y * c));
            }
            if (TryGetRally(v.Team, out var home) && Vector2.DistanceSquared(home, v.Position) > 16f)
                bearings.Add(Vector2.Normalize(home - v.Position));
            Vector2? best = null;
            var bestScore = 1f;
            var here = Vector2.Distance(v.Position, threat);
            foreach (var dir in bearings)
                for (var d = distance; d >= 4f; d -= 3f)
                {
                    var p = ClampToMap(v.Position + dir * d);
                    if (!Map.Contains(p) || !Grid.IsWalkable(p)) continue;
                    var moved = Vector2.Distance(p, v.Position);
                    if (moved < 4f) break;
                    var edge = Map.HalfSize - MathF.Max(MathF.Abs(p.X), MathF.Abs(p.Y));
                    // (It stops where it lands: not in a gate or a gap, where it would close the way.)
                    var score = Vector2.Distance(p, threat) - here + moved * 0.2f - MathF.Max(0f, 10f - edge) -
                                (!v.Flying && Lanes.NoParkAt(p) ? 8f : 0f);
                    if (score > bestScore)
                    {
                        bestScore = score;
                        best = p;
                    }
                    break;
                }
            return best;
        }

        internal Vehicle? FindNearestEnemy(Vehicle from, float range, bool requireVisible, float minRange = 0f,
            TargetLayers layers = TargetLayers.All, bool mobileOnly = false)
        {
            Vehicle? best = null;
            var bestDistance = float.MaxValue;
            foreach (var other in _vehicleList)
            {
                if (!other.IsAlive || other.Team == from.Team || other.Invulnerable || (mobileOnly && other.Def.Static)) continue;
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
            var slots = Formation.Slots(point, _unitBuffer.Count, spacing, Grid, _unitBuffer[0].Flying ? null : Lanes);
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
            if (prop.Def.BlocksFire) Cover.Add(prop);
        }

        /// <summary>Seconds a stealthy aircraft stays in plain sight after it fires (its bay doors open).</summary>
        private const double StealthReveal = 2.5;

        private void RefreshVisibility()
        {
            foreach (var target in _vehicleList)
            {
                // A fixed defence, once seen, stays on the map (it cannot move away), as buildings
                // stay under the fog in most RTS: artillery can shell it from beyond its own sight.
                var known = target.Def.Static ? target.VisibleToMask : 0;
                var mask = 0;
                // A stealthy aircraft shows only close up, or for a moment after it fires.
                var sight = target.Def.Stealth && Time - target.LastFiredAt > StealthReveal ? VehicleDef.StealthSight : 1f;
                if (target.Dummy)
                {
                    target.SeenByMask = target.VisibleToMask = ~0;
                    continue;
                }
                foreach (var spotter in _vehicleList)
                {
                    if (!spotter.IsAlive || spotter.Team < 0 || spotter.Team > 30) continue;
                    var range = spotter.Def.VisionRange * sight;
                    if (spotter.Team == target.Team ||
                        (Vector2.DistanceSquared(spotter.Position, target.Position) <= range * range &&
                         !Strikes.Obscures(spotter.Position, target.Position)))
                        mask |= 1 << spotter.Team;
                }
                target.SeenByMask = mask;
                target.VisibleToMask = mask | known;
            }
        }

        /// <summary>
        /// A fixed defence (a camp bastion, a point's tower, an Assault sector's guns, a fortress's
        /// turrets) stands on the ground like a building: routes go round it. Every one is anchored
        /// as it spawns; the map builder keeps the ground of those a map places clear and checks the
        /// routes round them.
        /// </summary>
        internal void AnchorDefence(Vehicle v)
        {
            if (!v.Def.Static || v.BlocksRoutes) return;
            v.BlocksRoutes = true;
            Grid.AddBlocker(v.Position, StaticFootprint(v.Def), StaticFootprint(v.Def), ObstacleClearance);
        }

        /// <summary>The square a fixed defence blocks, whichever way it faces.</summary>
        private static float StaticFootprint(VehicleDef def) => MathF.Max(def.Length, def.Width) * 0.8f;

        private void RemoveDead()
        {
            for (var i = _vehicleList.Count - 1; i >= 0; i--)
            {
                var v = _vehicleList[i];
                if (v.IsAlive) continue;
                _vehicleList.RemoveAt(i);
                _vehicles.Remove(v.Id);
                // Its ruin can be driven round or over: the ground opens again.
                if (v.BlocksRoutes) Grid.RemoveBlocker(v.Position, StaticFootprint(v.Def), StaticFootprint(v.Def), ObstacleClearance);
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
