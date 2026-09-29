using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Sandbox;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 21 part 3, the Sandbox's cheap checks (DECISIONS 20S): placing and turning (towers on hardpoints, anywhere
    /// on the test range, their rank-7 branch), undo, formations, the heading kept into the battle, a scenario run twice
    /// giving the same battle, saving and reading back (and a version-1 file), the boss tools, the overlays' numbers
    /// against the data, the player version's limits and a share code's stand-ins, the duel, A/B, the scenario test
    /// suite, and the words in both languages. The FPS at the unit ceiling waits for the testing phase.
    /// </summary>
    public class SandboxTests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SandboxEditor Editor(MapDefinition map = null, bool internalBuild = true, Func<VehicleDef, bool> allowed = null) =>
            new(Catalog, map ?? SandboxMaps.Flat(), new SandboxScenario(), internalBuild, allowed);

        private static (SimWorld world, SandboxBattle battle) Build(SandboxScenario s, MapDefinition map = null)
        {
            var world = new SimWorld(Catalog, map ?? SandboxMaps.Flat(), s.Seed);
            var battle = new SandboxBattle(s);
            battle.Setup(world);
            return (world, battle);
        }

        private static Vehicle Of(SimWorld world, SandboxBattle battle, int index) =>
            world.TryGetVehicle(new EntityId(battle.Spawned[index]), out var v) ? v : null;

        // ------------------------------------------------------------------ B.4-B.6, B.9: placing, turning, towers

        [Test]
        public void PlacingTurnsByTheStepAndTheHeadingGoesIntoTheBattle()
        {
            var e = Editor();
            Assert.AreEqual(SandboxRefusal.None, e.Place("main_battle_tank", new Vector2(10.004f, -20f), 37f, out var i));
            Assert.AreEqual(30f, e.Units[i].Heading, "snapped to the 15-degree step");
            Assert.AreEqual(10f, e.Units[i].X, 1e-4f, "kept to the centimetre");
            e.FreeRotation = true;
            e.Rotate(new[] { i }, 37.26f);
            Assert.AreEqual(37.3f, e.Units[i].Heading, 1e-3f, "free rotation");
            e.FreeRotation = false;
            e.Rotate(new[] { i }, SandboxRules.HeadingTowards(e.Units[i].Position, e.Units[i].Position + new Vector2(10f, 0f), false));
            Assert.AreEqual(90f, e.Units[i].Heading, "a drag east turns it east");
            e.RotateBy(new[] { i }, -SandboxRules.RotationStep);
            Assert.AreEqual(75f, e.Units[i].Heading);
            Assert.AreEqual(SandboxRefusal.OffMap, e.Place("main_battle_tank", new Vector2(500f, 0f), 0f, out _));
            Assert.AreEqual(SandboxRefusal.NoSea, e.Place(Catalog.Vehicles.Values.First(d => d.Naval != null && !d.Boss).Id, Vector2.Zero, 0f, out _));
            e.Settings(x => x.Sides[0].Ai = SandboxAi.Idle);
            var (world, battle) = Build(e.Scenario);
            var v = Of(world, battle, 0);
            Assert.AreEqual(SimMath.DegToRad(75f), v.Heading, 1e-4f, "the heading set is the one the battle starts with");
            // A few steps with no AI and nothing to shoot: it still faces the same way.
            for (var s = 0; s < 5; s++)
            {
                battle.Tick(world, SandboxLab.Step);
                world.Step(SandboxLab.Step);
            }
            Assert.AreEqual(SimMath.DegToRad(75f), v.Heading, 0.05f);
            // Setting up mirrors the scenario onto the field: its units taken off and placed again, nothing left over.
            var more = e.Scenario.Clone();
            more.Units.Add(new SandboxUnit { Def = "light_tank", Position = new Vector2(20f, 20f) });
            Assert.AreEqual(1, battle.Rebuild(world, more).Count);
            Assert.AreEqual(2, world.Vehicles.Count(x => x.IsAlive));
        }

        [Test]
        public void TowersGoOnHardpointsAnywhereOnTheRangeAndTakeTheirBranchAtRankSeven()
        {
            var map = GameContent.LoadMap("ashfield_conquest");
            var slot = map.Bases.SelectMany(b => b.Slots).First(s => s.Kind == HardpointKind.Tower && s.Class == SlotSize.Large);
            var player = Editor(map, internalBuild: false, allowed: _ => true);
            Assert.AreEqual(SandboxRefusal.NotOnHardpoint, player.Place("gun_turret", map.Centre + new Vector2(3f, 3f), 0f, out _), "off a hardpoint on a battlefield");
            Assert.AreEqual(SandboxRefusal.None, player.Place("gun_turret", slot.Position + new Vector2(2f, 1f), 0f, out var t));
            Assert.AreEqual(slot.Position.X, player.Units[t].X, 1e-3f, "snapped onto the hardpoint");
            Assert.AreEqual(SandboxRules.Normalise(slot.Facing), player.Units[t].Heading, 1e-3f, "facing as the hardpoint does");
            Assert.AreEqual(SandboxRefusal.HardpointTaken, player.Place("gun_turret", slot.Position, 0f, out _));
            // The internal build and the flat test range: anywhere.
            Assert.AreEqual(SandboxRefusal.None, Editor(map).Place("gun_turret", map.Centre + new Vector2(3f, 3f), 0f, out _));
            var range = Editor();
            Assert.AreEqual(SandboxRefusal.None, range.Place("aa_turret", new Vector2(5f, 5f), 20f, out var aa));
            Assert.AreEqual(5f, range.Units[aa].X, 1e-3f);
            // Rank 7 and a branch.
            var branches = SandboxRules.Branches(Catalog, "aa_turret");
            Assert.That(branches.Count, Is.GreaterThanOrEqualTo(2), "the AA tower has two branches");
            Assert.IsFalse(range.SetBranch(aa, branches[0]), "no branch under rank 7");
            range.Edit(new[] { aa }, u => u.Rank = 7);
            Assert.IsTrue(range.SetBranch(aa, branches[1]));
            Assert.AreEqual(branches[1], range.Units[aa].Def);
            var (world, battle) = Build(range.Scenario);
            Assert.AreEqual(branches[1], Of(world, battle, aa).Def.Id, "the tower fights as its branch");
            range.Edit(new[] { aa }, u => u.Rank = 5);
            Assert.AreEqual("aa_turret", range.Units[aa].Def, "under rank 7 the branch goes");
            Assert.AreEqual(SandboxTab.Towers, SandboxRules.TabOf(Catalog.Vehicles["aa_turret"]));
            Assert.IsNull(SandboxRules.TabOf(Catalog.Vehicles[branches[0]]), "branches are picked on the tower, not listed");
        }

        [Test]
        public void CopyDeleteMoveFormationsAndUndo()
        {
            var e = Editor();
            e.Place("light_tank", new Vector2(0f, 0f), 0f, out var a);
            e.Place("ifv", new Vector2(10f, 0f), 90f, out var b);
            var copies = e.Copy(new[] { a, b }, new Vector2(0f, 20f));
            Assert.AreEqual(4, e.Units.Count);
            Assert.AreEqual(20f, e.Units[copies[0]].Y, 1e-3f);
            Assert.AreEqual(90f, e.Units[copies[1]].Heading);
            Assert.IsTrue(e.Move(new[] { copies[0], copies[1] }, new Vector2(-30f, -30f)));
            Assert.AreEqual(-20f, e.Units[copies[1]].X, 1e-3f, "moved together, their places round the first kept");
            e.Delete(new[] { a });
            Assert.AreEqual(3, e.Units.Count);
            Assert.AreEqual(SandboxRefusal.None, e.PlaceFormation("main_battle_tank", new Vector2(40f, 40f), 44f, SandboxFormation.Line, 4, out var line));
            Assert.AreEqual(4, line.Count);
            Assert.IsTrue(line.All(i => e.Units[i].Heading == 45f), "the whole formation faces one way");
            var spacing = Vector2.Distance(e.Units[line[0]].Position, e.Units[line[1]].Position);
            Assert.AreEqual(SandboxRules.Spacing(Catalog.Vehicles["main_battle_tank"]), spacing, 0.05f);
            // Undo walks back every step, redo forward again.
            var after = e.Scenario.ToJson();
            Assert.IsTrue(e.Undo());
            Assert.AreEqual(3, e.Units.Count);
            Assert.IsTrue(e.Undo());
            Assert.AreEqual(4, e.Units.Count, "the deleted tank is back");
            Assert.IsTrue(e.Redo());
            Assert.IsTrue(e.Redo());
            Assert.AreEqual(after, e.Scenario.ToJson(), "redo gives exactly what was there");
            while (e.Undo()) { }
            Assert.AreEqual(0, e.Units.Count);
        }

        [Test]
        public void TheCeilingWarnsInTheInternalBuildAndStopsThePlayer()
        {
            var inside = Editor();
            var player = Editor(internalBuild: false, allowed: _ => true);
            for (var i = 0; i < SandboxRules.VehicleCap; i++)
            {
                var p = new Vector2(-120f + i % 16 * 15f, -100f + i / 16 * 15f);
                inside.Place("scout_jeep", p, 0f, out _);
                player.Place("scout_jeep", p, 0f, out _);
            }
            Assert.AreEqual(SandboxRefusal.None, inside.Place("scout_jeep", new Vector2(0f, 90f), 0f, out _));
            Assert.IsTrue(inside.OverCapWarning, "over the ceiling: a warning only");
            Assert.AreEqual(SandboxRefusal.CapReached, player.Place("scout_jeep", new Vector2(0f, 90f), 0f, out _));
            player.Team = 1;
            Assert.AreEqual(SandboxRefusal.None, player.Place("scout_jeep", new Vector2(0f, 90f), 0f, out _), "the ceiling is per side");
        }

        // ------------------------------------------------------------------ C.7: the same scenario, seed and controls, the same battle

        private static SandboxScenario Skirmish(int seed)
        {
            var s = new SandboxScenario { Seed = seed, Fog = false, Limit = 40f };
            void Add(string def, int team, float x, float y, float h) => s.Units.Add(new SandboxUnit { Def = def, Team = team, Heading = h, Position = new Vector2(x, y) });
            Add("main_battle_tank", 0, -10f, -35f, 0f);
            Add("ifv", 0, 10f, -35f, 0f);
            Add("aa_vehicle", 0, 0f, -45f, 0f);
            Add("heavy_tank", 1, 0f, 35f, 180f);
            Add("attack_helicopter", 1, 20f, 50f, 180f);
            s.Units[1].Hp = 60;
            s.Units[0].Ammo = 50;
            return s;
        }

        [Test]
        public void TheSameScenarioSeedAndControlsGiveTheSameBattle()
        {
            var s = Skirmish(7);
            List<(long, SandboxOp)> Journal(SandboxBattle b)
            {
                var ids = b.Spawned;
                return new List<(long, SandboxOp)>
                {
                    (10, new SandboxOp { Kind = SandboxOpKind.Move, Units = new[] { ids[0], ids[1] }, Point = new Vector2(0f, 0f) }),
                    (30, SandboxOp.For(SandboxOpKind.HoldFire, new[] { ids[2] }, 1)),
                    (60, SandboxOp.For(SandboxOpKind.Immortal, new[] { ids[3] }, 1)),
                    (200, SandboxOp.For(SandboxOpKind.Immortal, new[] { ids[3] }, 0)),
                    (220, SandboxOp.Side(SandboxOpKind.SideImmortal, 0, 1)),
                };
            }
            var (_, probe) = Build(s.Clone());
            var journal = Journal(probe);
            var a = SandboxLab.Run(Catalog, SandboxMaps.Flat(), s, 40f, journal: journal);
            var b = SandboxLab.Run(Catalog, SandboxMaps.Flat(), SandboxScenario.FromJson(s.ToJson()), 40f, journal: journal);
            Assert.AreEqual(a.Hash, b.Hash, "the same state at the end");
            Assert.AreEqual(a.Winner, b.Winner);
            Assert.AreEqual(a.Steps, b.Steps);
            Assert.AreEqual(a.Stats.Hits, b.Stats.Hits);
            Assert.Greater(a.Stats.Hits, 0, "they fought");
            // The replay export carries the scenario and the journal: played again, the same battle.
            var (world, battle) = Build(s.Clone());
            battle.Replay(journal);
            for (var i = 0; i < a.Steps && battle.Result == null; i++)
            {
                battle.Tick(world, SandboxLab.Step);
                world.Step(SandboxLab.Step);
                world.ClearEvents();
            }
            var (scenario, back) = SandboxBattle.ReadReplay(battle.ReplayJson());
            Assert.AreEqual(journal.Count, back.Count);
            var c = SandboxLab.Run(Catalog, SandboxMaps.Flat(), scenario, 40f, journal: back);
            Assert.AreEqual(a.Hash, c.Hash, "the exported replay plays the same battle");
        }

        [Test]
        public void ControlsTakeEffect()
        {
            var s = Skirmish(3);
            s.Sides[0].Cp = -1f;
            s.Sides[1].Ai = SandboxAi.Idle;
            s.Sides[0].Immortal = true;
            var (world, battle) = Build(s);
            var tank = Of(world, battle, 0);
            var heavy = Of(world, battle, 3);
            Assert.AreEqual(60f, Of(world, battle, 1).Hp / Of(world, battle, 1).MaxHp * 100f, 0.5f, "health set in the scenario");
            Assert.Less(tank.Ammo(0), tank.Def.Mounts[0].Weapon.Ammo > 0 ? tank.Def.Mounts[0].Weapon.Ammo : int.MaxValue);
            battle.Queue(SandboxOp.For(SandboxOpKind.Hold, new[] { heavy.Id.Value }));
            battle.Queue(new SandboxOp { Kind = SandboxOpKind.Move, Units = new[] { tank.Id.Value }, Point = new Vector2(-40f, -35f) });
            var start = heavy.Position;
            for (var i = 0; i < 100; i++)
            {
                battle.Tick(world, SandboxLab.Step);
                world.Step(SandboxLab.Step);
            }
            Assert.IsTrue(tank.Invulnerable, "the whole side is immortal");
            Assert.Less(Vector2.Distance(heavy.Position, start), 1f, "held in place");
            Assert.Less(Vector2.Distance(tank.Position, new Vector2(-40f, -35f)), 25f, "went where it was sent");
            Assert.IsTrue(world.TryGetEconomy(0, out var e) && e.Cp >= SandboxBattle.UnlimitedCp - 1f, "unlimited CP");
            Assert.Greater(battle.Journal.Count, 1, "every control is in the journal");
        }

        // ------------------------------------------------------------------ F.1, F.7: files, codes and old versions

        [Test]
        public void ScenariosSaveReadBackAndOldVersionsStillOpen()
        {
            var s = Skirmish(11);
            s.Name = "Thử \"quote\" · ü";
            s.Units[0].Rank = 6;
            s.Units[0].Gear = SandboxGear.Suggested;
            s.Units[1].Elite = true;
            s.Units.Add(new SandboxUnit { Def = "behemoth", Team = 1, Position = new Vector2(0f, 80f), Heading = 180f, Boss = new SandboxBossState { Phase = 1, BigOff = true, Broken = { 0, 2 } } });
            s.Sides[1].Ai = SandboxAi.Full;
            s.Sides[1].Deck.Add("light_tank");
            s.Checks.Add(new SandboxCheck { Kind = "win", Team = 0, Seconds = 45f });
            var json = s.ToJson();
            var back = SandboxScenario.FromJson(json);
            Assert.AreEqual(json, back.ToJson(), "read back exactly");
            Assert.AreEqual(SandboxScenario.Version, back.LoadedVersion);
            Assert.AreEqual(json, SandboxScenario.FromCode(s.ToCode()).ToJson(), "the share code carries all of it");
            StringAssert.StartsWith("MBS2.", s.ToCode());
            Assert.Throws<FormatException>(() => SandboxScenario.FromCode("MBS2.not-a-code"));
            Assert.Throws<FormatException>(() => SandboxScenario.FromJson("{\"version\":99,\"units\":[]}"), "a newer game's file is refused, not misread");
            // Version 1: map, seed and units, the heading in radians.
            var old = SandboxScenario.FromJson("{\"version\":1,\"map\":\"sandbox_flat\",\"seed\":5,\"units\":[{\"def\":\"light_tank\",\"team\":1,\"x\":4.5,\"y\":-2,\"h\":1.5707963}]}");
            Assert.AreEqual(1, old.LoadedVersion);
            Assert.AreEqual(1, old.Units.Count);
            Assert.AreEqual(90f, old.Units[0].Heading, 0.05f, "radians upgraded to degrees");
            Assert.AreEqual(100, old.Units[0].Hp);
            Assert.AreEqual(SandboxAi.Combat, old.Sides[0].Ai);
            StringAssert.Contains("\"version\":2", old.ToJson(), "written back in the current version");
        }

        // ------------------------------------------------------------------ D: boss tools

        [Test]
        public void BossToolsWork()
        {
            var parted = Catalog.Vehicles.Values.First(d => d.Boss && d.Parts.Count >= 2 && d.BigAttack != null && d.Tiers == null && d.Naval == null && !d.Flying);
            var s = new SandboxScenario { Fog = false };
            s.Sides[0].Ai = SandboxAi.Idle;
            s.Sides[1].Ai = SandboxAi.Idle;
            s.Units.Add(new SandboxUnit { Def = parted.Id, Team = 1, Position = new Vector2(0f, 40f), Heading = 180f, Boss = new SandboxBossState() });
            s.Units.Add(new SandboxUnit { Def = "scout_jeep", Team = 0, Position = new Vector2(0f, -120f), Immortal = true });
            var (world, battle) = Build(s);
            var boss = Of(world, battle, 0);
            void Step(int n = 1)
            {
                for (var i = 0; i < n; i++)
                {
                    battle.Tick(world, SandboxLab.Step);
                    world.Step(SandboxLab.Step);
                }
            }
            var id = boss.Id.Value;
            battle.Queue(SandboxOp.Boss(SandboxOpKind.BossBreak, id, 0));
            Step();
            Assert.IsTrue(boss.IsPartBroken(0), "a part broken");
            battle.Queue(SandboxOp.Boss(SandboxOpKind.BossRestore, id, 0));
            Step();
            Assert.IsFalse(boss.IsPartBroken(0), "and whole again");
            battle.Queue(SandboxOp.Boss(SandboxOpKind.BossBigOff, id, 1));
            Step();
            Assert.IsTrue(boss.BigAttack.Off, "big attack off");
            battle.Queue(SandboxOp.Boss(SandboxOpKind.BossBig, id));
            battle.Tick(world, SandboxLab.Step);
            Assert.IsFalse(boss.BigAttack.Off, "triggering switches it on again");
            Assert.That(boss.BigAttack.Stage != BigStage.Ready || boss.BigAttack.Next <= world.Time, "its big attack is due now");
            world.Step(SandboxLab.Step);
            var hp = boss.Hp;
            battle.Queue(SandboxOp.Boss(SandboxOpKind.BossPhase, id, 1));
            Step(2);
            Assert.That(boss.Phase >= 1 || boss.Hp < hp, "into its next phase");
            battle.Queue(SandboxOp.Boss(SandboxOpKind.BossEscorts, id, 0));
            Step();
            Assert.AreEqual(0, world.EscortsAlive(boss.Id), "escorts sent home");

            // Main and mini boss swapped in place, the selection following.
            var main = Catalog.Vehicles.Values.First(d => d.Boss && d.MiniVariant != null && Catalog.Vehicles.ContainsKey(d.MiniVariant));
            var s2 = new SandboxScenario();
            s2.Units.Add(new SandboxUnit { Def = main.Id, Team = 1, Position = new Vector2(0f, 40f), Boss = new SandboxBossState() });
            var (w2, b2) = Build(s2);
            b2.Queue(SandboxOp.Boss(SandboxOpKind.BossSwap, b2.Spawned[0]));
            b2.Tick(w2, SandboxLab.Step);
            Assert.IsTrue(w2.TryGetVehicle(new EntityId(b2.LastSwapped), out var mini) && mini.Def.Id == main.MiniVariant, "swapped for its mini boss");

            // An altitude-tier boss placed at the low tier comes down to it once out of its opening orbit.
            var tiered = Catalog.Vehicles.Values.First(d => d.Boss && d.Tiers != null);
            var s3 = new SandboxScenario();
            s3.Units.Add(new SandboxUnit { Def = tiered.Id, Team = 1, Position = new Vector2(0f, 40f), Tier = "low", Boss = new SandboxBossState() });
            var (w3, b3) = Build(s3);
            var v3 = Of(w3, b3, 0);
            for (var i = 0; i < 400 && v3.TierFrom != AltitudeTier.Low; i++)
            {
                b3.Tick(w3, SandboxLab.Step);
                w3.Step(SandboxLab.Step);
            }
            Assert.AreEqual(AltitudeTier.Low, v3.TierFrom, "forced to the chosen tier");
            b3.Queue(SandboxOp.Boss(SandboxOpKind.BossTier, v3.Id.Value, 2));
            b3.Tick(w3, SandboxLab.Step);
            Assert.AreEqual(AltitudeTier.High, v3.Shifting ? v3.TierTo : v3.TierFrom, "and on its way up again on command");
        }

        // ------------------------------------------------------------------ E: the overlays read the real numbers

        [Test]
        public void OverlaysMatchTheData()
        {
            var s = new SandboxScenario { Fog = false, Limit = 20f };
            s.Units.Add(new SandboxUnit { Def = "main_battle_tank", Team = 0, Position = new Vector2(0f, -15f), Heading = 0f });
            s.Units.Add(new SandboxUnit { Def = "heavy_tank", Team = 1, Position = new Vector2(0f, 15f), Heading = 90f });
            s.Sides[0].Ai = SandboxAi.Idle;
            s.Sides[1].Ai = SandboxAi.Idle;
            var (world, battle) = Build(s);
            var tank = Of(world, battle, 0);
            var (max, min) = SandboxProbe.Reach(tank);
            Assert.AreEqual(tank.Def.Mounts.Max(m => m.Weapon.Range), max, 1e-3f, "the range ring is the weapon's range");
            Assert.AreEqual(tank.Def.Mounts.Max(m => m.Weapon.MinRange), min, 1e-3f);
            var weapons = SandboxProbe.Weapons(tank);
            Assert.AreEqual(tank.Def.Mounts.Count, weapons.Count);
            for (var i = 0; i < 300 && battle.Stats.Hits < 3; i++)
            {
                battle.Tick(world, SandboxLab.Step);
                world.Step(SandboxLab.Step);
            }
            Assert.GreaterOrEqual(battle.Stats.Hits, 1, "hits are reported");
            var hit = battle.Stats.Recent.First(h => h.Attacker == tank.Id.Value);
            // The heavy tank stands side-on to the shooter: the round strikes its side (or its front if it turned).
            Assert.That(hit.Face is ArmorFace.Side or ArmorFace.Front, hit.Face.ToString());
            var target = Catalog.Vehicles["heavy_tank"];
            var expected = tank.Arms.Select(w => Catalog.Damage.Penetration(w.Penetration + tank.PenetrationUp, target.Armour[hit.Face])).ToList();
            Assert.That(expected.Any(p => Math.Abs(p - hit.Pen) < 1e-3f), $"the ✓ ~ ✕ mark is a round's penetration against the face struck ({hit.Pen} vs {string.Join(", ", expected)})");
            Assert.AreEqual(Matchup.Verdict(hit.Pen), hit.Verdict);
            var stats = battle.Stats.Get(tank.Id.Value);
            Assert.Greater(stats.DealtTotal, 0f);
            Assert.AreEqual(stats.Pierced + stats.Bounced, battle.Stats.Recent.Count(h => h.Attacker == tank.Id.Value));
        }

        // ------------------------------------------------------------------ A.2, F.7: the player version

        [Test]
        public void ThePlayerVersionOffersOnlyWhatThePlayerHasAndPaysNothing()
        {
            var boss = Catalog.Vehicles.Values.First(d => d.Boss && !d.MiniBoss);
            var offBoss = Catalog.Vehicles.Values.First(d => d.Boss && d.Id != boss.Id);
            var unlocked = new HashSet<string> { "light_tank", "main_battle_tank", "aa_turret", "attack_jet" };
            var access = new SandboxAccess(false, unlocked.Contains, id => id == boss.Id || id == offBoss.Id, id => id != offBoss.Id);
            Assert.IsTrue(access.Allowed(Catalog, Catalog.Vehicles["light_tank"]));
            Assert.IsFalse(access.Allowed(Catalog, Catalog.Vehicles["heavy_tank"]), "locked");
            Assert.IsTrue(access.Allowed(Catalog, boss), "a boss beaten");
            Assert.IsFalse(access.Allowed(Catalog, offBoss), "a boss of a chapter switched off, even beaten");
            Assert.IsFalse(access.InternalLayers, "no internal overlays");
            Assert.IsTrue(SandboxAccess.Everything.InternalLayers);
            var tanks = SandboxRules.Palette(Catalog, SandboxTab.Vehicles, allowed: d => access.Allowed(Catalog, d));
            CollectionAssert.AreEquivalent(new[] { "light_tank", "main_battle_tank" }, tanks.Select(d => d.Id));
            var elite = Catalog.EliteVariant("light_tank");
            if (elite != null) Assert.IsTrue(access.Allowed(Catalog, Catalog.Vehicles[elite]), "the elite of an unlocked vehicle");
            var branch = SandboxRules.Branches(Catalog, "aa_turret")[0];
            Assert.IsFalse(access.Allowed(Catalog, Catalog.Vehicles[branch]), "a branch not opened");

            // A code from someone else: locked units stand in by role, or go.
            var shared = new SandboxScenario();
            shared.Units.Add(new SandboxUnit { Def = "heavy_tank", Team = 0 });
            shared.Units.Add(new SandboxUnit { Def = "attack_helicopter", Team = 0 });
            shared.Units.Add(new SandboxUnit { Def = offBoss.Id, Team = 1, Boss = new SandboxBossState() });
            shared.Units.Add(new SandboxUnit { Def = "light_tank", Team = 1 });
            var code = shared.ToCode();
            var mine = SandboxScenario.FromCode(code);
            var changes = access.Fit(Catalog, mine);
            Assert.IsTrue(mine.Units.All(u => access.Allowed(Catalog, Catalog.Vehicles[u.Def])), "only what the player has");
            var heavy = changes.First(c => c.from == "heavy_tank");
            Assert.IsNotNull(heavy.to);
            Assert.AreEqual(SandboxTab.Vehicles, SandboxRules.TabOf(Catalog.Vehicles[heavy.to]), "a vehicle for a vehicle");
            Assert.AreEqual("attack_jet", changes.First(c => c.from == "attack_helicopter").to, "an aircraft for an aircraft");
            Assert.AreEqual(boss.Id, changes.First(c => c.from == offBoss.Id).to, "a boss for a boss");
            Assert.IsEmpty(SandboxAccess.Everything.Fit(Catalog, SandboxScenario.FromCode(code)), "the internal build changes nothing");

            // Nothing pays out, and nothing counts.
            Assert.IsNull(new SandboxSession().Outcome(new SimWorld(Catalog, SandboxMaps.Flat()), 10, 0), "no result card, no reward");
            DailyMissions.Suspended = true;
            var before = DailyMissions.Progress(0);
            DailyMissions.Record(DailyMissions.Current[0].Kind, 5);
            Assert.AreEqual(before, DailyMissions.Progress(0), "a Sandbox battle counts towards no challenge");
            DailyMissions.Suspended = false;
        }

        // ------------------------------------------------------------------ F.3, F.5: duel and A/B

        [Test]
        public void DuelsAndAbComparisonGiveTheRightAnswer()
        {
            var one = SandboxLab.Duel(Catalog, new[] { "heavy_tank" }, new[] { "scout_jeep" }, 40f, DuelFacing.Front, 1);
            Assert.AreEqual(0, one.Winner, "a heavy tank beats a scout jeep");
            Assert.Greater(one.HealthA, 0.5f);
            Assert.AreEqual(0f, one.HealthB);
            var again = SandboxLab.Duel(Catalog, new[] { "heavy_tank" }, new[] { "scout_jeep" }, 40f, DuelFacing.Front, 1);
            Assert.AreEqual(one.Seconds, again.Seconds, "the same duel twice, the same result");
            var (a, b, d) = SandboxLab.WinRate(Catalog, new[] { "scout_jeep" }, new[] { "heavy_tank" }, 40f, DuelFacing.Rear, 3);
            Assert.AreEqual(3, a + b + d);
            Assert.AreEqual(3, b, "the heavy tank wins every seed");
            var flank = SandboxLab.DuelScenario(Catalog, new[] { "light_tank" }, new[] { "heavy_tank" }, 50f, DuelFacing.Side, 1);
            Assert.AreEqual(90f, flank.Units[1].Heading, "into the flank: the second side turned side-on");

            // A/B: the same scenario, Blue three times as tough in B.
            var s = Skirmish(5);
            var (ra, rb) = SandboxLab.Compare(SandboxMaps.Flat(), s, 40f, Catalog, null, Catalog,
                (u, def) => u.Team == 0 ? new VehicleBoost(3f, 1f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f) : (VehicleBoost?)null);
            Assert.GreaterOrEqual(rb.HealthLeft[0], ra.HealthLeft[0], "tougher, it keeps more of its health");
            Assert.LessOrEqual(rb.Lost[0], ra.Lost[0]);
        }

        // ------------------------------------------------------------------ F.2: saved scenarios as tests

        [Test]
        public void SavedScenariosPassTheirChecks()
        {
            var dir = Path.Combine(UnityEngine.Application.dataPath, "MachineBrigade", "Tests", "EditMode", "Scenarios");
            var files = Directory.GetFiles(dir, "*.json");
            Assert.IsNotEmpty(files, "the suite has at least its sample");
            foreach (var file in files)
            {
                var s = SandboxScenario.FromJson(File.ReadAllText(file));
                Assert.IsNotEmpty(s.Checks, file + " says what passes");
                var map = SandboxMaps.IsFlat(s.Map) ? SandboxMaps.Flat() : GameContent.LoadMap(s.Map);
                var r = SandboxLab.Run(Catalog, map, s, SandboxLab.CheckSeconds(s));
                var failed = SandboxLab.Evaluate(s.Checks, r);
                Assert.IsEmpty(failed, Path.GetFileName(file) + ": " + string.Join("; ", failed));
            }
            // The samples all build and every unit in them exists.
            foreach (var sample in SandboxSamples.All())
                Assert.IsTrue(sample.Units.All(u => Catalog.Vehicles.ContainsKey(u.Def)), sample.Name);
        }

        // ------------------------------------------------------------------ the words

        [Test]
        public void EveryWordIsInBothLanguagesWithTheSameNamedParameters()
        {
            foreach (var (key, (en, vi)) in SandboxText.Table)
            {
                Assert.IsFalse(string.IsNullOrWhiteSpace(en), key + " en");
                Assert.IsFalse(string.IsNullOrWhiteSpace(vi), key + " vi");
                Assert.IsFalse(Regex.IsMatch(en + vi, @"\{\d+\}"), key + ": named parameters only");
                // The game's placeholder names, plurals ({count|# unit|# units}) included (prompt 21 I).
                CollectionAssert.AreEquivalent(Strings.PlaceholderNames(en).Distinct(), Strings.PlaceholderNames(vi).Distinct(), key);
            }
            foreach (SandboxTab tab in Enum.GetValues(typeof(SandboxTab))) Assert.IsTrue(Strings.Has("sandbox.tab." + tab), tab.ToString());
            foreach (SandboxRefusal r in Enum.GetValues(typeof(SandboxRefusal)))
                if (r != SandboxRefusal.None) Assert.IsTrue(Strings.Has("sandbox.refuse." + r), r.ToString());
            foreach (var id in SandboxSamples.Ids) Assert.IsTrue(Strings.Has("sandbox.sample." + id), id);
            var was = Strings.Vietnamese;
            Strings.Vietnamese = true;
            Assert.AreEqual("0,75", SandboxText.Number(0.75, 2));
            Assert.AreEqual("Đã chọn 3", SandboxText.Format("sandbox.selected", ("count", 3)));
            Strings.Vietnamese = false;
            Assert.AreEqual("1,234.5", SandboxText.Number(1234.5, 1));
            Strings.Vietnamese = was;
        }
    }
}
