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
    public sealed class Vehicle : IDamageable
    {
        internal readonly List<Vector2> Path = new();

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
            for (var i = 0; i < Weapons.Length; i++)
            {
                var ammo = def.Mounts[i].Weapon.Ammo;
                Weapons[i] = new WeaponState { Heading = heading, Ammo = ammo > 0 ? ammo : -1 };
            }
            SkillReadyAt = new double[def.Skills.Count];
            SkillUsed = new bool[def.Skills.Count];
        }

        /// <summary>Rounds left for mount <paramref name="index"/>, or -1 when unlimited.</summary>
        public int Ammo(int index) => Weapons[index].Ammo;

        /// <summary>Some limited weapon is not full.</summary>
        internal bool NeedsAmmo
        {
            get
            {
                for (var i = 0; i < Weapons.Length; i++)
                {
                    var max = Def.Mounts[i].Weapon.Ammo;
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
                var weapon = Def.Mounts[0].Weapon;
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

        /// <summary>A barrage skill is running: the guns fire much faster.</summary>
        public bool Barraging { get; private set; }

        /// <summary>Drive speed multiplier from skills.</summary>
        internal float SpeedFactor => (Overdriven ? OverdriveSpeed : 1f) * DoctrineSpeed;

        /// <summary>Fire-rate multiplier from skills.</summary>
        internal float FireFactor => (Barraging ? BarrageRate : 1f) * (Overdriven ? 1.3f : 1f) * FireBoost;

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
        public int Team { get; }
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
        internal float SpecialPower;

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
        internal Vector2 PathGoal;
        internal float RepathTimer;

        /// <summary>Enemy an attack-moving vehicle broke off its route to fight.</summary>
        internal EntityId Engaged;

        /// <summary>Distance to what the main weapon is aimed at (0 with no target); drives the barrel's elevation.</summary>
        public float AimDistance { get; internal set; }

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

        /// <summary>When the last main-gun, missile or rocket shot left this vehicle (its weapons take turns).</summary>
        internal double HeavyShotAt = double.NegativeInfinity;

        /// <summary>Which way round an obstacle the hull is edging (+1 or -1), and until when it keeps to it.</summary>
        internal float SlideSide;
        internal double SlideUntil = double.NegativeInfinity;

        internal bool HasPath => PathIndex < Path.Count;

        /// <summary>Diagnostics hook (tests only): told whenever a vehicle's path or order changes.</summary>
        internal static Action<Vehicle, string>? PathTrace;

        internal void SetPath(List<Vector2> points, Vector2 goal)
        {
            PathTrace?.Invoke(this, $"SetPath {points.Count} to {goal}");
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
