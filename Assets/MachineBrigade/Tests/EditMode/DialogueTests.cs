using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;

namespace MachineBrigade.Tests
{
    /// <summary>Prompt 23 H: the in-battle dialogue's rules (one line at a time, priorities, the gap, the log, the setting, story moments).</summary>
    public class DialogueTests
    {
        private static DialogueLine Line(DialoguePriority priority, string key = "radio.khai.c9m02.1", bool moment = false) =>
            new(key, priority, "khai", false, moment);

        [Test]
        public void PrioritiesDropsAndTheGap()
        {
            var d = new DialogueDirector();
            Assert.AreEqual(DialogueOutcome.Shown, d.Say(Line(DialoguePriority.Event), 0));
            Assert.AreEqual(DialogueOutcome.Dropped, d.Say(Line(DialoguePriority.Reaction), 1), "a lower line while one is up: dropped, not queued");
            // A warning waits, then cuts the event line short (after a second on show) and follows the fade.
            Assert.AreEqual(DialogueOutcome.Queued, d.Say(Line(DialoguePriority.Warning, "radio.bigattack.tempest_rail"), 1.2));
            Assert.AreEqual(DialogueOutcome.Dropped, d.Say(Line(DialoguePriority.Event), 1.3), "an event line while a warning waits");
            d.Tick(1.3);
            Assert.IsNull(d.Current, "cut short");
            d.Tick(1.3 + DialogueDirector.FadeSeconds);
            Assert.AreEqual(DialoguePriority.Warning, d.Current?.Priority);
            // Story lines queue ahead of warnings.
            d.Say(Line(DialoguePriority.Warning, "radio.bigattack.behemoth_barrage"), 2);
            d.Say(Line(DialoguePriority.Story, "radio.khai.c9m07.1"), 2.1);
            var order = new System.Collections.Generic.List<DialoguePriority>();
            d.Shown += l => order.Add(l.Priority);
            for (var t = 2.2; t < 30; t += 0.1) d.Tick(t);
            CollectionAssert.AreEqual(new[] { DialoguePriority.Story, DialoguePriority.Warning }, order);
            // Event and reaction lines at least Gap apart; reactions rarer while a boss is on the field.
            var e = new DialogueDirector();
            Assert.AreEqual(DialogueOutcome.Shown, e.Say(Line(DialoguePriority.Event), 100));
            for (var t = 100.0; t < 107; t += 0.1) e.Tick(t);
            Assert.IsNull(e.Current, "a line hides by itself within 6 s");
            Assert.AreEqual(DialogueOutcome.Dropped, e.Say(Line(DialoguePriority.Reaction), 107), "too soon after the last");
            Assert.AreEqual(DialogueOutcome.Shown, e.Say(Line(DialoguePriority.Reaction), 100 + DialogueDirector.Gap));
            for (var t = 109.0; t < 120; t += 0.1) e.Tick(t);
            e.BossBattle = true;
            Assert.AreEqual(DialogueOutcome.Dropped, e.Say(Line(DialoguePriority.Reaction), 120), "a boss battle waits longer for reactions");
            Assert.AreEqual(DialogueOutcome.Shown, e.Say(Line(DialoguePriority.Event), 120), "but not for event lines");
            Assert.That(DialogueDirector.SecondsFor(10), Is.EqualTo(3.0));
            Assert.That(DialogueDirector.SecondsFor(400), Is.EqualTo(6.0));
        }

        [Test]
        public void TheLogKeepsTheLastTwentyLines()
        {
            var d = new DialogueDirector();
            for (var i = 0; i < 25; i++)
            {
                d.Say(Line(DialoguePriority.Story, i % 2 == 0 ? "radio.khai.c9m02.1" : "radio.khai.c9m07.1"), i * 10);
                d.Tick(i * 10 + 7);
            }
            Assert.AreEqual(DialogueDirector.LogSize, d.Log.Count);
            Assert.AreEqual(50.0, d.Log[0].At, "the oldest five went");
            Assert.AreEqual(240.0, d.Log[d.Log.Count - 1].At, "newest last");
            Assert.IsTrue(d.Log.All(l => l.Line.Words.Length > 0 && !l.Line.Words.StartsWith("radio.")));
        }

        [Test]
        public void TheSettingHidesLinesButNeverTheStory()
        {
            foreach (var (setting, shown) in new[]
                     {
                         (DialogueSetting.Full, new[] { true, true, true, true }), (DialogueSetting.Important, new[] { true, true, false, false }),
                         (DialogueSetting.Off, new[] { true, false, false, false }),
                     })
                for (var p = 0; p < 4; p++)
                {
                    var d = new DialogueDirector { Setting = setting };
                    var outcome = d.Say(Line((DialoguePriority)p), 0);
                    Assert.AreEqual(shown[p], outcome != DialogueOutcome.Filtered, $"{setting} {(DialoguePriority)p}");
                }
        }

        [Test]
        public void AStoryMomentSlowsTheBattleWhileItsLinesPlay()
        {
            var d = new DialogueDirector();
            Assert.AreEqual(1f, d.TimeScale(0));
            d.Say(Line(DialoguePriority.Story, "radio.betrayal", moment: true), 0);
            d.Say(Line(DialoguePriority.Story, "radio.khai.c9m02.1"), 0);
            Assert.AreEqual(DialogueDirector.MomentScale, d.TimeScale(1), 1e-4, "half speed once eased in");
            for (var t = 0.0; t < 20; t += 0.1) d.Tick(t);
            Assert.AreEqual(2, d.Log.Count, "both lines played");
            Assert.AreEqual(1f, d.TimeScale(20), 1e-4, "full speed after the moment");
            // The event system's flags: Value = priority + 1, Mount 1 = a story moment.
            var heard = DialogueRules.FromEvent("radio.khai.c9m02.1", 0, 1f, 1, default, null);
            Assert.AreEqual(DialoguePriority.Story, heard.Priority);
            Assert.IsTrue(heard.Moment);
            Assert.AreEqual(DialoguePriority.Warning, DialogueRules.FromEvent("radio.bigattack.tempest_rail", 1, 0f, 0, default, null).Priority, "by key");
        }

        [Test]
        public void ASpeakerNamedInTheTextSpeaksWithoutThePrefix()
        {
            var was = Strings.Vietnamese;
            try
            {
                foreach (var vi in new[] { false, true })
                {
                    Strings.Vietnamese = vi;
                    var kessler = DialogueRules.Line("radio.bigattack.supergun_heavy", team: 1);
                    Assert.AreEqual("kessler", kessler.Speaker);
                    Assert.IsTrue(kessler.Enemy);
                    Assert.IsFalse(kessler.Words.Contains("Kessler") || kessler.Words.StartsWith("\""), kessler.Words);
                    var command = DialogueRules.Line("radio.bigattack.tempest_rail", team: 1);
                    Assert.AreEqual("hq", command.Speaker);
                    Assert.IsFalse(command.Enemy, "Command speaks for us whatever the team");
                    Assert.AreEqual(Strings.Get("dialogue.name.hq"), command.Name);
                }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }
    }
}
