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
            // Prompt 30 L12: every line queues; P3/P4 go stale after 8 s; the gap holds P2-P4 only.
            var d = new DialogueDirector();
            Assert.AreEqual(DialogueOutcome.Shown, d.Say(Line(DialoguePriority.Event), 0));
            Assert.AreEqual(DialogueOutcome.Queued, d.Say(Line(DialoguePriority.Reaction), 1), "a lower line while one is up waits");
            // A warning's line (P1) waits, then cuts the event line short (after a second on show) and follows the fade.
            Assert.AreEqual(DialogueOutcome.Queued, d.Say(Line(DialoguePriority.Warning, "radio.bigattack.doomsday_missile"), 1.2));
            d.Tick(1.3);
            Assert.IsNull(d.Current, "cut short");
            d.Tick(1.3 + DialogueDirector.FadeSeconds);
            Assert.AreEqual(DialoguePriority.Warning, d.Current?.Priority, "P1 ignores the gap");
            for (var t = 1.6; t < 12; t += 0.1) d.Tick(t);
            Assert.IsFalse(d.Log.Any(l => l.Line.Priority == DialoguePriority.Reaction), "the reaction went stale after 8 s, never saved up");
            Assert.AreEqual(0, d.Waiting);
            // Story lines queue ahead of warnings' lines, and either cuts an event line short.
            d.Say(Line(DialoguePriority.Event), 20);
            d.Say(Line(DialoguePriority.Warning, "radio.bigattack.behemoth_barrage"), 20.05);
            d.Say(Line(DialoguePriority.Story, "radio.khai.c9m07.1"), 20.1);
            var order = new System.Collections.Generic.List<DialoguePriority>();
            d.Shown += l => order.Add(l.Priority);
            for (var t = 20.2; t < 40; t += 0.1) d.Tick(t);
            CollectionAssert.AreEqual(new[] { DialoguePriority.Story, DialoguePriority.Warning }, order);
            // P2-P4 at least Gap apart (20 s with a boss on the field): a line asked for too soon waits, then shows.
            var e = new DialogueDirector();
            Assert.AreEqual(DialogueOutcome.Shown, e.Say(Line(DialoguePriority.Event), 100));
            for (var t = 100.0; t < 107; t += 0.1) e.Tick(t);
            Assert.IsNull(e.Current, "a line hides by itself within 6 s");
            Assert.AreEqual(DialogueOutcome.Queued, e.Say(Line(DialoguePriority.Reaction), 107), "too soon after the last: waits");
            e.Tick(100 + DialogueDirector.Gap - 0.05);
            Assert.IsNull(e.Current);
            e.Tick(100 + DialogueDirector.Gap);
            Assert.AreEqual(DialoguePriority.Reaction, e.Current?.Priority, "shown once the gap is over");
            for (var t = 109.0; t < 120; t += 0.1) e.Tick(t);
            e.BossBattle = true;
            Assert.AreEqual(DialogueOutcome.Queued, e.Say(Line(DialoguePriority.Event), 120), "a boss battle holds even P2 for 20 s");
            for (var t = 120.0; t < 128.9; t += 0.1) e.Tick(t);
            Assert.IsNull(e.Current);
            e.Tick(109 + DialogueDirector.BossGap);
            Assert.AreEqual(DialoguePriority.Event, e.Current?.Priority, "kept 12 s, shown 20 s after the last start");
            // P0 cuts any line at once and shows whatever the setting.
            var f = new DialogueDirector { Setting = DialogueSetting.Off };
            Assert.AreEqual(DialogueOutcome.Shown, f.Say(Line(DialoguePriority.Story), 0));
            Assert.AreEqual(DialogueOutcome.Shown, f.Say(Line(DialoguePriority.System, "radio.bigattack.doomsday_missile"), 0.2));
            Assert.AreEqual(DialoguePriority.System, f.Current?.Priority);
            Assert.AreEqual(1, DialogueDirector.Level(DialoguePriority.Story));
            Assert.AreEqual(4, DialogueDirector.Level(DialogueDirector.FromLevel(4)));
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
                         // System (P0), Story, Warning, Event, Reaction, Ambient.
                         (DialogueSetting.Full, new[] { true, true, true, true, true, true }),
                         (DialogueSetting.Important, new[] { true, true, true, false, false, false }),
                         (DialogueSetting.Off, new[] { true, true, false, false, false, false }),
                     })
                for (var p = -1; p <= 4; p++)
                {
                    var d = new DialogueDirector { Setting = setting };
                    var outcome = d.Say(Line((DialoguePriority)p), 0);
                    Assert.AreEqual(shown[p + 1], outcome != DialogueOutcome.Filtered, $"{setting} {(DialoguePriority)p}");
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
            Assert.AreEqual(DialoguePriority.Warning, DialogueRules.FromEvent("radio.bigattack.doomsday_missile", 1, 0f, 0, default, null).Priority, "by key");
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
                    var kessler = DialogueRules.Line("radio.bigattack.leviathan_volley", team: 1);
                    Assert.AreEqual("kessler", kessler.Speaker);
                    Assert.IsTrue(kessler.Enemy);
                    Assert.IsFalse(kessler.Words.Contains("Kessler") || kessler.Words.StartsWith("\""), kessler.Words);
                    var command = DialogueRules.Line("radio.bigattack.doomsday_missile", team: 1);
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
