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

        /// <summary>`Muzzle_&lt;slot&gt;` empties by lower-case slot name (main, coax, mg, missile, rocket, gun).</summary>
        public IReadOnlyDictionary<string, Transform> Muzzles { get; }

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

        public Renderer[] Renderers { get; }
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
    public sealed class ModelLibrary
    {
        private static readonly Regex RecoilPattern = new("^(main_cannon|muzzle_brake)", RegexOptions.IgnoreCase);

        /// <summary>Blender may suffix duplicate names (Turret.001); accept those too.</summary>
        private static readonly Regex TurretPattern = new(@"^Turret(\.\d+)?$");

        private static readonly Regex MuzzlePattern = new(@"^Muzzle_(main|coax|mg|missile|rocket|gun)(\.\d+)?$", RegexOptions.IgnoreCase);
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
        private static readonly Regex LoosePattern = new(@"^(Bombs|Pump_beam|Erector|Searchlight)(\.\d+)?$");

        /// <summary>
        /// Turret parts that elevate with the gun: barrels, muzzle brakes, mortar tubes, rocket and
        /// missile boxes, and the muzzle empties on them. Frames and carriages stay put.
        /// </summary>
        private static readonly Regex BarrelPattern = new(
            @"^(main_cannon|muzzle_brake|mortar_tube|rocket_tubes|tubes|tube_bores|pod(?!_frame)|atgm_pod|launcher|coax|muzzle_main|muzzle_coax|muzzle_missile|muzzle_rocket)\w*(\.\d+)?$",
            RegexOptions.IgnoreCase);

        private const string ElevationName = "Elevation";

        private readonly Dictionary<string, (float pitch, BarrelKind kind)> _elevations = new();

        private readonly MaterialLibrary _materials;
        private readonly Dictionary<string, GameObject> _prefabs = new();
        private readonly Dictionary<string, ChunkModel> _merged = new();
        private readonly Dictionary<string, GameObject> _templates = new();
        private readonly List<Mesh> _ownedMeshes = new();
        private Transform _templateRoot;

        private const string FallbackModel = "light_tank";

        public ModelLibrary(MaterialLibrary materials) => _materials = materials;

        public ModelInstance Spawn(string modelId, int team, Transform parent, bool castShadows = true)
        {
            var root = Object.Instantiate(Template(modelId), parent, false);
            root.name = modelId;
            var renderers = root.GetComponentsInChildren<Renderer>(true);
            foreach (var renderer in renderers)
            {
                var materials = renderer.sharedMaterials;
                for (var i = 0; i < materials.Length; i++)
                    materials[i] = _materials.ForModel(materials[i] != null ? materials[i].name : string.Empty, team);
                renderer.sharedMaterials = materials;
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
            var spinners = new List<Spinner>();
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                var m = MuzzlePattern.Match(t.name);
                if (m.Success) muzzles[m.Groups[1].Value.ToLowerInvariant()] = t;
                var mount = MountPattern.Match(t.name);
                if (mount.Success) mounts[mount.Groups[1].Value.ToLowerInvariant()] = t;
                foreach (var (name, axis, speed) in SpinnerPatterns)
                    if (name.IsMatch(t.name)) spinners.Add(new Spinner(t, axis, speed));
            }
            if (muzzles.TryGetValue("main", out var main)) muzzle = root.transform.InverseTransformPoint(main.position);
            _elevations.TryGetValue(modelId, out var raise);
            return new ModelInstance(root, turret, recoil, muzzle, renderers, muzzles, mounts, spinners, elevation,
                raise.pitch, elevation != null ? raise.kind : BarrelKind.None);
        }

        /// <summary>
        /// Every mesh of a model with its transform relative to the model root and its resolved
        /// materials, for merging many static copies into a few big meshes.
        /// </summary>
        public IEnumerable<(Mesh mesh, Matrix4x4 local, Material[] materials)> Parts(string modelId, int team = -1)
        {
            var root = Prefab(modelId).transform;
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
            var filter = Prefab(modelId).GetComponentInChildren<MeshFilter>(true);
            var renderer = filter != null ? filter.GetComponent<MeshRenderer>() : null;
            if (filter == null || renderer == null) throw new InvalidOperationException($"Model '{modelId}' has no mesh.");
            var materials = renderer.sharedMaterials;
            var resolved = new Material[materials.Length];
            for (var i = 0; i < materials.Length; i++)
                resolved[i] = _materials.ForModel(materials[i] != null ? materials[i].name : string.Empty, -1);
            return new ChunkModel(filter.sharedMesh, resolved);
        }

        /// <summary>Builds a model's merged template now rather than on its first spawn mid-battle.</summary>
        public void Prewarm(string modelId) => Template(modelId);

        /// <summary>Whether a model exists in Resources/Models.</summary>
        public bool Has(string modelId) => _prefabs.ContainsKey(modelId) || Resources.Load<GameObject>("Models/" + modelId) != null;

        /// <summary>
        /// The whole model baked into one mesh (one sub-mesh per material), for small pooled
        /// objects such as missiles and bombs. Cached; the caller must not destroy it.
        /// </summary>
        public ChunkModel Merged(string modelId)
        {
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
        /// A copy of the model with its rigid parts merged: every mesh is combined into one per
        /// part that moves on its own (the hull, the turret, each recoiling barrel, weapon mount,
        /// rotor and propeller). A tank drops from about twenty renderers to four or five, which
        /// cuts draw calls in the camera and the shadow pass alike. Built once per model.
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
            var raise = AddElevation(template.transform);
            if (raise.kind != BarrelKind.None) _elevations[modelId] = raise;
            MergeRigidParts(template.transform);
            _templates[modelId] = template;
            return template;
        }

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
        private static (float pitch, BarrelKind kind) AddElevation(Transform root)
        {
            var turret = Find(root, TurretPattern);
            if (turret == null || turret.Find(ElevationName) != null) return (0f, BarrelKind.None);
            var parts = new List<Transform>();
            Transform muzzle = null;
            foreach (Transform child in turret)
            {
                if (!BarrelPattern.IsMatch(child.name)) continue;
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
            var pitch = Mathf.Atan2(aim.y, Mathf.Max(0.01f, new Vector2(aim.x, aim.z).magnitude)) * Mathf.Rad2Deg;
            return (pitch, kind);
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

        private static bool IsMovingPart(Transform t)
        {
            var name = t.name;
            if (TurretPattern.IsMatch(name) || MountPattern.IsMatch(name) || LoosePattern.IsMatch(name)) return true;
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
