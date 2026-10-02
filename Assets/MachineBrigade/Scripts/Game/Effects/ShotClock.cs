using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Fix prompt L4, the delayed damage ("đạn dính ra 1 khoảng thời gian sau máu mới trừ"): rounds in flight
    /// (<see cref="ProjectilePool"/>, <see cref="TracerPool"/>, <see cref="EscapeWarnings"/>) are drawn on the simulation's
    /// clock, not the render clock. A round's damage lands on the Sim tick its travel ends; flown on <c>Time.time</c>, the
    /// drawn round got there first whenever the Sim ran slower than real time (the Sandbox slowed, a frame needing more
    /// than <see cref="MachineBrigade.Sim.Core.SimClock.MaxStepsPerFrame"/> steps, a heavy frame on a phone).
    /// <para>Play-test 12 (DECISIONS "Play-test 12 (lane B)"): L4's clock was one static for the whole game. The menu's
    /// in-action preview (<see cref="MachineBrigade.Game.Rendering.FiringRange"/>) runs its own little Sim while the lobby
    /// battle behind the menu rests (no steps), so the lobby froze the shared clock while it stayed on, and every round of
    /// the preview (and of any other tool drawing through an EffectsDirector) stuck at its muzzle. Now each
    /// <see cref="EffectsDirector"/> owns its clock, and the world that feeds it (MatchRunner, FiringRange) advances it.
    /// A clock never advanced stays off and passes the time it is given through.</para>
    /// </summary>
    internal sealed class ShotClock
    {
        /// <summary>Set once the owning world has advanced it; off, <see cref="Map"/> returns the time it is given.</summary>
        public bool Active { get; set; }

        /// <summary>The simulation seconds the views are drawn at this frame.</summary>
        public float SimNow { get; set; }

        /// <summary>
        /// A render-clock time (<c>Time.time</c>, or a moment that far ahead of it) on the shot clock: the same offset from
        /// <see cref="SimNow"/>. Unchanged while the clock is off.
        /// </summary>
        public float Map(float now) => Active ? SimNow + (now - Time.time) : now;

        /// <summary>The frame's update: <paramref name="simSeconds"/> as drawn, or on with the frame while the battle is frozen.</summary>
        public void Advance(double simSeconds, bool frozen, float frame)
        {
            if (frozen && Active) SimNow += Mathf.Max(0f, frame);
            else SimNow = (float)simSeconds;
            Active = true;
        }

        /// <summary>
        /// Play-test 12: while a step's events are drawn, the time that step began (rounds launched now start where the
        /// views draw that step, so they land on the frame their impact is drawn rather than up to a frame early).
        /// </summary>
        public void Launching(double stepStart)
        {
            SimNow = (float)stepStart;
            Active = true;
        }

        /// <summary><paramref name="clock"/>'s time for <paramref name="now"/>, or <paramref name="now"/> with no clock.</summary>
        public static float Map(ShotClock clock, float now) => clock != null ? clock.Map(now) : now;
    }
}
