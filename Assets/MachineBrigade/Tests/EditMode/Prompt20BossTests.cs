using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 20 pass 2 (DECISIONS 19E): the boss templates (frames, the part library, ranks, variants made by data), the
    /// main and mini boss rules on the existing bosses, the general links, the new bosses' mechanisms (Moloch's workshop,
    /// Kronos's crusher and swing, Ixion's charge, Typhon's dives, Daedalus's pods, Argus's fire direction) and the
    /// Sandbox's calls.
    /// </summary>
    public class Prompt20BossTests
    {
        private const float Step = 0.05f;

        private static Catalog C => Lab.Catalog;

        private static readonly string[] NewBosses =
            { "moloch", "daedalus", "kronos", "typhon", "ixion", "caspian", "bastion_mk0", "fenrir", "scylla", "locust", "behemoth_mk2", "icarus_mk0", "argus" };

        private static SimWorld Field(int seed = 3)
        {
            var world = Lab.Field(seed);
            world.BigAttackSettings = BigAttackSettings.For(C.BigAttackRules, "Normal");
            world.SetBoosts(0, _ => Lab.Harmless);
            return world;
        }

        private static List<SimEvent> Run(SimWorld world, float seconds, System.Func<bool> until = null)
        {
            var events = new List<SimEvent>();
            for (var t = 0f; t < seconds; t += Step)
            {
                world.Step(Step);
                events.AddRange(world.Events);
                world.ClearEvents();
                if (until != null && until()) break;
            }
            return events;
        }

        private static List<Vehicle> Group(SimWorld world, string def, Vector2 at, int n = 4, float hp = 50f)
        {
            var list = new List<Vehicle>();
            for (var i = 0; i < n; i++)
            {
                var v = world.SpawnVehicle(def, 0, at + new Vector2((i % 2) * 5f - 2.5f, (i / 2) * 5f), 0f);
                v.HpScale = hp;
                v.Hp = v.MaxHp;
                v.Scripted = true;
                list.Add(v);
            }
            return list;
        }

        // ------------------------------------------------------------------ E: the templates

        [Test]
        public void EveryBossIsBuiltOnAFrameARankAndItsGeneral()
        {
            var general = new Dictionary<string, string>
            {
                ["fortress_bastion"] = "brandt", ["bastion_mk0"] = "brandt", ["behemoth"] = "varga", ["moloch"] = "varga", ["behemoth_inferno"] = "varga",
                ["behemoth_mk2"] = "varga", ["mobile_fortress"] = "orlov", ["fenrir"] = "orlov", ["rail_supergun"] = "orlov", ["leviathan"] = "kessler",
                ["behemoth_tempest"] = "kessler", ["armored_train"] = "kessler", ["scylla"] = "kessler", ["landing_hovercraft"] = "kessler",
                ["drone_mothership"] = "sen", ["fortress_hive"] = "sen", ["locust"] = "sen", ["nuke_train"] = "hung", ["supreme_command"] = "hung",
                ["kronos"] = "hung", ["ixion"] = "hung", ["earth_borer"] = "hung", ["typhon"] = "hung", ["caspian"] = "hung", ["command_airship"] = "quaden",
                ["mega_gunship"] = "quaden", ["sky_fortress"] = "quaden", ["argus"] = "quaden", ["silver_bug"] = "aurel", ["daedalus"] = "aurel",
                ["icarus_mk0"] = "aurel", ["behemoth_mk0"] = "varga", ["morrigan"] = "quaden",
            };
            var bosses = C.Vehicles.Values.Where(v => v.Boss).ToList();
            Assert.AreEqual(33, bosses.Count, "12 main bosses and 21 mini bosses (prompt 22 E's two)");
            Assert.AreEqual(12, bosses.Count(b => b.Rank == BossRank.Main));
            Assert.AreEqual(21, bosses.Count(b => b.Rank == BossRank.Mini));
            foreach (var b in bosses)
            {
                Assert.IsNotNull(b.Frame, b.Id + " has a body frame");
                Assert.IsNotNull(b.RankDef, b.Id + " has its rank's rules");
                Assert.AreEqual(general[b.Id], b.General, b.Id + "'s general (prompt 20 K)");
                var phases = b.Tiers != null ? b.Tiers.Marks.Count : b.Phases.Count;
                Assert.AreEqual(b.MiniBoss ? 1 : 2, phases, b.Id + ": a main boss has three phases, a mini boss two");
                if (!b.MiniBoss) continue;
                // Play-test 6 (DECISIONS 21G): 0.8 -> 1.2 (+50 %); the big attack 0.7 -> 0.56 of that (+20 % in all).
                Assert.AreEqual(1.2f, b.DamageScale, 1e-4f, b.Id + ": a mini boss's weapons hit at 120 %");
                Assert.AreEqual(0.56f, b.BigAttackScale.Damage, 1e-4f, b.Id + ": its big attack at 56 % of that");
                Assert.AreEqual(1.1f, b.BigAttackScale.Cooldown, 1e-4f, b.Id + ": 10 % longer cooldown (30 % until play-test 6)");
                Assert.AreEqual(0f, b.BigAttackScale.Warn, 1e-4f, b.Id + ": the same warning");
            }
            // The resize (F.1, G.2): the model, hull and hit radius together; the parts with them.
            var behemoth = C.Vehicle("behemoth");
            Assert.AreEqual(1.2f * 1.35f, behemoth.Scale, 1e-3f);
            Assert.AreEqual(6.4f * 1.35f, behemoth.Radius, 1e-3f);
            Assert.AreEqual(3.5f * 1.35f, behemoth.Parts[behemoth.PartIndex("main_gun")].At.Y, 1e-3f);
            Assert.AreEqual(1.12f, C.Vehicle("leviathan").Scale, 1e-3f, "Leviathan about x1.1");
            Assert.AreEqual(1f, C.Vehicle("silver_bug").Scale, 1e-3f, "Icarus as prompt 19 left it");
            // The part library: Behemoth's new flank guns each carry a mount of their own with the library's weapon.
            var flank = behemoth.Parts[behemoth.PartIndex("side_gun_l")];
            Assert.AreEqual(1, flank.Mounts.Count);
            Assert.AreEqual("gun_120mm", behemoth.Mounts[flank.Mounts[0]].Weapon.Id);
            // A mini boss's dropped weapons (G.3): the Inferno has no flak, its model node hidden.
            var inferno = C.Vehicle("behemoth_inferno");
            Assert.AreEqual(-1, inferno.PartIndex("flak"));
            Assert.IsFalse(inferno.Mounts.Any(m => m.Weapon.Id == "boss_flak"), "the Inferno's flak is gone with its part");
            CollectionAssert.Contains(inferno.HiddenNodes.ToList(), "Mount_mg");
        }

        [Test]
        public void AVariantIsMadeFromItsMainBossByDataAlone()
        {
            // A new mini boss as one data entry: no code knows it.
            var json = File.ReadAllText(Path.Combine(Application.dataPath, "MachineBrigade/Resources/Data/balance.json"));
            const string entry = "{ \"id\": \"test_mk0\", \"variantOf\": \"behemoth\", \"bigAttack\": \"test_mk0_barrage\", " +
                                 "\"variant\": { \"size\": 0.6, \"keep\": [\"main_gun\", \"flak_l\"], \"tint\": [0.9, 1.0, 1.1], \"name\": \"mk0\" } },\n    ";
            json = json.Replace("\"vehicles\": [", "\"vehicles\": [\n    " + entry);
            json = json.Replace("\"bigAttacks\": [", "\"bigAttacks\": [\n    { \"id\": \"test_mk0_barrage\", \"from\": \"behemoth_barrage\", \"strikes\": [ { \"count\": 2 } ] },");
            var catalog = Catalog.FromJson(json);
            var mini = catalog.Vehicle("test_mk0");
            var main = catalog.Vehicle("behemoth");
            Assert.IsTrue(mini.Boss);
            Assert.AreEqual(BossRank.Mini, mini.Rank);
            Assert.AreEqual("behemoth", mini.VariantOf);
            Assert.AreEqual("mk0", mini.VariantName);
            Assert.AreEqual("behemoth", mini.Model, "drawn with its main boss's model");
            Assert.AreEqual(main.Scale * 0.6f, mini.Scale, 1e-3f, "shrunk from the main boss");
            Assert.AreEqual(main.Radius * 0.6f, mini.Radius, 1e-3f);
            Assert.AreEqual(main.MaxHp * 0.55f, mini.MaxHp, 1f, "a mini's health share");
            Assert.AreEqual(2, mini.Parts.Count, "only the parts it keeps");
            Assert.AreEqual(2, mini.Mounts.Count, "and only their weapons");
            Assert.AreEqual(1, mini.Parts[mini.PartIndex("flak_l")].Mounts[0], "the kept mounts renumbered");
            Assert.AreEqual(1.2f, mini.DamageScale, 1e-4f);
            Assert.IsNotNull(mini.Tint);
            Assert.IsTrue(mini.HiddenNodes.Contains("Mount_mg"), "the dropped flak is not drawn");
            Assert.AreEqual(2, mini.BigAttack.Strikes[0].Count, "its big attack scaled down from the main boss's");
            Assert.AreEqual(main.BigAttack.Strikes[0].Damage, mini.BigAttack.Strikes[0].Damage, 1e-3f);
            Assert.IsTrue(catalog.Escorts.TryGetValue("test_mk0", out var escorts), "its general's escort template");
            Assert.LessOrEqual(escorts.Arrive.Units.Count, 4, "a mini boss's escorts, four at most since play-test 6");
            Assert.IsNotNull(main.MiniVariant, "the main boss knows a mini version of itself");
        }

        // ------------------------------------------------------------------ H-J: the new bosses

        [Test]
        public void MolochBuildsFromItsDoorsCappedAndStopsWithThem()
        {
            var world = Field();
            var moloch = world.SpawnVehicle("moloch", 1, new Vector2(0f, 40f), 0f);
            moloch.BigAttack.Off = true;
            Run(world, 150f);
            var built = world.Bosses.BuiltAlive(moloch);
            Assert.That(built, Is.InRange(1, 6), "vehicles out of its doors, never more than six alive");
            foreach (var door in new[] { "door_l", "door_r" }) world.Bosses.Break(moloch, moloch.Def.PartIndex(door));
            var before = moloch.FactoryBuilt;
            Run(world, 60f);
            Assert.AreEqual(before, moloch.FactoryBuilt, "both doors broken: it builds no more");
        }

        [Test]
        public void KronosCrushesATowerInItsWayAndSwingsItsWheel()
        {
            var world = Field();
            var kronos = world.SpawnVehicle("kronos", 1, new Vector2(0f, 60f), SimMath.HeadingOf(new Vector2(0f, -1f)));
            kronos.BigAttack.Off = true;
            // A tower just in front of its bucket wheel.
            var tower = world.SpawnVehicle("gun_turret", 0, new Vector2(0f, 60f - kronos.Def.Length * 0.5f - 3f), 0f);
            Run(world, 30f, () => !tower.IsAlive);
            Assert.IsFalse(tower.IsAlive, "the bucket wheel crushes the tower in front of it");
            // The swing: everything in the arc in front of it; the boom broken, no more.
            var world2 = Field(4);
            var k2 = world2.SpawnVehicle("kronos", 1, Vector2.Zero, 0f);
            k2.Scripted = true;
            // The wheel broken first, so only the swing (the boom's) hurts.
            world2.Bosses.Break(k2, k2.Def.PartIndex("bucket_wheel"));
            // Only the swing: its guns (faster since play-test 6) would reach the tanks behind it.
            for (var m = 0; m < k2.MountOff.Length; m++) k2.MountOff[m] = true;
            var ahead = SimMath.Forward(k2.Heading);
            var front = Group(world2, "main_battle_tank", ahead * (k2.Def.Length * 0.5f + 8f), 2, 1f);
            var behind = Group(world2, "main_battle_tank", -ahead * (k2.Def.Length * 0.5f + 6f), 2, 1f);
            world2.Bosses.TriggerBig(k2);
            Run(world2, 8f);
            Assert.IsTrue(front.All(v => !v.IsAlive || v.Hp < v.MaxHp * 0.9f), "the tanks in the arc take the swing");
            Assert.IsTrue(behind.All(v => v.IsAlive && v.Hp >= v.MaxHp * 0.99f), "nothing behind it");
            world2.Bosses.Break(k2, k2.Def.PartIndex("boom"));
            world2.Bosses.TriggerBig(k2);
            var events = Run(world2, 8f);
            Assert.IsFalse(events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 1), "the boom broken: no more sweeps");
            // Its own route on the open-pit mine.
            var pit = new SimWorld(C, GameContent.LoadMap("openpit_sandbox"), 1);
            var k3 = pit.SpawnVehicle("kronos", 1, new Vector2(96f, 96f), 0f);
            Assert.IsNotNull(k3.OwnRoute, "Kronos follows the mine's kronos route");
        }

        [Test]
        public void IxionChargesDownItsLineAndABrokenWheelThrowsItOff()
        {
            var world = Field();
            var ixion = world.SpawnVehicle("ixion", 1, Vector2.Zero, 0f);
            ixion.Scripted = true;
            var line = Group(world, "light_tank", SimMath.Forward(ixion.Heading) * 30f, 2, 3f);
            world.Bosses.TriggerBig(ixion);
            var events = Run(world, 12f);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 1), "it charges");
            Assert.Greater(Vector2.Distance(ixion.Position, Vector2.Zero), 30f, "it has rolled down its line");
            Assert.IsTrue(line.All(v => !v.IsAlive || v.Hp < v.MaxHp), "the tanks on the line are hit");
            var world2 = Field(5);
            var i2 = world2.SpawnVehicle("ixion", 1, Vector2.Zero, 0f);
            i2.Scripted = true;
            Group(world2, "light_tank", SimMath.Forward(i2.Heading) * 30f, 2, 3f);
            world2.Bosses.TriggerBig(i2);
            Run(world2, 2f, () => i2.BigAttack.Stage == BigStage.Charging);
            Assert.AreEqual(BigStage.Charging, i2.BigAttack.Stage);
            world2.Bosses.Break(i2, i2.Def.PartIndex("wheel_l"));
            var e2 = Run(world2, 6f);
            Assert.IsTrue(e2.Any(e => e.Kind == SimEventKind.BigAttack && e.Mount == 2), "a big wheel broken in the warning: the charge is off");
            Assert.IsFalse(i2.IsCharging);
        }

        [Test]
        public void TyphonDivesOutOfReachSurfacesElsewhereAndStaysUpInPhaseThree()
        {
            var world = new SimWorld(C, GameContent.LoadMap("lighthousebay_sandbox"), 1) { RevealAll = true };
            var sea = world.Map.Sea!;
            var typhon = world.SpawnVehicle("typhon", 1, sea.At(-40f, sea.Lane("far")!.W), 0f);
            typhon.BigAttack.Off = true;
            Run(world, 60f, () => typhon.Burrowed);
            Assert.IsTrue(typhon.Burrowed, "it dives on its schedule");
            Assert.IsTrue(typhon.Invulnerable, "out of reach under water");
            var down = typhon.Position;
            Run(world, 40f, () => !typhon.Burrowed);
            Assert.IsFalse(typhon.Burrowed, "it surfaces");
            Assert.Greater(Vector2.Distance(down, typhon.Position), 20f, "somewhere else on the lane");
            world.Bosses.JumpPhase(typhon, 1);
            Run(world, 4f);
            world.Bosses.JumpPhase(typhon, 2);
            Run(world, 4f);
            Assert.AreEqual(2, typhon.Phase);
            Run(world, 60f);
            Assert.IsFalse(typhon.Burrowed, "phase 3: surfaced for good");
            Assert.IsFalse(typhon.Def.WakeMounts.Any(m => typhon.MountDormant[m]), "the deck gun woke with phase 3");
        }

        [Test]
        public void DaedalusMassDropFallsAsThreeWithABayGone()
        {
            var world = Field();
            var daedalus = world.SpawnVehicle("daedalus", 1, new Vector2(0f, 40f), 0f);
            Assert.AreEqual(AltitudeTier.Orbit, daedalus.Tier, "it opens in orbit");
            Group(world, "main_battle_tank", new Vector2(0f, -10f), 4, 20f);
            world.Bosses.JumpPhase(daedalus, 0);
            Run(world, 12f);
            Assert.AreNotEqual(AltitudeTier.Orbit, daedalus.Tier, "never back to orbit");
            world.Bosses.Break(daedalus, daedalus.Def.PartIndex("pod_bay_1"));
            world.Bosses.TriggerBig(daedalus);
            Run(world, 8f, () => daedalus.BigAttack.Stage == BigStage.Firing);
            Assert.AreEqual(3, daedalus.BigAttack.Rounds, "one bay gone: three pods fall, not six");
        }

        [Test]
        public void ArgusTightensItsSidesArtilleryUntilItsRadarBreaks()
        {
            var world = Field();
            Assert.AreEqual(1f, world.Bosses.SpotAuraFor(1), 1e-4f);
            var argus = world.SpawnVehicle("argus", 1, new Vector2(0f, 40f), 0f);
            Run(world, 1f);
            Assert.AreEqual(0.5f, world.Bosses.SpotAuraFor(1), 1e-4f, "its side's artillery falls half as wide");
            Assert.AreEqual(1f, world.Bosses.SpotAuraFor(0), 1e-4f, "not the other side's");
            world.Bosses.Break(argus, argus.Def.PartIndex("radar"));
            Run(world, 1f);
            Assert.AreEqual(1f, world.Bosses.SpotAuraFor(1), 1e-4f, "its radar broken: as usual");
        }

        [Test]
        public void TheSandboxCallsSwapRankMendPartsAndSendEscortsHome()
        {
            var world = Field();
            world.EscortSettings = EscortSettings.For(C.EscortRules, "Normal");
            var main = world.SpawnVehicle("behemoth", 1, new Vector2(0f, 40f), 0f);
            Run(world, 2f);
            Assert.Greater(world.EscortsAlive(main.Id), 0);
            world.Bosses.SetEscorts(main, false);
            Run(world, 1f);
            Assert.AreEqual(0, world.EscortsAlive(main.Id), "escorts off");
            var gun = main.Def.PartIndex("main_gun");
            world.Bosses.Break(main, gun);
            Assert.IsTrue(world.Bosses.Restore(main, gun));
            Assert.IsFalse(main.IsPartBroken(gun), "a part mended");
            main.Hp = main.MaxHp * 0.6f;
            var mini = world.Bosses.SwapRank(main);
            Assert.IsNotNull(mini);
            Assert.AreEqual("behemoth_mk2", mini.Def.Id, "the main boss for its mini version");
            Assert.AreEqual(0.6f, mini.Hp / mini.MaxHp, 0.01f, "at the same share of its health");
            Assert.AreEqual("behemoth", world.Bosses.SwapRank(mini).Def.Id, "and back");
        }

        [Test]
        public void EveryNewBossHasItsWords()
        {
            foreach (var id in NewBosses)
            {
                var def = C.Vehicle(id);
                foreach (var key in new[] { "unit." + id, "short." + id, "note." + id, "guide." + id, "guide.parts.tip." + id, def.RadioSpawn })
                    Assert.IsTrue(Strings.Has(key), $"{id}: text '{key}'");
                foreach (var p in def.Parts)
                {
                    Assert.IsTrue(Strings.Has("part." + p.Kind), $"{id}.{p.Id}: a word for '{p.Kind}'");
                    if (p.Radio != null) Assert.IsTrue(Strings.Has(p.Radio), $"{id}.{p.Id}: {p.Radio}");
                }
                if (def.Tiers != null)
                    foreach (var line in def.Tiers.Radio.Values) Assert.IsTrue(Strings.Has(line), $"{id}: {line}");
            }
            foreach (var b in C.Vehicles.Values.Where(v => v.Boss))
            {
                Assert.IsTrue(Strings.Has(b.RankDef.Label), b.Id + ": its bar's label");
                if (b.RadioSpawn != null) Assert.IsTrue(Strings.Has(b.RadioSpawn), b.Id + ": " + b.RadioSpawn);
                foreach (var ph in b.Phases)
                    if (ph.Radio != null) Assert.IsTrue(Strings.Has(ph.Radio), b.Id + ": " + ph.Radio);
            }
        }
    }
}
