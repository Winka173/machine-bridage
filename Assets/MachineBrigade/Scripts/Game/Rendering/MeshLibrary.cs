using System;
using System.Collections.Generic;
using MachineBrigade.Voxel;
using UnityEngine;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    public sealed class VehicleMeshes
    {
        public VehicleMeshes(Mesh hull, Mesh turret, Vector3 turretOffset, float muzzleHeight)
        {
            Hull = hull;
            Turret = turret;
            TurretOffset = turretOffset;
            MuzzleHeight = muzzleHeight;
        }

        public Mesh Hull { get; }
        public Mesh Turret { get; }
        public Vector3 TurretOffset { get; }
        public float MuzzleHeight { get; }
    }

    /// <summary>A debris piece: its mesh is centred on itself so it tumbles naturally.</summary>
    public readonly struct ChunkMesh
    {
        public ChunkMesh(Mesh mesh, Vector3 localCenter, Vector3 size)
        {
            Mesh = mesh;
            LocalCenter = localCenter;
            Size = size;
        }

        public Mesh Mesh { get; }

        /// <summary>Where the piece sits relative to the intact prop's origin.</summary>
        public Vector3 LocalCenter { get; }

        public Vector3 Size { get; }
    }

    public sealed class PropMeshes
    {
        public PropMeshes(Mesh intact, Mesh rubble, IReadOnlyList<ChunkMesh> chunks)
        {
            Intact = intact;
            Rubble = rubble;
            Chunks = chunks;
        }

        public Mesh Intact { get; }

        /// <summary>Null when the prop leaves nothing behind (barrels, trees).</summary>
        public Mesh Rubble { get; }

        public IReadOnlyList<ChunkMesh> Chunks { get; }
    }

    /// <summary>Builds voxel meshes on first use and shares them between every instance.</summary>
    public sealed class MeshLibrary : IDisposable
    {
        private readonly Dictionary<(string, int), VehicleMeshes> _vehicles = new();
        private readonly Dictionary<string, PropMeshes> _props = new();
        private readonly List<Mesh> _owned = new();

        public MeshLibrary()
        {
            Quad = Own(Primitives.Quad(Color.white));
            ScorchQuad = Own(Primitives.Quad(new Color(0.05f, 0.04f, 0.035f, 0.85f)));
            Ring = Own(Primitives.Ring(0.82f, 1f, 40));
            Box = Own(Primitives.Box());
        }

        /// <summary>1 x 1 quad facing -Z (towards a camera that shares its rotation).</summary>
        public Mesh Quad { get; }

        public Mesh ScorchQuad { get; }

        /// <summary>Flat ring of outer radius 1 lying on the ground.</summary>
        public Mesh Ring { get; }

        /// <summary>Unit cube centred on its origin.</summary>
        public Mesh Box { get; }

        public VehicleMeshes Vehicle(string defId, int team)
        {
            if (_vehicles.TryGetValue((defId, team), out var cached)) return cached;
            var model = VoxelShapes.Vehicle(defId);
            var palette = VoxelPalette.Create(TeamColors.Main(team), TeamColors.Dark(team));
            const float s = VoxelShapes.VoxelSize;
            var meshes = new VehicleMeshes(
                Own(VoxelMesher.Build(model.Hull, palette, s, model.HullPivot, $"{defId}_hull_{team}")),
                Own(VoxelMesher.Build(model.Turret, palette, s, model.TurretPivot, $"{defId}_turret_{team}")),
                (model.TurretMount - model.HullPivot) * s,
                model.MuzzleHeight * s);
            _vehicles[(defId, team)] = meshes;
            return meshes;
        }

        public PropMeshes Prop(string defId)
        {
            if (_props.TryGetValue(defId, out var cached)) return cached;
            const float s = VoxelShapes.VoxelSize;
            var model = VoxelShapes.Prop(defId);
            var pivot = new Vector3(model.SizeX * 0.5f, 0f, model.SizeZ * 0.5f);
            var intact = Own(VoxelMesher.Build(model, VoxelPalette.Neutral, s, pivot, defId));

            Mesh rubble = null;
            if (defId.StartsWith("house", StringComparison.Ordinal) || defId == "wall")
            {
                var pile = VoxelShapes.Rubble(model.SizeX, model.SizeZ, defId.GetHashCode());
                rubble = Own(VoxelMesher.Build(pile, VoxelPalette.Neutral, s, pivot, defId + "_rubble"));
            }

            var large = model.SizeX >= 16 || model.SizeZ >= 16;
            var pieces = large
                ? VoxelChunker.Split(model, 3, 2, 3)
                : VoxelChunker.Split(model, 2, Math.Max(1, model.SizeY / 6), 2, minSolid: 2);
            var chunks = new List<ChunkMesh>(pieces.Count);
            foreach (var piece in pieces)
            {
                var size = (Vector3)piece.Model.Size;
                var mesh = Own(VoxelMesher.Build(piece.Model, VoxelPalette.Neutral, s, size * 0.5f, defId + "_chunk"));
                var localCenter = ((Vector3)piece.Offset + size * 0.5f - pivot) * s;
                chunks.Add(new ChunkMesh(mesh, localCenter, size * s));
            }

            var result = new PropMeshes(intact, rubble, chunks);
            _props[defId] = result;
            return result;
        }

        public void Dispose()
        {
            foreach (var mesh in _owned)
                if (mesh != null) Object.Destroy(mesh);
            _owned.Clear();
            _vehicles.Clear();
            _props.Clear();
        }

        private Mesh Own(Mesh mesh)
        {
            _owned.Add(mesh);
            return mesh;
        }
    }
}
