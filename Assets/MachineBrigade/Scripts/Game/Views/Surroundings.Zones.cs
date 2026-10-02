using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 33 L1: the four zones beyond the battlefield. The decorated square reaches the outer ring's far edge (the
    /// edge band plus the widest camera frame + 15 %, <see cref="CameraFrame"/>); in the ring's far half the theme's
    /// trees are drawn as their biome's HLOD stand-in (a few dozen triangles, still instanced); and zone 4, the horizon,
    /// is the range carried on in coarse cells out past the square into the fog, over the horizon ground.
    /// </summary>
    public sealed partial class Surroundings
    {
        /// <summary>The HLOD stand-in drawn for the theme's trees in the far ring (null: keep the trees).</summary>
        private readonly string _farTree;

        private readonly HashSet<string> _treeModels = new();

        /// <summary>Cell of the horizon range (it is only ever seen in the fog, from the menu or a preview).</summary>
        private const float HorizonCell = 20f;

        /// <summary>How far the horizon range reaches, as a multiple of the decorated square's half-size.</summary>
        private const float HorizonReach = 1.8f;

        private string FarTree(ModelLibrary models, MapTheme theme)
        {
            foreach (var pool in new[] { theme.LowlandTrees, theme.HighlandTrees, theme.Trees })
                if (pool != null)
                    foreach (var poolId in pool) _treeModels.Add(poolId);
            var id = _dress != null && !string.IsNullOrEmpty(_dress.farTree) ? _dress.farTree : _biome?.farTree;
            if (string.IsNullOrEmpty(id) || id == "none") return null;
            return models.Has(id) ? id : null;
        }

        /// <summary>The model to draw for <paramref name="modelId"/> at <paramref name="position"/>: a tree in the ring's far half is its HLOD stand-in.</summary>
        private string FarModel(string modelId, Vector2 position) =>
            _farTree != null && _treeModels.Contains(modelId) && Beyond(position) >= _zones.HlodStart ? _farTree : modelId;

        /// <summary>
        /// Zone 4: the range's height field carried on outside the decorated square in <see cref="HorizonCell"/> cells,
        /// to <see cref="HorizonReach"/> times its half-size. The square is a whole number of cells wide, so every coarse
        /// cell is wholly outside the fine range (no overlap); flat cells and the sea are left to the horizon ground.
        /// </summary>
        private Mesh HorizonRange()
        {
            var vertices = new List<Vector3>();
            var normals = new List<Vector3>();
            var uvs = new List<Vector2>();
            var triangles = new List<int>();
            var across = Mathf.Max(1, Mathf.CeilToInt(Extent * 2f / HorizonCell));
            var cell = Extent * 2f / across;
            var rim = Mathf.CeilToInt(Extent * (HorizonReach - 1f) / cell);
            var count = across + rim * 2;
            var origin = new Vector2(_centre.x - Extent - rim * cell, _centre.y - Extent - rim * cell);
            var heights = new float[(count + 1) * (count + 1)];
            for (var z = 0; z <= count; z++)
            for (var x = 0; x <= count; x++)
            {
                var p = origin + new Vector2(x * cell, z * cell);
                heights[z * (count + 1) + x] = InSea(p, 0f) ? 0f : Height(p);
            }

            void Triangle(Vector3 a, Vector3 b, Vector3 c)
            {
                var normal = Vector3.Cross(b - a, c - a).normalized;
                if (normal.y < 0f)
                {
                    (b, c) = (c, b);
                    normal = -normal;
                }
                var uv = new Vector2(Mathf.Clamp01((a.y + b.y + c.y) / 3f / (SnowLine + 8f)), Mathf.Clamp01(Slope(normal) * 1.6f));
                var start = vertices.Count;
                vertices.Add(a);
                vertices.Add(b);
                vertices.Add(c);
                for (var k = 0; k < 3; k++)
                {
                    normals.Add(normal);
                    uvs.Add(uv);
                    triangles.Add(start + k);
                }
            }

            for (var z = 0; z < count; z++)
            for (var x = 0; x < count; x++)
            {
                // The fine range covers the square's cells.
                if (x >= rim && x < rim + across && z >= rim && z < rim + across) continue;
                var h00 = heights[z * (count + 1) + x];
                var h10 = heights[z * (count + 1) + x + 1];
                var h01 = heights[(z + 1) * (count + 1) + x];
                var h11 = heights[(z + 1) * (count + 1) + x + 1];
                if (h00 < 0.05f && h10 < 0.05f && h01 < 0.05f && h11 < 0.05f) continue;
                float Y(float h) => h < 0.05f ? -0.4f : h;
                var x0 = origin.x + x * cell;
                var z0 = origin.y + z * cell;
                var p00 = new Vector3(x0, Y(h00), z0);
                var p10 = new Vector3(x0 + cell, Y(h10), z0);
                var p01 = new Vector3(x0, Y(h01), z0 + cell);
                var p11 = new Vector3(x0 + cell, Y(h11), z0 + cell);
                if (((x + z) & 1) == 0)
                {
                    Triangle(p00, p01, p11);
                    Triangle(p00, p11, p10);
                }
                else
                {
                    Triangle(p00, p01, p10);
                    Triangle(p10, p01, p11);
                }
            }

            var mesh = new Mesh { name = "Horizon Range", indexFormat = IndexFormat.UInt32 };
            mesh.SetVertices(vertices);
            mesh.SetNormals(normals);
            mesh.SetUVs(0, uvs);
            var colours = new Color[vertices.Count];
            for (var i = 0; i < colours.Length; i++) colours[i] = Color.white;
            mesh.SetColors(colours);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }
    }
}
