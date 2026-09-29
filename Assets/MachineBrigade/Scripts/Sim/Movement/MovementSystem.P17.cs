#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>
    /// Prompt 17 C: the loyal wingman's flying (on its leader's wing, or on patrol over the front), the stealth
    /// fighter's hunt for air defences, and the bunker vehicle standing still while it digs in or packs up.
    /// </summary>
    internal sealed partial class MovementSystem
    {
        /// <summary>Where a wingman flies off its leader, in the leader's frame: this far out to the side and this far back.</summary>
        private const float WingSide = 9f, WingBack = 7f;

        /// <summary>A leader slower than this share of the wingman's speed (a helicopter, a hovering jet) is circled instead.</summary>
        private const float CircleSlowerThan = 0.4f;

        /// <summary>The share of its speed a wingman circles a slow leader at.</summary>
        private const float SlowCircle = 0.45f;

        /// <summary>Seconds between a wingman's looks for its leader.</summary>
        private const double WingCheck = 1.0;

        /// <summary>
        /// The bunker vehicle digging in, dug in or packing up: it stays where it is (its route, if any, waits for it
        /// to pack up), and is not taken for stuck meanwhile. True: skip its driving this step.
        /// </summary>
        private static bool DeployHeld(Vehicle v)
        {
            if (!v.DeployHolds) return false;
            v.Speed = 0f;
            v.StuckTimer = 0f;
            return true;
        }

        /// <summary>
        /// A wingman with no target of its own: on its leader's wing (matching its speed, circling a slow one), or,
        /// with no manned aircraft of its side within reach, on patrol over the front. False when the player is
        /// flying it by hand or it has an attack run to fly.
        /// </summary>
        private bool FlyWing(Vehicle v, float dt)
        {
            var wing = v.Def.Wingman!;
            var now = _world.Time;
            if (v.UnderPlayerControl(now) || v.Order.Kind is OrderKind.Attack or OrderKind.Move or OrderKind.Retreat) return false;
            if (now >= v.WingCheckAt)
            {
                v.WingCheckAt = now + WingCheck;
                v.WingLeader = ChooseLeader(v, wing);
                if (!v.WingLeader.IsValid) v.GuardPoint = FrontPoint(v.Team);
            }
            if (!_world.TryGetVehicle(v.WingLeader, out var leader) || !leader.IsAlive)
            {
                v.WingLeader = EntityId.None;
                return false;
            }
            // Its own fights stay near the leader.
            if (_world.TryGetVehicle(v.Engaged, out var engaged) && Vector2.Distance(engaged.Position, leader.Position) > wing.Decoy * 2f) v.Engaged = EntityId.None;
            var def = v.Def;
            var forward = SimMath.Forward(leader.Heading);
            var right = new Vector2(forward.Y, -forward.X);
            // Wingmen on one leader take turns sides.
            var side = (v.Id.Value & 1) == 0 ? 1f : -1f;
            var slot = leader.Position + right * (WingSide * side) - forward * WingBack;
            var gap = Vector2.Distance(v.Position, slot);
            Vector2 goal;
            var want = def.Speed;
            if (leader.Speed < def.Speed * CircleSlowerThan)
            {
                // A tight circle at its slowest round a hovering or slow leader.
                want = def.Speed * SlowCircle;
                goal = OrbitAround(v, leader.Position, MathF.Max(12f, want / def.TurnRate * 1.3f));
            }
            else
            {
                // Far off: straight for the slot; close: along the leader's line, easing into the slot.
                goal = gap > 14f ? slot : slot + forward * 20f + (slot - v.Position) * 0.5f;
                want = leader.Speed + (gap - 2f) * 0.8f;
            }
            var top = def.Speed * v.SpeedFactor;
            var speed = Math.Clamp(want, def.Speed * 0.35f, top);
            v.Heading = SimMath.RotateTowards(v.Heading, SimMath.HeadingOf(goal - v.Position), def.TurnRate * v.TurnFactor * dt);
            v.Speed = SimMath.MoveTowards(v.Speed, speed, def.Speed * 0.8f * dt);
            v.Position = _world.ClampToMap(v.Position + SimMath.Forward(v.Heading) * v.Speed * dt);
            v.InAttackHold = false;
            v.Orbiting = false;
            return true;
        }

        /// <summary>
        /// The manned aircraft of its side it escorts: the nearest within its follow reach (the one it has now while
        /// it is still within a fifth more), a leader with other wingmen counting 40 m further off per wingman.
        /// </summary>
        private EntityId ChooseLeader(Vehicle v, WingmanDef wing)
        {
            if (_world.TryGetVehicle(v.WingLeader, out var current) && current.IsAlive && current.Def.Manned &&
                Vector2.Distance(current.Position, v.Position) <= wing.Follow * 1.2f) return current.Id;
            Vehicle? best = null;
            var bestScore = float.MaxValue;
            foreach (var other in _world.VehicleList)
            {
                if (!other.IsAlive || other.Team != v.Team || !other.Def.Manned || other.Scripted) continue;
                var d = Vector2.Distance(other.Position, v.Position);
                if (d > wing.Follow) continue;
                var escorts = 0;
                foreach (var w in _world.VehicleList)
                    if (w != v && w.IsAlive && w.WingLeader == other.Id) escorts++;
                var score = d + 40f * escorts;
                if (score >= bestScore) continue;
                best = other;
                bestScore = score;
            }
            return best?.Id ?? EntityId.None;
        }

        /// <summary>
        /// The front for a side's patrol: halfway from the middle of its ground army to the nearest enemy on the
        /// ground it sees there (30 m on towards the enemy's camp with none seen); its camp with no army out.
        /// </summary>
        internal Vector2 FrontPoint(int team)
        {
            var sum = Vector2.Zero;
            var n = 0;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team != team || v.Flying || v.Def.Static || v.Scripted) continue;
                sum += v.Position;
                n++;
            }
            _world.TryGetRally(team, out var home);
            if (n == 0) return home;
            var middle = sum / n;
            Vehicle? nearest = null;
            var best = float.MaxValue;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == team || e.Team < 0 || e.Flying || !e.IsVisibleTo(team)) continue;
                var d2 = Vector2.DistanceSquared(e.Position, middle);
                if (d2 >= best) continue;
                nearest = e;
                best = d2;
            }
            if (nearest != null) return _world.ClampToMap((middle + nearest.Position) * 0.5f);
            foreach (var start in _world.Map.Teams)
            {
                if (start.Team == team) continue;
                var toward = start.Rally - middle;
                if (toward.LengthSquared() > 1f) return _world.ClampToMap(middle + Vector2.Normalize(toward) * 30f);
            }
            return middle;
        }

        /// <summary>
        /// The stealth fighter with no aircraft to fight and bombs left: the nearest air defence its side sees
        /// (a ground unit or tower with an anti-aircraft weapon) within half again its sight.
        /// </summary>
        private Vehicle? SeadTarget(Vehicle v)
        {
            if (!v.Def.Sead || v.Supply != SupplyState.Fighting) return null;
            var bombs = false;
            for (var i = 0; i < v.Def.Mounts.Count; i++)
                if (v.Arms[i].Projectile == ProjectileKind.Bomb && v.Weapons[i].Ammo != 0) bombs = true;
            if (!bombs) return null;
            Vehicle? best = null;
            var bestDistance = v.Def.VisionRange * 1.5f;
            foreach (var other in _world.VehicleList)
            {
                if (!other.IsAlive || other.Team == v.Team || other.Team < 0 || other.Flying || other.Invulnerable || !other.IsVisibleTo(v.Team) ||
                    !Combat.CombatSystem.IsAirDefence(other.Def)) continue;
                var d = Vector2.Distance(other.Position, v.Position);
                if (d >= bestDistance) continue;
                best = other;
                bestDistance = d;
            }
            return best;
        }
    }
}
