#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// AI MASTER lane P0-B: the buying AI's <see cref="ProcurementDirector"/> inside TryDeploy (Part A: the legacy score
    /// stays; the director filters first and adds the master score). See Docs/ai/spec_master/AUDIT_P0B.md.
    /// </summary>
    public sealed partial class ConquestAi
    {
        private ProcurementDirector? _procurement;
        private readonly List<(string id, float score)> _ranked = new();

        /// <summary>The side's procurement director (made on first use).</summary>
        public ProcurementDirector Procurement => _procurement ??= new ProcurementDirector(_team);

        /// <summary>Observes the battle for this decision: the drop zone, what is seen, the objectives and the tactic's shares.</summary>
        private void ObserveForProcurement(SimWorld world, TeamEconomy economy, float[] mix)
        {
            var deployAt = world.Bases.TryGetDropZone(_team, out var zone) ? zone : world.TryGetRally(_team, out var rally) ? rally : Vector2.Zero;
            var goal = Goal?.Invoke(world);
            var groups = Commander?.Targets(world, economy);
            Procurement.Observe(world, _tactics.KnownEnemies, deployAt, _mode, goal, DefendPoint, groups, RoleMix ?? mix);
        }

        /// <summary>The legality checks of TryDeploy's loop (bosses and trucks never; caps, limits, the aircraft cap).</summary>
        private bool Legal(SimWorld world, TeamEconomy economy, VehicleDef def, bool airFull) =>
            !def.Boss && def.CpCost > 0 && def.Card &&
            economy.VehicleCount < economy.VehicleCap &&
            !(def.MaxPerSide > 0 && world.Economy.Fielded(_team, def.Id) >= def.MaxPerSide) &&
            !(def.Flying && airFull && !def.AirCapFree);

        /// <summary>
        /// Section 16: the plan's next card first. True when this decision is done (bought, or saving for the plan's card);
        /// false lets the normal choice run (no plan, a thin army, CP about to overflow).
        /// </summary>
        private bool TryPlanned(SimWorld world, TeamEconomy economy, bool airFull, int ownTotal)
        {
            var director = Procurement;
            if (!director.PlanValid(world)) return false;
            var plan = director.Plan!;
            var id = plan.Cards[plan.Next];
            if (!world.Catalog.Vehicles.TryGetValue(id, out var def) || !Legal(world, economy, def, airFull))
            {
                director.Skip();
                return false;
            }
            if (!director.Gate(world, def, out _))
            {
                director.CancelPlan(world, "card-rejected");
                return false;
            }
            if (economy.PriceOf(id, def.CpCost) <= economy.Cp)
            {
                // AI MASTER P4 (P0-B 18): the forecast says the force is enough, or a seen boss nears its next phase: keep the CP.
                if (Commander != null && Commander.HoldPurchaseP4(world, economy, economy.PriceOf(id, def.CpCost), ownTotal)) return true;
                DeployOrDrop(world, id);
                Bought(world, id, economy);
                director.Bought(world, id, float.NaN, null);
                return true;
            }
            return !(ownTotal < 4 || economy.Cp >= economy.Bank - 3f || _difficulty == AiDifficulty.Easy);
        }

        /// <summary>Sorts the scored cards best first (ties by id, so a replay ranks the same).</summary>
        private void RankScored()
        {
            _ranked.Sort((a, b) => a.score != b.score ? b.score.CompareTo(a.score) : string.CompareOrdinal(a.id, b.id));
        }

        /// <summary>The best-ranked card that answers a confirmed counter need (section 18's reserve), or null.</summary>
        private VehicleDef? CounterCard(SimWorld world)
        {
            foreach (var (id, _) in _ranked)
                if (world.Catalog.Vehicles.TryGetValue(id, out var def) && Procurement.AnswersConfirmed(def, world.Time)) return def;
            return null;
        }

        /// <summary>Buys <paramref name="id"/> through the director: a reserve may hold it back; a plan is made when none runs.</summary>
        private bool BuyThroughDirector(SimWorld world, TeamEconomy economy, string id, float score, int ownTotal)
        {
            var director = Procurement;
            var def = world.Catalog.Vehicles[id];
            RankScored();
            if (director.Reserve(world, economy, def, CounterCard(world), ownTotal < 4, UnderFire(world))) return false;
            // AI MASTER P4 (P0-B 18): force enough by the forecast / CP kept for a seen boss's next phase.
            if (Commander != null && !UnderFire(world) && Commander.HoldPurchaseP4(world, economy, economy.PriceOf(id, def.CpCost), ownTotal)) return false;
            if (director.Plan == null && _difficulty != AiDifficulty.Easy && _ranked.Count >= SimTunables.Ai.Procurement.MinPlanCards &&
                _ranked[0].id == id)
                director.MakePlan(world, economy, _ranked, _difficulty);
            DeployOrDrop(world, id);
            Bought(world, id, economy);
            List<Factor>? factors = null;
            if (director.Context != null && director.Gate(world, def, out var influence))
            {
                factors = new List<Factor>();
                director.Score(world, economy, def, influence, CopiesOf(world, def.Id), Commander, factors);
            }
            director.Bought(world, id, score, factors);
            return true;
        }

        private int CopiesOf(SimWorld world, string id)
        {
            var n = 0;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == _team && (v.Def.Id == id || v.Def.EliteOf == id)) n++;
            return n;
        }
    }
}
