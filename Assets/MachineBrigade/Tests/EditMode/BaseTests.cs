using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Bases as a loadout: the HQ, fortification points by HQ level, towers in the map's
    /// hardpoints, flying destroyed towers back in, roles by mode, the fire-support rule, outposts,
    /// the AI's own base, and that battles with bases stay deterministic.
    /// </summary>
    public class BaseTests
    {
        [TearDown]
        public void RestoreProfile() => PlayerProfile.Load();

        [Test]
        public void AnOldPointLoadoutIsSortedIntoTheSizedSlots()
        {
            // A saved base from the fortification-point days: one list, heavy towers first.
            PlayerProfile.LoadForTests("{\"baseLevel\":5,\"baseTowers\":[\"heavy_turret\",\"missile_battery\",\"drone_hangar\",\"gun_turret\",\"rocket_turret\",\"gun_turret\",\"atgm_tower\",\"aa_turret\",\"guard_tower\"]}");
            var loadout = PlayerProfile.BaseLoadout;
            Assert.AreEqual(5, loadout.HqLevel);
            CollectionAssert.AreEqual(new[] { "heavy_turret", "missile_battery" }, loadout.Large, "the heavy towers take the two large slots");
            CollectionAssert.AreEqual(new[] { "gun_turret", "rocket_turret", "gun_turret" }, loadout.Medium, "the medium ones the medium slots");
            CollectionAssert.AreEqual(new[] { "aa_turret", "guard_tower" }, loadout.Small, "the light ones the small slots");
            Assert.IsFalse(loadout.Towers.Contains("drone_hangar") || loadout.Towers.Contains("atgm_tower"),
                "what finds no slot is left out (its card keeps its rank and gear)");
            var json = PlayerProfile.JsonForTests();
            PlayerProfile.LoadForTests(json);
            CollectionAssert.AreEqual(new[] { "heavy_turret", "missile_battery" }, PlayerProfile.BaseLoadout.Large, "moved once, saved sized");
        }

        private static Catalog Catalog => GameContent.LoadCatalog();

        private static void Run(SimWorld world, float seconds, IGameMode mode = null, params ConquestAi[] ais)
        {
            for (var t = 0f; t < seconds && !world.IsOver; t += TestWorlds.Step)
            {
                mode?.Tick(world, TestWorlds.Step);
                foreach (var ai in ais) ai.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void HqLevelsOpenSizedSlots()
        {
            var rules = Catalog.Base;
            int[] Of(SlotSize size) => Enumerable.Range(1, 5).Select(l => rules.Slots(l, size)).ToArray();
            CollectionAssert.AreEqual(new[] { 3, 4, 4, 5, 6 }, Of(SlotSize.Small));
            CollectionAssert.AreEqual(new[] { 1, 2, 2, 3, 3 }, Of(SlotSize.Medium));
            CollectionAssert.AreEqual(new[] { 0, 0, 1, 1, 2 }, Of(SlotSize.Large));
            CollectionAssert.AreEqual(new[] { 1, 1, 2, 2, 3 }, Enumerable.Range(1, 5).Select(l => rules.UtilitySlots(l)).ToArray());
            var catalog = Catalog;
            var loadout = new BaseLoadout
            {
                HqLevel = 1,
                Small = { "guard_tower", "gun_turret", "aa_turret", "mg_bunker", "guard_tower" },
                Medium = { "heavy_turret", "rocket_turret", "gun_turret" },
                Large = { "missile_battery" },
            }.Fitted(catalog);
            CollectionAssert.AreEqual(new[] { "guard_tower", "aa_turret", "mg_bunker" }, loadout.Small, "3 small slots, light towers only");
            CollectionAssert.AreEqual(new[] { "rocket_turret" }, loadout.Medium, "1 medium slot, no heavy tower in it");
            Assert.IsEmpty(loadout.Large, "no large slot at level 1");
        }

        [Test]
        public void TowerSizesFollowTheRoster()
        {
            var catalog = Catalog;
            foreach (var (id, size) in new[]
                     {
                         ("guard_tower", SlotSize.Small), ("mg_bunker", SlotSize.Small), ("aa_turret", SlotSize.Small),
                         ("gun_turret", SlotSize.Medium), ("rocket_turret", SlotSize.Medium), ("atgm_tower", SlotSize.Medium),
                         ("drone_hangar", SlotSize.Large), ("missile_battery", SlotSize.Large), ("heavy_turret", SlotSize.Large),
                     })
                Assert.AreEqual(size, catalog.Vehicles[id].Fort.Size, id);
            Assert.IsTrue(catalog.Vehicles["guard_tower"].Fort.Fits(SlotSize.Large), "a light tower goes anywhere");
            Assert.IsFalse(catalog.Vehicles["heavy_turret"].Fort.Fits(SlotSize.Medium), "a heavy one only into a large slot");
        }

        [Test]
        public void TheLoadoutFillsTheHardpointsFrontFirst()
        {
            var world = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            var site = world.Map.BaseOf(0);
            Assert.IsNotNull(site, "the map has a camp for side 0");
            var loadout = new BaseLoadout { HqLevel = 3, Small = { "aa_turret", "guard_tower" }, Medium = { "gun_turret" }, Large = { "heavy_turret" } };
            var b = world.Bases.Establish(0, loadout, BaseRole.Anchor);
            var towers = world.Bases.Towers(0).ToList();
            Assert.AreEqual(4, towers.Count, "every tower in the loadout stands");
            Assert.AreEqual(7, b.Slots.Count(s => s.Def.Kind == HardpointKind.Tower), "level 3 opens 4 small, 2 medium and 1 large hardpoint");
            HardpointState First(SlotSize size) => b.Slots.First(s => s.Def.Kind == HardpointKind.Tower && s.Def.Class == size);
            Assert.AreEqual("aa_turret", First(SlotSize.Small).Tower, "the first small tower in the first small hardpoint");
            Assert.AreEqual("gun_turret", First(SlotSize.Medium).Tower);
            Assert.AreEqual("heavy_turret", First(SlotSize.Large).Tower);
            Assert.IsTrue(towers.All(t => b.Slots.Any(s => Vector2.Distance(s.Def.Position, t.Position) < 0.01f)), "each on a hardpoint");
            Assert.IsTrue(world.VehicleList.Any(v => v.Id == b.Hq && v.Invulnerable), "an Anchor HQ, which cannot fall");
        }

        [Test]
        public void ADestroyedTowerIsFlownBackInForCpAfterItsCooldown()
        {
            var catalog = Catalog;
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            world.EnableEconomy(new MachineBrigade.Sim.Economy.TeamEconomy(0, 30f, bank: 60f));
            var b = world.Bases.Establish(0, new BaseLoadout { HqLevel = 5, Medium = { "gun_turret" } }, BaseRole.Anchor);
            var slot = b.Slots.First(s => s.Tower == "gun_turret");
            world.TryGetVehicle(slot.Structure, out var tower);
            world.Damage.Apply(tower, 1e7f, DamageType.HighExplosive);
            Run(world, 1f);
            Assert.IsTrue(slot.Down, "the hardpoint is down");
            var call = new Command(CommandType.CallTower, 0, Array.Empty<EntityId>(), slot.Def.Position);
            Assert.IsFalse(world.Submit(call).Accepted, "not before its cooldown");
            Run(world, catalog.Base.RebuildCooldown(catalog.Vehicles["gun_turret"]));
            world.TryGetEconomy(0, out var economy);
            economy.Cp = 20f;
            Assert.IsTrue(world.Submit(call).Accepted, "after it");
            Assert.AreEqual(20f - catalog.Base.RebuildCost(catalog.Vehicles["gun_turret"]), economy.Cp, 0.5f, "for its price in CP");
            // Prompt 32 L2: each tower's own baseRebuildCP (Tools/balance/p32_tower_prices.py), within the medium band 5-11.
            Assert.AreEqual(catalog.Vehicles["gun_turret"].BaseRebuildCp, catalog.Base.RebuildCost(catalog.Vehicles["gun_turret"]), "its own price");
            Assert.That(catalog.Base.RebuildCost(catalog.Vehicles["gun_turret"]), Is.InRange(5, 11), "a medium tower");
            Assert.Less(catalog.Base.RebuildCost(catalog.Vehicles["guard_tower"]), catalog.Base.RebuildCost(catalog.Vehicles["heavy_turret"]), "a light tower is cheaper to fly back");
            Assert.Less(catalog.Base.RebuildCooldown(catalog.Vehicles["guard_tower"]), catalog.Base.RebuildCooldown(catalog.Vehicles["heavy_turret"]), "and sooner");
            Run(world, catalog.Base.RebuildDelay + 0.5f);
            Assert.IsTrue(world.TryGetVehicle(slot.Structure, out var back) && back.IsAlive && back.Def.Id == "gun_turret", "it lands in its hardpoint");
            Assert.IsFalse(world.Submit(call).Accepted, "a standing tower cannot be called again");
        }

        [Test]
        public void AssaultsDefendingHqIsTheTargetAndCanBeShelled()
        {
            var world = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), seed: 4);
            var mode = new AssaultMode(new AssaultRules());
            mode.Setup(world);
            var hq = world.Bases.Of(mode.Defender);
            Assert.AreEqual(BaseRole.Target, hq.Role);
            world.TryGetVehicle(hq.Hq, out var building);
            Assert.IsFalse(building.Invulnerable, "the defending HQ can be destroyed");
            Assert.AreEqual(BaseRole.Anchor, world.Bases.RoleOf(mode.Attacker));
            if (world.TryGetEconomy(mode.Attacker, out var economy)) economy.Cp = 100f;
            Assert.IsTrue(world.Submit(Command.Strike(mode.Attacker, "artillery_barrage", hq.HqPosition)).Accepted, "fire support may be called on a base that is the objective");
            world.Damage.Apply(building, 1e8f, DamageType.HighExplosive);
            Run(world, 1f, mode);
            Assert.AreEqual(mode.Attacker, mode.Result?.WinningTeam, "destroying it wins the assault");
        }

        [Test]
        public void TheBaseRolesComeFromTheData()
        {
            var rules = Catalog.Base;
            Assert.AreEqual(BaseRole.Anchor, rules.RoleFor("Conquest"));
            Assert.AreEqual(BaseRole.Anchor, rules.RoleFor("KingOfTheHill"));
            Assert.AreEqual(BaseRole.Anchor, rules.RoleFor("Deathmatch"));
            Assert.AreEqual(BaseRole.Target, rules.RoleFor("Assault"));
            Assert.AreEqual(BaseRole.Target, rules.RoleFor("Siege"));
            Assert.AreEqual(BaseRole.Defend, rules.RoleFor("Defend"));
            Assert.AreEqual(BaseRole.Defend, rules.RoleFor("Endless"));
            Assert.AreEqual(BaseRole.None, rules.RoleFor("Survival"));
        }

        [Test]
        public void AnOutpostOnATakenPointTakesTowersAndBecomesTheDropZone()
        {
            var catalog = Catalog;
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: 5);
            var point = world.Map.Points.First(p => p.Outpost.Count > 0);
            var owner = -1;
            world.EnableEconomy(new MachineBrigade.Sim.Economy.TeamEconomy(0, 60f, bank: 60f));
            world.Bases.Ensure(0, new BaseLoadout());
            world.Bases.OutpostPoints.Add(point.Id);
            world.Bases.PointOwner = id => id == point.Id ? owner : -1;
            var setUp = new Command(CommandType.Outpost, 0, Array.Empty<EntityId>(), defId: point.Id);
            Assert.IsFalse(world.Submit(setUp).Accepted, "not on a point we do not hold");
            owner = 0;
            Assert.IsTrue(world.Submit(setUp).Accepted, "on one we hold");
            var slots = world.Bases.Of(0).Outposts[point.Id];
            Assert.That(slots.Count, Is.InRange(1, 2), "one or two hardpoints");
            Assert.IsTrue(world.Submit(new Command(CommandType.CallTower, 0, Array.Empty<EntityId>(), slots[0].Def.Position, defId: "guard_tower")).Accepted,
                "a tower flown onto it");
            Run(world, catalog.Base.RebuildDelay + 0.5f);
            Assert.IsTrue(world.Bases.Towers(0).Any(), "it stands");
            world.Bases.TryGetDropZone(0, out var zone);
            Assert.Less(Vector2.Distance(zone, point.Position), 1f, "bought vehicles land at the outpost");
            owner = 1;
            Run(world, 0.5f);
            Assert.IsFalse(world.Bases.Towers(0).Any(), "a lost point takes its outpost with it");
        }

        [Test]
        public void TheAiDrawsItsOwnBaseWithinItsBudget()
        {
            var catalog = Catalog;
            foreach (var difficulty in new[] { "Easy", "Normal", "Hard" })
                foreach (var style in catalog.Base.StyleNames)
                {
                    var a = BaseLoadout.ForAi(catalog, difficulty, style, 7);
                    var b = BaseLoadout.ForAi(catalog, difficulty, style, 7);
                    CollectionAssert.AreEqual(a.Towers.ToList(), b.Towers.ToList(), "the same seed, the same base");
                    foreach (SlotSize size in Enum.GetValues(typeof(SlotSize)))
                    {
                        Assert.LessOrEqual(a.Of(size).Count, catalog.Base.Slots(a.HqLevel, size), $"{difficulty}/{style}: no more {size} towers than slots");
                        Assert.IsTrue(a.Of(size).All(t => catalog.Vehicles[t].Fort.Fits(size)), $"{difficulty}/{style}: each fits its {size} slot");
                    }
                    Assert.Greater(a.Towers.Count(), 0, $"{difficulty}/{style} builds something");
                    if (a.HqLevel >= 3)
                        Assert.IsTrue(a.Towers.Any(t => catalog.Vehicles[t].Mounts.Any(m => m.Weapon.CanTarget(true) && m.Weapon.DamageType == DamageType.Fragmentation)),
                            $"{difficulty}/{style} brings anti-air");
                }
            Assert.Less(catalog.Base.AiLevel("Easy"), catalog.Base.AiLevel("Hard"), "a harder enemy has the bigger HQ");
        }

        [Test]
        public void ABattleWithBasesIsDeterministic()
        {
            long Play()
            {
                var catalog = Catalog;
                var world = new SimWorld(catalog, GameContent.LoadMap("greenvale_conquest"), seed: 9);
                var bases = new BaseSetup().Set(0, BaseLoadout.ForAi(catalog, "Normal", "armour", 3), BaseRole.Anchor)
                    .Set(1, BaseLoadout.ForAi(catalog, "Hard", "air", 4), BaseRole.Anchor);
                var mode = new ConquestMode(new ConquestRules { Bases = bases });
                mode.Setup(world);
                var ai0 = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 5);
                var ai1 = new ConquestAi(mode, 1, 0, AiDifficulty.Hard, 6);
                long hash = 17;
                for (var i = 0; i < 4 * 60 * 20 && !world.IsOver; i++)
                {
                    mode.Tick(world, TestWorlds.Step);
                    ai0.Tick(world, TestWorlds.Step);
                    ai1.Tick(world, TestWorlds.Step);
                    world.Step(TestWorlds.Step);
                    world.ClearEvents();
                    if (i % 100 != 0) continue;
                    foreach (var v in world.VehicleList)
                        hash = hash * 31 + (long)(v.Position.X * 100f) * 7 + (long)(v.Position.Y * 100f) + (long)v.Hp;
                }
                return hash;
            }
            Assert.AreEqual(Play(), Play(), "same seed, same battle, bases and all");
        }

        /// <summary>
        /// Tower sense, measured (run by hand with MB_BALANCE=1): Conquest battles between two AI
        /// commanders with full bases, with and without it; the share of the vehicles lost that died
        /// inside an enemy tower's reach with fewer than two friends near must fall.
        /// </summary>
        [Test, Category("Balance")]
        public void TheAiStopsFeedingVehiclesIntoTowers()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance check: set MB_BALANCE=1 to run it");
            var before = TowerDeaths(false, out var lostBefore, out var loneBefore);
            var after = TowerDeaths(true, out var lostAfter, out var loneAfter);
            Debug.Log($"TOWERS before: {before:P0} of {lostBefore} losses in tower reach, lone {loneBefore:P0}; after: {after:P0} of {lostAfter}, lone {loneAfter:P0}");
            Assert.LessOrEqual(after, before, "no more of the army dies under the towers");
            Assert.LessOrEqual(loneAfter, loneBefore, "and fewer go in alone");
        }

        private static float TowerDeaths(bool sense, out int lost, out float lone)
        {
            TacticalAi.TowerSense = sense;
            var inReach = 0;
            var alone = 0;
            lost = 0;
            try
            {
                foreach (var map in new[] { "ashfield_conquest", "greenvale_conquest", "dunebreak_conquest" })
                    for (var seed = 1; seed <= 5; seed++)
                    {
                        var catalog = Catalog;
                        var world = new SimWorld(catalog, GameContent.LoadMap(map), seed: seed);
                        var bases = new BaseSetup().Set(0, BaseLoadout.ForAi(catalog, "Hard", "default", seed), BaseRole.Anchor)
                            .Set(1, BaseLoadout.ForAi(catalog, "Hard", "armour", seed + 11), BaseRole.Anchor);
                        var deck = new[] { "main_battle_tank", "light_tank", "ifv", "armored_car", "tank_destroyer", "mlrs", "aa_vehicle", "artillery" };
                        var mode = new ConquestMode(new ConquestRules
                        {
                            Bases = bases, PlayerVehicles = deck, EnemyVehicles = deck,
                            PlayerSupports = Array.Empty<string>(), EnemySupports = Array.Empty<string>(),
                        });
                        mode.Setup(world);
                        var ais = new[] { new ConquestAi(mode, 0, 1, AiDifficulty.Hard, seed), new ConquestAi(mode, 1, 0, AiDifficulty.Hard, seed + 3) };
                        for (var i = 0; i < 9 * 60 * 20 && !world.IsOver; i++)
                        {
                            mode.Tick(world, TestWorlds.Step);
                            foreach (var ai in ais) ai.Tick(world, TestWorlds.Step);
                            world.Step(TestWorlds.Step);
                            foreach (var e in world.Events)
                            {
                                if (e.Kind != Sim.Events.SimEventKind.VehicleDestroyed || e.DefId == null || !catalog.Vehicles.TryGetValue(e.DefId, out var dead) ||
                                    dead.Static || dead.Flying) continue;
                                lost++;
                                var covered = false;
                                foreach (var t in world.VehicleList)
                                {
                                    if (!t.IsAlive || !t.Def.Static || t.Team == e.Team || t.Team < 0) continue;
                                    var reach = t.Def.Mounts.Where(m => m.Weapon.CanTarget(false)).Select(m => m.Weapon.Range).DefaultIfEmpty(0f).Max() + t.Radius;
                                    if (Vector2.Distance(t.Position, e.Position) < reach) covered = true;
                                }
                                if (!covered) continue;
                                inReach++;
                                var friends = world.VehicleList.Count(f => f.IsAlive && f.Id != e.Entity && f.Team == e.Team && !f.Def.Static && Vector2.Distance(f.Position, e.Position) < 20f);
                                if (friends < 2) alone++;
                            }
                            world.ClearEvents();
                        }
                    }
            }
            finally
            {
                TacticalAi.TowerSense = true;
            }
            lone = lost > 0 ? (float)alone / lost : 0f;
            return lost > 0 ? (float)inReach / lost : 0f;
        }
    }
}
