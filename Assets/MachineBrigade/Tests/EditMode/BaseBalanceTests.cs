using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Base balance (the sized-slot prompt and prompt 3): a level-5 base, its towers and HQ alone,
    /// against five kinds of attacking army of about the same CP, over seeds. A base scores its HQ's
    /// health left plus the share of the attackers it destroyed (0-2). Run by hand with
    /// MB_BALANCE=1: they take a while.
    /// </summary>
    public class BaseBalanceTests
    {
        private static void Gate()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance measurement: set MB_BALANCE=1 to run it");
        }

        /// <summary>The attacking armies, about 45-50 CP each.</summary>
        internal static readonly Dictionary<string, string[]> Enemies = new()
        {
            ["mixed"] = new[] { "main_battle_tank", "main_battle_tank", "ifv", "heavy_tank", "mlrs", "aa_vehicle", "attack_helicopter" },
            ["armour"] = new[] { "main_battle_tank", "main_battle_tank", "main_battle_tank", "heavy_tank", "heavy_tank", "tank_destroyer" },
            ["light+drones"] = new[] { "armored_car", "armored_car", "armored_car", "armored_car", "scout_jeep", "scout_jeep", "fpv_carrier", "fpv_carrier", "lancet_truck", "strike_drone", "wheeled_gun" },
            ["artillery"] = new[] { "mlrs", "mlrs", "artillery", "artillery", "heavy_rocket_artillery", "main_battle_tank", "main_battle_tank" },
            ["air"] = new[] { "attack_helicopter", "attack_helicopter", "gunship_heli", "attack_jet" },
        };

        /// <summary>A mixed base of all three sizes (the default a player starts with, and what the tests compare with).</summary>
        internal static BaseLoadout Mixed() => new()
        {
            HqLevel = 5,
            Small = { "guard_tower", "aa_turret", "mg_bunker", "ew_tower", "aa_turret", "guard_tower" },
            Medium = { "gun_turret", "atgm_tower", "c_ram" },
            Large = { "artillery_emplacement", "missile_battery" },
        };

        /// <summary>Every slot a tower fits filled with that one tower (a medium tower leaves the small slots empty).</summary>
        internal static BaseLoadout OnlyOf(Catalog catalog, string tower)
        {
            var b = new BaseLoadout { HqLevel = 5 };
            foreach (SlotSize size in Enum.GetValues(typeof(SlotSize)))
                if (catalog.Vehicles[tower].Fort.Fits(size))
                    for (var k = 0; k < catalog.Base.Slots(5, size); k++) b.Of(size).Add(tower);
            return b;
        }

        /// <summary>One battle: the defence at side 1's camp of Ashfield, the army at side 0's rally going for the HQ.</summary>
        internal static float Score(Catalog catalog, BaseLoadout defence, string[] army, int seed, float minutes = 5f) =>
            Battle(catalog, defence, army, seed, minutes, out _);

        /// <summary>One battle (see <see cref="Score"/>), and the share of the base's towers the attackers knocked down.</summary>
        internal static float Battle(Catalog catalog, BaseLoadout defence, string[] army, int seed, float minutes, out float towersDown)
        {
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: seed);
            var b = world.Bases.Establish(1, defence, BaseRole.Target);
            world.TryGetRally(0, out var start);
            var toward = Vector2.Normalize(b.HqPosition - start);
            var side = new Vector2(-toward.Y, toward.X);
            var attackers = new List<Vehicle>();
            for (var i = 0; i < army.Length; i++)
                attackers.Add(world.SpawnVehicle(army[i], 0, world.ClampToMap(start + side * ((i % 5) - 2) * 5f - toward * (i / 5) * 6f), SimMath.HeadingOf(toward)));
            var cp = attackers.Sum(v => v.Def.CpCost);
            var ai = new TacticalAi(0, 1, seed) { Objective = _ => b.HqPosition };
            world.TryGetVehicle(b.Hq, out var hq);
            for (var t = 0f; t < minutes * 60f && hq.IsAlive && attackers.Any(v => v.IsAlive); t += TestWorlds.Step)
            {
                ai.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            var killed = attackers.Where(v => !v.IsAlive).Sum(v => v.Def.CpCost) / (float)Math.Max(1, cp);
            var standing = b.Slots.Count(s => s.Tower != null);
            towersDown = standing > 0 ? b.Slots.Count(s => s.Tower != null && s.Down) / (float)standing : 0f;
            if (Verbose)
                Debug.Log($"BATTLE seed {seed}: HQ {(hq.IsAlive ? hq.Hp / hq.MaxHp : 0f):P0}, towers left {b.Slots.Count(s => s.Tower != null && !s.Down)}/{b.Slots.Count(s => s.Tower != null)}, " +
                          $"attackers lost {killed:P0}, closest to HQ {attackers.Where(v => v.IsAlive).Select(v => Vector2.Distance(v.Position, b.HqPosition)).DefaultIfEmpty(-1f).Min():0} m, time {world.Time / 60f:0.0} min");
            return (hq.IsAlive ? hq.Hp / hq.MaxHp : 0f) + killed;
        }

        internal static bool Verbose;

        private static float Mean(Catalog catalog, BaseLoadout defence, string[] army, int seeds) =>
            Enumerable.Range(1, seeds).Average(s => Score(catalog, defence, army, s));

        private static readonly string[] Weaponed =
            { "guard_tower", "mg_bunker", "aa_turret", "gun_turret", "atgm_tower", "rocket_turret", "c_ram", "gun_pit", "artillery_emplacement", "missile_battery", "drone_hangar", "heavy_turret" };

        [Test, Category("Balance")]
        public void AMixedBaseIsBestAgainstAMixedArmyAndNoOneTowerBaseBeatsEverything()
        {
            Gate();
            var catalog = GameContent.LoadCatalog();
            var bases = new Dictionary<string, BaseLoadout> { ["mixed"] = Mixed() };
            foreach (var t in Weaponed) bases["only " + t] = OnlyOf(catalog, t);
            var table = new Dictionary<(string b, string e), float>();
            foreach (var (name, loadout) in bases)
                foreach (var (enemy, army) in Enemies)
                    table[(name, enemy)] = Mean(catalog, loadout, army, 5);
            var report = new StringBuilder("BASES score (HQ left + share destroyed, 0-2), 5 seeds\n");
            report.Append("base".PadRight(30)).Append(string.Join("", Enemies.Keys.Select(k => k.PadLeft(14)))).Append('\n');
            foreach (var name in bases.Keys)
                report.Append(name.PadRight(30)).Append(string.Join("", Enemies.Keys.Select(e => table[(name, e)].ToString("0.00").PadLeft(14)))).Append('\n');
            Debug.Log(report.ToString());
            var mixedScore = table[("mixed", "mixed")];
            foreach (var name in bases.Keys.Where(n => n != "mixed"))
                Assert.GreaterOrEqual(mixedScore + 0.05f, table[(name, "mixed")], $"the mixed base beats {name} against a mixed army");
            foreach (var name in bases.Keys.Where(n => n != "mixed"))
                Assert.IsTrue(Enemies.Keys.Any(e => bases.Keys.Any(o => o != name && table[(o, e)] > table[(name, e)])),
                    $"{name} is not the best base against every army");
        }

        [Test, Category("Balance")]
        public void AFastLightSwarmWithDronesOverwhelmsABaseOfOnlyHeavyGuns()
        {
            Gate();
            var catalog = GameContent.LoadCatalog();
            var heavy = new BaseLoadout { HqLevel = 5, Medium = { "gun_turret", "gun_turret", "rocket_turret" }, Large = { "heavy_turret", "artillery_emplacement" } };
            var army = Enemies["light+drones"];
            float heavyDown = 0f, mixedDown = 0f, heavyScore = 0f, mixedScore = 0f;
            Verbose = true;
            for (var seed = 1; seed <= 5; seed++)
            {
                heavyScore += Battle(catalog, heavy, army, seed, 8f, out var h) / 5f;
                heavyDown += h / 5f;
                mixedScore += Battle(catalog, Mixed(), army, seed, 8f, out var m) / 5f;
                mixedDown += m / 5f;
            }
            Verbose = false;
            Debug.Log($"SWARM vs medium+large only: towers down {heavyDown:P0}, score {heavyScore:0.00}; vs mixed: towers down {mixedDown:P0}, score {mixedScore:0.00}");
            Assert.GreaterOrEqual(heavyDown, 0.6f, "the swarm overwhelms a base of only medium and large guns: most of its towers fall");
            Assert.Less(mixedDown, heavyDown, "a base with light towers loses fewer to it");
            Assert.Greater(mixedScore, heavyScore, "and holds better");
        }

        /// <summary>
        /// Which towers an optimiser picks: for each army, one pass of per-slot coordinate search
        /// from the mixed base (large, then medium, then small slots), 2 seeds a try; the rate each
        /// tower is chosen across the five armies' best bases.
        /// </summary>
        [Test, Category("Balance")]
        public void TowerPickRates()
        {
            Gate();
            var catalog = GameContent.LoadCatalog();
            var towers = TowerCards.All(catalog);
            var picks = new Dictionary<string, int>();
            var slots = 0;
            var log = new StringBuilder("PICKS\n");
            foreach (var (enemy, army) in Enemies)
            {
                var best = Mixed();
                var bestScore = Mean(catalog, best, army, 2);
                foreach (var size in new[] { SlotSize.Large, SlotSize.Medium, SlotSize.Small })
                    for (var k = 0; k < catalog.Base.Slots(5, size); k++)
                        foreach (var t in towers.Where(t => catalog.Vehicles[t].Fort.Fits(size)))
                        {
                            if (best.Of(size)[k] == t) continue;
                            var trial = best.Clone();
                            trial.Of(size)[k] = t;
                            var s = Mean(catalog, trial, army, 2);
                            if (s <= bestScore) continue;
                            best = trial;
                            bestScore = s;
                        }
                log.Append($"{enemy}: {bestScore:0.00} L[{string.Join(",", best.Large)}] M[{string.Join(",", best.Medium)}] S[{string.Join(",", best.Small)}]\n");
                foreach (var t in best.Towers)
                {
                    picks[t] = picks.TryGetValue(t, out var n) ? n + 1 : 1;
                    slots++;
                }
            }
            log.Append("rates: ").Append(string.Join(", ", towers.Select(t => $"{t} {(picks.TryGetValue(t, out var n) ? n : 0) * 100f / slots:0}%")));
            Debug.Log(log.ToString());
            Assert.Greater(slots, 0);
        }

        /// <summary>
        /// A tower against vehicles worth what its size is worth (small 5 CP, medium 8, large 12),
        /// five seeds each: how often the tower holds (stands at the end).
        /// </summary>
        [Test, Category("Balance")]
        public void TowerAgainstVehiclesOfEqualValue()
        {
            Gate();
            var catalog = GameContent.LoadCatalog();
            var armies = new Dictionary<SlotSize, string[][]>
            {
                [SlotSize.Small] = new[] { new[] { "armored_car", "scout_jeep" }, new[] { "light_tank" }, new[] { "ifv" } },
                [SlotSize.Medium] = new[] { new[] { "main_battle_tank" }, new[] { "armored_car", "armored_car", "scout_jeep" }, new[] { "ifv", "scout_jeep" } },
                [SlotSize.Large] = new[] { new[] { "heavy_tank", "scout_jeep" }, new[] { "main_battle_tank", "ifv" }, new[] { "mlrs", "artillery" } },
            };
            var report = new StringBuilder("TOWER vs equal value (holds out of 15)\n");
            foreach (var t in Weaponed)
            {
                var size = catalog.Vehicles[t].Fort.Size;
                var holds = 0;
                foreach (var army in armies[size])
                    for (var seed = 1; seed <= 5; seed++)
                    {
                        var world = new SimWorld(catalog, new MapDefinition("field", 200f,
                            new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                            new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);
                        var tower = world.SpawnVehicle(t, 1, new Vector2(0f, 0f), MathF.PI);
                        world.AnchorDefence(tower);
                        tower.VisibleToMask |= 1;
                        var vehicles = army.Select((id, i) => world.SpawnVehicle(id, 0, new Vector2(-6f + i * 6f, -70f), 0f)).ToList();
                        var ai = new TacticalAi(0, 1, seed) { Objective = _ => tower.Position };
                        for (var s = 0f; s < 180f && tower.IsAlive && vehicles.Any(v => v.IsAlive); s += TestWorlds.Step)
                        {
                            ai.Tick(world, TestWorlds.Step);
                            world.Step(TestWorlds.Step);
                            world.ClearEvents();
                        }
                        if (tower.IsAlive) holds++;
                    }
                report.Append($"{t} ({size}): {holds}/15\n");
            }
            Debug.Log(report.ToString());
        }

        /// <summary>An airfield keeps aircraft flying, not parked: over five battles they spend most of their time away from it, and still get shot down.</summary>
        [Test, Category("Balance")]
        public void TheAirfieldDoesNotMakeAircraftImmortal()
        {
            Gate();
            var catalog = GameContent.LoadCatalog();
            var atField = 0;
            var aloft = 0;
            var lost = 0;
            for (var seed = 1; seed <= 5; seed++)
            {
                var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: seed);
                var loadout = Mixed();
                loadout.Utilities.Add("airfield");
                var deck = new[] { "main_battle_tank", "ifv", "attack_helicopter", "gunship_heli", "aa_vehicle", "mlrs" };
                var mode = new ConquestMode(new ConquestRules
                {
                    Bases = new BaseSetup().Set(0, loadout, BaseRole.Anchor).Set(1, loadout.Clone(), BaseRole.Anchor),
                    PlayerVehicles = deck, EnemyVehicles = deck, PlayerSupports = Array.Empty<string>(), EnemySupports = Array.Empty<string>(),
                });
                mode.Setup(world);
                var ais = new[] { new ConquestAi(mode, 0, 1, AiDifficulty.Hard, seed), new ConquestAi(mode, 1, 0, AiDifficulty.Hard, seed + 3) };
                var fields = world.VehicleList.Where(v => v.Def.Id == "airfield").ToList();
                for (var i = 0; i < 8 * 60 * 20 && !world.IsOver; i++)
                {
                    mode.Tick(world, TestWorlds.Step);
                    foreach (var ai in ais) ai.Tick(world, TestWorlds.Step);
                    world.Step(TestWorlds.Step);
                    foreach (var e in world.Events)
                        if (e.Kind == Sim.Events.SimEventKind.VehicleDestroyed && e.DefId != null && catalog.Vehicles.TryGetValue(e.DefId, out var d) && d.Flying) lost++;
                    world.ClearEvents();
                    if (i % 20 != 0) continue;
                    foreach (var v in world.VehicleList)
                    {
                        if (!v.IsAlive || !v.Flying) continue;
                        aloft++;
                        if (fields.Any(f => f.Team == v.Team && Vector2.Distance(f.Position, v.Position) < 20f)) atField++;
                    }
                }
            }
            var share = aloft > 0 ? atField / (float)aloft : 0f;
            Debug.Log($"AIRFIELD aircraft at the airfield {share:P0} of their time, {lost} shot down over 5 battles");
            Assert.Less(share, 0.4f, "aircraft spend most of their time in the fight");
            Assert.Greater(lost, 0, "and still get shot down");
        }
    }
}
