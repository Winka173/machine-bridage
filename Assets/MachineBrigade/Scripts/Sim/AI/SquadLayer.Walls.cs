#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// Prompt 32 L3 (DECISIONS "Prompt 32 L3 / L7 / L9"): the way into a walled base, by the squad scoring of prompt 28 (no
    /// behaviour tree of its own). A squad attacking a goal behind an enemy wall line it stands outside compares, in metres
    /// of driving, the open ways (the gate and any rubble) with breaking each standing segment:
    /// <c>cost = routeCost x route + threatCost x threat + breachTimeCost x breach</c> (the weights from the mode's
    /// aiModeProfile "wallRoute"): route the straight way through the opening or the segment to the goal; threat the
    /// anti-tank and artillery reach along it over the squad's strength, 40 m per unit; breach the seconds the squad's guns
    /// take to bring the segment down (its health over their damage a second against it, the wall breakers' x1.5 counted, so
    /// a squad with wall breakers breaks walls sooner) times its speed. A breach is picked only when it costs a fifth less
    /// than the best open way (so a squad does not flip between the two); the squad then attacks that segment and goes on
    /// once it is rubble. Looked at with the squad's own interval; the choice is kept per squad (squad id order).
    /// </summary>
    public sealed partial class SquadLayer
    {
        /// <summary>Metres a unit of route threat (over the squad's strength) counts.</summary>
        internal static float ThreatMetres => global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.ThreatMetres;

        /// <summary>A breach must cost this share less than the best open way.</summary>
        internal static float BreachMargin => global::MachineBrigade.Sim.Content.SimTunables.Ai.SquadLayer.BreachMargin;

        /// <summary>The segment a squad has chosen to break (squad id -> entity).</summary>
        private readonly Dictionary<int, EntityId> _breach = new();

        /// <summary>The chosen segment of a squad (tests, the decision log); None: the gate.</summary>
        public EntityId BreachOf(Squad s) => _breach.TryGetValue(s.Id, out var id) ? id : EntityId.None;

        /// <summary>
        /// The enemy wall segment the squad should break on its way to <paramref name="target"/> (null: the gate or an open
        /// way, or no wall in the way). The line it has to cross first is the outermost one it stands outside and the goal
        /// lies inside.
        /// </summary>
        internal WallSegment? BreachChoice(SimWorld world, TeamIntel intel, Squad s, Vector2 target)
        {
            if (!world.HasWalls || s.MemberList.Count == 0) return null;
            WallLine? line = null;
            foreach (var l in world.Walls.Lines)
            {
                if (l.Team == _commander.Team || l.Team < 0 || l.Standing == 0) continue;
                if (!l.Inside(target) || l.Inside(s.Centre)) continue;
                if (line == null || l.Def.Radius > line.Def.Radius) line = l;
            }
            if (line == null) return null;
            var profile = world.AiProfile;
            var strength = MathF.Max(1f, s.Strength);
            var speed = SquadSpeed(world, s);
            float Way(Vector2 through) =>
                profile.WallRouteCost * (Vector2.Distance(s.Centre, through) + Vector2.Distance(through, target)) +
                profile.WallThreatCost * (MathF.Max(RouteThreat(intel, s.Centre, through), RouteThreat(intel, through, target)) / strength * ThreatMetres);
            var open = Way(line.Def.Gate);
            foreach (var seg in line.Segments)
                if (seg.Rubble) open = MathF.Min(open, Way(seg.Center));
            WallSegment? best = null;
            var bestCost = float.MaxValue;
            foreach (var seg in line.Segments)
            {
                if (seg.Rubble || !world.TryGetVehicle(seg.Entity, out var wall) || !wall.IsAlive) continue;
                var dps = SquadDps(world, s, wall);
                if (dps <= 0f) continue;
                var cost = Way(seg.Center) + profile.WallBreachCost * (wall.Hp / dps) * speed;
                if (cost < bestCost)
                {
                    bestCost = cost;
                    best = seg;
                }
            }
            return best != null && bestCost < open * BreachMargin ? best : null;
        }

        /// <summary>The squad's slowest member's speed (m/s): the time spent breaking counts as that much driving.</summary>
        private static float SquadSpeed(SimWorld world, Squad s)
        {
            var slowest = float.MaxValue;
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v) && v.IsAlive && !v.Flying) slowest = MathF.Min(slowest, v.Def.Speed);
            return slowest == float.MaxValue ? 5f : MathF.Max(1f, slowest);
        }

        /// <summary>The squad's ground members' damage a second against a wall segment (the damage table, armour, their bonuses).</summary>
        private static float SquadDps(SimWorld world, Squad s, Vehicle wall)
        {
            var total = 0f;
            foreach (var id in s.MemberList)
            {
                if (!world.TryGetVehicle(id, out var v) || !v.IsAlive || v.Flying) continue;
                var weapon = v.Weapon;
                if (!weapon.CanTarget(false)) continue;
                var effect = world.Damage.Estimate(weapon, v, wall);
                if (effect <= 0f) continue;
                total += weapon.SustainedDps * effect * DamageSystem.BonusFor(weapon, v, wall, world.Time);
            }
            return total;
        }

        /// <summary>
        /// Prompt 32 L3: an attacking squad's way into a walled base: the segment to break (its members ordered onto it, once),
        /// or false to drive on to the goal (through the gate).
        /// </summary>
        private bool Breach(SimWorld world, TeamIntel intel, Squad s, Vector2 target)
        {
            var seg = BreachChoice(world, intel, s, target);
            if (seg == null)
            {
                _breach.Remove(s.Id);
                return false;
            }
            var changed = !_breach.TryGetValue(s.Id, out var was) || was != seg.Entity;
            _breach[s.Id] = seg.Entity;
            if (changed) world.AiLog.Add(new DecisionEntry(world.Time, _commander.Team, AiLayer.Squad, s.Id, DecisionKind.Action, $"breach wall {seg.Site}"));
            var ids = new List<EntityId>();
            foreach (var id in s.MemberList)
                if (world.TryGetVehicle(id, out var v) && v.IsAlive && !v.Flying && (changed || v.Order.Kind != OrderKind.Attack || v.Order.Target != seg.Entity))
                    ids.Add(id);
            if (ids.Count > 0) world.Submit(new Command(CommandType.Attack, _commander.Team, ids.ToArray(), seg.Center, seg.Entity));
            s.Goal = seg.Center;
            s.IssuedGoal = seg.Center;
            s.IssuedAction = s.Action;
            return true;
        }
    }
}
