#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>A neutral map object: building, wall, tree, barrel, fuel tank.</summary>
    public sealed class Prop : IDamageable
    {
        internal Prop(EntityId id, PropDef def, Vector2 position, int rotation)
        {
            Id = id;
            Def = def;
            Position = position;
            Rotation = rotation;
            Hp = def.MaxHp;
            var sideways = rotation == 90 || rotation == 270;
            Width = sideways ? def.Depth : def.Width;
            Depth = sideways ? def.Width : def.Depth;
        }

        public EntityId Id { get; }
        public PropDef Def { get; }
        public int Team => Teams.Neutral;
        public Vector2 Position { get; }

        /// <summary>Degrees: 0, 90, 180 or 270.</summary>
        public int Rotation { get; }

        /// <summary>Footprint along X after rotation.</summary>
        public float Width { get; }

        /// <summary>Footprint along Y after rotation.</summary>
        public float Depth { get; }

        public float Radius => MathF.Max(Width, Depth) * 0.5f;
        public ArmorClass Armor => Def.Armor;
        public float Hp { get; internal set; }
        public float MaxHp => Def.MaxHp;
        public bool IsAlive => Hp > 0f;

        public bool Contains(Vector2 point, float margin = 0f) =>
            MathF.Abs(point.X - Position.X) <= Width * 0.5f + margin &&
            MathF.Abs(point.Y - Position.Y) <= Depth * 0.5f + margin;
    }
}
