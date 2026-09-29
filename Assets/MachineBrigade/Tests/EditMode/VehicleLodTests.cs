using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The vehicles' detail levels: every model the catalogue can field has a simplified level
    /// (far fewer triangles and draws, same size) and an impostor page; the level follows the
    /// vehicle's size on screen with a band that stops flicker; and nothing a player relies on
    /// (selection ring, health bar, team colours, turret aim, aircraft) is lost at any level.
    /// </summary>
    public class VehicleLodTests
    {
        /// <summary>The simplified level of any one model has at most this share of its triangles.</summary>
        private const float MaxShare = 0.75f;

        /// <summary>...and across the roster at most this share of all of them.</summary>
        private const float MaxRosterShare = 0.4f;

        private MaterialLibrary _materials;
        private ModelLibrary _models;
        private GameObject _root;

        [SetUp]
        public void SetUp()
        {
            _materials = new MaterialLibrary();
            _models = new ModelLibrary(_materials);
            _root = new GameObject("LOD Test");
        }

        [TearDown]
        public void TearDown()
        {
            VehicleLod.Forced = -1;
            ModelLibrary.HighDetail = false;
            Object.DestroyImmediate(_root);
            _models.Dispose();
            _materials.Dispose();
        }

        /// <summary>Every model the catalogue draws a vehicle, tower or boss with.</summary>
        private List<string> FieldableModels()
        {
            var catalog = GameContent.LoadCatalog();
            // Tower branches wear their own models (TowerArt): <tower>_a and _b.
            return catalog.Vehicles.Values.Select(d => TowerArt.ModelFor(d, _models.Has)).Distinct().Where(_models.Has).OrderBy(s => s).ToList();
        }

        [Test]
        public void EveryFieldableModelHasASimplerLevel()
        {
            long all0 = 0, all1 = 0, draws0 = 0, draws1 = 0;
            foreach (var id in FieldableModels())
            {
                var lod = _models.Lod(id);
                Assert.IsNotNull(lod, $"{id} has a simplified level");
                Assert.LessOrEqual(lod.Triangles1, lod.Triangles0 * MaxShare, $"{id}: {lod.Triangles1} of {lod.Triangles0} triangles");
                Assert.Less(lod.Draws1, lod.Draws0, $"{id} takes fewer draws far away");
                Assert.Greater(lod.BakeParts.Count, 0, $"{id} has parts for its impostor");
                all0 += lod.Triangles0;
                all1 += lod.Triangles1;
                draws0 += lod.Draws0;
                draws1 += lod.Draws1;

                var model = _models.Spawn(id, 1, _root.transform, lod: true);
                Assert.AreEqual(lod.Draws1, model.Lod1Renderers.Length, $"{id}: one simplified renderer a part");
                var full = Extent(model.Root.transform, model.Renderers);
                var simple = Extent(model.Root.transform, model.Lod1Renderers);
                var tolerance = Mathf.Max(full.size.x, Mathf.Max(full.size.y, full.size.z)) * 0.05f;
                Assert.AreEqual(full.center.x, simple.center.x, tolerance, $"{id} stays where it was");
                Assert.AreEqual(full.center.z, simple.center.z, tolerance, $"{id} stays where it was");
                Assert.AreEqual(full.size.x, simple.size.x, tolerance * 2f, $"{id} keeps its span");
                // Radio whips are centimetres thick: far away they are under a pixel and the simplifier drops them
                // (they are merged into the hull, so the full extent cannot leave them out). No taller, at most a fifth lower.
                Assert.That(simple.size.y, Is.InRange(full.size.y * 0.8f - tolerance, full.size.y + tolerance * 2f), $"{id} keeps its height");
                Assert.AreEqual(full.size.z, simple.size.z, tolerance * 2f, $"{id} keeps its length");
                foreach (var r in model.Lod1Renderers)
                {
                    Assert.IsFalse(r.gameObject.activeSelf, $"{id}: the simplified level waits until it is switched to");
                    Assert.AreSame(_materials.LodSurface(1), r.sharedMaterial, $"{id}: in its army's far-detail material");
                    var mesh = r.GetComponent<MeshFilter>().sharedMesh;
                    Assert.AreEqual(1, mesh.subMeshCount, $"{id}: one draw a part");
                    Assert.AreEqual(mesh.vertexCount, mesh.normals.Length, $"{id}: normals");
                    Assert.AreEqual(mesh.vertexCount, mesh.colors.Length, $"{id}: baked shading");
                    Assert.AreEqual(mesh.vertexCount, mesh.uv.Length, $"{id}: surfaces");
                }
                Object.DestroyImmediate(model.Root);
            }
            Assert.LessOrEqual(all1, all0 * MaxRosterShare, $"the roster far away: {all1} of {all0} triangles");
            Assert.LessOrEqual(draws1 * 4, draws0, $"the roster far away: {draws1} of {draws0} draws");
            Debug.Log($"[VehicleLodTests] roster: {all1} of {all0} triangles ({100f * all1 / all0:0}%), {draws1} of {draws0} draws");
        }

        [Test]
        public void HighDetailVariantsHaveASimplerLevelToo()
        {
            ModelLibrary.HighDetail = true;
            var checkedAny = false;
            foreach (var id in FieldableModels())
            {
                if (_models.ResolveId(id) == id) continue;
                var lod = _models.Lod(id);
                Assert.IsNotNull(lod, $"{id} (high detail)");
                Assert.AreEqual(id + ModelLibrary.HighDetailSuffix, lod.Id);
                Assert.LessOrEqual(lod.Triangles1, lod.Triangles0 * MaxShare, $"{lod.Id}: {lod.Triangles1} of {lod.Triangles0}");
                checkedAny = true;
            }
            Assert.IsTrue(checkedAny, "some high-detail variants ship");
        }

        private static Bounds Extent(Transform root, IEnumerable<Renderer> renderers)
        {
            var bounds = new Bounds();
            var first = true;
            foreach (var r in renderers)
            {
                var mesh = r.GetComponent<MeshFilter>().sharedMesh;
                var toRoot = root.worldToLocalMatrix * r.transform.localToWorldMatrix;
                var b = mesh.bounds;
                for (var i = 0; i < 8; i++)
                {
                    var p = toRoot.MultiplyPoint3x4(new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y,
                        (i & 4) == 0 ? b.min.z : b.max.z));
                    if (first) bounds = new Bounds(p, Vector3.zero);
                    else bounds.Encapsulate(p);
                    first = false;
                }
            }
            return bounds;
        }

        [Test]
        public void TheSimplifierKeepsShapesAndDropsWhatNobodySees()
        {
            // A flat 20 x 20 grid of 800 triangles is one quad's worth of surface.
            var positions = new List<Vector3>();
            var triangles = new List<int>();
            for (var z = 0; z <= 20; z++)
            for (var x = 0; x <= 20; x++)
                positions.Add(new Vector3(x * 0.1f, 0f, z * 0.1f));
            for (var z = 0; z < 20; z++)
            for (var x = 0; x < 20; x++)
            {
                var i = z * 21 + x;
                triangles.AddRange(new[] { i, i + 21, i + 1, i + 1, i + 21, i + 22 });
            }
            // Left half one surface, right half another: the line between them must stay put.
            var groups = new int[triangles.Count / 3];
            for (var t = 0; t < groups.Length; t++)
                groups[t] = positions[triangles[3 * t]].x + positions[triangles[3 * t + 1]].x + positions[triangles[3 * t + 2]].x < 3f ? 0 : 1;
            // A speck well under the error: gone.
            var speck = positions.Count;
            positions.Add(new Vector3(5f, 0f, 5f));
            positions.Add(new Vector3(5.001f, 0f, 5f));
            positions.Add(new Vector3(5f, 0f, 5.001f));
            triangles.AddRange(new[] { speck, speck + 2, speck + 1 });
            groups = groups.Append(0).ToArray();

            var (kept, keptGroups) = MeshSimplifier.Simplify(positions, triangles.ToArray(), groups, 0.01f, 0.02f);
            Assert.Less(kept.Length / 3, 60, "a flat grid collapses to a handful of triangles");
            Assert.IsFalse(kept.Any(i => i >= speck), "the speck is dropped");
            var area = new float[2];
            for (var t = 0; t < kept.Length / 3; t++)
            {
                var a = positions[kept[3 * t]];
                var n = Vector3.Cross(positions[kept[3 * t + 1]] - a, positions[kept[3 * t + 2]] - a);
                Assert.Greater(n.y, 0f, "no triangle turned over");
                area[keptGroups[t]] += n.magnitude * 0.5f;
            }
            Assert.AreEqual(2f, area[0], 1e-3f, "the left surface keeps its area (its outline and the seam held)");
            Assert.AreEqual(2f, area[1], 1e-3f, "and so does the right");

            // A rough surface keeps its bumps when they are bigger than the error.
            float Rough(Vector3 p) => Mathf.Repeat(Mathf.Sin(p.x * 129.898f + p.z * 782.33f) * 43758.5453f, 1f) * 0.05f;
            var bumpy = positions.Take(441).Select(p => new Vector3(p.x, Rough(p), p.z)).ToList();
            var (bumps, _) = MeshSimplifier.Simplify(bumpy, triangles.Take(2400).ToArray(), groups.Take(800).ToArray(), 0.01f);
            Assert.Greater(bumps.Length / 3, 400, "bumps five times the error are kept");
        }

        [Test]
        public void TheLevelFollowsTheSizeOnScreenWithABand()
        {
            Assert.AreEqual(VehicleLod.Full, VehicleLod.Choose(-1, 200f));
            Assert.AreEqual(VehicleLod.Simple, VehicleLod.Choose(-1, 100f));
            Assert.AreEqual(VehicleLod.Impostor, VehicleLod.Choose(-1, 10f));
            var t1 = VehicleLod.DetailPixels;
            var t2 = VehicleLod.ImpostorPixels;
            Assert.AreEqual(VehicleLod.Full, VehicleLod.Choose(VehicleLod.Full, t1 * 0.95f), "just under the threshold keeps full detail");
            Assert.AreEqual(VehicleLod.Simple, VehicleLod.Choose(VehicleLod.Full, t1 * 0.85f), "well under it drops a level");
            Assert.AreEqual(VehicleLod.Simple, VehicleLod.Choose(VehicleLod.Simple, t1 * 1.05f), "just over it stays simplified");
            Assert.AreEqual(VehicleLod.Full, VehicleLod.Choose(VehicleLod.Simple, t1 * 1.15f), "well over it comes back");
            Assert.AreEqual(VehicleLod.Simple, VehicleLod.Choose(VehicleLod.Impostor, t2 * 1.15f));
            Assert.AreEqual(VehicleLod.Impostor, VehicleLod.Choose(VehicleLod.Simple, t2 * 0.85f));
            Assert.AreEqual(VehicleLod.Full, VehicleLod.Choose(VehicleLod.Impostor, t1 * 2f), "a big jump goes straight to full detail");
            Assert.AreEqual(VehicleLod.Simple, VehicleLod.Choose(VehicleLod.Simple, t2 * 0.5f, VehicleLod.Simple), "no impostor yet: stays on meshes");
            Assert.AreEqual(VehicleLod.Full, VehicleLod.Choose(VehicleLod.Full, 1f, VehicleLod.Full), "no simpler level at all");

            // A pinch that wobbles round a threshold never flickers.
            var level = VehicleLod.Full;
            for (var i = 0; i < 200; i++)
            {
                level = VehicleLod.Choose(level, t1 * (1f + 0.08f * Mathf.Sin(i * 0.7f)));
                Assert.AreEqual(VehicleLod.Full, level, "wobbling within the band");
            }

            // Zooming right out and back in: each level change happens once each way, later on the way back.
            var camera = new GameObject("LOD Camera").AddComponent<Camera>();
            camera.transform.SetParent(_root.transform);
            camera.orthographic = true;
            camera.targetTexture = new RenderTexture(1920, 1080, 16);
            const float tank = 7.5f;
            var changesOut = new List<(float zoom, int level)>();
            var changesIn = new List<(float zoom, int level)>();
            level = -1;
            for (var zoom = 9f; zoom <= 400f; zoom *= 1.01f)
            {
                camera.orthographicSize = zoom;
                var next = VehicleLod.Choose(level, tank * VehicleLod.PixelsPerMetreOf(camera));
                if (level >= 0 && next != level) changesOut.Add((zoom, next));
                level = next;
            }
            for (var zoom = 400f; zoom >= 9f; zoom /= 1.01f)
            {
                camera.orthographicSize = zoom;
                var next = VehicleLod.Choose(level, tank * VehicleLod.PixelsPerMetreOf(camera));
                if (next != level) changesIn.Add((zoom, next));
                level = next;
            }
            Assert.AreEqual(2, changesOut.Count, "full, simplified, impostor going out");
            Assert.AreEqual(2, changesIn.Count, "and back");
            Assert.AreEqual(VehicleLod.Simple, changesOut[0].level);
            Assert.AreEqual(VehicleLod.Impostor, changesOut[1].level);
            Assert.Less(changesIn[0].zoom, changesOut[1].zoom, "the impostor gives way at a closer zoom than it came in");
            Assert.Less(changesIn[1].zoom, changesOut[0].zoom, "and so does the simplified model");
            camera.orthographicSize = 19f;
            Assert.AreEqual(1080f * VehicleLod.RenderScale / 38f, VehicleLod.PixelsPerMetreOf(camera), 1e-3f, "pixels per metre from the zoom and the resolution");
            camera.targetTexture.Release();
        }

        [Test]
        public void TheImpostorAtlasCoversEveryModel()
        {
            var atlas = new ImpostorAtlas(_materials);
            try
            {
                var models = FieldableModels();
                var cells = new HashSet<(int, UnityEngine.Vector2)>();
                var rotation = Quaternion.Euler(52f, -45f, 0f);
                foreach (var id in models)
                    for (var team = 0; team <= 2; team++)
                    {
                        var lod = _models.Lod(id);
                        var page = atlas.Request(lod, team);
                        Assert.IsNotNull(page, $"{id} has a page for army {team}");
                        Assert.AreSame(page, atlas.Request(lod, team), $"{id}: one page an army");
                        Assert.AreEqual(team, page.Team);
                        for (var k = 0; k < ImpostorAtlas.Headings; k++)
                        {
                            var cell = page.Cell(k);
                            Assert.IsTrue(cell.x >= 0f && cell.y >= 0f && cell.x < 1f && cell.y < 1f, $"{id}: heading {k} is on its sheet");
                            Assert.IsTrue(cells.Add((page.Sheet, cell)), $"{id}: heading {k} has a cell of its own");
                        }
                        // The card holds the model whichever way it faces.
                        foreach (var (mesh, local) in lod.BakeParts)
                        {
                            var b = mesh.bounds;
                            for (var i = 0; i < 8; i++)
                            {
                                var p = local.MultiplyPoint3x4(new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y,
                                    (i & 4) == 0 ? b.min.z : b.max.z));
                                Assert.LessOrEqual((p - page.Centre).magnitude, page.Radius, $"{id}: its card is big enough");
                            }
                        }
                    }
                Assert.AreEqual(models.Count * 3, atlas.Pages.Count);
                Assert.AreEqual(Mathf.CeilToInt(models.Count * 3f / ImpostorAtlas.PagesPerSheet), atlas.SheetCount, "sheets are filled before new ones start");
                Assert.AreEqual(models.Count * 3, atlas.PendingCount, "every page waits to be drawn");
                atlas.BakePending(rotation, 4);
                Assert.AreEqual(models.Count * 3 - 4, atlas.PendingCount, "a few pages a frame");
                atlas.BakePending(rotation, 10000);
                Assert.IsTrue(atlas.Pages.All(p => p.Baked), "and then all of them");
                Assert.AreEqual(ImpostorAtlas.PageTeam(0), 0);
                Assert.AreEqual(ImpostorAtlas.PageTeam(7), 2, "armies beyond the two sides share a page");
            }
            finally
            {
                atlas.Dispose();
            }
        }

        [Test]
        public void NothingIsLostAtAnyLevel()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 160f,
                new[] { new TeamStart(0, new Vector2(-60f, -60f)), new TeamStart(1, new Vector2(60f, 60f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));
            var meshes = new MeshLibrary();
            var views = new ViewRegistry(_models, meshes, _materials, _root.transform, 0);
            // The game's view of the two vehicles.
            var camera = new GameObject("LOD Camera").AddComponent<Camera>();
            camera.transform.SetParent(_root.transform);
            camera.orthographic = true;
            camera.orthographicSize = 19f;
            camera.transform.rotation = Quaternion.Euler(52f, -45f, 0f);
            camera.transform.position = new Vector3(5f, 0f, 0f) - camera.transform.forward * 130f;
            camera.farClipPlane = 400f;
            camera.targetTexture = new RenderTexture(1920, 1080, 16);
            views.LodCamera = camera;
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(10f, 0f), 0f);
            var tankView = views.Add(tank);
            var heliView = views.Add(heli);
            tank.Hp = tank.MaxHp * 0.7f;
            heli.Hp = heli.MaxHp * 0.7f;
            tankView.Selected = true;
            try
            {
                Assert.IsNotNull(tankView.Impostor, "a page is asked for when a vehicle is made");
                Assert.AreEqual(0, tankView.Impostor.Team);
                Assert.AreEqual(1, heliView.Impostor.Team);
                for (var level = VehicleLod.Full; level <= VehicleLod.Impostor; level++)
                {
                    VehicleLod.Forced = level;
                    tank.TurretHeading = 1.2f + level;
                    views.SnapshotAll();
                    views.SnapshotAll();
                    views.Render(1f, Quaternion.Euler(52f, -45f, 0f));
                    foreach (var view in new[] { tankView, heliView })
                    {
                        var name = $"{view.DefId} at level {level}";
                        Assert.AreEqual(level, view.Level, name);
                        Assert.IsTrue(view.Root.Find("HealthBar").gameObject.activeSelf, $"{name}: the health bar shows");
                        var lod0 = view.Root.GetComponentsInChildren<MeshRenderer>(true).Where(r => r.name != ModelLibrary.LodName && IsModel(r, view)).ToList();
                        var lod1 = view.Root.GetComponentsInChildren<MeshRenderer>(true).Where(r => r.name == ModelLibrary.LodName).ToList();
                        Assert.Greater(lod1.Count, 0, name);
                        Assert.IsTrue(lod0.All(r => r.enabled == (level == VehicleLod.Full)), $"{name}: the full model shows only at level 0");
                        Assert.IsTrue(lod1.All(r => r.gameObject.activeInHierarchy == (level == VehicleLod.Simple)), $"{name}: the simplified model only at level 1");
                        Assert.IsTrue(lod1.All(r => r.sharedMaterial == _materials.LodSurface(view.Team)), $"{name}: in its army's colours");
                    }
                    Assert.IsTrue(tankView.Root.Find("Selection").GetComponent<MeshRenderer>().enabled, $"level {level}: the selection ring shows");
                    Assert.IsTrue(heliView.Root.Find("Air Ring").GetComponent<MeshRenderer>().enabled, $"level {level}: the aircraft's ground ring shows");
                    // The turret follows its aim at every level, carrying the simplified turret with it.
                    Assert.AreEqual(Mathf.DeltaAngle(0f, (1.2f + level) * Mathf.Rad2Deg), Mathf.DeltaAngle(0f, tankView.Turret.eulerAngles.y), 1f,
                        $"level {level}: the turret aims");
                    Assert.IsNotNull(tankView.Turret.Find(ModelLibrary.LodName), "the simplified turret rides on the turret");
                    Assert.AreEqual(level == VehicleLod.Impostor ? 2 : 0, views.Impostors.LastDrawn, $"level {level}: a card for each vehicle at level 2");
                }
                Assert.IsTrue(heliView.Root.GetComponentsInChildren<Transform>(true).Any(t => t.name.StartsWith("Rotor") &&
                    t.Find(ModelLibrary.LodName) != null), "the rotor keeps its own simplified blades, so it spins");
                Assert.AreNotEqual(_materials.LodSurface(0).GetColor("_BaseColor"), _materials.LodSurface(1).GetColor("_BaseColor"), "the armies' colours differ far away");

                // A vehicle destroyed while it is a card becomes a hulk made of meshes again.
                views.Detach(tank.Id);
                tankView.BecomeWreck();
                Assert.AreEqual(VehicleLod.Simple, tankView.Level, "a hulk is a mesh (its turret can fly off)");
                tankView.AnimateWreck();
                Assert.AreEqual(VehicleLod.Simple, tankView.Level, "and stays one");
            }
            finally
            {
                views.Impostors.Dispose();
                camera.targetTexture.Release();
            }
        }

        /// <summary>A renderer of the vehicle's model (not its ring, bar, lights or rotor blur).</summary>
        private static bool IsModel(Renderer r, VehicleView view)
        {
            for (var t = r.transform; t != null && t != view.Root; t = t.parent)
                if (t == view.Body) return r.name != "Rotor Blur" && !r.name.StartsWith("Nav_");
            return false;
        }
    }
}
