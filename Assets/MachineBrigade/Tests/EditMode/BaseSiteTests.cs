using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Navigation;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The base hardpoints the map builder (Tools/maps/hardpoints.py) writes into every Conquest and
    /// Siege battlefield: each camp's HQ and its tower and utility hardpoints, and the outposts at
    /// the Conquest objectives. They stand on open ground, off every road and doorway, and with
    /// every one of them filled by the largest structure its size takes, every route of the
    /// battle is still open: camp to camp, camp to every objective, out of the camp in every
    /// direction, and no new doorway anywhere.
    /// </summary>
    public class BaseSiteTests
    {
        private static readonly string[] Maps =
        {
            "ashfield", "dunebreak", "frostpeak", "ironport", "redrock", "whiteout", "greenvale", "rustyard", "emberridge",
            "junglepass", "skyhold", "metrocity",
            "landingbeach", "hydrodam", "capital", "launchsite", "saltflat", "borderbridge", "swamp", "coralisles",
        };

        private static IEnumerable<string> Versions() => Maps.SelectMany(m => new[] { m + "_conquest", m + "_siege" });

        private static IEnumerable<string> Conquest() => Maps.Select(m => m + "_conquest");

        /// <summary>Metres across the largest structure each hardpoint size takes (what it must keep clear).</summary>
        private static readonly Dictionary<string, float> Clearance = new()
        {
            ["small"] = 5f,
            ["medium"] = 6.5f,
            ["large"] = 9f,
        };

        /// <summary>What a camp needs at least: tower hardpoints per size, and utility hardpoints.</summary>
        private static readonly (string size, int count)[] CampTowers = { ("large", 2), ("medium", 3), ("small", 6) };
        private const int CampUtilities = 3;

        /// <summary>Towers the fill may use, biggest first (the fill falls back to a plain footprint).</summary>
        private static readonly string[] Structures =
        {
            "missile_battery", "heavy_turret", "flak_tower", "artillery_emplacement", "gun_turret", "rocket_turret",
            "aa_turret", "mg_bunker", "guard_tower", "point_tower",
        };

        private const string Hq = "headquarters";

        private const LaneFlags Forbidden = LaneFlags.Road | LaneFlags.Narrow | LaneFlags.NoPark;

        // ------------------------------------------------------------------------------ the data

        private sealed class Slot
        {
            public Vector2 At;
            public string Kind;
            public string Size;
            public float Across;
            public float Facing;
            public int Point = -1;
        }

        private sealed class Camp
        {
            public int Team;
            public Vector2 Hq;
            public float Heading;
            public readonly List<Slot> Slots = new();
        }

        private sealed class Sites
        {
            public readonly List<Camp> Camps = new();
            public readonly List<List<Slot>> Outposts = new();
            public IEnumerable<Slot> AllOutposts => Outposts.SelectMany(o => o);
        }

        private static float Number(object value) => Convert.ToSingle(value);

        private static string Text(string id)
        {
            var asset = UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/maps/" + id);
            Assert.IsNotNull(asset, id);
            return asset.text;
        }

        /// <summary>
        /// The battlefield itself (props, outline, camps, objectives, units) without its hardpoints,
        /// which the geometry here reads from the file (see <see cref="Read"/>): so these tests stand
        /// whatever the game makes of the hardpoint sizes.
        /// </summary>
        private static MapDefinition Battlefield(string id)
        {
            var text = Regex.Replace(Text(id), @",\s*""outpost"":\s*\[[^\]]*\]", "");
            text = Regex.Replace(text, @",\s*""bases"":\s*\[.*?\r?\n  \]", "", RegexOptions.Singleline);
            return MapDefinition.FromJson(text);
        }

        /// <summary>The hardpoints as the file writes them (sizes as names, so the reading does not depend on how the game stores them).</summary>
        private static Sites Read(string id)
        {
            var root = (Dictionary<string, object>)MiniJson.Parse(Text(id));
            var sites = new Sites();

            Slot ParseSlot(Dictionary<string, object> s, string where)
            {
                var size = s["size"];
                var slot = new Slot
                {
                    At = new Vector2(Number(s["x"]), Number(s["z"])),
                    Kind = s.TryGetValue("kind", out var k) ? (string)k : "tower",
                    Facing = s.TryGetValue("facing", out var f) ? Number(f) : 0f,
                };
                if (size is string name)
                {
                    Assert.IsTrue(Clearance.ContainsKey(name), $"{where}: size '{name}' is small, medium or large");
                    slot.Size = name;
                    slot.Across = Clearance[name];
                }
                else
                {
                    slot.Across = Number(size);
                    slot.Size = slot.Across.ToString("0.#");
                }
                return slot;
            }

            if (root.TryGetValue("bases", out var bases))
                foreach (Dictionary<string, object> b in (List<object>)bases)
                {
                    var hq = (Dictionary<string, object>)b["hq"];
                    var camp = new Camp
                    {
                        Team = Convert.ToInt32(b["team"]),
                        Hq = new Vector2(Number(hq["x"]), Number(hq["z"])),
                        Heading = hq.TryGetValue("heading", out var h) ? Number(h) : 0f,
                    };
                    foreach (Dictionary<string, object> s in (List<object>)b["slots"])
                        camp.Slots.Add(ParseSlot(s, $"{id} team {camp.Team}"));
                    sites.Camps.Add(camp);
                }
            if (root.TryGetValue("points", out var points))
            {
                var list = (List<object>)points;
                for (var i = 0; i < list.Count; i++)
                {
                    var p = (Dictionary<string, object>)list[i];
                    var outpost = new List<Slot>();
                    if (p.TryGetValue("outpost", out var o))
                        foreach (Dictionary<string, object> s in (List<object>)o)
                        {
                            var slot = ParseSlot(s, $"{id} point {p["id"]}");
                            slot.Point = i;
                            outpost.Add(slot);
                        }
                    sites.Outposts.Add(outpost);
                }
            }
            return sites;
        }

        // ------------------------------------------------------------------------------ worlds

        private static float Across(VehicleDef def) => MathF.Max(def.Length, def.Width);

        /// <summary>The battlefield as a battle starts it: its props, and any fixed defences it places (the siege fortress) on their ground.</summary>
        private static SimWorld World(Catalog catalog, MapDefinition map)
        {
            var world = new SimWorld(catalog, map, seed: 1);
            foreach (var u in map.Units)
                if (catalog.Vehicle(u.DefId).Static)
                    world.SpawnVehicle(u.DefId, u.Team, u.Position, u.Heading);
            return world;
        }

        /// <summary>
        /// Puts the largest tower that fits into a hardpoint (SpawnVehicle anchors it on its ground);
        /// where no tower is quite as big as the size, its whole footprint is blocked as a structure
        /// that size would be (AnchorDefence: 0.8 times across, grown by the obstacle clearance).
        /// </summary>
        private static void Fill(SimWorld world, Catalog catalog, int team, Slot slot, string where)
        {
            var def = Structures.Where(catalog.Vehicles.ContainsKey).Select(catalog.Vehicle)
                .Where(d => d.Static && Across(d) <= slot.Across + 0.01f).OrderByDescending(Across).FirstOrDefault();
            if (def != null)
            {
                var tower = world.SpawnVehicle(def.Id, team, slot.At, Sim.Core.SimMath.DegToRad(slot.Facing));
                Assert.Less(Vector2.Distance(tower.Position, slot.At), 0.01f, $"{where}: the {def.Id} stands on its hardpoint at {slot.At}");
            }
            if (def == null || Across(def) < slot.Across - 0.01f)
                world.Grid.AddBlocker(slot.At, slot.Across * 0.8f, slot.Across * 0.8f, SimWorld.ObstacleClearance);
        }

        private static void FillCamps(SimWorld world, Catalog catalog, Sites sites, string id)
        {
            foreach (var camp in sites.Camps)
            {
                var hq = world.SpawnVehicle(Hq, camp.Team, camp.Hq, Sim.Core.SimMath.DegToRad(camp.Heading));
                Assert.Less(Vector2.Distance(hq.Position, camp.Hq), 0.01f, $"{id}: team {camp.Team}'s HQ stands on its spot");
                foreach (var slot in camp.Slots)
                    Fill(world, catalog, camp.Team, slot, $"{id} team {camp.Team}");
            }
        }

        private static bool[] Reach(NavGrid grid, Vector2 from)
        {
            var reached = new bool[grid.Width * grid.Height];
            var (sx, sy) = grid.CellOf(from);
            if (!grid.IsWalkable(sx, sy)) return reached;
            var todo = new Stack<(int, int)>();
            todo.Push((sx, sy));
            reached[grid.Index(sx, sy)] = true;
            while (todo.Count > 0)
            {
                var (x, y) = todo.Pop();
                foreach (var (dx, dy) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                {
                    int nx = x + dx, ny = y + dy;
                    if (!grid.IsWalkable(nx, ny) || reached[grid.Index(nx, ny)]) continue;
                    reached[grid.Index(nx, ny)] = true;
                    todo.Push((nx, ny));
                }
            }
            return reached;
        }

        /// <summary>A ground route with the movement system's pathfinder, ending within <paramref name="near"/> of the target.</summary>
        private static void AssertRoute(SimWorld world, Vector2 from, Vector2 to, float near, string what)
        {
            var finder = new PathFinder(world.Grid);
            var path = new List<Vector2>();
            Assert.IsTrue(finder.TryFindPath(from, to, path), $"{what}: no ground route from {from} to {to}");
            Assert.LessOrEqual(Vector2.Distance(path[path.Count - 1], to), near, $"{what}: the route ends {path[path.Count - 1]}, short of {to}");
        }

        /// <summary>
        /// Everything that must stay open once the hardpoints are filled: the routes between the camps
        /// and to every objective (and, in Siege, into the fortress), the way out of each camp to the
        /// map centre, every cell the camp reached before, and no new doorway (gate or narrow gap) anywhere.
        /// </summary>
        private static void AssertOpen(SimWorld bare, SimWorld filled, MapDefinition map, string what)
        {
            var grid = filled.Grid;
            var teams = map.Teams;
            foreach (var team in teams)
            {
                Assert.IsTrue(grid.IsWalkable(team.Rally), $"{what}: team {team.Team}'s drop zone is open");
                foreach (var other in teams.Where(t => t.Team != team.Team))
                    AssertRoute(filled, team.Rally, other.Rally, 6f, $"{what}: team {team.Team} to team {other.Team}'s camp");
                foreach (var point in map.Points)
                    AssertRoute(filled, team.Rally, point.Position, point.Radius, $"{what}: team {team.Team} to {point.Id}");
                AssertRoute(filled, team.Rally, Vector2.Zero, 34f, $"{what}: team {team.Team} out of its camp to the map centre");

                // Not one cell the camp could reach is cut off: every way out of the camp is still open.
                var before = Reach(bare.Grid, team.Rally);
                var after = Reach(grid, team.Rally);
                var lost = new List<Vector2>();
                for (var y = 0; y < grid.Height; y++)
                for (var x = 0; x < grid.Width; x++)
                {
                    var i = grid.Index(x, y);
                    if (before[i] && grid.IsWalkable(x, y) && !after[i]) lost.Add(grid.CellCenter(x, y));
                }
                Assert.IsEmpty(lost, $"{what}: filled hardpoints cut team {team.Team}'s camp off from {lost.Count} cells, e.g. {string.Join(", ", lost.Take(3))}");
            }

            foreach (var u in map.Units)
                if (!bare.Catalog.Vehicle(u.DefId).Static)
                    Assert.IsTrue(grid.IsWalkable(u.Position), $"{what}: the start {u.DefId} at {u.Position} is not under a structure");

            var bareLanes = bare.Lanes;
            var lanes = filled.Lanes;
            var doorways = new List<Vector2>();
            for (var y = 0; y < grid.Height; y++)
            for (var x = 0; x < grid.Width; x++)
                if (grid.IsWalkable(x, y) && (lanes.FlagsOf(x, y) & LaneFlags.Narrow) != 0 && (bareLanes.FlagsOf(x, y) & LaneFlags.Narrow) == 0)
                    doorways.Add(grid.CellCenter(x, y));
            Assert.IsEmpty(doorways, $"{what}: filled hardpoints make {doorways.Count} new doorway cells, e.g. {string.Join(", ", doorways.Take(3))}");
        }

        /// <summary>A square footprint stands inside the outline, on open ground, off every road and doorway (gates are doorways).</summary>
        private static void AssertOpenGround(SimWorld world, MapDefinition map, Vector2 at, float across, string what)
        {
            var half = new Vector2(across * 0.5f);
            foreach (var corner in new[] { at - half, at + half, new Vector2(at.X - half.X, at.Y + half.Y), new Vector2(at.X + half.X, at.Y - half.Y) })
                Assert.IsTrue(map.InsideBoundary(corner), $"{what}: {at} reaches outside the outline");
            var grid = world.Grid;
            var lanes = world.Lanes;
            var (x0, y0) = grid.CellOf(at - half);
            var (x1, y1) = grid.CellOf(at + half - new Vector2(1e-3f));
            for (var y = y0; y <= y1; y++)
            for (var x = x0; x <= x1; x++)
            {
                Assert.IsTrue(grid.IsWalkable(x, y), $"{what}: {at} covers blocked ground at {grid.CellCenter(x, y)}");
                var flags = lanes.FlagsOf(x, y) & Forbidden;
                Assert.AreEqual(LaneFlags.None, flags, $"{what}: {at} covers a {flags} cell at {grid.CellCenter(x, y)}");
            }
        }

        // ------------------------------------------------------------------------------ tests

        /// <summary>
        /// Conquest has both camps and an outpost (one medium and one small hardpoint) at every
        /// objective, Siege the attacker's camp only, Survival none; each camp has its HQ and at
        /// least 2 large, 3 medium and 6 small tower hardpoints and 3 utility hardpoints, and the
        /// game reads them all.
        /// </summary>
        [Test]
        public void EveryBattlefieldHasItsBases()
        {
            foreach (var m in Maps)
            {
                var conquest = Read(m + "_conquest");
                CollectionAssert.AreEquivalent(new[] { 0, 1 }, conquest.Camps.Select(c => c.Team).ToArray(), $"{m}_conquest: both camps");
                Assert.AreEqual(3, conquest.Outposts.Count, $"{m}_conquest: three objectives");
                for (var i = 0; i < conquest.Outposts.Count; i++)
                    CollectionAssert.AreEquivalent(new[] { "medium", "small" }, conquest.Outposts[i].Select(s => s.Size).ToArray(),
                        $"{m}_conquest: objective {i} has a medium and a small outpost hardpoint");
                var siege = Read(m + "_siege");
                CollectionAssert.AreEqual(new[] { 0 }, siege.Camps.Select(c => c.Team).ToArray(), $"{m}_siege: the attacker's camp only");
                Assert.IsEmpty(Read(m + "_sandbox").Camps, $"{m}_sandbox: Survival has no bases");

                foreach (var (id, sites) in new[] { (m + "_conquest", conquest), (m + "_siege", siege) })
                {
                    foreach (var camp in sites.Camps)
                    {
                        var towers = camp.Slots.Where(s => s.Kind == "tower").ToList();
                        foreach (var (size, count) in CampTowers)
                            Assert.GreaterOrEqual(towers.Count(s => s.Size == size), count, $"{id} team {camp.Team}: {size} tower hardpoints");
                        Assert.GreaterOrEqual(camp.Slots.Count(s => s.Kind == "utility"), CampUtilities, $"{id} team {camp.Team}: utility hardpoints");
                        Assert.IsTrue(camp.Slots.All(s => s.Kind == "tower" || s.Kind == "utility"), $"{id} team {camp.Team}: kinds");
                    }

                    // The game reads the same camps and outposts.
                    var map = GameContent.LoadMap(id);
                    Assert.AreEqual(sites.Camps.Count, map.Bases.Count, $"{id}: bases read");
                    foreach (var camp in sites.Camps)
                    {
                        var site = map.BaseOf(camp.Team);
                        Assert.IsNotNull(site, $"{id}: team {camp.Team}'s base read");
                        Assert.Less(Vector2.Distance(site.Hq, camp.Hq), 0.01f, $"{id}: team {camp.Team}'s HQ");
                        CollectionAssert.AreEqual(camp.Slots.Select(s => s.At).ToArray(), site.Slots.Select(s => s.Position).ToArray(),
                            $"{id}: team {camp.Team}'s hardpoints, in order");
                        CollectionAssert.AreEqual(camp.Slots.Select(s => s.Size).ToArray(),
                            site.Slots.Select(s => s.Class.ToString().ToLowerInvariant()).ToArray(), $"{id}: team {camp.Team}'s hardpoint sizes");
                        CollectionAssert.AreEqual(camp.Slots.Select(s => s.Across).ToArray(), site.Slots.Select(s => s.Size).ToArray(),
                            $"{id}: team {camp.Team}'s hardpoints keep the clearance the builder planned for");
                    }
                    for (var i = 0; i < sites.Outposts.Count; i++)
                        CollectionAssert.AreEqual(sites.Outposts[i].Select(s => s.At).ToArray(), map.Points[i].Outpost.Select(s => s.Position).ToArray(),
                            $"{id}: {map.Points[i].Id}'s outpost hardpoints");
                }
            }
        }

        /// <summary>Every HQ and hardpoint stands inside the outline on open ground, clear of every road, gate, narrow pass and no-parking mouth.</summary>
        [TestCaseSource(nameof(Versions))]
        public void HardpointsStandOnOpenGround(string id)
        {
            var catalog = GameContent.LoadCatalog();
            var map = Battlefield(id);
            var sites = Read(id);
            var world = World(catalog, map);
            var hqAcross = Across(catalog.Vehicle(Hq));
            foreach (var camp in sites.Camps)
            {
                AssertOpenGround(world, map, camp.Hq, hqAcross, $"{id} team {camp.Team} HQ");
                foreach (var slot in camp.Slots)
                    AssertOpenGround(world, map, slot.At, slot.Across, $"{id} team {camp.Team} {slot.Size} {slot.Kind}");
            }
            foreach (var slot in sites.AllOutposts)
                AssertOpenGround(world, map, slot.At, slot.Across, $"{id} {map.Points[slot.Point].Id} {slot.Size} outpost");
        }

        /// <summary>
        /// Every camp filled to the last hardpoint (the HQ, and in each hardpoint the largest
        /// structure its size takes) leaves every route open: camp to camp, camp to every objective,
        /// out of the camp to the map centre, and no ground cut off or new doorway made.
        /// </summary>
        [TestCaseSource(nameof(Versions))]
        public void FilledBasesKeepEveryRouteOpen(string id)
        {
            var catalog = GameContent.LoadCatalog();
            var map = Battlefield(id);
            var sites = Read(id);
            var bare = World(catalog, map);
            var filled = World(catalog, map);
            FillCamps(filled, catalog, sites, id);
            AssertOpen(bare, filled, map, id);
        }

        /// <summary>The outposts filled too (with both camps): every objective's circle can still be reached from both camps.</summary>
        [TestCaseSource(nameof(Conquest))]
        public void FilledOutpostsKeepEveryPointReachable(string id)
        {
            var catalog = GameContent.LoadCatalog();
            var map = Battlefield(id);
            var sites = Read(id);
            var bare = World(catalog, map);
            var filled = World(catalog, map);
            FillCamps(filled, catalog, sites, id);
            foreach (var slot in sites.AllOutposts)
                Fill(filled, catalog, 0, slot, $"{id} {map.Points[slot.Point].Id} outpost");
            AssertOpen(bare, filled, map, id + " with its outposts");
        }
    }
}
