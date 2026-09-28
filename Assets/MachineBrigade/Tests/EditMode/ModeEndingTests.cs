using System;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Every mode still comes to an end with bases in play, over five seeds, both sides played by
    /// their commanders (run by hand with MB_BALANCE=1: it takes a while). Timed modes must end on
    /// their clock (plus overtime); the rest within a generous cap.
    /// </summary>
    public class ModeEndingTests
    {
        private static readonly (GameModeKind kind, string map, float capMinutes)[] Modes =
        {
            (GameModeKind.Conquest, "ashfield", 30f),
            (GameModeKind.Deathmatch, "greenvale", 14f),
            (GameModeKind.KingOfTheHill, "dunebreak", 17f),
            (GameModeKind.Assault, "redrock", 16f),
            (GameModeKind.Siege, "ashfield", 26f),
            (GameModeKind.Defend, "greenvale", 22f),
            (GameModeKind.Endless, "ironport", 40f),
            (GameModeKind.Survival, "frostpeak", 40f),
            (GameModeKind.BossRush, "ashfield", 28f),
        };

        private static string[] Names() => Array.ConvertAll(Modes, m => m.kind.ToString());

        [Category("Balance")]
        [TestCaseSource(nameof(Names))]
        public void EndsWithinItsTime(string name)
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance check: set MB_BALANCE=1 to run it");
            var (kind, map, cap) = Array.Find(Modes, m => m.kind.ToString() == name);
            var text = "";
            var ended = 0;
            for (var seed = 1; seed <= 5; seed++)
            {
                MatchSettings.Mode = kind;
                MatchSettings.Difficulty = Sim.AI.AiDifficulty.Normal;
                var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(ModeSession.MapFile(kind, map)), seed: seed);
                var session = ModeSession.Create(kind, false, world, seed);
                var t = 0f;
                for (; t < cap * 60f && session.Mode.Result == null; t += 0.05f)
                {
                    session.Mode.Tick(world, 0.05f);
                    session.TickAi(world, 0.05f);
                    world.Step(0.05f);
                    world.ClearEvents();
                }
                var result = session.Mode.Result;
                if (result != null) ended++;
                text += $" s{seed}:{(result == null ? "open" : result.Value.WinningTeam == 0 ? "W" : result.Value.WinningTeam == 1 ? "L" : "D")}{t / 60f:0.0}m";
            }
            Debug.Log($"ENDS {name}: {ended}/5{text}");
            Assert.AreEqual(5, ended, $"{name} ends within {cap} minutes on every seed:{text}");
        }
    }
}
