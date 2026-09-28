using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>Temporary: why a mission ends as it does (removed once tuned).</summary>
    public class CampaignDiagTests
    {
        [TestCase("c6m03")]
        [TestCase("c3m04")]
        public void Trace(string id)
        {
            var def = Campaign.Get(id);
            var catalog = GameContent.LoadCatalog();
            var world = new SimWorld(catalog, Campaign.LoadMap(def), seed: 5);
            MatchSettings.Mission = id;
            var session = (MissionSession)ModeSession.Create(GameModeKind.Campaign, false, world, 5);
            var log = "";
            for (var t = 0f; t < 20 * 60 && session.Mode.Result == null; t += 0.05f)
            {
                session.Mode.Tick(world, 0.05f);
                session.TickAi(world, 0.05f);
                world.Step(0.05f);
                world.ClearEvents();
                if (world.Tick % 200 != 0) continue;
                var convoy = world.VehicleList.Where(v => v.Scripted && v.Team == 0).Select(v => $"{v.Def.Id}:{v.Hp / v.MaxHp:P0}@{v.Position.X:0},{v.Position.Y:0}");
                var point = session.Mission.Points.Select(p => $"{p.Def.Id}={p.Owner}/{p.Progress:0.00}");
                var outposts = world.Bases.Of(0)?.Outposts.Count ?? -1;
                world.TryGetEconomy(0, out var e);
                log += $"\n t{t:0} convoy[{string.Join(" ", convoy)}] points[{string.Join(" ", point)}] outposts {outposts} cp {e?.Cp:0} army {e?.ArmyCp} prog {session.Mission.Progress(world):P0}";
            }
            Debug.Log($"TRACE {id}: {session.Mode.Result?.WinningTeam}{log}");
        }
    }
}
