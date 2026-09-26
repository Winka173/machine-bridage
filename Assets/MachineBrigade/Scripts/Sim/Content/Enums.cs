namespace MachineBrigade.Sim.Content
{
    public enum ArmorClass
    {
        Light,
        Heavy,
        Air,
        Structure,
    }

    public enum DamageType
    {
        Kinetic,
        ArmorPiercing,
        HighExplosive,
        Fire,
        Flak,
    }

    /// <summary>Visual weight of an impact or explosion. Gameplay never depends on it.</summary>
    public enum ExplosionTier
    {
        Small,
        Medium,
        Large,
        Huge,
        Ultimate,
    }
}
