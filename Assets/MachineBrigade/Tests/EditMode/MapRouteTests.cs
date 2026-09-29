using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Navigation;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Every battlefield on the menu, in every version, as a battle starts it (props, outline and
    /// the fixed defences on their ground): from each team's drop zone the movement system's
    /// pathfinder finds a ground route to every capture point and to the other team's drop zone,
    /// and in Siege from the player's drop zone to the command HQ. The water maps (the swamp's
    /// causeways, the islands' bridges, the rivers' crossings) and the walled ones (the fenced
    /// launch site, the landing beach's bluffs) are where a route can be cut off by a single prop.
    /// </summary>
    public class MapRouteTests
    {
        private static IEnumerable<string> Maps() => MatchSettings.AllMaps.Select(m => m.Id);

        /// <summary>The twelve battlefields of the first rounds, the eight of round 4M, Lighthouse Bay (prompt 16) and the two of prompt 20 M, each once.</summary>
        [Test]
        public void TwentyBattlefieldsAreOnTheMenu()
        {
            var ids = Maps().ToList();
            Assert.AreEqual(23, ids.Count, string.Join(", ", ids));
            CollectionAssert.AllItemsAreUnique(ids);
            foreach (var id in new[] { "landingbeach", "hydrodam", "capital", "launchsite", "saltflat", "borderbridge", "swamp", "coralisles",
                         "lighthousebay", "openpit", "orbitalgate" })
            {
                CollectionAssert.Contains(ids, id);
                Assert.IsTrue(MatchSettings.MapAvailable(id), $"{id}: its battlefield ships");
            }
        }

        private static SimWorld World(Catalog catalog, MapDefinition map)
        {
            var world = new SimWorld(catalog, map, seed: 1);
            foreach (var u in map.Units)
                if (catalog.Vehicle(u.DefId).Static)
                    world.SpawnVehicle(u.DefId, u.Team, u.Position, u.Heading);
            return world;
        }

        private static void AssertRoute(PathFinder finder, Vector2 from, Vector2 to, float near, string what)
        {
            var path = new List<Vector2>();
            Assert.IsTrue(finder.TryFindPath(from, to, path), $"{what}: no ground route from {from} to {to}");
            Assert.IsNotEmpty(path, $"{what}: an empty route from {from} to {to}");
            Assert.LessOrEqual(Vector2.Distance(path[path.Count - 1], to), near,
                $"{what}: the route from {from} ends at {path[path.Count - 1]}, short of {to}");
        }

        [TestCaseSource(nameof(Maps))]
        public void EveryDropZoneReachesEveryObjective(string map)
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var version in new[] { "_conquest", "_sandbox", "_siege" })
            {
                var id = map + version;
                var def = GameContent.LoadMap(id);
                var world = World(catalog, def);
                var finder = new PathFinder(world.Grid);
                Assert.AreEqual(2, def.Teams.Count, $"{id}: two drop zones");
                foreach (var team in def.Teams)
                {
                    Assert.IsTrue(world.Grid.IsWalkable(team.Rally), $"{id}: team {team.Team}'s drop zone is open ground");
                    foreach (var point in def.Points)
                        AssertRoute(finder, team.Rally, point.Position, point.Radius, $"{id}: team {team.Team} to {point.Id}");
                    foreach (var other in def.Teams.Where(t => t.Team != team.Team))
                        AssertRoute(finder, team.Rally, other.Rally, 6f, $"{id}: team {team.Team} to team {other.Team}'s drop zone");
                }
                if (version == "_conquest")
                    Assert.AreEqual(3, def.Points.Count, $"{id}: three capture points");
                if (version != "_siege") continue;

                // Siege: the player's drop zone reaches the command HQ (point blank, beside its walls).
                var hq = def.Props.Single(p => p.DefId == "command_hq");
                var size = catalog.Prop("command_hq");
                var player = def.Teams.First(t => t.Team == 0).Rally;
                AssertRoute(finder, player, hq.Position, MathF.Max(size.Width, size.Depth) * 0.5f + 4f, $"{id}: the player to the command HQ");
            }
        }
    }
}
