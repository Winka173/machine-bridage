using System;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Siege and Defend played whole on Normal over five seeds (each on another battlefield), both
    /// sides by their commanders, the player's by its auto commander (run by hand with
    /// MB_BALANCE=1: it takes a few minutes). Siege: the auto commander breaks the fortress in most
    /// seeds within the time bank; Defend: it holds. Neither lasts more than 25 minutes.
    /// </summary>
    public class SiegeBalanceTests
    {
        private static readonly string[] Battlefields = { "ashfield", "dunebreak", "ironport", "redrock", "metrocity" };

        private static (int wins, string text, float longest) Play(GameModeKind kind)
        {
            var wins = 0;
            var text = "";
            var longest = 0f;
            for (var seed = 1; seed <= 5; seed++)
            {
                MatchSettings.Mode = kind;
                MatchSettings.Difficulty = Sim.AI.AiDifficulty.Normal;
                var map = Battlefields[seed - 1];
                var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(ModeSession.MapFile(kind, map)), seed: seed);
                var session = ModeSession.Create(kind, false, world, seed);
                var mode = (SiegeMode)session.Mode;
                var t = 0f;
                var stages = "";
                var stage = mode.Stage;
                for (; t < 26f * 60f && mode.Result == null; t += 0.05f)
                {
                    session.Mode.Tick(world, 0.05f);
                    session.TickAi(world, 0.05f);
                    world.Step(0.05f);
                    world.ClearEvents();
                    if (mode.Stage == stage) continue;
                    stage = mode.Stage;
                    stages += $" {stage}@{t / 60f:0.0}";
                }
                var won = mode.Result?.WinningTeam == 0;
                if (won) wins++;
                longest = Mathf.Max(longest, t / 60f);
                text += $"\n  s{seed} {map}: {(mode.Result == null ? "open" : won ? "WON" : "LOST")} in {t / 60f:0.0} min, progress {mode.Progress(world):P0}," +
                        $" stages{stages}, waves {mode.Wave}, super-gun {(mode.SuperGunDown ? "destroyed" : $"{mode.SuperGunShots} shells")}," +
                        $" arrivals {mode.Arrivals}, gates down {mode.Gates.Count - CountStanding(world, mode)}/{mode.Gates.Count}, losses {mode.Losses}, kills {mode.Kills}";
            }
            return (wins, text, longest);
        }

        private static int CountStanding(SimWorld world, SiegeMode mode)
        {
            var n = 0;
            foreach (var (id, _, _) in mode.Gates)
                if (world.TryGetProp(id, out var g) && g.IsAlive) n++;
            return n;
        }

        [Category("Balance")]
        [Test]
        public void SiegeIsWinnableOnNormal()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance check: set MB_BALANCE=1 to run it");
            var (wins, text, longest) = Play(GameModeKind.Siege);
            Debug.Log($"SIEGE BALANCE: {wins}/5 won, longest {longest:0.0} min{text}");
            Assert.GreaterOrEqual(wins, 3, $"the auto commander breaks the fortress in most seeds:{text}");
            Assert.LessOrEqual(longest, 25f, $"no siege lasts more than 25 minutes:{text}");
        }

        [Category("Balance")]
        [Test]
        public void DefendIsHeldOnNormal()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance check: set MB_BALANCE=1 to run it");
            var (wins, text, longest) = Play(GameModeKind.Defend);
            Debug.Log($"DEFEND BALANCE: {wins}/5 held, longest {longest:0.0} min{text}");
            Assert.GreaterOrEqual(wins, 4, $"the auto commander holds:{text}");
            Assert.LessOrEqual(longest, 25f, $"no defence lasts more than 25 minutes:{text}");
        }
    }
}
