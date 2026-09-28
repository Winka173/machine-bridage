#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>
    /// A vehicle's authoritative state. Views read it to draw; only the simulation's systems
    /// change it.
    /// </summary>
    public sealed partial class Vehicle : IDamageable
    {
        internal readonly List<Vector2> Path = new();

        /// <summary>Its part in the traffic rules: making way, waiting, queueing, backing out (see Movement.TrafficState).</summary>
        internal readonly Movement.TrafficState Traffic = new();

        internal Vehicle(EntityId id, VehicleDef def, int team, Vector2 position, float heading)
        {
            Id = id;
            Def = def;
            Team = team;
            Position = position;
            Heading = heading;
            TurretHeading = heading;
            Hp = def.MaxHp;
            ApsCharges = def.Aps?.Charges ?? 0;
            Order = Order.Idle;
            PathCompleted = true;
            GuardPoint = position;
            Weapons = new WeaponState[def.Mounts.Count];
            Arms = new WeaponDef[def.Mounts.Count];
            for (var i = 0; i < Weapons.Length; i++)
            {
                Arms[i] = def.Mounts[i].Weapon;
                var ammo = def.Mounts[i].Weapon.Ammo;
                Weapons[i] = new WeaponState { Heading = heading, Ammo = ammo > 0 ? ammo : -1 };
            }
            Aps = def.Aps;
            MineLayer = def.Mines;
            SkillReadyAt = new double[def.Skills.Count];
            SkillUsed = new bool[def.Skills.Count];
        }

        /// <summary>Rounds left for mount <paramref name="index"/>, or -1 when unlimited.</summary>
        public int Ammo(int index) => Weapons[index].Ammo;

        /// <summary>
        /// The weapon on mount <paramref name="index"/> as this vehicle carries it: the catalog's,
        /// or a copy its equipment tuned (range, magazine, reload...). Shared definitions never change.
        /// </summary>
        internal readonly WeaponDef[] Arms;

        public WeaponDef Arm(int index) => Arms[index];

        /// <summary>The main weapon as this vehicle carries it.</summary>
        public WeaponDef Weapon => Arms[0];

        /// <summary>Its active protection system (the model's own, or a Trophy module's).</summary>
        internal ApsDef? Aps;

        /// <summary>The mines it lays (a mine layer's own, or a Mine Dispenser module's).</summary>
        internal MineLayerDef? MineLayer;

        /// <summary>Fills every magazine to what it carries now (after its equipment changed the weapons).</summary>
        internal void RefillMagazines()
        {
            for (var i = 0; i < Weapons.Length; i++)
                Weapons[i].Ammo = Arms[i].Ammo > 0 ? Arms[i].Ammo : -1;
        }

        // ------------------------------------------------------------ equipment and timed effects
        /// <summary>Equipment beyond the plain multipliers: stat lines, traits and their counters (null: none).</summary>
        internal GearState? Gear;

        /// <summary>Timed effects (burning, slowed, shredded, marked, barrier...), by <see cref="StatusKind"/>.</summary>
        internal readonly Status[] Statuses = new Status[(int)StatusKind.Count];

        /// <summary>Speed and fire-rate multipliers from equipment and effects, worked out every step.</summary>
        internal float SpeedGear = 1f, FireGear = 1f;

        /// <summary>Hull and turret turn rates, vision and capture speed from equipment.</summary>
        internal float TurnFactor = 1f, TurretFactor = 1f, VisionFactor = 1f, CaptureFactor = 1f;

        /// <summary>Weapon reach from equipment effects of the moment (a siege anchor dug in).</summary>
        internal float RangeFactor = 1f;

        /// <summary>A guard tower's range aura on this tower this step (1: none).</summary>
        internal float TowerRange = 1f;

        /// <summary>Repairs it receives (regeneration, auras) are multiplied by this.</summary>
        internal float RepairReceived = 1f;

        /// <summary>Takes no damage until then (Unbreakable, Aegis Dome).</summary>
        internal double ImmuneUntil = double.NegativeInfinity;

        /// <summary>
        /// A last stand (Unbreakable, Aegis Dome) or an overheal shield (Phoenix Recovery) saved it
        /// recently: until then none of the three may save it again (they never chain on one blow).
        /// </summary>
        internal double LastStandUntil = double.NegativeInfinity;

        /// <summary>Driving to a new firing spot (shoot-and-scoot): the order waits until it is there.</summary>
        internal bool Relocating;

        /// <summary>Shoot-and-scoot: rounds fired from the current spot.</summary>
        internal int ScootShots;


        /// <summary>The share of every stun or EMP knock-out it shrugs off (a tower's Backup Generator; 1: immune).</summary>
        internal float StunResist;

        /// <summary>The fixed defences of each side (0 and 1) that last hit it, for Fire Link.</summary>
        internal readonly TowerFireMark[] TowerFire = new TowerFireMark[2];

        /// <summary>Hit points left in an absorbing barrier (Aegis Barrier, Shared Shield), for the view.</summary>
        public float Barrier => Statuses[(int)StatusKind.Barrier].Value;

        /// <summary>Reactive blocks left (Reactive Blocks trait), for a counter on the unit; 0 without the trait.</summary>
        public int ReactiveBlocksLeft => Gear != null && Gear.Has(TraitId.ReactiveBlocks) ? Gear.Blocks : 0;

        /// <summary>On fire from an Incendiary hit or a Firestorm, for the view.</summary>
        public bool Burning => Statuses[(int)StatusKind.Burn].Until > LastStatusCheck && Statuses[(int)StatusKind.Burn].Value > 0f;

        /// <summary>Sim time of the last step, so views can read timed effects without the clock.</summary>
        internal double LastStatusCheck;

        /// <summary>Capture speed on objectives, with its equipment.</summary>
        public float CaptureRate => Def.CaptureRate * CaptureFactor;

        /// <summary>Some limited weapon is not full.</summary>
        internal bool NeedsAmmo
        {
            get
            {
                for (var i = 0; i < Weapons.Length; i++)
                {
                    var max = Arms[i].Ammo;
                    if (max > 0 && Weapons[i].Ammo < max) return true;
                }
                return false;
            }
        }

        /// <summary>The main weapon has limited ammunition and none left.</summary>
        public bool OutOfAmmo => Weapons[0].Ammo == 0;

        /// <summary>Standing still enough for the crew to restock (fixed defences and aircraft always are).</summary>
        internal bool StillForReload => Def.Static || Flying || MathF.Abs(Speed) < Combat.CombatSystem.ReloadStillSpeed;

        /// <summary>The main weapon is empty but on the move, so its reload waits (the crew restocks standing still).</summary>
        public bool ReloadPaused => OutOfAmmo && !StillForReload;

        /// <summary>How far the main weapon's in-place reload has got, 0 to 1 (1 when it is not reloading).</summary>
        public float ReloadProgress
        {
            get
            {
                var weapon = Arms[0];
                if (weapon.Ammo <= 0 || Weapons[0].Ammo != 0) return 1f;
                var total = Combat.CombatSystem.ReloadSeconds(weapon);
                var left = Weapons[0].ReloadLeft > 0f ? Weapons[0].ReloadLeft : total;
                return Math.Clamp(1f - left / total, 0f, 1f);
            }
        }

        // ------------------------------------------------------------ skills and effects
        internal readonly double[] SkillReadyAt;
        internal readonly bool[] SkillUsed;
        internal double ShieldUntil = double.NegativeInfinity, OverdriveUntil = double.NegativeInfinity,
            BarrageUntil = double.NegativeInfinity, FlaresUntil = double.NegativeInfinity,
            StunnedUntil = double.NegativeInfinity, HealUntil = double.NegativeInfinity;
        internal float ShieldAmount, OverdriveSpeed = 1f, BarrageRate = 1f, Healing, RearmProgress;
        internal double NextMineAt;

        /// <summary>
        /// A boss's own countdown shown on the model, 0 to 1 (the Doomsday Train raising its
        /// missile before launch). Set by the mission.
        /// </summary>
        public float Charge { get; internal set; }

        /// <summary>A loaned aircraft (an escort item) leaves the battle at this time.</summary>
        internal double ExpiresAt = double.PositiveInfinity;

        /// <summary>Updates the effect flags views read; called every step by the ability system.</summary>
        internal void RefreshEffects(double now)
        {
            ShieldUp = ShieldUntil > now;
            Overdriven = OverdriveUntil > now;
            FlaresUp = FlaresUntil > now;
            Stunned = StunnedUntil > now || Dummy;
            Barraging = BarrageUntil > now;
        }

        /// <summary>A shield skill is soaking up damage.</summary>
        public bool ShieldUp { get; private set; }

        /// <summary>Overdrive: faster and firing more often.</summary>
        public bool Overdriven { get; private set; }

        /// <summary>Flares are out: guided weapons aimed at it miss.</summary>
        public bool FlaresUp { get; private set; }

        /// <summary>Knocked out by an EMP: cannot drive or fire.</summary>
        public bool Stunned { get; private set; }

        /// <summary>Holds its fire (a fortress keep's gun under its shield dome: nothing gets in or out).</summary>
        public bool HoldFire { get; internal set; }

        /// <summary>A barrage skill is running: the guns fire much faster.</summary>
        public bool Barraging { get; private set; }

        /// <summary>Drive speed multiplier from skills.</summary>
        internal float SpeedFactor => (Overdriven ? OverdriveSpeed : 1f) * DoctrineSpeed * SpeedGear * PhaseSpeed * PartSpeed;

        /// <summary>A multi-phase boss: the phases it has passed (0: the first bar).</summary>
        public int Phase { get; internal set; }

        /// <summary>Transforming between two phases (untouchable until <see cref="TransformUntil"/>).</summary>
        public bool Transforming { get; internal set; }

        internal double TransformUntil;
        internal float PhaseSpeed = 1f;

        /// <summary>The model it wears now if a phase changed it (null: its own).</summary>
        public string? Form { get; internal set; }

        /// <summary>Fire-rate multiplier from skills.</summary>
        internal float FireFactor => (Barraging ? BarrageRate : 1f) * (Overdriven ? 1.3f : 1f) * FireBoost * FireGear * CommandFire;

        /// <summary>A friendly command vehicle's aura (1: none in reach).</summary>
        internal float CommandFire = 1f;

        /// <summary>A friendly commander's damage aura (the Supreme Commander's; 1: none in reach).</summary>
        internal float CommandDamage = 1f;

        /// <summary>A gun pit down in its hole (see VehicleDef.Hidden): it cannot fire and is hard to see.</summary>
        public bool Lowered { get; internal set; }

        /// <summary>A gun pit just risen: its next shot hits harder (the Ambush branch).</summary>
        internal bool AmbushReady;

        /// <summary>A fixed minefield has laid its first mines.</summary>
        internal bool MinesLaid;

        /// <summary>A mode's own multiplier on fire rate (a fortress browned out, or making its last stand).</summary>
        internal float FireBoost = 1f;

        /// <summary>Until when a newly arrived vehicle takes only a fifth of the damage (home zones).</summary>
        internal double GraceUntil = double.NegativeInfinity;

        /// <summary>Takes no damage (a dormant fortress guardian, a spawn bastion).</summary>
        public bool Invulnerable { get; internal set; }

        /// <summary>Firing state per mount, parallel to <see cref="VehicleDef.Mounts"/>.</summary>
        internal readonly WeaponState[] Weapons;

        public EntityId Id { get; }
        public VehicleDef Def { get; }
        public int Team { get; internal set; }

        /// <summary>One of the allied commander's (a multi-stage mission): its own AI commands it, the player's does not.</summary>
        public bool Ally { get; internal set; }
        public Vector2 Position { get; internal set; }

        /// <summary>Hull heading in radians (see <see cref="SimMath"/> for the convention).</summary>
        public float Heading { get; internal set; }

        /// <summary>World-space turret heading in radians.</summary>
        public float TurretHeading { get; internal set; }

        /// <summary>Current forward speed in metres per second.</summary>
        public float Speed { get; internal set; }

        public float Hp { get; internal set; }
        public float MaxHp => Def.MaxHp * HpScale;

        /// <summary>Health multiplier from the side's doctrine.</summary>
        internal float HpScale = 1f;

        // ------------------------------------------------------------ upgrades (card rank, equipment)
        /// <summary>The side's upgrades for this vehicle's health and speed (the doctrine multiplies on top).</summary>
        internal float BoostHp = 1f;
        internal float BoostSpeed = 1f;

        /// <summary>Its rounds hit this much harder.</summary>
        internal float DamageBoost = 1f;

        /// <summary>It takes this share of the damage that lands on it (plating, reactive armour).</summary>
        internal float DamageTaken = 1f;

        /// <summary>Self-repair, as a share of its health a second, once it has not been hit for a few seconds.</summary>
        internal float Regen;

        internal SpecialModule Special;
        internal float SpecialPower, SpecialPower2;

        /// <summary>Its smoke dischargers have fired (once a battle).</summary>
        internal bool SmokeUsed;

        /// <summary>Drive speed multiplier from the side's doctrine.</summary>
        internal float DoctrineSpeed = 1f;
        public float Radius => Def.Radius;
        public ArmorClass Armor => Def.Armor;
        public bool IsAlive => Hp > 0f;
        public bool IsMoving => Speed > 0.1f;
        public bool Flying => Def.Flying;

        /// <summary>Current world heading of weapon mount <paramref name="index"/> (the turret for turret mounts).</summary>
        public float MountHeading(int index) => Def.Mounts[index].Aim switch
        {
            MountAim.Turret => TurretHeading,
            MountAim.Hull => Heading,
            _ => Weapons[index].Heading,
        };

        /// <summary>
        /// A target on a firing range (the detail page's demo): it never fires or moves, is always in
        /// sight, and cannot be destroyed (its health stops at a sliver and comes back).
        /// </summary>
        public bool Dummy { get; internal set; }

        /// <summary>A car bomb that set itself off: its own blast was the explosion (no second one as it dies).</summary>
        internal bool Detonated { get; set; }

        /// <summary>When it last fired anything (a stealthy aircraft shows for a moment after).</summary>
        public double LastFiredAt { get; internal set; } = double.NegativeInfinity;

        /// <summary>A VTOL jet holds in the air to shoot until then.</summary>
        public double HoverUntil { get; internal set; } = double.NegativeInfinity;

        /// <summary>A VTOL jet can stop in the air again from then.</summary>
        public double HoverReadyAt { get; internal set; } = double.NegativeInfinity;

        /// <summary>What mount <paramref name="index"/> is aimed at this step.</summary>
        public EntityId MountTarget(int index) => Weapons[index].Target;

        public Order Order { get; internal set; }

        /// <summary>What the main weapon is aimed at this step: the ordered target or an automatic one.</summary>
        public EntityId Target
        {
            get => Weapons[0].Target;
            internal set => Weapons[0].Target = value;
        }

        /// <summary>Main weapon cooldown in seconds.</summary>
        public float Cooldown
        {
            get => Weapons[0].Cooldown;
            internal set => Weapons[0].Cooldown = value;
        }

        /// <summary>Bit per team that can currently see this vehicle.</summary>
        public int VisibleToMask { get; internal set; }

        public bool IsVisibleTo(int team) => team >= 0 && (VisibleToMask & (1 << team)) != 0;

        /// <summary>
        /// Teams with it in sight right now (for a fixed defence, <see cref="VisibleToMask"/> also
        /// keeps the teams that have seen it before: they know where it stands).
        /// </summary>
        public int SeenByMask { get; internal set; }

        public bool IsSeenBy(int team) => team >= 0 && (SeenByMask & (1 << team)) != 0;

        internal int PathIndex;
        internal bool PathCompleted;

        /// <summary>Its new route waits for a step with path-finding to spare (see SimWorld.PathsPerStep).</summary>
        internal bool PathQueued;

        /// <summary>Where the waiting route goes.</summary>
        internal Vector2 QueuedGoal;
        internal Vector2 PathGoal;
        internal float RepathTimer;

        /// <summary>Enemy an attack-moving vehicle broke off its route to fight.</summary>
        internal EntityId Engaged;

        /// <summary>Distance to what the main weapon is aimed at (0 with no target); drives the barrel's elevation.</summary>
        public float AimDistance { get; internal set; }

        /// <summary>The turret is laid on something: the main weapon's target, or an aircraft its coaxial gun is chasing.</summary>
        public bool Aiming => Target.IsValid || CoaxAir.IsValid;

        /// <summary>Flight height of the aircraft the main weapon is aimed at (0 for ground targets).</summary>
        public float AimHeight { get; internal set; }

        internal bool ResumeRoute;

        /// <summary>Where an idle vehicle stands guard; it drives back here after a skirmish.</summary>
        internal Vector2 GuardPoint;

        /// <summary>Team of whoever last damaged this vehicle (-1: nobody, or a blast from the environment).</summary>
        internal int LastAttackerTeam = -1;

        /// <summary>Aeroplanes: the target of the current strafing run, kept while they pull through and turn.</summary>
        internal EntityId RunTarget;

        /// <summary>Aeroplanes: flying on past the target before turning in for the next run.</summary>
        internal bool RunExtending;

        /// <summary>Carrying out an order the player gave by hand.</summary>
        internal bool ManualOrder;

        /// <summary>Until when (sim time) the commander AI keeps its hands off after a manual order.</summary>
        internal double ManualUntil = double.NegativeInfinity;

        /// <summary>
        /// Driven by the mission script (a convoy truck, the armoured train): no AI and no player
        /// orders move it.
        /// </summary>
        public bool Scripted { get; internal set; }

        /// <summary>A mission's hunted vehicle: the game draws a target marker over it.</summary>
        public bool Marked { get; internal set; }

        /// <summary>The player took direct control of this vehicle recently.</summary>
        public bool UnderPlayerControl(double now) => ManualOrder || now < ManualUntil;

        /// <summary>Last enemy vehicle that hurt this one, so idle vehicles answer fire.</summary>
        internal EntityId LastAttacker;

        /// <summary>Simulation time of the last hit from <see cref="LastAttacker"/>.</summary>
        internal double LastHitTime = double.NegativeInfinity;

        /// <summary>A defence a mode put down, whose ground routes go round (see SimWorld.AnchorDefence).</summary>
        internal bool BlocksRoutes;

        /// <summary>Where the vehicle last stood still, and since when (entrenchment, see <see cref="SimWorld.Entrench"/>).</summary>
        internal Vector2 StillAt;
        internal double StillSince;

        /// <summary>Steering round a hull in the way: which way (+1 clockwise, -1 anticlockwise), and until when.</summary>
        internal float AvoidSide;

        internal double AvoidUntil = double.NegativeInfinity;

        internal Vector2 StuckSample;
        internal float StuckTimer;
        internal int StuckStrikes;

        /// <summary>The waypoint being driven to at the last stuck check, and how far off it was then.</summary>
        internal int StuckWaypoint = -1;
        internal float StuckWaypointDistance;

        /// <summary>Interceptors ready in the active protection system, and the reload under way.</summary>
        internal int ApsCharges;
        internal float ApsReload;

        /// <summary>Which launcher fires next (the systems alternate sides).</summary>
        internal bool ApsLeft;

        /// <summary>
        /// Its weapons take turns: when the last round of a main gun, missile or rocket (a salvo's
        /// rounds included) and of a machine gun left, from which mount, and when a heavy weapon
        /// last stood ready but held off for a machine gun's run.
        /// </summary>
        internal double HeavyRoundAt = double.NegativeInfinity;
        internal int HeavyMount = -1;
        internal double GunRoundAt = double.NegativeInfinity;
        internal int GunMount = -1;
        internal double HeavyWaitingAt = double.NegativeInfinity;
        internal double AnyRoundAt = double.NegativeInfinity;
        internal int AnyMount = -1;

        /// <summary>The centre of a gunship's pylon turn: it glides after the target instead of jumping (a new target, one on the move).</summary>
        internal System.Numerics.Vector2 OrbitCentre;
        internal bool Orbiting;

        /// <summary>An aircraft the coaxial machine gun is chasing while the main gun has nothing on the ground (the turret follows it).</summary>
        internal EntityId CoaxAir;

        /// <summary>Which way round an obstacle the hull is edging (+1 or -1), and until when it keeps to it.</summary>
        internal float SlideSide;
        internal double SlideUntil = double.NegativeInfinity;

        internal bool HasPath => PathIndex < Path.Count;

        /// <summary>Diagnostics hook (tests only): told whenever a vehicle's path or order changes.</summary>
        internal static Action<Vehicle, string>? PathTrace;

        internal void SetPath(List<Vector2> points, Vector2 goal)
        {
            PathTrace?.Invoke(this, $"SetPath {points.Count} to {goal}");
            PathQueued = false;
            Path.Clear();
            Path.AddRange(points);
            PathIndex = 0;
            PathGoal = goal;
            PathCompleted = Path.Count == 0;
            StuckSample = Position;
            StuckTimer = 0f;
            StuckStrikes = 0;
            StuckWaypoint = -1;
        }

        internal void ClearPath()
        {
            PathTrace?.Invoke(this, "ClearPath");
            PathQueued = false;
            Path.Clear();
            PathIndex = 0;
            PathCompleted = true;
        }

        internal void SetOrder(Order order)
        {
            PathTrace?.Invoke(this, $"SetOrder {order.Kind} {order.Point}");
            Order = order;
            RunTarget = EntityId.None;
            RunExtending = false;
            if (order.Kind == OrderKind.Idle) GuardPoint = Position;
            Engaged = EntityId.None;
            ResumeRoute = false;
            RepathTimer = 0f;
        }
    }
}
