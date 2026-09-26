#nullable enable
using System;

namespace MachineBrigade.Sim.Core
{
    /// <summary>
    /// Turns variable frame time into a whole number of fixed simulation steps.
    /// The simulation only ever advances by <see cref="StepSeconds"/>; views interpolate
    /// between the last two steps using <see cref="Alpha"/>, so gameplay does not depend
    /// on the device's frame rate.
    /// </summary>
    public sealed class SimClock
    {
        // Absorbs binary rounding of the step length (1/20 s is not exact in floating point),
        // so 0.15 s at 20 Hz yields 3 steps rather than 2.999... -> 2.
        private const double Epsilon = 1e-9;

        private double _accumulator;

        /// <param name="ticksPerSecond">Simulation rate; the plan starts at 20 Hz.</param>
        /// <param name="maxStepsPerFrame">
        /// Upper bound on catch-up work in one frame. Time beyond it is dropped so a long
        /// hitch (app backgrounded, breakpoint) cannot freeze the game with a burst of steps.
        /// </param>
        public SimClock(int ticksPerSecond = 20, int maxStepsPerFrame = 5)
        {
            if (ticksPerSecond <= 0) throw new ArgumentOutOfRangeException(nameof(ticksPerSecond));
            if (maxStepsPerFrame <= 0) throw new ArgumentOutOfRangeException(nameof(maxStepsPerFrame));
            TicksPerSecond = ticksPerSecond;
            StepSeconds = 1.0 / ticksPerSecond;
            MaxStepsPerFrame = maxStepsPerFrame;
        }

        public int TicksPerSecond { get; }

        public double StepSeconds { get; }

        public int MaxStepsPerFrame { get; }

        /// <summary>Total fixed steps advanced since the match started.</summary>
        public long Tick { get; private set; }

        /// <summary>While paused, frame time is ignored rather than banked.</summary>
        public bool Paused { get; set; }

        /// <summary>Fraction (0..1) of the next step already elapsed, for view interpolation.</summary>
        public float Alpha => (float)Math.Clamp(_accumulator / StepSeconds, 0.0, 1.0);

        /// <summary>
        /// Adds one frame of wall-clock time and returns how many fixed steps to run now.
        /// Non-finite or non-positive frame times are ignored.
        /// </summary>
        public int Advance(double frameSeconds)
        {
            if (Paused || !double.IsFinite(frameSeconds) || frameSeconds <= 0) return 0;

            _accumulator += frameSeconds;
            var steps = (int)Math.Floor((_accumulator + Epsilon) / StepSeconds);
            if (steps > MaxStepsPerFrame)
            {
                steps = MaxStepsPerFrame;
                _accumulator = 0;
            }
            else
            {
                _accumulator = Math.Max(0, _accumulator - steps * StepSeconds);
            }

            Tick += steps;
            return steps;
        }

        /// <summary>Returns the clock to tick 0 for a restarted match.</summary>
        public void Reset()
        {
            _accumulator = 0;
            Tick = 0;
            Paused = false;
        }
    }
}
