using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 25 F.2 (task E2, DECISIONS 25E): the support value of a support vehicle, which the combat value misses (a
    /// repair truck deals no damage). One vehicle of the kind goes with an escort (two battle tanks, an IFV, an MLRS and an
    /// attack helicopter) led by the tactical AI against a group that fires guided missiles and direct fire (two BMPTs, a
    /// battle tank and an attack helicopter; a new wave 3 s after one falls), for 3 minutes on the open field. It records
    /// what it did for its side:
    /// - health repaired: every repair its side's vehicles got (the field has no other source: no base, no gear, no strikes);
    /// - ammunition resupplied, in rounds: part-empty magazines topped up, the share of an in-place reload it cut short
    ///   (as rounds of that magazine), and the stores an aircraft took on at it;
    /// - missiles decoyed: the enemy's guided rounds its jammer scrambled at launch (and all the enemy's guided rounds, for
    ///   the share);
    /// - shield damage blocked: what its dome took.
    /// Support value per CP = (health repaired + shield blocked + the damage of the rounds resupplied and of the missiles
    /// decoyed) x the survival factor ((1 + share of the time alive) / 2) / CP: the same scale as the combat value.
    /// </summary>
    public partial class CombatValueMeasure
    {
        private const float SupportSeconds = 180f;

        internal static readonly string[] SupportEscort = { "main_battle_tank", "main_battle_tank", "ifv", "mlrs", "attack_helicopter" };

        internal static readonly Scenario SupportThreat = new()
        {
            Name = "support", Group = new[] { "ifv", "ifv", "main_battle_tank", "attack_helicopter" }, Seconds = SupportSeconds,
        };

        internal sealed class SupportResult
        {
            public string Id;
            public int Cp;
            public float Repaired, Resupplied, ResuppliedDamage, Decoyed, DecoyedDamage, Guided, Shielded, Survival, Value;

            /// <summary>The share of the enemy's guided rounds it scrambled.</summary>
            public float DecoyShare => Guided > 0f ? Decoyed / Guided : 0f;
        }

        /// <summary>A vehicle whose worth is in what it does for others: a repair, rearm, jamming or shield aura.</summary>
        internal static bool Supporter(VehicleDef def) =>
            def.RepairAura != null || def.RearmAura != null || def.AirRearm != null || def.Jammer > 0f || def.Dome != null;

        /// <summary>The support run on its own (a short measurement for the test phase): MB_BALANCE=1, MB_CV_OUT, MB_CV_TAG, MB_CV_ONLY.</summary>
        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance")]
        public void MeasureTheSupportVehicles()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("support value: set MB_BALANCE=1");
            var catalog = LoadCatalog();
            var support = MeasureSupport(catalog);
            var text = SupportTsv(support.Values);
            WriteOut($"combat_value_{Tag}_support.tsv", text);
            TestContext.Out.WriteLine(text);
            UnityEngine.Debug.Log("[CombatValueMeasure.Support]\n" + text);
            Assert.Pass();
        }

        private static string Tag => Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now";

        private static void WriteOut(string name, string text)
        {
            var outDir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (string.IsNullOrEmpty(outDir)) outDir = Path.GetTempPath();
            Directory.CreateDirectory(outDir);
            File.WriteAllText(Path.Combine(outDir, name), text, new UTF8Encoding(false));
        }

        /// <summary>Every support vehicle of the roster, averaged over the seeds.</summary>
        internal static Dictionary<string, SupportResult> MeasureSupport(Catalog catalog)
        {
            var results = new Dictionary<string, SupportResult>();
            foreach (var id in Roster(catalog))
            {
                if (!Supporter(catalog.Vehicle(id))) continue;
                var runs = Seeds.Select(seed => RunSupport(catalog, id, seed)).ToList();
                results[id] = new SupportResult
                {
                    Id = id, Cp = runs[0].Cp,
                    Repaired = runs.Average(r => r.Repaired), Resupplied = runs.Average(r => r.Resupplied),
                    ResuppliedDamage = runs.Average(r => r.ResuppliedDamage), Decoyed = runs.Average(r => r.Decoyed),
                    DecoyedDamage = runs.Average(r => r.DecoyedDamage), Guided = runs.Average(r => r.Guided),
                    Shielded = runs.Average(r => r.Shielded), Survival = runs.Average(r => r.Survival), Value = runs.Average(r => r.Value),
                };
            }
            return results;
        }

        internal static SupportResult RunSupport(Catalog catalog, string id, int seed)
        {
            var def = catalog.Vehicle(id);
            var world = Field(catalog, seed);
            world.RevealAll = true;
            var supporter = world.SpawnVehicle(id, 0, new Vector2(0f, -52f), 0f);
            var escort = new List<Vehicle>();
            for (var i = 0; i < SupportEscort.Length; i++)
            {
                var flying = catalog.Vehicle(SupportEscort[i]).Flying;
                escort.Add(world.SpawnVehicle(SupportEscort[i], 0, new Vector2((i - (SupportEscort.Length - 1) * 0.5f) * 8f, flying ? -95f : -45f - (i % 2) * 4f), 0f));
            }
            var theirs = new List<Vehicle>();
            void SendWave()
            {
                var group = SupportThreat.Group;
                for (var i = 0; i < group.Length; i++)
                    theirs.Add(world.SpawnVehicle(group[i], 1, GroupAt + new Vector2((i - (group.Length - 1) * 0.5f) * 8f, (i % 2) * 5f), MathF.PI));
            }
            SendWave();
            var ai = new TacticalAi(0, 1) { Objective = _ => GroupAt };
            var result = new SupportResult { Id = id, Cp = def.CpCost };
            // What each escort weapon held before the step: rounds and the reload left.
            var ammoBefore = escort.Select(v => new int[v.Weapons.Length]).ToArray();
            var reloadBefore = escort.Select(v => new float[v.Weapons.Length]).ToArray();
            var alive = 0f;
            var waveDownAt = -1.0;
            for (var t = 0f; t < SupportSeconds; t += TestWorlds.Step)
            {
                for (var e = 0; e < escort.Count; e++)
                    for (var i = 0; i < escort[e].Weapons.Length; i++)
                    {
                        ammoBefore[e][i] = escort[e].Weapons[i].Ammo;
                        reloadBefore[e][i] = escort[e].Weapons[i].ReloadLeft;
                    }
                var still = escort.Select(v => v.StillForReload).ToArray();
                ai.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                foreach (var ev in world.Events)
                {
                    if (ev.Kind == SimEventKind.Repaired && ev.Team == 0) result.Repaired += ev.Value;
                    else if (ev.Kind == SimEventKind.DomeHit && ev.Team == 0) result.Shielded += ev.Value;
                    else if (ev.Kind == SimEventKind.WeaponFired && ev.Team == 1 && ev.DefId != null && catalog.Weapons.TryGetValue(ev.DefId, out var w) && w.Guided)
                    {
                        result.Guided++;
                        if (ev.Jammed)
                        {
                            result.Decoyed++;
                            result.DecoyedDamage += w.Damage;
                        }
                    }
                }
                world.ClearEvents();
                for (var e = 0; e < escort.Count; e++)
                {
                    var v = escort[e];
                    if (!v.IsAlive) continue;
                    for (var i = 0; i < v.Weapons.Length; i++)
                    {
                        var arm = v.Arm(i);
                        var was = ammoBefore[e][i];
                        var now = v.Weapons[i].Ammo;
                        var rounds = 0f;
                        if (v.Flying)
                        {
                            // An aircraft's stores come back one round at a time wherever it rearms; count them at the carrier.
                            if (v.RearmAt == RearmSite.AmmoCarrier && now > Math.Max(0, was)) rounds = now - Math.Max(0, was);
                        }
                        else if (was > 0 && now > was) rounds = now - was;   // a part-empty magazine topped up (only an ammunition aura does)
                        else if (was == 0 && now == 0 && reloadBefore[e][i] > 0f && arm.Ammo > 0)
                        {
                            // An empty magazine reloading in place: the time taken off beyond its own crew's is the carrier's.
                            var own = still[e] ? TestWorlds.Step * v.RankFire : 0f;
                            var cut = reloadBefore[e][i] - v.Weapons[i].ReloadLeft - own;
                            if (cut > 1e-4f) rounds = cut / MathF.Max(0.1f, arm.MagazineReload) * arm.Ammo;
                        }
                        if (rounds <= 0f) continue;
                        result.Resupplied += rounds;
                        result.ResuppliedDamage += rounds * arm.Damage;
                    }
                }
                if (supporter.IsAlive) alive += TestWorlds.Step;
                if (!supporter.IsAlive && escort.All(v => !v.IsAlive)) break;
                if (theirs.All(v => !v.IsAlive))
                {
                    if (waveDownAt < 0) waveDownAt = world.Time;
                    if (world.Time - waveDownAt > 3.0)
                    {
                        theirs.Clear();
                        SendWave();
                        waveDownAt = -1.0;
                    }
                }
            }
            result.Survival = alive;
            var total = result.Repaired + result.Shielded + result.ResuppliedDamage + result.DecoyedDamage;
            result.Value = total * (1f + alive / SupportSeconds) * 0.5f / MathF.Max(1, result.Cp);
            return result;
        }

        internal static string SupportTsv(IEnumerable<SupportResult> results)
        {
            var sb = new StringBuilder("id\tcp\trepaired\tresupplied\tresuppliedDamage\tdecoyed\tdecoyedDamage\tguided\tdecoyShare\tshielded\tsurvival\tsupport\n");
            foreach (var r in results)
                sb.AppendLine(string.Join("\t", r.Id, r.Cp, F(r.Repaired), F(r.Resupplied), F(r.ResuppliedDamage), F(r.Decoyed), F(r.DecoyedDamage),
                    F(r.Guided), F(r.DecoyShare), F(r.Shielded), F(r.Survival), F(r.Value)));
            return sb.ToString();
        }

        /// <summary>The summary's support columns for one vehicle (empty for a vehicle that is no supporter).</summary>
        internal static string SupportCells(IReadOnlyDictionary<string, SupportResult> support, string id) =>
            support != null && support.TryGetValue(id, out var r)
                ? string.Join("\t", F(r.Repaired), F(r.Resupplied), F(r.Decoyed), F(r.Shielded), F(r.Value))
                : "\t\t\t\t";
    }
}
