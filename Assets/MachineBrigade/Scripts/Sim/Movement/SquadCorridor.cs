#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// AI MASTER spec 28-29 phase 1: one squad's shared route to its goal, planned once (a costed A* that goes round
    /// parked hulls, wrecks, jams and friendly boss corridors) and followed by every member: each joins it at the furthest
    /// point it can see among the first few, drives its middle, and leaves it at the last point that sees its formation slot.
    /// Local avoidance (ORCA-lite, the traffic rules) does the rest.
    /// </summary>
    public sealed class SquadCorridor
    {
        public int Id { get; internal set; }
        public int Team { get; internal set; }
        public int Owner { get; internal set; }
        public Vector2 From { get; internal set; }
        public Vector2 To { get; internal set; }
        public double BuiltAt { get; internal set; }
        public double UsedAt { get; internal set; }
        public bool Dirty { get; internal set; }

        /// <summary>The way (the start first, the goal last).</summary>
        public IReadOnlyList<Vector2> Points => PointList;

        internal readonly List<Vector2> PointList = new();

        public float Length
        {
            get
            {
                var length = 0f;
                for (var i = 1; i < PointList.Count; i++) length += Vector2.Distance(PointList[i - 1], PointList[i]);
                return length;
            }
        }

        /// <summary>Whether the way passes within <paramref name="radius"/> of <paramref name="p"/>.</summary>
        public bool Passes(Vector2 p, float radius)
        {
            for (var i = 1; i < PointList.Count; i++)
            {
                var a = PointList[i - 1];
                var ab = PointList[i] - a;
                var l = ab.LengthSquared();
                var t = l > 1e-6f ? Math.Clamp(Vector2.Dot(p - a, ab) / l, 0f, 1f) : 0f;
                if (Vector2.DistanceSquared(p, a + ab * t) <= radius * radius) return true;
            }
            return false;
        }
    }

    /// <summary>The shared squad corridors of a battle (spec 28-29): cached per owner, planned again when stale or dirty.</summary>
    public sealed class SquadCorridors
    {
        private readonly SimWorld _world;
        private readonly List<SquadCorridor> _list = new();
        private readonly PathFinder _finder;
        private readonly PathCosts _costs = new();
        private readonly List<Vector2> _buffer = new();
        private readonly List<(Vector2 min, Vector2 max)> _avoid = new();
        private int _nextId;
        private int _builtThisStep;

        /// <summary>Corridors planned per step at most (the rest of the squads use plain orders that step).</summary>
        private const int BuildsPerStep = 2;

        internal SquadCorridors(SimWorld world)
        {
            _world = world;
            _finder = new PathFinder(world.Grid);
        }

        public IReadOnlyList<SquadCorridor> All => _list;

        public SquadCorridor? ById(int id)
        {
            foreach (var c in _list)
                if (c.Id == id) return c;
            return null;
        }

        internal void Step()
        {
            _builtThisStep = 0;
            if (_world.Tick % global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.StepTickMod != global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.StepTickIs) return;
            // Corridors no squad asked for in 30 s are dropped.
            _list.RemoveAll(c => _world.Time - c.UsedAt > global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.StepTimeMin);
        }

        /// <summary>A wreck fell, a jam was stamped, a passage overloaded: corridors through there are planned again.</summary>
        public void MarkDirtyNear(int team, Vector2 at, float radius)
        {
            foreach (var c in _list)
                if ((team < 0 || c.Team == team) && c.Passes(at, radius)) c.Dirty = true;
        }

        /// <summary>
        /// The corridor of <paramref name="owner"/> from <paramref name="from"/> to <paramref name="to"/>: the cached one while
        /// its goal is within 10 m, it is younger than <c>ai.traffic.corridorRefreshS</c> and not dirty; else planned again
        /// (budget allowing; null: plain orders this time). <paramref name="avoid"/>: a passage to go round when the way round
        /// is under <c>ai.navigation.corridorAltMax</c> times the way through (spec 188's alternative route).
        /// </summary>
        public SquadCorridor? Get(int team, int owner, Vector2 from, Vector2 to, Passage? avoid = null)
        {
            if (!SimTunables.Ai.Traffic.Enabled) return null;
            var now = _world.Time;
            SquadCorridor? mine = null;
            foreach (var c in _list)
                if (c.Owner == owner && c.Team == team)
                {
                    mine = c;
                    break;
                }
            if (mine != null && avoid == null && !mine.Dirty && Vector2.Distance(mine.To, to) < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.GetDistanceMax &&
                now - mine.BuiltAt < SimTunables.Ai.Traffic.CorridorRefreshS && Vector2.Distance(mine.From, from) < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.GetDistanceMax2)
            {
                mine.UsedAt = now;
                _world.Traffic.Stats.CorridorsReused++;
                return mine;
            }
            if (_builtThisStep >= BuildsPerStep) return mine != null && !mine.Dirty && Vector2.Distance(mine.To, to) < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.GetDistanceMax ? mine : null;
            _builtThisStep++;
            if (!Plan(team, from, to, null)) return null;
            if (avoid != null)
            {
                var through = PathLength(from, _buffer);
                var plain = new List<Vector2>(_buffer);
                _avoid.Clear();
                var half = new Vector2(avoid.Reach);
                _avoid.Add((avoid.Centre - half, avoid.Centre + half));
                if (Plan(team, from, to, _avoid) && PathLength(from, _buffer) <= through * SimTunables.Ai.Navigation.CorridorAltMax)
                    _world.Traffic.Stats.CorridorAlternatives++;
                else
                {
                    _buffer.Clear();
                    _buffer.AddRange(plain);
                }
            }
            if (mine == null)
            {
                mine = new SquadCorridor { Id = ++_nextId, Team = team, Owner = owner };
                _list.Add(mine);
            }
            mine.From = from;
            mine.To = to;
            mine.BuiltAt = now;
            mine.UsedAt = now;
            mine.Dirty = false;
            mine.PointList.Clear();
            mine.PointList.Add(from);
            mine.PointList.AddRange(_buffer);
            _world.Traffic.Stats.CorridorsBuilt++;
            return mine;
        }

        private bool Plan(int team, Vector2 from, Vector2 to, List<(Vector2 min, Vector2 max)>? avoid)
        {
            _costs.Extra = _world.Movement.CostLayer(team);
            _costs.Start = from;
            _costs.StartSkip = 4f;
            _costs.HasBlocker = false;
            _costs.Avoid = avoid;
            _costs.AvoidCost = 250;
            _costs.MaxExpansions = Math.Max(global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.PlanCorridorNodesFloor, SimTunables.Ai.Traffic.CorridorNodes);
            return _finder.TryFindPath(from, to, _buffer, _costs) && _buffer.Count > 0;
        }

        private static float PathLength(Vector2 from, List<Vector2> path)
        {
            var length = 0f;
            var a = from;
            foreach (var b in path)
            {
                length += Vector2.Distance(a, b);
                a = b;
            }
            return length;
        }

        /// <summary>
        /// A member's route along the corridor: join at the furthest of the first few corridor points it can see (from the
        /// one nearest it), follow the middle, leave at the last point that sees <paramref name="slot"/>. False when it cannot
        /// see the corridor or the slot cannot be seen from it (the caller plans its own route).
        /// </summary>
        public bool Compose(SquadCorridor c, Vector2 from, Vector2 slot, List<Vector2> into)
        {
            into.Clear();
            var points = c.PointList;
            if (points.Count < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.ComposeCountMax) return false;
            var grid = _world.Grid;
            var nearest = 0;
            var best = float.MaxValue;
            for (var i = 0; i < points.Count; i++)
            {
                var d = Vector2.DistanceSquared(points[i], from);
                if (d >= best) continue;
                best = d;
                nearest = i;
            }
            var join = -1;
            for (var i = Math.Min(points.Count - 1, nearest + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.ComposeNearestAdd); i >= nearest; i--)
                if (grid.LineOfSight(from, points[i]))
                {
                    join = i;
                    break;
                }
            if (join < 0) return false;
            // (The corridor's own end is the squad's goal: a member bound for a slot beside it leaves the way before it.)
            var last = Vector2.DistanceSquared(points[points.Count - 1], slot) < 1f ? points.Count - 1 : points.Count - global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.ComposeCountSub;
            if (join > last)
            {
                if (!grid.LineOfSight(from, slot)) return false;
                into.Add(slot);
                c.UsedAt = _world.Time;
                return true;
            }
            var leave = -1;
            for (var i = last; i >= Math.Max(join, last - global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.ComposeLastSub); i--)
                if (grid.LineOfSight(points[i], slot))
                {
                    leave = i;
                    break;
                }
            if (leave < 0) return false;
            for (var i = join; i <= leave; i++)
                if (Vector2.DistanceSquared(points[i], from) > 1f || i > join) into.Add(points[i]);
            if (into.Count == 0 || Vector2.DistanceSquared(into[into.Count - 1], slot) > global::MachineBrigade.Sim.Content.SimTunables.Vehicles.SquadCorridors.ComposeDistanceSquaredMin) into.Add(slot);
            c.UsedAt = _world.Time;
            return true;
        }
    }
}
