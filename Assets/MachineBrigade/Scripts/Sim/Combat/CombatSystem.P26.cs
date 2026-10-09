#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Prompt 26 B.9 (DECISIONS 26AB): what a boss's weapons go for. An area weapon (a blast of 3 m or more) goes for the spot
    /// with the most vehicles in its core, a direct-fire gun for the dearest vehicle in reach; anti-air and the rest as before
    /// (aircraft first for the anti-air weapons, see <see cref="Score"/>).
    /// </summary>
    internal sealed partial class CombatSystem
    {
        /// <summary>An area weapon's core must reach at least this far to look for a crowd.</summary>
        internal const float CrowdFrom = 3f;

        /// <summary>The most a crowd in the core can raise a target's weight (and a dear target's, over the ordinary worth rule).</summary>
        internal static float CrowdMax => global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.CrowdMax;

        /// <summary>The boss's weighting of a ground target by weapon type; 1 for everyone else's fire.</summary>
        private float P26Worth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            if (!v.Def.Boss || other.Flying || weapon.Beam || weapon.Targets == TargetLayers.Air) return 1f;
            var worth = Math.Clamp(Worth(other), global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P26WorthWorthMin, global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P26WorthWorthMax);
            if (weapon.SplashRadius >= CrowdFrom)
            {
                // What stands in the core round this target, by worth, over the target's own.
                var core = weapon.SplashRadius;
                var crowd = worth;
                foreach (var e in _world.VehicleList)
                {
                    if (e == other || !e.IsAlive || e.Flying || e.Team != other.Team || e.Def.Static && e.Def.Obstacle) continue;
                    if (Vector2.DistanceSquared(e.Position, other.Position) <= (core + e.Radius) * (core + e.Radius)) crowd += Math.Clamp(Worth(e), 1f, global::MachineBrigade.Sim.Content.SimTunables.Weapons.CombatSystem.P26WorthWorthMax);
                }
                return Math.Clamp(crowd / worth, 1f, CrowdMax);
            }
            // A gun that fires straight: the dearest vehicle (the ordinary rule weighs worth by its square root; this makes it linear).
            return MathF.Sqrt(worth / 10f);
        }
    }
}
