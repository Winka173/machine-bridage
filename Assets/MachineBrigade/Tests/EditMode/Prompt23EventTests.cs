using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Navigation;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 23 A-D, the bare minimum: one behaviour test per kind of mission event, the difficulty table's warnings and
    /// allied share, the allied wave standing in for the underdog drop, a replay bringing the events back, every
    /// battlefield's spawn points with prompt 12's stuck probe from them (one seed), and the events' texts.
    /// </summary>
    public class Prompt23EventTests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SimWorld Field(int seed = 1) => new(Catalog, new MapDefinition("field", 300f,
            new[] { new TeamStart(0, new Vector2(-108.75f, -108.75f)), new TeamStart(1, new Vector2(108.75f, 108.75f)) },
            new List<PropPlacement>(), new List<UnitPlacement>()), seed);

        /// <summary>A mission (read as campaign.json is) playing library events, with extra mission fields.</summary>
        private static MissionDef Mission(string events, string refs, string extra = "") =>
            MissionDef.ListFromJson("{\"eventLibrary\": {\"events\": [" + events + "]}, \"missions\": [{\"id\": \"p23\", \"map\": \"field\", " +
                                    "\"goal\": \"Survive\", \"surviveSeconds\": 5000, \"enemyAi\": \"none\"" + extra + ", \"missionEvents\": [" + refs + "]}]}")[0];

        private sealed class Battle
        {
            public SimWorld World;
            public MissionMode Mode;
            public Vehicle Anchor;
            public readonly List<SimEvent> Seen = new();
            public MissionEventSystem Events => Mode.Events;
            public EventState State(int i = 0) => Events.States[i];
            public List<Vehicle> Brought(int team) => World.Vehicles.Where(v => v.IsAlive && v.Team == team && v.Reinforcement).ToList();
            public bool Logged(string moment) => Events.Log.Any(l => l.moment == moment);
        }

        private static Battle Start(MissionDef def, EventLevel level = EventLevel.Normal, int seed = 1, SideSetup enemy = null, SideSetup player = null)
        {
            var world = Field(seed);
            var mode = new MissionMode(def, player ?? new SideSetup(), enemy) { EventLevel = level };
            mode.Setup(world);
            // The player's army never falls (the mission would end), and stands in its camp, far from every spawn.
            var anchor = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-100f, -100f), 0f);
            anchor.Invulnerable = true;
            return new Battle { World = world, Mode = mode, Anchor = anchor };
        }

        private static void Run(Battle b, float seconds, Func<bool> until = null, Action each = null)
        {
            for (var t = 0f; t < seconds; t += Dt)
            {
                each?.Invoke();
                b.Mode.Tick(b.World, Dt);
                b.World.Step(Dt);
                b.Seen.AddRange(b.World.Events);
                b.World.ClearEvents();
                if (until != null && until()) return;
            }
        }

        private static IEnumerable<SimEvent> Notices(Battle b, string key) => b.Seen.Where(e => e.Kind == SimEventKind.EventNotice && e.DefId == key);

        private static IEnumerable<SimEvent> Strikes(Battle b, string support, int team) =>
            b.Seen.Where(e => e.Kind == SimEventKind.StrikeWarning && e.DefId == support && e.Team == team);

        private static Vehicle Group(Battle b, int team, Vector2 at, int count = 4, string def = "main_battle_tank")
        {
            Vehicle first = null;
            for (var i = 0; i < count; i++)
            {
                var v = b.World.SpawnVehicle(def, team, at + new Vector2(i * 4f, 0f), 0f);
                v.Invulnerable = true;
                first ??= v;
            }
            return first;
        }

        // ================================================================== C: reinforcements

        [Test]
        public void EnemyWavesComeWarnedByTheTableFromSeveralDirectionsWithTheGeneralsVehicles()
        {
            foreach (var level in new[] { EventLevel.Easy, EventLevel.Normal, EventLevel.Hard, EventLevel.VeryHard })
            {
                var d = EventRules.Default.Of(level);
                var b = Start(Mission("{\"id\": \"w\", \"kind\": \"EnemyWave\", \"trigger\": {\"at\": 5}, \"params\": {\"size\": 8}}", "\"w\"",
                    ", \"general\": \"varga\""), level, enemy: new SideSetup());
                Vehicle scout = null;
                // B.3: a player's scout parked on the wave's first point once it is warned: the wave comes in beside it instead.
                Run(b, 5f + d.Warning + 2f, each: () =>
                {
                    if (scout != null || b.State().Phase != EventPhase.Warned || level != EventLevel.Normal) return;
                    scout = b.World.SpawnVehicle("scout_jeep", 0, b.State().Arrows[0].at, 0f);
                    scout.Invulnerable = true;
                });
                var warn = Notices(b, "event.enemyWave.warn").ToList();
                Assert.AreEqual(1, warn.Count, level + ": one warning");
                Assert.AreEqual(d.Warning, warn[0].Value, 1e-3, level + ": the table's warning");
                Assert.GreaterOrEqual(warn[0].NoticeBearing, 0, level + ": the warning has a direction");
                Assert.AreEqual(LinePriority.Warning, warn[0].Priority);
                var s = b.State();
                Assert.AreEqual(d.Warning, s.HappenedAt - s.WarnedAt, 0.06, level + ": the wave comes when the warning said");
                var bearings = s.Arrows.Select(a => a.bearing).Distinct().Count();
                var available = b.Events.Spawns.Bearings(SpawnSide.Enemy).Count;
                Assert.That(bearings, Is.InRange(Math.Min(d.MinDirections, available), d.MaxDirections), level + ": directions");
                var wave = b.Brought(1);
                Assert.AreEqual((int)MathF.Round(8 * d.WaveScale), wave.Count, level + ": the wave's size");
                Assert.IsTrue(wave.All(v => v.Def.Class is UnitClass.Tank or UnitClass.Heavy or UnitClass.TankHunter), level + ": Varga sends armour");
                if (d.Elites) Assert.IsTrue(wave.Any(v => v.Def.Elite), "Very Hard brings elites");
                if (scout != null)
                    foreach (var e in b.Seen.Where(e => e.Kind == SimEventKind.VehicleSpawned && e.Team == 1))
                        Assert.Greater(Vector2.Distance(e.Position, scout.Position), EventRules.Default.NearSight - 12f, "never in the scout's close sight");
                Assert.AreEqual(0, b.World.Economy.TryGet(1, out var e1) ? e1.VehicleCount : 0, "C.4: outside the army cap");
            }
        }

        [Test]
        public void AccordWavesAreTheTablesShareOfAnEnemyWaveAndVeryHardSendsOne()
        {
            foreach (var level in new[] { EventLevel.Easy, EventLevel.Normal, EventLevel.Hard, EventLevel.VeryHard })
            {
                var share = EventRules.Default.Of(level).AllyShare;
                var b = Start(Mission("{\"id\": \"w\", \"kind\": \"EnemyWave\", \"trigger\": {\"at\": 1}, \"params\": {\"size\": 10}}, " +
                                      "{\"id\": \"a\", \"kind\": \"AllyWave\", \"trigger\": {\"at\": 30}, \"params\": {\"of\": \"w\"}}",
                    "\"w\", \"a\", {\"id\": \"a\", \"trigger\": {\"at\": 40}}"), level);
                Run(b, 50f);
                var wave = b.State(0);
                var allies = b.State(1);
                var ratio = allies.Strength / wave.Strength;
                var biggest = EventRules.Default.AccordRoster.Max(id => MissionEventSystem.Strength(Catalog.Vehicle(id)));
                Assert.AreEqual(share, ratio, biggest * 0.5f / wave.Strength + 0.01f, level + ": the allied share");
                Assert.IsNotEmpty(allies.Units, level + ": the Accord came");
                Assert.IsTrue(b.Brought(0).All(v => v.Ally && v.Accord), level + ": Accord units under the allied AI");
                Assert.AreEqual(level == EventLevel.VeryHard ? 1 : 2, b.Events.AllyWaves, level + ": allied waves");
            }
        }

        [Test]
        public void AnAlliedWaveStandsInForTheUnderdogsFreeDrop()
        {
            var def = Mission("{\"id\": \"a\", \"kind\": \"AllyWave\", \"trigger\": {\"at\": 9999}, \"params\": {\"strength\": 30}}", "\"a\"");
            var b = Start(def, enemy: new SideSetup { Vehicles = new[] { "main_battle_tank" } }, player: new SideSetup { Vehicles = new[] { "main_battle_tank" } });
            b.World.Economy.Underdog = new UnderdogRules { After = 1f, Ratio = 1.5f, MinimumArmy = 10 };
            for (var i = 0; i < 6; i++) b.World.SpawnVehicle("heavy_tank", 1, new Vector2(100f - i * 6f, 100f), 0f).Invulnerable = true;
            var before = b.World.Vehicles.Where(v => v.Team == 0).Select(v => v.Id).ToHashSet();
            Run(b, 12f);
            Assert.AreEqual(0, b.World.Economy.UnderdogTeam, "the player's side got the help");
            Assert.IsTrue(b.Logged("underdog"), "the mission's allied wave came instead");
            var arrived = b.World.Vehicles.Where(v => v.Team == 0 && !before.Contains(v.Id)).ToList();
            Assert.IsNotEmpty(arrived);
            Assert.IsTrue(arrived.All(v => v.Reinforcement), "and no free drop on top of it");
        }

        // ================================================================== D.1: fire support

        [Test]
        public void TheEnemyShellsTheBiggestGroupAfterAWarning()
        {
            var b = Start(Mission("{\"id\": \"f\", \"kind\": \"Barrage\", \"trigger\": {\"at\": 2}, \"params\": {\"salvos\": 3, \"radius\": 18}}", "\"f\""));
            Group(b, 0, new Vector2(0f, 0f));
            Run(b, 2f + 10f + 6f);
            Assert.AreEqual(10f, Notices(b, "event.barrage.warn").Single().Value, 1e-3);
            var shells = Strikes(b, "artillery_barrage", 1).ToList();
            Assert.AreEqual(3, shells.Count);
            Assert.IsTrue(shells.All(s => Vector2.Distance(s.Position, new Vector2(6f, 0f)) < 26f), "on the group");
        }

        [Test]
        public void TheEnemyAirRaidIsWarnedAndFlown()
        {
            var b = Start(Mission("{\"id\": \"r\", \"kind\": \"AirRaid\", \"trigger\": {\"at\": 2}}", "\"r\""));
            Group(b, 0, new Vector2(0f, 0f));
            Run(b, 2f + 6f + 1f);
            Assert.AreEqual(6f, Notices(b, "event.airRaid.warn").Single().Value, 1e-3, "at most 6 s of warning");
            Assert.AreEqual(1, Strikes(b, "air_raid", 1).Count());
        }

        [Test]
        public void AGunFiringFromOneSpotTooLongDrawsCounterBatteryFire()
        {
            var b = Start(Mission("{\"id\": \"c\", \"kind\": \"CounterBattery\", \"trigger\": {\"at\": 1}, \"params\": {\"still\": 20, \"lead\": 5}}", "\"c\""));
            var gun = b.World.SpawnVehicle("artillery", 0, new Vector2(-20f, -60f), 0f);
            gun.Invulnerable = true;
            Run(b, 9f, each: () =>
            {
                gun.StillSince = b.World.Time - 30.0;
                gun.LastFiredAt = b.World.Time;
            });
            var warn = Notices(b, "event.counterBattery.warn").First();
            Assert.AreEqual(5f, warn.Value, 1e-3);
            var fire = Strikes(b, "artillery_barrage", 1).ToList();
            Assert.IsNotEmpty(fire);
            Assert.Less(Vector2.Distance(fire[0].Position, gun.Position), 1f, "on the gun");
        }

        [Test]
        public void HawkCallsAnAlliedAirStrike()
        {
            var b = Start(Mission("{\"id\": \"h\", \"kind\": \"AllyAirStrike\", \"trigger\": {\"at\": 2}}", "\"h\""));
            Group(b, 1, new Vector2(40f, 40f));
            Run(b, 4f);
            Assert.AreEqual(1, Strikes(b, "airstrike", 0).Count());
            Assert.IsTrue(b.Seen.Any(e => e.Kind == SimEventKind.Radio && e.DefId == "radio.dieuhau.ev.allyAirStrike.start"));
        }

        [Test]
        public void AccordArtilleryFiresInSupport()
        {
            var b = Start(Mission("{\"id\": \"g\", \"kind\": \"AllyArtillery\", \"trigger\": {\"at\": 2}, \"params\": {\"salvos\": 3}}", "\"g\""));
            Group(b, 1, new Vector2(40f, 40f));
            Run(b, 8f);
            Assert.AreEqual(3, Strikes(b, "artillery_barrage", 0).Count());
        }

        // ================================================================== D.2: the general on the field

        [Test]
        public void TheGeneralTakesTheFieldWithTheirPassiveAndBreaksOffWhenTheStoryNeedsThem()
        {
            const string general = "{\"id\": \"g\", \"kind\": \"GeneralField\", \"trigger\": {\"at\": 1}, \"reward\": {\"cp\": 15}}";
            // An early chapter at Normal: the elite of Varga's card; the passive while on the field; the break-off at 30 %.
            var b = Start(Mission(general, "\"g\"", ", \"general\": \"varga\", \"chapter\": 2"));
            Run(b, 1f + 10f + 1f);
            var v = b.World.Vehicles.Single(x => x.General == "varga");
            Assert.AreEqual(Catalog.EliteVariant("heavy_tank"), v.Def.Id);
            Assert.AreSame(Commanders.General("varga"), b.World.CommanderOf(1), "Varga's passive");
            Assert.AreEqual(EventRules.Default.Of(EventLevel.Normal).Escorts, b.State().Others.Count, "escorts");
            v.Hp = v.MaxHp * 0.2f;
            Run(b, 1f);
            Assert.IsTrue(v.Invulnerable && b.Logged("retreat"), "breaks off");
            Run(b, 10f);
            Assert.IsFalse(v.IsAlive, "gone from the battle");
            Assert.IsNull(b.World.CommanderOf(1), "the passive goes with them");
            Assert.AreEqual(EventPhase.Done, b.State().Phase);

            // A late chapter at Hard: a mini boss of Varga's own, not the mission's boss.
            var late = Start(Mission(general, "\"g\"", ", \"general\": \"varga\", \"chapter\": 10, \"boss\": {\"def\": \"behemoth_inferno\", \"x\": 100, \"z\": 40}"),
                EventLevel.Hard);
            Run(late, 1f + 8f + 1f);
            var mini = late.World.Vehicles.Single(x => x.General == "varga");
            Assert.IsTrue(mini.Def.MiniBoss && mini.Def.General == "varga", mini.Def.Id);
            Assert.AreNotEqual("behemoth_inferno", mini.Def.Id);

            // The last chapter's operation: Varga's last battle, no break-off.
            var last = Start(Mission("{\"id\": \"g\", \"kind\": \"GeneralField\", \"trigger\": {\"at\": 1}, \"params\": {\"form\": \"elite\"}}", "\"g\"",
                ", \"general\": \"varga\", \"chapter\": 12, \"operation\": true"));
            Run(last, 12f);
            var final = last.World.Vehicles.Single(x => x.General == "varga");
            final.Hp = final.MaxHp * 0.2f;
            Run(last, 2f);
            Assert.IsFalse(final.Invulnerable || last.Logged("retreat"), "fights to the end");
        }

        // ================================================================== D.3-D.4

        [Test]
        public void SideObjectivesPayWhenDoneAndNeverLoseTheMission()
        {
            // Intercept: the files' trucks destroyed in time pay the coins.
            var b = Start(Mission("{\"id\": \"i\", \"kind\": \"SideObjective\", \"trigger\": {\"at\": 1}, \"params\": {\"type\": \"intercept\", \"count\": 2, \"seconds\": 60}, " +
                                  "\"reward\": {\"coins\": 150}}", "\"i\""));
            Run(b, 2f);
            var trucks = b.World.Vehicles.Where(v => v.Team == 1 && v.Def.Id == MissionEventSystem.Truck).ToList();
            Assert.AreEqual(2, trucks.Count);
            Assert.IsTrue(trucks.All(t => t.Scripted && t.Marked));
            Assert.AreEqual(60f, Notices(b, "event.sideObjective.intercept.start").Single().Value, 1e-3, "its clock");
            foreach (var t in trucks) t.Hp = 0f;
            Run(b, 1f);
            Assert.AreEqual(EventPhase.Done, b.State().Phase);
            Assert.IsTrue(b.Events.Earned.Any(x => x.kind == "coins" && x.amount == 150));

            // Rescue: the ring broken, the column joins the allied reinforcements.
            var r = Start(Mission("{\"id\": \"r\", \"kind\": \"SideObjective\", \"trigger\": {\"at\": 1}, \"params\": {\"type\": \"rescue\", \"count\": 2, \"size\": 3}}", "\"r\""));
            Run(r, 2f);
            var ring = r.World.Vehicles.Where(v => v.Team == 1 && v.Reinforcement).ToList();
            Assert.AreEqual(3, ring.Count);
            foreach (var v in ring) v.Hp = 0f;
            Run(r, 1f);
            var column = r.World.Vehicles.Where(v => v.Team == 0 && v.Accord).ToList();
            Assert.AreEqual(2, column.Count, "the column is the Accord's now");
            Assert.IsTrue(column.All(v => !v.Scripted));

            // Protect: the civilians lost, the objective fails and the mission goes on.
            var p = Start(Mission("{\"id\": \"p\", \"kind\": \"SideObjective\", \"trigger\": {\"at\": 1}, \"params\": {\"type\": \"protect\", \"count\": 3, \"need\": 2}}", "\"p\""));
            Run(p, 2f);
            foreach (var t in p.World.Vehicles.Where(v => v.Team == 0 && v.Def.Id == MissionEventSystem.Truck).ToList()) t.Hp = 0f;
            Run(p, 1f);
            Assert.AreEqual(EventPhase.Failed, p.State().Phase);
            Assert.IsNull(p.Mode.Result, "optional: never lost for");
        }

        [Test]
        public void ANeutralConvoysLoadGoesToWhoeverKnocksATruckOut()
        {
            var b = Start(Mission("{\"id\": \"n\", \"kind\": \"NeutralConvoy\", \"trigger\": {\"at\": 1}, \"params\": {\"count\": 2, \"cp\": 8}}", "\"n\""));
            Run(b, 2f);
            var trucks = b.World.Vehicles.Where(v => v.Team == Teams.Hostile).ToList();
            Assert.AreEqual(2, trucks.Count);
            b.World.TryGetEconomy(0, out var economy);
            economy.Cp = 0f;
            trucks[0].LastAttackerTeam = 0;
            Run(b, 0.1f);
            trucks[0].Hp = 0f;
            Run(b, 0.2f);
            Assert.AreEqual(8f, economy.Cp, 0.5f);
            Assert.IsTrue(b.Seen.Any(e => e.Kind == SimEventKind.Bounty && e.Team == 0 && e.DefId == "convoy"));
        }

        [Test]
        public void TheSideHoldingTheLootCrateTakesIt()
        {
            var b = Start(Mission("{\"id\": \"l\", \"kind\": \"LootDrop\", \"trigger\": {\"at\": 1}, \"params\": {\"cp\": 12}}", "\"l\""));
            Run(b, 1.2f);
            var crate = b.World.Crates.Single();
            b.World.SpawnVehicle("scout_jeep", 0, crate.Position, 0f).Invulnerable = true;
            b.World.TryGetEconomy(0, out var economy);
            economy.Cp = 0f;
            Run(b, 9f, () => b.State().Phase == EventPhase.Done);
            Assert.AreEqual(EventPhase.Done, b.State().Phase);
            Assert.GreaterOrEqual(economy.Cp, 12f);
            Assert.IsEmpty(b.World.Crates);
        }

        [Test]
        public void ARaidGoesForThePlayersSupplies()
        {
            var b = Start(Mission("{\"id\": \"s\", \"kind\": \"SupplyRaid\", \"trigger\": {\"at\": 1}, \"params\": {\"size\": 3}}", "\"s\""));
            var depot = b.World.SpawnVehicle("logistics_station", 0, new Vector2(-70f, -40f), 0f);
            Run(b, 1f + 10f + 1f);
            var raiders = b.Brought(1);
            Assert.AreEqual(3, raiders.Count);
            Assert.IsTrue(raiders.All(v => Vector2.Distance(v.Order.Point, depot.Position) < 16f), "for the depot");
            foreach (var v in raiders) v.Hp = 0f;
            Run(b, 1f);
            Assert.AreEqual(EventPhase.Done, b.State().Phase);
        }

        // ================================================================== D.5-D.9

        [Test]
        public void ASupplyDropRepairsAndRearmsWhatStandsUnderIt()
        {
            var b = Start(Mission("{\"id\": \"d\", \"kind\": \"SupplyDrop\", \"trigger\": {\"at\": 1}}", "\"d\""));
            var mlrs = Group(b, 0, new Vector2(-40f, -40f), 2, "mlrs");
            b.World.DebugEmpty(mlrs);
            Run(b, 6f);
            Assert.AreEqual(1, Strikes(b, "repair_drop", 0).Count());
            Assert.AreEqual(EventPhase.Done, b.State().Phase);
            Assert.AreNotEqual(0, mlrs.Weapons[0].Ammo, "rearmed");
        }

        [Test]
        public void NadiasReportShowsAHiddenEnemyForAFewSeconds()
        {
            var b = Start(Mission("{\"id\": \"n\", \"kind\": \"IntelReveal\", \"trigger\": {\"at\": 1}, \"params\": {\"seconds\": 8, \"radius\": 30}}", "\"n\""));
            var foe = Group(b, 1, new Vector2(80f, 80f), 1);
            Run(b, 0.5f);
            Assert.IsFalse(foe.IsVisibleTo(0));
            Run(b, 1.5f);
            Assert.IsTrue(foe.IsVisibleTo(0), "revealed");
            Run(b, 9f);
            Assert.IsFalse(foe.IsVisibleTo(0), "for a few seconds only");
        }

        [Test]
        public void TheBlackoutTakesTheRadarAwayForItsCountdown()
        {
            var b = Start(Mission("{\"id\": \"b\", \"kind\": \"Blackout\", \"trigger\": {\"at\": 1}, \"params\": {\"seconds\": 20}}", "\"b\""));
            var foe = Group(b, 1, new Vector2(60f, 60f), 1);
            b.World.Strikes.AddScan(0, foe.Position, 20f, 999f);
            Run(b, 2f);
            Assert.IsTrue(foe.IsVisibleTo(0), "the scan sees it");
            Run(b, 10f);
            Assert.IsTrue(b.World.BlackedOut(0));
            Assert.IsFalse(foe.IsVisibleTo(0), "only what the units see themselves");
            Assert.AreEqual(20f, Notices(b, "event.blackout.start").Single().Value, 1e-3, "the countdown");
            Run(b, 21f);
            Assert.IsFalse(b.World.BlackedOut(0));
            Assert.IsTrue(foe.IsVisibleTo(0));
            Assert.AreEqual(1, Notices(b, "event.blackout.end").Count());
        }

        [Test]
        public void AMiniBossOfTheGeneralsComesInThatIsNotTheMissionsBoss()
        {
            var b = Start(Mission("{\"id\": \"m\", \"kind\": \"MiniBoss\", \"trigger\": {\"at\": 1}}", "\"m\"",
                ", \"general\": \"varga\", \"boss\": {\"def\": \"behemoth_inferno\", \"x\": 100, \"z\": 40}"));
            Run(b, 1f + 10f + 1f);
            var mini = b.Brought(1).Single();
            Assert.IsTrue(mini.Def.MiniBoss && mini.Def.General == "varga" && mini.Def.Id != "behemoth_inferno", mini.Def.Id);
            Assert.IsTrue(b.Seen.Any(e => e.Kind == SimEventKind.Radio && e.DefId == "radio.varga.ev.miniBoss.start" && e.Entity == mini.Id));
        }

        [Test]
        public void KadesNewPlanChangesTheObjective()
        {
            var b = Start(Mission("{\"id\": \"p\", \"kind\": \"PlanChange\", \"trigger\": {\"at\": 2}, \"priority\": 0}",
                "{\"id\": \"p\", \"plan\": {\"surviveSeconds\": 50}}"));
            var replanned = false;
            b.Mode.Replanned += () => replanned = true;
            Run(b, 3f);
            Assert.IsTrue(replanned);
            Assert.AreEqual(50f, b.Mode.Def.SurviveSeconds);
            Assert.AreEqual(1, Notices(b, "event.planChange.start").Count());
            var line = b.Seen.Single(e => e.Kind == SimEventKind.Radio && e.DefId == "radio.khai.ev.planChange.start");
            Assert.AreEqual(LinePriority.Story, line.Priority);
        }

        [Test]
        public void TheWeatherTurnsOverItsSecondsAndSightFollows()
        {
            var b = Start(Mission("{\"id\": \"w\", \"kind\": \"WeatherShift\", \"trigger\": {\"at\": 1}, \"params\": {\"to\": \"Snow\", \"seconds\": 25}}", "\"w\""));
            Run(b, 1f + 10f + 0.1f);
            var shift = b.Seen.Single(e => e.Kind == SimEventKind.WeatherShift);
            Assert.AreEqual("Snow", shift.DefId);
            Assert.AreEqual(25f, shift.Value, 1e-3);
            Run(b, 12.5f);
            Assert.AreEqual(0.925f, b.World.WeatherSight, 0.01f, "halfway");
            Run(b, 13f);
            Assert.AreEqual(0.85f, b.World.WeatherSight, 1e-3, "snow's sight");
            Assert.AreEqual(EventPhase.Done, b.State().Phase);
        }

        // ================================================================== A.3: determinism

        [Test]
        public void AReplayOfTheJournalBringsTheEventsBack()
        {
            const string events = "{\"id\": \"w\", \"kind\": \"EnemyWave\", \"trigger\": {\"at\": 5}, \"params\": {\"size\": 6}}, " +
                                  "{\"id\": \"l\", \"kind\": \"LootDrop\", \"trigger\": {\"at\": 8}}, " +
                                  "{\"id\": \"g\", \"kind\": \"GeneralField\", \"trigger\": {\"after\": \"w\", \"delay\": 5}}, " +
                                  "{\"id\": \"s\", \"kind\": \"WeatherShift\", \"trigger\": {\"at\": 12}, \"params\": {\"to\": \"Fog\"}}, " +
                                  "{\"id\": \"b\", \"kind\": \"Blackout\", \"trigger\": {\"at\": 20}}";
            MissionDef Def() => Mission(events, "\"w\", \"l\", \"g\", \"s\", \"b\"", ", \"general\": \"orlov\", \"chapter\": 3");
            const long checkpoint = 700;

            var a = Start(Def(), seed: 7);
            var moves = new[] { (100L, new Vector2(-40f, -60f)), (400L, new Vector2(0f, -20f)) };
            ulong hash = 0;
            List<(long, string, string)> log = null;
            Run(a, 45f, each: () =>
            {
                foreach (var (tick, to) in moves)
                    if (a.World.Tick == tick) a.World.SubmitPlayer(new Command(CommandType.Move, 0, new[] { a.Anchor.Id }, to));
                if (a.World.Tick != checkpoint) return;
                hash = a.World.StateHash();
                log = a.Events.Log.ToList();
            });
            Assert.IsTrue(log.Any(l => l.Item2 == "g" && l.Item3 == "start") && log.Any(l => l.Item2 == "b" && l.Item3 == "warn"), "events under way at the checkpoint");

            // The checkpoint's way back (prompt 5): the same seed, the journal's commands at their steps.
            var b = Start(Def(), seed: 7);
            var journal = a.World.Journal.ToList();
            var next = 0;
            while (b.World.Tick < checkpoint)
            {
                while (next < journal.Count && journal[next].tick <= b.World.Tick) b.World.SubmitPlayer(journal[next++].command);
                b.Mode.Tick(b.World, Dt);
                b.World.Step(Dt);
                b.World.ClearEvents();
            }
            Assert.AreEqual(hash, b.World.StateHash(), "the battle, its events and their state");
            CollectionAssert.AreEqual(log, b.Events.Log.ToList(), "every moment of every event");
        }

        // ================================================================== B: spawn points and prompt 12's probe

        /// <summary>
        /// Every battlefield (Conquest's square and the long one) has enemy points on its front and a flank, allied points,
        /// all on the open ground of the battlefield and clear of the player's camp; a heavy hull from each drives into the
        /// battle without getting stuck (prompt 12's watch, one seed).
        /// </summary>
        [Test, Timeout(1800000)]
        public void EveryBattlefieldHasSpawnPointsAndNothingSticksOnTheWayIn()
        {
            var bad = new List<string>();
            var summary = new List<string>();
            foreach (var info in MatchSettings.AllMaps)
                foreach (var variant in new[] { "conquest", "long", "siege" })
                {
                    var file = info.Id + "_" + variant;
                    if (Resources.Load<TextAsset>("Data/maps/" + file) == null) continue;
                    var map = GameContent.LoadMap(file);
                    var world = new SimWorld(Catalog, map, 1);
                    var sp = SpawnPoints.Build(world);
                    var bearings = sp.Bearings(SpawnSide.Enemy);
                    if (!bearings.Contains(SpawnBearing.Front) || !(bearings.Contains(SpawnBearing.Left) || bearings.Contains(SpawnBearing.Right)))
                        bad.Add($"{file}: enemy directions {string.Join(",", bearings)}");
                    if (!sp.Of(SpawnSide.Ally).Any()) bad.Add($"{file}: no allied point");
                    foreach (var p in sp.All)
                    {
                        if (!world.Grid.IsWalkable(p.Position) || world.Grid.RegionOf(p.Position) != world.Grid.MainRegion) bad.Add($"{file}: {p.Id} off the open ground");
                        if (p.Side == SpawnSide.Enemy && Vector2.Distance(p.Position, sp.Home) < SpawnPoints.CampClearance - 1f) bad.Add($"{file}: {p.Id} in the player's camp");
                    }
                    // The probe: one heavy hull from every ground point, each to its own spot in the battle; the enemy's points and
                    // the allies' in two runs (the two streams would meet head-on in the middle, which is traffic, not a spawn).
                    var probes = 0;
                    var stuck = new List<StuckRecord>();
                    foreach (var side in new[] { SpawnSide.Enemy, SpawnSide.Ally })
                    {
                        var run = new SimWorld(Catalog, map, 1);
                        var points = SpawnPoints.Build(run).Of(side).Where(p => p.Kind is not (SpawnKind.Air or SpawnKind.Landing)).ToList();
                        var watch = new StuckWatch(file, "Spawn", 1);
                        run.TryGetRally(0, out var home);
                        foreach (var p in points)
                        {
                            var goal = side == SpawnSide.Enemy ? Vector2.Lerp(home, run.Map.Centre, 0.35f) : run.Map.Centre;
                            var angle = probes++ * 2.39996f;
                            goal += new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (14f + (probes % 5) * 9f);
                            var v = run.SpawnVehicle("main_battle_tank", 1, p.Position, MachineBrigade.Sim.Core.SimMath.HeadingOf(p.Inward));
                            run.Submit(new Command(CommandType.Move, 1, new[] { v.Id }, run.Map.Clamp(goal, 4f)));
                        }
                        for (var t = 0; t < 1600; t++)
                        {
                            run.Step(Dt);
                            run.ClearEvents();
                            watch.Observe(run);
                        }
                        watch.Finish(run);
                        stuck.AddRange(watch.Records.Where(r => r.Seconds >= 10.0));
                    }
                    foreach (var r in stuck) bad.Add($"{file}: #{r.VehicleId} stuck {r.Seconds:0}s at ({r.Position.X:0},{r.Position.Y:0}) {r.Cause} {r.Detail}");
                    summary.Add($"{file}: {sp.All.Count} points ({sp.Of(SpawnSide.Enemy).Count()} enemy, {sp.Of(SpawnSide.Ally).Count()} allied), {probes} probes, {stuck.Count} stuck");
                }
            Debug.Log("PROMPT23 SPAWNS\n" + string.Join("\n", summary));
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(60)));
        }

        // ================================================================== the texts

        /// <summary>Every notice and line an event of the library can show has both languages, the names as tokens, one language each.</summary>
        [Test]
        public void EveryEventTextExistsInBothLanguages()
        {
            var library = EventLibrary.FromJson(GameContent.CampaignJson);
            Assert.GreaterOrEqual(library.Ids.Count, 18);
            var kinds = new HashSet<MissionEventKind>();
            var bad = new List<string>();
            var generals = library.Rules.Generals.Keys.ToList();
            foreach (var id in library.Ids)
            {
                var e = library.Get(id);
                kinds.Add(e.Kind);
                var variant = e.Kind == MissionEventKind.SideObjective ? e.Word("type") : e.Kind == MissionEventKind.WeatherShift ? e.Word("to")?.ToLowerInvariant() : null;
                foreach (var moment in MissionEventSystem.NoticeMoments(e.Kind))
                    if (!Strings.Has(MissionEventSystem.NoticeKey(e, moment, variant))) bad.Add(MissionEventSystem.NoticeKey(e, moment, variant));
                foreach (var moment in MissionEventSystem.LineMoments(e.Kind))
                    foreach (var g in generals)
                        if (MissionEventSystem.DefaultSpeaker(e, moment, g) is { } who && !Strings.Has(MissionEventSystem.LineKey(e, moment, who, variant)))
                            bad.Add(MissionEventSystem.LineKey(e, moment, who, variant));
            }
            Assert.AreEqual(Enum.GetValues(typeof(MissionEventKind)).Length, kinds.Count, "the library has every kind");
            var allowed = UiLanguageTests.AllowedNames();
            var raw = new[] { "Kade", "Nadia", "Hawk", "Mara", "Thorne", "Raven" };
            foreach (var (key, (en, vi)) in EventText.Table)
            {
                if (UiLanguageTests.EnglishIn(vi, allowed) is { Count: > 0 } english) bad.Add($"{key}: English in the Vietnamese ({string.Join(", ", english)})");
                if (L10nTests.VietnameseLetter.IsMatch(L10nTests.WithoutKeptNames(en))) bad.Add($"{key}: Vietnamese in the English");
                if (raw.Any(n => en.Contains(n) || vi.Contains(n))) bad.Add($"{key}: a story name not written as its token");
                if (!Strings.PlaceholderNames(en).OrderBy(n => n).SequenceEqual(Strings.PlaceholderNames(vi).OrderBy(n => n))) bad.Add($"{key}: placeholders differ");
            }
            Assert.IsEmpty(bad, string.Join("\n", bad.Distinct()));
        }
    }
}
