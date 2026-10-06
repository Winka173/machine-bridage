using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Audio
{
    /// <summary>MVA W1-B (spec part AP): the gameplay priority class of a sound, P0 the highest.</summary>
    internal enum AudioClass
    {
        /// <summary>Critical UI, a lethal warning, a boss's super weapon (its alarm, the big whistle).</summary>
        P0 = 0,

        /// <summary>Incoming missile or artillery (the whistles), a critical HQ alarm.</summary>
        P1 = 1,

        /// <summary>Own heavy weapon, a nearby heavy hostile weapon, a boss's sound, a near blast.</summary>
        P2 = 2,

        /// <summary>Nearby normal weapons and impacts.</summary>
        P3 = 3,

        /// <summary>Distant normal combat, engines.</summary>
        P4 = 4,

        /// <summary>Ambience, repetitive machine-gun tails, cosmetic debris.</summary>
        P5 = 5,
    }

    /// <summary>MVA W1-B (spec part AS): the mix's control groups. The user-facing sliders map onto them (see <see cref="AudioPolicy.SliderOf"/>).</summary>
    internal enum AudioBus
    {
        Master,
        Music,
        UI,
        VoiceRadio,
        CriticalWarnings,
        PlayerWeapons,
        CombatSfx,
        Engines,
        Ambience,
    }

    /// <summary>What happens to a sound of a class when the voices run out (spec part AQ).</summary>
    internal enum Virtualization
    {
        /// <summary>Never cut or virtualised while it plays (P0, P1: an active warning).</summary>
        Never,

        /// <summary>Cut only by a more important sound, the weakest and quietest first.</summary>
        ByPriority,

        /// <summary>Dropped or folded into a cluster sound first (distant small arms).</summary>
        KillOrAggregate,
    }

    /// <summary>One class's rules (spec parts AP, AQ, AR, AT, BK): limits, cooldown, distance weighting, virtualisation, bus, ducking.</summary>
    internal readonly struct AudioClassPolicy
    {
        public AudioClassPolicy(AudioClass cls, int maxInstances, float cooldown, float distanceWeight, Virtualization virtualization,
            AudioBus bus, bool ducksOthers, bool compressed)
        {
            Class = cls;
            MaxInstances = maxInstances;
            Cooldown = cooldown;
            DistanceWeight = distanceWeight;
            Virtualization = virtualization;
            Bus = bus;
            DucksOthers = ducksOthers;
            Compressed = compressed;
        }

        public AudioClass Class { get; }

        /// <summary>At most this many of the class at once (its banks keep their own, smaller, limits).</summary>
        public int MaxInstances { get; }

        /// <summary>The shortest gap between two of one bank at one spot (a P0 / P1 cue elsewhere is never held back by it).</summary>
        public float Cooldown { get; }

        /// <summary>How much distance lowers its rank when the voices run out (0: none; 1: a far one counts a whole class lower).</summary>
        public float DistanceWeight { get; }

        public Virtualization Virtualization { get; }

        public AudioBus Bus { get; }

        /// <summary>Its start briefly ducks the lower classes (music, ambience, distant combat; never another warning).</summary>
        public bool DucksOthers { get; }

        /// <summary>Under the Effects compressor and the big-blast duck (warnings are not: they cut through).</summary>
        public bool Compressed { get; }

        /// <summary>Spec part BL: a P0 cue is never virtualised during its active warning.</summary>
        public bool CanBeVirtualized => Virtualization != Virtualization.Never;
    }

    /// <summary>
    /// MVA W1-B (spec parts AP-AT, BL, BV; DECISIONS "Map/visual/audio W1-B (lane B)"): the audio priority policy over the
    /// mix's existing 7-step <see cref="SoundPriority"/> scale, and the voice arbiter that guarantees the critical cues: a P0
    /// or P1 sound always gets a voice (a free one, else the weakest non-critical one, past its bank's limit if every voice of
    /// its bank is itself an active warning), and nothing ever takes a voice from a playing P0 / P1 sound. Kept free of Unity
    /// objects so the EditMode tests drive it with a crowded mix.
    /// </summary>
    internal static class AudioPolicy
    {
        /// <summary>Ducking envelope of a warning (spec part AT: fast attack 0.15-0.30 s, release 0.5-1.5 s).</summary>
        internal const float DuckAttack = 0.15f, DuckHold = 0.4f, DuckRelease = 0.8f;

        /// <summary>How far down a warning ducks music, ambience and the lower combat classes (brief: never the whole mix).</summary>
        internal const float DuckDepth = 0.55f;

        /// <summary>Two P0 / P1 cues of one bank this close (m) within its cooldown are one cue (aggregated, not missed).</summary>
        internal const float CueMergeRadius = 12f;

        private static readonly AudioClassPolicy[] Table =
        {
            new(AudioClass.P0, 6, 0f, 0f, Virtualization.Never, AudioBus.CriticalWarnings, true, false),
            new(AudioClass.P1, 6, 0f, 0f, Virtualization.Never, AudioBus.CriticalWarnings, true, false),
            new(AudioClass.P2, 10, 0.04f, 0.3f, Virtualization.ByPriority, AudioBus.CombatSfx, false, true),
            new(AudioClass.P3, 12, 0.05f, 0.5f, Virtualization.ByPriority, AudioBus.CombatSfx, false, true),
            new(AudioClass.P4, 8, 0.06f, 0.8f, Virtualization.KillOrAggregate, AudioBus.CombatSfx, false, true),
            new(AudioClass.P5, 6, 0.1f, 1f, Virtualization.KillOrAggregate, AudioBus.Ambience, false, true),
        };

        public static AudioClassPolicy For(AudioClass cls) => Table[(int)cls];

        public static IReadOnlyList<AudioClassPolicy> All => Table;

        /// <summary>The class of a sound on the mix's priority scale (<see cref="SoundPriority"/>).</summary>
        public static AudioClass ClassOf(int priority)
        {
            if (priority >= SoundPriority.Critical) return AudioClass.P0;
            if (priority >= SoundPriority.Warning) return AudioClass.P1;
            if (priority >= SoundPriority.NearBlast) return AudioClass.P2;
            if (priority >= SoundPriority.NearShot) return AudioClass.P3;
            if (priority >= SoundPriority.FarShot) return AudioClass.P4;
            return AudioClass.P5;
        }

        /// <summary>A P0 / P1 sound: never virtualised while it plays, on the CriticalWarnings bus.</summary>
        public static bool IsCritical(int priority) => priority >= SoundPriority.Warning;

        /// <summary>The user-facing slider a bus answers to (spec part AS: critical warnings are not on the ambience's slider).</summary>
        public static AudioGroup SliderOf(AudioBus bus) => bus switch
        {
            AudioBus.Music => AudioGroup.Music,
            AudioBus.UI => AudioGroup.UI,
            AudioBus.VoiceRadio => AudioGroup.Dialogue,
            AudioBus.CriticalWarnings => AudioGroup.Warnings,
            _ => AudioGroup.Effects,
        };

        /// <summary>
        /// The warning duck's gain <paramref name="since"/> s after a warning started (1 before it and after the release):
        /// down to <see cref="DuckDepth"/> over the attack, held, then back over the release.
        /// </summary>
        public static float DuckGain(float since)
        {
            if (since < 0f) return 1f;
            if (since < DuckAttack) return Mathf.Lerp(1f, DuckDepth, since / DuckAttack);
            if (since < DuckAttack + DuckHold) return DuckDepth;
            var t = (since - DuckAttack - DuckHold) / DuckRelease;
            return t >= 1f ? 1f : Mathf.Lerp(DuckDepth, 1f, t);
        }

        /// <summary>
        /// The rank a playing sound keeps when the voices run out: its priority, lowered by distance for the classes that
        /// weight it (a far machine gun ranks under a near one of the same step); critical sounds never lose rank.
        /// </summary>
        public static float Rank(int priority, float distanceShare)
        {
            if (IsCritical(priority)) return priority;
            var weight = For(ClassOf(priority)).DistanceWeight;
            return priority - weight * 10f * Mathf.Clamp01(distanceShare);
        }
    }

    /// <summary>One voice of the pool as the arbiter sees it.</summary>
    internal struct VoiceState
    {
        public bool Playing;

        /// <summary>The bank it plays (any id; equal ids are one bank).</summary>
        public int Bank;

        public int Priority;
        public float Level;
        public float Started;

        /// <summary>Its distance from the view as a share of the hearing reach (0-1).</summary>
        public float Distance;
    }

    /// <summary>
    /// MVA W1-B: which voice a new sound takes (<see cref="AudioPolicy"/>). The non-critical path is the mix's rule since fix
    /// pass L7 (a bank at its limit takes its own oldest, or with NoSteal its quietest only when twice as loud; past
    /// <see cref="EffectVoices"/> busy voices only the weakest lower-ranked one; the pool's last voices wait for warnings and
    /// boss sounds), with two guarantees on top: a playing P0 / P1 voice is never taken, and a P0 / P1 sound always gets a voice
    /// while any voice is not itself critical.
    /// </summary>
    internal static class VoiceArbiter
    {
        /// <summary>Effect voices at once before the least important is cut (of the pool's 32; the rest wait for warnings and boss sounds).</summary>
        internal const int EffectVoices = 24;

        /// <summary>-1: drop the new sound; else the index of the voice it takes.</summary>
        public static int Pick(IReadOnlyList<VoiceState> voices, int bank, int maxVoices, bool noSteal, int priority, float level, float distance = 0f)
        {
            var critical = AudioPolicy.IsCritical(priority);
            int oldest = -1, free = -1, weakest = -1, quietest = -1, softest = -1, playing = 0, busy = 0;
            var rank = AudioPolicy.Rank(priority, distance);
            float weakestRank = float.MaxValue, softestRank = float.MaxValue;
            for (var i = 0; i < voices.Count; i++)
            {
                var v = voices[i];
                if (!v.Playing)
                {
                    if (free < 0) free = i;
                    continue;
                }
                busy++;
                // A playing P0 / P1 voice is never taken (spec part BL: not virtualised during its active warning).
                var guarded = AudioPolicy.IsCritical(v.Priority);
                if (v.Bank == bank)
                {
                    playing++;
                    if (!guarded && (oldest < 0 || v.Started < voices[oldest].Started)) oldest = i;
                    if (!guarded && (quietest < 0 || v.Level < voices[quietest].Level)) quietest = i;
                }
                if (guarded) continue;
                var r = AudioPolicy.Rank(v.Priority, v.Distance);
                // The least important non-critical voice of all: a critical sound takes it whatever its rank.
                if (softest < 0 || r < softestRank || (r == softestRank && v.Level < voices[softest].Level))
                {
                    softest = i;
                    softestRank = r;
                }
                if (r > rank || (r == rank && v.Level > level)) continue;
                if (weakest < 0 || r < weakestRank || (r == weakestRank && v.Level < voices[weakest].Level))
                {
                    weakest = i;
                    weakestRank = r;
                }
            }
            if (critical)
            {
                // A warning always plays: a free voice, else the weakest non-critical one (its bank's limit gives way when every
                // voice of the bank is itself an active warning).
                if (playing >= maxVoices && oldest >= 0) return oldest;
                return free >= 0 ? free : softest;
            }
            if (playing >= maxVoices)
            {
                if (!noSteal) return oldest;
                return quietest >= 0 && voices[quietest].Level * 2f < level ? quietest : -1;
            }
            if (busy >= EffectVoices && priority < SoundPriority.Boss) return weakest;
            return free >= 0 ? free : weakest;
        }
    }
}
