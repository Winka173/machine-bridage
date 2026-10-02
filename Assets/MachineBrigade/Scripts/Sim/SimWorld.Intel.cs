#nullable enable
using System;
using MachineBrigade.Sim.AI;

namespace MachineBrigade.Sim
{
    public sealed partial class SimWorld
    {
        private WorldModel? _intel;

        /// <summary>Prompt 28 A: the shared battlefield picture the AI layers read (refreshed on demand, read-only).</summary>
        public WorldModel Intel => _intel ??= new WorldModel(this);

        /// <summary>Prompt 28 J.2-J.4: the AI's "VÌ SAO" records, churn counters and replay decision log.</summary>
        public DecisionLog AiLog { get; } = new();

        /// <summary>Prompt 28: each side's layered AI general, once it has one (a general reads the other's tactic only through scouts).</summary>
        public System.Collections.Generic.Dictionary<int, AiCommander> AiCommanders { get; } = new();

        /// <summary>
        /// Prompt 28 N: a random stream for one AI layer of one side, from the battle's seed. Each layer has its own
        /// stream, so adding or reordering a draw in one never shifts another's (or the battle's own), and a replay of
        /// the same seed draws the same numbers. Layers: 0 commander, 1 squads, 2 units, 3 tactic choice; free above.
        /// </summary>
        public Random AiRandom(int team, int layer) => new(unchecked(Seed * 7919 + (team + 3) * 104729 + layer * 1299709));

        /// <summary>
        /// Prompt 28 E.1: sets a tower's targeting mode (the Base screen and a tap on the tower in battle): the data's
        /// default for its type or one of its listed modes; Default goes back to the data's. False when not allowed.
        /// </summary>
        public bool SetTowerMode(int team, Core.EntityId tower, TowerMode mode)
        {
            if (!TryGetVehicle(tower, out var v) || !v.IsAlive || v.Team != team || !v.Def.Static) return false;
            if (mode != TowerMode.Default)
            {
                if (!Catalog.AiData.Towers.TryGetValue(v.Def.Id, out var def)) return false;
                var ok = def.Mode == mode;
                foreach (var m in def.Modes) ok |= m == mode;
                if (!ok) return false;
            }
            v.TowerMode = mode;
            AiLog.Add(new DecisionEntry(Time, team, AiLayer.Unit, tower.Value, DecisionKind.Target, $"tower mode {mode}"));
            return true;
        }
    }
}
