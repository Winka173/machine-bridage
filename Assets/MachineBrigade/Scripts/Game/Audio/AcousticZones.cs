using System;
using MachineBrigade.Sim;
using UnityEngine;

namespace MachineBrigade.Game.Audio
{
    /// <summary>MVA W2-B (spec parts AY, BP): the broad acoustic environments a map is cut into (no micro reverb volumes).</summary>
    internal enum AcousticZone
    {
        Open,
        UrbanStreet,
        Fortress,
        Forest,
        Harbor,
        Snowfield,

        /// <summary>Tunnel / interior: no map has one yet (listed so the table is complete).</summary>
        Interior,
    }

    /// <summary>
    /// One zone's audio metadata (spec part BP fields): its reverb preset (the environment tail of the far reports: an echo
    /// delay, decay and wet share), the occlusion material class (how much a wall in the way takes off: low-pass cutoff and
    /// gain), the ambient profile (the wind bed's level and top end) and the far-report tail length.
    /// </summary>
    internal readonly struct AcousticProfile
    {
        public AcousticProfile(AcousticZone zone, string reverbPreset, string occlusionMaterial, float occlusionCutoff, float occlusionGain,
            string ambientProfile, float ambientGain, float ambientCutoff, float echoDelayMs, float echoDecay, float echoWet, float farReportTail)
        {
            Zone = zone;
            ReverbPreset = reverbPreset;
            OcclusionMaterial = occlusionMaterial;
            OcclusionCutoff = occlusionCutoff;
            OcclusionGain = occlusionGain;
            AmbientProfile = ambientProfile;
            AmbientGain = ambientGain;
            AmbientCutoff = ambientCutoff;
            EchoDelayMs = echoDelayMs;
            EchoDecay = echoDecay;
            EchoWet = echoWet;
            FarReportTail = farReportTail;
        }

        public AcousticZone Zone { get; }
        public string ReverbPreset { get; }
        public string OcclusionMaterial { get; }
        public float OcclusionCutoff { get; }
        public float OcclusionGain { get; }
        public string AmbientProfile { get; }
        public float AmbientGain { get; }
        public float AmbientCutoff { get; }
        public float EchoDelayMs { get; }
        public float EchoDecay { get; }
        public float EchoWet { get; }

        /// <summary>How much of the environment tail a far report keeps (0-1, against the zone's echo).</summary>
        public float FarReportTail { get; }
    }

    /// <summary>
    /// MVA W2-B (spec parts AX, AY, BP; DECISIONS "Map/visual/audio W2 (lane B)"): the map's acoustic zones, generated once per
    /// battle from the map's own semantics (no acoustic geometry): its theme, the tall cover the Sim already keeps
    /// (CoverGrid: buildings, rock, fortress walls), the terrain tags (forest, shallow water), the sea and the wall lines. A
    /// coarse grid (<see cref="Cell"/> m) holds one zone a cell; the audio reads the zone at the listener (the view's focus) in
    /// O(1). Static: a fallen building does not change its cell's zone (broad zones, spec part AY).
    /// </summary>
    internal sealed class AcousticZones
    {
        /// <summary>Grid cell (m).</summary>
        internal const float Cell = 16f;

        /// <summary>Half the window a cell's zone is measured over (m): a street is a street a little past its corners.</summary>
        internal const float Window = 14f;

        private static readonly AcousticProfile[] Profiles =
        {
            new(AcousticZone.Open, "open", "soft", 2600f, 0.75f, "amb_open_wind", 1f, 22000f, 260f, 0.18f, 0.16f, 0.8f),
            new(AcousticZone.UrbanStreet, "street_canyon", "masonry", 1400f, 0.55f, "amb_urban_hum", 0.75f, 12000f, 90f, 0.42f, 0.34f, 1f),
            new(AcousticZone.Fortress, "fortress_courtyard", "concrete", 1100f, 0.5f, "amb_fortress", 0.7f, 10000f, 70f, 0.5f, 0.4f, 1f),
            new(AcousticZone.Forest, "forest", "foliage", 3200f, 0.85f, "amb_forest", 0.85f, 9000f, 45f, 0.2f, 0.14f, 0.5f),
            new(AcousticZone.Harbor, "harbor", "steel", 1800f, 0.6f, "amb_harbor_water", 1f, 16000f, 180f, 0.3f, 0.24f, 0.9f),
            new(AcousticZone.Snowfield, "snowfield", "soft", 2400f, 0.75f, "amb_snow_wind", 0.9f, 7000f, 220f, 0.12f, 0.1f, 0.5f),
            new(AcousticZone.Interior, "interior", "concrete", 900f, 0.45f, "amb_interior", 0.5f, 6000f, 35f, 0.55f, 0.45f, 1f),
        };

        public static AcousticProfile Of(AcousticZone zone) => Profiles[(int)zone];

        private readonly AcousticZone[] _cells;
        private readonly int _width, _height;
        private readonly Vector2 _origin;

        private AcousticZones(Vector2 origin, int width, int height, AcousticZone[] cells)
        {
            _origin = origin;
            _width = width;
            _height = height;
            _cells = cells;
        }

        /// <summary>One zone everywhere (the menu battle, a test).</summary>
        public static AcousticZones Uniform(AcousticZone zone) => new(Vector2.zero, 1, 1, new[] { zone });

        /// <summary>The zone for a cell's measures (pure: the tests drive it).</summary>
        /// <param name="tallShare">Share of the window under tall cover (buildings, rock, walls).</param>
        /// <param name="forestShare">Share of the window tagged forest.</param>
        /// <param name="waterShare">Share of the window on water (the sea, shallow water).</param>
        /// <param name="nearWall">A fortress wall line passes within the window.</param>
        public static AcousticZone Classify(string theme, float tallShare, float forestShare, float waterShare, bool nearWall)
        {
            if (nearWall && tallShare > 0.06f) return AcousticZone.Fortress;
            if (waterShare > 0.15f) return AcousticZone.Harbor;
            if (tallShare > 0.14f) return AcousticZone.UrbanStreet;
            if (forestShare > 0.3f || theme == "jungle" && tallShare < 0.05f) return AcousticZone.Forest;
            if (theme == "snow") return AcousticZone.Snowfield;
            if (theme == "harbor" && waterShare > 0.02f) return AcousticZone.Harbor;
            return AcousticZone.Open;
        }

        /// <summary>The zones of a battle's map, measured on its Sim world (static data only; never steps it).</summary>
        public static AcousticZones Build(SimWorld world)
        {
            if (world == null) return Uniform(AcousticZone.Open);
            var map = world.Map;
            var grid = world.Grid;
            var min = new Vector2(map.Min.X, map.Min.Y);
            var max = new Vector2(map.Max.X, map.Max.Y);
            var width = Mathf.Max(1, Mathf.CeilToInt((max.x - min.x) / Cell));
            var height = Mathf.Max(1, Mathf.CeilToInt((max.y - min.y) / Cell));
            var cells = new AcousticZone[width * height];
            var theme = (map.Theme ?? "temperate").ToLowerInvariant();
            var walls = new System.Collections.Generic.List<Vector2>();
            foreach (var line in map.Walls)
                foreach (var segment in line.Segments)
                    walls.Add(new Vector2(segment.Center.X, segment.Center.Y));
            var sea = map.Sea;
            const float step = 2f;
            for (var cy = 0; cy < height; cy++)
                for (var cx = 0; cx < width; cx++)
                {
                    var centre = min + new Vector2((cx + 0.5f) * Cell, (cy + 0.5f) * Cell);
                    int samples = 0, tall = 0, forest = 0, water = 0;
                    for (var y = -Window; y <= Window; y += step)
                        for (var x = -Window; x <= Window; x += step)
                        {
                            var p = new System.Numerics.Vector2(centre.x + x, centre.y + y);
                            samples++;
                            if (world.Cover.IsBlocked(p)) tall++;
                            var tag = grid.TerrainAt(p);
                            if (tag == Sim.Navigation.TerrainTag.Forest) forest++;
                            else if (tag == Sim.Navigation.TerrainTag.ShallowWater || sea != null && sea.IsSea(p)) water++;
                        }
                    var nearWall = false;
                    foreach (var w in walls)
                        if ((w - centre).sqrMagnitude < (Window + 12f) * (Window + 12f))
                        {
                            nearWall = true;
                            break;
                        }
                    var n = Math.Max(1, samples);
                    cells[cy * width + cx] = Classify(theme, tall / (float)n, forest / (float)n, water / (float)n, nearWall);
                }
            return new AcousticZones(min, width, height, cells);
        }

        /// <summary>The zone at a world point (x east, z north); outside the map, the nearest cell's.</summary>
        public AcousticZone At(Vector3 world)
        {
            var x = Mathf.Clamp(Mathf.FloorToInt((world.x - _origin.x) / Cell), 0, _width - 1);
            var y = Mathf.Clamp(Mathf.FloorToInt((world.z - _origin.y) / Cell), 0, _height - 1);
            return _cells[y * _width + x];
        }

        /// <summary>How many cells of each zone (the docs and the telemetry).</summary>
        public int[] Census()
        {
            var counts = new int[Profiles.Length];
            foreach (var c in _cells) counts[(int)c]++;
            return counts;
        }
    }
}
