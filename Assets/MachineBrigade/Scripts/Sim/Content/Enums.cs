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

    /// <summary>What a weapon fires. Missiles are guided; everything else lands on its aim point.</summary>
    public enum ProjectileKind
    {
        Shell,
        Bullet,
        Missile,
        Rocket,
        Flame,
        Bomb,

        /// <summary>A kamikaze drone: slow, guided, and it dives onto its target.</summary>
        Drone,
    }

    /// <summary>
    /// What a vehicle is for. Drives the counter table shown on the cards and the AI's sense of
    /// which enemy each unit should fight; damage itself comes from damage type against armour.
    /// </summary>
    public enum UnitClass
    {
        Scout,
        Light,
        Tank,
        Heavy,
        TankHunter,
        Artillery,
        AntiAir,
        Support,
        Helicopter,
        Plane,
        Defense,
        Boss,
    }

    /// <summary>Which layers a weapon can engage.</summary>
    [System.Flags]
    public enum TargetLayers
    {
        None = 0,
        Ground = 1,
        Air = 2,
        All = Ground | Air,
    }

    /// <summary>How a weapon mount is pointed.</summary>
    public enum MountAim
    {
        /// <summary>On the main turret: fires where the turret points.</summary>
        Turret,

        /// <summary>On its own fast mount (pintle machine gun, chin turret).</summary>
        Free,

        /// <summary>Fixed forward on the hull (helicopter rockets): the vehicle turns to aim.</summary>
        Hull,

        /// <summary>
        /// Out of the left side (an AC-130's guns, a door gunner): aims anywhere within 60 degrees
        /// of square to the left of the hull, and the aircraft flies to keep its target there.
        /// </summary>
        Left,

        /// <summary>Out of the right side (a door gunner), within 60 degrees of square to the right.</summary>
        Right,
    }
}
