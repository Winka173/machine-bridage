#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>A level crossing's state: open, warning (lights and bells), closed (barriers down), a train passing.</summary>
    public enum CrossingState
    {
        Open,
        Warning,
        Closed,
        TrainPassing,
    }

    /// <summary>A level crossing in play: its state and since when (prompt 33 L5).</summary>
    public sealed class RailCrossing
    {
        internal RailCrossing(int rail, RailCrossingDef def, string site)
        {
            Rail = rail;
            Def = def;
            Site = site;
            WarnSeconds = RailSystem.WarningFor(def);
        }

        public int Rail { get; }
        public RailCrossingDef Def { get; }

        /// <summary>The prebuilt ground state (prompt 31 L3) its barriers close: "open" / "closed".</summary>
        public string Site { get; }

        public CrossingState State { get; internal set; }

        /// <summary>The tick its state began.</summary>
        public long Since { get; internal set; }

        /// <summary>The least it warns before it closes: max(4 s, its length / 4.5 m/s + 0.5 s).</summary>
        public float WarnSeconds { get; }

        /// <summary>Whether the train coming (or passing) is a boss train.</summary>
        public bool Boss { get; internal set; }

        /// <summary>Whether its barriers close the ground (its "closed" state passed the load-time check).</summary>
        public bool Closes { get; internal set; }

        internal int ClearTicks;

        /// <summary>Every state change so far, in order: (tick, state) (the tests and the replay read it).</summary>
        public readonly List<(long tick, CrossingState state)> History = new();
    }

    /// <summary>
    /// A support train's run on a rail (the Siege defender's reinforcements): a sim object that only pushes, never a target.
    /// It runs the view's curve (<see cref="RailSystem.SupportOffset"/>): in over 9 s to its stop, 7 s there, out over 9 s.
    /// It is in play from the tick its front passes the entry gate (<see cref="EntryTick"/>) to the tick it is back out.
    /// </summary>
    public sealed class RailRun
    {
        internal RailRun(int rail, int team, double due, float stopFront)
        {
            Rail = rail;
            Team = team;
            Due = due;
            StopFront = stopFront;
        }

        public int Rail { get; }
        public int Team { get; }

        /// <summary>When it stands at its stop (the vehicles get off).</summary>
        public double Due { get; }

        /// <summary>Where its front stands at the stop (metres along the rail).</summary>
        public float StopFront { get; }

        public long EntryTick { get; internal set; } = -1;
        public long ExitTick { get; internal set; } = -1;
        public bool Inside { get; internal set; }
        public bool Done { get; internal set; }

        /// <summary>Its front at a moment (metres along the rail); a pure function of time, so the view's stand-in outside meets it at the gate.</summary>
        public float FrontAt(double time) => StopFront + RailSystem.SupportOffset((float)(time - Due));
    }

    /// <summary>
    /// Prompt 33 L5 (DECISIONS "Prompt 33 L5"): the trains on their rails (<see cref="RailSpline"/>) and the level crossings.
    /// <list type="bullet">
    /// <item>A boss train (frame "train": Juggernaut, Nemesis, Gungnir) spawned within 8 m of a rail is held on it: its
    /// orders' points are taken onto the line and it runs there (speeding up and braking at its own rate), never on the
    /// ground grid; the movement system and the separation leave it alone.</item>
    /// <item>The Siege support train: when the fortress line announces a train (<see cref="SimEventKind.Arrival"/>), a
    /// <see cref="RailRun"/> on the siege rail, on the view's curve, so the view's train outside the map (visual only) and
    /// the run meet at the entry gate on its entry tick.</item>
    /// <item>Crossings: OPEN -> WARNING when a train can reach it within its warning + 1.5 s (at the train's top speed, or
    /// within 8 m), WARNING -> CLOSED once it has warned its full time and the train is 1.5 s (or 3 m) off, CLOSED ->
    /// TRAIN_PASSING while the train is on it, -> OPEN 0.5 s after it has gone (or WARNING again for the next). CLOSED and
    /// TRAIN_PASSING close the crossing's ground through its prebuilt state (prompt 31 L3: routes go round, nobody left on
    /// it). While it warns no new route goes over it, nor over the rail ahead of a train (path costs); every vehicle on the
    /// line ahead of a train is told to get off it (its emergency move: the AI's squads also see the danger as warning rings
    /// and dodge them, prompt 28); whoever is still on it when the train comes is put beside the line (a fixed rule: the
    /// nearest open ground straight out from the line on its side; no physics). A support train only pushes; a boss train
    /// (Juggernaut, Nemesis) also hurts an enemy it rams and crushes fixed defences on its line, with a boss's warning
    /// (the siren and a notice) as it bears down on a crossing.</item>
    /// <item>No parking on a rail: a ground vehicle's order point on the line is moved off it (<see cref="OffRail"/>).</item>
    /// </list>
    /// Deterministic: vehicle-list order, the world's clock; everything in the fingerprint (<see cref="Mix"/>).
    /// </summary>
    public sealed class RailSystem
    {
        /// <summary>The slow vehicle a crossing's warning is timed for (m/s).</summary>
        public const float SlowReference = 4.5f;

        /// <summary>A crossing warns at least this long (s).</summary>
        public const float MinWarning = 4f;

        /// <summary>The barriers are down this long before the train (s), or when it is this near (m).</summary>
        public const float CloseLead = 1.5f;
        public const float CloseFloor = 3f;

        /// <summary>A crossing warns whenever a train is this near it (m), however slowly it comes.</summary>
        public const float WarnFloor = 8f;

        /// <summary>A crossing stays TRAIN_PASSING this long after the train has gone (ticks: 0.5 s).</summary>
        public const int ClearHoldTicks = 10;

        /// <summary>A boss train's ram (damage to one enemy, at most once in 2 s) and its crush on fixed defences (a second).</summary>
        public const float RamDamage = 600f;
        public const float CrushDps = 600f;

        /// <summary>The support train: its length, its front's stand back from the line's end, its curve (the view's).</summary>
        public const float SupportLength = 50f;
        public const float SupportStopBack = 12.5f;
        public const float SupportTravel = 9f;
        public const float SupportWait = 7f;
        public const float SupportRun = 110f;
        public const float SupportHalfWidth = 1.8f;

        /// <summary>A vehicle on the line ahead of a train is told again at most this often (s).</summary>
        public const double TellEvery = 1.0;

        public const string OpenState = "open";
        public const string ClosedState = "closed";

        private const float AttachReach = 8f;

        private readonly SimWorld _world;
        private readonly List<RailCrossing> _crossings = new();
        private readonly List<RailRun> _runs = new();
        private readonly List<RailRun> _finished = new();
        private readonly List<Train> _trains = new();
        private readonly List<(int rail, float from, float to, double due, bool boss, int team)> _strips = new();
        private readonly List<(Vector2 min, Vector2 max)> _avoid = new();
        private readonly List<(Vector2 centre, float radius, double due)> _dangers = new();
        private readonly PathCosts _costs = new();
        private readonly EntityId[] _one = new EntityId[1];
        private double _bossAlertAt = double.NegativeInfinity;
        private float _dt = 0.05f;

        /// <summary>A train this step: its rail, the stretch it covers (s from back to front), the way it runs and how fast.</summary>
        private struct Train
        {
            public int Rail;
            public float Back, Front;
            public int Dir;
            public float Speed, Top;
            public bool Boss;
            public int Team;
            public float HalfWidth;
            public Vehicle? Vehicle;
            public RailRun? Run;
        }

        public RailSystem(SimWorld world)
        {
            _world = world;
            var rails = world.Map.Rails;
            for (var r = 0; r < rails.Count; r++)
                foreach (var c in rails[r].Crossings)
                {
                    var site = $"rail_{rails[r].Id}_{c.Id}";
                    var crossing = new RailCrossing(r, c, site);
                    _crossings.Add(crossing);
                    if (!c.Closes || world.NavStates.Locked || world.NavStates.TryGet(site, out _)) continue;
                    world.NavStates.Define(new NavSiteDef(site, new[]
                    {
                        new NavStateDef(OpenState),
                        new NavStateDef(ClosedState, new[] { new NavBlock(c.Position, c.Width, c.Depth, 0f) }),
                    }, OpenState));
                }
            if (_crossings.Count == 0) return;
            var anchors = new List<Vector2>();
            foreach (var t in world.Map.Teams) anchors.Add(t.Rally);
            foreach (var p in world.Map.Points) anchors.Add(p.Position);
            Problems = world.NavStates.Validate(anchors);
            foreach (var c in _crossings) c.Closes = c.Def.Closes && world.NavStates.CanSwitch(c.Site, ClosedState);
        }

        public IReadOnlyList<RailSpline> Lines => _world.Map.Rails;
        public IReadOnlyList<RailCrossing> Crossings => _crossings;
        public IReadOnlyList<RailRun> Runs => _runs;

        /// <summary>The last support runs that have come and gone (the tests read their entry and exit ticks).</summary>
        public IReadOnlyList<RailRun> Finished => _finished;

        /// <summary>The crossings' load-time refusals (a crossing whose barriers would seal ground off never closes it; it still warns).</summary>
        public IReadOnlyList<string> Problems { get; private set; } = Array.Empty<string>();

        /// <summary>The danger this step (the minimap and the AI's warning rings): rings along the line ahead of each train and on each crossing that is not open.</summary>
        public IReadOnlyList<(Vector2 centre, float radius, double due)> Dangers => _dangers;

        /// <summary>Vehicles told to get off the line, and put beside it by a train, so far (tests and the stuck report).</summary>
        public int Told { get; private set; }
        public int Pushed { get; private set; }

        /// <summary>A crossing's least warning: max(4 s, its length / 4.5 m/s + 0.5 s).</summary>
        public static float WarningFor(RailCrossingDef c) => MathF.Max(MinWarning, c.Length / SlowReference + 0.5f);

        /// <summary>The support train's front against its stop at <paramref name="t"/> s from its stop time (the view's curve: in, wait, out).</summary>
        public static float SupportOffset(float t)
        {
            if (t < 0f)
            {
                var k = Math.Clamp(-t / SupportTravel, 0f, 1f);
                return -SupportRun * k * k;
            }
            if (t < SupportWait) return 0f;
            var o = (t - SupportWait) / SupportTravel;
            return -SupportRun * o * o;
        }

        // ================================================================== joining

        /// <summary>A vehicle joined: a train within reach of a rail is put on it, lined up with it the way it faced.</summary>
        internal void Joined(Vehicle v)
        {
            if (v.Def.Frame?.Move != BossMove.Rail || Lines.Count == 0) return;
            var best = -1;
            var bestS = 0f;
            var bestD = AttachReach;
            for (var r = 0; r < Lines.Count; r++)
            {
                var s = Lines[r].Project(v.Position, out var lateral);
                if (MathF.Abs(lateral) >= bestD) continue;
                bestD = MathF.Abs(lateral);
                best = r;
                bestS = s;
            }
            if (best < 0) return;
            var line = Lines[best];
            v.Rail = best;
            v.RailS = Math.Clamp(bestS, line.PlayFrom, line.PlayTo);
            v.Position = line.At(v.RailS);
            var t = line.Tangent(v.RailS);
            v.RailDir = Vector2.Dot(SimMath.Forward(v.Heading), t) >= 0f ? 1 : -1;
            v.Heading = SimMath.HeadingOf(t * v.RailDir);
            v.Speed = 0f;
        }

        // ================================================================== the siege support train

        /// <summary>A fortress line announced a train (<see cref="SimEventKind.Arrival"/>, kind "rail"): its run on the siege rail.</summary>
        internal void Announced(in SimEvent e)
        {
            if (e.Kind != SimEventKind.Arrival || e.DefId != "rail" || Lines.Count == 0) return;
            var best = -1;
            var bestD = 16f;
            for (var r = 0; r < Lines.Count; r++)
            {
                Lines[r].Project(e.Position, out var lateral);
                var d = MathF.Abs(lateral) - (Lines[r].Kind == "siege" ? 4f : 0f);
                if (d >= bestD) continue;
                bestD = d;
                best = r;
            }
            if (best < 0) return;
            var line = Lines[best];
            var due = _world.Time + e.Value;
            foreach (var run in _runs)
                if (run.Rail == best && Math.Abs(run.Due - due) < 0.5) return;
            _runs.Add(new RailRun(best, e.Team, due, line.Length - SupportStopBack));
        }

        // ================================================================== the step

        internal void Step(float dt)
        {
            _strips.Clear();
            _avoid.Clear();
            _dangers.Clear();
            _trains.Clear();
            if (Lines.Count == 0) return;
            if (dt > 0f) _dt = dt;
            var now = _world.Time;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || !v.OnRail || v.Rail >= Lines.Count) continue;
                if (!v.Def.Static) Drive(v, dt);
                var half = MathF.Max(1f, v.Def.Length * 0.5f);
                _trains.Add(new Train
                {
                    Rail = v.Rail, Back = v.RailS - half, Front = v.RailS + half, Dir = v.RailDir, Speed = MathF.Abs(v.Speed),
                    Top = MathF.Max(0.05f, v.Def.Speed * v.SpeedFactor), Boss = v.Def.Boss && !v.Def.Static, Team = v.Team,
                    HalfWidth = MathF.Max(1.2f, v.Def.Width * 0.5f), Vehicle = v,
                });
            }
            StepRuns(now);
            foreach (var c in _crossings) Update(c, now);
            MarkDangers(now);
            Tell(now);
            foreach (var t in _trains)
                if (t.Speed > 0.02f || t.Run != null) Push(t, dt, now);
        }

        /// <summary>A train runs along its rail to its order's point taken onto the line (speeding up and braking at its own rate).</summary>
        private void Drive(Vehicle v, float dt)
        {
            var line = Lines[v.Rail];
            var target = v.RailS;
            if (v.Order.Kind is OrderKind.Move or OrderKind.AttackMove) target = Math.Clamp(line.Project(v.Order.Point, out _), line.PlayFrom, line.PlayTo);
            var top = v.Stunned || v.Charging || v.Transforming ? 0f : v.Def.Speed * v.SpeedFactor;
            var accel = MathF.Max(0.05f, v.Def.Speed) * dt;
            var left = target - v.RailS;
            var dir = MathF.Abs(left) < 0.05f ? 0 : MathF.Sign(left);
            // The signed speed along the rail: braking to stop at the target.
            var along = v.Speed * v.RailDir;
            var want = dir == 0 ? 0f : dir * MathF.Min(top, MathF.Sqrt(2f * MathF.Max(0.05f, v.Def.Speed) * MathF.Abs(left)));
            along += Math.Clamp(want - along, -accel, accel);
            var step = along * dt;
            if (dir != 0 && MathF.Abs(step) > MathF.Abs(left)) step = left;
            v.RailS = Math.Clamp(v.RailS + step, line.PlayFrom, line.PlayTo);
            if (MathF.Abs(along) > 0.01f) v.RailDir = along > 0f ? 1 : -1;
            v.Speed = MathF.Abs(along);
            v.Position = line.At(v.RailS);
            v.Heading = SimMath.HeadingOf(line.Tangent(v.RailS) * v.RailDir);
            if (v.Order.Kind == OrderKind.Move && dir == 0 && v.Speed < 0.01f) v.SetOrder(Order.Idle);
        }

        private void StepRuns(double now)
        {
            for (var i = 0; i < _runs.Count; i++)
            {
                var run = _runs[i];
                var line = Lines[run.Rail];
                var front = run.FrontAt(now);
                var inside = front >= line.PlayFrom && now - run.Due < SupportWait + 3f * SupportTravel;
                if (inside && !run.Inside && run.EntryTick < 0) run.EntryTick = _world.Tick;
                if (!inside && run.Inside)
                {
                    run.ExitTick = _world.Tick;
                    run.Done = true;
                }
                run.Inside = inside;
                if (run.Done || now - run.Due > SupportWait + 3f * SupportTravel)
                {
                    _runs.RemoveAt(i--);
                    _finished.Add(run);
                    if (_finished.Count > 16) _finished.RemoveAt(0);
                    continue;
                }
                if (!inside) continue;
                var back = MathF.Max(line.PlayFrom, front - SupportLength);
                var later = run.FrontAt(now + _dt);
                _trains.Add(new Train
                {
                    Rail = run.Rail, Back = back, Front = front, Dir = later >= front ? 1 : -1, Speed = MathF.Abs(later - front) / _dt,
                    Top = 2f * SupportRun / SupportTravel, Boss = false, Team = run.Team, HalfWidth = SupportHalfWidth, Run = run,
                });
            }
        }

        // ================================================================== the crossings

        /// <summary>When (s from now) a train's stretch first reaches [lo, hi] along its rail, and how far off it is (m); infinity: never.</summary>
        private (float eta, float distance) Reach(in Train t, float lo, float hi, double now)
        {
            if (t.Run is { } run)
            {
                // The support train's curve, looked ahead a tenth of a second at a time (its first 12 s).
                for (var k = 1; k <= 120; k++)
                {
                    var time = now + 0.1 * k;
                    var front = run.FrontAt(time);
                    var line = Lines[run.Rail];
                    if (front < line.PlayFrom) continue;
                    var back = MathF.Max(line.PlayFrom, front - SupportLength);
                    if (back <= hi && front >= lo) return ((float)(time - now), MathF.Max(0f, lo - front));
                }
                return (float.PositiveInfinity, float.PositiveInfinity);
            }
            var distance = t.Dir > 0 ? lo - t.Front : t.Back - hi;
            if (distance < 0f) return (float.PositiveInfinity, float.PositiveInfinity);
            return (distance / t.Top, distance);
        }

        private void Update(RailCrossing c, double now)
        {
            var lo = c.Def.S - c.Def.Half - 1f;
            var hi = c.Def.S + c.Def.Half + 1f;
            var occupied = false;
            var warn = false;
            var close = false;
            var boss = false;
            foreach (var t in _trains)
            {
                if (t.Rail != c.Rail) continue;
                if (t.Back <= hi && t.Front >= lo)
                {
                    occupied = true;
                    boss |= t.Boss;
                    continue;
                }
                var (eta, distance) = Reach(t, lo, hi, now);
                if (eta <= c.WarnSeconds + CloseLead || distance <= WarnFloor)
                {
                    warn = true;
                    boss |= t.Boss;
                }
                if (eta <= CloseLead || distance <= CloseFloor) close = true;
            }
            // Announced support trains not yet at the gate warn from their curve too.
            foreach (var run in _runs)
            {
                if (run.Rail != c.Rail || run.Inside) continue;
                var (eta, _) = Reach(new Train { Run = run }, lo, hi, now);
                if (eta <= c.WarnSeconds + CloseLead) warn = true;
                if (eta <= CloseLead) close = true;
            }
            c.Boss = boss;
            var elapsed = (_world.Tick - c.Since) * _dt;
            switch (c.State)
            {
                case CrossingState.Open:
                    if (occupied || warn || close) Set(c, CrossingState.Warning);
                    break;
                case CrossingState.Warning:
                    if (!occupied && !warn && !close) Set(c, CrossingState.Open);
                    else if (occupied || (close && elapsed >= c.WarnSeconds - 1e-4)) Set(c, CrossingState.Closed);
                    break;
                case CrossingState.Closed:
                    if (occupied) Set(c, CrossingState.TrainPassing);
                    else if (!warn && !close) Set(c, CrossingState.Open);
                    break;
                case CrossingState.TrainPassing:
                    if (occupied) c.ClearTicks = 0;
                    else if (++c.ClearTicks >= ClearHoldTicks) Set(c, warn || close ? CrossingState.Warning : CrossingState.Open);
                    break;
            }
        }

        private void Set(RailCrossing c, CrossingState state)
        {
            var was = c.State;
            c.State = state;
            c.Since = _world.Tick;
            c.ClearTicks = 0;
            c.History.Add((_world.Tick, state));
            // The barriers: the crossing's ground closed while they are down (its prebuilt state, at the next tick boundary).
            var shut = state is CrossingState.Closed or CrossingState.TrainPassing;
            var wasShut = was is CrossingState.Closed or CrossingState.TrainPassing;
            if (c.Closes && shut != wasShut) _world.NavStates.Schedule(c.Site, shut ? ClosedState : OpenState, _world.Tick + 1, _world.Tick);
            // A boss train bearing down on a crossing: a boss's warning (the siren and a notice), at most every 20 s.
            if (state == CrossingState.Warning && c.Boss && _world.Time - _bossAlertAt >= 20.0)
            {
                _bossAlertAt = _world.Time;
                _world.Emit(SimEvent.Alert(c.Def.Position, "toast.railBoss"));
            }
        }

        // ================================================================== the danger

        /// <summary>The stretch of line each train will cover in the next few seconds, and the crossings not open: rings, avoided ground.</summary>
        private void MarkDangers(double now)
        {
            foreach (var t in _trains)
            {
                var line = Lines[t.Rail];
                float from, to;
                if (t.Run is { } run)
                {
                    from = t.Back;
                    to = t.Front;
                    for (var k = 1; k <= 11; k++)
                    {
                        var f = run.FrontAt(now + 0.5 * k);
                        from = MathF.Min(from, MathF.Max(line.PlayFrom, f - SupportLength));
                        to = MathF.Max(to, f);
                    }
                }
                else
                {
                    if (t.Speed < 0.02f && (t.Vehicle == null || t.Vehicle.Order.Kind == OrderKind.Idle)) continue;
                    var ahead = MathF.Max(WarnFloor, t.Top * (MinWarning + CloseLead));
                    from = t.Dir > 0 ? t.Front : t.Back - ahead;
                    to = t.Dir > 0 ? t.Front + ahead : t.Back;
                }
                from = MathF.Max(line.PlayFrom, from);
                to = MathF.Min(line.PlayTo, to);
                if (to <= from) continue;
                _strips.Add((t.Rail, from, to, now + MinWarning, t.Boss, t.Team));
            }
            // Announced support trains not in yet: the line from the gate in, from 5.5 s before they come.
            foreach (var run in _runs)
            {
                if (run.Inside) continue;
                var line = Lines[run.Rail];
                var front = run.FrontAt(now + MinWarning + CloseLead);
                if (front < line.PlayFrom) continue;
                _strips.Add((run.Rail, line.PlayFrom, MathF.Min(line.PlayTo, front), now + MinWarning, false, run.Team));
            }
            foreach (var (rail, from, to, due, _, _) in _strips)
            {
                var line = Lines[rail];
                for (var s = from; s < to; s += 10f)
                {
                    var e = MathF.Min(to, s + 10f);
                    var a = line.At(s);
                    var b = line.At(e);
                    var pad = RailSpline.BandHalf;
                    _avoid.Add((new Vector2(MathF.Min(a.X, b.X) - pad, MathF.Min(a.Y, b.Y) - pad), new Vector2(MathF.Max(a.X, b.X) + pad, MathF.Max(a.Y, b.Y) + pad)));
                }
                for (var s = from; s <= to + 0.01f; s += 6f) _dangers.Add((line.At(MathF.Min(s, to)), RailSpline.BandHalf + 3f, due));
            }
            foreach (var c in _crossings)
            {
                if (c.State == CrossingState.Open) continue;
                var half = new Vector2(c.Def.Width * 0.5f, c.Def.Depth * 0.5f);
                _avoid.Add((c.Def.Position - half, c.Def.Position + half));
                _dangers.Add((c.Def.Position, c.Def.Half + 3f, now + c.WarnSeconds));
            }
        }

        /// <summary>
        /// The emergency move: every ground vehicle on the line ahead of a train (or on a crossing that is not open) is told to
        /// drive straight off it to its own side, at most once a second; a scripted one (a convoy on its route) is not told.
        /// </summary>
        private void Tell(double now)
        {
            if (_strips.Count == 0 && _crossings.Count == 0) return;
            foreach (var v in _world.VehicleList)
            {
                if (!Movable(v) || v.Scripted || v.Def.Boss || now - v.RailToldAt < TellEvery) continue;
                if (!InDanger(v, out var rail, out var s, out var lateral)) continue;
                var line = Lines[rail];
                var side = lateral >= 0f ? 1f : -1f;
                var exit = line.At(s) + line.Left(s) * side * (RailSpline.BandHalf + v.Radius + 3f);
                if (!_world.Grid.IsWalkable(exit)) exit = line.At(s) - line.Left(s) * side * (RailSpline.BandHalf + v.Radius + 3f);
                if (!_world.Grid.IsWalkable(exit) && !_world.Grid.TryNearestWalkable(exit, 4, out exit)) continue;
                if (!_world.Map.Contains(exit)) continue;
                v.RailToldAt = now;
                _one[0] = v.Id;
                if (_world.Submit(new Command(CommandType.Move, v.Team, _one, exit)).Accepted) Told++;
            }
        }

        private static bool Movable(Vehicle v) =>
            v.IsAlive && !v.OnRail && !v.Flying && !v.Def.Static && v.Def.Naval == null && !v.Burrowed;

        /// <summary>Whether a vehicle stands on a stretch of line in danger or on a crossing that is not open (and where on the line).</summary>
        private bool InDanger(Vehicle v, out int rail, out float s, out float lateral)
        {
            foreach (var (r, from, to, _, _, _) in _strips)
            {
                var line = Lines[r];
                s = line.Project(v.Position, out lateral);
                if (s >= from - v.Radius && s <= to + v.Radius && MathF.Abs(lateral) < RailSpline.BandHalf + v.Radius)
                {
                    rail = r;
                    return true;
                }
            }
            foreach (var c in _crossings)
            {
                if (c.State == CrossingState.Open) continue;
                var line = Lines[c.Rail];
                s = line.Project(v.Position, out lateral);
                if (MathF.Abs(s - c.Def.S) <= c.Def.Half + v.Radius && MathF.Abs(lateral) < RailSpline.BandHalf + v.Radius)
                {
                    rail = c.Rail;
                    return true;
                }
            }
            rail = -1;
            s = 0f;
            lateral = 0f;
            return false;
        }

        // ================================================================== the push

        /// <summary>
        /// Whoever is still in a train's way is put beside the line (a fixed rule: straight out from the line on its own side to
        /// the band's edge and its hull clear, else the other side, else the nearest open ground of the main region off the
        /// band; no physics). A boss train hurts an enemy it rams (once in 2 s) and crushes fixed defences on its line.
        /// </summary>
        private void Push(in Train t, float dt, double now)
        {
            var line = Lines[t.Rail];
            var reach = t.Speed * dt * 2f + 0.5f;
            var back = t.Dir > 0 ? t.Back : t.Back - reach;
            var front = t.Dir > 0 ? t.Front + reach : t.Front;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.OnRail || v.Flying || v.Def.Naval != null || v.Burrowed || v == t.Vehicle) continue;
                var s = line.Project(v.Position, out var lateral);
                if (s < back - v.Radius || s > front + v.Radius || MathF.Abs(lateral) >= t.HalfWidth + v.Radius) continue;
                if (v.Def.Static)
                {
                    if (t.Boss && t.Vehicle is { } crusher && v.Team != t.Team && !v.Invulnerable)
                        _world.Damage.Apply(v, CrushDps * dt * crusher.DamageBoost, DamageType.Kinetic, Hit(crusher));
                    continue;
                }
                if (!PutBeside(v, line, s, lateral)) continue;
                Pushed++;
                if (t.Boss && t.Vehicle is { } ram && v.Team != t.Team && !v.Invulnerable && now - v.RailPushedAt >= 2.0)
                    _world.Damage.Apply(v, RamDamage * ram.DamageBoost, DamageType.Kinetic, Hit(ram));
                v.RailPushedAt = now;
            }
        }

        private static HitInfo Hit(Vehicle train) => new HitInfo(train, train.Team, null, train.Position, HitKind.Strike, false).WithPen(ArmourLevels.MaxUnit, false);

        private bool PutBeside(Vehicle v, RailSpline line, float s, float lateral)
        {
            var side = lateral >= 0f ? 1f : -1f;
            var at = line.At(Math.Clamp(s, 0f, line.Length));
            var left = line.Left(s);
            var out_ = RailSpline.BandHalf + v.Radius + 1f;
            var spot = at + left * side * out_;
            if (!_world.Grid.IsWalkable(spot)) spot = at - left * side * out_;
            if (!_world.Grid.IsWalkable(spot))
            {
                if (!_world.Grid.TryNearestInRegion(at + left * side * out_, _world.Grid.MainRegion, 12, out spot)) return false;
                line.Project(spot, out var off);
                if (MathF.Abs(off) < RailSpline.BandHalf) return false;
            }
            v.Position = spot;
            v.Speed = 0f;
            Vehicle.PathTrace?.Invoke(v, "Put beside the rail by a train");
            if (v.HasPath) _world.PathTo(v, v.PathGoal);
            return true;
        }

        // ================================================================== the routes' side

        /// <summary>
        /// The path costs for a new ground route while the rail is in danger (a crossing warning or closed, the line ahead of a
        /// train): its ground avoided; null: none (the plain search).
        /// </summary>
        internal PathCosts? AvoidFor(Vehicle v)
        {
            if (_avoid.Count == 0 || v.Flying || v.OnRail) return null;
            _costs.Avoid = _avoid;
            _costs.Extra = null;
            _costs.HasBlocker = false;
            _costs.StartSkip = 0f;
            _costs.MaxExpansions = int.MaxValue;
            return _costs;
        }

        /// <summary>No parking on a rail: an order's point on the line (within its band) is moved just off it, to the side the vehicle is on.</summary>
        internal Vector2 OffRail(Vehicle v, Vector2 goal)
        {
            if (Lines.Count == 0 || v.Flying || v.OnRail || v.Def.Naval != null) return goal;
            foreach (var line in Lines)
            {
                var s = line.Project(goal, out var lateral);
                if (s < line.PlayFrom || s > line.PlayTo) continue;
                var band = RailSpline.BandHalf + v.Radius;
                if (MathF.Abs(lateral) >= band) continue;
                // To the side the vehicle is on (it need not cross the line), else the side of the point.
                line.Project(v.Position, out var mine);
                var side = MathF.Abs(mine) > 0.3f ? MathF.Sign(mine) : lateral >= 0f ? 1f : -1f;
                var spot = line.At(s) + line.Left(s) * side * (band + 1f);
                if (!_world.Grid.IsWalkable(spot)) spot = line.At(s) - line.Left(s) * side * (band + 1f);
                if (_world.Grid.IsWalkable(spot) && _world.Map.Contains(spot)) return spot;
            }
            return goal;
        }

        /// <summary>The danger as the AI's warning rings (no side's: every side's squads dodge them).</summary>
        internal void Warnings(List<AI.WarningZone> into)
        {
            foreach (var (centre, radius, due) in _dangers) into.Add(new AI.WarningZone(-1, centre, radius, due, false));
        }

        // ================================================================== the fingerprint

        internal void Mix(Action<long> mix)
        {
            if (Lines.Count == 0) return;
            mix(Told);
            mix(Pushed);
            foreach (var c in _crossings) mix((long)c.State * 1000003L + c.Since);
            foreach (var r in _runs) mix(r.EntryTick * 31 + r.ExitTick);
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.OnRail) mix((long)MathF.Round(v.RailS * 100f) * 3 + v.RailDir + 1);
        }
    }
}
