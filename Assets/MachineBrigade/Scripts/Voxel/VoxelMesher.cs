using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Voxel
{
    /// <summary>
    /// Greedy mesher: merges coplanar faces of the same colour into large quads, so a
    /// 30x7x36 tank becomes a few hundred triangles instead of thousands. Output has flat
    /// normals and per-vertex colours for the VoxelLit shader.
    /// </summary>
    public static class VoxelMesher
    {
        public static Mesh Build(VoxelModel model, Color32[] palette, float voxelSize, Vector3 pivot, string name)
        {
            var vertices = new List<Vector3>();
            var normals = new List<Vector3>();
            var colors = new List<Color>();
            var triangles = new List<int>();
            var dims = new[] { model.SizeX, model.SizeY, model.SizeZ };
            var x = new int[3];
            var q = new int[3];

            for (var d = 0; d < 3; d++)
            {
                int u = (d + 1) % 3, v = (d + 2) % 3;
                var mask = new int[dims[u] * dims[v]];
                q[0] = q[1] = q[2] = 0;
                q[d] = 1;

                for (x[d] = -1; x[d] < dims[d];)
                {
                    // Mask of faces between slice x[d] and x[d] + 1: +colour faces point along +d, -colour along -d.
                    var n = 0;
                    for (x[v] = 0; x[v] < dims[v]; x[v]++)
                    for (x[u] = 0; x[u] < dims[u]; x[u]++)
                    {
                        int a = x[d] >= 0 ? model.Get(x[0], x[1], x[2]) : 0;
                        int b = x[d] < dims[d] - 1 ? model.Get(x[0] + q[0], x[1] + q[1], x[2] + q[2]) : 0;
                        mask[n++] = (a != 0) == (b != 0) ? 0 : a != 0 ? a : -b;
                    }
                    x[d]++;

                    n = 0;
                    for (var j = 0; j < dims[v]; j++)
                    for (var i = 0; i < dims[u];)
                    {
                        var c = mask[n];
                        if (c == 0)
                        {
                            i++;
                            n++;
                            continue;
                        }

                        var w = 1;
                        while (i + w < dims[u] && mask[n + w] == c) w++;
                        var h = 1;
                        for (; j + h < dims[v]; h++)
                        {
                            var rowMatches = true;
                            for (var k = 0; k < w; k++)
                                if (mask[n + k + h * dims[u]] != c) { rowMatches = false; break; }
                            if (!rowMatches) break;
                        }

                        x[u] = i;
                        x[v] = j;
                        var du = new int[3];
                        var dv = new int[3];
                        du[u] = w;
                        dv[v] = h;
                        EmitQuad(vertices, normals, colors, triangles, x, du, dv, d, c > 0, ToShader(palette[c > 0 ? c : -c]),
                            voxelSize, pivot);

                        for (var l = 0; l < h; l++)
                        for (var k = 0; k < w; k++)
                            mask[n + k + l * dims[u]] = 0;
                        i += w;
                        n += w;
                    }
                }
            }

            var mesh = new Mesh { name = name };
            if (vertices.Count > 65535) mesh.indexFormat = IndexFormat.UInt32;
            mesh.SetVertices(vertices);
            mesh.SetNormals(normals);
            mesh.SetColors(colors);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>
        /// Palette colours are authored in sRGB, but vertex colours reach shaders unconverted.
        /// In a Linear project they must be linearised here or every model looks washed out.
        /// </summary>
        public static Color ToShader(Color color) =>
            QualitySettings.activeColorSpace == ColorSpace.Linear ? color.linear : color;

        public static Color ToShader(Color32 color) => ToShader((Color)color);

        private static void EmitQuad(List<Vector3> vertices, List<Vector3> normals, List<Color> colors, List<int> triangles,
            int[] origin, int[] du, int[] dv, int axis, bool positive, Color color, float voxelSize, Vector3 pivot)
        {
            var o = new Vector3(origin[0], origin[1], origin[2]);
            var a = new Vector3(du[0], du[1], du[2]);
            var b = new Vector3(dv[0], dv[1], dv[2]);
            var normal = Vector3.zero;
            normal[axis] = positive ? 1f : -1f;

            var start = vertices.Count;
            vertices.Add((o - pivot) * voxelSize);
            vertices.Add((o + a - pivot) * voxelSize);
            vertices.Add((o + a + b - pivot) * voxelSize);
            vertices.Add((o + b - pivot) * voxelSize);
            for (var k = 0; k < 4; k++)
            {
                normals.Add(normal);
                colors.Add(color);
            }

            // cross(a, b) points along +axis, and Unity treats cross(v1 - v0, v2 - v0) as the front face.
            if (positive)
            {
                triangles.Add(start); triangles.Add(start + 1); triangles.Add(start + 2);
                triangles.Add(start); triangles.Add(start + 2); triangles.Add(start + 3);
            }
            else
            {
                triangles.Add(start); triangles.Add(start + 2); triangles.Add(start + 1);
                triangles.Add(start); triangles.Add(start + 3); triangles.Add(start + 2);
            }
        }
    }
}
