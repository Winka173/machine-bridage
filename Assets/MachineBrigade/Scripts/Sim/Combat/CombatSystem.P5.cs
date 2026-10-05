#nullable enable
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// AI MASTER P5 (lane A, DECISIONS "AI MASTER P5 (lane A)"): Part N tower coordination on the target score of an AI side's
    /// towers (the tower mode stays the base, <see cref="TowerCoordination"/> adds the protected-zone, AT, anti-artillery,
    /// critical-threat and cross-tower overkill factors) and Part L's target keeping during a reload. Player units and player
    /// towers are untouched (the same rule as P3: AI sides only, a side with a commander).
    /// </summary>
    internal sealed partial class CombatSystem
    {
        private long _p5Tick = -1;
        private readonly Dictionary<(int team, int target), float> _towerDamage = new();

        /// <summary>Part N: an AI side's tower's coordination factor (1 for anything else).</summary>
        private float P5Worth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            if (!SimTunables.Ai.Towers.Enabled || !v.Def.Static || v.Def.Boss || weapon.InterceptOnly || !_world.AiCommanders.ContainsKey(v.Team)) return 1f;
            var kind = TowerKindOf(v, weapon);
            var c = ClassCached(other);
            var hq = _world.Bases.Of(v.Team);
            var protectR = SimTunables.Ai.Towers.ProtectRadius;
            var critR = SimTunables.Ai.Towers.CriticalRadius;
            var shootsHq = hq != null && other.Target == hq.Hq;
            var nearHq = hq != null && Vector2.DistanceSquared(other.Position, hq.HqPosition) <= critR * critR;
            var threatZone = other.Flying && (hq != null && Vector2.DistanceSquared(other.Position, hq.HqPosition) <= protectR * protectR ||
                                              _world.TryGetVehicle(other.Target, out var aimed) && aimed.Team == v.Team && aimed.Def.Static);
            var mine = v.Target == other.Id || v.Weapons[MountOf(v, weapon)].Target == other.Id;
            var facts = new TowerTargetFacts(other.Flying, threatZone,
                c is TargetClass.SuperHeavy or TargetClass.Armour4 or TargetClass.Heavy or TargetClass.Mbt,
                c is TargetClass.Artillery or TargetClass.Support or TargetClass.SamRadar,
                shootsHq || nearHq && !other.Flying, OtherTowersDamage(v, other), other.Hp, mine);
            var worth = TowerCoordination.Worth(kind, facts);
            if (worth != 1f)
            {
                var health = _world.Health.Counters;
                if (TowerCoordination.Overkill(facts)) health.TowerOverkillAvoided++;
                if (facts.CriticalObjectiveThreat) health.TowerCriticalOverrides++;
            }
            return worth;
        }

        /// <summary>What a tower's mount is for (its weapon; a drone hangar counts as fire support).</summary>
        internal static TowerKind TowerKindOf(Vehicle v, WeaponDef weapon)
        {
            var kind = TowerKind.None;
            if (weapon.InterceptOnly) kind |= TowerKind.Defence;
            if (weapon.CanTarget(true)) kind |= TowerKind.AntiAir;
            if (weapon.AntiArmour && !weapon.Indirect) kind |= TowerKind.AntiTank;
            if (weapon.Indirect || v.Def.Id == "drone_hangar") kind |= TowerKind.FireSupport;
            return kind;
        }

        /// <summary>One cycle of damage of every other friendly tower already on <paramref name="target"/> (cached per step and side).</summary>
        private float OtherTowersDamage(Vehicle tower, Vehicle target)
        {
            if (_world.Tick != _p5Tick)
            {
                _p5Tick = _world.Tick;
                _towerDamage.Clear();
                foreach (var t in _world.VehicleList)
                {
                    if (!t.IsAlive || !t.Def.Static || t.Def.Boss || !t.Target.IsValid || !_world.AiCommanders.ContainsKey(t.Team)) continue;
                    var w = t.Arms.Length > 0 ? t.Arms[0] : t.Def.Weapon;
                    var key = (t.Team, t.Target.Value);
                    _towerDamage[key] = (_towerDamage.TryGetValue(key, out var d) ? d : 0f) + w.Damage * w.RoundsPerCycle;
                }
            }
            var sum = _towerDamage.TryGetValue((tower.Team, target.Id.Value), out var total) ? total : 0f;
            if (tower.Target == target.Id)
            {
                var own = tower.Arms.Length > 0 ? tower.Arms[0] : tower.Def.Weapon;
                sum -= own.Damage * own.RoundsPerCycle;
            }
            return sum > 0f ? sum : 0f;
        }

        /// <summary>
        /// Part L: an AI unit's mount reloading a meaningful magazine keeps its still-valid target until it can fire again (no
        /// re-scoring churn; the turret stays laid). Counted on the health monitor.
        /// </summary>
        private bool KeepWhileReloadingP5(Vehicle v, WeaponDef weapon)
        {
            if (!SimTunables.Ai.Ammo.Enabled || !_world.AiCommanders.ContainsKey(v.Team)) return false;
            var index = MountOf(v, weapon);
            if (!AmmoTactics.KeepTarget(AmmoTactics.Read(_world, v, index), true)) return false;
            _world.Health.Counters.TargetsKeptReloading++;
            return true;
        }
    }
}
