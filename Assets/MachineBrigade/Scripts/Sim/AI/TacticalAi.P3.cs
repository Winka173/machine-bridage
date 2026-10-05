#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER P3 spec 140, repair reservation: an engineer goes to the damaged friend near the front with the largest
    /// repair need not yet reserved by another engineer (RepairNeed - RepairReserved), and reserves its own repair for a
    /// window; with no deficit left it follows the army as before. Never 4-5 engineers on one tank.
    /// </summary>
    public sealed partial class TacticalAi
    {
        private Vector2? RepairTargetP3(SimWorld world, Vehicle engineer, Vector2 front)
        {
            if (!Tun.Coordination.Enabled || world.CoordinationIfAny?.Peek(_team) is not { } tc || engineer.Def.RepairAura is not { } aura) return null;
            var now = world.Time;
            Vehicle? best = null;
            var bestDeficit = 0f;
            var bestD = float.MaxValue;
            var covered = false;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != _team || v.Flying || v.Def.Static || v == engineer || v.Hp >= v.MaxHp * 0.8f) continue;
                var d = Vector2.Distance(v.Position, front);
                if (d > 60f) continue;
                var need = v.MaxHp - v.Hp;
                var reserved = tc.Board.RepairReserved(v.Id, engineer.Id, now);
                if (!PlannedActionBoard.RepairDeficit(need, reserved))
                {
                    covered = true;
                    continue;
                }
                var deficit = need - reserved;
                if (deficit > bestDeficit + 1e-3f || (MathF.Abs(deficit - bestDeficit) <= 1e-3f && d < bestD))
                {
                    best = v;
                    bestDeficit = deficit;
                    bestD = d;
                }
            }
            if (covered) tc.Metrics.DuplicateRepairPrevented++;
            if (best == null)
            {
                tc.Board.ReleaseRepair(engineer.Id);
                return null;
            }
            var amount = best.MaxHp * aura.Rate * Tun.Board.RepairWindowS;
            var had = tc.Board.RepairReserved(best.Id, default, now) > tc.Board.RepairReserved(best.Id, engineer.Id, now);
            tc.Board.ReserveRepair(best.Id, engineer.Id, amount, now + Tun.Board.RepairWindowS);
            if (!had) P3Reasons.Unit(world, engineer, DecisionKind.Plan, P3Reasons.RepairReserved, $"#{best.Id.Value} need {bestDeficit:0}");
            var away = best.Position - engineer.Position;
            var stand = away.LengthSquared() > 0.01f ? best.Position - Vector2.Normalize(away) * MathF.Max(2f, aura.Radius * 0.5f) : best.Position;
            return world.Grid.IsWalkable(stand) ? stand : best.Position;
        }
    }
}
