#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using Tun = MachineBrigade.Sim.Content.SimTunables.Maps.Topology;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// Map / visual / audio master spec Parts C-P (lane W1-A): the battlefield's gameplay semantics, generated from the canonical
    /// map geometry and built on the AI MASTER <see cref="MapTopology"/> (its domain graphs, clearance and chokes: no second
    /// geometry inference). It adds the size-class route graphs (Light ... Boss), every named place resolved to its components,
    /// the tactical chokes (the one measure the traffic coordinator's passages use), the spawn clear zones, and on demand the
    /// tactical lanes, route audits, spawn fairness, shore fire regions, the naval route kinematics and turn-radius audit,
    /// breach metadata, tactical positions, staging areas, terrain semantics, the map warnings and the load gates.
    ///
    /// Read-only: building it never changes the battle, it never forces a lane-map or topology rebuild (it reads the lane map as
    /// it stands and the topology the world already has), and no combat value depends on it. The AI reads it through
    /// <see cref="SimWorld.GameplayTopology"/>; Tools/maps/topogen writes it to Docs/maps for the export pack.
    /// </summary>
    public sealed partial class GameplayTopology
    {
        private readonly SimWorld _world;
        private readonly List<TopologyAnchor> _anchors = new();
        private readonly List<TacticalChoke> _chokes = new();
        private readonly List<SpawnClearZone> _spawnZones = new();
        private readonly SizeClassInfo[] _classes = new SizeClassInfo[5];
        private readonly DomainGraph[] _classGraphs = new DomainGraph[5];

        private GameplayTopology(SimWorld world, MapTopology map, LaneMap lanes)
        {
            _world = world;
            Map = map;
            LanesBuild = lanes.Builds;
        }

        /// <summary>The AI MASTER topology it is built on (its domain graphs, clearance and chokes).</summary>
        public MapTopology Map { get; }

        /// <summary>The lane map's build this was made from.</summary>
        public int LanesBuild { get; }

        /// <summary>How many times the battle's gameplay topology has been built (1: the first).</summary>
        public int Generation { get; private set; }

        public DomainGraph Ground => Map.Ground;
        public DomainGraph Naval => Map.Naval;
        public DomainGraph Amphibious => Map.Amphibious;

        /// <summary>Spec D1: the five size classes' reference hulls.</summary>
        public IReadOnlyList<SizeClassInfo> Classes => _classes;

        /// <summary>Spec D: places resolved to components (spawns, objectives, bases, fortress, batteries, lanes, boss routes...).</summary>
        public IReadOnlyList<TopologyAnchor> Anchors => _anchors;

        /// <summary>Spec E: the tactical chokes, doorways first then the topology's ground chokes (the traffic passages' order).</summary>
        public IReadOnlyList<TacticalChoke> Chokes => _chokes;

        /// <summary>Spec G: each side's spawn clear zone.</summary>
        public IReadOnlyList<SpawnClearZone> SpawnClearZones => _spawnZones;

        /// <summary>The ground graph of a size class (cells with the class's clearance, split into components).</summary>
        public DomainGraph ClassGraph(VehicleSizeClass cls) => _classGraphs[(int)cls];

        public SizeClassInfo Class(VehicleSizeClass cls) => _classes[(int)cls];

        // ================================================================================================ build

        /// <summary>Builds the gameplay topology on <paramref name="map"/> (the world's current topology) and the lane map as it stands.</summary>
        internal static GameplayTopology Build(SimWorld world, MapTopology map, LaneMap lanes, int generation)
        {
            var g = new GameplayTopology(world, map, lanes) { Generation = generation };
            g.MeasureClasses();
            g.BuildClassGraphs();
            g.BuildSpawnZones();
            g.ResolveAnchors();
            g.MeasurePassages(lanes);
            g.TypeChokes(lanes);
            return g;
        }

        // ------------------------------------------------------------------------------------------------ size classes

        /// <summary>Whether a vehicle drives the ground grid (not aircraft, fixed defences, ships, trains or spacecraft).</summary>
        public static bool DrivesGround(VehicleDef d) =>
            !d.Flying && !d.Static && d.Speed > 0f && d.Naval == null && d.RouteName != "rail" && d.FrameId != "spacecraft" &&
            d.Craft == null && d.Width > 0f;

        /// <summary>Spec D1: a hull's size class (bosses are Boss; the rest by hull width, maps.topology.sizeBands).</summary>
        public static VehicleSizeClass ClassOf(VehicleDef def)
        {
            if (def.Boss) return VehicleSizeClass.Boss;
            var bands = Tun.SizeBands;
            float Band(int i, float fallback) => i < bands.Length ? bands[i] : fallback;
            var w = def.Width;
            if (w < Band(0, 2.9f)) return VehicleSizeClass.Light;
            if (w < Band(1, 3.4f)) return VehicleSizeClass.Medium;
            if (w < Band(2, 4.5f)) return VehicleSizeClass.Heavy;
            return VehicleSizeClass.SuperHeavy;
        }

        /// <summary>
        /// The least clearance (cells to the nearest closed cell) a route cell needs for a hull <paramref name="width"/> wide: its
        /// width plus the side clearance on both sides, less the obstacles' grown margin on both sides, as open cells across.
        /// </summary>
        public static int ClearanceFor(float width, float cell)
        {
            var open = width + 2f * Tun.SideClearance - 2f * SimWorld.ObstacleClearance;
            return Math.Max(1, (int)MathF.Ceiling((open / cell + 1f) * 0.5f));
        }

        /// <summary>Physical clear width (m) of a corridor whose centre cell has <paramref name="clearance"/>.</summary>
        public float WidthOfClearance(int clearance) =>
            clearance <= 0 ? 0f : (clearance * 2f - 1f) * Map.Cell + 2f * SimWorld.ObstacleClearance;

        private void MeasureClasses()
        {
            var widths = new List<float>[5];
            var all = new List<float>[5];
            var lengths = new float[5];
            var speeds = new List<float>[5];
            for (var i = 0; i < 5; i++)
            {
                widths[i] = new List<float>();
                all[i] = new List<float>();
                speeds[i] = new List<float>();
            }
            var ids = new List<string>(_world.Catalog.Vehicles.Keys);
            ids.Sort(StringComparer.Ordinal);
            foreach (var id in ids)
            {
                var d = _world.Catalog.Vehicles[id];
                if (!DrivesGround(d)) continue;
                var c = (int)ClassOf(d);
                all[c].Add(d.Width);
                if (d.StoryOnly) continue;
                widths[c].Add(d.Width);
                lengths[c] = MathF.Max(lengths[c], d.Length);
                speeds[c].Add(d.Speed);
            }
            // Fallbacks keep a class usable on a catalog without members of it (tests' small catalogs).
            float[] defaultWidth = { 2.6f, 3.2f, 3.9f, 5.3f, 11f };
            for (var i = 0; i < 5; i++)
            {
                var list = widths[i].Count > 0 ? widths[i] : all[i];
                // The widest hull of a class must fit its routes; the Boss class is the boss chassis typical of it (the median:
                // boss hulls range from 6 to 16 m, and each giant drives its own scripted route or arena).
                var reference = list.Count == 0 ? defaultWidth[i] : i == (int)VehicleSizeClass.Boss ? Median(list) : Max(list);
                var median = list.Count > 0 ? Median(list) : defaultWidth[i];
                var length = lengths[i] > 0f ? lengths[i] : reference * 2.2f;
                var speed = speeds[i].Count > 0 ? Median(speeds[i]) : 5f;
                _classes[i] = new SizeClassInfo((VehicleSizeClass)i, all[i].Count, reference, median, length, speed, ClearanceFor(reference, Map.Cell));
            }
        }

        private static float Max(List<float> list)
        {
            var m = float.MinValue;
            foreach (var v in list) m = MathF.Max(m, v);
            return m;
        }

        private static float Median(List<float> list)
        {
            var copy = new List<float>(list);
            copy.Sort();
            var n = copy.Count;
            return n % 2 == 1 ? copy[n / 2] : (copy[n / 2 - 1] + copy[n / 2]) * 0.5f;
        }

        private void BuildClassGraphs()
        {
            var ground = Map.Ground.Passable;
            for (var i = 0; i < 5; i++)
            {
                var need = _classes[i].ClearanceCells;
                // A class that needs no more than one open cell drives the ground graph as it is (no second flood fill).
                if (need <= 1)
                {
                    _classGraphs[i] = Map.Ground;
                    continue;
                }
                // Same need as the class before: share its graph.
                if (i > 0 && _classes[i - 1].ClearanceCells == need)
                {
                    _classGraphs[i] = _classGraphs[i - 1];
                    continue;
                }
                var passable = new bool[ground.Length];
                for (var c = 0; c < ground.Length; c++) passable[c] = ground[c] && Map.Clearance[c] >= need;
                _classGraphs[i] = new DomainGraph(Map, MobilityDomain.Ground, passable);
            }
        }

        // ------------------------------------------------------------------------------------------------ spawn zones

        private void BuildSpawnZones()
        {
            var t = SimTunables.Ai.Traffic.SpawnExitRadius;
            for (var team = 0; team <= 1; team++)
                if (_world.TryGetRally(team, out var rally))
                    _spawnZones.Add(new SpawnClearZone(team, rally, t, SimTunables.Ai.Traffic.SpawnClearRadius, SimTunables.Ai.Traffic.SpawnRallyRadius));
        }

        /// <summary>Whether a point lies in any side's spawn clear zone.</summary>
        public bool InSpawnClearZone(Vector2 p)
        {
            foreach (var z in _spawnZones)
                if (z.Contains(p)) return true;
            return false;
        }

        // ------------------------------------------------------------------------------------------------ anchors

        private void ResolveAnchors()
        {
            var map = _world.Map;
            foreach (var t in map.Teams)
                Anchor("rally_" + t.Team, AnchorKind.Spawn, t.Rally, t.Team, Map.IsSea(t.Rally) ? MobilityDomain.Naval : MobilityDomain.Ground, 6f);
            for (var i = 0; i < map.Spawns.Count; i++)
            {
                var s = map.Spawns[i];
                var domain = s.Kind switch
                {
                    SpawnKind.Sea => MobilityDomain.Naval,
                    SpawnKind.Air => MobilityDomain.Air,
                    SpawnKind.Landing => MobilityDomain.Amphibious,
                    SpawnKind.Rail => MobilityDomain.Static,
                    _ => MobilityDomain.Ground,
                };
                Anchor($"spawn_{i}_{s.Kind.ToString().ToLowerInvariant()}", AnchorKind.MissionSpawn, s.Position, s.Side, domain, 6f);
            }
            foreach (var gate in map.EntryGates)
            {
                var domain = gate.Kind switch
                {
                    EntryGateKind.Air => MobilityDomain.Air,
                    // A sea gate is a landing ingress: its gameplay entry position is on the beach (ships keep their own routes).
                    EntryGateKind.Sea => MobilityDomain.Amphibious,
                    EntryGateKind.Rail => MobilityDomain.Static,
                    _ => MobilityDomain.Ground,
                };
                Anchor("gate_" + gate.Id, AnchorKind.EntryGate, gate.Position, -1, domain, 6f);
            }
            foreach (var p in map.Points) Anchor("point_" + p.Id, AnchorKind.Objective, p.Position, -1, MobilityDomain.Ground, MathF.Max(2f, p.Radius));
            foreach (var b in map.Bases) Anchor("hq_" + b.Team, AnchorKind.Base, b.Hq, b.Team, MobilityDomain.Ground, 8f);
            if (map.Fortress is { } fort)
            {
                Anchor("fortress_hq", AnchorKind.Fortress, fort.Hq, -1, MobilityDomain.Ground, 10f);
                for (var i = 0; i < fort.ForwardDrops.Count; i++)
                    Anchor("fortress_drop_" + i, AnchorKind.Fortress, fort.ForwardDrops[i], -1, MobilityDomain.Ground, 6f);
            }
            for (var i = 0; i < map.Neutrals.Count; i++)
                Anchor($"neutral_{i}_{map.Neutrals[i].Kind}", AnchorKind.Neutral, map.Neutrals[i].At, -1, MobilityDomain.Ground, 6f);
            foreach (var (name, line) in SortedRoutes(map))
            {
                if (line.Count == 0) continue;
                var domain = name == "rail" ? MobilityDomain.Static : MobilityDomain.Ground;
                Anchor($"route_{name}_start", AnchorKind.BossRoute, line[0], -1, domain, 6f);
                if (line.Count > 2) Anchor($"route_{name}_mid", AnchorKind.BossRoute, line[line.Count / 2], -1, domain, 6f);
                Anchor($"route_{name}_end", AnchorKind.BossRoute, line[line.Count - 1], -1, domain, 6f);
            }
            if (map.Sea is not { } sea) return;
            foreach (var b in sea.Batteries) Anchor("battery_" + b.Id, AnchorKind.Battery, b.At, -1, MobilityDomain.Ground, 8f);
            for (var i = 0; i < sea.Landings.Count; i++)
                Anchor("landing_" + i, AnchorKind.Landing, sea.Landings[i].At, -1, MobilityDomain.Amphibious, 6f);
            for (var i = 0; i < sea.Piers.Count; i++) Anchor("pier_" + i, AnchorKind.Pier, sea.Piers[i], -1, MobilityDomain.Ground, 6f);
            foreach (var lane in sea.Lanes) Anchor("lane_" + lane.Id, AnchorKind.NavalLane, sea.At(0f, lane.W), -1, MobilityDomain.Naval, 6f);
            if (RouteGraph() is { } graph)
                foreach (var n in graph.Nodes)
                    if (n.Kind != SeaNodeKind.Exit) Anchor("seanode_" + n.Id, AnchorKind.NavalNode, n.Position, -1, MobilityDomain.Naval, 6f);
        }

        private static List<(string, IReadOnlyList<Vector2>)> SortedRoutes(MapDefinition map)
        {
            var list = new List<(string, IReadOnlyList<Vector2>)>();
            foreach (var pair in map.Routes) list.Add((pair.Key, pair.Value));
            list.Sort((a, b) => string.CompareOrdinal(a.Item1, b.Item1));
            return list;
        }

        private void Anchor(string id, AnchorKind kind, Vector2 at, int team, MobilityDomain domain, float radius)
        {
            var rings = Math.Max(SimTunables.Ai.Topology.NearestRings, (int)MathF.Ceiling(radius / Map.Cell));
            var a = new TopologyAnchor
            {
                Id = id,
                Kind = kind,
                Position = at,
                Team = team,
                Domain = domain,
                GroundComponent = Map.Ground.ComponentOfCell(Map.Ground.NearestPassableCell(at, rings)),
                NavalComponent = Map.Naval.ComponentOfCell(Map.Naval.NearestPassableCell(at, rings)),
                AmphibiousComponent = Map.Amphibious.ComponentOfCell(Map.Amphibious.NearestPassableCell(at, rings)),
            };
            for (var i = 0; i < 5; i++)
            {
                var graph = _classGraphs[i];
                a.ClassComponent[i] = graph.ComponentOfCell(graph.NearestPassableCell(at, rings + _classes[i].ClearanceCells));
            }
            a.Resolved = domain switch
            {
                MobilityDomain.Ground => a.GroundComponent > 0 || a.AmphibiousComponent > 0,
                MobilityDomain.Naval => a.NavalComponent > 0,
                MobilityDomain.Amphibious => a.AmphibiousComponent > 0,
                _ => true,
            };
            _anchors.Add(a);
        }

        /// <summary>The anchor of an id, or null.</summary>
        public TopologyAnchor? AnchorOf(string id)
        {
            foreach (var a in _anchors)
                if (a.Id == id) return a;
            return null;
        }

        /// <summary>The sea route graph the naval system sails (the map's, else the one built from its lanes), bound to the coast; null without a sea.</summary>
        internal SeaRouteGraph? RouteGraph()
        {
            if (_routeGraph != null || _world.Map.Sea is not { } sea) return _routeGraph;
            _routeGraph = _world.Map.SeaRoutes ?? SeaRouteGraph.FromSea(sea, _world.Map.HalfSize);
            _routeGraph.Bind(sea);
            return _routeGraph;
        }

        private SeaRouteGraph? _routeGraph;

        // ------------------------------------------------------------------------------------------------ chokes

        /// <summary>
        /// The passages of AI MASTER spec 30, measured here once for the traffic coordinator and the map layer (moved from
        /// TrafficCoordinator.BuildDoorways / BuildChokes unchanged): the lane map's doorways (gates, gaps, narrow roads), then
        /// the topology's ground chokes no doorway covers (a choke over water or beside it is a bridge).
        /// </summary>
        private void MeasurePassages(LaneMap lanes)
        {
            var grid = _world.Grid;
            var count = lanes.DoorwayCount;
            if (count > 0)
            {
                var sum = new Vector2[count + 1];
                var cells = new int[count + 1];
                var road = new int[count + 1];
                for (var y = 0; y < grid.Height; y++)
                for (var x = 0; x < grid.Width; x++)
                {
                    var f = lanes.FlagsOf(x, y);
                    if ((f & LaneFlags.Narrow) == 0) continue;
                    var c = grid.CellCenter(x, y);
                    var id = lanes.DoorwayAt(c);
                    if (id <= 0 || id > count) continue;
                    sum[id] += c;
                    cells[id]++;
                    if ((f & LaneFlags.Road) != 0) road[id]++;
                }
                var lo = new float[count + 1];
                var hi = new float[count + 1];
                var wlo = new float[count + 1];
                var whi = new float[count + 1];
                for (var id = 1; id <= count; id++)
                {
                    lo[id] = wlo[id] = float.MaxValue;
                    hi[id] = whi[id] = float.MinValue;
                }
                for (var y = 0; y < grid.Height; y++)
                for (var x = 0; x < grid.Width; x++)
                {
                    if ((lanes.FlagsOf(x, y) & LaneFlags.Narrow) == 0) continue;
                    var c = grid.CellCenter(x, y);
                    var id = lanes.DoorwayAt(c);
                    if (id <= 0 || id > count || cells[id] == 0) continue;
                    var through = lanes.DoorwayThrough(id);
                    var across = new Vector2(through.Y, -through.X);
                    var d = c - sum[id] / cells[id];
                    var a = Vector2.Dot(d, through);
                    var w = Vector2.Dot(d, across);
                    lo[id] = MathF.Min(lo[id], a);
                    hi[id] = MathF.Max(hi[id], a);
                    wlo[id] = MathF.Min(wlo[id], w);
                    whi[id] = MathF.Max(whi[id], w);
                }
                for (var id = 1; id <= count; id++)
                {
                    if (cells[id] == 0) continue;
                    var length = hi[id] - lo[id] + grid.CellSize;
                    var width = whi[id] - wlo[id] + grid.CellSize;
                    _chokes.Add(new TacticalChoke
                    {
                        FromDoorway = true,
                        Shape = length > width * 3f && road[id] * 2 >= cells[id] ? PassageShape.NarrowRoad : PassageShape.Gate,
                        Centre = sum[id] / cells[id],
                        Through = lanes.DoorwayThrough(id),
                        OpenWidth = width,
                        Length = length,
                    });
                }
            }
            // Lane W2-A: while the AI MASTER topology waits for its rebuild (maps: ai.topology.rebuildSeconds) after a wall fell,
            // its chokes are the ones before the fall. One the rubble opened (rubble within its reach and its narrowest width now
            // well over the choke's) is dropped here at once, not one topology rebuild late; a static map is never stale.
            var stale = Tun.RemeasureStaleChokes && Map.GridVersion != grid.Version && _world.HasWalls && _world.Walls.HasRubble;
            foreach (var choke in Map.Chokes)
            {
                var covered = false;
                foreach (var p in _chokes)
                    if (Vector2.Distance(p.Centre, choke.Centre) < p.Reach + 4f)
                    {
                        covered = true;
                        break;
                    }
                if (covered) continue;
                // The narrowest of 8 bearings across it is "across"; the way through is square to it.
                var bestWidth = float.MaxValue;
                var across = Vector2.UnitX;
                for (var k = 0; k < 8; k++)
                {
                    var dir = SimMath.Forward(k * MathF.PI / 8f);
                    var width = Ray(grid, choke.Centre, dir, 30f) + Ray(grid, choke.Centre, -dir, 30f);
                    if (width >= bestWidth) continue;
                    bestWidth = width;
                    across = dir;
                }
                if (stale && bestWidth > choke.Width + 2f * grid.CellSize + 2f && RubbleNear(choke.Centre, MathF.Max(choke.Width, 8f) * 0.5f + 6f))
                {
                    StaleChokesDropped++;
                    continue;
                }
                var through = new Vector2(-across.Y, across.X);
                var half = MathF.Max(choke.Width, bestWidth) * 0.5f + 3f;
                var water = Map.IsSea(choke.Centre + across * half) || Map.IsSea(choke.Centre - across * half) ||
                            grid.TerrainAt(choke.Centre + across * half) == TerrainTag.ShallowWater ||
                            grid.TerrainAt(choke.Centre - across * half) == TerrainTag.ShallowWater;
                var length = MathF.Max(6f, choke.Cells * Map.Cell * Map.Cell / MathF.Max(2f, choke.Width));
                _chokes.Add(new TacticalChoke
                {
                    Shape = water ? PassageShape.Bridge : PassageShape.Choke,
                    Centre = choke.Centre,
                    Through = through,
                    OpenWidth = MathF.Max(2f, MathF.Min(choke.Width, bestWidth)),
                    Length = MathF.Min(length, 40f),
                });
            }
            for (var i = 0; i < _chokes.Count; i++) _chokes[i].Id = i + 1;
        }

        /// <summary>Topology chokes left out because the rubble of a fallen wall opened them before the topology's rebuild (lane W2-A).</summary>
        public int StaleChokesDropped { get; private set; }

        /// <summary>Wall rubble within <paramref name="reach"/> m of <paramref name="p"/> (its box grown by the reach).</summary>
        private bool RubbleNear(Vector2 p, float reach)
        {
            foreach (var (min, max) in _world.Walls.RubbleAreas)
                if (p.X >= min.X - reach && p.X <= max.X + reach && p.Y >= min.Y - reach && p.Y <= max.Y + reach) return true;
            return false;
        }

        private static float Ray(NavGrid grid, Vector2 from, Vector2 dir, float max)
        {
            for (var d = 1f; d <= max; d += 1f)
                if (!grid.IsWalkable(from + dir * d)) return d;
            return max;
        }

        /// <summary>Spec E / E1 / E2: each choke's type, physical width, capacity, throughput, queue areas and largest class.</summary>
        private void TypeChokes(LaneMap lanes)
        {
            var map = _world.Map;
            var grid = _world.Grid;
            var growth = SimWorld.ObstacleClearance;
            var margin = Tun.SeparationMargin;
            var light = Class(VehicleSizeClass.Light);
            var medium = Class(VehicleSizeClass.Medium);
            var heavy = Class(VehicleSizeClass.Heavy);
            foreach (var c in _chokes)
            {
                c.Type = TypeOf(c, map, grid);
                c.UsableWidthM = c.OpenWidth + 2f * growth;
                c.MaxLightSideBySide = (int)MathF.Floor(c.UsableWidthM / (light.MedianWidth + margin));
                c.MaxMediumSideBySide = (int)MathF.Floor(c.UsableWidthM / (medium.MedianWidth + margin));
                c.MaxHeavySideBySide = (int)MathF.Floor(c.UsableWidthM / (heavy.MedianWidth + margin));
                // AI MASTER spec 189's rule (the traffic coordinator's lanes from the open width), for a medium hull.
                var lanesThrough = Math.Max(1, (int)MathF.Floor(c.OpenWidth / MathF.Max(1f, medium.MedianWidth + 1f)));
                c.EstimatedThroughput = lanesThrough * MathF.Max(0.5f, medium.MedianSpeed) / MathF.Max(2f, medium.ReferenceLength + 4f);
                c.OppositeTrafficAllowed = c.MaxMediumSideBySide >= 2;
                c.QueueAreaA = Queue(c, -1);
                c.QueueAreaB = Queue(c, 1);
                var cell = Map.CellIndex(c.Centre);
                var clearance = cell >= 0 ? Map.Clearance[cell] : 0;
                var largest = VehicleSizeClass.Light;
                for (var i = 0; i < 5; i++)
                    if (_classes[i].ClearanceCells <= Math.Max(1, clearance) && c.UsableWidthM >= _classes[i].ReferenceWidth + 2f * Tun.SideClearance)
                        largest = (VehicleSizeClass)i;
                c.LargestClass = largest;
                c.Critical = (lanes.At(c.Centre) & LaneFlags.Route) != 0;
                c.Component = Map.Ground.ComponentOfCell(Map.Ground.NearestPassableCell(c.Centre, 2));
            }
        }

        private ChokeType TypeOf(TacticalChoke c, MapDefinition map, NavGrid grid)
        {
            foreach (var line in map.Walls)
            {
                if (Vector2.Distance(line.Gate, c.Centre) <= line.GateWidth * 0.5f + 4f) return ChokeType.Gate;
                foreach (var s in line.Segments)
                    if (Vector2.Distance(s.Center, c.Centre) <= s.Length * 0.5f + 2f) return ChokeType.WallBreach;
            }
            foreach (var rail in map.Rails)
                foreach (var x in rail.Crossings)
                    if (Vector2.Distance(x.Position, c.Centre) <= x.Half + 4f) return ChokeType.RailCrossing;
            if (grid.TerrainAt(c.Centre) == TerrainTag.ShallowWater) return ChokeType.RiverCrossing;
            if (c.Shape == PassageShape.Bridge) return ChokeType.Bridge;
            if (map.Sea is { } sea)
            {
                var f = sea.Frame(c.Centre);
                if (f.Y > sea.ShoreAt(f.X) - 25f) return ChokeType.HarborThroat;
                foreach (var pier in sea.Piers)
                    if (Vector2.Distance(pier, c.Centre) < 20f) return ChokeType.HarborThroat;
            }
            if (c.Shape == PassageShape.NarrowRoad || (c.FromDoorway && c.Length >= c.OpenWidth * 1.5f)) return ChokeType.StreetCanyon;
            return ChokeType.NaturalTerrainGap;
        }

        /// <summary>Spec E2: the queue box before a choke on side <paramref name="side"/> (-1: A, +1: B), and whether it is safe.</summary>
        private QueueArea Queue(TacticalChoke c, int side)
        {
            var spacing = SimTunables.Ai.Traffic.QueueSpacing;
            var back = c.Through * side;
            var halfAlong = spacing * 1.5f;
            var halfAcross = c.OpenWidth * 0.5f + 4f;
            var centre = c.Centre + back * (c.Length * 0.5f + SimTunables.Ai.Traffic.QueueStart + halfAlong);
            var issue = "";
            if (!_world.Grid.IsWalkable(centre)) issue = "not-open-ground";
            else
            {
                foreach (var z in _spawnZones)
                    if (Vector2.Distance(z.Centre, centre) < z.ClearRadius + halfAlong) issue = "spawn-clear-zone";
                if (issue.Length == 0)
                    foreach (var p in _world.Map.Points)
                        if (Vector2.Distance(p.Position, centre) < p.Radius + halfAlong) issue = "capture-circle";
                if (issue.Length == 0)
                    foreach (var o in _chokes)
                        if (o != c && o.Contains(centre)) issue = "inside-choke";
            }
            return new QueueArea(centre, back, halfAlong, halfAcross, issue.Length == 0, issue);
        }

        // ================================================================================================ AI queries

        /// <summary>
        /// Spec F: whether a vehicle may stop at <paramref name="p"/> (open ground, not a doorway or its mouths). The fire-support
        /// anchor's validity test reads it (same rule as before: the grid's walkability and the lane map's no-parking cells).
        /// </summary>
        public bool ParkingAllowed(Vector2 p) => _world.Grid.IsWalkable(p) && !_world.Lanes.NoParkAt(p);

        /// <summary>
        /// Spec F: how much standing at <paramref name="p"/> gets in the traffic's way: 1 on a main transit route, 0.5 on a road,
        /// 0 off them (the fire-support anchor's traffic term, as before).
        /// </summary>
        public float TransitConflict(Vector2 p)
        {
            var flags = _world.Lanes.At(p);
            return (flags & LaneFlags.Route) != 0 ? 1f : (flags & LaneFlags.Road) != 0 ? 0.5f : 0f;
        }

        /// <summary>Spec J: escape routes from <paramref name="p"/>: of 8 bearings, how many have open ground <paramref name="reach"/> m out.</summary>
        public int EscapeRoutes(Vector2 p, float reach)
        {
            var n = 0;
            for (var k = 0; k < 8; k++)
                if (_world.Grid.IsWalkable(p + SimMath.Forward(k * MathF.PI / 4f) * reach)) n++;
            return n;
        }

        /// <summary>
        /// Spec K / L: the stretch of the sea lane nearest <paramref name="centre"/> a ship seen there patrols, as
        /// <paramref name="samples"/> points (plus the centre itself last), or null when no lane is within the ship's radius +
        /// 12 m or the lane has no patrol. The engagement-feasibility check reads ships' lanes through it (moved from
        /// EngagementFeasibility.Observed unchanged).
        /// </summary>
        public static Vector2[]? LaneStretch(SeaDef sea, Vector2 centre, float radius, int samples)
        {
            if (sea.Lanes.Count == 0) return null;
            var f = sea.Frame(centre);
            SeaLaneDef? nearest = null;
            foreach (var l in sea.Lanes)
                if (nearest == null || MathF.Abs(l.W - f.Y) < MathF.Abs(nearest.W - f.Y)) nearest = l;
            if (nearest == null || MathF.Abs(nearest.W - f.Y) > radius + 12f || nearest.Patrol <= 0f) return null;
            var points = new Vector2[samples + 1];
            for (var k = 0; k < samples; k++)
            {
                var u = samples == 1 ? f.X : -nearest.Patrol + 2f * nearest.Patrol * k / (samples - 1);
                points[k] = sea.At(u, nearest.W);
            }
            points[samples] = centre;
            return points;
        }

        /// <summary>
        /// Spec D1: whether a hull of <paramref name="def"/>'s size class can drive from <paramref name="from"/> to within
        /// <paramref name="radius"/> of <paramref name="to"/> (true for anything that does not drive the ground grid).
        /// </summary>
        public bool SizeClassReaches(VehicleDef def, Vector2 from, Vector2 to, float radius)
        {
            if (!DrivesGround(def) || MapTopology.DomainOf(def) != MobilityDomain.Ground) return true;
            var graph = ClassGraph(ClassOf(def));
            var need = Class(ClassOf(def)).ClearanceCells;
            var source = graph.NearestPassableCell(from, SimTunables.Ai.Topology.NearestRings + need);
            var target = graph.NearestPassableCell(to, Math.Max(SimTunables.Ai.Topology.NearestRings, (int)MathF.Ceiling(radius / Map.Cell)) + need);
            return source >= 0 && target >= 0 && graph.ComponentOfCell(source) == graph.ComponentOfCell(target);
        }
    }
}
