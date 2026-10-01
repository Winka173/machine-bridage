#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>
    /// Prompt 19 (DECISIONS 18A): the runtime state of a boss on altitude tiers (<see cref="VehicleDef.Tiers"/>) and of a
    /// falling drop pod: its tier (for the rules: the lower of the two while it changes), the change under way, its
    /// schedule and phase, the crash, and the drawn height. Run by the boss system (BossSystem.Tiers).
    /// </summary>
    public sealed partial class Vehicle
    {
        /// <summary>The tier the rules use now (a change counts as the lower of its two tiers); None: an ordinary unit.</summary>
        public AltitudeTier Tier { get; internal set; }

        /// <summary>The tier it is at or changing from, and the one it is changing to (the same when settled).</summary>
        public AltitudeTier TierFrom { get; internal set; }

        public AltitudeTier TierTo { get; internal set; }

        /// <summary>Changing tier (climbing or diving) until <see cref="ShiftEnds"/>.</summary>
        public bool Shifting { get; internal set; }

        internal double ShiftStart, ShiftEnds;

        /// <summary>When its current step of the schedule ends (the next change begins), or its opening in orbit.</summary>
        public double TierNext { get; internal set; }

        /// <summary>The step of its phase's cycle it is on.</summary>
        internal int TierStep;

        /// <summary>The phase of its schedule (0 first; each health mark passed adds one).</summary>
        public int TierPhase { get; internal set; }

        /// <summary>It has left orbit (it never goes back).</summary>
        public bool LeftOrbit { get; internal set; }

        /// <summary>Its satellite, left in orbit as it came down (the later big attacks come from there).</summary>
        public bool HasSatellite { get; internal set; }

        public Vector2 SatelliteAt { get; internal set; }

        /// <summary>Its main engine is broken (a part that "stops": ["thrust"]): it cannot climb to the high tier.</summary>
        internal bool ThrustOff;

        /// <summary>Its main engine is broken: it stays at the low tier until it crashes (the HUD shows no countdown).</summary>
        public bool StuckLow => ThrustOff && Def.Tiers != null;

        /// <summary>Its pod bay is broken (a part that "stops": ["pods"]): no more drop pods.</summary>
        internal bool PodsOff;

        internal double PodNext;
        internal int PodsSent;

        /// <summary>Falling to its crash site (the last phase) until <see cref="CrashAt"/>.</summary>
        public bool Crashing { get; internal set; }

        /// <summary>Down on the ground: no longer a flier (a ground target for every weapon), a fortress that cannot move.</summary>
        public bool Crashed { get; internal set; }

        internal double CrashStart, CrashAt;
        internal Vector2 CrashFrom, CrashSpot;

        /// <summary>Mounts that sleep until it crashes (its guns all round).</summary>
        internal bool[] MountDormant = Array.Empty<bool>();

        /// <summary>Prompt 26 B.2: when its close-guard ring may next go off.</summary>
        internal double GuardNext;

        /// <summary>The height it is drawn at now (m), from its tier or its fall; 0 when crashed.</summary>
        public float AltitudeNow { get; internal set; }

        /// <summary>How high it flies now: the tier's height for a tiered boss or a falling pod, else its def's altitude.</summary>
        public float Height => Tier != AltitudeTier.None || Crashing || IsPod ? AltitudeNow : Crashed ? 0f : Def.Altitude;

        /// <summary>A drop pod on its way down (it lands at <see cref="PodLands"/>).</summary>
        public bool IsPod { get; internal set; }

        internal double PodLaunched, PodLands;
        internal float PodFrom;

        /// <summary>Prompt 19 E.6: a drone seized by an enemy boss, and the side it goes back to.</summary>
        internal int HijackedFrom = -1;

        internal double HijackNext, HijackAt, HijackEnds;
        internal bool HijackWarned;

        /// <summary>The tier the rules use for a change from <paramref name="a"/> to <paramref name="b"/>: the lower one.</summary>
        internal static AltitudeTier Lower(AltitudeTier a, AltitudeTier b) => a < b ? a : b;

        /// <summary>Its armour on every face by its altitude (prompt 19 C.2), or -1 for the ordinary faces.</summary>
        private float TierArmour()
        {
            if (Def.Tiers?.Armour is not { } a) return -1f;
            if (Crashed) return a.Grounded;
            return Tier == AltitudeTier.Low || Crashing ? a.Belly : a.Hull;
        }
    }
}
