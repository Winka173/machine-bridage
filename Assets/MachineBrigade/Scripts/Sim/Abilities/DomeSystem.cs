#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Abilities
{
    /// <summary>
    /// Prompt 17 C: shield domes (the shield carrier's 12 m, the shield generator's 25 m; <see cref="DomeDef"/>).
    /// A dome takes every hit but energy on a ground unit or tower of its side inside it until its hit points are
    /// spent, and is back at full its recharge time after the last hit it took. Domes never add up: a unit under
    /// two is covered by the one with the most left, and what a breaking dome cannot take goes through to the unit
    /// (not to the next dome). A shot from a ground vehicle inside the dome passes (it is a bubble); aircraft and
    /// mines are never inside. Deterministic: no random draws.
    /// </summary>
    internal sealed class DomeSystem
    {
        private readonly SimWorld _world;

        /// <summary>Emitters whose dome is up this step.</summary>
        private readonly List<Vehicle> _up = new();

        /// <summary>Tower-shield emitters alive this step, and the towers carrying one of their shields (DECISIONS 19T).</summary>
        private readonly List<Vehicle> _wardens = new();
        private readonly List<Vehicle> _warded = new();

        public DomeSystem(SimWorld world) => _world = world;

        /// <summary>A dome's full hit points on this emitter (its rank and boosts, as its own health).</summary>
        internal static float Full(Vehicle v) => v.Def.Dome is { } d ? d.Hp * (v.MaxHp / MathF.Max(1f, v.Def.MaxHp)) : 0f;

        public void Step()
        {
            var now = _world.Time;
            _up.Clear();
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Def.Dome is not { } dome) continue;
                if (!v.DomeInit)
                {
                    v.DomeInit = true;
                    v.DomeHp = Full(v);
                }
                var full = Full(v);
                if (v.DomeHp < full && now - v.DomeHitAt >= dome.Recharge)
                {
                    var was = v.DomeHp;
                    v.DomeHp = full;
                    if (was <= 0f) _world.Emit(SimEvent.DomeSwitched(v, true));
                }
                if (v.DomeUp) _up.Add(v);
            }
            StepWards(now);
        }

        /// <summary>
        /// Tower shields: every tower of an emitter's side within its reach carries a shield of its own (the nearest
        /// emitter's), full again its recharge time after its last hit; a tower out of every reach loses it.
        /// </summary>
        private void StepWards(double now)
        {
            _wardens.Clear();
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && !v.Stunned && v.Def.Wards != null) _wardens.Add(v);
            if (_wardens.Count == 0 && _warded.Count == 0) return;
            _warded.Clear();
            foreach (var t in _world.VehicleList)
            {
                if (!t.IsAlive || !t.Def.Static || t.Def.Fort == null || t.Def.Wards != null)
                {
                    if (t.WardFrom.IsValid) Drop(t);
                    continue;
                }
                Vehicle? from = null;
                var best = float.MaxValue;
                foreach (var e in _wardens)
                {
                    if (e.Team != t.Team) continue;
                    var d2 = Vector2.DistanceSquared(e.Position, t.Position);
                    var r = e.Def.Wards!.Radius;
                    if (d2 > r * r || d2 >= best) continue;
                    from = e;
                    best = d2;
                }
                if (from == null)
                {
                    if (t.WardFrom.IsValid) Drop(t);
                    continue;
                }
                var ward = from.Def.Wards!;
                var full = ward.Hp * (from.MaxHp / MathF.Max(1f, from.Def.MaxHp));
                if (t.WardFrom != from.Id)
                {
                    t.WardFrom = from.Id;
                    t.WardHp = full;
                }
                else if (t.WardHp < full && now - t.WardHitAt >= ward.Recharge) t.WardHp = full;
                t.WardFull = full;
                _warded.Add(t);
            }
        }

        private static void Drop(Vehicle t)
        {
            t.WardFrom = default;
            t.WardHp = 0f;
            t.WardFull = 0f;
        }

        /// <summary>Any dome up this step (a quick way out for the damage path).</summary>
        public bool Any => _up.Count > 0;

        /// <summary>The dome covering <paramref name="victim"/> against a hit (the one with the most left), or null.</summary>
        internal Vehicle? Covering(Vehicle victim, Vehicle? attacker)
        {
            if (_up.Count == 0 || victim.Flying) return null;
            Vehicle? best = null;
            foreach (var e in _up)
            {
                if (e.Team != victim.Team || !e.DomeUp) continue;
                var r = e.Def.Dome!.Radius;
                if (Vector2.DistanceSquared(e.Position, victim.Position) > r * r) continue;
                // Fired from inside the bubble: nothing to stop it.
                if (attacker != null && !attacker.Flying && Vector2.DistanceSquared(e.Position, attacker.Position) <= r * r) continue;
                if (best == null || e.DomeHp > best.DomeHp || (e.DomeHp == best.DomeHp && e.Id.Value < best.Id.Value)) best = e;
            }
            return best;
        }

        /// <summary>What is left of a hit on <paramref name="victim"/> after the dome over it (if any) has taken its share.</summary>
        internal float Absorb(Vehicle victim, float damage, DamageType type, in HitInfo hit)
        {
            if ((_up.Count == 0 && _warded.Count == 0) || !(damage > 0f) || type == DamageType.Energy || hit.Kind is HitKind.Burn or HitKind.Redirect or HitKind.Mine) return damage;
            var dome = _up.Count > 0 ? Covering(victim, hit.Attacker) : null;
            // A tower shield only where no dome covers the tower: the two never add up. It stops the rounds aimed at the
            // tower (direct hits and piercing rounds), not the blasts of shells, rockets and bombs round it.
            if (dome == null) return hit.Kind is HitKind.Direct or HitKind.Pierce ? AbsorbWard(victim, damage) : damage;
            var taken = MathF.Min(damage, dome.DomeHp);
            dome.DomeHp -= taken;
            dome.DomeHitAt = _world.Time;
            _world.Emit(SimEvent.DomeStruck(dome, victim.Position, taken));
            if (dome.DomeHp <= 0.01f)
            {
                dome.DomeHp = 0f;
                _world.Emit(SimEvent.DomeSwitched(dome, false));
            }
            return damage - taken;
        }

        /// <summary>A tower's own shield takes what it can of a hit (its generator's), and waits out its recharge again.</summary>
        private float AbsorbWard(Vehicle victim, float damage)
        {
            if (!(victim.WardHp > 0f) || !victim.WardFrom.IsValid) return damage;
            var taken = MathF.Min(damage, victim.WardHp);
            victim.WardHp -= taken;
            victim.WardHitAt = _world.Time;
            if (victim.WardHp <= 0.01f) victim.WardHp = 0f;
            return damage - taken;
        }

        /// <summary>
        /// Targeting: a unit a dome covers is a poor target for a weapon the dome stops (x0.3), and the emitter
        /// of a dome that is up is the one to go for (x2.5), whatever the weapon (prompt 17 C.7: "the generator
        /// first, or energy").
        /// </summary>
        internal float TargetWorth(Vehicle shooter, Vehicle target, WeaponDef weapon)
        {
            if (_up.Count == 0) return 1f;
            if (target.DomeUp) return 2.5f;
            if (weapon.DamageType == DamageType.Energy) return 1f;
            return Covering(target, shooter) != null ? 0.3f : 1f;
        }
    }
}
