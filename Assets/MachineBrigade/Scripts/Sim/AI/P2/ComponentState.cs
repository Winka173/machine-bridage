#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P2 Part F: what a vehicle can still do. Capability, never health: a vehicle at 5 % with its gun and engine
    /// is a full combatant; one at 90 % with its main gun's part broken is a screen. Nothing here sends anything home.
    /// </summary>
    public readonly struct ComponentState : IEquatable<ComponentState>
    {
        public ComponentState(bool mainGunLost, bool engineCrippled, bool radarLost, bool apsLost, int workingMounts)
        {
            MainGunLost = mainGunLost;
            EngineCrippled = engineCrippled;
            RadarLost = radarLost;
            ApsLost = apsLost;
            WorkingMounts = workingMounts;
        }

        /// <summary>F1: the main weapon's mount is out for good (its part broken), not a siege-mode or big-attack hold.</summary>
        public bool MainGunLost { get; }

        /// <summary>F2: the speed left (parts, slowing effects) is under ai.componentState.engineCrippledShare.</summary>
        public bool EngineCrippled { get; }

        /// <summary>F3: a fire-control / search radar destroyed (a part flag).</summary>
        public bool RadarLost { get; }

        /// <summary>F4: an active protection system or shield the vehicle had is gone.</summary>
        public bool ApsLost { get; }

        /// <summary>F5: a bit per mount whose part still stands (the first 31 mounts), for a boss's broadside recompute.</summary>
        public int WorkingMounts { get; }

        public bool Degraded => MainGunLost || EngineCrippled || RadarLost || ApsLost;

        public bool Equals(ComponentState o) => MainGunLost == o.MainGunLost && EngineCrippled == o.EngineCrippled && RadarLost == o.RadarLost &&
                                               ApsLost == o.ApsLost && WorkingMounts == o.WorkingMounts;

        public override bool Equals(object? obj) => obj is ComponentState o && Equals(o);

        public override int GetHashCode() => WorkingMounts * 31 + (MainGunLost ? 1 : 0) + (EngineCrippled ? 2 : 0) + (RadarLost ? 4 : 0) + (ApsLost ? 8 : 0);

        public override string ToString() =>
            $"{(MainGunLost ? "mainGunLost " : "")}{(EngineCrippled ? "engineCrippled " : "")}{(RadarLost ? "radarLost " : "")}{(ApsLost ? "apsLost " : "")}".Trim();

        /// <summary>The state of <paramref name="v"/> now.</summary>
        public static ComponentState Of(Vehicle v, double now)
        {
            var main = CombatSystem.MainMount(v);
            var mainLost = main < v.MountOff.Length && v.MountOff[main];
            var slow = StatusSystem.SlowShare(v, now);
            var speedLeft = MathF.Min(v.PartSpeed, 1f - slow);
            var crippled = v.Def.Speed > 0f && !v.Def.Static && speedLeft < Tun.ComponentState.EngineCrippledShare;
            var mask = 0;
            for (var i = 0; i < v.Def.Mounts.Count && i < 31; i++)
                if (i >= v.MountOff.Length || !v.MountOff[i]) mask |= 1 << i;
            return new ComponentState(mainLost, crippled, v.RadarOff, v.Aps != null && v.ApsOff, mask);
        }
    }

    /// <summary>
    /// AI MASTER P2 Part F: the battle's record of each vehicle's last component state, so a change is noticed once, logged
    /// with its reason code, and the layers that care (squad slots, flank scoring, the role doctrine, a boss's broadside)
    /// re-read it. Read on demand (no step of its own); deterministic (the caller's order).
    /// </summary>
    public sealed class ComponentWatch
    {
        private readonly SimWorld _world;
        private readonly Dictionary<EntityId, ComponentState> _last = new();

        internal ComponentWatch(SimWorld world) => _world = world;

        /// <summary>The state now (no log).</summary>
        public ComponentState Of(Vehicle v) => ComponentState.Of(v, _world.Time);

        /// <summary>The state now; on a change since the last look, the Part F reason codes are logged and true returned.</summary>
        public bool Check(Vehicle v, out ComponentState now)
        {
            now = ComponentState.Of(v, _world.Time);
            if (!_last.TryGetValue(v.Id, out var before))
            {
                _last[v.Id] = now;
                if (_last.Count > 4096) Prune();
                if (!now.Degraded) return false;
                before = new ComponentState(false, false, false, false, now.WorkingMounts);
            }
            if (before.Equals(now)) return false;
            _last[v.Id] = now;
            if (now.MainGunLost && !before.MainGunLost) P2Reasons.Unit(_world, v, DecisionKind.State, P2Reasons.RoleMainGunLost);
            if (now.EngineCrippled && !before.EngineCrippled) P2Reasons.Unit(_world, v, DecisionKind.State, P2Reasons.RoleEngineCrippled);
            if (now.RadarLost && !before.RadarLost) P2Reasons.Unit(_world, v, DecisionKind.State, P2Reasons.RoleRadarLost);
            if (now.ApsLost && !before.ApsLost) P2Reasons.Unit(_world, v, DecisionKind.State, P2Reasons.RoleApsLost);
            if (before.Degraded && !now.Degraded) P2Reasons.Unit(_world, v, DecisionKind.State, P2Reasons.RoleRestored);
            return true;
        }

        /// <summary>F5: whether a boss's set of working mounts changed since the last look (its broadside must be recomputed).</summary>
        public bool MountsChanged(Vehicle boss)
        {
            var before = _last.TryGetValue(boss.Id, out var b) ? b.WorkingMounts : -1;
            Check(boss, out var now);
            return before >= 0 && before != now.WorkingMounts;
        }

        private void Prune()
        {
            var dead = new List<EntityId>();
            foreach (var id in _last.Keys)
                if (!_world.TryGetVehicle(id, out var v) || !v.IsAlive) dead.Add(id);
            foreach (var id in dead) _last.Remove(id);
        }
    }
}
