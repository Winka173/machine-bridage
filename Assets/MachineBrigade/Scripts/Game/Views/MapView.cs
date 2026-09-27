using System;
using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using UnityEngine.Rendering;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Object = UnityEngine.Object;
using Random = System.Random;
using Vector2 = System.Numerics.Vector2;
using Vector3 = UnityEngine.Vector3;

namespace MachineBrigade.Game.Views
{
    public sealed class PropView
    {
        public PropView(Prop prop, GameObject gameObject, string model, string rubbleModel, IReadOnlyList<string> debris)
        {
            Prop = prop;
            GameObject = gameObject;
            Model = model;
            RubbleModel = rubbleModel;
            Debris = debris;
        }

        public Prop Prop { get; }
        public GameObject GameObject { get; set; }
        public Transform Transform => GameObject.transform;

        /// <summary>The model it is drawn with.</summary>
        public string Model { get; }

        /// <summary>Model left behind when destroyed, or null when the prop vanishes into its blast.</summary>
        public string RubbleModel { get; }

        /// <summary>Debris chunk models thrown when destroyed.</summary>
        public IReadOnlyList<string> Debris { get; }

        public bool IsBuilding => RubbleModel != null;
    }

    /// <summary>
    /// Ground, props and decoration. Destroyed buildings collapse into rubble; small props vanish
    /// into their blast. Decorative bushes are purely visual and never block movement. Surface
    /// tiles (lava pools, river water, fords) have no model: they are merged into smooth-edged
    /// meshes, lava glowing and slowly pulsing, water shading from shallow banks to deep water.
    /// </summary>
    public sealed class MapView : IDisposable
    {
        /// <summary>Props drawn with random yaw and size, like trees.</summary>
        private static readonly HashSet<string> Vegetation = new()
        {
            "tree", "palm", "cactus", "charred_tree", "jungle_tree_a", "jungle_tree_b", "jungle_tree_c", "bamboo_clump", "fern_bush",
            "dead_tree",
        };

        /// <summary>Surface tiles merged into meshes instead of spawned as models.</summary>
        private static readonly HashSet<string> Surfaces = new() { "lava_pool", "river_water", "river_ford" };

        private static readonly string[] LeafDebris = { "debris_leaves", "debris_leaves", "debris_leaves", "debris_wood" };
        private static readonly string[] SteelDebris = { "debris_metal", "debris_metal", "debris_metal", "debris_metal" };

        private static readonly string[] BuildingDebris =
            { "debris_concrete", "debris_plaster", "debris_roof", "debris_concrete", "debris_plaster", "debris_roof", "debris_wood", "debris_concrete" };

        private static readonly string[] BarnDebris =
            { "debris_wood", "debris_wood", "debris_roof", "debris_wood", "debris_plaster", "debris_wood", "debris_roof", "debris_wood" };

        private static readonly string[] MetalDebris =
            { "debris_metal", "debris_metal", "debris_concrete", "debris_metal", "debris_metal", "debris_roof", "debris_metal", "debris_metal" };


        /// <summary>Footprints of the rubble models, so rubble can be stretched over any building.</summary>
        private static readonly Dictionary<string, UnityEngine.Vector2> RubbleSize = new()
        {
            ["rubble_small"] = new UnityEngine.Vector2(8f, 8f),
            ["rubble_medium"] = new UnityEngine.Vector2(9f, 8.3f),
            ["rubble_large"] = new UnityEngine.Vector2(12f, 10f),
        };

        private readonly Dictionary<EntityId, PropView> _props = new();
        private readonly GameObject _root;
        private readonly SimWorld _world;
        private readonly ModelLibrary _models;
        private readonly MaterialLibrary _materials;
        private readonly List<Mesh> _meshes = new();
        private readonly MapTheme _theme;
        private readonly List<(Transform part, Quaternion rest, Vector3 axis, float speed, float phase, bool rocks)> _moving = new();
        private readonly List<Material> _ownedMaterials = new();
        private Texture2D _groundTexture;

        /// <summary>The battlefield from above for the minimap (painted with the ground; transparent beyond the outline).</summary>
        public Texture2D MinimapTexture { get; private set; }

        // The lava surface: its base colours, and a travelling wave of brightness over them.
        private Mesh _lava;
        private Color[] _lavaBase;
        private float[] _lavaPhase;
        private Color32[] _lavaColours;
        private float _lavaUpdated = -1f;

        /// <param name="shadows">The Shadows setting: trees cast shadows from Medium up, small clutter on High.</param>
        public MapView(SimWorld world, ModelLibrary models, MaterialLibrary materials, MapTheme theme, Transform parent,
            Match.ShadowLevel shadows = Match.ShadowLevel.High)
        {
            var treeShadows = shadows >= Match.ShadowLevel.Medium;
            var clutterShadows = shadows == Match.ShadowLevel.High;
            _world = world;
            _models = models;
            _materials = materials;
            _theme = theme;
            _root = new GameObject("Map");
            _root.transform.SetParent(parent, false);
            BuildGround(world, materials);

            var rng = new Random(17);
            var surfaces = new List<Prop>();
            var still = new List<GameObject>();
            foreach (var prop in world.Props)
            {
                var id = prop.Def.Id;
                if (Surfaces.Contains(id))
                {
                    surfaces.Add(prop);
                    continue;
                }
                var (model, rubble, debris) = Describe(id, rng);
                var vegetation = Vegetation.Contains(id);
                // Tiny clutter (barrels, crates, traps) casts a shadow only on High: many casters, little to see.
                var casts = shadows != Match.ShadowLevel.Off &&
                            (prop.Def.Width * prop.Def.Depth >= 3f || (vegetation ? treeShadows : clutterShadows));
                var movingBefore = _moving.Count;
                var instance = id is "oil_pump" or "radar_station" or "control_tower" or "command_hq" ? SpawnMoving(model, casts, rng) : Spawn(model, casts);
                // Towers on the battlefield are cut down to size so they do not hide the fighting
                // from the high camera (the skyline beyond the edge keeps them full height).
                if (id is "highrise_a" or "highrise_b" or "skyscraper") instance.transform.localScale = new Vector3(1f, 0.62f, 1f);
                if (id is "car" or "truck" or "bus" or "fuel_truck") Repaint(instance, _materials.CarPaints, rng);
                if (id is "container" or "container_stack") Repaint(instance, _materials.ContainerPaints, rng);
                var yaw = vegetation ? (float)rng.NextDouble() * 360f : prop.Rotation;
                // A bridge sits low so its deck is level with the ground and vehicles drive across it
                // (its girders and piers go down into the river).
                instance.transform.SetPositionAndRotation(new Vector3(prop.Position.X, id == "bridge_road" ? -1f : 0f, prop.Position.Y),
                    Quaternion.Euler(0f, yaw, 0f));
                if (vegetation) instance.transform.localScale = Vector3.one * (0.85f + (float)rng.NextDouble() * 0.35f);
                if (!Mathf.Approximately(prop.Def.Scale, 1f)) instance.transform.localScale *= prop.Def.Scale;
                _props.Add(prop.Id, new PropView(prop, instance, model, rubble, debris));
                // Buildings, vehicles and street furniture never move: batch them (not trees, whose
                // wind sway needs their own transforms, nor props with spinning parts).
                if (!vegetation && _moving.Count == movingBefore) still.Add(instance);
            }
            // Static batching: one shared vertex buffer per material instead of a draw per prop. A
            // city block is dozens of props in a dozen materials each; destroyed ones still hide.
            if (still.Count > 1) StaticBatchingUtility.Combine(still.ToArray(), _root);
            BuildSurfaces(world, surfaces);
            if (theme.Cracks > 0f) BuildCracks(TerrainPainter.Cracks(world, theme));
            ScatterBushes(world, rng);
        }

        /// <summary>Turns radar dishes, rocks pumpjacks and moves the glow over lava; call once per frame.</summary>
        private sealed class Collapse
        {
            public Transform Ghost, Rubble;
            public Vector3 Position, Scale, Heap, Axis;
            public Quaternion Rotation;
            public float Start, Seconds, Tilt, Seed;
        }

        private readonly List<Collapse> _collapses = new();
        private readonly Random _collapseRng = new(4242);

        /// <summary>
        /// Buildings coming down: a shudder, then the walls sink into the ground faster and faster
        /// (as falling floors do), spreading and leaning a little, while the rubble heap rises out
        /// of the dust in their place.
        /// </summary>
        private void AnimateCollapses(float time)
        {
            for (var i = _collapses.Count - 1; i >= 0; i--)
            {
                var c = _collapses[i];
                var t = (time - c.Start) / c.Seconds;
                if (t >= 1f || c.Ghost == null)
                {
                    if (c.Ghost != null) Object.Destroy(c.Ghost.gameObject);
                    if (c.Rubble != null) c.Rubble.localScale = c.Heap;
                    _collapses.RemoveAt(i);
                    continue;
                }
                var hold = Mathf.Clamp01(t / 0.15f);
                var fall = Mathf.Clamp01((t - 0.12f) / 0.88f);
                fall *= fall;
                var shake = (0.05f + 0.1f * hold) * (1f - fall);
                var jitter = new Vector3(Mathf.Sin(time * 47f + c.Seed) * shake, 0f, Mathf.Cos(time * 53f + c.Seed * 1.7f) * shake);
                c.Ghost.localScale = new Vector3(c.Scale.x * (1f + 0.08f * fall), c.Scale.y * Mathf.Max(0.04f, 1f - fall), c.Scale.z * (1f + 0.08f * fall));
                c.Ghost.SetPositionAndRotation(c.Position + jitter + Vector3.down * (0.3f * fall), Quaternion.AngleAxis(c.Tilt * fall, c.Axis) * c.Rotation);
                if (c.Rubble != null)
                {
                    var grow = Mathf.Clamp01((t - 0.3f) / 0.7f);
                    c.Rubble.localScale = new Vector3(c.Heap.x, c.Heap.y * Mathf.Lerp(0.08f, 1f, grow * (2f - grow)), c.Heap.z);
                }
            }
        }

        public void Animate(float time)
        {
            if (_collapses.Count > 0) AnimateCollapses(time);
            foreach (var (part, rest, axis, speed, phase, rocks) in _moving)
            {
                if (part == null || !part.gameObject.activeInHierarchy) continue;
                var angle = rocks ? Mathf.Sin(time * speed + phase) * 14f : time * speed + phase;
                part.localRotation = rest * Quaternion.AngleAxis(angle, axis);
            }
            // Slow bands of brightness roll across the lava; a dozen updates a second is plenty.
            if (_lava != null && time - _lavaUpdated >= 0.08f)
            {
                _lavaUpdated = time;
                for (var i = 0; i < _lavaBase.Length; i++)
                {
                    var glow = 0.82f + 0.18f * Mathf.Sin(time * 0.9f + _lavaPhase[i]);
                    _lavaColours[i] = Primitives.Linear(_lavaBase[i] * glow);
                }
                _lava.colors32 = _lavaColours;
            }
        }

        /// <summary>Living prop under a ground point, preferring the smallest (a barrel beside a house).</summary>
        public Prop PropAt(Vector2 point)
        {
            Prop best = null;
            foreach (var prop in _world.Props)
            {
                if (!prop.IsAlive || prop.Def.Indestructible || !prop.Contains(point, 0.6f)) continue;
                if (best == null || prop.Width * prop.Depth < best.Width * best.Depth) best = prop;
            }
            return best;
        }

        /// <summary>Swaps a destroyed prop for its rubble (or hides it) and returns its view for debris.</summary>
        public bool TryDestroy(EntityId id, out PropView view)
        {
            if (!_props.TryGetValue(id, out view)) return false;
            var transform = view.Transform;
            if (view.RubbleModel != null)
            {
                var rubble = Spawn(view.RubbleModel, true);
                rubble.transform.SetPositionAndRotation(transform.position, transform.rotation);
                // Stretch the rubble over the whole footprint (a church leaves a long heap).
                var heap = Vector3.one;
                if (RubbleSize.TryGetValue(view.RubbleModel, out var size))
                    heap = new Vector3(view.Prop.Def.Width / size.x, 1f, view.Prop.Def.Depth / size.y);
                rubble.transform.localScale = new Vector3(heap.x, heap.y * 0.08f, heap.z);
                // The building does not vanish: a copy of it (the original is merged into the static
                // batch and cannot move) shudders and sinks into its own dust while the heap rises.
                var ghost = Spawn(view.Model, true).transform;
                ghost.SetPositionAndRotation(transform.position, transform.rotation);
                ghost.localScale = transform.lossyScale;
                var bearing = (float)_collapseRng.NextDouble() * Mathf.PI * 2f;
                _collapses.Add(new Collapse
                {
                    Ghost = ghost, Rubble = rubble.transform, Position = transform.position, Rotation = transform.rotation,
                    Scale = transform.lossyScale, Heap = heap, Start = Time.time,
                    Seconds = Mathf.Lerp(1.3f, 2.1f, Mathf.InverseLerp(4f, 12f, view.Prop.Radius)),
                    Axis = new Vector3(Mathf.Cos(bearing), 0f, Mathf.Sin(bearing)), Tilt = 4f + (float)_collapseRng.NextDouble() * 7f,
                    Seed = (float)_collapseRng.NextDouble() * 100f,
                });
                view.GameObject.SetActive(false);
                view.GameObject = rubble;
            }
            else
            {
                view.GameObject.SetActive(false);
            }
            return true;
        }

        public void Dispose()
        {
            if (_root != null) Object.Destroy(_root);
            foreach (var mesh in _meshes)
                if (mesh != null) Object.Destroy(mesh);
            foreach (var material in _ownedMaterials)
                if (material != null) Object.Destroy(material);
            if (_groundTexture != null) Object.Destroy(_groundTexture);
            if (MinimapTexture != null) Object.Destroy(MinimapTexture);
            _meshes.Clear();
            _ownedMaterials.Clear();
            _props.Clear();
            _lava = null;
        }

        private (string model, string rubble, string[] debris) Describe(string defId, Random rng) => defId switch
        {
            "house_small" => ("house_small", "rubble_small", BuildingDebris),
            "house_large" => ("house_large", "rubble_large", BuildingDebris),
            "cottage" => ("cottage", "rubble_small", BuildingDebris),
            "townhouse" => ("townhouse", "rubble_medium", BuildingDebris),
            "apartment" => ("apartment", "rubble_large", BuildingDebris),
            "shop" => ("shop", "rubble_medium", BuildingDebris),
            "church" => ("church", "rubble_large", BuildingDebris),
            "barn" => ("barn", "rubble_medium", BarnDebris),
            "warehouse" => ("warehouse", "rubble_large", MetalDebris),
            "garage" => ("garage", "rubble_small", BuildingDebris),
            "ruin" => ("ruin", "rubble_small", BuildingDebris),
            "silo" => ("silo", null, MetalDebris),
            "water_tower" => ("water_tower", "rubble_small", MetalDebris),
            "fence" => ("fence", null, new[] { "debris_wood", "debris_wood", "debris_wood" }),
            "stone_wall" => ("stone_wall", null, new[] { "debris_concrete", "debris_concrete", "debris_concrete", "debris_concrete" }),
            "hedge" => ("hedge", null, new[] { "debris_leaves", "debris_leaves", "debris_leaves", "debris_wood" }),
            "car" => ("car", null, new[] { "debris_metal", "debris_metal", "debris_metal", "debris_metal" }),
            "truck" => ("truck", null, new[] { "debris_metal", "debris_metal", "debris_metal", "debris_metal", "debris_metal", "debris_wood" }),
            "wall" => ("wall", null, new[] { "debris_concrete", "debris_concrete", "debris_concrete", "debris_concrete" }),
            "fuel_tank" => ("fuel_tank", null, new[] { "debris_metal", "debris_metal", "debris_metal", "debris_metal", "debris_metal" }),
            "barrel" => ("barrel", null, new[] { "debris_metal", "debris_metal" }),
            "ammo_crate" => ("ammo_crate", null, new[] { "debris_wood", "debris_wood", "debris_wood" }),
            "sandbags" => ("sandbags", null, new[] { "debris_plaster", "debris_plaster", "debris_plaster" }),
            "tank_trap" => ("tank_trap", null, new[] { "debris_metal", "debris_metal", "debris_metal" }),
            "tree" => (rng.NextDouble() < _theme.DeadTrees ? "tree_dead" : _theme.Trees[rng.Next(_theme.Trees.Length)], null,
                new[] { "debris_leaves", "debris_leaves", "debris_leaves", "debris_wood" }),
            "palm" => ("palm", null, new[] { "debris_leaves", "debris_leaves", "debris_wood", "debris_wood" }),
            "cactus" => ("cactus", null, new[] { "debris_leaves", "debris_leaves" }),
            "adobe_house" => ("adobe_house", "rubble_small", BuildingDebris),
            "adobe_large" => ("adobe_large", "rubble_large", BuildingDebris),
            "market_stall" => ("market_stall", null, new[] { "debris_wood", "debris_wood", "debris_wood" }),
            "oil_pump" => ("oil_pump", null, MetalDebris),
            "refinery_tower" => ("refinery_tower", "rubble_medium", MetalDebris),
            "storage_tank" => ("storage_tank", null, MetalDebris),
            "pipeline" => ("pipeline", null, new[] { "debris_metal", "debris_metal", "debris_metal" }),
            "log_cabin" => ("log_cabin", "rubble_small", BarnDebris),
            "radar_station" => ("radar_station", "rubble_medium", MetalDebris),
            "watchtower" => ("watchtower", null, new[] { "debris_wood", "debris_metal", "debris_wood", "debris_metal" }),
            "container" or "container_stack" => (defId, null, MetalDebris),
            "gantry_crane" => ("gantry_crane", "rubble_large", MetalDebris),
            "factory" => ("factory", "rubble_large", MetalDebris),
            "office_block" => ("office_block", "rubble_large", BuildingDebris),
            "rail_tanker" or "rail_boxcar" => (defId, null, MetalDebris),
            "lamp_post" or "jersey_barrier" or "dock_bollards" => (defId, null, new[] { "debris_concrete", "debris_metal" }),
            // Volcanic: rock is indestructible; the burnt forest splinters.
            "basalt_rock_a" or "basalt_rock_b" or "basalt_rock_c" or "obsidian_spire" or "volcanic_cliff" or "lava_vent" =>
                (defId, null, Array.Empty<string>()),
            "charred_tree" => ("charred_tree", null, new[] { "debris_wood", "debris_wood", "debris_wood" }),
            // Jungle.
            "jungle_tree_a" or "jungle_tree_b" or "jungle_tree_c" or "bamboo_clump" => (defId, null, LeafDebris),
            "fern_bush" => ("fern_bush", null, new[] { "debris_leaves", "debris_leaves" }),
            "temple_ruin" => ("temple_ruin", "rubble_large", new[] { "debris_concrete", "debris_concrete", "debris_plaster", "debris_concrete",
                "debris_concrete", "debris_leaves", "debris_concrete", "debris_plaster" }),
            "stilt_hut" => ("stilt_hut", "rubble_small", BarnDebris),
            // Airbase: jets and tankers vanish into their fireballs.
            "hangar" => ("hangar", "rubble_large", MetalDebris),
            "control_tower" => ("control_tower", "rubble_medium", BuildingDebris),
            "radar_dome" => ("radar_dome", "rubble_medium", MetalDebris),
            "parked_jet" => ("parked_jet", null, new[] { "debris_metal", "debris_metal", "debris_metal", "debris_metal", "debris_metal",
                "debris_metal", "debris_roof" }),
            "fuel_truck" => ("fuel_truck", null, new[] { "debris_metal", "debris_metal", "debris_metal", "debris_metal", "debris_metal" }),
            "revetment" => ("revetment", null, Array.Empty<string>()),
            "runway_light" or "traffic_light" => (defId, null, new[] { "debris_metal" }),
            // City.
            "highrise_a" or "highrise_b" or "skyscraper" => (defId, "rubble_large", BuildingDebris),
            "parking_garage" => ("parking_garage", "rubble_large", new[] { "debris_concrete", "debris_concrete", "debris_concrete",
                "debris_metal", "debris_concrete", "debris_concrete", "debris_metal", "debris_concrete" }),
            "billboard" => ("billboard", null, new[] { "debris_metal", "debris_wood", "debris_metal", "debris_plaster" }),
            "bus" => ("bus", null, new[] { "debris_metal", "debris_metal", "debris_metal", "debris_metal", "debris_metal", "debris_roof" }),
            // Siege fortress.
            "command_hq" => ("command_hq", "rubble_large", new[] { "debris_concrete", "debris_metal", "debris_concrete", "debris_roof",
                "debris_concrete", "debris_metal", "debris_concrete", "debris_metal", "debris_plaster", "debris_concrete" }),
            "base_wall" => ("base_wall", null, new[] { "debris_concrete", "debris_concrete", "debris_concrete", "debris_concrete",
                "debris_concrete" }),
            "base_gate" or "helipad" => (defId, null, Array.Empty<string>()),
            "floodlight_mast" => ("floodlight_mast", null, SteelDebris),
            "fuel_depot" => ("fuel_depot", null, new[] { "debris_metal", "debris_metal", "debris_metal", "debris_metal", "debris_metal",
                "debris_metal" }),
            "ammo_dump" => ("ammo_dump", null, new[] { "debris_wood", "debris_metal", "debris_wood", "debris_metal", "debris_wood" }),
            "vehicle_hangar" => ("vehicle_hangar", "rubble_large", MetalDebris),
            "razor_wire" => ("razor_wire", null, new[] { "debris_metal", "debris_metal" }),
            "sandbag_wall" => ("sandbag_wall", null, new[] { "debris_plaster", "debris_plaster", "debris_plaster", "debris_plaster" }),
            // Map kit: wrecks break into scrap, ruins into rubble; earthworks, craters and the bridge never break.
            "wreck_tank" or "artillery_wreck" => (defId, null, new[] { "debris_metal", "debris_metal", "debris_metal", "debris_metal", "debris_metal",
                "debris_metal" }),
            "wreck_truck" or "wreck_car" or "power_pylon" or "radio_mast" => (defId, null, SteelDebris),
            "trench_straight" or "trench_corner" or "foxhole" or "crater_large" or "tank_ditch" or "bridge_road" => (defId, null, Array.Empty<string>()),
            "command_tent" or "camo_net" => (defId, null, new[] { "debris_wood", "debris_plaster", "debris_wood" }),
            "supply_pile" => ("supply_pile", null, new[] { "debris_wood", "debris_wood", "debris_metal", "debris_wood" }),
            "fuel_bladder" => ("fuel_bladder", null, new[] { "debris_metal", "debris_plaster" }),
            "checkpoint" => ("checkpoint", null, new[] { "debris_wood", "debris_metal", "debris_concrete", "debris_wood" }),
            "barricade" => ("barricade", null, new[] { "debris_concrete", "debris_metal", "debris_concrete" }),
            "telegraph_pole" or "dead_tree" => (defId, null, new[] { "debris_wood", "debris_wood" }),
            "ruin_house" or "ruin_tower" => (defId, "rubble_small", BuildingDebris),
            _ => (defId, null, Array.Empty<string>()),
        };

        /// <summary>
        /// Lava pools, river water and fords as smooth-edged meshes: the tiles' footprints are
        /// rasterised on a 1 m grid, blurred and roughened with noise, and contoured (marching
        /// squares), so a river of square tiles reads as one winding surface. Lava glows on the
        /// unlit shader (HDR through the bloom, not fogged, so it shines at night and in fog);
        /// water is lit, shallow at the banks and fords, dark where it is deep.
        /// </summary>
        private void BuildSurfaces(SimWorld world, List<Prop> tiles)
        {
            var lava = new List<Prop>();
            var water = new List<Prop>();
            var deep = new List<Prop>();
            foreach (var t in tiles)
            {
                if (t.Def.Id == "lava_pool") lava.Add(t);
                else water.Add(t);
                if (t.Def.Id == "river_water") deep.Add(t);
            }
            var half = world.Map.HalfSize;
            if (lava.Count > 0)
            {
                var crust = _theme.LavaCrust;
                var (mesh, verts, fields) = Contour("Lava", lava, null, half);
                _lavaBase = new Color[verts.Count];
                _lavaPhase = new float[verts.Count];
                _lavaColours = new Color32[verts.Count];
                for (var i = 0; i < verts.Count; i++)
                {
                    var v = verts[i];
                    var heat = Edge(0.5f, 0.95f, fields[i].x);
                    // Crust floats in plates on the hotter lava.
                    var n = Mathf.PerlinNoise(v.x * 0.19f + 3.1f, v.z * 0.19f + 7.7f);
                    var plates = Edge(0.52f, 0.7f, n);
                    // Orange to yellow, never white: the material's HDR tint would clip near-white
                    // vertices and show the 1 m grid between them.
                    var hot = Color.Lerp(new Color(0.85f, 0.33f, 0.12f), new Color(1f, 0.7f, 0.28f), heat);
                    _lavaBase[i] = Color.Lerp(crust, hot, (0.25f + heat * 0.75f) * (1f - 0.65f * plates)) * 0.72f;
                    _lavaPhase[i] = v.x * 0.21f + v.z * 0.13f + n * 2.5f;
                    _lavaColours[i] = Primitives.Linear(_lavaBase[i]);
                }
                mesh.colors32 = _lavaColours;
                _lava = mesh;
                var material = new Material(Shader.Find("MachineBrigade/Unlit")) { name = "Lava" };
                material.SetColor("_Color", _theme.LavaHot);
                _ownedMaterials.Add(material);
                Place("Lava", mesh, material, castShadows: false).transform.position = new Vector3(0f, 0.045f, 0f);
            }
            if (water.Count > 0)
            {
                // The material holds the shallow colour; vertex colours darken it to the deep one.
                var shallow = Color.Lerp(_theme.WaterColour, _theme.Palette.Sand, 0.42f);
                var ratio = new Color(Mathf.Clamp01(_theme.WaterColour.r / Mathf.Max(0.01f, shallow.r)),
                    Mathf.Clamp01(_theme.WaterColour.g / Mathf.Max(0.01f, shallow.g)),
                    Mathf.Clamp01(_theme.WaterColour.b / Mathf.Max(0.01f, shallow.b)));
                var (mesh, verts, fields) = Contour("River", water, deep, half);
                var colours = new Color32[verts.Count];
                for (var i = 0; i < verts.Count; i++)
                {
                    var depth = Edge(0.3f, 0.85f, fields[i].y);
                    colours[i] = Primitives.Linear(Color.Lerp(Color.white, ratio, depth));
                }
                mesh.colors32 = colours;
                var material = new Material(_materials.Water) { name = "River" };
                material.SetColor("_BaseColor", shallow);
                material.SetFloat("_Roughness", _theme.WaterRoughness);
                _ownedMaterials.Add(material);
                Place("River", mesh, material, castShadows: false).transform.position = new Vector3(0f, 0.04f, 0f);
            }
        }

        /// <summary>
        /// Marching squares over the tiles' blurred footprint (1 m cells). Returns the mesh, its
        /// vertices and, per vertex, the smoothed coverage of all tiles (x) and of `deep` tiles (y).
        /// </summary>
        private (Mesh mesh, List<Vector3> vertices, List<UnityEngine.Vector2> fields) Contour(string name, List<Prop> tiles,
            List<Prop> deep, float half)
        {
            const float cell = 1f;
            const float iso = 0.5f;
            float minX = float.MaxValue, minZ = float.MaxValue, maxX = float.MinValue, maxZ = float.MinValue;
            foreach (var t in tiles)
            {
                minX = Mathf.Min(minX, t.Position.X - t.Width * 0.5f);
                maxX = Mathf.Max(maxX, t.Position.X + t.Width * 0.5f);
                minZ = Mathf.Min(minZ, t.Position.Y - t.Depth * 0.5f);
                maxZ = Mathf.Max(maxZ, t.Position.Y + t.Depth * 0.5f);
            }
            minX = Mathf.Max(-half, Mathf.Floor(minX) - 3f);
            minZ = Mathf.Max(-half, Mathf.Floor(minZ) - 3f);
            maxX = Mathf.Min(half, Mathf.Ceil(maxX) + 3f);
            maxZ = Mathf.Min(half, Mathf.Ceil(maxZ) + 3f);
            var nx = Mathf.CeilToInt((maxX - minX) / cell);
            var nz = Mathf.CeilToInt((maxZ - minZ) / cell);
            var stride = nx + 1;

            float[] Coverage(List<Prop> set)
            {
                var field = new float[stride * (nz + 1)];
                if (set == null) return field;
                foreach (var t in set)
                {
                    var x0 = t.Position.X - t.Width * 0.5f - 0.3f;
                    var x1 = t.Position.X + t.Width * 0.5f + 0.3f;
                    var z0 = t.Position.Y - t.Depth * 0.5f - 0.3f;
                    var z1 = t.Position.Y + t.Depth * 0.5f + 0.3f;
                    for (var j = Mathf.Max(0, Mathf.CeilToInt((z0 - minZ) / cell)); j <= Mathf.Min(nz, Mathf.FloorToInt((z1 - minZ) / cell)); j++)
                    for (var i = Mathf.Max(0, Mathf.CeilToInt((x0 - minX) / cell)); i <= Mathf.Min(nx, Mathf.FloorToInt((x1 - minX) / cell)); i++)
                        field[j * stride + i] = 1f;
                }
                // Two box blurs (5 x 5) round the tiles' corners into curves.
                var temp = new float[field.Length];
                for (var pass = 0; pass < 2; pass++)
                {
                    for (var j = 0; j <= nz; j++)
                    for (var i = 0; i <= nx; i++)
                    {
                        var sum = 0f;
                        for (var k = -2; k <= 2; k++) sum += field[j * stride + Mathf.Clamp(i + k, 0, nx)];
                        temp[j * stride + i] = sum / 5f;
                    }
                    for (var j = 0; j <= nz; j++)
                    for (var i = 0; i <= nx; i++)
                    {
                        var sum = 0f;
                        for (var k = -2; k <= 2; k++) sum += temp[Mathf.Clamp(j + k, 0, nz) * stride + i];
                        field[j * stride + i] = sum / 5f;
                    }
                }
                return field;
            }

            var cover = Coverage(tiles);
            var depth = Coverage(deep);
            // A ragged shoreline: noise nudges the contour in and out.
            for (var j = 0; j <= nz; j++)
            for (var i = 0; i <= nx; i++)
            {
                var x = minX + i * cell;
                var z = minZ + j * cell;
                cover[j * stride + i] += (Mathf.PerlinNoise(x * 0.31f + 17f, z * 0.31f + 5f) - 0.5f) * 0.28f;
            }

            var vertices = new List<Vector3>();
            var fields = new List<UnityEngine.Vector2>();
            var triangles = new List<int>();
            var corner = new int[stride * (nz + 1)];
            for (var k = 0; k < corner.Length; k++) corner[k] = -1;
            var edges = new Dictionary<int, int>();

            int Corner(int i, int j)
            {
                var k = j * stride + i;
                if (corner[k] >= 0) return corner[k];
                corner[k] = vertices.Count;
                vertices.Add(new Vector3(minX + i * cell, 0f, minZ + j * cell));
                fields.Add(new UnityEngine.Vector2(cover[k], depth[k]));
                return corner[k];
            }

            int EdgePoint(int ia, int ja, int ib, int jb)
            {
                // One key per grid edge: horizontal edges even, vertical odd.
                var key = (Mathf.Min(ja, jb) * stride + Mathf.Min(ia, ib)) * 2 + (ja == jb ? 0 : 1);
                if (edges.TryGetValue(key, out var index)) return index;
                var a = cover[ja * stride + ia];
                var b = cover[jb * stride + ib];
                var t = Mathf.Clamp01((iso - a) / (b - a));
                index = vertices.Count;
                vertices.Add(new Vector3(minX + Mathf.Lerp(ia, ib, t) * cell, 0f, minZ + Mathf.Lerp(ja, jb, t) * cell));
                fields.Add(new UnityEngine.Vector2(iso, Mathf.Lerp(depth[ja * stride + ia], depth[jb * stride + ib], t)));
                edges[key] = index;
                return index;
            }

            var polygon = new List<int>(6);
            var ci = new int[4];
            var cj = new int[4];
            for (var j = 0; j < nz; j++)
            for (var i = 0; i < nx; i++)
            {
                // Corners walked clockwise seen from above, so the fan faces up.
                ci[0] = i; cj[0] = j;
                ci[1] = i; cj[1] = j + 1;
                ci[2] = i + 1; cj[2] = j + 1;
                ci[3] = i + 1; cj[3] = j;
                var any = false;
                for (var k = 0; k < 4; k++) any |= cover[cj[k] * stride + ci[k]] >= iso;
                if (!any) continue;
                polygon.Clear();
                for (var k = 0; k < 4; k++)
                {
                    var n = (k + 1) & 3;
                    var inA = cover[cj[k] * stride + ci[k]] >= iso;
                    var inB = cover[cj[n] * stride + ci[n]] >= iso;
                    if (inA) polygon.Add(Corner(ci[k], cj[k]));
                    if (inA != inB) polygon.Add(EdgePoint(ci[k], cj[k], ci[n], cj[n]));
                }
                for (var k = 1; k < polygon.Count - 1; k++)
                {
                    triangles.Add(polygon[0]);
                    triangles.Add(polygon[k]);
                    triangles.Add(polygon[k + 1]);
                }
            }

            var mesh = new Mesh { name = name, indexFormat = vertices.Count > 65000 ? IndexFormat.UInt32 : IndexFormat.UInt16 };
            mesh.SetVertices(vertices);
            var normals = new Vector3[vertices.Count];
            var uvs = new UnityEngine.Vector2[vertices.Count];
            for (var k = 0; k < normals.Length; k++)
            {
                normals[k] = Vector3.up;
                uvs[k] = new UnityEngine.Vector2(vertices[k].x * 0.25f, vertices[k].z * 0.25f);
            }
            mesh.normals = normals;
            mesh.uv = uvs;
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            // Room above the surface, so it is never culled while a wall of flame stands on it.
            var bounds = mesh.bounds;
            bounds.Expand(new Vector3(0f, 2f, 0f));
            mesh.bounds = bounds;
            Own(mesh);
            return (mesh, vertices, fields);
        }

        /// <summary>The glowing cores of the volcanic cracks: thin tapered ribbons on the unlit lava material.</summary>
        private void BuildCracks(List<UnityEngine.Vector2[]> cracks)
        {
            if (cracks.Count == 0) return;
            var vertices = new List<Vector3>();
            var colours = new List<Color32>();
            var triangles = new List<int>();
            var rng = new Random(911);
            foreach (var crack in cracks)
            {
                var width = 0.16f + (float)rng.NextDouble() * 0.16f;
                var start = vertices.Count;
                for (var i = 0; i < crack.Length; i++)
                {
                    var prev = crack[Mathf.Max(0, i - 1)];
                    var next = crack[Mathf.Min(crack.Length - 1, i + 1)];
                    var dir = (next - prev).normalized;
                    var side = new UnityEngine.Vector2(-dir.y, dir.x);
                    // Widest in the middle, closing to nothing at both ends.
                    var taper = Mathf.Sin(Mathf.PI * (i + 0.5f) / crack.Length) * width;
                    var p = crack[i];
                    vertices.Add(new Vector3(p.x + side.x * taper, 0f, p.y + side.y * taper));
                    vertices.Add(new Vector3(p.x - side.x * taper, 0f, p.y - side.y * taper));
                    var heat = 0.55f + 0.45f * (float)rng.NextDouble();
                    var c = Primitives.Linear(new Color(heat, heat * 0.72f, heat * 0.5f));
                    colours.Add(c);
                    colours.Add(c);
                }
                for (var i = 0; i < crack.Length - 1; i++)
                {
                    var a = start + i * 2;
                    // Two triangles per span, both wound to face up whichever way the crack turns.
                    AddUp(triangles, vertices, a, a + 1, a + 2);
                    AddUp(triangles, vertices, a + 1, a + 3, a + 2);
                }
            }
            var mesh = new Mesh { name = "Cracks", indexFormat = vertices.Count > 65000 ? IndexFormat.UInt32 : IndexFormat.UInt16 };
            mesh.SetVertices(vertices);
            mesh.SetColors(colours);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            Own(mesh);
            var material = new Material(Shader.Find("MachineBrigade/Unlit")) { name = "Cracks" };
            material.SetColor("_Color", _theme.LavaHot * 0.8f);
            _ownedMaterials.Add(material);
            Place("Cracks", mesh, material, castShadows: false).transform.position = new Vector3(0f, 0.03f, 0f);
        }

        private static void AddUp(List<int> triangles, List<Vector3> vertices, int a, int b, int c)
        {
            var normal = Vector3.Cross(vertices[b] - vertices[a], vertices[c] - vertices[a]);
            if (normal.y < 0f) (b, c) = (c, b);
            triangles.Add(a);
            triangles.Add(b);
            triangles.Add(c);
        }

        /// <summary>Shader-style smoothstep: 0 below <paramref name="from"/>, 1 above <paramref name="to"/>.</summary>
        private static float Edge(float from, float to, float x)
        {
            var t = Mathf.Clamp01((x - from) / (to - from));
            return t * t * (3f - 2f * t);
        }

        /// <summary>Bushes in open ground, kept clear of props and both rally areas.</summary>
        private void ScatterBushes(SimWorld world, Random rng)
        {
            if (_theme.Bush == null) return;
            var half = world.Map.HalfSize - 4f;
            var placed = 0;
            for (var attempt = 0; attempt < 400 && placed < 70; attempt++)
            {
                var p = new Vector2((float)(rng.NextDouble() * 2 - 1) * half, (float)(rng.NextDouble() * 2 - 1) * half);
                var clear = true;
                foreach (var prop in world.Props)
                    if (prop.Contains(p, 3f)) { clear = false; break; }
                foreach (var team in world.Map.Teams)
                    if (Vector2.Distance(team.Rally, p) < 22f) clear = false;
                if (!clear) continue;
                var bush = Spawn(_theme.Bush, false);
                bush.transform.SetPositionAndRotation(new Vector3(p.X, 0f, p.Y), Quaternion.Euler(0f, (float)rng.NextDouble() * 360f, 0f));
                bush.transform.localScale = Vector3.one * (0.7f + (float)rng.NextDouble() * 0.6f) * (_theme.Bush == "cactus" ? 0.6f : 1f);
                placed++;
            }
        }

        private void BuildGround(SimWorld world, MaterialLibrary materials)
        {
            var size = world.Map.Size;
            _groundTexture = TerrainPainter.Paint(world, _theme, out var minimap);
            MinimapTexture = minimap;
            materials.Ground.SetTexture("_BaseMap", _groundTexture);
            materials.Pebble.SetColor("_BaseColor", _theme.Pebble);
            materials.GrassTuft.SetColor("_BaseColor", _theme.GrassTuft);

            var groundObject = Place("Ground", Own(GroundMesh(size, 64)), materials.Ground, castShadows: false);
            var collider = groundObject.AddComponent<BoxCollider>();
            collider.center = new Vector3(0f, -0.5f, 0f);
            collider.size = new Vector3(size * 3f, 1f, size * 3f);

            // A dark earth block under the map, as in the reference: nothing is drawn beyond the edge.
            var skirt = Place("Skirt", Own(Primitives.Box()), materials.Skirt, castShadows: false);
            skirt.transform.position = new Vector3(0f, -1.27f, 0f);
            skirt.transform.localScale = new Vector3(size, 2.5f, size);

            var rng = new Random(1482);
            var spread = size - 6f;
            var density = (size / 96f) * (size / 96f) * 0.7f;
            Place("Pebbles", Own(Scatter(Pebble(), (int)(500 * density), spread, rng, world, 0.06f, 0.5f, 1.5f, tilt: true)),
                materials.Pebble, castShadows: false);
            if (_theme.Tufts > 0f)
                Place("Grass", Own(Scatter(GrassTuft(), (int)(850 * density * _theme.Tufts), spread, rng, world, 0f, 0.4f, 1.1f, tilt: false)),
                    materials.GrassTuft, castShadows: false);
        }

        /// <summary>Gives a car, truck or shipping container a random body colour from <paramref name="paints"/>.</summary>
        private static void Repaint(GameObject prop, Material[] paints, Random rng)
        {
            var renderer = prop.GetComponent<MeshRenderer>();
            var materials = renderer.sharedMaterials;
            var paint = paints[rng.Next(paints.Length)];
            for (var i = 0; i < materials.Length; i++)
                if (materials[i] == paints[0]) materials[i] = paint;
            renderer.sharedMaterials = materials;
        }

        /// <summary>
        /// A prop with a moving part (radar dish, pumpjack beam): spawned whole instead of merged,
        /// and its part registered for <see cref="Animate"/>.
        /// </summary>
        private GameObject SpawnMoving(string modelId, bool castShadows, Random rng)
        {
            var instance = _models.Spawn(modelId, -1, _root.transform, castShadows);
            var phase = (float)rng.NextDouble() * 360f;
            foreach (var spinner in instance.Spinners)
                _moving.Add((spinner.Transform, spinner.Rest, spinner.Axis, spinner.DegreesPerSecond * 0.35f, phase, false));
            foreach (var t in instance.Root.GetComponentsInChildren<Transform>(true))
                if (t.name.StartsWith("Pump_beam"))
                    _moving.Add((t, t.localRotation, Vector3.forward, 1.7f, phase, true));
            return instance.Root;
        }

        /// <summary>
        /// A static prop as one renderer: the model merged into a single mesh (one sub-mesh per
        /// material). Props never animate, and identical props then share a mesh, so the engine
        /// instances them: far fewer draw calls in both the camera and the shadow pass.
        /// </summary>
        private GameObject Spawn(string modelId, bool castShadows)
        {
            var merged = _models.Merged(modelId);
            var go = new GameObject(modelId);
            go.transform.SetParent(_root.transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = merged.Mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterials = merged.Materials;
            renderer.shadowCastingMode = castShadows ? ShadowCastingMode.On : ShadowCastingMode.Off;
            renderer.receiveShadows = true;
            return go;
        }

        private GameObject Place(string name, Mesh mesh, Material material, bool castShadows)
        {
            var go = new GameObject(name);
            go.transform.SetParent(_root.transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = castShadows ? ShadowCastingMode.On : ShadowCastingMode.Off;
            renderer.receiveShadows = true;
            return go;
        }

        private Mesh Own(Mesh mesh)
        {
            _meshes.Add(mesh);
            return mesh;
        }

        /// <summary>Many copies of a small mesh merged into one static mesh: one draw call for all.</summary>
        private static Mesh Scatter(Mesh source, int count, float spread, Random rng, SimWorld world, float lift,
            float minScale, float maxScale, bool tilt)
        {
            var instances = new List<CombineInstance>(count);
            for (var i = 0; i < count; i++)
            {
                var p = new Vector2((float)(rng.NextDouble() - 0.5) * spread, (float)(rng.NextDouble() - 0.5) * spread);
                var scale = minScale + (float)rng.NextDouble() * (maxScale - minScale);
                var rotation = tilt
                    ? Quaternion.Euler((float)rng.NextDouble() * 60f, (float)rng.NextDouble() * 360f, (float)rng.NextDouble() * 40f)
                    : Quaternion.Euler(0f, (float)rng.NextDouble() * 360f, 8f);
                var blocked = false;
                foreach (var prop in world.Props)
                    if ((prop.Def.BlocksMovement || Surfaces.Contains(prop.Def.Id)) && prop.Contains(p, 0.5f)) { blocked = true; break; }
                if (blocked) continue;
                instances.Add(new CombineInstance
                {
                    mesh = source,
                    transform = Matrix4x4.TRS(new Vector3(p.X, lift * scale, p.Y), rotation, Vector3.one * scale),
                });
            }
            var mesh = new Mesh { name = source.name + " scatter", indexFormat = IndexFormat.UInt32 };
            mesh.CombineMeshes(instances.ToArray(), true, true);
            Object.Destroy(source);
            return mesh;
        }

        /// <summary>Faceted pebble (flat-shaded icosahedron, about 0.22 m), like the reference's dodecahedra.</summary>
        private static Mesh Pebble()
        {
            var t = (1f + Mathf.Sqrt(5f)) / 2f;
            var corners = new[]
            {
                new Vector3(-1, t, 0), new Vector3(1, t, 0), new Vector3(-1, -t, 0), new Vector3(1, -t, 0),
                new Vector3(0, -1, t), new Vector3(0, 1, t), new Vector3(0, -1, -t), new Vector3(0, 1, -t),
                new Vector3(t, 0, -1), new Vector3(t, 0, 1), new Vector3(-t, 0, -1), new Vector3(-t, 0, 1),
            };
            int[] faces =
            {
                0, 11, 5, 0, 5, 1, 0, 1, 7, 0, 7, 10, 0, 10, 11, 1, 5, 9, 5, 11, 4, 11, 10, 2, 10, 7, 6, 7, 1, 8,
                3, 9, 4, 3, 4, 2, 3, 2, 6, 3, 6, 8, 3, 8, 9, 4, 9, 5, 2, 4, 11, 6, 2, 10, 8, 6, 7, 9, 8, 1,
            };
            return Faceted("Pebble", corners, faces, 0.22f / corners[0].magnitude, new Vector3(1f, 0.6f, 1f));
        }

        /// <summary>Three-sided grass cone (0.22 m wide, 0.6 m tall), like the reference's tufts.</summary>
        private static Mesh GrassTuft()
        {
            var corners = new Vector3[4];
            for (var i = 0; i < 3; i++)
            {
                var a = i * Mathf.PI * 2f / 3f;
                corners[i] = new Vector3(Mathf.Cos(a) * 0.22f, 0f, Mathf.Sin(a) * 0.22f);
            }
            corners[3] = new Vector3(0f, 0.6f, 0f);
            int[] faces = { 0, 3, 1, 1, 3, 2, 2, 3, 0 };
            return Faceted("GrassTuft", corners, faces, 1f, Vector3.one);
        }

        /// <summary>Flat-shaded mesh from shared corners; each triangle is turned to face outward.</summary>
        private static Mesh Faceted(string name, Vector3[] corners, int[] faces, float scale, Vector3 squash)
        {
            var vertices = new List<Vector3>();
            var normals = new List<Vector3>();
            var colors = new List<Color>();
            var triangles = new List<int>();
            var centre = Vector3.zero;
            foreach (var c in corners) centre += c;
            centre = Vector3.Scale(centre / corners.Length * scale, squash);
            for (var f = 0; f < faces.Length; f += 3)
            {
                var a = Vector3.Scale(corners[faces[f]] * scale, squash);
                var b = Vector3.Scale(corners[faces[f + 1]] * scale, squash);
                var c = Vector3.Scale(corners[faces[f + 2]] * scale, squash);
                var n = Vector3.Cross(b - a, c - a).normalized;
                if (Vector3.Dot(n, (a + b + c) / 3f - centre) < 0f)
                {
                    (b, c) = (c, b);
                    n = -n;
                }
                var start = vertices.Count;
                vertices.Add(a);
                vertices.Add(b);
                vertices.Add(c);
                for (var k = 0; k < 3; k++)
                {
                    normals.Add(n);
                    colors.Add(Color.white);
                    triangles.Add(start + k);
                }
            }
            var mesh = new Mesh { name = name };
            mesh.SetVertices(vertices);
            mesh.SetNormals(normals);
            mesh.SetColors(colors);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>Flat grid with UVs spanning the painted ground texture.</summary>
        private static Mesh GroundMesh(float size, int cells)
        {
            var count = cells + 1;
            var vertices = new Vector3[count * count];
            var uvs = new UnityEngine.Vector2[count * count];
            var colors = new Color[count * count];
            var normals = new Vector3[count * count];
            for (var z = 0; z < count; z++)
            for (var x = 0; x < count; x++)
            {
                var i = z * count + x;
                vertices[i] = new Vector3((x / (float)cells - 0.5f) * size, 0f, (z / (float)cells - 0.5f) * size);
                uvs[i] = new UnityEngine.Vector2(x / (float)cells, z / (float)cells);
                colors[i] = Color.white;
                normals[i] = Vector3.up;
            }

            var triangles = new int[cells * cells * 6];
            var t = 0;
            for (var z = 0; z < cells; z++)
            for (var x = 0; x < cells; x++)
            {
                var i = z * count + x;
                // Wound so the face points up (+Y).
                triangles[t++] = i; triangles[t++] = i + count; triangles[t++] = i + 1;
                triangles[t++] = i + 1; triangles[t++] = i + count; triangles[t++] = i + count + 1;
            }

            var mesh = new Mesh { name = "Ground" };
            mesh.SetVertices(vertices);
            mesh.SetUVs(0, uvs);
            mesh.SetColors(colors);
            mesh.SetNormals(normals);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }
    }
}
