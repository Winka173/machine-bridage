using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The upgraded siege fortress (Tools/maps/fortress.py, SiegeMode): it holds 40-50 % of every
    /// battlefield; its gates block until blown in, its walls fall into passable rubble and no set
    /// piece ever closes every way to the HQ; the shield dome goes with the last generator; the
    /// super-gun fires on its countdown until destroyed; reinforcements come in by rail or runway;
    /// its towers are the defender's loadout, the inner lines' tougher.
    /// </summary>
    public class SiegeUpgradeTests
    {
        private const float Step = 0.05f;

        private static readonly string[] Maps =
        {
            "ashfield", "dunebreak", "frostpeak", "ironport", "redrock", "whiteout", "greenvale", "rustyard", "emberridge",
            "junglepass", "skyhold", "metrocity",
        };

        private static (SimWorld world, SiegeMode mode) Siege(string map, SiegeRules rules = null, int seed = 3)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map + "_siege"), seed);
            var mode = new SiegeMode(rules ?? Quiet());
            mode.Setup(world);
            return (world, mode);
        }

        /// <summary>No income, no one buying: only what the test does happens.</summary>
        private static SiegeRules Quiet() => new()
        {
            Attacker = new SideSetup { StartCp = 0f, Income = 0.01f, Vehicles = new[] { "main_battle_tank" } },
            Defender = new SideSetup { StartCp = 0f, Income = 0.01f, Vehicles = new[] { "light_tank" } },
        };

        private static void Run(SimWorld world, SiegeMode mode, float seconds, List<SimEvent> seen = null)
        {
            for (var t = 0f; t < seconds && mode.Result == null; t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
                seen?.AddRange(world.Events);
                world.ClearEvents();
            }
        }

        private static void Destroy(SimWorld world, string defId)
        {
            foreach (var p in world.Props.ToList())
                if (p.IsAlive && p.Def.Id == defId) world.DebugDestroyProp(p);
        }

        /// <summary>Whether a ground route leads from a point to within 3 m of a footprint, on the grid as it is now.</summary>
        private static bool Reaches(SimWorld world, Vector2 from, Vector2 centre, float halfWidth, float halfDepth)
        {
            var grid = world.Grid;
            var reached = new bool[grid.Width * grid.Height];
            var (sx, sy) = grid.CellOf(from);
            if (!grid.IsWalkable(sx, sy)) return false;
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
            var (x0, y0) = grid.CellOf(centre - new Vector2(halfWidth + 3f, halfDepth + 3f));
            var (x1, y1) = grid.CellOf(centre + new Vector2(halfWidth + 3f, halfDepth + 3f));
            for (var y = y0; y <= y1; y++)
            for (var x = x0; x <= x1; x++)
                if (grid.InBounds(x, y) && reached[grid.Index(x, y)]) return true;
            return false;
        }

        private static Prop Hq(SimWorld world) => world.Props.First(p => p.Def.Id == "command_hq");

        [TestCaseSource(nameof(Maps))]
        public void TheFortressHoldsFortyToFiftyPercentOfTheBattlefield(string id)
        {
            var map = GameContent.LoadMap(id + "_siege");
            Assert.IsNotNull(map.Fortress, $"{id}: has a fortress");
            int inside = 0, fortress = 0;
            var half = map.HalfSize;
            for (var x = -half + 1f; x < half; x += 2f)
            for (var z = -half + 1f; z < half; z += 2f)
            {
                var p = new Vector2(x, z);
                if (!map.InsideBoundary(p)) continue;
                inside++;
                if (map.Fortress.Contains(p)) fortress++;
            }
            var share = fortress / (float)inside;
            Assert.That(share, Is.InRange(0.40f, 0.50f), $"{id}: the fortress holds {share:P0} of the play area");
            // The player's camp and its approach stay clear of it.
            Assert.IsFalse(map.Fortress.Contains(map.Teams.First(t => t.Team == 0).Rally), $"{id}: the attacker's camp is outside");
            foreach (var slot in map.BaseOf(0).Slots)
                Assert.IsFalse(map.Fortress.Contains(slot.Position), $"{id}: the attacker camp's hardpoint at {slot.Position} is outside the fortress");
        }

        /// <summary>
        /// With every fortress tower up and every gate shut the HQ can still be reached (the sally
        /// ports), and so it can once every wall and gate has fallen; a fallen wall's ground opens
        /// once it is down.
        /// </summary>
        [TestCaseSource(nameof(Maps))]
        public void TheHqCanBeReachedBeforeAndAfterTheWallsFall(string id)
        {
            var (world, mode) = Siege(id);
            world.TryGetRally(mode.Attacker, out var camp);
            var hq = Hq(world);
            Assert.Greater(mode.Gates.Count, 0, $"{id}: the fortress has gates");
            foreach (var (gateId, _, _) in mode.Gates)
            {
                world.TryGetProp(gateId, out var gate);
                Assert.IsFalse(world.Grid.IsWalkable(gate.Position), $"{id}: the gate at {gate.Position} is shut");
            }
            Assert.IsTrue(Reaches(world, camp, hq.Position, hq.Width / 2f, hq.Depth / 2f), $"{id}: the HQ can be reached with the gates shut");
            world.TryGetRally(mode.Defender, out var inside);
            Assert.IsTrue(Reaches(world, camp, inside, 1f, 1f), $"{id}: the defenders' camp in the keep can be reached");

            var walls = world.Props.Where(p => p.IsAlive && p.Def.Id == "base_wall").ToList();
            Destroy(world, "base_wall");
            Destroy(world, "fortress_gate");
            Assert.IsFalse(world.Grid.IsWalkable(walls[0].Position), $"{id}: a toppling wall still blocks while it comes down");
            Run(world, mode, 2f);
            Assert.IsTrue(walls.All(w => !w.IsAlive), $"{id}: every wall is down");
            Assert.IsTrue(world.Grid.IsWalkable(walls[0].Position) || !world.Map.InsideBoundary(walls[0].Position),
                $"{id}: a fallen wall's rubble can be driven over");
            Assert.IsTrue(Reaches(world, camp, hq.Position, hq.Width / 2f, hq.Depth / 2f), $"{id}: the HQ can be reached with the walls down");
        }

        [Test]
        public void AGateBlocksUntilItIsBlownIn()
        {
            var (world, mode) = Siege("ashfield");
            Destroy(world, "radar_station");
            var events = new List<SimEvent>();
            Run(world, mode, 0.5f, events);
            Assert.AreEqual(2, mode.Stage, "the relays down: the walls are next");
            // The attackers are outside the walls: they have to blow in the gate nearest them first.
            world.TryGetRally(mode.Attacker, out var camp);
            world.SpawnVehicle("main_battle_tank", mode.Attacker, camp, 0f);
            var gateId = mode.GateToBreak(world);
            Assert.IsTrue(gateId.IsValid, "a gate to blow in");
            Assert.AreEqual(gateId, mode.AttackTarget(world), "the army's target is the gate");
            world.TryGetProp(gateId, out var gate);
            Assert.Less(Vector2.Distance(mode.AttackGoal(world).Value, gate.Position), 12f, "the army goes to the gate");
            Assert.IsFalse(world.Grid.IsWalkable(gate.Position), "the gate blocks the way");
            world.DebugDestroyProp(gate);
            Run(world, mode, 0.5f, events);
            Assert.IsTrue(world.Grid.IsWalkable(gate.Position), "blown in: the way is open");
            Assert.IsFalse(mode.GateToBreak(world).IsValid, "the walls are breached: the army goes for the generators");
            Assert.IsTrue(world.TryGetProp(mode.Target(world), out var generator) && generator.Def.Id == "shield_generator");
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.FortressAlert && e.DefId == "siege.gate" && e.Team == 0),
                "the news of the gate (good news for the attacking player)");
        }

        [Test]
        public void TheShieldDomeDropsWithTheLastGenerator()
        {
            var (world, mode) = Siege("ashfield");
            var keepTowers = world.Bases.Of(mode.Defender).Slots.Where(s => s.Ring == 3 && s.Structure.IsValid).Select(s => s.Structure).ToList();
            Assert.Greater(keepTowers.Count, 0, "the keep has towers");
            Assert.IsTrue(mode.DomeUp, "the dome is up");
            Assert.Greater(mode.DomeRadius, 20f, "it covers the keep");
            Assert.IsTrue(keepTowers.All(id => world.TryGetVehicle(id, out var v) && v.Invulnerable), "under the dome the keep's guns cannot be hurt");
            Destroy(world, "radar_station");
            var events = new List<SimEvent>();
            Run(world, mode, 0.5f, events);
            Assert.IsTrue(mode.DomeUp, "the outer line down, the dome still stands");
            var generators = world.Props.Where(p => p.IsAlive && p.Def.Id == "shield_generator").ToList();
            Assert.GreaterOrEqual(generators.Count, 2);
            for (var i = 0; i < generators.Count; i++)
            {
                world.DebugDestroyProp(generators[i]);
                Run(world, mode, 0.5f, events);
                Assert.AreEqual(i < generators.Count - 1, mode.DomeUp, $"with {generators.Count - 1 - i} generators left");
            }
            Assert.AreEqual(3, mode.Stage);
            Assert.IsTrue(keepTowers.All(id => !world.TryGetVehicle(id, out var v) || !v.Invulnerable), "the dome down, the keep's guns can be hit");
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.FortressAlert && e.DefId == "siege.dome"), "the dome's fall is announced");
        }

        [Test]
        public void TheSuperGunFiresOnItsCountdownAndStopsWhenDestroyed()
        {
            var rules = Quiet();
            rules.SuperGunFirst = 10f;
            rules.SuperGunSeconds = 20f;
            var (world, mode) = Siege("ashfield", rules);
            Assert.IsTrue(mode.SuperGun.IsValid, "the fortress has its super-gun");
            world.TryGetRally(mode.Attacker, out var camp);
            for (var i = 0; i < 4; i++) world.SpawnVehicle("main_battle_tank", mode.Attacker, camp + new Vector2(i * 4f, 0f), 0f);
            Assert.That(mode.SuperGunCountdown(world), Is.EqualTo(10f).Within(0.1f));
            var events = new List<SimEvent>();
            Run(world, mode, 9.5f, events);
            Assert.IsFalse(events.Any(e => e.Kind == SimEventKind.StrikeWarning && e.DefId == "super_gun_shell"), "not before its countdown");
            Run(world, mode, 1f, events);
            var shot = events.FirstOrDefault(e => e.Kind == SimEventKind.StrikeWarning && e.DefId == "super_gun_shell");
            Assert.AreEqual(SimEventKind.StrikeWarning, shot.Kind, "it fires when the countdown runs out");
            Assert.Less(Vector2.Distance(shot.Position, camp), 20f, "at the knot of attackers");
            Assert.That(mode.SuperGunCountdown(world), Is.EqualTo(20f).Within(1f), "the countdown starts again");
            world.TryGetEconomy(mode.Attacker, out var attacker);
            var cp = attacker.Cp;
            world.TryGetVehicle(mode.SuperGun, out var gun);
            world.DebugDamage(gun, 5f);
            events.Clear();
            Run(world, mode, 40f, events);
            Assert.IsTrue(mode.SuperGunDown, "destroyed");
            Assert.AreEqual(-1f, mode.SuperGunCountdown(world), "no countdown any more");
            Assert.IsFalse(events.Any(e => e.Kind == SimEventKind.StrikeWarning && e.DefId == "super_gun_shell"), "it fires no more");
            Assert.GreaterOrEqual(attacker.Cp, cp + rules.SuperGunCp - 1f, "the side objective pays the attacker");
        }

        [TestCase("ironport", "rail")]
        [TestCase("ashfield", "runway")]
        public void ReinforcementsComeInByTheLine(string id, string kind)
        {
            var rules = Quiet();
            rules.Defender = new SideSetup { StartCp = 30f, Income = 0.01f, Vehicles = new[] { "light_tank" } };
            var (world, mode) = Siege(id, rules);
            var line = world.Map.Fortress.Arrival;
            Assert.IsNotNull(line, $"{id}: has a line in");
            Assert.AreEqual(kind, line.Kind.ToString().ToLowerInvariant());
            var events = new List<SimEvent>();
            Run(world, mode, 1f, events);
            Assert.IsTrue(world.Submit(Sim.Commands.Command.Deploy(mode.Defender, "light_tank")).Accepted, "the defender buys a tank");
            events.AddRange(world.Events);
            var arrival = events.FirstOrDefault(e => e.Kind == SimEventKind.Arrival);
            Assert.AreEqual(SimEventKind.Arrival, arrival.Kind, "a train or an aircraft is on its way");
            Assert.AreEqual(kind, arrival.DefId);
            Assert.IsTrue(events.Any(e => e.ByLine && e.DefId == "light_tank"), "the tank comes by the line, not by parachute");
            var lands = world.Time + arrival.Value;
            world.ClearEvents();
            Run(world, mode, arrival.Value - 1f);
            Assert.IsFalse(world.Vehicles.Any(v => v.Team == mode.Defender && v.Def.Id == "light_tank"), "not before it stops");
            Run(world, mode, 2f);
            var tank = world.Vehicles.FirstOrDefault(v => v.Team == mode.Defender && v.Def.Id == "light_tank");
            Assert.IsNotNull(tank, $"it rolls out when the {kind} stops at {lands:0.0} s");
            Assert.Less(Vector2.Distance(tank.Position, line.Stop), 20f, "at the line's stop");
        }

        [Test]
        public void TheFortressTowersAreTheLoadoutsAndTheInnerOnesTougher()
        {
            var catalog = GameContent.LoadCatalog();
            var loadout = BaseLoadout.ForAi(catalog, "Normal", "default", 5);
            var rules = Quiet();
            rules.FortressLoadout = loadout;
            var (world, mode) = Siege("dunebreak", rules);
            var fortress = world.Bases.Of(mode.Defender);
            Assert.IsNotNull(fortress, "the fortress is the defender's base");
            var allowed = new HashSet<string>(loadout.Towers.Concat(loadout.Utilities));
            var byRing = new Dictionary<string, (float ring1, float ring3)>();
            foreach (var slot in fortress.Slots)
            {
                if (!world.TryGetVehicle(slot.Structure, out var tower)) continue;
                Assert.IsTrue(allowed.Contains(tower.Def.CardId), $"the {tower.Def.Id} in ring {slot.Ring} is one of the loadout's");
                var (r1, r3) = byRing.TryGetValue(tower.Def.Id, out var hp) ? hp : (0f, 0f);
                if (slot.Ring == 1) r1 = tower.MaxHp;
                if (slot.Ring == 3) r3 = tower.MaxHp;
                byRing[tower.Def.Id] = (r1, r3);
            }
            Assert.GreaterOrEqual(fortress.Slots.Count(s => s.Structure.IsValid), 24, "every ring manned");
            // A tower of the same kind in the outer line and in the keep: the keep's is tougher.
            var pair = byRing.Where(kv => kv.Value.ring1 > 0f && kv.Value.ring3 > 0f).ToList();
            foreach (var (defId, (r1, r3)) in pair.Select(kv => (kv.Key, kv.Value)))
                Assert.That(r3 / r1, Is.EqualTo(rules.LineHealth[2] / rules.LineHealth[0]).Within(0.01f), $"{defId}: the keep's is tougher");
            var small = fortress.Slots.Where(s => s.Ring == 1 && s.Structure.IsValid).Select(s => world.TryGetVehicle(s.Structure, out var v) ? v.MaxHp / v.Def.MaxHp : 0f);
            var keep = fortress.Slots.Where(s => s.Ring == 3 && s.Def.Kind == HardpointKind.Tower && s.Structure.IsValid)
                .Select(s => world.TryGetVehicle(s.Structure, out var v) ? v.MaxHp / v.Def.MaxHp : 0f);
            Assert.Greater(keep.Min(), small.Max(), "the inner line's towers are tougher than the outer line's");
        }
    }
}
