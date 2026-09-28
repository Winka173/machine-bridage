using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>The campaign's radio chatter: the mission's own lines by trigger, each once, and the brigade's usual lines now and then.</summary>
    public class RadioDirectorTests
    {
        private string _mission;

        [SetUp]
        public void SetUp() => _mission = MatchSettings.Mission;

        [TearDown]
        public void TearDown() => MatchSettings.Mission = _mission;

        [Test]
        public void SpeakersComeFromTheKey()
        {
            Assert.AreEqual("khai", RadioDirector.SpeakerOf("radio.khai.c1m03.1"));
            Assert.AreEqual("varga", RadioDirector.SpeakerOf("radio.varga.taunt.2"));
            Assert.AreEqual("linh", RadioDirector.SpeakerOf("radio.betrayal"), "a known voice for a key without a speaker");
            Assert.AreEqual("hq", RadioDirector.SpeakerOf("radio.somethingelse"));
            Assert.IsTrue(new RadioLine("orlov", "x").Enemy);
            Assert.IsFalse(new RadioLine("mai", "x").Enemy);
        }

        [Test]
        public void AMissionsLinesPlayOnceWhenTheirMomentComes()
        {
            var def = Campaign.Get("c1m03");
            MatchSettings.Mission = def.Id;
            var world = new SimWorld(GameContent.LoadCatalog(), Campaign.LoadMap(def), seed: 2);
            var session = (MissionSession)ModeSession.Create(GameModeKind.Campaign, false, world, 2);
            var radio = new RadioDirector(def, 2);
            var said = new List<RadioLine>();
            radio.Spoke += said.Add;
            for (var t = 0f; t < 6 * 60 && session.Mode.Result == null; t += 0.05f)
            {
                session.Mode.Tick(world, 0.05f);
                session.TickAi(world, 0.05f);
                world.Step(0.05f);
                radio.Tick(world, session);
                radio.Consume(world, world.Events);
                world.ClearEvents();
            }
            radio.Tick(world, session);
            var keys = said.Select(l => l.Key).ToList();
            Assert.AreEqual("radio.khai.c1m03.1", keys[0], "the start line first");
            Assert.AreEqual(keys.Count, keys.Distinct().Count(), "every line once");
            Assert.IsTrue(keys.Contains("radio.linh.c1m03.2"), "the line for taking the crossroads");
            Assert.IsTrue(keys.All(Strings.Has), "every line is in the localisation");
            var generic = keys.Count(k => k.Contains(".gen."));
            Assert.LessOrEqual(generic, 1 + (int)(world.Time / 35.0) + 2, "the usual lines are rationed");
        }
    }
}
