using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 31 L4 (DECISIONS "Prompt 31 L4"): the placed allies of the MAKE LATER fixed decks. c6m03 first: Mara's Behemoth is
    /// the Escort's own convoy (the objective kept), shown as the placed ally, holding while the general order is Defend; a
    /// placed ally that is not a convoy comes onto the field on the player's side under the allied AI, and one the mission
    /// cannot lose loses it when it falls. Written for the lead to run (agents write tests, they do not run them).
    /// </summary>
    public class Prompt31PlacedAllyTests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static MissionDef Mission(string id) => Campaign.Everything.First(m => m.Id == id);

        private static SimWorld Field(int seed = 1) => new(Catalog, new MapDefinition("field", 300f,
            new[] { new TeamStart(0, new Vector2(-108.75f, -108.75f)), new TeamStart(1, new Vector2(108.75f, 108.75f)) },
            new List<PropPlacement>(), new List<UnitPlacement>()), seed);

        private static void Run(SimWorld world, MissionMode mode, float seconds)
        {
            for (var t = 0f; t < seconds; t += Dt)
            {
                mode.Tick(world, Dt);
                world.Step(Dt);
                world.ClearEvents();
                if (world.IsOver) return;
            }
        }

        // ================================================================== the data

        [Test]
        public void C6m03sBehemothIsItsConvoyAndThePlacedAlly()
        {
            var m = Mission("c6m03");
            Assert.IsNotNull(m.FixedDeck, "c6m03 has its fixed deck");
            Assert.AreEqual("MAKE_LATER", m.FixedDeck.Status);
            Assert.AreEqual(1, m.FixedDeck.PlacedAllies.Count);
            var ally = m.FixedDeck.PlacedAllies[0];
            Assert.IsTrue(ally.Convoy && ally.LossIfDestroyed, "the escorted Behemoth, lost if it falls");
            Assert.AreEqual(m.Convoy.Def, ally.Def, "the convoy unit itself, not a second Behemoth");
            // The objective before prompt 31: escort the one Behemoth to the end of its route.
            Assert.AreEqual(MissionGoal.Escort, m.Goal);
            Assert.AreEqual(1, m.ConvoyCount);
            Assert.AreEqual(1, m.ConvoyNeeded);
            Assert.AreEqual("behemoth", m.Convoy.Def);
        }

        [Test]
        public void EveryPlacedAllyIsAUnitTheBattleCanSpawn()
        {
            foreach (var m in Campaign.Everything.Where(m => m.FixedDeck != null))
                foreach (var ally in m.FixedDeck.PlacedAllies)
                {
                    Assert.IsNotNull(ally.SpawnDef(Catalog), $"{m.Id}: {ally.Def}");
                    if (ally.Convoy) Assert.AreEqual(m.Convoy?.Def, ally.Def, $"{m.Id}: a convoy ally is the mission's convoy");
                    if (ally.Name != null) Assert.IsTrue(Strings.Has("fixeddeck.ally." + ally.Name), $"{m.Id}: fixeddeck.ally.{ally.Name}");
                }
        }

        /// <summary>The MAKE LATER missions prompt 31 L4 made (DECISIONS "Prompt 31 L4"); none is left on the player's deck.</summary>
        private static readonly string[] MadeLater = { "c6m03", "c10m12", "c12m03", "i1m01", "c5m03", "c6m14", "i2m01", "c7m16", "c9m12", "c10m11" };

        [Test]
        public void EveryMakeLaterMissionMadeHasItsDeck()
        {
            foreach (var id in MadeLater)
            {
                var deck = Mission(id).FixedDeck;
                Assert.IsNotNull(deck, $"{id}: a fixed deck");
                Assert.AreEqual("MAKE_LATER", deck.Status, id);
                Assert.IsNotEmpty(deck.SpecialRules, $"{id}: its rule");
            }
            Assert.IsTrue(Mission("c10m12").FixedDeck.PlacedAllies.Single().LossIfDestroyed, "Hawk's fighter must live");
            Assert.IsFalse(Mission("c12m03").FixedDeck.PlacedAllies.Single().LossIfDestroyed, "c12m03 asks no more than c6m03");
        }

        [Test]
        public void C6m14sSwornColumnTakesNothingFromUsAndTheTruceHolds()
        {
            var ceasefire = Mission("c6m14").Events.First(e => e.Kind == MissionEventKind.Ceasefire);
            Assert.IsTrue(ceasefire.Flag("faction", false), "Varga's column is a ceasefire faction");
            Assert.GreaterOrEqual(ceasefire.Number("seconds", 0f), Mission("c6m14").TimeLimit, "for the whole battle");

            const string sworn = "{\"id\": \"cf\", \"kind\": \"Ceasefire\", \"trigger\": {\"at\": 1}, \"params\": {\"seconds\": 60, \"size\": 3, " +
                                 "\"enemyCp\": 20, \"faction\": true}}";
            var def = MissionDef.ListFromJson("{\"eventLibrary\": {\"events\": [" + sworn + "]}, \"missions\": [{\"id\": \"p31cf\", \"map\": \"field\", " +
                                              "\"goal\": \"Survive\", \"surviveSeconds\": 5000, \"enemyAi\": \"none\", \"general\": \"varga\", " +
                                              "\"missionEvents\": [\"cf\"]}]}")[0];
            var world = Field();
            var mode = new MissionMode(def, new SideSetup(), new SideSetup()) { EventLevel = EventLevel.Normal };
            mode.Setup(world);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-100f, -100f), 0f).Invulnerable = true;
            Run(world, mode, 2f);
            var column = world.Vehicles.Where(v => v.IsAlive && v.Team == 1 && v.Truce).ToList();
            Assert.AreEqual(3, column.Count, "the sworn column");
            Assert.IsTrue(column.All(v => v.Sworn));
            var gunner = world.SpawnVehicle("main_battle_tank", 0, column[0].Position + new Vector2(0f, -22f), 0f);
            gunner.Invulnerable = true;
            world.SubmitPlayer(new MachineBrigade.Sim.Commands.Command(MachineBrigade.Sim.Commands.CommandType.Attack, 0, new[] { gunner.Id },
                column[0].Position, column[0].Id, manual: true));
            Run(world, mode, 8f);
            Assert.IsTrue(column.All(v => v.Hp >= v.MaxHp), "an ordered attack does nothing to a sworn vehicle");
            Assert.IsFalse(mode.Events.Log.Any(l => l.moment == "broken"), "no shot of ours breaks the truce");
            Assert.AreEqual(EventPhase.Running, mode.Events.States[0].Phase);
            Assert.IsFalse(world.IsOver, "no loss for friendly fire");
        }

        // ================================================================== the battle

        private const string Deck = "\"vehicleIds\": [\"scout_jeep\", \"armored_car\", \"ifv\", \"main_battle_tank\", \"light_tank\", \"tank_destroyer\", " +
                                    "\"aa_vehicle\", \"mortar_carrier\"], \"supportIds\": [\"smoke_screen\", \"artillery_barrage\"], \"loanedCards\": [], " +
                                    "\"specialRules\": [], \"status\": \"MAKE_LATER\"";

        private static MissionDef Escort() => MissionDef.ListFromJson("{\"missions\": [{\"id\": \"p31esc\", \"map\": \"field\", \"goal\": \"Escort\", " +
            "\"enemyAi\": \"none\", \"timeLimit\": 5000, \"convoyCount\": 1, \"convoyNeeded\": 1, \"convoy\": {\"def\": \"behemoth\", \"x\": -60, \"z\": -60, " +
            "\"heading\": 45, \"route\": [-20, -20, 20, 20, 60, 60]}, \"fixedDeck\": {" + Deck + ", \"placedAllies\": [{\"def\": \"behemoth\", " +
            "\"x\": -60, \"z\": -60, \"heading\": 45, \"convoy\": true, \"lossIfDestroyed\": true}]}}]}")[0];

        [Test]
        public void TheConvoyBehemothHoldsWhileTheOrderIsDefend()
        {
            var world = Field();
            var mode = new MissionMode(Escort(), new SideSetup(), new SideSetup());
            var defend = true;
            mode.PlayerDefends = () => defend;
            mode.Setup(world);
            // An escort beside it (the convoy waits for one) that moves along with it.
            var escort = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-56f, -60f), 0f);
            escort.Invulnerable = true;
            Run(world, mode, 2f);
            var behemoth = world.Vehicles.First(v => v.IsAlive && v.Def.Id == "behemoth" && v.Team == 0);
            Assert.IsTrue(behemoth.Scripted, "the escort rules drive it, not a commander");
            Assert.IsEmpty(mode.PlacedAllies, "the convoy ally is not spawned twice");
            var start = behemoth.Position;
            Run(world, mode, 8f);
            Assert.Less(Vector2.Distance(start, behemoth.Position), 2f, "it holds on Defend");
            defend = false;
            Run(world, mode, 6f);
            Assert.Greater(Vector2.Distance(start, behemoth.Position), 2f, "it drives on when the order is Attack");
        }

        private static MissionDef Placed(bool loss) => MissionDef.ListFromJson("{\"missions\": [{\"id\": \"p31placed\", \"map\": \"field\", " +
            "\"goal\": \"Survive\", \"surviveSeconds\": 5000, \"enemyAi\": \"none\", \"fixedDeck\": {" + Deck + ", \"placedAllies\": [{\"def\": \"mara_behemoth\", " +
            "\"fallback\": \"heavy_tank\", \"x\": -80, \"z\": -80, \"heading\": 45, \"name\": \"behemoth_mara\", \"lossIfDestroyed\": " + (loss ? "true" : "false") + "}]}}]}")[0];

        [Test]
        public void APlacedAllyStandsOnOurSideUnderTheAlliedAi()
        {
            var world = Field();
            var mode = new MissionMode(Placed(false), new SideSetup(), new SideSetup());
            mode.Setup(world);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-100f, -100f), 0f).Invulnerable = true;
            var id = mode.PlacedAllies.Single();
            Assert.IsTrue(world.TryGetVehicle(id, out var ally));
            Assert.AreEqual(0, ally.Team);
            Assert.IsTrue(ally.Ally, "the allied AI drives it, the player's commander does not");
            Assert.IsFalse(ally.Scripted);
            // The allied AI (as the session makes it) takes it towards its objective.
            var ai = new MachineBrigade.Sim.AI.TacticalAi(0, 1, 11) { Allies = true, Objective = _ => new Vector2(0f, 0f) };
            var before = Vector2.Distance(ally.Position, Vector2.Zero);
            for (var t = 0f; t < 20f; t += Dt)
            {
                mode.Tick(world, Dt);
                ai.Tick(world, Dt);
                world.Step(Dt);
                world.ClearEvents();
            }
            Assert.Less(Vector2.Distance(ally.Position, Vector2.Zero), before - 5f, "it went where the allied AI sent it");
            Assert.IsFalse(world.IsOver);
        }

        [Test]
        public void LosingAPlacedAllyThatMustLiveLosesTheMission()
        {
            var world = Field();
            var mode = new MissionMode(Placed(true), new SideSetup(), new SideSetup());
            mode.Setup(world);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-100f, -100f), 0f).Invulnerable = true;
            Run(world, mode, 1f);
            Assert.IsNull(mode.Result);
            Assert.IsTrue(world.TryGetVehicle(mode.PlacedAllies.Single(), out var ally));
            ally.Hp = 0f;
            Run(world, mode, 1f);
            Assert.IsNotNull(mode.Result, "the mission ended");
            Assert.AreEqual(1, mode.Result.Value.WinningTeam, "lost");
        }
    }
}
