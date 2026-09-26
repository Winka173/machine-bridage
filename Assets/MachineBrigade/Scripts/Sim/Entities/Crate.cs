#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>
    /// A supply crate parachuted into the middle of a battle. The first side to hold the ground
    /// around it (a vehicle beside it and no enemy) claims it: a CP bonus and field repairs.
    /// </summary>
    public sealed class Crate
    {
        internal Crate(EntityId id, Vector2 position, double landsAt, double expiresAt)
        {
            Id = id;
            Position = position;
            LandsAt = landsAt;
            ExpiresAt = expiresAt;
        }

        public EntityId Id { get; }
        public Vector2 Position { get; }

        /// <summary>When it touches down (it is falling until then).</summary>
        public double LandsAt { get; }

        /// <summary>Unclaimed crates are lost after this.</summary>
        internal double ExpiresAt { get; }

        public bool IsAlive { get; internal set; } = true;

        /// <summary>Team currently holding it and how far the claim has got (0-1).</summary>
        public int Holder { get; internal set; } = -1;

        public float Claim { get; internal set; }
    }
}
