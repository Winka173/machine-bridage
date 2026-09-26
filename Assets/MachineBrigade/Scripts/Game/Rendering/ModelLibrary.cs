using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>A spawned model and the parts the game animates.</summary>
    public sealed class ModelInstance
    {
        public ModelInstance(GameObject root, Transform turret, IReadOnlyList<Transform> recoilParts, Vector3 muzzle,
            Renderer[] renderers, IReadOnlyDictionary<string, Transform> muzzles, IReadOnlyDictionary<string, Transform> mounts,
            IReadOnlyList<Spinner> spinners)
        {
            Root = root;
            Turret = turret;
            RecoilParts = recoilParts;
            Muzzle = muzzle;
            Renderers = renderers;
            Muzzles = muzzles;
            Mounts = mounts;
            Spinners = spinners;
        }

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
            (new Regex(@"^Rotor(\.\d+)?$"), Vector3.up, 1500f),
            (new Regex(@"^Tail_rotor(\.\d+)?$"), Vector3.right, 2400f),
            (new Regex(@"^Radar(\.\d+)?$"), Vector3.up, 120f),
        };

        private readonly MaterialLibrary _materials;
        private readonly Dictionary<string, GameObject> _prefabs = new();
        private readonly Dictionary<string, ChunkModel> _merged = new();

        public ModelLibrary(MaterialLibrary materials) => _materials = materials;

        public ModelInstance Spawn(string modelId, int team, Transform parent, bool castShadows = true)
        {
            var root = Object.Instantiate(Prefab(modelId), parent, false);
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
            if (turret != null)
            {
                foreach (Transform child in turret)
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
            return new ModelInstance(root, turret, recoil, muzzle, renderers, muzzles, mounts, spinners);
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

        private GameObject Prefab(string modelId)
        {
            if (_prefabs.TryGetValue(modelId, out var cached)) return cached;
            var prefab = Resources.Load<GameObject>("Models/" + modelId);
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
