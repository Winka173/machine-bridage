using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The tower-branch rework (DECISIONS 19T, F): the branches measured where their mechanisms matter (the scenarios the
    /// ladder of <see cref="TowerValueMeasure"/> does not reach), and how often the AI picks each branch against the decks
    /// it meets. Run by name with MB_BALANCE=1 (MB_CV_OUT, MB_CV_TAG for the output).
    /// </summary>
    public class BranchMeasure
    {
        private const float Step = 0.05f;
        private static Catalog C => Lab.Catalog;

        private static void Gate()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("branch measurement: set MB_BALANCE=1");
        }

        private static void Write(string name, string text)
        {
            TestContext.Out.WriteLine(text);
            UnityEngine.Debug.Log($"[BranchMeasure.{name}]\n{text}");
            var dir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (!string.IsNullOrEmpty(dir)) File.WriteAllText(Path.Combine(dir, $"{name}_{Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now"}.txt"), text);
        }

        private static SimWorld Field(int seed)
        {
            var w = Lab.Field(seed, 300f);
            return w;
        }

        private static Vehicle Tower(SimWorld world, string id, int team, Vector2 at)
        {
            var v = world.SpawnVehicle(id, team, at, 0f);
            world.AnchorDefence(v);
            return v;
        }

        private static void Run(SimWorld world, float seconds, Action each = null)
        {
            for (var t = 0f; t < seconds; t += Step)
            {
                each?.Invoke();
                world.Step(Step);
                world.ClearEvents();
            }
        }

        /// <summary>
        /// Each mechanism's own fight, both branches of the tower, three seeds: the Patriot under missiles, the shield
        /// generator under focused and area fire, the CP relay quiet and under attack.
        /// </summary>
        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance"), Timeout(3600000)]
        public void PrintMechanismScenarios()
        {
            Gate();
            var sb = new StringBuilder("scenario\tbranch\tresult\n");
            var seeds = new[] { 13, 14, 15 };

            // The Patriot: a base (a gun turret and three tanks) under two ballistic launchers for 90 s: damage the base took.
            foreach (var b in new[] { "missile_battery.pac3", "missile_battery.lrr" })
            {
                var lost = seeds.Average(seed =>
                {
                    var world = Field(seed);
                    Tower(world, b, 0, new Vector2(0f, -10f));
                    var targets = new List<Vehicle> { Tower(world, "gun_turret", 0, Vector2.Zero) };
                    for (var i = 0; i < 3; i++)
                    {
                        var t = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-8f + i * 8f, 6f), 0f);
                        world.MakeSparring(t);
                        t.HoldFire = true;
                        targets.Add(t);
                    }
                    targets[0].HoldFire = true;
                    for (var i = 0; i < 2; i++)
                    {
                        var l = world.SpawnVehicle("ballistic_launcher", 1, new Vector2(-15f + i * 30f, 110f), MathF.PI);
                        world.MakeSparring(l);
                        world.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.Attack, 1, new[] { l.Id }, targets[i + 1].Position, targets[i + 1].Id));
                    }
                    var taken = 0f;
                    DamageSystem.DamageLog = (by, victim, amount, kind, weapon) => { if (victim.Team == 0) taken += amount; };
                    try { Run(world, 90f); }
                    finally { DamageSystem.DamageLog = null; }
                    return taken;
                });
                sb.AppendLine($"base under ballistic missiles (damage taken, lower is better)\t{b}\t{lost:0}");
            }

            // The shield generator: four gun turrets round it; (direct fire) three tanks, each on its own tower; (area fire) an
            // artillery barrage on the cluster every 8 s. The towers' health lost in 60 s.
            foreach (var area in new[] { false, true })
                foreach (var b in new[] { "shield_tower.bulwark", "shield_tower.ward" })
                {
                    var lost = seeds.Average(seed =>
                    {
                        var world = Field(seed);
                        Tower(world, b, 0, Vector2.Zero);
                        var towers = new List<Vehicle>();
                        foreach (var at in new[] { new Vector2(12f, 8f), new Vector2(-12f, 8f), new Vector2(12f, -8f), new Vector2(-12f, -8f) })
                        {
                            var t = Tower(world, "gun_turret", 0, at);
                            t.HoldFire = true;
                            towers.Add(t);
                        }
                        var tanks = area ? new List<Vehicle>() : Enumerable.Range(0, 3).Select(i =>
                        {
                            var e = world.SpawnVehicle("main_battle_tank", 1, new Vector2(-10f + i * 10f, 40f), MathF.PI);
                            world.MakeSparring(e);
                            return e;
                        }).ToList();
                        var start = towers.Sum(t => t.Hp);
                        var next = 0.0;
                        Run(world, 60f, () =>
                        {
                            if (world.Time < next) return;
                            if (area)
                            {
                                next = world.Time + 8.0;
                                world.Strikes.Launch(C.Supports["artillery_barrage"], 1, Vector2.Zero, new Vector2(1f, 0f));
                                return;
                            }
                            next = world.Time + 2.0;
                            for (var i = 0; i < tanks.Count; i++)
                            {
                                var aim = towers.Skip(i).Concat(towers).FirstOrDefault(t => t.IsAlive);
                                if (aim != null && tanks[i].IsAlive) world.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.Attack, 1, new[] { tanks[i].Id }, aim.Position, aim.Id));
                            }
                        });
                        return start - towers.Sum(t => t.IsAlive ? t.Hp : 0f);
                    });
                    sb.AppendLine($"shield generator, {(area ? "area fire: a barrage every 8 s" : "direct fire: three tanks, a tower each")} (towers' health lost, lower is better)	{b}	{lost:0}");
                }

            // The CP relay: CP its side made over 3 minutes, quiet, and with armoured cars driving at a gun turret beside it.
            foreach (var attacked in new[] { false, true })
                foreach (var b in new[] { "cp_relay.hardened", "cp_relay.loot" })
                {
                    var made = seeds.Average(seed =>
                    {
                        var world = Field(seed);
                        world.EnableEconomy(new TeamEconomy(0, 0f, income: 0f, bank: 9999f));
                        world.EnableEconomy(new TeamEconomy(1, 0f, income: 0f, bank: 9999f));
                        Tower(world, b, 0, Vector2.Zero);
                        var gun = Tower(world, "heavy_turret", 0, new Vector2(10f, 8f));
                        world.MakeSparring(gun);
                        world.TryGetEconomy(0, out var own);
                        var next = 5.0;
                        Run(world, 180f, () =>
                        {
                            if (!attacked || world.Time < next) return;
                            next = world.Time + 12.0;
                            for (var i = 0; i < 3; i++)
                            {
                                var car = world.SpawnVehicle("armored_car", 1, new Vector2(-10f + i * 10f, 60f), MathF.PI);
                                world.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.Attack, 1, new[] { car.Id }, gun.Position, gun.Id));
                            }
                        });
                        return own.Cp;
                    });
                    sb.AppendLine($"CP relay, {(attacked ? "attacked: 3 armoured cars every 12 s" : "quiet")} (CP made in 3 min, higher is better)\t{b}\t{made:0}");
                }
            // A rush past the tower (a gate, a corner): six armoured cars driving by within 8 m; damage the tower dealt.
            foreach (var b in new[] { "mg_bunker.twin", "mg_bunker.flame", "gun_turret.long", "gun_turret.auto" })
            {
                var dealt = seeds.Average(seed =>
                {
                    var world = Field(seed);
                    var tower = Tower(world, b, 0, Vector2.Zero);
                    var cars = Enumerable.Range(0, 6).Select(i => world.SpawnVehicle("armored_car", 1, new Vector2(3f + (i % 2) * 2f, 60f + i * 6f), MathF.PI)).ToList();
                    foreach (var car in cars) world.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.Move, 1, new[] { car.Id }, new Vector2(car.Position.X, -60f)));
                    var sum = 0f;
                    DamageSystem.DamageLog = (by, victim, amount, kind, weapon) => { if (by == tower && victim.Team == 1) sum += amount; };
                    try { Run(world, 30f); }
                    finally { DamageSystem.DamageLog = null; }
                    return sum;
                });
                sb.AppendLine($"a rush past the tower: six armoured cars within 5 m (damage dealt, higher is better)	{b}	{dealt:0}");
            }

            // Guns standing at 70 m (artillery out past most towers' reach): damage the tower dealt them in 60 s.
            foreach (var b in new[] { "heavy_turret.coastal", "heavy_turret.bastion", "rocket_turret.guided", "rocket_turret.cluster", "gun_turret.long", "gun_turret.auto" })
            {
                var dealt = seeds.Average(seed =>
                {
                    var world = Field(seed);
                    var tower = Tower(world, b, 0, Vector2.Zero);
                    foreach (var (id, x) in new[] { ("artillery", -10f), ("mlrs", 0f), ("artillery", 10f) })
                    {
                        var g = world.SpawnVehicle(id, 1, new Vector2(x, 70f), MathF.PI);
                        g.Scripted = true;
                        g.HoldFire = true;
                        g.HpScale = 20f;
                        g.Hp = g.MaxHp;
                    }
                    var sum = 0f;
                    DamageSystem.DamageLog = (by, victim, amount, kind, weapon) => { if (by == tower && victim.Team == 1) sum += amount; };
                    try { Run(world, 60f); }
                    finally { DamageSystem.DamageLog = null; }
                    return sum;
                });
                sb.AppendLine($"guns standing at 70 m (damage dealt in 60 s, higher is better)	{b}	{dealt:0}");
            }
            Write("branch_scenarios", sb.ToString());
        }

        /// <summary>
        /// F.3: how often the AI's branch choice takes each branch, over the decks it meets: the enemy decks drawn for 40
        /// seeds at Normal, Hard and Very Hard, and the player's sample deck, each general's style in turn.
        /// </summary>
        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance")]
        public void PrintAiBranchPicks()
        {
            Gate();
            var pool = C.Vehicles.Values.Where(v => v.Card && v.CpCost > 0 && !v.Boss && !v.Static && !v.Elite).Select(v => v.Id).ToList();
            var decks = new List<IReadOnlyList<string>> { ModeBalanceMeasure.SampleDeck };
            foreach (var difficulty in new[] { AiDifficulty.Normal, AiDifficulty.Hard, AiDifficulty.VeryHard })
                for (var seed = 1; seed <= 40; seed++)
                    decks.Add(ConquestAi.PickDeck(C, pool, difficulty, seed));
            var styles = new[] { "default", "varga", "orlov", "kessler", "sen", "quaden", "aurel" };
            var towers = TowerCards.All(C).Where(t => TowerCards.Branches(C, t).Count > 0).ToList();
            var counts = new Dictionary<string, int>();
            var k = 0;
            foreach (var deck in decks)
            {
                var style = C.Base.Style(styles[k++ % styles.Length]);
                var loadout = new BaseLoadout { HqLevel = 5 };
                loadout.Large.AddRange(towers);
                BaseLoadout.ChooseAiBranches(C, loadout, deck.ToList(), style);
                foreach (var (_, b) in loadout.Branches) counts[b] = counts.GetValueOrDefault(b) + 1;
            }
            var sb = new StringBuilder($"AI branch picks over {decks.Count} decks (share of the tower's picks)\n");
            foreach (var t in towers)
                sb.AppendLine($"{t,-22} " + string.Join("  ", TowerCards.Branches(C, t).Select(b => $"{b.Substring(t.Length + 1)} {counts.GetValueOrDefault(b) * 100f / decks.Count:0}%")));
            Write("branch_picks", sb.ToString());
        }
    }
}
