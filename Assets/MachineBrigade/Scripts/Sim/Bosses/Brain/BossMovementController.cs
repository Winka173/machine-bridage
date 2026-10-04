#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Bosses.BossBrain;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// AI MASTER P0-C (spec 48 "BossMovementController", 50, 63-64, 33, Part U): the hull's arbiter for every moving boss.
    /// <list type="bullet">
    /// <item>Hull and turrets apart (spec 50): the hull follows the route / mission (MovementSystem's path, the naval
    /// controller at sea); the turrets track targets (CombatSystem). The hull turns for a target only when a hull-dependent
    /// weapon asks (<see cref="GrantAlignment"/>: a hull-fixed main weapon on a rotor craft or a ground boss; a ground boss's
    /// front to the heaviest fire, prompt 28 F.4) and the mission does not own the hull, never for an airship (lane H's
    /// warships hold their heading) and never flipping more than 120 degrees within 3 s.</item>
    /// <item>Anchor before target (spec 49): a boss leaves its way for a target only when the target is in reach already, a
    /// structure, or within the chase leash of its way (<see cref="MayChase"/>).</item>
    /// <item>Reverse (spec 52, 63): never at sea or in the air; a tracked / wheeled boss is designed to back up (unjamming,
    /// a doorway), at most once in 8 s, never continuously (<see cref="MayReverse"/>). Trains: the rail system.</item>
    /// <item>Flying laws (spec 64): rotor / hover (turn on the spot for a hull-fixed weapon, no 180-degree flip-flops),
    /// fixed wing (MovementSystem.DriveAeroplane's runs and orbits: no hover turns at all), airship (holds its heading to fire,
    /// turns only on its route).</item>
    /// <item>Corridor (spec 33, 63 "mobile fortress reserves a traffic corridor"): a ground boss under way reserves the stretch
    /// ahead of it, half its width + 2.5 m either side, 25-35 m long; its friends standing in it are asked to make way
    /// (MovementSystem.ClearBossCorridors). The list is <see cref="BossBrains.Corridors"/>, the API for the traffic lane.</item>
    /// </list>
    /// </summary>
    public static class BossMovementController
    {
        /// <summary>Spec 64: the steering law of a boss's body.</summary>
        public static BossCraft CraftOf(VehicleDef def)
        {
            var move = def.Frame?.Move;
            if (def.Naval != null || move is BossMove.Ship or BossMove.Submarine) return BossCraft.Naval;
            if (move == BossMove.Rail) return BossCraft.Rail;
            if (def.FixedWing) return BossCraft.FixedWing;
            if (def.Flying) return def.HoldsToFire || def.TurnRate <= SimMath.DegToRad(12f) ? BossCraft.Airship : BossCraft.Rotor;
            return BossCraft.Ground;
        }

        /// <summary>
        /// Part U: a hull-dependent weapon (or the armour's facing) asks for the hull on <paramref name="heading"/>; true when the
        /// arbiter grants it (no brain: always).
        /// </summary>
        internal static bool GrantAlignment(SimWorld world, Vehicle v, float heading, HullReason reason)
        {
            if (v.Brain is not { } b) return true;
            var now = world.Time;
            if (b.MissionLocked || b.Craft is BossCraft.Airship or BossCraft.Naval or BossCraft.Rail or BossCraft.FixedWing)
            {
                b.AlignRefused++;
                return false;
            }
            if (reason == HullReason.WeaponAlignment && now - b.AlignGrantedAt < Tun.AlignFlipSeconds &&
                MathF.Abs(SimMath.WrapAngle(heading - b.AlignGranted)) > SimMath.DegToRad(120f))
            {
                b.AlignRefused++;
                return false;
            }
            b.AlignGranted = heading;
            b.AlignGrantedAt = now;
            b.HullReason = reason;
            b.DesiredHullHeading = heading;
            return true;
        }

        /// <summary>
        /// Spec 49: whether a boss may leave its way to close on <paramref name="target"/>: the target is in its reach already
        /// (it stops to fight where it is), a structure (an objective), or within the chase leash of its way; never while the
        /// mission owns the hull. An aeroplane flies its attack runs (its law). No brain: always.
        /// </summary>
        internal static bool MayChase(SimWorld world, Vehicle v, IDamageable target)
        {
            if (v.Brain is not { } b) return true;
            if (b.Craft == BossCraft.FixedWing) return true;
            if (b.MissionLocked)
            {
                b.ChasesRefused++;
                return false;
            }
            var distance = Vector2.Distance(v.Position, target.Position) - target.Radius;
            var reach = 0f;
            for (var i = 0; i < v.Arms.Length; i++)
                if (v.MountWorks(i) && v.Arms[i].Damage > 0f) reach = MathF.Max(reach, v.Arms[i].Range * (v.Deploy == DeployState.Deployed ? v.RangeFactor : 1f));
            if (distance <= reach) return true;
            if (target is Vehicle structure && structure.Def.Static) return true;
            var way = v.Order.Kind is OrderKind.Move or OrderKind.AttackMove ? v.Order.Point : b.Anchor;
            if (BrainMath.DistanceToSegment(target.Position, v.Position, way) <= Tun.ChaseLeash) return true;
            b.ChasesRefused++;
            return false;
        }

        /// <summary>
        /// Spec 52, 63: whether a boss may back up now: never a ship, an aircraft or a train; a tracked or wheeled boss at most
        /// once in <see cref="Tun.GroundReverseCooldown"/> s. Counted on the brain. No brain: always.
        /// </summary>
        internal static bool MayReverse(SimWorld world, Vehicle v)
        {
            if (v.Brain is not { } b) return true;
            var now = world.Time;
            if (b.Craft != BossCraft.Ground || now - b.LastReverseAt < Tun.GroundReverseCooldown)
            {
                b.ReversesRefused++;
                if (b.Craft == BossCraft.Naval) world.Bosses.Brains.NavalReverseRefused++;
                return false;
            }
            b.LastReverseAt = now;
            b.Reverses++;
            return true;
        }

        /// <summary>Spec 33: the corridor of a ground boss under way (none standing, at sea, in the air, on rails).</summary>
        internal static void UpdateCorridor(Vehicle v, BossBrain b)
        {
            b.HasCorridor = false;
            if (b.Craft != BossCraft.Ground || v.Flying || v.Burrow != Vehicle.BurrowState.Surface || !v.HasPath) return;
            var dir = SimMath.Forward(v.Heading);
            var to = v.Path[v.PathIndex] - v.Position;
            if (to.LengthSquared() > 1f) dir = Vector2.Normalize(to);
            var reach = Math.Clamp(Tun.CorridorClearMin + 2f * v.Def.Speed, Tun.CorridorClearMin, MathF.Max(Tun.CorridorClearMin, Tun.CorridorClearMax));
            b.Corridor = new BossCorridor(v.Id, v.Team, v.Position, v.Position + dir * (v.Def.HullHalf + reach), v.Def.Width * 0.5f + Tun.CorridorMargin);
            b.HasCorridor = true;
        }
    }
}
