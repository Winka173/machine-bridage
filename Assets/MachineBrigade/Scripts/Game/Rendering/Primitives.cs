using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Small procedural meshes. All carry vertex colours, because the project shaders multiply
    /// by them and some graphics APIs leave a missing colour stream black.
    /// </summary>
    public static class Primitives
    {
        /// <summary>
        /// Vertex colours reach shaders unconverted. Colours authored in sRGB must be linearised
        /// in a Linear-colour-space project or they look washed out.
        /// </summary>
        public static Color Linear(Color color) =>
            QualitySettings.activeColorSpace == ColorSpace.Linear ? color.linear : color;

        public static Mesh Quad(Color color)
        {
            color = Linear(color);
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

        /// <summary>Unit cube centred on its origin, with flat normals.</summary>
        public static Mesh Box()
        {
            var vertices = new Vector3[24];
            var normals = new Vector3[24];
            var colors = new Color[24];
            var triangles = new int[36];
            var faces = new[] { Vector3.right, Vector3.left, Vector3.up, Vector3.down, Vector3.forward, Vector3.back };
            for (var f = 0; f < 6; f++)
            {
                var n = faces[f];
                var u = f < 2 ? Vector3.forward : Vector3.right;
                var v = Vector3.Cross(n, u);
                u = Vector3.Cross(v, n); // now cross(u, v) = n
                for (var k = 0; k < 4; k++)
                {
                    var su = k == 1 || k == 2 ? 0.5f : -0.5f;
                    var sv = k >= 2 ? 0.5f : -0.5f;
                    vertices[f * 4 + k] = n * 0.5f + u * su + v * sv;
                    normals[f * 4 + k] = n;
                    colors[f * 4 + k] = Color.white;
                }
                // Unity treats cross(v1 - v0, v2 - v0) as the front; cross(u, u + v) = n points outward.
                var b = f * 4;
                triangles[f * 6] = b; triangles[f * 6 + 1] = b + 1; triangles[f * 6 + 2] = b + 2;
                triangles[f * 6 + 3] = b; triangles[f * 6 + 4] = b + 2; triangles[f * 6 + 5] = b + 3;
            }

            var mesh = new Mesh { name = "Box" };
            mesh.SetVertices(vertices);
            mesh.SetNormals(normals);
            mesh.SetColors(colors);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }
    }
}
