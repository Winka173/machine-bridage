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
    public sealed partial class SimWorld
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
            Seed = seed;
            Random = new Random(seed);
            // The map's own rectangle (a long battlefield's is 300 x 480 m, prompt 17).
            Grid = new NavGrid(map.Min, map.Width, map.Length, 2f);
            Cover = new CoverGrid(map.Min, map.Width, map.Length);
            if (map.Boundary.Count >= 3)
            {
                // Beyond the outline is terrain: no driving there, and it stops direct fire.
                Grid.BlockWhere(map.InsideBoundary);
                Cover.BlockWhere(map.InsideBoundary);
            }
            // Prompt 33 L3: the static terrain tags (speeds, path costs, the forest's cover from sight).
            Grid.SetTerrain(map.TerrainZones);
            _pathFinder = new PathFinder(Grid);
            _lanes = new LaneMap(Grid);
            Damage = new DamageSystem(this);
            Status = new StatusSystem(this);
            Gear = new Abilities.GearSystem(this);
            Bosses = new MachineBrigade.Sim.Bosses.BossSystem(this);
            _movement = new MovementSystem(this);
            _combat = new CombatSystem(this);
            _abilities = new Abilities.AbilitySystem(this);
            Supply = new Abilities.SupplySystem(this);
            Economy = new EconomySystem(this);
            Strikes = new StrikeSystem(this);
            Bases = new Modes.BaseSystem(this);
            Domes = new Abilities.DomeSystem(this);
            Deploying = new Abilities.DeploySystem(this);
            // Prompt 25 F2 batch A: the new structures' and units' mechanisms.
            Works = new Abilities.FieldWorksSystem(this);

            foreach (var team in map.Teams) _rally[team.Team] = team.Rally;
            foreach (var placement in map.Props) SpawnProp(placement.DefId, placement.Position, placement.Rotation);
            Naval = new MachineBrigade.Sim.Bosses.NavalSystem(this);
            // Prompt 33 L5: the rails (their crossings are prebuilt ground states: built before the first step).
            _rails = new Movement.RailSystem(this);
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

        /// <summary>Rebuilds the lanes now (a wall came down and opened a breach: nobody may park in it).</summary>
        internal void RebuildLanesNow()
        {
            _lanes.Hurry();
            _lanes.RebuildIfDirty(this);
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

        /// <summary>
        /// Set by the game mode when the match ends; commands are refused afterwards. Prompt 30 L3: setting it resolves the
        /// match (<see cref="Ending"/>): from that tick the gameplay stands still.
        /// </summary>
        public bool IsOver
        {
            get => _over;
            set
            {
                if (value && !_over) Ending.Resolve(this);
                _over = value;
            }
        }

        private bool _over;

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

        /// <summary>Timed effects: burning, slowed, shredded, marked, barriers and aura buffs.</summary>
        internal StatusSystem Status { get; }

        /// <summary>Equipment traits and modules in battle.</summary>
        internal Abilities.GearSystem Gear { get; }

        /// <summary>Boss parts, boring, landings, the supergun's shot and boss guards (prompt 8).</summary>
        /// <summary>A side's elite budget (prompt 8 H): the modes set its share, cap and general.</summary>
        public Economy.EliteBudget Elites(int team) => Economy.EliteBudgetOf(team);

        /// <summary>
        /// Prompt 16 F: the battle's boss escorts (the modes set them by difficulty; Boss Rush's are
        /// smaller). Null: no escorts (the bare test battles).
        /// </summary>
        public Content.EscortSettings? EscortSettings { get; set; }

        /// <summary>
        /// Prompt 18: the battle's big attacks (the modes set them by difficulty). Null: no big attacks (the bare
        /// test battles).
        /// </summary>
        public Content.BigAttackSettings? BigAttackSettings { get; set; }

        /// <summary>How many escorts of this boss are alive now (the boss bar's count).</summary>
        public int EscortsAlive(EntityId boss) => Bosses.EscortsAlive(boss);

        internal MachineBrigade.Sim.Bosses.BossSystem Bosses { get; }

        /// <summary>Prompt 16: ships at sea, the coastal batteries and the lighthouse (made after the props: see the constructor).</summary>
        internal MachineBrigade.Sim.Bosses.NavalSystem Naval { get; }

        /// <summary>Prompt 16: the sea's rules for this battle (what the modes set, what they read).</summary>
        public MachineBrigade.Sim.Bosses.NavalRules SeaRules => Naval.Rules;

        internal CombatSystem Combat => _combat;

        /// <summary>Some round is flying at this vehicle.</summary>
        internal bool RoundIncoming(EntityId vehicle) => _combat.RoundIncoming(vehicle);
        internal EconomySystem Economy { get; }

        /// <summary>Each side's base: HQ, hardpoints, outposts (see <see cref="Modes.BaseSystem"/>).</summary>
        public Modes.BaseSystem Bases { get; }
        internal StrikeSystem Strikes { get; }
        internal Abilities.AbilitySystem Abilities => _abilities;

        /// <summary>Aircraft stores on the field and the holding pattern (prompt 13 C).</summary>
        internal Abilities.SupplySystem Supply { get; }

        /// <summary>Prompt 17 C: shield domes (the shield carrier, the shield generator).</summary>
        internal Abilities.DomeSystem Domes { get; }

        /// <summary>Prompt 25 F2 batch A (DECISIONS 25F2-A): walls, shelters, decoys, lights, balloons, jammers, drops and passes.</summary>
        internal Abilities.FieldWorksSystem Works { get; }

        /// <summary>
        /// Prompt 25 F2 batch A: night, fog or a sandstorm on this battlefield (the game sets it from its weather, before the
        /// battle and when the weather turns): searchlights and flare towers light the dark.
        /// </summary>
        public void SetDarkness(bool dark) => Works.SetDark(dark);

        /// <summary>Whether the battlefield is dark now (see <see cref="SetDarkness"/>).</summary>
        public bool Dark => Works.Dark;

        /// <summary>Prompt 17 C: vehicles that dig in (the bunker vehicle).</summary>
        internal Abilities.DeploySystem Deploying { get; }

        internal readonly List<Crate> CrateList = new();

        /// <summary>Supply crates falling or waiting on the field (battle events).</summary>
        public IReadOnlyList<Crate> Crates => CrateList;

        /// <summary>Mines on the field (see <see cref="Mine.IsVisibleTo"/> for who can see them).</summary>
        public IReadOnlyList<Mine> Mines => _abilities.Mines;

        /// <summary>A guided missile or drone is flying at this vehicle.</summary>
        internal bool MissileIncoming(EntityId vehicle) => _combat.MissileIncoming(vehicle);

        /// <summary>Play-test 13 (lane C): a guided round reaches this vehicle within the flare cue (the release moment).</summary>
        internal bool FlareCue(EntityId vehicle) => _combat.FlareCue(vehicle);

        /// <summary>A guided missile (not a drone) is flying at this ground vehicle.</summary>
        internal bool AtgmIncoming(EntityId vehicle) => _combat.AtgmIncoming(vehicle);

        /// <summary>Gives a side Command Points and a deck; modes without an economy never call this.</summary>
        /// <summary>
        /// Home zones (the capture modes): within <see cref="HomeRadius"/> of its own camp a
        /// vehicle repairs 2 % of its health a second once it has not been hit for 3 s, a newly
        /// arrived vehicle takes a fifth of the damage for its first 5 s, and the enemy cannot call
        /// strikes into the zone.
        /// </summary>
        public bool HomeZones { get; set; }

        public static float HomeRadius => global::MachineBrigade.Sim.Content.SimTunables.Modes.SimWorld.HomeRadius;

        /// <summary>
        /// Catch-up (the quick modes): the side losing the war of armies is reinforced faster and
        /// paid more for its kills (see <see cref="Economy.EconomySystem"/>).
        /// </summary>
        public bool CatchUp { get; set; }

        /// <summary>Prompt 30 L4: the catch-up's ceiling (+50 % by default; Conquest and Deathmatch +25 %, sheet "Luật trận").</summary>
        public float CatchUpMax { get; set; } = MachineBrigade.Sim.Economy.EconomySystem.MaxCatchUp;

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

        /// <summary>Previews: empties every weapon that runs out (its shots or its stores), to show a reload.</summary>
        public void DebugEmpty(Vehicle v)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
                if (v.Weapons[i].Ammo > 0) v.Weapons[i].Ammo = 0;
        }

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

        public static float EntrenchSeconds => global::MachineBrigade.Sim.Content.SimTunables.Modes.SimWorld.EntrenchSeconds;
        public const float EntrenchReduction = 0.2f;

        /// <summary>Hull-down: its side is dug in and it has not moved for a while.</summary>
        public bool IsEntrenched(Vehicle v) =>
            v.Team >= 0 && v.Team < _entrench.Length && _entrench[v.Team] && !v.Flying && !v.Def.Static &&
            Time - v.StillSince >= EntrenchSeconds;

        /// <summary>Whether a point lies in another side's home zone (strikes cannot be called there).</summary>
        /// <summary>Whether a point lies in the other side's camp, whatever the mode lets be shelled there (a tower is never dropped into it).</summary>
        internal bool InEnemyCamp(Vector2 point, int team)
        {
            foreach (var start in Map.Teams)
            {
                if (start.Team == team) continue;
                if (Vector2.Distance(start.Rally, point) < HomeRadius) return true;
                if (Bases.Of(start.Team) is { } b && Vector2.Distance(b.HqPosition, point) < HomeRadius) return true;
            }
            return false;
        }

        internal bool InEnemyHome(Vector2 point, int team)
        {
            if (!HomeZones) return false;
            foreach (var start in Map.Teams)
            {
                // A base that is the objective (Assault, a siege) or that can be lost may be shelled.
                if (start.Team == team || Bases.RoleOf(start.Team) is Content.BaseRole.Target or Content.BaseRole.Defend) continue;
                if (Vector2.Distance(start.Rally, point) < HomeRadius) return true;
                if (Bases.Of(start.Team) is { } b && Vector2.Distance(b.HqPosition, point) < HomeRadius) return true;
            }
            return false;
        }

        /// <summary>The mode being played ("Conquest", "Siege"...; null in tests), for data that differs by mode.</summary>
        public string? ModeTag { get; set; }

        /// <summary>
        /// Prompt 32 L6: the map's generic start units (<see cref="UnitPlacement.Start"/>) are left out: the mode gives its
        /// sides opening squads instead (set by the session; false in tests and missions).
        /// </summary>
        public bool SkipStartUnits { get; set; }

        /// <summary>The map's units a mode spawns at its start: all, or all but the generic start units (<see cref="SkipStartUnits"/>).</summary>
        public IEnumerable<UnitPlacement> MapUnits
        {
            get
            {
                foreach (var u in Map.Units)
                    if (!SkipStartUnits || !u.Start) yield return u;
            }
        }

        public void EnableEconomy(TeamEconomy economy)
        {
            // The catalog sets the pace of every economy (see balance.json "economy").
            economy.IncomeScale = Catalog.IncomeScale;
            economy.SupplyScale = Catalog.SupplyScale;
            // A mode that set no supply of its own takes the data's for it.
            if (economy.BaseArmyCap <= 0) economy.BaseArmyCap = Catalog.ArmyCapFor(ModeTag);
            // The enemy of the big modes may field more (the player keeps the ordinary ceiling).
            if (economy.Team == 1) economy.VehicleCap = Catalog.VehicleCapFor(ModeTag);
            // Prompt 29 E1: the mode's bank from the data, where the mode gave this side the bank the manifest moved.
            economy.BaseBank = Catalog.BankFor(ModeTag, economy.BaseBank);
            // Prompt 32 L6: the starting CP x the data's scale (1.16, the new prices) in the modes it lists, rounded half up;
            // the bank never below it.
            var start = Catalog.Opening.StartCp(ModeTag, economy.Cp);
            if (start != economy.Cp)
            {
                economy.Cp = start;
                economy.BaseBank = MathF.Max(economy.BaseBank, start);
            }
            Economy.Enable(economy);
            // Prompt 22 F: a commander set before the economy was enabled.
            ApplyCommander(economy);
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
            // A ship goes on the water where it is put (the naval system keeps it off the land).
            var afloat = def.Naval != null && Map.Sea != null;
            var at = def.Flying || afloat ? ClampToMap(position) : Grid.TryNearestWalkable(position, 8, out var walkable) ? walkable : position;
            // A landing in a pocket sealed off from the battlefield (between buildings, behind a wall
            // corner) would never get out: it comes down on the open ground nearest instead (prompt 12).
            if (!def.Flying && !def.Static && !afloat && Grid.RegionOf(at) is var region && region != Grid.MainRegion &&
                Grid.RegionSize(region) * 8 < Grid.RegionSize(Grid.MainRegion) && Grid.TryNearestInRegion(at, Grid.MainRegion, 12, out var open))
                at = open;
            if (!def.Flying && !def.Static && !afloat) at = FreeSpot(def, at);
            var vehicle = new Vehicle(NextId(), def, team, at, heading);
            // A side's own loadout towers carry their card's rank and equipment; other fixed defences
            // (a fortress, a point's watchtower) only when the side boosts everything.
            VehicleBoost? boost = null;
            if (team >= 0 && team < _boosts.Length && _boosts[team] is { } boosts &&
                // Prompt 26 A.4: a campaign boss keeps its data's health and damage (the target time sets them), never the arsenal's edge.
                (_boostAll[team] && !(BossesUnscaled && def.Boss) || (!def.Boss && (!def.Static || def.Fort is { Kind: Content.FortKind.Tower }))))
                boost = boosts(def);
            // Prompt 22 F: the side's commander on top, through the loadout's caps.
            boost = CommanderBoost(team, def, boost);
            if (boost is { } upgrade) Upgrade(vehicle, upgrade);
            // Prompt 26 A.6: the difficulty's own factors on the enemy's bosses (health, damage).
            if (team == 1 && def.Boss && BossDifficulty != null && Catalog.BigAttackRules.BossFactors(BossDifficulty) is var (bossHp, bossDamage))
            {
                vehicle.HpScale *= bossHp;
                vehicle.DamageBoost *= bossDamage;
            }
            // A mutator's change to a side's strength (the Operations mode's weekly twists).
            if (team >= 0 && team < _mutators.Length && _mutators[team] is { } mutate)
            {
                var (hp, damage) = mutate(def);
                vehicle.HpScale *= hp;
                vehicle.DamageBoost *= damage;
            }
            // Prompt 30 L5: the endless part's growth (stats only).
            if (team is 0 or 1 && _teamStats[team] is var (sh, sd) && (sh != 1f || sd != 1f))
            {
                vehicle.HpScale *= sh;
                vehicle.DamageBoost *= sd;
            }
            vehicle.Hp = vehicle.MaxHp;
            _vehicles.Add(vehicle.Id, vehicle);
            _vehicleList.Add(vehicle);
            // Its parts, a boss's timers, radio line and guards (prompt 8).
            Bosses.Joined(vehicle);
            Naval.Joined(vehicle);
            Rails.Joined(vehicle);
            Works.Joined(vehicle);
            // A fixed defence stands on its ground like a building from the start, wherever it came
            // from (a map's fortress as much as a mode's tower): routes go round it instead of into it.
            if (def.Static) AnchorDefence(vehicle);
            Emit(SimEvent.Spawned(vehicle));
            if (HomeZones && !vehicle.Def.Static) vehicle.GraceUntil = Time + 5.0;
            return vehicle;
        }

        /// <summary>Prompt 26 A.4: the enemy's bosses get no share of the player's arsenal edge (the campaign sets it).</summary>
        public bool BossesUnscaled { get; set; }

        /// <summary>Prompt 26 A.6: the difficulty key whose boss health and damage factors the enemy's bosses take (null: none).</summary>
        public string? BossDifficulty { get; set; }

        private readonly Func<VehicleDef, VehicleBoost>?[] _boosts = new Func<VehicleDef, VehicleBoost>?[3];
        private readonly Func<VehicleDef, (float hp, float damage)>?[] _mutators = new Func<VehicleDef, (float, float)>?[3];

        /// <summary>A side's vehicles enter with this health and damage (by def) on top of everything else; null: none.</summary>
        public void SetMutators(int team, Func<VehicleDef, (float hp, float damage)>? strength)
        {
            if (team >= 0 && team < _mutators.Length) _mutators[team] = strength;
        }
        /// <summary>
        /// Prompt 22 D.5: how far a side sees (1: as its units do; the story's choices can blind the enemy a little). Set before
        /// the battle starts; the same for every replay of it.
        /// </summary>
        public void SetVision(int team, float factor)
        {
            if (team >= 0 && team < _teamVision.Length) _teamVision[team] = factor;
        }

        private readonly float[] _teamVision = { 1f, 1f, 1f };
        private readonly Func<string, float>?[] _strikeBoosts = new Func<string, float>?[3];
        private readonly bool[] _boostAll = new bool[3];

        /// <summary>
        /// A side's upgrades (card ranks and equipment): what each of its vehicles gets as it enters
        /// the battle (null: none). Set before the forces are placed. Bosses and emplacements are
        /// left as they are unless <paramref name="everything"/> (a campaign enemy keeping pace
        /// with the player's arsenal: its boss and towers too).
        /// </summary>
        public void SetBoosts(int team, Func<VehicleDef, VehicleBoost>? boosts, Func<string, float>? strikeDamage = null, bool everything = false,
            Func<string, int>? strikeRank = null)
        {
            if (team < 0 || team >= _boosts.Length) return;
            _boosts[team] = boosts;
            _strikeBoosts[team] = strikeDamage;
            _strikeRanks[team] = strikeRank;
            _boostAll[team] = everything;
        }

        /// <summary>How much harder a side's fire support of this kind hits (its card's rank).</summary>
        internal float StrikeDamage(int team, string supportId) =>
            (team >= 0 && team < _strikeBoosts.Length && _strikeBoosts[team] is { } boost ? boost(supportId) : 1f) * Bases.SkillStrikeScale(team, supportId);

        /// <summary>The rank of a side's fire-support card (1 when the side has no ranks).</summary>
        internal int StrikeRank(int team, string supportId) =>
            team >= 0 && team < _strikeRanks.Length && _strikeRanks[team] is { } rank ? rank(supportId) : 1;

        private readonly Func<string, int>?[] _strikeRanks = new Func<string, int>?[3];

        private void Upgrade(Vehicle v, VehicleBoost b)
        {
            v.BoostHp = b.Hp;
            v.BoostSpeed = b.Speed;
            v.HpScale = b.Hp;
            v.SpeedScale = b.Speed;
            v.DamageBoost = b.Damage;
            v.FireBoost = b.FireRate;
            v.DamageTaken = b.DamageTaken;
            v.Regen = b.Regen;
            v.Special = b.Special;
            v.SpecialPower = b.SpecialPower;
            v.SpecialPower2 = b.SpecialPower2;
            switch (b.Special)
            {
                case SpecialModule.ReactiveArmor:
                    // Prompt 15 C.9: shaped charges only, hit by hit (GearSystem.Incoming).
                    break;
                case SpecialModule.AutoRepair:
                    v.Regen += b.SpecialPower;
                    break;
                case SpecialModule.VeteranCrew:
                    v.DamageBoost *= 1f + b.SpecialPower;
                    v.FireBoost *= 1f + b.SpecialPower;
                    break;
            }
            // Stat lines, tuned weapons, traits and the other modules.
            Gear.Equip(v, b);
            v.RefillMagazines();
        }

        /// <summary>
        /// Play-test 6: where a structure dropped by parachute (the field tower) lands: the nearest spot to the mark,
        /// in rings 2 m apart out to 16 m, whose whole footprint is open ground (walkable at its centre and all round its
        /// hull), clear of every vehicle and structure on the ground by both hulls, out of the gates and lane gaps, and
        /// never in the enemy's camp; the mark itself when none is near. It used to land on the mark whatever stood there
        /// and sat half inside a house or another tower.
        /// </summary>
        internal Vector2 ClearSpot(VehicleDef def, Vector2 at, int team)
        {
            var reach = def.HullBound + 0.5f;
            for (var ring = 0; ring <= 8; ring++)
            {
                var steps = ring == 0 ? 1 : ring * 8;
                for (var k = 0; k < steps; k++)
                {
                    var angle = k * SimMath.Tau / steps;
                    var p = at + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (ring * 2f);
                    if (!Map.Contains(p) || !FootprintOpen(p, reach) || Lanes.NoParkAt(p)) continue;
                    if (InEnemyCamp(p, team) || InEnemyHome(p, team)) continue;
                    var clear = true;
                    foreach (var other in _vehicleList)
                    {
                        if (!other.IsAlive || other.Flying) continue;
                        var gap = def.HullBound + other.Def.HullBound + 0.5f;
                        if (Vector2.DistanceSquared(other.Position, p) < gap * gap) { clear = false; break; }
                    }
                    if (clear) return p;
                }
            }
            return at;
        }

        /// <summary>Open ground at <paramref name="p"/> and at eight points round it <paramref name="reach"/> out.</summary>
        private bool FootprintOpen(Vector2 p, float reach)
        {
            if (!Grid.IsWalkable(p)) return false;
            for (var k = 0; k < 8; k++)
            {
                var angle = k * SimMath.Tau / 8f;
                var q = p + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * reach;
                if (!Map.Contains(q) || !Grid.IsWalkable(q)) return false;
            }
            return true;
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

        /// <summary>
        /// The player's own commands (from the screen, not the AI) with the step each was given at:
        /// replaying them into a fresh battle of the same seed brings it back to any moment (a
        /// multi-stage mission's checkpoints).
        /// </summary>
        public IReadOnlyList<(long tick, Command command)> Journal => _journal;

        private readonly List<(long tick, Command command)> _journal = new();

        /// <summary>A command from the player's screen: carried out and written in the journal.</summary>
        /// <summary>The side's part order (prompt 9): the boss and the index of the part its units in reach aim at, if one stands.</summary>
        public bool TryGetPartFocus(int team, out EntityId boss, out int part) => Bosses.TryGetFocus(team, out boss, out part);

        public CommandResult SubmitPlayer(Command command)
        {
            _journal.Add((Tick, command));
            return Submit(command);
        }

        /// <summary>
        /// A fingerprint of the battle now (every vehicle's id, side, place and health, every side's
        /// CP): two battles with the same fingerprint are in the same state as far as anyone can tell.
        /// </summary>
        public ulong StateHash()
        {
            unchecked
            {
                var h = 14695981039346656037UL;
                void Mix(long v)
                {
                    h ^= (ulong)v;
                    h *= 1099511628211UL;
                }
                Mix(Tick);
                foreach (var v in _vehicleList)
                {
                    if (!v.IsAlive) continue;
                    Mix(v.Id.Value);
                    Mix(v.Team);
                    Mix((long)MathF.Round(v.Position.X * 100f));
                    Mix((long)MathF.Round(v.Position.Y * 100f));
                    Mix((long)MathF.Round(v.Hp * 10f));
                    // Prompt 25 G: the round each gun of several rounds has in.
                    CombatSystem.MixRounds(v, Mix);
                    // A boss's parts (prompt 9): a checkpoint's replay must bring every part back the same.
                    for (var i = 0; i < v.PartCount; i++)
                        Mix((long)MathF.Round(v.PartFrac[i] * 1000f) * 4 + (v.PartBroken[i] ? 1 : 0) + (v.PartPatched[i] ? 2 : 0));
                }
                Bosses.Mix(Mix);
                // Prompt 32 L4: the HQ types' state (skill cooldowns, garrison stock, emergency domes).
                Bases.Mix(Mix);
                Naval.Mix(Mix);
                // Prompt 33 L5: the trains on their rails, the crossings' states, the support runs.
                Rails.Mix(Mix);
                // Prompt 23 A.3: the mission's events (their moments, the blackout, the weather's sight).
                MixEvents(Mix);
                // Prompt 31 L3: the prebuilt ground states in force.
                _navStates?.Mix(Mix);
                MixStorm(Mix);
                for (var team = 0; team <= 1; team++)
                    if (TryGetEconomy(team, out var e)) Mix((long)MathF.Round(e.Cp * 100f));
                return h;
            }
        }

        /// <summary>
        /// A vehicle changes sides (an ally betrays the player): it drops its orders and targets and
        /// fights for <paramref name="team"/> from now on.
        /// </summary>
        /// <summary>
        /// Where the player's side (team 0) may go: its moves stop at the edge (null: the whole map).
        /// A multi-stage mission opens more of the map as it goes (<see cref="Expand"/>).
        /// </summary>
        public PlayArea? PlayArea { get; private set; }

        /// <summary>Sets the play area (null: the whole map) and tells the view.</summary>
        public void Expand(PlayArea? area)
        {
            PlayArea = area;
            Emit(SimEvent.AreaChanged(area));
        }

        public void Defect(Vehicle v, int team)
        {
            if (!v.IsAlive || v.Team == team) return;
            Lanes.Release(v);
            v.ClearPath();
            v.SetOrder(Order.Idle);
            v.ManualOrder = false;
            for (var i = 0; i < v.Weapons.Length; i++) v.Weapons[i].Target = EntityId.None;
            v.Engaged = EntityId.None;
            v.Team = team;
            v.Ally = false;
            v.VisibleToMask = 0;
            Emit(SimEvent.Defected(v));
        }

        public CommandResult Submit(Command command)
        {
            if (IsOver) return CommandResult.Rejected(CommandError.MatchOver);
            if (command.Type == CommandType.Deploy) return Economy.Deploy(command.Team, command.DefId);
            if (command.Type == CommandType.Paradrop) return Economy.Paradrop(command.Team, command.DefId, command.Point);
            if (command.Type == CommandType.Strike) return Strikes.Call(command);
            if (command.Type == CommandType.CallTower) return Bases.CallTower(command);
            if (command.Type == CommandType.HqSkill) return Bases.UseSkill(command);
            if (command.Type == CommandType.Outpost) return Bases.SetUpOutpost(command);
            if (command.Type == CommandType.FocusPart) return Bosses.Focus(command);

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

                case CommandType.Rearm:
                    var sent = 0;
                    foreach (var v in _unitBuffer)
                    {
                        if (!v.HasStores || v.Supply != SupplyState.Fighting || v.StoresShare >= 0.999f) continue;
                        v.RearmRequested = true;
                        sent++;
                    }
                    return sent > 0 ? CommandResult.Ok : CommandResult.Rejected(CommandError.NoUnits);

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
            // Prompt 30 L3: once resolved, nothing of the battle moves (no paths, targets, damage, CP, capture, AI or
            // shots). The end sequence's clock is the view's (MatchEnd.Advance with unscaled time).
            if (Ending.Phase != MatchPhase.Running) return;
            Tick++;
            Time += dt;
            // Prompt 31 L3: prebuilt ground states switch only here, first thing in a step.
            _navStates?.Step(this);
            ServeQueuedPaths();
            if (Profile != null)
            {
                ProfiledStep(dt);
                return;
            }
            RefreshVisibility();
            Economy.Step(dt);
            Bases.Step();
            _movement.Step(dt);
            CrushVegetation();
            _abilities.Step(dt);
            Supply.Step(dt);
            Bosses.Step(dt);
            Naval.Step(dt);
            Rails.Step(dt);
            Status.Step(dt);
            Gear.Step(dt);
            Deploying.Step();
            Domes.Step();
            Works.Step(dt);
            _combat.Step(dt);
            Strikes.Step();
            Damage.Step();
            if (Map.Neutrals.Count > 0) Neutrals.Step(dt);
            RemoveDead();
        }

        /// <summary>The systems of a step, in order (the names of <see cref="Profile"/>'s columns).</summary>
        public static readonly string[] ProfileSections =
            { "visibility", "economy", "bases", "movement", "crush", "abilities", "status", "gear", "combat", "strikes", "damage", "remove" };

        /// <summary>
        /// When set (a measurement, never in play): each step adds one row of each system's time in
        /// milliseconds, in <see cref="ProfileSections"/> order.
        /// </summary>
        public List<double[]>? Profile { get; set; }

        private void ProfiledStep(float dt)
        {
            var row = new double[ProfileSections.Length];
            var ticks = System.Diagnostics.Stopwatch.GetTimestamp();
            void Lap(int i)
            {
                var now = System.Diagnostics.Stopwatch.GetTimestamp();
                row[i] = (now - ticks) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;
                ticks = now;
            }
            RefreshVisibility();
            Lap(0);
            Economy.Step(dt);
            Lap(1);
            Bases.Step();
            Lap(2);
            _movement.Step(dt);
            Lap(3);
            CrushVegetation();
            Lap(4);
            _abilities.Step(dt);
            Supply.Step(dt);
            Bosses.Step(dt);
            Naval.Step(dt);
            Rails.Step(dt);
            Lap(5);
            Status.Step(dt);
            Lap(6);
            Gear.Step(dt);
            Deploying.Step();
            Domes.Step();
            Works.Step(dt);
            Lap(7);
            _combat.Step(dt);
            Lap(8);
            Strikes.Step();
            Lap(9);
            Damage.Step();
            Lap(10);
            RemoveDead();
            Lap(11);
            Profile!.Add(row);
        }

        internal void Emit(in SimEvent e)
        {
            _events.Add(e);
            // Prompt 33 L5: a fortress line's train announced: its run on the siege rail.
            if (e.Kind == SimEventKind.Arrival) Rails.Announced(e);
        }

        /// <summary>Turns a vehicle into a firing-range target (see <see cref="Vehicle.Dummy"/>).</summary>
        public void MakeDummy(Vehicle v)
        {
            v.Dummy = true;
            v.RefreshEffects(Time);
        }

        /// <summary>Turns a vehicle into a firing-range sparring partner (see <see cref="Vehicle.Sparring"/>).</summary>
        public void MakeSparring(Vehicle v) => v.Sparring = true;

        /// <summary>A firing-range target or sparring partner that can be knocked out after all (see <see cref="Vehicle.Mortal"/>).</summary>
        public void MakeMortal(Vehicle v) => v.Mortal = true;

        /// <summary>Previews: tops every magazine and store back up (the In action clip's unit never runs dry).</summary>
        public void Refill(Vehicle v)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
            {
                var full = v.Weapons[i].Load > 0 ? v.Weapons[i].Load : v.Arms[i].Ammo > 0 ? v.Arms[i].Ammo : -1;
                if (v.Weapons[i].Ammo == full) continue;
                v.Weapons[i].Ammo = full;
                v.Weapons[i].ReloadLeft = 0f;
            }
            // A fixed minefield's mines are its rounds: once half are gone the field is laid again in a moment.
            if (v.MineLayer is { Spread: > 0f } field && v.NextMineAt > Time + 2.0)
            {
                var alive = 0;
                foreach (var m in _abilities.Mines)
                    if (m.IsAlive && m.Layer == v.Id) alive++;
                if (alive * 2 < field.Max) v.NextMineAt = Time + 2.0;
            }
        }

        /// <summary>
        /// Play-test 12, previews only: no weapon of <paramref name="v"/> waits more than <paramref name="most"/> s for its next
        /// round, nor its supergun or naval salvo and cells (a 60 s main battery shows in the "In action" clip). A battle never calls it.
        /// </summary>
        public void Hasten(Vehicle v, float most)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
                if (v.Weapons[i].Cooldown > most) v.Weapons[i].Cooldown = most;
            if (v.BombardNext > Time + most) v.BombardNext = Time + most;
        }

        /// <summary>Play-test 12, previews only (no sea there): a flagship's main turrets fire a salvo, each at an enemy of its own.</summary>
        public bool PreviewSalvo(Vehicle v) => Naval.PreviewSalvo(v);

        /// <summary>Play-test 12, previews only: a flagship's launch cells fire a cruise missile at the farthest enemy.</summary>
        public bool PreviewCruise(Vehicle v) => Naval.PreviewCruise(v);

        /// <summary>Previews: holds a vehicle's fire (or frees it), whatever its orders.</summary>
        public void HoldFire(Vehicle v, bool hold) => v.HoldFire = hold;

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
            // Full penetration from above, so armour (prompt 15: a fortress gate is level 4) cannot shrug it off.
            var hit = new HitInfo(null, -1, null, prop.Position, HitKind.Strike, false).WithPen(4f, true);
            for (var i = 0; i < 8 && prop.IsAlive; i++) Damage.Apply(prop, prop.Hp * 10f + 10000f, DamageType.HighExplosive, hit);
        }

        /// <summary>Lets game modes report what they decide (objectives changing hands).</summary>
        public void Announce(in SimEvent e) => _events.Add(e);

        /// <summary>
        /// Most ground routes found in one step. The rest wait for the next steps, first come first
        /// served, keeping the route they had: a commander ordering thirty vehicles at once (and
        /// their re-plans half a second later) made a step's worst case several times its mean.
        /// </summary>
        internal const int PathsPerStep = 6;

        private int _pathsThisStep;
        private readonly List<Vehicle> _pathQueue = new();

        /// <summary>Ground routes waiting for their step (for measurements).</summary>
        internal int QueuedPaths => _pathQueue.Count;

        /// <summary>
        /// Paths a vehicle towards <paramref name="goal"/>; on failure it simply stops. A ground
        /// route over this step's budget is found in a coming step (true: it is on its way).
        /// </summary>
        internal bool PathTo(Vehicle vehicle, Vector2 goal)
        {
            vehicle.RepathTimer = 0.5f;
            if (vehicle.Team == 0 && PlayArea is { } area) goal = area.Clamp(goal);
            // Prompt 33 L5: nobody parks on a rail.
            if (!vehicle.Flying) goal = Rails.OffRail(vehicle, goal);
            if (vehicle.Flying)
            {
                // Aircraft fly straight over buildings, wrecks and rivers.
                _pathBuffer.Clear();
                _pathBuffer.Add(ClampToMap(goal));
                vehicle.SetPath(_pathBuffer, goal);
                return true;
            }
            if (_pathsThisStep >= PathsPerStep)
            {
                if (!vehicle.PathQueued) _pathQueue.Add(vehicle);
                vehicle.PathQueued = true;
                vehicle.QueuedGoal = goal;
                return true;
            }
            return FindPath(vehicle, goal);
        }

        /// <summary>The routes waiting from earlier steps, in the order they were asked for, as far as this step's budget goes.</summary>
        private void ServeQueuedPaths()
        {
            _pathsThisStep = 0;
            var served = 0;
            while (served < _pathQueue.Count && _pathsThisStep < PathsPerStep)
            {
                var v = _pathQueue[served++];
                if (v.PathQueued && v.IsAlive) FindPath(v, v.QueuedGoal);
            }
            _pathQueue.RemoveRange(0, served);
        }

        private bool FindPath(Vehicle vehicle, Vector2 goal)
        {
            _pathsThisStep++;
            vehicle.PathQueued = false;
            // Prompt 33 L5: a new route keeps off a crossing that warns and off the line ahead of a train.
            if (_pathFinder.TryFindPath(vehicle.Position, goal, _pathBuffer, Rails.AvoidFor(vehicle)))
            {
                vehicle.SetPath(_pathBuffer, goal);
                return true;
            }
            vehicle.ClearPath();
            // (The stuck report tells a vehicle with no way to its goal from one held up on the way.)
            vehicle.Traffic.PathFailedAt = Time;
            vehicle.Traffic.PathFailedGoal = goal;
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
                    var edge = Map.EdgeDistance(p);
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
            var ground = !_unitBuffer[0].Flying;
            var slots = Formation.Slots(point, _unitBuffer.Count, spacing, Grid, ground ? Lanes : null, ground ? GroupRegion() : 0);
            Formation.Assign(_unitBuffer, slots, point, _slotBuffer);
            foreach (var v in _unitBuffer)
            {
                var goal = _slotBuffer.TryGetValue(v.Id, out var slot) ? slot : point;
                v.SetOrder(new Order(kind, goal, EntityId.None));
                PathTo(v, goal);
            }
        }

        /// <summary>The open ground most of the ordered ground vehicles stand on (their slots go there; prompt 12).</summary>
        private int GroupRegion()
        {
            int best = 0, bestCount = 0;
            foreach (var v in _unitBuffer)
            {
                if (v.Flying) continue;
                var region = Grid.RegionOf(v.Position);
                if (region == 0) continue;
                var count = 0;
                foreach (var o in _unitBuffer)
                    if (!o.Flying && Grid.RegionOf(o.Position) == region) count++;
                if (count <= bestCount) continue;
                best = region;
                bestCount = count;
            }
            return best;
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

        private readonly List<float> _sight = new();

        /// <summary>Bases with a working radar station this step: their side and HQ position.</summary>
        internal readonly List<(int team, Vector2 at)> _radarBases = new();
        private readonly List<float> _thermal = new();

        private void RefreshVisibility()
        {
            // Each spotter's reach with its equipment (optics; more standing still) and whether it
            // sees through smoke (a thermal imager).
            _sight.Clear();
            _thermal.Clear();
            foreach (var spotter in _vehicleList)
            {
                var reach = spotter.Def.VisionRange * spotter.VisionFactor * WeatherSight;
                // Prompt 31 L3: the sandstorm over one half of the map.
                if (StormActive) reach *= StormSight(spotter.Position);
                if (spotter.Team >= 0 && spotter.Team < _teamVision.Length) reach *= _teamVision[spotter.Team];
                var thermal = 0f;
                if (spotter.Gear is { } g)
                {
                    if (!spotter.IsMoving && Time - spotter.StillSince >= 1.0) reach *= 1f + g.Stat(StatId.StillVision);
                    // A thermal imager sees through smoke out to its share of the vision range.
                    if (g.Has(TraitId.ThermalImager)) thermal = reach * MathF.Min(1f, g.Trait(TraitId.ThermalImager).A);
                }
                // Prompt 25 F2 batch A: a scout's mast up (more sight standing still); a radar sees through smoke.
                reach = Works.SpotterReach(spotter, reach);
                if (spotter.Def.SmokeSight) thermal = reach;
                _sight.Add(reach);
                _thermal.Add(thermal);
            }
            foreach (var target in _vehicleList)
            {
                // A fixed defence, once seen, stays on the map (it cannot move away), as buildings
                // stay under the fog in most RTS: artillery can shell it from beyond its own sight.
                var known = target.Def.Static ? target.VisibleToMask : 0;
                var mask = 0;
                // A stealthy aircraft shows only close up, or for a moment after it fires.
                var sight = target.Def.Stealth && Time - target.LastFiredAt > StealthReveal ? VehicleDef.StealthSight : 1f;
                // A boss boring underground: only its own side knows where it is.
                if (target.Burrowed && !RevealAll)
                {
                    target.SeenByMask = target.VisibleToMask = target.Team is >= 0 and < 31 ? 1 << target.Team : 0;
                    continue;
                }
                if (target.Dummy || RevealAll)
                {
                    target.SeenByMask = target.VisibleToMask = ~0;
                    continue;
                }
                // Prompt 25 A1: a scout hiding where it stands (the scout jeep), until it fires.
                if (target.Def.StillCamouflage > 0f && !target.IsMoving && Time - target.StillSince >= 1.0 && Time - target.LastFiredAt > StealthReveal)
                    sight *= 1f - target.Def.StillCamouflage;
                // Prompt 33 L3: a ground vehicle in a forest is harder to make out (the same per-target factor, x 0.7).
                if (!target.Flying && target.Def.Naval == null && Grid.TerrainAt(target.Position) == TerrainTag.Forest) sight *= TerrainRules.ForestSight;
                // Equipment on the target: a camouflage net standing still, Ghillie Mode hidden.
                var hidden = false;
                if (target.Gear is { } tg)
                {
                    if (!target.IsMoving && Time - target.StillSince >= 1.0) sight *= 1f - Math.Clamp(tg.Stat(StatId.Camouflage), 0f, 0.5f);
                    hidden = tg.Hidden;
                }
                var naval = target.Def.Naval != null && Map.Sea != null;
                // Prompt 25 F2 batch A: a visual jammer of its side over it: only a scout, or an enemy this close, sees it.
                var screened = Works.ScreenedFrom(target);
                // Prompt 16: whoever holds the lighthouse watches the sea from its lamp.
                if (naval && Naval.Rules.LighthouseOwner is >= 0 and < 31 && target.Team != Naval.Rules.LighthouseOwner && !BlackedOut(Naval.Rules.LighthouseOwner) &&
                    Vector2.Distance(Map.Sea!.Lamp, target.Position) <= LighthouseSight * Naval.Rules.SeaSight + target.Radius)
                    mask |= 1 << Naval.Rules.LighthouseOwner;
                for (var i = 0; i < _vehicleList.Count; i++)
                {
                    var spotter = _vehicleList[i];
                    if (!spotter.IsAlive || spotter.Team < 0 || spotter.Team > 30) continue;
                    var range = _sight[i] * sight;
                    if (hidden) range = MathF.Min(range, GhillieReveal);
                    // A gun pit down in its hole: only a scout or a radar sees it from afar.
                    if (target.Lowered && spotter.Def.Class != UnitClass.Scout && spotter.Def.CounterBattery == null) range = MathF.Min(range, GhillieReveal);
                    // Prompt 22 F: Captain Kerr's side sees the stealthy, camouflaged and hidden farther off.
                    if ((sight < 1f || hidden || target.Lowered) && spotter.Team < _stealthSight.Length) range *= _stealthSight[spotter.Team];
                    // A guard tower sees stealth and hidden units within its guns' reach.
                    if (spotter.Def.RevealStealth && spotter.Team != target.Team) range = MathF.Max(range, spotter.Def.GunReach + target.Radius);
                    // The Patriot's long-range radar (DECISIONS 19T): the air picture over a wide circle, stealth aircraft too.
                    if (spotter.Def.RevealAir > 0f && target.Flying && spotter.Team != target.Team && !spotter.Stunned && !BlackedOut(spotter.Team))
                        range = MathF.Max(range, spotter.Def.RevealAir);
                    // Prompt 16: a ship's tall silhouette shows from further off (its hull's size), less in a sea storm.
                    if (naval) range = (range + target.Radius) * Naval.Rules.SeaSight;
                    if (screened < range && spotter.Def.Class != UnitClass.Scout) range = screened;
                    if (spotter.Team == target.Team) mask |= 1 << spotter.Team;
                    else
                    {
                        var d2 = Vector2.DistanceSquared(spotter.Position, target.Position);
                        var thermal = _thermal[i] * sight;
                        if (d2 <= range * range && ((thermal > 0f && d2 <= thermal * thermal) || !Strikes.Obscures(spotter.Position, target.Position)))
                            mask |= 1 << spotter.Team;
                    }
                }
                // Counter-battery radar: an enemy gun that fired is shown to the radar's side for a while.
                ref var reveal = ref target.Statuses[(int)StatusKind.Reveal];
                var radar = 0;
                if (reveal.Until > Time) radar |= reveal.Stacks;
                // A UAV scan: everything under it, stealth and hidden too.
                radar |= Strikes.ScanMask(target.Position, target.Team);
                // A base's radar: anything in the base shows.
                foreach (var (team, at) in _radarBases)
                    if (team != target.Team && Vector2.DistanceSquared(at, target.Position) < HomeRadius * HomeRadius) radar |= 1 << team;
                // Prompt 23 D.6: a side in an EW blackout gets nothing from its radars and scans, only its own eyes.
                for (var t = 0; t < _blackoutUntil.Length; t++)
                    if (Time < _blackoutUntil[t]) radar &= ~(1 << t);
                mask |= radar;
                // Prompt 25 F2 batch A: a searchlight's beam or a flare over it, in the dark (eyes, not radar: no blackout cuts it).
                mask |= Works.LitMask(target);
                target.SeenByMask = mask;
                target.VisibleToMask = mask | known;
            }
        }

        /// <summary>Prompt 16: how far out to sea the lighthouse's holder sees ships from its lamp.</summary>
        public static float LighthouseSight => global::MachineBrigade.Sim.Content.SimTunables.Modes.SimWorld.LighthouseSight;

        /// <summary>Ghillie Mode: a hidden vehicle shows only to enemies this close.</summary>
        public const float GhillieReveal = 8f;

        /// <summary>Measurements only (the equipment lab's duels): every vehicle is in everyone's sight, as a firing-range target is.</summary>
        internal bool RevealAll { get; set; }

        /// <summary>
        /// A fixed defence (a camp bastion, a point's tower, an Assault sector's guns, a fortress's
        /// turrets) stands on the ground like a building: routes go round it. Every one is anchored
        /// as it spawns; the map builder keeps the ground of those a map places clear and checks the
        /// routes round them.
        /// </summary>
        internal void AnchorDefence(Vehicle v)
        {
            if (!v.Def.Static || v.BlocksRoutes || v.Def.Passable) return;
            v.BlocksRoutes = true;
            Grid.AddBlocker(v.Position, StaticFootprint(v.Def), StaticFootprint(v.Def), ObstacleClearance);
            // A tower flown into a hardpoint where vehicles stand: they are put off its ground (they
            // could never have driven off it: prompt 12).
            _movement.ClearGround(v);
        }

        /// <summary>
        /// Prompt 19 E.5: a tiered boss down on the ground: its ground is closed to routes like a fixed defence's (the
        /// same square, opened again when it dies) and whatever stood there is put off it (prompt 12).
        /// </summary>
        internal void AnchorCrash(Vehicle v)
        {
            if (v.BlocksRoutes) return;
            v.BlocksRoutes = true;
            Grid.AddBlocker(v.Position, StaticFootprint(v.Def), StaticFootprint(v.Def), ObstacleClearance);
            _movement.ClearGround(v);
        }

        /// <summary>Prompt 19 E.5: cover dropped on the field (a crash's debris): a prop like the map's, spawned now.</summary>
        internal Prop? AddCover(string defId, Vector2 at)
        {
            if (!Catalog.TryGetProp(defId, out _) || !Map.Contains(at)) return null;
            SpawnProp(defId, at, 0);
            return _propList[_propList.Count - 1];
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

        internal Vector2 ClampToMap(Vector2 p) => Map.Clamp(p, 1f);
    }
}
