using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// MB_FINAL F3 (DECISIONS "MB_FINAL balance F3 (lane C)"): the ten later fixed decks READY with their rules made, the
    /// stars the rules give, Survival's minute a wave, and the ships' cruise blasts drawn Large. Written for the lead to run
    /// (agents write tests, they do not run them).
    /// </summary>
    public class MbFinalF3Tests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static MissionDef Mission(string id) => Campaign.Everything.First(m => m.Id == id);

        private static readonly string[] Ready = { "c5m03", "c6m03", "c6m14", "c7m16", "c9m12", "c10m11", "c10m12", "c12m03", "i1m01", "i2m01" };

        [Test]
        public void TheTenLaterDecksAreReadyWithTheirRules()
        {
            foreach (var id in Ready)
            {
                var deck = Mission(id).FixedDeck;
                Assert.IsNotNull(deck, id);
                Assert.AreEqual("READY", deck.Status, id);
                Assert.IsNotEmpty(deck.SpecialRules, id);
                foreach (var card in deck.Vehicles.Concat(deck.Supports))
                    Assert.IsTrue(Catalog.Vehicles.ContainsKey(card) || Catalog.TryGetSupport(card, out _), $"{id}: {card} is in the catalog");
            }
            Assert.IsFalse(Campaign.Everything.Any(m => m.FixedDeck is { Status: "MAKE_LATER" }), "no deck left MAKE_LATER");
            Assert.AreEqual("NoAlarm", Mission("i1m01").Challenge);
            Assert.AreEqual("BeforeDusk", Mission("i2m01").Challenge);
            Assert.AreEqual(600, Mission("i2m01").ChallengeValue, "dusk at the mission's 3-star time");
            Assert.AreEqual(MissionGoal.Hold, Mission("c10m11").Goal, "the landing count is a Hold clock");
            Assert.AreEqual(MissionGoal.Capture, Mission("c9m12").Goal, "island hopping over Capture points");
        }

        [Test]
        public void TheNewStarsReadTheBattle()
        {
            var noAlarm = new StarRule("NoAlarm", 0f);
            Assert.IsTrue(CampaignStars.Met(noAlarm, new StarFacts { Won = true }));
            Assert.IsFalse(CampaignStars.Met(noAlarm, new StarFacts { Won = true, AlarmRaised = true }));
            var dusk = new StarRule("BeforeDusk", 600f);
            Assert.IsTrue(CampaignStars.Met(dusk, new StarFacts { Won = true, Seconds = 599f }));
            Assert.IsFalse(CampaignStars.Met(dusk, new StarFacts { Won = true, Seconds = 601f }));
        }

        [Test]
        public void SurvivalSendsAWaveAMinute()
        {
            Assert.AreEqual(60f, SimTunables.Modes.SandboxMode.SurvivalWaveInterval, "~60 s a wave");
            Assert.AreEqual(10, SimTunables.Modes.EndlessRules.SurvivalWaves, "ten waves, unchanged");
            var lastWave = SimTunables.Modes.SandboxMode.FirstWaveDelay + 9 * SimTunables.Modes.SandboxMode.SurvivalWaveInterval;
            Assert.That(lastWave, Is.InRange(540f, 600f), "wave 10 sent by about nine and a half minutes: ~10 with its clearing");
        }

        [Test]
        public void ScyllaAndNyxCruiseBlastsAreLargeAndTheLeviathansStayUltimate()
        {
            Assert.AreEqual(ExplosionTier.Large, Catalog.Vehicles["scylla"].Cruise.ImpactTier);
            Assert.AreEqual(ExplosionTier.Large, Catalog.Vehicles["nyx"].Cruise.ImpactTier);
            Assert.AreEqual("leviathan_cruise", Catalog.Vehicles["scylla"].Cruise.Weapon, "the Kalibr, inherited: its T4 look rides on the blast");
            Assert.IsNull(Catalog.Vehicles["leviathan"].Cruise.ImpactTier, "the Leviathan's own Kalibr keeps its Ultimate");
        }
    }
}
