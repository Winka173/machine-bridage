#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Economy
{
    /// <summary>
    /// One side's elite budget (prompt 8 H): instead of a chance per delivery, a share of what the
    /// side spends may go on elites (they cost 1.6 times their base card), with a cap on how many
    /// are out at once. Both come from the difficulty (balance.json "elites"); a general favours
    /// some cards (Varga his tanks), the others get only part of the share. Waves and reinforcements
    /// sent for free are counted at their CP value, so they follow the same budget.
    /// </summary>
    public sealed class EliteBudget
    {
        /// <summary>The share of the side's spending that may go on elites (0: none).</summary>
        public float Share { get; set; }

        /// <summary>How many elites may be out at once (in the field or on their way).</summary>
        public int Cap { get; set; }

        /// <summary>The side's general, whose favoured cards get the whole share (null: every card alike).</summary>
        public GeneralRules? General { get; set; }

        /// <summary>CP value of every vehicle bought or sent since the battle began, elites at their elite price.</summary>
        public float Spent { get; internal set; }

        /// <summary>The elites' part of <see cref="Spent"/>.</summary>
        public float EliteSpent { get; internal set; }

        /// <summary>How many deliveries went out as elites.</summary>
        public int Promoted { get; internal set; }
    }

    internal sealed partial class EconomySystem
    {
        private readonly Dictionary<int, EliteBudget> _elite = new();

        public EliteBudget EliteBudgetOf(int team)
        {
            if (!_elite.TryGetValue(team, out var budget)) _elite[team] = budget = new EliteBudget();
            return budget;
        }

        /// <summary>
        /// The elite this card may go out as now, or null: the side has a budget, the card an elite
        /// version, the elite's price keeps the elites' part of the spending within the share (the
        /// general's other cards get <see cref="EliteRules.OtherShare"/> of it) and the cap is not reached.
        /// </summary>
        private VehicleDef? EliteRoom(int team, VehicleDef def, float minShare = 0f, int extraCap = 0)
        {
            if (!_elite.TryGetValue(team, out var budget)) return null;
            var share = MathF.Max(budget.Share, minShare);
            if (share <= 0f || budget.Cap + extraCap <= 0) return null;
            if (_world.Catalog.EliteVariant(def.Id) is not { } id || !_world.Catalog.Vehicles.TryGetValue(id, out var elite)) return null;
            if (budget.General != null && !budget.General.Prefers(def)) share *= _world.Catalog.Elites.OtherShare;
            var price = (float)elite.ArmyCost;
            if (budget.EliteSpent + price > share * (budget.Spent + price) + 0.001f) return null;
            if (ElitesOut(team) >= budget.Cap + extraCap) return null;
            return elite;
        }

        private void Count(int team, VehicleDef sent)
        {
            var budget = EliteBudgetOf(team);
            budget.Spent += sent.ArmyCost;
            if (!sent.Elite) return;
            budget.EliteSpent += sent.ArmyCost;
            budget.Promoted++;
        }

        /// <summary>
        /// A bought card, already paid for at its own price: the elite version instead when the
        /// budget has room and the side can pay the difference to the elite's price.
        /// </summary>
        private string Promote(int team, TeamEconomy economy, VehicleDef def)
        {
            var sent = def;
            if (EliteRoom(team, def) is { } elite)
            {
                var extra = elite.ArmyCost - def.CpCost;
                if (economy.Cp >= extra)
                {
                    economy.Cp -= extra;
                    sent = elite;
                }
            }
            Count(team, sent);
            return sent.Id;
        }

        /// <summary>
        /// A vehicle a wave or a reinforcement sends for free: its elite version when the budget has
        /// room, counted at its CP value either way. <paramref name="minShare"/> raises the share for
        /// this wave (a siege's late waves), and with it the cap by one elite per tenth.
        /// </summary>
        public string ForWave(int team, string defId, float minShare = 0f)
        {
            if (!_world.Catalog.Vehicles.TryGetValue(defId, out var def)) return defId;
            var extraCap = minShare > 0f ? (int)MathF.Ceiling(minShare * 10f) : 0;
            var sent = EliteRoom(team, def, minShare, extraCap) ?? def;
            Count(team, sent);
            return sent.Id;
        }

        /// <summary>Elites of a side out now: in the field or on their way (bosses and their parts aside).</summary>
        internal int ElitesOut(int team)
        {
            var n = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team && v.Def.Elite && !v.Def.Boss) n++;
            foreach (var p in _pending)
                if (p.team == team && _world.Catalog.Vehicles.TryGetValue(p.defId, out var d) && d.Elite) n++;
            return n;
        }
    }
}
