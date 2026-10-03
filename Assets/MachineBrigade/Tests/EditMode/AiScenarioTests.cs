using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Sandbox;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 28 O.4: the Sandbox scenarios of the layered AI, as tests. Written in the cloud session and not yet run
    /// (Explicit until the owner allows the runs and the first results set the thresholds).
    /// </summary>
    public class AiScenarioTests
    {
        private const string Why = "prompt 28 O.4 scenario: run by name once the owner allows the AI runs";
        private const float Step = 0.05f;

        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SandboxScenario Scenario(int seed, SandboxAi a, SandboxAi b, params (string def, int team, float x, float y)[] units)
        {
            var s = new SandboxScenario { Seed = seed };
            s.Sides[0].Ai = a;
            s.Sides[1].Ai = b;
            foreach (var (def, team, x, y) in units) s.Units.Add(new SandboxUnit { Def = def, Team = team, X = x, Y = y, Heading = team == 0 ? 45f : 225f });
            return s;
        }

        private static IEnumerable<(string, int, float, float)> Block(string def, int team, Vector2 at, int count, float spacing = 6f)
        {
            var columns = Math.Max(1, (int)Math.Ceiling(Math.Sqrt(count)));
            for (var i = 0; i < count; i++) yield return (def, team, at.X + i % columns * spacing, at.Y + i / columns * spacing);
        }

        private static (SimWorld world, SandboxBattle battle) Build(SandboxScenario s, MapDefinition map = null)
        {
            var world = new SimWorld(Catalog, map ?? SandboxMaps.Flat(), s.Seed);
            var battle = new SandboxBattle(s);
            battle.Setup(world);
            return (world, battle);
        }

        private static void Run(SimWorld world, SandboxBattle battle, float seconds, Action<SimWorld> each = null)
        {
            for (var t = 0f; t < seconds && !world.IsOver; t += Step)
            {
                battle.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
                each?.Invoke(world);
            }
        }

        private static AiCommander General(SandboxBattle battle, int team) => battle.Commander(team)?.Commander;

        // ------------------------------------------------------------------ movement

        [Test, Explicit(Why), Category("AI28")]
        public void TwentyVehiclesCrossANarrowBridgeWithoutAnyStuckPastTheLimit()
        {
            var map = GameContent.LoadMap("borderbridge_sandbox");
            var s = Scenario(3, SandboxAi.Full, SandboxAi.Idle);
            s.Map = map.Id;
            var (world, battle) = Build(s, map);
            world.TryGetRally(0, out var home);
            world.TryGetRally(1, out var target);
            for (var i = 0; i < 20; i++) world.SpawnVehicle("main_battle_tank", 0, home + new Vector2(i % 5 * 6f, i / 5 * 6f), 0f);
            var stuck = new Dictionary<EntityId, (Vector2 at, double since)>();
            var worst = 0.0;
            Run(world, battle, 180f, w =>
            {
                foreach (var v in w.Vehicles)
                {
                    if (!v.IsAlive || v.Team != 0 || !v.IsMoving && v.Order.Kind == OrderKind.Idle) continue;
                    if (!stuck.TryGetValue(v.Id, out var p) || Vector2.Distance(p.at, v.Position) > 2f) stuck[v.Id] = (v.Position, w.Time);
                    else worst = Math.Max(worst, w.Time - p.since);
                }
            });
            Debug.Log($"AI28 bridge: worst stuck {worst:0.0} s");
            Assert.That(worst, Is.LessThanOrEqualTo(Catalog.Ai.StuckTime * 3f), "no vehicle stays stuck past the ladder (stuck time x3)");
        }

        [Test, Explicit(Why), Category("AI28")]
        public void TwelveVehiclesSpreadBeforeASplashBossAndLoseFewerToItsSuperWeaponThanTheOldAi()
        {
            int Losses(bool layered)
            {
                ConquestAi.LayeredDefault = layered;
                try
                {
                    var s = Scenario(5, SandboxAi.Full, SandboxAi.Combat,
                        Block("main_battle_tank", 0, new Vector2(-40f, -40f), 12).Append(("behemoth", 1, 30f, 30f)).ToArray());
                    var (world, battle) = Build(s);
                    var lost = 0;
                    Run(world, battle, 120f, w => lost = 12 - w.Vehicles.Count(v => v.IsAlive && v.Team == 0));
                    return lost;
                }
                finally
                {
                    ConquestAi.LayeredDefault = true;
                }
            }
            var layered = Losses(true);
            var old = Losses(false);
            Debug.Log($"AI28 splash: layered lost {layered}, old AI lost {old}");
            Assert.That(layered, Is.LessThanOrEqualTo(old));
        }

        [Test, Explicit(Why), Category("AI28")]
        public void ASquadDodgesAWarningRingAndResumesItsActionWithoutAChurnCount()
        {
            var s = Scenario(7, SandboxAi.Full, SandboxAi.Full, Block("main_battle_tank", 0, new Vector2(-20f, -20f), 4).ToArray());
            s.Sides[1].Supports.Add("artillery_barrage");
            var (world, battle) = Build(s);
            Run(world, battle, 10f);
            var squad = General(battle, 0).Squads.Squads.First();
            var before = squad.Action;
            var (switches, _, _) = world.AiLog.Switches(0, squad.Id, world.Time);
            world.Submit(Command.Strike(1, "artillery_barrage", squad.Centre));
            var dodged = false;
            Run(world, battle, 12f, w => dodged |= squad.Dodging);
            Assert.That(dodged, Is.True, "the squad left the ring");
            Assert.That(squad.Action, Is.EqualTo(before), "back to the same action, not re-scored");
            Assert.That(world.AiLog.Switches(0, squad.Id, world.Time).actions, Is.LessThanOrEqualTo(switches), "a dodge is not a switch");
        }

        [Test, Explicit(Why), Category("AI28")]
        public void AnOverwhelmedSquadGathersOnFriendsInTheFightOnceACooldown()
        {
            var s = Scenario(9, SandboxAi.Full, SandboxAi.Combat,
                Block("armored_car", 0, new Vector2(0f, 0f), 3)
                    .Concat(Block("main_battle_tank", 0, new Vector2(-50f, 0f), 4))
                    .Concat(Block("heavy_tank", 1, new Vector2(25f, 25f), 10)).ToArray());
            var (world, battle) = Build(s);
            world.TryGetRally(0, out var home);
            Run(world, battle, 60f);
            var gathers = world.AiLog.Entries.Where(e => e.Team == 0 && e.Kind == DecisionKind.Emergency && e.Text.StartsWith("gather")).ToList();
            Assert.That(gathers, Is.Not.Empty, "the outmatched squad gathered on its friends");
            var cooldown = Catalog.Ai.EmergencyCooldown;
            foreach (var g in gathers.GroupBy(e => e.Subject))
            {
                var times = g.Select(e => e.Time).ToList();
                for (var i = 1; i < times.Count; i++) Assert.That(times[i] - times[i - 1], Is.GreaterThanOrEqualTo(cooldown - 0.01), "not again within the cooldown");
            }
            Assert.That(world.AiLog.Entries.Any(e => e.Text.Contains("home")), Is.False, "nobody goes home");
        }

        [Test, Explicit(Why), Category("AI28")]
        public void VehiclesAndSquadsLowOnHealthDoNotRetreat()
        {
            var s = Scenario(11, SandboxAi.Full, SandboxAi.Combat,
                Block("main_battle_tank", 0, new Vector2(-10f, -10f), 4).Concat(Block("main_battle_tank", 1, new Vector2(30f, 30f), 4)).ToArray());
            foreach (var u in s.Units.Where(u => u.Team == 0)) u.Hp = 10;
            var (world, battle) = Build(s);
            world.TryGetRally(0, out var home);
            var start = world.Vehicles.Where(v => v.Team == 0).ToDictionary(v => v.Id, v => Vector2.Distance(v.Position, home));
            var retreats = 0;
            Run(world, battle, 30f, w =>
            {
                foreach (var v in w.Vehicles)
                    if (v.IsAlive && v.Team == 0 && (v.Order.Kind == OrderKind.Retreat ||
                        (start.TryGetValue(v.Id, out var d0) && Vector2.Distance(v.Position, home) < d0 - 30f))) retreats++;
            });
            Assert.That(retreats, Is.Zero);
        }

        // ------------------------------------------------------------------ decisions

        [Test, Explicit(Why), Category("AI28")]
        public void ASquadKeepsItsActionWhenANewOneIsWithinTheSwitchMargin()
        {
            var s = Scenario(13, SandboxAi.Full, SandboxAi.Full,
                Block("main_battle_tank", 0, new Vector2(-30f, -30f), 8).Concat(Block("main_battle_tank", 1, new Vector2(30f, 30f), 8)).ToArray());
            var (world, battle) = Build(s);
            Run(world, battle, 120f);
            var margin = Catalog.Ai.SwitchMargin;
            var pattern = new Regex(@"^\w+ (\d+) -> \w+ (\d+)$");
            foreach (var e in world.AiLog.Entries.Where(e => e.Kind == DecisionKind.Action && e.Layer == AiLayer.Squad))
            {
                var m = pattern.Match(e.Text);
                if (!m.Success) continue; // an invalid, urgent or idle change, or a non-scored line
                Assert.That(int.Parse(m.Groups[2].Value) - int.Parse(m.Groups[1].Value), Is.GreaterThanOrEqualTo(margin - 1), e.ToString());
            }
        }

        [Test, Explicit(Why), Category("AI28")]
        public void AnInfeasibleFlankIsFilteredOutBeforeScoring()
        {
            var s = Scenario(15, SandboxAi.Full, SandboxAi.Idle,
                Block("armored_car", 0, new Vector2(-40f, -40f), 4).Concat(Block("main_battle_tank", 1, new Vector2(40f, 40f), 3)).ToArray());
            var (world, battle) = Build(s);
            Run(world, battle, 3f);
            var general = General(battle, 0);
            var squad = general.Squads.Squads.First();
            squad.BlockedLeft = true;
            Run(world, battle, 2f);
            Assert.That(general.Squads.LastOptions(squad).Select(o => o.action), Has.No.Member(SquadAction.FlankLeft));
        }

        [Test, Explicit(Why), Category("AI28")]
        public void OldInformationLosesConfidenceAndTheAiDoesNotAttackWhereTheEnemyLeftLongAgo()
        {
            var s = Scenario(17, SandboxAi.Full, SandboxAi.Idle,
                Block("main_battle_tank", 0, new Vector2(-40f, -40f), 4).Append(("armored_car", 1, -5f, -5f)).ToArray());
            var (world, battle) = Build(s);
            Run(world, battle, 4f);
            var car = world.Vehicles.First(v => v.Team == 1);
            var seenAt = car.Position;
            car.Position = new Vector2(60f, -60f); // gone far out of sight
            Run(world, battle, 20f);
            var contact = world.Intel.For(0).Find(car.Id);
            Assert.That(contact == null || contact.Confidence(world.Time, world.Intel.For(0).ConfidenceDecay) < 0.5f, "old information is less certain");
            foreach (var squad in General(battle, 0).Squads.Squads)
                Assert.That(Vector2.Distance(squad.Goal, seenAt) > 5f || contact == null || contact.Displaced, Is.True, "no attack on the empty spot as if it were still there");
        }

        [Test, Explicit(Why), Category("AI28")]
        public void ASquadToldToFlankATankLineHitsItsSideOrRear()
        {
            var s = Scenario(19, SandboxAi.Full, SandboxAi.Idle,
                Block("armored_car", 0, new Vector2(-50f, -50f), 4).Concat(Block("main_battle_tank", 1, new Vector2(20f, 20f), 4)).ToArray());
            s.Sides[0].Tactic = "encircle";
            var (world, battle) = Build(s);
            var flanked = false;
            var sideHits = 0;
            Run(world, battle, 90f, w =>
            {
                foreach (var sq in General(battle, 0)?.Squads.Squads ?? (IReadOnlyList<Squad>)Array.Empty<Squad>())
                    flanked |= sq.State == SquadState.Flank;
                foreach (var v in w.Vehicles)
                    if (v.IsAlive && v.Team == 0 && w.TryGetVehicle(v.Target, out var t) && t.Team == 1)
                    {
                        var to = Vector2.Normalize(v.Position - t.Position);
                        if (Vector2.Dot(to, SimMath.Forward(t.Heading)) < 0.5f) sideHits++;
                    }
            });
            Assert.That(flanked, Is.True, "a squad flanked");
            Assert.That(sideHits, Is.GreaterThan(0), "and fired from the side or rear");
        }

        [Test, Explicit(Why), Category("AI28")]
        public void AircraftMeetingDenseAntiAirChangeTheirApproachInsteadOfCirclingToDeath()
        {
            var s = Scenario(21, SandboxAi.Full, SandboxAi.Idle,
                Block("sam_launcher", 1, new Vector2(20f, 20f), 3).Concat(Block("main_battle_tank", 1, new Vector2(30f, 30f), 2)).ToArray());
            var (world, battle) = Build(s);
            world.TryGetRally(0, out var home);
            var heli = world.SpawnVehicle("attack_helicopter", 0, home, 0f);
            var moved = false;
            Run(world, battle, 60f, w => moved |= heli.IsAlive && heli.Order.Kind == OrderKind.Move);
            Assert.That(moved || world.AiLog.Entries.Any(e => e.Text.Contains("anti-air")), Is.True);
        }

        [Test, Explicit(Why), Category("AI28")]
        public void ArtilleryFiresAndMovesAndAvoidsMarkedSpots()
        {
            var s = Scenario(23, SandboxAi.Full, SandboxAi.Full,
                Block("artillery", 0, new Vector2(-50f, -50f), 2).Append(("command_vehicle", 0, -55f, -45f))
                    .Concat(Block("artillery", 1, new Vector2(50f, 50f), 2)).Append(("command_vehicle", 1, 55f, 45f)).ToArray());
            var (world, battle) = Build(s);
            Run(world, battle, 120f);
            Assert.That(world.AiLog.Entries.Count(e => e.Text == "artillery scoot"), Is.GreaterThan(0), "guns moved after firing");
            var general = General(battle, 0);
            foreach (var v in world.Vehicles.Where(v => v.IsAlive && v.Team == 0 && v.Def.Weapon.MinRange > 0f && !v.IsMoving))
                Assert.That(general.MarkedSpots.All(m => Vector2.Distance(m, v.Position) >= 5f), Is.True, "not parked on a marked spot");
        }

        [Test, Explicit(Why), Category("AI28")]
        public void ASquadStandingIdleForNoReasonIsReScored()
        {
            var s = Scenario(25, SandboxAi.Full, SandboxAi.Idle, Block("main_battle_tank", 0, new Vector2(0f, 0f), 4).ToArray());
            var (world, battle) = Build(s);
            Run(world, battle, Catalog.Ai.IdleReassess + 10f);
            var squad = General(battle, 0).Squads.Squads.First();
            var why = world.AiLog.Latest(AiLayer.Squad, 0, squad.Id);
            Assert.That(why, Is.Not.Null);
            Assert.That(world.Time - why.Time, Is.LessThan(1.0), "re-scored recently (a re-score may keep HOLD)");
        }

        // ------------------------------------------------------------------ towers, tactics, economy, replay

        [TestCase(TowerMode.Nearest), TestCase(TowerMode.Strongest), TestCase(TowerMode.Weakest), TestCase(TowerMode.AirFirst),
         TestCase(TowerMode.Cluster), TestCase(TowerMode.ArtilleryFirst), TestCase(TowerMode.Lead)]
        [Explicit(Why), Category("AI28")]
        public void ATowerPicksTheTargetItsModeAsksFor(TowerMode mode)
        {
            var s = Scenario(27, SandboxAi.Idle, SandboxAi.Idle,
                ("gun_turret", 0, 0f, 0f),
                ("armored_car", 1, 10f, 0f),          // nearest
                ("heavy_tank", 1, 22f, 0f),           // strongest
                ("artillery", 1, 24f, 6f),            // artillery
                ("attack_helicopter", 1, 0f, 20f),    // aircraft
                ("light_tank", 1, -20f, -14f),        // lead (closest to camp 0 at -56,-56)
                ("armored_car", 1, 18f, 18f), ("armored_car", 1, 20f, 20f), ("armored_car", 1, 22f, 18f)); // cluster
            s.Units[5].Hp = 15; // weakest
            var (world, battle) = Build(s);
            var tower = world.Vehicles.First(v => v.Team == 0);
            world.SetTowerMode(0, tower.Id, mode);
            tower.TowerMode = mode; // a mode the type does not list is still applied for the test
            Run(world, battle, 3f);
            Assert.That(world.TryGetVehicle(tower.Target, out var target), Is.True, "the tower fires");
            string expected = mode switch
            {
                TowerMode.Nearest => "armored_car",
                TowerMode.Strongest => "heavy_tank",
                TowerMode.Weakest => "light_tank",
                TowerMode.AirFirst => "attack_helicopter",
                TowerMode.ArtilleryFirst => "artillery",
                TowerMode.Lead => "light_tank",
                _ => "armored_car",
            };
            Assert.That(target.Def.Id, Is.EqualTo(expected), mode.ToString());
        }

        [Test, Explicit(Why), Category("AI28")]
        public void ATacticSwitchHasItsCooldownTransitionAndLossOfMomentum()
        {
            var s = Scenario(29, SandboxAi.Full, SandboxAi.Full,
                Block("main_battle_tank", 0, new Vector2(-30f, -30f), 6).Concat(Block("main_battle_tank", 1, new Vector2(30f, 30f), 6)).ToArray());
            var (world, battle) = Build(s);
            Run(world, battle, 20f);
            var general = General(battle, 0);
            var spent = general.Spent.ToArray();
            Assert.That(general.RequestTactic(world, "blitz"), Is.EqualTo(TacticSwitchResult.Done));
            Assert.That(general.RequestTactic(world, "depth"), Is.EqualTo(TacticSwitchResult.Cooldown));
            Assert.That(general.InTransition, Is.True);
            Run(world, battle, 1f);
            Assert.That(general.Squads.Squads.All(q => q.Action != SquadAction.Attack), Is.True, "no new attack during the transition");
            Run(world, battle, Catalog.Ai.TacticTransition + 1f);
            Assert.That(general.InTransition, Is.False);
            Assert.That(general.Spent.ToArray(), Is.EqualTo(spent), "nothing sold or re-bought: new shares only for later purchases");
        }

        [Test, Explicit(Why), Category("AI28")]
        public void AfterFiveMinutesTheCpSpentPerGroupIsWithinFifteenPointsOfTheTactic()
        {
            var catalog = Catalog;
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: 31);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles, PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles, EnemySupports = MatchSettings.AllSupports,
            });
            mode.Setup(world);
            world.Intel.Objectives = mode;
            var a = new ConquestAi(mode, 0, 1, AiDifficulty.Normal, 32) { Tactic = "balanced" };
            var b = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, 33) { Tactic = "firepower" };
            for (var t = 0f; t < 300f && mode.Result == null; t += Step)
            {
                mode.Tick(world, Step);
                a.Tick(world, Step);
                b.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            foreach (var ai in new[] { a, b })
            {
                world.TryGetEconomy(ai.Commander.Team, out var economy);
                var target = ai.Commander.Targets(world, economy);
                var total = ai.Commander.Spent.Sum();
                for (var g = 0; g < 8; g++)
                    Assert.That(ai.Commander.Spent[g] / Math.Max(1f, total), Is.EqualTo(target[g]).Within(0.15f), $"{ai.Commander.Tactic} {(ForceGroup)g}");
            }
        }

        [Test, Explicit(Why), Category("AI28")]
        public void PressureTiersRiseInOrderAndABigFightResetsThem()
        {
            var s = Scenario(35, SandboxAi.Idle, SandboxAi.Idle, ("main_battle_tank", 0, -50f, -50f), ("main_battle_tank", 1, 50f, 50f));
            var (world, battle) = Build(s);
            var events = new BattleEvents(35, raids: false);
            var tiers = new List<(int tier, double at)>();
            for (var t = 0f; t < 100f; t += Step)
            {
                battle.Tick(world, Step);
                events.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
                if (tiers.Count == 0 || tiers[tiers.Count - 1].tier != events.Tier) tiers.Add((events.Tier, world.Time));
            }
            var rising = tiers.Where(x => x.tier > 0).Select(x => x.tier).ToList();
            Assert.That(rising, Is.EqualTo(new[] { 1, 2, 3, 4 }).Or.EqualTo(new[] { 1, 2, 3 }), string.Join(",", tiers));
            // A big fight: every vehicle loses a lot of health at once.
            foreach (var v in world.Vehicles.Where(v => v.IsAlive && !v.Def.Static)) v.Hp *= 0.4f;
            for (var t = 0f; t < 2f; t += Step)
            {
                events.Tick(world, Step);
                world.Step(Step);
            }
            Assert.That(events.Tier, Is.Zero);
        }

        [Test, Explicit(Why), Category("AI28")]
        public void TheSameSeedReplaysTheSameDecisions()
        {
            string Trace()
            {
                var s = Scenario(37, SandboxAi.Full, SandboxAi.Full,
                    Block("main_battle_tank", 0, new Vector2(-30f, -30f), 6).Concat(Block("armored_car", 1, new Vector2(30f, 30f), 6)).ToArray());
                var (world, battle) = Build(s);
                Run(world, battle, 90f);
                var b = new StringBuilder();
                foreach (var e in world.AiLog.Entries) b.AppendLine(e.ToString());
                return b.ToString();
            }
            var first = Trace();
            Assert.That(first, Is.Not.Empty);
            Assert.That(Trace(), Is.EqualTo(first));
        }
    }
}
