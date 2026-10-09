#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// Prompt 28 I.6, on the battle events of prompt 23: pressure rises while no big fight happens (measured as the
    /// health both sides lost in the last 5 s, at least ai.world.bigFight). Tier 1 (economy.escalation.0, ~30 s): points
    /// are worth more (income and ticket bleed x world.escalationPoints); tier 2 (~50 s): a supply crate in the middle;
    /// tier 3 (~70 s): a barrage on the passive side (the army further from the middle); tier 4 (~90 s): each army is
    /// revealed to the other for 15 s. A big fight goes back to tier 0.
    /// </summary>
    public sealed partial class BattleEvents
    {
        // Balance final (spec 15): the scripted barrage (event support, the card's old values), not the Artillery Barrage card.
        private const string PressureBarrage = "scripted_barrage";

        private readonly Dictionary<EntityId, float> _health = new();
        private readonly float[] _window = new float[5];
        private double _lastFight, _nextSample;
        private int _windowAt;

        /// <summary>Whether the pressure tiers run (on in every mode with battle events).</summary>
        public bool Escalation { get; set; } = true;

        /// <summary>The tier reached (0: a fight is on or the field has been quiet only briefly).</summary>
        public int Tier { get; private set; }

        private void Escalate(SimWorld world, double now)
        {
            if (now < _nextSample) return;
            _nextSample = now + 1.0;
            var ai = world.Catalog.Ai;
            // Health lost in the last second, then the last 5 s.
            var lost = 0f;
            foreach (var v in world.VehicleList)
            {
                if (v.Team < 0 || v.Def.Static) continue;
                if (_health.TryGetValue(v.Id, out var hp) && v.Hp < hp) lost += hp - v.Hp;
                _health[v.Id] = v.IsAlive ? v.Hp : 0f;
            }
            _window[_windowAt] = lost;
            _windowAt = (_windowAt + 1) % _window.Length;
            var recent = 0f;
            foreach (var x in _window) recent += x;
            if (recent >= ai.Get("world.bigFight", 600f) || _lastFight == 0.0)
            {
                _lastFight = now;
                if (Tier > 0) SetTier(world, 0);
                return;
            }
            var quiet = now - _lastFight;
            var tier = 0;
            for (var i = 0; i < 4; i++)
                if (quiet >= ai.Get($"economy.escalation.{i}", 30f + 20f * i)) tier = i + 1;
            tier = Math.Min(tier, MaxTier(world.Stall));
            if (tier > Tier) SetTier(world, tier);
        }

        /// <summary>
        /// Prompt 28 appendix B: the stall policy caps the tiers. Off: none (escort, siege, waves); objective only: tier
        /// 1 (points worth more); attacker only and both: all four, the barrage and reveal aimed by <see cref="Pushed"/>.
        /// </summary>
        public static int MaxTier(Content.StallPolicy stall) => stall switch
        {
            Content.StallPolicy.Off => 0,
            Content.StallPolicy.ObjectiveStallOnly => 1,
            _ => global::MachineBrigade.Sim.Content.SimTunables.Modes.BattleEvents.MaxTierStallValue,
        };

        /// <summary>The side the tier-3 barrage and tier-4 reveal push: the attacker when one side defends, else the passive one.</summary>
        public static Vector2? Pushed(SimWorld world)
        {
            if (world.Stall == Content.StallPolicy.AttackerOnly && world.DefenderTeam is { } defender) return ArmyCentre(world, 1 - defender);
            return world.DefenderTeam is { } d ? ArmyCentre(world, 1 - d) : Passive(world);
        }

        private void SetTier(SimWorld world, int tier)
        {
            Tier = tier;
            world.PressureTier = tier;
            world.PointScale = tier >= 1 ? world.Catalog.Ai.Get("world.escalationPoints", 1.5f) : 1f;
            world.AiLog.Add(new DecisionEntry(world.Time, -1, AiLayer.Commander, 0, DecisionKind.Plan, $"pressure tier {tier}"));
            switch (tier)
            {
                case 2:
                    DropCrate(world, world.Time);
                    break;
                case 3:
                    if (Pushed(world) is { } passive && world.Catalog.TryGetSupport(PressureBarrage, out var support))
                        world.Strikes.Launch(support, Teams.Environment, passive, passive + Vector2.UnitX);
                    break;
                case 4:
                    // The defender's army is never revealed to push it off its ground; the attacker's is shown to it.
                    for (var team = 0; team <= 1; team++)
                        if (team != world.DefenderTeam && ArmyCentre(world, team) is { } at) world.Strikes.AddScan(1 - team, at, 45f, 15f);
                    break;
            }
        }

        /// <summary>The centre of the army further from the middle of the map (the side sitting back).</summary>
        private static Vector2? Passive(SimWorld world)
        {
            var a = ArmyCentre(world, 0);
            var b = ArmyCentre(world, 1);
            if (a == null || b == null) return a ?? b;
            var centre = world.Map.Centre;
            return Vector2.Distance(a.Value, centre) >= Vector2.Distance(b.Value, centre) ? a : b;
        }

        private static Vector2? ArmyCentre(SimWorld world, int team)
        {
            var sum = Vector2.Zero;
            var n = 0;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == team && !v.Flying && !v.Def.Static)
                {
                    sum += v.Position;
                    n++;
                }
            return n > 0 ? sum / n : null;
        }
    }
}
