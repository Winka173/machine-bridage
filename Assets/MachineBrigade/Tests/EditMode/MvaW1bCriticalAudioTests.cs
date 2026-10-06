using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Audio;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// MVA W1-B (spec parts AP, AQ, BL, BV; DECISIONS "Map/visual/audio W1-B (lane B)"): a P0 warning injected into the peak of
    /// a crowded battle mix gets a voice, and no later event of the storm takes it while it plays; P1 cues behave alike; the
    /// policy never lets a P0 / P1 cue be virtualised. Drives the pure <see cref="VoiceArbiter"/> the AudioDirector uses.
    /// Written for the owner's test runs; not run by the lane (owner token rule).
    /// </summary>
    public class MvaW1bCriticalAudioTests
    {
        private const int Pool = 32;
        private const int WhistleBank = 900, BigWhistleBank = 901;

        /// <summary>Every voice busy with the loudest combat the mix allows: near blasts, boss sounds, shots, small arms.</summary>
        private static VoiceState[] CrowdedMix()
        {
            var voices = new VoiceState[Pool];
            int[] priorities = { SoundPriority.Boss, SoundPriority.NearBlast, SoundPriority.NearShot, SoundPriority.SmallArms };
            for (var i = 0; i < Pool; i++)
                voices[i] = new VoiceState
                {
                    Playing = true, Bank = 100 + i % 6, Priority = priorities[i % priorities.Length], Level = 1f, Started = i * 0.01f,
                    Distance = (i % 5) * 0.2f,
                };
            return voices;
        }

        private static void Take(VoiceState[] voices, int i, int bank, int priority, float level, float now)
        {
            voices[i] = new VoiceState { Playing = true, Bank = bank, Priority = priority, Level = level, Started = now };
        }

        [Test]
        public void CriticalWarningSurvivesCrowdedMix()
        {
            var voices = CrowdedMix();
            var warning = VoiceArbiter.Pick(voices, BigWhistleBank, 2, false, SoundPriority.Critical, 0.4f);
            Assert.GreaterOrEqual(warning, 0, "the P0 warning gets a voice in a full mix");
            Assert.Less(voices[warning].Priority, SoundPriority.Warning, "it takes a non-critical voice");
            Take(voices, warning, BigWhistleBank, SoundPriority.Critical, 0.4f, 1f);

            // The storm: 500 louder combat events of every class and bank while the warning plays.
            int[] storm = { SoundPriority.Boss, SoundPriority.NearBlast, SoundPriority.NearShot, SoundPriority.FarBlast, SoundPriority.SmallArms };
            for (var n = 0; n < 500; n++)
            {
                var bank = 100 + n % 7;
                var pick = VoiceArbiter.Pick(voices, bank, 4, n % 3 == 0, storm[n % storm.Length], 2f, 0f);
                Assert.AreNotEqual(warning, pick, $"event {n} must not take the active P0 warning");
                if (pick >= 0) Take(voices, pick, bank, storm[n % storm.Length], 2f, 1f + n * 0.001f);
            }
            Assert.IsTrue(voices[warning].Playing && voices[warning].Priority == SoundPriority.Critical, "still playing");
        }

        [Test]
        public void WarningsPastTheirBankLimitStillPlay()
        {
            var voices = CrowdedMix();
            var taken = new List<int>();
            // Five incoming whistles at once on a three-voice bank: every one plays, none cuts another.
            for (var n = 0; n < 5; n++)
            {
                var pick = VoiceArbiter.Pick(voices, WhistleBank, 3, false, SoundPriority.Warning, 0.5f);
                Assert.GreaterOrEqual(pick, 0, $"whistle {n} plays");
                CollectionAssert.DoesNotContain(taken, pick, $"whistle {n} does not cut an active whistle");
                taken.Add(pick);
                Take(voices, pick, WhistleBank, SoundPriority.Warning, 0.5f, 2f + n);
            }
        }

        [Test]
        public void OrdinaryMixRulesStayForCombatSounds()
        {
            var voices = CrowdedMix();
            // Past the effect voices, a small-arms shot cannot take a boss sound or a near blast.
            var pick = VoiceArbiter.Pick(voices, 100, 8, false, SoundPriority.SmallArms, 0.1f, 1f);
            if (pick >= 0) Assert.LessOrEqual(voices[pick].Priority, SoundPriority.SmallArms);
            // A free voice is taken first.
            voices[7].Playing = false;
            Assert.AreEqual(7, VoiceArbiter.Pick(voices, 200, 8, false, SoundPriority.Boss, 1f));
        }

        [Test]
        public void PolicyKeepsCriticalCuesUnvirtualisedOnTheirOwnBus()
        {
            Assert.AreEqual(AudioClass.P0, AudioPolicy.ClassOf(SoundPriority.Critical));
            Assert.AreEqual(AudioClass.P1, AudioPolicy.ClassOf(SoundPriority.Warning));
            Assert.AreEqual(AudioClass.P5, AudioPolicy.ClassOf(SoundPriority.Ambient));
            foreach (var cls in new[] { AudioClass.P0, AudioClass.P1 })
            {
                var policy = AudioPolicy.For(cls);
                Assert.IsFalse(policy.CanBeVirtualized, cls + " is never virtualised during its warning");
                Assert.AreEqual(AudioBus.CriticalWarnings, policy.Bus);
                Assert.AreEqual(AudioGroup.Warnings, AudioPolicy.SliderOf(policy.Bus), "not on the ambience's slider");
                Assert.IsFalse(policy.Compressed);
            }
            // The duck is brief: down within the attack, back to full after the release.
            Assert.AreEqual(1f, AudioPolicy.DuckGain(-1f));
            Assert.AreEqual(AudioPolicy.DuckDepth, AudioPolicy.DuckGain(AudioPolicy.DuckAttack + 0.01f), 1e-4f);
            Assert.AreEqual(1f, AudioPolicy.DuckGain(AudioPolicy.DuckAttack + AudioPolicy.DuckHold + AudioPolicy.DuckRelease + 0.01f));
        }
    }
}
