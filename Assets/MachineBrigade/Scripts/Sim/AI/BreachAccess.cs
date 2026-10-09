#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P0 wiring (DECISIONS "AI MASTER P0 wiring + preview wrecks (lane A)"): breakable walls and gates count as
    /// passable after a breach (Part B breacher / siege doctrine, Part H objective-aware priority). A target sealed off from a
    /// unit's open ground only by structures the unit's side can shoot down (a base's wall segments, an enemy wall, gate or
    /// obstacle, a destructible prop such as a fortress gate) is not "unreachable": the unit breaks the first of them on the
    /// cheapest way in. Only a target no breach opens (a sealed pocket, cliffs, the sea for a ground unit) is truly unreachable.
    /// <para>
    /// A grid cell is breach-passable for a side when every blocker closing it (<see cref="NavGrid.BlockersAt"/>) is one of the
    /// breakable structures of its enemies (or neutral), counted on the same cells as the grid closes them. Per side and
    /// mobility (ground units keep off the sea) the breach-passable cells are flood-labelled once per grid version (a cheap
    /// "can a breach open it at all"); the way in is a Dijkstra over the cells, an open cell costing 1 and a breakable one
    /// 1 + <see cref="BreachCellCost"/>, from the unit to the first cell of the target's firing band; the structure owning the
    /// first breakable cell on that way is the one to break. Results are cached per (side, unit cell, target cell, bands) and
    /// dropped when the grid changes. Map knowledge only (walls and props are drawn on the map; enemy obstacles are static and
    /// stay known once seen), the order and cost are fixed: deterministic, fog-fair.
    /// </para>
    /// </summary>
    public sealed class BreachAccess
    {
        /// <summary>Extra cost of crossing one breakable cell (in open cells): a long way round is taken before a short breach.</summary>
        public static int BreachCellCost => global::MachineBrigade.Sim.Content.SimTunables.Ai.BreachAccess.BreachCellCost;

        /// <summary>Unit and target cells are grouped this many grid cells to a side for the cache key (2 m cells: 8 m).</summary>
        private const int Bucket = 4;

        /// <summary>Cached answers kept before the cache is cleared.</summary>
        public const int Capacity = 4096;

        private readonly SimWorld _world;
        private readonly Dictionary<int, Layer> _layers = new();
        private readonly Dictionary<(int, bool, int, int, int, int, int, int), EntityId> _cache = new();
        private int _version = int.MinValue;
        private int[] _cost = Array.Empty<int>();
        private int[] _prev = Array.Empty<int>();
        private int[] _stamp = Array.Empty<int>();
        private int _stampNow;
        private readonly List<long> _heap = new();

        public BreachAccess(SimWorld world) => _world = world;

        /// <summary>Way-in searches run (cache misses past the label check); the tests and the performance report read it.</summary>
        public int Searches { get; private set; }

        /// <summary>One side's breakable structures on the grid, and its breach-passable components.</summary>
        private sealed class Layer
        {
            public Layer(int n)
            {
                Count = new int[n];
                Owner = new int[n];
                Label = new int[n];
            }

            /// <summary>Per cell: breakable structures closing it (as the grid counts its blockers).</summary>
            public readonly int[] Count;

            /// <summary>Per cell: 1 + the index in <see cref="Ids"/> of a structure closing it (0: none).</summary>
            public readonly int[] Owner;

            /// <summary>Per cell: its breach-passable component (0: closed for good).</summary>
            public readonly int[] Label;

            public readonly List<EntityId> Ids = new();
        }

        /// <summary>
        /// The breakable structure <paramref name="unit"/> should attack first to get a firing position on a target at
        /// <paramref name="target"/> (radius <paramref name="radius"/>) for a weapon of <paramref name="reach"/> and
        /// <paramref name="minRange"/>; <see cref="EntityId.None"/> when no breach opens a way (or none is needed).
        /// </summary>
        public EntityId FirstBlocker(Vehicle unit, Vector2 target, float radius, float reach, float minRange)
        {
            var grid = _world.Grid;
            Refresh(grid);
            var (sx, sy) = grid.CellOf(unit.Position);
            if (!grid.IsWalkable(sx, sy))
            {
                if (!grid.TryNearestWalkable(unit.Position, global::MachineBrigade.Sim.Content.SimTunables.Ai.BreachAccess.FirstBlockerMaxRings, out var open)) return EntityId.None;
                (sx, sy) = grid.CellOf(open);
            }
            var amphibious = TerrainRules.Wades(unit.Def);
            var layer = LayerOf(unit.Team, amphibious);
            var start = grid.Index(sx, sy);
            var label = layer.Label[start];
            if (label == 0) return EntityId.None;
            var (tx, ty) = grid.CellOf(target);
            var key = (unit.Team, amphibious, sx / Bucket, sy / Bucket, tx / Bucket, ty / Bucket, (int)(reach / global::MachineBrigade.Sim.Content.SimTunables.Ai.BreachAccess.FirstBlockerReachDivisor), ((int)(minRange / global::MachineBrigade.Sim.Content.SimTunables.Ai.BreachAccess.FirstBlockerMinRangeDivisor) << 8) | (int)(radius / global::MachineBrigade.Sim.Content.SimTunables.Ai.BreachAccess.FirstBlockerRadiusDivisor));
            if (_cache.TryGetValue(key, out var known)) return known;
            if (_cache.Count >= Capacity) _cache.Clear();
            var result = InBand(grid, layer, label, target, radius, reach, minRange)
                ? Search(grid, layer, start, target, radius, reach, minRange)
                : EntityId.None;
            _cache[key] = result;
            return result;
        }

        /// <summary>Whether a cell (a grid index) is closed only by structures <paramref name="team"/>'s enemies can break.</summary>
        public bool Breakable(int team, int cell, bool amphibious = false)
        {
            var grid = _world.Grid;
            Refresh(grid);
            var blockers = grid.BlockersAt(cell);
            return blockers > 0 && LayerOf(team, amphibious).Count[cell] == blockers;
        }

        private void Refresh(NavGrid grid)
        {
            if (grid.Version == _version) return;
            _version = grid.Version;
            _layers.Clear();
            _cache.Clear();
        }

        private Layer LayerOf(int team, bool amphibious)
        {
            var id = team * 2 + (amphibious ? 1 : 0);
            if (_layers.TryGetValue(id, out var layer)) return layer;
            layer = Build(team, amphibious);
            _layers[id] = layer;
            return layer;
        }

        /// <summary>Whether a breakable structure can be brought down by a side at all (alive, not shielded, targetable).</summary>
        internal static bool CanBreak(Vehicle w) => w.IsAlive && !w.Invulnerable && !w.Def.Untargetable && !w.Truce;

        private Layer Build(int team, bool amphibious)
        {
            var grid = _world.Grid;
            var n = grid.Width * grid.Height;
            var layer = new Layer(n);
            var clearance = SimWorld.ObstacleClearance;
            // A base's wall segments: their prebuilt site's block while intact (WallSystem.Build).
            if (_world.HasWalls)
                foreach (var line in _world.Walls.Lines)
                {
                    if (line.Team == team) continue;
                    foreach (var seg in line.Segments)
                    {
                        if (seg.Rubble || !_world.TryGetVehicle(seg.Entity, out var wall) || !CanBreak(wall)) continue;
                        Mark(grid, layer, wall.Id, seg.Def.Center, seg.Def.Width + global::MachineBrigade.Sim.Content.SimTunables.Ai.BreachAccess.BuildClearanceScale * clearance, seg.Def.Depth + global::MachineBrigade.Sim.Content.SimTunables.Ai.BreachAccess.BuildClearanceScale * clearance);
                    }
                }
            // Enemy walls, gates and obstacles standing on their ground like buildings (SimWorld.AnchorDefence).
            foreach (var v in _world.VehicleList)
            {
                if (!v.BlocksRoutes || v.Team == team || !CombatSystem.IsBlockingStructure(v) || !CanBreak(v)) continue;
                var f = SimWorld.StaticFootprint(v.Def) + 2f * clearance;
                Mark(grid, layer, v.Id, v.Position, f, f);
            }
            // Destructible props that block the way (a fortress's gate and walls, a building).
            foreach (var prop in _world.Props)
            {
                if (!prop.IsAlive || !prop.Def.BlocksMovement || prop.Def.Indestructible || prop.Invulnerable) continue;
                Mark(grid, layer, prop.Id, prop.Position, prop.Width + global::MachineBrigade.Sim.Content.SimTunables.Ai.BreachAccess.BuildClearanceScale * clearance, prop.Depth + global::MachineBrigade.Sim.Content.SimTunables.Ai.BreachAccess.BuildClearanceScale * clearance);
            }
            // Components of the breach-passable cells (four-neighbour, as the route search moves).
            var sea = amphibious ? null : SeaCells(n);
            var queue = new int[n];
            var next = 0;
            for (var s = 0; s < n; s++)
            {
                if (layer.Label[s] != 0 || !Passable(grid, layer, sea, s)) continue;
                next++;
                layer.Label[s] = next;
                int head = 0, tail = 0;
                queue[tail++] = s;
                while (head < tail)
                {
                    var i = queue[head++];
                    int x = i % grid.Width, y = i / grid.Width;
                    if (x + 1 < grid.Width) Fill(i + 1);
                    if (x > 0) Fill(i - 1);
                    if (y + 1 < grid.Height) Fill(i + grid.Width);
                    if (y > 0) Fill(i - grid.Width);
                }

                void Fill(int j)
                {
                    if (layer.Label[j] != 0 || !Passable(grid, layer, sea, j)) return;
                    layer.Label[j] = next;
                    queue[tail++] = j;
                }
            }
            return layer;
        }

        /// <summary>The topology's sea cells when it matches the grid (ground units do not drive over the water); else none.</summary>
        private bool[]? SeaCells(int n)
        {
            if (_world.Map.Sea == null) return null;
            var topo = _world.Topology;
            return topo.HasSea && topo.Sea.Length == n ? topo.Sea : null;
        }

        private static bool Passable(NavGrid grid, Layer layer, bool[]? sea, int i)
        {
            if (sea != null && sea[i]) return false;
            var blockers = grid.BlockersAt(i);
            return blockers == 0 || layer.Count[i] == blockers;
        }

        /// <summary>Counts a structure's closed rectangle on the cells the grid closes for it (NavGrid.ChangeRect's cells).</summary>
        private static void Mark(NavGrid grid, Layer layer, EntityId id, Vector2 centre, float width, float depth)
        {
            layer.Ids.Add(id);
            var owner = layer.Ids.Count;
            var half = new Vector2(width * 0.5f, depth * 0.5f);
            var (minX, minY) = grid.CellOf(centre - half);
            var (maxX, maxY) = grid.CellOf(centre + half - new Vector2(1e-4f));
            for (var y = Math.Max(0, minY); y <= Math.Min(grid.Height - 1, maxY); y++)
            for (var x = Math.Max(0, minX); x <= Math.Min(grid.Width - 1, maxX); x++)
            {
                var i = grid.Index(x, y);
                layer.Count[i]++;
                if (layer.Owner[i] == 0) layer.Owner[i] = owner;
            }
        }

        /// <summary>Some cell of the unit's breach-passable component lies in the target's firing band.</summary>
        private static bool InBand(NavGrid grid, Layer layer, int label, Vector2 target, float radius, float reach, float minRange)
        {
            var outer = reach + radius;
            var cells = (int)MathF.Ceiling(outer / grid.CellSize);
            var (tx, ty) = grid.CellOf(target);
            var outerSq = outer * outer;
            var minSq = minRange * minRange;
            for (var dy = -cells; dy <= cells; dy++)
            for (var dx = -cells; dx <= cells; dx++)
            {
                int x = tx + dx, y = ty + dy;
                if (!grid.InBounds(x, y) || layer.Label[grid.Index(x, y)] != label) continue;
                var dsq = Vector2.DistanceSquared(grid.CellCenter(x, y), target);
                if (dsq <= outerSq && dsq >= minSq) return true;
            }
            return false;
        }

        /// <summary>The cheapest way from <paramref name="start"/> into the firing band; the owner of its first breakable cell.</summary>
        private EntityId Search(NavGrid grid, Layer layer, int start, Vector2 target, float radius, float reach, float minRange)
        {
            Searches++;
            var n = grid.Width * grid.Height;
            if (_cost.Length != n)
            {
                _cost = new int[n];
                _prev = new int[n];
                _stamp = new int[n];
                _stampNow = 0;
            }
            if (++_stampNow == int.MaxValue)
            {
                Array.Clear(_stamp, 0, n);
                _stampNow = 1;
            }
            var label = layer.Label[start];
            var outerSq = (reach + radius) * (reach + radius);
            var minSq = minRange * minRange;
            _heap.Clear();
            _stamp[start] = _stampNow;
            _cost[start] = 0;
            _prev[start] = -1;
            Push(start, 0);
            var found = -1;
            while (_heap.Count > 0)
            {
                var top = Pop();
                var i = (int)(top & 0xFFFFFFFF);
                var c = (int)(top >> 32);
                if (_cost[i] != c) continue;
                int x = i % grid.Width, y = i / grid.Width;
                var dsq = Vector2.DistanceSquared(grid.CellCenter(x, y), target);
                if (dsq <= outerSq && dsq >= minSq)
                {
                    found = i;
                    break;
                }
                if (x + 1 < grid.Width) Relax(i + 1);
                if (x > 0) Relax(i - 1);
                if (y + 1 < grid.Height) Relax(i + grid.Width);
                if (y > 0) Relax(i - grid.Width);

                void Relax(int j)
                {
                    if (layer.Label[j] != label) return;
                    var next = c + 1 + (grid.BlockersAt(j) > 0 ? BreachCellCost : 0);
                    if (_stamp[j] == _stampNow && _cost[j] <= next) return;
                    _stamp[j] = _stampNow;
                    _cost[j] = next;
                    _prev[j] = i;
                    Push(j, next);
                }
            }
            if (found < 0) return EntityId.None;
            // Back from the firing cell: the breakable cell nearest the unit is the first to break.
            var first = -1;
            for (var k = found; k >= 0; k = _prev[k])
                if (grid.BlockersAt(k) > 0) first = k;
            if (first < 0) return EntityId.None;
            var owner = layer.Owner[first];
            return owner > 0 ? layer.Ids[owner - 1] : EntityId.None;
        }

        // A binary min-heap of (cost << 32 | cell): ties broken by the cell index, so the search is the same on every machine.
        private void Push(int cell, int cost)
        {
            var item = ((long)cost << 32) | (uint)cell;
            _heap.Add(item);
            var k = _heap.Count - 1;
            while (k > 0)
            {
                var parent = (k - 1) >> 1;
                if (_heap[parent] <= item) break;
                _heap[k] = _heap[parent];
                k = parent;
            }
            _heap[k] = item;
        }

        private long Pop()
        {
            var top = _heap[0];
            var last = _heap[_heap.Count - 1];
            _heap.RemoveAt(_heap.Count - 1);
            var count = _heap.Count;
            if (count == 0) return top;
            var k = 0;
            while (true)
            {
                var child = 2 * k + 1;
                if (child >= count) break;
                if (child + 1 < count && _heap[child + 1] < _heap[child]) child++;
                if (_heap[child] >= last) break;
                _heap[k] = _heap[child];
                k = child;
            }
            _heap[k] = last;
            return top;
        }
    }
}
