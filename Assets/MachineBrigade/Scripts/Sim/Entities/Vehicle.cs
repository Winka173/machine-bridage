#nullable enable
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
            Order = Order.Idle;
            PathCompleted = true;
            GuardPoint = position;
            Weapons = new WeaponState[def.Mounts.Count];
            for (var i = 0; i < Weapons.Length; i++) Weapons[i] = new WeaponState { Heading = heading };
        }

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
        public float MaxHp => Def.MaxHp;
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

        internal int PathIndex;
        internal bool PathCompleted;
        internal Vector2 PathGoal;
        internal float RepathTimer;

        /// <summary>Enemy an attack-moving vehicle broke off its route to fight.</summary>
        internal EntityId Engaged;

        internal bool ResumeRoute;

        /// <summary>Where an idle vehicle stands guard; it drives back here after a skirmish.</summary>
        internal Vector2 GuardPoint;

        /// <summary>Carrying out an order the player gave by hand.</summary>
        internal bool ManualOrder;

        /// <summary>Until when (sim time) the commander AI keeps its hands off after a manual order.</summary>
        internal double ManualUntil = double.NegativeInfinity;

        /// <summary>The player took direct control of this vehicle recently.</summary>
        public bool UnderPlayerControl(double now) => ManualOrder || now < ManualUntil;

        /// <summary>Last enemy vehicle that hurt this one, so idle vehicles answer fire.</summary>
        internal EntityId LastAttacker;

        /// <summary>Simulation time of the last hit from <see cref="LastAttacker"/>.</summary>
        internal double LastHitTime = double.NegativeInfinity;

        internal Vector2 StuckSample;
        internal float StuckTimer;
        internal int StuckStrikes;

        internal bool HasPath => PathIndex < Path.Count;

        internal void SetPath(List<Vector2> points, Vector2 goal)
        {
            Path.Clear();
            Path.AddRange(points);
            PathIndex = 0;
            PathGoal = goal;
            PathCompleted = Path.Count == 0;
            StuckSample = Position;
            StuckTimer = 0f;
            StuckStrikes = 0;
        }

        internal void ClearPath()
        {
            Path.Clear();
            PathIndex = 0;
            PathCompleted = true;
        }

        internal void SetOrder(Order order)
        {
            Order = order;
            if (order.Kind == OrderKind.Idle) GuardPoint = Position;
            Engaged = EntityId.None;
            ResumeRoute = false;
            RepathTimer = 0f;
        }
    }
}
