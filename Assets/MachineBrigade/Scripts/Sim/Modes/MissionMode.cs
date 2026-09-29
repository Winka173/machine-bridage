#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// A campaign mission: one goal (capture, hold, destroy, escort, survive, boss, intercept),
    /// the enemy's waves, a scripted convoy or boss, a clock, and the losing conditions (the
    /// army wiped out, the clock, the objective lost). The Game layer adds the commander AIs and
    /// points them at <see cref="PlayerGoal"/> and <see cref="EnemyGoal"/>.
    /// </summary>
    /// <summary>What a mission marker over the battlefield asks for.</summary>
    public enum MissionMarkKind
    {
        /// <summary>Destroy it (a demolition target, a hunted vehicle).</summary>
        Attack,

        /// <summary>Keep it standing.</summary>
        Defend,

        /// <summary>Go and look (a recon objective not yet scouted).</summary>
        Scout,
    }

    /// <summary>A marker the game draws over a mission's target: a building, a vehicle or a spot.</summary>
    public readonly struct MissionMark
    {
        public MissionMark(MissionMarkKind kind, EntityId entity, bool prop, Vector2 position, float progress)
        {
            Kind = kind;
            Entity = entity;
            Prop = prop;
            Position = position;
            Progress = progress;
        }

        public MissionMarkKind Kind { get; }

        /// <summary>The building or vehicle marked (none for a spot).</summary>
        public EntityId Entity { get; }

        public bool Prop { get; }
        public Vector2 Position { get; }

        /// <summary>A scouting spot: how far the look is (0 to 1).</summary>
        public float Progress { get; }
    }

    public sealed class MissionMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;
        private const float CaptureSeconds = 10f;
        private const float WaypointReach = 5f;

        /// <summary>Seconds a route boss may make no headway before it is sent on again.</summary>
        private const double BossStall = 12.0;

        private float _bossBest = float.MaxValue;
        private double _bossProgressAt;

        private readonly MissionDef _def;
        private readonly SideSetup _player;
        private readonly SideSetup? _enemy;
        private readonly List<ObjectiveState> _points = new();
        private readonly List<EntityId> _targets = new();
        private readonly List<(EntityId id, int waypoint)> _hunted = new();
        private readonly Dictionary<string, float> _scouting = new();

        /// <summary>Seconds a vehicle must stay on a recon objective to scout it.</summary>
        public const float ScoutSeconds = 3f;
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
        private int _reinforced;
        private float _peak;
        private double _nextReinforce = ReinforceFirst;
        private readonly List<string> _roster = new();

        /// <summary>No reinforcements before this far in, and at least this long between two.</summary>
        private const double ReinforceFirst = 45.0, ReinforceGap = 75.0;

        /// <summary>The enemy calls for help once its army is down to this share of the strongest it has been.</summary>
        private const float ReinforceBelow = 0.6f;

        /// <summary>Times the enemy has been reinforced.</summary>
        public int Reinforced => _reinforced;
        private double _launchStarted = -1;

        /// <summary>Outpost: seconds the set-up outpost has stood with its point held.</summary>
        private float _outpostHeld;

        /// <summary>The boss broke off and is getting away (a boss with <see cref="ScriptedUnitDef.FleeAt"/>).</summary>
        public bool BossFled { get; private set; }

        /// <summary>Seconds a fleeing boss takes to leave the battle.</summary>
        private const double FleeSeconds = 8.0;

        /// <summary>The allied commander's HQ (set by the operation; none without an ally). Relieve is lost when it falls.</summary>
        internal EntityId AllyHq { get; set; }

        /// <param name="player">The player's CP and deck (the Game layer passes the unlocked cards).</param>
        /// <param name="enemy">The enemy's economy when it has a commander; null when it only sends waves.</param>
        public MissionMode(MissionDef def, SideSetup player, SideSetup? enemy)
        {
            _def = def;
            _player = player;
            _enemy = enemy;
            _ledger.Ignore = v => v.Scripted || v.Def.Boss || v.Ally;
        }

        public MissionDef Def => _def;

        /// <summary>When this mission (or stage) began: its clocks count from here.</summary>
        public double StartedAt { get; private set; }

        /// <summary>A stage of a longer mission: finishing it does not end the battle (the operation goes on).</summary>
        internal bool Staged { get; set; }

        private double Now(SimWorld world) => world.Time - StartedAt;

        public IReadOnlyList<ObjectiveState> Points => _points;

        public MatchResult? Result { get; private set; }

        /// <summary>The player's losses so far (scripted trucks and the boss not counted).</summary>
        public int Losses => _ledger.Losses(PlayerTeam);

        public int Kills => _ledger.Kills(PlayerTeam);

        public int Wave => _wave;

        /// <summary>The boss vehicle once it is on the field (invalid before and after).</summary>
        public EntityId Boss => _boss;

        public float SecondsLeft(SimWorld world) => _def.TimeLimit > 0f ? MathF.Max(0f, _def.TimeLimit - (float)Now(world)) : -1f;

        /// <summary>Seconds until the boss launches, or -1 while it is still on its way.</summary>
        public float LaunchIn(SimWorld world) =>
            _launchStarted < 0 ? -1f : MathF.Max(0f, _def.LaunchSeconds - (float)(world.Time - _launchStarted));

        /// <summary>How far the goal is (0 to 1).</summary>
        public float Progress(SimWorld world) => _def.Goal switch
        {
            MissionGoal.Capture => _points.Count == 0 ? 0f : PointCapture.Held(_points, PlayerTeam) / (float)_points.Count,
            MissionGoal.Hold => MathF.Min(1f, _held / MathF.Max(1f, _def.HoldSeconds)),
            MissionGoal.Destroy => _targets.Count == 0 ? 1f : 1f - AliveTargets(world) / (float)_targets.Count,
            MissionGoal.Escort => MathF.Min(1f, _arrived / (float)Math.Max(1, _def.ConvoyNeeded)),
            MissionGoal.Survive or MissionGoal.Protect => MathF.Min(1f, (float)Now(world) / MathF.Max(1f, _def.SurviveSeconds)),
            MissionGoal.Hunt => _hunted.Count == 0 ? 1f : 1f - AliveHunted(world) / (float)_hunted.Count,
            MissionGoal.Recon => _points.Count == 0 ? 1f : PointCapture.Held(_points, PlayerTeam) / (float)_points.Count,
            MissionGoal.ShootDown => MathF.Min(1f, _ledger.AirKills(PlayerTeam) / (float)Math.Max(1, _def.KillsNeeded)),
            MissionGoal.Outpost => MathF.Min(1f, _outpostHeld / MathF.Max(1f, _def.HoldSeconds)),
            MissionGoal.Relieve => _hunted.Count == 0 ? 1f : 1f - AliveHunted(world) / (float)_hunted.Count,
            MissionGoal.Evacuate => MathF.Min(1f, _arrived / (float)Math.Max(1, _def.ConvoyNeeded)),
            MissionGoal.Duel => world.Bases.Of(EnemyTeam) is not { } camp ? 0f
                : camp.HqFallen || !world.TryGetVehicle(camp.Hq, out var hq) || !hq.IsAlive ? 1f : 1f - hq.Hp / hq.MaxHp,
            _ => BossFled ? 1f : world.TryGetVehicle(_boss, out var boss) ? 1f - boss.Hp / boss.MaxHp : _boss.IsValid ? 1f : 0f,
        };

        /// <summary>Goal counters for the objective panel: done out of needed (e.g. trucks, targets, seconds).</summary>
        public (int done, int needed) Count(SimWorld world) => _def.Goal switch
        {
            MissionGoal.Capture => (PointCapture.Held(_points, PlayerTeam), _points.Count),
            MissionGoal.Hold => ((int)_held, (int)_def.HoldSeconds),
            MissionGoal.Destroy => (_targets.Count - AliveTargets(world), _targets.Count),
            MissionGoal.Escort => (_arrived, _def.ConvoyNeeded),
            MissionGoal.Survive or MissionGoal.Protect => ((int)Now(world), (int)_def.SurviveSeconds),
            MissionGoal.Hunt => (_hunted.Count - AliveHunted(world), _hunted.Count),
            MissionGoal.Recon => (PointCapture.Held(_points, PlayerTeam), _points.Count),
            MissionGoal.ShootDown => (Math.Min(_ledger.AirKills(PlayerTeam), _def.KillsNeeded), _def.KillsNeeded),
            MissionGoal.Outpost => ((int)_outpostHeld, (int)_def.HoldSeconds),
            MissionGoal.Relieve => (_hunted.Count - AliveHunted(world), _hunted.Count),
            MissionGoal.Evacuate => (_arrived, _def.ConvoyNeeded),
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
            // Prompt 16 F: bosses bring their escorts (Normal's cap unless the session sets its difficulty's).
            world.EscortSettings ??= Content.EscortSettings.For(world.Catalog.EscortRules, "Normal");
            SetupStage(world, true, null);
        }

        /// <summary>The objectives' owners now (a stage hands them to the next).</summary>
        internal Dictionary<string, int> Owners()
        {
            var owners = new Dictionary<string, int>();
            foreach (var p in _points) owners[p.Def.Id] = p.Owner;
            return owners;
        }

        /// <summary>
        /// Sets the mission up; a later stage of an operation (<paramref name="first"/> false) keeps
        /// the battle as it is (economies, the army, the map's units) and adds only its own units
        /// and objectives, the points keeping the owners <paramref name="owners"/> hand on.
        /// </summary>
        internal void SetupStage(SimWorld world, bool first, IReadOnlyDictionary<string, int>? owners)
        {
            StartedAt = world.Time;
            _nextReinforce = StartedAt + ReinforceFirst;
            if (first)
            {
                world.EnableEconomy(_player.Build(PlayerTeam));
                if (_enemy != null) world.EnableEconomy(_enemy.Build(EnemyTeam));
                foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
                // A siege battlefield's fortress is the enemy's, its towers in their hardpoints (drawn for the mission's difficulty).
                if (_enemy != null && world.Map.Fortress is { } fortress && fortress.Slots.Count > 0 && world.Bases.Of(EnemyTeam) == null)
                    world.Bases.EstablishFortress(EnemyTeam, BaseLoadout.ForAi(world.Catalog, _def.Difficulty), BaseRole.Target, fortress.Hq, fortress.Slots);
            }
            foreach (var unit in _def.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);

            // Objectives: the listed ones (all of them when none are listed) for capture; the one
            // held for hold (or set up as an outpost). Other goals fight over none.
            if (_def.Goal is MissionGoal.Capture or MissionGoal.Hold or MissionGoal.Recon or MissionGoal.Outpost)
                foreach (var p in world.Map.Points)
                {
                    if (_def.Points.Count > 0 && !Contains(_def.Points, p.Id)) continue;
                    if ((_def.Goal is MissionGoal.Hold or MissionGoal.Outpost) && _points.Count > 0) break;
                    var state = new ObjectiveState(p);
                    if (Contains(_def.EnemyOwns, p.Id) && _def.Goal != MissionGoal.Recon) PointCapture.Own(state, EnemyTeam);
                    else if (_def.Goal == MissionGoal.Hold) PointCapture.Own(state, PlayerTeam);
                    else if (owners != null && owners.TryGetValue(p.Id, out var owner) && owner >= 0) PointCapture.Own(state, owner);
                    _points.Add(state);
                }
            if (_def.Goal is MissionGoal.Destroy or MissionGoal.Protect)
                foreach (var prop in world.Props)
                    if (prop.IsAlive && Contains(_def.Targets, prop.Def.Id) && (_def.Goal == MissionGoal.Destroy || OnPlayerSide(world, prop.Position)) &&
                        (_def.TargetNear is not { } near || Vector2.Distance(prop.Position, near) <= _def.TargetRadius))
                    {
                        _targets.Add(prop.Id);
                        if (_def.TargetHealth > 1f) prop.Harden(_def.TargetHealth);
                    }

            if (_def.Boss != null)
            {
                // A boss still being modelled stands in as another until its def exists.
                var (bossDef, health) = _def.Boss.Resolve(world.Catalog);
                var boss = world.SpawnVehicle(bossDef, EnemyTeam, _def.Boss.Position, _def.Boss.Heading);
                _boss = boss.Id;
                // A weakened boss, or one in a stronger form than its def.
                if (MathF.Abs(health - 1f) > 1e-3f && health > 0f)
                {
                    boss.HpScale *= health;
                    boss.Hp = boss.MaxHp;
                }
                if (_def.Boss.Route.Count > 0)
                {
                    boss.Scripted = true;
                    Drive(world, boss, _def.Boss.Route[0]);
                }
            }
            foreach (var h in _def.Hunt)
            {
                var hunted = world.SpawnVehicle(h.Def, EnemyTeam, h.Position, h.Heading);
                hunted.Marked = true;
                // The hunted are hardened like demolition targets: a hunt, not a drive-by.
                if (_def.TargetHealth > 1f)
                {
                    hunted.HpScale *= _def.TargetHealth;
                    hunted.Hp = hunted.MaxHp;
                }
                _hunted.Add((hunted.Id, 0));
                if (h.Route.Count == 0) continue;
                hunted.Scripted = true;
                Drive(world, hunted, h.Route[0]);
            }
            // A hunt with nothing of its own goes after what is already marked (the traitor's base
            // once the ally has turned).
            if ((_def.Goal is MissionGoal.Hunt or MissionGoal.Relieve) && _def.Hunt.Count == 0)
                foreach (var v in world.VehicleList)
                    if (v.IsAlive && v.Marked && v.Team == EnemyTeam) _hunted.Add((v.Id, 0));
            _waveTimer = _def.Waves?.First ?? float.MaxValue;
            _convoyTimer = 0f;
        }

        private static bool OnPlayerSide(SimWorld world, Vector2 at) =>
            !world.TryGetRally(PlayerTeam, out var home) || !world.TryGetRally(EnemyTeam, out var camp) ||
            Vector2.Distance(at, home) < Vector2.Distance(at, camp);

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            if (_def.Goal == MissionGoal.Recon) Scout(world, dt);
            else
                foreach (var point in _points) PointCapture.Tick(world, point, dt, CaptureSeconds);
            DriveHunted(world);
            if (world.TryGetEconomy(PlayerTeam, out var e0)) e0.Bonus = 0.25f * PointCapture.Held(_points, PlayerTeam);
            SpawnWaves(world, dt);
            if (world.Tick % 20 == 0) CallReinforcements(world);
            DriveConvoy(world, dt);
            DriveBoss(world);
            CheckFlee(world);
            if (_def.Goal == MissionGoal.Outpost) HoldOutpost(world, dt);

            var won = _def.Goal switch
            {
                MissionGoal.Capture => _points.Count > 0 && PointCapture.Held(_points, PlayerTeam) == _points.Count,
                MissionGoal.Hold => (_held += _points.Count > 0 && _points[0].Owner == PlayerTeam ? dt : 0f) >= _def.HoldSeconds,
                MissionGoal.Destroy => AliveTargets(world) == 0,
                MissionGoal.Escort => _arrived >= _def.ConvoyNeeded,
                MissionGoal.Survive or MissionGoal.Protect => Now(world) >= _def.SurviveSeconds,
                MissionGoal.Hunt => _hunted.Count > 0 && AliveHunted(world) == 0,
                MissionGoal.Recon => _points.Count > 0 && PointCapture.Held(_points, PlayerTeam) == _points.Count,
                MissionGoal.ShootDown => _ledger.AirKills(PlayerTeam) >= _def.KillsNeeded,
                MissionGoal.Outpost => _outpostHeld >= _def.HoldSeconds,
                MissionGoal.Relieve => _hunted.Count > 0 && AliveHunted(world) == 0,
                MissionGoal.Evacuate => _arrived >= _def.ConvoyNeeded,
                MissionGoal.Duel => world.Bases.Of(EnemyTeam) is { HqFallen: true },
                _ => BossFled || (_boss.IsValid && (!world.TryGetVehicle(_boss, out var b) || !b.IsAlive)),
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
            MissionGoal.Hunt => NearestHunted(world, PlayerCentre(world) ?? Vector2.Zero),
            MissionGoal.Recon => NextSpot(world, PlayerCentre(world) ?? Vector2.Zero),
            MissionGoal.Protect => Threatened(world),
            MissionGoal.Outpost => _points.Count > 0 ? _points[0].Def.Position : null,
            // Break the ring where it presses the ally hardest.
            MissionGoal.Relieve => NearestHunted(world, AllyHqPosition(world) ?? PlayerCentre(world) ?? Vector2.Zero),
            MissionGoal.Evacuate => EvacuationPoint(world),
            MissionGoal.Duel => world.Bases.Of(EnemyTeam) is { HqFallen: false } camp ? camp.HqPosition : null,
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
                case MissionGoal.Hunt:
                    // Guard the marked vehicles: the one the player is closest to.
                    return NearestHunted(world, PlayerCentre(world) ?? Vector2.Zero);
                case MissionGoal.Recon:
                    // Get to the next spot first and wait there.
                    return NextSpot(world, PlayerCentre(world) ?? Vector2.Zero);
                case MissionGoal.Protect:
                    return world.TryGetProp(EnemyDemolish(world), out var building) ? building.Position : PlayerCentre(world);
                case MissionGoal.Outpost:
                    return _points.Count > 0 ? _points[0].Def.Position : null;
                case MissionGoal.Relieve:
                    // The besiegers press on the allied HQ.
                    return AllyHqPosition(world) ?? PlayerCentre(world);
                case MissionGoal.Evacuate:
                    return EvacuationPoint(world);
                case MissionGoal.Duel:
                case MissionGoal.ShootDown:
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
            if (_def.TimeLimit > 0f && Now(world) >= _def.TimeLimit && _def.Goal is not (MissionGoal.Survive or MissionGoal.Protect)) return true;
            if (_def.Goal == MissionGoal.Protect && _targets.Count > 0 && AliveTargets(world) < Math.Min(_def.ProtectNeeded, _targets.Count)) return true;
            // The held objective is lost only when the enemy keeps it for a while: time to hit back.
            if (_def.Goal == MissionGoal.Hold && _points.Count > 0)
            {
                var enemyHolds = _points[0].Owner == EnemyTeam;
                _heldByEnemySince = enemyHolds ? (_heldByEnemySince < 0 ? world.Time : _heldByEnemySince) : -1;
                if (_heldByEnemySince >= 0 && world.Time - _heldByEnemySince > 25.0) return true;
            }
            if ((_def.Goal is MissionGoal.Escort or MissionGoal.Evacuate) && _convoySpawned >= _def.ConvoyCount &&
                _arrived + ConvoyAlive(world) < _def.ConvoyNeeded)
                return true;
            // The allied base whose siege is to be broken has fallen.
            if (_def.Goal == MissionGoal.Relieve && AllyHq.IsValid &&
                (!world.TryGetVehicle(AllyHq, out var allyHq) || !allyHq.IsAlive || allyHq.Team != PlayerTeam))
                return true;
            // A base to defend (its role Defend): losing its HQ loses the mission, whatever the goal.
            if (world.Bases.Of(PlayerTeam) is { Role: BaseRole.Defend, HqFallen: true }) return true;
            if (_def.Goal == MissionGoal.Intercept && world.TryGetVehicle(_boss, out var train) && train.IsAlive &&
                _def.Boss != null && _bossWaypoint >= _def.Boss.Route.Count)
            {
                // At the launch site: the missile goes up, and the clock runs out on the player.
                if (_def.LaunchSeconds <= 0f) return true;
                if (_launchStarted < 0) _launchStarted = world.Time;
                train.Charge = MathF.Min(1f, (float)(world.Time - _launchStarted) / _def.LaunchSeconds);
                if (train.Charge >= 1f) return true;
            }
            // The army wiped out for a while (nothing alive or on the way).
            var wiped = world.TryGetEconomy(PlayerTeam, out var economy) && economy.ArmyCp == 0 && Now(world) > 5.0;
            _wipedSince = wiped ? (_wipedSince < 0 ? world.Time : _wipedSince) : -1;
            return _wipedSince >= 0 && world.Time - _wipedSince > 12.0;
        }

        private void Finish(SimWorld world, int winner)
        {
            Result = new MatchResult(winner);
            if (!Staged) world.IsOver = true;
        }

        private void SpawnWaves(SimWorld world, float dt)
        {
            var waves = _def.Waves;
            if (waves == null || waves.Roster.Count == 0) return;
            _waveTimer -= dt;
            if (_waveTimer > 0f) return;
            _waveTimer = waves.Interval;
            if (world.CountAlive(EnemyTeam) >= (_def.EnemyCap > 0 ? Math.Min(waves.MaxAlive, _def.EnemyCap) : waves.MaxAlive)) return;
            _wave++;
            var count = Math.Min(waves.MaxSize, waves.Size + (int)MathF.Floor(waves.Grow * (_wave - 1)));
            Vector2 origin;
            if (waves.Spawns.Count > 0) origin = waves.Spawns[_wave % waves.Spawns.Count];
            else if (!world.TryGetRally(EnemyTeam, out origin)) return;
            for (var i = 0; i < count; i++)
            {
                var def = world.Economy.ForWave(EnemyTeam, waves.Roster[(_wave * 3 + i) % waves.Roster.Count]);
                var angle = i * SimMath.Tau / Math.Max(1, count);
                var at = world.ClampToMap(origin + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * 8f);
                world.SpawnVehicle(def, EnemyTeam, at, SimMath.DegToRad(225f));
            }
        }

        /// <summary>
        /// The enemy calls for help when it is losing: once its army has fallen well below the
        /// strongest it has been, or the player's goal passes another milestone, a group is flown in
        /// to its camp (a parachute drop, as a bought vehicle comes), bigger each time, answering
        /// the player's aircraft with anti-air when it has some.
        /// </summary>
        private void CallReinforcements(SimWorld world)
        {
            var strength = EnemyStrength(world);
            _peak = MathF.Max(_peak, strength);
            if (_reinforced >= _def.Reinforcements || world.Time < _nextReinforce) return;
            var losing = _peak > 0f && strength < _peak * ReinforceBelow;
            var pressed = Progress(world) >= 0.3f + 0.25f * _reinforced;
            if (!losing && !pressed) return;
            if (!world.TryGetRally(EnemyTeam, out var camp)) return;
            var roster = Roster(world);
            if (roster.Count == 0) return;
            var count = Math.Min(8, _def.ReinforceSize + _reinforced);
            var answerAir = PlayerAirShare(world) > 0.25f;
            for (var i = 0; i < count; i++)
            {
                var id = roster[(_reinforced * 5 + i * 3) % roster.Count];
                if (i == 0 && answerAir && FirstAntiAir(world, roster) is { } aa) id = aa;
                world.Economy.Airlift(EnemyTeam, world.Economy.ForWave(EnemyTeam, id), camp);
            }
            _reinforced++;
            _nextReinforce = world.Time + ReinforceGap;
            world.Emit(SimEvent.Alert(camp, "toast.enemyReinforce"));
        }

        /// <summary>What the enemy calls in: its deck, else its wave roster, else what it started with.</summary>
        private IReadOnlyList<string> Roster(SimWorld world)
        {
            if (_enemy != null && _enemy.Vehicles.Count > 0) return _enemy.Vehicles;
            if (_def.Waves != null && _def.Waves.Roster.Count > 0) return _def.Waves.Roster;
            if (_roster.Count == 0)
                foreach (var u in world.Map.Units)
                    if (u.Team == EnemyTeam && world.Catalog.Vehicles.TryGetValue(u.DefId, out var def) && !def.Static && !def.Boss && !_roster.Contains(u.DefId))
                        _roster.Add(u.DefId);
            return _roster;
        }

        private static float EnemyStrength(SimWorld world)
        {
            var total = 0f;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == EnemyTeam && !v.Def.Boss && !v.Def.Static && !v.Scripted) total += v.Def.ArmyCost;
            return total;
        }

        private static float PlayerAirShare(SimWorld world)
        {
            var air = 0f;
            var all = 0f;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != PlayerTeam || v.Scripted) continue;
                all += v.Def.ArmyCost;
                if (v.Flying) air += v.Def.ArmyCost;
            }
            return all > 0f ? air / all : 0f;
        }

        private static string? FirstAntiAir(SimWorld world, IReadOnlyList<string> roster)
        {
            foreach (var id in roster)
                if (world.Catalog.Vehicles.TryGetValue(id, out var def) && !def.Flying && def.Weapon.CanTarget(true)) return id;
            return null;
        }

        private void DriveConvoy(SimWorld world, float dt)
        {
            var convoy = _def.Convoy;
            if (convoy == null || _def.Goal is not (MissionGoal.Escort or MissionGoal.Evacuate)) return;
            _convoyTimer -= dt;
            if (_convoySpawned < _def.ConvoyCount && _convoyTimer <= 0f)
            {
                // One truck every few seconds, so they leave as a column instead of a pile.
                _convoyTimer = MathF.Max(1f, _def.ConvoyInterval);
                _convoySpawned++;
                var truck = world.SpawnVehicle(convoy.Def, PlayerTeam, convoy.Position, convoy.Heading);
                truck.Scripted = true;
                // A convoy vehicle can be tougher than its def (the Behemoth Mai plated up for the road).
                if (MathF.Abs(convoy.Health - 1f) > 1e-3f && convoy.Health > 0f)
                {
                    truck.HpScale *= convoy.Health;
                    truck.Hp = truck.MaxHp;
                }
                _convoy.Add((truck.Id, 0));
                if (convoy.Route.Count > 0) Drive(world, truck, convoy.Route[0]);
            }
            for (var i = 0; i < _convoy.Count; i++)
            {
                var (id, waypoint) = _convoy[i];
                if (waypoint >= convoy.Route.Count || !world.TryGetVehicle(id, out var truck) || !truck.IsAlive) continue;
                // Unescorted trucks stop and wait rather than drive alone into an ambush; evacuees
                // run for it whatever (the army holds the site behind them).
                var escorted = _def.Goal == MissionGoal.Evacuate || Escorted(world, truck);
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
            if (BossFled || route == null || route.Count == 0 || _bossWaypoint >= route.Count) return;
            if (!world.TryGetVehicle(_boss, out var boss) || !boss.IsAlive) return;
            var left = Vector2.Distance(boss.Position, route[_bossWaypoint]);
            if (left > WaypointReach)
            {
                // Pushed off its line (it steers round vehicles parked on it) and getting no nearer:
                // sent on again to the same waypoint, with a fresh route.
                if (left < _bossBest - 1f)
                {
                    _bossBest = left;
                    _bossProgressAt = world.Time;
                }
                else if (world.Time - _bossProgressAt > BossStall)
                {
                    _bossBest = left;
                    _bossProgressAt = world.Time;
                    Drive(world, boss, route[_bossWaypoint]);
                }
                return;
            }
            _bossBest = float.MaxValue;
            _bossProgressAt = world.Time;
            _bossWaypoint++;
            // A boss fight's route is a patrol, flown round and round (it does not park on the drop zone).
            if (_def.Goal == MissionGoal.Boss && _bossWaypoint >= route.Count) _bossWaypoint = 0;
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

        /// <summary>The demolition target the player's commander should shoot at (a duel: the general's HQ), or none.</summary>
        public EntityId PlayerDemolish(SimWorld world) => _def.Goal switch
        {
            MissionGoal.Destroy => NearestTargetId(world),
            MissionGoal.Duel => world.Bases.Of(EnemyTeam) is { HqFallen: false } camp ? camp.Hq : EntityId.None,
            _ => EntityId.None,
        };

        /// <summary>Protect: the building the enemy goes for (the one nearest its army), or none.</summary>
        public EntityId EnemyDemolish(SimWorld world) => _def.Goal == MissionGoal.Protect ? NearestTargetId(world, EnemyCentre(world)) : EntityId.None;

        /// <summary>A side's HQ made tougher or weaker (a duel's target), at full health.</summary>
        public static void HardenHq(SimWorld world, int team, float scale)
        {
            if (scale <= 0f || world.Bases.Of(team) is not { } camp || !world.TryGetVehicle(camp.Hq, out var hq)) return;
            hq.HpScale *= scale;
            hq.Hp = hq.MaxHp;
        }

        /// <summary>The markers the game draws: what to destroy, keep standing or scout.</summary>
        public void Marks(SimWorld world, List<MissionMark> into)
        {
            into.Clear();
            var kind = _def.Goal == MissionGoal.Protect ? MissionMarkKind.Defend : MissionMarkKind.Attack;
            foreach (var id in _targets)
                if (world.TryGetProp(id, out var p) && p.IsAlive) into.Add(new MissionMark(kind, id, true, p.Position, 0f));
            foreach (var (id, _) in _hunted)
                if (world.TryGetVehicle(id, out var v) && v.IsAlive) into.Add(new MissionMark(MissionMarkKind.Attack, id, false, v.Position, 0f));
            if (_def.Goal == MissionGoal.Duel && world.Bases.Of(EnemyTeam) is { HqFallen: false } camp && world.TryGetVehicle(camp.Hq, out var hq) && hq.IsAlive)
                into.Add(new MissionMark(MissionMarkKind.Attack, hq.Id, false, hq.Position, 0f));
            if (_def.Goal == MissionGoal.Recon)
                foreach (var point in _points)
                    if (point.Owner != PlayerTeam)
                        into.Add(new MissionMark(MissionMarkKind.Scout, EntityId.None, false, point.Def.Position,
                            _scouting.TryGetValue(point.Def.Id, out var t) ? t / ScoutSeconds : 0f));
        }

        /// <summary>
        /// Recon: a spot is scouted once one of the player's vehicles (an aircraft too) has been on
        /// it for a few seconds; it then stays the player's (the enemy cannot take the look back).
        /// </summary>
        private void Scout(SimWorld world, float dt)
        {
            foreach (var point in _points)
            {
                if (point.Owner == PlayerTeam) continue;
                var there = false;
                foreach (var v in world.VehicleList)
                    if (v.IsAlive && v.Team == PlayerTeam && !v.Scripted &&
                        Vector2.DistanceSquared(v.Position, point.Def.Position) < point.Def.Radius * point.Def.Radius)
                    {
                        there = true;
                        break;
                    }
                _scouting.TryGetValue(point.Def.Id, out var seconds);
                seconds = there ? seconds + dt : MathF.Max(0f, seconds - dt * 0.5f);
                _scouting[point.Def.Id] = seconds;
                point.Progress = MathF.Min(1f, seconds / ScoutSeconds);
                if (seconds < ScoutSeconds) continue;
                PointCapture.Own(point, PlayerTeam);
                point.Locked = true;
                world.Emit(SimEvent.Captured(point.Def.Id, point.Def.Position, PlayerTeam));
            }
        }

        private Vector2? NextSpot(SimWorld world, Vector2 from)
        {
            Vector2? best = null;
            var bestDistance = float.MaxValue;
            foreach (var point in _points)
            {
                if (point.Owner == PlayerTeam) continue;
                var d = Vector2.DistanceSquared(from, point.Def.Position);
                if (d >= bestDistance) continue;
                bestDistance = d;
                best = point.Def.Position;
            }
            return best;
        }

        /// <summary>The hunted vehicles drive their patrol routes round and round (until the player's army is on them).</summary>
        private void DriveHunted(SimWorld world)
        {
            for (var i = 0; i < _hunted.Count; i++)
            {
                if (i >= _def.Hunt.Count) break;
                var (id, waypoint) = _hunted[i];
                var route = _def.Hunt[i].Route;
                if (route.Count == 0 || !world.TryGetVehicle(id, out var v) || !v.IsAlive) continue;
                if (Vector2.Distance(v.Position, route[waypoint]) > WaypointReach) continue;
                waypoint = (waypoint + 1) % route.Count;
                _hunted[i] = (id, waypoint);
                Drive(world, v, route[waypoint]);
            }
        }

        private int AliveHunted(SimWorld world)
        {
            var alive = 0;
            foreach (var (id, _) in _hunted)
                if (world.TryGetVehicle(id, out var v) && v.IsAlive) alive++;
            return alive;
        }

        private Vector2? NearestHunted(SimWorld world, Vector2 from)
        {
            Vector2? best = null;
            var bestDistance = float.MaxValue;
            foreach (var (id, _) in _hunted)
            {
                if (!world.TryGetVehicle(id, out var v) || !v.IsAlive) continue;
                var d = Vector2.DistanceSquared(from, v.Position);
                if (d >= bestDistance) continue;
                bestDistance = d;
                best = v.Position;
            }
            return best;
        }

        /// <summary>
        /// A boss that breaks off at a share of its health (the first sight of a boss that is not yet
        /// finished): once hit that hard it cannot be touched, turns for the far corner of the map and
        /// leaves the battle a few seconds later. Driving it off wins the fight.
        /// </summary>
        private void CheckFlee(SimWorld world)
        {
            if (BossFled || _def.Boss is not { FleeAt: > 0f } boss || !world.TryGetVehicle(_boss, out var v) || !v.IsAlive) return;
            if (v.Hp > v.MaxHp * boss.FleeAt) return;
            BossFled = true;
            v.Invulnerable = true;
            v.Scripted = true;
            v.ExpiresAt = world.Time + FleeSeconds;
            var away = world.TryGetRally(EnemyTeam, out var camp) ? camp : v.Position;
            var outward = away.LengthSquared() > 1f ? Vector2.Normalize(away) : Vector2.UnitY;
            world.Submit(new Command(CommandType.Move, v.Team, new[] { v.Id }, world.ClampToMap(away + outward * world.Map.HalfSize)));
            world.Emit(SimEvent.RadioMessage("radio.bossFled", PlayerTeam));
        }

        /// <summary>Outpost: the clock runs while the point is the player's and its outpost stands.</summary>
        private void HoldOutpost(SimWorld world, float dt)
        {
            if (_points.Count == 0) return;
            var site = _points[0];
            if (site.Owner != PlayerTeam) return;
            if (world.Bases.Of(PlayerTeam) is { } ours && ours.Outposts.ContainsKey(site.Def.Id)) _outpostHeld += dt;
        }

        /// <summary>The allied HQ while it stands on the player's side.</summary>
        private Vector2? AllyHqPosition(SimWorld world) =>
            AllyHq.IsValid && world.TryGetVehicle(AllyHq, out var hq) && hq.IsAlive && hq.Team == PlayerTeam ? hq.Position : null;

        /// <summary>
        /// Evacuation: the site while evacuees are still to leave it, then the last of them still on
        /// the road (the rearguard covers the column home).
        /// </summary>
        private Vector2? EvacuationPoint(SimWorld world)
        {
            if (_def.Convoy == null) return null;
            if (_convoySpawned < _def.ConvoyCount) return _def.Convoy.Position;
            for (var i = _convoy.Count - 1; i >= 0; i--)
            {
                var (id, waypoint) = _convoy[i];
                if (waypoint < _def.Convoy.Route.Count && world.TryGetVehicle(id, out var truck) && truck.IsAlive) return truck.Position;
            }
            return null;
        }

        /// <summary>Protect: the building the enemy is closest to, where the army should stand.</summary>
        private Vector2? Threatened(SimWorld world) =>
            world.TryGetProp(NearestTargetId(world, EnemyCentre(world)), out var p) ? p.Position : null;

        private static Vector2 EnemyCentre(SimWorld world)
        {
            var sum = Vector2.Zero;
            var count = 0;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != EnemyTeam || v.Flying || v.Def.Static) continue;
                sum += v.Position;
                count++;
            }
            if (count > 0) return sum / count;
            return world.TryGetRally(EnemyTeam, out var camp) ? camp : Vector2.Zero;
        }

        private Vector2? NearestTarget(SimWorld world) =>
            world.TryGetProp(NearestTargetId(world), out var p) ? p.Position : null;

        private EntityId NearestTargetId(SimWorld world) => NearestTargetId(world, PlayerCentre(world) ?? Vector2.Zero);

        private EntityId NearestTargetId(SimWorld world, Vector2 from)
        {
            var best = EntityId.None;
            var bestDistance = float.MaxValue;
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
