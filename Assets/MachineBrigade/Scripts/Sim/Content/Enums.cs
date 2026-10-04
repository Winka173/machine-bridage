namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// A broad class kept for the roles, the commander and the cards (prompt 15): Air (flying), Structure
    /// (towers and buildings), and on the ground Heavy (front armour level 3-5, the chassis armour class) or Light (0-2). Damage comes
    /// from <see cref="ArmourLevels"/> and <see cref="TargetKind"/>, not from this.
    /// </summary>
    public enum ArmorClass
    {
        Light,
        Heavy,
        Air,
        Structure,
    }

    /// <summary>
    /// Prompt 15 C: what a round does. The numbers stay the old ones where the meaning carried over
    /// (saved resistances are indexed by them): 1 was armour-piercing (its missiles, rockets and drones
    /// are shaped charges now; its tank guns kinetic), 4 was flak.
    /// </summary>
    public enum DamageType
    {
        /// <summary>Bullets, autocannon rounds, tank guns' darts, railgun slugs: pierce by calibre and speed; APS, reactive armour and cages do not stop them.</summary>
        Kinetic = 0,

        /// <summary>HEAT: anti-tank missiles and rockets, FPV drones, Lancets, anti-tank bomblets. Pierce well even when small; reactive armour and cages cut them hard, APS shoots the missiles, rockets and drones down.</summary>
        ShapedCharge = 1,

        /// <summary>Howitzers, mortars, artillery rockets, bombs: low penetration, a blast, more against structures (more still with the thermobaric tag).</summary>
        HighExplosive = 2,

        /// <summary>Flamethrowers and napalm: burns on; strong against armour 0-1, weak against thick armour.</summary>
        Fire = 3,

        /// <summary>Flak, airburst, C-RAM and proximity-fused anti-air missiles: strong against aircraft, drones and the unarmoured, weak against armour. Missiles are still fooled by flares.</summary>
        Fragmentation = 4,

        /// <summary>Lasers and energy beams: hit at once; APS and flares cannot stop them, smoke does.</summary>
        Energy = 5,
    }

    /// <summary>Prompt 15 A: a face of a unit's armour.</summary>
    public enum ArmorFace
    {
        Front,
        Side,
        Rear,
        Top,
    }

    /// <summary>Prompt 15 C.7: what the damage-type table is read by (armour itself is the levels).</summary>
    public enum TargetKind
    {
        Ground,
        Air,
        Structure,
    }

    /// <summary>
    /// Prompt 15 D.3: the shape of what a weapon fires, for its icon (a real round's shape; for kinetic
    /// rounds the shape also shows how well it pierces). Data "form"; derived from the family when absent.
    /// </summary>
    public enum WeaponForm
    {
        /// <summary>Fires nothing (a tower without a gun).</summary>
        None,
        /// <summary>7.62 mm machine guns: a small round ball.</summary>
        BulletSmall,
        /// <summary>12.7-14.5 mm machine guns: a bullet.</summary>
        BulletBig,
        /// <summary>20-57 mm autocannons: a belted round.</summary>
        BeltedAutocannon,
        /// <summary>Medium tank guns (57-105 mm): a dart.</summary>
        Dart,
        /// <summary>120 mm and up: a double-headed dart.</summary>
        DoubleDart,
        /// <summary>Railguns and coilguns: a dart with an electric ring.</summary>
        Rail,
        /// <summary>A howitzer's high-explosive shell.</summary>
        HeShell,
        /// <summary>A finned mortar bomb.</summary>
        MortarBomb,
        /// <summary>Flak, airburst and C-RAM rounds: a round with a spray of dots.</summary>
        Airburst,
        /// <summary>70-122 mm rockets: a short finned tube.</summary>
        RocketSmall,
        /// <summary>220-300 mm artillery rockets: a long finned tube.</summary>
        RocketBig,
        /// <summary>Anti-tank and air-to-ground missiles: a short body, a cone nose.</summary>
        Atgm,
        /// <summary>Anti-air missiles (ground and air-to-air): a slim body, mid wings.</summary>
        Sam,
        /// <summary>Cruise missiles: wings across.</summary>
        Cruise,
        /// <summary>Ballistic missiles: a big body, a sharp nose.</summary>
        Ballistic,
        /// <summary>An unguided bomb: a drop with a tail.</summary>
        Bomb,
        /// <summary>A guided bomb: a bomb with a curve.</summary>
        GuidedBomb,
        /// <summary>A cluster bomb or rocket: a bomb splitting into dots.</summary>
        Cluster,
        /// <summary>900 kg and up (the JDAM, the car bomb's charge): a big bomb.</summary>
        HeavyBomb,
        /// <summary>An FPV drone: four rotors.</summary>
        Fpv,
        /// <summary>A Shahed-type one-way drone: a delta wing.</summary>
        Shahed,
        /// <summary>A Lancet: X wings.</summary>
        Lancet,
        /// <summary>A flamethrower: a jet of flame.</summary>
        Flame,
        /// <summary>Napalm: a bomb with a flame mark.</summary>
        Napalm,
        /// <summary>A laser or energy beam: a straight beam with a glowing head.</summary>
        Energy,
        /// <summary>A 40 mm grenade launcher's grenade.</summary>
        Grenade,
        /// <summary>A bulldozer blade (a blow, not a round).</summary>
        Blade,
        /// <summary>A boring boss's drill head.</summary>
        Drill,
        /// <summary>The boss super-gun's 800 mm shell.</summary>
        SuperShell,
        /// <summary>A car bomb's charge going off.</summary>
        CarBomb,
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
    /// <summary>
    /// Play-test 13 (lane C): how a round flies (data "flightProfile"; <see cref="WeaponDef.Flight"/>): straight at its target
    /// (a gun, an ATGM on its wire, a rocket pod), lofted (a tube- or box-launched missile climbs, then dives or turns onto its
    /// target: top attack, VLS, coastal boxes), or ballistic (artillery shells and rockets, ballistic missiles: a high arc).
    /// </summary>
    public enum FlightProfile
    {
        Direct,
        Loft,
        Ballistic,
    }

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

    /// <summary>
    /// The four branches of the army an equipment loadout belongs to (Armour, Light, Artillery,
    /// Air). Which classes each holds is data (balance.json "branches"): an aircraft is always Air,
    /// the rest by class. The game's GearBranch has the same order.
    /// </summary>
    public enum ArmyBranch
    {
        Armor,
        Light,
        Artillery,
        Air,
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
