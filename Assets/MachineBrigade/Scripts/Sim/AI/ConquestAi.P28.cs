#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// Prompt 28: the layered AI on top of the commander of prompt 13. The general (<see cref="AiCommander"/>) plans and
    /// hands squads their tasks; the squad layer moves the ground army; TacticalAi keeps its helpers and the aircraft;
    /// buying gains the tactic's force shares, supports follow events.
    /// </summary>
    public sealed partial class ConquestAi
    {
        /// <summary>Whether new commanders use the layered AI (a switch to compare with the old AI, O.3).</summary>
        public static bool LayeredDefault = true;

        public bool Layered { get; set; } = LayeredDefault;

        /// <summary>The side's general (made on the first tick).</summary>
        public AiCommander? Commander { get; private set; }

        /// <summary>The tactic to start with (H.4: the player's choice; null: the general's preference, H.7).</summary>
        public string? Tactic { get; set; }

        /// <summary>The AI's skill; null: the difficulty's (K). The player's Auto-buy and Support AI should be Normal (K.2).</summary>
        public AiSkill? Skill { get; set; }

        /// <summary>The player's hint line (B.7).</summary>
        public AiHints Hints { get; } = new();

        private void TickLayered(SimWorld world, float dt)
        {
            if (Commander == null)
            {
                world.TryGetEconomy(_team, out var economy);
                // Prompt 28 appendix: the general's preference only where the profile plays it (campaign, operations, a
                // weekly fortress with its general); quick battles start balanced. Then the profile's allowed tactics.
                var profile = world.AiProfile;
                var general = profile.GeneralTactic || world.ModeTag is "Weekly" or "Operation";
                var tactic = AiCommander.AllowedTactic(world, Tactic ?? (general ? world.Catalog.AiData.GeneralTactic(economy?.Commander?.Id) : "balanced"));
                Commander = new AiCommander(_team, _enemyTeam, Skill ?? AiSkill.For(_difficulty, world.Catalog.Ai), tactic, ChooseObjective);
                world.AiCommanders[_team] = Commander;
                world.AiLog.Add(new DecisionEntry(world.Time, _team, AiLayer.Commander, 0, DecisionKind.Tactic, $"start {tactic}"));
            }
            // Recon before the alarm: patrol and hold, no chasing (engagement AVOID_UNLESS_BLOCKING).
            Commander.Defending = Stance == CommanderStance.Defend ||
                world.AiProfile.Engagement == EngagementPolicy.AvoidUnlessBlocking && !world.Alarm;
            world.AiCommanders.TryGetValue(_enemyTeam, out var enemy);
            Commander.Tick(world, dt, _tactics.GroundPool, enemy);
        }

        /// <summary>B.4: the support card the general wants now (smoke on a shelled squad, SEAD before an air window).</summary>
        private bool TrySupportWanted(SimWorld world, TeamEconomy economy)
        {
            if (Commander?.SupportWanted(world) is not { } want) return false;
            foreach (var id in economy.Supports)
            {
                if (!world.Catalog.Supports.TryGetValue(id, out var s) || s.Kind != want.kind || !Ready(world, economy, s)) continue;
                if (world.Submit(Command.Strike(_team, id, want.at)).Accepted)
                {
                    // AI MASTER P3 spec 142 / 144: the smoke mission on the board, the battery marked struck.
                    Commander!.NoteSupportP3(world, want.kind, want.at);
                    world.AiLog.Add(new DecisionEntry(world.Time, _team, AiLayer.Commander, 0, DecisionKind.Plan, $"support {id} for {want.kind}"));
                    return true;
                }
            }
            return false;
        }

        private void Bought(SimWorld world, string id, TeamEconomy economy)
        {
            if (Commander != null && world.Catalog.Vehicles.TryGetValue(id, out var def)) Commander.Bought(def, def.BaseCp); // R7: shares by base CP
        }
    }
}
