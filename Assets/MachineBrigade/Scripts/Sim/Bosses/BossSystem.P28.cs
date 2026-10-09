#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Prompt 28 F: boss behaviour types (sheet "Kiểu hành vi boss") on the bosses' existing weapons and escorts: the big
    /// attack's aim by type (F.3, the warning times unchanged), a ground boss turning its front slowly to the most
    /// firepower (F.4), escorts screening the side the enemy is massed on and closing round the boss on a new phase
    /// (F.5). Bosses see only what their side sees (F.6). Target weights are in CombatSystem.BossWorth (F.2).
    /// </summary>
    internal sealed partial class BossSystem
    {
        private readonly Dictionary<EntityId, (double at, float bearing)> _escortBearing = new();
        private readonly Dictionary<EntityId, double> _escortsClose = new();
        private readonly Dictionary<EntityId, int> _escortWaves = new();
        private double _faceAt;

        /// <summary>The boss's behaviour types (minis by their base id too); empty for a boss without a row.</summary>
        internal IReadOnlyList<BossBehaviour> Behaviours(Vehicle boss)
        {
            var data = _world.Catalog.AiData.Bosses;
            if (data.TryGetValue(boss.Def.Id, out var kinds)) return kinds;
            foreach (var kv in data)
                if (boss.Def.Id.StartsWith(kv.Key, StringComparison.Ordinal)) return kv.Value;
            return Array.Empty<BossBehaviour>();
        }

        private void StepP28(double now)
        {
            if (now < _faceAt) return;
            _faceAt = now + 1.0;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || !v.Def.Boss || v.Flying) continue;
                // Play-test 14: a train's body stays on its track; only its turrets bear.
                if (v.Def.Frame?.Move == BossMove.Rail) { v.FaceHeading = null; continue; }
                // F.4: the front (armour 5) to where most firepower comes from; slowly (half the turn rate), so it can be flanked.
                v.FaceHeading = Firepower(v, 100f) is { } bearing ? bearing : null;
            }
        }

        /// <summary>The heading towards the enemy firepower round <paramref name="boss"/> that its side can see, by strength.</summary>
        private float? Firepower(Vehicle boss, float reach)
        {
            var sum = Vector2.Zero;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == boss.Team || e.Team < 0 || !e.IsVisibleTo(boss.Team)) continue;
                var d = e.Position - boss.Position;
                var distance = d.Length();
                if (distance < 1f || distance > reach) continue;
                sum += d / distance * TeamIntel.StrengthOf(e);
            }
            return sum.LengthSquared() > global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossSystem.FirepowerLengthSquaredMin ? SimMath.HeadingOf(sum) : null;
        }

        /// <summary>F.5: the bearing escorts screen: the enemy mass round the boss (once a second), else the boss's heading.</summary>
        private float EscortBearing(Vehicle boss)
        {
            var now = _world.Time;
            if (_escortBearing.TryGetValue(boss.Id, out var c) && now - c.at < 1.0) return c.bearing;
            var bearing = Firepower(boss, 90f) ?? boss.Heading;
            _escortBearing[boss.Id] = (now, bearing);
            return bearing;
        }

        /// <summary>F.5: escorts close round the boss for 8 s after a new phase (an escort wave counts one).</summary>
        private float EscortSpread(EscortGroup g)
        {
            var now = _world.Time;
            _escortWaves.TryGetValue(g.Boss.Id, out var seen);
            if (g.Waves > seen)
            {
                _escortWaves[g.Boss.Id] = g.Waves;
                _escortsClose[g.Boss.Id] = now + global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossSystem.EscortSpreadNowAdd;
            }
            return _escortsClose.TryGetValue(g.Boss.Id, out var until) && now < until ? global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossSystem.EscortSpreadTryGetValueTrue : 1f;
        }

        /// <summary>F.3: a big attack's aim by the boss's type, used where its own aim is the generic densest group.</summary>
        private bool BehaviourAim(Vehicle v, BigAttackDef def, out Vector2 aim)
        {
            aim = v.Position;
            var kinds = Behaviours(v);
            if (kinds.Count == 0) return false;
            Vector2 best = v.Position;
            var bestScore = 0f;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying || !e.IsVisibleTo(v.Team)) continue;
                if (def.Reach > 0f && Vector2.Distance(e.Position, v.Position) > def.Reach) continue;
                var score = 1f + Crowd(e, 10f) * 0.5f;
                foreach (var k in kinds)
                    score *= k switch
                    {
                        BossBehaviour.AntiArtillery => e.Def.Weapon.MinRange > 0f ? global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossSystem.BehaviourAimMinRangeTrue : 1f,
                        BossBehaviour.AreaDenial => e.IsMoving ? 1f : 1.6f,
                        BossBehaviour.AntiBlob => 1f + Crowd(e, 10f) * 0.4f,
                        BossBehaviour.CoreProtection => Vector2.Distance(e.Position, v.Position) < global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossSystem.BehaviourAimDistanceMax ? global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossSystem.BehaviourAimDistanceTrue : 1f,
                        BossBehaviour.FlankPunishment => Behind(v, e) ? 2.2f : 1f,
                        _ => 1f,
                    };
                if (score > bestScore)
                {
                    bestScore = score;
                    best = e.Position;
                }
            }
            if (bestScore <= 0f) return false;
            aim = best;
            return true;
        }

        private int Crowd(Vehicle e, float radius)
        {
            var n = 0;
            foreach (var o in _world.VehicleList)
                if (o != e && o.IsAlive && o.Team == e.Team && !o.Flying && Vector2.DistanceSquared(o.Position, e.Position) <= radius * radius) n++;
            return n;
        }

        /// <summary>The enemy is off the boss's front arc (more than 60 degrees from its heading).</summary>
        internal static bool Behind(Vehicle boss, Vehicle e)
        {
            var to = e.Position - boss.Position;
            if (to.LengthSquared() < global::MachineBrigade.Sim.Content.SimTunables.Bosses.BossSystem.BehindLengthSquaredMax) return false;
            return Vector2.Dot(Vector2.Normalize(to), SimMath.Forward(boss.Heading)) < 0.5f;
        }
    }
}
