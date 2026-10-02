using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>What sits on a model's elevating pivot, which decides how high it is raised to fire.</summary>
    public enum BarrelKind
    {
        None,

        /// <summary>A gun barrel (tank cannon, howitzer, autocannon).</summary>
        Gun,

        /// <summary>A mortar tube: fires high.</summary>
        Mortar,

        /// <summary>A box of rocket or missile tubes.</summary>
        Launcher,
    }

    /// <summary>A spawned model and the parts the game animates.</summary>
    public sealed class ModelInstance
    {
        public ModelInstance(GameObject root, Transform turret, IReadOnlyList<Transform> recoilParts, Vector3 muzzle,
            Renderer[] renderers, IReadOnlyDictionary<string, Transform> muzzles, IReadOnlyDictionary<string, Transform> mounts,
            IReadOnlyList<Spinner> spinners, Transform elevation = null, float restPitch = 0f, BarrelKind barrel = BarrelKind.None)
        {
            Root = root;
            Turret = turret;
            RecoilParts = recoilParts;
            Muzzle = muzzle;
            Renderers = renderers;
            Muzzles = muzzles;
            Mounts = mounts;
            Spinners = spinners;
            Elevation = elevation;
            RestPitch = restPitch;
            Barrel = barrel;
        }

        /// <summary>
        /// The pivot the barrel (or launcher) is raised on, at its trunnion under the turret; null
        /// when the model has none. Rotating it about its local X pitches every barrel part,
        /// muzzle and recoiling piece on it.
        /// </summary>
        public Transform Elevation { get; }

        /// <summary>How far the barrel already points up in the model as built, in degrees.</summary>
        public float RestPitch { get; }

        public BarrelKind Barrel { get; }

        /// <summary>`Muzzle_&lt;slot&gt;` empties by lower-case slot name (main, coax, mg, missile, rocket, gun, aam, door_l, door_r, ramp).</summary>
        public IReadOnlyDictionary<string, Transform> Muzzles { get; }

        /// <summary>
        /// Every `Muzzle_&lt;slot&gt;` and `Mount_&lt;slot&gt;` of a slot in name order (Muzzle_mg,
        /// Muzzle_mg.001, ...): the k-th mount of a slot in the vehicle's data is the k-th here.
        /// </summary>
        public IReadOnlyDictionary<string, List<Transform>> MuzzleLists { get; internal set; } = new Dictionary<string, List<Transform>>();
        public IReadOnlyDictionary<string, List<Transform>> MountLists { get; internal set; } = new Dictionary<string, List<Transform>>();

        /// <summary>Launchers on both sides for a slot (pods, rails), left to right; see <see cref="LaunchPoint"/>.</summary>
        public IReadOnlyDictionary<string, List<LaunchPoint>> Launchers { get; internal set; } = new Dictionary<string, List<LaunchPoint>>();

        /// <summary>`Mount_&lt;slot&gt;` yaw pivots of weapons that turn on their own.</summary>
        public IReadOnlyDictionary<string, Transform> Mounts { get; }

        /// <summary>Rotors and radar dishes that spin continuously.</summary>
        public IReadOnlyList<Spinner> Spinners { get; }

        public GameObject Root { get; }

        /// <summary>The `Turret` pivot, or null for models without one.</summary>
        public Transform Turret { get; }

        /// <summary>Barrel parts (Main_cannon, Muzzle_brake) that kick back when firing.</summary>
        public IReadOnlyList<Transform> RecoilParts { get; }

        /// <summary>Muzzle position in the model root's space, for tracers and flashes.</summary>
        public Vector3 Muzzle { get; }

        /// <summary>The full-detail renderers (the far detail level's are in <see cref="Lod1Renderers"/>).</summary>
        public Renderer[] Renderers { get; }

        /// <summary>The far detail level's renderers, one per moving part, inactive until switched to; empty without one.</summary>
        public Renderer[] Lod1Renderers { get; internal set; } = Array.Empty<Renderer>();

        /// <summary>The model's far detail level (sizes, impostor parts); null without one.</summary>
        public ModelLod Lod { get; internal set; }
    }

    /// <summary>A part that spins about a local axis (helicopter rotors, radar dishes).</summary>
    public readonly struct Spinner
    {
        public Spinner(Transform transform, Vector3 axis, float degreesPerSecond)
        {
            Transform = transform;
            Axis = axis;
            DegreesPerSecond = degreesPerSecond;
            Rest = transform.localRotation;
        }

        public Transform Transform { get; }
        public Vector3 Axis { get; }
        public float DegreesPerSecond { get; }
        public Quaternion Rest { get; }
    }

    /// <summary>A single-mesh model (debris chunk) ready for pooled renderers.</summary>
    public readonly struct ChunkModel
    {
        public ChunkModel(Mesh mesh, Material[] materials)
        {
            Mesh = mesh;
            Materials = materials;
        }

        public Mesh Mesh { get; }
        public Material[] Materials { get; }
    }

    /// <summary>
    /// Instantiates the Blender GLB models from Resources/Models and swaps their materials for the
    /// project's (see <see cref="MaterialLibrary.ForModel"/>). Naming contract from the Blender
    /// tools: a `Turret` empty for turrets, Main_cannon / Muzzle_brake parts for recoil.
    /// </summary>
    public sealed partial class ModelLibrary
    {
        private static readonly Regex RecoilPattern = new("^(main_cannon|muzzle_brake)", RegexOptions.IgnoreCase);

        /// <summary>Blender may suffix duplicate names (Turret.001); accept those too.</summary>
        private static readonly Regex TurretPattern = new(@"^Turret(\.\d+)?$");

        /// <summary>Prompt 34 L4: one barrel's own muzzle (Muzzle_b1_gun_001), a child of its mount's Muzzle_ empty.</summary>
        private static readonly Regex AuthoredBarrel = new(@"^Muzzle_b\d+_[A-Za-z0-9_]+$");

        private static readonly Regex MuzzlePattern = new(@"^Muzzle_(main|coax|mg|missile|rocket|gun|aam|door_l|door_r|ramp|agl_l|agl_r|mortar)(\.\d+)?$", RegexOptions.IgnoreCase);
        private static readonly Regex MountPattern = new(@"^Mount_([a-z]+)(\.\d+)?$", RegexOptions.IgnoreCase);

        /// <summary>Spinning parts: (name, local axis, degrees per second). Blender Z (up) is Unity Y.</summary>
        private static readonly (Regex name, Vector3 axis, float speed)[] SpinnerPatterns =
        {
            // Extra copies take a fixed suffix (Rotor_rear, Propeller_2, Radar_search); parts under a
            // pivot are named Rotor_blades and the like, and must not spin a second time.
            (new Regex(@"^Rotor(_rear|_front|_\d+)?(\.\d+)?$"), Vector3.up, 1500f),
            (new Regex(@"^Tail_rotor(\.\d+)?$"), Vector3.right, 2400f),
            (new Regex(@"^Radar(_search|_\d+)?(\.\d+)?$"), Vector3.up, 120f),
            (new Regex(@"^Propeller(_\d+)?(\.\d+)?$"), Vector3.forward, 2200f),
        };

        /// <summary>
        /// Parts that are hidden or moved on their own (the strike jet's bombs, a pumpjack's beam, a
        /// launcher's erector, a tower's sweeping searchlight).
        /// </summary>
        private static readonly Regex LoosePattern = new(@"^(Bombs|Pump_beam|Erector|Searchlight|Lift|Blade)(\.\d+)?$");

        /// <summary>
        /// A boss's destructible parts (prompt 8: Part_engine, Part_hangar.001 ...): each is its own
        /// rigid group, so the view can hide it or put a wreck piece in its place when it breaks.
        /// </summary>
        internal static readonly Regex PartPattern = new(@"^Part_[a-z]+(\.\d+)?$", RegexOptions.IgnoreCase);

        /// <summary>
        /// Play-test 4 (DECISIONS 19R): the bunker vehicle's digging-in parts (Deploy_blade, Deploy_plate_l, Deploy_berm
        /// ...), each its own rigid group so VehicleView.Deploy can swing, raise or grow it at every detail level.
        /// </summary>
        internal static readonly Regex DeployPattern = new(@"^Deploy_[a-z]+(_[lr])?(\.\d+)?$", RegexOptions.IgnoreCase);

        /// <summary>Models whose radar turns slower than the usual 120 degrees a second (an EW tower's jammer head).</summary>
        private static readonly Dictionary<string, float> SlowRadars = new() { ["ew_tower"] = 30f };

        /// <summary>Models whose propeller is something slower (the earth borer's drill head: 300 degrees a second).</summary>
        private static readonly Dictionary<string, float> SlowPropellers = new() { ["earth_borer"] = 300f };

        /// <summary>
        /// Turret parts that elevate with the gun: barrels, muzzle brakes, mortar tubes, rocket and
        /// missile boxes, and the muzzle empties on them. Frames and carriages stay put.
        /// </summary>
        private static readonly Regex BarrelPattern = new(
            @"^(main_cannon|muzzle_brake|mortar_tube|rocket_tubes|tubes|tube_bores|pod(?!_frame)|atgm_pod|launcher|coax|muzzle_main|muzzle_coax|muzzle_missile|muzzle_rocket)\w*(\.\d+)?$",
            RegexOptions.IgnoreCase);

        private const string ElevationName = "Elevation";

        /// <summary>
        /// Play-test 6 (DECISIONS 21H): launchers whose erector is drawn under other names than the barrel parts: they
        /// join the elevating group, so the view can raise them to fire (the Iskander's erector and missiles, the Shahed
        /// truck's launch rack and drone, the Lancet truck's cell box).
        /// </summary>
        private static readonly Dictionary<string, Regex> ErectorParts = new()
        {
            ["ballistic_launcher"] = new Regex("^(erector|missile_)", RegexOptions.IgnoreCase),
            ["shahed_truck"] = new Regex("^(drone_|rack|ram_rods|rams)", RegexOptions.IgnoreCase),
            ["lancet_truck"] = new Regex("^(box_|cell|munition|ram_rods|rams|stripes)", RegexOptions.IgnoreCase),
        };

        /// <summary>
        /// Play-test 6: IFVs whose ATGM box sits on the turret's side. It gets a pivot of its own (`Deploy_atgm`, at the
        /// box's rear foot) instead of riding the gun, so the view raises it only to fire its missile, as a Bradley's TOW.
        /// </summary>
        internal static readonly HashSet<string> SideLaunchers = new() { "ifv", "elite_apc" };

        /// <summary>The ATGM box's own pivot in <see cref="SideLaunchers"/>: its launcher, tubes and missile muzzles move on to it.</summary>
        internal const string SideErectorName = "Deploy_atgm";

        private static void AddSideErector(Transform turret)
        {
            var box = new List<Transform>();
            foreach (Transform child in turret)
                if (Regex.IsMatch(child.name, "^(launcher|tubes|muzzle_missile)", RegexOptions.IgnoreCase)) box.Add(child);
            Bounds? bounds = null;
            foreach (var part in box)
            foreach (var filter in part.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null) continue;
                foreach (var corner in Corners(filter.sharedMesh.bounds))
                {
                    var p = turret.InverseTransformPoint(filter.transform.TransformPoint(corner));
                    if (bounds == null) bounds = new Bounds(p, Vector3.zero);
                    else
                    {
                        var b = bounds.Value;
                        b.Encapsulate(p);
                        bounds = b;
                    }
                }
            }
            if (bounds == null) return;
            var go = new GameObject(SideErectorName);
            go.transform.SetParent(turret, false);
            go.transform.localPosition = new Vector3(bounds.Value.center.x, bounds.Value.min.y, bounds.Value.min.z);
            foreach (var part in box) part.SetParent(go.transform, true);
        }

        /// <summary>
        /// Play-test 6 (DECISIONS 21H): models drawn with the turret in another heading than the one they spawn in. The
        /// siege tank is drawn sieged (siege cannon forward, so its elevating barrel is laid like every other); its
        /// turret is turned round on the template, so every copy (the menu's preview, the level-of-detail bake, the
        /// battle) starts in tank mode with the twin 105 mm forward. VehicleView.Deploy swings it back as it sieges.
        /// </summary>
        internal static readonly Dictionary<string, float> RestTurretYaw = new() { ["siege_tank"] = 180f };

        /// <summary>A coaxial gun's parts (Coax, Coax_mount, Coax_hider, Coax_housing) and its muzzle.</summary>
        private static readonly Regex CoaxPart = new(@"^(Coax(_[a-z]+)?|Muzzle_coax)(\.\d+)?$", RegexOptions.IgnoreCase);

        /// <summary>
        /// Play-test 7 (DECISIONS 22P): a tower model's weapons that none of its towers fire (<see cref="TowerArt.Unarmed"/>)
        /// come off the template before it is merged: a `Mount_&lt;slot&gt;` with everything on it, and the coaxial gun.
        /// </summary>
        private static void StripUnarmed(Transform root, string modelId)
        {
            var gone = new List<Transform>();
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                var mount = MountPattern.Match(t.name);
                if (mount.Success ? TowerArt.Unarmed(modelId, mount.Groups[1].Value) : CoaxPart.IsMatch(t.name) && TowerArt.Unarmed(modelId, "coax"))
                    gone.Add(t);
            }
            foreach (var t in gone)
                if (t != null) Object.DestroyImmediate(t.gameObject);
        }

        private static void TurnToRest(string modelId, Transform root)
        {
            if (!RestTurretYaw.TryGetValue(modelId, out var yaw)) return;
            var turret = Find(root, TurretPattern);
            if (turret != null) turret.localRotation = Quaternion.Euler(0f, yaw, 0f) * turret.localRotation;
        }

        private readonly Dictionary<string, (float pitch, BarrelKind kind)> _elevations = new();

        private readonly MaterialLibrary _materials;
        private readonly Dictionary<string, GameObject> _prefabs = new();
        private readonly Dictionary<string, ChunkModel> _merged = new();
        private readonly Dictionary<string, GameObject> _templates = new();
        private readonly List<Mesh> _ownedMeshes = new();
        private Transform _templateRoot;

        private const string FallbackModel = "light_tank";

        /// <summary>Suffix of a model's high-detail variant in Resources/Models (main_battle_tank_hd.glb).</summary>
        public const string HighDetailSuffix = "_hd";

        /// <summary>
        /// A def's own colour (prompt 20 G.2 boss variants, prompt 25 F2 stand-ins) as the "_Tint" multiply: the data's
        /// colour with the old warm cast (x 1, 0.97, 0.95), scaled to a luminance of 1 so it shifts the hue only. Play-test 11
        /// (DECISIONS "PT11 dark hulls"): the owner wants a variant as bright as its parent (the detail page's untinted
        /// preview); the data's tints run 0.5-1.2 and darkened every variant. No channel goes above 1.8.
        /// </summary>
        public static Vector3 TintOf(System.Numerics.Vector3? tint)
        {
            if (tint is not { } t) return Vector3.one;
            var c = new Vector3(t.X, 0.97f * t.Y, 0.95f * t.Z);
            var luma = 0.2126f * c.x + 0.7152f * c.y + 0.0722f * c.z;
            if (luma <= 1e-3f) return Vector3.one;
            c /= luma;
            var top = Mathf.Max(c.x, Mathf.Max(c.y, c.z));
            return top > 1.8f ? c * (1.8f / top) : c;
        }


        /// <summary>
        /// Load the high-detail variant of a model (Resources/Models/&lt;id&gt;_hd, built by
        /// Tools/blender/build_assets.py) wherever one ships, for the high graphics tiers; models without
        /// one load as usual. Off by default. It may change at any time: models are cached per variant,
        /// so spawns after a change use the other variant and models already in the scene keep theirs.
        /// A variant has the same pivots, muzzles and part names as its model, so nothing else changes.
        /// </summary>
        public static bool HighDetail { get; set; }

        /// <summary>Model id -> the id of its high-detail variant, or the model's own id when none ships.</summary>
        private readonly Dictionary<string, string> _detailIds = new();

        public ModelLibrary(MaterialLibrary materials) => _materials = materials;

        /// <summary>The material library its models are drawn with.</summary>
        public MaterialLibrary Materials => _materials;

        /// <summary>
        /// The resource a model loads from: its high-detail variant when <see cref="HighDetail"/> is on
        /// and one ships, else the model itself.
        /// </summary>
        public string ResolveId(string modelId)
        {
            if (!HighDetail) return modelId;
            if (!_detailIds.TryGetValue(modelId, out var id))
            {
                var variant = modelId + HighDetailSuffix;
                id = Resources.Load<GameObject>("Models/" + variant) != null ? variant : modelId;
                _detailIds[modelId] = id;
            }
            return id;
        }

        /// <param name="lod">Build and bring along the far detail level (vehicles; see <see cref="VehicleLod"/>).</param>
        public ModelInstance Spawn(string modelId, int team, Transform parent, bool castShadows = true, bool lod = false)
        {
            var id = ResolveId(modelId);
            if (lod) EnsureLod(id);
            var root = Object.Instantiate(Template(id), parent, false);
            root.name = modelId;
            var all = root.GetComponentsInChildren<Renderer>(true);
            var full = new List<Renderer>(all.Length);
            var far = new List<Renderer>();
            foreach (var renderer in all)
            {
                if (renderer.name == LodName)
                {
                    renderer.sharedMaterial = _materials.LodSurface(team);
                    far.Add(renderer);
                }
                else
                {
                    var materials = renderer.sharedMaterials;
                    for (var i = 0; i < materials.Length; i++)
                        materials[i] = _materials.ForModel(materials[i] != null ? materials[i].name : string.Empty, team);
                    renderer.sharedMaterials = materials;
                    full.Add(renderer);
                }
                renderer.shadowCastingMode = castShadows ? ShadowCastingMode.On : ShadowCastingMode.Off;
                renderer.receiveShadows = true;
                if (Match.DebugFlags.Has("-mb-probes-off"))
                {
                    renderer.lightProbeUsage = LightProbeUsage.Off;
                    renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
                }
            }

            var turret = Find(root.transform, TurretPattern);
            var recoil = new List<Transform>();
            var muzzle = new Vector3(0f, 1.5f, 1f);
            Transform elevation = null;
            if (turret != null)
            {
                elevation = turret.Find(ElevationName);
                foreach (Transform child in turret)
                    if (RecoilPattern.IsMatch(child.name)) recoil.Add(child);
                if (elevation != null)
                    foreach (Transform child in elevation)
                        if (RecoilPattern.IsMatch(child.name)) recoil.Add(child);
                muzzle = MuzzleOf(root.transform, recoil);
            }

            var muzzles = new Dictionary<string, Transform>();
            var mounts = new Dictionary<string, Transform>();
            var muzzleLists = new Dictionary<string, List<Transform>>();
            var mountLists = new Dictionary<string, List<Transform>>();
            var spinners = new List<Spinner>();
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                var m = MuzzlePattern.Match(t.name);
                if (m.Success)
                {
                    var slot = m.Groups[1].Value.ToLowerInvariant();
                    // The plain name wins for the single lookup (Muzzle_mg before Muzzle_mg.001).
                    if (!muzzles.ContainsKey(slot) || !m.Groups[2].Success) muzzles[slot] = t;
                    if (!muzzleLists.TryGetValue(slot, out var list)) muzzleLists[slot] = list = new List<Transform>();
                    list.Add(t);
                }
                var mount = MountPattern.Match(t.name);
                if (mount.Success)
                {
                    var slot = mount.Groups[1].Value.ToLowerInvariant();
                    if (!mounts.ContainsKey(slot) || !mount.Groups[2].Success) mounts[slot] = t;
                    if (!mountLists.TryGetValue(slot, out var list)) mountLists[slot] = list = new List<Transform>();
                    list.Add(t);
                }
                foreach (var (name, axis, speed) in SpinnerPatterns)
                    if (name.IsMatch(t.name))
                        spinners.Add(new Spinner(t, axis, SpinSpeed(modelId, id, t.name, speed)));
            }
            if (muzzles.TryGetValue("main", out var main)) muzzle = root.transform.InverseTransformPoint(main.position);
            else if (turret == null) muzzle = RoofFront(root.transform);
            _elevations.TryGetValue(id, out var raise);
            var launchers = new Dictionary<string, List<LaunchPoint>>();
            foreach (var point in root.GetComponentsInChildren<LaunchPoint>(true))
            {
                if (!launchers.TryGetValue(point.Slot, out var list)) launchers[point.Slot] = list = new List<LaunchPoint>();
                list.Add(point);
            }
            foreach (var list in muzzleLists.Values) list.Sort((a, b) => string.CompareOrdinal(a.name, b.name));
            foreach (var list in mountLists.Values) list.Sort((a, b) => string.CompareOrdinal(a.name, b.name));
            return new ModelInstance(root, turret, recoil, muzzle, full.ToArray(), muzzles, mounts, spinners, elevation,
                raise.pitch, elevation != null ? raise.kind : BarrelKind.None)
            {
                Launchers = launchers, MuzzleLists = muzzleLists, MountLists = mountLists,
                Lod1Renderers = far.ToArray(), Lod = lod && _lods.TryGetValue(id, out var info) ? info : null,
            };
        }

        /// <summary>
        /// Every mesh of a model with its transform relative to the model root and its resolved
        /// materials, for merging many static copies into a few big meshes.
        /// </summary>
        public IEnumerable<(Mesh mesh, Matrix4x4 local, Material[] materials)> Parts(string modelId, int team = -1)
        {
            var root = Prefab(ResolveId(modelId)).transform;
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                var renderer = filter.GetComponent<MeshRenderer>();
                if (filter.sharedMesh == null || renderer == null) continue;
                var source = renderer.sharedMaterials;
                var materials = new Material[source.Length];
                for (var i = 0; i < source.Length; i++)
                    materials[i] = _materials.ForModel(source[i] != null ? source[i].name : string.Empty, team);
                yield return (filter.sharedMesh, root.worldToLocalMatrix * filter.transform.localToWorldMatrix, materials);
            }
        }

        /// <summary>First mesh of a model, with materials resolved; used for pooled debris.</summary>
        public ChunkModel Chunk(string modelId)
        {
            var filter = Prefab(ResolveId(modelId)).GetComponentInChildren<MeshFilter>(true);
            var renderer = filter != null ? filter.GetComponent<MeshRenderer>() : null;
            if (filter == null || renderer == null) throw new InvalidOperationException($"Model '{modelId}' has no mesh.");
            var materials = renderer.sharedMaterials;
            var resolved = new Material[materials.Length];
            for (var i = 0; i < materials.Length; i++)
                resolved[i] = _materials.ForModel(materials[i] != null ? materials[i].name : string.Empty, -1);
            return new ChunkModel(filter.sharedMesh, resolved);
        }

        /// <summary>Builds a model's merged template (and its far detail level, unless -mb-no-lod) now rather than on its first spawn mid-battle.</summary>
        public void Prewarm(string modelId)
        {
            var id = ResolveId(modelId);
            Template(id);
            if (VehicleLod.Enabled) EnsureLod(id);
        }

        /// <summary>Whether a model exists in Resources/Models.</summary>
        public bool Has(string modelId) => _prefabs.ContainsKey(modelId) || Resources.Load<GameObject>("Models/" + modelId) != null;

        /// <summary>
        /// The whole model baked into one mesh (one sub-mesh per material), for small pooled
        /// objects such as missiles and bombs. Cached; the caller must not destroy it.
        /// </summary>
        public ChunkModel Merged(string modelId)
        {
            modelId = ResolveId(modelId);
            if (_merged.TryGetValue(modelId, out var cached)) return cached;
            var root = Prefab(modelId).transform;
            var byMaterial = new Dictionary<string, List<CombineInstance>>();
            var materials = new Dictionary<string, Material>();
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                var renderer = filter.GetComponent<MeshRenderer>();
                if (filter.sharedMesh == null || renderer == null) continue;
                var matrix = root.worldToLocalMatrix * filter.transform.localToWorldMatrix;
                var shared = renderer.sharedMaterials;
                for (var i = 0; i < filter.sharedMesh.subMeshCount; i++)
                {
                    var name = i < shared.Length && shared[i] != null ? shared[i].name : string.Empty;
                    if (!byMaterial.TryGetValue(name, out var list)) byMaterial[name] = list = new List<CombineInstance>();
                    list.Add(new CombineInstance { mesh = filter.sharedMesh, subMeshIndex = i, transform = matrix });
                    materials[name] = _materials.ForModel(name, -1);
                }
            }
            var parts = new List<CombineInstance>();
            var resolved = new List<Material>();
            foreach (var (name, list) in byMaterial)
            {
                var part = new Mesh { name = $"{modelId} {name}" };
                part.CombineMeshes(list.ToArray(), mergeSubMeshes: true, useMatrices: true);
                parts.Add(new CombineInstance { mesh = part, transform = Matrix4x4.identity });
                resolved.Add(materials[name]);
            }
            var merged = new Mesh { name = modelId + " merged" };
            merged.CombineMeshes(parts.ToArray(), mergeSubMeshes: false, useMatrices: false);
            foreach (var p in parts)
            {
                if (Application.isPlaying) Object.Destroy(p.mesh);
                else Object.DestroyImmediate(p.mesh);
            }
            var chunk = new ChunkModel(merged, resolved.ToArray());
            _merged[modelId] = chunk;
            return chunk;
        }

        /// <summary>Destroys the meshes this library built (merged models and templates).</summary>
        public void Dispose()
        {
            foreach (var mesh in _ownedMeshes) Release(mesh);
            foreach (var chunk in _merged.Values) Release(chunk.Mesh);
            if (_templateRoot != null) Release(_templateRoot.gameObject);
            _ownedMeshes.Clear();
            _merged.Clear();
            _templates.Clear();
        }

        /// <summary>
        /// A copy of the model (a resolved id, see <see cref="ResolveId"/>) with its rigid parts merged:
        /// every mesh is combined into one per part that moves on its own (the hull, the turret, each
        /// recoiling barrel, weapon mount, rotor and propeller). A tank drops from about twenty renderers
        /// to four or five, which cuts draw calls in the camera and the shadow pass alike. Built once per model.
        /// </summary>
        private GameObject Template(string modelId)
        {
            if (_templates.TryGetValue(modelId, out var cached)) return cached;
            if (_templateRoot == null)
            {
                var holder = new GameObject("Model Templates");
                holder.SetActive(false);
                _templateRoot = holder.transform;
            }
            var template = Object.Instantiate(Prefab(modelId), _templateRoot, false);
            template.name = modelId;
            StripUnarmed(template.transform, modelId);
            AlignMuzzles(template.transform);
            var raise = AddElevation(template.transform, modelId);
            if (raise.kind != BarrelKind.None) _elevations[modelId] = raise;
            AddLaunchPoints(template.transform);
            AddBarrelPoints(template.transform);
            // Prompt 29 5.5: the flare dispensers' and APS cassettes' effect points, while their meshes still say where they are.
            AddEffectPoints(template.transform);
            MergeRigidParts(template.transform);
            TurnToRest(modelId, template.transform);
            _templates[modelId] = template;
            return template;
        }

        /// <summary>
        /// Where each weapon slot's rounds leave from, looked for in this order: launchers in pairs
        /// or rows across the model (pods, rails, twin guns; one launch point each, used in turn),
        /// else the face of a box of tubes (one launch point in the middle of the face, each round
        /// leaving from a random spot on it, as from a different tube).
        /// </summary>
        private static readonly (string slot, string[] pairs, string[] faces)[] Launchers =
        {
            ("rocket", new[] { "Pods", "Rocket_pod", "Rocket_pods", "Standoff_missile", "Ordnance_bodies", "Bomb_bodies" },
                new[] { "Pod_face", "Tubes_bore", "Rocket_tubes_face", "Box_face", "Launcher_face", "Launcher_tubes_bore", "Tubes" }),
            ("missile", new[] { "Missiles", "Launch_tubes", "Missile_pack", "ATGM_pod", "Standoff_missile", "Missile_racks", "Bomb_bodies", "Ordnance_bodies" },
                new[] { "Tubes_bore", "Launcher_tubes_bore", "Launcher_covers", "Tubes" }),
            ("gun", new[] { "Miniguns" }, new string[0]),
            ("main", new[] { "Pods" },
                new[] { "Tubes_bore", "Pod_face", "Rocket_tubes_face", "Box_face", "Launcher_face", "Launcher_tubes_bore", "Launcher_covers", "Tubes" }),
        };

        /// <summary>
        /// Launch points for the slots in <see cref="Launchers"/>, next to the slot's muzzle so they
        /// turn and elevate with it. Paired launchers are found by grouping the meshes' vertices
        /// across the model (a gap of 0.35 m or more starts a new group; two groups at least); a
        /// face of tubes is taken whole. A slot with neither keeps its muzzle.
        /// </summary>
        private static void AddLaunchPoints(Transform root)
        {
            var byName = new Dictionary<string, List<MeshFilter>>(StringComparer.OrdinalIgnoreCase);
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null || !filter.sharedMesh.isReadable) continue;
                var name = Regex.Replace(filter.name, @"\.\d+$", string.Empty);
                if (!byName.TryGetValue(name, out var list)) byName[name] = list = new List<MeshFilter>();
                list.Add(filter);
            }
            var muzzles = new Dictionary<string, Transform>();
            var every = new List<(string slot, Transform muzzle)>();
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                var m = MuzzlePattern.Match(t.name);
                if (!m.Success) continue;
                muzzles[m.Groups[1].Value.ToLowerInvariant()] = t;
                every.Add((m.Groups[1].Value.ToLowerInvariant(), t));
            }
            foreach (var (slot, pairs, faces) in Launchers)
            {
                if (!muzzles.TryGetValue(slot, out var muzzle)) continue;
                // Only launchers round the slot's own muzzle: a model can carry other pods and
                // tubes elsewhere (a boss with sponson pods and a rear rocket box).
                var at = root.InverseTransformPoint(muzzle.position);
                var hint = root.InverseTransformDirection(muzzle.forward);
                List<(Vector3 front, Vector2 half, Vector3 axis, bool measured)> found = null;
                var face = false;
                foreach (var part in pairs)
                    if (byName.TryGetValue(part, out var filters) && LauncherGroups(root, filters, hint, Aligned(muzzle)) is { Count: >= 2 } groups &&
                        (AroundMuzzle(groups, at) || (part is "Ordnance_bodies" or "Bomb_bodies" && Straddles(groups, at))))
                    {
                        found = groups;
                        break;
                    }
                if (found == null)
                    foreach (var part in faces)
                        if (byName.TryGetValue(part, out var filters) && WholeFace(root, filters, hint) is var whole && Vector3.Distance(whole.front, at) < 1.6f)
                        {
                            found = new List<(Vector3, Vector2, Vector3, bool)> { whole };
                            face = true;
                            break;
                        }
                if (found == null) continue;
                for (var i = 0; i < found.Count; i++)
                {
                    var (front, half, axis, measured) = found[i];
                    var point = new GameObject($"Launch_{slot}_{i}").transform;
                    point.SetParent(muzzle.parent, false);
                    point.position = root.TransformPoint(front);
                    // Along its tubes (a tilted box's face is square to them), else the muzzle's way.
                    point.rotation = measured ? root.rotation * Quaternion.LookRotation(axis, Vector3.up) : muzzle.rotation;
                    var launch = point.gameObject.AddComponent<LaunchPoint>();
                    launch.Slot = slot;
                    launch.Spread = face ? half * 0.8f : Vector2.zero;
                    launch.Measured = measured || Aligned(muzzle);
                }
            }
            // Prompt 16: a second launcher of a slot on its own trainable mount (the hovercraft's two rocket
            // boxes): its face of tubes, found among the meshes on that mount alone, gets launch points of its own.
            foreach (var (slot, faces) in LauncherFaces())
                foreach (var (muzzleSlot, muzzle) in every)
                {
                    // Only a muzzle on its own Mount_<slot> pivot beside another of the slot's (not a pod pair on one airframe).
                    if (muzzleSlot != slot || muzzles[slot] == muzzle || !(MountOf(muzzle) is { } mount) || MountSlot(mount) != slot ||
                        MountOf(muzzles[slot]) is not { } primary || primary == mount || MountSlot(primary) != slot) continue;
                    if (mount.GetComponentsInChildren<LaunchPoint>(true).Length > 0) continue;
                    var at = root.InverseTransformPoint(muzzle.position);
                    var hint = root.InverseTransformDirection(muzzle.forward);
                    foreach (var part in faces)
                    {
                        if (!byName.TryGetValue(part, out var filters)) continue;
                        var own = filters.FindAll(f => f.transform.IsChildOf(mount));
                        if (own.Count == 0) continue;
                        var (front, half, axis, measured) = WholeFace(root, own, hint);
                        if (Vector3.Distance(front, at) >= 1.6f) continue;
                        var point = new GameObject($"Launch_{slot}_x").transform;
                        point.SetParent(muzzle.parent, false);
                        point.position = root.TransformPoint(front);
                        point.rotation = measured ? root.rotation * Quaternion.LookRotation(axis, Vector3.up) : muzzle.rotation;
                        var launch = point.gameObject.AddComponent<LaunchPoint>();
                        launch.Slot = slot;
                        launch.Spread = half * 0.8f;
                        launch.Measured = measured || Aligned(muzzle);
                        break;
                    }
                }
        }

        private static IEnumerable<(string slot, string[] faces)> LauncherFaces()
        {
            foreach (var (slot, _, faces) in Launchers) yield return (slot, faces);
        }

        private static string MountSlot(Transform mount) => MountPattern.Match(mount.name).Groups[1].Value.ToLowerInvariant();

        /// <summary>The weapon mount pivot (Mount_*) a muzzle turns with, or null.</summary>
        private static Transform MountOf(Transform muzzle)
        {
            for (var t = muzzle.parent; t != null; t = t.parent)
                if (MountPattern.IsMatch(t.name)) return t;
            return null;
        }

        /// <summary>Whether a row of launchers is the one a muzzle stands for: level with it, and spread either side of it.</summary>
        private static bool AroundMuzzle(List<(Vector3 front, Vector2 half, Vector3 axis, bool measured)> groups, Vector3 muzzle)
        {
            float y = 0f, z = 0f, left = float.MaxValue, right = float.MinValue;
            foreach (var (front, _, _, _) in groups)
            {
                y += front.y;
                z += front.z;
                left = Mathf.Min(left, front.x);
                right = Mathf.Max(right, front.x);
            }
            y /= groups.Count;
            z /= groups.Count;
            return Mathf.Abs(muzzle.y - y) < 1.2f && Mathf.Abs(muzzle.z - z) < 2f && muzzle.x > left - 0.6f && muzzle.x < right + 0.6f;
        }

        /// <summary>Stores hung either side of the centreline a muzzle marks (a drone's bombs under its wings, well behind the hint).</summary>
        private static bool Straddles(List<(Vector3 front, Vector2 half, Vector3 axis, bool measured)> groups, Vector3 muzzle)
        {
            float left = float.MaxValue, right = float.MinValue;
            foreach (var (front, _, _, _) in groups)
            {
                left = Mathf.Min(left, front.x);
                right = Mathf.Max(right, front.x);
            }
            return left < muzzle.x && right > muzzle.x;
        }

        /// <summary>The front face of a box of tubes: its middle (root space), its half width and height, and the tubes' axis.</summary>
        private static (Vector3 front, Vector2 half, Vector3 axis, bool measured) WholeFace(Transform root, List<MeshFilter> filters, Vector3 hint)
        {
            var points = new List<Vector3>();
            foreach (var filter in filters)
                foreach (var v in filter.sharedMesh.vertices)
                    points.Add(root.InverseTransformPoint(filter.transform.TransformPoint(v)));
            return Front(points, hint);
        }

        /// <summary>The launchers in a set of meshes, left to right: the middle of each one's front face (root space), its half width and height, and its axis.</summary>
        private static List<(Vector3 front, Vector2 half, Vector3 axis, bool measured)> LauncherGroups(Transform root, List<MeshFilter> filters, Vector3 hint,
            bool alongMuzzle = false)
        {
            var points = new List<Vector3>();
            foreach (var filter in filters)
                foreach (var v in filter.sharedMesh.vertices)
                    points.Add(root.InverseTransformPoint(filter.transform.TransformPoint(v)));
            points.Sort((a, b) => a.x.CompareTo(b.x));
            var groups = new List<(Vector3, Vector2, Vector3, bool)>();
            var start = 0;
            for (var i = 1; i <= points.Count; i++)
            {
                if (i < points.Count && points[i].x - points[i - 1].x < 0.35f) continue;
                if (alongMuzzle)
                {
                    // Raised tubes whose muzzle is turned along them: the front of each on its own axis.
                    var (front, half, _, _) = Front(points.GetRange(start, i - start), hint, pca: false);
                    groups.Add((front, half, hint, true));
                    start = i;
                    continue;
                }
                // Pods and rails sit level on their pylons: the front of each one's bounds (a raised
                // rack's axis is left to its muzzle; see AlignMuzzles).
                var lo = points[start];
                var hi = points[start];
                for (var k = start; k < i; k++)
                {
                    lo = Vector3.Min(lo, points[k]);
                    hi = Vector3.Max(hi, points[k]);
                }
                groups.Add((new Vector3((lo.x + hi.x) * 0.5f, (lo.y + hi.y) * 0.5f, hi.z), new Vector2((hi.x - lo.x) * 0.5f, (hi.y - lo.y) * 0.5f), hint, false));
                start = i;
            }
            return groups;
        }

        /// <summary>
        /// The front of a launcher (a pod, a stored missile, a box of tubes or its face) from its
        /// vertices: its axis is its long axis when it is long and thin, the normal of its face when
        /// it is flat, else <paramref name="hint"/> (the muzzle's way); the point is its middle on the
        /// plane square to that axis through its front-most vertex, with its half width and height
        /// in that plane. A tilted box of tubes (a raised MLRS pod) is square to its tubes, so its
        /// front is not the front of its bounding box (DECISIONS 13E).
        /// </summary>
        internal static (Vector3 front, Vector2 half, Vector3 axis, bool measured) Front(List<Vector3> points, Vector3 hint, bool pca = true)
        {
            hint = hint.sqrMagnitude > 1e-6f ? hint.normalized : Vector3.forward;
            var axis = hint;
            var measured = false;
            if (pca && Principal(points, out _, out var e1, out var e3, out var l1, out var l2, out var l3))
            {
                // A flat face first (a wide face of tubes is also longer across than it is tall),
                // then a long pod or missile; only one facing roughly the muzzle's way.
                foreach (var (a0, fits) in new[] { (e3, l3 < 0.3f * l2), (e1, l1 > 2.5f * l2) })
                {
                    if (!fits) continue;
                    var a = Vector3.Dot(a0, hint) < 0f ? -a0 : a0;
                    if (Vector3.Angle(a, hint) >= 60f) continue;
                    axis = a;
                    measured = true;
                    break;
                }
            }
            var far = float.MinValue;
            var sum = Vector3.zero;
            foreach (var p in points)
            {
                far = Mathf.Max(far, Vector3.Dot(p, axis));
                sum += p;
            }
            var centre = sum / Mathf.Max(1, points.Count);
            var front = centre + axis * (far - Vector3.Dot(centre, axis));
            var across = Vector3.Cross(Vector3.up, axis);
            across = across.sqrMagnitude > 1e-6f ? across.normalized : Vector3.right;
            var up = Vector3.Cross(axis, across);
            var half = Vector2.zero;
            foreach (var p in points)
            {
                var d = p - front;
                half = Vector2.Max(half, new Vector2(Mathf.Abs(Vector3.Dot(d, across)), Mathf.Abs(Vector3.Dot(d, up))));
            }
            return (front, half, axis, measured);
        }

        /// <summary>
        /// Principal axes of a point cloud: its mean, the axes of most and least spread and the
        /// three spreads (variances), largest first. False for fewer than four points.
        /// </summary>
        internal static bool Principal(List<Vector3> points, out Vector3 mean, out Vector3 major, out Vector3 minor, out float l1, out float l2, out float l3)
        {
            mean = Vector3.zero;
            major = Vector3.forward;
            minor = Vector3.up;
            l1 = l2 = l3 = 0f;
            if (points.Count < 4) return false;
            foreach (var p in points) mean += p;
            mean /= points.Count;
            double xx = 0, xy = 0, xz = 0, yy = 0, yz = 0, zz = 0;
            foreach (var p in points)
            {
                var d = p - mean;
                xx += d.x * d.x;
                xy += d.x * d.y;
                xz += d.x * d.z;
                yy += d.y * d.y;
                yz += d.y * d.z;
                zz += d.z * d.z;
            }
            var n = (double)points.Count;
            var c = new[,] { { xx / n, xy / n, xz / n }, { xy / n, yy / n, yz / n }, { xz / n, yz / n, zz / n } };
            var trace = c[0, 0] + c[1, 1] + c[2, 2];
            if (trace <= 1e-12) return false;
            // Power iteration on the covariance for the largest axis, then on what is left for the second.
            var v1 = Power(c, new[] { 0.3, 0.2, 1.0 }, null);
            var a1 = Rayleigh(c, v1);
            var v2 = Power(c, new[] { 1.0, 0.3, 0.2 }, v1);
            var a2 = Rayleigh(c, v2);
            var v3 = new[] { v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0] };
            var a3 = Rayleigh(c, v3);
            major = new Vector3((float)v1[0], (float)v1[1], (float)v1[2]).normalized;
            minor = new Vector3((float)v3[0], (float)v3[1], (float)v3[2]).normalized;
            l1 = (float)a1;
            l2 = (float)a2;
            l3 = (float)Math.Max(0.0, a3);
            return true;
        }

        private static double[] Power(double[,] c, double[] v, double[] orthogonalTo)
        {
            for (var it = 0; it < 64; it++)
            {
                if (orthogonalTo != null)
                {
                    var dot = v[0] * orthogonalTo[0] + v[1] * orthogonalTo[1] + v[2] * orthogonalTo[2];
                    for (var k = 0; k < 3; k++) v[k] -= dot * orthogonalTo[k];
                }
                var w = new double[3];
                for (var r = 0; r < 3; r++) w[r] = c[r, 0] * v[0] + c[r, 1] * v[1] + c[r, 2] * v[2];
                var len = Math.Sqrt(w[0] * w[0] + w[1] * w[1] + w[2] * w[2]);
                if (len < 1e-15) break;
                for (var k = 0; k < 3; k++) v[k] = w[k] / len;
            }
            var norm = Math.Sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
            if (norm > 0) for (var k = 0; k < 3; k++) v[k] /= norm;
            return v;
        }

        private static double Rayleigh(double[,] c, double[] v)
        {
            double s = 0;
            for (var r = 0; r < 3; r++)
                for (var k = 0; k < 3; k++) s += v[r] * c[r, k] * v[k];
            return s;
        }

        /// <summary>
        /// Turns every `Muzzle_` empty along the barrel it sits on (the Blender tools place them by
        /// position only, facing the model's front): a part beside it, under the same pivot, long
        /// and thin, whose axis runs through the muzzle and whose front end is at it. A mortar tube,
        /// a raised rocket box, a door gun or a flak barrel built pointing up then fires and flashes
        /// the way it is drawn (<see cref="VehicleView.DrawnBarrelOf"/>). Muzzles with no such part
        /// (a gun inside a merged hull mesh) keep facing the front (DECISIONS 13E).
        /// </summary>
        private static void AlignMuzzles(Transform root)
        {
            foreach (var muzzle in root.GetComponentsInChildren<Transform>(true))
            {
                if (!MuzzlePattern.IsMatch(muzzle.name) || muzzle.parent == null) continue;
                // Missile and rocket racks are found whole by AddLaunchPoints (their faces and pods).
                if (muzzle.name.StartsWith("Muzzle_missile") || muzzle.name.StartsWith("Muzzle_rocket")) continue;
                var at = muzzle.position;
                var best = float.MaxValue;
                var axis = Vector3.zero;
                foreach (Transform sibling in muzzle.parent)
                {
                    var filter = sibling.GetComponent<MeshFilter>();
                    if (filter == null || filter.sharedMesh == null || !filter.sharedMesh.isReadable) continue;
                    var all = new List<Vector3>();
                    foreach (var v in filter.sharedMesh.vertices) all.Add(filter.transform.TransformPoint(v));
                    // The piece of the part round the muzzle, or one of its connected pieces (a gun
                    // among several built as one part, an AC-130's side guns).
                    var candidates = Pieces(filter);
                    candidates.Add(Piece(all, at));
                    foreach (var points in candidates)
                    {
                        if (!Principal(points, out var mean, out var major, out _, out var l1, out var l2, out _) || l1 < 6f * l2) continue;
                        if (Vector3.Dot(major, at - mean) < 0f) major = -major;
                        // Its front end, and how far the muzzle is off its axis and from that end.
                        var far = float.MinValue;
                        foreach (var p in points) far = Mathf.Max(far, Vector3.Dot(p - mean, major));
                        var d = at - mean;
                        var along = Vector3.Dot(d, major);
                        var off = (d - major * along).magnitude;
                        var radius = Mathf.Sqrt(2f * l2);
                        var length = far;
                        if (off > Mathf.Max(0.06f, radius * 1.2f) || along < length * 0.75f || along > length + Mathf.Max(0.15f, length * 0.25f)) continue;
                        var score = off + Mathf.Abs(along - length) * 0.5f;
                        if (score >= best) continue;
                        best = score;
                        axis = major;
                    }
                }
                // Barrels built along the model's front keep it exactly: a whole gun's principal axis
                // (its body, feed and barrel) wanders a few degrees off its bore.
                if (axis == Vector3.zero || Vector3.Angle(axis, muzzle.forward) < 10f) continue;
                muzzle.rotation = Quaternion.LookRotation(axis, Mathf.Abs(axis.y) > 0.95f ? muzzle.forward : Vector3.up);
                muzzle.gameObject.AddComponent<AlignedMuzzle>();
            }
        }

        /// <summary>
        /// The piece of a part's vertices (world) round <paramref name="at"/>: split where they stand
        /// 0.35 m or more apart across the model (a part holding both wings' missiles, twin barrels),
        /// the piece whose span holds the point or is nearest it.
        /// </summary>
        private static List<Vector3> Piece(List<Vector3> points, Vector3 at)
        {
            points.Sort((a, b) => a.x.CompareTo(b.x));
            List<Vector3> best = points;
            var bestGap = float.MaxValue;
            var start = 0;
            for (var i = 1; i <= points.Count; i++)
            {
                if (i < points.Count && points[i].x - points[i - 1].x < 0.35f) continue;
                var lo = points[start].x;
                var hi = points[i - 1].x;
                var gap = at.x < lo ? lo - at.x : at.x > hi ? at.x - hi : 0f;
                if (gap < bestGap)
                {
                    bestGap = gap;
                    best = points.GetRange(start, i - start);
                }
                start = i;
            }
            return best;
        }

        /// <summary>
        /// A twin or quad gun built as one part with one `Muzzle_` between its barrels (a boss's twin flak,
        /// a fortress's autocannons, a bomber's tail guns, a jet's twin cannon): one launch point on each
        /// barrel's tip, so rounds and flashes leave from the barrels in turn, not from the air between
        /// them. The barrels are the part's separate long, thin pieces (its connected pieces, welded by
        /// position) running along the muzzle beside it, a barrel and its brake counting as one; parts
        /// that recoil (a main gun's Main_cannon, Main_cannon_2) are left to VehicleView's twin barrels.
        /// Slots that already have launch points keep them (DECISIONS 13E).
        /// </summary>
        private static void AddBarrelPoints(Transform root)
        {
            var taken = new HashSet<(Transform, string)>();
            foreach (var point in root.GetComponentsInChildren<LaunchPoint>(true)) taken.Add((point.transform.parent, point.Slot));
            // Prompt 34 L4: barrels the model names itself (Muzzle_b<k>_<tag> under a mount's Muzzle_<slot>, written by the Blender
            // builders for the guns that fire their barrels together): each is a launch point of its own, and the slot's muzzle
            // is not searched for barrels.
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                if (t.parent == null || !AuthoredBarrel.IsMatch(t.name) || t.GetComponent<LaunchPoint>() != null) continue;
                var owner = MuzzlePattern.Match(t.parent.name);
                if (!owner.Success) continue;
                var launch = t.gameObject.AddComponent<LaunchPoint>();
                launch.Slot = owner.Groups[1].Value.ToLowerInvariant();
                launch.Measured = true;
                launch.Barrel = true;
                taken.Add((t.parent.parent, launch.Slot));
            }
            foreach (var muzzle in root.GetComponentsInChildren<Transform>(true))
            {
                var match = MuzzlePattern.Match(muzzle.name);
                if (!match.Success || muzzle.parent == null) continue;
                var slot = match.Groups[1].Value.ToLowerInvariant();
                if (slot is "missile" or "rocket" || taken.Contains((muzzle.parent, slot))) continue;
                var at = muzzle.position;
                var forward = muzzle.forward;
                var lines = new List<(Vector3 point, Vector3 axis, float front, float radius)>();
                foreach (Transform sibling in muzzle.parent)
                {
                    if (RecoilPattern.IsMatch(sibling.name)) continue;
                    var filter = sibling.GetComponent<MeshFilter>();
                    if (filter == null || filter.sharedMesh == null || !filter.sharedMesh.isReadable) continue;
                    foreach (var piece in Pieces(filter))
                    {
                        if (!Principal(piece, out var mean, out var axis, out _, out var l1, out var l2, out _) || l1 < 6f * l2) continue;
                        if (Vector3.Dot(axis, forward) < 0f) axis = -axis;
                        if (Vector3.Angle(axis, forward) > 12f) continue;
                        var front = float.MinValue;
                        foreach (var p in piece) front = Mathf.Max(front, Vector3.Dot(p - mean, axis));
                        var d = at - mean;
                        var along = Vector3.Dot(d, axis);
                        var across = (d - axis * along).magnitude;
                        // A barrel beside the muzzle whose tip is level with it.
                        if (across > 0.6f || along < front - 0.25f || along > front + 0.1f) continue;
                        var radius = Mathf.Sqrt(2f * l2);
                        var merged = false;
                        for (var i = 0; i < lines.Count; i++)
                        {
                            var (lp, la, lf, lr) = lines[i];
                            var off = mean - lp;
                            if ((off - la * Vector3.Dot(off, la)).magnitude > Mathf.Max(0.02f, 0.5f * Mathf.Min(radius, lr))) continue;
                            // The same barrel (its brake, a sleeve): the front-most tip, the widest radius.
                            var tip = Vector3.Dot(mean + axis * front - lp, la);
                            lines[i] = (lp, la, Mathf.Max(lf, tip), Mathf.Max(lr, radius));
                            merged = true;
                            break;
                        }
                        if (!merged) lines.Add((mean, axis, front, radius));
                    }
                }
                if (lines.Count < 2) continue;
                // Only when the muzzle is between them, on none of them.
                var centre = Vector3.zero;
                var onOne = false;
                foreach (var (lp, la, _, lr) in lines)
                {
                    var d = at - lp;
                    var across = (d - la * Vector3.Dot(d, la)).magnitude;
                    if (across < Mathf.Max(0.02f, lr)) onOne = true;
                    centre += lp + la * Vector3.Dot(d, la);
                }
                centre /= lines.Count;
                if (onOne || Vector3.Distance(centre, at) > 0.15f) continue;
                lines.Sort((a, b) => a.point.x.CompareTo(b.point.x) != 0 ? a.point.x.CompareTo(b.point.x) : a.point.y.CompareTo(b.point.y));
                for (var i = 0; i < lines.Count; i++)
                {
                    var (lp, la, lf, _) = lines[i];
                    var point = new GameObject($"Launch_{slot}_barrel{i}").transform;
                    point.SetParent(muzzle.parent, false);
                    point.position = lp + la * lf;
                    point.rotation = Quaternion.LookRotation(la, Mathf.Abs(la.y) > 0.95f ? muzzle.forward : Vector3.up);
                    var launch = point.gameObject.AddComponent<LaunchPoint>();
                    launch.Slot = slot;
                    launch.Measured = true;
                    launch.Barrel = true;
                    // Keep the muzzle's own name next to its barrels, for the k-th mount of a slot.
                    point.SetSiblingIndex(muzzle.GetSiblingIndex() + 1);
                }
            }
        }

        /// <summary>A mesh's connected pieces (welded by position), as world-space vertex lists.</summary>
        private static List<List<Vector3>> Pieces(MeshFilter filter)
        {
            var mesh = filter.sharedMesh;
            var vertices = mesh.vertices;
            var triangles = mesh.triangles;
            var parent = new int[vertices.Length];
            for (var i = 0; i < parent.Length; i++) parent[i] = i;
            int Find(int i)
            {
                while (parent[i] != i) i = parent[i] = parent[parent[i]];
                return i;
            }
            void Join(int a, int b)
            {
                a = Find(a);
                b = Find(b);
                if (a != b) parent[a] = b;
            }
            var weld = new Dictionary<Vector3Int, int>();
            for (var i = 0; i < vertices.Length; i++)
            {
                var key = Vector3Int.RoundToInt(vertices[i] * 10000f);
                if (weld.TryGetValue(key, out var first)) Join(i, first);
                else weld[key] = i;
            }
            for (var t = 0; t + 2 < triangles.Length; t += 3)
            {
                Join(triangles[t], triangles[t + 1]);
                Join(triangles[t], triangles[t + 2]);
            }
            var pieces = new Dictionary<int, List<Vector3>>();
            for (var i = 0; i < vertices.Length; i++)
            {
                var r = Find(i);
                if (!pieces.TryGetValue(r, out var list)) pieces[r] = list = new List<Vector3>();
                list.Add(filter.transform.TransformPoint(vertices[i]));
            }
            return new List<List<Vector3>>(pieces.Values);
        }

        /// <summary>Whether a muzzle was turned along its barrel by <see cref="AlignMuzzles"/>.</summary>
        internal static bool Aligned(Transform muzzle) => muzzle != null && muzzle.GetComponent<AlignedMuzzle>() != null;

        private void MergeRigidParts(Transform root)
        {
            var anchors = new HashSet<Transform> { root };
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
                if (IsMovingPart(t)) anchors.Add(t);

            var groups = new Dictionary<Transform, List<MeshFilter>>();
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null || filter.GetComponent<MeshRenderer>() == null) continue;
                var anchor = filter.transform;
                while (!anchors.Contains(anchor)) anchor = anchor.parent;
                if (!groups.TryGetValue(anchor, out var list)) groups[anchor] = list = new List<MeshFilter>();
                list.Add(filter);
            }

            foreach (var (anchor, filters) in groups)
            {
                if (filters.Count < 2) continue;
                var byMaterial = new Dictionary<Material, List<CombineInstance>>();
                var vertices = 0;
                foreach (var filter in filters)
                {
                    var matrix = anchor.worldToLocalMatrix * filter.transform.localToWorldMatrix;
                    var shared = filter.GetComponent<MeshRenderer>().sharedMaterials;
                    vertices += filter.sharedMesh.vertexCount;
                    for (var i = 0; i < filter.sharedMesh.subMeshCount && i < shared.Length; i++)
                    {
                        if (shared[i] == null) continue;
                        if (!byMaterial.TryGetValue(shared[i], out var list)) byMaterial[shared[i]] = list = new List<CombineInstance>();
                        list.Add(new CombineInstance { mesh = filter.sharedMesh, subMeshIndex = i, transform = matrix });
                    }
                }
                var format = vertices > 65000 ? UnityEngine.Rendering.IndexFormat.UInt32 : UnityEngine.Rendering.IndexFormat.UInt16;
                var parts = new List<CombineInstance>();
                var materials = new List<Material>();
                foreach (var (material, list) in byMaterial)
                {
                    var part = new Mesh { indexFormat = format };
                    part.CombineMeshes(list.ToArray(), mergeSubMeshes: true, useMatrices: true);
                    parts.Add(new CombineInstance { mesh = part, transform = Matrix4x4.identity });
                    materials.Add(material);
                }
                var merged = new Mesh { name = $"{root.name} {anchor.name} merged", indexFormat = format };
                merged.CombineMeshes(parts.ToArray(), mergeSubMeshes: false, useMatrices: false);
                foreach (var p in parts) Release(p.mesh);
                _ownedMeshes.Add(merged);

                foreach (var filter in filters)
                {
                    // Immediate: the template is instantiated this very frame.
                    Object.DestroyImmediate(filter.GetComponent<MeshRenderer>());
                    Object.DestroyImmediate(filter);
                }
                var go = new GameObject("Merged");
                go.transform.SetParent(anchor, false);
                go.AddComponent<MeshFilter>().sharedMesh = merged;
                go.AddComponent<MeshRenderer>().sharedMaterials = materials.ToArray();
            }
        }

        /// <summary>
        /// Puts the turret's barrel parts on an elevating pivot at their trunnion (the rear of the
        /// barrel group, low down), so guns, mortars and launchers can be raised to fire. Returns
        /// how far the barrel already points up and what kind it is; no pivot without a turret or
        /// a Muzzle_main to aim along.
        /// </summary>
        private static (float pitch, BarrelKind kind) AddElevation(Transform root, string modelId = null)
        {
            var turret = Find(root, TurretPattern);
            if (turret == null || turret.Find(ElevationName) != null) return (0f, BarrelKind.None);
            if (modelId != null && SideLaunchers.Contains(modelId)) AddSideErector(turret);
            var parts = new List<Transform>();
            Transform muzzle = null;
            var erector = modelId != null && ErectorParts.TryGetValue(modelId, out var extra) ? extra : null;
            foreach (Transform child in turret)
            {
                if (!BarrelPattern.IsMatch(child.name) && (erector == null || !erector.IsMatch(child.name))) continue;
                parts.Add(child);
                if (child.name.StartsWith("Muzzle_main", StringComparison.OrdinalIgnoreCase)) muzzle = child;
            }
            if (muzzle == null) return (0f, BarrelKind.None);
            // A missile muzzle rides with the gun only when its launcher does (an IFV's turret
            // box); a SAM rack of its own beside the gun stays put.
            var launcherRides = parts.Exists(p => Regex.IsMatch(p.name, "^(launcher|tubes|pod|atgm_pod)", RegexOptions.IgnoreCase));
            if (!launcherRides) parts.RemoveAll(p => p.name.StartsWith("Muzzle_missile", StringComparison.OrdinalIgnoreCase));

            Bounds? box = null;
            var kind = BarrelKind.Gun;
            foreach (var part in parts)
            {
                var name = part.name.ToLowerInvariant();
                if (name.StartsWith("mortar_tube")) kind = BarrelKind.Mortar;
                else if (kind == BarrelKind.Gun && (name.StartsWith("tubes") || name.StartsWith("rocket_tubes") || name.StartsWith("pod") ||
                                                    name.StartsWith("launcher")) && !HasCannon(parts)) kind = BarrelKind.Launcher;
                foreach (var filter in part.GetComponentsInChildren<MeshFilter>(true))
                {
                    if (filter.sharedMesh == null) continue;
                    foreach (var corner in Corners(filter.sharedMesh.bounds))
                    {
                        var p = turret.InverseTransformPoint(filter.transform.TransformPoint(corner));
                        if (box == null) box = new Bounds(p, Vector3.zero);
                        else
                        {
                            var b = box.Value;
                            b.Encapsulate(p);
                            box = b;
                        }
                    }
                }
            }
            if (box == null) return (0f, BarrelKind.None);
            var bounds = box.Value;
            // The trunnion: the back of the barrel group, a third of the way up it.
            var pivot = new Vector3(bounds.center.x, bounds.min.y + bounds.size.y * 0.3f, bounds.min.z + bounds.size.z * 0.06f);
            var go = new GameObject(ElevationName);
            go.transform.SetParent(turret, false);
            go.transform.localPosition = pivot;
            foreach (var part in parts) part.SetParent(go.transform, true);
            var aim = turret.InverseTransformPoint(muzzle.position) - pivot;
            // A muzzle turned along its barrel (AlignMuzzles) gives the barrel's own pitch; the line
            // from the trunnion to the muzzle runs several degrees off a tilted tube or box (13E).
            if (Aligned(muzzle)) aim = turret.InverseTransformDirection(muzzle.forward);
            var pitch = Mathf.Atan2(aim.y, Mathf.Max(0.01f, new Vector2(aim.x, aim.z).magnitude)) * Mathf.Rad2Deg;
            return (pitch, kind);
        }

        /// <summary>
        /// Where a model with neither a turret nor a Muzzle_main fires from (a supply truck's
        /// self-defence gun): on its roof towards the front, not out of the middle of its side.
        /// </summary>
        private static Vector3 RoofFront(Transform root)
        {
            var lo = Vector3.positiveInfinity;
            var hi = Vector3.negativeInfinity;
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null) continue;
                var b = filter.sharedMesh.bounds;
                for (var i = 0; i < 8; i++)
                {
                    var corner = b.center + Vector3.Scale(b.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                    var p = root.InverseTransformPoint(filter.transform.TransformPoint(corner));
                    lo = Vector3.Min(lo, p);
                    hi = Vector3.Max(hi, p);
                }
            }
            if (lo.x > hi.x) return new Vector3(0f, 1.5f, 1f);
            return new Vector3((lo.x + hi.x) * 0.5f, hi.y + 0.15f, Mathf.Lerp((lo.z + hi.z) * 0.5f, hi.z, 0.6f));
        }

        private static bool HasCannon(List<Transform> parts)
        {
            foreach (var p in parts)
                if (p.name.StartsWith("Main_cannon", StringComparison.OrdinalIgnoreCase)) return true;
            return false;
        }

        private static void Release(Object o)
        {
            if (o == null) return;
            if (Application.isPlaying) Object.Destroy(o);
            else Object.DestroyImmediate(o);
        }

        /// <summary>A spinner's speed: its pattern's, or a slower one for this model (an EW tower's radar, a drill head).</summary>
        private static float SpinSpeed(string modelId, string resolvedId, string part, float speed)
        {
            if (part.StartsWith("Radar") && (SlowRadars.TryGetValue(resolvedId, out var radar) || SlowRadars.TryGetValue(modelId, out radar))) return radar;
            if (part.StartsWith("Propeller") && (SlowPropellers.TryGetValue(resolvedId, out var prop) || SlowPropellers.TryGetValue(modelId, out prop))) return prop;
            return speed;
        }

        private static bool IsMovingPart(Transform t)
        {
            var name = t.name;
            if (TurretPattern.IsMatch(name) || MountPattern.IsMatch(name) || LoosePattern.IsMatch(name) || PartPattern.IsMatch(name) ||
                DeployPattern.IsMatch(name)) return true;
            if (name == ElevationName && t.parent != null && TurretPattern.IsMatch(t.parent.name)) return true;
            if (RecoilPattern.IsMatch(name) && t.parent != null &&
                (TurretPattern.IsMatch(t.parent.name) || t.parent.name == ElevationName)) return true;
            foreach (var (pattern, _, _) in SpinnerPatterns)
                if (pattern.IsMatch(name)) return true;
            return false;
        }

        private GameObject Prefab(string modelId)
        {
            if (_prefabs.TryGetValue(modelId, out var cached)) return cached;
            var prefab = Resources.Load<GameObject>("Models/" + modelId);
            if (prefab == null && modelId != FallbackModel)
            {
                // Tolerate missing art: warn once and stand in a model we always ship.
                Debug.LogWarning($"[ModelLibrary] Missing model Resources/Models/{modelId}.glb; using {FallbackModel}.");
                prefab = Prefab(FallbackModel);
            }
            if (prefab == null) throw new InvalidOperationException($"Missing model Resources/Models/{modelId}.glb.");
            _prefabs[modelId] = prefab;
            return prefab;
        }

        /// <summary>Front centre of the barrel's bounds (the muzzle brake when there is one).</summary>
        private static Vector3 MuzzleOf(Transform root, List<Transform> recoil)
        {
            Bounds? bounds = null;
            foreach (var part in recoil)
            foreach (var filter in part.GetComponentsInChildren<MeshFilter>())
            {
                var mesh = filter.sharedMesh;
                if (mesh == null) continue;
                foreach (var corner in Corners(mesh.bounds))
                {
                    var p = root.InverseTransformPoint(filter.transform.TransformPoint(corner));
                    if (bounds == null) bounds = new Bounds(p, Vector3.zero);
                    else
                    {
                        var b = bounds.Value;
                        b.Encapsulate(p);
                        bounds = b;
                    }
                }
            }
            if (bounds == null) return new Vector3(0f, 1.5f, 1f);
            var box = bounds.Value;
            return new Vector3(box.center.x, box.center.y, box.max.z);
        }

        private static IEnumerable<Vector3> Corners(Bounds b)
        {
            for (var i = 0; i < 8; i++)
                yield return new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y,
                    (i & 4) == 0 ? b.min.z : b.max.z);
        }

        private static Transform Find(Transform root, Regex name)
        {
            if (name.IsMatch(root.name)) return root;
            foreach (Transform child in root)
            {
                var found = Find(child, name);
                if (found != null) return found;
            }
            return null;
        }
    }
}
