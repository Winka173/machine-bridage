using System;
using NUnit.Framework;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Tests
{
    public class SimClockTests
    {
        [Test]
        public void WholeFrameTimeProducesMatchingSteps()
        {
            var clock = new SimClock(ticksPerSecond: 20);

            Assert.AreEqual(3, clock.Advance(0.15));
            Assert.AreEqual(3, clock.Tick);
        }

        [Test]
        public void PartialFramesAccumulateUntilAStepIsDue()
        {
            var clock = new SimClock(ticksPerSecond: 20);

            Assert.AreEqual(0, clock.Advance(0.03));
            Assert.AreEqual(1, clock.Advance(0.03));
            Assert.AreEqual(0.2f, clock.Alpha, 1e-4f);
        }

        [Test]
        public void LongHitchIsCappedAndBacklogDropped()
        {
            var clock = new SimClock(ticksPerSecond: 20, maxStepsPerFrame: 5);

            Assert.AreEqual(5, clock.Advance(10.0));
            Assert.AreEqual(0f, clock.Alpha);
            Assert.AreEqual(1, clock.Advance(0.05));
        }

        [Test]
        public void PausedClockIgnoresTimeInsteadOfBankingIt()
        {
            var clock = new SimClock(ticksPerSecond: 20) { Paused = true };

            Assert.AreEqual(0, clock.Advance(1.0));
            clock.Paused = false;
            Assert.AreEqual(1, clock.Advance(0.05));
        }

        [TestCase(-0.1)]
        [TestCase(0.0)]
        [TestCase(double.NaN)]
        [TestCase(double.PositiveInfinity)]
        public void InvalidFrameTimeIsIgnored(double frameSeconds)
        {
            var clock = new SimClock();

            Assert.AreEqual(0, clock.Advance(frameSeconds));
            Assert.AreEqual(0, clock.Tick);
        }

        [Test]
        public void ResetReturnsToTickZero()
        {
            var clock = new SimClock();
            clock.Advance(0.12);

            clock.Reset();

            Assert.AreEqual(0, clock.Tick);
            Assert.AreEqual(0f, clock.Alpha);
        }

        [Test]
        public void RejectsNonPositiveRates()
        {
            Assert.Throws<ArgumentOutOfRangeException>(() => new SimClock(ticksPerSecond: 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => new SimClock(maxStepsPerFrame: 0));
        }
    }
}
