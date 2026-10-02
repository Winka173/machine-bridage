using System;
using System.Collections.Generic;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// A siege fortress's set pieces as the player sees them (the simulation decides, this draws):
    /// <list type="bullet">
    /// <item><description>the shield dome over the keep while a generator stands (the shared shield
    /// look, <see cref="ShieldVisual"/>): rounds landing on it ripple it, it flickers as the
    /// generators are hurt, and it shatters when the last one falls;</description></item>
    /// <item><description>the line in: a rail line with its train, or a runway with the transport
    /// that lands on it, rolls to its stop, lets the vehicles out and takes off again;</description></item>
    /// <item><description>at night, searchlights sweeping from the fortress's floodlight masts,
    /// locking on to attackers that come near;</description></item>
    /// <item><description>the super-gun's muzzle blast when it fires.</description></item>
    /// </list>
    /// </summary>
    internal sealed class FortressView : IDisposable
    {
        private const float DomeHeight = 0.5f;
        private const float TrainTravel = 9f;
        private const float TrainWait = 7f;
        private const float PlaneApproach = 7f;
        private const float PlaneRoll = 5f;
        private const float PlaneWait = 8f;
        private const float LightHeight = 9f;
        private const int MaxLights = 16;

        private readonly SimWorld _world;
        private readonly SiegeMode _mode;
        private readonly ModelLibrary _models;
        private readonly MaterialLibrary _materials;
        private readonly EffectsDirector _effects;
        private readonly GameObject _root;
        private readonly List<Mesh> _meshes = new();
        private readonly List<Material> _owned = new();
        private readonly int _playerTeam;

        private ShieldVisual _dome;
        private bool _domeShown;

        /// <summary>The fortress's shield generators, their full health together, and what the view last saw of them.</summary>
        private readonly List<Prop> _generators = new();
        private float _generatorsFull, _generatorsLast = 1f;
        private int _generatorsStanding;
        private float _surgeUntil = -1f, _surge;

        private readonly List<Searchlight> _lights = new();
        private Material _coneMaterial, _poolMaterial;
        private bool _night;

        private readonly List<Run> _runs = new();

        public FortressView(SimWorld world, SiegeMode mode, ModelLibrary models, MaterialLibrary materials, EffectsDirector effects,
            Transform parent, int playerTeam)
        {
            _world = world;
            _mode = mode;
            _models = models;
            _materials = materials;
            _effects = effects;
            _playerTeam = playerTeam;
            _root = new GameObject("Fortress");
            _root.transform.SetParent(parent, false);
            BuildDome();
            if (world.Map.Fortress?.Arrival is { } line) BuildLine(line);
            BuildSearchlights();
        }

        // ------------------------------------------------------------------ materials and meshes

        private Material Additive(string name, float intensity, int queue = 3012)
        {
            var m = new Material(Shader.Find("MachineBrigade/Particle")) { name = name };
            m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            m.SetFloat("_DstBlend", (float)BlendMode.One);
            m.SetFloat("_Intensity", intensity);
            m.SetFloat("_Shape", 2f);
            m.SetFloat("_Softness", 1f);
            m.SetFloat("_DepthPull", 0f);
            m.renderQueue = queue;
            _owned.Add(m);
            return m;
        }

        private GameObject Place(string name, Mesh mesh, Material material, bool shadows = false)
        {
            var go = new GameObject(name);
            go.transform.SetParent(_root.transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = shadows ? ShadowCastingMode.On : ShadowCastingMode.Off;
            renderer.receiveShadows = true;
            return go;
        }

        private Mesh Own(Mesh mesh)
        {
            _meshes.Add(mesh);
            return mesh;
        }

        /// <summary>Boxes (centre, size, yaw in degrees) merged into one mesh.</summary>
        private Mesh Boxes(string name, List<(Vector3 centre, Vector3 size, float yaw)> boxes)
        {
            var box = Own(Primitives.Box());
            var parts = new CombineInstance[boxes.Count];
            for (var i = 0; i < boxes.Count; i++)
                parts[i] = new CombineInstance
                {
                    mesh = box, transform = Matrix4x4.TRS(boxes[i].centre, Quaternion.Euler(0f, boxes[i].yaw, 0f), boxes[i].size),
                };
            var mesh = new Mesh { name = name, indexFormat = IndexFormat.UInt32 };
            mesh.CombineMeshes(parts, true, true);
            mesh.RecalculateBounds();
            return Own(mesh);
        }

        // ------------------------------------------------------------------ the shield dome

        /// <summary>
        /// The dome over the keep, exactly the simulation's radius (and half as high): blue when
        /// it is ours (Defend), red-orange when it is the enemy's (Siege).
        /// </summary>
        private void BuildDome()
        {
            if (_mode.DomeRadius <= 1f) return;
            var r = _mode.DomeRadius;
            _dome = new ShieldVisual("Shield Dome", _root.transform, ShieldVisual.Shape.Dome, r);
            var c = _mode.DomeCentre;
            _dome.Transform.position = new Vector3(c.X, 0f, c.Y);
            _dome.Transform.localScale = new Vector3(r, r * DomeHeight, r);
            _dome.SetSide(_mode.Defender == _playerTeam);
            foreach (var prop in _world.Props)
            {
                if (!prop.IsAlive || prop.Def.Id != "shield_generator") continue;
                _generators.Add(prop);
                _generatorsFull += prop.MaxHp;
            }
            _generatorsStanding = _generators.Count;
            _domeShown = _mode.DomeUp;
            if (_domeShown) _dome.Raise(Time.time, 0f);
        }

        private void AnimateDome(float time)
        {
            if (_dome == null) return;
            var r = _mode.DomeRadius;
            if (_domeShown && !_mode.DomeUp)
            {
                // The last generator gone: the dome flares and shatters, its tiles flying off,
                // and a ring of its light runs out over the ground.
                _domeShown = false;
                _dome.Collapse(time);
                var at = new Vector3(_mode.DomeCentre.X, 0.3f, _mode.DomeCentre.Y);
                var colour = ShieldVisual.SideColour(_mode.Defender == _playerTeam);
                _effects.Shockwave(at, r * 2.4f, new Color(colour.r * 2.4f, colour.g * 2.4f, colour.b * 2.4f, 1f));
                _effects.Shockwave(at, r * 1.6f, new Color(1.8f, 1.8f, 1.9f, 0.8f));
                _effects.Jolt(at + Vector3.up * r * 0.3f, 0.45f, 0.12f);
            }
            else if (!_domeShown && _mode.DomeUp)
            {
                _domeShown = true;
                _dome.Raise(time);
            }
            if (_domeShown) _dome.Flicker = GeneratorFlicker(time);
            _dome.Tick(time);
        }

        /// <summary>
        /// How much the dome flickers: more the more its generators are hurt, a burst when one is
        /// hit, and a longer surge when one is destroyed while the others hold it up.
        /// </summary>
        private float GeneratorFlicker(float time)
        {
            if (_generators.Count == 0 || _generatorsFull <= 0f) return 0f;
            var health = 0f;
            var standing = 0;
            foreach (var g in _generators)
            {
                if (!g.IsAlive) continue;
                health += g.Hp;
                standing++;
            }
            var share = health / _generatorsFull;
            if (standing < _generatorsStanding) Surge(time, 1f, 1.1f);
            else if (share < _generatorsLast - 1e-4f) Surge(time, 0.7f, 0.25f);
            _generatorsStanding = standing;
            _generatorsLast = share;
            var flicker = Mathf.Clamp01((1f - share) * 0.8f);
            if (time < _surgeUntil) flicker = Mathf.Max(flicker, _surge);
            return flicker;
        }

        private void Surge(float time, float amount, float seconds)
        {
            if (time < _surgeUntil && _surge > amount) return;
            _surge = amount;
            _surgeUntil = time + seconds;
        }

        /// <summary>A round or a strike landing on the dome, or inside it: a ripple where it struck.</summary>
        private void RippleDome(SimEvent e, float now)
        {
            if (!_domeShown || _dome == null) return;
            var d = System.Numerics.Vector2.Distance(e.Position, _mode.DomeCentre);
            if (d > _mode.DomeRadius * 1.05f) return;
            _dome.Hit(new Vector3(e.Position.X, 0.5f, e.Position.Y), now, default, e.Kind == SimEventKind.StrikeImpact ? 1.5f : 1f);
        }

        // ------------------------------------------------------------------ the line in

        private ArrivalDef _line;
        private float _lineLength;

        /// <summary>The rail line (ballast, sleepers, two rails, a buffer stop) or the runway (tarmac, centre dashes, edge lights).</summary>
        private void BuildLine(ArrivalDef line)
        {
            _line = line;
            if (line.Path.Count < 2) return;
            var a = line.Path[line.Path.Count - 2];
            var b = line.Path[line.Path.Count - 1];
            var dir = new Vector3(b.X - a.X, 0f, b.Y - a.Y);
            _lineLength = dir.magnitude;
            if (_lineLength < 1f) return;
            dir /= _lineLength;
            var yaw = Mathf.Atan2(dir.x, dir.z) * Mathf.Rad2Deg;
            var start = new Vector3(a.X, 0f, a.Y);
            if (line.Kind == ArrivalKind.Rail)
            {
                var bed = new List<(Vector3, Vector3, float)> { (start + dir * (_lineLength * 0.5f) + Vector3.up * 0.04f, new Vector3(3.6f, 0.08f, _lineLength), yaw) };
                Place("Rail Bed", Boxes("Rail Bed", bed), _materials.ForModel("Dirt", -1));
                var sleepers = new List<(Vector3, Vector3, float)>();
                for (var d = 0.6f; d < _lineLength; d += 1.2f) sleepers.Add((start + dir * d + Vector3.up * 0.1f, new Vector3(2.6f, 0.12f, 0.3f), yaw));
                Place("Sleepers", Boxes("Sleepers", sleepers), _materials.ForModel("Wood", -1));
                var side = Vector3.Cross(Vector3.up, dir);
                var rails = new List<(Vector3, Vector3, float)>();
                foreach (var s in new[] { -0.72f, 0.72f })
                    rails.Add((start + dir * (_lineLength * 0.5f) + side * s + Vector3.up * 0.24f, new Vector3(0.12f, 0.16f, _lineLength), yaw));
                // The buffer stop at the end, and the platform's edge beside the stop.
                rails.Add((start + dir * (_lineLength - 0.4f) + Vector3.up * 0.7f, new Vector3(2.4f, 1.1f, 0.6f), yaw));
                Place("Rails", Boxes("Rails", rails), _materials.ForModel("Steel", -1), shadows: true);
                var platform = new List<(Vector3, Vector3, float)>
                {
                    (new Vector3(line.Stop.X, 0.25f, line.Stop.Y) - side * 2.2f + dir * 2f, new Vector3(4f, 0.5f, 30f), yaw),
                };
                Place("Platform", Boxes("Platform", platform), _materials.ForModel("Concrete", -1), shadows: true);
                return;
            }
            // A runway: the full length, from the far end of the approach to the stop's end.
            var first = new Vector3(line.Path[1].X, 0f, line.Path[1].Y);
            var runwayDir = (new Vector3(b.X, 0f, b.Y) - first);
            var runwayLength = runwayDir.magnitude;
            runwayDir /= Mathf.Max(0.01f, runwayLength);
            var runwayYaw = Mathf.Atan2(runwayDir.x, runwayDir.z) * Mathf.Rad2Deg;
            var mid = first + runwayDir * (runwayLength * 0.5f);
            var tarmac = new List<(Vector3, Vector3, float)> { (mid + Vector3.up * 0.03f, new Vector3(16f, 0.06f, runwayLength), runwayYaw) };
            Place("Runway", Boxes("Runway", tarmac), _materials.ForModel("Asphalt", -1));
            var marks = new List<(Vector3, Vector3, float)>();
            for (var d = 6f; d < runwayLength - 4f; d += 12f) marks.Add((first + runwayDir * d + Vector3.up * 0.075f, new Vector3(0.6f, 0.04f, 5f), runwayYaw));
            var sideways = Vector3.Cross(Vector3.up, runwayDir);
            foreach (var s in new[] { -1f, 1f })
                marks.Add((mid + sideways * (s * 7.2f) + Vector3.up * 0.075f, new Vector3(0.35f, 0.04f, runwayLength), runwayYaw));
            // Piano keys at the threshold.
            for (var k = -3; k <= 3; k++) marks.Add((first + runwayDir * 3f + sideways * (k * 1.8f) + Vector3.up * 0.075f, new Vector3(0.9f, 0.04f, 4f), runwayYaw));
            Place("Runway Marks", Boxes("Runway Marks", marks), _materials.ForModel("PlasterWhite", -1));
            var lamps = new List<(Vector3, Vector3, float)>();
            for (var d = 2f; d < runwayLength; d += 10f)
                foreach (var s in new[] { -1f, 1f })
                    lamps.Add((first + runwayDir * d + sideways * (s * 8.6f) + Vector3.up * 0.3f, new Vector3(0.35f, 0.35f, 0.35f), runwayYaw));
            Place("Runway Lights", Boxes("Runway Lights", lamps), _materials.NavWhite);
        }

        /// <summary>A train or an aircraft on its way in: its models and when it stops.</summary>
        private sealed class Run
        {
            public ArrivalKind Kind;
            public float StopAt;
            public readonly List<(Transform part, float behind)> Parts = new();
            public Transform Plane;
            public bool Dusted;
        }

        public void Consume(IReadOnlyList<SimEvent> events)
        {
            var now = Time.time;
            foreach (var e in events)
            {
                if (e.Kind == SimEventKind.Arrival) StartRun(e, now);
                else if (e.Kind == SimEventKind.FortressAlert && e.DefId != null && e.DefId.EndsWith("gunFire")) GunBlast(e.Position);
                else if (e.Kind is SimEventKind.ProjectileImpact or SimEventKind.StrikeImpact && !e.Airborne) RippleDome(e, now);
            }
        }

        private void StartRun(SimEvent e, float now)
        {
            if (_line == null) return;
            var run = new Run { Kind = _line.Kind, StopAt = now + e.Value };
            var team = e.Team;
            if (_line.Kind == ArrivalKind.Rail)
            {
                var loco = _models.Spawn(_models.Has("armored_train") ? "armored_train" : "truck", team, _root.transform);
                loco.Root.transform.localScale = Vector3.one * 1.15f;
                run.Parts.Add((loco.Root.transform, 0f));
                var behind = 12f;
                foreach (var wagon in new[] { "rail_boxcar", "rail_tanker", "rail_boxcar" })
                {
                    if (!_models.Has(wagon)) continue;
                    var w = _models.Spawn(wagon, -1, _root.transform);
                    behind += 6.2f;
                    run.Parts.Add((w.Root.transform, behind));
                    behind += 6.2f;
                }
            }
            else
            {
                var plane = _models.Spawn(_models.Has("heavy_bomber") ? "heavy_bomber" : "strike_jet", team, _root.transform);
                plane.Root.transform.localScale = Vector3.one * 1.3f;
                run.Plane = plane.Root.transform;
            }
            _runs.Add(run);
            PlaceRun(run, now);
        }

        /// <summary>
        /// Where along the line (metres from its stop, negative: before it) a train is at a moment: decelerating in, standing,
        /// then backing out the way it came. Prompt 33 L5: the Sim's own curve (RailSystem.SupportOffset), so this train (the
        /// visual stand-in outside the map) and the support train's run in the battle meet at the entry gate on its tick.
        /// </summary>
        private static float TrainOffset(float t) => MachineBrigade.Sim.Movement.RailSystem.SupportOffset(t);

        private void PlaceRun(Run run, float now)
        {
            var t = now - run.StopAt;
            if (run.Kind == ArrivalKind.Rail)
            {
                var a = _line.Path[_line.Path.Count - 2];
                var b = _line.Path[_line.Path.Count - 1];
                var end = new Vector3(b.X, 0f, b.Y);
                var dir = (end - new Vector3(a.X, 0f, a.Y)).normalized;
                var front = end - dir * 12.5f + dir * TrainOffset(t);
                var rotation = Quaternion.LookRotation(dir);
                foreach (var (part, behind) in run.Parts)
                {
                    var p = front - dir * behind;
                    part.SetPositionAndRotation(p, behind > 0f ? rotation * Quaternion.Euler(0f, 90f, 0f) : rotation);
                }
                if (!run.Dusted && t >= -0.5f)
                {
                    run.Dusted = true;
                    _effects.Shockwave(new Vector3(_line.Stop.X, 0.2f, _line.Stop.Y), 16f, new Color(1.1f, 1f, 0.85f, 0.7f));
                }
                return;
            }
            // The runway: from beyond its threshold down to touchdown, the roll to the stop, a wait
            // while the vehicles drive out, then round and away the way it came.
            var first = new Vector3(_line.Path[1].X, 0f, _line.Path[1].Y);
            var stop = new Vector3(_line.Stop.X, 0f, _line.Stop.Y);
            var along = (stop - first).normalized;
            var roll = Vector3.Distance(first, stop);
            Vector3 at;
            var heading = along;
            var pitch = 0f;
            var touch = -PlaneRoll;
            if (t < touch)
            {
                var k = Mathf.Clamp01((touch - t) / PlaneApproach);
                at = first - along * (90f * k) + Vector3.up * (1.2f + 26f * k);
                pitch = -4f;
            }
            else if (t < 0f)
            {
                var k = (t - touch) / PlaneRoll;
                at = first + along * (roll * (1f - (1f - k) * (1f - k))) + Vector3.up * 1.2f;
                if (!run.Dusted)
                {
                    run.Dusted = true;
                    _effects.Shockwave(first + Vector3.up * 0.2f, 12f, new Color(1.2f, 1.1f, 0.95f, 0.8f));
                }
            }
            else if (t < PlaneWait)
            {
                at = stop + Vector3.up * 1.2f;
            }
            else
            {
                var k = t - PlaneWait;
                var turn = Mathf.Clamp01(k / 3f);
                heading = Vector3.Slerp(along, -along, turn).normalized;
                var run2 = Mathf.Max(0f, k - 3f);
                var travel = 3f * run2 * run2;
                at = stop - along * travel + Vector3.up * (1.2f + Mathf.Max(0f, travel - 45f) * 0.35f);
                pitch = travel > 45f ? 8f : 0f;
            }
            run.Plane.SetPositionAndRotation(at, Quaternion.LookRotation(heading) * Quaternion.Euler(pitch, 0f, 0f));
        }

        private void AnimateRuns(float now)
        {
            for (var i = _runs.Count - 1; i >= 0; i--)
            {
                var run = _runs[i];
                var t = now - run.StopAt;
                var done = run.Kind == ArrivalKind.Rail ? t > TrainWait + TrainTravel : t > PlaneWait + 10f;
                if (done)
                {
                    foreach (var (part, _) in run.Parts)
                        if (part != null) Object.Destroy(part.gameObject);
                    if (run.Plane != null) Object.Destroy(run.Plane.gameObject);
                    _runs.RemoveAt(i);
                    continue;
                }
                PlaceRun(run, now);
            }
        }

        // ------------------------------------------------------------------ the super-gun

        /// <summary>The super-gun fires: a blast at its muzzle that shakes the screen.</summary>
        private void GunBlast(Vector2 gun)
        {
            var heading = _world.Map.Fortress?.SuperGunHeading ?? 0f;
            var forward = new Vector3(Mathf.Sin(heading), 0f, Mathf.Cos(heading));
            var muzzle = new Vector3(gun.X, 4.5f, gun.Y) + forward * 9f;
            _effects.Blast(ExplosionTier.Huge, muzzle, 1.5f);
            _effects.Shockwave(new Vector3(gun.X, 0.2f, gun.Y), 26f, new Color(1.3f, 1.1f, 0.9f, 0.8f));
        }

        // ------------------------------------------------------------------ searchlights

        private sealed class Searchlight
        {
            public Vector3 Mast;
            public Transform Cone, Pool;
            public Vector3 Aim;
            public float Phase, Base;
        }

        /// <summary>A light cone and its pool on the ground from each of the fortress's floodlight masts (the nearest the HQ first).</summary>
        private void BuildSearchlights()
        {
            var fortress = _world.Map.Fortress;
            if (fortress == null) return;
            var masts = new List<Vector2>();
            foreach (var prop in _world.Props)
                if (prop.IsAlive && prop.Def.Id == "floodlight_mast" && fortress.Contains(prop.Position)) masts.Add(prop.Position);
            masts.Sort((a, b) => Vector2.DistanceSquared(a, fortress.Hq).CompareTo(Vector2.DistanceSquared(b, fortress.Hq)));
            if (masts.Count == 0) return;
            var cone = Own(Cone(20));
            var pool = Own(Pool());
            _coneMaterial = Additive("Searchlight", 1.1f, 3011);
            _poolMaterial = new Material(Shader.Find("MachineBrigade/Particle")) { name = "Searchlight Pool" };
            _poolMaterial.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            _poolMaterial.SetFloat("_DstBlend", (float)BlendMode.One);
            _poolMaterial.SetFloat("_Intensity", 1.6f);
            _poolMaterial.SetFloat("_Shape", 0f);
            _poolMaterial.SetFloat("_Softness", 1.4f);
            _poolMaterial.renderQueue = 2961;
            _owned.Add(_poolMaterial);
            var toward = _world.TryGetRally(_mode.Attacker, out var camp) ? camp : Vector2.Zero;
            for (var i = 0; i < masts.Count && i < MaxLights; i++)
            {
                var m = masts[i];
                var mast = new Vector3(m.X, LightHeight, m.Y);
                var outward = new Vector3(toward.X - m.X, 0f, toward.Y - m.Y);
                var light = new Searchlight
                {
                    Mast = mast, Phase = i * 1.7f, Base = Mathf.Atan2(outward.x, outward.z),
                    Cone = Place("Searchlight", cone, _coneMaterial).transform,
                    Pool = Place("Searchlight Pool", pool, _poolMaterial).transform,
                };
                light.Aim = mast + new Vector3(Mathf.Sin(light.Base), 0f, Mathf.Cos(light.Base)) * 20f;
                light.Aim.y = 0f;
                _lights.Add(light);
            }
            SetNight(_night);
        }

        /// <summary>A unit cone: apex at the origin, opening along +Z to a radius of 1 at z = 1, fading towards its end.</summary>
        private static Mesh Cone(int segments)
        {
            var vertices = new List<Vector3> { Vector3.zero };
            var colours = new List<Color> { Primitives.Linear(new Color(1f, 0.96f, 0.82f, 0.5f)) };
            var uvs = new List<UnityEngine.Vector2> { UnityEngine.Vector2.zero };
            var triangles = new List<int>();
            for (var s = 0; s <= segments; s++)
            {
                var a = s / (float)segments * Mathf.PI * 2f;
                vertices.Add(new Vector3(Mathf.Cos(a), Mathf.Sin(a), 1f));
                colours.Add(Primitives.Linear(new Color(1f, 0.94f, 0.78f, 0.06f)));
                uvs.Add(new UnityEngine.Vector2(s / (float)segments, 1f));
            }
            for (var s = 1; s <= segments; s++) triangles.AddRange(new[] { 0, s, s + 1 });
            var mesh = new Mesh { name = "Searchlight Cone" };
            mesh.SetVertices(vertices);
            mesh.SetColors(colours);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>A flat quad lying on the ground for the soft pool of light (the particle shader's round shape).</summary>
        private static Mesh Pool()
        {
            var colour = Primitives.Linear(new Color(1f, 0.95f, 0.8f, 0.55f));
            var mesh = new Mesh { name = "Searchlight Pool" };
            mesh.SetVertices(new[] { new Vector3(-0.5f, 0f, -0.5f), new Vector3(0.5f, 0f, -0.5f), new Vector3(0.5f, 0f, 0.5f), new Vector3(-0.5f, 0f, 0.5f) });
            mesh.SetUVs(0, new[] { new UnityEngine.Vector2(0f, 0f), new UnityEngine.Vector2(1f, 0f), new UnityEngine.Vector2(1f, 1f), new UnityEngine.Vector2(0f, 1f) });
            mesh.SetColors(new[] { colour, colour, colour, colour });
            mesh.SetTriangles(new[] { 0, 2, 1, 0, 3, 2 }, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>Night falls or lifts: the searchlights come on or go out.</summary>
        public void SetNight(bool night)
        {
            _night = night;
            foreach (var l in _lights)
            {
                l.Cone.gameObject.SetActive(night);
                l.Pool.gameObject.SetActive(night);
            }
        }

        private void AnimateSearchlights(float time, float dt)
        {
            if (!_night) return;
            foreach (var l in _lights)
            {
                // Sweep out over the approaches; lock on to an attacker that comes within reach.
                var sweep = l.Base + Mathf.Sin(time * 0.33f + l.Phase) * 1.0f;
                var reach = 22f + 9f * Mathf.Sin(time * 0.21f + l.Phase * 1.3f);
                var target = new Vector3(l.Mast.x + Mathf.Sin(sweep) * reach, 0f, l.Mast.z + Mathf.Cos(sweep) * reach);
                var best = 42f * 42f;
                foreach (var v in _world.Vehicles)
                {
                    if (!v.IsAlive || v.Team != _mode.Attacker || v.Flying || v.Def.Static) continue;
                    if (v.Team != _playerTeam && !v.IsVisibleTo(_mode.Defender)) continue;
                    var d = (new Vector3(v.Position.X, 0f, v.Position.Y) - new Vector3(l.Mast.x, 0f, l.Mast.z)).sqrMagnitude;
                    if (d >= best) continue;
                    best = d;
                    target = new Vector3(v.Position.X, 0f, v.Position.Y);
                }
                l.Aim = Vector3.Lerp(l.Aim, target, 1f - Mathf.Exp(-dt * 2.2f));
                var ray = l.Aim - l.Mast;
                var length = ray.magnitude;
                if (length < 0.5f) continue;
                var spread = 2.6f + length * 0.08f;
                l.Cone.SetPositionAndRotation(l.Mast, Quaternion.LookRotation(ray / length));
                l.Cone.localScale = new Vector3(spread, spread, length);
                l.Pool.position = l.Aim + Vector3.up * 0.12f;
                l.Pool.localScale = new Vector3(spread * 2.4f, 1f, spread * 2.4f);
            }
        }

        // ------------------------------------------------------------------ per frame

        public void Tick(float time, float dt)
        {
            AnimateDome(time);
            AnimateRuns(time);
            AnimateSearchlights(time, dt);
        }

        public void Dispose()
        {
            if (_root != null) Object.Destroy(_root);
            foreach (var m in _meshes)
                if (m != null) Object.Destroy(m);
            foreach (var m in _owned)
                if (m != null) Object.Destroy(m);
            _meshes.Clear();
            _owned.Clear();
        }
    }
}
