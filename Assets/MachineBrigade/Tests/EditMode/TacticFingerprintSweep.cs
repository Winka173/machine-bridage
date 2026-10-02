using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 28 H.3 and O.5, written in the cloud session, not yet run. (1) Each tactic's behaviour fingerprint (the
    /// sheet "Dấu vân hành vi": engagement distance, squad spread, flank time, artillery and air CP shares, first attack,
    /// hold-fire time, force concentration) over 5 seeds of AI-versus-AI Conquest against Balanced, normalised 0-1, and
    /// every pair's distance; pairs under ai merge threshold (0.15) are the merge candidates (the sheet's "Cặp cần kiểm
    /// tra gộp" first). Writes Docs/ai/fingerprints.csv. (2) The whole campaign at Normal over 5 seeds with Balanced and
    /// three other tactics; logs the wins per mission and tactic.
    /// </summary>
    public class TacticFingerprintSweep
    {
        private const string Why = "a measurement: run it by name with MB_BALANCE=1 once the owner allows the runs";
        private const float Step = 0.05f;
        private const int Seeds = 5;

        private static string Env(string key, string fallback) => Environment.GetEnvironmentVariable(key) is { Length: > 0 } v ? v : fallback;

        public static readonly string[] Metrics =
            { "engageShare", "squadSpread", "flankShare", "artilleryCp", "airCp", "firstAttack", "holdShare", "concentration" };

        [Test, Explicit(Why), Category("Balance"), Timeout(int.MaxValue)]
        public void FingerprintEveryTacticAndListMergeCandidates()
        {
            var catalog = GameContent.LoadCatalog();
            var map = Env("MB_SWEEP_MAPS", "ashfield");
            var minutes = float.Parse(Env("MB_SWEEP_MINUTES", "10"), System.Globalization.CultureInfo.InvariantCulture);
            var prints = new Dictionary<string, double[]>();
            foreach (var t in catalog.AiData.Tactics)
            {
                var sum = new double[Metrics.Length];
                for (var seed = 0; seed < Seeds; seed++)
                {
                    var m = Fingerprint(map, 200 + seed, minutes, t.Id);
                    for (var i = 0; i < sum.Length; i++) sum[i] += m[i] / Seeds;
                }
                prints[t.Id] = sum;
                Debug.Log($"AI28 fingerprint {t.Id}: {string.Join(", ", Metrics.Select((n, i) => $"{n} {sum[i]:0.###}"))}");
            }
            // Normalise each metric to 0-1 across the tactics (min-max), then the pair distances (RMS over the metrics).
            var ids = prints.Keys.ToList();
            for (var i = 0; i < Metrics.Length; i++)
            {
                var min = ids.Min(id => prints[id][i]);
                var max = ids.Max(id => prints[id][i]);
                foreach (var id in ids) prints[id][i] = max > min ? (prints[id][i] - min) / (max - min) : 0.0;
            }
            var threshold = catalog.Ai.Get("world.mergeThreshold", 0.15f);
            var csv = new StringBuilder("tactic," + string.Join(",", Metrics) + "\n");
            foreach (var id in ids) csv.Append(id).Append(',').Append(string.Join(",", prints[id].Select(x => x.ToString("0.###")))).Append('\n');
            csv.Append("\npair,distance,checkWith,merge\n");
            for (var a = 0; a < ids.Count; a++)
            for (var b = a + 1; b < ids.Count; b++)
            {
                var d = Math.Sqrt(Enumerable.Range(0, Metrics.Length).Sum(i => Math.Pow(prints[ids[a]][i] - prints[ids[b]][i], 2)) / Metrics.Length);
                var check = catalog.AiData.Tactic(ids[a]).CheckWith == ids[b] || catalog.AiData.Tactic(ids[b]).CheckWith == ids[a];
                csv.Append($"{ids[a]}-{ids[b]},{d:0.###},{(check ? "sheet" : "")},{(d < threshold ? "candidate" : "")}\n");
            }
            var output = Env("MB_SWEEP_OUT", Path.Combine(Application.dataPath, "..", "Docs", "ai", "fingerprints.csv"));
            File.WriteAllText(output, csv.ToString());
            Debug.Log($"AI28 fingerprints written to {output}");
        }

        /// <summary>One battle of <paramref name="tactic"/> (team 0) against Balanced; its 8 fingerprint numbers.</summary>
        private static double[] Fingerprint(string map, int seed, float minutes, string tactic)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map + "_conquest"), seed: seed);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles, PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles, EnemySupports = MatchSettings.AllSupports,
            });
            mode.Setup(world);
            world.Intel.Objectives = mode;
            var a = new ConquestAi(mode, 0, 1, AiDifficulty.Normal, seed + 1) { Tactic = tactic };
            var b = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, seed + 2) { Tactic = "balanced" };
            double engage = 0, engageN = 0, spread = 0, spreadN = 0, flank = 0, squads = 0, hold = 0, primary = 0;
            var firstAttack = minutes * 60.0;
            for (var t = 0f; t < minutes * 60f && mode.Result == null; t += Step)
            {
                mode.Tick(world, Step);
                a.Tick(world, Step);
                b.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
                if (world.Tick % 20 != 0 || a.Commander == null) continue;
                foreach (var v in world.VehicleList)
                    if (v.IsAlive && v.Team == 0 && world.TryGetVehicle(v.Target, out var target) && v.Def.Weapon.Range > 0f)
                    {
                        engage += Vector2.Distance(v.Position, target.Position) / v.Def.Weapon.Range;
                        engageN++;
                    }
                foreach (var s in a.Commander.Squads.Squads)
                {
                    squads++;
                    if (s.State == SquadState.Flank) flank++;
                    if (s.State == SquadState.Hold && s.Members.Any(id => world.TryGetVehicle(id, out var m) && m.AiHoldFire)) hold++;
                    if (s.Task.Kind == TaskKind.Primary) primary++;
                    if (s.State == SquadState.Combat)
                    {
                        spread += s.Spread;
                        spreadN++;
                    }
                }
                if (firstAttack >= minutes * 60.0 && a.Commander.Intent.AttackWindow) firstAttack = world.Time;
            }
            var spent = a.Commander?.Spent.Sum() ?? 0f;
            double Share(ForceGroup g) => spent > 0f ? a.Commander.Spent[(int)g] / spent : 0.0;
            return new[]
            {
                engageN > 0 ? engage / engageN : 0, spreadN > 0 ? spread / spreadN : 0, squads > 0 ? flank / squads : 0,
                Share(ForceGroup.Artillery), Share(ForceGroup.Helicopter) + Share(ForceGroup.Plane), firstAttack,
                squads > 0 ? hold / squads : 0, squads > 0 ? primary / squads : 0,
            };
        }

        [Test, Explicit(Why), Category("Balance"), Timeout(int.MaxValue)]
        public void TheWholeCampaignIsWinnableAtNormalWithBalancedAndThreeOtherTactics()
        {
            var tactics = Env("MB_SWEEP_TACTICS", "balanced,blitz,depth,firepower").Split(',');
            var log = new StringBuilder();
            var unwinnable = new List<string>();
            foreach (var mission in Campaign.All)
            {
                if (!Campaign.MapExists(mission)) continue;
                foreach (var tactic in tactics)
                {
                    var wins = 0;
                    for (var seed = 0; seed < Seeds; seed++)
                        if (Play(mission, 300 + seed, tactic.Trim())) wins++;
                    log.AppendLine($"{mission.Id} {tactic}: {wins}/{Seeds}");
                    if (wins == 0) unwinnable.Add($"{mission.Id} {tactic}");
                }
            }
            Debug.Log("AI28 campaign sweep:\n" + log);
            var balancedFails = unwinnable.Where(u => u.EndsWith(" balanced")).ToList();
            Assert.That(balancedFails, Is.Empty, "every mission is won at least once in 5 seeds with Balanced");
            var perMission = Campaign.All.Where(Campaign.MapExists).Select(m => tactics.Count(t => !unwinnable.Contains($"{m.Id} {t.Trim()}")));
            Assert.That(perMission.All(n => n >= 4), Is.True, "and with at least three other tactics:\n" + string.Join("\n", unwinnable));
        }

        private static bool Play(MissionDef def, int seed, string tactic)
        {
            var catalog = GameContent.LoadCatalog();
            CampaignTests.PlayerAt(def, catalog);
            var world = new SimWorld(catalog, Campaign.LoadMap(def), seed: seed);
            var session = (MissionSession)ModeSession.Create(GameModeKind.Campaign, false, world, seed);
            if (session.PlayerAi != null)
            {
                session.PlayerAi.Tactic = tactic;
                session.PlayerAi.Skill = AiSkill.For(AiDifficulty.Normal, catalog.Ai);
            }
            var cap = def.Operation ? 34f : def.TimeLimit > 0f ? def.TimeLimit / 60f + 1f : 22f;
            for (var t = 0f; t < cap * 60f && session.Mode.Result == null; t += Step)
            {
                session.Mode.Tick(world, Step);
                session.TickAi(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            return session.Mode.Result?.WinningTeam == 0;
        }
    }
}
