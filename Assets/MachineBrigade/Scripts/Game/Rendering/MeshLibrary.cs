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
            Box = Own(Primitives.Box());
        }

        /// <summary>1 x 1 quad facing -Z (towards a camera that shares its rotation).</summary>
        public Mesh Quad { get; }

        public Mesh ScorchQuad { get; }

        /// <summary>Flat ring of outer radius 1 lying on the ground.</summary>
        public Mesh Ring { get; }

        /// <summary>Unit cube centred on its origin.</summary>
        public Mesh Box { get; }

        public void Dispose()
        {
            foreach (var mesh in _owned)
                if (mesh != null) Object.Destroy(mesh);
            _owned.Clear();
        }

        private Mesh Own(Mesh mesh)
        {
            _owned.Add(mesh);
            return mesh;
        }
    }
}
