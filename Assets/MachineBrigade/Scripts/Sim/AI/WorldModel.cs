#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Sim.AI
{
    /// <summary>The 8 force groups of the research sheet "Chiến thuật" (its CP share columns, in that order).</summary>
    public enum ForceGroup
    {
        Armour,
        Light,
        AntiTank,
        Artillery,
        AntiAir,
        Helicopter,
        Plane,
        Support,
    }

    /// <summary>The threat layers of the World Model (prompt 28 A.1).</summary>
    public enum ThreatKind
    {
        AntiAir,
        AntiTank,
        Artillery,
        Splash,
    }

    /// <summary>The five event kinds of the sheet "Sự kiện" (prompt 28 A.4).</summary>
    public enum IntelEventKind
    {
        Threat,
        Opportunity,
        Window,
        Mismatch,
        ObjectivePressure,
    }

    /// <summary>What a side knows about one area for a threat kind: "not seen" is not "confirmed absent" (A.2).</summary>
    public enum Knowledge
    {
        Unknown,
        Present,
        ConfirmedAbsent,
    }

    /// <summary>One enemy as a side remembers it (A.2): where and when it was last seen, and how sure the side still is.</summary>
    public sealed class Contact
    {
        internal Contact(EntityId id) => Id = id;

        public EntityId Id { get; }
        public string Unit { get; internal set; } = "";
        public ForceGroup? Group { get; internal set; }
        public Vector2 Position { get; internal set; }

        /// <summary>The movement observed when last seen (m/s).</summary>
        public Vector2 Velocity { get; internal set; }

        /// <summary>Fighting worth when last seen (the catalog's Power times the health share).</summary>
        public float Strength { get; internal set; }
        public double LastSeen { get; internal set; }
        public bool Flying { get; internal set; }
        public bool HighValue { get; internal set; }

        /// <summary>Its last position was seen empty since: the side knows it exists, not where (not painted on the grid).</summary>
        public bool Displaced { get; internal set; }

        /// <summary>Seen this update (in sight now).</summary>
        public bool InSight { get; internal set; }

        internal bool WasInSight;
        internal Vector2 PreviousPosition;
        internal bool AntiAir, AntiTank, Artillery, Reloading;
        internal float Reach, SplashRadius;

        public float Age(double now) => (float)(now - LastSeen);

        /// <summary>1 when seen now, falling by <paramref name="decay"/> a second since (prompt 28 L: confidence decay).</summary>
        public float Confidence(double now, float decay) => MathF.Max(0f, 1f - Age(now) * decay);

        public override string ToString() => $"{Group?.ToString() ?? "Other"} {Unit}#{Id.Value}, strength {Strength:0.#}";
    }

    /// <summary>A situation the World Model found (A.4): the commander and squads read these, never the raw map.</summary>
    public sealed class IntelEvent
    {
        public IntelEventKind Kind { get; internal set; }
        public string Reason { get; internal set; } = "";

        /// <summary>0-100.</summary>
        public float Priority { get; internal set; }

        /// <summary>0-1: below 1 when built on information that is not certain.</summary>
        public float Confidence { get; internal set; }
        public double Created { get; internal set; }
        public double Expires { get; internal set; }
        public Vector2 Centre { get; internal set; }
        public float Radius { get; internal set; }

        /// <summary>The enemy (or objective index) it is about, if one.</summary>
        public EntityId Subject { get; internal set; }

        /// <summary>MISMATCH: the force group to buy.</summary>
        public ForceGroup? Need { get; internal set; }

        public override string ToString() => $"{Kind} p{Priority:0} c{Confidence:0.00} {Reason}";
    }

    /// <summary>A cluster of known enemies and the movement observed for it (A.1: the enemy squads' vectors).</summary>
    public readonly struct EnemyGroup
    {
        public EnemyGroup(Vector2 centre, Vector2 velocity, float strength, float confidence, int count, bool air)
        {
            Centre = centre;
            Velocity = velocity;
            Strength = strength;
            Confidence = confidence;
            Count = count;
            Air = air;
        }

        public Vector2 Centre { get; }
        public Vector2 Velocity { get; }
        public float Strength { get; }
        public float Confidence { get; }
        public int Count { get; }
        public bool Air { get; }
    }

    /// <summary>A telegraphed blow about to land: a boss's big attack or super weapon, or a fire-support strike.</summary>
    public readonly struct WarningZone
    {
        public WarningZone(int team, Vector2 centre, float radius, double due, bool big)
            : this(team, centre, radius, due, big, 0, centre)
        {
        }

        /// <summary>AI MASTER P4 (spec 214): a boss's zone with the boss (id) and where it stood when it telegraphed (public).</summary>
        public WarningZone(int team, Vector2 centre, float radius, double due, bool big, int source, Vector2 origin)
        {
            Team = team;
            Centre = centre;
            Radius = radius;
            Due = due;
            Big = big;
            Source = source;
            Origin = origin;
        }

        /// <summary>AI MASTER P4: the caster's id (0: unknown / a support strike).</summary>
        public int Source { get; }

        /// <summary>AI MASTER P4: where the caster stood (the centre when unknown): the frame a boss pattern is learnt in.</summary>
        public Vector2 Origin { get; }

        /// <summary>The side that called it.</summary>
        public int Team { get; }
        public Vector2 Centre { get; }
        public float Radius { get; }
        public double Due { get; }

        /// <summary>A boss's big attack (or super weapon) rather than a support strike.</summary>
        public bool Big { get; }
    }

    /// <summary>
    /// Prompt 28 A: the battlefield picture shared by every AI layer. One <see cref="TeamIntel"/> per side, refreshed
    /// about <see cref="AiParams.WorldRate"/> times a second on demand (the first query of a side after its interval),
    /// so every squad and unit reads the same tables and nobody recomputes them (A.6, M.3). Reads only; changes nothing
    /// in the world, so it can never change a battle by being asked.
    /// </summary>
    public sealed class WorldModel
    {
        private readonly SimWorld _world;
        private readonly Dictionary<int, TeamIntel> _teams = new();

        public WorldModel(SimWorld world) => _world = world;

        /// <summary>The capture points, if the mode has them (OBJECTIVE_PRESSURE events).</summary>
        public IObjectiveMode? Objectives { get; set; }

        /// <summary>The side's picture, refreshed first if its interval has passed.</summary>
        public TeamIntel For(int team)
        {
            if (!_teams.TryGetValue(team, out var intel))
                _teams[team] = intel = new TeamIntel(_world, this, team);
            var rate = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.WorldModel.ForWorldRateFloor, _world.Catalog.Ai.WorldRate);
            if (!intel.Ready || _world.Time - intel.UpdatedAt >= 1.0 / rate - 1e-6)
                intel.Refresh();
            return intel;
        }

        /// <summary>
        /// Prompt 28 J: the side's picture as it stands, never refreshed (null before its first refresh). The local AI
        /// viewer reads this, so looking at the AI never moves the moment it refreshes (a battle stays the same).
        /// </summary>
        public TeamIntel? Peek(int team) => _teams.TryGetValue(team, out var intel) && intel.Ready ? intel : null;
    }

    /// <summary>One side's battlefield picture: grids of strength and threat (cells of <see cref="AiParams.WorldCell"/> m), contacts and events.</summary>
    public sealed class TeamIntel
    {
        private const int Groups = 8;
        private const int Threats = 4;

        private readonly SimWorld _world;
        private readonly WorldModel _model;
        private readonly Vector2 _min;
        private readonly bool[] _narrow;
        private readonly List<Contact> _contacts = new();
        private readonly Dictionary<EntityId, Contact> _byId = new();
        private readonly List<IntelEvent> _events = new();
        private readonly List<EnemyGroup> _groups = new();
        private readonly List<WarningZone> _warnings = new();
        private readonly List<int> _contested = new();
        private readonly List<int> _front = new();
        private readonly List<int> _chokepoints = new();
        private readonly List<(int team, Vector2 point, float radius, double lands)> _strikeBuffer = new();
        private readonly float[] _blurOwn, _blurEnemy;

        internal TeamIntel(SimWorld world, WorldModel model, int team)
        {
            _world = world;
            _model = model;
            Team = team;
            Cell = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.CtorWorldCellFloor, world.Catalog.Ai.WorldCell);
            _min = world.Map.Min;
            Columns = Math.Max(1, (int)MathF.Ceiling(world.Map.Width / Cell));
            Rows = Math.Max(1, (int)MathF.Ceiling(world.Map.Length / Cell));
            var n = Columns * Rows;
            Own = new float[n];
            Enemy = new float[n];
            Density = new int[n];
            Seen = new double[n];
            for (var i = 0; i < n; i++) Seen[i] = double.NegativeInfinity;
            Threat = new float[Threats][];
            for (var k = 0; k < Threats; k++) Threat[k] = new float[n];
            _blurOwn = new float[n];
            _blurEnemy = new float[n];
            _narrow = NarrowCells(world, n);
        }

        public int Team { get; }
        public float Cell { get; }
        public int Columns { get; }
        public int Rows { get; }
        public double UpdatedAt { get; private set; }
        internal bool Ready { get; private set; }

        /// <summary>Prompt 28 K: Very Hard's designed advantage (sees every enemy). Off for every other difficulty.</summary>
        public bool Omniscient { get; set; }

        /// <summary>Overrides the confidence decay (K: slower for Very Hard); null: the catalog's.</summary>
        public float? Decay { get; set; }

        public float ConfidenceDecay => Decay ?? _world.Catalog.Ai.ConfidenceDecay;

        /// <summary>Own fighting worth per cell.</summary>
        public float[] Own { get; }

        /// <summary>Estimated enemy fighting worth per cell (confidence-weighted).</summary>
        public float[] Enemy { get; }

        /// <summary>Per <see cref="ThreatKind"/>, the enemy's reach per cell (confidence-weighted strength covering it).</summary>
        public float[][] Threat { get; }

        /// <summary>Vehicles per cell (own, and enemies in sight): with narrow cells, the chokepoints.</summary>
        public int[] Density { get; }

        /// <summary>When a cell was last inside this side's sight.</summary>
        public double[] Seen { get; }

        /// <summary>Own and estimated enemy strength by <see cref="ForceGroup"/>.</summary>
        public float[] OwnComposition { get; } = new float[Groups];
        public float[] EnemyComposition { get; } = new float[Groups];
        public float OwnTotal { get; private set; }
        public float EnemyTotal { get; private set; }

        /// <summary>The largest splash radius among known enemy weapons (the spread-out distance of prompt 28 L is a multiple of it).</summary>
        public float EnemySplash { get; private set; }

        public IReadOnlyList<Contact> Contacts => _contacts;
        public IReadOnlyList<IntelEvent> Events => _events;
        public IReadOnlyList<EnemyGroup> EnemyGroups => _groups;
        public IReadOnlyList<WarningZone> Warnings => _warnings;

        /// <summary>Cells both sides reach with comparable strength.</summary>
        public IReadOnlyList<int> Contested => _contested;

        /// <summary>Cells where the balance of strength turns from this side's to the enemy's: the estimated front line.</summary>
        public IReadOnlyList<int> Front => _front;

        /// <summary>Narrow passages (partly blocked cells) with two or more vehicles in them.</summary>
        public IReadOnlyList<int> Chokepoints => _chokepoints;

        public int CellIndex(Vector2 p)
        {
            var x = Math.Clamp((int)((p.X - _min.X) / Cell), 0, Columns - 1);
            var y = Math.Clamp((int)((p.Y - _min.Y) / Cell), 0, Rows - 1);
            return y * Columns + x;
        }

        public Vector2 CellCentre(int index) =>
            _min + new Vector2((index % Columns + global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.CellCentreIndexAdd) * Cell, (index / Columns + global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.CellCentreIndexAdd) * Cell);

        public float ThreatAt(ThreatKind kind, Vector2 p) => Threat[(int)kind][CellIndex(p)];

        /// <summary>A side tells "no enemy anti-air seen here" (Unknown) from "seen lately and none there" (ConfirmedAbsent).</summary>
        public Knowledge Know(ThreatKind kind, Vector2 p, float? freshSeconds = null)
        {
            var c = CellIndex(p);
            if (Threat[(int)kind][c] > 0f) return Knowledge.Present;
            return _world.Time - Seen[c] <= (freshSeconds ?? global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.KnowFreshSeconds) ? Knowledge.ConfirmedAbsent : Knowledge.Unknown;
        }

        /// <summary>Own and estimated enemy strength within <paramref name="radius"/> of a point (by cell centres).</summary>
        public (float own, float enemy) StrengthAround(Vector2 p, float radius)
        {
            float own = 0f, enemy = 0f;
            ForCells(p, radius, c =>
            {
                own += Own[c];
                enemy += Enemy[c];
            });
            return (own, enemy);
        }

        public Contact? Find(EntityId id) => _byId.TryGetValue(id, out var c) ? c : null;

        public static ForceGroup? GroupOf(Content.VehicleDef def) => def.Class switch
        {
            Content.UnitClass.Tank or Content.UnitClass.Heavy => ForceGroup.Armour,
            Content.UnitClass.Scout or Content.UnitClass.Light => ForceGroup.Light,
            Content.UnitClass.TankHunter => ForceGroup.AntiTank,
            Content.UnitClass.Artillery => ForceGroup.Artillery,
            Content.UnitClass.AntiAir => ForceGroup.AntiAir,
            Content.UnitClass.Helicopter => ForceGroup.Helicopter,
            Content.UnitClass.Plane => ForceGroup.Plane,
            Content.UnitClass.Support => ForceGroup.Support,
            _ => null, // fixed defences and bosses are not bought: they count in strength and threat, not composition
        };

        /// <summary>A vehicle's fighting worth: the catalog's Power (CP, elites and defences by health) times its health share.</summary>
        public static float StrengthOf(Vehicle v)
        {
            var power = v.Def.Boss ? v.MaxHp / global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.StrengthOfMaxHpDivisor : v.Def.Power;
            return power * (v.MaxHp > 0f ? Math.Clamp(v.Hp / v.MaxHp, 0f, 1f) : 1f);
        }

        internal void Refresh()
        {
            var now = _world.Time;
            var ai = _world.Catalog.Ai;
            var decay = ConfidenceDecay;
            UpdatedAt = now;
            Ready = true;
            Array.Clear(Own, 0, Own.Length);
            Array.Clear(Enemy, 0, Enemy.Length);
            Array.Clear(Density, 0, Density.Length);
            foreach (var t in Threat) Array.Clear(t, 0, t.Length);
            Array.Clear(OwnComposition, 0, Groups);
            Array.Clear(EnemyComposition, 0, Groups);
            OwnTotal = EnemyTotal = 0f;

            // Own side and its sight.
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Team) continue;
                var s = StrengthOf(v);
                var c = CellIndex(v.Position);
                Own[c] += s;
                Density[c]++;
                OwnTotal += s;
                if (GroupOf(v.Def) is { } g) OwnComposition[(int)g] += s;
                ForCells(v.Position, v.Def.VisionRange, i => Seen[i] = now);
            }

            // Enemies in sight become (or refresh) contacts.
            foreach (var c in _contacts)
            {
                c.WasInSight = c.InSight;
                c.InSight = false;
                c.PreviousPosition = c.Position;
            }
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team == Team || v.Team == Teams.Neutral) continue;
                if (!Omniscient && !v.IsVisibleTo(Team)) continue;
                if (!_byId.TryGetValue(v.Id, out var contact))
                {
                    contact = new Contact(v.Id);
                    Insert(contact);
                    contact.PreviousPosition = v.Position;
                }
                See(contact, v, now);
                Density[CellIndex(v.Position)]++;
            }

            // Forget what is gone: dead where the side could see it, or certainty run out; mark moved-off ones.
            for (var i = _contacts.Count - 1; i >= 0; i--)
            {
                var c = _contacts[i];
                if (c.InSight) continue;
                var cell = CellIndex(c.Position);
                var seenEmpty = Seen[cell] >= now;
                var alive = _world.TryGetVehicle(c.Id, out var v) && v.IsAlive;
                if ((!alive && seenEmpty) || c.Confidence(now, decay) <= 0f)
                {
                    _byId.Remove(c.Id);
                    _contacts.RemoveAt(i);
                    continue;
                }
                if (seenEmpty) c.Displaced = true;
            }

            // Paint strength and threats; composition counts every contact, placed or not.
            var maxSplash = 0f;
            var meanPower = 0f;
            foreach (var c in _contacts) meanPower += c.Strength;
            meanPower = _contacts.Count > 0 ? meanPower / _contacts.Count : 0f;
            var highValue = ai.Get("world.highValue", 1.5f);
            foreach (var c in _contacts)
            {
                var conf = c.Confidence(now, decay);
                var s = c.Strength * conf;
                EnemyTotal += s;
                if (c.Group is { } g) EnemyComposition[(int)g] += s;
                c.HighValue = c.Group is ForceGroup.Artillery or ForceGroup.Support || c.Strength >= meanPower * highValue;
                maxSplash = MathF.Max(maxSplash, c.SplashRadius);
                if (c.Displaced) continue;
                Enemy[CellIndex(c.Position)] += s;
                if (c.AntiAir) Paint(ThreatKind.AntiAir, c.Position, c.Reach, s);
                if (c.AntiTank) Paint(ThreatKind.AntiTank, c.Position, c.Reach, s);
                if (c.Artillery) Paint(ThreatKind.Artillery, c.Position, c.Reach, s);
                if (c.SplashRadius >= ai.Get("world.splashMin", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.RefreshFallback2)) Paint(ThreatKind.Splash, c.Position, c.Reach, s);
            }
            EnemySplash = maxSplash;

            CollectWarnings();
            FrontLine();
            FindChokepoints();
            Cluster(now, decay);
            Detect(now, decay);
        }

        private void Insert(Contact contact)
        {
            // Kept in id order: every walk over the contacts is the same in a replay (prompt 28 N).
            var at = _contacts.Count;
            while (at > 0 && _contacts[at - 1].Id.Value > contact.Id.Value) at--;
            _contacts.Insert(at, contact);
            _byId[contact.Id] = contact;
        }

        private void See(Contact c, Vehicle v, double now)
        {
            c.Unit = v.Def.Id;
            c.Group = GroupOf(v.Def);
            c.Position = v.Position;
            c.Velocity = SimMath.Forward(v.Heading) * v.Speed;
            c.Strength = StrengthOf(v);
            c.LastSeen = now;
            c.Flying = v.Flying;
            c.InSight = true;
            c.Displaced = false;
            c.Reloading = v.OutOfAmmo;
            c.AntiAir = c.AntiTank = c.Artillery = false;
            c.Reach = c.SplashRadius = 0f;
            foreach (var w in v.Arms)
            {
                c.Reach = MathF.Max(c.Reach, w.Range);
                c.SplashRadius = MathF.Max(c.SplashRadius, w.SplashRadius);
                if (w.CanTarget(true)) c.AntiAir = true;
                if (w.MinRange > 0f) c.Artillery = true;
            }
            c.AntiAir &= c.Group is ForceGroup.AntiAir or null || !v.Def.Weapon.CanTarget(false);
            c.AntiTank = c.Group is ForceGroup.AntiTank or ForceGroup.Armour || (c.Group == null && v.Def.Weapon.CanTarget(false));
            c.Artillery |= c.Group == ForceGroup.Artillery;
        }

        private void Paint(ThreatKind kind, Vector2 at, float radius, float value)
        {
            var layer = Threat[(int)kind];
            ForCells(at, radius, i => layer[i] += value);
        }

        private void ForCells(Vector2 at, float radius, Action<int> visit)
        {
            var (x0, y0) = XY(at - new Vector2(radius));
            var (x1, y1) = XY(at + new Vector2(radius));
            var r2 = (radius + Cell * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.ForCellsCellScale) * (radius + Cell * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.ForCellsCellScale);
            for (var y = y0; y <= y1; y++)
            for (var x = x0; x <= x1; x++)
            {
                var i = y * Columns + x;
                if (Vector2.DistanceSquared(CellCentre(i), at) <= r2) visit(i);
            }
        }

        private (int x, int y) XY(Vector2 p) =>
            (Math.Clamp((int)((p.X - _min.X) / Cell), 0, Columns - 1), Math.Clamp((int)((p.Y - _min.Y) / Cell), 0, Rows - 1));

        private void CollectWarnings()
        {
            _warnings.Clear();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.BigAttack is not { Stage: BigStage.Charging } big) continue;
                foreach (var z in big.Zones)
                    if (z.Harmful)
                        _warnings.Add(new WarningZone(v.Team, z.Centre, z.Rect ? MathF.Max(z.HalfLength, z.HalfWidth) : z.Radius, z.Due, true, v.Id.Value, v.Position));
            }
            _strikeBuffer.Clear();
            _world.Strikes.Incoming(_strikeBuffer);
            foreach (var (team, point, radius, lands) in _strikeBuffer)
                _warnings.Add(new WarningZone(team, point, radius, lands, false));
            // Prompt 33 L5: the rail ahead of a train and the crossings that warn (no side's: every squad dodges them).
            _world.Rails.Warnings(_warnings);
        }

        private void FrontLine()
        {
            Blur(Own, _blurOwn);
            Blur(Enemy, _blurEnemy);
            _contested.Clear();
            _front.Clear();
            for (var i = 0; i < _blurOwn.Length; i++)
            {
                float own = _blurOwn[i], enemy = _blurEnemy[i];
                if (own > 0f && enemy > 0f && MathF.Abs(own - enemy) <= global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.FrontLineMaxScale * MathF.Max(own, enemy)) _contested.Add(i);
                var sign = MathF.Sign(own - enemy);
                if (sign <= 0 || own <= 0f) continue;
                // A cell this side holds next to one the enemy holds.
                int x = i % Columns, y = i / Columns;
                if ((x > 0 && Holds(i - 1)) || (x < Columns - 1 && Holds(i + 1)) || (y > 0 && Holds(i - Columns)) || (y < Rows - 1 && Holds(i + Columns)))
                    _front.Add(i);
            }
            bool Holds(int j) => _blurEnemy[j] > _blurOwn[j];
        }

        private void Blur(float[] src, float[] dst)
        {
            for (var y = 0; y < Rows; y++)
            for (var x = 0; x < Columns; x++)
            {
                var sum = 0f;
                for (var dy = -1; dy <= 1; dy++)
                for (var dx = -1; dx <= 1; dx++)
                {
                    int nx = x + dx, ny = y + dy;
                    if (nx >= 0 && ny >= 0 && nx < Columns && ny < Rows) sum += src[ny * Columns + nx];
                }
                dst[y * Columns + x] = sum;
            }
        }

        private void FindChokepoints()
        {
            _chokepoints.Clear();
            for (var i = 0; i < Density.Length; i++)
                if (_narrow[i] && Density[i] >= 2) _chokepoints.Add(i);
        }

        private bool[] NarrowCells(SimWorld world, int n)
        {
            // A cell is narrow when part of its ground is blocked: a lane between walls, cliffs or wrecks.
            var narrow = new bool[n];
            var grid = world.Grid;
            for (var i = 0; i < n; i++)
            {
                var centre = CellCentre(i);
                int open = 0, all = 0;
                for (var sy = -2; sy <= 2; sy++)
                for (var sx = -2; sx <= 2; sx++)
                {
                    all++;
                    if (grid.IsWalkable(centre + new Vector2(sx, sy) * (Cell * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.NarrowCellsCellScale))) open++;
                }
                narrow[i] = open > 0 && open <= all * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.NarrowCellsAllScale;
            }
            return narrow;
        }

        private void Cluster(double now, float decay)
        {
            _groups.Clear();
            float reach = global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.ClusterReach;
            var used = new bool[_contacts.Count];
            for (var i = 0; i < _contacts.Count; i++)
            {
                var a = _contacts[i];
                if (used[i] || a.Displaced) continue;
                Vector2 centre = Vector2.Zero, velocity = Vector2.Zero;
                float strength = 0f, weight = 0f, confidence = 1f;
                var count = 0;
                for (var j = i; j < _contacts.Count; j++)
                {
                    var b = _contacts[j];
                    if (used[j] || b.Displaced || b.Flying != a.Flying || Vector2.Distance(a.Position, b.Position) > reach) continue;
                    used[j] = true;
                    var w = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.ClusterStrengthFloor, b.Strength);
                    centre += b.Position * w;
                    velocity += b.Velocity * w;
                    weight += w;
                    var conf = b.Confidence(now, decay);
                    strength += b.Strength * conf;
                    confidence = MathF.Min(confidence, conf);
                    count++;
                }
                _groups.Add(new EnemyGroup(centre / weight, velocity / weight, strength, confidence, count, a.Flying));
            }
        }

        private void Detect(double now, float decay)
        {
            var ai = _world.Catalog.Ai;
            var life = ai.Get("world.eventLife", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectFallback);
            _events.RemoveAll(e => e.Expires <= now);

            foreach (var c in _contacts)
            {
                if (!c.InSight) continue;
                // OPPORTUNITY: a valuable target has just come into sight.
                if (!c.WasInSight && c.HighValue)
                    Raise(IntelEventKind.Opportunity, $"{c.Group?.ToString() ?? c.Unit} spotted", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectMinAdd + global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectMinScale * MathF.Min(global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectStrengthCap, c.Strength / MathF.Max(1f, EnemyTotal / MathF.Max(1, _contacts.Count))),
                        1f, now + life, c.Position, Cell, c.Id);
                // WINDOW: enemy anti-air has moved off where it stood; a valuable enemy is reloading.
                if (c.WasInSight && c.Group == ForceGroup.AntiAir && Vector2.Distance(c.PreviousPosition, c.Position) > Cell * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectCellScale)
                    Raise(IntelEventKind.Window, "enemy anti-air moved off", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectPriority, 1f, now + life, c.PreviousPosition, c.Reach, c.Id);
                if (c.Reloading && c.HighValue)
                    Raise(IntelEventKind.Window, $"{c.Unit} reloading", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectPriority2, 1f, now + life * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectLifeScale, c.Position, Cell, c.Id);
            }

            // THREAT: a telegraphed blow over own vehicles; a stronger enemy group closing in; aircraft inbound.
            foreach (var w in _warnings)
            {
                if (w.Team == Team || w.Due < now) continue;
                var (own, _) = StrengthAround(w.Centre, w.Radius);
                if (own > 0f)
                    Raise(IntelEventKind.Threat, w.Big ? "big attack incoming" : "strike incoming", w.Big ? global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectBigTrue : global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectBigFalse, 1f, w.Due, w.Centre, w.Radius, EntityId.None);
            }
            var overwhelm = ai.OverwhelmRatio;
            for (var i = 0; i < _groups.Count; i++)
            {
                var g = _groups[i];
                if (g.Velocity.LengthSquared() < global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectLengthSquaredMax) continue;
                var ahead = g.Centre + Vector2.Normalize(g.Velocity) * Cell * 3f;
                var (own, _) = StrengthAround(ahead, Cell * 3f);
                if (own <= 0f) continue;
                if (g.Air)
                    Raise(IntelEventKind.Threat, "enemy aircraft inbound", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectPriority3, g.Confidence, now + life, ahead, Cell * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectCellScale2, EntityId.None, null, i);
                else if (g.Strength >= own * overwhelm)
                    Raise(IntelEventKind.Threat, "overwhelming enemy force closing", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectPriority4, g.Confidence, now + life, ahead, Cell * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectCellScale2, EntityId.None, null, i);
            }

            // MISMATCH: the army does not fit the enemy's.
            if (EnemyTotal > 0f && OwnTotal > 0f)
            {
                var air = (EnemyComposition[(int)ForceGroup.Helicopter] + EnemyComposition[(int)ForceGroup.Plane]) / EnemyTotal;
                var aa = OwnComposition[(int)ForceGroup.AntiAir] / OwnTotal;
                if (air >= ai.Get("world.airShare", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectFallback2) && aa < ai.Get("world.aaShare", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectFallback3))
                    Raise(IntelEventKind.Mismatch, "no anti-air against many aircraft", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectPriority5, AverageConfidence(now, decay), now + life * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectLifeScale2,
                        Vector2.Zero, 0f, EntityId.None, ForceGroup.AntiAir);
                var armour = EnemyComposition[(int)ForceGroup.Armour] / EnemyTotal;
                var at = (OwnComposition[(int)ForceGroup.AntiTank] + OwnComposition[(int)ForceGroup.Armour] * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectOwnCompositionScale) / OwnTotal;
                if (armour >= ai.Get("world.armourShare", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectFallback4) && at < ai.Get("world.atShare", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectFallback5))
                    Raise(IntelEventKind.Mismatch, "no anti-tank against many tanks", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectPriority, AverageConfidence(now, decay), now + life * global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectLifeScale2,
                        Vector2.Zero, 0f, EntityId.None, ForceGroup.AntiTank);
            }

            // OBJECTIVE_PRESSURE: an own point contested, or a point the enemy is taking; points worth more (I.6).
            if (_model.Objectives is { } mode)
            {
                for (var i = 0; i < mode.Points.Count; i++)
                {
                    var p = mode.Points[i];
                    if (_world.PressureTier >= 1 && p.Owner != Team && !p.Locked)
                        Raise(IntelEventKind.ObjectivePressure, $"point {p.Def.Name} worth more", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectPriority2, 1f, now + life, p.Def.Position, p.Def.Radius,
                            new EntityId(-(i + 1)));
                    if (p.Owner == Team && p.Contested)
                        Raise(IntelEventKind.ObjectivePressure, $"losing point {p.Def.Name}", global::MachineBrigade.Sim.Content.SimTunables.Ai.TeamIntel.DetectPriority6, 1f, now + life, p.Def.Position, p.Def.Radius,
                            new EntityId(-(i + 1)));
                }
            }
        }

        private float AverageConfidence(double now, float decay)
        {
            if (_contacts.Count == 0) return 0f;
            var sum = 0f;
            foreach (var c in _contacts) sum += c.Confidence(now, decay);
            return sum / _contacts.Count;
        }

        /// <summary>Adds an event unless one of the same kind, subject and reason is still running (that one is refreshed).</summary>
        private void Raise(IntelEventKind kind, string reason, float priority, float confidence, double expires, Vector2 centre, float radius,
            EntityId subject, ForceGroup? need = null, int tag = 0)
        {
            foreach (var e in _events)
            {
                if (e.Kind != kind || e.Subject.Value != subject.Value || e.Reason != reason || e.Need != need) continue;
                if (subject.Value == 0 && need == null && Vector2.Distance(e.Centre, centre) > radius + e.Radius) continue;
                e.Expires = Math.Max(e.Expires, expires);
                e.Confidence = confidence;
                e.Centre = centre;
                return;
            }
            _events.Add(new IntelEvent
            {
                Kind = kind, Reason = reason, Priority = priority, Confidence = confidence, Created = _world.Time,
                Expires = expires, Centre = centre, Radius = radius, Subject = subject, Need = need,
            });
        }
    }
}
