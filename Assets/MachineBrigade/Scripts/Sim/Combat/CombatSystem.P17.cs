#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>Prompt 17 C: the new units' part in combat (the laser's ramp, the wingman's decoy, the swarm, the bunker's arc, the relay and dome priorities).</summary>
    internal sealed partial class CombatSystem
    {
        /// <summary>An enemy CP relay is worth this much more as a target (prompt 17 C.8: the attackers go for the relays first).</summary>
        internal const float RelayPriority = 6f;

        /// <summary>A stealth fighter's bombs weigh an air defence this much more (it hunts them).</summary>
        internal const float SeadPriority = 3f;

        /// <summary>The prompt 17 target weights for <see cref="BestInRange"/>.</summary>
        private float NewContentWorth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            var f = _world.Domes.TargetWorth(v, other, weapon);
            if (other.Def.Relay != null) f *= RelayPriority;
            if (v.Def.Sead && weapon.Projectile == ProjectileKind.Bomb && !other.Flying && IsAirDefence(other.Def)) f *= SeadPriority;
            return f;
        }

        /// <summary>A ground air defence (an anti-air vehicle, or a tower with an anti-air gun or missiles: the SEAD strike's list).</summary>
        internal static bool IsAirDefence(VehicleDef def) => !def.Flying && Strikes.StrikeSystem.IsAirDefence(def);

        /// <summary>
        /// The focused laser's ramp: the multiplier for this round, x0.3 on a new target up to x2 after 6 s on the
        /// same one; a new target, or a pause longer than the ramp's grace, starts it again.
        /// </summary>
        private float RampScale(Vehicle shooter, int index, EntityId target)
        {
            var ramp = shooter.Arms[index].Ramp;
            if (ramp == null) return 1f;
            var state = shooter.Weapons[index];
            var now = _world.Time;
            if (state.RampTarget != target || now - state.RampLastAt > ramp.Grace)
            {
                state.RampTarget = target;
                state.RampSince = now;
            }
            state.RampLastAt = now;
            return ramp.At(now - state.RampSince);
        }

        /// <summary>
        /// A loyal wingman's decoy: an anti-air missile fired at a manned aircraft with an escorting wingman of its
        /// side close by turns onto the wingman at the wingman's pull (one roll a missile, and only when a wingman
        /// is there, so battles without one draw the same numbers as before).
        /// </summary>
        private EntityId WingmanPull(Vehicle shooter, WeaponDef weapon, EntityId target, bool targetFlying)
        {
            if (!targetFlying || weapon.Projectile != ProjectileKind.Missile || !weapon.Guided || !_world.TryGetVehicle(target, out var aimed) ||
                !aimed.Def.Manned || _wingmen == 0) return target;
            Vehicle? decoy = null;
            var best = float.MaxValue;
            foreach (var w in _world.VehicleList)
            {
                if (!w.IsAlive || w.Team != aimed.Team || w.Def.Wingman is not { } wing || w.WingLeader != aimed.Id) continue;
                var d2 = Vector2.DistanceSquared(w.Position, aimed.Position);
                if (d2 > wing.Decoy * wing.Decoy || d2 >= best) continue;
                decoy = w;
                best = d2;
            }
            if (decoy == null) return target;
            return _world.Random.NextDouble() < decoy.Def.Wingman!.Pull ? decoy.Id : target;
        }

        /// <summary>Wingmen alive this step (none: the decoy check is skipped).</summary>
        private int _wingmen;

        private void CountWingmen()
        {
            _wingmen = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Def.Wingman != null) _wingmen++;
        }

        /// <summary>
        /// A swarm salvo's next drone: the enemy on the ground within the swarm's reach of the salvo's aim that has
        /// the least coming at it for its health (so the drones spread over the group), the nearest breaking ties.
        /// </summary>
        private Vehicle? SwarmTarget(Vehicle v, WeaponDef weapon, Vector2 around)
        {
            Vehicle? best = null;
            var bestScore = float.MaxValue;
            var reach2 = weapon.SwarmReach * weapon.SwarmReach;
            foreach (var other in _world.VehicleList)
            {
                if (!other.IsAlive || other.Flying || other.Team == v.Team || other.Team < 0 || other.Invulnerable || other.Def.Untargetable ||
                    !other.IsVisibleTo(v.Team)) continue;
                var d2 = Vector2.DistanceSquared(other.Position, around);
                if (d2 > reach2) continue;
                var due = _incoming.TryGetValue(other.Id, out var incoming) ? incoming : 0f;
                var score = due / MathF.Max(1f, other.Hp) + MathF.Sqrt(d2) * 0.01f;
                if (other.Def.Obstacle) score += 10f;
                if (score >= bestScore) continue;
                best = other;
                bestScore = score;
            }
            return best;
        }

        /// <summary>The bunker vehicle on its tracks: its turret stays within its arc of the nose.</summary>
        private static void KeepToArc(Vehicle v)
        {
            if (v.Def.Deploy is not { } dep || v.Deploy == DeployState.Deployed) return;
            var off = SimMath.WrapAngle(v.TurretHeading - v.Heading);
            if (MathF.Abs(off) > dep.Arc) v.TurretHeading = v.Heading + MathF.Sign(off) * dep.Arc;
        }
    }
}
