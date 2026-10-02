using System;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>The camera frame the outer ring was sized from, as written by Tools/maps/map_dressing.py (a test keeps it equal to the code).</summary>
    [Serializable]
    public sealed class DressingCamera
    {
        public float tiltDegrees, maxZoomSquare, maxZoomLong, yawSquare, yawLong, pad;
        public bool rotates;
        public float[] aspects;
        public float reachSquare, reachLongSide, reachLongEnd, ringSquare, ringLongSide, ringLongEnd;
    }

    /// <summary>
    /// One biome's decoration (prompt 33 L6): instances per hectare in each zone, the weighted model lists, the HLOD
    /// stand-in for the theme's trees in the far ring, and the visual relief per map. Decoration only: drawn
    /// instanced, no collider, never in the simulation or its vision.
    /// </summary>
    [Serializable]
    public sealed class DressingBiome
    {
        public string id;
        public float edgeBand, play, band, ring, far;
        public string[] playSet, bandSet, ringSet, farSet, seaSet, horizonSet;
        public string farTree;
        public int hills, berms, ditches, dryBeds;
    }

    /// <summary>One map family's zones and dressing (the map JSON files themselves are not touched).</summary>
    [Serializable]
    public sealed class DressingMap
    {
        public string id, biome, farTree;
        public float edgeBand, density;
        public int seed, hills, berms, ditches, dryBeds;
    }

    /// <summary>Prompt 33 L2 (view): the prebuilt piece for a corner name of the map's edges data.</summary>
    [Serializable]
    public sealed class DressingCorner
    {
        /// <summary><see cref="first"/>: the edge type on the piece's own -X side (a junction) or its +Z strip (an outer corner).</summary>
        public string piece, model, first;
        public float radius;
    }

    /// <summary>Prompt 33 L2 (view): what dresses a SEA stretch out to the horizon (water only: no land, houses or woods).</summary>
    [Serializable]
    public sealed class DressingSea
    {
        public string[] waves, ships, islands;
        public float waveDensity, laneStep;
        public string surf, stack, quay, crane, containers, laneBuoy;
        public int shipsPerSide, islandsPerSide;
    }

    /// <summary>Prompt 33 L2 (view): an edge type's or modifier's ring dressing (INDUSTRIAL, HARBOR, URBAN, CLIFF).</summary>
    [Serializable]
    public sealed class DressingEdgeSet
    {
        public string key;
        public float ring;
        public string[] set;
    }

    [Serializable]
    public sealed class DressingRail
    {
        public string track, portal;
        public float step;
    }

    [Serializable]
    public sealed class DressingEdges
    {
        public DressingCorner[] corners;
        public DressingSea sea;
        public DressingEdgeSet[] sets;
        public DressingRail rail;

        public DressingCorner Corner(string piece)
        {
            if (corners == null) return null;
            foreach (var c in corners)
                if (c != null && c.piece == piece) return c;
            return null;
        }

        public DressingEdgeSet Set(string key)
        {
            if (sets == null || string.IsNullOrEmpty(key)) return null;
            foreach (var s in sets)
                if (s != null && s.key == key) return s;
            return null;
        }
    }

    /// <summary>
    /// Prompt 33 L3 (view): a landmark model the map has no prop for, stood where map_dressing.py found room for it
    /// (decoration: no collider, no sight blocking; <see cref="onPlay"/> when it stands on drivable ground).
    /// </summary>
    [Serializable]
    public sealed class DressingLandmark
    {
        public string map, id, model;
        public float x, z, yaw, scale;
        public bool onPlay;
    }

    [Serializable]
    public sealed class MapDressingData
    {
        public int version;
        public DressingCamera camera;
        public DressingBiome[] biomes;
        public DressingMap[] maps;
        public DressingEdges edges;
        public DressingLandmark[] landmarks;
    }

    /// <summary>Reads Resources/Data/map_dressing.json (prompt 33 L1 / L6), for the view only.</summary>
    public static class MapDressing
    {
        public const string ResourcePath = "Data/map_dressing";

        /// <summary>The default edge band where a map and its biome give none.</summary>
        public const float DefaultEdgeBand = 16f;

        private static readonly string[] Modes = { "_conquest", "_long", "_sandbox", "_siege" };
        private static MapDressingData _data;

        /// <summary>The shipped file, or an empty set (no dressing) when it is missing or unreadable.</summary>
        public static MapDressingData Data
        {
            get
            {
                if (_data != null) return _data;
                var asset = Resources.Load<TextAsset>(ResourcePath);
                _data = asset != null ? Parse(asset.text) : null;
                return _data ??= new MapDressingData
                {
                    biomes = Array.Empty<DressingBiome>(), maps = Array.Empty<DressingMap>(), landmarks = Array.Empty<DressingLandmark>(),
                };
            }
        }

        public static MapDressingData Parse(string json)
        {
            try
            {
                var data = JsonUtility.FromJson<MapDressingData>(json);
                if (data == null) return null;
                data.biomes ??= Array.Empty<DressingBiome>();
                data.maps ??= Array.Empty<DressingMap>();
                data.landmarks ??= Array.Empty<DressingLandmark>();
                return data;
            }
            catch (ArgumentException)
            {
                return null;
            }
        }

        /// <summary>The map family of a map id: greenvale_conquest, greenvale_long and greenvale_siege are all greenvale.</summary>
        public static string Family(string mapId)
        {
            if (string.IsNullOrEmpty(mapId)) return string.Empty;
            foreach (var mode in Modes)
                if (mapId.EndsWith(mode, StringComparison.Ordinal))
                    return mapId.Substring(0, mapId.Length - mode.Length);
            return mapId;
        }

        /// <summary>The entry for a map id (any mode of the family; an unknown suffix is cut off a part at a time), or null.</summary>
        public static DressingMap ForMap(string mapId)
        {
            var key = Family(mapId);
            while (!string.IsNullOrEmpty(key))
            {
                foreach (var map in Data.maps)
                    if (map != null && map.id == key) return map;
                var cut = key.LastIndexOf('_');
                if (cut <= 0) break;
                key = key.Substring(0, cut);
            }
            return null;
        }

        public static DressingBiome Biome(string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            foreach (var biome in Data.biomes)
                if (biome != null && biome.id == id) return biome;
            return null;
        }

        /// <summary>The biome a map is dressed as: its own entry's, else the one named like its theme, else temperate.</summary>
        public static DressingBiome BiomeFor(DressingMap map, string themeId) =>
            Biome(map?.biome) ?? Biome(themeId) ?? Biome("temperate");

        /// <summary>The edge band in metres: the map's, else its biome's, else <see cref="DefaultEdgeBand"/> (12-20 m).</summary>
        public static float EdgeBand(DressingMap map, DressingBiome biome)
        {
            var band = map != null && map.edgeBand > 0f ? map.edgeBand : biome != null && biome.edgeBand > 0f ? biome.edgeBand : DefaultEdgeBand;
            return Mathf.Clamp(band, MapZones.MinBand, MapZones.MaxBand);
        }

        /// <summary>The fixed scenery seed of a map: its entry's, else the stable hash of its family.</summary>
        public static int Seed(string mapId)
        {
            var map = ForMap(mapId);
            return map != null && map.seed != 0 ? map.seed : StableSeed(Family(mapId));
        }

        /// <summary>FNV-1a (32 bit) of the text's UTF-8 bytes, kept positive; the same as map_dressing.py's stable_seed.</summary>
        public static int StableSeed(string text)
        {
            unchecked
            {
                var hash = 2166136261u;
                foreach (var b in System.Text.Encoding.UTF8.GetBytes(text ?? string.Empty))
                {
                    hash ^= b;
                    hash *= 16777619u;
                }
                return (int)(hash & 0x7FFFFFFFu);
            }
        }

        /// <summary>The landmark models to stand on one map file (its exact id; none for a map without any).</summary>
        public static System.Collections.Generic.List<DressingLandmark> LandmarksFor(string mapId)
        {
            var list = new System.Collections.Generic.List<DressingLandmark>();
            if (string.IsNullOrEmpty(mapId) || Data.landmarks == null) return list;
            foreach (var l in Data.landmarks)
                if (l != null && l.map == mapId) list.Add(l);
            return list;
        }

        /// <summary>For tests: forget the loaded file.</summary>
        internal static void Reset() => _data = null;
    }
}
