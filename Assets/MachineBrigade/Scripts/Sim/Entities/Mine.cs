#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>An anti-tank mine: buried by a mine layer, set off by the first enemy ground vehicle over it.</summary>
    public sealed class Mine
    {
        internal Mine(EntityId id, int team, EntityId layer, Vector2 position, MineLayerDef def, double armedAt)
        {
            Id = id;
            Team = team;
            Layer = layer;
            Position = position;
            Def = def;
            ArmedAt = armedAt;
        }

        public EntityId Id { get; }
        public int Team { get; }

        /// <summary>The vehicle that laid it.</summary>
        public EntityId Layer { get; }

        public Vector2 Position { get; }
        internal MineLayerDef Def { get; }

        /// <summary>A fresh mine is harmless for a moment, so the layer drives off it.</summary>
        internal double ArmedAt { get; }

        public bool IsAlive { get; internal set; } = true;

        /// <summary>When a scattered mine clears itself (never for a mine layer's).</summary>
        internal double ExpiresAt { get; set; } = double.PositiveInfinity;

        /// <summary>Bit per team that can see it: always the owner, the enemy only up close.</summary>
        public int VisibleToMask { get; internal set; }

        public bool IsVisibleTo(int team) => team >= 0 && (VisibleToMask & (1 << team)) != 0;
    }
}
