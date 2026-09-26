#nullable enable
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// Placeholder opponent: once a second, idle vehicles attack-move as a group towards the
    /// nearest enemy (or the enemy rally point). It issues ordinary commands, so it plays by
    /// the same rules as the player. The utility-based AI from the plan replaces it later.
    /// </summary>
    public sealed class SandboxAi
    {
        private const float DecisionInterval = 1f;

        private readonly int _team;
        private readonly int _enemyTeam;
        private readonly List<EntityId> _idle = new();
        private float _timer;

        public SandboxAi(int team, int enemyTeam)
        {
            _team = team;
            _enemyTeam = enemyTeam;
        }

        public void Tick(SimWorld world, float dt)
        {
            _timer -= dt;
            if (_timer > 0f) return;
            _timer = DecisionInterval;

            _idle.Clear();
            var centre = Vector2.Zero;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Team != _team || v.Order.Kind != OrderKind.Idle || v.Target.IsValid) continue;
                _idle.Add(v.Id);
                centre += v.Position;
            }
            if (_idle.Count == 0) return;
            centre /= _idle.Count;

            if (TryFindObjective(world, centre, out var objective))
                world.Submit(new Command(CommandType.AttackMove, _team, _idle.ToArray(), objective));
        }

        private bool TryFindObjective(SimWorld world, Vector2 from, out Vector2 objective)
        {
            var best = float.MaxValue;
            objective = default;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Team != _enemyTeam) continue;
                var d = Vector2.DistanceSquared(from, v.Position);
                if (d >= best) continue;
                best = d;
                objective = v.Position;
            }
            if (best < float.MaxValue) return true;
            return world.TryGetRally(_enemyTeam, out objective);
        }
    }
}
