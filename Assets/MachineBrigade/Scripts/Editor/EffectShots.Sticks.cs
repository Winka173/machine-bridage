using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEditor.SceneManagement;
using UnityEngine;
using Object = UnityEngine.Object;
using Random = UnityEngine.Random;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// The bomb-run fix, pass 4 (DECISIONS "Ném bom rải thảm"): the design document's stick pictures, rendered with the
    /// other effect shots (<see cref="FxBatch"/>; keys stick_heavy_bomber and stick_command_airship, "-mbFxIds sticks").
    /// Each stick is laid twice on the metre grid, a main battle tank beside it for scale and every bomb's core (red) and
    /// edge (orange) ring drawn: BEFORE the fix (the heavy bomber's bombs one release speed x burst interval apart, 3.5 m; a
    /// boss bay's eight on one point within its scatter) and AFTER it (the data's stick: n bombs one spacing apart along the
    /// line with their jitter, one release interval after the other). Each lands as EffectsDirector draws a bomb
    /// (<see cref="FxImpact"/>); frames at 0 / 1 / 3 s after the first bomb lands: &lt;dir&gt;/&lt;key&gt;/before_impact_0s.png,
    /// before_impact_1s.png, before_impact_3s.png, after_impact_0s.png, after_impact_1s.png, after_impact_3s.png. The jitter is
    /// schematic (the Sim's is seeded per bomb); nothing changes a game value.
    /// </summary>
    public static partial class EffectShots
    {
        /// <summary>Seconds after a stick's first landing at which its frames are taken.</summary>
        public static readonly float[] FxStickMoments = { 0f, 1f, 3f };

        /// <summary>The sticks shot: the heavy bomber's free-falling stick and one boss bay (the command airship's main bay).</summary>
        private static readonly (string unit, string weapon)[] FxStickSubjects =
        {
            ("heavy_bomber", "bomber_payload"), ("command_airship", "p26_roc_main_roc_bombs"),
        };

        /// <summary>The way the sticks run on the ground: across the screen (the shot camera looks down from 45 degrees round).</summary>
        private static readonly Vector3 FxStickWay = new Vector3(1f, 0f, 1f).normalized;

        private static void FxStickJobs(Catalog catalog, List<FxJob> jobs)
        {
            foreach (var (unit, weapon) in FxStickSubjects)
            {
                if (!catalog.Vehicles.TryGetValue(unit, out var def) || !catalog.Weapons.TryGetValue(weapon, out var w) || w.Stick == null) continue;
                if (string.IsNullOrEmpty(def.Model) || Resources.Load<GameObject>("Models/" + def.Model) == null) continue;
                jobs.Add(new FxJob { Key = "stick_" + unit, Weapon = w, Carrier = def, Slot = null, Tier = Mathf.Max(0, TierFx.Of(w)), Stick = true });
            }
        }

        /// <summary>
        /// Where a stick's bombs land round <paramref name="centre"/>, along <paramref name="way"/>: after the fix (the data's
        /// spacing, a small alternating jitter within the data's) or before it (a free-falling bomber's release speed x burst
        /// interval apart, a boss bay's all on one point; a small spiral of scatter within 0.15 / 0.3 of the core).
        /// </summary>
        internal static List<Vector3> FxStickPoints(WeaponDef w, bool after, Vector3 centre, Vector3 way)
        {
            var s = w.Stick;
            var n = Mathf.Max(1, s.Bombs);
            var overfly = s.Drop == StickDrop.Overfly;
            var spacing = after ? s.Spacing : overfly ? s.ReleaseSpeed * w.BurstInterval : 0f;
            var side = new Vector3(way.z, 0f, -way.x);
            var points = new List<Vector3>(n);
            for (var i = 0; i < n; i++)
            {
                var along = (i - (n - 1) * 0.5f) * spacing;
                float jitterAlong, jitterAcross;
                if (after)
                {
                    jitterAlong = (i % 2 == 0 ? 0.4f : -0.4f) * s.JitterAlong;
                    jitterAcross = (i % 3 - 1) * 0.5f * s.JitterAcross;
                }
                else
                {
                    var turn = i * 2.39996f;
                    var r = Mathf.Max(0.5f, w.SplashRadius * (overfly ? 0.15f : 0.3f)) * Mathf.Sqrt((i + 0.5f) / n);
                    jitterAlong = Mathf.Cos(turn) * r;
                    jitterAcross = Mathf.Sin(turn) * r;
                }
                points.Add(centre + way * (along + jitterAlong) + side * jitterAcross);
            }
            return points;
        }

        /// <summary>Seconds between two bombs landing: the data's release interval after the fix, the burst interval before it.</summary>
        internal static float FxStickGap(WeaponDef w, bool after) => Mathf.Max(0.05f, after ? w.Stick.Interval : w.BurstInterval);

        /// <summary>One stick subject: the stick before and after the fix, each at 0 / 1 / 3 s after its first landing.</summary>
        private static List<string> FxStickRender(Catalog catalog, FxJob job, string output)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20261003);
            var fog = RenderSettings.fog;
            RenderSettings.fog = false;
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Stick Shots").transform;
            var owned = new List<Material>();
            var written = new List<string>();
            var rt = new RenderTexture(FxWidth, FxHeight, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            Texture2D frame = null;
            Camera camera = null;
            try
            {
                Stage(materials, root, 1400f);
                var rig = new FxRig
                {
                    Layers = new BlastLayers(materials, root),
                    Muzzle = new MuzzleFx(materials, root),
                    Smoke = new ImpactSmoke(root),
                    Decals = new DecalPool(meshes.ScorchQuad, root, 64),
                    Debris = new DebrisPool(EffectBudget.High.Debris),
                    Fires = new FireSpots(materials, root),
                };
                rig.Layers.Chunks = new ChunkThrower(rig.Debris, materials, models, rig.Fires, root);
                for (var tier = 2; tier <= TierFx.Top; tier++)
                {
                    rig.TierBlasts[tier] = ExplosionEffect.CreateTier(tier, rig.Layers);
                    rig.Blasts.Add(rig.TierBlasts[tier]);
                    if (tier < 3) continue;
                    rig.TierFire[tier] = ExplosionEffect.CreateTierFire(tier, rig.Layers);
                    rig.Blasts.Add(rig.TierFire[tier]);
                }
                foreach (ExplosionTier t in Enum.GetValues(typeof(ExplosionTier)))
                {
                    rig.Rounds[t] = ExplosionEffect.Create(t, rig.Layers);
                    rig.Blasts.Add(rig.Rounds[t]);
                }

                var w = job.Weapon;
                var stick = w.Stick;
                var core = Mathf.Max(0.5f, w.SplashRadius);
                var edge = Mathf.Max(core, w.SplashEdge);
                var length = Mathf.Max(0, stick.Bombs - 1) * stick.Spacing;
                // Both sticks at one scale (the longer, after the fix): the whole stick and its blasts' edges across the frame.
                var view = Mathf.Max(14f, (length * 0.5f + edge + 6f) / (FxWidth / (float)FxHeight));
                var grid = FxMaterial(materials, owned, new Color(0.09f, 0.09f, 0.08f));
                var gridBold = FxMaterial(materials, owned, new Color(0.02f, 0.02f, 0.02f));
                var coreRing = FxMaterial(materials, owned, new Color(2.6f, 0.25f, 0.15f));
                var edgeRing = FxMaterial(materials, owned, new Color(2.4f, 1.2f, 0.2f));
                var events = new List<(float at, Action<float> run)>();
                var captures = new List<FxCapture>();
                var folder = Path.Combine(output, job.Key);
                Directory.CreateDirectory(folder);
                var side = new Vector3(FxStickWay.z, 0f, -FxStickWay.x);
                var yaw = Mathf.Atan2(FxStickWay.x, FxStickWay.z) * Mathf.Rad2Deg;

                foreach (var after in new[] { false, true })
                {
                    var at = after ? new Vector3(0f, 0.15f, 360f) : new Vector3(0f, 0.15f, 0f);
                    var points = FxStickPoints(w, after, at, FxStickWay);
                    var gap = FxStickGap(w, after);
                    FxGrid(root, at, view * 2f * (FxWidth / (float)FxHeight) * 1.15f, view, grid, gridBold);
                    foreach (var p in points)
                    {
                        FxCircle(root, p, core, coreRing, view);
                        if (edge > core + 0.05f) FxCircle(root, p, edge, edgeRing, view);
                    }
                    // A main battle tank beside the stick for scale.
                    FxScaleTank(models, catalog, root, at + side * (edge + stick.JitterAcross + 5f));
                    // The carrier: a bomber flown on past the end of its stick; a boss off to the side (it lays its stick from a stand-off).
                    var carrier = FxSpawn(models, job.Carrier, Vector3.zero, yaw, 1, root);
                    var size = FxSize(carrier);
                    var place = stick.Drop == StickDrop.Overfly
                        ? at + FxStickWay * (length * 0.5f + edge + size * 0.5f)
                        : at - side * (edge + stick.JitterAcross + size * 0.5f + 6f);
                    carrier.Root.transform.position = new Vector3(place.x, carrier.Root.transform.position.y, place.z);
                    for (var i = 0; i < points.Count; i++)
                    {
                        var p = points[i];
                        events.Add((FxStart + i * gap, now => FxImpact(rig, w, p, now, events)));
                    }
                    var prefix = after ? "after" : "before";
                    foreach (var m in FxStickMoments)
                        captures.Add(new FxCapture(FxStart + Mathf.Max(m, FxStep), at + Vector3.up * Mathf.Min(6f, 1f + m * 0.4f), view,
                            Path.Combine(folder, $"{prefix}_impact_{FxNumber(m)}s.png")));
                }
                FxShoot(rig, root, events, captures, rt, written, ref camera, ref frame);
            }
            finally
            {
                RenderTexture.active = null;
                if (camera != null) camera.targetTexture = null;
                rt.Release();
                Object.DestroyImmediate(rt);
                if (frame != null) Object.DestroyImmediate(frame);
                foreach (var m in owned) Object.DestroyImmediate(m);
                Object.DestroyImmediate(root.gameObject);
                models.Dispose();
                meshes.Dispose();
                materials.Dispose();
                RenderSettings.fog = fog;
            }
            return written;
        }

        /// <summary>
        /// The entries of an index.json already written whose keys this run did not render (a run for some keys only keeps the
        /// rest): each entry is one line starting with <c>{"key": </c> (as <see cref="FxIndexEntry"/> writes them).
        /// </summary>
        private static IEnumerable<string> FxKeptEntries(string path, IEnumerable<string> rendered)
        {
            if (!File.Exists(path)) return Enumerable.Empty<string>();
            var done = new HashSet<string>(rendered, StringComparer.Ordinal);
            var kept = new List<string>();
            foreach (var line in File.ReadAllLines(path))
            {
                var entry = line.TrimEnd().TrimEnd(',');
                var head = entry.TrimStart();
                if (!head.StartsWith("{\"key\": \"", StringComparison.Ordinal)) continue;
                var from = "{\"key\": \"".Length;
                var close = head.IndexOf('"', from);
                if (close < 0 || done.Contains(head.Substring(from, close - from))) continue;
                kept.Add("    " + head);
            }
            return kept;
        }
    }
}
