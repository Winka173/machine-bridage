#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>Prompt 33 L3: the terrain tag of a navigation cell (static: built once with the grid, never changed by a tick).</summary>
    public enum TerrainTag : byte
    {
        Normal,
        Road,
        Rough,
        Forest,
        ShallowWater,
    }

    /// <summary>One rectangle of a tag (map data "terrain"."zones"): the cells whose centres lie inside it.</summary>
    public readonly struct TerrainZoneDef
    {
        public TerrainZoneDef(TerrainTag tag, Vector2 min, Vector2 max)
        {
            Tag = tag;
            Min = min;
            Max = max;
        }

        public TerrainTag Tag { get; }
        public Vector2 Min { get; }
        public Vector2 Max { get; }

        /// <summary>Map data "terrain": {"cell", "zones": [{"tag", "rects": [x0, z0, x1, z1, ...]}]} (Tools/maps/terrain.py).</summary>
        internal static IReadOnlyList<TerrainZoneDef> ParseAll(JsonObject root)
        {
            if (!root.Has("terrain")) return Array.Empty<TerrainZoneDef>();
            var t = root.Object("terrain");
            var list = new List<TerrainZoneDef>();
            if (!t.Has("zones")) return list;
            foreach (var z in t.Array("zones"))
            {
                var tag = TerrainRules.Parse(z.String("tag"));
                var r = z.FloatArray("rects");
                if (r.Count % 4 != 0) throw new FormatException($"{z.Path}.rects: needs x0, z0, x1, z1 quadruples.");
                for (var i = 0; i < r.Count; i += 4)
                {
                    if (!(r[i + 2] > r[i]) || !(r[i + 3] > r[i + 1])) throw new FormatException($"{z.Path}.rects[{i / 4}]: an empty rectangle.");
                    list.Add(new TerrainZoneDef(tag, new Vector2(r[i], r[i + 1]), new Vector2(r[i + 2], r[i + 3])));
                }
            }
            return list;
        }
    }

    /// <summary>
    /// Prompt 33 L3: what the terrain tags do (DECISIONS "Prompt 33 L2 / L3"). Speed: ROAD +20 %, ROUGH -15 %, FOREST -25 %,
    /// SHALLOW_WATER -50 % but for the amphibious and air-cushion vehicles (no change there). A ground vehicle in FOREST is
    /// harder to see: the enemy's sight on it x 0.7 (the visibility's own per-target factor, as camouflage). Path costs are
    /// static, by tag, the same for every vehicle (the path finder has no per-type costs: the precheck's item 3): the time to
    /// cross a cell at an ordinary vehicle's speed there, so routes never swing from tick to tick. Nothing else: no height,
    /// armour, deformation or cover percentage by terrain (the prompt's list of what not to add).
    /// </summary>
    public static class TerrainRules
    {
        public static float RoadSpeed => global::MachineBrigade.Sim.Content.SimTunables.Maps.TerrainRules.RoadSpeed;
        public static float RoughSpeed => global::MachineBrigade.Sim.Content.SimTunables.Maps.TerrainRules.RoughSpeed;
        public static float ForestSpeed => global::MachineBrigade.Sim.Content.SimTunables.Maps.TerrainRules.ForestSpeed;
        public static float WaterSpeed => global::MachineBrigade.Sim.Content.SimTunables.Maps.TerrainRules.WaterSpeed;

        /// <summary>The enemy's sight on a ground vehicle in a forest.</summary>
        public static float ForestSight => global::MachineBrigade.Sim.Content.SimTunables.Maps.TerrainRules.ForestSight;

        /// <summary>The cheapest cell's path cost (a road's): the A* heuristic is scaled by it to stay admissible.</summary>
        public static float MinPathCost => 1f / RoadSpeed;

        /// <summary>The amphibious and air-cushion vehicles, by id (the light tank is the amphibious light tank in the game's names).</summary>
        private static readonly HashSet<string> Waders = new() { "light_tank", "hover_gunboat", "landing_hovercraft" };

        /// <summary>Whether shallow water does not slow it: an amphibious vehicle, an air-cushion one (the hovercraft frame).</summary>
        public static bool Wades(VehicleDef def) => Waders.Contains(def.Id) || def.FrameId == "hovercraft";

        /// <summary>The drive speed multiplier on a tag for a vehicle.</summary>
        public static float SpeedOf(TerrainTag tag, VehicleDef def) => tag switch
        {
            TerrainTag.Road => RoadSpeed,
            TerrainTag.Rough => RoughSpeed,
            TerrainTag.Forest => ForestSpeed,
            TerrainTag.ShallowWater => Wades(def) ? 1f : WaterSpeed,
            _ => 1f,
        };

        /// <summary>The static path cost of a cell of the tag (1 / an ordinary vehicle's speed there).</summary>
        public static float PathCost(TerrainTag tag) => tag switch
        {
            TerrainTag.Road => 1f / RoadSpeed,
            TerrainTag.Rough => 1f / RoughSpeed,
            TerrainTag.Forest => 1f / ForestSpeed,
            TerrainTag.ShallowWater => 1f / WaterSpeed,
            _ => 1f,
        };

        public static TerrainTag Parse(string tag) => tag switch
        {
            "ROAD" => TerrainTag.Road,
            "ROUGH" => TerrainTag.Rough,
            "FOREST" => TerrainTag.Forest,
            "SHALLOW_WATER" => TerrainTag.ShallowWater,
            "NORMAL" => TerrainTag.Normal,
            _ => throw new FormatException($"map.terrain: unknown tag '{tag}' (NORMAL, ROAD, ROUGH, FOREST, SHALLOW_WATER)."),
        };
    }
}
