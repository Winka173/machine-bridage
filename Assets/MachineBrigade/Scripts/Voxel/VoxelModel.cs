using System;
using UnityEngine;

namespace MachineBrigade.Voxel
{
    /// <summary>
    /// A dense grid of palette indices (0 = empty). Models are authored in code with the
    /// drawing helpers below, then turned into meshes by <see cref="VoxelMesher"/>.
    /// </summary>
    public sealed class VoxelModel
    {
        private readonly byte[] _cells;

        public VoxelModel(int sizeX, int sizeY, int sizeZ)
        {
            if (sizeX <= 0 || sizeY <= 0 || sizeZ <= 0) throw new ArgumentException("Voxel model sizes must be positive.");
            SizeX = sizeX;
            SizeY = sizeY;
            SizeZ = sizeZ;
            _cells = new byte[sizeX * sizeY * sizeZ];
        }

        public int SizeX { get; }
        public int SizeY { get; }
        public int SizeZ { get; }

        public Vector3Int Size => new Vector3Int(SizeX, SizeY, SizeZ);

        public bool InBounds(int x, int y, int z) =>
            x >= 0 && y >= 0 && z >= 0 && x < SizeX && y < SizeY && z < SizeZ;

        public byte Get(int x, int y, int z) => InBounds(x, y, z) ? _cells[(y * SizeZ + z) * SizeX + x] : (byte)0;

        public void Set(int x, int y, int z, byte color)
        {
            if (InBounds(x, y, z)) _cells[(y * SizeZ + z) * SizeX + x] = color;
        }

        /// <summary>Fills the box from the min corner (inclusive) to the max corner (exclusive), clipped to the model.</summary>
        public void Box(int x0, int y0, int z0, int x1, int y1, int z1, byte color)
        {
            for (var y = Math.Max(0, y0); y < Math.Min(SizeY, y1); y++)
            for (var z = Math.Max(0, z0); z < Math.Min(SizeZ, z1); z++)
            for (var x = Math.Max(0, x0); x < Math.Min(SizeX, x1); x++)
                _cells[(y * SizeZ + z) * SizeX + x] = color;
        }

        /// <summary>Vertical cylinder centred on (cx, cz) in voxel units, layers y0 (inclusive) to y1 (exclusive).</summary>
        public void Cylinder(float cx, float cz, float radius, int y0, int y1, byte color)
        {
            var r2 = radius * radius;
            for (var y = Math.Max(0, y0); y < Math.Min(SizeY, y1); y++)
            for (var z = 0; z < SizeZ; z++)
            for (var x = 0; x < SizeX; x++)
            {
                float dx = x + 0.5f - cx, dz = z + 0.5f - cz;
                if (dx * dx + dz * dz <= r2) Set(x, y, z, color);
            }
        }

        public void Ellipsoid(float cx, float cy, float cz, float rx, float ry, float rz, byte color)
        {
            for (var y = 0; y < SizeY; y++)
            for (var z = 0; z < SizeZ; z++)
            for (var x = 0; x < SizeX; x++)
            {
                float dx = (x + 0.5f - cx) / rx, dy = (y + 0.5f - cy) / ry, dz = (z + 0.5f - cz) / rz;
                if (dx * dx + dy * dy + dz * dz <= 1f) Set(x, y, z, color);
            }
        }

        /// <summary>Recolours solid voxels matching a predicate; used for surface detail such as windows.</summary>
        public void Paint(Func<int, int, int, bool> where, byte color)
        {
            for (var y = 0; y < SizeY; y++)
            for (var z = 0; z < SizeZ; z++)
            for (var x = 0; x < SizeX; x++)
                if (Get(x, y, z) != 0 && where(x, y, z)) Set(x, y, z, color);
        }

        /// <summary>Copies the region [min, max) into a new model.</summary>
        public VoxelModel Crop(Vector3Int min, Vector3Int max)
        {
            var size = max - min;
            var result = new VoxelModel(size.x, size.y, size.z);
            for (var y = 0; y < size.y; y++)
            for (var z = 0; z < size.z; z++)
            for (var x = 0; x < size.x; x++)
                result.Set(x, y, z, Get(min.x + x, min.y + y, min.z + z));
            return result;
        }

        public int CountSolid()
        {
            var count = 0;
            foreach (var c in _cells)
                if (c != 0) count++;
            return count;
        }
    }
}
