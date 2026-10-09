#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// AI MASTER P3 (lane A, DECISIONS "AI MASTER P3 (lane A)"): the coordination layer's factors on the existing target
    /// score, for AI sides only (a side whose commander made its <see cref="TeamCoordination"/>; player units are untouched):
    /// spec 139 planned damage (with P0-A's in-flight damage: over 1.15 x health a unit that has not fired picks another),
    /// spec 149 stances (ReturnFire only on what shoots at the side; Defend prefers what threatens it), spec 200 handoff
    /// (the handed target weighs more for its new owner, less for the old), spec 141 coverage (an AA's aircraft over its own
    /// asset first) and spec 201 the multi-weapon director (secondary mounts on what they are made for). Infeasible targets
    /// never get here (the hard filter runs first).
    /// </summary>
    internal sealed partial class CombatSystem
    {
        private long _p3Tick = -1;
        private readonly System.Collections.Generic.HashSet<long> _p3Counted = new();

        private float P3Worth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            if (!SimTunables.Ai.Coordination.Enabled || _world.CoordinationIfAny?.Peek(v.Team) is not { } tc) return 1f;
            var now = _world.Time;
            var worth = 1f;
            var shootsUs = _world.TryGetVehicle(other.Target, out var victim) && victim.Team == v.Team;
            // Spec 149.
            switch (v.P3Stance)
            {
                case UnitStance.ReturnFire:
                    if (!StanceRules.ReturnFireAllows(shootsUs, now, v.LastHitTime)) return 0f;
                    break;
                case UnitStance.Defend:
                    worth *= shootsUs || Vector2.DistanceSquared(other.Position, v.Position) < global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P3WorthScale * global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P3WorthScale ? global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P3WorthShootsUsTrue : global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P3WorthShootsUsFalse;
                    break;
            }
            // Spec 200.
            if (now < v.P3HandoffUntil)
            {
                if (other.Id == v.P3Prefer) worth *= SimTunables.Ai.Board.PreferWorth;
                else if (other.Id == v.P3Avoid) worth *= SimTunables.Ai.Board.AvoidWorth;
            }
            // Spec 141.
            if (other.Flying && v.P3CoverAt is { } asset && weapon.CanTarget(true))
                worth *= Vector2.Distance(other.Position, asset) <= v.P3CoverRadius ? SimTunables.Ai.Coverage.CoverWorth : SimTunables.Ai.Coverage.OffWorth;
            // Spec 201.
            var index = MountOf(v, weapon);
            if (index != MainMount(v)) worth *= MountFit(v, other, weapon, index);
            // Spec 139.
            var planned = tc.Board.PlannedDamage(other.Id, v.Id, now);
            if (planned > 0f && v.Weapons[index].Target != other.Id && PlannedActionBoard.Overkill(planned, Committed(other.Id), other.Hp) &&
                !OverkillExempt(v, other) && !(v.SquadFocus == other.Id && v.SquadFocusWeight >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P3WorthSquadFocusWeightMin))
            {
                worth *= OverkillFloor;
                // Spec 225 plannedOverkillPrevented: a shooter-target pair counted once per step.
                if (_world.Tick != _p3Tick)
                {
                    _p3Tick = _world.Tick;
                    _p3Counted.Clear();
                }
                if (_p3Counted.Add(((long)v.Id.Value << 32) | (uint)other.Id.Value)) tc.Metrics.PlannedOverkillPrevented++;
            }
            return worth;
        }

        /// <summary>Spec 201: a secondary mount's fit: light guns off heavy armour, on light / air; area launchers on groups and structures.</summary>
        private float MountFit(Vehicle v, Vehicle other, WeaponDef weapon, int index)
        {
            var main = v.Arms[MainMount(v)];
            var c = ClassCached(other);
            var light = weapon.Damage < main.Damage * global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.MountFitDamageScale && weapon.SplashRadius < global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.MountFitSplashRadiusMax;
            if (light)
            {
                if (c is TargetClass.SuperHeavy or TargetClass.Armour4 or TargetClass.Heavy or TargetClass.Mbt or TargetClass.Boss) return SimTunables.Ai.Board.SecondaryHeavy;
                if (other.Flying || c is TargetClass.Light or TargetClass.Recon or TargetClass.Drone) return SimTunables.Ai.Board.SecondaryFit;
            }
            if (weapon.Burst > 1 && weapon.SplashRadius >= global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.MountFitSplashRadiusMin && (other.Def.Static || ClusteredCached(other))) return SimTunables.Ai.Board.SecondaryFit;
            if (weapon.CanTarget(true) && !weapon.CanTarget(false) && other.Flying) return SimTunables.Ai.Board.SecondaryFit;
            return 1f;
        }

        /// <summary>Spec 139: a mount that takes a new target reserves one cycle of its expected damage on it (released on change, timed out).</summary>
        private void ReserveP3(Vehicle v, int index, EntityId next)
        {
            if (!SimTunables.Ai.Coordination.Enabled || _world.CoordinationIfAny?.Peek(v.Team) is not { } tc) return;
            if (!next.IsValid || index >= v.Arms.Length || !_world.TryGetVehicle(next, out var target))
            {
                tc.Board.ReleaseDamage(v.Id, index);
                return;
            }
            var weapon = v.Arms[index];
            var expected = weapon.Damage * weapon.RoundsPerCycle * _world.Damage.Estimate(weapon, v, target);
            var now = _world.Time;
            tc.Board.ReserveDamage(next, v.Id, index, expected, now + weapon.CycleSeconds + SimTunables.Ai.Board.DamageLeadS);
        }
    }
}
