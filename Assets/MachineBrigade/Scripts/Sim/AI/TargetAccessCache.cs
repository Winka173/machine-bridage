#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P0-A, spec 47 + 83: "CanUnitClassInfluenceRegion": whether a ground unit can drive to some open ground of its
    /// own connected region (NavGrid.RegionOf) from which its weapon reaches a target point (outside the weapon's minimum
    /// reach). Spec 7: "có thể bắn tới" is not "có thể đi tới": a tank whose region never comes within reach of a ship on the
    /// water, or of a pocket sealed behind a shut gate, must drop it instead of driving round the map.
    /// <para>
    /// Cached per (unit region, coarse target cell, reach and minimum-reach band). The cache is dropped whenever the ground
    /// changes (<see cref="Navigation.NavGrid.Version"/>: a gate opening or closing, a bridge or wall going down, a hardpoint
    /// built, a wreck blocking a narrow way, a scripted terrain state), which are spec 83's invalidation events.
    /// </para>
    /// <para>
    /// Coordination (lane P0-B builds MapTopology / EngagementFeasibility / the reachable firing region): <see cref="Resolver"/>
    /// lets that layer answer instead; this class keeps the cache and the domain rules (aircraft, ships, fixed defences).
    /// Deterministic: grid reads only, a fixed sampling order, no randomness.
    /// </para>
    /// </summary>
    public sealed class TargetAccessCache
    {
        private readonly SimWorld _world;
        private readonly Dictionary<long, bool> _cache = new();
        private int _version = int.MinValue;

        /// <summary>Entries kept before the cache is cleared (a bound on memory; it refills on demand).</summary>
        public const int Capacity = 8192;

        /// <summary>Target cells are grouped this many grid cells to a side for the cache key (2 m cells: 8 m).</summary>
        private const int Bucket = 4;

        public TargetAccessCache(SimWorld world) => _world = world;

        /// <summary>
        /// Optional replacement of the region test (lane P0-B's reachable firing region): (unit region, target point, reach,
        /// minimum reach) -> whether some open cell of the region lies within reach. Null: this class's own grid sampling.
        /// </summary>
        public Func<int, Vector2, float, float, bool>? Resolver { get; set; }

        /// <summary>Lookups served and region tests run (the measures and tests read them).</summary>
        public int Hits { get; private set; }
        public int Misses { get; private set; }

        /// <summary>
        /// Whether <paramref name="unit"/> (with its main weapon) can get a firing solution on a target at
        /// <paramref name="target"/>. Aircraft reach everything; a flying target comes to the unit (and only air-capable
        /// weapons are ever pointed at it, by the domain filter); ships and fixed defences answer by their weapon's reach from
        /// where they stand (ships: the naval lane's routes are the boss/naval lane's, so a ship counts as able to close in).
        /// </summary>
        public bool CanInfluence(Vehicle unit, Vector2 target, bool targetFlying)
        {
            if (unit.Flying || targetFlying) return true;
            var weapon = unit.Def.Weapon;
            if (weapon.Damage <= 0f) return false;
            if (unit.Def.Naval != null) return true;
            var reach = MathF.Max(1f, weapon.Range * (unit.Deploy == DeployState.Deployed ? unit.RangeFactor : 1f));
            if (unit.Def.Static || unit.Def.Speed <= 0f) return Vector2.Distance(unit.Position, target) <= reach;
            var grid = _world.Grid;
            var region = grid.RegionOf(unit.Position);
            // A unit standing on a closed cell (pushed onto a blocker's edge) is judged from the open ground next to it.
            if (region == 0 && grid.TryNearestWalkable(unit.Position, 3, out var open)) region = grid.RegionOf(open);
            if (region == 0) return true;
            return Reachable(region, target, reach, weapon.MinRange);
        }

        /// <summary>The cached region test: some open cell of <paramref name="region"/> within reach (and beyond the minimum).</summary>
        public bool Reachable(int region, Vector2 target, float reach, float minRange)
        {
            var grid = _world.Grid;
            if (grid.Version != _version || _cache.Count >= Capacity)
            {
                _cache.Clear();
                _version = grid.Version;
            }
            var (cx, cy) = grid.CellOf(target);
            var key = ((long)region << 40) ^ ((long)(cx / Bucket & 0xFFF) << 28) ^ ((long)(cy / Bucket & 0xFFF) << 16) ^
                      ((long)((int)(reach / 4f) & 0xFF) << 8) ^ ((int)(minRange / 4f) & 0xFF);
            if (_cache.TryGetValue(key, out var known))
            {
                Hits++;
                return known;
            }
            Misses++;
            var result = Resolver?.Invoke(region, target, reach, minRange) ?? Sample(region, target, reach, minRange);
            _cache[key] = result;
            return result;
        }

        /// <summary>
        /// Samples the disc of <paramref name="reach"/> round the target for an open cell of the region: a lattice of at most
        /// about 25 x 25 points first, then (only when that finds none) every cell.
        /// </summary>
        private bool Sample(int region, Vector2 target, float reach, float minRange)
        {
            var grid = _world.Grid;
            var cell = grid.CellSize;
            var cells = (int)MathF.Ceiling(reach / cell);
            var coarse = Math.Max(1, cells / 12);
            // A coarse lattice first; only when it finds nothing, every cell (a narrow strip of shore, a lane between rocks).
            return Pass(coarse) || (coarse > 1 && Pass(1));

            bool Pass(int stride)
            {
                var (tx, ty) = grid.CellOf(target);
                var reachSq = reach * reach;
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
