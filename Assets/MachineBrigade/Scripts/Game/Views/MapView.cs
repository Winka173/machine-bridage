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
        public PropView(Prop prop, GameObject gameObject, string rubbleModel, IReadOnlyList<string> debris)
        {
            Prop = prop;
            GameObject = gameObject;
            RubbleModel = rubbleModel;
            Debris = debris;
        }

        public Prop Prop { get; }
        public GameObject GameObject { get; set; }
        public Transform Transform => GameObject.transform;

        /// <summary>Model left behind when destroyed, or null when the prop vanishes into its blast.</summary>
        public string RubbleModel { get; }

        /// <summary>Debris chunk models thrown when destroyed.</summary>
        public IReadOnlyList<string> Debris { get; }

        public bool IsBuilding => RubbleModel != null;
    }

    /// <summary>
    /// Ground, props and decoration. Destroyed buildings collapse into rubble; small props vanish
    /// into their blast. Decorative bushes are purely visual and never block movement.
    /// </summary>
    public sealed class MapView : IDisposable
    {
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
        private Texture2D _groundTexture;

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
            foreach (var prop in world.Props)
            {
                var id = prop.Def.Id;
                var (model, rubble, debris) = Describe(id, rng);
                var vegetation = id is "tree" or "palm" or "cactus";
                // Tiny clutter (barrels, crates, traps) casts a shadow only on High: many casters, little to see.
                var casts = shadows != Match.ShadowLevel.Off &&
                            (prop.Def.Width * prop.Def.Depth >= 3f || (vegetation ? treeShadows : clutterShadows));
                var instance = id is "oil_pump" or "radar_station" ? SpawnMoving(model, casts, rng) : Spawn(model, casts);
                if (id is "car" or "truck") Repaint(instance, _materials.CarPaints, rng);
                if (id is "container" or "container_stack") Repaint(instance, _materials.ContainerPaints, rng);
                var yaw = vegetation ? (float)rng.NextDouble() * 360f : prop.Rotation;
                instance.transform.SetPositionAndRotation(new Vector3(prop.Position.X, 0f, prop.Position.Y),
                    Quaternion.Euler(0f, yaw, 0f));
                if (vegetation) instance.transform.localScale = Vector3.one * (0.85f + (float)rng.NextDouble() * 0.35f);
                _props.Add(prop.Id, new PropView(prop, instance, rubble, debris));
            }
            ScatterBushes(world, rng);
        }

        /// <summary>Turns radar dishes and rocks pumpjacks; call once per frame.</summary>
        public void Animate(float time)
        {
            foreach (var (part, rest, axis, speed, phase, rocks) in _moving)
            {
                if (part == null || !part.gameObject.activeInHierarchy) continue;
                var angle = rocks ? Mathf.Sin(time * speed + phase) * 14f : time * speed + phase;
                part.localRotation = rest * Quaternion.AngleAxis(angle, axis);
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
                if (RubbleSize.TryGetValue(view.RubbleModel, out var size))
                    rubble.transform.localScale = new Vector3(view.Prop.Def.Width / size.x, 1f, view.Prop.Def.Depth / size.y);
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
            if (_groundTexture != null) Object.Destroy(_groundTexture);
            _meshes.Clear();
            _props.Clear();
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
            _ => (defId, null, Array.Empty<string>()),
        };

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
            _groundTexture = TerrainPainter.Paint(world, _theme);
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
                    if (prop.Def.BlocksMovement && prop.Contains(p, 0.5f)) { blocked = true; break; }
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
