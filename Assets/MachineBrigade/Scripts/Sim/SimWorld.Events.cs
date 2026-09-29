#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Sim
{
    /// <summary>
    /// Prompt 23: what a mission's events change in the battle itself: the running event systems (in the battle's
    /// fingerprint), the electronic-warfare blackout of a side's radar, and how far units see as the weather turns.
    /// </summary>
    public sealed partial class SimWorld
    {
        /// <summary>The seed the battle was made with (the events draw from it).</summary>
        public int Seed { get; }

        internal readonly List<MissionEventSystem> EventSystems = new();

        /// <summary>The mission's event systems (the operation's own and the current stage's), for the Game's notices, arrows and bars.</summary>
        public IReadOnlyList<MissionEventSystem> MissionEvents => EventSystems;

        private readonly double[] _blackoutUntil = new double[3];

        /// <summary>D.6: a side's minimap and radar are dark (an EW storm): it sees only what its units see themselves.</summary>
        public bool BlackedOut(int team) => team >= 0 && team < _blackoutUntil.Length && Time < _blackoutUntil[team];

        /// <summary>Seconds of a side's blackout left (0 when none): the countdown.</summary>
        public float BlackoutLeft(int team) => BlackedOut(team) ? (float)(_blackoutUntil[team] - Time) : 0f;

        internal void Blackout(int team, double until)
        {
            if (team >= 0 && team < _blackoutUntil.Length) _blackoutUntil[team] = Math.Max(_blackoutUntil[team], until);
        }

        /// <summary>
        /// D.9: how far every unit sees against the mission's own weather (1), moved by a weather change as it rolls in (a
        /// snowstorm: 0.85). Visibility multiplies each spotter's reach by it.
        /// </summary>
        public float WeatherSight { get; internal set; } = 1f;

        private void MixEvents(Action<long> mix)
        {
            foreach (var s in EventSystems) s.Mix(mix);
            mix((long)Math.Round(WeatherSight * 1000f));
            for (var i = 0; i < _blackoutUntil.Length; i++) mix((long)Math.Round(_blackoutUntil[i] * 20.0));
        }
    }
}
