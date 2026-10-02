using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Navigation;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 32 L3 (DECISIONS "Prompt 32 L3 / L7 / L9"): the base walls. The data (types, durability, breakers, the AI's
    /// type by general); every base map's lines (counts, sizes); the NavGrid kept joined with every line intact, in every
    /// INTACT/RUBBLE combination of a camp's segments (enumerated on one map, monotonic elsewhere: rubble only opens
    /// ground), large vehicles through every gate, the way back behind each line; a segment destroyed switching to RUBBLE on
    /// the next tick only; rubble slowing; the gun wall taking one of the base's own small slots; the wall breakers x1.5 on
    /// walls only; a replay and a snapshot restoring the same rubble. Written for the lead to run (agents do not run tests).
    /// </summary>
    public class WallP32Tests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static readonly string[] Variants = { "_conquest", "_siege", "_long" };

        private static IEnumerable<string> BaseMaps()
        {
            foreach (var info in MatchSettings.AllMaps)
                foreach (var v in Variants)
                    if (Resources.Load<TextAsset>("Data/maps/" + info.Id + v) != null) yield return info.Id + v;
        }

        private static BaseLoadout Walls(WallType type, int small = 6)
        {
            var loadout = BaseLoadout.ForAi(Catalog, "Normal", "default", 3, level: 5);
            loadout.Walls = new List<WallType> { type, type, type };
            return loadout;
        }

        private static int Region(NavGrid grid, Vector2 p) =>
            grid.RegionOf(p) is var r && r > 0 ? r : grid.TryNearestWalkable(p, 5, out var open) ? grid.RegionOf(open) : 0;

        private static List<Vector2> Anchors(SimWorld world) =>
            world.Map.Teams.Select(t => t.Rally).Concat(world.Map.Points.Select(p => p.Position)).Concat(world.Map.Neutrals.Select(n => n.At)).ToList();

        private static void AssertJoined(SimWorld world, string what, List<string> bad)
        {
            var anchors = Anchors(world);
            var home = Region(world.Grid, anchors[0]);
            foreach (var a in anchors)
                if (Region(world.Grid, a) != home) bad.Add($"{what}: ({a.X:0}, {a.Y:0}) cut off");
        }

        // ================================================================== data

        [Test]
        public void TheWallTypesAreInTheDataWithTheirDurability()
        {
            var walls = Catalog.Base.Walls;
            Assert.IsNull(walls.Of(WallType.None));
            foreach (var (type, durability) in new[] { (WallType.Hesco, 1.0f), (WallType.TWall, 1.6f), (WallType.GunWall, 1.2f) })
            {
                var t = walls.Of(type);
                Assert.IsNotNull(t, type.ToString());
                Assert.That(t.Durability, Is.EqualTo(durability).Within(1e-4f), type.ToString());
                Assert.IsTrue(Catalog.Vehicles.TryGetValue(t.Def, out var def), t.Def);
                Assert.IsTrue(def.Wall && def.Obstacle && def.Static, t.Def);
                Assert.AreEqual(0, def.CpCost, t.Def);
                Assert.IsNull(def.Fort, t.Def + " is no tower card");
                // The data's hp is segmentHp x durability; the catalog's MaxHp carries the toughness on top, so the ratio to HESCO's.
                var hesco = Catalog.Vehicles[walls.Of(WallType.Hesco).Def];
                Assert.That(def.MaxHp / hesco.MaxHp, Is.EqualTo(durability).Within(1e-3f), t.Def + ": health = segment health x durability");
            }
            Assert.IsTrue(walls.Of(WallType.TWall).Extra, "the T-wall builds the extra segment (the narrower gate)");
            Assert.IsTrue(walls.Of(WallType.GunWall).Gun, "the gun wall carries a small tower");
            Assert.That(walls.RubbleSlow, Is.EqualTo(0.2f).Within(1e-4f));
            Assert.AreEqual(2, walls.CampLines);
            Assert.AreEqual(3, walls.FortressLines);
        }

        [Test]
        public void TheEnemyPicksItsWallByGeneral()
        {
            var walls = Catalog.Base.Walls;
            Assert.AreEqual(WallType.TWall, walls.ForAi("brandt"));
            Assert.AreEqual(WallType.TWall, walls.ForAi("kessler"));
            Assert.AreEqual(WallType.GunWall, walls.ForAi("varga"));
            Assert.AreEqual(WallType.Hesco, walls.ForAi("orlov"));
            Assert.AreEqual(WallType.Hesco, walls.ForAi("default"));
            var ai = BaseLoadout.ForAi(Catalog, "Normal", "brandt", 1);
            Assert.AreEqual(WallType.TWall, ai.WallFor(0));
            Assert.AreEqual(WallType.TWall, ai.WallFor(1));
            Assert.AreEqual(WallType.None, new BaseLoadout().WallFor(0), "a loadout made in code has no walls");
        }

        [Test]
        public void TheWallBreakersHitWallsOneAndAHalfTimesAndNothingElse()
        {
            var world = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), 1);
            foreach (var id in Catalog.Base.WallBreakers)
            {
                Assert.IsTrue(Catalog.Vehicles[id].WallBreaker, id);
                Assert.That(Catalog.Vehicles[id].WallBreakerScale, Is.EqualTo(1.5f).Within(1e-4f), id);
            }
            Assert.IsFalse(Catalog.Vehicles["main_battle_tank"].WallBreaker);
            var dozer = world.SpawnVehicle("engineer_vehicle", 0, new Vector2(0f, 0f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(4f, 0f), 0f);
            var wall = world.SpawnVehicle("wall_hesco", 1, new Vector2(0f, 20f), 0f);
            var tower = world.SpawnVehicle("guard_tower", 1, new Vector2(20f, 20f), 0f);
            var onWall = DamageSystem.BonusFor(dozer.Weapon, dozer, wall, world.Time);
            var onTower = DamageSystem.BonusFor(dozer.Weapon, dozer, tower, world.Time);
            Assert.GreaterOrEqual(onWall, onTower);
            if (dozer.Weapon.Bonuses.Count == 0) Assert.That(onWall / onTower, Is.EqualTo(1.5f).Within(0.01f), "x1.5 on a wall, not on a tower");
            Assert.That(DamageSystem.BonusFor(tank.Weapon, tank, wall, world.Time), Is.EqualTo(DamageSystem.BonusFor(tank.Weapon, tank, tower, world.Time)).Within(1e-4f),
                "no bonus for a vehicle that is no wall breaker");
        }

        // ================================================================== the maps' lines

        [Test]
        public void EveryBaseMapsLinesHaveThreeToFiveSegmentsAndAGate()
        {
            var bad = new List<string>();
            var lines = 0;
            foreach (var id in BaseMaps())
            {
                var map = GameContent.LoadMap(id);
                foreach (var group in map.Walls.GroupBy(l => l.Owner))
                {
                    var max = group.Key == "fortress" ? 3 : 2;
                    if (group.Count() > max) bad.Add($"{id} {group.Key}: {group.Count()} lines (at most {max})");
                    if (group.Select(l => l.Ring).Distinct().Count() != group.Count()) bad.Add($"{id} {group.Key}: a ring twice");
                }
                foreach (var l in map.Walls)
                {
                    lines++;
                    var plain = l.Segments.Count(s => !s.Extra);
                    if (l.Segments.Count < 3 || l.Segments.Count > 5 || plain < 3) bad.Add($"{id} {l.Owner} ring {l.Ring}: {l.Segments.Count} segments ({plain} plain)");
                    if (l.Segments.Count(s => s.Extra) > 1 || l.Segments.Count(s => s.Gun) != 1) bad.Add($"{id} {l.Owner} ring {l.Ring}: extra / gun segments");
                    if (l.GateWidth < 12f) bad.Add($"{id} {l.Owner} ring {l.Ring}: gate {l.GateWidth} m");
                    foreach (var s in l.Segments)
                        if (s.Length < 11.9f || System.MathF.Min(s.Width, s.Depth) > 2.1f) bad.Add($"{id} {l.Owner} ring {l.Ring}: a segment {s.Width} x {s.Depth}");
                }
            }
            Assert.Greater(lines, 100, "the base maps have wall lines (Tools/maps/p32_walls.py)");
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        /// <summary>Both camps (or the fortress) built with T-walls (every segment, the extra too) and gun walls' towers.</summary>
        private static SimWorld Built(string id, WallType type, out List<WallLine> lines)
        {
            var world = new SimWorld(Catalog, GameContent.LoadMap(id), 1);
            var map = world.Map;
            lines = new List<WallLine>();
            foreach (var b in map.Bases)
                lines.AddRange(world.Bases.Establish(b.Team, Walls(type), BaseRole.Target).Walls);
            if (map.Fortress is { Slots: { Count: > 0 } } f)
                lines.AddRange(world.Bases.EstablishFortress(1, Walls(type), BaseRole.Defend, f.Hq, f.Slots).Walls);
            return world;
        }

        [Test]
        public void EveryLineIntactKeepsTheBattlefieldJoinedOnEveryBaseMap()
        {
            var bad = new List<string>();
            foreach (var id in BaseMaps())
                foreach (var type in new[] { WallType.TWall, WallType.GunWall })
                {
                    var world = Built(id, type, out var lines);
                    bad.AddRange(world.Walls.Problems.Select(p => $"{id} {type}: {p}"));
                    if (world.Map.Walls.Count > 0 && lines.Count == 0) bad.Add($"{id} {type}: no line built");
                    AssertJoined(world, $"{id} {type} intact", bad);
                }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [Test]
        public void EveryInactAndRubbleCombinationOfACampKeepsTheBattlefieldJoined()
        {
            // Every combination of one camp's segments (both lines, the T-wall's extra included) on the grid as it loads.
            var bad = new List<string>();
            var world = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), 1);
            var lines = world.Map.WallsOf("camp0");
            var blocks = lines.SelectMany(l => l.Segments).Select(s => new NavBlock(s.Center, s.Width, s.Depth)).ToList();
            Assert.Greater(blocks.Count, 5);
            Assert.LessOrEqual(blocks.Count, 10);
            for (var mask = 0; mask < 1 << blocks.Count; mask++)
            {
                for (var i = 0; i < blocks.Count; i++)
                    if ((mask & (1 << i)) != 0) world.Grid.Mark(blocks[i], +1);
                AssertJoined(world, $"combination {mask}", bad);
                for (var i = 0; i < blocks.Count; i++)
                    if ((mask & (1 << i)) != 0) world.Grid.Mark(blocks[i], -1);
                if (bad.Count > 5) break;
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [Test]
        public void EveryRubbleSegmentSwitchedInForRealKeepsTheBattlefieldJoined()
        {
            var bad = new List<string>();
            foreach (var id in new[] { "ashfield_conquest", "foundry_siege", "metrocity_long" })
            {
                var world = Built(id, WallType.TWall, out var lines);
                foreach (var seg in lines.SelectMany(l => l.Segments).ToList())
                {
                    if (world.TryGetVehicle(seg.Entity, out var v)) world.Damage.Apply(v, 1e7f, DamageType.HighExplosive);
                    world.Step(Dt);
                    Assert.AreEqual(WallSystem.RubbleState, world.NavStates.ActiveOf(seg.Site), $"{id} {seg.Site}");
                    AssertJoined(world, $"{id} {seg.Site} rubble", bad);
                }
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [Test]
        public void LargeVehiclesFitThroughEveryGateAndEveryLineHasAWayBack()
        {
            var widest = Catalog.Vehicles.Values.Where(d => d.Card && !d.Static && !d.Flying && !d.Boss && d.Naval == null).Max(d => d.Width);
            // The narrowest gate (a T-wall's, the extra closing half): 12 m less the obstacle clearance either side.
            var open = 12f - 2f * SimWorld.ObstacleClearance;
            Assert.Less(widest + 2f, open, $"the widest ground card ({widest} m) fits a T-wall's gate ({open} m clear)");
            var bad = new List<string>();
            foreach (var id in BaseMaps())
            {
                var world = Built(id, WallType.TWall, out var lines);
                foreach (var line in lines)
                {
                    var rally = line.Team is 0 or 1 && world.TryGetRally(line.Team, out var r) ? r : line.Hq;
                    var home = Region(world.Grid, rally);
                    var outside = Region(world.Grid, line.Def.Gate + Vector2.Normalize(line.Def.Gate - line.Hq) * 8f);
                    if (outside == 0 || outside != home) bad.Add($"{id} team {line.Team} ring {line.Ring}: the gate does not lead in");
                    // The way back: from in front of every segment to the side's own rally.
                    foreach (var s in line.Segments)
                        if (Region(world.Grid, s.Def.Out(4f)) != home) bad.Add($"{id} team {line.Team} {s.Site}: no way back from in front of it");
                }
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        // ================================================================== the state

        [Test]
        public void ASegmentGoesToRubbleOnTheNextTickOnlyAndNothingRunsEveryTick()
        {
            var world = Built("ashfield_conquest", WallType.Hesco, out var lines);
            Assert.Greater(lines.Count, 0);
            for (var i = 0; i < 200; i++) world.Step(Dt);
            Assert.AreEqual(0, world.NavStates.Switches, "no switch without a segment falling");
            var seg = lines[0].Segments[0];
            Assert.IsTrue(world.TryGetVehicle(seg.Entity, out var v));
            world.Damage.Apply(v, 1e7f, DamageType.HighExplosive);
            Assert.IsTrue(seg.Rubble);
            Assert.AreEqual(WallSystem.Intact, world.NavStates.ActiveOf(seg.Site), "the ground opens at a tick boundary, not mid-step");
            Assert.IsFalse(world.Grid.IsWalkable(seg.Center));
            world.Step(Dt);
            Assert.AreEqual(WallSystem.RubbleState, world.NavStates.ActiveOf(seg.Site));
            Assert.IsTrue(world.Grid.IsWalkable(seg.Center));
            Assert.AreEqual(1, world.NavStates.Switches);
            Assert.IsTrue(world.Walls.InRubble(seg.Center));
        }

        [Test]
        public void RubbleSlowsGroundVehiclesByAFifth()
        {
            var world = Built("ashfield_conquest", WallType.Hesco, out var lines);
            var seg = lines[0].Segments[0];
            world.TryGetVehicle(seg.Entity, out var v);
            world.Damage.Apply(v, 1e7f, DamageType.HighExplosive);
            world.Step(Dt);
            var tank = world.SpawnVehicle("main_battle_tank", 1, seg.Center, 0f);
            tank.Position = seg.Center;
            for (var i = 0; i < 20; i++) world.Step(Dt);
            var slow = tank.Statuses[(int)StatusKind.Slow];
            Assert.Greater(slow.Until, world.Time, "slowed while on the rubble");
            Assert.That(slow.Value, Is.EqualTo(0.2f).Within(1e-4f));
        }

        [Test]
        public void AGunWallTakesOneOfTheBasesOwnSmallSlots()
        {
            var plain = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), 1);
            var withWalls = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), 1);
            var a = plain.Bases.Establish(0, Walls(WallType.None), BaseRole.Target);
            var b = withWalls.Bases.Establish(0, Walls(WallType.GunWall), BaseRole.Target);
            Assert.AreEqual(a.Slots.Count(s => s.Tower != null), b.Slots.Count(s => s.Tower != null), "no free slot: as many towers as without walls");
            var guns = b.Walls.Where(l => l.Gun != null).ToList();
            Assert.Greater(guns.Count, 0);
            foreach (var line in guns)
            {
                Assert.IsTrue(line.Gun.OnWall);
                Assert.AreEqual(SlotSize.Small, line.Gun.Def.Class);
                var seg = line.Segments.First(s => s.Def.Gun);
                Assert.That(Vector2.Distance(line.Gun.Def.Position, seg.Center), Is.LessThan(0.01f));
                Assert.IsTrue(withWalls.TryGetVehicle(line.Gun.Structure, out var tower) && tower.IsAlive);
                Assert.That(Vector2.Distance(tower.Position, seg.Center), Is.LessThan(0.01f), "the tower stands on its wall");
                // The wall falls: its tower comes down with it.
                withWalls.TryGetVehicle(seg.Entity, out var wall);
                withWalls.Damage.Apply(wall, 1e7f, DamageType.HighExplosive);
                Assert.IsFalse(tower.IsAlive);
            }
        }

        [Test]
        public void ALineThatWouldCutTheBattlefieldIsNotBuilt()
        {
            var map = GameContent.LoadMap("ashfield_conquest");
            var world = new SimWorld(Catalog, map, 1);
            // A line straight across the whole battlefield through the middle: the rallies would be cut apart.
            var segs = new List<WallSegmentDef>();
            for (var x = -150f; x < 150f; x += 12f) segs.Add(new WallSegmentDef(new Vector2(x + 6f, 0f), 12f, 2f, 0f, false, x < -140f));
            var cutting = new WallLineDef("camp9", 1, 300f, new Vector2(0f, 0f), 24f, segs);
            var built = world.Walls.Build(0, new[] { cutting }, Walls(WallType.Hesco), new Vector2(0f, -100f));
            Assert.AreEqual(0, built.Count);
            Assert.AreEqual(1, world.Walls.Problems.Count);
            Assert.AreEqual(0, world.NavStates.Sites.Count, "nothing defined for a refused line");
        }

        // ================================================================== replay and loads

        private static SimWorld Battle(int seed, int fallAt, out List<WallLine> lines)
        {
            var world = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), seed);
            lines = new List<WallLine>();
            foreach (var b in world.Map.Bases)
                lines.AddRange(world.Bases.Establish(b.Team, Walls(WallType.TWall), BaseRole.Target).Walls);
            for (var i = 0; i < 120; i++)
            {
                if (i == fallAt)
                    foreach (var seg in lines.SelectMany(l => l.Segments).Where((_, k) => k % 3 == 0).ToList())
                        if (world.TryGetVehicle(seg.Entity, out var v)) world.Damage.Apply(v, 1e7f, DamageType.HighExplosive);
                world.Step(Dt);
            }
            return world;
        }

        [Test]
        public void AReplayEndsWithTheSameWallsAndTheSameFingerprint()
        {
            var a = Battle(7, 40, out var la);
            var b = Battle(7, 40, out var lb);
            Assert.AreEqual(a.StateHash(), b.StateHash());
            CollectionAssert.AreEqual(a.Walls.Snapshot(), b.Walls.Snapshot());
            foreach (var site in a.NavStates.Sites)
                Assert.AreEqual(site.ActiveName, b.NavStates.ActiveOf(site.Id), site.Id);
            Assert.Greater(a.Walls.Snapshot().Count, 0);
        }

        [Test]
        public void ASnapshotRestoresTheRubble()
        {
            var a = Battle(3, 10, out _);
            var b = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), 3);
            foreach (var m in b.Map.Bases) b.Bases.Establish(m.Team, Walls(WallType.TWall), BaseRole.Target);
            b.Walls.Restore(a.Walls.Snapshot());
            CollectionAssert.AreEqual(a.Walls.Snapshot(), b.Walls.Snapshot());
            foreach (var site in a.NavStates.Sites)
            {
                Assert.AreEqual(site.ActiveName, b.NavStates.ActiveOf(site.Id), site.Id);
                var seg = b.Walls.Lines.SelectMany(l => l.Segments).First(s => s.Site == site.Id);
                Assert.AreEqual(site.ActiveName == WallSystem.RubbleState, b.Grid.IsWalkable(seg.Center), site.Id);
            }
        }

        [Test]
        public void ThePlayersWallsComeFromTheSave()
        {
            var types = PlayerProfile.WallTypes();
            Assert.AreEqual(PlayerProfile.WallLines, types.Count);
            Assert.AreEqual(WallType.Hesco, WallRules.Next(WallType.None));
            Assert.AreEqual(WallType.TWall, WallRules.Next(WallType.Hesco));
            Assert.AreEqual(WallType.GunWall, WallRules.Next(WallType.TWall));
            Assert.AreEqual(WallType.None, WallRules.Next(WallType.GunWall));
            foreach (WallType t in System.Enum.GetValues(typeof(WallType)))
            {
                Assert.IsTrue(WallRules.TryParse(WallRules.Key(t), out var back));
                Assert.AreEqual(t, back);
            }
        }
    }
}
