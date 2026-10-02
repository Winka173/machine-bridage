using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 32 L7 (DECISIONS "Prompt 32 L3 / L7 / L9"): Showdown. The match rules in the prompt 30 schema (and the mode's
    /// own fields), the eligible maps (300 x 300 symmetric only), the AI profile (data only), the anti-snipe until the outer
    /// defence is breached, the escalation at minutes 6 and 10, the HQ lead at the limit, sudden death and the draw, the
    /// catch-up as income only, the menu entry and its words. Short clocks are set in code so the tests stay quick. Written
    /// for the lead to run (agents do not run tests).
    /// </summary>
    public class ShowdownP32Tests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        [Test]
        public void TheMatchRulesFollowThePrompt30Schema()
        {
            var r = Catalog.MatchRules.For("showdown");
            Assert.IsNotNull(r);
            foreach (var field in new[] { "winCondition", "loseCondition", "timeLimit", "overtimeRule", "drawRule", "scoreRule", "catchUpPolicy", "antiSnipeRule", "breachRule" })
                Assert.IsTrue(r.Text.ContainsKey(field) && r.Text[field].Length > 0, field);
            Assert.AreEqual(720f, r.Get("timeLimit", 0f));
            Assert.AreEqual(0.25f, r.Get("antiSnipeShare", 0f), 1e-4f);
            Assert.AreEqual(60f, r.Get("antiSnipeRange", 0f));
            Assert.AreEqual(360f, r.Get("escalationAt", 0f));
            Assert.AreEqual(1.5f, r.Get("escalationIncome", 0f), 1e-4f);
            Assert.AreEqual(600f, r.Get("rebuildCutoff", 0f));
            Assert.AreEqual(0.05f, r.Get("overtimeLead", 0f), 1e-4f);
            Assert.AreEqual(90f, r.Get("suddenDeath", 0f));
            Assert.AreEqual(2f, r.Get("suddenDeathIncome", 0f), 1e-4f);
            Assert.AreEqual(0.25f, r.Get("catchUpMax", 0f), 1e-4f);
        }

        [Test]
        public void OnlySymmetric300MetreBattlefieldsAreEligible()
        {
            var maps = ShowdownSession.Eligible(Catalog);
            Assert.Greater(maps.Count, 10);
            foreach (var id in maps)
            {
                var map = GameContent.LoadMap(id + "_conquest");
                Assert.AreEqual(300f, map.Size, id);
                Assert.AreEqual(300f, map.Max.Y - map.Min.Y, 0.01f, id + " is no 300 x 480 battlefield");
                Assert.AreEqual(2, map.Bases.Count, id + " has both camps");
            }
            // The audit's RED maps (Docs/checks/map_audit.md) are out.
            foreach (var red in new[] { "borderbridge", "emberridge", "hydrodam" }) CollectionAssert.DoesNotContain(maps, red);
            Assert.AreEqual(maps[0] + "_conquest", ModeSession.MapFile(GameModeKind.Showdown, "hydrodam"), "an ineligible pick plays the first eligible map");
            Assert.AreEqual("ashfield_conquest", ModeSession.MapFile(GameModeKind.Showdown, "ashfield"));
        }

        [Test]
        public void TheAiProfileIsData()
        {
            var p = Catalog.AiModes.For("Showdown", null);
            Assert.AreEqual("showdown", p.Id);
            Assert.IsTrue(p.Has(AiController.Commander));
            Assert.AreEqual(StallPolicy.Both, p.Stall);
            Assert.IsTrue(p.SpendPressure);
            Assert.IsTrue(p.AdvancePressure);
            Assert.That(p.ObjectivePolicy, Does.Contain("(1)"));
            Assert.Greater(p.WallBreachCost, 0f);
            Assert.AreEqual(BaseRole.Target, Catalog.Base.RoleFor("Showdown"));
            Assert.IsTrue(Catalog.Opening.AppliesTo("Showdown"));
            Assert.IsTrue(Catalog.Opening.EnemyAppliesTo("Showdown"));
        }

        private static ShowdownMode Match(out SimWorld world, ShowdownRules rules = null, WallType walls = WallType.Hesco)
        {
            world = new SimWorld(Catalog, GameContent.LoadMap("ashfield_conquest"), 5) { ModeTag = "Showdown" };
            var loadout = BaseLoadout.ForAi(Catalog, "Normal", "default", 2, level: 3);
            loadout.Walls = new System.Collections.Generic.List<WallType> { walls, walls };
            rules ??= new ShowdownRules();
            rules.Bases = new BaseSetup().Set(0, loadout, BaseRole.Target).Set(1, loadout.Clone(), BaseRole.Target);
            var mode = new ShowdownMode(rules);
            mode.Setup(world);
            return mode;
        }

        private static Vehicle Hq(SimWorld world, int team)
        {
            Assert.IsTrue(world.TryGetVehicle(world.Bases.Of(team).Hq, out var hq));
            return hq;
        }

        [Test]
        public void BothHqsCanFallAndTheRulesAreSetUp()
        {
            var mode = Match(out var world);
            Assert.IsFalse(Hq(world, 0).Invulnerable);
            Assert.IsFalse(Hq(world, 1).Invulnerable);
            Assert.AreEqual(600.0, world.Bases.RebuildUntil);
            Assert.IsTrue(world.CatchUp);
            Assert.IsTrue(world.CatchUpIncomeOnly, "catch-up income only, no kill pay by the odds");
            Assert.AreEqual(0.25f, world.CatchUpMax, 1e-4f);
            Assert.IsNull(world.Economy.Underdog, "no free reinforcement");
            Assert.AreEqual(2, mode.Points.Count);
            world.Damage.Apply(Hq(world, 1), 1e8f, DamageType.HighExplosive);
            mode.Tick(world, Dt);
            Assert.AreEqual(0, mode.Result.Value.WinningTeam);
        }

        [Test]
        public void TheHqTakesAQuarterFromAfarUntilItsBaseIsBreached()
        {
            var mode = Match(out var world, walls: WallType.None);
            var hq = Hq(world, 1);
            var gun = world.SpawnVehicle("artillery", 0, hq.Position + new Vector2(0f, -100f), 0f);
            var near = world.SpawnVehicle("main_battle_tank", 0, hq.Position + new Vector2(0f, -30f), 0f);
            var far = new HitInfo(gun, 0, gun.Weapon, gun.Position, HitKind.Direct, true);
            var close = new HitInfo(near, 0, near.Weapon, near.Position, HitKind.Direct, false);
            Assert.AreEqual(250f, mode.HqDamage(hq, far, 1000f), 1e-3f, "artillery from 100 m: 25 %");
            Assert.AreEqual(1000f, mode.HqDamage(hq, close, 1000f), 1e-3f, "direct fire from 30 m: full");
            // An enemy ground vehicle inside the base breaches it.
            mode.Tick(world, Dt);
            Assert.IsTrue(mode.Breached(1), "the tank 30 m from the HQ is inside the base");
            Assert.AreEqual(1000f, mode.HqDamage(hq, far, 1000f), 1e-3f, "breached: full damage from afar");
        }

        [Test]
        public void ARubbleSegmentOfTheOuterLineThatOpensARouteBreachesTheBase()
        {
            var mode = Match(out var world);
            var outer = world.Walls.LinesOf(1).OrderBy(l => l.Ring).First();
            Assert.AreEqual(1, outer.Ring);
            mode.Tick(world, Dt);
            Assert.IsFalse(mode.Breached(1));
            var seg = outer.Segments.First(s => !s.Def.Extra);
            world.TryGetVehicle(seg.Entity, out var wall);
            world.Damage.Apply(wall, 1e7f, DamageType.HighExplosive);
            world.Step(Dt);
            Assert.IsTrue(world.Walls.RubbleRoute(1), "the rubble opens a NavGrid route through the line");
            for (var i = 0; i < 12; i++)
            {
                mode.Tick(world, Dt);
                world.Step(Dt);
            }
            Assert.IsTrue(mode.Breached(1));
        }

        [Test]
        public void MinuteSixRaisesIncomeAndStopsTheRelays()
        {
            var mode = Match(out var world, new ShowdownRules { EscalationAt = 1f });
            world.Economy.TryGet(0, out var e);
            var before = e.IncomeScale;
            for (var i = 0; i < 30; i++)
            {
                mode.Tick(world, Dt);
                world.Step(Dt);
            }
            Assert.AreEqual(before * 1.5f, e.IncomeScale, 1e-4f);
            Assert.IsTrue(world.RelaysOff);
        }

        [Test]
        public void AFivePointLeadWinsAtTheLimit()
        {
            var mode = Match(out var world, new ShowdownRules { TimeLimit = 0.5f, EscalationAt = 999f });
            var hq = Hq(world, 1);
            hq.Hp = hq.MaxHp * 0.94f;
            for (var i = 0; i < 20 && mode.Result == null; i++)
            {
                mode.Tick(world, Dt);
                world.Step(Dt);
            }
            Assert.AreEqual(0, mode.Result.Value.WinningTeam);
        }

        [Test]
        public void UnderFivePointsGoesToSuddenDeathThenTheDamageThenADraw()
        {
            var mode = Match(out var world, new ShowdownRules { TimeLimit = 0.5f, SuddenDeath = 1f, EscalationAt = 999f });
            Hq(world, 1).Hp = Hq(world, 1).MaxHp * 0.97f;
            for (var i = 0; i < 12; i++)
            {
                mode.Tick(world, Dt);
                world.Step(Dt);
            }
            Assert.AreEqual(ShowdownPhase.SuddenDeath, mode.Phase);
            Assert.IsNull(mode.Result);
            // In sudden death no anti-snipe, and the damage to the enemy HQ is counted.
            var hq = Hq(world, 1);
            var gun = world.SpawnVehicle("artillery", 0, hq.Position + new Vector2(0f, -100f), 0f);
            Assert.AreEqual(500f, mode.HqDamage(hq, new HitInfo(gun, 0, gun.Weapon, gun.Position, HitKind.Direct, true), 500f), 1e-3f);
            Assert.Greater(mode.SuddenDeathDamage(0), 0f);
            for (var i = 0; i < 40 && mode.Result == null; i++)
            {
                mode.Tick(world, Dt);
                world.Step(Dt);
            }
            Assert.AreEqual(0, mode.Result.Value.WinningTeam, "more damage to the enemy HQ in sudden death wins");

            var level = Match(out var w2, new ShowdownRules { TimeLimit = 0.5f, SuddenDeath = 1f, EscalationAt = 999f });
            for (var i = 0; i < 60 && level.Result == null; i++)
            {
                level.Tick(w2, Dt);
                w2.Step(Dt);
            }
            Assert.IsTrue(level.Result.Value.IsDraw, "level after sudden death: a draw");
        }

        [Test]
        public void TheModeIsInTheMenuInBothLanguages()
        {
            CollectionAssert.Contains(MenuScreen.BattleModes.ToList(), GameModeKind.Showdown);
            foreach (var key in new[] { "mode.showdown", "mode.showdownSub", "mode.showdown.kicker", "mode.showdown.sub", "mode.showdown.toast", "stat.hq" })
            {
                Assert.IsTrue(BaseText.Table.TryGetValue(key, out var text), key);
                Assert.IsNotEmpty(text.en, key);
                Assert.IsNotEmpty(text.vi, key);
            }
            Assert.AreEqual("Đối công", BaseText.Table["mode.showdown"].vi);
        }
    }
}
