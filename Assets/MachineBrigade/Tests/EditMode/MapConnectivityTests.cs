using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 12 C.2, on the shipped map data and the sim's own grid: every drop zone, outpost, gate
    /// and objective is connected to the others for the biggest hull (a route at least three cells
    /// wide, the width of a gate: every cell of it with open ground all round), with every
    /// hardpoint filled by the biggest tower its size takes and every gate shut. Blocking only
    /// grows with a bigger tower in a hardpoint, so that is the worst of every hardpoint
    /// configuration; and each hardpoint's own centre is open ground, so no tower lands off it.
    /// </summary>
    public class MapConnectivityTests
    {
        private static IEnumerable<string> Maps() => MatchSettings.AllMaps.Select(m => m.Id);

        /// <summary>How near a place (metres beyond its footprint) the wide route has to come.</summary>
        private const float Reach = 6f;

        /// <summary>An objective is shot, not driven onto: a firing position this near will do.</summary>
        private const float FireReach = 15f;

        /// <summary>The loadout with the biggest tower of each size in every slot (and the utility modules).</summary>
        internal static BaseLoadout Biggest(Catalog catalog)
        {
            string Largest(SlotSize size, FortKind kind) => catalog.Vehicles.Values
                .Where(d => d.Fort is { } f && f.Kind == kind && f.Fits(size) && TowerCards.IsLoadoutTower(d.Id) && d.BranchOf == null && !d.Passable)
                .OrderByDescending(d => Math.Max(d.Length, d.Width)).ThenBy(d => d.Id, StringComparer.Ordinal).First().Id;
            var loadout = new BaseLoadout { HqLevel = catalog.Base.MaxLevel };
            foreach (var size in new[] { SlotSize.Small, SlotSize.Medium, SlotSize.Large })
                for (var i = 0; i < 8; i++) loadout.Of(size).Add(Largest(size, FortKind.Tower));
            loadout.Utilities.AddRange(catalog.Vehicles.Values.Where(d => d.Fort is { Kind: FortKind.Utility } && !d.Passable)
                .OrderByDescending(d => Math.Max(d.Length, d.Width)).ThenBy(d => d.Id, StringComparer.Ordinal).Select(d => d.Id).Take(3));
            return loadout;
        }

        /// <summary>The cells a hull of the biggest size can use: open, and open all round (clearance two cells).</summary>
        private static HashSet<int> WideFrom(SimWorld world, Vector2 start)
        {
            var grid = world.Grid;
            var lanes = world.Lanes;
            bool Wide(int x, int y) => grid.IsWalkable(x, y) && lanes.ClearanceAt(grid.CellCenter(x, y)) >= 2;
            var seen = new HashSet<int>();
            var (sx, sy) = grid.CellOf(start);
            // The drop zone's nearest wide cell.
            var best = -1;
            var bestD = float.MaxValue;
            for (var y = sy - 6; y <= sy + 6; y++)
            for (var x = sx - 6; x <= sx + 6; x++)
            {
                if (!grid.InBounds(x, y) || !Wide(x, y)) continue;
                var d = Vector2.DistanceSquared(grid.CellCenter(x, y), start);
                if (d >= bestD) continue;
                bestD = d;
                best = grid.Index(x, y);
            }
            if (best < 0) return seen;
            var queue = new Queue<int>();
            seen.Add(best);
            queue.Enqueue(best);
            while (queue.Count > 0)
            {
                var i = queue.Dequeue();
                int cx = i % grid.Width, cy = i / grid.Width;
                foreach (var (nx, ny) in new[] { (cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1) })
                {
                    if (!grid.InBounds(nx, ny) || !Wide(nx, ny)) continue;
                    if (seen.Add(grid.Index(nx, ny))) queue.Enqueue(grid.Index(nx, ny));
                }
            }
            return seen;
        }

        /// <summary>Whether a reached wide cell lies within <see cref="Reach"/> of a place's footprint.</summary>
        private static bool Reached(SimWorld world, HashSet<int> seen, Vector2 at, float halfX, float halfY)
        {
            var grid = world.Grid;
            var (x0, y0) = grid.CellOf(at - new Vector2(halfX + Reach, halfY + Reach));
            var (x1, y1) = grid.CellOf(at + new Vector2(halfX + Reach, halfY + Reach));
            for (var y = y0; y <= y1; y++)
            for (var x = x0; x <= x1; x++)
                if (grid.InBounds(x, y) && seen.Contains(grid.Index(x, y))) return true;
            return false;
        }

        [TestCaseSource(nameof(Maps))]
        public void EverySiegePlaceIsConnectedForTheBiggestHull(string id)
        {
            var catalog = GameContent.LoadCatalog();
            var map = GameContent.LoadMap(id + "_siege");
            var world = new SimWorld(catalog, map, 1);
            var hardpoints = map.Fortress?.Slots.Select(s => s.Hardpoint.Position).ToList() ?? new List<Vector2>();
            if (map.BaseOf(0) is { } camp) hardpoints.AddRange(camp.Slots.Select(s => s.Position));
            foreach (var h in hardpoints)
                Assert.IsTrue(world.Grid.IsWalkable(h), $"{id}: the hardpoint at {h} stands on open ground (its tower lands on it)");
            var biggest = Biggest(catalog);
            var mode = new SiegeMode(new SiegeRules { FortressLoadout = biggest, AttackerBase = biggest, Manning = 1f, Arrivals = false });
            mode.Setup(world);
            Assert.IsTrue(world.TryGetRally(0, out var attacker));
            var seen = WideFrom(world, attacker);
            var missing = new List<string>();
            void Need(string what, Vector2 at, float hx = 0f, float hy = 0f)
            {
                if (!Reached(world, seen, at, hx, hy)) missing.Add($"{what} {at}");
            }
            if (world.TryGetRally(1, out var keep)) Need("the defenders' drop zone", keep);
            foreach (var p in world.Props)
            {
                if (!p.IsAlive) continue;
                if (p.Def.Id is "radar_station_prop" or "shield_generator" or "command_hq")
                    Need(p.Def.Id, p.Position, p.Width / 2 + FireReach - Reach, p.Depth / 2 + FireReach - Reach);
                if (p.Def.Id == "base_gate")
                {
                    // Both mouths of every gateway (a shut gate's inner one by the long way round).
                    var across = p.Rotation % 180 == 0 ? new Vector2(0f, 1f) : new Vector2(1f, 0f);
                    Need("a gateway's mouth", p.Position + across * 6f);
                    Need("a gateway's mouth", p.Position - across * 6f);
                }
            }
            if (mode.SuperGun.IsValid && world.TryGetVehicle(mode.SuperGun, out var gun)) Need("the super-gun", gun.Position, 4f + FireReach - Reach, 4f + FireReach - Reach);
            if (map.Fortress?.Arrival is { } line) Need("the line's stop", line.Stop);
            Assert.IsEmpty(missing, $"{id} siege: out of reach of the biggest hull with every gate shut and every hardpoint filled: {string.Join("; ", missing)}");
        }

        [TestCaseSource(nameof(Maps))]
        public void EveryConquestPlaceIsConnectedForTheBiggestHull(string id)
        {
            var catalog = GameContent.LoadCatalog();
            var map = GameContent.LoadMap(id + "_conquest");
            var world = new SimWorld(catalog, map, 1);
            foreach (var b in map.Bases)
            foreach (var s in b.Slots)
                Assert.IsTrue(world.Grid.IsWalkable(s.Position), $"{id}: team {b.Team}'s hardpoint at {s.Position} stands on open ground");
            var biggest = Biggest(catalog);
            world.Bases.Establish(0, biggest, BaseRole.Anchor);
            world.Bases.Establish(1, biggest, BaseRole.Anchor);
            // Every outpost built, with the biggest tower each hardpoint takes.
            foreach (var point in map.Points)
                foreach (var h in point.Outpost)
                {
                    var tower = biggest.TowerForFortress(h.Class, 0);
                    if (tower != null) world.AnchorDefence(world.SpawnVehicle(tower, 0, h.Position, h.Facing));
                }
            Assert.IsTrue(world.TryGetRally(0, out var home));
            var seen = WideFrom(world, home);
            var missing = new List<string>();
            if (world.TryGetRally(1, out var enemy) && !Reached(world, seen, enemy, 0f, 0f)) missing.Add($"the enemy drop zone {enemy}");
            foreach (var point in map.Points)
                if (!Reached(world, seen, point.Position, 0f, 0f)) missing.Add($"point {point.Id} {point.Position}");
            Assert.IsEmpty(missing, $"{id} conquest: out of reach of the biggest hull with every hardpoint and outpost filled: {string.Join("; ", missing)}");
        }
    }
}
