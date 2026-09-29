#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Sandbox;

namespace MachineBrigade.Sim
{
    /// <summary>
    /// Prompt 21: what the Sandbox needs of the battlefield, kept out of the main file. Nothing here runs unless the
    /// Sandbox (or a test) asks for it: the hit report is null in every other battle.
    /// </summary>
    public sealed partial class SimWorld
    {
        /// <summary>
        /// Told of every hit a vehicle takes (the face struck, the penetration multiplier, what got through); null in
        /// play. The Sandbox's statistics and floating hit numbers read it; it never changes the battle.
        /// </summary>
        public Action<HitReport>? HitLog { get; set; }

        internal void ReportHit(Vehicle victim, float dealt, DamageType type, ArmorFace face, float pen, in HitInfo hit) =>
            HitLog?.Invoke(new HitReport(Tick, hit.Attacker?.Id.Value ?? 0, hit.Attacker?.Team ?? hit.Team, victim.Id.Value, victim.Team, dealt, type,
                face, pen, victim.Position, victim.IsAlive));

        /// <summary>
        /// Places a vehicle with its own card rank and equipment (a Sandbox unit), whatever its side's boosts are:
        /// <paramref name="boost"/> null leaves it as the data has it.
        /// </summary>
        public Vehicle SpawnBoosted(string defId, int team, Vector2 position, float heading, VehicleBoost? boost)
        {
            if (team < 0 || team >= _boosts.Length) return SpawnVehicle(defId, team, position, heading);
            var (was, all) = (_boosts[team], _boostAll[team]);
            _boosts[team] = boost is { } b ? _ => b : null;
            _boostAll[team] = boost != null;
            try
            {
                return SpawnVehicle(defId, team, position, heading);
            }
            finally
            {
                _boosts[team] = was;
                _boostAll[team] = all;
            }
        }

        /// <summary>Fog of war (prompt 21 B.8): off, every vehicle is in everyone's sight.</summary>
        public bool FogOfWar
        {
            get => !RevealAll;
            set => RevealAll = !value;
        }
    }
}
