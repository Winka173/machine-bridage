using System;
using System.Collections.Generic;
using System.Diagnostics;
using UnityEngine;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>What a model's far detail level is made of, for the level choice and the impostor atlas.</summary>
    public sealed class ModelLod
    {
        /// <summary>The resolved model id (a high-detail variant keeps its own).</summary>
        public string Id { get; internal set; }

        /// <summary>Triangles and draws (sub-meshes) of the whole model at full and at far detail.</summary>
        public int Triangles0 { get; internal set; }
        public int Triangles1 { get; internal set; }
        public int Draws0 { get; internal set; }
        public int Draws1 { get; internal set; }

        /// <summary>Largest extent of the model (length, span or height) in its own units, before a def's scale.</summary>
        public float Length { get; internal set; }

        /// <summary>The far-detail parts at rest in the model root's space, fast spinners (rotors, propellers) left out: what an impostor shows.</summary>
        public IReadOnlyList<(Mesh mesh, Matrix4x4 local)> BakeParts { get; internal set; } = Array.Empty<(Mesh, Matrix4x4)>();

        /// <summary>Bounds of <see cref="BakeParts"/> in the model root's space.</summary>
        public Bounds BakeBounds { get; internal set; }

        /// <summary>How long building the far detail level took, in milliseconds.</summary>
        public double BuildMilliseconds { get; internal set; }
    }

    /// <summary>
    /// The vehicles' far detail level (LOD1), made from the merged model when it is first needed:
    /// one mesh per moving part (hull, turret, elevating barrel, weapon mounts, rotors, loose
    /// parts; recoiling barrels ride on their mount's), simplified by <see cref="MeshSimplifier"/>
    /// to half a pixel of error at the size it is first shown, and drawn with one material per
    /// army (<see cref="MaterialLibrary.LodSurface"/>). It lives under each part as a "Lod1"
    /// object, inactive until <see cref="Views.VehicleView"/> switches to it.
    /// </summary>
    public sealed partial class ModelLibrary
    {
        /// <summary>Name of the far-detail object under each moving part.</summary>
        public const string LodName = "Lod1";

        /// <summary>Error allowed in the far detail level, in pixels at the size it is first shown (<see cref="VehicleLod.DetailPixels"/>).</summary>
        public const float LodErrorPixels = 0.5f;

        /// <summary>Normals are smoothed across edges flatter than this; sharper edges stay hard.</summary>
        private const float CreaseDegrees = 50f;

        /// <summary>Spinners faster than this are left out of impostors (a still rotor reads as a cross; the view's blur disc stays).</summary>
        private const float FastSpin = 600f;

        private readonly Dictionary<string, ModelLod> _lods = new();

        /// <summary>The far detail level of a model (a resolved id), built into its template on first call; null when it has none.</summary>
        public ModelLod Lod(string modelId)
        {
            var id = ResolveId(modelId);
            EnsureLod(id);
            return _lods.TryGetValue(id, out var lod) ? lod : null;
        }

        private void EnsureLod(string id)
        {
            if (_lods.ContainsKey(id)) return;
            var watch = Stopwatch.StartNew();
            var template = Template(id);
            var lod = BuildLod(template.transform);
            if (lod != null)
            {
                lod.Id = id;
                lod.BuildMilliseconds = watch.Elapsed.TotalMilliseconds;
            }
            _lods[id] = lod;
        }

        private ModelLod BuildLod(Transform root)
        {
            var anchors = new HashSet<Transform> { root };
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
                if (IsMovingPart(t)) anchors.Add(t);

            Transform LodAnchor(Transform t)
            {
                while (!anchors.Contains(t)) t = t.parent;
                // A recoiling barrel is part of its mount far away (the kick is too small to see).
                while (t != root && t.parent != null && (IsMountBarrel(t) || RecoilPattern.IsMatch(t.name) &&
                       (TurretPattern.IsMatch(t.parent.name) || t.parent.name == ElevationName)))
                {
                    t = t.parent;
                    while (!anchors.Contains(t)) t = t.parent;
                }
                return t;
            }

            var groups = new Dictionary<Transform, List<MeshRenderer>>();
            var order = new List<Transform>();
            var lodBox = new Bounds();
            var first = true;
            int triangles0 = 0, draws0 = 0;
            foreach (var renderer in root.GetComponentsInChildren<MeshRenderer>(true))
            {
                var filter = renderer.GetComponent<MeshFilter>();
                if (filter == null || filter.sharedMesh == null || renderer.name == LodName) continue;
                var mesh = filter.sharedMesh;
                draws0 += mesh.subMeshCount;
                for (var s = 0; s < mesh.subMeshCount; s++) triangles0 += (int)(mesh.GetIndexCount(s) / 3);
                var toRoot = root.worldToLocalMatrix * renderer.transform.localToWorldMatrix;
                foreach (var corner in Corners(mesh.bounds))
                {
                    var p = toRoot.MultiplyPoint3x4(corner);
                    if (first) lodBox = new Bounds(p, Vector3.zero);
                    else lodBox.Encapsulate(p);
                    first = false;
                }
                var anchor = LodAnchor(renderer.transform);
                if (!groups.TryGetValue(anchor, out var list))
                {
                    groups[anchor] = list = new List<MeshRenderer>();
                    order.Add(anchor);
                }
                list.Add(renderer);
            }
            if (groups.Count == 0) return null;

            // Tall towers are seen across their height as much as their width.
            var length = Mathf.Max(lodBox.size.x, Mathf.Max(lodBox.size.y, lodBox.size.z));
            var error = LodErrorPixels * length / VehicleLod.DetailPixels;
            var lod = new ModelLod { Triangles0 = triangles0, Draws0 = draws0, Length = length };
            var placeholder = _materials.LodSurface(-1);
            var bake = new List<(Mesh, Matrix4x4)>();
            var bakeBox = new Bounds();
            var bakeFirst = true;
            foreach (var anchor in order)
            {
                // The error is measured in the model's units; the part may be scaled inside it (not a Deploy_ part:
                // the bunker's spoil bank is stored at 1 % and shown full size).
                var scale = DeployPattern.IsMatch(anchor.name) ? 1f : Mathf.Max(1e-4f, anchor.lossyScale.x / Mathf.Max(1e-4f, root.lossyScale.x));
                var mesh = SurfaceMesh($"{root.name} {anchor.name} lod1", anchor, groups[anchor], error / scale);
                if (mesh == null) continue;
                _ownedMeshes.Add(mesh);
                var go = new GameObject(LodName);
                go.transform.SetParent(anchor, false);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                go.AddComponent<MeshRenderer>().sharedMaterial = placeholder;
                go.SetActive(false);
                lod.Triangles1 += (int)(mesh.GetIndexCount(0) / 3);
                lod.Draws1 += 1;
                if (OnFastSpinner(anchor, root)) continue;
                var local = root.worldToLocalMatrix * go.transform.localToWorldMatrix;
                bake.Add((mesh, local));
                foreach (var corner in Corners(mesh.bounds))
                {
                    var p = local.MultiplyPoint3x4(corner);
                    if (bakeFirst) bakeBox = new Bounds(p, Vector3.zero);
                    else bakeBox.Encapsulate(p);
                    bakeFirst = false;
                }
            }
            if (lod.Draws1 == 0) return null;
            lod.BakeParts = bake;
            lod.BakeBounds = bakeBox;
            return lod;
        }

        private static bool OnFastSpinner(Transform t, Transform root)
        {
            for (; t != null && t != root; t = t.parent)
                foreach (var (pattern, _, speed) in SpinnerPatterns)
                    if (speed > FastSpin && pattern.IsMatch(t.name)) return true;
            return false;
        }

        /// <summary>
        /// One part's far-detail mesh: every sub-mesh of its renderers in the part's space, welded,
        /// simplified, with normals rebuilt (hard where the simplified faces meet at a sharp angle)
        /// and each vertex's kit surface as a palette column in its UV. Null when nothing is readable.
        /// </summary>
        private Mesh SurfaceMesh(string name, Transform anchor, List<MeshRenderer> renderers, float error)
        {
            var positions = new List<Vector3>();
            var colours = new List<Vector4>();
            var weld = new Dictionary<long, int>();
            var triangles = new List<int>();
            var surfaces = new List<int>();
            var columns = new List<float>();
            var columnOf = new Dictionary<float, int>();
            var vertices = new List<Vector3>();
            var meshColours = new List<Color>();
            var indices = new List<int>();
            var remap = new List<int>();
            foreach (var renderer in renderers)
            {
                var mesh = renderer.GetComponent<MeshFilter>().sharedMesh;
                if (!mesh.isReadable)
                {
                    UnityEngine.Debug.LogWarning($"[ModelLibrary] {name}: mesh {mesh.name} is not readable; left out of the far detail level.");
                    continue;
                }
                var toAnchor = anchor.worldToLocalMatrix * renderer.transform.localToWorldMatrix;
                mesh.GetVertices(vertices);
                mesh.GetColors(meshColours);
                remap.Clear();
                for (var i = 0; i < vertices.Count; i++)
                {
                    var p = toAnchor.MultiplyPoint3x4(vertices[i]);
                    var key = WeldKey(p);
                    if (!weld.TryGetValue(key, out var v))
                    {
                        v = positions.Count;
                        weld[key] = v;
                        positions.Add(p);
                        colours.Add(Vector4.zero);
                    }
                    var c = i < meshColours.Count ? meshColours[i] : Color.white;
                    colours[v] += new Vector4(c.r, c.g, c.b, 1f);
                    remap.Add(v);
                }
                var materials = renderer.sharedMaterials;
                for (var s = 0; s < mesh.subMeshCount; s++)
                {
                    var u = _materials.PaletteU(s < materials.Length && materials[s] != null ? materials[s].name : string.Empty);
                    if (!columnOf.TryGetValue(u, out var surface))
                    {
                        surface = columns.Count;
                        columnOf[u] = surface;
                        columns.Add(u);
                    }
                    mesh.GetTriangles(indices, s);
                    for (var i = 0; i + 2 < indices.Count; i += 3)
                    {
                        int a = remap[indices[i]], b = remap[indices[i + 1]], c = remap[indices[i + 2]];
                        if (a == b || b == c || a == c) continue;
                        triangles.Add(a);
                        triangles.Add(b);
                        triangles.Add(c);
                        surfaces.Add(surface);
                    }
                }
            }
            if (triangles.Count == 0) return null;
            var (kept, keptSurfaces) = MeshSimplifier.Simplify(positions, triangles.ToArray(), surfaces.ToArray(), error, error * 2f);
            // Every piece was smaller than the error (a part made only of bolts): keep it whole rather than lose it.
            if (kept.Length == 0) (kept, keptSurfaces) = MeshSimplifier.Simplify(positions, triangles.ToArray(), surfaces.ToArray(), error);
            if (kept.Length == 0) return null;
            for (var i = 0; i < colours.Count; i++)
            {
                var c = colours[i];
                colours[i] = c.w > 0f ? new Vector4(c.x / c.w, c.y / c.w, c.z / c.w, 1f) : Vector4.one;
            }
            return Rebuild(name, positions, colours, kept, keptSurfaces, columns);
        }

        /// <summary>A position rounded to a tenth of a millimetre, packed (21 bits an axis: within about 100 m of the part's origin).</summary>
        private static long WeldKey(Vector3 p)
        {
            long Axis(float v) => Math.Clamp(Mathf.RoundToInt(v * 1e4f) + (1 << 20), 0, (1 << 21) - 1);
            return (Axis(p.x) << 42) | (Axis(p.y) << 21) | Axis(p.z);
        }

        /// <summary>
        /// Splits the welded, simplified triangles into render vertices: one per position, surface
        /// and normal, where each corner's normal averages the faces round it that meet its own
        /// within <see cref="CreaseDegrees"/>.
        /// </summary>
        private static Mesh Rebuild(string name, List<Vector3> positions, List<Vector4> colours, int[] triangles, int[] surfaces, List<float> columns)
        {
            var count = triangles.Length / 3;
            var face = new Vector3[count];
            var unit = new Vector3[count];
            for (var t = 0; t < count; t++)
            {
                var a = positions[triangles[3 * t]];
                var n = Vector3.Cross(positions[triangles[3 * t + 1]] - a, positions[triangles[3 * t + 2]] - a);
                face[t] = n;
                unit[t] = n.sqrMagnitude > 1e-20f ? n.normalized : Vector3.up;
            }
            var start = new int[positions.Count + 1];
            foreach (var v in triangles) start[v + 1]++;
            for (var i = 1; i < start.Length; i++) start[i] += start[i - 1];
            var around = new int[triangles.Length];
            var fill = (int[])start.Clone();
            for (var t = 0; t < count; t++)
                for (var k = 0; k < 3; k++)
                    around[fill[triangles[3 * t + k]]++] = t;

            var crease = Mathf.Cos(CreaseDegrees * Mathf.Deg2Rad);
            var outPositions = new List<Vector3>();
            var outNormals = new List<Vector3>();
            var outColours = new List<Color>();
            var outUvs = new List<Vector2>();
            var outIndices = new int[triangles.Length];
            // Render vertices already made for each welded vertex, as a chain through `next`.
            var head = new int[positions.Count];
            for (var i = 0; i < head.Length; i++) head[i] = -1;
            var next = new List<int>();
            var outSurface = new List<int>();
            for (var t = 0; t < count; t++)
                for (var k = 0; k < 3; k++)
                {
                    var v = triangles[3 * t + k];
                    var sum = Vector3.zero;
                    for (var j = start[v]; j < start[v + 1]; j++)
                    {
                        var other = around[j];
                        if (Vector3.Dot(unit[t], unit[other]) >= crease) sum += face[other];
                    }
                    var normal = sum.sqrMagnitude > 1e-20f ? sum.normalized : unit[t];
                    var index = head[v];
                    while (index >= 0 && (outSurface[index] != surfaces[t] || Vector3.Dot(outNormals[index], normal) <= 0.999f)) index = next[index];
                    if (index < 0)
                    {
                        index = outPositions.Count;
                        outPositions.Add(positions[v]);
                        outNormals.Add(normal);
                        var c = colours[v];
                        outColours.Add(new Color(c.x, c.y, c.z, c.w));
                        outUvs.Add(new Vector2(columns[surfaces[t]], 0.5f));
                        outSurface.Add(surfaces[t]);
                        next.Add(head[v]);
                        head[v] = index;
                    }
                    outIndices[3 * t + k] = index;
                }

            var mesh = new Mesh
            {
                name = name,
                indexFormat = outPositions.Count > 65000 ? UnityEngine.Rendering.IndexFormat.UInt32 : UnityEngine.Rendering.IndexFormat.UInt16,
            };
            mesh.SetVertices(outPositions);
            mesh.SetNormals(outNormals);
            mesh.SetColors(outColours);
            mesh.SetUVs(0, outUvs);
            mesh.SetTriangles(outIndices, 0, true);
            // Players only draw it; the editor keeps it readable for the tests.
            if (!Application.isEditor) mesh.UploadMeshData(true);
            return mesh;
        }
    }
}
