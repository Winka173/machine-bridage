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
            Hp = MaxHp = def.MaxHp;
            var sideways = rotation == 90 || rotation == 270;
            Width = sideways ? def.Depth : def.Width;
            Depth = sideways ? def.Width : def.Depth;
            // A diagonal prop (a bridge across a diagonal river) keeps the square that bounds it.
            if (rotation % 90 != 0) Width = Depth = (def.Width + def.Depth) * 0.70710677f;
        }

        public EntityId Id { get; }
        public PropDef Def { get; }
        public int Team => Teams.Neutral;
        public Vector2 Position { get; }

        /// <summary>Degrees, a multiple of 45 (diagonals only for props that are driven over, like bridges).</summary>
        public int Rotation { get; }

        /// <summary>Footprint along X after rotation.</summary>
        public float Width { get; }

        /// <summary>Footprint along Y after rotation.</summary>
        public float Depth { get; }

        public float Radius => MathF.Max(Width, Depth) * 0.5f;
        public ArmorClass Armor => Def.Armor;
        public TargetKind Kind => Def.Kind;
        public ArmourLevels Armour => Def.Armour;
        public float Hp { get; internal set; }
        /// <summary>The definition's health, unless a mission hardened this one (a demolition target).</summary>
        public float MaxHp { get; private set; }
        public bool IsAlive => Hp > 0f;

        /// <summary>Multiplies this structure's health (full health, scaled).</summary>
        /// <summary>Shielded (a siege objective whose stage has not come yet): it takes no damage.</summary>
        public bool Invulnerable { get; internal set; }

        internal void Harden(float factor)
        {
            MaxHp = Def.MaxHp * factor;
            Hp = MaxHp;
        }

        public bool Contains(Vector2 point, float margin = 0f) =>
            MathF.Abs(point.X - Position.X) <= Width * 0.5f + margin &&
            MathF.Abs(point.Y - Position.Y) <= Depth * 0.5f + margin;
    }
}
