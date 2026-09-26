using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Voxel
{
    /// <summary>One piece of a model, used as flying debris.</summary>
    public sealed class VoxelChunk
    {
        public VoxelChunk(VoxelModel model, Vector3Int offset)
        {
            Model = model;
            Offset = offset;
        }

        public VoxelModel Model { get; }

        /// <summary>Position of the chunk's min corner inside the source model, in voxels.</summary>
        public Vector3Int Offset { get; }
    }

    /// <summary>
    /// Pre-splits models into a few chunks. Destruction then throws a handful of rigid pieces
    /// instead of simulating individual voxels, which keeps physics cost fixed and small.
    /// </summary>
    public static class VoxelChunker
    {
        public static List<VoxelChunk> Split(VoxelModel model, int countX, int countY, int countZ, int minSolid = 4)
        {
            var chunks = new List<VoxelChunk>();
            for (var cy = 0; cy < countY; cy++)
            for (var cz = 0; cz < countZ; cz++)
            for (var cx = 0; cx < countX; cx++)
            {
                var min = new Vector3Int(model.SizeX * cx / countX, model.SizeY * cy / countY, model.SizeZ * cz / countZ);
                var max = new Vector3Int(model.SizeX * (cx + 1) / countX, model.SizeY * (cy + 1) / countY,
                    model.SizeZ * (cz + 1) / countZ);
                if (max.x <= min.x || max.y <= min.y || max.z <= min.z) continue;
                var piece = model.Crop(min, max);
                if (piece.CountSolid() >= minSolid) chunks.Add(new VoxelChunk(piece, min));
            }
            return chunks;
        }
    }
}
