using System;
using System.Collections.Generic;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Fixed-capacity pool. When every instance is busy the oldest one is replayed, so a
    /// huge battle costs a bounded amount and only visuals are lost, never gameplay (T02).
    /// </summary>
    internal sealed class EffectPool
    {
        private readonly List<ExplosionEffect> _items = new();
        private readonly Func<ExplosionEffect> _create;
        private readonly int _capacity;

        public EffectPool(Func<ExplosionEffect> create, int capacity)
        {
            _create = create;
            _capacity = Math.Max(1, capacity);
        }

        public ExplosionEffect Acquire(float now)
        {
            ExplosionEffect oldest = null;
            foreach (var item in _items)
            {
                if (!item.IsBusy(now)) return item;
                if (oldest == null || item.PlayedAt < oldest.PlayedAt) oldest = item;
            }
            if (_items.Count < _capacity)
            {
                var created = _create();
                _items.Add(created);
                return created;
            }
            return oldest;
        }
    }
}
