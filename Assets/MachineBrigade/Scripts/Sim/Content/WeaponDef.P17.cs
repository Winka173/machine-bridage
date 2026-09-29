#nullable enable
using System;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 17 C: a weapon whose damage grows while it stays on one target (the focused laser): from
    /// <see cref="From"/> times its damage to <see cref="To"/> times over <see cref="Seconds"/> of fire on the
    /// same target; another target, or <see cref="Grace"/> seconds without a round on it, starts again.
    /// </summary>
    public sealed class RampDef
    {
        public float From { get; internal set; } = 0.3f;
        public float To { get; internal set; } = 2f;
        public float Seconds { get; internal set; } = 6f;
        public float Grace { get; internal set; } = 1.5f;

        /// <summary>The multiplier after <paramref name="onTarget"/> seconds on the same target.</summary>
        public float At(double onTarget) => From + (To - From) * (float)Math.Clamp(onTarget / Math.Max(0.1, Seconds), 0.0, 1.0);

        /// <summary>The mean multiplier over the first <paramref name="seconds"/> on one target (the theoretical table's figure).</summary>
        public float MeanOver(float seconds)
        {
            if (seconds <= 0f) return From;
            var ramp = Math.Min(seconds, Seconds);
            var rising = (From + At(ramp)) * 0.5f * ramp;
            return (rising + To * Math.Max(0f, seconds - ramp)) / seconds;
        }
    }

    public sealed partial class WeaponDef
    {
        /// <summary>Prompt 17 C: its damage ramps up on one target (null: it does not).</summary>
        public RampDef? Ramp { get; internal set; }

        /// <summary>
        /// Prompt 17 C: a swarm of drones (the swarm carrier's): each drone of a salvo picks its own target within
        /// this many metres of the salvo's aim, and one whose target is gone when it arrives strikes another within
        /// it (0: not a swarm).
        /// </summary>
        public float SwarmReach { get; internal set; }

        /// <summary>
        /// Prompt 17 D.6: a dual-purpose gun's high-explosive round (the heavy tank's 152 mm): the gun loads it instead
        /// of its own round for a structure, a light vehicle or a wall (<see cref="WantsHe"/>); null: one round only.
        /// </summary>
        public WeaponDef? HeRound { get; internal set; }

        /// <summary>Armour at or below this front level takes the high-explosive round (light vehicles).</summary>
        public const int HeArmourMax = 1;

        /// <summary>Whether a dual-purpose gun loads its high-explosive round for this target (a structure, light armour).</summary>
        public static bool WantsHe(ArmorClass armor, ArmourLevels levels, bool isStatic) =>
            isStatic || armor == ArmorClass.Structure || levels.Front <= HeArmourMax;
    }
}
