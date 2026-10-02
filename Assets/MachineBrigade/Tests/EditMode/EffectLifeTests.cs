using NUnit.Framework;
using MachineBrigade.Game.Effects;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Fix prompt L6 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"): the lifetimes table by size band, craters that close and
    /// go when their time is up, at most three big smoke columns at once. Written, not run (the owner's rule).
    /// </summary>
    public class EffectLifeTests
    {
        [Test]
        public void TheTableGrowsWithTheBand()
        {
            Assert.AreEqual(0f, EffectLife.Crater(0), 1e-4f, "up to 14.5 mm: no crater");
            Assert.AreEqual(10f, EffectLife.Crater(1), 1e-4f);
            Assert.AreEqual(30f, EffectLife.Crater(3), 1e-4f);
            Assert.AreEqual(60f, EffectLife.Crater(5), 1e-4f);
            Assert.AreEqual(12f, EffectLife.Of(4).SmokeMin, 1e-4f, "a 203 mm column 12-20 s");
            Assert.AreEqual(40f, EffectLife.Of(5).SmokeMax, 1e-4f, "a 406 mm column up to 40 s");
            for (var b = 1; b <= EffectLife.Top; b++)
            {
                Assert.Greater(EffectLife.Of(b).Fireball, EffectLife.Of(b - 1).Fireball, "fireball band " + b);
                Assert.GreaterOrEqual(EffectLife.Of(b).SmokeMin, EffectLife.Of(b - 1).SmokeMax, "smoke band " + b);
                Assert.Greater(EffectLife.Crater(b), EffectLife.Crater(b - 1), "crater band " + b);
            }
            Assert.AreEqual(4, EffectLife.BandOf(null, ExplosionTier.Huge), "no family: by its explosion tier");
        }

        [Test]
        public void ACraterClosesAndGoesWhenItsTimeIsUp()
        {
            var root = new GameObject("decal test");
            try
            {
                var quad = new Mesh();
                var pool = new DecalPool(quad, root.transform, 4);
                pool.Tick(0f);
                pool.Place(Vector3.zero, 2f, 10f);
                var mark = root.transform.GetChild(0).GetChild(0);
                Assert.IsTrue(mark.gameObject.activeSelf);
                pool.Tick(5f);
                Assert.AreEqual(2f * 1.35f, mark.localScale.x, 1e-3f, "whole until its last quarter");
                pool.Tick(9f);
                Assert.Less(mark.localScale.x, 2f * 1.35f, "closing over its last quarter");
                pool.Tick(10.5f);
                Assert.IsFalse(mark.gameObject.activeSelf, "gone when its time is up");
                pool.Place(Vector3.one, 2f);
                pool.Tick(1000f);
                Assert.IsTrue(root.transform.GetChild(0).GetChild(1).gameObject.activeSelf, "a mark with no life stays");
            }
            finally
            {
                Object.DestroyImmediate(root);
            }
        }

        [Test]
        public void AtMostThreeBigColumnsStand()
        {
            var root = new GameObject("smoke test");
            try
            {
                var smoke = new ImpactSmoke(root.transform);
                for (var k = 0; k < 5; k++) smoke.Linger(4, new Vector3(k * 30f, 0f, 0f), 9f, k * 0.5f, TierFx.Detail.Full);
                Assert.LessOrEqual(smoke.Standing, ImpactSmoke.BigColumns);
                smoke.Tick(3f);
                smoke.Tick(60f);
                Assert.AreEqual(0, smoke.Standing, "all cleared within their time");
            }
            finally
            {
                Object.DestroyImmediate(root);
            }
        }
    }
}
