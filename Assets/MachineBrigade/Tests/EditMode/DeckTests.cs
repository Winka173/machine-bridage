using System.Collections.Generic;
using MachineBrigade.Game.Match;
using NUnit.Framework;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The deck keeps each card in its slot: taking one out leaves that slot empty (the others do
    /// not slide along, which read as the wrong card leaving), and the last card of a kind stays.
    /// </summary>
    public class DeckTests
    {
        private List<string> _vehicles, _supports;

        [SetUp]
        public void SetUp()
        {
            _vehicles = new List<string>(MatchSettings.DeckVehicles);
            _supports = new List<string>(MatchSettings.DeckSupports);
        }

        [TearDown]
        public void TearDown()
        {
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(_vehicles);
            MatchSettings.DeckSupports.Clear();
            MatchSettings.DeckSupports.AddRange(_supports);
            MatchSettings.DeckLayout(false);
            MatchSettings.DeckLayout(true);
        }

        private static void Supports(params string[] ids)
        {
            MatchSettings.DeckSupports.Clear();
            MatchSettings.DeckLayout(true);
            MatchSettings.DeckSupports.AddRange(ids);
            MatchSettings.DeckLayout(true);
        }

        [Test]
        public void TakingOutTheFirstSupportLeavesTheSecondInItsSlot()
        {
            Supports("artillery_barrage", "cruise_missile");
            Assert.That(MatchSettings.ToggleDeckCard("artillery_barrage", true), Is.EqualTo(MatchSettings.DeckChange.Removed));
            var layout = MatchSettings.DeckLayout(true);
            Assert.That(layout[0], Is.Null);
            Assert.That(layout[1], Is.EqualTo("cruise_missile"));
            Assert.That(MatchSettings.DeckSupports, Is.EqualTo(new[] { "cruise_missile" }));
        }

        [Test]
        public void TheLastSupportStaysAndNothingIsAddedBack()
        {
            Supports("cruise_missile");
            Assert.That(MatchSettings.ToggleDeckCard("cruise_missile", true), Is.EqualTo(MatchSettings.DeckChange.LastCard));
            Assert.That(MatchSettings.DeckSupports, Is.EqualTo(new[] { "cruise_missile" }));
        }

        [Test]
        public void AnAddedCardFillsTheEmptySlot()
        {
            Supports("artillery_barrage", "cruise_missile");
            MatchSettings.ToggleDeckCard("artillery_barrage", true);
            Assert.That(MatchSettings.ToggleDeckCard("airstrike", true), Is.EqualTo(MatchSettings.DeckChange.Added));
            var layout = MatchSettings.DeckLayout(true);
            Assert.That(layout[0], Is.EqualTo("airstrike"));
            Assert.That(layout[1], Is.EqualTo("cruise_missile"));
            Assert.That(MatchSettings.ToggleDeckCard("repair_drop", true), Is.EqualTo(MatchSettings.DeckChange.Full));
        }
    }
}
