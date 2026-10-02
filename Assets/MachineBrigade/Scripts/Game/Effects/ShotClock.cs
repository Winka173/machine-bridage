using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Fix prompt L4, the delayed damage ("đạn dính ra 1 khoảng thời gian sau máu mới trừ"): rounds in flight
    /// (<see cref="ProjectilePool"/>, <see cref="TracerPool"/>) are drawn on the simulation's clock, not the render clock.
    /// A round's damage lands on the Sim tick its travel ends; flown on <c>Time.time</c>, the drawn round got there first
    /// whenever the Sim ran slower than real time (the Sandbox slowed or stepping, a frame needing more than
    /// <see cref="MachineBrigade.Sim.Core.SimClock.MaxStepsPerFrame"/> steps, whose rest is dropped, a heavy frame on a
    /// phone), and sat there until the hit points dropped. On this clock it lands on the frame its impact is drawn.
    /// <para>MatchRunner sets <see cref="SimNow"/> every frame to the time the views are drawn at (the last step less the
    /// part of a step still to come, as the views interpolate); while the battle is frozen (its end) it runs on with the
    /// frame so the rounds still in the air finish. Off (tests, tools, the menu's preview), the pools keep the time they
    /// are given.</para>
    /// </summary>
    internal static class ShotClock
    {
        /// <summary>Set by a running battle; off, <see cref="Map"/> returns the time it is given.</summary>
        public static bool Active { get; set; }

        /// <summary>The simulation seconds the views are drawn at this frame.</summary>
        public static float SimNow { get; set; }

        /// <summary>
        /// A render-clock time (<c>Time.time</c>, or a moment that far ahead of it) on the shot clock: the same offset from
        /// <see cref="SimNow"/>. Unchanged while the clock is off.
        /// </summary>
        public static float Map(float now) => Active ? SimNow + (now - Time.time) : now;

        /// <summary>The frame's update: <paramref name="simSeconds"/> as drawn, or on with the frame while the battle is frozen.</summary>
        public static void Advance(double simSeconds, bool frozen, float frame)
        {
            Active = true;
            SimNow = frozen ? SimNow + Mathf.Max(0f, frame) : (float)simSeconds;
        }
    }
}
