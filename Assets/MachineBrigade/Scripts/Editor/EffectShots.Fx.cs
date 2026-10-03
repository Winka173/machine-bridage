using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Object = UnityEngine.Object;
using Random = UnityEngine.Random;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// Full fix L10, PDF rule C (DECISIONS "Sửa lỗi tổng hợp L9.7/L10 (lane C)"): the effects of every tier T0-T5 and of every
    /// weapon of 120 mm and up, frozen at fixed moments on a metre grid, a main battle tank beside them for scale and the
    /// blast's core (red) and edge (orange) rings drawn over: firing at 0 / 0.2 / 1 s, the landing at 0 / 0.5 / 2 / 10 / 30 s,
    /// and for a gun with more than one barrel one salvo (every barrel's flash and every fall point) and its landing.
    /// <para>Like <see cref="BlastRig"/>, it drives the battle's effect systems on its own clock (no match, no Sim), each step
    /// mirroring what EffectsDirector draws for the round: the round's own blast (its impact tier, scale and size), the edge
    /// ring, the tier's redrawn blast and shockwave rings (EffectsDirector.TierImpact), the lingering smoke (ImpactSmoke), the
    /// crater (DecalPool) and, at the gun, the muzzle flash, the tier's firing look and its ground ring
    /// (EffectsDirector.TierShot). Shared materials only (the grid and rings are copies of the strike-warning material);
    /// nothing changes a game value.</para>
    /// Batch (with graphics): -batchmode -force-d3d11 -quit -executeMethod MachineBrigade.Editor.EffectShots.FxBatch
    /// [-mbFxOut &lt;dir&gt;] (default Builds/effect_shots) [-mbFxIds "tier_T3,p26_leviathan_lev406"] (only these keys or
    /// weapon ids; "tiers" for the six tiers). Writes &lt;dir&gt;/&lt;key&gt;/fire_0s.png, fire_0.2s.png, fire_1s.png,
    /// impact_0s.png, impact_0.5s.png, impact_2s.png, impact_10s.png, impact_30s.png, salvo.png and salvo_impact.png (multi-barrel
    /// guns), and &lt;dir&gt;/index.json (each key's weapon, tier, carrier, core, edge and files), which Tools/docs/build_doc.py reads.
    /// </summary>
    public static partial class EffectShots
    {
        /// <summary>Seconds after the shot at which the firing frames are taken (0: the first frame after it).</summary>
        public static readonly float[] FxFireMoments = { 0f, 0.2f, 1f };

        /// <summary>Seconds after the landing at which the impact frames are taken.</summary>
        public static readonly float[] FxImpactMoments = { 0f, 0.5f, 2f, 10f, 30f };

        private const float FxStep = 1f / 60f;
        private const float FxStart = 1f;
        private const float FxCalibreFrom = 120f;
        private const int FxWidth = 960, FxHeight = 540;

        private static readonly Color FxShockColour = new(1.35f, 1.05f, 0.7f, 0.95f);
        private static readonly Color FxDustRingColour = new(0.8f, 0.7f, 0.55f, 0.6f);
        private static readonly Color FxEdgeRingColour = new(1f, 0.62f, 0.3f, 0.5f);
        private static readonly Color FxLoneRingColour = new(0.95f, 0.9f, 0.75f, 0.35f);
        private static readonly Regex FxBarrelMuzzle = new(@"^Muzzle_b\d+_");

        /// <summary>One subject: a tier's representative round or a weapon of 120 mm and up, with the unit that carries it.</summary>
        private sealed class FxJob
        {
            public string Key;
            public WeaponDef Weapon;
            public VehicleDef Carrier;
            public string Slot;
            public int Tier;
            public bool Salvo;

            /// <summary>The bomb-run fix, pass 4: a stick of bombs (EffectShots.Sticks: before / after the fix), not a gun.</summary>
            public bool Stick;
        }

        /// <summary>A frame to take: when (on the rig's clock), where the camera looks, how much it shows, the file.</summary>
        private readonly struct FxCapture
        {
            public FxCapture(float at, Vector3 focus, float view, string file)
            {
                At = at;
                Focus = focus;
                View = view;
                File = file;
            }

            public float At { get; }
            public Vector3 Focus { get; }
            public float View { get; }
            public string File { get; }
        }

        [MenuItem("Machine Brigade/Render Effect Shots (fix L10)")]
        public static void FxBatch()
        {
            var output = Path.GetFullPath(Argument("-mbFxOut") ?? Path.Combine(Application.dataPath, "../Builds/effect_shots"));
            var only = Argument("-mbFxIds");
            var catalog = GameContent.LoadCatalog();
            var jobs = FxJobs(catalog, only);
            Directory.CreateDirectory(output);
            var entries = new List<string>();
            var failed = new List<string>();
            foreach (var job in jobs)
            {
                try
                {
                    var files = job.Stick ? FxStickRender(catalog, job, output) : FxRender(catalog, job, output);
                    entries.Add(FxIndexEntry(job, files));
                    Debug.Log($"[EffectShots] {job.Key}: {job.Weapon.Id} on {job.Carrier.Id}, {files.Count} frames");
                }
                catch (Exception ex)
                {
                    failed.Add(job.Key);
                    Debug.LogError($"[EffectShots] {job.Key} failed: {ex}");
                }
            }
            var index = new StringBuilder();
            index.Append("{\n  \"note\": \"Written by MachineBrigade.Editor.EffectShots.FxBatch (full fix L10, rule C): one folder per key, ");
            index.Append("frames at fire +0 / 0.2 / 1 s and impact +0 / 0.5 / 2 / 10 / 30 s, a salvo for a multi-barrel gun; 1 m grid, ");
            index.Append("5 m lines darker; core ring red, edge ring orange; a main battle tank for scale.\",\n");
            index.Append("  \"failed\": [").Append(string.Join(", ", failed.Select(FxQuote))).Append("],\n");
            // The bomb-run fix, pass 4: a run for some keys only (-mbFxIds) keeps the other keys' entries already in the index.
            entries.AddRange(FxKeptEntries(Path.Combine(output, "index.json"), jobs.Select(j => j.Key)));
            index.Append("  \"jobs\": [\n").Append(string.Join(",\n", entries)).Append("\n  ]\n}\n");
            File.WriteAllText(Path.Combine(output, "index.json"), index.ToString(), new UTF8Encoding(false));
            Debug.Log($"[EffectShots] wrote {entries.Count} subjects to {output} ({failed.Count} failed)");
        }

        // ------------------------------------------------------------------------------------------------ which subjects

        /// <summary>
        /// The six tiers (each its representative: a round of that tier on a unit with a model, one with a blast first, then not
        /// a boss's, then the largest core, then the id) and every weapon of 120 mm and up a unit carries. <paramref name="only"/>
        /// (comma list) keeps the keys or weapon ids named; "tiers" keeps the six tiers.
        /// </summary>
        private static List<FxJob> FxJobs(Catalog catalog, string only)
        {
            var carriers = new Dictionary<string, (VehicleDef def, string slot)>();
            foreach (var v in catalog.Vehicles.Values.OrderBy(x => x.Boss ? 1 : 0).ThenBy(x => x.Flying ? 1 : 0).ThenBy(x => x.Id, StringComparer.Ordinal))
            {
                if (string.IsNullOrEmpty(v.Model) || Resources.Load<GameObject>("Models/" + v.Model) == null) continue;
                foreach (var mount in v.Mounts)
                    if (mount.Weapon.Damage > 0f && !carriers.ContainsKey(mount.Weapon.Id)) carriers[mount.Weapon.Id] = (v, mount.Slot);
            }
            var jobs = new List<FxJob>();
            for (var tier = 0; tier <= TierFx.Top; tier++)
            {
                var t = tier;
                var pick = catalog.Weapons.Values
                    .Where(w => w.Tier == t && carriers.ContainsKey(w.Id) && !w.Beam && w.Projectile != ProjectileKind.Flame)
                    .OrderBy(w => w.SplashRadius > 0f ? 0 : 1)
                    .ThenBy(w => carriers[w.Id].def.Boss ? 1 : 0)
                    .ThenByDescending(w => w.SplashRadius)
                    .ThenBy(w => w.Id, StringComparer.Ordinal)
                    .FirstOrDefault();
                if (pick == null) continue;
                var (def, slot) = carriers[pick.Id];
                jobs.Add(new FxJob { Key = "tier_T" + t, Weapon = pick, Carrier = def, Slot = slot, Tier = t, Salvo = pick.Barrels > 1 });
            }
            foreach (var w in catalog.Weapons.Values.Where(x => x.CaliberMm >= FxCalibreFrom && carriers.ContainsKey(x.Id)).OrderBy(x => x.Id, StringComparer.Ordinal))
            {
                var (def, slot) = carriers[w.Id];
                jobs.Add(new FxJob { Key = w.Id, Weapon = w, Carrier = def, Slot = slot, Tier = Mathf.Max(0, TierFx.Of(w)), Salvo = w.Barrels > 1 });
            }
            // The bomb-run fix, pass 4: the bomb sticks, before and after the fix (EffectShots.Sticks).
            FxStickJobs(catalog, jobs);
            if (string.IsNullOrEmpty(only)) return jobs;
            var keep = new HashSet<string>(only.Split(',').Select(x => x.Trim()).Where(x => x.Length > 0), StringComparer.Ordinal);
            return jobs.Where(j => keep.Contains(j.Key) || keep.Contains(j.Weapon.Id) || (keep.Contains("tiers") && j.Key.StartsWith("tier_T", StringComparison.Ordinal))
                || (keep.Contains("sticks") && j.Stick)).ToList();
        }

        private static string FxQuote(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";

        private static string FxNumber(float x) => x.ToString("0.###", CultureInfo.InvariantCulture);

        private static string FxIndexEntry(FxJob job, List<string> files)
        {
            var w = job.Weapon;
            return "    {\"key\": " + FxQuote(job.Key) + ", \"weapon\": " + FxQuote(w.Id) + ", \"tier\": " + job.Tier
                + ", \"carrier\": " + FxQuote(job.Carrier.Id) + ", \"model\": " + FxQuote(job.Carrier.Model)
                + ", \"core\": " + FxNumber(w.SplashRadius) + ", \"edge\": " + FxNumber(w.SplashEdge)
                + ", \"barrels\": " + w.Barrels + ", \"simultaneous\": " + (w.Simultaneous ? "true" : "false")
                + ", \"files\": [" + string.Join(", ", files.Select(FxQuote)) + "]}";
        }

        // ------------------------------------------------------------------------------------------------ one subject

        /// <summary>The effect systems one subject needs, on the rig's clock.</summary>
        private sealed class FxRig
        {
            public BlastLayers Layers;
            public MuzzleFx Muzzle;
            public ImpactSmoke Smoke;
            public DecalPool Decals;
            public DebrisPool Debris;
            public FireSpots Fires;
            public readonly List<ExplosionEffect> Blasts = new();
            public readonly ExplosionEffect[] TierBlasts = new ExplosionEffect[TierFx.Top + 1];
            public readonly ExplosionEffect[] TierFire = new ExplosionEffect[TierFx.Top + 1];
            public readonly Dictionary<ExplosionTier, ExplosionEffect> Rounds = new();

            public void Tick(float now, float dt)
            {
                foreach (var b in Blasts) b.Tick(now);
                Muzzle.Tick(now);
                Smoke.Tick(now);
                Decals.Tick(now);
                Debris.Tick(now, dt);
                Fires.Tick(now, dt);
            }
        }

        private static List<string> FxRender(Catalog catalog, FxJob job, string output)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Random.InitState(20261003);
            var fog = RenderSettings.fog;
            RenderSettings.fog = false;
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Effect Shots").transform;
            var owned = new List<Material>();
            var written = new List<string>();
            var rt = new RenderTexture(FxWidth, FxHeight, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            Texture2D frame = null;
            Camera camera = null;
            try
            {
                Stage(materials, root, 900f);
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
                var core = Mathf.Max(0f, w.SplashRadius);
                var edge = Mathf.Max(core, w.SplashEdge);
                var reach = Mathf.Max(edge, 2f);
                var grid = FxMaterial(materials, owned, new Color(0.09f, 0.09f, 0.08f));
                var gridBold = FxMaterial(materials, owned, new Color(0.02f, 0.02f, 0.02f));
                var coreRing = FxMaterial(materials, owned, new Color(2.6f, 0.25f, 0.15f));
                var edgeRing = FxMaterial(materials, owned, new Color(2.4f, 1.2f, 0.2f));

                // Three places on one clock, far apart: the gun firing, the round landing, the salvo.
                var gunAt = new Vector3(0f, 0f, 0f);
                var landAt = new Vector3(260f, 0.15f, 0f);
                var salvoAt = new Vector3(0f, 0f, 260f);
                var events = new List<(float at, Action<float> run)>();
                var captures = new List<FxCapture>();
                var folder = Path.Combine(output, job.Key);
                Directory.CreateDirectory(folder);

                // The gun: the carrier at its in-game size, facing +X, an MBT beside it.
                var shooter = FxSpawn(models, job.Carrier, gunAt, 90f, 0, root);
                var size = FxSize(shooter);
                var gunView = Mathf.Max(9f, size * 0.85f);
                FxGrid(root, gunAt, gunView * 2.2f, gunView, grid, gridBold);
                FxScaleTank(models, catalog, root, gunAt + new Vector3(0f, 0f, -(size * 0.6f + 6f)));
                events.Add((FxStart, now => FxFire(rig, job, shooter, now)));
                foreach (var m in FxFireMoments)
                    captures.Add(new FxCapture(FxStart + Mathf.Max(m, FxStep), gunAt + Vector3.up * 1.5f, gunView, Path.Combine(folder, $"fire_{FxNumber(m)}s.png")));

                // The landing: the round's blast on the grid, its rings drawn, an MBT just outside the edge.
                var landView = Mathf.Max(10f, reach * 1.7f + 4f);
                FxGrid(root, landAt, landView * 2.2f, landView, grid, gridBold);
                if (core > 0f) FxCircle(root, landAt, core, coreRing, landView);
                if (edge > core) FxCircle(root, landAt, edge, edgeRing, landView);
                FxScaleTank(models, catalog, root, landAt + new Vector3(reach + 4.5f, -0.15f, -(reach + 4.5f)) * 0.7071f);
                events.Add((FxStart, now => FxImpact(rig, w, landAt, now, events)));
                foreach (var m in FxImpactMoments)
                    captures.Add(new FxCapture(FxStart + Mathf.Max(m, FxStep), landAt + Vector3.up * Mathf.Min(6f, 1f + m * 0.4f), landView,
                        Path.Combine(folder, $"impact_{FxNumber(m)}s.png")));

                // The salvo: every barrel's flash and every fall point in one frame, then their landings.
                if (job.Salvo) FxSalvo(rig, job, models, catalog, root, salvoAt, events, captures, folder, grid, gridBold, coreRing, edgeRing);

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
        /// Runs the rig's clock from 0 to the last capture: the events as they fall due, the effect systems stepped, each
        /// capture rendered to its file (the first render is thrown away: it compiles the shaders).
        /// </summary>
        private static void FxShoot(FxRig rig, Transform root, List<(float at, Action<float> run)> events, List<FxCapture> captures,
            RenderTexture rt, List<string> written, ref Camera camera, ref Texture2D frame)
        {
            camera = Camera(root);
            camera.aspect = FxWidth / (float)FxHeight;
            camera.farClipPlane = 400f;
            camera.targetTexture = rt;
            // The first render compiles the shaders (drawn magenta): thrown away.
            camera.Render();
            frame = new Texture2D(FxWidth, FxHeight, TextureFormat.RGB24, false);
            var systems = root.GetComponentsInChildren<ParticleSystem>(true);
            var end = captures.Count > 0 ? captures.Max(c => c.At) + FxStep : FxStart;
            var time = 0f;
            var nextEvent = 0;
            var nextCapture = 0;
            events.Sort((a, b) => a.at.CompareTo(b.at));
            captures.Sort((a, b) => a.At.CompareTo(b.At));
            while (time <= end)
            {
                time += FxStep;
                var ran = false;
                // Events may add later ones (a T5 ring after the first): sort what is left each time one runs.
                while (nextEvent < events.Count && events[nextEvent].at <= time + 1e-4f)
                {
                    events[nextEvent++].run(time);
                    ran = true;
                    if (nextEvent < events.Count) events.Sort(nextEvent, events.Count - nextEvent, Comparer<(float at, Action<float> run)>.Create((a, b) => a.at.CompareTo(b.at)));
                }
                if (ran) systems = root.GetComponentsInChildren<ParticleSystem>(true);
                rig.Tick(time, FxStep);
                foreach (var ps in systems) ps.Simulate(FxStep, false, false, false);
                while (nextCapture < captures.Count && captures[nextCapture].At <= time + 1e-4f)
                {
                    var c = captures[nextCapture++];
                    camera.orthographicSize = c.View;
                    camera.transform.position = c.Focus - camera.transform.forward * 150f;
                    rig.Debris.Draw(time);
                    camera.Render();
                    RenderTexture.active = rt;
                    frame.ReadPixels(new Rect(0, 0, FxWidth, FxHeight), 0, 0);
                    frame.Apply();
                    RenderTexture.active = null;
                    File.WriteAllBytes(c.File, frame.EncodeToPNG());
                    written.Add(Path.GetFileName(c.File));
                }
            }
        }

        // ------------------------------------------------------------------------------------------------ the gun

        /// <summary>The flash a weapon's shot draws (as WeaponEffects picks it): the kind and its size.</summary>
        private static (MuzzleFx.Kind kind, float scale) FxFlash(WeaponDef w)
        {
            switch (w.Projectile)
            {
                case ProjectileKind.Rocket: return (MuzzleFx.Kind.Rocket, w.Indirect ? 1.2f : 0.9f);
                case ProjectileKind.Missile: return (MuzzleFx.Kind.Missile, 1f);
                case ProjectileKind.Bullet: return w.CaliberMm >= 20f ? (MuzzleFx.Kind.Autocannon, 1f) : (MuzzleFx.Kind.MachineGun, 0.8f);
                default:
                    if (w.Indirect) return (MuzzleFx.Kind.Artillery, w.CaliberMm > 0f && w.CaliberMm < 130f && w.Family == "mortar" ? 0.55f : 1f);
                    return (MuzzleFx.Kind.Cannon, w.CaliberMm >= 120f ? 1.5f : 1.2f);
            }
        }

        /// <summary>The muzzles a shot leaves from: each barrel's own (Muzzle_b&lt;k&gt;_) when the model names them, else the slot's.</summary>
        private static List<Transform> FxMuzzles(ModelInstance shooter, string slot, int barrels)
        {
            var list = new List<Transform>();
            foreach (var t in shooter.Root.GetComponentsInChildren<Transform>(true))
                if (FxBarrelMuzzle.IsMatch(t.name) && (t.name.EndsWith("_" + slot, StringComparison.OrdinalIgnoreCase) || t.name.Contains("_" + slot + "_")))
                    list.Add(t);
            if (list.Count == 0)
                foreach (var t in shooter.Root.GetComponentsInChildren<Transform>(true))
                    if (FxBarrelMuzzle.IsMatch(t.name)) list.Add(t);
            if (list.Count == 0)
            {
                if (shooter.Muzzles.TryGetValue(slot ?? "main", out var own)) list.Add(own);
                else if (shooter.Muzzles.TryGetValue("main", out var main)) list.Add(main);
            }
            list.Sort((a, b) => string.CompareOrdinal(a.name, b.name));
            return list.Count > barrels && barrels > 0 ? list.GetRange(0, barrels) : list;
        }

        private static Vector3 FxAim(WeaponDef w, Transform shooter) =>
            w.Indirect ? (shooter.forward + Vector3.up * 0.9f).normalized : shooter.forward;

        /// <summary>One shot as EffectsDirector draws it: the flash on each barrel firing together, the tier's look, its ground ring.</summary>
        private static void FxFire(FxRig rig, FxJob job, ModelInstance shooter, float now)
        {
            var w = job.Weapon;
            var muzzles = FxMuzzles(shooter, job.Slot, w.Simultaneous ? w.Barrels : 1);
            var t = shooter.Root.transform;
            var direction = FxAim(w, t);
            var (kind, scale) = FxFlash(w);
            var groundY = job.Carrier.Flying ? (float?)null : 0f;
            var first = true;
            foreach (var muzzle in muzzles)
            {
                var from = muzzle.position;
                var anchor = new MuzzleFx.Anchor(muzzle, from, direction);
                rig.Muzzle.Fire(kind, from, direction, now, anchor, scale, groundY);
                if (first) FxTierShot(rig, job.Tier, from, direction, groundY, anchor, now);
                first = false;
            }
            if (muzzles.Count == 0)
            {
                var from = t.TransformPoint(shooter.Muzzle);
                var anchor = new MuzzleFx.Anchor(t, from, direction);
                rig.Muzzle.Fire(kind, from, direction, now, anchor, scale, groundY);
                FxTierShot(rig, job.Tier, from, direction, groundY, anchor, now);
            }
        }

        /// <summary>EffectsDirector.TierShot at full detail: the tier's flash and smoke, the pressure ring, the ground's dust ring.</summary>
        private static void FxTierShot(FxRig rig, int tier, Vector3 from, Vector3 direction, float? groundY, MuzzleFx.Anchor anchor, float now)
        {
            if (tier < 1) return;
            var share = Mathf.Max(0.3f, ExplosionEffect.RichShare);
            rig.Muzzle.TierShot(tier, from, direction, now, anchor, groundY, share);
            if (tier < 3) return;
            var look = TierFx.FireOf(tier);
            var dir = direction.sqrMagnitude > 1e-4f ? direction.normalized : Vector3.forward;
            if (look.Pressure > 0f)
            {
                rig.Layers.AirShock.Emit(new ParticleSystem.EmitParams
                {
                    position = from, startSize = look.Pressure, startLifetime = 0.22f, applyShapeToPosition = false,
                }, 1);
                if (tier >= 5)
                    rig.Layers.AirShock.Emit(new ParticleSystem.EmitParams
                    {
                        position = from, startSize = look.Pressure * 1.5f, startLifetime = 0.34f, applyShapeToPosition = false,
                    }, 1);
            }
            if (groundY.HasValue && rig.TierFire[tier] != null)
            {
                var ground = new Vector3(from.x, groundY.Value + 0.1f, from.z);
                rig.TierFire[tier].Play(ground + new Vector3(dir.x, 0f, dir.z) * 1.5f, now, 1f, 1f, 1f, 0f, share);
            }
        }

        // ------------------------------------------------------------------------------------------------ the landing

        /// <summary>
        /// One round landing on the ground as EffectsDirector draws it (ProjectileImpact): its own blast (impact tier, scale,
        /// size, the ring on its core), the edge ring, the tier's blast, rings, crater and fire (TierImpact), the smoke it leaves
        /// (Linger) and the scorch. No random size or offset (EffectsDirector varies them a little: here the frames compare).
        /// </summary>
        private static void FxImpact(FxRig rig, WeaponDef w, Vector3 at, float now, List<(float at, Action<float> run)> later)
        {
            var core = Mathf.Max(0f, w.SplashRadius);
            var edge = w.SplashEdge;
            var scale = w.ImpactScale > 0f ? w.ImpactScale : 1f;
            var blast = rig.Rounds[w.ImpactTier];
            var grow = BlastSizes.Round(w);
            if (w.ImpactTier > ExplosionTier.Small) grow = Mathf.Max(1f, grow) * BlastSizes.Bigger;
            var ring = core > 0f ? BlastSizes.RingFor(core, blast.RingReach, scale) : 0f;
            blast.Play(at, now, scale, grow, 1f, ring);
            if (core > 0f && blast.RingReach <= 0f) FxRing(rig, at, BlastSizes.RingQuad(core), FxLoneRingColour, 0.6f);
            if (edge > core && core > 0f) FxRing(rig, at, BlastSizes.RingQuad(edge), FxEdgeRingColour, 0.6f);

            var tier = TierFx.Of(w);
            if (tier >= 2)
            {
                var reach = edge > core ? edge : core;
                if (tier >= 4)
                {
                    if (tier >= 5 && core > 0f && edge > core)
                    {
                        FxRing(rig, at, BlastSizes.RingQuad(core), FxShockColour, 0.6f);
                        later.Add((now + 0.25f, _ => FxRing(rig, at, BlastSizes.RingQuad(edge), FxShockColour, 0.85f)));
                    }
                    else if (reach > 0f) FxRing(rig, at, BlastSizes.RingQuad(reach), FxShockColour, 0.7f);
                    if (reach > 0f) later.Add((now + (tier >= 5 ? 0.4f : 0.12f), _ => FxRing(rig, at, BlastSizes.RingQuad(reach), FxDustRingColour, 1.2f)));
                    rig.Decals.Place(at, Mathf.Max(4f, (core > 0f ? core : 4f) * (tier >= 5 ? 1.5f : 1.2f)), EffectLife.Crater(tier));
                }
                rig.TierBlasts[tier].Play(at, now, TierFx.OverlayScale(tier, core), 1f, 1f, 0f, ExplosionEffect.RichShare);
                if (tier >= 3) rig.Fires.Ignite(at, tier >= 5 ? 2f : tier >= 4 ? 1.3f : 0.6f, tier >= 5 ? 40f : tier >= 4 ? 24f : 10f, now);
            }
            var band = EffectLife.BandOf(w, w.ImpactTier);
            rig.Smoke.Linger(band, at, core, now, TierFx.Detail.Full);
            if (w.ImpactTier >= ExplosionTier.Medium)
                rig.Decals.Place(at, (w.ImpactTier >= ExplosionTier.Large ? 5f : 2.2f) * scale * BlastSizes.Ground(w) * BlastSizes.Round(w), EffectLife.Crater(band));
        }

        /// <summary>A shockwave ring on the ground (the blast layers' Shockwave system), as EffectsDirector.Ring / TierRing.</summary>
        private static void FxRing(FxRig rig, Vector3 at, float quad, Color colour, float life)
        {
            if (quad <= 0f) return;
            rig.Layers.Shockwave.Emit(new ParticleSystem.EmitParams
            {
                position = at + Vector3.up * 0.25f, startSize = quad, startColor = colour, startLifetime = life, applyShapeToPosition = false,
            }, 1);
        }

        // ------------------------------------------------------------------------------------------------ the salvo

        /// <summary>
        /// A multi-barrel gun's salvo: the carrier fires every barrel (together, staggered by the view's
        /// <see cref="WeaponDef.BarrelGap"/>, or one after another at its burst interval) towards a spot 45 m off; the fall
        /// points (one per round, spread round the aim point over the blast's core, schematic: the Sim's spread is random) are
        /// marked by their core rings and land 0.6 s after the last shot. salvo.png: just after the last flash, the fall points
        /// in the frame; salvo_impact.png: half a second after the landings.
        /// </summary>
        private static void FxSalvo(FxRig rig, FxJob job, ModelLibrary models, Catalog catalog, Transform root, Vector3 at,
            List<(float at, Action<float> run)> events, List<FxCapture> captures, string folder, Material grid, Material gridBold,
            Material coreRing, Material edgeRing)
        {
            var w = job.Weapon;
            var shooter = FxSpawn(models, job.Carrier, at, 90f, 0, root);
            var size = FxSize(shooter);
            var target = at + new Vector3(Mathf.Max(45f, size * 1.5f), 0.15f, 0f);
            var focus = (at + target) * 0.5f;
            var core = Mathf.Max(2f, w.SplashRadius);
            var view = Mathf.Max(18f, Vector3.Distance(at, target) * 0.62f + core);
            FxGrid(root, focus, view * 2.4f, view, grid, gridBold);
            FxScaleTank(models, catalog, root, at + new Vector3(0f, 0f, -(size * 0.6f + 6f)));
            var barrels = Mathf.Max(1, w.Barrels);
            var muzzles = FxMuzzles(shooter, job.Slot, barrels);
            var gap = w.Simultaneous ? WeaponDef.BarrelGap : Mathf.Max(WeaponDef.BarrelGap, w.BurstInterval);
            var direction = FxAim(w, shooter.Root.transform);
            var (kind, scale) = FxFlash(w);
            var falls = new List<Vector3>();
            for (var k = 0; k < barrels; k++)
            {
                var angle = barrels == 1 ? 0f : k * Mathf.PI * 2f / barrels;
                falls.Add(target + (barrels == 1 ? Vector3.zero : new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * core * 0.8f));
            }
            foreach (var p in falls)
            {
                FxCircle(root, p, core, coreRing, view);
                if (w.SplashEdge > core) FxCircle(root, p, w.SplashEdge, edgeRing, view);
            }
            for (var k = 0; k < barrels; k++)
            {
                var index = k;
                events.Add((FxStart + k * gap, now =>
                {
                    var muzzle = muzzles.Count > 0 ? muzzles[index % muzzles.Count] : shooter.Root.transform;
                    var from = muzzles.Count > 0 ? muzzle.position : shooter.Root.transform.TransformPoint(shooter.Muzzle);
                    var anchor = new MuzzleFx.Anchor(muzzle, from, direction);
                    rig.Muzzle.Fire(kind, from, direction, now, anchor, scale, 0f);
                    if (index == 0) FxTierShot(rig, job.Tier, from, direction, 0f, anchor, now);
                }));
            }
            var last = FxStart + (barrels - 1) * gap;
            var land = last + 0.6f;
            for (var k = 0; k < falls.Count; k++)
            {
                var p = falls[k];
                events.Add((land + k * 0.04f, now => FxImpact(rig, w, p, now, events)));
            }
            captures.Add(new FxCapture(last + 0.05f, focus + Vector3.up * 1.5f, view, Path.Combine(folder, "salvo.png")));
            captures.Add(new FxCapture(land + falls.Count * 0.04f + 0.5f, focus + Vector3.up * 2f, view, Path.Combine(folder, "salvo_impact.png")));
        }

        // ------------------------------------------------------------------------------------------------ the stage

        /// <summary>A unit's model at its in-game size, turned to <paramref name="yaw"/> (degrees), on the ground or at its height.</summary>
        private static ModelInstance FxSpawn(ModelLibrary models, VehicleDef def, Vector3 at, float yaw, int team, Transform parent)
        {
            var instance = models.Spawn(def.Model, team, parent);
            var t = instance.Root.transform;
            t.localScale = Vector3.one * VehicleView.DrawScaleOf(def, instance.Root);
            t.SetPositionAndRotation(at + Vector3.up * (def.Flying ? Mathf.Min(def.Altitude, 12f) : 0f), Quaternion.Euler(0f, yaw, 0f));
            return instance;
        }

        /// <summary>The model's largest horizontal size (m) as drawn.</summary>
        private static float FxSize(ModelInstance instance)
        {
            var renderers = instance.Root.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0) return 6f;
            var bounds = renderers[0].bounds;
            for (var i = 1; i < renderers.Length; i++) bounds.Encapsulate(renderers[i].bounds);
            return Mathf.Max(bounds.size.x, bounds.size.z);
        }

        /// <summary>A main battle tank (the player's colours) standing at <paramref name="at"/> for scale.</summary>
        private static void FxScaleTank(ModelLibrary models, Catalog catalog, Transform root, Vector3 at)
        {
            if (!catalog.Vehicles.TryGetValue("main_battle_tank", out var mbt) || !models.Has(mbt.Model)) return;
            FxSpawn(models, mbt, new Vector3(at.x, 0f, at.z), 45f, 0, root);
        }

        private static Material FxMaterial(MaterialLibrary materials, List<Material> owned, Color colour)
        {
            var m = new Material(materials.StrikeWarning) { name = "Effect Shot Line" };
            m.SetColor("_Color", colour);
            owned.Add(m);
            return m;
        }

        /// <summary>A metre grid on the ground round <paramref name="centre"/>: a line every metre, every fifth bolder; widths in pixels of the view.</summary>
        private static void FxGrid(Transform root, Vector3 centre, float span, float view, Material thin, Material bold)
        {
            var parent = new GameObject("Metre Grid").transform;
            parent.SetParent(root, false);
            var half = Mathf.Ceil(span * 0.5f);
            var pixel = view * 2f / FxHeight;
            var x0 = Mathf.Round(centre.x);
            var z0 = Mathf.Round(centre.z);
            for (var k = -half; k <= half; k += 1f)
            {
                var heavy = Mathf.Abs(Mathf.Round(k)) % 5f < 0.5f;
                FxLine(parent, new Vector3(x0 + k, 0.06f, z0 - half), new Vector3(x0 + k, 0.06f, z0 + half), heavy ? bold : thin, pixel * (heavy ? 2f : 1f));
                FxLine(parent, new Vector3(x0 - half, 0.06f, z0 + k), new Vector3(x0 + half, 0.06f, z0 + k), heavy ? bold : thin, pixel * (heavy ? 2f : 1f));
            }
        }

        private static void FxLine(Transform parent, Vector3 a, Vector3 b, Material material, float width)
        {
            var line = new GameObject("Line").AddComponent<LineRenderer>();
            line.transform.SetParent(parent, false);
            line.sharedMaterial = material;
            line.useWorldSpace = true;
            line.widthMultiplier = width;
            line.positionCount = 2;
            line.SetPosition(0, a);
            line.SetPosition(1, b);
            line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            line.receiveShadows = false;
        }

        /// <summary>A ring on the ground of <paramref name="radius"/> m (the blast's core or edge), 3 pixels wide.</summary>
        private static void FxCircle(Transform root, Vector3 at, float radius, Material material, float view)
        {
            var line = new GameObject("Blast Ring").AddComponent<LineRenderer>();
            line.transform.SetParent(root, false);
            line.sharedMaterial = material;
            line.loop = true;
            line.useWorldSpace = true;
            line.widthMultiplier = view * 2f / FxHeight * 3f;
            line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            line.receiveShadows = false;
            const int points = 96;
            line.positionCount = points;
            for (var i = 0; i < points; i++)
            {
                var a = i * Mathf.PI * 2f / points;
                line.SetPosition(i, new Vector3(at.x + Mathf.Cos(a) * radius, 0.14f, at.z + Mathf.Sin(a) * radius));
            }
        }
    }
}
