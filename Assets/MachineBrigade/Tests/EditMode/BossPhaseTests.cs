using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Multi-phase bosses (prompt 5, item 9): the bar stops at each phase's mark, the boss
    /// transforms untouchable for a while, then fights on with the phase's changes.
    /// </summary>
    public class BossPhaseTests
    {
        private const float Step = 0.05f;

        private static (SimWorld world, Sim.Entities.Vehicle boss) Boss()
        {
            var json = Resources.Load<TextAsset>("Data/balance").text;
            var at = json.IndexOf("\"vehicles\": [", System.StringComparison.Ordinal) + "\"vehicles\": [".Length;
            json = json.Insert(at, @"{ ""id"": ""test_phased"", ""inherits"": ""behemoth"", ""general"": ""varga"", ""phases"": [
                { ""at"": 0.33, ""transform"": 2, ""damage"": 1.5, ""skills"": [""boss_rage""], ""radio"": ""radio.test.last"" },
                { ""at"": 0.66, ""transform"": 2, ""heal"": 0.1, ""damage"": 1.2, ""speed"": 1.1, ""armor"": 0.8, ""model"": ""behemoth_inferno"", ""radio"": ""radio.test.second"" } ] },");
            var catalog = Catalog.FromJson(json);
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: 2);
            foreach (var v in world.VehicleList) v.Hp = 0f;
            world.Step(Step);
            world.ClearEvents();
            return (world, world.SpawnVehicle("test_phased", 1, new Vector2(30f, 30f), 0f));
        }

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0f; t < seconds; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void PhasesAreReadHighestMarkFirst()
        {
            var (_, boss) = Boss();
            CollectionAssert.AreEqual(new[] { 0.66f, 0.33f }, boss.Def.Phases.Select(p => p.At).ToArray());
            Assert.AreEqual("varga", boss.Def.General);
            Assert.AreEqual("boss_rage", boss.Def.Phases[1].Skills[0].Id);
        }

        [Test]
        public void AHugeBlowStopsAtTheMarkAndTheBossTransformsUntouchable()
        {
            var (world, boss) = Boss();
            world.Damage.Apply(boss, boss.MaxHp * 5f, DamageType.ShapedCharge);
            Assert.AreEqual(0.66f, boss.Hp / boss.MaxHp, 1e-3f, "what went past the mark is lost");
            Assert.IsTrue(boss.IsAlive && boss.Transforming);
            var events = world.Events.Where(e => e.Kind == SimEventKind.BossPhase).ToList();
            Assert.AreEqual(1, events.Count);
            Assert.AreEqual(2f, events[0].Value, "phase 2 begins");
            Assert.AreEqual(1, events[0].Mount, "its transformation");
            Assert.AreEqual("radio.test.second", events[0].DefId, "its general's line");
            world.ClearEvents();
            Assert.AreEqual(0f, world.Damage.Apply(boss, 1000f, DamageType.ShapedCharge), "untouchable while it changes");
        }

        [Test]
        public void AfterTheTransformationItFightsOnStronger()
        {
            var (world, boss) = Boss();
            var damage = boss.DamageBoost;
            world.Damage.Apply(boss, boss.MaxHp, DamageType.ShapedCharge);
            Run(world, 2.2f);
            Assert.IsFalse(boss.Transforming);
            Assert.AreEqual(1, boss.Phase);
            Assert.AreEqual(0.76f, boss.Hp / boss.MaxHp, 0.01f, "the phase's heal");
            Assert.AreEqual(damage * 1.2f, boss.DamageBoost, 1e-4f);
            Assert.AreEqual("behemoth_inferno", boss.Form, "its new form");
            var before = boss.Hp;
            var lost = world.Damage.Apply(boss, 100f, DamageType.ShapedCharge);
            Assert.Greater(lost, 0f, "it can be hurt again");
            Assert.Less(lost, 100f * 0.81f, "and takes a fifth less");
            Assert.AreEqual(before - lost, boss.Hp, 1e-3f);
        }

        [Test]
        public void EveryPhaseMustBeFoughtThroughBeforeItFalls()
        {
            var (world, boss) = Boss();
            for (var i = 0; i < 6 && boss.IsAlive; i++)
            {
                world.Damage.Apply(boss, boss.MaxHp * 5f, DamageType.ShapedCharge);
                Run(world, 2.2f);
            }
            Assert.IsFalse(boss.IsAlive, "down after its last phase");
            Assert.AreEqual(2, boss.Phase, "through both marks");
        }
    }
}
