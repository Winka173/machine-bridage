#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>Anything a weapon can hit: vehicles and props.</summary>
    public interface IDamageable
    {
        EntityId Id { get; }

        /// <summary>Owning team, or <see cref="Teams.Neutral"/> for props.</summary>
        int Team { get; }

        Vector2 Position { get; }
        float Radius { get; }
        ArmorClass Armor { get; }

        /// <summary>Prompt 15: what the damage-type table reads it as (ground, air, structure).</summary>
        TargetKind Kind { get; }

        /// <summary>Prompt 15 A: its armour level on each face, from its definition.</summary>
        ArmourLevels Armour { get; }
        float Hp { get; }
        float MaxHp { get; }
        bool IsAlive { get; }
    }

    public static class Teams
    {
        public const int Neutral = -1;

        /// <summary>
        /// Neutral and hostile to everyone (a watchtower on a capture point): it fires on every side
        /// and every side fires on it.
        /// </summary>
        public const int Hostile = 2;

        /// <summary>Source team for environmental blasts, which hurt every side.</summary>
        public const int Environment = -2;
    }
}
