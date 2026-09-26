using NUnit.Framework;
using MachineBrigade.Voxel;
using UnityEngine;

namespace MachineBrigade.Tests
{
    public class VoxelTests
    {
        private static readonly Color32[] Palette = VoxelPalette.Neutral;

        [Test]
        public void SingleVoxelMakesACubeWithOutwardNormals()
        {
            var model = new VoxelModel(1, 1, 1);
            model.Set(0, 0, 0, VoxelPalette.Stone);

            var mesh = VoxelMesher.Build(model, Palette, 1f, new Vector3(0.5f, 0.5f, 0.5f), "cube");
            try
            {
                Assert.AreEqual(24, mesh.vertexCount);
                Assert.AreEqual(36, mesh.triangles.Length);
                var vertices = mesh.vertices;
                var triangles = mesh.triangles;
                for (var t = 0; t < triangles.Length; t += 3)
                {
                    Vector3 a = vertices[triangles[t]], b = vertices[triangles[t + 1]], c = vertices[triangles[t + 2]];
                    var faceNormal = Vector3.Cross(b - a, c - a);
                    var centre = (a + b + c) / 3f;
                    Assert.Greater(Vector3.Dot(faceNormal, centre), 0f, "every face must point away from the centre");
                }
            }
            finally
            {
                Object.DestroyImmediate(mesh);
            }
        }

        [Test]
        public void SameColouredFacesMergeIntoOneQuad()
        {
            var model = new VoxelModel(4, 1, 1);
            model.Box(0, 0, 0, 4, 1, 1, VoxelPalette.Stone);

            var mesh = VoxelMesher.Build(model, Palette, 1f, Vector3.zero, "bar");
            try
            {
                Assert.AreEqual(6 * 4, mesh.vertexCount, "a 4x1x1 bar is still six quads");
            }
            finally
            {
                Object.DestroyImmediate(mesh);
            }
        }

        [Test]
        public void EveryShapeBuildsANonEmptyMesh()
        {
            foreach (var id in new[] { "scout_jeep", "light_tank", "main_battle_tank", "artillery" })
            {
                var vehicle = VoxelShapes.Vehicle(id);
                Assert.Greater(vehicle.Hull.CountSolid(), 0, id);
                Assert.Greater(vehicle.Turret.CountSolid(), 0, id);
            }
            foreach (var id in new[] { "house_small", "house_large", "wall", "fuel_tank", "barrel", "ammo_crate", "tree" })
                Assert.Greater(VoxelShapes.Prop(id).CountSolid(), 0, id);
        }

        [Test]
        public void ChunksCoverTheModelWithoutLosingVoxels()
        {
            var model = VoxelShapes.Prop("house_small");
            var chunks = VoxelChunker.Split(model, 3, 2, 3, minSolid: 0);

            var total = 0;
            foreach (var chunk in chunks) total += chunk.Model.CountSolid();
            Assert.AreEqual(model.CountSolid(), total);
        }
    }
}
