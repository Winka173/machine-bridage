using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Modes;
using NUnit.Framework;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Tower-branch prompt C: every tower's two rank-7 branches wear models and icons of their own that
    /// differ from each other (C.1, C.4), with the muzzles their weapons need and a shared simpler level
    /// (C.6); ranks 1-6 show bars and plates that grow with the rank (C.2).
    /// </summary>
    public class TowerBranchArtTests
    {
        private MaterialLibrary _materials;
        private ModelLibrary _models;

        [SetUp]
        public void SetUp()
        {
            _materials = new MaterialLibrary();
            _models = new ModelLibrary(_materials);
        }

        [TearDown]
        public void TearDown()
        {
            TowerArt.Ranks = null;
            TowerArt.Lean = false;
            _models.Dispose();
            _materials.Dispose();
        }

        [Test]
        public void TheTwoBranchesOfEveryTowerDifferInModelAndIcon()
        {
            var catalog = GameContent.LoadCatalog();
            // Prompt 32 L1: the cards that gained branches by the merge have no <tower>_a/_b art yet (Docs/ai/LOCAL_TODO.md).
            var artPending = new HashSet<string> { "laser_ad_station" };
            var towers = TowerCards.All(catalog).Where(t => TowerCards.Branches(catalog, t).Count == 2 && !artPending.Contains(t)).ToList();
            Assert.GreaterOrEqual(towers.Count, 12, "every tower of the spec has two branches (14 cards after play-test 14)");
            var problems = new List<string>();
            foreach (var tower in towers)
            {
                var looks = new List<(string model, int tris, Vector3 size, string icon, int far)>();
                foreach (var (branch, letter) in TowerCards.Branches(catalog, tower).Zip("ab", (b, l) => (b, l)))
                {
                    var def = catalog.Vehicles[branch];
                    var model = TowerArt.ModelFor(def, _models.Has);
                    if (model != catalog.Vehicles[tower].Model + "_" + letter) problems.Add($"{branch}: wears {model}");
                    var prefab = Resources.Load<GameObject>("Models/" + model);
                    if (prefab == null)
                    {
                        problems.Add($"{branch}: no model {model}");
                        continue;
                    }
                    // The branch's weapons fire from muzzles on its own model.
                    foreach (var mount in def.Mounts)
                        if (!mount.Weapon.Melee && mount.Weapon.Damage > 0f && Find(prefab.transform, "Muzzle_" + mount.Slot) == null)
                            problems.Add($"{model}: no Muzzle_{mount.Slot} for {mount.Weapon.Id}");
                    var icon = TowerIcons.For(branch);
                    if (icon != TowerIcons.For(tower) + "_" + letter || !Icons.Exists(icon)) problems.Add($"{branch}: icon {icon}");
                    var lod = _models.Lod(model);
                    if (lod == null || lod.Draws1 >= lod.Draws0) problems.Add($"{model}: no simpler shared level");
                    looks.Add((model, Triangles(prefab), Size(prefab), icon, lod?.Triangles1 ?? 0));
                }
                if (looks.Count != 2) continue;
                var (a, b) = (looks[0], looks[1]);
                // Different meshes: other triangle counts or another shape, near and far (the simpler level).
                if (a.tris == b.tris && (a.size - b.size).magnitude < 0.05f) problems.Add($"{tower}: {a.model} and {b.model} look alike");
                if (a.far == b.far) problems.Add($"{tower}: the far levels of {a.model} and {b.model} are alike");
                if (Icons.Source(a.icon) == Icons.Source(b.icon)) problems.Add($"{tower}: one icon for both branches");
            }
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }

        [Test]
        public void RankDetailsGrowWithTheRank()
        {
            TowerRankDetails.Clear();
            Assert.AreEqual((1, 0), TowerRankDetails.Tier(1));
            Assert.AreEqual((3, 1), TowerRankDetails.Tier(3));
            Assert.AreEqual((5, 2), TowerRankDetails.Tier(5));
            Assert.AreEqual((6, 2), TowerRankDetails.Tier(7), "a branch keeps six bars and the heavy plates");
            foreach (var model in new[] { "gun_turret", "mg_bunker", "guard_tower", "heavy_turret", "gun_turret_b" })
            {
                var one = TowerRankDetails.For(model, 1, false);
                var three = TowerRankDetails.For(model, 3, false);
                var five = TowerRankDetails.For(model, 5, false);
                var lean = TowerRankDetails.For(model, 5, true);
                Assert.IsNotNull(one, model + ": rank bars");
                Assert.Less(one.vertexCount, three.vertexCount, model + ": more at rank 3");
                Assert.Less(three.vertexCount, five.vertexCount, model + ": more at rank 5");
                Assert.LessOrEqual(lean.vertexCount, five.vertexCount, model + ": leaner on Low graphics");
                Assert.AreEqual(2, five.subMeshCount, model + ": plates and bars");
                Assert.AreEqual(0, one.GetTriangles(0).Length, model + ": no plates below rank 3");
                Assert.Greater(three.GetTriangles(0).Length, 0, model + ": plates at rank 3");
                Assert.Greater(five.bounds.size.magnitude, 0.5f);
                // Faces point out (wound clockwise seen from outside, as Unity draws them).
                var verts = five.vertices;
                var normals = five.normals;
                for (var s = 0; s < 2; s++)
                {
                    var tris = five.GetTriangles(s);
                    for (var i = 0; i < tris.Length; i += 3)
                    {
                        var n = Vector3.Cross(verts[tris[i + 1]] - verts[tris[i]], verts[tris[i + 2]] - verts[tris[i]]);
                        Assert.Greater(Vector3.Dot(n, normals[tris[i]]), 0f, model + ": a face points inward");
                    }
                }
            }
            var root = new GameObject("rank");
            try
            {
                var renderer = TowerRankDetails.Attach(root.transform, "gun_turret", 5, 1, _materials);
                Assert.IsNotNull(renderer);
                Assert.AreEqual(2, renderer.sharedMaterials.Length);
            }
            finally
            {
                Object.DestroyImmediate(root);
            }
        }

        [Test]
        public void ABranchShowsRankSevenAndATowerItsCardsRank()
        {
            var catalog = GameContent.LoadCatalog();
            TowerArt.Ranks = (team, card) => team == 0 ? 3 : 1;
            Assert.AreEqual(3, TowerArt.RankOf(0, catalog.Vehicles["gun_turret"]));
            Assert.AreEqual(1, TowerArt.RankOf(1, catalog.Vehicles["gun_turret"]));
            Assert.AreEqual(TowerCards.BranchRank, TowerArt.RankOf(1, catalog.Vehicles["gun_turret.long"]));
            Assert.IsTrue(TowerArt.WearsRank(catalog.Vehicles["gun_turret"]));
            Assert.IsFalse(TowerArt.WearsRank(catalog.Vehicles["headquarters"]));
            // The id table's model id for a branch (DECISIONS 19U).
            Assert.AreEqual("gun_turret_b", TowerArt.BranchModel("gun_turret.auto"));
        }

        private static int Triangles(GameObject prefab) =>
            prefab.GetComponentsInChildren<MeshFilter>(true).Where(f => f.sharedMesh != null).Sum(f => f.sharedMesh.triangles.Length / 3);

        private static Vector3 Size(GameObject prefab)
        {
            var bounds = new Bounds();
            var first = true;
            foreach (var f in prefab.GetComponentsInChildren<MeshFilter>(true))
            {
                if (f.sharedMesh == null) continue;
                var b = f.sharedMesh.bounds;
                var m = prefab.transform.worldToLocalMatrix * f.transform.localToWorldMatrix;
                for (var i = 0; i < 8; i++)
                {
                    var p = m.MultiplyPoint3x4(new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y,
                        (i & 4) == 0 ? b.min.z : b.max.z));
                    if (first) bounds = new Bounds(p, Vector3.zero);
                    else bounds.Encapsulate(p);
                    first = false;
                }
            }
            return bounds.size;
        }

        private static Transform Find(Transform root, string name)
        {
            if (root.name == name) return root;
            foreach (Transform child in root)
                if (Find(child, name) is { } found) return found;
            return null;
        }
    }
}
