using System.Collections.Generic;
using System.Text.RegularExpressions;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Play-test 14 wave M7 (owner, 04/10: "nên có lửa sau động cơ"): a flying boss's engines burn while it flies. Every
    /// nozzle the model marks with an <c>Engine_flame</c> empty (.001, .002 ...; Tools/blender/mb_pt14_m7.py) gets a
    /// rocket flame drawn the way a missile's motor is (<see cref="MotorPlumes"/>: a white-hot core on the nozzle, a hot
    /// yellow tongue, a cone of stretched flame quads that tapers and reddens and flickers every frame, a soft glow body
    /// for the bloom), plus what a big engine shows and a missile does not: a heat halo round the nozzle's mouth and a row
    /// of shock diamonds down the flame. The empty sits on the nozzle's exit plane; its scale is the exit radius (model
    /// metres) and the flame leaves along its back (-Z in Unity, +Y in Blender: aft for an unrotated empty).
    /// <list type="bullet">
    /// <item>The particles live in the boss's body space (a rig of local-space systems on its Body), so the flame stays on
    /// the nozzle whatever the boss does: hover, strafe, bank, climb or fly off. Fed after the vehicles are drawn
    /// (EffectsDirector.LaunchShots), on the nozzles as drawn this frame.</item>
    /// <item>Throttle: a hovering boss idles at about three quarters, flying and climbing open it up (a climb to a higher
    /// tier burns long), a descent throttles back; a boss flying off the map burns at full power.</item>
    /// <item>A nozzle on a broken part (its node hidden, VehicleView.ShowBroken) goes out; under a quarter of its health
    /// the engine sputters. A crashed, dead or wrecked boss burns nothing.</item>
    /// <item>The engines light the boss's stern and what is under it (one <see cref="HeatLights"/> glow per boss).</item>
    /// <item>Low tier: two cone quads, no glow body, no halo, no diamonds; never fewer than a missile's motor.</item>
    /// </list>
    /// No material on a model renderer is touched (never a MaterialPropertyBlock on MachineBrigade/Lit): only particles.
    /// </summary>
    internal sealed class EngineFlames
    {
        /// <summary>The nozzle empties' names: Engine_flame, Engine_flame.001 ...</summary>
        public static readonly Regex NozzlePattern = new(@"^Engine_flame(\.\d+)?$");

        /// <summary>The flame's length at full throttle in exit radii; its width at the nozzle in exit radii.</summary>
        private const float FlameLength = 7.5f, FlameWidth = 1.9f;

        /// <summary>Stretched quads' lengths in their widths (as MotorPlumes), and the share of a quad the fire fills.</summary>
        private const float ConeStretch = 4.5f, TongueStretch = 3f, GlowStretch = 4f, DiamondStretch = 1.7f, Fill = 0.5f;

        /// <summary>How fast the particles drift towards the nozzle (m/s): only to set the stretch direction (aft).</summary>
        private const float Drift = 0.6f;

        private static Material _fire;

        private sealed class Rig
        {
            public Transform Root;
            public ParticleSystem Core, Cone, Tongue, Glow, Halo, Diamonds;
        }

        private sealed class Engines
        {
            public VehicleView View;
            public Transform[] Nozzles;
            public int[] Parts;
            public Rig Rig;
            public float LastAltitude = float.NaN;
            public float Climb;
            public float Throttle = 0.75f;
            public bool Seen;
            public Vector3 LightAt;
            public float LightReach, LightPower;
            public int Seed;
        }

        private readonly Dictionary<EntityId, Engines> _engines = new();
        private readonly List<EntityId> _gone = new();
        private readonly Stack<Rig> _pool = new();
        private readonly MaterialLibrary _materials;
        private readonly Transform _parent;
        private readonly ScreenCull _cull;

        public EngineFlames(MaterialLibrary materials, Transform parent, ScreenCull cull)
        {
            _materials = materials;
            _parent = parent;
            _cull = cull;
            if (_fire == null)
            {
                // A hotter copy of the fire material, as the missiles' motors burn (MotorPlumes).
                _fire = new Material(materials.Fire) { name = "Engine Fire", hideFlags = HideFlags.DontSave };
                _fire.SetFloat("_Intensity", 2.6f);
            }
            // Built up front (a particle system made mid-battle hitches the frame): two flying bosses at once is the most
            // a battle stages; a third makes its own rig.
            for (var i = 0; i < 2; i++) _pool.Push(Build());
        }

        private Rig Build()
        {
            var root = new GameObject("Engine Flames").transform;
            root.SetParent(_parent, false);
            var rig = new Rig { Root = root };
            rig.Glow = Shared(root, "Engine Glow", _materials.Glow, 300, ParticleSystemRenderMode.Stretch, GlowStretch);
            rig.Halo = Shared(root, "Engine Halo", _materials.Glow, 200, ParticleSystemRenderMode.Billboard, 0f);
            rig.Cone = Shared(root, "Engine Flame", _fire, 900, ParticleSystemRenderMode.Stretch, ConeStretch);
            rig.Tongue = Shared(root, "Engine Tongue", _fire, 300, ParticleSystemRenderMode.Stretch, TongueStretch);
            rig.Diamonds = Shared(root, "Engine Diamonds", _fire, 500, ParticleSystemRenderMode.Stretch, DiamondStretch);
            rig.Core = Shared(root, "Engine Core", _fire, 300, ParticleSystemRenderMode.Billboard, 0f);
            root.gameObject.SetActive(false);
            return rig;
        }

        private static ParticleSystem Shared(Transform parent, string name, Material material, int max, ParticleSystemRenderMode mode, float stretch)
        {
            var ps = PB.Create(parent, name, material, mode);
            var main = ps.main;
            main.loop = true;
            main.maxParticles = max;
            main.startRotation = 0f;
            // The body's space: the flame rides the nozzle while the boss moves, turns, banks and climbs.
            main.simulationSpace = ParticleSystemSimulationSpace.Local;
            main.scalingMode = ParticleSystemScalingMode.Hierarchy;
            var emission = ps.emission;
            emission.enabled = false;
            PB.Colors(ps, Flat(1f));
            if (mode == ParticleSystemRenderMode.Stretch)
            {
                var renderer = ps.GetComponent<ParticleSystemRenderer>();
                renderer.velocityScale = 0f;
                renderer.lengthScale = stretch;
            }
            ps.Play();
            return ps;
        }

        /// <summary>White with the alpha held and then gone: the particle's own colour sets its hue.</summary>
        private static Gradient Flat(float alpha)
        {
            var g = new Gradient();
            g.SetKeys(new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                new[] { new GradientAlphaKey(alpha, 0f), new GradientAlphaKey(alpha * 0.85f, 0.6f), new GradientAlphaKey(0f, 1f) });
            return g;
        }

        /// <summary>
        /// One frame of every flying boss's engines, on the nozzles as just drawn: <paramref name="views"/> the live
        /// vehicles, <paramref name="departing"/> the aircraft flying off the map (a boss among them burns at full power).
        /// </summary>
        public void Feed(IReadOnlyList<VehicleView> views, IReadOnlyList<VehicleView> departing, float dt)
        {
            if (dt <= 0f) return;
            foreach (var e in _engines.Values) e.Seen = false;
            for (var i = 0; i < views.Count; i++) Feed(views[i], false, dt);
            for (var i = 0; i < departing.Count; i++) Feed(departing[i], true, dt);
            _gone.Clear();
            foreach (var (id, e) in _engines)
                if (!e.Seen) _gone.Add(id);
            foreach (var id in _gone)
            {
                Release(_engines[id]);
                _engines.Remove(id);
            }
        }

        private void Feed(VehicleView view, bool leaving, float dt)
        {
            if (view == null || view.Def == null || !view.Def.Boss || !view.Flying || view.Body == null) return;
            if (!_engines.TryGetValue(view.Id, out var e) || e.View != view)
            {
                // A boss redrawn with another model (its view rebuilt) has other nozzles: found again.
                if (e != null) Release(e);
                if (!view.Sim.IsAlive) return;
                _engines[view.Id] = e = Find(view);
            }
            e.Seen = true;
            e.LightPower = 0f;
            var burning = !view.IsWreck && view.Sim.IsAlive && !view.Sim.Crashed && view.Altitude > 1.5f;
            if (e.Nozzles.Length == 0 || !burning)
            {
                Release(e);
                return;
            }
            // Throttle: idle in the hover, up when it flies or climbs, back when it sinks; flat out when it leaves.
            var altitude = view.Altitude;
            var climb = float.IsNaN(e.LastAltitude) ? 0f : (altitude - e.LastAltitude) / dt;
            e.LastAltitude = altitude;
            e.Climb = Mathf.Lerp(e.Climb, climb, 1f - Mathf.Exp(-dt * 4f));
            var speed = Mathf.Clamp01(view.Speed / Mathf.Max(1f, view.Def.Speed));
            var want = leaving ? 1.25f : Mathf.Clamp(0.72f + 0.2f * speed + Mathf.Clamp(e.Climb / 8f, -0.25f, 0.45f), 0.45f, 1.25f);
            e.Throttle = Mathf.MoveTowards(e.Throttle, want, dt * 1.5f);
            if (!_cull.Visible(view.Position, 0.35f)) return;
            if (e.Rig == null || e.Rig.Root == null) e.Rig = Take(view);
            var rig = e.Rig.Root;
            var tier = MatchSettings.Tier;
            var segments = tier switch { GraphicsQuality.Low => 2, GraphicsQuality.Medium => 4, _ => 6 };
            var rich = tier != GraphicsQuality.Low;
            var life = Mathf.Clamp(dt * 2.4f, 0.05f, 0.12f);
            var lightAt = Vector3.zero;
            var lit = 0;
            var reach = 0f;
            for (var n = 0; n < e.Nozzles.Length; n++)
            {
                var nozzle = e.Nozzles[n];
                if (nozzle == null || !nozzle.gameObject.activeInHierarchy) continue;
                var part = e.Parts[n];
                var throttle = e.Throttle;
                if (part >= 0 && view.Sim.PartShare(part) < 0.25f)
                {
                    // A hurt engine coughs: it misses beats and burns short.
                    if (Random.value < 0.3f) continue;
                    throttle *= Random.Range(0.45f, 0.8f);
                }
                var radius = Mathf.Abs(nozzle.lossyScale.y);
                if (radius < 0.01f) continue;
                var mouth = rig.InverseTransformPoint(nozzle.position);
                var axis = rig.InverseTransformDirection(-nozzle.forward).normalized;
                Burn(e.Rig, mouth, axis, radius, throttle, life, segments, rich);
                lightAt += nozzle.position - nozzle.forward * radius * 2.5f;
                reach = Mathf.Max(reach, radius);
                lit++;
            }
            if (lit == 0) return;
            e.LightAt = lightAt / lit;
            e.LightReach = Mathf.Max(8f, reach * 10f + lit * 1.5f);
            e.LightPower = Mathf.Lerp(1.8f, 3.2f, Mathf.InverseLerp(0.45f, 1.25f, e.Throttle));
        }

        /// <summary>One frame of one nozzle's flame, in the rig's space (metres): mouth, flame axis, exit radius.</summary>
        private static void Burn(Rig rig, Vector3 mouth, Vector3 axis, float radius, float throttle, float life, int maxSegments, bool rich)
        {
            // The particles creep towards the nozzle only so the stretched quads lie along the axis, trailing aft.
            var drift = -axis * Drift;
            var total = radius * FlameLength * Mathf.Lerp(0.5f, 1.15f, Mathf.InverseLerp(0.45f, 1.25f, throttle)) * Random.Range(0.86f, 1.14f);
            var width = radius * FlameWidth;
            var step = ConeStretch * Fill;
            var segments = Mathf.Clamp(Mathf.RoundToInt(total / (width * step * 0.8f)), 2, maxSegments);
            var taper = 0f;
            for (var i = 0; i < segments; i++) taper += 1f - 0.55f * i / Mathf.Max(1, segments - 1);
            var baseWidth = Mathf.Clamp(total / (step * taper), width * 0.6f, width * 1.3f);
            // The first quad reaches forward over the nozzle by the end its fire leaves unfilled, so the flame starts on it.
            var along = -baseWidth * ConeStretch * (1f - Fill) * 0.5f;
            for (var i = 0; i < segments; i++)
            {
                var k = segments > 1 ? i / (segments - 1f) : 0f;
                var w = baseWidth * (1f - 0.55f * k) * Random.Range(0.9f, 1.1f);
                var l = w * ConeStretch;
                var dir = (axis + Random.insideUnitSphere * 0.03f).normalized;
                var colour = Color.Lerp(new Color(1f, 0.78f, 0.42f), new Color(1f, 0.26f, 0.05f), k);
                colour.a = Mathf.Lerp(1f, 0.65f, k);
                Emit(rig.Cone, mouth + dir * along, drift, w, life, colour);
                along += l * Fill;
            }
            // The hot tongue out of the throat and a white-hot core on the exit plane.
            var tongue = baseWidth * 0.72f * Random.Range(0.92f, 1.08f);
            Emit(rig.Tongue, mouth - axis * (tongue * TongueStretch * 0.1f), drift, tongue, life, new Color(1f, 0.88f, 0.58f));
            Emit(rig.Core, mouth + axis * (radius * 0.12f), drift, radius * 1.7f * Random.Range(0.92f, 1.08f), life, new Color(1f, 0.93f, 0.72f));
            if (!rich) return;
            // A soft orange body under the whole flame for the bloom, and the heat halo round the mouth.
            var glow = Mathf.Max(baseWidth * 1.6f, total * 1.05f / GlowStretch);
            Emit(rig.Glow, mouth - axis * (glow * GlowStretch * 0.08f), drift, glow, life * 1.2f, new Color(1f, 0.48f, 0.15f, 0.85f));
            Emit(rig.Halo, mouth + axis * (radius * 0.4f), drift, radius * 3.4f * Random.Range(0.94f, 1.06f), life * 1.3f, new Color(1f, 0.55f, 0.2f, 0.55f));
            // Shock diamonds: bright knots down the jet, about one and a half exit diameters apart, fading downstream.
            for (var d = 0; d < 4; d++)
            {
                var at = radius * (2.4f + 2.8f * d);
                var size = radius * (0.95f - 0.15f * d) * Random.Range(0.9f, 1.1f);
                var length = size * DiamondStretch;
                if (at + length * 0.5f > total * 0.8f) break;
                var colour = new Color(1f, 0.95f, 0.8f, (0.95f - 0.2f * d) * Mathf.Clamp01(throttle));
                Emit(rig.Diamonds, mouth + axis * (at - length * 0.5f), drift, size, life, colour);
            }
        }

        private static void Emit(ParticleSystem system, Vector3 position, Vector3 velocity, float size, float life, Color colour)
        {
            system.Emit(new ParticleSystem.EmitParams
            {
                position = position,
                velocity = velocity,
                startSize = size,
                startLifetime = life,
                startColor = colour,
                rotation = 0f,
                applyShapeToPosition = false,
            }, 1);
        }

        /// <summary>The engines' light on the boss's stern and the ground below (between HeatLights.Begin and Commit).</summary>
        public void Light(float now)
        {
            foreach (var e in _engines.Values)
                if (e.LightPower > 0f) HeatLights.Add(e.LightAt, e.LightReach, e.LightPower, e.Seed, now);
        }

        /// <summary>A boss's nozzle empties and the breakable part each rides on (its nearest ancestor that is a part's node).</summary>
        private static Engines Find(VehicleView view)
        {
            var nozzles = new List<Transform>();
            foreach (var t in view.ModelRoot.GetComponentsInChildren<Transform>(true))
                if (NozzlePattern.IsMatch(t.name)) nozzles.Add(t);
            nozzles.Sort((a, b) => string.CompareOrdinal(a.name, b.name));
            var parts = new int[nozzles.Count];
            for (var n = 0; n < nozzles.Count; n++)
            {
                parts[n] = -1;
                for (var t = nozzles[n].parent; t != null && parts[n] < 0; t = t.parent)
                    for (var p = 0; p < view.Def.Parts.Count; p++)
                    {
                        var node = view.Def.Parts[p].Node;
                        if (string.IsNullOrEmpty(node) || System.Array.IndexOf(node.Split('|'), t.name) < 0) continue;
                        parts[n] = p;
                        break;
                    }
            }
            return new Engines { View = view, Nozzles = nozzles.ToArray(), Parts = parts, Seed = view.Id.Value };
        }

        /// <summary>A rig from the pool, put on the boss's body (its scale undone, so the rig's space is in metres).</summary>
        private Rig Take(VehicleView view)
        {
            Rig rig = null;
            while (_pool.Count > 0 && rig == null)
            {
                rig = _pool.Pop();
                if (rig.Root == null) rig = null;
            }
            rig ??= Build();
            rig.Root.SetParent(view.Body, false);
            rig.Root.localPosition = Vector3.zero;
            rig.Root.localRotation = Quaternion.identity;
            // The body carries the model's draw scale: undone here, so sizes and places in the rig are metres.
            rig.Root.localScale = Vector3.one / Mathf.Max(1e-3f, Mathf.Abs(view.Body.lossyScale.y));
            rig.Root.gameObject.SetActive(true);
            foreach (var ps in new[] { rig.Core, rig.Cone, rig.Tongue, rig.Glow, rig.Halo, rig.Diamonds })
                if (ps != null && !ps.isPlaying) ps.Play();
            return rig;
        }

        /// <summary>Back to the pool (when the rig survived its boss): cleared and parked under the effects.</summary>
        private void Release(Engines e)
        {
            if (e.Rig == null) return;
            var rig = e.Rig;
            e.Rig = null;
            if (rig.Root == null) return;
            foreach (var ps in new[] { rig.Core, rig.Cone, rig.Tongue, rig.Glow, rig.Halo, rig.Diamonds })
                if (ps != null) ps.Clear();
            rig.Root.SetParent(_parent, false);
            rig.Root.localScale = Vector3.one;
            rig.Root.gameObject.SetActive(false);
            _pool.Push(rig);
        }

        /// <summary>Tests: the nozzles burning on a boss now (its found empties).</summary>
        internal int Nozzles(EntityId boss) => _engines.TryGetValue(boss, out var e) ? e.Nozzles.Length : 0;
    }
}
