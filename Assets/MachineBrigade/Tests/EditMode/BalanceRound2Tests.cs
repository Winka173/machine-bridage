using System;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Economy;

namespace MachineBrigade.Tests
{
    /// <summary>Prompt 29 pass 1 (S02, S03, S04, S09): the round-2 balance infrastructure. Written in the cloud, not yet run.</summary>
    public class BalanceRound2Tests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        [TestCase(12.5, 1, 13)]
        [TestCase(19.5, 1, 20)]
        [TestCase(12.4999, 1, 12)]
        [TestCase(2485, 10, 2490)]
        [TestCase(2484.9, 10, 2480)]
        [TestCase(4270, 10, 4270)]
        public void RoundHalfUpIsTheOneRounding(double value, double step, int expected) =>
            Assert.That(SimMath.RoundHalfUp(value, step), Is.EqualTo(expected));

        [Test]
        public void OutgoingDamageMultDefaultsToOneAndScalesOnlyTheVehicle()
        {
            foreach (var def in Catalog.Vehicles.Values)
            {
                Assert.That(def.OutgoingDamageMult, Is.GreaterThan(0f), def.Id);
                if (def.OutgoingDamageMult == 1f) continue;
                // R8: the vehicle's figure moves, its weapon's data does not.
                var w = def.Weapon;
                Assert.That(FirePower.Sustained(w, def), Is.EqualTo(FirePower.Sustained(w, null) * (w.Laid ? 1f : def.WeaponDamage) * def.OutgoingDamageMult).Within(1e-3f), def.Id);
            }
        }

        [Test]
        public void ASharedWeaponIsNeverChangedByAUnitRow()
        {
            // Every weapon carried by two or more vehicles: the round-2 manifest edits none of them (R8); this lists them.
            var carriers = Catalog.Vehicles.Values.GroupBy(v => v.Weapon.Id).Where(g => g.Count() > 1).ToList();
            Assert.That(carriers, Is.Not.Empty);
            foreach (var g in carriers)
                Assert.That(g.Select(v => v.Weapon).Distinct().Count(), Is.EqualTo(1), $"{g.Key} is one weapon for {string.Join(", ", g.Select(v => v.Id))}");
        }

        [Test]
        public void DropDelayDefaultsToTheOldDeliveryAndBaseCpIsTheCardPrice()
        {
            foreach (var def in Catalog.Vehicles.Values)
            {
                Assert.That(def.DropDelay, Is.InRange(0.5f, 30f), def.Id);
                Assert.That(def.BaseCp, Is.EqualTo(def.CpCost), def.Id);
            }
            var economy = new TeamEconomy(0);
            economy.Discounts["ifv"] = 1;
            Assert.That(economy.RuntimeCallCost("ifv", 6), Is.EqualTo(5f), "a ranked card costs less to call");
            Assert.That(Catalog.Vehicle("ifv").BaseCp, Is.EqualTo(Catalog.Vehicle("ifv").CpCost), "and keeps its base price for everything else");
        }

        [Test]
        public void TurnRatesAreDegreesInTheDataAndRadiansInTheCode()
        {
            var raw = MachineBrigade.Sim.Content.MiniJson.Parse(UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/balance").text);
            var vehicles = ((System.Collections.Generic.Dictionary<string, object>)raw)["vehicles"] as System.Collections.Generic.List<object>;
            foreach (System.Collections.Generic.Dictionary<string, object> v in vehicles)
            {
                if (!v.TryGetValue("turnRate", out var deg) || !Catalog.Vehicles.TryGetValue((string)v["id"], out var def)) continue;
                Assert.That(def.TurnRate, Is.EqualTo((float)((double)deg * Math.PI / 180.0)).Within(1e-4f), (string)v["id"]);
            }
        }
    }
}
