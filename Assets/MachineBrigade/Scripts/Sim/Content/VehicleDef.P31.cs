#nullable enable

namespace MachineBrigade.Sim.Content
{
    /// <summary>Prompt 31 L5: how heavy a ground vehicle is (the frozen lake's ice gives under the medium and heavy ones).</summary>
    public enum WeightClass
    {
        Light,
        Medium,
        Heavy,
    }

    public sealed partial class VehicleDef
    {
        /// <summary>
        /// Prompt 31 L5: its weight (data "weightClass"; else from its armour and health: heavy front armour and 1,400 health or
        /// more, or a boss, Heavy; heavy front armour, Medium; the rest Light). Never its CP: a cheap heavy is still heavy.
        /// </summary>
        public WeightClass Weight { get; internal set; }

        /// <summary>Prompt 31 L5: the ice of a frozen lake cracks under it (a ground vehicle of medium or heavy weight).</summary>
        public bool BreaksIce => !Flying && !Static && Weight != WeightClass.Light;

        internal static WeightClass InferWeight(VehicleDef def)
        {
            if (def.Boss) return WeightClass.Heavy;
            if (def.Flying || def.Armour.GroundClass != ArmorClass.Heavy) return WeightClass.Light;
            return def.MaxHp >= 1400f ? WeightClass.Heavy : WeightClass.Medium;
        }
    }
}
