using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Audio;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// MVA W2-B (DECISIONS "Map/visual/audio W2 (lane B)"): the acceptance rows of spec part CI this lane covers: the threat
    /// cue table has no gap left (mine detected, EMP) and top attack sounds unlike a direct missile; boss parts have readable
    /// destruction states; P0 / P1 cues survive a crowded mix (a warning storm on top of the W1 combat storm); distance does
    /// not erase a large weapon's identity; occlusion and the acoustic zones; the reduced-effects / shake settings keep the
    /// gameplay truth; no runtime node of a renamed model depends on a Blender suffix; the renderer outliers are merged.
    /// Written for the owner's test runs; not run by the lane (owner token rule).
    /// </summary>
    public class MvaW2bTests
    {
        // ------------------------------------------------------------------ threat cues (spec parts AE, AF, BL)

        [Test]
        public void EveryThreatHasACueNow()
        {
            foreach (var cue in ThreatCues.All)
            {
                Assert.AreNotEqual(CancelBehavior.NotImplemented, cue.Cancel, cue.Type + " has a cue");
                StringAssert.DoesNotContain("none yet", cue.VisualTelegraph, cue.Type.ToString());
                StringAssert.DoesNotContain("none yet", cue.AudioCue, cue.Type.ToString());
                Assert.IsFalse(cue.CanBeOccludedVisually, cue.Type + " draws above smoke, decals and debris");
                Assert.IsTrue(cue.KeptOnLowPreset);
            }
            StringAssert.Contains("trigger radius", ThreatCues.For(ThreatType.MineDetected).TelegraphShape);
            StringAssert.Contains("EMP radius", ThreatCues.For(ThreatType.Emp).TelegraphShape);
        }

        [Test]
        public void TopAttackSoundsUnlikeADirectMissile()
        {
            var top = ThreatCues.For(ThreatType.TopAttack).AudioCue;
            var direct = ThreatCues.For(ThreatType.MissileIncoming).AudioCue;
            StringAssert.Contains("warn_topattack", top);
            StringAssert.DoesNotContain("warn_topattack", direct);
            Assert.AreNotEqual(top, direct, "spec part BB: a different terminal warning when the response differs");
            // The dive clip itself: lock tones first, then the swell (it ends loud, cut at the landing).
            var clip = SoundSynth.TopAttackDive(990);
            Assert.Greater(clip.length, 0.8f);
        }

        [Test]
        public void CueFeedCountsAndForwards()
        {
            ViewTelemetry.Reset();
            var seen = new List<ThreatType>();
            void Hear(CueEvent e) => seen.Add(e.Type);
            CueFeed.Raised += Hear;
            try
            {
                CueFeed.Raise(ThreatType.MineDetected, Vector3.zero);
                CueFeed.Raise(ThreatType.Emp, Vector3.one);
            }
            finally
            {
                CueFeed.Raised -= Hear;
            }
            CollectionAssert.AreEqual(new[] { ThreatType.MineDetected, ThreatType.Emp }, seen);
            Assert.AreEqual(1, ViewTelemetry.CuesOf(ThreatType.Emp));
            StringAssert.Contains("MineDetected:1", ViewTelemetry.Summary());
        }

        // ------------------------------------------------------------------ boss part states (spec parts Y, AH, AN)

        [Test]
        public void BossPartStatesFollowThePartsHealth()
        {
            Assert.AreEqual(PartDamageState.Healthy, BossPartStates.Of(1f, false));
            Assert.AreEqual(PartDamageState.Healthy, BossPartStates.Of(0.5f, false));
            Assert.AreEqual(PartDamageState.Damaged, BossPartStates.Of(0.49f, false));
            Assert.AreEqual(PartDamageState.Critical, BossPartStates.Of(0.2f, false));
            Assert.AreEqual(PartDamageState.Destroyed, BossPartStates.Of(0.9f, true));
            // Each state reads darker than the one before (on the model, so Low and culled effects keep it).
            var healthy = BossPartStates.Tint(PartDamageState.Healthy);
            var damaged = BossPartStates.Tint(PartDamageState.Damaged);
            var critical = BossPartStates.Tint(PartDamageState.Critical);
            Assert.AreEqual(Vector3.one, healthy);
            Assert.Less(damaged.magnitude, healthy.magnitude);
            Assert.Less(critical.magnitude, damaged.magnitude);
            Assert.Greater(critical.x, critical.z, "a hot cast, not only darker");
        }

        // ------------------------------------------------------------------ audio (spec parts AV, AX, AY, BP, BV)

        [Test]
        public void WarningStormOnTopOfCombatStormMissesNothing()
        {
            // 32 voices busy with combat; 40 warnings (P1 whistles, P0 big whistles, mine pings, EMP, top-attack dives) arrive in
            // waves of 6 while 300 combat events keep coming: every warning that arrives gets a voice while fewer than 32
            // warnings play, and no combat sound ever takes a playing warning.
            var voices = new VoiceState[32];
            for (var i = 0; i < voices.Length; i++)
                voices[i] = new VoiceState { Playing = true, Bank = 100 + i % 6, Priority = SoundPriority.NearBlast, Level = 1f, Started = i * 0.01f };
            var warnings = new HashSet<int>();
            var misses = 0;
            var time = 1f;
            for (var w = 0; w < 40; w++)
            {
                var priority = w % 5 == 0 ? SoundPriority.Critical : SoundPriority.Warning;
                var bank = 900 + w % 5;
                var pick = VoiceArbiter.Pick(voices, bank, 2, false, priority, 0.4f);
                if (pick < 0) misses++;
                else
                {
                    Assert.IsFalse(warnings.Contains(pick), $"warning {w} must not cut a playing warning");
                    voices[pick] = new VoiceState { Playing = true, Bank = bank, Priority = priority, Level = 0.4f, Started = time };
                    warnings.Add(pick);
                }
                for (var n = 0; n < 8; n++)
                {
                    time += 0.01f;
                    var combat = VoiceArbiter.Pick(voices, 100 + n % 7, 4, false, SoundPriority.Boss, 2f);
                    Assert.IsFalse(combat >= 0 && warnings.Contains(combat), "combat never takes a playing warning");
                    if (combat >= 0) voices[combat] = new VoiceState { Playing = true, Bank = 100 + n % 7, Priority = SoundPriority.Boss, Level = 2f, Started = time };
                }
                // Warnings end after six waves (their clips are about a second long).
                if (w % 6 == 5)
                    foreach (var k in warnings.ToList())
                    {
                        voices[k].Playing = false;
                        warnings.Remove(k);
                    }
            }
            Assert.AreEqual(0, misses, "spec part BV: no warning misses in the crowded mix");
            Assert.Greater(AudioDirector.CriticalReach, 0f, "warnings carry past the effects' reach");
            Assert.GreaterOrEqual(AudioDirector.ScheduledCap, 24);
        }

        [Test]
        public void DistanceKeepsALargeWeaponsIdentity()
        {
            Assert.AreEqual(0, AudioDirector.LayerOf(0.1f));
            Assert.AreEqual(1, AudioDirector.LayerOf(0.4f));
            Assert.AreEqual(2, AudioDirector.LayerOf(0.8f));
            // Near: the whole band; far: the body only, never the small sounds' plain fade.
            Assert.AreEqual(22000f, AudioDirector.CutoffOf(true, 0.1f, 0f), 1f);
            Assert.Less(AudioDirector.CutoffOf(true, 0.9f, 0f), AudioDirector.CutoffOf(false, 0.9f, 0f));
            Assert.Greater(AudioDirector.FarReportLevel(1f, 0.8f), 0.05f, "a far report keeps a body");
            Assert.AreEqual(0f, AudioDirector.FarReportLevel(1f, 1f), "nothing past the reach");
            // The old curve for the other sounds (22 kHz to 2.2 kHz) in clear weather.
            Assert.AreEqual(Mathf.Lerp(22000f, 2200f, 1f), AudioDirector.CutoffOf(false, 1f, 0f), 1f);
        }

        [Test]
        public void AcousticZonesFromMapSemantics()
        {
            Assert.AreEqual(AcousticZone.Fortress, AcousticZones.Classify("temperate", 0.2f, 0f, 0f, true));
            Assert.AreEqual(AcousticZone.UrbanStreet, AcousticZones.Classify("urban", 0.3f, 0f, 0f, false));
            Assert.AreEqual(AcousticZone.Harbor, AcousticZones.Classify("harbor", 0.02f, 0f, 0.4f, false));
            Assert.AreEqual(AcousticZone.Forest, AcousticZones.Classify("temperate", 0f, 0.6f, 0f, false));
            Assert.AreEqual(AcousticZone.Snowfield, AcousticZones.Classify("snow", 0f, 0f, 0f, false));
            Assert.AreEqual(AcousticZone.Open, AcousticZones.Classify("desert", 0.01f, 0f, 0f, false));
            foreach (AcousticZone zone in System.Enum.GetValues(typeof(AcousticZone)))
            {
                var profile = AcousticZones.Of(zone);
                Assert.AreEqual(zone, profile.Zone);
                Assert.That(profile.OcclusionGain, Is.InRange(0.3f, 1f), "occlusion turns down, never mutes");
                Assert.That(profile.EchoWet, Is.InRange(0f, 0.5f));
                Assert.IsNotEmpty(profile.ReverbPreset);
                Assert.IsNotEmpty(profile.AmbientProfile);
            }
            // Walls ring more than an open field, a street more than a forest.
            Assert.Greater(AcousticZones.Of(AcousticZone.Fortress).EchoDecay, AcousticZones.Of(AcousticZone.Open).EchoDecay);
            Assert.Less(AcousticZones.Of(AcousticZone.UrbanStreet).OcclusionCutoff, AcousticZones.Of(AcousticZone.Forest).OcclusionCutoff);
            Assert.AreEqual(AcousticZone.Harbor, AcousticZones.Uniform(AcousticZone.Harbor).At(new Vector3(500f, 0f, -500f)));
            Assert.LessOrEqual(AudioDirector.OcclusionBudget, 8, "spec part AX: no raycast per emitter per frame");
        }

        // ------------------------------------------------------------------ accessibility (spec parts AK, AL, BS)

        [Test]
        public void ShakeAndEffectSettingsKeepTheGameplayTruth()
        {
            var shake = MatchSettings.ShakeIntensity;
            var reduced = MatchSettings.ReducedEffects;
            try
            {
                MatchSettings.ScreenShake = 0;
                Assert.AreEqual(0f, MatchSettings.ShakeScale);
                MatchSettings.ScreenShake = 1;
                Assert.AreEqual(1, MatchSettings.ScreenShake);
                MatchSettings.ShakeIntensity = 0.6f;
                Assert.AreEqual(0.6f, MatchSettings.ShakeScale, 1e-4f);
                MatchSettings.ReducedEffects = true;
                Assert.AreEqual(0.5f, MatchSettings.CosmeticShare);
                MatchSettings.ReducedEffects = false;
                Assert.AreEqual(1f, MatchSettings.CosmeticShare);
            }
            finally
            {
                MatchSettings.ShakeIntensity = shake;
                MatchSettings.ReducedEffects = reduced;
            }
            Assert.AreEqual(0.5f, MachineBrigade.Game.Hud.BattleHud.FlashGap, 1e-4f, "at most two full-screen flashes a second");
        }

        // ------------------------------------------------------------------ models (spec parts W, Z, AB, CG)

        private static readonly string[] Renamed =
        {
            "bastion_mk0", "behemoth", "behemoth_tempest", "command_airship", "daedalus", "drone_mothership", "earth_borer", "fenrir",
            "fortress_bastion", "hydra_sub", "ixion", "kraken", "landing_hovercraft", "leviathan", "mega_gunship", "mobile_fortress",
            "moloch", "monster", "nuke_train", "nyx", "sea_cruiser", "silver_bug", "silver_bug_wreck", "typhon",
        };

        [Test]
        public void NoRuntimeNodeDependsOnABlenderSuffix()
        {
            foreach (var model in Renamed)
            {
                var prefab = Resources.Load<GameObject>("Models/" + model);
                Assert.IsNotNull(prefab, model);
                foreach (var t in prefab.GetComponentsInChildren<Transform>(true))
                    Assert.IsFalse(RuntimeNodes.IsLegacySuffixed(t.name), $"{model}: {t.name}");
            }
        }

        [Test]
        public void RendererOutliersAreUnderTheirCaps()
        {
            // glb_check's caps (renderers): structure 48, jet 44, ground 76, boss_s 162.
            var caps = new Dictionary<string, int>
            {
                ["cp_relay"] = 48, ["vehicle_hangar_base"] = 48, ["aircraft_hangar"] = 48, ["attack_jet"] = 44, ["fpv_carrier"] = 76,
                ["heavy_aa"] = 76, ["ixion"] = 162,
            };
            foreach (var (model, cap) in caps)
            {
                var prefab = Resources.Load<GameObject>("Models/" + model);
                Assert.IsNotNull(prefab, model);
                Assert.LessOrEqual(prefab.GetComponentsInChildren<MeshRenderer>(true).Length, cap, model);
            }
        }
    }
}
