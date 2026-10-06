using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using MachineBrigade.Game.Effects;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Audio
{
    /// <summary>
    /// The bomb-run fix, pass 3 (DECISIONS "Ném bom rải thảm"): a stick's blasts heard as a stick. Each bomb cracks at its
    /// own point along the line (the sound walks with the blasts, panned and delayed by distance as every blast is); when
    /// the next bomb of the same stick goes off, the one before fades out over <see cref="ChokeSeconds"/>, so the stick
    /// carries one rolling tail, the last bomb's, instead of seven tails piled on each other (and the bank's three voices
    /// cutting the oldest dead mid-boom). A bomb belongs to the stick of the last bomb of its weapon that landed within
    /// <see cref="RunGap"/> release intervals and a few spacings of it. View only.
    /// </summary>
    public sealed partial class AudioDirector
    {
        /// <summary>A blast whose stick went on fades out over this (s).</summary>
        internal const float ChokeSeconds = 0.4f;

        /// <summary>A bomb within this many of its stick's release intervals of the last (and 0.25 s more) is the same stick's.</summary>
        internal const float RunGap = 2.5f;

        private readonly Dictionary<string, (float at, Vector2 where, int run)> _stickRuns = new();
        private int _stickRunCount;

        /// <summary>
        /// The stick a landing bomb of <paramref name="round"/> at <paramref name="at"/> is part of (0: not a stick's): the last
        /// one of its weapon when it follows on, and that bomb's blast is choked; else a new stick.
        /// </summary>
        private int StickRun(WeaponDef round, Vector2 at)
        {
            if (round?.Stick is not { Laid: true } stick) return 0;
            var now = Time.unscaledTime;
            int run;
            if (_stickRuns.TryGetValue(round.Id, out var last) && SameStick(stick, now - last.at, Vector2.Distance(last.where, at)))
            {
                run = last.run;
                foreach (var v in _voices)
                    if (v.Run == run && v.Choke < 0f && v.Source.isPlaying) v.Choke = now;
            }
            else run = ++_stickRunCount;
            _stickRuns[round.Id] = (now, at, run);
            if (_stickRuns.Count > 32) _stickRuns.Clear();
            return run;
        }

        /// <summary>When each shooter's mount last whistled for a stick (render clock).</summary>
        private readonly Dictionary<long, float> _stickWhistled = new();

        /// <summary>
        /// A stick's first bomb released: one falling whistle for the whole stick, timed to end as its first bomb lands (the
        /// big one from 400 kg, T4), heard as any whistle is (its reach, its priority). Not for the rest of its bombs, not for
        /// a guided bomb nor a lone one, and not when the fall is too short for the clip.
        /// </summary>
        private void StickWhistle(in SimEvent e, WeaponDef weapon)
        {
            if (weapon.Stick is not { Laid: true } stick || e.Value <= WhistleLead + 0.2f) return;
            var key = ((long)e.Entity.Value << 8) | (uint)(e.Mount & 0xff);
            var now = Time.unscaledTime;
            if (_stickWhistled.TryGetValue(key, out var last) && now - last < stick.Bombs * stick.Interval + 0.5f) return;
            _stickWhistled[key] = now;
            if (_stickWhistled.Count > 64) _stickWhistled.Clear();
            Whistle(e.Target, 0.75f, e.Value - WhistleLead, weapon.Tier >= 4, ThreatCues.Of(weapon));
        }

        /// <summary>A bomb <paramref name="gap"/> s and <paramref name="apart"/> m after the last of its weapon follows on in the same stick.</summary>
        internal static bool SameStick(StickDef stick, float gap, float apart) =>
            gap >= 0f && gap <= stick.Interval * RunGap + 0.25f && apart <= stick.Spacing * RunGap + 2f * (stick.JitterAlong + stick.JitterAcross) + 1f;

        /// <summary>The level left of a voice whose stick went on (1: not choked); a fully choked voice stops.</summary>
        private static float Choked(Voice v, float now)
        {
            if (v.Choke < 0f) return 1f;
            var left = 1f - (now - v.Choke) / ChokeSeconds;
            if (left > 0f) return left * left;
            v.Source.Stop();
            v.Choke = -1f;
            v.Run = 0;
            return 0f;
        }
    }
}
