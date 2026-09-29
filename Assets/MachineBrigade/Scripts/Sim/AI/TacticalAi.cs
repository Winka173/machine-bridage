#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// Utility-style opponent (game plan section 9). Every decision it sorts its army into roles
    /// and gives each the most useful order:
    /// <list type="bullet">
    /// <item>badly damaged heavy vehicles pull back behind the line;</item>
    /// <item>artillery holds a standoff position, shells clusters, and backs away from anything
    /// inside its minimum range;</item>
    /// <item>fast vehicles swing around a flank while the main body advances;</item>
    /// <item>the main body moves in bounds and waits for stragglers at each rendezvous, so it
    /// arrives together instead of trickling into the guns one by one.</item>
    /// </list>
    /// It only knows about enemies its team can see and issues ordinary commands, so it plays by
    /// the same rules as the player (architecture rule 8).
    /// </summary>
    public sealed class TacticalAi
    {
        private const float DecisionInterval = 0.75f;
        private const float DamagedFraction = 0.3f;
        private const float BoundLength = 24f;
        private const float FlankOffset = 24f;
        private const float FastSpeed = 11f;
        private const float ClusterRadius = 7f;
        private const int ClusterSize = 3;
        private const float EdgeMargin = 6f;

        /// <summary>A pulled-back vehicle rejoins once repaired this far, or after this long.</summary>
        private const float RecoveredFraction = 0.6f;
        private const float FallBackSeconds = 30f;

        private readonly int _team;
        private readonly int _enemyTeam;
        private float _flankSide;
        private bool _hadFlankers;
        private readonly List<Vehicle> _line = new();
        private readonly List<Vehicle> _fast = new();
        private readonly List<Vehicle> _artillery = new();
        private readonly List<Vehicle> _enemies = new();

        /// <summary>Known enemy fixed defences that can hit the ground (their reach is a wall for artillery).</summary>
        private readonly List<Vehicle> _defences = new();

        /// <summary>Engineers and jammers: they follow the army and cover it.</summary>
        private readonly List<Vehicle> _support = new();

        /// <summary>Launchers out of ammunition on their way to be restocked.</summary>
        private readonly List<Vehicle> _rearming = new();
        /// <summary>Vehicles pulled back to recover, with when they left the line.</summary>
        private readonly Dictionary<EntityId, double> _fallingBack = new();

        private readonly List<EntityId> _released = new();
        private Vector2 _lastObjective;
        private readonly HashSet<EntityId> _flanked = new();
        private readonly List<EntityId> _ids = new();
        private readonly List<EntityId> _otherIds = new();
        private float _timer;

        /// <summary>
        /// Where to advance when no enemy is in sight (Conquest: the objective to take). Null
        /// falls back to the enemy rally point.
        /// </summary>
        public Func<SimWorld, Vector2?>? Objective { get; set; }

        /// <summary>
        /// A structure the army has to knock down (a mission's demolition target), or none. Shells
        /// only splash buildings, so without an order nothing hits a target with no enemy beside it.
        /// </summary>
        public Func<SimWorld, EntityId>? Demolish { get; set; }

        /// <summary>
        /// Enemy buildings worth shooting up when there is nothing military in reach (a siege's
        /// fortress buildings, each paying a bounty); null or empty for none.
        /// </summary>
        public Func<SimWorld, IReadOnlyList<EntityId>>? Plunder { get; set; }

        /// <summary>
        /// With an objective set, how far from it the army may chase enemies (a point it has to
        /// hold); null lets it go after anything in sight.
        /// </summary>
        public float? Leash { get; set; }

        /// <summary>
        /// The commander's own leash while it holds ground (the Defend stance), used when no
        /// mission leash is set. Like <see cref="Leash"/>, a holding army never falls back.
        /// </summary>
        public float? HoldLeash { get; set; }

        /// <summary>
        /// Which way the army faces while it holds a point (towards the threat); null faces
        /// along the advance. Artillery stands behind the line, the line in front of the point.
        /// </summary>
        public Func<SimWorld, Vector2?>? Facing { get; set; }

        private float? ActiveLeash => Leash ?? HoldLeash;

        /// <summary>Below this ratio of our strength to theirs around the front, the army stops attacking.</summary>
        private const float OutmatchedRatio = 0.6f;

        /// <summary>It attacks again once reinforcements bring the ratio back up to this.</summary>
        private const float RecoveredRatio = 0.95f;

        /// <summary>How long a fall-back lasts at least, so the army does not bob in and out of range.</summary>
        private const float FallBackHold = 12f;

        private bool _outmatched;

        /// <summary>After holding back this long without catching up, the army commits anyway: an enemy
        /// dug in on its objectives never comes out, and waiting forever loses on the clock.</summary>
        private const float Patience = 30f;

        /// <summary>
        /// How long a committed attack presses on before the odds are weighed again: long enough to
        /// cross open ground to a dug-in enemy and fight it out, not only to reach it and turn back.
        /// </summary>
        private const double CommitSeconds = 60.0;

        /// <summary>Enemies seen near the front: their strength then, when, and where.</summary>
        private readonly Dictionary<EntityId, (float power, double seen, Vector2 at)> _seen = new();

        private readonly List<EntityId> _forget = new();

        private double _committedUntil = double.NegativeInfinity;
        private double _outmatchedSince;
        private Vector2 _fallBackPoint;

        /// <summary>
        /// Where to fall back to when outmatched, given the front (an objective we hold); null
        /// falls back towards home.
        /// </summary>
        public Func<SimWorld, Vector2, Vector2?>? FallBackTo { get; set; }

        /// <summary>Our strength over theirs around the front at the last decision (1 with nobody in sight).</summary>
        public float StrengthRatio { get; private set; } = 1f;

        /// <summary>The army is outmatched and holding a position behind the front until reinforcements arrive.</summary>
        public bool HoldingBack => _outmatched;

        /// <summary>Visible enemy vehicles, refreshed every decision.</summary>
        public IReadOnlyList<Vehicle> KnownEnemies => _enemies;

        /// <summary>
        /// Tower sense (on by default; off only to measure what it changes): towers weigh in the
        /// odds of going into their reach, the line waits at the edge of their guns until it is
        /// strong enough and the artillery has shelled them, and flankers and crate runners keep
        /// out of their reach.
        /// </summary>
        public static bool TowerSense = true;

        /// <summary>
        /// Prompt 13 I.3 (Hard and Very Hard): fighters go after enemy aircraft seen flying out to rearm or
        /// circling their holding pattern (their stores spent), and with the enemy flying three aircraft or
        /// more, artillery and strike aircraft go for its landing pads and ammunition carriers.
        /// </summary>
        public bool HuntSupply { get; set; }

        /// <summary>Our strength at the edge of a defended area must be this many times the defences' there to go in.</summary>
        private const float AssaultOdds = 1.4f;

        /// <summary>Seconds the line gives its artillery on the towers before going in with the strength it has.</summary>
        private const double ShellingTime = 35.0;

        /// <summary>After waiting this long at the edge, it goes in anyway if it is at least a match for the towers.</summary>
        private const double EdgePatience = 70.0;

        private double _atEdgeSince = double.NaN;

        /// <summary>This AI commands the allied commander's units (and only those); the player's commands the rest.</summary>
        public bool Allies
        {
            get => _allies;
            set
            {
                // The ally thinks a quarter of an interval after the player's commander (see the constructor).
                if (value && !_allies) _timer += DecisionInterval * 0.25f;
                _allies = value;
            }
        }

        private bool _allies;

        public TacticalAi(int team, int enemyTeam, int seed = 7)
        {
            _team = team;
            _enemyTeam = enemyTeam;
            _flankSide = new Random(seed).Next(2) == 0 ? -1f : 1f;
            // The two sides' commanders think on different steps, so their heaviest steps (orders,
            // routes for a whole group) do not land on the same one.
            _timer = team == 1 ? DecisionInterval * 0.5f : 0f;
        }

        public void Tick(SimWorld world, float dt)
        {
            _timer -= dt;
            if (_timer > 0f) return;
            _timer = DecisionInterval;
            if (world.IsOver) return;

            Sort(world);
            var body = _line.Count > 0 ? _line : _fast.Count > 0 ? _fast : _artillery;
            if (body.Count == 0) return;

            var front = FrontOf(world, body);
            GatherReinforcements(world, front);
            if (_line.Count == 0 && _fast.Count == 0 && _artillery.Count == 0) return;
            body = _line.Count > 0 ? _line : _fast.Count > 0 ? _fast : _artillery;
            var contact = _enemies.Count > 0;
            Vector2 objective;
            // Aircraft do not steer the army: ground forces go for ground targets and objectives.
            var groundContact = NearestGround(front, out _) < float.MaxValue;
            var goal = Objective?.Invoke(world);
            var chase = groundContact;
            if (chase && goal.HasValue && ActiveLeash is { } leash) chase = Vector2.Distance(NearestCluster(front), goal.Value) < leash;
            if (chase && (goal == null || NearestGround(front, out _) < 45f)) objective = NearestCluster(front);
            else if (goal.HasValue) objective = goal.Value;
            else if (chase) objective = NearestCluster(front);
            else if (!world.TryGetRally(_enemyTeam, out objective)) return;
            else if (world.HomeZones)
            {
                // The camp itself is guarded by bastions that cannot be destroyed: press up to its edge, not into it.
                var inward = objective.LengthSquared() > 1f ? Vector2.Normalize(-objective) : Vector2.UnitX;
                objective += inward * (SimWorld.HomeRadius + 18f);
            }
            contact = groundContact;
            if (JudgeOdds(world, front, contact))
            {
                // Outmatched: break contact, gather behind the front and let them come to us. Idle
                // vehicles still fight anything that walks into range; artillery keeps shelling.
                PullBackDamaged(world, front, Direction(front, objective));
                FocusBoss(world);
                DirectArtillery(world, front, objective, Direction(front, objective), contact);
                FallBack(world);
                return;
            }
            // A new objective: every fast vehicle may be sent round a flank again.
            if (Vector2.Distance(objective, _lastObjective) > 20f) _flanked.Clear();
            _lastObjective = objective;
            var forward = Direction(front, objective);
            // Holding a point: face the threat, and stand the line a little in front of it.
            var holding = HoldLeash != null && Leash == null && goal.HasValue && !chase && Facing?.Invoke(world) is { } facing;
            if (holding)
            {
                forward = Facing!(world)!.Value;
                objective = Clamp(world, goal!.Value + forward * 5f);
            }

            PullBackDamaged(world, front, forward);
            GrabCrates(world);
            SendToRearm(world);
            DirectSupport(world, front, forward);
            BreachObstacles(world, front, objective);
            DirectBreachers(world, front, objective);
            if (HuntSupply) HuntRearming(world);
            FocusBoss(world);
            FocusDemolition(world);
            ShootBuildings(world);
            DirectArtillery(world, front, objective, forward, contact);
            DirectFlankers(world, objective, forward, contact);
            DirectMainBody(world, objective, contact);
        }

        /// <summary>
        /// Compares our strength near the front with the enemy's there and decides whether to
        /// fall back. Holding a point (a leash) never falls back: that is the point of holding.
        /// </summary>
        private bool JudgeOdds(SimWorld world, Vector2 front, bool contact)
        {
            var ours = 0f;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != _team || v.Scripted || v.IsEscort) continue;
                if (Vector2.Distance(v.Position, front) < 55f) ours += v.Def.Power * (v.Hp / v.MaxHp);
            }
            // Fixed defences do not count: they cannot chase, and the army picks the range to fight
            // them at (artillery outranges every turret). The odds are about the mobile fight.
            foreach (var e in _enemies)
                if (!e.Def.Static && Vector2.Distance(e.Position, front) < 60f) _seen[e.Id] = (e.Def.Power * (e.Hp / e.MaxHp), world.Time, e.Position);
            // Every enemy seen near the front is remembered: out of sight is not the same as gone.
            // One in view counts as it is now; one out of view fades (half in about 45 s); one
            // known destroyed is forgotten. The patience rule still commits in the end.
            var theirs = 0f;
            _forget.Clear();
            foreach (var (id, (power, seen, at)) in _seen)
            {
                var age = world.Time - seen;
                if (!world.TryGetVehicle(id, out var known) || !known.IsAlive || age > 120.0)
                {
                    _forget.Add(id);
                    continue;
                }
                // Only what was last seen around where the army is now.
                if (Vector2.Distance(at, front) < 70f) theirs += power * (float)Math.Pow(0.5, age / 45.0);
            }
            foreach (var id in _forget) _seen.Remove(id);
            StrengthRatio = theirs > 0.5f ? ours / theirs : 1f;

            if (ActiveLeash != null)
            {
                _outmatched = false;
                return false;
            }
            if (_outmatched)
            {
                var held = world.Time - _outmatchedSince > FallBackHold;
                if (held && (StrengthRatio >= RecoveredRatio || theirs <= 0.5f)) _outmatched = false;
                else if (world.Time - _outmatchedSince > Patience)
                {
                    _outmatched = false;
                    _committedUntil = world.Time + CommitSeconds;
                }
            }
            else if (contact && theirs > 3f && StrengthRatio < OutmatchedRatio && world.Time >= _committedUntil)
            {
                _outmatched = true;
                _outmatchedSince = world.Time;
                // Fall back to a point we hold, else towards home, far enough to break contact.
                var home = world.TryGetRally(_team, out var rally) ? rally : front;
                var back = Direction(front, home);
                var distance = MathF.Min(30f, Vector2.Distance(front, home));
                _fallBackPoint = Clamp(world, FallBackTo?.Invoke(world, front) ?? front + back * distance);
            }
            return _outmatched;
        }

        /// <summary>Supply crates on the ground and the vehicle sent to claim each.</summary>
        private readonly Dictionary<EntityId, EntityId> _crateRunners = new();

        private readonly List<EntityId> _staleCrates = new();

        /// <summary>How far a free vehicle will go out of its way for a supply crate.</summary>
        private const float CrateDetour = 50f;

        /// <summary>
        /// A supply crate that has landed is worth fighting over: the nearest free vehicle (a
        /// fast one first) drives onto it and sits there until it is claimed; the others carry on.
        /// </summary>
        private void GrabCrates(SimWorld world)
        {
            _staleCrates.Clear();
            foreach (var (crateId, _) in _crateRunners)
            {
                var alive = false;
                foreach (var c in world.CrateList)
                    if (c.Id == crateId && c.IsAlive) alive = true;
                if (!alive) _staleCrates.Add(crateId);
            }
            foreach (var id in _staleCrates) _crateRunners.Remove(id);

            foreach (var crate in world.CrateList)
            {
                if (!crate.IsAlive || world.Time < crate.LandsAt) continue;
                // A crate under enemy guns is bait: nobody goes for it alone.
                if (TowerSense && Exposed(crate.Position, 2f)) continue;
                if (!_crateRunners.TryGetValue(crate.Id, out var runnerId) || !world.TryGetVehicle(runnerId, out var runner) || !runner.IsAlive ||
                    runner.Team != _team)
                {
                    runner = Nearest(_fast, crate.Position) ?? Nearest(_line, crate.Position);
                    if (runner == null) continue;
                    _crateRunners[crate.Id] = runner.Id;
                }
                _fast.Remove(runner);
                _line.Remove(runner);
                if (Vector2.Distance(runner.Position, crate.Position) < 2.5f) continue;
                if (runner.Order.Kind == OrderKind.Move && Vector2.Distance(runner.Order.Point, crate.Position) < 2f) continue;
                _ids.Clear();
                _ids.Add(runner.Id);
                Issue(world, CommandType.Move, _ids, crate.Position);
            }
        }

        private Vehicle? Nearest(List<Vehicle> pool, Vector2 at)
        {
            Vehicle? best = null;
            var bestDistance = CrateDetour;
            foreach (var v in pool)
            {
                if (v.Flying || _crateRunners.ContainsValue(v.Id)) continue;
                var d = Vector2.Distance(v.Position, at);
                if (d >= bestDistance) continue;
                best = v;
                bestDistance = d;
            }
            return best;
        }

        private readonly HashSet<EntityId> _rearmIds = new();

        /// <summary>A supply vehicle closer than this is worth the drive for an empty launcher (it reloads three times as fast).</summary>
        private const float DepotReach = 40f;

        /// <summary>
        /// Empty launchers reload where they stand: the crew restocks only while the vehicle is
        /// still, so the AI stops them. Prompt 13 C.7: an ammunition carrier or home (the camp, with
        /// its depot) reloads three times as fast; the launcher drives there when the drive and the
        /// reload there take less time than the reload in place. A launcher with an enemy about to
        /// reach it moves out of reach first. Once the magazine is back they rejoin their role.
        /// </summary>
        private void SendToRearm(SimWorld world)
        {
            _rearmIds.Clear();
            foreach (var v in _rearming)
            {
                _rearmIds.Add(v.Id);
                Vector2? depot = null;
                var left = v.Weapons[0].ReloadLeft > 0f ? v.Weapons[0].ReloadLeft : Combat.CombatSystem.ReloadSeconds(v.Arm(0));
                var speed = MathF.Max(1f, v.Def.Speed * 0.8f);
                // Time in place, against the drive there and a reload three times as fast (2 s to settle).
                var best = left;
                void Offer(Vector2 at, float reach)
                {
                    var d = MathF.Max(0f, Vector2.Distance(at, v.Position) - reach);
                    if (d > DepotReach * 1.5f) return;
                    var time = d / speed + left / 3f + 2f;
                    if (time >= best) return;
                    best = time;
                    depot = at;
                }
                foreach (var e in world.VehicleList)
                    if (e.IsAlive && e.Team == _team && e.Def.RearmAura != null && e != v) Offer(e.Position, e.Def.RearmAura.Radius * 0.6f);
                if (world.TryGetRally(_team, out var camp)) Offer(camp, 12f);
                if (depot != null && Vector2.Distance(v.Position, depot.Value) > 8f && !world.InEnemyHome(depot.Value, _team))
                {
                    if (v.Order.Kind != OrderKind.Move || Vector2.Distance(v.Order.Point, depot.Value) > 6f)
                        Issue(world, CommandType.Move, v.Id, Clamp(world, depot.Value));
                    continue;
                }
                var closest = NearestGround(v.Position, out var threat);
                if (threat != null && threat.Def.Weapon.CanTarget(false) && closest < threat.Def.Weapon.Range + 4f &&
                    world.EscapeRoute(v, threat.Position, threat.Def.Weapon.Range + 10f - closest) is { } away)
                {
                    if (v.Order.Kind != OrderKind.Move || Vector2.Distance(v.Order.Point, away) > 6f) Issue(world, CommandType.Move, v.Id, away);
                    continue;
                }
                // A move already under way to get out of reach finishes first; otherwise stop and reload.
                if (v.Order.Kind == OrderKind.Move && v.HasPath && Vector2.Distance(v.Position, v.Order.Point) > 3f &&
                    threat != null && closest < threat.Def.Weapon.Range + 14f) continue;
                if (v.Order.Kind != OrderKind.Idle || v.HasPath) world.Submit(new Command(CommandType.Stop, _team, new[] { v.Id }));
            }
        }

        private readonly HashSet<EntityId> _refitting = new();

        /// <summary>Health share under which an aircraft goes back to the airfield, and the share it waits for.</summary>
        private const float RefitBelow = 0.35f, RefitUntil = 0.9f;

        /// <summary>
        /// An aircraft's trip to be mended: below 35 % health it goes to the landing pad (see
        /// UtilityDef.AirRepair; it mends 3 % a second there), else to the HQ (1 % a second), and is
        /// released at 90 %, or when neither stands. Prompt 13 C.4: never in the middle of an attack
        /// (its salvo, hold or pass finishes first). Stores are the simulation's own business now
        /// (SupplySystem: they come back over the field, no trip home needed).
        /// </summary>
        private bool Refit(SimWorld world, Vehicle v)
        {
            Vehicle? field = null;
            foreach (var m in world.VehicleList)
                if (m.IsAlive && m.Team == _team && m.Def.Utility is { AirRepair: > 0f }) { field = m; break; }
            if (field == null)
                foreach (var m in world.VehicleList)
                    if (m.IsAlive && m.Team == _team && m.Def.Fort is { Kind: FortKind.Hq }) { field = m; break; }
            if (field == null)
            {
                _refitting.Remove(v.Id);
                return false;
            }
            var hurt = v.Hp < v.MaxHp * RefitBelow;
            if (!_refitting.Contains(v.Id) && hurt && world.Supply.CanBreakOff(v)) _refitting.Add(v.Id);
            if (!_refitting.Contains(v.Id)) return false;
            if (v.Hp >= v.MaxHp * RefitUntil)
            {
                _refitting.Remove(v.Id);
                return false;
            }
            if (v.Order.Kind != OrderKind.Move || Vector2.Distance(v.Order.Point, field.Position) > 4f)
                Issue(world, CommandType.Move, v.Id, field.Position);
            return true;
        }

        /// <summary>
        /// Prompt 13 C.4: an aircraft with its stores low (under a fifth) goes to rearm early when the
        /// fight round it has a lull (no known enemy it can hit near it), so it is full for the next one.
        /// </summary>
        private void RearmInLulls(SimWorld world, Vehicle v)
        {
            if (!v.HasStores || v.Supply != SupplyState.Fighting || v.StoresShare >= Abilities.SupplySystem.LowShare || v.RearmRequested) return;
            if (v.Target.IsValid || world.Time - v.LastFiredAt < 4.0) return;
            var reach = v.Def.VisionRange + 15f;
            foreach (var e in _enemies)
                if (Vector2.Distance(e.Position, v.Position) < reach) return;
            _ids.Clear();
            _ids.Add(v.Id);
            world.Submit(new Command(CommandType.Rearm, _team, _ids));
        }

        /// <summary>
        /// Dragon's teeth in the way: when the line is near a known obstacle between it and the
        /// objective and no other enemy is round it, the line and the engineers knock it down (the
        /// engineers breach three times as fast).
        /// </summary>
        private void BreachObstacles(SimWorld world, Vector2 front, Vector2 objective)
        {
            if (_line.Count == 0) return;
            Vehicle? block = null;
            var best = BreachReach;
            var toGoal = objective - front;
            if (toGoal.LengthSquared() < 1f) return;
            var dir = Vector2.Normalize(toGoal);
            foreach (var e in _enemies)
            {
                if (!e.Def.Obstacle) continue;
                var off = e.Position - front;
                var along = Vector2.Dot(off, dir);
                if (along < -4f || (off - dir * along).Length() > 18f) continue;
                var d = off.Length();
                if (d >= best) continue;
                best = d;
                block = e;
            }
            if (block == null) return;
            foreach (var e in _enemies)
                if (!e.Def.Obstacle && !e.Def.Passive && Vector2.Distance(e.Position, block.Position) < 25f) return;
            _ids.Clear();
            foreach (var v in _line)
                if (v.Target != block.Id) _ids.Add(v.Id);
            foreach (var v in _support)
                if (v.Def.RepairAura != null && v.Target != block.Id) _ids.Add(v.Id);
            foreach (var id in _ids) Issue(world, CommandType.Attack, id, block.Position, block.Id);
        }

        /// <summary>How near the front an obstacle must be for the line to breach it.</summary>
        private const float BreachReach = 30f;

        /// <summary>How far ahead of the front a breacher looks for an enemy structure to open the way through.</summary>
        private const float BreacherReach = 70f;

        /// <summary>
        /// Breachers (the armoured bulldozer) open the way into an enemy base ahead of the line: the
        /// enemy obstacle or fixed defence nearest the line's way to the objective, an obstacle at once,
        /// a defence once the line is strong enough to follow it in. With nothing to break they push on
        /// with the line.
        /// </summary>
        private void DirectBreachers(SimWorld world, Vector2 front, Vector2 objective)
        {
            var toGoal = objective - front;
            var dir = toGoal.LengthSquared() > 1f ? Vector2.Normalize(toGoal) : Vector2.UnitX;
            for (var i = _line.Count - 1; i >= 0; i--)
            {
                var v = _line[i];
                if (!v.Def.Breacher) continue;
                Vehicle? pick = null;
                var best = float.MaxValue;
                foreach (var e in _enemies)
                {
                    if (!e.IsAlive || !e.Def.Static || e.Def.Untargetable || (e.Def.Fort == null && !e.Def.Obstacle)) continue;
                    var off = e.Position - front;
                    var along = Vector2.Dot(off, dir);
                    if (along < -10f || along > BreacherReach) continue;
                    var score = Vector2.Distance(e.Position, v.Position) + (off - dir * along).Length() * 1.5f - (e.Def.Obstacle ? 25f : 0f);
                    if (score >= best) continue;
                    best = score;
                    pick = e;
                }
                if (pick == null) continue;
                // A defence only once the line can follow it in; an obstacle at once.
                if (!pick.Def.Obstacle && !StrongEnough(world, pick.Position, front)) continue;
                _line.RemoveAt(i);
                if (v.Order.Kind == OrderKind.Attack && v.Order.Target == pick.Id) continue;
                Issue(world, CommandType.Attack, v.Id, pick.Position, pick.Id);
            }
        }

        /// <summary>
        /// Engineers, jammers, command vehicles and radars keep a little behind the middle of the army.
        /// Prompt 13 F.2: an ammunition carrier parks by the side's launchers and helicopters (a little
        /// behind them, towards home), where they rearm off it; with none, behind the army too.
        /// </summary>
        private void DirectSupport(SimWorld world, Vector2 front, Vector2 forward)
        {
            var spot = Clamp(world, front - forward * 9f);
            _ids.Clear();
            Vector2? resupply = null;
            foreach (var v in _support)
            {
                var at = spot;
                if (v.Def.RearmAura != null || v.Def.AirRearm != null)
                {
                    resupply ??= ResupplySpot(world, forward) ?? spot;
                    at = resupply.Value;
                    if (Vector2.Distance(v.Position, at) < 6f) continue;
                    if (v.Order.Kind == OrderKind.Move && Vector2.Distance(v.Order.Point, at) < 5f) continue;
                    Issue(world, CommandType.Move, v.Id, at);
                    continue;
                }
                if (Vector2.Distance(v.Position, spot) < 10f) continue;
                if (v.Order.Kind == OrderKind.Move && Vector2.Distance(v.Order.Point, spot) < 8f) continue;
                _ids.Add(v.Id);
            }
            if (_ids.Count > 0) Issue(world, CommandType.Move, _ids, spot);
        }

        /// <summary>The middle of the side's launchers and helicopters, 6 m back towards home (null: it has none).</summary>
        private Vector2? ResupplySpot(SimWorld world, Vector2 forward)
        {
            var sum = Vector2.Zero;
            var n = 0;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != _team || v.Def.Static || v.Ally != Allies) continue;
                var launcher = !v.Flying && v.Arm(0).Ammo > 0;
                var heli = v.Flying && !v.Def.FixedWing && v.HasStores;
                if (!launcher && !heli) continue;
                sum += v.Position;
                n++;
            }
            if (n == 0) return null;
            var at = world.Lanes.OffLane(Clamp(world, sum / n - forward * 6f), 8f);
            return Exposed(at, 2f) ? null : at;
        }

        /// <summary>Everyone in the line drives (not attack-moves) back to the fall-back point and waits there.</summary>
        private void FallBack(SimWorld world)
        {
            _ids.Clear();
            CollectFallBack(_line);
            CollectFallBack(_fast);
            if (_ids.Count > 0) Issue(world, CommandType.Move, _ids, _fallBackPoint);
        }

        private void CollectFallBack(List<Vehicle> vehicles)
        {
            foreach (var v in vehicles)
            {
                if (Vector2.Distance(v.Position, _fallBackPoint) < 12f) continue;
                if (v.Order.Kind == OrderKind.Move && Vector2.Distance(v.Order.Point, _fallBackPoint) < SameRendezvous) continue;
                _ids.Add(v.Id);
            }
        }

        private void Sort(SimWorld world)
        {
            _line.Clear();
            _fast.Clear();
            _artillery.Clear();
            _enemies.Clear();
            _defences.Clear();
            _support.Clear();
            _rearming.Clear();
            // Pulled-back vehicles rejoin once repaired (or rested a while); the dead are forgotten.
            _released.Clear();
            foreach (var (id, since) in _fallingBack)
                if (!world.TryGetVehicle(id, out var v) || !v.IsAlive || v.Hp / v.MaxHp >= RecoveredFraction || world.Time - since > FallBackSeconds)
                    _released.Add(id);
            foreach (var id in _released) _fallingBack.Remove(id);
            _flanked.RemoveWhere(id => !world.TryGetVehicle(id, out _));
            // Once a flanking group is spent, the next one swings round the other side.
            if (_hadFlankers && _flanked.Count == 0) _flankSide = -_flankSide;
            _hadFlankers = _flanked.Count > 0;

            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive) continue;
                if (v.Team == _enemyTeam || v.Team == Teams.Hostile)
                {
                    if (v.IsVisibleTo(_team) && !v.Invulnerable)
                    {
                        // A remembered defence is not contact (nobody chases a gun seen minutes ago),
                        // but its reach is a wall for artillery and the edge the line gathers at.
                        if (!v.Def.Static || v.IsSeenBy(_team)) _enemies.Add(v);
                        if (v.Def.Static && GroundReach(v) > 0f) _defences.Add(v);
                    }
                    continue;
                }
                // Vehicles the player is steering by hand are left alone, and each commander keeps to its own (the ally's or the player's).
                // Escorts keep to their boss (prompt 16 F).
                if (v.Team != _team || v.Scripted || v.IsEscort || v.Def.Static || v.Ally != Allies || _fallingBack.ContainsKey(v.Id) || v.UnderPlayerControl(world.Time)) continue;
                // Aircraft with an airfield at home fly back to it out of ammunition or badly hurt,
                // and stay until mended and rearmed (the airfield repairs and rearms them).
                if (v.Flying && Refit(world, v)) continue;
                if (v.Flying) RearmInLulls(world, v);
                // An empty launcher stands and reloads (or goes to a supply vehicle close by) until its magazine is back.
                if (!v.Flying && v.OutOfAmmo)
                {
                    _rearming.Add(v);
                    continue;
                }
                // Engineers, jammers, command vehicles (their aura, and a forward drop zone when they
                // stand) and counter-battery radars keep a little behind the middle of the army.
                if (v.Def.RepairAura != null || v.Def.RearmAura != null || v.Def.Jammer > 0f || v.Def.CommandAura != null || v.Def.CounterBattery != null) _support.Add(v);
                else if (v.Def.Weapon.MinRange > 0f) _artillery.Add(v);
                else if (v.Def.Speed >= FastSpeed) _fast.Add(v);
                else _line.Add(v);
            }
        }

        private void HuntRearming(SimWorld world)
        {
            var aircraft = 0;
            foreach (var e in _enemies)
            {
                if (!e.Flying) continue;
                aircraft++;
                if (!e.HasStores || e.Supply == SupplyState.Fighting) continue;
                // The nearest free fighter within reach goes after it.
                Vehicle? hunter = null;
                var best = 150f;
                foreach (var v in _fast)
                {
                    if (!v.Def.Interceptor || v.Order.Kind == OrderKind.Attack) continue;
                    var d = Vector2.Distance(v.Position, e.Position);
                    if (d >= best) continue;
                    best = d;
                    hunter = v;
                }
                if (hunter == null) continue;
                _fast.Remove(hunter);
                Issue(world, CommandType.Attack, hunter.Id, e.Position, e.Id);
            }
            if (aircraft < 3) return;
            Vehicle? supply = null;
            foreach (var e in _enemies)
                if (e.IsAlive && (e.Def.Utility is { AirRepair: > 0f } || e.Def.AirRearm != null)) { supply = e; break; }
            if (supply == null) return;
            foreach (var list in new[] { _artillery, _fast })
                for (var i = list.Count - 1; i >= 0; i--)
                {
                    var v = list[i];
                    var w = v.Def.Weapon;
                    var strike = v.Flying && v.Def.FixedWing && !v.Def.Interceptor;
                    if (!strike && w.MinRange <= 0f) continue;
                    if (!w.CanTarget(false)) continue;
                    var d = Vector2.Distance(v.Position, supply.Position);
                    if (d > w.Range + (strike ? 120f : 20f) || d < w.MinRange) continue;
                    list.RemoveAt(i);
                    if (v.Order.Kind == OrderKind.Attack && v.Order.Target == supply.Id) continue;
                    Issue(world, CommandType.Attack, v.Id, supply.Position, supply.Id);
                }
        }

        /// <summary>How far past its weapon's range a vehicle turns to engage a boss.</summary>
        private const float BossReach = 30f;

        /// <summary>
        /// A boss in sight is the priority: everything that can hurt it and is close enough gets
        /// an attack order on it (artillery included), so the army does not trade shots with
        /// escorts while the boss grinds through it.
        /// </summary>
        private void FocusBoss(SimWorld world)
        {
            Vehicle? boss = null;
            foreach (var e in _enemies)
                if (e.Def.Boss)
                {
                    boss = e;
                    break;
                }
            if (boss == null) return;
            FocusOn(world, boss, _line);
            FocusOn(world, boss, _fast);
            FocusOn(world, boss, _artillery);
        }

        private void FocusOn(SimWorld world, Vehicle boss, List<Vehicle> vehicles)
        {
            for (var i = vehicles.Count - 1; i >= 0; i--)
            {
                var v = vehicles[i];
                var weapon = v.Def.Weapon;
                if (!weapon.CanTarget(boss.Flying)) continue;
                // A flying boss is for anti-air and aircraft; the rest shoot it only when it comes near.
                if (boss.Flying && !v.Flying && !Combat.CombatSystem.IsAntiAir(weapon)) continue;
                var distance = Vector2.Distance(v.Position, boss.Position);
                if (distance > weapon.Range + BossReach || distance < weapon.MinRange) continue;
                vehicles.RemoveAt(i);
                if (v.Order.Kind == OrderKind.Attack && v.Order.Target == boss.Id) continue;
                Issue(world, CommandType.Attack, v.Id, boss.Position, boss.Id);
            }
        }

        /// <summary>
        /// Units near the demolition target with no enemy inside their own weapon range shoot at
        /// the structure; anything with a fight on its hands keeps fighting.
        /// </summary>
        private void FocusDemolition(SimWorld world)
        {
            if (!DemolishTarget(world, out var at, out var radius, out var id)) return;
            DemolishWith(world, at, radius, id, _line);
            DemolishWith(world, at, radius, id, _fast);
        }

        /// <summary>
        /// The structure to knock down, if it still stands: a building, or a fixed defence (a
        /// general's HQ in a duel).
        /// </summary>
        private bool DemolishTarget(SimWorld world, out Vector2 position, out float radius, out EntityId id)
        {
            position = default;
            radius = 0f;
            id = Demolish?.Invoke(world) ?? EntityId.None;
            if (world.TryGetProp(id, out var prop) && prop.IsAlive)
            {
                position = prop.Position;
                radius = prop.Radius;
                return true;
            }
            if (world.TryGetVehicle(id, out var fixedDefence) && fixedDefence.IsAlive && fixedDefence.Def.Static && fixedDefence.Team != _team)
            {
                position = fixedDefence.Position;
                radius = fixedDefence.Radius;
                return true;
            }
            return false;
        }

        private void DemolishWith(SimWorld world, Vector2 at, float radius, EntityId id, List<Vehicle> vehicles)
        {
            for (var i = vehicles.Count - 1; i >= 0; i--)
            {
                var v = vehicles[i];
                var weapon = v.Def.Weapon;
                if (!weapon.CanTarget(false)) continue;
                var distance = Vector2.Distance(v.Position, at) - radius;
                if (distance > weapon.Range + BossReach || distance < weapon.MinRange) continue;
                if (NearestGround(v.Position, out _) < weapon.Range) continue;
                vehicles.RemoveAt(i);
                if (v.Order.Kind == OrderKind.Attack && v.Order.Target == id) continue;
                Issue(world, CommandType.Attack, v.Id, at, id);
            }
        }

        /// <summary>
        /// Vehicles standing idle with no enemy (vehicle or defence) in reach shoot up the enemy
        /// buildings next to them; the military targets always come first, and nobody leaves the
        /// advance for a building.
        /// </summary>
        private void ShootBuildings(SimWorld world)
        {
            if (Plunder?.Invoke(world) is not { Count: > 0 } buildings) return;
            PlunderWith(world, buildings, _line);
            PlunderWith(world, buildings, _fast);
        }

        private void PlunderWith(SimWorld world, IReadOnlyList<EntityId> buildings, List<Vehicle> vehicles)
        {
            for (var i = vehicles.Count - 1; i >= 0; i--)
            {
                var v = vehicles[i];
                if (!Ready(v) || Busy(world, v)) continue;
                var weapon = v.Def.Weapon;
                if (!weapon.CanTarget(false) || world.Catalog.Damage.Effective(weapon, Matchup.StructureLevel, TargetKind.Structure) < 0.25f) continue;
                if (NearestGround(v.Position, out _) < weapon.Range + 8f) continue;
                Prop? best = null;
                var bestDistance = weapon.Range + 2f;
                foreach (var id in buildings)
                {
                    if (!world.TryGetProp(id, out var building) || !building.IsAlive) continue;
                    var distance = Vector2.Distance(v.Position, building.Position) - building.Radius;
                    if (distance >= bestDistance) continue;
                    best = building;
                    bestDistance = distance;
                }
                if (best == null) continue;
                vehicles.RemoveAt(i);
                if (v.Order.Kind == OrderKind.Attack && v.Order.Target == best.Id) continue;
                Issue(world, CommandType.Attack, v.Id, best.Position, best.Id);
            }
        }

        /// <summary>Heavy vehicles close to death drop behind the line while others cover them.</summary>
        private void PullBackDamaged(SimWorld world, Vector2 front, Vector2 forward)
        {
            if (_line.Count + _fast.Count < 3) return;
            _ids.Clear();
            for (var i = _line.Count - 1; i >= 0; i--)
            {
                var v = _line[i];
                if (v.Armor != ArmorClass.Heavy || v.Hp / v.MaxHp > DamagedFraction || Nearest(v.Position, out _) > v.Def.VisionRange)
                    continue;
                _ids.Add(v.Id);
                _fallingBack[v.Id] = world.Time;
                _line.RemoveAt(i);
            }
            if (_ids.Count > 0) Issue(world, CommandType.Move, _ids, Clamp(world, front - forward * 16f));
        }

        private void DirectArtillery(SimWorld world, Vector2 front, Vector2 objective, Vector2 forward, bool contact)
        {
            foreach (var a in _artillery)
            {
                var weapon = a.Def.Weapon;
                // Only ground threats: a gun cannot outrun a helicopter, and running from one
                // hovering overhead only herded it into the map's edge (its machine gun and the
                // anti-air answer aircraft).
                var closest = NearestGround(a.Position, out var threat);
                if (threat != null && closest < weapon.MinRange + 6f)
                {
                    // Too close to shoot back: open the distance, by the best way out (never into the
                    // map's edge); cornered, it stays and its machine gun fights.
                    if (world.EscapeRoute(a, threat.Position, weapon.MinRange + 14f - closest) is { } escape)
                        Issue(world, CommandType.Move, a.Id, escape);
                    continue;
                }
                // Kiting: outranging the nearest threat by 6 m or more, never let it into its own
                // reach; back off to just beyond it, then fire again.
                var reach = threat != null && threat.Def.Weapon.CanTarget(a.Flying) ? threat.Def.Weapon.Range : 0f;
                if (reach > 0f && weapon.Range >= reach + 6f && closest < reach + 3f && a.Order.Kind != OrderKind.Move &&
                    world.EscapeRoute(a, threat!.Position, reach + 10f - closest) is { } kite)
                {
                    Issue(world, CommandType.Move, a.Id, kite);
                    continue;
                }
                if (a.Order.Kind == OrderKind.Move && !Standing(a)) continue;

                if (contact && TryFindCluster(a, out var cluster) && !Exposed(a.Position, 0f))
                {
                    if (a.Order.Kind != OrderKind.Attack) Issue(world, CommandType.Attack, a.Id, cluster.Position, cluster.Id);
                    continue;
                }
                // Fixed defences first (the military targets), then the structure the mission wants
                // down: each from a spot inside our range and outside every known gun's reach.
                if (ShellDefences(world, a)) continue;
                if (ShellStructure(world, a)) continue;
                if (a.Order.Kind != OrderKind.Idle || a.Target.IsValid) continue;

                // Stand off behind the main body, close enough to reach the enemy. With no main body
                // (an army of launchers and drone carriers) there is nothing to stand behind: close
                // to firing distance of the objective instead of backing away from their own centre.
                var alone = !_outmatched && _line.Count == 0 && _fast.Count == 0;
                var standoff = contact || alone ? objective - forward * (weapon.Range * 0.7f) : front - forward * 18f;
                if (!alone && Vector2.Distance(standoff, objective) < Vector2.Distance(front, objective)) standoff = front - forward * 10f;
                // Never into a known gun's reach: back along the line of advance until clear of it.
                for (var step = 0; step < 8 && Exposed(standoff, StandoffMargin); step++) standoff -= forward * 6f;
                // Guns deploy beside the roads and main routes, never in a gate: parked there they
                // are what the rest of the army jams behind.
                var stand = world.Lanes.OffLane(Clamp(world, standoff), 10f);
                // Alone they attack-move, so they stop and fire at the first enemy that comes into sight.
                if (Vector2.Distance(a.Position, stand) > 10f)
                    Issue(world, alone && !contact ? CommandType.AttackMove : CommandType.Move, a.Id, stand);
            }
        }

        /// <summary>Extra room an artillery piece keeps outside a fixed defence's reach.</summary>
        private const float StandoffMargin = 4f;

        /// <summary>How far past its own range an artillery piece looks for a defence to shell.</summary>
        private const float DefenceSearch = 45f;

        /// <summary>A defence's reach against the ground (its longest ground weapon), 0 when it cannot hit the ground.</summary>
        private static float GroundReach(Vehicle d)
        {
            var reach = 0f;
            foreach (var m in d.Def.Mounts)
                if (m.Weapon.CanTarget(false) && m.Weapon.Damage > 0f) reach = MathF.Max(reach, m.Weapon.Range);
            return reach;
        }

        /// <summary>A point inside some known fixed defence's reach (plus <paramref name="margin"/>).</summary>
        private bool Exposed(Vector2 p, float margin)
        {
            foreach (var d in _defences)
            {
                var reach = GroundReach(d) + margin + d.Radius;
                if (Vector2.DistanceSquared(p, d.Position) < reach * reach) return true;
            }
            return false;
        }

        /// <summary>Standing at its firing spot (a move order it has as good as finished).</summary>
        private static bool Standing(Vehicle v) => !v.HasPath || Vector2.Distance(v.Position, v.Order.Point) < 3f;

        /// <summary>Firing-spot scoring: on a road, per main route through the cell, per friend parked within 7 m, open ground (another gun's booked spot is out).</summary>
        private const float SpotRoadPenalty = 12f, SpotRoutePenalty = 20f, SpotCrowdPenalty = 8f, SpotOpenBonus = 6f;

        /// <summary>
        /// A spot to fire at <paramref name="target"/> from: inside our range (just short of it,
        /// beyond our minimum), outside every known gun's reach, on open ground. Rings at 0.95,
        /// 0.85 and 0.75 of our range, 24 bearings each, the nearest to where the gun already is
        /// (after the standoff solvers of RTS bots such as PurpleWave and Steamhammer), scored as
        /// in tactical position selection (generate, filter, score): never in a doorway or its
        /// mouth, off the roads and main routes the rest of the army drives along, spread out from
        /// other parked friends (fewer jams, less splash), and not on a spot another gun has
        /// booked. The chosen spot is booked (Company of Heroes reserves destinations the same way).
        /// </summary>
        private static readonly float[] SpotRings = { 0.95f, 0.85f, 0.75f, 0.65f, 0.55f };

        private Vector2? FiringSpot(SimWorld world, Vehicle shooter, Vector2 target, float targetRadius)
        {
            var weapon = shooter.Def.Weapon;
            var lanes = world.Lanes;
            var low = weapon.MinRange + 2f;
            Vector2? best = null;
            var bestScore = float.MaxValue;
            var start = SimMath.HeadingOf(shooter.Position - target);
            // Nearer rings (0.65, 0.55) only matter when the outer ones are all exposed or booked.
            foreach (var fraction in SpotRings)
            {
                var distance = MathF.Max(low, weapon.Range * fraction + targetRadius * 0.5f);
                if (distance > weapon.Range + targetRadius) continue;
                // The outer ring first: a nearer ring has to be clearly better to win.
                var ringPenalty = (0.95f - fraction) * weapon.Range * 0.5f;
                for (var k = 0; k < 24; k++)
                {
                    // Bearings fan out from the side the gun is on: 0, +15, -15, +30 degrees and so on.
                    var turn = ((k + 1) / 2) * (k % 2 == 0 ? 1f : -1f) * SimMath.DegToRad(15f);
                    var p = Clamp(world, target + SimMath.Forward(start + turn) * distance);
                    if (!world.Grid.IsWalkable(p) || Exposed(p, StandoffMargin)) continue;
                    var f = lanes.At(p);
                    if ((f & LaneFlags.NoPark) != 0) continue;
                    var score = Vector2.Distance(p, shooter.Position) + MathF.Abs(turn) * 4f + ringPenalty +
                                ((f & LaneFlags.Road) != 0 ? SpotRoadPenalty : 0f) +
                                ((f & LaneFlags.Route) != 0 ? SpotRoutePenalty * lanes.RouteCountAt(p) : 0f) -
                                (lanes.ClearanceAt(p) >= 4 ? SpotOpenBonus : 0f);
                    if (score >= bestScore) continue;
                    // Another gun's booked spot is never taken, even as the only safe one left (a
                    // short-ranged siege gun round a fortress has few): the gun waits instead.
                    if (lanes.ReservedByOther(p, shooter.Id, world)) continue;
                    score += SpotCrowdPenalty * FriendsParkedNear(world, p, 7f, shooter);
                    if (score >= bestScore) continue;
                    bestScore = score;
                    best = p;
                }
            }
            if (best is { } spot) lanes.Reserve(spot, shooter);
            return best;
        }

        /// <summary>Friendly ground vehicles standing (no route) within <paramref name="radius"/> of <paramref name="p"/>, other than <paramref name="self"/>.</summary>
        private int FriendsParkedNear(SimWorld world, Vector2 p, float radius, Vehicle self)
        {
            var count = 0;
            foreach (var v in world.VehicleList)
            {
                if (v == self || !v.IsAlive || v.Team != _team || v.Flying || v.Def.Static || v.HasPath) continue;
                if (Vector2.DistanceSquared(v.Position, p) < radius * radius) count++;
            }
            return count;
        }

        /// <summary>
        /// Shells the nearest known fixed defence it can reach from a safe spot: drives there (a
        /// plain move, never an attack-move that would chase into the guns), then fires from it.
        /// </summary>
        private bool ShellDefences(SimWorld world, Vehicle a)
        {
            var weapon = a.Def.Weapon;
            if (!weapon.CanTarget(false) || world.Catalog.Damage.Effective(weapon, Matchup.StructureLevel, TargetKind.Structure) <= 0.2f) return false;
            Vehicle? pick = null;
            var pickDistance = float.MaxValue;
            foreach (var d in _defences)
            {
                var distance = Vector2.Distance(d.Position, a.Position);
                if (distance > weapon.Range + DefenceSearch || distance >= pickDistance) continue;
                pick = d;
                pickDistance = distance;
            }
            return pick != null && ShellFromSafety(world, a, pick.Position, pick.Radius, pick.Id);
        }

        /// <summary>The mission's structure (a relay, a generator, the HQ) from a safe spot, once no defence needs shelling first.</summary>
        private bool ShellStructure(SimWorld world, Vehicle a)
        {
            if (!DemolishTarget(world, out var at, out var radius, out var id)) return false;
            var weapon = a.Def.Weapon;
            if (!weapon.CanTarget(false) || Vector2.Distance(a.Position, at) > weapon.Range + DefenceSearch * 2f) return false;
            return ShellFromSafety(world, a, at, radius, id);
        }

        private bool ShellFromSafety(SimWorld world, Vehicle a, Vector2 target, float radius, EntityId targetId)
        {
            var weapon = a.Def.Weapon;
            var distance = Vector2.Distance(a.Position, target) - radius;
            var inRange = distance <= weapon.Range - 0.5f && distance >= weapon.MinRange + 1f;
            // A wall fell and opened a breach where the gun stands: its spot is a doorway now, and it
            // moves off it to a new one rather than block the way in.
            if (a.Traffic.HasReservation && world.Lanes.NoParkAt(a.Traffic.ReservedAt))
            {
                world.Lanes.Release(a);
                inRange = false;
            }
            if (inRange && !Exposed(a.Position, 1f))
            {
                if (a.Order.Kind != OrderKind.Attack || a.Order.Target != targetId) Issue(world, CommandType.Attack, a.Id, target, targetId);
                return true;
            }
            if (FiringSpot(world, a, target, radius) is not { } spot) return false;
            if (a.Order.Kind != OrderKind.Move || Vector2.Distance(a.Order.Point, spot) > 4f) Issue(world, CommandType.Move, a.Id, spot);
            return true;
        }

        /// <summary>Fast vehicles drive round the side of the fight, then attack from there.</summary>
        private void DirectFlankers(SimWorld world, Vector2 objective, Vector2 forward, bool contact)
        {
            if (!contact || _fast.Count < 2 || _line.Count < 2)
            {
                _line.AddRange(_fast); // not enough for a flank: they fight with the main body
                return;
            }
            var side = new Vector2(-forward.Y, forward.X) * _flankSide;
            var flankPoint = Clamp(world, objective + side * FlankOffset - forward * 6f);
            // A flank that runs into a tower's guns is no flank: they fight with the main body.
            if (TowerSense && _defences.Count > 0 && Exposed(flankPoint, 2f))
            {
                _line.AddRange(_fast);
                return;
            }
            _ids.Clear();
            _otherIds.Clear();
            foreach (var f in _fast)
            {
                if (f.Order.Kind != OrderKind.Idle || Busy(world, f)) continue;
                if (!_flanked.Contains(f.Id) && Vector2.Distance(f.Position, flankPoint) < 9f) _flanked.Add(f.Id);
                if (_flanked.Contains(f.Id)) _otherIds.Add(f.Id);
                else _ids.Add(f.Id);
            }
            // Move (not attack-move) on the way round, so they do not stop for the first thing they see.
            if (_ids.Count > 0) Issue(world, CommandType.Move, _ids, flankPoint);
            if (_otherIds.Count > 0) Issue(world, CommandType.AttackMove, _otherIds, Clamp(world, objective));
        }

        /// <summary>
        /// Out of contact the body advances in bounds anchored on its lead vehicle: everyone gets
        /// the same next rendezvous, and the next bound starts only once most have arrived, so
        /// stragglers and fresh waves catch up instead of dragging the front back. In contact,
        /// everyone free joins the fight.
        /// </summary>
        private void DirectMainBody(SimWorld world, Vector2 objective, bool contact)
        {
            _ids.Clear();
            Vehicle? lead = null;
            var leadDistance = float.MaxValue;
            foreach (var v in _line)
            {
                var distance = Vector2.Distance(v.Position, objective);
                if (distance < leadDistance)
                {
                    lead = v;
                    leadDistance = distance;
                }
                if (Ready(v) && !Busy(world, v)) _ids.Add(v.Id);
            }
            if (_ids.Count == 0 || lead == null) return;

            if (contact)
            {
                // Those already standing on the objective stay put rather than being re-sent every decision.
                for (var i = _ids.Count - 1; i >= 0; i--)
                    if (world.TryGetVehicle(_ids[i], out var there) && Vector2.Distance(there.Position, objective) < 8f) _ids.RemoveAt(i);
                // An enemy fighting under its towers: go in only with the strength for both, else
                // hold at the edge of their guns and let the enemy (and the artillery) come.
                var into = Clamp(world, objective);
                if (TowerSense && _defences.Count > 0 && Exposed(into, 2f) && !StrongEnough(world, into, lead.Position))
                    into = EdgeBefore(world, into, lead.Position);
                if (_ids.Count > 0) Issue(world, CommandType.AttackMove, _ids, into);
                return;
            }
            if (_ids.Count < MathF.Ceiling(_line.Count * 0.75f)) return;
            var goal = Clamp(world, leadDistance > BoundLength * 1.5f ? lead.Position + Direction(lead.Position, objective) * BoundLength : objective);
            // Into the reach of known defences only together: the next bound stops at the edge of
            // their guns until most of the line has gathered there, then everyone goes in at once.
            if (_defences.Count > 0 && Exposed(goal, 2f))
            {
                var edge = goal;
                var back = Direction(goal, lead.Position);
                for (var step = 0; step < 14 && Exposed(edge, 2f); step++) edge += back * 4f;
                edge = Clamp(world, edge);
                var gathered = 0;
                foreach (var v in _line)
                    if (Vector2.Distance(v.Position, edge) < 16f) gathered++;
                var together = gathered >= MathF.Ceiling(_line.Count * 0.8f);
                if (TowerSense)
                {
                    // At the edge: go in once together and strong enough for the towers there (after
                    // the artillery has had its time on them), or, after waiting long, as a match for them.
                    if (together && double.IsNaN(_atEdgeSince)) _atEdgeSince = world.Time;
                    var waited = double.IsNaN(_atEdgeSince) ? 0.0 : world.Time - _atEdgeSince;
                    var shelled = _artillery.Count == 0 || waited >= ShellingTime;
                    var go = together && ((shelled && StrongEnough(world, objective, edge)) || (waited >= EdgePatience && StrongEnough(world, objective, edge, 1f)));
                    goal = go ? Clamp(world, objective) : edge;
                    if (go) _atEdgeSince = double.NaN;
                }
                else goal = together ? Clamp(world, objective) : edge;
            }
            else _atEdgeSince = double.NaN;
            // Those already on their way to this rendezvous keep their route, and those standing at
            // it stay put: sending them again would reshuffle the slots and keep everyone moving.
            for (var i = _ids.Count - 1; i >= 0; i--)
                if (world.TryGetVehicle(_ids[i], out var going) &&
                    ((going.Order.Kind == OrderKind.AttackMove && Vector2.Distance(going.Order.Point, goal) < SameRendezvous) ||
                     (going.Order.Kind == OrderKind.Idle && Vector2.Distance(going.Position, goal) < SameRendezvous))) _ids.RemoveAt(i);
            if (_ids.Count > 0) Issue(world, CommandType.AttackMove, _ids, goal);
        }

        /// <summary>
        /// Our line near <paramref name="from"/> (health counted) is at least <paramref name="odds"/>
        /// times the known defences covering <paramref name="target"/> and the enemies round it.
        /// </summary>
        private bool StrongEnough(SimWorld world, Vector2 target, Vector2 from, float odds = AssaultOdds)
        {
            var ours = 0f;
            var fast = 0f;
            var air = 0f;
            void Count(Vehicle v)
            {
                if (Vector2.Distance(v.Position, from) >= 35f) return;
                var p = v.Def.Power * (v.Hp / v.MaxHp);
                ours += p;
                if (v.Flying) air += p;
                else if (v.Def.Speed >= FastSpeed) fast += p;
            }
            foreach (var v in _line) Count(v);
            foreach (var v in _fast) Count(v);
            var theirs = 0f;
            foreach (var d in _defences)
            {
                var reach = GroundReach(d) + d.Radius + 8f;
                if (Vector2.DistanceSquared(d.Position, target) < reach * reach) theirs += d.Def.Power * (d.Hp / d.MaxHp) * Threat(d, ours, fast, air);
            }
            foreach (var e in _enemies)
                if (!e.Def.Static && !e.Flying && Vector2.Distance(e.Position, target) < 30f) theirs += e.Def.Power * (e.Hp / e.MaxHp);
            return theirs <= 0.5f || ours >= theirs * odds;
        }

        /// <summary>
        /// How much of our group a defence can really fight (0-1): its share of our ground force if it
        /// fires on the ground, of our aircraft if it fires at the air; a slow-turning cannon (a gun or
        /// heavy tower) counts half against fast vehicles, which run rings round it.
        /// </summary>
        private static float Threat(Vehicle d, float ours, float fast, float air)
        {
            if (ours <= 0f) return 1f;
            bool ground = false, sky = false;
            foreach (var m in d.Def.Mounts)
            {
                if (m.Weapon.Damage <= 0f) continue;
                ground |= m.Weapon.CanTarget(false);
                sky |= m.Weapon.CanTarget(true);
            }
            var slowCannon = d.Def.TurretTurnRate < 60f && d.Def.Weapon.Projectile == ProjectileKind.Shell && d.Def.Weapon.MinRange <= 0f;
            var groundShare = (ours - air) / ours;
            var share = 0f;
            if (ground) share += groundShare - (slowCannon ? 0.5f * fast / ours : 0f);
            if (sky) share += air / ours;
            return Math.Clamp(share, 0f, 1f);
        }

        /// <summary>The last point on the way from <paramref name="from"/> to <paramref name="target"/> outside every known defence's reach.</summary>
        private Vector2 EdgeBefore(SimWorld world, Vector2 target, Vector2 from)
        {
            var edge = target;
            var back = Direction(target, from);
            for (var step = 0; step < 16 && Exposed(edge, 2f); step++) edge += back * 4f;
            return Clamp(world, edge);
        }

        /// <summary>A vehicle this far from the army and this close to home is a reinforcement still to join.</summary>
        private const float ReinforcementGap = 50f;
        private const float HomeReach = 45f;

        /// <summary>Reinforcements go forward in groups of this many (or once the first has waited this long).</summary>
        private const int WaveSize = 3;
        private const double WaveWait = 25.0;

        /// <summary>Reinforcements waiting at the staging point, and since when.</summary>
        private readonly Dictionary<EntityId, double> _staged = new();
        private readonly List<Vehicle> _joining = new();
        private readonly List<EntityId> _gone = new();

        /// <summary>Where the army is: the middle of the vehicles out in the field (reinforcements still at home do not drag it back).</summary>
        private Vector2 FrontOf(SimWorld world, List<Vehicle> body)
        {
            if (!world.TryGetRally(_team, out var home)) return Centre(body);
            var sum = Vector2.Zero;
            var count = 0;
            foreach (var v in body)
            {
                if (Vector2.Distance(v.Position, home) < HomeReach) continue;
                sum += v.Position;
                count++;
            }
            return count >= 2 ? sum / count : Centre(body);
        }

        /// <summary>
        /// New vehicles do not drive out to the front one by one (each would meet the enemy alone):
        /// they gather at a staging point a little out from home and go forward together once
        /// three have gathered, or the first has waited long enough (after the reinforcement rule
        /// of StarCraft bots such as UAlbertaBot: join only as a group, else wait for the next wave).
        /// </summary>
        private void GatherReinforcements(SimWorld world, Vector2 front)
        {
            _joining.Clear();
            if (!world.TryGetRally(_team, out var home) || Vector2.Distance(front, home) < ReinforcementGap + HomeReach * 0.5f)
            {
                _staged.Clear();
                return;
            }
            var staging = Clamp(world, home + Direction(home, front) * 22f);
            CollectJoining(world, home, front, _line);
            CollectJoining(world, home, front, _fast);
            // The army out in the field has to be more than these few, or they are the army.
            if (_joining.Count == 0 || _line.Count + _fast.Count - _joining.Count < 2)
            {
                _staged.Clear();
                return;
            }
            _gone.Clear();
            foreach (var id in _staged.Keys)
                if (!_joining.Exists(v => v.Id == id)) _gone.Add(id);
            foreach (var id in _gone) _staged.Remove(id);

            var waiting = 0;
            var oldest = world.Time;
            foreach (var v in _joining)
            {
                if (Vector2.Distance(v.Position, staging) > 12f) continue;
                if (!_staged.TryGetValue(v.Id, out var since)) _staged[v.Id] = since = world.Time;
                waiting++;
                oldest = Math.Min(oldest, since);
            }
            // Enough of them (or long enough): they go forward together with the rest of the army.
            if (waiting >= WaveSize || (waiting > 0 && world.Time - oldest > WaveWait))
            {
                foreach (var v in _joining) _staged.Remove(v.Id);
                return;
            }
            _ids.Clear();
            foreach (var v in _joining)
            {
                _line.Remove(v);
                _fast.Remove(v);
                if (Vector2.Distance(v.Position, staging) < 10f) continue;
                if (v.Order.Kind == OrderKind.Move && Vector2.Distance(v.Order.Point, staging) < 8f) continue;
                _ids.Add(v.Id);
            }
            if (_ids.Count > 0) Issue(world, CommandType.Move, _ids, staging);
        }

        private void CollectJoining(SimWorld world, Vector2 home, Vector2 front, List<Vehicle> vehicles)
        {
            foreach (var v in vehicles)
                if (!v.Flying && Vector2.Distance(v.Position, home) < HomeReach && Vector2.Distance(v.Position, front) > ReinforcementGap &&
                    !Busy(world, v))
                    _joining.Add(v);
        }

        /// <summary>Two rendezvous closer than this are the same one (group moves spread their slots).</summary>
        private const float SameRendezvous = 12f;

        /// <summary>
        /// Free for the next bound: idle, or as good as arrived. Vehicles jostling for their slot
        /// never finish their move, and anti-aircraft vehicles deliberately hold short while tanks
        /// are near, so waiting for their orders to complete would stall the whole army.
        /// </summary>
        private static bool Ready(Vehicle v) =>
            v.Order.Kind == OrderKind.Idle ||
            (v.Order.Kind == OrderKind.AttackMove && Vector2.Distance(v.Position, v.Order.Point) < SameRendezvous);

        /// <summary>
        /// Fighting something on the ground. Shooting at an aircraft overhead does not count, or a
        /// hovering helicopter would freeze the whole advance.
        /// </summary>
        private static bool Busy(SimWorld world, Vehicle v)
        {
            if (world.TryGetVehicle(v.Engaged, out var engaged) && engaged.IsAlive && !engaged.Flying) return true;
            return v.Target.IsValid && !(world.TryGetVehicle(v.Target, out var target) && target.Flying);
        }

        /// <summary>Centre of the enemy group nearest to <paramref name="from"/>.</summary>
        private float NearestGround(Vector2 from, out Vehicle? nearest)
        {
            nearest = null;
            var best = float.MaxValue;
            foreach (var e in _enemies)
            {
                if (e.Flying) continue;
                var d = Vector2.Distance(from, e.Position);
                if (d >= best) continue;
                best = d;
                nearest = e;
            }
            return best;
        }

        private Vector2 NearestCluster(Vector2 from)
        {
            NearestGround(from, out var lead);
            if (lead == null) return from;
            var sum = Vector2.Zero;
            var count = 0;
            foreach (var e in _enemies)
            {
                if (e.Flying || Vector2.Distance(e.Position, lead.Position) > 12f) continue;
                sum += e.Position;
                count++;
            }
            return sum / Math.Max(1, count);
        }

        /// <summary>An enemy in range with at least <see cref="ClusterSize"/> vehicles around it.</summary>
        private bool TryFindCluster(Vehicle shooter, out Vehicle target)
        {
            var weapon = shooter.Def.Weapon;
            target = null!;
            var best = ClusterSize - 1;
            foreach (var e in _enemies)
            {
                if (!weapon.CanTarget(e.Flying)) continue;
                var distance = Vector2.Distance(shooter.Position, e.Position);
                if (distance < weapon.MinRange + 2f || distance > weapon.Range) continue;
                var around = 0;
                foreach (var other in _enemies)
                    if (other.Flying == e.Flying && Vector2.Distance(other.Position, e.Position) <= ClusterRadius) around++;
                if (around <= best) continue;
                best = around;
                target = e;
            }
            return target != null;
        }

        private float Nearest(Vector2 from, out Vehicle? nearest)
        {
            nearest = null;
            var best = float.MaxValue;
            foreach (var e in _enemies)
            {
                var d = Vector2.Distance(from, e.Position);
                if (d >= best) continue;
                best = d;
                nearest = e;
            }
            return best;
        }

        private void Issue(SimWorld world, CommandType type, EntityId unit, Vector2 point, EntityId target = default)
        {
            world.Submit(new Command(type, _team, new[] { unit }, point, target));
        }

        private void Issue(SimWorld world, CommandType type, List<EntityId> units, Vector2 point)
        {
            world.Submit(new Command(type, _team, units.ToArray(), point));
        }

        private static Vector2 Centre(List<Vehicle> vehicles)
        {
            var sum = Vector2.Zero;
            foreach (var v in vehicles) sum += v.Position;
            return sum / vehicles.Count;
        }

        private static Vector2 Direction(Vector2 from, Vector2 to)
        {
            var d = to - from;
            var length = d.Length();
            return length > 0.01f ? d / length : Vector2.UnitX;
        }

        private static Vector2 Clamp(SimWorld world, Vector2 p)
        {
            var limit = world.Map.HalfSize - EdgeMargin;
            return new Vector2(Math.Clamp(p.X, -limit, limit), Math.Clamp(p.Y, -limit, limit));
        }
    }
}
