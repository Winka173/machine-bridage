using NUnit.Framework;
using MachineBrigade.Game.Audio;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The bomb-run fix, pass 3 (DECISIONS "Ném bom rải thảm"): the view's side of a stick, without a scene: the run the view
    /// follows from the fired events (StickRuns), its warning rectangle giving up its ground as the bombs land, the far bombs
    /// of a long stick drawn lighter, the hinged bay doors' node names, a falling bomb's trail and the blasts heard as one
    /// stick. Written, not run (the owner's rule).
    /// </summary>
    public class BombStickViewTests
    {
        private static Catalog Shipped => GameContent.LoadCatalog();

        /// <summary>Fires a stick's bombs along +X from the origin, one release interval apart; returns the run.</summary>
        private static StickRuns.Run Lay(StickRuns runs, WeaponDef round, int bombs, float travel, long owner = 1, int skip = -1)
        {
            var s = round.Stick;
            StickRuns.Run run = null;
            for (var i = 0; i < bombs; i++)
            {
                if (i == skip) continue;
                var at = new Vector3(i * s.Spacing + (i % 2 == 0 ? 0.4f : -0.4f) * s.JitterAlong, 0f, 0.5f * s.JitterAcross);
                var got = runs.Fired(owner, round, at, Vector3.right, i * s.Interval, travel, true, false, out var index);
                Assert.AreEqual(i, index, round.Id + ": bomb " + i + " on its own section");
                if (run == null) run = got;
                Assert.AreSame(run, got, round.Id + ": bomb " + i + " is the same stick's");
            }
            return run;
        }

        [Test, Category("BombStick")]
        public void EveryBombOfAStickGoesOnItsOwnSectionOfOneRun()
        {
            var c = Shipped;
            foreach (var id in new[] { "bomber_payload", "p26_roc_main_roc_bombs" })
            {
                var round = c.Weapons[id];
                var runs = new StickRuns();
                var run = Lay(runs, round, round.Stick.Bombs, 2.7f);
                Assert.AreEqual(1, runs.Runs.Count, id + ": one run for the stick");
                Assert.AreEqual(round.Stick.Bombs, run.Seen, id + ": every bomb seen");
                for (var i = 0; i < run.Bombs; i++)
                    Assert.AreEqual(i * round.Stick.Interval + 2.7f, run.Due[i], 1e-4f, id + ": section " + i + " due when its bomb lands");
            }
        }

        [Test, Category("BombStick")]
        public void TheRectangleCoversTheWholeStickAndGivesUpItsGroundAsTheBombsLand()
        {
            var round = Shipped.Weapons["bomber_payload"];
            var s = round.Stick;
            var runs = new StickRuns();
            var first = runs.Fired(1, round, Vector3.zero, Vector3.right, 0f, 2.7f, true, false, out _);
            // Right after the first bomb: the whole stick, its end bombs' blast edges and jitter included.
            Assert.IsTrue(StickRuns.Span(first, 0.1f, first.Edge, out var centre, out var half, out var front, out var last));
            Assert.AreEqual(0, front);
            Assert.AreEqual(s.Bombs - 1, last, "the rectangle warns of the bombs still to come");
            Assert.AreEqual((s.Bombs - 1) * s.Spacing * 0.5f + first.Edge + s.JitterAlong, half, 1e-3f, "half its length");
            Assert.AreEqual((s.Bombs - 1) * s.Spacing * 0.5f, centre.x, 1e-3f, "centred on the stick");
            var run = Lay(runs, round, s.Bombs, 2.7f, owner: 2);
            Assert.AreEqual(2, runs.Runs.Count, "another bomber's stick is its own run");
            // After the third bomb has landed: the rectangle starts at the fourth.
            var now = 2 * s.Interval + 2.7f + 0.01f;
            Assert.IsTrue(StickRuns.Span(run, now, run.Edge, out var later, out var shorter, out front, out _));
            Assert.AreEqual(3, front, "the landed sections are let go");
            Assert.Less(shorter, half, "the rectangle shrinks");
            Assert.Greater(later.x, centre.x, "and moves on along the stick");
            Assert.IsFalse(StickRuns.Span(run, (s.Bombs - 1) * s.Interval + 2.7f + 0.01f, run.Edge, out _, out _, out _, out _),
                "gone once the last bomb has landed");
        }

        [Test, Category("BombStick")]
        public void ABombNeverDroppedLetsItsSectionGoAndTheOthersKeepTheirs()
        {
            var round = Shipped.Weapons["bomber_payload"];
            var s = round.Stick;
            var runs = new StickRuns();
            var run = Lay(runs, round, s.Bombs, 2.7f, skip: 3);
            // Bomb 3 was held back (a friend under it): its section goes a grace after its release time.
            var after = 3 * s.Interval + StickRuns.Grace(s) + 0.01f;
            runs.Tick(after);
            Assert.LessOrEqual(run.Due[3], after, "the skipped section is let go");
            Assert.AreEqual(4 * s.Interval + 2.7f, run.Due[4], 1e-4f, "the next bomb keeps its section");
            Assert.IsFalse(run.Fired[3]);
        }

        [Test, Category("BombStick")]
        public void AStickCutToAFewBombsLetsItsTailGo()
        {
            var round = Shipped.Weapons["bomber_payload"];
            var s = round.Stick;
            var runs = new StickRuns();
            // A long fall, so the bombs dropped are still in the air when the last section's release time has passed.
            var run = Lay(runs, round, s.Reduced, 6f);
            var after = (s.Bombs - 1) * s.Interval + StickRuns.Grace(s) + 0.01f;
            runs.Tick(after);
            Assert.IsTrue(StickRuns.Span(run, after, run.Edge, out _, out _, out _, out var last));
            Assert.AreEqual(s.Reduced - 1, last, "the rectangle ends at the last bomb dropped");
        }

        [Test, Category("BombStick")]
        public void ALandingBombFindsItsSection()
        {
            var round = Shipped.Weapons["p26_roc_main_roc_bombs"];
            var s = round.Stick;
            var runs = new StickRuns();
            Lay(runs, round, s.Bombs, 1.3f);
            var run = runs.Landed(round, new Vector3(5 * s.Spacing + 0.6f, 0f, -0.8f), out var index);
            Assert.IsNotNull(run);
            Assert.AreEqual(5, index);
            Assert.IsNull(runs.Landed(Shipped.Weapons["bomber_payload"], Vector3.zero, out _), "another weapon's bomb is not this stick's");
            Assert.IsNull(runs.Landed(round, new Vector3(3 * s.Spacing, 0f, 60f), out _), "far off the line: not this stick's");
        }

        [Test, Category("BombStick")]
        public void TheFarBombsOfALongStickAreLighterTheNearOnesWhole()
        {
            Assert.AreEqual(TierFx.Detail.Full, TierFx.StickDetail(TierFx.Detail.Full, 7, 10f), "near the view: whole");
            Assert.AreEqual(TierFx.Detail.Reduced, TierFx.StickDetail(TierFx.Detail.Full, 7, 50f), "far: one level less");
            Assert.AreEqual(TierFx.Detail.Full, TierFx.StickDetail(TierFx.Detail.Full, 2, 50f), "a pair: as any blast");
            Assert.AreEqual(TierFx.Detail.Far, TierFx.StickDetail(TierFx.Detail.Full, 20, 80f), "a 20-bomb carpet's farthest: flash and rings");
            Assert.AreEqual(TierFx.Detail.Reduced, TierFx.StickDetail(TierFx.Detail.Full, 20, 50f));
            Assert.AreEqual(TierFx.Detail.Reduced, TierFx.StickDetail(TierFx.Detail.Reduced, 0, 50f), "not a stick: unchanged");
        }

        [Test, Category("BombStick")]
        public void OnlyTheHingedBayDoorsSwing()
        {
            Assert.IsTrue(ModelLibrary.BayDoorPattern.IsMatch("Part_bay_door_L"));
            Assert.IsTrue(ModelLibrary.BayDoorPattern.IsMatch("Part_bay_door_R"));
            Assert.IsTrue(ModelLibrary.BayDoorPattern.IsMatch("Part_bay_door_L.001"));
            Assert.IsFalse(ModelLibrary.BayDoorPattern.IsMatch("Bay_doors"), "a door merged into the hull has no hinge");
            Assert.IsFalse(ModelLibrary.BayDoorPattern.IsMatch("Bay_door_l"), "the door's mesh, not its hinge");
            Assert.IsFalse(ModelLibrary.PartPattern.IsMatch("Part_bay_door_L"), "not a boss part either (why it has its own pattern)");
        }

        [Test, Category("BombStick")]
        public void FreeFallingBombsTrailAndGuidedOnesDoNot()
        {
            var c = Shipped;
            Assert.Greater(WeaponEffects.BombStreak(c.Weapons["bomber_payload"]), 0f);
            Assert.Greater(WeaponEffects.BombStreak(c.Weapons["jet_bombs"]), 0f);
            Assert.AreEqual(0f, WeaponEffects.BombStreak(c.Weapons["stealth_payload"]), "a JDAM flies its own way");
            Assert.AreEqual(0f, WeaponEffects.BombStreak(c.Weapons["guided_bomb"]));
            Assert.AreEqual(0f, WeaponEffects.BombStreak(null));
        }

        [Test, Category("BombStick")]
        public void AStickIsHeardAsOneStick()
        {
            var s = Shipped.Weapons["bomber_payload"].Stick;
            Assert.IsTrue(AudioDirector.SameStick(s, s.Interval, s.Spacing), "the next bomb follows on");
            Assert.IsTrue(AudioDirector.SameStick(s, s.Interval * 2f, s.Spacing * 2f), "one skipped bomb between");
            Assert.IsFalse(AudioDirector.SameStick(s, 10f, s.Spacing), "the next stick, a cycle later");
            Assert.IsFalse(AudioDirector.SameStick(s, s.Interval, 200f), "another bomber's stick elsewhere");
        }

        [Test, Category("BombStick")]
        public void TheFrontEdgeGlidesOnToTheNextBombInsteadOfJumping()
        {
            var round = Shipped.Weapons["bomber_payload"];
            var s = round.Stick;
            var runs = new StickRuns();
            var run = runs.Fired(1, round, Vector3.zero, Vector3.right, 0f, 2.7f, true, false, out _);
            Assert.AreEqual(-3f, StickWarnings.Glide(run, -3f, 0f), 1e-4f, "not drawn yet: where it is");
            run.ShownFrom = 0f;
            run.ShownAt = 0f;
            var half = StickWarnings.Glide(run, s.Spacing, StickWarnings.FrontGlide * 0.5f);
            Assert.AreEqual(s.Spacing * 0.5f, half, 1e-3f, "half a glide: half way to the next section");
            Assert.AreEqual(s.Spacing, StickWarnings.Glide(run, s.Spacing, StickWarnings.FrontGlide * 2f), 1e-4f, "never past it");
            Assert.AreEqual(-1f, StickWarnings.Glide(run, -1f, 1f), 1e-4f, "never behind the front section");
        }

        [Test, Category("BombStick")]
        public void TheGateTakesAStickAsARectangle()
        {
            var gate = new WarningGate { MaxShown = 6, PlayerTeam = 0 };
            var stick = new object();
            gate.OfferRect(stick, Vector3.zero, Vector3.right, 40f, 12f, WarningKind.Round);
            gate.Resolve(null, Vector3.zero);
            Assert.IsTrue(gate.Shown(stick, WarningKind.Round), "a stick's rectangle is a warning like a ring");
            gate.Level = 2;
            gate.OfferRect(stick, Vector3.zero, Vector3.right, 40f, 12f, WarningKind.Round);
            gate.Resolve(null, Vector3.zero);
            Assert.IsFalse(gate.Shown(stick, WarningKind.Round), "Off: no rectangle (only the super weapons stay)");
        }

        [Test, Category("BombStick")]
        public void TheStickWarningsAreTheDataShape()
        {
            var c = Shipped;
            Assert.AreEqual(StickWarn.StickRect, c.Weapons["bomber_payload"].Stick.Warn, "500 kg: one rectangle");
            Assert.AreEqual(StickWarn.StickRect, c.Weapons["p26_roc_main_roc_bombs"].Stick.Warn, "a boss bay: one rectangle");
            Assert.AreEqual(StickWarn.None, c.Weapons["jet_bombs"].Stick.Warn, "250 kg: none");
        }
    }
}
