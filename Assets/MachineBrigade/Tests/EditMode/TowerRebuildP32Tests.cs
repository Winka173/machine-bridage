using System;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 32 L2 (DECISIONS "Prompt 32 L0/L1/L2"): flying fallen towers back in. A rebuilt tower is outside the army
    /// value supply reads; destroying a tower pays nothing; the runtime price is the base price under Brandt's cut, rounded
    /// half up; nothing lands while an enemy stands within 20 m; the drop's fall by size; no call after Showdown's cut-off,
    /// a paid drop still landing; the HQ's one free rescue at a quarter of its health. Written, not run.
    /// </summary>
    public class TowerRebuildP32Tests
    {
        private static Catalog _catalog;
        private static Catalog C => _catalog ??= GameContent.LoadCatalog();

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0f; t < seconds && !world.IsOver; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        /// <summary>A base of one tower on Ashfield, its tower knocked down and its cooldown run out; CP to spare.</summary>
        private static (SimWorld world, TeamBase b, HardpointState slot, TeamEconomy economy) Fallen(string tower, SlotSize size)
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 5);
            world.EnableEconomy(new TeamEconomy(0, 60f, bank: 80f));
            world.EnableEconomy(new TeamEconomy(1, 30f, bank: 60f));
            var loadout = new BaseLoadout { HqLevel = 5 };
            loadout.Of(size).Add(tower);
            var b = world.Bases.Establish(0, loadout, BaseRole.Defend);
            var slot = b.Slots.First(s => s.Tower == tower);
            world.TryGetVehicle(slot.Structure, out var t);
            world.Damage.Apply(t, 1e7f, DamageType.HighExplosive);
            Run(world, C.Base.RebuildCooldown(C.Vehicles[tower]) + 0.5f);
            world.TryGetEconomy(0, out var economy);
            return (world, b, slot, economy);
        }

        private static Command Call(HardpointState slot) => new Command(CommandType.CallTower, 0, Array.Empty<EntityId>(), slot.Def.Position);

        [Test]
        public void ARebuiltTowerIsNotInTheArmyValueSupplyReads()
        {
            var (world, _, slot, economy) = Fallen("gun_turret", SlotSize.Medium);
            Run(world, 1f);
            var before = economy.ArmyCp;
            Assert.IsTrue(world.Submit(Call(slot)).Accepted);
            Run(world, C.Base.RebuildDrop(C.Vehicles["gun_turret"]) + 0.5f);
            Assert.IsTrue(world.TryGetVehicle(slot.Structure, out var back) && back.IsAlive, "it landed");
            Run(world, 1f);
            Assert.AreEqual(before, economy.ArmyCp, "the army value supply reads is unchanged");
        }

        [Test]
        public void DestroyingATowerPaysNothing()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 5);
            world.EnableEconomy(new TeamEconomy(0, 10f, bank: 80f));
            world.EnableEconomy(new TeamEconomy(1, 10f, bank: 80f));
            var b = world.Bases.Establish(0, new BaseLoadout { HqLevel = 5, Medium = { "gun_turret" } }, BaseRole.Defend);
            var slot = b.Slots.First(s => s.Tower == "gun_turret");
            world.TryGetVehicle(slot.Structure, out var tower);
            var shooter = world.SpawnVehicle("main_battle_tank", 1, slot.Def.Position + new Vector2(0f, 25f), MathF.PI);
            world.TryGetEconomy(1, out var enemy);
            enemy.Cp = 10f;
            tower.LastAttackerTeam = 1;
            tower.LastHitTime = world.Time;
            world.Damage.Apply(tower, 1e7f, DamageType.Kinetic);
            world.Economy.OnVehicleDestroyed(tower, shooter);
            Assert.AreEqual(10f, enemy.Cp, 1e-3f, "no CP for the side that destroyed it (0 %)");
        }

        [Test]
        public void TheRuntimePriceIsTheBaseUnderBrandtRoundedHalfUp()
        {
            var (world, _, slot, economy) = Fallen("heavy_flak_tower", SlotSize.Medium);
            var baseCp = world.Bases.CostOf(slot);
            Assert.AreEqual(C.Vehicles["heavy_flak_tower"].BaseRebuildCp, baseCp, "baseRebuildCP from the data");
            Assert.AreEqual(baseCp, world.Bases.RuntimeCostOf(0, slot), "no commander: the base price");
            world.SetCommander(0, Commanders.Get("brandt"));
            var runtime = world.Bases.RuntimeCostOf(0, slot);
            Assert.AreEqual(SimMath.RoundHalfUp(baseCp * 0.8), runtime, "Brandt: -20 %, rounded half up once");
            Assert.AreEqual(baseCp, world.Bases.CostOf(slot), "the base price stays for every calculation");
            economy.Cp = 40f;
            Assert.IsTrue(world.Submit(Call(slot)).Accepted);
            Assert.AreEqual(40f - runtime, economy.Cp, 1e-3f, "the side pays the runtime price as the drop starts");
        }

        [Test]
        public void NoDropWithAnEnemyWithin20m()
        {
            var (world, _, slot, economy) = Fallen("guard_tower", SlotSize.Small);
            var enemy = world.SpawnVehicle("scout_jeep", 1, slot.Def.Position + new Vector2(12f, 0f), 0f);
            world.MakeSparring(enemy);
            var result = world.Submit(Call(slot));
            Assert.IsFalse(result.Accepted);
            Assert.AreEqual(CommandError.EnemyNear, result.Error);
            Assert.IsEmpty(world.Bases.Callable(0), "nor does the AI see it as callable");
            enemy.Position = slot.Def.Position + new Vector2(25f, 0f);
            Assert.IsTrue(world.Submit(Call(slot)).Accepted, "once it is beyond 20 m");
        }

        [TestCase("guard_tower", SlotSize.Small, 2.5f)]
        [TestCase("gun_turret", SlotSize.Medium, 3.5f)]
        [TestCase("heavy_turret", SlotSize.Large, 5f)]
        public void TheDropFallsByItsSize(string tower, SlotSize size, float fall)
        {
            Assert.AreEqual(fall, C.Base.RebuildDrop(C.Vehicles[tower]), 1e-4f);
            var (world, _, slot, _) = Fallen(tower, size);
            Assert.IsTrue(world.Submit(Call(slot)).Accepted);
            Run(world, fall - 0.3f);
            Assert.IsFalse(slot.Structure.IsValid, "still falling");
            Run(world, 0.6f);
            Assert.IsTrue(world.TryGetVehicle(slot.Structure, out var back) && back.IsAlive, "landed, at full health");
            Assert.AreEqual(back.MaxHp, back.Hp, 1e-3f);
        }

        [Test]
        public void ShowdownStopsRebuildsAtMinuteTenButAPaidDropLands()
        {
            var (world, b, slot, _) = Fallen("gun_turret", SlotSize.Medium);
            Assert.AreEqual(600f, C.Base.ShowdownRebuildCutoff, 1e-3f);
            // A drop paid just before the cut-off still lands.
            world.Bases.RebuildUntil = world.Time + 0.2;
            Assert.IsTrue(world.Submit(Call(slot)).Accepted);
            Run(world, C.Base.RebuildDrop(C.Vehicles["gun_turret"]) + 0.5f);
            Assert.IsTrue(world.TryGetVehicle(slot.Structure, out var back) && back.IsAlive, "the paid drop landed after the cut-off");
            // After the cut-off: nothing more.
            world.Damage.Apply(back, 1e7f, DamageType.HighExplosive);
            Run(world, C.Base.RebuildCooldown(C.Vehicles["gun_turret"]) + 0.5f);
            Assert.IsFalse(world.Submit(Call(slot)).Accepted, "no call after the cut-off");
            Assert.IsEmpty(world.Bases.Callable(0));
        }

        [Test]
        public void TheHqRescuesItsCheapestFallenSmallOrMediumTowerOnce()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 5);
            world.EnableEconomy(new TeamEconomy(0, 0f, bank: 80f));
            var b = world.Bases.Establish(0, new BaseLoadout { HqLevel = 5, Small = { "guard_tower" }, Medium = { "gun_turret" }, Large = { "heavy_turret" } },
                BaseRole.Defend);
            foreach (var slot in b.Slots.Where(s => s.Structure.IsValid))
                if (world.TryGetVehicle(slot.Structure, out var t)) world.Damage.Apply(t, 1e7f, DamageType.HighExplosive);
            Run(world, 0.5f);
            world.TryGetVehicle(b.Hq, out var hq);
            hq.Hp = hq.MaxHp * 0.2f;
            Run(world, 0.2f);
            Assert.IsTrue(b.HqRescueUsed);
            var incoming = b.Slots.Where(s => s.Incoming).ToList();
            Assert.AreEqual(1, incoming.Count, "one tower, once");
            var cheapest = new[] { "guard_tower", "gun_turret" }.OrderBy(id => C.Base.RebuildCost(C.Vehicles[id])).First();
            Assert.AreEqual(cheapest, incoming[0].Tower, "the cheapest small or medium one, never the large");
            world.TryGetEconomy(0, out var economy);
            Assert.AreEqual(0f, economy.Cp, 1e-3f, "free, and no CP given");
        }

        [Test]
        public void TheDataPricesSitInTheirSizeBands()
        {
            foreach (var card in TowerCards.All(C))
                foreach (var id in new[] { card }.Concat(TowerCards.Branches(C, card)))
                {
                    var def = C.Vehicles[id];
                    var (lo, hi) = def.Fort.Size switch { SlotSize.Small => (3, 6), SlotSize.Medium => (5, 11), _ => (9, 18) };
                    Assert.That(def.BaseRebuildCp, Is.InRange(lo, hi), id);
                }
        }
    }
}
