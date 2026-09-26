#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    public enum OrderKind
    {
        /// <summary>Holds position and fires at visible enemies in weapon range.</summary>
        Idle,

        /// <summary>Drives to a point. Never chases; turreted vehicles may fire on the way.</summary>
        Move,

        /// <summary>Hunts one chosen target until it dies.</summary>
        Attack,

        /// <summary>Advances, engages anything spotted on the way, then resumes the route.</summary>
        AttackMove,

        /// <summary>Like Move, back to the team's rally point.</summary>
        Retreat,
    }

    /// <summary>
    /// The player's (or AI's) explicit instruction to one vehicle. Automatic targeting is
    /// tracked separately and can never replace this.
    /// </summary>
    public readonly struct Order
    {
        public Order(OrderKind kind, Vector2 point, EntityId target)
        {
            Kind = kind;
            Point = point;
            Target = target;
        }

        public static Order Idle => default;

        public OrderKind Kind { get; }

        /// <summary>Destination for movement orders (this vehicle's formation slot).</summary>
        public Vector2 Point { get; }

        public EntityId Target { get; }
    }
}
