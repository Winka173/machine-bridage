#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// Parked hulls as path costs, one layer per side (a friend parked in the road is a smaller
    /// matter than an enemy): each standing ground vehicle stamps its hull dear and a ring round
    /// it cheaper. A route planned on it goes round parked vehicles where there is room and
    /// through them only where there is not (the "park stamp" of Planetary Annihilation, the
    /// occupancy grid of the PurpleWave bot). Moving hulls are left out: they flow with the
    /// traffic. Only routes planned after a vehicle got stuck pay these costs.
    /// </summary>
    public sealed class UnitCostField
    {
        /// <summary>Layers for sides 0, 1 and the hostile side (2); any other side uses the last.</summary>
        public const int Layers = 3;

        /// <summary>Below this speed a vehicle counts as parked.</summary>
        public static float ParkedSpeed => global::MachineBrigade.Sim.Content.SimTunables.Maps.UnitCostField.ParkedSpeed;

        /// <summary>Step multipliers x5, x9, x26 and x2 at the path finder's 0.1 scale.</summary>
        public const byte FriendParkedCost = 40, EnemyParkedCost = 80, StunnedCost = 250, RingCost = 10;

        /// <summary>The ring reaches this far past the hull (metres).</summary>
        private static float RingReach => global::MachineBrigade.Sim.Content.SimTunables.Maps.UnitCostField.RingReach;

        /// <summary>A refresh is good for this many steps (half a second at 20 Hz).</summary>
        private static int RefreshTicks => global::MachineBrigade.Sim.Content.SimTunables.Maps.UnitCostField.RefreshTicks;

        private readonly NavGrid _grid;
        private readonly byte[][] _cost;
        private long _refreshedAt = -RefreshTicks;

        public UnitCostField(NavGrid grid)
        {
            _grid = grid;
            _cost = new byte[Layers][];
            for (var i = 0; i < Layers; i++) _cost[i] = new byte[grid.Width * grid.Height];
        }

        /// <summary>The costs a vehicle of <paramref name="team"/> pays.</summary>
        public byte[] For(int team) => _cost[team >= 0 && team < Layers ? team : Layers - 1];

        /// <summary>Refreshes the layers if the last refresh is older than half a second (on demand, at most once a step).</summary>
        internal void RefreshIfStale(SimWorld world)
        {
            if (world.Tick - _refreshedAt < RefreshTicks) return;
            Refresh(world);
        }

        /// <summary>Stamps every parked ground hull (stamping is order independent: each cell keeps its dearest stamp).</summary>
        internal void Refresh(SimWorld world)
        {
            _refreshedAt = world.Tick;
            foreach (var layer in _cost) Array.Clear(layer, 0, layer.Length);
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Flying || v.BlocksRoutes) continue;
                if (!v.Def.Static && v.HasPath && MathF.Abs(v.Speed) > ParkedSpeed) continue;
                // A hull knocked out (stunned) cannot make way at all: as good as a wall for a while.
                for (var team = 0; team < Layers; team++)
                    Stamp(_cost[team], v, v.Stunned ? StunnedCost : team == v.Team ? FriendParkedCost : EnemyParkedCost);
            }
        }

        private void Stamp(byte[] layer, Vehicle v, byte core)
        {
            var half = SimMath.Forward(v.Heading) * v.Def.HullHalf;
            var a = v.Position - half;
            var b = v.Position + half;
            var inner = v.Def.HullRadius + 0.5f;
            var outer = inner + RingReach;
            var min = Vector2.Min(a, b) - new Vector2(outer);
            var max = Vector2.Max(a, b) + new Vector2(outer);
            var (x0, y0) = _grid.CellOf(min);
            var (x1, y1) = _grid.CellOf(max);
            var ab = b - a;
            var length = ab.LengthSquared();
            for (var y = Math.Max(0, y0); y <= Math.Min(_grid.Height - 1, y1); y++)
            for (var x = Math.Max(0, x0); x <= Math.Min(_grid.Width - 1, x1); x++)
            {
                var c = _grid.CellCenter(x, y);
                var t = length > 1e-6f ? Math.Clamp(Vector2.Dot(c - a, ab) / length, 0f, 1f) : 0f;
                var d = Vector2.DistanceSquared(c, a + ab * t);
                if (d > outer * outer) continue;
                var cost = d <= inner * inner ? core : RingCost;
                var i = _grid.Index(x, y);
                if (layer[i] < cost) layer[i] = cost;
            }
        }
    }
}
