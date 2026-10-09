#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 19 B (DECISIONS 18A): how high a target that uses altitude tiers is, which decides the weapons that
    /// reach it. Only a boss whose data opts in (<see cref="TierDef"/>, the Silver Bug now; prompt 20's Daedalus,
    /// Icarus Mk.0 and Typhon later) and its falling drop pods use tiers; every other unit is <see cref="None"/> and
    /// keeps the ordinary air and ground rules. Ordered from the lowest: a unit changing tier is hit as at the lower.
    /// </summary>
    public enum AltitudeTier
    {
        /// <summary>No tier: the ordinary rules (a weapon that targets aircraft for a flier, a ground weapon for the rest).</summary>
        None,

        /// <summary>Low altitude: every weapon that can hit aircraft, helicopters' weapons, and weapons with a "ceiling" of low (railguns).</summary>
        Low,

        /// <summary>High altitude: only weapons with a "ceiling" of high (long-range SAMs, Patriot batteries, fighters' air weapons).</summary>
        High,

        /// <summary>Out of reach (low orbit; prompt 20's submerged submarine can reuse it): nothing reaches it.</summary>
        Orbit,
    }

    /// <summary>One step of a phase's fixed schedule: this tier for so many seconds (the change to it comes first).</summary>
    public readonly struct TierStepDef
    {
        public TierStepDef(AltitudeTier tier, float seconds)
        {
            Tier = tier;
            Seconds = seconds;
        }

        public AltitudeTier Tier { get; }
        public float Seconds { get; }
    }

    /// <summary>Armour by altitude (prompt 19 C.2): the upper hull, the belly (what faces the ground at low altitude), and crashed.</summary>
    public sealed class TierArmourDef
    {
        public int Hull { get; internal set; } = 4;
        public int Belly { get; internal set; } = 2;
        public int Grounded { get; internal set; } = 3;
    }

    /// <summary>
    /// Prompt 19 E.5: the last phase's crash: it falls for <see cref="Fall"/> s to <see cref="At"/> (a point on the map, the
    /// nearest open ground to it), its impact blast, its wrecked model, the mounts that wake there (guns all round), and
    /// the debris round it that gives cover (passable, blocking fire, in the boss's frame as it lands).
    /// </summary>
    public sealed class CrashDef
    {
        public float Fall { get; internal set; } = 6f;
        public Vector2 At { get; internal set; }
        public float Damage { get; internal set; } = 500f;
        public float Radius { get; internal set; } = 16f;
        public string? Form { get; internal set; }
        public string? Warning { get; internal set; }
        public IReadOnlyList<int> Guns { get; internal set; } = Array.Empty<int>();
        public string Debris { get; internal set; } = "crash_debris";
        public IReadOnlyList<Vector2> DebrisAt { get; internal set; } = Array.Empty<Vector2>();
    }

    /// <summary>
    /// Prompt 19 E.6: at the hardest difficulties, in its last phase, it seizes the other side's drones for a few seconds
    /// (drone aircraft and drone launchers; any within reach of that side's jammers and EW towers are safe), after a warning.
    /// </summary>
    public sealed class HijackDef
    {
        public IReadOnlyList<string> Difficulties { get; internal set; } = new[] { "VeryHard", "Heroic", "Iron" };
        public float First { get; internal set; } = 10f;
        public float Every { get; internal set; } = 40f;
        public float Warn { get; internal set; } = 4f;
        public float Seconds { get; internal set; } = 6f;

        public bool On(string? difficulty)
        {
            if (difficulty == null) return false;
            foreach (var d in Difficulties)
                if (d == difficulty) return true;
            return false;
        }
    }

    /// <summary>
    /// Prompt 19 B/E (DECISIONS 18A): a boss that keeps to altitude tiers on a fixed schedule, whatever the other side does.
    /// Optional opening in <see cref="AltitudeTier.Orbit"/> for <see cref="Opening"/> s (untouchable, holding its guns), a
    /// <see cref="Descend"/> s way down, then per phase (the health <see cref="Marks"/>) its own cycle of steps; each change
    /// takes <see cref="Shift"/> s (longer with its manoeuvring thrusters broken). With its main engine broken ("stops":
    /// ["thrust"]) it keeps to the low tier. Its last phase with a <see cref="Crash"/> is the fall to the ground. Radio
    /// lines are text keys named in the data. Any boss can opt in (prompt 20): nothing here is the Silver Bug's own.
    /// </summary>
    public sealed class TierDef
    {
        public float Opening { get; internal set; }
        public float Descend { get; internal set; } = 4f;
        public float Shift { get; internal set; } = 3.5f;

        /// <summary>Drawn heights (m) of each tier, for the view and a shot-down pod's fall.</summary>
        public float OrbitHeight { get; internal set; } = 150f;
        public float HighHeight { get; internal set; } = 60f;
        public float LowHeight { get; internal set; } = 22f;

        /// <summary>Shares of full health where each next phase begins (0.7, 0.3): phase n has passed n marks.</summary>
        public IReadOnlyList<float> Marks { get; internal set; } = Array.Empty<float>();

        /// <summary>Each phase's cycle, repeated (the last one is used for any phase past the list, unless it crashes).</summary>
        public IReadOnlyList<IReadOnlyList<TierStepDef>> Schedule { get; internal set; } = Array.Empty<IReadOnlyList<TierStepDef>>();

        public TierArmourDef? Armour { get; internal set; }

        /// <summary>The fall in the last phase (null: it keeps its schedule to the end).</summary>
        public CrashDef? Crash { get; internal set; }

        public HijackDef? Hijack { get; internal set; }

        /// <summary>Its escorts come as it leaves orbit, not while it is still out of reach.</summary>
        public bool EscortsOnDescend { get; internal set; } = true;

        /// <summary>
        /// Play-test 13 (lane C), data "enterLow" (default true, the owner's rule): it comes onto the battlefield already at its
        /// low flight level, on the first low step of its opening cycle: no orbit opening and no slow descent (an aircraft
        /// arrives at its working height). False keeps the opening and the descent.
        /// </summary>
        public bool EnterLow { get; internal set; } = true;

        /// <summary>Prompt 20: the phase (0 up) from which it stops moving (-1: never).</summary>
        public int HaltPhase { get; internal set; } = -1;

        /// <summary>Radio keys by moment: appear, descend, phase2, phase3, crash, down, hijack, hijackWarn.</summary>
        public IReadOnlyDictionary<string, string> Radio { get; internal set; } = new Dictionary<string, string>();

        public string? RadioFor(string moment) => Radio.TryGetValue(moment, out var key) ? key : null;

        public float HeightOf(AltitudeTier tier) => tier switch
        {
            AltitudeTier.Orbit => OrbitHeight,
            AltitudeTier.High => HighHeight,
            AltitudeTier.Low => LowHeight,
            _ => 0f,
        };

        /// <summary>The cycle of phase <paramref name="phase"/> (0 first).</summary>
        public IReadOnlyList<TierStepDef> CycleOf(int phase) =>
            Schedule.Count == 0 ? Array.Empty<TierStepDef>() : Schedule[Math.Clamp(phase, 0, Schedule.Count - 1)];

        /// <summary>The phase that crashes (the one after the last mark), or -1.</summary>
        public int CrashPhase => Crash != null ? Marks.Count : -1;

        /// <summary>Seconds of a phase's cycle it spends reachable at the low tier (the combat value's exposure; the changes count as low).</summary>
        public float LowShare(int phase)
        {
            var cycle = CycleOf(phase);
            float low = 0f, all = 0f;
            for (var i = 0; i < cycle.Count; i++)
            {
                var step = cycle[i];
                var before = cycle[(i + cycle.Count - 1) % cycle.Count].Tier;
                var shift = before != step.Tier ? Shift : 0f;
                all += step.Seconds + shift;
                if (step.Tier == AltitudeTier.Low) low += step.Seconds;
                if (shift > 0f && (step.Tier == AltitudeTier.Low || before == AltitudeTier.Low)) low += shift;
            }
            return all > 0f ? low / all : 0f;
        }
    }

    /// <summary>
    /// Prompt 19 D: drop pods from a boss while it is at one of <see cref="Tiers"/>: <see cref="Count"/> pods every
    /// <see cref="Every"/> s (the first <see cref="First"/> s after it appears), each carrying 1 or 2 of <see cref="Units"/>
    /// in turn (elites by the side's elite budget). A pod (<see cref="Unit"/>, a low-tier target with its own health) falls
    /// for <see cref="Fall"/> s onto a warned spot short of the other side's biggest group; shot down, what it carries
    /// never lands. At most <see cref="Max"/> of the pods' vehicles alive (and on the way) at once, apart from the escort
    /// cap. Its pod bay broken ("stops": ["pods"]): no more drops.
    /// </summary>
    public sealed class PodDef
    {
        public string Unit { get; internal set; } = "drop_pod";
        public float First { get; internal set; } = 4f;
        public float Every { get; internal set; } = 14f;
        public int Count { get; internal set; } = 2;
        public int Min { get; internal set; } = 1;
        public int PerPod { get; internal set; } = 2;
        public float Fall { get; internal set; } = 6f;
        public int Max { get; internal set; } = 6;
        public float Offset { get; internal set; } = 30f;
        public float Spread { get; internal set; } = 12f;
        public string? Warning { get; internal set; }

        /// <summary>Prompt 26 B.7: what a pod does where it lands: a two-layer blast of this damage (0: none) within <see cref="Radius"/> m and a <see cref="Stun"/> second stun.</summary>
        public float Damage { get; internal set; }

        public float Radius { get; internal set; } = 6f;
        public float Stun { get; internal set; } = 1f;

        public IReadOnlyList<AltitudeTier> Tiers { get; internal set; } = new[] { AltitudeTier.Orbit, AltitudeTier.High };
        public IReadOnlyList<string> Units { get; internal set; } = Array.Empty<string>();

        /// <summary>Prompt 20: seconds between drops by phase (the last holds after; empty: <see cref="Every"/>).</summary>
        public IReadOnlyList<float> EveryByPhase { get; internal set; } = Array.Empty<float>();

        public float EveryIn(int phase) => EveryByPhase.Count == 0 ? Every : MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Bosses.PodDef.EveryInEveryByPhaseFloor, EveryByPhase[Math.Clamp(phase, 0, EveryByPhase.Count - 1)]);

        public bool DropsAt(AltitudeTier tier)
        {
            foreach (var t in Tiers)
                if (t == tier) return true;
            return false;
        }
    }

    /// <summary>Prompt 19 B.1-B.2: which weapons reach which tier (plain rules, the sim's and the HUD's).</summary>
    public static class TierRules
    {
        /// <summary>
        /// The highest tier this weapon on this carrier reaches: its own "ceiling" (a railgun's low, a SAM's high); a
        /// weapon that can hit aircraft reaches low at least, and the carrier's ceiling (a fighter's high) when above;
        /// a helicopter's weapons reach low (the spec's "helicopters").
        /// </summary>
        public static AltitudeTier Ceiling(WeaponDef weapon, VehicleDef? carrier)
        {
            if (weapon.Damage <= 0f) return AltitudeTier.None;
            var ceiling = weapon.Ceiling;
            if (weapon.CanTarget(true))
            {
                if (ceiling < AltitudeTier.Low) ceiling = AltitudeTier.Low;
                if (carrier != null && carrier.Ceiling > ceiling) ceiling = carrier.Ceiling;
            }
            if (carrier != null && carrier.Flying && !carrier.FixedWing && ceiling < AltitudeTier.Low) ceiling = AltitudeTier.Low;
            return ceiling >= AltitudeTier.Orbit ? AltitudeTier.High : ceiling;
        }

        /// <summary>Whether the weapon reaches a target at <paramref name="tier"/> (None: the ordinary air/ground rule).</summary>
        public static bool Reaches(WeaponDef weapon, VehicleDef? carrier, AltitudeTier tier, bool targetFlying) => tier switch
        {
            AltitudeTier.None => weapon.CanTarget(targetFlying),
            AltitudeTier.Orbit => false,
            _ => Ceiling(weapon, carrier) >= tier,
        };

        /// <summary>For the HUD's ✓ ~ ✕: 2 its main weapon reaches that tier, 1 only another of its weapons does, 0 none.</summary>
        public static int Verdict(VehicleDef unit, AltitudeTier tier)
        {
            if (Reaches(unit.Weapon, unit, tier, true)) return 2;
            for (var i = 1; i < unit.Mounts.Count; i++)
                if (Reaches(unit.Mounts[i].Weapon, unit, tier, true)) return 1;
            return 0;
        }
    }
}
