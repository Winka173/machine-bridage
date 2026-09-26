#nullable enable
using System;

namespace MachineBrigade.Sim.Core
{
    /// <summary>
    /// Stable identity of a simulation entity. Ids are never reused within a match, so a
    /// reference held by the UI or a queued command can only ever resolve to the entity it
    /// was taken from (or to nothing once that entity is gone).
    /// </summary>
    public readonly struct EntityId : IEquatable<EntityId>
    {
        public static readonly EntityId None = default;

        public EntityId(int value) => Value = value;

        public int Value { get; }

        public bool IsValid => Value > 0;

        public bool Equals(EntityId other) => Value == other.Value;

        public override bool Equals(object? obj) => obj is EntityId other && Equals(other);

        public override int GetHashCode() => Value;

        public override string ToString() => IsValid ? $"#{Value}" : "#none";

        public static bool operator ==(EntityId a, EntityId b) => a.Value == b.Value;

        public static bool operator !=(EntityId a, EntityId b) => a.Value != b.Value;
    }
}
