using System;
using System.Collections.Generic;
using UnityEngine;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>Procedural helper meshes (rings, quads, boxes) shared by every instance.</summary>
    public sealed class MeshLibrary : IDisposable
    {
        private readonly List<Mesh> _owned = new();

        public MeshLibrary()
        {
            Quad = Own(Primitives.Quad(Color.white));
            ScorchQuad = Own(Primitives.Quad(new Color(0.05f, 0.04f, 0.035f, 0.85f)));
            Ring = Own(Primitives.Ring(0.82f, 1f, 48));
            ThinRing = Own(Primitives.Ring(0.955f, 1f, 96));
            Box = Own(Primitives.Box());
            GroundQuad = Own(FlatQuad());
        }

        /// <summary>A 2 x 2 quad lying on the ground (radius 1), UVs 0..1, for ground markings.</summary>
        public Mesh GroundQuad { get; }

        /// <summary>1 x 1 quad facing -Z (towards a camera that shares its rotation).</summary>
        public Mesh Quad { get; }

        public Mesh ScorchQuad { get; }

        /// <summary>Flat ring of outer radius 1 lying on the ground.</summary>
        public Mesh Ring { get; }

        /// <summary>A hairline ring for large circles (objectives, strike telegraphs).</summary>
        public Mesh ThinRing { get; }

        /// <summary>Unit cube centred on its origin.</summary>
        public Mesh Box { get; }

        public void Dispose()
        {
            foreach (var mesh in _owned)
                if (mesh != null) Object.Destroy(mesh);
            _owned.Clear();
        }

        private static Mesh FlatQuad()
        {
            var mesh = new Mesh { name = "Ground Quad" };
            mesh.SetVertices(new[] { new Vector3(-1f, 0f, -1f), new Vector3(1f, 0f, -1f), new Vector3(1f, 0f, 1f), new Vector3(-1f, 0f, 1f) });
            mesh.SetUVs(0, new[] { new Vector2(0f, 0f), new Vector2(1f, 0f), new Vector2(1f, 1f), new Vector2(0f, 1f) });
            mesh.SetNormals(new[] { Vector3.up, Vector3.up, Vector3.up, Vector3.up });
            mesh.SetTriangles(new[] { 0, 2, 1, 0, 3, 2 }, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        private Mesh Own(Mesh mesh)
        {
            _owned.Add(mesh);
            return mesh;
        }
    }
}
