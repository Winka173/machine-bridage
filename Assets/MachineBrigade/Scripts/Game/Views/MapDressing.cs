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

    [Serializable]
    public sealed class MapDressingData
    {
        public int version;
        public DressingCamera camera;
        public DressingBiome[] biomes;
        public DressingMap[] maps;
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
                return _data ??= new MapDressingData { biomes = Array.Empty<DressingBiome>(), maps = Array.Empty<DressingMap>() };
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

        /// <summary>For tests: forget the loaded file.</summary>
        internal static void Reset() => _data = null;
    }
}
