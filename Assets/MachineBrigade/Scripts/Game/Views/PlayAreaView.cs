using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// The edge of a multi-stage mission's play area, drawn on the ground as a dashed amber line:
    /// the player's side goes no further until the next stage opens more of the map.
    /// </summary>
    public sealed class PlayAreaView
    {
        private const float Dash = 2.5f, Gap = 1.5f, Width = 0.8f;
        private readonly GameObject _line;
        private readonly MeshFilter _filter;
        private Mesh _mesh;

        public PlayAreaView(MaterialLibrary materials, Transform parent)
        {
            _line = new GameObject("Play Area");
            _line.transform.SetParent(parent, false);
            _filter = _line.AddComponent<MeshFilter>();
            var renderer = _line.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = materials.MarkScout;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            _line.SetActive(false);
        }

        /// <summary>Shows the edge of <paramref name="area"/>, or hides it (null: the whole map is open).</summary>
        public void Show(PlayArea? area)
        {
            if (area is not { } a)
            {
                _line.SetActive(false);
                return;
            }
            var corners = new[]
            {
                new Vector2(a.Min.X, a.Min.Y), new Vector2(a.Max.X, a.Min.Y), new Vector2(a.Max.X, a.Max.Y), new Vector2(a.Min.X, a.Max.Y),
            };
            var vertices = new List<Vector3>();
            var triangles = new List<int>();
            for (var i = 0; i < 4; i++)
            {
                var from = corners[i];
                var to = corners[(i + 1) % 4];
                var length = Vector2.Distance(from, to);
                if (length < 0.01f) continue;
                var dir = (to - from) / length;
                var side = new Vector2(-dir.y, dir.x) * (Width * 0.5f);
                for (var at = 0f; at < length; at += Dash + Gap)
                {
                    var p0 = from + dir * at;
                    var p1 = from + dir * Mathf.Min(length, at + Dash);
                    var n = vertices.Count;
                    vertices.Add(new Vector3(p0.x - side.x, 0.07f, p0.y - side.y));
                    vertices.Add(new Vector3(p0.x + side.x, 0.07f, p0.y + side.y));
                    vertices.Add(new Vector3(p1.x + side.x, 0.07f, p1.y + side.y));
                    vertices.Add(new Vector3(p1.x - side.x, 0.07f, p1.y - side.y));
                    triangles.AddRange(new[] { n, n + 1, n + 2, n, n + 2, n + 3 });
                }
            }
            if (_mesh == null) _mesh = new Mesh { name = "Play Area Edge", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            _mesh.Clear();
            _mesh.SetVertices(vertices);
            _mesh.SetTriangles(triangles, 0);
            _mesh.RecalculateBounds();
            _filter.sharedMesh = _mesh;
            _line.SetActive(true);
        }
    }
}
