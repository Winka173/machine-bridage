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
    }
}
