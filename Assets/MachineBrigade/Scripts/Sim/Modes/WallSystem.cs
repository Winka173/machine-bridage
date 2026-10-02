#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>One logic segment of a wall line as the battle holds it: its entity, its prebuilt ground site, rubble or not.</summary>
    public sealed class WallSegment
    {
        internal WallSegment(WallLine line, int index, WallSegmentDef def, string site)
        {
            Line = line;
            Index = index;
            Def = def;
            Site = site;
        }

        public WallLine Line { get; }
        public int Index { get; }
        public WallSegmentDef Def { get; }

        /// <summary>The NavGrid site that holds its ground ("wall.&lt;team&gt;.&lt;ring&gt;.&lt;index&gt;").</summary>
        public string Site { get; }

        /// <summary>The segment's entity (a static obstacle vehicle); None once it is rubble.</summary>
        public EntityId Entity { get; internal set; }

        /// <summary>Destroyed: its ground is (or turns, at the next tick) open and slow.</summary>
        public bool Rubble { get; internal set; }

        public Vector2 Center => Def.Center;
    }

    /// <summary>A side's wall line in the battle: its map line, its type, its segments, the tower a gun wall carries.</summary>
    public sealed class WallLine
    {
        internal WallLine(int team, WallLineDef def, WallType type, Vector2 hq)
        {
            Team = team;
            Def = def;
            Type = type;
            Hq = hq;
        }

        public int Team { get; }
        public WallLineDef Def { get; }
        public WallType Type { get; }
        public int Ring => Def.Ring;

        /// <summary>The HQ the line guards (its inside is within the line's radius of it).</summary>
        public Vector2 Hq { get; }

        public List<WallSegment> Segments { get; } = new();

        /// <summary>A gun wall's tower (the hardpoint of the small slot it took), null otherwise.</summary>
        public HardpointState? Gun { get; internal set; }

        /// <summary>Whether a point lies behind the line (within its radius of the HQ, Chebyshev).</summary>
        public bool Inside(Vector2 p) => MathF.Max(MathF.Abs(p.X - Hq.X), MathF.Abs(p.Y - Hq.Y)) < Def.Radius - 1f;

        public int Standing
        {
            get
            {
                var n = 0;
                foreach (var s in Segments)
                    if (!s.Rubble) n++;
                return n;
            }
        }
    }

    /// <summary>
    /// Prompt 32 L3 (DECISIONS "Prompt 32 L3 / L7 / L9"): the bases' walls. Built once as a base is set up (before the first
    /// step): each line the loadout gives a type gets its segments (static obstacle entities) on prebuilt NavGrid sites
    /// (prompt 31's <see cref="NavStates"/>: INTACT closes the segment's ground, RUBBLE opens it), after a check that the
    /// whole line keeps the battlefield's anchors joined (else the line is not built: NONE, in <see cref="Problems"/>).
    /// Everything after is event-driven: a segment destroyed asks its site for RUBBLE at the next tick
    /// (<see cref="OnDestroyed"/>, from the damage system); nothing of the walls runs every tick. Rubble slows ground
    /// vehicles by <see cref="WallRules.RubbleSlow"/> (the slow-aura pass, only while there is rubble). A load restores the
    /// rubble (<see cref="Snapshot"/>, <see cref="Restore"/>); a replay switches on the same steps (the sites are in the hash).
    /// </summary>
    public sealed class WallSystem
    {
        public const string Intact = "INTACT", RubbleState = "RUBBLE";

        private readonly SimWorld _world;
        private readonly List<WallLine> _lines = new();
        private readonly Dictionary<EntityId, WallSegment> _byEntity = new();
        private readonly List<(Vector2 min, Vector2 max)> _rubble = new();
        private readonly List<string> _problems = new();

        public WallSystem(SimWorld world) => _world = world;

        public IReadOnlyList<WallLine> Lines => _lines;

        /// <summary>Lines not built and why (a line that would cut the battlefield apart, a missing def).</summary>
        public IReadOnlyList<string> Problems => _problems;

        /// <summary>Ground left as rubble (min, max corners).</summary>
        public IReadOnlyList<(Vector2 min, Vector2 max)> RubbleAreas => _rubble;

        public bool HasRubble => _rubble.Count > 0;

        public IEnumerable<WallLine> LinesOf(int team)
        {
            foreach (var l in _lines)
                if (l.Team == team) yield return l;
        }

        /// <summary>The segment an entity is (null: not a wall).</summary>
        public WallSegment? SegmentOf(EntityId id) => _byEntity.TryGetValue(id, out var s) ? s : null;

        /// <summary>
        /// Builds a side's wall lines from the map's lines and the loadout's types (line ring k takes the loadout's k-1). Only
        /// before the first step. Returns the lines built.
        /// </summary>
        public List<WallLine> Build(int team, IReadOnlyList<WallLineDef> lines, BaseLoadout loadout, Vector2 hq)
        {
            var built = new List<WallLine>();
            if (lines.Count == 0 || _world.NavStates.Locked) return built;
            var rules = _world.Catalog.Base.Walls;
            foreach (var def in lines)
            {
                var type = loadout.WallFor(def.Ring - 1);
                if (rules.Of(type) is not { } kind) continue;
                if (!_world.Catalog.Vehicles.TryGetValue(kind.Def, out var segmentDef))
                {
                    _problems.Add($"team {team} ring {def.Ring}: no def {kind.Def}");
                    continue;
                }
                var segments = new List<WallSegmentDef>();
                foreach (var s in def.Segments)
                    if (!s.Extra || kind.Extra) segments.Add(s);
                if (!KeepsAnchors(segments, kind.Gun))
                {
                    _problems.Add($"team {team} ring {def.Ring}: the line would cut the battlefield apart (NONE)");
                    continue;
                }
                var line = new WallLine(team, def, type, hq);
                for (var i = 0; i < segments.Count; i++)
                {
                    var s = segments[i];
                    var segment = new WallSegment(line, i, s, $"wall.{team}.{def.Ring}.{i}");
                    // Spawned before its ground is closed: on closed ground the spawn would move it to the nearest open cell.
                    var v = _world.SpawnVehicle(segmentDef.Id, team, s.Center, s.Facing);
                    v.Position = s.Center;
                    segment.Entity = v.Id;
                    _byEntity[v.Id] = segment;
                    _world.NavStates.Define(new NavSiteDef(segment.Site, new[]
                    {
                        new NavStateDef(Intact, new[] { new NavBlock(s.Center, s.Width, s.Depth) }),
                        new NavStateDef(RubbleState),
                    }, Intact));
                    line.Segments.Add(segment);
                }
                _lines.Add(line);
                built.Add(line);
            }
            return built;
        }

        /// <summary>The whole line (and a gun wall's tower block) drawn: the rallies and capture points still in one region.</summary>
        private bool KeepsAnchors(List<WallSegmentDef> segments, bool gun)
        {
            var grid = _world.Grid;
            var blocks = new List<NavBlock>();
            foreach (var s in segments)
            {
                blocks.Add(new NavBlock(s.Center, s.Width, s.Depth));
                if (gun && s.Gun) blocks.Add(new NavBlock(s.Center, GunAcross, GunAcross));
            }
            foreach (var b in blocks) grid.Mark(b, +1);
            try
            {
                var region = -1;
                foreach (var a in Anchors())
                {
                    var r = grid.RegionOf(a);
                    if (r == 0 && grid.TryNearestWalkable(a, 5, out var open)) r = grid.RegionOf(open);
                    if (r == 0) continue;
                    if (region < 0) region = r;
                    else if (r != region) return false;
                }
                return true;
            }
            finally
            {
                foreach (var b in blocks) grid.Mark(b, -1);
            }
        }

        /// <summary>A gun wall's small tower's anchored square (0.8 of a small slot's 5 m).</summary>
        internal const float GunAcross = 4f;

        private IEnumerable<Vector2> Anchors()
        {
            foreach (var t in _world.Map.Teams) yield return t.Rally;
            foreach (var p in _world.Map.Points) yield return p.Position;
            foreach (var n in _world.Map.Neutrals) yield return n.At;
        }

        /// <summary>
        /// A segment destroyed (the damage system): its site goes to RUBBLE at the next tick, its ground becomes slow rubble,
        /// and a gun wall's tower standing on it comes down with it.
        /// </summary>
        internal void OnDestroyed(Vehicle v)
        {
            if (!_byEntity.TryGetValue(v.Id, out var segment) || segment.Rubble) return;
            Ruin(segment, true);
            if (segment.Def.Gun && segment.Line.Gun is { } gun && _world.TryGetVehicle(gun.Structure, out var tower) && tower.IsAlive)
                _world.Damage.Apply(tower, 1e7f, DamageType.HighExplosive);
        }

        private void Ruin(WallSegment segment, bool schedule)
        {
            segment.Rubble = true;
            _byEntity.Remove(segment.Entity);
            segment.Entity = EntityId.None;
            if (schedule) _world.NavStates.Schedule(segment.Site, RubbleState, _world.Tick + 1, _world.Tick);
            var s = segment.Def;
            var half = new Vector2(s.Width * 0.5f + 1f, s.Depth * 0.5f + 1f);
            _rubble.Add((s.Center - half, s.Center + half));
            _breachVersion = -1;
        }

        /// <summary>Whether a ground point is on rubble (the slow-aura pass asks, only while there is rubble).</summary>
        public bool InRubble(Vector2 p)
        {
            foreach (var (min, max) in _rubble)
                if (p.X >= min.X && p.X <= max.X && p.Y >= min.Y && p.Y <= max.Y) return true;
            return false;
        }

        /// <summary>
        /// A fortress ring already broken (the weekly fortress): its line starts as rubble, before the first step (the sites
        /// put straight into RUBBLE, the segments removed quietly).
        /// </summary>
        public void RuinRing(int team, int ring)
        {
            var states = new List<(string, string)>();
            foreach (var l in _lines)
            {
                if (l.Team != team || l.Ring != ring) continue;
                foreach (var s in l.Segments)
                {
                    if (s.Rubble) continue;
                    if (_world.TryGetVehicle(s.Entity, out var v)) _world.RemoveQuietly(v);
                    Ruin(s, false);
                    states.Add((s.Site, RubbleState));
                }
            }
            if (states.Count > 0) _world.NavStates.Restore(states);
        }

        // ------------------------------------------------------------------ the breach (Showdown's outerDefenseBreached)

        private long _breachVersion = -1;
        private readonly bool[] _breached = new bool[2];

        /// <summary>
        /// Prompt 32 L7: whether a rubble segment of the side's outer line (ring 1) has opened a route into its base, by the
        /// NavGrid as it stands: the ground before and behind the fallen segment open and in one region. Worked out again only
        /// when the grid changed.
        /// </summary>
        public bool RubbleRoute(int team)
        {
            if (team < 0 || team > 1) return false;
            var grid = _world.Grid;
            if (_breachVersion == grid.Version) return _breached[team];
            _breachVersion = grid.Version;
            _breached[0] = _breached[1] = false;
            foreach (var l in _lines)
            {
                if (l.Ring != 1 || l.Team < 0 || l.Team > 1 || _breached[l.Team]) continue;
                foreach (var s in l.Segments)
                {
                    if (!s.Rubble || _world.NavStates.ActiveOf(s.Site) != RubbleState) continue;
                    var outside = RegionNear(s.Def.Out(3f));
                    var inside = RegionNear(s.Def.Out(-(MathF.Min(s.Def.Width, s.Def.Depth) + 3f)));
                    if (outside > 0 && outside == inside)
                    {
                        _breached[l.Team] = true;
                        break;
                    }
                }
            }
            return _breached[team];
        }

        private int RegionNear(Vector2 p)
        {
            var grid = _world.Grid;
            var r = grid.RegionOf(p);
            if (r == 0 && grid.TryNearestWalkable(p, 2, out var open)) r = grid.RegionOf(open);
            return r;
        }

        // ------------------------------------------------------------------ loads

        /// <summary>The segments that are rubble (their sites), in line order: what a load needs.</summary>
        public IReadOnlyList<string> Snapshot()
        {
            var list = new List<string>();
            foreach (var l in _lines)
                foreach (var s in l.Segments)
                    if (s.Rubble) list.Add(s.Site);
            return list;
        }

        /// <summary>A load: each named segment back to rubble (entity removed quietly, its site straight to RUBBLE).</summary>
        public void Restore(IReadOnlyList<string> rubble)
        {
            var wanted = new HashSet<string>(rubble, StringComparer.Ordinal);
            var states = new List<(string, string)>();
            foreach (var l in _lines)
                foreach (var s in l.Segments)
                {
                    if (s.Rubble || !wanted.Contains(s.Site)) continue;
                    if (_world.TryGetVehicle(s.Entity, out var v)) _world.RemoveQuietly(v);
                    Ruin(s, false);
                    states.Add((s.Site, RubbleState));
                }
            if (states.Count > 0) _world.NavStates.Restore(states);
        }
    }
}
