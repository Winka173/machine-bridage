using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Tower-branch art (tower-branch prompt C). A tower's rank-7 branch is drawn with its own model and
    /// shown with its own icon: <c>&lt;tower model&gt;_a</c> / <c>_b</c> and <c>&lt;tower icon&gt;_a</c> / <c>_b</c>, the
    /// letter being the branch's place among its tower's branch defs in balance.json (A first, the
    /// spec's order). A branch entry that names its own <c>"model"</c> keeps it, so the data can choose
    /// any model for any branch; the table is in DECISIONS 19U. Below rank 7 a tower shows its card's
    /// rank (<see cref="TowerRankDetails"/>): bars on its body, add-on plates from rank 3, thicker from 5.
    /// </summary>
    public static class TowerArt
    {
        /// <summary>Plates from this rank, thicker ones (and a second layer) from <see cref="HeavyPlateRank"/>.</summary>
        public const int PlateRank = 3;

        public const int HeavyPlateRank = 5;

        /// <summary>The most rank bars a tower wears (rank 6; a branch keeps them).</summary>
        public const int MaxBars = 6;

        /// <summary>Branch def id -> (its tower's model, its letter), from the last catalog learned.</summary>
        private static readonly Dictionary<string, (string model, char letter)> Branches = new();

        /// <summary>Card rank of a tower card for a side (team, card id); set by the match. Null: rank 1.</summary>
        public static Func<int, string, int> Ranks { get; set; }

        /// <summary>Low graphics: rank details without bolts or the second plate layer.</summary>
        public static bool Lean { get; set; }

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            Ranks = null;
            Lean = false;
        }

        /// <summary>Learns every tower's branches from a catalog: each branch's letter is its data order.</summary>
        public static void Learn(Catalog catalog)
        {
            Branches.Clear();
            var seen = new HashSet<string>();
            foreach (var def in catalog.Vehicles.Values)
            {
                if (def.BranchOf == null || !seen.Add(def.BranchOf) || !catalog.Vehicles.TryGetValue(def.BranchOf, out var tower)) continue;
                var list = TowerCards.Branches(catalog, def.BranchOf);
                for (var i = 0; i < list.Count && i < 26; i++) Branches[list[i]] = (tower.Model, (char)('a' + i));
            }
        }

        /// <summary>The branch's letter (a, b), or null when the id is not a learned branch.</summary>
        public static char? Letter(string branchId) =>
            branchId != null && Branches.TryGetValue(branchId, out var b) ? b.letter : null;

        /// <summary>The branch model id a branch would wear by its letter (gun_turret_a), whether it ships or not.</summary>
        public static string BranchModel(string branchId) =>
            branchId != null && Branches.TryGetValue(branchId, out var b) ? b.model + "_" + b.letter : null;

        /// <summary>
        /// The model a def is drawn with: a branch that names no model of its own wears its letter's model
        /// when that ships (<paramref name="ships"/>, e.g. ModelLibrary.Has); everything else its own.
        /// </summary>
        public static string ModelFor(VehicleDef def, Func<string, bool> ships)
        {
            if (def == null) return null;
            if (def.BranchOf == null || !Branches.TryGetValue(def.Id, out var b) || def.Model != b.model) return def.Model;
            var id = b.model + "_" + b.letter;
            return ships == null || ships(id) ? id : def.Model;
        }

        /// <summary>The branch's icon by its letter (t_gun_a) when it exists (<paramref name="exists"/>), else null.</summary>
        public static string BranchIcon(string branchId, string towerIcon, Func<string, bool> exists)
        {
            if (towerIcon == null || Letter(branchId) is not { } letter) return null;
            var icon = towerIcon + "_" + letter;
            return exists == null || exists(icon) ? icon : null;
        }

        /// <summary>The rank a tower shows: its card's (1 without a provider); a branch is rank 7 at least.</summary>
        public static int RankOf(int team, VehicleDef def)
        {
            var rank = Mathf.Max(1, Ranks?.Invoke(team, def.CardId) ?? 1);
            return def.BranchOf != null ? Mathf.Max(rank, TowerCards.BranchRank) : rank;
        }

        /// <summary>A tower (not a utility module, the HQ or a wall) wears rank details.</summary>
        public static bool WearsRank(VehicleDef def) => def.Fort is { Kind: FortKind.Tower } && TowerCards.IsLoadoutTower(def.CardId);
    }

    /// <summary>
    /// A tower's rank details (tower-branch prompt C.2), one mesh with two materials (Armor plates,
    /// Hazard bars) laid on the tower's static body: rays from four sides find its walls (never the
    /// turret or anything else that moves), rank bars stack on the side walls (one a rank, up to six)
    /// and from rank 3 add-on plates stand on the four diagonals, thicker from rank 5 with a second
    /// layer and bolts (not on Low graphics). A model whose body is too low or too thin for them wears
    /// the bars on a marker post at its corner. Meshes are cached per model, rank and leanness.
    /// </summary>
    public static class TowerRankDetails
    {
        private readonly struct Anchor
        {
            public Anchor(Vector3 point, Vector3 normal, float width)
            {
                Point = point;
                Normal = normal;
                Width = width;
            }

            public Vector3 Point { get; }
            public Vector3 Normal { get; }
            public float Width { get; }
        }

        private sealed class Layout
        {
            public readonly List<Anchor> Bars = new();
            public readonly List<Anchor> Plates = new();
            public Vector3 Post;
        }

        private static readonly Dictionary<string, Layout> Layouts = new();
        private static readonly Dictionary<(string, int, bool), Mesh> Meshes = new();

        /// <summary>Surface colour baked into the vertices, as the Blender kit bakes its shading (top, foot).</summary>
        private static readonly Color Lit = new(.66f, .66f, .66f, 1f), Foot = new(.46f, .46f, .46f, 1f);

        private static readonly System.Text.RegularExpressions.Regex Moving = new(
            @"^(Turret|Radar|Rotor|Searchlight|Mount_|Emitter|Elevation|Erector|Lift)", System.Text.RegularExpressions.RegexOptions.IgnoreCase);

        /// <summary>The number of bars and plate tier a rank shows: (bars, 0 none / 1 plates / 2 heavy plates).</summary>
        public static (int bars, int plates) Tier(int rank) =>
            (Mathf.Clamp(rank, 1, TowerArt.MaxBars), rank >= TowerArt.HeavyPlateRank ? 2 : rank >= TowerArt.PlateRank ? 1 : 0);

        /// <summary>The details mesh (sub-mesh 0 Armor, 1 Hazard) for a model at a rank; null when the model is missing.</summary>
        public static Mesh For(string modelId, int rank, bool lean)
        {
            var (bars, plates) = Tier(rank);
            var key = (modelId, bars * 3 + plates, lean);
            if (Meshes.TryGetValue(key, out var cached)) return cached;
            var layout = LayoutOf(modelId);
            var mesh = layout == null ? null : Build(layout, bars, plates, lean);
            if (mesh != null) mesh.name = $"RankDetails {modelId} {bars}/{plates}{(lean ? " lean" : "")}";
            Meshes[key] = mesh;
            return mesh;
        }

        /// <summary>Adds the details under a spawned model; returns their renderer (null when there are none).</summary>
        public static MeshRenderer Attach(Transform modelRoot, string modelId, int rank, int team, MaterialLibrary materials)
        {
            var mesh = For(modelId, rank, TowerArt.Lean);
            if (mesh == null) return null;
            var go = new GameObject("RankDetails");
            go.transform.SetParent(modelRoot, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterials = new[] { materials.ForModel("Armor", team), materials.ForModel("Hazard", team) };
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            return renderer;
        }

        // ------------------------------------------------------------------ measuring

        private static Layout LayoutOf(string modelId)
        {
            if (Layouts.TryGetValue(modelId, out var known)) return known;
            var prefab = Resources.Load<GameObject>("Models/" + modelId);
            Layout layout = null;
            if (prefab != null)
            {
                var tris = new List<Vector3>();
                Collect(prefab.transform, prefab.transform, tris);
                layout = tris.Count >= 3 ? Measure(tris) : null;
            }
            Layouts[modelId] = layout;
            return layout;
        }

        /// <summary>The triangles of every static part in the model root's space (moving parts left out).</summary>
        private static void Collect(Transform root, Transform t, List<Vector3> tris)
        {
            if (t != root && Moving.IsMatch(t.name)) return;
            var filter = t.GetComponent<MeshFilter>();
            var mesh = filter != null ? filter.sharedMesh : null;
            if (mesh != null && mesh.isReadable)
            {
                var toRoot = root.worldToLocalMatrix * t.localToWorldMatrix;
                var verts = mesh.vertices;
                for (var s = 0; s < mesh.subMeshCount; s++)
                {
                    var idx = mesh.GetTriangles(s);
                    for (var i = 0; i + 2 < idx.Length; i += 3)
                    {
                        tris.Add(toRoot.MultiplyPoint3x4(verts[idx[i]]));
                        tris.Add(toRoot.MultiplyPoint3x4(verts[idx[i + 1]]));
                        tris.Add(toRoot.MultiplyPoint3x4(verts[idx[i + 2]]));
                    }
                }
            }
            foreach (Transform child in t) Collect(root, child, tris);
        }

        private static Layout Measure(List<Vector3> tris)
        {
            var min = tris[0];
            var max = tris[0];
            foreach (var p in tris)
            {
                min = Vector3.Min(min, p);
                max = Vector3.Max(max, p);
            }
            var centre = new Vector3((min.x + max.x) * 0.5f, 0f, (min.z + max.z) * 0.5f);
            var reach = Mathf.Max(max.x - min.x, max.z - min.z) + 2f;
            var layout = new Layout { Post = new Vector3(max.x - 0.25f, 0f, min.z + 0.25f) };
            // Bars on the side walls at a comfortable height; plates lower, on the diagonals.
            var height = max.y;
            var barHeights = new[] { 1.1f, 0.8f, 1.5f, 2.0f, 0.55f };
            var plateHeights = new[] { 0.5f, 0.75f, 0.35f, 1.0f };
            for (var k = 0; k < 4; k++)
            {
                var yaw = k * 90f;
                var dir = Quaternion.Euler(0f, yaw, 0f) * Vector3.forward;
                if (Find(tris, centre, dir, reach, barHeights, height, 0.28f, Vector3.zero, out var bar)) layout.Bars.Add(bar);
                // A plate a quadrant: on the diagonal (a round or chamfered body), else beside the bars on the wall.
                var diag = Quaternion.Euler(0f, yaw + 45f, 0f) * Vector3.forward;
                var beside = Vector3.Cross(Vector3.up, dir) * 0.8f;
                if (Find(tris, centre, diag, reach, plateHeights, height, 0.42f, Vector3.zero, out var plate) ||
                    Find(tris, centre, dir, reach, plateHeights, height, 0.42f, beside, out plate)) layout.Plates.Add(plate);
            }
            return layout;
        }

        /// <summary>
        /// A wall facing <paramref name="dir"/>: the first height where a ray from outside hits a near-upright
        /// surface and two rays <paramref name="half"/> to either side hit it within a few centimetres (a
        /// real wall, not a railing or a leg).
        /// </summary>
        private static bool Find(List<Vector3> tris, Vector3 centre, Vector3 dir, float reach, float[] heights, float top, float half,
            Vector3 shift, out Anchor anchor)
        {
            var side = Vector3.Cross(Vector3.up, dir).normalized;
            foreach (var h in heights)
            {
                if (h > top - 0.2f) continue;
                var origin = centre + shift + dir * reach + Vector3.up * h;
                if (!Cast(tris, origin, -dir, out var t, out var normal) || Mathf.Abs(normal.y) > 0.5f) continue;
                if (!Cast(tris, origin + side * half, -dir, out var tl, out _) || Mathf.Abs(tl - t) > 0.12f) continue;
                if (!Cast(tris, origin - side * half, -dir, out var tr, out _) || Mathf.Abs(tr - t) > 0.12f) continue;
                var flat = new Vector3(normal.x, 0f, normal.z);
                if (flat.sqrMagnitude < 1e-4f || Vector3.Dot(flat, dir) < 0.3f) flat = dir;
                anchor = new Anchor(origin - dir * Mathf.Min(t, Mathf.Min(tl, tr)), flat.normalized, half * 2f);
                return true;
            }
            anchor = default;
            return false;
        }

        /// <summary>The nearest hit of a ray on the triangles (Möller-Trumbore, both faces).</summary>
        private static bool Cast(List<Vector3> tris, Vector3 origin, Vector3 dir, out float best, out Vector3 normal)
        {
            best = float.MaxValue;
            normal = Vector3.zero;
            for (var i = 0; i + 2 < tris.Count; i += 3)
            {
                Vector3 a = tris[i], e1 = tris[i + 1] - a, e2 = tris[i + 2] - a;
                var p = Vector3.Cross(dir, e2);
                var det = Vector3.Dot(e1, p);
                if (Mathf.Abs(det) < 1e-8f) continue;
                var inv = 1f / det;
                var s = origin - a;
                var u = Vector3.Dot(s, p) * inv;
                if (u < 0f || u > 1f) continue;
                var q = Vector3.Cross(s, e1);
                var v = Vector3.Dot(dir, q) * inv;
                if (v < 0f || u + v > 1f) continue;
                var t = Vector3.Dot(e2, q) * inv;
                if (t <= 0f || t >= best) continue;
                best = t;
                normal = Vector3.Cross(e1, e2).normalized;
                if (Vector3.Dot(normal, dir) > 0f) normal = -normal;
            }
            return best < float.MaxValue;
        }

        // ------------------------------------------------------------------ building

        private static Mesh Build(Layout layout, int bars, int plates, bool lean)
        {
            var verts = new List<Vector3>();
            var norms = new List<Vector3>();
            var cols = new List<Color>();
            var armor = new List<int>();
            var hazard = new List<int>();
            if (layout.Bars.Count > 0)
                foreach (var anchor in layout.Bars) Stack(anchor, bars, verts, norms, cols, hazard);
            else
            {
                // A low or open model (a minefield, wire): a marker post at its corner carries the bars.
                var post = layout.Post;
                Box(post + Vector3.up * 0.7f, Quaternion.identity, new Vector3(0.1f, 1.4f, 0.1f), verts, norms, cols, armor);
                for (var k = 0; k < 2; k++)
                {
                    var n = k == 0 ? Vector3.back : Vector3.right;
                    Stack(new Anchor(post + Vector3.up * 1.0f + n * 0.05f, n, 0.3f), bars, verts, norms, cols, hazard);
                }
            }
            if (plates > 0)
                foreach (var anchor in layout.Plates)
                {
                    var heavy = plates > 1;
                    var width = Mathf.Min(anchor.Width + 0.35f, heavy ? 1.2f : 1.0f);
                    var thick = heavy ? 0.16f : 0.07f;
                    var h = heavy ? 0.66f : 0.5f;
                    var rot = Quaternion.LookRotation(anchor.Normal, Vector3.up);
                    var centre = anchor.Point + anchor.Normal * (thick * 0.5f + 0.012f);
                    centre.y = Mathf.Max(centre.y, h * 0.5f + 0.05f);
                    Box(centre, rot, new Vector3(width, h, thick), verts, norms, cols, armor);
                    if (!heavy || lean) continue;
                    var outer = centre + anchor.Normal * (thick * 0.5f + 0.03f);
                    Box(outer, rot, new Vector3(width * 0.72f, h * 0.62f, 0.06f), verts, norms, cols, armor);
                    var right = rot * Vector3.right;
                    for (var i = -1; i <= 1; i += 2)
                    for (var j = -1; j <= 1; j += 2)
                        Box(outer + right * (i * width * 0.28f) + Vector3.up * (j * h * 0.2f) + anchor.Normal * 0.04f, rot,
                            new Vector3(0.06f, 0.06f, 0.04f), verts, norms, cols, hazard);
                }
            if (verts.Count == 0) return null;
            var mesh = new Mesh();
            mesh.SetVertices(verts);
            mesh.SetNormals(norms);
            mesh.SetColors(cols);
            var uv = new Vector2[verts.Count];
            for (var i = 0; i < uv.Length; i++) uv[i] = new Vector2(verts[i].x + verts[i].z, verts[i].y);
            mesh.uv = uv;
            mesh.subMeshCount = 2;
            mesh.SetTriangles(armor, 0);
            mesh.SetTriangles(hazard, 1);
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>A rank's bars stacked up the wall at the anchor, each a raised strip in the anchor's facing.</summary>
        private static void Stack(Anchor anchor, int bars, List<Vector3> verts, List<Vector3> norms, List<Color> cols, List<int> tris)
        {
            var rot = Quaternion.LookRotation(anchor.Normal, Vector3.up);
            const float pitch = 0.11f, tall = 0.07f, deep = 0.035f;
            var width = Mathf.Min(0.46f, anchor.Width);
            var bottom = anchor.Point.y - (bars - 1) * pitch * 0.5f;
            for (var i = 0; i < bars; i++)
            {
                var c = new Vector3(anchor.Point.x, bottom + i * pitch, anchor.Point.z) + anchor.Normal * (deep * 0.5f + 0.012f);
                Box(c, rot, new Vector3(width, tall, deep), verts, norms, cols, tris);
            }
        }

        private static readonly int[] Faces = { 0, 1, 2, 0, 2, 3 };

        /// <summary>A box of six flat faces (own normals), shaded darker at its foot.</summary>
        private static void Box(Vector3 c, Quaternion rot, Vector3 size, List<Vector3> verts, List<Vector3> norms, List<Color> cols, List<int> tris)
        {
            var h = size * 0.5f;
            for (var f = 0; f < 6; f++)
            {
                var axis = f / 2;
                var sign = f % 2 == 0 ? 1f : -1f;
                var n = Vector3.zero;
                n[axis] = sign;
                var u = Vector3.zero;
                u[(axis + 1) % 3] = 1f;
                var v = Vector3.Cross(n, u);
                var start = verts.Count;
                for (var k = 0; k < 4; k++)
                {
                    var su = k is 0 or 3 ? -1f : 1f;
                    var sv = k < 2 ? -1f : 1f;
                    var local = Vector3.Scale(n * 1f + u * su + v * sv, h);
                    var p = c + rot * local;
                    verts.Add(p);
                    norms.Add(rot * n);
                    cols.Add(Color.Lerp(Foot, Lit, Mathf.Clamp01(0.5f + local.y / Mathf.Max(0.01f, size.y))));
                }
                foreach (var i in Faces) tris.Add(start + i);
            }
        }

        /// <summary>Forgets cached layouts and meshes (tests, model rebuilds).</summary>
        public static void Clear()
        {
            foreach (var mesh in Meshes.Values)
                if (mesh != null) Object.DestroyImmediate(mesh);
            Meshes.Clear();
            Layouts.Clear();
        }
    }
}
