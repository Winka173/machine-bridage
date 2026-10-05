#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P0-A, spec 47 + 83: "CanUnitClassInfluenceRegion": whether a ground unit can drive to some ground of its own
    /// connected component from which its weapon reaches a target (outside the weapon's minimum reach). Spec 7: "có thể bắn
    /// tới" is not "có thể đi tới": a tank whose ground never comes within reach of a ship on the water, or of a pocket sealed
    /// behind rock, must drop it instead of driving round the map.
    /// <para>
    /// P0 wiring (DECISIONS "AI MASTER P0 wiring + preview wrecks (lane A)"): the answer is P0-B's reachable firing region
    /// (<see cref="Resolver"/>, set by <see cref="SimWorld.TargetAccess"/> to <see cref="EngagementFeasibility.CanFireFromComponent"/>):
    /// the unit's mobility-domain component (a ground unit's leaves out the sea, so a shore gun line is judged from the shore),
    /// the firing band measured as the combat system measures it (distance - target radius &lt;= reach, distance &gt;= minimum).
    /// While the topology lags the grid (it is rebuilt at most every <c>ai.topology.rebuildSeconds</c>), or with no resolver,
    /// the grid's own regions are sampled, so a gate shut this step is seen this step.
    /// </para>
    /// <para>
    /// Cached per (source component, coarse target cell, reach, minimum-reach and radius band). The cache is dropped whenever
    /// the ground changes (<see cref="Navigation.NavGrid.Version"/>: a gate opening or closing, a bridge or wall going down, a
    /// hardpoint built, a scripted terrain state) or the topology is rebuilt: spec 83's invalidation events. Breakable walls
    /// and gates: <see cref="BreachFirst"/> (<see cref="BreachAccess"/>). Deterministic: grid reads only, a fixed order.
    /// </para>
    /// </summary>
    public sealed class TargetAccessCache
    {
        private readonly SimWorld _world;
        private readonly Dictionary<(long, bool, int, int, int, int, int), bool> _cache = new();
        private int _version = int.MinValue;
        private MapTopology? _topology;
        private BreachAccess? _breach;

        /// <summary>Entries kept before the cache is cleared (a bound on memory; it refills on demand).</summary>
        public const int Capacity = 8192;

        /// <summary>Target cells are grouped this many grid cells to a side for the cache key (2 m cells: 8 m).</summary>
        private const int Bucket = 4;

        public TargetAccessCache(SimWorld world) => _world = world;

        /// <summary>
        /// P0-B's reachable firing region: (mobility domain, component of that domain's graph, target point, target radius,
        /// minimum reach, reach) -> whether some cell of the component lies in the firing band. Null: the grid sampling only.
        /// </summary>
        public Func<MobilityDomain, int, Vector2, float, float, float, bool>? Resolver { get; set; }

        /// <summary>Lookups served and region tests run (the measures and tests read them).</summary>
        public int Hits { get; private set; }
        public int Misses { get; private set; }

        /// <summary>Region tests answered by P0-B's firing region (the others by the grid sampling).</summary>
        public int Resolved { get; private set; }

        /// <summary>Breakable walls and gates as passable after a breach (made on first use).</summary>
        public BreachAccess Breach => _breach ??= new BreachAccess(_world);

        /// <summary>
        /// Whether <paramref name="unit"/> (with its main weapon) can get a firing solution on a target at
        /// <paramref name="target"/> (of <paramref name="targetRadius"/>). Aircraft reach everything; a flying target comes to
        /// the unit (and only air-capable weapons are ever pointed at it, by the domain filter); ships and fixed defences answer
        /// by their weapon's reach from where they stand (ships: the naval lane's routes are the boss/naval lane's, so a ship
        /// counts as able to close in).
        /// </summary>
        public bool CanInfluence(Vehicle unit, Vector2 target, bool targetFlying, float targetRadius = 0f)
        {
            if (unit.Flying || targetFlying) return true;
            var weapon = unit.Def.Weapon;
            if (weapon.Damage <= 0f) return false;
            if (unit.Def.Naval != null) return true;
            var reach = Reach(unit);
            if (unit.Def.Static || unit.Def.Speed <= 0f) return Vector2.Distance(unit.Position, target) - targetRadius <= reach;
            var grid = _world.Grid;
            Refresh(grid);
            // P0-B: the unit's mobility-domain component, while the topology matches the grid.
            if (Resolver != null && _topology != null && _topology.GridVersion == grid.Version)
            {
                var domain = MapTopology.DomainOf(unit.Def);
                if (_topology.For(domain) is { } graph)
                {
                    var component = graph.ComponentOfCell(graph.NearestPassableCell(unit.Position, SimTunables.Ai.Topology.NearestRings));
                    if (component > 0)
                        return Reachable(((long)(int)domain << 24) | (uint)component, true, domain, target, targetRadius, reach, weapon.MinRange);
                }
            }
            var region = grid.RegionOf(unit.Position);
            // A unit standing on a closed cell (pushed onto a blocker's edge) is judged from the open ground next to it.
            if (region == 0 && grid.TryNearestWalkable(unit.Position, 3, out var open)) region = grid.RegionOf(open);
            if (region == 0) return true;
            return Reachable(region, false, MobilityDomain.Ground, target, targetRadius, reach, weapon.MinRange);
        }

        /// <summary>The cached grid-region test: some open cell of <paramref name="region"/> within reach (and beyond the minimum).</summary>
        public bool Reachable(int region, Vector2 target, float reach, float minRange)
        {
            Refresh(_world.Grid);
            return Reachable(region, false, MobilityDomain.Ground, target, 0f, reach, minRange);
        }

        /// <summary>
        /// Part B / Part H (P0 wiring): the breakable structure (wall segment, gate, obstacle, destructible prop) a ground unit
        /// must break first to get a firing solution on <paramref name="target"/>, which <see cref="CanInfluence"/> found
        /// sealed off; null when no breach opens a way (truly unreachable) or the unit cannot shoot at ground structures.
        /// </summary>
        public IDamageable? BreachFirst(Vehicle unit, IDamageable target)
        {
            if (unit.Flying || unit.Def.Naval != null || unit.Def.Static || unit.Def.Speed <= 0f) return null;
            var weapon = unit.Def.Weapon;
            if (weapon.Damage <= 0f || !weapon.CanTarget(false)) return null;
            var id = Breach.FirstBlocker(unit, target.Position, target.Radius, Reach(unit), weapon.MinRange);
            if (!id.IsValid || id == target.Id) return null;
            return _world.TryGetTarget(id, out var blocker) && blocker.IsAlive && blocker.Team != unit.Team ? blocker : null;
        }

        private static float Reach(Vehicle unit) =>
            MathF.Max(1f, unit.Def.Weapon.Range * (unit.Deploy == DeployState.Deployed ? unit.RangeFactor : 1f));

        /// <summary>Drops the cache when the ground changed or the topology was rebuilt; picks up the current topology.</summary>
        private void Refresh(NavGrid grid)
        {
            var topology = Resolver != null ? _world.Topology : null;
            if (grid.Version == _version && ReferenceEquals(topology, _topology) && _cache.Count < Capacity) return;
            _cache.Clear();
            _version = grid.Version;
            _topology = topology;
        }

        private bool Reachable(long source, bool resolved, MobilityDomain domain, Vector2 target, float radius, float reach, float minRange)
        {
            var grid = _world.Grid;
            var (cx, cy) = grid.CellOf(target);
            var key = (source, resolved, cx / Bucket, cy / Bucket, (int)(reach / 4f), (int)(minRange / 4f), (int)(radius / 2f));
            if (_cache.TryGetValue(key, out var known))
            {
                Hits++;
                return known;
            }
            Misses++;
            bool result;
            if (resolved)
            {
                Resolved++;
                result = Resolver!(domain, (int)(source & 0xFFFFFF), target, radius, minRange, reach);
            }
            else result = Sample((int)source, target, radius, reach, minRange);
            _cache[key] = result;
            return result;
        }

        /// <summary>
        /// Samples the disc of <paramref name="reach"/> (plus the target's radius) round the target for an open cell of the
        /// region: a lattice of at most about 25 x 25 points first, then (only when that finds none) every cell.
        /// </summary>
        private bool Sample(int region, Vector2 target, float radius, float reach, float minRange)
        {
            var grid = _world.Grid;
            var cell = grid.CellSize;
            var outer = reach + radius;
            var cells = (int)MathF.Ceiling(outer / cell);
            var coarse = Math.Max(1, cells / 12);
            // A coarse lattice first; only when it finds nothing, every cell (a narrow strip of shore, a lane between rocks).
            return Pass(coarse) || (coarse > 1 && Pass(1));

            bool Pass(int stride)
            {
                var (tx, ty) = grid.CellOf(target);
                var reachSq = outer * outer;
                var minSq = minRange * minRange;
                for (var dy = -cells; dy <= cells; dy += stride)
                for (var dx = -cells; dx <= cells; dx += stride)
                {
                    int x = tx + dx, y = ty + dy;
                    if (!grid.InBounds(x, y) || grid.RegionOf(x, y) != region) continue;
                    var d = grid.CellCenter(x, y) - target;
                    var dsq = d.LengthSquared();
                    if (dsq <= reachSq && dsq >= minSq) return true;
                }
                return false;
            }
        }
    }
}
