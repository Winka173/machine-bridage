using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Rendering;
using NUnit.Framework;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The shared shield look (prompt 11C): hexagonal tiles (twelve pentagons among them), a
    /// round's ripple on the dome straight above where it landed, a shatter that ends hidden,
    /// blue for our side and red-orange for the enemy's in both palettes, and the Low variant.
    /// </summary>
    public class ShieldVisualTests
    {
        private GameObject _root;
        private int _palette;

        [SetUp]
        public void SetUp()
        {
            _root = new GameObject("Shield Test");
            _palette = TeamColors.Palette;
        }

        [TearDown]
        public void TearDown()
        {
            TeamColors.Palette = _palette;
            ShieldVisual.LiteOverride = null;
            Object.DestroyImmediate(_root);
        }

        [Test]
        public void ABubbleIsHexagonsAndTwelvePentagons()
        {
            var bubble = new ShieldVisual("Bubble", _root.transform, ShieldVisual.Shape.Bubble, 4f);
            var mesh = bubble.Transform.GetComponent<MeshFilter>().sharedMesh;
            // A geodesic sphere split twice has 162 points: 12 pentagon tiles and 150 hexagons,
            // each a centre and its corners, fanned into five or six triangles.
            Assert.AreEqual(12 * 6 + 150 * 7, mesh.vertexCount);
            Assert.AreEqual((12 * 5 + 150 * 6) * 3, (int)mesh.GetIndexCount(0));
        }

        [Test]
        public void AHitRipplesTheDomeAboveItAndACollapseEndsHidden()
        {
            var dome = new ShieldVisual("Dome", _root.transform, ShieldVisual.Shape.Dome, 20f);
            dome.Transform.position = new Vector3(100f, 0f, 50f);
            dome.Transform.localScale = new Vector3(20f, 10f, 20f);
            dome.Raise(0f, 0f);
            Assert.IsTrue(dome.Standing);
            // A round landing 10 m east of the middle: the ripple is on the skin straight above.
            dome.Hit(new Vector3(110f, 1f, 50f), 1f);
            Assert.IsTrue(dome.Tick(1.1f));
            var block = new MaterialPropertyBlock();
            dome.Transform.GetComponent<MeshRenderer>().GetPropertyBlock(block);
            var ripple = block.GetVector("_Ripple0");
            Assert.AreEqual(0.5f, ripple.x, 1e-3f);
            Assert.AreEqual(Mathf.Sqrt(0.75f), ripple.y, 1e-3f);
            Assert.AreEqual(1f, ripple.w, 1e-4f);
            // Far outside it, a round never touched it.
            dome.Hit(new Vector3(160f, 1f, 50f), 1.2f);
            dome.Tick(1.25f);
            dome.Transform.GetComponent<MeshRenderer>().GetPropertyBlock(block);
            Assert.AreEqual(-100f, block.GetVector("_Ripple1").w, 1e-4f);

            dome.Collapse(2f);
            Assert.IsFalse(dome.Standing);
            Assert.IsTrue(dome.Tick(2f + ShieldVisual.CollapseSeconds * 0.5f));
            Assert.IsFalse(dome.Tick(2f + ShieldVisual.CollapseSeconds + 0.01f));
            Assert.IsFalse(dome.Transform.gameObject.activeSelf);
        }

        [Test]
        public void OursIsBlueTheEnemysRedOrangeInBothPalettes()
        {
            foreach (var palette in new[] { 0, 1 })
            {
                TeamColors.Palette = palette;
                var ours = ShieldVisual.SideColour(true);
                var theirs = ShieldVisual.SideColour(false);
                Assert.Greater(ours.b, ours.r, $"palette {palette}: ours blue");
                Assert.Greater(theirs.r, theirs.b * 3f, $"palette {palette}: theirs red-orange");
                Assert.Greater(theirs.r, theirs.g, $"palette {palette}: theirs red-orange");
            }
        }

        [Test]
        public void LowGraphicsDrawsTheLighterVariant()
        {
            ShieldVisual.LiteOverride = true;
            var lite = new ShieldVisual("Lite", _root.transform, ShieldVisual.Shape.Bubble, 4f);
            ShieldVisual.LiteOverride = false;
            var full = new ShieldVisual("Full", _root.transform, ShieldVisual.Shape.Bubble, 4f);
            Assert.IsTrue(lite.Transform.GetComponent<MeshRenderer>().sharedMaterial.IsKeywordEnabled("_SHIELD_LITE"));
            Assert.IsFalse(full.Transform.GetComponent<MeshRenderer>().sharedMaterial.IsKeywordEnabled("_SHIELD_LITE"));
        }
    }
}
