#nullable enable
using System;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Timed effects on vehicles, each in its own fixed slot per vehicle (see <see cref="StatusKind"/>):
    /// burning (Fire damage over time, half repair), slowed, shredded (takes more damage from
    /// everyone), marked (one side deals more damage), a barrier that soaks damage, and the buffs
    /// equipment auras hand out. Negative effects are shortened by Fire Extinguisher (and burns by
    /// a fire-retardant hull) and blocked for a moment after Damage Control cleanses them.
    /// </summary>
    internal sealed class StatusSystem
    {
        private readonly SimWorld _world;

        public StatusSystem(SimWorld world) => _world = world;

        public void Step(float dt)
        {
            var now = _world.Time;
            var list = _world.VehicleList;
            for (var i = 0; i < list.Count; i++)
            {
                var v = list[i];
                if (!v.IsAlive) continue;
                v.LastStatusCheck = now;
                ref var burn = ref v.Statuses[(int)StatusKind.Burn];
                if (burn.Until > now && burn.Value > 0f)
                {
                    _world.TryGetVehicle(burn.Source, out var lighter);
                    _world.Damage.Burn(v, burn.Value * dt, lighter, burn.Team, burn.Source);
                }
                ref var shred = ref v.Statuses[(int)StatusKind.Shred];
                if (shred.Stacks > 0 && shred.Until <= now) shred.Stacks = 0;
            }
        }

        public static bool Has(Vehicle v, StatusKind kind, double now) => v.Statuses[(int)kind].Until > now;

        public bool Burning(Vehicle v) => Has(v, StatusKind.Burn, _world.Time);

        /// <summary>How long a negative effect lasts on this vehicle, against its nominal length.</summary>
        public static float DurationFactor(Vehicle v, bool fire)
        {
            if (v.Gear == null) return 1f;
            var f = 1f - Math.Clamp(v.Gear.Stat(StatId.StatusDuration), 0f, 0.6f);
            if (fire) f *= 1f - Math.Clamp(v.Gear.Stat(StatId.ResistFire) * 2f, 0f, 0.5f);
            return f;
        }

        private bool Cleansed(Vehicle v) => Has(v, StatusKind.Cleansed, _world.Time);

        /// <summary>
        /// Sets it on fire: <paramref name="dps"/> Fire damage a second for <paramref name="seconds"/>; a
        /// stronger fire replaces a weaker one. <paramref name="stack"/> (Incendiary Rounds): the new fire
        /// adds to what is still to burn, spread over its seconds (a fast gun's many small fires add up).
        /// </summary>
        public void Burn(Vehicle target, float dps, float seconds, int team, EntityId source, bool firestorm = false, bool stack = false)
        {
            if (!target.IsAlive || dps <= 0f || Cleansed(target) || target.Team == team) return;
            var now = _world.Time;
            seconds *= DurationFactor(target, true);
            ref var s = ref target.Statuses[(int)StatusKind.Burn];
            if (stack && s.Until > now && s.Value > 0f)
            {
                var left = s.Value * (float)(s.Until - now);
                s.Value = (left + dps * seconds) / seconds;
                s.Until = now + seconds;
                s.Team = team;
                s.Source = source;
                s.Flag |= firestorm;
                return;
            }
            if (s.Until <= now || dps >= s.Value)
            {
                s.Value = dps;
                s.Team = team;
                s.Source = source;
                s.Flag = firestorm;
            }
            else s.Flag |= firestorm;
            s.Until = Math.Max(s.Until, now + seconds);
        }

        /// <summary>Slows it by <paramref name="share"/> (half on aircraft); slows do not stack, the stronger holds.</summary>
        public void Slow(Vehicle target, float share, float seconds)
        {
            if (!target.IsAlive || share <= 0f || Cleansed(target)) return;
            var now = _world.Time;
            if (target.Flying) share *= 0.5f;
            seconds *= DurationFactor(target, false);
            ref var s = ref target.Statuses[(int)StatusKind.Slow];
            s.Value = s.Until > now ? Math.Max(s.Value, share) : share;
            s.Until = Math.Max(s.Until, now + seconds);
        }

        /// <summary>
        /// <paramref name="stacks"/> more stacks of shred (up to <paramref name="maxStacks"/>; a fraction
        /// is kept towards the next), each making it take <paramref name="perStack"/> more damage.
        /// </summary>
        public void Shred(Vehicle target, float perStack, float seconds, int maxStacks = 5, float stacks = 1f)
        {
            if (!target.IsAlive || perStack <= 0f || Cleansed(target)) return;
            var now = _world.Time;
            ref var s = ref target.Statuses[(int)StatusKind.Shred];
            if (s.Until <= now)
            {
                s.Stacks = 0;
                s.Extra = 0f;
            }
            s.Extra += stacks;
            var whole = (int)MathF.Floor(s.Extra);
            s.Extra -= whole;
            s.Stacks = Math.Min(maxStacks, s.Stacks + whole);
            s.Value = Math.Max(s.Until > now ? s.Value : 0f, perStack);
            s.Until = now + seconds * DurationFactor(target, false);
        }

        /// <summary>Suppressive fire: it fires <paramref name="share"/> slower for <paramref name="seconds"/> (the stronger holds).</summary>
        public void Suppress(Vehicle target, float share, float seconds)
        {
            if (!target.IsAlive || share <= 0f || Cleansed(target)) return;
            var now = _world.Time;
            seconds *= DurationFactor(target, false);
            ref var s = ref target.Statuses[(int)StatusKind.Suppressed];
            s.Value = s.Until > now ? Math.Max(s.Value, share) : share;
            s.Until = Math.Max(s.Until, now + seconds);
        }

        /// <summary>Marks it for <paramref name="team"/>: that side deals <paramref name="bonus"/> more damage to it, its artillery reaches <paramref name="reach"/> farther.</summary>
        public void Mark(Vehicle target, float bonus, float seconds, int team, float reach)
        {
            if (!target.IsAlive) return;
            ref var s = ref target.Statuses[(int)StatusKind.Mark];
            s.Value = s.Until > _world.Time && s.Team == team ? Math.Max(s.Value, bonus) : bonus;
            s.Team = team;
            s.Extra = reach;
            s.Until = _world.Time + seconds;
        }

        /// <summary>A barrier of <paramref name="amount"/> hit points (a bigger one replaces a smaller).</summary>
        public void AddBarrier(Vehicle target, float amount)
        {
            if (!target.IsAlive || amount <= 0f) return;
            ref var s = ref target.Statuses[(int)StatusKind.Barrier];
            s.Value = Math.Max(s.Value, amount);
            s.Until = double.PositiveInfinity;
        }

        /// <summary>What is left of a hit after the barrier soaks what it can.</summary>
        public float Absorb(Vehicle v, float damage)
        {
            ref var s = ref v.Statuses[(int)StatusKind.Barrier];
            if (s.Value <= 0f || damage <= 0f) return damage;
            var soaked = Math.Min(s.Value, damage);
            s.Value -= soaked;
            if (s.Value <= 0.01f)
            {
                s.Value = 0f;
                s.Until = 0;
            }
            return damage - soaked;
        }

        /// <summary>Knocked out (an EMP) until <paramref name="until"/>, unless just cleansed; shortened by Fire Extinguisher and a tower's Backup Generator.</summary>
        public void Stun(Vehicle target, double until)
        {
            if (!target.IsAlive || Cleansed(target)) return;
            var now = _world.Time;
            var seconds = _world.Gear.StunSeconds(target, (float)(until - now));
            if (seconds <= 0f) return;
            until = now + seconds;
            var factor = DurationFactor(target, false);
            if (factor < 1f) until = now + (until - now) * factor;
            target.StunnedUntil = Math.Max(target.StunnedUntil, until);
        }

        /// <summary>Whether it has any effect Damage Control would clear.</summary>
        public bool Afflicted(Vehicle v)
        {
            var now = _world.Time;
            return Has(v, StatusKind.Burn, now) || Has(v, StatusKind.Slow, now) || (Has(v, StatusKind.Shred, now) && v.Statuses[(int)StatusKind.Shred].Stacks > 0) ||
                   v.StunnedUntil > now;
        }

        /// <summary>Clears burning, slows, shred and stuns, and keeps new ones off for <paramref name="immune"/> seconds.</summary>
        public void Cleanse(Vehicle v, float immune)
        {
            var now = _world.Time;
            v.Statuses[(int)StatusKind.Burn].Until = 0;
            v.Statuses[(int)StatusKind.Slow].Until = 0;
            v.Statuses[(int)StatusKind.Shred].Until = 0;
            v.Statuses[(int)StatusKind.Shred].Stacks = 0;
            v.Statuses[(int)StatusKind.Suppressed].Until = 0;
            if (v.StunnedUntil > now) v.StunnedUntil = now;
            v.Statuses[(int)StatusKind.Cleansed].Until = now + immune;
            v.RefreshEffects(now);
        }

        /// <summary>The share of speed a slow takes off now.</summary>
        public static float SlowShare(Vehicle v, double now) => Has(v, StatusKind.Slow, now) ? v.Statuses[(int)StatusKind.Slow].Value : 0f;
    }
}
