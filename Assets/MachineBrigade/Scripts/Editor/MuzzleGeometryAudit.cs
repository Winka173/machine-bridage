using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using UnityEditor;
using UnityEngine;
using Object = UnityEngine.Object;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Where every weapon's rounds leave from, checked against the model's own geometry (DECISIONS 13E).
    /// Each armed vehicle, elite, boss and tower is spawned through the game's own path (ViewRegistry,
    /// ModelLibrary's merged template, VehicleView's slot mapping) and posed as drawn. For every weapon
    /// mount, the points <see cref="VehicleView.MuzzleOf"/> hands out (each pod, rail, barrel of a twin,
    /// spots on a face of tubes) are measured against the barrel, tube or pod they sit on: the model's
    /// triangles (the imported glTF meshes, per part, on the spawned model's posed transforms) in the
    /// muzzle's own moving group (its turret, weapon mount or boss part; the whole model for a hull or
    /// aircraft gun). Along the drawn barrel's line, eight rays out sideways at each point tell whether
    /// the line runs inside the barrel there; the open end is where that stops. From the same rays:
    /// how far the line is off the barrel's middle, and the barrel's own axis (its middle at the tip
    /// and further back) against the line the flash is drawn along (<see cref="VehicleView.DrawnBarrelOf"/>).
    /// Batch mode: -executeMethod MachineBrigade.Editor.MuzzleGeometryAudit.Report [-mbAuditOut &lt;md&gt;]
    /// [-mbAuditIds a+b] writes Docs/muzzle-audit.md; MuzzleAuditTests asserts every mount passes.
    /// </summary>
    public static class MuzzleGeometryAudit
    {
        /// <summary>A muzzle may sit this far inside its barrel's open end, or this far ahead of it (drawn metres).</summary>
        public const float Inside = 0.08f, Ahead = 0.15f;

        /// <summary>Off a single barrel's middle: this much, or half its radius if more (drawn metres).</summary>
        public const float Across = 0.05f;

        /// <summary>The flash's line against the barrel's own axis (degrees).</summary>
        public const float Angle = 6f;

        /// <summary>How far out sideways a barrel, tube or box wall is looked for (drawn metres).</summary>
        private const float Reach = 2.6f;

        /// <summary>How far behind and ahead of the muzzle its barrel's open end is looked for (drawn metres).</summary>
        private const float Back = 1.6f, Forward = 1.6f;

        public sealed class Finding
        {
            public string Vehicle, Model, Slot, Weapon, Kind, Node = "", Part = "", Verdict = "OK", Note = "";
            public int Mount, Points;

            /// <summary>Worst over the mount's points: + ahead of the open end, - inside it (drawn metres; NaN: no barrel found).</summary>
            public float AheadOfTip;

            /// <summary>Worst off the barrel's middle at its tip (drawn metres; not judged on a face of tubes).</summary>
            public float OffAxis;

            public float Radius, AxisAngle;
            public bool Face;

            /// <summary>Each point it fires from and the open end found for it (world), for the render.</summary>
            public readonly List<(Vector3 muzzle, Vector3 tip)> Marks = new();

            public bool Ok => Verdict is "OK" or "n/a";
        }

        private sealed class Part
        {
            public string Name;
            public Transform Node;
            public Vector3[] Tri;
            public Bounds Box;
        }

        private readonly struct Tri
        {
            public Tri(Vector3 a, Vector3 b, Vector3 c, string part)
            {
                A = a;
                E1 = b - a;
                E2 = c - a;
                Part = part;
            }

            public readonly Vector3 A, E1, E2;
            public readonly string Part;
        }

        /// <summary>Every mount of every armed vehicle in the catalogue (or of <paramref name="only"/>).</summary>
        public static List<Finding> Run(Catalog catalog, ICollection<string> only = null, bool highDetail = false, Action<VehicleView, List<Finding>> seen = null)
        {
            var findings = new List<Finding>();
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var wasHigh = ModelLibrary.HighDetail;
            ModelLibrary.HighDetail = highDetail;
            var models = new ModelLibrary(materials);
            var root = new GameObject("Muzzle Geometry Audit").transform;
            var state = UnityEngine.Random.state;
            try
            {
                foreach (var def in catalog.Vehicles.Values.OrderBy(d => d.Id, StringComparer.Ordinal))
                {
                    if (only != null && !only.Contains(def.Id)) continue;
                    if (!def.Mounts.Any(Armed)) continue;
                    if (highDetail && models.ResolveId(def.Model) == def.Model) continue;
                    findings.AddRange(Vehicle(catalog, models, meshes, materials, root, def, seen));
                }
            }
            finally
            {
                UnityEngine.Random.state = state;
                Object.DestroyImmediate(root.gameObject);
                models.Dispose();
                materials.Dispose();
                ModelLibrary.HighDetail = wasHigh;
            }
            return findings;
        }

        /// <summary>A mount that fires something (not a blade, a detonator or an empty slot).</summary>
        public static bool Armed(WeaponMount m) => !m.Weapon.Melee && m.Weapon.Id is not ("none" or "detonator") && m.Weapon.Damage > 0f;

        private static List<Finding> Vehicle(Catalog catalog, ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials, Transform root,
            VehicleDef def, Action<VehicleView, List<Finding>> seen)
        {
            var holder = new GameObject(def.Id).transform;
            holder.SetParent(root, false);
            var found = new List<Finding>();
            try
            {
                var map = new MapDefinition("audit", 200f,
                    new[] { new TeamStart(0, new Vector2(0f, -80f)), new TeamStart(1, new Vector2(0f, 80f)) },
                    new List<PropPlacement>(), new List<UnitPlacement>());
                var world = new SimWorld(catalog, map, seed: 5);
                var views = new ViewRegistry(models, meshes, materials, holder, 0);
                var view = views.Add(world.SpawnVehicle(def.Id, 0, Vector2.Zero, 0f));
                views.SnapshotAll();
                views.SnapshotAll();
                views.Render(1f, Quaternion.identity);
                // As a shot does: the main gun is laid first (its idle angle here), then its muzzle read.
                // (Aircraft too, so a flying boss's raised barrels do not depend on the frame time.)
                view.LayForShot();
                var parts = Geometry(models, view);
                var modelRoot = view.Model.Root.transform;
                var mainNodes = new HashSet<Transform>();
                for (var i = 0; i < def.Mounts.Count; i++)
                {
                    var mount = def.Mounts[i];
                    var f = new Finding
                    {
                        Vehicle = def.Id, Model = models.ResolveId(def.Model), Mount = i, Slot = mount.Slot, Weapon = mount.Weapon.Id,
                        Kind = mount.Weapon.Beam ? "Beam" : mount.Weapon.Charge > 0f ? "Rail" : mount.Weapon.Projectile.ToString(),
                    };
                    found.Add(f);
                    if (!Armed(mount))
                    {
                        f.Verdict = "n/a";
                        f.Note = "does not fire";
                        continue;
                    }
                    Measure(view, i, parts, modelRoot, f, mainNodes);
                }
                seen?.Invoke(view, found);
            }
            finally
            {
                Object.DestroyImmediate(holder.gameObject);
            }
            return found;
        }

        private static void Measure(VehicleView view, int index, List<Part> parts, Transform modelRoot, Finding f, HashSet<Transform> mainNodes)
        {
            var def = view.Def;
            var mount = def.Mounts[index];
            // The points it fires from, as the game hands them out: each pod or rail in turn, a
            // twin gun's barrels in turn (the main gun recoils first, as a shot does), spots on a face of tubes.
            UnityEngine.Random.InitState(17 + index);
            var points = new List<(Vector3 at, Transform node)>();
            var tries = view.Model.Launchers.Values.Sum(l => l.Count) * 2 + 4;
            for (var k = 0; k < tries; k++)
            {
                if (index == 0) view.Recoil();
                var at = view.MuzzleOf(index);
                var node = view.LastMuzzleNode;
                if (!points.Any(p => (p.at - at).sqrMagnitude < 1e-4f)) points.Add((at, node));
            }
            var nodes = points.Select(p => p.node).Distinct().ToList();
            var names = nodes.Select(n => n == null ? "(none)" : n.name).Distinct().ToList();
            f.Node = string.Join(" ", names.Take(4)) + (names.Count > 4 ? $" (+{names.Count - 4})" : "");
            f.Points = points.Count;
            f.Face = nodes.Any(IsSpread);
            var direction = view.DrawnBarrelOf(index).normalized;
            // A side gun (an AC-130's, a door gunner's) is drawn along the side it aims out of; parked
            // here, the simulation still has it facing the nose.
            if (mount.Aim is MountAim.Left or MountAim.Right && !ModelLibrary.Aligned(view.Model.Muzzles.TryGetValue(mount.Slot, out var sideMuzzle) ? sideMuzzle : null))
                direction = view.Body.right * (mount.Aim == MountAim.Left ? -1f : 1f);
            if (Verbose)
                foreach (var n in nodes)
                    if (n != null && n.GetComponent<LaunchPoint>() is { } lp)
                        f.Note += $"[{n.name} at {modelRoot.InverseTransformPoint(n.position):F2} fwd {modelRoot.InverseTransformDirection(n.forward):F2} spread {lp.Spread:F2} measured {lp.Measured}; dir {modelRoot.InverseTransformDirection(direction):F2}] ";
            var notes = new List<string>();
            var fallback = nodes.Any(n => n == null || !(n.name.StartsWith("Muzzle_") || n.name.StartsWith("Launch_")));
            if (fallback) notes.Add("no muzzle of its own (" + (view.Model.Muzzles.ContainsKey(mount.Slot) ? $"Muzzle_{mount.Slot} unused" : $"no Muzzle_{mount.Slot}") + ")");
            var borrowed = false;
            if (index == 0) mainNodes.UnionWith(nodes.Where(n => n != null));
            else if (mount.Slot != def.Mounts[0].Slot && nodes.Any(mainNodes.Contains))
            {
                notes.Add("fires from the main gun's muzzle");
                borrowed = true;
            }

            float? worstAhead = 0f;
            var worstAcross = 0f;
            var worstAngle = 0f;
            var radius = 0f;
            var bad = new List<string>();
            var partNames = new SortedSet<string>();
            if (mount.Weapon.Projectile is ProjectileKind.Bomb or ProjectileKind.Drone)
            {
                // Bombs drop from a bay or pylon, drones climb off a rack, out of a cell or a hangar's
                // door: the release point only has to be on the model.
                var box = new Bounds(modelRoot.position, Vector3.zero);
                var first = true;
                foreach (var p in parts)
                {
                    if (first) box = p.Box;
                    else box.Encapsulate(p.Box);
                    first = false;
                }
                box.Expand(0.3f);
                foreach (var (at, _) in points)
                {
                    f.Marks.Add((at, at));
                    if (!box.Contains(at)) bad.Add("released off the model");
                }
                f.Part = mount.Weapon.Projectile == ProjectileKind.Bomb ? "dropped" : "released";
                f.AheadOfTip = float.NaN;
                notes.AddRange(bad.Distinct());
                f.Note = string.Join("; ", notes);
                f.Verdict = bad.Count > 0 || borrowed ? "WRONG" : "OK";
                return;
            }
            foreach (var (at, node) in points)
            {
                var tris = Candidates(parts, Group(node, modelRoot), at, direction);
                var probe = Probe(tris, at, direction);
                if (probe == null)
                {
                    bad.Add("no barrel, tube or pod round its line" + (Verbose ? $" [{Why}; {tris.Count} tris]" : ""));
                    worstAhead = null;
                    f.Marks.Add((at, at));
                    continue;
                }
                var (tip, across, r, angle, part) = probe.Value;
                var spread = IsSpread(node);
                if (spread)
                {
                    // A face of tubes, perhaps sunk in a frame that reaches past it: rounds leave from
                    // the face itself, the first surface behind the point along its line.
                    // Rays from ahead onto it round the point: the front-most hit is the face (a
                    // ray down a tube's bore reaches its bottom instead).
                    var side = Vector3.Cross(direction, Mathf.Abs(direction.y) < 0.9f ? Vector3.up : Vector3.right).normalized;
                    var lift = Vector3.Cross(side, direction);
                    var hitsBack = new List<(float back, string part, float angle)>();
                    for (var k = 0; k < 9; k++)
                    {
                        var ring = k == 0 ? Vector3.zero : (side * Mathf.Cos(k * Mathf.PI / 4f) + lift * Mathf.Sin(k * Mathf.PI / 4f)) * 0.08f;
                        var back = Cast(tris, at + ring + direction * Forward, -direction, Forward + Back, out var facePart, out var normal);
                        if (back >= Forward + Back) continue;
                        // The tubes' way is square to their face.
                        hitsBack.Add((back, facePart, Vector3.Angle(Vector3.Dot(normal, direction) < 0f ? -normal : normal, direction)));
                    }
                    if (hitsBack.Count > 0)
                    {
                        var front = hitsBack.Min(h => h.back);
                        var onFace = hitsBack.Where(h => h.back < front + 0.03f).ToList();
                        tip = Forward - front;
                        part = onFace[0].part;
                        // The face's own triangles are the ones square to the line (a rim's sides are not).
                        angle = onFace.Min(h => h.angle);
                    }
                }
                f.Marks.Add((at, at + direction * tip));
                partNames.Add(part);
                var ahead = -tip; // the muzzle ahead of the open end (+) or inside it (-)
                if (worstAhead.HasValue && Mathf.Abs(ahead) > Mathf.Abs(worstAhead.Value)) worstAhead = ahead;
                if (!spread && !float.IsNaN(across)) worstAcross = Mathf.Max(worstAcross, across);
                if (!float.IsNaN(angle)) worstAngle = Mathf.Max(worstAngle, angle);
                radius = Mathf.Max(radius, r);
                if (ahead < -Inside) bad.Add($"{-ahead:0.00} m inside");
                if (ahead > Ahead) bad.Add($"{ahead:0.00} m ahead of the open end");
                if (!spread && across > Mathf.Max(Across, r * 0.5f)) bad.Add($"{across:0.00} m off the barrel's middle");
                if (!float.IsNaN(angle) && angle > Angle) bad.Add($"flash {angle:0} deg off the barrel");
            }
            f.AheadOfTip = worstAhead ?? float.NaN;
            f.OffAxis = worstAcross;
            f.AxisAngle = worstAngle;
            f.Radius = radius;
            f.Part = string.Join(" ", partNames.Take(3));
            notes.AddRange(bad.Distinct());
            f.Note = (Verbose ? f.Note : "") + string.Join("; ", notes);
            f.Verdict = bad.Count > 0 || borrowed ? "WRONG" : "OK";
        }

        /// <summary>Tools: explain probes that find nothing.</summary>
        public static bool Verbose;

        private static string Why = "";

        private static bool IsSpread(Transform node) => node != null && node.GetComponent<LaunchPoint>() is { } lp && lp.Spread != UnityEngine.Vector2.zero;

        private static readonly Regex GroupPattern = new(@"^(Turret|Mount_[a-z]+|Part_[a-z]+)(\.\d+)?$", RegexOptions.IgnoreCase);

        /// <summary>
        /// The moving group a muzzle belongs to: its nearest turret, weapon mount or boss part, else
        /// the whole model (a hull or aircraft gun).
        /// </summary>
        private static Transform Group(Transform node, Transform modelRoot)
        {
            if (node == null || !node.IsChildOf(modelRoot)) return modelRoot;
            for (var t = node; t != null; t = t.parent)
            {
                if (t == modelRoot) return modelRoot;
                if (GroupPattern.IsMatch(t.name)) return t;
            }
            return modelRoot;
        }

        /// <summary>The model's triangles per part: the imported meshes placed on the spawned model's (posed) transforms.</summary>
        private static List<Part> Geometry(ModelLibrary models, VehicleView view)
        {
            var parts = new List<Part>();
            var prefab = Resources.Load<GameObject>("Models/" + models.ResolveId(view.Def.Model));
            if (prefab == null) return parts;
            var byName = new Dictionary<string, Queue<Transform>>();
            foreach (var t in view.Model.Root.GetComponentsInChildren<Transform>(true))
            {
                if (!byName.TryGetValue(t.name, out var q)) byName[t.name] = q = new Queue<Transform>();
                q.Enqueue(t);
            }
            foreach (var filter in prefab.GetComponentsInChildren<MeshFilter>(true))
            {
                var mesh = filter.sharedMesh;
                if (mesh == null || !byName.TryGetValue(filter.name, out var q) || q.Count == 0) continue;
                var node = q.Dequeue();
                if (!node.gameObject.activeInHierarchy) continue;
                var v = mesh.vertices;
                var tris = mesh.triangles;
                if (tris.Length == 0) continue;
                var m = node.localToWorldMatrix;
                var world = new Vector3[tris.Length];
                var box = new Bounds(m.MultiplyPoint3x4(v[tris[0]]), Vector3.zero);
                for (var i = 0; i < tris.Length; i++)
                {
                    world[i] = m.MultiplyPoint3x4(v[tris[i]]);
                    box.Encapsulate(world[i]);
                }
                parts.Add(new Part { Name = filter.name, Node = node, Tri = world, Box = box });
            }
            return parts;
        }

        /// <summary>The group's triangles near the line through <paramref name="at"/> along <paramref name="dir"/>.</summary>
        private static List<Tri> Candidates(List<Part> parts, Transform group, Vector3 at, Vector3 dir)
        {
            var near = new Bounds(at, Vector3.zero);
            near.Encapsulate(at - dir * Back);
            near.Encapsulate(at + dir * Forward);
            near.Expand(Reach * 2f);
            var list = new List<Tri>();
            foreach (var p in parts)
            {
                if (!p.Node.IsChildOf(group) || !p.Box.Intersects(near)) continue;
                for (var i = 0; i + 2 < p.Tri.Length; i += 3)
                {
                    var a = p.Tri[i];
                    var b = p.Tri[i + 1];
                    var c = p.Tri[i + 2];
                    var lo = Vector3.Min(a, Vector3.Min(b, c));
                    var hi = Vector3.Max(a, Vector3.Max(b, c));
                    if (hi.x < near.min.x || lo.x > near.max.x || hi.y < near.min.y || lo.y > near.max.y || hi.z < near.min.z || lo.z > near.max.z) continue;
                    list.Add(new Tri(a, b, c, p.Name));
                }
            }
            return list;
        }

        /// <summary>
        /// The barrel round a muzzle: where the line along the drawn barrel stops running inside it (its
        /// open end, metres along the line from the muzzle), how far off its middle the line is there,
        /// its radius, the angle between its own axis and the line, and the part it is. Null when no
        /// part runs round the line within <see cref="Back"/> of the muzzle.
        /// </summary>
        private static (float tip, float across, float radius, float angle, string part)? Probe(List<Tri> tris, Vector3 at, Vector3 dir)
        {
            var side = Vector3.Cross(dir, Mathf.Abs(dir.y) < 0.9f ? Vector3.up : Vector3.right).normalized;
            var up = Vector3.Cross(side, dir).normalized;
            var rays = new Vector3[8];
            for (var k = 0; k < 8; k++)
            {
                var a = k * Mathf.PI / 4f;
                rays[k] = side * Mathf.Cos(a) + up * Mathf.Sin(a);
            }
            var hits = new float[8];
            var hitParts = new string[8];

            // Whether the line runs inside something here: walls all round it (seven of eight ways).
            bool InsideAt(float along)
            {
                var o = at + dir * along;
                var n = 0;
                for (var k = 0; k < 8; k++)
                {
                    hits[k] = Cast(tris, o, rays[k], Reach, out hitParts[k]);
                    if (hits[k] < Reach) n++;
                }
                return n >= 7;
            }

            const float step = 0.04f;
            float tip;
            if (Verbose)
            {
                var sb = new StringBuilder();
                foreach (var a in new[] { 0f, -0.1f, -0.3f })
                {
                    InsideAt(a);
                    sb.Append($"@{a}: " + string.Join(",", hits.Select(h => h >= Reach ? "-" : h.ToString("0.00"))) + " ");
                }
                Why = sb.ToString();
            }
            if (InsideAt(0f))
            {
                var a = 0f;
                while (a < Forward && InsideAt(a + step)) a += step;
                if (a >= Forward) return null; // inside something long: not at a barrel's end
                tip = Edge(InsideAt, a, a + step);
            }
            else
            {
                var a = 0f;
                while (a > -Back && !InsideAt(a - step)) a -= step;
                if (a <= -Back) return null;
                tip = Edge(InsideAt, a - step, a);
            }
            // Its middle just behind the open end, and further back for its axis.
            if (!Middle(tip - 0.03f, out var c1, out var r1, out var part)) return (tip, float.NaN, 0f, float.NaN, "?");
            var angle = float.NaN;
            foreach (var back in new[] { 0.45f, 0.25f, 0.12f })
            {
                if (!Middle(tip - 0.03f - back, out var c2, out var r2, out _) || r2 > r1 * 1.6f + 0.02f || r2 < r1 * 0.5f - 0.02f) continue;
                var p1 = at + dir * (tip - 0.03f) + c1;
                var p2 = at + dir * (tip - 0.03f - back) + c2;
                angle = Vector3.Angle(p1 - p2, dir);
                break;
            }
            return (tip, c1.magnitude, r1, angle, part);

            bool Middle(float along, out Vector3 centre, out float radius, out string name)
            {
                centre = Vector3.zero;
                radius = 0f;
                name = "?";
                if (!InsideAt(along)) return false;
                var n = 0;
                for (var k = 0; k < 4; k++)
                {
                    if (hits[k] >= Reach || hits[k + 4] >= Reach) continue;
                    // The middle between the walls either way (rays k and k + 4 point opposite ways).
                    centre += rays[k] * ((hits[k] - hits[k + 4]) * 0.5f);
                    radius += (hits[k] + hits[k + 4]) * 0.5f;
                    n++;
                }
                if (n == 0) return false;
                // Four pairs 45 degrees apart each see the middle's offset along their own line.
                centre *= n == 4 ? 0.5f : 1f / n;
                radius /= n;
                name = hitParts.Where(x => x != null).GroupBy(x => x).OrderByDescending(g => g.Count()).First().Key;
                return true;
            }
        }

        /// <summary>The edge between inside and outside somewhere between <paramref name="a"/> and <paramref name="b"/>, to 1 mm.</summary>
        private static float Edge(Func<float, bool> inside, float a, float b)
        {
            var aIn = inside(a);
            for (var i = 0; i < 6; i++)
            {
                var m = (a + b) * 0.5f;
                if (inside(m) == aIn) a = m;
                else b = m;
            }
            return aIn ? a : b;
        }

        /// <summary>The nearest hit of a ray on the triangles, either face (or <paramref name="max"/>).</summary>
        private static float Cast(List<Tri> tris, Vector3 o, Vector3 d, float max, out string part) => Cast(tris, o, d, max, out part, out _);

        private static float Cast(List<Tri> tris, Vector3 o, Vector3 d, float max, out string part, out Vector3 normal)
        {
            var best = max;
            part = null;
            normal = Vector3.zero;
            for (var i = 0; i < tris.Count; i++)
            {
                var tri = tris[i];
                var p = Vector3.Cross(d, tri.E2);
                var det = Vector3.Dot(tri.E1, p);
                if (det > -1e-10f && det < 1e-10f) continue;
                var inv = 1f / det;
                var s = o - tri.A;
                var u = Vector3.Dot(s, p) * inv;
                if (u < 0f || u > 1f) continue;
                var q = Vector3.Cross(s, tri.E1);
                var v = Vector3.Dot(d, q) * inv;
                if (v < 0f || u + v > 1f) continue;
                var t = Vector3.Dot(tri.E2, q) * inv;
                if (t > 1e-4f && t < best)
                {
                    best = t;
                    part = tri.Part;
                    normal = Vector3.Cross(tri.E1, tri.E2).normalized;
                }
            }
            return best;
        }

        /// <summary>Batch mode: writes the audit table (Docs/muzzle-audit.md, or -mbAuditOut).</summary>
        public static void Report()
        {
            var path = Argument("-mbAuditOut") ?? Path.Combine(Directory.GetCurrentDirectory(), "Docs", "muzzle-audit.md");
            var ids = Argument("-mbAuditIds");
            Verbose = Argument("-mbAuditVerbose") != null;
            var only = ids != null ? new HashSet<string>(ids.Split('+')) : null;
            var catalog = GameContent.LoadCatalog();
            var rows = Run(catalog, only);
            var hd = Run(catalog, only, highDetail: true);
            File.WriteAllText(path, Markdown(rows, hd).Replace("\n", "\r\n"));
            Debug.Log($"MUZZLE AUDIT: {rows.Count(r => r.Verdict != "n/a")} firing mounts, {rows.Count(r => !r.Ok)} wrong; " +
                      $"high detail {hd.Count(r => r.Verdict != "n/a")} mounts, {hd.Count(r => !r.Ok)} wrong -> {path}");
            foreach (var r in rows.Concat(hd).Where(r => !r.Ok))
                Debug.Log($"MUZZLE WRONG {r.Model} m{r.Mount} {r.Slot} {r.Weapon} [{r.Node}] ahead {r.AheadOfTip:0.00} off {r.OffAxis:0.00} axis {r.AxisAngle:0.0}: {r.Note}");
            if (Application.isBatchMode) EditorApplication.Exit(0);
        }

        public static string Markdown(List<Finding> rows, List<Finding> hd)
        {
            var sb = new StringBuilder();
            sb.Append("# Muzzle audit\n\n");
            sb.Append("Generated by `MachineBrigade.Editor.MuzzleGeometryAudit.Report` (DECISIONS 13E); `MuzzleAuditTests` enforces it.\n\n");
            sb.Append("Every weapon mount of every armed vehicle, elite, boss and tower, spawned through the game's own path ");
            sb.Append("(`ModelLibrary`'s template and launch points, `VehicleView.MuzzleOf`'s slot mapping) and measured against the model's own ");
            sb.Append("triangles in the muzzle's moving group (its turret, weapon mount or boss part; the whole model for a hull or aircraft gun).\n\n");
            sb.Append("- **Ahead of tip:** where the muzzle sits along the drawn barrel's line against the open end of its barrel, tube or pod ");
            sb.Append($"(+ ahead of it, - inside it), drawn metres, worst over the mount's points. Allowed -{Inside:0.00} to +{Ahead:0.00}.\n");
            sb.Append($"- **Off axis:** off the barrel's middle at its open end, drawn metres (allowed {Across:0.00}, or half the barrel's radius). ");
            sb.Append("On a face of tubes, where rounds leave from spots all over it, the point only has to be on the face (`face`).\n");
            sb.Append($"- **Axis:** the barrel's own axis (its middle at the tip and further back) against the line the flash is drawn along, degrees (allowed {Angle:0}).\n");
            sb.Append("- **Points:** how many different points the mount fires from (pods, rails, twin barrels, spots on a face).\n");
            sb.Append("- **Part:** the model part the barrel's walls belong to at its open end.\n\n");
            var firing = rows.Where(r => r.Verdict != "n/a").ToList();
            sb.Append($"**{firing.Count} firing mounts on {firing.Select(r => r.Vehicle).Distinct().Count()} vehicles: {firing.Count(r => r.Ok)} right, {firing.Count(r => !r.Ok)} wrong.** ");
            sb.Append($"High-detail variants: {hd.Count(r => r.Verdict != "n/a")} mounts, {hd.Count(r => !r.Ok)} wrong.\n\n");
            Table(sb, rows);
            if (hd.Count > 0)
            {
                sb.Append("\n## High-detail variants (`_hd`, loaded on the high graphics tiers)\n\n");
                Table(sb, hd);
            }
            return sb.ToString();
        }

        private static void Table(StringBuilder sb, List<Finding> rows)
        {
            sb.Append("| Vehicle | Mount | Weapon | Muzzle node | Points | Ahead of tip (m) | Off axis (m) | Axis (deg) | Verdict | Part, notes |\n");
            sb.Append("|---|---|---|---|---|---|---|---|---|---|\n");
            foreach (var r in rows)
            {
                var na = r.Verdict == "n/a";
                var ahead = na ? "" : float.IsNaN(r.AheadOfTip) ? "-" : r.AheadOfTip.ToString("+0.00;-0.00;0.00");
                var across = na ? "" : r.Face ? (r.OffAxis > 0f ? $"{r.OffAxis:0.00}, face" : "face") : r.OffAxis.ToString("0.00");
                var angle = na ? "" : r.AxisAngle.ToString("0.0");
                var notes = string.Join("; ", new[] { r.Part, r.Note }.Where(s => !string.IsNullOrEmpty(s)));
                sb.Append($"| {r.Vehicle}{(r.Model != r.Vehicle ? $" ({r.Model})" : "")} | {r.Mount} {r.Slot} | {r.Weapon} ({r.Kind}) | {r.Node} | ");
                sb.Append($"{(na ? "" : r.Points.ToString())} | {ahead} | {across} | {angle} | {r.Verdict} | {notes} |\n");
            }
        }

        private static string Argument(string name)
        {
            var args = Environment.GetCommandLineArgs();
            for (var i = 0; i < args.Length - 1; i++)
                if (args[i] == name) return args[i + 1];
            return null;
        }
    }
}
