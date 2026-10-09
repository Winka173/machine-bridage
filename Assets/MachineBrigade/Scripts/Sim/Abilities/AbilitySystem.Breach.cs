#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Abilities
{
    /// <summary>
    /// Prompt 8 A: the armoured bulldozer ploughs dragon's teeth flat as it drives into them, and the
    /// SP howitzer shoots and scoots (after a few rounds from one spot it drives 15 to 20 m to a new
    /// one still in reach of its target, so the counter-battery fire its shots drew lands on nothing).
    /// </summary>
    internal sealed partial class AbilitySystem
    {
        /// <summary>A breacher's blade flattens an enemy obstacle it touches (dragon's teeth, hedgehogs, wire).</summary>
        private void Plough(Vehicle v)
        {
            if (v.Stunned || v.Flying) return;
            foreach (var o in _world.VehicleList)
            {
                if (!o.IsAlive || !o.Def.Obstacle || o.Def.Wall || o.Team == v.Team || o.Team < 0) continue;
                var reach = v.Def.HullBound + o.Def.HullBound + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.PloughHullBoundAdd;
                if (Vector2.DistanceSquared(o.Position, v.Position) > reach * reach) continue;
                _world.Damage.Apply(o, o.Hp + o.MaxHp, v.Weapon.DamageType, new HitInfo(v, v.Team, v.Weapon, v.Position, HitKind.Direct, false));
                _world.Emit(SimEvent.Proc(v, "plough"));
            }
        }

        /// <summary>
        /// Shoot-and-scoot: once its shots from this spot are fired and the gun is reloading, it drives
        /// to a new spot 15 to 20 m off, still in reach of its target, and takes its order up again there.
        /// Not while the player has it on a move of their own.
        /// </summary>
        private void Scoot(Vehicle v, double now)
        {
            var scoot = v.Def.Scoot!;
            if (v.ScootShots < scoot.Shots || v.Relocating || v.IsMoving || v.Stunned || v.HasPath || v.PathQueued) return;
            if (v.Order.Kind is OrderKind.Move or OrderKind.Retreat) return;
            // Just fired: the reload is under way (it moves in the time it would be waiting anyway).
            if (v.Weapons[0].Cooldown < 1f && v.Weapons[0].Ammo != 0) return;
            Vector2? target = null;
            if (_world.TryGetTarget(v.Order.Kind == OrderKind.Attack ? v.Order.Target : v.Target, out var aimed) && aimed.IsAlive) target = aimed.Position;
            var weapon = v.Weapon;
            var rng = _world.Random;
            var distance = scoot.Min + (float)rng.NextDouble() * MathF.Max(0f, scoot.Max - scoot.Min);
            // Across the line of fire first (either way, drawn), then angled back, then straight back.
            var bearing = target is { } t && Vector2.DistanceSquared(t, v.Position) > 1f ? SimMath.HeadingOf(v.Position - t) : v.Heading + MathF.PI;
            var first = rng.NextDouble() < global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.ScootNextDoubleMax ? 1f : -1f;
            float[] turns = { 1.57f * first, -1.57f * first, 2.2f * first, -2.2f * first, 0f };
            foreach (var turn in turns)
            {
                // Relative to the direction from the target to the gun: 0 is straight back.
                var spot = _world.ClampToMap(v.Position + SimMath.Forward(bearing + (turn == 0f ? 0f : MathF.PI - turn)) * distance);
                if (!_world.Map.Contains(spot) || !_world.Grid.IsWalkable(spot) || _world.Lanes.NoParkAt(spot)) continue;
                if (target is { } aim)
                {
                    var reach = Vector2.Distance(spot, aim);
                    if (reach > weapon.Range - global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.ScootRangeSub || reach < weapon.MinRange + global::MachineBrigade.Sim.Content.SimTunables.Vehicles.AbilitySystem.ScootMinRangeAdd) continue;
                }
                if (!_world.PathTo(v, spot)) continue;
                v.Relocating = true;
                v.ScootShots = 0;
                _world.Emit(SimEvent.Proc(v, "scoot"));
                return;
            }
            // Nowhere to go: it fires on from here and tries again after its next rounds.
            v.ScootShots = 0;
        }
    }
}
