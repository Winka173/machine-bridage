#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// Prompt 28 D, the unit layer's local logic for squad members (target scoring itself runs every tick in CombatSystem):
    /// the tactic's target groups, armour facing, the role's short move when overwhelmed (never a retreat on health),
    /// scouts at the edge of sight; and G.2, a squad taking a crowded narrow passage in turns.
    /// </summary>
    public sealed partial class SquadLayer
    {
        /// <summary>A member's short move when overwhelmed is made at most this often (seconds).</summary>
        private const double ShortMoveEvery = 8.0;

        private readonly Dictionary<EntityId, double> _shortMoveAt = new();

        private void Units(SimWorld world, TeamIntel intel, Squad s, TacticDef tactic)
        {
            var now = world.Time;
            var overwhelmed = now < s.EmergencyReadyAt && Overwhelmed(intel, s, world.Catalog.Ai);
            Vector2? threat = s.Focus.IsValid && intel.Find(s.Focus) is { InSight: true } f ? f.Position : NearestEnemy(intel, s.Centre);
            foreach (var id in s.MemberList)
            {
                if (!world.TryGetVehicle(id, out var v)) continue;
                v.SquadTargets = tactic.Modules.Targets;
                ExplainTarget(world, s, v, tactic);
                // D.4: a standing vehicle with a thicker front turns it to the threat (the turret aims on its own).
                v.FaceHeading = !v.IsMoving && threat is { } t && Vector2.Distance(t, v.Position) <= s.Reach * 1.5f &&
                                v.ArmourOn(ArmorFace.Front) > v.ArmourOn(ArmorFace.Side)
                    ? SimMath.HeadingOf(t - v.Position)
                    : null;
                var role = world.Catalog.AiData.RoleOf(v.Def.Id);
                if (role == null) continue;
                // Scouts keep to the edge of their sight, not in the fight.
                if (role.Id == "Recon" && threat is { } seen && s.State == SquadState.Combat &&
                    Vector2.Distance(seen, v.Position) < v.Def.VisionRange * 0.75f && !v.IsMoving)
                {
                    var back = world.Map.Clamp(seen + Direction(seen, v.Position) * v.Def.VisionRange * 0.9f, 6f);
                    if (world.Grid.IsWalkable(back)) world.Submit(new Command(CommandType.Move, _commander.Team, new[] { id }, back));
                    continue;
                }
                if (overwhelmed && threat is { } danger) ShortMove(world, intel, v, role.Overwhelmed, danger, now);
            }
        }

        private readonly Dictionary<EntityId, EntityId> _explained = new();

        /// <summary>J.2 for a unit: its state, its target and why that one (recorded when the target changes).</summary>
        private void ExplainTarget(SimWorld world, Squad s, Vehicle v, TacticDef tactic)
        {
            if (_explained.TryGetValue(v.Id, out var last) && last.Value == v.Target.Value) return;
            _explained[v.Id] = v.Target;
            var factors = new List<Factor>();
            var choice = "none";
            if (world.TryGetVehicle(v.Target, out var t))
            {
                choice = t.Def.Id;
                if (t.Id == s.Focus) factors.Add(new Factor("squadFocus", 1f));
                if (TeamIntel.GroupOf(t.Def) is { } g)
                    foreach (var x in tactic.Modules.Targets)
                        if (x == g) factors.Add(new Factor("tacticTarget", 1f));
                if (t.Target == v.Id) factors.Add(new Factor("shootsAtUs", 1f));
                if (t.Hp < t.MaxHp * 0.3f) factors.Add(new Factor("nearlyDead", 1f));
                factors.Add(new Factor("effectiveDamage", 1f));
                if (!t.IsVisibleTo(v.Team)) factors.Add(new Factor("notInSight", -1f));
            }
            var (plus, minus) = Why.Split(factors);
            world.AiLog.Record(new Why
            {
                Layer = AiLayer.Unit, Team = v.Team, Subject = v.Id.Value, Time = world.Time, Choice = choice, Plus = plus, Minus = minus,
                Context = $"squad {s.Id} {s.State}",
            });
        }

        /// <summary>D.3: the role's short move in the fight when overwhelmed: cover, a shift of 15-25 m, out of smoke.</summary>
        private void ShortMove(SimWorld world, TeamIntel intel, Vehicle v, OverwhelmedMove move, Vector2 danger, double now)
        {
            if (move is OverwhelmedMove.Hold or OverwhelmedMove.Rearm or OverwhelmedMove.Scoot) return;
            if (_shortMoveAt.TryGetValue(v.Id, out var at) && now - at < ShortMoveEvery) return;
            var away = Direction(danger, v.Position);
            var side = new Vector2(away.Y, -away.X) * ((v.Id.Value & 1) == 0 ? 1f : -1f);
            Vector2? spot = null;
            switch (move)
            {
                case OverwhelmedMove.Smoke:
                    foreach (var z in world.Strikes.Smoke)
                        if (Vector2.Distance(z.Centre, v.Position) < z.Radius)
                            spot = z.Centre + Direction(z.Centre, v.Position) * (z.Radius + 4f);
                    break;
                case OverwhelmedMove.Cover:
                    // The nearest of a few spots with less anti-tank reach on it.
                    var best = intel.ThreatAt(ThreatKind.AntiTank, v.Position);
                    for (var k = -2; k <= 2; k++)
                    {
                        var p = v.Position + side * (k * 6f) + away * 6f;
                        var d = intel.ThreatAt(ThreatKind.AntiTank, p);
                        if (d < best && world.Grid.IsWalkable(p))
                        {
                            best = d;
                            spot = p;
                        }
                    }
                    break;
                default: // Shift: a new firing spot a few tens of metres across
                    spot = v.Position + side * 20f;
                    break;
            }
            if (spot is not { } to) return;
            to = world.Map.Clamp(to, 4f);
            if (!world.Grid.IsWalkable(to)) return;
            _shortMoveAt[v.Id] = now;
            world.Submit(new Command(CommandType.AttackMove, _commander.Team, new[] { v.Id }, to));
        }

        /// <summary>G.2: a crowded narrow passage (a chokepoint cell) within 12 m of the squad's next 40 m.</summary>
        private static bool Crowded(TeamIntel intel, Vector2 from, Vector2 to)
        {
            if (intel.Chokepoints.Count == 0) return false;
            var dir = Direction(from, to);
            var end = from + dir * MathF.Min(40f, Vector2.Distance(from, to));
            foreach (var c in intel.Chokepoints)
            {
                var p = intel.CellCentre(c);
                var along = Math.Clamp(Vector2.Dot(p - from, dir), 0f, Vector2.Distance(from, end));
                if (Vector2.Distance(from + dir * along, p) < 12f && intel.Density[c] >= 3) return true;
            }
            return false;
        }
    }
}
