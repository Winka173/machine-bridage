#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    internal sealed partial class CombatSystem
    {
        /// <summary>
        /// Prompt 28: the AI layers' weights on the existing target score (which already weighs effective damage by damage
        /// type, penetration and facing, D.2 / C.7): the squad's focus (C.6) by the tactic's focus weight, the tactic's
        /// target groups (H.1), and, for direct fire, a friend standing in the line of fire (G.4: another target if one
        /// is as good).
        /// </summary>
        private float P28Worth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            var worth = 1f;
            if (v.SquadFocus.IsValid && v.SquadFocus.Value == other.Id.Value) worth *= 1f + 0.6f * Math.Clamp(v.SquadFocusWeight, 0f, 2f);
            if (v.SquadTargets is { Count: > 0 } targets && TeamIntel.GroupOf(other.Def) is { } group)
                foreach (var t in targets)
                    if (t == group)
                    {
                        worth *= 1.8f;
                        break;
                    }
            if (!v.Flying && weapon.MinRange <= 0f && weapon.Projectile != ProjectileKind.Bomb && FriendInLine(v, other)) worth *= 0.6f;
            worth *= TowerWorth(v, other, weapon) * BossWorth(v, other, weapon);
            return worth;
        }

        /// <summary>G.4: a friendly ground hull within 2 m of the straight line to the target (direct fire only).</summary>
        private bool FriendInLine(Vehicle v, Vehicle target)
        {
            var from = v.Position;
            var to = target.Position;
            var d = to - from;
            var length = d.Length();
            if (length < 4f) return false;
            var dir = d / length;
            foreach (var f in _world.VehicleList)
            {
                if (f == v || !f.IsAlive || f.Team != v.Team || f.Flying || f.Def.Static) continue;
                var rel = f.Position - from;
                var along = Vector2.Dot(rel, dir);
                if (along <= 2f || along >= length - 2f || along > 60f) continue;
                var across = MathF.Abs(rel.X * dir.Y - rel.Y * dir.X);
                if (across < f.Radius + 1f) return true;
            }
            return false;
        }
    }
}
