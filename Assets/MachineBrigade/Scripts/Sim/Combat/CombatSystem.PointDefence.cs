#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Play-test 5 (DECISIONS 20W): a gun point defence (the C-RAM: <see cref="ApsDef.Burst"/> seconds) takes a round
    /// down with a burst of fire, never one shot. It lays its gun on the incoming round that lands soonest among those
    /// aimed inside its reach that it can take (the same rules as <see cref="DamageSystem"/>'s interception: rockets,
    /// guided rounds, its share of shells), streams at it every step, and once the burst has run the round bursts in
    /// the air where it has got to (an interceptor spent, as before). One round at a time; a round that would land
    /// before a short burst could run is not engaged.
    /// </summary>
    internal sealed partial class CombatSystem
    {
        /// <summary>Seconds before it lands that a round may be engaged, and the shortest burst that takes one down.</summary>
        internal const float EngageWindow = 3f, ShortestBurst = 0.2f;

        /// <summary>Rounds a step in the stream (60 a second, the simulation's cap for a mount).</summary>
        private const int BurstRoundsPerStep = 3;

        private void EngageIncoming(float dt)
        {
            var now = _world.Time;
            foreach (var v in _world.VehicleList)
            {
                var aps = v.Aps;
                if (aps == null || aps.Burst <= 0f) continue;
                var round = v.PdRound;
                if (round != null && (round.TimeLeft <= 0f || !v.IsAlive || v.Stunned || v.ApsOff))
                {
                    round.EngagedBy = EntityId.None;
                    v.PdRound = round = null;
                }
                if (!v.IsAlive || v.Stunned || v.ApsOff || v.Team < 0) continue;
                if (round == null)
                {
                    if (v.ApsCharges <= 0 || (round = RoundToEngage(v, aps)) == null) continue;
                    v.PdRound = round;
                    v.PdSince = now;
                    v.PdBurst = MathF.Max(ShortestBurst, MathF.Min(aps.Burst, round.TimeLeft - dt));
                    round.EngagedBy = v.Id;
                }
                var at = RoundAt(round);
                var weapon = v.Def.Weapon;
                v.TurretHeading = SimMath.RotateTowards(v.TurretHeading, SimMath.HeadingOf(at - v.Position), 720f * dt);
                _world.Emit(SimEvent.PointDefence(v, weapon, at, RoundHeight(round), BurstRoundsPerStep));
                if (now - v.PdSince + 1e-6 < v.PdBurst) continue;
                // The burst has run: the round is down, one interceptor's worth spent (the old one-shot rules).
                v.PdRound = null;
                if (v.ApsCharges <= 0) continue;
                v.ApsCharges--;
                if (aps.Reload > 0f) v.ApsReload = 0f;
                v.ApsLeft = !v.ApsLeft;
                RemoveRound(round);
                _world.Emit(SimEvent.Intercept(v, round.Weapon, at, v.ApsLeft));
            }
        }

        /// <summary>The round landing soonest that this point defence may engage now (none: null).</summary>
        private Projectile? RoundToEngage(Vehicle v, ApsDef aps)
        {
            Projectile? best = null;
            foreach (var p in _projectiles)
            {
                if (p.OwnerTeam == v.Team || p.Tandem || p.TargetFlying || p.EngagedBy.IsValid || p.PdPassed) continue;
                if (p.TimeLeft < ShortestBurst || p.TimeLeft > EngageWindow) continue;
                // Prompt 28 E.4: a tower's mode orders the rounds (key structures, boss missiles); the soonest first otherwise.
                if (best != null && !BetterRound(v, p, best)) continue;
                var mark = _world.TryGetTarget(p.Target, out var target) && target.IsAlive ? target.Position : p.AimPoint;
                if (Vector2.DistanceSquared(v.Position, mark) > aps.Radius * aps.Radius) continue;
                if (!DamageSystem.GunTakes(aps, p.Weapon, out var shell)) continue;
                // Prompt 32 L4, the stacking rule: the round is the nearest free gun's that may take it (ties by id); this one
                // leaves it to that one (overlapping guns add reach and interceptors, never a second chance).
                if (NearerGun(v, p, mark)) continue;
                // Its share of the shells, decided once per shell (the old roll at the moment of impact).
                if (shell && _world.Random.NextDouble() >= aps.Shells)
                {
                    p.PdPassed = true;
                    continue;
                }
                best = p;
            }
            return best;
        }

        /// <summary>Another free gun point defence of the side, nearer the round's mark, that may take it now (ties by id).</summary>
        private bool NearerGun(Vehicle v, Projectile p, Vector2 mark)
        {
            var mine = Vector2.DistanceSquared(v.Position, mark);
            foreach (var o in _world.VehicleList)
            {
                if (o == v || o.Team != v.Team || o.Aps is not { Burst: > 0f } a || !o.IsAlive || o.Stunned || o.ApsOff || o.ApsCharges <= 0 || o.PdRound != null) continue;
                var d = Vector2.DistanceSquared(o.Position, mark);
                if (d > a.Radius * a.Radius || d > mine || (d == mine && o.Id.Value > v.Id.Value)) continue;
                if (DamageSystem.GunTakes(a, p.Weapon, out _)) return true;
            }
            return false;
        }

        /// <summary>Where a round in flight has got to (along the ground from where it was fired to where it lands).</summary>
        private static Vector2 RoundAt(Projectile p)
        {
            var done = p.Flight > 0f ? Math.Clamp(1f - p.TimeLeft / p.Flight, 0f, 1f) : 1f;
            return Vector2.Lerp(p.Origin, p.AimPoint, done);
        }

        /// <summary>The round's height there, as the view draws its path (a lobbed round's arc, a direct one's low line).</summary>
        private static float RoundHeight(Projectile p)
        {
            var done = p.Flight > 0f ? Math.Clamp(1f - p.TimeLeft / p.Flight, 0f, 1f) : 1f;
            // Play-test 13 (lane C): the weapon's flight profile sets the arc (ballistic, lofted, direct).
            var share = p.Weapon.ArcShare;
            return 1.5f + Vector2.Distance(p.Origin, p.AimPoint) * share * 4f * done * (1f - done);
        }

        /// <summary>Takes a round out of the air before it lands (its expected damage off its target's books).</summary>
        private void RemoveRound(Projectile p)
        {
            var i = _projectiles.IndexOf(p);
            if (i < 0) return;
            _projectiles[i] = _projectiles[_projectiles.Count - 1];
            _projectiles.RemoveAt(_projectiles.Count - 1);
            p.TimeLeft = 0f;
            if (p.Incoming > 0f && _incoming.TryGetValue(p.Target, out var due))
            {
                if (due - p.Incoming > 0.01f) _incoming[p.Target] = due - p.Incoming;
                else _incoming.Remove(p.Target);
            }
        }
    }
}
