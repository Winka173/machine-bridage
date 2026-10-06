using System;
using System.Text;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>One critical cue as it started (a warning sound, a mine found, an EMP): what, where (world), when (unscaled s).</summary>
    internal readonly struct CueEvent
    {
        public CueEvent(ThreatType type, Vector3 at, float time)
        {
            Type = type;
            At = at;
            Time = time;
        }

        public ThreatType Type { get; }
        public Vector3 At { get; }
        public float Time { get; }
    }

    /// <summary>
    /// MVA W2-B (spec parts BH, BL, CB): every critical cue reports here the moment it starts (AudioDirector when the warning
    /// sound gets its voice, HazardCues for a mine found or an EMP, the super weapons' alarm), so the captions (CueCaptions)
    /// and the view telemetry read one feed and never disagree with what was played. View only.
    /// </summary>
    internal static class CueFeed
    {
        public static event Action<CueEvent> Raised;

        public static void Raise(ThreatType type, Vector3 at)
        {
            var e = new CueEvent(type, at, UnityEngine.Time.unscaledTime);
            ViewTelemetry.Cue(type);
            Raised?.Invoke(e);
        }

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics() => Raised = null;
    }

    /// <summary>
    /// MVA W2-B (spec parts BT visual / audio, CA-CC, brief "view telemetry"): read-only counters of what the presentation did,
    /// for the stress scenes, the -mb-perf report (PerfProbe.Detail) and the match-end log line. Counting only: nothing here
    /// changes what is drawn or played. Audio: sounds asked for, started, dropped (no voice) and voices taken by class; P0 /
    /// P1 cues asked for and started (a miss is one asked for that never got a voice: the BV gate wants 0); occlusion
    /// queries. Visual: cues raised by threat, captions shown, mines found, EMPs, boss part state changes.
    /// </summary>
    internal static class ViewTelemetry
    {
        private const int Classes = 6;

        private static readonly int[] Requested = new int[Classes], Started = new int[Classes], Dropped = new int[Classes], Stolen = new int[Classes];
        private static readonly int[] Cues = new int[Enum.GetValues(typeof(ThreatType)).Length];
        private static int _occlusionQueries, _occluded, _captions, _partStates, _peakVoices;
        private static string _zone = "-";

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        public static void Reset()
        {
            Array.Clear(Requested, 0, Classes);
            Array.Clear(Started, 0, Classes);
            Array.Clear(Dropped, 0, Classes);
            Array.Clear(Stolen, 0, Classes);
            Array.Clear(Cues, 0, Cues.Length);
            _occlusionQueries = _occluded = _captions = _partStates = _peakVoices = 0;
            _zone = "-";
        }

        public static void Cue(ThreatType type) => Cues[(int)type]++;
        public static void SoundRequested(int cls) => Requested[Mathf.Clamp(cls, 0, Classes - 1)]++;
        public static void SoundStarted(int cls) => Started[Mathf.Clamp(cls, 0, Classes - 1)]++;
        public static void SoundDropped(int cls) => Dropped[Mathf.Clamp(cls, 0, Classes - 1)]++;
        public static void VoiceStolen(int cls) => Stolen[Mathf.Clamp(cls, 0, Classes - 1)]++;
        public static void OcclusionQuery(bool occluded)
        {
            _occlusionQueries++;
            if (occluded) _occluded++;
        }

        public static void Caption() => _captions++;
        public static void PartState() => _partStates++;
        public static void Voices(int busy) => _peakVoices = Mathf.Max(_peakVoices, busy);
        public static void Zone(string zone) => _zone = zone ?? "-";

        /// <summary>P0 / P1 sounds asked for that never started (the audio load gate wants none).</summary>
        public static int CriticalMisses => Mathf.Max(0, Requested[0] - Started[0]) + Mathf.Max(0, Requested[1] - Started[1]);

        public static int CuesOf(ThreatType type) => Cues[(int)type];
        public static int StartedOf(int cls) => Started[Mathf.Clamp(cls, 0, Classes - 1)];
        public static int DroppedOf(int cls) => Dropped[Mathf.Clamp(cls, 0, Classes - 1)];
        public static int OcclusionQueries => _occlusionQueries;
        public static int Captions => _captions;

        /// <summary>One line: per class started / dropped / taken, the P0-P1 misses, occlusion, the cues by threat, the zone.</summary>
        public static string Summary()
        {
            var text = new StringBuilder("view: ");
            for (var c = 0; c < Classes; c++) text.Append('P').Append(c).Append('=').Append(Started[c]).Append('/').Append(Dropped[c]).Append('/').Append(Stolen[c]).Append(' ');
            text.Append("p01miss=").Append(CriticalMisses).Append(" voicesPeak=").Append(_peakVoices).Append(" occl=").Append(_occluded).Append('/').Append(_occlusionQueries);
            text.Append(" captions=").Append(_captions).Append(" partStates=").Append(_partStates).Append(" zone=").Append(_zone).Append(" cues=");
            for (var i = 0; i < Cues.Length; i++)
                if (Cues[i] > 0) text.Append((ThreatType)i).Append(':').Append(Cues[i]).Append(',');
            return text.ToString();
        }
    }
}
