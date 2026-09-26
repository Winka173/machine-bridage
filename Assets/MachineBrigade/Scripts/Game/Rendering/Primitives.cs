using MachineBrigade.Voxel;
using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Small procedural meshes. All carry vertex colours, because the project shaders
    /// multiply by them and some graphics APIs leave a missing colour stream black.
    /// </summary>
    public static class Primitives
    {
        public static Mesh Quad(Color color)
        {
            color = VoxelMesher.ToShader(color);
            var mesh = new Mesh { name = "Quad" };
            mesh.SetVertices(new[]
            {
                new Vector3(-0.5f, -0.5f, 0f), new Vector3(0.5f, -0.5f, 0f),
                new Vector3(0.5f, 0.5f, 0f), new Vector3(-0.5f, 0.5f, 0f),
            });
            mesh.SetUVs(0, new[] { new Vector2(0f, 0f), new Vector2(1f, 0f), new Vector2(1f, 1f), new Vector2(0f, 1f) });
            mesh.SetColors(new[] { color, color, color, color });
            mesh.SetNormals(new[] { Vector3.back, Vector3.back, Vector3.back, Vector3.back });
            mesh.SetTriangles(new[] { 0, 2, 1, 0, 3, 2 }, 0); // front face towards -Z
            mesh.RecalculateBounds();
            return mesh;
        }

        public static Mesh Ring(float innerRadius, float outerRadius, int segments)
        {
            var vertices = new Vector3[segments * 2];
            var colors = new Color[segments * 2];
            var normals = new Vector3[segments * 2];
            var triangles = new int[segments * 6];
            for (var i = 0; i < segments; i++)
            {
                var angle = i * Mathf.PI * 2f / segments;
                var direction = new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle));
                vertices[i * 2] = direction * innerRadius;
                vertices[i * 2 + 1] = direction * outerRadius;
                colors[i * 2] = colors[i * 2 + 1] = Color.white;
                normals[i * 2] = normals[i * 2 + 1] = Vector3.up;

                int inner = i * 2, outer = i * 2 + 1;
                int nextInner = (i + 1) % segments * 2, nextOuter = nextInner + 1;
                var t = i * 6;
                // Wound so the face points up (+Y).
                triangles[t] = inner; triangles[t + 1] = nextOuter; triangles[t + 2] = outer;
                triangles[t + 3] = inner; triangles[t + 4] = nextInner; triangles[t + 5] = nextOuter;
            }

            var mesh = new Mesh { name = "Ring" };
            mesh.SetVertices(vertices);
            mesh.SetColors(colors);
            mesh.SetNormals(normals);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        public static Mesh Box()
        {
            var cube = new VoxelModel(1, 1, 1);
            cube.Set(0, 0, 0, 1);
            var palette = new Color32[256];
            palette[1] = new Color32(255, 255, 255, 255);
            return VoxelMesher.Build(cube, palette, 1f, new Vector3(0.5f, 0.5f, 0.5f), "Box");
        }
    }
}
