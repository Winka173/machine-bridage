#nullable enable
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// AI MASTER P2 (lane C, DECISIONS "AI MASTER P2 (lane C)"): Part B's role ladders for every role P0-A did not cover
    /// (B4-B13, F1's screen) and Part I's mode target weights, as factors on the existing score. Main weapon only (a tank's
    /// machine gun keeps the generic score). Infeasible targets never get here (the hard filter runs first). Caches are per
    /// step (roles, clusters) or per entity (target classes); deterministic.
    /// </summary>
    internal sealed partial class CombatSystem
    {
        private readonly Dictionary<EntityId, (long tick, DoctrineRole role)> _roleCache = new();
        private readonly Dictionary<EntityId, TargetClass> _classCache = new();
        private readonly Dictionary<EntityId, (long tick, bool clustered)> _clusterCache = new();

        internal DoctrineRole RoleCached(Vehicle v)
        {
            var tick = _world.Tick;
            if (_roleCache.TryGetValue(v.Id, out var c) && c.tick == tick) return c.role;
            var role = CombatRoleDoctrine.RoleOf(_world, v);
            if (_roleCache.Count > 4096) _roleCache.Clear();
            _roleCache[v.Id] = (tick, role);
            return role;
        }

        internal TargetClass ClassCached(Vehicle t)
        {
            if (_classCache.TryGetValue(t.Id, out var c)) return c;
            c = CombatRoleDoctrine.ClassOf(_world, t);
            if (_classCache.Count > 8192) _classCache.Clear();
            _classCache[t.Id] = c;
            return c;
        }

        private bool ClusteredCached(Vehicle t)
        {
            var tick = _world.Tick;
            if (_clusterCache.TryGetValue(t.Id, out var c) && c.tick == tick) return c.clustered;
            var clustered = CombatRoleDoctrine.Clustered(_world, t);
            if (_clusterCache.Count > 4096) _clusterCache.Clear();
            _clusterCache[t.Id] = (tick, clustered);
            return clustered;
        }

        /// <summary>Part B B4-B13 / F1: the role ladder's factor for <paramref name="v"/>'s main weapon on <paramref name="other"/>.</summary>
        private float P2RoleWorth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            if (MountOf(v, weapon) != MainMount(v) && !(v.Def.Deploy is { Siege: true })) return 1f;
            var role = RoleCached(v);
            if (role is DoctrineRole.Generic or DoctrineRole.Recon or DoctrineRole.Support or DoctrineRole.Breacher or DoctrineRole.Siege) return 1f;
            var c = ClassCached(other);
            var survival = ImmediateSurvivalThreat(v, other) || ThreatensNear(v, other);
            var objective = ThreatToObjective(v, other);
            var needsCluster = role is DoctrineRole.FireSupport or DoctrineRole.Bomber;
            var clustered = needsCluster && ClusteredCached(other);
            var onOurHeavy = _world.TryGetVehicle(other.Target, out var victim) && victim.Team == v.Team &&
                             victim.Def.Class is UnitClass.Tank or UnitClass.Heavy;
            var salvo = weapon.Burst > 1 && weapon.MinRange > 0f;
            return CombatRoleDoctrine.Worth(role, c, survival, objective, clustered, onOurHeavy, other.IsMoving, Worth(other), salvo);
        }

        /// <summary>B5 "immediate threat to self / squad": aiming at one of our vehicles within 15 m of this one, able to hit it.</summary>
        private bool ThreatensNear(Vehicle v, Vehicle other)
        {
            if (!_world.TryGetVehicle(other.Target, out var victim) || victim.Team != v.Team || victim == v) return false;
            if (Vector2.DistanceSquared(victim.Position, v.Position) > 15f * 15f) return false;
            var w = other.Def.Weapon;
            return w.Damage > 0f && w.CanTarget(victim.Flying) && Vector2.Distance(other.Position, victim.Position) - victim.Radius <= w.Range;
        }

        /// <summary>Part I ObjectiveTargetWeights of the battle's mode doctrine for <paramref name="v"/> on <paramref name="other"/>.</summary>
        private float P2ModeWorth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            var doctrine = _world.Doctrine;
            var d = doctrine.For(v.Team);
            if (ReferenceEquals(d, ModeCombatDoctrine.Get(ModeCombatDoctrine.Base)) && doctrine.Stage == ShowdownStage.None) return 1f;
            var role = RoleCached(v);
            var c = ClassCached(other);
            var mission = doctrine.MissionTargetOf(v.Team) == other.Id;
            // Only the air-first and quiet doctrines ask whether it threatens the mission (Part H's factor is P0-A's already).
            var threatens = (d.AirFirst || d.QuietStrikes) &&
                            (ThreatToObjective(v, other) > 0f ||
                             (_world.TryGetVehicle(other.Target, out var victim) && victim.Team == v.Team &&
                              (victim.Def.Static || victim.Def.Class == UnitClass.AntiAir)));
            return ModeCombatDoctrine.TargetWeight(d, doctrine.Stage, role, c, mission, threatens, other.IsEscort, Worth(other));
        }
    }
}
