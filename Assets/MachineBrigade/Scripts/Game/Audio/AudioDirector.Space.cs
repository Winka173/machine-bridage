using MachineBrigade.Game.Effects;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Navigation;
using UnityEngine;

namespace MachineBrigade.Game.Audio
{
    /// <summary>
    /// MVA W2-B (spec parts AV, AX, AY, BE, BF, BP; DECISIONS "Map/visual/audio W2 (lane B)"): the space a sound travels
    /// through. The project has no AudioMixer (EffectsLimiter), so this is per voice, on the low-pass and echo filters every
    /// voice carries, and cheap:
    /// <list type="bullet">
    /// <item>Distance layers (AV): a large weapon (<see cref="Bank.Layered"/>) is heard as a near transient (full band),
    /// then its body (the top end closing), then a far report: a floor on its level (it never fades like a rifle), a deeper
    /// low-pass, a slightly lower pitch (a softened transient) and the zone's environment tail on the echo filter.</item>
    /// <item>Occlusion (AX): a near (under <see cref="OcclusionRange"/>), high-value (P2 / P3) sound with tall cover between
    /// it and the listener (the Sim's CoverGrid: buildings, rock, walls) is turned down and low-passed by the zone's
    /// occlusion material, re-checked every <see cref="OcclusionPeriod"/> s, at most <see cref="OcclusionBudget"/> queries
    /// a frame. Warnings (P0 / P1) are never occluded (they must stay intelligible) and far or small sounds are never
    /// queried: no raycast per emitter per frame.</item>
    /// <item>Acoustic zones (AY, BP): the zone at the listener sets the tail (echo delay, decay, wet), the occlusion
    /// material and the wind bed's level and top end (AcousticZones).</item>
    /// <item>Weather (BE, Q): the weather's presentation (low-pass amount, reverb family) damps the tails and the far top
    /// end; the beds (wind, rain) duck under a warning like the lower classes, so weather never masks a warning.</item>
    /// </list>
    /// </summary>
    public sealed partial class AudioDirector
    {
        /// <summary>Occlusion is only worked out for sounds this near the listener (m).</summary>
        internal const float OcclusionRange = 70f;

        /// <summary>How often one voice's occlusion is re-checked (s).</summary>
        internal const float OcclusionPeriod = 0.25f;

        /// <summary>Most occlusion queries in one frame (the rest wait for the next).</summary>
        internal const int OcclusionBudget = 6;

        /// <summary>The far report's level floor as a share of the sound's own level, at the edge of the reach (AV).</summary>
        internal const float FarReportFloor = 0.16f;

        private SimWorld _world;
        private AcousticZones _zones = AcousticZones.Uniform(AcousticZone.Open);
        private AcousticProfile _zone = AcousticZones.Of(AcousticZone.Open);
        private WeatherPresentation _weatherLook = WeatherPresentation.Of("Clear");
        private float _ambientBase = -1f, _rainBase, _bedGain = 1f;
        private AudioLowPassFilter _ambientFilter;
        private int _occlusionCursor;

        /// <summary>The weather's presentation (Rendering.Weather sets it; never a gameplay value).</summary>
        internal WeatherPresentation WeatherLook
        {
            get => _weatherLook;
            set => _weatherLook = value;
        }

        /// <summary>The zone at the listener now (telemetry, tests).</summary>
        internal AcousticZone ZoneNow => _zone.Zone;

        /// <summary>The battle's world: its acoustic zones are measured once, and its cover is what occludes.</summary>
        public void SetWorld(SimWorld world)
        {
            _world = world;
            _zones = _lobby || world == null ? AcousticZones.Uniform(AcousticZone.Open) : AcousticZones.Build(world);
            if (_ambientFilter == null && _ambient != null)
            {
                _ambientFilter = _ambient.gameObject.AddComponent<AudioLowPassFilter>();
                _ambientFilter.cutoffFrequency = 22000f;
            }
        }

        /// <summary>The level a large weapon's far report keeps at <paramref name="share"/> of the reach (0 past it).</summary>
        internal static float FarReportLevel(float own, float share) =>
            share >= 1f ? 0f : own * FarReportFloor * Mathf.Clamp01((1f - share) / 0.4f);

        /// <summary>
        /// The layer a sound at <paramref name="share"/> of the reach is heard in: 0 near transient (under 0.25), 1 body
        /// (under 0.6), 2 far report.
        /// </summary>
        internal static int LayerOf(float share) => share < 0.25f ? 0 : share < 0.6f ? 1 : 2;

        /// <summary>The low-pass a sound starts with: a large weapon's by layer, the others as before (22 kHz to 2.2 kHz).</summary>
        internal static float CutoffOf(bool layered, float share, float weatherLowpass)
        {
            var far = Mathf.Pow(Mathf.Clamp01(share), 0.8f);
            if (!layered) return Mathf.Lerp(22000f, 2200f, far) * (1f - 0.3f * weatherLowpass * far);
            // Near transient: the full band; the body closes to 5 kHz; the far report down to 1.1 kHz (its body, no crack).
            var cutoff = share < 0.25f ? 22000f : share < 0.6f ? Mathf.Lerp(22000f, 5000f, (share - 0.25f) / 0.35f) : Mathf.Lerp(5000f, 1100f, (share - 0.6f) / 0.4f);
            return cutoff * (1f - 0.4f * weatherLowpass * far);
        }

        /// <summary>A starting voice's filters: its layer's low-pass and tail, and its first occlusion check.</summary>
        private void Space(Voice voice, Bank bank, float distance, float reach, bool critical)
        {
            var share = Mathf.Clamp01(distance / reach);
            var lowpass = Mathf.Clamp01(_weatherLook.LowpassEnvironmentAmount);
            voice.BaseCutoff = CutoffOf(bank.Layered, share, lowpass);
            voice.Filter.cutoffFrequency = voice.BaseCutoff;
            voice.Occlusion = voice.OcclusionTarget = 1f;
            voice.NextOcclusion = 0f;
            // The environment tail: a large weapon's body and far report, in the zone's space (a street rings, a field hardly).
            var tail = bank.Layered && !critical && LayerOf(share) >= 1;
            voice.Echo.enabled = tail;
            if (tail)
            {
                var damp = _weatherLook.ReverbProfile switch { "reverb_damped" => 0.6f, "reverb_dust" => 0.7f, "reverb_wet" => 1.1f, _ => 1f };
                var far = LayerOf(share) == 2 ? _zone.FarReportTail : 0.6f;
                voice.Echo.delay = _zone.EchoDelayMs;
                voice.Echo.decayRatio = Mathf.Clamp(_zone.EchoDecay * damp, 0.05f, 0.7f);
                voice.Echo.wetMix = Mathf.Clamp01(_zone.EchoWet * far * damp);
                voice.Echo.dryMix = 1f;
                // A softened transient far off: a shade lower.
                if (LayerOf(share) == 2) voice.Source.pitch *= 0.96f;
            }
            if (!critical && voice.Priority >= SoundPriority.NearShot && distance < OcclusionRange) Occlude(voice, true);
        }

        /// <summary>Re-checks whether tall cover stands between the listener and a voice; sets its occlusion target.</summary>
        private void Occlude(Voice voice, bool snap)
        {
            if (_world == null) return;
            var from = new System.Numerics.Vector2(Focus.x, Focus.z);
            var to = new System.Numerics.Vector2(voice.Where.x, voice.Where.z);
            // Skip the listener's own spot and the source's own footprint (a gun on a roof is not behind its roof).
            var blocked = _world.Cover.TryFirstHit(from, to, 2f, 4f, null, out _);
            ViewTelemetry.OcclusionQuery(blocked);
            voice.OcclusionTarget = blocked ? _zone.OcclusionGain : 1f;
            voice.NextOcclusion = Time.unscaledTime + OcclusionPeriod;
            if (snap) voice.Occlusion = voice.OcclusionTarget;
            var cutoff = blocked ? Mathf.Min(voice.BaseCutoff, _zone.OcclusionCutoff) : voice.BaseCutoff;
            voice.Filter.cutoffFrequency = snap ? cutoff : Mathf.Lerp(voice.Filter.cutoffFrequency, cutoff, 0.5f);
        }

        /// <summary>Per frame: the listener's zone, the beds' level, the occlusion queries due (round robin, budgeted).</summary>
        private void TickSpace(float now, float warned)
        {
            _zone = AcousticZones.Of(_zones.At(Focus));
            ViewTelemetry.Zone(_zone.ReverbPreset);
            ViewTelemetry.Voices(BusyVoices);
            // The beds (wind, rain): the zone's ambience and the warnings' duck (spec parts AT, BE, BF).
            if (_ambientBase < 0f) _ambientBase = _ambient.volume;
            _bedGain = _zone.AmbientGain * warned;
            _ambient.volume = _ambientBase * _bedGain;
            if (_rain.isPlaying) _rain.volume = _rainBase * _bedGain;
            if (_ambientFilter != null)
                _ambientFilter.cutoffFrequency = _zone.AmbientCutoff * (1f - 0.5f * Mathf.Clamp01(_weatherLook.LowpassEnvironmentAmount));
            var queries = 0;
            for (var k = 0; k < _voices.Length; k++)
            {
                var v = _voices[(_occlusionCursor + k) % _voices.Length];
                if (v.Bank == null || !v.Source.isPlaying) continue;
                if (AudioPolicy.IsCritical(v.Priority) || v.Priority < SoundPriority.NearShot || Vector3.Distance(v.Where, Focus) >= OcclusionRange)
                {
                    v.OcclusionTarget = 1f;
                }
                else if (now >= v.NextOcclusion && queries < OcclusionBudget)
                {
                    Occlude(v, false);
                    queries++;
                }
                v.Occlusion = Mathf.MoveTowards(v.Occlusion, v.OcclusionTarget, Time.unscaledDeltaTime * 4f);
            }
            _occlusionCursor = (_occlusionCursor + 1) % _voices.Length;
        }

        /// <summary>
        /// MVA W2-B (THREAT_CUES "mine detected"): a hostile mine the player's side just spotted: the mine ping, a P1 cue (its
        /// caption: [Mine detected]); a minefield found at once is one ping (the bank's cooldown at one spot).
        /// </summary>
        public void MineFound(System.Numerics.Vector2 at)
        {
            if (_lobby) return;
            Play(_banks[Sound.MinePing], at, 1f, 20f, SoundPriority.Warning, cue: (int)ThreatType.MineDetected);
        }

        /// <summary>
        /// MVA W2-B (THREAT_CUES "EMP"): an EMP going off at <paramref name="at"/> over <paramref name="radius"/> m: a P1
        /// warning with its caption when an enemy's EMP reaches the player's units, else the plain burst (a near effect).
        /// </summary>
        private void EmpBurst(System.Numerics.Vector2 at, float radius, int team)
        {
            var hits = false;
            if (_views != null && _playerTeam >= 0 && team != _playerTeam)
            {
                var all = _views.All;
                for (var i = 0; i < all.Count && !hits; i++)
                {
                    var v = all[i];
                    if (v.Sim.Team != _playerTeam || !v.Sim.IsAlive || v.Flying) continue;
                    hits = System.Numerics.Vector2.Distance(v.Sim.Position, at) <= radius + v.Def.HullRadius;
                }
            }
            if (hits) Play(_banks[Sound.Emp], at, 1f, 20f, SoundPriority.Warning, cue: (int)ThreatType.Emp);
            else Play(_banks[Sound.Emp], at, 0.8f, 0f, SoundPriority.NearShot);
        }

        /// <summary>The radius of the skill a SkillUsed event is (the user's own), else 15 m.</summary>
        private float SkillRadius(in Sim.Events.SimEvent e)
        {
            if (_views != null && _views.TryGet(e.Entity, out var user))
                foreach (var skill in user.Def.Skills)
                    if (skill.Id == e.DefId) return skill.Radius;
            return 15f;
        }

        /// <summary>The large weapons' banks (spec part AV), by library name.</summary>
        private static readonly string[] LayeredBanks =
        {
            "shot_s3", "shot_s4", "shot_s406", "shot_super", "launch_big", "launch_cruise", "blast_he_s3", "blast_he_s4", "blast_bomb",
            "blast_he_s406", "blast_super", "blast_thermo_s3", "blast_thermo_s4", "wreck_tank", "wreck_artillery", "crash_impact",
        };

        /// <summary>Marks the large weapons' banks as layered (the synthesised fallbacks and the library's).</summary>
        private void MarkLayered()
        {
            foreach (var sound in new[] { Sound.HeavyCannon, Sound.Howitzer, Sound.ExplosionLarge, Sound.ExplosionHuge, Sound.Collapse })
                if (_banks.TryGetValue(sound, out var bank)) bank.Layered = true;
            foreach (var name in LayeredBanks)
                if (_tierBanks.TryGetValue(name, out var bank)) bank.Layered = true;
        }
    }
}
